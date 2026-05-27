from unittest.mock import patch, MagicMock
import src.collectors.youtube as yt_mod
from src.collectors.youtube import YouTubeCollector

@patch.dict(yt_mod.YOUTUBE_CHANNELS, {"UCfake": "FakeLabel"}, clear=True)
@patch("src.collectors.youtube.feedparser.parse")
def test_fetch_raw_prefixes_label(mock_parse):
    fake = MagicMock()
    fake.entries = [MagicMock(link="https://y/v1", title="Demo video", published="t", summary="s")]
    mock_parse.return_value = fake
    items = YouTubeCollector().fetch_raw()
    assert len(items) == 1
    assert items[0]["title"].startswith("[FakeLabel]")
