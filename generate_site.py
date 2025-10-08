import os
import re
import html

engagements_dir = "engagements"
personal_dir = "personal"
education_file = os.path.join("education", "educations.txt")
courses_file = os.path.join("courses", "courses.txt")
courses_short_file = os.path.join("courses", "courses-short.txt")
blocks_dir = "blocks"
blocks_config = os.path.join("static", "blocks.txt")
logo_dirs = ["pictures", "logos", "logo", "images", "static/images"]
css_path = "static/style.css"
output_file = "cv.html"

def norm_path_for_html(p):
    return p.replace("\\", "/")

def find_site_logo():
    for name in ("pictures/logo.png","pictures/logo.jpg","pictures/logo-header.png"):
        if os.path.isfile(name): return norm_path_for_html(name)
    for d in logo_dirs:
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                if n.lower().startswith("logo") and n.lower().endswith((".png",".jpg",".jpeg",".webp",".gif")):
                    return norm_path_for_html(os.path.join(d,n))
    return ""

def find_profile_image():
    for name in ("pictures/profile.png","pictures/profile.jpg","pictures/profile.jpeg"):
        if os.path.isfile(name): return norm_path_for_html(name)
    for d in logo_dirs:
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                ln = n.lower()
                if any(pfx in ln for pfx in ("profile","profielfoto","foto","portrait","headshot")) and ln.endswith((".png",".jpg",".jpeg",".webp",".gif")):
                    return norm_path_for_html(os.path.join(d,n))
    return ""

def parse_personal(directory):
    # read all files in personal/ or personal.txt lines like "Tag|Value"
    data = {}
    if os.path.isdir(directory):
        files = sorted(os.listdir(directory))
    else:
        files = []
    # also accept single file personal.txt at root of personal_dir
    for fname in files:
        path = os.path.join(directory, fname)
        if not os.path.isfile(path): continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line: continue
                k,v = [p.strip() for p in line.split("|",1)]
                data[k] = v
    return data

_url_re = re.compile(r"(https?://[^\s<>]+|www\.[^\s<>]+|[A-Za-z0-9._%+-]+@[A-ZaZ0-9.-]+\.[A-Za-z]{2,})")
def linkify(text):
    if not text: return ""
    parts=[]; last=0
    for m in _url_re.finditer(text):
        s,e = m.span()
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

def parse_engagement(file_path):
    with open(file_path, encoding="utf-8") as f:
        raw = f.read()
    lines = [ln.rstrip() for ln in raw.splitlines()]
    data = {}
    cur = None; buf=[]
    for line in lines:
        s = line.strip()
        if s and s == s.upper() and not s.startswith("•"):
            if cur:
                data[cur] = "\n".join(buf).strip()
            cur = s
            buf=[]
        else:
            buf.append(line)
    if cur:
        data[cur] = "\n".join(buf).strip()
    filename = os.path.basename(file_path)
    periode = filename.replace("opdracht_","").replace(".txt","").replace("_"," – ")
    data = {"PERIODE": periode, **data}
    return data

def extract_year(filename):
    nums = re.findall(r"\d{4}", filename)
    if nums:
        try: return int(nums[-1])
        except: return 0
    return 0

def format_value_for_html(value):
    if value is None: return ""
    lines = value.splitlines()
    parts=[]; in_list=False; buf=[]
    def flush():
        nonlocal buf
        if buf:
            text = " ".join(p.strip() for p in buf).strip()
            if text: parts.append(f"<p>{linkify(text)}</p>")
            buf=[]
    for ln in lines:
        s = ln.strip()
        if s.startswith("•"):
            flush()
            item = s.lstrip("•").strip()
            if not in_list:
                in_list=True; parts.append("<ul>")
            parts.append(f"<li>{linkify(item)}</li>")
        else:
            if in_list:
                parts.append("</ul>"); in_list=False
            if s=="":
                flush()
            else:
                buf.append(ln)
    flush()
    if in_list: parts.append("</ul>")
    return "".join(parts)

