# annota.py - interfaccia locale per annotare i propri schemi: pagina a sinistra (selezione con il mouse), commenti a destra.
# Avvio: python annota.py   -> apre il browser su http://127.0.0.1:8777
import http.server, io, json, os, socketserver, sys, urllib.parse, webbrowser
H = os.path.expanduser('~'); QUI = os.path.dirname(os.path.abspath(__file__))
MAT = (sys.argv[1] if len(sys.argv) > 1 else 'architettura')  # cartella materiale: architettura | linguaggi | ...
CONF = json.load(io.open(os.path.join(QUI, 'materiali.json'), encoding='utf-8'))[MAT]
PORTA = CONF['porta']
PAGINE_DIR = os.path.join(QUI, MAT, 'pagine')
DATI = os.path.join(QUI, MAT, 'annotazioni.json')
PAGINE = sorted(f for f in os.listdir(PAGINE_DIR) if f.endswith('.png') and ('_p' in f))


def leggi():
    return json.load(io.open(DATI, encoding='utf-8')) if os.path.exists(DATI) else {}


class App(http.server.SimpleHTTPRequestHandler):
    def _invia(self, corpo, tipo='application/json'):
        b = corpo if isinstance(corpo, bytes) else corpo.encode('utf-8')
        self.send_response(200); self.send_header('Content-Type', tipo); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        r = urllib.parse.urlparse(self.path)
        if r.path in ('/', '/index.html'): return self._invia(io.open(os.path.join(QUI, 'annota.html'), 'rb').read(), 'text/html; charset=utf-8')
        if r.path == '/pagine': return self._invia(json.dumps(PAGINE))
        if r.path == '/dati': return self._invia(json.dumps(leggi()))
        if r.path == '/fonti': return self._invia(io.open(os.path.join(QUI, MAT, 'fonti', 'mappa.json'), encoding='utf-8').read() if os.path.exists(os.path.join(QUI, MAT, 'fonti', 'mappa.json')) else '{}')
        if r.path.startswith('/fonte/'):
            f = os.path.basename(urllib.parse.unquote(r.path[7:])); g = os.path.join(QUI, MAT, 'fonti', f)
            if os.path.exists(g): return self._invia(io.open(g, 'rb').read(), 'image/png')
            self.send_error(404); return
        if r.path.startswith('/img/'):
            f = os.path.basename(urllib.parse.unquote(r.path[5:]))
            if f in PAGINE: return self._invia(io.open(os.path.join(PAGINE_DIR, f), 'rb').read(), 'image/png')
        self.send_error(404)

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); corpo = json.loads(self.rfile.read(n) or b'{}')
        d = leggi(); d[corpo['pagina']] = corpo['note']
        io.open(DATI, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
        self._invia(json.dumps({'ok': True, 'pagine_annotate': len(d), 'note_totali': sum(len(v) for v in d.values())}))

    def log_message(self, *a): pass


if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORTA), App) as s:
        print(f'Annotatore [{MAT}] su http://127.0.0.1:{PORTA}  (CTRL+C per chiudere) ·', len(PAGINE), 'pagine ·', DATI)
        webbrowser.open(f'http://127.0.0.1:{PORTA}'); s.serve_forever()
