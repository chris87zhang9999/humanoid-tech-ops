"""Funding announcements via 36氪 / IT桔子 / TechCrunch 公开 RSS。"""
import logging
import feedparser
from src.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

FUNDING_FEEDS = [
    "https://36kr.com/feed-newsflash",  # 36氪快讯,含融资
    "https://techcrunch.com/category/venture/feed/",
]

class FundingCollector(BaseCollector):
    name = "funding"

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for url in FUNDING_FEEDS:
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
                logger.warning("funding %s: %s", url, ex)
        return out
