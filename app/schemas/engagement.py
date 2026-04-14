from pydantic import BaseModel, Field


class GenerateCommentsRequest(BaseModel):
    post_content: str = Field(..., min_length=10)
    incoming_comments: list[str] = Field(default_factory=list)


class ReplySuggestion(BaseModel):
    source_comment: str
    suggested_reply: str


class GenerateCommentsResponse(BaseModel):
    daily_comments: list[str]
    reply_suggestions: list[ReplySuggestion]
