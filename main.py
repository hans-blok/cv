"""mkdocs-macros-plugin hook module (module_name: main) + native MkDocs hook.

This is the ONLY place technical logic lives for turning docs/data/**
(plain YAML/Markdown content, safe for non-technical editors) into the
HTML structure defined by templates/*.html (owns all CSS classes).
"""
from pathlib import Path

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "docs" / "data"
TEMPLATES_DIR = ROOT / "templates"

jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
jinja_env.filters["markdown"] = lambda text: md.markdown(text.strip()) if text else ""


def load_yaml(name):
    return yaml.safe_load((DATA_DIR / name).read_text(encoding="utf-8"))


def define_env(env):
    """mkdocs-macros-plugin hook: registers macros usable as {{ macro() }} in docs/*.md"""

    @env.macro
    def render_personal_data():
        data = load_yaml("personal-data.yml")
        return jinja_env.get_template("personal_data.html").render(**data)

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
        eng_dir = DATA_DIR / "engagements"
        files = sorted(
            eng_dir.glob("*.yml"),
            key=lambda p: yaml.safe_load(p.read_text(encoding="utf-8"))["order"],
            reverse=True,
        )
        items = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in files]
        return jinja_env.get_template("engagement_item.html").render(items=items)


def on_env(env, config, files):
    """Native MkDocs hook (separate mechanism from mkdocs-macros-plugin's define_env
    above): makes the contact sidebar available to overrides/main.html, the page
    shell template, which is rendered outside mkdocs-macros-plugin's per-page
    macro context.
    """
    links = load_yaml("contact.yml")
    env.globals["contact_sidebar_html"] = jinja_env.get_template("contact_sidebar.html").render(links=links)
    return env
