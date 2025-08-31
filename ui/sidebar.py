
# --------------------------------
# file: meeting_assistant/ui/sidebar.py
# --------------------------------
import tkinter as tk
from tkinter import ttk
from core.logger import logger

class Sidebar(ttk.Frame):
    def __init__(self, master, on_nav):
        logger.debug("Sidebar.__init__")
        super().__init__(master)
        self.on_nav = on_nav
        self.configure(padding=16)
        self._build()

    def _build(self):
        logger.debug("Sidebar._build")
        logo = ttk.Label(self, text="📝 AI Meeting Assistant", style="Heading.TLabel")
        logo.pack(anchor="w", pady=(0, 10))
        sub = ttk.Label(self, text="Dashboard", style="Muted.TLabel")
        sub.pack(anchor="w", pady=(0, 20))

        ttk.Separator(self).pack(fill="x", pady=10)

        nav_items = [
            ("🟢 Start New Meeting", "start"),
            ("📁 Sessions", "sessions"),
            ("📊 Dashboard", "dashboard"),
            ("⚙ Settings", "settings"),
        ]
        for text, key in nav_items:
            btn = ttk.Button(self, text=text, style="Nav.TButton", command=lambda k=key: (logger.debug(f"Sidebar click: {k}"), self.on_nav(k)))
            btn.pack(fill="x", pady=4)

        ttk.Separator(self).pack(fill="x", pady=16)
        foot = ttk.Label(self, text="© 2025", style="Muted.TLabel")
        foot.pack(anchor="w")