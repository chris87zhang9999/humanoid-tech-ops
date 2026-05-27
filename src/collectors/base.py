"""Collector 基类: 抓 → 去重 → 转 RawSource。子类只实现 fetch_raw。"""
import logging
from abc import ABC, abstractmethod
from src.schemas import RawSource, source_hash

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    name: str = "base"

    @abstractmethod
    def fetch_raw(self) -> list[dict]:
        """返回 dict 列表,每个含 url/title/published_at/summary。"""

    def collect(self) -> list[RawSource]:
        raw = self.fetch_raw()
        seen: set[str] = set()
        out: list[RawSource] = []
        for item in raw:
            try:
                h = source_hash(item["url"], item["title"])
                if h in seen:
                    continue
                seen.add(h)
                out.append(RawSource(
                    hash_id=h,
                    url=item["url"],
                    title=item["title"],
                    source=self.name,
                    published_at=item["published_at"],
                    raw_summary=item.get("summary", ""),
                ))
            except KeyError as e:
                logger.warning("collector=%s skip malformed item: missing %s", self.name, e)
        logger.info("collector=%s collected %d (dedup from %d)", self.name, len(out), len(raw))
        return out
