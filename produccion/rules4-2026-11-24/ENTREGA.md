# Entrega: Reel «4 RULES EVERY PLAYER MUST KNOW» (2026-11-24)

Estado: **entregado para revisión, sin publicar.** Rama `claude/project-thread-qocfjn` (sin fusionar). Motor por defecto sin cambios.

## Archivos (en `/mnt/project-files/tactical-studio/4-rules/`)
| Archivo | Qué es |
|---|---|
| `E2A-4-BASKETBALL-RULES-FINAL.mp4` | Máster: 1080×1920, 30 fps, H.264 + AAC, 41,95 s, −14,3 LUFS, TP −1,5 dBTP |
| `E2A-4-BASKETBALL-RULES-TRIAL.mp4` | Variante para trial reel: zoom 3 %, grade y EQ de voz suaves, misma toma. SSIM 0,60, −15,3 LUFS, TP −1,2 |
| `E2A-4-RULES-NARRATION-TEST.mp4` | Extracto de narración (12,8 s): hook + bloque Scoring (crescendo ONE/TWO/THREE) |
| `E2A-4-RULES-CONTACT-SHEET.png` | Hoja de contactos del MP4 exportado |
| `PRESET-NARRACION-ENERGICA.md` | Nuevo preset de narración «Energía educativa» v1 |
| `REFERENCIA-Y-REGLAS.md` | Análisis de la referencia y tabla de verificación reglamentaria |

## Motor y recursos reutilizados
- Tactical3DV2 (Remotion + three.js), Realism V3.3 (`athleteRenderer v33`, play `v33: compile`), entorno `cinema`, mallas V3.2, logotipo 2026.
- Estándar visual HORNS v33 (pins, leyendas, ritmo) y Floor Graphics Stability Standard (un gráfico por idea, alturas fijas, sin parpadeo).
- Música original `music/e2a_music.py` (trap_b, `--no-sfx`): sin botes de balón.
- Cadena de voz: `voice-dynamics.py --preserve` del Arrow Press.

## Mejoras nuevas (todas opt-in; los vídeos y el motor por defecto no cambian)
- `compile33`: `v33extra` (pasos y pivotes explícitos), `v33still` (pies quietos mientras el cuerpo gira), evento de tiro `H` (altura de salto; TL casi sin salto).
- `motion33`: `v33grab` (mano que agarra la cadera de un rival: falta por holding sin atravesar cuerpos).
- Gráficos 3D de reglas `src/t3d/rules3d.tsx`: anillo de pie de pivote (sube con la suela), anillo de balón, marca de mano, zona de 2 rellena, línea de 3 trazada.
- Pantalla: `score` (+1/+2/+3 con pop), `verdict` (✓/✕ rojo/verde), `section` (01–04).
- Voz: `scripts/voice-emphasis.py` (ganancia por palabra, sin cambio de tono ni tiempo) y `scripts/voice-energy-qc.py` (rango de F0 y energía).
- QC reglamentario sobre los cuerpos renderizados: `scripts/qc-rules4.mts`.

## Cómo se verificaron las reglas
- `qc-rules4.mts` mide los cuerpos V3.3 a 60 fps: **8/8 jugadas PASS** (travel 11/11, doble regate 7/7, TL/2/3/línea 6/6 cada una, falta 6/6, saque 4/4). Detalle por regla en `REFERENCIA-Y-REGLAS.md`.
- Puntos clave: el pie de pivote no se desliza y vuelve al suelo con el balón en las manos; nadie toca el balón entre los dos regates; el tirador de tres tiene las dos suelas a más de 6,75 m; en el caso «ON THE LINE = 2» la puntera pisa la línea.
- **Limitación:** el PDF FIBA OBR 2026 v1.1 no se pudo abrir desde el contenedor (red bloqueada). Se usó el texto vigente que conocemos (2024). Recomendado: revisión humana rápida con el PDF de 2026.

## QC del MP4 exportado
- Técnico y audio (`qc-video.py`): PASS. 1080×1920, 30 fps, H.264, 41,95 s (dentro de 38–42 s), −14,3 LUFS, TP −1,5.
- Estabilidad de gráficos (`qc-floor-flicker.py`): 0 frames negros o en mosaico, **0 parpadeos y 0 caídas** en los 5 tramos congelados.
- Revisión visual de 26 fotogramas: subtítulos legibles y sin solapes, por encima de la zona de la interfaz (y = 1390), rótulos y marcadores visibles.
- Voz: rango de F0 10,2 semitonos y desviación 3,66 st (Arrow V3: 8,9 / 3,28; Zona 1-3-1: 3,13). Rango de energía 20,6 dB (HORNS 15,6). TRAVEL! y THREE! son las palabras más fuertes del bloque.

## Defectos corregidos durante la producción
- Pivote: el cuerpo no quedaba sobre los pies (pelvis desplazada 0,24 m). Ahora la trayectoria gira alrededor del pie de pivote y los pies se quedan quietos.
- Falta: el balón atravesaba el torso del defensor (ahora bota con la izquierda) y la palma no tocaba la cadera (ajustado a ± 7 cm).
- Cámaras: cabezas y pies bajo los subtítulos y balón fuera de cuadro. Encuadres reajustados con `frame-fit`.
- Zona de 2 invisible por profundidad: elevada a 2 cm, opacidad 0,3.
- Trial: el true peak salía a −0,8 dBTP. Corregido a −1,2 con −0,4 dB.

## Pendiente o conocido (no bloqueante)
- PDF FIBA 2026 no verificado en directo. El brief cita el Art. 42; en la edición 2024 la penalización por faltas de equipo es el Art. 41.
- `qc-tactical3d` marca «duración 30–40 s» como fallo a 41,95 s. Se mantiene la duración del brief (38–42 s).
- La zona de 2 rellena se ve algo grisácea sobre el parqué.
- El crescendo ONE/TWO es leve (−17,5 / −17,2 dBFS). THREE! sí destaca (−14,9).
- Inicio del bloque Doble regate (14,0–16,0 s): un reflejo de luz claro en el lado derecho del parqué (aviso `flat_band`, no es un objeto delante de la cámara).
- La cámara del saque de banda es amplia.

## Archivos reutilizables (repo e2a-tiktok-media, `template/`)
- `tactical/specs/_gen-rules4.py` → `tactical/plays/rules4-*.json` (8 jugadas: travel, dribble, ft, two, three, line, foul, throwin).
- `tactical/episodes/_gen-rules4.py` y `tactical/episodes/rules4/` (episodio, palabras, curvas de voz).
- `src/t3d/rules3d.tsx` y los opt-ins de `compile33.ts`, `motion33.ts`, `Tactical3D.tsx` y `overlays3d.tsx`.
- `scripts/qc-rules4.mts`, `scripts/voice-emphasis.py`, `scripts/voice-energy-qc.py`.
- `public/rules4/` (voz final y música, reutilizables en una re-edición sin gastar créditos).

## Coste
ElevenLabs: una toma eleven_v3 de Deuce, **733 créditos** (aprobada por el propietario). Scribe: 0. Sin otros servicios de pago.
