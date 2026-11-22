# E2A Realism V3: entrega (§15)

Fecha: 22-11-2026.

- Rama: `claude/realism-v3`, creada desde `claude/chicago-v3` en `4682d58`. El commit de entrega está al final de este documento.
- Gasto: 0 €. No se ha usado ElevenLabs ni ningún servicio de pago. No se ha publicado ni programado nada.
- No se han tocado Metricool, `main` ni las PR #12/#13. No hay merges.

## Resumen

| Pregunta | Respuesta |
|---|---|
| ¿Qué es V3? | Un renderer de atleta opcional: `athleteRenderer: 'v3'`, por episodio, plano o split. Usa la misma jugada y las mismas poses del motor, y añade 27 huesos con dedos, correctivos, ropa nueva, agarre del balón y una capa de peso |
| ¿Qué pasa con lo que ya existe? | El valor por defecto es `'legacy'`. Lo existente queda idéntico a nivel de píxel, comprobado |
| ¿Hay one-take? | Sí: 12,5 s sin cortes, legacy y V3 con la misma cámara, más dos split-screen y un primer plano |
| ¿Cuál es el estado real? | Mejoras medibles en dedos, ropa, dorsal y peso en la frenada. Con la cámara abierta, legacy y V3 se distinguen poco. Siguen abiertos: aspecto de maniquí (cara, piel), glúteo marcado en cuclillas y contacto palma–balón (lo pone el motor). **No es fotorrealista ni está listo para producción** |

## Tabla de componentes

