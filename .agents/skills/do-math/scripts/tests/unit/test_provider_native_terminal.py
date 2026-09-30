"""An unsubmitted provider terminal is not a research result: the engine's collection of a submitted result
(``core_engine._collect_submitted_result``, layer 2), moved from ``test_provider_final_contract``.

A bound call returns only provider evidence. Without a central submission the
engine tries to capture the native final, which needs the collection and
termination evidence the runner records; a result without it fails as an
execution failure and captures nothing. The legacy test called the method on
an engine object over an in-memory store (``bare_engine``); here it is the real
engine loaded from a small state on the Git fake (``support.provider_state``).
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from support.provider_state import engine_over


class UnsubmittedTerminalTests(unittest.TestCase):
    def test_unsubmitted_provider_terminal_is_not_a_research_result(self):
        engine, _ = engine_over(Path(self.enterContext(tempfile.TemporaryDirectory())))
        result = {'status': 'completed', 'output': None, 'collection': 'provider_evidence_only'}
        before, head = deepcopy(engine.runtime), engine.head
        rejected = engine._collect_submitted_result({}, result, {}, {}, None)
        self.assertEqual(rejected['status'], 'failed')
        self.assertEqual(rejected['error_kind'], 'execution_failure')
        self.assertIsNone(rejected['output'])
        self.assertEqual(rejected['error'], 'native completion evidence is missing or malformed')
        # Nothing was captured or published.
        self.assertEqual(engine.runtime, before)
        self.assertEqual(engine.head, head)


if __name__ == '__main__':
    unittest.main()
