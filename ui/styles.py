# --------------------------------
# file: meeting_assistant/ui/styles.py
# --------------------------------
import tkinter as tk
from tkinter import ttk

PRIMARY_BG = "#0f1115"
PANEL_BG   = "#141720"
FG         = "#f2f2f2"
SUB_FG     = "#b9beca"
ACCENT     = "#ffffff"
BORDER     = "#1e2230"
MUTED      = "#2a2f40"


def heading_style_name():
    return "Heading.TLabel"


def apply_dark_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=PRIMARY_BG, foreground=FG, fieldbackground=PANEL_BG, bordercolor=BORDER)
    style.configure("TFrame", background=PRIMARY_BG)
    style.configure("Panel.TFrame", background=PANEL_BG)

    style.configure("TLabel", background=PRIMARY_BG, foreground=FG)
    style.configure("Muted.TLabel", background=PRIMARY_BG, foreground=SUB_FG)
    style.configure(heading_style_name(), font=("Segoe UI", 16, "bold"))
    style.configure("CardTitle.TLabel", background=PANEL_BG, foreground=SUB_FG)
    style.configure("CardNumber.TLabel", background=PANEL_BG, foreground=FG, font=("Segoe UI", 22, "bold"))

    style.configure("TButton", background=PANEL_BG, foreground=FG, bordercolor=BORDER, focusthickness=0, focuscolor=BORDER, padding=8)
    style.map("TButton", background=[("active", MUTED)], foreground=[("disabled", SUB_FG)])
    style.configure("Nav.TButton", anchor="w")

    style.configure("Treeview", background=PANEL_BG, fieldbackground=PANEL_BG, foreground=FG, bordercolor=BORDER)
    style.map("Treeview", background=[("selected", MUTED)])

    style.configure("Treeview.Heading", background=PANEL_BG, foreground=SUB_FG, bordercolor=BORDER)
    style.map("Treeview.Heading", background=[("active", MUTED)])

    style.configure("TEntry", fieldbackground=PANEL_BG, insertcolor=FG, foreground=FG)
    style.configure("TCombobox", fieldbackground=PANEL_BG)
    style.configure("TSeparator", background=BORDER)

    return style