# Formatos: ficha de técnica (`e2a.technique/1`) y análisis (`e2a.analysis/1`)

## Ficha de técnica — `editing-library/techniques/tec-NNNN.json`

```json
{
 "schema": "e2a.technique/1",
 "id": "tec-0002",
 "version": 2,
 "nombre": "Titular corto con una sola palabra clave en dorado",
 "categoria": "tipografia",
 "descripcion": "Qué es y cómo se ve, con nuestras palabras (nunca copiado de la referencia).",
 "para": ["record", "player", "curiosity", "comparison"],
 "evitar_en": [],
 "aplicar_a": {"scene_type": "headline", "posicion": "cualquiera"},
 "receta": {
  "scene": {"layout": "high", "transition": "cut"},
  "episode": {"hook": "stat-slam"},
  "sfx": ["tick"],
  "music": {"payoff_en_esta_escena": true}
 },
 "comprobacion": {
  "texto": "regla legible para una persona",
  "reglas": [
   {"metrica": "plan.escena_s", "op": "<=", "valor": 4},
   {"metrica": "text.texto_en_pantalla_pct", "op": ">=", "valor": 0.6}
  ]
 },
 "evidencia": [
  {"ref_id": "R-0001", "medidas": {"texto_en_pantalla_pct": 0.99}, "nivel": "estimacion"},
  {"ref_id": "R-0001", "medidas": {}, "nivel": "hipotesis", "nota": "visto en la hoja de contactos"}
 ],
 "origen": "R-0001 (propio)",
 "estado": "propuesta",
 "requiere_codigo": false,
 "creada": "2026-11-11", "actualizada": "2026-11-11",
 "historial": [{"fecha": "…", "de": "propuesta", "a": "probada", "motivo": "…"}]
}
```

| Campo | Reglas (las comprueba `library.py validate`) |
|---|---|
| `categoria` | cortes, ritmo, animacion, transicion, efectos, sonido, subtitulos, tipografia, narrativa, camara, estructura, color, composicion. APPLY elige como mucho una por categoría |
| `para` / `evitar_en` | tipos de historia de `StoryType` en `types.ts`; no pueden coincidir. `evitar_en` excluye la ficha |
| `aplicar_a.scene_type` | un `type` de escena de Remotion Pro (media, headline, stat, scoreboard, timeline, split, court) o ausente |
| `aplicar_a.posicion` | primera, segunda, ultima, penultima, climax (escena más cercana al payoff de la música o al 75%), mas_larga, cualquiera |
| `receta.scene` | solo campos de edición: `transition`, `camera`, `layout`, `backdrop`, `captions`, `bg_treatment`, `sfxTransition`. Valores leídos de `template/src/pro/types.ts` (si el tipo cambia, la validación cambia con él). Cualquier campo del guion (`lines`, `label`, `value`, `media`…) invalida la ficha |
| `receta.episode` | `hook` (stat-slam, photo-line, split, clock) y `ending`. APPLY **no cambia** el `ending` de un guion que ya lo tiene: si no coincide, la ficha se descarta como recomendación |
| `receta.sfx` | nombres de `SfxName`; respetan el presupuesto (`sfxBudget` del episodio o `audio-mix.json`) |
| `receta.music` | `payoff_en_esta_escena` / `drop_en_esta_escena` → `music.payoffAt` / `music.dropAt` = ancla de la escena |
| `comprobacion.reglas` | al menos una. Métricas `plan.*` (se evalúan al planificar: `plan.escena_s`, `plan.mediana_escenas_s`, `plan.max_escena_s`, `plan.escenas_n`, `plan.duracion_s`, `plan.sfx_n`) o rutas del `analysis.json` del render (`editing.*`, `retention.*`, `rhythm.*`, `structure.*`, `audio.*`, `color.*`, `text.*`, `technical.*`), evaluadas por `apply_plan.py qc`. `op`: `<= >= < > == !=` |
| `evidencia` | al menos una entrada con `ref_id` y `nivel` (observacion / estimacion / hipotesis) |
| `estado` | propuesta → probada → activa, o descartada. Con `requiere_codigo: true` nunca puede ser activa |
| `version` | entero; `library.py status` lo sube y deja `historial` |

## Análisis — `editing-library/analyses/R-NNNN/analysis.json`

Secciones (todas obligatorias; `validate_analysis.py` las comprueba):

- `schema_version`, `ref_id`, `source` {`title`, `key`, `sha256`, `rights` propio|tercero, `size_bytes`}
- `technical` {duración, fps, ancho, alto, aspecto, orientación, códecs, audio}
- `editing` {`cuts`, `n_planos`, mediana/media/mín/máx de plano, % estáticos, cambios de perspectiva}
- `shots[]` {n, inicio, fin, duración, movimiento de imagen, `camara` {movimiento, zoom_total, desplazamientos, temblor, nivel}, `color`}
- `transitions` {items [{t, duración, tipo, nivel, evidencia}], resumen}
- `camera` (resumen), `rhythm` (cortes/10 s, por ventana de 5 s, cambios de ritmo, CV)
- `structure` {gancho, desarrollo, climax, desenlace, método}
- `text` {texto_en_pantalla_pct, franjas_ocupadas, subtitulos {posición, alto, ritmo, color, resaltado, aparición, tipografía}}
- `overlays`, `color` (global, estética, paleta, afinidad E2A, destellos), `audio` (o null), `sync`, `retention`
- `frames` (rutas relativas, nunca absolutas), `meta` {skill_version, code_sha256, params, content_sha256, analyzed_at}

`content_sha256` es la huella de todo salvo `meta`: si alguien edita el análisis a mano, la validación
lo detecta. `analyzed_at` es lo único que cambia entre dos análisis del mismo archivo.

## Índice — `editing-library/index.json`

Una entrada por referencia: `ref_id`, `source_key` (id de Drive o URL normalizada), `source_title`,
`kind` file|link, `rights`, `status` analyzed|failed, `reason`, `sha256`, `content_sha256`,
`analyzed_at`, `cards`, `summary`. `library.py seen` busca por clave y por huella del archivo (el mismo
vídeo subido con otro nombre no se analiza dos veces).

## Uso — `editing-library/usage.json`

`{"uses": [{"episode", "date", "techniques", "plan_sha256", "library_version"}]}`. Lo escribe
`apply_plan.py plan --record`; una entrada por episodio (se reemplaza, no se duplica). APPLY resta 2
puntos a las técnicas usadas en los 3 últimos vídeos para rotar.
