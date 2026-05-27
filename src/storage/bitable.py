"""飞书 Bitable 薄适配层。所有 entrypoint/MCP 走这里,禁止跳过 (CLAUDE.md 口径一致)。"""
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

BASE = "https://open.feishu.cn/open-apis"
BATCH_SIZE = 500  # 飞书 batch_create 上限,见 https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_create


def recent_filter(field: str, days: int) -> str:
    """构造 Bitable v1 filter,只查 field >= 当前-days 天的记录。
    field 必须是 text 类型且存 ISO8601 字符串 (lexicographic 可比)。
    用于增量去重防止全表扫描 (CLAUDE.md "魔法数字必须标注来源" - 30 天 = arxiv 索引最大延迟 + 1 周缓冲)。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    return f'CurrentValue.[{field}]>"{cutoff}"'


class BitableClient:
    def __init__(self, app_id: str, app_secret: str, app_token: str):
        self._app_id = app_id
        self._app_secret = app_secret
        self._app_token = app_token
        self._http = httpx.Client(timeout=30.0)
        self._token: str | None = None
        self._token_exp = 0.0

    def _tenant_token(self) -> str:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        r = self._http.post(
            f"{BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": self._app_id, "app_secret": self._app_secret},
        )
        data = r.json()
        if data.get("code") != 0:
            raise RuntimeError(f"tenant_token failed: {data}")
        self._token = data["tenant_access_token"]
        self._token_exp = time.time() + data.get("expire", 7200)
        return self._token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._tenant_token()}", "Content-Type": "application/json"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def insert_records(self, table_id: str, records: list[dict[str, Any]]) -> list[str]:
        url = f"{BASE}/bitable/v1/apps/{self._app_token}/tables/{table_id}/records/batch_create"
        ids: list[str] = []
        for i in range(0, len(records), BATCH_SIZE):
            chunk = records[i : i + BATCH_SIZE]
            r = self._http.post(url, headers=self._headers(),
                                json={"records": [{"fields": f} for f in chunk]})
            data = r.json()
            if data.get("code") != 0:
                raise RuntimeError(f"insert_records failed: {data}")
            ids.extend(rec["record_id"] for rec in data["data"]["records"])
        return ids

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def query_records(self, table_id: str, *, filter_: str | None = None,
                      page_size: int = 200) -> list[dict[str, Any]]:
        url = f"{BASE}/bitable/v1/apps/{self._app_token}/tables/{table_id}/records"
        params: dict[str, Any] = {"page_size": page_size}
        if filter_:
            params["filter"] = filter_
        out: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            if page_token:
                params["page_token"] = page_token
            r = self._http.get(url, headers=self._headers(), params=params)
            data = r.json()
            if data.get("code") != 0:
                raise RuntimeError(f"query_records failed: {data}")
            out.extend(data["data"].get("items", []))
            if not data["data"].get("has_more"):
                break
            page_token = data["data"].get("page_token")
        return out

    def update_record(self, table_id: str, record_id: str, fields: dict[str, Any]) -> None:
        url = f"{BASE}/bitable/v1/apps/{self._app_token}/tables/{table_id}/records/{record_id}"
        r = self._http.put(url, headers=self._headers(), json={"fields": fields})
        data = r.json()
        if data.get("code") != 0:
            raise RuntimeError(f"update_record failed: {data}")
