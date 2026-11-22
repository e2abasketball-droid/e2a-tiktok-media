# Realism V3.1 — Entrega

Rama `claude/realism-v3-1` (desde `claude/realism-v3` `a9db5d1`). No se ha hecho merge, publicación ni programación. Metricool, `main`, la tarea diaria y los PR #12/#13 no se han tocado. Coste: 0 €.
Salidas: `/mnt/project-files/tactical-studio/realism-v3-1/`. Documentos: `produccion/realism-v3-1/` (AUDIT, DESIGN-DECISION, QA, METRICS.json, contact_sheet.jpg).

## 1. Qué ha cambiado de verdad respecto a V3

**Completado**
- **Movimiento autorado** (`template/src/t3d/realism-v3-1/motion.ts`, `clips.ts`). En V3 el cuerpo usaba la misma pose del motor que legacy; ahora O1 tiene un clip tecleado a mano, en función pura de (jugada, id, t):
  - calendario de 36 pisadas anclado al track, con el pie bloqueado durante el apoyo;
  - pivote sobre la planta y cabeceo del pie (despegue de puntera, apoyo de talón);
  - capas de marcha y desplazamiento lateral del peso;
  - limitador de alcance;
  - salto balístico de 0,505 m;
  - brazos por modos con fundido;
  - balón en mano con socket y corrección de palma.
- **Puente de huesos** (`skelclip.ts`): la pelvis puede llevar un «up» propio (`hipsUp`) distinto al del tronco. El pie ya no se hunde 4,7° con la puntera hacia abajo.
- **Asset V3.1** (`tools/blender/build_player.py --body v31 --shoe v31 --garment v31`):
  - cuerpo atlético con morphs MakeHuman CC0 (hombros, dorsales, trapecio, antebrazos, gemelos);
  - camiseta holgada con sisa profunda y separación del cuerpo;
  - pantalón más ancho;
  - **suela separada** con caída talón-puntera y punta levantada;
  - metadatos JSON.
- **Tela L1** (`clothV31`): muelle amortiguado por la trayectoria real de la pelvis, determinista.
- **Flag** `athleteRenderer: 'v31'` opt-in. `legacy` sigue por defecto y es idéntico al píxel.
- **QC** `template/scripts/qc-realism-v31.mts`: deriva de pies, suela plana, hueco palma-balón, continuidad del balón, aceleraciones, seek en 3 órdenes y amplitud frente a legacy.

**Parcial**
- Pesos del tirante de la camiseta: arreglados tras la revisión del coordinador (upperarm→clavicle, clavicle→chest), pero el abombamiento del hombro a 3,30 s y el pliegue a 4,93 s **siguen visibles**.
- Rendimiento con 10 jugadores: medido solo como render offline de 1,5 s (ver §3).
- Clip solo para O1 en una jugada. Los demás jugadores usan la pose del motor sobre el GLB V3.1.

**Bloqueado / descartado**
- **Tela L2 (bake de Blender): probado, no integrado.** Funciona en headless (90 frames en 5,13 s), pero:
  - estira un 41 %;
  - cae 4–9 cm en reposo;
  - requiere un bake por jugada y jugador (≈ 1,9 MB float16 por toma).
  - Detalle en QA.md, Gate D.
- Mocap o librerías de animación: sin licencia verificable a 0 €; no se usaron.

**Planificado**: librería de clips reutilizables; tirante corrector; horma de zapatilla modelada; integración en un extracto táctico corto tras la revisión del propietario.

## 2. Prueba visual (rutas verificadas)
| Archivo | Verificado (ffprobe / ls) |
|---|---|
| `legacy_vs_v3_1_locked_ab.mp4` | 1080×1920, 30 fps, 375 frames, 12,5 s |
| `legacy_vs_v3_1_locked_ab_close.mp4` (cámara cercana; héroe ≈ 70–80 % de cada mitad) | 1080×1920, 30 fps, 375 frames, 12,5 s |
| `motion_v3_1_diagnostic.mp4` (toma única) | 1080×1920, 30 fps, 375 frames, 12,5 s; toma única con cámara de seguimiento 3/4 (el salto a 8,2 s corta el balón por arriba) |
| `technical_diagnostics.mp4` (plano abierto, recorrido completo) | 1080×1920, 30 fps, 375 frames, 12,5 s; plano abierto fijo de la jugada completa. **No** es un montaje con depuración de huesos/contactos: esos datos están en qa/qc-realism-v31.json |
| `contact_sheet.png` (8 pares a tiempos idénticos + primeros planos con la misma caja de recorte) | 2880×1170 |
| `assets/e2a_player_{off,def}_v31.{glb,blend,meta.json}`, `assets/license.json` | sha256 en license.json |
| `evidence/` (turntable, wireframe, frente y lado, primer plano de la suela, gate1_v31_2s.mp4, cloth_l2_bake.json, ab_close_strip.png) | presentes. Los stills de bpy son de la pose de reposo, que no cambia con el arreglo de pesos |

Encuadre: en el A/B bloqueado normal el héroe ocupa ≈ 35–40 % del alto total (≈ 70 % de cada mitad, con el plano abierto que exige ver suelas y balón). El A/B cercano es el que se debe juzgar en el móvil.

