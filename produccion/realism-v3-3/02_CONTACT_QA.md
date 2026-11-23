# Realism V3.3 — 02 CONTACT QA

**Detector:**
- `template/scripts/qc-realism-v33.mts`. Sus detectores originales son los de V3.2 sin cambios: mismos radios, umbrales y 120 Hz, sin saltar frames.
- Se le añade un **detector anatómico**: volúmenes medidos en la malla (`anat33.ts`, `qa/anat33_radii_off.json`) con tres clases:
  - `contactAllowed`: antebrazo de la mano que sujeta el balón, ≤ 1,5 cm. Es el contacto real de una mano con el balón.
  - `visible`: más de 1 cm en cualquier otra región.
  - `minor`: el resto.
- El detector de referencia (`ballBody`) se mantiene y es el que cuenta en la comparación.

## Comparación (mismo detector, mismos eventos)
| Prueba | Métrica | V3.2 | V3.3 | Δ |
|---|---|---|---|---|
| One-take (O1) | Muestras balón-cuerpo, 120 Hz (`ballBody`) | 86 | **0** | −100 % |
| One-take | Filas de defecto (todas las clases) | 27 | **2** | −93 % |
| One-take | Muñeca máx. | 994 m/s² | **433 m/s²** | −56 % |
| One-take | Hueco palma-balón (mediana / máx.) | 1,2 / — cm | 1,2 / 3,3 cm | = |
| One-take | Anatómico «visible» (> 1 cm) | — | **0** (máx. 1,3 cm, antebrazo permitido) | |
| Trío | Muestras balón-cuerpo | 60 | **0** | −100 % |
| Trío | Filas de defecto | 23 | **5** (solo cabeza) | −78 % |
| Trío | Muñeca máx. | 765 m/s² | 393 m/s² | −49 % |
| 5v5 (10 jugadores) | Muestras balón-cuerpo | — (motor legacy: 24) | **0** | |
| 5v5 | Anatómico «visible» | motor legacy: 250 (máx. 4,9 cm) | **25** (máx. 2,1 cm) | −90 % |

## Contactos residuales (no ocultos)
- 5v5, O1, 5,64–5,92 s: el antebrazo derecho pasa ≤ 1,9 cm por el balón mientras lo presenta para el hand-off. Clase `visible` porque está en el límite. **P2.**
- 5v5, O2, 6,14–6,29 s: el antebrazo derecho llega a 2,1 cm durante la recepción → set del tiro rápido. **P2.**
- 5v5, O1, 6,1 y 6,2 s: muñeca de 611 y 474 m/s² justo después de soltar el hand-off. **P1:** la mano vuelve demasiado rápido a la postura de bloqueo.
- 5v5, O2, 6,43 s: muñeca de 689 m/s² en la suelta del triple rápido. **P1.**

## Falsos positivos y detector
- Los radios no se han reducido. Los volúmenes anatómicos usan la P50 de la distancia al eje del hueso.
- El tronco es una elipse de 15 cm por delante, 10,5 por detrás y 18,5 lateral. Es más estricta que la cápsula de 5 cm del detector V3.2.
- El contacto «permitido» se limita al antebrazo de la mano que sujeta el balón y a ≤ 1,5 cm. Todo lo demás cuenta.

## Archivos
- `qa/abc_v33.json`, `qa/abc_v33_rows.json`, `qa/abc_v33.csv` (CSV por frame: estado, dueño, balón, región, profundidad, clase).
- Lo mismo para `trio_v33`, `5v5_v33`, `5v5_engine` y `onetake_v33`.
- Baseline: `qa/baseline_*.json`.
