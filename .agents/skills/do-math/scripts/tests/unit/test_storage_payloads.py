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
    def test_object_editions_share_key_paths_without_repeating_the_coordinate_table(self):
        source = {f'source-{i}': f'exact source row {i}' for i in range(32)}
        blobs, refs = {}, {}
        for index in range(1, 17):
            # Insert in reverse lexical order: prefix-sharing a sorted flat
            # table would copy its suffix at every insertion.
            key = f'coordinate-{17 - index:02d}'
            refs[key] = source
            envelope, nodes = encode({'contract_id': 'test', 'family': 'delegation_applications',
                'record': {'id': 'DA', 'basis': deepcopy(refs)}})
            blobs.update(nodes)
            self.assertEqual(decode(envelope, blobs.__getitem__)['basis'], refs)
        leaves = [json.loads(raw) for path, raw in blobs.items() if '/snapshot-' in path]
        coordinates = [row['key'] for row in leaves if 'key' in row and row['key'].startswith('coordinate-')]
        self.assertEqual(sorted(coordinates), sorted(refs))
        # A full-key trie has at most nine nodes per UTF-8 key byte plus one
        # for each new coordinate, independent of the referenced source size.
        self.assertLessEqual(len(leaves), 9 * sum(len(key.encode()) for key in [*source, *refs]) + 2)

    def test_structural_fanout_shares_small_rows_and_restores_independent_values(self):
        """About 10 s exceeds 0.2 s: full structured fanout is encoded and decoded.

        This checks logical bytes and detached values, not execution speed.
        """
        # No string reaches LIMIT. The independent input is made once, before
        # any repeated basis, owner or pending-seat coordinates are produced.
        source = {'rows': [{'id': f'row-{i}', 'text': f'exact 원천 {i}', 'flags': [True, None, i]}
                           for i in range(256)]}
        source_bytes = len(canonical_json(source))
        for count in (1, 8):
            blobs, envelopes = {}, []
            for index in range(count):
                for family, record in (
                    ('delegation_applications', {'id': f'DA-{index}', 'basis': {'target': source, 'references': {'KN': source}}}),
                    ('intent_imports', {'id': f'II-{index}', 'owner_basis': {'unit': source},
                                       'application': {'post_owner_basis': {'unit': source}}}),
                    ('review_inputs', {f'seat-{index}': {'proposal': source, 'restored_messages': [source]}})):
                    envelope, added = encode({'contract_id': 'test', 'family': family, 'record': deepcopy(record)})
                    blobs.update(added)
                    envelopes.append((envelope, record))
            # Node cells, child hashes and list links: <= 32 source bytes per
            # byte of these short input rows; 4096 for the six fanout roots per
            # index. Constants come from this encoding, not Git compression.
            self.assertLessEqual(sum(map(len, blobs.values())) + sum(len(canonical_json(e)) for e, _ in envelopes),
                                 32 * source_bytes + 4096 * count)
            print('R22 codec bytes', {'references': count, 'source': source_bytes,
                'logical': sum(map(len, blobs.values())) + sum(len(canonical_json(e)) for e, _ in envelopes),
                'bound': 32 * source_bytes + 4096 * count})
            for envelope, expected in envelopes:
                restored = decode(envelope, blobs.__getitem__)
                self.assertEqual(restored, expected)
            restored = decode(envelopes[0][0], blobs.__getitem__)
            restored['basis']['target']['rows'][0]['text'] = 'mutated'
            self.assertEqual(restored['basis']['references']['KN'], source)
            self.assertEqual(decode(envelopes[0][0], blobs.__getitem__), envelopes[0][1])
            # Exact source markers occur once across all graph node blobs.
            for index in range(256):
                marker = canonical_json(f'exact 원천 {index}').strip()
                self.assertEqual(sum(raw.count(marker) for raw in blobs.values()), 1)

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
        # A graph's text cell shares the existing large-text blob with an
        # ordinary leaf; structural sharing must not inline that original.
        mixed = payloads.seal_large({'id': 'DA', 'title': text, 'basis': {'large': text}})
        graph, graph_blobs = payloads.encode({'contract_id': 'test', 'family': 'delegation_applications', 'record': mixed})
        self.assertEqual(sum('/payload-' in path for path in graph_blobs), 1)
        self.assertEqual(payloads.decode(graph, graph_blobs.__getitem__), mixed)


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
            # One batch reads record files; one reads the distinct payload.
            self.assertEqual([call['commit'] for call in reads.captured('read_many')], [head, head])
            self.assertEqual(reads.captured('read_many')[1]['paths'], [stored['payloads'][0]['path']])
            with ObservedCalls(read_many=GitStateStore.read_many) as reads:
                new_head, new_i, new_r = repo.save_with_state(head, instance, {**runtime, 'status': 'ready'})
            self.assertEqual([call['commit'] for call in reads.captured('read_many') if call['commit'] == head], [])
            self.assertEqual(repo.load(new_head), (new_head, new_i, new_r))
            instance['title'] = 'caller mutation'
            self.assertEqual(repo.load(head)[1]['title'], text)
            self.assertEqual(repo.read(stored['payloads'][0]['path'], head),
                             repo.read(stored['payloads'][0]['path'], new_head))


    def test_damaged_unreferenced_payload_blocks_reappearance_before_object_write_or_cas(self):
        from do_math.canonical import FrozenText
        from support.storage_git import ObservedGit, rewrite_commit

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend = ObservedGit()
            repo = record_store(root, backend=backend)
            value = 'exact 원문\n' * 20000
            first = repo.initialize(*current_state({'title': value}))
            paths = repo.list_files('runtime/artifacts/', first)
            self.assertEqual(len(paths), 1)
            path, = paths
            original = repo.read(path, first)
            self.assertIs(type(original), bytes)
            self.assertEqual(original, canonical_json(value))
            _, instance, runtime = repo.load(first)
            self.assertIs(type(instance['title']), FrozenText)
            instance['title'] = 'short'
            second = repo.save_with_state(first, instance, runtime)[0]
            damaged = rewrite_commit(repo, second, {path: b'corrupted archive\n'})
            reader = record_store(root, backend=backend, contract=installed_contract())
            _, instance, runtime = reader.load(damaged)
            self.assertEqual(instance['title'], 'short')
            instance['title'] = value
            caller = canonical_json([instance, runtime])
            start = len(backend.calls)
            with self.assertRaises(ValueError) as caught:
                reader.save_with_state(damaged, instance, runtime)
            self.assertIs(type(caught.exception), ValueError)
            self.assertEqual(str(caught.exception), 'immutable artifact differs from encoded state: ' + path)
            self.assertEqual([name for name, _ in backend.calls[start:]
                              if name in {'write_object', 'update_ref'}], [])
            self.assertEqual(backend.artifact_specs('read_objects', start), [[damaged + ':' + path]])
            self.assertEqual(reader.load()[0], damaged)
            self.assertEqual(reader.load()[1]['title'], 'short')
            self.assertEqual(reader.read_many([path], damaged), {path: b'corrupted archive\n'})
            self.assertEqual(reader.read_many([path], first), {path: original})
            self.assertEqual(canonical_json([instance, runtime]), caller)


if __name__ == '__main__':
    unittest.main()
