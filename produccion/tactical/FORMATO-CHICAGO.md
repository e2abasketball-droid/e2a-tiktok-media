# Formato estándar de vídeo táctico E2A ("formato Chicago")

Decisión del dueño, 2026-11-14 20:11 UTC: "a partir de ahora todos los vídeos sean parecidos a este (con el mismo formato)". Referencia: el piloto Chicago action (`tactical-studio/chicago-action-pilot/`, página privada https://claude.ai/artifact/McGgqVpAm14BxkCpTrxwaF).

Este documento describe el formato. **No autoriza por sí solo publicar ni cambiar tareas programadas.**

## Ficha PCD de la apertura (obligatoria desde 2026-11-20, antes del storyboard)
Todo vídeo E2A nuevo empieza por su **ficha PCD (Promesa, Curiosidad, Disruptividad)**. Va antes que el guion y el storyboard. Origen: encargo del dueño «Double Drag V2 y método PCD».
1. **Crear:** `python3 tools/pcd.py new --cid <id> --out produccion/tactical/pcd/<id>.md --ficha <FICHA-TACTICA.md>`.
   - Con ficha táctica, la ficha PCD hereda el título, las jugadas y las dos lecturas como BORRADOR.
   - Los 11 campos son: público, promesa, curiosidad, disruptividad, comienzo visible, primera evidencia, primer desenlace, reenganche, segundo desenlace, variante A/B y pregunta final.
   - Se añaden 2 aperturas candidatas como mínimo y la elegida.
2. **Guion:** la primera línea de `guion.txt` es `PCD: produccion/tactical/pcd/<id>.md`.
   - El gate `T script` (`tools/tactical_studio.py script_check`) rechaza el guion si la ficha no pasa `python3 tools/pcd.py check <ficha>`.
   - Sin esa línea el guion se acepta con `pcd.status = absent`. Pasa a ser obligatoria si el dueño pone `"pcd": {"required": true}` en la configuración, tras la fusión.
3. **Gancho en imagen:** el plano, la frase y el primer movimiento cuentan el mismo problema.
   - El sujeto es legible a 360 px de ancho.
   - Hay una primera pista de movimiento en 0–0,4 s.
   - Hay una sola señal visual por vez.
   - El resultado queda oculto hasta el desenlace.
4. **Puerta editorial antes del render final:** `python3 tools/pcd.py check <ficha> --stage render`. Comprueba:
   - los primeros 1–2 s, a tamaño de móvil y sin audio;
   - el tramo hasta la primera evidencia;
   - el fotograma donde se cumple la promesa (el resultado de cada tiro se ve);
   - que el final cierre la pregunta;
   - que la variante A/B cambie una sola variable.
5. **Tras publicar:** se registran los datos observables o «sin dato». Son hipótesis: una sola pareja de publicaciones no prueba el PCD.

**Referencias:**
- Plantilla: `produccion/tactical/pcd/PLANTILLA-PCD.md`. Las versiones anteriores del estándar se recuperan con `git log -- produccion/tactical/pcd/` y `git show <sha>:<ruta>`.
- Ejemplo completo (renderizado, ganchos A/B): `produccion/tactical/pcd/double-drag-transicion-V2.md`, generador `template/tactical/episodes/_gen-ddtr2.py`.
- Muestra nueva hecha con la plantilla: `produccion/tactical/pcd/slip-vs-hedge.md` + `slip-vs-hedge.guion.txt` (pasa el gate `script`).

## Ficha técnica
- Vertical 1080×1920, 30 fps, H.264/AAC 48 kHz, **32–36 s**, inglés. (Double Drag V2, 2026-11-20: ≈ 30 s cuando la apertura PCD y los desenlaces completos lo piden. Se protege el resultado de cada tiro y se recorta la explicación repetida.)
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

## Jugadores 3D y acabado por defecto (desde 2026-11-19, paquete `e2a-player-v1`)
Rige en cuanto el propietario fusione la rama `claude/lab-mpfb-default-player`; antes de eso la tarea diaria (fijada a su commit) no lo ve.
- **No hay que pedirlo ni activarlo.** Todo episodio Tactical3DV2 nuevo dibuja a los jugadores con el personaje deformable de E2A: ataque = azul marino `#0E2147` con dorado, defensa = blanco `#F3F1EC` con granate, complexión distinta; tono de piel y dorsal por jugador; escala por la longitud de pierna del motor (los pies plantados no deslizan).
- **Animación por acción (automática):** si un jugador hace un patrón con clip validado (hoy `screen` + `roll` → clip de 5452 en espejo o sin espejo, elegido por el lado del giro) y la geometría de la jugada encaja (giro añadido ≤ 35°), se usa el clip; si no, la animación compatible del motor (rig procedural o coreografía `choreo`) aplicada a la malla. El motivo de cada elección sale en el registro del render (`[E2A players3d] …`) y en `qc-tactical3d` (sección `players3d`).
- **Cómo comprobarlo antes de gastar render:** `node --experimental-strip-types scripts/players3d-plan.mts tactical/episodes/<ep>.json` y `qc-tactical3d` (incluye pies, manos sobre el balón, cabeza y determinismo de la malla).
- **Excepciones por datos, nunca por recordatorio en el chat:** `"players3d": "A"` en el episodio (o en un plano) vuelve al atleta cápsula anterior; los episodios con `faces` (caras expresivas) siguen con cápsula porque la malla tiene cara neutra. Si un `.glb` no carga, el render sigue con cápsulas y lo registra como `FALLBACK`.
- **Recursos:** `template/public/players3d/e2a_player_{off,def}.glb` (+ `.provenance.json`), `template/src/t3d/players/*.rig.json`, clips en `template/src/t3d/clips/`. Regeneración: `tools/blender/build_player.py` (informe `template/tactical/reports/3d-animation-mpfb-2026-11-19/INFORME.md`).
- **Sonido:** cero sonido de bote por defecto (`autoSfx` ya no pone botes, recepciones ni caídas con la muestra de bote salvo que el episodio lo pida con un volumen explícito).
- **Edición:** el clip validado está en el bloqueo y continuación: muestra al bloqueador y al defensor que lo sufre en el mismo encuadre cuando ocurre el apoyo (oblicua de tres cuartos), y la salida en la cenital.

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

## Regla editorial permanente: tipo de contenido → framework (decisión del dueño, 2026-11-19, encargo Spain PnR 2.0)
Antes de escribir guion o planos de CUALQUIER vídeo E2A, identifica primero el tipo de contenido y elige su framework.
No uses siempre el mismo hook ni la misma estructura.

| Tipo | Framework |
|---|---|
| TACTICAL EXPLAINER (jugada con lecturas) | HOOK → MECHANISM → DECISION → PAYOFF → REHOOK (solo si hay segunda lectura; preferiblemente visual: freeze + rewind + «SAME ACTION. DIFFERENT READ.») → SECOND PAYOFF → TAKEAWAY → CTA |
| TECHNIQUE / MISTAKE-FIX / DRILL | PROBLEM / MISTAKE → WHY → CORRECT MOVEMENT → PROOF → TAKEAWAY → CTA |
| STORY | TENSION → PROGRESSION → TURN → PAYOFF → CTA |
| PLAYER BREAKDOWN / CONCEPT / COMPARISON | el más cercano de los anteriores, justificado en una línea en la entrega |

**Regla superior: CLARITY > FRAMEWORK.** Nunca fuerces un framework si empeora la explicación.
Regla de lectura asociada: muchos efectos a lo largo del vídeo, **una sola idea visual principal en cada momento**
(máx. 1 título + subtítulos + 1 etiqueta táctica a la vez); cada gráfico tiene entrada, permanencia y salida.
Referencia aplicada: `template/tactical/episodes/_gen-spain-pnr-2-shots.py` (capa `src/t3d/telestration3d.tsx`).

## Añadidos 2026-11-20 (Double Drag en transición)
- **El gancho se lee en el fotograma 0:** el título y el anillo del gancho llevan `from` negativo (−0,6 / −0,8 s), así que ya están dentro en el primer fotograma (portada automática y primer frame del feed).
- **Zona segura:** los títulos van con `y` ≥ 252 y los subtítulos con `subtitleY` ≤ 1360, porque `qc-bounds` corta en y = 1500. Cuando el jugador clave queda abajo en el plano, los subtítulos suben con `subtitleYAt` (y ≈ 300).
- **Variante de gancho (B):** cambian solo la voz y el título de apertura. La voz B es la toma corta del gancho empalmada en el silencio de la toma A antes de «As…». El vídeo B se monta con los fotogramas 0–91 de B y el resto de A, sin renderizar el cuerpo dos veces.
- **Comparativa actual / nuevo:** la misma jugada, cámara y ventana con el perfil anterior y con el nuevo (`_gen-ddtr-lab.py`), en `comparativa/`.
