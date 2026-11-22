# E2A Realism V3.2: auditoría

Fecha: 22-11-2026. Base: `claude/realism-v3-1` en `e014de3`. Rama de trabajo: `claude/realism-v3-2`.

**Entorno**

- CPU de 4 núcleos, sin GPU. Chromium headless `--gl=swangle`. 15 GB de RAM.
- bpy 5.3 en un venv.
- Remotion 4.0.539.

## 1. Auditoría de V3.1 (antes de tocar nada)

Se midió con herramientas nuevas que usan el **mismo camino de código que el render**:

- `scripts/qc_cloth_v32.py` reimplementa en CPU el skinning y el shader de tela sobre la malla exportada del `.blend`.
- `scripts/qc-realism-v32.mts` mide sobre los huesos resueltos.

Todos los valores son de la jugada one-take, jugador O1, V3.1 completo (asset V3.1, movimiento V3.1, tela V3.1).

| Defecto de la revisión | Causa raíz encontrada | Evidencia medida (V3.1) | Archivo |
|---|---|---|---|
| Pico en el pantalón ~3,75 s | Los shorts usaban **los mismos uniforms de tela que la camiseta** (balanceo y giro de camiseta aplicados al bajo del pantalón). En el bajo, una arista se estira ×2,1 | Desplazamiento máx. del pantalón 13,2 cm (4,03 s). Estiramiento máx. del bajo 2,13. 89 frames del bajo > 1,3 | `SkinnedAthlete.tsx` (un solo `clothU` para las dos prendas), `cloth2.ts` |
| Casco en el tirante del hombro | Pesos de la camiseta copiados del cuerpo vértice a vértice: la banda pecho-espalda sigue a spine/chest (22,5°) y el tirante, a clavícula/brazo. Sin correctivo | Estiramiento máx. del tirante **3,39** (3,33 s). P95 1,35 | `build_player.py`, transferencia de pesos V3.1 |
| Picos laterales del bajo 5,3-5,8 s | Mismo origen: el peso del bajo salta entre caderas y muslos de una fila de vértices a la siguiente | Bajo de la camiseta: máx. 2,15; **376 frames** con estiramiento > 1,3 | `build_player.py` |
| Zapatilla de zapatilla de casa | Pala = envolvente convexa del pie inflado. Solo hay suela separada (V3.1): sin cuello, sin contrafuerte ni puntera, todo el pie pesado a `foot` | Inspección del `.blend` y del render | `build_player.py`, bloque de zapatillas |
| Postura de preparado y de defensa floja | Clip V3.1 tecleado a mano para un solo jugador. Sin parámetros de postura (ancho, bajada, brazos) reutilizables | Solo hay claves a mano en `realism-v3-1/clips.ts` | `realism-v3-1/clips.ts` |
| Tiro en suspensión 8,5-9,5 s | V3.1: salto como curva de altura independiente de los brazos. El balón «se lleva» a mano hasta el punto del motor; sin carga ni recepción acopladas | El ciclo no tiene fases explícitas (QC: muñeca derecha 2640 m/s² a 8,275 s, en el release) | `realism-v3-1/motion.ts` |
| Oclusión ~6,75 s | Cámara de seguimiento 3/4 con O2 en la línea de visión durante el bote | Revisión visual del A/B V3.1 | props `rv31-ab-close` |

## 2. Qué cambió en V3.2 y dónde

