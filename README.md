# Pacchetto schemi di studio

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/03gilbe-design/pacchetto-schemi-studio/blob/main/Demo_Pacchetto_Schemi_Colab.ipynb)

**Prova in 1 clic:** il notebook `Demo_Pacchetto_Schemi_Colab.ipynb` gira su Colab senza chiavi, credenziali o Drive, sugli esempi inclusi.

Un vocabolario di regole per far generare a un modello (Claude, GPT, Gemini) **schemi di studio nello stile di uno studente preciso**, a partire da una pagina del docente. Le regole sono state ricavate confrontando le pagine del prof con gli schemi che lo studente ne ha fatto a mano. Lavoro di tirocinio, CdL Informatica, Università di Verona (2026).

## Cosa c'è
```
pacchetto/    le regole da dare al modello (A, B, C, E) e il modulo per estrarne di nuove (D); PACCHETTO.pdf = tutto in un file
strumenti/    codice usato per preparare i dati e misurare i risultati
  1_trascrizione_colab/     trascrivere lezioni/call su GPU Colab (Whisper + chi parla)
  2_collega_pagine_prof/    collegare ogni pagina di appunti alla pagina del prof da cui viene
  3_numeri_da_appunti/      estrarre numeri (colore, zone, tinte, stile, testo) da appunti e pagine generate
esempi/       2 confronti + 1 grafico (solo pagine generate e schemi dello studente)
```

## Come si usa il pacchetto (generare uno schema)
Si dà al modello, in quest'ordine (dettagli e conteggio token in `pacchetto/PACCHETTO.md`):
1. **A_VOCABOLARIO.md** — solo le regole (macro 1-5, fino alla riga `---`). Le regole vengono prima dello stile.
2. **B_NON_FARE.md** — solo le 5 voci **[GENERALE]** (1, 2, 6, 10, 11), una riga ciascuna, senza motivi e fonti.
3. **C_STILE.md** — sezione 1 + elenco degli hex della palette + sezione 6, presentati come tono.
4. **E_AGGIUNTA_FIGURA.md** — la frase "scegli UN caso concreto che attraversi tutti i concetti della pagina".
5. Per ultima la pagina del docente, con un prompt minimale e neutro.

Restano fuori: gli esempi in fondo ad A e C, le tabelle numeriche di C, le voci [OVERFITTING] di B, tutto D. Totale circa 2.070 token. In fondo a B ci sono domande "DA DECIDERE" ancora aperte.

## Come si estraggono regole nuove
`pacchetto/D_MODULO_ESTRAI_REGOLE.md`: ingresso = una pagina del docente + lo schema che lo studente ne ha fatto (oppure solo appunti, confermando la regola su una seconda pagina). Un modello estrae **una** regola (prompt E1), un secondo modello la usa su una pagina del docente mai vista, il primo rivede il risultato. Solo schemi veri dello studente, mai fatti con l'AI.

## Prova veloce: trovare in numeri cosa distingue i tuoi schemi da quelli dell'AI
```
cd strumenti/3_numeri_da_appunti
pip install -r requirements.txt
python -m playwright install chromium
python -X utf8 trova_differenze.py --suoi esempi_numeri/suoi/Architettura_Gilberto.pdf --generate esempi_numeri/generate --prof-parole 385
```
Il risultato è in `risultati_numeri/`: la classifica dei numeri che distinguono lo studente dall'AI, le frasi da dare al modello e i valori per il controllo automatico.

**Con i propri appunti, in 3 passi:**
1. **Una cartella con le pagine fatte dall'AI** (`.html`, `.svg` o `.png`).
2. **Il comando** `python -X utf8 trova_differenze.py --suoi miei_schemi.pdf --generate cartella`.
3. **Le frasi e il controllo:**
   - le frasi di `FRASI_PER_IL_MODELLO.md` vanno nel prompt;
   - ogni pagina nuova si controlla con `python -X utf8 controlla_stile.py pagina.png --sorgente pagina.html --rif risultati_numeri/numeri.json`, che stampa OK o FUORI.

I dettagli sono in `strumenti/3_numeri_da_appunti/README.md`.

## Strumenti
Ognuno ha il suo README con cosa fa, input, output e comando.
- **Trascrizione Colab** — `trascrivi.py "audio.m4a"` -> `audio_chi_parla.txt`.
- **Collegare pagine** — `annotatore/` (solo codice, parole rare in comune + interfaccia per annotare) e `groq/` (modello che guarda la pagina, sceglie fra 10 candidate BM25, confronto con verità nota).
- **Numeri dagli appunti** — `trova_differenze.py` (tutto con un comando, vedi sopra), `controlla_stile.py pagina.png --sorgente pagina.html` (OK/FUORI su 10 numeri), `controlla_attenzione.py pagina.png` (OK/FUORI rispetto alle pagine dello studente), `quanto_urla.py`, `stile_numeri.py`, `numeri_coppie.py`.

## Risultati principali (esperimenti 39, 40, 41, pagina "cache associativo a gruppi" di Architettura)
- Tre numeri separano le pagine dello studente da quelle generate: colore forte 3,7-14,3% della pagina (generate: mediana 1,85%), zone di colore forte 1-6 (generate: mediana 6,5), tinta principale 68-99,5% del colore (generate: mediana 67,5%).
- Senza regole le pagine generate sono "arcobaleno": fino a 14 macchie di colore e tinta principale sotto il 60%; con le sue regole la tinta diventa una sola, come la sua.
- Solo 1 pagina generata su 18 sta dentro tutti e tre i suoi range: Claude + pacchetto, prova r1 (7,6% / 3 zone / 84,9%).
- Claude + pacchetto riprende tono (fondo crema, un solo colore forte che segue il caso), il disegno centrale e la barra dell'indirizzo in 3 campi in 3 prove su 3; difetti di impaginazione: senza regole 14 e 24, con pacchetto 0, 5 e 8.
- Cosa non passa ancora: un terzo della pagina resta vuoto, forme perfette invece di contorni a mano (ignorati 3/3), il testo del prof sparisce nelle etichette. Con GPT, la voce NOT TODO toglie le legende (0/5 contro 3/5 senza).

## Cosa c'è e cosa no (scelte per il repo pubblico)
- **Pagine del docente: tolte.** In `esempi/` resta solo la versione `p03_cache_associativo_senza_prof.png` (riquadro del prof oscurato); l'originale resta sul disco ed è in `.gitignore`.
- **`strumenti/3_numeri_da_appunti/esempi_numeri/suoi/Architettura_Gilberto.pdf`: tenuto.** Sono appunti dello studente (7 pagine, Architettura degli elaboratori), servono alla demo di `trova_differenze.py` come esempio di "suoi schemi". Non contengono dati personali oltre al nome; in una pagina ci sono piccoli ritagli di microistruzioni del corso.
- `esempi_numeri/generate/` contiene solo pagine generate dall'AI.
- Nessuna chiave è nel codice: la chiave Groq si passa con la variabile d'ambiente `GROQ_API_KEY`. `.env`, `*auth*.json` e `materiali.json` (percorsi locali) sono esclusi da `.gitignore`.
