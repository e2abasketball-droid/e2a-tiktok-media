# Realism V3.3 — Manifest de assets y licencias

| Archivo nuevo | Origen | Licencia / derechos |
|---|---|---|
| `template/public/tactical/realism-v3-3/silence.mp3` | Generado con ffmpeg (`anullsrc`, 20 s de silencio, 16 kbps) | Sin contenido; propio de E2A |
| `template/tactical/plays/realism-v3-3-5v5.json` (+ `.spec.json`) | Derivado de la jugada original de E2A `chicago-v3-under-three` + ampliaciones de preparación y cierre | Propio de E2A |
| `template/src/t3d/realism-v3-3/anat33.ts` (radios) | Medidos con bpy en `e2a_player_off_v32.glb` (MakeHuman CC0, ver la procedencia V3.2) | Datos derivados de un asset CC0 |
| `qa/cloth_l2_v33_*` (JSON) | Bake de prueba de Blender sobre la GLB V3.2 | Propio; la GLB del bake (morph) **no** se versiona |

**Ninguna malla, textura, mocap ni audio nuevo.** V3.3 renderiza las GLB V3.2 ya inventariadas en V3.2/V3.1.
- Sin ElevenLabs ni servicios de pago.
- Los renders son mudos: no llevan sonido de bote ni de ninguna otra clase.
- Logo 2026 (`template/public/brand/e2a-logo-2026.png`) solo en el vídeo editorial 08, ya presente en el repo.

**Pendiente heredado:** la clave de licencia `3d/e2a-player-makehuman-cc0` sigue sin estar en `config/asset_licences.json`, como en V3. Necesita el OK del propietario y no se ha tocado.
