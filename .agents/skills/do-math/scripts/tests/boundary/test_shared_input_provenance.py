"""Real two-module shared producer/open/consumer regression; all runs use disposable files and processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_categories import test_group

SCRIPTS = Path(__file__).resolve().parents[2]

PRODUCER = '''
from pathlib import Path
from support.branch_gate import shared_state, used_state, unmeasured

INPUT = Path(__file__).resolve().parents[1] / 'input.txt'
UNUSED = INPUT.with_name('unused.txt')
EVENTS = []
VALUES = {}
NESTED = {nested}


def read_input():
    EVENTS.append('read')
    return INPUT.read_text(encoding='utf-8')


def leaf():
    if 'leaf' not in VALUES:
        with shared_state('leaf'):
            VALUES['leaf'] = read_input()
    used_state('leaf')
    return VALUES['leaf']


def warm():
    if 'outer' not in VALUES:
        with shared_state('outer'):
            VALUES['outer'] = leaf() if NESTED else read_input()
        # Building another, unconsumed template does not make its inputs outer's.
        with shared_state('unused-outer'):
            with shared_state('unused-leaf'):
                UNUSED.read_text(encoding='utf-8')
            used_state('unused-leaf')


def consume():
    warm()
    used_state('outer')
    return VALUES['outer']


def paused_consume():
    with unmeasured():
        consume()
'''

MODULE = '''
import unittest
import producer

setUpModule = producer.warm


class Case(unittest.TestCase):
    def test_consume(self):
        self.assertEqual(producer.consume(), 'observed input')
        self.assertEqual(producer.EVENTS, ['read'])
'''

PASSIVE = '''
    def test_passive(self):
        # Runner bookkeeping must not acquire a shared dependency while paused.
        producer.paused_consume()
        self.assertEqual(2 + 2, 4)
'''

PROBE = r'''
import importlib.util
import json
from pathlib import Path
import sys
import unittest

real_scripts, root, mode, order = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path[:0] = [str(real_scripts), str(real_scripts / 'tests')]
import run_tests
from support import branch_gate as bg, t3_store as ts, selection
import coverage

scripts = root / 'scripts'
bg.SCRIPTS, bg.TESTS = scripts, scripts / 'tests'
sys.path.insert(0, str(scripts))
worker = root / 'worker'
worker.mkdir()
measurement = bg.Measurement(root, data_file=worker / bg.DATA) if mode == 'measured' else None
if measurement:
    measurement.start()
modules = {}
try:
    for letter in 'ab':
        name = 'unit.test_input_' + letter
        spec = importlib.util.spec_from_file_location(name, scripts / 'tests' / 'unit' / ('test_input_' + letter + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        modules[letter] = module
    tests = [test for letter in order
             for test in run_tests.flatten(unittest.defaultTestLoader.loadTestsFromModule(modules[letter]))]
    ids = [test.id() for test in tests]
    if measurement:
        measurement.begin(ids)
    result = run_tests._run_suite(tests, root / 'run', measurement=measurement)
finally:
    if measurement:
        measurement.save(worker)
assert result['successful'], result
import producer
assert producer.EVENTS == ['read'], producer.EVENTS
outcomes = {row['id']: row['outcome'] for row in result['rows']}

if measurement:
    consumers = {'unit.test_input_a.Case.test_consume', 'unit.test_input_b.Case.test_consume'}
    first = 'unit.test_input_' + order[0]
    first_fixture = bg.FIXTURE + first
    input_path = 'input.txt'
    expected = consumers | {test for test in ids if test.rsplit('.', 2)[0] == first}
    # This existing entry point works on the baseline too: its first failure
    # must be the missing later-module reader, before using any new API.
    index_path = root / '.selection-index.json'
    bg.write_index(measurement, {}, ids, path=index_path)
    index = json.loads(index_path.read_text(encoding='utf-8'))
    assert {ids[o] for o in index['files'][input_path]['readers']} == expected, index
    dependencies = measurement.input_dependencies()
    assert dependencies == {test: [input_path] for test in consumers}, dependencies
    assert measurement.shared_inputs['shared:' + ('leaf' if producer.NESTED else 'outer')] == {input_path}
    assert measurement.calls.users['outer'] == consumers
    if producer.NESTED:
        assert measurement.calls.users['leaf'] == {'shared:outer'}
    assert measurement.calls.users['unused-leaf'] == {'shared:unused-outer'}
    assert measurement.opens[first_fixture] == {'input.txt', 'unused.txt'}, dict(measurement.opens)
    assert all(input_path not in paths for label, paths in measurement.opens.items() if label != first_fixture)
    assert not measurement.producers
    entered = measurement.entered()
    assert ['scripts/producer.py', 'read_input'] in entered['shared:' + ('leaf' if producer.NESTED else 'outer')]
    assert all(['scripts/producer.py', 'read_input'] not in entered.get(test, []) for test in ids)
    data = measurement.coverage.get_data()
    producer_file = str(scripts / 'producer.py')
    read_line = next(i for i, line in enumerate((scripts / 'producer.py').read_text().splitlines(), 1)
                     if "return INPUT.read_text" in line)
    assert set(data.contexts_by_lineno(producer_file)[read_line]) == {first_fixture}
    arcs = {path: sorted(data.arcs(path) or []) for path in data.measured_files()}

    merged = bg.Measurement(root, data_file=root / 'merged.data')
    assert merged.merge([worker]) == []
    assert merged.input_dependencies() == dependencies
    assert merged.opens == measurement.opens
    assert merged.entered() == entered
    assert {path: sorted(merged.coverage.get_data().arcs(path) or [])
            for path in merged.coverage.get_data().measured_files()} == arcs
    exported = json.loads((worker / bg.OPENED).read_text())
    assert exported['input_dependencies'] == dependencies
    assert exported['opens'] == measurement.opened()['opens']

    current = ts.Tree(root)
    paths = bg.scripts_python(root) + ['input.txt', 'unused.txt']
    blobs = current.blobs(paths)
    # A literal fixture open is still credited under the existing fixture rule.
    assert {ids[o] for o in index['files']['unused.txt']['readers']} == {
        test for test in ids if test.rsplit('.', 2)[0] == first}
    assert {ids[o] for o in index['files']['scripts/producer.py']['functions']['read_input']} == consumers
    whole = {module.__name__: [test for test in ids if test.rsplit('.', 2)[0] == module.__name__]
             for module in modules.values()}
    snapshots = ts.module_records(whole, entered, measurement.opens, current, 'scripts',
                                  input_dependencies=dependencies)
    assert all(row['inputs'][input_path] == blobs[input_path] for row in snapshots.values())
    assert all('read_input' in row['functions']['scripts/producer.py'] for row in snapshots.values())
    record = ts.records(root, scripts, snapshots, entered, measurement.opens, measurement.import_opens,
                        current, coverage.__version__, input_dependencies=dependencies)
    store = root / 'store'
    ts.write(store, worker / bg.DATA, record)
    stored = ts.read(store)
    assert stored['input_dependencies'] == dependencies
    universe = set(whole)
    unchanged = ts.plan(stored, universe, universe, ts.Tree(root), 'scripts',
                        coverage_version=coverage.__version__)
    assert unchanged.reuse == universe and not unchanged.measure

    # Dropping the builder's module must not drop a retained consumer's input dependency.
    later = 'unit.test_input_' + order[1]
    kept = {later}
    reused = bg.Measurement(root)
    reused.absorb(*ts.stored_entries(stored, kept))
    kept_dependencies = {test: paths for test, paths in dependencies.items()
                         if test.rsplit('.', 2)[0] == later}
    assert reused.input_dependencies() == kept_dependencies
    retained = ts.records(root, scripts, {}, {}, {}, {}, ts.Tree(root), coverage.__version__,
                          stored=stored, keep=kept, input_dependencies={})
    assert retained['input_dependencies'] == kept_dependencies
    kept_index = bg.build_index(reused.entered(), whole[later], reused.opens, {}, blobs, index['commit'],
                               scripts_prefix='scripts', input_dependencies=reused.input_dependencies())
    assert {whole[later][o] for o in kept_index['files'][input_path]['readers']} == {
        test for test in consumers if test.rsplit('.', 2)[0] == later}
    # Coverage retention remains the actual module-context subset; no shared arcs are copied.
    target = ts.reused_data(store, kept, root / 'kept.data')
    kept_data = coverage.CoverageData(basename=str(target))
    kept_data.read()
    assert kept_data.measured_contexts() <= ts.module_contexts(kept)
    assert read_line not in (kept_data.lines(producer_file) or [])

    for missing in (False, True):
        if missing:
            (root / input_path).unlink()
        else:
            (root / input_path).write_text('changed real input', encoding='utf-8')
        changed = ts.Tree(root)
        planned = ts.plan(stored, universe, universe, changed, 'scripts', coverage_version=coverage.__version__)
        assert planned.measure == universe and not planned.reuse, planned.report()
        selected = selection.select_with_index(index, changed.blobs(paths), lambda blob: None, changed.source,
                                               selection.Paths('scripts', {}), lambda: {})
        assert selected.tests == expected, selected.tests
    # The baseline limitation can also be observed through the current API by
    # deliberately asking for literal-only selection; this is not a stored index.
    literal = bg.build_index(entered, ids, measurement.opens, measurement.import_opens, blobs, index['commit'],
                            scripts_prefix='scripts', input_dependencies={})
    assert {ids[o] for o in literal['files'][input_path]['readers']} == {
        test for test in ids if test.rsplit('.', 2)[0] == first}

(root / 'proof.json').write_text(json.dumps({'outcomes': outcomes, 'reads': producer.EVENTS}), encoding='utf-8')
'''


def make_fixture(root, *, nested=True, producer=None, modules=None, inputs=None):
    """The same disposable Git fixture serves the original and adversarial proofs."""
    scripts = root / 'scripts'
    tests = scripts / 'tests' / 'unit'
    tests.mkdir(parents=True)
    for name, value in (inputs or {'input.txt': 'observed input', 'unused.txt': 'unconsumed input'}).items():
        (root / name).write_text(value, encoding='utf-8')
    (scripts / 'producer.py').write_text(
        producer if producer is not None else PRODUCER.replace('{nested}', repr(nested)), encoding='utf-8')
    for letter, source in (modules or {'a': MODULE, 'b': MODULE + PASSIVE}).items():
        (tests / ('test_input_' + letter + '.py')).write_text(source, encoding='utf-8')
    subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Provenance fixture',
                    '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                    'commit', '--quiet', '-m', 'Shared input fixture'], check=True, capture_output=True)


# These helpers execute only inside disposable child processes. Snapshots are
# observations, never fed back into Measurement, the index, or the store.
SNAPSHOT = r'''
import json
import os
from pathlib import Path
import sys

real_scripts, root, directory = map(Path, sys.argv[1:4])
sys.path[:0] = [str(real_scripts), str(real_scripts / 'tests')]
import run_tests
from support import branch_gate as bg, t3_store as ts
import coverage

scripts = root / 'scripts'
bg.SCRIPTS, bg.TESTS = scripts, scripts / 'tests'
run_tests.SCRIPTS = scripts
sys.path.insert(0, str(scripts))


def cover(data):
    data.set_query_contexts(None)
    files = sorted(data.measured_files())
    contexts = {}
    for context in sorted(data.measured_contexts()):
        data.set_query_context(context)
        rows = {}
        for path in files:
            lines, arcs = sorted(data.lines(path) or []), sorted(data.arcs(path) or [])
            if lines or arcs:
                rows[Path(path).relative_to(root).as_posix()] = {
                    'lines': lines, 'arcs': [list(arc) for arc in arcs]}
        contexts[context] = rows
    data.set_query_contexts(None)
    return {'files': sorted(Path(path).relative_to(root).as_posix() for path in files),
            'contexts': contexts}


def snapshot(measurement):
    return {'entered': measurement.entered(),
            'opens': {label: sorted(paths) for label, paths in measurement.opens.items()},
            'import_opens': {path: sorted(openers) for path, openers in measurement.import_opens.items()},
            'coverage': cover(measurement.coverage.get_data())}
'''

WORKER = SNAPSHOT + r'''
import importlib.util
import unittest

mode, order, input_name = sys.argv[4:7]
directory.mkdir()
# This selects an actual input file. Both workers import identical producer code
# and use the same shared keys; neither worker receives fabricated record data.
os.environ['PROVENANCE_INPUT'] = input_name
measurement = bg.Measurement(root, data_file=directory / bg.DATA) if mode != 'ordinary' else None
if measurement:
    measurement.start()
try:
    modules = {}
    for letter in order:
        name = 'unit.test_input_' + letter
        spec = importlib.util.spec_from_file_location(
            name, scripts / 'tests' / 'unit' / ('test_input_' + letter + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        modules[letter] = module
    tests = [test for letter in order
             for test in run_tests.flatten(unittest.defaultTestLoader.loadTestsFromModule(modules[letter]))]
    ids = [test.id() for test in tests]
    if measurement:
        measurement.begin(ids)
    result = run_tests._run_suite(tests, directory / 'run', measurement=measurement)
finally:
    if measurement:
        measurement.save(directory)
assert result['complete'] and result['successful'], result
assert result['tests_run'] == len(ids), result
assert {row['id'] for row in result['rows']} == set(ids), result
assert all(row['outcome'] == 'passed' for row in result['rows']), result
producer = sys.modules.get('producer')
proof = {'ids': ids, 'outcomes': {row['id']: row['outcome'] for row in result['rows']},
         'reads': list(getattr(producer, 'EVENTS', [])),
         'extra_reads': list(getattr(producer, 'EXTRA_READS', []))}
out = {'pid': os.getpid(), 'ordinary': proof, 'rows': result['rows']}
if measurement:
    out.update(snapshot(measurement))
    # The baseline capture uses only the old common APIs above. It neither
    # requests nor reconstructs the new dependency relation.
    if mode == 'measured':
        out['dependencies'] = measurement.input_dependencies()
        out['shared_inputs'] = {label: sorted(paths) for label, paths in measurement.shared_inputs.items()}
        bg.write_index(measurement, {}, ids, path=directory / 'index.json')
        out['index'] = json.loads((directory / 'index.json').read_text(encoding='utf-8'))
(directory / 'snapshot.json').write_text(json.dumps(out), encoding='utf-8')
'''

# Use the runner's normal storable_modules -> module_records -> records -> write
# path. Coverage retention/absorb mirrors _finish_t3 before that writer.
STORE = SNAPSHOT + r'''
action = sys.argv[4]
workers = [Path(path) for path in sys.argv[5:]]
directory.mkdir()
measured = bg.Measurement(root, data_file=directory / bg.DATA)
missing = measured.merge(workers)
assert missing == [], missing
observations = [json.loads((worker / 'snapshot.json').read_text(encoding='utf-8')) for worker in workers]
fresh = snapshot(measured)
fresh['dependencies'] = measured.input_dependencies()
old = ts.read(root / 'store') if action == 'replace' else {}
chosen = {module: row['tests'] for module, row in old.get('modules', {}).items()}
fresh_ids = [test for observation in observations for test in observation['ordinary']['ids']]
for module in {test.rsplit('.', 2)[0] for test in fresh_ids}:
    chosen[module] = sorted(test for test in fresh_ids if test.rsplit('.', 2)[0] == module)
current = ts.Tree(root)
plan = ts.plan(old, set(chosen), set(chosen), current, 'scripts', coverage_version=coverage.__version__)
if action == 'replace':
    assert plan.measure == {'unit.test_input_b'} and plan.reuse == {'unit.test_input_a'}, plan.report()
    retained_path = ts.reused_data(root / 'store', plan.reuse, directory / 'reused.data')
    retained = coverage.CoverageData(basename=str(retained_path))
    retained.read()
    measured.coverage.get_data().update(retained)
    measured.absorb(*ts.stored_entries(old, plan.reuse))
else:
    assert plan.measure == set(chosen) and not plan.reuse, plan.report()
measured.coverage.save()
store = {'plan': plan, 'records': old, 'root': root, 'tree': current, 'chosen': chosen,
         'partial': set(), 'coverage_version': coverage.__version__, 'path': root / 'store'}
rows = [row for observation in observations for row in observation['rows']]
run_tests._write_t3_store(measured, store, directory, rows)
stored = ts.read(root / 'store')
data = coverage.CoverageData(basename=str(root / 'store' / ts.DATA))
data.read()
assert cover(data) == cover(measured.coverage.get_data())
ids = [test for module in sorted(chosen) for test in chosen[module]]
bg.write_index(measured, {}, ids, path=directory / 'index.json')
out = snapshot(measured)
out.update(dependencies=measured.input_dependencies(), fresh=fresh, stored=stored,
           plan=plan.report(), index=json.loads((directory / 'index.json').read_text(encoding='utf-8')))
# Also check a fresh absorb of the normal store, without producer input tables.
restored = bg.Measurement(root)
restored.absorb(*ts.stored_entries(stored, set(chosen)))
assert restored.input_dependencies() == measured.input_dependencies()
assert restored.entered() == measured.entered()
assert dict(restored.opens) == dict(measured.opens)
if action == 'collision':
    (root / 'input-b.txt').write_text('changed worker b input', encoding='utf-8')
    changed = ts.plan(stored, set(chosen), set(chosen), ts.Tree(root), 'scripts',
                      coverage_version=coverage.__version__)
    assert changed.measure == {'unit.test_input_b'} and changed.reuse == {'unit.test_input_a'}, changed.report()
    out['changed_plan'] = changed.report()
if action == 'replace':
    (root / 'input.txt').write_text('changed actual input', encoding='utf-8')
    changed = ts.plan(stored, set(chosen), set(chosen), ts.Tree(root), 'scripts',
                      coverage_version=coverage.__version__)
    assert changed.measure == {'unit.test_input_a'} and changed.reuse == {'unit.test_input_b'}, changed.report()
    out['changed_plan'] = changed.report()
(directory / 'snapshot.json').write_text(json.dumps(out), encoding='utf-8')
'''

IMPORT_PRODUCER = PRODUCER.replace('{nested}', 'True') + r'''
EXTRA_READS = []


def read_named(name):
    value = INPUT.with_name(name).read_text(encoding='utf-8')
    EXTRA_READS.append([name, value])
    return value


def prime_import():
    with shared_state('import-leaf'):
        VALUES['import-leaf'] = read_named('import.txt')
    with shared_state('import-unused'):
        VALUES['import-unused'] = read_named('import-unused.txt')


def restore(key):
    used_state(key)
    return VALUES[key]


def prime_fixture():
    assert restore('import-leaf') == 'import value'
    # The child is already built; this is actual nested consumption of it.
    with shared_state('fixture-parent'):
        VALUES['fixture-parent'] = restore('import-leaf') + '/' + read_named('fixture.txt')
    with shared_state('fixture-unused'):
        VALUES['fixture-unused'] = read_named('fixture-unused.txt')
    with unmeasured():
        with shared_state('paused-build'):
            VALUES['paused-build'] = read_named('paused.txt')
        assert restore('import-leaf') == 'import value'


def touch():
    return 'no use'


def paused_restore():
    with unmeasured():
        assert restore('fixture-parent') == 'import value/fixture value'
'''

IMPORT_MODULES = {
    'a': r'''
import unittest
import producer

producer.prime_import()
setUpModule = producer.prime_fixture


class Case(unittest.TestCase):
    def test_actual(self):
        self.assertEqual(producer.restore('import-leaf'), 'import value')

    def test_observer(self):
        self.assertEqual(producer.touch(), 'no use')

    def test_paused(self):
        producer.paused_restore()
        self.assertEqual(2 + 2, 4)
''',
    'b': r'''
import unittest
import producer


class Case(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = producer.restore('fixture-parent')

    def test_first(self):
        self.assertEqual(self.value, 'import value/fixture value')

    def test_second(self):
        self.assertEqual(self.value, 'import value/fixture value')
''',
}

REPLACEMENT_MODULE = r'''
import unittest


class Case(unittest.TestCase):
    def test_consume(self):
        self.assertEqual(2 + 2, 4)

    def test_passive(self):
        self.assertEqual(3 + 3, 6)
'''


def split_entries(entered):
    """Keep all literal label records, including empties; isolate only use markers."""
    return ({label: [pair for pair in pairs if pair[0] != '<shared>'] for label, pairs in entered.items()},
            {label: [pair[1] for pair in pairs if pair[0] == '<shared>']
             for label, pairs in entered.items() if any(pair[0] == '<shared>' for pair in pairs)})


def union_records(records):
    merged = {}
    for record in records:
        for label, values in record.items():
            merged.setdefault(label, set()).update(tuple(value) if isinstance(value, list) else value
                                                   for value in values)
    return {label: [list(value) if isinstance(value, tuple) else value for value in sorted(values)]
            for label, values in merged.items()}


def union_coverage(snapshots):
    files, contexts = set(), {}
    for snapshot in snapshots:
        files.update(snapshot['files'])
        for context, paths in snapshot['contexts'].items():
            target = contexts.setdefault(context, {})
            for path, values in paths.items():
                row = target.setdefault(path, {'lines': set(), 'arcs': set()})
                row['lines'].update(values['lines'])
                row['arcs'].update(tuple(arc) for arc in values['arcs'])
    return {'files': sorted(files), 'contexts': {
        context: {path: {'lines': sorted(row['lines']), 'arcs': [list(arc) for arc in sorted(row['arcs'])]}
                  for path, row in paths.items()} for context, paths in contexts.items()}}


def readers(snapshot, path):
    index = snapshot['index']
    return {index['tests'][ordinal] for ordinal in index['files'][path].get('readers', [])}


@test_group('resource')
class SharedInputProvenanceTests(unittest.TestCase):
    def test_actual_two_module_consumers_keep_literal_opens_separate_through_selection_and_store(self):
        for nested in (False, True):
            for order in ('ab', 'ba'):
                with self.subTest(nested=nested, order=order):
                    results = []
                    for mode in ('ordinary', 'measured'):
                        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
                        make_fixture(root, nested=nested)
                        completed = subprocess.run(
                            [sys.executable, '-B', '-c', PROBE, str(SCRIPTS), str(root), mode, order],
                            cwd=SCRIPTS, capture_output=True, text=True, timeout=90)
                        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                        results.append(json.loads((root / 'proof.json').read_text(encoding='utf-8')))
                    self.assertEqual(results[0], results[1])


    def fixture(self, **kwargs):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        make_fixture(root, **kwargs)
        return root

    def child(self, program, root, name, *args, scripts=SCRIPTS):
        directory = root / name
        completed = subprocess.run(
            [sys.executable, '-B', '-c', program, str(scripts), str(root), str(directory), *map(str, args)],
            cwd=scripts, capture_output=True, text=True, timeout=90)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads((directory / 'snapshot.json').read_text(encoding='utf-8'))

    def worker(self, root, name, *, order='ab', mode='measured', input_name='input.txt', scripts=SCRIPTS):
        return self.child(WORKER, root, name, mode, order, input_name, scripts=scripts)

    def pair(self, root, name, **kwargs):
        ordinary = self.worker(root, name + '-ordinary', mode='ordinary', **kwargs)
        measured = self.worker(root, name, **kwargs)
        self.assertEqual(ordinary['ordinary'], measured['ordinary'])
        return measured

    def test_two_real_workers_keep_same_key_inputs_isolated_after_merge_and_store(self):
        producer = PRODUCER.replace('{nested}', 'True').replace(
            "INPUT = Path(__file__).resolve().parents[1] / 'input.txt'",
            "import os\nINPUT = Path(__file__).resolve().parents[1] / os.environ['PROVENANCE_INPUT']")
        root = self.fixture(producer=producer, inputs={
            'input-a.txt': 'observed a', 'input-b.txt': 'observed b', 'unused.txt': 'unconsumed input'},
            modules={'a': MODULE.replace('observed input', 'observed a'),
                     'b': (MODULE + PASSIVE).replace('observed input', 'observed b')})
        ordinary = {letter: self.worker(root, 'ordinary-' + letter, mode='ordinary', order=letter,
                                        input_name='input-' + letter + '.txt') for letter in 'ab'}
        # Launch both before collecting either. These are two live interpreter
        # workers, each running _run_suite with its own Measurement and save.
        children = []
        try:
            for letter in 'ab':
                child = subprocess.Popen(
                    [sys.executable, '-B', '-c', WORKER, str(SCRIPTS), str(root),
                     str(root / ('worker-' + letter)), 'measured', letter, 'input-' + letter + '.txt'],
                    cwd=SCRIPTS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                children.append(child)
            for child in children:
                stdout, stderr = child.communicate(timeout=90)
                self.assertEqual(child.returncode, 0, stdout + stderr)
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                child.communicate()
        workers = [json.loads((root / ('worker-' + letter) / 'snapshot.json').read_text(encoding='utf-8'))
                   for letter in 'ab']
        self.assertEqual(len({worker['pid'] for worker in workers}), 2)
        expected = {}
        for letter, worker in zip('ab', workers):
            self.assertEqual(worker['ordinary'], ordinary[letter]['ordinary'])
            self.assertEqual(worker['ordinary']['reads'], ['read'])
            consumer = 'unit.test_input_' + letter + '.Case.test_consume'
            expected[consumer] = ['input-' + letter + '.txt']
            self.assertEqual(worker['dependencies'], {consumer: expected[consumer]})
            self.assertEqual(worker['shared_inputs'], {
                'shared:leaf': expected[consumer], 'shared:unused-leaf': ['unused.txt']})
            self.assertEqual(worker['opens'], {
                'fixture:unit.test_input_' + letter: ['input-' + letter + '.txt', 'unused.txt']})
            self.assertEqual(worker['import_opens'], {})
            literal, markers = split_entries(worker['entered'])
            self.assertIn(['scripts/producer.py', 'read_input'], literal['shared:leaf'])
            self.assertNotIn(['scripts/producer.py', 'read_input'], literal.get(consumer, []))
            self.assertEqual(markers, {consumer: ['outer'], 'shared:outer': ['leaf'],
                                       'shared:unused-outer': ['unused-leaf']})
        merged = self.child(STORE, root, 'merged', 'collision', root / 'worker-a', root / 'worker-b')
        self.assertEqual(merged['dependencies'], expected)
        self.assertEqual(merged['stored']['input_dependencies'], expected)
        self.assertEqual(merged['changed_plan']['measured_modules'], ['unit.test_input_b'])
        self.assertEqual(merged['changed_plan']['reused_modules'], ['unit.test_input_a'])
        self.assertEqual(merged['entered'], union_records([worker['entered'] for worker in workers]))
        for field in ('opens', 'import_opens'):
            self.assertEqual(merged[field], union_records([worker[field] for worker in workers]))
        self.assertEqual(merged['coverage'], union_coverage([worker['coverage'] for worker in workers]))
        for letter, worker in zip('ab', workers):
            module = 'unit.test_input_' + letter
            path = 'input-' + letter + '.txt'
            self.assertEqual(readers(merged, path), set(worker['ordinary']['ids']))
            self.assertEqual(set(merged['stored']['modules'][module]['inputs']), {path, 'unused.txt'})
            self.assertIn('read_input', merged['stored']['modules'][module]['functions']['scripts/producer.py'])

    def test_remeasured_consumer_stops_using_producer_and_normal_store_drops_dependency(self):
        root = self.fixture()
        before = self.pair(root, 'before')
        initial = self.child(STORE, root, 'initial-store', 'initial', root / 'before')
        a, b = 'unit.test_input_a', 'unit.test_input_b'
        self.assertEqual(initial['stored']['input_dependencies'], {
            a + '.Case.test_consume': ['input.txt'], b + '.Case.test_consume': ['input.txt']})
        self.assertEqual(before['opens'], {'fixture:' + a: ['input.txt', 'unused.txt']})
        # A real source edit followed by a fresh interpreter changes the test's
        # behavior. Never erase dependency data, use markers, or store stamps.
        (root / 'scripts/tests/unit/test_input_b.py').write_text(REPLACEMENT_MODULE, encoding='utf-8')
        after = self.pair(root, 'after', order='b')
        self.assertEqual(after['ordinary']['reads'], [])
        self.assertEqual(after['ordinary']['outcomes'],
                         {b + '.Case.test_consume': 'passed', b + '.Case.test_passive': 'passed'})
        self.assertEqual(after['dependencies'], {})
        self.assertEqual(after['opens'], {})
        self.assertEqual(after['import_opens'], {})
        self.assertEqual(split_entries(after['entered'])[1], {})
        replaced = self.child(STORE, root, 'replaced-store', 'replace', root / 'after')
        self.assertEqual(replaced['fresh']['entered'], after['entered'])
        self.assertEqual(replaced['fresh']['coverage'], after['coverage'])
        self.assertEqual(replaced['stored']['modules'][a], initial['stored']['modules'][a])
        self.assertEqual(replaced['stored']['modules'][b]['inputs'], {})
        self.assertEqual(replaced['stored']['modules'][b]['functions'], {})
        expected = {a + '.Case.test_consume': ['input.txt']}
        self.assertEqual(replaced['dependencies'], expected)
        self.assertEqual(replaced['stored']['input_dependencies'], expected)
        self.assertEqual(readers(replaced, 'input.txt'), {a + '.Case.test_consume'})
        self.assertEqual(split_entries(replaced['entered'])[1].get(b + '.Case.test_consume'), None)
        for field in ('entered', 'opens', 'input_dependencies'):
            kept_before = {label: value for label, value in initial['stored'][field].items()
                           if label == 'fixture:' + a or label.startswith(a + '.')}
            kept_after = {label: value for label, value in replaced['stored'][field].items()
                          if label == 'fixture:' + a or label.startswith(a + '.')}
            self.assertEqual(kept_after, kept_before)
        retained = {'files': initial['coverage']['files'], 'contexts': {
            context: paths for context, paths in initial['coverage']['contexts'].items()
            if context in {a, 'fixture:' + a}}}
        self.assertEqual(replaced['coverage'], union_coverage([retained, after['coverage']]))
        self.assertEqual(replaced['coverage']['contexts'].get(b, {}), {})
        # STORE changes the real input only after replacing the normal store.
        self.assertEqual(replaced['changed_plan']['measured_modules'], [a])
        self.assertEqual(replaced['changed_plan']['reused_modules'], [b])

    def import_fixture(self):
        return self.fixture(producer=IMPORT_PRODUCER, modules=IMPORT_MODULES, inputs={
            'import.txt': 'import value', 'import-unused.txt': 'unconsumed import',
            'fixture.txt': 'fixture value', 'fixture-unused.txt': 'unconsumed fixture',
            'paused.txt': 'paused actual read'})

    def test_real_import_and_fixture_builds_separate_literal_readers_from_actual_consumers(self):
        root = self.import_fixture()
        observed = self.pair(root, 'imports')
        a, b = 'unit.test_input_a', 'unit.test_input_b'
        a_ids = {test for test in observed['ordinary']['ids'] if test.startswith(a + '.')}
        b_ids = {test for test in observed['ordinary']['ids'] if test.startswith(b + '.')}
        self.assertEqual(observed['ordinary']['extra_reads'], [
            ['import.txt', 'import value'], ['import-unused.txt', 'unconsumed import'],
            ['fixture.txt', 'fixture value'], ['fixture-unused.txt', 'unconsumed fixture'],
            ['paused.txt', 'paused actual read']])
        self.assertEqual(observed['dependencies'], {
            'fixture:' + a: ['import.txt'],
            'fixture:' + b: ['fixture.txt', 'import.txt'],
            a + '.Case.test_actual': ['import.txt']})
        self.assertEqual(observed['opens'], {'fixture:' + a: ['fixture-unused.txt', 'fixture.txt']})
        self.assertEqual(observed['import_opens'], {
            'import.txt': ['scripts/producer.py'], 'import-unused.txt': ['scripts/producer.py']})
        self.assertEqual(observed['shared_inputs'], {
            'shared:import-leaf': ['import.txt'], 'shared:import-unused': ['import-unused.txt'],
            'shared:fixture-parent': ['fixture.txt'], 'shared:fixture-unused': ['fixture-unused.txt']})
        literal, markers = split_entries(observed['entered'])
        self.assertEqual(markers, {
            'fixture:' + a: ['import-leaf'], 'fixture:' + b: ['fixture-parent'],
            a + '.Case.test_actual': ['import-leaf'], 'shared:fixture-parent': ['import-leaf']})
        self.assertIn(['scripts/producer.py', 'read_named'], literal['shared:import-leaf'])
        self.assertIn(['scripts/producer.py', 'read_named'], literal['shared:fixture-parent'])
        self.assertTrue(all(['scripts/producer.py', 'read_named'] not in literal.get(test, [])
                            for test in observed['ordinary']['ids']))
        # Existing import-open attribution is intentionally broader: observer
        # enters touch() but has no shared-use edge. Fixture credit also includes
        # passive tests. Neither fact turns them into direct dependency labels.
        self.assertEqual(readers(observed, 'import.txt'), a_ids | b_ids)
        self.assertEqual(readers(observed, 'import-unused.txt'), a_ids | b_ids)
        self.assertEqual(readers(observed, 'fixture.txt'), a_ids | b_ids)
        self.assertEqual(readers(observed, 'fixture-unused.txt'), a_ids)
        self.assertNotIn('paused.txt', observed['index']['files'])
        read_line = next(i for i, line in enumerate(IMPORT_PRODUCER.splitlines(), 1)
                         if "value = INPUT.with_name(name).read_text" in line)
        contexts = observed['coverage']['contexts']
        self.assertEqual({context for context, paths in contexts.items()
                          if read_line in paths.get('scripts/producer.py', {}).get('lines', [])},
                         {'', 'fixture:' + a})
        self.assertTrue(all(not context.startswith('shared:') for context in contexts))
        self.assertNotIn(read_line, contexts.get('fixture:' + b, {}).get('scripts/producer.py', {}).get('lines', []))
        stored = self.child(STORE, root, 'import-store', 'imports', root / 'imports')
        self.assertEqual(stored['dependencies'], observed['dependencies'])
        self.assertEqual(stored['stored']['input_dependencies'], observed['dependencies'])
        self.assertEqual(stored['opens'], observed['opens'])
        self.assertEqual(stored['import_opens'], observed['import_opens'])
        self.assertEqual(stored['entered'], observed['entered'])
        self.assertEqual(stored['coverage'], observed['coverage'])
        self.assertEqual(set(stored['stored']['import_inputs']), {'import.txt', 'import-unused.txt'})
        self.assertEqual(set(stored['stored']['modules'][a]['inputs']),
                         {'import.txt', 'fixture.txt', 'fixture-unused.txt'})
        self.assertEqual(set(stored['stored']['modules'][b]['inputs']), {'import.txt', 'fixture.txt'})

    def assert_baseline_capture(self, root, name, *, order='ab', input_name='input.txt'):
        baseline = Path(os.environ['SHARED_INPUT_BASELINE_SCRIPTS']).resolve()
        self.assertNotEqual(baseline, SCRIPTS.resolve(), 'Baseline must be a separate pre-fix scripts tree')
        ordinary_old = self.worker(root, name + '-old-ordinary', mode='ordinary', order=order,
                                   input_name=input_name, scripts=baseline)
        ordinary_new = self.worker(root, name + '-new-ordinary', mode='ordinary', order=order, input_name=input_name)
        old = self.worker(root, name + '-old', mode='baseline', order=order, input_name=input_name, scripts=baseline)
        new = self.worker(root, name + '-new', order=order, input_name=input_name)
        self.assertEqual(ordinary_old['ordinary'], ordinary_new['ordinary'])
        self.assertEqual(old['ordinary'], ordinary_old['ordinary'])
        self.assertEqual(new['ordinary'], ordinary_new['ordinary'])
        old_literal, old_markers = split_entries(old['entered'])
        new_literal, new_markers = split_entries(new['entered'])
        self.assertEqual(old_literal, new_literal)  # Every label, every pair, including empty lists.
        self.assertEqual(old['opens'], new['opens'])
        self.assertEqual(old['import_opens'], new['import_opens'])
        self.assertEqual(old['coverage'], new['coverage'])  # Exact files, contexts, lines AND arcs.
        return old, new, old_markers, new_markers

    @unittest.skipUnless(os.environ.get('SHARED_INPUT_BASELINE_SCRIPTS'),
                         'P10/P11 pending: supply a separate pre-provenance-fix scripts tree')
    def test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences(self):
        for nested in (False, True):
            for order in ('ab', 'ba'):
                with self.subTest(nested=nested, order=order):
                    root = self.fixture(nested=nested)
                    old, new, old_markers, new_markers = self.assert_baseline_capture(root, 'serial', order=order)
                    consumers = {'unit.test_input_' + letter + '.Case.test_consume': ['outer'] for letter in 'ab'}
                    fixture = 'fixture:unit.test_input_' + order[0]
                    self.assertEqual(old_markers, {
                        **consumers, fixture: ['leaf', 'unused-leaf'] if nested else ['unused-leaf'],
                        'unit.test_input_b.Case.test_passive': ['outer']})
                    self.assertEqual(new_markers, {
                        **consumers, **({'shared:outer': ['leaf']} if nested else {}),
                        'shared:unused-outer': ['unused-leaf']})
        root = self.import_fixture()
        old, new, old_markers, new_markers = self.assert_baseline_capture(root, 'imports')
        self.assertEqual(old_markers, {
            'fixture:unit.test_input_a': ['import-leaf'],
            'fixture:unit.test_input_b': ['fixture-parent'],
            'unit.test_input_a.Case.test_actual': ['import-leaf'],
            'unit.test_input_a.Case.test_paused': ['fixture-parent']})
        self.assertEqual(new_markers, {
            'fixture:unit.test_input_a': ['import-leaf'],
            'fixture:unit.test_input_b': ['fixture-parent'],
            'unit.test_input_a.Case.test_actual': ['import-leaf'],
            'shared:fixture-parent': ['import-leaf']})

    @unittest.skipUnless(os.environ.get('SHARED_INPUT_BASELINE_SCRIPTS'),
                         'P10/P11 pending: supply a separate pre-provenance-fix scripts tree')
    def test_exact_baseline_two_worker_raw_union(self):
        producer = PRODUCER.replace('{nested}', 'True').replace(
            "INPUT = Path(__file__).resolve().parents[1] / 'input.txt'",
            "import os\nINPUT = Path(__file__).resolve().parents[1] / os.environ['PROVENANCE_INPUT']")
        root = self.fixture(producer=producer, inputs={
            'input-a.txt': 'observed a', 'input-b.txt': 'observed b', 'unused.txt': 'unconsumed input'},
            modules={'a': MODULE.replace('observed input', 'observed a'),
                     'b': (MODULE + PASSIVE).replace('observed input', 'observed b')})
        old_workers, new_workers = [], []
        for letter in 'ab':
            old, new, old_markers, new_markers = self.assert_baseline_capture(
                root, letter, order=letter, input_name='input-' + letter + '.txt')
            consumer = 'unit.test_input_' + letter + '.Case.test_consume'
            self.assertEqual(old_markers, {
                consumer: ['outer'], 'fixture:unit.test_input_' + letter: ['leaf', 'unused-leaf'],
                **({'unit.test_input_b.Case.test_passive': ['outer']} if letter == 'b' else {})})
            self.assertEqual(new_markers, {consumer: ['outer'], 'shared:outer': ['leaf'],
                                           'shared:unused-outer': ['unused-leaf']})
            old_workers.append(old)
            new_workers.append(new)
        baseline = Path(os.environ['SHARED_INPUT_BASELINE_SCRIPTS']).resolve()
        merge = SNAPSHOT + r'''
directory.mkdir()
measured = bg.Measurement(root, data_file=directory / bg.DATA)
assert measured.merge([Path(path) for path in sys.argv[4:]]) == []
(directory / 'snapshot.json').write_text(json.dumps(snapshot(measured)), encoding='utf-8')
'''
        old = self.child(merge, root, 'old-merge', root / 'a-old', root / 'b-old', scripts=baseline)
        new = self.child(merge, root, 'new-merge', root / 'a-new', root / 'b-new')
        for merged, workers in ((old, old_workers), (new, new_workers)):
            self.assertEqual(merged['entered'], union_records([worker['entered'] for worker in workers]))
            self.assertEqual(merged['coverage'], union_coverage([worker['coverage'] for worker in workers]))
            for field in ('opens', 'import_opens'):
                self.assertEqual(merged[field], union_records([worker[field] for worker in workers]))
        self.assertEqual(split_entries(old['entered'])[0], split_entries(new['entered'])[0])
        self.assertEqual(old['opens'], new['opens'])
        self.assertEqual(old['import_opens'], new['import_opens'])
        self.assertEqual(old['coverage'], new['coverage'])


if __name__ == '__main__':
    unittest.main()
