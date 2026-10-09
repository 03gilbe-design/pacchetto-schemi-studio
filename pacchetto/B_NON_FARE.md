# B — COSE DA NON FARE (con classificazione)
Testi delle voci copiati da `fai_word_regole.py` (DA_FARE, DA_NON) = `PIANO/NOT_TODO_MODELLO.md`; voci 10-11 da `PIANO/regole.json`;
voci 12-17 = regole TOLTE dal vocabolario (testo da `regole.json`), messe qui solo per decidere dove stanno.
Classi: **[GENERALE]** vale per chiunque, si dà al modello · **[CORREZIONE MODELLO]** rincorre un difetto dei modelli: utile, ma non è una regola di Gilberto ·
**[OVERFITTING]** troppo legata a una pagina, a una materia o a un esperimento.
Fonte G = parole di Gilberto; CHAT = proposta di una chat; CC = aggiunta da Claude Code.

## Da fare (NOT TODO, sezione "Da fare")
1. **[GENERALE]** il significato di un colore può restare locale: serve a seguire un elemento attraverso i passaggi di una stessa dimostrazione, senza valere per l'intero documento
   — motivo: precisa la 5.4 (stesso colore = collegamento) e l'ha ritrovata sulle sue pagine; i modelli invece fissano un colore per tutto il foglio.
   — fonte: commento suo "todo per AI" (fai_word_regole.py, 09/10); zone_grigie_notte/RITROVATE_claude.md n.27 ("L'AI dice invece 'uguali in tutto il foglio'"). → vedi DA DECIDERE 1.

## Da non fare (NOT TODO)
2. **[GENERALE]** riquadri in fila uno sotto l'altro (trenino)
   — motivo: in fila inizio e fine non si toccano: è il contrario della macro 3 (percorso unico da A a B).
   — fonte G: "NIENTE TRENINO: non mettere riquadri ordinati in fila" (REGOLE_GRANDI, regole dette da lui); CRITICHE_GILBERTO C "trenino di riquadri".
3. **[CORREZIONE MODELLO]** box "IDEA"/"RICORDA"
   — motivo: è il riquadro "da manuale" che i modelli aggiungono di default; nei suoi schemi non c'è.
   — fonte CHAT (regole.json N1b: "aggiungono testo da manuale (box IDEA…)", OBIETTIVI_E_ZONE_GRIGIE_notte).
4. **[CORREZIONE MODELLO]** passi 1-2-3 come struttura
   — motivo: impaginazione a passi numerati tipica dei modelli; il caso generale è già coperto dalla voce 2 (trenino).
   — fonte CHAT (regole.json N1b, segnata "inventato: passi numerati 1-2-3").
5. **[CORREZIONE MODELLO]** spiegazioni "in generale": sempre il caso concreto
   — motivo: i modelli spiegano il meccanismo in astratto invece di seguire un caso; ma "un caso concreto con numeri piccoli" Gilberto l'ha messo nello STILE ("è nel mio stile, non una regola").
   — fonte CHAT (regole.json N3: giudici AI); vicina alla sua A8 "non spiegarlo, MOSTRARLO" (CRITICHE_GILBERTO). → vedi DA DECIDERE 2.
6. **[GENERALE]** legende: se serve la legenda, va cambiato il disegno
   — motivo: dice la causa (il disegno non si capisce da solo, 4.2), non solo il divieto; vale per chiunque.
   — fonte G: "No leggende" (Telegram 08/10 sera, CRITICHE_GILBERTO C4).
7. **[CORREZIONE MODELLO]** emoji
   — motivo: abitudine dei modelli; nessuno schema a mano le usa, non è una scelta di metodo.
   — fonte G: "Vietati emojis" (Telegram 08/10 sera, C4).
8. **[CORREZIONE MODELLO]** testo sovrapposto ad altro testo o ai disegni
   — motivo: è un difetto tecnico dell'impaginazione generata (SVG a coordinate fisse), non una scelta di stile.
   — fonte G: "correzione modello low: no testo sovrapposto" (Desktop\altro promtp.txt, regole.json N5); CRITICHE_08-10 #18.
9. **[CORREZIONE MODELLO]** uno stile fisso copiato pari pari su ogni pagina
   — motivo: con il blocco STILE nel prompt il modello lo copia identico (overgeneralizing); per questo C_STILE è scritto come tono.
   — fonte G: CRITICHE_08-10 #1 "Niente blocco STILE fisso… Il modello lo copia pari pari"; CONGELATI 21:51 ("togli stile a Claude").

## In regole.json ma non nel NOT TODO
10. **[GENERALE]** niente etichette sparse a capo ("grana sul piatto")
    — motivo: troppe etichette spezzate disperdono l'occhio; vale per chiunque (macro 5).
    — fonte G: "un sacco di etichette a capo in grigio… sembra grana su un piatto" (CRITICHE_GILBERTO A13).
11. **[GENERALE]** niente testo minuto su tre livelli di grigio
    — motivo: troppi livelli di enfasi; la macro 5 vuole pochi livelli ben distinti.
    — fonte G: "testi piccoli in grigio, grafici grigi, poi testo piccolo in nero…" (CRITICHE_GILBERTO A7).