## 3. Números
- Mallas con skinning: 10 (Body, Jersey, JerseyTrim, Shorts, ShortsTrim, Shoe.L/R, Sole.L/R, Hair). Mallas de prenda: 4 (+4 de calzado).
- Huesos: 27. Animaciones en el GLB: 1 (`E2A_rest`); el movimiento es código determinista. Morphs: 12 (6 cuerpo + 6 pantalón). Materiales: 8.
- Triángulos: 29 958 por jugador (Body 19 398, Jersey 2 812). GLB: 1,54 MB (off) / 1,52 MB (def).
- Tiempos de render: A/B 988 s (375 frames, 2,63 s/frame, 7,5 GB RSS); diagnóstico 580 s (1,55 s/frame); bench 10 jugadores 1,5 s: legacy 164 s, V3.1 192 s (+17 %), RSS 3,4 → 4,2 GB. CPU con SwiftShader, sin GPU; no se afirma tiempo real. Tabla completa en QA.md, Gate F.
- Tests:
  - tsc 0;
  - regresión de píxeles 12/12 idénticos;
  - regress-poses 14/14 (12+2);
  - qc-realism-v31: deriva de pie máx 1 mm, palma-balón mediana 1,2 cm / máx 3,7 cm, seek idéntico en 3 órdenes;
  - test-play 11/13 (falla aceleración 32,6 m/s² en 3,27 s; 5v5 no aplica);
  - test-ball 6/7 (hueco 0,311 m a 7,59 s con la pose legacy).
- Amplitud legacy → V3.1:
  - rango de altura de pelvis 0,559 → 0,71 m;
  - inclinación 0,53 → 0,72 rad;
  - giro de cabeza 1,955 → 2,425 rad;
  - altura en el aire 0,418 → 0,524 m.

## 4. Qué mejoró perceptivamente (timestamps del A/B)
Autoevaluación no ciega; sin revisores humanos, así que el Gate E **no** está superado.
- **3,3 s**: frenada con pie plantado, cadera baja y tronco contra-inclinado (legacy pasa de pie y erguido).
- **3,3–3,6 s**: corte lateral con empuje desde el pie exterior.
- **4,9–5,9 s**: manos preparadas antes de la recepción, pivote sobre la planta y balón al bolsillo.
- **6,1–6,9 s**: bote con paso atrás; mano, balón y suelo coinciden.
- **7,9–8,6 s**: carga, salto de 0,5 m, suelta y follow-through.
- Siluetas: hombros y espalda más anchos, camiseta suelta con sisa, suela visible.

Advertencias: a 1,0 s, 2,3 s y 11,8 s la diferencia es pequeña. La camiseta en el hombro se ve **peor** que en legacy en primer plano a 3,30 s y 4,93 s.

## 5. Los 5 defectos principales y su arreglo
1. **Tirante/sisa como carcasa rígida** (3,30 s abombado, 4,93 s pliegue rígido). Pesos ya corregidos parcialmente. → Siguiente: morph corrector del tirante accionado por el ángulo clavícula/hombro, o 2 huesos de tirante guiados por la clavícula con un límite de separación.
2. **Defensa y preparado poco legibles** (1,0 s, 11,8 s: brazos poco abiertos, base estrecha). → Teclear el modo `defense`/`ready` con manos por fuera de los hombros y una base 1,3× más ancha.
3. **Zapatilla con forma de zapatilla de casa** (cuña sin cuello ni contrafuerte). → Horma modelada (cuello acolchado, contrafuerte, puntera) por código en `build_player.py`.
4. **Esquina del track en B** (aceleración 32,6 m/s² a 3,27 s) y clips hechos a mano por jugada. → Suavizar la esquina en el generador de la jugada; librería de clips (arranque, frenada, corte, recepción, tiro) re-temporizable sobre cualquier track.
5. **Bajo de la camiseta con picos laterales** en giros rápidos (5,3–5,8 s) y giro de tela limitado. → Limitar la torsión por anillo en `clothV31` y suavizar los pesos del bajo; si no basta, un bake L2 corto solo del bajo.
Otros: la palma no puede rotar (roll) sobre el balón; en el A/B cercano el salto corta cabeza y balón a 8,2 s.

## 6. Cómo reproducir
```bash
cd /home/user/e2a-tiktok-media
# assets (bpy 5.3 headless; cada variante en su carpeta: las texturas se escriben en <dir>/tex)
python -I tools/blender/build_player.py -- --variant off --rig v3 --garment v31 --body v31 --shoe v31 \
  --out-blend B/e2a_player_off_v31.blend --out-glb B/e2a_player_off_v31.glb \
  --out-rig B/e2a-off-v31.rig.json --out-meta B/e2a_player_off_v31.meta.json      # ídem --variant def
python -I tools/blender/cloth_bake_l2.py -- B/e2a_player_off_v31.blend l2.json 90   # experimento L2
# jugada y episodios
python3 template/tactical/specs/_gen-realism-v3-1-onetake.py
python3 template/tactical/episodes/_gen-realism-v3-1-onetake.py <props_dir>
# QC
cd template && npx tsx scripts/qc-realism-v31.mts && npx tsc --noEmit
# render (CPU, SwiftShader)
npx remotion bundle src/index.ts <bundle>
npx remotion render <bundle> Tactical3DV2 out/ab.mp4 --props=<props rv31-ab> --gl=swangle --concurrency=4 --muted
```
Props usadas: `ab`, `ab-close`, `v31`, `wide-v31`, `bench-{1,10}-{legacy,v31}`, generadas por `_gen-realism-v3-1-onetake.py`.
Rama `claude/realism-v3-1`; el commit está en el informe final. Nada mergeado ni publicado.

## 7. Siguiente hito
Solo después de la revisión del propietario (checklist en QA.md, Gate E): arreglar el tirante, la defensa y la zapatilla; después, integrar V3.1 en un extracto táctico corto; después, diez jugadores; después, nuevos Reels.
