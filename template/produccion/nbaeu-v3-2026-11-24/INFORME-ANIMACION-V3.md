# Informe de animación V3

Motor 3D global **sin cambios** (cuerpos v33, entorno cinema). Todo lo nuevo es opcional y está en el generador de la V3 o en piezas de pantalla. La V1 y la V2 se renderizan igual: lo he comprobado con un fotograma de la V2 re-renderizado, idéntico al MP4 entregado.

## Hooks
- **Hook A (principal):** primer plano del tirador a la altura del hombro, 3/4 por detrás. La cámara sube y se abre (unos 30° de giro en 2 s, sin vueltas). Con «EuroLeague» entra la pista de EuroLeague desde abajo (pantalla partida animada, 0,73–1,52 s). Las dos cámaras quedan iguales y los dos tiradores lanzan a la vez: el balón entra a los 4,12 s, con +2 arriba y +3 abajo.
- **Hook B:** una sola pista vista desde arriba. Se dibuja el arco NBA (azul) con «NBA» y el FIBA (naranja) con «EuroLeague», y el tirador queda entre los dos. La cámara se inclina y gira 14°. Con «But the rules…» la pista se parte y entra la de EuroLeague. El final es el mismo tiro doble con +2/+3 que en A.
- **Sin pantalla negra:** el paso a los cuartos es un corte directo.

## Triple: «Same shot. Different value.»
- Un solo plano en EuroLeague (10,9–15,0 s): vista táctica con los dos arcos y el aro dorado en el punto de tiro. Con «From the exact same spot» la cámara baja detrás del tirador (plano de detalle, más cerca que en la V2) y el tiro completo entra con «three». El +3 crece desde la pista y se eleva al salir.
- **Corte de continuidad al NBA (15,0 s):** el mismo tiro, desde el mismo punto (7,05 m), con la misma cámara y desde el mismo momento antes de soltar. Velocidad real 1,0. El balón entra a los 16,4 s, con «in the NBA», y aparece el +2.
- **Pies:** el tirador no se desplaza en toda la jugada, con la pista fija y sin deslizamiento. QC de cuerpos de las dos jugadas: 11/11 PASS (suelas sobre el suelo, balón fuera del cuerpo, cada pie respecto a los dos arcos).
- **Arcos:** plano breve con los dos arcos y una sola clave de color, sin distancias de esquina.

## Faltas
Las mismas escenas de contacto de la V1 y la V2: 6/6 PASS en cada liga. Solo cambian los gráficos (sin cabecera).

## Tres segundos defensivos
- **Cámara:** elevada en 3/4 (giro −26°, 42° desde la vertical), la misma en las dos escenas.
- **Escena A (NBA):** el ataque controla el balón en campo delantero y X5 está en la zona sin defender a nadie, marcado con un aro rojo discreto. La cuenta 1-2-3 va a velocidad real (1 s por número). Con «That's defensive three seconds» aparecen el veredicto y una pausa corta con esquinas, sin etiquetas, y se corta a EuroLeague 0,15 s después de la frase (la pausa dura 1,8 s; en la V2 eran 2,4 s). QC: 10/10 PASS. X5 está en la zona, nadie a menos de 1,2 m, ningún atacante en la zona y solo O1 toca el balón.
- **Escena B (EuroLeague): nueva jugada `nbaeu-drive-el`.** Mismos 10 jugadores y posiciones iniciales que la escena A.
  - O1 lee la defensa 1,3 s y penetra por la izquierda. X1 le sigue por el otro lado.
  - X5, que sigue en la zona (legal en EuroLeague), da un paso y defiende el tiro con los brazos arriba justo con «protect the rim».
  - X2 y X3 cierran la ayuda. O1 se para y la saca a O2, y X2 sale a defenderle.
  - Va a velocidad real y no es una estatua.
  - QC 4/4 PASS. La distancia mínima entre torsos es de 0,62 m (sin choques). El balón nunca entra en un cuerpo y las suelas no bajan del suelo.
  - O1 está menos de 1,5 s en la zona y en penetración, y O5 no entra, así que no hay 3 segundos ofensivos.

## Cierre
Pantalla partida con los dos tiradores en el mismo encuadre que el hook, para enlazar en bucle con el inicio. Lleva la frase única y el logotipo E2A pequeño sobre la costura 0,1 s después de la pregunta, que queda 1,05 s en pantalla.

## Limitaciones honestas
- Durante los 1,3 s previos a la penetración, los jugadores sin balón solo mantienen su postura defensiva u ofensiva, sin desplazarse.
- En el hook, el balón roza el borde superior de cada mitad cerca del aro durante unos fotogramas.
- La cuenta 1-2-3 tapa en parte el tablero de la canasta. Ningún jugador queda tapado.
