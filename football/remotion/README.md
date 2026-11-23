# FBTactical3D — motor 3D de fútbol (Remotion)

Entrada Remotion propia de Football. **No importa nada de `template/`** (baloncesto): tiene su `package.json` con las
mismas versiones exactas de Remotion 4.0.539, three 0.180.0, React 19.1.0 y @react-three/fiber 9.8.2
(`check_isolation.py` comprueba que coinciden con `template/package-lock.json`: un solo motor, sin bifurcar versiones).

| Archivo | Qué hace |
|---|---|
| `src/play.ts` | Lee una jugada `FB-PLAY` y la precalcula en una rejilla de 1/120 s: trayectorias suaves (Hermite), velocidad, orientación con giro limitado (los defensas lentos que retroceden miran al balón), fase de zancada ligada a la distancia recorrida, balón en el pie / pase con frenada / tiro con elevación y red, giro del balón sin deslizar. Determinista: cualquier fotograma sale igual aunque se renderice suelto. |
| `src/athlete.tsx` | Futbolista estilizado articulado (cadera, rodilla, hombro, codo, cabeza) con carrera procedural: amplitud y zancada según velocidad, inclinación por aceleración, inclinación en curvas, brazos opuestos, golpeo (armado, impacto, acompañamiento), estirada del portero. Equipaciones: Navy (E2A), White XI, portero. |
| `src/pitch3d.tsx` | Campo 105×68 con franjas de corte y textura de césped, líneas IFAB, porterías con postes, larguero y red deformable (se abomba con el gol), vallas, gradas, focos y sombras suaves. |
| `src/camera.ts` | Tres cámaras: `overview` (táctica alta), `tracking` (sigue balón/corredor), `detail` (baja y cerrada). Foco suavizado, claves con entrada/salida suave, vibración de cámara opcional. |
| `src/overlays3d.tsx` | Gráficos pintados en el césped: líneas de pase sobre la trayectoria real del balón, flechas de desmarque sobre la ruta real, zonas, línea defensiva, línea de fuera de juego, anillos. |
| `src/screen.tsx` | Capa 2D para Shorts 1080×1920 con márgenes seguros: títulos cinéticos, sellos, etiquetas sobre jugadores, subtítulos palabra a palabra, etiquetas PAUSE / SLOW-MO / REPLAY, logo 2026, cierre. |
| `src/FBTactical3D.tsx` | Composición: planos con reasignación de tiempo (cámara lenta, congelado, repetición), cámaras, gráficos y audio. |
| `src/episodes/*.ts` | Montaje de cada vídeo (guion con tiempos, planos, gráficos). |

## Render

```bash
cd football/remotion && npm ci                       # dependencias propias (node_modules ignorado por Git)
python3 ../scripts/fb_stage.py [--audio src:music-bed.mp3]   # fuentes del motor compartido + logo 2026 -> public/ (ignorado)
CHROME=$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell | head -1)
npx remotion render src/index.ts FBTactical3D out/x.mp4 --gl=swangle --browser-executable=$CHROME --concurrency=4 --timeout=240000 --crf=18
```
`FBTactical3DSilent` = mismo montaje sin música. Un render de 35 s tarda ~17 min con 4 núcleos (swangle, sin GPU).
Los MP4 van a `/mnt/project-files/football/productions/FB-…/renders/`, nunca a Git.
