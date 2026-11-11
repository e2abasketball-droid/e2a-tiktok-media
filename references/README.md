# E2A edit-reference library (phase 1, SHADOW)

Reference videos added to Google Drive become reusable, verifiable editing techniques for the
Remotion Pro template. Phase 1 only builds the library: **production does not read it yet**.

- Drive: `E2A — VIDEO REFERENCES/` (ids in `config.json`): `01_INBOX` (videos + sheet `ENLACES`),
  `02_ANALYZED`, `03_EDITING_TECHNIQUES`, `04_FAILED_REVIEW`.
- Repo: `analyze_reference.py` (measures), `library.py` (index without duplicates, card validator),
  `index.json` (one entry per reference), `techniques/tec-NNNN.json` (cards).
- Third-party videos stay in the owner's private Drive. The repo only holds measures and original
  descriptions of techniques: no frames, audio, captions or text copied from a reference.

## Daily run (scheduled task "E2A — VIDEO REFERENCES", 22:30 Australia/Sydney)

Hard rules: never touch the production task, Metricool, the video registry, the Control Center,
`template/` or `music/`. Never spend ElevenLabs credits (`limits.elevenlabs_credits` = 0). Never
publish. At most `limits.max_refs_per_run` references and about `limits.max_minutes_per_run`
minutes; the rest waits for the next run. A failure on one reference is recorded and the run
moves on. If Drive is unreachable, report it and stop: production is not affected.

1. **Setup.** `git fetch origin claude/project-thread-s0mqpc && git checkout -B claude/project-thread-s0mqpc FETCH_HEAD`.
   Read `references/config.json`.
2. **Find new references.**
   - Files: Drive `search_files` with `parentId = '<inbox>'`, skip Google Docs/Sheets.
   - Links: Sheets `get_values` on `links_sheet` / `links_range`; rows with column A filled and column C empty.
   - For each, `python3 references/library.py seen <drive id or url>`: exit 10 = already processed, skip.
3. **Get the video** (next free id: `library.py next-id`).
   - Drive file: if `fileSize` > `max_download_mb` MB → failed, reason `demasiado grande (>10 MB, límite del conector)`.
     Otherwise `download_file_content` (it saves the MP4 to a local path) and copy it to a scratch folder outside the repo.
   - Link: try `curl -sSL --max-time 60 -o <scratch>/ref.mp4 <url>` only if the URL ends in a video file;
     social links (instagram, tiktok, youtube, x.com, facebook) are not downloadable from the cloud →
     failed, reason `enlace no descargable desde la nube; sube el vídeo como archivo`.
4. **Measure.** `python3 -I references/analyze_reference.py <video> <scratch>/<R-id> --ref-id <R-id>`.
   Exit 2 → failed with the printed reason. Then `library.py seen <key> --sha256 <sha from measures.json>`
   (same video under another name → mark it `duplicado de R-xxxx`, move to 02_ANALYZED, no new cards).
5. **Look.** Open `<scratch>/<R-id>/sheet.jpg` (one row per shot: first, middle, last frame) and the
   measures. Describe, with evidence from the measures or the frames, the 10 dimensions:
   cuts, rhythm, animations, transitions, effects, sound, subtitles, typography, narrative, camera moves.
   Separate what is measured from what is judged by eye.
6. **Write 1–4 technique cards** (`library.py next-tec`), only for patterns that are reusable and fit
   E2A (premium, navy #0B1C3D / gold #C9A24D, voice first). Format: see `techniques/_example.json`.
   - `receta` uses only values Remotion Pro already supports (the validator enforces it). If a technique
     needs a new option, set `"requiere_codigo": true`, `estado: "propuesta"` and describe it.
   - `comprobacion` is a measurable rule QC can check on our render (e.g. `plano del dato <= 1.6 s`).
   - `medidas_origen` copies the relevant numbers from measures.json.
   - Write in Spanish. Never copy the reference's script, captions, graphics or music.
   Run `python3 references/library.py validate`; fix or delete any card that fails.
7. **Record.** Write `<scratch>/<R-id>.json` with `ref_id, source_key, source_title, kind (file|link),
   status (analyzed|failed), reason, sha256, analyzed_at (UTC), cards [tec ids], summary (≤ 3 lines)`,
   then `library.py record` it. Commit only `references/` with message
   `refs: <R-id> <analyzed|failed>` and `git push -u origin claude/project-thread-s0mqpc` (retry on network errors).
8. **Drive.**
   - Analyzed: `update_file` parentId → `analyzed`. Create one Google Doc in `techniques` named
     `<R-id> — <source title>` with the summary and the cards in plain Spanish.
   - Failed: `update_file` parentId → `failed`, and set the file description to the reason.
   - Links: write status, date, R-id and reason into columns C–F of its row (never edit A–B).
9. **Report** (≤ 12 lines): references found / analyzed / failed (with reasons), cards created,
   commit SHA, anything the owner must do. Push notification only if something failed.
