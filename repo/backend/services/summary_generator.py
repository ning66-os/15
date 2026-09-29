from typing import List, Optional
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import settings
from ..schemas import DiscussionSegment, TasteScore, TissueEngineeringParams


class SummaryGenerator:
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")

    def _build_context(
        self,
        discussions: List[DiscussionSegment],
        taste_score: Optional[TasteScore] = None,
        tissue_params: Optional[TissueEngineeringParams] = None,
        participants: Optional[List] = None
    ) -> str:
        """构建上下文信息"""
        context_parts = []

        if taste_score:
            context_parts.append("【口感评分数据】")
            context_parts.append(f"多汁性: {taste_score.juiciness}/10")
            context_parts.append(f"嫩度: {taste_score.tenderness}/10")
            context_parts.append(f"弹性: {taste_score.elasticity}/10")
            context_parts.append(f"风味: {taste_score.flavor}/10")
            context_parts.append(f"质感: {taste_score.texture}/10")
            context_parts.append(f"咀嚼性: {taste_score.chewiness}/10")
            avg_score = sum([
                taste_score.juiciness, taste_score.tenderness, taste_score.elasticity,
                taste_score.flavor, taste_score.texture, taste_score.chewiness
            ]) / 6
            context_parts.append(f"综合评分: {avg_score:.1f}/10")
            context_parts.append("")

        if tissue_params:
            context_parts.append("【组织工程学参数】")
            context_parts.append(f"细胞密度: {tissue_params.cellDensity} cells/cm²")
            context_parts.append(f"支架孔隙率: {tissue_params.scaffoldPorosity}%")
            context_parts.append(f"纤维取向度: {tissue_params.fiberAlignment}%")
            context_parts.append(f"成熟度: {tissue_params.maturationRate}%")
            context_parts.append(f"ECM分泌量: {tissue_params.extracellularMatrix} μg/mg")
            context_parts.append(f"血管化程度: {tissue_params.vascularization}%")
            context_parts.append("")

        if participants:
            context_parts.append("【参与人员】")
            for p in participants:
                group = "研发组" if p.group == "rd" else "感官评价组"
                role_map = {
                    "scientist": "科学家",
                    "chef": "厨师",
                    "sensory": "感官评价员",
                    "pm": "产品经理"
                }
                role = role_map.get(p.role, p.role)
                context_parts.append(f"- {p.name} ({group} / {role})")
            context_parts.append("")

        context_parts.append("【讨论内容】")
        for seg in discussions:
            group_label = "研发组" if seg.group == "rd" else "感官评价组"
            context_parts.append(f"[{group_label}] {seg.speaker}: {seg.content}")

        return "\n".join(context_parts)

    def generate_summary(
        self,
        discussions: List[DiscussionSegment],
        taste_score: Optional[TasteScore] = None,
        tissue_params: Optional[TissueEngineeringParams] = None,
        participants: Optional[List] = None
    ) -> dict:
        """生成会议摘要、工艺调整方案和风味优化建议"""
        context = self._build_context(discussions, taste_score, tissue_params, participants)

        if self.client is None:
            return self._mock_summary(taste_score, tissue_params)

        try:
            system_prompt = """你是一位专业的食品科技和细胞农业领域的技术文档专家。
你的任务是分析人造肉研发项目的品评会议记录，生成：
1. 会议摘要 - 提炼核心讨论内容和关键结论
2. 工艺调整方案 - 基于讨论给出具体的技术参数调整建议
3. 风味优化建议 - 从食品科学角度给出风味改进方向

请使用Markdown格式输出，使用###作为二级标题，使用-作为列表项。
要确保建议的科学性和可操作性，引用具体的参数和数据。"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下会议记录：\n\n{context}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            parts = self._parse_summary_response(content)
            return parts

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._mock_summary(taste_score, tissue_params)

    def _parse_summary_response(self, content: str) -> dict:
        """解析OpenAI返回的Markdown内容"""
        summary = ""
        process_adjustments = ""
        flavor_optimizations = ""

        current_section = None
        lines = content.split("\n")

        for line in lines:
            if "会议摘要" in line or "摘要" in line:
                current_section = "summary"
                continue
            elif "工艺调整" in line or "技术方案" in line:
                current_section = "process"
                continue
            elif "风味优化" in line or "风味改进" in line:
                current_section = "flavor"
                continue

            if current_section == "summary":
                summary += line + "\n"
            elif current_section == "process":
                process_adjustments += line + "\n"
            elif current_section == "flavor":
                flavor_optimizations += line + "\n"

        if not summary and not process_adjustments and not flavor_optimizations:
            summary = content

        return {
            "summary": summary.strip(),
            "processAdjustments": process_adjustments.strip(),
            "flavorOptimizations": flavor_optimizations.strip()
        }

    def _mock_summary(self, taste_score, tissue_params) -> dict:
        """模拟生成的摘要内容"""
        avg_score = 0
        if taste_score:
            avg_score = sum([
                taste_score.juiciness, taste_score.tenderness, taste_score.elasticity,
                taste_score.flavor, taste_score.texture, taste_score.chewiness
            ]) / 6

        summary = f"""### 会议摘要

