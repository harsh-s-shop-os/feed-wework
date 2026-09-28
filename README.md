# ShopOS Feed — WeWork India fork

A single-page prototype of the ShopOS Feed — URL onboarding, live setup, the feed,
and the Pro deck with a Signals column — branded for **WeWork India** (wework.co.in).
No build step, no framework, no dependencies.

Built from the base prototype (the Google Sheet driven build), with the looping video support ported from an earlier fork. The git history starts fresh at this fork; none of the the previous brand history is carried.

## The brand, as read off the live site

- **Logo:** the real WeWork wordmark path, taken from the footer SVG on wework.co.in
  (`assets/ww-logo.svg`), and the "we" roundel built from the same path for the badge.
- **Palette:** black `#000000`, white `#FFFFFF`, WeWork blue `#0000FF` (the site's link
  and accent colour, `--color-blue-700`) and yellow `#FFE40D` (its rating stars).
- **Type:** WeWork Serif for headlines, Apercu for body, per the site's CSS. Neither is
  bundled; the brand kit card falls back to Georgia.
- **Stack:** Next.js with images that originate in Sanity (asset ids and `cdn.sanity.io`
  in the bundle), served through their own CloudFront. No commerce platform: booking and
  checkout are their own. Tag Manager carries Meta, four Google Ads conversion IDs,
  LinkedIn Insight, Microsoft Ads, Taboola, X, GA4 and Clarity; MoEngage and Mixpanel run
  in the app. Every connector surface in the prototype (connect cards, Signals sources,
  rail flyouts, search) names this stack.

## Imagery

All from ShopOS's WeWork Drive folder, art-directed in two registers:

- **Catalog / storefront** (`ww-centre-*`): the real centre photography, as shot.
  Wide, eye-level, daylight and warm practicals, whole room in frame, true colour.
  Nothing is added to these, because a listing has to show the room as it is.
- **Campaign / creative** (`ww-ad-*`, `ww-people-*`, `ww-yoga-*`, `ww-xmas-*`): the
  POC Aug directions and the Usecase sets. Warm, lived-in, people mid-conversation,
  greenery, serif headline with a blue emphasis word, wordmark at the foot. Posters are
  kept whole and squared with their own blurred extension, so no headline or logo is cut.

Video: the Drive's commute film (cut to 15 s, square) and the homepage walkthrough film
from wework.co.in, each as webm (first) and mp4, with a poster frame.

## Content comes from the Brand Feeds sheet

Posts, deck cards and Brand Memory load from `data/feed-data.js`, written by
`tools/sync_sheet.py`. This fork reads one tab, **WeWork-1** (`tools/sheet.config.json`).
That tab does not exist in the Brand Feeds sheet yet: its seed is `data/wework-seed.xlsx`.

    python3 tools/sync_sheet.py --file data/wework-seed.xlsx   # works today
    python3 tools/sync_sheet.py                                # once WeWork-1 is in the sheet

Import the seed as a new tab named `WeWork-1` in the Brand Feeds sheet
(https://docs.google.com/spreadsheets/d/1KKs-1639ns-eRO9PxOjMPK2vw_W9tFUmG0u3SZuwP6g)
and the live sync takes over. The brand block has one new row, **Catalog unit**, so the
setup line reads "79 centres" rather than "79 products".

## Run it locally

    python3 -m http.server 5173

Then open http://localhost:5173. Opening `index.html` directly also works.

## Deploying to Vercel

It is a static site: `npx vercel`, or import the repo at vercel.com with framework
preset "Other", no build command, output directory `.`.
