# prepara.py <materiale> - rende le mie pagine e trova/rende il materiale del prof per quel materiale.
# 09/10: il calcolo e' in due funzioni (pagine_prof, migliori) per riusarlo da collega_deterministico.py; stesso risultato di prima.
import collections, io, json, math, os, re, sys
import fitz
par = lambda t: re.findall(r'[a-zàèéìòù]{4,}', t.lower())


def pagine_prof(files):
    """pagine del prof con testo (>= 8 parole) -> lista (file, pagina 1-based, set parole), idf delle parole."""
    df = collections.Counter(); pag_prof = []
    for f in files:
        if not os.path.exists(f): print('manca', f); continue
        for i, p in enumerate(fitz.open(f)):
            ws = set(par(p.get_text()))
            if len(ws) < 8: continue
            pag_prof.append((f, i + 1, ws)); df.update(ws)
    idf = {w: math.log(max(2, len(pag_prof)) / c) for w, c in df.items()}
    return pag_prof, idf


def migliori(mie, pag_prof, idf, n=3):
    """le n pagine del prof piu' simili a un set di parole mie (parole rare in comune, pesate IDF) -> [(pagina, punteggio)]."""
    pun_di = lambda x: sum(idf.get(w, 0) for w in mie & x[2]) / (1 + math.log(1 + len(x[2])))
    return [(x, pun_di(x)) for x in sorted(pag_prof, key=pun_di, reverse=True)[:n]]


if __name__ == '__main__':
    QUI = os.path.dirname(os.path.abspath(__file__)); MAT = sys.argv[1] if len(sys.argv) > 1 else 'architettura'
    C = json.load(io.open(os.path.join(QUI, 'materiali.json'), encoding='utf-8'))[MAT]
    PAG = os.path.join(QUI, MAT, 'pagine'); FON = os.path.join(QUI, MAT, 'fonti'); os.makedirs(PAG, exist_ok=True); os.makedirs(FON, exist_ok=True)
    pag_prof, idf = pagine_prof(C['prof'])
    mappa = {}; n = 0
    for nome, f in C['miei']:
        if not os.path.exists(f): print('manca mio', f); continue
        d = fitz.open(f)
        for i, p in enumerate(d):
            k = f'{nome}_p{i + 1:02d}'; p.get_pixmap(dpi=200).save(os.path.join(PAG, k + '.png')); n += 1
            mie = set(par(p.get_text()))
            if not mie or not pag_prof: continue
            top = migliori(mie, pag_prof, idf); ordinate = [x for x, _ in top]
            best, pun = top[0]
            if pun < .8: continue
            fitz.open(best[0])[best[1] - 1].get_pixmap(dpi=200).save(os.path.join(FON, k + '.png'))
            # due misure: quanto della MIA pagina viene da li' (ripresa) e quanto della PAGINA DEL PROF ho tenuto (tenuto)
            unione = set().union(*[x[2] for x in ordinate])
            ripresa = round(100 * len(mie & unione) / max(1, len(mie)))
            tenuto = round(100 * len(mie & best[2]) / max(1, len(best[2])))
            mappa[k] = {'nome': os.path.basename(best[0]), 'pagina': best[1], 'punteggio': round(pun, 2),
                        'ripresa': ripresa, 'tenuto': tenuto, 'parole_mie': len(mie),
                        'altre_pagine': [x[1] for x in ordinate[1:]],
                        'parole': ', '.join(sorted(mie & best[2], key=lambda w: -idf.get(w, 0))[:8])}
    io.open(os.path.join(FON, 'mappa.json'), 'w', encoding='utf-8').write(json.dumps(mappa, ensure_ascii=False, indent=1))
    print(MAT, ':', n, 'mie pagine ·', len(mappa), 'con materiale del prof')
