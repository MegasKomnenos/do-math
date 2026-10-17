"""Extreme mutation of changed product functions (docs/do-math/시험-재편-2026-09-29/설계.md 6.3).

Targets: every function or method, nested ones included, of a layer 1-3 module
of ``do_math.layers.LAYERS`` whose body (docstring excluded, compared as AST)
differs from the base commit's, or that the base commit lacks. A function is
keyed by its qualified name (``Class.method``, ``outer.<locals>.inner``); a
repeated name gets ``#2``, ``#3`` in order of appearance.

Rule by the shape of the body, looking only at the function's own scope, not
at nested functions, and ignoring the return annotation:

* ``return_first`` for a generator (the body holds ``yield``): ``return`` goes
  before the first statement (``return; `` on a one-line body);
* ``return_none`` when the body holds ``return <value>`` with a value other than
  the constant None: the whole body becomes ``return None``;
* ``pass`` otherwise (a function that changes state): the whole body becomes ``pass``.

The docstring stays. A body that is only ``pass`` or ``...`` is ``trivial`` and not
mutated, because its mutant would be the function itself.

Tests: those the selection index credits with entering the function (its
qualified name, without the ``#n`` of a repeated name). A function the index
does not know in a file that changed since the index was measured, or a
missing or stale index, adds the module's layer folders
(``selection.LAYER_FOLDERS``). A function no test entered in an unchanged file
is ``not_executed``; the branch gate reports it, and it does not enter the
pseudo-tested list.

``--test ID`` (repeatable; API ``explicit_tests``) adds exact unittest method
IDs to the automatic selection for every targeted function of the ``--only``
modules. It requires a nonempty ``--only`` scope and never replaces indexed
tests or the layer-folder fallback. IDs are deduplicated; they are supplied
inputs, not measured entry ordinals. Each outcome's ``selection`` records the
indexed ordinals, explicit IDs and effective tests/folders. Collection and
execution use the same child evidence and unmutated-baseline rules below.

``--function module:key`` (repeatable; API ``function_selectors``) restricts
plans to exact scripts-relative modules and the keys returned by ``functions``
(including nested and repeated names). Every selector must resolve within the
layer 1-3 / ``--only`` / changed-function scope before any child starts. Use
``--every`` to include unchanged functions. Invalid or unresolved selectors
raise ValueError (CLI usage error); they never fall back to a whole module.
The report records the deduplicated selectors. List updates affect only actual
outcomes; other entries and their reasons remain intact.

Each child writes one result: ``selection`` (tests/folders/exclude), actual
``collected`` IDs, ``rows`` (id/outcome/fixture), ``tests_run`` and ``load_error``
(null or the failing batch's selection and diagnostic strings). ``validate_result``
is used by both producer and reader. ``attempt.json`` adds the command, PID,
exit code, elapsed seconds and any process/result error; ``output.txt`` keeps
tracebacks. A missing, malformed or inconsistent result, abnormal exit, empty
execution, fixture error/skip, test skip or expected failure is evidence failure,
not a normal pass. Attempts have distinct directories and are never overwritten.
The CLI and T3 use the same ``passed`` predicate: unreasoned survivors,
unmutated baseline failures, execution/mutation errors or unexecuted targets
prevent a pass even when the pseudo-tested list is empty.

Execution: never in the working tree. The mutant source is written to a
temporary file, and a child interpreter (``--child``) imports it in place of the
module through a meta-path loader that keeps the original ``__file__``. One
failing test kills a mutant, so the child runs the chosen tests cheapest first
(the unmeasured module times of ``tests/.timings.json`` per chosen test, a
module's tests kept together) and stops at the first failure (``failfast``).
There is no baseline run of every chosen test (결함 D9): a test that failed a
mutant is run once unmutated, alone, and remembered. A mutant is ``killed`` when
a test fails, errors or unexpectedly passes that actually passes unmutated.
A load error kills only if its same batch actually collects and passes unmutated;
its diagnostic text is never a test ID. Baseline attempts and their disposition
are retained in ``baselines`` and linked from each mutant attempt. A failing test
that also fails unmutated is set aside
and the mutant runs again without it. Otherwise the mutant survived. Elapsed
time is reported, never used to terminate a child or certify a killed mutant.

``--jobs 1..3`` (API ``jobs``, default 1) runs that many function plans in
threads, each owning at most one mutant or normal child at a time. Concurrent
requests for the same normal selection share one Future. All children use the
runner's Windows Job ownership and separate scratch directories. There is no
cross-command baseline cache. Source and selection inputs must stay unchanged
during the command; other test commands count against the same three slots.
Only the parent updates the list after joining the plans. The output directory
must be new or empty. Each completed plan also retains ``outcome.json``. An
explicit interrupt joins owned trees, retains attempts, returns ``interrupted``
and does not update the list. Restart with a new output directory; there is no
automatic resume or promotion of an unfinished attempt to a completed result.

List: ``tests/pseudo_tested.json`` holds ``{"entries": [{module, function, rule,
base, reason}]}``. A survivor without an entry gains one with an empty reason;
the entry of a killed function is removed. The report counts entries whose
reason is empty; a sub-stage closes only when that count is 0.

``run_tests.py --tier T3 --mutation-base <commit>`` runs this after the coverage
run, on the index just written. A worker may run it alone, e.g.
``python tests/support/mutation.py --base <fork point> [--only do_math/x.py]``.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from concurrent.futures import CancelledError, Future, ThreadPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Event, Lock
import time
import traceback

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = SCRIPTS / 'tests'
PSEUDO_TESTED = TESTS / 'pseudo_tested.json'
TIMINGS = TESTS / '.timings.json'  # the runner's unmeasured module seconds; a mutant child runs unmeasured
UNKNOWN_TEST_SECONDS = 0.5  # a module the record does not know, per test (as run_tests)
MAX_JOBS = 3
FAILURES = frozenset({'failed', 'error', 'unexpected_success'})
NOTE = ('Pseudo-tested functions (설계 6.3): the extreme mutant of each survived every test that runs the '
        'function. An entry closes a sub-stage only with a reason; a function whose None return equals '
        'its behaviour says so in the reason.')
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


class _FunctionSelectionError(ValueError):
    """Selector usage errors; other run failures keep their existing CLI exit meaning."""


def functions(tree):
    """[(key, node)] for every function in ``tree``, in source order."""
    found, seen = [], Counter()

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                seen[name] += 1
                found.append((name if seen[name] == 1 else f'{name}#{seen[name]}', child))
                visit(child, name + '.<locals>.')
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + '.')
            else:
                visit(child, prefix)

    visit(tree, '')
    return found


def _is_docstring(statement):
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) \
        and isinstance(statement.value.value, str)


def body(node):
    """The function's statements after its docstring."""
    return node.body[1:] if node.body and _is_docstring(node.body[0]) else list(node.body)


