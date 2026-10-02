"""Read one FDA association-table row; preserve it as a separate source type."""
import hashlib,json
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Tables(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=None;self.cell=None;self.section='';self.heading=None;self.table=0
    def handle_starttag(self,tag,attrs):
        if tag=='h2':self.heading=[]
        if tag=='table':self.table+=1
        if tag=='tr':self.row=[]
        if tag in ('td','th') and self.row is not None:self.cell=[]
        if tag=='br' and self.cell is not None:self.cell.append(' ')
    def handle_data(self,text):
        if self.heading is not None:self.heading.append(text)
        if self.cell is not None:self.cell.append(text)
    def handle_endtag(self,tag):
        if tag=='h2' and self.heading is not None:self.section=' '.join(''.join(self.heading).split());self.heading=None
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append({'section':self.section,'table':self.table,'cells':self.row});self.row=None

def parse(html):
    parser=Tables();parser.feed(html)
    found=[r for r in parser.rows if r['cells'] and r['cells'][0].casefold()=='clopidogrel']
    if len(found)!=1:raise ValueError('Expected exactly one clopidogrel row; source structure needs review')
    row=found[0];cells=row['cells']
    if len(cells)!=4 or cells[1]!='CYP2C19' or not row['section'].startswith('Section 1:'):
        raise ValueError('Unexpected gene, section or columns')
    if cells[2]!='intermediate or poor metabolizers':raise ValueError('Changed subgroup requires manual mapping review')
    if not cells[3]:raise ValueError('Missing source description')
    return {'sourceType':'fda-association-table','drug':'clopidogrel','gene':'CYP2C19','section':row['section'],
            'subgroupText':cells[2],'directPhenotypeLabels':['Intermediate Metabolizer','Poor Metabolizer'],
            'description':cells[3],'indicationContext':None,'locator':{'tableOrdinal':row['table'],'rowDrug':'Clopidogrel','rowGene':'CYP2C19'},
            'limits':['This association table is not a drug label.','No indication-specific scope is supplied in this row.','Absence from this row is not evidence of safety or lack of association.','Likely phenotypes are not automatically mapped to this source subgroup.']}

def load():
    manifest=json.loads((ROOT/'data/fda-source-manifest.json').read_text());raw=(ROOT/'data/raw'/manifest['file']).read_bytes()
    if len(raw)!=manifest['bytes'] or hashlib.sha256(raw).hexdigest()!=manifest['sha256']:raise ValueError('FDA snapshot checksum mismatch')
    return {**parse(raw.decode()),'provenance':manifest}
if __name__=='__main__':
    result=load();(ROOT/'data/derived/fda-association.json').write_text(json.dumps(result,indent=2)+'\n');print('FDA association row parsed and bound to its separate source snapshot.')
