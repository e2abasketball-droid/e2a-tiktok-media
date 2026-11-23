# E2A MINIMAL V1 — estilo de producción (propuesta, NO activado)

Nace con el Reel HORNS (2026-11-23). Es un estándar documentado para revisar, **no** un cambio del pipeline. No se ha aplicado a ningún otro episodio ni tarea programada.

## Principio
Claridad editorial antes que realismo, y realismo antes que efectos. Una idea por vídeo. La tensión sale de causa → efecto y de seguir a **un** jugador, no del movimiento de cámara.

## Cámara
- Una cámara táctica fija para todo el vídeo, canasta arriba, sin órbitas, sin roll y sin cambiar de lado.
- Se encuadra con `scripts/fit-search.mts` para que los 10 jugadores (pies y cabeza) quepan en la banda segura 380–1330 px durante toda la acción.
- Como mucho un zoom del 5–10 % en una pausa. La cámara llega a su sitio antes del pase importante.

## Montaje
- Una toma por frase y tomas de 4–8 s.
- Cámara lenta solo donde la frase lo pide (0,25–0,7×). La acción de pago (tiro, finalización) va cerca del tiempo real.
- Las ramas A/B parten del **mismo fotograma**, porque las dos jugadas son idénticas hasta la decisión (`test-branches.mts`). El reset se marca con un sello de menos de 0,9 s (`SAME ACTION. DIFFERENT HELP.`).
- Congelados de 0,35–0,5 s, con borde y la etiqueta FREEZE discreta.

## Gráficos (máximo 2 elementos tácticos a la vez)
- Anillo dorado (#C9A24D) solo en el jugador clave.
- Rutas finas: ROLL en azul claro (#8EC5F0) y POP en dorado, con su etiqueta en el suelo.
- Línea de pase blanca, solo mientras el balón vuela.
- Etiquetas de una palabra: HORNS, ROLL, POP, HELP, STAY. Cada una dura 0,7–1,3 s.
- Títulos arriba (y ≈ 236), de 2–4 palabras. Subtítulos abajo (y ≈ 1390), una frase del guion por bloque, con palabras clave en dorado.
- Sin fuego, sin partículas, sin flashes, sin temblores, sin enjambres de flechas.

## Audio
- Una voz tranquila, a unas 112–122 palabras por minuto.
- Música propia minimalista: `tools/audio/horns_minimal_bed.py`, sintetizada con numpy, de E2A. Va por debajo de la voz con ducking.
- Como mucho dos acentos suaves, en el rehook y en el cierre.
- **Ningún sonido de bote**, chirrido ni whoosh.

## Marca
- Navy #0B1C3D, dorado #C9A24D, dorado profundo #A9842F y blanco.
- Logo 2026 solo en el último segundo, pequeño.

## QA obligatoria
Antes de dar el vídeo por bueno:
- `test-play.mts`: claims ligados a cada frase;
- `test-branches.mts`;
- `qc-realism-v33.mts` con los 10 jugadores (balón-cuerpo = 0);
- hoja de 12 fotogramas extraída del MP4;
- `ffprobe` y loudness;
- revisión de una preview a escala reducida.
