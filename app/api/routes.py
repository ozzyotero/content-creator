from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
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


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedIn Content Agent</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    .header { background: #1e293b; border-bottom: 1px solid #334155; padding: 24px 0; text-align: center; }
    .header h1 { font-size: 24px; font-weight: 700; color: #f8fafc; }
    .header p { color: #94a3b8; margin-top: 4px; font-size: 14px; }
    .container { max-width: 800px; margin: 0 auto; padding: 32px 16px; }
    .actions { display: flex; gap: 12px; justify-content: center; margin-bottom: 32px; flex-wrap: wrap; }
    button { padding: 12px 24px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
    button:hover { opacity: 0.9; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-generate { background: #3b82f6; color: white; }
    .btn-email { background: #10b981; color: white; }
    .spinner { display: none; text-align: center; padding: 48px; color: #94a3b8; }
    .spinner.active { display: block; }
    .spinner .dot { display: inline-block; width: 8px; height: 8px; margin: 0 4px; background: #3b82f6; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
    .spinner .dot:nth-child(1) { animation-delay: -0.32s; }
    .spinner .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    #content { display: none; }
    #content.loaded { display: block; }
    .section-title { font-size: 20px; font-weight: 700; color: #f8fafc; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #334155; }
    .cigar-title { border-color: #b45309; }
    .personal-title { border-color: #3b82f6; }
    .post-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    .post-header { font-size: 13px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }
    .post-body { white-space: pre-line; line-height: 1.7; font-size: 15px; color: #cbd5e1; }
    .post-tags { margin-top: 12px; font-size: 13px; color: #3b82f6; }
    .post-signature { margin-top: 8px; font-style: italic; color: #64748b; font-size: 14px; }
    .divider { margin: 40px 0; border: none; border-top: 1px solid #334155; }
    .toast { position: fixed; bottom: 24px; right: 24px; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; color: white; display: none; z-index: 100; }
    .toast.success { background: #10b981; display: block; }
    .toast.error { background: #ef4444; display: block; }
  </style>
</head>
<body>
  <div class="header">
    <h1>LinkedIn Content Agent</h1>
    <p>Generate your weekly cigar + personal brand posts</p>
  </div>
  <div class="container">
    <div class="actions">
      <button class="btn-generate" id="btnGenerate" onclick="generate()">Generate Weekly Content</button>
      <button class="btn-email" id="btnEmail" onclick="sendEmail()" disabled>Send to My Email</button>
    </div>
    <div class="spinner" id="spinner">
      <p style="margin-bottom: 16px;">Generating your posts... this takes about a minute</p>
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
    <div id="content"></div>
  </div>
  <div class="toast" id="toast"></div>
  <script>
    let cachedData = null;

    async function generate() {
      const btn = document.getElementById('btnGenerate');
      const spinner = document.getElementById('spinner');
      const content = document.getElementById('content');
      btn.disabled = true;
      btn.textContent = 'Generating...';
      content.className = '';
      content.innerHTML = '';
      spinner.className = 'spinner active';
      try {
        const res = await fetch('/generate-weekly-content', { method: 'POST' });
        if (!res.ok) throw new Error('Generation failed');
        cachedData = await res.json();
        render(cachedData);
        document.getElementById('btnEmail').disabled = false;
      } catch (e) {
        showToast('Failed to generate content. Check your OpenAI key.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Weekly Content';
        spinner.className = 'spinner';
      }
    }

    function render(data) {
      const content = document.getElementById('content');
      let html = '<h2 class="section-title cigar-title">Cigar Brand Posts</h2>';
      data.cigar_posts.forEach((p, i) => {
        html += postCard('Post ' + (i + 1), p);
      });
      html += '<hr class="divider">';
      html += '<h2 class="section-title personal-title">Personal Brand Posts</h2>';
      data.personal_posts.forEach((p, i) => {
        const day = p.suggested_posting_day || '';
        html += postCard('Post ' + (i + 1) + (day ? ' &middot; ' + day : ''), p);
      });
      content.innerHTML = html;
      content.className = 'loaded';
    }

    function postCard(label, post) {
      const tags = (post.hashtags || []).join(' ');
      const sig = post.signature_line ? '<div class="post-signature">' + esc(post.signature_line) + '</div>' : '';
      return '<div class="post-card">' +
        '<div class="post-header">' + label + '</div>' +
        '<div class="post-body">' + esc(post.content) + '</div>' +
        (tags ? '<div class="post-tags">' + esc(tags) + '</div>' : '') +
        sig + '</div>';
    }

    function esc(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }

    async function sendEmail() {
      if (!cachedData) return;
      const btn = document.getElementById('btnEmail');
      btn.disabled = true;
      btn.textContent = 'Sending...';
      try {
        const res = await fetch('/send-weekly-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(cachedData),
        });
        if (!res.ok) throw new Error('Email failed');
        showToast('Email sent!', 'success');
      } catch (e) {
        showToast('Failed to send email. Check SMTP settings.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Send to My Email';
      }
    }

    function showToast(msg, type) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.className = 'toast ' + type;
      setTimeout(() => { t.className = 'toast'; }, 4000);
    }
  </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@router.post("/generate-weekly-content")
def generate_weekly_content() -> dict:
    cigar = weekly_content_service.generate_cigar_content()
    personal = weekly_content_service.generate_personal_content()
    return {
        "cigar_posts": [p.model_dump() for p in cigar.posts],
        "personal_posts": [p.model_dump() for p in personal],
    }


@router.post("/send-weekly-email")
def send_weekly_email(data: dict) -> dict:
    from app.core.config import get_settings
    from app.schemas.post import GeneratedPost, GeneratePostsResponse

    settings = get_settings()
    cigar = GeneratePostsResponse(posts=[GeneratedPost(**p) for p in data["cigar_posts"]])
    personal = [GeneratedPost(**p) for p in data["personal_posts"]]
    return weekly_content_service.send_combined_weekly_email(
        email_to=settings.weekly_report_email,
        cigar_posts=cigar,
        personal_posts=personal,
    )


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
