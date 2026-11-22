# Cómo iniciar una producción de fútbol

> En la fase 1 solo existe la infraestructura. Los pasos 4–7 necesitan el motor de la fase 2 y la aprobación del
> propietario (voz = créditos de ElevenLabs).

1. **Crear la carpeta:** `python3 football/scripts/fb.py new-production "<tema>"` →
   `/mnt/project-files/football/productions/FB-AAAAMMDD-<slug>/` (nunca sobrescribe una existente).
2. **Concepto y gancho:** elegir un `FB-Cnn` de `tactical-library/concepts.json`; rellenar la ficha PCD del gancho
   (`fb.py shared resolve research.pcd`, ficha guardada en `script/`).
3. **Jugada:** escribir `tactical-library/plays/FB-PLAY-<slug>.json` y validarla con `fb.py check-play`.
4. **Guion y voz:** guion en inglés en `script/`; **una** toma de Deuce tras aprobación por vídeo; pausas con
   `narration.voice-splice` ejecutado con la carpeta `voice/` como directorio de trabajo.
5. **Música:** `audio.music-bed` con una pista de `music/cinematic/` (registrar la elección en `production.json`, no en
   `music/history.json`). Sin bote de balón ni efectos por defecto.
6. **Render:** composición `FB…` (fase 2) → `renders/FB-…-main.mp4`; versión trial con `trial.variant` →
   `renders/FB-…-trial.mp4`.
7. **Portada y QC:** `fb_cover.py` → `thumbnails/FB-…-cover.jpg` (logo 2026); `qc.video-pro` / `qc.video-real`
   → `qa/`; `qa/check_isolation.py`.
8. **Entrega:** informe en `qa/` y revisión del propietario. Publicar está desactivado (`config/publishing.json`).

## Dónde queda cada cosa
| Qué | Dónde |
| --- | --- |
| Datos reutilizables (jugadas, formaciones, conceptos) | `football/tactical-library/` (Git) |
| Guion, voz, renders, portadas, QC, métricas de una producción | `/mnt/project-files/football/productions/FB-…/` |
| Caché de piezas compartidas | `football/.cache/` (ignorada por Git) |
| Cola y registro de publicación futuros | `/mnt/project-files/football/queue.json`, `publications.jsonl` (aún no existen) |
