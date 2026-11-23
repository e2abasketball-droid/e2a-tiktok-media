# HORNS — cámara y composición

## Una sola cámara para todo el vídeo
| Parámetro | Valor |
|---|---|
| Tipo | órbita fija (`orbit`), sin movimiento |
| Objetivo | (0,0; 7,45; 0,6) m: centro de la formación 1-2-2, un poco por encima del codo |
| Distancia | 22,0 m |
| Inclinación (pitch) | 52° |
| Yaw | 0°: canasta arriba, cámara detrás del ataque, sin cambiar de lado |
| FOV | 50° |
| Formato | 1080×1920, 30 fps |

No hay órbitas, ni roll, ni cortes de cámara: las siete tomas usan la misma cámara. Lo único que cambia es el tiempo de la jugada (cámara lenta y congelados) y los gráficos.

## Cómo se eligió
- `scripts/fit-search.mts` probó combinaciones de distancia, inclinación y FOV para que los 10 jugadores (pies y cabeza) quepan en la banda segura vertical 380–1330 px durante 2,4–9,4 s de jugada. Con FOV 40 no encontró ninguna, así que se usó FOV 50 e inclinación 52.
- La cancha se bajó en el encuadre para que los títulos de arriba (y ≈ 236) no tapen el tablero ni a los jugadores.

## Comprobación en todos los fotogramas (`scripts/frame-fit.mts`)
- **Primera versión:** tenía un zoom del 10 % en la toma *read* (16,6–20,6 s). `frame-fit` marcó que **O3 y X3, en la esquina derecha, salían del cuadro** (hasta x = 1213 px en un ancho de 1080). Con la cámara principal, los tiradores de las esquinas quedan a 17–25 px de los bordes, así que ningún zoom cabe.
- **Corrección:** zoom eliminado. La toma *read* se queda en la misma cámara. Se volvieron a renderizar solo los fotogramas 497–620.
- **Resultado final:** `frame-fit` con banda 380–1330 px y margen lateral de 12 px da **0 fotogramas marcados de 1289**. Los 10 jugadores están dentro en todo el vídeo.
- Límite conocido: los tiradores de las esquinas quedan muy cerca del borde lateral (17–25 px). Están enteros, pero no hay aire a los lados.

## Zonas de texto
- Títulos: arriba, en y ≈ 236, de 2–4 palabras.
- Subtítulos: abajo, en y = 1390, una frase por bloque, con palabras clave en dorado.
- Logo 2026: solo el último 1,6 s, pequeño.
- La acción vive entre 380 y 1330 px, así que ni títulos ni subtítulos tapan a ningún jugador.

## Gráficos tácticos (máximo 2 a la vez)
- Anillo dorado #C9A24D solo en el jugador clave (X4). En *setup* hay anillos de presentación en los interiores (dorado) y las esquinas (blanco).
- Rutas: ROLL en azul claro #8EC5F0 y POP en dorado, de 0,09 m de grosor y con su etiqueta en el suelo.
- Línea de pase blanca, solo mientras vuela el balón.
- Etiquetas de una palabra: HELP, STAY, ROLL; y «OPEN THREE» (antes «POP → THREE»; la fuente no tiene la flecha).
- Sin fuego, partículas, flashes ni temblores.