def parse_educations(file_path):
    items=[]
    if not os.path.isfile(file_path): return items
    with open(file_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line: continue
            if line.upper().startswith("OPLEIDING"): continue
            parts = [p.strip() for p in line.split("|")]
            period = parts[0] if len(parts)>0 else ""
            name = parts[1] if len(parts)>1 else ""
            institute = parts[2] if len(parts)>2 else ""
            place = parts[3] if len(parts)>3 else ""
            addition = parts[4] if len(parts)>4 else (parts[2] if len(parts)==3 else "")
            items.append({"PERIODE":period,"NAAM":name,"INSTITUUT":institute,"PLAATS":place,"TOELICHTING":addition})
    return items

def parse_courses(file_path):
    rows=[]
    if not os.path.isfile(file_path): return rows
    with open(file_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line: continue
            if line.lower().startswith("courses"): continue
            parts = [p.strip() for p in line.split("|")]
            period = parts[0] if len(parts)>0 else ""
            items = parts[1:] if len(parts)>1 else []
            rows.append({"PERIODE":period,"ITEMS":items})
    return rows

def parse_courses_short(file_path):
    # if file contains "period|item1|item2" treat like courses, else collect simple lines
    rows=[]
    if not os.path.isfile(file_path): return rows
    simple=[]
    with open(file_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line: continue
            if "|" in line:
                parts=[p.strip() for p in line.split("|")]
                period=parts[0]; items=parts[1:]
                rows.append({"PERIODE":period,"ITEMS":items})
            else:
                simple.append(line)
    if simple:
        rows.append({"PERIODE":"","ITEMS":simple})
    return rows

def parse_blocks(config_path, blocks_directory):
    blocks=[]
    if not os.path.isfile(config_path): return blocks
    with open(config_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"): continue
            parts = [p.strip() for p in line.split("|",1)]
            blockname = parts[0]
            blocktitle = parts[1] if len(parts)>1 else blockname
            blocks.append({"NAME":blockname, "TITLE":blocktitle})
    return blocks

def pretty_label(key):
    mapping = {
        "PERIODE":"Periode",
        "ORGANISATIE":"Organisatie",
        "FUNCTIE":"Functie",
        "WERKZAAMHEDEN":"Werkzaamheden",
        "BELANGRIJKSTE PRESTATIES":"Belangrijkste prestaties"
    }
    if not key: return ""
    return mapping.get(key.strip().upper(), key.strip().capitalize())

# build content
site_logo = find_site_logo()
profile_image = find_profile_image()
personal = parse_personal(personal_dir)
educations = parse_educations(education_file)
courses = parse_courses(courses_file) + parse_courses_short(courses_short_file)
blocks = parse_blocks(blocks_config, blocks_dir)

def render_personal():
    if not personal: return ""
    rows=[]
    for k,v in personal.items():
        rows.append(f"<tr><td class='label'>{html.escape(k)}</td><td class='value'><div class='tekstblok'>{format_personal_value_for_html(v)}</div></td></tr>")
    return "<table class='personal-table'>" + "".join(rows) + "</table>"

def format_personal_value_for_html(value):
    lines = value.splitlines()
    if len(lines)==1:
        return linkify(lines[0])
    return "".join(f"<p>{linkify(line)}</p>" for line in lines)

def render_education():
    if not educations: return ""
    rows=[]
    # compute min-width in ch
    max_chars = 0
    for ed in educations:
        name_full = ed["NAAM"] + (f" — {ed['INSTITUUT']}" if ed["INSTITUUT"] else "")
        max_chars = max(max_chars, len(name_full))
    min_ch = max_chars + 2
    for ed in educations:
        peri = html.escape(ed["PERIODE"])
        naam = html.escape(ed["NAAM"] + (f" — {ed['INSTITUUT']}" if ed["INSTITUUT"] else ""))
        plaats = html.escape(ed["PLAATS"])
        toel = format_value_for_html(ed["TOELICHTING"])
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name' style='min-width:{min_ch}ch'>{naam}</td><td class='edu-place'>{plaats}</td></tr>")
        if toel:
            rows.append(f"<tr><td class='label'>&nbsp;</td><td class='edu-desc' colspan='2'><div class='tekstblok'>{toel}</div></td></tr>")
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_courses():
    if not courses: return ""
    rows=[]
    for c in courses:
        peri = html.escape(c["PERIODE"])
        items = ", ".join(html.escape(it) for it in c["ITEMS"])
        rows.append(f"<tr><td class='label'>{peri}</td><td class='edu-name' colspan='2'>{items}</td></tr>")
    return "<table class='education-table'>" + "".join(rows) + "</table>"

def render_engagements():
    if not os.path.isdir(engagements_dir): return ""
    parts=[]
    for fname in sorted(os.listdir(engagements_dir), key=extract_year, reverse=True):
        if not fname.endswith(".txt"): continue
        data = parse_engagement(os.path.join(engagements_dir,fname))
        rows=[]
        for k,v in data.items():
            label = html.escape(pretty_label(k))
            rows.append(f"<tr><td class='label'>{label}</td><td class='value'><div class='tekstblok'>{format_value_for_html(v)}</div></td></tr>")
        parts.append("<table class='engagement-table'>" + "".join(rows) + "</table>")
    return "".join(parts)

# assemble blocks in order
blocks_html = []
for b in blocks:
    name = b["NAME"].lower()
    title = html.escape((b["TITLE"] or "").upper())
    content = ""
    if name in ("personal","persoonlijk"):
        content = render_personal()
    elif name in ("education","educations","opleidingen"):
        content = render_education()
    elif name in ("courses","cursussen"):
        content = render_courses()
    elif name in ("courses_short","courses-short","coursesshort"):
        content = render_courses()
    elif name in ("engagements","werkervaring","opdrachten"):
        content = render_engagements()
    else:
        # try to load a block file from blocks/ with same name
        candidate = os.path.join(blocks_dir, name)
        if os.path.isfile(candidate):
            with open(candidate, encoding="utf-8") as bf:
                content = format_value_for_html(bf.read().strip())
        elif os.path.isfile(candidate + ".txt"):
            with open(candidate + ".txt", encoding="utf-8") as bf:
                content = format_value_for_html(bf.read().strip())
    # combine: title (bold uppercase) then content; blocks are separated by a thicker light gray line via CSS
    blocks_html.append(f"<section class='block'><div class='block-title'>{title}</div>{content}</section>")

html_doc = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>CV</title>
<link rel="stylesheet" href="{norm_path_for_html(css_path)}">
</head>
<body>
{"<img src=\"" + html.escape(find_site_logo()) + "\" alt=\"Logo\" class=\"site-logo\" />" if find_site_logo() else ""}
<div class="container">
{"".join(blocks_html)}
<h1>WERKERVARING</h1>
{render_engagements()}
</div>
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("Gegeneerd:", output_file)
