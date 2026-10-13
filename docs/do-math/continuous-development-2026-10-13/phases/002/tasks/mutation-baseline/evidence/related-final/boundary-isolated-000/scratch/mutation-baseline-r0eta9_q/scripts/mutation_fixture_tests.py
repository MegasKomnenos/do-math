import os
import unittest
from mutation_fixture_subject import value
import atexit
if value() == 2:
    atexit.register(lambda: os._exit(23))
class Case(unittest.TestCase):
    def test_value(self):

        self.assertEqual(value(), 2)
