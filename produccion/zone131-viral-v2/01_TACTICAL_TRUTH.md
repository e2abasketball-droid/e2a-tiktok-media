# 01 · Verdad táctica — 1-3-1 Zone V2

**Variante:** 1-3-1 a media pista con trap en las esquinas de fondo, ala del lado del balón + tail. No es una match-up, ni una presión a toda pista, ni la 1-3-1 ofensiva.
**Nombres** (iguales en todo el vídeo):
- Defensa: X1 chaser/top, X2 left wing, X3 right wing (primer closeout tras el skip), X4 tail/runner de fondo, X5 center.
- Ataque (azul): O1 base, O2 ala izquierda, O3 esquina derecha, O4 esquina izquierda, O5 poste alto.

**Ejes:** el repo usa x = −x del brief. x > 0 es la izquierda del ataque, es decir, la izquierda de la pantalla con la canasta arriba. Todas las cámaras V2 tienen yaw 0 (canasta arriba). La V2 ya no tiene la vista lateral con el aro a la izquierda.

Las jugadas son **las mismas de la V1**: no se ha cambiado ninguna coordenada (test-play 86/86, claims PASS; `zone131-2026-11-23/TEST-PLAY.txt`).

## Máquina de estados (eventos de las jugadas, segundos de jugada)
| Evento | A (trap) | B (LATE) | C (ON TIME) |
|---|---|---|---|
| pass_start O1→O2 | 0,70 | 0,70 | 0,70 |
| ball_wing (catch O2) | 1,45 | 1,45 | 1,45 |
| X4 shade al lado del balón | 2,05 | 2,05 | 2,05 |
| pass_start O2→O4 / skip_release O2→O3 | 2,35 | 2,10 | 2,10 |
| ball_corner / skip_arrival | 2,85 | 3,30 | 3,30 |
| trap_complete (X4 3,35 · X2 3,45) | 3,50 | — | — |
| X1 elbow / X5 deny / X3 weak block | 3,45 / 3,50 / 3,40 | — | — |
| X3_closeout_start | — | 2,22 | 2,12 |
| X4_baseline_sprint_start | — | 2,32 | 2,18 |
| X3_arrival | — | 4,05 | 3,43 |
| shot_release | — | 3,68 | 3,68 |
| X4_arrival / X4_takeover (bump) | — | 4,37 / 5,27 | 4,23 / 5,13 |
| X3 de vuelta al ala | — | 5,72 | 5,58 |
| Resultado | O4 recoge, sin robo | triple dentro (4,78) | fallo, sin +3 |

## Mismo estado para LATE y ON TIME (comprobación numérica, 120 Hz)
Muestreo con `sample()` de `src/tactical/play.ts` a 120 Hz; el resultado está en `QA-DATA.json`.
- Diferencia máxima de **los diez jugadores** entre B y C de 0 a 2,10 s (skip): **0,0000 m**.
- Diferencia máxima de **los cinco atacantes** de 2,10 s al lanzamiento (3,68 s): **0,0000 m**. Pase, receptor y momento del tiro son idénticos.
- Diferencia máxima del **balón** hasta el lanzamiento: **0,0000 m**.
- Solo cambia la defensa: X3 sale a 2,12 s en lugar de 2,22 s, sin la deriva de 0,6 s mirando el balón; X4 sale a 2,18 s en lugar de 2,32 s.
- En la V2 los dos casos se ven a la vez (pantalla partida), con la **misma cámara y el mismo reloj**.

## Tabla de responsabilidades en fotogramas clave
| Momento | X1 | X2 | X3 | X4 | X5 |
|---|---|---|---|---|---|
| A 1,45 balón en el ala | shade al balón | sale a O2 | se hunde en el lado débil | se desplaza al lado del balón | entre O5 y el aro |
| A 3,50 trap | elbow (1,76 m de O5; no marca a O2) | trap (1,01 m de O4) | bloque débil | trap (0,93 m de O4) | interior, a 4,93 m de O4 (no es tercer trapper) |
| B/C 2,10 skip | línea de inversión | presiona a O2 | **sale primero** | **arranca por el fondo** | protege dentro |
| B 3,68 tiro LATE | — | — | a **1,97 m** de O3 (llega tarde) | a 3,17 m | — |
| C 3,68 tiro ON TIME | — | — | a **1,31 m**, mano arriba (contesta X3, no X4) | a 2,42 m | — |
| B/C ~5,2 bump | — | — | vuelve al ala | se queda con O3 | — |

## Geometría
- O3 lanza desde (−6,88, 1,25): a 6,89 m del aro. Fuera de la línea de esquina FIBA (6,60 m) y dentro de la banda (7,50 m), con los dos pies.
- Skip directo O2→O3 de 13,8 m en 1,2 s, con pase por encima de la cabeza y arco de 3,3 m: pasa **por encima** de la zona.
- Balón-cuerpo: 0 en B y C. En A solo hay 2 muestras a 6,5 s, que la V2 no muestra (A se usa hasta 4,3 s).

## Lo que el vídeo NO afirma
- Que un skip deje siempre un triple libre: el payoff muestra los dos desenlaces.
- Que X4 cubra las dos esquinas a la vez.
- Que haya robo en el trap.
- Que el ON TIME lo conteste X4: lo contesta X3, y X4 llega después y hace el bump.

## Fuentes
Las cuatro webs del brief **no se pudieron abrir desde el contenedor** (DNS bloqueado, igual que en la V1). Las reglas siguen el documento maestro E2A y la enseñanza estándar de esta variante, y quedan marcadas como **no verificadas en vivo**.
