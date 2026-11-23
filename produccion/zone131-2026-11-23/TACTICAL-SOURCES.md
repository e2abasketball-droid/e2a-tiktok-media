# 1-3-1 Zone — fuentes y comprobación táctica (2026-11-23)

## Estado de las fuentes
Las cinco páginas del prompt (Basketball For Coaches, The Hoops Geek ×2, Coach's Clipboard, Championship Productions) **no se pudieron abrir desde el contenedor de render** (DNS bloqueado por la red del entorno, verificado con curl y con un lector web el 23-11 a las ~11:30 UTC). El FIBA WABC manual tampoco.
**No finjo haberlas leído.** Las reglas de abajo son las que el prompt maestro resume y atribuye a esas fuentes, y coinciden con la enseñanza estándar de la 1-3-1 a media pista con trap en las esquinas de fondo. Quedan marcadas como **NO verificadas en vivo**.

## Variante elegida (una sola)
**1-3-1 a media pista con trap en la esquina de fondo (ball-side wing + tail).**
- No es el *wing trap* de la 1-3-1 extendida (chaser + wing cerca de medio campo).
- No es la 1-3-1 *match-up* del manual FIBA WABC (otra numeración, otras reglas).
- Numeración (convención The Hoops Geek, fija en todo el vídeo): **X1 chaser/top, X2 left wing, X3 right wing, X4 tail/warrior, X5 center**.

## Regla → escena → comprobación
| Regla (fuente según el prompt) | Escena | Comprobación en la jugada |
|---|---|---|
| Forma 1 arriba, 3 en medio, 1 detrás (A, B) | hook, gamble, shape | X1–X4 5,60 m; línea X2-X5-X3 |
| Balón en el ala: el wing del balón sale, el chaser hace shade, el wing débil se hunde, el tail se desplaza al lado del balón (A, B) | corner | X4 a 4,24 m de O4 a los 2,05 s; X3 en bloque débil |
| Balón a la esquina: **X4 cierra y X2 se une al trap** (B) | trap | X4–O4 0,93 m, X2–O4 1,01 m, X2–X4 1,37 m (dos ángulos, sin choque) |
| X1 al elbow del lado del balón, X5 niega interior, X3 al bloque débil (B) | rot | X1–O5 1,76 m y X1–O2 3,61 m (no marca a O2); X5 a 4,93 m de O4 (no es tercer trapper); X3 a 5,56 m de O3 |
| **Skip al lado contrario: el wing débil sale primero, el tail corre la línea de fondo y hace el bump** (A, B) | first, sprint, ontime | X3 arranca antes que X4 (B 2,22 < 2,32 s; C 2,12 < 2,18 s) y llega antes (B 4,05 < 4,37 s; C 3,43 < 4,23 s); bump: X4 se queda con O3 y X3 vuelve al ala después |
| El triple solo es abierto si la recuperación llega tarde | three | B: defensor más cercano a 1,97 m en el lanzamiento, O3 a 6,89 m del aro (fuera de la línea FIBA), balón dentro |
| Recuperación a tiempo = tiro punteado, no +3 | ontime | C: X3 a 1,31 m al lanzar, mano arriba, tiro fallado, sin +3 |

## Lo que el vídeo NO afirma
- Que el tail cubra las dos esquinas a la vez (las cubre a lo largo del tiempo).
- Que toda 1-3-1 atrape o presione a medio campo.
- Que el skip siempre dé un triple abierto.
- Ningún robo: en A el éxito es cerrar el espacio; O4 recoge el balón.

## Ajustes respecto a las anclas del prompt
- Skip directo O2→O3, 13,8 m en 1,2 s con pase por encima de la cabeza. Para que pase **por encima** de la zona y no atraviese a X5/X3, el pase tiene un arco de 3,3 m (nueva opción `arc` del pase overhead en `play.ts`, por defecto sin cambios).
- X2 defiende a O2 por el lado de fondo (5,3; 5,0), fuera de la línea del skip.
- La salida de X3 en la rama tardía es una deriva de 0,6 s mirando el balón y luego el sprint; así sale primero pero llega tarde.
- El closeout de X3 entra por el lado alto de O3 (fuera de la línea del pase), y X4 llega por la línea de fondo.
