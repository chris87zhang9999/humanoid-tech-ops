"""Podcast RSS feeds (Lex Fridman, Latent Space, 张小珺, etc.)."""
import logging
import feedparser
from src.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

PODCAST_FEEDS = [
    "https://lexfridman.com/feed/podcast/",
    "https://api.substack.com/feed/podcast/1084089.rss",  # Latent Space
    # 张小珺访谈 / 其它中文播客 — Phase 2 补
]

class PodcastCollector(BaseCollector):
    name = "podcast"

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for url in PODCAST_FEEDS:
            try:
                f = feedparser.parse(url)
                for e in f.entries:
                    out.append({
                        "url": getattr(e, "link", ""),
                        "title": getattr(e, "title", "").strip(),
                        "published_at": getattr(e, "published", ""),
                        "summary": getattr(e, "summary", "")[:1500],
                    })
            except Exception as ex:
                logger.warning("podcast %s: %s", url, ex)
        return out
