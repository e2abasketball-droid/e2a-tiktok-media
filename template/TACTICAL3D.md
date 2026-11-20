# Tactical3D — motor 3D real para episodios tácticos (Episodio 02: Stagger Screen)

Composición Remotion `Tactical3D` (1080×1920, 30 fps). Escena three.js real (`@remotion/three`):
jugadores con volumen, sombras, luz de pabellón y cámaras que se mueven en 3D. El motor 2.5D
(`src/tactical/`, composición `Tactical`) sigue intacto; este motor reutiliza sus jugadas
(`tactical/plays/*.json`), su resolución de anclas por palabra y sus remaps de tiempo.

## Piezas (todas dirigidas por datos)

| Archivo | Qué hace |
|---|---|
| `src/t3d/rig.ts` | Atleta procedural: simulación de pasos a 120 Hz (cada pie está **plantado** o en vuelo hacia su siguiente apoyo, así que un pie apoyado no puede deslizar), IK de dos huesos en piernas y brazos, inclinación, giro de hombros y acciones mezcladas (screen, stance, topLock, catchReady, shoot, layup, pass, dribble, contest, seal, celebrate). `footTrack()` expone los pies para el QC. |
| `src/t3d/Athlete.tsx` | Malla del jugador: extremidades torneadas con tapas, torso en V con camiseta (número delante y detrás), pantalón, calcetines, zapatillas, cabeza esculpida sin cara, piel MeshPhysical. Equipaciones: ataque azul marino con dorado, defensa blanca con granate. 10 tonos de piel. |
| `src/t3d/Court3D.tsx` | Parqué procedural (tablas, veta, mapa de rugosidad), líneas FIBA, zona azul marino, logo central, canasta completa con red que reacciona al enceste, gradas con público tenue, techo con focos, luces (foco principal con sombras suaves, relleno y contraluz). |
| `src/t3d/camera3d.ts` | Cámaras `orbit` (objetivo fijo o que sigue a jugadores, distancia, inclinación, giro, fov) y `pov` (detrás de un jugador mirando a otro). Las claves se mezclan en espacio de órbita (distancia logarítmica, giro por el camino corto), sin saltos de orientación. |
| `src/t3d/overlays3d.tsx` | Gráficos dentro de la escena 3D: anillo, ruta (trazo progresivo), bloqueo (panel dorado + barra), línea de pase (`src`→`dst`), separación, espacio libre, negación (cuña roja), bloqueado (X roja). |
| `src/t3d/screen3d.tsx` | Gráficos de pantalla: titular cinético, sello con placa azul marino y borde dorado, etiqueta anclada a un jugador proyectado desde 3D, congelación con esquinas doradas, rebobinado, logo y subtítulos premium palabra a palabra. |
| `src/brand.ts` | Logo oficial único para todas las composiciones (Tactical3D, suelo del Court3D, Probe/Course3D, Tactical 2D, Pro): `LOGO = 'brand/e2a-logo-2026.png'` (logo 2026 E2A Sports Academy, recorte transparente de la JPEG del propietario con `tools/brand/cutout_logo.py`, procedencia en `public/brand/e2a-logo-2026.png.provenance.json`). El antiguo `public/e2a_logo_white.png` queda retirado: un cambio de marca = una línea. |
| `src/t3d/Tactical3D.tsx` | Composición: planos anclados a palabras de la locución real, remaps (velocidad real, cámara lenta, congelación, rebobinado), cámaras, gráficos, voz, música y efectos. |
| `tactical/episodes/stagger-screen.json` | El episodio entero como datos: 9 planos, huecos acústicos de la voz, palabras clave, música. |

## Comandos

```bash
cd template
node --experimental-strip-types scripts/test-stagger.mts tactical/plays/stagger-*.json        # QC táctico (65 checks)
node --experimental-strip-types scripts/qc-tactical3d.mts tactical/episodes/stagger-screen.json  # QC del motor (9 checks)
node --experimental-strip-types scripts/storyboard-tactical3d.mts tactical/episodes/stagger-screen.json  # línea de tiempo real
python3 scripts/tactical-voice.py tactical/episodes/stagger-screen.json   # huecos acústicos + palabras (sin créditos)
npx remotion render src/index.ts Tactical3D out/stagger.mp4 --gl=swangle \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --concurrency=4
```

