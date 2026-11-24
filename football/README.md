# E2A Football

División de vídeo de **fútbol** de E2A Sports. Vive entera en esta carpeta (`football/`) y en
`/mnt/project-files/football/`, y comparte con baloncesto solo la tecnología general (voz, edición, audio, QC,
portadas), **sin tocar ni un archivo de baloncesto**.

> Estado (2026-11-23): Fase 1 (infraestructura) y Fase 2 (motor 3D, piloto third-man run) hechas en ramas sin fusionar.
> Desde la directiva **SET PIECES STUDIO V1.0** la línea editorial es **solo balón parado**, vídeo a vídeo con
> aprobación del propietario entre uno y otro (hoja de ruta en `tactical-library/setpieces/roadmap.json`).
> La publicación sigue **desactivada**.

## 1. Qué es E2A Football
Una línea de producción de vídeos tácticos y educativos de fútbol (YouTube Shorts primero, 1080×1920, inglés),
con el mismo estándar que el sistema de baloncesto y su propio catálogo, guiones, métricas, calendario y colas.
Baloncesto sigue siendo un sistema separado y protegido.

## 2. Cómo funciona su agente
Un único agente, `e2a-football-director` (`.claude/agents/e2a-football-director.md`). Dirige idea, guion,
instrucciones 3D, montaje y QC; habla en español; escribe los vídeos en inglés. Su descripción le impide activarse en
tareas de baloncesto. No publica, no usa Metricool ni ElevenLabs, no toca tareas programadas. Detalle:
[documentation/AGENTE.md](documentation/AGENTE.md).

## 3. Qué herramientas reutiliza
Las del motor compartido de categoría **A** (directas) y **B** (con adaptador de fútbol), registradas con su
commit y su huella en [`config/shared-engine.json`](config/shared-engine.json). Football las ejecuta en modo
lectura: desde su ruta si están en el commit actual, o desde una copia en caché (`football/.cache/`, fuera de Git)
si solo existen en otra rama. Tabla completa: [documentation/ARQUITECTURA.md](documentation/ARQUITECTURA.md#motor-compartido).

## 4. Qué herramientas son exclusivas de fútbol
Modelo de campo y fuera de juego (`engine/pitch.py`), formato de jugada `FB-PLAY` (`engine/schema/`), validador de
jugadas (`engine/playcheck.py`), biblioteca táctica (`tactical-library/`), configuración y marca de fútbol
(`config/`), adaptador de portadas con el logo 2026 (`scripts/fb_cover.py`), CLI (`scripts/fb.py`) y QC de
aislamiento (`qa/`).

## 5. Cómo está organizada
```
football/
├── README.md, CHANGELOG.md        este documento y la lista de cambios propia
├── config/                        division.json (ids, rutas, fase) · brand.json · publishing.json · shared-engine.json
├── assets/brand/                  logo 2026 (blanco y navy) + procedencia
├── engine/                        pitch.py · playcheck.py · schema/fb-play.schema.json · README (módulos de la fase 2)
├── tactical-library/              formations.json · concepts.json · plays/FB-PLAY-*.json
├── scripts/                       fb.py (CLI) · fb_lib.py · fb_cover.py (adaptador)
├── qa/                            check_isolation.py · baseline.json · tests/
└── documentation/                 ARQUITECTURA · AGENTE · PRODUCCION · AISLAMIENTO
```
Las carpetas del esquema del propietario que aún no tienen contenido (`scenes/`, `animations/`, `compositions/`,
`skills/`) no se crean vacías: están descritas en `engine/README.md` y aparecerán en la fase que las use.
`renders/`, `thumbnails/` y `analytics/` viven por producción en la carpeta del proyecto (punto 7).

## 6. Cómo iniciar una nueva producción
```bash
python3 football/scripts/fb.py new-production "third man run"     # crea FB-AAAAMMDD-third-man-run
```
Pasos completos en [documentation/PRODUCCION.md](documentation/PRODUCCION.md).

### Render 3D (fase 2)
Motor y comandos en [remotion/README.md](remotion/README.md). Primer vídeo: `FB-20261123-third-man-run`.

### Set Pieces Studio (balón parado)
1. Diseña la jugada como **spec** con waypoints (posición + velocidad) en `tactical-library/setpieces/FB-SETPIECE-nnn.spec.json`.
2. `python3 football/scripts/fb_motion.py build <spec> tactical-library/plays/<play>.json` construye las trayectorias
   (curvas de mínimo tirón) y valida reglas (Ley 17, 9,15 m, doble toque, fuera de juego, carril de pase) y física.
3. `node football/qa/qc_play_motion.mjs <play>.json` revisa el balón y los cuerpos con el motor real (sin render).
4. Episodio en `remotion/src/episodes/`, composición `FBSetPiece<nnn>` en `Root.tsx`, fotogramas con `out/stills.mjs`.
5. QC del vídeo con `qa/qc_render.py --duration 20-25` y la lista `qa/SETPIECE-QC-CHECKLIST.md`.
6. Registra lo aprendido en `tactical-library/setpieces/LEARNING-LOG.md` (capacidades, errores, arreglos, límites,
   requisitos del siguiente vídeo) y la ficha educativa `FB-SETPIECE-nnn.json`.

## 7. Dónde se guardan los vídeos
`/mnt/project-files/football/productions/FB-AAAAMMDD-<slug>/` con `script/ voice/ scenes/ renders/ thumbnails/ qa/
analytics/` y `production.json`. Nunca en Git ni en carpetas de baloncesto. Cada archivo generado lleva un id `FB-`.

## 8. Cómo comprobar errores
```bash
python3 football/qa/check_isolation.py                 # baloncesto intacto + reglas de fútbol
python3 -m unittest discover -s football/qa/tests      # pruebas de fútbol (sin red ni créditos)
python3 football/scripts/fb.py shared verify           # piezas compartidas iguales a lo registrado
python3 football/scripts/fb.py check-play <jugada.json> # jugada válida (campo, velocidades, fuera de juego)
python3 football/qa/qc_render.py <video.mp4>           # QC del MP4: formato, 30 fps, duración, -14 LUFS, negros, saltos
```

## 9. Cómo mejorar el sistema
Cambios solo dentro de `football/`, en una rama `claude/football-*`, con entrada en `CHANGELOG.md` y las
comprobaciones del punto 8 en verde. Para usar una pieza compartida nueva, añádela a `config/shared-engine.json`
(categoría, commit, huella) en vez de copiarla.

## 10. Cómo mantenerlo separado de Basketball
Reglas y mecanismos en [documentation/AISLAMIENTO.md](documentation/AISLAMIENTO.md): ids `FB-`, lista de rutas
prohibidas en `config/division.json`, registro del motor compartido con huellas, publicación desactivada y
`qa/check_isolation.py` antes de cada entrega.