| Componente | Estado | Ruta real | Prueba o artefacto | Limitación |
|---|---|---|---|---|
| Auditoría de entorno, SHA, PR y bloqueos | HECHO | `REALISM_V3_AUDIT.md` | `gh api` de PR #12/#13, inventario medido | — |
| Matriz de licencias | HECHO | `LICENCIAS_V3.md` | Procedencia sha256 en `assets/*.provenance.json` | Falta en `config/asset_licences.json` la clave `3d/e2a-player-makehuman-cc0` (propuesta incluida, sin aplicar) |
| Personaje V3: build en Blender (bpy), 27 huesos con dedos | HECHO | `tools/blender/build_player.py --rig v3 --garment v3`, `tools/blender/skeleton.py` (`enable_fingers`) | `assets/e2a_player_{off,def}_v3.{glb,blend}` y `.rig.json`; Gate A | Sin MPFB (descarga 403): malla base MakeHuman CC0, cara neutra |
| Correctivos de rodilla, codo y cadera (delta-mush → morph targets) | HECHO | `build_player.py` (`corrective`, `transfer_corrective`); pesos en runtime en `athleteV3.ts` | 6 morphs por GLB; pesos medidos en `qa/qc-realism-v3.json` | Cadera solo en cuerpo + shorts; la camiseta no lleva correctivo |
| Camiseta V3 (cae desde los hombros, se estrecha, sin aro en el bajo, Taubin + Fourier) | PARCIAL | `build_player.py` (bloque GV3 jersey) | Gate D: número ×1,61 (legacy ×1,72); `contact_hero_v3.jpg` | Sin simulación de tela: se lee más ajustada que una camiseta de baloncesto real |
| Shorts V3 (tubo por pierna, perneras holgadas con tela cloth2, asiento con puente) | PARCIAL | `build_player.py` (bloque GV3 shorts) + `SkinnedAthlete.tsx` (rama v3) | Gate D; `qa/sprint_fix_before_after.jpg` | Glúteo todavía marcado en cuclillas; shorts atraviesan la camiseta 2,7 cm @3,33 s |
| Textura de dorsal V3 (2048×1024, keyline) | HECHO | `SkinnedAthlete.tsx` `jerseyTextureV3` | `qa/captures_legacy_vs_v3.jpg` | — |
| AthleteV3: puente pose → huesos (cabeza, dedos, morphs, peso) | HECHO | `template/src/t3d/realism-v3/athleteV3.ts`, `index.ts` | `scripts/qc-realism-v3.mts`, seek test | Función pura; los jugadores con clip esquelético siguen en legacy |
| Envoltura de dedos sobre el balón (búsqueda 2-D) | PARCIAL | `athleteV3.ts` `solveCurl` | Mediana \|punta–superficie\| 38,2 → **7,4 mm**; 17/28 frames ≤ 10 mm; pulgar −39,9 → +0,4 mm | La palma la coloca el motor, 1,7 cm dentro del balón (mediana); no hay IK de muñeca |
| Peso en frenada y corte (cadera baja, tronco inclinado, IK de piernas) | PARCIAL | `athleteV3.ts` `weightShift` / `applyWeight` | Caída máx. 6,0 cm, inclinación máx. 11,5°; foot_plant sin cambios (4,4 cm); `qa/brake_weight_sbs_close.jpg` | Visible en la deceleración (2,2–2,6 s), no en el apoyo del corte (3,3 s) |
| Flag `athleteRenderer` en Tactical3D / Scene3D | HECHO | `Tactical3D.tsx`, `Scene.tsx` | `tsc` rc 0; píxeles legacy 8/8 idénticos | — |
| Fixture one-take (12,5 s) + generador de props | HECHO | `tactical/specs/_gen-realism-v3-onetake.py`, `tactical/plays/realism-v3-onetake.json`, `tactical/episodes/_gen-realism-v3-onetake.py` | `test-play` 12/13 (el 5v5 no aplica), `test-motion` 7/7 | `catchV2` retirado por una discontinuidad del motor (incidencia 2) |
| `baseline_legacy.mp4` | HECHO | `baseline_legacy.mp4` | 1080×1920, 30 fps, 375 frames, 12,5 s | — |
| `prototype_v3.mp4` | HECHO | `prototype_v3.mp4` | Ídem | — |
| `side_by_side.mp4` (cámara del one-take) | HECHO | `side_by_side.mp4` | Split sincronizado LEGACY arriba / V3 abajo | Con esta cámara abierta la diferencia apenas se ve |
| `side_by_side_close.mp4` (3/4 cercano, misma cámara) | HECHO | `side_by_side_close.mp4` | `contact_sheets/contact_sbs_close.jpg` | El cuerpo ocupa ~50–55 % de cada mitad, no el 60 % pedido |
| `hero_jersey_closeup.mp4` (+ versión legacy) | HECHO | `hero_jersey_closeup.mp4`, `hero_jersey_closeup_legacy.mp4` | `contact_hero_*.jpg` | En el release (7,87 s) la cámara corta la cabeza |
| Contact sheets y capturas con tiempos | HECHO | `contact_sheets/`, `qa/captures_legacy_vs_v3.jpg`, `qa/brake_weight_sbs_close.jpg` | Frame y PTS del MP4 exportado | — |
| Seek test 301 → 12 → 129 → 12 | HECHO | `qa/seek.txt` | f12 con sha idéntico las dos veces; en frío frente a secuencia: ≤ 12 píxeles de fondo distintos | Determinismo de swangle no bit a bit en gradas y suelo |
| QA gates A–E | HECHO (gates C y D en FAIL) | `QA_REPORT.md`, `qa/` | Números reales | Los FAIL de contacto y ropa se comparten con legacy (motor) |
| Benchmark 1/2/5/10 atletas | HECHO | `QA_REPORT.md`, `qa/benchmark.txt` | 10 atletas: V3 +22 % de tiempo frente a legacy | RSS medido a nivel de sistema; no hay GPU ni VRAM |
| LOD mid/far, clips V3, 2 jugadores con DHO (3ª pasada), 10 jugadores en producción (4ª) | BLOQUEADO / NO INICIADO | — | — | Fuera de esta sesión (ver próximos pasos) |
| Cara, piel y pelo realistas | BLOQUEADO | — | — | Sin MPFB ni assets de piel con licencia; no se usan rips |

## Archivos modificados y por qué

