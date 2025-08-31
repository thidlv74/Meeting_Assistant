# ------------------------------
# file: meeting_assistant/db/mysql.py
# ------------------------------
from core.config import CONFIG
import pymysql
from core.logger import logger

_conn = None

def get_conn():
    global _conn
    if _conn is None or not getattr(_conn, "open", False):
        logger.info("Opening MySQL connection to %s/%s", CONFIG.mysql_host, CONFIG.mysql_db)
        _conn = pymysql.connect(
            host=CONFIG.mysql_host,
            user=CONFIG.mysql_user,
            password=CONFIG.mysql_password,
            database=CONFIG.mysql_db,
            charset="utf8mb4",
            autocommit=True,
        )
    return _conn

def reset_connection():
    """
    Đóng kết nối hiện tại (nếu có). Lần gọi get_conn() sau sẽ mở lại theo CONFIG mới.
    """
    global _conn
    try:
        if _conn is not None:
            logger.info("Resetting MySQL connection")
            _conn.close()
    except Exception as e:
        logger.warning("Error closing existing MySQL connection: %s", e)
    finally:
        _conn = None
