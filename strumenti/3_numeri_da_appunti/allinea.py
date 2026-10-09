"""ALLINEATORE prof -> mio, fatto bene (PROGETTO_ALLINEATORE.md, Gilberto 04/10: 'codice fatto bene con AI e componente codice d'aiuto').
Il CODICE trova gli oggetti della pagina e li numera; l'AI (Gemini Pro) SCEGLIE solo numeri; il codice costruisce e controlla.
Niente coordinate dall'AI -> mai testo tagliato, figure sempre intere.
Uso: python allinea.py schema_esercizi_p02 [...]  [--solo-oggetti]   ->  allinea/<chiave>/ (P_num.png, S_num.png, risposta, pezzi.json, controllo.jpg)"""
import json, re, subprocess, sys
from pathlib import Path
import cv2, fitz, numpy as np
from PIL import Image, ImageDraw, ImageFont
from allinea_auto import AGY, ANN, pdf_mio, pdf_prof

QUI = Path(__file__).parent; OUT = QUI / "allinea"; OUT.mkdir(exist_ok=True)
Z = 2  # zoom delle immagini di pagina


# ---------- 1. OGGETTI (codice, deterministico, niente OCR) ----------
def unisci_vicini(rett, gap):
    """unisce i rettangoli che si toccano o distano meno di gap (fino a che non cambia piu' niente)."""
    rr = [fitz.Rect(r) for r in rett]
    cambiato = True
    while cambiato:
        cambiato = False
        for i in range(len(rr)):
            for j in range(i + 1, len(rr)):
                a, b = rr[i], rr[j]
                if fitz.Rect(a.x0 - gap, a.y0 - gap, a.x1 + gap, a.y1 + gap).intersects(b):
                    rr[i] = a | b; rr.pop(j); cambiato = True; break
            if cambiato:
                break
    return rr


def forme_in_foto(pg, r):
    """dentro una FOTO scansionata: blocchi di scritta e riquadri trovati con OpenCV (soglia + dilatazione + contorni)."""
    pix = pg.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=r)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    b = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 15)
    b = cv2.dilate(b, cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5)))
    cont, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    A = pix.width * pix.height; out = []
    for c in cont:
        x, y, w, h = cv2.boundingRect(c)
        if .004 * A < w * h < .9 * A:
            out.append(fitz.Rect(r.x0 + x / Z, r.y0 + y / Z, r.x0 + (x + w) / Z, r.y0 + (y + h) / Z))
    return unisci_vicini(out, 3)


def paragrafi(pg):
    """paragrafi veri: il pdf a volte mette due paragrafi in un blocco (p02 S10). Nuovo paragrafo se tra due righe c'e' uno spazio
    piu' grande di mezza riga o se la riga parte molto piu' a sinistra/destra (colonna diversa)."""
    out = []
    for b in pg.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        cur = None
        for l in b["lines"]:
            r = fitz.Rect(l["bbox"]); t = "".join(sp["text"] for sp in l["spans"]).strip()
            if not t:
                continue
            nuova_frase = cur and re.search(r"[.:]$", cur["testo"]) and re.match(r"[A-ZÀ-Ý]", t)  # p02 prof: 'volta.' -> 'Ecco come...'
            if cur and (r.y0 - cur["ultima"].y1 > .5 * r.height or abs(r.x0 - cur["r"].x0) > 40 and r.y0 >= cur["ultima"].y1 - 2
                        or nuova_frase):  # niente regola sulla larghezza: spezzava i paragrafi che girano attorno a una figura
                out.append(cur); cur = None
            if cur is None:
                cur = {"tipo": "testo", "r": fitz.Rect(r), "testo": t, "ultima": r, "righe": [fitz.Rect(r)]}
            else:
                cur["r"] |= r; cur["testo"] += " " + t; cur["ultima"] = r; cur["righe"].append(fitz.Rect(r))
        if cur:
            out.append(cur)
    for e in out:
        e.pop("ultima")
    return out


