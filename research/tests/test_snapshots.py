import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from snapshots import local_bundle,replay,store,load_snapshot,activate,refresh,changes,make_bundle
class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.bundle=local_bundle()
    def test_portable_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);key=store(self.bundle,d);self.assertEqual(load_snapshot(key,d),self.bundle)
            self.assertEqual(len(replay(json.loads(json.dumps(self.bundle)))['comparisons']),24)
    def test_tampered_source_and_analysis_rejected(self):
        for mode in ['source','analysis']:
            b=copy.deepcopy(self.bundle)
            if mode=='source':b['sources'][0]['text']+=' '
            else:b['analysis']['comparisons'][0]['clinicalAgreement']='equivalent'
            with self.assertRaises(ValueError):replay(b)
    def test_missing_duplicate_and_path_identity_rejected(self):
        b=copy.deepcopy(self.bundle);b['sources'][-1]=b['sources'][0]
        with self.assertRaises(ValueError):replay(b)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):load_snapshot('../outside',Path(tmp))
    def test_activation_compare_and_swap(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);key=store(self.bundle,d);activate(key,d,None)
            original=(d/'current.json').read_bytes()
            with self.assertRaises(ValueError):activate(key,d,None)
            self.assertEqual((d/'current.json').read_bytes(),original)
    def test_corrupt_stored_snapshot_cannot_activate(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);key=store(self.bundle,d);(d/(key+'.json')).write_text('{}')
            with self.assertRaises(ValueError):activate(key,d,None)
            self.assertFalse((d/'current.json').exists())
    def test_partial_fetch_preserves_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);key=store(self.bundle,d);activate(key,d,None);original=(d/'current.json').read_bytes();calls=[]
            def get(url):
                calls.append(url)
                if len(calls)==3:raise TimeoutError('synthetic third-source outage')
                return next(s['text'] for s in self.bundle['sources'] if s['manifest']['url']==url)
            with self.assertRaises(TimeoutError):refresh(self.bundle,get)
            self.assertEqual((d/'current.json').read_bytes(),original);self.assertEqual(len(list(d.glob('*.json'))),2)
    def test_refresh_candidate_does_not_activate_and_unchanged_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);key=store(self.bundle,d);activate(key,d,None)
            after=refresh(self.bundle,lambda url:next(s['text'] for s in self.bundle['sources'] if s['manifest']['url']==url));new=store(after,d)
            self.assertEqual(json.loads((d/'current.json').read_text())['snapshot'],key)
            report=changes(self.bundle,after);self.assertEqual(report['changedSources'],[]);self.assertFalse(report['fdaContentChanged'])
            activate(new,d,key);pointer=json.loads((d/'current.json').read_text());self.assertEqual(pointer['previous'],key)
    def test_unapproved_import_url_not_fetched(self):
        b=copy.deepcopy(self.bundle);b['sources'][0]['manifest']['url']='https://example.invalid/'
        b=make_bundle(b['sources'],b['contextMap']);calls=[]
        with self.assertRaises(ValueError):refresh(b,lambda url:calls.append(url))
        self.assertEqual(calls,[])
    def test_manual_context_change_is_visible_without_source_change(self):
        contexts=copy.deepcopy(self.bundle['contextMap'])
        contexts['mappings'][0]['label']='Changed review label'
        after=make_bundle(self.bundle['sources'],contexts)
        report=changes(self.bundle,after)
        self.assertTrue(report['contextMapChanged'])
        self.assertEqual(report['changedSources'],[])
if __name__=='__main__':unittest.main()
