"""The T3 store: an incremental T3 measures again only the test modules whose measurement may have changed (설계 A29).

A full T3 run leaves its measurement in a store (default ``tests/.t3-store``,
Git-ignored, one per working tree): the coverage data with a context per test
module (``<module>`` and ``fixture:<module>``, see ``branch_gate``), each test's
entered functions and opened inputs, and a record of what every module's
measurement relied on. The next T3 run plans against the current tree (``plan``).

A test module is **reused** (its tests do not run; its stored measurement joins
the new one) unless one of these holds for it, in which case it is **measured**
again:

(a) it is new to the store, or its file changed (git blob);
(b) the body or the position of a function its tests or fixtures entered
    changed (``code_digests``). A shared build it restored (a Sim template,
    ``branch_gate.shared_state``) counts as entered. Position is part of it
    because stored arcs are line numbers: a function that only moved cannot
    reuse them;
(d) an input its tests or fixtures opened, or an observed shared producer
    they consumed opened, changed or is gone.

Everything is measured again (a **full** plan) when the store is missing, of
another format or coverage version, or when ``--full`` asks for it, or when:

(c) the module- or class-level code of any non-test ``.py`` under ``scripts/``
    the store knows changed or is gone (``code_digests`` top: imports,
    definitions and their signatures, defaults and decorators, class bodies),
    or a runner file changed (``RUNNER``, including all of
    ``test_categories.py``), or an input read at import by non-test code changed.

"Product" in A29 is read broadly here: ``tests/support`` and fixture modules are
recorded like product code, so their function bodies follow (b) and their
module level follows (c). A ``.py`` new to the tree is not a change: only code
that changed can import it, and that code is measured again. A module the
store holds that no longer exists is dropped.

A run that reused any module is no closing run: sub-stages and regions close
only on a run that reused none (``closing_eligible`` in the runner's report).
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess

from support.branch_gate import FIXTURE, SHARED, credited_functions

FORMAT = 'do-math-t3-store/2'
DATA, RECORDS = 'coverage.data', 'records.json'
COVERAGE_SCHEMA = 7  # coverage 7.x data file schema; another one is never filtered
# Scripts-relative files whose change measures everything again: the runner and the measurement.
RUNNER = ('run_tests.py', 'test_categories.py', 'tests/support/branch_gate.py', 'tests/support/t3_store.py')


def _digest(value):
    return hashlib.sha256(repr(value).encode('utf-8')).hexdigest()[:20]


def _is_docstring(statement):
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) \
        and isinstance(statement.value.value, str)


def _without_docstring(statements):
    return statements[1:] if statements and _is_docstring(statements[0]) else list(statements)


def _start(node):
    return min([node.lineno] + [decorator.lineno for decorator in getattr(node, 'decorator_list', [])])


class _Top(ast.NodeTransformer):
    """Module- and class-level code: every function body emptied, docstrings of module and classes dropped."""

    def visit_Module(self, node):
        node.body = _without_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        node.body = _without_docstring(node.body) or [ast.Pass()]
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        node.body = [ast.Pass()]
        for field in ('decorator_list', 'args', 'returns', 'type_params'):
            value = getattr(node, field, None)
            if isinstance(value, list):
                setattr(node, field, [self.visit(item) for item in value])
            elif isinstance(value, ast.AST):
                setattr(node, field, self.visit(value))
        return node

    visit_AsyncFunctionDef = visit_FunctionDef


def code_digests(text):
    """``{'top': digest, 'functions': {qualname: digest}}`` of a Python source, or None when it does not parse.

    ``top`` covers module- and class-level code without positions. A function's
    digest covers its body (docstring excluded) and its first and last line; a
    class's covers its lines; ``<module>`` covers the lines of every top-level
    statement. Qualified names follow ``co_qualname`` (``Class.method``,
    ``outer.<locals>.inner``); repeated names share one digest.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    functions = {}

    def add(name, value):
        functions[name] = _digest((functions.get(name), value))

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                add(name, (ast.dump(ast.Module(body=_without_docstring(child.body), type_ignores=[])),
                           _start(child), child.end_lineno))
                visit(child, name + '.<locals>.')
            elif isinstance(child, ast.ClassDef):
                name = prefix + child.name
                add(name, (_start(child), child.end_lineno))
                visit(child, name + '.')
            else:
                visit(child, prefix)
    visit(tree, '')
    functions['<module>'] = _digest([(_start(statement), statement.end_lineno) for statement in tree.body])
    top = _digest(ast.dump(_Top().visit(ast.parse(text))))
    return {'top': top, 'functions': functions}


