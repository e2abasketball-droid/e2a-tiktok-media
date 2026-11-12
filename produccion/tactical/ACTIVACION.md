# Activación y revocación — Tactical Studio V3 (publicación automática delegada)

Nada de esto está activo. Sustituye al plan anterior (supervised / limited y los horarios antiguos del kit del Knowledge Hub).
`owner_manual` queda como modo de reserva si no se concede la delegación.

## Cómo funciona la autorización (fuera del alcance del agente)
| Control | Quién lo cambia | Qué impide |
|---|---|---|
| `config/delegation.tactical-studio.json` en `main` con `status: granted` | El propietario (merge a `main`) | Publicar sin delegación; el agente no hace merge |
| sha256 de ese fichero fijado en el prompt de la tarea STUDIO | El propietario (edición de la tarea) | Delegaciones creadas, ampliadas o falsificadas: cualquier otro contenido tiene otro sha |
| Cron de la tarea limitado a las fechas de la delegación | El propietario | Que siga programando después de la caducidad aunque el código fallara |
| `permitted_tools` de Metricool: STUDIO solo `createScheduledPost` como escritura; CHECK sin escritura | El propietario | `update`, borrado, revisión, mover posts |
| Sin conector Claude_Code_Remote en las tareas | — | Que una tarea cree, reactive o amplíe tareas |
| Protección de `main`, `studio-state` y `tactical-media` (sin force-push ni borrado; `main` con PR) | El propietario (rulesets) | Reescribir la historia o la delegación |

Lo que el código no puede garantizar: un agente con shell controla su propia ejecución. Por eso los controles
duros son los de la tabla (fuera del repositorio editable por el agente). El código añade: comprobación de la
delegación antes de `authorise` y antes de cada creación, registro encadenado por hash, un único camino a
`createScheduledPost`, intento registrado antes de llamar y nunca un segundo intento sin lectura del calendario.

## Etapas
| Etapa | Qué cambia | Criterio para pasar | Vuelta atrás |
|---|---|---|---|
| 1 Desarrollo (ahora) | PR sin merge | 12 pruebas + prueba integral en verde | Cerrar el PR |
| 2 Puesta en producción (UNA autorización) | Merge del PR; delegación `granted` 7 días; `mode: direct_delegated`; dos tareas con el sha fijado | Bloqueos A–E resueltos | Desactivar la tarea STUDIO |
| 3 Piloto real (7 días, 14 vídeos) | Programación automática 10:00 y 13:00 | Sin incidencias, informe diario | Desactivar la tarea |
| 4 Renovación | Nueva delegación (nuevo sha, nuevas fechas) | Revisión del propietario | No renovar = se para sola |

## Revocación
1. Inmediata: claude.ai → tareas programadas → desactivar o borrar «E2A — TACTICAL STUDIO». No se crea nada más.
2. Por fichero: cualquier edición de la delegación en `main` (p. ej. `revoked: true`) cambia el sha → la siguiente comprobación falla.
3. Caducidad: el cron solo se dispara dentro de las fechas; `check_delegation` rechaza fuera de `valid_from`–`valid_until`.
4. Lo ya programado sigue en Metricool; el propietario lo borra allí si quiere (el agente nunca borra).

## Bloqueos antes de la etapa 2
- A Licencias: plan y facturación de ElevenLabs el 12-nov, términos de la voz Deuce (biblioteca compartida) y estado de eleven_v4. Solo el propietario puede cambiar `pending_owner_confirmation`.
- B Verificación del medio: RESUELTO 2026-11-13. `static.metricool.com` añadido a la red del entorno (aprobado por el propietario). Prueba real: el MP4 que Metricool sirve para el post 426159230 es byte a byte idéntico al original (9.272.409 B, sha256 32da0a16…): Metricool no recomprime, la verificación por bytes funciona.
- C Rama de medios `tactical-media`: CREADA 2026-11-13 desde main. Falta la protección (rulesets) de `main`, `studio-state` y `tactical-media`: la hace el propietario.
- D Límite de publicaciones de Metricool: RESUELTO 2026-11-13. Plan del propietario «Starter 5» (de pago, activo, mensual; captura del propietario). Los planes de pago tienen programación ilimitada sujeta a la política de uso razonable (metricool.com/pricing). El límite de 20/mes era del plan gratuito y de la regla de la rutina semanal de Instagram; el piloto añade 14 posts en 7 días. El propietario QUITÓ la regla de 20/mes el 2026-11-13 (también en el prompt de la tarea semanal de Instagram).
- E Contradicciones de configuración (horarios antiguos, `createScheduledPostForReview`, `owner_manual` como modo vigente): resueltas en este PR.
