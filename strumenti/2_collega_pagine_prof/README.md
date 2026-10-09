# 2. Collegare le pagine di appunti alle pagine del prof

Due strumenti: uno solo codice (annotatore), uno con un modello che guarda l'immagine (Groq).

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
