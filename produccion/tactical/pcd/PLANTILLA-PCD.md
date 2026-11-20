# Plantilla — Ficha PCD de la apertura (E2A)

Método de ganchos **PCD: Promesa, Curiosidad, Disruptividad** (encargo del dueño «Double Drag V2 y método PCD», 2026-11-20). Es obligatoria en todo vídeo E2A nuevo y se rellena **antes del storyboard**. Punto de entrada: `produccion/tactical/FORMATO-CHICAGO.md` → «Ficha PCD».

- **Crear:** `python3 tools/pcd.py new --cid <id> --out produccion/tactical/pcd/<id>.md --ficha <FICHA-TACTICA.md>`. Si existe ficha táctica, la ficha PCD hereda de ella el título, las jugadas y las dos lecturas (como BORRADOR).
- **Validar:** `python3 tools/pcd.py check produccion/tactical/pcd/<id>.md` (antes del guion) y `--stage render` (antes del render final).
- **Gate:** la primera línea del guion es `PCD: produccion/tactical/pcd/<id>.md`. `T script` rechaza el guion si la ficha está incompleta.
- **Ejemplos completos:** `produccion/tactical/pcd/double-drag-transicion-V2.md` (reel Double Drag V2, ganchos A/B; palanca: ángulo) y `produccion/tactical/pcd/pistol-fake-handoff.md` (reel Pistol Fake Handoff, ganchos A/B; palanca: idea comprobable en el balón).

**Principio.** Una persona sabe qué mirar al comienzo y prevé qué va a recibir si se queda. El plano, la frase y el primer movimiento cuentan el mismo problema. La brecha de curiosidad tiene una respuesta filmable. La disruptividad sale del ángulo de comunicación, de la idea o del formato: elige la palanca que de verdad aporta al tema. El sonido solo añade énfasis donde la imagen ya funciona.

**Por formato:**
- **Táctica 3D:** una pista que cambia la lectura antes de nombrar la jugada.
- **Técnica:** una corrección o comparación visible, con efectos medidos presentados como medidos.
- **Promo o trials:** dos o tres momentos concretos propios y un CTA fiel a la inscripción.
- **Vídeo largo:** PCD en el arranque; una pregunta por capítulo si aporta.
- **Otros deportes:** la habilidad o decisión que exista en el material.

<!-- FICHA -->
## Ficha (11 campos; «TODO» o «BORRADOR» cuentan como vacío)
- **Público y momento:** TODO
- **Promesa (qué aprende, ve o gana dentro del vídeo):** TODO
- **Curiosidad (qué sabe al principio y qué pregunta concreta le queda):** TODO
- **Disruptividad (palanca: ángulo | idea | formato):** TODO
- **Comienzo visible (fotograma 0 y qué cambia en el primer segundo, sin audio):** TODO
- **Primera evidencia (cuándo ve algo que cumple parte de la promesa):** TODO
- **Primer desenlace (qué sucede, escena y corte donde se confirma):** TODO
- **Reenganche (pregunta nueva que nace de lo aprendido):** TODO
- **Segundo desenlace (dónde se responde y dónde se verifica):** TODO
- **Variante de guion (qué cambia en A/B; una sola variable):** TODO
- **Pregunta final (qué intervención le corresponde al usuario):** TODO

## Aperturas candidatas (al menos 2; etiquetas de prueba)
- H-A: TODO (voz | texto en pantalla | primer plano)
- H-B: TODO
- Elegida: TODO (motivo: claridad, encaje con el material, capacidad de responder a la pregunta)

## Puerta editorial (antes del render final; `pcd.py check --stage render`)
- [ ] 1. Ficha completa y al menos dos aperturas. Se elige una o se entregan dos como variante A/B.
- [ ] 2. Primeros 1–2 s a 360 px de ancho y SIN audio. Responde: cuál es el sujeto, qué está a punto de pasar y por qué seguir mirando. Si se ve el círculo pero no qué mira, arregla el plano. Si se entiende cómo acaba pero no por qué importa, rehace la pregunta. Si solo se entiende con la voz, acorta el texto o deja que el plano presente el gesto.
- [ ] 3. Tramo hasta la primera evidencia: sin cartelas que repitan el gancho. Cada pausa anota qué información aporta, su tamaño y su duración.
- [ ] 4. Fotograma donde se cumple la promesa (tiempo E + evento S). En táctica, el resultado de cada tiro se ve.
- [ ] 5. El final cierra la pregunta. La llamada dice por qué se pregunta. Las aperturas A/B difieren en una sola variable.
- [ ] 6. Datos observables guardados tras publicar (ventanas equivalentes, plataforma, denominadores). «Sin dato» si la plataforma no lo da. Se tratan como hipótesis: una sola pareja de publicaciones no prueba el PCD.

## Registro de resultados (tras publicar)
| Variante | Plataforma | Ventana | Vistas | Retención / visionado medio | Interacción | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| H-A | | | sin dato | sin dato | sin dato | |
| H-B | | | sin dato | sin dato | sin dato | |
