import importlib.util,json,hashlib,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('replay',ROOT/'scripts/replay-marker-evidence.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class MarkerReplayTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'evidence';shutil.copytree(ROOT/'research/marker-evidence',self.root)
 def test_exact_browser_rules(self):self.assertEqual(module.reproduce(self.root),(ROOT/'dist/marker-rules.mjs').read_text())
 def test_changed_source_is_rejected(self):
  p=self.root/'raw/4244285.json';p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'checksum'):module.reproduce(self.root)
 def test_changed_coordinate_is_rejected_even_with_unchanged_source_hashes(self):
  p=self.root/'manifest.json';d=json.loads(p.read_text());d['selectedRules'][0]['position']+=1;p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'placement'):module.reproduce(self.root)
 def test_wrong_source_identity_rejected_even_if_rehashed(self):
  p=self.root/'raw/4244285.json';d=json.loads(p.read_text());d['refsnp_id']=42;p.write_text(json.dumps(d));m=self.root/'manifest.json';d=json.loads(m.read_text());row=d['sources'][0];row['bytes']=p.stat().st_size;row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();m.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'identity'):module.reproduce(self.root)
 def test_escape_path_rejected(self):
  p=self.root/'manifest.json';d=json.loads(p.read_text());d['sources'][0]['file']='../secret';p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'escapes'):module.reproduce(self.root)
 def test_dpyd_palindromic_orientation_rejected(self):
  p=self.root/'manifest.json';d=json.loads(p.read_text());r=next(x for x in d['selectedRules'] if x['id']=='rs67376798');r.update(reference='A',alternate='T');p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'orientation'):module.reproduce(self.root)
 def test_dpyd_direct_policy_required(self):
  p=self.root/'manifest.json';d=json.loads(p.read_text());next(x for x in d['selectedRules'] if x['id']=='rs75017182')['directOnly']=False;p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'orientation'):module.reproduce(self.root)
