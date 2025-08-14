# ------------------------------
# file: meeting_assistant/audio/recorder.py
# ------------------------------
"""Minimal microphone recorder with optional sounddevice backend.

If sounddevice/soundfile are not installed, this acts as a no-op stub and
raises a clear error on .start().

Install:
  pip install sounddevice soundfile
"""
from __future__ import annotations
import threading
from typing import Optional
import os

try:
    import sounddevice as sd
    import soundfile as sf
except Exception:
    sd = None
    sf = None


class Recorder:
    def __init__(self, samplerate: int = 16000, channels: int = 1):
        self.samplerate = samplerate
        self.channels = channels
        self._stream: Optional[sd.InputStream] = None if sd else None
        self._file: Optional[sf.SoundFile] = None if sf else None
        self._paused = False
        self._lock = threading.Lock()
        self._path: Optional[str] = None

    def start(self, path: str):
        if sd is None or sf is None:
            raise RuntimeError("sounddevice/soundfile chưa được cài. Chạy: pip install sounddevice soundfile")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._path = path
        self._file = sf.SoundFile(path, mode='w', samplerate=self.samplerate, channels=self.channels, subtype='PCM_16')

        def callback(indata, frames, time, status):
            if status:
                # You may want to log status
                pass
            with self._lock:
                if not self._paused and self._file is not None:
                    self._file.write(indata.copy())

        self._stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=callback)
        self._stream.start()

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False

    def stop(self) -> str:
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if self._file is not None:
                self._file.flush()
                self._file.close()
                self._file = None
        return self._path or ""
