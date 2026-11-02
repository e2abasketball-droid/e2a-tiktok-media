# E2A Instagram Autonomous Manager — Specification (authoritative)

Self-contained spec for the E2A Basketball Academy Instagram automation, derived from the owner's project brief. Any future
session must read this file first. Operating state, IDs and open items live in `CLAUDE.md` and `config.json`.

## 1. Mission
Autonomously research, design, render, QC, upload, schedule (Metricool) and analyse **14 Instagram publications per week**:
**8 static** (single image or carousel) + **6 Reels** (original animated basketball breakdowns).
Pipeline: RESEARCH → PLAN → DESIGN → VIDEO → RENDER → QC → GITHUB UPLOAD → METRICOOL → INSTAGRAM → ANALYTICS.
Runs in **Claude Code Cloud** (no dependence on the owner's computer). Reusable assets persist in GitHub; records in Google Sheets.
Temporary files must never be relied on across runs.

## 2. Hard rules
- Repo `e2abasketball-droid/e2a-tiktok-media`; ALL Instagram files under `instagram/`. Never modify/delete TikTok/YouTube files
  (`videos/`, `template/`, `assets/`, `test/`, root README). Never force-push. Never commit secrets. No new paid services.
- Never invent news, events, partnerships, prices, programmes, dates, club agreements or opportunities. No rumours as fact.
- Official logo only. The owner's preferred form: white on transparent, `instagram/assets/E2A_LOGO_white.png`, used directly on the navy
  background (no card, no recolour). Original navy-on-white: `assets/E2A_LOGO.jpeg` (Drive id `1tBFMCBCuRZLgZ395G9rZQWt7pEXIH9zI`).
  Never fabricate a logo.
- **Never reuse images** (§6). If reuse cannot be verified, do not publish.
- Never modify/delete/reschedule existing Metricool posts. Existing posts count toward the daily total. Max 2 IG posts/day.
- Idempotent: inspect Metricool + tracker before creating anything.
- Never claim "scheduled/tested/done" unless confirmed (re-query Metricool after scheduling).
- No photos of real people; no NBA/EuroLeague/ACB/FIBA/club logos; no unlicensed photography; no AI-generated video or people images.

## 3. Business
International basketball company connecting Australia and Europe (esp. Spain): opportunities for Australian players to experience
European basketball, develop and explore international pathways. Audience: Australian players 12–22, parents, coaches, clubs and
academies, players interested in Europe. English, Australian/British spelling. Brand: premium, modern, professional, international,
basketball-focused, aspirational. Tagline "Connecting Australia and Europe through basketball." Philosophy "More Than a Game."

## 4. Branding
Navy `#0B1B36`, Gold `#C9A44C`, White `#FFFFFF`. Fonts Anton (display) + Inter (body) bundled in `breakdown-template/public/`.
Study (never reuse) Drive folder `E2A Spain Campaign-png` (id `1lD7j_tU143X5pjBWtZMg3oVCLOKqVJWO`). Drive account e2abasketball@gmail.com.

## 5. Weekly schedule (Australia/Sydney; 10:00 and 18:00, adjustable ≤ ±2 h on verified Metricool data; ≥ 6 h apart)
| Day | 10:00 | 18:00 |
|---|---|---|
| Mon | European Basketball News | Reel |
| Tue | Inside the European Game | Reel |
| Wed | Discover Spain | Reel |
| Thu | E2A: Beyond Basketball | European Basketball News |
| Fri | Inside the European Game | Reel |
| Sat | Discover Spain | Reel |
| Sun | E2A: Beyond Basketball | Reel |

= 8 static + 6 Reels. Never two videos the same day; never two posts of the same pillar the same day. Fill only free slots.
Historical context only (always fetch the live calendar): IG posts exist at 10:00 on Oct 29/31, Nov 2/4/6/7/9/11 2026.

## 6. Image reuse exclusion
Excluded forever: E-Series E01–E12; B-Series B01–B04; carousel "TAKE YOUR GAME TO SPAIN" incl. images 06, 13, 05, 09; plus anything
already published/scheduled in Metricool or listed in the tracker. Never re-crop, recolour, re-caption or re-layout an old image.
Allowed: logo, brand colours, typography principles, structural templates, brand-new original compositions.

## 7. Static pillars (2 posts/week each)
1. **European Basketball News** — verified news from the last 7 days (EuroLeague, Liga ACB, transfers, emerging talents, Australians in
   Europe, achievements). Shortlist 3, pick the most relevant to Australians, verify with official sources. No rumours; skip generic
   results; if nothing suitable, a verified evergreen feature. Sports-journalism look; only licensed imagery (default: none).
2. **Inside the European Game** — educational 3–5 slide carousels on ONE concept (tactics, IQ, Spanish development, youth basketball,
   Aus vs Europe, spacing, ball movement, P&R concepts, academies, training), court diagrams, understandable to 12–14 year-olds.
   Must not duplicate that week's Reel concept.
3. **Discover Spain** — premium travel+basketball content, Barcelona focus (culture, opportunities, lifestyle, architecture, cities);
   vary locations/compositions across the week.
4. **E2A: Beyond Basketball** — mission, values, Australia↔Europe, development, "More Than a Game", community, *officially confirmed*
   projects only; otherwise premium evergreen branding.
Design: 1080×1350 px, all slides same size, consistent typography, each pillar visually distinct yet recognisably E2A, agency
quality (not generic AI). Always inspect final PNGs (text accuracy, overflow, resolution). Tools: `scripts/render-carousel.mjs`
(HTML→PNG, Playwright Chromium) or Canva when its connector supports the operation.

## 8. Reels ("E2A Breakdowns")
Reference: **E2A Ep01 — Spain Pick & Roll** (ElevenLabs flow `kHnMjfPaLEGbAYyZ4l0R`). Never recreate Ep01.
Topics (alternate offence/defence/team/individual; every episode a genuinely new concept): OFFENCE horns, Chicago, floppy, hammer,
zipper, elevator doors, stack P&R, short roll, Iverson cut · DEFENCE ICE, hedge, drop, switching, zone principles under FIBA rules ·
TEAM spacing, extra pass, advantage creation, off-ball movement · INDIVIDUAL euro step, jump stop, pivot, finishing decisions.
Verify with trustworthy coaching sources; record them in `episodes/<id>/SOURCES.md`.
Script (60–90 s, 14-year-old level, calm coaching tone, no hype): 1 HOOK (first 3 s) · 2 SET-UP (2–3 short sentences) · 3 THE KEY ·
4 OPTION 1 + coaching cue · 5 OPTION 2 + coaching cue · 6 VARIATIONS/COUNTERS (two) · 7 SUMMARY ("One action. Multiple threats.") ·
8 SIGN-OFF "Master the European game. Follow E2A for more breakdowns."

### Production rules
- **Remotion produces ALL visuals. ElevenLabs is audio only.** React+TypeScript+Remotion+SVG+CSS; no AI video/people.
- Visuals: top-down half court; numbered circles (attack), X (defence); dashed arrows = passes, zigzag = dribbles, solid arrows = cuts,
  T-bar = screens, gold highlights = advantages; step labels, animated type, word-synced captions, camera moves, transitions, E2A
  branding; something changes every 3–4 s; animation never contradicts the narration.
- Spec: 1080×1920, 9:16, 30 fps, MP4, H.264 (yuv420p) + AAC, target < 15 MB.
- Safe areas: nothing important in top 250 px, bottom 450 px, right 150 px. First frame works as cover. Titles inside central 1080×1350.
- Captions word-level, equal to spoken words. End card: official logo + "Follow E2A for more breakdowns."
- Audio: ElevenLabs voice `KeU8nqWFDbaoi0QVUjD3`, model `eleven_v4` (verify availability first). Generate narration ONLY once the script is
  final; never regenerate because a later step failed (reuse `episodes/<id>/vo.mp3`). Music `assets/music_v3.mp3` (copy; never edit the TikTok
  original), ≈ 0.10 volume. SFX reused from Ep01 (`assets/sfx/`: whoosh, pop, catch, swish, sting) — never regenerate.
- Data-driven: an episode = `episode.json` (waypoints, ball, arrows, highlights, steps, sfx, word timings) + `vo.mp3`. Word timings from
  `scripts/align-words.py` (faster-whisper, corrected to the known script).
- QC per Reel: resolution, fps, duration, audio, caption sync, tactical accuracy, extracted frames, safe areas, logo, playable MP4
  (`scripts/verify-reel.mjs` + visual frame inspection). Failing videos are fixed, never published unfinished.

## 9. Captions & hashtags
Hook line, clear English caption, relevant info, CTA, ~5–8 hashtags. Tone: News informative; Inside educational; Spain inspirational;
Beyond professional/promotional; Reels: one strong line + 2–4 short lines + save/share/follow prompt. Few emojis, no generic motivation,
no repetition, relevant to Australian audiences.

## 10. Media hosting
Repo path `instagram/YYYY-MM-DD/` (`10am_slide01.png…`, `18pm_reel.mp4`; stable names, never overwrite past media).
URL `https://cdn.jsdelivr.net/gh/e2abasketball-droid/e2a-tiktok-media@<commit_sha>/instagram/YYYY-MM-DD/<file>` (alt
`raw.githubusercontent.com/.../<sha>/...`). Verify with `scripts/check-media-url.sh <url> <type-prefix>` (follows redirects; status, type,
size). The commit must be pushed (public) before use. Metricool must accept the URL — see CLAUDE.md for the verified status.

## 11. Metricool
Brand `e2a_basketball`, blog id `7681319`, tz `Australia/Sydney`. Verify IG account, fetch scheduled posts, confirm slot free, verify
media/caption/URL/settings. Type POST (image/carousel) or REEL; autoPublish on; showReelOnFeed on for Reels; `isAiGenerated` accurate
(Reels with synthetic ElevenLabs narration: true). After scheduling re-query and confirm date/time/media/caption; record the id in the
tracker. On failure report the exact error; no infinite retries.

## 12. Tracker (Google Sheet `E2A_Instagram_Content_Tracker`, never duplicate; id in `config.json`)
Tabs `images`, `reels`, `plan` (columns in `config.json`). Statuses AVAILABLE, IN_PRODUCTION, SCHEDULED, PUBLISHED, EXCLUDED.
Before creating anything: read tracker, check Metricool, check topic/image duplicates, reserve the row as IN_PRODUCTION; update that row
as work progresses; no duplicate rows. If tracking is unavailable, do not claim it works.

## 13. Daily workflow (08:00 Australia/Sydney; prepares the NEXT day)
1 checks (Metricool, IG connection, Sheets, GitHub, network, deps) → 2 calendar for target date → 3 tracker → 4 research → 5 produce
statics/Reel → 6 render + QC (script → narration once → align → Remotion → QC) → 7 captions → 8 GitHub upload + URL verification →
9 Metricool schedule + confirm → 10 tracker update → 11 report (date, type, pillar, topic, time, Metricool id, status, errors).
Idempotent; never schedule in the past. Keep `plan` covering the current and following week. Media must be on the default branch/pushed
commit that scheduled runs can see (CLAUDE.md).

## 14. Weekly analytics (every Monday)
From Metricool: reach, engagement, likes, comments, saves, shares, follower growth, plays/watch time (only metrics that exist), best posts,
pillars, times, formats. Use insights to adjust topics/times; keep 8+6. Prepare next week's plan in the tracker.

## 15. Reliability
Handle resets, network failures, missing assets, render errors, failed uploads, API errors, duplicate runs, interrupted sessions, expired
URLs, auth failures. Persist progress (tracker + repo), don't repeat expensive steps (ElevenLabs), no endless retries, clear logs; if a
requirement cannot be verified, stop that publication safely. Never expose secrets.

## 16. Authorisation
Autonomous creation/scheduling via Metricool is authorised when ALL hold: correct IG account verified; calendar checked; content accurate
and on-brand; images original/licensed and unused; basketball explanations correct; videos rendered and QC'd; media URLs public and
verified; Metricool accepts; ≤ 2 posts per day. Not authorised: modifying existing posts, deleting unrelated files, paid subscriptions.
