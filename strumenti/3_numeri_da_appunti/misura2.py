"""41 (Gilberto "forse ti mancano dei numeri"): metriche in piu' oltre all'attenzione, solo codice.
Dal PNG: VUOTO (griglia relativa alla pagina), CONTORNI DRITTI, SPESSORE del tratto, EVIDENZIATI (pixel), RIQUADRI, DISPERSIONE.
Dal sorgente (misure3.json di combinazioni.py: PDF suo vettoriale / HTML / SVG): testo, corpo, fondo, evidenziato, combinazioni.
NIENTE OCR (09/10: easyocr ha saturato memoria e disco; ocr_cache.py non va rilanciato).
Uso: C:\\Python310\\python.exe -X utf8 ESPERIMENTI\\41_ATTENZIONE_NUMERI\\misura2.py [--robustezza]"""
import html as H, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
D = Path(__file__).resolve().parent; E = D.parent
N = E / "4_NOTTE_genera_pagine_e_regole_dimenticate"
PDF_SUO = D / "esempi_numeri" / "suoi" / "Architettura_Gilberto.pdf"  # pagina k = 4_NOTTE/p0k


def gruppi():
    g = {"SUOI": sorted(N.glob("p0*/gilberto.png"))}
    for c in ["SENZA", "CON_REGOLE", "CON_REGOLE_FIGURA"]:
        g[f"40 Claude {c}"] = sorted((E / "40_CLAUDE_ARCH_PACCHETTO" / "prove" / c).glob("r*/pagina.png"))
    g["41 Claude SVG+numeri"] = sorted((D / "prove" / "SVG_CON_NUMERI").glob("r*/pagina.png"))
    for c in ["Z1_SENZA_NOT", "Z1_CON_NOT", "Z2_SENZA", "Z2_CON_REGOLE_GPT", "Z2_CON_PULITO"]:
        g[f"39 GPT {c}"] = sorted((E / "39_ZONE_GRIGIE_CODEX" / "ARCH_p03" / c).glob("r*/pagina.png"))
    return {k: v for k, v in g.items() if v}


def prof_di(p):  # pagina del prof corrispondente
    return p.parent / "prof.png" if p.name == "gilberto.png" else N / "p03" / "prof.png"


def tutte_le_pagine():
    pag = [p for v in gruppi().values() for p in v]
    return pag + sorted({prof_di(p) for p in pag})


def carica(f, w):
    im = Image.open(f).convert("RGB")
    return np.asarray(im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)).astype(float)


