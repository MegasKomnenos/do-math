"""Discovery of the host installation: the Lean executable and the installed skill files whose hashes name the edition."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import engine as engine_module
from research_fixtures import bare_engine


class ToolDiscoveryTests(unittest.TestCase):
    def test_lean_is_rediscovered_at_most_once_per_second(self):
        engine = bare_engine()
        engine.instance = {'config': {'scholarly_enabled': False, 'scholarly_server': None},
                           'knowledge': {}, 'sources': []}
        engine.runtime = {'tasks': {}}
        clock = [100.0]
        with patch.object(engine_module, 'discover_lean', return_value=['lean']) as discover, \
                patch.object(engine_module.time, 'monotonic', side_effect=lambda: clock[0]):
            for _ in range(5):
                self.assertIn('tool:lean', engine._available_inputs())
            self.assertEqual(discover.call_count, 1)
            discover.return_value = None
            clock[0] += 1.0
            self.assertNotIn('tool:lean', engine._available_inputs())
            self.assertEqual(discover.call_count, 2)

    def test_periodic_installation_check_rehashes_no_unchanged_file(self):
        from do_math import file_io
        # Freshly edited files are not yet settled; age every fingerprint for this check.
        with patch.object(file_io, 'RACY_NS', 0):
            baseline = engine_module.ResearchEngine._installation_manifest()
            # Forget the hashed edition so the full walk runs, not the listing shortcut.
            with patch.object(engine_module, '_HASHED_INSTALLATION', None), \
                    patch.object(file_io, 'sha256_file', side_effect=AssertionError('unchanged file was rehashed')):
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)

    def test_unchanged_installation_listing_reuses_the_hashed_edition(self):
        from do_math import file_io
        with patch.object(file_io, 'RACY_NS', 0), patch.object(engine_module, '_HASHED_INSTALLATION', None):
            baseline = engine_module.ResearchEngine._installation_manifest()
            with patch.object(engine_module, 'reading_map', side_effect=AssertionError('role map reread')):
                self.assertIs(engine_module.ResearchEngine._installation_manifest(), baseline)
            listing = engine_module._HASHED_INSTALLATION[1]
            changed = {**listing, 'scripts/do_math/added.py': (1, 1, 1)}
            with patch.object(engine_module, '_installation_listing', side_effect=[changed, listing]), \
                    patch.object(engine_module, 'reading_map', wraps=engine_module.reading_map) as rebuilt:
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)
            self.assertEqual(rebuilt.call_count, 1)

    def test_installation_listing_reports_added_removed_and_rewritten_files(self):
        import os, tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'scripts' / 'do_math'
            (package / 'sub').mkdir(parents=True)
            (root / 'docs').mkdir()
            for path in (package / 'a.py', package / 'sub' / 'b.py', root / 'docs' / 'x.md', root / 'SKILL.md'):
                path.write_text('v1', encoding='utf-8')
            documents = ('SKILL.md', 'docs/x.md')
            listing = lambda: engine_module._installation_listing(root, documents)
            before = listing()
            self.assertEqual(set(before), {'scripts/do_math/a.py', 'scripts/do_math/sub/b.py', 'SKILL.md', 'docs/x.md'})
            # Files the manifest never hashes do not move the listing.
            (package / '__pycache__').mkdir()
            (package / '__pycache__' / 'a.cpython-312.pyc').write_bytes(b'cache')
            (root / 'docs' / 'unlisted.md').write_text('other', encoding='utf-8')
            self.assertEqual(listing(), before)
            (package / 'new').mkdir()
            (package / 'new' / 'c.py').write_text('v1', encoding='utf-8')
            self.assertEqual(set(listing()) - set(before), {'scripts/do_math/new/c.py'})
            (package / 'new' / 'c.py').unlink()
            (package / 'sub' / 'b.py').unlink()
            self.assertEqual(set(before) - set(listing()), {'scripts/do_math/sub/b.py'})
            for relative in ('docs/x.md', 'scripts/do_math/a.py'):
                path = root / relative
                old = listing()[relative]
                path.write_text('v2', encoding='utf-8')  # same size: only the time moves
                os.utime(path, ns=(old[1] + 10**9, old[1] + 10**9))
                self.assertNotEqual(listing()[relative], old, relative)


if __name__ == "__main__":
    unittest.main()
