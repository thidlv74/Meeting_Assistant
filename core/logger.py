# --------------------------------------
# file: meeting_assistant/core/logger.py
# --------------------------------------
import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("meeting_assistant")