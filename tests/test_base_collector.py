from src.collectors.base import BaseCollector
from src.schemas import RawSource

class FakeCollector(BaseCollector):
    name = "fake"
    def fetch_raw(self):
        return [
            {"url": "https://a", "title": "T1", "published_at": "2026-05-26T00:00:00Z", "summary": "s1"},
            {"url": "https://a", "title": "T1", "published_at": "2026-05-26T00:00:00Z", "summary": "s1"},  # dup
            {"url": "https://b", "title": "T2", "published_at": "2026-05-26T00:00:00Z", "summary": "s2"},
        ]

def test_dedup_within_batch():
    out = FakeCollector().collect()
    assert len(out) == 2
    assert all(isinstance(x, RawSource) for x in out)
    assert out[0].source == "fake"
