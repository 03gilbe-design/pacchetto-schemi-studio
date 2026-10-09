"""06/10 'quanto e' URLATA la pagina' (Gilberto: la sua e' un arlecchino, contrasti sparsi, soglia molto alta) -> numeri, senza AI.
colorfulness = Hasler-Susstrunk; saturi_% = pixel con saturazione e luminosita' alte; tinte = quante tinte diverse occupano >=1% della pagina;
macchie = quante zone separate di colore saturo (arlecchino); contrasto = deviazione standard della luminosita'.
Uso: C:\\Python310\\python.exe -X utf8 quanto_urla.py"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

E = Path(__file__).parent / "ESPERIMENTI"


def misura(f):
    im = Image.open(f).convert("RGB"); im.thumbnail((800, 800)); a = np.asarray(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; rg, yb = r - g, 0.5 * (r + g) - b
    colorf = np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean())
    hsv = np.asarray(im.convert("HSV")).astype(float); s, v, h = hsv[..., 1], hsv[..., 2], hsv[..., 0]
    saturo = (s > 90) & (v > 90)
    tinte = sum(1 for k in range(12) if (saturo & (h // 21.34 == k)).mean() >= 0.01)
    _, macchie = ndimage.label(ndimage.binary_opening(saturo, iterations=2))
    return {"colorfulness": round(colorf, 1), "saturi_%": round(100 * saturo.mean(), 1), "tinte": tinte, "macchie": int(macchie),
            "contrasto": round(np.asarray(im.convert("L")).astype(float).std(), 1)}


N1, ST, G7 = E / "4_NOTTE_genera_pagine_e_regole_dimenticate", E / "5_STILE_in_numeri", E / "7_REGOLE_GRANDI_rigenera"
fonti = {"TUA": [N1 / p / "gilberto.png" for p in ("p02", "p03", "p04", "p05", "p06", "p07")],
         "AI senza stile": sorted(N1.glob("p0*/pagina.png")), "AI carta di stile": sorted(ST.glob("p0*/pagina.png")),
         "Codex regole grandi": sorted(G7.glob("p0*/codex/pagina.png")), "Gemini regole grandi": sorted(G7.glob("p0*/gemini/pagina.png"))}
ris = {}
for nome, fs in fonti.items():
    m = [misura(f) for f in fs if f.exists()]
    ris[nome] = {k: round(float(np.mean([x[k] for x in m])), 1) for k in m[0]} | {"pagine": len(m)}
    print(f"{nome:22} " + "  ".join(f"{k}={v}" for k, v in ris[nome].items()))
(E / "quanto_urla.json").write_text(json.dumps(ris, ensure_ascii=False, indent=1), encoding="utf-8")
