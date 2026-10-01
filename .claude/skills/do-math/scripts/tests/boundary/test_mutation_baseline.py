"""Mutation baseline bookkeeping against actual Git blobs and HEAD."""
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from support import mutation
from test_categories import test_group


@test_group("resource")
class LazyBaselineTests(unittest.TestCase):
    def test_only_a_test_that_failed_a_mutant_is_rechecked_unmutated_and_one_failing_unmutated_is_set_aside(self):
        """No union baseline: a mutant's failing test counts only if it passes unmutated (D9)."""
        from support.branch_gate import git_blobs, repository_root
        root = repository_root()
        module = 'do_math/http_request.py'
        path = f'{mutation.SCRIPTS.relative_to(root).as_posix()}/{module}'
        index = {'tests': ['t0', 't1', 't2'],
                 'files': {path: {'blob': git_blobs(root, [path])[path],
                                  'functions': {'check_url': [1], 'check_body': [0, 2]}}}}
        calls = []

        def child(spec, directory, timeout):
            tests = spec['tests']
            calls.append((spec['mutant'] is not None, tests))
            if spec['mutant'] is None:
                return {'t0'} & set(tests), 0.1
            return ({'t1'} if 't1' in tests else {'t0'} if 't0' in tests else set()), 0.1
        self.enterContext(mock.patch.object(mutation, '_child_run', child))
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        report = mutation.run('HEAD', index, {module: '1'}, root, directory, only=[module], every=True, timeout=60.0,
                              listing_path=directory / 'pseudo_tested.json')
        self.assertEqual({o['function']: o['status'] for o in report['outcomes']},
                         {'check_url': 'killed', 'check_body': 'survived'})
        self.assertEqual([tests for mutated, tests in calls if not mutated], [['t1'], ['t0']])
        self.assertEqual(report['baseline_failing'], ['t0'])
