import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from task_tools import HERE, REPO, RUN, write

SCRIPTS = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from do_math import trust_inventory as records
from do_math.windows_job import WindowsJob
from support.knowledge_roundtrip import installed_request
from support.trust_inputs import trust_fixture

root = HERE / 'fixture-audit'
root.mkdir()
old = json.loads((RUN / 'phases/015/tasks/t4-adapter-report/evidence/fixture-reproduction.json').read_bytes())
identity = old['identity']
before = records.observe_fingerprint(identity)
request = installed_request(root / 'installed-record', identity)
record = records.read_record(Path(request['toolchain_record']['path']))
baseline = record['baselines'][0]
assert records.record_errors(record) == []
assert request['toolchain'] == identity
assert request['binding'] == records.binding(record)
assert before == baseline['fingerprint'] == records.observe_fingerprint(identity)
assert set(before['files']) == set(baseline['content']['files'])
samples = sorted(before['files'])[:2] + sorted(before['files'])[-2:]
samples += [next(p for p in before['files'] if p.startswith(name + '/') and p.endswith('.dll'))
            for name in records.roots(identity) if any(p.startswith(name + '/') and p.endswith('.dll') for p in before['files'])]
observed = {}
for relative in samples:
    name, _, rest = relative.partition('/')
    path = records.roots(identity)[name] / rest
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == baseline['content']['files'][relative]
    observed[relative] = actual

synthetic = trust_fixture(root / 'synthetic', ['synthetic-lean'])
synthetic_request = installed_request(root / 'synthetic-adoption', synthetic['toolchain'])
synthetic_record = records.read_record(Path(synthetic_request['toolchain_record']['path']))
sb = synthetic_record['baselines'][0]
assert sb['content'] == records.content_hashes(synthetic['toolchain'], sb['fingerprint']['files'])
write('fixture-audit.json', {'identity_source':str(RUN / 'phases/015/tasks/t4-adapter-report/evidence/fixture-reproduction.json'),
    'record_path':request['toolchain_record']['path'],'record_sha256':hashlib.sha256(Path(request['toolchain_record']['path']).read_bytes()).hexdigest(),
    'judgment_files':len(before['files']), 'fingerprint_unchanged':True, 'record_errors':[],
    'content_sha256':baseline['content']['sha256'], 'raw_content_samples':observed,
    'synthetic_judgment_files':len(sb['content']['files']), 'synthetic_all_hashes_match':True,
    'validation_is_synthetic':True, 'installation_record_adoption':False})

tree = ast.parse((SCRIPTS / 'tests/boundary/test_scheduling_background_processes.py').read_text(encoding='utf-8'))
source = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='DESCENDANTS_PROBE' for t in n.targets))
osroot = root / 'repaired-os'
osroot.mkdir()
probe = osroot / 'probe.py'
probe.write_text(source,encoding='utf-8')
argv = [str(Path(sys.executable).with_name('pythonw.exe')), '-B', str(probe), str(SCRIPTS), str(osroot)]
with WindowsJob(argv,cwd=osroot) as child:
    pid=child.pid
    child.resume()
    child.wait()
    code=child.poll()
assert code == 0, code
positive, negative = json.loads((osroot / 'actual.json').read_bytes())
assert any(positive['consoles']) and not any(negative['consoles'])
assert negative['visible'] == [] and all(x['stdin_unchanged'] for x in (positive,negative))
write('repaired-os-observation.json', {'argv':argv,'pid':pid,'exit_code':code,
    'positive':positive,'negative':negative,'binary_readback':True,
    'scope':'actual pythonw created in WindowsJob; real Git and descendants; separate console observer'})
print(json.dumps({'judgment_files':len(before['files']),'synthetic_files':len(sb['content']['files']),
                  'os_exit':code,'positive':positive,'negative':negative}))
