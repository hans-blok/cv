# TEST123
import os
import re
import html
import base64
from pathlib import Path
from datetime import datetime

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
BLOCKS_DIR = CONTENT_DIR / "blocks"
BLOCKS_CONFIG = CONTENT_DIR / "blocks.txt"
FUNCTIONAL_DM = ROOT / "specs" / "functional_dm.md"
CSS_PATH = Path("static") / "style.css"
OUTPUT_FILE = ROOT / "cv.html"

LOGO_CANDIDATES = ["content/pictures/logo-header.png", "content/pictures/logo-header.jpg", "content/pictures/logo.png", "content/pictures/logo.jpg"]
PROFILE_CANDIDATES = ["content/pictures/profile-photo.jpg", "content/pictures/profile-photo.png", "content/pictures/profile.jpg", "content/pictures/profile.png"]
LOGO_DIRS = ["pictures", "logos", "logo", "images", "static/images"]

_URL_RE = re.compile(r"(https?://[^\s<>]+|www\.[^\s<>]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")

PREFERRED_CASING = {
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "website": "Website",
    "name": "Naam",
    "usual_name": "Roepnaam",
    "place_of_residence": "Woonplaats",
    "date_of_birth": "Geboortedatum",
    "available": "Beschikbaar",
    "job_title": "Functie",
    "telefoon": "Telefoon",
    "beschikbaar per": "Beschikbaar per"
}

PRETTY_KEYS = {
    "PERIODE": "Periode",
    "ORGANISATIE": "Organisatie",
    "FUNCTIE": "Functie",
    "WERKZAAMHEDEN": "Werkzaamheden",
    "BELANGRIJKSTE PRESTATIES": "Belangrijkste prestaties",
    "TREFWOORDEN": "Trefwoorden"
}

