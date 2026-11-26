# Zero Cut · test agresivo · música y transiciones

**Pista propia** generada con `tools/audio/darkshuffle_states.py` (numpy, sin samples, sin grabaciones de terceros, sin servicios de música IA, sin créditos). Original de E2A, uso comercial libre. 136 BPM, re frigio (D–Eb–Bb–C).

## Una sola identidad, dos mundos
- **A · shuffle oscuro (UK garage / breakbeat):** batería 2-step con semicorcheas swing (~58 %), bombo en el 1 y en el "y" del 3 (siempre dentro del kit completo, nunca aislado, para que nada suene a bote), palmada + caja en 2 y 4, hats y shaker con swing, clicks metálicos, bajo reese sincopado con wobble de filtro a corcheas (se aparta bajo el bombo) y acordes menores filtrados en los golpes con swing.
- **B · psicodélico (cámara lenta):** mismo tempo y misma tonalidad, sensación a medio tiempo. Sin bombo. Una palmada enorme con reverb en el tiempo 3, ticks suaves, sub en la tónica, pad con coro que gira de un oído al otro y "respira", y un arpegio hipnótico del mismo acorde a través de un delay ping-pong que se oscurece en cada repetición.
- **C · liberación:** un swell corto y filtrado que resuelve exactamente en el evento; el grid de la batería se reinicia ahí, así el golpe cae en el fotograma.

## Mapa del montaje (segundos)
| Tramo | Estado | Evento |
|---|---|---|
| 0,0–9,6 | A | Hook y explicación rápida |
| 9,6–22,0 | B | "Watch the defender": pierna roja, arco de cadera, el pasillo se abre |
| **22,0** | C → A | "One pass": el balón sale de las manos del pívot |
| 27,0–32,5 | B | La ayuda cruza, la esquina se abre |
| **32,5** | C → A | El pase a la esquina |
| 37,9–43,1 | B | Punto de decisión, READ THE DEFENSE |
| **43,1** | C → A | "The future elite...", hasta el cierre |
Golpes de acorde en THE ZERO CUT (5,3), ONE CUT (34,2) y TWO READS (35,9).

## Mezcla
Solo voz + música. Sin botes, sin SFX, sin whooshes (los swells están a −5 dB respecto a la V2). La música baja bajo la voz por frase (`voice-dynamics.py`, curva en `zerocut3-voice-dynamics.json`). Mezcla −14,8 LUFS, pico −1,5 dBTP antes del mux.
