"""Sequential group-by-group unittest runner with owned, bounded Lean/resource workers.

Legacy tests (``tests/test_*.py``) run in shards; new-system tests live in the
tier folders under ``tests/`` and are chosen with ``--tier T0``..``T5``
(docs/do-math/시험-재편-2026-09-29/설계.md 5). Tests are selected by ID or
module (positional), by shard, by tier, or, when none is given, every legacy
shard plus the in-process tiers; boundary and smoke tests run only when asked.
Every selected test runs; there is no result cache. Shards and the isolation
labels live in ``test_categories.py`` beside this runner; a legacy test module
missing from ``SHARDS`` stops the run. The report states the number of open
entries in ``tests/known_defects.json``. When and what to run is in
``tests/시험-지침.md``.

T0 adds to the structure checks the tests that ran the changed lines, by the
selection index and its safety rules (``tests/support/selection.py``). T3 runs
the T2 folders under branch coverage with a context per test
(``tests/support/branch_gate.py``; with ``--jobs`` each worker process measures
its modules and the runner combines the data): the branch-reach gate over layer 1-3
modules fails the run when a branch or line is unreached, and a full T3 run
rewrites the selection index ``tests/.selection-index.json``. With
``--mutation-base <commit>`` T3 then mutates the functions changed since that
commit (``tests/support/mutation.py``) and fails while ``tests/pseudo_tested.json``
has an entry without a reason.

Lean and resource tests run per class in an owned Windows Job with a per-phase
deadline. Normal unittest discovery still works but imposes no outer deadlines.
This runner never changes the product's Lean time limits.
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

from test_categories import SHARDS, isolation_for, shard_for, unregistered_modules

SCRIPTS = Path(__file__).resolve().parent
TESTS = SCRIPTS / 'tests'
# New-system tests live in these packages under tests/; the folder is the tier
# group (docs/do-math/시험-재편-2026-09-29/설계.md 5.4). Legacy tests/test_*.py
# modules keep their SHARDS until they are retired.
FOLDERS = ('structure', 'unit', 'sim', 'flows', 'contracts', 'boundary', 'smoke')
TIERS = {
    'T0': ('structure',),
    'T1': ('structure', 'unit', 'contracts'),
    'T2': ('structure', 'unit', 'contracts', 'sim'),
    # flows: Sim scenarios longer than the Sim budget, moved to the rarer tier (설계 6.1, 결정 A26).
    'T3': ('structure', 'unit', 'contracts', 'sim', 'flows'),
    'T4': ('boundary',),
    'T5': ('smoke',),
}
# Folders that run when no --tier/--shard/test ID narrows the selection. Boundary
# and smoke tests need real tools or model calls, so they run only when asked.
DEFAULT_FOLDERS = TIERS['T3']


def folder_of(test):
    """The tier folder a test module lives in, or None for a legacy tests/test_*.py module."""
    head = type(test).__module__.split('.')[0]
    return head if head in FOLDERS else None


def select_tiers(tests, tiers):
    folders = {folder for tier in tiers for folder in TIERS[tier]}
    return [test for test in tests if folder_of(test) in folders]


# A new-system module the timing record does not know yet is estimated at this per test.
UNKNOWN_TEST_SECONDS = 0.5
TIMINGS = TESTS / '.timings.json'


def module_seconds(counts, recorded):
    """Each module's expected seconds: its recorded time, else its test count times ``UNKNOWN_TEST_SECONDS``."""
    return {module: recorded.get(module, count * UNKNOWN_TEST_SECONDS) for module, count in counts.items()}


def lpt_groups(seconds, jobs):
    """Modules in at most ``jobs`` groups, longest first to the lightest group (LPT, 설계 5.4)."""
    groups = [[0.0, index, []] for index in range(jobs)]
    for module, cost in sorted(seconds.items(), key=lambda item: (-item[1], item[0])):
        lightest = min(groups, key=lambda group: (group[0], group[1]))
        lightest[0] += cost
        lightest[2].append(module)
    return [group[2] for group in groups if group[2]]


def module_of(test):
    return test.id().rsplit('.', 2)[0]


