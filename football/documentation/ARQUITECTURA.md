# Arquitectura de E2A Football

E2A Sports = **motor compartido** (tecnología general) + **divisiones** (Basketball, Football). Football usa el motor
compartido sin cambiarlo y añade solo lo que es de fútbol.

```
E2A SPORTS
├── SHARED ENGINE  (código existente del repo, NO se mueve ni se renombra)
│   ├── Narration ........ template/scripts/tactical-voice.py · ElevenLabs (Deuce)
│   ├── Video Editing .... template/src/pro/* · validate-episode.mjs · trial-variant.sh · pcd.py
│   ├── Subtitles ........ template/src/pro/subtitles.tsx
│   ├── Motion Graphics .. template/src/pro/graphics.tsx · fx.tsx · camera.tsx
│   ├── Audio ............ tactical-music-bed.py · music/ (biblioteca con licencia) · audio-stems.py
│   ├── Rendering ........ Remotion 4.0.539 + three 0.180 (template/package-lock.json)
│   ├── Branding ......... fuentes Anton/Inter · make_cover.py · logo 2026
│   └── Quality Control .. qc-pro.mjs · qc-video.py · qc-bounds.mts
├── BASKETBALL     (sistema existente: template/, tools/, config/, produccion/, ramas tactical-media, studio-state…)
└── FOOTBALL       (football/ + .claude/agents/e2a-football-director.md + /mnt/project-files/football/)
```

## Motor compartido

- **A** = se usa directamente con rutas de fútbol, sin riesgo para baloncesto.
- **B** = se usa mediante un adaptador o una configuración propia de fútbol (nunca editando el archivo de baloncesto).
- **C** = específico de baloncesto: football no lo usa (`fb.py shared resolve` lo rechaza).

Cada pieza está fijada a un commit y a la huella (blob) de su archivo. `fb.py shared verify` avisa si cambia.

| Cat. | Componente | Área | Dónde vive | Cómo lo usa Football |
| --- | --- | --- | --- | --- |
| A | `research.commons` | Assets | `template/scripts/fetch-commons.mjs` (main) | Directo, con rutas de fútbol |
| A | `audio.music-bed` | Audio | `template/scripts/tactical-music-bed.py` (main) | Directo, con rutas de fútbol |
| A | `audio.music-library` | Audio | `music/library.json` (main) | Directo, con rutas de fútbol |
| A | `branding.fonts` | Branding | `template/public/anton.woff2` (main) | Directo, con rutas de fútbol |
| A | `narration.voice-splice` | Narration | `template/scripts/tactical-voice.py` (main) | fb.py shared resolve narration.voice-splice; run with cwd=<production>/voice |
| A | `qc.video-pro` | Quality Control | `template/scripts/qc-pro.mjs` (main) | Directo, con rutas de fútbol |
| A | `qc.video-real` | Quality Control | `template/scripts/qc-video.py` (claude/realism-v3-1) | resolve from claude/realism-v3-1; episode argument must be an FB episode |
| A | `rendering.remotion-stack` | Rendering | `template/package-lock.json` (main) | football package.json pins same versions |
| A | `editing.episode-validator` | Video Editing | `template/scripts/validate-episode.mjs` (main) | Directo, con rutas de fútbol |
| A | `editing.reference-library` | Video Editing | `.claude/skills/e2a-video-editing-intelligence/SKILL.md` (main) | Directo, con rutas de fútbol |
| A | `research.pcd` | Video Editing | `tools/pcd.py` (claude/realism-v3-1) | resolve from claude/realism-v3-1; FB sheets live in the FB production dir |
| A | `trial.variant` | Video Editing | `template/scripts/trial-variant.sh` (claude/realism-v3-1) | resolve from claude/realism-v3-1 |
| B | `audio.stems-report` | Audio | `template/scripts/audio-stems.py` (main) | football adapter needed (media root + FB timeline) |
| B | `thumbnails.cover` | Branding | `tools/make_cover.py` (claude/project-thread-9ybhcw) | football/scripts/fb_cover.py (phase 2) passes the 2026 logo |
| B | `publishing.metricool-publisher` | Publishing | `tools/tactical_publisher.py` (main) | own FB publisher config and delegation (later phase, owner approval) |
| B | `qc.bounds` | Quality Control | `template/scripts/qc-bounds.mts` (main) | football composition probe |
| B | `rendering.pro-script` | Rendering | `template/scripts/render-pro.sh` (main) | football render wrapper (phase 2) |
| B | `editing.pro-engine` | Video Editing / Subtitles / Motion Graphics | `template/src/pro/Pro.tsx` (main) | FB Remotion entry imports template/src/pro/* read-only |
| C | `bb.tactical3d` | 3D | `template/src/t3d/Court3D.tsx` (main) | No se usa |
| C | `bb.tactical2d` | Motion Graphics | `template/src/tactical/Court.tsx` (main) | No se usa |
| C | `bb.config` | Publishing | `config/tactical_studio.json` (main) | No se usa |
| C | `bb.studio` | Publishing | `tools/tactical_studio.py` (main) | No se usa |
| C | `state.studio-sync` | Publishing | `tools/studio_sync.py` (main) | No se usa |
| A | `svc.elevenlabs` | Narration | ElevenLabs connector, voice Deuce (DaueUomjhh8LFuAV8aGj), Creator plan commercial licence | one take per video, written approval per video, never regenerate |
| B | `svc.metricool` | Publishing | Metricool brand 7681319 (includes the E2A Sports YouTube channel) | disabled for football in phase 1; own queue, catalogue and delegation before any write |
| B | `svc.blender` | 3D | Blender/MPFB tooling (tools/blender/* on branches claude/e2a-3d-next, claude/realism-v3-1); bpy via pip venv; no Blender binary in the container | body/garment pipeline reusable; football kit and motions are new (phase 2) |
| A | `svc.remotion-skills` | Rendering | Claude Code Remotion skills (remotion:*) | read-only guidance |

### Por qué no se copia el motor
El propietario pidió compartir la tecnología sin mantener dos versiones. Por eso football **no copia** código del
motor: lo ejecuta en su sitio (piezas de `main`) o desde una caché fuera de Git sacada con `git show <commit>:<ruta>`
(piezas que solo existen en ramas sin fusionar: `qc-video.py`, `trial-variant.sh`, `pcd.py` de
`claude/realism-v3-1` y `make_cover.py` de `claude/project-thread-9ybhcw`). Cuando esas ramas se fusionen, basta con
actualizar el commit fijado en el registro.

## Motor de fútbol (lo nuevo)
Ver [`../engine/README.md`](../engine/README.md): entorno 3D, personajes, inteligencia táctica y efectos visuales,
con lo que ya existe en la fase 1 (modelo de campo, fuera de juego, formato de jugada y validador) y lo que llega en la
fase 2.

## Identificadores
| Qué | Formato | Ejemplo |
| --- | --- | --- |
| Producción | `FB-AAAAMMDD-<slug>` | `FB-20261123-third-man-run` |
| Contenido publicado | `FB-TACTICAL-AAAAMMDD-Vnn` | `FB-TACTICAL-20261123-V01` |
| Jugada | `FB-PLAY-<slug>` | `FB-PLAY-third-man-run` |
| Concepto | `FB-Cnn` | `FB-C01` |
| Composición Remotion | prefijo `FB` | `FBTactical3D`, `FBPro` |

Baloncesto conserva sus ids actuales (`E2A-TACTICAL-…`); `BB-` es solo la etiqueta que usa football para referirse a
él. Renombrar ids de baloncesto requiere aprobación del propietario.
