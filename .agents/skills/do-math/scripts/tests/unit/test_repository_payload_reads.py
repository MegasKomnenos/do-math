"""Batched restoration keeps exact snapshots and the payload trust boundary."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.git_store import GitStateStoreError
from support.storage_records import record_store
from support.storage_snapshot_cases import fresh_reader, payload_state, snapshot_files


class RepositoryPayloadReads(unittest.TestCase):
    def test_reachable_bytes_and_detached_values_are_exact_across_editions(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = record_store(Path(directory))
            original = payload_state()
            first = writer.initialize(*original)
            _, instance, runtime = writer.load(first)
            instance['title'] = 'later edition'
            later = writer.save_with_state(first, instance, runtime,
                artifacts={'runtime/artifacts/BA-unrelated/unused.bin': b'never needed'})[0]
            reader = fresh_reader(writer)
            self.assertEqual(reader.load(first)[1:], original)
            restored = reader.load(later)
            self.assertEqual(restored[1]['title'], 'later edition')
            self.assertEqual(restored[2], original[1])
            retained = reader._read_documents(later)[3]
            self.assertNotIn('runtime/artifacts/BA-unrelated/unused.bin', retained)
            persisted = snapshot_files(writer, later)
            self.assertEqual(retained, {p: persisted[p] for p in retained})
            restored[2]['review_inputs']['seat']['proposal']['rows'][0]['flags'][0] = False
            self.assertTrue(restored[2]['review_inputs']['seat']['request']['same']['rows'][0]['flags'][0])
            self.assertEqual(reader.load(first)[1:], original)

    def test_missing_corrupt_and_noncanonical_references_reject_on_real_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = record_store(Path(directory) / 'original')
            head = writer.initialize(*payload_state(2))
            files = snapshot_files(writer, head)
            text_path = next(p for p in files if '/payload-' in p)
            node_path = next(p for p in files if '/snapshot-' in p)
            mutations = [('missing text', {text_path: None}, GitStateStoreError, 'batch read did not return a blob'),
                         ('missing node', {node_path: None}, GitStateStoreError, 'batch read did not return a blob'),
                         ('corrupt text', {text_path: b'wrong'}, ValueError, 'immutable payload bytes differ'),
                         ('corrupt node', {node_path: b'wrong'}, ValueError, 'immutable snapshot bytes differ')]
            record_path = 'runtime/inputs/UI-payload-0.json'
            envelope = json.loads(files[record_path])
            envelope['payloads'][0]['bytes'] += 1
            mutations.append(('wrong size', {record_path: canonical_json(envelope)}, ValueError, 'immutable payload bytes differ'))
            envelope = json.loads(files[record_path])
            envelope['payloads'][0]['path'] = 'runtime/artifacts/../outside'
            mutations.append(('invalid path', {record_path: canonical_json(envelope)}, ValueError, 'invalid immutable payload reference'))
            # A hash-matched blob still has to be canonical JSON.
            envelope = json.loads(files[record_path])
            ref = envelope['payloads'][0]
            raw = b' ' + files[ref['path']]
            digest = hashlib.sha256(raw).hexdigest()
            ref.update(path=f'runtime/artifacts/payload-{digest}/value.json', sha256=digest, bytes=len(raw))
            mutations.append(('noncanonical text', {record_path: canonical_json(envelope), ref['path']: raw},
                              ValueError, 'noncanonical immutable payload'))
            # Hash-matched but malformed snapshot nodes cannot supply children.
            record_path = 'runtime/review_inputs/state.json'
            envelope = json.loads(files[record_path])
            ref = envelope['payloads'][0]
            raw = canonical_json({'kind': 'object', 'key': 'broken', 'value': ['node', 'invalid-hash']})
            digest = hashlib.sha256(raw).hexdigest()
            ref.update(path=f'runtime/artifacts/snapshot-{digest}/value.json', sha256=digest, bytes=len(raw))
            mutations.append(('malformed child', {record_path: canonical_json(envelope), ref['path']: raw},
                              ValueError, 'invalid snapshot node reference'))
            for index, (label, changes, error_type, reason) in enumerate(mutations):
                with self.subTest(label=label):
                    # A fresh repository prevents a prior verified artifact or
                    # validated head from concealing hostile external bytes.
                    bad = record_store(Path(directory) / f'bad-{index}')
                    changed = deepcopy(files)
                    for path, replacement in changes.items():
                        if replacement is None:
                            del changed[path]
                        else:
                            changed[path] = replacement
                    bad_head = bad._store.publish(None, changed).head
                    with self.assertRaisesRegex(error_type, '^' + reason):
                        bad.load(bad_head)


if __name__ == '__main__':
    unittest.main()
