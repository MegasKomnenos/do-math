"""Record observed results and exact tested editions; never infer a pass from a partial log."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(r'C:\math')
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
SKILL = ROOT / '.claude/skills/do-math'
SESSION = ROOT / '.codex/writing-flow/01a0a911-23c1-7c52-965a-f3b56d8bfc0d'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def relative(path):
    return path.relative_to(AUDIT).as_posix()

def result(name):
    path = HERE / name
    raw = path.read_bytes()
    text = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig').replace('\r\n', '\n')
    match = re.search(r'^Ran (\d+) tests? in ([\d.]+)s$', text, re.M)
    assert match, f'No complete test summary: {name}'
    verdict = re.search(r'^(OK(?: \([^\n]*\))?|FAILED[^\n]*)$', text, re.M)
    assert verdict and verdict[0].startswith('OK'), f'Test failure: {name}'
    skipped = re.search(r'skipped=(\d+)', verdict[0])
    count, skip = int(match[1]), int(skipped[1]) if skipped else 0
    return {'log': relative(path), 'sha256': digest(path), 'tests': count,
            'passed': count - skip, 'skipped': skip, 'seconds': float(match[2]), 'verdict': verdict[0]}

full = result('full-v2.log')
reading = json.loads((HERE / 'reading-manifest.json').read_bytes())
assert len(reading['files']) == 102
assert all(row['lines'] == row['read_to'] for row in reading['files'])
assert sum(row['lines'] for row in reading['files']) == 20830
frozen = json.loads((HERE / 'full-v2-manifest.json').read_bytes())
changed = [row['path'] for row in frozen if digest(SKILL / row['path']) != row['sha256']]
assert set(changed) == {'GLOSSARY.md', 'references/CLI-실행-계약.md', '계약/독립-운영.md'}, changed
assert all(not path.startswith('scripts/') for path in changed)

reader_dir = HERE / 'reader-evidence'
reader_dir.mkdir(exist_ok=True)
jobs = []
for label, job_id in [('skill', '0c2f1a93c67c4a68ba160d668ec9d5f5'),
                      ('report-memory', '08d7bb879a3248b691afe927483ae138')]:
    job = SESSION / 'jobs' / job_id
    state = json.loads((job / 'state.json').read_bytes())
    assert state['decision']['verdict'] == 'accept'
    report = Path(state['reading']['report_path'])
    assert json.loads(report.read_bytes())['status'] == 'complete'
    draft = Path(state['paths']['draft'])
    assert digest(draft) == state['reading']['input_hashes']['draft']
    destination = reader_dir / (label + '-final.json')
    shutil.copyfile(report, destination)
    decision = reader_dir / (label + '-decision.json')
    shutil.copyfile(Path(state['decision']['path']), decision)
    jobs.append({'label': label, 'whole': state['reading']['scope'] == 'whole',
                 'draft': relative(draft), 'draft_sha256': digest(draft),
                 'report': relative(destination), 'report_sha256': digest(destination),
                 'decision': relative(decision), 'decision_sha256': digest(decision),
                 'reader_session': state['reading']['reader_session']})

smoke = json.loads((HERE / 'real-producer-smoke-result.json').read_bytes())
checks = smoke['checker_observations']
assert any(row['exit_code'] == 1 and not row['passed'] for row in checks)
assert checks[-1]['exit_code'] == 0 and checks[-1]['passed']
assert smoke['outcome'] == 'output_accepted' and smoke['checked_value_equals_received']
assert [(r['path'], r['sha256']) for r in checks[-1]['files']] == [(r['path'], r['sha256']) for r in smoke['output_files']]
actual = HERE / 'real-producer-smoke/work/runs' / smoke['execution_id'] / 'evidence'
raw_dir = HERE / 'real-call-evidence'
raw_dir.mkdir(exist_ok=True)
for name in ('input.txt', 'output.schema.json', 'stdout.jsonl', 'stderr.txt', 'final.txt', 'worker-status.json'):
    shutil.copyfile(actual / name, raw_dir / name)

manifest = [{'path': p.relative_to(SKILL).as_posix(), 'sha256': digest(p), 'bytes': p.stat().st_size}
            for p in sorted(SKILL.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
(HERE / 'final-source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
data = {
    'status': 'verified_with_stated_scope',
    'source_root': '.claude/skills/do-math', 'generated_root': '.agents/skills/do-math',
    'read_before_audit': {'files': 102, 'lines': 20830, 'manifest': 'repair/reading-manifest.json'},
    'baseline': result('baseline-frozen.log'), 'full_regression': full,
    'focused_runs': [result(n) for n in ('boundaries-v1.log', 'integration-v2.log', 'boundaries-v3.log',
                                        'packed-tools.log', 'latest-focused.log', 'final-installation.log')],
    'interrupted_not_counted': ['repair/baseline.log', 'repair/full-v1.log'],
    'diagnostic_rerun': result('formal-test-diagnostic.log'),
    'test_edition': {'manifest': 'repair/full-v2-manifest.json', 'post_freeze_changes': changed,
                     'difference': 'Three prose clarifications only; final code and tests equal the full-regression edition. Final docs separately read and copied installation checked.'},
    'final_source_manifest': 'repair/final-source-manifest.json',
    'regressions_before_repairs': [{'log': relative(p), 'sha256': digest(p)} for p in sorted(HERE.glob('*-red.log'))],
    'real_producer': {'result': 'repair/real-producer-smoke-result.json', 'result_sha256': digest(HERE / 'real-producer-smoke-result.json'),
        'instance_id': smoke['instance_id'], 'execution_id': smoke['execution_id'], 'model': smoke['model'],
        'outcome': smoke['outcome'], 'checks': [{'exit_code': r['exit_code'], 'passed': r['passed']} for r in checks],
        'final_json_equal': True, 'final_file_hashes_equal': True,
        'recoverable_patch_error': {'tool': 'apply_patch', 'count': 1,
            'reason': 'multiple_operations_same_path', 'execution_continued': True},
        'raw_evidence': [{'path': relative(p), 'sha256': digest(p)} for p in sorted(raw_dir.iterdir())]},
    'reading_jobs': jobs,
    'extension_schema_matrix': {'path': 'repair/extension-schema-matrix.json',
        'variants': len(json.loads((HERE / 'extension-schema-matrix.json').read_text(encoding='utf-8-sig'))),
        'scope': 'JSON Schema validity and emitted role families; behavior covered by regression tests'},
    'mirror': {'log': 'repair/mirror-check.log', 'passed': '드리프트 없음' in (HERE / 'mirror-check.log').read_text(encoding='utf-8-sig')},
    'limits': ['The suite uses scripted model responses for orchestration; real Git, threads and SQLite are exercised.',
               'Actual Lean and Windows tests are separate from model mathematical judgment.',
               'The real Codex producer call covers one bounded maintenance assignment, not all-role reliability.',
               'No live research instance, scheduled research run, user goal or budget was changed.',
               'Windows symlink privilege skip is retained; full logs identify the skipped case.',
               'Document reading checks comprehension, not an independent code rebuttal or long-term research quality.']
}
assert data['mirror']['passed']
(AUDIT / '수리-검증.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'full': full, 'final_files': len(manifest), 'reading_jobs': len(jobs)}, ensure_ascii=False))
