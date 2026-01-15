#!/usr/bin/env python3
"""
Generate DOCX from CV data with similar layout to PDF
"""

from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

# Paths
ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
ENGAGEMENTS_DIR = CONTENT_DIR / "engagements"
PERSONAL_DATA_FILE = CONTENT_DIR / "personal-data.txt"
PERSONAL_TEXT_FILE = CONTENT_DIR / "personal-text.txt"
URLS_FILE = CONTENT_DIR / "urls-contact.txt"
EDUCATION_FILE = CONTENT_DIR / "educations.txt"
COURSES_FILE = CONTENT_DIR / "courses.txt"
COURSES_SHORT_FILE = CONTENT_DIR / "courses-short.txt"
CERTIFICATIONS_FILE = CONTENT_DIR / "certifications.txt"
BLOCKS_CONFIG = CONTENT_DIR / "blocks.txt"
PROFILE_PHOTO = ROOT / "content" / "pictures" / "profile-photo.jpg"
OUTPUT_FILE = ROOT / "docs" / "cv.docx"

# Colors
GREY_TEXT = RGBColor(99, 110, 114)  # #636e72
GREY_LIGHT = RGBColor(178, 190, 195)  # #b2bec3

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

def parse_file_with_delimiter(path: Path, skip_header=True):
    """Parse pipe-delimited file"""
    if not path.is_file():
        return []
    lines = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        if skip_header and '`' in line and '|' in line:
            continue
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            lines.append(parts)
    return lines

