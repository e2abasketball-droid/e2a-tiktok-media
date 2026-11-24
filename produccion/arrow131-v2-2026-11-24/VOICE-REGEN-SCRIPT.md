# Arrow Press 1-3-1: guion segmentado para una toma nueva (opcional, NO ejecutado)

**Estado:** preparado, sin gastar créditos. Solo se ejecuta si el propietario lo autoriza.
- Voz: Deuce `DaueUomjhh8LFuAV8aGj`
- Modelo: `eleven_multilingual_v2`
- Una toma (generations_count 1)

## Opción 1: toma completa nueva (recomendada si se regenera), unos 610 créditos

- Coherente de principio a fin: mismo aire, misma prosodia y sin empalmes.
- El montaje se recalcula solo a partir de las palabras de Scribe (0 créditos). Después se vuelve a renderizar.

Ajustes: stability 0,38 · similarity 0,75 · style 0,40 · speaker boost activado.

Texto, por fases. Los saltos de párrafo son pausas. No se añade texto nuevo y la estructura narrativa no cambia.

```
[A — hook, seguro, con punch]
Half court isn't a line. It's a trap!

[B — explicación, clara]
This is the one-three-one arrow press. One at the point. Three across half court. One safety deep.
The point turns the ball to the sideline. Never let it go middle.

[C — activación, urgencia creciente]
The ball crosses half court... and the wing jumps. Trap!
The sideline and the half-court line are two extra defenders.

[D — lecturas, control]
The middle takes away the middle. The far wing reads the cross-court pass. The safety guards the long pass.

[C — segunda activación]
Now the ball escapes. Don't chase it. Sprint back!

[E — conclusión, cálida]
Same five players, same spots... and the arrow becomes a one-three-one zone.
Would you trap at half court... or wait in the zone?
```

Los únicos cambios de puntuación frente a V1 son «It's a trap!» y «Sprint back!», para pedir energía. Los corchetes son notas para nosotros y **no** se envían.

## Opción 2: solo las frases clave, unos 200 créditos

Son 10 frases:
- «Half court isn't a line.»
- «It's a trap!»
- «The ball crosses half court...»
- «and the wing jumps.»
- «Trap!»
- «Now the ball escapes.»
- «Don't chase it.»
- «Sprint back!»
- «Would you trap at half court...»
- «or wait in the zone?»

Riesgo: empalmar tomas distintas puede notarse (cambio de aire o de entonación entre frases). Por eso es menos recomendable que la opción 1.

## Después de cualquier toma

1. Scribe (0 créditos): words → `tactical-voice.py` (pausas) → `_gen-arrow131-v2.py --words`.
2. `voice-dynamics.py` con la misma curva.
3. Render con headless shell, QC de parpadeo y A/B.
