# ADR-0002: 飞书 Bitable 作为 Source-of-Truth, 不用 SQLite / Postgres

## 背景

Agent 需要持久化原始来源 (`tbl_sources`)、结构化洞察 (`tbl_insights`)、预警记录 (`tbl_alerts`)、模板 (`tbl_templates`)。

候选方案:
- (A) GitHub Actions 内 SQLite, 文件 commit 回 repo
- (B) 远端 Postgres (Supabase / 公司内 RDS)
- (C) 飞书 Bitable

## 决策

选 (C) 飞书 Bitable, 4 张表。

## 数据依据

| 维度 | SQLite (A) | Postgres (B) | Bitable (C) |
|------|-----------|--------------|-------------|
| 用户能直接看/筛/标注 | 不能 | 不能 (要 BI) | **能** |
| 周报作者用什么改稿 | 自己写脚本 | 自己写脚本 | **直接编辑表** |
| 跨 GA Job 一致性 | repo race 风险 | OK | OK |
| 部署/初始化复杂度 | 简单 | 中 (SQL 迁移) | 简单 (建表即可) |
| 容量 (Phase 1: 千级行) | OK | OK | OK |
| Phase 2 看板/仪表盘 | 要 BI | 要 BI | **Bitable 自带** |
| 团队多人协作 | 0 | 中 (要 SQL 权限) | **强** |

最关键的: 用户希望"洞察像编辑文档一样可改、可筛、可分享", Bitable 是唯一同时满足这三项的选择。

## 权衡

**好处**:
- 用户直接编辑、筛选、给同事分享某个 view
- 0 数据库运维; 飞书机器人推送链接天然指向用户已熟悉的 UI
- 表结构在飞书里改, 代码层 `to_feishu_fields()` 只对接字段名

**代价**:
- 字段类型受 Bitable 限制 (例: 长文本 ≤ 50000 字)
- API 限流: 单批 ≤ 500 条 insert (代码已封 `BATCH_SIZE`), 长查询要分页
- 没有 SQL 复杂查询, MCP 端只能 `query_records` 然后内存过滤
- Phase 1 数据量小 (千级) 无压力, Phase 2 万级以上需评估服务端过滤

## Phase 2 触发条件

如果 `tbl_sources` 累计行数超过 50K, 或 MCP `query_insights` 单次响应 > 5s, 评估:
- 服务端 filter 表达式 (Bitable API `filter` 参数)
- 镜像一份到 Postgres 给 MCP 走 SQL
