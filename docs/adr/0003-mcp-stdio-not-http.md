# ADR-0003: Phase 1 用 stdio MCP, 不部署 HTTP MCP

## 背景

希望在 Claude Code 里直接问"最近 VLA 怎么样", 让 agent 查飞书表里沉淀的洞察并返回 markdown。

MCP server 有两种部署形态:
- (A) **stdio**: Claude Code 启动时 fork 一个本地子进程, 走 stdin/stdout 通信
- (B) **HTTP**: 独立服务, 走 HTTP/SSE, 可被任何 MCP client 远程访问

## 决策

Phase 1 选 (A) stdio, 通过 `~/.claude.json` 的 `mcpServers` 段配置启动命令。

## 数据依据

- 当前需求只服务一个用户 (本人) + 一台机器 (Mac)
- Claude Code 是唯一消费方, 无远程协作需求
- 飞书 App ID/Secret 已经在本机环境变量, stdio 子进程可直接读, 不需要部署侧再配
- HTTP MCP 部署额外引入: 鉴权层 / 反向代理 / TLS 证书 / 进程管理 / 公网入口 → 这些都是工作量, 没有对应收益

## 权衡

**好处**:
- 0 部署成本, `pyproject.toml` 装依赖即可用
- 凭证本地化, 无外泄面
- 启动参数全在 `~/.claude.json`, 修改不需要重启服务

**代价**:
- 仅自己机器可用, 无法和同事共享
- Claude Code 启动时要 fork 子进程, 首次冷启动延迟 ~1s

## Phase 2 触发条件

升 HTTP MCP 的明确信号 (任一即可):
- 同事希望从他自己的 Claude Code 查同一份洞察库
- 在飞书机器人里加 "@bot 查 VLA 进展" 的对话能力 (机器人 → HTTP MCP)
- 在公司内网部署 webhook / 自动化 pipeline 消费 MCP

升级时保留 `mcp_server.py` 的 tool 定义, 把 transport 从 stdio 切到 SSE/HTTP 即可, 业务逻辑无需改。
