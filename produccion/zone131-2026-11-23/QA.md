# E2A — 1-3-1 Zone Defense · QA (2026-11-23)

## 1. Táctica (jugadas)
- `test-play`: **86/86 comprobaciones genéricas + todos los claims PASS** (A 27/27, B 31/31, C 28/28). Informe completo: `TEST-PLAY.txt`.
- Claims clave (detalle en `TACTICAL-SOURCES.md`):
  - Trap A: X4–O4 0,93 m, X2–O4 1,01 m, X2–X4 1,37 m (dos ángulos, sin choque). X5 a 4,93 m de O4 (no es tercer trapper).
  - X3 sale y llega antes que X4: B 2,22 < 2,32 s y 4,05 < 4,37 s; C 2,12 < 2,18 s y 3,43 < 4,23 s.
  - B tardía: defensor más cercano a 1,97 m al lanzar, O3 a 6,89 m del aro (fuera de la línea FIBA), balón dentro → triple abierto.
  - C a tiempo: X3 a 1,31 m al lanzar, mano arriba, tiro fallado, sin +3.
  - El skip pasa **por encima** de la zona (arco 3,3 m), sin atravesar a X5/X3.
- **Fuentes de coaching NO verificadas en vivo** (DNS bloqueado en el contenedor). Las reglas siguen el prompt maestro.

## 2. Movimiento (Realism v33, 120 Hz, 10 jugadores)
Resumen en `QC-REALISM-V33.json`.
| Jugada | Deslizamiento de pie >2 cm | Deslizamiento máx. | Balón-cuerpo | Interpenetración visible | Aceleración máx. de pelvis |
|---|---|---|---|---|---|
| A | 0 | 0,8 cm | 2 muestras a 6,5 s (fin de jugada, **no se muestra**: el montaje usa A hasta 4,4 s) | 1 (mismo instante, no se muestra) | 276 m/s² |
| B | 0 | 1,2 cm | 0 | 0 | 384 m/s² |
| C | 0 | 1,0 cm | 0 | 0 | 384 m/s² |
- Los «pops» de cabeza, pelvis y muñeca (pequeños tirones en arranques bruscos) son una limitación conocida de V3.3 y no se aprecian a velocidad normal.

## 3. Encuadre (frame-fit, banda segura: arriba 380, abajo 1330, laterales 20 px)
- Planos generales (hook, gamble, shape, corner, rot, reset, skip, first, sprint, close): **0 fotogramas marcados**.
- trap (cámara nueva): 9 fotogramas al entrar el plano (X2 aún acercándose roza la banda de subtítulos). Con el trap formado, todos los jugadores quedan por encima del subtítulo.
- three / ontime: 4 fotogramas al final de ontime (X3 volviendo al ala roza el borde inferior).

## 4. Revisión de render
- Master completo revisado con hoja de contactos (20 fotogramas).
- **Fallo corregido:** en el primer render, el plano del trap quedaba en el tercio superior contra la grada. Se reencuadró la cámara TRAP y se re-renderizaron solo esos 67 fotogramas (362–428), que se empalmaron en el master.

## 5. Audio y archivo
- Master: H.264 1080×1920, 30 fps, 1289 fotogramas, 42,94 s, AAC 48 kHz. Loudness **-14,0 LUFS**, true peak **-3,7 dBFS**.
- Voz: una sola toma de Deuce (sin cortes audibles; silencios añadidos entre frases). Música: `cine_b` generada con `--no-sfx`.
- **Sin sonido de bote de balón** ni otros SFX (regla del propietario 18-11).
- Trial: `E2A-ZONE-131-TRIAL.mp4` (zoom 3 %, grade, EQ suave de voz, re-encode): SSIM 0,66 frente al master, -14,5 LUFS. Misma toma de voz, sin créditos nuevos.

## 6. Defectos conocidos (no bloqueantes)
- Tirones leves de pelvis/cabeza en arranques bruscos (limitación de V3.3).
- En el plano general los jugadores se ven pequeños (encuadre de media pista completo, igual que la 2-3 MASTER).
- En el plano del triple, el arco del balón sale por arriba del encuadre un instante.
- Fuentes tácticas sin verificación en vivo (ver sección 1).
