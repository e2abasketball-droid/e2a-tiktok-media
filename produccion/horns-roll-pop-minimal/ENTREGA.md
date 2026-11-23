# HORNS: THE DEFENDER'S DILEMMA — entrega FINAL con voz (2026-11-23)

**Estado: FINAL con voz aprobada.** El propietario autorizó la voz el 23-11 a las 09:26 (Madrid). **No se ha subido, publicado ni programado nada**, ni se ha tocado Metricool o ninguna tarea. Coste: 461 créditos de ElevenLabs (una toma de Deuce, eleven_v4); Scribe 0 créditos; 0 €.

## Archivos FINAL (`tactical-studio/horns/entrega-final/`)
| Archivo | Qué es |
|---|---|
| `E2A-HORNS-ROLL-POP-FINAL.mp4` | 1080×1920, 30 fps, H.264 High, yuv420p, 1311 fotogramas, 43,70 s, 12,5 MB. AAC 48 kHz: −14,5 LUFS, pico −1,7 dBTP, LRA 6,8. md5 `56216d46e62aa944fde3ddc7eded0990` |
| `E2A-HORNS-ROLL-POP-FINAL-TRIAL.mp4` | Versión para el trial reel (regla del propietario): zoom 3 %, más saturación, contraste y nitidez, EQ suave de voz, misma toma. SSIM 0,70 frente al FINAL. md5 `f93ff2d127e0e903c00911f8d526ec95` |
| `horns-roll-pop-minimal-PREVIEW.mp4` | FINAL a 540×960 |
| `contact_sheet.jpg` | 12 fotogramas del FINAL (también en esta carpeta del repo) |

## Qué cambió con la voz
- Una sola toma con el guion exacto (73 palabras) y tres etiquetas de tono. No se estiró ni se aceleró: solo se añadieron silencios digitales entre frases (`scripts/tactical-voice.py`, `gapFill: silence`) para que cada frase caiga en su toma. Episodio de voz: `template/tactical/episodes/horns/`.
- Cortes y subtítulos recalculados con los tiempos reales (Scribe): hook 0, setup 3,49, action 9,26, read 17,39, branchA 20,73, branchB 28,15, close 35,23; fin 43,70 s.
- `frame-fit` con los nuevos cortes: 0 fotogramas marcados de 1311.
- Mezcla offline (`MEZCLA.txt`): voz comprimida suave, música propia regenerada a 43,7 s con acentos en el rehook y el cierre, con ducking. Sin bote, chirridos ni whooshes.
- Dentro de cada frase Deuce habla a su ritmo natural (~165 palabras por minuto); contando las pausas, el vídeo va a ~108. Es más rápido por frase que las 112–122 del estilo propuesto.
- Scribe da tiempos por palabra algo aproximados; revisé la sincronía en fotogramas sueltos, no palabra por palabra.

## Veredicto FINAL
- **GO para tu revisión** y, si te gusta, para programarlo cuando lo pidas.
- Siguen abiertos los pendientes de movimiento de abajo (ninguno de balón-cuerpo).

---

# Entrega v1 anterior (sin voz)

**Estado: VISUAL_MASTER_PENDING_AUDIO. NO-GO para publicar** hasta que haya voz aprobada. No se ha subido, publicado ni programado nada. No se ha tocado Metricool ni ninguna tarea. Coste: 0 € y 0 créditos de ElevenLabs.

## Archivos
Los MP4 no van al repositorio. Están en la carpeta del proyecto `tactical-studio/horns/entrega-v1/`:

| Archivo | Qué es |
|---|---|
| `E2A-HORNS-ROLL-POP-VISUAL_MASTER_PENDING_AUDIO.mp4` | Máster 1080×1920, 30 fps, H.264 High, yuv420p, 1289 fotogramas, 42,967 s, 12,8 MB. Audio: solo la música propia (AAC 48 kHz). md5 `8ee1c5d2841383f8b3dfe203a0031d83` |
| `horns-roll-pop-minimal-PREVIEW.mp4` | El mismo máster a 540×960 para revisar en el móvil. md5 `c222022c4cb6a7953e47d76f9ae47e4e` |
| `contact_sheet.jpg` | 12 fotogramas extraídos del máster final (también en esta carpeta del repo) |

**No hay `E2A-HORNS-ROLL-POP-FINAL.mp4`**, porque no existe audio aprobado (regla del documento maestro).

