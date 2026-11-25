# E2A — 3-2 Zone Defense: rutas del proyecto y asignación de herramientas

Repo `e2abasketball-droid/e2a-tiktok-media`, rama **`claude/project-thread-rytopx`**, creada desde
`claude/project-thread-5a4aj1` (3ebcbca, la última con 2-3 V2 Dynamic Coverage, 1-3-1, Arrow Press, 4 Rules, NBA vs EL).
No se toca ningún proyecto anterior (2-3: `claude/zona-2-3-v2`; sus jugadas `zone23-*` y `zone32-*` de ataque quedan igual).

## Referencias auditadas
| Referencia | Dónde | Qué se reutiliza |
|---|---|---|
| 2-3 Zone V2 (principal) | rama `claude/zona-2-3-v2`, `template/tactical/episodes/_gen-zona23-v2.py`, `src/t3d/coverage3d.tsx` | Dynamic Coverage (áreas X1–X5 en el parqué), formato de la serie defensiva |
| 1-3-1 Zone | `template/tactical/episodes/_gen-zone131.py`, `specs/_gen-zone131.py` | estructura del generador (líneas → planos), cámara MAIN aro arriba, marker/legend, pins, chips |
| HORNS V2 | `produccion/horns-roll-pop-minimal/`, `template/tactical/presets/e2a-visual-standard-v1.json` | E2A Basketball Visual Standard v1: `athleteRenderer: v33`, `env: cinema` |
| Arrow Press V3 | `produccion/arrow131-v2-2026-11-24/` | Floor Graphics Stability Standard (activeKeys, stable, una cobertura por plano), Voice Dynamics, eleven_v3 con etiquetas |
| 4 Rules / NBA vs EL | `produccion/rules4-2026-11-24/`, `produccion/nbaeu-*` | `voice-energy-qc.py`, render con headless shell |
| Realism | V3.3 (`claude/realism-v3-3`, flag `v33` por episodio) | elegido: el más estable usado en todos los reels desde el 23 nov. El valor por defecto global (legacy) NO cambia |

## Archivos nuevos de este Reel
| Qué | Ruta |
|---|---|
| Reglas de rotación | `produccion/zone32d-2026-11-25/REGLAS-ROTACION-3-2.md` |
| Generador de jugadas | `template/tactical/specs/_gen-zone32d.py` → `template/tactical/plays/zone32d-{a-wing-corner,b-high-post,c-shot-boxout,d-swing}.json` |
| Esquema de áreas 3-2 (reutilizable) | `template/src/t3d/coverage3d.tsx` → `COVERAGE_SCHEMES['3-2']` |
| Cara «rim» en el rig (box-out) | `template/src/t3d/rig.ts` `lookAngle` (antes rompía; ninguna jugada antigua la usaba) |
| Generador del montaje (+ `--trial`) | `template/tactical/episodes/_gen-zone32d.py` |
| Voz (corte sin regenerar) | `template/tactical/episodes/zone32d/_voice-zone32d.py`, curva `zone32d-voice-dynamics.json`, palabras `zone32d-voice.words.final.json` |
| Audio (no en git) | `template/public/zone32d/` (toma cruda, voz cortada, voz con dinámica, música, mezcla) |
| Entregables | `/mnt/project-files/tactical-studio/zona-3-2-defensa/` |

## Herramientas por paso
| Paso | Herramienta |
|---|---|
| Fuentes tácticas | WebSearch (fragmentos); páginas de coaching bloqueadas por DNS en el contenedor |
| Validación táctica | `scripts/test-play.mts` (física + claims ligados al guion) |
| Encuadre | `scripts/fit-search.mts` (cámaras), `scripts/frame-fit.mts` (todo el montaje) |
| Motor / montaje | `scripts/qc-tactical3d.mts` |
| Voz | ElevenLabs `creative_generate_speech` eleven_v3, Deuce `DaueUomjhh8LFuAV8aGj` (1 toma, 838 cr aprobados), Scribe (0 cr) |
| Dinámica de voz y mezcla | `scripts/voice-dynamics.py --preserve` (−14 LUFS, TP ≤ −1), `scripts/voice-energy-qc.py` |
| Música | `music/e2a_music.py --story tactical --no-sfx` (síntesis propia: uso comercial sin licencia; sin botes) |
| Render | Remotion `Tactical3DV2`, `--gl=swangle`, chrome-headless-shell 1243, concurrency 4, render único |
| QC del MP4 | `scripts/qc-video.py`, `scripts/qc-floor-flicker.py`, ffprobe/ebur128, hoja de contactos |
| Trial | mismo generador `--trial` (otro gancho) + `scripts/trial-variant.sh` (zoom/color/EQ), misma toma de voz |
| Portada | fotograma del vídeo + `scripts/make-cover.py` |
