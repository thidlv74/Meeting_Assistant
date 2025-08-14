# -----------------------------------
# file: meeting_assistant/ui/tabs_settings.py
# -----------------------------------
from tkinter import ttk

class SettingsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._build()

    def _build(self):
        form = ttk.Frame(self, style="Panel.TFrame", padding=16)
        form.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        row = 0
        def add(label, widget):
            nonlocal row
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=6)
            widget.grid(row=row, column=1, sticky="ew", pady=6, padx=(12,0))
            form.grid_columnconfigure(1, weight=1)
            row += 1

        from core.config import CONFIG
        asr_model = ttk.Combobox(form, values=["tiny","base","small","medium","large-v2"], state="readonly")
        asr_model.set(CONFIG.asr_model)
        add("ASR Model (Whisper)", asr_model)

        gpt_model = ttk.Entry(form)
        gpt_model.insert(0, CONFIG.gpt_model)
        add("GPT Model", gpt_model)

        mysql_host = ttk.Entry(form); mysql_host.insert(0, CONFIG.mysql_host)
        mysql_user = ttk.Entry(form); mysql_user.insert(0, CONFIG.mysql_user)
        mysql_pass = ttk.Entry(form, show="*")
        mysql_db   = ttk.Entry(form); mysql_db.insert(0, CONFIG.mysql_db)
        add("MySQL Host", mysql_host)
        add("MySQL User", mysql_user)
        add("MySQL Password", mysql_pass)
        add("MySQL Database", mysql_db)

        base_dir = ttk.Entry(form); base_dir.insert(0, CONFIG.base_dir)
        add("Base Folder", base_dir)

        autosave = ttk.Entry(form); autosave.insert(0, str(CONFIG.autosave_sec))
        add("Autosave Interval (s)", autosave)

        save = ttk.Button(self, text="💾 Save Settings", command=lambda: None)
        save.grid(row=1, column=0, sticky="e", pady=(12,0))
