# PACCHETTO — cosa dare al modello, in che ordine
1. **A_VOCABOLARIO.md**, solo le regole (macro 1-5, fino alla riga `---`): prima, perché le regole vengono prima dello stile. ~5.325 caratteri ≈ 1.330 token.
2. **B_NON_FARE.md**, solo le 5 voci [GENERALE] (1, 2, 6, 10, 11), una riga ciascuna, senza motivi e fonti. ~370 caratteri ≈ 90 token.
3. **C_STILE.md**, sezione 1 (sue frasi) + elenco degli hex della palette + sezione 6 (cosa ne consegue), presentati come tono. ~2.590 caratteri ≈ 650 token.
4. Totale pacchetto: ~8.280 caratteri ≈ **2.070 token** (caratteri/4). Le 5 correzioni della domanda 5 di B (voci 3, 4, 7, 8, 9) aggiungerebbero ~150 caratteri ≈ 40 token, solo se la risposta è sì.
5. Restano FUORI: gli esempi (fondo di A e di C), le tabelle numeriche di C, le voci [OVERFITTING], tutto D (D serve a noi per estrarre regole nuove, non al modello che genera).
6. Ultima, la pagina del docente; il prompt resta minimale e neutro (K15). Prima di usarlo: rispondere alle 7 domande "DA DECIDERE" in fondo a B.
