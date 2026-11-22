# E2A Realism V3.1: decisión de diseño

Fecha: 22-11-2026. Rama `claude/realism-v3-1`, creada desde `claude/realism-v3` (`a9db5d1`).

## Problema (medido en la auditoría)

En V3 el cuerpo se movía exactamente igual que en legacy. `Scene.tsx` (rama V3, líneas 318-320 de `a9db5d1`) llama a `poseAt`, la misma pose del motor, y la pasa a `bonesV3`. V3 solo añadía:

- dedos;
- correctivos;
- una capa de peso pequeña (6 cm de bajada de cadera, 11,5° de inclinación).

Sobre el mismo esqueleto, la diferencia se reducía a la piel. Por eso el owner no distinguía los dos lados.

Además había tres limitaciones del puente compartido (`skelclip.ts`):

1. **Pelvis.** Seguía la línea del tronco (`F.hips = twoVec(chest - pelvis, side)`), así que no podía haber una pelvis que cae mientras el tronco contra-inclina.
2. **Pie.** Siempre plano. El talón se derivaba de la puntera (`heel.z = toe.z - 0.01`) y el pie quedaba 4,7° con la puntera hacia abajo: bola del pie 1,15 cm bajo el suelo, talón +0,5 cm (medido con FK del rig V3.1).
3. **Zapatilla.** Era el casco convexo del pie, sin suela.

## Opciones consideradas

| Opción | Qué daría | Por qué no / sí |
|---|---|---|
| A. Seguir afinando `poseAt` (rig.ts) | Cambia legacy también | Rompe la regla «legacy idéntico al píxel»; el motor es procedural por diseño |
| B. Mocap o librería de animación (Mixamo, packs) | Movimiento real | Sin licencia verificable, de pago o con descarga bloqueada; el brief prohíbe mocap sin licencia |
| C. Clips de Blender con keyframes, exportados en el GLB y reproducidos con `AnimationMixer` | Animación «real» en el asset | Un clip fijo no respeta el track táctico: el pie patinaría al retemporizar. En bpy sin interfaz no hay editor de curvas, así que habría que escribir los keys por código igualmente |
| **D. Capa de movimiento AUTORADA en el motor (elegida)** | Keys a mano + calendario de pisadas anclado al track; el pie queda bloqueado | Pura y determinista (seek seguro). Usa el mismo esqueleto y el mismo puente de huesos. El track es solo la raíz. Opt-in por jugador con clip; el resto sigue en la pose del motor |

## Lo que se construyó

**Asset** (`tools/blender/build_player.py --body v31 --shoe v31 --garment v31`; las opciones nuevas no alteran los builds legacy ni V3):

- **Cuerpo.** Set atlético de morphs MakeHuman CC0:
  - músculo macro 0,45 → 0,75;
  - dorsales y V del tronco;
  - deltoides, antebrazos y gemelos;
  - trapecio (`neck-back-scale-depth`);
  - cadera más estrecha y muslo más largo.
- **Zapatilla.** Suela separada (`E2A_Sole.L/R`):
  - contorno = casco 2-D de la parte baja del upper + 5 mm;
  - talón 3,2 cm → antepié 2,1 cm;
  - toe spring de 1,3 cm, bisel de talón y pared abombada.
- **Camiseta.**
  - Sisas profundas: elipse en el plano x-z alrededor de cada hombro, fondo 21 cm bajo la articulación, tirantes de 6 cm. La piel queda visible 3 cm dentro.
  - 1,2 cm de aire sobre el pecho.
  - Holgura de 3 → 4,6 cm hacia el bajo.
  - +0,9 cm de separación en la sisa y la espalda alta.
- **Shorts.** Perneras de 2,0 cm en la entrepierna → 5,8 cm en el bajo.

**Movimiento** (`template/src/t3d/realism-v3-1/motion.ts` + `clips.ts`, todo tecleado a mano):

