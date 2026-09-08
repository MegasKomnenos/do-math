import json,unittest
from pathlib import Path
from shard import partition,aggregate
BASE=Path(__file__).resolve().parents[2]
class ShardTests(unittest.TestCase):
 def test_actual_assignment_has_no_missing_or_duplicate_member(self):
  papers=[json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]
  parts=[partition(papers,i,2) for i in range(2)]
  ids=[p['paper_id'] for group in parts for p in group]
  self.assertEqual(len(ids),5138);self.assertEqual(len(set(ids)),5138);self.assertEqual(set(ids),{p['paper_id'] for p in papers})
  self.assertEqual(parts[0],partition(papers,0,2))
 def test_filtering_completed_members_does_not_change_shard_ownership(self):
  papers=list(range(8));original=partition(papers,1,2)
  self.assertEqual([p for p in partition(papers,1,2) if p not in {1,5}],[3,7]);self.assertEqual(original,[1,3,5,7])
 def test_missing_failed_shard_is_explicit_and_duplicate_report_rejected(self):
  progress={'shard_index':0,'shard_count':2,'assigned':4,'processed':2,'unprocessed':2,'saved_with_remaining_work':1,'abstract_found':1,'fulltext_found':0}
  summary=aggregate([progress],8)
  self.assertEqual(summary['missing_shards'],[1]);self.assertFalse(summary['all_shards_reported']);self.assertEqual(summary['unreported_assigned'],4)
  with self.assertRaises(ValueError):aggregate([progress,progress],8)
 def test_two_shard_counts_do_not_duplicate_missing_papers(self):
  rows=[{'shard_index':i,'shard_count':2,'assigned':4,'processed':2,'unprocessed':2,'saved_with_remaining_work':1,'abstract_found':1,'fulltext_found':0} for i in range(2)]
  r=aggregate(rows,8);self.assertEqual(r['processed'],4);self.assertEqual(r['unprocessed'],4);self.assertEqual(r['total_remaining_papers'],6)
 def test_result_write_rejects_other_shard_before_creating_file(self):
  import run,tempfile
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as directory,patch.object(run,'ROOT',Path(directory)),patch.object(run,'OWNED_IDS',{'mine'}):
   with self.assertRaises(ValueError):run.store_json(Path(directory)/'results/other.json',{})
   self.assertFalse((Path(directory)/'results/other.json').exists())
 def test_shared_capture_parallel_writes_preserve_every_hash(self):
  import run,tempfile,hashlib
  from unittest.mock import patch
  from concurrent.futures import ThreadPoolExecutor
  with tempfile.TemporaryDirectory() as directory,patch.object(run,'BASE',Path(directory)),patch.object(run,'RAW',Path(directory)/'raw'):
   def save(i):return run.capture('_batches','same-query.json',str(i),'https://example.org/ui')
   with ThreadPoolExecutor(max_workers=8) as pool:records=list(pool.map(save,range(32)))
   self.assertEqual(len({r['path'] for r in records}),32)
   for i,r in enumerate(records):
    data=(Path(directory)/r['path']).read_bytes();self.assertEqual(data,str(i).encode());self.assertEqual(hashlib.sha256(data).hexdigest(),r['sha256'])
 def test_http_failure_metrics_retain_host_and_request_type_without_query(self):
  import resume
  from types import SimpleNamespace
  response=SimpleNamespace(status=503,url='https://provider.test/paper?private=value',request=SimpleNamespace(resource_type='document'))
  metrics={};resume.observe_response(response,metrics)
  self.assertEqual(metrics['all_http_5xx'],1);self.assertEqual(metrics['http_failures'][0],{'status':503,'host':'provider.test','path':'/paper','resource_type':'document'})
if __name__=='__main__':unittest.main()
