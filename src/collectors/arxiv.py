"""arXiv 抓取 cs.RO + cs.AI 中含人形/具身/VLA 关键词的近 24h 论文。"""
import logging
import arxiv
from src.collectors.base import BaseCollector

log = logging.getLogger(__name__)

QUERY = (
    'cat:cs.RO AND ('
    'abs:"humanoid" OR abs:"embodied" OR abs:"VLA" OR '
    'abs:"vision-language-action" OR abs:"dexterous" OR abs:"sim2real"'
    ')'
)
MAX_RESULTS = 50  # arxiv API 单次上限,实测合理值见 https://arxiv.org/help/api

class ArxivCollector(BaseCollector):
    name = "arxiv"

    def fetch_raw(self) -> list[dict]:
        # page_size=50 避免单次拉 100 触发 arxiv server 429
        # delay_seconds=5 比默认 3 更礼貌,减少限流命中
        client = arxiv.Client(page_size=50, delay_seconds=5, num_retries=3)
        search = arxiv.Search(
            query=QUERY,
            max_results=MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        out: list[dict] = []
        try:
            for r in client.results(search):
                out.append({
                    "url": r.entry_id,
                    "title": r.title.strip().replace("\n", " "),
                    "published_at": r.published.isoformat(),
                    "summary": r.summary.strip().replace("\n", " "),
                })
        except arxiv.UnexpectedEmptyPageError as e:
            log.warning("arxiv empty page (likely transient): %s", e)
        return out
