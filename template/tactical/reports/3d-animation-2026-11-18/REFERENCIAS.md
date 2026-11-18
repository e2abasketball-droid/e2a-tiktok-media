# Mapa de referencias para las próximas fases (3D · 2026-11-18)

Fuente: índice del propietario `E2A-indice-y-prompt-Claude-3D.md` (Drive `1t9cD7zM1TiYhMry6HlI3SKIP7uCo_YR3`) y
carpeta «Videos jugador». Los intervalos son los del índice (ventanas aproximadas desde 00:00 del original); se
validarán fotograma a fotograma con `tools/ref_frames.py` antes de calibrar cada acción. Lado = perspectiva del
jugador. Ningún vídeo ni fotograma entra en Git: copia local en
`/mnt/project-files/tactical-studio/referencias-3d/<subcarpeta>/<nombre original>`.

**Descarga.** El conector de Drive rechaza archivos de más de 10 MB. Tamaños comprobados hoy con
`get_file_metadata`: 5407 = 10 549 143 B (supera 10 MiB: **necesita copia en la Biblioteca**), 5406 = 10 093 831 B
y 5457 = 10 036 065 B (**frontera**: superan 10 000 000 B pero no 10 MiB; no se ha probado la descarga, prever copia
en la Biblioteca si falla). Según el índice superan el límite seguro 5404, 5405, 5439, 5446 y 5448 (además de 5438 y
5440, ya disponibles en la Biblioteca). El resto se descarga por el conector, una llamada por archivo.

Columna «Acceso»: `Drive` = descarga por conector; `Biblioteca` = el propietario debe subir el original a los
archivos del proyecto; `Frontera` = probar conector, si falla Biblioteca.

## Bote

| Original | Nombre en Drive | Intervalos a usar | Para qué | Acceso |
|---|---|---|---|---|
| 5408 | `E2A_BOTE_ESTACIONARIO_DERECHA_DETALLE_FRONTAL_T05.MOV` | 0.84 primer descenso; 1.13–3.09 ciclos mano derecha; 3.38–5.91 repetición | dedos, muñeca, separación mano-balón, flexión de rodilla (cabeza fuera) | Drive |
| 5410 | `E2A_BOTE_ESTACIONARIO_MANO_DERECHA_DETALLE_T02.MOV` | 0.60–1.05; 1.20–2.20; 2.40 cambio de altura; 3.20–3.60 | contacto con pista y altura del bote (tres cuartos posterior) | Drive |
| 5404 | `E2A_BOTE_ESTACIONARIO_DERECHA_POSTERIOR_CUERPO_ENTERO_T03.MOV` | 3.10–5.68 serie; 6.19–10.84 repetición | duración real del ciclo derecho, pies completos (posterior) | Biblioteca |
| 5405 | `E2A_BOTE_ESTACIONARIO_DERECHA_FRONTAL_CUERPO_ENTERO_T04.MOV` | 2.30–5.36; 5.74–7.66 variación de altura; 8.04 recoge | balanceo de tronco, cabeza, brazo libre (frontal) | Biblioteca |
| 5439 | `E2A_BOTE_ESTACIONARIO_DERECHA_ORBITA_360_CUERPO_ENTERO_T06.MOV` | 0.30–3.40 frente; 4.50–8.60 perfil; 10.30–13.70 espalda; 15.10–18.60 perfil opuesto | contraste multivista del bote (no sincronizar vistas entre sí) | Biblioteca |
| 5407 | `E2A_08_CROSSOVER_DERECHA_A_IZQUIERDA_LATERAL_FRONTAL_T02.MOV` | 1.41–3.52 prepara; 3.55–4.24 cambio (3.65–3.84 cruza, 3.93 recibe izquierda) | crossover, vista frontal | Biblioteca (10,5 MB) |
| 5406 | `E2A_08_CROSSOVER_DERECHA_A_IZQUIERDA_LATERAL_POSTERIOR_T01.MOV` | 4.14 carga; 4.23–4.40 cambio; 4.48–7.20 salida | giro de pelvis y base del crossover (posterior) | Frontera (10,09 MB) |
| 5409 | `E2A_09_ENTRE_PIERNAS_DERECHA_A_IZQUIERDA_FRONTAL_T01.MOV` | 3.10–3.58 (3.32 junto a pierna izquierda, 3.39–3.58 toma izquierda) | entre las piernas, frontal | Drive |
| 5411 | `E2A_09_ENTRE_PIERNAS_DERECHA_A_IZQUIERDA_POSTERIOR_T02.MOV` | 2.74–3.18 (2.87 balón entre los pies) | hueco real de la zancada; que el balón no atraviese el muslo | Drive |
| 5429 | `E2A_MIX_10_CAMBIO_POR_LA_ESPALDA_Y_ENTRADA_POSTERIOR_T01.MOV` | 0.69–1.65 por la espalda; 1.65–3.37 transición a entrada | ficha 10 | Drive |
| 5430 | `E2A_MIX_12_REVERSO_CON_BOTE_Y_FINALIZACION_T02.MOV` | 1.70–2.70 reverso; 3.75–5.45 enlace a finalización | ficha 12 | Drive |
| 5443 / 5442 | `E2A_07_BOTE_AVANCE_DETALLE_APOYOS_T01/T02.MOV` | 5443: 0.69–1.12, 1.33–1.77, 1.96–2.15 · 5442: 1.00–1.40, 1.66–1.96, 2.16–2.81 | sincronía zancada-bote en avance (sentidos opuestos) | Drive |
| 5453 | `E2A_BOTE_ESTACIONARIO_MANO_DERECHA_FRONTAL_ALTA_T01.MOV` | 0.60–1.15; 2.55–3.92 | ciclos consecutivos, cámara alta | Drive |

