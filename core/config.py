# --------------------------------------
# file: meeting_assistant/core/config.py
# --------------------------------------
from dataclasses import dataclass
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

@dataclass
class AppConfig:
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_db: str = os.getenv("MYSQL_DB", "meeting_db")
    base_dir: str = os.getenv("BASE_DIR", "./records")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gpt_model: str = os.getenv("GPT_MODEL", "gpt-4o-mini")
    asr_model: str = os.getenv("ASR_MODEL", "medium")
    autosave_sec: int = int(os.getenv("AUTOSAVE_SEC", "2"))

CONFIG = AppConfig()
