# NBA vs EuroLeague: informe de QA del archivo exportado (2026-11-24)

Archivo: `E2A-NBA-VS-EUROLEAGUE-FINAL.mp4`. Sin publicar.

## Datos técnicos (ffprobe / ebur128)
| Control | Resultado |
|---|---|
| Resolución | 1080 × 1920 |
| Fotogramas | 30 fps constantes (r = avg = 30/1), 1.373 fotogramas |
| Duración | 45,8 s (pedido: unos 40–45 s) |
| Vídeo / audio | H.264 High yuv420p / AAC 48 kHz 192 kb/s, faststart |
| Sonoridad | -14,8 LUFS integrados, pico real -2,7 dBFS, LRA 3,0 LU. Sin saturación. |
| Sonido de bote | Ninguno. Música E2A generada sin SFX (`--no-sfx`), voz Deuce y música. |

## Controles automáticos
- **qc-video:** PASS. Un aviso «transient» en 27,33 s: es el barrido intencionado al entrar en la falta NBA, no un fallo.
- **qc-floor-flicker:** 0 fotogramas negros o rotos. Congelado de la técnica (38,3–39,2 s): diferencia media 0,26, 0 parpadeos, 0 caídas. El oro del plano del reloj sube por escalones (se encienden los cuartos Q1–Q4); no es parpadeo.
- **qc-nbaeu (geometría y reglas sobre los cuerpos):** 7/7 PASS. Suelas del tirador entre 6,815 y 7,157 m (triple FIBA, dos NBA). El balón entra en los dos tiros. En los 3 segundos, X5 está en la zona, sin nadie a menos de 1,2 m y sin atacantes en la zona ni tiro.
- **Voz:** rango de tono 12,7 semitonos y energía 21,4 dB (4 Basketball Rules: 10,2 y 20,6). FORTY-EIGHT, FORTY, FIVE y SIX reforzados.

## Revisión sin sonido (hecha dos veces)
Primera pasada, con 3 defectos corregidos y re-renderizados:
1. El chip «BALL IN THE FRONTCOURT» se solapaba con el título «DEFENSIVE 3 SECONDS». Ahora entra 0,6 s después.
2. La línea dorada «DO YOU PREFER?» caía sobre la unión de las dos pistas. Se ha subido.
3. La palabra NBA / EUROLEAGUE pintada en el suelo competía con los subtítulos. Se ha suavizado.

Segunda pasada sobre el archivo final: hook, relojes 48/40, arcos con medida, tiro 3/2, faltas 5/6, salida de pista, cuenta 1-2-3 con técnica y versión EuroLeague, y cierre dividido. Todo legible y sin textos sobre los jugadores ni sobre las líneas clave.

## Limitaciones conocidas (menores)
- En el plano de faltas, la palabra del suelo queda bajo el subtítulo y se ve en parte. Se lee bien, pero es un detalle.
- Las reglas oficiales no se pudieron abrir en directo desde este entorno (ver `VALIDACION-REGLAMENTARIA.md`). Conviene que una persona compruebe los 4 puntos antes de publicar.

## Versión trial
`E2A-NBA-VS-EUROLEAGUE-TRIAL.mp4`: misma toma de voz y mismo montaje, con zoom del 3 %, color y nitidez algo más altos y una EQ suave en la voz. SSIM 0,64 frente al original, -15,3 LUFS.