`--gl=angle` no crea contexto WebGL en el contenedor; usar `swangle`. Borrador rápido: `--scale=0.5`.
La composición `Probe3D` sirve para probar jugadores y cámaras sin montar un episodio.

## Reglas del motor

- Todo lo que aparece en pantalla se ancla a una palabra de la locución (`"trails"`, `"for three>+0.25"`, `"@end"`); si cambia la toma, el montaje se recoloca solo y el QC falla si un ancla cae fuera de su plano.
- Los gráficos que apuntan a jugadores (`player`, `a`, `b`, `src`, `dst`) deben existir en la jugada del plano: lo comprueba el QC.
- Cámara: ≤ 0,9 m de desplazamiento por fotograma dentro de un plano y nunca por debajo de 0,8 m.
- Jugadores resaltados dentro de la zona segura (x 60–1020, y 230–1560).
- Rojo solo para la defensa; resto en azul marino, dorado y blanco.

## Jugadores por defecto: paquete `e2a-player-v1` (2026-11-19)

Todo `Tactical3D`/`Tactical3DV2` dibuja ahora a los jugadores con el personaje deformable de E2A (base MakeHuman CC0
construida con `tools/blender/build_player.py`), sin campos nuevos en el episodio:

| Pieza | Archivo |
|---|---|
| Mallas (ataque / defensa) | `public/players3d/e2a_player_{off,def}.glb` (+ `.provenance.json`) |
| Esqueleto para el motor | `src/t3d/players/e2a-{off,def}.rig.json` (21 huesos, metros, z arriba, reposo mirando a −y) |
| Elección por jugador | `src/t3d/player3d.ts` (`planPlayers3d`, `CLIP_LIBRARY`): clip validado por patrón de acciones si la geometría encaja; si no, rig procedural o `choreo` re-resuelto sobre la malla |
| Pose → huesos | `src/t3d/skelclip.ts` `bonesFromPose` + `meshScale` (escala por longitud de pierna; piernas y brazos re-resueltos desde las caderas y hombros de la malla; cabeza por mirada) |
| Dibujo | `src/t3d/SkinnedAthlete.tsx` (un clon con su esqueleto por jugador, piel y dorsal por jugador), `Scene.tsx` |
| Clips y registro | `src/t3d/clips/*.json`, `src/t3d/clips/registry.json` |
| QC | `scripts/qc-players3d.mts <play>`, sección `players3d` de `qc-tactical3d`, `scripts/players3d-plan.mts <ep|play>` |

- Volver al aspecto anterior (comparativas, episodios antiguos): `"players3d": "A"` en el episodio o en un plano.
- Episodios con `faces`: siguen en cápsula (la malla tiene cara neutra); se registra el motivo.
- Si un `.glb` no carga: cápsulas y `FALLBACK` en el registro del render (no se cancela el render).
- `autoSfx`: botes, recepciones y caídas a 0 por defecto (regla de cero sonido de bote).


## Telestración broadcast (2026-11-19, `src/t3d/telestration3d.tsx` + `screen3d.tsx`)
Todo es función pura de (jugada, tiempo de jugada, edad): buscar = reproducir; congelaciones y rebobinados los arrastran.
| Concepto del encargo | Tipo en el episodio | Dónde |
|---|---|---|
| PlayerSpotlight | ov3 `spot` (halo + cono de luz que sigue al jugador; `beam:false` solo halo) | telestration3d.tsx |
| ImpactPulse | ov3 `ripple` (dos anillos que se expanden en el contacto) | telestration3d.tsx |
| Floor label / endpoint | ov3 `floorText` (rótulo pintado en el parqué, `yaw` = yaw de la cámara, `plate`) | telestration3d.tsx |
| BallTrail | ov3 `ballTrail` (estela del balón en pases y tiros) | telestration3d.tsx |
| GhostTrail | ov3 `ghostTrail` (posiciones pasadas: discos + columnas translúcidas) | telestration3d.tsx |
| PassWindow que viaja | ov3 `passLane` + `travel` (s) + `dstAt` (tiempo de la recepción) | telestration3d.tsx `PassTravel` |
| FloorRoute que nace bajo el jugador | ov3 `route` + `consume:true` | overlays3d.tsx |
| PlayerRing / ScreenMarker / DecisionZone / DefensiveVector / tether | `ring` / `screen` / `openSpace` / `deny` o `route` roja con `trail` / `separation` | overlays3d.tsx (existentes) |
| PlayerLabel / FreezeCallout / Rewind / títulos / sello | `pin` (pinV2) / `freeze` (+`grade`) / `rewind` / `title` / `stamp` | screen3d.tsx (existentes) |
| Foco en el defensor (resto atenuado) | screen `focus` (FocusVignette) | screen3d.tsx |
| TacticalHUD | screen `hud` (chip «A · HE STAYS») | screen3d.tsx |
| Punch-in / whip / flash | screen `punch`, `whip`, `flash` (capa 3D; `flash` reutiliza `pro/fx.tsx Flash`) | screen3d.tsx `sceneFx`, Tactical3D.tsx |
`qc-tactical3d` trata `spot` con jugador como resaltado (zona segura), igual que `ring`.

