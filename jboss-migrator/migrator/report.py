"""Renders the Markdown templates in templates/."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

_env = Environment(loader=FileSystemLoader(TEMPLATES), undefined=StrictUndefined,
                   trim_blocks=False, lstrip_blocks=False, keep_trailing_newline=True)


def render(template: str, **context) -> str:
    return _env.get_template(template).render(**context)


def write(template: str, dest: Path, **context) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render(template, **context), encoding="utf-8")
    return dest
