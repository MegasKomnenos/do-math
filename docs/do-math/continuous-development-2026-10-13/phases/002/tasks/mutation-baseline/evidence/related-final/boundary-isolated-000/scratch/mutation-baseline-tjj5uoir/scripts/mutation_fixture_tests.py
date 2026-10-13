import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        self.fail("normal failure")
        self.assertEqual(value(), 2)
    def test_z(self):
        self.assertEqual(value(), 2)
