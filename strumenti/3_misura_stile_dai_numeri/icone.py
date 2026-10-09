"""41 (Gilberto: "mettici una minigrafica quadrata affianco"): un'iconcina quadrata per ogni metrica, stile slide
(crema, marrone, un tocco corallo). icona(chiave) -> PIL.Image 120x120. Uso diretto: scrive confronti/icone/*.png per guardarle."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
CREMA, MARR, COR, PES, AZZ, GRI = "#FAF6EF", "#795548", "#FF654C", "#F2AA84", "#C2D9E5", "#C8B8B0"
S = 4; L = 120 * S  # disegno 4x e poi rimpicciolisco: bordi morbidi


def _font(n, mano=False):
    f = r"C:\Windows\Fonts\segoepr.ttf" if mano else r"C:\Windows\Fonts\segoeui.ttf"
    try: return ImageFont.truetype(f, n * S)
    except OSError: return ImageFont.load_default()


def _righe(d, x0, y0, x1, n, passo=13, col=MARR, w=3, corte=False):
    for i in range(n):
        xe = x1 - (i % 2) * (x1 - x0) * 0.25 if not corte else x0 + (x1 - x0) * 0.35
        d.line([(x0 * S, (y0 + i * passo) * S), (xe * S, (y0 + i * passo) * S)], fill=col, width=w * S)


def _pagina(d, x0=28, y0=12, x1=92, y1=108):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill="white", outline=MARR, width=2 * S)


def icona(k):
    im = Image.new("RGB", (L, L), CREMA); d = ImageDraw.Draw(im); R = lambda *b, **kw: d.rectangle([v * S for v in b], **kw)
    if k.startswith("corpo"):
        d.text((14 * S, 18 * S), "Aa", font=_font(46), fill=MARR); d.text((76 * S, 62 * S), "aa", font=_font(16), fill=GRI)
        d.line([(14 * S, 100 * S), (106 * S, 100 * S)], fill=COR, width=3 * S)
    elif k.startswith("testo_su_fondo"):
        _righe(d, 16, 24, 104, 6, 14)
    elif "evidenziat" in k:
        _righe(d, 16, 24, 104, 6, 14, col=GRI); R(30, 48, 78, 64, fill=PES); _righe(d, 34, 56, 74, 1, col=MARR, corte=False)
    elif k.startswith("vuoto_terzo"):
        _pagina(d); R(34, 18, 86, 44, fill=GRI); R(34, 50, 70, 70, fill=GRI)
        R(30, 76, 90, 106, outline=COR, width=2 * S); d.text((50 * S, 80 * S), "?", font=_font(16), fill=COR)
    elif k.startswith("blocco_piu"):
        for b in [(12, 14, 46, 40), (58, 12, 104, 34), (14, 56, 40, 84), (52, 48, 106, 100), (14, 92, 38, 108)]:
            R(*b, fill=GRI)
        R(52, 48, 106, 100, outline=COR, width=3 * S)
    elif k == "blocchi_n":
        for i in range(3):
            for j in range(3): R(14 + 34 * i, 14 + 34 * j, 38 + 34 * i, 38 + 34 * j, fill=GRI)
    elif k.startswith("colore_forte"):
        _pagina(d); R(28, 12, 92, 30, fill=COR); d.ellipse([60 * S, 70 * S, 72 * S, 82 * S], fill=COR); _righe(d, 36, 44, 84, 3, 10, col=GRI, w=2)
    elif k.startswith("zone_forti"):
        _pagina(d)
        for c in [(36, 20), (70, 54), (44, 88)]: d.ellipse([c[0] * S, c[1] * S, (c[0] + 14) * S, (c[1] + 14) * S], fill=COR)
    elif k.startswith("tinta_dominante"):
        d.pieslice([16 * S, 16 * S, 104 * S, 104 * S], 0, 250, fill=COR); d.pieslice([16 * S, 16 * S, 104 * S, 104 * S], 250, 320, fill=PES)
        d.pieslice([16 * S, 16 * S, 104 * S, 104 * S], 320, 360, fill=AZZ)
    elif k.startswith("parole_su_prof"):
        _pagina(d, 8, 16, 54, 104); _righe(d, 14, 26, 48, 6, 12, col=GRI, w=2)
        _pagina(d, 66, 16, 112, 104); _righe(d, 72, 26, 106, 3, 12, col=MARR, w=2); d.text((80 * S, 70 * S), "½", font=_font(20), fill=COR)
    elif k.startswith("parole_in_righe"):
        _righe(d, 12, 22, 108, 3, 14); _righe(d, 12, 74, 108, 3, 12, col=GRI, corte=True)
    elif k == "parole":
        _pagina(d); _righe(d, 36, 24, 84, 6, 13, col=MARR, w=2)
    elif k.startswith("combinazioni_stile") or k.startswith("entropia"):
        for i, (c, f) in enumerate([(MARR, False), (COR, True), (GRI, False)]):
            d.text((14 * S, (10 + 34 * i) * S), "Aa", font=_font(24, f), fill=c)
        d.text((70 * S, 40 * S), "×3", font=_font(22), fill=MARR)
    elif k.startswith("combinazioni_forme"):
        R(12, 14, 50, 48, outline=MARR, width=3 * S); d.ellipse([64 * S, 14 * S, 104 * S, 50 * S], fill=PES)
        d.line([(14 * S, 90 * S), (104 * S, 70 * S)], fill=GRI, width=4 * S); R(70, 84, 104, 106, fill=AZZ)
    elif k.startswith("forme_linee"):
        d.line([(12 * S, 30 * S), (108 * S, 60 * S)], fill=GRI, width=4 * S); d.line([(12 * S, 90 * S), (108 * S, 70 * S)], fill=MARR, width=4 * S)
    elif k == "vuoto_%":
        _pagina(d); R(34, 18, 70, 34, fill=GRI)
    elif k.startswith("contorni_dritti"):
        R(10, 30, 52, 90, outline=MARR, width=3 * S)
        pts = [(66 + 2 * math.sin(t), 30 + t * 4) for t in range(16)] + [(66 + t * 2.6, 90 + 2 * math.sin(t)) for t in range(16)] + \
              [(108 + 2 * math.sin(t), 90 - t * 4) for t in range(16)] + [(108 - t * 2.6, 30 + 2 * math.sin(t)) for t in range(17)]
        d.line([(x * S, y * S) for x, y in pts], fill=COR, width=3 * S)
    elif k.startswith("dentro_riquadri") or k.startswith("riquadri"):
        R(14, 20, 106, 100, outline=MARR, width=3 * S); _righe(d, 26, 40, 94, 4, 14, col=GRI)
    elif k.startswith("spessore"):
        d.line([(12 * S, 36 * S), (108 * S, 36 * S)], fill=MARR, width=2 * S); d.line([(12 * S, 80 * S), (108 * S, 80 * S)], fill=MARR, width=9 * S)
    elif k.startswith("scuro") or k.startswith("tenue"):
        _righe(d, 12, 26, 108, 3, 12, col="#222222"); _righe(d, 12, 74, 108, 3, 12, col=GRI)
    elif k.startswith("pastello") or k == "tinte":
        for i, c in enumerate([PES, AZZ, GRI, "#CFE8C8"]): R(12 + 25 * i, 40, 32 + 25 * i, 80, fill=c)
    elif k.startswith("forte_"):
        _pagina(d); R(28, 12, 92, 30, fill=COR)
    else:
        _pagina(d)
    R(1, 1, 119, 119, outline=GRI, width=2 * S)
    return im.resize((120, 120), Image.LANCZOS)


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
    from classifica_info import INFO
    o = Path(__file__).resolve().parent / "confronti" / "icone"; o.mkdir(parents=True, exist_ok=True)
    tav = Image.new("RGB", (130 * 6, 130 * math.ceil(len(INFO) / 6)), "white")
    for i, k in enumerate(INFO):
        tav.paste(icona(k), (130 * (i % 6) + 5, 130 * (i // 6) + 5))
    tav.save(o / "tutte.png")
