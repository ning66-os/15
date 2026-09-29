import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import markdown
from typing import Optional
from datetime import datetime

from ..config import settings
from .. import models


class EmailSender:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    def _build_email_content(self, meeting: models.MeetingNote) -> str:
        """构建邮件的Markdown内容"""
        avg_score = (
            meeting.juiciness + meeting.tenderness + meeting.elasticity +
            meeting.flavor + meeting.texture + meeting.chewiness
        ) / 6

        content = f"""# 🥩 人造肉研发品评会议纪要

**会议标题**: {meeting.title}
**会议时间**: {meeting.date}
**记录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 综合评分

**综合评分: {avg_score:.1f}/10**

| 指标 | 评分 |
|------|------|
| 多汁性 | {meeting.juiciness}/10 |
| 嫩度 | {meeting.tenderness}/10 |
| 弹性 | {meeting.elasticity}/10 |
| 风味 | {meeting.flavor}/10 |
| 质感 | {meeting.texture}/10 |
| 咀嚼性 | {meeting.chewiness}/10 |

---

## 🔬 组织工程学参数

| 参数 | 数值 |
|------|------|
| 细胞密度 | {meeting.cell_density:,.0f} cells/cm² |
| 支架孔隙率 | {meeting.scaffold_porosity}% |
| 纤维取向度 | {meeting.fiber_alignment}% |
| 成熟度 | {meeting.maturation_rate}% |
| ECM分泌量 | {meeting.extracellular_matrix} μg/mg |
| 血管化程度 | {meeting.vascularization}% |

---

## 👥 参与人员

"""

        for p in meeting.participants:
            group = "研发组" if p.group == "rd" else "感官评价组"
            role_map = {
                "scientist": "科学家",
                "chef": "厨师",
                "sensory": "感官评价员",
                "pm": "产品经理"
            }
            role = role_map.get(p.role, p.role)
            content += f"- {p.name} ({group} / {role})\n"

        content += "\n---\n\n"

        if meeting.summary:
            content += "## 📝 会议摘要\n\n"
            content += meeting.summary + "\n\n"

        if meeting.process_adjustments:
            content += "## ⚙️ 工艺调整方案\n\n"
            content += meeting.process_adjustments + "\n\n"

        if meeting.flavor_optimizations:
            content += "## 🍖 风味优化建议\n\n"
            content += meeting.flavor_optimizations + "\n\n"

        content += """---

*此邮件由人造肉研发品评会议系统自动生成，请勿直接回复。*
如需查看完整会议记录，请访问系统平台。
"""
        return content

    def send_meeting_email(
        self,
        meeting: models.MeetingNote,
        to_email: Optional[str] = None,
        cc_emails: Optional[list] = None
    ) -> bool:
        """发送会议纪要邮件"""
        if to_email is None:
            to_email = settings.PRODUCT_MANAGER_EMAIL

        markdown_content = self._build_email_content(meeting)
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code']
        )

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"【品评会议纪要】{meeting.title}"
        msg['From'] = self.smtp_user
        msg['To'] = to_email

        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)

        text_part = MIMEText(markdown_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')

        msg.attach(text_part)
        msg.attach(html_part)

        try:
            if self.smtp_host == "smtp.example.com":
                print("Mock email sent (SMTP not configured)")
                print(f"To: {to_email}")
                print(f"Subject: {msg['Subject']}")
                print("\n" + "=" * 50 + "\n")
                print(markdown_content)
                return True

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                recipients = [to_email]
                if cc_emails:
                    recipients.extend(cc_emails)
                server.sendmail(self.smtp_user, recipients, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


email_sender = EmailSender()
