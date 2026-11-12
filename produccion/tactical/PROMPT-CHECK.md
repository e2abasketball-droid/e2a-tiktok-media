# E2A — TACTICAL CHECK (prompt corto, 08:30 Sydney, solo lectura)

Comprueba los 2 vídeos de HOY con `python3 tools/tactical_studio.py plan --date <hoy>` y la lectura de
Metricool (`getScheduledPosts` del día, timezone Australia/Sydney).
- Si ambos están `scheduled_confirmed`: informe «OK» de 3 líneas.
- Si falta alguno, hay un duplicado o una colisión con otro post a la misma hora: informe de incidencia con
  `content_id`, red y causa. NO programes, edites, muevas ni borres nada: esta tarea no tiene herramientas
  de escritura. La corrección es humana.
- Lanza analítica pendiente (24 h / 72 h / 7 d) solo con métricas reales de `getAnalyticsDataByMetrics`;
  si no hay dato, escribe «sin dato», nunca un número inventado.
