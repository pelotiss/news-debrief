# News Debrief

A personal morning news briefing: pulls today's headlines + free teaser text
from 13 RSS feeds, asks Claude to write one short narrative overview of what's
going on (grouped by topic, not by source), and renders it to a local HTML
page with links back to every source article.

Only the free title/teaser text each RSS feed already publishes is used --
nothing paywalled is scraped.

## Setup

```bash
cd news-debrief
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your own Anthropic API key (get one at
https://console.anthropic.com/settings/keys).

## Run

```bash
source venv/bin/activate
python src/main.py
```

Then open `output/latest.html` in a browser.

## Sources

See `config/sources.yaml`. All 14 originally requested sources were checked;
13 have working RSS feeds. **The Berliner** does not currently expose a
working feed (its `/feed/` endpoint redirects back to the homepage) so it's
left out for now -- add it to `sources.yaml` if you find a working feed URL.

## What's next (not built yet)

- Hosting the page somewhere with a stable URL.
- Automating the daily run (cron).
- Getting it onto a Kobo e-reader (likely via bookmarking the page in Kobo's
  hidden/experimental browser).
