import json
from unittest.mock import MagicMock
from src.analyzer.insight import generate_insight

def test_generate_insight_ok():
    llm = MagicMock()
    llm.chat.return_value = json.dumps({
        "headline": "Figure 02 进入 BMW 工厂",
        "key_facts": ["10h 连续作业", "新驱动器", "BMW"],
        "industry_implication": "首例人形车厂量产试点",
    })
    out = generate_insight(llm, title="t", summary="s", track="VLA", vendor="Figure")
    assert out["headline"].startswith("Figure")
    assert len(out["key_facts"]) == 3

def test_generate_insight_malformed_returns_none():
    llm = MagicMock()
    llm.chat.return_value = "garbage"
    assert generate_insight(llm, title="t", summary="s", track="VLA", vendor="V") is None

def test_generate_insight_content_filter_returns_none():
    # 智谱 content filter 返回 BadRequestError, 不该让整个 pipeline 崩
    from openai import BadRequestError
    import httpx
    llm = MagicMock()
    llm.chat.side_effect = BadRequestError(
        message="content filter",
        response=httpx.Response(400, request=httpx.Request("POST", "http://x")),
        body={"error": {"code": "1301"}},
    )
    assert generate_insight(llm, title="t", summary="s", track="VLA", vendor="V") is None
