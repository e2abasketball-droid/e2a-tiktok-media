# Zero Cut · test agresivo frente a la versión normal (V2)

| | Normal (V2) | Test agresiva |
|---|---|---|
| Duración | 49,4 s | 53,6 s |
| Hook | YOU'RE NEVER GOING PRO / IF YOU CAN'T READ THIS | **STOP CALLING YOURSELF ELITE / IF YOU CAN'T READ THIS** (ELITE y READ THIS en dorado), toma nueva más agresiva; arranca en plena acción y se congela sin resolver justo en el error del defensor |
| Pierna del defensor | Anillo rojo en el pie **izquierdo** (era el lado equivocado) | Medido sobre el cuerpo animado: el defensor cae y carga la **derecha**. Toda la pierna parpadea en rojo 3 veces y se queda marcada solo durante la explicación |
| Cambio de dirección | Flecha del recorrido | **Arco dorado alrededor de la cadera** que une el ángulo del falso handoff (flecha blanca) con el ángulo real del corte (flecha dorada), solo en el momento decisivo |
| Qué espera / qué finge | Implícito | FAKE HANDOFF → EXPECTS THE HANDOFF → HE JUMPS THE HANDOFF → WEIGHT ON THE WRONG LEG |
| Bandeja | El cortador frenaba en un "1-2" y saltaba en vertical en el sitio | Recepción en carrera a ~4,5 m/s, dos pasos de recogida, despegue **en** el punto y vuelo hacia delante hasta debajo del aro; soltado con el brazo más extendido hacia el aro. El ritmo vuelve justo cuando el balón sale de las manos del pívot |
| Segunda lectura | Cenital → empuje | Cenital para situar → **acercamiento a la ayuda** (RIM PROTECTED, pase bloqueado) → la esquina se revela tarde → pase y tiro |
| Música | Dark techno industrial 144 BPM | **Shuffle oscuro UK garage / breakbeat** 136 BPM ↔ **psicodélico a medio tiempo** (pad que gira, arpegio con delay), misma tonalidad e identidad; vuelve a tope en el pase, en el pase a la esquina y en el cierre |
| Cierre | DO YOU HAVE WHAT IT TAKES? | THINK FASTER · READ FASTER · PUNISH EVERY MISTAKE sobre la jugada completa → **BE PART OF THE ELITE OF THE FUTURE** + logo |
| Voz | Hook V1 + toma V2 (552 cr) | Una toma nueva completa (627 cr) |

## Componentes nuevos reutilizables
- `src/t3d/cues3d.tsx`: `legLoad` (pierna cargada, con detección automática por apoyo real) y `pivotArc` (arco de cambio de dirección en la cadera). Opt-in: no cambia ningún vídeo anterior.
- `tools/audio/darkshuffle_states.py`: música por estados shuffle ↔ psicodélico desde el plan del montaje, con stems.
- `motion33.ts`: soltado de bandeja `reach` (opt-in por evento).
- `tactical/specs/_gen-zerocut-test.py`: final reconstruido (carrera continua y vuelo hacia el aro).
- `scripts/_probe-support33.mts`: mide qué pie lleva el peso y la dirección real del cuerpo en cada instante.

## Limitaciones que siguen
- El motor V3.3 aún no tiene bandeja a una pierna: el despegue es a dos pies y los brazos usan la forma de tiro, ahora con avance real hacia el aro y el brazo más extendido. Es claramente mejor que la V2, pero no es una bandeja perfecta.
