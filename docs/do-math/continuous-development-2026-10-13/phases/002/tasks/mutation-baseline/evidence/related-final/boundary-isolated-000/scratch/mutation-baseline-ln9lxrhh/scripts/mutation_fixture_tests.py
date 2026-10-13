import os
import unittest
from mutation_fixture_subject import value

class Case(unittest.TestCase):
    def test_value(self):
        with self.subTest(axis=1):
            self.assertEqual(value(), 2)
        self.assertEqual(value(), 2)
