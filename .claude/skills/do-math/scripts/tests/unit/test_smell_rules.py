"""Test-smell rules (설계 6.2) judged on synthetic test sources."""
import textwrap
import unittest

from support.smell_rules import normalization_issues, pragma_issues, smell_issues


def _rules(source):
    return sorted(issue['rule'] for issue in smell_issues(textwrap.dedent(source), 'unit/test_x.py'))


class SmellTests(unittest.TestCase):
    def test_a_test_with_an_assertion_passes(self):
        self.assertEqual(_rules('''
            class T:
                def test_a(self):
                    self.assertEqual(1, 1)
        '''), [])

    def test_a_test_without_any_assertion_is_reported(self):
        self.assertEqual(_rules('''
            class T:
                def test_a(self):
                    value = 1 + 1
        '''), ['no_assertion'])

    def test_a_registered_assertion_helper_counts_as_an_assertion(self):
        self.assertEqual(_rules('''
            from support.sim import assert_reaches
            class T:
                def test_a(self):
                    assert_reaches(self, None)
        '''), [])

    def test_an_exception_type_alone_does_not_pin_the_rejection_reason(self):
        self.assertEqual(_rules('''
            class T:
                def test_a(self):
                    with self.assertRaises(ValueError):
                        int('x')
        '''), ['unpinned_rejection'])

    def test_a_rejection_reason_pinned_by_regex_or_by_inspecting_the_exception_passes(self):
        self.assertEqual(_rules('''
            class T:
                def test_a(self):
                    with self.assertRaisesRegex(ValueError, 'invalid literal'):
                        int('x')
                def test_b(self):
                    with self.assertRaises(ValueError) as caught:
                        int('x')
                    self.assertIn('invalid literal', str(caught.exception))
        '''), [])

    def test_patching_a_product_name_is_reported(self):
        self.assertEqual(_rules('''
            from unittest.mock import patch
            from do_math import engine
            class T:
                def test_a(self):
                    with patch.object(engine, 'run'):
                        self.assertTrue(True)
                def test_b(self):
                    with patch('do_math.engine.run'):
                        self.assertTrue(True)
        '''), ['product_patch', 'product_patch'])

    def test_patching_a_product_name_outside_a_test_method_is_reported(self):
        self.assertEqual(_rules('''
            from unittest.mock import patch
            def helper():
                return patch('do_math.engine.run')
            @patch('do_math.formal.discover_lean')
            class T:
                def setUp(self):
                    patch('do_math.engine.run').start()
                def test_a(self):
                    self.assertTrue(True)
        '''), ['product_patch', 'product_patch', 'product_patch'])

    def test_fixed_sleep_skip_without_reason_and_broad_except_are_reported(self):
        self.assertEqual(_rules('''
            import time, unittest
            class T:
                @unittest.skip('')
                def test_a(self):
                    self.assertTrue(True)
                def test_b(self):
                    time.sleep(1)
                    self.assertTrue(True)
                def test_c(self):
                    try:
                        self.assertTrue(True)
                    except Exception:
                        pass
        '''), ['broad_except', 'fixed_sleep', 'unreasoned_skip'])

    def test_a_skip_with_a_reason_passes(self):
        self.assertEqual(_rules('''
            import unittest
            class T:
                @unittest.skipUnless(False, 'needs Windows')
                def test_a(self):
                    self.assertTrue(True)
        '''), [])


class NormalizationTests(unittest.TestCase):
    def test_a_character_that_normalization_changes_is_reported_by_line_and_an_escape_is_not(self):
        combining = 'x = "e' + chr(0x301) + '"\n'
        kelvin = 'y = "' + chr(0x212A) + '"\n'
        issues = normalization_issues('a = 1\n' + combining + kelvin, 'unit/test_x.py')
        self.assertEqual([(i['rule'], i['line']) for i in issues], [('unnormalized_text', 2), ('unnormalized_text', 3)])
        self.assertEqual(normalization_issues('x = "e\\u0301"\n', 'unit/test_x.py'), [])


class PragmaTests(unittest.TestCase):
    def test_a_coverage_exclusion_needs_a_reason(self):
        self.assertEqual([i['rule'] for i in pragma_issues('x = 1  # pragma: no cover\n', 'm.py')],
                         ['unreasoned_exclusion'])
        self.assertEqual(pragma_issues('x = 1  # pragma: no cover - unreachable on Windows\n', 'm.py'), [])


if __name__ == '__main__':
    unittest.main()
