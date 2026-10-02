"""Compare evidence scope, never infer clinical agreement from source labels."""
from evidence import lookup

def compare(rows,fda,phenotype,context=None):
    if fda.get('sourceType')!='fda-association-table' or fda.get('gene')!='CYP2C19' or fda.get('drug')!='clopidogrel':
        raise ValueError('Unsupported comparison source')
    cpic=lookup(rows,phenotype,context)
    if cpic['status']!='found':return {'status':cpic['status'],'cpic':cpic,'clinicalAgreement':'not-assessed'}
    membership='explicitly-listed' if phenotype in fda['directPhenotypeLabels'] else 'not-explicitly-listed'
    return {'status':'scope-review-required','cpic':cpic['records'][0],
            'fda':{'sourceType':fda['sourceType'],'subgroupMembership':membership,'indicationContext':fda['indicationContext'],'provenance':fda['provenance']},
            'clinicalAgreement':'not-assessed',
            'reasons':['Source types differ: guideline record versus association table.','The FDA row does not specify the selected CPIC indication context.','Different classifications or missing coverage must not become an automatic conflict, equivalence or safety verdict.']}
