"""GitStateStore (layer 2) over the in-process Git fake and the fake clock."""
from datetime import datetime, timezone
import tempfile
import unittest

from support.fakes.git_backend import make_repository
from do_math.git_store import GitStateStore
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake

INSTANCE = 'RI-01M3HM0X0000000000000000AB'


class StoreClockTests(unittest.TestCase):
    def test_batch_metadata_preserves_unicode_path_boundaries_and_rejects_trailing_output(self):
        from do_math.storage_finish_git_output import parse_object_info
        from do_math.ports.git_backend import GitBackendError
        for separator in ('\u0085', '\u2028', '\u2029'):
            spec = 'head:missing' + separator + 'name'
            self.assertEqual(parse_object_info([spec], (spec + ' missing\n').encode()), [None])
        for raw in (b'hash blob 3\nextra', b'hash blob 3\nextra\n'):
            with self.subTest(raw=raw), self.assertRaisesRegex(GitBackendError, '^batch object check response count differs$'):
                parse_object_info(['head:path'], raw)

    def test_a_publication_stamps_its_commit_with_the_clock_port_time(self):
        wall = datetime(2026, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            repository = make_repository(directory)
            backend = make_fake()
            store = GitStateStore(repository, INSTANCE, backend=backend, clock=FakeClock(wall=wall))
            head = store.publish(None, {'research/a.json': b'{}\n', 'runtime/b.json': b'{}\n'}).head
            kind, body = backend.read_objects(repository, [head])[0]
        self.assertEqual(kind, 'commit')
        self.assertIn(f'author do-math <do-math@invalid> {int(wall.timestamp())} '.encode(), body)


if __name__ == '__main__':
    unittest.main()
