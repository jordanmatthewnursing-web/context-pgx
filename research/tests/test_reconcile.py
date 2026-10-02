import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reconcile import read_workbook,compare_records,ROOT
class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.workbook=read_workbook(ROOT/'data/review/clopidogrel-recommendation.xlsx')
        self.api=json.loads((ROOT/'data/raw/recommendations.json').read_text())
    def test_all_records_and_field_text_match(self):
        checks=compare_records(self.workbook,self.api)
        self.assertEqual(len(checks),24)
        self.assertTrue(all(not c['differentFields'] for c in checks))
        self.assertEqual(len({c['sheet'] for c in checks}),3)
    def test_each_content_field_change_is_visible(self):
        for field in range(4):
            changed=copy.deepcopy(self.workbook)
            changed[0]['values'][field]+=' changed'
            differences=[c for c in compare_records(changed,self.api) if c['differentFields']]
            self.assertEqual(len(differences),1)
            self.assertEqual(len(differences[0]['differentFields']),1)
    def test_missing_record_cannot_report_success(self):
        with self.assertRaises(ValueError):compare_records(self.workbook[:-1],self.api)
    def test_duplicate_record_cannot_report_success(self):
        with self.assertRaises(ValueError):compare_records(self.workbook+[self.workbook[0]],self.api)
    def test_context_change_cannot_transfer_record(self):
        self.workbook[0]['context']='unreviewed context'
        with self.assertRaises(ValueError):compare_records(self.workbook,self.api)
if __name__=='__main__':unittest.main()
