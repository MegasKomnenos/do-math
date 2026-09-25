from __future__ import annotations
import json, os, sys, tempfile, unittest, subprocess
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
SCRIPTS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SCRIPTS))
import do_math.context_store as store

@contextmanager
def junction_at_open(target, outside, *, restore_before_return):
 """Real junction swap at the actual open, after callers' path prechecks."""
 original_open=Path.open
 parent=target.parent
 saved=parent.with_name(parent.name+'-held')
 fired=[]
 def intercepted(path,*args,**kwargs):
  if path==target and not fired and (args[0] if args else kwargs.get('mode','r'))=='rb':
   fired.append(True)
   parent.rename(saved)
   def quoted(value):return "'"+str(value).replace("'","''")+"'"
   subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',
    'New-Item -ItemType Junction -Path '+quoted(parent)+' -Target '+quoted(outside)+' | Out-Null'],check=True,capture_output=True)
   stream=original_open(path,*args,**kwargs)
   if restore_before_return:
    # Remove only this known test junction, never recurse into its target.
    parent.rmdir()
    saved.rename(parent)
   return stream
  return original_open(path,*args,**kwargs)
 try:
  with patch.object(Path,'open',intercepted):yield fired
 finally:
  if saved.exists():
   if parent.exists():parent.rmdir()
   saved.rename(parent)


@unittest.skipUnless(os.name=='nt','actual Windows junction boundary')
class OpenedHandleBoundaryTests(unittest.TestCase):
 def test_collection_rejects_real_junction_swap_at_open(self):
  for transient in (False,True):
   with self.subTest(transient=transient),tempfile.TemporaryDirectory() as directory:
    base=Path(directory); root=base/'workspace'; sub=root/'sub'; sub.mkdir(parents=True)
    outside=base/'outside';outside.mkdir()
    target=sub/'result.txt';target.write_bytes(b'worker output')
    (outside/'result.txt').write_bytes(b'outside bytes')
    self.assertEqual(store.collect_outputs(root)['files']['sub/result.txt'],b'worker output')
    with junction_at_open(target,outside,restore_before_return=transient) as fired:
     result=store.collect_outputs(root,required_paths=['sub/result.txt'])
    self.assertTrue(fired)
    self.assertNotIn('sub/result.txt',result['files'],result)
    self.assertFalse(result['complete'])
    omission=next(row for row in result['omitted'] if row['path']=='sub/result.txt')
    self.assertEqual(omission['reason'],'physical_boundary')
    self.assertTrue(omission['required'])
    self.assertTrue(omission['error'])
    self.assertEqual((outside/'result.txt').read_bytes(),b'outside bytes')

 def test_source_read_rejects_handle_outside_restored_lexical_path(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);root=base/'workspace';sub=root/'input';sub.mkdir(parents=True)
   outside=base/'outside';outside.mkdir();target=sub/'result.txt'
   target.write_bytes(b'worker output');(outside/'result.txt').write_bytes(b'outside bytes')
   with junction_at_open(target,outside,restore_before_return=True):
    result=store.read_source(root,{'path':'input/result.txt'})
   self.assertEqual(result['status'],'error',result)
   self.assertEqual(result['bytes'],b'')
   self.assertIn('physical',result['reason'])

 def test_retention_inventory_rejects_same_real_open_race(self):
  from do_math.retention import _inventory
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);root=base/'runs/EX-1';root.mkdir(parents=True)
   outside=base/'outside';outside.mkdir();target=root/'result.txt'
   target.write_bytes(b'worker output');(outside/'result.txt').write_bytes(b'outside bytes')
   with junction_at_open(target,outside,restore_before_return=True):
    with self.assertRaisesRegex(ValueError,'physical'):_inventory(root)

 def test_cleanup_preserves_run_when_open_boundary_changes(self):
  from do_math.retention import cleanup_candidates,cleanup
  from test_redesign_SURFACE import archived_run
  for phase in ('eligibility','deletion'):
   with self.subTest(phase=phase),tempfile.TemporaryDirectory() as directory:
    base=Path(directory);root=base/'workspace'
    run,state,archive,read=archived_run(root)
    outside=base/'outside';outside.mkdir()
    # Matching archived bytes must not make an outside handle admissible.
    (outside/'output.txt').write_bytes(b'preserved result')
    candidates=cleanup_candidates(root,read_artifact=read,**state)
    self.assertTrue(candidates[0]['eligible'])
    with junction_at_open(run/'output.txt',outside,restore_before_return=True):
     if phase=='eligibility':
      result=cleanup_candidates(root,read_artifact=read,**state)
      self.assertFalse(result[0]['eligible'])
      self.assertTrue(any('physical' in reason for reason in result[0]['reasons']))
     else:
      result=cleanup(root,candidates,current_state=lambda:state,read_artifact=read)
      self.assertEqual(result['deleted'],[])
      self.assertEqual(result['status'],'degraded')
      self.assertTrue(any('physical' in row['error'] for row in result['failures']))
    self.assertEqual((run/'output.txt').read_bytes(),b'preserved result')
    self.assertEqual((outside/'output.txt').read_bytes(),b'preserved result')
    self.assertEqual(state['executions']['EX-1']['status'],'ended')

class ContextStoreTests(unittest.TestCase):
 def test_directory_read_failure_is_an_omission_even_without_required_paths(self):
  for required in ([], ['blocked/proof.txt']):
   with self.subTest(required=required), tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    (root/'blocked').mkdir()
    (root/'visible.txt').write_bytes(b'preserved sibling')
    def walk(path, topdown=True, followlinks=False, onerror=None):
     yield str(root), ['blocked'], ['visible.txt']
     error=PermissionError(13, 'Permission denied', str(root/'blocked'))
     if onerror is not None:
      onerror(error)
    with patch.object(store.os, 'walk', side_effect=walk):
     result=store.collect_outputs(root, required_paths=required)
    self.assertEqual(result['files'], {'visible.txt': b'preserved sibling'})
    self.assertFalse(result['complete'])
    omission=next(row for row in result['omitted'] if row['path']=='blocked')
    self.assertEqual(omission['reason'], 'read_error')
    self.assertEqual(omission['error_type'], 'PermissionError')
    self.assertEqual(omission['required'], bool(required))
    self.assertIn('Permission denied', omission['error'])
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
 def test_invalid_empty_capture_does_not_disappear(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(TypeError, 'captured_files must be'):
    store.collect_outputs(Path(d), captured_files=[])
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
 def test_catalog_and_overflow_history_preserve_exact_values(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'new-workspace';context={'goal':'g','action':{'role':'plan'},'recent_history':[{'n':i,'text':'x'*100} for i in range(40)],'tasks':[{'id':'T1','title':'t','question':'q','status':'ready','completion_criteria':['c'],'detail':'y'*1000},{'id':'T2','status':'completed'}],'knowledge_catalog':[{'id':'K','detail':'z'*2000}]}
   fitted=store.fit_context(context,max_bytes=1200,workspace=root,mandatory_keys=['goal','action']);self.assertIsNone(fitted['overflow']);self.assertLessEqual(fitted['actual_bytes'],1200);self.assertTrue(fitted['reductions'])
   task_reduction=next(x for x in fitted['reductions'] if x['key']=='tasks');self.assertEqual(json.loads(store.read_source(root,task_reduction['source_ref'],limit=10**7)['bytes']),context['tasks'])
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
