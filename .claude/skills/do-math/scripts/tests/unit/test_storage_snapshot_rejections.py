"""정상 Git snapshot의 한 문서만 훼손해 실제 Repository 적재의 반려를 확인한다."""
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.repository import RepositoryCursorError, _encode_cursor
from support.fakes.git_backend import InProcessGit
from support.state_builders import current_state, installed_contract
from support.storage_git import rewrite_commit
from support.storage_records import record_store


class SnapshotRejections(unittest.TestCase):
    def test_root_manifest_and_metadata_damage_reaches_actual_loader(self):
        cases = (
            ('manifest', 'remove', None, 'missing family manifest: research'),
            ('manifest', 'contract', {}, 'unsupported stored contract/schema version or manifest'),
            ('manifest', 'object_format', 'sha256', 'snapshot object_format differs from Git'),
            ('manifest', 'containers', [], 'invalid family manifest containers'),
            ('metadata', 'remove', None, 'missing root metadata record: research'),
            ('metadata', 'family', 'other', 'invalid root metadata envelope: research'),
            ('metadata', 'record', [], 'invalid root metadata envelope: research'),
        )
        for document, field, value, reason in cases:
            with self.subTest(document=document, field=field), tempfile.TemporaryDirectory() as directory:
                backend = InProcessGit()
                repo = record_store(Path(directory), backend=backend)
                head = repo.initialize(*current_state({'title': 'original'}))
                self.assertEqual(repo.load(head)[1]['title'], 'original')
                path = f'research/_state/{document}.json'
                original = repo.read(path, head)
                row = json.loads(original)
                row[field] = value
                damaged = rewrite_commit(repo, head, {path: None if field == 'remove' else canonical_json(row)})
                reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    reader.load(damaged)
                self.assertEqual(reader.read(path, head), original)
                self.assertEqual(reader._store.read_snapshot().head, damaged)

    def test_declared_family_membership_and_record_identity_are_checked(self):
        cases = (
            ('unknown', {'shape': 'map', 'ids': []}, None, 'unregistered manifest family: unknown'),
            ('inputs', None, None, 'unregistered manifest family: inputs'),
            ('inputs', {'shape': 'map', 'ids': ['UI-fixture']}, None, 'manifest shape differs from registered family: inputs'),
            ('inputs', {'shape': 'list', 'ids': [True]}, None, 'invalid family membership: inputs'),
            ('inputs', {'shape': 'list', 'ids': 'UI-fixture'}, None, 'invalid family membership: inputs'),
            ('inputs', {'shape': 'list', 'ids': ['UI-fixture'], 'extra': 0}, None, 'invalid family membership: inputs'),
            ('history', {'shape': 'singleton', 'id': 'extra'}, None, 'invalid family membership: history'),
            ('inputs', {'shape': 'list', 'ids': ['UI-fixture', 'UI-fixture']}, None, 'invalid family membership: inputs'),
            ('inputs', {'shape': 'list', 'ids': ['UI-absent']}, None,
             'missing registered record file: runtime/inputs/UI-absent.json'),
            ('inputs', {'shape': 'list', 'ids': ['UI-fixture']}, ('family', 'other'),
             'invalid record envelope: runtime/inputs/UI-fixture.json'),
            ('inputs', {'shape': 'list', 'ids': ['UI-fixture']}, ('id', 'UI-other'),
             'record path and id differ: runtime/inputs/UI-fixture.json'),
        )
        for family, descriptor, change, reason in cases:
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                backend = InProcessGit()
                repo = record_store(Path(directory), backend=backend)
                head = repo.initialize(*current_state())
                path = 'runtime/_state/manifest.json'
                manifest = json.loads(repo.read(path, head))
                manifest['containers'][family] = descriptor
                changes = {path: canonical_json(manifest)}
                if change:
                    record_path = 'runtime/inputs/UI-fixture.json'
                    row = json.loads(repo.read(record_path, head))
                    if change[0] == 'id':
                        row['record']['id'] = change[1]
                    else:
                        row[change[0]] = change[1]
                    changes[record_path] = canonical_json(row)
                damaged = rewrite_commit(repo, head, changes)
                reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    reader.load(damaged)
                self.assertEqual(reader.load(head)[2]['inputs'][0]['id'], 'UI-fixture')

    def test_strict_json_and_cursor_shapes_fail_with_distinct_reasons(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = InProcessGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state())
            path = 'research/_state/metadata.json'
            for raw, reason in ((b'\xff', 'stored document is not strict JSON'),
                                (b'[]\n', 'stored instance and runtime documents must be JSON objects'),
                                (b'{}', 'stored document is not canonical JSON')):
                damaged = rewrite_commit(repo, repo._store.read_snapshot().head, {path: raw})
                reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    reader.load(damaged)
            for cursor, reason in (('', 'cursor must be a non-empty string'),
                                   ('!!!', 'cursor is malformed'),
                                   (_encode_cursor({'wrong': 'shape'}), 'cursor has an invalid shape')):
                with self.subTest(cursor=cursor), self.assertRaisesRegex(RepositoryCursorError, '^' + reason + '$'):
                    repo.query(snapshot=head, cursor=cursor)


    def test_metadata_descriptor_and_undeclared_file_damage_preserve_original_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = InProcessGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state({'title': '원본'}))
            metadata_path = 'research/_state/metadata.json'
            manifest_path = 'research/_state/manifest.json'
            metadata_raw = repo.read(metadata_path, head)
            manifest = json.loads(repo.read(manifest_path, head))
            metadata = json.loads(metadata_raw)
            # Keep the earlier metadata-membership check satisfied, so the
            # malformed descriptor is the specific reason this reader rejects.
            del metadata['record']['title']
            manifest['containers']['title']['extra'] = True
            cases = (
                ({metadata_path: canonical_json(metadata), manifest_path: canonical_json(manifest)},
                 'invalid metadata descriptor: title'),
                ({'research/unregistered.json': b'{}\n'},
                 "undeclared state files: ['research/unregistered.json']"),
            )
            for changes, reason in cases:
                with self.subTest(reason=reason):
                    current = repo._store.read_snapshot().head
                    # Restore the two original documents if the preceding
                    # corruption was another writer's current head.
                    changes = {metadata_path: metadata_raw,
                               manifest_path: repo.read(manifest_path, head), **changes}
                    damaged = rewrite_commit(repo, current, changes)
                    reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                    with self.assertRaises(ValueError) as caught:
                        reader.load(damaged)
                    self.assertIs(type(caught.exception), ValueError)
                    self.assertEqual(str(caught.exception), reason)
                    self.assertEqual(reader._store.read_snapshot().head, damaged)
                    self.assertEqual(reader.load(head)[1]['title'], '원본')
                    self.assertEqual(reader.read(metadata_path, head), metadata_raw)

    def test_query_and_export_rejections_leave_snapshot_and_destination_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = record_store(root / 'repository')
            head = repo.initialize(*current_state({'title': 'query original'}))
            paths = repo.list_files('research/', head)
            original = repo.read_many(paths, head)
            destination = root / 'export'
            destination.mkdir()
            for options in ({'text': None}, {'limit': True}, {'limit': 0}, {'limit': 1.5}):
                with self.subTest(options=options), self.assertRaises(ValueError) as caught:
                    repo.query(snapshot=head, **options)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), 'text must be a string and limit a positive integer')
            for prefix, reason in ((None, 'prefix must be a slash-terminated POSIX state path'),
                                   ('research', 'prefix must be a slash-terminated POSIX state path'),
                                   ('/', 'prefix may not be the state root')):
                with self.subTest(prefix=prefix), self.assertRaises(ValueError) as caught:
                    repo.list_files(prefix, head)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
            for prefixes in ([], ()):
                with self.subTest(prefixes=prefixes), self.assertRaises(ValueError) as caught:
                    repo.export(destination, head, prefixes=prefixes)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), 'prefixes must be a non-empty tuple')
                self.assertEqual(list(destination.iterdir()), [])
            with self.assertRaises(KeyError) as caught:
                repo.read_record('UI-absent', head)
            self.assertIs(type(caught.exception), KeyError)
            self.assertEqual(caught.exception.args, ('record not found: UI-absent',))
            page = repo.query(snapshot=head, limit=1)
            self.assertIs(type(page['next_cursor']), str)
            _, instance, runtime = repo.load(head)
            instance['title'] = 'query successor'
            final = repo.save_with_state(head, instance, runtime)[0]
            with self.assertRaises(RepositoryCursorError) as caught:
                repo.query(snapshot=final, limit=1, cursor=page['next_cursor'])
            self.assertIs(type(caught.exception), RepositoryCursorError)
            self.assertEqual(str(caught.exception), 'cursor is bound to another snapshot or query')
            sizes = repo.blob_sizes(paths, head)
            self.assertEqual(sizes, {path: len(raw) for path, raw in original.items()})
            self.assertTrue(all(type(size) is int for size in sizes.values()))
            exported = repo.export(destination, head)
            self.assertEqual(exported, {'snapshot': head, 'files': paths})
            self.assertEqual({path: (destination / path).read_bytes() for path in paths}, original)
            self.assertEqual(repo.load()[0], final)
            self.assertEqual(repo.read_many(paths, head), original)


if __name__ == '__main__':
    unittest.main()
