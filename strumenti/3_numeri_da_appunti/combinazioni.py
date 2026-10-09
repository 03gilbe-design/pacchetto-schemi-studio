"""41: COMBINAZIONI di attributi (Gilberto 08:11) e VARIANZA (quante combinazioni di stile per pagina), da elementi.json.
Testi pesati per numero di caratteri, forme per numero. Suo % = sulle sue 6 pagine insieme; generate % = tutte le generate insieme.
Uso: C:\\Python310\\python.exe -X utf8 ESPERIMENTI\\41_ATTENZIONE_NUMERI\\combinazioni.py"""
import colorsys, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path
D = Path(__file__).resolve().parent; E = D.parent; sys.path.insert(0, str(D))
from misura2 import gruppi


def tinta(c):
    if c is None: return "nessuno"
    r, g, b = (x / 255 for x in c); h, s, v = colorsys.rgb_to_hsv(r, g, b); h *= 360
    if s < 0.15: return "bianco/crema" if v > 0.88 else "nero" if v < 0.28 else "grigio"
    if v < 0.65 and (h < 45 or h >= 340): return "marrone"
    if h < 25 or h >= 340: return "corallo/rosso" if s >= 0.5 and v >= 0.8 else "pesca/rosa"
    if h < 45: return "arancio" if s >= 0.6 else "pesca/rosa"
    return "giallo" if h < 70 else "verde" if h < 165 else "turchese" if h < 200 else "azzurro/blu" if h < 255 else "viola"


MANO = re.compile(r"AFont1|cursive|Caveat|Comic|Segoe Print|Segoe Script|Kalam|Patrick|Gochi|Indie|Architects|Shadows|Chalk|Marker|Handlee|Bradley|Ink Free", re.I)


def font(f):
    if MANO.search(f): return "a mano"
    if re.search(r"mono|Courier|Consolas", f, re.I): return "mono"
    first = f.split(",")[0]
    if re.search(r"Georgia|Times|Cambria|Garamond|^\s*serif", first, re.I): return "serif"
    return "sans"


def dim(rel):  # corpo / larghezza pagina: 0,018 = 14 px su 794 = 10,7 pt su A4
    return "piccolo" if rel < 0.018 else "medio" if rel < 0.026 else "grande"


area = lambda b: max(0, b[2] - b[0]) * max(0, b[3] - b[1])
dentro = lambda b, x, y: b[0] <= x <= b[2] and b[1] <= y <= b[3]


def ruolo(f):
    b = f["box"]; w, h = b[2] - b[0], b[3] - b[1]
    if not f["chiusa"] or min(w, h) < 0.006: return "linea"
    if f["fill"] and w >= 0.6 and h <= 0.2: return "fascia"
    return "riquadro"


def attributi(pag):
    grandi = [f for f in pag["forme"] if area(f["box"]) >= 0.8 and f["fill"]]
    bg = max(grandi, key=lambda f: area(f["box"]))["fill"] if grandi else [255, 255, 255]
    forme = []
    for f in pag["forme"]:  # il fondo pagina non e' una forma; un riempimento uguale al fondo pagina conta come "senza fondo"
        if area(f["box"]) >= 0.8: continue
        if f["fill"] and max(abs(a - b) for a, b in zip(f["fill"], bg)) <= 8: f = {**f, "fill": None}
        forme.append(f)
    piene = [f for f in forme if f["fill"] and f["chiusa"]]; bordate = [f for f in forme if f["stroke"] and f["chiusa"] and ruolo(f) != "linea"]
    T = []
    for t in pag["testi"]:
        b = t["box"]; x, y = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; ht = max(b[3] - b[1], 1e-4)
        sotto = min((f for f in piene if dentro(f["box"], x, y)), key=lambda f: area(f["box"]), default=None)
        bordo = min((f for f in bordate if dentro(f["box"], x, y)), key=lambda f: area(f["box"]), default=None)
        ev = bool(sotto and (sotto["box"][3] - sotto["box"][1]) <= 3 * ht and area(sotto["box"]) < 0.03)
        T.append({"n": len(t["t"]), "colore": tinta(t["colore"]), "font": font(t["font"]), "dim": dim(t["rel"]),
                  "peso": "grassetto" if t["peso"] >= 600 else "normale", "fondo": tinta(sotto["fill"]) if sotto else "pagina",
                  "evidenziato": "evidenziato" if ev else "no", "bordo": tinta(bordo["stroke"]) if bordo else "nessun riquadro"})
    F = [{"n": 1, "ruolo": ruolo(f), "fill": tinta(f["fill"]), "stroke": tinta(f["stroke"]), "tratt": "tratteggio" if f["tratt"] else "pieno"} for f in forme]
    return T, F


COPPIE = [("T", "colore", "fondo"), ("T", "font", "dim"), ("T", "font", "colore"), ("T", "peso", "colore"), ("T", "evidenziato", "font"),
          ("T", "bordo", "colore"), ("T", "dim", "colore"), ("T", "fondo", "font"),
          ("F", "ruolo", "fill"), ("F", "ruolo", "stroke"), ("F", "fill", "stroke"), ("F", "tratt", "ruolo")]
