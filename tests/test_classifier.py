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

def test_classify_strips_markdown_fence():
    # GLM-4-flash 实际输出常带 ```json 围栏,要能抠出来
    llm = MagicMock()
    llm.chat.return_value = '```json\n{"track": "VLA", "vendor": "Figure", "confidence": 0.8}\n```'
    out = classify(llm, title="t", summary="s", source="arxiv")
    assert out["track"] == "VLA"
    assert out["vendor"] == "Figure"

def test_classify_extracts_json_from_prose():
    # LLM 习惯在前后加解释文字,要能从中抠出 JSON
    llm = MagicMock()
    llm.chat.return_value = '根据标题和摘要,这条属于 VLA 赛道。{"track": "VLA", "vendor": "Figure", "confidence": 0.7} 以上分析。'
    out = classify(llm, title="t", summary="s", source="arxiv")
    assert out["track"] == "VLA"

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
