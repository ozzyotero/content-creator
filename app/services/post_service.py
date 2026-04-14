from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.schemas.post import SavePostRequest, SchedulePostRequest


class PostService:
    def save_post(self, db: Session, request: SavePostRequest) -> Post:
        post = Post(
            content=request.content,
            topic=request.topic,
            status=request.status,
            scheduled_at=request.scheduled_at,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def schedule_post(self, db: Session, request: SchedulePostRequest) -> Post:
        post = db.get(Post, request.post_id)
        if post is None:
            raise ValueError("Post not found")

        post.scheduled_at = request.scheduled_at
        post.status = PostStatus.SCHEDULED
        db.commit()
        db.refresh(post)
        return post

    def get_posts(self, db: Session, topic: str | None = None, status: PostStatus | None = None) -> list[Post]:
        query = select(Post).order_by(Post.created_at.desc())
        if topic:
            query = query.where(Post.topic == topic)
        if status:
            query = query.where(Post.status == status)
        return list(db.scalars(query))

    def get_due_scheduled_posts(self, db: Session) -> list[Post]:
        now = datetime.now(timezone.utc)
        query = (
            select(Post)
            .where(Post.status == PostStatus.SCHEDULED)
            .where(Post.scheduled_at.is_not(None))
            .where(Post.scheduled_at <= now)
            .order_by(Post.scheduled_at.asc())
        )
        return list(db.scalars(query))

    def mark_posted(self, db: Session, post: Post) -> Post:
        post.status = PostStatus.POSTED
        db.commit()
        db.refresh(post)
        return post
