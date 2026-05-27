"""一线人形机器人厂商官方 RSS / 新闻 feed。"""
import feedparser
import logging
from src.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

VENDOR_FEEDS = {
    # name → feed_url。无 RSS 的留 Phase 2 用 readability 抓页面。
    "Figure":  "https://www.figure.ai/news.rss",            # 实测前先确认存在
    "BostonDynamics": "https://bostondynamics.com/feed/",
    "Apptronik": "https://apptronik.com/news?format=rss",
    # Tesla / Unitree / 智元 / 宇树 — 多无标准 RSS,Phase 1 先在 RssCollector 里覆盖一线媒体的厂商报道
}

class VendorCollector(BaseCollector):
    name = "vendor"

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for vendor, url in VENDOR_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for e in feed.entries:
                    out.append({
                        "url": getattr(e, "link", ""),
                        "title": f"[{vendor}] " + getattr(e, "title", "").strip(),
                        "published_at": getattr(e, "published", ""),
                        "summary": getattr(e, "summary", "")[:1500],
                    })
            except Exception as ex:
                logger.warning("vendor feed %s failed: %s", vendor, ex)
        return out
