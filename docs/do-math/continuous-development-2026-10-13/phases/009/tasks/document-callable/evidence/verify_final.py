"""Compare final source bytes, real runner records, and prior inspected evidence."""
import collections
import hashlib
import json
import subprocess
from run_command import ROOT, EVIDENCE, snapshot, changed, write_json

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OLD = RUN / 'phases/008/tasks/document-recovery/evidence'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evidence_ref(path):
    return 'run:' + path.relative_to(RUN).as_posix()

initial, final = read(EVIDENCE / 'source-start.json'), snapshot()
write_json(EVIDENCE / 'source-final.json', final)
phase = read(RUN / 'phases/009/phase.json')['tasks'][0]
changes = changed(initial, final)
assert set(changes) == set(phase['writes']), changes
start = read(EVIDENCE / 'start-state.json')
head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, check=True).stdout.decode().strip()
assert head == start['head']
prior = read(OLD / 'source-final.json')
assert initial == prior
for ref, record in read(EVIDENCE / 'input-hashes.json').items():
    scope, rel = ref.split(':', 1)
    path = (ROOT if scope == 'repo' else RUN) / rel
    if rel != '.claude/skills/do-math/references/CLI-실행-계약.md':
        assert sha(path) == record['sha256'], ref
runtime = read(RUN / 'phases/007/manager-evidence/verification.json')['runtime_unchanged_since_live']
assert len(runtime) == 124 and all(initial[p] == final[p] for p in runtime)
smoke = read(RUN / 'phases/008/manager-evidence/verification.json')['smoke_inputs_unchanged']
assert len(smoke) == 3 and all(initial[p] == final[p] for p in smoke)
corpus = read(OLD / 'corpus-final.json')
corpus_summary = {}
for tree, record in corpus['trees'].items():
    for item in record['files'].values():
        assert final[item['path']] == initial[item['path']] == item['sha256']
        assert (ROOT / item['path']).stat().st_size == item['bytes']
    assert record['entry_count'] == 18 and record['file_count'] == 51
    assert record['bytes'] == 223685 and len(record['bindings']) == 50
    corpus_summary[tree] = {k: record[k] for k in ('entry_count', 'file_count', 'bytes')}
    corpus_summary[tree]['explicit_sha_bindings'] = len(record['bindings'])
assert sum(v['file_count'] for v in corpus_summary.values()) == 102
suites = {}
failed_before_to_passed_after = {}
for label, old_label, tree, expected in (
        ('canonical-final', 'canonical-joined-final', '.claude', 110),
        ('mirror-final', 'mirror-final', '.agents', 89)):
    path = EVIDENCE / label
    report = read(path / 'results/report.json')
    command = read(path / 'command.json')
    rows = [r for group in report['reports'] for r in group['rows']]
    ids = [r['id'] for r in rows]
    old_report = read(OLD / old_label / 'results/report.json')
    assert len(ids) == len(set(ids)) == len(report['selected']) == expected
    assert set(ids) == set(report['selected']) == set(old_report['selected'])
    assert all(row['outcome'] == 'passed' for row in rows)
    assert dict(collections.Counter(r['outcome'] for r in rows)) == report['counts'] == {'passed': expected}
    assert report['complete'] and report['successful'] and not report['changed_during_run']
    assert command['exit_code'] == 0 and command['state'] == 'exited'
    assert command['ended_at'] > command['started_at']
    before, after = read(path / 'source-before.json'), read(path / 'source-after.json')
    delta = changed(before, after)
    assert delta == command['changed_sources']
    assert delta == [tree + '/skills/do-math/scripts/tests/.timings.json']
    base = tree + '/skills/do-math/scripts/'
    assert len(report['source_sha256']) == 865
    assert all(before[base + p] == h == after[base + p] == final[base + p]
               for p, h in report['source_sha256'].items())
    doc_path = tree + '/skills/do-math/references/CLI-실행-계약.md'
    assert before[doc_path] == after[doc_path] == final[doc_path]
    failures = [r for g in old_report['reports'] for r in g['rows'] if r['outcome'] == 'failed']
    assert len(failures) == 4
    by_id = {row['id']: row for row in rows}
    failed_before_to_passed_after[tree] = [
        {'id': r['id'], 'before': r['outcome'], 'after': by_id[r['id']]['outcome'],
         'prior_report': evidence_ref(OLD / old_label / 'results/report.json'),
         'current_report': evidence_ref(path / 'results/report.json')}
        for r in failures]
    suites[label] = {'selected': expected, 'unique_rows': len(set(ids)), 'counts': report['counts'],
                     'exit_code': command['exit_code'], 'complete': report['complete'],
                     'successful': report['successful'], 'changed_during_run': report['changed_during_run'],
                     'python_source_count': len(report['source_sha256']),
                     'report_sha256': sha(path / 'results/report.json'),
                     'command_sha256': sha(path / 'command.json'),
                     'source_changes': delta}
assert {r['id'] for r in failed_before_to_passed_after['.claude']} == {
    r['id'] for r in failed_before_to_passed_after['.agents']}
for label, plan_label in (('mirror-build', 'mirror-plan'), ('cache-sync', 'cache-plan')):
    command = read(EVIDENCE / label / 'command.json')
    assert command['exit_code'] == 0 and command['state'] == 'exited'
    assert set(command['changed_sources']) == set(read(EVIDENCE / (plan_label + '.json'))['changed'])
gates = {}
for label in ('mirror-check', 'skill-only'):
    command = read(EVIDENCE / label / 'command.json')
    assert command['exit_code'] == 0 and command['state'] == 'exited'
    assert read(EVIDENCE / label / 'source-before.json') == read(EVIDENCE / label / 'source-after.json') == final
    gates[label] = (EVIDENCE / label / 'stdout.txt').read_text(encoding='utf-8')
assert (ROOT / '.claude/skills/do-math/scripts/tests/.timings.json').read_bytes() == (
        ROOT / '.agents/skills/do-math/scripts/tests/.timings.json').read_bytes()
old = (EVIDENCE / 'cli-before.txt').read_bytes()
new = (ROOT / '.claude/skills/do-math/references/CLI-실행-계약.md').read_bytes()
assert new.replace(b'`provider_final.output_contract(...)`', b'`provider_final.output_contract`') == old
result = {'head': head, 'source_count': len(final), 'difference_from_008_at_start': [],
          'changes': changes, 'suites': suites, 'failed_before_to_passed_after': failed_before_to_passed_after,
          'runtime_unchanged': runtime, 'smoke_inputs_unchanged': smoke, 'corpus': corpus_summary,
          'corpus_byte_paths_preserved': 102,
          'prior_git_clean_evidence': 'run:phases/008/manager-evidence/git-clean-observation.json',
          'git_clean_reuse_condition': 'Every corpus path and byte hash remains identical to phase008 inspection; no rules or attributes changed.',
          'gates': gates, 'unchanged_tests_and_runtime': True,
          'callable_probe': read(EVIDENCE / 'callable-probe.json')}
write_json(EVIDENCE / 'verification-final.json', result)
status = subprocess.run(['git', '-c', 'core.quotepath=false', 'status', '--porcelain=v1'],
                        cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
write_json(EVIDENCE / 'end-state.json', {'head': head, 'status': status})
print(json.dumps({'source_count': len(final), 'changes': changes,
                  'suites': {k: v['counts'] for k, v in suites.items()},
                  'runtime_preserved': len(runtime), 'corpus_preserved': 102}, ensure_ascii=False))
