# lancia.py - eseguito nel kernel Colab: avvia worker.py in un processo nuovo (pip aggiorna numpy: il kernel ha già quello vecchio)
import subprocess, sys
p = subprocess.Popen([sys.executable, "-u", "/content/worker.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for riga in p.stdout:
    if "Warning" not in riga and "warn(" not in riga: print(riga, end="", flush=True)
p.wait()