def runner_marks(current, paths):
    """Each runner file's git blob; every change invalidates the stored measurement."""
    return current.blobs(paths)


class Plan:
    """What an incremental T3 does: ``measure`` and ``reuse`` split the run's modules; ``drop`` leaves the store."""

    def __init__(self, mode, reason, measure, reuse, drop, why=None):
        self.mode, self.reason = mode, reason
        self.measure, self.reuse, self.drop = set(measure), set(reuse), set(drop)
        self.why = dict(why or {})

    def report(self):
        return {'mode': self.mode, 'reason': self.reason, 'measured_modules': sorted(self.measure),
                'reused_modules': sorted(self.reuse), 'dropped_modules': sorted(self.drop),
                'why': dict(sorted(self.why.items()))}


def test_module_path(scripts_prefix, module):
    """Repository path of a tier-folder test module (``unit.test_a`` -> ``<scripts>/tests/unit/test_a.py``)."""
    folder, name = module.split('.', 1)
    return f'{scripts_prefix}/tests/{folder}/{name}.py'


def plan(records, universe, existing, current, scripts_prefix, *, coverage_version, full=False):
    """The plan for a T3 run over test modules ``universe`` (see the module docstring for the rules).

    ``records`` is the stored record (``read``) or empty; ``existing`` holds
    every T3 test module of the tree now; ``current`` answers ``blobs(paths)``
    (a path's git blob, None when absent) and ``digests(path)``
    (``code_digests`` of the file, None when absent).
    """
    stored = (records or {}).get('modules', {})

    def everything(reason):
        return Plan('full', reason, universe, (), set(stored))
    if full:
        return everything('--full')
    if not records or records.get('format') != FORMAT:
        return everything('no store')
    if records.get('coverage') != coverage_version:
        return everything(f"store of coverage {records.get('coverage')}")
    runner = [f'{scripts_prefix}/{name}' for name in RUNNER]
    paths = set(runner) | set(records['import_inputs'])
    for module in universe & set(stored):
        paths.add(test_module_path(scripts_prefix, module))
        paths |= set(stored[module]['inputs'])
    blobs = current.blobs(sorted(paths))
    if runner_marks(current, runner) != {path: records['runner'].get(path) for path in runner}:
        return everything('the runner changed')
    digests = {}

    def digest_of(path):
        if path not in digests:
            digests[path] = current.digests(path)
        return digests[path]
    for path, top in sorted(records['tops'].items()):
        now = digest_of(path)
        if now is None or now['top'] != top:
            return everything(f'module- or class-level code changed: {path}')
    for path, blob in sorted(records['import_inputs'].items()):
        if blobs[path] != blob:
            return everything(f'an input read at import changed: {path}')
    measure, reuse, why = set(), set(), {}
    for module in sorted(universe):
        snapshot = stored.get(module)
        reason = None
        if snapshot is None:
            reason = 'new to the store'
        elif blobs[test_module_path(scripts_prefix, module)] != snapshot['blob']:
            reason = 'its file changed'
        else:
            for path, functions in sorted(snapshot['functions'].items()):
                now = digest_of(path)
                changed = [name for name, digest in sorted(functions.items())
                           if now is None or now['functions'].get(name) != digest]
                if changed:
                    reason = f'entered {path}:{changed[0]} changed'
                    break
            else:
                changed = sorted(path for path, blob in snapshot['inputs'].items() if blobs[path] != blob)
                if changed:
                    reason = f'input {changed[0]} changed'
        if reason:
            measure.add(module)
            why[module] = reason
        else:
            reuse.add(module)
    return Plan('incremental', f'{len(measure)} measured, {len(reuse)} reused', measure, reuse,
                set(stored) - set(existing), why)


def label_module(label):
    """The test module a recorder label belongs to (a test id or ``fixture:<module>``), else None."""
    if not label or label.startswith(SHARED):
        return None
    if label.startswith(FIXTURE):
        return label[len(FIXTURE):] or None
    return label.rsplit('.', 2)[0]


