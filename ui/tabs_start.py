import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os, time, threading, uuid, wave
from dataclasses import dataclass
from datetime import datetime

from core.config import CONFIG
from core.logger import logger
from ui.styles import PANEL_BG, FG

from audio.recorder import Recorder
from asr.whisper_worker import WhisperWorker
from nlp.summarizer import Summarizer
from nlp.extractor import Extractor
from db.dao import upsert_session, insert_transcript


@dataclass
class StartState:
    recording: bool = False
    paused: bool = False
    start_ts: float = 0.0
    timer_job: str | None = None
    current_audio_path: str | None = None
    last_audio_path: str | None = None
    last_segments: list | None = None


class SaveDialog(tk.Toplevel):
    def __init__(self, master, default_title="Meeting", default_topic=""):
        super().__init__(master)
        self.title("Session Info")
        self.resizable(False, False)
        self.result = None

        frm = ttk.Frame(self, padding=16); frm.grid(row=0, column=0, sticky="nsew")
        ttk.Label(frm, text="Title").grid(row=0, column=0, sticky="w", pady=(0,6))
        self.e_title = ttk.Entry(frm, width=48); self.e_title.insert(0, default_title)
        self.e_title.grid(row=0, column=1, sticky="ew", pady=(0,6), padx=(10,0))
        ttk.Label(frm, text="Main Topic").grid(row=1, column=0, sticky="w", pady=(0,6))
        self.e_topic = ttk.Entry(frm, width=48); self.e_topic.insert(0, default_topic)
        self.e_topic.grid(row=1, column=1, sticky="ew", pady=(0,6), padx=(10,0))

        btns = ttk.Frame(frm); btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8,0))
        ttk.Button(btns, text="Cancel", command=self._cancel).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="OK", command=self._ok).grid(row=0, column=1)

        self.bind("<Return>", lambda e: self._ok()); self.bind("<Escape>", lambda e: self._cancel())
        self.grab_set(); self.e_title.focus_set(); self.wait_visibility(); self.transient(master)

    def _ok(self):
        self.result = {"title": self.e_title.get().strip(), "main_topic": self.e_topic.get().strip()}
        self.destroy()
    def _cancel(self):
        self.result = None
        self.destroy()


