"""Reconcile original reports, worker/native bytes, preserved inputs and corpus."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
E = Path(__file__).parent
S = R / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(S), str(S / 'tests')]
from do_math.codex_stream import parse_jsonl
from support.scholarly_live import list_sources_observation

def read(p):
    return json.loads(p.read_bytes())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

start = read(E / 'source-start.json')
paths = set(start)
for prefix in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
    paths.update(p.relative_to(R).as_posix() for p in (R / prefix).rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
final = {p:sha(R / p) for p in sorted(paths) if (R / p).is_file()}
save('source-final.json', final)
changes = {p:{'before':start.get(p),'after':final.get(p)} for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)}
writes = read(RUN / 'phases/014/phase.json')['tasks'][0]['writes']
outside = [p for p in changes if not any(p==w or w.endswith('/') and p.startswith(w) for w in writes)]
assert not outside, outside
assert not read(E / 'start-comparison.json')['changed_from_013']

suites = []
for name in ['live-01','live-02','live-final','canonical-related','mirror-related','canonical-final','mirror-final']:
    result = read(E / name / 'report.json')
    rows = [row for group in result['reports'] for row in group['rows']]
    selected = result['selected']
    assert len(rows)==len({row['id'] for row in rows})==len(selected)
    assert set(selected)=={row['id'] for row in rows}
    assert not result['changed_during_run']
    command = read(E / (name + '.command.json'))
    item = {'folder':name,'selected':selected,'rows':rows,'counts':result['counts'],
            'complete':result['complete'],'successful':result['successful'],'actual_exit':command['exit_code'],
            'source_count':len(result['source_sha256']),'seconds':result['total_seconds'],'changed_during_run':result['changed_during_run']}
    tree = '.agents' if name.startswith('mirror') else '.claude'
    differences = [p for p,h in result['source_sha256'].items() if sha(R/tree/'skills/do-math/scripts'/p)!=h]
    item['source_current_differences'] = differences
    if name in ['live-final','canonical-final','mirror-final']:
        assert result['complete'] and result['successful'] and command['exit_code']==0
        assert all(row['outcome']=='passed' for row in rows)
    if name in ['canonical-final','mirror-final']:
        assert not differences
    suites.append(item)
assert suites[-1]['selected']==suites[-2]['selected']

smoke_path = next((E/'live-final').rglob('smoke.json'))
smoke = read(smoke_path)
assert smoke['passed'] and smoke['runner_calls']==1 and all(smoke['checks'].values())
call = smoke_path.parent/'files/evidence'
request_path = Path(smoke['worker_snapshot']['path'])
request = read(request_path)
status = read(call/'worker-status.json')
assert request['model']=='gpt-6-astra' and request['effort']=='low' and request['max_runtime_seconds'] is None
assert status['request_sha256']==sha(request_path)
assert status['stdin_sha256']==sha(Path(request['prompt_path']))
assert status['schema_sha256']==sha(Path(request['output_schema_path']))
assert status['state']=='exited' and status['cli_exit_code']==0
probe = read(smoke_path.parent/'files/report.json')
collected = probe['result']['execution']['collect']
assert collected['result']=='output_collected' and not collected['reasons']
barrier = collected['termination_barrier']
assert barrier['confirmed'] and barrier['root_signaled'] and barrier['active_processes']==0 and barrier['process_ids']==[]
registry = read(smoke_path.parent/'registry.stdout.json')
for p,h in registry['source_sha256'].items():
    assert sha(Path(smoke['server']['args'][0]).parent/p)==h
for key in ('cli_identity','server_python'):
    assert sha(Path(smoke[key]['path']))==smoke[key]['sha256']
native = list_sources_observation((call/'stdout.jsonl').read_bytes(),registry['sources'])
assert native['structured_content_present'] and native['structuredContent']==json.loads(native['content'][0]['text'])
save('native-observation-current.json', {'source':smoke_path.relative_to(RUN).as_posix(),
    'raw_sha256':sha(call/'stdout.jsonl'),'current_observer_sha256':sha(S/'tests/support/scholarly_live.py'),
    'observation':native,'correction':'Original live smoke queried camelCase rather than the actual native structured_content key; immutable report retained. Current observer checks both complete bodies in the same actual recording.',
    'no_new_call':'Only the observer/replay/docs changed; actual probe prompt/schema/worker/adapter inputs and runtime remain unchanged.'})
calls = []
for name in ['live-01','live-02','live-final']:
    stream = next((E/name).rglob('stdout.jsonl'))
    original = [json.loads(line) for line in stream.read_bytes().splitlines() if line.strip()]
    mcp = [e for e in original if e.get('item',{}).get('type')=='mcp_tool_call']
    assert len([e for e in mcp if e['type']=='item.started'])==1
    assert len([e for e in mcp if e['type']=='item.completed'])==1
    assert all((e['item']['server'],e['item']['tool'],e['item']['arguments'])==('scholarly','list_sources',{}) for e in mcp)
    calls.append({'folder':name,'path':stream.relative_to(RUN).as_posix(),'sha256':sha(stream),
                  'mcp_requests':1,'native_current_observation':{k:v for k,v in list_sources_observation(stream.read_bytes(),registry['sources']).items()
                       if k not in ('content','structuredContent','sources')}})

old = read(RUN/'phases/012/tasks/lean-smoke/evidence/verification-final.json')
reuse = old['runtime_paths']+old['provider_inputs']+old['host_inputs']
reuse += [f'{tree}/skills/do-math/scripts/tests/{p}' for tree in ('.claude','.agents')
          for p in ('smoke/test_lean_live.py','support/lean_live.py','smoke/test_scheduler_live.py','support/scheduler_live.py')]
assert all(start[p]==final[p] for p in reuse)
host_records = old['host_recordings_reused']
assert all(sha(RUN/p['path'])==p['sha256'] for p in host_records)
tools = old['host_tool_conditions_reused']
for p,h in [('python','python_sha256'),('pythonw','pythonw_sha256'),('powershell','powershell_sha256_now')]:
    assert sha(Path(tools[p]))==tools[h]
lean = read(RUN/'phases/012/tasks/lean-smoke/evidence/live-final-observation.json')
assert all(sha(Path(p))==h for p,h in lean['executables'].items())

corpus = read(E/'corpus-final.json')
before = read(E/'manifest-before.json')
current = read(S/'tests/corpus/manifest.json')
assert current['entries'][:-1]==before['entries'] and current['supported_stream_versions']==before['supported_stream_versions']
old_files = [p for p in start if '/tests/corpus/' in p and not p.endswith('/manifest.json')]
assert len(old_files)==122 and all(start[p]==final[p] for p in old_files)
assert all(corpus[k] for k in ('raw_clean_equal','sha_refs_match','mirror_bytes_equal'))
assert all(t['entries']==22 and t['bytes']<=5*1024*1024 for t in corpus['trees'].values())

# Replay and live use official mirror transforms, including the runtime imports
# consumed by the existing probe; path relocation is not a second live call.
spec = importlib.util.spec_from_file_location('builder',R/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
rules = builder.load_rules(R/'.agents/diff')
mirror_inputs = list(old['runtime_paths'])+old['provider_inputs']+['.claude/skills/do-math/scripts/tests/support/scholarly_live.py',
                 '.claude/skills/do-math/scripts/tests/smoke/test_scholarly_live.py']
mirrored = []
for p in mirror_inputs:
    if not p.startswith('.claude/skills/'):
        continue
    relative = p.removeprefix('.claude/skills/')
    other = R/'.agents/skills'/relative
    assert builder.transform(relative,(R/p).read_bytes(),rules)==other.read_bytes()
    mirrored.append(p)

historical = R/'docs/do-math/개선-검증-2026-09-16/operator-probe.json'
h = read(historical)
historical_paths = [Path(h['run_directory'])/'evidence/stdout.jsonl',Path(h['original_result_path'])]
save('history-original-reports.json', {'report':historical.relative_to(R).as_posix(),'report_sha256':sha(historical),
    'original_paths':[{'path':str(p),'exists':p.exists()} for p in historical_paths],
    'judgment':'Existing report is descriptive history; its absent native/raw paths cannot establish current list_sources success or add historical counts.'})

record = {'at_utc':datetime.now(timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),
          'source_start_count':len(start),'source_final_count':len(final),'changes':changes,'outside_writes':outside,
          'suites':suites,'actual_calls':calls,'live_checks':smoke['checks'],'barrier':barrier,
          'structured_current_observation':'native-observation-current.json','runtime_preserved':old['runtime_paths'],
          'reused_inputs':reuse,'host_recordings_reused':host_records,'host_tool_conditions':tools,
          'lean_tool_executables_preserved':lean['executables'],'old_corpus_nonmanifest_preserved':old_files,
          'mirror_transformed_inputs':mirrored,
          'limitations':['No new mirror paid call; offline parser/configuration and exact official transform establish limited reuse.',
                         'Native MCP initialize handshake/protocolVersion and wire isError not separately emitted; native status/error and complete successful payload checked.',
                         'Initial official error/failure and initial structured-content observation retained unchanged.',
                         'No literature search/fetch, account/credential/service changes, research operation, whole general/T3/mutation or final review.']}
save('verification-final.json',record)
print('verified',len(changes),'changes;',[(x['folder'],x['counts']) for x in suites],'; source preservation and native structured body pass')
