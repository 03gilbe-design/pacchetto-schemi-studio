# C — STILE (un tono, non un modello da copiare)
Le regole A vengono prima. Questo è il tono dei suoi schemi di Architettura: da usare come direzione, variando da pagina a pagina.
Non va riprodotto identico (con il blocco stile fisso il modello lo copiava pari pari: CRITICHE_08-10 #1).
Numeri misurati dal codice (`stile_numeri.py` → `ESPERIMENTI/5_STILE_in_numeri/stile_gilberto.json`) su 6 sue pagine di Architettura (p02-p07, PDF vettoriale).

## 1. Le sue frasi (sezione 6 del Word, parola per parola)
- simboli e formule: la formula simbolica può comparire, ma solo come rinforzo, sotto la versione visiva
- forme irregolari: un contorno a mano si distingue dal testo e dalle forme tecniche; in genere gli elementi disordinati (font a mano, forme irregolari) richiamano l'attenzione
- etichette corte e vicine: il testo è corto, a poco contrasto, attaccato al disegno che descrive
- il nome al posto del verbo: dove il professore scrive una frase, io scrivo il nome della cosa
- il risultato in fondo, in evidenza: l'arrivo è il risultato del caso (cosa esce), non una frase riassuntiva
- il contesto sempre in alto: in cima alla pagina scrivo da dove si parte e dove si arriva, anche se il professore non lo dice
- passaggi: se posso, rappresento graficamente lo stato prima, cosa succede e lo stato dopo
- varietà a campana: quasi tutto ha la stessa forma principale; le varianti (altro testo, altra forma, altro colore) sono poche e messe solo dove servono, come le code di una campana
- zoom sul dettaglio: se un passaggio sta dentro un altro, lo metto dentro con uno zoom collegato
- un caso concreto con numeri piccoli, seguito dall'inizio alla fine, prima della forma generale
- fondo caldo color crema, tratti marroni sottili
- UN solo colore forte (corallo/arancio): sul titolo e sul caso che si segue
- titolo in una fascia in alto; per il resto il disegno sta sul foglio, senza riquadri pesanti
- scritto a mano solo per titolo e risultato, sans-serif per tutto il resto
- è un tono, non un modello: le regole vengono prima

(Tolti solo i due esempi tra parentesi di materia: "(MEMORIA e CACHE attaccate ai loro rettangoli)" e "(«preleva l'istruzione» → FETCH)": stanno in fondo, tra gli esempi.)

## 2. Palette (area dei riempimenti, % su 6 pagine)
| ruolo | hex | quanto |
|---|---|---|
| fondo crema | #FAF6EF | colore di fondo di tutte le pagine (106,4%: le aree sovrapposte si sommano) |
| colore forte (corallo) | #FF654C | 8,7% dell'area; fascia del titolo in 6 pagine su 6 |
| pesca chiaro (riempimenti) | #F2AA84 | 5,5% |
| bianco (riquadri dentro la fascia, caselle) | #FFFFFF | 3,1% |
| marrone (tratti, parole chiave) | #795548 | 0,8% |
| azzurro chiaro | #C2D9E5 | 0,5% |
| grigio-rosa | #C8B8B0 | 0,5% |
| turchese (collegamenti) | #2BBFCF | 0,3% |
| marrone chiaro | #997E71 | 0,3% |
| rosso (collegamenti) | #FF1F3C | 0,2% |

Colore del testo (% dei 6.934 caratteri): marrone chiaro #997E71 51,1% · nero #000000 32,0% · marrone #795548 7,0% ·
bianco #FFFFFF 5,8% (3,4% grande ≥ 20 pt, 2,4% piccolo) · #AB9488 1,7% · corallo #FF654C 1,5% (solo grande) · crema #FAF6EF 1,0%.

## 3. Font per ruolo (% dei 7.125 caratteri)
| font | ruolo | % caratteri | grandezza mediana (min-max) |
|---|---|---|---|
| AFont1 (scritto a mano) | titolo, etichette che devono attirare | 5,7% | 28 pt (20-28) |
| Aptos (sans-serif) | tutto il testo | 85,0% | 12 pt (9-28) |
| Aptos Bold | parole chiave | 9,2% | 12 pt (9-32) |
| Arial | residuo | 0,04% (3 caratteri) | 12 pt |

## 4. Tratto
Spessore linee (558 tratti): 1,5 pt nel 74,6% · 1,2 pt 11,6% · 2,2 pt 10,2% · 3,0 pt 3,6%.
Linee piene 537, tratteggiate 34 (6,0%). Fascia del titolo: alta 9,6% della pagina in p02-p04 (cache, LRU), 4,2-5,3% in p05-p07 (esercizi memoria, fetch).

## 5. Pattern ricorrenti
Fascia corallo in alto con il titolo a mano · testo marrone chiaro, mai nero puro come colore principale · un elemento corallo che segue il caso ·
disegni a tratto sottile, riempimenti chiari (pesca, azzurro, grigio-rosa) · collegamenti tratteggiati colorati · risultato in fondo.

## 6. Cosa ne consegue (regole operative ricavate da Claude Code dai numeri sopra; non sono sue parole)
1. Un solo colore forte: il corallo sta sotto il 10% dell'area; tutto il resto è crema, marrone e tinte chiare.
2. Il colore forte va dove c'è da seguire qualcosa (titolo, caso, risultato), non su riquadri decorativi.
3. Il testo corrente è tenue (marrone chiaro, 51%); il nero e il grassetto (9%) servono per ciò che deve emergere.
4. Il font a mano è raro (meno del 6% dei caratteri): solo dove si vuole l'occhio (titolo, risultato).
5. Tratto sottile come base (1,5 pt in 3 tratti su 4); lo spessore maggiore (2,2-3 pt, 14%) solo per evidenziare.
6. Tratteggio per i collegamenti, non per i contorni (6% delle linee).
7. In alto il contesto da A a B; in fondo il risultato in evidenza.
8. Fondo crema, mai bianco puro.
9. Variare: la fascia, i colori e le forme non si ripetono identici su ogni pagina; si tiene il tono.

## Esempi (solo esempi, dai suoi schemi; non fanno parte dello stile da dare al modello)
- etichette corte e vicine: MEMORIA e CACHE attaccate ai loro rettangoli
- il nome al posto del verbo: «preleva l'istruzione» → FETCH
- miniature frase | ritaglio: `ESPERIMENTI/35_STILE_MINIATURE/STILE_FRASI_MINIATURE.pdf` (14 frasi su 15 con esempio; deboli 8, 10, 12; l'ultima senza esempio)
