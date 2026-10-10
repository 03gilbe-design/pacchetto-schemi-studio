# Come estrarre le regole dai propri schemi

> Copia senza modifiche di `ESPERIMENTO_REGOLE_SCHEMI/COME_ESTRARRE_LE_REGOLE.md` del progetto di tirocinio (bozza del 09/10/2026). Nel repo il vocabolario è in `vocabolario/` (non `VOCABOLARIO_GENERALE.docx`); le cartelle `ESPERIMENTI\` citate in fondo restano sul disco dello studente, non sono pubblicate. I prompt pronti da usare sono in `vocabolario/D_MODULO_ESTRAI_REGOLE.md`.

Bozza del 09/10/2026. Descrive il metodo seguito nelle ultime settimane per ricavare un vocabolario di regole generali dai propri schemi di studio. Gli esempi citati servono solo a chiarire i passi: il metodo non dipende da nessuna materia.

## 1. Obiettivo

Ricavare dai propri schemi un **vocabolario di regole generali**: un insieme di scelte riusabili per spiegare qualunque argomento, a partire dalle pagine del docente. Il vocabolario deve poter essere usato da una persona o da un modello linguistico per costruire pagine nuove su argomenti mai visti.

Il risultato attuale è il documento *Vocabolario generale* (VOCABOLARIO_GENERALE.docx / .pdf), organizzato in sei sezioni: Cognitive offload, Transcodifica, Mappatura End-to-End con visione olistica, Il disegno, Attenzione, Il mio stile di Architettura (leggero).

## 2. Materiali di partenza

- **Schemi propri.** Solo schemi fatti davvero dallo studente: appunti a mano, pagine OneNote, schemi d'esame. Va controllato che lo siano: un PDF può sembrare proprio ed essere invece identico a materiale ricevuto da altri; alcuni schemi sono stati fatti con l'aiuto dell'AI; anche tra i propri appunti ci sono pagine fatte bene e pagine fatte male.
- **Pagine del docente.** Sono il punto di partenza da cui lo schema nasce. Senza di esse si vede solo il risultato, non la trasformazione.
- **Collegamenti.** La coppia *pagina del docente ↔ schema proprio* mostra che cosa è stato tenuto, tolto, ridotto o trasformato. Una pagina dello studente può corrispondere a più pagine del docente: prima di estrarre o generare va stabilito quali pagine del docente servono. Nelle prove, un programma ha trovato la pagina giusta tra 10 candidate in 9 casi su 9; un modello gratuito (Groq) in 5 su 9.
- **Parole dello studente.** Il prompt personale per estrarre il vocabolario, le riflessioni scritte su come fare gli schemi, le frasi dette in chat e le critiche registrate alle pagine generate. Dove possibile le regole riprendono queste parole.

## 3. Passi del metodo

### 3.1 Partire dai bisogni di chi studia

Il punto di partenza non è l'aspetto delle pagine, ma il bisogno di chi studia: in particolare la fatica della memoria di lavoro. Lo schema è comodo per chi lo guarda, non per chi lo scrive. Prima di leggere il testo del docente, lo studente si mette davanti al problema come se dovesse risolverlo lui. Una prima prova che aveva preso colori e impaginazione, saltando questo lavoro mentale, è stata giudicata banale.

### 3.2 Estrarre logiche e perché, non l'aspetto

La parte più difficile è estrarre logiche e pattern: è facile dire che lo sfondo è beige, è difficile dire il **perché**. Per ogni regola si cerca la causa, non l'effetto. Esempio: lo zoom non è una regola, nasce da *tutti i componenti* più *tanti pezzi*; trattarlo come regola sarebbe overfitting. Per ogni regola si salva anche il **grilletto**, cioè la condizione che la fa scattare (per esempio: si ridisegna lo stesso oggetto quando c'è un aspetto nuovo da mostrare). Quando una regola non vale, non si crea un'eccezione: si cerca un'altra regola su un altro piano.

### 3.3 Misurare range e frequenze

Il prompt personale chiede di trovare i range tipici (massimo e minimo, con distribuzione anche non uniforme) di:

- font e grandezze, e dove viene usato ogni font;
- numero e grandezza dei blocchi di testo;
- numero di forme, icone e immagini; varietà delle forme nei disegni;
- livello di complessità grafica, con la sua frequenza;
- palette, separata per sfondo, testo, titoli e grafiche;
- eventuale "firma" della pagina (un colore in più, una forma speciale, un disegno ripetuto);
- griglie: rapporti o multipli di un'unità base per distanze, grandezze, colori e spazi.

Le misure servono a confrontare schemi propri e pagine generate. Esempio: colore saturo intorno al 6-10% della pagina negli schemi dello studente, 18-24% nelle pagine prodotte dall'AI.

### 3.4 Separare tre contenitori

Le indicazioni raccolte vanno divise in tre gruppi, tenuti in file diversi:

1. **Regole generali**: valgono per qualunque argomento. Vanno nel vocabolario.
2. **NOT TODO**: correzioni che servono solo a contrastare i difetti tipici dei modelli ("inseguire il modello cattivo"). Esempi: riquadri in fila uno sotto l'altro, riquadri "IDEA/RICORDA", legende, emoji, testo sovrapposto, uno stile fisso copiato su ogni pagina. Stanno in un file a parte per il modello, non nel vocabolario.
3. **Stile personale**: il tono di una materia (colori, font, fondo). È un tono, non un modello: le regole vengono prima. Se lo stile entra nel prompt generale, il modello lo copia pari pari (overgeneralizing).

Vanno tolte anche le regole nate "dal modello" e non dallo studente.

### 3.5 Organizzare il vocabolario

- Prima le regole più importanti; macro-regole con una breve introduzione, poi regole numerate (N.k).
- Ogni regola: nome, descrizione, esempio sotto, grafica accanto solo se chiarisce davvero.
- Ogni regola importante deve avere la sua grafica: dove manca, chi genera tende a mettere testo al posto del disegno. La grafica deve rappresentare esattamente quella regola, senza testo dentro.
- Le formulazioni nuove proposte a partire dalle frasi dello studente si segnano a parte (per esempio in blu, numerate) e le sceglie lui; quelle approvate entrano nel testo.

### 3.6 Esempi: solo dai propri schemi, ritagliati bene

- Gli esempi vengono **solo** dagli schemi dello studente; dove non c'è un esempio certo, non si mette nessun esempio.
- Il ritaglio contiene solo ciò che serve alla regola, senza parti che non c'entrano; meglio ridisegnare l'elemento originale dal PDF che usare uno screenshot.
- Una didascalia breve dice che cosa l'esempio mostra.
- L'esempio illustra la regola, non la definisce: la regola deve reggere anche senza di esso.
- Sono utili anche esempi negativi (per esempio pagine generate dove troppi colori competono).

### 3.7 Nomi scientifici verificati

Per ogni regola si cerca il termine della letteratura, con fonte primaria (autori, anno, titolo, sede) e DOI controllato. Si indica il grado di corrispondenza: **esatta**, **parziale** o **vicina**. Esempi: *cognitive offloading* (Risko e Gilbert, 2016) corrisponde in modo esatto alla prima macro-regola; *dual coding* (Paivio, 1971) solo in parte. Le etichette che in letteratura non esistono (per esempio "isomorfismo spaziale") si presentano come etichette proprie, collegate ai termini veri. Vanno scartati i falsi amici: termini esistenti che significano un'altra cosa.

### 3.8 Errori tipici emersi

- **Overfitting**: regole costruite su un singolo esempio o su un effetto invece che su una causa (lo zoom; una regola "una domanda per ogni ruolo" poi tolta).
- **Regole o frasi inventate**: formulazioni che non venivano dallo studente, eliminate in revisione.
- **Esempi fuori posto**: presi da un file sbagliato (non suo) o ritagliati con parti che non c'entrano.
- **Troppi colori**: pagine "arlecchino" dove tutto richiama l'attenzione e nulla emerge; colori nati senza volerlo (sfumature, sovrapposizioni).
- **Troppi livelli** di enfasi e di dettaglio; etichette sparse e spezzate ("grana sul piatto").
- **Trenino**: riquadri in fila in cui inizio e fine non si toccano.
- **Troppo materiale in ingresso**: dare al modello l'intera tavola delle grafiche peggiora il risultato; meglio la grafica giusta per la regola.

## 4. Come si valida

- **Prima, non dopo.** Una regola decisa guardando una pagina si conferma su una pagina **mai vista**. I prompt usati nelle prove si congelano (file con hash e data) prima di vedere i risultati.
- **Test con i modelli.** Stessa pagina del docente, chat nuova per ogni prova, confronto *senza regole / con regole*. Almeno cinque prove per prompt: con due i numeri oscillano troppo. Un controllo automatico conta i difetti di impaginazione (testo sovrapposto, tagliato), ma non sostituisce lo sguardo: il conteggio e il giudizio a occhio possono non coincidere.
- **Differenze tra modelli.** Le stesse regole non rendono allo stesso modo su tutti i modelli (nelle prove, la regola "un disegno intero" funzionava con Claude e peggiorava GPT): il risultato va annotato per modello.
- **Isolamento.** Al modello si dà solo il pacchetto della singola prova, mai le soluzioni: in un caso la soluzione era nel pacchetto e il modello l'ha copiata.
- **Entra → esce.** Si mostra sempre la pagina del docente e il prompt esatto accanto alla pagina generata intera.
- **Lui guarda.** Il giudizio finale è dello studente: guarda la pagina a colpo d'occhio (se l'occhio si perde, è sbagliata), dice che cosa non va con un'immagine concreta, ne ricava la causa, la ritrova su un proprio schema diverso, salva il grilletto. Criteri ulteriori: con pochi pezzi la pagina dice tutto? coprendo il testo, la grafica comunica da sola?
- **Registro.** Tutte le pagine generate sono ricostruibili da un registro deterministico (prompt inviato, prompt atteso, immagini).

## 5. Prossimi passi

1. Mostrare ogni frase dello stile personale con la miniatura di un esempio vero accanto.
2. Collegare ogni regola generale a ritagli ben fatti dei propri schemi, partendo dagli schemi d'esame di Basi di Dati.
3. Verificare che cosa manca se si danno al modello solo poche regole.
4. Comprimere regole generali, NOT TODO e stile in un file da dare al modello insieme al vocabolario.
5. **Test definitivo**, in due parti:
   - a) capacità di **estrarre** regole, usando i collegamenti tra PDF del docente e schemi propri: un Claude estrae, un secondo Claude genera, si mostrano i risultati, si corregge e si ripete (numero di immagini e regole per giro da decidere);
   - b) **Claude e GPT gratuiti**, da browser con l'account dello studente, sul vocabolario finale.

## Appendice: esperimenti svolti

Cartelle in `ESPERIMENTI\`: 1_COLLEGARE_tu_con_chat_gratis, 2_ESTRARRE_REGOLE_noi, 3_GENERARE_PAGINA_noi, 4_NOTTE_genera_pagine_e_regole_dimenticate, 5_STILE_in_numeri, 6_MODELLO_piu_intelligente_e_grande_regola, 7_REGOLE_GRANDI_rigenera, 8_INTUISCE_con_hint, 9_SFIDA_meno_bottoni, 10_DEFINIZIONE_e_QUANTO_URLA, 11_SFIDA_frase_corta, 12_SMENTITORE, 13_FRASE_che_evolve, 14_PRINCIPI_viene_da_se, 15_E3_numero_regole_E4_struttura, 16_E1b_principio_MAPPA, 17_GENERAZIONE_FINALE, 18_HTML_e_CONTROLLO, 18b_GEMINI_isolato, 19_CHAT_GPT_VERA, 24_COLONNA2, 25_MODELLO_vs_REGOLE, 26_PAGINA_MAI_VISTA, 27_LONTANO_STATISTICA, 28_GPT_REGOLE_ESTRATTE, 29_CHEBYSHEV, 30_QUARTILI, 31_BAYES, 32_BINOMIALE, 33_COLLEGA_GROQ, 35_STILE_MINIATURE.

Fonti di questo documento: `ESPERIMENTI\PIANO\` (STATO_VOCABOLARIO_0910, PIANO_GOAL_0910_NOTTE, CRITICHE_08-10, CONGELATI, CONSEGNA_PIANO, NOT_TODO_MODELLO, NOMI_SCIENTIFICI_REGOLE), `ESPERIMENTI\CRITICHE_GILBERTO.md`, `LAB_FONDAMENTI\PROMPT_JEANS_VOCABOLARIO.txt`, le riflessioni e le frasi dello studente, VOCABOLARIO_GENERALE.pdf.
