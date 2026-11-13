# Alojamiento GitHub Raw fijado a commit — validación 2026-11-12

Sin subir nada nuevo: se validó con los dos MP4 que Metricool ya aceptó el 7-nov (rama `claude/manual-2026-11-08`).

| Comprobación | video_01 (commit 991fdd1b…) | video_02 (commit e60206a4…) |
| --- | --- | --- |
| HTTP | 200, 0,49 s | 200, 0,43 s |
| Descarga completa | 10.904.303 B = content-length | 6.655.584 B = content-length |
| Integridad | sha256 descarga = sha256 del blob git (de892a56…) | igual (33ce276c…) |
| Formato | H.264 1080×1920 + AAC, 25,1 s | H.264 1080×1920 + AAC, 31,4 s |
| Range (206) | sí | sí |
| Content-Type | application/octet-stream (Metricool lo aceptó igualmente) | igual |
| Metricool | aceptado al programar (posts 420159756 y 420153674, 7-nov) | igual |

Persistencia: la URL lleva el sha del commit, no el nombre de la rama: el contenido no puede cambiar. Solo desaparece si el commit deja de ser alcanzable (borrar la rama o force-push), por eso la rama de vídeos debe protegerse igual que `studio-state`.
Límites: archivo < 100 MB (nuestros MP4 ≤ 10 MB); el repo crece ~0,56 GB/mes con 2 vídeos/día (GitHub recomienda < 5 GB por repo).
Control: el gate `asset` solo acepta una URL https cuyos bytes coincidan con el MP4 QC_PASS y con licencias oficiales; los MP4 con licencias de prueba quedan rechazados (asset-V0x-refused.txt).
