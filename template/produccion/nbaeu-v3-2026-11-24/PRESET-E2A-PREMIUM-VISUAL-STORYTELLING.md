# Preset opcional «E2A Premium Visual Storytelling» (V3, pendiente de aprobación)

Es un preset **opcional**. No cambia el estilo global, no toca vídeos anteriores y ningún episodio lo usa si no lo pide.
Código en la rama `claude/project-thread-5a4aj1` del repo e2a-tiktok-media. La V1 y la V2 se siguen generando igual.

## Principio
**Enseña la regla, no la escribas.** Orden de importancia: acción 3D > consecuencia > gráfico esencial > voz > subtítulo.

## Jerarquía de texto (4 niveles)
1. **Dato principal:** +2/+3, 12:00/10:00, círculos de faltas, cuenta 1-2-3, veredicto.
2. **Identificación:** logotipo o pestaña de liga, pequeña y fija.
3. **Subtítulo:** en minúscula, una línea (máximo dos), sin tapar jugadores, arcos ni pies.
4. **Información adicional:** solo si hace falta (cabeceras, notas). Por defecto, nada.

**Regla:** como máximo 2 regiones informativas a la vez (nivel 1 o 4, más el subtítulo). Se comprueba con `scripts/qc-text-density.py`.

## Piezas (todas opcionales)
| Pieza | Cómo se activa | Qué hace |
|---|---|---|
| Subtítulos en minúscula | `"subtitleCase": "sentence"`, `"subtitleSize": 54`, grupos de ≤ 26 caracteres | Frase normal, centrada, peso 800, una línea |
| Marcador compacto | `scoreboard` con `"teams": null, "shot": null` | Solo liga + Q1 + reloj, mismo tamaño para las dos ligas; sin equipos, puntos ni reloj de posesión |
| Pestaña de liga integrada | `leagueLogo` con `"variant": "tab", "dock": "above"/"below", "y": 960` | Pestaña pequeña pegada a la costura de la pantalla partida, sale de la costura (sin tarjeta flotante ni rebote) |
| Pantalla partida animada | `split.ratioKeys: [[t, 1.0], [t2, 0.5]]` | La segunda pista entra desde abajo mientras las cámaras siguen moviéndose |
| Valor con profundidad | `score` con `"enter": "depth", "out": t` | +2/+3 crece desde la pista (0,35 → 1,06 → 1), y al final se eleva y desaparece en 0,28 s |
| Clave de dos líneas | `arcKey` con filas `{league, color, value}` | Una sola caja: color del arco, liga y valor (sustituye a 2 etiquetas + 2 cifras) |
| Pausa discreta | `freeze` con `"label": ""` | Solo esquinas doradas, sin la etiqueta «FREEZE» |
| Faltas sin cabecera | `fouls` con `"label": ""` | Solo los círculos y un único «FOULED OUT» |
| Suelo sin palabra gigante | en el generador, `courtLook.word = ""` sobre una copia de la jugada | La pista se identifica por el color de la zona y la pestaña |

## Cámaras
- **HERO:** primer plano a la altura del hombro, 3/4 por detrás (`pitch` 80, distancia 3,3 m).
- **TACTICAL:** cenital o elevada (`pitch` 22–46) para líneas y espacios.
- **DETAIL:** detrás del tirador (`pitch` 64, distancia 9,6 m) para el tiro.
- **Continuidad:** la misma cámara en las dos ligas cuando se comparan (corte de continuidad). Movimientos suaves y sin giros de más de unos 30°.

## Audio
Se reutiliza la toma aprobada sin tocarla. Música discreta, sin bote de balón y sin SFX.

## Herramientas de QA
- `scripts/qc-text-density.py`: línea de tiempo de textos (nivel, tamaño, posición, duración, solapes y repeticiones).
- `scripts/qc-video.py`, `scripts/qc-floor-flicker.py`, `scripts/qc-nbaeu.mts`: formato, parpadeo y cuerpos.
