from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from src.collectors.arxiv import ArxivCollector

@patch("src.collectors.arxiv.arxiv.Client")
def test_fetch_raw(mock_client_cls):
    res = MagicMock()
    res.entry_id = "https://arxiv.org/abs/2501.00001"
    res.title = "VLA paper"
    res.summary = "Abs"
    res.published = datetime(2026, 5, 25, 10, 0, tzinfo=timezone.utc)
    mock_client_cls.return_value.results.return_value = iter([res])
    items = ArxivCollector().fetch_raw()
    assert len(items) == 1
    assert items[0]["title"] == "VLA paper"
    assert items[0]["url"].startswith("https://arxiv.org")
