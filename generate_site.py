import os
import re
import html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
ENGAGEMENTS_DIR = ROOT / "engagements"
PERSONAL_DIR = ROOT / "personal"
EDUCATION_FILE = ROOT / "education" / "educations.txt"
COURSES_FILE = ROOT / "courses" / "courses.txt"
COURSES_SHORT_FILE = ROOT / "courses-short" / "courses-short.txt"
CERTIFICATIONS_FILE = ROOT / "certifications" / "certifications.txt"
BLOCKS_DIR = ROOT / "blocks"
BLOCKS_CONFIG = ROOT / "static" / "blocks.txt"
FUNCTIONAL_DM = ROOT / "specs" / "functional_dm.md"
CSS_PATH = Path("static") / "style.css"
OUTPUT_FILE = ROOT / "cv.html"

LOGO_CANDIDATES = ["pictures/logo-header.png", "pictures/logo-header.jpg", "pictures/logo.png", "pictures/logo.jpg"]
PROFILE_CANDIDATES = ["pictures/profile-photo.jpg", "pictures/profile-photo.png", "pictures/profile.jpg", "pictures/profile.png"]
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
    "job_title": "Functie"
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
    for m in re.finditer(r"`([^`]+)`\s*\(([^)]+)\)", txt):
        key = m.group(1).strip()
        label = m.group(2).strip()
        pc = PREFERRED_CASING.get(key.lower())
        if pc:
            label = pc
        tag_map[key] = label
    for m in re.finditer(r"`([^`]+)`(?!\s*\()", txt):
        key = m.group(1).strip()
        if key not in tag_map:
            tag_map[key] = PREFERRED_CASING.get(key.lower(), key.capitalize())
    return tag_map

TAG_MAP = load_tag_map()

def resolve_label(key: str) -> str:
    if not key:
        return ""
    if key in TAG_MAP:
        return TAG_MAP[key]
    lk = key.lower()
    for k,v in TAG_MAP.items():
        if k.lower() == lk:
            return v
    for k,v in TAG_MAP.items():
        if v.lower() == key.strip().lower():
            return v
    return PREFERRED_CASING.get(lk, key.strip().capitalize())

def is_attribute_header(line: str) -> bool:
    if not line:
        return False
    st = line.strip()
    if st.startswith("`") and "`" in st:
        return True
    if "|" in st and "`" in st:
        return True
    if st.lower().startswith("attribute"):
        return True
    return False

def parse_personal(directory: Path):
    data = {}
    def process_text(txt):
        for ln in txt.splitlines():
            if not ln.strip() or is_attribute_header(ln): continue
            if "|" not in ln: continue
            k,v = [p.strip() for p in ln.split("|",1)]
            data[k] = v
    if directory.is_dir():
        for f in sorted(directory.iterdir()):
            if not f.is_file(): continue
            process_text(f.read_text(encoding="utf-8"))
    else:
        p = ROOT / "personal.txt"
        if p.is_file():
            process_text(p.read_text(encoding="utf-8"))
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
    cur = None; buf = []
    for ln in lines:
        s = ln.strip()
        # header detection: uppercase-ish or lines that end with ':' or backtick-enclosed keys
        letters = re.sub(r'[^A-Za-z]', '', s)
        is_header = False
        if s and not s.startswith("•"):
            if letters and letters == letters.upper() and len(letters) >= 2:
                is_header = True
            elif s.endswith(":") and len(s) < 60:
                is_header = True
            elif s.startswith("`") and "`" in s:
                is_header = True
        if is_header:
            if cur:
                data[cur] = "\n".join(buf).strip()
            # normalize header key: strip trailing ':' and backticks
            cur = s.rstrip(":").strip().strip("`")
            buf = []
        else:
            buf.append(ln)
    if cur:
        data[cur] = "\n".join(buf).strip()
    # ensure period key (if not present) from filename
    period = path.name.replace("opdracht_","").replace(".txt","").replace("_"," – ")
    if "PERIODE" not in data and "Periode" not in data:
        data["PERIODE"] = period
    return data

def normalize_key(k: str) -> str:
    return re.sub(r'[^a-z0-9]', '', k.lower())

