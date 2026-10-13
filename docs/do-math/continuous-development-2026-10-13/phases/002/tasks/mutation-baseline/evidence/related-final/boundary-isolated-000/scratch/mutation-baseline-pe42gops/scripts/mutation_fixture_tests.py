import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        if value() is None:
            os._exit(19)
        self.assertEqual(value(), 2)