En el repositorio, rama `claude/horns-roll-pop-minimal-v1` (sin fusionar):
- `FUENTES-Y-TACTICA.md`: fuentes, convención, cobertura, marcas de tiempo de la jugada.
- `GUIÓN-Y-TIMINGS.md`: guion, tiempos guía, tomas y ruta editable.
- `CÁMARA-Y-COMPOSICIÓN.md`: cámara única y comprobación de encuadre.
- `PLAY-QC.json`: resultados de test-play, test-branches y QC de realismo.
- `PRODUCTION_STYLE_E2A_MINIMAL_V1.md`: propuesta de estilo, no activada.
- Código: `template/tactical/specs/_gen-horns-roll-pop.py` (jugadas), `template/tactical/episodes/_gen-horns-roll-pop.py` (montaje), `tools/audio/horns_minimal_bed.py` (música).

## QA hecha (resultados reales)
| Prueba | Resultado |
|---|---|
| `test-play.mts` (A y B) | **49/49 PASS**, con claims ligados a cada frase |
| `test-branches.mts` | **13/13 PASS**: 10 jugadores idénticos hasta el fork (máx. 0,12 cm), balón idéntico, X4 lee distinto (3,44 m), triple anotado a 7,27 m frente a bandeja a 1,32 m |
| `qc-realism-v33.mts` (10 jugadores por rama) | contacto balón-cuerpo **0** en A y en B; 18 filas de aviso en A y 17 en B (ver pendientes) |
| `frame-fit.mts` en todos los fotogramas | **0 de 1289 marcados** (banda 380–1330 px, margen lateral 12 px) |
| `ffprobe` | ver tabla de archivos |
| Loudness | música sola: −24,4 LUFS integrados, pico −9,3 dBFS, LRA 1,1 LU. Es nivel de cama para ir bajo la voz, no de mezcla final |
| Hoja de 12 fotogramas y uniones | revisadas. Las dos uniones del render (fotogramas 496/497 y 620/621) son continuas |

## Corrección hecha durante la QA
El primer montaje tenía un zoom del 10 % en el rehook. `frame-fit` mostró que **O3 y X3 salían del cuadro** por la derecha. Quité el zoom y volví a renderizar solo esos 124 fotogramas.

## Pendientes y defectos conocidos (sin esconder)
1. ~~Sin voz~~ Resuelto en el FINAL (arriba).
2. **Movimiento (QC v33, avisos P1/P2, ninguno de balón):**
   - O1, muñeca izquierda, 541–666 m/s² a 5,3–5,8 s, al usar el bloqueo. Compartido por las dos ramas.
   - O4, muñecas, ~450–460 m/s² en la recepción de A (8,2 s).
   - O5 en B: cabeza 210 m/s² a 8,17 s y tobillo 921 m/s² a 8,5 s, en el paso de reunión.
   - Algún codo de X4 por encima de 155°.
   - A velocidad normal no se ven como saltos claros en la hoja, pero no los declaro resueltos.
3. **Cámara lenta del remate:** el triple de A y la bandeja de B van a ~0,5×, no casi a tiempo real como pide el estilo, para que las frases quepan sobre la acción. Se puede ajustar al meter la voz.
4. **Duración de tomas:** hook (2,8 s) y read (3,2 s) quedan por debajo de 4 s, y action (8,2 s) y close (8,3 s) por encima de 8 s.
5. **Encuadre justo:** los tiradores de las esquinas quedan a 17–25 px del borde lateral.
6. **B arranca 0,3 s antes del fotograma de decisión** (6,3 s, idéntico en A y B) y llega al 6,6 bajo el sello de reset.
7. **Divergencia del balón en V3.3:** la anticipación de la mano diverge desde 6,70 s. Por eso el fotograma de decisión del vídeo es el 6,6 s, donde todo es idéntico.
8. **Motor:** usa el renderer V3.3 por props (`athleteRenderer: "v33"`). Legacy sigue siendo el motor por defecto, y V3.1 y V3.2 no se tocan.
9. **Coste de render:** CPU (swangle). Las dos mitades tardaron 21 y 26 min, y la corrección otros 9 min.

## Veredicto
- **GO** para revisión interna del aspecto visual, la táctica y el montaje.
- **NO-GO** para publicar hasta que haya voz aprobada y se haga el FINAL con mezcla.
