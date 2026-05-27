"""赛道归类。LLM 输出 JSON schema 校验失败则降级到'其他' (CLAUDE.md "优雅降级")。"""
import json
import logging
from src.llm_client import LLMClient
from src.prompts.classify import CLASSIFY_SYSTEM, build_user_prompt
from src.schemas import TRACK_ENUM

logger = logging.getLogger(__name__)

def classify(llm: LLMClient, *, title: str, summary: str, source: str) -> dict:
    user = build_user_prompt(title, summary, source)
    try:
        raw = llm.chat(system=CLASSIFY_SYSTEM, user=user, max_tokens=200, temperature=0.0)
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("classify: LLM returned non-JSON, fallback")
        return {"track": "其他", "vendor": "未知", "confidence": 0.0}
    track = data.get("track", "其他")
    if track not in TRACK_ENUM:
        logger.warning("classify: track %r not in enum, fallback", track)
        track = "其他"
    return {
        "track": track,
        "vendor": data.get("vendor", "未知"),
        "confidence": float(data.get("confidence", 0.0)),
    }
