from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import PostStatus
from app.schemas.engagement import GenerateCommentsRequest, GenerateCommentsResponse
from app.schemas.post import (
    GeneratePostsRequest,
    GeneratePostsResponse,
    PostResponse,
    SavePostRequest,
    SchedulePostRequest,
    WeeklyEmailRequest,
)
from app.services.ai_service import AIService
from app.services.post_service import PostService
from app.services.weekly_service import WeeklyContentService


router = APIRouter()
ai_service = AIService()
post_service = PostService()
weekly_content_service = WeeklyContentService()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/generate-posts", response_model=GeneratePostsResponse)
def generate_posts(request: GeneratePostsRequest) -> GeneratePostsResponse:
    return ai_service.generate_posts(request)


@router.post("/save-post", response_model=PostResponse)
def save_post(request: SavePostRequest, db: Session = Depends(get_db)) -> PostResponse:
    return post_service.save_post(db, request)


@router.post("/schedule-post", response_model=PostResponse)
def schedule_post(request: SchedulePostRequest, db: Session = Depends(get_db)) -> PostResponse:
    try:
        return post_service.schedule_post(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/get-posts", response_model=list[PostResponse])
def get_posts(
    topic: str | None = Query(default=None),
    status: PostStatus | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PostResponse]:
    return post_service.get_posts(db, topic=topic, status=status)


@router.post("/generate-comments", response_model=GenerateCommentsResponse)
def generate_comments(request: GenerateCommentsRequest) -> GenerateCommentsResponse:
    return ai_service.generate_comments(request)


@router.post("/send-weekly-cigar-email")
def send_weekly_cigar_email(request: WeeklyEmailRequest) -> dict:
    email_to = request.email_to or weekly_content_service.email_service.settings.weekly_report_email
    return weekly_content_service.send_cigar_weekly_email(email_to=email_to, count=request.count)


@router.post("/send-weekly-personal-email")
def send_weekly_personal_email(request: WeeklyEmailRequest) -> dict:
    email_to = request.email_to or weekly_content_service.email_service.settings.weekly_report_email
    return weekly_content_service.send_personal_weekly_email(email_to=email_to)