def own_nodes(node):
    """Nodes of the function's own scope: nested functions, lambdas and classes are not entered."""
    stack = list(node.body)
    while stack:
        current = stack.pop()
        if isinstance(current, _SCOPES):
            continue
        yield current
        stack.extend(ast.iter_child_nodes(current))


def rule_of(node):
    own = list(own_nodes(node))
    if any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in own):
        return 'return_first'
    if any(isinstance(n, ast.Return) and n.value is not None
           and not (isinstance(n.value, ast.Constant) and n.value.value is None) for n in own):
        return 'return_none'
    return 'pass'


def _dump(statements):
    return [ast.dump(statement) for statement in statements]


def changed_functions(base_text, text):
    """Functions of ``text`` whose body differs from ``base_text``'s function of the same key, or that are new."""
    base = {key: _dump(body(node)) for key, node in functions(ast.parse(base_text))} if base_text else {}
    return [(key, node) for key, node in functions(ast.parse(text)) if base.get(key) != _dump(body(node))]


def _trivial(statements):
    return all(isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                                           and s.value.value is Ellipsis) for s in statements)


def mutate(text, node):
    """(rule, mutant text) for ``node`` of ``text``, or (rule, None) when the body is trivial or empty.

    AST column offsets are UTF-8 byte offsets, so the splice works on bytes.
    """
    rule, statements = rule_of(node), body(node)
    if not statements or _trivial(statements):
        return rule, None
    lines = text.encode('utf-8').splitlines(keepends=True)
    first, last = statements[0], statements[-1]
    start = min([(first.lineno, first.col_offset)]
                + [(d.lineno, d.col_offset - 1) for d in getattr(first, 'decorator_list', [])])
    end = (last.end_lineno, last.end_col_offset)
    before, head = b''.join(lines[:start[0] - 1]), lines[start[0] - 1][:start[1]]
    if rule == 'return_first':
        # A block body starts on its own indented line; a one-line body follows ``def ...:``.
        opener = b'return\n' + head if not head.strip() else b'return; '
        mutated = before + head + opener + b''.join(lines[start[0] - 1:])[start[1]:]
    else:
        replacement = b'return None' if rule == 'return_none' else b'pass'
        mutated = before + head + replacement + lines[end[0] - 1][end[1]:] + b''.join(lines[end[0]:])
    return rule, mutated.decode('utf-8')