ENG_SYNONYMS = {
    "functie": ["functie","functienaam","job","jobtitle","job_title"],
    "werkzaamheden": ["werkzaamheden","work","workdetails","textblockwork","text_block_work","work_description"],
    "prestaties": ["belangrijksteprestaties","achievements","achievements_text","text_block_achievements","achievements_list"],
    "trefwoorden": ["trefwoorden","keywords","text_block_keywords","keywords_list"],
    "organisatie": ["organisatie","organisatie_naam","organization","employer"]
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
    order_keys = ["name","usual_name","place_of_residence","date_of_birth","available","job_title","linkedin_url","website_url","github_url"]
    for key in order_keys:
        if key in personal:
            rows.append(f"<tr><td class='label'>{html.escape(resolve_label(key))}</td><td class='value'><div class='tekstblok'>{format_value_for_html(personal[key])}</div></td></tr>")
    for k,v in personal.items():
        if k in order_keys: continue
        kk = k.strip().strip("`")
        label = resolve_label(kk) if kk in TAG_MAP else kk.capitalize()
        rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{format_value_for_html(v)}</div></td></tr>")
    table = "<table class='personal-table'>" + "".join(rows) + "</table>"
    photo = f'<img src="{html.escape(profile_img)}" alt="Foto" class="profile-photo">' if profile_img else ""
    return f'<div class="personal-block"><div class="personal-table-wrap">{table}</div>{photo}</div>'

def render_education_block(eds):
    if not eds: return ""
    max_chars = max((len(ed.get("NAAM","") + ed.get("INSTITUUT","")) for ed in eds), default=20)
    min_ch = max_chars + 2
    rows = []
    for ed in eds:
        peri = html.escape(ed.get("PERIODE",""))
        naam = html.escape(ed.get("NAAM","") + (f" — {ed.get('INSTITUUT','')}" if ed.get("INSTITUUT") else ""))
        plaats = html.escape(ed.get("PLAATS",""))
        toel = format_value_for_html(ed.get("TOEL",""))
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name' style='min-width:{min_ch}ch'>{naam}</td><td class='edu-place'>{plaats}</td></tr>")
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
    normalized = {normalize_key(k): v for k,v in data.items()}
    def get_variant(variants):
        for v in variants:
            nv = normalize_key(v)
            if nv in normalized:
                return normalized[nv]
        return None
    order = [
        ("periode", ["periode","PERIODE"]),
        ("functie", ENG_SYNONYMS["functie"]),
        ("werkzaamheden", ENG_SYNONYMS["werkzaamheden"]),
        ("prestaties", ENG_SYNONYMS["prestaties"]),
        ("trefwoorden", ENG_SYNONYMS["trefwoorden"]),
        ("organisatie", ENG_SYNONYMS["organisatie"])
    ]
    rows = []
    handled = set()
    for canon, variants in order:
        val = get_variant(variants)
        if val:
            label = PRETTY_KEYS.get(canon.upper(), resolve_label(canon))
            rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{format_value_for_html(val)}</div></td></tr>")
            handled.add(normalize_key(canon))
    # append remaining blocks (preserve order in file)
    for k,v in data.items():
        nk = normalize_key(k)
        if nk in handled: continue
        # Strip backticks from the key before resolving its label
        k_clean = k.strip().strip("`").strip()
        # Only show keys that are actually in the tag map (skip raw backtick keys)
        if k_clean.lower() not in [t.lower() for t in TAG_MAP.keys()]:
            continue
        label = resolve_label(k_clean)
        rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{format_value_for_html(v)}</div></td></tr>")
    return "<table class='engagement-table'>" + "".join(rows) + "</table>"

def load_block_text(name: str):
    c = BLOCKS_DIR / name
    if c.exists() and c.is_file():
        return c.read_text(encoding="utf-8").strip()
    c2 = BLOCKS_DIR / (name + ".txt")
    if c2.exists() and c2.is_file():
        return c2.read_text(encoding="utf-8").strip()
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
    personal = parse_personal(PERSONAL_DIR)
    educations = parse_educations(EDUCATION_FILE)
    certifications = parse_certifications(CERTIFICATIONS_FILE)
    courses = parse_courses(COURSES_FILE)
    courses_short = parse_courses_short(COURSES_SHORT_FILE)
    cfg = parse_blocks_config()

    if not cfg:
        cfg = [
            {"name":"personal","title":"Persoonlijk"},
            {"name":"education","title":"OPLEIDINGEN"},
            {"name":"certifications","title":"CERTIFICERINGEN"},
            {"name":"courses","title":"CURSUSSEN"},
            {"name":"courses_short","title":"OVERIGE CURSUSSEN"},
            {"name":"engagements","title":"WERKERVARING"},
        ]
    else:
        names = [b["name"].strip().lower().replace(".txt","") for b in cfg]
        if "personal" not in names and "persoonlijk" not in names and personal:
            cfg.insert(0, {"name":"personal","title":"Persoonlijk"})

    now = datetime.now().strftime("%d %B %Y %H:%M:%S")
    out = []
    out.append("<!doctype html><html lang='nl'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'/>")
    out.append(f"<title>CV</title><link rel='stylesheet' href='{norm(str(CSS_PATH))}'>")
    out.append("</head><body>")
    if logo:
        out.append(f"<div class='logo-area'><img src='{html.escape(logo)}' class='site-logo' alt='Logo'/><div class='generated'>{html.escape(now)}</div></div>")
    else:
        out.append(f"<div class='generated no-logo'>{html.escape(now)}</div>")
    out.append("<div class='container'>")

    for b in cfg:
        title = (b.get("title") or "").strip()
        if title:
            out.append(f"<section class='block'><div class='block-title'>{html.escape(title.upper())}</div>")
        else:
            out.append("<section class='block'>")
        name = b.get("name","").strip().lower()
        if name in ("personal","persoonlijk"):
            out.append(render_personal(personal, profile))
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
        out.append("<div class='block-sep'></div>")

    out.append("</div></body></html>")
    return "\n".join(out)

if __name__ == "__main__":
    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print("Generated:", OUTPUT_FILE)
