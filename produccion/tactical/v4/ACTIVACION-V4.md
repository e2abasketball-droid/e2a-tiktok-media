# V4 — Activación de 4 vídeos al día (preparada, NO aplicada)

Estado: **sombra**. Nada de esto está activo. La delegación vigente (V3, 2 vídeos a las 10:00 y 13:00, posts del 14 al 20 nov, sha d5be6cd2…) **no se ha cambiado ni ampliado**; lo comprueba un test.

## Qué separa el alcance vivo (2) de la producción en sombra (4)

| | V3 en vivo | V4 en sombra |
|---|---|---|
| Config | `config/tactical_studio.json` (2 franjas) | `config/tactical_studio.v4-shadow.json` (4 franjas) |
| IDs | `E2A-TACTICAL-<fecha>-V01/V02` | `E2A-TACTICAL-<fecha>-S01..S04` |
| Publica | sí, solo con la delegación fijada por sha | nunca: modo shadow, verificador blocked |
| Planificador | `tactical_studio.py plan` | `tools/tactical_planner_v4.py` (sin código de Metricool) |

Defensas en capas, todas con test:
1. El publicador solo acepta IDs `V<nn>` de una franja de **su** config, así que un `S01` se rechaza.
2. El alcance de la delegación debe coincidir campo a campo: con 4 franjas en la config, la delegación de 2 lo rechaza.
3. Un presupuesto de la config mayor que el delegado también se rechaza.
4. El planificador se niega a correr con un perfil que pueda publicar o si existe `state/tactical-v4/REVOKED`.

Los cinco bucles de «2 vídeos» (colisiones, plan y report del Studio; alcance y status del publicador) y el validador del ID salen ahora de `slot_numbers(config)`. Con la config viva, el resultado es idéntico: las 103 pruebas anteriores pasan sin cambios.

## Diff exacto para activar (`activacion-v4.diff`)

Se aplicaría **después** de que termine la ventana V3 (21 nov 00:00 Sydney), como concesión nueva, no como ampliación:
1. `config/tactical_studio.json`: 4 franjas con formato, versión 0.4.0 y presupuesto de 4 vídeos al día.
2. `config/delegation.tactical-studio.json`: borrador nuevo con `max_videos_per_day` 4, las 4 franjas y el presupuesto; fechas y concesión las pones tú.
3. `config/routine.tactical-studio.json`: CHECK pasa a las 07:30 (antes de la primera franja de las 08:30), nuevo sha fijado en el prompt de STUDIO y fechas a tu elección.

## Franjas: la decisión que falta

Con la regla de trial reel a +2 h, la rejilla inicial 10/13/16/19 deja cada trial 60 min antes de la franja siguiente. La regla de colisión (±60 min) la bloquea, y el publicador solo programa en la hora exacta de la franja, así que V02–V04 quedarían vacíos casi a diario. Lo comprueba un test y el plan real del 16–17 nov.

Alternativas calculadas con el mejor momento de publicación de Metricool (actividad de audiencia del 8 al 14 nov, no retención):
- **08:30 / 12:00 / 15:30 / 19:00:** compatible con los trials, puntuación 2,295. Es la del diff.
- **10:00 / 12:00 / 16:00 / 18:00:** la mejor (2,710) **si los trial reels no bloquearan**, lo que exigiría cambiar tu regla de colisión.
- **10/13/16/19:** 2,455, pero inválida con los trials.

## Lo que activa la aplicación del diff (pasos del propietario)

1. Aprobar el presupuesto V4 y leer el saldo de ElevenLabs (reconectar el conector).
2. Elegir la rejilla.
3. Conceder la delegación V4 (fechas de 7 días como máximo).
4. Fusionar a main.
5. Actualizar las tareas con el nuevo sha.

Hasta entonces, las dos tareas actuales siguen como están.