def parse_engagement_file(path: Path):
    """Parse engagement text file"""
    txt = path.read_text(encoding='utf-8')
    lines = [l.rstrip() for l in txt.splitlines()]
    data = {}
    cur = None
    buf = []
    
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
            
        if '|' in s:
            parts = s.split('|', 1)
            key = parts[0].strip().strip('`').strip("'").strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            if cur:
                data[cur] = '\n'.join(buf).strip()
            
            cur = key
            buf = [value] if value else []
        elif s.startswith('•') or (cur and '|' not in s):
            if cur:
                buf.append(ln)
    
    if cur:
        data[cur] = '\n'.join(buf).strip()
    
    period = path.name.replace("opdracht_", "").replace(".txt", "").replace("_", " – ")
    if "period" not in data and "periode" not in data and "PERIODE" not in data:
        data["periode"] = period
    
    return data

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
    personal_data = parse_file_with_delimiter(PERSONAL_DATA_FILE)
    
    add_section_title(doc, 'PERSOONLIJKE GEGEVENS')
    
    if personal_data:
        table = doc.add_table(rows=len(personal_data), cols=2)
        table.style = 'Table Grid'
        table.autofit = False
        table.allow_autofit = False
        
        for idx, parts in enumerate(personal_data):
            row = table.rows[idx]
            label_cell = row.cells[0]
            value_cell = row.cells[1]
            
            # Remove borders
            set_cell_border(label_cell, top=True, left=True, bottom=True, right=True)
            set_cell_border(value_cell, top=True, left=True, bottom=True, right=True)
            
            # Label (grey, bold)
            label = parts[0] if len(parts) > 0 else ""
            p = label_cell.paragraphs[0]
            run = p.add_run(label)
            run.font.color.rgb = GREY_TEXT
            run.font.bold = True
            run.font.size = Pt(11)
            
            # Value
            value = parts[1] if len(parts) > 1 else ""
            value_cell.text = value
            value_cell.paragraphs[0].runs[0].font.size = Pt(11)
    
    add_horizontal_line(doc)
    
    # Personal Text
    if PERSONAL_TEXT_FILE.is_file():
        text = PERSONAL_TEXT_FILE.read_text(encoding='utf-8')
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                p = doc.add_paragraph()
                add_text_with_breaks(p, para.strip())
                p.paragraph_format.space_after = Pt(6)
    
    add_horizontal_line(doc)
    
    # Education
    add_section_title(doc, 'OPLEIDINGEN')
    educations = parse_file_with_delimiter(EDUCATION_FILE)
    
    for parts in educations:
        period = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        institute = parts[2] if len(parts) > 2 else ""
        place = parts[3] if len(parts) > 3 else ""
        
        p = doc.add_paragraph()
        # Period (grey)
        run = p.add_run(f"{period}  ")
        run.font.color.rgb = GREY_TEXT
        run.font.size = Pt(11)
        # Name and institute
        run = p.add_run(f"{name}")
        if institute:
            run = p.add_run(f" — {institute}")
        if place:
            run = p.add_run(f", {place}")
        p.paragraph_format.space_after = Pt(3)
    
    add_horizontal_line(doc)
    
    # Certifications
    add_section_title(doc, 'CERTIFICERINGEN')
    certifications = parse_file_with_delimiter(CERTIFICATIONS_FILE)
    
    for parts in certifications:
        period = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        org = parts[2] if len(parts) > 2 else ""
        
        p = doc.add_paragraph()
        run = p.add_run(f"{period}  ")
        run.font.color.rgb = GREY_TEXT
        run = p.add_run(f"{name}")
        if org:
            run = p.add_run(f" — {org}")
        p.paragraph_format.space_after = Pt(3)
    
    add_horizontal_line(doc)
    
    # Courses
    add_section_title(doc, 'CURSUSSEN')
    courses = parse_file_with_delimiter(COURSES_FILE)
    
    # Group by period
    periods = {}
    for parts in courses:
        period = parts[0] if len(parts) > 0 else ""
        items = parts[1:] if len(parts) > 1 else []
        if period not in periods:
            periods[period] = []
        periods[period].extend(items)
    
    for period, items in periods.items():
        p = doc.add_paragraph()
        run = p.add_run(f"{period}  ")
        run.font.color.rgb = GREY_TEXT
        run = p.add_run(", ".join(items))
        p.paragraph_format.space_after = Pt(3)
    
    add_horizontal_line(doc)
    
    # Werkervaring (Engagements)
    add_section_title(doc, 'WERKERVARING')
    
    if ENGAGEMENTS_DIR.is_dir():
        engagement_files = sorted(ENGAGEMENTS_DIR.iterdir(), key=lambda p: p.name, reverse=True)
        
        for eng_file in engagement_files:
            if not eng_file.is_file() or eng_file.suffix.lower() != ".txt":
                continue
            
            data = parse_engagement_file(eng_file)
            
            # Get data with case-insensitive lookup
            def get_field(variants):
                for v in variants:
                    for key, value in data.items():
                        if key.lower() == v.lower():
                            return value
                return ""
            
            periode = get_field(["periode", "PERIODE", "period"])
            organisatie = get_field(["organisatie", "ORGANISATIE", "organisatie_naam", "organization", "organization_name"])
            functie = get_field(["functie", "FUNCTIE", "job", "job_title"])
            werkzaamheden = get_field(["werkzaamheden", "WERKZAAMHEDEN", "work", "text_block_work"])
            prestaties = get_field(["belangrijkste prestaties", "BELANGRIJKSTE PRESTATIES", "prestaties", "achievements"])
            trefwoorden = get_field(["trefwoorden", "TREFWOORDEN", "keywords"])
            
            # Summary line
            p = doc.add_paragraph()
            if periode:
                run = p.add_run(f"{periode}  ")
                run.font.color.rgb = GREY_TEXT
            if organisatie:
                run = p.add_run(f"{organisatie}")
            if functie:
                run = p.add_run(f" — {functie}")
            p.paragraph_format.space_after = Pt(6)
            
            # Details
            if werkzaamheden:
                p = doc.add_paragraph()
                run = p.add_run("Werkzaamheden")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                
                p = doc.add_paragraph()
                add_text_with_breaks(p, werkzaamheden)
                p.paragraph_format.space_after = Pt(6)
            
            if prestaties:
                p = doc.add_paragraph()
                run = p.add_run("Belangrijkste prestaties")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                
                p = doc.add_paragraph()
                add_text_with_breaks(p, prestaties)
                p.paragraph_format.space_after = Pt(6)
            
            if trefwoorden:
                p = doc.add_paragraph()
                run = p.add_run("Trefwoorden")
                run.font.color.rgb = GREY_TEXT
                run.font.bold = True
                run.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                
                p = doc.add_paragraph()
                add_text_with_breaks(p, trefwoorden)
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
