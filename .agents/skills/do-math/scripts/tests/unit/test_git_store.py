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
