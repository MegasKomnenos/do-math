import collections
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from collect_evidence import ROOT, BASE, REPO, SNAPSHOT, save, query

def git_bytes(path):
    return subprocess.check_output(['git','-C',str(REPO),'show',f'{SNAPSHOT}:{path}'])

def git_json(path):
    return json.loads(git_bytes(path))

def seconds(a,b):
    return round((datetime.fromisoformat(b)-datetime.fromisoformat(a)).total_seconds(),3) if a and b else None

def main():
    for kind in ['events','formal-result','identity-assessment','review-cycle','reservations','integrations','history']:
        if not (ROOT/'evidence'/f'{kind}.json').exists(): print(query(kind), flush=True)
    executions=json.loads((ROOT/'evidence/execution.json').read_text(encoding='utf-8'))['records']
    summaries=[]
    for n, ex in enumerate(executions,1):
        result=git_json(ex['result_ref']) if ex.get('result_ref') else {}
        output=result.get('output',{}) or {}
        save(ROOT/'evidence/outputs'/f'{n:02d}-{ex["id"]}.json', output)
        local=result.get('execution',{}) or {}
        collect=local.get('collect',{}) or {}
        # Keep only explicit metadata; never duplicate provider raw text/base64.
        row={k:ex.get(k) for k in ['id','role','model','effort','created_at','started_at','ended_at','outcome','error','error_kind','authority_revocation','currentness_changes','execution_window','result_disposition','integration_result','continuation_of','result_ref','artifact_bundle','input_metrics','usage']}
        row.update(number=n,seconds=seconds(ex.get('started_at'),ex.get('ended_at')),
                   target=ex.get('action',{}).get('target'),action_id=ex.get('action',{}).get('id'),
                   stage=ex.get('action',{}).get('stage'),action_reason=ex.get('action',{}).get('reason'),
                   action_evidence_refs=ex.get('action',{}).get('evidence_refs'),
                   prompt_bytes=(ex.get('input_manifest') or {}).get('prompt',{}).get('bytes') if isinstance(ex.get('input_manifest'),dict) else None,
                   result_status=result.get('status'),result_error=result.get('error'),
                   provider_result_status=result.get('provider_result_status'),
                   collect_diagnostics=collect.get('diagnostics'),
                   output_summary=output.get('summary'),output_report=output.get('report'),
                   output_decision=output.get('decision'),output_disposition=output.get('disposition'),
                   result_keys=list(result),execution_keys=list(local),collect_keys=list(collect))
        summaries.append(row)
    save(ROOT/'evidence/execution-analysis.json',summaries)
    fields=['number','id','role','stage','model','effort','started_at','ended_at','seconds','outcome','error','target','continuation_of','prompt_bytes','result_ref']
    with (ROOT/'executions.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k) for k in fields} for r in summaries)
    totals={}
    for r in summaries:
        for k,v in (r.get('usage') or {}).items():
            if isinstance(v,(int,float)):totals[k]=totals.get(k,0)+v
    stats={'count':len(summaries),'outcomes':dict(collections.Counter(r['outcome'] for r in summaries)),
           'roles':dict(collections.Counter(r['role'] for r in summaries)),
           'usage':totals,'sum_execution_seconds':sum(r['seconds'] or 0 for r in summaries),
           'roles_detail':[]}
    for role in dict.fromkeys(r['role'] for r in summaries):
        rs=[r for r in summaries if r['role']==role]
        stats['roles_detail'].append({'role':role,'count':len(rs),'outcomes':dict(collections.Counter(r['outcome'] for r in rs)),
            'seconds':sum(r['seconds'] or 0 for r in rs),'usage':{k:sum((r.get('usage') or {}).get(k,0) for r in rs) for k in totals}})
    save(ROOT/'evidence/statistics.json',stats)
    print(json.dumps(stats,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
