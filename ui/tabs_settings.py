# -----------------------------------
# file: meeting_assistant/ui/tabs_settings.py
# -----------------------------------
from __future__ import annotations
import os
from tkinter import ttk, filedialog, messagebox
from core.logger import logger
from core.config import AppConfig, CONFIG, save_config, set_config
from db.mysql import reset_connection

class SettingsTab(ttk.Frame):
    def __init__(self, master):
        logger.debug("SettingsTab.__init__")
        super().__init__(master, padding=16)
        self._build()
        self._load_from_config()

    def _build(self):
        logger.debug("SettingsTab._build UI")
        form = ttk.Frame(self, style="Panel.TFrame", padding=16)
        form.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        row = 0
        def add(label, widget, browse_btn=False):
            nonlocal row
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=6)
            widget.grid(row=row, column=1, sticky="ew", pady=6, padx=(12,0))
            form.grid_columnconfigure(1, weight=1)
            if browse_btn:
                ttk.Button(form, text="Browse", command=self._browse_base_dir).grid(row=row, column=2, padx=8)
            row += 1

        # --- ASR / GPT ---
        self.cb_asr = ttk.Combobox(form, values=["tiny","base","small","medium","large-v2"], state="readonly")
        add("ASR Model (Whisper)", self.cb_asr)

        self.e_gpt = ttk.Entry(form)
        add("GPT Model", self.e_gpt)

        self.e_openai = ttk.Entry(form, show="*")
        add("OpenAI API Key", self.e_openai)

        # --- MySQL ---
        self.e_host = ttk.Entry(form)
        add("MySQL Host", self.e_host)

        self.e_user = ttk.Entry(form)
        add("MySQL User", self.e_user)

        self.e_pass = ttk.Entry(form, show="*")
        add("MySQL Password", self.e_pass)

        self.e_db = ttk.Entry(form)
        add("MySQL Database", self.e_db)

        # --- Paths / autosave ---
        self.e_base = ttk.Entry(form)
        add("Base Folder", self.e_base, browse_btn=True)

        self.e_autosave = ttk.Entry(form, width=8)
        add("Autosave Interval (s)", self.e_autosave)

        # actions
        actions = ttk.Frame(self)
        actions.grid(row=1, column=0, sticky="e", pady=(12,0))
        ttk.Button(actions, text="💾 Save Settings", command=self._save).grid(row=0, column=0, padx=(0,8))
        ttk.Button(actions, text="Test DB", command=self._test_db).grid(row=0, column=1)

    def _load_from_config(self):
        logger.debug("SettingsTab._load_from_config")
        self.cb_asr.set(CONFIG.asr_model)
        self.e_gpt.delete(0, "end"); self.e_gpt.insert(0, CONFIG.gpt_model)
        self.e_openai.delete(0, "end"); self.e_openai.insert(0, CONFIG.openai_api_key or "")

        self.e_host.delete(0, "end"); self.e_host.insert(0, CONFIG.mysql_host)
        self.e_user.delete(0, "end"); self.e_user.insert(0, CONFIG.mysql_user)
        self.e_pass.delete(0, "end"); self.e_pass.insert(0, CONFIG.mysql_password)
        self.e_db.delete(0, "end"); self.e_db.insert(0, CONFIG.mysql_db)

        self.e_base.delete(0, "end"); self.e_base.insert(0, CONFIG.base_dir)
        self.e_autosave.delete(0, "end"); self.e_autosave.insert(0, str(CONFIG.autosave_sec))

    def _browse_base_dir(self):
        logger.info("SettingsTab._browse_base_dir")
        path = filedialog.askdirectory(initialdir=self.e_base.get() or os.getcwd(), title="Chọn thư mục lưu trữ")
        if path:
            self.e_base.delete(0, "end")
            self.e_base.insert(0, path)

    def _save(self):
        try:
            autosave_sec = int(self.e_autosave.get().strip() or "2")
            if autosave_sec < 1:
                raise ValueError("Autosave phải >= 1 giây")

            new_cfg = AppConfig(
                mysql_host=self.e_host.get().strip() or "localhost",
                mysql_user=self.e_user.get().strip() or "root",
                mysql_password=self.e_pass.get().strip(),
                mysql_db=self.e_db.get().strip() or "meeting_db",
                base_dir=self.e_base.get().strip() or "./records",
                openai_api_key=self.e_openai.get().strip(),
                gpt_model=self.e_gpt.get().strip() or "gpt-4o-mini",
                asr_model=self.cb_asr.get().strip() or "medium",
                autosave_sec=autosave_sec,
            )

            # 1) save to .env
            env_path = save_config(new_cfg)
            # 2) update in-memory CONFIG
            set_config(new_cfg)
            # 3) reset DB connection (sẽ mở lại theo cấu hình mới ở lần query sau)
            reset_connection()

            # 4) tạo base_dir nếu chưa có
            os.makedirs(new_cfg.base_dir, exist_ok=True)

            messagebox.showinfo("Saved", f"Settings saved.\n.env → {env_path}")
        except Exception as e:
            logger.exception("Settings save error: %s", e)
            messagebox.showerror("Error", str(e))

    def _test_db(self):
        logger.info("SettingsTab._test_db")
        # tạm thời mở / đóng kết nối để kiểm tra credential
        try:
            from db.mysql import get_conn
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            messagebox.showinfo("DB OK", f"Kết nối MySQL thành công tới {CONFIG.mysql_host}/{CONFIG.mysql_db}")
        except Exception as e:
            logger.exception("Test DB failed: %s", e)
            messagebox.showerror("DB Error", str(e))
