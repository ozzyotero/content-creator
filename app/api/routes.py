from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.weekly_service import WeeklyContentService


router = APIRouter()
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
    button { padding: 12px 24px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    button:hover { opacity: 0.9; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-generate { background: #3b82f6; color: white; }
    .btn-copy { background: transparent; border: 1px solid #475569; color: #94a3b8; padding: 6px 14px; font-size: 13px; border-radius: 6px; }
    .btn-copy:hover { border-color: #3b82f6; color: #3b82f6; }
    .btn-copy.copied { border-color: #10b981; color: #10b981; }
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
    .post-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 16px; position: relative; }
    .post-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .post-label { font-size: 13px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .post-body { white-space: pre-line; line-height: 1.7; font-size: 15px; color: #cbd5e1; user-select: all; }
    .post-tags { margin-top: 12px; font-size: 13px; color: #3b82f6; }
    .post-signature { margin-top: 8px; font-style: italic; color: #64748b; font-size: 14px; }
    .divider { margin: 40px 0; border: none; border-top: 1px solid #334155; }
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
    </div>
    <div class="spinner" id="spinner">
      <p style="margin-bottom: 16px;">Generating your posts... this takes about a minute</p>
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
    <div id="content"></div>
  </div>
  <script>
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
        render(await res.json());
      } catch (e) {
        content.innerHTML = '<p style="color:#ef4444;text-align:center;">Failed to generate. Check your OpenAI key.</p>';
        content.className = 'loaded';
      } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Weekly Content';
        spinner.className = 'spinner';
      }
    }

    function render(data) {
      const content = document.getElementById('content');
      let html = '<h2 class="section-title cigar-title">Cigar Brand Posts</h2>';
      data.cigar_posts.forEach((p, i) => { html += postCard('Post ' + (i + 1), p, 'cigar-' + i); });
      html += '<hr class="divider">';
      html += '<h2 class="section-title personal-title">Personal Brand Posts</h2>';
      data.personal_posts.forEach((p, i) => {
        const day = p.suggested_posting_day || '';
        html += postCard('Post ' + (i + 1) + (day ? ' &middot; ' + day : ''), p, 'personal-' + i);
      });
      content.innerHTML = html;
      content.className = 'loaded';
    }

    function postCard(label, post, id) {
      const tags = (post.hashtags || []).join(' ');
      const sig = post.signature_line || '';
      const full = post.content + (tags ? '\\n\\n' + tags : '') + (sig ? '\\n\\n' + sig : '');
      return '<div class="post-card">' +
        '<div class="post-header">' +
          '<span class="post-label">' + label + '</span>' +
          '<button class="btn-copy" onclick="copyPost(this, \\'' + id + '\\')">Copy</button>' +
        '</div>' +
        '<div class="post-body" id="' + id + '">' + esc(post.content) + '</div>' +
        (tags ? '<div class="post-tags">' + esc(tags) + '</div>' : '') +
        (sig ? '<div class="post-signature">' + esc(sig) + '</div>' : '') +
        '<textarea id="raw-' + id + '" style="display:none">' + esc(full) + '</textarea>' +
        '</div>';
    }

    function esc(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }

    async function copyPost(btn, id) {
      const text = document.getElementById('raw-' + id).value;
      await navigator.clipboard.writeText(text);
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
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


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
