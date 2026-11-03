# E2A TikTok Remotion template (v1)

Used by the daily "E2A — Daily TikTok Videos" scheduled task.

- `src/Main.tsx`: scenes, captions, header, audio. Each new video replaces `SCENES`, `src/words.json` and the audio files in `public/` (vo.mp3, music.mp3 = ../assets/music_v3.mp3). Music v2: `music/e2a_music.py` writes a premixed `public/music.mp3` and sets `src/music-mix.json` to premixed (see `music/README.md`); with the default `music-mix.json` the old 0.13 volume curve is used.
- `src/theme.ts`: E2A colours (navy, gold, white) and local fonts (Anton, Inter).
- Render: `npx remotion render src/index.ts Main out.mp4 --browser-executable=<chrome-headless-shell> --codec=h264 --crf=20 --x264-preset=veryfast`, then normalise audio with ffmpeg loudnorm (I=-14).
- First used for 2026-10-28 video_01 (1972 Olympic final).

## Pro editing system (v3)

New `Pro` composition next to `Daily`: one JSON file per video in `episodes/`, cinematic camera,
motion graphics, word-by-word subtitles, sound design, styles per story type and automatic QC.
See [PRO-EDITING.md](PRO-EDITING.md). Render: `scripts/render-pro.sh episodes/<id>.json out/<id>.mp4`.
