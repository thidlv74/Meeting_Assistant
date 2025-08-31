# ------------------------------
# file: meeting_assistant/ui/tabs_sessions.py
# ------------------------------
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import json

from core.logger import logger
from db.dao import (
    list_sessions,
    get_session,
    list_transcripts,
    get_transcript,
    update_session_title_topic,
    delete_session,
    insert_transcript,
)
from report.docx_export import export_meeting_report
from ui.styles import PRIMARY_BG, PANEL_BG, FG, BORDER


def _fmt_dt(dt_val):
    if not dt_val:
        return ""
    if isinstance(dt_val, datetime):
        return dt_val.strftime("%Y-%m-%d %H:%M")
    return str(dt_val)[:16]


def _fmt_dur(minutes):
    try:
        m = int(minutes or 0)
    except Exception:
        return ""
    if m < 60:
        return f"{m}m"
    h, mm = divmod(m, 60)
    return f"{h}h" if mm == 0 else f"{h}h {mm}m"


def _lines_to_list(s: str) -> list[str]:
    return [ln.strip() for ln in (s or "").splitlines() if ln.strip()]


def _list_to_lines(arr: list[str]) -> str:
    return "\n".join(arr or [])


def _ai_rows_to_list(tree: ttk.Treeview) -> list[dict]:
    out = []
    for iid in tree.get_children():
        item, assign, due, done = tree.item(iid, "values")
        out.append({
            "item": item or "",
            "assignee": assign or "",
            "due": due or "",
            "done": True if str(done).strip().lower() in ("1","true","yes","y","✔","x") else False
        })
    return out


