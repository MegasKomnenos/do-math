"""T3 measurement: branch coverage, the branch-reach gate, and the selection index (설계 5.3, 5.5).

``Measurement`` runs coverage.py in branch mode over ``scripts/`` in the runner's
own process. It starts before test discovery so import-time lines count. The
runner calls ``test_started``/``test_stopped`` around every test. Two records
are kept, one per purpose:

* coverage.py measures branch arcs for the gate. Its context is the test
  *module* (``tests.<folder>.<module>`` of the running test, or the fixture
  label between two tests), not the test, so its data grows with modules and
  never holds a per-test line table;
* a ``sys.monitoring`` recorder (``FunctionRecorder``) keeps, per label, the
  functions (code objects) of ``scripts/`` that were entered. Each code object
  reports once per label, so the recorder costs a few percent. The index
  credits a function to the tests that entered it.

Labels:

* ``<test id>`` while a test (its setUp, body, tearDown) runs;
* ``fixture:<module>[,<module>]`` between two tests, where setUpModule,
  setUpClass and their tear-downs run; it names the module of the test before
  and the test after, and the index credits such functions to every test of
  those modules;
* ``''`` during discovery and imports; nothing is credited.

A Python audit hook (``sys.addaudithook``, event ``open``) records every file
inside the repository that is not Python source and is opened under a context.
A file opened under the import context is credited to the tests that entered
any function of the innermost measured module on the stack at the open, or to
every test of that module when the opener is a test module.

A parallel T3 (``--jobs``) measures in each worker process instead: a worker
starts its own ``Measurement`` before it loads its tests and keeps the data and
the opened inputs (``save``); the parent combines them (``merge``) and judges
the gate and writes the index from the combined data as a one-process run does.

Measured: every ``.py`` under ``scripts/`` except test modules
(``tests/**/test_*.py``), the legacy fixtures (``tests/*_fixtures.py``), the
runner pair (``run_tests.py``, ``test_categories.py``) and this module, whose
code runs inside every test context. ``tests/support`` is measured so that
support changes select the tests that ran them.

Gate (``gate``): every module of ``do_math.layers.LAYERS`` whose layer is '1', '2'
or '3' must have no missing branch arc and no missing line. Adapters are not
judged. ``# pragma: no cover`` excludes a line (and the block it opens) only
when a reason follows it on the same line (``REASONED_EXCLUSION``); an
unreasoned mark excludes nothing, and the structure check fails it besides.

Index (``build_index``) format ``do-math-selection-index/2``::

    {"format", "commit": HEAD when measured, "created",
     "tests": [test id, ...],                       # ordinals below refer to this list
     "files": {repo-relative path: {"blob": git blob id at measurement,
                                    "functions": {"<qualname>": [ordinal, ...]},  # measured .py only
                                    "readers": [ordinal, ...]}}}                  # non-Python inputs only

A function is keyed by its qualified name (``Class.method``,
``outer.<locals>.inner``); a lambda or generator expression is credited to the
function that holds it. Every ``.py`` under ``scripts/`` has an entry (with
``blob``) so that T0 can tell changed, new and deleted files apart;
``functions`` holds only functions some test or fixture entered. Selection
from the index is in ``selection.py``.
"""
from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = SCRIPTS / 'tests'
INDEX = TESTS / '.selection-index.json'
FORMAT = 'do-math-selection-index/2'
GATED_LAYERS = ('1', '2', '3')
# A coverage exclusion counts only with a reason after the mark (설계 5.5, 6.2).
REASONED_EXCLUSION = r'#\s*pragma: no cover[ \-:]*[^ \-:\s]'
FIXTURE = 'fixture:'
DATA, OPENED, ENTERED = 'coverage.data', 'opened.json', 'entered.json'  # a parallel T3 worker's measurement
MONITOR_TOOL = 3  # sys.monitoring tool id; 0 debugger, 1 coverage, 2 profiler and 5 optimizer are taken by convention
# Test state built once per process and restored by many tests (a Sim template, 결함 D2): what its build enters is
# recorded under ``shared:<key>``, and each label that restores it gets the pair [SHARED_USE, key] in its record.
SHARED, SHARED_USE = 'shared:', '<shared>'
# Code objects that are not functions of their own: credited to the function that holds them.
_ANONYMOUS = ('<lambda>', '<genexpr>', '<listcomp>', '<dictcomp>', '<setcomp>')


