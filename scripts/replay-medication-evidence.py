"""Verify captured guideline bytes and regenerate the educational medication catalog."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def reproduce(root):
 root=Path(root);raw=(root/'manifest.json').read_bytes();data=json.loads(raw)
 if data['schemaVersion']!=1:raise ValueError('Unsupported catalog schema')
 sources={}
 for s in data['sources']:
  path=(root/s['file']).resolve()
  if root.resolve() not in path.parents:raise ValueError('Source path escapes capture')
  b=path.read_bytes()
  if len(b)!=s['bytes'] or hashlib.sha256(b).hexdigest()!=s['sha256']:raise ValueError('Guideline checksum mismatch')
  if s['id'] in sources:raise ValueError('Duplicate guideline')
  sources[s['id']]=s
 ids=set()
 for m in data['medications']:
  if m['id'] in ids:raise ValueError('Duplicate medication')
  ids.add(m['id'])
  if m['sourceId'] not in sources:raise ValueError('Uncaptured medication source')
  if m['gene'] not in ['CYP2C19','SLCO1B1','DPYD']:raise ValueError('Unsupported gene')
 payload={'catalogVersion':data['catalogVersion'],'manifestSha256':hashlib.sha256(raw).hexdigest(),'sources':sources,'medications':data['medications']}
 return '// Generated from research/medication-evidence; source summaries are curated, not machine-validated clinical claims.\nexport const MEDICATION_CATALOG='+json.dumps(payload,separators=(',',':'))+';\n'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();out=reproduce(ROOT/'research/medication-evidence');dest=ROOT/'dist/medication-catalog.mjs'
 if a.check:
  if dest.read_text()!=out:raise SystemExit('Medication catalog differs from captured manifest')
 else:dest.write_text(out)
 print('Medication guideline hashes and catalog references verified.')
