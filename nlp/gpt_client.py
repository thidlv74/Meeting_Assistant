# ------------------------------
# file: meeting_assistant/nlp/gpt_client.py
# ------------------------------
from core.config import CONFIG

class GPTClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or CONFIG.openai_api_key
        self.model = model or CONFIG.gpt_model
        # NOTE: integrate openai sdk when wiring backend

    def chat(self, messages: list[dict], **kwargs) -> str:
        # TODO: call OpenAI (chat.completions) and return text
        return ""