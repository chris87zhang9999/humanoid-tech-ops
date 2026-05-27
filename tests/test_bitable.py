from unittest.mock import patch, MagicMock
from src.storage.bitable import BitableClient

CFG_KW = dict(
    app_id="cli", app_secret="sec", app_token="tok",
)

@patch("src.storage.bitable.httpx.Client")
def test_get_tenant_token(mock_httpx):
    inst = mock_httpx.return_value
    inst.post.return_value.json.return_value = {"code": 0, "tenant_access_token": "t_xxx"}
    c = BitableClient(**CFG_KW)
    assert c._tenant_token() == "t_xxx"

@patch("src.storage.bitable.httpx.Client")
def test_insert_records_batches(mock_httpx):
    inst = mock_httpx.return_value
    inst.post.side_effect = [
        MagicMock(**{"json.return_value": {"code": 0, "tenant_access_token": "t"}}),
        MagicMock(**{"json.return_value": {"code": 0, "data": {"records": [{"record_id": "r1"}]}}}),
    ]
    c = BitableClient(**CFG_KW)
    ids = c.insert_records("tblX", [{"title": "a"}])
    assert ids == ["r1"]
