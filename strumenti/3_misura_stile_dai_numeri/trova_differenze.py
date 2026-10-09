"""UN comando: trova i numeri che distinguono i TUOI schemi da quelli generati da un'AI, li mette in classifica
(sgama x convertibile, x efficace se ci sono prove con/senza frasi), scrive le frasi-istruzione per il modello e i range per il controllo.
Solo codice: niente OCR, niente modelli. Memoria < 1 GB.

  python trova_differenze.py --suoi miei_schemi.pdf [altri.pdf|png ...] --generate cartella_generate [--out risultati]
         [--prof-parole N] [--efficace-senza cartella --efficace-con cartella]

--suoi       PDF vettoriali (meglio: testo, font, colori esatti) o PNG (solo le misure sull'immagine).
--generate   cartella con pagine generate: *.html / *.svg (rese in PNG da sole) e/o *.png. Cerca anche nelle sottocartelle.
--prof-parole  numero di parole della pagina del docente (per "parole rispetto al prof"; se manca la metrica salta).
Uscita in --out: CLASSIFICA.md, FRASI_PER_IL_MODELLO.md, numeri.json (range per controlla_stile.py --rif), classifica.png."""
import argparse, json, sys, tempfile
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D))
from misura import metriche as attenzione
from misura2 import immagine
from combinazioni import per_pagina
import combinazioni
from classifica_info import INFO

# frasi-istruzione con i TUOI range (lo, hi, med); None = non convertibile in frase
FRASE = {
    "corpo_medio_o_grande_%": lambda lo, hi, m: f"Il testo corrente ha font-size di almeno 14 px su una pagina larga 794 px: almeno il {lo:.0f}% dei caratteri (mediana {m:.0f}%).",
    "testo_su_fondo_pagina_%": lambda lo, hi, m: f"Almeno il {lo:.0f}% del testo sta direttamente sul fondo pagina: niente background dietro paragrafi ed etichette, salvo la fascia titolo.",
    "testo_evidenziato_%": lambda lo, hi, m: f"Background colorato aderente al testo (pillola, casella, evidenziatore) al massimo sul {hi:.0f}% del testo.",
    "vuoto_terzo_basso_%": lambda lo, hi, m: f"Il disegno arriva fino in fondo: nel terzo basso della pagina resta vuoto tra il {lo:.0f}% e il {hi:.0f}% dello spazio.",
    "blocco_piu_grande_%": lambda lo, hi, m: f"Nessun gruppo di contenuto (separato dagli altri da circa 16 px di spazio) supera il {hi:.0f}% del contenuto: niente unico pannello che contiene tutto.",
    "colore_forte_%": lambda lo, hi, m: f"Un solo colore forte (saturo) su circa il {lo:.0f}-{hi:.0f}% della pagina (mediana {m:.0f}%): fascia titolo + poche evidenziazioni.",
    "zone_forti": lambda lo, hi, m: f"Il colore forte compare in al massimo {hi:.0f} punti separati della pagina (di solito {m:.0f}).",
    "tinta_dominante_%": lambda lo, hi, m: f"Almeno il {lo:.0f}% del colore della pagina appartiene a una sola famiglia di tinta; le altre solo come tocchi piccoli.",
    "parole_su_prof_%": lambda lo, hi, m: f"Tieni circa il {lo:.0f}-{hi:.0f}% delle parole della pagina del docente: le frasi che spiegano il perché restano.",
    "parole_in_righe_lunghe_%": lambda lo, hi, m: f"Circa il {m:.0f}% delle parole (almeno il {lo:.0f}%) sta in frasi di almeno 5 parole su righe larghe almeno un terzo della pagina.",
    "parole": lambda lo, hi, m: f"La pagina contiene circa {lo:.0f}-{hi:.0f} parole.",
    "combinazioni_stile_n": lambda lo, hi, m: f"Al massimo {hi:.0f} combinazioni diverse di colore × font × corpo × peso nel testo.",
    "dentro_riquadri_%": lambda lo, hi, m: f"Al massimo il {hi:.0f}% della pagina sta dentro riquadri chiusi.",
    "vuoto_%": lambda lo, hi, m: f"Spazio vuoto tra il {lo:.0f}% e il {hi:.0f}% della pagina.",
    "forme_linee_%": lambda lo, hi, m: f"Circa il {m:.0f}% delle forme sono linee (collegamenti), non riquadri.",
}


