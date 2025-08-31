# ------------------------------
# file: meeting_assistant/nlp/extractor.py
# ------------------------------
from .gpt_client import GPTClient
from core.logger import logger
import json

_EXTRACT_INSTRUCTIONS = """
Bạn là trợ lý trích xuất thông tin từ transcript họp (tiếng Việt). 
Hãy trả về JSON đúng schema sau, không thêm trường khác:

{
  "goal": ["mục tiêu 1", "mục tiêu 2"],
  "agenda": ["mục 1", "mục 2"],
  "attendance": ["Tên (vai trò)", "Tên (vai trò)"],
  "decisions": ["quyết định 1", "quyết định 2"],
  "action_items": [
    {"item":"việc cần làm", "assignee":"ai", "due":"YYYY-MM-DD hoặc rỗng", "done": false}
  ]
}

Ghi “[]” nếu không có thông tin. Giữ ngắn gọn, rõ ràng, đúng nội dung.
Transcript:
"""

class Extractor:
    def __init__(self, client: GPTClient | None = None):
        self.client = client or GPTClient()
        logger.debug("Extractor init")

    def extract_fields(self, transcript: str) -> dict:
        logger.info("Extractor.extract_fields len=%d", len(transcript or ""))
        if not transcript:
            return {"goal":[], "agenda":[], "attendance":[], "decisions":[], "action_items":[]}
        msgs = [
            {"role":"system","content":"Bạn là hệ thống trích xuất dữ liệu họp chính xác và súc tích."},
            {"role":"user","content": _EXTRACT_INSTRUCTIONS + transcript},
        ]
        raw = self.client.chat_json(msgs, temperature=0.0, max_tokens=1400)
        try:
            data = json.loads(raw)
        except Exception:
            logger.warning("Extractor JSON parse failed, returning empty. Raw: %s", raw[:2000])
            data = {}
        # Chuẩn hóa keys
        return {
            "goal": data.get("goal", []) or [],
            "agenda": data.get("agenda", []) or [],
            "attendance": data.get("attendance", []) or [],
            "decisions": data.get("decisions", []) or [],
            "action_items": data.get("action_items", []) or [],
        }
