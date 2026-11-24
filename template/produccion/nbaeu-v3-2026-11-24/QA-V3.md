# QA final V3 (sobre los MP4 exportados)

| Prueba | Resultado |
|---|---|
| G. Formato | 1080 × 1920, 30 fps constantes, H.264 High + AAC 48 kHz, 41,5 s. Hooks: 5,7 s cada uno |
| G. qc-video | **PASS**, sin avisos |
| G. Fotogramas negros (blackdetect) | 0 |
| G. Parpadeo del suelo (qc-floor-flicker) | 0 fotogramas rotos. Pausa de 31,5–33,25 s: 0 parpadeos, 0 caídas |
| F. Audio | -14,1 LUFS, pico real -2,4 dBFS (igual que la V2) |
| F. Voz | la misma toma B de la V2, sin cortes, sin cambios de velocidad ni silencios nuevos. 0 créditos de ElevenLabs |
| F. Música | la misma pista E2A de la V2, sin SFX ni bote de balón |
| D. Cuerpos (qc-nbaeu) | triple EL 11/11, triple NBA 11/11, 3 s NBA 10/10, faltas 6/6 + 6/6, penetración EL 4/4 |
| B. Densidad de texto | 24 regiones (V2: 36). Más de 2 regiones informativas solo 2,0 s (V2: 19,7 s). Ver REDUCCION-TEXTO-V3.md |
| Trial | `E2A-NBA-VS-EUROLEAGUE-V3-TRIAL.mp4`: zoom del 3 %, color, nitidez y EQ suave de voz. SSIM 0,65 frente al original, -14,7 LUFS. Misma toma de voz |
| V1 y V2 | se siguen generando igual (fotograma de V2 re-renderizado idéntico al MP4 entregado). MP4 originales intactos |

## A. Primeros 5 segundos, fotograma a fotograma
Hojas `QA-A-primeros5s-hookA.jpg` y `QA-A-primeros5s-hookB.jpg`, con un fotograma de cada 5.
- **Hook A:**
  - 0–0,7 s: primer plano del jugador, con el balón y la pista NBA azul. Fotograma 0 limpio, sin texto.
  - 0,73–1,52 s: entra la pista de EuroLeague desde abajo y aparecen las pestañas de liga en la costura.
  - 2,7–4,1 s: los dos tiran a la vez y los arcos se dibujan con «rules».
  - 4,12 s: +2 y +3.
  - Sin cortes bruscos, destellos ni negro.
- **Hook B:**
  - 0–2,4 s: pista desde arriba, con el arco azul y luego el naranja y las pestañas en el centro izquierdo.
  - 2,4–3,0 s: la pista se parte.
  - Final igual que en A.

## C. Legibilidad en móvil (fotogramas a 360 × 640, `QA-C-legibilidad-movil.jpg`)
- **Se leen bien:** 12:00, 10:00, +3, +2, los círculos 1–5 y 1–6, FOULED OUT, la cuenta 1-2-3, los tres veredictos, la clave de arcos, los subtítulos y la frase del cierre.
- **Más justo:**
  - El logotipo de EuroLeague dentro del marcador compacto: es horizontal y la celda es estrecha. Se reconoce, pero el texto del logotipo es pequeño.
  - La pestaña NBA del hook, de unos 25 px de alto a escala de móvil.

## E. Reglas (fuentes oficiales; detalle en `../VALIDACION-REGLAMENTARIA.md`)
- **Cuartos:** NBA Rule 5, 12 min. FIBA Art. 8, 10 min. **Sin tiempo total** en voz, subtítulos ni gráficos (el generador se detiene si aparece).
- **Arco:**
  - NBA 7,24 m.
  - FIBA y EuroLeague 6,75 m.
  - El tiro está a 7,05 m: 3 en EuroLeague y 2 en NBA.
  - Las esquinas se omiten en pantalla, a petición del brief.
- **Faltas:** FIBA Art. 40, 5 faltas. NBA Rule 3, 6 personales.
- **3 segundos defensivos:** NBA Rule 10 Sec. VII.
  - Escena A: ataque con control en campo delantero, defensor en la zona más de 3 s sin defender activamente.
  - Escena B: EuroLeague no tiene esa infracción y el pívot defiende el aro.
  - No se dice que no haya restricciones en la zona ni que la zona esté prohibida.
  - Los 3 segundos ofensivos (FIBA Art. 26) siguen existiendo. Esta nota va en el texto de la publicación propuesto.

## Pendiente / no verificado
- **Licencia comercial de los logotipos NBA y EuroLeague sin confirmar.** No publicar hasta que lo decidas. La versión sin logotipos se puede renderizar quitando `template/public/leagues/`.
- **No he escuchado el audio:** es el mismo archivo de la V2, comprobado por medidas.
