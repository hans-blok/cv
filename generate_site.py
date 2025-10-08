import os
import re
import html
from pathlib import Path

# --- configuration (adjust paths if needed) ---
ROOT = Path(__file__).resolve().parent
ENGAGEMENTS_DIR = ROOT / "engagements"
PERSONAL_DIR = ROOT / "personal"
EDUCATION_FILE = ROOT / "education" / "educations.txt"
COURSES_FILE = ROOT / "courses" / "courses.txt"
COURSES_SHORT_FILE = ROOT / "courses" / "courses-short.txt"
BLOCKS_DIR = ROOT / "blocks"
BLOCKS_CONFIG_CANDIDATES = [ROOT / "specs" / "blocks.txt", ROOT / "static" / "blocks.txt"]
CSS_PATH = ROOT / "static" / "style.css"
OUTPUT_FILE = ROOT / "cv.html"
LOGO_DIRS = ["pictures", "logos", "logo", "images", "static/images"]

# --- utilities ---
def norm_path_for_html(p: str) -> str:
    return p.replace("\\", "/")

def find_file_in_dirs(names):
    for n in names:
        p = ROOT / n
        if p.is_file():
            return norm_path_for_html(str(p))
    for d in LOGO_DIRS:
        dd = ROOT / d
        if dd.is_dir():
            for f in sorted(dd.iterdir()):
                if f.is_file() and f.name.lower().startswith("logo") and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                    return norm_path_for_html(str(f))
    return ""

def find_site_logo():
    return find_file_in_dirs(["pictures/logo.png", "pictures/logo.jpg", "pictures/logo-header.png"])

def find_profile_image():
    return find_file_in_dirs(["pictures/profile.jpg", "pictures/profile.png", "pictures/profile.jpeg"])

# --- text helpers ---
_URL_RE = re.compile(r"(https?://[^\s<>]+|www\.[^\s<>]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")

