"""41: controllo automatico dello STILE (attenzione + numeri in piu') su una pagina generata. Per un agente: OK/FUORI -> rigenera.
Range = min-max dei SUOI 6 schemi di Architettura (misure.json + misure2.json). Solo codice, niente modelli/OCR.
Dal PNG: colore forte, zone forti, tinta principale, vuoto nel terzo basso, blocco piu' grande.
Dal sorgente (--sorgente pagina.html|pagina.svg): corpo del testo, testo libero sul foglio, testo evidenziato, parole/prof (con --prof-parole N).
Uso: C:\\Python310\\python.exe -X utf8 controlla_stile.py pagina.png [--sorgente pagina.html] [--prof-parole 385] [--rif numeri.json]
Exit code: 0 tutto OK, 1 almeno un numero FUORI."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D))
from misura import metriche as attenzione
from misura2 import immagine

_leggi = lambda f, k: json.loads((D / f).read_text(encoding="utf-8"))[k] if (D / f).exists() else [{}]
S1 = _leggi("misure.json", "SUOI (6 pagine Architettura)")  # range di default = Architettura; con --rif si usano altri appunti
S2 = _leggi("misure2.json", "SUOI")
# chiave: (nome, sorgente dati, consiglio se basso, consiglio se alto)
TENUTE = {
    "colore_forte_%": ("colore forte (% pagina)", "png", "troppo poco corallo: fascia titolo piena #FF644B o 1-2 evidenziazioni", "troppo corallo: toglilo da riquadri/fondi, usa pastello"),
    "zone_forti": ("zone di colore forte", "png", "nessuna zona forte: metti la fascia titolo corallo", "troppe zone forti: corallo solo su titolo + 1-2 elementi"),
    "tinta_dominante_%": ("tinta principale (% del colore)", "png", "troppe tinte: riduci azzurri/verdi/gialli, resta nella famiglia corallo-pesca", "una tinta sola: va bene, al massimo un tocco di un'altra"),
    "vuoto_terzo_basso_%": ("vuoto nel terzo basso (%)", "png", "fondo troppo pieno: lascia respirare l'ultimo terzo", "fondo vuoto: allarga il disegno principale fino in fondo alla pagina"),
    "blocco_piu_grande_%": ("blocco piu' grande (% contenuto)", "png", "contenuto troppo frammentato: unisci i pezzi in 2-3 gruppi", "un solo blocco enorme: separa le parti con spazio (almeno 2% della larghezza)"),
    "corpo_medio_o_grande_%": ("testo a corpo >= 14 px (%)", "src", "testo troppo piccolo: corpo del testo corrente 16-19 px su 794", "testo tutto grande: titoli piu' grandi, testo corrente 16-19 px su 794"),
    "testo_su_fondo_pagina_%": ("testo libero sul foglio (%)", "src", "troppo testo dentro box colorati/bianchi: scrivi sul foglio", "tutto il testo nudo sul foglio: metti 2-3 etichette chiave in una pillola o casella"),
    "testo_evidenziato_%": ("testo evidenziato (%)", "src", "quasi niente evidenziato: metti 2-3 parole chiave in una pillola corallo/pesca", "troppe pillole/caselle colorate dietro il testo: tienile per poche etichette"),
    "parole_in_righe_lunghe_%": ("parole in frasi lunghe (%)", "src", "solo etichette: tieni frasi intere (>= 5 parole) accanto al disegno", "troppe frasi lunghe: trasforma qualcuna in etichetta accanto al disegno"),
    "parole_su_prof_%": ("parole / parole del prof (%)", "src", "testo troppo compresso: tieni le frasi del prof che spiegano il perche'", "troppo testo: comprimi in etichette"),
}
SUOI = {k: [x[k] for x in (S1 if k in S1[0] else S2) if k in x] for k in TENUTE}
RANGE = {k: (min(v), max(v)) for k, v in SUOI.items() if v}


def dal_sorgente(f, prof_parole=None):
    from elementi import da_html
    from combinazioni import per_pagina
    import combinazioni
    if prof_parole: combinazioni.PROF_PAROLE["p03"] = prof_parole
    else: combinazioni.PROF_PAROLE.pop("p03", None)
    return per_pagina("generata", da_html([("generata", f)])["generata"])


def controlla(png, src=None, prof_parole=None):
    m = {**attenzione(png), **immagine(png)}
    if src: m.update(dal_sorgente(src, prof_parole))
    esiti = {}
    for k, (nome, _, basso, alto) in TENUTE.items():
        if k not in m or k not in RANGE: continue
        lo, hi = RANGE[k]; v = m[k]
        ok = bool(lo <= v <= hi)
        esiti[k] = {"nome": nome, "valore": v, "range_suo": [lo, hi], "ok": ok, "consiglio": "" if ok else (basso if v < lo else alto)}
    return esiti


if __name__ == "__main__":
    import argparse
    from trova_differenze import errore, apri_png
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", nargs="+", help="pagina generata in PNG (una o piu')")
    ap.add_argument("--sorgente", help="pagina.html o pagina.svg da cui viene il PNG (aggiunge i numeri sul testo)")
    ap.add_argument("--prof-parole", type=int, help="parole della pagina del docente")
    ap.add_argument("--rif", help="numeri.json scritto da trova_differenze.py (range di altri tuoi appunti)")
    a = ap.parse_args(); src, prof = a.sorgente, a.prof_parole
    if a.rif:  # range di altri suoi appunti: numeri.json scritto da trova_differenze.py
        try: RANGE.update({k: tuple(v) for k, v in json.loads(Path(a.rif).read_text(encoding="utf-8"))["range"].items() if k in TENUTE})
        except (OSError, ValueError, KeyError): errore(f"--rif {a.rif}: non e' un numeri.json di trova_differenze.py (o non esiste).")
    if src and not Path(src).is_file(): errore(f"--sorgente {src} non esiste.")
    for f in a.png:
        if f.lower().endswith(".pdf"): errore(f"{f}: serve il PNG della pagina generata, non un PDF (vedi --help).")
        apri_png(Path(f))
    tutti_ok = True
    for f in a.png:
        e = controlla(f, src, prof); print(f)
        for x in e.values():
            print(f"  {'OK   ' if x['ok'] else 'FUORI'} {x['nome']:34} {x['valore']:>6g}   suo {x['range_suo'][0]:g}-{x['range_suo'][1]:g}   {x['consiglio']}")
            tutti_ok &= x["ok"]
    sys.exit(0 if tutti_ok else 1)
