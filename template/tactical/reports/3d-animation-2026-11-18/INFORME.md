# Informe 3D · personaje, bloqueo y continuación (2026-11-18)

Rama `claude/project-thread-qjlep9` (base `84d8906` = `main` con el motor Tactical3DV2 de producción). Sin push, sin
publicación, sin cambios de guion/voz/música. La rama `claude/project-thread-z2h3ja` no se ha portado: el trabajo se
ha hecho sobre la base pedida. «Observado» = visto en la referencia (vídeo + intervalo); «estimado» = inferido.

## 1. Referencias usadas

Todas horizontales 1920×1080, 29,97 fps (30000/1001), HEVC 10 bits HLG (bt2020/arib-std-b67): los fotogramas valen
para pose y silueta, no para color. Copias locales fuera de Git en `/mnt/project-files/…`.

| Original | Archivo (Drive id) | Intervalos usados | Vista / lado | Uso |
|---|---|---|---|---|
| 5438 | `E2A_MODELO_CUERPO_ENTERO_ORBITA_360_POSE_CON_BALON_T01.MOV` (`14teJ27djLimNUBqZX-EwF0UsiiilpntE`, Biblioteca) | 1.50 frente; 4.20 tres cuartos; 7.00 perfil; 13.00 espalda; 18.50 perfil contrario; 21.00 tres cuartos opuesto | cuerpo entero, sudadera, balón en manos | proporciones relativas y silueta |
| 5440 | `E2A_MODELO_CABEZA_Y_HOMBROS_ORBITA_360_T01.MOV` (`1QxOiaOOfupTNAzhxqj1FiAZlMfaZlDDM`, Biblioteca) | 0.60 frente; 1.65 tres cuartos; 2.40 perfil; 4.40 nuca; 6.30 perfil opuesto | cabeza y hombros | volumen de pelo, cráneo, cuello |
| 5449 | `E2A_25_BLOQUEO_PLANTADO_TRES_CUARTOS_T01.MOV` (`1Qs_TyECiiDUmxaCkANwne_HA7pi5KNd9`) | 0.69–1.13 aproximación; 1.13 último paso en el aire; 1.31 base abierta; 1.45–1.80 punto más bajo; 2.40–3.20 sube parcialmente; 3.20 cuerpo entero sin mangas | tres cuartos frontal, sin defensor | llegada, plantado, manos, hombros/brazos sin mangas |
| 5450 | `E2A_25_BLOQUEO_PLANTADO_APROXIMACION_OPUESTA_T02.MOV` (`1aM6B4Ug-cmUuK3gZ7udRPc8wzRhMmyYO`) | 0.73–1.24 aproximación con braceo; 1.38–1.60 junta las manos; 1.83–2.14 base escalonada; 2.60 ligera subida | aproximación desde el otro lado | tiempo hasta estabilizar, manos, base escalonada |
| 5451 | `E2A_26_BLOQUEO_GIRO_Y_ROLL_AL_ARO_T01.MOV` (`1u8K3kpDbFOKBIr0wX4W-M0oNx8GvCfxu`) | 1.25–2.24 aproximación; 2.24–2.39 plantado; 2.39–3.13 mantiene; 3.13–3.33 paso de apertura (pie IZQUIERDO), pivote en el DERECHO; 3.43–3.63 cruce del pie derecho = primer paso; ~3.80 de espaldas a cámara; 3.99–4.30 carrera con mano alta | frontal, aro detrás del jugador | giro a SU IZQUIERDA, apertura de pecho, primeros pasos |
| 5452 | `E2A_26_BLOQUEO_GIRO_Y_ROLL_APROXIMACION_OPUESTA_T02.MOV` (`1I5-pyXrF2bkJOIZYU6hK_MTfCR6RDVEt`) | 1.05–1.73 aproximación; 1.89 establecido; 1.89–2.74 mantiene; 2.74–2.94 paso de apertura (pie DERECHO), pivote en el IZQUIERDO; 3.04–3.24 primer paso; ~3.39 de espaldas; 3.66–4.71 acelera con mano alta | frontal, giro espejo de 5451 | giro a SU DERECHA (es el caso de la jugada de laboratorio) |

