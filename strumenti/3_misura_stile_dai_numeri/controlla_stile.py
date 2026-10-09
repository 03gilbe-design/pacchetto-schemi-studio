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
    "tinta_dominante_%": ("tinta principale (% del colore)", "png", "troppe tinte: riduci azzurri/verdi/gialli, resta nella famiglia corallo-pesca", "-"),
    "vuoto_terzo_basso_%": ("vuoto nel terzo basso (%)", "png", "fondo troppo pieno: lascia respirare l'ultimo terzo", "fondo vuoto: allarga il disegno principale fino in fondo alla pagina"),
    "blocco_piu_grande_%": ("blocco piu' grande (% contenuto)", "png", "contenuto troppo frammentato: unisci i pezzi in 2-3 gruppi", "un solo blocco enorme: separa le parti con spazio (almeno 2% della larghezza)"),
    "corpo_medio_o_grande_%": ("testo a corpo >= 14 px (%)", "src", "testo troppo piccolo: corpo del testo corrente 16-19 px su 794", "-"),
    "testo_su_fondo_pagina_%": ("testo libero sul foglio (%)", "src", "troppo testo dentro box colorati/bianchi: scrivi sul foglio", "-"),
    "testo_evidenziato_%": ("testo evidenziato (%)", "src", "-", "troppe pillole/caselle colorate dietro il testo: tienile per poche etichette"),
    "parole_in_righe_lunghe_%": ("parole in frasi lunghe (%)", "src", "solo etichette: tieni frasi intere (>= 5 parole) accanto al disegno", "-"),
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
    a = sys.argv[1:]; src = prof = None
    if "--rif" in a:  # range di altri suoi appunti: numeri.json scritto da trova_differenze.py
        i = a.index("--rif"); RANGE.update({k: tuple(v) for k, v in json.loads(Path(a[i + 1]).read_text(encoding="utf-8"))["range"].items() if k in TENUTE}); a = a[:i] + a[i + 2:]
    if "--sorgente" in a: i = a.index("--sorgente"); src = a[i + 1]; a = a[:i] + a[i + 2:]
    if "--prof-parole" in a: i = a.index("--prof-parole"); prof = int(a[i + 1]); a = a[:i] + a[i + 2:]
    tutti_ok = True
    for f in a:
        e = controlla(f, src, prof); print(f)
        for x in e.values():
            print(f"  {'OK   ' if x['ok'] else 'FUORI'} {x['nome']:34} {x['valore']:>6g}   suo {x['range_suo'][0]:g}-{x['range_suo'][1]:g}   {x['consiglio']}")
            tutti_ok &= x["ok"]
    sys.exit(0 if tutti_ok else 1)