def budget_report(rows, tiers, seconds, budgets):
    """Tests over their folder's budget and the named tiers' run time against their budget (설계 5.2).

    ``rows`` are report rows; legacy modules and fixture rows have no budget.
    Several tiers in one run are held to the largest of their budgets.
    """
    per_test = budgets['per_test_seconds']
    over = sorted(({'id': row['id'], 'seconds': row['seconds'], 'budget_seconds': per_test[row['id'].split('.')[0]]}
                   for row in rows if not row.get('fixture') and row['id'].split('.')[0] in per_test
                   and row['seconds'] > per_test[row['id'].split('.')[0]]), key=lambda row: row['id'])
    tier = None
    if tiers:
        limit = max(budgets['tier_seconds'][name] for name in tiers)
        tier = {'tiers': sorted(tiers), 'budget_seconds': limit, 'seconds': seconds, 'over': seconds > limit}
    return {'over_budget': over, 'tier': tier}


def group_of(test):
    return folder_of(test) or shard_for(test)


def discover(loader=None):
    loader = loader or unittest.TestLoader()
    return list(flatten(loader.discover(str(TESTS), pattern='test_*.py', top_level_dir=str(TESTS))))


# do_math is imported on first use, not at module import: T3 starts coverage before any product import.
def _write_json(path, value):
    from do_math.file_io import write_bytes_atomic
    write_bytes_atomic(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))