STILE = ("colore", "font", "dim", "peso")  # una "combinazione di stile" del testo (con anche "fondo": suoi 5-12, gen 8-14, non separa)


def distribuzione(elem, a, b):
    c = Counter()
    for e in elem: c[(e[a], e[b])] += e["n"]
    tot = sum(c.values()) or 1
    return {k: 100 * v / tot for k, v in c.items()}


def varianza(T):  # combinazioni di stile distinte (>= 1% dei caratteri) ed entropia in bit
    c = Counter()
    for e in T: c[tuple(e[k] for k in STILE)] += e["n"]
    tot = sum(c.values()) or 1; p = [v / tot for v in c.values()]
    return sum(1 for x in p if x >= 0.01), round(-sum(x * math.log2(x) for x in p if x > 0), 2)


PAROLA = re.compile(r"[A-Za-zÀ-ÿ]{2,}")
PROF_PAROLE = {"p02": 301, "p03": 385, "p04": 608, "p06": 222}  # testo esatto del PDF del prof (architettura_2semestre.pdf p.16, 18, 19, 13; p05/p07 non trovate)


def per_pagina(k, pag):
    T, F = attributi(pag); ch = sum(e["n"] for e in T) or 1
    n, ent = varianza(T)
    par = [(len(PAROLA.findall(t["t"])), t["box"][2] - t["box"][0]) for t in pag["testi"]]
    tot = sum(p for p, _ in par) or 1
    m = {"corpo_medio_o_grande_%": round(100 * sum(e["n"] for e in T if e["dim"] != "piccolo") / ch, 1),
         "testo_su_fondo_pagina_%": round(100 * sum(e["n"] for e in T if e["fondo"] == "pagina") / ch, 1),
         "testo_evidenziato_%": round(100 * sum(e["n"] for e in T if e["evidenziato"] == "evidenziato") / ch, 1),
         "combinazioni_stile_n": n, "entropia_stile_bit": ent,
         "combinazioni_forme_n": sum(1 for v in Counter((f["ruolo"], f["fill"], f["stroke"], f["tratt"]) for f in F).values() if v >= 0.02 * len(F)),
         "forme_linee_%": round(100 * sum(f["ruolo"] == "linea" for f in F) / max(len(F), 1), 1),
         "parole": tot, "parole_in_righe_lunghe_%": round(100 * sum(p for p, w in par if p >= 5 and w >= 0.3) / tot, 1)}
    mp = re.search(r"p0\d", k) if "gilberto" in k else None
    pr = mp.group(0) if mp else "p03"
    if pr in PROF_PAROLE: m["parole_su_prof_%"] = round(100 * tot / PROF_PAROLE[pr])
    return m


if __name__ == "__main__":
    EL = json.loads((D / "elementi.json").read_text(encoding="utf-8")); g = gruppi()
    att = {k: attributi(v) for k, v in EL.items()}
    pp = {k: per_pagina(k, v) for k, v in EL.items()}
    (D / "misure3.json").write_text(json.dumps(pp, ensure_ascii=False, indent=1), encoding="utf-8")
    suoi = [str(p.relative_to(E)) for p in g["SUOI"]]; gen = [k for k in att if k not in suoi]
    pool = lambda ks, tipo: [e for k in ks for e in att[k][0 if tipo == "T" else 1]]
    righe = []
    for tipo, a, b in COPPIE:
        ds, dg = distribuzione(pool(suoi, tipo), a, b), distribuzione(pool(gen, tipo), a, b)
        for k in set(ds) | set(dg):
            righe.append((f"{a} × {b}", f"{k[0]} + {k[1]}", round(ds.get(k, 0), 1), round(dg.get(k, 0), 1)))
    righe.sort(key=lambda r: -abs(r[2] - r[3]))
    var = {k: varianza(att[k][0]) for k in att}
    (D / "combinazioni.json").write_text(json.dumps({"coppie": righe, "varianza": var}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("coppia | combinazione | suo % | generate %")
    for r in righe[:40]: print(" | ".join(map(str, r)))
    import numpy as np
    print("\nper pagina, separazione suoi vs generate:")
    for c in pp[suoi[0]]:
        s = [pp[k][c] for k in suoi if c in pp[k]]; t = [pp[k][c] for k in gen if c in pp[k]]
        fuori = np.mean([(v < min(s)) or (v > max(s)) for v in t])
        print(f"  {c:26} fuori={fuori:.2f} suoi {min(s):g}-{max(s):g} (med {np.median(s):g}) | gen med {np.median(t):g} ({min(t):g}-{max(t):g})")
        for gr, v in g.items():
            if gr == "SUOI": continue
            vv = [pp[str(p.relative_to(E))][c] for p in v if c in pp[str(p.relative_to(E))]]
            print(f"      {gr:28} {vv}")
