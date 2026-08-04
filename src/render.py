"""Render the synthesized digest markdown into a readable HTML page."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import markdown as md

_WEEKDAYS_ES = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
]
_MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _spanish_date(d: date) -> str:
    weekday = _WEEKDAYS_ES[d.weekday()]
    month = _MONTHS_ES[d.month - 1]
    return f"{weekday}, {d.day} de {month} de {d.year}"


def render_html(digest_markdown: str, template_path: Path) -> str:
    content_html = md.markdown(digest_markdown)
    template = template_path.read_text()
    today = _spanish_date(date.today())
    return template.format(date=today, content=content_html)


def save_output(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
