"""T3 measurement: branch coverage per test, the branch-reach gate, and the selection index (설계 5.3, 5.5).

``Measurement`` runs coverage.py in branch mode over ``scripts/`` in the runner's
own process. It starts before test discovery so import-time lines count. The
runner calls ``test_started``/``test_stopped`` around every test, and the
measurement switches the coverage context to label each line with the test
that ran it:

* ``<test id>`` while a test (its setUp, body, tearDown) runs;
* ``fixture:<module>[,<module>]`` between two tests, where setUpModule,
  setUpClass and their tear-downs run; it names the module of the test before
  and the test after, and the index credits such lines to every test of those
  modules;
* ``''`` during discovery and imports; the index credits these lines to no test.

A Python audit hook (``sys.addaudithook``, event ``open``) records every file
inside the repository that is not Python source and is opened under a context.
A file opened under the import context is credited to the tests that ran any
line of the innermost measured module on the stack at the open.

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

Index (``build_index``) format ``do-math-selection-index/1``::

    {"format", "commit": HEAD when measured, "created",
     "tests": [test id, ...],                       # ordinals below refer to this list
     "files": {repo-relative path: {"blob": git blob id at measurement,
                                    "lines": {"<line>": [ordinal, ...]},  # measured .py only
                                    "readers": [ordinal, ...]}}}          # non-Python inputs only

Every ``.py`` under ``scripts/`` has an entry (with ``blob``) so that T0 can tell
changed, new and deleted files apart; ``lines`` holds only lines some test or
fixture ran. Selection from the index is in ``selection.py``.
"""
from __future__ import annotations

from collections import defaultdict
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
FORMAT = 'do-math-selection-index/1'
GATED_LAYERS = ('1', '2', '3')
# A coverage exclusion counts only with a reason after the mark (설계 5.5, 6.2).
REASONED_EXCLUSION = r'#\s*pragma: no cover[ \-:]*[^ \-:\s]'
FIXTURE = 'fixture:'
DATA, OPENED = 'coverage.data', 'opened.json'  # a parallel T3 worker's measurement, in its directory


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


def fixture_label(before, after):
    """Context label of the fixture phase between two test ids (either may be None)."""
    modules = sorted({test.rsplit('.', 2)[0] for test in (before, after) if test})
    return FIXTURE + ','.join(modules)


class Measurement:
    """One T3 coverage session in this process; see the module docstring."""

    def __init__(self, root, data_file=None):
        import coverage
        self.root, self.started = root, False
        self.context = ''
        self.order, self.position = [], {}
        self.opens = defaultdict(set)      # context -> repo paths
        self.import_opens = defaultdict(set)  # repo path -> opener module repo paths
        omit = [str(TESTS / 'test_*.py'), str(TESTS / '*' / 'test_*.py'), str(TESTS / '*_fixtures.py'),
                str(SCRIPTS / 'run_tests.py'), str(SCRIPTS / 'test_categories.py'), str(Path(__file__).resolve())]
        self.coverage = coverage.Coverage(data_file=str(data_file) if data_file else None, branch=True, source=[str(SCRIPTS)], omit=omit,
                                          config_file=False)
        self.coverage.set_option('report:exclude_lines', [REASONED_EXCLUSION])
        self.coverage.set_option('report:partial_branches', [])
        self.coverage.set_option('json:show_contexts', True)

    def start(self):
        global _ACTIVE
        _ACTIVE = self
        _install_hook()
        self.coverage.start()
        self.started = True

    def begin(self, order):
        """Tests will run in ``order``; label the first fixture phase."""
        self.order = list(order)
        self.position = {test: index for index, test in enumerate(self.order)}
        self._switch(fixture_label(None, self.order[0] if self.order else None))

    def _switch(self, label):
        self.context = label
        self.coverage.switch_context(label)

    def test_started(self, test_id):
        self._switch(test_id)

    def test_stopped(self, test_id):
        index = self.position.get(test_id)
        after = self.order[index + 1] if index is not None and index + 1 < len(self.order) else None
        self._switch(fixture_label(test_id, after))

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

    def abandon(self):
        """Stop measuring without a report (the run ended before any test ran)."""
        global _ACTIVE
        _ACTIVE = None
        self.coverage.stop()

    def save(self, directory):
        """A worker of a parallel T3: stop measuring; keep the data file and the opened inputs for the parent."""
        global _ACTIVE
        _ACTIVE = None
        self.coverage.stop()
        self.coverage.save()
        opened = {'opens': {context: sorted(paths) for context, paths in self.opens.items()},
                  'import_opens': {path: sorted(openers) for path, openers in self.import_opens.items()}}
        (Path(directory) / OPENED).write_text(json.dumps(opened), encoding='utf-8')

    def merge(self, directories):
        """The parent of a parallel T3: combine the workers' data files and opened inputs into this measurement."""
        self.coverage.combine([str(Path(directory) / DATA) for directory in directories], keep=True)
        for directory in directories:
            opened = json.loads((Path(directory) / OPENED).read_text(encoding='utf-8'))
            for context, paths in opened['opens'].items():
                self.opens[context].update(paths)
            for path, openers in opened['import_opens'].items():
                self.import_opens[path].update(openers)

    def finish(self, directory):
        """Stop measuring; return the coverage JSON with repository-relative file keys."""
        global _ACTIVE
        _ACTIVE = None
        if self.started:
            self.coverage.stop()
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


def _hook(event, arguments):
    global _RECORDING
    if event != 'open' or _ACTIVE is None or _RECORDING or not arguments \
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


def build_index(files, tests, opens, import_opens, blobs, commit, created=None):
    """The selection index from coverage JSON ``files`` (repo-relative keys, with ``contexts``).

    ``tests`` is the ordered list of test ids that ran; ``opens`` maps a context to
    the non-Python paths opened under it; ``import_opens`` maps such a path to the
    measured modules that opened it at import; ``blobs`` maps every tracked
    path (all scripts/ .py and every opened input) to its git blob id.
    """
    ordinal = {test: index for index, test in enumerate(tests)}
    tests_by_module = defaultdict(set)
    for test, index in ordinal.items():
        tests_by_module[test.rsplit('.', 2)[0]].add(index)
    entries = {path: {'blob': blob} for path, blob in blobs.items()}
    for path, value in files.items():
        lines = {}
        for line, contexts in value.get('contexts', {}).items():
            credited = set().union(*(_credited(c, tests_by_module, ordinal) for c in contexts))
            if credited:
                lines[line] = sorted(credited)
        entries.setdefault(path, {})['lines'] = dict(sorted(lines.items(), key=lambda item: int(item[0])))
    readers = defaultdict(set)
    for context, paths in opens.items():
        for path in paths:
            readers[path] |= _credited(context, tests_by_module, ordinal)
    for path, openers in import_opens.items():
        for opener in openers:
            readers[path] |= {o for ordinals in entries.get(opener, {}).get('lines', {}).values() for o in ordinals}
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
    index = build_index(report['files'], tests, measurement.opens, measurement.import_opens, blobs, commit)
    handle, temporary = tempfile.mkstemp(dir=Path(path).parent, prefix='.selection-index-', suffix='.tmp')
    with os.fdopen(handle, 'w', encoding='utf-8') as stream:
        json.dump(index, stream, ensure_ascii=False, separators=(',', ':'))
    os.replace(temporary, path)
    return {'path': str(path), 'commit': commit, 'tests': len(tests),
            'measured_files': sum('lines' in e for e in index['files'].values()),
            'inputs': sum('readers' in e for e in index['files'].values())}