| Archivo | Cambio |
|---|---|
| `tools/blender/skeleton.py` | Huesos de dedos opcionales (`enable_fingers`). Por defecto, sin cambios |
| `tools/blender/build_player.py` | `--rig v3`, `--garment v3`: correctivos, camiseta y shorts V3, atributos de tela, sin aro en el bajo, rig JSON con `fingers` y `correctives`. `--garment v2` sigue dando el mismo sha (`f46cb06d…`) |
| `template/src/t3d/realism-v3/athleteV3.ts`, `index.ts`, `rigs/*.rig.json` | AthleteV3: dedos, cabeza, morphs, capa de peso; flag y manifiesto |
| `template/public/players3d/e2a_player_{off,def}_v3.glb` + `.provenance.json` | GLB V3 con sha256 y procedencia |
| `template/src/t3d/SkinnedAthlete.tsx` | Textura de dorsal V3, morphs por nombre, rama de shorts V3 con tela cloth2 |
| `template/src/t3d/Scene.tsx`, `Tactical3D.tsx` | Flag `athleteRenderer` (episodio, plano, split) y rama V3 |
| `template/scripts/qc-realism.mts` | Modo `--v3`: mallas V3, `bonesV3`, capa de peso, morphs; lee accessors sparse |
| `template/scripts/qc-realism-v3.mts` | QA nuevo: dedos legacy frente a V3, pesos de correctivos, capa de peso |
| `template/tactical/specs/_gen-realism-v3-onetake.py`, `plays/realism-v3-onetake.json`, `specs/realism-v3-onetake.spec.json`, `episodes/_gen-realism-v3-onetake.py` | Fixture del one-take y props de render (los props se generan fuera del repo) |
| `template/tactical/reports/realism-v3-2026-11-22/` | Copia de este informe y de las salidas de QA (texto) |

## Comandos exactos y resultados

```bash
# build V3 (unos 5 s por variante; bpy 5.3 en venv, sin binario de Blender)
/tmp/claude-0/venv3d/bin/python -I tools/blender/build_player.py -- --variant off --rig v3 --garment v3 \
  --out-blend <dir>/e2a_player_off_v3.blend --out-glb <dir>/e2a_player_off_v3.glb --out-rig <dir>/e2a-off-v3.rig.json
#   -> corrective knee 4.76 cm, elbow 2.48 cm, hip 2.09 cm; shorts hip 2.37 cm; seat bridge 3.0 cm; glb 1 471 924 B
# legacy sigue determinista
build_player.py -- --variant off --garment v2 ...   # sha256 f46cb06d2489… (igual antes y después)

# props y render (sin audio)
python3 tactical/episodes/_gen-realism-v3-onetake.py /tmp/claude-0/rv3/props
npx remotion bundle --out-dir <bundle>
npx remotion render <bundle> Tactical3DV2 out.mp4 --props=<props>/rv3-v3.props.json --gl=swangle --muted --concurrency=4
#   (rv3-legacy, rv3-v3, rv3-sbs, rv3-sbs-close, rv3-hero-v3, rv3-hero-legacy, rv3-bench-{1,2,5,10}-{legacy,v3})

# QA
npx tsc --noEmit -p .                                              # rc 0
npx tsx scripts/regress-poses.mts                                  # 12/12 idénticas
npx tsx scripts/regress-poses.mts --ref tactical/reports/chicago-v3-2026-11-22/regression-hashes-rv2.json   # 2/2
npx tsx scripts/qc-realism.mts tactical/plays/realism-v3-onetake.json [--v3]
npx tsx scripts/qc-realism-v3.mts
npx tsx scripts/test-play.mts tactical/plays/realism-v3-onetake.json   # 12/13 (5v5 no aplica)
npx tsx scripts/test-motion.mts tactical/plays/realism-v3-onetake.json # 7/7
npx tsx scripts/test-ball.mts tactical/plays/realism-v3-onetake.json   # 6/7 (mano 0,288 m @7,27 s, motor)
# píxeles legacy: bundle de git archive 4682d58 frente al bundle final -> 8/8 sha idénticos (qa/pixel-regression.txt)
python3 scripts/contact-sheet-pts.py video.mp4 out.jpg 6 <tiempos...>
```

## Baseline y V3: rutas

Todas en `/mnt/project-files/tactical-studio/realism-v3/`:
- `baseline_legacy.mp4`
- `prototype_v3.mp4`
- `side_by_side.mp4`
- `side_by_side_close.mp4`
- `hero_jersey_closeup.mp4`
- `hero_jersey_closeup_legacy.mp4`

Los seis: 1080×1920, 30 fps, 375 frames, 12,5 s, sin audio.

Nota sobre las copias: el almacenamiento compartido reescribe el contenedor MP4 (unos 6 KB), pero el vídeo decodificado es idéntico (mismo md5 de frames).

## Capturas con marca de tiempo