def function_key(qualname):
    """The qualified name a code object is credited to: its own, or the holding function's for a lambda or genexpr."""
    parts = qualname.split('.')
    while parts and parts[-1] in _ANONYMOUS:
        parts.pop()
        if parts and parts[-1] == '<locals>':
            parts.pop()
    return '.'.join(parts)


def module_label(label):
    """The coverage context of a recorder label: the test module of a test id, else the label itself."""
    return label if not label or label.startswith(FIXTURE) else label.rsplit('.', 2)[0]


class FunctionRecorder:
    """Per label, the code objects under ``prefix`` that started or resumed (``sys.monitoring``).

    Each code location reports once and is then disabled; ``switch`` re-enables
    every location, so a function counts once per label however often it runs.
    ``sys.monitoring.restart_events`` re-enables the locations of every tool, so a
    coverage core that also uses ``sys.monitoring`` (sysmon) would see more events;
    T3's branch measurement runs on the settrace core, where this does not arise.
    """

    def __init__(self, prefix, tool=MONITOR_TOOL):
        self.prefix, self.tool = prefix, tool
        self.current = None
        self.paused = False
        self.entered = defaultdict(set)
        self.users = defaultdict(set)  # shared state key -> labels that restored it

    def _on_event(self, code, offset):
        if self.paused:
            # Neither record nor disable: the same test may still enter this function after the pause.
            return None
        if self.current is not None and code.co_filename.startswith(self.prefix):
            self.current.add(code)
        return sys.monitoring.DISABLE

    def start(self):
        monitoring = sys.monitoring
        monitoring.use_tool_id(self.tool, 'do-math T3')
        for event in (monitoring.events.PY_START, monitoring.events.PY_RESUME):
            monitoring.register_callback(self.tool, event, self._on_event)
        monitoring.set_events(self.tool, monitoring.events.PY_START | monitoring.events.PY_RESUME)

    def switch(self, label):
        self.current = self.entered[label] if label else None
        sys.monitoring.restart_events()

    @contextmanager
    def building(self, key):
        """Record what runs in this block under ``shared:<key>``, then return to the label it interrupted."""
        previous = self.current
        self.current = self.entered[SHARED + key]
        sys.monitoring.restart_events()
        try:
            yield
        finally:
            self.current = previous
            sys.monitoring.restart_events()

    def stop(self):
        monitoring = sys.monitoring
        if monitoring.get_tool(self.tool) is not None:
            monitoring.set_events(self.tool, 0)
            monitoring.free_tool_id(self.tool)
        self.current = None

    def records(self, root):
        """{label: [[repo path, function key], ...]}; test modules and the runner pair, as coverage omits them, are left out."""
        prefix = SCRIPTS.relative_to(root).as_posix()
        skipped = {f'{prefix}/run_tests.py', f'{prefix}/test_categories.py', f'{prefix}/tests/support/branch_gate.py'}
        paths, out = {}, {}
        for label, codes in self.entered.items():
            keys = set()
            for code in codes:
                if code.co_filename not in paths:
                    try:
                        path = Path(code.co_filename).resolve().relative_to(root).as_posix()
                    except ValueError:
                        path = None
                    paths[code.co_filename] = None if path in skipped or (path and _test_module(path, prefix)) else path
                path = paths[code.co_filename]
                if path:
                    keys.add((path, function_key(code.co_qualname)))
            out[label] = sorted([path, key] for path, key in keys if key)
        for key, labels in self.users.items():
            for label in labels:
                out[label] = sorted(out.get(label, []) + [[SHARED_USE, key]])
        return out


def repository_root(start=SCRIPTS):
    return Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=start, capture_output=True,
                               text=True, check=True).stdout.strip()).resolve()


def git_blobs(root, paths):
    """Git blob ids of working-tree files, eol normalization applied, in one ``git hash-object`` call."""
    if not paths:
        return {}
    output = subprocess.run(['git', 'hash-object', '--stdin-paths'], cwd=root, input='\n'.join(paths) + '\n',
                            capture_output=True, text=True, check=True).stdout.split()
    return dict(zip(paths, output))