## Regla editorial permanente: tipo de contenido → framework (decisión del dueño, 2026-11-19, encargo Spain PnR 2.0)
Antes de escribir guion o planos de CUALQUIER vídeo E2A, identifica primero el tipo de contenido y elige su framework.
No uses siempre el mismo hook ni la misma estructura.

| Tipo | Framework |
|---|---|
| TACTICAL EXPLAINER (jugada con lecturas) | HOOK → MECHANISM → DECISION → PAYOFF → REHOOK (solo si hay segunda lectura; preferiblemente visual: freeze + rewind + «SAME ACTION. DIFFERENT READ.») → SECOND PAYOFF → TAKEAWAY → CTA |
| TECHNIQUE / MISTAKE-FIX / DRILL | PROBLEM / MISTAKE → WHY → CORRECT MOVEMENT → PROOF → TAKEAWAY → CTA |
| STORY | TENSION → PROGRESSION → TURN → PAYOFF → CTA |
| PLAYER BREAKDOWN / CONCEPT / COMPARISON | el más cercano de los anteriores, justificado en una línea en la entrega |

**Regla superior: CLARITY > FRAMEWORK.** Nunca fuerces un framework si empeora la explicación.
Regla de lectura asociada: muchos efectos a lo largo del vídeo, **una sola idea visual principal en cada momento**
(máx. 1 título + subtítulos + 1 etiqueta táctica a la vez); cada gráfico tiene entrada, permanencia y salida.
Referencia aplicada: `template/tactical/episodes/_gen-spain-pnr-2-shots.py` (capa `src/t3d/telestration3d.tsx`).

## Novedades 2026-11-20 (pilotos Slip vs Hedge y Double Drag en transición)
Todo es opcional y se activa por jugada o por episodio. Lo que no lo usa no cambia: las 79 jugadas anteriores dan los mismos jugadores y balón fotograma a fotograma antes y después (comparación con `play-dump`, base 23a2cd8).
- **`"catchV2": 2`** (jugada): recepción por encima del hombro cuando el pase llega desde detrás de la carrera (*slip*, *dive*, puerta atrás). El punto de recepción se desplaza hacia el pasador y deja de atravesar el tronco (qc-catch: de 12,8 cm a 0). `true` mantiene el modelo del 19 nov.
- **`env: 'academy'`** (episodio o plano): look mate y sin brillos (suelo sin mapa de rugosidad, tela con *sheen*, luz frontal de relleno). Sin `env`, el aspecto es el de antes.
- **Inicio lanzado:** un 4.º elemento `"fly"` en el PRIMER punto de un track (`[0, x, y, "fly"]`) hace que el jugador ya vaya lanzado en t = 0. Es para jugadas cuyo reloj empieza en plena transición. Sin la marca, cada tramo sigue empezando y acabando parado.
- **Recogida tras bote con mano** (`hand` / `cross`): el balón pasa de la mano del bote a las dos manos en 0,2 s, por delante del tronco. Antes daba un salto de 0,3 m en un fotograma.
- **Reloj S y anclas del encargo:** `tactical/specs/_gen-ddrag-tr.py` convierte tablas «S → (x, y)» en tracks: x del repo = −x del encargo. Los cambios quedan en `spec.sclock.adjust`.
- **QC:**
  - `qc-contact` mide el bote con la mano que bota (antes, siempre la derecha).
  - `qc-tactical3d` admite un `from` numérico negativo (≥ −1) en el plano inicial: el gancho entra ya visible en el fotograma 0.
