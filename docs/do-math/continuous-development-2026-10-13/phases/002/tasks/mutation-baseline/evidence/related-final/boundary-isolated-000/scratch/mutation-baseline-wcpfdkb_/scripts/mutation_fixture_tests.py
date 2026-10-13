import os
import unittest
from mutation_fixture_subject import value
if value() is None:
    raise ImportError("specimen load")
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
