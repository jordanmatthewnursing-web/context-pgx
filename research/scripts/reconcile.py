"""Compare the pinned CPIC recommendation workbook with API text, offline.

This narrowly scoped OOXML reader accepts the provider's text-only tables.
It does not evaluate formulas or infer clinical equivalence from different text.
"""
import hashlib,json,posixpath,zipfile,xml.etree.ElementTree as ET
from evidence import ROOT,load_sources,normalize
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
HEADERS=['CYP2C19 Phenotype','CYP2C19 Implications for Phenotypic Measures','Therapeutic Recommendation','Classification of Recommendation','Comments']
CONTEXTS={'CVI ACS PCI','CVI non-ACS non-PCI','NVI'}

def read_workbook(path):
    result=[]
    with zipfile.ZipFile(path) as archive:
        strings=[''.join(t.text or '' for t in si.findall('.//s:t',NS)) for si in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        relations={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        sheets=ET.fromstring(archive.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)
        contexts=set()
        for sheet in sheets:
            name=sheet.attrib['name']
            if name=='Change log':continue
            if not name.startswith('population '):raise ValueError('Unexpected recommendation sheet')
            context=name[len('population '):].strip()
            if context not in CONTEXTS or context in contexts:raise ValueError('Unexpected or duplicate context')
            contexts.add(context)
            target=relations[sheet.attrib['{'+REL+'}id']]
            location=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            if not location.startswith('xl/worksheets/'):raise ValueError('Unexpected worksheet target')
            rows=ET.fromstring(archive.read(location)).findall('s:sheetData/s:row',NS)
            for index,row in enumerate(rows):
                cells={}
                for cell in row:
                    if cell.find('s:f',NS) is not None:raise ValueError('Formula in source text table')
                    address=cell.attrib['r'];column=address.rstrip('0123456789')
                    if column not in 'ABCDE' or len(column)!=1 or column in cells:raise ValueError('Unexpected cell')
                    value=cell.findtext('s:v',default='',namespaces=NS)
                    if cell.attrib.get('t')=='s':value=strings[int(value)]
                    elif cell.attrib.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//s:t',NS))
                    cells[column]=value
                values=[cells.get(c,'') for c in 'ABCDE']
                if index==0:
                    if values!=HEADERS:raise ValueError('Recommendation headers changed')
                    continue
                if not values[0].startswith('CYP2C19 '):raise ValueError('Unexpected phenotype label')
                result.append({'context':context,'phenotype':values[0][8:],'values':values[1:], 'sheet':name,'range':'A'+row.attrib['r']+':E'+row.attrib['r']})
        if contexts!=CONTEXTS:raise ValueError('Missing context sheet')
    return result

def compare_records(workbook,api):
    def index(rows,key):
        indexed={key(r):r for r in rows}
        if len(indexed)!=len(rows):raise ValueError('Duplicate context and phenotype')
        return indexed
    a=index(workbook,lambda r:(r['context'],r['phenotype']))
    b=index(api,lambda r:(r['population'].strip(),r['phenotypes']['CYP2C19']))
    if a.keys()!=b.keys():raise ValueError('Workbook/API coverage differs')
    checks=[]
    for key in sorted(a):
        row=b[key];expected=[row['implications']['CYP2C19'],row['drugrecommendation'],row['classification'],row['comments']]
        changed=[HEADERS[i+1] for i,(x,y) in enumerate(zip(a[key]['values'],expected)) if x!=y]
        checks.append({'context':key[0],'phenotype':key[1],'sourceId':row['id'],'sheet':a[key]['sheet'],'range':a[key]['range'],'differentFields':changed})
    return checks

def main():
    path=ROOT/'data/review/clopidogrel-recommendation.xlsx'
    manifest=json.loads((path.parent/'recommendation-manifest.json').read_text());raw=path.read_bytes()
    if len(raw)!=manifest['bytes'] or hashlib.sha256(raw).hexdigest()!=manifest['sha256']:raise ValueError('Workbook checksum mismatch')
    data=load_sources();normalize(data['drug'],data['guideline'],data['recommendations'])
    checks=compare_records(read_workbook(path),data['recommendations'])
    result={'status':'text-correspondence-verified' if all(not c['differentFields'] for c in checks) else 'differences-require-review','workbook':manifest,'apiManifest':json.loads((ROOT/'data/source-manifest.json').read_text()),'checks':checks,'limits':['Exact text correspondence only; workbook and API may share the same upstream database.','Does not independently validate clinical recommendations or establish future currency.','No genotype-to-phenotype mapping is assessed.']}
    (ROOT/'data/derived/guideline-reconciliation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'records':len(checks),'differences':[c for c in checks if c['differentFields']]}))
if __name__=='__main__':main()