## Tiro y entradas

| Original | Nombre en Drive | Intervalos a usar | Para qué | Acceso |
|---|---|---|---|---|
| 5418 | `E2A_TIRO_EN_SALTO_LATERAL_T03.MOV` | 1.50–1.87 arma; 2.05–2.13 extensión; 2.13–2.20 suelta; 2.34–2.43 caída | cadena tobillo-rodilla-cadera y arco (perfil, principal) | Drive |
| 5419 | `E2A_TIRO_EN_SALTO_FRONTAL_T01.MOV` | 0.65 flexión; 0.88 subida; 1.27–1.36 despegue y suelta; 1.46–1.57 caída | alineación de piernas y caída (frontal) | Drive |
| 5420 | `E2A_TIRO_EN_SALTO_FRONTAL_DETALLE_T02.MOV` | 0.80–1.20 armado; 1.40–1.60 suelta; 1.80–2.60 muñeca | mano de apoyo, muñeca, codos | Drive |
| 5417 | `E2A_TIRO_TRAS_BOTE_POSTERIOR_T01.MOV` | 1.78–2.23 recoge y carga; 2.45–2.67 suelta | enlace bote-recogida-tiro (y el fallo preexistente del balón en la recogida, ver INFORME) | Drive |
| 5413 / 5414 | `E2A_22_ENTRADA_DERECHA/IZQUIERDA_POSTERIOR_T01/T02.MOV` | 5413: 1.66–3.55 · 5414: 1.35–3.65 | trayectoria de la entrada (posterior) | Drive |
| 5415 / 5416 | `E2A_22_ENTRADA_LATERAL_HACIA_IZQUIERDA/DERECHA_EN_PLANO_T03/T04.MOV` | 5415: 1.95–2.95 · 5416: 2.17–3.26 | dos últimos apoyos, despegue, suelta (perfil) | Drive |
| 5436 | `E2A_24_POSTE_RECEPCION_GIRO_Y_FINALIZACION_T01.MOV` | 1.68–2.16 recepción; 2.40–2.88 giro; 3.60–3.84 suelta | poste: recepción, pivote, finalización | Drive |

## Defensa

| Original | Nombre en Drive | Intervalos a usar | Para qué | Acceso |
|---|---|---|---|---|
| 5431 | `E2A_03_ARRANQUE_LATERAL_Y_FRENADA_LATERAL_T01.MOV` | 0.75 baja cadera; 0.92–1.24 impulso; 1.73–1.95 desaceleración; 2.12 estable | freno escalonado y desplazamiento corto (siguiente piloto: X del bloqueo) | Drive |
| 5432 | `E2A_32_CLOSEOUT_FRONTAL_MANO_DERECHA_T01.MOV` | 0.80–1.00 acorta pasos; 1.20–1.40 mano alta y base | closeout frontal | Drive |
| 5433 | `E2A_32_CLOSEOUT_POSTERIOR_DESACELERACION_T02.MOV` | 1.17–1.43 asentamiento; 1.63–2.04 base | pies de la frenada (posterior) | Drive |
| 5434 | `E2A_31_RETROCESO_DEFENSIVO_POSTERIOR_T01.MOV` | 0.80–1.60 | apoyo corto hacia atrás (secundaria) | Drive |
| 5435 | `E2A_31_DEFENSA_LATERAL_RETROCESO_ZIGZAG_FRONTAL_T02.MOV` | 0.20–0.60; 0.80–1.40 cambio de dirección; 1.60–2.25 | defensa lateral con retroceso | Drive |

## Contacto y secuencias

| Original | Nombre en Drive | Intervalos a usar | Para qué | Acceso |
|---|---|---|---|---|
| 5459 | `E2A_MIX_UNO_CONTRA_UNO_BOTE_PROTECCION_Y_MANO_DEFENSIVA_T05.MOV` | 3.45–6.60 (mano 5.55–5.90); 11.35–16.67 (13.49–14.43) | distancia defensor-manejador, brazo de protección (sin colisión corporal) | Drive |
| 5448 | `E2A_MIX_PASE_RECEPCION_TIRO_POSTE_CONTACTO_Y_CONTESTACION_T06.MOV` | 09.60–15.10; 37.65–40.65; 45.00–48.65; 01:05.65–01:08.60; 01:24.90–01:28.50 | recepción-tiro, contacto lateral, contestación | Biblioteca |
| 5446 | `E2A_MIX_BOTE_CAMBIOS_ENTRADAS_Y_TIRO_SECUENCIA_LARGA_T03.MOV` | 5.55–13.90 cambios; 13.90–18.35 entrada; 45.40–49.10 giro y tiro | transiciones entre acciones (por ventanas) | Biblioteca |
| 5457 | `E2A_MIX_TRIPLE_AMENAZA_AMAGOS_Y_TIRO_T04.MOV` | 0.33–2.31 cargas; 2.96–3.62 amago; 6.53–6.95 tiro | amago frente a tiro real | Frontera (10,04 MB) |

## Ya usadas en esta entrega (bloqueo y continuación, modelo)

5438, 5440 (Biblioteca), 5449, 5450, 5451, 5452 (Drive). Detalle de intervalos e hitos en `INFORME.md`.
