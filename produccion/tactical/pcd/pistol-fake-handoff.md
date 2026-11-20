# Ficha PCD: Pistol Fake Handoff en transición (ejemplo completo)

- **Episodio:** `pfh-main-a` / `pfh-main-b` (variantes `Hook-A` / `Hook-B`).
- **Jugadas:**
  - `template/tactical/plays/pfh-keep.json` (rama `keep`, el amago);
  - `template/tactical/plays/pfh-give.json` (rama `give`, la entrega real).
- **Generadores:**
  - jugadas: `template/tactical/specs/_gen-pfh.py`;
  - episodio: `template/tactical/episodes/_gen-pfh.py`.
- **Fuente del método:** el brief del dueño `E2A-Prompt-Claude-Pistol-Fake-Handoff-PCD.md`, sec. 2, 3 y 7.4.
  - El vídeo de referencia de WhatsApp no estaba adjunto. Se ha trabajado con la descripción escrita del brief.
- **Segundo ejemplo de la plantilla** (el primero es `double-drag-transicion-V2.md`).
  - Aquí la palanca es la **idea**: el engaño se puede comprobar en el balón.
  - En Double Drag la palanca era el **ángulo**: se mira al defensor sin balón.

## Ficha (11 campos)
- **Público y momento:** jugador o entrenador que conoce el mano a mano (handoff) en ataque temprano.
  - En el fotograma 0 se ven:
    - el balón delante de la cadera de O2 (azul, número 2);
    - las manos de O1 (azul, número 1) llegando por dentro;
    - X2 (blanco, número 2) entre O2 y la línea de fondo.
- **Promesa (qué aprende, ve o gana dentro del vídeo):** distinguir un mano a mano falso de uno real y saber qué abre cada uno.
  - El falso (`keep`) abre la línea de fondo.
  - El real (`give`) deja a O1 atacando por dentro.
- **Curiosidad (qué sabe al principio y qué pregunta concreta le queda):** ve una entrega a punto de ocurrir y un defensor que gira hacia ella. Le queda una pregunta: quién se queda el balón.
  - El gancho se corta en S052,5, antes de que O1 pase con las manos vacías (S053–S054).
- **Disruptividad (palanca: idea):** «This handoff is a lie.» El vídeo afirma que la entrega que se está viendo es mentira, y el espectador puede comprobarlo mirando el balón.
  - Se pide mirar primero las manos y después al defensor.
  - No hay efectos de sonido. El impacto inicial de la música se ha quitado (`--soft-edges`).
- **Comienzo visible (fotograma 0 y qué cambia en el primer segundo, sin audio):** plano 3/4 cerrado desde dentro y arriba, S041.
  - En el primer segundo (S041→S048):
    - O2 presenta el balón;
    - O1 acerca las manos;
    - X2 empieza a girar el pecho, con un foco rojo pequeño bajo él desde E 0,55 s.
  - El titular se lee desde el fotograma 0.
- **Primera evidencia (cuándo ve algo que cumple parte de la promesa):** E 9,15–11,5 s (S050→S060).
  - O1 pasa sin balón (O1 queda a 15 cm o más del balón; las manos no lo tocan).
  - O2 recoge el balón por delante del cuerpo.
  - Rótulo «STILL HIS BALL» entre «keeps» y «way.».
  - Primer bote hacia S059–S060, con «The wing keeps it».
- **Primer desenlace (qué sucede, escena y corte donde se confirma):** `keep`, plano bajo 3/4 desde el lado de fondo.
  - Una franja discreta marca el carril de fondo hasta «baseline.».
  - Penetración, recogida en S100, despegue y suelta.
  - Canasta en S124: el balón atraviesa el aro y se ve la caída (E ≈ 13,2–17,5 s).
  - Repetición elevada del amago (E 17,5–19,1 s):
    - ruta aparente discontinua (la devolución que no ocurre);
    - ruta real continua de O2 hacia el fondo.
- **Reenganche (pregunta nueva que nace de lo aprendido):** «Same setup. If that lane stays shut, look for the handoff back.»
  - Mismo encuadre que el plano del amago.
  - Ahora X2 guarda el fondo (foco rojo entre «If» y «shut,»).
- **Segundo desenlace (dónde se responde y dónde se verifica):** `give`, entrega real de O2 a O1 entre S047 y S055.
  - En t = 1,73 s (S052) las dos parejas de manos están a la vez sobre el balón, con los pechos a 0,85 m (`qc-handoff`).
  - O1 es dueño del balón en S055 y da el primer paso por dentro (E ≈ 19,1–23,1 s).
  - Después, KEEP y GIVE en planos consecutivos con el mismo encuadre y los mismos frames S046–S058 (E ≈ 23,1–24,85 s).
- **Variante de guion (qué cambia en A/B; una sola variable):** solo cambian la voz de apertura y su titular.
  - A: «This handoff is a lie.» / «THIS HANDOFF / IS A LIE.».
  - B: «He sold a handoff that never happened.» / «HE SOLD A HANDOFF / THAT NEVER HAPPENED».
  - Todo lo demás es igual en A y B:
    - plano, remapeo y ventana del gancho (2,80 s);
    - música y cuerpo del reel;
    - la voz es idéntica muestra a muestra desde E 2,78 s.
- **Pregunta final (qué intervención le corresponde al usuario):** «That's the Pistol fake handoff. Would you bite?».
  - Se vuelve al plano del gancho (S034→S041), que termina en la imagen inicial del reel (bucle).
  - La música termina sin golpe; acordes que se apagan en 2 s.

## Aperturas candidatas (al menos 2; etiquetas de prueba)
- H-A: voz «This handoff is a lie.», texto «THIS HANDOFF / IS A LIE.», plano HOOK (3/4 cerrado, keep S041→S052,5).
- H-B: voz «He sold a handoff that never happened.», texto «HE SOLD A HANDOFF / THAT NEVER HAPPENED», mismo plano.
- Elegida: se entregan las dos como variante A/B (decisión del brief).
  - La A es más corta; la voz hace una pausa breve («handoff... is a lie») para ocupar la misma ventana que la B.

## Puerta editorial (antes del render final; `pcd.py check --stage render`)
- [x] 1. La ficha está completa y hay dos aperturas, que se entregan como variante A/B.
- [x] 2. Primeros 1–2 s a 360 px de ancho y sin audio:
  - se ven el balón, las manos de O1 y el giro de X2 (`ensayo/gancho-A-*.jpg`, `ensayo/gancho-B-f000.jpg`);
  - el titular se lee en el fotograma 0.
- [x] 3. Hasta la primera evidencia no hay cartelas que repitan el gancho. No se usan pausas.
  - Gráficos hasta ese punto:
    - trayectoria real del pase adelantado (ballPath);
    - línea fina de la ruta de O1, que se apaga antes de los dedos;
    - foco en X2.
- [x] 4. La promesa se cumple en E ≈ 11,5 s (S060, primer bote de O2 con el balón): se confirma el amago.
  - La bandeja (make en S124) se ve en E ≈ 15,8 s, con el balón atravesando el aro.
- [x] 5. El final cierra la pregunta: «Would you bite?» sobre el fotograma del gancho.
  - Las aperturas A/B se diferencian en una sola variable (voz + titular).
- [ ] 6. Datos observables tras publicar (ventanas equivalentes, plataforma, denominadores). «Sin dato» si la plataforma no los da.

## Registro de resultados (tras publicar)
| Variante | Plataforma | Ventana | Vistas | Retención / visionado medio | Interacción | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| H-A | | | sin dato | sin dato | sin dato | |
| H-B | | | sin dato | sin dato | sin dato | |
