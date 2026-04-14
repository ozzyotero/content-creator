from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.post import PostStatus


class GeneratePostsRequest(BaseModel):
    idea: str = Field(..., min_length=5)
    topic: str = Field(..., min_length=2)
    brand: str = Field("personal", pattern="^(personal|cigar)$")
    count: int = Field(3, ge=3, le=5)


class GeneratedPost(BaseModel):
    content: str
    hashtags: list[str]
    suggested_posting_day: str | None = None
    signature_line: str | None = None


class GeneratePostsResponse(BaseModel):
    posts: list[GeneratedPost]


class SavePostRequest(BaseModel):
    content: str = Field(..., min_length=10)
    topic: str = Field(..., min_length=2)
    status: PostStatus = PostStatus.DRAFT
    scheduled_at: datetime | None = None


class SchedulePostRequest(BaseModel):
    post_id: int
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def validate_schedule(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("scheduled_at must include timezone information")
        return value


class PostResponse(BaseModel):
    id: int
    content: str
    topic: str
    status: PostStatus
    scheduled_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WeeklyEmailRequest(BaseModel):
    email_to: str | None = None
    count: int = Field(4, ge=3, le=5)
