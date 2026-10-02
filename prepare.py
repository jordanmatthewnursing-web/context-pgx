"""Package only validated evidence for the static prototype."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESEARCH=ROOT/'research'
sys.path.insert(0,str(RESEARCH/'scripts'))
from snapshots import load_snapshot,replay
from change_report import report
key=json.loads((RESEARCH/'data/snapshots/current.json').read_text())['snapshot']
bundle=load_snapshot(key,RESEARCH/'data/snapshots');replay(bundle)
review=json.loads((RESEARCH/'data/derived/guideline-reconciliation.json').read_text())
manifest={s['manifest']['file']:s['manifest']['sha256'] for s in bundle['sources']}
if any(manifest.get(m['file'])!=m['sha256'] for m in review['apiManifest']):raise ValueError('Review does not cover current API evidence')
if review['status']!='text-correspondence-verified' or len(review['checks'])!=24 or any(c['differentFields'] for c in review['checks']):raise ValueError('Unresolved correspondence review')
workbook=(RESEARCH/'data/review/clopidogrel-recommendation.xlsx').read_bytes()
if hashlib.sha256(workbook).hexdigest()!=review['workbook']['sha256']:raise ValueError('Review workbook differs')
(ROOT/'dist/evidence.json').write_bytes((RESEARCH/'data/snapshots'/(key+'.json')).read_bytes())
review['pageReview']=json.loads((RESEARCH/'data/review/guideline-page-review.json').read_text())
raw=(json.dumps(review,indent=2)+'\n').encode();(ROOT/'dist/review.json').write_bytes(raw)
(ROOT/'dist/config.js').write_text('export const SNAPSHOT='+json.dumps(key)+';\nexport const REVIEW_HASH='+json.dumps(hashlib.sha256(raw).hexdigest())+';\n')
for name in ['newsreader.woff2','plex-sans.woff2','newsreader-OFL.txt','ibmplexsans-OFL.txt']:
 if not (ROOT/'dist'/name).is_file():raise ValueError('Missing bundled font or license: '+name)
print('Packaged verified snapshot and matching correspondence review')

candidate='b9e899c09ecf593a50ae8e7a7d145d4392e48961f74eb5f76812b9c84104ae42'
comparison=report(bundle,load_snapshot(candidate,RESEARCH/'data/snapshots'))
raw=(json.dumps(comparison,indent=2)+'\n').encode()
(ROOT/'dist/changes.json').write_bytes(raw)
with (ROOT/'dist/config.js').open('a') as out:out.write('export const CHANGES_HASH='+json.dumps(hashlib.sha256(raw).hexdigest())+';\n')
