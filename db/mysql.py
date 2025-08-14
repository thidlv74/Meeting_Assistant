# ------------------------------
# file: meeting_assistant/db/mysql.py
# ------------------------------
# Minimal MySQL connector wrapper (pymysql or mysqlclient)
from core.config import CONFIG
import pymysql

_conn = None

def get_conn():
    global _conn
    if _conn is None or not _conn.open:
        _conn = pymysql.connect(
            host=CONFIG.mysql_host,
            user=CONFIG.mysql_user,
            password=CONFIG.mysql_password,
            database=CONFIG.mysql_db,
            charset="utf8mb4",
            autocommit=True,
        )
    return _conn
