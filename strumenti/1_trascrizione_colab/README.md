# 1. Trascrizione su Colab (Whisper large-v3 + chi parla)

**Cosa fa:** trascrive un audio (lezione del prof, call di tirocinio) su una GPU T4 di Google Colab, comandata dal PC con il Colab CLI. Whisper large-v3 (faster-whisper) fa il testo, pyannote dice chi parla.

**Input:** un file audio locale (`.m4a`, `.mp3`, `.wav`, ...).
**Output:** `<audio>_chi_parla.txt` accanto all'audio, righe `[hh:mm:ss] SPEAKER_xx` + testo. Se pyannote non parte, esce solo il testo con i tempi.

**Comando (dal PC, Windows + WSL con il Colab CLI già loggato in `~/.local/bin/colab`):**
```
python trascrivi.py "C:\percorso\audio.m4a" --parole "nomi, sigle" [--voci N] [--modello large-v3]
```
- `--parole`: nomi propri e sigle da scrivere giusti (hotwords di Whisper).
- `--voci`: quante persone parlano, se lo sai (omesso = 1-6 automatico).
- Modello più veloce: `--modello deepdml/faster-whisper-large-v3-turbo-ct2`.

**File:**
- `trascrivi.py` (gira sul PC): apre la sessione Colab T4, carica audio + `worker.py` + modelli pyannote, lancia, scarica il risultato, chiude **sempre** la sessione.
- `lancia.py` (gira nel kernel Colab): avvia `worker.py` in un processo nuovo.
- `worker.py` (gira in Colab): trascrizione + diarizzazione, scrive `/content/risultato_chi_parla.txt`.

**Nota modelli pyannote:** `trascrivi.py` impacchetta in `pyannote_cache.tar` i modelli pyannote già scaricati sul PC (`~/.cache/huggingface/hub`), così in Colab non serve un token Hugging Face. Per scaricarli la prima volta serve accettare le condizioni dei modelli `pyannote/speaker-diarization-3.1` su Hugging Face. Il `.tar` (circa 60 MB) **non** è nel repo (`.gitignore`).

**Per le lezioni Panopto UniVR** il testo esiste già: dalla pagina del player si può scaricare l'SRT ufficiale (`/Panopto/Pages/Transcription/GenerateSRT.ashx?id=<sessionId>&language=21`, 21 = italiano). Questo strumento serve quando l'SRT non c'è o per le registrazioni proprie.
