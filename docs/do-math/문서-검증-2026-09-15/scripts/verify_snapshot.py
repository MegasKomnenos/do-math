"""Run tests against an immutable local copy while editorial review continues."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import unittest

root = Path(r'C:\math')
parser = argparse.ArgumentParser()
parser.add_argument('--destination', type=Path, required=True)
parser.add_argument('--module', action='append')
parser.add_argument('--skill-source', type=Path)
parser.add_argument('--repository-support', type=Path, default=root)
parser.add_argument('--lean-bin', type=Path)
args = parser.parse_args()
args.destination.mkdir(parents=True, exist_ok=False)
snapshot = args.destination / 'skill'
skill_source = (args.skill_source or root / '.claude/skills/do-math').resolve()
shutil.copytree(skill_source, snapshot,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
files = {p.relative_to(snapshot).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(snapshot.rglob('*')) if p.is_file()}
(args.destination / 'manifest.json').write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding='utf-8')

repository_support = args.repository_support.resolve()
test_repository = (snapshot / 'scripts/tests/test_preflight.py').resolve().parents[5]
support_rows = []
for relative in (Path('docs/do-math/통합-설계-명세-v9'), Path('docs/do-math/통합-설계.md'),
                 Path('docs/형식과-절차.md')):
    source = repository_support / relative
    sources = sorted(source.rglob('*')) if source.is_dir() else [source]
    for source_file in sources:
        if not source_file.is_file() or '__pycache__' in source_file.parts:
            continue
        item_relative = source_file.relative_to(repository_support)
        target = test_repository / item_relative
        raw = source_file.read_bytes()
        if target.resolve() != source_file.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != raw:
                raise FileExistsError(f'support target contains different bytes: {target}')
            if not target.exists():
                target.write_bytes(raw)
        support_rows.append({'path': item_relative.as_posix(), 'source': str(source_file.resolve()),
                             'materialized_path': str(target.resolve()),
                             'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})

lean_bin = args.lean_bin.resolve() if args.lean_bin else None
if lean_bin:
    if not (lean_bin / 'lean.exe').is_file():
        raise FileNotFoundError(f'lean.exe is absent from --lean-bin: {lean_bin}')
    os.environ['PATH'] = str(lean_bin) + os.pathsep + os.environ.get('PATH', '')
(args.destination / 'support-manifest.json').write_text(json.dumps({
    'skill_source': str(skill_source), 'repository_support': str(repository_support),
    'test_repository': str(test_repository), 'lean_bin': str(lean_bin) if lean_bin else None,
    'files': support_rows}, ensure_ascii=False, indent=2), encoding='utf-8')

test_path = snapshot / 'scripts/tests'
sys.path[:0] = [str(snapshot / 'scripts'), str(test_path)]
loader = unittest.defaultTestLoader
suite = (unittest.TestSuite(loader.loadTestsFromName(name) for name in args.module)
         if args.module else loader.discover(str(test_path)))
with (args.destination / 'tests.txt').open('w', encoding='utf-8') as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
report = {'tests_run': result.testsRun, 'passed': result.wasSuccessful(),
          'failures': [{'test': str(test), 'traceback': trace} for test, trace in result.failures],
          'errors': [{'test': str(test), 'traceback': trace} for test, trace in result.errors],
          'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped]}
(args.destination / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