def tests_for(entry, current_blob, key, layer):
    """(test ids as ordinals, fallback folders) for the function ``key`` (see module docstring)."""
    from support.selection import LAYER_FOLDERS, SELECTABLE
    folders = tuple(LAYER_FOLDERS.get(layer, SELECTABLE))
    if entry is None or 'functions' not in entry:
        return set(), folders
    ordinals = set(entry['functions'].get(key.split('#', 1)[0], ()))
    if ordinals or entry.get('blob') == current_blob:
        return ordinals, ()
    return set(), folders


def read_list(path=PSEUDO_TESTED):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {'note': NOTE, 'entries': []}


def update_list(listing, outcomes, base):
    """Add survivors without an entry (empty reason), drop entries of killed functions; returns whether it changed."""
    before = json.dumps(listing, sort_keys=True)
    killed = {(o['module'], o['function']) for o in outcomes if o['status'] == 'killed'}
    entries = [e for e in listing['entries'] if (e['module'], e['function']) not in killed]
    known = {(e['module'], e['function']) for e in entries}
    for o in outcomes:
        if o['status'] == 'survived' and (o['module'], o['function']) not in known:
            entries.append({'module': o['module'], 'function': o['function'], 'rule': o['rule'],
                            'base': base, 'reason': ''})
    listing['entries'] = sorted(entries, key=lambda e: (e['module'], e['function']))
    return json.dumps(listing, sort_keys=True) != before


def unreasoned(listing):
    return sum(not str(e.get('reason', '')).strip() for e in listing['entries'])


def _git(root, *arguments):
    return subprocess.run(['git', *arguments], cwd=root, capture_output=True, check=False)




