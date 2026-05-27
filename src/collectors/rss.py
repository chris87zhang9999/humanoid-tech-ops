"""通用 RSS collector,从 feeds.HUMANOID_FEEDS 拉取。"""
import logging
import feedparser
from src.collectors.base import BaseCollector
from src.collectors.feeds import HUMANOID_FEEDS

logger = logging.getLogger(__name__)

class RssCollector(BaseCollector):
    name = "rss"

    def __init__(self, feeds: list[str] | None = None):
        self._feeds = feeds if feeds is not None else HUMANOID_FEEDS

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for url in self._feeds:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries:
                    out.append({
                        "url": getattr(e, "link", ""),
                        "title": getattr(e, "title", "").strip(),
                        "published_at": getattr(e, "published", ""),
                        "summary": getattr(e, "summary", "")[:1500],
                    })
            except Exception as ex:
                # 单源失败不阻塞 (CLAUDE.md "fail-closed defaults" - 跳过该源)
                logger.warning("rss feed %s failed: %s", url, ex)
        return out
