import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER

from schemas import StudentProfile

PRIMARY   = colors.HexColor("#1a237e")
SECONDARY = colors.HexColor("#283593")
LIGHT_BG  = colors.HexColor("#e8eaf6")
WHITE     = colors.white
GREY_TEXT = colors.HexColor("#546e7a")
BORDER    = colors.HexColor("#c5cae9")


def _fmt(value: object, fallback: str = "N/A") -> str:
    if value is None or str(value).strip() in ("", "None", "none"):
        return fallback
    return str(value)


def _fmt_date(value: object, fallback: str = "N/A") -> str:
    if not value:
        return fallback
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(value)


def generate_pdf(student: StudentProfile) -> str:
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf",
        prefix=f"student_{student.id}_",
    )
    pdf_path = tmp.name
    tmp.close()

    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()
    generated_on = datetime.now().strftime("%d %B %Y, %I:%M %p")

    #  Styles 
    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=22, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#c5cae9"), alignment=TA_CENTER)
    section_style = ParagraphStyle("Section", parent=styles["Normal"],
        fontSize=11, textColor=WHITE, fontName="Helvetica-Bold", leftIndent=6)
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
        fontSize=9, textColor=GREY_TEXT, fontName="Helvetica-Bold")
    value_style = ParagraphStyle("Value", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#1a1a2e"))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"],
        fontSize=8, textColor=GREY_TEXT, alignment=TA_CENTER)

    story = []

    #  Banner 
    banner = Table([
        [Paragraph("School Management System", title_style)],
        [Paragraph("Student Academic Report", subtitle_style)],
        [Paragraph(f"Generated on: {generated_on}", subtitle_style)],
    ], colWidths=[doc.width])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING",    (0, 0), (-1,  0), 18),
        ("BOTTOMPADDING", (0,-1), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story += [banner, Spacer(1, 0.4*cm)]

    #  Name badge 
    status_color = colors.HexColor("#2e7d32") if student.systemAccess else colors.HexColor("#c62828")
    status_text  = "Active" if student.systemAccess else "Inactive"

    badge = Table([[
        Paragraph(f"<b>{_fmt(student.name)}</b>", ParagraphStyle(
            "N", parent=styles["Normal"], fontSize=16,
            textColor=PRIMARY, fontName="Helvetica-Bold")),
        Paragraph(f"ID: #{student.id}", ParagraphStyle(
            "I", parent=styles["Normal"], fontSize=10, textColor=GREY_TEXT)),
        Paragraph(f"● {status_text}", ParagraphStyle(
            "S", parent=styles["Normal"], fontSize=10, textColor=status_color)),
    ]], colWidths=[doc.width*0.55, doc.width*0.25, doc.width*0.20])
    badge.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), ( 0, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story += [badge, Spacer(1, 0.5*cm)]

    #  Helpers 
    def sec_header(title: str) -> Table:
        t = Table([[Paragraph(title, section_style)]], colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), SECONDARY),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        return t

    def rows(pairs: list[tuple[str, str]]) -> list[Table]:
        result = []
        for i in range(0, len(pairs), 2):
            l, r = pairs[i], pairs[i+1] if i+1 < len(pairs) else ("", "")
            cl = Table([[Paragraph(l[0], label_style)], [Paragraph(l[1], value_style)]])
            cr = Table([[Paragraph(r[0], label_style)], [Paragraph(r[1], value_style)]])
            t = Table([[cl, cr]], colWidths=[doc.width/2]*2)
            t.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("LINEBELOW",     (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            result.append(t)
        return result

    #  Section 1 — Personal 
    story += [sec_header("1.  Personal Information"), Spacer(1, 0.1*cm)]
    story += rows([
        ("Full Name",      _fmt(student.name)),
        ("Email",          _fmt(student.email)),
        ("Date of Birth",  _fmt_date(student.dob)),
        ("Gender",         _fmt(student.gender)),
        ("Phone",          _fmt(student.phone)),
        ("Admission Date", _fmt_date(student.admissionDate)),
    ])

    #  Section 2 — Academic 
    story += [Spacer(1, 0.4*cm), sec_header("2.  Academic Information"), Spacer(1, 0.1*cm)]
    story += rows([
        ("Class",         _fmt(student.classe)),
        ("Section",       _fmt(student.section)),
        ("Roll Number",   _fmt(student.roll)),
        ("Class Teacher", _fmt(student.reporterName)),
    ])

    #  Section 3 — Family 
    story += [Spacer(1, 0.4*cm), sec_header("3.  Family Information"), Spacer(1, 0.1*cm)]
    story += rows([
        ("Father's Name",     _fmt(student.fatherName)),
        ("Father's Phone",    _fmt(student.fatherPhone)),
        ("Mother's Name",     _fmt(student.motherName)),
        ("Mother's Phone",    _fmt(student.motherPhone)),
        ("Guardian Name",     _fmt(student.guardianName)),
        ("Guardian Phone",    _fmt(student.guardianPhone)),
        ("Guardian Relation", _fmt(student.relationOfGuardian)),
        ("", ""),
    ])

    #  Section 4 — Address 
    story += [Spacer(1, 0.4*cm), sec_header("4.  Address Information"), Spacer(1, 0.1*cm)]
    story += rows([
        ("Current Address",   _fmt(student.currentAddress)),
        ("Permanent Address", _fmt(student.permanentAddress)),
    ])

    # Footer 
    story += [
        Spacer(1, 0.6*cm),
        HRFlowable(width="100%", thickness=1, color=BORDER),
        Spacer(1, 0.2*cm),
        Paragraph(
            f"Auto-generated by School Management System · {generated_on}",
            footer_style
        ),
    ]

    doc.build(story)
    return pdf_path