Descargas por el conector de Drive (hoy): 5450, 5451 y 5452, una llamada por archivo; bytes del binario descargado =
`fileSize` de Drive en los tres (5 170 468 / 7 306 755 / 7 790 987 B). **Observado**: al copiarlos a
`/mnt/project-files/tactical-studio/referencias-3d/05_Bloqueos_y_cortes/`, el almacenamiento del proyecto inserta una
caja `uuid` de 5 881 B tras `ftyp` (los cuatro MOV de bloqueo, incluido 5449, miden fileSize + 5 881 B). Mismos flujos
y mismo número de fotogramas (ffprobe: 129 fotogramas HEVC en 5450 en ambas copias); no afecta al análisis, pero el
hash local no coincidirá con el de Drive.

Inspección (fuera de Git): `/mnt/project-files/tactical-studio/referencias-3d/_inspeccion/` — `crops/5449.jpg`,
`crops/5450.jpg`, `crops/5451.jpg`, `crops/5452.jpg` (hitos), `crops/5451_giro.jpg` y `crops/5452_giro.jpg` (pies cada
0,10 s durante el giro), `crops/5438.jpg` (seis vistas), `crops/medidas.png` (rejilla de 50 px para medir),
`5440/contact.jpg`.

## 2. Personaje: medidas y cambios

Medidas sobre `crops/medidas.png` (5438 a 1.50 s, frente, de pie; 5449 a 3.20 s, sin mangas, tres cuartos) y la hoja
de 5440. Sin escala absoluta (no hay medida conocida en plano: el aro de 5449 queda al fondo y en otra profundidad),
así que todo es **relativo a la altura de pie** y **estimado** con ±1–2 % por perspectiva y ropa.

| Medida (relativa a la altura) | Referencia | Motor antes | Motor después |
|---|---|---|---|
| Cabeza, coronilla-barbilla sin volumen de pelo | ≈ 0,133 (5438 frente: 107 px / 802 px) | 0,117 | 0,125 (+7 %) |
| Volumen de pelo sobre el cráneo | ≈ 0,015–0,02 (pelo rizado arriba, laterales y nuca cortos: 5440 0.60/2.40/4.40) | 0 (solo color) | ≈ 0,012 (casquete) |
| Anchura de cabeza a la altura de las orejas | ≈ 0,106 | 0,089 | 0,095 |
| Anchura de deltoides / anchura de cabeza | 2,1 (5449, tres cuartos, comprime) – 3,2 (5438, con sudadera, infla) → ≈ 2,6–2,8 | 3,35 | 3,04 |
| Altura de hombros / altura | ≈ 0,817 | 0,826 | 0,826 (sin cambio) |
| Anchura de pantalón (frente) | ≈ 0,26 (pantalón holgado) | 0,177 | 0,187 |
| Torso a la altura del pecho | ≈ 0,19 (5449 sin mangas) | 0,188 | sin cambio |
| Cuello visible (barbilla-escote) | ≈ 0,035 | ≈ 0,03 | sin cambio |

La referencia es un jugador de complexión normal (altura real desconocida); los jugadores del motor miden 1,90–2,10 m
y la cabeza humana no escala con la estatura, así que **no se ha copiado la proporción 1/7,5 completa**: se ha cerrado
la mitad de la diferencia (cabeza +7 %, hombros −5 %). Brazo/pierna y cadera no se han cambiado: la sudadera (5438) y
el balón ocultan codos y cadera, y en 5449–5452 el jugador nunca está de pie con los brazos sueltos.

Cambios (`template/src/t3d/rig.ts` `dimsFor`; `template/src/t3d/Athlete.tsx` `Athlete`):
- `dimsFor`: `shW` 0,215·k → 0,205·k; `headR` 0,112·k → 0,12·k (la cabeza sube 7 mm).
- `Athlete`: la malla de la cabeza escala con `dims.headR`; casquete de pelo oscuro (`G.hair`) con volumen arriba y
  retranqueado sobre la frente; orejas a la nueva anchura; pantalón 1,04→1,10 (ancho) y 0,98→1,02 (fondo).
- Deformación revisada en render (frente, tres cuartos, perfil, espalda) en flexión de bloqueo (t = 2,0 s) y en giro de
  cadera del roll (t = 2,62 s): `vistas_personaje.png` en la carpeta de entregables.

## 3. Movimiento: bloqueo y continuación

### Tiempos medidos (observado)