def recorded_seconds():
    """The runner's unmeasured seconds per test module (``tests/.timings.json``), or none."""
    try:
        return json.loads(Path(TIMINGS).read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        return {}




def expected_seconds(chosen, seconds):
    """Recorded seconds of the modules of ``chosen`` tests and of every module of its folders."""
    modules = {test.rsplit('.', 2)[0] for test in chosen['tests']}
    modules |= {module for module in seconds if module.split('.')[0] in chosen['folders']}
    return sum(seconds.get(module, UNKNOWN_TEST_SECONDS) for module in modules)

def cheapest_first(tests, seconds):
    """``tests`` ordered by their module's recorded seconds per chosen test, cheapest first, modules kept together."""
    modules = [type(test).__module__ for test in tests]
    counts = Counter(modules)
    cost = {module: seconds.get(module, UNKNOWN_TEST_SECONDS * counts[module]) / counts[module] for module in counts}
    order = sorted(range(len(tests)), key=lambda i: (cost[modules[i]], modules[i], i))
    return [tests[i] for i in order]


def _selection(spec):
    return {key: list(spec.get(key, ())) for key in ('tests', 'folders', 'exclude')}


def _new_result(spec):
    return {'selection': _selection(spec), 'collected': [], 'rows': [], 'tests_run': 0, 'load_error': None}


def validate_result(result, spec):
    """Reject malformed/unbound child evidence at both ends; no legacy formats."""
    def names(value):
        return (isinstance(value, list) and all(isinstance(name, str) and name for name in value)
                and len(set(value)) == len(value))

    if not isinstance(result, dict) or set(result) != set(_new_result(spec)):
        raise ValueError('invalid result fields')
    chosen = result['selection']
    if (not isinstance(chosen, dict) or set(chosen) != {'tests', 'folders', 'exclude'}
            or not all(names(value) for value in chosen.values()) or chosen != _selection(spec)):
        raise ValueError('result selection does not match spec')
    if not names(result['collected']) or not isinstance(result['rows'], list):
        raise ValueError('invalid collected IDs or rows')
    collected, seen = set(result['collected']), set()
    if collected & set(chosen['exclude']):
        raise ValueError('excluded test was collected')
    if any(name not in chosen['tests'] and not any(name.startswith(folder + '.') for folder in chosen['folders'])
           for name in collected):
        raise ValueError('collected test is outside the selection')
    for row in result['rows']:
        if (not isinstance(row, dict) or set(row) != {'id', 'outcome', 'fixture'}
                or not isinstance(row['id'], str) or not row['id']
                or type(row['fixture']) is not bool or not isinstance(row['outcome'], str)
                or row['outcome'] not in FAILURES | {'passed', 'skipped', 'expected_failure'}):
            raise ValueError('invalid result row')
        if row['id'] in seen or (not row['fixture'] and row['id'] not in collected):
            raise ValueError('duplicate or uncollected result row')
        seen.add(row['id'])
    if (type(result['tests_run']) is not int
            or result['tests_run'] != sum(not row['fixture'] for row in result['rows'])):
        raise ValueError('tests_run does not match executed rows')
    error = result['load_error']
    if error is not None:
        if (not isinstance(error, dict) or set(error) != {'selection', 'details'}
                or not isinstance(error['selection'], dict)
                or set(error['selection']) != set(chosen)
                or not all(names(value) for value in error['selection'].values())
                or error['selection']['exclude'] != chosen['exclude']
                or not set(error['selection']['tests']) <= set(chosen['tests'])
                or not set(error['selection']['folders']) <= set(chosen['folders'])
                or not (error['selection']['tests'] or error['selection']['folders'])
                or not isinstance(error['details'], list) or not error['details']
                or not all(isinstance(item, str) and item for item in error['details'])):
            raise ValueError('invalid load_error')


def _evidence_error(result):
    """A valid shape may still contain no completed, usable test evidence."""
    for row in result['rows']:
        if row['fixture'] or row['outcome'] in {'skipped', 'expected_failure'}:
            return f"{'fixture' if row['fixture'] else 'test'} {row['id']}: {row['outcome']}"
    if result['load_error'] is not None:
        return None  # run() checks the identical batch unmutated before judging a load failure
    if not result['tests_run']:
        return 'no tests executed'
    if not any(row['outcome'] in FAILURES for row in result['rows']):
        executed = {row['id'] for row in result['rows']}
        missing = (set(result['collected']) | set(result['selection']['tests'])) \
            - set(result['selection']['exclude']) - executed
        if missing:
            return 'expected tests did not execute: ' + ', '.join(sorted(missing))
    return None


def validate_jobs(jobs):
    """The mutation command owns at most three simultaneous mutant/normal children."""
    if type(jobs) is not int or not 1 <= jobs <= MAX_JOBS:
        raise ValueError(f'jobs must be an integer between 1 and {MAX_JOBS}')
    return jobs


def _child_run(spec, directory, *, cancelled=None):
    """Run one real child without a timeout; retain process, raw result and validation errors."""
    from do_math.windows_job import WindowsJob
    from run_tests import wait_for_worker, worker_exit_code

    directory = Path(directory)
    directory.mkdir(parents=True)  # a retry must use a new path, never stale result bytes
    (directory / 'spec.json').write_text(json.dumps(spec), encoding='utf-8')
    started = time.monotonic()
    attempt = {'directory': str(directory), 'started': datetime.now(timezone.utc).isoformat(),
               'command': [sys.executable, '-B', str(Path(__file__).resolve()), '--child',
                           str(directory / 'spec.json')], 'pid': None, 'exit_code': None,
               'result': None, 'error': None}
    errors = []
    scratch = directory / 'scratch'
    scratch.mkdir()
    (directory / 'output.txt').touch()
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                   'TEMP': str(scratch), 'TMP': str(scratch), 'TMPDIR': str(scratch)}
    try:
        if cancelled is not None and cancelled.is_set():
            raise CancelledError('mutation run interrupted before child start')
        with WindowsJob(attempt['command'], cwd=SCRIPTS, env=environment) as job:
            attempt['pid'] = job.pid
            try:
                (directory / 'attempt.json').write_text(json.dumps(attempt, indent=1), encoding='utf-8')
                job.resume()
                wait_for_worker(job, cancelled=cancelled)
            except BaseException:
                job.terminate()
                wait_for_worker(job)
                attempt['exit_code'] = worker_exit_code(job)
                raise
            attempt['exit_code'] = worker_exit_code(job)
        if attempt['exit_code'] != 0:
            errors.append(f"child exit {attempt['exit_code']}")
    except (OSError, CancelledError, KeyboardInterrupt) as error:
        errors.append(f'child process error: {type(error).__name__}: {error}')
        if isinstance(error, KeyboardInterrupt) and cancelled is not None:
            cancelled.set()
    try:
        result = json.loads((directory / 'result.json').read_text(encoding='utf-8'))
        validate_result(result, spec)
        attempt['result'] = result
    except (OSError, ValueError, UnicodeError) as error:
        errors.append(f'child result error: {type(error).__name__}: {error}')
    attempt.update(seconds=time.monotonic() - started, finished=datetime.now(timezone.utc).isoformat(),
                   error='; '.join(errors) if errors else None)
    (directory / 'attempt.json').write_text(json.dumps(attempt, indent=1), encoding='utf-8')
    return attempt


