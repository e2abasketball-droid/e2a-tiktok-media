# Motor de fútbol

Arquitectura preparada en la fase 1 para que los componentes de la fase 2 entren sin rehacer nada.
Convenciones comunes: metros y segundos; origen en el punto central; el equipo que ataca va hacia +x; z hacia arriba.

| Módulo | Qué tendrá | Estado (2026-11-22) |
| --- | --- | --- |
| **Datos de jugada** | `schema/fb-play.schema.json`: equipos, hasta 22 jugadores con keyframes `[t, x, y]`, eventos de balón con altura (`ground/low/lofted`), marcas sincronizadas | **Hecho** + validador `playcheck.py` |
| **Reglas** | `pitch.py`: campo 105×68 (IFAB), áreas, línea de fuera de juego, posición de fuera de juego | **Hecho** (probado) |
| **Inteligencia táctica** | formaciones, presión alta, líneas defensivas, desmarques, tercer hombre, superioridades, pases entre líneas, espacios, transiciones | Formaciones (4) y catálogo de 10 conceptos en `../tactical-library/`; reglas tácticas automáticas en fase 2 |
| **Football 3D Environment** | campo, porterías, red, césped con textura, líneas, estadio, iluminación, cámaras tácticas (cenital, lateral alta) y cinematográficas | Fase 2: `engine/src/pitch3d/` (three.js en una entrada Remotion `FB…` propia) |
| **Football Characters** | jugador y portero 3D, carreras, cambios de dirección, aceleración/frenada, golpeo, pase, tiro, cabezazo, control del balón | Fase 2: `engine/src/athlete/`; reutiliza el pipeline de cuerpo/ropa de Blender/MPFB (categoría B) con equipación de fútbol propia |
| **Visual Effects** | flechas, líneas de pase, seguimiento de jugador, zonas, congelados, repeticiones, zooms, gráficos sincronizados con la voz | Fase 2: `engine/src/overlays/`; los tipos de marca ya están en el esquema (`arrow, passLine, zone, defLine, highlight, freeze, label`) |
| **Composiciones** | `FBTactical3D` (táctica ~35 s) y `FBPro` (historia/curiosidades) | Fase 2: entrada Remotion propia que importa `template/src/pro/*` en lectura y fija las mismas versiones de Remotion |
| **Escenas / animaciones** | `scenes/` y `animations/` por concepto | Se crean cuando haya contenido (sin carpetas vacías) |
