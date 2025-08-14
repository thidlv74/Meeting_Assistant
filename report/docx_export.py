# ------------------------------
# file: meeting_assistant/report/docx_export.py
# ------------------------------
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path

def export_meeting_report(docx_path: str, meta: dict, summary: str, extracted: dict):
    doc = Document()
    styles = doc.styles
    if "Normal" in styles:
        styles["Normal"].font.name = "Segoe UI"
        styles["Normal"].font.size = Pt(10)

    title = doc.add_paragraph(meta.get("title", "Meeting Report"))
    title.runs[0].font.size = Pt(18)
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.add_paragraph(f"Ngày giờ họp: {meta.get('datetime', '')}")

    doc.add_heading("Summary", level=1)
    doc.add_paragraph(summary or "Chưa xác định")

    doc.add_heading("Goal", level=1)
    for g in extracted.get("goal", []) or ["Chưa xác định"]:
        doc.add_paragraph(f"• {g}")

    doc.add_heading("Agenda", level=1)
    for a in extracted.get("agenda", []) or ["Chưa xác định"]:
        doc.add_paragraph(f"• {a}")

    doc.add_heading("Meeting Attendance", level=1)
    for att in extracted.get("attendance", []) or ["Chưa xác định"]:
        doc.add_paragraph(f"• {att}")

    doc.add_heading("Decisions", level=1)
    for d in extracted.get("decisions", []) or ["Chưa xác định"]:
        doc.add_paragraph(f"• {d}")

    doc.add_heading("Action Items", level=1)
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Action Item"
    hdr_cells[1].text = "Assigned To"
    hdr_cells[2].text = "Due Date"
    hdr_cells[3].text = "Completed"
    for it in extracted.get("action_items", []) or []:
        row = table.add_row().cells
        row[0].text = it.get("item", "")
        row[1].text = it.get("assignee", "")
        row[2].text = it.get("due", "")
        row[3].text = "✔" if it.get("done") else ""

    Path(docx_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(docx_path)