def oggetti(pg, filtri=True):
    """elementi della pagina: paragrafi (blocchi di testo), disegni vettoriali raggruppati, immagini (o le loro forme se foto)."""
    el = paragrafi(pg)
    P = pg.rect.get_area()
    # 05/10: la FILIGRANA (lettere diagonali grigio chiaro, solo riempimento) non e' contenuto: unita diventava un rettangolone (p03)
    filigrana = lambda d: filtri and d.get("fill") and not d.get("color") and min(d["fill"]) > .78 and max(d["fill"]) - min(d["fill"]) < .03
    dis = [d["rect"] for d in pg.get_drawings() if d["rect"].get_area() < .3 * P and (d["rect"].width > 3 or d["rect"].height > 3) and not filigrana(d)]
    # 05/10 (Gilberto: 'rettangolone che prende un po' di tutto'): evidenziature/sottolineature SULLE righe di testo non si
    # uniscono agli altri disegni (unite a catena diventavano un 'disegno' gigante su paragrafi e figure): restano singole
    righe_t = [q for e in el if e["tipo"] == "testo" for q in (e.get("righe") or [e["r"]])]
    decor = lambda r: filtri and (r.height < 5 or any((r & q).get_area() >= .5 * r.get_area() for q in righe_t))
    disegni = [r for r in unisci_vicini([r for r in dis if not decor(r)], 8) if r.get_area() > .0005 * P]         + [r for r in unisci_vicini([r for r in dis if decor(r) and r.height >= 5], 2) if r.get_area() > .0005 * P]
    for r in disegni:
        dentro = [e for e in el if e["tipo"] == "testo" and (e["r"] & r).get_area() >= .8 * e["r"].get_area()]
        if dentro and sum(e["r"].get_area() for e in dentro) > .7 * r.get_area():
            continue  # il "disegno" e' solo la cornice/sfondo di un testo: resta il testo
        el = [e for e in el if e not in dentro]  # le scritte DENTRO un disegno fanno parte del disegno
        t = " ".join(e["testo"] for e in dentro)
        if not t and r.get_area() < .02 * P:  # evidenziatura/cornice piccola su una parola (p02: 'DIRETTO' giallo): prende il testo che copre
            t = " ".join(pg.get_text("text", clip=r).split())
        el.append({"tipo": "disegno", "r": r, "testo": t[:200]})
    for x in pg.get_images():
        for r in pg.get_image_rects(x[0]):
            if r.get_area() < .002 * P:
                continue
            forme = forme_in_foto(pg, r) if r.get_area() > .05 * P else []
            if len(forme) >= 2:  # foto con dentro schema/scritte: i suoi pezzi + la foto intera (cosi' niente si perde)
                el += [{"tipo": "foto", "r": f, "testo": ""} for f in forme if f.get_area() < .85 * r.get_area()]
                el.append({"tipo": "immagine", "r": r, "testo": "", "intera": True})
            else:
                el.append({"tipo": "immagine", "r": r, "testo": ""})
    # un disegno che contiene quasi solo un blocco di testo e' una cornice: resta un oggetto solo (il disegno)
    el.sort(key=lambda e: (round(e["r"].y0 / 8), e["r"].x0))
    return el


# 05/10: filtri filigrana/evidenziature sulla pagina SUA solo qui (p04/p06 ricollegati con la numerazione nuova);
# altrove la numerazione sua resta quella su cui sono stati fatti i legami
FILTRI_MIO = {"schema_esercizi_p04", "schema_esercizi_p06"}


# ---------- 2. PAGINE NUMERATE ----------
COL = {"testo": (60, 110, 200), "disegno": (200, 90, 40), "immagine": (60, 150, 80), "foto": (140, 70, 170)}


def numerata(pg, el, pref, out, da=1):
    pix = pg.get_pixmap(matrix=fitz.Matrix(Z, Z)); im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
    st = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(st); f = ImageFont.truetype("arialbd.ttf", 22)
    for i, e in enumerate(el, da):
        r = e["r"]; c = COL[e["tipo"]]; box = [r.x0 * Z, r.y0 * Z, r.x1 * Z, r.y1 * Z]
        d.rectangle(box, outline=c + (230,), width=3)
        et = f"{pref}{i}"; w = d.textlength(et, font=f)
        d.rectangle([box[0], box[1] - 24, box[0] + w + 8, box[1]], fill=c + (235,)); d.text((box[0] + 4, box[1] - 24), et, fill="white", font=f)
    im.alpha_composite(st); im.convert("RGB").save(out)


