# Vocabolario di stile per generare schemi di studio (tirocinio UniVR)

Tirocinio di Informatica (UniVR): dai miei schemi di studio estraggo un **vocabolario di regole** (cosa fare, cosa non fare, stile, numeri misurabili) e lo do a un modello (Claude/GPT) perché generi schemi nuovi nel mio stile. Gli strumenti misurano quanto la pagina generata somiglia ai miei schemi e collegano ogni schema alla pagina del prof da cui nasce.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/03gilbe-design/vocabolario-schemi-studio/blob/main/Demo_Pacchetto_Schemi_Colab.ipynb)

![Cosa trovi nelle cartelle](img/cartelle.png)

![Come funziona](img/come_funziona.png)

- **Prova in 1 clic:** bottone Colab qui sopra. Niente chiavi, gira sugli esempi inclusi.
- **Usa il vocabolario:** scarica `per_GPT.zip` dalla Demo e dallo a GPT o Claude in chat, poi la pagina del prof.
- **Scarica una versione vecchia:** tab *Commits* → *Browse files* → *Code* → *Download ZIP*.

| Cartella | Cosa c'è |
|---|---|
| `esempi_schemi_e_pagine_generate/` | appunti e pagine di prova |
| `vocabolario/` | le regole da dare al modello |
| `strumenti/` | 1 trascrivi lezioni · 2 collega schema a pagina prof · 3 misura stile dai numeri |

Spiegazioni complete e risultati: [docs/DETTAGLI.md](docs/DETTAGLI.md)