def _read_json(path):
    from do_math.file_io import read_bytes_shared
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
    def __init__(self, *args, directory, checkpoint=False, measurement=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory, self.checkpoint, self.measurement = directory, checkpoint, measurement
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
        if self.measurement is not None:
            self.measurement.test_started(test.id())
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
        if self.measurement is not None:
            self.measurement.test_stopped(test.id())
        self._progress(None, 'fixture_or_shutdown')

    def preserve(self, *, complete):
        report = {'complete': complete, 'successful': complete and self.wasSuccessful(),
                  'tests_run': self.testsRun, 'rows': list(self.rows.values())}
        _write_json(self.directory / 'result.json', report)
        return report


def _run_suite(tests, directory, *, checkpoint=False, measurement=None):
    directory.mkdir(parents=True, exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2, resultclass=lambda *a, **k: TimedResult(
        *a, directory=directory, checkpoint=checkpoint, measurement=measurement, **k)).run(unittest.TestSuite(tests))
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


def _isolated(tests, directory, timeout, *, measure=False):
    from do_math.windows_job import WindowsJob
    directory.mkdir(parents=True)
    identifiers = [test.id() for test in tests]
    _write_json(directory / 'requested.json', identifiers)
    if measure:  # a parallel T3 worker measures its own tests (support/branch_gate.py)
        _write_json(directory / 'measure.json', True)
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
    measurement = None
    if (directory / 'measure.json').exists():
        from support.branch_gate import DATA, Measurement, repository_root
        measurement = Measurement(repository_root(), data_file=directory / DATA)
        measurement.start()  # before the tests load, so import-time lines count
    with (directory / 'stdout.txt').open('w', encoding='utf-8', buffering=1) as out, \
            (directory / 'stderr.txt').open('w', encoding='utf-8', buffering=1) as err, \
            redirect_stdout(out), redirect_stderr(err):
        loader = unittest.TestLoader()
        if measurement is not None:
            # Import every test module as a one-process T3 does in discovery, so import-time lines
            # carry no test context here either; a module first imported inside a test would
            # otherwise credit its module-level lines to that one test, and T0 would select only it.
            discover(loader)
        tests = list(flatten(loader.loadTestsFromNames(_read_json(directory / 'requested.json'))))
        if measurement is not None:
            measurement.begin([test.id() for test in tests])
        report = _run_suite(tests, directory, checkpoint=True, measurement=measurement)
    if measurement is not None:
        measurement.save(directory)
    return 0 if report['successful'] else 1


def _edition():
    return {path.relative_to(SCRIPTS).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(SCRIPTS.rglob('*.py')) if '__pycache__' not in path.parts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tests', nargs='*', help='test IDs or modules; default: every shard')
    parser.add_argument('--shard', action='append', choices=tuple(SHARDS), help='legacy shard; repeat to combine')
    parser.add_argument('--tier', action='append', choices=tuple(TIERS), help='new-system tier T0-T5; repeat to combine')
    parser.add_argument('--match', action='append', default=[], help='test-ID glob; repeat for alternatives')
    parser.add_argument('--list', action='store_true', help='discover and list without running tests')
    parser.add_argument('--timeout', type=float, default=300, help='seconds per isolated test/fixture phase (default: 300)')
    parser.add_argument('--output', type=Path, help='new or empty results directory; default: a unique temporary directory')
    parser.add_argument('--mutation-base', help='with --tier T3: extreme-mutate the functions changed since this commit')
    parser.add_argument('--jobs', type=int, default=1,
                        help='run new-system in-process tests in this many worker processes, modules balanced by '
                             'their last recorded time (default: 1); with T3 each worker measures and the runner '
                             'combines their data')
    parser.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return _worker(args.worker)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    tiers = args.tier or []
    if args.mutation_base and 'T3' not in tiers:
        parser.error('--mutation-base runs with --tier T3')
    if args.jobs < 1:
        parser.error('--jobs is a positive count')
    missing, stale = unregistered_modules(TESTS)
    if missing or stale:
        print('scripts/test_categories.py SHARDS is out of date. Unregistered: ' + (', '.join(missing) or '-')
              + '. Listed but absent: ' + (', '.join(stale) or '-'), file=sys.stderr)
        return 2
    before = _edition()
    started_run = time.monotonic()
    measurement = None
    if 'T3' in tiers:
        if str(TESTS) not in sys.path:
            sys.path.insert(0, str(TESTS))
        from support.branch_gate import Measurement, repository_root
        measurement = Measurement(repository_root())
        if args.jobs == 1:
            measurement.start()  # before discovery, so import-time lines count

    def bail(code):
        if measurement is not None:
            measurement.abandon()
        return code

    loader = unittest.TestLoader()
    discovered = discover(loader)
    if loader.errors:
        print('\n'.join(loader.errors), file=sys.stderr)
        return bail(2)
    selection = None
    if args.tier or args.shard:
        pool = select_tiers(discovered, tiers) + [
            test for test in discovered if folder_of(test) is None and args.shard and shard_for(test) in args.shard]
        if 'T0' in tiers:
            from do_math.layers import LAYERS
            from support.branch_gate import repository_root
            from support.selection import choose
            selection = choose(repository_root(), LAYERS)
            chosen = {test.id() for test in pool}
            pool += [test for test in discovered if test.id() not in chosen and selection.picks(test.id())]
    elif args.tests:
        pool = discovered
    else:
        pool = [test for test in discovered if folder_of(test) is None or folder_of(test) in DEFAULT_FOLDERS]
    selected = [test for test in pool
                if (not args.tests or any(test.id() == name or test.id().startswith(name + '.') for name in args.tests))
                and (not args.match or any(fnmatch.fnmatchcase(test.id(), pattern) for pattern in args.match))]
    unknown = [name for name in args.tests or []
               if not any(test.id() == name or test.id().startswith(name + '.') for test in discovered)]
    if unknown:
        # A mistyped ID would otherwise drop out silently and read as a pass.
        print('No test matches: ' + ', '.join(unknown), file=sys.stderr)
        return bail(2)
    if not selected:
        print('No tests selected; no pass was established.', file=sys.stderr)
        return bail(2)
    if args.list:
        for test in selected:
            print(group_of(test) + '\t' + test.id())
        return bail(0)
    directory = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='do-math-tests-'))
    if directory.exists() and any(directory.iterdir()):
        bail(None)
        parser.error('--output must be new or empty; previous evidence is never overwritten')
    directory.mkdir(parents=True, exist_ok=True)
    from support.known_defects import open_count  # tests/ is importable after discovery
    open_defects = open_count()
    print(f'Open known defects: {open_defects}', flush=True)
    if selection is not None:
        print(selection_summary(selection), flush=True)
    reports, shard_seconds = [], {}
    if measurement is not None and not measurement.started:
        # Parallel T3: the workers measure; this measurement only combines their data.
        from support.branch_gate import Measurement, repository_root
        measurement = Measurement(repository_root(), data_file=directory / 'coverage.data')
    if measurement is not None and measurement.started:
        measurement.begin([test.id() for shard in (*SHARDS, *FOLDERS) for test in selected
                           if group_of(test) == shard and isolation_for(test) is None])
    parallel = args.jobs > 1
    if parallel:
        workers = _run_parallel([test for test in selected if folder_of(test) and isolation_for(test) is None],
                                directory, args.jobs, args.timeout, shard_seconds, measure=measurement is not None)
        reports += workers
        if measurement is not None:
            measurement.merge([report['directory'] for report in workers])
    for shard in (*SHARDS, *FOLDERS):
        tests = [test for test in selected if group_of(test) == shard]
        if not tests:
            continue
        started = time.monotonic()
        print(f'[{shard}] {len(tests)} tests', flush=True)
        in_process = [test for test in tests if isolation_for(test) is None and not (parallel and shard in FOLDERS)]
        if in_process:
            reports.append({'shard': shard, **_run_suite(
                in_process, directory / shard, measurement=measurement if measurement and measurement.started else None)})
        classes = defaultdict(list)
        for test in tests:
            if isolation_for(test) is not None:
                classes[type(test)].append(test)
        for index, members in enumerate(classes.values()):
            print('  isolated: ' + members[0].id().rsplit('.', 1)[0], flush=True)
            report = _isolated(members, directory / f'{shard}-isolated-{index:03}', args.timeout)
            print('  ' + str(dict(Counter(row['outcome'] for row in report['rows'] if not row.get('fixture')))), flush=True)
            reports.append({'shard': shard, **report})
        shard_seconds[shard] = round(time.monotonic() - started, 1)
        _write_json(directory / 'report.json', {'complete': False, 'shard_seconds': shard_seconds, 'reports': reports})
    after = _edition()
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    rows = [row for report in reports for row in report['rows']]
    _record_timings(rows)
    complete = all(report['complete'] for report in reports)
    t3 = _finish_t3(measurement, directory, selected, args, complete and not changed) if measurement else {}
    # T3's whole run, analysis and mutation included, is held to the T3 budget (설계 5.1, 5.2).
    total = round(time.monotonic() - started_run if measurement else sum(shard_seconds.values()), 1)
    budget = budget_report(rows, args.tier or [], total, json.loads((TESTS / 'budgets.json').read_text(encoding='utf-8')))
    result = {'open_known_defects': open_defects, 'budget': budget, **t3,
        't0_selection': selection.report() if selection is not None else None,
        'complete': all(report['complete'] for report in reports),
        'successful': not changed and all(report['successful'] for report in reports),
        'selected': [test.id() for test in selected], 'discovered': len(discovered),
        'shards': sorted(args.shard or []), 'tiers': sorted(args.tier or []), 'tests': args.tests,
        'shard_seconds': shard_seconds, 'total_seconds': total,
        'counts': dict(Counter(row['outcome'] for row in rows if not row.get('fixture'))),
        'fixture_counts': dict(Counter(row['outcome'] for row in rows if row.get('fixture'))),
        'source_sha256': before, 'changed_during_run': changed, 'reports': reports,
        'slowest': sorted((row for row in rows if not row.get('fixture')),
                          key=lambda row: row['seconds'], reverse=True)[:20]}
    _write_json(directory / 'report.json', result)
    tier = budget['tier']
    for line in t3.get('summary', []):
        print(line, flush=True)
    print(f"Over budget: {len(budget['over_budget'])} tests"
          + (f"; {'+'.join(tier['tiers'])} ran {tier['seconds']}s of {tier['budget_seconds']}s"
             + (' (over)' if tier['over'] else '') if tier else ''), flush=True)
    for row in budget['over_budget']:
        print(f"  {row['seconds']:9.3f}s > {row['budget_seconds']}s {row['id']}")
    print(json.dumps({name: result[name] for name in ('complete', 'successful', 'counts', 'shard_seconds', 'total_seconds')},
                     ensure_ascii=False))
    for row in result['slowest']:
        print(f"{row['seconds']:9.3f}s {row['outcome']:18} {row['id']}")
    if changed:
        print('Files changed during the run, so this is not a pass: ' + ', '.join(changed), file=sys.stderr)
    print('Report: ' + str(directory / 'report.json'))
    return 0 if result['successful'] and t3.get('passed', True) else 1


