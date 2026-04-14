import html

from app.schemas.post import GeneratePostsResponse, GeneratedPost
from app.services.ai_service import AIService
from app.services.email_service import EmailService


class WeeklyContentService:
    def __init__(self) -> None:
        self.ai_service = AIService()
        self.email_service = EmailService()

    def send_cigar_weekly_email(self, email_to: str, count: int = 4) -> dict:
        generated = self.ai_service.generate_post_batch(
            idea="A week's worth of reflective premium cigar LinkedIn content",
            topic="Cigars, reflection, brotherhood, slowing down, subtle faith",
            brand="cigar",
            count=count,
        )
        subject = "Your Weekly LinkedIn Posts – Cigar Edition"
        html_body = self._render_cigar_html(generated)
        text_body = self._render_cigar_text(generated)
        email_result = self.email_service.send_email(email_to, subject, html_body, text_body)
        return {"subject": subject, "posts": generated.posts, "email_result": email_result}

    def send_personal_weekly_email(self, email_to: str) -> dict:
        posts = [
            self._generate_single_personal_post("Product Leadership", "A sharp product leadership lesson from real operating experience", "Monday"),
            self._generate_single_personal_post("AI in Product & Technology", "A strong opinion on how AI is changing product and execution", "Tuesday"),
            self._generate_single_personal_post("Faith", "A grounded faith reflection for leaders that is thoughtful but not preachy", "Wednesday"),
            self._generate_single_personal_post("Lifestyle", "A reflection on lifestyle, cigars, brotherhood, or stillness that fits LinkedIn", "Thursday"),
            self._generate_single_personal_post("Personal / Leadership", "A real leadership or growth lesson learned in the trenches", "Friday"),
        ]
        subject = "Your Weekly LinkedIn Posts – Personal Brand"
        html_body = self._render_personal_html(posts)
        text_body = self._render_personal_text(posts)
        email_result = self.email_service.send_email(email_to, subject, html_body, text_body)
        return {"subject": subject, "posts": posts, "email_result": email_result}

    def _generate_single_personal_post(self, topic: str, idea: str, day: str) -> GeneratedPost:
        generated = self.ai_service.generate_post_batch(
            idea=idea,
            topic=topic,
            brand="personal",
            count=1,
        )
        post = generated.posts[0]
        post.suggested_posting_day = day
        return post

    def _render_cigar_html(self, generated: GeneratePostsResponse) -> str:
        blocks = []
        for index, post in enumerate(generated.posts, start=1):
            safe_content = html.escape(post.content)
            safe_signature = html.escape(post.signature_line) if post.signature_line else ""
            hashtags = html.escape(" ".join(post.hashtags))
            signature = f"<p><em>{safe_signature}</em></p>" if safe_signature else ""
            blocks.append(
                f"""
                <section style="margin-bottom: 32px;">
                  <h2 style="font-size: 18px;">Post {index}</h2>
                  <p style="white-space: pre-line; line-height: 1.6;">{safe_content}</p>
                  <p><strong>{hashtags}</strong></p>
                  {signature}
                </section>
                """
            )
        return f"""
        <html>
          <body style="font-family: Georgia, serif; color: #222; max-width: 720px; margin: 0 auto;">
            <h1>Your Weekly LinkedIn Posts – Cigar Edition</h1>
            {''.join(blocks)}
          </body>
        </html>
        """.strip()

    def _render_cigar_text(self, generated: GeneratePostsResponse) -> str:
        lines = ["Your Weekly LinkedIn Posts – Cigar Edition", ""]
        for index, post in enumerate(generated.posts, start=1):
            lines.extend(
                [
                    f"Post {index}",
                    post.content,
                    " ".join(post.hashtags),
                    post.signature_line or "",
                    "",
                ]
            )
        return "\n".join(lines).strip()

    def _render_personal_html(self, posts: list[GeneratedPost]) -> str:
        blocks = []
        for index, post in enumerate(posts, start=1):
            safe_content = html.escape(post.content)
            hashtags = html.escape(" ".join(post.hashtags))
            day = html.escape(post.suggested_posting_day or "TBD")
            blocks.append(
                f"""
                <section style="margin-bottom: 32px;">
                  <h2 style="font-size: 18px;">Post {index} • Suggested day: {day}</h2>
                  <p style="white-space: pre-line; line-height: 1.6;">{safe_content}</p>
                  <p><strong>{hashtags}</strong></p>
                </section>
                """
            )
        return f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #1f2937; max-width: 720px; margin: 0 auto;">
            <h1>Your Weekly LinkedIn Posts – Personal Brand</h1>
            {''.join(blocks)}
          </body>
        </html>
        """.strip()

    def _render_personal_text(self, posts: list[GeneratedPost]) -> str:
        lines = ["Your Weekly LinkedIn Posts – Personal Brand", ""]
        for index, post in enumerate(posts, start=1):
            lines.extend(
                [
                    f"Post {index} - Suggested day: {post.suggested_posting_day or 'TBD'}",
                    post.content,
                    " ".join(post.hashtags),
                    "",
                ]
            )
        return "\n".join(lines).strip()
