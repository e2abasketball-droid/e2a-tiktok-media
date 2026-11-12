# Fase 1 — ¿Funciona `createScheduledPost` con el plan actual? (2026-11-12, sin crear publicaciones)

Respuesta: SÍ, verificado con evidencia real de esta cuenta y este plan.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Permiso efectivo | `createScheduledPost` creó el post 426159230 (Stagger V2) con este usuario y plan; `createScheduledPostForReview` da 403 (sin gestión de equipos) | respuesta real en `tools/tests/fixtures/metricool_create_response_426159230.json` |
| Tres redes en un post | El 426159230 salió **PUBLICADO** el 13-nov 10:00 Sydney en Instagram (Reel), TikTok y YouTube (Short) | lectura `getScheduledPosts` 2026-11-12 ~23:35Z: los tres proveedores `PUBLISHED` con URL pública |
| URL de GitHub Raw | Metricool aceptó URLs raw fijadas a commit (posts 420159756 y 420153674, 7-nov) | `prueba-2026-11-20/evidencias/hosting-github-raw.md` |
| Rehospedaje | Metricool copia el medio a `static.metricool.com/planner/...mp4` (el mismo fichero en los dos posts del Stagger) | lectura |
| Campos por red | `instagramData.type REEL`, `tiktokData.privacyOption/title/isAigc`, `youtubeData.title/type short/privacy/category/madeForKids/isAiGeneratedContent` según el esquema actual de la herramienta | esquema leído el 2026-11-12 |
| Hora de Sydney | `date` `YYYY-MM-DDTHH:MM:SS+11:00` + `publicationDate {dateTime, timezone: Australia/Sydney}`; la marca tiene zona `Australia/Sydney` | `getBrandSettings` |
| Retorno | `data.id`, `data.uuid`, `plannerUrl`, `providers[].status` `PENDING` | fixture |
| Confirmación | `getScheduledPosts` devuelve también los ya publicados (con `publicUrl`) | lectura |
| Cuentas oficiales | instagram `e2a_basketball`, tiktok `e2a.basketball`, youtube `UCdjEpbOnxtCaNn1m7YXyJqQ` (marca 7681319) | `getBrandSettings` |
| Límite del plan | **Desconocido.** No hay herramienta que lo lea; la regla «20/mes» de la memoria es de la rutina semanal de Instagram | bloqueo D |

Diferencias a tener en cuenta:
- La lectura no devuelve `tiktokData.isAigc` aunque se envíe: la confirmación no depende de ese campo.
- Verificar los BYTES del medio exige leer `static.metricool.com`, bloqueado por la red de este entorno (bloqueo B).
