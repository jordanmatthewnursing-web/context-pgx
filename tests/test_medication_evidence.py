import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('medication_replay',ROOT/'scripts/replay-medication-evidence.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class MedicationEvidenceTests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)/'data';shutil.copytree(ROOT/'research/medication-evidence',self.root)
 def test_browser_catalog_matches(self):self.assertEqual(m.reproduce(self.root),(ROOT/'dist/medication-catalog.mjs').read_text())
 def test_tampered_guideline_fails(self):
  p=self.root/'raw/ppi-2020.pdf';p.write_bytes(p.read_bytes()+b'x')
  with self.assertRaisesRegex(ValueError,'checksum'):m.reproduce(self.root)
 def test_uncaptured_reference_fails(self):
  p=self.root/'manifest.json';d=json.loads(p.read_text());d['medications'][0]['sourceId']='missing';p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'Uncaptured'):m.reproduce(self.root)
