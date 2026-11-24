# NBA vs EuroLeague V2: informe comparativo (2026-11-24)

**Archivo:** `E2A-NBA-VS-EUROLEAGUE-V2.mp4`. Sin publicar. La V1 sigue intacta en la carpeta superior.

**Pendiente para cerrar la V2:** los logotipos oficiales. No estaban en el proyecto y no he podido comprobar que tengamos permiso para usarlos. En su lugar la intro y el cierre muestran huecos marcados como «LOGO PLACEHOLDER». Cuando lleguen `nba.svg|png` y `euroleague.svg|png` se colocan solos, y hace falta un render de unos 14 minutos. Después se hará también la copia trial.

## 1. Diagnóstico de la V1 (por qué sonaba leída)
- **Voz:** Deuce con eleven_v3, una sola toma de 49,4 s. No estaba hecha a trozos: la segmentación **no** era la causa.
- **Causas reales:**
  - El guion era una lista: «Rule one: GAME TIME. NBA: seven point two four metres…».
  - Las etiquetas [excited], [emphatic] y [shouting] caían sobre cada cifra.
  - En la edición se cortaron 28 pausas.
  - Se subió el volumen de las palabras clave: THREE +4,5 dB, TWO +6 dB, SIX +4 dB.
- **Sin cambios de tono ni de velocidad en V1.** Mezcla: EQ de presencia, compresión 2,5:1 y -14 LUFS.

## 2. Cambios en el guion
- Guion del brief, con dos microajustes explicados en `GUION-V2.md`.
- Se eliminan «Rule one/two/three», los metros dichos en voz alta y los gritos de cifras.
- La voz explica y los gráficos llevan los números.
- **No hay tiempo total del partido** en la voz, los subtítulos ni los gráficos. El generador lo comprueba solo y se detiene si aparece.

## 3. Interpretación y configuración vocal
- Se generaron dos tomas completas con el mismo narrador y el mismo modelo, en el mismo flujo de ElevenLabs:
  - **A, Natural Conversation:** etiqueta [conversational]. 656 créditos, 38,6 s.
  - **B, Natural Sports Explanation:** etiquetas suaves [curious], [interested], [surprised], [thoughtful] y [playful]. 697 créditos, 37,4 s.
- **Total: 1.353 créditos.**
- Para comparar tramos con la V1 hay archivos al mismo volumen percibido (-16 LUFS): `prueba-vocal/COMPARA-hook|tres|d3s-V1-A-B.mp3`.

| Medida | V1 | A | B |
|---|---|---|---|
| Rango de tono (semitonos, p5–p95) | 12,6 | 9,9 | 10,8 |
| Desviación de tono (semitonos) | 4,5 | 3,5 | 3,7 |
| Ritmo (palabras por segundo) | – | 2,83 | 2,91 |
| Pausas naturales entre frases (> 0,25 s) | cortadas | 3 | 12 (0,25–0,38 s) |

- **Elegida: B.**
  - Respira entre frases con pausas cortas y naturales. A va casi sin respirar en 38 s y suena más a lectura seguida.
  - B tiene algo más de variación que A, sin llegar a los picos gritados de V1.
  - La V1 «mide» más variación precisamente porque gritaba las cifras.
  - No he podido escuchar las tomas: la elección se apoya en estas medidas y en que la alineación de las 109 palabras sale completa en las dos tomas. Conviene que escuches las comparaciones.
- **Postproducción de B:**
  - Toma entera, sin cortes, sin cambios de velocidad o tono y sin refuerzos de palabras.
  - Solo se alargan 6 respiraciones en los cambios de bloque: +0,25, +0,5, +0,7, +0,55, +0,55 y +0,3 s, en total +2,85 s.
  - EQ de presencia, compresión suave 1,6:1 y curva plana.
  - Música E2A sin SFX, unos 21 LU por debajo de la voz.

## 4. Logotipos
- **Procedencia:** ninguna en el vídeo. El propietario indicó como referencia los SVG de Wikimedia Commons (NBA 2017-present y EuroLeague) y el brand center de EuroLeague, sin licencia confirmada para uso comercial.
- Commons marca los dos archivos como «Public domain» para el derecho de autor, pero también como **trademarked**: el uso como marca sigue restringido.
- Por indicación del propietario se mantienen los **placeholders**. Los SVG solo se usaron como referencia de proporciones: NBA 915 × 2079 (vertical) y EuroLeague 960 × 219 (horizontal). Las placas tienen ya esas proporciones, así que al colocar los archivos encajarán sin deformarse.
- No se ha inventado, trazado ni modificado ningún logotipo, y ninguno se ha copiado al repositorio.
- **Integración preparada:**
  - Cada logotipo va sobre una placa blanca, sin deformarse.
  - Aparece cuando la voz nombra su liga: NBA a 0,1 s y EuroLeague a 0,8 s.
  - En el marcador sustituye al nombre escrito.
  - En el cierre aparece en pequeño.
- **Aviso:** el vídeo no se presenta como colaboración ni patrocinio de ninguna competición.

