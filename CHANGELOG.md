# Changelog

Human-readable log of what changed in the onboarding prototype, for product review. Updated at each local commit — most recent first.

## 2026-09-25 — WeWork India fork

A new fork for WeWork India, built on the current base code (the Google Sheet driven build) with the video support from an earlier fork. It starts with a clean git history of its own.

**The brand.** Everything is keyed on `wework.co.in`: Brand Memory, the setup rail, the workspace badge, the deck sidebar and the welcome line. The logo is WeWork's own wordmark, lifted from the vector on their site, not redrawn. The kit is black, white, WeWork blue and the yellow they use for ratings, all read off the site's CSS. The intro card copy is untouched; only its three illustrations and wash were regraded from the previous brand green to WeWork blue, and the story rings were recoloured to match.

**What WeWork actually is, and what that changed.** WeWork sells space, not products, and has no commerce platform. So the catalog is its 79 centres (the setup line now says "79 centres"), and Shopify is gone from every surface: the feed and deck connect cards and the Brand Memory connect row name Sanity, the CMS their site images come from; the rail flyouts and search list Sanity, Meta Ads, Google Ads, LinkedIn Ads and MoEngage; Signals reads member and booking records through MoEngage and WhatsApp instead of Shopify and Klaviyo.

**Twenty posts, every one a recommendation waiting for approval, and every number in them read off wework.co.in on 25 September.**

- **Catalog.** Tag each centre photo to the product it sells. The homepage counts 79 centres but the sitemap has 65 centre pages, so 14 have no page of their own.
- **Creatives.** Run the line-art set as one campaign. Cut the commute film to a 15-second Reel. Swap the empty lounge for the same lounge with a team in it. Run the after-hours set for founders. Shoot people working, not rooms waiting. Give Members Day a rooftop yoga morning. Lock the December set now.
- **Ads.** Four Google Ads conversion IDs fire on one site, so a booking can count twice. Confirm the ₹9,999 in the membership concept before it runs, because no page on the site shows that price. Point the meeting-room ad at the ₹2,000 hour. Take the enterprise frame to LinkedIn, where the Insight Tag is already live.
- **Storefront.** Three pages quote three starting prices for Virtual Office (₹999, Rs. 1099 and ₹2,499). The Pavilion lists its day pass at ₹600 when a first visit with PASS35 costs ₹390. Open The Pavilion page on the walkthrough film that only the homepage plays.
- **Visibility.** All 65 centre pages have meta descriptions of 490 characters or more (median 737) when search shows about 160. The 8 city Day Pass pages reach crawlers with no page title. llms.txt is a third blog posts, has 17 entries with one identical title, and lists the checkout under an error message.

**Imagery.** All from the WeWork Drive folder. Catalog cards use the real centre photos exactly as shot. Creative cards use the POC Aug directions and the Usecase sets; posters are kept whole, never cropped through a headline. Frames that quote the unconfirmed ₹9,999 are left out everywhere except the card that asks to confirm it. Every the previous brand image has been deleted.

**Known limits.**
- The Signals counts (members, reachable, RSVPs) and source volumes are placeholders; nobody has connected WeWork's member data.
- There is no AI-engine prompt audit for WeWork, so the visibility cards carry site facts only, with no share-of-voice numbers.
- Sanity as the CMS is inferred from the site bundle, not confirmed by WeWork.
- The Drive's Meta ads for an Ahmedabad launch and the "Merry Beginning in Ahmedabad" set are not used: the site lists 8 cities and no Ahmedabad centre. One Drive concept that pastiches a well-known film scene is also left out, as is the Drive ad with the "communiy" typo.
- The ₹390 day pass assumes PASS35 applies to The Pavilion's ₹600 price; the site states the code, not where it applies.
- Stories are ShopOS's own copy apart from Trends and Popular ads, which are written for WeWork.
- The introductory post sequence is still to be decided.
- The WeWork-1 tab is not in the Brand Feeds sheet yet; the feed syncs from `data/wework-seed.xlsx` until it is.
