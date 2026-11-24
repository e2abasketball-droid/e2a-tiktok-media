# Reducción de texto: V2 → V3

Medido con `scripts/qc-text-density.py` sobre los props de cada versión (sin render; cuenta todo texto en pantalla y el subtítulo).

| Medida | V2 | V3 |
|---|---|---|
| Regiones de texto en todo el vídeo | 36 | 24 |
| Regiones de información adicional (nivel 4: cabeceras, notas, chips) | 12 | 0 |
| Máximo de regiones informativas a la vez (con subtítulo) | 5 (s 10,1) | 3 (s 8,7) |
| Segundos con más de 2 regiones informativas | 19,7 s | 2,0 s |
| Subtítulos | mayúsculas, hasta 2 líneas | frase normal, 1 línea (≤ 26 caracteres) |

Los 2,0 s con 3 regiones son los dos marcadores (12:00 y 10:00) con el subtítulo «it's ten.»: los dos marcadores son la misma pieza de comparación.

## Qué se ha quitado
- Cabeceras «01 QUARTER LENGTH», «02 THREE-POINT LINE», «03 PERSONAL FOULS» y el título grande «DEFENSIVE 3 SECONDS» del arranque.
- La cabecera duplicada «PERSONAL FOULS» de los contadores de faltas.
- «MINUTES PER QUARTER», «SAME SPOT → 7 m», «OUTSIDE 6.75 m», «INSIDE 7.24 m», «BALL IN THE FRONTCOURT».
- «IN THE LANE · NOT GUARDING ANYONE» (lo dice la voz y se ve en la escena) y «TECHNICAL FOUL · 1 FREE THROW · BALL KEPT».
- La etiqueta «FREEZE»: la pausa queda solo con las esquinas.
- Equipos ficticios, puntos 0–0 y reloj de posesión en los marcadores.
- Las distancias de esquina (6,71 y 6,60 m) y las dos etiquetas de liga del plano de arcos: ahora es una sola clave (NBA 7.24 m, EUROLEAGUE 6.75 m).
- Las palabras gigantes NBA y EUROLEAGUE del suelo.
- «OFFENSIVE 3 SECONDS STILL APPLIES»: pasa al texto de la publicación (ver INFORME-V3).
- En el cierre, los dos logotipos grandes y el título en tres líneas: ahora una frase en dos líneas, las pestañas de liga y el logotipo E2A pequeño.

## Qué se mantiene (información imprescindible)
12:00 y 10:00, +3 y +2, los círculos 1–5 y 1–6 con un único FOULED OUT, la cuenta 1-2-3, «DEFENSIVE 3 SECONDS», «NO DEFENSIVE 3-SECOND RULE» y después «PROTECT THE RIM», las dos distancias principales de los arcos y la identificación de liga en cada escena.

## Línea de tiempo V3 (versión principal, Hook A)
Niveles: 1 dato principal, 2 identificación, 4 información adicional. y = posición vertical en px sobre 1920.

| De | A | Dur. | Nivel | Tipo | Texto | y | tamaño | ¿Repite subtítulo? |
|---|---|---|---|---|---|---|---|---|
| 1.47 | 5.71 | 4.24 | 2 | leagueLogo | leagueLogo nba | 960 |  | no |
| 1.62 | 5.71 | 4.09 | 2 | leagueLogo | leagueLogo el | 960 |  | no |
| 4.12 | 5.71 | 1.59 | 1 | score | +2 | 250 | 150 | no |
| 4.17 | 5.71 | 1.54 | 1 | score | +3 | 1210 | 150 | no |
| 5.81 | 10.94 | 5.13 | 1 | scoreboard | board nba Q1 12:00 | 640 |  | no |
| 8.67 | 10.94 | 2.27 | 1 | scoreboard | board el Q1 10:00 | 840 |  | no |
| 12.31 | 15.00 | 2.69 | 2 | league | league el | 200 | 48 | no |
| 14.09 | 15.00 | 0.91 | 1 | score | +3 | 560 | 240 | no |
| 15.00 | 17.17 | 2.17 | 2 | league | league nba | 200 | 48 | no |
| 16.40 | 17.17 | 0.77 | 1 | score | +2 | 560 | 240 | no |
| 17.32 | 18.80 | 1.48 | 1 | arcKey | nba 7.24 m | el 6.75 m | 230 |  | no |
| 18.80 | 21.51 | 2.71 | 2 | league | league el | 200 | 48 | no |
| 18.90 | 21.51 | 2.61 | 1 | fouls | fouls 1-5 + FOULED OUT | 300 |  | no |
| 21.51 | 33.28 | 11.77 | 2 | league | league nba | 200 | 48 | no |
| 21.51 | 23.98 | 2.47 | 1 | fouls | fouls 1-6 + FOULED OUT | 300 |  | no |
| 28.37 | 31.47 | 3.10 | 1 | count3 | count 1-2-3 | 270 | 170 | no |
| 31.47 | 33.28 | 1.81 | 1 | verdict | DEFENSIVE 3 SECONDS | 320 | 60 | no |
| 33.28 | 38.61 | 5.33 | 2 | league | league el | 200 | 48 | no |
| 33.58 | 36.06 | 2.48 | 1 | verdict | NO DEFENSIVE 3-SECOND RULE | 320 | 50 | no |
| 36.65 | 38.61 | 1.96 | 1 | verdict | PROTECT THE RIM | 320 | 56 | no |
| 38.61 | 41.44 | 2.83 | 2 | leagueLogo | leagueLogo nba | 960 |  | no |
| 38.61 | 41.44 | 2.83 | 2 | leagueLogo | leagueLogo el | 960 |  | no |
| 38.66 | 41.44 | 2.78 | 1 | title | WHICH RULES WOULD / YOU PLAY UNDER? | 330 | 82 | no |
| 40.39 | 41.44 | 1.05 | 2 | logo | E2A logo | 905 |  | no |

