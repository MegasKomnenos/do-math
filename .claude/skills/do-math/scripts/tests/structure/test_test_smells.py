"""New-system tests carry no smell of 설계 6.2, and product coverage exclusions state a reason.

Test-side helpers get the product-patch rule too, so a patch cannot enter a new
test through a helper: ``tests/support`` always, and the legacy ``*_fixtures.py``
modules once no legacy test is left to need their patches (1f).
"""
from pathlib import Path
import unittest

from do_math.layers import LAYERS, PENDING
from run_tests import FOLDERS  # every new-system tier folder, so a new folder cannot escape the check
from support.smell_rules import patch_issues, pragma_issues, smell_issues

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = SCRIPTS / 'tests'


class SmellTests(unittest.TestCase):
    def test_new_system_tests_have_no_smell(self):
        files = [path for folder in FOLDERS for path in sorted((TESTS / folder).glob('test_*.py'))]
        self.assertGreater(len(files), 0)
        issues = [issue for path in files
                  for issue in smell_issues(path.read_text(encoding='utf-8'), path.relative_to(TESTS).as_posix())]
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))

    def test_test_side_helpers_patch_no_product_name(self):
        helpers = sorted((TESTS / 'support').rglob('*.py'))
        if not list(TESTS.glob('test_*.py')):
            helpers += sorted(TESTS.glob('*_fixtures.py'))
        issues = [issue for path in helpers
                  for issue in patch_issues(path.read_text(encoding='utf-8'), path.relative_to(TESTS).as_posix())]
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))

    def test_product_coverage_exclusions_state_a_reason(self):
        issues = [issue for module in sorted({**LAYERS, **PENDING})
                  for issue in pragma_issues((SCRIPTS / module).read_text(encoding='utf-8'), module)]
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))


if __name__ == '__main__':
    unittest.main()