- **Herramientas:**
  - `scripts/play-dump.mts`: jugadores, balón y fase a 30 fps.
  - `tools/tactical_2d.py`: pase táctico 2D, MP4 y hoja.
  - `scripts/pose-dump.mts`: articulaciones del rig.
  - `tools/blender/catch_pilot.py`: bpy 5.3; recepción en mallas desde el lateral y a tres cuartos, con distancias balón–tronco y balón–mano medidas en la malla y `--inject behind` para provocar el fallo a propósito.
- **Comparativa controlada:** `_gen-slip-lab.py` y `_gen-ddtr-lab.py` renderizan la misma jugada, cámara y ventana con el perfil anterior y con el nuevo.
- **MPFB 2.0.18:** clonado (assets CC0). No se pudo instalar como extensión de Blender en la sesión (bloqueado por el clasificador de permisos), así que sigue el pipeline CC0 de `tools/blender/build_player.py`.

## Double Drag V2 + método PCD (2026-11-20)
- **Apertura PCD:** ficha `produccion/tactical/pcd/<id>.md` (plantilla `PLANTILLA-PCD.md`, herramienta `tools/pcd.py`), enlazada desde el guion con `PCD: <ruta>`. El gate `script` la valida.
- **Cámaras elegidas con números, no a ojo.** Además de `cam-probe`, el reel V2 usó rejillas de separación proyectada (yaw × pitch × dist) con estos criterios:
  - balón frente al cuerpo de los defensores (caja 0–2 m × 0,3 m);
  - frente del receptor en la recepción (ángulo rumbo–cámara < 90°);
  - aro y receptor dentro del marco seguro;
  - escala del sujeto (X3 ≈ 330 px de alto = 110 px a 360 px de ancho).
  - Los scripts están en `tactical/episodes/_gen-ddtr2.py`, junto a cada cámara.
- **Resultado de tiro protegido:** el plano del tiro se corta con un ancla del remapeo posterior al evento de resultado (balón bajo el plano del aro S166). La V1 cortaba en S157 = la llegada al aro. La jugada se alarga (`duration`) hasta cubrir la red y la caída.
- **Carga de tiro posterior a la recepción:** la acción automática `shoot` empieza 0,5 s antes de `t0`. Con `t0 − 0,5 < t1` del pase, la recepción y la carga se funden. Hay que dejar `t0 ≥ t1 + 0,6`.
- **Suelas y línea de tres:** `tactical/episodes/_control-ddtr2.py` mide toe/ankle de ambos pies contra |x| > 6,60 en la esquina y d > 6,75 en el arco. En la V2 el pie interior de O3 estaba a 6,593 m, sobre la línea, y se corrigió.
- **Regresión «pase por dentro del cuerpo»:** `bash scripts/regress-catch.sh`. El fixture `tactical/regress/regress-pass-through-body.json` debe FALLAR en `qc-catch` (`ball_torso`, X5).

### Corrección pase + audio (2026-11-20)
- **Pase alto «por fases» (opt-in `"phased": true` en un pase `overhead` cargado desde un balón sostenido).**
  - Fases en el marco del pase (pasador → receptor en `t1`): recogida en el marco del cuerpo (rumbo simulado del rig, `setYawHook`), bolsillo del pecho, carga justo sobre la frente (1,81 m, codo ~90°), empuje acelerado y suelta a 2,00 m, 0,42 m hacia el receptor.
  - El vuelo empieza en `phasedRelease()`: la última posición en mano y la primera en vuelo son la misma.
  - Tras la suelta, las manos siguen la línea del pase (follow-through). Las jugadas sin la opción no cambian.
- **Sin el «brazo protector» del bote tras la recogida** (solo en ese pase): ya no hay balón a una mano durante 5 fotogramas.
- **Plano de pase:** empieza en la recogida, mantiene el mismo ángulo hasta la suelta + 6 fotogramas y queda en el mismo lado de la línea que el plano anterior y el siguiente. La estela nace en la suelta y se apaga ≥ 6 fotogramas antes de las manos del receptor.
- **Relleno de voz:** nunca `np.resize()` de un trozo de room tone. Se repite cada 0,217 s y suena como clics. El final de la toma se funde 0,15 s y después va silencio. La música lleva la cola.
- **Regresión «balón dentro de un cuerpo» en la recogida del skip:** `tactical/regress/regress-skip-ball-in-body.json`, con X4 aparcado en el bolsillo de O1. Lo ejecuta `scripts/regress-catch.sh`.