# ---------- 3. ABBINAMENTO (AI: sceglie solo numeri) ----------
PROMPT = ("Nella cartella ci sono P_num.png (una pagina di libro; se ci sono anche P_num_2.png, P_num_3.png sono le pagine vicine)\n"
          "e S_num.png (uno schema fatto a partire da quelle pagine: a volte prende da piu' pagine).\n"
          "Ogni oggetto ha un riquadro e un numero (P1, P2.. e S1, S2..). Qui sotto l'elenco con il testo di ogni oggetto e, per ogni S,\n"
          "i P piu' simili secondo un programma (solo un suggerimento, puo' sbagliare).\n\n{elenco}\n\n"
          "Guarda le due immagini. Per OGNI oggetto S dimmi da quali oggetti P viene: nessuno, uno, o piu' di uno (anche lontani tra loro,\n"
          "se lo schema unisce cose prese da punti diversi). Vale anche per i disegni: da quale testo o figura di P vengono.\n"
          "Se il legame e' incerto metti debole.\n{esempi}"
          'Rispondi SOLO con JSON: {{"S1": {{"p": ["P1"], "debole": false}}, "S2": {{"p": [], "debole": false}}}}')


CORR = QUI / "correzioni_allinea.json"


def correzioni():
    return json.loads(CORR.read_text(encoding="utf-8")) if CORR.exists() else {}


def esempi(n=2):
    """fino a n correzioni fatte a mano (con il perche'), come esempi nel prompt: cosi' Gemini impara dagli errori gia' visti."""
    ee = [a for v in correzioni().values() if isinstance(v, dict) for a in v.get("aggiungi", []) if a.get("testo_s")][:n]
    if not ee:
        return ""
    return "Esempi di legami giusti che erano stati sbagliati:\n" + "\n".join(
        f"- lo schema '{a['testo_s']}' viene da '{a['testo_p']}': {a['perche']}" for a in ee) + "\n"


def elenco(el, pref):
    return "\n".join(f"{pref}{i} [{e['tipo']}]: {e['testo'][:160] or '(senza testo)'}" for i, e in enumerate(el, 1))


def parole(t):
    return set(re.findall(r"[a-zàèéìòù]{4,}", t.lower())) | set(re.findall(r"\d+", t))


def candidati(ep, es, n=3):
    """il CODICE aiuta: per ogni S i 3 P con piu' parole/numeri in comune (riduce le combinazioni da valutare)."""
    righe = []
    for j, e in enumerate(es, 1):
        ws = parole(e["testo"])
        sc = sorted(((len(ws & parole(p["testo"])) / (len(ws) or 1), i) for i, p in enumerate(ep, 1) if ws), reverse=True)[:n]
        sc = [f"P{i} ({v:.1f})" for v, i in sc if v > 0]
        righe.append(f"S{j} simile a: " + (", ".join(sc) if sc else "(nessun testo in comune: guarda le immagini)"))
    return "\n".join(righe)


def abbina(d, ep, es, rifai=False, nome="risposta.txt"):
    f = d / nome
    if not (rifai and f.exists()):
        p = PROMPT.format(elenco=elenco(ep, "P") + "\n\n" + elenco(es, "S") + "\n\n" + candidati(ep, es), esempi=esempi())
        (d / nome.replace("risposta", "prompt")).write_text(p, encoding="utf-8")
        out = subprocess.run([AGY, "-p", p, "--model", "gemini-3.1-pro-high", "--print-timeout", "20m"], capture_output=True,
                             text=True, encoding="utf-8", errors="ignore", timeout=1500, cwd=str(d)).stdout
        f.write_text(out, encoding="utf-8")
    out = f.read_text(encoding="utf-8")
    for i in [m.start() for m in re.finditer(r"\{", out)]:
        try:
            js, _ = json.JSONDecoder().raw_decode(out[i:])
            if isinstance(js, dict) and "pezzi" in js:
                return js
            if isinstance(js, dict) and js and all(re.match(r"S\d+$", str(k)) for k in js):
                gruppi = {}
                for sk, v in js.items():
                    v = v if isinstance(v, dict) else {"p": v}
                    fonti = tuple(sorted(set(v.get("p") or []), key=lambda x: int(re.sub(r"\D", "", x) or 0)))
                    if fonti:
                        g = gruppi.setdefault(fonti, {"s": [], "p": list(fonti), "debole": False}); g["s"].append(sk)
                        g["debole"] = g["debole"] or bool(v.get("debole"))
                return {"pezzi": list(gruppi.values()), "s_solo_miei": [k for k, v in js.items() if not (v.get("p") if isinstance(v, dict) else v)]}
        except ValueError:
            continue
    return {"pezzi": [], "s_solo_miei": []}


