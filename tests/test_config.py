import os
import pytest
from src.config import load_config, Config

def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://x.com/")
    monkeypatch.setenv("LLM_MODEL", "glm-4-flash")
    monkeypatch.setenv("FEISHU_APP_ID", "cli_xxx")
    monkeypatch.setenv("FEISHU_APP_SECRET", "secret")
    monkeypatch.setenv("FEISHU_BITABLE_APP_TOKEN", "tok")
    monkeypatch.setenv("FEISHU_TBL_SOURCES", "tblA")
    monkeypatch.setenv("FEISHU_TBL_INSIGHTS", "tblB")
    monkeypatch.setenv("FEISHU_TBL_ALERTS", "tblC")
    monkeypatch.setenv("FEISHU_TBL_TEMPLATES", "tblD")
    monkeypatch.setenv("FEISHU_BOT_WEBHOOK", "https://hook")
    cfg = load_config()
    assert isinstance(cfg, Config)
    assert cfg.llm_api_key == "test-key"
    assert cfg.feishu_tbl_sources == "tblA"

def test_load_config_missing_required(monkeypatch):
    for k in ["LLM_API_KEY", "FEISHU_APP_ID"]:
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(ValueError, match="missing"):
        load_config()
