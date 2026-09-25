"""Sequential grouped unittest runner with owned, bounded Lean/resource workers.

Normal unittest discovery is still supported but does not impose these outer
process deadlines. This runner never changes the product's Lean time limits.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stderr, redirect_stdout
import fnmatch
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
import uuid

from test_categories import GROUPS, group_for
from do_math.file_io import write_bytes_atomic, read_bytes_shared

SCRIPTS = Path(__file__).resolve().parent
TESTS = SCRIPTS / 'tests'


def _write_json(path, value):
    write_bytes_atomic(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))


def _read_json(path):
    try:
        return json.loads(read_bytes_shared(path).decode('utf-8'))
    except FileNotFoundError:
        return None


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, directory, checkpoint=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory, self.checkpoint = directory, checkpoint
        self.rows, self.starts, self.sequence = {}, {}, 0

    def _progress(self, identifier, phase):
        if self.checkpoint:
            self.sequence += 1
            self.preserve(complete=False)
            # Immutable publications avoid replacing a file the Windows parent
            # may currently have open for reading.
            _write_json(self.directory / f'progress-{self.sequence:06}.json', {
                'sequence': self.sequence, 'test_id': identifier, 'phase': phase})

    def startTest(self, test):
        super().startTest(test)
        self.starts[test.id()] = time.monotonic()
        self.rows[test.id()] = {'id': test.id(), 'outcome': 'running', 'seconds': 0, 'details': []}
        self._progress(test.id(), 'test')

    def _outcome(self, test, outcome, detail=None):
        row = self.rows.setdefault(test.id(), {'id': test.id(), 'outcome': outcome,
                                               'seconds': 0, 'details': [], 'fixture': True})
        row['outcome'] = outcome
        if detail:
            row['details'].append(detail)
        if outcome in {'failed', 'error', 'unexpected_success'}:
            # Publish this failure before the next possibly long test begins.
            # It is diagnostic evidence, not a completed group result.
            path = self.directory / 'failures' / (hashlib.sha256(test.id().encode()).hexdigest() + '.json')
            _write_json(path, {'complete': False, 'event': 'test_failure', 'test': row})
            self.stream.writeln('  failure evidence: ' + str(path))
            self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        self._outcome(test, 'passed')

    def addError(self, test, error):
        super().addError(test, error)
        self._outcome(test, 'error', self._exc_info_to_string(error, test))

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self._outcome(test, 'failed', self._exc_info_to_string(error, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        parent = getattr(test, 'test_case', None)
        if parent is not None:
            row = self.rows[parent.id()]
            row.setdefault('skipped_subtests', []).append({'id': test.id(), 'reason': reason})
            if row['outcome'] == 'running':
                row['outcome'] = 'skipped'
            return
        self._outcome(test, 'skipped', reason)

    def addExpectedFailure(self, test, error):
        super().addExpectedFailure(test, error)
        self._outcome(test, 'expected_failure', self._exc_info_to_string(error, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._outcome(test, 'unexpected_success')

    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        if error is not None:
            outcome = 'failed' if issubclass(error[0], test.failureException) else 'error'
            self._outcome(test, outcome, str(subtest) + '\n' + self._exc_info_to_string(error, test))

    def stopTest(self, test):
        self.rows[test.id()]['seconds'] = time.monotonic() - self.starts.pop(test.id())
        super().stopTest(test)
        self._progress(None, 'fixture_or_shutdown')

    def preserve(self, *, complete):
        report = {'complete': complete, 'successful': complete and self.wasSuccessful(),
                  'tests_run': self.testsRun, 'rows': list(self.rows.values())}
        _write_json(self.directory / 'result.json', report)
        return report


def _run_suite(tests, directory, *, checkpoint=False):
    directory.mkdir(parents=True, exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2, resultclass=lambda *a, **k: TimedResult(
        *a, directory=directory, checkpoint=checkpoint, **k)).run(unittest.TestSuite(tests))
    report = result.preserve(complete=True)
    reported = {row['id'] for row in report['rows']}
    fixtures = [row for row in report['rows'] if row.get('fixture')]
    for test in tests:
        if test.id() in reported:
            continue
        scopes = {f'setUpClass ({type(test).__module__}.{type(test).__qualname__})',
                  f'setUpModule ({type(test).__module__})'}
        skipped = next((row for row in fixtures if row['id'] in scopes and row['outcome'] == 'skipped'), None)
        report['rows'].append({'id': test.id(), 'outcome': 'skipped' if skipped else 'not_run', 'seconds': 0,
            'details': skipped['details'] if skipped else ['A fixture failed before this test could run.']})
    report['successful'] = report['successful'] and all(row['outcome'] in {
        'passed', 'skipped', 'expected_failure'} for row in report['rows'])
    _write_json(directory / 'result.json', report)
    return report


def _empty(job):
    state = job.inspect()
    return state.root_signaled and not state.active_processes and not state.process_ids


def _exit_code(job):
    import ctypes
    from ctypes import wintypes
    function = ctypes.WinDLL('kernel32', use_last_error=True).GetExitCodeProcess
    function.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    function.restype = wintypes.BOOL
    code = wintypes.DWORD()
    if not function(job.process_handle, ctypes.byref(code)):
        raise ctypes.WinError(ctypes.get_last_error())
    return code.value


def wait_for_worker(job, progress_path, timeout, *, clock=None, pause=None):
    """Each test and the surrounding fixture/shutdown phase has its own limit."""
    clock, pause = clock or time.monotonic, pause or time.sleep
    phase_started = clock()
    deadline, sequence, progress = phase_started + timeout, None, {'phase': 'startup_or_fixture', 'test_id': None}
    while True:
        published = sorted(progress_path.parent.glob(progress_path.stem + '-*.json'))
        observed = _read_json(published[-1] if published else progress_path)
        if observed and observed.get('sequence') != sequence:
            sequence, progress = observed['sequence'], observed
            phase_started = clock()
            deadline = phase_started + timeout
        if job.wait(0) and _empty(job):
            return None
        if clock() >= deadline:
            elapsed = clock() - phase_started
            job.terminate()
            end = clock() + 10
            while not _empty(job) and clock() < end:
                pause(.02)
            return {**progress, 'timeout_seconds': timeout, 'observed_seconds': elapsed,
                    'termination_confirmed': _empty(job)}
        pause(.05)


def _isolated(tests, directory, timeout):
    from do_math.windows_job import WindowsJob
    directory.mkdir(parents=True)
    identifiers = [test.id() for test in tests]
    _write_json(directory / 'requested.json', identifiers)
    scratch = directory / 'scratch'
    scratch.mkdir()
    environment = {**os.environ, 'TMP': str(scratch), 'TEMP': str(scratch), 'TMPDIR': str(scratch)}
    started = time.monotonic()
    try:
        with WindowsJob([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(directory)],
                        cwd=directory, env=environment, name='do-math-tests-' + uuid.uuid4().hex) as job:
            job.resume()
            timeout_record = wait_for_worker(job, directory / 'progress.json', timeout)
            returncode = _exit_code(job)
        report = _read_json(directory / 'result.json') or {'complete': False, 'successful': False, 'rows': []}
        report['returncode'] = returncode
        report['successful'] = report['successful'] and returncode == 0
    except Exception as error:
        report = _read_json(directory / 'result.json') or {'rows': []}
        report.update(complete=False, successful=False, worker_error=f'{type(error).__name__}: {error}')
        timeout_record = None
    report.update(worker_seconds=time.monotonic() - started, directory=str(directory), requested=identifiers)
    if timeout_record is not None:
        report.update(complete=False, successful=False, timeout=timeout_record)
    # A class-level skip is different from unfinished tests after a worker error.
    fixtures = [row for row in report['rows'] if row.get('fixture')]
    skipped_fixture = next((row for row in fixtures if row['outcome'] == 'skipped'), None)
    completed = {row['id'] for row in report['rows'] if row['outcome'] != 'running'}
    report['rows'] = [row for row in report['rows'] if row['outcome'] != 'running']
    for identifier in identifiers:
        if identifier in completed:
            continue
        timed_out = timeout_record is not None and timeout_record.get('test_id') == identifier
        skipped = report['complete'] and skipped_fixture is not None
        report['rows'].append({'id': identifier, 'outcome': 'timeout' if timed_out else 'skipped' if skipped else 'not_run',
            'seconds': timeout_record['observed_seconds'] if timed_out else 0,
            'details': skipped_fixture['details'] if skipped else [
                'Worker exceeded its limit.' if timed_out else 'Worker did not complete this test; inspect retained logs.']})
    report['successful'] = bool(report['successful'] and all(row['outcome'] in {
        'passed', 'skipped', 'expected_failure'} for row in report['rows']))
    _write_json(directory / 'worker-report.json', report)
    return report


def _worker(directory):
    sys.path.insert(0, str(TESTS))
    with (directory / 'stdout.txt').open('w', encoding='utf-8', buffering=1) as out, \
            (directory / 'stderr.txt').open('w', encoding='utf-8', buffering=1) as err, \
            redirect_stdout(out), redirect_stderr(err):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(_read_json(directory / 'requested.json'))
        report = _run_suite(list(flatten(suite)), directory, checkpoint=True)
    return 0 if report['successful'] else 1


def _edition():
    return {path.relative_to(SCRIPTS).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(SCRIPTS.rglob('*.py')) if '__pycache__' not in path.parts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', action='append', choices=('all', *GROUPS), help='repeat to combine; default: all')
    parser.add_argument('--match', action='append', default=[], help='test-ID glob; repeat for alternatives')
    parser.add_argument('--list', action='store_true', help='discover and list without running tests')
    parser.add_argument('--timeout', type=float, default=300, help='seconds per isolated test/fixture phase (default: 300)')
    parser.add_argument('--output', type=Path, help='new or empty results directory; default: a unique temporary directory')
    parser.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return _worker(args.worker)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    groups = set(args.group or ['all'])
    if 'all' in groups:
        groups = set(GROUPS)
    before = _edition()
    loader = unittest.TestLoader()
    discovered = list(flatten(loader.discover(str(TESTS), pattern='test_*.py')))
    if loader.errors:
        print('\n'.join(loader.errors), file=sys.stderr)
        return 2
    selected = [test for test in discovered if group_for(test) in groups and
                (not args.match or any(fnmatch.fnmatchcase(test.id(), pattern) for pattern in args.match))]
    if not selected:
        print('No tests selected; no pass was established.', file=sys.stderr)
        return 2
    if args.list:
        for test in selected:
            print(group_for(test) + '\t' + test.id())
        return 0
    directory = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='do-math-tests-'))
    if directory.exists() and any(directory.iterdir()):
        parser.error('--output must be new or empty; previous evidence is never overwritten')
    directory.mkdir(parents=True, exist_ok=True)
    reports = []
    for group in GROUPS:
        tests = [test for test in selected if group_for(test) == group]
        if not tests:
            continue
        print(f'[{group}] {len(tests)} tests', flush=True)
        if group in {'lean', 'resource'}:
            classes = defaultdict(list)
            for test in tests:
                classes[type(test)].append(test)
            for index, members in enumerate(classes.values()):
                print('  isolated: ' + members[0].id().rsplit('.', 1)[0], flush=True)
                report = _isolated(members, directory / f'{group}-{index:03}', args.timeout)
                print('  ' + str(dict(Counter(row['outcome'] for row in report['rows'] if not row.get('fixture')))), flush=True)
                reports.append({'group': group, **report})
        else:
            reports.append({'group': group, **_run_suite(tests, directory / group)})
        _write_json(directory / 'report.json', {'complete': False, 'reports': reports})
    after = _edition()
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    rows = [row for report in reports for row in report['rows']]
    result = {'complete': all(report['complete'] for report in reports),
        'successful': not changed and all(report['successful'] for report in reports),
        'selected': [test.id() for test in selected], 'discovered': len(discovered),
        'groups': sorted(groups), 'counts': dict(Counter(row['outcome'] for row in rows if not row.get('fixture'))),
        'fixture_counts': dict(Counter(row['outcome'] for row in rows if row.get('fixture'))),
        'source_sha256': before, 'changed_during_run': changed, 'reports': reports,
        'slowest': sorted((row for row in rows if not row.get('fixture')),
                          key=lambda row: row['seconds'], reverse=True)[:20]}
    _write_json(directory / 'report.json', result)
    print(json.dumps({key: result[key] for key in ('complete', 'successful', 'counts')}, ensure_ascii=False))
    for row in result['slowest']:
        print(f"{row['seconds']:9.3f}s {row['outcome']:18} {row['id']}")
    print('Report: ' + str(directory / 'report.json'))
    return 0 if result['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
