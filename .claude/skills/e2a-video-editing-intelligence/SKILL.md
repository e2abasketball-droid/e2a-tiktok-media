---
name: e2a-video-editing-intelligence
description: Analiza vídeos de referencia (cortes, cámara, transiciones, subtítulos, color, audio, sincronía, retención) con ffmpeg y numpy, guarda técnicas verificables en una biblioteca versionada y las aplica a episodios originales de E2A en Remotion Pro sin tocar el guion aprobado. Úsala para "analiza esta referencia", "qué técnicas de edición usa este vídeo", "aplica técnicas de la biblioteca a este episodio" o "planifica la edición de este guion".
---

# E2A Video Editing Intelligence (v1.0.0)

Módulo adicional del pipeline audiovisual de E2A. **No sustituye nada**: el guion, las categorías,
ElevenLabs, Remotion Pro (`template/`), `render-pro.sh`, la mezcla (`template/audio-mix.json`),
Metricool y las tareas programadas siguen igual. El productor lo invoca cuando quiere medir una
referencia o mejorar la edición de un episodio; nada se activa solo.

Todo corre en Claude Code en la nube con lo que ya trae el contenedor: `ffmpeg`, `ffprobe`,
Python 3 y `numpy` (y `node` para el validador de Remotion). Sin servicios de pago, sin
transcripción y sin créditos de ElevenLabs.

## Reglas que no se negocian

1. **El guion aprobado no se toca.** APPLY solo cambia campos de edición (transición, cámara,
   layout, backdrop, posición de subtítulos, tratamiento del fondo, efectos, tipo de gancho y anclas
   de la música). Compara la huella del guion antes y después y aborta si cambiara algo.
2. **No inventar.** Cada medida lleva su nivel: `observacion` (medido), `estimacion` (deducido con
   un método conocido) o `hipotesis` (hay que confirmarlo mirando los fotogramas). Lo que no se puede
   medir (tipografía exacta, qué cuenta el vídeo, máscaras complejas) se escribe como hipótesis o se
   deja para la revisión visual.
3. **Material de terceros fuera del repo** (el repo es público). Al repositorio solo van medidas
   (`analysis.json`), el informe y fichas escritas con nuestras palabras. Vídeos, fotogramas y audio
   se quedan en la carpeta temporal o en el Drive privado. Nunca copiar textos, gráficos ni música de
   una referencia.
4. **Sin efectos fuera de alcance:** no renderizar para publicar, no publicar, no generar voz, no
   modificar tareas programadas ni fusionar en `main` sin autorización del propietario.

## Archivos

| Ruta | Para qué |
|---|---|
| `scripts/analyze_video.py` | ANALYZE: mide un vídeo y escribe `analysis.json` + `report.md` + fotogramas |
| `scripts/extract_frames.py` | fotogramas a baja resolución para medir, fotogramas representativos y hoja de contactos |
| `scripts/analyze_audio.py` | sonoridad, silencios, golpes, tempo, voz/música/efectos, mezcla |
| `scripts/validate_analysis.py` | valida un `analysis.json` (estructura, tiempos, niveles, huella) |
| `scripts/report.py` | informe Markdown en 12 secciones |
| `scripts/library.py` | biblioteca: índice sin duplicados, fichas, validación, versiones |
| `scripts/remotion_options.py` | lee de `template/src/pro/types.ts` lo que Remotion Pro acepta |
| `scripts/apply_plan.py` | APPLY: selección de técnicas, plan con tiempos, episodio aplicado, QC |
| `references/analysis-method.md` | cómo se mide cada una de las 12 dimensiones y sus límites |
| `references/technique-schema.md` | formato de las fichas `tec-NNNN` y del `analysis.json` |
| `references/quality-standards.md` | estándares de calidad del plan (Q1–Q10) y del render (R1–R7) |
| `tests/test_skill.py` | 58 pruebas con vídeos generados en local |
| `examples/` | planes APPLY de ejemplo y QC de un render de prueba |
| `../../../editing-library/` | biblioteca persistente y versionada (raíz del repo) |

## Modo ANALYZE (vídeo de referencia)

```bash
S=.claude/skills/e2a-video-editing-intelligence/scripts
ID=$(python3 -I $S/library.py next-id)                       # R-NNNN
python3 -I $S/library.py seen "<id de Drive o URL>"          # exit 10 = ya analizada, no repetir
python3 -I $S/analyze_video.py <video.mp4> /tmp/refs/$ID --ref-id $ID \
        --title "<título>" --source-key "<id de Drive o URL>" --rights tercero   # o propio
python3 -I $S/validate_analysis.py /tmp/refs/$ID/analysis.json
```