def scripts_python(root):
    """Repository-relative paths of every .py under scripts/."""
    return sorted(path.relative_to(root).as_posix() for path in SCRIPTS.rglob('*.py')
                  if '__pycache__' not in path.parts)


def process_caches(prefix):
    """The ``functools`` caches (``cache``, ``lru_cache``) alive in this process whose function lies under ``prefix``.

    A cached body runs in the first test that calls it and never again in the
    process, so the recorder would credit it, and what it calls, to that test
    alone (결함 D2). The measurement clears these before every test. Caches made
    after ``begin`` (a function decorated inside another) and ``cached_property``
    values (held per instance) are not cleared.
    """
    import functools
    import gc
    wrapper = type(functools.lru_cache()(lambda: None))
    return [item for item in gc.get_objects() if isinstance(item, wrapper)
            and getattr(getattr(item, '__wrapped__', None), '__code__', None) is not None
            and item.__wrapped__.__code__.co_filename.startswith(prefix)]


def fixture_label(before, after):
    """Context label of the fixture phase between two test ids (either may be None)."""
    modules = sorted({test.rsplit('.', 2)[0] for test in (before, after) if test})
    return FIXTURE + ','.join(modules)


class Measurement:
    """One T3 coverage session in this process; see the module docstring."""

    def __init__(self, root, data_file=None):
        import coverage
        self.root, self.started = root, False
        self.data_file = Path(data_file) if data_file else None
        self.context = ''
        self.order, self.position, self.caches = [], {}, []
        self.opens = defaultdict(set)      # context -> repo paths
        self.import_opens = defaultdict(set)  # repo path -> opener module repo paths
        omit = [str(TESTS / 'test_*.py'), str(TESTS / '*' / 'test_*.py'), str(TESTS / '*_fixtures.py'),
                str(SCRIPTS / 'run_tests.py'), str(SCRIPTS / 'test_categories.py'), str(Path(__file__).resolve())]
        self.coverage = coverage.Coverage(data_file=str(data_file) if data_file else None, branch=True, source=[str(SCRIPTS)], omit=omit,
                                          config_file=False)
        self.coverage.set_option('report:exclude_lines', [REASONED_EXCLUSION])
        self.coverage.set_option('report:partial_branches', [])
        self.coverage_context = ''
        self.calls = FunctionRecorder(str(SCRIPTS) + os.sep)

    def start(self):
        global _ACTIVE
        _ACTIVE = self
        _install_hook()
        self.coverage.start()
        self.calls.start()
        self.started = True

    def begin(self, order):
        """Tests will run in ``order``; find the process caches to clear; label the first fixture phase."""
        self.order = list(order)
        self.position = {test: index for index, test in enumerate(self.order)}
        self.caches = process_caches(self.calls.prefix)
        self._switch(fixture_label(None, self.order[0] if self.order else None))

    def _switch(self, label):
        self.context = label
        self.calls.switch(label)
        context = module_label(label)
        if context != self.coverage_context:
            self.coverage_context = context
            self.coverage.switch_context(context)

    def test_started(self, test_id):
        for cache in self.caches:  # 결함 D2: each test recomputes what a process cache held, so it enters it
            cache.cache_clear()
        self._switch(test_id)

    def module_started(self, module):
        """A test module's own suite begins: its setUpModule and setUpClass run under its fixture label."""
        self._switch(FIXTURE + module)

    def test_stopped(self, test_id):
        """Until the next test, fixtures are those of this test's module: the runner gives each module its own
        suite, so a module's tear-downs run before the next module starts (A29: a module's measurement is its own)."""
        self._switch(FIXTURE + test_id.rsplit('.', 2)[0])

    def record_open(self, path):
        try:
            resolved = Path(os.fsdecode(path)).resolve()
            relative = resolved.relative_to(self.root).as_posix()
        except (TypeError, ValueError, OSError):
            return
        if resolved.suffix in ('.py', '.pyc') or relative.startswith('.git/') or '__pycache__' in resolved.parts:
            return
        if self.context:
            self.opens[self.context].add(relative)
            return
        frame = sys._getframe(2)  # record_open <- _hook <- the Python caller of the audited open
        while frame is not None:
            opener = Path(frame.f_code.co_filename)
            if opener.suffix == '.py' and SCRIPTS in opener.parents:
                self.import_opens[relative].add(opener.resolve().relative_to(self.root).as_posix())
                return
            frame = frame.f_back

    def _stop(self):
        global _ACTIVE
        _ACTIVE = None
        if self.started:
            self.calls.stop()
            self.coverage.stop()

    def abandon(self):
        """Stop measuring without a report (the run ended before any test ran)."""
        self._stop()

    def save(self, directory):
        """A worker of a parallel T3: stop measuring; keep the data file, the entered functions and the opened inputs."""
        self._stop()
        self.coverage.save()
        opened = {'opens': {context: sorted(paths) for context, paths in self.opens.items()},
                  'import_opens': {path: sorted(openers) for path, openers in self.import_opens.items()}}
        (Path(directory) / OPENED).write_text(json.dumps(opened), encoding='utf-8')
        (Path(directory) / ENTERED).write_text(json.dumps(self.calls.records(self.root)), encoding='utf-8')

    def merge(self, directories):
        """The parent of a parallel T3: combine the workers' data files and records into this measurement.

        A worker that ended before ``save`` (a timeout) left nothing; it is skipped
        and returned (결함 D6), so the run still reports. Its tests are then unmeasured:
        the gate sees more gaps, and the run is incomplete, so no index is written.
        """
        saved = [Path(directory) for directory in directories
                 if all((Path(directory) / name).is_file() for name in (DATA, OPENED, ENTERED))]
        missing = [Path(directory) for directory in directories if Path(directory) not in saved]
        if saved:
            self.coverage.combine([str(directory / DATA) for directory in saved], keep=True)
        self.merged_entered = defaultdict(set)
        for directory in saved:
            opened = json.loads((Path(directory) / OPENED).read_text(encoding='utf-8'))
            for context, paths in opened['opens'].items():
                self.opens[context].update(paths)
            for path, openers in opened['import_opens'].items():
                self.import_opens[path].update(openers)
            for label, keys in json.loads((Path(directory) / ENTERED).read_text(encoding='utf-8')).items():
                self.merged_entered[label].update(tuple(key) for key in keys)
        return missing

    def entered(self):
        """{label: [[repo path, function key], ...]} of this process or of the merged workers."""
        merged = getattr(self, 'merged_entered', None)
        if merged is not None:
            return {label: sorted(list(key) for key in keys) for label, keys in merged.items()}
        return self.calls.records(self.root)

    def absorb(self, entered, opens):
        """Join stored records (a T3 store's reused modules, A29) to this run's entered functions and opened inputs."""
        merged = defaultdict(set)
        for records in (self.entered(), entered):
            for label, keys in records.items():
                merged[label].update(tuple(key) for key in keys)
        self.merged_entered = merged
        for label, paths in opens.items():
            self.opens[label].update(paths)

    def finish(self, directory, before_report=None):
        """Stop measuring; keep the entered functions (``entered.json``); return the coverage JSON with repo-relative keys.

        ``before_report(self)`` runs after measuring stops and before the report:
        an incremental T3 joins its reused measurement there.
        """
        self._stop()
        if before_report is not None:
            before_report(self)
        (Path(directory) / ENTERED).write_text(json.dumps(self.entered()), encoding='utf-8')
        path = Path(directory) / 'coverage.json'
        self.coverage.json_report(outfile=str(path))
        report = json.loads(path.read_text(encoding='utf-8'))
        report['files'] = {(Path.cwd() / name).resolve().relative_to(self.root).as_posix(): value
                           for name, value in report['files'].items()}
        path.write_text(json.dumps(report), encoding='utf-8')
        return report


