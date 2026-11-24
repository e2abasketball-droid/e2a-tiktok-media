# E2A Floor Graphics Stability Standard v1

Origen: Arrow Press 1-3-1 V2 (2026-11-24). Se aplica a cualquier reel del motor Tactical3DV2 que dibuje gráficos sobre la pista: áreas de cobertura, líneas de pista iluminadas, rutas, marcadores y glows.

## Comportamiento obligatorio de cada gráfico

1. **Entrada suave.** Fundido de 0,25–0,35 s. Nada de pop, de rebote ni de pulso.
2. **Estado activo estable.** Mientras dura la idea, el gráfico no cambia de opacidad, grosor ni color.
3. **Salida breve.** Fundido de 0,25–0,4 s.
4. **Una sola idea principal a la vez.** Un área activa (o un grupo que forma una idea) más, como mucho, una línea o un carril de pase que la acompañe.
5. **Anclado a la pista.** Los gráficos son mallas 3D del suelo dentro de la misma escena y la misma cámara. No se usan capas 2D pegadas a la pantalla para cosas que viven en la pista.

## Reglas de montaje (dónde nacía el parpadeo)

| Regla | Por qué |
|---|---|
| **Una superposición de cobertura por idea.** Los cambios de jugador activo van dentro de ella con `activeKeys` (fundido cruzado de 0,3–0,35 s), nunca como cadenas de superposiciones que se tocan. | Cada superposición tiene su fundido de salida (0,25 s) y la siguiente su fundido de entrada (0,25 s). Encadenadas, el área cae casi a 0 y vuelve, y eso se ve como un parpadeo. |
| **Mismo fotograma + misma cámara = un solo plano.** No se corta un plano congelado en dos. Las subideas van como tiempos dentro del plano. | Un corte reinicia todas las superposiciones, las esquinas del freeze, el dibujado de las rutas y los pins. Medido en V1: diferencia 2,7 en un corte invisible, frente a 0 en V2. |
| **Si hay que cortar sobre el mismo fotograma, usar `fin: 0` / `fout: 0`** en las superposiciones que continúan (reads → escape). | Así no hay fundido en el corte. `fade()` acepta 0 desde V2; antes daba NaN. |
| **Cambio de aspecto (todas las áreas → área activa) por solapamiento** (`fout` del primero = `fin` del segundo = 0,35 s), nunca uno detrás de otro. | Sin solapamiento hay un hueco. |
| **No poner un marcador sobre un defensor cuya área ya está activa.** | Dos círculos dorados encima del mismo jugador compiten y vibran. |
| **Un único render limpio.** Nunca se mezclan fotogramas de renders distintos (texturas, navegador o PNG frente a vídeo). | V1 mezclaba 3 fuentes. Pasar de una a otra cambiaba la textura del suelo y daba un salto de luminancia (diferencia de unos 5,7 en un plano congelado). |

## Motor (rama `claude/project-thread-cpevo1`)

- `coverage3d.tsx`, en `CoverageOv`:
  - `activeKeys: [[segundo, [ids]], ...]` y `activeFade` (0,3 por defecto): el peso activo se interpola con smoothstep. Color, relleno, grosor y opacidad se mezclan sin caída. La etiqueta se funde con el peso.
  - `stable: true`:
    - sin modulación del borde por la velocidad del defensor;
    - sin pulso del reveal;
    - referencia del balón a 0,4 s muestreada cada 0,02 s (21 muestras), en lugar de 5 muestras, que hacían aliasing con el bote del balón.
- `overlays3d.tsx`: `fade(age, dur, fin, fout)` admite `fin = 0` / `fout = 0` (visible desde el primer o hasta el último fotograma).
- Todo es **opt-in**. Sin `activeKeys` ni `stable` el render es idéntico al anterior. No cambia el motor predeterminado.

**Cómo activarlo en un montaje nuevo:**
```python
cov(0.0, d, mode="active", activeKeys=[[0, ["X5"]], [r1, ["X3"]], [r2, ["X4"]]], activeFade=0.35, dim=0.4, stable=True)
```
Ejemplo completo: `template/tactical/episodes/_gen-arrow131-v2.py`.

## Render

- Usar **chrome-headless-shell** (`/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`), concurrency 4.
- La pista completa con Chromium completo producía fotogramas en mosaico o negros.
- Si aparece un fotograma malo, se vuelve a renderizar todo el vídeo, no se parchea.

## QC obligatorio antes de entregar (`template/scripts/qc-floor-flicker.py`)

Se ejecuta sobre el **MP4 exportado**, no sobre fotogramas sueltos.

| Prueba | Umbral de aprobado |
|---|---|
| Fotogramas malos (oscuros o en mosaico) | 0 |
| Parpadeos (blinks) en tramos congelados | 0 |
| Caídas de luminancia o de oro en tramos congelados | 0, salvo las entradas o salidas que pide el guion |
| Diferencia en un corte sobre el mismo fotograma | Menor que 0,3 (no hay corte invisible) |
| Jitter de oro (2.ª diferencia relativa) por plano | p99 ≤ 0,10 en planos congelados |
| Revisión de todas las cámaras | Todos los planos aparecen en el informe |

Además: una hoja de contactos de los tramos congelados y una comparación lado a lado con la versión anterior.