| Subsistema | Estado | Qué hay | Medido (detalle en QA.md) |
|---|---|---|---|
| Tela: uniforms separados camiseta / pantalón | **implementado** | `CLOTH32`: shorts con escala 0,33, máx. 2 cm, `maxDisp` 2,5 cm, sin giro; camiseta con `maxDisp` 6 cm. Límite `\|d\| ≤ maxDisp·hem` en el shader v32 | Desplazamiento del pantalón 13,2 → < 1 cm |
| Tela: pesos suavizados en origen | **implementado** | Laplaciano sobre el grafo de aristas: bajo del pantalón (28 it.), hombros/tirante (30), toda la camiseta (150), campo `hem` (10-12) | Tirante 3,39 → 1,71; frames de bajo > 1,3: 376 → 8 (con movimiento V3.1, asset V3.2) |
| Tela: correctivos de pliegue | **implementado** | Camiseta: `trunk` (flexión del pecho, pliegues ±6 mm) y `shoulder.L/R` (tirón del tirante al subir el brazo). Shorts: pliegues delanteros en `hip.L/R`. Modos nuevos `flexUp` y `raise`, solo en rigs v32 | Pesos de morph por frame en el volcado |
| Tela: grosor del bajo | **parcial** | Se mantiene el ribete-tubo (trim) de V3.1, que ahora lleva los shape keys. No hay banda de grosor nueva | — |
| Tela L2 (simulación) | **pendiente** | No se reintentó: el límite de presupuesto del render tenía prioridad. V3.1 dejó el experimento documentado | — |
| Biblioteca de movimiento paramétrica | **implementado** | `library.ts`: 9 primitivas, variación por semilla (tiempo, amplitud, cadencia, inclinación, bajada, braceo, ancho). Dos jugadas con guion: one-take y trío | QC por frame (QA.md) |
| Pasos / alcance | **implementado** | Cadencia y duty según la velocidad; el pie despega antes de quedarse > 0,5 m atrás; vuelo de balanceo ≤ 0,38-0,4 s | Deslizamiento máx. 1,6 cm (V3.1: 0,6; motor: 51,6 cm) |
| Pelvis | **implementado** | Envolvente suave (log-sum-exp) del alcance de pierna. Guarda de alcance de la malla pesada por apoyo (`Pose.reachW`, opcional; legacy y V3.1 no la usan) | Picos de pelvis > 60 m/s² fuera de aterrizajes: 0 filas (antes de los arreglos: 2295 m/s² a 2,80 s) |
| Posturas preparado / defensa / triple amenaza / closeout | **implementado** | Ancho, bajada e inclinación por postura, con paso bajo de ±0,24 s. Brazos propios por modo | Visual en los renders. Parámetros en `library.ts` |
| Tiro en suspensión acoplado | **implementado** | `shotPhase`: recogida → dip/carga → impulso (Hermite C1) → vuelo balístico (subida / release 35 ms antes del ápice / follow / descenso) → aterrizaje → recuperación. Brazos y balón con el mismo reloj | Hueco de palma en el release 1,2 cm (con el primer guion V3.2 era 0,8 m) |
| Balón: máquina de estados | **implementado** | FREE / INCOMING / FIRST_CONTACT / CONTROLLED / SECURED / DRIBBLE / SHOOT_PREP / RELEASE / FLIGHT / PASS | Primer contacto 4,925 s (pase a 4,933). Hueco de palma: P95 1,2 cm |
| Zapatilla v32 | **parcial** | Horma modelada (cuello acolchado con forro oscuro alrededor del tobillo, contrafuerte, puntera redondeada más baja que el empeine, panel de cordones, franja lateral). Antepié pesado al hueso `toe` en la bola del pie | Visual. No es una zapatilla de producto: sin cordones en geometría ni lengüeta |
| Interacción de 3 jugadores | **implementado** | Jugada `realism-v3-2-trio` con guiones O1 / O2 / X2 desde `play.marks` | QC: el balón no atraviesa el cuerpo de O1 (0 frames); en O2, ≤ 1,8 cm con el antebrazo durante el bolsillo |
| Debug de contactos | **implementado** | `debug32`: discos de pie, palmas y halo de estado del balón | Render `debug` |
| Paneles de comparación | **implementado** | `panels` en `Tactical3D` (A/B/C, test A, test B) | Renders |
| Visibilidad / oclusión | **experimental** | Rayos cámara → cabeza/manos/pies/balón frente a las cápsulas de otros jugadores (`--props`) | QA.md |
| 10 jugadores | **parcial** | Benchmark offline de 2 s con 10 copias V3.2 | QA.md, METRICS.json |

## 3. Lo que NO se cambió

- Legacy: pose del motor, assets y shaders. Es el valor por defecto y se comprobó con regresión de píxeles (QA.md).
- El camino V3.1 (`athleteRenderer: 'v31'`): mismo código y mismos assets. El build `--garment v31 --shoe v31` reproduce el GLB V3.1 bit a bit (sha `dce47ae8…`).
- La iluminación y los materiales del estadio. Ninguna mejora de este informe viene de luz o materiales:
  - el test A compara el movimiento con materiales neutros sobre la misma malla;
  - el test B compara la malla con el mismo movimiento.
