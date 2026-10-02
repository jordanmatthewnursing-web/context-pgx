import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evidence import normalize,lookup,diff,load_sources
class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_sources()
    def rows(self,raw=None):return normalize(self.data['drug'],self.data['guideline'],raw if raw is not None else self.data['recommendations'])
    def test_coverage_and_traceable_pointer(self):
        rows=self.rows();self.assertEqual(len(rows),24);self.assertEqual(len(set(r['context'] for r in rows)),3)
        for row in rows:self.assertEqual(self.data['recommendations'][int(row['sourcePointer'].split('#/')[1])]['id'],row['sourceId'])
    def test_context_required_and_unknown_not_inherited(self):
        self.assertEqual(lookup(self.rows(),'Normal Metabolizer')['status'],'context-required')
        self.assertEqual(lookup(self.rows(),'Normal Metabolizer','unknown')['status'],'not-covered')
    def test_no_recommendation_is_explicit_state(self):
        r=lookup(self.rows(),'Indeterminate','CVI ACS PCI')['records'][0]
        self.assertEqual(r['state'],'no-recommendation')
    def test_missing_is_distinct_from_no_recommendation(self):
        raw=copy.deepcopy(self.data['recommendations']);raw[0]['classification']=None
        self.assertEqual(next(r for r in self.rows(raw) if r['sourceId']==raw[0]['id'])['state'],'unreported')
    def test_duplicate_context_or_id_rejected(self):
        raw=copy.deepcopy(self.data['recommendations']);raw.append(copy.deepcopy(raw[0]))
        with self.assertRaises(ValueError):self.rows(raw)
        raw[-1]['id']=999999
        with self.assertRaises(ValueError):self.rows(raw)
    def test_wrong_join_or_missing_context_rejected(self):
        for field,value in [('drugid','wrong'),('population',None),('phenotypes',{'CYP2D6':'Normal Metabolizer'})]:
            raw=copy.deepcopy(self.data['recommendations']);raw[0][field]=value
            with self.assertRaises(ValueError):self.rows(raw)
    def test_text_change_detected_even_with_same_classification(self):
        raw=copy.deepcopy(self.data['recommendations']);raw[0]['comments']='Synthetic changed source text for testing'
        change=diff(self.rows(),self.rows(raw))
        self.assertEqual(len(change['changed']),1);self.assertIn('sourceRowSha256',change['changed'][0]['fields'])
    def test_identical_and_added_removed(self):
        rows=self.rows();self.assertEqual(diff(rows,rows),{'added':[],'removed':[],'changed':[]})
        self.assertEqual(diff(rows,rows[:-1])['removed'],[rows[-1]['sourceId']])
        self.assertEqual(diff(rows[:-1],rows)['added'],[rows[-1]['sourceId']])
if __name__=='__main__':unittest.main()
