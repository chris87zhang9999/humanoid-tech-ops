"""洞察生成。LLM 失败 → 返回 None,上游决定是否跳过此条 (fail-closed)。"""
import json
import logging
from src.llm_client import LLMClient
from src.prompts.insight import INSIGHT_SYSTEM, build_user_prompt

logger = logging.getLogger(__name__)

def generate_insight(llm: LLMClient, *, title: str, summary: str,
                     track: str, vendor: str) -> dict | None:
    user = build_user_prompt(title, summary, track, vendor)
    try:
        raw = llm.chat(system=INSIGHT_SYSTEM, user=user, max_tokens=500, temperature=0.2)
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("insight: non-JSON output, skip")
        return None
    if "headline" not in data or "key_facts" not in data:
        logger.warning("insight: missing keys, skip")
        return None
    return data
