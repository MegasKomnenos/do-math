"""The frozen supervisor copy's fingerprint cache, called in process (``operator_bootstrap``, layer 3).

This sits with the flows because the scenario itself outlasts the 2 s budget of
a layer-3 test: freezing copies and hashes the whole installed skill.
``verify_snapshot`` checks a frozen supervisor copy before any of its code is
imported. After a first full verification it keeps the settled file
fingerprints beside the manifest and hashes a file again only when its
fingerprint changed. A fresh copy's file times are too recent to count as
settled, so the test moves them into the past (``settle``) instead of changing
the product's racy window; the hash calls are observed on the unchanged product.
"""
import json
from pathlib import Path
import tempfile
import unittest

import operator_bootstrap as bootstrap
from do_math import file_io
from support.provider_probes import ObservedCalls, settle


SKILL = Path(file_io.__file__).resolve().parents[2]


class FrozenSnapshotTests(unittest.TestCase):
    def test_verified_frozen_files_are_rehashed_only_after_their_fingerprint_changes(self):
        """About 3 s: freezing copies and hashes the whole installed skill, which is the subject of the check."""
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(bootstrap.freeze(SKILL, Path(directory))['manifest'])
            snapshot = manifest.parent
            files = json.loads(manifest.read_text(encoding='utf-8'))['files']
            for name in files:
                settle(snapshot / name)
            bootstrap.verify_snapshot(manifest)
            self.assertTrue((snapshot / bootstrap.MARKS).is_file())
            self.assertEqual(set(json.loads((snapshot / bootstrap.MARKS).read_text(encoding='utf-8'))), set(files))
            with ObservedCalls(hashed=file_io.sha256_file) as observed:
                bootstrap.verify_snapshot(manifest)
            self.assertEqual(observed.count('hashed'), 0, 'an unchanged frozen file was rehashed')
            changed = snapshot / 'scripts/do_math/repository.py'
            changed.write_text('changed\n', encoding='utf-8')
            # Settled as well, so the changed fingerprint alone, not a fresh file time, forces the rehash.
            settle(changed)
            with ObservedCalls(hashed=file_io.sha256_file) as observed:
                with self.assertRaisesRegex(ValueError, 'bootstrap file hash mismatch: scripts/do_math/repository.py'):
                    bootstrap.verify_snapshot(manifest)
            self.assertEqual([Path(row['path']) for row in observed.captured('hashed')], [changed])


if __name__ == '__main__':
    unittest.main()
