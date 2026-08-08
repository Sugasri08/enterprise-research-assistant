"""
Report export — TXT and PDF, both using free libraries only
(fpdf2 ships with reportlab-free PDF generation).
"""
import io
from agents.schemas import Report


def to_txt_bytes(report: Report) -> bytes:
    return report.to_markdown().encode("utf-8")


def to_pdf_bytes(report: Report) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def heading(text, size=14):
        pdf.set_font("Helvetica", "B", size)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def body(text, size=11):
        pdf.set_font("Helvetica", "", size)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def bullets(items):
        pdf.set_font("Helvetica", "", 11)
        for item in items or ["None noted"]:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, f"- {item}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    heading(report.title, 16)
    heading("Executive Summary")
    body(report.executive_summary)
    heading("Key Findings")
    bullets(report.key_findings)
    heading("Strengths")
    bullets(report.strengths)
    heading("Weaknesses")
    bullets(report.weaknesses)
    heading("Future Opportunities")
    bullets(report.future_opportunities)
    heading("Conclusion")
    body(report.conclusion)
    heading("References")
    bullets(report.references)

    return bytes(pdf.output())
