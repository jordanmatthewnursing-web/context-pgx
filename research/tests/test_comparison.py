import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evidence import load_sources,normalize
from fda import load,parse,ROOT
from compare import compare
class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fda=load();d=load_sources();cls.rows=normalize(d['drug'],d['guideline'],d['recommendations']);cls.html=(ROOT/'data/raw/fda-associations.html').read_text()
    def test_actual_source_row(self):
        self.assertEqual(self.fda['gene'],'CYP2C19');self.assertIsNone(self.fda['indicationContext']);self.assertEqual(self.fda['sourceType'],'fda-association-table')
    def test_missing_duplicate_or_changed_subgroup_rejected(self):
        for html in [self.html.replace('Clopidogrel','NotTheDrug'),self.html+self.html,self.html.replace('intermediate or poor metabolizers','changed subgroup')]:
            with self.assertRaises(ValueError):parse(html)
    def test_context_required(self):
        self.assertEqual(compare(self.rows,self.fda,'Poor Metabolizer')['status'],'context-required')
    def test_direct_match_does_not_establish_equivalence(self):
        r=compare(self.rows,self.fda,'Poor Metabolizer','CVI ACS PCI')
        self.assertEqual(r['fda']['subgroupMembership'],'explicitly-listed');self.assertEqual(r['clinicalAgreement'],'not-assessed');self.assertEqual(r['status'],'scope-review-required')
    def test_likely_not_automatically_mapped(self):
        r=compare(self.rows,self.fda,'Likely Poor Metabolizer','CVI ACS PCI')
        self.assertEqual(r['fda']['subgroupMembership'],'not-explicitly-listed')
    def test_no_recommendation_not_conflict_or_safety(self):
        r=compare(self.rows,self.fda,'Intermediate Metabolizer','CVI non-ACS non-PCI')
        self.assertEqual(r['cpic']['state'],'no-recommendation');self.assertEqual(r['clinicalAgreement'],'not-assessed')
    def test_unknown_context_not_inherited(self):
        self.assertEqual(compare(self.rows,self.fda,'Poor Metabolizer','other')['status'],'not-covered')
    def test_wrong_source_type_rejected(self):
        f=copy.deepcopy(self.fda);f['sourceType']='drug-label'
        with self.assertRaises(ValueError):compare(self.rows,f,'Poor Metabolizer','NVI')
if __name__=='__main__':unittest.main()
