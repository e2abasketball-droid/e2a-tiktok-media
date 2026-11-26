# THE ZERO CUT: informe de producción

Fecha: 26 nov 2026 · Rama `claude/project-thread-1690kk` (repo e2a-tiktok-media, sin fusionar) · **No publicado ni programado.**

## Entregables
| Archivo | Qué es |
|---|---|
| `e2a-zero-cut-social.mp4` | Versión principal, 1080×1920, 30 fps, H.264, AAC 48 kHz, ~40,9 s |
| `e2a-zero-cut-trial.mp4` | Versión para trial reel: hook distinto ("NEVER GOING PRO?" / "NOT IF YOU CAN'T READ THIS", cámara más abierta) + retoque de imagen y EQ suave. Misma toma de voz |
| `e2a-zero-cut-social.srt` | Subtítulos en inglés (22 bloques, máx. 2 líneas, sincronizados por palabra) |
| `e2a-zero-cut-cover.jpg` | Portada vertical "THE ZERO CUT" con logo 2026 |
| `animacion/` | Datos de animación de las dos lecturas (`zerocut-a-layup`, `zerocut-b-kick`: spec + jugada compilada) y el episodio editable |
| `MUSICA-Y-DERECHOS.md` | Registro de música, voz y derechos |
| `GUION-Y-TIEMPOS.md` | Análisis de la referencia, guion final y tiempos |

## La jugada (lo que se ve)
- **Lectura 1 (bandeja):** O5 (pívot) recibe arriba; O2 esprinta hacia él vendiendo el handoff; X2 lo sigue y se anticipa al lado; O2 planta y corta por detrás; O5 le da el pase picado; bandeja.
- **Lectura 2 (esquina):** misma acción, pero la ayuda baja (X3) cruza a parar el corte; O5 lanza el pase por encima a la esquina débil, O3 tira solo.
- Ambas validadas con el comprobador de jugadas (velocidades, aceleraciones, distancias de pase, sin teletransportes): A 25/25, B 24/24.

## Montaje (12 planos, ~40,9 s)
Hook con seguimiento y zoom a los pies de X2 → congelación en la máxima ventaja · cenital con rebobinado y título · seguimiento de la venta del handoff · POV del defensor y bajada a los pies (cámara lenta) · órbita dinámica en el corte con pasillo dorado · repaso cenital en 3 pasos · lectura 2 con la esquina iluminada · SAME ACTION / READ 1 / READ 2 · BASKETBALL IQ con logo · último plano = primer plano del hook (loop).

## Mejoras visuales y técnicas nuevas (reutilizables)
1. **`openLane` (nuevo overlay 3D):** pasillo dorado translúcido que nace detrás del defensor batido y llega al aro (o a cualquier punto), con galones blancos en movimiento. Solo aparece cuando el defensor ya se ha girado. `src/t3d/telestration3d-bp.tsx`.
2. **Música D&B propia por código** (`tools/audio/zerocut_dnb.py`): se genera a partir de los cortes del montaje (golpes, subidas y break caen exactamente en los cambios de plano). Reutilizable para cualquier reel cambiando BPM y cortes.
3. **Generador de jugadas medido** (`tactical/specs/_gen-zerocut.py`): mide los tiempos reales de cada acción y encadena la siguiente, así la defensa reacciona después del ataque y nunca antes.
4. **Generador de montaje con variante trial** (`tactical/episodes/_gen-zerocut.py --trial`): el mismo archivo produce la versión principal y la de trial.
5. Encuadres revisados con el comprobador automático de fotogramas (ningún jugador clave fuera de cuadro en los planos explicativos). El cenital se rehízo para evitar reflejos de focos.

## Control de calidad
- Principal: 1080×1920, 30 fps, H.264, AAC 48 kHz, 40,87 s. **−14,7 LUFS, pico −1,5 dBTP, LRA 2,7.** qc-video: PASS, sin avisos.
- Parpadeo del suelo (qc-floor-flicker): 0 fotogramas malos en 1.226; congelaciones estables.
- Encuadres: comprobador automático en todos los planos explicativos; cenital rehecho.
- Audio: solo voz + música propia. Sin botes de balón ni SFX.
- Trial: −15,1 LUFS, pico −1,2 dBTP; SSIM frente a la principal 0,60 (hook distinto + zoom 3 % + color + EQ suave).

## Limitaciones conocidas
- El audio de la referencia no se pudo transcribir (descarga del modelo bloqueada por la red); el análisis se hizo con la imagen.
- En los primeros planos cortos (hook, READ 1/READ 2) hay jugadores secundarios fuera de cuadro a propósito.