## Línea de tiempo V2 (referencia)
| De | A | Dur. | Nivel | Tipo | Texto | y | tamaño | ¿Repite subtítulo? |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 5.71 | 5.66 | 2 | leagueLogo | leagueLogo nba | 40 |  | no |
| 0.78 | 5.71 | 4.93 | 2 | leagueLogo | leagueLogo el | 1040 |  | no |
| 5.76 | 10.94 | 5.18 | 4 | section | QUARTER LENGTH | 300 |  | sí |
| 5.81 | 10.94 | 5.13 | 1 | scoreboard | board nba Q1 12:00 + teams/scores + shot clock | 600 |  | no |
| 8.67 | 10.94 | 2.27 | 1 | scoreboard | board el Q1 10:00 + teams/scores + shot clock | 820 |  | no |
| 10.08 | 10.94 | 0.86 | 4 | chip | MINUTES PER QUARTER | 1060 | 46 | sí |
| 10.99 | 12.77 | 1.78 | 4 | section | THREE-POINT LINE | 200 |  | no |
| 12.31 | 13.07 | 0.76 | 4 | chip | SAME SPOT → 7 m | 330 | 60 | sí |
| 12.77 | 15.15 | 2.38 | 2 | league | league el | 200 | 66 | no |
| 14.09 | 15.15 | 1.06 | 1 | score | +3 (OUTSIDE 6.75 m) | 600 | 220 | no |
| 15.15 | 17.17 | 2.02 | 2 | league | league nba | 200 | 66 | no |
| 15.95 | 17.17 | 1.22 | 1 | score | +2 (INSIDE 7.24 m) | 600 | 220 | no |
| 17.17 | 18.80 | 1.63 | 4 | section | THREE-POINT LINE | 200 |  | no |
| 17.27 | 18.80 | 1.53 | 2 | league | league nba | 330 | 50 | no |
| 17.32 | 18.80 | 1.48 | 1 | score | 7.24 m (CORNERS 6.71 m) | 410 | 120 | no |
| 17.42 | 18.80 | 1.38 | 2 | league | league el | 640 | 50 | no |
| 17.47 | 18.80 | 1.33 | 1 | score | 6.75 m (CORNERS 6.60 m) | 720 | 120 | no |
| 18.85 | 23.98 | 5.13 | 4 | section | PERSONAL FOULS | 200 |  | sí |
| 18.90 | 21.51 | 2.61 | 1 | fouls | fouls 1-5 + FOULED OUT + header 'PERSONAL FOULS' | 330 |  | no |
| 21.51 | 23.98 | 2.47 | 1 | fouls | fouls 1-6 + FOULED OUT + header 'PERSONAL FOULS' | 330 |  | no |
| 24.03 | 26.49 | 2.46 | 1 | title | DEFENSIVE / 3 SECONDS | 200 | 104 | sí |
| 26.49 | 33.92 | 7.43 | 2 | league | league nba | 170 | 62 | no |
| 26.49 | 28.37 | 1.88 | 4 | chip | BALL IN THE FRONTCOURT | 300 | 48 | no |
| 28.37 | 31.47 | 3.10 | 1 | count3 | count 1-2-3 | 290 | 200 | no |
| 28.47 | 31.47 | 3.00 | 4 | micro | IN THE LANE · NOT GUARDING ANYONE | 600 |  | sí |
| 31.47 | 33.92 | 2.45 | 4 | freeze | FREEZE tag 'FREEZE' |  |  | no |
| 31.47 | 33.92 | 2.45 | 1 | verdict | DEFENSIVE 3 SECONDS | 300 | 60 | no |
| 31.72 | 33.92 | 2.20 | 4 | micro | TECHNICAL FOUL · 1 FREE THROW · BALL KEPT | 410 |  | sí |
| 33.92 | 38.61 | 4.69 | 2 | league | league el | 170 | 62 | no |
| 34.17 | 38.61 | 4.44 | 1 | verdict | NO DEFENSIVE 3-SECOND RULE | 300 | 52 | no |
| 36.23 | 38.61 | 2.38 | 4 | chip | BIGS CAN STAY → PROTECT THE RIM | 410 | 50 | sí |
| 36.53 | 38.61 | 2.08 | 4 | micro | OFFENSIVE 3 SECONDS STILL APPLIES | 510 |  | sí |
| 38.61 | 41.44 | 2.83 | 2 | leagueLogo | leagueLogo nba | 40 |  | no |
| 38.61 | 41.44 | 2.83 | 2 | leagueLogo | leagueLogo el | 1000 |  | no |
| 38.66 | 41.44 | 2.78 | 1 | title | WHICH RULES / WOULD YOU / PLAY UNDER? | 560 | 96 | no |
| 38.81 | 41.44 | 2.63 | 2 | logo | E2A logo |  |  | no |
