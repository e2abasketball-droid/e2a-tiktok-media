# E2A Basketball Visual Standard v1

> Estándar visual y de edición **por defecto** para todos los próximos vídeos de baloncesto de E2A (regla del propietario, 2026-11-23, tras el HORNS V2). No se vuelve al estilo antiguo salvo petición explícita. Preset: `template/tactical/presets/e2a-visual-standard-v1.json`.

Nace del Reel **HORNS: THE DEFENDER'S DILEMMA**. Recoge lo que ya funciona y fija las dos mejoras del V2 (ritmo e inicio).

## Personajes 3D
- Motor **v33** (`athleteRenderer: "v33"`): mejor silueta, ropa y presencia que legacy/v31/v32. Movimiento compilado por jugador. Contacto balón-cuerpo = 0 (`qc-realism-v33.mts`).
- No se cambia el motor por defecto del código (legacy sigue de reserva) ni la tarea diaria de publicación: eso se decide aparte.

## Pista y escenario
- `env: "cinema"`: pista y luz actuales, acabado limpio y profesional. Sin fuego, partículas, flashes ni efectos de público.

## Gráficos y overlays
- **Marcadores de jugador** (`marker`, no el anillo plano): ataque = anillo dorado sólido con brillo suave en el suelo; defensa = anillo blanco **segmentado** y más fino. Cambian forma Y color, así que se distinguen al primer vistazo, también en el móvil.
- **Leyenda** ATTACK / DEFENSE arriba a la izquierda al presentar la formación.
- **Aparición secuencial**: primero los 5 atacantes, luego los 5 defensores (~0,17 s entre cada uno), con un pulso suave y un realce del jugador clave al final.
- Rutas finas con etiqueta en el suelo: ataque en dorado, lectura/roll en azul claro #8EC5F0. Máximo 2 overlays tácticos a la vez. Línea de pase blanca solo mientras vuela el balón. Pines de una palabra (HELP, STAY, ROLL) y chips de resultado cortos (THREE., LAYUP.).
- Nunca recargar: cada elemento ayuda a entender la jugada.

## Cámaras
- Una cámara táctica clara por idea, canasta arriba, detrás del ataque. Se encuadra con `fit-search.mts` y se **verifica todo el montaje** con `frame-fit.mts` (0 fotogramas marcados en la banda 380–1330 px).
- Movimiento solo si aporta comprensión. Sin órbitas ni roll gratuitos. Si un zoom saca a algún jugador del cuadro, se quita.

## Ritmo
- Tranquilo y claro, pero siempre avanzando hacia una conclusión. Ningún silencio de más de ~2,9 s, y cualquier pausa larga va sobre un remate real (tiro/finalización) con un chip en pantalla, nunca aire muerto.
- Se reutiliza la toma de voz aprobada; solo se insertan silencios entre frases (`scripts/tactical-voice.py`, `gapFill: silence`). Voz nueva solo si es imprescindible.

## Audio
- Una voz calmada + música propia minimalista, con ducking. Mezcla offline a −14 LUFS ±1, pico ≤ −1 dBTP. Sin sonido de bote, chirridos ni whooshes.

## Marca
- Navy #0B1C3D, dorado #C9A24D, dorado profundo #A9842F, blanco. Logo 2026 pequeño en el último segundo.

## QA obligatoria
`test-play.mts`, `test-branches.mts` (si hay ramas), `qc-realism-v33.mts` (balón-cuerpo 0), `frame-fit.mts` (0 marcados), `ffprobe` + loudness, hoja de 12 fotogramas del MP4 final y revisión de una preview a tamaño móvil.
