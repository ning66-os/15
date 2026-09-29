import os
import shutil
import tempfile
import numpy as np
from typing import List, Tuple, Optional

try:
    import librosa
    import librosa.display
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

from ..config import settings
from ..schemas import SpeakerSegment


class AudioProcessor:
    def __init__(self, audio_dir: str = "./audio_files"):
        self.whisper_model = None
        self.pyannote_pipeline = None
        self.sample_rate = 16000
        self.audio_dir = audio_dir
        os.makedirs(self.audio_dir, exist_ok=True)

    def _init_whisper(self):
        if self.whisper_model is None and WHISPER_AVAILABLE:
            self.whisper_model = whisper.load_model("base")

    def _init_pyannote(self):
        if self.pyannote_pipeline is None and PYANNOTE_AVAILABLE:
            try:
                self.pyannote_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=settings.PYANNOTE_AUTH_TOKEN
                )
            except Exception as e:
                print(f"Failed to load pyannote: {e}")

    def remove_centrifuge_noise(self, audio_path: str, output_path: str) -> str:
        """
        使用 librosa 去除实验室离心机噪声
        离心机噪声通常是低频周期性噪声，使用谱减法去除
        """
        if not LIBROSA_AVAILABLE:
            print("Librosa not available, skipping noise removal")
            if os.path.abspath(audio_path) != os.path.abspath(output_path):
                shutil.copyfile(audio_path, output_path)
            return output_path

        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        centrifuge_freq_range = (20, 200)

        D = librosa.stft(y)
        magnitude, phase = librosa.magphase(D)

        freq_bins = librosa.fft_frequencies(sr=sr)
        centrifuge_mask = (freq_bins >= centrifuge_freq_range[0]) & (freq_bins <= centrifuge_freq_range[1])

        noise_estimate = np.mean(magnitude[centrifuge_mask, :], axis=0)
        noise_estimate = np.tile(noise_estimate, (magnitude.shape[0], 1))

        alpha = 2.0
        beta = 0.01
        magnitude_clean = np.maximum(magnitude - alpha * noise_estimate, beta * magnitude)

        D_clean = magnitude_clean * phase
        y_clean = librosa.istft(D_clean)

        y_clean = librosa.decompose.nn_filter(
            y_clean,
            aggregate=np.median,
            metric='cosine',
            width=int(librosa.time_to_samples(0.05, sr=sr))
        )

        sf.write(output_path, y_clean, sr)
        return output_path

    def transcribe_with_whisper(self, audio_path: str) -> Tuple[str, List[dict]]:
        """
        使用 Whisper 识别生物学术语转录
        """
        if not WHISPER_AVAILABLE:
            print("Whisper not available, returning mock transcription")
            return self._mock_transcription()

        self._init_whisper()

        if self.whisper_model is None:
            return self._mock_transcription()

        result = self.whisper_model.transcribe(
            audio_path,
            language="zh",
            initial_prompt="这是一个关于人造肉、细胞培养、组织工程、生物反应器、3D生物打印、干细胞、肌肉细胞、脂肪细胞、细胞外基质、支架材料、生物墨水、风味物质、美拉德反应的技术讨论会议。",
            word_timestamps=True
        )

        full_text = result["text"]
        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        return full_text, segments

    def diarize_speakers(self, audio_path: str) -> List[dict]:
        """
        使用 pyannote 分离研发组与感官评价组
        """
        if not PYANNOTE_AVAILABLE:
            print("Pyannote not available, returning mock diarization")
            return self._mock_diarization()

        self._init_pyannote()

        if self.pyannote_pipeline is None:
            return self._mock_diarization()

        diarization = self.pyannote_pipeline(audio_path)

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })

        return segments

    def assign_groups(self, speaker_segments: List[dict], transcript_segments: List[dict]) -> List[SpeakerSegment]:
        """
        根据发言内容和模式分配组别（研发组/感官评价组）
        研发组偏向讨论技术参数、细胞培养、生物反应器等
        感官评价组偏向讨论口感、风味、质地等
        """
        rd_keywords = [
            "细胞", "培养", "生物反应器", "支架", "3D打印", "生物墨水",
            "干细胞", "增殖", "分化", "培养基", "血清", "胶原蛋白",
            "纤维蛋白", "壳聚糖", "海藻酸盐", "血管化", "灌注",
            "剪切应力", "氧分压", "pH值", "接种密度", "细胞外基质",
            "肌管", "肌纤维", "成熟度", "分化率", "细胞系",
            "生物材料", "可降解", "孔隙率", "机械强度"
        ]

        sensory_keywords = [
            "口感", "风味", "质地", "嫩度", "多汁性", "弹性", "咀嚼性",
            "香味", "腥味", "草味", "肉香", "脂肪味", "苦味", "甜味",
            "鲜味", "酸度", "咸味", "回味", "层次感", "饱满度",
            "嚼劲", "软硬", "颗粒感", "纤维感", "油脂感", "多汁",
            "打分", "评分", "对照组", "偏好", "接受度", "相似度"
        ]

        def find_speaker(start: float, end: float) -> str:
            """按时间重叠最大的声纹段归属说话人，无重叠时取时间最近的段"""
            best = None
            best_overlap = 0.0
            for ds in speaker_segments:
                overlap = min(end, ds["end"]) - max(start, ds["start"])
                if overlap > best_overlap:
                    best_overlap = overlap
                    best = ds
            if best is not None:
                return best["speaker"]
            if speaker_segments:
                nearest = min(
                    speaker_segments,
                    key=lambda ds: max(ds["start"] - end, start - ds["end"], 0.0)
                )
                return nearest["speaker"]
            return "SPEAKER_00"

        # 第一遍：确定每个转录段的说话人，并按说话人聚合关键词得分
        segment_speakers = []
        speaker_scores = {}
        for seg in transcript_segments:
            text = seg["text"]
            rd_count = sum(1 for kw in rd_keywords if kw in text)
            sensory_count = sum(1 for kw in sensory_keywords if kw in text)

            speaker = find_speaker(seg["start"], seg["end"])
            segment_speakers.append((seg, speaker))

            scores = speaker_scores.setdefault(speaker, [0, 0])
            scores[0] += rd_count
            scores[1] += sensory_count

        # 第二遍：按说话人全部发言的累计得分多数表决分组
        speaker_groups = {}
        for speaker, (rd_total, sensory_total) in speaker_scores.items():
            speaker_groups[speaker] = "sensory" if sensory_total > rd_total else "rd"

        result = []
        for seg, speaker in segment_speakers:
            result.append(SpeakerSegment(
                speaker=speaker,
                start=seg["start"],
                end=seg["end"],
                text=seg["text"],
                group=speaker_groups.get(speaker, "rd")
            ))

        return result

    def process_audio(self, audio_content: bytes, meeting_id: Optional[str] = None) -> dict:
        """
        完整的音频处理流程：降噪 -> 转录 -> 声纹分离 -> 分组
        降噪后的音频保存到持久目录，返回长期有效的文件路径
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name

        try:
            file_stem = meeting_id or os.path.splitext(os.path.basename(temp_audio_path))[0]
            denoised_path = os.path.join(self.audio_dir, f"{file_stem}_denoised.wav")
            self.remove_centrifuge_noise(temp_audio_path, denoised_path)

            transcript, transcript_segments = self.transcribe_with_whisper(denoised_path)

            speaker_segments = self.diarize_speakers(denoised_path)

            final_segments = self.assign_groups(speaker_segments, transcript_segments)

            return {
                "denoisedAudioPath": denoised_path,
                "transcript": transcript,
                "speakerSegments": final_segments
            }

        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)

    def _mock_transcription(self) -> Tuple[str, List[dict]]:
        """模拟转录结果，用于开发测试"""
        mock_segments = [
            {"start": 0.0, "end": 5.2, "text": "各位好，今天我们来品评第5批人造肉样本，首先请研发组介绍一下本次的培养参数。"},
            {"start": 5.5, "end": 12.3, "text": "这次我们将细胞接种密度提高到了1500万每平方厘米，支架孔隙率调整为85%，电纺纤维的取向度达到了78%。"},
            {"start": 12.6, "end": 18.9, "text": "生物反应器的灌注速率我们优化到了每分钟5毫升，氧分压控制在21%，pH值维持在7.2到7.4之间。"},
            {"start": 19.2, "end": 25.8, "text": "成熟培养时间是14天，肌管分化率约72%，细胞外基质的胶原蛋白含量达到了85微克每毫克。"},
            {"start": 26.1, "end": 32.4, "text": "好的，那现在请感官评价组的成员分享一下品尝后的感受。"},
            {"start": 32.7, "end": 38.9, "text": "我觉得这次的嫩度比上一批好很多，咬下去的感觉更接近真实牛肉。"},
            {"start": 39.2, "end": 45.6, "text": "多汁性还可以，但是咀嚼的时候稍微有点颗粒感，可能是纤维排列还不够均匀。"},
            {"start": 45.9, "end": 52.3, "text": "风味方面，基础的肉香有了，但是缺少脂肪带来的那种丰润感，回味稍微短了一点。"},
            {"start": 52.6, "end": 59.1, "text": "弹性不错，和对照组相比大概能达到85%的相似度，整体接受度还是很高的。"},
            {"start": 59.4, "end": 65.8, "text": "好的，感谢大家的反馈。接下来我们讨论一下下一批的工艺调整方向。"},
            {"start": 66.1, "end": 73.5, "text": "我建议可以尝试增加脂肪细胞的共培养比例，从现在的10%提高到20%，应该能改善多汁性和风味。"},
            {"start": 73.8, "end": 80.2, "text": "另外，我们可以优化一下电纺参数，把纤维直径从800纳米降到500纳米，可能会减少颗粒感。"},
            {"start": 80.5, "end": 87.9, "text": "还有，建议在成熟培养后期添加少量的肌红蛋白，这样可以改善色泽和风味物质的生成。"},
        ]

        full_text = " ".join([seg["text"] for seg in mock_segments])
        return full_text, mock_segments

    def _mock_diarization(self) -> List[dict]:
        """模拟声纹分离结果"""
        return [
            {"speaker": "SPEAKER_00", "start": 0.0, "end": 5.2},
            {"speaker": "SPEAKER_01", "start": 5.5, "end": 18.9},
            {"speaker": "SPEAKER_02", "start": 19.2, "end": 25.8},
            {"speaker": "SPEAKER_00", "start": 26.1, "end": 32.4},
            {"speaker": "SPEAKER_03", "start": 32.7, "end": 38.9},
            {"speaker": "SPEAKER_04", "start": 39.2, "end": 45.6},
            {"speaker": "SPEAKER_05", "start": 45.9, "end": 52.3},
            {"speaker": "SPEAKER_06", "start": 52.6, "end": 59.1},
            {"speaker": "SPEAKER_00", "start": 59.4, "end": 65.8},
            {"speaker": "SPEAKER_01", "start": 66.1, "end": 73.5},
            {"speaker": "SPEAKER_02", "start": 73.8, "end": 80.2},
            {"speaker": "SPEAKER_01", "start": 80.5, "end": 87.9},
        ]


audio_processor = AudioProcessor()
