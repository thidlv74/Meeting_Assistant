# ------------------------------
# file: meeting_assistant/ui/infopanel.py
# ------------------------------
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

class InfoPanel(ttk.Frame):
    """Optional side panel to show Summary / Decisions / Action Items.
    Methods:
      - set_summary(text)
      - set_decisions(list[str])
      - set_action_items(list[dict[item, assignee, due, done]])
    """
    def __init__(self, master):
        super().__init__(master, padding=10)
        self._build()

    def _build(self):
        # Summary
        sum_card = ttk.Frame(self, style="Panel.TFrame", padding=12)
        sum_card.pack(fill="both", expand=False, pady=(0,10))
        ttk.Label(sum_card, text="Summary", style="CardTitle.TLabel").pack(anchor="w")
        from ui.styles import PANEL_BG, FG
        self.summary = scrolledtext.ScrolledText(sum_card, height=8, bd=0, relief="flat")
        self.summary.configure(bg=PANEL_BG, fg=FG, insertbackground=FG, padx=8, pady=8, state="disabled")
        self.summary.pack(fill="both", expand=True, pady=(8,0))

        # Decisions
        dec_card = ttk.Frame(self, style="Panel.TFrame", padding=12)
        dec_card.pack(fill="both", expand=False, pady=(0,10))
        ttk.Label(dec_card, text="Decisions", style="CardTitle.TLabel").pack(anchor="w")
        self.decisions = tk.Listbox(dec_card, height=6, bd=0, highlightthickness=0)
        self.decisions.pack(fill="both", expand=True, pady=(8,0))

        # Action Items
        ai_card = ttk.Frame(self, style="Panel.TFrame", padding=12)
        ai_card.pack(fill="both", expand=True)
        ttk.Label(ai_card, text="Action Items", style="CardTitle.TLabel").pack(anchor="w")
        cols = ("item","assignee","due","done")
        self.ai_tree = ttk.Treeview(ai_card, columns=cols, show="headings")
        for c, w in zip(cols, (220, 120, 90, 70)):
            self.ai_tree.heading(c, text=c.title())
            self.ai_tree.column(c, width=w, anchor="w")
        self.ai_tree.pack(fill="both", expand=True, pady=(8,0))

    # --- Update methods ---
    def set_summary(self, text: str):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("end", text or "Chưa xác định")
        self.summary.configure(state="disabled")

    def set_decisions(self, decisions: list[str]):
        self.decisions.delete(0, "end")
        for d in (decisions or ["Chưa xác định"]):
            self.decisions.insert("end", f"• {d}")

    def set_action_items(self, items: list[dict]):
        for i in self.ai_tree.get_children():
            self.ai_tree.delete(i)
        for it in (items or []):
            self.ai_tree.insert("", "end", values=(it.get("item",""), it.get("assignee",""), it.get("due",""), "✔" if it.get("done") else ""))
