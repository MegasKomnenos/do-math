"""10-B B-27/D-10: Git 포트 계수와 실제 파일 쓰기/해시 결과를 함께 고정한다.

N=1043 파일의 생성·export와 8MiB 경계는 단위 예산 초과 가능성이 있다.
파일 수/바이트 경계를 줄이지 않으며 실행 시간은 슬롯 수신 후 기록한다.
"""
import hashlib
import math
from pathlib import Path
import tempfile
import unittest

from do_math.git_store import GitStateStore
from support.provider_probes import ObservedCalls
from support.state_builders import current_state
from support.storage_files import audit_events
from support.storage_git import ObservedGit
from support.storage_obligations import COST_CASES
from support.storage_probes import BuiltinCalls
from support.storage_records import record_store


class StorageCostCounts(unittest.TestCase):
    def test_query_path_matches_and_pages_hash_only_hydrated_items(self):
        with tempfile.TemporaryDirectory() as directory:
            files = {f'runtime/artifacts/BA-needle/{i}.txt': str(i).encode() for i in range(3)}
            repo, backend, head = self.prepared(Path(directory), files)
            expected = [{'path': path, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                        for path, raw in sorted(files.items())]
            with BuiltinCalls(hashlib.sha256) as hashes:
                first = repo.query(snapshot=head, prefix='runtime/artifacts/BA-needle/', limit=2)
            self.assertEqual(hashes.arguments, list(files.values())[:2])
            self.assertEqual(first['items'], expected[:2])
            self.assertEqual((first['total'], first['truncated']), (3, True))
            with BuiltinCalls(hashlib.sha256) as hashes:
                last = repo.query(prefix='runtime/artifacts/BA-needle/', limit=2, cursor=first['next_cursor'])
            self.assertEqual(hashes.arguments, list(files.values())[2:])
            self.assertEqual(last['items'], expected[2:])
            self.assertEqual((last['snapshot'], last['total'], last['next_cursor'], last['truncated']),
                             (head, 3, None, False))
            with BuiltinCalls(hashlib.sha256) as hashes:
                matched = repo.query(snapshot=head, prefix='runtime/artifacts/BA-needle/', text='needle')
            self.assertEqual(hashes.arguments, list(files.values()))
            self.assertEqual(matched['items'], expected)
            start = len(backend.calls)
            with BuiltinCalls(hashlib.sha256) as hashes:
                empty = repo.query(snapshot=head, prefix='runtime/artifacts/BA-absent/')
            self.assertEqual(empty, {'snapshot': head, 'total': 0, 'items': [],
                                    'next_cursor': None, 'truncated': False})
            self.assertEqual(hashes.arguments, [])
            self.assertNotIn('read_objects', backend.operations(start))

    def prepared(self, root, files):
        backend = ObservedGit()
        writer = record_store(root / 'repo', backend=backend)
        head = writer.initialize(*current_state())
        _, instance, runtime = writer.load(head)
        head = writer.save_with_state(head, instance, runtime, artifacts=files)[0]
        # GitStateStore 트리 캐시가 없는 실제 새 reader. 명시 head로 ref 읽기 제외.
        reader = record_store(root / 'repo', backend=backend)
        return reader, backend, head

    def test_export_count_scales_by_batch_and_writes_every_exact_file(self):
        for count in COST_CASES['B-27']['sizes']:
            with self.subTest(count=count), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                files = {f'runtime/artifacts/BA-cost/{i:04}.bin': i.to_bytes(4, 'big') * 256
                         for i in range(count)}
                repo, backend, head = self.prepared(root, files)
                start = len(backend.calls)
                with audit_events('open') as opened, ObservedCalls(single=GitStateStore.read_bytes) as calls:
                    result = repo.export(root / 'out', head, prefixes=('runtime/artifacts/',))
                operations = backend.operations(start, writes=True)
                self.assertEqual(operations.count('read_objects'), math.ceil(count / 64))
                self.assertEqual(operations.count('object_info'), 1)
                self.assertEqual(operations.count('list_tree'), 1)
                self.assertEqual(len(operations), math.ceil(count / 64) + 2)
                self.assertEqual(calls.count('single'), 0)
                self.assertEqual(result, {'snapshot': head, 'files': sorted(files)})
                output_names = {str(root / 'out' / path) for path in files}
                output_opens = [str(args[0]) for _, args in opened if str(args[0]) in output_names]
                self.assertEqual(sorted(output_opens), sorted(output_names))
                self.assertEqual({path: (root / 'out' / path).read_bytes() for path in files}, files)
                self.assertEqual(repo._store.read_snapshot().head, head)

    def test_export_byte_limit_splits_batches_but_allows_one_oversized_file(self):
        for sizes, expected in (((4 * 1024**2, 4 * 1024**2, 1), (2, 1)),
                                ((8 * 1024**2 + 1, 1), (1, 1))):
            with self.subTest(sizes=sizes), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                files = {f'runtime/artifacts/BA-large/{i}.bin': bytes([65 + i]) * size
                         for i, size in enumerate(sizes)}
                repo, backend, head = self.prepared(root, files)
                start = len(backend.calls)
                with ObservedCalls(batch=GitStateStore.read_many,
                                   capture={'batch': lambda args: list(args['paths'])}) as calls:
                    result = repo.export(root / 'out', head, prefixes=('runtime/artifacts/',))
                batches = calls.captured('batch')
                self.assertEqual(tuple(map(len, batches)), expected)
                self.assertEqual([path for batch in batches for path in batch], sorted(files))
                self.assertEqual(backend.operations(start, writes=True).count('read_objects'), len(expected))
                self.assertEqual(result, {'snapshot': head, 'files': sorted(files)})
                self.assertEqual({path: (root / 'out' / path).read_bytes() for path in files}, files)

    def test_query_counts_reads_and_hashes_without_cached_candidate_inputs(self):
        for count in COST_CASES['D-10']['sizes']:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                files = {f'runtime/artifacts/BA-query/{i:04}.bin': f'needle {i}'.encode()
                         for i in range(count)}
                # Only identical publication is shared. Every text case has a
                # newly constructed real reader with no previous query inputs.
                _, backend, head = self.prepared(root, files)
                for text in ('', 'needle', 'absent'):
                    with self.subTest(count=count, text=text):
                        repo = record_store(root / 'repo', backend=backend)
                        expected = [{'path': path, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                                    for path, raw in sorted(files.items())] if text != 'absent' else []
                        start = len(backend.calls)
                        with BuiltinCalls(hashlib.sha256) as hashes:
                            result = repo.query(snapshot=head, prefix='runtime/artifacts/BA-query/', text=text, limit=count)
                        self.assertEqual(result, {'snapshot': head, 'total': len(expected), 'items': expected,
                                                  'next_cursor': None, 'truncated': False})
                        operations = backend.operations(start, writes=True)
                        self.assertEqual(operations.count('read_objects'), math.ceil(count / 16))
                        self.assertEqual(operations.count('list_tree'), 1)
                        self.assertEqual(len(operations), math.ceil(count / 16) + 1)
                        self.assertEqual(hashes.arguments, list(files.values()) if expected else [])
                        self.assertEqual(repo._store.read_snapshot().head, head)



if __name__ == '__main__':
    unittest.main()
