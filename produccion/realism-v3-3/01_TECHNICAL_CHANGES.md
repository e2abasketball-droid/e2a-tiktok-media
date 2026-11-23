# Realism V3.3 — 01 TECHNICAL CHANGES

## Arquitectura antes → después
| | V3.2 | V3.3 |
|---|---|---|
| Quién define el cuerpo | Clip escrito a mano por jugada (`clips32.ts`) para 1–3 jugadores. El resto usa el motor legacy. | **Compilador de eventos** (`compile33.ts`): deriva el guion de cada jugador a partir de la jugada (pistas, balón, acciones, marcas). Los clips V3.2 se siguen admitiendo como scripts de compatibilidad. |
| Balón | Dos fuentes: el motor (`sample().ball`) y el socket de la mano | **Una sola fuente**: `ballV33(play, t)`. Vuelos balísticos entre puntos de suelta y recepción derivados de los cuerpos; pase picado con dos arcos; hand-off; bote multi-rebote. El renderer y el QC leen la misma función. |
| Contacto balón-cuerpo | Ninguno; el balón cruza el tronco | **Solver anatómico suave** (softplus 1 cm) con volúmenes medidos en la malla (`anat33.ts`): tronco elíptico, cabeza y muslos. Las manos se mueven con el balón. |
| Bote | Un solo bote fijo | Bote multi-rebote con física (bajada, rebote, ascenso), cadencia según la velocidad, mano en los dos tramos |
| Tiro | Fases fijas de 1,05 s | Tiempos adaptados a la jugada (recepción → tiro), tiro rápido con salto bajo, parada 1-2 antes de saltar |
| Rendimiento del QC | 4 min 47 s por one-take | ≈2 s (memoización de pies y cuerpo en una rejilla de 10 ms y oscilador de tela precalculado) |

## Archivos tocados
**Nuevos** (no tocan nada existente):
- `template/src/t3d/realism-v3-3/library33.ts`: biblioteca de primitivas, copia de `library.ts` con añadidos:
  - postura de bloqueo;
  - `dribbleRun`;
  - estilos de pase y recepción;
  - perfiles de cuerpo;
  - `windowsOf`;
  - tiro rápido (`armT`, `quick`).
- `template/src/t3d/realism-v3-3/motion33.ts`: cuerpo, pies, brazos, balón, solver de contacto, tela L1 y estados del balón.
- `template/src/t3d/realism-v3-3/compile33.ts`: compilador de eventos → guion por jugador.
- `template/src/t3d/realism-v3-3/clips33.ts`: origen de cada jugador (compilado, compatibilidad o ninguno).
- `template/src/t3d/realism-v3-3/scene33.ts`: `athleteV33`, la entrada única para renderer y QC.
- `template/src/t3d/realism-v3-3/anat33.ts`: radios anatómicos medidos con bpy en la GLB V3.2 (P50 de la distancia al eje del hueso).
- `template/src/t3d/realism-v3-3/index.ts`
- `template/scripts/qc-realism-v33.mts`: copia del QC V3.2 con los detectores originales intactos. Añade:
  - detector anatómico clasificado;
  - CSV por frame;
  - `--rig`;
  - `--dump`.
- `template/scripts/qc-determinism-v33.mts`: orden ascendente, descendente y aleatorio, en frío y en caliente.
- `template/scripts/qc-cloth-l2-v33.mts`: carga en three.js del bake L2.
- `template/scripts/_probe33.mts`, `_compile-dump33.mts`: diagnóstico, no forman parte del QC.
- `template/tactical/specs/_gen-realism-v3-3-5v5.py` → `tactical/plays/realism-v3-3-5v5.json`: la jugada 5v5 de prueba.
- `template/tactical/episodes/_gen-realism-v3-3.py`: props de los renders de prueba.
- `template/public/tactical/realism-v3-3/silence.mp3`: pista silenciosa de 20 s. Los renders son mudos, pero la composición exige un archivo de voz.
- `tools/blender/cloth_bake_l2_v33.py`, `template/tools/blender/measure_anat_v33.py`.

