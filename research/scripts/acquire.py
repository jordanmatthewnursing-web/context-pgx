"""Acquire a bounded CPIC snapshot. Existing snapshots are never overwritten."""
import datetime,hashlib,json,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data/raw'
BASE='https://api.cpicpgx.org/v1/'
def main():
    if any(DEST.iterdir()): raise SystemExit('Snapshot already exists; use a new directory for a new acquisition.')
    manifest=[]
    def get(name,path,params):
        url=BASE+path+'?'+urllib.parse.urlencode(params)
        with urllib.request.urlopen(url,timeout=30) as response:raw=response.read()
        data=json.loads(raw)
        if not isinstance(data,list) or not data:raise ValueError('Empty or invalid source '+name)
        (DEST/(name+'.json')).write_bytes(raw)
        manifest.append({'file':name+'.json','url':url,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
        return data
    drug=get('drug','drug',{'name':'eq.clopidogrel'})
    if len(drug)!=1:raise ValueError('Ambiguous drug')
    d=drug[0]
    get('guideline','guideline',{'id':'eq.'+str(d['guidelineid'])})
    get('recommendations','recommendation',{'drugid':'eq.'+d['drugid'],'order':'id.asc'})
    get('publications','publication',{'guidelineid':'eq.'+str(d['guidelineid']),'order':'id.asc'})
    (ROOT/'data/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Saved four bounded CPIC snapshots and their exact request/checksum manifest.')
if __name__=='__main__':main()
