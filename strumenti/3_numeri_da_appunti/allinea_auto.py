"""Allineamento AUTOMATICO prof -> Gilberto per tutte le pagine dell'annotatore (Gilberto 04/10: 'mi fai le altre, con i collegamenti,
colori meno invasivi, devo poter leggere'). Codice: frasi del prof trovate parola per parola + blocchi della sua pagina.
Gemini Flash: abbina per SIGNIFICATO ogni frase del prof al blocco suo che dice la stessa cosa (o nessuno). Disegni: non ancora.
Uso: python allinea_auto.py [chiave ...]   (es. schemi_architettura_p02)   senza argomenti = tutte. Esce: auto/<chiave>.jpg + .json"""
import json, re, subprocess, sys
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

QUI = Path(__file__).parent; H = Path.home()
import os
ANN = Path(os.environ.get("ANNOTATORE_DIR", str(H / "Downloads" / "tirocinio" / "annotatore")))  # cartella con materiali.json
AGY = os.environ.get("AGY", str(H / "AppData" / "Local" / "agy" / "bin" / "agy.exe"))  # CLI Gemini (Antigravity)
OUT = QUI / "auto"; OUT.mkdir(exist_ok=True)
MAT = json.loads((ANN / "materiali.json").read_text(encoding="utf-8"))
# colori tenui (velatura leggera + bordo sottile): il testo sotto deve restare leggibile
COLORI = [(192, 80, 77), (79, 129, 189), (120, 160, 80), (128, 100, 162), (230, 140, 60), (70, 160, 180), (150, 120, 90), (200, 90, 150)]


def pdf_mio(materia, chiave):
    nome, n = chiave.rsplit("_p", 1)
    f = dict(MAT[materia]["miei"])[nome]
    return f, int(n) - 1


def pdf_prof(materia, voce):
    if voce.get("file"):
        return voce["file"]
    return next(p for p in MAT[materia]["prof"] if Path(p).name == voce["nome"])


def frasi_prof(pg):
    """frasi del prof con i riquadri delle loro righe (parola per parola)."""
    ws = pg.get_text("words"); frasi, cur = [], []
    for w in ws:
        cur.append(w)
        if re.search(r"[.:;!?]$", w[4]) and len(cur) >= 4:
            frasi.append(cur); cur = []
    if len(cur) >= 3:
        frasi.append(cur)
    out = []
    for f in frasi:
        righe = {}
        for w in f:
            k = (w[5], w[6]); r = righe.get(k, list(w[:4])); righe[k] = [min(r[0], w[0]), min(r[1], w[1]), max(r[2], w[2]), max(r[3], w[3])]
        out.append({"testo": " ".join(w[4] for w in f), "zone": list(righe.values())})
    return out


def blocchi_miei(pg):
    return [{"testo": " ".join(b[4].split()), "zone": [list(b[:4])]} for b in pg.get_text("blocks") if len(" ".join(b[4].split())) > 3]


def abbina(frasi, blocchi):
    prompt = ("A = frasi di una pagina di libro. B = pezzi di testo di uno schema fatto a partire da quella pagina.\n"
              "Per ogni frase di A indica i pezzi di B che esprimono lo stesso contenuto (anche con parole diverse), oppure nessuno.\n"
              "Rispondi SOLO con JSON: [{\"a\": numero, \"b\": [numeri]}] (metti solo le frasi che hanno almeno un pezzo).\n\nA:\n"
              + "\n".join(f"{i}. {f['testo'][:300]}" for i, f in enumerate(frasi, 1)) + "\n\nB:\n"
              + "\n".join(f"{j}. {b['testo'][:200]}" for j, b in enumerate(blocchi, 1)))
    out = subprocess.run([AGY, "-p", prompt, "--model", "gemini-3.8-flash-medium", "--print-timeout", "10m"], capture_output=True,
                         text=True, encoding="utf-8", errors="ignore", timeout=900).stdout
    dec = json.JSONDecoder()
    for i in [m.start() for m in re.finditer(r"\[", out)]:
        try:
            js, _ = dec.raw_decode(out[i:])
            if isinstance(js, list) and all(isinstance(x, dict) and "a" in x for x in js):
                return js, prompt, out
        except ValueError:
            continue
    return [], prompt, out


GIA = {}  # quante etichette ha gia' ogni zona: piu' frasi del prof nello stesso blocco -> numeri IN FILA, non sovrapposti


def disegna(img, zone, colore, dx, dy, z, etichetta, f):
    strato = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(strato)
    for n, (x0, y0, x1, y1) in enumerate(zone):
        box = [x0 * z + dx, y0 * z + dy, x1 * z + dx, y1 * z + dy]
        chiave = tuple(int(v) for v in box); k = GIA.get(chiave, 0); GIA[chiave] = k + 1
        if k == 0:
            d.rectangle(box, fill=colore + (38,), outline=colore + (170,), width=2)
        if n == 0:
            ox = box[0] - 30 + k * 30
            d.ellipse([ox, box[1] - 4, ox + 26, box[1] + 22], fill=colore + (210,))
            d.text((ox + 7, box[1] - 2), etichetta, fill=(255, 255, 255, 255), font=f)
    img.alpha_composite(strato)


