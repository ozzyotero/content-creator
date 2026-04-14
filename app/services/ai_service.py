from pydantic import BaseModel, Field
from openai import OpenAI

from app.core.config import get_settings
from app.core.prompts import CIGAR_BRAND_CONTEXT, PERSONAL_BRAND_CONTEXT, VOICE_RULES
from app.schemas.post import GeneratePostsResponse, GeneratedPost


class GeneratedPostPayload(BaseModel):
    content: str
    hashtags: list[str] = Field(min_length=5, max_length=5)
    suggested_posting_day: str | None = None
    signature_line: str | None = None


class GeneratedPostsPayload(BaseModel):
    posts: list[GeneratedPostPayload] = Field(min_length=1, max_length=5)


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_post_batch(self, idea: str, topic: str, brand: str, count: int) -> GeneratePostsResponse:
        brand_context = PERSONAL_BRAND_CONTEXT if brand == "personal" else CIGAR_BRAND_CONTEXT
        posting_day_rule = (
            "Include a suggested posting day from Monday through Friday for each post."
            if brand == "personal"
            else "Do not include suggested posting days unless they naturally help."
        )
        signature_rule = (
            'For cigar posts, you may include the signature line "Light Up – Slow Down – Lift Up" when it fits.'
            if brand == "cigar"
            else "Do not include a signature line."
        )

        prompt = f"""
        Create {count} LinkedIn posts.

        Topic: {topic}
        Raw idea: {idea}
        Brand: {brand}

        {brand_context}

        Requirements:
        - Each post must start with a strong hook.
        - Keep paragraphs short.
        - Include a clear opinion or lesson.
        - Share practical insight with no fluff.
        - End with a question.
        - Include exactly 5 relevant hashtags per post.
        - {posting_day_rule}
        - {signature_rule}
        """.strip()

        parsed = self.client.responses.parse(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": VOICE_RULES},
                {"role": "user", "content": prompt},
            ],
            text_format=GeneratedPostsPayload,
        )
        payload = parsed.output_parsed
        if payload is None:
            raise ValueError("Model returned no structured content for posts")

        return GeneratePostsResponse(
            posts=[
                GeneratedPost(
                    content=item.content.strip(),
                    hashtags=item.hashtags,
                    suggested_posting_day=item.suggested_posting_day,
                    signature_line=item.signature_line,
                )
                for item in payload.posts
            ]
        )
