# Elevator Screen · Piloto 01 · V2: informe de cambios

Revisión quirúrgica sobre el mismo proyecto Remotion. Es la segunda pasada de edición sobre la V1.

- Rama `claude/project-thread-iqip2t-v2`, que parte de la rama de la V1. **Sin merge.**
- Se conservan:
  - el guion palabra por palabra;
  - la toma de voz (Deuce);
  - las dos jugadas (sin tocar ni una coordenada);
  - la cancha, los jugadores, la marca y los gráficos.

Todos los tiempos «V1» son del vídeo original; los «V2» son del vídeo nuevo.

## 1. Duración y audio: antes y después

| | V1 | V2 |
|---|---|---|
| Duración (contenedor) | 75,50 s | 66,00 s |
| Duración del contenido (última palabra + cola) | 75,44 s | 65,89 s |
| Primera palabra | 0,70 s | 0,31 s |
| Cola después de la última palabra | 2,4 s | 1,1 s |
| Sonoridad integrada | −14,2 LUFS | __LUFS__ |
| Pico real | −1,3 dBTP | __TP__ |
| Rango de sonoridad (LRA) | 3,8 LU | __LRA__ |
| Silencios en la mezcla final (silencedetect −35 dB, ≥ 0,25 s) | 16 tramos, el mayor de 1,64 s | __SIL__ |
| Silencio añadido a la voz | 10,0 s de silencio digital (9,3 s en 10 pausas + 0,7 s de entrada), más la cola de 2,4 s | 1,75 s (ruido de sala en 7 pausas, entrada de 0,15 s) |
| Voz | Deuce, 1 toma, misma cadena (paso alto 80 Hz, +2 dB a 3,2 kHz, compresión 2,5:1, −16 LUFS) | **Idéntica**: misma toma y misma cadena; no se ha cambiado el timbre |
| Música | motor E2A, drop 24,62 s / payoff 57,6 s fijos | motor E2A, drop y payoff anclados a «First scenario» (21,11 s) y «That's what makes» (50,09 s); continua bajo la voz |

## 2. Los 7 intervalos de audio indicados

### Causa

El fallo no estaba en la toma de ElevenLabs ni en el MP4. Estaba en mi script de pausas de la V1 (`tactical-voice.py`):

- Insertaba **silencio digital absoluto** (0,5–1,5 s) después de 10 frases.
- Ese silencio se sumaba a la pausa natural de la voz (~0,45 s).
- Además, la V1 empezaba con 0,7 s de silencio y terminaba con una cola de 2,4 s.

### Ninguna palabra estaba cortada

Lo verifiqué comparando la toma original con la pista de voz, muestra a muestra:

- Todos los cortes caen dentro de silencios acústicos de la toma, entre −59 y −89 dB.
- La diferencia máxima entre la voz de la V2 y la fuente es de 0,00005. Es decir, la voz es idéntica salvo el redondeo a 16 bits.

### Tabla de intervalos

| V1 | Duración | Qué era | Corrección | V2 (mismo punto) | Verificación |
|---|---|---|---|---|---|
| 00:09.90–00:10.81 | 0,91 s | Tras «This is the elevator screen.»: 1,3 s de silencio insertado + pausa natural | Pausa total fijada en 0,55 s: la natural de la toma (0,46 s) + 0,09 s de su propio ruido de sala | 00:09.48–00:09.97 (0,49 s) | silencedetect en la voz V2 |
| 00:12.36–00:13.19 | 0,83 s | Tras «Here's how it works.»: 0,5 s insertados | Eliminado el relleno; queda solo la pausa natural | 00:10.92–00:11.32 (0,40 s) | ídem |
| 00:16.57–00:17.48 | 0,90 s | Tras «leaving a narrow opening.»: 0,5 s insertados | Eliminado el relleno; queda la pausa natural | 00:14.61–00:15.10 (0,49 s) | ídem |
| 00:27.13–00:27.51 | 0,38 s | Pausa **natural** de la toma («…follows the shooter. / Watch…») | **Conservada**: es puntuación real | 00:23.70–00:24.10 (0,39 s) | ídem |
| 00:35.68–00:36.08 | 0,40 s | Pausa **natural** («…right on time. / Catch.») | **Conservada**: prepara «Catch. Shoot. Three points.» | 00:31.43–00:31.83 (0,39 s) | ídem |
| 00:57.07–00:57.64 | 0,57 s | Tras «…a layup opportunity instead.»: 1,5 s de silencio digital. Es la caída más profunda porque la música estaba atenuada bajo la voz | 0,75 s en total (0,42 s natural + 0,33 s de ruido de sala); la música sigue sonando por debajo | 00:49.47–00:50.20 (0,72 s, pausa de cambio de bloque) | silencedetect en la voz y en la mezcla final |
| 01:13.86–01:15.50 | 1,64 s | Cola de 2,4 s después de la última palabra | Cola reducida a 1,1 s: logo + final de la música. El vídeo acaba al terminar el sonido | Final a 01:05.89 | ffprobe + revisión del último fotograma |