# ---------- 4. PEZZI + CONTROLLI (codice) ----------
COLORI = [(192, 80, 77), (79, 129, 189), (120, 160, 80), (128, 100, 162), (230, 140, 60), (70, 160, 180), (150, 120, 90), (200, 90, 150)]


def ids(lista, el, pref):
    out = []
    for x in lista or []:
        m = re.match(pref + r"(\d+)$", str(x).strip())
        if m and 0 < int(m.group(1)) <= len(el):
            out.append(int(m.group(1)) - 1)
    return out


def unione(el, idx):
    r = fitz.Rect(el[idx[0]]["r"])
    for i in idx[1:]:
        r |= el[i]["r"]
    return r


def occupa(e):
    """cio' che un oggetto occupa DAVVERO: righe per il testo (un paragrafo che gira attorno a una figura ha un rettangolo
    che contiene la figura), rettangolo per disegni/immagini."""
    return list(e["righe"]) if e.get("tipo") == "testo" and e.get("righe") else [fitz.Rect(e["r"])]


def ritaglio(pg, r, tenere, out, z=4):
    """05/10 (Gilberto: 'quando prendi un paragrafo e tiri giu' un rettangolo non puoi non tenere conto di quello che prendi attorno'):
    nel riquadro resta NITIDO solo cio' che appartiene al pezzo (tenere = righe/rettangoli dei suoi oggetti); tutto il resto sbiadito."""
    pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), clip=r); im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
    velo = Image.new("RGBA", im.size, (255, 255, 255, 115)); d = ImageDraw.Draw(velo)  # 05/10 velo piu leggero: si legge ancora
    for q in tenere:
        d.rectangle([(q.x0 - r.x0) * z - 2, (q.y0 - r.y0) * z - 2, (q.x1 - r.x0) * z + 2, (q.y1 - r.y0) * z + 2], fill=(0, 0, 0, 0))
    im.alpha_composite(velo); im.convert("RGB").save(out)


def per_pagina(ep, pi):
    """gli oggetti del prof di un pezzo, divisi per pagina (un pezzo puo' prendere da piu' pagine)."""
    g = {}
    for i in pi:
        g.setdefault(ep[i].get("pag", 0), []).append(i)
    return g


def ritaglio_multi(pps, ep, pi, buchi_di, out):
    """ritaglio del prof: una striscia per pagina usata, una sotto l'altra."""
    parti = []
    for pag, idx in sorted(per_pagina(ep, pi).items()):
        r = unione(ep, idx); tmp = out.with_suffix(f".p{pag}.png"); ritaglio(pps[pag], r, [q for i in idx for q in occupa(ep[i])], tmp)
        with Image.open(tmp) as x_:
            parti.append(x_.copy())
        tmp.unlink()
    W_ = max(x.width for x in parti); im = Image.new("RGB", (W_, sum(x.height for x in parti) + 12 * (len(parti) - 1)), (255, 255, 255)); y = 0
    for x in parti:
        im.paste(x, (0, y)); y += x.height + 12
    im.save(out)


