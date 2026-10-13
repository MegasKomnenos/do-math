import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
EVIDENCE = Path(__file__).resolve().parent
PYTHON = Path('C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe')

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def snapshot():
    baseline = read(RUN / 'phases/010/manager-evidence/source-inspected.json')
    return {p: sha(REPO / p) if (REPO / p).is_file() else None for p in baseline}

def compare(before, after):
    return [{'path': p, 'before': before.get(p), 'after': after.get(p)}
            for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]

def start():
    current = snapshot()
    baseline = read(RUN / 'phases/010/manager-evidence/source-inspected.json')
    save(EVIDENCE / 'source-start.json', current)
    save(EVIDENCE / 'start-verification.json', {
        'at_utc': now(), 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'source_count': len(current), 'versus_010_manager': compare(baseline, current),
        'git_status': subprocess.check_output(['git', 'status', '--short'], cwd=REPO, text=True, encoding='utf-8')})
    print('source-start:', len(current), 'changes versus 010 manager:', len(compare(baseline, current)))

def execute(label, args):
    before = snapshot()
    save(EVIDENCE / (label + '-source-before.json'), before)
    command = [str(PYTHON), '-u', '-B', *args]
    record = {'command': command, 'cwd': str(REPO), 'started_utc': now(), 'wrapper_pid': os.getpid()}
    save(EVIDENCE / (label + '-execution.json'), record)
    with (EVIDENCE / (label + '.stdout.log')).open('wb') as out, (EVIDENCE / (label + '.stderr.log')).open('wb') as err:
        process = subprocess.Popen(command, cwd=REPO, stdout=out, stderr=err)
        record['pid'] = process.pid
        save(EVIDENCE / (label + '-execution.json'), record)
        code = process.wait()
    after = snapshot()
    save(EVIDENCE / (label + '-source-after.json'), after)
    record.update(ended_utc=now(), exit_code=code, changes=compare(before, after))
    save(EVIDENCE / (label + '-execution.json'), record)
    print(label, 'exit', code, 'source changes', len(record['changes']))
    print((EVIDENCE / (label + '.stdout.log')).read_text(encoding='utf-8', errors='replace')[-1500:])
    print((EVIDENCE / (label + '.stderr.log')).read_text(encoding='utf-8', errors='replace')[-1500:])
    return code

RELATED = [
    'boundary.test_scheduling_windows_job', 'boundary.test_scheduling_owned_job_children',
    'boundary.test_scheduling_call_jobs', 'boundary.test_role_input_snapshot_reach',
    'boundary.test_port_jobs', 'contracts.test_port_jobs', 'structure.test_test_smells',
    'structure.test_boundary_invariants', 'structure.test_ports',
    'structure.test_doc_code', 'sim.test_knowledge_currentness.RecoveryMaterialTests',
    'sim.test_role_input_context.OperationalInputTests',
    'flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests',
    'unit.test_role_input_packaging', 'unit.test_role_input_scoped_packaging']

def selection():
    code = execute('canonical-selection', ['.claude/skills/do-math/scripts/run_tests.py', *RELATED, '--list'])
    assert code == 0
    lines = (EVIDENCE / 'canonical-selection.stdout.log').read_text(encoding='utf-8').splitlines()
    selected = [line.strip().split()[-1] for line in lines if line.strip().split() and line.strip().split()[-1].startswith(
        ('structure.', 'contracts.', 'unit.', 'sim.', 'flows.', 'boundary.'))]
    old = read(RUN / 'phases/010/tasks/host-smoke/evidence/related-results/report.json')['selected']
    previous = read(RUN / 'phases/009/tasks/document-callable/evidence/canonical-final/results/report.json')['selected']
    added_009 = [p for p in previous if any(p == x or p.startswith(x + '.') for x in RELATED[9:])]
    assert len(selected) == len(set(selected)) and set(old) <= set(selected)
    assert set(selected) == set(old) | set(added_009)
    save(EVIDENCE / 'selection.json', {'selectors': RELATED, 'selected': selected,
        'count': len(selected), 'phase010_count': len(old), 'phase009_related_count': len(added_009),
        'duplicates': [], 'missing_phase010': [], 'missing_phase009_related': []})
    print('selected', len(selected), 'phase010', len(old), '009 related', len(added_009))

def suite(label, mirror=False):
    tree = '.agents' if mirror else '.claude'
    return execute(label, [tree + '/skills/do-math/scripts/run_tests.py', *RELATED,
        '--jobs', '1', '--output', str(EVIDENCE / (label + '-results'))])

def mirror_plan(label):
    spec = importlib.util.spec_from_file_location('build_skill_mirrors',
        REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base = module.iter_files(REPO / module.BASE_REL)
    diff = REPO / '.agents/diff'
    rules = module.load_rules(diff)
    overlays = {rel: p for rel, p in module.iter_files(diff).items() if rel not in module.RESERVED}
    outputs = {rel: module.transform(rel, p.read_bytes(), rules) for rel, p in base.items()}
    outputs.update({rel: p.read_bytes() for rel, p in overlays.items()})
    existing = module.iter_files(REPO / '.agents/skills')
    changes = []
    for rel in sorted(set(outputs) | set(existing)):
        original = existing[rel].read_bytes() if rel in existing else None
        desired = outputs.get(rel)
        if original != desired:
            changes.append({'path': '.agents/skills/' + rel,
                'before': hashlib.sha256(original).hexdigest() if original is not None else None,
                'after': hashlib.sha256(desired).hexdigest() if desired is not None else None})
    writes = read(RUN / 'phases/011/phase.json')['tasks'][0]['writes']
    assert all(row['path'] in writes for row in changes), changes
    manifest = {'overlays': {rel: read(diff / '_manifest.json')['overlays'][rel] for rel in sorted(overlays) if rel in base}}
    assert all(module.sha1(base[rel].read_bytes()) == manifest['overlays'][rel] for rel in overlays if rel in base)
    predicted_manifest = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()
    # write_text translates newline on this Windows host, unlike transform/write_bytes.
    predicted_manifest = predicted_manifest.replace(b'\n', os.linesep.encode())
    assert predicted_manifest == (diff / '_manifest.json').read_bytes()
    save(EVIDENCE / (label + '.json'), {'at_utc': now(), 'changes': changes,
        'manifest_unchanged': True, 'all_changes_within_writes': True, 'output_count': len(outputs)})
    print(label, len(changes), [row['path'] for row in changes])

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'start':
        start()
    elif action == 'execute':
        sys.exit(execute(sys.argv[2], sys.argv[3:]))
    elif action == 'selection':
        selection()
    elif action == 'suite':
        sys.exit(suite(sys.argv[2], mirror='--mirror' in sys.argv[3:]))
    elif action == 'mirror-plan':
        mirror_plan(sys.argv[2])