def _run_parallel(tests, directory, jobs, timeout, shard_seconds, *, measure=False):
    """New-system in-process tests in ``jobs`` worker processes, whole modules per worker (설계 5.4).

    A module stays in one process because its ``setUpModule`` and the Sim
    template belong to that process. Groups are balanced by the modules' last
    recorded seconds (``tests/.timings.json``).
    """
    from concurrent.futures import ThreadPoolExecutor
    if not tests:
        return []
    by_module = defaultdict(list)
    for test in tests:
        by_module[module_of(test)].append(test)
    recorded = _read_json(TIMINGS) or {}
    groups = lpt_groups(module_seconds({m: len(t) for m, t in by_module.items()}, recorded), jobs)
    print(f'[parallel] {len(tests)} tests in {len(groups)} workers', flush=True)
    started = time.monotonic()
    with ThreadPoolExecutor(len(groups)) as pool:
        futures = [pool.submit(_isolated, [test for module in group for test in by_module[module]],
                               directory / f'parallel-{index}', timeout, measure=measure)
                   for index, group in enumerate(groups)]
        reports = [{'shard': f'parallel-{index}', **future.result()} for index, future in enumerate(futures)]
    for report in reports:
        print(f"  {report['shard']}: " + str(dict(Counter(row['outcome'] for row in report['rows'] if not row.get('fixture'))))
              + f" in {round(report['worker_seconds'], 1)}s", flush=True)
    shard_seconds['parallel'] = round(time.monotonic() - started, 1)
    return reports


