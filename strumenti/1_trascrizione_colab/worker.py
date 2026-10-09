# worker.py - gira DENTRO Colab (GPU). Legge /content/audio.*, scrive /content/risultato_chi_parla.txt
import os, sys, glob, subprocess, time, tarfile
def log(t): print(time.strftime("%H:%M:%S"), t, flush=True)
AUDIO = glob.glob("/content/audio.*")[0]
CFG = dict(l.split("=", 1) for l in open("/content/cfg.txt", encoding="utf-8").read().splitlines() if "=" in l)
log("installo librerie...")
subprocess.run([sys.executable, "-m", "pip", "-q", "install", "faster-whisper", "pyannote.audio>=4"], check=True)
import ctypes, torch
for lib in glob.glob(os.path.join(os.path.dirname(torch.__file__), "..", "nvidia", "cudnn", "lib", "libcudnn*.so*")):
    try: ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)
    except OSError: pass

from faster_whisper import WhisperModel, BatchedInferencePipeline
log(f"trascrivo con {CFG['MODELLO']}...")
wm = WhisperModel(CFG["MODELLO"], device="cuda", compute_type="float16")
segs, info = BatchedInferencePipeline(wm).transcribe(AUDIO, language="it", batch_size=8, beam_size=5, vad_filter=True,
                                                     word_timestamps=True, hotwords=CFG.get("PAROLE") or None)
out = [[s.start, s.end, s.text.strip(), [[w.start, w.end, w.word] for w in (s.words or [])]] for s in segs]
log(f"trascrizione: {len(out)} frasi, {info.duration/60:.1f} min audio")
del wm; torch.cuda.empty_cache()

turni = []
try:
    tarfile.open("/content/pyannote_cache.tar").extractall("/root/.cache/huggingface/hub", filter="data")
    os.environ["HF_HUB_OFFLINE"] = "1"                   # modelli caricati dal PC: niente token
    from pyannote.audio import Pipeline
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", AUDIO, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    wav = torch.from_numpy(np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0)[None]
    dia = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1").to(torch.device("cuda"))
    nv = int(CFG.get("VOCI") or 0)
    res = dia({"waveform": wav, "sample_rate": 16000}, **({"num_speakers": nv} if nv else {"min_speakers": 1, "max_speakers": 6}))
    ann = getattr(res, "exclusive_speaker_diarization", None) or getattr(res, "speaker_diarization", None) or res
    turni = sorted([t.start, t.end, spk] for t, _, spk in ann.itertracks(yield_label=True))
    log(f"chi parla: {len({t[2] for t in turni})} voci")
except Exception as e:
    log(f"CHI PARLA NON RIUSCITO ({str(e)[:300]}) -> solo testo")

def hms(s): return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d}"
def parlante(a, b):
    ov = {}
    for ts, te, spk in turni:
        if ts >= b: break
        o = min(b, te) - max(a, ts)
        if o > 0: ov[spk] = ov.get(spk, 0) + o
    if ov: return max(ov, key=ov.get)
    mid = (a + b) / 2
    return min(turni, key=lambda x: min(abs(mid - x[0]), abs(mid - x[1])))[2]
righe, ultimo, buf = [], None, []
for a, b, frase, parole in out:
    if not turni:
        righe.append(f"[{hms(a)}] {frase}"); continue
    for wa, wb, w in (parole or [[a, b, " " + frase]]):
        p = parlante(wa, wb)
        if p != ultimo:
            if buf: righe.append("".join(buf).strip())
            buf = []; righe.append(f"\n[{hms(wa)}] {p}"); ultimo = p
        buf.append(w)
if buf: righe.append("".join(buf).strip())
open("/content/risultato_chi_parla.txt", "w", encoding="utf-8").write("\n".join(righe).strip() + "\n")
log("FATTO")
