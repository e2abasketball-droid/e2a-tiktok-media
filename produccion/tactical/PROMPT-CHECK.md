# E2A — TACTICAL CHECK (08:30 Sydney, SOLO LECTURA)

Esta tarea no tiene herramientas de escritura: no puede programar, cancelar, mover ni modificar publicaciones.

1. `python3 tools/studio_sync.py pull` (sin lease) y `python3 tools/tactical_publisher.py status <hoy>`.
2. `getScheduledPosts` de hoy (00:00–23:59 Australia/Sydney, brand 7681319).
3. Comprueba para V01 (10:00) y V02 (13:00): un único post por vídeo, en las 3 redes, a su hora, con el estado
   que registró `confirm`; ningún duplicado ni otro post nuestro a ±60 min.
4. Todo correcto → informe «OK» de 3 líneas. Si falta algo, hay un duplicado, un error de red o una colisión →
   informe de incidencia con `content_id`, red, id de Metricool y causa. La corrección es humana.
5. Analítica pendiente (24 h / 72 h / 7 d) solo con datos reales de `getAnalyticsDataByMetrics`; si no hay dato,
   «sin dato», nunca un número inventado.