- **Pisadas.** `{lado, despegue, apoyo, offset adelante/lateral, yaw, altura, pitch de apoyo, toe-off, salto}`.
  - El punto de apoyo se fija con el track en el instante del apoyo y queda bloqueado hasta el despegue.
  - Pivotes sobre la bola del pie.
  - Pitch del pie: toe-off, puntera abajo en el vuelo, golpe de talón al frenar, apoyo sobre la bola al aterrizar.
- **Canales.** Heading, adelanto de hombros, lean, roll, roll de pelvis y bajada de pelvis, con keys cúbicas monótonas (sin sobreoscilación).
- **Capas de la marcha.**
  - Bote de pelvis en cada apoyo y caída de pelvis en el lado en vuelo.
  - Contra-rotación pelvis/pecho.
  - Braceo opuesto a la pierna.
  - Desplazamiento lateral de la pelvis sobre el pie de apoyo.
  - Limitador de alcance: la pierna nunca supera el 98,5 % de su longitud y la pelvis cede con una banda suave de 2 cm.
- **Cabeza.** Objetivos con mezcla: camino, giro antes del cuerpo en el corte, pasador, balón en vuelo, aro. El cuello gira como máximo 70° respecto a los hombros.
- **Brazos.** Modos con fundido: ready, run, brake, reach, give, pocket, triple, jab, dribble, gather, set, shoot, follow, land, defense.
- **Balón.** Mientras O1 lo tiene, es el «socket» de las manos:
  - en la recepción, las manos llegan al balón del motor en `t1` del pase;
  - un solo bote propio (empuje, suelo y vuelta a la mano);
  - suelta en el punto de release del motor, con la altura del salto adaptada para alcanzarlo (0,505 m).
  - Las palmas se corrigen con dos pasadas de IK usando la FK real de la malla.
- **Salto.** Pelvis balística `4H·u·(1-u)` entre el despegue y el aterrizaje.

**Tela L1** (`clothV31`):

- Muelle amortiguado (1,7 Hz, ζ 0,26) movido por la pelvis AUTORADA:
  - la aceleración horizontal da retraso o vaivén;
  - la vertical da vuelo en el salto y asentamiento al aterrizar;
  - la del yaw de pelvis da torsión.
- Límites: 8,5 cm horizontal, +7,5/-3,5 cm vertical, 0,24 rad de torsión.
- Se integra desde `t - 1,2 s` a 120 Hz, así que es pura en `t`.
- La aplica el mismo shader cloth2 (atributos `_E2A_HEM` / `_E2A_EASE`).

**Tela L2** (experimento, no integrado): `tools/blender/cloth_bake_l2.py`. Resultados en `QA.md`, puerta D.

## Integración y fallback

- `athleteRenderer: 'legacy' | 'v3' | 'v31'` en el episodio, el plano o el split.
- Por defecto `'legacy'`. Cualquier otro valor cae en el código legacy, es decir, falla cerrado.
- En `'v31'`:
  - un jugador con clip usa `motionV31` + `framesV31`;
  - un jugador sin clip usa la pose del motor con el puente V3 (`bonesV3`) sobre el asset V3.1.
- Cambios aditivos en código compartido, ambos con valor por defecto que deja todo idéntico:
  - `bonesFromPose(..., hipsUp?)`;
  - `bonesV3(..., hipsUp?)`, más las exportaciones `palmWorld` / `fkHeads` / `baseRig`.

## Limitaciones conocidas de esta decisión

- **Un clip por jugador y por jugada.** El clip está tecleado para esta jugada de prueba; otra jugada necesita su propio clip. La librería reutilizable de clips es el siguiente paso.
- **Sin simulación de tela real.** L1 es una deformación por vértice guiada por un muelle; L2 se probó y no se integra (ver `QA.md`).
- **Mano.** La orientación de la palma sale del plano del codo (limitación de `bonesFromPose`): la mano no gira la muñeca por sí misma.
