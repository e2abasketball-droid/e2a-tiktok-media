# Zero Cut V2: música nueva, transiciones y derechos

## Pista
- **"Zero Cut Dark"**: dark techno × industrial × breakbeat, **144 BPM**, re frigio (D–Eb–Bb–C), casi sin melodía.
- **Origen:** sintetizada por código propio de E2A (`tools/audio/darktech_states.py`, rama `claude/project-thread-1690kk` del repo e2a-tiktok-media). Sin samples, sin loops de terceros, sin servicios de música con IA. **100 % propiedad de E2A**, uso comercial libre, sin Content ID.
- **Stems:** batería, bajo, sintes y efectos se generan por separado (`--stems`).
- **Sin botes de balón:** en los tramos lentos no hay bombo (un golpe grave aislado podría sonar a bote). Ningún SFX en el vídeo.

## Estados de energía (sincronizados con eventos reales de la animación y de la voz)
| Estado | Qué suena | Dónde |
|---|---|---|
| **A · energía** | Bombo 4/4 distorsionado, cajas industriales en 2 y 4 + fantasmas, hats metálicos a semicorcheas, bajo reese rodante a contratiempo + sub, stabs oscuros | 0–9,2 s · 19,4–26,5 s · 32,1–38,5 s · 43,7–49,4 s |
| **B · cámara lenta** | Mismo tempo (144) con sensación de **media parte (72 BPM)**: palmada enorme con reverb en el tiempo 3, tic de hats en corcheas, drone de sub y pad oscuro que respira. La pista NO se ralentiza | 9,2–19,4 s (defensor) · 26,5–32,1 s (ayuda) · 38,5–43,7 s (lección) |
| **C · liberación** | Subida de ruido invertido que resuelve justo en el evento + golpe de stab, y vuelve A completo | **19,36 s** = primer paso explosivo del cortador ("CUTS") · **32,06 s** = el pase a la esquina ("FIND") · **43,69 s** = la pregunta final ("So…") |

Los tiempos salen del generador del montaje (`_gen-zerocut-v2.py --plan`): si cambia la edición, la música se regenera en 3 s y sigue cuadrando.

## Prueba A/B
`ab-camara-lenta-musica-V1.mp4` y `ab-camara-lenta-musica-V2.mp4`: el mismo tramo (9–24 s, defensor + corte + bandeja) con la música D&B de la V1 y con la nueva. Con la V2 la cámara lenta suena pesada y tensa (media parte) y el ritmo vuelve en el momento exacto en que el cortador acelera.

## Voz
- Deuce, eleven_v3. Hook de la V1 (toma aprobada, 0 créditos nuevos) + **1 toma nueva de 552 créditos** (aprobada por el owner). Transcripción Scribe: 0 créditos.
- Mezcla final: voz siempre por encima de la música (ducking), −14 LUFS ±1, pico ≤ −1 dBTP.
