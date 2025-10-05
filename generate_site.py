#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genereer index.html uit txt-bestanden in ./engagements
- Tabel per engagement: [Tag] [ : ] [Tekst]
- Sortering: meest recent eerst (op basis van eerste gevonden jaar in Period/Periode)
- Logo linksboven uit config/config.json ("logo") of eerste file in ./logos
- Geen externe dependencies
"""
import os, re, json, html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DIR_ENG = ROOT / "engagements"
DIR_LOGOS = ROOT / "logos"
DIR_CONFIG = ROOT / "config"
OUT_DIR = ROOT / "docs"
OUT_FILE = OUT_DIR / "index.html"

# ---- hulpfuncties -----------------------------------------------------------

KEYS_ORDER = [
    # eerst de meest gebruikelijke labels (NL/EN varianten), rest volgt in file-volgorde
    "Periode","Period","Role","Functie","Client","Klant","Organisatie","Samenvatting","Summary",
    "Omschrijving","Description","Key Result","Resultaat","Trefwoorden","Tags"
]

def detect_logo():
    # 1) config/config.json met {"logo":"logos/naam.png","title":"..."} (relatief aan repo-root)
    title = "Engagements"
    cfg = DIR_CONFIG / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            title = data.get("title", title)
            logo_path = data.get("logo", "")
            if logo_path:
                p = (ROOT / logo_path).resolve()
                if p.exists():
                    return p, title
        except Exception:
            pass
    # 2) eerste logo in ./logos
    for ext in ("png","jpg","jpeg","svg","gif","webp"):
        files = sorted(DIR_LOGOS.glob(f"*.{ext}"))
        if files:
            return files[0], title
    return None, title

def parse_txt_file(p: Path):
    """
    Verwacht regels 'Key: Value'. Meeregelige waarden toegestaan
    tot volgende 'Key:'-regel. Key-match is case-insensitive.
    """
    data = {}
    current_key = None
    keys_seen_order = []
    pat = re.compile(r"^\s*([^:]+?)\s*:\s*(.*)$")
    with p.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = pat.match(line)
            if m:
                key, val = m.group(1).strip(), m.group(2).strip()
                current_key = key
                if key not in data:
                    keys_seen_order.append(key)
                    data[key] = val
                else:
                    data[key] += ("\n" + val if val else "")
            else:
                # vervolg op vorige key
                if current_key:
                    data[current_key] = (data[current_key] + "\n" + line).strip()
                elif line.strip():
                    # geen key gezien: vang alles onder "Omschrijving"
                    data.setdefault("Omschrijving", "")
                    data["Omschrijving"] = (data["Omschrijving"] + "\n" + line).strip()
    data["_file"] = p.name
    data["_keys_order"] = keys_seen_order
    return data

def year_key(d: dict):
    # pak eerste 4-cijferig jaartal uit "Periode"/"Period" of uit bestandsnaam
    cand = ""
    for k in ("Periode","Period"):
        if k in d and d[k]:
            cand = d[k]
            break
    if not cand:
        cand = d.get("_file","")
    m = re.search(r"(20|19)\d{2}", cand)
    return -(int(m.group(0))) if m else 0

def order_keys_for_table(d: dict):
    # Sorteer keys: eerst KEYS_ORDER (die bestaan), dan overige in oorspronkelijke volgorde
    present = set(d.keys()) - {"_file","_keys_order"}
    first = [k for k in KEYS_ORDER if k in present]
    rest = [k for k in d.get("_keys_order", []) if k not in set(first)]
    # zet Tags/Trefwoorden als laatste mooier
    for tail in ("Tags","Trefwoorden"):
        if tail in first:
            first = [k for k in first if k != tail] + [tail]
        if tail in rest:
            rest = [k for k in rest if k != tail] + [tail]
    return first + [k for k in rest if k not in set(first)]

def esc(x): 
    return html.escape(str(x), quote=True)

def val_to_html(v):
    # meeregelige waarden netjes maken; eenvoudige URL-detectie → link
    if not v:
        return ""
    parts = []
    for line in str(v).splitlines():
        line = line.strip()
        line = re.sub(r"(https?://\S+)", r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', esc(line))
        parts.append(line if line else "<br>")
    return "<br>".join(parts)

def build_table(d: dict):
    rows = []
    for k in order_keys_for_table(d):
        v = d.get(k, "")
        # representatie van "Tags"/"Trefwoorden" als badges
        if k in ("Tags","Trefwoorden"):
            tags = [t.strip() for t in re.split(r"[;,]", v) if t.strip()] if isinstance(v,str) else v
            v_html = " ".join(f'<span class="tag">{esc(t)}</span>' for t in tags) if tags else ""
        else:
            v_html = val_to_html(v)
        rows.append(
            f"<tr><th class='k'>{esc(k)}</th><td class='sep'>:</td><td class='v'>{v_html}</td></tr>"
        )
    return "<table class='engagement'>\n" + "\n".join(rows) + "\n</table>"

# ---- main build -------------------------------------------------------------

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = [parse_txt_file(p) for p in sorted(DIR_ENG.glob("*.txt"))]
    items.sort(key=year_key)  # meest recent eerst (negatief jaar)

    logo_path, title = detect_logo()
    logo_html = ""
    if logo_path and logo_path.exists():
        rel_logo = os.path.relpath(logo_path, OUT_DIR).replace("\\","/")
        logo_html = f'<img class="logo" src="{esc(rel_logo)}" alt="Logo">'

    css = """
    :root{--ink:#0f172a;--muted:#64748b;--line:#e2e8f0;--bg:#f8fafc;--tag:#eef2ff;--tagtxt:#3730a3}
    *{box-sizing:border-box} body{margin:0;font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink)}
    header.site{display:flex;align-items:center;gap:12px;padding:16px;border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
    .logo{height:40px;width:auto;object-fit:contain}
    .title{font-weight:700;font-size:18px;line-height:1}
    .wrap{max-width:1000px;margin:0 auto;padding:20px}
    .list{display:flex;flex-direction:column;gap:16px}
    .card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 1px 2px rgba(0,0,0,.03)}
    table.engagement{width:100%;border-collapse:collapse}
    table.engagement th.k{white-space:nowrap;text-align:left;vertical-align:top;padding:6px 8px;color:var(--muted);width:1%}
    table.engagement td.sep{width:10px;text-align:center;color:var(--muted)}
    table.engagement td.v{padding:6px 0 6px 8px}
    .tag{display:inline-block;background:var(--tag);color:var(--tagtxt);padding:2px 8px;border-radius:999px;font-size:12px;margin-right:6px;margin-bottom:4px;border:1px solid #c7d2fe}
    footer.site{margin:24px 0;color:var(--muted);font-size:12px;text-align:center}
    """

    cards_html = "\n".join(f"<section class='card'>{build_table(d)}</section>" for d in items) if items else "<p>Geen engagements gevonden.</p>"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_doc = f"""<!doctype html>
<html lang="nl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="icon" href="data:,">
<style>{css}</style>
<body>
<header class="site">
  {logo_html}
  <div class="title">{esc(title)}</div>
</header>
<main class="wrap">
  <div class="list">
    {cards_html}
  </div>
</main>
<footer class="site">Gegenereerd op {esc(now)} • Bron: map <code>engagements/</code></footer>
</body></html>"""
    OUT_FILE.write_text(html_doc, encoding="utf-8")
    print(f"[OK] Geschreven: {OUT_FILE}")

if __name__ == "__main__":
    if not DIR_ENG.exists():
        raise SystemExit(f"[ERR] Map ontbreekt: {DIR_ENG}")
    main()
