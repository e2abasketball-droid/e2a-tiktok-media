# E2A TikTok Remotion template (v1)

Used by the daily "E2A — Daily TikTok Videos" scheduled task.

- `src/Main.tsx`: scenes, captions, header, audio. Each new video replaces `SCENES`, `src/words.json` and the audio files in `public/` (vo.mp3, music.mp3 = ../assets/music_v3.mp3).
- `src/theme.ts`: E2A colours (navy, gold, white) and local fonts (Anton, Inter).
- Render: `npx remotion render src/index.ts Main out.mp4 --browser-executable=<chrome-headless-shell> --codec=h264 --crf=20 --x264-preset=veryfast`, then normalise audio with ffmpeg loudnorm (I=-14).
- First used for 2026-10-28 video_01 (1972 Olympic final).