## 5. Nuevo marcador (E2A Broadcast Scoreboard)
- Dos marcadores originales a la misma escala, uno encima del otro.
- **NBA:** Q1 · 12:00 · SHOT 24. Aparece con «In the NBA, each quarter lasts twelve minutes».
- **EuroLeague:** Q1 · 10:00 · SHOT 24. Aparece debajo con «In EuroLeague, it's ten».
- Equipos ficticios NAVY y WHITE, 0–0.
- Se ve el momento antes del salto inicial: las pistas están vacías y no hay balón vivo. Por eso los relojes parados son coherentes.
- Un contorno dorado resalta solo los dos relojes de partido, y debajo aparece «MINUTES PER QUARTER».
- Los dos marcadores quedan juntos en pantalla 2,3 s antes de pasar al triple.

## 6. Componentes modificados (todo opcional; la V1 renderiza igual que antes)
- `src/t3d/broadcast.tsx` (nuevo): BroadcastScoreboard y LeagueLogo.
- `src/t3d/Tactical3D.tsx`: elementos `scoreboard` y `leagueLogo`, y `split.seam: "brand"`.
- `tactical/specs/_gen-nbaeu-v2.py`: jugadas de pista vacía `nbaeu-empty-nba|el`.
- `tactical/episodes/_gen-nbaeu-v2.py`: montaje V2. El generador de la V1 no se ha tocado.
- `tactical/episodes/nbaeu-v2/_voice-v2.py`: alarga las respiraciones.
- Personajes, pistas, arcos, contadores de faltas y la escena de 3 segundos son los de la V1, sin cambios en el motor.

## 7. Problemas corregidos respecto a la V1
- Voz leída y cifras gritadas: nuevo guion y nueva toma, sin refuerzos.
- **Tiempo total (48/40) eliminado en todo el vídeo.** Antes aparecía en el hook y en los relojes.
- Hook con nombres escritos: sustituido por la intro de pista partida con logotipos.
- Relojes esquemáticos: sustituidos por marcadores de estilo retransmisión.
- **Tiro NBA:** ahora es el mismo tiro retomado en vuelo, y el +2 cae justo sobre «two».
- **3 segundos:** la cuenta va a velocidad real, 1 s por número, y la técnica salta con «That's defensive three seconds».

## 8. Defectos pendientes
- Logotipos pendientes (huecos visibles en la intro y el cierre). La V2 **no es publicable** hasta colocarlos.
- Falta la copia trial, que se hará con los logotipos ya puestos.
- En el plano «Different arc» el suelo es el de EuroLeague. Los dos arcos y sus medidas se ven encima en sus colores, pero la palabra EUROLEAGUE del suelo asoma bajo el subtítulo.
- La elección de toma se ha hecho por medidas, no de oído.

## 9. Verificación reglamentaria
- No se pueden abrir desde aquí las webs de official.nba.com, about.fiba.basketball ni mediacentre.euroleague.net (el proxy las bloquea, 403). El detalle está en `../VALIDACION-REGLAMENTARIA.md`.
- **EuroLeague no se trata como FIBA idéntica.** Los cambios 2026-27 de EuroLeague (inicio del tiro, faltas disruptive y flagrant, flopping) no afectan a estas cuatro reglas.
- Cuartos: NBA Rule 5 (12 min) y FIBA Art. 8 (10 min).
- Arcos: NBA 7,24 m con esquinas de 6,71 m, y FIBA 6,75 m con esquinas de 6,60 m.
- Faltas: FIBA Art. 40 (5 faltas, personales y técnicas) y NBA Rule 3 (6 personales).
- **3 segundos defensivos (NBA Rule 10, Sec. VII):**
  - El ataque controla el balón en su campo y el defensor está en la zona más de 3 s sin defender activamente.
  - La sanción es técnica: 1 tiro libre y el ataque conserva la posesión. Esta sanción sale de una fuente secundaria.
  - En EuroLeague no existe la regla y se recuerda que los 3 segundos ofensivos sí existen.
  - No se dice que la defensa zonal esté prohibida.
- **Escena comprobada sobre los cuerpos** (`qc-nbaeu`, 7/7 PASS), en toda la jugada y por tanto también en la ventana usada:
  - X5 está en la zona.
  - Nadie está a menos de 1,2 m de él.
  - Ningún atacante pisa la zona.
  - Solo O1 toca el balón, en campo delantero.

## 10. QC del MP4 exportado
- **Formato:** 1080 × 1920 a 30 fps constantes, 41,5 s, H.264 y AAC.
- **Sonido:** -14,1 LUFS, pico real -2,4 dBFS, sin saturación.
- **qc-video:** PASS, sin avisos.
- **qc-floor-flicker:**
  - 0 fotogramas rotos.
  - Congelado de la técnica (31,5–33,9 s): 0 parpadeos y 0 caídas.
  - La variación del dorado en el plano del marcador NBA es su entrada en cortinilla desde cero, no un parpadeo.
- **Revisión sin sonido** de 21 fotogramas del archivo exportado:
  - intro partida con los huecos de logotipo
  - marcadores legibles y alineados, Q1 y relojes con el mismo formato
  - +3 y +2 sobre «three» y «two»
  - faltas 5 y 6 con FOULED OUT
  - cuenta 1-2-3, técnica congelada y versión EuroLeague
  - cierre en tres líneas
  - los subtítulos no tapan jugadores ni líneas clave
