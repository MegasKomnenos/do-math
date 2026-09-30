"""T0 test selection from the T3 selection index (docs/do-math/시험-재편-2026-09-29/설계.md 5.3).

T0 always runs the structure checks; ``choose`` adds tests from the in-process
folders ``unit``, ``contracts`` and ``sim`` (``SELECTABLE``). Boundary and smoke
tests stay in T4/T5 and legacy ``tests/test_*.py`` modules in their shards.

Fresh index (its ``commit`` is HEAD or an ancestor of HEAD). A file changed
when its current git blob id differs from the one the index recorded at
measurement. Comparing with the measured content rather than with HEAD keeps
the index's line numbers valid when T3 ran on an uncommitted tree or on an
older commit. For each changed path:

* a test file of a selectable folder: that whole test module (5.3 row 1);
* a measured ``.py`` whose measured text is still in git: the changed regions
  are found with ``difflib`` against that text. A region that touches code
  (not blank, comment or docstring lines) is owned by the innermost function
  whose *body* holds each touched line, in the measured text for replaced or
  deleted lines and in the current text for inserted ones; a definition's
  header (decorators, signature, defaults) runs in the enclosing scope and
  belongs to it. Only a test that entered the owning function can run a
  changed body line, inserted ones included, so the tests the index credits
  with entering the owners are chosen. A touched line outside every function
  body (module or class level, run at import) takes the module's fallback
  (5.3 row 2). A function no test entered selects nothing: its body runs in no
  test until other code changes;
* a measured ``.py`` whose measured text is gone from git, or that was deleted:
  every test that entered any of its functions, plus the module's fallback;
* an unmeasured or new ``.py``: the module's fallback;
* a non-Python input the index saw opened: the tests that opened it (5.3 row 3);
  an input opened with no test to credit (an import-time open whose opener no
  test entered) takes every selectable folder. New inputs have no reader yet;
  the change that makes a test read one selects that test.

Fallback of a module (also the whole rule when the index is missing, of
another format, or stale, 5.3 row 4). The fallback is the module-level
selection T1 makes:

* a product module (``do_math.layers.LAYERS`` or under ``do_math/``): every test
  of its layer's folders (``LAYER_FOLDERS``: layers 1 and 2 -> unit and contracts,
  layer 3 -> sim, adapter -> contracts, undeclared -> all three);
* a test file of a selectable folder: that module;
* any other ``.py`` under ``scripts/`` (support, runner, fixtures): the
  selectable test modules that import it directly or through other non-product
  modules (AST imports);
* without an index, a non-Python file under the skill: all selectable folders.

Without an index the changed paths come from ``git diff --name-only HEAD`` and
``git ls-files --others --exclude-standard`` under the skill directory. Paths
outside the skill directory select nothing.
"""
from __future__ import annotations

import ast
import difflib
import json
from pathlib import Path
import subprocess

from support.branch_gate import FORMAT, INDEX, SCRIPTS, git_blobs, scripts_python

SELECTABLE = ('unit', 'contracts', 'sim')
TEST_FOLDERS = ('structure', 'unit', 'contracts', 'sim', 'flows', 'boundary', 'smoke')
LAYER_FOLDERS = {'1': ('unit', 'contracts'), '2': ('unit', 'contracts'), '3': ('sim',), 'adapter': ('contracts',)}


class Selection:
    """What T0 adds to the structure checks: test ids, test modules and whole folders, with reasons."""

    def __init__(self, mode, reason=''):
        self.mode, self.reason = mode, reason
        self.tests, self.modules, self.folders = set(), set(), set()
        self.reasons = []

    def add(self, path, rule, *, tests=(), modules=(), folders=()):
        tests, modules, folders = set(tests), set(modules), set(folders)
        self.tests |= tests
        self.modules |= modules
        self.folders |= folders
        self.reasons.append({'path': path, 'rule': rule, 'tests': len(tests),
                             'modules': sorted(modules), 'folders': sorted(folders)})

    def picks(self, test_id):
        folder = test_id.split('.')[0]
        return folder in SELECTABLE and (folder in self.folders or test_id in self.tests
                                         or test_id.rsplit('.', 2)[0] in self.modules)

    def report(self):
        return {'mode': self.mode, 'reason': self.reason, 'tests': len(self.tests),
                'modules': sorted(self.modules), 'folders': sorted(self.folders), 'changes': self.reasons}


