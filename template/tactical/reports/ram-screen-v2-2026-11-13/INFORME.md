# RAM SCREEN V2 — informe de producción (2026-11-13)

Rama: `claude/project-thread-rray0k` (e2a-tiktok-media). Sin merge, sin publicación, sin Metricool ni tareas programadas.

## Entregables (`/mnt/project-files/tactical-studio/ram-screen-v2/`)
- `ram-screen-v2-social.mp4`: máster social, 1080×1920, 30 fps, 34,1 s, −14 LUFS con ganancia fija.
- `ram-screen-v2-master-hq.mp4`: render Remotion sin recomprimir (1858 s de render a resolución completa).
- `antes-despues-v2.mp4`: 6,6 s, V1 frente a V2 con la misma cámara fija a tres cuartos, el mismo tiempo de jugada y velocidad normal. Tiene tres tramos: la salida de O5 del primer bloqueo, la frenada y el tiro de O1, y el pase y la recepción de O5. V1 es el motor y las jugadas del commit 3c4c973.
- `contact-sheet.png`: hoja de contactos de qc-video.

## Diagnóstico del máster V1
- **00:00–00:04.** Cámara baja con diez jugadores a la vista y ningún foco. En la V2 el gancho sigue a O5, con X5 detrás. Hay un único anillo dorado (O5) y uno rojo (X5), con la línea de separación desde el primer segundo, y el plano corta antes del bloqueo directo.
- **00:11–00:14, el rótulo X5.** El ID, el dorsal y el anillo eran correctos: X5 lleva el #5 y el anillo estaba en su posición. El fallo era el ancla. El rótulo se proyectaba a 2,25 m fijos sobre el jugador y además subía 70 px. Con una cámara alta, eso lo dejaba sobre X4 (#4), que estaba detrás en la imagen.
  - El nuevo control `every pin label sits on its own player` lo detecta en V1: 18 muestras de X5 sobre X4, y también «1 · OFF-BALL SCREEN» y «2 · BALL SCREEN» sobre X4.
  - En la V2 los rótulos se anclan a la cabeza real del cuerpo posado. Se colocan una sola vez por rótulo: encima, al lado, con una guía en diagonal, o bajo los pies, siempre en un sitio que no tape a otro jugador.
  - El freeze de 1,3 s desaparece. La primera resolución (He backs up) llega a 2,5 s del rótulo, en lugar de 3,5 s.
- **00:15–00:19.** Antes faltaban la frenada y la subida del balón, y el aro no se veía desde el plano del tiro. Ahora:
  - readA1 sigue a O1 y a X5 en la frenada, la recogida, la subida y la suelta.
  - El corte va a un plano detrás del tirador en el mismo eje del tiro: O1 abajo, el balón en vuelo y el aro arriba.
  - El sello +2 aparece después del enceste.
- **00:22–00:27.** Antes había un corte entre el pase y la recepción. Ahora readB2 es un único eje vertical: O1 abajo, el hueco, O5 en el centro y el aro arriba. La línea de pase aparece solo cuando se abre el hueco. El balón llega a las manos que ofrece O5 y se ven sus apoyos hasta la bandeja.
- **00:28–00:34.** El resumen repetía acciones. Ahora son dos planos con la misma cámara y el mismo instante de jugada (t = 3,72 s): BIG BACK y BIG UP. Después viene la pregunta final.

## Movimiento (rig compartido, reutilizable)
- **Anticipación automática.** Antes de arrancar, el jugador baja la cadera, inclina el tronco y gira caderas y pecho hacia la salida. Se calcula mirando 0,24 s adelante en la simulación de pasos. Se ve en O5 al salir del ram.
- **Frenada.** Una deceleración fuerte baja la cadera y echa el peso atrás. Se ve en O4 al plantarse, en X5 en el blitz y en O1 antes del pull-up.
- **Acción `bump`.** Es el defensor que absorbe el bloqueo: recula, sube los antebrazos y gira los hombros. X5 la usa entre 1,5 y 1,85 s y después rodea a O4 por dentro. Ese es el medio paso que pierde.
- **Acción `gather`.** Recogida con los dos pies antes del pull-up.
- **`face: 'ball'`.** Los defensores de ayuda miran al balón.
- **Mirada del base.** O1 mira al receptor en los últimos 0,6 s antes del pase.
- **Recepción.** En los últimos 0,22 s las manos de O5 van al balón. Con `squareUp`, que es opcional por jugada, el receptor se orienta al pasador mientras el balón vuela.
- **Manos sobre el balón.** Las manos van sobre el balón hasta la suelta del tiro y de la bandeja, y durante la carga del pase por encima de la cabeza.
- **Jugadas V2.** O4 llega antes y se planta. El contacto con X5 deja 0,75 m de separación (antes había interpenetración). O5 planta el bloqueo directo en 2,9 s, antes de que O1 lo use. En la lectura A, X5 retrocede con pasos de contención; en la B, X2 llega tarde a la ayuda y X3 se queda con el tirador.

