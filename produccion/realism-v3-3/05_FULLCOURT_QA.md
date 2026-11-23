# Realism V3.3 — 05 FULLCOURT QA (Gate 4, 5v5)

## Jugada
- `template/tactical/plays/realism-v3-3-5v5.json`, generada por `template/tactical/specs/_gen-realism-v3-3-5v5.py`. Dura **11,0 s** y tiene 10 jugadores.
- La base es la posesión original de E2A **Chicago V3 UNDER → THREE** (`chicago-v3-under-three`): pin-down de O4 sobre X2, hand-off O1 → O2, X2 pasa por debajo y O2 tira de tres.
- **La geometría y los tiempos relativos de la jugada son los mismos**. Solo se desplaza +3,5 s.
- **Ampliaciones de coreografía**, declaradas como tales y no como mejora de animación:
  1. **Preparación (0–3,5 s):** O1 sube el balón desde medio campo botando y X1 retrocede delante de él. El hueco se cierra de 1,37 a 0,98 m solo al final; con 0,82 m el bote de O1 tocaba el muslo de X1. El resto de jugadores va a sus posiciones y cada defensor sigue a su hombre.
  2. **Cierre (8,5–11 s):** tras la canasta, O4 va al rebote, X4 le cierra el rebote y los demás se reubican.
- Las comprobaciones tácticas de la jugada original se mantienen con las marcas desplazadas. `scripts/test-play.mts` da **23/23 PASS** (`qa/test-play-5v5.txt`): pin-down 0,85 m, hand-off 0,91 m, triple a 7,63 m, X2 a 1,62 m en la transferencia, defensor más cercano a 1,43 m en el tiro, bloqueos estáticos, sin solapamiento de cuerpos.
  - Dos correcciones de coreografía de esta fase: en la versión inicial del cierre O1 cruzaba a O2 a 0,29 m y O4/X4 se solapaban a 0,36 m.

## Cobertura V3.3: 10/10
Todos los jugadores salen del **compilador de eventos** (`v33-compiled`). Ningún jugador usa el motor legacy y ninguno tiene guion escrito a mano.

| Jugador | Papel | Origen V3.3 | Filas QC con el motor legacy | Filas QC V3.3 | Deslizamiento de pie, legacy → V3.3 |
|---|---|---|---|---|---|
| O1 | Base: sube el balón, ofrece y entrega el hand-off, cuerpo como 2.º bloqueo | v33-compiled | 174 | 5 | 55,7 → 0,6 cm |
| O2 | Cortador: sale del pin-down, recibe el hand-off y tira de tres | v33-compiled | 142 | 8 | 19,2 → 0,5 cm |
| O3 | Esquina, espaciado | v33-compiled | 82 | 0 | 19,6 → 0,8 cm |
| O4 | Bloqueador del pin-down, luego rebote | v33-compiled | 200 | 0 | 40,5 → 0,5 cm |
| O5 | Ala débil, espaciado | v33-compiled | 72 | 0 | 20,6 → 0,8 cm |
| X1 | Sobre el base, sin cambio | v33-compiled | 52 | 2 | 12,2 → 1,4 cm |
| X2 | Sobre el cortador: pasa por debajo, cierre tarde | v33-compiled | 69 | 1 | 48,2 → 0,5 cm |
| X3 | Esquina: ayuda y recupera | v33-compiled | 28 | 0 | 52,8 → 0,6 cm |
| X4 | Sobre el bloqueador; cierre de rebote | v33-compiled | 37 | 4 | 33,5 → 0,9 cm |
| X5 | Ala débil: ayuda y recupera | v33-compiled | 43 | 0 | 36,0 → 0,9 cm |
| **Total** | | **10/10** | **899** | **20** | |

**V3.2 en esta jugada:** V3.2 solo tiene clips para `realism-v3-2-abc` y el trío. En el 5v5, los 10 jugadores de V3.2 caerían al motor legacy (0/10 de cobertura V3.2). Por eso la comparación válida en 5v5 es **motor legacy frente a V3.3**.

## Qué genera el compilador (resumen real)
- O1:
  - bote 0–5,57 s, 10 botes;
  - pase hand-off a O2 en 5,9 s.
- O2:
  - recepción en 6,1 s;
  - parada 1-2 (6,02 / 6,18 s);
  - despegue 6,26 s, suelta 6,43 s (tiro rápido, salto bajo de 0,22 m).
- X1: de espaldas 0,34–3,94 s y 6,0–6,56 s.
- Resto:
  - posturas de defensa, bloqueo, triple amenaza, preparado y relajado;
  - mirada (a su hombre o al balón);
  - frenadas en cambios de dirección por encima de 0,85 rad a más de 1,3 m/s;
  - perfil por papel (cadencia de los grandes 0,94, del resto 1,04; postura defensiva).
- Sin primitivas no soportadas en esta jugada. La bandeja (layup) no tiene primitiva y el compilador lo avisaría.

## Defectos del 5v5 (ver 03)
- **P1:**
  - O2: sacudida de cabeza de 1 frame en el despegue del triple rápido (6,2 s).
  - O1: arranque al trote en 9,07 s, cadera 376 m/s².
  - X4: arranque lateral en 1,57 s.
  - O5, X2: tirones al arrancar desde parado (máximos fuera de filas).
  - O1: muñeca al soltar el hand-off.
- **P2:** antebrazos rozando el balón ≤ 2,1 cm (O1 presentando, O2 en el set); brazos de O2 en carrera muy rápida; codo de X2 en el contest.
- Balón-cuerpo: **0** muestras. Anatómico «visible»: 25 muestras, todas de antebrazo ≤ 2,1 cm (frente a 250 y 4,9 cm del motor legacy).
- El perfil corporal es sencillo: O5 recibe la cadencia de «grande» por su número, aunque juega de ala. **P2.**
