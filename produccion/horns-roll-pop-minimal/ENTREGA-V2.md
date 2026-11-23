# HORNS V2 — ritmo, inicio más visual y estándar por defecto (2026-11-23)

**Estado:** V2 entregada para revisión. **No se ha subido, publicado ni programado nada.** Coste: **0 créditos** de ElevenLabs y 0 €. Se reutiliza la misma toma de Deuce del FINAL.

## Archivos (`tactical-studio/horns/entrega-v2/`)
| Archivo | Qué es |
|---|---|
| `E2A-HORNS-ROLL-POP-V2.mp4` | 1080×1920, 30 fps, H.264, 1166 fotogramas, 38,87 s. Audio: −14,1 LUFS, pico −1,5 dBTP. md5 `3a9942b56838395a52fcabdcae7e71df` |
| `E2A-HORNS-ROLL-POP-V2-TRIAL.mp4` | Versión para el trial reel (zoom 3 %, color, nitidez, EQ suave, misma toma) |
| `horns-roll-pop-minimal-PREVIEW-V2.mp4` | V2 a 540×960 |
| `contact_sheet_v2.jpg` | 12 fotogramas de la V2 |

## 1. Silencios corregidos (sin voz nueva)
Medí la distancia entre el final de cada frase y el inicio de la siguiente en el FINAL. Había tres huecos largos:

| Hueco | FINAL | V2 | Qué hay en pantalla |
|---|---|---|---|
| «behind the arc» → «Now this defender…» | 1,97 s | 0,92 s | congelado del rehook |
| «open for three» → «If he stays…» | 5,16 s | 2,90 s | el triple entra + chip **THREE.** + sello de reset |
| «might be there» → «Same setup» | 4,08 s | 2,56 s | la bandeja + chip **LAYUP.** |

- La toma no se estira ni se acelera: solo se acortan los silencios insertados entre frases (`tactical-voice.py`, `gapFill: silence`).
- Los dos huecos que quedan por encima de 2 s van sobre el remate real, con un chip de resultado, así que no hay aire muerto.
- Además, el triple y la bandeja ahora van cerca del tiempo real (antes ~0,5×), que era uno de los pendientes del FINAL.
- Duración: 43,7 → 38,9 s.

## 2. Inicio más visual (ataque y defensa)
- Nuevo marcador de jugador en el motor (`marker`): **ataque = anillo dorado sólido con brillo suave**; **defensa = anillo blanco segmentado, más fino**. Cambian forma y color, así que se distinguen al primer vistazo.
- Aparición **secuencial**: O1, O5, O4, O3, O2 y luego X1, X5, X4, X3, X2, cada 0,17 s, con un pulso suave al aparecer.
- **Leyenda** ATTACK / DEFENSE arriba a la izquierda mientras dura la presentación.
- X4 (el defensor del gancho) se realza al final de la toma para enlazar con la acción.
- Se quitan los anillos planos anteriores. Sin textos extra: los dorsales ya identifican a cada jugador.

## 3. Estándar visual por defecto
- Documento: `E2A_BASKETBALL_VISUAL_STANDARD_V1.md`.
- Preset: `template/tactical/presets/e2a-visual-standard-v1.json` (motor v33, `env: cinema`, marcadores, leyenda, cámara, ritmo, audio y QA).
- Guardado en la memoria del proyecto como regla del propietario, así que los próximos vídeos lo usan por defecto.
- **Lo que no he cambiado sin preguntarte:** el motor por defecto del código sigue siendo legacy (de reserva) y la tarea diaria automática no se ha tocado, porque publica sola.

## QA
- `frame-fit.mts`: 0 fotogramas marcados de 1166 (banda 380–1330 px).
- Remaps monótonos en las 7 tomas. Jugadas sin cambios: test-play 49/49, test-branches 13/13 y balón-cuerpo 0 siguen valiendo.
- Chips de resultado movidos a y = 1230 tras ver que en y = 980 tapaban a un jugador; se volvieron a renderizar solo esos fotogramas.

## Pendientes (los mismos del FINAL)
Pequeños tirones de muñeca y tobillo en el bloqueo y en las recepciones. Ninguno es de balón-cuerpo.
