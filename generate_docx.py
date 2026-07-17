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
from bs4 import BeautifulSoup

# Paths - source is the MkDocs Markdown/HTML fragments, not the retired content/*.txt DSL
ROOT = Path(__file__).resolve().parent
INCLUDES_DIR = ROOT / "docs" / "includes"
ENGAGEMENTS_DIR = INCLUDES_DIR / "engagements"
PERSONAL_DATA_FILE = INCLUDES_DIR / "personal-data.md"
PERSONAL_TEXT_FILE = INCLUDES_DIR / "personal-text.md"
EDUCATION_FILE = INCLUDES_DIR / "educations.md"
COURSES_FILE = INCLUDES_DIR / "courses.md"
CERTIFICATIONS_FILE = INCLUDES_DIR / "certifications.md"
OUTPUT_FILE = ROOT / "docs" / "assets" / "cv.docx"

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

def tekstblok_text(tag):
    """Convert a <div class='tekstblok'> fragment back to plain text: bullets
    become '• ' lines, <br> becomes a line break, paragraphs are separated by
    a blank line - the inverse of generate_site.py's format_value_for_html().
    """
    if tag is None:
        return ""
    for br in tag.find_all('br'):
        br.replace_with('\n')
    children = tag.find_all(['p', 'ul'], recursive=False)
    if not children:
        # No <p>/<ul> wrapping (e.g. courses.md is plain linkified text) - use the raw text.
        return tag.get_text().strip()
    blocks = []
    for child in children:
        if child.name == 'ul':
            items = ['• ' + li.get_text().strip() for li in child.find_all('li', recursive=False)]
            blocks.append('\n'.join(items))
        else:
            blocks.append(child.get_text().strip())
    return '\n\n'.join(b for b in blocks if b)

def parse_personal_data(path: Path):
    """Parse docs/includes/personal-data.md (a <table class='personal-table'> fragment)"""
    if not path.is_file():
        return []
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    rows = []
    for tr in soup.select('table.personal-table tr'):
        label_td = tr.find('td', class_='label')
        value_td = tr.find('td', class_='value')
        if not label_td or not value_td:
            continue
        label = label_td.get_text(strip=True)
        value = tekstblok_text(value_td.find('div', class_='tekstblok'))
        rows.append([label, value])
    return rows

def parse_personal_text(path: Path):
    """Parse docs/includes/personal-text.md (a <div class='tekstblok'> fragment)"""
    if not path.is_file():
        return ""
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    return tekstblok_text(soup.find('div', class_='tekstblok'))

def parse_education_table(path: Path):
    """Parse docs/includes/educations.md or certifications.md (a <table class='education-table'>
    fragment). Name/institute are already merged with an em dash by the conversion step, so this
    returns [period, name(+institute), "", place] - the empty institute slot keeps the existing
    render loop below unchanged.
    """
    if not path.is_file():
        return []
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    rows = []
    for tr in soup.select('table.education-table tr'):
        label_td = tr.find('td', class_='label')
        if not label_td:
            continue
        period = label_td.get_text(strip=True)
        if not period:
            continue  # description continuation row, not used by the DOCX output
        tds = tr.find_all('td')
        name_td = tds[1] if len(tds) > 1 else None
        place_td = tr.find('td', class_='edu-place')
        name = name_td.get_text(strip=True) if name_td else ""
        place = place_td.get_text(strip=True) if place_td else ""
        rows.append([period, name, "", place])
    return rows

def parse_courses(path: Path):
    """Parse docs/includes/courses.md (one <table class='education-table'> per period,
    already pre-grouped by the conversion step)."""
    if not path.is_file():
        return []
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    result = []
    for table in soup.find_all('table', class_='education-table'):
        tr = table.find('tr')
        if not tr:
            continue
        label_td = tr.find('td', class_='label')
        period = label_td.get_text(strip=True) if label_td else ""
        tds = tr.find_all('td')
        value_td = tds[-1] if tds else None
        items_text = tekstblok_text(value_td.find('div', class_='tekstblok')) if value_td else ""
        result.append((period, items_text))
    return result

def parse_engagement_md(path: Path):
    """Parse a docs/includes/engagements/opdracht_*.md fragment (an .engagement-item div)"""
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    periode_span = soup.find('span', class_='engagement-period')
    org_span = soup.find('span', class_='engagement-org')
    role_span = soup.find('span', class_='engagement-role')
    periode = periode_span.get_text(strip=True) if periode_span else ""
    organisatie = org_span.get_text(strip=True) if org_span else ""
    functie = role_span.get_text(strip=True) if role_span else ""

    werkzaamheden = prestaties = trefwoorden = ""
    for item in soup.find_all('div', class_='engagement-detail-item'):
        label_div = item.find('div', class_='detail-label')
        label_text = label_div.get_text(strip=True) if label_div else ""
        value = tekstblok_text(item.find('div', class_='tekstblok'))
        if label_text == 'Werkzaamheden':
            werkzaamheden = value
        elif label_text == 'Belangrijkste prestaties':
            prestaties = value
        elif label_text == 'Trefwoorden':
            trefwoorden = value
    return periode, organisatie, functie, werkzaamheden, prestaties, trefwoorden

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
    personal_data = parse_personal_data(PERSONAL_DATA_FILE)
    
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
    text = parse_personal_text(PERSONAL_TEXT_FILE)
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
    educations = parse_education_table(EDUCATION_FILE)
    
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
    certifications = parse_education_table(CERTIFICATIONS_FILE)
    
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
    courses = parse_courses(COURSES_FILE)

    for period, items_text in courses:
        p = doc.add_paragraph()
        run = p.add_run(f"{period}  ")
        run.font.color.rgb = GREY_TEXT
        run = p.add_run(items_text)
        p.paragraph_format.space_after = Pt(3)
    
    add_horizontal_line(doc)
    
    # Werkervaring (Engagements)
    add_section_title(doc, 'WERKERVARING')
    
    if ENGAGEMENTS_DIR.is_dir():
        engagement_files = sorted(ENGAGEMENTS_DIR.iterdir(), key=lambda p: p.name, reverse=True)

        for eng_file in engagement_files:
            if not eng_file.is_file() or eng_file.suffix.lower() != ".md":
                continue

            periode, organisatie, functie, werkzaamheden, prestaties, trefwoorden = parse_engagement_md(eng_file)

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
