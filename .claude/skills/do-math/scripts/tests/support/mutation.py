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

Execution: never in the working tree. The mutant source is written to a
temporary file, and a child interpreter (``--child``) imports it in place of the
module through a meta-path loader that keeps the original ``__file__``. One
failing test kills a mutant, so the child runs the chosen tests cheapest first
(the unmeasured module times of ``tests/.timings.json`` per chosen test, a
module's tests kept together) and stops at the first failure (``failfast``).
There is no baseline run of every chosen test (결함 D9): a test that failed a
mutant is run once unmutated, alone, and remembered. A mutant is ``killed`` when
a test fails, errors or unexpectedly passes that passes unmutated, or when a
test module fails to load, or when the child exceeds its limit (``timeout``). A
failing test that also fails unmutated is set aside and the mutant runs again
without it. Otherwise the mutant ``survived``. Each mutant's time limit is three
times the recorded seconds of the modules it runs (at least 30 s, at most
``--timeout``, ``mutant_timeout``).

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
from collections import Counter
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = SCRIPTS / 'tests'
PSEUDO_TESTED = TESTS / 'pseudo_tested.json'
TIMINGS = TESTS / '.timings.json'  # the runner's unmeasured module seconds; a mutant child runs unmeasured
UNKNOWN_TEST_SECONDS = 0.5  # a module the record does not know, per test (as run_tests)
NOTE = ('Pseudo-tested functions (설계 6.3): the extreme mutant of each survived every test that runs the '
        'function. An entry closes a sub-stage only with a reason; a function whose None return equals '
        'its behaviour says so in the reason.')
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


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
    killed = {(o['module'], o['function']) for o in outcomes if o['status'] in ('killed', 'timeout')}
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


def mutant_timeout(expected_seconds, ceiling):
    """A mutant's time limit: three times the expected unmutated run, at least 30 s, at most ``ceiling``.

    A mutant that hangs counts as killed either way, so the limit only has to
    let a mutant that survives but runs slower (a result it throws away is
    recomputed) finish. The expectation is the recorded seconds of every module
    the mutant's tests belong to, which bounds the run of a part of them.
    """
    return min(ceiling, max(30.0, 3 * expected_seconds))


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


def _is_test_id(name):
    """A failing entry that names a test, not a loader error's text."""
    return bool(name) and not any(character.isspace() for character in name)


def _child_run(spec, directory, timeout):
    """Run one child; returns (failing test ids or None on timeout, seconds)."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'spec.json').write_text(json.dumps(spec), encoding='utf-8')
    started = time.monotonic()
    with (directory / 'output.txt').open('w', encoding='utf-8') as output:
        process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--child',
                                    str(directory / 'spec.json')], cwd=SCRIPTS, stdout=output,
                                   stderr=subprocess.STDOUT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return None, time.monotonic() - started
    result = json.loads((directory / 'result.json').read_text(encoding='utf-8')) \
        if (directory / 'result.json').exists() else {'failing': ['<child produced no result>']}
    return set(result['failing']), time.monotonic() - started


def run(base, index, layers, root, directory, *, only=(), every=False, timeout=300.0, listing_path=PSEUDO_TESTED):
    """Mutate the functions changed since ``base`` and report; see the module docstring.

    ``every`` targets every function of the chosen modules, as if ``base`` lacked
    them: stage 1f moves tests without changing the product, so the check that
    moved tests look at results mutates the functions those tests reach.
    """
    from support.branch_gate import git_blobs
    started = time.monotonic()
    resolved = _git(root, 'rev-parse', '--verify', '--quiet', f'{base}^{{commit}}')
    if resolved.returncode:
        raise ValueError(f'base {base!r} is not a commit')
    base = resolved.stdout.decode().strip()
    directory = Path(directory).resolve()
    prefix = SCRIPTS.relative_to(root).as_posix()
    tests = index['tests'] if index else []
    modules = sorted(m for m, layer in layers.items() if layer in ('1', '2', '3')
                     and (not only or any(fnmatch.fnmatchcase(m, pattern) for pattern in only)))
    blobs = git_blobs(root, [f'{prefix}/{m}' for m in modules])
    outcomes, plans = [], []
    for module in modules:
        path = f'{prefix}/{module}'
        text = (SCRIPTS / module).read_text(encoding='utf-8')
        shown = _git(root, 'show', f'{base}:{path}')
        base_text = shown.stdout.decode('utf-8') if shown.returncode == 0 and not every else ''
        for key, node in changed_functions(base_text, text):
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
            if not ordinals and not folders:
                outcome['status'] = 'not_executed'
                continue
            outcome['tests'] = len(ordinals)
            outcome['folders'] = list(folders)
            plans.append((outcome, mutant, {'tests': sorted(tests[o] for o in ordinals), 'folders': list(folders)}))
    seconds = recorded_seconds()
    unmutated = {}  # test id -> whether it fails with no mutant

    def fails_unmutated(test):
        if test not in unmutated:
            failing, _ = _child_run({'tests': [test], 'folders': [], 'exclude': [], 'target': None, 'mutant': None},
                                    Path(directory) / f'unmutated-{len(unmutated):04}', timeout)
            unmutated[test] = failing is None or test in failing
        return unmutated[test]

    for number, (outcome, mutant, chosen) in enumerate(plans):
        work = Path(directory) / f'mutant-{number:04}'
        work.mkdir(parents=True, exist_ok=True)
        (work / 'mutant.py').write_text(mutant, encoding='utf-8')
        limit, excluded, took = mutant_timeout(expected_seconds(chosen, seconds), timeout), set(), 0.0
        while True:
            failing, spent = _child_run({'tests': [t for t in chosen['tests'] if t not in excluded],
                                         'folders': chosen['folders'], 'exclude': sorted(excluded),
                                         'target': str(SCRIPTS / outcome['module']), 'mutant': str(work / 'mutant.py')},
                                        work, limit)
            took += spent
            if failing is None:
                outcome['status'] = 'timeout'
                break
            broken = {t for t in failing if _is_test_id(t) and fails_unmutated(t)}
            killers = sorted(failing - broken)
            if killers or not broken:
                outcome['status'] = 'killed' if killers else 'survived'
                outcome['killed_by'] = killers[:5]
                break
            excluded |= broken  # it fails unmutated too: run the mutant again without it
        outcome['seconds'] = round(took, 2)
    baseline = {test for test, fails in unmutated.items() if fails}
    listing = read_list(listing_path)
    if update_list(listing, outcomes, base):
        Path(listing_path).write_text(json.dumps(listing, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    counts = Counter(o['status'] for o in outcomes)
    return {'base': base, 'every': every, 'functions': len(outcomes), 'counts': dict(counts),
            'baseline_failing': sorted(baseline), 'unreasoned_entries': unreasoned(listing),
            'list': str(listing_path), 'seconds': round(time.monotonic() - started, 1),
            'survived': [f"{o['module']}:{o['function']}" for o in outcomes if o['status'] == 'survived'],
            'outcomes': outcomes}


def summary(report):
    counts = report['counts']
    scope = 'every function of the chosen modules' if report.get('every') else f"since {report['base'][:12]}"
    return (f"Extreme mutation, {scope}: {report['functions']} functions; "
            + ', '.join(f'{name} {counts[name]}' for name in sorted(counts))
            + f"; unreasoned pseudo-tested entries: {report['unreasoned_entries']} ({report['seconds']}s)")


def _flatten(suite):
    for item in suite:
        if hasattr(item, '__iter__'):
            yield from _flatten(item)
        else:
            yield item


def _child(spec_path):
    """Import the mutant in place of its module and run the chosen tests; write the failing ids."""
    import importlib.abc
    import importlib.machinery
    import unittest
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
    suite = unittest.TestSuite()
    for folder in spec['folders']:
        suite.addTests(loader.discover(str(TESTS / folder), pattern='test_*.py', top_level_dir=str(TESTS)))
    covered = set(spec['folders'])
    names = [name for name in spec['tests'] if name.split('.')[0] not in covered]
    if names:
        suite.addTests(loader.loadTestsFromNames(names))
    excluded = set(spec.get('exclude', ()))
    tests = [test for test in _flatten(suite) if test.id() not in excluded]
    ordered = unittest.TestSuite(cheapest_first(tests, recorded_seconds()))
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1, failfast=True).run(ordered)
    failing = [test.id() for test, _ in result.failures + result.errors] \
        + [test.id() for test in result.unexpectedSuccesses]
    failing += [str(error) for error in loader.errors]
    (Path(spec_path).parent / 'result.json').write_text(json.dumps({'failing': failing}), encoding='utf-8')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', help='commit the changed functions are compared with')
    parser.add_argument('--only', action='append', default=[], help='scripts-relative module glob; repeat')
    parser.add_argument('--every', action='store_true',
                        help='mutate every function of the chosen modules, not only those changed since --base')
    parser.add_argument('--timeout', type=float, default=300.0,
                        help='ceiling in seconds of the unmutated run and of each mutant run (default: 300); '
                             'a mutant gets three times the unmutated run, at least 30 s')
    parser.add_argument('--output', type=Path, help='work directory; default: a new temporary directory')
    parser.add_argument('--child', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child:
        return _child(args.child)
    if not args.base:
        parser.error('--base is required')
    sys.path[:0] = [str(SCRIPTS), str(TESTS)]
    from do_math.layers import LAYERS
    from support.branch_gate import repository_root
    from support.selection import is_ancestor_of_head, read_index, usable
    root = repository_root()
    index, reason = usable(*read_index(), is_ancestor_of_head(root))
    if index is None:
        print(f'Selection index unusable ({reason}); every mutant runs its layer folders.', flush=True)
    directory = args.output or Path(tempfile.mkdtemp(prefix='do-math-mutation-'))
    report = run(args.base, index, LAYERS, root, directory, only=args.only, every=args.every, timeout=args.timeout)
    (Path(directory) / 'mutation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(summary(report))
    for name in report['survived']:
        print('  survived: ' + name)
    print('Report: ' + str(Path(directory) / 'mutation.json'))
    return 0 if report['unreasoned_entries'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
