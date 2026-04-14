from pydantic import BaseModel


class GeneratedPost(BaseModel):
    content: str
    hashtags: list[str]
    suggested_posting_day: str | None = None
    signature_line: str | None = None


class GeneratePostsResponse(BaseModel):
    posts: list[GeneratedPost]
