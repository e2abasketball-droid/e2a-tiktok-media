# Status (updated 2026-11-01 ~18:xx Sydney)
Note: branch `claude/magical-hamilton-xvxh96` and the earlier `instagram/README.md` were never pushed to the remote; work restarted on `claude/clever-albattani-t7d4f1`.

| Area | State |
|---|---|
| SPEC/CLAUDE/README/ROUTINE_PROMPT | Implemented |
| Network (jsDelivr, raw.githubusercontent, npm, PyPI, app.metricool.com) | Tested OK (HTTP 200). storage.googleapis.com / www.googleapis.com / github.com / api.elevenlabs.io return 400/404 on bare root (reachable, not meaningful tests) |
| Node 22, npm, Python 3.11, FFmpeg 6.1, Chromium 1243 | Tested present |
| Remotion (`template/` deps install, bundle, headless Chromium launch) | Partially tested: install+bundle+browser launch OK; no MP4 rendered (template needs per-episode words.json/vo.mp3) |
| Metricool read (brand 7681319, scheduled posts) | Tested OK |
| Metricool accepting jsDelivr/raw URLs | NOT tested |
| ElevenLabs, Google Sheets tracker, Drive logo | NOT tested / tracker not created |
| `breakdown-template/`, SFX import, Ep01 registration, scripts for render/upload/schedule | Not started |
| Cloud routine | Not created (no tool available); see ROUTINE_PROMPT.md |

## Findings
- 2026-11-02 already has 6 Instagram items in Metricool (09:00, 10:00 x2, 12:00, 15:00, 18:00), including four history/tactics Reels also targeting TikTok+YouTube. This exceeds the 2/day cap, so nothing was scheduled for Nov 2.
- Existing IG posts 10:00 on Nov 2,4,6,7,9,11,13,14 (carousels) are in place; not touched.