| Fase | 5449 | 5450 | 5451 | 5452 | Valor usado |
|---|---|---|---|---|---|
| Aproximación | 0.69–1.13 (fin) | 0.73–1.24 | 1.25–2.24 (≈1,0 s) | 1.05–1.73 (≈0,7 s) | ≈1,0 s (dato de jugada) |
| Freno y plantado en dos apoyos | 1.13→1.31→1.45 (≈0,3 s) | 1.83→2.14 (≈0,3 s) | 2.24→2.39 | 1.73→1.89 | dos pasos de asentamiento (simulación) |
| Punto más bajo tras plantar | 1.45–1.80 | 1.98–2.14 | 2.39–2.80 | 1.89–2.30 | 0,22–0,45 s tras `screen.from` |
| Mantiene | 1.80–3.65 (sube a 2.40) | 2.14–3.00 | 2.39–3.13 (0,74 s) | 1.89–2.74 (0,85 s) | 1,0 s incl. plantado |
| Paso de apertura | — | — | 3.13–3.33 (0,20 s) | 2.74–2.94 (0,20 s) | `OPEN_STEP` = 0,20 s |
| Primer paso (cruce del pie de pivote) | — | — | 3.43 (+0,30 s) | 3.04 (+0,30 s) | `CROSS_AT` = 0,30 s |
| De cara a la canasta | — | — | ≈3.80 (+0,67 s) | ≈3.39 (+0,65 s) | `turn` = 0,62 s |
| Pasos siguientes | — | — | 3.53–3.93 cada ≈0,2–0,3 s | 3.14–3.54 | cadencia mínima 2,3 ciclos/s, zancada ×0,72 durante 0,8 s |

**Observado**: manos juntas (una sobre otra) a la altura de la ingle durante todo el bloqueo (5449 1.31–3.65, 5450
1.38–2.60, 5451 2.24–3.13, 5452 1.89–2.74); separación lateral de los pies ≈ 1,15–1,25 × la anchura de deltoides
(5451 2.24/2.39, 5452 1.89), con un pie algo adelantado (5450 «base escalonada»); pivote sobre el pie contrario al
sentido del giro (5451 gira a su izquierda pivotando en el derecho; 5452, espejo); durante el giro, un brazo se abre
hacia el balón (5451 3.50, 5452 3.10) y en la carrera la mano sube como objetivo (5451 3.99–4.30, 5452 3.66).
**Estimado**: profundidad de la flexión (≈0,15 m de caída de cadera en el punto más bajo; sin escala), el reparto de
peso entre pies (no hay plataforma ni vista de suela) y la inclinación del tronco (≈8–10°).

### Implementación (reutilizable, `template/src/t3d/rig.ts`)

- `Action` admite parámetros: `screen` → `width`, `stagger`, `dip`; nueva acción `roll` → `turn`, `side`, `pivot`,
  `face` (ver el comentario del tipo). Una jugada solo declara `{"type":"roll","from":…,"to":…,"face":"O1"}` tras el
  `screen` y una pierna (`legs`) hacia el aro; el resto lo resuelve el rig.
- `simulate`:
  - `baseAt(t)`: base del bloqueo = 1,2 × anchura de hombros con 0,08 m de escalonado; el pie que aterriza usa la base
    del instante de apoyo (`tMid`), así el bloqueador frena en dos apoyos ya abiertos.
  - `roll`: rumbo guiado por una curva adelantada (≈½ del giro en el paso de apertura) en el sentido más corto o
    `side`; pie de pivote plantado; el otro pie da el paso de apertura de 0,20 s alrededor del pivote; a los 0,30 s
    se devuelve el control a la marcha con la fase puesta para que el pie de pivote cruce primero; primeros 0,8 s con
    pasos cortos y rápidos.
  - **Corrección general de deslizamiento**: swings de ≤ 0,4 s (≤ 0,22 s si el cuerpo acelera), aterrizaje acotado al
    alcance de la cadera y «guardia de alcance» que levanta un pie plantado al que la cadera ya ha dejado atrás.
- `poseAt`:
  - flexión del bloqueo con perfil temporal (baja al plantar, mínimo a 0,22–0,45 s, se asienta algo más arriba);
  - manos juntas a la ingle con codos algo abiertos;
  - `roll`: pecho abierto hacia `face` durante el giro (±0,7 rad), mano del lado del balón como objetivo y luego alta,
    flexión que se libera en 0,55 s; tronco casi erguido durante el giro y los primeros pasos (inclinación lateral
    ×0,25, inclinación por aceleración ×0,4, descenso de carrera ×0,5): ajuste hecho tras comparar con 5452
    2.84–3.66 en la hoja de contacto (commit `960780f`);
  - **tope de altura de pelvis**: envolvente suave en el tiempo (min-filtro + media ±0,07 s) de la altura desde la que
    los pies plantados son alcanzables; siempre ≤ al tope exacto (el pie no puede resbalar) y sin saltos al apoyar o
    levantar.

