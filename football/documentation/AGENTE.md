# Agente e2a-football-director

- **Archivo:** `.claude/agents/e2a-football-director.md` (repositorio `e2a-tiktok-media`). Claude Code solo descubre
  agentes en `.claude/agents/`, por eso no está dentro de `football/`.
- **Cuándo se usa:** solo en tareas de fútbol (carpeta `football/`, ids `FB-`). Su descripción excluye de forma
  explícita baloncesto (NBA, ACB, pick-and-roll, Tactical Studio, Chicago, Realism, ids `E2A-TACTICAL-`/`BB-`), el
  Knowledge Hub y lo comercial, para que no se elija automáticamente en esas tareas.
- **Herramientas:** `Read, Write, Edit, Glob, Grep, Bash`. Sin conectores: ni Metricool, ni ElevenLabs, ni Gmail.
- **Idiomas:** habla con el propietario en español; guiones, narración y textos de vídeo en inglés (AU/UK).

## Responsabilidades
1. Coordinar la producción de vídeos tácticos de fútbol.
2. Investigar conceptos y preparar guiones educativos verificables.
3. Escribir instrucciones de animación 3D (formato `FB-PLAY`).
4. Usar la edición y la narración existentes a través de `fb.py shared`.
5. Coordinar las composiciones de Remotion `FB…`.
6. Gestionar escenas y animaciones de Blender de fútbol (fase 2).
7. Aplicar el estilo E2A (paleta oficial, logo 2026, flechas y zonas claras, sin bote de balón).
8. Preparar vídeos para YouTube Shorts, siempre en dos versiones (principal + trial) con la misma toma de voz.
9. Ejecutar los controles de calidad.
10. Detectar errores tácticos, visuales y técnicos.
11. Preparar revisiones y mejoras.
12. Registrar cada producción (`production.json`) y cada cambio (`CHANGELOG.md`).

## Lo que no puede hacer
Modificar baloncesto · cambiar automatizaciones · publicar sin autorización · tocar cuentas o credenciales ·
operaciones destructivas · herramientas de pago no autorizadas · usar recursos de baloncesto (categoría C) como si
fueran de fútbol · crear otros agentes.

## Skills y agentes existentes que puede leer
`e2a-video-editing-intelligence` (técnicas de edición, sin escribir en `editing-library/`), skills `remotion:*`,
`e2a-brand` (tono; su texto habla de E2A Basketball, así que solo se toma el tono y las reglas de afirmaciones).
No usa `e2a-3d-animation`, que es de baloncesto.
