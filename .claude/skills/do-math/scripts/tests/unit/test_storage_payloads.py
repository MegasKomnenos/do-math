"""Payload references and payload blobs (``payloads``, layer 2): canonical reference order, blob reuse and collision rejection.

The codec is called directly. Publication runs the real ``ResearchRepository``
on the Git port's in-process fake (설계 4.3); the store's Git reads are counted
by observing ``GitStateStore.read_many`` (``ObservedCalls``), not by replacing it.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math import payloads
from do_math.canonical import canonical_json
from do_math.git_store import GitStateStore
from do_math.payloads import decode, encode, seal_large
from support.state_builders import current_state, installed_contract
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_probes import ObservedCalls
from support.storage_records import record_store


class PayloadCodecTests(unittest.TestCase):
    def test_multiple_payload_references_follow_canonical_key_order(self):
        value = {'z': 'z' * 70000, 'a': 'a' * 70000}
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': seal_large(value)})
        stored = json.loads(canonical_json(envelope))
        self.assertEqual([row['tokens'] for row in stored['payloads']], [['a'], ['z']])
        self.assertEqual(decode(stored, lambda path: blobs[path]), value)


class PayloadPublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = record_store(Path(temporary.name))
        self.head = self.repo.initialize(*current_state({'title': 'initial'}))

    def payload_candidate(self):
        """``(instance, runtime, path, raw)``: a state whose large title is a payload blob at ``path`` with bytes ``raw``."""
        _, instance, runtime = self.repo.load()
        instance['title'] = 'new exact 원문\n' * 20000
        candidate = self.repo.validate_candidate(instance, runtime, self.head)
        path = next(p for p in candidate['files'] if p.startswith('runtime/artifacts/'))
        return instance, runtime, path, candidate['files'][path]

    def test_unreferenced_payload_can_be_reused_without_rewriting_the_blob(self):
        value = 'exact 원문\n' * 20000
        _, instance, runtime = self.repo.load()
        instance['title'] = value
        head, instance, runtime = self.repo.save_with_state(self.repo.load()[0], instance, runtime)
        paths = [p for p in self.repo.list_files('runtime/artifacts/', head)
                 if p.startswith('runtime/artifacts/payload-')]
        original = self.repo.read_many(paths, head)
        instance['title'] = 'short'
        head, instance, runtime = self.repo.save_with_state(head, instance, runtime)
        instance['title'] = value
        head, instance, runtime = self.repo.save_with_state(head, instance, runtime)
        self.assertEqual(self.repo.load(head)[1]['title'], value)
        self.assertEqual(self.repo.read_many(paths, head), original)

    def test_payload_collision_is_rejected_by_validation_and_publication_before_cas(self):
        instance, runtime, path, _ = self.payload_candidate()
        for boundary in (self.repo.validate_candidate,
                         lambda i, r, h, **kw: self.repo.save_with_state(h, i, r, **kw)):
            with self.subTest(boundary=boundary), self.assertRaisesRegex(
                    ValueError, '^immutable artifact differs from encoded state: ' + re.escape(path) + '$'):
                boundary(instance, runtime, self.head, artifacts={path: b'different bytes'})
        self.assertEqual(self.repo._store.read_snapshot().head, self.head)

    def test_matching_payload_and_separate_artifact_publish_exact_validated_bytes(self):
        instance, runtime, path, raw = self.payload_candidate()
        head, normalized, saved = self.repo.save_with_state(self.head, instance, runtime,
            artifacts={path: raw, 'runtime/artifacts/BA-new/result.txt': b'result'})
        self.assertEqual(self.repo.load(head), (head, normalized, saved))
        self.assertEqual(self.repo.read(path, head), raw)
        with self.assertRaisesRegex(ValueError, '^immutable artifact differs from encoded state: ' + re.escape(path) + '$'):
            self.repo.save_with_state(head, normalized, saved, artifacts={path: b'changed'})


class PayloadEncodingTests(unittest.TestCase):
    def test_payloads_are_exact_shared_and_immutable(self):
        text = '원문 코드포인트\n' * 20000
        value = payloads.seal_large({'title': text, 'source': {'text': text}})
        envelope = {'contract_id': 'test', 'family': 'test', 'record': value}
        encoded, blobs = payloads.encode(envelope)
        self.assertEqual(len(blobs), 1)
        self.assertLess(len(canonical_json(encoded)), 1500)

        def read(path):
            return blobs[path]
        read.decoded = {}
        restored = payloads.decode(encoded, read)
        self.assertEqual(restored, value)
        self.assertTrue(restored['title'] is restored['source']['text'], 'one immutable value should be shared')
        bad = deepcopy(encoded)
        bad['payloads'][0]['sha256'] = '0' * 64
        # The reference's path names the old digest, so the reference itself is refused.
        with self.assertRaisesRegex(ValueError, '^invalid immutable payload reference$'):
            payloads.decode(bad, read)


class PayloadStorageTests(unittest.TestCase):
    def test_large_payload_storage_and_cached_parent_remain_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Both repository objects read the same Git objects.
            backend, clock = InProcessGit(), FakeClock()

            def labelled():
                contract = installed_contract()
                contract.register_family('research', 'label', shape='metadata', schema={'type': 'string'}, identity=False)
                return contract
            repo = record_store(root, contract=labelled(), backend=backend, clock=clock)
            text = 'exact 원문\n' * 20000
            head = repo.initialize(*current_state({'title': text, 'label': text}))
            stored = json.loads(repo.read('research/_state/metadata.json', head))
            self.assertIsNone(stored['record']['title'])
            self.assertEqual(len({r['path'] for r in stored['payloads']}), 1)
            _, instance, runtime = repo.load(head)
            self.assertEqual(instance['title'], text)
            # Decoding (a head this repository object did not publish) shares one value per payload.
            reader = record_store(root, contract=labelled(), backend=backend, clock=clock)
            with ObservedCalls(read_many=GitStateStore.read_many) as reads:
                decoded = reader.load(head)[1]
            self.assertTrue(decoded['title'] is decoded['label'], 'decoded values should share immutable bytes')
            # The observation sees the parent read of a head published elsewhere (the second contract's cache).
            self.assertEqual([call['commit'] for call in reads.captured('read_many')], [head])
            with ObservedCalls(read_many=GitStateStore.read_many) as reads:
                new_head, new_i, new_r = repo.save_with_state(head, instance, {**runtime, 'status': 'ready'})
            self.assertEqual([call['commit'] for call in reads.captured('read_many') if call['commit'] == head], [])
            self.assertEqual(repo.load(new_head), (new_head, new_i, new_r))
            instance['title'] = 'caller mutation'
            self.assertEqual(repo.load(head)[1]['title'], text)
            self.assertEqual(repo.read(stored['payloads'][0]['path'], head),
                             repo.read(stored['payloads'][0]['path'], new_head))


if __name__ == '__main__':
    unittest.main()
