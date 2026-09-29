import os
import sys
import tempfile
import uuid

_tmpdir = tempfile.mkdtemp(prefix="meatlab_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.chdir(_tmpdir)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def _create_meeting():
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "title": "第5批品评会议",
        "date": "2026-09-24T10:00:00",
        "participants": [
            {"id": f"p1-{suffix}", "name": "张三", "role": "scientist", "group": "rd"},
            {"id": f"p2-{suffix}", "name": "李四", "role": "sensory", "group": "sensory"},
        ],
        "discussions": [
            {"id": f"d1-{suffix}", "speaker": "SPEAKER_00", "group": "rd",
             "content": "细胞密度提高到1500万", "timestamp": 0.0, "duration": 5.0},
        ],
    }
    resp = client.post("/api/meetings", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_update_with_same_child_ids_no_pk_conflict():
    """缺陷1：子表主键冲突 500"""
    meeting = _create_meeting()
    mid = meeting["id"]
    p1, p2 = meeting["participants"][0]["id"], meeting["participants"][1]["id"]
    d1 = meeting["discussions"][0]["id"]

    update = {
        "participants": [
            {"id": p1, "name": "张三", "role": "scientist", "group": "rd"},
            {"id": p2, "name": "李四", "role": "sensory", "group": "sensory"},
            {"id": f"p3-{mid[:8]}", "name": "王五", "role": "chef", "group": "sensory"},
        ],
        "discussions": [
            {"id": d1, "speaker": "SPEAKER_00", "group": "rd",
             "content": "更新后的讨论内容", "timestamp": 0.0, "duration": 5.0},
        ],
    }
    resp = client.put(f"/api/meetings/{mid}", json=update)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["participants"]) == 3
    assert data["discussions"][0]["content"] == "更新后的讨论内容"

    # 再次整体替换，确认可重复执行
    resp = client.put(f"/api/meetings/{mid}", json=update)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["participants"]) == 3


def test_clearable_fields():
    """缺陷3：字段无法清空"""
    meeting = _create_meeting()
    mid = meeting["id"]

    # 生成摘要后有值
    resp = client.post(f"/api/meetings/{mid}/summary")
    assert resp.status_code == 200, resp.text
    assert client.get(f"/api/meetings/{mid}").json()["summary"]

    # 显式传 null 清空摘要字段
    resp = client.put(f"/api/meetings/{mid}", json={
        "summary": None, "processAdjustments": None, "flavorOptimizations": None,
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["summary"] is None
    assert data["processAdjustments"] is None
    assert data["flavorOptimizations"] is None

    # 空字符串标题也应生效（不再被 truthy 判断吞掉）
    resp = client.put(f"/api/meetings/{mid}", json={"title": ""})
    assert resp.status_code == 200, resp.text
    assert resp.json()["title"] == ""

    # 未传字段保持不变
    resp = client.put(f"/api/meetings/{mid}", json={"title": "新标题"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["date"] == meeting["date"]


def test_audio_denoised_path_persisted_and_reprocess():
    """缺陷2：返回失效文件路径；缺陷1：重复处理音频主键冲突"""
    meeting = _create_meeting()
    mid = meeting["id"]

    wav_header = (
        b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " +
        (16).to_bytes(4, "little") + (1).to_bytes(2, "little") +
        (1).to_bytes(2, "little") + (16000).to_bytes(4, "little") +
        (32000).to_bytes(4, "little") + (2).to_bytes(2, "little") +
        (16).to_bytes(2, "little") + b"data" + (0).to_bytes(4, "little")
    )
    for _ in range(2):
        resp = client.post(
            f"/api/meetings/{mid}/audio",
            files={"audio": ("test.wav", wav_header, "audio/wav")},
        )
        assert resp.status_code == 200, resp.text
        result = resp.json()
        path = result["denoisedAudioPath"]
        assert os.path.exists(path), f"denoisedAudioPath 指向的文件不存在: {path}"
        assert result["speakerSegments"]

    # 重复处理后讨论记录被整体替换而非累积/报错
    data = client.get(f"/api/meetings/{mid}").json()
    assert len(data["discussions"]) == len(result["speakerSegments"])


def test_email_no_fake_success():
    """缺陷4：SMTP 未配置时不得假成功"""
    meeting = _create_meeting()
    mid = meeting["id"]

    resp = client.post(f"/api/meetings/{mid}/email")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is False
    assert client.get(f"/api/meetings/{mid}").json()["emailSent"] is False


def test_single_utc_time_base():
    """缺陷5：实验记录使用统一的 UTC 时间基准"""
    from datetime import datetime, timezone
    meeting = _create_meeting()
    mid = meeting["id"]

    before = datetime.now(timezone.utc).replace(microsecond=0)
    resp = client.post(f"/api/meetings/{mid}/experiment-record")
    after = datetime.now(timezone.utc).replace(microsecond=0)
    assert resp.status_code == 200, resp.text
    markdown = resp.json()["markdown"]

    line = next(l for l in markdown.splitlines() if l.startswith("记录日期:"))
    ts_str = line.split(":", 1)[1].strip().replace(" (UTC)", "")
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    assert before <= ts <= after


def test_speaker_group_assignment():
    """缺陷6：声纹分组按说话人聚合多数表决，且按最大重叠匹配"""
    from backend.services.audio_processor import AudioProcessor

    processor = AudioProcessor.__new__(AudioProcessor)

    diarization = [
        {"speaker": "SPEAKER_00", "start": 0.0, "end": 4.0},
        {"speaker": "SPEAKER_01", "start": 5.0, "end": 20.0},
    ]
    transcript = [
        # SPEAKER_01 首条发言不含关键词（旧逻辑会误判为 rd）
        {"start": 5.0, "end": 8.0, "text": "大家好我说两句"},
        {"start": 9.0, "end": 12.0, "text": "嫩度和多汁性这次提升明显"},
        {"start": 13.0, "end": 16.0, "text": "风味和口感还需要优化"},
        {"start": 17.0, "end": 20.0, "text": "弹性和咀嚼性评分不错"},
        # 与任何声纹段都不重叠，应归属最近的 SPEAKER_00 而非硬编码默认值
        {"start": 4.2, "end": 4.8, "text": "好的"},
    ]
    result = processor.assign_groups(diarization, transcript)

    speaker_01_groups = {s.group for s in result if s.speaker == "SPEAKER_01"}
    assert speaker_01_groups == {"sensory"}, "应按全部发言聚合判定为感官评价组"

    gap_seg = next(s for s in result if abs(s.start - 4.2) < 1e-6)
    assert gap_seg.speaker == "SPEAKER_00", "无重叠段应归属时间最近的说话人"
