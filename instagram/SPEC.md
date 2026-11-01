# E2A Instagram Autonomous Manager — Specification (authoritative)

Self-contained spec derived from the project brief. Repo: `e2abasketball-droid/e2a-tiktok-media`. All Instagram files live in `instagram/`. Never modify/delete TikTok/YouTube files (`template/`, `videos/`, `assets/music_v3.mp3`, root README). Never force-push. Never commit secrets.

## 1. Goal
Autonomously produce and schedule **14 Instagram publications/week: 8 static (single image or carousel) + 6 Reels**, via Metricool, for E2A Basketball Academy (@e2a_basketball). Pipeline: research → plan → design → video → render → QC → GitHub upload → Metricool schedule → Sheets record → analytics. Runs in Claude Code Cloud only (no local machine dependence). Nothing may rely on temp files persisting; persistence = GitHub (code/media) + Google Sheets (records).

## 2. Business & brand
E2A connects Australia and Europe (esp. Spain) through basketball. Audience: Australian players 12–22, parents, coaches, clubs/academies, players interested in Europe. English (Australian/British). Tone: premium, modern, professional, international, aspirational. Tagline "Connecting Australia and Europe through basketball." Philosophy "More Than a Game."
Colours: Navy `#0B1B36`, Gold `#C9A44C`, White `#FFFFFF`. Official logo: Drive file `E2A_LOGO.jpeg` (ID `1tBFMCBCuRZLgZ395G9rZQWt7pEXIH9zI`, account e2abasketball@gmail.com). Never invent a logo; if inaccessible, report it. Campaign folder `E2A Spain Campaign-png` (ID `1lD7j_tU143X5pjBWtZMg3oVCLOKqVJWO`) = style reference only.

## 3. Never reuse images
Excluded: E01–E12, B01–B04, carousel "TAKE YOUR GAME TO SPAIN" (images 06, 13, 05, 09), plus anything published/scheduled in Metricool or in Drive. No re-crops, recolours, or re-texting of old designs, no reuse of scheduled images. Allowed: logo, palette, typography principles, structural templates, new original compositions. If unverifiable → do not publish.

## 4. Weekly schedule (Australia/Sydney; 10:00 and 18:00, ±2h only with verified Metricool data; ≥6h apart)
| Day | 10:00 | 18:00 |
|---|---|---|
| Mon | European Basketball News | Reel |
| Tue | Inside the European Game | Reel |
| Wed | Discover Spain | Reel |
| Thu | E2A: Beyond Basketball | European Basketball News |
| Fri | Inside the European Game | Reel |
| Sat | Discover Spain | Reel |
| Sun | E2A: Beyond Basketball | Reel |
Max 2 IG publications/day; one video/day; no two same-pillar posts/day. Always fetch current Metricool calendar; existing posts count toward the day; fill only free slots; never delete/overwrite/reschedule existing posts.

## 5. Static pillars (2/week each)
1. **European Basketball News** — verified news from last 7 days (EuroLeague, ACB, transfers, young talents, Australians in Europe); pick the 3 best, choose most relevant to Aussie fans; official sources; no rumours/invention; evergreen verified feature if no news.
2. **Inside the European Game** — educational 3–5 slide carousels, one concept, court diagrams, understandable by young players; don't duplicate that week's Reel concept.
3. **Discover Spain** — premium visuals, mainly Barcelona; different location/composition for the two weekly posts.
4. **E2A: Beyond Basketball** — mission, values, community, confirmed projects only. Never invent events, partnerships, prices, programmes, dates, club deals, opportunities. Evergreen branding if no news.
Design: finished 1080×1350 PNGs, consistent per-carousel; professional agency quality; only licensed/original imagery; verify text and resolution. Canva only if its connector supports needed ops; otherwise code (HTML/SVG rendered via Chromium).

## 6. Reels ("E2A Breakdowns")
Reference: "E2A Ep01 — Spain Pick & Roll" (ElevenLabs flow `kHnMjfPaLEGbAYyZ4l0R`: narration, voice, music, 5 SFX). Register as episode 01; never recreate. Topics rotate offence (Horns, Chicago, Floppy, Hammer, Zipper, Elevator doors, Stack PnR, Short roll, Iverson cut), defence (ICE, Hedge, Drop, Switching, FIBA-legal zone principles), team (spacing, extra pass, advantage creation, off-ball), skills (Euro step, jump stop, pivot, finishing). Every episode a new concept; verify with coaching sources. No real-player photos, no league/club logos.
Script (60–90 s, 14-year-old comprehension, calm coaching tone): Hook (3 s) → Set-up → The Key → Option 1 (+cue) → Option 2 (+cue) → Variations/Counters (2) → Summary line → Sign-off "Master the European game. Follow E2A for more breakdowns."