def norm(p: str) -> str:
    return p.replace("\\", "/")

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 data URI"""
    if not image_path:
        return ""
    
    path = Path(image_path)
    if not path.is_file():
        return ""
    
    # Determine MIME type from extension
    ext = path.suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    # Read and encode image
    with open(path, 'rb') as f:
        img_data = f.read()
    b64_data = base64.b64encode(img_data).decode('utf-8')
    
    return f"data:{mime_type};base64,{b64_data}"

def find_first(cands):
    for c in cands:
        p = ROOT / c
        if p.is_file():
            return norm(str(p))
    for d in LOGO_DIRS:
        dd = ROOT / d
        if dd.is_dir():
            for f in sorted(dd.iterdir()):
                if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                    nm = f.name.lower()
                    if any(k in nm for k in ("logo","profile","foto","portrait")):
                        return norm(str(f))
    return ""

def linkify(text: str) -> str:
    if not text:
        return ""
    parts, last = [], 0
    for m in _URL_RE.finditer(text):
        s, e = m.span()
        parts.append(html.escape(text[last:s]))
        match = m.group(0)
        if "@" in match and not match.startswith("http"):
            href = "mailto:" + match
        else:
            href = match if match.startswith("http") else "http://" + match
        parts.append(f'<a href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">{html.escape(match)}</a>')
        last = e
    parts.append(html.escape(text[last:]))
    return "".join(parts)

def format_value_for_html(value: str) -> str:
    if not value:
        return ""
    lines = value.splitlines()
    out = []
    in_list = False
    buf = []
    def flush_para():
        nonlocal buf
        if buf:
            txt = " ".join(p.strip() for p in buf).strip()
            if txt:
                out.append(f"<p>{linkify(txt)}</p>")
            buf = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("•"):
            flush_para()
            item = s.lstrip("•").strip()
            if not in_list:
                in_list = True
                out.append("<ul>")
            out.append(f"<li>{linkify(item)}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if s == "":
                flush_para()
            else:
                buf.append(ln)
    flush_para()
    if in_list:
        out.append("</ul>")
    return "".join(out)

def load_tag_map():
    tag_map = {}
    if not FUNCTIONAL_DM.is_file():
        return tag_map
    txt = FUNCTIONAL_DM.read_text(encoding="utf-8")
    # Parse `key` (label) patterns - these are the primary mappings
    for m in re.finditer(r"`([^`]+)`\s*\(([^)]+)\)", txt):
        key = m.group(1).strip()
        label = m.group(2).strip()
        pc = PREFERRED_CASING.get(key.lower())
        if pc:
            label = pc
        tag_map[key] = label
        # Also add reverse mapping: Dutch label -> Dutch label (so Naam maps to Naam)
        tag_map[label] = label
    # Parse backtick-wrapped keys without labels
    for m in re.finditer(r"`([^`]+)`(?!\s*\()", txt):
        key = m.group(1).strip()
        if key not in tag_map:
            tag_map[key] = PREFERRED_CASING.get(key.lower(), key.capitalize())
    # Parse lines like: name (label) without backticks
    for m in re.finditer(r"^([A-Za-z0-9_]+)\s*\(([^)]+)\)", txt, re.M):
        key = m.group(1).strip()
        label = m.group(2).strip()
        if key not in tag_map:
            pc = PREFERRED_CASING.get(key.lower())
            tag_map[key] = pc if pc else (label.capitalize() if label else key.capitalize())
        # Also add reverse mapping
        tag_map[label] = label
    return tag_map

TAG_MAP = load_tag_map()

def resolve_label(key: str) -> str:
    if not key:
        return ""
    # Try exact match in tag map first
    if key in TAG_MAP:
        return TAG_MAP[key]
    # Try case-insensitive match
    lk = key.lower()
    for k,v in TAG_MAP.items():
        if k.lower() == lk:
            return v
    # Check PREFERRED_CASING for short known names (LinkedIn, GitHub, etc.)
    fallback = PREFERRED_CASING.get(lk)
    if fallback:
        return fallback
    # Default: return nicely capitalized label
    return key.strip().capitalize() if key else ""

def is_attribute_header(line: str) -> bool:
    if not line:
        return False
    st = line.strip()
    # Explicit backtick-wrapped headers (e.g., `year`|`name`|...)
    if st.startswith("`") and "`" in st and "|" in st:
        return True
    # Lines explicitly starting with "attribute" keyword
    if st.lower().startswith("attribute"):
        return True
    return False

def parse_personal(path: Path):
    data = {}
    def process_text(txt):
        for ln in txt.splitlines():
            if not ln.strip() or is_attribute_header(ln): continue
            if "|" not in ln: continue
            k,v = [p.strip() for p in ln.split("|",1)]
            data[k] = v
    # If path is a directory, read personal.txt from it; otherwise read the file directly
    if path.is_dir():
        f = path / "personal.txt"
        if f.is_file():
            process_text(f.read_text(encoding="utf-8"))
    elif path.is_file():
        process_text(path.read_text(encoding="utf-8"))
    return data

def parse_urls(path: Path):
    """Parse URLs file (linkedin, website, github)"""
    data = {}
    if not path.is_file():
        return data
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or is_attribute_header(ln):
            continue
        if "|" not in ln:
            continue
        k, v = [p.strip() for p in ln.split("|", 1)]
        # Strip backticks and quotes from key
        k = k.strip("`'\"").strip()
        data[k] = v.strip()
    return data

def parse_simple_table(path: Path, skip_header=True):
    rows = []
    if not path.is_file(): return rows
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip(): continue
        if skip_header and is_attribute_header(ln): continue
        parts = [p.strip() for p in ln.split("|")]
        rows.append(parts)
    return rows

def parse_educations(path: Path):
    out = []
    rows = parse_simple_table(path, skip_header=True)
    for parts in rows:
        period = parts[0] if len(parts)>0 else ""
        name = parts[1] if len(parts)>1 else ""
        institute = parts[2] if len(parts)>2 else ""
        place = parts[3] if len(parts)>3 else ""
        addition = parts[4] if len(parts)>4 else (parts[2] if len(parts)==3 else "")
        out.append({"PERIODE":period,"NAAM":name,"INSTITUUT":institute,"PLAATS":place,"TOEL":addition})
    return out

def parse_certifications(path: Path):
    """Parse a simple certifications table with columns: year|name|organization
    and return a list of dicts compatible with render_education_block (PERIODE, NAAM, INSTITUUT).
    """
    out = []
    rows = parse_simple_table(path, skip_header=True)
    for parts in rows:
        period = parts[0] if len(parts)>0 else ""
        name = parts[1] if len(parts)>1 else ""
        org = parts[2] if len(parts)>2 else ""
        out.append({"PERIODE":period,"NAAM":name,"INSTITUUT":org,"PLAATS":"","TOEL":""})
    return out

def parse_courses(path: Path):
    out = []
    rows = parse_simple_table(path, skip_header=True)
    # Group courses by year/period, maintaining order of first appearance
    periods_dict = {}
    periods_order = []
    for parts in rows:
        period = parts[0] if len(parts)>0 else ""
        items = parts[1:] if len(parts)>1 else []
        if period not in periods_dict:
            periods_dict[period] = []
            periods_order.append(period)
        periods_dict[period].extend(items)
    # Convert back to list of dicts, maintaining order of first appearance
    for period in periods_order:
        out.append({"PERIODE":period,"ITEMS":periods_dict[period]})
    return out

def parse_courses_short(path: Path):
    out = []
    if not path.is_file(): return out
    simple = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip(): continue
        if is_attribute_header(ln): continue
        if "|" in ln:
            parts = [p.strip() for p in ln.split("|")]
            period = parts[0]; items = parts[1:]
            out.append({"PERIODE":period,"ITEMS":items})
        else:
            simple.append(ln.strip())
    if simple:
        out.append({"PERIODE":"","ITEMS":simple})
    return out

def parse_engagement_file(path: Path):
    txt = path.read_text(encoding="utf-8")
    lines = [l.rstrip() for l in txt.splitlines()]
    data = {}
    cur = None
    buf = []
    
    for ln in lines:
        s = ln.strip()
        if not s:  # skip empty lines
            continue
            
        # Check for pipe-separated key|value format: `key`|value or key|value
        if "|" in s:
            parts = s.split("|", 1)
            key = parts[0].strip().strip("`").strip("'").strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            # Save previous key's buffer if any
            if cur:
                data[cur] = "\n".join(buf).strip()
            
            cur = key
            buf = [value] if value else []
        # Bullet point or continuation - add to current buffer
        elif s.startswith("•") or (cur and not "|" in s):
            if cur:
                buf.append(ln)
        else:
            # Unknown line format - skip
            pass
    
    # Save last key's buffer
    if cur:
        data[cur] = "\n".join(buf).strip()
    
    # Ensure period key from filename
    period = path.name.replace("opdracht_","").replace(".txt","").replace("_"," – ")
    if "period" not in data and "periode" not in data and "PERIODE" not in data:
        data["periode"] = period
    
    return data

def normalize_key(k: str) -> str:
    return re.sub(r'[^a-z0-9]', '', k.lower())

ENG_SYNONYMS = {
    "functie": ["functie","functienaam","job","jobtitle","job_title"],
    "werkzaamheden": ["werkzaamheden","work","workdetails","textblockwork","text_block_work","work_description"],
    "prestaties": ["belangrijksteprestaties","achievements","achievements_text","text_block_achievements","achievements_list"],
    "trefwoorden": ["trefwoorden","keywords","text_block_keywords","keywords_list"],
    "organisatie": ["organisatie","organisatie_naam","organization","organization_name","employer"]
}

def find_data_for_variant(data: dict, variants: list):
    for key in data.keys():
        if normalize_key(key) in variants:
            return data[key]
    return None

def render_personal(personal: dict, profile_img: str):
    if not personal and not profile_img:
        return ""
    rows = []
    # Order keys based on personal-data.txt structure
    # personal-data.txt has: Naam, Roepnaam, Woonplaats, Geboortedatum, Beschikbaar per, Functie
    # Note: URLs (LinkedIn, Website, GitHub) are now in urls-contact.txt and rendered in sidebar
    order_keys = ["Naam", "Roepnaam", "Woonplaats", "Geboortedatum", "Telefoon", "Beschikbaar per ", "Functie"]
    
    handled_keys = set()
    for key in order_keys:
        if key in personal:
            val = personal[key]
            label = resolve_label(key)
            rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{format_value_for_html(val)}</div></td></tr>")
            handled_keys.add(key)
    
    # Render remaining keys that weren't in the ordered list
    for k,v in personal.items():
        if k in handled_keys: continue
        kk = k.strip().strip("`")
        label = resolve_label(kk)
        rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{format_value_for_html(v)}</div></td></tr>")
    
    table = "<table class='personal-table'>" + "".join(rows) + "</table>"
    # Convert profile image to base64 if present
    photo_src = image_to_base64(profile_img) if profile_img else ""
    photo = f'<img src="{photo_src}" alt="Foto" class="profile-photo">' if photo_src else ""
    # Table first, then photo on the right
    return f'<div class="personal-block"><div class="personal-table-wrap">{table}</div>{photo}</div>'

def render_urls_sidebar(urls: dict, logo: str = ""):
    """Render URLs in sidebar format (RULE 13 & RULE 18)"""
    if not urls and not logo:
        return ""
    out = ['<aside class="urls-sidebar">']
    
    # Add logo at the top of sidebar - convert to base64
    if logo:
        logo_src = image_to_base64(logo)
        if logo_src:
            out.append(f'<div class="sidebar-logo"><img src="{logo_src}" alt="Logo" class="sidebar-logo-img"/></div>')
    
    # Define order and configuration for contact items with display labels
    contact_items = [
        ("linkedin_url", "linkedin", "https://", "LinkedIn"),
        ("linkedin", "linkedin", "https://", "LinkedIn"),
        ("website_url", "website", "https://", "Website"),
        ("website", "website", "https://", "Website"),
        ("github_url", "github", "https://", "GitHub"),
        ("github", "github", "https://", "GitHub"),
        ("phone_nr", "phone", "tel:", ""),  # Show actual number
        ("phone-nr", "phone", "tel:", ""),
        ("telefoon", "phone", "tel:", ""),
        ("telephone", "phone", "tel:", ""),
        ("e-mail", "email", "mailto:", ""),  # Show actual email
        ("email", "email", "mailto:", ""),
    ]
    
    # Track which URLs have been rendered to avoid duplicates
    rendered = set()
    
    for key, val in urls.items():
        if not val:
            continue
            
        key_lower = key.strip("'\"").lower().replace("_", "-")
        
        # Skip if already rendered
        if key_lower in rendered:
            continue
        
        # Find matching contact item
        icon_name = None
        href_prefix = ""
        display_label = ""
        for item_key, item_icon, item_prefix, item_label in contact_items:
            if key_lower == item_key.lower().replace("_", "-"):
                icon_name = item_icon
                href_prefix = item_prefix
                display_label = item_label if item_label else val  # Use actual value if no label
                # Mark all variants as rendered
                rendered.add(key_lower)
                for k, i, p, l in contact_items:
                    if i == item_icon:
                        rendered.add(k.lower().replace("_", "-"))
                break
        
        if not icon_name:
            icon_name = key_lower
            href_prefix = ""
            display_label = val
            rendered.add(key_lower)
        
        # Create href with proper prefix
        href = val if val.startswith(('http://', 'https://', 'tel:', 'mailto:')) else href_prefix + val
        # Contact link with icon and text label
        out.append(f'<a href="{html.escape(href)}" class="contact-link" data-type="{icon_name}" title="{html.escape(val)}"><span class="contact-text">{html.escape(display_label)}</span></a>')
    
    out.append('</aside>')
    return "\n".join(out) if len(out) > 2 else ""

def render_education_block(eds):
    if not eds: return ""
    rows = []
    for ed in eds:
        peri = html.escape(ed.get("PERIODE",""))
        naam = html.escape(ed.get("NAAM",""))
        instituut = html.escape(ed.get("INSTITUUT",""))
        plaats = html.escape(ed.get("PLAATS",""))
        toel = format_value_for_html(ed.get("TOEL",""))
        
        # First row: periode, naam — instituut, plaats
        naam_instituut = f"{naam} — {instituut}" if instituut else naam
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name'>{naam_instituut}</td><td class='edu-place'>{plaats}</td></tr>")
        
        # Second row: toelichting if present
        if toel:
            rows.append(f"<tr><td class='label'>&nbsp;</td><td class='edu-desc' colspan='2'><div class='tekstblok'>{toel}</div></td></tr>")
    
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_certifications_block(eds):
    # Render certifications without bold (no edu-name class).
    if not eds: return ""
    rows = []
    for ed in eds:
        peri = html.escape(ed.get("PERIODE",""))
        naam = html.escape(ed.get("NAAM","") + (f" — {ed.get('INSTITUUT','')}" if ed.get("INSTITUUT") else ""))
        plaats = html.escape(ed.get("PLAATS",""))
        toel = format_value_for_html(ed.get("TOEL",""))
        rows.append(f"<tr><td class='label'>{peri}</td><td>{naam}</td><td class='edu-place'>{plaats}</td></tr>")
        if toel:
            rows.append(f"<tr><td class='label'>&nbsp;</td><td colspan='2'><div class='tekstblok'>{toel}</div></td></tr>")
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_courses_block(rows):
    if not rows: return ""
    out = []
    for r in rows:
        peri = html.escape(r.get("PERIODE",""))
        items_html = ", ".join(html.escape(i) for i in r.get("ITEMS",[]))
        out.append(f"<table class='education-table'><tr><td class='label'>{peri}</td><td colspan='2'><div class='tekstblok'>{linkify(items_html)}</div></td></tr></table>")
    return "".join(out)

def render_courses_short_block(rows):
    if not rows: return ""
    parts = []
    for r in rows:
        peri = html.escape(r.get("PERIODE",""))
        items = r.get("ITEMS",[])
        items_html = ", ".join(item.strip() for item in items)
    parts.append(f"<table class='education-table'><tr><td class='label'>{peri}</td><td colspan='2'><div class='tekstblok'>{linkify(items_html)}</div></td></tr></table>")
    return "".join(parts)

def render_engagements_block():
    if not ENGAGEMENTS_DIR.is_dir(): return ""
    parts = []
    for f in sorted(ENGAGEMENTS_DIR.iterdir(), key=lambda p: p.name, reverse=True):
        if not f.is_file() or f.suffix.lower() != ".txt": continue
        parts.append(render_one_engagement(f))
    return "".join(parts)

def render_one_engagement(path: Path):
    data = parse_engagement_file(path)
    normalized = {normalize_key(k): (k, v) for k,v in data.items()}
    
    def get_variant(variants):
        for v in variants:
            nv = normalize_key(v)
            if nv in normalized:
                return normalized[nv][1]  # return value only
        return None
    
    # Get summary data (always visible)
    periode = get_variant(["periode","PERIODE"])
    organisatie = get_variant(ENG_SYNONYMS["organisatie"])
    functie = get_variant(ENG_SYNONYMS["functie"])
    
    # Get detail data (collapsible)
    werkzaamheden = get_variant(ENG_SYNONYMS["werkzaamheden"])
    prestaties = get_variant(ENG_SYNONYMS["prestaties"])
    trefwoorden = get_variant(ENG_SYNONYMS["trefwoorden"])
    
    # Build collapsible engagement HTML (RULE 20)
    out = ['<div class="engagement-item">']
    
    # Summary line (always visible, clickable)
    out.append('<div class="engagement-summary" role="button" tabindex="0" aria-expanded="false">')
    out.append('<span class="engagement-toggle">▶</span>')
    out.append('<div class="engagement-summary-content">')
    
    if periode:
        out.append(f'<span class="engagement-period">{html.escape(periode)}</span>')
    if organisatie:
        out.append(f'<span class="engagement-org">{html.escape(organisatie)}</span>')
    if functie:
        out.append(f'<span class="engagement-role">{html.escape(functie)}</span>')
    
    out.append('</div>')  # Close engagement-summary-content
    out.append('</div>')  # Close engagement-summary
    
    # Detail section (hidden by default)
    out.append('<div class="engagement-details">')
    
    if werkzaamheden:
        label = PRETTY_KEYS.get("WERKZAAMHEDEN", "Werkzaamheden")
        out.append(f'<div class="engagement-detail-item"><div class="detail-label">{html.escape(label)}</div>')
        out.append(f'<div class="tekstblok">{format_value_for_html(werkzaamheden)}</div></div>')
    
    if prestaties:
        label = PRETTY_KEYS.get("BELANGRIJKSTE PRESTATIES", "Belangrijkste prestaties")
        out.append(f'<div class="engagement-detail-item"><div class="detail-label">{html.escape(label)}</div>')
        out.append(f'<div class="tekstblok">{format_value_for_html(prestaties)}</div></div>')
    
    if trefwoorden:
        label = PRETTY_KEYS.get("TREFWOORDEN", "Trefwoorden")
        out.append(f'<div class="engagement-detail-item"><div class="detail-label">{html.escape(label)}</div>')
        out.append(f'<div class="tekstblok">{format_value_for_html(trefwoorden)}</div></div>')
    
    out.append('</div>')  # Close engagement-details
    out.append('</div>')  # Close engagement-item
    
    return "".join(out)

def load_block_text(name: str):
    # First try BLOCKS_DIR (content/blocks/)
    c = BLOCKS_DIR / name
    if c.exists() and c.is_file():
        return c.read_text(encoding="utf-8").strip()
    c2 = BLOCKS_DIR / (name + ".txt")
    if c2.exists() and c2.is_file():
        return c2.read_text(encoding="utf-8").strip()
    # Then try CONTENT_DIR directly (content/)
    c3 = CONTENT_DIR / name
    if c3.exists() and c3.is_file():
        return c3.read_text(encoding="utf-8").strip()
    c4 = CONTENT_DIR / (name + ".txt")
    if c4.exists() and c4.is_file():
        return c4.read_text(encoding="utf-8").strip()
    return ""

def parse_blocks_config():
    if not BLOCKS_CONFIG.is_file():
        return []
    out = []
    for ln in BLOCKS_CONFIG.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.strip().startswith("#"): continue
        if is_attribute_header(ln): continue
        parts = [p.strip() for p in ln.split("|",1)]
        out.append({"name": parts[0], "title": parts[1] if len(parts)>1 else ""})
    return out

def build_html():
    logo = find_first(LOGO_CANDIDATES)
    profile = find_first(PROFILE_CANDIDATES)
    personal = parse_personal(PERSONAL_DATA_FILE)
    urls = parse_urls(URLS_FILE)
    educations = parse_educations(EDUCATION_FILE)
    certifications = parse_certifications(CERTIFICATIONS_FILE)
    courses = parse_courses(COURSES_FILE)
    courses_short = parse_courses_short(COURSES_SHORT_FILE)
    cfg = parse_blocks_config()

    if not cfg:
        cfg = [
            {"name":"personal","title":"PERSOONLIJK"},
            {"name":"education","title":"OPLEIDINGEN"},
            {"name":"certifications","title":"CERTIFICERINGEN"},
            {"name":"courses","title":"CURSUSSEN"},
            {"name":"courses_short","title":"OVERIGE CURSUSSEN"},
            {"name":"engagements","title":"WERKERVARING"},
        ]
    else:
        names = [b["name"].strip().lower().replace(".txt","") for b in cfg]
        if "personal" not in names and "personal-data" not in names and "persoonlijk" not in names and personal:
            cfg.insert(0, {"name":"personal","title":"Persoonlijk"})

    now = datetime.now().strftime("%d %B %Y %H:%M:%S")
    css_version = datetime.now().strftime("%Y%m%d")  # Cache-busting version for CSS
    out = []
    out.append("<!doctype html><html lang='nl'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'/>")
    out.append(f"<title>CV</title><link rel='stylesheet' href='{norm(str(CSS_PATH))}?v={css_version}'>")
    out.append("</head><body>")
    
    # Container with sidebar and main content
    out.append("<div class='container'>")
    
    # Sidebar with logo and contact info (RULE 13, RULE 18)
    urls_sidebar = render_urls_sidebar(urls, logo)
    if urls_sidebar:
        out.append(urls_sidebar)
    
    # Main content wrapper
    out.append("<div class='main-content'>")

    for i, b in enumerate(cfg):
        title = (b.get("title") or "").strip()
        name = b.get("name","").strip().lower()
        
        # Skip urls - already rendered in sidebar (RULE 13)
        if name in ("urls","urls_sidebar"):
            continue
            
        if title:
            out.append(f"<section class='block'><div class='block-title'>{html.escape(title.upper())}</div>")
        else:
            out.append("<section class='block'>")
        
        if name in ("personal","persoonlijk","personal-data"):
            # Render personal data table with profile photo
            out.append(render_personal(personal, profile))
        elif name in ("personal-text","persoonlijke-tekst"):
            # Render personal text block if exists
            txt = load_block_text("personal-text")
            if txt:
                out.append(f"<div class='tekstblok'>{format_value_for_html(txt)}</div>")
        elif name in ("education","educations","opleidingen"):
            out.append(render_education_block(educations))
        elif name in ("certifications","certificeringen"):
            out.append(render_certifications_block(certifications))
        elif name in ("courses","cursussen"):
            out.append(render_courses_block(courses))
        elif name in ("courses_short","courses-short","overige_cursussen","coursesshort"):
            out.append(render_courses_short_block(courses_short))
        elif name in ("engagements","werkervaring","opdrachten"):
            out.append(render_engagements_block())
        else:
            txt = load_block_text(b.get("name",""))
            if txt:
                out.append(f"<div class='tekstblok'>{format_value_for_html(txt)}</div>")
        out.append("</section>")
        # Only add separator if not the last block
        if i < len(cfg) - 1:
            out.append("<div class='block-sep'></div>")

    out.append("</div>")  # Close main-content
    out.append("</div>")  # Close container
    out.append(f"<div class='generated'>{html.escape(now)}</div>")
    
    # Add JavaScript for collapsible engagements (RULE 20)
    out.append("<script>")
    out.append("""
document.addEventListener('DOMContentLoaded', function() {
  const summaries = document.querySelectorAll('.engagement-summary');
  
  summaries.forEach(summary => {
    // Click handler
    summary.addEventListener('click', function() {
      toggleEngagement(this);
    });
    
    // Keyboard handler (Enter or Space)
    summary.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleEngagement(this);
      }
    });
  });
  
  function toggleEngagement(summary) {
    const expanded = summary.getAttribute('aria-expanded') === 'true';
    summary.setAttribute('aria-expanded', !expanded);
  }
});
""")
    out.append("</script>")
    out.append("</body></html>")
    return "\n".join(out)

if __name__ == "__main__":
    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print("Generated:", OUTPUT_FILE)
