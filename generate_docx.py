#!/usr/bin/env python3
"""
Generate DOCX from CV data with similar layout to PDF.

Reads directly from docs/data/**/*.yml (plain content, no HTML/CSS
round-tripping) - the same source of truth the MkDocs site itself is
built from via main.py's macros.
"""

from pathlib import Path
import yaml
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Paths
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "docs" / "data"
ENGAGEMENTS_DIR = DATA_DIR / "engagements"
OUTPUT_FILE = ROOT / "docs" / "assets" / "cv.docx"

# Colors
GREY_TEXT = RGBColor(99, 110, 114)  # #636e72
GREY_LIGHT = RGBColor(178, 190, 195)  # #b2bec3

def load_yaml(name):
    path = DATA_DIR / name
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding='utf-8'))

def md_bullets_to_docx_text(text):
    """Normalize migrated content ('- ' Markdown bullets, trailing hard-break
    spaces) into the plain '• '-bulleted, line-broken text add_text_with_breaks()
    expects - the same bullet character the site/PDF renders via the |markdown
    Jinja filter turning '- ' into <li>, here turned into '• ' directly."""
    if not text:
        return ""
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("- "):
            line = "• " + line[2:]
        lines.append(line)
    return "\n".join(lines)

def add_horizontal_line(doc):
    """Add a horizontal line separator"""
    p = doc.add_paragraph()
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'B2BEC3')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def set_cell_border(cell, **kwargs):
    """Set cell borders"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        if edge in kwargs:
            border = OxmlElement(f'w:{edge}')
            border.set(qn('w:val'), 'none')
            tcBorders.append(border)
    tcPr.append(tcBorders)

def add_section_title(doc, title):
    """Add section title (grey, uppercase, bold)"""
    p = doc.add_paragraph()
    p.add_run(title.upper()).font.color.rgb = GREY_TEXT
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(11)
    p.space_after = Pt(6)
    return p

def add_text_with_breaks(paragraph, text):
    """Add text with line breaks preserved"""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            paragraph.add_run(line.strip())
            if i < len(lines) - 1:
                paragraph.add_run('\n')

def generate_docx():
    """Generate Word document"""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Segoe UI'
    font.size = Pt(11)

    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

    # Personal Data
    personal = load_yaml("personal-data.yml") or {}
    fields = personal.get("fields", [])

    add_section_title(doc, 'PERSOONLIJKE GEGEVENS')

    if fields:
        table = doc.add_table(rows=len(fields), cols=2)
        table.style = 'Table Grid'
        table.autofit = False
        table.allow_autofit = False

        for idx, f in enumerate(fields):
            row = table.rows[idx]
            label_cell = row.cells[0]
            value_cell = row.cells[1]

            set_cell_border(label_cell, top=True, left=True, bottom=True, right=True)
            set_cell_border(value_cell, top=True, left=True, bottom=True, right=True)

            p = label_cell.paragraphs[0]
            run = p.add_run(f.get("label", ""))
            run.font.color.rgb = GREY_TEXT
            run.font.bold = True
            run.font.size = Pt(11)

            value_cell.text = f.get("value", "")
            value_cell.paragraphs[0].runs[0].font.size = Pt(11)

    add_horizontal_line(doc)

    # Personal Text
    personal_text_file = DATA_DIR / "personal-text.md"
    text = personal_text_file.read_text(encoding='utf-8') if personal_text_file.is_file() else ""
    if text:
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = doc.add_paragraph()
                add_text_with_breaks(p, para.strip())
                p.paragraph_format.space_after = Pt(6)

    add_horizontal_line(doc)

    # Education
    add_section_title(doc, 'OPLEIDINGEN')
    educations = load_yaml("educations.yml") or []

    for row in educations:
        p = doc.add_paragraph()
        run = p.add_run(f"{row.get('period', '')}  ")
        run.font.color.rgb = GREY_TEXT
        run.font.size = Pt(11)
        run = p.add_run(row.get("name", ""))
        if row.get("institute"):
            run = p.add_run(f" — {row['institute']}")
        if row.get("place"):
            run = p.add_run(f", {row['place']}")
        p.paragraph_format.space_after = Pt(3)

    add_horizontal_line(doc)

    # Certifications
    add_section_title(doc, 'CERTIFICERINGEN')
    certifications = load_yaml("certifications.yml") or []

    for row in certifications:
        p = doc.add_paragraph()
        run = p.add_run(f"{row.get('period', '')}  ")
        run.font.color.rgb = GREY_TEXT
        run = p.add_run(row.get("name", ""))
        if row.get("institute"):
            run = p.add_run(f" — {row['institute']}")
        p.paragraph_format.space_after = Pt(3)

    add_horizontal_line(doc)

    # Courses
    add_section_title(doc, 'CURSUSSEN')
    courses = load_yaml("courses.yml") or []

    for group in courses:
        p = doc.add_paragraph()
        run = p.add_run(f"{group.get('period', '')}  ")
        run.font.color.rgb = GREY_TEXT
        run = p.add_run(group.get("items_text", ""))
        p.paragraph_format.space_after = Pt(3)

    add_horizontal_line(doc)

    # Werkervaring (Engagements)
    add_section_title(doc, 'WERKERVARING')

    if ENGAGEMENTS_DIR.is_dir():
        engagement_files = sorted(
            ENGAGEMENTS_DIR.glob("*.yml"),
            key=lambda p: yaml.safe_load(p.read_text(encoding='utf-8'))["order"],
            reverse=True,
        )

        for eng_file in engagement_files:
            eng = yaml.safe_load(eng_file.read_text(encoding='utf-8'))

            # Summary line
            p = doc.add_paragraph()
            if eng.get("period"):
                run = p.add_run(f"{eng['period']}  ")
                run.font.color.rgb = GREY_TEXT
            if eng.get("organisation"):
                run = p.add_run(eng["organisation"])
            if eng.get("role"):
                run = p.add_run(f" — {eng['role']}")
            p.paragraph_format.space_after = Pt(6)

            # Details
            if eng.get("activities"):
                p = doc.add_paragraph()
                run = p.add_run("Werkzaamheden")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)

                p = doc.add_paragraph()
                add_text_with_breaks(p, md_bullets_to_docx_text(eng["activities"]))
                p.paragraph_format.space_after = Pt(6)

            if eng.get("achievements"):
                p = doc.add_paragraph()
                run = p.add_run("Belangrijkste prestaties")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)

                p = doc.add_paragraph()
                add_text_with_breaks(p, md_bullets_to_docx_text(eng["achievements"]))
                p.paragraph_format.space_after = Pt(6)

            if eng.get("keywords"):
                p = doc.add_paragraph()
                run = p.add_run("Trefwoorden")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)

                p = doc.add_paragraph()
                add_text_with_breaks(p, eng["keywords"])
                p.paragraph_format.space_after = Pt(6)

            # Separator between engagements
            add_horizontal_line(doc)

    # Save document
    doc.save(OUTPUT_FILE)
    print(f"✓ Word document generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        generate_docx()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
