# Realism V3.1 — QA (gates A–H)

Rama `claude/realism-v3-1` (desde `claude/realism-v3` `a9db5d1`). Fecha 2026-11-22.
Entorno: contenedor sin GPU, Chromium headless shell 1243 con `--gl=swangle` (SwiftShader, CPU), Remotion 4.0.539, bpy 5.3 headless.
Todas las cifras salen de los ficheros de `qa/` y de `ffprobe` sobre los MP4 exportados. Donde no se midió, se indica.

| Gate | Resultado | Resumen |
|---|---|---|
| A estructural | PASA | GLB con SkinnedMesh, 27 huesos, 10 mallas separadas (cuerpo / camiseta / ribete / pantalón / ribete / zapatilla×2 / suela×2 / pelo), `.blend` fuente guardado |
| B determinismo | PASA | 3 órdenes de seek con pose idéntica byte a byte; stills fríos 100→5→250→100 con sha idéntico en f100 |
| C contactos | PASA (provisional) | deriva de pie apoyado ≤ 1 mm en 15 apoyos; hueco palma-balón mediana 1,2 cm, máx 3,7 cm |
| D prenda | PARCIAL | sin explosiones ni normales invertidas; **defecto visible en el tirante/sisa a 3,30 s y pliegue rígido a 4,93 s** (mejorado, no resuelto) |
| E percepción | **NO SUPERADO / SIN EVALUAR** | no hay revisores humanos en esta sesión; ver checklist del propietario |
| F rendimiento | MEDIDO | ver tabla; CPU sin GPU, no se afirma tiempo real |
| G regresión | PASA | 12/12 píxeles idénticos (legacy, V3, rv31-legacy), 14/14 poses idénticas, tsc 0 |
| H licencias | PASA | CC0 (MakeHuman vía ara3d-data 1.1.0) + código E2A; sin assets ni APIs de pago |

## Gate A — autenticidad estructural
Fuente: `assets/e2a_player_{off,def}_v31.meta.json` (generado por `build_player.py --out-meta`).

| Malla | Vértices | Triángulos | Morphs |
|---|---|---|---|
| E2A_Body | 9814 | 19398 | 6 (correctivos rodilla/codo/cadera) |
| E2A_Jersey | 1499 | 2812 | 0 |
| E2A_JerseyTrim | 708 | 1416 | 0 |
| E2A_Shorts | 861 | 1632 | 6 |
| E2A_ShortsTrim | 264 | 528 | 0 |
| E2A_Shoe.L / .R | 1555 ×2 | 1248 ×2 | 0 |
| E2A_Sole.L / .R | 290 ×2 | 576 ×2 | 0 |
| E2A_Hair | 301 | 524 | 0 |
| **Total** | | **29958** | 12 |

- Huesos de deformación: 27 (incluye clavícula.L/R y dedos). Materiales: 8. Animaciones en el GLB: 1 (`E2A_rest`); el movimiento es una función determinista en TS (`realism-v3-1/motion.ts`), no un clip glTF.
- Prendas: 4 mallas de prenda (camiseta, ribete, pantalón, ribete) + 4 de calzado.
- GLB: off 1 538 368 B, def 1 524 368 B. `.blend` fuente: 941 061 B / 936 945 B.
- Carga en runtime verificada: los vídeos `gate1_v31_2s.mp4`, A/B y diagnóstico se renderizan con este GLB a través de `Scene.tsx` → `SkinnedAthlete`.

## Gate B — render determinista
- `qc-realism-v31.mts`: pose de O1 en 3 órdenes de seek (`[100,5,250,100]`, `[312,17,180,312]`, `[60,340,222,60]`) después de `resetV31Caches`: **idéntica** (JSON de 2884 B comparado byte a byte).
- `seek.sh` (stills en frío en procesos separados frente a render secuencial): ver `qa/seek.txt`. stills en frío f100 (1.º) y f100 (4.º, tras f5 y f250): **sha idéntico** (`3e3ea78f…`). Frío frente a secuencial: f5 idéntico al píxel; f100: 7 píxeles distintos, máx 15/255; f250: 3 píxeles, máx 14/255 (ruido de SwiftShader).
- Tolerancia de píxel documentada: SwiftShader puede dar ≤ 15/255 en ≤ 7 píxeles entre render en frío y secuencial (medido en Gate 1); se considera ruido del rasterizador, no estado.