def costruisci(chiave, d, pps, pm, ep, es, js):
    RP = QUI / "ritagli_allinea"; RP.mkdir(exist_ok=True)
    usati_p, usati_s, coppie, pezzi = set(), set(), [], []
    c = correzioni().get(chiave, {})  # correzioni a mano per ID: vengono PRIMA, quindi vincono su Gemini
    via = set(c.get("togli", []))
    lista = list(c.get("aggiungi", [])) + [pz for k, pz in enumerate(js.get("pezzi", []), 1) if k not in via]
    for pz in lista:
        si = [i for i in ids(pz.get("s"), es, "S") if i not in usati_s]; pi = ids(pz.get("p"), ep, "P")
        if not si or not pi:
            continue
        usati_s |= set(si); usati_p |= set(pi); pezzi.append((si, pi, bool(pz.get("debole"))))
    for k, (si, pi, debole) in enumerate(pezzi, 1):
        rs = unione(es, si)
        fonti_s = {j: set(pp) for sj, pp, _ in pezzi for j in sj}  # 05/10 (LRU): stessa fonte = stesso blocco, non sbiadirlo
        bs = [es[j]["r"] for j in range(len(es)) if j not in si and j in usati_s and rs.intersects(es[j]["r"]) and not any(fitz.Rect(es[j]["r"]).contains(es[i]["r"]) for i in si)
              and not (fonti_s.get(j, set()) & set(pi))]
        buchi_p = lambda pag, r, idx: [ep[j]["r"] for j in range(len(ep)) if j not in pi and j in usati_p and ep[j].get("pag", 0) == pag
                                       and r.intersects(ep[j]["r"]) and not ep[j].get("intera") and not any(fitz.Rect(ep[j]["r"]).contains(ep[i]["r"]) for i in idx)]
        a = " ".join(ep[i]["testo"] for i in pi if ep[i]["testo"]); b = " ".join(es[i]["testo"] for i in si if es[i]["testo"])
        figura = any(ep[i]["tipo"] in ("foto", "immagine", "disegno") for i in pi) and len(a) < 120
        disegno = any(es[i]["tipo"] in ("disegno", "immagine", "foto") for i in si)
        fa, fb = RP / f"{chiave}_{k}_prof.png", RP / f"{chiave}_{k}_mio.png"
        ritaglio_multi(pps, ep, pi, buchi_p, fa); ritaglio(pm, rs, [q for i in si for q in occupa(es[i])], fb)
        pagine = sorted({ep[i].get("pag", 0) for i in pi})
        coppie.append({"coppia": f"{chiave.rsplit('_p', 1)[1]}:{k}", "pagina": chiave, "debole": debole, "prof_figura": figura,
                       "tipo": "testo+immagine" if disegno else "testo", "prof_testo": a, "mio_testo": b + ("  (+ disegno)" if disegno else ""),
                       "prof_ritaglio": f"ritagli_allinea/{fa.name}", "mio_ritaglio": f"ritagli_allinea/{fb.name}",
                       "piu_pagine": len(pagine) > 1 or pagine != [0],
                       "oggetti": {"s": [f"S{i + 1}" for i in si], "p": [f"P{i + 1}" for i in pi]}})
    non_usati = [i for i in range(len(ep)) if i not in usati_p and not ep[i].get("intera") and ep[i].get("pag", 0) == 0]
    solo_miei = [i for i in range(len(es)) if i not in usati_s]
    controllo_img(chiave, pps, pm, ep, es, pezzi, non_usati, solo_miei)
    controllo_img(chiave, pps, pm, ep, es, pezzi, non_usati, solo_miei, gap=320, suffisso='_linee')
    (OUT / f"{chiave}.json").write_text(json.dumps(coppie, ensure_ascii=False, indent=1), encoding="utf-8")
    return coppie, non_usati, solo_miei


def tratteggio(dr, box, colore, pieno=12, vuoto=8, w=3):
    x0, y0, x1, y1 = box
    for (a, b, c, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        lung = max(abs(c - a), abs(e - b)) or 1; t = 0
        while t < lung:
            t2 = min(t + pieno, lung)
            dr.line([a + (c - a) * t / lung, b + (e - b) * t / lung, a + (c - a) * t2 / lung, b + (e - b) * t2 / lung], fill=colore, width=w)
            t += pieno + vuoto


def area(st, dr, oggetti, pos, c, debole, margine=6, unisci=14):
    """Gilberto 04/10: evidenzia AREE, non un riquadrone. Ogni oggetto (il testo riga per riga) con un margine; gli oggetti vicini
    dello stesso pezzo si fondono (chiusura morfologica) in UNA forma; si disegna la forma piena chiara + il suo bordo.
    pos(e) = (ox, oy) dell'oggetto: la pagina (del prof ce ne possono essere piu' d'una, una sotto l'altra)."""
    W_, H_ = st.size; mask = np.zeros((H_, W_), np.uint8)
    for e in oggetti:
        ox, oy = pos(e)
        for r in (e.get("righe") or [e["r"]]):
            x0, y0, x1, y1 = int(ox + r.x0 * Z) - margine, int(oy + r.y0 * Z) - margine, int(ox + r.x1 * Z) + margine, int(oy + r.y1 * Z) + margine
            cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(W_ - 1, x1), min(H_ - 1, y1)), 255, -1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (unisci, unisci)))
    cont, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cn in cont:
        pts = [tuple(int(v) for v in q[0]) for q in cn]
        if len(pts) < 3:
            continue
        dr.polygon(pts, fill=c + (28 if debole else 45,))
        if debole:  # legame incerto: bordo tratteggiato
            for i in range(0, len(pts), 2):
                dr.line([pts[i], pts[(i + 1) % len(pts)]], fill=c + (230,), width=3)
        else:
            dr.line(pts + [pts[0]], fill=c + (220,), width=3, joint="curve")


