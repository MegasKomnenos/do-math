"""Layer rules (설계 2.1, 3.3) judged on small synthetic product trees."""
from pathlib import Path
import tempfile
import textwrap
import unittest

from support.layer_rules import check_tree


def _tree(files):
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    for name, source in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(source), encoding='utf-8')
    return directory, root


def _rules(issues):
    return sorted((issue['module'], issue['rule']) for issue in issues)


class EffectBanTests(unittest.TestCase):
    def check(self, source, layer):
        directory, root = _tree({'do_math/__init__.py': '', 'do_math/m.py': source})
        with directory:
            return _rules(check_tree(root, {'do_math/__init__.py': '1', 'do_math/m.py': layer}, {}))

    def test_first_and_second_layers_may_not_touch_processes_threads_or_ambient_time(self):
        for source in ('import subprocess\n', 'import threading\n', 'import ctypes\n',
                       'import time\nx = time.time()\n', 'import time\ntime.sleep(1)\n',
                       'from datetime import datetime\nx = datetime.now()\n',
                       'import os\nx = os.urandom(4)\n', 'import uuid\nx = uuid.uuid4()\n'):
            for layer in ('1', '2'):
                with self.subTest(source=source, layer=layer):
                    self.assertEqual(self.check(source, layer), [('do_math/m.py', 'effect')])

    def test_third_layer_and_adapters_may_use_effects(self):
        for layer in ('3', 'adapter'):
            self.assertEqual(self.check('import subprocess\nimport time\ntime.sleep(1)\n', layer), [])

    def test_first_layer_may_not_do_file_io_but_second_layer_may(self):
        source = "from pathlib import Path\ndef f(p):\n    return Path(p).read_text()\n"
        self.assertEqual(self.check(source, '1'), [('do_math/m.py', 'effect')])
        self.assertEqual(self.check(source, '2'), [])
        self.assertEqual(self.check("def f(p):\n    return open(p).read()\n", '1'), [('do_math/m.py', 'effect')])

    def test_a_reasoned_exemption_comment_allows_one_line(self):
        self.assertEqual(self.check('import time\nx = time.time()  # layer: wall clock for a log label\n', '2'), [])

    def test_an_exemption_comment_without_a_reason_is_not_an_exemption(self):
        self.assertEqual(self.check('import time\nx = time.time()  # layer:\n', '2'), [('do_math/m.py', 'effect')])

    def test_pure_code_passes_in_the_first_layer(self):
        self.assertEqual(self.check('import json\ndef f(x):\n    return json.dumps(x, sort_keys=True)\n', '1'), [])


class ImportDirectionTests(unittest.TestCase):
    def check(self, layers, sources):
        files = {'do_math/__init__.py': '', **sources}
        directory, root = _tree(files)
        with directory:
            return _rules(check_tree(root, {'do_math/__init__.py': '1', **layers}, {}))

    def test_allowed_directions(self):
        layers = {'do_math/a.py': '1', 'do_math/j.py': 'adapter', 'do_math/k.py': 'adapter',
                  'do_math/b.py': '2', 'do_math/c.py': '3'}
        sources = {'do_math/a.py': '', 'do_math/j.py': 'from do_math import a\n',
                   'do_math/k.py': 'from do_math import j\n',
                   'do_math/b.py': 'from do_math import a\n', 'do_math/c.py': 'from do_math import b, j\n'}
        self.assertEqual(self.check(layers, sources), [])

    def test_forbidden_directions(self):
        cases = [
            ({'do_math/a.py': '1', 'do_math/b.py': '2'}, {'do_math/a.py': 'from do_math import b\n', 'do_math/b.py': ''}, 'do_math/a.py'),
            ({'do_math/b.py': '2', 'do_math/j.py': 'adapter'}, {'do_math/b.py': 'from do_math import j\n', 'do_math/j.py': ''}, 'do_math/b.py'),
            ({'do_math/j.py': 'adapter', 'do_math/b.py': '2'}, {'do_math/j.py': 'from do_math.b import x\n', 'do_math/b.py': 'x = 1\n'}, 'do_math/j.py'),
            ({'do_math/b.py': '2', 'do_math/c.py': '3'}, {'do_math/b.py': 'def f():\n    from do_math import c\n', 'do_math/c.py': ''}, 'do_math/b.py'),
        ]
        for layers, sources, offender in cases:
            with self.subTest(offender=offender, sources=sources):
                self.assertEqual(self.check(layers, sources), [(offender, 'import_direction')])

    def test_relative_imports_resolve_to_product_modules(self):
        layers = {'do_math/a.py': '1', 'do_math/b.py': '2'}
        self.assertEqual(self.check(layers, {'do_math/a.py': 'from .b import x\n', 'do_math/b.py': 'x = 1\n'}),
                         [('do_math/a.py', 'import_direction')])


class CompletenessTests(unittest.TestCase):
    def test_every_product_module_is_declared_or_pending_and_names_exist(self):
        directory, root = _tree({'do_math/__init__.py': '', 'do_math/a.py': '', 'do_math/b.py': '', 'tool.py': ''})
        with directory:
            issues = check_tree(root, {'do_math/__init__.py': '1', 'do_math/a.py': '1', 'do_math/gone.py': '1'},
                                {'do_math/b.py': '2'})
        self.assertEqual(_rules(issues), [('do_math/gone.py', 'declared_but_absent'), ('tool.py', 'undeclared')])

    def test_pending_modules_are_not_judged_and_may_not_also_be_declared(self):
        directory, root = _tree({'do_math/__init__.py': '', 'do_math/a.py': 'import subprocess\n'})
        with directory:
            self.assertEqual(check_tree(root, {'do_math/__init__.py': '1'}, {'do_math/a.py': '1'}), [])
            self.assertEqual(_rules(check_tree(root, {'do_math/__init__.py': '1', 'do_math/a.py': '1'},
                                               {'do_math/a.py': '1'})), [('do_math/a.py', 'declared_and_pending')])

    def test_the_test_runner_files_are_not_product_modules(self):
        directory, root = _tree({'do_math/__init__.py': '', 'run_tests.py': '', 'test_categories.py': ''})
        with directory:
            self.assertEqual(check_tree(root, {'do_math/__init__.py': '1'}, {}), [])


if __name__ == '__main__':
    unittest.main()
