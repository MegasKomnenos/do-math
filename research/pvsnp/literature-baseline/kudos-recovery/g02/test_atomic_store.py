"""Regression for shard 1's observed WinError 5 at Path.replace."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run


class AtomicStoreTests(unittest.TestCase):
 def test_transient_replace_denial_preserves_old_until_success(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'record.json'
   path.write_text('{"old": true}',encoding='utf-8')
   original=Path.replace
   calls=[]
   def replace(source,target):
    calls.append(source)
    if len(calls)<3:
     self.assertEqual(json.loads(path.read_text()),{'old':True})
     raise PermissionError(13,'Access denied')
    return original(source,target)
   with patch.object(Path,'replace',replace),patch.object(run.time,'sleep'):
    try:run.store_json(path,{'new':True})
    except PermissionError:self.fail('Transient replace denial terminated collection.')
   self.assertEqual(json.loads(path.read_text()),{'new':True})
   self.assertEqual(len(calls),3)

 def test_persistent_denial_keeps_old_and_pending_payload(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'record.json'
   path.write_text('{"old": true}',encoding='utf-8')
   with patch.object(Path,'replace',side_effect=PermissionError(13,'Access denied')) as replace,patch.object(run.time,'sleep'):
    with self.assertRaises(PermissionError):run.store_json(path,{'new':True})
   self.assertLessEqual(replace.call_count,6)
   self.assertEqual(json.loads(path.read_text()),{'old':True})
   self.assertEqual(json.loads(path.with_suffix('.tmp').read_text()),{'new':True})

 def test_other_filesystem_error_is_not_retried(self):
  with tempfile.TemporaryDirectory() as directory:
   with patch.object(Path,'replace',side_effect=OSError('disk failure')) as replace,patch.object(run.time,'sleep') as sleep:
    with self.assertRaises(OSError):run.store_json(Path(directory)/'record.json',{'new':True})
   self.assertEqual(replace.call_count,1)
   sleep.assert_not_called()


if __name__=='__main__':unittest.main()
