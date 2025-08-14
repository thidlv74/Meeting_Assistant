# ================================
# meeting_assistant — project files
# Paste these into your folder structure as indicated by the file headers.
# ================================

# -------------------------------
# file: meeting_assistant/app.py
# -------------------------------
import tkinter as tk
from tkinter import ttk

from ui.styles import apply_dark_style, PRIMARY_BG
from ui.sidebar import Sidebar
from ui.tabs_start import StartTab
from ui.tabs_sessions import SessionsTab
from ui.tabs_dashboard import DashboardTab
from ui.tabs_reports import ReportsTab
from ui.tabs_settings import SettingsTab


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Meeting Assistant — Dashboard")
        self.geometry("1200x720")
        self.configure(bg=PRIMARY_BG)
        self.minsize(1024, 640)

        apply_dark_style(self)
        self._build_layout()

    def _build_layout(self):
        # Grid: 0 = sidebar (fixed ~240px), 1 = main
        self.grid_columnconfigure(0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_nav=self._on_nav)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Main area — title bar + content container
        self.main = ttk.Frame(self, padding=(12,12))
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # Current tab title
        from ui.styles import heading_style_name
        self.tab_title = ttk.Label(self.main, text="Start New Meeting", style=heading_style_name())
        self.tab_title.grid(row=0, column=0, sticky="w", pady=(0,8))
        ttk.Separator(self.main).grid(row=0, column=0, sticky="ew", pady=(36,8))

        # Content container that will swap frames
        self.content = ttk.Frame(self.main)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Instantiate pages
        self.frames = {
            "start":    StartTab(self.content),
            "sessions": SessionsTab(self.content),
            "dashboard":DashboardTab(self.content),
            "reports":  ReportsTab(self.content),
            "settings": SettingsTab(self.content),
        }
        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        self._show_frame("start")

    def _show_frame(self, key: str):
        titles = {
            "start": "Start New Meeting",
            "sessions": "Sessions",
            "dashboard": "Dashboard",
            "reports": "Reports",
            "settings": "Settings",
        }
        for name, frame in self.frames.items():
            if name == key:
                frame.tkraise()
            else:
                frame.lower()
        self.tab_title.configure(text=titles.get(key, key.title()))

    def _on_nav(self, key: str):
        self._show_frame(key)


if __name__ == "__main__":
    app = App()
    app.mainloop()


