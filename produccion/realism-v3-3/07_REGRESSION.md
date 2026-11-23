# Realism V3.3 — 07 REGRESIÓN (Legacy / V3.1 / V3.2 intactos)

## Método
- Mismas props V3.2 (`rv32-abc`, que muestra Legacy, V3.1 y V3.2 en tres paneles, y `rv32-testA`, Legacy + V3.2).
- Se renderiza cada fotograma dos veces con `npx remotion still`, mismos flags (`--gl=swangle`):
  1. bundle de la rama `claude/realism-v3-3` (V3.3 integrada);
  2. bundle de la base `claude/realism-v3-2` @ 28b06ea (worktree aparte).
- Comparación píxel a píxel en RGB (numpy) y MD5 de los PNG.

## Resultado

| Props | Fotograma | Renderers en pantalla | Diferencia máxima | Píxeles distintos | MD5 idéntico |
|---|---|---|---|---|---|
| rv32-abc | 60 | Legacy · V3.1 · V3.2 | 0 | 0 | Sí |
| rv32-abc | 200 | Legacy · V3.1 · V3.2 | 0 | 0 | Sí |
| rv32-abc | 330 | Legacy · V3.1 · V3.2 | 0 | 0 | Sí |
| rv32-testA | 120 | Legacy · V3.2 | 0 | 0 | Sí |

**PASS: los tres motores anteriores dan píxeles idénticos con y sin V3.3.** El valor por defecto de `athleteRenderer` sigue siendo `legacy`. V3.3 solo se activa con `athleteRenderer: "v33"`.

Hashes en `qa/regression/md5.txt`. Los PNG no se versionan (binarios).

## Otras comprobaciones
- `npx tsc --noEmit`: OK.
- `scripts/smoke-realism.sh`: exit 0 (`qa/smoke-realism.txt`). Las líneas FAIL informativas de las puertas V2 ya existían antes de V3.3.
- `scripts/test-play.mts` sobre la jugada 5v5 nueva: 23/23 PASS.

## Límite
Son 4 fotogramas de 2 escenas, no un render completo de cada episodio antiguo. El cambio de código en las rutas compartidas (`Scene.tsx`) se limita a ramas `av33`, que con renderer distinto de `v33` no se ejecutan.
