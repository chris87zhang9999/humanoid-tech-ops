"""GitHub releases for主流 humanoid / embodied AI 仓库。
不用 GitHub API token (公共 endpoint, 限流 60/h 够用 Phase 1)。"""
import logging
import httpx
from src.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

REPOS = [
    # owner/repo
    "huggingface/lerobot",
    "openai/gym",  # placeholder; 用户可后续补具身 AI 重要仓库
]

class GithubReleaseCollector(BaseCollector):
    name = "github_release"

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for repo in REPOS:
            url = f"https://api.github.com/repos/{repo}/releases"
            try:
                r = httpx.get(url, timeout=15, headers={"Accept": "application/vnd.github+json"})
                if r.status_code != 200:
                    logger.warning("github %s: HTTP %s", repo, r.status_code)
                    continue
                for rel in r.json()[:5]:  # 最近 5 个 release
                    out.append({
                        "url": rel.get("html_url", ""),
                        "title": f"[{repo}] {rel.get('name') or rel.get('tag_name','')}",
                        "published_at": rel.get("published_at", ""),
                        "summary": (rel.get("body") or "")[:1500],
                    })
            except Exception as ex:
                logger.warning("github %s: %s", repo, ex)
        return out