class Paths:
    """Classifies repository-relative paths against the skill's layout."""

    def __init__(self, scripts_prefix, layers):
        self.scripts, self.layers = scripts_prefix.rstrip('/'), layers
        self.skill = self.scripts.rsplit('/', 1)[0]

    def scripts_relative(self, path):
        return path[len(self.scripts) + 1:] if path.startswith(self.scripts + '/') else None

    def test_module(self, path):
        """``folder.test_x`` for a test file of a tier folder, else None."""
        relative = self.scripts_relative(path)
        parts = relative.split('/') if relative else []
        if len(parts) == 3 and parts[0] == 'tests' and parts[1] in TEST_FOLDERS \
                and parts[2].startswith('test_') and parts[2].endswith('.py'):
            return parts[1] + '.' + parts[2][:-3]
        return None

    def is_legacy_test(self, path):
        relative = self.scripts_relative(path) or ''
        return relative.count('/') == 1 and relative.startswith('tests/test_') and relative.endswith('.py')

    def product_layer(self, path):
        """(True, layer or None) for a product module, else (False, None)."""
        relative = self.scripts_relative(path)
        if relative in self.layers:
            return True, self.layers[relative]
        if relative and relative.startswith('do_math/') and relative.endswith('.py'):
            return True, None
        return False, None

    def module_name(self, path):
        """Import name of a non-product scripts .py: tests/ and scripts/ are both on sys.path."""
        relative = self.scripts_relative(path)
        name = relative[len('tests/'):] if relative.startswith('tests/') else relative
        name = name[:-3].replace('/', '.')
        return name[:-len('.__init__')] if name.endswith('.__init__') else name


def code_owners(text):
    """{line: first line of the innermost statement holding it} for lines that are code, or None on a syntax error.

    Blank lines, comment-only lines and docstrings are not code. A decorated
    definition starts at its first decorator, as coverage records it.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    lines = text.splitlines()
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docstrings.update(range(first.lineno, first.end_lineno + 1))
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.stmt, ast.excepthandler, ast.match_case)) and hasattr(node, 'lineno'):
            start = min([node.lineno] + [d.lineno for d in getattr(node, 'decorator_list', [])])
            end = getattr(node, 'end_lineno', None) or node.lineno
            spans.append((end - start, start, end))
    owners = {}
    for _, start, end in sorted(spans, reverse=True):  # widest first, so inner statements win
        for line in range(start, end + 1):
            owners[line] = start
    return {line: owner for line, owner in owners.items()
            if line not in docstrings and line <= len(lines)
            and lines[line - 1].strip() and not lines[line - 1].strip().startswith('#')}


def _text_code(text):
    """Fallback for a text that does not parse: every non-blank, non-comment line is its own statement."""
    return {number: number for number, line in enumerate(text.splitlines(), 1)
            if line.strip() and not line.strip().startswith('#')}


def region_anchors(old_text, new_text):
    """Per changed region that touches code, the old-text statement lines that anchor it (see module docstring)."""
    old_lines, new_lines = old_text.splitlines(), new_text.splitlines()
    old_code = code_owners(old_text)
    old_code = _text_code(old_text) if old_code is None else old_code
    new_code = code_owners(new_text)
    new_code = _text_code(new_text) if new_code is None else new_code
    ordered = sorted(old_code)
    regions = []
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        touched_old = [line for line in range(i1 + 1, i2 + 1) if line in old_code]
        touched_new = [line for line in range(j1 + 1, j2 + 1) if line in new_code]
        if not touched_old and not touched_new:
            continue
        # A test that ran none of the replaced or deleted statements runs the same after the change;
        # only a pure insertion needs its neighbours to say which tests pass through the new code.
        anchors = {old_code[line] for line in touched_old}
        if not anchors:
            before = [line for line in ordered if line <= i1]
            after = [line for line in ordered if line > i2]
            anchors = {old_code[before[-1]]} if before else set()
            anchors |= {old_code[after[0]]} if after else set()
        regions.append({'old': [i1 + 1, i2], 'new': [j1 + 1, j2], 'anchors': sorted(anchors)})
    return regions


def body_owners(text):
    """{line: qualified name of the innermost function whose body holds it}, or None on a syntax error.

    A body runs from its first statement to the function's last line; the
    header (decorators, signature, defaults) belongs to the enclosing scope.
    Qualified names follow ``co_qualname`` (``Class.method``, ``f.<locals>.g``).
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    owners = {}

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                for line in range(child.body[0].lineno, child.end_lineno + 1):
                    owners[line] = name
                visit(child, name + '.<locals>.')
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + '.')
            else:
                visit(child, prefix)
    visit(tree, '')
    return owners


