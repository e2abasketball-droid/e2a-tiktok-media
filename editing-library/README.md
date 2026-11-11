# E2A editing technique library

Persistent, versioned memory of the skill `.claude/skills/e2a-video-editing-intelligence`.
Version in `library.json` (`library.py bump` adds a minor version and a `CHANGELOG.md` line);
every card has its own `version` and `historial`.

- `index.json` — one entry per reference video (analyzed or failed), no duplicates by Drive id/URL or by file hash.
- `analyses/R-NNNN/analysis.json` + `report.md` — measures and report. **Never frames, video or audio.**
- `techniques/tec-NNNN.json` — technique cards (schema `e2a.technique/1`), validated against
  `template/src/pro/types.ts` by `library.py validate`.
- `usage.json` — which techniques each episode used (rotation).

Status today (2026-11-11): shadow mode. 5 cards, all `propuesta`, from R-0001 (an own E2A video
used as a system test). Production does not read this library until the owner approves it.

Third-party references: only measures and our own descriptions live here (the repository is public).
