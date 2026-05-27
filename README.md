# humanoid-tech-ops

人形机器人行业技术运营 Agent。7×24 自动采集行业全栈信息 → 赛道归类 → 周报 + 突发预警 → 提供 MCP 让 Claude Code 即时查询。

设计文档: [docs/plans/2026-05-26-humanoid-tech-ops-agent-design.md](docs/plans/2026-05-26-humanoid-tech-ops-agent-design.md)

## Status

Phase 1 MVP, 开发中。

## MCP 安装 (本地 Claude Code)

1. clone 本仓库到本地: `git clone https://github.com/chris87zhang9999/humanoid-tech-ops.git`
2. `cd humanoid-tech-ops && ept uv sync`
3. 复制 `.env.example` → `.env`,填入飞书凭证
4. 在 `~/.claude.json` 的 `mcpServers` 加:

```json
"humanoid-tech-ops": {
  "command": "/Users/<你>/humanoid-tech-ops/.venv/bin/python",
  "args": ["-m", "entrypoints.mcp_server"],
  "cwd": "/Users/<你>/humanoid-tech-ops"
}
```

5. 重启 Claude Code,问"最近 VLA 有什么进展"测试。