# ================================
# import tkinter as tk
# from tkinter import ttk
# from tkinter import scrolledtext, filedialog
# from dataclasses import dataclass
# import os
#
# # ============================
# # Theme & Style
# # ============================
# PRIMARY_BG = "#0f1115"      # app background
# PANEL_BG   = "#141720"      # cards / panels
# FG         = "#f2f2f2"      # main text
# SUB_FG     = "#b9beca"      # secondary text
# ACCENT     = "#ffffff"      # pure white accents
# BORDER     = "#1e2230"      # borders
# MUTED      = "#2a2f40"      # hover / selection
# SUCCESS    = "#2ecc71"
# WARNING    = "#f1c40f"
# DANGER     = "#e74c3c"
# INFO       = "#3498db"
#
# CARD_RADIUS = 18
#
#
# def apply_dark_style(root: tk.Tk) -> ttk.Style:
#     style = ttk.Style(root)
#     # Use clam theme for better control
#     style.theme_use("clam")
#
#     # Global
#     style.configure(".",
#                     background=PRIMARY_BG,
#                     foreground=FG,
#                     fieldbackground=PANEL_BG,
#                     bordercolor=BORDER)
#
#     # Frames
#     style.configure("TFrame", background=PRIMARY_BG)
#     style.configure("Panel.TFrame", background=PANEL_BG)
#
#     # Labels
#     style.configure("TLabel", background=PRIMARY_BG, foreground=FG)
#     style.configure("Muted.TLabel", background=PRIMARY_BG, foreground=SUB_FG)
#     style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"))
#     style.configure("CardTitle.TLabel", background=PANEL_BG, foreground=SUB_FG)
#     style.configure("CardNumber.TLabel", background=PANEL_BG, foreground=FG, font=("Segoe UI", 22, "bold"))
#
#     # Buttons
#     style.configure("TButton",
#                     background=PANEL_BG, foreground=FG,
#                     bordercolor=BORDER, focusthickness=0, focuscolor=BORDER,
#                     padding=8)
#     style.map("TButton",
#               background=[("active", MUTED)],
#               foreground=[("disabled", SUB_FG)])
#
#     # Nav buttons
#     style.configure("Nav.TButton", anchor="w")
#
#     # Treeview
#     style.configure("Treeview",
#                     background=PANEL_BG, fieldbackground=PANEL_BG,
#                     foreground=FG, bordercolor=BORDER)
#     style.map("Treeview",
#               background=[("selected", MUTED)])
#
#     # Entry / Combobox
#     style.configure("TEntry", fieldbackground=PANEL_BG, insertcolor=FG, foreground=FG)
#     style.configure("TCombobox", fieldbackground=PANEL_BG)
#
#     # Separator
#     style.configure("TSeparator", background=BORDER)
#
#     return style
#
#
# @dataclass
# class AppState:
#     current_session_id: str | None = None
#
#
# class Sidebar(ttk.Frame):
#     def __init__(self, master, on_nav):
#         super().__init__(master, style="TFrame")
#         self.on_nav = on_nav
#         self.configure(padding=16)
#         self._build()
#
#     def _build(self):
#         # Logo / App name
#         logo = ttk.Label(self, text="📝 AI Meeting Assistant", style="Heading.TLabel")
#         logo.pack(anchor="w", pady=(0, 10))
#         sub = ttk.Label(self, text="Dashboard", style="Muted.TLabel")
#         sub.pack(anchor="w", pady=(0, 20))
#
#         ttk.Separator(self).pack(fill="x", pady=10)
#
#         # Nav buttons
#         nav_items = [
#             ("🟢 Start New Meeting", "start"),
#             ("📁 Sessions", "sessions"),
#             ("📊 Dashboard", "dashboard"),
#             ("📄 Reports", "reports"),
#             ("⚙ Settings", "settings"),
#         ]
#         for text, key in nav_items:
#             btn = ttk.Button(self, text=text, style="Nav.TButton",
#                              command=lambda k=key: self.on_nav(k))
#             btn.pack(fill="x", pady=4)
#
#         # Footer
#         ttk.Separator(self).pack(fill="x", pady=16)
#         foot = ttk.Label(self, text="© 2025", style="Muted.TLabel")
#         foot.pack(anchor="w")
#
#
# class StartTab(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master, style="TFrame", padding=16)
#         self.audio_file_path: str | None = None
#         self._build()
#
#     def _build(self):
#         # Controls bar
#         controls = ttk.Frame(self, style="Panel.TFrame", padding=14)
#         controls.grid(row=0, column=0, sticky="ew")
#         for col in (0,1,2,3,4,5):
#             controls.grid_columnconfigure(col, minsize=10)
#         controls.grid_columnconfigure(6, weight=1)  # spacer
#
#         self.start_btn    = ttk.Button(controls, text="▶ Start", command=self.on_start)
#         self.pause_btn    = ttk.Button(controls, text="⏸ Pause", command=self.on_pause, state="disabled")
#         self.continue_btn = ttk.Button(controls, text="▶ Continue", command=self.on_continue, state="disabled")
#         self.stop_btn     = ttk.Button(controls, text="⏹ Stop", command=self.on_stop, state="disabled")
#         self.timer_lbl    = ttk.Label(controls, text="00:00:00", style="Heading.TLabel")
#
#         self.import_btn   = ttk.Button(controls, text="📂 Add Recording", command=self.on_import)
#         self.file_label   = ttk.Label(controls, text="No file", style="Muted.TLabel")
#
#         # Layout controls
#         self.start_btn.grid(row=0, column=0, padx=(0,6))
#         self.pause_btn.grid(row=0, column=1, padx=6)
#         self.continue_btn.grid(row=0, column=1, padx=6)
#         self.continue_btn.grid_remove()
#         self.stop_btn.grid(row=0, column=3, padx=6)
#         ttk.Separator(controls, orient="vertical").grid(row=0, column=4, padx=10, sticky="ns")
#         self.timer_lbl.grid(row=0, column=5, padx=(0,12))
#         self.import_btn.grid(row=0, column=7, padx=(0,8))
#         self.file_label.grid(row=0, column=8)
#
#         # Body (Transcript only)
#         body = ttk.Frame(self, style="TFrame")
#         body.grid(row=1, column=0, sticky="nsew", pady=(12,0))
#         self.grid_rowconfigure(1, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#
#         transcript_card = ttk.Frame(body, style="Panel.TFrame", padding=14)
#         transcript_card.grid(row=0, column=0, sticky="nsew")
#         body.grid_rowconfigure(0, weight=1)
#         body.grid_columnconfigure(0, weight=1)
#
#         ttk.Label(transcript_card, text="🗣 Transcript (live)", style="CardTitle.TLabel").pack(anchor="w")
#         self.transcript = scrolledtext.ScrolledText(
#             transcript_card, height=18, bg=PANEL_BG, fg=FG, insertbackground=FG,
#             bd=0, relief="flat", padx=8, pady=8
#         )
#         self.transcript.pack(fill="both", expand=True, pady=(8,0))
#         self.transcript.configure(state="disabled")
#
#     # --- Event handlers (stubs to connect later) ---
#     def on_start(self):
#         self._set_controls(recording=True)
#         # TODO: hook SessionManager + Recorder start
#
#     def on_pause(self):
#         # Swap Pause -> Continue
#         self.pause_btn.grid_remove()
#         self.continue_btn.configure(state="normal")
#         self.continue_btn.grid()
#         # TODO: hook Recorder pause
#
#     def on_continue(self):
#         # Swap Continue -> Pause
#         self.continue_btn.grid_remove()
#         self.pause_btn.configure(state="normal")
#         self.pause_btn.grid()
#         # TODO: hook Recorder resume
#
#     def on_stop(self):
#         self._set_controls(recording=False)
#         # TODO: hook Recorder stop + finalize pipeline
#
#     def on_import(self):
#         path = filedialog.askopenfilename(
#             title="Chọn file ghi âm",
#             filetypes=[("Audio", "*.wav *.mp3 *.m4a *.flac"), ("All", "*.*")]
#         )
#         if path:
#             self.audio_file_path = path
#             base = os.path.basename(path)
#             self.file_label.configure(text=base)
#             self.append_transcript(f"\n[Imported file] {base}\n")
#
#     # --- Controls state ---
#     def _set_controls(self, recording: bool):
#         if recording:
#             self.start_btn.configure(state="disabled")
#             self.pause_btn.configure(state="normal")
#             self.continue_btn.configure(state="disabled")
#             self.stop_btn.configure(state="normal")
#             self.continue_btn.grid_remove()
#             self.pause_btn.grid()
#         else:
#             self.start_btn.configure(state="normal")
#             self.pause_btn.configure(state="disabled")
#             self.continue_btn.configure(state="disabled")
#             self.stop_btn.configure(state="disabled")
#             self.continue_btn.grid_remove()
#             self.pause_btn.grid()
#
#     # Public method to append transcript (thread-safe via after)
#     def append_transcript(self, text: str):
#         def _append():
#             self.transcript.configure(state="normal")
#             self.transcript.insert("end", text + " ")
#             self.transcript.see("end")
#             self.transcript.configure(state="disabled")
#         self.after(0, _append)
#
#
# class SessionsTab(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master, style="TFrame", padding=16)
#         self._build()
#
#     def _build(self):
#         # Filter/search bar
#         bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
#         bar.grid(row=0, column=0, sticky="ew")
#         self.grid_columnconfigure(0, weight=1)
#
#         ttk.Label(bar, text="🔎 Search:").grid(row=0, column=0, padx=(0,6))
#         self.search_var = tk.StringVar()
#         search_entry = ttk.Entry(bar, textvariable=self.search_var, width=32)
#         search_entry.grid(row=0, column=1)
#
#         ttk.Label(bar, text=" Status:").grid(row=0, column=2, padx=(12,6))
#         self.status_var = tk.StringVar(value="All")
#         status = ttk.Combobox(bar, textvariable=self.status_var, values=["All","recording","processing","completed"], width=16, state="readonly")
#         status.grid(row=0, column=3)
#
#         ttk.Button(bar, text="Refresh", command=self.refresh).grid(row=0, column=4, padx=(12,0))
#
#         # Table
#         table_frame = ttk.Frame(self, style="Panel.TFrame", padding=8)
#         table_frame.grid(row=1, column=0, sticky="nsew", pady=(12,0))
#         self.grid_rowconfigure(1, weight=1)
#
#         cols = ("id","title","start","duration","status")
#         self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
#         for c in cols:
#             self.tree.heading(c, text=c.title())
#             self.tree.column(c, width=140 if c!="title" else 260, anchor="w")
#         self.tree.pack(fill="both", expand=True)
#
#         # Demo data
#         self._demo_rows()
#
#     def _demo_rows(self):
#         for i in range(1,6):
#             self.tree.insert("", "end", values=(f"MSN-{1000+i}", f"Dự án A - Họp {i}", "2025-08-10 09:30", "45m", "completed" if i%2 else "processing"))
#
#     def refresh(self):
#         # TODO: query MySQL and update tree
#         pass
#
#
# class DashboardTab(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master, style="TFrame", padding=16)
#         self._build()
#
#     def _build(self):
#         # Grid cards
#         grid = ttk.Frame(self, style="TFrame")
#         grid.grid(row=0, column=0, sticky="nsew")
#         self.grid_columnconfigure(0, weight=1)
#         self.grid_rowconfigure(1, weight=1)
#
#         cards = [
#             ("Tổng cuộc họp", "24"),
#             ("Tổng thời lượng", "18h 30m"),
#             ("Action Items", "56"),
#             ("Completion Rate", "72%"),
#         ]
#         for idx, (title, number) in enumerate(cards):
#             r, c = divmod(idx, 2)
#             card = ttk.Frame(grid, style="Panel.TFrame", padding=16)
#             card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
#             grid.grid_columnconfigure(c, weight=1)
#             ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
#             ttk.Label(card, text=number, style="CardNumber.TLabel").pack(anchor="w")
#
#         # Placeholder area for charts (future)
#         chart = ttk.Frame(self, style="Panel.TFrame", padding=16)
#         chart.grid(row=1, column=0, sticky="nsew", pady=(12,0))
#         ttk.Label(chart, text="📈 Charts (Keywords / Trends) — sẽ được vẽ sau", style="CardTitle.TLabel").pack(anchor="w")
#
#
# class ReportsTab(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master, style="TFrame", padding=16)
#         self._build()
#
#     def _build(self):
#         bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
#         bar.grid(row=0, column=0, sticky="ew")
#
#         ttk.Button(bar, text="Open Folder", command=self.open_folder).grid(row=0, column=0)
#         ttk.Button(bar, text="Regenerate", command=self.regenerate).grid(row=0, column=1, padx=8)
#
#         table = ttk.Frame(self, style="Panel.TFrame", padding=8)
#         table.grid(row=1, column=0, sticky="nsew", pady=(12,0))
#         self.grid_rowconfigure(1, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#
#         cols = ("session","report_path","created")
#         self.tree = ttk.Treeview(table, columns=cols, show="headings")
#         for c in cols:
#             self.tree.heading(c, text=c.title())
#             self.tree.column(c, anchor="w", width=260 if c=="report_path" else 160)
#         self.tree.pack(fill="both", expand=True)
#
#         # Demo rows
#         self.tree.insert("", "end", values=("MSN-1001", "records/1001/meeting_report.docx", "2025-08-10 11:02"))
#
#     def open_folder(self):
#         filedialog.askdirectory()
#
#     def regenerate(self):
#         pass
#
#
# class SettingsTab(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master, style="TFrame", padding=16)
#         self._build()
#
#     def _build(self):
#         # Two-column form
#         form = ttk.Frame(self, style="Panel.TFrame", padding=16)
#         form.grid(row=0, column=0, sticky="nsew")
#         self.grid_columnconfigure(0, weight=1)
#
#         row = 0
#         def add_field(label, widget):
#             nonlocal row
#             ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=6)
#             widget.grid(row=row, column=1, sticky="ew", pady=6, padx=(12,0))
#             form.grid_columnconfigure(1, weight=1)
#             row += 1
#
#         # ASR
#         asr_model = ttk.Combobox(form, values=["tiny","base","small","medium","large-v2"], state="readonly")
#         asr_model.set("medium")
#         add_field("ASR Model (Whisper)", asr_model)
#
#         # GPT
#         gpt_model = ttk.Entry(form)
#         gpt_model.insert(0, "gpt-4o-mini")
#         add_field("GPT Model", gpt_model)
#
#         # MySQL
#         mysql_host = ttk.Entry(form); mysql_host.insert(0, "localhost")
#         mysql_user = ttk.Entry(form); mysql_user.insert(0, "root")
#         mysql_pass = ttk.Entry(form, show="*")
#         mysql_db   = ttk.Entry(form); mysql_db.insert(0, "meeting_db")
#         add_field("MySQL Host", mysql_host)
#         add_field("MySQL User", mysql_user)
#         add_field("MySQL Password", mysql_pass)
#         add_field("MySQL Database", mysql_db)
#
#         # Paths
#         base_dir = ttk.Entry(form); base_dir.insert(0, "./records")
#         add_field("Base Folder", base_dir)
#
#         # Autosave / Misc
#         autosave = ttk.Entry(form); autosave.insert(0, "2")
#         add_field("Autosave Interval (s)", autosave)
#
#         # Save button
#         save = ttk.Button(self, text="💾 Save Settings", command=lambda: None)
#         save.grid(row=1, column=0, sticky="e", pady=(12,0))
#
#
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("AI Meeting Assistant — Dashboard")
#         self.geometry("1200x720")
#         self.configure(bg=PRIMARY_BG)
#         self.minsize(1024, 640)
#         self.state = AppState()
#
#         apply_dark_style(self)
#         self._build_layout()
#
#     def _build_layout(self):
#         # Grid: 0 = sidebar (fixed ~240px), 1 = main
#         self.grid_columnconfigure(0, minsize=240)
#         self.grid_columnconfigure(1, weight=1)
#         self.grid_rowconfigure(0, weight=1)
#
#         self.sidebar = Sidebar(self, on_nav=self._on_nav)
#         self.sidebar.grid(row=0, column=0, sticky="nsw")
#
#         # Main area (no Notebook) — title bar + content container
#         self.main = ttk.Frame(self, style="TFrame", padding=(12,12))
#         self.main.grid(row=0, column=1, sticky="nsew")
#         self.main.grid_rowconfigure(1, weight=1)
#         self.main.grid_columnconfigure(0, weight=1)
#
#         # Current tab title
#         self.tab_title = ttk.Label(self.main, text="Start New Meeting", style="Heading.TLabel")
#         self.tab_title.grid(row=0, column=0, sticky="w", pady=(0,8))
#         ttk.Separator(self.main).grid(row=0, column=0, sticky="ew", pady=(36,8))
#
#         # Content container that will swap frames
#         self.content = ttk.Frame(self.main, style="TFrame")
#         self.content.grid(row=1, column=0, sticky="nsew")
#         self.content.grid_rowconfigure(0, weight=1)
#         self.content.grid_columnconfigure(0, weight=1)
#
#         # Instantiate pages
#         self.frames = {
#             "start":    StartTab(self.content),
#             "sessions": SessionsTab(self.content),
#             "dashboard":DashboardTab(self.content),
#             "reports":  ReportsTab(self.content),
#             "settings": SettingsTab(self.content),
#         }
#         for f in self.frames.values():
#             f.grid(row=0, column=0, sticky="nsew")
#
#         self._show_frame("start")
#
#     def _show_frame(self, key: str):
#         titles = {
#             "start": "Start New Meeting",
#             "sessions": "Sessions",
#             "dashboard": "Dashboard",
#             "reports": "Reports",
#             "settings": "Settings",
#         }
#         for name, frame in self.frames.items():
#             if name == key:
#                 frame.tkraise()
#             else:
#                 frame.lower()
#         self.tab_title.configure(text=titles.get(key, key.title()))
#
#     def _on_nav(self, key: str):
#         self._show_frame(key)
#
#
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
