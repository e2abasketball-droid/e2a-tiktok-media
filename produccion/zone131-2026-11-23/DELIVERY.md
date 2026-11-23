# E2A — 1-3-1 Zone Defense · ENTREGA (2026-11-23)

**Estado:** entregado para revisión. **No publicado, no fusionado.** Sin tareas programadas, Metricool ni publicador tocados. Default del motor (Legacy) sin cambiar.

## Archivos (carpeta del proyecto `tactical-studio/zona-1-3-1/`)
- `E2A-ZONE-131-MASTER-FINAL.mp4`: Reel principal, 42,94 s, 1080×1920, 30 fps.
- `E2A-ZONE-131-TRIAL.mp4`: variante para trial reel (zoom 3 %, grade, EQ; SSIM 0,66).
- `E2A-ZONE-131-contact-sheet.jpg`: 20 fotogramas del master final.
- `TACTICAL-SOURCES.md`, `SHOTLIST.md`, `QA.md`, `TEST-PLAY.txt`, `QC-REALISM-V33.json`.

## Formato
Mismo formato, efectos, narrador y ritmo que **E2A-2-3-Zone-MASTER** (gancho, áreas de cobertura, caso A, reset, caso B tardío / C a tiempo, cierre en loop con pregunta), con el look **E2A Basketball Visual Standard v1** (atletas v33, entorno cinema, marcadores y leyenda) y el logo 2026.

## Créditos y gastos
- ElevenLabs: **599 créditos** (una toma de Deuce, autorizada por el propietario). Transcripción Scribe: 0 créditos. Trial: 0 créditos (misma toma).
- Ningún otro servicio de pago.

## Rama y commits
`e2a-tiktok-media`, rama `claude/project-thread-yalqgn` (desde `claude/horns-roll-pop-minimal-v1` 8f72841).
- Jugadas: `template/tactical/specs/_gen-zone131.py` → `template/tactical/plays/zone131-*.json`
- Montaje: `template/tactical/episodes/_gen-zone131.py`
- Motor: opción `arc` del pase overhead (`play.ts`, por defecto sin cambio), esquema `1-3-1` en `coverage3d.tsx`, `--dmax` en `fit-search.mts`.

## Reproducir
```
cd template
python3 tactical/episodes/_gen-zone131.py --out props.json --words tactical/episodes/zone131/zone131-voice.words.json --voice tactical/zone131/voice.mix.wav
npx remotion render src/index.ts Tactical3DV2 raw.mp4 --props=props.json --browser-executable=$CH --concurrency=4 --timeout=300000 --muted
# mezcla offline voz + música (-14 LUFS) y mux; el trap (fotogramas 362-428) se re-renderizó con la cámara TRAP final y se empalmó.
bash scripts/trial-variant.sh E2A-ZONE-131-MASTER-FINAL.mp4 E2A-ZONE-131-TRIAL.mp4
```
