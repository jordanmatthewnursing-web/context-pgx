"""Build the reviewable two-source scope comparison from verified snapshots."""
import json
from evidence import ROOT,load_sources,normalize
from fda import load
from compare import compare

def assemble(data,fda,contexts,manifest):
    rows=normalize(data['drug'],data['guideline'],data['recommendations'])
    if {r['context'] for r in rows}!={r['code'] for r in contexts['mappings']}:raise ValueError('Context mapping incomplete or changed')
    if contexts['doi'] not in {r['doi'] for r in data['publications']}:raise ValueError('Context publication not in source bibliography')
    result={'schemaVersion':1,'purpose':'Source-scope comparison for education; no patient recommendation',
            'contextMap':contexts,'cpicRecords':rows,'fdaAssociation':fda,
            'comparisons':[compare(rows,fda,r['phenotype'],r['context']) for r in rows],
            'cpicManifest':manifest,
            'limits':['Current guideline-page updates have not yet been reconciled with the snapshot.','A matching drug and gene do not establish equivalent source scope.','No clinical agreement or conflict is inferred.']}
    return result

def main():
    result=assemble(load_sources(),load(),json.loads((ROOT/'data/context-map.json').read_text()),json.loads((ROOT/'data/source-manifest.json').read_text()))
    target=ROOT/'data/derived/comparison.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print('Built 24 source-scope comparisons with distinct CPIC and FDA provenance.')
if __name__=='__main__':main()
