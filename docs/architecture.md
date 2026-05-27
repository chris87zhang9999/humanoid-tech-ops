# 架构总览

## 一句话定位

具身智能赛道 7×24 情报与洞察 Agent: 抓 → 分类 → 沉淀 → 周报 + 实时预警 + MCP 即时查询。

## 数据流

```
                  ┌────────────────────────────────────────────┐
                  │  数据源 (公开)                                │
                  │  arxiv / RSS / Vendor blog / YouTube /      │
                  │  Podcast / GitHub releases / Funding RSS    │
                  └─────────────────────┬──────────────────────┘
                                        │
                          ┌─────────────▼──────────────┐
                          │  collectors/* (统一 RawSource) │
                          └─────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
        ┌─────▼─────┐             ┌─────▼─────┐             ┌─────▼─────┐
        │ daily 1AM │             │ alerts15m │             │ weekly 一│
        │ collect   │             │  watch    │             │  build   │
        └─────┬─────┘             └─────┬─────┘             └─────┬────┘
              │                         │                         │
              │  classify (LLM)         │  rule pre-filter +      │  group_by_track
              │  insight (LLM)          │  is_urgent (LLM)        │  + LLM 总结
              │                         │                         │
        ┌─────▼─────────────────────────▼───────┐         ┌──────▼──────┐
        │           飞书 Bitable (SoT)            │         │ reports/*.md│
        │  tbl_sources / tbl_insights / tbl_alerts│         │   (git)     │
        └────────────────────┬────────────────────┘         └──────┬──────┘
                             │                                     │
                ┌────────────▼─────────────┐         ┌────────────▼─────────┐
                │  MCP stdio: query_insights│         │  飞书机器人 webhook   │
                │     / search_sources      │         │  (周报链接 + 预警)    │
                └────────────┬──────────────┘         └──────────────────────┘
                             │
                       ┌─────▼─────┐
                       │ Claude Code│
                       └────────────┘
```

## 分层

| 层 | 路径 | 职责 |
|----|------|------|
| 入口 | `entrypoints/` | 4 个调用方: collect_daily / build_weekly / watch_alerts / mcp_server |
| 引擎 | `src/` | 无头 (headless), 不依赖任何入口框架 |
| Collectors | `src/collectors/` | 7 类源, 统一产出 `RawSource` |
| LLM | `src/llm_client.py` | OpenAI 兼容协议, 重试 x3 |
| 分类/分析 | `src/classifier.py` `src/analyzer/` | 闭枚举 + JSON schema 防编造 |
| 存储 | `src/storage/bitable.py` | 飞书 Bitable 客户端, batch ≤ 500 |
| 投递 | `src/delivery/` | 周报 markdown + 实时预警 |
| Prompts | `src/prompts/` | system 提示词, 分文件,可独立迭代 |

## 关键决策摘要

参见 `docs/adr/`:
- ADR-0001: LLM provider 选 GLM-4-flash + multi-provider
- ADR-0002: 飞书 Bitable 作为 SoT, 不用 SQLite
- ADR-0003: Phase 1 用 stdio MCP, 不部署 HTTP MCP

## 安全 / Fail-Closed 默认

- 闭枚举 `TRACK_ENUM` (9 个赛道), LLM 返回非法值时 fallback `"其他"`
- LLM 解析失败 → insight 直接丢弃, 不写表
- urgent 判定双层: 规则预筛 + LLM 复核, 任一未过 = 不推送
- 外部内容只走 user message, 永远不进 system prompt (防注入)
- Tenacity 重试 x3 + 指数退避, 超过即 raise (避免雪崩)

## CI / 调度

| Workflow | Cron | 作用 |
|----------|------|------|
| `collect-daily.yml` | `0 1 * * *` UTC | 全量 collector + classify + insight |
| `weekly-report.yml` | `30 0 * * 1` UTC | 拉本周 insights + LLM 总结 → reports/ + 飞书机器人 |
| `alert-watch.yml` | `*/15 * * * *` | 仅 vendor + RSS, 仅判定突发 |
| `ci.yml` | push / PR | ruff + pytest |

## Phase 2 候选

- collector 加 PaperWithCode / Twitter (X) / Hugging Face Models
- bitable view / 时间过滤改为服务端
- LLM 升级 glm-4-plus 或切 DeepSeek
- HTTP MCP (远端共享时再做)
