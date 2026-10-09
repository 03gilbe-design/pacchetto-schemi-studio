"""09/10 esperimento 41 (Gilberto 07:10 "troppa differenza nell'uso dell'attenzione, che si puo' estrarre tramite numeri").
Metriche dell'attenzione sui PNG, solo codice. colore forte = sat() di 39_ZONE_GRIGIE_CODEX/analizza.py (corallo #FF644B conta).
Uso: C:\\Python310\\python.exe -X utf8 ESPERIMENTI\\41_ATTENZIONE_NUMERI\\misura.py"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
D = Path(__file__).resolve().parent; E = D.parent
W = 600  # ponytail: tutte le pagine portate a 600 px di larghezza, cosi' aree e zone sono confrontabili


def carica(f):
    im = Image.open(f).convert("RGB")
    return np.asarray(im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)).astype(float)


def forte(a):  # stessa formula di sat() in 39/analizza.py
    mx, mn = a.max(2), a.min(2)
    return ((mx - mn) / np.maximum(mx, 1) >= 0.55) & (mx >= 90)


def metriche(f):
    a = carica(f); mx, mn = a.max(2), a.min(2); ch = (mx - mn) / np.maximum(mx, 1)
    lum = a @ [0.299, 0.587, 0.114]
    F = forte(a); n = F.size; h = F.shape[0]
    # zone forti separate: componenti connesse (dopo chiusura 5x5 per unire lettere/tratti vicini) >= 0.1% pagina
    lab, k = ndimage.label(ndimage.binary_closing(F, np.ones((5, 5))))
    aree = np.bincount(lab.ravel())[1:] if k else np.array([])
    zone = int((aree >= 0.001 * n).sum())
    # tinte: pixel colorati (anche pastello: croma >= 0.15, non scuri) raggruppati in 12 spicchi di tinta da 30 gradi
    col = (ch >= 0.15) & (mx >= 90)
    r, g, b = (a[..., i][col] for i in range(3)); M, m = mx[col], mn[col]; d = np.maximum(M - m, 1e-6)
    hue = np.where(M == r, (g - b) / d % 6, np.where(M == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    cnt = np.bincount((hue // 30).astype(int) % 12, minlength=12)
    tinte = int((cnt >= 0.03 * max(cnt.sum(), 1)).sum())
    dom = round(100 * cnt.max() / max(cnt.sum(), 1), 1)
    # fondo = colore piu' frequente; tenue = non fondo, non scuro, non forte
    q = (a // 8).astype(int); key = q[..., 0] * 1024 + q[..., 1] * 32 + q[..., 2]
    fondo = np.bincount(key.ravel()).argmax()
    nonfondo = np.abs(a - a[key == fondo].mean(0)).max(2) > 18
    scuro = lum < 110
    tenue = nonfondo & ~scuro & ~F
    terzi = [F[i * h // 3:(i + 1) * h // 3].sum() for i in range(3)]
    tf = max(sum(terzi), 1)
    return {"colore_forte_%": round(100 * F.mean(), 1), "zone_forti": zone,
            "pastello_%": round(100 * (col & ~F).mean(), 1),
            "tinte": tinte, "tinta_dominante_%": dom,
            "scuro_%": round(100 * scuro.mean(), 1), "tenue_%": round(100 * tenue.mean(), 1),
            "scuro_su_tenue": round(scuro.mean() / max(tenue.mean(), 1e-6), 2),
            "forte_alto_%": round(100 * terzi[0] / tf), "forte_centro_%": round(100 * terzi[1] / tf), "forte_fondo_%": round(100 * terzi[2] / tf)}


def gruppi():
    N = E / "4_NOTTE_genera_pagine_e_regole_dimenticate"
    g = {"SUOI (6 pagine Architettura)": sorted(N.glob("p0*/gilberto.png"))}
    for c in ["SENZA", "CON_REGOLE", "CON_REGOLE_FIGURA"]:
        g[f"40 Claude {c}"] = sorted((E / "40_CLAUDE_ARCH_PACCHETTO" / "prove" / c).glob("r*/pagina.png"))
    for c in ["Z1_SENZA_NOT", "Z1_CON_NOT", "Z2_SENZA", "Z2_CON_REGOLE_GPT", "Z2_CON_PULITO"]:
        g[f"39 GPT {c}"] = sorted((E / "39_ZONE_GRIGIE_CODEX" / "ARCH_p03" / c).glob("r*/pagina.png"))
    nuove = sorted((D / "prove" / "SVG_CON_NUMERI").glob("r*/pagina.png"))
    if nuove: g["41 Claude SVG pacchetto+numeri"] = nuove
    return g


if __name__ == "__main__":
    if "--suoi" in sys.argv:  # appunti qualsiasi: misura.py --suoi a.png b.png ... --out rif.json (solo i suoi, niente generate)
        a = sys.argv[sys.argv.index("--suoi") + 1:]; out = D / "rif_suoi.json"
        if "--out" in a: out = Path(a[a.index("--out") + 1]); a = a[:a.index("--out")]
        pngs = [Path(x) for x in a]
        m = [{"file": str(p), **metriche(p)} for p in pngs]
        out.write_text(json.dumps({"SUOI (6 pagine Architettura)": m}, ensure_ascii=False, indent=1), encoding="utf-8")
        for k in ("colore_forte_%", "zone_forti", "tinta_dominante_%"):
            v = [x[k] for x in m]; print(f"{k:20} {min(v):g}-{max(v):g} (mediana {np.median(v):g})")
        sys.exit()
    tutto = {k: [{"file": str(p.relative_to(E)), **metriche(p)} for p in v] for k, v in gruppi().items()}
    (D / "misure.json").write_text(json.dumps(tutto, ensure_ascii=False, indent=1), encoding="utf-8")
    chiavi = [k for k in next(iter(tutto.values()))[0] if k != "file"]
    righe = ["| gruppo | n | " + " | ".join(chiavi) + " |", "|---|---|" + "---|" * len(chiavi)]
    for g, m in tutto.items():
        cel = []
        for c in chiavi:
            v = [x[c] for x in m]
            cel.append(f"{min(v):g}-{max(v):g} (med {np.median(v):g})")
        righe.append(f"| {g} | {len(m)} | " + " | ".join(cel) + " |")
    (D / "tabella.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))
    # separazione: quanto le generate (tutte) stanno fuori dal range suo
    suoi = tutto["SUOI (6 pagine Architettura)"]; gen = [x for g, m in tutto.items() if not g.startswith(("SUOI", "41")) for x in m]
    print("\nseparazione (frazione generate fuori dal suo min-max | distanza mediane / spread):")
    for c in chiavi:
        s = [x[c] for x in suoi]; t = [x[c] for x in gen]
        fuori = np.mean([(v < min(s)) or (v > max(s)) for v in t])
        dist = abs(np.median(t) - np.median(s)) / max(np.std(s) + np.std(t), 1e-6)
        print(f"  {c:20} fuori={fuori:.2f} dist={dist:.2f}  suoi med {np.median(s):g} gen med {np.median(t):g}")
