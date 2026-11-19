# Logo oficial de E2A (desde el 19-11-2026)

Logo **«E2A Sports Academy»**: «E2A» en blanco con la silueta de Australia, líneas de balón blancas y anillo dorado.
Sustituye al logo anterior (solo «E2A» en blanco) **en todo lo que se cree a partir del 19-11-2026**: vídeos,
portadas, cierres, documentos, webs y propuestas. Regla del propietario, 19-11-2026.

No se redibuja ni se altera: las variantes se sacan del JPG original solo quitando el fondo
(`tools/brand/make_logo_variants.py`, reproducible).

| Archivo | Uso |
|---|---|
| `E2A-Logo-2026-Sports-Academy-original.jpg` | Original del propietario (1254×1254, fondo azul casi negro). Fuente única. |
| `e2a_logo_2026_color.png` | **Por defecto.** Colores originales (blanco + dorado) sobre transparente. Para vídeo y fondos oscuros/azul marino. |
| `e2a_logo_2026_white.png` | Una tinta blanca sobre transparente. Marcas de agua pequeñas o fondos con color. |
| `e2a_logo_2026_navy.png` | Una tinta azul marino #0B1C3D sobre transparente. Fondos blancos o claros (documentos, web). |
| `e2a_logo_2026_on_navy.png` | Logo a color sobre azul marino de marca #0B1C3D, cuadrado y opaco. Avatar, cierres, portadas. |

Nunca pongas el logo a color sobre fondo blanco o claro: el blanco desaparece. Usa la versión azul marino.

## En los motores de vídeo

`template/public/e2a_logo_white.png` **ya contiene el logo nuevo a color** (copia de `e2a_logo_2026_color.png`).
El nombre del archivo se mantiene a propósito: los motores 2D, 3D y Pro y `tools/make_cover.py` (rama de portadas)
lo cargan por ese nombre, así que todas las ramas que se fusionen con `main` usan el logo nuevo sin tocar código.

Para regenerar:

```bash
python3 tools/brand/make_logo_variants.py brand/E2A-Logo-2026-Sports-Academy-original.jpg brand/
cp brand/e2a_logo_2026_color.png template/public/e2a_logo_white.png
```
