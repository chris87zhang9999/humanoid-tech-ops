"""stdio MCP server: 让 Claude Code 即时查询飞书表里沉淀的洞察。
通过 ~/.claude.json mcpServers 配置启动 (见 README)。"""
import json
from datetime import datetime, timedelta, timezone
from mcp.server.fastmcp import FastMCP
from src.config import load_config
from src.storage.bitable import BitableClient

cfg = load_config()
bitable = BitableClient(cfg.feishu_app_id, cfg.feishu_app_secret, cfg.feishu_bitable_app_token)
mcp = FastMCP("humanoid-tech-ops")

@mcp.tool()
def query_insights(track: str = "", since_days: int = 7,
                   vendors: list[str] | None = None,
                   keywords: list[str] | None = None) -> str:
    """查询本地沉淀的洞察。

    何时调用: 用户问"最近 VLA 怎么样"、"Figure 这周有啥动作"、"上个月灵巧手进展" 等。
    何时不调用: 用户问最新外部新闻 (这是历史沉淀,不是实时新闻)。

    参数:
        track: 赛道。空字符串 = 不过滤。可选值: VLA / 运控 / 灵巧手 / Sim2Real / 整机硬件 / 数据采集 / 产业链 / 政策标准 / 其他。
        since_days: 时间窗口,默认 7 天。
        vendors: 厂商过滤。例 ["Figure", "Tesla"]。空表示不过滤。
        keywords: 标题/事实关键词。空表示不过滤。

    返回: Markdown 摘要,按厂商分组。
    """
    rows = bitable.query_records(cfg.feishu_tbl_insights)
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    out: list[dict] = []
    for r in rows:
        f = r.get("fields", {})
        if not f:
            continue
        if track and f.get("track") != track:
            continue
        if vendors and f.get("vendor") not in vendors:
            continue
        if keywords:
            blob = (f.get("headline","") + " " + f.get("key_facts","")).lower()
            if not any(k.lower() in blob for k in keywords):
                continue
        out.append(f)
    if not out:
        return "未找到匹配的洞察。"
    # 按厂商分组渲染
    by_vendor: dict[str, list[dict]] = {}
    for x in out:
        by_vendor.setdefault(x.get("vendor","未知"), []).append(x)
    md = [f"# 洞察查询结果 (共 {len(out)} 条, 近 {since_days} 天)\n"]
    for vendor, items in by_vendor.items():
        md.append(f"## {vendor}")
        for i in items:
            md.append(f"- **{i.get('headline','')}** [{i.get('track','')}]")
            kf = i.get("key_facts", "")
            if kf:
                md.append(f"  {kf}")
        md.append("")
    return "\n".join(md)

@mcp.tool()
def search_sources(keyword: str, since_days: int = 30) -> str:
    """全文搜索原始来源 (tbl_sources)。

    何时调用: 用户问"最近有谁提到过 xxx 技术"、"找一下含 xxx 关键词的所有来源"。
    何时不调用: 关心结构化洞察时用 query_insights 更精准。

    参数:
        keyword: 必填,关键词。
        since_days: 默认 30 天。
    """
    rows = bitable.query_records(cfg.feishu_tbl_sources)
    kw = keyword.lower()
    matches = []
    for r in rows:
        f = r.get("fields", {})
        if not f:
            continue
        if kw in (f.get("title","") + f.get("raw_summary","")).lower():
            matches.append(f)
    if not matches:
        return f"未找到含 '{keyword}' 的来源。"
    md = [f"# 搜索结果: '{keyword}' (共 {len(matches)} 条)\n"]
    for m in matches[:30]:
        md.append(f"- [{m.get('source','')}] {m.get('title','')}")
        md.append(f"  {m.get('url','')}")
    return "\n".join(md)

if __name__ == "__main__":
    mcp.run()
