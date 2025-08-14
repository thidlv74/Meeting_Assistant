# ------------------------------
# file: meeting_assistant/nlp/extractor.py
# ------------------------------
from .gpt_client import GPTClient

class Extractor:
    def __init__(self, client: GPTClient | None = None):
        self.client = client or GPTClient()

    def extract_fields(self, transcript: str) -> dict:
        # TODO: real prompt
        return {
            "goal": [],
            "agenda": [],
            "attendance": [],
            "decisions": [],
            "action_items": [],
        }