import os
import unittest
from mutation_fixture_subject import value
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