## 7. Video production rules
**Remotion makes ALL visuals; ElevenLabs ONLY audio.** No AI video/images/people. React+TS+Remotion+SVG+CSS only. Required: top-down animated court, numbered attackers, X defenders, passes, dribbles, movement, screens, defensive reactions, arrows, gold highlights, step labels, animated type, synced captions (word-level), camera moves, transitions, E2A branding. Notation: zigzag=dribble, solid arrow=cut, dashed arrow=pass, T-bar=screen, gold=advantage. Visual change every 3–4 s; animation must match narration. Template in `instagram/breakdown-template/` driven by structured episode data (reuse components; may reuse `template/` read-only).
Specs: 1080×1920, 9:16, 30 fps, MP4 H.264 + AAC, <15 MB. Safe areas: avoid top 250 px, bottom 450 px, right 150 px; first frame works as cover; titles within central 1080×1350. End card: official logo + "Follow E2A for more breakdowns."
Audio: ElevenLabs voice `KeU8nqWFDbaoi0QVUjD3`, model `eleven_v4` (verify availability first). Generate narration once per finished script; cache it; never regenerate because a later step failed. Music: `assets/music_v3.mp3` (copy, never modify), well below voice. SFX (whoosh, UI pop, ball catch, swish, logo sting) from Ep01 flow stored in `instagram/assets/sfx/`. Word timing via faster-whisper or equivalent. Bundle fonts/media locally (no external loads at render time). Chromium: use `/opt/pw-browsers/chromium-*/chrome-linux64/chrome` via `--browser-executable`.
QC per video: resolution, fps, duration, audio, caption sync, tactical accuracy, extracted-frame inspection, safe areas, logo, plays. Fix failures before publishing.

## 8. Tracker — Google Sheet `E2A_Instagram_Content_Tracker` (single, no duplicates)
Tabs: **images** (filename, file ID/URL, category, pub date, title, Metricool ID, IG URL, status AVAILABLE/IN_PRODUCTION/SCHEDULED/PUBLISHED/EXCLUDED); **reels** (episode no., title, concept, semantic ids, script, sources, MP4 URL, Metricool ID, date, time, status; Ep01 registered); **plan** (date, time, type, pillar, topic, status; current + next week). Before creating anything: read tracker, check Metricool, check topic/image reuse, reserve row IN_PRODUCTION; update the same row later. If persistence unavailable, say so.

## 9. Media hosting
Store under `instagram/YYYY-MM-DD/` (`10am_slide01.png`, `reel.mp4`; stable names; never overwrite published media). URLs: `https://cdn.jsdelivr.net/gh/e2abasketball-droid/e2a-tiktok-media@<commit_sha>/instagram/<date>/<file>` or `https://raw.githubusercontent.com/e2abasketball-droid/e2a-tiktok-media/<sha>/instagram/<date>/<file>`. Verify with redirects followed (`scripts/check-media-url.sh`): status, type, size, downloadability. **Verify Metricool accepts the URL format before relying on it.** No new paid services.

## 10. Metricool scheduling
Brand `e2a_basketball`, blogId `7681319`, tz `Australia/Sydney`. Before scheduling: confirm IG account, fetch scheduled posts, slot free, media complete/unused, caption OK, URL public, settings OK. instagramData type POST (image/carousel) or REEL; autoPublish true; showReelOnFeed true for Reels; `isAiGenerated` set accurately. After: re-query, confirm date/time/media/caption, record ID in Sheet. Never claim scheduled without Metricool confirmation. No infinite retries; report exact errors.

## 11. Captions
Hook line, clear English, useful info, CTA, ~5–8 hashtags; tone per pillar (News informative; Inside educational; Spain inspirational; Beyond professional/promotional). Reels: strong opener, 2–4 short lines, save/share/follow prompt. Few emojis, no generic motivation, no repetition, Aussie relevance.

## 12. Daily workflow (08:00 Australia/Sydney; prepares the NEXT day; idempotent)
1 preflight (Metricool, IG, Sheet, GitHub, network, deps — `scripts/check-env.sh`) → 2 check tomorrow's Metricool slots → 3 read tracker → 4 research → 5 produce statics/Reel → 6 script, narrate, Remotion render, QC → 7 captions → 8 upload to GitHub, verify URLs → 9 schedule in Metricool, verify → 10 update Sheet → 11 short report (date, type, pillar, topic, time, Metricool ID, status, errors). Never schedule in the past; re-running must not duplicate.
**Over-capacity rule:** if the target day already holds ≥2 IG publications, or the slot is taken, schedule nothing and report it.

## 13. Weekly analytics (Mondays)
Via Metricool: reach, engagement, likes, comments, saves, shares, follower growth, plays, watch time, best posts/pillars/times (only what exists). Derive insights, keep 8+6 structure, record next week's plan in the Sheet.

## 14. Authorisation to publish
Auto-schedule without per-post approval only if: correct IG account verified; calendar checked; content accurate and on-brand; images original/licensed/unreused; basketball correct; videos rendered and QC'd; URLs public and verified; Metricool accepts; ≤2 IG posts that day. Do not modify existing posts, delete unrelated files, or subscribe to paid services.

## 15. Reliability
Handle resets, network blips, missing assets, render/upload/API/auth errors, duplicate runs, interrupted sessions. Persistent progress in Sheet + git. Don't regenerate expensive assets. No infinite retries. Stop the affected publication safely if a critical requirement can't be verified. Never expose secrets.

## 16. Delivery
Commit to the designated branch, push, open PR to default branch; routine must use merged code (`main`). Report honestly: implemented / tested / partial / blocked / not started.