class SessionDetailWindow(tk.Toplevel):
    """Cửa sổ chi tiết: nền đen, box có viền, Summary dài hơn."""
    def __init__(self, master, session_uuid: str):
        super().__init__(master)
        self.title("Session Detail")
        self.geometry("1000x890")
        self._uuid = session_uuid
        self._current_transcript_id = None

        # NỀN ĐEN cho toplevel
        self.configure(bg=PRIMARY_BG)

        # Style riêng cho cửa sổ chi tiết
        st = ttk.Style(self)
        st.configure("Detail.TFrame", background=PRIMARY_BG)
        st.configure("Box.TLabelframe",
                    background=PRIMARY_BG,
                    bordercolor=BORDER,
                    borderwidth=2,
                    relief="solid")
        st.configure("Box.TLabelframe.Label",
                    background=PRIMARY_BG,
                    foreground=FG)

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)

        # Header meta (Frame trên nền đen)
        meta = ttk.Frame(self, style="Detail.TFrame", padding=12)
        meta.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
        for c in range(4): meta.columnconfigure(c, weight=1)

        ttk.Label(meta, text="Title").grid(row=0, column=0, sticky="w")
        self.e_title = ttk.Entry(meta)
        self.e_title.grid(row=0, column=1, sticky="ew", padx=(6,12))

        ttk.Label(meta, text="Main Topic").grid(row=0, column=2, sticky="w")
        self.e_topic = ttk.Entry(meta)
        self.e_topic.grid(row=0, column=3, sticky="ew", padx=(6,0))

        ttk.Label(meta, text="Start").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.l_start = ttk.Label(meta, text="")
        self.l_start.grid(row=1, column=1, sticky="w", padx=(6,12), pady=(8,0))

        ttk.Label(meta, text="End").grid(row=1, column=2, sticky="w", pady=(8,0))
        self.l_end = ttk.Label(meta, text="")
        self.l_end.grid(row=1, column=3, sticky="w", padx=(6,0), pady=(8,0))

        ttk.Label(meta, text="Duration").grid(row=2, column=0, sticky="w", pady=(6,0))
        self.l_dur = ttk.Label(meta, text="")
        self.l_dur.grid(row=2, column=1, sticky="w", padx=(6,12), pady=(6,0))

        ttk.Label(meta, text="Audio").grid(row=2, column=2, sticky="w", pady=(6,0))
        self.l_audio = ttk.Label(meta, text="")
        self.l_audio.grid(row=2, column=3, sticky="w", padx=(6,0), pady=(6,0))

        # SUMMARY — tăng chiều cao và viền box
        sum_card = ttk.LabelFrame(self, text="Summary", style="Box.TLabelframe", padding=8)
        sum_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10,0))
        self.t_summary = tk.Text(sum_card, height=12, wrap="word", bd=0)
        self.t_summary.configure(bg=PANEL_BG, fg=FG, insertbackground=FG)
        self.t_summary.pack(fill="both", expand=True, padx=6, pady=6)

        # 4 boxes có viền
        grid4 = ttk.Frame(self, style="Detail.TFrame")
        grid4.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10,0))
        for c in range(4): grid4.columnconfigure(c, weight=1)

        def mk_box(parent, title):
            box = ttk.LabelFrame(parent, text=title, style="Box.TLabelframe", padding=6)
            txt = tk.Text(box, height=8, wrap="word", bd=0)
            txt.configure(bg=PANEL_BG, fg=FG, insertbackground=FG)
            txt.pack(fill="both", expand=True, padx=6, pady=6)
            return box, txt

        self.box_goal, self.t_goal = mk_box(grid4, "Goal (mỗi dòng 1 mục)")
        self.box_agenda, self.t_agenda = mk_box(grid4, "Agenda (mỗi dòng 1 mục)")
        self.box_att, self.t_att = mk_box(grid4, "Attendance (Tên (vai trò) mỗi dòng)")
        self.box_dec, self.t_dec = mk_box(grid4, "Decisions (mỗi dòng 1 mục)")

        self.box_goal.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        self.box_agenda.grid(row=0, column=1, sticky="nsew", padx=6)
        self.box_att.grid(row=0, column=2, sticky="nsew", padx=6)
        self.box_dec.grid(row=0, column=3, sticky="nsew", padx=(6,0))

        # Action Items (box có viền)
        ai_card = ttk.LabelFrame(self, text="Action Items", style="Box.TLabelframe", padding=6)
        ai_card.grid(row=3, column=0, sticky="nsew", padx=10, pady=(10,0))
        ai_card.columnconfigure(0, weight=1)

        cols = ("item","assignee","due","done")
        self.ai_tree = ttk.Treeview(ai_card, columns=cols, show="headings", height=8)
        for c,w in zip(cols,(380,180,140,80)):
            self.ai_tree.heading(c, text=c.title())
            self.ai_tree.column(c, width=w, anchor="w")
        self.ai_tree.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        addbar = ttk.Frame(ai_card, style="Detail.TFrame")
        addbar.grid(row=1, column=0, sticky="ew", padx=4, pady=(0,4))
        ttk.Label(addbar, text="Item").grid(row=0, column=0, sticky="w")
        self.e_ai_item = ttk.Entry(addbar, width=40); self.e_ai_item.grid(row=0, column=1, padx=6)
        ttk.Label(addbar, text="Assignee").grid(row=0, column=2, sticky="w")
        self.e_ai_assign = ttk.Entry(addbar, width=18); self.e_ai_assign.grid(row=0, column=3, padx=6)
        ttk.Label(addbar, text="Due").grid(row=0, column=4, sticky="w")
        self.e_ai_due = ttk.Entry(addbar, width=12); self.e_ai_due.grid(row=0, column=5, padx=6)
        ttk.Label(addbar, text="Done").grid(row=0, column=6, sticky="w")
        self.e_ai_done = ttk.Combobox(addbar, values=["", "True", "False"], width=8, state="readonly")
        self.e_ai_done.grid(row=0, column=7, padx=6)
        ttk.Button(addbar, text="Add", command=self._ai_add).grid(row=0, column=8, padx=(6,0))
        ttk.Button(addbar, text="Remove Selected", command=self._ai_del).grid(row=0, column=9, padx=(8,0))

        # Action buttons
        actions = ttk.Frame(self, style="Detail.TFrame")
        actions.grid(row=4, column=0, sticky="e", padx=10, pady=(12,0))
        ttk.Button(actions, text="💾 Save Changes", command=self._save_changes).grid(row=0, column=0, padx=(0,8))
        ttk.Button(actions, text="🗑 Delete Session", command=self._delete_session).grid(row=0, column=1, padx=(0,8))
        ttk.Button(actions, text="📄 Export DOCX", command=self._export_docx).grid(row=0, column=2)

        # filler
        ttk.Frame(self, style="Detail.TFrame").grid(row=5, column=0, pady=6)
        self._load()

    # ---- load + helpers ----
    def _load(self):
        try:
            row = get_session(self._uuid)
            if not row:
                messagebox.showwarning("Not found", "Session không tồn tại."); self.destroy(); return
            _uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path = row
            self.e_title.delete(0,"end"); self.e_title.insert(0, title or "")
            self.e_topic.delete(0,"end"); self.e_topic.insert(0, main_topic or "")
            self.l_start.configure(text=_fmt_dt(start_time))
            self.l_end.configure(text=_fmt_dt(end_time))
            self.l_dur.configure(text=_fmt_dur(duration_min))
            self.l_audio.configure(text=os.path.basename(audio_path or "") or "")

            items = list_transcripts(self._uuid, limit=1)
            self._current_transcript_id = items[0][0] if items else None

            full_text = ""; summary = ""; goal=[]; agenda=[]; attendance=[]; decisions=[]; action_items=[]
            if self._current_transcript_id:
                t = get_transcript(self._current_transcript_id)
                if t:
                    full_text = t[2] or ""
                    summary = t[3] or ""
                    goal = json.loads(t[4] or "[]")
                    agenda = json.loads(t[5] or "[]")
                    attendance = json.loads(t[6] or "[]")
                    decisions = json.loads(t[7] or "[]")
                    action_items = json.loads(t[8] or "[]")

            self.t_summary.delete("1.0","end"); self.t_summary.insert("end", summary or "")
            for w, data in (
                (self.t_goal, goal), (self.t_agenda, agenda), (self.t_att, attendance), (self.t_dec, decisions)
            ):
                w.delete("1.0","end"); w.insert("end", _list_to_lines(data))

            for iid in self.ai_tree.get_children(): self.ai_tree.delete(iid)
            for it in (action_items or []):
                self.ai_tree.insert("", "end", values=(it.get("item",""), it.get("assignee",""), it.get("due",""), "✔" if it.get("done") else ""))

        except Exception as e:
            logger.exception("SessionDetailWindow._load error: %s", e)
            messagebox.showerror("Error", str(e))
            self.destroy()

    def _ai_add(self):
        item = self.e_ai_item.get().strip()
        if not item: return
        assign = self.e_ai_assign.get().strip()
        due = self.e_ai_due.get().strip()
        done = (self.e_ai_done.get() or "").strip()
        self.ai_tree.insert("", "end", values=(item, assign, due, done))
        self.e_ai_item.delete(0,"end"); self.e_ai_assign.delete(0,"end"); self.e_ai_due.delete(0,"end"); self.e_ai_done.set("")

    def _ai_del(self):
        for iid in self.ai_tree.selection():
            self.ai_tree.delete(iid)

    def _save_changes(self):
        try:
            title = self.e_title.get().strip()
            topic = self.e_topic.get().strip()
            update_session_title_topic(self._uuid, title=title, main_topic=topic)

            summary = self.t_summary.get("1.0","end").strip()
            goal = _lines_to_list(self.t_goal.get("1.0","end"))
            agenda = _lines_to_list(self.t_agenda.get("1.0","end"))
            attendance = _lines_to_list(self.t_att.get("1.0","end"))
            decisions = _lines_to_list(self.t_dec.get("1.0","end"))
            action_items = _ai_rows_to_list(self.ai_tree)

            extracted = {
                "goal": goal,
                "agenda": agenda,
                "attendance": attendance,
                "decisions": decisions,
                "action_items": action_items,
            }

            # ⚠️ ƯU TIÊN UPDATE transcript mới nhất. Nếu chưa có -> INSERT.
            from db.dao import update_latest_transcript
            rows = update_latest_transcript(
                session_uuid=self._uuid,
                summary=summary,
                extracted=extracted,
                full_text=None  # hoặc truyền full_text nếu bạn muốn cập nhật luôn
            )
            if rows == 0:
                # chưa có transcript nào -> tạo mới
                insert_transcript(self._uuid, full_text="", summary=summary, extracted=extracted)

            messagebox.showinfo("Saved", "Đã lưu thay đổi.")
        except Exception as e:
            logger.exception("Save changes error: %s", e)
            messagebox.showerror("Error", str(e))

    def _delete_session(self):
        if messagebox.askyesno("Confirm", "Xoá phiên họp này? Mọi transcript liên quan sẽ bị xoá."):
            try:
                delete_session(self._uuid)
                messagebox.showinfo("Deleted", "Đã xoá phiên họp.")
                self.destroy()
            except Exception as e:
                logger.exception("Delete session error: %s", e)
                messagebox.showerror("Error", str(e))

    def _export_docx(self):
        try:
            row = get_session(self._uuid)
            if not row:
                messagebox.showwarning("Not found", "Session không tồn tại."); return
            _uuid, title, main_topic, start_time, end_time, duration_min, status, audio_path = row

            summary = self.t_summary.get("1.0","end").strip()
            goal = _lines_to_list(self.t_goal.get("1.0","end"))
            agenda = _lines_to_list(self.t_agenda.get("1.0","end"))
            attendance = _lines_to_list(self.t_att.get("1.0","end"))
            decisions = _lines_to_list(self.t_dec.get("1.0","end"))
            action_items = _ai_rows_to_list(self.ai_tree)

            save_path = filedialog.asksaveasfilename(
                title="Lưu báo cáo DOCX",
                defaultextension=".docx",
                filetypes=[("Word Document","*.docx")],
                initialfile=f"{(title or 'meeting').strip().replace(' ','_')}.docx"
            )
            if not save_path: return

            meta = {
                "title": title or "Meeting Report",
                "datetime": f"{_fmt_dt(start_time)} → {_fmt_dt(end_time)}  ({_fmt_dur(duration_min)})",
            }
            export_meeting_report(save_path, meta, summary, {
                "goal": goal, "agenda": agenda, "attendance": attendance,
                "decisions": decisions, "action_items": action_items
            })
            messagebox.showinfo("Exported", f"Đã xuất báo cáo:\n{save_path}")
        except Exception as e:
            logger.exception("Export DOCX error: %s", e)
            messagebox.showerror("Error", str(e))


