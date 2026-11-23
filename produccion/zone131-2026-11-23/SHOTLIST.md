# E2A — 1-3-1 Zone Defense · SHOTLIST (montaje final, 42,94 s, 1080×1920, 30 fps)

Formato: el mismo que **E2A-2-3-Zone-MASTER** (gancho, explicación cenital, caso A / reset / caso B, cierre con pregunta, narrador Deuce) con el look **E2A Basketball Visual Standard v1** (HORNS V2: atletas v33, entorno cinema, marcadores y leyenda).
Cámaras siempre con la canasta arriba (yaw 0): la izquierda de la pantalla es la izquierda del ataque.
Jugadas: **A** = `zone131-a-corner-trap`, **B** = `zone131-b-skip-corner` (recuperación tardía), **C** = `zone131-c-early-closeout` (recuperación a tiempo).

| # | Plano | Entra (s) | Jugada (tiempo de jugada) | Cámara | Voz | Qué se ve |
|---|---|---|---|---|---|---|
| 1 | hook | 0,00 | A 0 (congelada) | MAIN cenital | "One defender. Two corners." | X4 con anillo dorado pulsante; ruta por la línea de fondo a cada esquina |
| 2 | gamble | 2,61 | A 0 | MAIN | "That's the gamble of the one-three-one." | Áreas de cobertura 1-3-1 + marcadores de ataque y defensa |
| 3 | shape | 5,29 | A 0 | MAIN | "One up top. Three across the middle. One runner behind the zone." | X1 / X2-X5-X3 / X4 en secuencia |
| 4 | corner | 9,57 | A 0,25 → 2,98 | MAIN | "Watch the ball reach the corner." | O1 → O2 → O4; X2 sale, X1 hace shade, X4 se desplaza |
| 5 | trap | 12,06 | A 2,98 → 3,5, congelado | TRAP (esquina izquierda, cerca) | "The wing and the runner trap." | X2 + X4 atrapan a O4; chip CORNER TRAP; FREEZE |
| 6 | rot | 14,29 | A 3,5 → 4,4 | MAIN | "The top drops to the elbow. The middle protects inside. And the far wing drops." | X1 al elbow, X5 niega dentro, X3 al bloque débil |
| 7 | reset | 19,64 | B 0 | MAIN | "Now reset." | NEW POSSESSION |
| 8 | skip | 20,97 | B 0 → 3,3 | MAIN | "Move the ball to one wing... then skip it straight to the opposite corner." | Pase al ala y skip O2 → O3 por encima de la zona (arco 3,3 m) |
| 9 | first | 25,41 | B | MAIN | "The far wing closes out first." | X3 sale del bloque débil primero |
| 10 | sprint | 27,54 | B | MAIN | "The runner sprints across to take over." | Ruta de X4 por la línea de fondo, a su velocidad |
| 11 | three | 30,20 | B 3,3 → 4,9 | MAIN → THREE | "If they arrive late... corner three." | Pies detrás de la línea, balón dentro |
| 12 | ontime | 33,07 | C 2,0 → 5,4 | MAIN → THREE | "Recover on the pass? Contested." | X3 a 1,31 m con la mano arriba, tiro fallado; bump: X4 se queda con O3 y X3 vuelve al ala |
| 13 | close | 37,74 | A 0 | MAIN | "That's the one-three-one. Pressure creates the trap. Quick passing tests the recovery." | Mismo encuadre que el gancho (loop), título TRAP OR RECOVER?, logo 2026 |
| — | fin | 42,94 | | | | |

Cámaras (`template/tactical/episodes/_gen-zone131.py`): MAIN `orb([0.3,7.81,0.6],24.75,48)`, TRAP `orb([5.6,0.9,0.6],10.5,46)`, THREE `orb([-3.4,1.5,1.2],16.0,58)`.
