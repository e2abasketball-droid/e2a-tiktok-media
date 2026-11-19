# E2A 3D — jugador deformable por defecto (fase 4, 2026-11-19)

Rama `claude/lab-mpfb-default-player` (desde `claude/lab-skeletal-screen-roll` + fusión de
`origin/claude/project-thread-5rxcux`). Sin push, sin publicar. Entregables binarios en
`/mnt/project-files/tactical-studio/3d-animation-mpfb/` (fuera de Git).

## 1. Base del jugador C

- **MPFB: no usado.** La sesión no puede descargarlo (403 en las descargas; no hay ZIP en `/mnt/project-files/`
  ni en `uploads/`). Queda preparado `tools/blender/mpfb_player.py`: busca los ZIP por contenido (manifiesto
  `id = "mpfb"`, carpeta `skins/` del pack de assets), registra la extensión en bpy 5.3, crea humano + rig
  GameEngine, guarda/reabre `.blend`, exporta `.glb` y vuelca la malla base a `mpfb_basemesh.npz`. Probado: sale con
  `no zip with blender_manifest.toml id="mpfb"`. Paso que falta: dejar los dos ZIP en la Biblioteca, ejecutarlo y
  pasar el npz a `mh_body.build()` en lugar de las posiciones de ara3d (misma topología hm08; ejes y unidades por
  comprobar sobre el archivo real).
- **C = activo actual refinado (vía 3):** malla base y morphs MakeHuman de ara3d-data 1.1.0 (CC0, npm), ropa,
  texturas y rig de 21 huesos hechos por E2A en `tools/blender/build_player.py` (bpy 5.3 como módulo).
  Dos variantes: ataque (`e2a_player_off.glb`, 1,31 MB, con las acciones del clip) y defensa
  (`e2a_player_def.glb`, 1,19 MB, más pesada y ancha, rapado, zapatilla negra). Colores de `KITS` del motor; piel y
  dorsal por jugador en el render (textura de camiseta generada, número delante y detrás).

## 2. Cabeza que miraba arriba: corregida en origen

Observado (5452, 1,5/2,2/2,9/3,6 s): ojos al nivel del manejador. Medido: el marco nariz-orejas de MediaPipe daba
cara a +5,2/+18,2/+29,6° (mín/mediana/máx) sobre el horizonte. `tools/blender/fix_head.py` corrige el dato
(`*_motion_hf.json`) antes de construir el `.blend`, el `.glb` y los clips:
calibración constante −22,24° (mediana → −4°), cabeza frente a pecho en [−8, +24]°, cara absoluta en [−12, +6]°,
cuello = slerp(pecho, cabeza, 0,5). Resultado: −12,1/−3,4/+6,1°. Reimportado el `.glb`: mismas cifras (las tres
acciones `E2A_rest`, `E2A_screen_roll_5452`, `E2A_screen_roll_5452m`). El límite del motor en `skelclip.ts`
(antes ocultaba el error) queda solo como red: [−8, +30]°.

## 3. Integración por defecto (sin activar nada a mano)

`src/t3d/player3d.ts` decide por jugador, como función pura de la jugada:
1. `play.skel[id]` explícito; 2. `CLIP_LIBRARY` por patrón de acciones (`screen`+`roll` → `screen-roll-5452m` o
`-5452`) si la colocación encaja (giro añadido ≤ 35°, aproximación ≤ 60°); 3. animación del rig/choreo re-resuelta
sobre el esqueleto de la malla (`skelclip.bonesFromPose`: longitudes de la malla, piernas desde las caderas FK,
protección de alcance ≤ 8 cm, yemas sobre la mano del motor). Alternativa: cápsula (`Athlete.tsx`) si el `.glb` no
carga (`[E2A players3d] FALLBACK …` en el log), si `episode.players3d = 'A'` / `shot.players3d = 'A'`, o si el
episodio usa `faces` (caras estilizadas). El plan sale en el log del render (`[E2A players3d] e2a-player-v1 play …`)
y en `qc-tactical3d` (sección players3d). Sonido de bote/recepción/caída a 0 por defecto (`autoSfx`).

Verificación: el Eurostep se renderizó con las props normales del episodio (sin `players3d`, sin `skel`); el log del
render dice `O1:C/off/choreo | X1:C/def/choreo` en las jugadas A y B, sin `FALLBACK`. En el laboratorio del bloqueo,
la variante C (bundle sin nada) eligió sola `O5:C/off/screen-roll-5452m` y el resto `C/off|def/rig`.

## 4. Comprobaciones

