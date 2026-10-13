import os
import unittest
from mutation_fixture_subject import value
def setUpModule():
    if value() == 2:
        raise RuntimeError("fixture error")
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
