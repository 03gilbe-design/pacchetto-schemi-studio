"""08/10 notte Gilberto: test Groq per vedere se COLLEGA bene il PDF del prof alle pagine del MIO schema di Architettura.
Verita' di riferimento: RECUPERO_FONTI_2026-09-16/dettaglio_tecnico__fonti_pagina_per_pagina.md (confronto parola per parola del 16/09).
Passi (deterministici tranne 2 e 4):
 1 codice: testo di ogni pagina del prof (FONTE_1 slide 21p, FONTE_2 slide 131p, FONTE_3 dispensa 162p)
 2 Groq qwen (vede l'immagine): descrive la mia pagina -> argomento + 15 parole chiave
 3 codice: le 10 pagine del prof piu' vicine alle parole chiave (BM25)
 4 Groq: sceglie fra le 10 (o "nessuna") e dice perche'
 5 codice: confronto con la verita' (giusto se stessa fonte e pagina +-1)
Uscita: ESPERIMENTI/33_COLLEGA_GROQ/{risultati.json, RISULTATI.md, p<N>/...}"""
import json
import math
import re
import time
from collections import Counter
from pathlib import Path
import fitz
from groq import chiama_groq

import os
Q = Path(__file__).parent; O = Q / "risultati_collega"; O.mkdir(parents=True, exist_ok=True)
MOD = "qwen/qwen3.8-27b"; PAUSA = 40
SCHEMA = Path(os.environ["SCHEMA_PDF"])  # PDF dei tuoi schemi (una pagina = una pagina di appunti)
RF = Path(os.environ["FONTI_DIR"])       # cartella con i PDF del prof (sotto FONTI) e dettaglio_tecnico__fonti_pagina_per_pagina.md (verita')
FONTI = {"F1_slide21": RF / "1_Architettura__fonti_originali_degli_schemi" / "FONTE_1_piu_forte__slide_Architettura_2semestre_21pag__cache_a_pag_2-3-16-20.pdf",
         "F2_slide131": RF / "1_Architettura__fonti_originali_degli_schemi" / "FONTE_2__slide_Architettura_secondo_semestre_131pag__cache_a_pag_2-9-10-14.pdf",
         "F3_dispensa": RF / "1_Architettura__fonti_originali_degli_schemi" / "FONTE_3__dispensa_Architettura_2021-22_162pag__frase_associare_blocco_a_pag_90-92-93-100.pdf"}
NOMI_VERITA = {"2semestre": "F1_slide21", "SECONDO-SEMESTRE": "F2_slide131", "2021_2022": "F3_dispensa"}  # nome file nel rapporto -> fonte


def verita():
    """mia pagina -> (fonte, pagina prof, copia%) dal rapporto del 16/09 (la riga di fonte prof col punteggio piu' alto)."""
    v, cur = {}, None
    for l in (RF / "dettaglio_tecnico__fonti_pagina_per_pagina.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"### ARCH p(\d+) ", l)
        if m: cur = int(m.group(1)); continue
        m = re.match(r"- copia (\d+)% .*?`([^`]+)` \[p(\d+)\]", l)
        if cur and m:
            f = next((k for n, k in NOMI_VERITA.items() if n in m.group(2)), None)
            if f and (cur not in v or int(m.group(1)) > v[cur][2]): v[cur] = (f, int(m.group(3)), int(m.group(1)))
    return v


parole = lambda s: [w for w in re.findall(r"[a-zÃ -Ã¹]{4,}", s.lower())]
PAG = [(f, i + 1, t) for f, p in FONTI.items() for i, t in enumerate(pg.get_text() for pg in fitz.open(p))]
DOC = [Counter(parole(t)) for _, _, t in PAG]; N = len(DOC); AVG = sum(sum(c.values()) for c in DOC) / N
DF = Counter(w for c in DOC for w in c)


def bm25(q, k=10):
    sc = []
    for i, c in enumerate(DOC):
        L = sum(c.values()); s = 0
        for w in q:
            if w in c: s += math.log(1 + (N - DF[w] + .5) / (DF[w] + .5)) * c[w] * 2.2 / (c[w] + 1.2 * (.25 + .75 * L / AVG))
        sc.append((s, i))
    return [i for s, i in sorted(sc, reverse=True)[:k]]


V = verita(); RIS = []
for n, pg in enumerate(fitz.open(SCHEMA), 1):
    d = O / f"p{n:02d}"; d.mkdir(exist_ok=True); img = d / "mia_pagina.png"; pg.get_pixmap(dpi=80).save(img)
    f_ris = d / "esito.json"
    if f_ris.exists(): RIS.append(json.loads(f_ris.read_text(encoding="utf-8"))); continue
    desc = chiama_groq("Questa e' una pagina di appunti di uno studente di Architettura degli elaboratori. Rispondi SOLO con JSON: "
                       '{"argomento": "...", "parole_chiave": ["15 parole tecniche ITALIANE presenti o implicite nella pagina"]}', img, MOD, 600)
    (d / "1_descrizione.txt").write_text(desc, encoding="utf-8"); time.sleep(PAUSA)
    q = parole(desc); cand = bm25(q)
    elenco = "\n".join(f"[{j}] {PAG[i][0]} pag {PAG[i][1]}: " + re.sub(r"\s+", " ", PAG[i][2])[:450] for j, i in enumerate(cand))
    scelta = chiama_groq("Pagina di appunti dello studente (immagine). Quale di queste pagine del professore e' la FONTE da cui lo studente ha preso "
                         "l'argomento? Rispondi SOLO con JSON {\"scelta\": numero tra 0 e 9 oppure -1 se nessuna, \"perche\": \"una frase\"}\n\n" + elenco, img, MOD, 400)
    (d / "2_candidati.txt").write_text(elenco, encoding="utf-8"); (d / "3_scelta.txt").write_text(scelta, encoding="utf-8"); time.sleep(PAUSA)
    m = re.search(r'"scelta"\s*:\s*(-?\d+)', scelta); k = int(m.group(1)) if m else None
    sc = (PAG[cand[k]][0], PAG[cand[k]][1]) if k is not None and 0 <= k < len(cand) else None
    vv = V.get(n)
    r = {"mia_pagina": n, "verita": vv, "groq": sc, "bm25_top1": (PAG[cand[0]][0], PAG[cand[0]][1]),
         "verita_nei_10": bool(vv and any(PAG[i][0] == vv[0] and abs(PAG[i][1] - vv[1]) <= 1 for i in cand)),
         "giusto": bool(vv and sc and sc[0] == vv[0] and abs(sc[1] - vv[1]) <= 1)}
    f_ris.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8"); RIS.append(r); print(r, flush=True)
con = [r for r in RIS if r["verita"]]
righe = [f"| {r['mia_pagina']} | {r['verita']} | {r['groq']} | {'SI' if r['giusto'] else 'no'} | {'si' if r['verita_nei_10'] else 'no'} |" for r in RIS]
(O / "risultati.json").write_text(json.dumps(RIS, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
(O / "RISULTATI.md").write_text("# Groq collega mie pagine Architettura -> PDF prof\n\n"
                               f"Giuste: {sum(r['giusto'] for r in con)}/{len(con)} (pagine con verita' nota). Verita' tra i 10 candidati: {sum(r['verita_nei_10'] for r in con)}/{len(con)}.\n\n"
                               "| mia p | verita' (fonte, pag, copia%) | Groq | giusto | verita' nei 10 |\n|---|---|---|---|---|\n" + "\n".join(righe) + "\n", encoding="utf-8")
print("FINITO", sum(r["giusto"] for r in con), "/", len(con), flush=True)