### Pausas que se mantienen a propósito

Son las únicas por encima de 0,6 s:

| V2 | Duración | Por qué |
|---|---|---|
| 00:06.75–00:07.57 | 0,82 s | Golpe dramático tras «…destroy an entire defense.»: congelado «TRAPPED.» y comienzo del rebobinado |
| 00:34.01–00:34.84 | 0,84 s | El balón cae por el aro: «OPEN THREE» |
| 00:49.47–00:50.20 | 0,72 s | La bandeja entra y se pasa a la comparación |
| 00:59.00–00:59.74 | 0,74 s | Resumen en pantalla partida antes de la conclusión |

Las demás pausas miden 0,26–0,53 s y son las naturales de la toma.

**Método (nuevo `tactical-voice.py`):**

- Se buscan los silencios acústicos en la propia toma, porque los tiempos de Scribe no son fiables para cortar.
- Se corta en los 20 ms más silenciosos de cada silencio.
- Solo se añade lo que falta hasta la pausa objetivo, y se rellena con el ruido de sala de esa misma pausa.
- Cada empalme lleva un fundido de 8 ms.
- No se ha regenerado la voz y no se ha gastado ningún crédito.

## 3. Sincronización

Al acortar las pausas, todo se movió con la voz. Las referencias en segundos absolutos se cambiaron por anclas de narración:

- Nuevo resolvedor `makeTacticalResolver` (`src/tactical/edit.ts`) con estos formatos:
  - «frase»: inicio de la frase;
  - «frase>»: fin de la frase;
  - «frase#2»: segunda aparición;
  - «frase+0.25»: frase más un desfase en segundos;
  - «@end-0.5»: tiempo relativo al final del plano.
- Pasan a anclas todos los tiempos que dependían de segundos absolutos:
  - congelaciones y títulos;
  - remapeos del reloj de juego (pase, tiro, canasta);
  - claves de cámara;
  - efectos de sonido;
  - cortes de plano;
  - picos de la música (`musicDrop` y `musicPayoff`, que resuelve `scripts/tactical-cue.mjs`).
- Los subtítulos salen de los tiempos por palabra desplazados, en el mismo sistema.
- QC de la skill: Q9 ✔. Todos los cortes caen entre palabras; en la primera pasada de V2 había 4 cortes a mitad de palabra y se corrigieron.

## 4. Cambios visuales por escena

