"""Collega ogni pagina dei TUOI schemi alla pagina del prof piu' simile. Solo codice, niente AI.
Riusa il codice gia' nel repo:
  - annotatore/prepara.py: pagine_prof() + migliori()  -> parole rare in comune pesate IDF (pagine con testo)
  - 3_misura_stile_dai_numeri/allinea_auto.py: frasi_prof() + blocchi_miei()  e  allinea.py: parole()
        -> per ogni coppia, quante frasi del prof ritrovi nel tuo schema (al posto di Gemini, solo sovrapposizione di parole)
  - 3_misura_stile_dai_numeri/trova_differenze.py  -> lanciato alla fine con --prof-parole preso dalle pagine del prof collegate
Nuovo qui solo il ripiego VISIVO per pagine senza testo (PNG/scansioni): hash percettivo (dHash) + istogramma dei grigi.
Opzione --gemini (UNICA parte con AI, solo per le pagine senza testo): Gemini guarda lo schema e le pagine del prof
(fogli di miniature numerate -> 3 finaliste a piena risoluzione -> sceglie). Chiave da GEMINI_API_KEY / GEMINI_KEY
(variabile d'ambiente o segreto Colab GEMINI_KEY), mai scritta su file.
Uso: python collega_deterministico.py --schemi miei.pdf [pag.png ...] --prof prof.pdf [prof2.pdf pag.png ...] [--out dir] [--generate cartella_AI] [--gemini]
Esce: <out>/collegamenti.json e la tabella schema -> prof stampata."""
import argparse, json, os, statistics, subprocess, sys, tempfile
from pathlib import Path
import fitz
from PIL import Image

QUI = Path(__file__).resolve().parent; NUM = QUI.parent / "3_misura_stile_dai_numeri"
sys.path[:0] = [str(QUI / "annotatore"), str(NUM)]
from prepara import pagine_prof, migliori, par
_vuota = tempfile.mkdtemp(); Path(_vuota, "materiali.json").write_text("{}", encoding="utf-8")
os.environ.setdefault("ANNOTATORE_DIR", _vuota)  # allinea_auto legge materiali.json all'import: qui non serve
from allinea_auto import frasi_prof, blocchi_miei
from allinea import parole

from trova_differenze import errore, apri_pdf, apri_png
PDF = {".pdf"}; IMG = {".png", ".jpg", ".jpeg", ".webp"}


def pagine(files, chi="schemi"):
    """file -> [(nome, file, pagina 1-based o None, testo, immagine piccola in grigi)]; file sbagliati -> messaggio chiaro e exit 1"""
    out = []
    for f in map(str, files):
        if Path(f).suffix.lower() in PDF:
            for i, p in enumerate(apri_pdf(Path(f))):
                pix = p.get_pixmap(dpi=30, colorspace=fitz.csGRAY)
                out.append((f"{Path(f).name} p.{i + 1}", f, i + 1, p.get_text(), Image.frombytes("L", (pix.width, pix.height), pix.samples)))
        else:  # apri_png: errore chiaro per .docx, file vuoti, immagini rovinate
            out.append((Path(apri_png(Path(f))).name, f, None, "", Image.open(f).convert("L")))
    if not out: errore(f"--{chi}: nessuna pagina da leggere.")
    return out


def bianca(img):
    """pagina quasi uniforme (bianca o vuota): la vista la collega comunque con punteggio alto"""
    from PIL import ImageStat
    return ImageStat.Stat(img).stddev[0] < 4


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


def foto(p, lato):
    """pagina a colori, lato lungo ~= lato pixel (per Gemini)"""
    if p[2] is None:
        im = Image.open(p[1]).convert("RGB"); im.thumbnail((lato, lato)); return im
    pg = fitz.open(p[1])[p[2] - 1]; z = lato / max(pg.rect.width, pg.rect.height)
    pix = pg.get_pixmap(matrix=fitz.Matrix(z, z)); return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def fogli(pp, idx, col=4, rig=4, cella=(400, 300)):
    """miniature numerate (numero = posizione in pp) in fogli col x rig"""
    from PIL import ImageDraw
    out = []
    for s in range(0, len(idx), col * rig):
        f = Image.new("RGB", (col * cella[0], rig * cella[1]), "white"); d = ImageDraw.Draw(f)
        for j, k in enumerate(idx[s:s + col * rig]):
            x, y = j % col * cella[0], j // col * cella[1]; im = foto(pp[k], cella[0] - 10); im.thumbnail((cella[0] - 10, cella[1] - 30))
            f.paste(im, (x + 5, y + 28)); d.rectangle([x, y, x + cella[0] - 1, y + cella[1] - 1], outline="gray")
            d.rectangle([x, y, x + 70, y + 26], fill="black"); d.text((x + 6, y + 4), str(k), fill="white", font_size=20)
        out.append(f)
    return out


