# --------------------------------
# file: meeting_assistant/ui/tabs_start.py
# --------------------------------
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from core.session_manager import SESSION_MANAGER

class StartTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.audio_file_path: str | None = None
        self._build()

    def _build(self):
        controls = ttk.Frame(self, style="Panel.TFrame", padding=14)
        controls.grid(row=0, column=0, sticky="ew")
        for col in (0,1,2,3,4,5):
            controls.grid_columnconfigure(col, minsize=10)
        controls.grid_columnconfigure(6, weight=1)

        self.start_btn    = ttk.Button(controls, text="▶ Start", command=self.on_start)
        self.pause_btn    = ttk.Button(controls, text="⏸ Pause", command=self.on_pause, state="disabled")
        self.continue_btn = ttk.Button(controls, text="▶ Continue", command=self.on_continue, state="disabled")
        self.stop_btn     = ttk.Button(controls, text="⏹ Stop", command=self.on_stop, state="disabled")
        self.timer_lbl    = ttk.Label(controls, text="00:00:00", style="Heading.TLabel")

        self.import_btn   = ttk.Button(controls, text="📂 Add Recording", command=self.on_import)
        self.file_label   = ttk.Label(controls, text="No file", style="Muted.TLabel")

        self.start_btn.grid(row=0, column=0, padx=(0,6))
        self.pause_btn.grid(row=0, column=1, padx=6)
        self.continue_btn.grid(row=0, column=1, padx=6)
        self.continue_btn.grid_remove()
        self.stop_btn.grid(row=0, column=3, padx=6)
        ttk.Separator(controls, orient="vertical").grid(row=0, column=4, padx=10, sticky="ns")
        self.timer_lbl.grid(row=0, column=5, padx=(0,12))
        self.import_btn.grid(row=0, column=7, padx=(0,8))
        self.file_label.grid(row=0, column=8)

        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        transcript_card = ttk.Frame(body, style="Panel.TFrame", padding=14)
        transcript_card.grid(row=0, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        ttk.Label(transcript_card, text="🗣 Transcript (live)", style="CardTitle.TLabel").pack(anchor="w")
        self.transcript = scrolledtext.ScrolledText(transcript_card, height=18, bd=0, relief="flat")
        # apply dark colors
        from ui.styles import PANEL_BG, FG
        self.transcript.configure(bg=PANEL_BG, fg=FG, insertbackground=FG, padx=8, pady=8)
        self.transcript.pack(fill="both", expand=True, pady=(8,0))
        self.transcript.configure(state="disabled")

    def on_start(self):
        self._set_controls(recording=True)
        SESSION_MANAGER.create()
        SESSION_MANAGER.start()

    def on_pause(self):
        self.pause_btn.grid_remove()
        self.continue_btn.configure(state="normal")
        self.continue_btn.grid()
        SESSION_MANAGER.pause()

    def on_continue(self):
        self.continue_btn.grid_remove()
        self.pause_btn.configure(state="normal")
        self.pause_btn.grid()
        SESSION_MANAGER.resume()

    def on_stop(self):
        self._set_controls(recording=False)
        SESSION_MANAGER.stop()

    def on_import(self):
        path = filedialog.askopenfilename(
            title="Chọn file ghi âm",
            filetypes=[("Audio", "*.wav *.mp3 *.m4a *.flac"), ("All", "*.*")]
        )
        if path:
            self.audio_file_path = path
            base = os.path.basename(path)
            self.file_label.configure(text=base)
            self.append_transcript(f"\n[Imported file] {base}\n")

    def _set_controls(self, recording: bool):
        if recording:
            self.start_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal")
            self.continue_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.continue_btn.grid_remove()
            self.pause_btn.grid()
        else:
            self.start_btn.configure(state="normal")
            self.pause_btn.configure(state="disabled")
            self.continue_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            self.continue_btn.grid_remove()
            self.pause_btn.grid()

    def append_transcript(self, text: str):
        def _append():
            self.transcript.configure(state="normal")
            self.transcript.insert("end", text + " ")
            self.transcript.see("end")
            self.transcript.configure(state="disabled")
        self.after(0, _append)
