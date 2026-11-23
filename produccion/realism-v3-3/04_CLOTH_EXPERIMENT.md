# Realism V3.3 — 04 CLOTH EXPERIMENT (Gate 3, L2 acotado)

**Decisión: EXPERIMENTAL. No se integra.** La tela que se renderiza en V3.3 es la de V3.2: L1 con el oscilador precalculado (`CLOTH33`, `clothV33`).

## Qué se probó
- Script: `tools/blender/cloth_bake_l2_v33.py`, con bpy 5.3 sin interfaz, sobre la GLB V3.2 `e2a_player_off_v32.glb`. Es la malla que usa V3.3.
- Prueba: la misma que en V3.1, para poder comparar (90 frames: carrera, frenada, salto de 0,35 m y caída).
- Se atacaron las tres causas por las que V3.1 rechazó L2:

| Causa V3.1 | Cambio V3.3 | Resultado |
|---|---|---|
| Estiramiento 41 % | Tensión y compresión 40 (antes 12), calidad 10 (antes 6) | P99 por frame ≤ **11,7 %** ✔. Máx. **3,58×** ✘ en unas pocas aristas |
| Caída de 4–9 cm en reposo | Pre-roll estático de 30 frames | Caída en reposo **1,8 mm** (mediana del bajo), deriva tras el pre-roll **1,2 mm** ✔ |
| Sin camino a Three.js | Exportación de los frames como morph targets glTF + carga real con `GLTFLoader` de three.js | **Carga OK**: 1518 vértices, 94 morph targets (90 del bake + 4 propios de la malla), todo finito, 1,74 MB ✔ |

## Datos (`qa/cloth_l2_v33_bake.json`, `qa/cloth_l2_v33_three_load.json`)
- Bake: 10,3 s de pared para 120 frames (pre-roll incluido), 88 ms por frame (mediana).
- Velocidad máx. de vértice: 1,55 m/s.
- Desplazamiento del bajo respecto al skinning: mediana 0,87 cm, **máx. 21,5 cm**. Es un valor atípico: unas pocas aristas rotas en el aterrizaje.
- Se probó soldar las costuras UV (`--weld`, 1518 → 1499 vértices) por si la tela se abría en ellas. **No cambia nada** (máx. 3,58), así que la causa no son las costuras. Lo más probable es la colisión con el cuerpo en el aterrizaje. Sin cerrar.
- Coste: un bake por jugada y por jugador; unos 1,7 MB por cada 3 s y jugador sin comprimir. Para un 5v5 de 11 s serían unos 63 MB.

## Por qué no se integra
1. Hay aristas sueltas que se estiran 3,6 veces: en primer plano se verían como un desgarro.
2. Hace falta un bake por jugada: la tela no viaja con el compilador de eventos. Cada jugada nueva exige Blender.
3. El peso (decenas de MB por jugada) no compensa frente a L1, que es gratis en tiempo de render.

**No hay vídeo `05_cloth_L2_vs_hybrid.mp4`.** El bake no se reprodujo dentro de la escena de Remotion, solo se cargó en three.js. Hacer un vídeo con una prenda que se desgarra no aportaría nada. Si se quiere avanzar con L2: colisión más gruesa en el aterrizaje, límite de estiramiento por resorte y un clip híbrido (L2 solo en el bajo de la camiseta).
