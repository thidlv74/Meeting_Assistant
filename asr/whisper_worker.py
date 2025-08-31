# ------------------------------
# file: meeting_assistant/asr/whisper_worker.py
# ------------------------------
"""Faster-Whisper integration wrapper.
Install: pip install faster-whisper
"""
from __future__ import annotations
from typing import Iterable, Tuple, List, Dict
from core.logger import logger

# --- add at top (before importing faster_whisper) ---
import os
# Cho phép chạy khi có 2 bản OpenMP (workaround). Lưu ý: Intel cảnh báo có thể không tối ưu,
# nhưng thực tế chạy ổn trong đa số case.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
# Giảm số luồng để tránh va chạm / CPU quá tải khi gọi CTranslate2
os.environ.setdefault("OMP_NUM_THREADS", "1")
# ----------------------------------------------------

try:
    from faster_whisper import WhisperModel
except Exception as e:
    WhisperModel = None  # type: ignore
    logger.warning("WhisperModel import failed: %s", e)

try:
    import torch
    _has_cuda = torch.cuda.is_available()
except Exception as e:
    _has_cuda = False
    logger.warning("Torch/CUDA check failed: %s", e)


class WhisperWorker:
    def __init__(self, model_size: str = "medium", language: str | None = None):
        logger.info("WhisperWorker.__init__ model=%s language=%s cuda=%s", model_size, language, _has_cuda)
        if WhisperModel is None:
            raise RuntimeError("Chưa cài faster-whisper. Chạy: pip install faster-whisper")
        device = "cuda" if _has_cuda else "cpu"
        compute_type = "float16" if _has_cuda else "int8"
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.language = language

    def transcribe_file(self, audio_path: str) -> Tuple[str, List[Dict]]:
        logger.info("WhisperWorker.transcribe_file -> %s", audio_path)
        segments, info = self.model.transcribe(audio_path, language=self.language)
        full_text = []
        seg_list: List[Dict] = []
        for seg in segments:
            text = seg.text.strip()
            full_text.append(text)
            seg_list.append({"start": seg.start, "end": seg.end, "text": text})
        logger.info("WhisperWorker.transcribe_file done, chars=%d segments=%d", len(" ".join(full_text)), len(seg_list))
        return " ".join(full_text), seg_list

    def transcribe_stream(self, chunks_iterable: Iterable[bytes]) -> str:
        logger.info("WhisperWorker.transcribe_stream called (not implemented)")
        raise NotImplementedError("Streaming ASR chưa được triển khai")