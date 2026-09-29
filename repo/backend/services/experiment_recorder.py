import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from .. import models


class ExperimentRecorder:
    def __init__(self, records_dir: str = "./experiment_records"):
        self.records_dir = records_dir
        os.makedirs(records_dir, exist_ok=True)

    def _build_experiment_record(self, meeting: models.MeetingNote) -> str:
        """构建实验记录本的Markdown内容"""
        record_id = f"EXP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        avg_score = (
            meeting.juiciness + meeting.tenderness + meeting.elasticity +
            meeting.flavor + meeting.texture + meeting.chewiness
        ) / 6

        rd_participants = [p for p in meeting.participants if p.group == "rd"]
        sensory_participants = [p for p in meeting.participants if p.group == "sensory"]

        content = f"""---
记录编号: {record_id}
记录日期: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} (UTC)
会议日期: {meeting.date}
项目名称: 人造肉研发项目
实验类型: 品评会议
---

# {record_id}: {meeting.title}

## 1. 实验目的

评估第X批人造肉样本的口感、风味和组织特性，收集研发组和感官评价组的反馈，为下一批次的工艺优化提供依据。

## 2. 实验材料

- 人造肉样本批次: 待补充
- 培养周期: 14天
- 生物反应器: 待补充
- 培养基配方: 待补充

## 3. 组织工程学参数

| 参数名称 | 数值 | 单位 | 备注 |
|----------|------|------|------|
| 细胞接种密度 | {meeting.cell_density:,.0f} | cells/cm² | |
| 支架孔隙率 | {meeting.scaffold_porosity} | % | |
| 纤维取向度 | {meeting.fiber_alignment} | % | |
| 成熟度 | {meeting.maturation_rate} | % | |
| 细胞外基质(ECM) | {meeting.extracellular_matrix} | μg/mg | |
| 血管化程度 | {meeting.vascularization} | % | |

## 4. 感官评价结果

### 4.1 综合评分

**综合评分: {avg_score:.1f}/10**

### 4.2 分项评分

| 评价指标 | 评分 | 满分 | 评价标准 |
|----------|------|------|----------|
| 多汁性 (Juiciness) | {meeting.juiciness} | 10 | 咀嚼过程中释放水分的程度 |
| 嫩度 (Tenderness) | {meeting.tenderness} | 10 | 牙齿咬入所需的力 |
| 弹性 (Elasticity) | {meeting.elasticity} | 10 | 受压后恢复原状的能力 |
| 风味 (Flavor) | {meeting.flavor} | 10 | 整体风味强度和愉悦度 |
| 质感 (Texture) | {meeting.texture} | 10 | 整体质地的均匀性 |
| 咀嚼性 (Chewiness) | {meeting.chewiness} | 10 | 咀嚼所需的次数和力量 |

### 4.3 评分雷达图

(此处插入雷达图)

## 5. 参与人员

### 5.1 研发组
"""

        for p in rd_participants:
            role_map = {"scientist": "科学家", "chef": "厨师", "pm": "产品经理", "sensory": "感官评价员"}
            content += f"- {p.name}: {role_map.get(p.role, p.role)}\n"

        content += "\n### 5.2 感官评价组\n"

        for p in sensory_participants:
            role_map = {"scientist": "科学家", "chef": "厨师", "pm": "产品经理", "sensory": "感官评价员"}
            content += f"- {p.name}: {role_map.get(p.role, p.role)}\n"

        content += "\n## 6. 讨论记录\n\n"

        if meeting.discussions:
            for seg in meeting.discussions:
                timestamp = f"{int(seg.timestamp // 60):02d}:{int(seg.timestamp % 60):02d}"
                group_label = "研发组" if seg.group == "rd" else "感官评价组"
                content += f"**[{timestamp}] {seg.speaker} ({group_label})**: {seg.content}\n\n"
        else:
            content += "(无讨论记录)\n"

        if meeting.summary:
            content += "\n## 7. 会议摘要\n\n"
            content += meeting.summary + "\n"

        if meeting.process_adjustments:
            content += "\n## 8. 工艺调整方案\n\n"
            content += meeting.process_adjustments + "\n"

        if meeting.flavor_optimizations:
            content += "\n## 9. 风味优化建议\n\n"
            content += meeting.flavor_optimizations + "\n"

        content += """
## 10. 后续行动计划

- [ ] 按照工艺调整方案进行下一批次实验
- [ ] 评估脂肪细胞共培养比例提升效果
- [ ] 优化电纺纤维直径参数
- [ ] 测试肌红蛋白添加效果

## 11. 备注

(填写其他需要说明的内容)

---

**记录人**: 系统自动生成
**审核人**: _______________
**审核日期**: _______________
"""

        return record_id, content

    def create_record(self, meeting: models.MeetingNote) -> dict:
        """创建实验记录并保存到文件"""
        record_id, markdown_content = self._build_experiment_record(meeting)

        record_file = os.path.join(
            self.records_dir,
            f"{record_id}_{meeting.title.replace(' ', '_')}.md"
        )

        with open(record_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {
            "recordId": record_id,
            "markdown": markdown_content,
            "filePath": record_file
        }


experiment_recorder = ExperimentRecorder()