def _record_timings(rows):
    """Keep each new-system module's seconds for the next parallel run's balance; a partial run updates its modules."""
    seconds = defaultdict(float)
    for row in rows:
        if not row.get('fixture') and row['id'].split('.', 1)[0] in FOLDERS:
            seconds[row['id'].rsplit('.', 2)[0]] += row['seconds']
    if seconds:
        _write_json(TIMINGS, {**(_read_json(TIMINGS) or {}), **{m: round(v, 3) for m, v in seconds.items()}})


def selection_summary(selection):
    """T0's selection in one line, then one line per changed path and rule."""
    lines = [f"T0 selection ({selection.mode}{': ' + selection.reason if selection.reason else ''}): "
             f"{len(selection.tests)} tests, modules {sorted(selection.modules) or '-'}, folders {sorted(selection.folders) or '-'}"]
    lines += [f"  {change['path']}: {change['rule']}" for change in selection.reasons]
    return '\n'.join(lines)


def _finish_t3(measurement, directory, selected, args, clean):
    """Stop measuring; judge the gate, rewrite the index after a full clean run, and mutate on request.

    The index is written only when the run was the whole T3 selection (no test
    IDs, no --match), every group completed and no file changed during it; a
    partial run would drop tests from the index.
    """
    from do_math.layers import LAYERS
    from support import branch_gate
    report = measurement.finish(directory)
    prefix = SCRIPTS.relative_to(measurement.root).as_posix()
    gate = branch_gate.gate(report['files'], LAYERS, prefix)
    summary = [branch_gate.gate_summary(gate)]
    index = None
    if clean and not args.tests and not args.match:
        tests = [test.id() for test in selected if isolation_for(test) is None]
        index = branch_gate.write_index(measurement, report, tests)
        summary.append(f"Selection index: {index['tests']} tests, {index['measured_files']} measured files, "
                       f"{index['inputs']} inputs, commit {index['commit'][:12]} -> {index['path']}")
    else:
        summary.append('Selection index not written: the run was partial, incomplete or saw files change.')
    mutation = None
    if args.mutation_base:
        from support import mutation as mutation_tool
        from support.selection import read_index
        current, _ = read_index()
        mutation = mutation_tool.run(args.mutation_base, current if index else None, LAYERS, measurement.root,
                                     directory / 'mutation', timeout=args.timeout)
        summary.append(mutation_tool.summary(mutation))
        summary += [f'  survived: {name}' for name in mutation['survived']]
    passed = gate['passed'] and (mutation is None or mutation['unreasoned_entries'] == 0)
    return {'branch_gate': gate, 'selection_index': index, 'mutation': mutation, 'summary': summary, 'passed': passed}


if __name__ == '__main__':
    raise SystemExit(main())
