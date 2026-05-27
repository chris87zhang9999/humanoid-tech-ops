import json
import logging
from src.llm_client import LLMClient
from src.prompts.urgent import URGENT_SYSTEM

logger = logging.getLogger(__name__)

KEY_VENDORS = {
    "Figure", "Tesla", "BostonDynamics", "Apptronik",
    "宇树", "智元", "Unitree", "Agibot", "1X",
}
KEY_TRACKS = {"VLA", "运控", "灵巧手", "Sim2Real"}

def is_urgent(llm: LLMClient, *, title: str, summary: str,
              track: str, vendor: str) -> tuple[bool, str]:
    # 规则层:快速过滤
    if vendor not in KEY_VENDORS and track not in KEY_TRACKS:
        return (False, "not in key vendor/track")
    # LLM 层
    try:
        raw = llm.chat(system=URGENT_SYSTEM,
                       user=f"赛道={track} 厂商={vendor}\n{title}\n{summary[:800]}",
                       max_tokens=120, temperature=0.0)
        data = json.loads(raw)
        return (bool(data.get("urgent")), data.get("reason", ""))
    except json.JSONDecodeError:
        # fail-closed: 解析失败默认不发预警
        logger.warning("urgent: non-JSON, fallback to non-urgent")
        return (False, "llm parse failed")
