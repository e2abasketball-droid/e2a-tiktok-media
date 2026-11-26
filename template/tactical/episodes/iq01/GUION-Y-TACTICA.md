# E2A BASKETBALL IQ · EP 01 — CAN YOU FIND THE OPEN PLAYER?

Guion final, tiempos y justificación táctica. Narrador: Deuce (ElevenLabs eleven_v3), **una sola toma** (461 créditos, flow `1pTn5uvKMIOx2UDpt8GV`); transcripción Scribe 156 créditos. La voz no se regenera ni se estira: solo se insertan silencios en sus pausas naturales (`_voice-iq01.py`).

## Estructura (ACTION → QUESTION → THINK → REPLAY → REVEAL → EXPLANATION → PAYOFF)

| Tiempo | Narración | Imagen |
|---|---|---|
| 0,0–3,1 | He beats his man, and here comes the help. | **ACTION.** Plano cercano detrás del base: O1 supera a X1 hacia el centro; rampa de cámara lenta mientras X3 rota; la cámara sube a la vista completa 4c4. Título "CAN YOU FIND THE OPEN PLAYER?" + sello BASKETBALL IQ · EP 01 |
| 3,1–7,0 | Freeze it. Who's open? A, B, or C? | **QUESTION.** Congelado en el instante en que X3 ya está comprometido. Letras A (O2), B (O4), C (O3) aparecen sobre cada jugador al decirlas; tres líneas de pase blancas iguales (sin pista) |
| 7,0–9,1 | *(silencio, 2,1 s)* | **THINK.** "YOUR CALL: A, B OR C". Sin temporizador; la música baja a un pad sin percusión |
| 9,1–10,4 | Lock it in. | "LOCK IT IN" |
| 10,4–14,7 | Now watch the low defender. He leaves the corner to stop the drive. | **REPLAY.** Rebobinado + repetición en cámara lenta desde el lado débil: X3 marcado, flecha roja de su rotación, espacio dorado en la esquina que deja |
| 14,7–17,2 | A, his defender is still home. | **REVEAL A.** Esquina derecha congelada: X2 a 1,4 m de O2 (línea de separación roja). Letra A tachada |
| 17,2–21,2 | B, still guarded, and his defender is sitting in the passing lane. | **REVEAL B.** Ala izquierda: X4 cerca de O4 y dentro de la línea de pase O1→O4 (línea roja bloqueada). Letra B tachada |
| 21,2–23,2 | C, wide open. | **REVEAL C.** Esquina izquierda: 6,4 m entre X3 y O3 (separación dorada). Letra C dorada |
| 23,2–26,9 | Kick it to the corner. The next rotation is too late. | **EXPLANATION.** Velocidad real: pase, X4 reacciona tarde (línea roja X4→O3, "2ND ROTATION: TOO LATE"), recepción, triple. "THREE." |
| 26,9–29,4 | Don't watch the ball. Watch the help. | **LESSON.** Rebobinado, vista cenital: la rotación de X3 |
| 29,4–32,7 | Did you find him? Tell us what you picked. | **PAYOFF.** Vuelta al encuadre de la pregunta con las letras neutras: "A, B OR C? COMMENT IT" + logo 2026 (invita a comentar y a volver a verlo) |

## Por qué C (en esta posesión, no como regla universal)
- **Ayuda del hombre bajo (WABC/FIBA, ayuda balón-tú-hombre):** X3 empieza en posición de ayuda entre O3 y la zona. Cuando O1 supera a X1 hacia el centro, X3 rota al aro para parar la penetración (0,3 s después del primer paso: reacción, no adivinación).
- **A (O2):** X2 da un paso de ayuda ("pinch") pero sigue a 1,4 m de O2: el pase genera un tiro contestado.
- **B (O4):** X4 se hunde en ayuda y amaga; sigue a ~2,1 m de O4 y casi encima de la línea de pase O1→O4: pase arriesgado y tiro defendido.
- **C (O3):** su defensor está en la zona (6,4 m). La **segunda rotación** (X4) existe, pero en esta posesión X4 tiene que seguir con O4: reacciona al pase y en la recepción aún está a 3,9 m de O3. Por eso C es la mejor respuesta aquí. Con una defensa que rote antes (X4 bajando a la esquina y otro defensor tapando el ala) la respuesta podría cambiar: el vídeo no afirma que la esquina débil quede siempre libre.

## Coordenadas
Media pista FIBA (15 × 14 m), canasta en (0; 1,575), triple 6,75 m / 6,60 m en las esquinas. El brief usa x positivo = derecha del ataque; el motor usa x negativo = derecha del ataque, así que **x_motor = −x_brief** (y igual).

| Jugador | Brief (x, y) | Motor (x, y) | Papel |
|---|---|---|---|
| O1 | +3,3 / 7,6 | −3,3 / 7,6 | Base, slot derecho, penetra hacia el centro |
| O2 | +6,9 / 2,2 | −6,9 / 2,2 | Esquina derecha = **A** |
| O3 | −6,9 / 2,2 | 6,9 / 2,2 | Esquina izquierda = **C** |
| O4 | −5,5 / 7,3 | 5,5 / 7,3 | Ala izquierda = **B** |
| X1 | +3,0 / 6,8 | −3,0 / 6,8 | Defiende el balón, superado, persigue a la cadera |
| X2 | +6,3 / 2,8 | −6,3 / 2,8 | Pinch a (−5,75; 3,0), no abandona a O2 |
| X3 | −4,1 / 3,3 | 4,1 / 3,3 | Ayuda baja, rota a (−0,2; 3,0) delante del aro; cierre tardío tras el pase |
| X4 | −4,3 / 6,3 (diseñado) | 4,3 / 6,3 | Se hunde a (3,95; 5,95), tras el pase da un paso a (4,4; 5,2); nunca llega a la esquina antes de la recepción |

Validación automática (`scripts/test-play.mts`): **28/28** (4c4, sin teletransportes ni solapes, pase de 8,1 m a 10,1 m/s con línea libre, tiro desde detrás del arco con el defensor más cercano a 3,4 m, y todas las afirmaciones del guion comprobadas en la pista).
