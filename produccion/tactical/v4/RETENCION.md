# V4 — Retención por plataforma y formato (lectura 2026-11-14 16:55Z)

Fuente: Metricool (marca 7681319). Datos brutos: `retencion/snapshot-2026-11-14T1655Z.json`. Cálculo: `tools/retention_report.py`.
Reglas aplicadas: no se deduce retención de las views, no se declara ganador por volumen, cada ratio lleva su numerador, su denominador y N.

## Qué hay y qué falta

| Plataforma | Disponible en Metricool | Falta (etiquetado) |
|---|---|---|
| Instagram Reels | tiempo medio visto (s), tiempo total, alcance, % de vistas > 3 s, % de salto en 3 s, guardados, compartidos | `retention` (IGRE27) y duración (IGRE26) vienen **vacíos**: la duración se toma del MP4 publicado |
| TikTok | views, duración, comentarios, compartidos | **tiempo visto, % visto completo y alcance vienen vacíos** para todas las piezas: no hay retención de TikTok |
| YouTube Shorts | views, minutos vistos, duración media vista (s) | «se quedaron a verlo» / «deslizaron» y % medio visto **no se exponen**; además las filas paran el 11 nov (retraso de YouTube Analytics): Stagger V2, Flare y RAM aún no aparecen |

Nota de método (verificada): en Instagram, «tiempo medio visto» = tiempo total / **alcance** (821 779,5 / 46 359 = 17,73 s frente a 17,744 s). El denominador es personas alcanzadas, no views.

## Instagram: piezas 3D tácticas (N = 1 por fila)

| pieza | formato | edad | ventana | dur. s | alcance | media vista s | % medio visto | salto 3 s % | guardados ‰ | compartidos ‰ |
|---|---|---|---|---|---|---|---|---|---|---|
| elevator-v2 | tactical3d | 65.8 h | other (65.8 h) | 66.0 | 2220 | 18.155 | 27.5 | 44.9 | 14.0 | 20.7 |
| elevator-v2-2nd | tactical3d | 61.8 h | other (61.8 h) | 66.0 | 73678 | 26.078 | 39.5 | 26.7 | 9.7 | 46.1 |
| stagger-v2 | tactical3d | 41.8 h | other (41.8 h) | 33.344 | 46359 | 17.744 | 53.2 | 27.0 | 6.8 | 12.9 |
| stagger-v2-trial | tactical3d-trial | 38.9 h | other (38.9 h) | 33.344 | 26840 | 16.67 | 50.0 | 26.0 | 4.7 | 17.8 |
| flare | tactical3d | 14.8 h | other (14.8 h) | 34.901 | 13893 | 15.874 | 45.5 | 36.7 | 13.6 | 26.1 |
| ram-v1 | tactical3d | 5.5 h | other (5.5 h) | 37.312 | 1220 | 17.7 | 47.4 | 30.6 | 1.6 | 0.8 |

**Ventanas 24 h / 72 h / 7 d.** Metricool devuelve el valor acumulado en el momento de leer, no por edad. Ninguna fila cae hoy dentro de ±6 h de 24 h, 72 h o 7 d. Las ventanas solo existirán si se toma una lectura a esas edades (la tarea CHECK, de solo lectura, podría hacerlo; cambiar su prompt necesita tu OK).

**Línea base 2D (tablero), indicativa.** Tres reels de pizarra 2D de 9–11 nov, con 4–5 días de edad, N = 1 cada uno: blitz 9,4 s de media y 59,6 % de salto; elevator 2D 9,1 s y 54,9 %; stagger 2D 9,7 s y 53,3 %. Su duración (34–37 s) es la de la copia de TikTok (**inferida**). Así salen 25–28 % de media vista, frente al 45–53 % de las piezas 3D de 33–37 s. Edad, tema y duración no coinciden, así que **no es una comparación válida ni declara ganador**. Solo justifica medir.

**Lo que no se concluye.** Que Elevator 2.º tenga 73 678 de alcance no dice nada de retención. El 27,5 % de Elevator V2 (66 s) frente al 53,2 % de Stagger V2 (33 s) mezcla duración y contenido.

## Experimento propuesto (un solo cambio editorial medible)

- **Cambio:** apertura en plano táctico alto con la decisión visible desde el fotograma 0 y eje fijo hasta la revelación (variante B del A/B RAM V2). Voz, mezcla, jugada, rótulos y duración idénticos (audio byte a byte del control).
- **Métrica principal:** % de salto en 3 s en Instagram (IGRE30). Secundaria: tiempo medio visto / duración (IGRE24 y duración del MP4). TikTok y YouTube no aportan retención hoy por Metricool.
- **Diseño:** N ≥ 3 piezas por brazo, lecturas a 24 h, 72 h y 7 d, misma franja y mismo tipo de publicación (no se mezcla un trial reel con uno de feed).
- **Decisión:** solo si la diferencia en salto 3 s es ≥ 5 puntos en las tres lecturas y en la misma dirección. Si no, se mantiene el control.
- **Publicar el experimento requiere tu autorización.** No se ha programado nada.
