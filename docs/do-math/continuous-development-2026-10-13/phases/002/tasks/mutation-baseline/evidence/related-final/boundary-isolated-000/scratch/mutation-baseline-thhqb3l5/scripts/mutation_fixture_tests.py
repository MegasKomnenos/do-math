import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        if value() == 2:
            os._exit(17)
        self.assertEqual(value(), 2)