_ACTIVE = None
_HOOKED = False


_RECORDING = False


@contextmanager
def unmeasured():
    """Runner bookkeeping (결함 D5): code and files the runner itself touches count as no test's reach or input.

    The runner writes its result and progress files through ``do_math.file_io``,
    between tests and inside test contexts; measured, those lines would pass the
    gate with no test having run them, and the index would credit them to the
    running test. Inside this block the coverage tracer, the function recorder
    and the open recorder stand still; the coverage context is restored after.
    """
    global _PAUSED
    active = _ACTIVE
    if active is None or not active.started or _PAUSED:
        yield
        return
    _PAUSED = True
    active.coverage.stop()
    active.calls.paused = True
    try:
        yield
    finally:
        active.calls.paused = False
        active.coverage.start()
        if active.coverage_context:
            active.coverage.switch_context(active.coverage_context)
        _PAUSED = False


_PAUSED = False


@contextmanager
def shared_state(key):
    """Build test state that many tests restore (a Sim template) inside this block (결함 D2).

    The build runs once per process, in whichever test or fixture asks first, so
    what it enters would be credited to that one. Recorded under ``shared:<key>``,
    it is credited to every label that ``used_state(key)`` names. Outside a T3
    measurement this does nothing.
    """
    active = _ACTIVE
    if active is None or _PAUSED:
        yield
        return
    with active.calls.building(key):
        yield