def pagine_suoi(files, tmp):
    out = []  # (nome, png, elementi|None)
    for f in map(Path, files):
        if f.suffix.lower() == ".pdf":
            import fitz
            from elementi import pagina_pdf
            doc = fitz.open(f)
            for i, pg in enumerate(doc):
                png = tmp / f"suo_{f.stem}_{i + 1}.png"; pg.get_pixmap(dpi=110).save(png)
                out.append((f"{f.name} p.{i + 1}", png, pagina_pdf(pg)))
        else:
            out.append((f.name, f, None))
    return out


def rendi(src, png):
    from playwright.sync_api import sync_playwright
    from elementi import sorgente
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        pg.set_content(sorgente(src)); pg.wait_for_timeout(300); pg.screenshot(path=str(png)); b.close()


def generate(cartella, tmp):
    from elementi import da_html
    c = Path(cartella); out = []; usati = set()
    tutti = sorted(list(c.rglob("*.html")) + list(c.rglob("*.svg")))
    # se in una cartella c'e' pagina.html/svg, conta solo quella (le altre sono bozze/copie dell'agente)
    tutti = [s for s in tutti if s.stem == "pagina" or not any(x.stem == "pagina" for x in tutti if x.parent == s.parent)]
    for src in tutti:
        png = src.with_suffix(".png")  # pagina.html -> pagina.png accanto, se c'e'
        if not png.exists(): png = tmp / f"gen_{len(out)}.png"; rendi(src, png)
        usati.add(png.resolve()); out.append((str(src.relative_to(c)), png, da_html([("x", src)])["x"]))
    for png in sorted(c.rglob("*.png")):
        if png.resolve() not in usati and png.name != "prof.png": out.append((str(png.relative_to(c)), png, None))
    return out


def misura_tutto(pagine, prof_parole):
    combinazioni.PROF_PAROLE.clear()
    if prof_parole: combinazioni.PROF_PAROLE["p03"] = prof_parole  # per_pagina usa la chiave p03 per le pagine non "gilberto"
    res = []
    for nome, png, el in pagine:
        m = {**attenzione(png), **immagine(png)}
        if el: m.update(per_pagina(nome, el))
        res.append({"pagina": nome, **m})
    return res


def classifica(suoi, gen, eff=None):
    righe = []
    for k, (nome, rob, conv, _) in INFO.items():
        s = [x[k] for x in suoi if k in x]; g = [x[k] for x in gen if k in x]
        if not s or not g: continue
        lo, hi, med = min(s), max(s), float(np.median(s))
        fuori = float(np.mean([(v < lo) or (v > hi) for v in g]))
        sgama = fuori if rob in ("si", "sorgente") else 0.0
        e = (eff or {}).get(k)
        punt = sgama * conv * (e if e is not None else 1)
        righe.append({"k": k, "nome": nome, "lo": lo, "hi": hi, "med": med, "gen_med": float(np.median(g)), "fuori": fuori, "rob": rob, "conv": conv,
                      "eff": e, "punteggio": punt, "frase": FRASE[k](lo, hi, med) if k in FRASE and conv > 0 else None})
    tenuta = lambda r: r["fuori"] >= 0.5 and r["conv"] > 0 and r["rob"] in ("si", "sorgente") and r["frase"]
    righe.sort(key=lambda r: (-bool(tenuta(r)), -r["punteggio"], -r["fuori"]))
    for r in righe: r["tenuta"] = bool(tenuta(r))
    return righe


