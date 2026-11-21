# D1 — Auditoría del motor (Realism V2, 2026-11-21)

## Base reproducible
- Repositorio `e2a-tiktok-media`, rama de trabajo `claude/realism-v2`.
- Línea base (baseline): commit `d700987`, el último de `main` al empezar. El motor de la base se reconstruye con `git worktree add <dir> d700987` y `npx remotion bundle`.
- Stack:
  - Remotion 4.0.539, three 0.180, React 19.1 y Node 22;
  - render por CPU (`--gl=swangle`), 4 hilos y sin GPU;
  - Blender por `bpy` 5.3 (venv) para construir los jugadores.
- Cadena de un jugador: pista de la jugada (`posAt`) → `simulate` a 120 Hz (rumbo, velocidad, fase de zancada, pies) → `poseAt` (IK de 2 huesos en brazos y piernas) → `bonesFromPose` → `SkinnedAthlete`. Este último usa el GLB `e2a-player-v1`: 21 huesos y mallas de cuerpo, camiseta, pantalón, zapatillas y pelo.
- El balón lo calcula `play.ts`: `ballAt` es una máquina de eventos (hold/dribble/pocket/present, pass/handoff, shot/layup).

## PRs leídas (solo lectura, `gh api`)
- **#12 (abierta, sin fusionar):** Tactical Studio V4 en sombra. Incluye el planificador, el A/B RAM, el máster común, la retención y `FORMATO-CHICAGO.md`. **No se activa ni se toca.**
- **#13 (abierta):** subagente `e2a-3d-animation`, `ref_frames.py`, `qc-contact.mts` y el laboratorio screen-roll. Su motor de clips (`skelclip.ts`, clips `screen-roll-5452(m)`) ya está en `main`, y lo reutiliza la biblioteca de movimientos v1.

## Diagnóstico priorizado
Las medidas salen de `scripts/qc-realism.mts --legacy`, con la misma jugada Chicago y el motor sin el módulo V2.

| # | Defecto (baseline) | Medida | Prioridad |
|---|---|---|---|
| 1 | Las manos no tocan el balón en el hand-off: el pasador lo empuja con los puños por encima y el receptor no lo alcanza | palma enterrada 3,9 cm (O1@2,60 s); la palma más cercana queda a 12,0 cm (O2@2,40 s) | P0 |
| 2 | El balón atraviesa el tronco del poseedor (bolsillo / hand-off) | 14,5 cm dentro del tronco (O1@2,18 s) | P0 |
| 3 | El bote atraviesa el muslo en carrera (punto de bote pegado al cuerpo) | 13–15 cm dentro del muslo (O2@3,2 s, X1@1,9 s) | P1 |
| 4 | Salto del balón al pasar de bolsillo a bote | 8,4 cm en 1/120 s; 1 violación de continuidad | P1 |
| 5 | Giros instantáneos: el objetivo de orientación (`face: 'ball'`) cambia de jugador | 1678°/s (O4@2,33 s) | P1 |
| 6 | El bloqueador del pin-down «marca el paso»: gira ~150° en el sitio siguiendo al defensor y re-pisa continuamente | pies levantados en el contacto; rumbo de −107° a +102° en 1 s | P1 |
| 7 | Codo que se invierte | 2 inversiones de polo (O1.R@2,10, O2.R@2,70) | P2 |
| 8 | Camiseta pegada a la piel: sin caída ni movimiento secundario; se ve el glúteo bajo la tela | inspección visual + aceleración del bajo = la del cuerpo | P1 |
| 9 | Estiramiento de malla por skinning lineal (axilas) | p99,9 ×2,16 / máx ×4,9 | P2 (no resuelto) |
| 10 | Brazos dentro de la camiseta en sprint / piel fuera del pantalón | 4,9 cm / 3,8 cm | P2 (no resuelto) |

## Qué no se tocó
No se tocaron el publicador, Metricool, las tareas programadas, la PR #12, el commit fijado de la tarea diaria, los episodios publicados ni `main`.
