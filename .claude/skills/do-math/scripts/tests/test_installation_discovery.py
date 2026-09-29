"""Discovery of the host installation: the Lean executable and the installed skill files whose hashes name the edition."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import engine as engine_module
from do_math import core_engine as core_engine_module


class ToolDiscoveryTests(unittest.TestCase):
    def test_periodic_installation_check_rehashes_no_unchanged_file(self):
        from do_math import file_io
        # Freshly edited files are not yet settled; age every fingerprint for this check.
        with patch.object(file_io, 'RACY_NS', 0):
            baseline = engine_module.ResearchEngine._installation_manifest()
            # Forget the hashed edition so the full walk runs, not the listing shortcut.
            with patch.object(core_engine_module, '_HASHED_INSTALLATION', None), \
                    patch.object(file_io, 'sha256_file', side_effect=AssertionError('unchanged file was rehashed')):
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)

    def test_unchanged_installation_listing_reuses_the_hashed_edition(self):
        from do_math import file_io
        with patch.object(file_io, 'RACY_NS', 0), patch.object(core_engine_module, '_HASHED_INSTALLATION', None):
            baseline = engine_module.ResearchEngine._installation_manifest()
            with patch.object(core_engine_module, 'reading_map', side_effect=AssertionError('role map reread')):
                self.assertIs(engine_module.ResearchEngine._installation_manifest(), baseline)
            listing = core_engine_module._HASHED_INSTALLATION[1]
            changed = {**listing, 'scripts/do_math/added.py': (1, 1, 1)}
            with patch.object(core_engine_module, '_installation_listing', side_effect=[changed, listing]), \
                    patch.object(core_engine_module, 'reading_map', wraps=core_engine_module.reading_map) as rebuilt:
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)
            self.assertEqual(rebuilt.call_count, 1)


if __name__ == "__main__":
    unittest.main()
