"""StateContract의 등록/입력/참조 거부 및 실제 Repository 게시 원자성."""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.state_contract import StateContract
from support.state_builders import current_state, installed_contract
from support.storage_git import ObservedGit
from support.storage_records import record_store


class ContractRejections(unittest.TestCase):
    def test_invalid_registration_never_installs_a_family(self):
        for options, reason in (
                ({'root': 'other', 'name': 'x'}, 'invalid family root/name'),
                ({'root': 'research', 'name': 'Bad'}, 'invalid family root/name'),
                ({'root': 'research', 'name': 'x', 'shape': 'tuple'}, 'invalid family shape'),
                ({'root': 'research', 'name': 'x', 'shape': 'metadata'},
                 'metadata fields cannot allocate independent record identities')):
            contract = StateContract()
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                contract.register_family(**options, schema={'type': 'object', 'additionalProperties': False})
            self.assertEqual(contract.families(), ())

    def test_roots_and_family_containers_reject_wrong_shape(self):
        contract = installed_contract()
        base_i, base_r = current_state({'object_format': 'sha1'})
        cases = (([], base_r, 'research must be an object'),
                 (base_i, [], 'runtime must be an object'),
                 ({**base_i, 'object_format': 'other'}, base_r, 'research object_format is missing or unsupported'),
                 ({**base_i, 'knowledge': []}, base_r, 'knowledge must be a record map'),
                 ({**base_i, 'sources': {}}, base_r, 'sources must be a record list'))
        for instance, runtime, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                contract.validate(instance, runtime)
        self.assertEqual(contract.validate(base_i, base_r)['UI-fixture'][1], 'inputs')

    def test_identity_checks_run_even_when_schema_allows_missing_or_unsafe_id(self):
        contract = installed_contract()
        contract.register_family('research', 'probe', schema={'type': 'object', 'additionalProperties': False,
            'properties': {'id': {'type': 'string'}}})
        for record, key, reason in (({}, 'p', 'probe requires a path-safe record id'),
                ({'id': 'p'}, 'q', 'probe map key and id differ'),
                ({'id': 'CON'}, 'CON', 'probe requires a path-safe record id: path contains a reserved Windows device name')):
            instance, runtime = current_state({'object_format': 'sha1', 'probe': {key: record}})
            with self.subTest(record=record), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                contract.validate(instance, runtime)

    def test_instance_identity_collision_and_wrong_reference_family_are_rejected(self):
        contract = installed_contract()
        instance, runtime = current_state({'object_format': 'sha1', 'id': 'UI-fixture'})
        with self.assertRaisesRegex(ValueError, '^record IDs must be globally unique: UI-fixture$'):
            contract.validate(instance, runtime)
        schema = {'type': 'object', 'additionalProperties': False, 'required': ['id'],
                  'properties': {'id': {'type': 'string'}}}
        contract.register_family('research', 'probe', schema=schema,
                                 references=lambda row: [(None, 'inputs'), ('UI-fixture', 'sources')])
        instance.pop('id')
        instance['probe'] = {'PR-one': {'id': 'PR-one'}}
        with self.assertRaisesRegex(ValueError, '^probe reference has wrong family: UI-fixture$'):
            contract.validate(instance, runtime)

    def test_rejected_field_preserves_head_files_and_caller_then_valid_save_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state({'title': 'before'}))
            paths = repo.list_files('research/', head) + repo.list_files('runtime/', head)
            before_files = repo.read_many(paths, head)
            _, instance, runtime = repo.load(head)
            instance['title'] = []
            caller = canonical_json([instance, runtime])
            start = len(backend.calls)
            with self.assertRaisesRegex(ValueError, r"^research/title/None/: \[\] is not of type 'string'$"):
                repo.save_with_state(head, instance, runtime)
            self.assertEqual([args for name, args in backend.calls[start:] if name == 'write_object'], [])
            self.assertEqual(repo.load()[0], head)
            self.assertEqual(repo.read_many(paths, head), before_files)
            self.assertEqual(canonical_json([instance, runtime]), caller)
            instance['title'] = 'after'
            final, saved_i, saved_r = repo.save_with_state(head, instance, runtime)
            self.assertNotEqual(final, head)
            self.assertEqual(repo.load(final), (final, saved_i, saved_r))
            self.assertEqual(saved_i['title'], 'after')


    def test_repository_boundary_rejections_preserve_ref_objects_and_input_bytes(self):
        from do_math.initialization import initialize_state
        from support.entry import entry
        from support.storage_records import INSTANCE_ID

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend = ObservedGit()
            repo = record_store(root, backend=backend)
            with self.assertRaises(ValueError) as absent:
                repo.load()
            self.assertIs(type(absent.exception), ValueError)
            self.assertEqual(str(absent.exception), 'repository has no authoritative snapshot')
            ports = entry().ports
            instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='Preserve input',
                workspace=root / 'workspace', config={}, source_input='원본\ninput',
                clock=ports.clock, host=ports.host)
            head = repo.initialize(instance, runtime)
            paths = repo.list_files('research/', head) + repo.list_files('runtime/', head)
            original = repo.read_many(paths, head)
            caller = canonical_json([instance, runtime])
            cases = (
                (lambda: repo.initialize(instance, runtime), ValueError,
                 'the instance ref already has an initial state'),
                (lambda: repo.validate_candidate([], runtime), ValueError,
                 'instance and runtime must be objects'),
                (lambda: repo.validate_candidate(instance, []), ValueError,
                 'instance and runtime must be objects'),
                (lambda: repo.save_with_state(head, instance, runtime, artifacts=[]), TypeError,
                 'artifacts must map full artifact paths to bytes'),
            )
            for operation, kind, reason in cases:
                with self.subTest(reason=reason):
                    start = len(backend.calls)
                    with self.assertRaises(kind) as caught:
                        operation()
                    self.assertIs(type(caught.exception), kind)
                    self.assertEqual(str(caught.exception), reason)
                    self.assertEqual([name for name, _ in backend.calls[start:]
                                      if name in {'write_object', 'update_ref'}], [])
                    self.assertEqual(repo._store.read_snapshot().head, head)
                    self.assertEqual(repo.read_many(paths, head), original)
                    self.assertEqual(canonical_json([instance, runtime]), caller)
            broken = deepcopy(instance)
            broken['lifecycle']['immutable_input']['text'] += 'changed'
            with self.assertRaises(ValueError) as caught:
                repo.save_with_state(head, broken, runtime)
            self.assertIs(type(caught.exception), ValueError)
            self.assertEqual(str(caught.exception), 'immutable original input changed')
            self.assertEqual(repo.load()[0], head)
            self.assertEqual(repo.read_many(paths, head), original)

    def test_unbound_validated_candidate_is_revalidated_before_single_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state({'title': 'before'}))
            _, instance, runtime = repo.load(head)
            instance['title'] = '다음\nedition'
            candidate = repo.validate_candidate(instance, runtime)
            self.assertEqual(candidate['basis'], {'head': None})
            before = deepcopy(candidate)
            start = len(backend.calls)
            final, saved_i, saved_r = repo.save_validated(head, candidate)
            self.assertEqual([args for name, args in backend.calls[start:] if name == 'update_ref'],
                             [(final, head)])
            self.assertNotEqual(final, head)
            self.assertEqual(repo.load(), (final, saved_i, saved_r))
            self.assertEqual(saved_i['title'], '다음\nedition')
            self.assertIs(type(saved_i['title']), str)
            self.assertEqual(repo.read('research/_state/metadata.json', final),
                             candidate['files']['research/_state/metadata.json'])
            self.assertEqual(candidate, before)
            saved_i['title'] = 'caller mutation'
            self.assertEqual(repo.load(final)[1]['title'], '다음\nedition')


if __name__ == '__main__':
    unittest.main()
