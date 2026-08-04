"""Fetch today's items from every configured RSS feed.

Only the title, link, and free teaser/description text from each feed is
kept -- never the full article body -- so paywalled sources are respected
by construction.
"""

from __future__ import annotations

import re
from calendar import timegm
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml

RECENT_WINDOW = timedelta(hours=48)
MAX_PER_SOURCE = 15
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) NewsDebrief/1.0"


@dataclass
class Article:
    source: str
    title: str
    link: str
    teaser: str
    published: datetime | None


def load_sources(config_path: Path) -> list[dict]:
    with config_path.open() as f:
        data = yaml.safe_load(f)
    return data["sources"]


def _clean_teaser(raw: str) -> str:
    """Strip HTML tags feeds sometimes embed in the description field."""
    text = re.sub(r"<[^>]+>", " ", raw or "")
    return re.sub(r"\s+", " ", text).strip()


def _entry_published(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)


def fetch_source(name: str, url: str) -> list[Article]:
    parsed = feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})
    now = datetime.now(timezone.utc)
    cutoff = now - RECENT_WINDOW

    all_articles: list[Article] = []
    for entry in parsed.entries:
        published = _entry_published(entry)
        teaser = _clean_teaser(entry.get("summary", ""))
        all_articles.append(
            Article(
                source=name,
                title=entry.get("title", "").strip(),
                link=entry.get("link", ""),
                teaser=teaser,
                published=published,
            )
        )

    recent = [a for a in all_articles if a.published and a.published >= cutoff]
    if recent:
        # High-volume wire-style feeds (El País, O Globo, Folha...) can publish
        # 100+ items in 48h -- cap to the most recent so the digest stays
        # focused on the day's main stories instead of every minor update.
        recent.sort(key=lambda a: a.published, reverse=True)
        return recent[:MAX_PER_SOURCE]

    # Weekly/monthly publishers won't have anything in the last 48h most days --
    # fall back to their single latest item so they still get a chance to surface.
    dated = [a for a in all_articles if a.published]
    if dated:
        dated.sort(key=lambda a: a.published, reverse=True)
        return dated[:1]
    return all_articles[:1]


def fetch_all(config_path: Path) -> list[Article]:
    articles: list[Article] = []
    for source in load_sources(config_path):
        try:
            articles.extend(fetch_source(source["name"], source["url"]))
        except Exception as exc:  # noqa: BLE001 -- one bad feed shouldn't kill the run
            print(f"  [warn] failed to fetch {source['name']}: {exc}")
    return articles
