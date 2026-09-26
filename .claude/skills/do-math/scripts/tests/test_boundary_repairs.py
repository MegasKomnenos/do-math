"""Regression tests for state/evidence boundaries found in the September audit."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import ResearchRepository, new_id
from do_math.payloads import decode, encode, seal_large
from do_math.repository import canonical_json
from research_fixtures import current_state
from test_categories import test_group


class PayloadCodecTests(unittest.TestCase):
    def test_multiple_payload_references_follow_canonical_key_order(self):
        value = {'z': 'z' * 70000, 'a': 'a' * 70000}
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': seal_large(value)})
        stored = json.loads(canonical_json(envelope))
        self.assertEqual([row['tokens'] for row in stored['payloads']], [['a'], ['z']])
        self.assertEqual(decode(stored, lambda path: blobs[path]), value)


@test_group('integration')
class PayloadPublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        self.repo = ResearchRepository(root, new_id('RI'))
        self.head = self.repo.initialize(*current_state({'title': 'initial'}))

    def test_unreferenced_payload_can_be_reused_without_rewriting_the_blob(self):
        for value in ('exact 원문\n' * 20000,
                      {'foundation_profile': {}, 'files': ['source'] * 20000}):
            with self.subTest(type=type(value).__name__):
                key = 'title' if isinstance(value, str) else 'manifest'
                if key == 'manifest':
                    self.repo.register_family('research', key, shape='metadata',
                        schema={'type': ['object', 'null']}, identity=False)
                _, instance, runtime = self.repo.load()
                instance[key] = value
                head, instance, runtime = self.repo.save_with_state(self.repo.load()[0], instance, runtime)
                paths = [p for p in self.repo.list_files('runtime/artifacts/', head)
                         if p.startswith('runtime/artifacts/payload-')]
                original = self.repo.read_many(paths, head)
                instance[key] = 'short' if key == 'title' else None
                head, instance, runtime = self.repo.save_with_state(head, instance, runtime)
                instance[key] = value
                head, instance, runtime = self.repo.save_with_state(head, instance, runtime)
                self.assertEqual(self.repo.load(head)[1][key], value)
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


if __name__ == '__main__':
    unittest.main()
