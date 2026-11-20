# Ficha PCD — Slip vs Hard Hedge (2026-11-20)

**Episodio:** `slip-vs-hedge`. **Ficha táctica:** `produccion/tactical/pcd/fichas/slip-vs-hedge.FICHA-TACTICA.md`. **Jugadas:** `template/tactical/plays/slip-a-dive.json`, `template/tactical/plays/slip-b-pullup.json`.
**Generada:** `python3 tools/pcd.py new --cid slip-vs-hedge --out produccion/tactical/pcd/slip-vs-hedge.md --ficha produccion/tactical/pcd/fichas/slip-vs-hedge.FICHA-TACTICA.md` (plantilla `produccion/tactical/pcd/PLANTILLA-PCD.md`). Rellénala antes del storyboard; `python3 tools/pcd.py check` la valida.

**Estado:** muestra del método (ficha de nivel guion, 2026-11-20). Sin render: la puerta editorial se marca cuando haya previsualizaciones. El episodio sigue aparcado hasta que el dueño lo active.

## Ficha (11 campos; «TODO» o «BORRADOR» cuentan como vacío)
- **Público y momento:** jugador o entrenador que defiende pick and roll con *hard hedge*. En el fotograma 0 se ven X5 por encima de la línea del bloqueo, O5 llegando a poner la pantalla y la pintura vacía detrás.
- **Promesa (qué aprende, ve o gana dentro del vídeo):** saber cuándo el bloqueador debe irse antes del contacto (*slip*) y cuándo usar el bloqueo de verdad, mirando un solo pie: el primer paso de X5.
- **Curiosidad (qué sabe al principio y qué pregunta concreta le queda):** ve a X5 salir antes de que llegue el bloqueo y un hueco detrás. La pregunta es quién aprovecha ese hueco y qué pasa si X5 espera.
- **Disruptividad (palanca: ángulo | idea | formato):** ángulo e idea. Se mira al defensor del bloqueador, no al manejador. La ventaja aparece antes de que se mueva el balón: el bloqueo NO se pone.
- **Comienzo visible (fotograma 0 y qué cambia en el primer segundo, sin audio):** S000 = mismo arranque A/B (escena hasta 0,60 s). X5 da su primer paso por encima de la línea en el primer segundo, con una marca pequeña en el pie. O5 todavía se acerca. Se oculta el pase.
- **Primera evidencia (cuándo ve algo que cumple parte de la promesa):** O5 planta, abre cadera y sale hacia el aro mientras X5 sigue arriba (lectura A, primer tercio del vídeo).
- **Primer desenlace (qué sucede, escena y corte donde se confirma):** A (`slip-a-dive.json`): pase por encima a O5 en carrera, recepción de frente, dos apoyos y bandeja con despegue y aterrizaje en un plano lateral.
- **Reenganche (pregunta nueva que nace de lo aprendido):** «Same start. Now he waits.» Vuelta al fotograma de decisión de X5 (0,60 s) con la misma cámara del gancho.
- **Segundo desenlace (dónde se responde y dónde se verifica):** B (`slip-b-pullup.json`): X5 espera en *drop*, el bloqueo es legal y estático, y O1 frena a dos pies y tira en suspensión delante de él. Se ve el resultado del tiro.
- **Variante de guion (qué cambia en A/B; una sola variable):** H-A frente a H-B: cambian solo la voz y las cartelas del gancho. La imagen, la duración, la música y el cuerpo son los mismos.
- **Pregunta final (qué intervención le corresponde al usuario):** «You're guarding the screener: show early or wait?», sobre el fotograma de decisión de X5.

## Aperturas candidatas (al menos 2; etiquetas de prueba)
- H-A: «He left before the screen. Who's open?» | «HE LEFT EARLY» → «WHO'S OPEN?» | plano 3/4 bajo sobre X5 y la pintura vacía
- H-B: «Don't set the screen. Watch his feet.» | «DON'T SET IT» → «WATCH HIS FEET» | el mismo plano
- Elegida: H-A para el render, porque la pregunta tiene respuesta filmable en el pase al hueco. H-B queda como variante A/B de una sola variable si se pide.

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
