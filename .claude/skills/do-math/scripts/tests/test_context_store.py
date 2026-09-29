from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
SCRIPTS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SCRIPTS))
import do_math.context_store as store

class StableReadTests(unittest.TestCase):
 def test_metadata_change_during_one_read_is_not_one_version(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'x';path.write_bytes(b'bytes')
   self.assertEqual(store.read_stable(path),b'bytes')
   with patch.object(store,'stat_fingerprint',side_effect=[(5,1,1),(5,2,1)]):
    with self.assertRaises(store._ChangedDuringRead):store.read_stable(path)


class ContextStoreTests(unittest.TestCase):
 def test_changed_during_read_is_not_success(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'x').write_bytes(b'x')
   with patch.object(store,'read_stable',side_effect=store._ChangedDuringRead('moving')):
    got=store.collect_outputs(root,required_paths=['x'])
   self.assertFalse(got['complete']);self.assertEqual(got['omitted'][0]['reason'],'changed_during_read')


if __name__=='__main__':unittest.main(verbosity=2)
