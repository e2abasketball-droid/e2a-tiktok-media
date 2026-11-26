# Parte 2: QA del MP4 exportado y componentes reutilizables

## Archivos (en `/mnt/project-files/tactical-studio/4-rules-part-2/`)
| Archivo | Qué es |
|---|---|
| `E2A-4-BASKETBALL-RULES-PART-2.mp4` | Máster, hook A (las 4 reglas en orden, título al final del hook). 1080×1920, 30 fps, H.264 + AAC, 44,09 s |
| `E2A-4-BASKETBALL-RULES-PART-2-HOOK-B.mp4` | Misma pieza con el hook B (goaltending congelado primero, título desde el primer fotograma) |
| `E2A-4-RULES-P2-HOOK-A.mp4` / `-HOOK-B.mp4` | Solo los 5 s de cada hook, para comparar |
| `E2A-4-BASKETBALL-RULES-PART-2-TRIAL.mp4` | Variante para reel de prueba (norma del propietario): zoom 3 %, color y nitidez, EQ suave de voz. SSIM 0,70. Misma toma de voz |
| `E2A-4-RULES-P2-CONTACT-SHEET.jpg` | Hoja de contactos del máster exportado |
| `deuce-take-raw.mp3` | Toma original de Deuce (eleven_v3, 793 cr). No regenerar: reutilizar |
| `GUION-FINAL.md`, `REGLAS-Y-ESCENAS.md`, `PARTE1-VS-PARTE2.md`, este archivo | Guion con dirección de voz, reglas por escena, comparación y QA |

## QA
- **Reglas** (`scripts/qc-rules4p2.mts`, sobre los cuerpos 3D renderizados): 22/22 PASS. Detalle en `REGLAS-Y-ESCENAS.md`.
- **Técnico y audio** (`qc-video.py`): PASS. −14,4 LUFS, pico real −1,5 dBTP. Trial: −14,9 LUFS, −1,3 dBTP.
- **Estabilidad de gráficos** (`qc-floor-flicker.py`): 0 fotogramas negros o en mosaico. **0 parpadeos y 0 caídas** en los 5 tramos congelados (hook, 8 s, campo atrás, 3 s, goaltending).
- **Motor** (`qc-tactical3d`): 40/41. El único fallo es la duración (44,09 s frente a 30–40 s del estándar diario). Se respeta lo que pide el brief (40–45 s).
- **Encuadre** (`frame-fit`): 0 jugadores fuera de cuadro en los planos generales. Los primeros planos (pies en 8 s, aro en goaltending) cortan cuerpos a propósito.
- **Revisión visual** de unos 40 fotogramas del MP4 exportado:
  - Sincronía: el 8 se pone en rojo al terminar «frontcourt…», el veredicto de los 3 s llega con «Violation.» y el congelado del goaltending cae en «touches».
  - Subtítulos: máximo 2 líneas, por encima de la interfaz. No tapan la línea central, los pies, el balón, el aro ni el contador.
- **Voz:** una sola toma de Deuce. Énfasis por palabra (EIGHT SECONDS, cross!, BACKCOURT, paint, Violation, GOALTENDING!, counts!) y curva de energía con `voice-dynamics --preserve`. Música original trap_b `--no-sfx`, sin botes.

## Defectos conocidos (no bloqueantes)
- La lista final «1 · 8 SECONDS … 4 · GOALTENDING» es pequeña y se parte en dos líneas.
- En el 8, el pie derecho está en fase de impulso: la puntera toca el suelo y el talón está levantado unos 7 cm. Reglamentariamente es correcto.
- El tiro del goaltending es algo tenso (vuelo de 0,85 s) para que un salto realista (0,78 m) llegue al balón por encima del aro. El test genérico pide 0,9–1,3 s.
- El PDF FIBA 2026 no se pudo abrir desde el contenedor; se usó el texto de 2024.

## Componentes reutilizables (repo e2a-tiktok-media, rama `claude/project-thread-qocfjn`)
- Jugadas: `template/tactical/specs/_gen-rules4p2.py` → `tactical/plays/rules4p2-*.json`.
- QC reglamentario: `template/scripts/qc-rules4p2.mts`.
- Edición: `template/tactical/episodes/_gen-rules4p2.py`. Opciones: `--hook A|B`, y `--placeholder` para montar con tiempos provisionales antes de tener la voz.
- Gráficos opt-in, en `src/t3d/rules3d.tsx`:
  - `paint`: zona restringida;
  - `centerLine`: línea central que se dibuja desde el centro;
  - `rimLine`: altura del aro.
- Rótulo opt-in `clock` (en `Tactical3D.tsx`): un contador con pasos y salto de tiempo.
- Opt-in `v33grab` con `target: 'ball'` (en `motion33.ts`): la mano toca el balón.
- Voz: `tactical/episodes/rules4p2/` (palabras, énfasis, curva); audio en `public/rules4p2/`.
