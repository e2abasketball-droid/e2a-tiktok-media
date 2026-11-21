# D2 — ADR: Realism V2 (2026-11-21)

## Contexto
El render es por CPU (swangle) y no hay GPU. Cada Reel tiene unos 1200 fotogramas y un presupuesto de 0 USD. El motor procedural (`rig.ts`) ya da jugadas tácticas exactas: pistas, reloj, balón. Los defectos visibles están en los contactos (manos y balón), en el balón dentro del cuerpo, en los giros y pies, y en una ropa sin física (ver AUDITORIA.md).

## Decisiones

1. **Rig híbrido, procedural primero.**
   - La pista de la jugada sigue siendo la autoridad de posición y reloj.
   - Los clips mocap (`skelclip.ts`) se usan por jugador y por acción solo cuando superan los gates. Hoy hay 2 clips; ver `src/t3d/motion-library.v1.json`.
   - *Alternativa descartada:* sustituir la animación por mocap completo. No tenemos capturas propias suficientes (solo 5452, frontal, a 30 fps) y se perdería la exactitud táctica.

2. **Contactos como restricciones, no como poses.**
   - El balón sostenido se resuelve en el marco del cuerpo (rumbo real del tronco).
   - Un *solver* de tronco lo saca de la elipse pelvis→pecho de la POSE (`setTrunkHook`) y de la cabeza; la cabeza siempre por delante.
   - Las palmas se fijan a la superficie del balón con IK de contacto: 4 pasadas, con la mano tangente al balón.
   - En el hand-off: mano derecha ARRIBA, mano izquierda DETRÁS. El receptor alcanza desde t0−0,3 s. Al soltar, las manos se despegan en 0,2 s y vuelven al cuerpo en 0,18 s.
   - Al cambiar de evento, el balón continúa: el desfase se suaviza en 0,15 s.
   - *Descartado:* física rígida del balón. Rompe la exactitud del guion táctico y no aporta en planos de 1–3 s.

3. **Locomoción.**
   - Rumbo limitado a 12 rad/s (688°/s).
   - Un jugador lento (< 0,2 m/s) solo levanta el pie que está fuera de su base.
   - El bote va más abierto y adelantado con la velocidad: 0,34 m lateral y 0,36 + 0,04·v m adelante.
   - El bloqueo del pin-down tiene un ángulo FIJO (dato de la jugada, `face` numérico).

4. **Ropa: LOD-B en tiempo real.**
   - Nueva malla v2 (`build_player.py --garment v2`):
     - camiseta con caída recta desde el pecho, 3,5 cm más larga y siempre por fuera del pantalón;
     - 45 % del peso del muslo se conserva en el bajo, así la rodilla empuja la tela;
     - cintura del pantalón con peso de pelvis;
     - atributos `_E2A_HEM` / `_E2A_EASE`.
   - Movimiento secundario en el vertex shader (`cloth2.ts`): un muelle amortiguado de 1,6 Hz y ζ 0,32, excitado por la aceleración de la pelvis, la altura de salto y la aceleración angular del rumbo. Produce *sway*, torsión y *flutter* con tope y nunca entra en el cuerpo más del 85 % de la holgura.
   - Es determinista por fotograma, así que no hay *flicker* entre los trozos del render paralelo.
   - **LOD-A, el horneado de cloth en Blender, queda PENDIENTE DE EJECUCIÓN.** No se ha ejecutado.
   - *Descartado ahora:* la simulación de tela por fotograma. Es inviable en CPU para 1200 fotogramas × 10 jugadores y no es determinista entre procesos.

5. **Exportación y rendimiento.**
   - GLB v2 de 1,30–1,32 MB, frente a 1,30 MB en v1, con el mismo esqueleto y el mismo rig.
   - El coste por fotograma se mide en el A/B (D7).

6. **Interruptor y compatibilidad.**
   - Todo va tras `play.realism >= 2` (`realismV2`). Sin esa clave, el motor da poses y balón idénticos a `d700987`: 12 jugadas comprobadas por hash; ver QA.md.
   - Para volver a legacy en un episodio V2, quitar `"realism": 2` del spec/play o usar `qc-realism --legacy`.
   - Por defecto ON solo en las jugadas nuevas generadas con el preset V2 (TACTICAL3D.md).

## Compromisos aceptados
- Skinning lineal: el estiramiento de axilas (p99,9 ×2,06) y los brazos dentro de la camiseta en sprint (4,9 cm) siguen igual que en la base. Se resuelve con *dual quaternions* o con *corrective shapes* (propuesto).
- La cabeza del gate es una cápsula vertical burda. En el tiro, el balón sale 2–4 cm «dentro» de esa cápsula, aunque visualmente pasa por delante de la frente.