## Pasada solo de balón (`scripts/test-ball.mts`, nuevo)
Sigue el balón a 240 Hz con estos criterios:
- Velocidad 3D ≤ 20 m/s.
- Nunca por debajo del suelo.
- Una mano a ≤ 10 cm cuando está agarrado.
- Cada bote llega al suelo.
- Sale de las manos.
- Pasa por el aro.
- Baja por la red hasta el suelo.

Corrigió cuatro saltos:
- La carga del pase por encima de la cabeza (43,6 m/s).
- El primer bote después de una recepción (41 m/s).
- Las manos lejos del balón en la recogida (0,27–0,56 m).
- La salida del aro, donde el balón se paraba en seco (20,5 m/s).

## Personajes
- Piel mate con un brillo suave, sin el clearcoat plástico.
- La tela, rugosa, lleva un brillo tintado con el color del equipo, de modo que el azul marino sigue siendo azul marino.
- Rótulas y codos redondos, trapecio que une hombro y cuello, y manos más llenas con pulgar.
- Luz lateral baja y sombras de contacto bajo cada zapatilla, más oscuras con el pie apoyado.
- Las siluetas por jugador (O1 0,92, O5 1,14, X5 1,12) vienen de la V1.

No hay una malla con esqueleto y licencia en el repositorio, así que se ha mejorado la malla procedural.

## Locución V2
Voz Deuce, ElevenLabs eleven_v4, una toma: 348 créditos. La transcripción Scribe costó 94 créditos.

| Tiempo | Texto | Plano |
|---|---|---|
| 0–3,4 | How did the big get there first? | gancho |
| 3,4–9,2 | Watch the first screen. It gives Five a head start. | rebobinado y plano alto, rótulo RAM SCREEN |
| 9,2–11,7 | Now watch the big's defender. | rótulo X5 en el jugador correcto |
| 11,7–18,1 | He backs up. That's enough room for the pull-up. | DROP → PULL-UP y corte al aro |
| 18,1–27,4 | Same setup. Now both defenders go to the ball. Five is open on the short roll. | BLITZ → SHORT ROLL |
| 27,4–34,1 | Same play. Where would you put the big? | BIG BACK / BIG UP, DROP OR BLITZ?, logo |

**Dónde se ve mejor la mejora:**
- 0,8–3,0 s: O5 carga y se escapa mientras X5 absorbe el bloqueo.
- 13,5–16,2 s: frenada, subida, suelta, aterrizaje y enceste.
- 22,0–24,6 s: pase al hueco, recepción en las manos ofrecidas y primer apoyo.

**Sonido.** A petición del propietario se han quitado los efectos fuertes (whoosh, impact, whip). Solo quedan contactos ligeros (bote, frenada, recepción, red, aterrizaje), un rebobinado breve y suave y el ambiente bajo. La música es el sintetizador propio.

## Controles
| Control | Resultado |
|---|---|
| test-play (todas) | 263/263 |
| test-motion (todas) | 95/95 |
| test-ball RAM V2 | 15/15 (V1 con el motor nuevo, también 15/15) |
| test-stagger | 88/88 |
| test-tactical | 329/333: la regla de triple de Elevator no aplica a un pull-up de media distancia; stagger-b ya fallaba en main |
| qc-tactical3d RAM V2 | 12/12 |
| qc-bounds | PASS, 0 violaciones |
| qc-video máster | PASS: −14,0 LUFS, TP −1,5 dBTP, sin avisos |
| tsc | OK |
| unittest | OK |

**Regresión.** El nuevo control de rótulos encuentra solapes que ya estaban en Stagger V2: «2» sobre O4 y «HELP: LATE» sobre O2. No he tocado ese episodio. `pinV2` no los resuelve del todo porque los grupos están muy juntos, así que hace falta reencuadrar.

## Cómo activarlo en Tactical3DV2
- El rig, el balón y los materiales nuevos se aplican solos a todas las jugadas.
- Para los rótulos, añade `"pinV2": true` en el episodio.
- Las acciones nuevas son `bump`, `gather` y `face: "ball"`. En la spec, `"squareUp": true` activa la orientación del receptor.
- Revisión de movimiento con cámara fija: `python3 tactical/review/make-review-props.py out.json jugadaA.json jugadaB.json [--speed 0.25]`. Con `--speed 0.25` sale la revisión a cámara lenta.
- `node --experimental-strip-types scripts/test-ball.mts tactical/plays/<jugada>.json` hace la pasada solo de balón.
- `scripts/pin-probe.mts <episodio> <t>` explica dónde cae cada rótulo.

## Limitaciones
- **Ropa.** No hay física de tela: es volumen y sombreado.
- **Malla.** Sigue siendo procedural, sin malla con esqueleto.
- **Ritmo.** Algunos tramos van a cámara lenta suave (0,4–0,7x) para encajar con la voz. Las resoluciones (vuelo del tiro, pase y bandeja) van entre 0,5 y 0,8x. El clip antes/después está a 1x.
- **Otras jugadas.** test-ball encuentra saltos de balón en jugadas antiguas de otros episodios (hammer-b-rim, spain-a-roll, elevator). No las he tocado.