## Gate C — contactos (umbrales provisionales)
Fuente `qa/qc-realism-v31.json` (muestreo 30 Hz, balón 120 Hz).
- Pies: 15 apoyos, deriva máx **0,001 m**, mediana 0. Suela plana: z de la suela = 0 en 285 muestras de apoyo (corregido el hundimiento de 4,7° punta-abajo heredado de `bonesFromPose`).
- Balón en mano: 164 muestras, hueco palma-superficie mediana **0,012 m** (objetivo 0,012), p95 0,012, mín −0,022 (6,77 s, ligera interpenetración en el bote), máx 0,037 (8,17 s, inicio del follow-through).
- Continuidad del balón: salto máx 0,077 m por 1/120 s (vuelo del tiro, físico). En eventos: recepción 0,058 m, empuje del bote 0,001, recogida 0,001, suelta 0,002.
- Aceleración máx de articulaciones: cadera 129 m/s² a 8,6 s (aterrizaje), mano R 807 m/s² a 8,28 s (flick de muñeca), mano L 429 a 6,75 s.
- Salto: 0,505 m de altura.
- No medido: intersección barrida balón-cuerpo (solo revisión visual).
- Tests genéricos: `test-play` 11/13 (5v5 no aplica; aceleración 32,6 m/s² en O1 a 3,27 s por la esquina de la trayectoria en B — **falla**), `test-ball` 6/7 (hueco 0,311 m a 7,59 s medido con la pose legacy del motor, no con V3.1).

## Gate D — prenda
- Sin explosiones de malla, sin normales invertidas visibles en los frames del contact sheet.
- Cloth L1 (`clothV31`): muelle amortiguado (1,7 Hz, ζ 0,26) sobre la trayectoria de la pelvis, integrado desde t−1,2 s a 120 Hz → determinista en seek.
- **Defecto abierto (revisión del coordinador)**: a 3,30 s el tirante/hombro de la camiseta se abomba y forma un quiebro (la sisa se separa del hombro como una carcasa rígida); a 4,93 s, pliegue rígido.
  - Causa encontrada: los vértices del tirante heredaban peso de `upperarm` por transferencia del vecino más cercano; al levantar el brazo arrastraban el tirante.
  - Arreglo aplicado: 85 % del peso `upperarm.L/R` de la camiseta → `clavicle`; 40 % del peso `clavicle` por debajo de la sisa (rampa 8 cm) → `chest`. Comparación visual antes/después: **mejora parcial**, el bulto sigue visible en primer plano.
  - Siguiente arreglo: morph correctivo de tirante accionado por el ángulo del hombro, o huesos de tirante guiados por la clavícula.
- Bajo de la camiseta: pequeños picos laterales en giros rápidos (pivote 5,3–5,8 s).
- **L2 (bake de tela con Blender)** — sí se probó: `tools/blender/cloth_bake_l2.py`, resultado en `evidence/cloth_l2_bake.json`.
  - 90 frames, 1499 vértices, bake 5,13 s (54 ms/frame mediana, 98,5 máx), todos los valores finitos.
  - Estiramiento máx de arista 1,41 (41 %), velocidad máx 1,68 m/s, desplazamiento del bajo mediana 1,0 cm / máx 23,1 cm, vértices fijados ≤ 1,9 cm.
  - Caída de 4–9 cm en reposo antes de cualquier movimiento: la prenda no está en equilibrio de caída.
  - Coste estimado para 375 frames: 6,75 MB float32, 1,88 MB float16 solo vértices móviles, 0,94 MB int8.
  - **Decisión: no integrado.** Funciona en headless, pero necesita un bake por jugada y jugador, estira demasiado y cae en reposo. Se mantiene L1.

## Gate E — mejora perceptual
**No superado: no hubo revisores humanos.** No se inventan resultados.

Autoevaluación (Claude, no ciega, sesgo evidente) sobre `legacy_vs_v3_1_locked_ab.mp4`:
- Diferencias claras: 3,3 s apoyo de frenada; 3,3–3,6 s corte; 4,9–5,9 s recepción, pivote y bolsillo; 6,1–6,9 s bote con paso atrás; 7,9–8,6 s carga y salto.
- Débil o igual: 1,0 s (preparado), 2,3 s (carrera), 11,8 s (defensa con brazos poco abiertos).
- Peor que legacy: camiseta en el hombro en primer plano (3,30 s, 4,93 s).

