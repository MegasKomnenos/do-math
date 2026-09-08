import unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch
import run
class ProgressTests(unittest.TestCase):
 def test_unchanged_checkpoint_avoids_rereading_every_result(self):
  original_root=run.ROOT
  with tempfile.TemporaryDirectory(dir=original_root/'tdd') as name:
   tmp=Path(name).resolve();assert tmp.is_relative_to(original_root.resolve())
   try:
    run.ROOT=tmp;run._STATUS_ROWS=None
    value={'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'unresolved'}}
    path=tmp/'results/a.json';run.store_json(path,value);run.progress('first')
    reads=[];original=Path.read_text
    def counted(p,*a,**k):
     if p.parent==tmp/'results':reads.append(p)
     return original(p,*a,**k)
    with patch.object(Path,'read_text',counted):run.progress('unchanged')
    self.assertEqual(reads,[],'Checkpoint must not reread unchanged result files')
    value['abstract']['status']='found';run.store_json(path,value);run.progress('updated')
    state=json.loads((tmp/'progress.json').read_text(encoding='utf-8'))
    self.assertEqual(state['processed'],1);self.assertEqual(state['abstract_found'],1)
    run._STATUS_ROWS=None;run.progress('resumed')
    self.assertEqual(json.loads((tmp/'progress.json').read_text(encoding='utf-8'))['abstract_found'],1)
   finally:run.ROOT=original_root;run._STATUS_ROWS=None
if __name__=='__main__':unittest.main()
