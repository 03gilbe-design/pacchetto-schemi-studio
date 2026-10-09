# trascrivi.py - dal PC: audio locale -> Colab GPU (CLI in WSL) -> <audio>_chi_parla.txt accanto all'audio.
# Uso: python trascrivi.py "C:\...\audio.m4a" [--voci N] [--parole "a, b"] [--modello large-v3]
import argparse, os, subprocess, sys, tarfile, glob, time
QUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("--voci", default="")
ap.add_argument("--parole", default="Gilberto"); ap.add_argument("--modello", default="large-v3")
a = ap.parse_args()
AUDIO = os.path.abspath(a.audio)
if not os.path.isfile(AUDIO): sys.exit(f"audio non trovato: {AUDIO}")
OUT = os.path.splitext(AUDIO)[0] + "_chi_parla.txt"
S = "trascr"

def wslp(p): return subprocess.run(["wsl", "-e", "wslpath", "-a", p.replace("\\", "/")], capture_output=True, text=True).stdout.strip()
def colab(*args, t=None):
    cmd = "~/.local/bin/colab " + " ".join(f"'{x}'" for x in args) + " </dev/null"
    r = subprocess.run(["wsl", "-e", "bash", "-lc", cmd], text=True, encoding="utf-8", errors="replace", timeout=t)
    return r.returncode

TAR = os.path.join(QUI, "pyannote_cache.tar")               # modelli pyannote del PC (niente token HF)
if not os.path.isfile(TAR):
    hub = os.path.expanduser("~/.cache/huggingface/hub")
    with tarfile.open(TAR, "w") as t:
        for d in glob.glob(os.path.join(hub, "models--pyannote--*")) + glob.glob(os.path.join(hub, "models--*wespeaker*")):
            t.add(d, arcname=os.path.basename(d))
CFG = os.path.join(QUI, "cfg.txt")
open(CFG, "w", encoding="utf-8").write(f"MODELLO={a.modello}\nVOCI={a.voci}\nPAROLE={a.parole}\n")

t0 = time.time()
print("apro sessione Colab T4...", flush=True)
if colab("new", "-s", S, "--gpu", "T4", t=600) != 0: sys.exit("sessione Colab non creata (login scaduto? quota GPU finita?)")
try:
    ext = os.path.splitext(AUDIO)[1]
    for src, dst in ((AUDIO, f"/content/audio{ext}"), (TAR, "/content/pyannote_cache.tar"),
                     (CFG, "/content/cfg.txt"), (os.path.join(QUI, "worker.py"), "/content/worker.py")):
        print("carico", os.path.basename(src), flush=True)
        if colab("upload", "-s", S, wslp(src), dst, t=1800) != 0: sys.exit(f"upload fallito: {src}")
    colab("exec", "-s", S, "-f", wslp(os.path.join(QUI, "lancia.py")), t=6 * 3600)
    if colab("download", "-s", S, "/content/risultato_chi_parla.txt", wslp(OUT), t=600) != 0 or not os.path.isfile(OUT):
        sys.exit("risultato non scaricato: guarda l'output sopra")
    print(f"OK {OUT}  ({(time.time()-t0)/60:.1f} min)")
finally:
    colab("stop", "-s", S, t=300)                           # sempre: non sprecare quota GPU
