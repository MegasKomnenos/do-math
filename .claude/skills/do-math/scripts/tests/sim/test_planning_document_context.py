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


class InstallationEditionTests(unittest.TestCase):
    def engine(self):
        from do_math.engine import ResearchEngine
        from support.storage_finish_installation import copy_installation
        sim = Sim.activated()
        root = copy_installation(sim.root / 'installation')
        sim.engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=root, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        return sim, root

    def test_periodic_installation_check_rehashes_no_unchanged_file(self):
        from do_math import file_io, core_engine
        from support.provider_probes import ObservedCalls
        sim, root = self.engine()
        baseline = sim.engine._installation_manifest()
        # Only the installation summary is forgotten; file fingerprints/digests remain.
        core_engine._HASHED_INSTALLATION.clear()
        with ObservedCalls(hash=file_io.sha256_file, reading=core_engine.reading_map) as calls:
            self.assertEqual(sim.engine._installation_manifest(), baseline)
        self.assertEqual(calls.count('reading'), 1)
        self.assertEqual(calls.count('hash'), 0)

    def test_unchanged_installation_listing_reuses_the_hashed_edition(self):
        """About 3 s: two real installation copies distinguish root isolation from edition reuse."""
        import os
        from do_math import core_engine
        from do_math.engine import ResearchEngine
        from support.provider_probes import ObservedCalls, settle
        from support.storage_finish_installation import copy_installation
        sim, root = self.engine()
        e = sim.engine
        baseline = e._installation_manifest()
        other = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=root / '.', codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        with ObservedCalls(reading=core_engine.reading_map) as calls:
            self.assertIs(e._installation_manifest(), baseline)
            self.assertIs(other._installation_manifest(), baseline)
        self.assertEqual(calls.count('reading'), 0)
        path = root / 'scripts/do_math/engine.py'
        stamp = path.stat()
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns - 10 ** 9))
        with ObservedCalls(reading=core_engine.reading_map) as calls:
            self.assertEqual(e._installation_manifest(), baseline)
        self.assertEqual(calls.count('reading'), 1)
        added = root / 'scripts/do_math/storage_finish_added.py'
        added.write_bytes(b'edition = 1\n')
        settle(added)
        changed = e._installation_manifest()
        self.assertNotEqual(changed, baseline)
        self.assertIn('scripts/do_math/storage_finish_added.py', changed['files'])
        added.unlink()
        self.assertEqual(e._installation_manifest(), baseline)
        second = copy_installation(sim.root / 'another-installation')
        second_engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=second, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        self.assertEqual(second_engine._installation_manifest(), baseline)
        (second / 'references/공통-실행.md').write_bytes(b'edited document\n')
        self.assertNotEqual(second_engine._installation_manifest(), baseline)
        self.assertEqual(e._installation_manifest(), baseline)
        documents = {row['path']: row for row in second_engine._documents['research_preparation']}
        self.assertEqual(documents['references/공통-실행.md']['content'], 'edited document\n')

    def test_installation_polling_is_bounded_and_forced_checks_still_detect_edits(self):
        from support.provider_probes import ObservedCalls
        sim, root = self.engine()
        e = sim.engine
        self.assertTrue(callable(e._check_installation))
        e._installation
        with ObservedCalls(manifest=e._installation_manifest) as calls:
            for _ in range(10):
                self.assertTrue(e._check_installation())
            self.assertLessEqual(calls.count('manifest'), 1)
            sim.clock.advance(.999)
            self.assertTrue(e._check_installation())
            self.assertEqual(calls.count('manifest'), 1)
            sim.clock.advance(.002)
            self.assertTrue(e._check_installation())
            self.assertEqual(calls.count('manifest'), 2)
        (root / 'scripts/do_math/engine.py').write_bytes(b'# edited installation\n')
        self.assertFalse(e._check_installation(force=True))
        self.assertEqual(e.runtime['status'], 'paused')

    def test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check(self):
        from do_math import contracts
        from do_math.engine import ResearchEngine
        from do_math.repository import ResearchRepository
        from support.engine_lifecycle import applied
        from support.provider_probes import ObservedCalls
        sim, root = self.engine()
        source = sim.root / 'note.txt'
        source.write_bytes(b'archived source bytes')
        applied(sim, 'source', config={'path': str(source)})
        self.assertTrue(sim.instance['sources'])
        with ObservedCalls(manifest=ResearchEngine._installation_manifest, documents=contracts.all_prompt_documents,
                           read=ResearchRepository.read, many=ResearchRepository.read_many) as calls:
            engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=root, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
            status = engine.status()
        self.assertEqual({name: calls.count(name) for name in calls.calls},
                         {'manifest': 0, 'documents': 0, 'read': 0, 'many': 0})
        self.assertEqual(status['submission_checks']['status'], 'not_evaluated')
        storage = next(area for area in status['inspection']['areas'] if area['name'] == 'record_storage')
        self.assertIn('artifact presence and length', storage['checked_invariants'])
