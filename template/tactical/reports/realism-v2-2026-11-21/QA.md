# D6 — QA de Realism V2 (2026-11-21)

## Automatización
| Herramienta | Qué mide | Estado |
|---|---|---|
| `scripts/qc-realism.mts` (nuevo) | 10 gates sobre la malla DIBUJADA (FK + skinning en CPU + cloth2), con `--legacy` para el A/B | ejecutado: 4 corridas (A/B × V2/legacy) |
| `scripts/regress-poses.mts` (nuevo) | hash de todas las articulaciones y del balón a 30 fps en 12 jugadas legacy, comparado con el motor `d700987` | **12/12 PASS** |
| `scripts/smoke-realism.sh` (nuevo) | regresión + test-play + qc-contact/catch/handoff + gates sobre jugadas V2 | ejecutado: PASS |
| `scripts/test-play.mts` | táctica (velocidades, aceleraciones, solapes, claims) | A 22/22, B 23/23 |
| `qc-contact` / `qc-catch` / `qc-handoff` | contactos, dedos y fases del balón | PASS en A y B |

## Gates de `qc-realism` (los umbrales son puntos de partida del encargo y se informa de cada valor)
- `foot_plant`: deriva del pie apoyado (WARN > 2 cm, FAIL > 5 cm). Los pivotes se informan aparte. Hundimiento medido respecto a la mediana: la suela queda 1,3 cm bajo el plano, una calibración constante.
- `contact_pose`: palma contra la superficie del balón mientras se sostiene o en el hand-off. FAIL si hay > 2 cm enterrada o si ambas palmas quedan > 5 cm fuera.
- `swept_ball`: el balón se barre 8 veces por fotograma contra cápsulas (tronco, cabeza, brazos, muslos) de todos los jugadores.
- `ball_continuity`: a 240 Hz, salto > 6 cm o |dv| > 4 m/s fuera de impactos declarados.
- `ik_reach`: brazo saturado, codos que se invierten y rodillas al revés.
- `root_foot`: rumbo (FAIL > 900°/s, WARN > 720°/s) y deslizamiento con los dos pies apoyados > 0,25 s.
- `blocking`: el bloqueador está parado y con los dos pies apoyados cuando el defensor pasa más cerca. Si `face` es un ángulo, el defensor es el rival más próximo que no sea su par.
- `cloth_clip`: piel fuera de la ropa, brazos dentro de la camiseta y shorts a través de la camiseta, cada uno > 1 cm durante > 3 fotogramas. Excluye las caras del bajo con normal vertical.
- `cloth_stability`: estiramiento de aristas ≥ 1 cm (p99,9) y aceleración del bajo respecto a la pelvis (p99).
- `court`: constantes del balón y del aro, suelas dentro de la pista, y que la canasta cruce el aro.

## Resultados
La tabla completa por gate (baseline frente a V2) está en `D7-ab/README.md`.

**Calibración de los gates (honesta)**
- La primera versión daba falsos positivos y se corrigió antes de comparar:
  - el «ball of the foot» se mide en la articulación del dedo;
  - las aristas < 1 cm se excluyen del estiramiento;
  - el deslizamiento solo cuenta si dura > 0,25 s (el doble apoyo al andar es normal);
  - las caras del bajo con normal vertical se excluyen del clipping.
- **Ningún umbral se relajó para que V2 pasase.** Las mismas reglas se aplican a la baseline.

**FAIL que siguen en V2 (los mismos o menores que en la baseline):**
- `swept_ball` 4,5 cm: bote contra el muslo. 4,0 cm: cápsula de la cabeza en la subida del tiro.
- `blocking`: el hand-off de O1 es un pivote (no está plantado al empezar su bloqueo de cuerpo). En B, O4 aún recoloca un pie cuando X2 pasa por debajo, a 1,37 s.
- `foot_plant` B: X2 deriva 8,2 cm en la ruta under.
- `cloth_clip` y `cloth_stability`: limitaciones del skinning lineal.

## Capturas de momentos críticos
`D7-ab/cmp-*.jpg` (hand-off, camiseta y pies) y `D5-apparel/` (pose a pose y vuelta completa).
