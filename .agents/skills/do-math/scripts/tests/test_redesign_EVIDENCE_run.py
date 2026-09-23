"""Run EVIDENCE in a frozen repository and preserve actual per-test evidence.

This is a local test runner, not a provider runner. It neither modifies the
trace's execution states nor treats a structural check as a feature pass.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest

from test_redesign_EVIDENCE import ROOT


def manifest():
    files = []
    for relative in ('.agents/skills/do-math', 'docs/do-math'):
        files.extend(p for p in (ROOT / relative).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = {}

    def coordinate(self, test):
        parts = test.id().split('.')
        return '.agents/skills/do-math/scripts/tests/' + parts[0] + '.py::' + '.'.join(parts[1:])

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.setdefault(self.coordinate(test), 'passed')

    def addFailure(self, test, err):
        super().addFailure(test, err); self.outcomes[self.coordinate(test)] = 'failed'

    def addError(self, test, err):
        super().addError(test, err); self.outcomes[self.coordinate(test)] = 'failed'

    def addSkip(self, test, reason):
        super().addSkip(test, reason); self.outcomes[self.coordinate(test)] = 'skipped'

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None: self.outcomes[self.coordinate(test)] = 'failed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ('run.log', 'report.json')):
        raise ValueError('use a new run directory; never overwrite previous evidence')
    before = manifest()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), 'test_redesign_EVIDENCE*.py')
    with (output / 'run.log').open('w', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    after = manifest()
    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    report = {'command': [sys.executable, *sys.argv], 'repository': str(ROOT), 'python': sys.version,
        'tests_run': result.testsRun, 'tests': result.outcomes, 'file_sha256': before,
        'edition_stable': not changed, 'changed_during_run': changed,
        'successful': result.wasSuccessful() and not changed,
        'failures': [{'test': t.id(), 'traceback': reason} for t, reason in [*result.errors, *result.failures]],
        'log_sha256': hashlib.sha256((output / 'run.log').read_bytes()).hexdigest(),
        'boundaries': ['No model, provider or Lean invocation', 'Real Python domain transitions',
            'Disposable local Git and Windows child processes only',
            'Compiler/model verdicts, capability observations and input snapshot transport are fixtures',
            'Synthetic changed PID is not natural OS PID reuse; no research efficacy evaluation']}
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('tests_run', 'edition_stable', 'successful', 'changed_during_run')}))
    print(str(output / 'report.json'))
    return 0 if report['successful'] else 1


if __name__ == '__main__': raise SystemExit(main())
