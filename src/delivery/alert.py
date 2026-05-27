import httpx

def push_alert(webhook: str, *, headline: str, track: str, vendor: str,
               url: str, reason: str) -> None:
    text = (
        f"🚨 人形机器人行业突发\n"
        f"赛道: {track} | 厂商: {vendor}\n"
        f"事件: {headline}\n"
        f"判定理由: {reason}\n"
        f"原文: {url}"
    )
    httpx.post(webhook, json={"msg_type": "text", "content": {"text": text}}, timeout=15)
