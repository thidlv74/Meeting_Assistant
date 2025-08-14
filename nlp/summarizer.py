# ------------------------------
# file: meeting_assistant/nlp/summarizer.py
# ------------------------------
from .gpt_client import GPTClient

class Summarizer:
    def __init__(self, client: GPTClient | None = None):
        self.client = client or GPTClient()

    def summarize(self, transcript: str) -> str:
        # TODO: real prompt
        return "(summary placeholder)"