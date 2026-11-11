"""Markdown report (Spanish) for an analysis.json. Used by analyze_video.py; also runnable:
  python3 report.py <analysis.json>   -> prints the report
"""
import json
import sys

TAG = {"observacion": "observación", "estimacion": "estimación", "hipotesis": "hipótesis"}


def tag(level):
    return f"`[{TAG.get(level, level)}]`"


def fmt_list(xs, n=12):
    xs = list(xs)
    s = ", ".join(str(x) for x in xs[:n])
    return s + (f" … (+{len(xs) - n})" if len(xs) > n else "")


def render(a):
    t, e, st, rh = a["technical"], a["editing"], a["structure"], a["rhythm"]
    au, tx, ov, col, sy, rt = a.get("audio") or {}, a["text"], a["overlays"], a["color"], a["sync"], a["retention"]
    L = []
    w = L.append
    title = a["source"]["title"]
    w(f"# Análisis de edición — {a.get('ref_id') or ''} {title}".strip())
    w("")
    w(f"Esquema `{a['schema_version']}` · skill v{a['meta']['skill_version']} · sha256 `{a['source']['sha256'][:12]}…` · "
      f"derechos: {a['source']['rights']}")
    w("")
    w("Niveles de evidencia: **observación** = medido directamente; **estimación** = deducido de medidas con un método "
      "conocido; **hipótesis** = lectura que hay que confirmar mirando los fotogramas.")
    w("")
    w("## 1. Datos técnicos " + tag(t["nivel"]))
    w(f"- Duración {t['duration_s']} s · {t['fps']} fps · {t['width']}×{t['height']} ({t['aspect_ratio']}, {t['orientation']})")
    w(f"- Vídeo {t['video_codec']} {t['pix_fmt']} · audio {t['audio_codec'] or 'sin audio'}"
      + (f" {t['audio_sample_rate']} Hz" if t['audio_sample_rate'] else ""))
    w("")
    w("## 2. Estructura narrativa " + tag("estimacion"))
    g = st["gancho"]
    w(f"- Gancho 0–{g['fin']} s: {g['cortes']} cortes, texto antes de 1 s: {'sí' if g['texto_antes_de_1s'] else 'no'}")
    w(f"- Desarrollo {st['desarrollo']['inicio']}–{st['desarrollo']['fin']} s" + (f" ({st['desarrollo']['nota']})" if st['desarrollo'].get('nota') else ""))
    w(f"- Clímax {st['climax']['inicio']}–{st['climax']['fin']} s ({st['climax']['motivo']})")
    d = st["desenlace"]
    w(f"- Desenlace {d['inicio']}–{d['fin']} s" + (f", silencio final {d['silencio_final_s']} s" if d.get("silencio_final_s") else ""))
    w(f"- Método: {st['metodo']}. La lectura del contenido (qué se cuenta) requiere ver el vídeo {tag('hipotesis')}.")
    w("")
    w("## 3. Cortes y duración de planos " + tag(e["nivel"]))
    w(f"- {len(e['cuts'])} cortes, {e['n_planos']} planos · mediana {e['plano_mediano_s']} s · media {e['plano_medio_s']} s · "
      f"mín {e['plano_min_s']} s · máx {e['plano_max_s']} s · {rh['cortes_por_10s']} cortes/10 s")
    w(f"- Cortes (s): {fmt_list(e['cuts'], 20)}")
    w("")
    w("| plano | inicio | dur. (s) | imagen | cámara " + tag("estimacion") + " | luma | sat. |")
    w("|---|---|---|---|---|---|---|")
    for s in a["shots"][:40]:
        w(f"| {s['n']} | {s['inicio']} | {s['duracion_s']} | {s['imagen']} | {s['camara']['movimiento']} | "
          f"{s['color']['luma_media']} | {s['color']['saturacion_media']} |")
    if len(a["shots"]) > 40:
        w(f"| … | | | | | | (+{len(a['shots']) - 40} planos) |")
    w("")
    w("## 4. Movimientos de cámara y cambios de perspectiva " + tag("estimacion"))
    w(f"- Resumen: {', '.join(f'{k} ×{v}' for k, v in a['camera']['resumen'].items())}")
    w(f"- Cambios de perspectiva entre planos consecutivos (encuadre o luz muy distintos): {e['cambios_de_perspectiva']}")
    w(f"- Nota: {a['camera']['nota']}. Nombres de movimiento = los de Remotion Pro (`template/src/pro/camera.tsx`).")
    w("")
    w("## 5. Zooms, paneos, recortes y movimientos simulados " + tag("estimacion"))
    zs = [s for s in a["shots"] if s["camara"]["movimiento"] in ("push-in", "pull-out")]
    ps = [s for s in a["shots"] if s["camara"]["movimiento"].startswith(("pan", "tilt"))]
    w(f"- Zoom en {len(zs)} planos" + (": " + fmt_list([f"{s['inicio']} s ×{s['camara']['zoom_total']}" for s in zs], 8) if zs else ""))
    w(f"- Paneo/inclinación en {len(ps)} planos" + (": " + fmt_list([f"{s['inicio']} s {s['camara']['movimiento']}" for s in ps], 8) if ps else ""))
    shaky = [s["inicio"] for s in a["shots"] if s["camara"].get("nota", "").startswith("movimiento irregular")]
    if shaky:
        w(f"- Movimiento irregular (cámara en mano o sacudida simulada) en planos que empiezan en {fmt_list(shaky)} s")
    w("")
    w("## 6. Transiciones y efectos visuales " + tag(a["transitions"]["nivel"]))
    w(f"- Tipos: {', '.join(f'{k} ×{v}' for k, v in a['transitions']['resumen'].items()) or 'ninguna'}")
    for it in [x for x in a["transitions"]["items"] if x["tipo"] != "corte"][:12]:
        w(f"  - {it['t']} s: {it['tipo']} ({it['duracion_s']} s) — {it['evidencia']}")
    if col["flashes"]:
        w(f"- Destellos de luz: {fmt_list(col['flashes'])} s {tag('observacion')}")
    w("")
    w("## 7. Subtítulos " + tag(tx["subtitulos"]["nivel"]))
    sb = tx["subtitulos"]
    w(f"- Texto en pantalla en el {round(tx['texto_en_pantalla_pct'] * 100)}% de los fotogramas muestreados")
    if sb.get("probable"):
        w(f"- Posición: franja al {sb['posicion_y_pct']}% de la altura · bloque de ~{sb['alto_bloque_px_aprox']} px")
        w(f"- Ritmo: {sb['cambios_por_s']} cambios/s, intervalo mediano {sb['intervalo_mediano_s']} s")
        w(f"- Color dominante: {sb['color_dominante']} · palabras resaltadas en color: {'sí' if sb['palabras_resaltadas_en_color'] else 'no detectado'}")
        w(f"- Aparición: {sb['aparicion']} {tag(sb['aparicion_nivel'])}")
        w(f"- Tipografía: {sb['tipografia']}")
    else:
        w(f"- Sin subtítulos claros: {sb.get('motivo')}")
    w("")
    w("## 8. Gráficos, overlays, máscaras y composiciones " + tag(ov["nivel"]))
    if ov["items"]:
        for it in ov["items"]:
            extra = f" — {it['lectura']} {tag(it['lectura_nivel'])}" if it.get("lectura") else ""
            w(f"- {it['tipo']}" + (f" en {it['zona']}" if it.get("zona") else "") + f" {tag(it['nivel'])}{extra}")
    else:
        w("- Ningún gráfico fijo, banda o pantalla dividida detectado")
    w(f"- Franjas con texto/gráficos: {fmt_list([f'{b['y_pct']}% ({b['presencia']})' for b in tx['franjas_ocupadas']], 10) or 'ninguna'}")
    w(f"- {ov['nota']}")
    w("")
    w("## 9. Color, contraste, iluminación y estética " + tag(col["nivel"]))
    gc = col["global"]
    w(f"- Luma media {gc['luma_media']}, contraste {gc['contraste_std']}, saturación {gc['saturacion_media']}, "
      f"calidez (R−B) {gc['calidez_r_menos_b']}, negros {gc['negros_pct']}, blancos {gc['blancos_pct']}")
    w(f"- Estética: {', '.join(col['estetica'])} {tag(col['estetica_nivel'])}")
    w(f"- Paleta dominante: {', '.join(f'{p['hex']} ({p['proporcion']})' for p in col['paleta'])}")
    w(f"- Afinidad con la paleta E2A (píxeles cercanos): " + ", ".join(f"{k} {v}" for k, v in col["afinidad_paleta_e2a"].items()))
    w("")
    w("## 10. Narración, música, efectos, silencios y mezcla")
    if not au:
        w("- El vídeo no tiene audio " + tag("observacion"))
    elif "error" in au:
        w(f"- No se pudo medir el audio: {au['error']}")
    else:
        lo = au["loudness"]
        w(f"- Sonoridad {lo['integrated_lufs']} LUFS, pico real {lo['true_peak_dbfs']} dBFS, LRA {lo['lra_lu']} LU {tag('observacion')}")
        w(f"- Silencios (< −35 dB, ≥ 0.25 s): {fmt_list([f'{a_}–{b_}' for a_, b_ in au['silences']['items']], 10) or 'ninguno'} {tag('observacion')}")
        w(f"- Voz: {'sí' if au['voz']['presente'] else 'no detectada'} ({round(au['voz']['proporcion'] * 100)}% del tiempo) {tag('estimacion')}")
        w(f"- Música de fondo: {'probable' if au['musica']['presente'] else 'no detectada'} {tag('estimacion')}")
        if au.get("tempo") and au["tempo"].get("fiable"):
            w(f"- Tempo: {au['tempo']['bpm']} BPM (confianza {au['tempo']['confianza']}) {tag('estimacion')}")
        elif au.get("tempo"):
            w(f"- Sin pulso rítmico claro (mejor candidato {au['tempo']['bpm']} BPM, confianza {au['tempo']['confianza']}) {tag('estimacion')}")
        w(f"- Golpes de audio: {au['hits']['per_10s']} por 10 s · efectos candidatos fuera de la voz: {fmt_list(au['efectos_candidatos']['times'], 10) or 'ninguno'} {tag(au['efectos_candidatos']['nivel'])}")
        if au["mezcla"]["voz_sobre_fondo_db"] is not None:
            w(f"- Mezcla: voz {au['mezcla']['voz_sobre_fondo_db']} dB sobre el fondo ({au['mezcla']['nota']}) {tag('estimacion')}")
        b = au["bandas"]
        w(f"- Reparto de energía: graves {b['graves_pct']}, banda de voz {b['voz_pct']}, agudos {b['agudos_pct']}")
        w("- Sin transcripción (no se gastan créditos de ElevenLabs en esta fase).")
    w("")
    w("## 11. Sincronización audio, imagen y texto " + tag(sy["nivel"]))
    if "cortes_en_golpe_de_audio" in sy:
        c = sy["cortes_en_golpe_de_audio"]
        w(f"- Cortes sobre un golpe de audio (±{c['tolerancia_s']} s): {c['n']}/{c['de']} (azar ≈ {c['esperado_por_azar']})")
    if "cortes_en_el_pulso" in sy:
        c = sy["cortes_en_el_pulso"]
        w(f"- Cortes en el pulso musical: {round(c['en_pulso_pct'] * 100)}% (desviación mediana {c['desviacion_mediana_s']} s)")
    if "texto_y_voz" in sy:
        c = sy["texto_y_voz"]
        w(f"- Inicios de frase con cambio de texto: {c['inicios_de_frase_con_cambio_de_texto']}/{c['frases']}")
    if "cortes_tras_silencio" in sy:
        w(f"- Cortes justo después de un silencio: {sy['cortes_tras_silencio']}")
    w(f"- {sy['lectura']}")
    w("")
    w("## 12. Técnicas de retención y cambios de ritmo " + tag(rt["nivel"]))
    w(f"- Primer corte {rt['primer_corte_s']} s · primer sonido {rt['primer_sonido_s']} s · texto en el primer segundo: "
      f"{'sí' if rt['texto_en_el_primer_segundo'] else 'no'}")
    w(f"- Mayor tramo sin cambio visual {rt['mayor_tramo_sin_cambio_visual_s']} s · interrupciones de patrón {rt['interrupciones_de_patron']}")
    w(f"- Ritmo: {rh['cortes_10s_primera_mitad']} cortes/10 s en la 1ª mitad, {rh['cortes_10s_segunda_mitad']} en la 2ª; "
      f"variación de planos (CV) {rh['variacion_planos_cv']}")
    if rh["cambios_de_ritmo"]:
        w(f"- Cambios bruscos de ritmo: {fmt_list([f'{c['t']} s ({c['de']}→{c['a']} cortes/5 s)' for c in rh['cambios_de_ritmo']], 8)}")
    for l_ in rt["lecturas"]:
        w(f"- {l_['texto']} {tag(l_['nivel'])}")
    w("")
    w("## Fotogramas representativos")
    w(f"- Hoja de contactos: `{a['frames']['sheet']}` ({len(a['frames']['items'])} fotogramas) — {a['frames']['nota']}")
    w(f"- Tiempos: {fmt_list([f['t'] for f in a['frames']['items']], 30)}")
    w("")
    w("## Revisión visual (la completa Claude o una persona mirando la hoja de contactos)")
    w("- Qué cuenta el vídeo y cómo se reparte la historia entre gancho, desarrollo, clímax y desenlace " + tag("hipotesis"))
    w("- Tipografía, animación de los subtítulos y gráficos que no se pueden medir " + tag("hipotesis"))
    w("- Técnicas reutilizables para E2A → fichas `tec-NNNN` con `library.py propose` + revisión")
    w("")
    return "\n".join(L)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        print(render(json.load(f)))
