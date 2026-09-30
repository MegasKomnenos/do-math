"""The public ``initialize`` preserves the user's exact input text and source file (``initialization``), moved from ``test_initial_intent_connection``.

The legacy test ran the public ``initialize`` on a real Git repository
(``research_fixtures.new_instance``); here it runs on a Sim
(``Sim(root, sources=...)``) and the stored state and source bytes are read back
through the Sim engine's ``ResearchRepository`` over the Git port's fake.
"""
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim

# A combining accent and the Kelvin sign: text that Unicode normalization would change.
UNSTABLE = 'e\N{COMBINING ACUTE ACCENT} and \N{KELVIN SIGN} are exact source text'


class InitialIntentConnectionTests(unittest.TestCase):
    def test_public_initialization_stores_exact_text_and_source_filename(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'e\N{COMBINING ACUTE ACCENT}.txt'
            source.write_bytes(UNSTABLE.encode())
            sim = Sim(root / 'sim', goal=UNSTABLE, sources=[source])
            store = sim.engine.store
            head, instance, _ = store.load()
            self.assertEqual(instance['lifecycle']['immutable_input']['text'], UNSTABLE)
            preserved = instance['sources'][0]
            self.assertEqual(preserved['name'], source.name)
            self.assertIn(source.name, preserved['path'])
            self.assertEqual(store.read(preserved['path'], head), source.read_bytes())


if __name__ == '__main__':
    unittest.main()
