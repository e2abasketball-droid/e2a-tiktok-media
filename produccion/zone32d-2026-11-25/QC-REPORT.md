# E2A — 3-2 Zone Defense: informe de calidad (2026-11-26)

Estado: **entregado para revisión, NO publicado ni programado.** Rama `claude/project-thread-rytopx` (sin fusionar).

## Entregables (`/mnt/project-files/tactical-studio/zona-3-2-defensa/`)
| Archivo | Datos |
|---|---|
| `E2A-3-2-ZONE-DEFENSE-FINAL.mp4` | 1080×1920, 9:16, 30 fps, H.264 + AAC 48 kHz, 48,39 s, −14,5 LUFS, pico −1,3 dBTP |
| `E2A-3-2-ZONE-DEFENSE-TRIAL.mp4` | copia trial (zoom 3 %, color/nitidez, EQ suave), misma toma de voz, SSIM 0,585 vs FINAL, −15,6 LUFS, −1,5 dBTP |
| `E2A-3-2-ZONE-DEFENSE-COVER.png` | fotograma limpio del propio vídeo (título «3-2 ZONE DEFENSE», mismo estilo que la serie) |
| `E2A-3-2-ZONE-NARRATION-SAMPLE.mp3` | 16,2 s: hook + rotación + CTA, cortados de la toma aprobada |
| `REGLAS-ROTACION-3-2.md`, `RUTAS-Y-HERRAMIENTAS.md` | reglas X1–X5 por posición del balón; rutas y herramientas |
| `E2A-3-2-ZONE-CONTACT-SHEET.png` | hoja de contactos del MP4 exportado |

## Qué se usó
- Proyecto 2-3 de referencia: V2 Dynamic Coverage (`claude/zona-2-3-v2`, `coverage3d.tsx`) y su continuación 1-3-1 (`_gen-zone131.py`). No se modificó ninguno.
- Motor: Tactical3DV2 + Realism V3.3 por episodio (`athleteRenderer: v33`, `env: cinema`): el más estable de los reels del 23–25 nov. El valor por defecto global no cambia.
- Reutilizado: cancha, jugadores, cámaras orbitales, marker/legend, pins, chips, títulos, subtítulos, Dynamic Coverage (nuevo esquema `3-2`), passLane, route, glow, freeze, rewind, Floor Graphics Stability Standard, Voice Dynamics, motor de música.
- Nuevo: 4 jugadas 3-2 (ala+esquina, poste alto, tiro+box-out, circulación final), esquema de áreas `3-2`, cara `rim` para el box-out, generador del montaje con opción `--trial`.

## Pruebas ejecutadas (todas sobre datos reales; las de vídeo sobre el MP4 exportado)
| Prueba | Resultado |
|---|---|
| `test-play` (física, 5v5, sin teletransportes, aceleración ≤ 22 m/s², carriles de pase, tirador tras el arco) | 100/100 |
| Claims tácticos ligados al guion (formación 3-2 vs 1-2-2, closeout, desplazamiento, esquina, aro protegido, sin dobles, poste alto, box-out) | todos PASS (TEST-PLAY.txt) |
| `qc-tactical3d` (anclas, cámaras ≤ 0,9 m/fotograma, pins sobre su jugador, zona segura) | 40/41: solo falla la duración 30–40 s (48,4 s) |
| `frame-fit` (planos abiertos: los 10 jugadores en el marco; planos cercanos: sus protagonistas) | 0 fotogramas marcados en los planos comprobados |
| `qc-floor-flicker` en el MP4 | 0 fotogramas malos, 0 parpadeos, 0 caídas en los 5 tramos congelados |
| `qc-video` en el MP4 | PASS (formato, −14,5 LUFS, TP −1,3) |
| `voice-energy-qc` | rango F0 9,2 semitonos (p5–p95), «shut» 225 Hz vs mediana 160 Hz, energía 20,9 dB |
| Revisión visual | preview a media resolución completo + 18 fotogramas del FINAL |

## Problemas detectados y corregidos
- Pase O1→O3 atravesaba a X2 (carril < 0,6 m): ala izquierda más alta y closeout por debajo de la línea.
- Aceleraciones > 22 m/s² en el closeout de X5 y en la vuelta de X3: trayectos más largos.
- Cámaras de tres cuartos mal orientadas en el primer animatic (casi cenitales): corregidas con yaw/pitch reales.
- «2 DOWN LOW» quedaba bajo el tablero; chips de la esquina tapaban pins: recolocados.
- Box-out ilegible en plano general: empuje de cámara al lado fuerte + pins «FIND A BODY» / «BOX OUT».
- Pin «REACT» pasaba sobre O1: aparece más tarde.
- La cara `rim` rompía el rig: soportada (ninguna jugada antigua la usaba).
- Portada con fuente de reserva y título cortado: sustituida por fotograma limpio del vídeo.

## Límites y pendientes (honesto)
- **Duración 48,4 s** (objetivo 35–42 s). La toma completa duraba 49,2 s sin pausas largas; se quitaron «The goal?» y «On every shot:» y no se aceleró la voz. Para bajar a ~42 s habría que recortar frases enteras (0 créditos) o pedir una toma más corta (créditos).
- Fuentes tácticas: páginas de coaching bloqueadas (DNS); reglas basadas en fragmentos de HoopTactics / Coach's Clipboard. No verificadas en vivo.
- No hay primitiva de rebote: el box-out se ve con el balón en el aro; el rebote no se captura.
- Sin efectos de sonido (ni botes). Música propia sintetizada (`e2a_music.py`, uso comercial sin licencia).
- SSIM del trial 0,585 (algo más distinto que el objetivo 0,7–0,8).
- No se revisó con audio en un móvil real (el contenedor no reproduce sonido); la sincronía voz-acción se comprobó con las marcas de palabra.
