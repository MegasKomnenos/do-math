"""The engine supplies the declared reading documents to a role input and to the installation check
(``core_engine._context``, ``_installation_manifest``; layer 2), moved from ``test_reading_map`` (``DocumentContextTests``).

The legacy tests ran on the synthetic active template (``ActivatedPurposeHarness``,
with the provider adapter patched). Here the engine is a restored Sim's: the
public activation's instance on the port fakes, with nothing replaced.
"""
import hashlib
import unittest

from support.sim import Sim, warm_template

setUpModule = warm_template


class DocumentContextTests(unittest.TestCase):
    def test_declared_documents_have_recoverable_input_copies(self):
        sim = Sim.activated()
        engine = sim.engine
        workspace = sim.root / 'preview'
        workspace.mkdir()
        context = engine._context({'role': 'research_preparation'}, workspace)
        self.assertIn('implementation_documents', context)
        documents = context['implementation_documents']
        self.assertEqual([d['path'] for d in documents], [d['path'] for d in engine._documents['research_preparation']])
        for row, original in zip(documents, engine._documents['research_preparation']):
            raw = (workspace / row['local_path']).read_bytes()
            self.assertEqual(raw, original['content'].encode('utf-8'))
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])

    def test_installed_reference_changes_are_part_of_the_version_check(self):
        engine = Sim.activated().engine
        files = engine._installation_manifest()['files']
        self.assertIn('references/공통-실행.md', files)
        self.assertIn('references/지식-저작과-재사용.md', files)
        self.assertIn('references/학술자료-활용.md', files)


if __name__ == '__main__':
    unittest.main()
