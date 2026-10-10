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
# se nei TUOI il numero e' sempre 0 (appunti senza colore): frase diversa o nessuna frase
ZERO = {"colore_forte_%": "Nessun colore forte (saturo): testo e disegni in nero o grigio, al massimo qualche tinta pastello.",
        "zone_forti": None, "tinta_dominante_%": None, "testo_evidenziato_%": "Niente background colorato dietro il testo (pillole, caselle, evidenziatore)."}


IMG = {".png", ".jpg", ".jpeg", ".webp"}
FOTO = {".jpg", ".jpeg"}


def errore(msg):
    """input sbagliato: messaggio in italiano e exit code 1 (niente traceback)"""
    print(f"\nERRORE: {msg}", file=sys.stderr, flush=True); sys.exit(1)


def apri_pdf(f):
    import fitz
    fitz.TOOLS.mupdf_display_errors(False)  # nasconde "MuPDF error: No common ancestor in structure tree": non e' un errore vero
    if not f.is_file(): errore(f"{f} non esiste.")
    try: doc = fitz.open(f)
    except Exception: errore(f"{f.name} non e' un PDF valido (vuoto o rovinato). Da Word/Pages: File > Esporta > PDF.")
    if doc.page_count == 0: errore(f"{f.name} non ha pagine.")
    return doc


def apri_png(f):
    from PIL import Image
    if not f.is_file(): errore(f"{f} non esiste.")
    if f.suffix.lower() not in IMG and f.suffix.lower() != ".pdf":
        errore(f"{f.name}: formato {f.suffix or 'senza estensione'} non letto. Servono PDF o immagini (.png/.jpg). Da Word: File > Esporta > PDF.")
    try: Image.open(f).verify()
    except Exception: errore(f"{f.name} non e' un'immagine valida (vuota o rovinata).")
    return f


def pagine_suoi(files, tmp):
    out = []  # (nome, png, elementi|None)
    for f in map(Path, files):
        if f.suffix.lower() == ".pdf":
            from elementi import pagina_pdf
            doc = apri_pdf(f)
            for i, pg in enumerate(doc):
                png = tmp / f"suo_{f.stem}_{i + 1}.png"; pg.get_pixmap(dpi=110).save(png)
                out.append((f"{f.name} p.{i + 1}", png, pagina_pdf(pg)))
        else:
            out.append((f.name, apri_png(f), None))
    if any(f.suffix.lower() in FOTO for f in map(Path, files)):
        print("  AVVISO: foto (.jpg): ombre e fondo grigio contano come disegno (il vuoto esce piu' basso). Meglio una scansione o una foto ritagliata con fondo bianco.", flush=True)
    return out


def senza_niente(m, el):
    """pagina senza testo vero e senza nessun colore: bianca, oppure scansione in bianco e nero"""
    return not (el and el.get("testi")) and m.get("colore_forte_%", 0) == 0 and m.get("pastello_%", 0) == 0


def togli_vuote(suoi, pagine):
    """i tuoi schemi: via le pagine senza testo ne' colore (darebbero regole tipo 'colore forte 0-0%'); se non resta niente, stop"""
    el = {nome: e for nome, _, e in pagine}
    vuote = [x["pagina"] for x in suoi if senza_niente(x, el.get(x["pagina"]))]
    if len(vuote) == len(suoi):
        errore("nei tuoi schemi non c'e' niente da misurare: nessun testo e nessun colore "
               f"({', '.join(vuote[:3])}{' ...' if len(vuote) > 3 else ''}). Pagina bianca o scansione in bianco e nero? "
               "Serve il PDF esportato da Canva/Word/GoodNotes (con testo) o una pagina a colori.")
    for v in vuote: print(f"  AVVISO: {v}: niente testo ne' colore, la salto.", flush=True)
    senza_testo = [x for x, _, e in pagine if x not in vuote and e is not None and not e.get("testi")]  # e = None: immagine, non PDF
    if senza_testo: print(f"  AVVISO: {len(senza_testo)} pagine PDF senza testo (scansione?): misuro solo l'immagine (colore, vuoto, blocchi).", flush=True)
    tieni = [x for x in suoi if x["pagina"] not in vuote]
    if len(tieni) < 3: print(f"  AVVISO: solo {len(tieni)} pagine tue: i range (min-max) escono strettissimi, meglio almeno 3-5 pagine.", flush=True)
    if all(x.get("colore_forte_%", 0) == 0 for x in tieni):
        print("  AVVISO: nei tuoi schemi non c'e' colore forte: le frasi su colore e disegni contano poco (appunti solo testo?).", flush=True)
    return tieni


