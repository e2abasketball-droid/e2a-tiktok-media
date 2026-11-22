# Cambios de E2A Football
Historial propio de la división Football (independiente del de Basketball). La más reciente arriba.

## 2026-11-22 — Fase 1: arquitectura, aislamiento y agente
- Nueva carpeta `football/` y agente `e2a-football-director` (aprobación del propietario 2026-11-22 20:52 UTC).
- Configuración propia: ids `FB-`, rutas, marca (paleta oficial + logo 2026), publicación **desactivada** (YouTube en el
  canal E2A Sports con catálogo `FB` propio, preparado y apagado; Instagram y TikTok preparados y apagados).
- Registro del motor compartido (23 piezas A/B/C + 4 servicios) con commit y huella; acceso en lectura con caché.
- Motor de fútbol, base: modelo de campo y fuera de juego, formato `FB-PLAY`, validador, 4 formaciones,
  10 conceptos, 1 jugada de ejemplo (ficticia).
- Adaptador de portadas con el logo 2026; CLI `fb.py`; QC de aislamiento y 18 pruebas.
- Base de comparación: `main` b3f0321 (292 archivos). Ningún archivo de baloncesto modificado.