def linkify(text: str) -> str:
    if not text:
        return ""
    parts = []
    last = 0
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
    parts = []
    in_list = False
    para = []

    def flush_para():
        nonlocal para
        if para:
            txt = " ".join(p.strip() for p in para).strip()
            if txt:
                parts.append(f"<p>{linkify(txt)}</p>")
            para = []

    for ln in lines:
        s = ln.strip()
        if s.startswith("•"):
            flush_para()
            item = s.lstrip("•").strip()
            if not in_list:
                in_list = True
                parts.append("<ul>")
            parts.append(f"<li>{linkify(item)}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            if s == "":
                flush_para()
            else:
                para.append(ln)
    flush_para()
    if in_list:
        parts.append("</ul>")
    return "".join(parts)

def pretty_label(key: str) -> str:
    if not key:
        return ""
    mapping = {
        "PERIODE": "Periode",
        "ORGANISATIE": "Organisatie",
        "FUNCTIE": "Functie",
        "WERKZAAMHEDEN": "Werkzaamheden",
        "BELANGRIJKSTE PRESTATIES": "Belangrijkste prestaties"
    }
    up = key.strip().upper()
    return mapping.get(up, key.strip().capitalize())

# --- parsers ---
def parse_personal(directory: Path) -> dict:
    data = {}
    if directory.is_dir():
        for fname in sorted(directory.iterdir()):
            if not fname.is_file():
                continue
            with fname.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "|" not in line:
                        continue
                    k, v = [p.strip() for p in line.split("|", 1)]
                    data[k] = v
    else:
        pfile = ROOT / "personal.txt"
        if pfile.is_file():
            with pfile.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "|" not in line:
                        continue
                    k, v = [p.strip() for p in line.split("|", 1)]
                    data[k] = v
    return data

def parse_educations(file_path: Path):
    items = []
    if not file_path.is_file():
        return items
    with file_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.upper().startswith("OPLEIDING"):
                continue
            parts = [p.strip() for p in line.split("|")]
            period = parts[0] if len(parts) > 0 else ""
            name = parts[1] if len(parts) > 1 else ""
            institute = parts[2] if len(parts) > 2 else ""
            place = parts[3] if len(parts) > 3 else ""
            addition = parts[4] if len(parts) > 4 else (parts[2] if len(parts) == 3 else "")
            items.append({"PERIODE": period, "NAAM": name, "INSTITUUT": institute, "PLAATS": place, "TOELICHTING": addition})
    return items

def parse_courses(file_path: Path):
    rows = []
    if not file_path.is_file():
        return rows
    with file_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.lower().startswith("courses"):
                continue
            parts = [p.strip() for p in line.split("|")]
            period = parts[0] if len(parts) > 0 else ""
            items = parts[1:] if len(parts) > 1 else []
            rows.append({"PERIODE": period, "ITEMS": items})
    return rows

def parse_courses_short(file_path: Path):
    rows = []
    if not file_path.is_file():
        return rows
    simple = []
    with file_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                period = parts[0]
                items = parts[1:]
                rows.append({"PERIODE": period, "ITEMS": items})
            else:
                simple.append(line)
    if simple:
        rows.append({"PERIODE": "", "ITEMS": simple})
    return rows

def parse_engagement(file_path: Path):
    with file_path.open(encoding="utf-8") as f:
        raw = f.read()
    lines = [ln.rstrip() for ln in raw.splitlines()]
    data = {}
    current = None
    buffer = []
    for ln in lines:
        s = ln.strip()
        if s and s == s.upper() and not s.startswith("•"):
            if current:
                data[current] = "\n".join(buffer).strip()
            current = s
            buffer = []
        else:
            buffer.append(ln)
    if current:
        data[current] = "\n".join(buffer).strip()
    filename = file_path.name
    period = filename.replace("opdracht_", "").replace(".txt", "").replace("_", " – ")
    data = {"PERIODE": period, **data}
    return data

def extract_year(filename: str) -> int:
    nums = re.findall(r"\d{4}", filename)
    if nums:
        try:
            return int(nums[-1])
        except Exception:
            return 0
    return 0

def parse_blocks_config() -> list:
    cfg = None
    for candidate in BLOCKS_CONFIG_CANDIDATES:
        if candidate.is_file():
            cfg = candidate
            break
    if cfg is None:
        return []
    blocks = []
    with cfg.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|", 1)]
            filename = parts[0]
            title = parts[1] if len(parts) > 1 else filename
            blocks.append({"NAME": filename, "TITLE": title})
    return blocks

# --- render helpers ---
def format_personal_value_for_html(value: str) -> str:
    if not value:
        return ""
    lines = value.splitlines()
    if len(lines) == 1:
        return linkify(lines[0])
    return "".join(f"<p>{linkify(l)}</p>" for l in lines)

def render_personal(personal: dict) -> str:
    if not personal:
        return ""
    rows = []
    for k, v in personal.items():
        rows.append(f"<tr><td class='label'>{html.escape(k)}</td><td class='value'><div class='tekstblok'>{format_personal_value_for_html(v)}</div></td></tr>")
    return "<table class='personal-table'>" + "".join(rows) + "</table>"

def render_educations(educations: list) -> str:
    if not educations:
        return ""
    max_chars = 0
    for ed in educations:
        name_full = ed.get("NAAM", "") + (f" — {ed.get('INSTITUUT', '')}" if ed.get("INSTITUUT") else "")
        max_chars = max(max_chars, len(name_full))
    min_ch = max_chars + 2
    rows = []
    for ed in educations:
        peri = html.escape(ed.get("PERIODE", ""))
        naam = html.escape(ed.get("NAAM", "") + (f" — {ed.get('INSTITUUT', '')}" if ed.get("INSTITUUT") else ""))
        plaats = html.escape(ed.get("PLAATS", ""))
        toel = format_value_for_html(ed.get("TOELICHTING", ""))
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name' style='min-width:{min_ch}ch'>{naam}</td><td class='edu-place'>{plaats}</td></tr>")
        if toel:
            rows.append(f"<tr><td class='label'>&nbsp;</td><td class='edu-desc' colspan='2'><div class='tekstblok'>{toel}</div></td></tr>")
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_courses(courses_list: list) -> str:
    if not courses_list:
        return ""
    rows = []
    for c in courses_list:
        peri = html.escape(c.get("PERIODE", ""))
        items = ", ".join(html.escape(i) for i in c.get("ITEMS", []))
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name' colspan='2'>{items}</td></tr>")
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_engagements() -> str:
    if not ENGAGEMENTS_DIR.is_dir():
        return ""
    parts = []
    for fname in sorted(ENGAGEMENTS_DIR.iterdir(), key=lambda p: extract_year(p.name), reverse=True):
        if not fname.is_file() or fname.suffix.lower() != ".txt":
            continue
        data = parse_engagement(fname)
        rows = []
        for k, v in data.items():
            label = html.escape(pretty_label(k))
            rows.append(f"<tr><td class='label'>{label}</td><td class='value'><div class='tekstblok'>{format_value_for_html(v)}</div></td></tr>")
        parts.append("<table class='engagement-table'>" + "".join(rows) + "</table>")
    return "".join(parts)

# --- main assembly following blocks config order ---
def build_html():
    site_logo = find_site_logo()
    profile = find_profile_image()
    personal = parse_personal(PERSONAL_DIR)
    educations = parse_educations(EDUCATION_FILE)
    courses = parse_courses(COURSES_FILE) + parse_courses_short(COURSES_SHORT_FILE)
    blocks_cfg = parse_blocks_config()

    blocks_html = []
    render_map = {
        "personal": lambda: render_personal(personal),
        "education": lambda: render_educations(educations),
        "education/educations": lambda: render_educations(educations),
        "courses": lambda: render_courses(parse_courses(COURSES_FILE)),
        "courses_short": lambda: render_courses(parse_courses_short(COURSES_SHORT_FILE)),
        "engagements": render_engagements
    }

    for b in blocks_cfg:
        name = b["NAME"].strip()
        key = name.lower().replace(".txt", "").replace("-", "_")
        title = html.escape((b.get("TITLE") or name).upper())
        content_html = ""
        if key in render_map:
            content_html = render_map[key]()
        else:
            candidate = BLOCKS_DIR / name
            if not candidate.exists():
                candidate = BLOCKS_DIR / (name + ".txt")
            if candidate.exists():
                with candidate.open(encoding="utf-8") as f:
                    content_html = format_value_for_html(f.read().strip())
        blocks_html.append(f"<section class='block'><div class='block-title'>{title}</div>{content_html}</section>")

    html_doc = [
        "<!doctype html>",
        "<html lang='nl'>",
        "<head>",
        "  <meta charset='utf-8'>",
        "  <meta name='viewport' content='width=device-width,initial-scale=1'/>",
        "  <title>CV</title>",
        f"  <link rel='stylesheet' href='{norm_path_for_html(str(CSS_PATH))}'>",
        "</head>",
        "<body>",
    ]
    if site_logo:
        html_doc.append(f"<img src=\"{html.escape(site_logo)}\" alt=\"Logo\" class=\"site-logo\" />")
    html_doc.append("<div class='container'>")
    html_doc.extend(blocks_html)
    html_doc.append("<h1>WERKERVARING</h1>")
    html_doc.append(render_engagements())
    html_doc.append("</div></body></html>")
    return "\n".join(html_doc)

if __name__ == "__main__":
    out = build_html()
    OUTPUT_FILE.write_text(out, encoding="utf-8")
    print(f"Generated: {OUTPUT_FILE}")
