# ------------------------------
# file: meeting_assistant/nlp/summarizer.py
# ------------------------------
from .gpt_client import GPTClient
from core.logger import logger
import textwrap

_SUMMARY_PROMPT = """Bạn là trợ lý tóm tắt biên bản họp bằng tiếng Việt.
YÊU CẦU: Viết ngắn gọn, rõ ràng, chỉ các ý chính; tránh lặp; giữ đúng ngữ cảnh.
Nếu input dài, tổng hợp thành 5–10 bullet, sau đó chốt 1–2 dòng 'Kết luận'.

Văn bản cần tóm tắt (tiếng Việt):
"""

class Summarizer:
    def __init__(self, client: GPTClient | None = None):
        self.client = client or GPTClient()
        logger.debug("Summarizer init")

    def _summarize_chunk(self, text: str) -> str:
        msgs = [
            {"role":"system","content":"Bạn là chuyên gia tóm tắt cuộc họp tiếng Việt."},
            {"role":"user","content": _SUMMARY_PROMPT + text},
        ]
        return self.client.chat(msgs, temperature=0.2, max_tokens=900)

    def summarize(self, transcript: str) -> str:
        logger.info("Summarizer.summarize len=%d", len(transcript or ""))
        if not transcript:
            return ""
        # Chunk theo ~4k ký tự để an toàn
        chunks = []
        buf = transcript.strip()
        chunk_size = 4000
        for i in range(0, len(buf), chunk_size):
            chunks.append(buf[i:i+chunk_size])

        partials = [self._summarize_chunk(ch) for ch in chunks]
        # Tóm tắt lại lần cuối
        final_input = "\n\n---\n\n".join(partials)
        final = self._summarize_chunk(final_input)
        return final.strip()
