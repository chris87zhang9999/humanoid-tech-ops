from unittest.mock import patch, MagicMock
from src.collectors.rss import RssCollector

FAKE_FEED = MagicMock()
FAKE_FEED.entries = [
    MagicMock(link="https://r/a", title="Robot launch",
              published="2026-05-26T00:00:00Z", summary="x"),
]

@patch("src.collectors.rss.feedparser.parse", return_value=FAKE_FEED)
def test_fetch_raw_iterates_feeds(_p):
    items = RssCollector(["https://feed1"]).fetch_raw()
    assert len(items) == 1
    assert items[0]["title"] == "Robot launch"
