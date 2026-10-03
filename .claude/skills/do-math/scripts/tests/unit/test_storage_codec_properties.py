"""1-D: 실제 코덱과 실제 Repository의 생성형 왕복 및 재등장 보존.

예제당 큰 값 둘, 7~9회 게시를 유지한다. 단위 0.2초 초과 가능성은
슬롯 수신 후 실측한다. deadline은 정확성 대신 시간으로 거부하지 않는다.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from hypothesis import example, given, settings

from do_math.initialization import initialize_state
from do_math.canonical import canonical_json, validate_storage_value
from do_math.payloads import LIMIT, decode, encode, seal_large
from do_math.repository import artifact_verified
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.fakes.host import FakeHost
from support.state_builders import current_state, installed_contract
from support.storage_obligations import JSON_VALUES, payload_records, title_sequences
from support.storage_records import INSTANCE_ID, record_store
from support.storage_probes import BuiltinCalls


class CodecProperties(unittest.TestCase):
    def test_new_git_directory_verifies_payload_once_before_fresh_contract_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = InProcessGit()
            writer = record_store(Path(directory) / 'source', backend=backend)
            value = 'A' * LIMIT
            head = writer.initialize(*current_state(runtime={'history': [{'value': value}]}))
            files = writer._store.read_many(head, sorted(writer._store.tree_paths(head)))
            payload = next(path for path in files if path.startswith('runtime/artifacts/payload-'))
            raw, digest = canonical_json(value), hashlib.sha256(canonical_json(value)).hexdigest()
            self.assertEqual(files[payload], raw)
            reader = record_store(Path(directory) / 'receiver', backend=backend, contract=installed_contract())
            # A valid snapshot arrives from another writer in a different Git directory.
            received = reader._store.publish(None, files).head
            self.assertFalse(artifact_verified(reader.git_dir, payload, digest, len(raw)))
            with BuiltinCalls(hashlib.sha256) as hashes:
                loaded = reader.load(received)[2]['history'][0]['value']
            self.assertEqual(canonical_json(loaded), raw)
            self.assertEqual(sum(argument == raw for argument in hashes.arguments), 1)
            self.assertTrue(artifact_verified(reader.git_dir, payload, digest, len(raw)))
            fresh = record_store(Path(directory) / 'receiver', backend=backend, contract=installed_contract())
            with BuiltinCalls(hashlib.sha256) as hashes:
                loaded = fresh.load(received)[2]['history'][0]['value']
            self.assertEqual(canonical_json(loaded), raw)
            self.assertEqual(sum(argument == raw for argument in hashes.arguments), 0)

    @settings(max_examples=20, derandomize=True, deadline=None)
    @example(value=None)
    @example(value=True)
    @example(value=1)
    @example(value=[])
    @example(value=[False, 0, {'nested': [None, '한']}])
    @given(value=JSON_VALUES)
    def test_small_root_values_preserve_type_and_canonical_bytes(self, value):
        raw = canonical_json(value)
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': deepcopy(value)})
        restored = decode(json.loads(canonical_json(envelope)), blobs.__getitem__)
        self.assertIs(type(restored), type(value))
        self.assertEqual(canonical_json(restored), raw)
        self.assertEqual(blobs, {})

    @settings(max_examples=20, derandomize=True, deadline=None)
    @example(value={'z': 'Z' * LIMIT, 'a': 'A' * LIMIT})
    @given(value=payload_records())
    def test_random_key_order_and_multiple_large_values_roundtrip(self, value):
        original = canonical_json(value)
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test',
                                  'record': seal_large(deepcopy(value))})
        restored = decode(json.loads(canonical_json(envelope)), blobs.__getitem__)
        self.assertEqual(restored, value)
        self.assertEqual(canonical_json(restored), original)
        self.assertIsNone(validate_storage_value(restored))
        self.assertEqual(encode({**envelope, 'record': seal_large(deepcopy(restored))}),
                         (envelope, blobs))
        self.assertGreaterEqual(len(blobs), 2)
        for ref in envelope['payloads']:
            leaf = value
            for token in ref['tokens']:
                leaf = leaf[token]
            raw = canonical_json(leaf)
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(ref, {'tokens': ref['tokens'], 'bytes': len(raw), 'sha256': digest,
                                  'path': 'runtime/artifacts/payload-' + digest + '/value.json'})
            self.assertEqual(blobs[ref['path']], raw)

    def test_externalization_uses_canonical_byte_threshold_and_keeps_unicode(self):
        for size in (LIMIT - 1, LIMIT, LIMIT + 1):
            # 따옴표 둘과 마지막 개행의 세 바이트를 포함한 ASCII 경계.
            value = 'a' * (size - 3)
            envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': seal_large(value)})
            self.assertEqual(len(canonical_json(value)), size)
            self.assertEqual(len(blobs), int(size >= LIMIT))
            self.assertEqual(decode(envelope, blobs.__getitem__).encode(), value.encode())
        for token in ('한', 'e\N{COMBINING ACUTE ACCENT}', '\N{KELVIN SIGN}', '"', '\\', '\r\n'):
            value = token * LIMIT
            envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': seal_large(value)})
            self.assertEqual(list(blobs.values()), [canonical_json(value)])
            self.assertEqual(decode(envelope, blobs.__getitem__).encode(), value.encode())

    @settings(max_examples=8, derandomize=True, deadline=None)
    @given(sequence=title_sequences(), value=payload_records())
    def test_every_publication_and_fresh_contract_load_preserves_exact_bytes(self, sequence, value):
        history = [{'evidence': value}]
        for object_format in ('sha1', 'sha256'):
            with self.subTest(object_format=object_format), tempfile.TemporaryDirectory() as directory:
                backend, clock = InProcessGit(), FakeClock()
                repo = record_store(Path(directory), backend=backend, clock=clock, object_format=object_format)
                head = repo.initialize(*initialize_state(instance_id=INSTANCE_ID, goal='G',
                    workspace=Path(directory) / 'work', config={}, source_input='original ' + sequence[0],
                    title='initial', clock=clock, host=FakeHost()))
                first_blobs = None
                for title in sequence:
                    _, instance, runtime = repo.load(head)
                    instance['title'] = title
                    runtime['history'] = deepcopy(history)
                    head, saved_i, saved_r = repo.save_with_state(head, instance, runtime)
                    reader = record_store(Path(directory), backend=backend, clock=clock, contract=installed_contract())
                    loaded_head, loaded_i, loaded_r = reader.load(head)
                    self.assertEqual(loaded_head, head)
                    self.assertEqual(canonical_json(loaded_i['title']), canonical_json(title))
                    self.assertEqual(canonical_json(loaded_r['history']), canonical_json(history))
                    self.assertEqual(canonical_json([loaded_i, loaded_r]), canonical_json([saved_i, saved_r]))
                    reader.contract.validate(loaded_i, loaded_r)
                    self.assertEqual(loaded_i['title'].encode('utf-8'), title.encode('utf-8'))
                    if title == sequence[0]:
                        envelope = json.loads(reader.read('research/_state/metadata.json', head))
                        refs = [row for row in envelope['payloads'] if row['tokens'] == ['title']]
                        self.assertEqual(len(refs), 1)
                        current = reader.read_many([refs[0]['path']], head)
                        self.assertEqual(current, {refs[0]['path']: canonical_json(title)})
                        if first_blobs is None:
                            first_blobs = current
                        else:
                            self.assertEqual(current, first_blobs)


if __name__ == '__main__':
    unittest.main()
