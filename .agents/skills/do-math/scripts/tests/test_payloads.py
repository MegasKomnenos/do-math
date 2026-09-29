"""Payload references and payload blobs: canonical reference order, blob reuse and collision rejection before publication."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import ResearchRepository
from do_math.system_clock import new_id
from do_math.payloads import decode, encode, seal_large
from do_math.canonical import canonical_json
from copy import deepcopy
from unittest.mock import patch
from do_math import payloads
from research_fixtures import current_state, git_init, installed_contract

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
        root = Path(temporary.name)
        git_init(root)
        self.repo = ResearchRepository(root, new_id('RI'))
        self.head = self.repo.initialize(*current_state({'title': 'initial'}))

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
        _, instance, runtime = self.repo.load()
        instance['title'] = 'new exact 원문\n' * 20000
        candidate = self.repo.validate_candidate(instance, runtime, self.head)
        path = next(p for p in candidate['files'] if p.startswith('runtime/artifacts/'))
        for boundary in (self.repo.validate_candidate,
                         lambda i, r, h, **kw: self.repo.save_with_state(h, i, r, **kw)):
            with self.subTest(boundary=boundary), self.assertRaisesRegex(ValueError, 'artifact.*differs|collision'):
                boundary(instance, runtime, self.head, artifacts={path: b'different bytes'})
        self.assertEqual(self.repo._store.read_snapshot().head, self.head)

    def test_matching_payload_and_separate_artifact_publish_exact_validated_bytes(self):
        _, instance, runtime = self.repo.load()
        instance['title'] = 'new exact 원문\n' * 20000
        candidate = self.repo.validate_candidate(instance, runtime, self.head)
        path = next(p for p in candidate['files'] if p.startswith('runtime/artifacts/'))
        raw = candidate['files'][path]
        head, normalized, saved = self.repo.save_with_state(self.head, instance, runtime,
            artifacts={path: raw, 'runtime/artifacts/BA-new/result.txt': b'result'})
        self.assertEqual(self.repo.load(head), (head, normalized, saved))
        self.assertEqual(self.repo.read(path, head), raw)
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.repo.save_with_state(head, normalized, saved, artifacts={path: b'changed'})


class PayloadEncodingTests(unittest.TestCase):
    def test_payloads_are_exact_shared_and_immutable(self):
        text = '원문 코드포인트\n' * 20000
        value = payloads.seal_large({'title':text, 'source':{'text':text}})
        envelope={'contract_id':'test','family':'test','record':value}
        encoded, blobs=payloads.encode(envelope)
        self.assertEqual(len(blobs), 1)
        self.assertLess(len(canonical_json(encoded)), 1500)
        def read(path): return blobs[path]
        read.decoded={}
        restored=payloads.decode(encoded, read)
        self.assertEqual(restored, value)
        self.assertTrue(restored['title'] is restored['source']['text'], 'one immutable value should be shared')
        bad = deepcopy(encoded)
        bad['payloads'][0]['sha256']='0'*64
        with self.assertRaises(ValueError): payloads.decode(bad, read)


class PayloadStorageTests(unittest.TestCase):
    def test_large_payload_storage_and_cached_parent_remain_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            git_init(root)
            identifier=new_id('RI')
            def labelled():
                contract=installed_contract()
                contract.register_family('research','label',shape='metadata',schema={'type':'string'},identity=False)
                return contract
            repo=ResearchRepository(root,identifier,contract=labelled())
            text='exact 원문\n'*20000
            head=repo.initialize(*current_state({'title':text,'label':text}))
            stored=json.loads(repo.read('research/_state/metadata.json',head))
            self.assertIsNone(stored['record']['title'])
            self.assertEqual(len({r['path'] for r in stored['payloads']}),1)
            _, instance, runtime=repo.load(head)
            self.assertEqual(instance['title'],text)
            # Decoding (a head this repository object did not publish) shares one value per payload.
            reader=ResearchRepository(root,identifier,contract=labelled())
            decoded=reader.load(head)[1]
            self.assertTrue(decoded['title'] is decoded['label'], 'decoded values should share immutable bytes')
            with patch.object(repo._store,'read_many',wraps=repo._store.read_many) as reads:
                new_head, new_i, new_r=repo.save_with_state(head,instance,{**runtime,'status':'ready'})
            self.assertEqual(len([c for c in reads.call_args_list if c.args[0]==head]),0)
            self.assertEqual(repo.load(new_head),(new_head,new_i,new_r))
            instance['title']='caller mutation'
            self.assertEqual(repo.load(head)[1]['title'],text)
            self.assertEqual(repo.read(stored['payloads'][0]['path'],head),repo.read(stored['payloads'][0]['path'],new_head))


if __name__ == "__main__":
    unittest.main()
