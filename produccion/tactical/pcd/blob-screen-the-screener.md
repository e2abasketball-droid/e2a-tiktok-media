# Ficha PCD: BLOB Box Screen-the-Screener (versión única, 40 s)

- **Episodio:** `blob-box-screen-the-screener-v1`, una única versión. No hay variante A/B ni gancho alternativo, por decisión del brief.
- **Jugadas:**
  - `template/tactical/plays/blob-a-rim.json`: lectura A, X4 se queda; O3→O5, bandeja.
  - `template/tactical/plays/blob-b-three.json`: lectura B, X4 ayuda; finta, O3→O2, triple.
- **Generadores:**
  - jugadas: `template/tactical/specs/_gen-blob.py`;
  - episodio: `template/tactical/episodes/_gen-blob.py`.
- **Fuente:** brief del dueño `E2A_CLAUDE_MASTER_BLOB_SCREEN_THE_SCREENER_40S.md`, sec. 02, 03, 07 y 15.
- **Palanca:** la **contradicción**. La defensa tapa el aro y, aun así, alguien queda libre. Además, ese jugador es el que acaba de bloquear.

## Ficha (11 campos)
- **Público y momento:** jugador o entrenador que ha visto saques de fondo (BLOB) en formación de caja.
  - En el fotograma 0 (rama B, S073) se ven:
    - O3 (azul, n.º 3) fuera de pista con el balón, arriba;
    - X4 (blanco, n.º 4) caído al aro;
    - O2 (azul, n.º 2) en el centro inferior, saliendo de su primer bloqueo hacia la cámara.
- **Promesa (qué aprende, ve o gana dentro del vídeo):** una lectura de saque de fondo con dos salidas según lo que haga X4.
  - Si X4 se queda, bandeja de O5.
  - Si X4 ayuda, «bloqueo al bloqueador» y triple de O2.
- **Curiosidad (qué sabe al principio y qué pregunta concreta le queda):** ve a la defensa cerrando el aro. Le queda una pregunta: «so how is HE open?».
  - Desde 0,7 s, «HE» es O2: anillo dorado con pulso y foco.
- **Disruptividad (palanca: contradicción):** se entra directamente en el instante contradictorio (X4 en el aro, O2 liberándose), antes de explicar la secuencia de bloqueos.
  - No hay logo inicial, efectos de sonido ni datos inventados.
- **Comienzo visible (fotograma 0 y qué cambia en el primer segundo, sin audio):** cámara elevada que sigue a O2, X4 y O3 (rama B, 2,45→2,95 s de juego).
  - X4 tiene un foco rojo desde 0,2 s.
  - O2 tiene anillo dorado y foco desde 0,7 s.
  - El subtítulo va arriba, sobre la grada, y no tapa a ningún jugador.
- **Primera evidencia (cuándo ve algo que cumple parte de la promesa):** E 7,3–11 s.
  - O2 planta el primer bloqueo con los dos pies (S043–S046) sobre X5.
  - O5 corta por debajo hacia el aro, con dorsal «2» fijado y ruta discontinua.
  - Locución: «But watch number TWO. He screens for FIVE.».
- **Primer desenlace (qué sucede, escena y corte donde se confirma):** lectura A, X4 se queda.
  - Pase O3→O5 (suelta a 2,27 s de saque; recepción en «home…»).
  - Bandeja con make en «easy layup.» (E ≈ 11–14,5 s).
  - Rótulo «READ 1: RIM».
- **Reenganche (pregunta nueva que nace de lo aprendido):** «But what if they protect the rim?» (E 14,6 s).
  - Rebobinado inequívoco a la misma situación.
  - X4 ayuda (foco y «HELP» en el suelo).
  - La línea de pase O3→O5 aparece en rojo con «NO PASS».
- **Segundo desenlace (dónde se responde y dónde se verifica):** lectura B.
  - O2 sigue: «The first screener isn't finished.».
  - O4 le hace bloqueo directo hacia abajo (down screen) sobre X2 (S086–S106).
  - O2 sale al ala y recibe en «Catch.» (suelta de O3 a 3,70 s, antes de 5 s).
  - Tira en «Three.»; el balón entra y se ve la red (E ≈ 24,2–28,4 s).
  - Rótulo «READ 2: THREE».
- **Variante de guion (qué cambia en A/B; una sola variable):** no aplica, porque se entrega una única versión (brief).
  - Las dos lecturas A/B son de la jugada, no del gancho. Comparten todo hasta la decisión de X4 (S050).
- **Pregunta final (qué intervención le corresponde al usuario):** «You're X4. Protect the rim, or switch onto TWO? Comment: RIM or SWITCH.».
  - Cierre sobre el fotograma congelado de la decisión, con la flecha RIM en rojo y la de SWITCH en dorado.
  - Logo desde «SWITCH».
  - La música termina sin golpe (`--soft-edges`).

## Aperturas candidatas (al menos 2; etiquetas de prueba)
- H-1: rama B a 2,45 s, cámara elevada que sigue a O2/X4/O3, anillo dorado en O2 desde 0,7 s.
- H-2: plano centrado en X4 y su anillo. Descartada en previs (`previs/hook-f0039.jpg`).
  - O3 quedaba pequeño y tapado por X3.
  - Dos jugadores azules quedaban cortados por los bordes.
  - El sujeto, O2, no se leía a tamaño de móvil (nota del coordinador).
- Elegida: H-1. El brief pide una sola versión, así que no se entrega ninguna A/B.

## Puerta editorial (antes del render final; `pcd.py check --stage render`)
- [x] 1. La ficha está completa. Hay dos aperturas comparadas en previs y una elegida; el brief prohíbe las A/B.
- [x] 2. Primeros 1–2 s a 390 px de ancho y sin audio: se ven O3 con el balón, X4 en el aro y O2 marcado en dorado.
  - Comprobado en `E2A-BLOB-CONTACTS/hook-390px.png`, extraído del MP4 final.
- [x] 3. Hasta la primera evidencia no hay cartelas que repitan el gancho.
  - Gráficos hasta ese punto:
    - foco en X4;
    - anillo en O2;
    - fantasma de X2;
    - «BOX» en el suelo;
    - placa INBOUNDER.
- [x] 4. La promesa se cumple en E ≈ 14 s (bandeja de la lectura A) y en E ≈ 27–28 s (triple de la lectura B), con el balón atravesando el aro en los dos casos.
- [x] 5. El final cierra la pregunta. Pregunta concreta de decisión defensiva (RIM o SWITCH) sobre el fotograma de la decisión.
- [ ] 6. Datos observables tras publicar (ventanas equivalentes, plataforma, denominadores). «Sin dato» si la plataforma no los da.

## Registro de resultados (tras publicar)
| Variante | Plataforma | Ventana | Vistas | Retención / visionado medio | Interacción | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| única | | | sin dato | sin dato | sin dato | |
