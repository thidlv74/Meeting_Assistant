# ------------------------------
# file: meeting_assistant/db/dao.py
# ------------------------------
from __future__ import annotations

from .mysql import get_conn
from core.logger import logger
import json
from typing import Iterable, Optional


# ------------------------------
# Sessions
# ------------------------------
def upsert_session(
    uuid: str,
    title: str,
    main_topic: str,
    start_time: str,
    end_time: str,
    duration_min: int,
    status: str,
    audio_path: str,
) -> None:
    """
    Tạo mới hoặc cập nhật phiên họp theo uuid (ON DUPLICATE KEY UPDATE).
    """
    sql = (
        "INSERT INTO sessions (uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE "
        "title=VALUES(title), main_topic=VALUES(main_topic), "
        "start_time=VALUES(start_time), end_time=VALUES(end_time), "
        "duration_min=VALUES(duration_min), status=VALUES(status), audio_path=VALUES(audio_path)"
    )
    with get_conn().cursor() as cur:
        cur.execute(sql, (uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path))
    logger.info("upsert_session ok uuid=%s duration_min=%s", uuid, duration_min)


def update_session_title_topic(uuid: str, title: Optional[str] = None, main_topic: Optional[str] = None) -> int:
    """
    Cập nhật nhanh Title / Main Topic.
    Trả về số dòng ảnh hưởng.
    """
    sets = []
    params: list = []
    if title is not None:
        sets.append("title=%s")
        params.append(title)
    if main_topic is not None:
        sets.append("main_topic=%s")
        params.append(main_topic)
    if not sets:
        return 0
    params.append(uuid)
    sql = f"UPDATE sessions SET {', '.join(sets)} WHERE uuid=%s"
    with get_conn().cursor() as cur:
        rows = cur.execute(sql, params)
    logger.info("update_session_title_topic uuid=%s rows=%s", uuid, rows)
    return rows


def delete_session(uuid: str) -> int:
    """
    Xoá một session (transcripts sẽ bị xoá theo FK ON DELETE CASCADE).
    Trả về số dòng ảnh hưởng.
    """
    with get_conn().cursor() as cur:
        rows = cur.execute("DELETE FROM sessions WHERE uuid=%s", (uuid,))
    logger.info("delete_session uuid=%s rows=%s", uuid, rows)
    return rows


def list_sessions(
    limit: int = 200,
    search: Optional[str] = None,
    order: str = "DESC",
) -> list[tuple]:
    """
    Lấy danh sách sessions để hiển thị.
    Trả về list các tuple: (uuid, title, start_time, duration_min, status)

    - `search`: nếu có, lọc theo LIKE trên title (client-side filter cũng ok,
      nhưng thêm lọc SQL giúp giảm dữ liệu trả về).
    - `order`: 'ASC' | 'DESC' (theo start_time).
    """
    order = "ASC" if str(order).upper() == "ASC" else "DESC"

    if search:
        sql = (
            "SELECT uuid, title, start_time, duration_min, status "
            "FROM sessions "
            "WHERE title LIKE %s "
            f"ORDER BY start_time {order} "
            "LIMIT %s"
        )
        params = (f"%{search}%", limit)
    else:
        sql = (
            "SELECT uuid, title, start_time, duration_min, status "
            "FROM sessions "
            f"ORDER BY start_time {order} "
            "LIMIT %s"
        )
        params = (limit,)

    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    # pymysql mặc định trả về tuple; giữ nguyên để tương thích UI
    logger.debug("list_sessions rows=%s", len(rows or []))
    return rows or []


def get_session(uuid: str) -> Optional[tuple]:
    """
    Lấy chi tiết một session (đủ trường cho trang chi tiết nếu cần).
    Trả về tuple: (uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path)
    """
    sql = (
        "SELECT uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path "
        "FROM sessions WHERE uuid=%s"
    )
    with get_conn().cursor() as cur:
        cur.execute(sql, (uuid,))
        row = cur.fetchone()
    return row


