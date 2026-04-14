from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.post import Post


class LinkedInService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def publish_post(self, post: Post) -> dict:
        if self.settings.linkedin_mock_mode:
            return {
                "provider": "mock",
                "published": True,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "post_preview": post.content[:120],
            }

        return {
            "provider": "linkedin",
            "published": False,
            "message": "LinkedIn API integration is not configured yet. Running in safe fallback mode.",
        }
