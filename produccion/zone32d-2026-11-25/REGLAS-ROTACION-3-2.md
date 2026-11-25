# E2A — 3-2 Zone Defense: reglas exactas de rotación (X1–X5)

Sistema elegido: **3-2 de media pista convencional, variante «el defensor bajo sale a la esquina»**
(ball-side low out, weak-side low across). Es UN solo sistema y lo usan todas las escenas del Reel.
No se mezcla con la variante «el ala baja a la esquina» ni con trampas de esquina.

Fuentes (no se pudieron abrir desde el contenedor: DNS bloqueado; solo fragmentos del buscador, 2026-11-25):
- HoopTactics «Three Two Zone» y Coach's Clipboard (zona 1-2-2 / 3-2): «Baseline defender X5 is on ball, X4 covers low
  post area, X3 drops to weakside baseline, X2 cuts off pass out of corner and X1 defends the high post area.»
- Fragmento sobre 3-2/1-2-2: «the ball-side low defender steps out to guard the corner, while the weak-side low
  defender rotates to the ball-side low block».
- Breakthrough Basketball «3-2 Zone» (variante con trampa de esquina: NO usada).
Estado: **reglas coherentes con esas fuentes, no verificadas en vivo contra las páginas completas.**

## Numeración y ejes

| Jugador | Puesto | Casa (ejes del repo, metros) |
|---|---|---|
| X1 | arriba-centro | (0,00, 7,75) |
| X2 | ala IZQUIERDA (del ataque) | (3,95, 6,75) |
| X3 | ala DERECHA | (−3,95, 6,75) |
| X4 | bajo IZQUIERDO | (2,05, 2,55) |
| X5 | bajo DERECHO | (−2,05, 2,55) |

Ejes del repo: x = −x del brief; aro (0, 1,575); línea de TL y = 5,8; arco FIBA 6,75 m. Con la cámara detrás del
ataque (aro arriba), la DERECHA del ataque (x < 0) es la derecha de la pantalla.

**Por qué es 3-2 y no 1-2-2:** X1, X2 y X3 están en UNA línea (diferencia de profundidad 1,0 m, separación 3,95 m);
en un 1-2-2 el punta sale alto (~9 m) y las alas quedan claramente por debajo. Comprobado en `test-play`
(«Three defenders up top», X1–X2 y X1–X3 ≤ 4,3 m en t = 0).

## Responsabilidades por posición del balón (lado derecho; el izquierdo es el espejo X2↔X3, X4↔X5)

| Balón | X1 | X2 (ala débil) | X3 (ala fuerte) | X4 (bajo débil) | X5 (bajo fuerte) |
|---|---|---|---|---|---|
| **Formación / balón arriba** | Presiona el balón (~1,3 m) | Ala izq., hundido hacia el codo extendido | Ala dcha., hundido hacia el codo extendido | Bloque izquierdo | Bloque derecho |
| **Balón en el ala** | Baja al codo del lado fuerte (poste alto) | Baja al centro (línea de TL): ayuda y skip | **Closeout** controlado al tirador | Delante del aro (centro de la zona) | Bloque del lado fuerte (poste bajo, línea de fondo) |
| **Balón en la esquina** | Poste alto / codo fuerte | Baja al **bloque débil** (aro + rebote débil) | Corta el pase de vuelta esquina→ala (entre ambos) | **Cruza la zona** al bloque fuerte | **Sale a la esquina** (closeout por el lado de fondo) |
| **Balón en el poste alto** | **Reacciona**: gira y cae sobre el receptor | Pinza al codo izq. (dig) sin perder la línea de pase al ala | Pinza al codo dcho. (dig) sin perder la línea de pase al ala | Sube un paso: muro de la zona, no sale de ella | Sube un paso: muro de la zona, no sale de ella |
| **Tiro y rebote** | Bloquea al jugador de arriba (O1) | (si el tiro es en su ala) contesta y bloquea al tirador | Bloquea al ala débil (O2) | Bloquea al grande (O5) | Bloquea al de la esquina (O4) |

Reglas transversales:
1. El aro nunca queda vacío en una rotación «correcta»: con balón en el ala, X4 delante del aro; en la esquina, X4 en el
   bloque fuerte y X2 en el bloque débil (dos defensores bajo el aro, separados ≥ 2,4 m: sin dos en el mismo sitio).
2. Nadie dobla la esquina: X3 no es segundo defensor del balón (≥ 2,5 m de O4).
3. Cada rotación la dispara una acción visible del ataque (pase, flash, tiro) y empieza después de ella.
4. En el rebote nadie vuelve a su casa: cada uno busca un cuerpo, se coloca entre él y el aro y mira al aro.
5. Debilidades que el vídeo enseña: esquinas (dos pases y la zona llega tarde), poste alto (hueco detrás de X1 cuando
   presiona el balón arriba) y rebote débil (solo dos defensores bajos).

## Implementación y verificación

| Pieza | Ruta |
|---|---|
| Jugadas (A ala+esquina, B poste alto, C tiro+rebote, D circulación final) | `template/tactical/specs/_gen-zone32d.py` → `template/tactical/plays/zone32d-*.json` |
| Esquema de áreas «3-2» (Dynamic Coverage) | `template/src/t3d/coverage3d.tsx` (`COVERAGE_SCHEMES['3-2']`) |
| Comprobación | `node --experimental-strip-types scripts/test-play.mts tactical/plays/zone32d-*.json` |

Cada regla de la tabla es un `claim` de la jugada ligado a la frase del guion (`near`, `far`, `near_rim`, `order`,
`behind_arc`). Resultado en el informe de QC.
