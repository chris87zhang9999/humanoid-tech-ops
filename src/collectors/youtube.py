"""YouTube channel uploads via channel-level RSS (no API key required).
Phase 2 可改 YouTube Data API v3 拿到更多元数据。"""
import logging
import feedparser
from src.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

# channel_id -> 厂商或频道名。format: https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx
YOUTUBE_CHANNELS = {
    # Phase 1 占位:用户后续按需补 channel_id。每条 = (channel_id, label)
    # 例: ("UCBpxspUNl1Th33XbugiHJzw", "BostonDynamics"),
}

class YouTubeCollector(BaseCollector):
    name = "youtube"

    def fetch_raw(self) -> list[dict]:
        out: list[dict] = []
        for channel_id, label in YOUTUBE_CHANNELS.items():
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            try:
                f = feedparser.parse(url)
                for e in f.entries:
                    out.append({
                        "url": getattr(e, "link", ""),
                        "title": f"[{label}] " + getattr(e, "title", "").strip(),
                        "published_at": getattr(e, "published", ""),
                        "summary": getattr(e, "summary", "")[:1500] if hasattr(e, "summary") else "",
                    })
            except Exception as ex:
                logger.warning("youtube %s: %s", label, ex)
        return out