class StartTab(ttk.Frame):
    """Start New Meeting (no waveform).
    - Start/Pause/Continue/Stop + timer
    - Add Recording → ASR → Transcript editable
    - Save Meeting → GPT summarize & extract → save sessions + transcripts
    """
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.state = StartState()
        self.recorder: Recorder | None = None
        self.worker = WhisperWorker(CONFIG.asr_model, language="vi")
        self._build()

    def _build(self):
        controls = ttk.Frame(self, style="Panel.TFrame", padding=14)
        controls.grid(row=0, column=0, sticky="ew")
        for c in range(0, 9): controls.grid_columnconfigure(c, minsize=10)
        controls.grid_columnconfigure(6, weight=1)

        self.btn_start = ttk.Button(controls, text="▶ Start", command=self.on_start)
        self.btn_pause = ttk.Button(controls, text="⏸ Pause", command=self.on_pause, state="disabled")
        self.btn_cont  = ttk.Button(controls, text="▶ Continue", command=self.on_continue, state="disabled")
        self.btn_stop  = ttk.Button(controls, text="⏹ Stop", command=self.on_stop, state="disabled")
        self.timer_lbl = ttk.Label(controls, text="00:00:00", style="Heading.TLabel")
        self.btn_upload= ttk.Button(controls, text="📂 Add Recording", command=self.on_upload)
        self.file_lbl  = ttk.Label(controls, text="No file", style="Muted.TLabel")

        self.btn_start.grid(row=0, column=0, padx=(0,6))
        self.btn_pause.grid(row=0, column=1, padx=6)
        self.btn_cont.grid(row=0, column=1, padx=6); self.btn_cont.grid_remove()
        self.btn_stop.grid(row=0, column=3, padx=6)
        ttk.Separator(controls, orient="vertical").grid(row=0, column=4, padx=10, sticky="ns")
        self.timer_lbl.grid(row=0, column=5, padx=(0,12))
        self.btn_upload.grid(row=0, column=7, padx=(0,8))
        self.file_lbl.grid(row=0, column=8)

        body = ttk.Frame(self); body.grid(row=1, column=0, sticky="nsew", pady=(12,0))
        self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(0, weight=1)
        card = ttk.Frame(body, style="Panel.TFrame", padding=14); card.grid(row=0, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1); body.grid_columnconfigure(0, weight=1)

        ttk.Label(card, text="🗣 Transcript (live)", style="CardTitle.TLabel").pack(anchor="w")
        self.txt = scrolledtext.ScrolledText(card, height=18, bg=PANEL_BG, fg=FG,
                                             insertbackground=FG, bd=0, relief="flat", padx=8, pady=8,
                                             wrap="word")
        self.txt.pack(fill="both", expand=True, pady=(8,0))
        self.txt.configure(state="normal")

        save_bar = ttk.Frame(self); save_bar.grid(row=2, column=0, sticky="ew", pady=(8,0))
        self.btn_save = ttk.Button(save_bar, text="💾 Save Meeting", command=self.on_save_meeting)
        self.btn_save.pack(anchor="e")

        self.status = ttk.Label(self, text="Ready", style="Muted.TLabel"); self.status.grid(row=3, column=0, sticky="w", pady=(8,0))

    # ---------- Timer ----------
    def _tick(self):
        if not self.state.recording: return
        elapsed = int(time.time() - self.state.start_ts)
        h, m, s = elapsed//3600, (elapsed%3600)//60, elapsed%60
        self.timer_lbl.configure(text=f"{h:02}:{m:02}:{s:02}")
        self.state.timer_job = self.after(500, self._tick)

    # ---------- Handlers ----------
    def on_start(self):
        try:
            self.state.recording=True; self.state.paused=False; self.state.start_ts=time.time(); self._tick()
            os.makedirs(CONFIG.base_dir, exist_ok=True)
            outfile = os.path.join(CONFIG.base_dir, f"record_{int(self.state.start_ts)}.wav")
            self.recorder = Recorder(); self.recorder.start(outfile)
            self.state.current_audio_path=None
            self.btn_start.configure(state="disabled"); self.btn_pause.configure(state="normal")
            self.btn_cont.configure(state="disabled"); self.btn_stop.configure(state="normal")
            self.btn_cont.grid_remove(); self.btn_pause.grid()
            self.status.configure(text="Recording...")
        except Exception as e:
            self.status.configure(text=f"Recorder error: {e}")
            self.state.recording=False
            if self.state.timer_job:
                try: self.after_cancel(self.state.timer_job)
                except Exception: pass
                self.state.timer_job=None
            self.timer_lbl.configure(text="00:00:00")

    def on_pause(self):
        if not self.recorder: return
        try:
            self.recorder.pause(); self.state.paused=True
            self.btn_pause.grid_remove(); self.btn_cont.configure(state="normal"); self.btn_cont.grid()
            self.status.configure(text="Paused")
        except Exception as e:
            self.status.configure(text=f"Pause error: {e}")

    def on_continue(self):
        if not self.recorder: return
        try:
            self.recorder.resume(); self.state.paused=False
            self.btn_cont.grid_remove(); self.btn_pause.configure(state="normal"); self.btn_pause.grid()
            self.status.configure(text="Recording...")
        except Exception as e:
            self.status.configure(text=f"Resume error: {e}")

    def on_stop(self):
        self.state.recording=False
        if self.state.timer_job:
            try: self.after_cancel(self.state.timer_job)
            except Exception: pass
            self.state.timer_job=None
        rec_path=None
        if self.recorder:
            try: rec_path=self.recorder.stop()
            except Exception as e: self.status.configure(text=f"Stop error: {e}")
            finally: self.recorder=None
        self.btn_start.configure(state="normal"); self.btn_pause.configure(state="disabled")
        self.btn_cont.configure(state="disabled"); self.btn_stop.configure(state="disabled")
        self.btn_cont.grid_remove(); self.btn_pause.grid()
        audio_path = rec_path or self.state.current_audio_path
        if not audio_path:
            self.status.configure(text="No audio to process"); return
        self._run_asr_async(audio_path)

    def on_upload(self):
        path = filedialog.askopenfilename(title="Chọn file ghi âm",
            filetypes=[("Audio","*.wav *.mp3 *.m4a *.flac"),("All","*.*")])
        if not path: return
        self.state.current_audio_path = path
        self.file_lbl.configure(text=os.path.basename(path))
        self._run_asr_async(path)

    # ---------- ASR ----------
    def _run_asr_async(self, audio_path: str):
        self.status.configure(text="ASR running...")
        self.txt.delete("1.0","end"); self.txt.insert("end", f"[Đang nhận dạng: {os.path.basename(audio_path)}]\n")
        def task():
            try:
                full_text, segments = self.worker.transcribe_file(audio_path)
                return (full_text, segments, None)
            except Exception as e:
                return (None, None, str(e))
        def done(res):
            full_text, segments, err = res
            if err:
                self.status.configure(text=f"ASR error: {err}"); return
            self.txt.delete("1.0","end"); self.txt.insert("end", full_text or "")
            self.state.last_audio_path = audio_path; self.state.last_segments = segments or []
            self.status.configure(text="ASR done")
        threading.Thread(target=lambda: self._thread(task, done), daemon=True).start()

    def _thread(self, task, cb):
        res = task(); self.after(0, lambda: cb(res))

    # ---------- Duration helpers ----------
    def _probe_duration_minutes(self, path: str) -> int:
        """Get duration (minutes, rounded) from audio file.
        Prefer mutagen (mp3/m4a/flac), fallback to soundfile/wave."""
        # 1) mutagen (mp3/m4a/flac/…)
        try:
            from mutagen import File as MFile  # pip install mutagen
            mf = MFile(path)
            length = getattr(getattr(mf, "info", None), "length", None)
            if length:
                return int(round(float(length) / 60.0))
        except Exception as e:
            logger.debug("mutagen probe failed: %s", e)

        # 2) soundfile (wav/flac/ogg…)
        try:
            import soundfile as sf
            with sf.SoundFile(path) as f:
                seconds = len(f) / float(f.samplerate)
                return int(round(seconds / 60.0))
        except Exception as e:
            logger.debug("soundfile probe failed: %s", e)

        # 3) wave (wav only)
        try:
            with wave.open(path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                seconds = frames / float(rate)
                return int(round(seconds / 60.0))
        except Exception as e:
            logger.debug("wave probe failed: %s", e)

        # Fallback to 0
        return 0

    # ---------- SAVE (GPT + DB) ----------
    def on_save_meeting(self):
        full_text = self.txt.get("1.0","end").strip()
        if not full_text:
            self.status.configure(text="No content to save"); return

        dlg = SaveDialog(self, "Meeting", "")
        self.wait_window(dlg)
        if dlg.result is None:
            self.status.configure(text="Save canceled"); return
        title = dlg.result.get("title","").strip()
        main_topic = dlg.result.get("main_topic","").strip()

        start_dt = datetime.fromtimestamp(self.state.start_ts) if self.state.start_ts else datetime.now()
        end_dt = datetime.now()
        # LẤY DURATION THEO FILE AUDIO (ưu tiên file, fallback đồng hồ)
        audio_path = self.state.last_audio_path or self.state.current_audio_path or ""
        if audio_path and os.path.exists(audio_path):
            duration_min = self._probe_duration_minutes(audio_path)
        else:
            duration_min = int((end_dt - start_dt).total_seconds() // 60)

        session_uuid = str(uuid.uuid4())
        self.status.configure(text="Analyzing with GPT and saving...")

        def task():
            try:
                summary = Summarizer().summarize(full_text)
                extracted = Extractor().extract_fields(full_text)
                from db.dao import upsert_session, insert_transcript
                upsert_session(
                    uuid=session_uuid, title=title, main_topic=main_topic,
                    start_time=start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    end_time=end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    duration_min=duration_min, status="completed",
                    audio_path=audio_path,
                )
                insert_transcript(session_uuid, full_text, summary, extracted)
                return (session_uuid, None)
            except Exception as e:
                return (None, str(e))

        def done(res):
            sid, err = res
            if err: self.status.configure(text=f"Save failed: {err}")
            else:   self.status.configure(text=f"Saved session {sid}")
        threading.Thread(target=lambda: self._thread(task, done), daemon=True).start()
