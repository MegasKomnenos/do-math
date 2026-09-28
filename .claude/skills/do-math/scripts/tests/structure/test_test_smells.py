"""New-system tests carry no smell of 설계 6.2, and product coverage exclusions state a reason."""
from pathlib import Path
import unittest

from do_math.layers import LAYERS, PENDING
from support.smell_rules import pragma_issues, smell_issues

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = SCRIPTS / 'tests'
FOLDERS = ('structure', 'unit', 'sim', 'contracts', 'boundary', 'smoke')


class SmellTests(unittest.TestCase):
    def test_new_system_tests_have_no_smell(self):
        files = [path for folder in FOLDERS for path in sorted((TESTS / folder).glob('test_*.py'))]
        self.assertGreater(len(files), 0)
        issues = [issue for path in files
                  for issue in smell_issues(path.read_text(encoding='utf-8'), path.relative_to(TESTS).as_posix())]
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))

    def test_product_coverage_exclusions_state_a_reason(self):
        issues = [issue for module in sorted({**LAYERS, **PENDING})
                  for issue in pragma_issues((SCRIPTS / module).read_text(encoding='utf-8'), module)]
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))


if __name__ == '__main__':
    unittest.main()