| Escena (V1 → V2) | Problema | Cambio | Verificación |
|---|---|---|---|
| Hook 00:00–07:90 → 00:00–07:27 | Momentos sin acción; congelado largo | Acercamiento suave hacia el hueco sobre «One tiny gap». Las puertas se cierran a cámara lenta bajo «And one decision…». El congelado y «TRAPPED.» caen **sobre la palabra "destroy"** (antes, a un segundo fijo). El congelado pasa de 2,9 s a 2,3 s | Captura 01 |
| Rebobinado 07:90–11:29 → 07:27–09:99 | Grúa lenta tras una pausa larga | El rebobinado empieza en la pausa tras «defense.». La grúa termina justo antes del corte, encuadrando una cancha más grande | Captura 02; QC de cámara 0,035/fotograma (límite 0,035) |
| Explicación 11:29–24:52 → 09:99–21:11 | Cancha pequeña, pausas, todo a la vez | Cancha más grande: distancia 41 → 30 m. Un movimiento cada ~2 s (cenital → hueco → acercamiento → bloqueo → «puertas»). Orden de la información: bloqueadores → hueco → **tirador O2 (anillo «SHOOTER»)** → ruta → cierre. Se elimina la barra de tiempos y el pasillo desaparece cuando entra el tirador | Capturas 03–06 |
| Case A 24:52–31:37 → 21:11–27:12 | 2,8 s parado bajo el título | La jugada arranca con «the defender follows» (cámara lenta) y va a velocidad real desde «Watch what happens». Cámara de seguimiento de O2. Rutas de O2 y X2 progresivas. La canasta se reserva para el plano del tiro | Capturas 07–08 |
| Repetición 31:37–36:09 → 27:12–31:84 | — | Sin cambios de contenido (separación, línea de pase, espacio abierto); solo el final anclado al corte | Captura 09 |
| Tiro 36:09–39:78 → 31:84–34:76 | La canasta llegaba tarde y el resultado se veía poco | Recepción en ligera cámara lenta. Vuelo del balón a velocidad real. **La canasta entra sobre «points.»** y la cámara pasa al aro. «OPEN THREE +3» se ve 1,2 s y es un 20 % más pequeño | Captura 10 |
| Cambio de caso 39:78–44:39 → 34:76–39:07 | Pregunta larga, bifurcación cargada | Rebobinado en vista cenital y **match cut** con la posición inicial idéntica del Case B. Texto «WHAT IF THEY SWITCH?»; se eliminan la bifurcación y «SAME START» | Captura 11 |
| Case B 44:39–57:48 → 39:07–50:09 | Encuadres parecidos, demasiada información, «+2» enorme | La cámara se mueve hacia el espacio que deja X5 («SPACE LEFT OPEN»). La línea de pase solo aparece cuando se abre (se quitó del plano de la lectura). «SLIP TO THE RIM +2» al 62 %, sin tapar a O5. **La bandeja sí entra** (marca `make` de la jugada B), así que «+2» es un hecho mostrado | Capturas 12–15 |
| Comparación 57:48–67:70 → 50:09–60:83 | Dos canchas pequeñas durante 10 s, un panel oscurecido | **Case A ampliado (6,0 s)**: «CHASE → OPEN THREE», con seguimiento de O2 y la canasta sobre «three». **Case B ampliado (3,4 s)**: «AGGRESSIVE SWITCH → SLIP». **Split de 1,4 s** con los dos resultados. Sin paneles oscurecidos | Capturas 16–18 |
| Conclusión 67:70–75:44 → 60:83–65:89 | Poca energía, cancha pequeña, 2,4 s de silencio | Pizarra más grande (distancia 41 → 26,5 m) con acercamiento lento durante la frase final. «READ THE DEFENSE.» a 128 px, «HOW WOULD YOU GUARD IT?» en una sola línea y logo E2A sobre «it?». Final 1,1 s después de la última palabra | Capturas 19–20 |

## 5. QA

__QA__

## 6. Lo que no se ha podido cumplir

- **La duración queda en 65,9 s, no en 70–73 s.** La narración sin pausas añadidas dura 63 s. Llegar a 70 s exigiría unos 5 s de pausas artificiales, justo lo que pedís eliminar. Se priorizó la naturalidad, como indica el punto 11 del brief.
- **Control de calidad de la skill:** usa una réplica del storyboard en formato Pro (la skill no lee el formato táctico), así que algunos avisos no aplican a este vídeo.
  - Q1 (duración ideal de 20–60 s para curiosidades), Q2, Q4 y Q6: la réplica trata cada plano como una imagen fija.
  - Q10: las fuentes y el final «question» no existen en formato Pro.
  - Q8: lo provoca el nombre del split en la réplica.
  - Los controles que sí aplican pasan: Q3, Q5, Q7 y Q9.
- La pantalla partida sigue siendo pequeña en el móvil. Por eso ahora dura 1,4 s y solo enseña los resultados.
