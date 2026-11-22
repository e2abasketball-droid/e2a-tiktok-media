# E2A Realism V3: auditoría de fase cero (§2)

Fecha: 22-11-2026. Rama de trabajo: `claude/realism-v3`, creada desde `claude/chicago-v3` en `4682d58`.

## 1. Entorno (medido)

| Recurso | Valor real | Consecuencia |
|---|---|---|
| CPU | 4 núcleos, sin GPU (render por software: Chromium headless + `--gl=swangle`) | Todo render es CPU; los tiempos del benchmark son de CPU |
| RAM | 15 GB (13 GB libres al empezar) | Suficiente para 4 pestañas de render concurrentes |
| Disco | ~5,2 GB libres de 252 GB (tras limpiar scratch) | Hubo que borrar bundles y vídeos temporales antiguos; no se guardan PNG sueltos |
| Node | v22.23.4; Remotion 4.0.539; three.js (repo) | Igual que en producción |
| Python | 3.13.18; numpy; PIL | Scripts de QA y contact sheets |
| Blender | **sin binario**; `bpy` 5.3 como módulo en el venv `/tmp/claude-0/venv3d` | Build de personaje sin interfaz (~5 s por variante). Sin Draco ni meshopt (avisos inocuos: no se usan) |
| MPFB2 / MakeHuman | descarga bloqueada (403, ya comprobado en `claude/lab-mpfb-default-player`) | Se usa la malla base MakeHuman CC0 de npm `ara3d-data 1.1.0` |
| Red | proxy con lista blanca; sin servicios de pago | 0 € de gasto. ElevenLabs no se usa (no hay voz) |

## 2. Repositorio

- Repo: `e2abasketball-droid/e2a-tiktok-media`.
- SHA base: `4682d58` (`claude/chicago-v3`, "Chicago Action V3 (Reel) + Realism V2 (trial)").
- `main` = `b3f0321`. No se ha tocado.

Ramas consultadas:

| Rama | SHA | Uso |
|---|---|---|
| `claude/lab-mpfb-default-player` | `aefe3cf` | Origen de `build_player.py`, `skeleton.py` y del registro de clips. Ya estaba integrada en la base |
| `claude/lab-skeletal-screen-roll` | `94d84d0` | Consultada. No hace falta para el one-take (clips de bloqueo) |

PRs consultadas (`gh api`, 22-11-2026):

| PR | Estado | Título | Acción |
|---|---|---|---|
| #12 | abierta, draft, sin fusionar (head `fb41445`) | Tactical Studio V4 (sombra) | No tocada |
| #13 | abierta, sin fusionar (head `d1d44b7`) | Subagente e2a-3d-animation + herramienta de referencias de vídeo | No tocada ni fusionada. Sin solape de archivos con esta rama |

## 3. Qué es "legacy" en esta base

En `4682d58` los atletas por defecto son ya `e2a-player-v1`:
- malla MakeHuman CC0 con 21 huesos;
- `players3d/e2a_player_{off,def}.glb`;
- ropa `_v2` cuando el episodio pide realismo 2 o 3.

Los muñecos procedurales (`Athlete.tsx`) solo se usan como fallback.

**Baseline legacy = el renderer de producción actual de esta base, no los muñecos.** Así el A/B no compara contra algo deliberadamente peor.

## 4. Mapa de interfaces (dónde entra V3)

```
play JSON (tracks, ball events, actions)        ← sin cambios
   └─ rig.ts poseAt()  → Pose (articulaciones)  ← sin cambios (mismo solver para ambos)
        ├─ legacy: skelclip.bonesFromPose()  → SkinnedAthlete (21 huesos)
        └─ v3:     realism-v3/athleteV3.bonesV3() = bonesFromPose() + corrección de cabeza + dedos con agarre
                                                   + pesos de correctivos → SkinnedAthlete (27 huesos, morphs, v3)
Scene3D(athleteRenderer) ← Tactical3D: episode.athleteRenderer / shot.athleteRenderer / split.athleteRenderer
```

- Flag `athleteRenderer`:
  - valor por defecto `'legacy'` (`realism-v3/index.ts`);
  - si no se declara, el código sigue exactamente el camino anterior.
- Jugadores con clip esquelético (`spec`): siguen en legacy aunque el flag sea `v3`. Es una limitación documentada.

## 5. Bloqueos detectados en la auditoría

1. Sin MPFB2: no hay ropa MakeHuman ni rig "game engine". Se construyen la ropa y el rig propios (`build_player.py`).
2. Sin GPU: el render 3D es lento y el benchmark lo refleja.
3. Sin simulación de tela offline (Blender cloth necesita bake y binario/tiempo). Se hace así:
   - tela determinista en el motor (`cloth2`, muelle analítico);
   - shape keys correctivos horneados.
4. Sin captura de movimiento ni biblioteca de clips con licencia clara: las poses salen del solver procedural del motor (`rig.ts`).
5. `config/asset_licences.json` no tiene la clave `3d/e2a-player-makehuman-cc0`, que sí usan las procedencias de los GLB. Ver `LICENCIAS_V3.md`.
