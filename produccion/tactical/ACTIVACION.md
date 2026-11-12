# Activación por etapas y vuelta atrás — Tactical Studio

Nada de esto está activo. Cada paso necesita la aprobación explícita del propietario.

| Etapa | Qué cambia | Criterio para pasar | Vuelta atrás |
|---|---|---|---|
| 0 Auditoría | Nada | Informe entregado | — |
| 1 Desarrollo | Ramas `claude/project-thread-akohki`, sin merge | Tests A–O en verde | Borrar la rama no fusionada (con permiso) |
| 2 Sombra (3 días) | Tarea STUDIO con `mode: shadow`, sin conector Metricool de escritura | 6 vídeos QC_PASS, sin intervención | Desactivar la tarea |
| 3 Piloto supervisado | `mode: supervised`: solo `createScheduledPostForReview`, cada post lo aprueba un humano en Metricool | 7 días sin incidencias | Quitar Metricool de la tarea |
| 4 Autonomía limitada (7 días) | `mode: limited` (revisión opcional) | Revisión de métricas y errores | Volver a `supervised` |
| 5 Revisión y renovación | Informe semanal | Aprobación del propietario | Desactivar la tarea |

Lo que el código NO puede garantizar (y qué lo cubre fuera del agente):
- Un agente con shell puede editar ficheros locales o llamar a un conector directamente. El registro detecta
  ediciones (cadena de hashes) y la sincronización rechaza historias divergentes o rotas, y un `authorised`
  falsificado no sirve porque `schedule-check` vuelve a preguntar al verificador. Los controles duros son
  externos: `permitted_tools` de la tarea (solo `createScheduledPostForReview`), la aprobación humana en
  Metricool y la protección de la rama de estado en GitHub (sin force-push ni borrado).

Bloqueos antes de la etapa 2:
- B1 Alojamiento del MP4: la única vía automática probada es raw.githubusercontent fijado a un commit de una
  rama de medios. Necesita autorización (repo público).
- B2 Verificador: `permitted_tools` de la tarea + flujo de revisión de Metricool. Sin probar; hasta probarlo,
  la publicación sigue siendo humana.
- B3 Saldo y licencia comercial de ElevenLabs y de la música cinematográfica.
- B5 Rama de estado: aprobar el nombre (propuesto `studio-state`) y protegerla en GitHub.
- B6 Red: este entorno bloquea static.metricool.com y drive.google.com; sin acceso a static.metricool.com la
  confirmación nunca puede verificar los bytes del medio y por tanto nunca confirma (falla cerrada).
- B4 Calendario: hoy los slots 12:00/18:00 del kit del Knowledge Hub chocan con 10:00/13:00.

Vuelta atrás general: desactivar las dos tareas en claude.ai. La rutina no puede reactivarse: no tiene el
conector Claude_Code_Remote. Ninguna publicación ya programada se toca automáticamente.
