import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        if value() == 2:
            self.skipTest("normal skip")
        self.assertEqual(value(), 2)
