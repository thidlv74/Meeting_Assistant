# ------------------------------------
# file: meeting_assistant/ui/tabs_dashboard.py
# ------------------------------------
from __future__ import annotations
import json
from datetime import datetime
from tkinter import ttk, messagebox

from core.logger import logger
from db.mysql import get_conn
from ui.styles import PANEL_BG, FG


def _fmt_duration(total_min: int) -> str:
    try:
        m = int(total_min or 0)
    except Exception:
        return "0m"
    if m < 60:
        return f"{m}m"
    h, mm = divmod(m, 60)
    return f"{h}h {mm}m" if mm else f"{h}h"


class DashboardTab(ttk.Frame):
    """
    Dashboard mới:
      - 4 cards thống kê: Tổng cuộc họp, Tổng thời lượng, Action Items, Completion Rate
      - Bảng: Recent Meetings
      - Bảng: Action Items (tổng hợp từ transcripts gần nhất)
      - Nút Refresh để tải lại từ DB
    """
    def __init__(self, master):
        logger.debug("DashboardTab.__init__")
        super().__init__(master, padding=16)
        self._build()
        self.refresh()

    # ------------- UI -------------
    def _build(self):
        logger.debug("DashboardTab._build UI")
        # Thanh công cụ
        bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
        bar.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        ttk.Label(bar, text="📊 Overview", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side="right")

        # Vùng cards (2x2)
        cards_grid = ttk.Frame(self)
        cards_grid.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        for c in range(2):
            cards_grid.grid_columnconfigure(c, weight=1)

        self.card_total_meetings = self._create_card(cards_grid, 0, 0, "Tổng cuộc họp")
        self.card_total_duration = self._create_card(cards_grid, 0, 1, "Tổng thời lượng")
        self.card_action_items   = self._create_card(cards_grid, 1, 0, "Action Items")
        self.card_completion     = self._create_card(cards_grid, 1, 1, "Completion Rate")

        # Khu vực dưới: Recent Meetings (trái) + Action Items (phải)
        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        self.grid_rowconfigure(2, weight=1)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)

        # Recent Meetings
        left = ttk.Frame(bottom, style="Panel.TFrame", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ttk.Label(left, text="🗓 Recent Meetings", style="CardTitle.TLabel").pack(anchor="w")
        self.tbl_recent = ttk.Treeview(left, columns=("title", "start", "duration"), show="headings", height=10)
        self.tbl_recent.heading("title", text="Title")
        self.tbl_recent.heading("start", text="Start Time")
        self.tbl_recent.heading("duration", text="Duration")
        self.tbl_recent.column("title", width=380, anchor="w")
        self.tbl_recent.column("start", width=160, anchor="w")
        self.tbl_recent.column("duration", width=100, anchor="w")
        self.tbl_recent.pack(fill="both", expand=True, pady=(8, 0))

        # Action Items (aggregate)
        right = ttk.Frame(bottom, style="Panel.TFrame", padding=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ttk.Label(right, text="✅ Action Items (latest)", style="CardTitle.TLabel").pack(anchor="w")
        self.tbl_ai = ttk.Treeview(right, columns=("item", "assignee", "due", "done"), show="headings", height=10)
        self.tbl_ai.heading("item", text="Action Item")
        self.tbl_ai.heading("assignee", text="Assigned To")
        self.tbl_ai.heading("due", text="Due Date")
        self.tbl_ai.heading("done", text="Done")
        self.tbl_ai.column("item", width=320, anchor="w")
        self.tbl_ai.column("assignee", width=140, anchor="w")
        self.tbl_ai.column("due", width=120, anchor="w")
        self.tbl_ai.column("done", width=60, anchor="center")
        self.tbl_ai.pack(fill="both", expand=True, pady=(8, 0))

        # Gợi ý mở Sessions để xem chi tiết
        hint = ttk.Label(right, text="📌 Mở tab Sessions để chỉnh sửa/chi tiết từng meeting.", style="Muted.TLabel")
        hint.pack(anchor="w", pady=(8, 0))

        logger.debug("DashboardTab UI built")

    def _create_card(self, parent: ttk.Frame, row: int, col: int, title: str):
        card = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        parent.grid_rowconfigure(row, weight=1)
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        num = ttk.Label(card, text="—", style="CardNumber.TLabel")
        num.pack(anchor="w")
        return num

    # ------------- Data load -------------
    def refresh(self):
        logger.info("DashboardTab.refresh -> query DB")
        try:
            stats = self._fetch_stats()
            recent = self._fetch_recent_sessions(limit=12)
            ai_list = self._fetch_latest_action_items(limit=20)
        except Exception as e:
            logger.exception("DashboardTab.refresh error: %s", e)
            messagebox.showerror("DB Error", str(e))
            return

        # Update cards
        self.card_total_meetings.configure(text=str(stats["total_meetings"]))
        self.card_total_duration.configure(text=_fmt_duration(stats["total_duration_min"]))
        self.card_action_items.configure(text=str(stats["total_action_items"]))
        self.card_completion.configure(text=f'{stats["completion_rate"]:.0f}%')

        # Update Recent Meetings table
        self._render_recent(recent)

        # Update AI table
        self._render_ai(ai_list)

    # ---- Queries ----
    def _fetch_stats(self) -> dict:
        """
        - total_meetings: COUNT(*) from sessions
        - total_duration_min: SUM(duration_min)
        - action items & completion rate: đọc transcripts, parse JSON tại Python
        """
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*), COALESCE(SUM(duration_min),0) FROM sessions")
            row = cur.fetchone() or (0, 0)
            total_meetings, total_duration_min = int(row[0] or 0), int(row[1] or 0)

            # Lấy tất cả action_items JSON (có thể giới hạn nếu data lớn)
            cur.execute("SELECT action_items FROM transcripts ORDER BY created_at DESC LIMIT 500")
            action_rows = cur.fetchall() or []

        total_ai = 0
        done_ai = 0
        for (blob,) in action_rows:
            if not blob:
                continue
            try:
                items = json.loads(blob)
                for it in items or []:
                    total_ai += 1
                    if str(it.get("done", "")).lower() in ("1", "true", "yes", "y"):
                        done_ai += 1
            except Exception:
                continue

        completion_rate = (done_ai / total_ai * 100) if total_ai else 0.0
        return {
            "total_meetings": total_meetings,
            "total_duration_min": total_duration_min,
            "total_action_items": total_ai,
            "completion_rate": completion_rate,
        }

    def _fetch_recent_sessions(self, limit=12) -> list[tuple]:
        """
        Trả về list tuples: (title, start_time_txt, duration_txt)
        MySQL không hỗ trợ NULLS LAST -> dùng (start_time IS NULL) để đẩy NULL xuống cuối.
        """
        conn = get_conn()
        with conn.cursor() as cur:
            # dùng ORDER BY (start_time IS NULL) ASC để NULL xuống sau
            sql = (
                "SELECT title, start_time, duration_min "
                "FROM sessions "
                "ORDER BY (start_time IS NULL) ASC, start_time DESC, id DESC "
                "LIMIT %s"
            )
            cur.execute(sql, (int(limit),))
            rows = cur.fetchall() or []

        out = []
        for title, start, dur in rows:
            title = title or "(untitled)"
            # _fmt_dt là helper trong class; nếu bạn dùng hàm ngoài thì gọi đúng tên tương ứng
            start_txt = self._fmt_dt(start)
            out.append((title, start_txt, _fmt_duration(int(dur or 0))))
        return out

    def _fetch_latest_action_items(self, limit=20) -> list[dict]:
        """
        Gom các action_items từ transcripts mới nhất (giới hạn).
        Mỗi item: {"item": str, "assignee": str, "due": str, "done": bool}
        """
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT action_items FROM transcripts "
                "ORDER BY created_at DESC LIMIT 100"
            )
            rows = cur.fetchall() or []

        acc: list[dict] = []
        for (blob,) in rows:
            if not blob:
                continue
            try:
                items = json.loads(blob) or []
                for it in items:
                    acc.append({
                        "item": it.get("item", ""),
                        "assignee": it.get("assignee", ""),
                        "due": it.get("due", ""),
                        "done": bool(it.get("done", False)),
                    })
            except Exception:
                continue
            if len(acc) >= limit:
                break
        return acc[:limit]

    # ---- Render helpers ----
    def _render_recent(self, rows: list[tuple]):
        # rows: (title, start, duration)
        for iid in self.tbl_recent.get_children():
            self.tbl_recent.delete(iid)
        for title, start, dur in rows:
            self.tbl_recent.insert("", "end", values=(title, start, dur))

    def _render_ai(self, items: list[dict]):
        for iid in self.tbl_ai.get_children():
            self.tbl_ai.delete(iid)
        for it in items or []:
            self.tbl_ai.insert(
                "", "end",
                values=(it["item"], it["assignee"], it["due"], "✔" if it["done"] else "")
            )

    # ---- utils ----
    @staticmethod
    def _fmt_dt(dt_val):
        if not dt_val:
            return ""
        if isinstance(dt_val, datetime):
            return dt_val.strftime("%Y-%m-%d %H:%M")
        # pymysql có thể trả string; cắt gọn
        return str(dt_val)[:16]
