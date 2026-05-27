from unittest.mock import MagicMock
from src.analyzer.urgent import is_urgent

def test_rules_filter_non_key():
    llm = MagicMock()
    urgent, _ = is_urgent(llm, title="t", summary="s", track="政策标准", vendor="未知")
    assert urgent is False
    llm.chat.assert_not_called()

def test_llm_called_when_key():
    llm = MagicMock()
    llm.chat.return_value = '{"urgent": true, "reason": "新品发布"}'
    urgent, reason = is_urgent(llm, title="t", summary="s", track="VLA", vendor="Figure")
    assert urgent is True
    assert "新品" in reason
