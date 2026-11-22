# E2A Realism V3.2: integración

Fecha: 22-11-2026. Rama `claude/realism-v3-2` (desde `claude/realism-v3-1`, `e014de3`).

## 1. Interruptores (episodio, shot, panel)

| Clave | Valores | Por defecto | Efecto |
|---|---|---|---|
| `athleteRenderer` | `legacy` · `v31` · `v32` | `legacy` | Legacy no cambia (mismos píxeles, ver QA.md). `v31` es la entrega V3.1 sin cambios. `v32` usa la malla V3.2 y el movimiento de la biblioteca V3.2 |
| `athleteMotion` | `engine` · `v31` · `v32` | `v32` | Solo con `athleteRenderer: 'v32'`. Elige el generador de movimiento sobre la malla V3.2. Sirve para el test A (solo movimiento) |
| `athleteMesh` | `v31` · `v32` | `v32` | Solo con `v32`. Elige malla y ropa. Sirve para el test B (personaje y tela) |
| `neutral` | `true` | — | Materiales grises neutros por pieza (test A). No toca la geometría |
| `debug32` | `true` | — | Discos de pie (verde = apoyado, rojo = en el aire), esferas en las palmas y un halo del balón con el color de su estado |
| `panels` | `Panel3[]` | — | N vistas 3D apiladas a la misma altura, con el mismo reloj. Cada panel admite los interruptores de arriba. Sin `panels`, el shot se pinta igual que antes |

Un jugador sin clip V3.2 (los extras de una jugada) usa con `v32` la pose del motor sobre la malla V3.2: es el puente V3. Ningún episodio existente cambia porque ninguno declara `v32`.

## 2. Cómo se mueve un jugador V3.2

1. `realism-v3-2/clips32.ts` es el **guion**: unas pocas primitivas por jugador, con tiempos tomados de la jugada (`play.marks`, eventos de balón).
   - Primitivas: `stand`, `move` (`run` / `shuffle` / `backpedal` / `closeout`), `plant`, `step`, `pivot`, `catch`, `dribble`, `pass`, `jumpshot`.
   - Cada jugador tiene una semilla (variación de tiempo y amplitud).
2. `realism-v3-2/library.ts` (`buildClip`) convierte el guion en canales:
   - rumbo, con un límite de giro de 6 rad/s centrado;
   - pasos, con la cadencia de la velocidad del track y despegue por alcance;
   - inclinación, bajada y anchura de la postura, con paso bajo de ±0,24 s;
   - brazos, donde las ventanas con balón mandan;
   - mirada y balón.
3. `realism-v3-2/motion32.ts` (`motionV32`, `framesV32`) evalúa el clip en t:
   - pies;
   - pelvis, con la envolvente de alcance de pierna;
   - ciclo del tiro en suspensión acoplado a piernas y brazos;
   - palmas en el balón;
   - corrección de las palmas sobre la malla;
   - pie y puntera (la zapatilla V3.2 flexiona en la bola del pie).
4. `realism-v3-2/scene32.ts` (`athleteV32`) es el único punto de entrada. Lo usan:
   - `Scene.tsx` (render);
   - `scripts/dump-frames-v32.mts`, que alimenta el QC de tela;
   - `scripts/qc-realism-v32.mts`, el QC de movimiento.

   Lo que se mide es lo que se pinta.

## 3. Añadir un jugador o una jugada

1. La jugada (`tactical/plays/*.json`) debe tener tracks y eventos de balón; los tiempos clave van en `marks`.
2. Se escribe el guion del jugador en `clips32.ts`, en `trio(play)`, como modelo.
   - Los tiempos se toman de `marks`, nunca se teclean frames.
3. Se registra la jugada en `clip32For`.
   - Una copia de benchmark puede reutilizar un guion con `v32clip: {"<id>": "<play>:<jugador>"}`.
4. Se valida antes de renderizar:
   - `npx tsx scripts/qc-realism-v32.mts <play> --players ... --motion v32`;
   - umbrales en QA.md.
5. Se renderiza con `athleteRenderer: 'v32'`.

## 4. Assets

- Malla V3.2: `public/players3d/e2a_player_{off,def}_v32.glb`. Cada una tiene su `.provenance.json` (CC0 MakeHuman/ara3d, todo lo demás hecho por E2A).
- Rigs: `src/t3d/realism-v3-2/rigs/e2a-{off,def}-v32.rig.json`.
- Build: `tools/blender/build_player.py --rig v3 --garment v32 --body v31 --shoe v32 --variant off|def`.
  - Las opciones `v31` siguen produciendo el GLB V3.1 bit a bit: sha `dce47ae8…`, recompilado y comprobado.

## 5. Límites conocidos

Detalle y medidas en AUDIT.md y QA.md.

- Solo hay guiones para el one-take (O1) y el trío (O1, O2, X2). Los demás jugadores usan el puente.
- La tela sigue siendo un muelle procedural en el shader más correctivos. No es simulación: L2 no se reintentó en V3.2.
- Render por CPU (SwiftShader): no se afirma tiempo real.
