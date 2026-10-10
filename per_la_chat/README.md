# Per la chat: 2 file + la pagina del prof + il prompt

Funziona con ChatGPT, Claude o Gemini, anche gratis. Non serve Colab né un account Google.

1. **Scarica** questi due file (aprili e premi *Download raw file*):
   - [PACCHETTO_MODELLO.md](PACCHETTO_MODELLO.md): le regole
   - [FRASI_PER_IL_MODELLO.md](FRASI_PER_IL_MODELLO.md): i numeri della pagina
2. **Allegali in chat** insieme alla **pagina del prof** (PDF o foto).
3. **Incolla** il testo di [PROMPT.txt](PROMPT.txt).
4. Se vedi un errore, scrivi quale regola non ha rispettato e «correggi solo questo» (video 5 e 7 del README).

Niente zip: non tutte le chat aprono i .zip, i file singoli vanno bene ovunque.

**Da dove vengono:**
- `PACCHETTO_MODELLO.md`: copia identica di [vocabolario/completo/PACCHETTO_MODELLO.md](../vocabolario/completo/PACCHETTO_MODELLO.md) (esperimento 38, `38_PACCHETTO_MODELLO/FINALE/`): regole A, da fare/non fare B, stile C, figura E, numeri.
- `FRASI_PER_IL_MODELLO.md`: le fonti sono scritte in cima al file (`trova_differenze.py` + esperimento 41).
- `PROMPT.txt`: il prompt `PROMPT_PER_GPT.txt` della Demo Colab, con i soli 3 file della ricetta.
- `PROMPT_SENZA_REGOLE.txt`: serve solo per fare il TUO vocabolario (passo 2 del README): il prompt `prompt_SENZA.txt` dell'esperimento 40, da cui vengono le pagine `claude_SENZA` di esempio.

Le frasi sono quelle di Gilberto (Architettura). Per le tue: Demo Colab, punto 4, oppure `strumenti/3_misura_stile_dai_numeri/trova_differenze.py`.