## 4. Jugada y bundles de laboratorio

- `template/tactical/specs/_gen-screen-roll-lab.py` → `screen-roll-lab.spec.json` → `tactical/plays/screen-roll-lab.json`
  (pick-and-roll lateral en el ala derecha: O1 manejador con bote, O5 bloqueador/roller, X1 defensor del balón, X5
  defensor del bloqueador en drop; O2–O4/X2–X4 abiertos para cumplir 5 contra 5). Tiempos de las referencias (tabla).
- `template/scripts/screen-roll-lab-bundle.py` → `out/lab/screen-roll-lab-{real,slow,close,view-*}.bundle.json`
  (sin voz: WAV silencioso generado con ffmpeg en `public/tactical/_lab/`, ignorado por Git; palabras ficticias con
  subtítulos ocultos). Cámara fija tres cuartos desde arriba de la pista (`yaw −22`, `pitch 62`, `dist 12`), vertical
  1080×1920, bloqueador y manejador en el mismo plano. Lento = remap del motor a 0,4× (juego 1,15–3,35 s en 5,5 s).

### Comandos reproducibles

```bash
cd template
python3 tactical/specs/_gen-screen-roll-lab.py
node --experimental-strip-types scripts/build-play.mts tactical/specs/screen-roll-lab.spec.json tactical/plays/screen-roll-lab.json
node --experimental-strip-types scripts/test-play.mts tactical/plays/screen-roll-lab.json
node --experimental-strip-types scripts/qc-contact.mts tactical/plays/screen-roll-lab.json
python3 scripts/screen-roll-lab-bundle.py
CHROME=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell | head -1)
npx remotion bundle src/index.ts --out-dir /tmp/claude-0/run/bundle-after
npx remotion render /tmp/claude-0/run/bundle-after Tactical3DV2 out/lab/after-real.mp4 --props=out/lab/screen-roll-lab-real.bundle.json \
  --gl=swangle --browser-executable=$CHROME --concurrency=4 --timeout=180000 --scale=0.5     # 129 fotogramas
# igual con screen-roll-lab-slow.bundle.json (165 fotogramas); el «antes» con el mismo bundle sobre un worktree en 84d8906:
git worktree add /tmp/claude-0/run/wt-before 84d8906 && ln -s $PWD/node_modules /tmp/claude-0/run/wt-before/template/node_modules
mkdir -p /tmp/claude-0/run/wt-before/template/public/tactical/_lab && cp public/tactical/_lab/silence.wav $_
(cd /tmp/claude-0/run/wt-before/template && npx remotion bundle src/index.ts --out-dir /tmp/claude-0/run/bundle-before)
```

Los props llevan la jugada embebida, así que antes y después usan exactamente el mismo dato; el motor de `84d8906`
ignora la acción `roll` (no la conoce): esa es la diferencia que se compara.

## 5. Entregables (fuera de Git)

Carpeta `/mnt/project-files/tactical-studio/3d-animation-2026-11-18/`:

| Archivo | Contenido |
|---|---|
| `comparativa_real.mp4` | antes (84d8906) │ después (960780f), 1080×960 (dos paneles 540×960 = render vertical 1080×1920 a escala 0,5), 4,3 s, 30 fps, juego 0,3–4,6 s |
| `comparativa_lenta.mp4` | igual, cámara lenta del motor 0,4× (juego 1,15–3,35 s en 5,5 s): plantado, transferencia y primer paso |
| `comparativa_real_y_lenta.mp4` | las dos anteriores encadenadas (9,8 s) |
| `contacto_referencia_vs_render.png` | REF (5449 1.45; 5452 2.30/2.84/3.10/3.24/3.66) │ ANTES │ DESPUÉS en plantado, mantiene, apertura, giro, primer paso, carrera (bloqueador solo, primer plano tres cuartos) |
| `vistas_personaje.png` | frente, tres cuartos, perfil, espalda; antes/después; flexión de bloqueo (2,00 s) y giro de cadera (2,62 s) |

Misma jugada, mismos props, misma cámara y mismo remap en ambos motores; solo cambia el código.

## 6. QC

### `qc-contact.mts` (nuevo) antes → después