# ------------------------------
# Transcripts
# ------------------------------
def insert_transcript(session_uuid: str, full_text: str, summary: str | None, extracted: dict | None) -> None:
    """
    Thêm transcript mới cho một session (mỗi session có thể có nhiều bản nếu tái sinh/tái phân tích).
    Các trường list/dict sẽ được lưu ở dạng JSON.
    """
    data = extracted or {}
    sql = (
        "INSERT INTO transcripts (session_uuid, full_text, summary, goal, agenda, attendance, decisions, action_items) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    with get_conn().cursor() as cur:
        cur.execute(
            sql,
            (
                session_uuid,
                full_text,
                summary or "",
                json.dumps(data.get("goal", []), ensure_ascii=False),
                json.dumps(data.get("agenda", []), ensure_ascii=False),
                json.dumps(data.get("attendance", []), ensure_ascii=False),
                json.dumps(data.get("decisions", []), ensure_ascii=False),
                json.dumps(data.get("action_items", []), ensure_ascii=False),
            ),
        )
    logger.info("insert_transcript ok session_uuid=%s len(full_text)=%s", session_uuid, len(full_text or ""))


def list_transcripts(session_uuid: str, limit: int = 50) -> list[tuple]:
    """
    Trả về danh sách transcript theo session_uuid (mới nhất trước).
    Mỗi dòng: (id, created_at, summary) — đủ cho preview list;
    cần chi tiết dùng get_transcript().
    """
    sql = (
        "SELECT id, created_at, summary "
        "FROM transcripts WHERE session_uuid=%s "
        "ORDER BY created_at DESC LIMIT %s"
    )
    with get_conn().cursor() as cur:
        cur.execute(sql, (session_uuid, limit))
        return cur.fetchall() or []


def get_transcript(transcript_id: int) -> Optional[tuple]:
    """
    Lấy đầy đủ 1 transcript:
    (id, session_uuid, full_text, summary, goal, agenda, attendance, decisions, action_items, created_at)
    """
    sql = (
        "SELECT id, session_uuid, full_text, summary, goal, agenda, attendance, decisions, action_items, created_at "
        "FROM transcripts WHERE id=%s"
    )
    with get_conn().cursor() as cur:
        cur.execute(sql, (transcript_id,))
        return cur.fetchone()


def delete_transcripts(session_uuid: str) -> int:
    """
    Xoá tất cả transcripts của một session (không xoá session).
    """
    with get_conn().cursor() as cur:
        rows = cur.execute("DELETE FROM transcripts WHERE session_uuid=%s", (session_uuid,))
    logger.info("delete_transcripts session_uuid=%s rows=%s", session_uuid, rows)
    return rows

def update_transcript(
    transcript_id: int,
    summary: str | None,
    extracted: dict | None,
    full_text: str | None = None,
) -> int:
    """
    Cập nhật 1 transcript theo ID. Trả về số dòng ảnh hưởng.
    Chỉ cập nhật các trường được truyền vào (không None).
    """
    sets = []
    params = []
    if full_text is not None:
        sets.append("full_text=%s")
        params.append(full_text)
    if summary is not None:
        sets.append("summary=%s")
        params.append(summary)
    if extracted is not None:
        import json as _json
        sets.append("goal=%s")
        params.append(_json.dumps(extracted.get("goal", []), ensure_ascii=False))
        sets.append("agenda=%s")
        params.append(_json.dumps(extracted.get("agenda", []), ensure_ascii=False))
        sets.append("attendance=%s")
        params.append(_json.dumps(extracted.get("attendance", []), ensure_ascii=False))
        sets.append("decisions=%s")
        params.append(_json.dumps(extracted.get("decisions", []), ensure_ascii=False))
        sets.append("action_items=%s")
        params.append(_json.dumps(extracted.get("action_items", []), ensure_ascii=False))

    if not sets:
        return 0

    sql = f"UPDATE transcripts SET {', '.join(sets)} WHERE id=%s"
    params.append(transcript_id)
    with get_conn().cursor() as cur:
        rows = cur.execute(sql, params)
    return rows


def update_latest_transcript(
    session_uuid: str,
    summary: str | None,
    extracted: dict | None,
    full_text: str | None = None,
) -> int:
    """
    Cập nhật transcript mới nhất của 1 session.
    Nếu không có transcript nào -> trả 0 để caller biết mà insert mới.
    """
    # lấy id transcript mới nhất
    sql = "SELECT id FROM transcripts WHERE session_uuid=%s ORDER BY created_at DESC LIMIT 1"
    with get_conn().cursor() as cur:
        cur.execute(sql, (session_uuid,))
        row = cur.fetchone()
    if not row:
        return 0
    tid = row[0]
    return update_transcript(tid, summary=summary, extracted=extracted, full_text=full_text)
