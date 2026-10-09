"""Collega ogni pagina dei TUOI schemi alla pagina del prof piu' simile. Solo codice, niente AI.
Riusa il codice gia' nel repo:
  - annotatore/prepara.py: pagine_prof() + migliori()  -> parole rare in comune pesate IDF (pagine con testo)
  - 3_numeri_da_appunti/allinea_auto.py: frasi_prof() + blocchi_miei()  e  allinea.py: parole()
        -> per ogni coppia, quante frasi del prof ritrovi nel tuo schema (al posto di Gemini, solo sovrapposizione di parole)
  - 3_numeri_da_appunti/trova_differenze.py  -> lanciato alla fine con --prof-parole preso dalle pagine del prof collegate
Nuovo qui solo il ripiego VISIVO per pagine senza testo (PNG/scansioni): hash percettivo (dHash) + istogramma dei grigi.
Uso: python collega_deterministico.py --schemi miei.pdf [pag.png ...] --prof prof.pdf [prof2.pdf pag.png ...] [--out dir] [--generate cartella_AI]
Esce: <out>/collegamenti.json e la tabella schema -> prof stampata."""
import argparse, json, os, statistics, subprocess, sys, tempfile
from pathlib import Path
import fitz
from PIL import Image

QUI = Path(__file__).resolve().parent; NUM = QUI.parent / "3_numeri_da_appunti"
sys.path[:0] = [str(QUI / "annotatore"), str(NUM)]
from prepara import pagine_prof, migliori, par
_vuota = tempfile.mkdtemp(); Path(_vuota, "materiali.json").write_text("{}", encoding="utf-8")
os.environ.setdefault("ANNOTATORE_DIR", _vuota)  # allinea_auto legge materiali.json all'import: qui non serve
from allinea_auto import frasi_prof, blocchi_miei
from allinea import parole

PDF = {".pdf"}; IMG = {".png", ".jpg", ".jpeg", ".webp"}


def pagine(files):
    """file -> [(nome, file, pagina 1-based o None, testo, immagine piccola in grigi)]"""
    out = []
    for f in map(str, files):
        if Path(f).suffix.lower() in PDF:
            for i, p in enumerate(fitz.open(f)):
                pix = p.get_pixmap(dpi=30, colorspace=fitz.csGRAY)
                out.append((f"{Path(f).name} p.{i + 1}", f, i + 1, p.get_text(), Image.frombytes("L", (pix.width, pix.height), pix.samples)))
        elif Path(f).suffix.lower() in IMG:
            out.append((Path(f).name, f, None, "", Image.open(f).convert("L")))
    return out


def impronta(img):
    """dHash 16x16 (forma) + istogramma a 16 livelli (quanto e' scura/colorata)"""
    a = list(img.resize((17, 16)).getdata())
    h = [a[r * 17 + c] > a[r * 17 + c + 1] for r in range(16) for c in range(16)]
    st = img.resize((128, 128)).histogram(); st = [sum(st[i:i + 16]) / (128 * 128) for i in range(0, 256, 16)]
    return h, st


def simile_vista(a, b):
    ham = sum(x != y for x, y in zip(a[0], b[0])) / len(a[0])
    return round(.5 * (1 - ham) + .5 * sum(min(x, y) for x, y in zip(a[1], b[1])), 3)


def frasi_riprese(mio, prof):
    """allinea_auto: frasi del prof e blocchi miei; una frase e' 'ripresa' se >= meta' delle sue parole sono nel mio schema."""
    if mio[2] is None or prof[2] is None: return None
    fr = frasi_prof(fitz.open(prof[1])[prof[2] - 1])
    mie = set().union(*[parole(b["testo"]) for b in blocchi_miei(fitz.open(mio[1])[mio[2] - 1])] or [set()])
    ok = sum(1 for f in fr if parole(f["testo"]) and len(parole(f["testo"]) & mie) >= .5 * len(parole(f["testo"])))
    return f"{ok}/{len(fr)}"


def collega(schemi, prof, soglia=.8):
    mie, pp = pagine(schemi), pagine(prof)
    pag_prof, idf = pagine_prof([f for f in map(str, prof) if Path(f).suffix.lower() in PDF])
    chiave = {(f, n): k for k, (_, f, n, _, _) in enumerate(pp)}
    imp = [impronta(x[4]) for x in pp]; ris = []
    for m in mie:
        ws = set(par(m[3])); top = migliori(ws, pag_prof, idf) if ws and pag_prof else []
        if top and top[0][1] >= soglia:
            (f, n, _), pun = top[0]; k = chiave[(f, n)]; metodo = "testo"; altre = [x[1] for x, _ in top[1:]]
        else:  # ripiego visivo: nessun testo (PNG/scansione) o parole in comune troppo poche
            im = impronta(m[4]); sc = sorted(((simile_vista(im, b), k) for k, b in enumerate(imp)), reverse=True)[:3]
            pun, k = sc[0]; metodo = "vista"; altre = [pp[j][0] for _, j in sc[1:]]
        p = pp[k]
        ris.append({"schema": m[0], "prof": p[0], "prof_file": Path(p[1]).name, "prof_pagina": p[2], "metodo": metodo,
                    "punteggio": round(pun, 2), "altre": altre, "prof_parole": len(p[3].split()) if p[3] else None,
                    "frasi_prof_riprese": frasi_riprese(m, p)})
    return ris


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schemi", nargs="+", required=True); ap.add_argument("--prof", nargs="+", required=True)
    ap.add_argument("--out", default="risultati_collega_det"); ap.add_argument("--generate", help="pagine AI: se c'e' lancia trova_differenze.py")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ris = collega(a.schemi, a.prof)
    (out / "collegamenti.json").write_text(json.dumps(ris, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'schema':42} {'pagina del prof':52} metodo punt. frasi_prof_riprese")
    for r in ris:
        prof = f"{r['prof_file'][:44]} p.{r['prof_pagina']}" if r["prof_pagina"] else r["prof_file"][:52]
        print(f"{r['schema'][:42]:42} {prof:52} {r['metodo']:6} {r['punteggio']:5} {r['frasi_prof_riprese'] or '-'}", flush=True)
    if a.generate:
        np_ = [r["prof_parole"] for r in ris if r["prof_parole"]]
        cmd = [sys.executable, "-X", "utf8", str(NUM / "trova_differenze.py"), "--suoi", *map(str, a.schemi), "--generate", a.generate,
               "--out", str(out / "differenze")] + (["--prof-parole", str(int(statistics.median(np_)))] if np_ else [])
        print("\nlancio trova_differenze.py (--prof-parole = mediana delle pagine del prof collegate)"); subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
