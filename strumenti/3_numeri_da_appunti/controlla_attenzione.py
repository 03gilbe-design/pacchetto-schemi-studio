"""41: controllo automatico dell'attenzione su un PNG generato. Per un agente: misura -> OK/FUORI -> se FUORI rigenera.
Range = min-max dei SUOI 6 schemi di Architettura, letti da misure.json (rifallo con misura.py se cambiano le sue pagine).
Uso: C:\\Python310\\python.exe -X utf8 controlla_attenzione.py pagina.png [altre.png ...] [--rif rif_suoi.json]
Exit code: 0 tutto OK, 1 almeno un numero FUORI."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from misura import metriche
D = Path(__file__).resolve().parent
ARG = sys.argv[1:]; RIF = D / "misure.json"  # --rif altro.json = range da altri suoi appunti (fatto con misura.py --suoi)
if "--rif" in ARG: i = ARG.index("--rif"); RIF = Path(ARG[i + 1]); ARG = ARG[:i] + ARG[i + 2:]
SUOI = json.loads(RIF.read_text(encoding="utf-8"))["SUOI (6 pagine Architettura)"]
TRE = {"colore_forte_%": ("colore forte (% pagina)", "troppo poco colore forte: fascia titolo piena #FF644B o 1-2 evidenziazioni", "troppo colore forte: togli #FF644B da box/fondi, usa pastello"),
       "zone_forti": ("zone di colore forte", "nessuna zona forte: metti la fascia titolo #FF644B", "troppe zone forti: tieni #FF644B solo su titolo + 1-2 elementi, il resto in pastello"),
       "tinta_dominante_%": ("tinta principale (% del colore)", "troppe tinte: riduci azzurri/verdi/gialli, resta nella famiglia corallo-pesca", "-")}
RANGE = {k: (min(x[k] for x in SUOI), max(x[k] for x in SUOI)) for k in TRE}


def controlla(png):
    m = metriche(png); esiti = {}
    for k, (nome, basso, alto) in TRE.items():
        lo, hi = RANGE[k]; v = m[k]
        esiti[k] = {"nome": nome, "valore": v, "range_suo": [lo, hi], "ok": bool(lo <= v <= hi),
                    "consiglio": "" if lo <= v <= hi else (basso if v < lo else alto)}
    return esiti


if __name__ == "__main__":
    tutti_ok = True
    for f in ARG:
        e = controlla(f); print(f)
        for x in e.values():
            print(f"  {'OK   ' if x['ok'] else 'FUORI'} {x['nome']:32} {x['valore']:>6g}   suo {x['range_suo'][0]:g}-{x['range_suo'][1]:g}   {x['consiglio']}")
            tutti_ok &= x["ok"]
    sys.exit(0 if tutti_ok else 1)
