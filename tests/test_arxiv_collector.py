from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from src.collectors.arxiv import ArxivCollector

@patch("src.collectors.arxiv.arxiv.Client")
@patch("src.collectors.arxiv.arxiv.Search")
def test_fetch_raw(mock_search_cls, mock_client_cls):
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

@patch("src.collectors.arxiv.arxiv.Client")
@patch("src.collectors.arxiv.arxiv.Search")
def test_fetch_raw_uses_submitted_date_window(mock_search_cls, mock_client_cls):
    """arxiv 默认按 SubmittedDate 排序但不限范围 → 拉到几个月前的旧 paper。
    必须在 query 里加 submittedDate:[NOW-7d TO NOW] 才能保证近期论文。"""
    mock_client_cls.return_value.results.return_value = iter([])
    ArxivCollector().fetch_raw()
    # 检查 Search 被调用时 query 含 submittedDate 区间
    assert mock_search_cls.called
    kwargs = mock_search_cls.call_args.kwargs
    q = kwargs.get("query") or (mock_search_cls.call_args.args[0] if mock_search_cls.call_args.args else "")
    assert "submittedDate:" in q, f"query missing date filter: {q}"
