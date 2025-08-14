# ------------------------------
# file: meeting_assistant/report/srt_export.py
# ------------------------------
from pathlib import Path

def export_srt(srt_path: str, segments: list[dict]):
    """segments: [{"start": float, "end": float, "text": str}]"""
    lines = []
    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    for i, seg in enumerate(segments, start=1):
        lines.append(str(i))
        lines.append(f"{fmt(seg['start'])} --> {fmt(seg['end'])}")
        lines.append(seg['text'])
        lines.append("")
    Path(srt_path).parent.mkdir(parents=True, exist_ok=True)
    Path(srt_path).write_text(".join(lines)", encoding="utf-8")