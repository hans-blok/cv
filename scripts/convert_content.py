"""One-time migration script: convert content/*.txt (custom pipe-delimited DSL)
into docs/includes/*.md fragments for the MkDocs-based site.

Reuses the parsing/formatting functions from generate_site.py so the rendered
HTML fragments are byte-for-byte consistent with what the legacy generator
produced (minus base64 image embedding, which is replaced by static asset
references).

Re-runnable: safe to run again if content/*.txt changes during the transition.
"""
import sys
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import generate_site as gs  # noqa: E402

DOCS_DIR = ROOT / "docs"
INCLUDES_DIR = DOCS_DIR / "includes"
ENGAGEMENTS_OUT_DIR = INCLUDES_DIR / "engagements"


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("Wrote", path.relative_to(ROOT))


def convert_personal_data():
    personal = gs.parse_personal(gs.PERSONAL_DATA_FILE)
    order_keys = ["Naam", "Roepnaam", "Woonplaats", "Geboortedatum", "Telefoon", "Beschikbaar per ", "Functie"]
    rows = []
    handled = set()
    for key in order_keys:
        if key in personal:
            label = gs.resolve_label(key)
            rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{gs.format_value_for_html(personal[key])}</div></td></tr>")
            handled.add(key)
    for k, v in personal.items():
        if k in handled:
            continue
        label = gs.resolve_label(k.strip().strip("`"))
        rows.append(f"<tr><td class='label'>{html.escape(label)}</td><td class='value'><div class='tekstblok'>{gs.format_value_for_html(v)}</div></td></tr>")
    table = "<table class='personal-table'>" + "".join(rows) + "</table>"
    photo = '<img src="assets/img/profile-photo.png" alt="Foto" class="profile-photo">'
    fragment = f'<div class="personal-block"><div class="personal-table-wrap">{table}</div>{photo}</div>'
    write(INCLUDES_DIR / "personal-data.md", fragment)


def convert_personal_text():
    txt = gs.PERSONAL_TEXT_FILE.read_text(encoding="utf-8")
    fragment = f"<div class='tekstblok'>{gs.format_value_for_html(txt)}</div>"
    write(INCLUDES_DIR / "personal-text.md", fragment)


def convert_educations():
    eds = gs.parse_educations(gs.EDUCATION_FILE)
    write(INCLUDES_DIR / "educations.md", gs.render_education_block(eds))


def convert_certifications():
    certs = gs.parse_certifications(gs.CERTIFICATIONS_FILE)
    write(INCLUDES_DIR / "certifications.md", gs.render_certifications_block(certs))


def convert_courses():
    courses = gs.parse_courses(gs.COURSES_FILE)
    write(INCLUDES_DIR / "courses.md", gs.render_courses_block(courses))


def convert_courses_short():
    courses_short = gs.parse_courses_short(gs.COURSES_SHORT_FILE)
    write(INCLUDES_DIR / "courses-short.md", gs.render_courses_short_block(courses_short))


CONTACT_ITEMS = [
    ("linkedin_url", "linkedin", "https://", "LinkedIn"),
    ("linkedin", "linkedin", "https://", "LinkedIn"),
    ("website_url", "website", "https://", "Website"),
    ("website", "website", "https://", "Website"),
    ("github_url", "github", "https://", "GitHub"),
    ("github", "github", "https://", "GitHub"),
    ("phone_nr", "phone", "tel:", ""),
    ("phone-nr", "phone", "tel:", ""),
    ("telefoon", "phone", "tel:", ""),
    ("telephone", "phone", "tel:", ""),
    ("e-mail", "email", "mailto:", ""),
    ("email", "email", "mailto:", ""),
]


def convert_urls_contact():
    urls = gs.parse_urls(gs.URLS_FILE)
    out = []
    rendered = set()
    for key, val in urls.items():
        if not val:
            continue
        key_lower = key.strip("'\"").lower().replace("_", "-")
        if key_lower in rendered:
            continue
        icon_name = None
        href_prefix = ""
        display_label = ""
        for item_key, item_icon, item_prefix, item_label in CONTACT_ITEMS:
            if key_lower == item_key.lower().replace("_", "-"):
                icon_name = item_icon
                href_prefix = item_prefix
                display_label = item_label if item_label else val
                rendered.add(key_lower)
                for k, i, p, l in CONTACT_ITEMS:
                    if i == item_icon:
                        rendered.add(k.lower().replace("_", "-"))
                break
        if not icon_name:
            icon_name = key_lower
            href_prefix = ""
            display_label = val
            rendered.add(key_lower)
        href = val if val.startswith(("http://", "https://", "tel:", "mailto:")) else href_prefix + val
        out.append(f'<a href="{html.escape(href)}" class="contact-link" data-type="{icon_name}" title="{html.escape(val)}"><span class="contact-text">{html.escape(display_label)}</span></a>')
    write(INCLUDES_DIR / "urls-contact.md", "\n".join(out))


def convert_engagements():
    if not gs.ENGAGEMENTS_DIR.is_dir():
        return
    for f in sorted(gs.ENGAGEMENTS_DIR.iterdir(), key=lambda p: p.name, reverse=True):
        if not f.is_file() or f.suffix.lower() != ".txt":
            continue
        data = gs.parse_engagement_file(f)
        periode = data.get("periode") or data.get("PERIODE") or ""
        fragment_html = gs.render_one_engagement(f)
        fragment = f"<!-- periode: {periode} -->\n{fragment_html}"
        out_path = ENGAGEMENTS_OUT_DIR / (f.stem + ".md")
        write(out_path, fragment)


def main():
    convert_personal_data()
    convert_personal_text()
    convert_educations()
    convert_certifications()
    convert_courses()
    convert_courses_short()
    convert_urls_contact()
    convert_engagements()


if __name__ == "__main__":
    main()
