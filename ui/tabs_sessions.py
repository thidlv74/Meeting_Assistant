# -----------------------------------
# file: meeting_assistant/ui/tabs_sessions.py
# -----------------------------------
import tkinter as tk
from tkinter import ttk

class SessionsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._build()

    def _build(self):
        bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
        bar.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(bar, text="🔎 Search:").grid(row=0, column=0, padx=(0,6))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bar, textvariable=self.search_var, width=32)
        search_entry.grid(row=0, column=1)

        ttk.Label(bar, text=" Status:").grid(row=0, column=2, padx=(12,6))
        self.status_var = tk.StringVar(value="All")
        status = ttk.Combobox(bar, textvariable=self.status_var, values=["All","recording","processing","completed"], width=16, state="readonly")
        status.grid(row=0, column=3)

        ttk.Button(bar, text="Refresh", command=self.refresh).grid(row=0, column=4, padx=(12,0))

        table_frame = ttk.Frame(self, style="Panel.TFrame", padding=8)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        self.grid_rowconfigure(1, weight=1)

        cols = ("id","title","start","duration","status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=140 if c!="title" else 260, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._demo_rows()

    def _demo_rows(self):
        for i in range(1,6):
            self.tree.insert("", "end", values=(f"MSN-{1000+i}", f"Dự án A - Họp {i}", "2025-08-10 09:30", "45m", "completed" if i%2 else "processing"))

    def refresh(self):
        pass