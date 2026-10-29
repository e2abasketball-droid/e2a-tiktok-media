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
- Done/tested: Remotion template renders 1080×1920 30 fps H.264+AAC; word-synced captions; tracker sheet created and written; Ep02 Horns Reel produced;
  carousel generator; 5-slide carousel for 2026-10-30 10:00.
- Not yet verified: that Metricool `createScheduledPost` accepts jsDelivr/raw URLs for images/Reels (TikTok flow already used jsDelivr SHA URLs).
- Not done: Cloud Routine creation (not possible from a session — owner creates it using `ROUTINE_PROMPT.md`); merge of the PR to `main`.
- Known gaps: sting SFX is 1 s (Ep01 original); Discover Spain / News / Beyond pillars have no templates yet beyond `render-carousel.mjs`.
