# ================================
# meeting_assistant — project files (with debug logs)
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
from ui.tabs_settings import SettingsTab
from core.logger import logger


class App(tk.Tk):
    def __init__(self):
        logger.info("App.__init__ starting")
        super().__init__()
        self.title("AI Meeting Assistant — Dashboard")
        self.geometry("1200x720")
        self.configure(bg=PRIMARY_BG)
        self.minsize(1024, 640)

        apply_dark_style(self)
        self._build_layout()
        logger.info("App.__init__ finished")

    def _build_layout(self):
        logger.debug("App._build_layout: configuring grid and sidebar")
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
        logger.debug("App._build_layout: creating frames")
        self.frames = {
            "start":    StartTab(self.content),
            "sessions": SessionsTab(self.content),
            "dashboard":DashboardTab(self.content),
            "settings": SettingsTab(self.content),
        }
        for name, f in self.frames.items():
            logger.debug(f"Adding frame '{name}' to grid")
            f.grid(row=0, column=0, sticky="nsew")

        self._show_frame("start")

    def _show_frame(self, key: str):
        logger.info(f"App._show_frame: switching to '{key}'")
        titles = {
            "start": "Start New Meeting",
            "sessions": "Sessions",
            "dashboard": "Dashboard",
            "settings": "Settings",
        }
        for name, frame in self.frames.items():
            if name == key:
                frame.tkraise()
            else:
                frame.lower()
        self.tab_title.configure(text=titles.get(key, key.title()))

    def _on_nav(self, key: str):
        logger.debug(f"App._on_nav: clicked '{key}'")
        self._show_frame(key)


if __name__ == "__main__":
    logger.info("Launching Tk app")
    app = App()
    app.mainloop()