## Regole tolte dal vocabolario (dove stanno?)
12. **[CORREZIONE MODELLO]** P8 UN DISEGNO INTERO: la pagina è UN solo disegno da A a B che contiene tutto il caso
    — motivo: funziona con Claude, peggiora GPT (Bayes 29, 40 difetti; CRITICHE_08-10 #11): dipende dal modello.
    — fonte G: "un disegno intero è una cazzata" (chat 09/10, tolto dal Word).
13. **[CORREZIONE MODELLO]** P2 UNA PAGINA: tutto deve stare in una pagina e leggersi a colpo d'occhio
    — motivo: è il formato dell'esperimento (A4 HTML), non un modo di fare schemi.
    — fonte G: CRITICHE_08-10 #9 "regole del modello, non sue".
14. **[CORREZIONE MODELLO]** P7 GRAFICHE LIBERE: non restare bloccato alle forme base
    — motivo: spinge il modello a disegnare di più; Gilberto: "non è un modo di fare robe".
    — fonte G: CRITICHE_08-10 #9.
15. **[CORREZIONE MODELLO]** PR4 segna cosa devi GENERARE perché il prof non lo dà
    — motivo: serve a noi per vedere il testo inventato (checklist K8), non al lettore dello schema.
    — fonte G: CRITICHE_08-10 #9.
16. **[OVERFITTING]** P1 COMPLETEZZA: tutti i componenti del caso, dal primo all'ultimo passaggio
    — motivo: nata dalle pagine di Architettura (tutti i chip, tutti i bit); Gilberto: "semi overfitting".
    — fonte G: CRITICHE_08-10 #9. La seconda metà ("ogni ingresso ha il suo arrivo visibile", A16) è più generale → DA DECIDERE 4.
17. **[OVERFITTING]** M2 colore saturo su circa il 10% della pagina
    — motivo: numero misurato su 6 pagine di una sola materia (lui 6-10%, AI 18-24%); come soglia fissa per il modello è una misura, non una causa. La causa è già in 5.2/5.3.
    — fonte G: "è un arlecchino" (CRITICHE_GILBERTO C); CRITICHE_08-10 #9 la elenca tra le regole del modello. → DA DECIDERE 3.
18. **[OVERFITTING]** "una domanda per ogni ruolo" (MAR = DOVE?, MDR = COSA?)
    — motivo: nata da una sola pagina (microistruzioni); tolta dal Word come overfitting. Il principio generale sopravvive in 5.4 (stessa forma, colore dietro = ruolo).
    — fonte: STATO_VOCABOLARIO_0910 riga 83 ("domanda per ruolo tolta=overfitting"); CRITICHE_GILBERTO A6.
19. **[OVERFITTING]** lo zoom come regola
    — motivo: è un effetto, non una causa: nasce da "tutti i componenti" + "tanti pezzi".
    — fonte G: "zoom è overfitting, non logica" (CRITICHE_GILBERTO C, B3). Resta solo come voce di STILE ("zoom sul dettaglio").

## Conteggio
| | GENERALE | CORREZIONE MODELLO | OVERFITTING | totale |
|---|---|---|---|---|
| NOT TODO (voci 1-9) | 3 (1, 2, 6) | 6 (3, 4, 5, 7, 8, 9) | 0 | 9 |
| regole.json (10-11) | 2 (10, 11) | 0 | 0 | 2 |
| tolte dal vocabolario (12-19) | 0 | 4 (12, 13, 14, 15) | 4 (16, 17, 18, 19) | 8 |
| **tutte** | **5** | **10** | **4** | **19** |

---

## DA DECIDERE CON GILBERTO: overfitting accettato o no?
1. **Colore locale** (voce 1): la mettiamo nel vocabolario come seconda frase della 5.4? **sì / no**
2. **"Sempre il caso concreto"** (voce 5): la diamo al modello come divieto, anche se il caso concreto con numeri piccoli l'hai messo nello stile ("è nel mio stile, non una regola")? **sì / no**
   (nota: in 37_TEST_MANUALE_REGOLA il modello, guardando una sola coppia prof | tuo schema, ha estratto proprio questa: "rifalla con un esempio in miniatura").
3. **Colore saturo ~10%** (voce 17): diamo il numero al modello come tetto, sapendo che viene da 6 pagine di Architettura? **sì / no**
4. **Completezza** (voce 16): teniamo solo "ogni ingresso ha il suo arrivo visibile" come regola generale? **sì / no**
5. **Correzioni modello** (voci 3, 4, 7, 8, 9): le diamo comunque al modello, in un blocco separato chiamato "correzioni per il modello" (overfitting accettato, perché sono difetti dei modelli e non regole tue)? **sì / no**
6. **Zoom nello stile** (voce 19): "zoom sul dettaglio" resta nella sezione stile, anche se come regola era overfitting? **sì / no**
7. **La parola "studente"** nel vocabolario (intro macro 1, corsivo "il bisogno dello studente che studia"): resta nel testo dato al modello, anche se la checklist K15 dice di non nominarlo nel prompt? **sì / no**
