"""Fixed original-position ownership and read-only progress aggregation."""
def partition(papers,index,count):
 if count not in (1,2) or not 0<=index<count:raise ValueError('Expected one or two fixed shards and a valid index.')
 return [paper for position,paper in enumerate(papers) if position%count==index]

def aggregate(rows,assigned):
 if not rows:return {'assigned':assigned,'all_shards_reported':False,'unreported_assigned':assigned}
 counts={r['shard_count'] for r in rows};indices=[r['shard_index'] for r in rows]
 if len(counts)!=1 or len(set(indices))!=len(indices):raise ValueError('Inconsistent or duplicate shard progress.')
 count=counts.pop()
 if count not in (1,2) or any(i not in range(count) for i in indices):raise ValueError('Invalid shard identity.')
 result={'assigned':assigned,'missing_shards':sorted(set(range(count))-set(indices)),'unreported_assigned':assigned-sum(r['assigned'] for r in rows)}
 if result['unreported_assigned']<0:raise ValueError('Shard assignment exceeds global assignment.')
 result['all_shards_reported']=not result['missing_shards'] and not result['unreported_assigned']
 for key in ('processed','unprocessed','saved_with_remaining_work','abstract_found','fulltext_found'):result[key]=sum(r[key] for r in rows)
 result['total_remaining_papers']=result['unprocessed']+result['saved_with_remaining_work']+result['unreported_assigned']
 return result