def rendi(src, png):
    from playwright.sync_api import sync_playwright
    from elementi import sorgente
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        pg.set_content(sorgente(src)); pg.wait_for_timeout(300); pg.screenshot(path=str(png)); b.close()


def generate(cartella, tmp):
    from elementi import da_html
    c = Path(cartella); out = []; usati = set()
    if not c.is_dir(): errore(f"la cartella delle pagine generate {c} non esiste.")
    tutti = sorted(list(c.rglob("*.html")) + list(c.rglob("*.svg")))
    # se in una cartella c'e' pagina.html/svg, conta solo quella (le altre sono bozze/copie dell'agente)
    tutti = [s for s in tutti if s.stem == "pagina" or not any(x.stem == "pagina" for x in tutti if x.parent == s.parent)]
    for src in tutti:
        png = src.with_suffix(".png")  # pagina.html -> pagina.png accanto, se c'e'
        if not png.exists(): png = tmp / f"gen_{len(out)}.png"; rendi(src, png)
        usati.add(png.resolve()); out.append((str(src.relative_to(c)), png, da_html([("x", src)])["x"]))
    for png in sorted(c.rglob("*.png")):
        if png.resolve() not in usati and png.name != "prof.png": out.append((str(png.relative_to(c)), apri_png(png), None))
    if not out: errore(f"in {c} non ci sono pagine generate (.html, .svg o .png). Mettici almeno 3 pagine fatte da un'AI.")
    if len(out) < 3: print(f"  AVVISO: solo {len(out)} pagine generate in {c}: i numeri valgono poco, meglio almeno 3.", flush=True)
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
        frase = FRASE[k](lo, hi, med) if k in FRASE and conv > 0 else None
        if hi == 0 and k in ZERO: frase = ZERO[k]  # appunti senza colore: niente frasi "su circa il 0-0% della pagina"
        righe.append({"k": k, "nome": nome, "lo": lo, "hi": hi, "med": med, "gen_med": float(np.median(g)), "fuori": fuori, "rob": rob, "conv": conv,
                      "eff": e, "punteggio": punt, "frase": frase})
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
    a = ap.parse_args()
    for d in filter(None, (a.generate, a.efficace_senza, a.efficace_con)):  # controlli prima di misurare: errori subito, non dopo un minuto
        if not Path(d).is_dir(): errore(f"la cartella {d} non esiste.")
        if not any(f.suffix.lower() in (".html", ".svg", ".png") for f in Path(d).rglob("*")):
            errore(f"in {d} non ci sono pagine generate (.html, .svg o .png). Mettici almeno 3 pagine fatte da un'AI.")
    for f in map(Path, a.suoi):
        if not f.is_file(): errore(f"{f} non esiste.")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="numeri_"))
    print("misuro i tuoi schemi...", flush=True); ps = pagine_suoi(a.suoi, tmp); suoi = togli_vuote(misura_tutto(ps, None), ps)
    print("misuro le generate...", flush=True); pg = generate(a.generate, tmp); gen = misura_tutto(pg, a.prof_parole)
    for x, (_, _, e) in zip(gen, pg):
        if senza_niente(x, e): print(f"  AVVISO: generata {x['pagina']}: niente testo ne' colore (pagina rotta o bianca?).", flush=True)
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
