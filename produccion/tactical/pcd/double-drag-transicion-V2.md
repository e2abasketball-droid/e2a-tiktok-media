# Ficha PCD — Double Drag en transición V2 (ejemplo completo)

**Episodio:** `ddtr2-main-a` / `ddtr2-main-b` (variantes `V2-Hook-A` / `V2-Hook-B`). **Ficha táctica:** `tactical-studio/double-drag-transicion/ficha/FICHA-TACTICA.md`. **Jugadas:** `template/tactical/plays/ddtr-a-roll.json` (rama `stay_home`) y `template/tactical/plays/ddtr-b-skip.json` (rama `tag_roll`). **Generador:** `template/tactical/episodes/_gen-ddtr2.py`.
**Fuente del método:** el brief del dueño `E2A-prompt-Claude-Double-Drag-V2-y-metodo-PCD.md`, sec. 3 y 6. El vídeo de referencia de WhatsApp NO estaba adjunto en esta sesión: el método se aplica a partir del resumen escrito en el brief.

## Ficha (11 campos)
- **Público y momento:** jugador o entrenador que reconoce una ayuda desde la esquina. En el fotograma 0 ya están X3 (defensor de la esquina), O3 (su tirador, abajo) y la dirección de la pintura (O5 rodando, O1 con balón, arriba a la derecha).
- **Promesa (qué aprende, ve o gana dentro del vídeo):** reconocer qué tiro concede el primer paso de X3 en un Double Drag: bandeja (si se queda) o triple de esquina (si ayuda).
- **Curiosidad (qué sabe al principio y qué pregunta concreta le queda):** ve a X3 entre dos responsabilidades y el pie que empieza a cargar. La pregunta es cuál de las dos va a quitar y qué deja libre: «Layup or three?».
- **Disruptividad (palanca: ángulo):** se mira al defensor sin balón, no al manejador. La cámara 3/4 a media altura desde el lado débil centra su pie. El cambio de patrón ocurre dentro de la jugada: el mismo fotograma lleva a dos desenlaces.
- **Comienzo visible (fotograma 0 y qué cambia en el primer segundo, sin audio):** X3 parado justo antes de su primer apoyo (escena S063). El pie carga y arranca hacia dentro a los ≈ 0,2 s, con una marca roja pequeña bajo él. O3 sigue en la esquina. El pase y su resultado no se ven.
- **Primera evidencia (cuándo ve algo que cumple parte de la promesa):** E 3,3–5,0 s, las dos pantallas sobre X1 (O5 primero en S032, O4 después en S053). E 5,0–8,2 s, la separación ROLL/POP.
- **Primer desenlace (qué sucede, escena y corte donde se confirma):** `stay_home`. Pase S084, recepción por delante S098, dos apoyos, suelta S116, canasta S131 y caída, en un solo plano (E ≈ 10,2–14,0 s).
- **Reenganche (pregunta nueva que nace de lo aprendido):** «Same play. Now watch him step in.» Vuelta atrás al mismo fotograma de decisión (S058–S068) y con la misma cámara que el gancho. Ahora X3 sí entra.
- **Segundo desenlace (dónde se responde y dónde se verifica):** `tag_roll`. El hueco que deja X3 (fantasma en su sitio de S066) y el skip S086. Después, la recepción de frente (S114), la carga, la suelta S133 y el balón que atraviesa el aro (S163–S166), con red y caída a 1×, hasta S193 (E ≈ 19,3–22,9 s).
- **Variante de guion (qué cambia en A/B; una sola variable):** solo la voz y las dos cartelas de la apertura. A: «Layup or three? Watch this foot.» / «LAYUP OR THREE?» → «WATCH THIS FOOT». B: «Take away the layup. What opens up?» / «TAKE AWAY THE LAYUP» → «WHAT OPENS UP?». Se mantienen iguales la imagen, el plano, el remapeo, la duración, la música y el cuerpo, que es idéntico muestra a muestra desde E 3,168 s.
- **Pregunta final (qué intervención le corresponde al usuario):** «You're guarding the corner. Help or stay home?». Va sobre el mismo fotograma de decisión, con X3 identificado, y el plano termina en el gesto del inicio (bucle).

## Aperturas candidatas (al menos 2; etiquetas de prueba)
- H-A: «Layup or three? Watch this foot.» | «LAYUP OR THREE?» → «WATCH THIS FOOT» | plano HOOK (3/4 lado débil, S063→S082)
- H-B: «Take away the layup. What opens up?» | «TAKE AWAY THE LAYUP» → «WHAT OPENS UP?» | el mismo plano
- H-V1 (referencia, no se renderiza): «One step changes the shot.» Es la apertura declarativa de la V1 y queda como comparativa.
- Elegida: se entregan H-A y H-B como variante A/B de una sola variable (lo pide el brief). Si hay que publicar solo una, H-A, porque nombra los dos desenlaces y el objeto que hay que mirar.

## Puerta editorial (antes del render final; `pcd.py check --stage render`)
- [x] 1. Ficha completa y dos aperturas. Se entregan las dos como variante A/B.
- [x] 2. Primeros 1–2 s a 360 px y sin audio: `tactical-studio/double-drag-transicion/v2/previsualizaciones/`, con la apertura V1 al lado. Sujeto: X3 y su pie. Lo que va a pasar: entra hacia la pintura y deja a O3. Por qué seguir: las cartelas preguntan cuál de los dos tiros sale.
- [x] 3. Hasta la primera evidencia no hay cartela de tema. Pausas: la cámara lenta del gancho (≈ 0,2×) existe solo para el apoyo de X3. La del bloque tag_roll (≈ 0,2×) acompaña la entrada de X3 y el giro de O1.
- [x] 4. Promesa cumplida. A: canasta S131, E ≈ 13,2 s. B: balón bajo el aro S166, E ≈ 21,8 s. El plano sigue al menos 11 cuadros más.
- [x] 5. El final cierra la pregunta: «Help or stay home?» sobre el fotograma de decisión. A y B difieren en una sola variable (la voz y la cartela de la apertura).
- [ ] 6. Datos tras publicar: sin dato (este encargo no publica).

## Registro de resultados (tras publicar)
| Variante | Plataforma | Ventana | Vistas | Retención / visionado medio | Interacción | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| H-A | — | — | sin dato | sin dato | sin dato | no publicado (revisión) |
| H-B | — | — | sin dato | sin dato | sin dato | no publicado (revisión) |
