"""Multi-provider LLM 客户端。OpenAI 兼容协议,通过 base_url 切换 provider。
重试 3 次后熔断 (CLAUDE.md "自动重试必须带熔断器")。"""
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import Config

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, cfg: Config):
        self._cfg = cfg
        self._client = OpenAI(api_key=cfg.llm_api_key, base_url=cfg.llm_base_url)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def chat(self, *, system: str, user: str, max_tokens: int = 800, temperature: float = 0.3) -> str:
        """system 含规则、user 含外部内容 (防注入,见 CLAUDE.md "外部内容隔离")。"""
        resp = self._client.chat.completions.create(
            model=self._cfg.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
