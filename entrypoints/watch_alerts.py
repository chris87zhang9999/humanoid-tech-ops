"""每 15 分钟轻量轮询。只跑高时效 collector,只跑突发判定。"""
import logging
import sys
from src.config import load_config
from src.llm_client import LLMClient
from src.storage.bitable import BitableClient
from src.collectors.vendor import VendorCollector
from src.collectors.rss import RssCollector
from src.classifier import classify
from src.analyzer.urgent import is_urgent
from src.delivery.alert import push_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("watch")

def main() -> int:
    cfg = load_config()
    bitable = BitableClient(cfg.feishu_app_id, cfg.feishu_app_secret, cfg.feishu_bitable_app_token)
    llm = LLMClient(cfg)

    sources = []
    for c in [VendorCollector(), RssCollector()]:
        try:
            sources.extend(c.collect())
        except Exception as e:
            log.error("%s failed: %s", c.name, e)

    # 增量去重(共用 tbl_sources)
    existing = bitable.query_records(cfg.feishu_tbl_sources)
    existing_ids = {r["fields"].get("hash_id") for r in existing if r.get("fields")}
    fresh = [s for s in sources if s.hash_id not in existing_ids]

    if not fresh:
        return 0

    bitable.insert_records(cfg.feishu_tbl_sources, [s.to_feishu_fields() for s in fresh])

    alerts = 0
    for s in fresh:
        cls = classify(llm, title=s.title, summary=s.raw_summary, source=s.source)
        urgent, reason = is_urgent(llm, title=s.title, summary=s.raw_summary,
                                    track=cls["track"], vendor=cls["vendor"])
        if not urgent:
            continue
        push_alert(cfg.feishu_bot_webhook, headline=s.title, track=cls["track"],
                   vendor=cls["vendor"], url=s.url, reason=reason)
        bitable.insert_records(cfg.feishu_tbl_alerts, [{
            "trigger_at": s.published_at, "track": cls["track"],
            "vendor": cls["vendor"], "headline": s.title,
            "source_url": s.url, "pushed": True,
        }])
        alerts += 1
    log.info("triggered %d alerts", alerts)
    return 0

if __name__ == "__main__":
    sys.exit(main())
