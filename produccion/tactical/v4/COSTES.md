# V4 — Coste por pieza y por día (medido)

| Recurso | Muestras medidas | Máx. por pieza | 2/día (V3) | 4/día (V4) |
|---|---|---|---|---|
| Voz ElevenLabs (1 toma) | RAM V2 348, RAM V1 426, Hammer 447, Spain 478, Flare 508 cr | 508 cr | 1 016 cr | 2 032 cr |
| Scribe (transcripción) | RAM V2 94, RAM V1 156, Flare 166 cr | 166 cr | 332 cr | 664 cr |
| **Créditos totales** | | **674 cr** | **1 348 cr/día ≈ 41 k/mes** | **2 696 cr/día ≈ 82 k/mes** |
| Render Remotion completo | 1 700 / 1 858 / 1 960 s | 1 960 s | 65 min | 2 h 11 min |
| Llamadas createScheduledPost | 1 por vídeo (3 redes agrupadas) | 1 (+1 reintento) | 2 (máx. 4) | 4 (máx. 6) |
| Destinos | 3 por vídeo | | 6 | 12 |

Fuentes: INFORME de RAM V1 y V2, informe diario 2026-11-14 (Flare), memoria de la prueba E2E (Hammer 447 y Spain 478), tiempos de render en los informes de RAM y de calidad del 13 nov.

**Sin verificar.** El saldo y el límite mensual de ElevenLabs: el conector devuelve «requiere permisos adicionales» y hay que reconectarlo. Hasta leerlo, que 82 k cr/mes quepan en el plan es un **supuesto**. La capacidad de Metricool (Starter 5, programación ilimitada con uso razonable) está verificada el 13 nov; 4 posts de vídeo al día no se han probado.

**Presupuesto V4 propuesto** (`config/tactical_studio.v4-shadow.json`, sin aprobar):
- 4 tomas, 2 100 cr de voz y 700 cr de Scribe;
- 6 renders y 6 llamadas;
- 12 publicaciones.

Hoy Scribe no lo cuenta el control de presupuesto del Studio V3: es una fuga de unos 166 cr por vídeo que V4 cierra con su propia línea.

**Ahorros sin repetir contenido** (propuestas, no aplicadas):
1. **Quitar Scribe** usando las marcas de tiempo que devuelve la síntesis (−94 a −166 cr por pieza, −15 a −25 %). Hay que comprobar que la herramienta de voz las expone.
2. **Guion objetivo de 80–85 palabras** en vez de 90–95 (la voz cobra por carácter): alrededor de −8 %.
3. **Un único render maestro por jugada para social y curso.** El Course3D 16:9 de 6,6 s tarda minutos, no repite voz y no gasta créditos.
4. **No regenerar la voz en los A/B editoriales.** El A/B de RAM V2 reutiliza el audio del control: 0 cr.
