"""Turn today's fetched articles into one narrative morning-briefing digest."""

from __future__ import annotations

import os

from anthropic import Anthropic

from fetch import Article

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 3000  # was 2000 -- three sections + ICYMI need more room

SECTION_BERLIN = "Berlín"
SECTION_MUNDO = "Mundo"
SECTION_ICYMI = "Si te lo perdiste"

SYSTEM_PROMPT = f"""You are writing a personal morning news briefing for one reader who \
lives in Berlin and reads this on their commute.

You will be given two things:
1. Today's headlines and short teaser snippets pulled from RSS feeds across \
~15 newspapers and magazines (English, Spanish, French, German, and \
Portuguese sources). A few of these sources are Berlin-local (marked \
"(fuente local de Berlín)" next to the source name) -- most of what those \
sources publish is still general/national news and should be treated like \
any other story, not automatically local.
2. A short history of the last several days' briefings, for the "{SECTION_ICYMI}" \
section only.

Write the briefing in Spanish, in your own words, organized into exactly \
these three sections, in this order, using markdown "##" headers with these \
exact titles:

## {SECTION_BERLIN}
Anything today directly relevant to the reader as a Berlin resident: \
(a) train/transit/traffic disruptions that could affect a commute (strikes, \
closures, major delays -- U-Bahn, S-Bahn, BVG, DB regional, or major roads), \
and (b) law or regulation changes that could actually affect him -- Berlin \
Senate/state-level decisions and local ordinances, AND EU-level regulations \
or directives (e.g. consumer, tenant, tax, data/privacy rules) that apply \
EU-wide. Skip abstract political debate that doesn't actually change \
anything for a resident -- only include law/regulation items with concrete, \
plausible personal relevance. Call these out explicitly even if they're \
minor items that would otherwise be skipped -- a single-sentence bullet is \
fine. If there is genuinely nothing Berlin-relevant today, write one line \
saying so rather than omitting the section.

## {SECTION_MUNDO}
Everything else worth knowing about today, grouped by topic/story rather \
than by source: skimmable, a couple of sentences per topic.

## {SECTION_ICYMI}
Look at the history of the last several days provided below. Resurface at \
most a handful of stories that are still relevant, ongoing, or unresolved \
(e.g. an open strike, an unresolved investigation, a regulation still \
moving through approval) and that a reader who skimmed daily might have \
missed or forgotten. Do not repeat anything you already wrote about in \
"{SECTION_BERLIN}" or "{SECTION_MUNDO}" above -- this section is only for \
older, still-open threads. If nothing from the history genuinely qualifies, \
omit this section entirely (don't write an empty or padded one just to \
fill it).

Every point in every section must link back to the article(s) it's based \
on, inline, as markdown links using the exact URLs provided -- e.g. \
"...segun [El País](https://...)." Do not invent facts beyond what the \
provided titles/teasers support, and do not quote teasers at length -- \
paraphrase in your own words.

Output plain markdown only, starting directly with "## {SECTION_BERLIN}". \
No preamble before it.
"""


def _format_items(articles: list[Article]) -> str:
    lines = []
    for a in articles:
        teaser = a.teaser[:400] if a.teaser else "(no teaser available)"
        tag = " (fuente local de Berlín)" if a.region == "berlin" else ""
        lines.append(f"- [{a.source}]{tag} {a.title}\n  teaser: {teaser}\n  url: {a.link}")
    return "\n".join(lines)


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(sin historial disponible todavía -- es de las primeras ejecuciones.)"
    chunks = [f"### {day['date']}\n{day['digest_markdown']}" for day in history]
    return "\n\n".join(chunks)


def build_digest(articles: list[Article], history: list[dict] | None = None) -> str:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    items_text = _format_items(articles)
    history_text = _format_history(history or [])
    user_prompt = (
        f"Artículos de hoy:\n\n{items_text}\n\n"
        f"Historial de los últimos días (solo para '{SECTION_ICYMI}' -- "
        f"no repitas nada de esto en '{SECTION_BERLIN}' o '{SECTION_MUNDO}'):\n\n"
        f"{history_text}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