def module_records(tests, entered, opens, current, scripts_prefix, *, input_dependencies):
    """``{module: {tests, blob, functions, inputs}}``: what each measured module's measurement relied on.

    ``tests`` maps each module measured whole to its test ids; ``entered`` and
    ``opens`` are the run's records by label. A module relies on the functions
    its tests and its fixture phases entered, on those a shared build it
    restored entered, and on literal inputs plus separately recorded shared
    input dependencies. Shared function dependencies are transitive.
    """
    labels = {}
    for label in set(entered) | set(opens) | set(input_dependencies):
        module = label_module(label)
        if module in tests:
            labels.setdefault(module, []).append(label)
    out = {}
    paths = {test_module_path(scripts_prefix, module) for module in tests}
    module_inputs = {module: {path for label in labels.get(module, ())
                              for record in (opens, input_dependencies) for path in record.get(label, ())}
                     for module in tests}
    paths |= {path for inputs in module_inputs.values() for path in inputs}
    blobs = current.blobs(sorted(paths))
    digests = {}
    for module, ids in sorted(tests.items()):
        pairs = set()
        for label in labels.get(module, ()):
            pairs |= credited_functions(entered, label)
        functions = {}
        for path, key in sorted(pairs):
            if path not in digests:
                digests[path] = current.digests(path)
            functions.setdefault(path, {})[key] = (digests[path] or {}).get('functions', {}).get(key)
        inputs = {path: blobs[path] for path in module_inputs[module]}
        out[module] = {'tests': sorted(ids), 'blob': blobs[test_module_path(scripts_prefix, module)],
                       'inputs': dict(sorted(inputs.items())), 'functions': functions}
    return out


def records(root, scripts, modules, entered, opens, import_opens, current, coverage_version, stored=None,
            keep=(), *, input_dependencies):
    """The store record after a run: ``modules`` measured now, plus the stored modules in ``keep``.

    ``tops``, ``runner`` and ``import_inputs`` describe the tree now. Kept
    modules keep their stored record and their stored labels' entries.
    """
    prefix = scripts.relative_to(root).as_posix()
    runner = {f'{prefix}/{name}' for name in RUNNER}
    code = sorted(path.relative_to(root).as_posix() for path in scripts.rglob('*.py') if '__pycache__' not in path.parts)
    tops = {}
    for path in code:
        # Tier-folder test modules (tests/<folder>/test_*.py) and legacy ones (tests/test_*.py) are no product code.
        test = path.startswith(prefix + '/tests/') and Path(path).name.startswith('test_') \
            and path.count('/') - prefix.count('/') in (2, 3)
        if path in runner or test:
            continue
        digests = current.digests(path)
        tops[path] = digests['top'] if digests else None
    imported = sorted(path for path, openers in import_opens.items()
                      if any(not (Path(opener).name.startswith('test_') and '/tests/' in opener) for opener in openers))
    blobs = current.blobs(sorted(runner) + imported)
    stored = stored or {}
    kept = {module: stored['modules'][module] for module in keep if module in stored.get('modules', {})}
    kept_labels = {label for label in stored.get('entered', {}) if label_module(label) in kept} \
        | {label for label in stored.get('opens', {}) if label_module(label) in kept}
    merged_entered = {label: pairs for label, pairs in stored.get('entered', {}).items()
                      if label in kept_labels or label.startswith(SHARED)}
    for label, pairs in entered.items():
        if label.startswith(SHARED) and label in merged_entered:
            pairs = sorted({tuple(pair) for pair in merged_entered[label]} | {tuple(pair) for pair in pairs})
        merged_entered[label] = [list(pair) for pair in pairs]
    merged_opens = {label: paths for label, paths in stored.get('opens', {}).items() if label in kept_labels}
    merged_opens.update({label: sorted(paths) for label, paths in opens.items()})
    dependencies = {label: paths for label, paths in (stored['input_dependencies'] if stored else {}).items()
                    if label_module(label) in kept}
    dependencies.update({label: sorted(paths) for label, paths in input_dependencies.items()
                         if label_module(label) in modules})
    return {'format': FORMAT, 'coverage': coverage_version, 'root': str(root),
            'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'tops': tops, 'runner': runner_marks(current, sorted(runner)),
            'import_inputs': {path: blobs[path] for path in imported},
            'modules': {**kept, **modules}, 'entered': merged_entered, 'opens': merged_opens,
            'input_dependencies': dependencies,
            'import_opens': {path: sorted(openers) for path, openers in import_opens.items()}}