class SessionsTab(ttk.Frame):
    """Danh sách phiên họp (list-only). Chọn một hàng sẽ mở cửa sổ chi tiết."""
    def __init__(self, master):
        logger.debug("SessionsTab.__init__")
        super().__init__(master, padding=16)
        self._rows = []  # [(uuid, title, start_time, duration_min, status)]
        self._build()

    def _build(self):
        logger.debug("SessionsTab._build UI")
        # Top bar
        bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
        bar.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(bar, text="🔎 Search:").grid(row=0, column=0, padx=(0,6))
        self.search_var = tk.StringVar()
        e = ttk.Entry(bar, textvariable=self.search_var, width=38)
        e.grid(row=0, column=1)
        self.search_var.trace_add("write", lambda *_: self._apply_filter())

        ttk.Button(bar, text="Refresh", command=self.refresh).grid(row=0, column=2, padx=(12,0))
        ttk.Button(bar, text="Open", command=self._open_selected).grid(row=0, column=3, padx=(8,0))

        # Table only
        table_frame = ttk.Frame(self, style="Panel.TFrame", padding=8)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.cols = ("title","start","duration")
        self.tree = ttk.Treeview(table_frame, columns=self.cols, show="headings", height=18)
        self.tree.heading("title", text="Title")
        self.tree.heading("start", text="Start Time")
        self.tree.heading("duration", text="Duration")
        self.tree.column("title", width=420, anchor="w")
        self.tree.column("start", width=200, anchor="w")
        self.tree.column("duration", width=120, anchor="w")
        self.tree.pack(fill="both", expand=True)

        # double click to open detail
        self.tree.bind("<Double-1>", self._on_double_click)

        self.refresh()
        logger.debug("SessionsTab UI built")

    def refresh(self):
        logger.info("SessionsTab.refresh -> DB")
        try:
            self._rows = list_sessions(limit=300) or []
            self._apply_filter()
        except Exception as e:
            logger.exception("SessionsTab.refresh DB error: %s", e)
            self._rows = []
            self._render_rows([])

    def _apply_filter(self):
        text = (self.search_var.get() or "").strip().lower()
        out = []
        for (uuid, title, start_time, duration_min, _status) in self._rows:
            if text and text not in (title or "").lower():
                continue
            out.append((uuid, title or "", _fmt_dt(start_time), _fmt_dur(duration_min)))
        self._render_rows(out)

    def _render_rows(self, rows):
        # rows: [(uuid, title, start, dur)]
        self.tree.delete(*self.tree.get_children())
        for uuid, title, start, dur in rows:
            self.tree.insert("", "end", iid=uuid, values=(title, start, dur))

    def _on_double_click(self, event):
        sel = self.tree.identify_row(event.y)
        if sel:
            SessionDetailWindow(self, sel)

    def _open_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Hãy chọn một phiên họp."); return
        SessionDetailWindow(self, sel[0])