def region_owners(old_text, new_text, region):
    """(qualified names owning the region's touched code lines, whether a touched line lies outside every body)."""
    names, outside = set(), False
    for text, (start, end) in ((old_text, region['old']), (new_text, region['new'])):
        code = code_owners(text)
        code = _text_code(text) if code is None else code
        owners = body_owners(text) or {}
        for line in range(start, end + 1):
            if line in code:
                if line in owners:
                    names.add(owners[line])
                else:
                    outside = True
    return names, outside


def tests_of_functions(entry, names):
    return {o for name in names for o in entry.get('functions', {}).get(name, ())}


def import_graph(scripts):
    """{module name: set of module names it imports} for every non-product .py under ``scripts``."""
    graph = {}
    for path in scripts.rglob('*.py'):
        relative = path.relative_to(scripts)
        if '__pycache__' in relative.parts or relative.parts[0] == 'do_math' \
                or (len(relative.parts) == 2 and relative.parts[0] == 'tests' and relative.name.startswith('test_')):
            continue
        in_tests = relative.parts[0] == 'tests'
        name = '.'.join((relative.parts[1:] if in_tests else relative.parts))[:-3]
        package = name.rsplit('.', 1)[0] if '.' in name else ''
        if name.endswith('.__init__'):
            name = package = name[:-len('.__init__')]
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
        except SyntaxError:
            graph[name] = set()
            continue
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ''
                if node.level:
                    parent = package.split('.')[:len(package.split('.')) - node.level + 1] if package else []
                    base = '.'.join([p for p in parent if p] + ([node.module] if node.module else []))
                imported.add(base)
                imported |= {f'{base}.{alias.name}' if base else alias.name for alias in node.names}
        graph[name] = imported
    return graph


def importing_test_modules(graph, module):
    """Selectable test modules that import ``module`` directly or through other non-product modules."""
    reached, frontier = {module}, [module]
    while frontier:
        target = frontier.pop()
        for name, imported in graph.items():
            if name not in reached and any(i == target or i.startswith(target + '.') for i in imported):
                reached.add(name)
                frontier.append(name)
    return {name for name in reached if name.split('.')[0] in SELECTABLE and name.split('.')[-1].startswith('test_')}


def fallback(selection, paths, path, graph, *, no_index=False, note=''):
    """Module-level selection for ``path`` (see module docstring)."""
    module = paths.test_module(path)
    if module:
        if module.split('.')[0] in SELECTABLE:
            selection.add(path, 'test file' + note, modules={module})
        return
    product, layer = paths.product_layer(path)
    if product:
        selection.add(path, f'layer {layer or "undeclared"} tests' + note,
                      folders=LAYER_FOLDERS.get(layer, SELECTABLE))
        return
    if path.endswith('.py') and paths.scripts_relative(path) and not paths.is_legacy_test(path):
        selection.add(path, 'importing test modules' + note,
                      modules=importing_test_modules(graph(), paths.module_name(path)))
        return
    if no_index and path.startswith(paths.skill + '/') and not path.endswith('.py'):
        selection.add(path, 'non-code input without an index', folders=SELECTABLE)


