# ------------------------------
# file: meeting_assistant/nlp/gpt_client.py
# ------------------------------
from core.config import CONFIG
from core.logger import logger

try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None
    logger.warning("OpenAI SDK not available: %s", e)

class GPTClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or CONFIG.openai_api_key
        self.model = model or CONFIG.gpt_model
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY chưa được cấu hình (.env)")
        if OpenAI is None:
            raise RuntimeError("Chưa cài openai SDK. Chạy: pip install openai")
        self.client = OpenAI(api_key=self.api_key)
        logger.debug("GPTClient init model=%s key_set=%s", self.model, bool(self.api_key))

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        messages: [{"role":"system"|"user"|"assistant", "content":"..."}]
        return: assistant text
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.2),
            max_tokens=kwargs.get("max_tokens", 800),
        )
        return (resp.choices[0].message.content or "").strip()

    def chat_json(self, messages: list[dict], **kwargs) -> str:
        """
        Force JSON output (for extractor). Return raw string (JSON).
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 1200),
            response_format={"type": "json_object"},
        )
        return (resp.choices[0].message.content or "").strip()
