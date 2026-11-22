# Cómo se mantiene Football separado de Basketball

| Riesgo | Mecanismo | Se comprueba con |
| --- | --- | --- |
| Editar un archivo de baloncesto | Football solo escribe en `football/`, su agente y `/mnt/project-files/football/` (`config/division.json` → `write_allow` / `write_deny`) | `fb.py guard <ruta>`; `check_isolation.py` compara los 292 archivos de la base byte a byte |
| Sobrescribir renders de baloncesto | Todo archivo generado lleva id `FB-` y va a la carpeta de producción de fútbol; `new-production` nunca reutiliza una carpeta existente | pruebas `Guard` |
| Que cambie una pieza compartida sin enterarnos | Registro con commit y huella por pieza | `fb.py shared verify` |
| Usar lógica de baloncesto en fútbol | Piezas de categoría C rechazadas por `resolve` | prueba `test_category_c_refused` |
| Mezclar configuración | Config propia en `football/config/`; nunca lee `config/tactical_studio.json` ni la delegación del Tactical Studio | `check_isolation.py` |
| Publicar por error | `publishing.json` en `disabled`, redes apagadas, sin escrituras en Metricool; no hay código de fútbol que llame a Metricool | `check_isolation.py` |
| Dependencias nuevas | La fase 1 no añade manifiestos de paquetes; Remotion se fijará a las mismas versiones | `check_isolation.py` |
| Secretos | Ningún token ni dato personal en archivos de fútbol | `check_isolation.py` (+ `scripts/check_secrets.sh` del Knowledge Hub) |
| Agente elegido para baloncesto | Descripción con exclusión explícita | `check_isolation.py` (frontmatter) |
| Tareas programadas | Football no crea ni toca tareas | No se ve desde Git: se compara `list_triggers` antes/después en cada fase |

## Ramas
Trabajo en ramas propias de la sesión o `claude/football-*`. Nunca push a `main`, `tactical-media`, `studio-state`
ni a ramas de baloncesto. Cuando haya publicación aprobada: `football-media` y `football-state`.