def run(base, index, layers, root, directory, *, only=(), every=False, listing_path=PSEUDO_TESTED,
        explicit_tests=(), jobs=1, function_selectors=()):
    """Mutate the functions changed since ``base`` and report; see the module docstring.

    ``every`` targets every function of the chosen modules, as if ``base`` lacked
    them: stage 1f moves tests without changing the product, so the check that
    moved tests look at results mutates the functions those tests reach.

    ``explicit_tests`` supplements the automatic selection in the required
    ``only`` module scope; it does not assert measured function entry.
    ``jobs`` limits mutant and normal children together, within this command.
    """
    from support.branch_gate import git_blobs
    validate_jobs(jobs)
    explicit_tests = sorted(set(explicit_tests))
    if explicit_tests and not only:
        raise ValueError('explicit tests require an --only module scope')
    if any(len(name.split('.')) < 3 or not all(part.isidentifier() for part in name.split('.'))
           for name in explicit_tests):
        raise ValueError('explicit tests must be exact qualified unittest method IDs')
    started = time.monotonic()
    resolved = _git(root, 'rev-parse', '--verify', '--quiet', f'{base}^{{commit}}')
    if resolved.returncode:
        raise ValueError(f'base {base!r} is not a commit')
    base = resolved.stdout.decode().strip()
    directory = Path(directory).resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('mutation output directory must be new or empty')
    directory.mkdir(parents=True, exist_ok=True)
    prefix = SCRIPTS.relative_to(root).as_posix()
    tests = index['tests'] if index else []
    modules = sorted(m for m, layer in layers.items() if layer in ('1', '2', '3')
                     and (not only or any(fnmatch.fnmatchcase(m, pattern) for pattern in only)))
    requested = set()
    for selector in function_selectors:
        if not isinstance(selector, str) or selector.count(':') != 1:
            raise _FunctionSelectionError(f'invalid function selector {selector!r}; expected scripts-relative-module:key')
        module, key = selector.split(':')
        if not module or not key or module not in modules:
            raise _FunctionSelectionError(f'function selector outside selected layer 1-3 modules: {selector!r}')
        requested.add((module, key))
    if requested:
        modules = [module for module in modules if any(m == module for m, _ in requested)]
    blobs = git_blobs(root, [f'{prefix}/{m}' for m in modules])
    outcomes, plans = [], []
    resolved_functions = set()
    for module in modules:
        path = f'{prefix}/{module}'
        text = (SCRIPTS / module).read_text(encoding='utf-8')
        shown = _git(root, 'show', f'{base}:{path}')
        base_text = shown.stdout.decode('utf-8') if shown.returncode == 0 and not every else ''
        for key, node in changed_functions(base_text, text):
            if requested and (module, key) not in requested:
                continue
            resolved_functions.add((module, key))
            rule, mutant = mutate(text, node)
            outcome = {'module': module, 'function': key, 'rule': rule, 'line': node.lineno}
            outcomes.append(outcome)
            if mutant is None:
                outcome['status'] = 'trivial'
                continue
            try:
                compile(mutant, str(SCRIPTS / module), 'exec', dont_inherit=True)
            except SyntaxError as error:
                outcome.update(status='mutation_error', detail=str(error))
                continue
            entry = index['files'].get(path) if index else None
            ordinals, folders = tests_for(entry, blobs[path], key, layers[module])
            chosen_tests = sorted({tests[o] for o in ordinals} | set(explicit_tests))
            outcome['selection'] = {'indexed_ordinals': sorted(ordinals),
                                    'explicit_tests': explicit_tests,
                                    'tests': chosen_tests, 'folders': list(folders)}
            if not chosen_tests and not folders:
                outcome['status'] = 'not_executed'
                continue
            outcome['tests'] = len(chosen_tests)
            outcome['folders'] = list(folders)
            plans.append((outcome, mutant, {'tests': chosen_tests, 'folders': list(folders)}))
    unresolved = requested - resolved_functions
    if unresolved:
        raise _FunctionSelectionError('unresolved function selectors in changed-function scope (use --every for unchanged functions): '
                                      + ', '.join(f'{module}:{key}' for module, key in sorted(unresolved)))
    seconds = recorded_seconds()
    unmutated = {}  # selection -> one Future; a concurrent request shares the same normal child
    baseline_lock, cancelled = Lock(), Event()

    def baseline(chosen):
        key = tuple(tuple(chosen[field]) for field in ('tests', 'folders', 'exclude'))
        with baseline_lock:
            owner = key not in unmutated
            if owner:
                unmutated[key] = Future()
            future = unmutated[key]
            number = list(unmutated).index(key)
        if not owner:
            return future.result()
        try:
            attempt = _child_run({**chosen, 'target': None, 'mutant': None},
                                 directory / f'unmutated-{number:04}', cancelled=cancelled)
            result = attempt['result']
            error = attempt['error'] or _evidence_error(result)
            if not error and result['load_error'] is not None:
                error = 'normal selection failed to load: ' + '; '.join(result['load_error']['details'])
            failing = [row['id'] for row in result['rows']
                       if not row['fixture'] and row['outcome'] in FAILURES] if result else []
            normal = {'id': number, 'selection': chosen, 'attempt': attempt,
                      'status': 'evidence_error' if error else 'failing' if failing else 'passed',
                      'failing': failing, 'detail': error}
            future.set_result(normal)
        except BaseException as error:
            future.set_exception(error)
            raise
        return normal

    def execute(number, plan):
        if cancelled.is_set():
            return
        outcome, mutant, chosen = plan
        outcome['estimated_seconds'] = expected_seconds(chosen, seconds)
        work = Path(directory) / f'mutant-{number:04}'
        work.mkdir(parents=True, exist_ok=True)
        (work / 'mutant.py').write_text(mutant, encoding='utf-8')
        excluded, took = set(), 0.0
        outcome['attempts'] = []
        while True:
            remaining = {'tests': [t for t in chosen['tests'] if t not in excluded],
                         'folders': chosen['folders'], 'exclude': sorted(excluded)}
            if not remaining['tests'] and not remaining['folders']:
                # All candidates really failed normally. Do not invent a zero-test pass.
                outcome.update(status='baseline_failing', detail='all selected tests fail unmutated')
                break
            attempt = _child_run({**remaining, 'target': str(SCRIPTS / outcome['module']),
                                   'mutant': str(work / 'mutant.py')},
                                  work / f'attempt-{len(outcome["attempts"]):04}', cancelled=cancelled)
            record = {'execution': attempt, 'baselines': []}
            outcome['attempts'].append(record)
            took += attempt['seconds']
            result = attempt['result']
            error = attempt['error'] or _evidence_error(result)
            if error:
                outcome.update(status='execution_error', detail=error)
                record['decision'] = error
                break
            if result['load_error'] is not None:
                normal = baseline(result['load_error']['selection'])
                record['baselines'].append(normal['id'])
                if normal['status'] == 'passed':
                    outcome.update(status='killed', killed_by=[row['id'] for row in normal['attempt']['result']['rows']],
                                   detail='mutant batch failed to load; the same normal selection actually passed')
                else:
                    outcome.update(status='execution_error',
                                   detail=normal['detail'] or 'normal selection also failed; load failure is not a kill')
                record['decision'] = outcome['detail']
                break
            failing = [row['id'] for row in result['rows'] if row['outcome'] in FAILURES]
            broken, killers, errors = set(), [], []
            for test in failing:
                normal = baseline({'tests': [test], 'folders': [], 'exclude': []})
                record['baselines'].append(normal['id'])
                if normal['status'] == 'passed':
                    killers.append(test)
                elif normal['status'] == 'failing':
                    broken.add(test)
                else:
                    errors.append(f"normal test {test}: {normal['detail']}")
            if errors:
                outcome.update(status='execution_error', detail='; '.join(errors))
                record['decision'] = outcome['detail']
                break
            if killers or not broken:
                outcome.update(status='killed' if killers else 'survived', killed_by=killers[:5])
                record['decision'] = outcome['status']
                break
            record['decision'] = 'exclude normal failures and retry'
            excluded |= broken
        outcome['seconds'] = round(took, 2)
        (work / 'outcome.json').write_text(json.dumps(outcome, ensure_ascii=False, indent=1), encoding='utf-8')

    pool = ThreadPoolExecutor(max_workers=jobs)
    pending = []
    try:
        pending = [pool.submit(execute, number, plan) for number, plan in enumerate(plans)]
        for future in as_completed(pending):
            future.result()
    except KeyboardInterrupt:
        cancelled.set()
    except BaseException:
        cancelled.set()
        raise
    finally:
        if cancelled.is_set():
            for future in pending:
                future.cancel()
        pool.shutdown(wait=True, cancel_futures=True)
    for outcome, _, _ in plans:
        if 'status' not in outcome:
            outcome.update(status='execution_error', detail='mutation run interrupted before completion')
    baselines = [future.result() for future in unmutated.values()]
    baseline_failing = {test for item in baselines for test in item['failing']}
    listing = read_list(listing_path)
    if not cancelled.is_set() and update_list(listing, outcomes, base):
        Path(listing_path).write_text(json.dumps(listing, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    counts = Counter(o['status'] for o in outcomes)
    return {'base': base, 'every': every, 'explicit_tests': explicit_tests, 'jobs': jobs,
            'function_selectors': [f'{module}:{key}' for module, key in sorted(requested)],
            'interrupted': cancelled.is_set(),
            'functions': len(outcomes), 'counts': dict(counts),
            'baseline_failing': sorted(baseline_failing), 'baselines': baselines,
            'unreasoned_entries': unreasoned(listing),
            'list': str(listing_path), 'seconds': round(time.monotonic() - started, 1),
            'survived': [f"{o['module']}:{o['function']}" for o in outcomes if o['status'] == 'survived'],
            'outcomes': outcomes}


def summary(report):
    counts = report['counts']
    scope = 'every function of the chosen modules' if report.get('every') else f"since {report['base'][:12]}"
    if report.get('function_selectors'):
        scope = 'exact selected functions'
    return (f"Extreme mutation, {scope}: {report['functions']} functions; "
            + ', '.join(f'{name} {counts[name]}' for name in sorted(counts))
            + f"; unreasoned pseudo-tested entries: {report['unreasoned_entries']} ({report['seconds']}s)")


def passed(report):
    """A zero survivor count cannot cover failed measurement or untested functions."""
    return (not report.get('interrupted', False) and report['unreasoned_entries'] == 0 and not report['baseline_failing']
            and not any(report['counts'].get(name, 0)
                        for name in ('execution_error', 'mutation_error', 'not_executed', 'baseline_failing')))


def _flatten(suite):
    for item in suite:
        if hasattr(item, '__iter__'):
            yield from _flatten(item)
        else:
            yield item


def _child(spec_path):
    """Import the temporary mutant and record actual collection and execution, including fixture events."""
    import importlib.abc
    import importlib.machinery
    import unittest

    class Result(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rows = {}

        def startTest(self, test):
            super().startTest(test)
            self.rows[test.id()] = {'id': test.id(), 'outcome': 'running', 'fixture': False}

        def record(self, test, outcome):
            row = self.rows.setdefault(test.id(), {'id': test.id(), 'fixture': True})
            row['outcome'] = outcome

        def addSuccess(self, test):
            super().addSuccess(test)
            self.record(test, 'passed')

        def addFailure(self, test, err):
            super().addFailure(test, err)
            self.record(test, 'failed')

        def addError(self, test, err):
            super().addError(test, err)
            self.record(test, 'error')

        def addSkip(self, test, reason):
            super().addSkip(test, reason)
            self.record(getattr(test, 'test_case', test), 'skipped')

        def addExpectedFailure(self, test, err):
            super().addExpectedFailure(test, err)
            self.record(test, 'expected_failure')

        def addUnexpectedSuccess(self, test):
            super().addUnexpectedSuccess(test)
            self.record(test, 'unexpected_success')

        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            if err is not None:
                self.record(test, 'failed' if issubclass(err[0], test.failureException) else 'error')

    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    sys.path[:0] = [str(SCRIPTS), str(TESTS)]
    sys.dont_write_bytecode = True
    if spec['target']:
        target = Path(spec['target']).resolve()
        source = Path(spec['mutant']).read_text(encoding='utf-8')

        class MutantLoader(importlib.machinery.SourceFileLoader):
            def get_code(self, fullname):
                return compile(source, self.path, 'exec', dont_inherit=True)

        class MutantFinder(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path, target_module=None):
                found = importlib.machinery.PathFinder.find_spec(name, path)
                if found is not None and found.origin and Path(found.origin).resolve() == target:
                    found.loader = MutantLoader(name, found.origin)
                    return found
                return None

        sys.meta_path.insert(0, MutantFinder())
    loader = unittest.TestLoader()
    seconds = recorded_seconds()
    if spec['folders']:
        # Unknown/stale index retains the complete folder discovery fallback.
        covered = set(spec['folders'])
        batches = [(spec['folders'], [name for name in spec['tests'] if name.split('.')[0] not in covered])]
    else:
        modules = defaultdict(list)
        for name in spec['tests']:
            modules[name.rsplit('.', 2)[0]].append(name)
        ordered_modules = sorted(modules, key=lambda module: (
            seconds.get(module, UNKNOWN_TEST_SECONDS * len(modules[module])) / len(modules[module]), module))
        batches = [([], modules[module]) for module in ordered_modules]
    excluded = set(spec.get('exclude', ()))
    evidence = _new_result(spec)
    for folders, names in batches:
        suite = unittest.TestSuite()
        load_error = None
        try:
            for folder in folders:
                suite.addTests(loader.discover(str(TESTS / folder), pattern='test_*.py', top_level_dir=str(TESTS)))
            if names:
                suite.addTests(loader.loadTestsFromNames(names))
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            load_error = [f'{type(error).__name__}: {error}']
        if load_error or loader.errors:
            evidence['load_error'] = {'selection': {'tests': names, 'folders': folders,
                                                    'exclude': sorted(excluded)},
                                      'details': load_error or list(loader.errors)}
            for detail in evidence['load_error']['details']:
                print(detail)
            break
        tests = [test for test in _flatten(suite) if test.id() not in excluded]
        evidence['collected'].extend(test.id() for test in tests)
        ordered = unittest.TestSuite(cheapest_first(tests, seconds))
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1, failfast=True,
                                         resultclass=Result).run(ordered)
        evidence['tests_run'] += result.testsRun
        evidence['rows'].extend(result.rows.values())
        if not result.wasSuccessful():
            break
    validate_result(evidence, spec)
    (Path(spec_path).parent / 'result.json').write_text(json.dumps(evidence), encoding='utf-8')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', help='commit the changed functions are compared with')
    parser.add_argument('--only', action='append', default=[], help='scripts-relative module glob; repeat')
    parser.add_argument('--function', action='append', default=[],
                        help='exact scripts-relative module:qualified-function-key within scope; repeat')
    parser.add_argument('--test', action='append', default=[],
                        help='exact unittest method ID added to automatic selection; requires --only; repeat')
    parser.add_argument('--every', action='store_true',
                        help='mutate every function of the chosen modules, not only those changed since --base')
    parser.add_argument('--jobs', type=int, default=1, help='simultaneous mutant/normal children, 1..3 (default: 1)')
    parser.add_argument('--output', type=Path, help='work directory; default: a new temporary directory')
    parser.add_argument('--child', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child:
        with (args.child.parent / 'output.txt').open('w', encoding='utf-8') as output:
            # This private child owns its process streams, including native writes
            # and subprocess output that Python's redirect_stdout cannot capture.
            os.dup2(output.fileno(), 1)
            os.dup2(output.fileno(), 2)
            with redirect_stdout(output), redirect_stderr(output):
                try:
                    return _child(args.child)
                except BaseException:
                    traceback.print_exc()
                    raise
    if not args.base:
        parser.error('--base is required')
    try:
        validate_jobs(args.jobs)
    except ValueError as error:
        parser.error(str(error))
    if args.test and not args.only:
        parser.error('--test requires --only')
    sys.path[:0] = [str(SCRIPTS), str(TESTS)]
    from do_math.layers import LAYERS
    from support.branch_gate import repository_root
    from support.selection import is_ancestor_of_head, read_index, usable
    root = repository_root()
    index, reason = usable(*read_index(), is_ancestor_of_head(root))
    if index is None:
        print(f'Selection index unusable ({reason}); every mutant runs its layer folders.', flush=True)
    directory = args.output or Path(tempfile.mkdtemp(prefix='do-math-mutation-'))
    try:
        report = run(args.base, index, LAYERS, root, directory, only=args.only, every=args.every,
                     explicit_tests=args.test, jobs=args.jobs, function_selectors=args.function)
    except _FunctionSelectionError as error:
        parser.error(str(error))
    (Path(directory) / 'mutation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(summary(report))
    for name in report['survived']:
        print('  survived: ' + name)
    print('Report: ' + str(Path(directory) / 'mutation.json'))
    return 0 if passed(report) else 1


if __name__ == '__main__':
    raise SystemExit(main())