Deslizamiento = movimiento del tobillo RENDERIZADO (tras IK) mientras el pie simulado está plantado. Holgura = distancia
mínima entre cápsulas de torso (pelvis→pecho, r = 0,15·k) y esferas de cadera (r = 0,095·k) de cualquier pareja
(negativa = interpenetración). Mano-balón: hueco máximo con balón sujeto (sin bote) y peor hueco de contacto por bote.
`-` = la jugada no tiene tramos de balón sujeto fuera de pases/tiros.

| Jugada | Deslizamiento máx. (mm/fotograma) | Holgura mín. (m) | Hueco balón sujeto (m) | Hueco bote (m) |
|---|---|---|---|---|
| screen-roll-lab | **127,9 → 0,0** | 0,160 → 0,150 | - | −0,024 → −0,030 |
| stagger-a-trail | **138,5 → 0,0** | 0,107 → 0,104 | 0,408 → 0,414 ✗ | −0,031 → −0,033 |
| stagger-b-backdoor | **124,9 → 0,0** | 0,008 → 0,005 | 0,210 → 0,211 ✗ | −0,043 → −0,035 |
| hammer-a-skip | **166,9 → 0,0** | 0,257 → 0,257 | 0,193 → 0,198 ✗ | −0,028 → −0,030 |
| hammer-b-rim | **156,0 → 0,0** | 0,205 → 0,205 | - | −0,035 → −0,038 |
| spain-a-roll | **160,7 → 0,0** | 0,030 → 0,028 | - | −0,036 → −0,037 |
| spain-b-pop | **165,1 → 0,0** | 0,029 → 0,027 | 0,352 → 0,358 ✗ | −0,036 → −0,037 |

- Deslizamiento: el motor de producción arrastraba el pie plantado hasta 13–17 cm por fotograma en arranques y frenadas
  (la pierna no llegaba al pie y el IK lo recortaba). Corregido en todas las jugadas.
- Suavidad vertical de la pelvis (segunda diferencia máxima por fotograma; los picos son saltos de tiro o bandeja en
  ambos motores): lab 83 → 93 mm, hammer-a 87 → 92, stagger-a 47 → 58, stagger-b 72 → 77, spain-a 72 → 57.
- Hueco con balón sujeto ✗ **preexistente, no tocado**: en recepción-y-tiro el balón deja de seguir a las manos en
  cuanto empieza la acción `shoot` (0,5 s antes de soltar). Queda para la fase de tiro (5417/5418/5419).
- Ninguna interpenetración (holgura ≥ 0). stagger-b y spain rozan 0 (contacto de bloqueo), igual que antes.

### `test-play.mts`

Las 10 jugadas en verde (0 FAIL), incluida `screen-roll-lab` (20/20 genéricas + 5 claims; bloqueo legal 0,000 m/s).

### `qc-tactical3d.mts` antes → después

stagger-screen 9/9 → 9/9, stagger-screen-v2 9/9 → 9/9, hammer-screen 9/9 → 9/9, spain-pick-and-roll 9/9 → 9/9
(elevator-screen es el episodio 2D: el único FAIL, «duración 65,9 s», es igual antes y después y no depende del rig).

## 7. Pendiente y tomas que faltan

- **Defensores del bloqueo**: no hay toma de top-lock/negación ni de paso por encima/debajo del bloqueo con contacto;
  X1 sigue usando `stance` y la trayectoria de la jugada. Faltaría: ficha 34 (por encima / por debajo), tres cuartos,
  cuerpo entero, con un bloqueador real (≥ 4 s).
- **Contacto bloqueador-defensor**: 5449–5452 son tomas en solitario; el «golpe» y la reacción del defensor no se pueden
  validar. Faltaría una toma con dos jugadores y cámara lateral fija (pies visibles).
- **Escala absoluta**: ninguna toma de modelo tiene una medida conocida en el mismo plano. Bastaría una toma de 5438
  junto a la línea de tiros libres o con la altura real del jugador anotada.
- **Hombros y brazos**: sin una pose en T/A sin mangas (5438 lleva sudadera y balón); propuesto: órbita cuerpo entero
  con camiseta sin mangas y brazos separados 30°.
- **Reparto de peso** en el plantado: estimado; no se ve la carga en suela. Una toma lateral baja a la altura de los
  tobillos lo resolvería.
- Balón en recogida de tiro (✗ preexistente) y transición `roll`→recepción en carrera: siguiente fase con 5418/5419/5417.
- El cambio de alcance de pies afecta a todas las jugadas (mejora medible); conviene revisar visualmente un episodio
  completo antes de re-renderizar producción.
