"""Render the synthesized digest markdown into a readable HTML page."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import markdown as md

from synthesize import SECTION_BERLIN, SECTION_ICYMI

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


def _wrap_section(html: str, header_text: str, css_class: str) -> str:
    """Wrap the HTML from a given "<h2>...</h2>" section (through to the next
    <h2> or end of document) in a <div class="css_class">, so specific
    sections (Berlín, Si te lo perdiste) can be styled distinctly."""
    start_tag = f"<h2>{header_text}</h2>"
    start = html.find(start_tag)
    if start == -1:
        return html  # section omitted by the model (e.g. empty ICYMI) -- fine
    next_h2 = html.find("<h2>", start + len(start_tag))
    end = next_h2 if next_h2 != -1 else len(html)
    return html[:start] + f'<div class="{css_class}">' + html[start:end] + "</div>" + html[end:]


def render_html(digest_markdown: str, template_path: Path) -> str:
    content_html = md.markdown(digest_markdown)
    content_html = _wrap_section(content_html, SECTION_BERLIN, "local")
    content_html = _wrap_section(content_html, SECTION_ICYMI, "missing")
    template = template_path.read_text()
    today = _spanish_date(date.today())
    return template.format(date=today, content=content_html)


def save_output(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
