# E2A edit-reference intake (SHADOW)

Reference videos added to Google Drive become measured analyses and reusable technique cards.
Since 2026-11-11 the measuring and the library belong to the skill
`.claude/skills/e2a-video-editing-intelligence` (read its `SKILL.md`); the library lives in
`editing-library/`. This folder keeps only the Drive intake: `config.json` (Drive ids, limits) and
the daily procedure below. **Production does not read the library yet.**

- Drive: `E2A — VIDEO REFERENCES/` (ids in `config.json`): `01_INBOX` (videos + sheet `ENLACES`),
  `02_ANALYZED`, `03_EDITING_TECHNIQUES`, `04_FAILED_REVIEW`.
- Third-party videos stay in the owner's private Drive. The repo only holds measures, reports and
  original descriptions of techniques: no frames, audio, captions or text copied from a reference.

## Daily run (scheduled task "E2A — VIDEO REFERENCES (sombra)", 22:17 Australia/Sydney)

Hard rules: never touch the production task, Metricool, the video registry, the Control Center,
`template/` or `music/`. Never spend ElevenLabs credits (`limits.elevenlabs_credits` = 0). Never
publish or render. At most `limits.max_refs_per_run` references and about `limits.max_minutes_per_run`
minutes; the rest waits for the next run. A failure on one reference is recorded and the run moves
on. If Drive is unreachable, report it and stop: production is not affected.

`S=.claude/skills/e2a-video-editing-intelligence/scripts` and `SCR=$(mktemp -d)` (scratch, outside the repo).

1. **Setup.** `git fetch origin claude/project-thread-s0mqpc && git checkout -B claude/project-thread-s0mqpc FETCH_HEAD`.
   Read `references/config.json`.
2. **Find new references.**
   - Files: Drive `search_files` with `parentId = '<inbox>'`, skip Google Docs/Sheets.
   - Links: Sheets `get_values` on `links_sheet` / `links_range`; rows with column A filled and column C empty.
   - For each, `python3 -I $S/library.py seen <drive id or url>`: exit 10 = already processed, skip.
3. **Get the video** (id: `python3 -I $S/library.py next-id`).
   - Drive file: if `fileSize` > `max_download_mb` MB → `library.py fail <R-id> <drive id> "demasiado grande (>10 MB, límite del conector)" --title "<name>"`.
     Otherwise `download_file_content` (it saves the MP4 to a local path) and copy it to `$SCR`.
   - Link: try `curl -sSL --max-time 60 -o $SCR/ref.mp4 <url>` only if the URL ends in a video file;
     social links (instagram, tiktok, youtube, x.com, facebook) are not downloadable from the cloud →
     `library.py fail <R-id> <url> "enlace no descargable desde la nube; sube el vídeo como archivo" --kind link`.
4. **Measure.** `python3 -I $S/analyze_video.py $SCR/ref.mp4 $SCR/<R-id> --ref-id <R-id> --title "<name>" --source-key <drive id or url> --rights tercero`
   (`--rights propio` only for E2A's own videos). Exit 2 → `library.py fail` with the printed reason.
   `python3 -I $S/validate_analysis.py $SCR/<R-id>/analysis.json` must say OK.
5. **Look.** Read `$SCR/<R-id>/report.md` and open `$SCR/<R-id>/frames/sheet.jpg`. Complete the visual
   review (what the video tells, typography, graphics) as hypotheses unless a measure backs them.
6. **Store.** `python3 -I $S/library.py add $SCR/<R-id>` (exit 10 = the same video is already in the
   library under another id: move it to 02_ANALYZED, no new cards).
7. **Cards (0–4).** `python3 -I $S/library.py propose editing-library/analyses/<R-id>/analysis.json`
   gives drafts from the measures. Keep only reusable patterns that fit E2A (premium, navy #0B1C3D /
   gold #C9A24D, voice first), rewrite them in Spanish with our own words, add what you saw as
   `hipotesis` evidence, save them (`propose --write`, then edit, or write by hand with
   `library.py next-tec`) and run `python3 -I $S/library.py validate` (fix or delete any card that
   fails). Add the card ids and a ≤ 3-line summary to the reference's entry in `editing-library/index.json`.
   Then `python3 -I $S/library.py bump "<R-id>: <n> cards"`.
8. **Commit.** Only `editing-library/` (never frames or videos), message `refs: <R-id> <analyzed|failed>`,
   and `git push -u origin claude/project-thread-s0mqpc` (retry on network errors).
9. **Drive.**
   - Analyzed: `update_file` parentId → `analyzed`. Create one Google Doc in `techniques` named
     `<R-id> — <source title>` with the summary and the cards in plain Spanish.
   - Failed: `update_file` parentId → `failed`, and set the file description to the reason.
   - Links: write status, date, R-id and reason into columns C–F of its row (never edit A–B).
10. **Report** (≤ 12 lines): references found / analyzed / failed (with reasons), cards created,
   commit SHA, anything the owner must do. Push notification only if something failed.
