# Cambios de E2A Football
Historial propio de la división Football (independiente del de Basketball). La más reciente arriba.

## 2026-11-23 — Fase 2: motor 3D de fútbol y piloto «The Third-Man Run» (VIDEO 001)
- Aprobación del propietario (23-nov, 00:27 Madrid): desarrollo audiovisual local y renders de prueba solo dentro de
  Football. **No** aprobado: publicar, fusionar, tocar Basketball, servicios de pago.
- Rama nueva `claude/football-phase2-third-man-run` derivada de la Fase 1 (`a73af5f`, PR #15 intacto y sin fusionar).
- Entrada Remotion propia `football/remotion/` (FBTactical3D): campo 105×68, porterías con red deformable, gradas y
  focos con sombras; futbolista articulado con zancada ligada a la distancia, golpeo y estirada del portero; balón con
  frenada, giro y gol en la red; tres cámaras (overview, tracking, detail); gráficos sobre el césped y capa 2D Shorts.
  Mismas versiones exactas que baloncesto (comprobado), sin importar nada de `template/`.
- Jugada `FB-PLAY-third-man-run` v2 (3 s de construcción, el central salta con el 9, el mediocentro mira el balón,
  el tercer hombre llega en juego por detrás de la línea).
- `fb_stage.py` (fuentes del motor compartido + logo 2026 a `remotion/public/`, ignorado), `fb_words.py` (tiempos de
  subtítulos), `qa/qc_render.py` (QC del MP4), 8 pruebas nuevas (26 en total); `check_isolation.py` admite solo el
  manifiesto propio de Remotion y exige versiones idénticas a baloncesto.
- Producción `FB-20261123-third-man-run`: V01 muda, V02 con música propia E2A (síntesis), versión trial y portadas.
  0 créditos de ElevenLabs. Nada publicado.

## 2026-11-22 — Fase 1: arquitectura, aislamiento y agente
- Nueva carpeta `football/` y agente `e2a-football-director` (aprobación del propietario 2026-11-22 20:52 UTC).
- Configuración propia: ids `FB-`, rutas, marca (paleta oficial + logo 2026), publicación **desactivada** (YouTube en el
  canal E2A Sports con catálogo `FB` propio, preparado y apagado; Instagram y TikTok preparados y apagados).
- Registro del motor compartido (23 piezas A/B/C + 4 servicios) con commit y huella; acceso en lectura con caché.
- Motor de fútbol, base: modelo de campo y fuera de juego, formato `FB-PLAY`, validador, 4 formaciones,
  10 conceptos, 1 jugada de ejemplo (ficticia).
- Adaptador de portadas con el logo 2026; CLI `fb.py`; QC de aislamiento y 18 pruebas.
- Base de comparación: `main` b3f0321 (292 archivos). Ningún archivo de baloncesto modificado.