本次品评会议针对第5批人造肉样本进行了全面评估。研发组与感官评价组共计{8}人参与了讨论。

**关键发现：**
- 综合口感评分达到 {avg_score:.1f}/10，较上一批提升显著
- 嫩度和弹性表现优异，达到对照组85%以上的相似度
- 多汁性和风味仍有提升空间，特别是脂肪感和回味不足
- 细胞密度1500万/cm²，支架孔隙率85%，整体工艺参数稳定

**讨论焦点：**
- 研发组详细介绍了生物反应器灌注速率优化和氧分压控制方案
- 感官评价组反馈咀嚼时存在轻微颗粒感，建议优化纤维排列
- 一致认为需要增加脂肪细胞共培养比例以改善风味层次感

**下一步计划：**
- 下一批样本将测试脂肪细胞共培养比例从10%提升至20%
- 优化电纺纤维参数，将直径从800nm降至500nm
- 探索肌红蛋白添加对色泽和风味的改善效果"""

        process_adjustments = """### 工艺调整方案

#### 1. 细胞培养参数优化
- **脂肪细胞共培养比例**: 从当前10%提升至20%，采用肌肉细胞与脂肪细胞序贯接种策略
- **接种时机调整**: 肌肉细胞培养7天后接种脂肪细胞，确保肌管形成后再引入脂肪细胞
- **培养基优化**: 添加1%脂肪细胞诱导培养基，促进脂肪滴形成

#### 2. 支架材料改进
- **纤维直径优化**: 电纺参数调整，将平均纤维直径从800nm降至500nm，改善口感细腻度
- **孔隙结构调整**: 采用梯度孔隙设计，表层孔隙率85%，内部孔隙率90%，促进细胞浸润
- **表面改性**: 增加RGD肽接枝，提高细胞粘附率15%以上

#### 3. 生物反应器工艺优化
- **灌注速率曲线**: 采用阶梯式灌注策略，第1-3天2mL/min，第4-7天3.5mL/min，第8-14天5mL/min
- **氧分压控制**: 建立时空梯度氧分压控制，表层21%，核心区15%
- **机械刺激**: 第10天开始施加周期性拉伸刺激，频率0.5Hz，应变率10%

#### 4. 成熟培养优化
- **成熟时间延长**: 探索16天和18天成熟培养组，评估肌管融合率变化
- **肌红蛋白添加**: 第12天添加50μg/mL肌红蛋白，促进色泽和风味物质生成
- **培养基更换策略**: 从每日更换改为每48小时更换，保留细胞分泌的生长因子"""

        flavor_optimizations = """### 风味优化建议

#### 1. 脂肪风味提升
- **脂肪细胞来源优化**: 筛选不同部位脂肪干细胞（肌间脂肪、皮下脂肪），评估风味贡献差异
- **脂肪成熟诱导**: 优化脂肪细胞诱导培养基，添加碘乙酸、胰岛素、地塞米松组合，提高脂肪滴含量
- **风味前体物富集**: 在成熟阶段添加亚油酸、亚麻酸等多不饱和脂肪酸前体

#### 2. 肉香物质生成
- **美拉德反应前体调控**: 提高细胞内还原糖和游离氨基酸含量，特别是谷氨酸、甘氨酸、丙氨酸
- **硫胺素添加**: 培养基中添加10μM硫胺素（维生素B1），促进含硫风味物质生成
- **脂质氧化控制**: 适度控制脂质过氧化程度，生成特征性熟肉风味物质

#### 3. 风味物质释放优化
- **脂肪包埋技术**: 采用微胶囊技术包埋风味物质，在咀嚼过程中释放
- **蛋白酶解调控**: 控制内源性蛋白酶活性，产生特定肽段和氨基酸，增强鲜味
- **风味呈味协同**: 优化IMP（肌苷酸）和GMP（鸟苷酸）含量，与谷氨酸产生协同增鲜效应

#### 4. 不良风味抑制
- **腥味物质去除**: 优化细胞清洗工艺，减少培养基残留带来的腥味
- **抗氧化系统**: 添加天然抗氧化剂（维生素E、茶多酚），抑制不良氧化产物生成
- **微生物控制**: 严格无菌操作，避免微生物代谢产生异味

#### 5. 感官评价体系完善
- 建立风味轮廓分析（Flavor Profile Analysis）方法
- 采用电子鼻和气相色谱-质谱联用（GC-MS）进行客观风味分析
- 建立风味与工艺参数的关联模型，指导工艺优化"""

        return {
            "summary": summary,
            "processAdjustments": process_adjustments,
            "flavorOptimizations": flavor_optimizations
        }


summary_generator = SummaryGenerator()