| Qué | Archivo | Tiempos |
|---|---|---|
| Pies | `contact_sheets/contact_sbs_close.jpg` | 0,5 / 2,4 / 3,3 / 10,5 / 11,0 s |
| Manos | `qa/captures_legacy_vs_v3.jpg` | bote 6,000 s, gather 7,133 s, recepción 4,667 s |
| Camiseta y espalda | `qa/captures_legacy_vs_v3.jpg`, `contact_hero_*.jpg` | 3,300 s |
| Cuerpo entero | `contact_v3.jpg`, `contact_legacy.jpg` | 12 tiempos |
| Tiro | `contact_hero_*.jpg`, `qa/captures_legacy_vs_v3.jpg` | 7,867 s |
| Frenada / peso | `qa/brake_weight_sbs_close.jpg` | 2,333 / 2,500 / 3,300 s |

## Métricas: resumen

El detalle está en `QA_REPORT.md`.

**Por jugador.** V3 off: 28 662 triángulos, 15 580 vértices, 8 materiales, 2 texturas, 27 huesos, 6 morphs, 11 draw calls, 1,47 MB. Legacy off: 29 318 triángulos, 21 huesos, 0 morphs, 1,32 MB.

**Render, 60 frames.**

| Atletas | Legacy | V3 |
|---|---|---|
| 1 | 112,8 s | 114,8 s |
| 2 | 112,5 s | 119,6 s |
| 5 | 132,0 s | 145,2 s |
| 10 | 156,9 s | 191,4 s |

**Memoria del render.** Unos 3,1 GB con 1 atleta legacy y unos 4,2 GB con 10 V3: RSS del sistema menos 2,7 GB de procesos en reposo.

## Qué se integró, qué queda tras el flag y cómo volver atrás

- **Integrado (inactivo por defecto):**
  - el código V3 en `src/t3d/realism-v3/`;
  - la rama en `Scene3D`;
  - el flag en `Tactical3D`;
  - el modo `--v3` de qc-realism;
  - el QA `qc-realism-v3`.
- **Tras el flag:** todo lo visual de V3, con `athleteRenderer: 'v3'` en el episodio, el plano o el split. Ningún episodio existente lo declara.
- **Rollback:** no declarar el flag, o poner `'legacy'`. Los GLB y el código legacy no se han modificado: hashes de pose 14/14 y píxeles 8/8 idénticos. Para retirarlo del todo basta con revertir el commit.

## Matriz de incidencias y QC

La matriz completa, con 10 filas, está en `QA_REPORT.md`. Las principales:

| # | Incidencia | Estado |
|---|---|---|
| 1 | Hueco del muslo al esprintar | Arreglado, 17,1 → 1,6 cm |
| 2 | Discontinuidad de `catchV2` en el motor | Abierta |
| 3 | Glúteo marcado | Parcial |
| 4 | Palma dentro del balón (motor) | Abierta |
| 5 | Roce del balón con la cabeza 2,1 cm (V3) | Abierta |
| 6 | Shorts atraviesan la camiseta 2,7 cm | Abierta |
| 7 | Sin peso en el apoyo del corte | Abierta |
| 8 | Aspecto de maniquí | Bloqueada |

## Próximos pasos (por impacto técnico)

1. **IK de muñeca V3 contra la superficie del balón.** Corrige la palma dentro del balón y la mano separada en el gather, que es el mayor FAIL compartido. Con eso el agarre 2-D ya existente cerraría el gate C.
2. **Tela simulada horneada (Blender cloth) para camiseta y shorts en planos hero,** o un muelle por vértice en el motor. Es lo único que dará caída real (camiseta holgada sin efecto caja) y eliminará el glúteo marcado. Requiere un binario de Blender o tiempo de bake: aquí solo hay bpy.
3. **Término de carga en el apoyo** (eventos de pie del motor) para la capa de peso: el corte a 3,3 s todavía no transmite peso.
4. **Cara, piel y pelo:** pipeline MPFB2 cuando la descarga sea posible, o escaneos CC0 revisados. Es el motivo principal del aspecto de maniquí a distancia.
5. **Retarget de clips esqueléticos a 27 huesos,** para que los jugadores con `spec` también puedan ir en V3.
6. **LOD mid/far** (sin dedos ni morphs a distancia). Con 10 atletas V3 cuesta un 22 % más, así que el LOD lo recuperaría.
7. **Tercera pasada (2 jugadores, DHO) y cuarta (10 atletas),** antes de proponer V3 por defecto.
8. **Registrar la licencia `3d/e2a-player-makehuman-cc0`** en `config/asset_licences.json`, en un PR aparte.

## Commit

COMMIT_LINE
