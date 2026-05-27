"""加载并校验环境配置。系统边界做一次性校验,内部不再重复 (CLAUDE.md "不过度防御")。"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

REQUIRED = [
    "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL",
    "FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_BITABLE_APP_TOKEN",
    "FEISHU_TBL_SOURCES", "FEISHU_TBL_INSIGHTS",
    "FEISHU_TBL_ALERTS", "FEISHU_TBL_TEMPLATES",
    "FEISHU_BOT_WEBHOOK",
]

@dataclass(frozen=True)
class Config:
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    feishu_app_id: str
    feishu_app_secret: str
    feishu_bitable_app_token: str
    feishu_tbl_sources: str
    feishu_tbl_insights: str
    feishu_tbl_alerts: str
    feishu_tbl_templates: str
    feishu_bot_webhook: str

def load_config() -> Config:
    load_dotenv()
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        raise ValueError(f"missing env vars: {missing}")
    return Config(
        llm_api_key=os.environ["LLM_API_KEY"],
        llm_base_url=os.environ["LLM_BASE_URL"],
        llm_model=os.environ["LLM_MODEL"],
        feishu_app_id=os.environ["FEISHU_APP_ID"],
        feishu_app_secret=os.environ["FEISHU_APP_SECRET"],
        feishu_bitable_app_token=os.environ["FEISHU_BITABLE_APP_TOKEN"],
        feishu_tbl_sources=os.environ["FEISHU_TBL_SOURCES"],
        feishu_tbl_insights=os.environ["FEISHU_TBL_INSIGHTS"],
        feishu_tbl_alerts=os.environ["FEISHU_TBL_ALERTS"],
        feishu_tbl_templates=os.environ["FEISHU_TBL_TEMPLATES"],
        feishu_bot_webhook=os.environ["FEISHU_BOT_WEBHOOK"],
    )
