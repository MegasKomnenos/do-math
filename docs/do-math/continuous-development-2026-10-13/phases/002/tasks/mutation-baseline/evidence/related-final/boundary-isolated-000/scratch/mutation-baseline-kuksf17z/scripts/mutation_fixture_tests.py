import os
import unittest
from mutation_fixture_subject import value
@unittest.expectedFailure
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