1. Lee `report.md` y **mira `frames/sheet.jpg`** (Read de la imagen). Completa la revisión visual:
   qué cuenta, tipografía, gráficos. Lo que veas es `hipotesis` salvo que una medida lo respalde.
2. `python3 -I $S/library.py add /tmp/refs/$ID` guarda `analysis.json` y `report.md` en
   `editing-library/analyses/$ID/` (nunca los fotogramas). Exit 10 = el mismo vídeo ya está con otro id.
3. `python3 -I $S/library.py propose editing-library/analyses/$ID/analysis.json` da borradores de
   fichas a partir de las medidas. Quédate solo con lo reutilizable y coherente con E2A (premium, azul
   marino #0B1C3D / dorado #C9A24D, la voz primero), reescribe la descripción con tus palabras,
   añade la evidencia visual como `hipotesis` y guarda con `propose --write` o a mano
   (`library.py next-tec`). Luego `library.py validate` y `library.py bump "<cambio>"`.
4. Si el archivo está dañado, es demasiado grande o es un enlace no descargable:
   `library.py fail <R-id> <clave> "<motivo>"` (el análisis falla con exit 2 y un motivo, nunca rompe).

Un segundo análisis del mismo archivo devuelve el resultado guardado (`cached: true`); `--force`
recalcula y da las mismas medidas.

## Modo APPLY (episodio original de E2A)

El storyboard es el episodio JSON del pipeline (`template/episodes/<id>.json`: narración con tiempos
por palabra + escenas ancladas a frases).

```bash
python3 -I $S/apply_plan.py plan template/episodes/<id>.json --out /tmp/plan-<id>
```

Qué hace: carga las fichas válidas, descarta las que no encajan (tipo de historia, escena que no
existe, final distinto al del guion, reglas que el guion no permite cumplir), puntúa el resto
(encaje con el tipo de historia, estado, evidencia, reglas medibles, rotación por `usage.json`),
elige como mucho 4 (una por categoría), las aplica una a una pasando cada vez el validador de
Remotion Pro (`template/scripts/validate-episode.mjs`; rechaza la técnica si añade errores o avisos)
y escribe:

- `plan.md` / `plan.json`: técnicas con el porqué, escena y tiempos, cambios antes → después, reglas
  de comprobación, técnicas descartadas con su motivo, plan por escena con la frase de la voz,
  instrucciones para Remotion, mezcla de audio (de `audio-mix.json`) y QC del plan (Q1–Q10).
- `<id>.applied.json`: el episodio con las técnicas aplicadas y la lista `techniques`. El original
  no se modifica; el productor decide si lo usa.

Después, **solo con autorización**, se renderiza con el pipeline de siempre
(`cd template && bash scripts/render-pro.sh <applied.json> out/<id>.mp4`) y se comprueba:

```bash
python3 -I $S/apply_plan.py qc out/<id>.mp4 --plan /tmp/plan-<id>/plan.json   # exit 1 si algo falla
```

`qc` analiza el render con ANALYZE, evalúa las reglas de cada técnica y los estándares R1–R7
(1080×1920, 30/60 fps, −14 ± 1 LUFS, pico ≤ −1 dBTP, primer cambio ≤ 2.5 s, ningún tramo > 4 s sin
cambio visual, duración igual al plan). Con `--record` en `plan` la selección queda en
`editing-library/usage.json` para rotar técnicas en los siguientes vídeos.

Una técnica que necesite una opción nueva de Remotion se marca `"requiere_codigo": true` y se queda
en `propuesta`: implementarla es trabajo de código aparte (usa la skill `remotion:remotion-best-practices`)
y necesita el visto bueno del propietario.

## Estados de una ficha

`propuesta` (nace de una referencia; modo sombra) → `probada` (aplicada y su QC cumplido en un render)
→ `activa` (aprobada por el propietario para producción) · `descartada`. Cambiar estado:
`library.py status <tec-id> <estado> "<motivo>"` (sube la versión de la ficha y deja historial).

## Pruebas

```bash
python3 -I .claude/skills/e2a-video-editing-intelligence/tests/test_skill.py            # ~30 s
python3 -I .claude/skills/e2a-video-editing-intelligence/tests/test_skill.py --remotion # + still de Remotion
```
