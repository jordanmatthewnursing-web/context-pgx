"""Local-only fault fixtures; never packaged into the Site."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import time
ROOT=Path(__file__).resolve().parents[1]/'dist'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def do_GET(self):
  parts=self.path.split('/')
  mode=parts[1];self.path='/'+'/'.join(parts[2:])
  if self.path in ['/review.json','/changes.json'] and mode=='supplement-slow':time.sleep(12)
  if self.path=='/evidence.json' and mode=='missing':self.send_error(503);return
  if self.path=='/changes.json' and mode=='changes-missing':self.send_error(503);return
  if self.path=='/review.json' and mode=='review-missing':self.send_error(503);return
  if self.path=='/evidence.json' and mode=='tampered':
   raw=(ROOT/'evidence.json').read_bytes()+b' '
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw);return
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',4183),Handler).serve_forever()
