# NBA vs EuroLeague V3: informe (2026-11-24)

**Sin publicar.** La V1 y la V2, con sus MP4, siguen intactas. Rama `claude/project-thread-5a4aj1`, sin fusionar.

## Entregables
| # | Archivo |
|---|---|
| 1 | `E2A-NBA-EUROLEAGUE-HOOK-A.mp4` (5,7 s) |
| 2 | `E2A-NBA-EUROLEAGUE-HOOK-B.mp4` (5,7 s, mismo audio) |
| 3 | `E2A-NBA-VS-EUROLEAGUE-V3.mp4` (41,5 s, con Hook A) + `…-V3-TRIAL.mp4` (variante para trial reel) |
| 4 | `COMPARA-V2-V3-1…6-*.jpg`: intro, marcadores, triple, faltas, 3 segundos y cierre |
| 5 | `REDUCCION-TEXTO-V3.md` |
| 6 | `INFORME-ANIMACION-V3.md` |
| 7 | `QA-V3.md` + `QA-A-primeros5s-hookA/B.jpg` + `QA-C-legibilidad-movil.jpg` |
| 8 | `PRESET-E2A-PREMIUM-VISUAL-STORYTELLING.md` (componentes reutilizables) |

## Storyboard final (voz de la V2 intacta, 41,44 s)
| Tramo | V3 | Brief |
|---|---|---|
| Hook | 0–5,7 | 0–4,5 |
| Cuartos | 5,7–10,9 | 4,5–9 |
| Triple | 10,9–18,8 | 9–17 |
| Faltas | 18,8–24,0 | 17–21 |
| 3 segundos | 24,0–38,6 | 21–36 |
| Cierre | 38,6–41,4 | 36–39 |

Los tiempos siguen a la locución aprobada. Para cuadrar con el storyboard habría que acelerar o cortar la voz, y el brief lo prohíbe. Se mantiene la duración de unos 41,5 s, como permite el brief.

## Hook A frente a Hook B
| | A «Same Game, Different Rules» | B «Cinematic Dual Court» |
|---|---|---|
| Fotograma 0 | primer plano de un jugador, sin texto | pista desde arriba con el tirador pequeño |
| Qué entiende el espectador al segundo 1 | dos ligas, el mismo jugador y la misma acción | dónde está cada línea de triple |
| Logotipos | pestañas en la costura al partirse la pantalla (1,5 s) | pestañas desde «NBA» (0,1 s) y «EuroLeague» (0,8 s) |
| Avance del +2/+3 | 4,1 s | 4,1 s |

**Principal: A.** Mi hipótesis es que un primer plano humano en movimiento retiene mejor el primer segundo que un plano cenital. B explica antes la diferencia de arcos. **No hay métricas que lo demuestren:** propongo probar B como trial reel o en una segunda publicación y comparar la retención a 3 s.

## Cambios principales respecto a la V2
- **Gráficos:**
  - Subtítulos en minúscula y en una línea.
  - Marcadores compactos iguales (solo liga, Q1 y reloj; sin equipos, puntos ni posesión).
  - Sin cabeceras, sin palabras gigantes en el suelo y sin etiqueta FREEZE.
- **Triple:** plano de detalle más cercano y corte de continuidad al mismo tiro en la NBA. +3/+2 con profundidad que desaparecen.
- **3 segundos:** cámara en 3/4 igual en las dos escenas. En EuroLeague hay una penetración real y el pívot defiende el aro.
- **Cierre:** una frase, pestañas de liga y logotipo E2A pequeño, con el encuadre del hook para enlazar en bucle.

## Texto de la publicación propuesto (nota de 3 segundos ofensivos)
> NBA vs EuroLeague: same game, different rules. 12-minute quarters vs 10, a 7.24 m arc vs 6.75 m, 6 fouls vs 5, and defensive three seconds only in the NBA (offensive three seconds still apply in both). Which rules would you rather play under?

## Créditos y servicios
- **0 créditos de ElevenLabs:** voz y música reutilizadas de la V2.
- Ningún servicio de pago adicional.

## Logotipos y licencia
- Los archivos son los que aportaste (NBA PNG y EuroLeague JPG). Solo se ha recortado el margen, sin cambiar colores ni proporciones.
- Ningún texto sugiere colaboración oficial.
- **La licencia para uso comercial sigue sin confirmar:** las versiones son de revisión. Si no se confirma, se renderiza la versión sin logotipos (unos 15 min) quitando `template/public/leagues/`.

## Defectos conocidos
1. Licencia de los logotipos pendiente.
2. El logotipo de EuroLeague en el marcador compacto y la pestaña NBA del hook quedan pequeños en móvil.
3. Unos fotogramas del hook con el balón en el borde superior de cada mitad.
4. La cuenta 1-2-3 tapa parte del tablero.
5. «DEFENSIVE 3 SECONDS» coincide con la voz que lo dice: el brief pide revelarlo en ese momento.
6. En los cuartos no hay acción 3D (pista vacía antes del salto). Es el único bloque que se apoya en el gráfico.
7. No he escuchado el resultado: el audio es el mismo archivo de la V2, verificado por medidas.

## Reproducir
`python3 tactical/episodes/_gen-nbaeu-v3.py --hook A|B --out props.json` y después el render habitual de Tactical3DV2.
