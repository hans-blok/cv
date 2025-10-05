#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genereer docs/index.html uit engagements/*.txt
- Layout: tabel per engagement met 3 kolommen: [KOPJE] [ : ] [TEKST]
- Kopjes + volgorde komen uit config/config_tags.txt (linkerzijde = mogelijke keys, rechterzijde = label)
- Sorteert op meest recente jaar uit Periode/Period of bestandsnaam
- Logo linksboven (config/config.json -> "logo") of 1e bestand in logos/
- Verwijdert placeholders als [tag01], [tag12], etc.
- Zet lijstjes met -, *, • om naar <ul><li>…</li></ul>
- Geen externe packages nodig
"""
import os, re, json, html
from pathlib import Path
from datetime import datetime

ROOT       = Path(__file__).resolve().parent
DIR_ENG    = ROOT / "engagements"
DIR_LOGOS  = ROOT / "logos"
DIR_CONFIG = ROOT / "config"
OUT_DIR    = ROOT / "docs"
OUT_FILE   = OUT_DIR / "index.html"

# ---------- helpers ----------------------------------------------------------

def read_config_tags():
    """
    Leest config/config_tags.txt
    Formaat per regel: 'key1|key2 = LABEL'
    Retourneert list van tuples: [( [bronkeys], LABEL ), ...]
    """
    p = DIR_CONFIG / "config_tags.txt"
    if not p.exists():
        # fallback default
        return [
            (["Periode","Period"], "PERIODE"),
            (["Bedrijf","Client","Organisatie"], "BEDRIJF"),
            (["Functie","Role"], "FUNCTIE"),
            (["Taakomschrijving en verantwoordelijkheid","Omschrijving","Summary"], "TAAKOMSCHRIJVING EN VERANTWOORDELIJKHEID"),
            (["Belangrijkste prestaties","Key Result"], "BELANGRIJKSTE PRESTATIES"),
            (["Trefwoorden","Tags"], "TREFWOORDEN"),
        ]
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    pairs = []
    for ln in lines:
        m = re.match(r"^(.*?)\s*=\s*(.+)$", ln)
        if not m:
            continue
        left, right = m.group(1).strip(), m.group(2).strip()
        keys = [k.strip() for k in left.split("|") if k.strip()]
        pairs.append((keys, right))
    return pairs

def detect_logo_and_title():
    title = "Engagements"
    cfg = DIR_CONFIG / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            title = data.get("title", title)
            if data.get("logo"):
                p = (ROOT / data["logo"]).resolve()
                if p.exists():
                    return p, title
        except Exception:
            pass
    # 1e logo in logos/
    for ext in ("png","jpg","jpeg","svg","gif","webp"):
        files = sorted(DIR_LOGOS.glob(f"*.{ext}"))
        if files:
            return files[0], title
    return None, title

def parse_txt(p: Path):
    """Parse key: value; meeregelig; case-insensitive keys."""
    data = {}
    cur = None
    pat = re.compile(r"^\s*([^:]+?)\s*:\s*(.*)$")
    txt = p.read_text(encoding="utf-8")
    # strip [tagNN] placeholders overal
    txt = re.sub(r"\[tag\d{2}\]", "", txt, flags=re.IGNORECASE)
    for raw in txt.splitlines():
        m = pat.match(raw)
        if m:
            k, v = m.group(1).strip(), m.group(2).strip()
            cur = k
            data.setdefault(k, "")
            if data[k]:
                data[k] += "\n" + v
            else:
                data[k] = v
        else:
            if cur:
                data[cur] = (data[cur] + "\n" + raw).strip()
    data["_file"] = p.name
    return data

def bullets_to_html(text: str) -> str:
    """Zet lines met -, *, • om naar <ul>…</ul>, behoudt overige regels met <br>."""
    if not text: return ""
    lines = [ln.strip() for ln in str(text).splitlines()]
    out = []
    in_ul = False
    for ln in lines:
        # detecteer bullet
        m = re.match(r"^(\u2022|\*|\-)\s+(.*)$", ln)  # • of * of -
        if m:
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{linkify(m.group(2))}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(linkify(ln) if ln else "<br>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)

def linkify(s: str) -> str:
    # simpele URL -> <a> vervanging
    s = html.escape(s, quote=True)
    return re.sub(r"(https?://\S+)", r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', s)

def year_sort_key(d: dict):
    # pak eerste jaar uit Periode/Period of uit bestandsnaam
    cand = ""
    for k in ("Periode","Period"):
        # zoek case-insensitive
        for dk in d.keys():
            if dk.lower() == k.lower():
                cand = d[dk]
                break
        if cand: break
    if not cand:
        cand = d.get("_file","")
    m = re.search(r"(20|19)\d{2}", str(cand))
    return -(int(m.group(0))) if m else 0

def pick_value(d: dict, keys_candidates):
    """Zoek value in d voor één van de candidate keys (case-insensitive)."""
    lowmap = {k.lower(): v for k, v in d.items()}
    for k in keys_candidates:
        v = lowmap.get(k.lower())
        if v is not None and str(v).strip():
            return v
    return ""

# ---------- build ------------------------------------------------------------

def build_html(items, mappings, logo_path, title):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    css = """
    :root{--ink:#0f172a;--muted:#475569;--line:#cbd5e1;--bg:#f8fafc}
    *{box-sizing:border-box}body{margin:0;font-family:Segoe UI,Inter,Arial,sans-serif;background:var(--bg);color:var(--ink)}
    header.site{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
    .logo{height:42px;object-fit:contain}
    .title{font-weight:700;font-size:18px}
    main.wrap{max-width:1100px;margin:0 auto;padding:24px 20px}
    .card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin:0 0 16px 0;overflow:hidden}
    table.cv{width:100%;border-collapse:collapse}
    table.cv tr{border-bottom:1px solid #eef2f7}
    table.cv tr:last-child{border-bottom:none}
    table.cv th, table.cv td{padding:10px 12px;vertical-align:top}
    table.cv th.k{width:280px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.3px}
    table.cv td.sep{width:16px;text-align:center;color:var(--muted)}
    table.cv td.v{width:auto}
    ul{margin:.3em 0 .6em 1.2em}
    li{margin:.15em 0}
    a{color:#0ea5e9;text-decoration:none} a:hover{text-decoration:underline}
    footer.site{margin:18px 0;color:#64748b;font-size:12px;text-align:center}
    """

    def table_for(d):
        # bouw rijen in volgorde van mappings
        rows = []
        for keys, label in mappings:
            raw = pick_value(d, keys)
            if not raw:
                continue
            # verwijder eventuele [tagNN] die alsnog zouden zijn blijven staan
            raw = re.sub(r"\[tag\d{2}\]", "", raw, flags=re.IGNORECASE).strip()
            # bullets -> ul, anders br's
            if re.search(r"^(\u2022|\*|\-)\s+", raw, flags=re.MULTILINE):
                vhtml = bullets_to_html(raw)
            else:
                vhtml = "<br>".join(linkify(x.strip()) if x.strip() else "<br>" for x in raw.splitlines())
            rows.append(f"<tr><th class='k'>{html.escape(label)}</th><td class='sep'>:</td><td class='v'>{vhtml}</td></tr>")
        return "<table class='cv'>\n" + "\n".join(rows) + "\n</table>"

    # logo en title
    logo_html = ""
    if logo_path and logo_path.exists():
        rel = os.path.relpath(logo_path, OUT_DIR).replace("\\","/")
        logo_html = f'<img class="logo" src="{html.escape(rel)}" alt="Logo">'

    cards = "\n".join(f"<section class='card'>{table_for(d)}</section>" for d in items) if items else "<p>Geen items gevonden.</p>"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html_doc = f"""<!doctype html>
<html lang="nl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="data:,">
<style>{css}</style>
<body>
<header class="site">{logo_html}<div class="title">{html.escape(title)}</div></header>
<main class="wrap">
  {cards}
</main>
<footer class="site">Gegenereerd op {html.escape(now)} • Bron: <code>engagements/</code> • Layout: config/config_tags.txt</footer>
</body></html>"""
    OUT_FILE.write_text(html_doc, encoding="utf-8")
    print(f"[OK] Geschreven: {OUT_FILE}")

def main():
    if not DIR_ENG.exists():
        raise SystemExit(f"[ERR] Map ontbreekt: {DIR_ENG}")
    items = [parse_txt(p) for p in sorted(DIR_ENG.glob("*.txt"))]
    items.sort(key=year_sort_key)  # meest recent eerst
    mappings = read_config_tags()
    logo_path, title = detect_logo_and_title()
    build_html(items, mappings, logo_path, title)

if __name__ == "__main__":
    main()
