"""B-27/D-10의 실제 Git 자식 프로세스 수. 포트 호출 계수와 별도 증거다."""
import math
from pathlib import Path
import tempfile
import unittest

from do_math.git_process import GitProcess
from support.fakes.clock import FakeClock
from support.entry import entry
from support.state_builders import current_state
from support.storage_files import audit_events
from support.storage_records import record_store


class BatchProcessCounts(unittest.TestCase):
    def test_export_and_query_start_one_git_child_per_batch(self):
        for count in (3, 200, 1043):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                backend, clock = GitProcess(environment=entry().environment), FakeClock()
                writer = record_store(root / 'repo', backend=backend, clock=clock)
                head = writer.initialize(*current_state())
                _, instance, runtime = writer.load(head)
                files = {f'runtime/artifacts/BA-process/{i:04}.txt': f'needle {i}'.encode() for i in range(count)}
                head = writer.save_with_state(head, instance, runtime, artifacts=files)[0]
                reader = record_store(root / 'repo', backend=backend, clock=clock)
                with audit_events('subprocess.Popen') as processes:
                    exported = reader.export(root / 'out', head, prefixes=('runtime/artifacts/BA-process/',))
                self.assertEqual(len(processes), math.ceil(count / 64) + 2)
                self.assertEqual(exported, {'snapshot': head, 'files': sorted(files)})
                self.assertEqual({name: (root / 'out' / name).read_bytes() for name in files}, files)
                reader = record_store(root / 'repo', backend=backend, clock=clock)
                with audit_events('subprocess.Popen') as processes:
                    result = reader.query(snapshot=head, prefix='runtime/artifacts/BA-process/', text='needle', limit=count)
                self.assertEqual(len(processes), math.ceil(count / 16) + 1)
                self.assertEqual([item['path'] for item in result['items']], sorted(files))
                self.assertEqual((result['total'], result['next_cursor'], result['truncated']), (count, None, False))


if __name__ == '__main__':
    unittest.main()
