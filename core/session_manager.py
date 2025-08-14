# -----------------------------------------------
# file: meeting_assistant/core/session_manager.py
# -----------------------------------------------
from dataclasses import dataclass, field
from typing import Optional
import uuid
import os
from datetime import datetime
from core.config import CONFIG
from core.logger import logger

@dataclass
class Session:
    uuid: str
    title: str = ""
    main_topic: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "idle"  # idle|recording|paused|stopped|processing|completed
    audio_path: Optional[str] = None

class SessionManager:
    def __init__(self):
        self.current: Optional[Session] = None
        os.makedirs(CONFIG.base_dir, exist_ok=True)

    def create(self, title: str = "", topic: str = "") -> Session:
        sid = str(uuid.uuid4())
        folder = os.path.join(CONFIG.base_dir, sid)
        os.makedirs(folder, exist_ok=True)
        self.current = Session(uuid=sid, title=title, main_topic=topic, status="idle",
                               audio_path=os.path.join(folder, "raw.wav"))
        logger.info(f"Created session {sid}")
        return self.current

    def start(self):
        if not self.current:
            self.create()
        self.current.start_time = datetime.now()
        self.current.status = "recording"
        logger.info("Session started")

    def pause(self):
        if self.current:
            self.current.status = "paused"
            logger.info("Session paused")

    def resume(self):
        if self.current:
            self.current.status = "recording"
            logger.info("Session resumed")

    def stop(self):
        if self.current:
            self.current.end_time = datetime.now()
            self.current.status = "stopped"
            logger.info("Session stopped")

SESSION_MANAGER = SessionManager()
