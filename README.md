# humanoid-tech-ops

人形机器人行业技术运营 Agent。7×24 自动采集行业全栈信息 → 赛道归类 → 周报 + 突发预警 → 提供 MCP 让 Claude Code 即时查询。

## Status

Phase 1 MVP。

## 架构 / 决策

- 架构总览: [docs/architecture.md](docs/architecture.md)
- 关键决策: [docs/adr/](docs/adr/)
- 完整实现计划: [docs/plans/2026-05-26-humanoid-tech-ops-implementation.md](docs/plans/2026-05-26-humanoid-tech-ops-implementation.md)

## 调度

| Workflow | Cron (UTC) | 作用 |
|----------|-----------|------|
| `collect-daily.yml` | `0 1 * * *` | 全量 collector + 分类 + 提炼洞察 |
| `weekly-report.yml` | `30 0 * * 1` | 拉本周 insights → LLM 总结 → reports/ + 飞书机器人 |
| `alert-watch.yml` | `*/15 * * * *` | 仅 vendor + RSS, 仅判定突发 |
| `ci.yml` | push / PR | ruff + pytest |

## 本地运行

```bash
# 1. 安装依赖
ept uv sync --extra dev

# 2. 配置 secrets
cp .env.example .env
$EDITOR .env  # 填入 LLM_API_KEY / FEISHU_APP_ID 等

# 3. 单次运行
ept uv run python -m entrypoints.collect_daily
ept uv run python -m entrypoints.build_weekly
ept uv run python -m entrypoints.watch_alerts

# 4. 测试
ept uv run pytest -v
ept uv run ruff check src/ entrypoints/ tests/
```

## MCP 安装 (本地 Claude Code)

1. clone 本仓库: `git clone https://github.com/chris87zhang9999/humanoid-tech-ops.git`
2. `cd humanoid-tech-ops && ept uv sync`
3. 复制 `.env.example` → `.env`, 填入飞书凭证
4. 在 `~/.claude.json` 的 `mcpServers` 加:

```json
"humanoid-tech-ops": {
  "command": "/Users/<你>/humanoid-tech-ops/.venv/bin/python",
  "args": ["-m", "entrypoints.mcp_server"],
  "cwd": "/Users/<你>/humanoid-tech-ops"
}
```

5. 重启 Claude Code, 问"最近 VLA 有什么进展"测试。

## 暴露的 MCP tools

- `query_insights(track, since_days, vendors, keywords)` — 查 `tbl_insights` 沉淀的结构化洞察, 按厂商分组返回 markdown
- `search_sources(keyword, since_days)` — 全文搜 `tbl_sources` 原始来源

## 部署到 GitHub Actions

仓库 Settings → Secrets and variables → Actions, 添加:

| Secret | 说明 |
|--------|------|
| `LLM_API_KEY` | 智谱 / DeepSeek 等 OpenAI 兼容 provider 的 key |
| `LLM_BASE_URL` | 例: `https://open.bigmodel.cn/api/paas/v4/` |
| `LLM_MODEL` | 例: `glm-4-flash` |
| `FEISHU_APP_ID` | 飞书自建应用 App ID |
| `FEISHU_APP_SECRET` | 飞书自建应用 App Secret |
| `FEISHU_BITABLE_APP_TOKEN` | Bitable app token (URL 中 `/base/<这段>`) |
| `FEISHU_TBL_SOURCES` | tbl_sources 表 ID |
| `FEISHU_TBL_INSIGHTS` | tbl_insights 表 ID |
| `FEISHU_TBL_ALERTS` | tbl_alerts 表 ID |
| `FEISHU_TBL_TEMPLATES` | tbl_templates 表 ID |
| `FEISHU_BOT_WEBHOOK` | 群机器人 webhook URL |

## License

私有, 暂未授权第三方使用。