def stored_entries(stored, modules):
    """Stored entries, literal opens and input dependencies of reused labels, plus shared function records."""
    entered = {label: pairs for label, pairs in stored.get('entered', {}).items()
               if label_module(label) in modules or label.startswith(SHARED)}
    opens = {label: paths for label, paths in stored.get('opens', {}).items() if label_module(label) in modules}
    dependencies = {label: paths for label, paths in stored['input_dependencies'].items()
                    if label_module(label) in modules}
    return entered, opens, dependencies


def module_contexts(modules):
    """The coverage contexts that hold ``modules``' measurement (``branch_gate``: ``<module>``, ``fixture:<module>``)."""
    return {name for module in modules for name in (module, FIXTURE + module)}


def reused_data(store, modules, target):
    """A copy of the store's coverage data at ``target`` holding only ``modules``' contexts; returns ``target``.

    The copy is filtered in SQL on coverage's schema 7; any other schema raises
    ``ValueError`` and the caller measures in full.
    """
    target = Path(target)
    shutil.copyfile(Path(store) / DATA, target)
    keep = module_contexts(modules)
    connection = sqlite3.connect(target)
    try:
        version = connection.execute('select version from coverage_schema').fetchone()[0]
        if version != COVERAGE_SCHEMA:
            raise ValueError(f'coverage data schema {version} is not {COVERAGE_SCHEMA}')
        dropped = [(identity,) for identity, context in connection.execute('select id, context from context')
                   if context not in keep]
        for table in ('arc', 'line_bits'):
            connection.executemany(f'delete from {table} where context_id = ?', dropped)
        connection.executemany('delete from context where id = ?', dropped)
        connection.commit()
    finally:
        connection.close()
    return target


def path_mapper(old_root, new_root):
    """Map a measured file path from the store's tree to this one (a store copied from another worktree)."""
    old, new = str(old_root).rstrip('\\/'), str(new_root).rstrip('\\/')

    def mapped(path):
        return new + path[len(old):] if path.lower().startswith(old.lower()) else path
    return mapped


def read(store):
    """The stored record, or {} when there is none or it does not read."""
    try:
        return json.loads((Path(store) / RECORDS).read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        return {}


def write(store, data_file, record, extra=None):
    """Replace the store with ``data_file`` (plus ``extra`` coverage data, already mapped) and ``record``."""
    from coverage import CoverageData
    store = Path(store)
    fresh, old = store.with_name(store.name + '.new'), store.with_name(store.name + '.old')
    for path in (fresh, old):
        shutil.rmtree(path, ignore_errors=True)
    fresh.mkdir(parents=True)
    shutil.copyfile(data_file, fresh / DATA)
    if extra is not None:
        CoverageData(basename=str(fresh / DATA)).update(CoverageData(basename=str(extra[0])), map_path=extra[1])
    (fresh / RECORDS).write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
    if store.exists():
        store.rename(old)
    fresh.rename(store)
    shutil.rmtree(old, ignore_errors=True)


class Tree:
    """The working tree now: git blobs (batched, cached) and ``code_digests`` of files by repository path."""

    def __init__(self, root):
        self.root = Path(root)
        self._blobs, self._digests = {}, {}

    def blobs(self, paths):
        missing = [path for path in paths if path not in self._blobs]
        present = [path for path in missing if (self.root / path).is_file()]
        if present:
            output = subprocess.run(['git', 'hash-object', '--stdin-paths'], cwd=self.root,
                                    input='\n'.join(present) + '\n', capture_output=True, text=True,
                                    check=True).stdout.split()
            self._blobs.update(zip(present, output))
        self._blobs.update({path: None for path in missing if path not in present})
        return {path: self._blobs[path] for path in paths}

    def source(self, path):
        """The file's text, or None when absent or not UTF-8."""
        try:
            return (self.root / path).read_text(encoding='utf-8')
        except (FileNotFoundError, UnicodeDecodeError):
            return None

    def digests(self, path):
        if path not in self._digests:
            text = self.source(path)
            self._digests[path] = code_digests(text) if text is not None else None
        return self._digests[path]
