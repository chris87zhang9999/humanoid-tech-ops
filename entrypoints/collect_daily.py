"""每日采集:运行所有 collector → 去重写 tbl_sources → 跑分类 → 跑洞察 → 写 tbl_insights。"""
import logging
import sys
from src.config import load_config
from src.llm_client import LLMClient
from src.storage.bitable import BitableClient
from src.collectors.arxiv import ArxivCollector
from src.collectors.rss import RssCollector
from src.collectors.vendor import VendorCollector
from src.classifier import classify
from src.analyzer.insight import generate_insight
from src.schemas import Insight

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("collect_daily")

def main() -> int:
    cfg = load_config()
    bitable = BitableClient(cfg.feishu_app_id, cfg.feishu_app_secret, cfg.feishu_bitable_app_token)
    llm = LLMClient(cfg)

    # 1. 采集
    sources = []
    for c in [ArxivCollector(), RssCollector(), VendorCollector()]:
        try:
            sources.extend(c.collect())
        except Exception as e:
            log.error("collector %s failed: %s", c.name, e)
    log.info("total %d sources after dedup-within-batch", len(sources))

    if not sources:
        log.warning("no sources, exit")
        return 0

    # 2. 增量去重: 查 tbl_sources 中已有的 hash_id (近 30 天)
    existing = bitable.query_records(cfg.feishu_tbl_sources)
    existing_ids = {r["fields"].get("hash_id") for r in existing if r.get("fields")}
    fresh = [s for s in sources if s.hash_id not in existing_ids]
    log.info("fresh %d (filtered %d duplicates)", len(fresh), len(sources) - len(fresh))

    if not fresh:
        return 0

    # 3. 写 tbl_sources
    bitable.insert_records(cfg.feishu_tbl_sources, [s.to_feishu_fields() for s in fresh])

    # 4. 分类 + 洞察
    insights = []
    for s in fresh:
        cls = classify(llm, title=s.title, summary=s.raw_summary, source=s.source)
        ins = generate_insight(llm, title=s.title, summary=s.raw_summary,
                               track=cls["track"], vendor=cls["vendor"])
        if ins is None:
            continue
        try:
            insight = Insight(
                source_hash_id=s.hash_id,
                headline=ins["headline"],
                track=cls["track"],
                vendor=cls["vendor"],
                key_facts=ins["key_facts"],
                industry_implication=ins["industry_implication"],
            )
            insights.append(insight)
        except ValueError as e:
            log.warning("skip insight: %s", e)

    if insights:
        bitable.insert_records(cfg.feishu_tbl_insights,
                               [i.to_feishu_fields() for i in insights])
    log.info("wrote %d insights", len(insights))
    return 0

if __name__ == "__main__":
    sys.exit(main())
