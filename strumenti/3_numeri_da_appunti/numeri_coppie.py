"""ESPERIMENTO NUMERI (PROGETTO_NUMERI.md, Gilberto 04/10): le coppie prof -> mio ridotte a numeri, su due rami (testo, grafica).
1) MISURE (codice) per ogni coppia di allinea/   2) l'agente (Gemini) vede una TABELLA delle coppie di allenamento e propone
quali misure contano e in che range   3) il codice VERIFICA i range sulle coppie tenute da parte -> parametri.json (solo quelli che reggono).
Uso: python numeri_coppie.py [--solo-misure]   ->  NUMERI_COPPIE.md, numeri_coppie.json, parametri.json"""
import json, random, re, statistics as st, subprocess, sys
from pathlib import Path
import fitz
from allinea import OUT, oggetti, unione, ids
from allinea_auto import AGY, ANN, pdf_mio, pdf_prof

QUI = Path(__file__).parent
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def numeri_in(t):
    return [float(x.replace(",", ".")) for x in NUM.findall(t)]


def ramo_testo(a, b):
    pa, pb = len(a.split()), len(b.split())
    na, nb = numeri_in(a), numeri_in(b)
    return {"parole_prof": pa, "parole_mie": pb, "rapporto_parole": round(pb / pa, 2) if pa else None,
            "frasi_prof": len(re.findall(r"[.!?:](\s|$)", a)), "frasi_mie": len(re.findall(r"[.!?:](\s|$)", b)),
            "numeri_prof": len(na), "numeri_miei": len(nb),
            "numero_max_prof": max(na) if na else None, "numero_max_mio": max(nb) if nb else None,
            "maiuscole_mie": round(sum(c.isupper() for c in b) / max(1, sum(c.isalpha() for c in b)), 2) if b else None}


def ramo_grafica(pg, r):
    """dentro il riquadro: disegni vettoriali (riquadri, linee/frecce, colori di riempimento), grandezze del carattere, area disegnata."""
    dd = [d for d in pg.get_drawings() if r.contains(d["rect"]) and d["rect"].get_area() < .9 * r.get_area()]
    rett = sum(1 for d in dd for it in d["items"] if it[0] in ("re", "qu"))
    linee = sum(1 for d in dd for it in d["items"] if it[0] == "l")
    colori = len({tuple(round(c, 1) for c in d["fill"]) for d in dd if d.get("fill")})
    size = {round(sp["size"]) for b in pg.get_text("dict", clip=r)["blocks"] if b.get("type") == 0 for l in b["lines"] for sp in l["spans"] if sp["text"].strip()}
    area_dis = sum(d["rect"].get_area() for d in dd) / max(1, r.get_area())
    return {"riquadri": rett, "linee": linee, "colori": colori, "grandezze_testo": len(size), "area_disegnata": round(min(area_dis, 9), 2)}


def misure():
    mp = json.loads((ANN / "architettura" / "fonti" / "mappa.json").read_text(encoding="utf-8"))
    righe = []
    for f in sorted(OUT.glob("schema_esercizi_p*.json")):
        chiave = f.stem; voce = mp[chiave]
        fm, nm = pdf_mio("architettura", chiave); pp, pm = fitz.open(pdf_prof("architettura", voce))[voce["pagina"] - 1], fitz.open(fm)[nm]
        ep, es = oggetti(pp), oggetti(pm)
        for c in json.loads(f.read_text(encoding="utf-8")):
            si, pi = ids(c["oggetti"]["s"], es, "S"), ids(c["oggetti"]["p"], ep, "P")
            if not si or not pi:
                continue
            gp, gs = ramo_grafica(pp, unione(ep, pi)), ramo_grafica(pm, unione(es, si))
            r = {"coppia": c["coppia"], "figura_prof": c["prof_figura"], "disegno_mio": c["tipo"] == "testo+immagine"}
            r.update(ramo_testo(c["prof_testo"], c["mio_testo"].split("  (+")[0]))
            r.update({f"{k}_prof": v for k, v in gp.items()}); r.update({f"{k}_mio": v for k, v in gs.items()})
            # unione dei due rami: il testo sparito e' diventato disegno?
            r["testo_diventa_disegno"] = bool(r["rapporto_parole"] is not None and r["rapporto_parole"] < .5 and gs["riquadri"] > gp["riquadri"])
            righe.append(r)
    return righe


def tabella_md(righe, campi):
    out = ["| " + " | ".join(campi) + " |", "|" + "---|" * len(campi)]
    for r in righe:
        out.append("| " + " | ".join("" if r.get(k) is None else str(r.get(k)) for k in campi) + " |")
    return "\n".join(out)


PROMPT = ("Ogni riga e' una coppia: un pezzo di una pagina di libro (prof) e il pezzo di uno schema fatto da quella pagina (mio).\n"
          "Le colonne sono misure fatte da un programma (testo e grafica). Guarda la tabella e trova le misure che sembrano REGOLARI\n"
          "(quasi sempre in un certo intervallo, o legate tra loro). Non spiegare, rispondi SOLO con JSON:\n"
          '[{{"misura": "rapporto_parole", "min": 0.1, "max": 0.4, "quando": "sempre | se figura_prof | se disegno_mio", "perche": "..."}}]\n\n{tab}')