def immagine(f, w=600):
    a = carica(f, w); h = a.shape[0]
    q = (a // 8).astype(int); key = q[..., 0] * 1024 + q[..., 1] * 32 + q[..., 2]
    fondo = a[key == np.bincount(key.ravel()).argmax()].mean(0)
    diff = np.abs(a - fondo).max(2)
    # VUOTO: griglia 40 colonne (relativa alla pagina); cella vuota se nessun pixel si stacca dal fondo di oltre 20
    c = w // 40; R = h // c
    celle = diff[:R * c, :40 * c].reshape(R, c, 40, c).max((1, 3)) < 20
    vuoto = celle.mean(); basso = celle[2 * R // 3:].mean()
    # SPESSORE: inchiostro = diff > 60, tolti i riempimenti (apertura 1% w); spessore = area / lunghezza scheletro, in millesimi di w
    from skimage.morphology import skeletonize
    ink = diff > 60; k = max(3, round(0.01 * w))
    sottile = ink & ~ndimage.binary_opening(ink, np.ones((k, k)))
    spess = 1000 * sottile.sum() / max(skeletonize(sottile).sum(), 1) / w
    mx, mn = a.max(2), a.min(2); ch = (mx - mn) / np.maximum(mx, 1); lum = a @ [0.299, 0.587, 0.114]
    area = w * h
    # EVIDENZIATO: macchie di colore (croma >= 0.12, chiare abbastanza da reggere testo scuro) alte come una riga di testo
    # (1-4,5% di w), larghe < 45% di w, con dentro pixel scuri (testo)
    tinta = (ch >= 0.12) & (lum > 110) & (diff > 20)
    lab, n = ndimage.label(ndimage.binary_fill_holes(ndimage.binary_closing(tinta, np.ones((3, 3)))))
    scuri = lum < 130; ev_n = 0; ev_a = 0
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = s[0].stop - s[0].start, s[1].stop - s[1].start
        if 0.01 * w <= hh <= 0.045 * w and 0.02 * w <= ww <= 0.45 * w and scuri[s][lab[s] == i].mean() > 0.03:
            ev_n += 1; ev_a += (lab[s] == i).sum()
    # CONTORNATI: riquadri chiusi da un contorno scuro (lum < 160); dentro >= 0.2% pagina, quasi rettangolari (riempie >= 80% del bbox)
    cont = lum < 160
    dentro = ndimage.binary_fill_holes(cont) & ~cont
    lab, n = ndimage.label(dentro); rq_n = 0; rq_a = 0
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        a_i = (lab[s] == i).sum(); bb = (s[0].stop - s[0].start) * (s[1].stop - s[1].start)
        if a_i >= 0.002 * area and a_i >= 0.8 * bb: rq_n += 1; rq_a += a_i
    # DISPERSIONE: contenuto = diff > 20, dilatato di 2% w -> blocchi (>= 0.3% pagina); quota del blocco piu' grande
    cont_m = ndimage.binary_dilation(diff > 20, np.ones((round(0.02 * w), round(0.02 * w))))
    lab, n = ndimage.label(cont_m); ar = np.bincount(lab.ravel())[1:]
    ar = ar[ar >= 0.003 * area] if n else np.array([0])
    grande = ar.max() / max(ar.sum(), 1)
    # CONTORNI DRITTI: bordi dell'inchiostro; quota che sta in tratti orizz./vert. perfettamente dritti lunghi >= 4% di w
    bordo = ink & ~ndimage.binary_erosion(ink)
    L = max(3, round(0.04 * w))
    hor = ndimage.binary_opening(bordo, np.ones((1, L))); ver = ndimage.binary_opening(bordo, np.ones((L, 1)))
    dritti = (hor | ver).sum() / max(bordo.sum(), 1)
    return {"vuoto_%": round(100 * vuoto, 1), "vuoto_terzo_basso_%": round(100 * basso, 1),
            "spessore_tratto_‰": round(spess, 2), "contorni_dritti_%": round(100 * dritti, 1),
            "evidenziati_n": ev_n, "evidenziati_area_%": round(100 * ev_a / area, 1),
            "riquadri_n": rq_n, "dentro_riquadri_%": round(100 * rq_a / area, 1),
            "blocchi_n": int(len(ar)), "blocco_piu_grande_%": round(100 * grande, 1)}


def metriche(p, m3):  # immagine + metriche dal sorgente (misure3.json, scritto da combinazioni.py: PDF suo / HTML / SVG)
    return {**immagine(p), **m3.get(str(p.relative_to(E)), {})}


def robustezza():
    g = gruppi()
    for w in (400, 600, 900):
        print(w)
        for k, v in g.items():
            r = [immagine(p, w) for p in v]
            print(f"  {k:28}", {c: [x[c] for x in r] for c in r[0]})


if __name__ == "__main__":
    if "--robustezza" in sys.argv: robustezza(); sys.exit()
    m3 =json.loads((D / "misure3.json").read_text(encoding="utf-8"))
    tutto = {k: [{"file": str(p.relative_to(E)), **metriche(p, m3)} for p in v] for k, v in gruppi().items()}
    (D / "misure2.json").write_text(json.dumps(tutto, ensure_ascii=False, indent=1), encoding="utf-8")
    chiavi = list(dict.fromkeys(k for x in tutto["SUOI"] for k in x if k != "file"))
    righe = ["| gruppo | n | " + " | ".join(chiavi) + " |", "|---|---|" + "---|" * len(chiavi)]
    for g, m in tutto.items():
        if g == "PROF": continue
        cel = []
        for c in chiavi:
            v = [x[c] for x in m if c in x]
            cel.append(f"{min(v):g}-{max(v):g} (med {np.median(v):g})" if v else "-")
        righe.append(f"| {g} | {len(m)} | " + " | ".join(cel) + " |")
    (D / "tabella2.md").write_text("\n".join(righe) + "\n", encoding="utf-8"); print("\n".join(righe))
    suoi = tutto["SUOI"]; gen = [x for g, m in tutto.items() if g not in ("SUOI", "PROF") for x in m]
    print("\nseparazione:")
    for c in chiavi:
        s = [x[c] for x in suoi if c in x]; t = [x[c] for x in gen if c in x]
        if not s or not t: continue
        fuori = np.mean([(v < min(s)) or (v > max(s)) for v in t])
        print(f"  {c:26} fuori={fuori:.2f}  suoi {min(s):g}-{max(s):g} med {np.median(s):g} | gen med {np.median(t):g} ({min(t):g}-{max(t):g})")