| Comprobación | Resultado |
|---|---|
| `test-play` screen-roll-lab | 20/20 |
| `qc-players3d` screen-roll-lab | tobillo, deslizamiento, yemas 1,3 mm, cabeza arriba 3,0°, cabeza no enterrada −20,0° (O5@1,90 s), seek = reproducción 0 |
| `qc-contact` screen-roll-lab | deriva del pin 1,45 mm |
| `qc-tactical3d` eurostep-main | 26/27; único FAIL preexistente (ancla `gather` 3,19/3,15 en la base); players3d PASS (tobillo 0,0 mm, deslizamiento ≤ 0,47 mm/fotograma, cabeza +4,9°/−26,9°) |
| `qc-tactical3d` compatibilidad | gortat-screen-v3 26/27, hide4-main 40/41 (FAIL de duración preexistentes; con `faces` → A con motivo), spanoulis-main 27/27 |
| Mallas en 73 jugadas (`qc-players3d`) | 71/73; floppy-a-curl y hide-poss: yemas del portador > 40 mm con el brazo estirado |
| test-motion / test-ball | mismos fallos que la base 5rxcux (8 conocidos; ram-b/ram-v2/switch-a) |
| `.glb` | 21 huesos, 8 mallas con skin, texturas embebidas; se reimporta en bpy |

## 5. Tiempos y pesos (scale 0,5, 4 CPU)

| Render (Tactical3DV2, `--scale=0.5`, concurrency 4) | A cápsula | C E2A player | Fase 3 (lab, A / C) |
|---|---|---|---|
| bloqueo, vista táctica, real (108 fotogramas) | — (no cronometrado) | 252 s | 321 s / 239 s |
| bloqueo, tres cuartos, real | 198 s | 198 s | 187 s / 203 s |
| bloqueo, vista táctica, 0,4× | 378 s | 399 s | — |
| bloqueo, tres cuartos, 0,4× | 304 s | 303 s | — |
| muestra de acabado (8,47 s, 254 fotogramas) | — | 453 s | — |
| Eurostep completo (38,3 s, 1150 fotogramas) | — | 1510 s | — |

Pesos: `e2a_player_off.glb` 1,31 MB + `e2a_player_def.glb` 1,19 MB (2,50 MB, se cargan una vez por pestaña) frente
a 1,29 MB del `.glb` único del laboratorio de la fase 3 y 0 MB de la cápsula. Coste de C frente a A: igual dentro
del ruido (±5 %) en las cuatro tomas cronometradas del bloqueo.

## 6. Registro de clips

`src/t3d/clips/registry.json`: `screen-roll-5452m` (abre a su izquierda, validado en screen-roll-lab) y
`screen-roll-5452` (a su derecha, solo colocación). Fuente `E2A_26_BLOQUEO_GIRO_Y_ROLL_APROXIMACION_OPUESTA_T02.MOV`,
1,001–4,037 s, apoyos y pivote en el registro. Documentación de producción: `produccion/tactical/FORMATO-CHICAGO.md`
(«Jugadores 3D y acabado por defecto»), `template/TACTICAL3D.md`.

## 7. Entregables (fuera de Git)

`/mnt/project-files/tactical-studio/3d-animation-mpfb/`: `comparativa_{tactica,34}_{real,lenta}.mp4` y
`comparativa_combinada.mp4` (A | C | REF 5452 en espejo, alineada por los hitos del clip, fases rotuladas);
`renders/` (paneles sueltos, `finish.mp4` = muestra del acabado, `euro.mp4` = Eurostep por la ruta normal con su
voz y música aprobadas, `players3d-log-lines.txt`, props y logs); `glb/`, `blender/{off,def}/`, `clips/`,
`datos_pose/`. Reproducir: `npx remotion bundle src/index.ts --out-dir <B>` en 5fb1382 y
`npx remotion render <B> Tactical3DV2 <out>.mp4 --props=<props> --gl=swangle --concurrency=4 --scale=0.5 --log=warn`
(bundles del bloqueo: `scripts/screen-roll-lab-compare-bundle.py`; acabado: `scripts/players3d-finish-bundle.py`;
composición: `PANELS=A,C,REF REFDIR=… python3 scripts/screen-roll-lab-compose.py <renders> <dest>`).
B (clip + cápsula) no se volvió a renderizar: las B de la fase 3 llevan la cabeza antigua y C ya contiene el clip.

## 8. Pendiente (estado exacto)

- Licencia: la clave `3d/e2a-player-makehuman-cc0` va en el sidecar `*.glb.provenance.json`; falta añadirla a
  `config/asset_licences.json` y al `bundle_manifest` de tactical_studio (requiere aprobación del propietario; no tocado).
- Estimado: el clip lleva el tronco ~20° más inclinado que la toma en el bloqueo (solo cámara frontal); O5 baja la
  cara a −20° en 1,90 s (mirando al suelo cerca, dentro del QC). Necesita perfil de 5452/5451.
- Cuello y sisas con ligera ondulación en primer plano; yemas en floppy-a-curl/hide-poss.
- Episodios con `faces` siguen en A (la malla tiene cara neutra).
- Para que un spec use el clip, la jugada debe declarar `roll` tras `screen`; si no, va por el rig (también C).
- Acabado gráfico: sin cambios de estilo salvo jugador y bote a 0.
- Tomas que faltan: perfil 90° de 5452/5451, lateral a 60 fps, 5431/5433 (defensa), 5413–5416.
