import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
E = RUN / 'phases/012/tasks/lean-smoke/evidence'
PYTHON = sys.executable

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot(name):
    previous = json.loads((RUN / 'phases/011/manager-evidence/source-inspected.json').read_bytes())
    paths = set(previous)
    for prefix in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
        for path in (REPO / prefix).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                paths.add(path.relative_to(REPO).as_posix())
    result = {p: digest(REPO / p) for p in sorted(paths) if (REPO / p).is_file()}
    save(E / (name + '.json'), result)
    if name == 'source-start':
        differences = {p: [previous.get(p), result.get(p)] for p in previous if previous.get(p) != result.get(p)}
        save(E / 'start-comparison.json', {'previous_count':len(previous), 'current_count':len(result), 'differences':differences})
    print(name, len(result))

def command(name, argv):
    record = {'argv':argv, 'cwd':str(REPO), 'started_at':datetime.now(timezone.utc).isoformat()}
    with (E / (name + '.stdout')).open('wb') as out, (E / (name + '.stderr')).open('wb') as err:
        process = subprocess.Popen(argv, cwd=REPO, stdout=out, stderr=err,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        record['pid'] = process.pid
        save(E / (name + '.started.json'), record)
        record['exit_code'] = process.wait()
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    save(E / (name + '.command.json'), record)
    print(name, 'exit', record['exit_code'])
    print((E / (name + '.stdout')).read_text(encoding='utf-8', errors='replace')[-2200:])
    print((E / (name + '.stderr')).read_text(encoding='utf-8', errors='replace')[-1800:])
    return record['exit_code']

def read_inputs():
    phase = json.loads((RUN / 'phases/012/phase.json').read_bytes())
    observations = []
    for reference in phase['tasks'][0]['inputs']:
        root, relative = reference.split(':', 1)
        path = (REPO if root == 'repo' else RUN) / relative
        raw = path.read_bytes()
        row = {'reference':reference, 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()}
        if path.suffix == '.json':
            value = json.loads(raw)
            row['keys'] = list(value) if isinstance(value, dict) else None
        observations.append(row)
    save(E / 'input-inventory.json', observations)
    # Select the actual B38 history record, wherever the original indexes place it.
    def collect(value, predicate, found):
        if isinstance(value, dict):
            if predicate(value): found.append(value)
            for child in value.values(): collect(child, predicate, found)
        elif isinstance(value, list):
            for child in value: collect(child, predicate, found)
    for name, path in (
        ('b38-review', RUN / 'phases/001/tasks/closure-map/evidence/prior-review-state.json'),
        ('b38-tracking', REPO / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json')):
        found = []
        collect(json.loads(path.read_bytes()), lambda row:row.get('history_id') == 'B38' or row.get('id') == 'B38', found)
        save(E / (name + '.json'), found)
        print(name, json.dumps(found, ensure_ascii=False)[:14000])
    for relative in ('phases/001/tasks/gate-readiness/evidence/gate-readiness.json',
                     'phases/001/tasks/gate-readiness/evidence/environment.json',
                     'phases/011/tasks/regression-reading/report.json',
                     'phases/011/manager-evidence/verification.json'):
        value = json.loads((RUN / relative).read_bytes())
        print(relative, 'keys', list(value))
    print('inputs', len(observations))

def history():
    records = json.loads((E / 'b38-tracking.json').read_bytes())
    b38 = next(row for row in records if 'actual_lean' in row)
    original = []
    for key, value in b38.items():
        if isinstance(value, dict) and 'path' in value:
            path = Path(value['path'])
            original.append({'selector':'/current_work/git_port_integration/' + key + '/path',
                             'path':str(path), 'exists':path.is_file(),
                             'sha256':digest(path) if path.is_file() else None,
                             'reported_sha256':value.get('sha256')})
    save(E / 'history-original-reports.json', original)
    print(json.dumps(original, ensure_ascii=False, indent=2))
    for relative in ('phases/001/tasks/gate-readiness/evidence/environment.json',
                     'phases/001/tasks/gate-readiness/evidence/gate-readiness.json',
                     'phases/011/tasks/regression-reading/report.json'):
        value = json.loads((RUN / relative).read_bytes())
        if 'environment' in relative:
            print(json.dumps({k:value.get(k) for k in ('which','mathlib_toolchain','lean_test_override_present')}, ensure_ascii=False))
        elif 'gate-readiness' in relative:
            print(json.dumps(value['environment_readiness'], ensure_ascii=False)[:11000])
        else:
            print(json.dumps({k:value[k] for k in ('status','narrative','findings')}, ensure_ascii=False)[:11000])

def summary(folder):
    sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
    from do_math.file_io import read_bytes_shared
    value = json.loads(read_bytes_shared(E / folder / 'report.json'))
    print('report keys', list(value))
    print(json.dumps({k:v for k,v in value.items() if k not in ('reports','source_before','source_after','selected','selection','code_version')}, ensure_ascii=False)[:2500])
    for report in value.get('reports', []):
        print('inner keys', list(report))
        print(json.dumps(report, ensure_ascii=False)[:1800])
    for path in (E / folder).rglob('smoke.json'):
        smoke = json.loads(path.read_bytes())
        print(str(path), smoke.get('checks'), smoke.get('error'))
        print('identity', smoke.get('identity'))

def corpus_audit(name):
    trees = {}
    for prefix in ('.claude/skills/do-math/scripts/tests/corpus', '.agents/skills/do-math/scripts/tests/corpus'):
        root = REPO / prefix
        manifest = json.loads((root / 'manifest.json').read_bytes())
        paths = sorted(p for p in root.rglob('*') if p.is_file())
        rows = []
        for path in paths:
            relative = path.relative_to(REPO).as_posix()
            commands = [['git','hash-object','--no-filters','--',relative],
                        ['git','hash-object','--path=' + relative,relative]]
            completed = [subprocess.run(argv, cwd=REPO, capture_output=True, creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)) for argv in commands]
            rows.append({'path':relative, 'bytes':path.stat().st_size,'sha256':digest(path),
                'argv':commands,'exit_codes':[r.returncode for r in completed],
                'raw_oid':completed[0].stdout.decode().strip(), 'clean_oid':completed[1].stdout.decode().strip(),
                'stderr':[r.stderr.decode(errors='replace') for r in completed]})
        sha_refs = []
        for entry in manifest['entries']:
            for recording in entry.get('recordings', []):
                sha_refs.append({'id':entry['id'], 'path':recording['path'], 'expected':recording['sha256'], 'actual':digest(root / recording['path'])})
            for hash_key, path_key in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
                if hash_key in entry:
                    sha_refs.append({'id':entry['id'],'path':entry[path_key], 'expected':entry[hash_key], 'actual':digest(root / entry[path_key])})
        trees[prefix] = {'entries':len(manifest['entries']), 'file_count':len(paths), 'bytes':sum(row['bytes'] for row in rows),
            'rows':rows, 'sha_refs':sha_refs}
    ordered = list(trees.values())
    result = {'trees':trees,
        'raw_clean_equal':all(row['exit_codes'] == [0,0] and row['raw_oid'] == row['clean_oid'] for tree in ordered for row in tree['rows']),
        'sha_refs_match':all(row['expected'] == row['actual'] for tree in ordered for row in tree['sha_refs']),
        'mirrored_bytes_equal':{r['path'].split('/corpus/')[1]:r['sha256'] for r in ordered[0]['rows']} == {r['path'].split('/corpus/')[1]:r['sha256'] for r in ordered[1]['rows']}}
    save(E / (name + '.json'), result)
    print(name, [(v['entries'],v['file_count'],v['bytes'],len(v['sha_refs'])) for v in ordered], {k:v for k,v in result.items() if k != 'trees'})
    assert all(result[k] for k in ('raw_clean_equal','sha_refs_match','mirrored_bytes_equal'))

def promote():
    paths = list((E / 'live-final').rglob('smoke.json'))
    assert len(paths) == 1
    smoke = json.loads(paths[0].read_bytes())
    assert smoke['passed'] and all(smoke['checks'].values())
    scratch = paths[0].parent
    job = Path(smoke['normal_job']['directory'])
    corpus = REPO / '.claude/skills/do-math/scripts/tests/corpus'
    manifest = json.loads((corpus / 'manifest.json').read_bytes())
    original = json.loads((E / 'corpus-start.json').read_bytes())
    assert len(manifest['entries']) == 18
    stem = 'lean/mathlib-live-20261014'
    files = {'path':stem + '.stdout.txt', 'source_path':stem + '.lean',
             'compiled_path':stem + '.compiled.lean', 'stderr_path':stem + '.stderr.txt',
             'provenance_path':stem + '.recording.json'}
    for source, key in ((job / 'out','path'),(scratch / 'normal.lean','source_path'),
                        (job / 'compiled.lean','compiled_path'),(job / 'err','stderr_path')):
        assert not (corpus / files[key]).exists()
        shutil.copyfile(source, corpus / files[key])
    normal = smoke['normal']
    verdict = {key:normal[key] for key in ('status','declaration_signatures','axioms','signature_hash',
                'dependency_closure','declaration_evidence','dependency_evidence')}
    verdict['compiled_input_matches'] = True
    provenance = {'source_evidence':paths[0].relative_to(REPO).as_posix(),
        'recorded_at':smoke['started_at'],'finished_at':smoke['finished_at'],
        'identity':smoke['identity'],'command':normal['command'],
        'cwd':smoke['normal_job']['request']['cwd'], 'worker':smoke['normal_job']['identity'],
        'job_name':smoke['normal_job']['job_name'],'exit_code':normal['exit_code'],
        'extract_evidence':True, 'lean_source_sha256':normal['source_sha256'],
        'raw_stdout_sha256':digest(job / 'out'),
        'product_stdout_sha256':hashlib.sha256(normal['stdout'].encode()).hexdigest(),
        'source_complete':True, 'output_complete':True,'truncation':None,
        'scope':'Two small named Mathlib-imported declarations with full dependency extraction; representative Mathlib compile, invalid input and installation fingerprints remain in execution evidence.',
        'checks':smoke['checks']}
    save(corpus / files['provenance_path'], provenance)
    entry = {'id':'lean-mathlib-live-20261014','kind':'lean_output',
        'path':files['path'],'source_path':files['source_path'],'compiled_path':files['compiled_path'],
        'tool_version':smoke['identity']['version'],'recorded_at':smoke['started_at'],
        'command':normal['command'],'cwd':smoke['normal_job']['request']['cwd'],
        'role':'formal_verification','source':paths[0].relative_to(REPO).as_posix(),
        'source_sha256':digest(corpus / files['path']), 'extract_evidence':True,
        'declarations':smoke['declarations'],'verdict':verdict,
        'recordings':[{'path':relative,'sha256':digest(corpus / relative)} for relative in files.values()]}
    manifest['entries'].append(entry)
    save(corpus / 'manifest.json', manifest)
    save(E / 'corpus-promotion.json', {'entry':entry, 'provenance':provenance,
        'raw_bytes_copied':{key:digest(corpus / files[key]) for key in ('path','source_path','compiled_path','stderr_path')},
        'existing_entries_preserved':manifest['entries'][:-1] == json.loads((REPO / '.agents/skills/do-math/scripts/tests/corpus/manifest.json').read_bytes())['entries']})
    print('promoted', entry['id'], len(manifest['entries']), [(relative,(corpus / relative).stat().st_size) for relative in files.values()])

def mirror_plan(name):
    spec = importlib.util.spec_from_file_location('build_skill_mirrors',REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rules = json.loads((REPO / '.agents/diff/_rules.json').read_bytes())
    outputs = {relative:builder.transform(relative,path.read_bytes(),rules) for relative,path in builder.iter_files(REPO / '.claude/skills').items()}
    overlays = builder.iter_files(REPO / '.agents/diff')
    outputs.update({relative:path.read_bytes() for relative,path in overlays.items() if relative not in builder.RESERVED})
    existing = builder.iter_files(REPO / '.agents/skills')
    changed = ['.agents/skills/' + relative for relative,raw in outputs.items() if relative not in existing or existing[relative].read_bytes() != raw]
    removed = ['.agents/skills/' + relative for relative in existing if relative not in outputs]
    writes = json.loads((RUN / 'phases/012/phase.json').read_bytes())['tasks'][0]['writes']
    outside = [path for path in changed + removed if not any(path == w or w.endswith('/') and path.startswith(w) for w in writes)]
    save(E / (name + '.json'), {'changed':changed,'removed':removed,'outside_writes':outside,'output_count':len(outputs)})
    print(name, json.dumps({'changed':changed,'removed':removed,'outside':outside},ensure_ascii=False))
    assert not outside

def smoke_observation(folder):
    smoke_path = next((E / folder).rglob('smoke.json'))
    smoke = json.loads(smoke_path.read_bytes())
    scratch = smoke_path.parent
    assert smoke['passed'] and all(smoke['checks'].values())
    before = json.loads((scratch / 'judgment-before.json').read_bytes())
    after = json.loads((scratch / 'judgment-after.json').read_bytes())
    validation = smoke['validation']
    seconds = (datetime.fromisoformat(validation['finished_at']) - datetime.fromisoformat(validation['started_at'])).total_seconds()
    row = {'smoke_path':smoke_path.relative_to(REPO).as_posix(), 'checks':smoke['checks'],
        'version':smoke['identity']['version'],'executables':smoke['identity']['executables'],
        'configured_command':smoke['identity']['configured_command'],
        'installation_inputs_equal':smoke['installation_before'] == smoke['installation_after'],
        'judgment_files_equal':before == after,'judgment_file_count':len(before['files']),
        'dependencies':smoke['installation_before']['dependencies'],
        'representative_seconds':seconds, 'representative_scope':validation['scope'],
        'normal_status':smoke['normal']['status'],'normal_exit':smoke['normal']['exit_code'],
        'normal_source_sha256':smoke['normal']['source_sha256'],
        'signatures':smoke['normal']['declaration_signatures'], 'signature_hash':smoke['normal']['signature_hash'],
        'declarations':smoke['normal']['declarations'],'axioms':smoke['normal']['axioms'],
        'dependency_count':len(smoke['normal']['dependency_evidence']),
        'invalid_status':smoke['invalid']['status'],'invalid_exit':smoke['invalid']['exit_code'],
        'invalid_reason':smoke['invalid']['reason'],'jobs':len(smoke['jobs']),
        'cleanup':[{k:j[k] for k in ('job_name','identity','root_ended','active_processes','process_ids')} for j in smoke['jobs']]}
    save(E / (folder + '-observation.json'), row)
    print(json.dumps(row, ensure_ascii=False, indent=2)[:8000])

def versions():
    smoke = json.loads(next((E / 'live-final').rglob('smoke.json')).read_bytes())
    command('lake-version', [smoke['identity']['executable'],'--version'])
    command('git-head', ['git','rev-parse','HEAD'])
    save(E / 'host-version-inputs.json', {'python':str(Path(sys.executable)), 'python_sha256':digest(Path(sys.executable)),
        'python_version':sys.version,'path_lean':shutil.which('lean'), 'path_lake':shutil.which('lake'),
        'path_elan':shutil.which('elan'), 'lake':smoke['identity']['executable'],
        'lake_sha256_before':smoke['identity']['sha256'],
        'lake_sha256_after':digest(Path(smoke['identity']['executable']))})

def verification():
    sys.path.insert(0,str(REPO / '.claude/skills/do-math/scripts'))
    from do_math.file_io import read_bytes_shared
    initial = json.loads((E / 'source-start.json').read_bytes())
    final = json.loads((E / 'source-final.json').read_bytes())
    task = json.loads((RUN / 'phases/012/phase.json').read_bytes())['tasks'][0]
    changes = {p:{'before':initial.get(p),'after':final.get(p)} for p in initial.keys() | final.keys() if initial.get(p) != final.get(p)}
    outside = [p for p in changes if not any(p == w or w.endswith('/') and p.startswith(w) for w in task['writes'])]
    suites = {}
    for name in ('live-01','live-02','live-final','canonical-related','mirror-live','mirror-related'):
        report = json.loads(read_bytes_shared(E / name / 'report.json'))
        command_record = json.loads((E / (name + '.command.json')).read_bytes())
        rows = [row for group in report['reports'] for row in group['rows']]
        ids = [row['id'] for row in rows]
        tree = '.agents' if any('.agents/skills/do-math/scripts/run_tests.py' in arg for arg in command_record['argv']) else '.claude'
        mismatches = {p:[hashvalue,digest(REPO / tree / 'skills/do-math/scripts' / p)] for p,hashvalue in report['source_sha256'].items()
                      if not (REPO / tree / 'skills/do-math/scripts' / p).is_file() or digest(REPO / tree / 'skills/do-math/scripts' / p) != hashvalue}
        expected = name not in ('live-01','live-02')
        row = {'selected':report['selected'],'row_ids':ids,'counts':report['counts'],
            'complete':report['complete'],'successful':report['successful'],'exit_code':command_record['exit_code'],
            'source_python_count':len(report['source_sha256']),'source_mismatches':mismatches,
            'changed_during_run':report['changed_during_run'],'seconds':report['total_seconds'],
            'budget':report['budget'],'report_sha256':digest(E / name / 'report.json')}
        suites[name] = row
        assert len(ids) == len(set(ids)) and set(ids) == set(report['selected']) and len(ids) == len(report['selected'])
        assert report['complete'] and not report['changed_during_run']
        if expected:
            assert report['successful'] and command_record['exit_code'] == 0 and all(r['outcome'] == 'passed' for r in rows) and not mismatches
        else:
            assert not report['successful'] and command_record['exit_code'] == 1 and report['counts'] == {'error':1}
    assert set(suites['canonical-related']['selected']) == set(suites['mirror-related']['selected'])
    assert suites['live-final']['selected'] == suites['mirror-live']['selected']
    old = json.loads((E / 'corpus-start.json').read_bytes())
    preserved = []
    for tree in old['trees'].values():
        for row in tree['rows']:
            if not row['path'].endswith('/manifest.json'):
                assert digest(REPO / row['path']) == row['sha256']
                preserved.append(row['path'])
    c = json.loads((REPO / '.claude/skills/do-math/scripts/tests/corpus/manifest.json').read_bytes())
    m = json.loads((REPO / '.agents/skills/do-math/scripts/tests/corpus/manifest.json').read_bytes())
    old_manifest = subprocess.run(['git','show','HEAD:.claude/skills/do-math/scripts/tests/corpus/manifest.json'],cwd=REPO,capture_output=True)
    assert old_manifest.returncode == 0
    old_entries = json.loads(old_manifest.stdout)['entries']
    assert c == m and c['entries'][:-1] == old_entries and len(old_entries) == 18
    unchanged_inputs = [p for p in initial if p.startswith('.claude/skills/do-math/scripts/do_math/') and p.endswith('.py')]
    prior = json.loads((RUN / 'phases/011/tasks/regression-reading/evidence/verification-final.json').read_bytes())
    provider = prior['provider_inputs_unchanged']
    host = [p for p in initial if p.endswith(('tests/smoke/test_host_live.py','tests/support/host_live.py'))]
    reused = unchanged_inputs + provider + host
    assert all(initial[p] == final[p] for p in reused)
    host_records = []
    for recorded in prior['host_recordings_reused']:
        path = RUN / recorded['path']
        row = {**recorded,'exists_now':path.is_file(),'sha256_now':digest(path) if path.is_file() else None}
        if path.is_file(): assert row['sha256_now'] == row['sha256']
        host_records.append(row)
    conditions = prior['tool_conditions']
    assert digest(Path(conditions['python'])) == conditions['python_sha256']
    assert digest(Path(conditions['pythonw'])) == conditions['pythonw_sha256']
    assert digest(Path(conditions['powershell'])) == conditions['powershell_sha256_now']
    # Global execution snapshots may differ only at official timing cache writes.
    snapshot_differences = {}
    for left,right in [('source-canonical','source-canonical-after'),('source-mirror','source-mirror-after')]:
        a=json.loads((E / (left+'.json')).read_bytes()); b=json.loads((E / (right+'.json')).read_bytes())
        differing=[p for p in a.keys() | b.keys() if a.get(p)!=b.get(p)]
        assert all(p.endswith('/tests/.timings.json') for p in differing)
        snapshot_differences[left+' to '+right]=differing
    result = {'source_start_count':len(initial),'source_final_count':len(final), 'changes':changes,
        'outside_writes':outside,'suites':suites,'execution_snapshot_differences':snapshot_differences,
        'existing_corpus_files_unchanged':preserved,'old_entries_unchanged':True,
        'runtime_paths':unchanged_inputs,'provider_inputs':provider,'host_inputs':host,
        'reused_inputs_unchanged':True,'host_recordings_reused':host_records,
        'host_tool_conditions_reused':conditions,'corpus_final':json.loads((E / 'corpus-final.json').read_bytes()),
        'corpus_promotion':json.loads((E / 'corpus-promotion.json').read_bytes())}
    assert not outside
    save(E / 'verification-final.json',result)
    print('verified sources',len(initial),len(final),'changes',len(changes),'runtime',len(unchanged_inputs),'provider',provider,'host',host)
    print('suites', {name:(len(row['selected']),row['counts'],row['seconds']) for name,row in suites.items()})

def report():
    verified = json.loads((E / 'verification-final.json').read_bytes())
    ref = lambda path:'run:phases/012/tasks/lean-smoke/evidence/' + path
    checks = []
    for name in ('live-01','live-02','live-final','t5-list','canonical-related','mirror-build','mirror-live','mirror-related','mirror-cache-build','mirror-check','skill-only','lake-version'):
        metadata = json.loads((E / (name+'.command.json')).read_bytes())
        detail = {'live-01':'도우미 상태 타입/Calls 접근 오류로 error1. 원보고와 원spool을 보존했으며 완료 근거로 세지 않는다.',
            'live-02':'대표/정상/타입오류 컴파일은 실제 수행했지만 Calls factory에 futures를 읽은 도우미 오류로 error1. 원보고는 보존한다.',
            'live-final':'Mathlib 대표 컴파일·정상 전체 증거·실제 타입 오류·설치 불변·Job 정리20판정 및 공식1선택/1passed/exit0.',
            'mirror-live':'생성된 미러 경로의 독립 Mathlib 실실행.20판정 및 공식1선택/1passed/exit0. 유료 호출은 없다.',
            't5-list':'T5 discovery6개에 새 Lean1개가 포함됐다. 공급자/host T5는 이번에 실행하지 않았다.',
            'canonical-related':'명시10선택의48고유시험이 전건passed·exit0. corpus3모듈·필수boundary/structure와 Git 정체성/identity8사례를 포함한다.',
            'mirror-related':'정본과 정확히 같은48시험이 전건passed·exit0이며 skip/error/미실행0.',
            'mirror-build':'사전 계획11경로 모두 writes 안. 생성7/갱신4/삭제0, 공식1314파일 생성.',
            'mirror-cache-build':'미러 시험 뒤 비용캐시 한 파일만 공식 재생성. 다른 제품 변화 없음.',
            'mirror-check':'공식 생성물1314파일 drift 없음.',
            'skill-only':'공식 skill-only 구조 검사verified.',
            'lake-version':'실제 탐색한 Lake 실행 파일의 판본을 별도 보존. Lake5.0.0-src+8c9756b/Lean4.32.0이며 성공 컴파일의 대체 근거가 아니다.'}[name]
        evidence=[ref(name+'.command.json'),ref(name+'.stdout'),ref(name+'.stderr')]
        if name in verified['suites']: evidence.append(ref(name+'/report.json'))
        checks.append({'command':subprocess.list2cmdline(metadata['argv']),'cwd':'repo:.',
            'result':'pass' if metadata['exit_code'] == 0 else 'fail','exit_code':metadata['exit_code'],
            'evidence':evidence,'detail':detail})
    for name, argument, evidence, detail in (
        ('corpus','corpus-start','corpus-start.json','기존 양쪽18항목/51파일/223685바이트/50명시SHA 및 총102경로 Git raw/clean·미러 바이트 전건 일치.'),
        ('corpus','corpus-final','corpus-final.json','새 양쪽19항목/56파일의 전112경로 Git raw/clean·명시SHA·미러바이트 전건 일치. 기존18entries/verdict 및100비manifest경로는 불변.'),
        ('verification','','verification-final.json','시작2644/최종2658소스와 정확22변경/writes,6공식 실행의선택/고유row/실제exit/소스 불변,기존 corpus 및 runtime124/공급자입력3/host입력·8원자료와도구 조건을 대조했다.')):
        argv=[PYTHON,'-B',str(E/'task_tools.py'),name] + ([argument] if argument else [])
        checks.append({'command':subprocess.list2cmdline(argv),'cwd':'repo:.','result':'pass','exit_code':0,
                       'evidence':[ref(evidence)],'detail':detail})
    details = {
        'A1':'현재 toolchain_root/discover_lean의 Mathlib 명령과 Lean/Lake SHA·판본, lean-toolchain/manifest/ready marker·9의존 HEAD를 결속했다. 실제 inspect_toolchain 및 verify_environment의 Mathlib 대표프로그램이exit0이다. source/argv/cwd/시각·Job/PID/원stdout/stderr/validation을 보존했다. 설치입력/신뢰기록바이트 및 판단파일11094개 메타데이터가 전후 같고 신뢰 채택/재기록·설치/download는 없다.',
        'A2':'공식 T5 discovery에 lean격리1건을 연결했다. real_ports/worker/Job/clock/검증/parser를 유지해 정상2선언의 정확서명·서명hash·빈axioms·full32의존 증거와 타입오류의exit1/failed/lean rejected/진단을 검사했다. 최종정본1passed/79.4초·미러1passed/84.4초다. 각각5실Job종료/active0/close/named빈값/자기proposal·workspace정리와factory호출0을 확인했다. 초기두도우미오류는 fail원보고로 보존한다.',
        'A3':'새 정상원out71704bytes/source120bytes/compiled6597bytes/빈stderr를 변경·절단 없이 녹화했다. provenance는 실제명령·판본·시각·Job/PID·전체추출범위와원stdout/제품축약stdout SHA를 구별한다. 새full녹화에만 reader full범위를 열고 기존두Lean은 preview경로/기존18entries와판정을 유지했다. 양쪽각56파일/19항목·총112Git경로·모든명시SHA·생성bytes·5MiB상한과 corpus3모듈전건을 통과했다.',
        'A4':'원문설계3.3/4.5/5.1·9-C와 현지침을 대조했고 B38/8afa57c7 formal/setup/Git포트의 실제hunk·현소비자·원보고selector를 검토해 유지했다. 원보고10개부재와 PR02전체미종결을 명시했다. 정본/미러각48선택/고유row전건passed·exit0,각869Python해시와 전후소스가 결속됐다. 생성계획11개·실제11개,캐시만1개동기화·--check1314/skill-only verified. runtime124/공급자입력3/host입력·기존corpus바이트는 불변이며 기존실호출은 승인된한정성질로 재사용한다. 전체일반/T3/변이/나머지G7/최종review는 후속책임이다.'}
    acceptance_evidence = {
        'A1':['start-comparison.json','live-final-observation.json','live-final/report.json','lake-version.stdout','host-version-inputs.json'],
        'A2':['live-final-observation.json','live-final/report.json','mirror-live-observation.json','mirror-live/report.json','t5-list.stdout'],
        'A3':['corpus-promotion.json','corpus-start.json','corpus-final.json','canonical-related/report.json','mirror-related/report.json','verification-final.json'],
        'A4':['review.md','history-b38.stdout','history-original-reports.json','verification-final.json','canonical-related/report.json','mirror-related/report.json','mirror-plan-initial.json','mirror-plan-cache.json','mirror-check.stdout','skill-only.stdout']}
    changes=[]
    for path in sorted(verified['changes']):
        if path.endswith('/tests/.timings.json'): detail='공식 실행 비용캐시 갱신 및 최종 공식 미러 동기화.'
        elif path.endswith('/test_lean_live.py'): detail='실제 Mathlib 대표/정상전체증거/타입오류/설치·자원 불변을 확인하는 lean격리T5 discovery시험 추가.'
        elif path.endswith('/support/lean_live.py'): detail='기존real_ports/entry와 passive ObservedCalls를 사용해 실행·원spool·실설치조건·Job종료를 보존하고 검사하는 시험helper 추가.'
        elif path.endswith('/test_corpus_replay.py'): detail='명시extract_evidence=True인 새Lean녹화의 full서명hash/의존증거와 compiled input을 재생; 기존preview판정은 유지.'
        elif path.endswith('/manifest.json'): detail='기존18항목을 보존하고 새실Lean정상녹화 한 항목·5파일과 명시SHA/판본/실명령/판정을 추가.'
        elif '/corpus/lean/' in path: detail='최종 실제컴파일의 원stdout/source/compiled input/stderr 또는 provenance를 보존한 새녹화. 기존Lean파일은 불변.'
        else: detail='T5 Lean 실행·실환경조건·원자료/full범위·정리·한계를 지침에 추가하고 전체T5선택설명을 갱신.'
        if path.startswith('.agents/'): detail='공식 생성기로 반영한 대응 미러. '+detail
        changes.append({'path':path,'detail':detail})
    value = {'status':'complete',
        'narrative':'phase012 lean-smoke의 A1~A4를 완료했다. 시작2644소스는011 manager의 source-inspected와 전건 같다. 현재 기존 portable Lean4.32.0/Lake5.0.0 및 Mathlib v4.32.0과9의존rev를 직접 확인하고 real_ports로 inspect_toolchain/대표Mathlib컴파일/실제verifier의정상·타입오류를 실행했다. 설치·신뢰기록 채택/수정이나 다운로드는 없고 전후입력바이트/11094판단파일메타데이터는 같다.\n\n최종정본T5 1passed/79.4초·미러1passed/84.4초이고 각각20판정/5실Job정리를 확인했다. source에 명시한ℕ표기와수학적내용에서 기대서명/빈공리/타입오류를 정했으며 signature hash·full32의존/원compiled input을 검사했다. 초기live-01/02는 새도우미의상태타입·Calls factory오해로error1씩이며 실패원보고를 보존했다. 이들을실컴파일최종성공으로 소급하지 않는다. live-02의차가운대표컴파일308.275825초와최종21.170028초는각조건의실측으로만 해석한다. 시간에 따른종료나단언약화는 없다.\n\n최종실정상출력71704bytes·source120·compiled6597·빈stderr를 원바이트로복사하고판본/실명령/시각/Job/PID/full범위를결속했다. 큰설치fingerprint·대표/오류원자료는실행evidence에유지하고출하corpus는작은정상녹화만추가했다. 제품축약stdout은원out과구별한다. 새full녹화의서명hash/의존결과를 현재parser로재생하며 기존두Leanpreview·18entries/verdict·100비manifest경로를보존했다. 최종양쪽19항목/56파일의112Gitraw/clean·명시SHA·미러bytes·5MiB상한이맞는다.\n\n정본/미러관련48건씩이전건passed·exit0이며명시선택과고유row·각869Python해시/실행전후소스가대응한다. corpus3모듈,필수setup/verifierboundary와smell/invariants/ports구조,기존Git정체성8사례를포함한다. 생성계획11개가writes와일치하고공식생성뒤미러실경계를검사했다. 실행뒤비용캐시1개만공식재동기화하고--check1314파일과skill-only를통과했다. 최종2658소스의정확22변경은모두writes안이다.\n\nB38/8afa57c7의formal/setup/Git포트slice는실제diff·현재소비자·원보고selector를대조해유지한다. 원보고10개가없어과거counts는현재성공으로세지않고PR02전체도종료하지않는다. runtime124·공급자입력3·host입력/8원자료와도구조건,기존corpus를보존해011에서승인한실호출의한정성질을재사용한다. 새유료호출/hostT5/예약/학술호출은0이다. Gitstage/commit/reset/checkout/push·graphify갱신·기존연구시작/재개/삭제는없다. 전체일반·freshT3·전체함수변이·나머지G7/읽기조건·최종review 및관리마감은후속manager책임이다.',
        'acceptance':[{'id':key,'result':'pass','detail':detail,'evidence':[ref(p) for p in acceptance_evidence[key]]} for key,detail in details.items()],
        'changes':changes,'seams':[],
        'findings':[
            {'id':'F1','kind':'fact','detail':'현재기존Lean/Mathlib설치에서대표컴파일과실제verifier정상/full32의존·타입오류연쇄가정본/미러T5로완결됐다. 설치입력/신뢰기록·11094판단파일메타데이터는변경없고원자료/5Job정리를보존했다. 이는G7의지정Leanslice증거이며다른실외부와최종G전체의완료가아니다.',
             'evidence':[ref(p) for p in ('live-final-observation.json','mirror-live-observation.json','verification-final.json','review.md')],
             'affects':['run:context.md#C11','run:context.md#G7','run:plan.md'],
             'next_action':'manager가원실행/해시/판정을검수해Lean배정의남김을갱신하고예약·학술·T4보고및최종관문을독립후속배정한다. 설치신뢰승인으로확대하지않는다.'},
            {'id':'F2','kind':'decision','detail':'B38/941fc04cformal/setupGit포트slice를현재필수backend전달·identity별memo·None/미추적/.lake제외·환경/stop/오류계약대로유지한다. 원보고selector10개는현재file이없고과거counts를새성공에합산하지않는다. currentcode/diff·관련8sim·실환경으로이slice만검토했으며PR02전체는미종결이다.',
             'evidence':[ref(p) for p in ('history-b38.stdout','b38-review.json','b38-tracking.json','history-original-reports.json','review.md','canonical-related/report.json')],
             'affects':['run:context.md#C9','run:context.md#G2','run:plan.md','repo:.claude/skills/do-math/scripts/do_math/formal.py','repo:.claude/skills/do-math/scripts/setup_lean.py'],
             'next_action':'manager가해당B38slice유지판정과원보고부재한계를검수해현재맥락에반영한다. 다른PR02slice와최종판본연결책임은유지한다.'},
            {'id':'F3','kind':'fact','detail':'runtime124·공급자입력3·host입력/8원자료·도구조건과기존corpus의비manifest100경로/18entries/verdict가보존됐다. 새녹화1개와현재fullreader·정본/미러48회귀만추가했고기존승인실호출은불변경로의한정성질로재사용한다. 최종변경22개/생성11개·캐시1개동기화는writes안이다.',
             'evidence':[ref(p) for p in ('verification-final.json','corpus-start.json','corpus-final.json','source-start.json','source-final.json','mirror-plan-initial.json','mirror-plan-cache.json')],
             'affects':['run:context.md#C12','run:context.md#G7','run:context.md#G8','run:plan.md'],
             'next_action':'manager가기존실호출재사용/원바이트보존을유지하고이번제품단위를검수·마감한다. 부분회귀합산을전체일반/T3/변이/최종review로세지않는다.'}],
        'checks':checks}
    value['narrative'] = (
        'phase 012 lean-smoke의 A1~A4를 완료했다. 시작 소스 2644개는 011 manager의 source-inspected와 전건 같았다. 현 toolchain_root/discover_lean에서 기존 portable Lean 4.32.0, Lake 5.0.0 및 Mathlib v4.32.0을 찾았고, 설치된 의존 저장소 9개의 HEAD가 manifest revision과 같음을 확인했다. real_ports를 전달해 inspect_toolchain, 대표 Mathlib 컴파일과 실제 verifier의 정상·타입 오류를 실행했다. 설치 입력과 신뢰 기록의 바이트, 판단 파일 11094개의 메타데이터는 전후 같았다. 설치·다운로드나 신뢰 기록의 채택·재기록은 수행하지 않았다.\n\n'
        '최종 정본 T5는 1passed/79.4초, 미러는 1passed/84.4초였다. 각각 20개 판정과 실제 Job 5개의 종료·정리를 확인했다. 소스에 명시한 ℕ 표기와 증명의 수학적 내용에서 정확 서명과 빈 공리 집합을 정했고, 서명 해시·전체 의존 증거 32개·원 컴파일 입력을 검사했다. 같은 선언에 True.intro를 잘못 적용한 입력은 exit 1, failed, lean rejected와 타입 진단을 반환했다. worker·compiler·Job·clock·parser·검증기를 대체하지 않았다.\n\n'
        '초기 live-01/02는 새 도우미가 Job 상태의 정수 타입과 Calls factory를 잘못 읽어 각각 error 1이었다. 실패 원보고와 원자료를 보존했고 성공으로 소급하지 않는다. live-02의 대표 컴파일 308.275825초와 최종 21.170028초는 서로 다른 파일 캐시 조건에서의 실측이다. 시간에 따른 중단이나 단언 약화는 없으며, 이 차이를 코드 최적화의 증거로 주장하지 않는다.\n\n'
        '최종 정상 원출력 71704바이트, source 120바이트, compiled input 6597바이트와 빈 stderr를 자르거나 재작성하지 않고 corpus에 복사했다. provenance는 판본·실명령·시각·Job/PID·전체 추출 범위와 원출력 SHA를 결속한다. 제품 결과의 축약 stdout과 원out을 구별한다. 대표·오류 입력과 설치 fingerprint는 실행 evidence에 남기고 출하 corpus에는 작은 정상 녹화만 추가했다. reader는 새 full 녹화의 서명 해시·의존 증거를 재생하며, 기존 두 Lean 항목의 preview 경로와 기존 18개 entry/verdict·비manifest 100경로는 유지한다. 최종 corpus는 양쪽 각각 19항목·56파일·320687바이트이고, 총 112경로의 Git raw/clean·명시 SHA·미러 바이트와 5MiB 상한을 확인했다.\n\n'
        '관련 회귀는 정본과 미러 각각 48건이 전부 passed·exit 0이었다. corpus 3모듈, 지정 setup/verifier boundary와 smell/invariants/ports 구조 검사, Git 정체성·identity 8사례를 포함한다. 선택과 고유 row, 각 869개 Python 소스 해시와 실행 전후 소스를 대조했다. 사전 생성 계획 11경로는 모두 writes 안이었고, 공식 생성 뒤 미러의 실제 Lean 경로를 검사했다. 실행 뒤 비용 캐시 한 파일만 공식 재동기화했으며 --check 1314파일과 skill-only 검사가 통과했다. 최종 소스 2658개의 정확한 22변경은 모두 배정 범위 안이다.\n\n'
        'B38/8afa57c7의 formal/setup Git 포트 slice는 실제 diff·현재 소비자·원보고 selector를 대조해 유지했다. 원보고 10개가 현재 없어 과거 counts를 새 성공에 합산하지 않고 PR02 전체도 종료하지 않는다. runtime 124파일, 공급자 입력 3파일, host 입력·8원자료와 도구 조건, 기존 corpus를 보존해 011에서 승인한 실호출의 한정된 성질을 재사용한다. 새 유료 호출·host T5·예약·학술 호출은 없다. Git stage/commit/reset/checkout/push, graphify 갱신, 기존 연구 시작·재개·삭제는 수행하지 않았다. 전체 일반 검사·fresh T3·전체 함수 변이·나머지 G7/읽기 조건·최종 review와 관리 마감은 후속 manager의 책임이다.'
    )
    save(E.parent / 'report.json',value)
    print('report complete',len(changes),'changes',len(checks),'checks')

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'snapshot': snapshot(sys.argv[2])
    elif action == 'inputs': read_inputs()
    elif action == 'history': history()
    elif action == 'summary': summary(sys.argv[2])
    elif action == 'corpus': corpus_audit(sys.argv[2])
    elif action == 'promote': promote()
    elif action == 'mirror-plan': mirror_plan(sys.argv[2])
    elif action == 'smoke-observation': smoke_observation(sys.argv[2])
    elif action == 'versions': versions()
    elif action == 'verification': verification()
    elif action == 'report': report()
    elif action == 'run': raise SystemExit(command(sys.argv[2], sys.argv[3:]))
