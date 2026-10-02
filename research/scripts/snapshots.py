"""Immutable evidence bundles, offline replay and guarded snapshot promotion."""
import argparse,datetime,fcntl,hashlib,json,os,re,tempfile,urllib.request
from pathlib import Path
from evidence import ROOT,diff
from fda import parse
from build import assemble
CPIC={'drug.json','guideline.json','recommendations.json','publications.json'}
FILES=CPIC|{'fda-associations.html'}

def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()

def replay(bundle):
    if set(bundle)!={'format','sources','contextMap','analysis'} or bundle['format']!='pgx-evidence-bundle-v1':raise ValueError('Unknown bundle format')
    sources=bundle['sources']
    if len(sources)!=5 or {s['manifest']['file'] for s in sources}!=FILES:raise ValueError('Missing or duplicate source')
    data={};manifests=[];fda=None
    for source in sources:
        if set(source)!={'manifest','text'}:raise ValueError('Invalid source envelope')
        m=source['manifest'];raw=source['text'].encode()
        if digest(raw)!=m['sha256'] or len(raw)!=m['bytes']:raise ValueError('Source checksum mismatch')
        if m['file'] in CPIC:data[Path(m['file']).stem]=json.loads(source['text']);manifests.append(m)
        else:fda={**parse(source['text']),'provenance':m}
    analysis=assemble(data,fda,bundle['contextMap'],manifests)
    if analysis!=bundle['analysis']:raise ValueError('Exported analysis differs from replay')
    return analysis

def make_bundle(sources,contexts):
    data={Path(s['manifest']['file']).stem:json.loads(s['text']) for s in sources if s['manifest']['file'] in CPIC}
    source=next(s for s in sources if s['manifest']['file']=='fda-associations.html')
    fda={**parse(source['text']),'provenance':source['manifest']}
    manifests=[s['manifest'] for s in sources if s['manifest']['file'] in CPIC]
    bundle={'format':'pgx-evidence-bundle-v1','sources':sources,'contextMap':contexts,'analysis':assemble(data,fda,contexts,manifests)}
    replay(bundle);return bundle

def local_bundle():
    manifests=json.loads((ROOT/'data/source-manifest.json').read_text())+[json.loads((ROOT/'data/fda-source-manifest.json').read_text())]
    return make_bundle([{'manifest':m,'text':(ROOT/'data/raw'/m['file']).read_text()} for m in manifests],json.loads((ROOT/'data/context-map.json').read_text()))

def atomic_write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def store(bundle,directory):
    replay(bundle);raw=encoded(bundle);key=digest(raw);path=directory/(key+'.json')
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Snapshot identity collision')
    else:atomic_write(path,raw)
    return key

def load_snapshot(key,directory):
    if not re.fullmatch('[0-9a-f]{64}',key):raise ValueError('Invalid snapshot identity')
    raw=(directory/(key+'.json')).read_bytes()
    if digest(raw)!=key:raise ValueError('Snapshot content does not match identity')
    bundle=json.loads(raw);replay(bundle);return bundle

def activate(key,directory,expected):
    directory.mkdir(parents=True,exist_ok=True)
    with (directory/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        load_snapshot(key,directory)
        pointer=directory/'current.json'
        current=json.loads(pointer.read_text())['snapshot'] if pointer.exists() else None
        if current!=expected:raise ValueError('Current snapshot changed; review again before activation')
        if current:load_snapshot(current,directory)
        atomic_write(pointer,encoded({'snapshot':key,'previous':current}))
    return key

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PGx-evidence-prototype/1.0'}),timeout=30) as response:
        raw=response.read(5_000_001)
        if len(raw)>5_000_000:raise ValueError('Source exceeds bounded response size')
        return raw.decode('utf-8')

def refresh(base,get=fetch):
    # URLs come from this project's reviewed acquisition manifests, never from an imported bundle.
    allowed={m['file']:m['url'] for m in json.loads((ROOT/'data/source-manifest.json').read_text())+[json.loads((ROOT/'data/fda-source-manifest.json').read_text())]}
    replay(base);sources=[]
    for source in base['sources']:
        m=dict(source['manifest'])
        if m['url']!=allowed[m['file']]:raise ValueError('Unapproved refresh URL')
        text=get(m['url']);raw=text.encode();m.update(bytes=len(raw),sha256=digest(raw),retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
        sources.append({'manifest':m,'text':text})
    return make_bundle(sources,base['contextMap'])

def changes(before,after):
    a,b=replay(before),replay(after)
    source_changes=[s['manifest']['file'] for s in after['sources'] if next(x['manifest']['sha256'] for x in before['sources'] if x['manifest']['file']==s['manifest']['file'])!=s['manifest']['sha256']]
    return {'changedSources':source_changes,'contextMapChanged':a['contextMap']!=b['contextMap'],'cpicRecords':diff(a['cpicRecords'],b['cpicRecords']),
            'fdaContentChanged':{k:v for k,v in a['fdaAssociation'].items() if k!='provenance'}!={k:v for k,v in b['fdaAssociation'].items() if k!='provenance'},
            'activation':'explicit-review-required; candidate does not replace current'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('pack')
    p=sub.add_parser('replay');p.add_argument('file',type=Path)
    p=sub.add_parser('refresh');p.add_argument('snapshot')
    p=sub.add_parser('compare');p.add_argument('before');p.add_argument('after')
    p=sub.add_parser('activate');p.add_argument('snapshot');p.add_argument('--expected-current',required=True,help='Exact prior snapshot ID, or none for first activation')
    args=parser.parse_args();directory=ROOT/'data/snapshots'
    if args.command=='pack':print(store(local_bundle(),directory))
    elif args.command=='replay':print(json.dumps({'verified':True,'comparisons':len(replay(json.loads(args.file.read_text()))['comparisons'])}))
    elif args.command=='activate':print(activate(args.snapshot,directory,None if args.expected_current=='none' else args.expected_current))
    elif args.command=='compare':print(json.dumps(changes(load_snapshot(args.before,directory),load_snapshot(args.after,directory)),indent=2))
    else:
        before=load_snapshot(args.snapshot,directory);after=refresh(before);key=store(after,directory)
        print(json.dumps({'candidate':key,'review':changes(before,after)},indent=2))
if __name__=='__main__':main()