def used_state(key):
    """The running test or fixture restores the shared state ``key``; see ``shared_state``."""
    active = _ACTIVE
    if active is not None and active.context:
        active.calls.users[key].add(active.context)


def _hook(event, arguments):
    global _RECORDING
    if event != 'open' or _ACTIVE is None or _RECORDING or _PAUSED or not arguments \
            or not isinstance(arguments[0], (str, bytes, os.PathLike)):
        return
    _RECORDING = True  # path resolution must not re-enter the hook
    try:
        _ACTIVE.record_open(arguments[0])
    finally:
        _RECORDING = False


def _install_hook():
    global _HOOKED
    if not _HOOKED:  # an audit hook cannot be removed; one per process suffices
        sys.addaudithook(_hook)
        _HOOKED = True


def gate(files, layers, scripts_prefix):
    """Branch-reach gate over coverage JSON ``files`` (repo-relative keys) for the gated layers.

    ``layers`` maps scripts-relative module paths to layers (``do_math.layers.LAYERS``);
    ``scripts_prefix`` is the repo-relative path of ``scripts/``. A judged module
    absent from ``files`` was never measured and fails with every line unknown.
    """
    modules, excluded = {}, 0
    judged = sorted(module for module, layer in layers.items() if layer in GATED_LAYERS)
    for module in judged:
        entry = files.get(f'{scripts_prefix}/{module}')
        if entry is None:
            modules[module] = {'layer': layers[module], 'unmeasured': True, 'missing_branches': [], 'missing_lines': []}
            continue
        excluded += len(entry.get('excluded_lines', []))
        branches, lines = entry.get('missing_branches', []), entry.get('missing_lines', [])
        if branches or lines:
            modules[module] = {'layer': layers[module], 'missing_branches': branches, 'missing_lines': lines}
    return {'passed': not modules, 'judged_modules': len(judged), 'modules_with_gaps': len(modules),
            'missing_branches': sum(len(m['missing_branches']) for m in modules.values()),
            'missing_lines': sum(len(m['missing_lines']) for m in modules.values()),
            'unmeasured_modules': sorted(m for m, value in modules.items() if value.get('unmeasured')),
            'excluded_lines': excluded, 'modules': modules}


def gate_summary(result):
    """One line for the head of the run output."""
    return (f"Branch gate {'passed' if result['passed'] else 'FAILED'}: {result['modules_with_gaps']} of "
            f"{result['judged_modules']} layer 1-3 modules have gaps; {result['missing_branches']} missing branch arcs, "
            f"{result['missing_lines']} missing lines, {result['excluded_lines']} excluded lines"
            + (f"; never measured: {', '.join(result['unmeasured_modules'])}" if result['unmeasured_modules'] else ''))


def _credited(context, tests_by_module, ordinal):
    """Test ordinals a context stands for: the test itself, every test of a fixture's modules, or none."""
    if context.startswith(FIXTURE):
        return {o for module in context[len(FIXTURE):].split(',') if module for o in tests_by_module.get(module, ())}
    return {ordinal[context]} if context in ordinal else set()


