"""Manager reconciliation of immutable task evidence and current source bytes."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).parent
T = RUN / 'phases/014/tasks/scholarly-smoke'
E = T / 'evidence'
S = R / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(S), str(S/'tests')]
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v): (O/n).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def command(n, argv):
    p = subprocess.run(argv, cwd=R, capture_output=True)
    save(n, {'argv':argv,'cwd':str(R),'exit_code':p.returncode,
             'stdout':p.stdout.decode('utf-8', errors='replace'),'stderr':p.stderr.decode('utf-8', errors='replace')})
    assert p.returncode == 0, n

command('report-check.json', [sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'014','scholarly-smoke'])
start, final = (read(E/n) for n in ('source-start.json','source-final.json'))
previous = read(RUN/'phases/013/manager-evidence/source-inspected.json')
assert all(start.get(p)==h for p,h in previous.items())
current = {p:sha(R/p) for p in final}
assert current == final
save('source-inspected.json', current)
changes = {p for p in start.keys() | final.keys() if start.get(p)!=final.get(p)}
report = read(T/'report.json')
assert changes == {c['path'] for c in report['changes']}
writes = read(RUN/'phases/014/phase.json')['tasks'][0]['writes']
assert all(any(p==w or w.endswith('/') and p.startswith(w) for w in writes) for p in changes)
suites=[]
for n in ['live-01','live-02','live-final','canonical-related','mirror-related','canonical-final','mirror-final']:
    v=read(E/n/'report.json'); c=read(E/(n+'.command.json'))
    rows=[r for g in v['reports'] for r in g['rows'] if not r.get('fixture')]
    assert len(rows)==len(v['selected'])==len({r['id'] for r in rows})
    assert {r['id'] for r in rows}==set(v['selected'])
    assert dict(Counter(r['outcome'] for r in rows))==v['counts']
    assert not v['changed_during_run']
    tree=R/('.agents' if n.startswith('mirror') else '.claude')/'skills/do-math/scripts'
    diff=[p for p,h in v['source_sha256'].items() if sha(tree/p)!=h]
    if n.endswith('final'):
        assert v['complete'] and v['successful'] and c['exit_code']==0
        assert all(r['outcome']=='passed' for r in rows)
    if n in ['canonical-final','mirror-final']: assert not diff
    suites.append({'name':n,'selected':v['selected'],'counts':v['counts'],'exit':c['exit_code'],
                   'complete':v['complete'],'successful':v['successful'],'source_count':len(v['source_sha256']),
                   'current_source_differences':diff,'seconds':v['total_seconds']})
assert suites[-1]['selected']==suites[-2]['selected']

from support.scholarly_live import list_sources_observation
from do_math.codex_worker import build_argv
from do_math.codex_stream import parse_jsonl
from do_math.provider_final import final_bytes, semantic_output
smoke_path=next((E/'live-final').rglob('smoke.json'))
smoke=read(smoke_path); root=smoke_path.parent; call=root/'files/evidence'; workspace=root/'files/workspace'
assert smoke['passed'] and smoke['runner_calls']==1 and len(smoke['checks'])==16 and all(smoke['checks'].values())
registry=read(root/'registry.stdout.json')
raw=(call/'stdout.jsonl').read_bytes()
events=[json.loads(line) for line in raw.splitlines() if line.strip()]
mcp=[e for e in events if e.get('item',{}).get('type')=='mcp_tool_call']
assert [e['type'] for e in mcp]==['item.started','item.completed']
first,last=[e['item'] for e in mcp]
assert first['id']==last['id'] and last['status']=='completed' and last['error'] is None
assert all((e['item']['server'],e['item']['tool'],e['item']['arguments'])==('scholarly','list_sources',{}) for e in mcp)
payload=json.loads(last['result']['content'][0]['text'])
assert payload==last['result']['structured_content']
assert payload['status']=='ok' and {s['id']:s for s in payload['sources']}=={s['id']:s for s in registry['sources']}
native=list_sources_observation(raw,registry['sources'])
assert native['structured_content_present'] and native['structuredContent']==payload
old_observation=smoke['native_list_sources']['structured_content_present']
assert old_observation is False
request_path=Path(smoke['worker_snapshot']['path']); request=read(request_path); status=read(call/'worker-status.json')
assert request['model']=='gpt-6-astra' and request['effort']=='low' and request['max_runtime_seconds'] is None
argv=build_argv(request)
assert sha(request_path)==status['request_sha256']
assert hashlib.sha256('\0'.join(argv).encode('utf-8')).hexdigest()==status['argv_sha256']
assert sha(Path(request['prompt_path']))==status['stdin_sha256']
assert sha(Path(request['output_schema_path']))==status['schema_sha256']
assert status['state']=='exited' and status['cli_exit_code']==0
assert Path(request['cwd']).resolve()==workspace.resolve()
server=read(E/'server-selection.json')['server']
assert request['scholarly_server']==server
data_dir=str(workspace.resolve()/'scholarly-data')
assert 'mcp_servers.scholarly.args='+json.dumps([*server['args'],'--data-dir',data_dir],ensure_ascii=False) in argv
saved=read(root/'files/report.json'); result=saved['result']; collected=result['execution']['collect']
assert collected['result']=='output_collected' and not collected['reasons']
barrier=collected['termination_barrier']
assert barrier['confirmed'] and barrier['root_signaled'] and barrier['active_processes']==0 and barrier['process_ids']==[]
final_bytes_actual=final_bytes(parse_jsonl(raw))
assert final_bytes_actual==(call/'final.txt').read_bytes() and semantic_output('codex',final_bytes_actual)==result['output']
nonce=read(call/'output.schema.json')['properties']['nonce']['const']
assert (workspace/'probe-evidence.txt').read_bytes()==nonce.encode('utf-8')
for p,h in registry['source_sha256'].items(): assert sha(Path(server['args'][0]).parent/p)==h
for k in ['cli_identity','server_python']: assert sha(Path(smoke[k]['path']))==smoke[k]['sha256']
calls=[]
for n in ['live-01','live-02','live-final']:
    p=next((E/n).rglob('stdout.jsonl')); obs=list_sources_observation(p.read_bytes(),registry['sources'])
    calls.append({'name':n,'path':p.relative_to(RUN).as_posix(),'sha256':sha(p),'tool_id':obs['tool_id'],'sources':len(obs['sources'])})
promotion=read(E/'promotion.json')
for row in promotion['recordings']:
    p=S/'tests/corpus'/row['path']; source=R/row['source']
    assert p.read_bytes()==source.read_bytes() and sha(p)==row['sha256']

task_verification=read(E/'verification-final.json')
for p in task_verification['reused_inputs']: assert start[p]==final[p]
for row in task_verification['host_recordings_reused']: assert sha(RUN/row['path'])==row['sha256']
tool=task_verification['host_tool_conditions']
for p,h in [('python','python_sha256'),('pythonw','pythonw_sha256'),('powershell','powershell_sha256_now')]: assert sha(Path(tool[p]))==tool[h]
for p,h in task_verification['lean_tool_executables_preserved'].items(): assert sha(Path(p))==h
manifest=read(S/'tests/corpus/manifest.json'); before=read(E/'manifest-before.json')
assert manifest['entries'][:-1]==before['entries'] and manifest['supported_stream_versions']==before['supported_stream_versions']
for p in task_verification['old_corpus_nonmanifest_preserved']: assert start[p]==final[p]
spec=importlib.util.spec_from_file_location('audit',E/'audit_artifacts.py'); audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
audit.OUT=O; audit.corpus_audit()
corpus=read(O/'corpus-final.json')
command('mirror-check.json',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
assert all(sha(R/p)==h for p,h in current.items())
save('verification.json',{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),
     'source_count':len(current),'start_count':len(start),'previous_count':len(previous),'changes':sorted(changes),
     'suites':suites,'calls':calls,'promotion_files':len(promotion['recordings']),'live_checks':smoke['checks'],
     'barrier':barrier,'registry_count':len(registry['sources']),'native_content_structured_equal':True,
     'historical_smoke_structured_present':old_observation,'native_sha256':hashlib.sha256(raw).hexdigest(),
     'reused_inputs':task_verification['reused_inputs'],'mirror_transformed_inputs':task_verification['mirror_transformed_inputs'],
     'corpus':{k:{'entries':v['entries'],'files':v['file_count'],'bytes':v['bytes'],'sha_references':len(v['sha_refs'])} for k,v in corpus['trees'].items()},
     'limitations':['No new live call or complete general/T3/mutation run by manager.',
                    'Historical live failures remain failures; structured-content correction reuses the same native bytes.',
                    'Only list_sources and local termination; no search/fetch, remote termination, wire negotiation or actual model/cost proof.']})
print('PASS manager reconciliation: source, reports, native, reuse, raw corpus and mirror')
