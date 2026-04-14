from app.schemas.post import GeneratePostsResponse, GeneratedPost
from app.services.ai_service import AIService


class WeeklyContentService:
    def __init__(self) -> None:
        self.ai_service = AIService()

    def generate_cigar_content(self, count: int = 4) -> GeneratePostsResponse:
        return self.ai_service.generate_post_batch(
            idea="A week's worth of reflective premium cigar LinkedIn content",
            topic="Cigars, reflection, brotherhood, slowing down, subtle faith",
            brand="cigar",
            count=count,
        )

    def generate_personal_content(self) -> list[GeneratedPost]:
        return [
            self._generate_single_personal_post("Product Leadership", "A sharp product leadership lesson from real operating experience", "Monday"),
            self._generate_single_personal_post("AI in Product & Technology", "A strong opinion on how AI is changing product and execution", "Tuesday"),
            self._generate_single_personal_post("Faith", "A grounded faith reflection for leaders that is thoughtful but not preachy", "Wednesday"),
            self._generate_single_personal_post("Lifestyle", "A reflection on lifestyle, cigars, brotherhood, or stillness that fits LinkedIn", "Thursday"),
            self._generate_single_personal_post("Personal / Leadership", "A real leadership or growth lesson learned in the trenches", "Friday"),
        ]

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
