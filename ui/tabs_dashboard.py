# ------------------------------------
# file: meeting_assistant/ui/tabs_dashboard.py
# ------------------------------------
from tkinter import ttk

class DashboardTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._build()

    def _build(self):
        grid = ttk.Frame(self)
        grid.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cards = [
            ("Tổng cuộc họp", "24"),
            ("Tổng thời lượng", "18h 30m"),
            ("Action Items", "56"),
            ("Completion Rate", "72%"),
        ]
        for idx, (title, number) in enumerate(cards):
            r, c = divmod(idx, 2)
            card = ttk.Frame(grid, style="Panel.TFrame", padding=16)
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            grid.grid_columnconfigure(c, weight=1)
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, text=number, style="CardNumber.TLabel").pack(anchor="w")

        chart = ttk.Frame(self, style="Panel.TFrame", padding=16)
        chart.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        ttk.Label(chart, text="📈 Charts (Keywords / Trends) — sẽ được vẽ sau", style="CardTitle.TLabel").pack(anchor="w")

