# 2. Collegare le pagine di appunti alle pagine del prof

Tre strumenti: due solo codice (collega_deterministico, annotatore), uno con un modello che guarda l'immagine (Groq).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/03gilbe-design/vocabolario-schemi-studio/blob/main/Collega_Pagine_Colab.ipynb)

## collega_deterministico.py (solo codice; su Colab: `Collega_Pagine_Colab.ipynb`)
**Cosa fa:** per ogni pagina dei tuoi schemi (PDF o PNG) trova la pagina del prof più simile (PDF o PNG). Riusa `annotatore/prepara.py` (`pagine_prof`, `migliori`: parole rare in comune pesate IDF) quando c'è testo; senza testo ripiega su hash percettivo + istogramma. Per ogni coppia conta le frasi del prof ritrovate nello schema (`frasi_prof`, `blocchi_miei` di `3_misura_stile_dai_numeri/allinea_auto.py`, `parole` di `allinea.py`). Con `--generate` lancia `trova_differenze.py` con `--prof-parole` = mediana delle pagine del prof collegate.
**Quando fidarsi:** la colonna `affidabile` dice `si` per i collegamenti fatti col **testo** (o con Gemini); `NO` per quelli a **vista** (scansioni, foto: nel test UX 2 giuste su 7) e per gli schemi bianchi, che la vista collega comunque con punteggio alto (0,97). Se il PDF del prof non ha testo lo script lo dice all'inizio. File vuoti, Word o cartelle che non esistono: messaggio `ERRORE:` e exit 1.
**Prova (09/10, 15 schemi di Architettura con fonte nota, 3 PDF del prof = 314 pagine; giusta = stesso PDF e pagina ±1):**

| | solo codice | codice + Gemini (fra i 5 del codice) | Gemini su tutte le pagine (`--gemini`) |
|---|---|---|---|
| con testo (PDF) | 15/15 | 13/15 | - |
| solo immagini | 1/15 | 3/15 (la giusta era fra i 5 solo 8 volte) | 13/15 (giusta fra le 3 finaliste 15/15) |

Quindi: col testo basta il codice (Gemini sbaglia 2 volte); senza testo serve `--gemini`, che usa Gemini solo sulle pagine senza testo: fogli di miniature numerate di tutte le pagine del prof -> 3 finaliste -> 1 (2 chiamate per pagina). Se la seconda chiamata non sceglie, tiene la prima finalista (sulle stesse risposte: 14/15). Grafico: `collega_codice_vs_gemini.png`. Il test è stato fatto con Gemini 3.8 Flash via CLI `agy`; la chiave API locale era senza credito, quindi la strada via API (`--gemini`) è provata solo con risposte finte.
```
python collega_deterministico.py --schemi miei.pdf --prof prof1.pdf prof2.pdf [--generate cartella_AI] [--out risultati_collega_det]
```

## annotatore/ (solo codice + interfaccia nel browser)
**Cosa fa:** per ogni pagina dei tuoi schemi trova la pagina del prof più simile (parole rare in comune, pesate IDF), la rende in PNG e calcola due misure: `ripresa` (quanto della tua pagina viene da lì) e `tenuto` (quanto della pagina del prof hai tenuto). Poi un'interfaccia locale mostra la tua pagina con la fonte del prof accanto e permette di annotare con il mouse.

**Input:** `materiali.json` (copia `materiali.esempio.json` e metti i tuoi percorsi): per ogni materia i PDF tuoi (`miei`) e i PDF del prof (`prof`). Funziona con PDF che hanno testo (non scansioni).
**Output:** `<materia>/pagine/*.png` (tue pagine a 200 dpi), `<materia>/fonti/*.png` + `<materia>/fonti/mappa.json` (pagina tua -> file e pagina del prof, punteggio, parole in comune), `<materia>/annotazioni.json` (le note fatte nell'interfaccia).

**Comandi:**
```
pip install pymupdf
python prepara.py architettura      # collega e rende le pagine
python annota.py architettura       # apre http://127.0.0.1:8777  (oppure ANNOTA.bat)
```

## groq/ (modello che vede l'immagine)
**Cosa fa:** per ogni pagina dei tuoi schemi: 1) un modello Groq (qwen, vede l'immagine) descrive la pagina con argomento + 15 parole chiave; 2) il codice prende le 10 pagine del prof più vicine (BM25); 3) il modello sceglie fra le 10 (o nessuna) e dice perché; 4) il codice confronta con una verità nota (giusto se stessa fonte e pagina ±1).

**Input (variabili d'ambiente):**
- `GROQ_API_KEY` — chiave Groq (piano gratis va bene; lo script aspetta da solo sui limiti 429).
- `SCHEMA_PDF` — PDF dei tuoi schemi.
- `FONTI_DIR` — cartella con i PDF del prof (nomi file nel dizionario `FONTI` dentro lo script, da adattare) e `dettaglio_tecnico__fonti_pagina_per_pagina.md` (la verità, confronto parola per parola).

**Output:** `risultati_collega/p<N>/` (descrizione, candidati, scelta, `esito.json`), `risultati_collega/risultati.json`, `risultati_collega/RISULTATI.md` (giuste / totale, verità fra i 10 candidati).

**Comando:**
```
pip install pymupdf
set GROQ_API_KEY=...   &  set SCHEMA_PDF=C:\...\schemi.pdf  &  set FONTI_DIR=C:\...\fonti
python test_collega_groq.py
python groq.py          # elenca i modelli disponibili
```
