# Realism V3.3 — 03 MOTION QA

Mismo QC y mismos umbrales que V3.2:
- pop de cadera o cabeza: 60 m/s²;
- pop de muñeca: 400 m/s²;
- tobillo: 600 m/s²;
- rodilla > 150° o < −3°, codo > 155°, cuello > 80°;
- deslizamiento de pie apoyado;
- suelo.

Las aterrizadas de salto se excluyen igual que en V3.2.

| | One-take V3.2 | One-take V3.3 | Trío V3.2 | Trío V3.3 | 5v5 motor legacy | 5v5 V3.3 |
|---|---|---|---|---|---|---|
| Filas totales | 27 | **2** | 23 | **5** | 899 | **20** |
| Deslizamiento de pie máx. | 1,6 cm | 1,6 cm | 0,7 cm | 0,7 cm | 55,7 cm | **1,4 cm** |
| Cadera máx. (m/s²) | 237 | **120** | 194 | **67** | 1257 | 457 (X4, 1,575 s) |
| Cabeza máx. | 238 | **155** | 470 | 404 | 1264 | 457 (X4, 1,575 s) |
| Muñeca máx. | 994 | **433** | 765 | **393** | 8985 | 795 |

**Objetivo del brief:** menos de 20 filas y deslizamiento ≤ 1,6 cm.
- One-take: **cumplido** (2 filas, 1,6 cm).
- Trío: cumplido (5 filas).
- 5v5: **20 filas, en el límite; no está por debajo de 20.**

## Filas que quedan (con segundo)
- **One-take:**
  - `pop:head` 3,1 s y `pop:wrL` 2,4 s. Las dos existían ya en V3.2.
- **Trío:**
  - 5 `pop:head` (60–115 m/s²) en las frenadas O2 1,43 s y X2 1,73 s y en X2 4,13 s. Aparecen también en V3.2 con valores parecidos (75–87).
- **5v5:**
  - **O1:**
    - cabeza 5,3 s (101);
    - muñeca 6,1 y 6,2 s (hand-off);
    - cadera y cabeza 9,07 s (376): arranca a trotar desde la postura relajada en la fase de cierre. **P1.**
  - **O2:**
    - cabeza 6,0, 6,2 (304), 6,5 y 6,53 s: despegue y caída del triple rápido. **P1.** Se ve como una sacudida de cabeza de 1 frame al despegar; la causa no se ha cerrado.
    - muñecas 4,8–5,47 s (420–540): brazos en carrera rápida a 3,9 m/s rodeando a O1. **P2.**
  - **X1:** 9,1 s (70): cambio de postura. **P2.**
  - **X2:** codo a 162° en 6,6 s (contest con el brazo estirado). **P2.**
  - **X4:** cadera y cabeza 1,57–1,6 s (169): arranque lateral desde la defensa. **P1.**

**Nota sobre el detector:** el QC heredado de V3.2 solo escribe una fila cada 4 muestras de 120 Hz. Por eso hay picos aislados que están en «máx.» pero no en las filas. Se mantiene así para que la comparación con V3.2 sea la misma. Los picos que no aparecen en las filas del 5v5 son:
- O5 en 1,14 s, cadera 290 m/s² (arranque en la fase de preparación);
- X2 en 1,29 s, 176 m/s²;
- X1 en 8,99 s, 119 m/s²;
- X3 en 7,95 s, 110 m/s².

Son **P1/P2** y se ven como un pequeño tirón al arrancar desde parado.

## Robustez con dos perfiles corporales
El 5v5 se pasó con todos los jugadores en el cuerpo `off` y con todos en el cuerpo `def`. Son dos builds distintos: hombros de 25,0 y 26,9 cm de semiancho.
- Resultado: las mismas 20 filas.
- Cadera máx. 457–458 m/s², muñeca 795 m/s².
- Ninguna penetración del balón.

Archivos: `qa/5v5_v33_rigoff*.json`, `qa/5v5_v33_rigdef*.json`.

## Determinismo
`scripts/qc-determinism-v33.mts`: huesos y balón de todos los jugadores en orden ascendente, descendente y aleatorio (con caché en frío y en caliente).
- **Idéntico bit a bit** en one-take (376 frames), trío (226) y 5v5 (331 frames × 10 jugadores).
- `qa/determinism_*.json`.
