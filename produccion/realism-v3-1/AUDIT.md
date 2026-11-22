# E2A Realism V3.1: auditoría (fase cero)

Fecha: 22-11-2026. Base: `claude/realism-v3` en `a9db5d1`; rama de trabajo `claude/realism-v3-1`.

Mismo entorno que V3:

- 4 núcleos de CPU, sin GPU; render por software con Chromium headless `--gl=swangle`; 15 GB de RAM.
- bpy 5.3 en un venv, sin binario de Blender.
- Remotion 4.0.539 y three.js del repo.

**Baseline.** No se generó un render nuevo antes de los cambios. Se usaron como baseline los vídeos V3 entregados y verificados en `/mnt/project-files/tactical-studio/realism-v3/`:

- `side_by_side_close.mp4`, el que revisó el owner;
- `baseline_legacy.mp4`;
- `prototype_v3.mp4`.

Los hashes de píxel de legacy son los de `template/tactical/reports/realism-v3-2026-11-22/pixel-regression.txt`.

| Afirmación | Qué se encontró | Archivo/línea | Verificado | Acción siguiente |
|---|---|---|---|---|
| «V3 mueve el cuerpo distinto de legacy» | **Falso.** La rama V3 llama a `poseAt` (la misma pose del motor) y solo añade `weightShift`: 6 cm de bajada y 11,5° de inclinación, y se apaga con balón | `template/src/t3d/Scene.tsx:318-320` (`a9db5d1`); `realism-v3/athleteV3.ts:115` | Sí (código y QA V3) | Capa de movimiento autorada (`realism-v3-1/motion.ts`) |
| «La pelvis puede inclinarse sola» | **No.** El frame de la pelvis usa el vector pecho-pelvis: la pelvis copia el tronco | `template/src/t3d/skelclip.ts:576` (`F.hips = twoVec(up, side)`) | Sí | `hipsUp` opcional en `bonesFromPose` (sin él, idéntico) |
| «Los pies hacen toe-off y golpe de talón» | **No.** El talón se deriva de la puntera (`heel.z = toe.z - 0.01`): el pie siempre queda plano. Además queda 4,7° con la puntera abajo: bola del pie 1,15 cm bajo el suelo, talón +0,5 cm | `skelclip.ts:660`; medido con FK sobre el rig V3.1 | Sí (script de medida, frames 0,5 s y 12 s) | Pitch de pie propio en `framesV31` + corrección de pendiente medida |
| «Las zapatillas tienen suela» | **No.** Casco convexo del pie; la «suela» es solo un cambio de material por debajo de 3 cm | `tools/blender/build_player.py:974` (`a9db5d1`) | Sí | `--shoe v31`: pieza de suela separada |
| «El cuerpo es atlético» | Músculo macro 0,45; ofensivo `EXTRA` solo hombro +0,25 y mano | `tools/blender/mh_body.py:16`; `build_player.py:80` | Sí | `--body v31`: set atlético |
| «La camiseta es holgada» | V3: holgura 2,2 → 3,6 cm, ceñida al cuerpo hacia la cadera; sisa en el borde de la región de torso de MakeHuman | `build_player.py:745` (`a9db5d1`) | Sí | `--garment v31`: sisas profundas, aire, más holgura |
| «La tela reacciona al cuerpo» | cloth2 se mueve con la aceleración del TRACK (`posAt`) y la altura de salto del motor, no con el cuerpo; límite horizontal 5 cm | `template/src/t3d/cloth2.ts:21,33` | Sí | `clothV31`: muelle movido por la pelvis autorada; límite 8,5 cm |
| «El balón sale de la mano» | V3: las manos hacen IK al balón del motor (mediana de punta de dedo 7,4 mm) | informe V3 `QA_REPORT.md` | Sí (QA V3) | V3.1: el balón es el socket de la mano mientras se tiene, con release al punto del motor |
| «Legacy es el render por defecto» | `DEFAULT_ATHLETE_RENDERER = 'legacy'` | `template/src/t3d/realism-v3/index.ts:12` | Sí | Se mantiene; se añade el valor `'v31'` |
| «El seek es determinista» | V3: stills en frío idénticos; secuencial frente a frío, diferencias de ≤17 píxeles | `template/tactical/reports/realism-v3-2026-11-22/seek.txt` | Sí | Repetido en V3.1 (`QA.md`, puerta B) |
| «Hay dedos con huesos» | Sí: 27 huesos, con 3 por mano | `tools/blender/skeleton.py` (`enable_fingers`) | Sí (`metadata`) | Se reutiliza |
| «El build legacy no cambia» | `--garment v2` sha `f46cb06d…`; `--rig v3 --garment v3` = el GLB V3 del repo (`d16acc05…`) | `build_player.py` | Sí: recompilado tras los cambios V3.1 y sha idénticos | — |
| «Existe un `.blend` fuente» | Sí: `build_player.py` guarda `.blend` y `.glb` por variante | `build_player.py`, final del archivo | Sí | `.blend` V3.1 en `/mnt/project-files/.../realism-v3-1/assets/` |
| «Se puede simular tela en bpy sin interfaz» | Sí: el modificador Cloth hornea al avanzar frames (ver `QA.md`, puerta D) | `tools/blender/cloth_bake_l2.py` | Sí (experimento L2) | No se integra; razones en `QA.md` |