TUTTE = []  # tutte le coppie (per capire se un intervallo copre tutto = banale)


def vale(q, r):
    """la condizione 'quando' di Gemini: sempre / se figura_prof / se disegno_mio / se X > 0 (confronti semplici)."""
    q = (q or "sempre").strip().lower()
    if q.startswith("sempre"):
        return True
    if q.endswith("figura_prof"):
        return bool(r["figura_prof"])
    if q.endswith("disegno_mio"):
        return bool(r["disegno_mio"])
    m = re.search(r"(\w+)\s*(>=|<=|==|!=|>|<)\s*([\d.]+|true|false)", q)
    if m and m.group(1) in r and isinstance(r[m.group(1)], (int, float)):
        a, op = r[m.group(1)], m.group(2); b = {"true": 1, "false": 0}.get(m.group(3), None)
        b = float(m.group(3)) if b is None else b
        return {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b, "==": a == b, "!=": a != b}[op]
    return False


def verifica(proposte, prova):
    """un range resta solo se vale per almeno il 70% delle coppie tenute da parte (che l'agente non ha visto)."""
    tenuti = []
    for p in proposte:
        k = p.get("misura"); q = p.get("quando", "sempre")
        rr = [r for r in prova if r.get(k) is not None and vale(q, r)]
        if len(rr) < 2 or p.get("min") is None or p.get("max") is None:
            continue
        dentro = sum(p["min"] <= r[k] <= p["max"] for r in rr) / len(rr)
        p["verifica"] = f"{dentro:.0%} di {len(rr)} coppie mai viste"
        tutti = [r[k] for r in TUTTE if isinstance(r.get(k), (int, float))]
        p["banale"] = bool(tutti) and p["min"] <= min(tutti) and p["max"] >= max(tutti)  # copre tutti i valori: non scopre niente
        if dentro >= .7 and not p["banale"]:
            tenuti.append(p)
    return tenuti


def main():
    if "--riverifica" in sys.argv:  # rifa' solo la verifica sulle proposte gia' salvate (senza Gemini)
        par = json.loads((QUI / "parametri.json").read_text(encoding="utf-8")); righe = json.loads((QUI / "numeri_coppie.json").read_text(encoding="utf-8"))
        TUTTE[:] = righe
        random.seed(4); random.shuffle(righe); n = max(2, len(righe) * 7 // 10)
        par["tenuti"] = verifica(par["proposti"], righe[n:])
        (QUI / "parametri.json").write_text(json.dumps(par, ensure_ascii=False, indent=1), encoding="utf-8")
        for t in par["proposti"]:
            print(f"  {t['misura']} {t.get('min')}-{t.get('max')} ({t.get('quando')}) -> {t.get('verifica', 'non provabile')}{' BANALE' if t.get('banale') else ''}")
        return
    righe = misure()
    (QUI / "numeri_coppie.json").write_text(json.dumps(righe, ensure_ascii=False, indent=1), encoding="utf-8")
    campi = [k for k in righe[0] if k != "coppia"]
    md = ["# Numeri delle coppie (codice, nessuna AI)", f"{len(righe)} coppie da allinea/. Mediana e range 10-90% per misura:\n",
          "| misura | mediana | 10% | 90% |", "|---|---|---|---|"]
    for k in campi:
        v = sorted(r[k] for r in righe if isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool))
        if len(v) >= 3:
            md.append(f"| {k} | {st.median(v):g} | {v[len(v) // 10]:g} | {v[min(len(v) - 1, len(v) * 9 // 10)]:g} |")
    md += ["", "## Tutte le coppie", tabella_md(righe, ["coppia"] + campi)]
    (QUI / "NUMERI_COPPIE.md").write_text("\n".join(md), encoding="utf-8")
    print(f"misure: {len(righe)} coppie, {len(campi)} misure -> NUMERI_COPPIE.md")
    if "--solo-misure" in sys.argv:
        return
    TUTTE[:] = righe
    random.seed(4); random.shuffle(righe); n = max(2, len(righe) * 7 // 10)
    allena, prova = righe[:n], righe[n:]
    d = QUI / "giri" / "numeri"; d.mkdir(parents=True, exist_ok=True)
    p = PROMPT.format(tab=tabella_md(allena, campi)); (d / "prompt.txt").write_text(p, encoding="utf-8")
    out = subprocess.run([AGY, "-p", p, "--model", "gemini-3.1-pro-high", "--print-timeout", "15m"], capture_output=True, text=True,
                         encoding="utf-8", errors="ignore", timeout=1200, cwd=str(d)).stdout
    (d / "risposta.txt").write_text(out, encoding="utf-8")
    m = re.search(r"\[.*\]", out, re.S); proposte = []
    try:
        proposte = json.loads(m.group()) if m else []
    except ValueError:
        pass
    tenuti = verifica(proposte, prova)
    (QUI / "parametri.json").write_text(json.dumps({"tenuti": tenuti, "proposti": proposte, "allena": len(allena), "prova": len(prova)},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gemini propone {len(proposte)} range; reggono sulle coppie mai viste: {len(tenuti)}")
    for t in tenuti:
        print(f"  {t['misura']} {t['min']}-{t['max']} ({t.get('quando')}) · {t['verifica']} · {t.get('perche', '')[:80]}")


if __name__ == "__main__":
    main()
