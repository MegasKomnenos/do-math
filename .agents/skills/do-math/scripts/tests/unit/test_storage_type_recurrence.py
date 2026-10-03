"""1-D의 bool/int 동등성 충돌: 정상 수용과 부모 재사용을 별도로 검사한다."""
from pathlib import Path
from copy import deepcopy
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.repository import _encode_families
from support.state_builders import current_state, installed_contract
from support.storage_git import ObservedGit
from support.storage_records import record_store


class TypeRecurrence(unittest.TestCase):
    def test_engine_noop_check_publishes_boolean_integer_swaps(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.initialization import initialize_state
        from support.fakes.clock import FakeClock
        from support.storage_records import INSTANCE_ID, engine_on, fake_ports
        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            clock = FakeClock()
            repo = record_store(Path(directory), backend=backend, clock=clock)
            ports = fake_ports(clock, backend)
            workspace = Path(directory)/'work'
            state = initialize_state(instance_id=INSTANCE_ID, goal='Observe exact storage types',
                workspace=workspace, config=DEFAULT_CONFIG, source_input='Observe exact storage types',
                clock=clock, host=ports.host)
            engine, _ = engine_on(repo, *state, workspace=workspace, ports=ports)
            engine.runtime['history'].append({'typed_value': 1})
            engine._save()
            old_head = engine.head
            for value in (True, 1):
                engine.runtime['history'][-1]['typed_value'] = value
                previous_head = engine.head
                engine._save()
                self.assertNotEqual(engine.head, previous_head)
                reader = record_store(Path(directory), backend=backend, clock=clock,
                                      contract=installed_contract())
                loaded = reader.load(engine.head)[2]['history'][-1]['typed_value']
                self.assertIs(type(loaded), type(value))
                self.assertEqual(canonical_json(loaded), canonical_json(value))
                head = engine.head
                engine._save()
                self.assertEqual(engine.head, head)
            self.assertIs(type(reader.load(old_head)[2]['history'][-1]['typed_value']), int)

    def test_json_equality_matches_exact_bytes_for_nested_types_and_sealed_text(self):
        from do_math.canonical import same_json_value
        from do_math.payloads import seal
        text = seal('정확한 원문')
        cases = [(None, None), (False, 0), (True, 1), (2, 2), (2, 3),
                 ({'x': [True, None]}, {'x': [1, None]}),
                 ({'x': [0, False]}, {'x': [False, 0]}),
                 ({'a': [1], 'b': '원문'}, {'b': '원문', 'a': [1]}),
                 ({'x': text}, {'x': '정확한 원문'}), ([], {}), ([1], [1, 2])]
        for left, right in cases:
            with self.subTest(left=left, right=right):
                expected = canonical_json(left) == canonical_json(right)
                self.assertIs(same_json_value(left, right), expected)
                self.assertIs(same_json_value(right, left), expected)

    def test_equal_parent_reuses_body_and_changed_integer_encodes_new_body(self):
        contract = installed_contract()
        with tempfile.TemporaryDirectory() as directory:
            repo = record_store(Path(directory), contract=contract)
            head = repo.initialize(*current_state(runtime={'history': [{'value': 1}]}))
            _, instance, runtime = repo.load(head)
        contract.validate(instance, runtime)
        files = _encode_families(instance, runtime, contract, 'sha1')
        parent = (deepcopy(instance), deepcopy(runtime), files)
        path = 'runtime/history/state.json'
        unchanged = _encode_families(instance, runtime, contract, 'sha1', parent=parent)
        self.assertIs(unchanged[path], files[path])
        # JSON identity distinguishes boolean and integer despite Python equality.
        runtime['history'][0]['value'] = True
        contract.validate(instance, runtime)
        typed = _encode_families(instance, runtime, contract, 'sha1', parent=parent)
        self.assertIsNot(typed[path], files[path])
        self.assertEqual(typed[path], _encode_families(instance, runtime, contract, 'sha1')[path])
        runtime['history'][0]['value'] = 2
        contract.validate(instance, runtime)
        changed = _encode_families(instance, runtime, contract, 'sha1', parent=parent)
        self.assertIsNot(changed[path], files[path])
        self.assertEqual(changed[path], _encode_families(instance, runtime, contract, 'sha1')[path])
        self.assertNotEqual(changed[path], files[path])

    def test_both_scalar_types_are_accepted_without_parent_reuse(self):
        for value in (1, True):
            with self.subTest(value=repr(value)), tempfile.TemporaryDirectory() as directory:
                backend = ObservedGit()
                writer = record_store(Path(directory), backend=backend)
                head = writer.initialize(*current_state(runtime={'history': [{'value': value}]}))
                reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                loaded = reader.load(head)[2]['history'][0]['value']
                self.assertEqual(canonical_json(loaded), canonical_json(value))
                self.assertIs(type(loaded), type(value))

    def test_parent_boolean_cannot_hide_an_integer_from_the_schema_check(self):
        with tempfile.TemporaryDirectory() as directory:
            contract = installed_contract()
            contract.register_family('runtime', 'typed_probe', shape='singleton', identity=False,
                schema={'type': 'object', 'properties': {'flag': {'type': 'boolean'}},
                        'required': ['flag'], 'additionalProperties': False})
            repo = record_store(Path(directory), contract=contract)
            instance, runtime = current_state(runtime={'typed_probe': {'flag': False}})
            head = repo.initialize(instance, runtime)
            published = deepcopy(repo.load(head))
            _, instance, runtime = repo.load(head)
            runtime['typed_probe']['flag'] = 0
            before = deepcopy((instance, runtime))
            with self.assertRaisesRegex(ValueError,
                    "^runtime/typed_probe/None/flag: 0 is not of type 'boolean'$"):
                repo.save_with_state(head, instance, runtime)
            self.assertEqual((instance, runtime), before)
            self.assertEqual(repo.load(head), published)

    def test_equal_python_scalars_do_not_reuse_different_json_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            writer = record_store(Path(directory), backend=backend)
            head = writer.initialize(*current_state(runtime={'history': [{'value': 1}]}))
            for value in (True, 1):
                _, instance, runtime = writer.load(head)
                runtime['history'][0]['value'] = value
                writer.contract.validate(instance, runtime)
                head, _, _ = writer.save_with_state(head, instance, runtime)
                reader = record_store(Path(directory), backend=backend, contract=installed_contract())
                loaded = reader.load(head)[2]['history'][0]['value']
                self.assertEqual(canonical_json(loaded), canonical_json(value))
                self.assertIs(type(loaded), type(value))


if __name__ == '__main__':
    unittest.main()
