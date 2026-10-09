"""Groq (API gratis, OpenAI-compatibile) per l'esperimento schemi. Chiave dalla variabile d'ambiente GROQ_API_KEY (mai stampata).
python groq.py            -> elenca i modelli
chiama_groq(prompt, png, modello) -> testo della risposta"""
import base64
import json
import os
import urllib.error
import urllib.request

URL = "https://api.groq.com/openai/v1/"


def chiave():
    k = os.environ.get("GROQ_API_KEY")
    if not k: raise SystemExit("manca la variabile d'ambiente GROQ_API_KEY")
    return k


def _req(path, dati=None, timeout=300):
    r = urllib.request.Request(URL + path, data=json.dumps(dati).encode() if dati else None,
                               headers={"Authorization": "Bearer " + chiave(), "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=timeout))


def chiama_groq(prompt, png, modello, max_tokens=5000):
    """png=None -> solo testo. Piano gratis: 8000 token/min TOTALI (prompt+immagine+risposta): su 429 aspetta 70 s e riprova una volta."""
    cont = [{"type": "text", "text": prompt}]
    if png: cont.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(open(png, "rb").read()).decode()}})
    dati = {"model": modello, "max_tokens": max_tokens, "temperature": 0.7, "messages": [{"role": "user", "content": cont}]}
    import re, time
    for tentativo in range(8):  # 429: aspetta quanto dice Groq ("try again in 2m43s"; limite giornaliero = finestra mobile), poi riprova
        try:
            d = _req("chat/completions", dati); break
        except urllib.error.HTTPError as e:
            if e.code != 429 or tentativo == 7: raise
            m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", e.read().decode(errors="ignore"))
            time.sleep(min(900, (int(m.group(1) or 0) * 60 + float(m.group(2)) + 5) if m else 70))
    return d["choices"][0]["message"]["content"]


if __name__ == "__main__":
    for m in sorted(x["id"] for x in _req("models")["data"]): print(m)
