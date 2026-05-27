from unittest.mock import patch, MagicMock
from src.collectors.vendor import VendorCollector

@patch("src.collectors.vendor.feedparser.parse")
def test_prefixes_vendor(mock_parse):
    fake = MagicMock()
    fake.entries = [MagicMock(link="https://x", title="Launch", published="t", summary="s")]
    mock_parse.return_value = fake
    items = VendorCollector().fetch_raw()
    assert all(i["title"].startswith("[") for i in items)
