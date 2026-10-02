import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from snapshots import local_bundle,make_bundle,digest
from change_report import report
class ChangeReportTests(unittest.TestCase):
 def setUp(self):self.before=local_bundle()
 def test_same_content_new_retrieval(self):
  sources=copy.deepcopy(self.before['sources'])
  for s in sources:s['manifest']['retrievedAt']='2026-10-01T00:00:00Z'
  result=report(self.before,make_bundle(sources,self.before['contextMap']))
  self.assertNotEqual(result['beforeSnapshot'],result['afterSnapshot'])
  self.assertEqual(result['recordChanges'],[])
  self.assertTrue(all(not s['contentChanged'] for s in result['sourceFiles']))
 def test_text_change_visible_without_classification_change(self):
  sources=copy.deepcopy(self.before['sources']);source=next(s for s in sources if s['manifest']['file']=='recommendations.json')
  rows=json.loads(source['text']);rows[0]['comments']+=' Test-only changed qualification.'
  source['text']=json.dumps(rows);raw=source['text'].encode();source['manifest'].update(sha256=digest(raw),bytes=len(raw))
  result=report(self.before,make_bundle(sources,self.before['contextMap']))
  self.assertEqual(len(result['recordChanges']),1)
  change=result['recordChanges'][0]
  self.assertEqual(change['before']['classification'],change['after']['classification'])
  self.assertNotEqual(change['before']['comments'],change['after']['comments'])
 def test_invalid_derived_comparison_rejected(self):
  after=copy.deepcopy(self.before);after['analysis']['comparisons']=[]
  with self.assertRaises(ValueError):report(self.before,after)
if __name__=='__main__':unittest.main()
