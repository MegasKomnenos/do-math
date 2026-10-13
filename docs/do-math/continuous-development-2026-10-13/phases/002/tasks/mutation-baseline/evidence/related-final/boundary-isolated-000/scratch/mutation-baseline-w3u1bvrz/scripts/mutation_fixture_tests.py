import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        if value() == 2:
            with self.subTest(axis=1):
                self.skipTest("subtest skip")
        self.assertEqual(value(), 2)
