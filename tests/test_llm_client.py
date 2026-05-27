from unittest.mock import MagicMock, patch
from src.llm_client import LLMClient
from src.config import Config

def make_cfg():
    return Config(
        llm_api_key="k", llm_base_url="https://x/", llm_model="glm-4-flash",
        feishu_app_id="x", feishu_app_secret="x", feishu_bitable_app_token="x",
        feishu_tbl_sources="x", feishu_tbl_insights="x",
        feishu_tbl_alerts="x", feishu_tbl_templates="x",
        feishu_bot_webhook="x",
    )

@patch("src.llm_client.OpenAI")
def test_chat_returns_content(mock_openai):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="hello"))]
    mock_openai.return_value.chat.completions.create.return_value = mock_resp
    client = LLMClient(make_cfg())
    out = client.chat(system="sys", user="hi")
    assert out == "hello"

@patch("src.llm_client.OpenAI")
def test_chat_retries_on_failure(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = [
        Exception("transient"), Exception("transient"),
        MagicMock(choices=[MagicMock(message=MagicMock(content="ok"))]),
    ]
    client = LLMClient(make_cfg())
    assert client.chat(system="s", user="u") == "ok"
    assert mock_client.chat.completions.create.call_count == 3
