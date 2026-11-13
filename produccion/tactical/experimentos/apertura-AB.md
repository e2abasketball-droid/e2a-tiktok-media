# Experimento de retención — apertura A/B (diseño, NO programado)

Estado: **propuesta** (2026-11-13). No crea publicaciones ni cambia tareas. Activarlo requiere decisión del propietario.

## Hipótesis
Ver el segundo bloqueo y la ventaja en el primer segundo (B) retiene más que abrir detrás del defensor (A, como Stagger V2).

## Variantes
| | A — detrás del defensor | B — ventaja en el primer segundo |
|---|---|---|
| 0–1 s | POV detrás del defensor del tirador (`pov behind X2`), titular corto | Plano alto que ya muestra los dos bloqueadores y la separación del tirador (anillos + línea de separación desde el fotograma 0) |
| Pregunta | La que plantee el guion | Pregunta o decisión explícita en pantalla antes de 1,0 s («¿Persigues o cambias?») |
| Igual en ambas | Voz (misma voz Deuce, misma toma por guion), subtítulos, duración 30–40 s, motor Tactical3DV2, tipo de jugada (acción con bloqueo y dos lecturas), música de la biblioteca propia, CTA final |

Implementación: solo cambia la primera toma (`shots[0]`) del episodio; el resto del episodio es idéntico en estructura. Cada vídeo es una pieza distinta (jugada distinta): nunca se publica el mismo vídeo dos veces en un canal.

## Calendario (franjas vigentes: `config/tactical_studio.json` → 10:00 y 13:00 Australia/Sydney)
Diseño cruzado para anular el efecto de la hora: día 1 V01=A / V02=B, día 2 V01=B / V02=A, y así sucesivamente. Mínimo **6 pares (12 vídeos, 6 días)**. Si un hueco está ocupado o un vídeo falla el QC, ese par se descarta entero (no se compara un vídeo sin su pareja).

## Registro (una fila por vídeo, plataforma y ventana)
`content_id · variante · plataforma · fecha/hora Sydney · duración (s) · ventana (24 h / 72 h / 7 d) · métricas · fuente · observed_at`

| Plataforma | Métrica primaria | Secundarias | Fuente real (comprobado 2026-11-06 en P2-A) |
|---|---|---|---|
| YouTube Shorts | **Stayed to watch** (% que no deslizó) | % medio visto = duración media (YTVP08) / duración; engaged views | Stayed to watch **solo en YouTube Studio** (Analytics → Contenido → Shorts): Metricool no lo da → copia manual o YouTube Analytics API (no conectada). YTVP08 sí está en Metricool. |
| Instagram Reels | % medio visto = tiempo medio (IGRE24) / duración (IGRE26) | alcance, compartidos/alcance, guardados, seguidores | Metricool: IGRE24 y IGRE26 sí; `retention` (IGRE27) llegó **null** en 20/20 reels. Tasa de salto/retención por segundo: solo en Instagram nativo → «sin dato» si no se copia. |
| TikTok | % medio visto = tiempo total / reproducciones / duración | compartidos/reproducción, seguidores | Metricool: `fullVideoWatchedRate` y `totalTimeWatched` llegaron **null** en 23/23 → primaria «sin dato» en Metricool; TikTok Studio nativo muestra tiempo medio y % vídeo completo. |

Si una métrica no llega: se escribe «sin dato» y se indica si existe en la app nativa (columna `fuente`). Nunca 0.
Las lecturas de Metricool son acumuladas: la ventana es la lectura más cercana a 24 h / 72 h / 7 d (`metricool_ingest.py`, rama `feature/multiagent-v2-p2a-metricas` del Knowledge Hub).

## Cómo interpretar con muestras pequeñas
- Comparar **solo dentro de cada plataforma** y **por pares del mismo día** (B − A), nunca medias globales entre redes.
- Primaria por plataforma: test de signos sobre los pares. Con 6 pares, B gana 6/6 → p ≈ 0,016 (una cola); 5/6 → p ≈ 0,11 (indicio, no prueba).
- Decisión propuesta: adoptar B si gana ≥ 5/6 pares en la primaria de YouTube **y** la mediana de la diferencia es ≥ +3 puntos, sin que compartidos/reproducción empeoren > 20 %. Si no, «no concluyente» → ampliar a 10 pares o cerrar.
- Registrar a la vez tipo de jugada y hora para descartar que una jugada muy buena decida el resultado (revisar el par atípico a mano).

## Lo que falta para ejecutarlo
1. Decisión del propietario y orden de variantes en el prompt diario (no se ha tocado).
2. Una plantilla de primera toma «B» en el motor (cámara alta inicial con anillos y separación desde el fotograma 0).
3. Acceso de lectura a «Stayed to watch» (copia manual semanal o YouTube Analytics API).
