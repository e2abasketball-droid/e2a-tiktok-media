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
