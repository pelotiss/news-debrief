"""Persist and load daily digest history for the ICYMI ("Si te lo perdiste")
section.

Cross-run memory for the pipeline: GitHub Actions workspaces are ephemeral,
so each run's result (today's digest markdown + the raw articles used) is
written to a JSON file under history/ and committed back to the repo by the
workflow. On the next run, the last N days of files are read back in to give
the synthesizer material for the ICYMI section.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from fetch import Article


def _file_for(history_dir: Path, day: date) -> Path:
    return history_dir / f"{day.isoformat()}.json"


def save_day(
    history_dir: Path, day: date, digest_markdown: str, articles: list[Article]
) -> None:
    history_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": day.isoformat(),
        "digest_markdown": digest_markdown,
        "articles": [
            {
                "source": a.source,
                "title": a.title,
                "link": a.link,
                "teaser": a.teaser,
                "region": a.region,
                "published": a.published.isoformat() if a.published else None,
            }
            for a in articles
        ],
    }
    _file_for(history_dir, day).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2)
    )


def load_recent(
    history_dir: Path, days: int = 7, before: date | None = None
) -> list[dict]:
    """Return up to `days` days of history strictly before `before` (defaults
    to today), oldest first. Missing/corrupt files are silently skipped --
    this also makes the very first run (no history/ directory at all) work
    with zero special-casing."""
    before = before or date.today()
    out = []
    for offset in range(1, days + 1):
        path = _file_for(history_dir, before - timedelta(days=offset))
        if not path.exists():
            continue
        try:
            out.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    out.reverse()
    return out
