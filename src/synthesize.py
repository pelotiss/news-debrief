"""Turn today's fetched articles into one narrative morning-briefing digest."""

from __future__ import annotations

import os

from anthropic import Anthropic

from fetch import Article

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """You are writing a personal morning news briefing for one reader.

You will be given a list of today's headlines and short teaser snippets pulled \
from RSS feeds across ~13 newspapers and magazines (English, Spanish, French, \
German, and Portuguese sources). Some are daily papers, some weekly/monthly \
magazines.

Write a short briefing in Spanish, in your own words, organized by topic or \
story rather than by source -- group related headlines from different outlets \
into a single point where they cover the same story. Cover the main things \
worth knowing about today. Keep it skimmable: a couple of sentences per topic \
is enough, not an essay.

Every point must link back to the article(s) it's based on, inline, as \
markdown links using the exact URLs provided -- e.g. "...segun [El País]\
(https://...)." Do not invent facts beyond what the provided titles/teasers \
support, and do not quote the teasers at length -- paraphrase in your own words.

Output plain markdown only: a short paragraph or two, or a few bullet points \
per topic. No preamble, no headers like "Morning Briefing", just the content.
"""


def _format_items(articles: list[Article]) -> str:
    lines = []
    for a in articles:
        teaser = a.teaser[:400] if a.teaser else "(no teaser available)"
        lines.append(f"- [{a.source}] {a.title}\n  teaser: {teaser}\n  url: {a.link}")
    return "\n".join(lines)


def build_digest(articles: list[Article]) -> str:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    items_text = _format_items(articles)
    user_prompt = f"Today's items:\n\n{items_text}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
