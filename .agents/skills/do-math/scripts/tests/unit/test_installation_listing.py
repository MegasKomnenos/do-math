"""The installation listing (``core_engine._installation_listing``, layer 2): the files an edition hashes, by fingerprint."""
import os
from pathlib import Path
import tempfile
import unittest

from do_math.core_engine import _installation_listing


class InstallationListingTests(unittest.TestCase):
    def test_installation_listing_reports_added_removed_and_rewritten_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'scripts' / 'do_math'
            (package / 'sub').mkdir(parents=True)
            (root / 'docs').mkdir()
            for path in (package / 'a.py', package / 'sub' / 'b.py', root / 'docs' / 'x.md', root / 'SKILL.md'):
                path.write_text('v1', encoding='utf-8')
            documents = ('SKILL.md', 'docs/x.md')

            def listing():
                return _installation_listing(root, documents)
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


if __name__ == '__main__':
    unittest.main()
