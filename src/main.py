"""Entry point: fetch today's articles, synthesize a digest, render to HTML."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from fetch import fetch_all
from history import load_recent, save_day
from render import render_html, save_output
from synthesize import build_digest

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "sources.yaml"
TEMPLATE_PATH = ROOT / "templates" / "digest.html"
OUTPUT_PATH = ROOT / "output" / "index.html"  # renamed from latest.html for GitHub Pages
HISTORY_DIR = ROOT / "history"
ICYMI_LOOKBACK_DAYS = 7


def main() -> None:
    load_dotenv(ROOT / ".env")

    print("Fetching feeds...")
    articles = fetch_all(CONFIG_PATH)
    print(f"  {len(articles)} items collected from today/this run's window.")

    if not articles:
        print("No articles found -- nothing to summarize. Exiting.")
        return

    print("Loading recent history for the ICYMI section...")
    history = load_recent(HISTORY_DIR, days=ICYMI_LOOKBACK_DAYS)
    print(f"  {len(history)} day(s) of history loaded.")

    print("Asking Claude to write the briefing...")
    digest_markdown = build_digest(articles, history)

    print("Rendering HTML...")
    html = render_html(digest_markdown, TEMPLATE_PATH)
    save_output(html, OUTPUT_PATH)

    print("Saving today's history entry...")
    save_day(HISTORY_DIR, date.today(), digest_markdown, articles)

    print(f"Done. Open {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
