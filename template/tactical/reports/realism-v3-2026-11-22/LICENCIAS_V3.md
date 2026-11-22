# Realism V3: matriz de licencias

Ningún activo procede de juegos (no hay rips) ni reproduce la imagen de jugadores reales. Los dorsales son números genéricos y la cara está neutralizada.

| Activo | Origen | Licencia | Uso comercial | Dónde está | Verificado |
|---|---|---|---|---|---|
| Malla base humana + morph targets | MakeHuman, vía npm `ara3d-data 1.1.0` | CC0-1.0 | Sí | entrada de `tools/blender/mh_body.py` / `build_player.py` | Sí: paquete npm con licencia CC0 (comprobado en `claude/lab-mpfb-default-player`) |
| Esqueleto de 27 huesos (21 + dedos) y pesos | E2A (`tools/blender/skeleton.py`); pesos transferidos de los grupos CC0 de MakeHuman | Propio | Sí | `skeleton.py`, `build_player.py` | Sí |
| Correctivos (rodilla, codo, cadera) | E2A, generados por código (delta-mush) | Propio | Sí | shape keys en los GLB `_v3` | Sí |
| Camiseta, shorts, ribetes, calcetines, zapatillas | E2A, geometría generada por código | Propio | Sí | `build_player.py --garment v3` | Sí |
| Textura de camiseta (dorsal) | E2A, canvas generado en tiempo de render | Propio | Sí | `SkinnedAthlete.tsx` `jerseyTextureV3` | Sí |
| Fuente del dorsal | Anton (Google Fonts) | SIL OFL 1.1 | Sí | `config/asset_licences.json` → `anton.woff2` | Sí: ya está en el registro |
| Pista, gradas, luces | Procedural E2A | Propio | Sí | `config/asset_licences.json` → `3d/procedural` | Sí: ya está en el registro |
| GLB `e2a_player_{off,def}_v3.glb` | build de los anteriores | CC0 + propio | Sí | `template/public/players3d/` + `.provenance.json` (sha256) | Sí |

**Hueco registrado (no corregido en esta pasada):** las procedencias usan `licence_key: 3d/e2a-player-makehuman-cc0`, pero `config/asset_licences.json` solo contiene `3d/procedural`.

**Acción propuesta:** añadir esta entrada:

```json
"3d/e2a-player-makehuman-cc0": {
  "origin": "MakeHuman base mesh (ara3d-data 1.1.0) + E2A clothes/rig",
  "licence": "CC0-1.0 + E2A",
  "commercial_use": true
}
```

No se ha añadido porque ese registro lo comparten otras ramas y producción. Basta con un cambio de una línea en un PR aparte.

**No se usa:** MPFB2 (descarga bloqueada), packs de terceros, Mixamo, capturas de movimiento externas, ElevenLabs ni ningún servicio de pago.
