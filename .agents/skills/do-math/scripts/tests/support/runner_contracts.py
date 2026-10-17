"""Temporary on-disk runner packages; discovery and reporting stay real.

Only the filesystem roots and import namespace are isolated. Specimens may
change this temporary tree without editing the official runner's source tree.
"""
from pathlib import Path
import sys
import tempfile
from unittest import mock

import run_tests


def runner_tree(case):
    scripts = Path(case.enterContext(tempfile.TemporaryDirectory())) / 'scripts'
    root = scripts / 'tests'
    for folder in run_tests.FOLDERS:
        package = root / folder
        package.mkdir(parents=True)
        (package / '__init__.py').write_text('', encoding='utf-8')
    (root / 'budgets.json').write_bytes((run_tests.TESTS / 'budgets.json').read_bytes())
    case.enterContext(mock.patch.object(run_tests, 'SCRIPTS', scripts))
    case.enterContext(mock.patch.object(run_tests, 'TESTS', root))
    case.enterContext(mock.patch.object(run_tests, 'TIMINGS', root / '.timings.json'))
    case.enterContext(mock.patch.object(sys, 'path', sys.path.copy()))
    case.enterContext(mock.patch.dict(sys.modules))
    for name in list(sys.modules):
        if name.split('.')[0] in run_tests.FOLDERS:
            del sys.modules[name]
    return root
