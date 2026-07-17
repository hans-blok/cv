"""mkdocs-macros-plugin hook module (module_name: main) + native MkDocs hook.

This is the ONLY place technical logic lives for turning docs/data/**
(plain YAML/Markdown content, safe for non-technical editors) into the
HTML structure defined by templates/*.html (owns all CSS classes).
"""
from datetime import datetime, timezone
from pathlib import Path

import markdown as md
import yaml
from babel.dates import format_date
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "docs" / "data"
TEMPLATES_DIR = ROOT / "templates"

jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
jinja_env.filters["markdown"] = lambda text: md.markdown(text.strip()) if text else ""


def load_yaml(name):
    return yaml.safe_load((DATA_DIR / name).read_text(encoding="utf-8"))


def load_engagements():
    """All engagement records, newest first, sorted by their explicit `order` field."""
    eng_dir = DATA_DIR / "engagements"
    files = sorted(
        eng_dir.glob("*.yml"),
        key=lambda p: yaml.safe_load(p.read_text(encoding="utf-8"))["order"],
        reverse=True,
    )
    return [yaml.safe_load(f.read_text(encoding="utf-8")) for f in files]


def compute_experience_years(engagements):
    """Years since the earliest engagement's start year - a single computed
    number, so it never has to be hand-maintained in sync with the data."""
    years = [e["order"] // 10000 for e in engagements if e.get("order")]
    if not years:
        return None
    return datetime.now().year - min(years)


def define_env(env):
    """mkdocs-macros-plugin hook: registers macros usable as {{ macro() }} in docs/*.md"""

    @env.macro
    def render_personal_data():
        data = load_yaml("personal-data.yml")
        return jinja_env.get_template("personal_data.html").render(**data)

    @env.macro
    def experience_years():
        """Years since the earliest engagement's start year. Not currently
        wired into any template/page - available to call from docs/*.md or a
        template (e.g. {{ experience_years() }}) if/when wanted."""
        return compute_experience_years(load_engagements())

    @env.macro
    def render_personal_text():
        text = (DATA_DIR / "personal-text.md").read_text(encoding="utf-8")
        return f"<div class='tekstblok'>{env.render(text)}</div>"

    @env.macro
    def render_education_table(source, bold=False):
        rows = load_yaml(f"{source}.yml")
        return jinja_env.get_template("education_table.html").render(rows=rows, bold=bold)

    @env.macro
    def render_courses(source):
        groups = load_yaml(f"{source}.yml")
        return jinja_env.get_template("course_table.html").render(groups=groups)

    @env.macro
    def render_engagements():
        return jinja_env.get_template("engagement_item.html").render(items=load_engagements())

    @env.macro
    def render_expertise_tags():
        """Deduplicated tag list from every engagement's keywords plus every
        certification name - a single scannable summary derived entirely from
        existing content, nothing hand-authored twice."""
        seen = set()
        tags = []

        def add(raw):
            tag = (raw or "").strip()
            key = tag.lower()
            if tag and key not in seen:
                seen.add(key)
                tags.append(tag)

        for engagement in load_engagements():
            for kw in (engagement.get("keywords") or "").split(","):
                add(kw)
        for cert in load_yaml("certifications.yml") or []:
            add(cert.get("name", ""))

        return jinja_env.get_template("expertise_tags.html").render(tags=tags)


def on_env(env, config, files):
    """Native MkDocs hook (separate mechanism from mkdocs-macros-plugin's define_env
    above): makes the contact sidebar available to overrides/main.html, the page
    shell template, which is rendered outside mkdocs-macros-plugin's per-page
    macro context.
    """
    links = load_yaml("contact.yml")
    env.globals["contact_sidebar_html"] = jinja_env.get_template("contact_sidebar.html").render(links=links)

    # Single source of truth for "today", computed once per build, so the
    # visible publication date and the PDF download filename can never drift
    # apart. Dutch month name via Babel's CLDR data - locale-independent
    # (doesn't rely on the OS/browser locale) and no hardcoded month names.
    today = datetime.now(timezone.utc).date()
    env.globals["publicatiedatum_nl"] = format_date(today, format="d MMMM y", locale="nl_NL")
    env.globals["publicatiedatum_iso"] = today.isoformat()
    env.globals["publicatiedatum_spaced"] = today.strftime("%Y %m %d")
    return env
