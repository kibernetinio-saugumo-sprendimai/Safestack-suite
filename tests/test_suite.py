import tempfile, unittest, importlib.util, pathlib
ROOT=pathlib.Path(__file__).parents[1]
def load(path):
 s=importlib.util.spec_from_file_location('m',ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
class SuiteTests(unittest.TestCase):
 def test_backup_roundtrip(self):
  m=load('safestack-backup-guardian/guardian.py')
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d); (p/'a').write_text('x'); m.write(p,p/'m.json'); self.assertEqual(m.verify(p,p/'m.json'),{'missing':[],'changed':[],'new':['m.json']})
 def test_dns_deduplicates(self):
  m=load('safestack-dns-shield/shield.py')
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d); (p/'in').write_text('Example.com\nexample.com\n# x\n'); self.assertEqual(m.generate(p/'in',p/'out'),1)
if __name__=='__main__': unittest.main()
