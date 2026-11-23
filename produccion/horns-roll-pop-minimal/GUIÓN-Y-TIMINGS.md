# HORNS: THE DEFENDER'S DILEMMA — guion y tiempos

> **Los tiempos de este documento son tiempos GUÍA, no de una locución real.** No hay voz aprobada (no se han gastado créditos de ElevenLabs). Los subtítulos y los cortes siguen estos tiempos guía. Cuando exista una toma aprobada, se recalculan solos desde sus palabras (ver «Ruta editable»).

## Guion (fijo, del documento maestro): 16 frases, 73 palabras

| # | Clave | Frase | Inicio (s) | Fin (s) | Toma |
|---|---|---|---|---|---|
| 1 | hook1 | Don't watch the ball. | 0,15 | 1,18 | hook |
| 2 | hook2 | Watch this defender. | 1,30 | 2,36 | hook |
| 3 | horns | This is Horns. | 3,00 | 3,92 | setup |
| 4 | bigs | Two bigs at the elbows, | 4,25 | 5,56 | setup |
| 5 | corners | with shooters in both corners. | 5,70 | 7,36 | setup |
| 6 | screen | The guard takes Five's screen. | 8,70 | 10,46 | action |
| 7 | roll | Five rolls hard to the rim. | 11,00 | 12,77 | action |
| 8 | pop | Four pops behind the arc. | 13,30 | 14,97 | action |
| 9 | read | Now this defender has to read both. | 16,95 | 19,12 | read |
| 10 | help | If he tags the roll, | 20,30 | 21,52 | branchA |
| 11 | three | Four is open for three. | 21,70 | 23,07 | branchA |
| 12 | stay | If he stays with Four, | 28,30 | 29,62 | branchB |
| 13 | inside | the pass inside might be there. | 29,80 | 31,67 | branchB |
| 14 | setup | Same setup. | 35,50 | 36,26 | close |
| 15 | threats | Two threats. | 36,65 | 37,45 | close |
| 16 | pressure | That's the pressure Horns creates. | 37,95 | 39,96 | close |

La última palabra termina en 39,96 s y la cola es de 3,0 s, así que el vídeo dura **42,958 s** (1289 fotogramas a 30 fps). Ritmo: 73 palabras en 39,8 s, unas 110 palabras por minuto contando las pausas.

## Tomas (una cámara, un corte por bloque de frases)

| Toma | Entra (s) | Dura (s) | Tiempo de jugada mostrado | Gráficos |
|---|---|---|---|---|
| hook | 0,000 | 2,81 | 5,95 → 6,60 y congelado | anillo dorado en X4; «DON'T WATCH / THE BALL.» → «WATCH HIM.»; FREEZE |
| setup | 2,808 | 5,55 | 0,00 → 2,55 en tiempo real, luego 2,55 → 3,90 a 0,45× | anillos en O4/O5 (dorado) y O2/O3 (blanco); título HORNS |
| action | 8,361 | 8,21 | 3,90 → 5,50 a 0,7×, luego 5,50 → 6,60 a 0,2× | ruta ROLL (azul claro) y ruta POP (dorado), con etiqueta en el suelo |
| read | 16,574 | 3,20 | 6,60 congelado (fotograma de decisión) | anillo en X4; dos líneas discontinuas: ayuda / quedarse; FREEZE |
| branchA | 19,771 | 7,50 | 6,60 → 7,55 (0,4×) → 8,75 (0,55×) → 10,20 (0,5×) | pin HELP, línea de pase, pin OPEN THREE |
| branchB | 27,267 | 7,40 | 6,30 → 6,60 (0,27×) → 7,55 → 8,20 → 9,70 (0,54×) | sello «SAME ACTION. DIFFERENT HELP.», pines STAY y ROLL, línea de pase |
| close | 34,667 | 8,29 | 6,60 congelado | rutas ROLL/POP; «ONE SET. / TWO READS.»; «HELP OR STAY?»; logo 2026 el último 1,6 s |

Notas sinceras:
- **hook (2,8 s) y read (3,2 s)** son más cortas que las 4–8 s del estilo, porque cada una cubre una sola frase. **action (8,2 s) y close (8,3 s)** pasan un poco de 8 s.
- **branchB** arranca en 6,30 s de jugada, 0,3 s antes del fotograma de decisión. Ese tramo es idéntico en A y B (`test-branches`: máx. 0,12 cm). Llega al 6,60 en 1,1 s de pantalla, mientras está el sello, y desde ahí diverge.
- **Desviación del estilo:** el tiro de A (8,65 → 9,70) y la finalización de B (8,85 → 9,30) van a unos 0,5×, no casi a tiempo real. Así las frases 11 y 13 caben sobre la acción con los tiempos guía. Con la voz real puede ajustarse el `remap` de esas dos tomas sin tocar la jugada.

## Ruta editable (re-timing sin reanimar)
Cada corte está anclado al inicio o fin de su frase (`LINES[...]` en `template/tactical/episodes/_gen-horns-roll-pop.py`). Con una toma real:
1. Generar **una** toma con la voz aprobada (solo con autorización; estimación ~400 créditos de ElevenLabs).
2. Sacar los tiempos por palabra (Scribe) y montar la pista con `scripts/tactical-voice.py`, como en los episodios anteriores.
3. `python3 tactical/episodes/_gen-horns-roll-pop.py --out props.json --words <words.json> --voice <voz.wav> --music tactical/horns/music-bed.mp3`
4. Volver a renderizar. Las jugadas (`horns-rp-a-help`, `horns-rp-b-stay`) no se tocan: solo se mueven los cortes, los subtítulos y los gráficos.
5. Mezclar la voz por encima de la música con ducking y medir loudness.