def select_with_index(index, current, read_blob, read_text, paths, graph):
    """Selection from a fresh ``index``; ``current`` maps paths to current blob ids (absent: deleted).

    ``read_blob(blob)`` returns a blob's text or None when git no longer has it;
    ``read_text(path)`` returns the current text; ``graph()`` the import graph.
    """
    selection = Selection('index')
    tests = index['tests']
    files = index['files']
    for path in sorted(set(files) | set(current)):
        entry = files.get(path, {})
        old, new = entry.get('blob'), current.get(path)
        if old == new:
            continue
        if paths.test_module(path) or paths.is_legacy_test(path):
            if new is not None:
                fallback(selection, paths, path, graph)
            continue
        if 'readers' in entry:
            if entry['readers']:
                selection.add(path, 'input readers', tests={tests[o] for o in entry['readers']})
            else:
                selection.add(path, 'input opened at import with no test to credit', folders=SELECTABLE)
            continue
        if not path.endswith('.py'):
            continue
        if 'functions' not in entry:
            fallback(selection, paths, path, graph)
            continue
        everything = {tests[o] for ordinals in entry['functions'].values() for o in ordinals}
        old_text = read_blob(old) if new is not None else None
        if old_text is None:
            selection.add(path, 'deleted' if new is None else 'measured text gone', tests=everything)
            fallback(selection, paths, path, graph)
            continue
        new_text = read_text(path)
        for region in region_anchors(old_text, new_text):
            names, outside = region_owners(old_text, new_text, region)
            chosen = {tests[o] for o in tests_of_functions(entry, names)}
            if chosen:
                selection.add(f"{path}:{region['new'][0]}", 'tests that entered the changed functions', tests=chosen)
            if outside:
                fallback(selection, paths, path, graph,
                         note=f" (lines {region['new'][0]}-{region['new'][1]} run at import)")
    return selection


def select_without_index(changed, paths, graph, reason):
    selection = Selection('fallback', reason)
    for path in sorted(changed):
        fallback(selection, paths, path, graph, no_index=True)
    return selection


def _git(root, *arguments, check=True):
    return subprocess.run(['git', *arguments], cwd=root, capture_output=True, text=True, encoding='utf-8',
                          check=check)


def read_index(path=INDEX):
    try:
        index = json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None, 'no selection index'
    except ValueError:
        return None, 'unreadable selection index'
    if index.get('format') != FORMAT:
        return None, f"index format {index.get('format')!r} is not {FORMAT}"
    return index, ''


def usable(index, reason, is_ancestor):
    """(index, '') when the index exists and its commit is HEAD or an ancestor of HEAD, else (None, reason)."""
    if index is not None and not is_ancestor(index['commit']):
        return None, f"index commit {index['commit'][:12]} is not an ancestor of HEAD"
    return index, reason


def is_ancestor_of_head(root):
    return lambda commit: _git(root, 'merge-base', '--is-ancestor', commit, 'HEAD', check=False).returncode == 0


def choose(root, layers, index_path=INDEX):
    """T0's selection in the repository at ``root`` (all paths repository-relative)."""
    paths = Paths(SCRIPTS.relative_to(root).as_posix(), layers)
    cache = {}
    graph = lambda: cache.setdefault('graph', import_graph(SCRIPTS))
    index, reason = usable(*read_index(index_path), is_ancestor_of_head(root))
    if index is None:
        changed = set(_git(root, 'diff', '--name-only', 'HEAD', '--', paths.skill).stdout.split('\n'))
        changed |= set(_git(root, 'ls-files', '--others', '--exclude-standard', '--full-name', '--', paths.skill
                            ).stdout.split('\n'))
        return select_without_index({p for p in changed if p}, paths, graph, reason)
    candidates = scripts_python(root) + sorted(p for p, e in index['files'].items()
                                               if 'readers' in e and (root / p).is_file())
    current = git_blobs(root, candidates)

    def read_blob(blob):
        result = subprocess.run(['git', 'cat-file', 'blob', blob], cwd=root, capture_output=True, check=False)
        return result.stdout.decode('utf-8') if result.returncode == 0 else None

    return select_with_index(index, current, read_blob, lambda p: (root / p).read_text(encoding='utf-8'), paths, graph)
