"""Every product module is declared in do_math/layers.py, and declared modules obey their layer."""
from pathlib import Path
import unittest

from do_math.layers import LAYERS, PENDING
from support.layer_rules import check_tree

SCRIPTS = Path(__file__).resolve().parents[2]


class LayerTests(unittest.TestCase):
    def test_declared_modules_obey_their_layer_and_no_module_is_undeclared(self):
        issues = check_tree(SCRIPTS, LAYERS, PENDING)
        self.assertEqual(issues, [], '\n'.join(str(issue) for issue in issues))


if __name__ == '__main__':
    unittest.main()
