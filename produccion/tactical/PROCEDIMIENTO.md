# Procedimiento por fases — Tactical Studio

Cada fase termina con `python3 tools/tactical_studio.py advance <cid> <estado> --op <op> [--artifact f]`.
El registro (`state/tactical/events.jsonl`) es append-only; si la ejecución se corta, `plan` dice dónde seguir.
IDs: `E2A-TACTICAL-{YYYY-MM-DD}-V01|V02` (fecha Sydney del post).

| Fase | Estado al terminar | Qué se hace | Puerta |
|---|---|---|---|
| 1 Investigación | `researched` | 3–5 candidatos de jugada original (conceptos, no clips de terceros) | Fuentes citadas, sin scraping |
| 2 Selección | `selected` | Puntuación /100 (25 visual, 20 gancho, 20 táctica, 15 originalidad, 10 audiencia, 10 viabilidad) | `repeat-check` OK (45 días, solape < 0.6) |
| 3 Guion | `scripted` | HOOK / SETUP / CASO A / CASO B o CONTRA / TAKEAWAY / CTA, 30–40 s (ideal 35–38), gancho y CTA rotados | Guion congelado (hash) |
| 4 Jugadas | `storyboard_ready` | Spec → `scripts/build-play.mts` → `scripts/test-play.mts` con claims ligados al guion; plano y cámaras | 100 % PASS del validador |
| 5 Audio | `audio_ready` | `voice-lookup`; si no hay, 1 toma ElevenLabs; Scribe para tiempos; mezcla V2 (música nunca sube, sin normalizar sobre SFX) | Presupuesto de voz |
| 6 Render | `rendered` | `npx remotion render src/index.ts Tactical3DV2 --props=<bundle>` (≈35 min) | 1080×1920, ≥30 fps, H.264/AAC |
| 7 QC | `qc_passed` | `qc <cid> --reports <dir> --mp4 <f>`: táctico, motor, audio (−14 LUFS ±1, TP ≤ −1), técnico, fotogramas, licencias | QC_PASS en las 6 |
| 8 Activo | `asset_ready` | URL estable del MP4 (ver ACTIVACION.md, bloqueo B1) | URL responde 200 y tamaño coincide |
| 9 Paquete | `authorised` | `package` (1 post, IG Reel + TikTok + YT Short; título YT ≤100 y `#shorts`) + autorización por verificador | Verificador no falsificable |
| 10 Programación | `scheduled_partial` / `scheduled_confirmed` | `reserve` por red → `createScheduledPostForReview` → `getScheduledPosts` → `confirm` | Lectura confirma hora, zona y hash del texto |
| 11 Analítica | `analytics_pending` → `analysed` | 24 h / 72 h / 7 d con datos reales | Sin dato = «sin dato» |

Fallo: `fail <cid> --phase <p> --reason <r> [--retry-after <iso>]`. Un reintento por fase; luego `failed`.
Corte de producción: si a las 09:00 del día del post no está `scheduled_confirmed`, ese vídeo se cancela
(no se publica tarde) y se informa.
