# Arrow Press 1-3-1 V3: voz animada (eleven_v3), 2026-11-24

**Petición del propietario (13:22 Madrid):** voz mucho más animada, con altibajos de entonación en los momentos críticos.
**Autorizado:** una toma eleven_v3 con marcas de emoción, unos 840 créditos (confirmado en una segunda tarjeta). **Gasto real: 841 créditos.** Scribe: 0 créditos.

## Toma
- Voz Deuce `DaueUomjhh8LFuAV8aGj`, modelo `eleven_v3`, generations_count 1.
- Flow `ndgUpjM1yh1oVHsHvoQ5`, generación `XWe2QfFeLDJ26yek5b3l`.
- Texto con marcas: `VOICE-V3-TAGGED.txt`. Las palabras son las mismas que en V1.
- Alineación de las 109 palabras: todas coinciden con el guion. Las marcas no se oyen: caen en los silencios entre frases (comprobado con silencedetect).
- Pausas: `arrow131v3-voice.json`, con los mismos huecos que V1. Voz final de 44,03 s.

## Audio
`voice-dynamics.py --preserve` (nuevo):
- nunca baja una frase; solo sube las que quedan más de 1,5 dB por debajo de su objetivo;
- compresión suave (−18 dB, 1,6:1);
- toma normalizada antes a −23 LUFS.

Niveles relativos a la explicación:
- «It's a TRAP!» +3,5 dB
- «TRAP!» +2,7 dB
- «SPRINT back!» +1,7 dB
- LRA de la voz 3,1 (V2: 2,4)

Música nueva con la misma regla de la toma anterior (`e2a_music.py tactical --no-sfx`, pista drive_a):
- primer drop en «Trap!» (18,34 s);
- segundo en «becomes» (37,5 s).

## Vídeo
- Mismo montaje V2 (`_gen-arrow131-v2.py`), recalculado con las palabras nuevas. Duración 45,47 s.
- Táctica y cámaras sin cambios.
- Un solo render con headless shell: 0 fotogramas malos.

## QC (MP4 exportado, `qc-v3.json`)
- Tramos congelados: 0 parpadeos (en V2 también 0).
- Las únicas variaciones son las mismas transiciones de subtítulo y título que en V2.
- Máster: −14,5 LUFS, −1,2 dBTP. Trial: −15,6 LUFS, −1,4 dBTP, SSIM 0,69.
