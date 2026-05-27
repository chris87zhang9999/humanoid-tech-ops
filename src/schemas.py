"""数据模型与赛道枚举。封闭枚举防 LLM 编造分类 (CLAUDE.md "约束优于鼓励")。"""
import hashlib
from dataclasses import dataclass, field
from typing import Final

TRACK_ENUM: Final[set[str]] = {
    "VLA", "运控", "灵巧手", "Sim2Real",
    "整机硬件", "数据采集", "产业链", "政策标准", "其他",
}

def source_hash(url: str, title: str) -> str:
    """URL + 标题做 SHA1 前 16 位,用于跨 collector 去重。"""
    return hashlib.sha1(f"{url}||{title}".encode()).hexdigest()[:16]

@dataclass
class RawSource:
    hash_id: str
    url: str
    title: str
    source: str        # arxiv / rss / vendor / youtube / podcast / github_release / funding
    published_at: str  # ISO8601
    raw_summary: str
    classified: bool = False

    def to_feishu_fields(self) -> dict:
        return {
            "hash_id": self.hash_id,
            "url": self.url,
            "title": self.title,
            "source": self.source,
            "published_at": self.published_at,
            "raw_summary": self.raw_summary,
            "classified": self.classified,
        }

@dataclass
class Insight:
    source_hash_id: str
    headline: str
    track: str
    vendor: str
    key_facts: list[str]
    industry_implication: str

    def __post_init__(self):
        if self.track not in TRACK_ENUM:
            raise ValueError(f"track {self.track!r} not in {TRACK_ENUM}")

    def to_feishu_fields(self) -> dict:
        return {
            "source_hash_id": self.source_hash_id,
            "headline": self.headline,
            "track": self.track,
            "vendor": self.vendor,
            "key_facts": "\n".join(f"- {f}" for f in self.key_facts),
            "industry_implication": self.industry_implication,
        }