def una(materia, chiave, voce):
    GIA.clear()
    fm, nm = pdf_mio(materia, chiave); fp = pdf_prof(materia, voce)
    pm, pp = fitz.open(fm)[nm], fitz.open(fp)[voce["pagina"] - 1]
    frasi, blocchi = frasi_prof(pp), blocchi_miei(pm)
    if not frasi or not blocchi:
        return None
    coppie, prompt, risposta = abbina(frasi, blocchi)
    metodo = "gemini-3.8-flash-medium (per significato)"
    if not coppie:  # 04/10: Gemini gratis esaurito (429) -> ripiego SENZA AI: parole in comune (piu' debole, lo si dichiara)
        pw = lambda s: set(re.findall(r"[a-zàèéìòù]{4,}", s.lower()))
        coppie = []
        for i, fr in enumerate(frasi, 1):
            best = max(((len(pw(fr["testo"]) & pw(bl["testo"])) / (len(pw(fr["testo"]) | pw(bl["testo"])) or 1), j) for j, bl in enumerate(blocchi, 1)), default=(0, 0))
            if best[0] >= 0.15:
                coppie.append({"a": i, "b": [best[1]]})
        metodo = "parole in comune (ripiego senza AI: Gemini non disponibile)"
    z = 2
    ip = Image.frombytes("RGB", *[(lambda x: ((x.width, x.height), x.samples))(pp.get_pixmap(matrix=fitz.Matrix(z, z)))][0])
    im = Image.frombytes("RGB", *[(lambda x: ((x.width, x.height), x.samples))(pm.get_pixmap(matrix=fitz.Matrix(z, z)))][0])
    tela = Image.new("RGBA", (ip.width + im.width + 80, max(ip.height, im.height) + 110), (255, 255, 255, 255))
    tela.paste(ip, (30, 70)); tela.paste(im, (ip.width + 70, 70))
    f = ImageFont.truetype("arialbd.ttf", 18); ft = ImageFont.truetype("arialbd.ttf", 30); dd = ImageDraw.Draw(tela)
    dd.text((30, 18), f"PROF · {Path(fp).name[:40]} p.{voce['pagina']}", fill="black", font=ft)
    dd.text((ip.width + 70, 18), f"TUA PAGINA · {chiave}", fill="black", font=ft)
    dd.text((30, tela.height - 30), "abbinato da: " + metodo, fill=(110, 110, 110), font=f)
    for k, c in enumerate(coppie, 1):
        col = COLORI[(k - 1) % len(COLORI)]
        a = c["a"] - 1
        if 0 <= a < len(frasi):
            disegna(tela, frasi[a]["zone"], col, 30, 70, z, str(k), f)
        for b in c.get("b", []):
            if 0 < b <= len(blocchi):
                disegna(tela, blocchi[b - 1]["zone"], col, ip.width + 70, 70, z, str(k), f)
    tela.convert("RGB").save(OUT / f"{chiave}.jpg", quality=86)
    (OUT / f"{chiave}.json").write_text(json.dumps({"materia": materia, "prof": fp, "pagina_prof": voce["pagina"], "mio": fm, "pagina_mia": nm + 1,
        "coppie": [{"n": k, "prof": frasi[c["a"] - 1]["testo"] if 0 < c["a"] <= len(frasi) else None,
                    "zone_prof": frasi[c["a"] - 1]["zone"] if 0 < c["a"] <= len(frasi) else [],
                    "mio": [blocchi[b - 1]["testo"] for b in c.get("b", []) if 0 < b <= len(blocchi)],
                    "zone_mio": [blocchi[b - 1]["zone"][0] for b in c.get("b", []) if 0 < b <= len(blocchi)]} for k, c in enumerate(coppie, 1)],
        "abbinato_da": metodo, "prompt": prompt, "risposta": risposta[-3000:]}, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(coppie)


def main():
    scelte = sys.argv[1:]
    for materia in ("architettura", "linguaggi"):
        mp = json.loads((ANN / materia / "fonti" / "mappa.json").read_text(encoding="utf-8"))
        for chiave, voce in sorted(mp.items()):
            if (scelte and chiave not in scelte) or chiave == "schema_esercizi_p01":
                continue
            try:
                n = una(materia, chiave, voce)
                print(f"{chiave}: {n} collegamenti")
            except Exception as e:
                print(f"{chiave}: errore {type(e).__name__}: {str(e)[:100]}")


if __name__ == "__main__":
    main()
