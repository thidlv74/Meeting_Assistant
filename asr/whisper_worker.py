# ------------------------------
# file: meeting_assistant/asr/whisper_worker.py
# ------------------------------
"""Faster-Whisper integration wrapper.
Install: pip install faster-whisper
"""
from __future__ import annotations
from typing import Iterable, Tuple, List, Dict

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None  # type: ignore

try:
    import torch
    _has_cuda = torch.cuda.is_available()
except Exception:
    _has_cuda = False