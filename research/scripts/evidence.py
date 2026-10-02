"""Context-preserving source index. No genotype interpretation or prescribing output."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def normalize(drugs,guidelines,rows):
    if len(drugs)!=1 or len(guidelines)!=1:raise ValueError('Ambiguous source identity')
    drug,guideline=drugs[0],guidelines[0]
    if drug['name']!='clopidogrel' or drug['guidelineid']!=guideline['id'] or 'CYP2C19' not in guideline['genes']:
        raise ValueError('Wrong drug/gene/guideline join')
    result=[];ids=set();keys=set()
    for index,row in enumerate(rows):
        if row['id'] in ids:raise ValueError('Duplicate source record')
        ids.add(row['id'])
        if row['drugid']!=drug['drugid'] or row['guidelineid']!=guideline['id']:raise ValueError('Wrong recommendation join')
        if set(row['phenotypes'])!={'CYP2C19'}:raise ValueError('Unexpected gene context')
        phenotype=row['phenotypes']['CYP2C19'];context=row['population']
        if not isinstance(context,str) or not context.strip():raise ValueError('Missing context')
        if not isinstance(phenotype,str) or not phenotype.strip():raise ValueError('Missing phenotype')
        key=(context.strip(),phenotype)
        if key in keys:raise ValueError('Ambiguous context/phenotype records')
        keys.add(key)
        classification=row['classification']
        if classification is not None and not isinstance(classification,str):raise ValueError('Invalid classification')
        result.append({'sourceId':row['id'],'sourceVersion':row['version'],'context':context.strip(),
            'sourceContext':context,'phenotype':phenotype,'classification':classification,
            'state':'unreported' if classification is None else 'no-recommendation' if classification=='No Recommendation' else 'reported',
            'sourcePointer':'recommendations.json#/'+str(index),
            'sourceRowSha256':hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
    return sorted(result,key=lambda r:(r['context'],r['phenotype']))

def lookup(rows,phenotype,context=None):
    if not context:return {'status':'context-required','records':[]}
    matches=[r for r in rows if r['context']==context and r['phenotype']==phenotype]
    if len(matches)>1:raise ValueError('Ambiguous lookup')
    return {'status':'found' if matches else 'not-covered','records':matches}

def diff(before,after):
    def indexed(rows):
        result={r['sourceId']:r for r in rows}
        if len(result)!=len(rows):raise ValueError('Duplicate source identity in diff')
        return result
    a,b=indexed(before),indexed(after)
    return {'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),
            'changed':[{'sourceId':i,'fields':sorted(k for k in set(a[i])|set(b[i]) if a[i].get(k)!=b[i].get(k))} for i in sorted(a.keys()&b.keys()) if a[i]!=b[i]]}

def load_sources():
    result={}
    for item in json.loads((ROOT/'data/source-manifest.json').read_text()):
        path=ROOT/'data/raw'/item['file'];raw=path.read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Source checksum mismatch: '+item['file'])
        result[path.stem]=json.loads(raw)
    return result

def main():
    data=load_sources();rows=normalize(data['drug'],data['guideline'],data['recommendations'])
    output={'schemaVersion':1,'purpose':'Educational source comparison; not a prescribing tool','drug':'clopidogrel','gene':'CYP2C19',
            'guideline':data['guideline'][0],'records':rows,'sourceManifest':json.loads((ROOT/'data/source-manifest.json').read_text()),
            'limits':['Source population codes are preserved; expanded labels still need verification.','No Recommendation is not a negative recommendation or an assurance of safety.','Missing context cannot inherit another context’s record.','Classification is source terminology, not an app-generated score.','Snapshot retrieval time is not publication date or assurance of current guidance.']}
    (ROOT/'data/derived/evidence-index.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'records':len(rows),'contexts':sorted(set(r['context'] for r in rows)),'phenotypes':len(set(r['phenotype'] for r in rows))}))
if __name__=='__main__':main()
