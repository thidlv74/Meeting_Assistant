# ------------------------------
# file: meeting_assistant/db/dao.py
# ------------------------------
from .mysql import get_conn

# Simple DAO examples — expand later

def insert_session(uuid: str, title: str, start_time: str, status: str):
    sql = "INSERT INTO sessions (uuid, title, start_time, status) VALUES (%s,%s,%s,%s)"
    with get_conn().cursor() as cur:
        cur.execute(sql, (uuid, title, start_time, status))


def list_sessions(limit: int = 100):
    sql = "SELECT uuid, title, start_time, duration_min, status FROM sessions ORDER BY start_time DESC LIMIT %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (limit,))
        return cur.fetchall()
