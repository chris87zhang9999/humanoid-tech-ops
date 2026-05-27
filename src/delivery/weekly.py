"""组装周报 Markdown。"""
from datetime import datetime, timezone
from src.llm_client import LLMClient
from src.prompts.weekly import WEEKLY_SYSTEM
from src.storage.bitable import BitableClient

def fetch_week_insights(bitable: BitableClient, table_id: str, days: int = 7) -> list[dict]:
    # Phase 1 数据量不大,直接拉全表; Phase 2 再用 days 做服务端过滤
    _ = days
    out = []
    for r in bitable.query_records(table_id):
        f = r.get("fields", {})
        if not f:
            continue
        out.append(f)
    return out

def group_by_track(insights: list[dict]) -> dict[str, list[dict]]:
    g: dict[str, list[dict]] = {}
    for i in insights:
        g.setdefault(i.get("track", "其他"), []).append(i)
    return g

def build_markdown(llm: LLMClient, insights: list[dict]) -> str:
    by_track = group_by_track(insights)
    user_payload = "\n\n".join(
        f"## {track}\n" + "\n".join(f"- {i.get('headline','')}" for i in items)
        for track, items in by_track.items()
    )
    summary = llm.chat(system=WEEKLY_SYSTEM, user=user_payload,
                       max_tokens=1500, temperature=0.3)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"# 具身智能技术洞察周报 ({today})\n\n{summary}\n\n---\n\n## 本周条目\n\n{user_payload}\n"
