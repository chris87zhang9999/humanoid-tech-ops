import logging, sys
from datetime import datetime
from pathlib import Path
import httpx
from src.config import load_config
from src.llm_client import LLMClient
from src.storage.bitable import BitableClient
from src.delivery.weekly import fetch_week_insights, build_markdown

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("weekly")

def main() -> int:
    cfg = load_config()
    bitable = BitableClient(cfg.feishu_app_id, cfg.feishu_app_secret, cfg.feishu_bitable_app_token)
    llm = LLMClient(cfg)

    insights = fetch_week_insights(bitable, cfg.feishu_tbl_insights)
    if not insights:
        log.warning("no insights this week, skip")
        return 0

    md = build_markdown(llm, insights)

    # 写到 reports/YYYY-WW.md (commit 由 Action 完成)
    iso_year, iso_week, _ = datetime.utcnow().isocalendar()
    out = Path("reports") / f"{iso_year}-W{iso_week:02d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    log.info("wrote %s", out)

    # 推送到飞书机器人 (链接到 GitHub Public 路径)
    repo = "chris87zhang9999/humanoid-tech-ops"
    link = f"https://github.com/{repo}/blob/main/{out.as_posix()}"
    httpx.post(cfg.feishu_bot_webhook, json={
        "msg_type": "text",
        "content": {"text": f"📊 本周具身智能技术洞察周报已生成:\n{link}"},
    }, timeout=15)
    return 0

if __name__ == "__main__":
    sys.exit(main())
