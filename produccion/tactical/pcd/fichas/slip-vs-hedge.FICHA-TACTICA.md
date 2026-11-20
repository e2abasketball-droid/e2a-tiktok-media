# Ficha táctica: Slip vs Hard Hedge (2026-11-20)

**Episodio:** `slip-vs-hedge`, concepto de catálogo `slip-vs-hedge` (`config/tactical_concepts.v4.json`, formato *counter*). No se había producido ni publicado antes. Lo comprobé en `state/tactical/plays.jsonl`, en las carpetas de `tactical-studio/` y en `template/tactical/plays/`.

**Jugadas (datos):**
- `template/tactical/plays/slip-a-dive.json` (A, acción principal)
- `template/tactical/plays/slip-b-pullup.json` (B, contraataque lógico)
- Generador: `template/tactical/specs/_gen-slip.py`

**Liga y reglamento representados:** pista y reglas FIBA (medio campo de 15 × 14 m, línea de 3 a 6,75 m, aro en (0, 1,575)).

## Por qué este episodio (sec. 1 del encargo)
- **La ventaja se ve antes de que se mueva el balón.** El defensor del bloqueador (X5) sale a *hedge* por encima de la línea del bloqueo **antes de que el bloqueo llegue**, y la pintura queda vacía detrás de él. Se entiende sin sonido: un defensor sale y deja un hueco.
- **Una acción principal y un contraataque lógico desde el mismo arranque.** El inicio es idéntico hasta el primer paso de X5 (0,60 s).
  - A: X5 sale pronto. O5 hace *slip* (planta, se abre y se va hacia el aro) y O1 le da el pase por encima.
  - B: X5 espera. Entonces el bloqueo es real (legal) y O1 tira en suspensión delante del *drop*.
- **Dos acciones protagonistas muy animables, que son las prioridades del encargo:**
  1. Planta, apertura y recepción en carrera con bandeja (incluye despegue y aterrizaje).
  2. Frenada a dos pies y tiro en suspensión.
- **Una sola lectura defensiva:** el primer paso de X5.
- **Descartados:**
  - Ghost Screen: ya publicado el 16 nov.
  - Blind Pig, Ram, Hammer, Spain, Closeout, Post double, Flare, Elevator, Stagger, Chicago y el resto de las familias ya producidas (lista en `tactical-studio/`).
  - Reject vs ICE: el V02 del 16 nov se quedó en QC_FAIL, sin publicar. Su lectura depende del bote del manejador, que es la acción menos fiable del rig.

## Referencias (sec. 4.1)
| Tipo | Fuente | Qué se tomó como evidencia | Estado |
|---|---|---|---|
| Entrenamiento | Hooper University, «Ball Screen Offense — Beating The Hard Hedge», https://www.hooperuniversity.com/breakdowns/ball-screen-offense-beating-the-hard-hedge | El *slip* como contraataque del *hard hedge*, junto con el *wrap pass* y el *pick and pop*. | Título y resumen vistos en el buscador. La página está bloqueada por la red de la sesión (ENOTFOUND), así que no pude abrirla. |
| Entrenamiento | Breakthrough Basketball, «3 Offensive Counters For The Hard Hedge On Ball Screens», https://www.breakthroughbasketball.com/offense/3-counters-hard-hedge | El manejador no bota de inmediato ante el *hedge* (amaga o retrocede) y se pasa al bloqueador que se va hacia el aro. | Igual: solo resumen del buscador. |
| Entrenamiento (lectura del *slip*) | «Recognizing When to Slip a Screen» (resultado del buscador) | Lectura clave: «the hedge defender shows above the 3-point line or leaves a gap behind», y el *slip* justo antes del contacto. | Solo resumen del buscador. |
| Juego real | Hoops Beyond the Huddle, vol. 16, https://hoops-beyond-the-huddle.beehiiv.com/p/hoops-beyond-huddle-vol-16 | Partido internacional (Letonia contra el *hard hedge* español, ventana FIBA): el bloqueador hace *slip* hacia el poste bajo tras el *hedge* (índices 4-6 a 4-10 del boletín). | **Sin verificar visualmente.** No conozco el autor del clip ni el minuto exacto: la página no se puede abrir desde la sesión. Pendiente de que E2A mire el clip. |
| Juego real (contexto) | FIBA Basketball Champions League, «Tactics breakdown» (Cholet, *hard hedge* que deja libre el pase al *short roll*) | El *hard hedge* deja libre la línea por detrás del que sale. | Solo resumen del buscador. |
| Reglas | Reglamento FIBA 2026, https://assets.fiba.basketball/image/upload/documents-corporate-fiba-official-rules-2026-v1-1.pdf | Art. 33.7: el bloqueo legal es estático y sin contacto con desplazamiento. Art. 25: pasos y recepción en carrera con dos apoyos. | No pude descargarlo (red bloqueada). Las reglas se aplican tal como las comprueba `test-play` (bloqueo ≤ 0,15 m/s mientras está vivo, apoyos). |

