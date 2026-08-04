# News Debrief

A personal morning news briefing for a Berlin-based reader: pulls today's
headlines + free teaser text from RSS feeds, asks Claude to write a short
digest split into three sections -- **Berlín** (transit/traffic disruptions
and Berlin state-level or EU-level law/regulation changes that could
plausibly affect the reader), **Mundo** (everything else, grouped by topic
rather than by source), and **Si te lo perdiste** (an "in case you missed
it" recap of still-open stories from the last 7 days) -- and renders it to
an HTML page with links back to every source article.

Only the free title/teaser text each RSS feed already publishes is used --
nothing paywalled is scraped.

**Known limitation:** there is no clean, dedicated RSS feed for live Berlin
transit disruptions (VBB's disruption data sits behind a registration-gated
API; BVG's traffic page is JS-rendered, no feed). Commute alerts in the
Berlín section only surface when a Berlin news source (e.g. Tagesspiegel)
actually reports on a strike or closure -- this is not a real-time transit
status feed.

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

Then open `output/index.html` in a browser.

## Sources

See `config/sources.yaml`. 14 sources have confirmed working RSS feeds,
including Tagesspiegel (Berlin-local, tagged `region: berlin`). **The
Berliner** does not currently expose a working feed (its `/feed/` endpoint
redirects back to the homepage) so it's left out for now. A few more Berlin
sources (rbb24, Berliner Zeitung, BZ Berlin) are listed commented-out in
`sources.yaml` -- their feed URLs weren't reachable from an automated
fetch (likely bot-blocking) and need a human browser check before being
enabled.

Sources tagged `region: berlin` are treated as a *hint* that a source is
Berlin-local for the digest's "Berlín" section -- it doesn't mean every item
from that source is local; most of what these outlets publish is still
general/national news.

## Automation & hosting

A GitHub Actions workflow (`.github/workflows/digest.yml`) runs the pipeline
daily (~05:00 UTC) and publishes `output/` to GitHub Pages, so the digest is
ready without needing your machine on. It also commits each day's
`history/YYYY-MM-DD.json` (digest + articles) back to the repo, which feeds
the "Si te lo perdiste" section on later runs.

One-time manual setup required (not automatable):

1. Decide public vs. private repo -- GitHub Pages on a private repo needs a
   paid GitHub plan.
2. `git remote add origin <your-repo-url>` and `git push -u origin main`.
3. Repo Settings → Pages → Build and deployment → Source → **GitHub Actions**.
4. Repo Settings → Secrets and variables → Actions → add `ANTHROPIC_API_KEY`.
5. Repo Settings → Actions → General → Workflow permissions → ensure "Read
   and write permissions" is enabled (needed for the workflow's history
   commit step to push successfully).
6. Verify the commented-out Berlin source feed URLs in `sources.yaml` in a
   real browser before enabling them.

Note: GitHub Actions cron is always UTC and doesn't shift for daylight
saving time, so the Berlin-local delivery time drifts by an hour across the
year -- adjust the cron in `digest.yml` around the March/October changeovers
if that matters to you.

## What's next (not built yet)

- Getting it onto a Kobo e-reader (likely via bookmarking the Pages URL in
  Kobo's hidden/experimental browser).
- A real transit-disruption feed integration (see "Known limitation" above)
  if VBB/BVG ever expose one without requiring API registration.
