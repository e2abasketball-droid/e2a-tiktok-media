# Componentes reutilizables V2 (pendientes de aprobación)

Todos son opcionales: ningún vídeo los usa si no los pide, y no son el estilo por defecto.
Código en la rama `claude/project-thread-5a4aj1` del repo e2a-tiktok-media.

## E2A Broadcast Scoreboard
- **Archivo:** `template/src/t3d/broadcast.tsx` (`BroadcastScoreboard`). En el episodio es el elemento de pantalla `scoreboard`.
- **Diseño:** barra oscura de 980 × 176 px con borde discreto y sombra suave, sin neón. Lleva cuatro bloques:
  - identificación de la liga (logotipo oficial si existe; si no, el nombre sobre blanco)
  - dos equipos, cada uno con barra de color, nombre y puntos
  - periodo y reloj de partido (números tabulares de 92 px)
  - reloj de posesión aparte, en ámbar y en una caja negra, para que no se confunda con el reloj de partido
- **Animación:** entra con una cortinilla de izquierda a derecha de 0,38 s, sin rebote. `highlight` dibuja un contorno dorado solo alrededor del reloj de partido. `dim` lo atenúa.
- **Reloj en marcha:** `run` hace que el reloj de partido y el de posesión descuenten 1 s por segundo desde ese momento. Así un marcador puede acompañar una posesión real sin quedarse congelado.
- **Ejemplo:**
  `{"type":"scoreboard","league":"nba","logo":"leagues/nba.svg","teams":[{"name":"NAVY","color":"#0B1C3D","score":0},{"name":"WHITE","color":"#F2F2F2","score":0}],"period":"Q1","clock":"12:00","shot":24,"highlight":3.2,"y":600}`

## E2A League Comparison Intro
- **Archivo:** `template/src/t3d/broadcast.tsx` (`LeagueLogo`). Usa el elemento `leagueLogo` y la pantalla partida con `split.seam: "brand"` (costura fina azul marino y dorada).
- **Composición:** la pista NBA arriba y la de EuroLeague abajo. Cada logotipo oficial va sobre una placa blanca con `object-fit: contain`, así que nunca se deforma. Entra con opacidad y escala de 0,92 a 1 en 0,45 s, en el momento en que la voz nombra la liga.
- **Logotipos:** se leen de `template/public/leagues/nba.svg|png` y `euroleague.svg|png`. Si falta el archivo, se dibuja un hueco marcado como «LOGO PLACEHOLDER» con la ruta que hay que rellenar. Nunca se inventa un logotipo.

## E2A Natural Sports Narration
- **Escritura:** frases habladas y conectadas, sin «Rule number one». La voz explica el significado y los gráficos llevan las cifras.
- **Generación:** Deuce con eleven_v3, una sola toma de todo el guion para que el timbre y el contexto se mantengan. Pocas etiquetas: [curious], [interested], [surprised], [thoughtful] y [playful]. Nada de [shouting] ni [excited] en las cifras.
- **Postproducción** (`tactical/episodes/nbaeu-v2/_voice-v2.py` y `scripts/voice-dynamics.py --preserve` con curva plana):
  - no se corta nada, no se cambia la velocidad ni el tono, y las cifras no se refuerzan
  - solo se alargan unas pocas respiraciones en los cambios de bloque (+0,25 a +0,7 s), para que el gráfico tenga tiempo de leerse
- **Criterio de elección:** se elige la toma más creíble, no la más fuerte. Se compara con el mismo volumen percibido, mirando las pausas, la variación de tono y la continuidad.