Checklist para el propietario (ver en el móvil, `legacy_vs_v3_1_locked_ab_close.mp4` primero):
1. Tapa las etiquetas. ¿Qué mitad parece una persona y cuál un maniquí? Anota el segundo exacto.
2. 3,0–3,6 s: ¿se nota el frenazo (cadera baja, pie plantado sin patinar)?
3. 4,5–5,9 s: ¿las manos van al balón antes de que llegue? ¿El pivote gira sobre la planta?
4. 6,1–6,9 s: ¿el bote coincide con mano y suelo?
5. 7,9–9,0 s: ¿carga, salto, suelta y aterrizaje se leen como un tiro?
6. Hombros y tirantes en 3,3 s y 4,9 s: ¿molesta el abombamiento?
7. Zapatillas: ¿se leen como zapatillas o como zapatillas de casa?
8. Veredicto: ¿V3.1 es mejor que legacy? sí / no / igual, y qué cambiarías primero.

## Gate F — rendimiento
CPU (SwiftShader), concurrencia 4, 1080×1920, 30 fps. Otros renders en paralelo pueden inflar las cifras; se indica.

| Render (CPU SwiftShader, conc. 4) | Frames | Pared (s) | s/frame | RSS pico (MB) |
|---|---|---|---|---|
| A/B bloqueado (split, 2 escenas) | 375 | 988,0 | 2,63 | 7509 |
| A/B cercano (split) | 375 | 716,4 | 1,91 | 4274 |
| Diagnóstico V3.1 (1 escena) | 375 | 579,7 | 1,55 | 3597 |
| Plano abierto V3.1 | 375 | 486,2 | 1,30 | 3535 |
| Gate 1 V3.1 (2 s) | 60 | 131,8 | 2,20 | 3358 |
| Bench 1 jugador legacy | 45 | 104,3 | 2,32 | 3110 |
| Bench 1 jugador V3.1 | 45 | 105,4 | 2,34 | 3240 |
| Bench 10 jugadores legacy | 45 | 164,1 | 3,65 | 3377 |
| Bench 10 jugadores V3.1 | 45 | 192,4 | 4,28 | 4213 |

Lectura: con 10 jugadores V3.1 es un 17 % más lento que legacy (192,4 frente a 164,1 s) y usa +836 MB de RSS pico; con 1 jugador, igual (+1 %). Los bench incluyen ≈ 60–70 s fijos de arranque (bundle, navegador, GLB), así que el coste por frame real es menor que la columna s/frame. Los renders se lanzaron en serie (A/B y A/B cercano coincidieron unos minutos con un render antiguo que se paró).

- Bytes de asset: GLB V3.1 1,54 MB por variante (2 variantes = 3,06 MB) frente al GLB legacy.
- Escalado a 10 jugadores: ver bench-10. La geometría (≈ 30 k tris por jugador → ≈ 300 k) no es el cuello de botella en CPU; el skinning y el rasterizado SwiftShader sí. No se afirma tiempo real.

## Gate G — regresión cero
- `tsc --noEmit`: rc 0.
- Regresión de píxeles (`qa/pixel-regression.txt`): **12/12 idénticos** (maxdiff 0) — episodios legacy (blob, chicago v2/v3, zona 2-3), renderer V3 de rv3 y rv31 en legacy.
- `regress-poses`: 12/12 idénticas a `d700987` y 2/2 a `8e418e9`.
- El flag `athleteRenderer` vale `legacy` por defecto; valores desconocidos → legacy (fallo cerrado). `v31` solo se activa por props explícitas.
- Sin cambios en publicador, Metricool, subida automática ni tarea diaria.
- Builds legacy y V3 del GLB reproducibles: `--garment v2` sha `f46cb06d…`, `--rig v3 --garment v3` = GLB V3 commiteado `d16acc05…`.

## Gate H — licencias y procedencia
`assets/license.json` y `players3d/*.provenance.json`: base MakeHuman y targets CC0-1.0 (npm `ara3d-data` 1.1.0, uso comercial sí, atribución no requerida); esqueleto, prendas, texturas y movimiento: código E2A. Movimiento tecleado a mano en `clips.ts`, sin captura de movimiento ni metraje de retransmisiones. 0 € gastados.