class Gemini:
    """2 chiamate per schema: 1) fogli di miniature -> 3 numeri; 2) le 3 a piena risoluzione -> 1 numero (o nessuna)."""
    def __init__(self, chiave, modello="gemini-flash-latest"):
        from google import genai
        self.c, self.m, self.chiamate, self.cache = genai.Client(api_key=chiave), modello, 0, None

    def _chiedi(self, parti):
        import time
        from google.genai import types
        for t in range(5):
            try:
                self.chiamate += 1
                r = self.c.models.generate_content(model=self.m, contents=parti, config=types.GenerateContentConfig(response_mime_type="application/json"))
                return json.loads(r.text)
            except Exception as e:  # 429/503: aspetta e riprova
                print("  gemini riprovo:", str(e)[:80], flush=True); time.sleep(20 * (t + 1))
        return {}

    def scegli(self, schema, pp, idx):
        if self.cache is None or self.cache[0] != idx: self.cache = (idx, fogli(pp, idx))
        fin = list(idx) if len(idx) <= 5 else self._chiedi(
            [foto(schema, 1600), *self.cache[1], "La prima immagine e' uno schema di studio fatto da uno studente. Le altre sono fogli di "
             "miniature delle pagine del materiale del docente, ognuna con il suo numero in un riquadro nero. Quali pagine del docente "
             "sono la fonte dello schema (stesso argomento e stessi contenuti specifici, non solo stessa materia)? "
             'Rispondi solo JSON: {"migliori": [n1, n2, n3]} dalla piu probabile.']).get("migliori", [])[:3]
        fin = [k for k in fin if isinstance(k, int) and 0 <= k < len(pp)]
        if not fin: return None, ""
        r = self._chiedi([foto(schema, 1600), *sum(([f"Pagina {k}:", foto(pp[k], 1600)] for k in fin), []),
                          "La prima immagine e' uno schema di studio fatto da uno studente; poi alcune pagine del materiale del docente. "
                          "Quale pagina e' la fonte dello schema (stessi contenuti specifici)? Se nessuna, null. "
                          'Rispondi solo JSON: {"scelta": numero o null, "perche": "una frase"}'])
        k = r.get("scelta")
        if isinstance(k, int) and 0 <= k < len(pp): return k, r.get("perche", "")
        # test 09/10: se la 2a chiamata dice "nessuna", la 1a finalista era giusta (A_p6); con top<=5 resta None
        return (fin[0] if len(idx) > 5 else None), "prima finalista (la 2a chiamata non ha scelto)"


def collega(schemi, prof, soglia=.8, gemini=None, top=0):
    mie, pp = pagine(schemi, "schemi"), pagine(prof, "prof")
    if not any(x[3].strip() for x in pp):
        print("  AVVISO: le pagine del prof non hanno testo (scansione o immagini): collego solo a vista, poco affidabile. "
              "Controlla a occhio o usa --gemini.", flush=True)
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
            if gemini:  # top=0: tutte le pagine del prof; top=N: solo le N piu' simili alla vista
                idx = sorted(k for _, k in sorted(((simile_vista(im, b), k) for k, b in enumerate(imp)), reverse=True)[:top]) if top else list(range(len(pp)))
                g, perche = gemini.scegli(m, pp, idx)
                if g is not None: k, pun, metodo, altre = g, 0, "gemini", [perche]
        p = pp[k]
        # affidabile: solo testo (giuste 7/7 nel test UX) o gemini; la vista sbaglia spesso e da' 0,97 anche a una pagina bianca
        avviso = "schema bianco/vuoto" if bianca(m[4]) else ("" if metodo != "vista" else "controlla a occhio o usa --gemini")
        ris.append({"schema": m[0], "prof": p[0], "prof_file": Path(p[1]).name, "prof_pagina": p[2], "metodo": metodo,
                    "punteggio": round(pun, 2), "altre": altre, "prof_parole": len(p[3].split()) if p[3] else None,
                    "frasi_prof_riprese": frasi_riprese(m, p), "affidabile": not avviso, "avviso": avviso})
    return ris


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schemi", nargs="+", required=True); ap.add_argument("--prof", nargs="+", required=True)
    ap.add_argument("--out", default="risultati_collega_det"); ap.add_argument("--generate", help="pagine AI: se c'e' lancia trova_differenze.py")
    ap.add_argument("--gemini", action="store_true", help="pagine senza testo: sceglie Gemini (chiave GEMINI_API_KEY o GEMINI_KEY)")
    ap.add_argument("--gemini-top", type=int, default=0, help="0 = Gemini vede tutte le pagine del prof (fogli di miniature, poi 3 finaliste); N = solo le N piu simili per il codice")
    a = ap.parse_args()
    for f in [*a.schemi, *a.prof]:
        if not Path(f).is_file(): errore(f"{f} non esiste.")
    if a.generate and not Path(a.generate).is_dir(): errore(f"--generate: la cartella {a.generate} non esiste.")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    gem = None
    if a.gemini:
        chiave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")
        if not chiave: sys.exit("--gemini: manca la chiave (variabile GEMINI_API_KEY o GEMINI_KEY)")
        gem = Gemini(chiave)
    ris = collega(a.schemi, a.prof, gemini=gem, top=a.gemini_top)
    if gem: print("chiamate Gemini:", gem.chiamate)
    (out / "collegamenti.json").write_text(json.dumps(ris, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'schema':42} {'pagina del prof':52} metodo punt. frasi_prof_riprese affidabile")
    for r in ris:
        prof = f"{r['prof_file'][:44]} p.{r['prof_pagina']}" if r["prof_pagina"] else r["prof_file"][:52]
        print(f"{r['schema'][:42]:42} {prof:52} {r['metodo']:6} {r['punteggio']:5} {r['frasi_prof_riprese'] or '-':18} {'si' if r['affidabile'] else 'NO: ' + r['avviso']}", flush=True)
    if a.generate:
        np_ = [r["prof_parole"] for r in ris if r["prof_parole"]]
        cmd = [sys.executable, "-X", "utf8", str(NUM / "trova_differenze.py"), "--suoi", *map(str, a.schemi), "--generate", a.generate,
               "--out", str(out / "differenze")] + (["--prof-parole", str(int(statistics.median(np_)))] if np_ else [])
        print("\nlancio trova_differenze.py (--prof-parole = mediana delle pagine del prof collegate)"); subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
