"""LLM 输出 JSON 解析容错。GLM-4-flash 习惯套 ```json 围栏或在前后加解释。"""
import json
import re

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
# 第一个匹配的最外层大括号块, non-greedy 但跨行
_BRACE_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_lenient_json(raw: str) -> dict:
    """尝试 strict parse → 剥 markdown 围栏 → 抠最外层大括号。三连失败 raises JSONDecodeError。"""
    s = raw.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    m = _FENCE_RE.search(s)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    m = _BRACE_RE.search(s)
    if m:
        return json.loads(m.group(0))
    raise json.JSONDecodeError("no JSON found", s, 0)
