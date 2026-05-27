from unittest.mock import patch, MagicMock
from src.collectors.funding import FundingCollector

@patch("src.collectors.funding.feedparser.parse")
def test_fetch_raw(mock_parse):
    fake = MagicMock()
    fake.entries = [MagicMock(link="https://k/1", title="X 公司完成 1 亿融资",
                              published="t", summary="s")]
    mock_parse.return_value = fake
    items = FundingCollector().fetch_raw()
    assert any("融资" in i["title"] for i in items)
