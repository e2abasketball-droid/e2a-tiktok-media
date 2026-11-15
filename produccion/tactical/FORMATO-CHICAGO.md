# Formato estándar de vídeo táctico E2A ("formato Chicago")

Decisión del dueño, 2026-11-14 20:11 UTC: "a partir de ahora todos los vídeos sean parecidos a este (con el mismo formato)". Referencia: el piloto Chicago action (`tactical-studio/chicago-action-pilot/`, página privada https://claude.ai/artifact/McGgqVpAm14BxkCpTrxwaF).

Este documento describe el formato. **No autoriza por sí solo publicar ni cambiar tareas programadas.**

## Ficha técnica
- Vertical 1080×1920, 30 fps, H.264/AAC 48 kHz, **32–36 s**, inglés.
- Voz E2A en inglés (Deuce, eleven_v4 con etiquetas de tono). Gancho firme con el verbo clave acentuado; la frase de lectura más lenta; la orden clave seca.
- Mezcla a −14 LUFS ±1, pico ≤ −1 dBTP, ganancia fija al final (sin loudnorm sobre la mezcla). Música propia discreta; solo SFX de contacto.
- Subtítulos con tiempos reales de palabra, palabras clave en dorado.

## Estructura (8 planos, una jugada con dos lecturas A/B)
1. **Gancho (0–4,5 s):** plano medio alto en movimiento sobre el error del defensor; título de 2 líneas con el resultado ("HE JUMPED THE HANDOFF"); corta antes de la canasta.
2. **Cenital (≈4,5–10 s):** cámara casi vertical (pitch 0–8°), canasta arriba; título con el nombre de la acción + subtítulo; ruta del jugador clave dibujada mientras se mueve; defensor marcado primero.
3. **Caso A, oblicua de tres cuartos** desde el mismo lado del eje, cruzando la línea pasador-receptor (que nada tape el contacto): contacto, primer paso, espacio.
4. **Caso B, la MISMA cenital y el mismo arranque:** paso del defensor ralentizado, congelado con etiqueta corta en la lectura.
5. **Corte a lateral** cuando empieza la acción final; seguir el balón hasta la recepción; marcar la ayuda tarde.
6–7. **Repetición rápida de A y B** en la misma orientación.
8. **CTA:** pregunta de 3 opciones sobre la jugada en movimiento ("CHASE / JUMP / SWITCH?"), logo corto.

## Gráficos
Una indicación por lectura; defensor marcado antes que el atacante; gráficos anclados a jugadores o a la pista; zonas seguras respetadas; ninguna etiqueta encima de un título o de los subtítulos.

## Control de calidad obligatorio
- Táctica validada antes de generar la voz (test-play, test-ball con un solo dueño del balón, test-motion).
- 3 fragmentos de revisión antes del render final (primeros 3 s, la acción de A, el paso + corte de B).
- QC del motor 12/12, qc-video PASS, revisión del vídeo completo a tamaño de móvil.
- Si un render se interrumpe, se conserva el último archivo reproducible.

## Coste orientativo por vídeo
Voz ≈ 1.100 créditos (2 tomas); render ≈ 25 min; más la revisión de fragmentos.

## Cómo aplicarlo en la tarea diaria (desde el 15 nov 2026, decisión del dueño 20:12 UTC del 14 nov)
- **Plantilla:** copia y adapta `template/tactical/episodes/_gen-chicago-action-shots.py` (planos, cámaras `TOP`/`TOP_IN`/`HOOK`/`OBL`/`SIDE`, superposiciones) y `_gen-chicago-action.py` (huecos de voz). Las jugadas, con dos lecturas A/B del mismo arranque, siguen `template/tactical/specs/_gen-chicago.py`. Para entregas mano a mano usa `style: 'handoff'`.
- **Guion:** las fases `HOOK/SETUP/CASE A/CASE B/TAKEAWAY/CTA` del procedimiento se mapean a los 8 planos de arriba (TAKEAWAY = repetición rápida A/B). Hook de 2 frases (resultado + consecuencia), CTA con pregunta de 3 opciones.
- **Voz:** UNA sola toma por vídeo (`generations_count` 1), para que dos vídeos quepan en `budget_per_day` (1.200 créditos, 2 tomas). Etiquetas de tono como en `ENTREGA` del piloto.
- **Fragmentos antes del render final:** renderiza con `--frames` los primeros 3 s, la acción del caso A y el paso + corte del caso B; mira los fotogramas y corrige (oclusiones, etiquetas sobre títulos o subtítulos, encuadre) antes del render completo.
- **Cámara:** oblicua cruzando la línea pasador-receptor (nunca por la espalda del pasador); cenital de A y B con el MISMO encuadre; QC del motor 12/12 obligatorio.
- **`qc-bounds` ANTES del render final** (lección del 15 nov: los dos vídeos del 16 nov se perdieron por un título 15 px dentro de la franja superior): `node --experimental-strip-types scripts/qc-bounds.mts <props.json> <informe.json>` sobre las props definitivas (modo sonda, sin render 3D, unos minutos). Solo con 0 violaciones se lanza el render final. Títulos: `y` ≥ 250 con `size` 104 (la plantilla ya usa 252).
- **Tamaño y encuadre:** en las cenitales, el grupo de jugadores implicados debe ocupar al menos la mitad del ancho (usa `TOP_IN` o acerca `dist`); en el CTA, los 10 jugadores visibles o, si no caben, un encuadre que no corte a ninguno por el borde.
- **Revisión final a tamaño de móvil** (fotogramas a 360 px de ancho) del vídeo completo antes de `package`.
- Todo lo demás (puertas, QC, licencias, publicación, delegación) sigue `PROCEDIMIENTO.md` sin cambios.

## Portada (desde el 15 nov 2026, decisión del dueño)
- **Herramienta:** `tools/make_cover.py`. Usa un fotograma del propio vídeo (nunca imágenes externas ni generadas), 1080×1920, fondo navy #0B1C3D, título blanco/dorado #C9A24D en Anton y el logo blanco pequeño.
- **Fotograma:** del gancho (0,5–3 s), cuando se ven a la vez el atacante que decide y su defensor en la franja central. El vídeo lleva títulos y subtítulos grabados: la herramienta usa solo la franja de acción (por defecto y 480–1180, zoom 1,2; ajusta `--band`/`--focus-x` si la acción queda fuera).
- **Título:** la pregunta del CTA en 2–5 palabras en inglés (p. ej. «Catch or Backdoor?», «Curl or Fade?»).
- **Recorte de perfil:** la herramienta falla si el título sale del recorte 1:1 o 3:4, o el logo del 3:4. Revisa además `profile-grid-mock.png` a tamaño de móvil.
- **Publicación:** `cover.jpg` en el mismo commit de `tactical-media` que el MP4; `package --cover-url --cover-report`. Si falla, se programa sin portada y se anota en el informe.
- Primera prueba: Iverson «Catch or Backdoor?», borrador de Metricool 429067806 (miniatura guardada idéntica byte a byte).

