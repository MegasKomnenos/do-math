"""Observe the existing TestCase during normal unittest lifecycle, before its cleanups."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest

E = Path(__file__).resolve().parent
SCRIPTS = Path('C:/math/.claude/skills/do-math/scripts')
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
module = importlib.import_module('boundary.test_shared_input_provenance')
observations = []
original_run = subprocess.run

def recorded_run(*args, **kwargs):
    argv = args[0] if args else kwargs['args']
    receipt = {'argv': list(map(str, argv)), 'cwd': str(kwargs.get('cwd', os.getcwd())),
               'baseline_environment': os.environ.get('SHARED_INPUT_BASELINE_SCRIPTS'),
               'started_ns': time.time_ns()}
    try:
        completed = original_run(*args, **kwargs)
        receipt.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        return completed
    finally:
        receipt['ended_ns'] = time.time_ns()
        observations.append(receipt)

subprocess.run = recorded_run
methods = [name.rsplit('.', 1)[-1] for name in (
    'test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences',
    'test_exact_baseline_two_worker_raw_union')]
saved = []

def preserve_cleanup(case, original):
    def cleanup(self):
        # All fixtures belong to this fresh process's task-owned TEMP/TMP.
        roots = sorted(Path(tempfile.gettempdir()).glob('tmp*'))
        for root in roots:
            if not root.is_dir(): continue
            destination = E / 'companion-raw' / methods[methods.index(self._testMethodName)] / root.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(root, destination)
            files = [{'path': p.relative_to(destination).as_posix(), 'bytes': p.stat().st_size,
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                     for p in sorted(destination.rglob('*')) if p.is_file()]
            saved.append({'test': self.id(), 'original_root': str(root), 'preserved_root': str(destination), 'files': files})
        return original()
    return types.MethodType(cleanup, case)

cases = []
for name in methods:
    case = module.SharedInputProvenanceTests(name)
    case.doCleanups = preserve_cleanup(case, case.doCleanups)
    cases.append(case)
result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(cases))
subprocess.run = original_run
def serialize(data):
    return json.dumps(data, ensure_ascii=False, indent=2, default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x))
(E / 'companion-invocations.json').write_text(serialize(observations), encoding='utf-8')
(E / 'companion-manifest.json').write_text(serialize(saved), encoding='utf-8')
(E / 'companion-result.json').write_text(serialize({'tests_run': result.testsRun, 'successful': result.wasSuccessful(),
    'failures': [(t.id(), detail) for t, detail in result.failures], 'errors': [(t.id(), detail) for t, detail in result.errors],
    'skipped': [(t.id(), detail) for t, detail in result.skipped], 'fixtures': len(saved),
    'module_sha256': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
    'worker_sha256': hashlib.sha256(module.WORKER.encode()).hexdigest(), 'snapshot_sha256': hashlib.sha256(module.SNAPSHOT.encode()).hexdigest(),
    'baseline_environment': os.environ.get('SHARED_INPUT_BASELINE_SCRIPTS'), 'pid': os.getpid()}), encoding='utf-8')
sys.exit(0 if result.wasSuccessful() else 1)