> Uso de terceros: solo como referencia táctica interna. El render es una puesta en escena original de E2A (coordenadas propias). La lectura B («espera → usa el bloqueo») es el contraataque estándar del *drop*, pero en este vídeo es nuestra puesta en escena, no una regla universal.

## Disposición inicial (común a A y B), en metros
Convenio del repo: x a lo ancho; x > 0 = **izquierda** de la imagen en las cámaras de la casa (vistas desde medio campo); y desde la línea de fondo.

| Jugador | Rol | Posición | Mano / notas |
|---|---|---|---|
| O1 | Manejador, *slot* izquierdo | (2,45, 9,05) | Diestro. Bote vivo. |
| O5 | Bloqueador | (0,65, 5,55), codo izquierdo | Sube a bloquear desde 0,35 s. |
| O2 | Ala derecha | (−4,9, 6,7) | Espaciado. |
| O3 | Esquina derecha | (−6,6, 1,35) | Espaciado. Fija a X3. |
| O4 | Esquina izquierda | (6,6, 1,35) | Espaciado. |
| X1 | Sobre el balón | (2,3, 8,05) | |
| X5 | Defensor del bloqueador (**la lectura**) | (0,15, 5,15) | |
| X2 | Ala derecha | (−4,05, 6,05) | Mira al balón. |
| X3 | Hombre bajo del lado débil | (−4,45, 2,45) | Ayuda tarde en A. |
| X4 | Esquina izquierda | (5,25, 2,25) | Se queda con su hombre. |

## Tabla por evento: A, `slip-a-dive` (5,4 s)
| t (s) | Evento | Quién | Qué ve / causa | Pies, cuerpo, balón |
|---|---|---|---|---|
| 0,35 | `up` | O5 | — | Sube trotando hacia el bloqueo (2,15 m/s). |
| 0,60 | `show` | X5 | Estímulo: O5 empieza a subir (+0,25 s de latencia). | Sale fuerte por el lado de la pintura y por delante de O5. |
| 1,20 | — | X1 | Oye y ve venir el bloqueo. | Se coloca arriba (*top side*) pegado a O1: se libera la línea de pase hacia el aro. |
| 1,23–1,94 | — | O1 | Ve llegar el *hedge*. | Bote de retroceso hacia la banda (2,45 → 3,25): abre el ángulo de pase. |
| 1,98 | `hedged` | X5 | — | Ya está **por encima de la línea del bloqueo**, en (1,7, 9,3), delante de O1. El bloqueo todavía no existe. |
| 2,03 | `pick` | O1 | El *hedge* está delante. | Recoge el balón con las dos manos y lo carga por encima de la cabeza. |
| 2,08 | `plant` | O5 | Ve a X5 fuera. | Llega a 0,8 m de X1 **sin contacto**: frena y planta el pie exterior. |
| 2,18 | `slip` | O5 | — | Se abre hacia el aro y se va por detrás del *hedge*. |
| 2,53 | `pass` | O1 | Mira a O5 0,5 s antes. | Pase cargado por encima (*over the top*); vuelo de 0,58 s, unos 9 m/s, arco hasta unos 2,4 m. |
| 2,73 | — | X3 | Estímulo: el pase sale (+0,2 s). | Rota tarde hacia la zona restringida. |
| 3,11 | `catch` | O5 | — | **Recepción en carrera** con catchV2 = 2: balón por el lado del pasador, por encima del hombro, delante del tronco; dos manos; CONTACT → SECURED. |
| 3,62 | `finish` | O5 | — | Bandeja a 1,27 m del aro. Defensor más cercano a ≥ 1,0 m: llega tarde. |
| 4,02 | `make` | — | — | Canasta. |

