"""Read-only manager verification of phase 009 and its exact predecessor evidence."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
EV = RUN / 'phases/009/tasks/document-callable/evidence'
OLD = RUN / 'phases/008/tasks/document-recovery/evidence'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout
def changed(a, b):
    return sorted(p for p in a.keys() | b.keys() if a.get(p) != b.get(p))

check = subprocess.run([sys.executable, '-B', str(ROOT/'services/continuous-development/check.py'),
                       'report', str(ROOT), str(RUN), '009', 'document-callable'],
                       cwd=ROOT, capture_output=True)
write('report-check.json', {'argv': check.args, 'exit_code': check.returncode,
      'stdout': check.stdout.decode(), 'stderr': check.stderr.decode()})
assert check.returncode == 0
initial, final = read(EV/'source-start.json'), read(EV/'source-final.json')
paths = set()
for rel in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
    paths.update(p for p in (ROOT/rel).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
paths.add(ROOT/'.gitattributes')
current = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}
assert current == final
assert initial == read(OLD/'source-final.json')
report = read(EV.parent/'report.json')
assignment = read(RUN/'phases/009/phase.json')['tasks'][0]
changes = changed(initial, final)
assert set(changes) == set(assignment['writes']) == {r['path'] for r in report['changes']}
checks = {}
for label, old_label, tree, count in [('canonical-final', 'canonical-joined-final', '.claude', 110),
                                     ('mirror-final', 'mirror-final', '.agents', 89)]:
    path = EV/label
    result, command = read(path/'results/report.json'), read(path/'command.json')
    old = read(OLD/old_label/'results/report.json')
    rows = [r for g in result['reports'] for r in g['rows']]
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)) == len(result['selected']) == count
    assert set(ids) == set(result['selected']) == set(old['selected'])
    assert collections.Counter(r['outcome'] for r in rows) == result['counts'] == {'passed': count}
    assert result['complete'] and result['successful'] and not result['changed_during_run']
    assert command['exit_code'] == 0 and command['state'] == 'exited'
    assert command['ended_at'] > command['started_at']
    before, after = read(path/'source-before.json'), read(path/'source-after.json')
    assert changed(before, after) == command['changed_sources'] == [tree+'/skills/do-math/scripts/tests/.timings.json']
    assert len(result['source_sha256']) == 865
    assert all(before[tree+'/skills/do-math/scripts/'+p] == h == after[tree+'/skills/do-math/scripts/'+p]
               == current[tree+'/skills/do-math/scripts/'+p] for p, h in result['source_sha256'].items())
    doc = tree+'/skills/do-math/references/CLI-실행-계약.md'
    assert before[doc] == after[doc] == current[doc]
    old_failures = sorted(r['id'] for g in old['reports'] for r in g['rows'] if r['outcome'] == 'failed')
    assert len(old_failures) == 4 and set(old_failures) <= set(ids)
    checks[label] = {'selected': count, 'unique_rows': len(set(ids)), 'counts': result['counts'],
                    'exit_code': command['exit_code'], 'complete': result['complete'],
                    'python_source_count': 865, 'prior_failures_now_passed': old_failures,
                    'report_sha256': sha(path/'results/report.json'), 'command_sha256': sha(path/'command.json')}
assert checks['canonical-final']['prior_failures_now_passed'] == checks['mirror-final']['prior_failures_now_passed']
commands = {}
for p in sorted(EV.glob('*/command.json')):
    record = read(p)
    assert record['state'] == 'exited'
    commands[p.parent.name] = {'exit_code': record['exit_code'], 'sha256': sha(p),
                             'changed_sources': record['changed_sources']}
    assert (p.parent/'stdout.txt').is_file() and (p.parent/'stderr.txt').is_file()
assert commands['plan-build']['exit_code'] == 1 and commands['plan-build']['changed_sources'] == []
assert all(v['exit_code'] == 0 for k, v in commands.items() if k != 'plan-build')
gates = {}
for label in ('mirror-check', 'skill-only'):
    assert read(EV/label/'source-before.json') == read(EV/label/'source-after.json') == current
    gates[label] = (EV/label/'stdout.txt').read_text(encoding='utf-8')
old_bytes = (EV/'cli-before.txt').read_bytes()
new_bytes = (ROOT/'.claude/skills/do-math/references/CLI-실행-계약.md').read_bytes()
assert new_bytes.replace(b'`provider_final.output_contract(...)`', b'`provider_final.output_contract`') == old_bytes
assert len(new_bytes) - len(old_bytes) == 5
runtime = read(RUN/'phases/007/manager-evidence/verification.json')['runtime_unchanged_since_live']
smoke = read(RUN/'phases/008/manager-evidence/verification.json')['smoke_inputs_unchanged']
assert len(runtime) == 124 and len(smoke) == 3
assert all(initial[p] == current[p] for p in list(runtime)+list(smoke))
corpus = read(OLD/'corpus-final.json')
corpus_count = 0
for record in corpus['trees'].values():
    for item in record['files'].values():
        assert current[item['path']] == initial[item['path']] == item['sha256']
        assert (ROOT/item['path']).stat().st_size == item['bytes']
        corpus_count += 1
    assert (record['entry_count'], record['file_count'], record['bytes'], len(record['bindings'])) == (18, 51, 223685, 50)
assert corpus_count == 102
sys.path.insert(0, str(ROOT/'.claude/skills/do-math/scripts'))
sys.path.insert(0, str(ROOT/'.claude/skills/do-math/scripts/tests'))
from support import doc_code
from do_math import provider_final
doc = new_bytes.decode('utf-8')
assert callable(provider_final.output_contract)
assert doc_code.function_reference_issues(doc) == []
assert doc_code.unowned_field_references(doc, doc_code.field_schemas()) == []
assert doc_code.function_reference_issues('`governance.missing_function(...)`')
assert doc_code.function_reference_issues('`planning.RECORD_FAMILIES(...)`')
product = sorted({r['path'] for r in read(OLD.parent/'report.json')['changes']} | set(changes))
product = [p for p in product if not p.endswith('/.timings.json')]
assert len(product) == 28
dirty_product = git('diff', '--name-only', '-z', '--', '.claude/skills/do-math', '.agents/skills/do-math').decode('utf-8').split('\0')
assert set(filter(None, dirty_product)) == set(product)
write('verification.json', {'head': git('rev-parse', 'HEAD').decode().strip(), 'source_count': len(current),
      'current_mismatches': [], 'changes': changes, 'suites': checks, 'commands': commands,
      'gates': gates, 'runtime_unchanged': runtime, 'smoke_inputs_unchanged': smoke,
      'corpus_byte_paths_preserved': corpus_count, 'callable_issues': [], 'unowned_fields': [],
      'notation_only_added_bytes': 5, 'product_commit_paths': product,
      'git_clean_reuse': 'All corpus, attribute and generator bytes equal phase008; reuse its exact-path raw/clean checks.'})
write('source-inspected.json', current)
print(json.dumps({'sources': len(current), 'changes': len(changes), 'suites': {k:v['counts'] for k,v in checks.items()},
                  'product_commit_paths': len(product)}, ensure_ascii=False))
