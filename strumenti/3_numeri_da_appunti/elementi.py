"""41 (Gilberto 08:11 "hai un sacco di combinazioni"): elementi della pagina con i loro attributi, ESATTI dal sorgente.
- SUE pagine: dal suo PDF vettoriale Architettura_Gilberto.pdf (pagina k = 4_NOTTE/p0k): testo (font, corpo, colore, grassetto) e
  forme (fill/stroke) con PyMuPDF. Le immagini raster dentro il PDF (chip, alcune etichette) sono ignorate.
- GENERATE: HTML e SVG resi in Chromium (Playwright), stili calcolati (getComputedStyle) di ogni testo e di ogni forma.
Uscita: elementi.json {pagina: {"testi": [...], "forme": [...]}}; coordinate normalizzate 0-1 sulla larghezza/altezza pagina.
Uso: C:\\Python310\\python.exe -X utf8 ESPERIMENTI\\41_ATTENZIONE_NUMERI\\elementi.py"""
import json, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent; E = D.parent; sys.path.insert(0, str(D))
from misura2 import gruppi, PDF_SUO

JS = r"""() => {
  const W = document.documentElement.scrollWidth > 794 ? 794 : 794, H = 1123, out = {testi: [], forme: []};
  const rgb = c => { const m = (c || '').match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number);
                     return (v.length > 3 && v[3] === 0) ? null : v.slice(0, 3); };
  const n = r => [r.left / W, r.top / H, r.right / W, r.bottom / H];
  for (const e of document.querySelectorAll('body *')) {
    if (['SCRIPT', 'STYLE', 'DEFS', 'defs', 'marker', 'title'].includes(e.tagName) || e.closest('defs,marker')) continue;
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const svg = e instanceof SVGElement;
    const testo = [...e.childNodes].filter(x => x.nodeType === 3).map(x => x.textContent).join('').trim();
    if (testo.length > 0 && s.visibility !== 'hidden' && s.display !== 'none') {
      const rg = document.createRange(); rg.selectNodeContents(e); const b = rg.getBoundingClientRect();
      out.testi.push({t: testo, box: n(b), colore: svg ? rgb(s.fill) : rgb(s.color), font: s.fontFamily,
                      px: parseFloat(s.fontSize), peso: parseInt(s.fontWeight) || (s.fontWeight === 'bold' ? 700 : 400)});
    }
    if (svg) {
      if (!['rect', 'circle', 'ellipse', 'polygon', 'path', 'line', 'polyline'].includes(e.tagName)) continue;
      const aperta = ['line', 'polyline'].includes(e.tagName) || (e.tagName === 'path' && !/[zZ]\s*$/.test(e.getAttribute('d') || ''));
      out.forme.push({box: n(r), fill: aperta ? null : rgb(s.fill), stroke: (s.stroke !== 'none' && parseFloat(s.strokeWidth) > 0) ? rgb(s.stroke) : null,
                      tratt: s.strokeDasharray !== 'none', chiusa: !aperta, tag: e.tagName});
    } else {
      const bg = rgb(s.backgroundColor), bw = parseFloat(s.borderTopWidth) + parseFloat(s.borderLeftWidth), bs = s.borderTopStyle !== 'none' || s.borderLeftStyle !== 'none';
      const bc = bw > 0 && bs ? rgb(s.borderTopWidth !== '0px' ? s.borderTopColor : s.borderLeftColor) : null;
      const tutto = parseFloat(s.borderTopWidth) > 0 && parseFloat(s.borderBottomWidth) > 0 && parseFloat(s.borderLeftWidth) > 0 && parseFloat(s.borderRightWidth) > 0;
      if (bg || bc) out.forme.push({box: n(r), fill: bg, stroke: bc, tratt: /dash|dot/.test(s.borderTopStyle), chiusa: tutto || !!bg, tag: e.tagName.toLowerCase()});
    }
  }
  return out;
}"""


def sorgente(f):  # pagina.html o pagina.svg -> HTML da rendere
    t = Path(f).read_text(encoding="utf-8", errors="ignore")
    return t if Path(f).suffix.lower() != ".svg" else "<!doctype html><html><body style='margin:0;width:794px;height:1123px;overflow:hidden'>" + t + "</body></html>"


def da_html(pagine):  # pagine = lista di (chiave, file sorgente)
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 794, "height": 1123})
        for k, f in pagine:
            pg.set_content(sorgente(f)); pg.wait_for_timeout(300)
            r = pg.evaluate(JS)
            for t in r["testi"]: t["rel"] = t.pop("px") / 794  # corpo in frazione della larghezza pagina
            out[k] = r
        b.close()
    return out


def sorgente_di(png):
    return next((png.parent / n for n in ("pagina.html", "pagina.svg") if (png.parent / n).exists()), None)


def da_pdf(pagine):
    import fitz
    doc = fitz.open(PDF_SUO)
    return {str(png.relative_to(E)): pagina_pdf(doc[int(png.parent.name[1:]) - 1]) for png in pagine}


def pagina_pdf(pg):  # una pagina PyMuPDF -> {"testi", "forme"}
    W, H = pg.rect.width, pg.rect.height
    n = lambda r: [r[0] / W, r[1] / H, r[2] / W, r[3] / H]
    c255 = lambda c: [round(255 * x) for x in c[:3]] if c else None
    testi = []
    for bl in pg.get_text("dict")["blocks"]:
        for l in bl.get("lines", []):
            for s in l["spans"]:
                if not s["text"].strip(): continue
                col = s["color"]; testi.append({"t": s["text"].strip(), "box": n(s["bbox"]), "colore": [col >> 16 & 255, col >> 8 & 255, col & 255],
                                                "font": s["font"], "rel": s["size"] / W, "peso": 700 if ("Bold" in s["font"] or s["flags"] & 16) else 400})
    forme = []
    for d in pg.get_drawings():
        tipi = {it[0] for it in d["items"]}
        # i suoi contorni a mano sono tracciati di curve non chiusi formalmente: chiusa se il tracciato torna al punto di partenza
        p0 = d["items"][0][1]; p1 = d["items"][-1][-1]; r = d["rect"]
        torna = len(d["items"]) > 2 and hasattr(p0, "x") and hasattr(p1, "x") and abs(p0.x - p1.x) + abs(p0.y - p1.y) < 0.05 * max(r.width + r.height, 1)
        aperta = tipi <= {"l", "c"} and not d.get("closePath", False) and not torna
        forme.append({"box": n(d["rect"]), "fill": None if aperta else c255(d.get("fill")) if d["type"] in ("f", "fs") else None,
                      "stroke": c255(d.get("color")) if d["type"] in ("s", "fs") else None, "tratt": bool(d.get("dashes") and d["dashes"] not in ("[] 0", "")),
                      "chiusa": not aperta, "tag": d["type"]})
    return {"testi": testi, "forme": forme}


if __name__ == "__main__":
    g = gruppi()
    tutto = da_pdf(g["SUOI"])
    tutto.update(da_html([(str(p.relative_to(E)), sorgente_di(p)) for k, v in g.items() if k != "SUOI" for p in v if sorgente_di(p)]))
    (D / "elementi.json").write_text(json.dumps(tutto, ensure_ascii=False), encoding="utf-8")
    for k, v in tutto.items(): print(f"{k:70} testi {len(v['testi']):4} forme {len(v['forme']):4}")
