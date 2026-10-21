import json
import hashlib
import subprocess
import sys
from pathlib import Path
from collect_evidence import ROOT, BASE, REPO, SNAPSHOT, save
from analyze_records import git_bytes

def main():
    rows=json.loads((ROOT/'evidence/execution.json').read_text(encoding='utf-8'))['records']
    frozen=BASE/'work/operator/bootstrap/cf10dcac0e0caefc42f947189c4be90fad298411e6c8f960b1ece0ef8ef9460a'
    live=Path(r'C:\math\.agents\skills\do-math')
    ex=next(e for e in rows if e['id']=='EX-01M5E6DN6P0GD8BVQT86GSJMC3')
    rawpath=str(Path(ex['result_ref']).parent/'provider-evidence/stdout.jsonl').replace('\\','/')
    original=git_bytes(rawpath)
    input_path=ROOT/'evidence/literature-stdout.jsonl'
    input_path.write_bytes(original)
    code="""import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from do_math.codex_stream import parse_jsonl
raw=Path(sys.argv[2]).read_bytes()
p=parse_jsonl(raw)
keys=['parsed_bytes','unparsed_tail_bytes','parse_complete','turn_completed','turn_failed','unknown_events','web_search_envelopes','usage']
r={k:p.get(k) for k in keys}
r['final_sha256']=hashlib.sha256(p['final_text'].encode()).hexdigest() if p.get('final_text') else None
print(json.dumps(r))
"""
    parses={}
    for label, install in [('frozen_before',frozen),('live_after',live)]:
        p=subprocess.run([sys.executable,'-B','-c',code,str(install/'scripts'),str(input_path)],capture_output=True)
        if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
        parses[label]=json.loads(p.stdout)
    finalpath=str(Path(ex['result_ref']).parent/'provider-evidence/final.txt').replace('\\','/')
    parses['preserved_final_sha256']=hashlib.sha256(git_bytes(finalpath)).hexdigest()
    parses['matches_preserved_final']=parses['live_after']['final_sha256']==parses['preserved_final_sha256']
    save(ROOT/'evidence/parser-reproduction.json',parses)
    # Copy exact source excerpts as read-only audit evidence, preserving path/hash metadata.
    paths=['scripts/do_math/codex_stream.py','scripts/do_math/observation_transport.py','scripts/do_math/model_call.py','scripts/do_math/model_runner.py','scripts/do_math/scheduled_operator.py','scripts/do_math/engine.py','scripts/do_math/submission.py','scripts/do_math/observations.py','scripts/do_math/repair_execution.py','references/자기-점검.md']
    copies=[]
    for path in paths:
        for label,install in [('frozen',frozen),('live',live)]:
            src=install/path
            if not src.exists():continue
            dest=ROOT/'evidence/source'/label/path
            dest.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes();dest.write_bytes(data)
            copies.append({'edition':label,'source':str(src),'copy':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()})
    save(ROOT/'evidence/source-manifest.json',copies)
    # Aggregate usage: raw successful terminal observations are distinct from the accepted ledger.
    logs=json.loads((ROOT/'evidence/log-inspection.json').read_text(encoding='utf-8'))
    totals={}; observed=0
    for log in logs:
        terms=[t['event'] for t in log['terminal'] if t['event']['type']=='turn.completed']
        if len(terms)==1:
            observed+=1
            for k,v in terms[0].get('usage',{}).items():
                if isinstance(v,(int,float)):totals[k]=totals.get(k,0)+v
    save(ROOT/'evidence/terminal-usage.json',{'complete_terminal_count':observed,'ai_execution_count':len(logs),'totals':totals,'note':'Diagnostic sum of one turn.completed per stream. The rejected literature stream is inspected, not retrospectively accepted. Two cancelled executions have no terminal usage here.'})
    print(json.dumps({'parser_before':{k:v for k,v in parses['frozen_before'].items() if k not in ['usage']},'parser_after':{k:v for k,v in parses['live_after'].items() if k not in ['usage','web_search_envelopes']},'final_matches':parses['matches_preserved_final'],'terminal_usage':totals},ensure_ascii=False))

if __name__=='__main__':main()