## Tabla por evento: B, `slip-b-pullup` (5,6 s)
| t (s) | Evento | Quién | Qué ve / causa | Pies, cuerpo, balón |
|---|---|---|---|---|
| 0,35 | `up` | O5 | — | Sube a bloquear (2,7 m/s). |
| 0,60 | `wait` | X5 | El mismo estímulo que en A. | **Espera:** paso de *drop* por debajo del bloqueo, a (0,85, 6,55); pecho hacia O1. |
| 1,87–2,9 | — | O5 | — | Bloqueo legal: **estático** (≤ 0,15 m/s, `test-play`) en la cadera de X1 que da al centro. |
| 2,06 | `use` | O1 | El bloqueo está puesto. | Sale por encima del bloqueo, botando. |
| 2,36 | `bump` | X1 | Choca con O5 (centros a 0,57 m). | Absorbe (`bump`), rodea por arriba y llega tarde. |
| 2,30–3,44 | — | X5 | Ve venir a O1. | Retrocede a (0,55, 4,6): protege el aro y el *roll*. |
| 3,61 | `gather` | O1 | X5 está atrás. | Frena a dos pies en el codo derecho (−0,45, 6,45); recoge el balón. |
| 4,03 | `release` | O1 | — | Tiro en suspensión de 2 (4,9 m). Defensor más cercano a ≥ 1,8 m. |
| 4,98 | `make` | — | — | Canasta. |

**Jugadores sin balón:** O2, O3 y O4 mantienen el espaciado (las esquinas abiertas dejan sin ayuda la pintura en A). X2 y X4 miran al balón. X3 es el único que ayuda y lo hace tarde, como consecuencia del pase.

## Pase táctico 2D (sec. 4.2)
- `ficha/pase-tactico-2D.mp4`: vista alta limpia de A y luego B a velocidad real.
  - Jugadores numerados, orientación del pecho y estela de 1 s.
  - Balón siempre visible, con su dueño o la fase de vuelo, la altura z y la línea del pase.
  - Metros en los ejes y lado fuerte / débil.
- `ficha/pase-tactico-2D-hoja.png`: fotogramas en cada evento.
- Ambos salen de `template/scripts/play-dump.mts` + `tools/tactical_2d.py`, con **las mismas funciones y tiempos** que el 3D.

**Qué corrigió el 2D antes del 3D:**
1. X1 tapaba el pase por encima (0,07 m de la línea): pasa al *top side* y O1 retrocede hacia la banda (línea limpia a ≥ 0,6 m).
2. El primer *hedge* se veía lejos de O1 (2,3 m): se acerca a 1,5 m, delante de su salida hacia el centro.
3. En B, X1 no llegaba a chocar con el bloqueo (0,8 m entre centros): ahora choca a 0,57 m y absorbe el contacto.
4. En A, el balón del pase por detrás atravesaba el tronco del receptor en los últimos 0,05 s (qc-catch, 12,8 cm). Se corrigió con catchV2 = 2 (ver INFORME).

## QC de la jugada (todo PASS)
`test-play` 21/21 y 17/17 · `test-ball` 7/7 y 6/6 · `test-motion` 7/7 y 6/6 · `qc-catch` (torso, manos delante, dos manos, continuidad, fases) · `qc-contact` (pies sin deslizar, sin interpenetración, manos en el balón) · `qc-players3d` (malla).
