# Realism V3.3 — 00 BASELINE (2026-11-22)

## Rama y punto de partida
- Repo `e2abasketball-droid/e2a-tiktok-media`, rama **`claude/realism-v3-3`** creada desde **`28b06ea`** (V3.2, rama `claude/realism-v3-2`).
- Sin fusionar. Sin tocar `main`. No se ha hecho ningún rebase.
- Inventario de la base: `28b06ea` lleva **126 commits que no están en `main`**. Son las ramas de reels y del motor: Chicago V3 `4682d58`/`4010374`, RAM, Stagger, V3/V3.1/V3.2…
  - Diferencia `main..28b06ea`: 1093 archivos.
  - V3.3 no toca ninguno de ellos, salvo `Scene.tsx` y `realism-v3/index.ts` (ver 01).

## Herramientas
| | Versión |
|---|---|
| Node | v22.23.5 |
| Remotion | 4.0.539 (CLI del repo) |
| Chromium | Chrome for Testing 157.0.8103.78, headless shell (`/opt/pw-browsers/chromium_headless_shell-1243`), `--gl=swangle` |
| Python | 3.13.18 |
| Blender | bpy 5.3.0 (pip, sin interfaz; 5.0 no estaba disponible) |
| ffmpeg | 6.1.1 |
| Máquina | 4 núcleos, 15 GB RAM, sin GPU |

## Baseline repetida (mismo detector V3.2, sin cambios)
Medida con `scripts/qc-realism-v33.mts`, que es una copia exacta de `qc-realism-v32.mts` más detectores añadidos. Los detectores originales no se modificaron: mismos radios, umbrales y frecuencia de 120 Hz.

| One-take (`realism-v3-2-abc`, O1) | Legacy (engine) | V3.1 | V3.2 |
|---|---|---|---|
| Filas de defecto | 218 | 27 | **27** |
| Muestras balón-cuerpo (120 Hz) | 26 | 45 | **86** |
| Aceleración máx. de muñeca (m/s²) | 5786 | 2640 | **994** (6,725 s) |
| Deslizamiento de pie máx. | 51,6 cm | 0,6 cm | **1,6 cm** |

Trío V3.2 (`realism-v3-2-trio`): 23 filas y 60 muestras balón-cuerpo (O2).

Las cifras coinciden con `produccion/realism-v3-2/QA.md`: la baseline se reprodujo exactamente.
JSON: `qa/baseline_*.json`.

## Riesgos detectados al empezar
- **P0** El QC de V3.2 tardaba 4 min 47 s por one-take: `clothV32` vuelve a integrar 1,2 s de muelle en cada frame. Eso impide iterar. V3.3 lo resuelve memoizando y precalculando el oscilador una vez por jugada.
- **P0** El balón de V3.2 tiene dos fuentes de verdad: el motor y el socket de la mano. Eso produce saltos y atraviesa el cuerpo.
- **P1** La biblioteca V3.2 solo cubre clips escritos a mano para 1–3 jugadores. En una jugada 5v5 el resto caería al motor legacy.
- **P2** MPFB sigue bloqueado (403) y no hay Blender con interfaz. No afecta a V3.3, que reutiliza las mallas V3.2.
