"""arXiv 抓取 cs.RO + cs.AI 中含人形/具身/VLA 关键词的近 24h 论文。"""
import arxiv
from src.collectors.base import BaseCollector

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
        client = arxiv.Client()
        search = arxiv.Search(
            query=QUERY,
            max_results=MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        out: list[dict] = []
        for r in client.results(search):
            out.append({
                "url": r.entry_id,
                "title": r.title.strip().replace("\n", " "),
                "published_at": r.published.isoformat(),
                "summary": r.summary.strip().replace("\n", " "),
            })
        return out
