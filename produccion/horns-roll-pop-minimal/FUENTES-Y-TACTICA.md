# HORNS: THE DEFENDER'S DILEMMA — fuentes y táctica

## Fuentes y qué afirma cada una
No he abierto estas páginas desde esta sesión. Su contenido es el que resume el brief del propietario (§01.1), y uso solo lo que ahí se cita.

| Fuente | Lo que sostiene en este Reel |
|---|---|
| FIBA Europe Coaching, «Horns» | 1-2-2: el base usa uno de los dos bloqueos altos. Si usa el de O5, O5 continúa al aro y O4 se abre al lado contrario (pop). El base puede penetrar, tirar o asistir. |
| The Hoops Geek, «Horns Pick & Roll, Pick & Pop» (A. Rauh, 18-06-2025) | El interior que bloquea hace **roll** y el del otro codo hace **pop**. La variante inversa (el bloqueador hace pop y el otro corta) es otra lectura y no se enseña aquí. |
| The Hoops Geek, guía de Horns | Formación 1-2-2: dos interiores en los codos, tiradores en las esquinas y el base arriba. Distingue la formación de jugadas como Twist, Flare, Flex, Spain, Zoom… |
| Basketball for Coaches, «Pick and Roll» (sección Horns) | El bloqueador elegido continúa y el otro interior se abre detrás del triple. Las esquinas castigan las ayudas largas. La ventaja no aparece si la defensa reacciona perfectamente. |

`template/tactical/plays/v4-horns-twist.json` **es otra jugada** (segundo bloqueo y cambios). Solo he consultado su sistema de coordenadas. No reutilizo ninguno de sus tracks.

## Convención (una sola orientación en todo el vídeo)
- Canasta arriba y cámara detrás del ataque, con yaw 0. En el repo, `x < 0` es la **derecha** de la pantalla, que es la derecha del ataque.
- Posiciones de ataque:
  - O1 arriba con balón (0,35, 9,5);
  - O5 en el codo **derecho** (-2,45, 5,85);
  - O4 en el codo **izquierdo** (2,45, 5,85);
  - O3 en la esquina derecha (-6,6, 1,3);
  - O2 en la esquina izquierda (6,6, 1,3).
- Cada defensor X1–X5 guarda a su homólogo O1–O5. La defensa es individual.

## Cobertura representada (ilustrativa, no «la única»)
- **X5** sale al balón: show y contención temporal delante de la penetración de O1. No desaparece. Recupera tarde.
- **X1** pasa por encima del bloqueo y llega retrasado.
- **X4**, defensor de O4, es el personaje clave. En la decisión está en el hueco (2,3, 5,35), entre el roll y el pop.
- **X2 y X3** se quedan en sus esquinas. No hay zona, ni 2x1, ni rotaciones inventadas.

## La jugada (tiempos reales del play, `marks`)
Hay dos jugadas con base común:
- `horns-rp-a-help` (rama A, HELP);
- `horns-rp-b-stay` (rama B, STAY).

Se generan con `template/tactical/specs/_gen-horns-roll-pop.py`.

| Mark | s | Qué pasa |
|---|---|---|
| align | 2,4 | Formación 1-2-2 completa. Los interiores llegan a los codos desde arriba, nunca desde debajo del aro. |
| setUp | 3,35 | O1 hace un paso a su izquierda para preparar a X1. |
| screenSet | 5,1 | O5 planta el bloqueo en la cadera derecha de X1, a 0,86 m. Está parado: 0,000 m/s entre 5,15 y 5,95 s. |
| screenUse | 5,25 | O1 bota por la derecha y pasa a 0,98 m del hombro de O5. |
| rollPop | 6,0 | O5 abre y hace roll al aro. O4 hace pop al slot izquierdo, a 7,27 m del aro, detrás de la línea de 6,75 m. |
| frame de decisión | 6,6 | Fotograma del gancho, del rehook y del reset A→B. |
| decision (fork) | 6,75 | Los tracks son idénticos en A y B hasta aquí (máx. 0,2 cm). |

**Rama A, X4 ayuda (TAG):**
1. 6,8 s: X4 da dos pasos al carril de O5 y queda a 0,94 m de él.
2. 7,4 s: O1 recoge el bote.
3. 7,55 s: O1 hace un pase por encima a O4, con calle libre a 1,0 m o más de cualquier defensor.
4. 8,2 s: O4 recibe.
5. 8,65 s: O4 lanza. El defensor más cercano está a 2,77 m porque X4 hace el closeout tarde.
6. 9,7 s: canasta.

**Rama B, X4 se queda (STAY):**
1. 6,8 s: X4 sigue a O4 y queda a 1,09 m de él.
2. O5 rueda y abre el pecho al pasador.
3. 7,55 s: O1 le pasa (calle a 0,95 m de X5).
4. 8,0 s: O5 recibe. X5 está a 3,57 m porque sigue en el balón, y X1 sigue detrás.
5. 8,15–8,63 s: paso de reunión.
6. 8,85 s: finalización a dos pies desde 1,32 m del aro.
7. 9,3 s: canasta.

## Pruebas tácticas
- `scripts/test-play.mts`: **49/49 PASS**. Cubre:
  - limites del campo;
  - velocidades ≤ 22 m/s² y balón ≤ 15 m/s;
  - calles de pase;
  - triple detrás del arco;
  - bloqueo legal;
  - claims ligados a cada frase del guion.
- `scripts/test-branches.mts`: **todas PASS**. Comprueba:
  - 10 jugadores idénticos hasta el fork;
  - balón dibujado idéntico;
  - X4 lee distinto en cada rama;
  - resultados distintos: triple frente a finalización en el aro.
- Extensión de `test-branches` en esta rama: `branch.reader` (por defecto X2, como en Chicago) y el resultado `rim_finish`, que es una recepción y finalización del roll sin bote.

## Divergencias frente a la referencia del propietario
- El vídeo de referencia está en `tactical-studio/horns/ref/`: 576×1024, 66,47 s. Lo he revisado con su hoja de contactos de 27 fotogramas, no fotograma a fotograma.
- Tiene cancha de los Knicks, efectos de fuego y rótulos grandes. Nada de eso se reutiliza.
- Solo uso la estructura: formación, roll/pop y foco en el ayudador.
- Ni cancha, ni uniformes, ni locución, ni texto, ni música, ni transiciones del vídeo ajeno.
- Duración de ~43 s frente a 66 s. Una sola cámara alta y estable. Un solo defensor resaltado.

## Afirmaciones que el vídeo **no** hace
- No dice «Horns siempre genera un tiro».
- No dice «imparable».
- No atribuye la jugada a ningún equipo.
- No da estadísticas.

«Might» en la rama B es deliberado: la defensa puede recuperar.