**Modificados** (solo para añadir la opción; Legacy sigue por defecto):
- `template/src/t3d/realism-v3/index.ts`: `AthleteRenderer` acepta `'v33'` y se añade `isV33`.
- `template/src/t3d/Scene.tsx`:
  - rama `av33`;
  - GLB V3.2 para v33;
  - `ballPos = ballV33(...)` solo si es v33.
  - Las ramas legacy, v3, v31 y v32 no cambian (regresión en 07).

No se ha tocado nada de V3.1 ni de V3.2: `realism-v3-1/`, `realism-v3-2/`, sus QC y sus jugadas.

## Decisiones y por qué
1. **Copias, no ediciones, de la biblioteca V3.2.** El brief exige conservar V3.1 y V3.2. Copiar `library.ts` y `motion32.ts` a V3.3 deja V3.2 congelada y comparable.
2. **Balón como función pura de la jugada.** Es la única manera de que el render y el QC midan lo mismo y de que el resultado sea idéntico al saltar frames.
3. **Solver suave (softplus) en lugar de un empujón duro.** El empujón duro provocaba tirones de muñeca de 600–900 m/s². El suave es C∞ en la posición del balón.
4. **Volúmenes medidos, no inventados.** Los radios del tronco salen de la malla (bpy, `tools/blender/measure_anat_v33.py`). Los brazos se excluyen del solver: van con el balón.
5. **Compilador antes que clips a mano.** El brief exige cubrir 10 jugadores sin keyframes manuales por jugada. El 5v5 tiene 10/10 jugadores compilados y ningún guion escrito a mano.
6. **Sin variables de entorno de ajuste.** Todas las constantes son fijas; se comprobó con grep `process.env` en `realism-v3-3/` y no hay ninguna.

## Correcciones de la segunda pasada (con la causa medida)
| Defecto (QC) | Causa | Arreglo |
|---|---|---|
| Tirón de muñeca 645 m/s² en la suelta del pase (trío 2,70 s) | La corrección de palma se apagaba de golpe (palma → null) | La palma se mantiene y su peso `pw` se desvanece |
| Muñeca 744 m/s² en el tiro (trío 4,75 s) | La mano guía soltaba la palma de golpe (rel > 0,85) | Desvanecimiento `pw` de 0,6 a 0,95 |
| Muñeca 441 m/s² en la suelta del tiro | La mano se paraba en seco en el punto de suelta | Acompañamiento: la mano sigue la trayectoria de lanzamiento y frena en 0,18 s |
| Cadera en la V-cut (trío 1,43 s) | El vaivén de reposo se activaba 50 ms al pasar la velocidad por 0 | `still` usa la velocidad máxima entre t−0,3 y t+0,3 |
| Bote (5v5 O1), 450–670 m/s² en cada bote | La palma se encendía y apagaba en cada toque | La mano sigue su trayectoria de palma en las dos fases |
| Defensores (5v5) con caderas a 150–490 m/s² | Desplazamiento lateral a 2,8 m/s durante 7 m y cambios lateral → carrera cada 0,4 s | Lateral solo hasta 1,8 m/s, de espaldas hasta 2,6 m/s, tramos de 0,6 s como mínimo |
| Tiro tras hand-off (5v5 O2), 3,5 km/s² | Los pasos de carrera se solapaban con el despegue y las fases del tiro quedaban desordenadas | Parada 1-2 compilada antes del despegue, tiro rápido (H 0,22 m, `armT`), trayectoria recepción → set directa |
| Mano a 40 cm en un frame (5v5 O2 6,18 s) | El solver usaba cápsulas de brazo con el codo aparcado a −50 m | Brazos excluidos del solver |
| Mano en el hand-off, 1 km/s² | Objetivo fijo del balón presentado, alcanzado desde una carrera a 3,6 m/s | El objetivo sigue el balón presentado en el instante t |
| Escalón de cadera en el despegue | El límite de pierna en suelo y en el aire cambiaba de golpe | Transición de 0,1 s entre los dos límites |
| Cabeza 2,4 cm en un frame | La mirada «balón propio» cambiaba de golpe a 0,5 m | Mezcla entre 0,3 y 0,7 m |
