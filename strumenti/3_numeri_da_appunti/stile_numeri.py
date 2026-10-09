"""STILE di Gilberto in NUMERI (05/10 notte): dai suoi PDF vettoriali (p02-p07) estrae font/grandezze per ruolo, palette, banner,
spessori e tratteggi -> ESPERIMENTI/5_STILE_in_numeri/stile_gilberto.json + .md. Valori validi per tutte le pagine (mediana + intervallo).
Uso: C:\\Python310\\python.exe -X utf8 stile_numeri.py"""
import json, statistics as st
from collections import Counter, defaultdict
from pathlib import Path
import fitz
import allinea as A

OUT = Path(__file__).parent / "ESPERIMENTI" / "5_STILE_in_numeri"; OUT.mkdir(parents=True, exist_ok=True)
PAGINE = ["p02", "p03", "p04", "p05", "p06", "p07"]
hexc = lambda c: "#%02X%02X%02X" % tuple(round(x * 255) for x in c[:3]) if c else None
hexi = lambda i: "#%06X" % i
font_sz, font_col, font_nome, fill_area, strokes, dashes, banner = defaultdict(list), Counter(), Counter(), Counter(), [], Counter(), []
W = H = None
for p in PAGINE:
    fm, nm = A.pdf_mio("architettura", f"schema_esercizi_{p}"); pg = fitz.open(fm)[nm]; W, H = pg.rect.width, pg.rect.height
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if not t:
                    continue
                sz = round(s["size"]); font_sz[s["font"]].append(sz); font_col[(hexi(s["color"]), sz >= 20)] += len(t); font_nome[s["font"]] += len(t)
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("fill"):
            fill_area[hexc(d["fill"])] += r.width * r.height
            if r.width > 0.5 * W and r.height < 0.15 * H and r.y0 < 0.25 * H:
                banner.append({"pagina": p, "colore": hexc(d["fill"]), "altezza_%": round(100 * r.height / H, 1), "y_%": round(100 * r.y0 / H, 1)})
        if d.get("color") and d.get("width"):
            strokes.append(round(d["width"], 1)); dashes["tratteggio" if d.get("dashes") and d["dashes"] not in ("[] 0", "") else "pieno"] += 1

ruoli = []
for f, v in font_sz.items():
    ruoli.append({"font": f, "grandezza_mediana": st.median(v), "min": min(v), "max": max(v), "caratteri": font_nome[f]})
ruoli.sort(key=lambda x: -x["grandezza_mediana"])
fondo = max(fill_area, key=fill_area.get) if fill_area else None
stile = {"pagina_pt": [round(W), round(H)], "colore_fondo": fondo,
         "palette_per_area": [{"colore": c, "area_%": round(100 * a / (W * H * len(PAGINE)), 1)} for c, a in fill_area.most_common(10)],
         "font_per_ruolo": ruoli[:8],
         "colori_testo": [{"colore": c, "titolo": tit, "caratteri": n} for (c, tit), n in font_col.most_common(8)],
         "banner_in_alto": banner,
         "spessore_linee": {"mediana": st.median(strokes) if strokes else None, "tipici": Counter(strokes).most_common(4)},
         "linee": dict(dashes)}
(OUT / "stile_gilberto.json").write_text(json.dumps(stile, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(stile, ensure_ascii=False, indent=1)[:3500])
