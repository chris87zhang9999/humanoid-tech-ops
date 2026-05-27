import pytest
from src.schemas import RawSource, Insight, TRACK_ENUM, source_hash

def test_track_enum_closed():
    assert "VLA" in TRACK_ENUM
    assert "其他" in TRACK_ENUM
    assert "随便编一个" not in TRACK_ENUM

def test_source_hash_stable():
    h1 = source_hash("https://x.com/a", "Title")
    h2 = source_hash("https://x.com/a", "Title")
    h3 = source_hash("https://x.com/b", "Title")
    assert h1 == h2
    assert h1 != h3

def test_raw_source_roundtrip():
    s = RawSource(
        hash_id="abc", url="https://x", title="t", source="arxiv",
        published_at="2026-05-26T10:00:00Z", raw_summary="s",
    )
    d = s.to_feishu_fields()
    assert d["hash_id"] == "abc"
    assert d["classified"] is False

def test_insight_validates_track():
    with pytest.raises(ValueError):
        Insight(source_hash_id="x", headline="h", track="invalid", vendor="V",
                key_facts=["a"], industry_implication="i")
