# Procedimiento por fases — Tactical Studio (v2 + publicador V3)

Cada estado sensible se alcanza SOLO con su comando-puerta, que ejecuta el control real. `advance` solo
sirve para `candidate`, `researched` y `analytics_*`. El registro es append-only y encadenado por hash
(`verify` lo comprueba); entre sesiones se sincroniza con `tools/studio_sync.py` (lease → pull → … → push → release).
IDs: `E2A-TACTICAL-{YYYY-MM-DD}-V01|V02` (fecha Sydney del post). `T = python3 tools/tactical_studio.py`,
`P = python3 tools/tactical_publisher.py` (el ÚNICO componente que puede llevar a una llamada `createScheduledPost`).

| Estado | Comando | Control que ejecuta el propio comando |
|---|---|---|
| candidate / researched | `T advance CID <estado> --op …` | — |
| selected | `T select CID --play-id … --family … --variant … --concepts … [--differential …] --sources …` | repetición 45 días por familia/variante/conceptos contra el registro de jugadas |
| scripted | `T script CID guion.txt` | HOOK/SETUP/CASE A/CASE B o COUNTER/TAKEAWAY/CTA y duración estimada 30–40 s; congela el hash |
| storyboard_ready | `T storyboard CID jugada-a.json jugada-b.json` | ejecuta `test-play.mts`: 0 fallos y ≥1 claim de narración por jugada; guion intacto |
| (antes de ElevenLabs) | `T voice-permit CID --credits N` | presupuesto diario (tomas y créditos); niega si ya hay toma pagada para ese guion |
| audio_ready | `T audio CID --voice … --words …` | permiso emitido + la transcripción Scribe dice el guion congelado (≥ 0,90) |
| rendered | `T render CID bundle.json --out dir` | licencias de cada medio (sidecar `.provenance.json` con hash) ANTES de gastar; voz = la de audio_ready; presupuesto de renders; Remotion + encode social con UNA ganancia fija de master (objetivo −14 LUFS, tope por true peak −1,2 dBTP y ±6 dB; sin loudnorm, sin limitador: música y SFX conservan su relación con la voz) |
| rendered (re-entrada) | `T remaster CID --op …` | solo tras un QC_FAIL exclusivamente de audio; re-codifica EL MISMO master (hash) sin renderizar fotogramas (no gasta presupuesto de render); máximo 1 por vídeo; conserva las referencias de licencia del render |
| qc_passed | `T qc CID --episode … --reports dir` | mide el MP4 (ffprobe, EBU R128, blackdetect, silencios, 8 fotogramas), test-play, qc-tactical3d, licencias; hash = el renderizado |
| asset_ready | `T asset CID https://…` | descarga la URL: SHA-256 y tamaño = MP4 del QC; exige el fichero oficial de licencias |
| authorised | `P authorise CID --sha S --op …` | modo `direct_delegated` + delegación de `origin/main` con el sha fijado en la tarea, `granted`, no revocada, ≤7 días, en vigor, alcance = estudio (marca, cuentas, 3 redes, 10:00/13:00, Tactical3DV2, 30–40 s, QC completo, presupuestos). `T authorise` sigue bloqueado |
| (paquete) | `T package CID --caption … --titles …` | un post, 3 redes, medio = URL verificada, etiquetas IA, título YT con #shorts |
| (antes de crear) | `P prepare CID --package … --readback … --sha S --probe-url …` | delegación EN VIVO; ruta de verificación del medio (static.metricool.com legible) o no se crea nada; estado `authorised`; sin confirmaciones, sin `created`, sin intento abierto; sin el mismo vídeo en el calendario; ≤2 intentos; `schedule-check` (lectura fresca de todo el día, colisiones ±60 min, hash del paquete, reserva de las 3 redes); presupuesto `create_calls`; escribe `intent` y da los argumentos de UNA llamada |
| (tras la llamada) | `P record CID --intent … --response -` | id + uuid → `created`; cualquier otra cosa → `create_uncertain` (nunca se reintenta a ciegas) |
| (si es incierto) | `P reconcile CID --readback … --package …` | lectura del día: 1 coincidencia → se adopta; 0 → `create_absent` (se permite otro `prepare`); >1 → DUPLICADO, `failed` e informe, no se borra nada |
| scheduled_* | `P confirm CID --readback … --package …` | ticket del mismo paquete; mismo post una sola vez; hora, zona y texto; BYTES del medio = MP4 del QC; no borrador ni pendiente; estado real por red (las redes confirmadas se conservan) |
| published_confirmed | `T published CID --readback …` | PUBLISHED + URL pública en el dominio de cada red |

Fallo: `T fail CID --phase P --reason R [--retry-after ISO]`. Un reintento por fase; luego `failed` e informe.
Si a las 09:00 del día del post no está `scheduled_confirmed`, ese vídeo se cancela (no se publica tarde).

Informe diario: `P status <fecha>` → `produccion/tactical/INFORME-DIARIO.md`.
