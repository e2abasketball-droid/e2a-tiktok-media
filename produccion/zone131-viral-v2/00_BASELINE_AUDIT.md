# 00 · Auditoría de partida — 1-3-1 Zone V2 (2026-11-23)

## Punto de partida
- Repo `e2a-tiktok-media`, rama `claude/project-thread-yalqgn`, commit de partida **acfc096** (V1 entregada; sin merge, sin publicar).
  La rama que pedía el brief (`claude/e2a-zone131-viral-v2`) no se crea: esta sesión solo puede empujar a `claude/project-thread-yalqgn`. La V2 vive en archivos propios (`_gen-zone131-v2.py`, `zone131v2/`, esta carpeta) y no toca la V1.
- Vídeo de referencia que se mejora: `tactical-studio/zona-1-3-1/E2A-ZONE-131-TRIAL.mp4`: 42,944 s, 1080×1920, 30 fps, H.264 + AAC 48 kHz estéreo, 3,6 Mb/s. Es la variante trial del master V1 (zoom 3 %, grade y EQ); el montaje es el mismo.
- Referencias de serie abiertas: `zona-2-3/E2A-2-3-Zone-MASTER.mp4` y `horns/entrega-final/E2A-HORNS-ROLL-POP-FINAL.mp4` (también `entrega-v2`).
- Fuente editable real:
  - Montaje V1: `template/tactical/episodes/_gen-zone131.py` (13 planos)
  - Jugadas: `template/tactical/plays/zone131-{a-corner-trap,b-skip-corner,c-early-closeout}.json`, generadas por `tactical/specs/_gen-zone131.py`
  - Composición Remotion: `Tactical3DV2`
- Render: atletas **v33** (Realism V3.3 por props; el default global Legacy no se toca), entorno `cinema`, overlays de cobertura `1-3-1` (`coverage3d.tsx`).
- Audio accesible:
  - Toma única de Deuce aprobada: `public/tactical/zone131/voice-raw.mp3` (599 créditos ya gastados, con timings de palabra de Scribe)
  - Música interna `music/e2a_music.py` (`cine_b`, sin samples ni botes)
  - No hay más locución.

## Cortes de la V1 (s)
hook 0 · gamble 2,61 · shape 5,29 · corner 9,57 · trap 12,06 · rot 14,29 · reset 19,64 · skip 20,97 · first 25,41 · sprint 27,54 · three 30,20 · ontime 33,07 · close 37,74 · fin 42,94.

## Verificación de los 9 puntos del brief (sobre el MP4 exportado, no sobre el preview)
| # | Punto | Lo que se ve en el MP4 V1 | Estado |
|---|---|---|---|
| 1 | Hook 0–3 s | Formación congelada (A 0) con X4 pulsando y una ruta dibujada; nadie se mueve hasta 9,6 s | Confirmado |
| 2 | Formación / zonas 3–10 s | gamble + shape: 6,9 s de pista quieta antes del primer pase | Confirmado |
| 3 | Jugadores pequeños | Cámara MAIN a 24,75 m; la cancha usa ~50 % del alto. El encuadre está limitado por el **ancho** (las dos esquinas tocan los bordes) | Confirmado; solo se puede acercar ~6 % sin perder esquinas |
| 4 | Trap 12–19 s | Trap con freeze + ELBOW / PAINT / WEAK BLOCK: 7,6 s | Confirmado (demasiado largo) |
| 5 | NEW POSSESSION 19,6–21 s | Plano propio de 1,3 s con la jugada congelada | Confirmado |
| 6 | Skip / X3 / X4 24–30 s | Bien resuelto pero con dos rutas y tres etiquetas | Mejorable |
| 7 | Cambio de eje 30–37 s | La cámara THREE apunta a la esquina derecha y el aro queda **a la izquierda** de la imagen; LATE y ON TIME se ven en dos planos distintos, uno detrás del otro | Confirmado |
| 8 | Título "DECIDE" ~38 s | **No existe ningún texto "DECIDE"** en la V1. En 37,0–42,9 s hay dos títulos seguidos: "PRESSURE. / RECOVERY." y "TRAP OR / RECOVER?". Revisados fotograma a fotograma (1110–1288): cada línea entra deslizándose dentro de una máscara que la recorta, así que durante ~6 fotogramas por título solo se ven medias letras (p. ej. "RFCOVFRY" a 38,2 s y 40,6 s). Visto a velocidad normal en móvil, ese recorte y el cambio RECOVERY → RECOVER? se leen como letras deformadas o duplicadas | Defecto real (otra palabra, misma causa) → **arreglado** |
| 9 | Cierre 38–42,9 s | Resumen + 2 títulos + logo: 5,2 s, redundante | Confirmado |

## Plan
1. Título: nuevo modo `reveal: "block"` en `KineticTitle` (sin máscara, el bloque entra con fade + 18 px). Por defecto no cambia nada para los demás episodios.
2. Voz: remontar la toma aprobada con un editor nuevo (`scripts/tactical-voice-edit.py`): solo frases enteras cortadas en silencios acústicos, sin síntesis ni time-stretch. 0 créditos.
3. Montaje V2 (`_gen-zone131-v2.py`):
   - cold open sobre el skip en el aire (hook A) o sobre el trap (hook B)
   - 1/3/1 en 4 s
   - reset y skip en un solo plano (NEW POSSESSION 0,6 s)
   - X3 FIRST y X4 TAKEOVER
   - payoff LATE / ON TIME en pantalla partida sincronizada, misma cámara con la canasta arriba y mismo reloj
   - cierre que vuelve al primer fotograma
4. Render, revisión del MP4 real, correcciones y documentación.
