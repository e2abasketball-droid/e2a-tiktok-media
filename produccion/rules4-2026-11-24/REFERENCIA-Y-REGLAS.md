# 4 Rules: análisis de la referencia y verificación reglamentaria (2026-11-24)

## Vídeo de referencia (subido por el propietario, solo para análisis)
- Duración: 44,2 s, 464×832, 30 fps.
- Cortes por escena detectados: 6,97 s y 32,1 s. El resto son transiciones con barrido naranja.
- Estructura:
  - título «Basketball rules in 40 seconds» (0–2,5 s);
  - 01 Traveling (≈ 3–9 s);
  - 02 Double dribble (≈ 9–16 s);
  - 03 Scoring (≈ 17–25 s);
  - 04 Fouls (≈ 26–35 s);
  - «Now you know the basics» (≈ 36–39 s);
  - tarjeta final de TikTok (≈ 39–44 s).
- Recursos: figuras 2D de palo, un jugador por escena, sello rojo ✕ y verde ✓, rótulo de la regla arriba y frase explicativa abajo.
- **Lo que conservamos (formato, no material):** cuatro bloques secuenciales, explicaciones cortas, pocos jugadores y contraste legal/ilegal.
- **Lo que NO copiamos:** animaciones, gráficos, colores, música, narración y el final con logotipo largo. Todo lo nuestro es original: motor 3D E2A V3.3, voz Deuce y música sintetizada E2A.
- **Mejoras:**
  - el hook ya muestra las cuatro reglas en 4 s, en lugar de un título de 2,5 s;
  - cierre de 3,8 s que enlaza con el primer fotograma (loop), sin tarjeta de 5 s.

## Reglas comprobadas (FIBA Official Basketball Rules)
No se pudo abrir el documento oficial desde el contenedor: about.fiba.basketball está bloqueado por la red (`curl` 000). Por eso la versión 2026 v1.1 **no se ha verificado en directo**. Las demostraciones siguen el texto de las reglas FIBA vigentes que conocemos (edición 2024), que en estos puntos no ha cambiado de forma sustancial. Conviene una revisión humana con el PDF de 2026 antes de publicar.

| Regla | Qué dice | Cómo lo enseña el Reel | Control automático |
|---|---|---|---|
| Art. 25 Travelling | Con los dos pies en el suelo al recibir, cualquiera puede ser pie de pivote. El pie de pivote puede levantarse en un pase o tiro, pero **no volver al suelo** antes de soltar el balón. | O1 recibe con los dos pies apoyados y pivota legalmente sobre el izquierdo (✓ LEGAL PIVOT). Después levanta el izquierdo y lo apoya 30 cm por delante con el balón en las manos (✕ TRAVEL). Sin bote ni gather step: el ejemplo no es ambiguo. | `qc-rules4` travel 11/11: el pie no se desliza en el pivote (0 cm), se levanta 10 cm, vuelve a tocar el suelo y el balón no sale de las manos. |
| Art. 24 Dribbling | El regate termina cuando el jugador toca el balón con las dos manos a la vez o lo deja descansar en una mano. No puede volver a botar salvo que haya perdido el control por un tiro, un toque de un rival, etc. | Bota, recoge con las dos manos (DRIBBLE ENDED), lo sostiene 1,3 s y vuelve a botar. **Nadie más toca el balón** y no hay defensor en pantalla. | `qc-rules4` dribble 7/7: balón en dos manos el 100 % de la sujeción, nunca cerca del suelo y segundo bote real. |
| Art. 16 Valor de las canastas | Tiro libre 1. Canasta desde la zona de 2: 2. Desde la de 3: 3. **La línea de tres no forma parte de la zona de tres.** | +1 desde detrás de la línea de TL. +2 a 4,8 m. +3 a 7,0 m con los dos pies fuera. Pie sobre la línea: «ON THE LINE = 2». | `qc-rules4`: TL con la puntera a ≥ 5,85 m de la línea de fondo. Dos: suela más lejana a 6,7 m o menos. Tres: suela más cercana a más de 6,75 m. Línea: puntera a 6,695 m (la línea va de 6,70 a 6,75 m, la suela la pisa) en el despegue. |
| Art. 33/34 Contacto y falta personal | Agarrar (holding) es un contacto ilegal que impide la libertad de movimiento. | X1 agarra a O1 por la cintura con la mano izquierda y le frena: la velocidad pasa de 3 m/s a 0,15 m/s. Sin empujón violento ni caída teatral. | `qc-rules4` foul 6/6: la palma, sobre la superficie de la cadera (± 7 cm). Los cuerpos no se atraviesan (torsos a más de 0,42 m). |
| Penalización por faltas de equipo (Art. 41 en la edición 2024; el brief cita el 42) | Una falta personal sin tiro se sanciona con saque si el equipo no ha llegado a la penalización (4 faltas de equipo en el periodo). | Saque de banda y «NOT EVERY FOUL = FREE THROWS». Un microtexto aclara «NON-SHOOTING FOUL · TEAM NOT IN PENALTY». No se dice que todo contacto sea falta. | Revisión del guion. |

**Correcciones frente a la referencia:**
- La referencia enseña la falta como «golpe en el brazo del tirador → tiros libres». Es correcto, pero puede hacer pensar que toda falta da tiros libres. Nuestro Reel muestra la falta sin tiro y el saque.
- La referencia dice «behind the 3-point line = 3». Añadimos el caso de la línea: pisarla vale 2.
