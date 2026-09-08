"""Operator snapshot from unique result IDs; never add whole shard totals."""
import json,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from work_queue import pending_work

def summarize(rows,assigned_ids):
 unique={}
 for row in rows:
  pid=row['paper_id']
  if pid not in assigned_ids:raise ValueError('Result is outside assignment.')
  if pid in unique and unique[pid]!=row:raise ValueError('Conflicting observations of one result ID.')
  unique[pid]=row
 values=list(unique.values());unprocessed=len(assigned_ids)-len(values);pending=sum(bool(pending_work(row)) for row in values)
 return {'assigned':len(assigned_ids),'processed':len(values),'unprocessed':unprocessed,'remaining':unprocessed,'saved_with_remaining_work':pending,'total_remaining_papers':pending+unprocessed,'abstract_found':sum(row['abstract']['status']=='found' for row in values),'fulltext_found':sum(row['fulltext']['status']=='found' for row in values),'unresolved':sum(any(row[k]['status']=='unresolved' for k in ('identity','abstract','fulltext')) for row in values)}

if __name__=='__main__':
 base=ROOT.parents[1];assignment=json.loads((ROOT/'assignment.json').read_text(encoding='utf-8-sig'))
 assigned={json.loads(line)['paper_id'] for line in (base/assignment['members_path']).read_text(encoding='utf-8-sig').splitlines() if line.strip()}
 rows=[json.loads(path.read_text(encoding='utf-8')) for path in (ROOT/'results').glob('*.json')]
 result=summarize(rows,assigned);result.update(stage='operator-unique-result-snapshot',updated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),aggregation='Unique assigned paper_id, read from atomic result checkpoints; shard progress totals are not summed.')
 temporary=ROOT/('progress.'+uuid.uuid4().hex+'.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');temporary.replace(ROOT/'progress.json');print(json.dumps(result,ensure_ascii=False))
