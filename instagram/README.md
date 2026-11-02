# E2A Instagram automation (cloud)

Status: **scaffold only, NOT active.** The authoritative specification (calendar, pillars, times, QC and
publishing-authorisation rules) was not available to the setup session, so it is not yet saved here.
Add it as `instagram/SPEC.md`; nothing may be generated or scheduled until it exists.

Do not touch `videos/`, `template/`, `assets/`, `test/` (TikTok automation).

## Connectivity verified 2026-10-29 (new cloud session, Full network)
| Target | Result |
|---|---|
| registry.npmjs.org, api.github.com | 200 |
| cdn.jsdelivr.net (npm and `/gh/` paths) | 200 |
| raw.githubusercontent.com (repo is public, `main`) | 200 |
| storage.googleapis.com, www.googleapis.com, api.elevenlabs.io | reachable (400/404 on bare root, no auth) |
| Metricool MCP: brand 7681319 (`e2a_basketball`, Australia/Sydney), read scheduled posts | works |
| Google Drive MCP search/list | works |
| ElevenLabs MCP | connected; no speech generated (credits not spent) |

Metricool already hosts IG posts scheduled to 2026-11-11 (10:00 Sydney) and TikTok/YouTube videos on
2026-10-30. The daily run must read these before scheduling.

## Media hosting
Media must be on `main` (branch-less/pinned-SHA URLs only work once pushed). Use
`https://cdn.jsdelivr.net/gh/e2abasketball-droid/e2a-tiktok-media@<commit-sha>/<path>` (pinned SHA avoids
CDN caching) with `raw.githubusercontent.com/.../<sha>/<path>` as fallback. Check with
`instagram/scripts/check-media-url.sh <url> video/` before calling Metricool.
**Not yet verified:** that Metricool's createScheduledPost accepts these URLs for Reels. The existing TikTok
flow uses jsDelivr SHA URLs successfully (registry E2A-TT-0002), which is strong evidence for video.
