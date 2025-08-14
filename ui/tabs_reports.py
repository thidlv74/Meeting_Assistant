# ----------------------------------
# file: meeting_assistant/ui/tabs_reports.py
# ----------------------------------
import tkinter as tk
from tkinter import ttk, filedialog

class ReportsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._build()

    def _build(self):
        bar = ttk.Frame(self, style="Panel.TFrame", padding=12)
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Open Folder", command=self.open_folder).grid(row=0, column=0)
        ttk.Button(bar, text="Regenerate", command=self.regenerate).grid(row=0, column=1, padx=8)

        table = ttk.Frame(self, style="Panel.TFrame", padding=8)
        table.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cols = ("session","report_path","created")
        self.tree = ttk.Treeview(table, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, anchor="w", width=260 if c=="report_path" else 160)
        self.tree.pack(fill="both", expand=True)

        self.tree.insert("", "end", values=("MSN-1001", "records/1001/meeting_report.docx", "2025-08-10 11:02"))

    def open_folder(self):
        filedialog.askdirectory()

    def regenerate(self):
        pass