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

Tests: those the selection index credits with running any code line of the
function's body. When the file changed since the index was measured, current
lines map to measured lines through the ``difflib`` equal blocks against the
measured text. A code line that does not map, a measured text that git no
longer has, or a missing or stale index adds the module's layer folders
(``selection.LAYER_FOLDERS``). A function no test runs is ``not_executed``; the
branch gate reports it, and it does not enter the pseudo-tested list.

Execution: never in the working tree. The mutant source is written to a
temporary file, and a child interpreter (``--child``) imports it in place of the
module through a meta-path loader that keeps the original ``__file__``. It runs
the chosen tests with unittest; each mutant has a time limit. One baseline child
first runs the union of all chosen tests unmutated; a mutant is ``killed`` when a
test fails, errors or unexpectedly passes that did not at baseline, or when the
child exceeds its limit (``timeout``). Otherwise it ``survived``.

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
import difflib
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


def body_lines(node):
    statements = body(node)
    first = statements[0]
    start = min([first.lineno] + [d.lineno for d in getattr(first, 'decorator_list', [])])
    return range(start, statements[-1].end_lineno + 1)


def line_map(old_text, new_text):
    """{new line: old line} for lines inside difflib's equal blocks."""
    matcher = difflib.SequenceMatcher(None, old_text.splitlines(), new_text.splitlines(), autojunk=False)
    return {b + k + 1: a + k + 1 for a, b, size in matcher.get_matching_blocks() for k in range(size)}


def tests_for(entry, current_blob, read_blob, text, lines, layer):
    """(test ids as ordinals, fallback folders) for code ``lines`` of the current ``text`` (see module docstring)."""
    from support.selection import LAYER_FOLDERS, SELECTABLE, code_owners
    folders = tuple(LAYER_FOLDERS.get(layer, SELECTABLE))
    if entry is None or 'lines' not in entry:
        return set(), folders
    owners = code_owners(text) or {}
    code = [line for line in lines if line in owners]
    if entry.get('blob') == current_blob:
        mapping = {line: line for line in code}
    else:
        old_text = read_blob(entry.get('blob'))
        if old_text is None:
            return set(), folders
        mapping = line_map(old_text, text)
    ordinals = {o for line in code if line in mapping for o in entry['lines'].get(str(mapping[line]), ())}
    return ordinals, folders if any(line not in mapping for line in code) else ()


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

    def read_blob(blob):
        result = _git(root, 'cat-file', 'blob', blob) if blob else None
        return result.stdout.decode('utf-8') if result is not None and result.returncode == 0 else None

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
            ordinals, folders = tests_for(entry, blobs[path], read_blob, text, body_lines(node), layers[module])
            if not ordinals and not folders:
                outcome['status'] = 'not_executed'
                continue
            outcome['tests'] = len(ordinals)
            outcome['folders'] = list(folders)
            plans.append((outcome, mutant, {'tests': sorted(tests[o] for o in ordinals), 'folders': list(folders)}))
    baseline = set()
    if plans:
        union = {'tests': sorted({t for _, _, s in plans for t in s['tests']}),
                 'folders': sorted({f for _, _, s in plans for f in s['folders']})}
        baseline, seconds = _child_run({**union, 'target': None, 'mutant': None}, Path(directory) / 'baseline', timeout)
        if baseline is None:
            raise RuntimeError(f'baseline run of the chosen tests exceeded {timeout} s')
    for number, (outcome, mutant, chosen) in enumerate(plans):
        work = Path(directory) / f'mutant-{number:04}'
        work.mkdir(parents=True, exist_ok=True)
        (work / 'mutant.py').write_text(mutant, encoding='utf-8')
        failing, seconds = _child_run({**chosen, 'target': str(SCRIPTS / outcome['module']),
                                       'mutant': str(work / 'mutant.py')}, work, timeout)
        outcome['seconds'] = round(seconds, 2)
        if failing is None:
            outcome['status'] = 'timeout'
        else:
            new = sorted(failing - baseline)
            outcome['status'] = 'killed' if new else 'survived'
            outcome['killed_by'] = new[:5]
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
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
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
    parser.add_argument('--timeout', type=float, default=300.0, help='seconds per mutant run (default: 300)')
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
