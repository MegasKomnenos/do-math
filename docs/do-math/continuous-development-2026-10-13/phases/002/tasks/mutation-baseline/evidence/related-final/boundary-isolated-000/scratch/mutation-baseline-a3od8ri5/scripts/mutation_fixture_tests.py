import os
import unittest
from mutation_fixture_subject import value
def setUpModule():
    if value() == 2:
        raise unittest.SkipTest("fixture skip")
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
