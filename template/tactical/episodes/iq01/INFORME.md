# E2A BASKETBALL IQ · EP 01 — CAN YOU FIND THE OPEN PLAYER?: informe de producción

26 nov 2026 · Rama `claude/project-thread-7z7nri` (repo e2a-tiktok-media, sin fusionar) · **No publicado ni programado.**

## Entregables
| Archivo | Qué es |
|---|---|
| `e2a-basketball-iq-01-social.mp4` | Versión principal, 1080×1920, 30 fps, H.264 + AAC 48 kHz, 32,7 s |
| `e2a-basketball-iq-01-trial.mp4` | Versión para trial reel: hook distinto (título "WHO'S OPEN? FIND HIM", cámara más alta) + zoom 3 %, color y EQ suave. Misma toma de voz |
| `e2a-basketball-iq-01.srt` | Subtítulos en inglés (16 bloques) |
| `GUION-Y-TACTICA.md` | Guion, tiempos, coordenadas y por qué C es la respuesta en esta posesión |
| `contact-sheet.jpg` | Un fotograma cada 1,5 s |
| `deuce-take-raw.mp3` | Toma original de la voz (no regenerar) |

## Sistema usado (verificado, estable)
- Base: rama de Zero Cut (contiene HORNS, 1-3-1, Arrow Press, 4 Rules y NBA vs EuroLeague). Estándar visual E2A v1 (estilo HORNS V2): jugadores 3D `v33` (compilador Realism V3.3 por jugada, el valor por defecto del motor no cambia), entorno `cinema`, marcadores de ataque/defensa, chips cortos.
- Novedades (opcionales, no cambian vídeos anteriores): jugadas 4c4 (`format: "4v4"` en el validador), equipaciones IQ por jugada (`kitSet: "iq"`: ataque claro con dorado, defensa azul marino) y la insignia de respuesta `letter` (A/B/C sobre el jugador, con estado tachado o resuelto).

## Control de calidad
- Jugada: 28/28 comprobaciones (4c4, velocidades, sin solapes, línea de pase libre, tirador detrás del arco y solo, y cada frase del guion comprobada en la pista).
- Encuadres: comprobador automático, los 8 jugadores dentro de cuadro en todos los planos de pregunta y cierre.
- Vídeo principal: qc-video PASS sin avisos; −14,6 LUFS, pico −1,3 dBTP. Parpadeo del suelo: 0 fotogramas malos de 980 (2 bajadas de luz breves coinciden con cambios de gráfico, no con el suelo).
- Audio: voz + música propia generada por código (sin muestras ni créditos). Sin botes de balón. Durante los 2 s de pensar solo queda un pad grave, sin percusión ni tic-tac.
- Créditos ElevenLabs: 461 (voz, una toma) + 156 (transcripción Scribe).

## Limitaciones conocidas
- En el plano de la pregunta los jugadores se ven pequeños: la media pista entera (15 m) tiene que caber en vertical.
- En el plano de A, X2 aparece con el brazo extendido hacia el balón y la postura parece algo forzada de cerca.
- Sin portada: la generada automáticamente se solapaba con las letras. Se puede elegir un fotograma en Instagram o la preparo aparte.
