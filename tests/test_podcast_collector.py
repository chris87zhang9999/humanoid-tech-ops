from unittest.mock import patch, MagicMock
from src.collectors.podcast import PodcastCollector

@patch("src.collectors.podcast.feedparser.parse")
def test_fetch_raw(mock_parse):
    fake = MagicMock()
    fake.entries = [MagicMock(link="https://x", title="ep1", published="t", summary="s")]
    mock_parse.return_value = fake
    items = PodcastCollector().fetch_raw()
    assert any(i["title"] == "ep1" for i in items)
