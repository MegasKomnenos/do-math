"""Layer rules of docs/do-math/시험-재편-2026-09-29/설계.md 2.1 and 3.3, judged by AST.

A product module is every ``.py`` under ``do_math/`` plus the ``.py`` files
beside it, except the test runner files. Each is declared in
``do_math/layers.py`` with a layer (``'1'``, ``'2'``, ``'3'``, ``'adapter'``)
or listed as pending while it cannot yet obey its intended layer.

Checks for a declared module:
* import direction between product modules (layer 1 imports layer 1; an
  adapter imports layer 1 or adapters; layer 2 imports layers 1 and 2; layer 3
  imports anything), counting imports inside functions;
* layers 1 and 2 do not use processes, threads, ambient time, randomness,
  environment or host identity, directly or through a default argument;
* layer 1 additionally does no file-system I/O.
A line ending in ``# layer: <reason>`` is exempt; an empty reason is not.
"""
import ast
from pathlib import Path

LAYERS = ('1', '2', '3', 'adapter')
ALLOWED_IMPORTS = {'1': {'1'}, 'adapter': {'1', 'adapter'}, '2': {'1', '2'}, '3': set(LAYERS)}
NOT_PRODUCT = {'run_tests.py', 'test_categories.py'}
BANNED_MODULES = {'subprocess', 'threading', 'multiprocessing', 'ctypes', 'socket', 'msvcrt', '_winapi',
                  'winreg', 'concurrent', 'secrets'}
BANNED_NAMES = {
    'time.time', 'time.time_ns', 'time.monotonic', 'time.monotonic_ns', 'time.perf_counter', 'time.sleep',
    'datetime.datetime.now', 'datetime.datetime.utcnow', 'datetime.datetime.today', 'datetime.date.today',
    'os.urandom', 'os.environ', 'os.getenv', 'os.system', 'os.popen', 'os.startfile', 'os.getpid',
    'uuid.uuid1', 'uuid.uuid4', 'platform.node',
    'random.random', 'random.randint', 'random.randrange', 'random.choice', 'random.choices',
    'random.shuffle', 'random.sample', 'random.uniform', 'random.getrandbits', 'random.randbytes',
}
FILE_NAMES = {'os.remove', 'os.unlink', 'os.rename', 'os.replace', 'os.makedirs', 'os.mkdir', 'os.rmdir',
              'os.listdir', 'os.scandir', 'os.walk', 'os.stat', 'os.path.exists', 'os.path.isfile',
              'os.path.isdir', 'os.path.getsize', 'os.path.getmtime', 'glob.glob', 'glob.iglob'}
FILE_MODULES = {'shutil', 'tempfile'}
FILE_METHODS = {'read_text', 'write_text', 'read_bytes', 'write_bytes', 'mkdir', 'unlink', 'rmdir', 'touch',
                'iterdir', 'rglob', 'is_file', 'is_dir', 'exists', 'stat', 'open'}


def product_modules(root):
    root = Path(root)
    found = {path.relative_to(root).as_posix() for path in (root / 'do_math').rglob('*.py')
             if '__pycache__' not in path.parts}
    found |= {path.name for path in root.glob('*.py') if path.name not in NOT_PRODUCT}
    return found


def _resolve(module, population):
    """Product module path for a dotted name, or None when it is not a product module."""
    base = module.replace('.', '/')
    for candidate in (base + '.py', base + '/__init__.py'):
        if candidate in population:
            return candidate
    return None


def _imports(tree, path, population):
    package = path.rsplit('/', 1)[0].replace('/', '.') if '/' in path else ''
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, _resolve(alias.name, population)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split('.') if package else []
                parts = parts[:len(parts) - node.level + 1]
                base = '.'.join(parts + ([node.module] if node.module else []))
            else:
                base = node.module or ''
            target = _resolve(base, population)
            for alias in node.names:
                submodule = _resolve(base + '.' + alias.name, population)
                yield node.lineno, submodule or target


def _aliases(tree):
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names[alias.asname or alias.name.split('.')[0]] = alias.asname and alias.name or alias.name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            for alias in node.names:
                names[alias.asname or alias.name] = node.module + '.' + alias.name
    return names


def _dotted(node, aliases):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name) or node.id not in aliases:
        return None
    return '.'.join([aliases[node.id], *reversed(parts)])


def _effects(tree, layer):
    aliases = _aliases(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in BANNED_MODULES or (layer == '1' and alias.name.split('.')[0] in FILE_MODULES):
                    yield node.lineno, 'import ' + alias.name
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            head = node.module.split('.')[0]
            if head in BANNED_MODULES or (layer == '1' and head in FILE_MODULES):
                yield node.lineno, 'from ' + node.module
        elif isinstance(node, (ast.Attribute, ast.Name)) and isinstance(node.ctx, ast.Load):
            name = _dotted(node, aliases) if isinstance(node, ast.Attribute) else aliases.get(node.id)
            if name in BANNED_NAMES or (layer == '1' and name in FILE_NAMES):
                yield node.lineno, name
        if layer == '1' and isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'open':
                yield node.lineno, 'open()'
            elif isinstance(node.func, ast.Attribute) and node.func.attr in FILE_METHODS:
                yield node.lineno, '.' + node.func.attr + '()'


def _exempt(line):
    marker = line.find('# layer:')
    return marker >= 0 and line[marker + len('# layer:'):].strip() != ''


def check_tree(root, layers, pending):
    root = Path(root)
    population = product_modules(root)
    issues = []
    for path in sorted(population - layers.keys() - pending.keys()):
        issues.append({'module': path, 'rule': 'undeclared'})
    for path in sorted(layers.keys() - population):
        issues.append({'module': path, 'rule': 'declared_but_absent'})
    for path in sorted(pending.keys() - population):
        issues.append({'module': path, 'rule': 'pending_but_absent'})
    for path in sorted(layers.keys() & pending.keys()):
        issues.append({'module': path, 'rule': 'declared_and_pending'})
    for path, layer in sorted({**layers, **pending}.items()):
        if layer not in LAYERS:
            issues.append({'module': path, 'rule': 'bad_layer', 'detail': layer})
    known = {**pending, **layers}
    for path in sorted(layers.keys() & population - pending.keys()):
        layer = layers[path]
        if layer not in LAYERS:
            continue
        source = (root / path).read_text(encoding='utf-8')
        lines = source.splitlines()
        tree = ast.parse(source)
        exempt = lambda number: 0 < number <= len(lines) and _exempt(lines[number - 1])
        for number, target in _imports(tree, path, population):
            if target and target != path and target in known and known[target] not in ALLOWED_IMPORTS[layer] \
                    and not exempt(number):
                issues.append({'module': path, 'rule': 'import_direction', 'line': number,
                               'detail': f'{layer} imports {target} ({known[target]})'})
        if layer in ('1', '2'):
            for number, detail in _effects(tree, layer):
                if not exempt(number):
                    issues.append({'module': path, 'rule': 'effect', 'line': number, 'detail': detail})
    unique = []
    for issue in issues:
        if issue not in unique:
            unique.append(issue)
    return unique
