# NBA vs EuroLeague: validación reglamentaria (2026-11-24)

## Cómo se ha verificado
- **Desde este contenedor no se pueden abrir** official.nba.com, about.fiba.basketball, assets.fiba.basketball, mediacentre.euroleague.net ni euroleaguebasketball.net. El proxy de red los bloquea (403 o DNS).
- **NBA:** el texto se ha contrastado con los fragmentos de las páginas oficiales que devuelve el buscador (official.nba.com, Rule 1, Rule 3 y Rule 10). También con el videorulebook.nba.com.
- **FIBA:** se ha usado el texto de las Official Basketball Rules 2024 (en vigor desde el 1 de octubre de 2024), que ya conocíamos. No se ha podido abrir en directo el PDF de 2026.
- **EuroLeague:** las novedades 2026-27 se han revisado en la prensa especializada (Eurohoops, Flashscore y otros), no en la web oficial.
- **Recomendación:** antes de publicar, que una persona compruebe el PDF FIBA 2026 y la nota oficial 2026-27 de EuroLeague. Basta con los 4 puntos de abajo.

## Las 4 diferencias

| # | Afirmación del vídeo | NBA | FIBA / EuroLeague | Estado |
|---|---|---|---|---|
| 1 | NBA 4 × 12:00 = 48; EuroLeague 4 × 10:00 = 40 | Rule 5: cuartos de 12 min | Art. 8: 4 periodos de 10 min | NBA verificado (oficial vía buscador). FIBA según texto 2024. Las novedades 2026-27 de EuroLeague no cambian la duración. |
| 2 | Triple frontal: NBA 7,24 m; EuroLeague 6,75 m | Rule 1: arco de 23'9" (7,24 m) desde el centro del aro. Rectas a 3 ft (0,91 m) de las bandas, es decir, a 22 ft (6,71 m) en las esquinas. | Art. 2.2.4: 6,75 m. Rectas a 0,90 m de las bandas, es decir, a 6,60 m en las esquinas. | Verificado. La línea NBA no tiene un radio único: sus esquinas son más cortas, y así está modelada. |
| 3 | EuroLeague: 5 faltas = fuera; NBA: 6.ª falta personal = descalificado | Rule 3 Sec. I: el jugador queda descalificado al recibir su sexta falta personal (excepción: si no quedan suplentes) | Art. 40: el jugador con 5 faltas (personales y técnicas) debe abandonar el partido | NBA verificado. FIBA según texto 2024. El vídeo dice «FIVE! And you're out» y muestra «PERSONAL FOULS» de un solo jugador. No habla de faltas de equipo ni de expulsión disciplinaria. |
| 4 | Defensive 3 seconds solo en la NBA | Rule 10 Sec. VII: un defensor en la zona (16 ft) debe defender activamente a un rival en 3 segundos (a un brazo de distancia y en posición de defensa) o salir. La cuenta se suspende si hay tiro, pérdida de control, defensa activa, si sale de la zona o si es inminente que quede legal. Sanción: falta técnica. | No existe una regla equivalente. Solo están los 3 segundos ofensivos (Art. 26). | Verificado. La sanción es 1 tiro libre y el ataque conserva la posesión (Rule 12 A, falta técnica). Esto último sale de una fuente secundaria (Wikipedia), no del texto oficial. |

## Lo que el vídeo NO afirma (por indicación del brief)
- No dice que la defensa zonal esté prohibida en la NBA. Es legal desde 2001 y la regla es solo la de los 3 segundos defensivos.
- No confunde los 3 segundos ofensivos con los defensivos. En la escena EuroLeague aparece el rótulo «OFFENSIVE 3 SECONDS STILL APPLIES».
- No dice que las defensas europeas sean estáticas ni que todos los tiros cerca del aro sean más difíciles. Solo dice: «The big can stay home and protect the rim».
- La 6.ª falta NBA no se presenta como una expulsión: el rótulo es «FOULED OUT».

## Condiciones del ejemplo de 3 segundos defensivos (comprobadas sobre los cuerpos renderizados con `scripts/qc-nbaeu.mts`)
- El ataque controla el balón en su pista delantera: O1 bota en lo alto y es el único jugador que toca el balón.
- X5 tiene la pelvis dentro de la zona durante toda la jugada.
- X5 nunca está a menos de 1,2 m de un atacante, con las manos incluidas. Es decir, no defiende activamente a nadie.
- Ningún atacante pisa la zona: así no entran en juego los 3 segundos ofensivos.
- No hay tiro durante la cuenta.
- El reloj de juego avanza 1 s por cada número («One», «two», «three»). La técnica se pita a los 3,1 s.

## Geometría (comprobada sobre los cuerpos)
- Las dos pistas comparten el mismo mundo: el centro del aro está fijo y solo cambian las líneas pintadas. No se ha escalado ninguna pista.
- El tirador está a 7,05 m del centro del aro. En el despegue, todos los puntos de sus suelas están entre 6,815 y 7,157 m.
- Eso queda fuera de la línea FIBA (6,75 m, con la pintura hasta 6,775 m): son 3 puntos en EuroLeague.
- Y queda dentro de la línea NBA (7,24 m, con la pintura desde 7,215 m): son 2 puntos en la NBA.
- El balón entra por el aro en los dos tiros (control «ball through the rim»).

## Fuentes consultadas
- https://official.nba.com/rule-no-1-court-dimensions-equipment/ (vía buscador)
- https://official.nba.com/rule-no-3-players-substitutes-and-coaches/ (vía buscador)
- https://official.nba.com/rule-no-10-violations-and-penalties/ (vía buscador)
- https://videorulebook.nba.com/archive/defensive-three-seconds-defender-remains-in-lane-for-longer-than-3-seconds
- https://about.fiba.basketball/en/news/fiba-official-basketball-rules-2024-come-into-force-on-october-1
- https://www.eurohoops.net/en/euroleague/2008221/euroleague-basketball-announces-rule-updates-for-2026-27-season (2026-27: inicio del tiro, faltas «disruptive» y «flagrant», flopping. Nada de esto afecta a estas 4 reglas.)
- https://en.wikipedia.org/wiki/Defensive_three-second_violation (secundaria, para la sanción)
