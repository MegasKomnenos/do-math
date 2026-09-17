from __future__ import annotations
import json, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
SCRIPTS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SCRIPTS))
import do_math.context_store as store

class ContextStoreTests(unittest.TestCase):
 def test_large_ongoing_preparation_is_recoverable_without_prompt_overflow(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); entries=[{'execution_id':'E','status':'running','reason':'assigned obligation '*1000}]
   result=store.fit_context({'goal':'g','ongoing_preparation':entries},max_bytes=1200,workspace=root,mandatory_keys=['goal'])
   self.assertIsNone(result['overflow'])
   ref=result['context']['ongoing_preparation']['source_ref']
   self.assertEqual(json.loads(store.read_source(root,ref,limit=100000)['bytes']),entries)
 def test_materialize_and_invalid_utf8_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); data=b'\xff\x00abc'; result=store.materialize_inputs(root,{'sources/raw.bin':data})
   ref=result['manifest'][0]; self.assertEqual((root/ref['path']).read_bytes(),data)
   read=store.read_source(root,{**ref,'format':'bytes'},limit=99);self.assertEqual(read['status'],'ok');self.assertEqual(read['bytes'],data);self.assertFalse(read['truncated'])
 def test_traversal_and_absolute_paths_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   for name in ('../x','/absolute','C:/absolute','a\\b'):
    with self.assertRaises(ValueError):store.materialize_inputs(Path(d),{name:b'x'})
 def test_collect_preserves_outputs_and_excludes_noise(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'input').mkdir();(root/'input/x').write_bytes(b'in');(root/'.git').mkdir();(root/'.git/x').write_bytes(b'g');(root/'__pycache__').mkdir();(root/'__pycache__/x').write_bytes(b'p')
   (root/'src').mkdir();(root/'src/main.lean').write_bytes(b'lean');(root/'checkpoint.bin').write_bytes(b'\xffcp')
   got=store.collect_outputs(root,required_paths=['src/main.lean','checkpoint.bin']);self.assertTrue(got['complete']);self.assertEqual(got['files']['checkpoint.bin'],b'\xffcp');self.assertEqual(set(got['files']),{'src/main.lean','checkpoint.bin'})
 def test_required_missing_and_limit_are_incomplete(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'large').write_bytes(b'x'*20)
   got=store.collect_outputs(root,required_paths=['missing','large'],max_bytes=5);self.assertFalse(got['complete']);self.assertEqual({x['reason'] for x in got['omitted']},{'required_missing','max_bytes_exceeded'})
 def test_changed_during_read_is_not_success(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'x').write_bytes(b'x')
   with patch.object(store,'_read_stable',side_effect=store._ChangedDuringRead('moving')):
    got=store.collect_outputs(root,required_paths=['x'])
   self.assertFalse(got['complete']);self.assertEqual(got['omitted'][0]['reason'],'changed_during_read')
 @unittest.skipUnless(hasattr(os,'symlink'),'symlink unavailable')
 def test_outside_symlink_is_reported_when_supported(self):
  with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
   root=Path(d); target=Path(outside)/'secret';target.write_bytes(b's')
   try:(root/'link').symlink_to(target)
   except OSError as error:self.skipTest(str(error))
   got=store.collect_outputs(root,required_paths=['link']);self.assertFalse(got['complete']);self.assertEqual(got['omitted'][0]['reason'],'outside_symlink')
 def test_catalog_and_overflow_history_are_lossless(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'new-workspace';context={'goal':'g','action':{'role':'plan'},'recent_history':[{'n':i,'text':'x'*100} for i in range(40)],'tasks':[{'id':'T1','title':'t','question':'q','status':'ready','completion_criteria':['c'],'detail':'y'*1000},{'id':'T2','status':'completed'}],'knowledge_catalog':[{'id':'K','detail':'z'*2000}]}
   fitted=store.fit_context(context,max_bytes=1200,workspace=root,mandatory_keys=['goal','action']);self.assertIsNone(fitted['overflow']);self.assertLessEqual(fitted['actual_bytes'],1200);self.assertTrue(fitted['reductions'])
   task_reduction=next(x for x in fitted['reductions'] if x['key']=='tasks');self.assertEqual(task_reduction['ready_universe_ids'],['T1'])
   ref=next(x for x in fitted['manifest'] if x['key']=='recent_history');raw=store.read_source(root,ref,limit=10**7);self.assertEqual(json.loads(raw['bytes']),context['recent_history'])
 def test_mandatory_overflow_reports_size_without_reduction(self):
  with tempfile.TemporaryDirectory() as d:
   context={'goal':'x'*1000,'recent_history':[1,2,3]};got=store.fit_context(context,max_bytes=100,workspace=Path(d),mandatory_keys=['goal']);self.assertEqual(got['overflow']['reason'],'mandatory_context_exceeds_limit');self.assertEqual(got['context']['goal'],context['goal'])
 def test_read_source_range_missing_and_hash_error(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);mat=store.materialize_inputs(root,{'x.bin':b'abcdef'});ref=mat['manifest'][0]
   part=store.read_source(root,ref,offset=2,limit=2);self.assertEqual(part['bytes'],b'cd');self.assertTrue(part['truncated']);self.assertEqual(part['range'],{'start':2,'end':4,'total':6})
   self.assertEqual(store.read_source(root,{'path':'input/nope','sha256':'0','bytes':1})['status'],'missing')
   self.assertEqual(store.read_source(root,{**ref,'sha256':'0'*64})['status'],'error')
if __name__=='__main__':unittest.main(verbosity=2)
