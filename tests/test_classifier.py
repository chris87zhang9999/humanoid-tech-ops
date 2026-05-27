import json
from unittest.mock import MagicMock
from src.classifier import classify

def test_classify_valid_track():
    llm = MagicMock()
    llm.chat.return_value = json.dumps({"track": "VLA", "vendor": "Figure", "confidence": 0.9})
    out = classify(llm, title="Figure VLA paper", summary="...", source="arxiv")
    assert out["track"] == "VLA"
    assert out["vendor"] == "Figure"

def test_classify_invalid_track_falls_back():
    llm = MagicMock()
    llm.chat.return_value = json.dumps({"track": "胡编", "vendor": "X", "confidence": 0.5})
    out = classify(llm, title="t", summary="s", source="arxiv")
    assert out["track"] == "其他"

def test_classify_malformed_json_falls_back():
    llm = MagicMock()
    llm.chat.return_value = "not json"
    out = classify(llm, title="t", summary="s", source="arxiv")
    assert out["track"] == "其他"

def test_classify_content_filter_falls_back():
    # 智谱 content filter 返回 BadRequestError, 不该让整个 pipeline 崩
    from openai import BadRequestError
    import httpx
    llm = MagicMock()
    llm.chat.side_effect = BadRequestError(
        message="content filter",
        response=httpx.Response(400, request=httpx.Request("POST", "http://x")),
        body={"error": {"code": "1301"}},
    )
    out = classify(llm, title="t", summary="s", source="arxiv")
    assert out["track"] == "其他"
    assert out["vendor"] == "未知"