def efficacia(suoi, senza, con):
    out = {}
    for k in INFO:
        s = [x[k] for x in suoi if k in x]
        if not s: continue
        lo, hi = min(s), max(s); dentro = lambda L: [lo <= x[k] <= hi for x in L if k in x]
        dc = dentro(con)
        if dc: out[k] = sum(dc) / len(dc)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suoi", nargs="+", required=True); ap.add_argument("--generate", required=True)
    ap.add_argument("--out", default="risultati_numeri"); ap.add_argument("--prof-parole", type=int)
    ap.add_argument("--efficace-senza"); ap.add_argument("--efficace-con")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="numeri_"))
    print("misuro i tuoi schemi...", flush=True); suoi = misura_tutto(pagine_suoi(a.suoi, tmp), None)
    print("misuro le generate...", flush=True); gen = misura_tutto(generate(a.generate, tmp), a.prof_parole)
    # ponytail: "parole rispetto al prof" per i TUOI non si calcola (servirebbe la pagina del prof di ogni tuo schema): la metrica salta
    eff = None
    if a.efficace_senza and a.efficace_con:
        print("misuro le prove di efficacia...", flush=True)
        eff = efficacia(suoi, misura_tutto(generate(a.efficace_senza, tmp), a.prof_parole), misura_tutto(generate(a.efficace_con, tmp), a.prof_parole))
    R = classifica(suoi, gen, eff)
    (out / "misure.json").write_text(json.dumps({"suoi": suoi, "generate": gen}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (out / "numeri.json").write_text(json.dumps({"range": {r["k"]: [r["lo"], r["hi"]] for r in R}}, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Classifica dei numeri", "", f"Tuoi: {len(suoi)} pagine. Generate: {len(gen)} pagine.",
          "sgama = quota di generate fuori dal tuo min-max (zero se la misura dipende dalla risoluzione); convertibile 1 / 0,6 / 0; efficace = quota di pagine 'con frasi' nel tuo range.", "",
          "| # | numero | tuo min-max (mediana) | generate (mediana) | sgama | convertibile | efficace | punteggio | tenuta |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(R, 1):
        e = "-" if r["eff"] is None else f"{r['eff']:.2f}"
        md.append(f"| {i} | {r['nome']} | {r['lo']:g}-{r['hi']:g} ({r['med']:g}) | {r['gen_med']:g} | {r['fuori']:.2f} | {r['conv']} | {e} | {r['punteggio']:.2f} | {'SI' if r['tenuta'] else ''} |")
    (out / "CLASSIFICA.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    fr = ["# Frasi per il modello che genera (incollale nella parte stile del prompt)", ""] + [f"{i}. {r['frase']}" for i, r in enumerate([r for r in R if r["tenuta"]], 1)]
    fr += ["", "## Controllo automatico di una pagina generata", "```",
           f"python {Path(__file__).with_name('controlla_stile.py').name} pagina.png --sorgente pagina.html --rif {out / 'numeri.json'}" + (f" --prof-parole {a.prof_parole}" if a.prof_parole else ""), "```"]
    (out / "FRASI_PER_IL_MODELLO.md").write_text("\n".join(fr) + "\n", encoding="utf-8")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rr = R[::-1]; fig, ax = plt.subplots(figsize=(10, 0.4 * len(rr) + 1.5), dpi=110)
    ax.barh(range(len(rr)), [r["fuori"] for r in rr], color=["#FF644B" if r["tenuta"] else "#C8B8B0" for r in rr])
    ax.set_yticks(range(len(rr)), [r["nome"] for r in rr], fontsize=9); ax.set_xlim(0, 1); ax.set_xlabel("quanto sgama (corallo = tenuta)")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "classifica.png", facecolor="white"); plt.close(fig)
    print(f"\nTenute: {sum(r['tenuta'] for r in R)}. Apri {out / 'CLASSIFICA.md'} e {out / 'FRASI_PER_IL_MODELLO.md'}")
    for r in R[:8]: print(f"  {'SI' if r['tenuta'] else '  '} {r['fuori']:.2f} {r['nome']}")


if __name__ == "__main__":
    main()
