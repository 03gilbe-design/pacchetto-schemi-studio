# 3. Estrarre numeri dagli appunti

Misure fatte solo dal codice (niente AI, tranne dove scritto), per dire con numeri come è fatta una pagina di appunti e controllare se una pagina generata le somiglia.

## trova_differenze.py: tutto con un comando
**Cosa fa.** Confronta i tuoi schemi con le pagine generate da un'AI. Misura circa 30 numeri: colore, vuoto, blocchi, corpo del testo, testo libero o dentro caselle, parole e combinazioni di stile. Poi tiene solo quelli che:
- **sgamano:** le pagine generate cadono fuori dal tuo intervallo;
- **reggono:** non cambiano con la risoluzione;
- **si convertono:** si possono scrivere come istruzione per il modello.

Per quelli tenuti scrive la frase da dare al modello e i valori per il controllo automatico. Tutto solo con codice: niente OCR, niente modelli, meno di 1 GB di memoria, circa 30 secondi sugli esempi.

**Installazione** (una volta sola):
```
pip install -r requirements.txt
python -m playwright install chromium
```

**Prova con gli esempi inclusi** (`esempi_numeri/`: un PDF di schemi dello studente, 7 pagine di Claude in HTML/SVG):
```
python -X utf8 trova_differenze.py --suoi esempi_numeri/suoi/Architettura_Gilberto.pdf --generate esempi_numeri/generate --prof-parole 385
```
Il risultato finisce in `risultati_numeri/`:
- `CLASSIFICA.md`: tutti i numeri, con il tuo intervallo e i valori delle generate;
- `FRASI_PER_IL_MODELLO.md`: le frasi da incollare nel prompt;
- `numeri.json`: i tuoi intervalli, da usare per il controllo;
- `classifica.png`: il grafico.

**Con i tuoi appunti, in 3 passi:**
1. **Metti in una cartella le pagine generate dall'AI.** Vanno bene `.html`, `.svg` o `.png`, anche in sottocartelle. Con `.html`/`.svg` si misurano anche testo e font; con solo `.png` solo colore, vuoto e blocchi.
2. **Lancia il comando:**
   ```
   python -X utf8 trova_differenze.py --suoi i_miei_schemi.pdf --generate cartella_generate
   ```
   - Il PDF deve essere quello esportato da Canva/Word/GoodNotes, con testo vero: dà font, colori e corpo esatti. Vanno bene anche `.png`, ma con meno misure.
   - Aggiungi `--prof-parole N` se sai quante parole ha la pagina del docente.
3. **Incolla le frasi nel prompt e controlla la pagina che esce:**
   - le frasi sono in `risultati_numeri/FRASI_PER_IL_MODELLO.md`, vanno nella parte stile del prompt;
   - per controllare una pagina generata:
     ```
     python -X utf8 controlla_stile.py pagina.png --sorgente pagina.html --rif risultati_numeri/numeri.json
     ```
     Stampa OK o FUORI, con un consiglio. Esce con 0 se tutto è OK, 1 se qualcosa è fuori: un agente può rigenerare la pagina finché è tutto OK.

**Efficacia (facoltativo).** Le frasi cambiano davvero il modello? Genera qualche pagina senza frasi e qualche pagina con le frasi, in due cartelle, e aggiungi:
```
--efficace-senza cartella_senza --efficace-con cartella_con
```
La classifica guadagna la colonna "efficace".

**Altri file:**
- `misura.py`: numeri del colore sul PNG;
- `misura2.py`: vuoto e blocchi;
- `elementi.py`: testi e forme dal PDF/HTML/SVG;
- `combinazioni.py`: coppie di attributi e varietà;
- `classifica_info.py`: per ogni numero, se regge alla risoluzione e se si converte in frase;
- `icone.py`: le iconcine dei grafici;
- `misure.json` / `misure2.json`: gli intervalli di riferimento dell'esperimento (6 pagine di Architettura), usati da `controlla_stile.py` quando non c'è `--rif`.

## controlla_attenzione.py + misura.py (esperimento 41) — il più pronto
**Cosa fa:** misura l'"attenzione" di una pagina PNG: colore forte (% pagina), zone di colore forte separate, quanta parte del colore prende la tinta principale (più pastello, tinte, scuro/tenue, posizione del colore forte). `controlla_attenzione.py` confronta le 3 misure che separano di più con il range (min-max) delle pagine di riferimento e dice OK/FUORI con un consiglio. Pensato per un agente: misura -> se FUORI rigenera.
**Input:** uno o più PNG. Il range di riferimento è in `misure.json` (gruppo `SUOI`, 6 pagine di Architettura).
**Output:** a schermo, una riga per misura; exit code 0 = tutto dentro, 1 = almeno una FUORI.
```
pip install numpy pillow scipy
python -X utf8 controlla_attenzione.py pagina.png [altre.png ...]
python -X utf8 misura.py --suoi a.png b.png ... --out rif.json     # misura appunti qualsiasi (nuovo riferimento)
```
Per usare un riferimento nuovo: rinomina `rif.json` in `misure.json` (la chiave del gruppo resta `SUOI (6 pagine Architettura)`). `misura.py` senza argomenti rifà la tabella dell'esperimento e serve la cartella `ESPERIMENTI/` originale.

## quanto_urla.py
**Cosa fa:** "quanto è urlata la pagina": colorfulness (Hasler-Süsstrunk), % pixel saturi, numero di tinte, macchie di colore separate, contrasto. Funzione `misura(png)` riusabile.
**Input/Output:** così com'è legge le cartelle dell'esperimento (`ESPERIMENTI/4_NOTTE.../p0*/`) e scrive `ESPERIMENTI/quanto_urla.json`; per altre pagine importa `misura`.
```
python -X utf8 quanto_urla.py
```

## stile_numeri.py
**Cosa fa:** dai PDF vettoriali dei tuoi schemi estrae lo stile in numeri: font e grandezze per ruolo, palette per area, colori del testo, fascia/banner in alto, spessore linee, pieno/tratteggio.
**Input:** pagine `schema_esercizi_p02..p07` lette tramite `allinea_auto.pdf_mio` (cioè dal `materiali.json` dell'annotatore, cartella in `ANNOTATORE_DIR`).
**Output:** `ESPERIMENTI/5_STILE_in_numeri/stile_gilberto.json`.
```
pip install pymupdf opencv-python numpy pillow
set ANNOTATORE_DIR=C:\...\annotatore
python -X utf8 stile_numeri.py
```

## numeri_coppie.py (+ allinea.py, allinea_auto.py)
**Cosa fa:** per ogni coppia "pezzo di pagina del prof -> pezzo del tuo schema" (prodotte da `allinea.py`) calcola numeri su due rami: testo (parole, frasi, numeri, rapporto parole mio/prof, maiuscole) e grafica (riquadri, linee, colori, grandezze del testo, area disegnata). Poi Gemini guarda la tabella del 70% delle coppie e propone range; il codice tiene solo quelli che reggono (≥70%) sul 30% mai visto e scarta quelli banali.
**Input:** le coppie in `allinea/` (create da `python allinea.py <chiave>`), `materiali.json` + `fonti/mappa.json` dell'annotatore (`ANNOTATORE_DIR`), la CLI Gemini `agy` (percorso in `AGY`).
**Output:** `numeri_coppie.json`, `NUMERI_COPPIE.md` (mediana e 10-90% per misura), `parametri.json` (range proposti e tenuti).
```
python numeri_coppie.py --solo-misure    # solo i numeri, niente AI
python numeri_coppie.py                  # + proposta Gemini e verifica
python numeri_coppie.py --riverifica     # rifà solo la verifica
```
