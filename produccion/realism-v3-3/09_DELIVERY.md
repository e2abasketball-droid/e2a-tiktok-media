# Realism V3.3 — 09 ENTREGA y GO/NO-GO

**Rama:** `claude/realism-v3-3` (desde `claude/realism-v3-2` @ 28b06ea). Sin merge, sin PR, sin publicar.
**Motor por defecto:** `legacy` (sin cambios). V3.1 y V3.2 se conservan y dan píxeles idénticos (07).
**Coste:** 0 €. Sin ElevenLabs ni servicios de pago. Los vídeos son mudos (sin sonido de bote).

## Vídeos renderizados (1080×1920, 30 fps, H.264, mudos)
Carpeta: `/mnt/project-files/tactical-studio/realism-v3-3/videos/` (las hojas de contacto están en `contact-sheets/`).

| # | Archivo | Qué muestra | Duración | Tiempo de render |
|---|---|---|---|---|
| 01 | `01_contact_v32_vs_v33.mp4` | One-take, V3.2 arriba y V3.3 abajo, misma cámara | 12,5 s | 694 s |
| 02 | `02_contact_debug_v33.mp4` | V3.3 con esferas de contacto y apoyos de pie | 12,5 s | 642 s |
| 03 | `03_motion_only_v32_vs_v33.mp4` | Solo movimiento (material gris), V3.2 frente a V3.3 | 12,5 s | 632 s |
| 04 | `04_motion_slowmo_v33.mp4` | V3.3 a 0,5×, recepción, tiro y caída | 10,2 s | 541 s |
| 05 | — | **No hay vídeo de tela L2**: el experimento no se integra (ver 04) | — | — |
| 06 | `06_trio_v33.mp4` | Trío O1/O2/X2 en V3.3 | 7,5 s | 336 s |
| 07 | `07_fullcourt_v33_raw.mp4` | 5v5 completo, 10/10 compilados V3.3, sin gráficos | 11,0 s | 736 s |
| 08 | `08_fullcourt_v33_editorial.mp4` | El mismo 5v5 con título, rótulos y logo 2026 | 11,0 s | 655 s |
| 09 | `09_benchmark_10players_v33.mp4` | Benchmark de 10 jugadores, 2 s | 2,0 s | 158 s |

## Resultados medidos (detalle en 02, 03 y 05)

| Prueba | Antes | V3.3 |
|---|---|---|
| One-take: filas de QC | 27 (V3.2) | 2 |
| One-take: muestras balón-cuerpo | 86 | **0** |
| Trío: filas de QC | 23 | 5 (solo cabeza) |
| Trío: muestras balón-cuerpo | 60 | **0** |
| 5v5: filas de QC | 899 (motor legacy) | 20 |
| 5v5: muestras balón-cuerpo | — | **0** |
| 5v5: deslizamiento de pie máximo | 55,7 cm | 1,4 cm |
| 5v5: cobertura | — | 10/10 V3.3 compilados |
| Determinismo (3 escenas, órdenes y cachés distintos) | — | bit a bit idéntico |
| Regresión Legacy / V3.1 / V3.2 | — | píxeles idénticos |

## Lo que sigue mal (sin esconder)
- **P1, movimiento:**
  - O2 tiene una sacudida de cabeza de 1 frame al despegar en el triple rápido (6,2 s del 5v5). La causa no está cerrada.
  - Hay tirones de cadera y cabeza al arrancar desde parado: O1 a 9,07 s, X4 a 1,57 s, y O5 y X2 por debajo de las filas.
- **P1, manos:** la muñeca va demasiado rápida al soltar el hand-off de O1 y en la suelta del triple rápido de O2.
- **P2:**
  - Antebrazos que rozan el balón, como mucho 2,1 cm.
  - Codo de X2 en el contest.
  - Perfil corporal por dorsal, no por papel.
- **Ropa:** sigue la de V3.2. Los bajos del pantalón se ven dentados en los primeros planos de 04. La tela L2 es experimental y no se integra: estiramiento máximo 3,58, pico del bajo 21,5 cm.
- **Encuadre de 04:** en la cumbre del salto, la cámara lenta corta la cabeza del jugador. Es un problema de cámara del vídeo de prueba, no del motor, y no se ha corregido para no retrasar la entrega.
- **Tamaño en el 5v5:** con la cámara de pista completa, los jugadores se ven pequeños en el móvil. Para un Reel hará falta un encuadre más cerrado.
- **Licencias:** la clave `3d/e2a-player-makehuman-cc0` sigue fuera de `config/asset_licences.json`, igual que en V3–V3.2.

## GO / NO-GO para el primer Reel piloto con V3.3
**GO CONDICIONADO, solo como piloto para revisión interna. No es un GO para publicar ni para cambiar el motor por defecto.**

**Motivos del GO:**
- El problema P0 del brief, el balón atravesando cuerpos, está a 0 muestras en las tres escenas.
- El 5v5 entero sale del compilador sin guiones a mano y sin caer al motor legacy.
- Es determinista y no rompe nada de lo anterior.

**Condiciones:**
1. Usar `athleteRenderer: "v33"` solo en las props de ese piloto. Legacy sigue siendo el valor por defecto.
2. La jugada solo puede usar primitivas soportadas: bote, pase, hand-off, recepción, tiro en suspensión o rápido, bloqueo, defensa y carrera. No hay bandeja.
3. Encuadre más cerrado que el 07/08 para que los jugadores se lean en el móvil.
4. Antes de publicar, el propietario revisa en particular el triple rápido (cabeza de O2) y los arranques desde parado.
5. Mantener el registro QC (`qc-realism-v33.mts`) en el piloto y no relajar umbrales.

**NO-GO para:**
- cambiar el motor por defecto;
- usar la tela L2;
- publicar sin revisión humana.
