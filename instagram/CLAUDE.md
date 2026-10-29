# E2A Instagram automation — start here

Read `SPEC.md` (authoritative rules) then `config.json` (IDs). Keep Instagram files inside `instagram/`; never touch TikTok/YouTube files
(`videos/ template/ assets/ test/`). Daily routine prompt: `ROUTINE_PROMPT.md`.

## Layout
- `breakdown-template/` Remotion project (data-driven; `npm install` first, ~1 min). `src/Breakdown.tsx` renders an `episode.json`.
- `episodes/<epNN-slug>/` `script.txt`, `vo.mp3` (ElevenLabs, generated once), `words.json`, `build-episode.mjs` → `episode.json`, `SOURCES.md`.
- `scripts/` `render-reel.mjs` (render + loudnorm + QC), `verify-reel.mjs`, `align-words.py`, `render-carousel.mjs`, `check-media-url.sh`.
- `assets/` `E2A_LOGO_white.png` (use directly on navy, no card), `E2A_LOGO.jpeg`, `music_v3.mp3`, `sfx/*.mp3` (Ep01 effects, reused).
- `YYYY-MM-DD/` published media (never overwrite past dates).

## Reel recipe (tested 2026-10-29)
1. Script per SPEC §8 → verify sources → `episodes/<id>/script.txt`.
2. ElevenLabs `creative_generate_speech` (model eleven_v4, voice in config) ONCE with `estimate_only` first; download `content_url` with curl → `vo.mp3`.
3. `python3.13 scripts/align-words.py vo.mp3 script.txt words.json` (needs `pip install faster-whisper`; model downloads from HuggingFace).
4. Copy `build-episode.mjs` from the last episode, set choreography/anchors from `words.json`, run → `episode.json`.
5. `node scripts/render-reel.mjs episodes/<id>/episode.json <out>.mp4` (~2–3 min; uses /opt/pw-browsers headless shell; output QC runs automatically).
6. Extract frames (`ffmpeg -ss T -frames:v 1`), inspect visually (safe areas, logo, tactical accuracy vs narration) before upload.
Note: `ep.durationSec` must be ≥ narration + ~3.2 s end card.

## Environment facts (verified 2026-10-29, Full network)
Node 22, ffmpeg 6.1, Python 3.11/3.13, Playwright at `/opt/node-tools`, Chromium headless shell in `/opt/pw-browsers`. Reachable: jsDelivr, raw.githubusercontent,
storage.googleapis.com, registry.npmjs.org, PyPI, HuggingFace (model download), api.elevenlabs.io, app.metricool.com. ElevenLabs/Metricool/Drive/Sheets
are MCP connectors (no raw API keys in the sandbox). Drive MCP downloads return base64 inline — use the public URL in `config.json` for the logo instead.
ElevenLabs signed URLs from `creative_get_flow_run_status` work with plain `curl` for 2 h.

## Status (update this section every session)
- Tested 2026-10-29: Remotion renders 1080x1920/30fps H.264+AAC (QC script passes); word-synced captions; tracker sheet read/write; ElevenLabs voice+model
  (generated twice for Ep02 — the first take had a factual error in the flare sentence; do not repeat); jsDelivr SHA URLs (video/mp4, image/png) work for commits
  on any pushed branch; raw.githubusercontent serves mp4 as octet-stream (prefer jsDelivr). **Metricool accepted jsDelivr URLs for a 5-image carousel (POST)
  and a Reel (REEL) and re-hosted them on static.metricool.com**; re-query confirmed date/time/caption/media.
- Scheduled 2026-10-30: 10:00 carousel "Spacing" (Metricool 410018084), 18:00 Reel "Ep02 The Horns Set" (410018106).
- Not done: Cloud Routine (owner creates it from `ROUTINE_PROMPT.md`); PR merge to `main` (owner/next session); templates for News/Spain/Beyond pillars beyond `render-carousel.mjs`;
  weekly analytics not yet run (first Monday 2026-11-02); no Canva use. Sting SFX is 1 s (Ep01 original).
- Tracker `plan` tab covers 2026-10-29 → 2026-11-03 only; extend weekly.