def _test_module(path, scripts_prefix):
    """``folder.test_x`` when ``path`` (repo-relative) is a tier-folder test module, else None."""
    parts = path[len(scripts_prefix) + 1:].split('/') if path.startswith(scripts_prefix + '/') else []
    if len(parts) == 3 and parts[0] == 'tests' and parts[2].startswith('test_') and parts[2].endswith('.py'):
        return parts[1] + '.' + parts[2][:-3]
    return None


def build_index(entered, tests, opens, import_opens, blobs, commit, created=None, scripts_prefix=None):
    """The selection index from the recorder's ``entered`` ({label: [[repo path, function key], ...]}).

    ``tests`` is the ordered list of test ids that ran; ``opens`` maps a context to
    the non-Python paths opened under it; ``import_opens`` maps such a path to the
    modules that opened it at import; ``blobs`` maps every tracked path (all
    scripts/ .py and every opened input) to its git blob id. Every measured .py
    under ``scripts/`` gets ``functions``, empty when no test entered one.
    """
    scripts_prefix = scripts_prefix or SCRIPTS.relative_to(repository_root()).as_posix()
    ordinal = {test: index for index, test in enumerate(tests)}
    tests_by_module = defaultdict(set)
    for test, index in ordinal.items():
        tests_by_module[test.rsplit('.', 2)[0]].add(index)
    entries = {path: {'blob': blob} for path, blob in blobs.items()}
    functions = defaultdict(lambda: defaultdict(set))
    users = defaultdict(set)  # shared state key -> labels that restored it
    for label, keys in entered.items():
        users_of = [key for path, key in keys if path == SHARED_USE]
        for key in users_of:
            users[key].add(label)
    for label, keys in entered.items():
        if label.startswith(SHARED):  # a shared build: credited to every label that restored it
            credited = set().union(*(_credited(user, tests_by_module, ordinal) for user in users[label[len(SHARED):]]))
        else:
            credited = _credited(label, tests_by_module, ordinal)
        if credited:
            for path, key in keys:
                if path != SHARED_USE:
                    functions[path][key] |= credited
    for path, entry in entries.items():
        if path.endswith('.py') and path.startswith(scripts_prefix + '/') and not _test_module(path, scripts_prefix):
            entry['functions'] = {key: sorted(o) for key, o in sorted(functions.get(path, {}).items())}
    readers = defaultdict(set)
    for context, paths in opens.items():
        for path in paths:
            readers[path] |= _credited(context, tests_by_module, ordinal)
    for path, openers in import_opens.items():
        for opener in openers:
            module = _test_module(opener, scripts_prefix)
            readers[path] |= tests_by_module.get(module, set()) if module else {
                o for ordinals in functions.get(opener, {}).values() for o in ordinals}
    for path, credited in readers.items():
        if path in entries:  # an opened path without a blob no longer exists or is untracked scratch
            entries[path]['readers'] = sorted(credited)
    return {'format': FORMAT, 'commit': commit,
            'created': created or datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'tests': list(tests), 'files': dict(sorted(entries.items()))}


def write_index(measurement, report, tests, path=INDEX):
    """Build the index from a finished measurement and replace ``path``; returns its summary."""
    root = measurement.root
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True,
                            check=True).stdout.strip()
    inputs = {p for paths in measurement.opens.values() for p in paths} | set(measurement.import_opens)
    candidates = scripts_python(root) + sorted(p for p in inputs if (root / p).is_file())
    blobs = git_blobs(root, candidates)
    index = build_index(measurement.entered(), tests, measurement.opens, measurement.import_opens, blobs, commit,
                        scripts_prefix=SCRIPTS.relative_to(root).as_posix())
    handle, temporary = tempfile.mkstemp(dir=Path(path).parent, prefix='.selection-index-', suffix='.tmp')
    with os.fdopen(handle, 'w', encoding='utf-8') as stream:
        json.dump(index, stream, ensure_ascii=False, separators=(',', ':'))
    os.replace(temporary, path)
    return {'path': str(path), 'commit': commit, 'tests': len(tests),
            'measured_files': sum(bool(e.get('functions')) for e in index['files'].values()),
            'inputs': sum('readers' in e for e in index['files'].values())}