def controllo_img(chiave, pps, pm, ep, es, pezzi, non_usati, solo_miei, gap=20, suffisso=''):
    """stesso numero e colore = stesso pezzo; si colorano gli OGGETTI veri; grigio tratteggiato = non usato / solo mio.
    A sinistra le pagine del prof (la principale e, se usate, le vicine) una sotto l'altra; a destra la mia pagina."""
    usate = sorted({0} | {ep[i].get("pag", 0) for _, pi, _ in pezzi for i in pi})
    img = lambda pg, clip=None: (lambda x: Image.frombytes("RGB", (x.width, x.height), x.samples).convert("RGBA"))(pg.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=clip))
    CLIP = {0: pps[0].rect}
    for pag in usate[1:]:  # Gilberto 04/10: delle pagine vicine si mostra solo la parte usata (+ margine), non la pagina intera
        r = unione(ep, [i for _, pi, _ in pezzi for i in pi if ep[i].get("pag", 0) == pag])
        CLIP[pag] = fitz.Rect(r.x0 - 25, r.y0 - 25, r.x1 + 25, r.y1 + 25) & pps[pag].rect
    ips = {pag: img(pps[pag], CLIP[pag] if pag else None) for pag in usate}; im = img(pm)
    OY, y = {}, 30
    for pag in usate:
        OY[pag] = y; y += ips[pag].height + 40
    LW = max(x.width for x in ips.values()); SX = LW + 20 + gap
    tela = Image.new("RGBA", (SX + im.width + 20, max(y, im.height + 40)), (255, 255, 255, 255))
    st = Image.new("RGBA", tela.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(st); f = ImageFont.truetype("arialbd.ttf", 24); fp = ImageFont.truetype("arial.ttf", 15)
    for pag in usate:
        tela.paste(ips[pag], (20, OY[pag]))
        if len(usate) > 1:
            dr.text((24, OY[pag] - 26), "pagina principale" if pag == 0 else f"pagina vicina {pag} (solo la parte usata)", fill=(90, 90, 90, 255), font=fp)
    tela.paste(im, (SX, 30))
    posP = lambda e: (20 - CLIP[e.get("pag", 0)].x0 * Z, OY.get(e.get("pag", 0), 30) - CLIP[e.get("pag", 0)].y0 * Z); posS = lambda e: (SX, 30)
    box = lambda e, pos: [pos(e)[0] + e["r"].x0 * Z, pos(e)[1] + e["r"].y0 * Z, pos(e)[0] + e["r"].x1 * Z, pos(e)[1] + e["r"].y1 * Z]
    # oggetti del prof usati da PIU' pezzi: colorati una volta sola (col primo pezzo), con i numeri di tutti accanto
    chi_usa = {}
    for k, (si, pi, _) in enumerate(pezzi, 1):
        for i in pi:
            chi_usa.setdefault(i, []).append(k)
    for k, (si, pi, debole) in enumerate(pezzi, 1):
        c = COLORI[(k - 1) % len(COLORI)]
        area(st, dr, [es[i] for i in si], posS, c, debole)
        area(st, dr, [ep[i] for i in pi if chi_usa[i][0] == k], posP, c, debole)
        bx = box(es[si[0]], posS); dr.ellipse([bx[0] - 6, bx[1] - 6, bx[0] + 28, bx[1] + 28], fill=c + (235,)); dr.text((bx[0] + 3, bx[1] - 3), str(k), fill="white", font=f)
    for i, kk in chi_usa.items():  # una sola etichetta per oggetto: '3' oppure '1·2·3' se serve a piu' pezzi
        bx = box(ep[i], posP); et = "·".join(str(k) for k in kk); w = dr.textlength(et, font=f) + 12
        c = COLORI[(kk[0] - 1) % len(COLORI)]
        dr.rounded_rectangle([bx[0] - 6, bx[1] - 6, bx[0] - 6 + w, bx[1] + 22], radius=12, fill=c + (235,)); dr.text((bx[0], bx[1] - 5), et, fill="white", font=f)
    for lista, el, pos, et in ((non_usati, ep, posP, "non usato"), (solo_miei, es, posS, "solo mio")):
        for i in lista:
            bx = box(el[i], pos); tratteggio(dr, bx, (120, 120, 120, 210), 8, 6, 2)
            dr.rectangle([bx[0], bx[1] - 17, bx[0] + 64, bx[1] - 1], fill=(255, 255, 255, 230)); dr.text((bx[0] + 2, bx[1] - 17), et, fill=(90, 90, 90, 255), font=fp)
    if gap > 100:  # Gilberto 04/10: linee OBLIQUE, una per ogni fonte: dal bordo destro dell'oggetto del prof al bordo sinistro del mio pezzo
        for k, (si, pi, debole) in enumerate(pezzi, 1):
            c = COLORI[(k - 1) % len(COLORI)]; rs = unione(es, si)
            for n, i in enumerate(pi):
                bp = box(ep[i], posP)
                a = (bp[2] + 4, (bp[1] + bp[3]) / 2)
                yb = 30 + rs.y0 * Z + (rs.height * Z) * (n + 1) / (len(pi) + 1)  # fonti diverse arrivano in punti diversi del mio pezzo
                b = (SX + rs.x0 * Z - 6, yb)
                dr.line([a, b], fill=c + (200,), width=3)
                dr.ellipse([a[0] - 5, a[1] - 5, a[0] + 5, a[1] + 5], fill=c + (255,)); dr.polygon([b, (b[0] - 13, b[1] - 7), (b[0] - 13, b[1] + 7)], fill=c + (255,))
    tela.alpha_composite(st); tela.convert("RGB").save(OUT / f"{chiave}{suffisso}.jpg", quality=86)


# ---------- 5. PROVE (coppie note: se una cade si vede subito) ----------
PROVE = {"schema_esercizi_p02": [("5 BIT ETICHETTA", "2 2 3", "tabella dei bit -> barra 2|2|3")],
         "schema_esercizi_p06": [("Finora si", "Dobbiamo creare una memoria", "paragrafo del prof -> sua Esempio/Spiegazione")]}


def unisci():
    """coppie_pdf.json per il regolario: tutti i pezzi di allinea/, tranne i copiati (i pezzi-figura si tengono sempre)."""
    def copiata(a, b):  # copiata da esperimento.py (repo: niente dipendenza da quel file)
        par = lambda t: set(re.findall(r"[a-zàèéìòù]{4,}", t.lower()))
        pb, pa = par(b), par(a)
        return bool(pb) and len(pb & pa) / len(pb) > 0.6 and len(pb) / max(1, len(pa)) > 0.6
    tutte = []
    for f in sorted(OUT.glob("*.json")):
        for c in json.loads(f.read_text(encoding="utf-8")):
            b = c["mio_testo"].split("  (+")[0]
            c["copiata"] = bool(not c["prof_figura"] and c["prof_testo"] and b and copiata(c["prof_testo"], b))
            tutte.append(c)
    # 05/10: coppie_pdf_tutte.json anche coi copiati (per la revisione: nasconderli faceva sembrare sbagliato il legame, es. LRU)
    (QUI / "coppie_pdf_tutte.json").write_text(json.dumps(tutte, ensure_ascii=False, indent=1), encoding="utf-8")
    tutte = [c for c in tutte if not c["copiata"]]
    (QUI / "coppie_pdf.json").write_text(json.dumps(tutte, ensure_ascii=False, indent=1), encoding="utf-8")
    print("coppie_pdf.json:", len(tutte), "coppie,", sum(c["prof_figura"] for c in tutte), "figure")


def prove(chiave, ep, es, coppie):
    for tp, ts, nome in PROVE.get(chiave, []):
        ip = [f"P{i + 1}" for i, e in enumerate(ep) if tp in e["testo"]]; is_ = [f"S{i + 1}" for i, e in enumerate(es) if ts in e["testo"]]
        ok = any(set(ip) & set(c["oggetti"]["p"]) and set(is_) & set(c["oggetti"]["s"]) for c in coppie)
        print(f"   prova '{nome}': {'OK' if ok else 'CADUTA'} (P {ip}, S {is_})")


def una(materia, chiave, voce, vicine=None):
    """prima SOLO la pagina principale; le pagine vicine (altre_pagine) solo se restano scollegati piu' del 30% dei miei oggetti
    (04/10: con le vicine sempre, p04 migliora ma p05/p07 peggiorano: troppi oggetti e Gemini si perde)."""
    d = OUT / chiave; d.mkdir(exist_ok=True)
    fm, nm = pdf_mio(materia, chiave); fp = pdf_prof(materia, voce)
    doc = fitz.open(fp); pm = fitz.open(fm)[nm]
    if vicine is None:
        vicine = "--vicine" in sys.argv
    nump = [voce["pagina"]] + ([n for n in voce.get("altre_pagine", [])[:2] if 0 < n <= len(doc)] if vicine else [])
    pps = [doc[n - 1] for n in nump]; ep = []
    for f_ in d.glob("P_num_*.png"):
        f_.unlink()
    for pag, pg in enumerate(pps):  # Gilberto 04/10: 'quando prendo da due pagine e metto in una' -> anche le pagine vicine
        el = oggetti(pg)
        for e in el:
            e["pag"] = pag
        numerata(pg, el, "P", d / ("P_num.png" if pag == 0 else f"P_num_{pag + 1}.png"), da=len(ep) + 1); ep += el
    es = oggetti(pm, filtri=chiave in FILTRI_MIO)
    numerata(pm, es, "S", d / "S_num.png")
    conta = lambda el: ", ".join(f"{t} {sum(e['tipo'] == t for e in el)}" for t in COL)
    print(f"{chiave}{' (+ pagine vicine)' if vicine else ''}: prof {len(ep)} oggetti ({conta(ep)}), mio {len(es)} ({conta(es)})")
    if "--solo-oggetti" in sys.argv:
        return ep, es
    base = sys.argv[sys.argv.index("--risposte") + 1] if "--risposte" in sys.argv else "risposta_claude" if "--claude" in sys.argv else "risposta"
    nome = base + ("" if vicine else "_una") + ".txt"  # --risposte risposta_claude3: versioni dei legami a confronto
    # 05/10 Gilberto: 'i legami vanno fatti con calma da Claude, contestualizzati: quelli di Gemini fanno cagare'
    # --claude: legge le risposte scritte dagli agenti Claude (stesso formato JSON), Gemini non viene chiamato
    js = abbina(d, ep, es, "--rifai" in sys.argv or "--claude" in sys.argv or "--risposte" in sys.argv, nome)
    coppie, nu, sm = costruisci(chiave, d, pps, pm, ep, es, js)
    print(f"   {len(coppie)} pezzi, {len(nu)} oggetti del prof non usati, {len(sm)} oggetti solo miei")
    if not vicine and voce.get("altre_pagine") and len(sm) > .3 * len(es) and "--una-pagina" not in sys.argv:
        print("   troppi oggetti scollegati -> riprovo con le pagine vicine")
        return una(materia, chiave, voce, vicine=True)
    prove(chiave, ep, es, coppie)
    return coppie


if __name__ == "__main__":
    if "--unisci" in sys.argv:
        unisci(); sys.exit()
    mp = json.loads((ANN / "architettura" / "fonti" / "mappa.json").read_text(encoding="utf-8"))
    salta = {sys.argv[sys.argv.index("--risposte") + 1]} if "--risposte" in sys.argv else set()  # il valore di --risposte non e' una pagina
    for ch in [a for a in sys.argv[1:] if not a.startswith("--") and a not in salta]:
        una("architettura", ch, mp[ch])
