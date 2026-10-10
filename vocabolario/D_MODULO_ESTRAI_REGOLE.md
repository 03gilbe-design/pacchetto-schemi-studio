# D — MODULO PER ESTRARRE UNA REGOLA (riutilizzabile)
Basato su [`docs/COME_ESTRARRE_LE_REGOLE.md`](../docs/COME_ESTRARRE_LE_REGOLE.md) (passi 3.2, 3.4, 4) e sull'esperimento 37 del tirocinio
(Claude A estrae → Claude B genera su pagina mai vista → Claude A rivede). I prompt E1, V1, R1 sono qui sotto, pronti da incollare in chat (due aggiunte segnate [+]): non serve codice.

## 0. Ingresso
- **Caso 1 (coppia):** una pagina del docente + lo schema che Gilberto ne ha ricavato, dello STESSO argomento (checklist K7). Se il suo schema copre più pagine del docente, prima si sceglie quali servono.
- **Caso 2 (appunti qualsiasi):** solo una sua pagina, senza la pagina del docente. Vale lo stesso modulo, ma si vede solo il risultato, non la trasformazione: la regola va confermata su una seconda sua pagina diversa prima del passo 3.
- **Pagina di verifica:** una pagina del docente MAI usata per ricavare regole (K3), di un'altra materia se possibile.
- Si usano solo suoi schemi veri (non fatti con l'AI, non ricevuti da altri).

## 1. Prompt E1 — estrai UNA regola (Claude A, chat nuova)
```
Ci sono due immagini: {PROF} e' una pagina del professore, {SUO} e' lo schema di studio che uno studente ha fatto a partire da quella pagina (aprile e guardale).
Che regola usa lo studente per passare dalla pagina del prof al suo schema?
Precauzioni:
- una regola sola (al massimo 2);
- generale: deve valere per qualsiasi materia, quindi niente nomi dell'argomento di queste pagine;
- deve dire PERCHE' si fa e QUANDO si applica, non descrivere le mosse che si vedono (colori, frecce, riquadri) come da copiare;
- niente stile grafico (font, colori, impaginazione) come regola;
- frase breve. [+] Al massimo 2 righe.
[+] Scrivi a parte il GRILLETTO: la condizione della pagina del professore che fa scattare la regola.
Rispondi SOLO con JSON: {"regola": "...", "grilletto": "..."}
```
Caso 2: sostituire le prime due righe con "C'e' un'immagine: {SUO} e' uno schema di studio. Quale scelta ricorrente lo guida?".

## 2. Prompt V1 — verifica: genera una pagina nuova con SOLO quella regola (Claude B, chat nuova, non sa da dove viene la regola)
```
Trasforma la pagina del professore allegata in UNA pagina di schema di studio applicando questa regola:
«{regola}»
Output: UNA pagina HTML completa (<!doctype html>...</html>), un solo file, CSS dentro <style>, A4 verticale: body largo esattamente 794px e alto 1123px, overflow hidden. Usa flex/grid e lascia che il testo vada a capo da solo (niente position:absolute per i testi). Disegni e frecce in SVG inline dentro l'HTML. Testi in italiano, niente immagini esterne, niente font esterni.

La pagina del professore e' il file immagine: {NUOVA} (aprilo e guardalo).
```
Poi: guarda la pagina a occhio (testo tagliato o sovrapposto?); per i numeri rendila in PNG e controllala con `strumenti/3_misura_stile_dai_numeri/controlla_stile.py`.

## 3. Prompt R1 — revisione (Claude A, stessa regola, vede tutte e quattro le immagini)
```
Prima hai guardato {PROF} (pagina del professore) e {SUO} (schema di studio fatto da uno studente da quella pagina) e hai estratto questa regola:
«{regola}»
Poi un altro modello ha ricevuto una pagina del professore diversa, {NUOVA}, e SOLO la tua regola, e ha prodotto {GEN}. Apri e guarda tutte e quattro le immagini.
La tua regola e' stata seguita? Il risultato fa quello che fa lo studente? La modifichi?
Se la modifichi, la nuova regola deve rispettare le stesse precauzioni:
{PRECAUZIONI}
Rispondi SOLO con JSON: {"seguita": "si'/in parte/no", "perche": "una o due frasi", "modifico": true/false, "regola": "la regola (nuova se la modifichi, altrimenti la stessa)"}
```

## 4. Ciclo (al massimo 2 giri)
E1 → V1 → R1. Se `modifico` = true: V1 con la regola nuova → R1. Dopo il secondo giro ci si ferma comunque.
- Il prompt di ogni passo si salva (file + sha256) PRIMA di vedere il risultato (CONGELATI).
- Se la risposta non è JSON (es. limite di usage) il passo si ripete; non si interpreta. In 37 il passo A2 è fallito così una volta.
- Per concludere servono almeno 5 generazioni V1 con la regola finale (K4); una sola prova è un indizio.

## 5. Criteri per accettarla nel vocabolario (checklist del tirocinio)
- K9 è una CAUSA con il suo quando (grilletto), non una mossa vista e copiata.
- K10 dentro la regola non c'è nessun esempio né nome di materia; gli esempi stanno sotto, separati.
- K11 non è una regola "del modello" (completezza, una pagina, soglie di colore, disegno intero): quelle vanno in B.
- K12 se Gilberto la riformula, vale il suo testo, parola per parola.
- K13 non è stile (font, colori, fascia): quello va in C.
- K3 confermata su una pagina mai vista; K4 almeno 5 prove, con modello e condizioni scritti.
- K1 si mostra entra → esce: pagina docente + suo schema + prompt esatto → pagina generata intera.
- Ritrovata da Gilberto su una SUA pagina diversa (il suo metodo).
- Lui guarda la pagina generata: se l'occhio si perde, la regola non basta (K6: il conteggio dei difetti non sostituisce lo sguardo).

## 6. Come classificarla
- **A (vocabolario)**: vale per qualunque materia e qualunque persona; spiega perché e quando. Si mette nella macro 1-5 più vicina; se duplica una regola esistente, si unisce a quella.
- **B (non fare)**: dice cosa evitare. GENERALE se ne dà la causa e vale per chiunque; CORREZIONE MODELLO se rincorre un difetto dei modelli; OVERFITTING se nasce da una pagina o una materia sola.
- **C (stile)**: riguarda aspetto (colori, font, tratto, impaginazione) o un'abitudine sua che lui chiama stile ("è nel mio stile, non una regola").
- In dubbio: va nella lista DA DECIDERE con una domanda sì/no.

## 7. Cosa dice 37_TEST_MANUALE_REGOLA finora (NON concluso)
- Coppia: prof cache "1) DIRETTO" (architettura_2semestre Copy.pdf p.16) | suo schema Architettura_Gilberto.pdf p.2. Pagina nuova: Amos p.46-47 (Bernoulli e binomiale).
- A1 ha estratto: «Quando una spiegazione si basa su numeri grandi o casi astratti, rifalla con un esempio in miniatura che puoi seguire passo per passo fino in fondo: con pochi elementi vedi tutto il meccanismo e capisci davvero come funziona, invece di memorizzare formule.»
- B1 generata: 4 difetti dal controllo automatico (1 testo tagliato, 3 sovrapposizioni). A2: "seguita: sì", ma la modifica («…seguendo gli stessi passaggi ma in scala ridotta…»).
- B2 non generata (limite di usage alle 05:55); MANIFEST finale non scritto. 1 prova sola: nessuna conclusione.
- Già da qui: la regola estratta coincide con una voce che Gilberto ha messo nello STILE ("un caso concreto con numeri piccoli"). Per questo il passo 6 (classificare) è obbligatorio prima di accettarla.

## 8. Estrarre in numeri (attenzione, macro 5) — deterministico, senza AI
Gli script stanno in [`strumenti/3_misura_stile_dai_numeri/`](../strumenti/3_misura_stile_dai_numeri/) (README con i comandi).
Una regola di attenzione non si estrae con un prompt: si **misura** sui suoi schemi. Il procedimento vale per appunti qualsiasi, anche senza la pagina del docente.

1. **Misura i suoi appunti.** Servono i suoi PDF o PNG a pagina intera (meglio 5 o più: i range vengono dal suo min-max) e almeno 3 pagine generate dall'AI senza regole, per vedere quali numeri le distinguono.
   ```
   python -X utf8 trova_differenze.py --suoi appunti.pdf --generate cartella_generate --out rif_MATERIA
   ```
   Fra i numeri misurati (in `rif_MATERIA/CLASSIFICA.md`, con min-max e mediana) ci sono questi 3:
   - **colore forte (% della pagina):** la stessa funzione `sat()` del grafico delle slide, in cui il corallo #FF644B conta;
   - **zone di colore forte separate;**
   - **tinta principale:** quale percentuale dei pixel colorati prende la tinta più usata.
   
   Su Architettura (6 pagine) i valori sono 3,7-14,3% (mediana 5,8), 1-6 zone (mediana 2,5) e 68-99,5% (mediana 87,6).
2. **Trasforma i numeri in frasi per il modello.** Ogni numero diventa un'istruzione che il modello può controllare mentre scrive HTML/SVG. Esempio: "corallo pieno su circa il {mediana}-{max tipico}% della pagina, cioè una fascia titolo più 1-2 evidenziazioni; il corallo in al massimo {zone} punti separati; almeno il {min}% del colore nella famiglia corallo-pesca".
   - Si usano numeri e oggetti concreti (px, quanti elementi, quali hex), non aggettivi ("poco", "calmo").
   - `trova_differenze.py` le scrive da solo in `rif_MATERIA/FRASI_PER_IL_MODELLO.md`.
3. **Controlla la pagina generata.** Prima si rende la pagina in PNG, poi:
   ```
   python -X utf8 controlla_stile.py pagina.png --sorgente pagina.html --rif rif_MATERIA/numeri.json
   ```
   - Per ogni numero stampa `OK` o `FUORI`, con il range suo e un consiglio di correzione.
   - Exit code 0 se tutto è OK, 1 se qualcosa è fuori. Senza `--rif` usa i range di Architettura.
   - Se c'è un FUORI, il consiglio torna al modello e la pagina si rigenera (al massimo 2 giri, come al passo 4).
4. **Prima di fidarti, lancialo sui suoi appunti.** Tutte le sue pagine devono uscire OK; per costruzione succede, perché i range sono il loro min-max. Poi prova una sua pagina che NON era tra quelle misurate: se esce FUORI, i range sono troppo stretti e vanno misurate più pagine.
- **Non usare "testo scuro %":** dipende dalla risoluzione del PNG (in 41 una pagina passa da 1,4% a 0,2% solo rimpicciolendola).
- Questi numeri sono **stile (C)**, non vocabolario: dicono *quanto* colore c'è, mentre il *perché* sta nella macro 5 di A.
