# Zero Cut: comparación V1 → V2

| | V1 (`e2a-zero-cut-social.mp4`) | V2 (`e2a-zero-cut-v2-social.mp4`) |
|---|---|---|
| Duración | 40,9 s | 49,4 s (cada tramo añadido es cámara lenta explicativa, la segunda lectura o el cierre nuevo) |
| Música | Drum & bass 168 BPM, sonaba alegre | Dark techno / industrial 144 BPM propio, con 3 estados: A energía, B media parte en la cámara lenta, C liberación exacta en la aceleración, el pase a la esquina y la pregunta final |
| Hook | YOU'RE NEVER GOING PRO / IF YOU CAN'T READ THIS | Igual (misma toma de voz), arranca con el corte ya en marcha |
| Error del defensor | 1 plano POV + pies (4 s), poco claro | 3 planos en cámara lenta (geometría → pie plantado y cadera → flecha roja del compromiso + espacio dorado detrás) y el plant del cortador dentro del plano siguiente |
| Corte y bandeja | Varios planos; el cortador se paraba en el falso handoff y la bandeja era un saltito de tiro | Un solo plano continuo: plant real (el motor lo detecta y apoya el pie de fuera), el ritmo vuelve en "CUTS", recepción en carrera, dos pasos de recogida y despegue de bandeja más alto |
| Defensor | Se giraba 0,30 s después del corte | Se queda comprometido arriba y se recupera tarde (0,38 s) |
| Segunda lectura | Cenital lejano, jugadores pequeños | Cenital breve para situar → acercamiento a la ayuda y a la esquina; la esquina solo se ilumina cuando el defensor ya ha rotado; línea de pase roja bloqueada + línea dorada fina al tirador |
| Cierre | BASKETBALL IQ + logo | ONE CUT / TWO READS con la misma cámara para las dos lecturas → punto de decisión con las dos reacciones posibles (fantasma rojo) → READ THE DEFENSE → DO YOU HAVE WHAT IT TAKES?, que enlaza con el primer fotograma del hook |
| Voz | 1 toma (572 cr) | Hook reutilizado + 1 toma nueva (552 cr) |

## Componentes reutilizables nuevos o mejorados
- `tools/audio/darktech_states.py`: generador de música por estados (A/B/C) a partir de un plan de tiempos del montaje, con stems.
- `tactical/specs/_gen-zerocut-v2.py`: fusiona dos carreras de un jugador en una sola trayectoria para que el motor genere un **plant** real en un cambio de dirección (antes se paraba en seco).
- `compile33.ts`: la altura de salto `H` de una bandeja (opcional por evento) también fija el momento del despegue: los dos pasos de recogida cuadran con el salto. Opt-in: los vídeos anteriores no cambian.
- `_gen-zerocut-v2.py --plan`: el montaje exporta el plan musical (estados y liberaciones), así la música siempre cuadra con la edición.
- `_voice-zerocut2.py`: montaje de voz a partir de una toma sin regenerar, con corrección automática del desfase de los tiempos de Scribe.
- Gráficos usados en 3D: `arrow3d` (compromiso del defensor), `openLane` (espacio detrás), `ghost` (reacción alternativa), `ripple` (ayuda), `passLane` + `blocked`.

## Limitaciones que siguen
- El motor V3.3 aún no tiene una bandeja con despegue a una pierna: V2 usa el salto de tiro con más altura y dos pasos de recogida (mejor que la V1, no perfecto).
- No he probado Blender ni cambiado el sistema de personajes: el brief pide hacerlo solo si se demuestra una mejora, y el cambio de movimiento real estaba en la coreografía.

## Control de calidad V2
- 1080×1920, 30 fps constantes, H.264, AAC 48 kHz, **49,36 s**.
- **−14,8 LUFS integrados, pico −1,3 dBTP, LRA 4,1.** qc-video: PASS sin avisos.
- Parpadeo del suelo: 0 fotogramas malos en 1.480; congelaciones estables.
- Jugadas: comprobador táctico 25/25 (lectura 1) y 24/24 (lectura 2): sin teletransportes, velocidades y aceleraciones reales, la defensa reacciona después del ataque.
- Encuadres revisados con el comprobador automático y fotogramas de prueba: ningún jugador clave fuera de cuadro en los planos explicativos.
- Audio: solo voz + música propia, sin botes ni SFX.
