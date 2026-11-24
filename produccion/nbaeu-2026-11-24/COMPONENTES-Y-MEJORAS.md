# NBA vs EuroLeague: componentes reutilizados y mejoras gráficas (2026-11-24)

Rama `claude/project-thread-5a4aj1` del repo e2a-tiktok-media (sale de la rama de 4 Basketball Rules). No está fusionada.
Todas las novedades del motor son opcionales: si un episodio no las pide, el motor se comporta igual que antes.

## Reutilizado tal cual
- Motor 3D Tactical3DV2 (Remotion + three.js), cuerpos v33, ambiente «cinema», estándar visual E2A v1 (HORNS V2).
- Formato y ritmo de 4 Basketball Rules: hook inmediato, 4 bloques, rótulos grandes, pregunta final, logo 2026.
- Superposiciones de reglas de 4 Rules: zona de 2 puntos, arco de 3, títulos, chips, veredictos, marcador, congelado.
- Jugada de falta de 4 Rules (`rules4-foul`), copiada como `nbaeu-foul-el` y `nbaeu-foul-nba`.
- Herramientas: frame-fit, qc-video, voice-emphasis, voice-dynamics, trial-variant, música E2A sin SFX.
- Estándar de gráficos de suelo sin parpadeo (arcos y zona con geometría fija, sin animación por fotograma).

## Nuevo en el motor
| Pieza | Qué hace |
|---|---|
| `geometry.ts` → `COURTS {fiba, nba}` | Dos juegos de líneas sobre el mismo mundo. El centro del aro no se mueve; solo cambian las líneas. Medidas NBA pasadas de pies a metros (arco 7,24 m, esquinas 6,71 m, zona de 16 ft). |
| Pista con `courtRules` y `courtLook` | La pista se pinta con las líneas NBA o FIBA, la zona en el color de la liga y la palabra NBA o EUROLEAGUE en el suelo. |
| `lane` | Resalta la zona (relleno y borde). Se usa en la cuenta de los 3 segundos. |
| `measure` | Línea desde el centro del aro hasta un punto, con marcas en los extremos. Así se ven 7,24 m y 6,75 m medidos de verdad. |
| `arc3` / `area2` por liga | El arco y la zona de 2 se dibujan con la línea de cada liga. |
| `leagues.tsx` | Etiqueta de liga, título VS, relojes 12:00 / 10:00 con Q1–Q4 y total 48 / 40, contador de faltas personales con «FOULED OUT», contador 1-2-3 con anillo. |
| Colores de liga | NBA azul #2F6FE4, EuroLeague naranja #F28C28. Son tonos secundarios: el azul marino y el dorado de E2A siguen mandando. Sin logos oficiales. |

## Jugadas nuevas (verificadas sobre los cuerpos con `scripts/qc-nbaeu.mts`, 7/7 PASS)
- Tiro desde 7,05 m: las suelas en el despegue están entre 6,815 y 7,157 m. Triple en EuroLeague, dos en la NBA. El balón entra.
- Salida de pista tras la 5.ª falta (el jugador se va al banquillo, sin contacto violento).
- 5 contra 5 para los 3 segundos defensivos: el pívot defensor se queda en la zona sin defender a nadie, ningún atacante pisa la zona y no hay tiro.

## Mejoras gráficas respecto a 4 Basketball Rules
- Comparación en la misma pista: se cambia solo la pintura, no el plano. El arco NBA y el FIBA se ven a la vez, con la distancia medida.
- Relojes que siguen corriendo entre el plano NBA y el EuroLeague (no reinician en el corte).
- Contador de faltas que cae sobre la palabra «FIVE!» y «SIX!» de la voz.
- Reloj de juego real en los 3 segundos: 1 s de juego por número dicho, la técnica se pita a los 3,1 s y la imagen se congela con el veredicto.
- Pantalla final dividida NBA arriba y EuroLeague abajo, con la pregunta encima.
- Voz más dinámica que en 4 Rules (rango de tono 12,7 semitonos frente a 10,2) y con las cifras clave reforzadas.

## Ajustes hechos tras la revisión sin sonido
- El chip «BALL IN THE FRONTCOURT» empezaba antes de que terminara el título «DEFENSIVE 3 SECONDS» y se solapaban. Ahora entra 0,6 s después.
- La segunda línea dorada del título final caía sobre la unión de las dos pistas. Ahora está más arriba.
- La palabra pintada en el suelo (NBA / EUROLEAGUE) competía con los subtítulos. Ahora es más suave (opacidad 0,32).
