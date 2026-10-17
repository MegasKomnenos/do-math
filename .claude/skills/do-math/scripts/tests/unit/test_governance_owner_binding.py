"""Builtin owner identity survives removal of a caller's clock binding."""
import unittest

from do_math import governance
from support.fakes.clock import FakeClock


class OwnerBindingTests(unittest.TestCase):
    def test_unbinding_preserves_the_actual_builtin_callbacks(self):
        bound = governance.import_owner_handlers(clock=FakeClock())['evidence']
        self.assertEqual(governance._unbound(bound), {
            'apply': governance._knowledge_import,
            'validate': governance._validate_knowledge_import,
            'basis': governance._knowledge_import_basis,
        })
