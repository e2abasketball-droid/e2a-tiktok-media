# 05 · Informe de render

| | |
|---|---|
| Archivo | `E2A-ZONE-131-V2-FINAL-REVIEW.mp4` |
| Formato | H.264 High, yuv420p, 1080×1920, 30 fps, 1028 fotogramas, 34,24 s, ~2,9 Mb/s vídeo + AAC LC 48 kHz estéreo 192 kb/s |
| Loudness | −14,0 LUFS integrado, pico −3,7 dBFS |
| Render | `npx remotion render src/index.ts Tactical3DV2 raw-v2.mp4 --props=props.json --concurrency=4 --timeout=300000 --muted --crf=16` con Chromium headless del contenedor: **45 min 19 s** (memoria no medida) |
| Props | `python3 tactical/episodes/_gen-zone131-v2.py --out props.json --words tactical/episodes/zone131v2/zone131v2-voice.words.json` (hook A por defecto) |
| Voz | `python3 scripts/tactical-voice-edit.py tactical/episodes/zone131v2/zone131v2-voice.json` → `public/tactical/zone131v2/voice.wav` (33,71 s) + la misma cadena de EQ/compresión de la V1 (`voice.mix.wav`) |
| Música | `python3 music/e2a_music.py --story tactical --track cine_b --duration 34.24 --drop-at 8.98 --payoff-at 25.07 --no-sfx --soft-edges --history "" --voice …` |
| Mezcla y mux | amix voz + música → loudnorm −14 → +0,7 dB → mux sin recodificar el audio en origen (x264 slow crf 18) |
| Hooks | fotogramas 0–95 de cada variante, ~4 min cada uno |
| Trial | `scripts/trial-variant.sh` → `E2A-ZONE-131-V2-TRIAL.mp4` (zoom 3 %, grade, EQ; SSIM 0,667). Regla de E2A de dos archivos por reel. No es un segundo candidato. |
