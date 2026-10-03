"""실제 해결·반려·계획 실행에서 만든 해소 기록의 봉인과 원자성을 검사한다."""
from copy import deepcopy
import hashlib
import unittest

from do_math import academic
from do_math.canonical import exact_content_hash
from support.academic_resolution_cases import rejection_case
from support.academic_scenes import consumer_sim


class AcademicResolutionValidationTests(unittest.TestCase):
    def test_storage_rejects_resolution_seal_damage_without_publication(self):
        from do_math.state_contract import default_state_contract

        engine = self.engine
        produced = academic.record_resolution(engine.instance, engine.runtime, self.basis,
            self.resolution, execution_id=self.execution_id)
        engine._save()
        published = deepcopy(engine.store.load())
        head, instance, runtime = published
        self.assertEqual(runtime['academic_resolution_records'], [produced])
        self.assertEqual(academic.unresolved_rejections(instance, runtime, self.basis), [])
        family = default_state_contract().family('runtime', 'academic_resolution_records')
        family.checker.validate(produced)
        self.assertIsNone(family.validator(deepcopy(produced)))
        reason = 'academic resolution seal/evidence binding is invalid'

        for damage in ('stale_content', 'empty_evidence', 'missing_hash', 'extra_hash'):
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                row = broken['academic_resolution_records'][0]
                if damage == 'stale_content':
                    row['evidence'] += ' changed after sealing'
                elif damage == 'empty_evidence':
                    row['evidence_refs'] = []
                    row['evidence_hashes'] = {}
                elif damage == 'missing_hash':
                    row['evidence_hashes'].pop(row['evidence_refs'][0])
                else:
                    self.assertNotIn(self.execution_id, row['evidence_hashes'])
                    row['evidence_hashes'][self.execution_id] = exact_content_hash(
                        runtime['executions'][self.execution_id])
                if damage != 'stale_content':
                    row['sha256'] = exact_content_hash({k: v for k, v in row.items() if k != 'sha256'})
                family.checker.validate(row)
                before = deepcopy((instance, broken))
                with self.assertRaises(ValueError) as leaf:
                    family.validator(deepcopy(row))
                self.assertIs(type(leaf.exception), ValueError)
                self.assertEqual(str(leaf.exception), reason)
                with self.assertRaises(ValueError) as caught:
                    engine.store.save_with_state(head, instance, broken)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((instance, broken), before)
                self.assertEqual(engine.store.load(), published)

    def test_record_and_mapping_factories_validate_produced_resolution_bytes(self):
        from jsonschema import Draft202012Validator
        from do_math.record_schemas import schemas
        from do_math.state_contract import default_state_contract, validate_record

        engine = self.engine
        produced = academic.record_resolution(engine.instance, engine.runtime, self.basis,
            self.resolution, execution_id=self.execution_id)
        engine._save()
        published = deepcopy(engine.store.load())
        head, instance, runtime = published
        self.assertEqual(runtime['academic_resolution_records'], [produced])
        installed = default_state_contract().family('runtime', 'academic_resolution_records').schema
        # Call the factories inside the selected test, using the installed producer contract.
        record_schema = schemas.record(
            {key: deepcopy(value) for key, value in installed['properties'].items() if key != 'id'},
            tuple(key for key in installed['required'] if key != 'id'))
        hashes_schema = schemas.mapping(deepcopy(schemas.HASH))
        self.assertEqual(record_schema, installed)
        self.assertEqual(hashes_schema, installed['properties']['evidence_hashes'])
        self.assertEqual(record_schema['required'][0], 'id')
        self.assertIs(record_schema['additionalProperties'], False)
        label = 'runtime/academic_resolution_records/None'
        record_checker = Draft202012Validator(record_schema)
        hashes_checker = Draft202012Validator(hashes_schema)
        self.assertIsNone(validate_record(record_checker, produced, label))
        self.assertTrue(produced['evidence_hashes'])
        self.assertIsNone(validate_record(hashes_checker, produced['evidence_hashes'], label + '/evidence_hashes'))
        reference = produced['evidence_refs'][0]

        cases = (('missing_id', label + "/: 'id' is a required property"),
                 ('extra_field', label + "/: Additional properties are not allowed ('unexpected' was unexpected)"),
                 ('map_container', label + "/evidence_hashes: [] is not of type 'object'"),
                 ('map_value', label + '/evidence_hashes/' + reference + ": 17 is not of type 'string'"))
        for damage, reason in cases:
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                row = broken['academic_resolution_records'][0]
                if damage == 'missing_id':
                    row.pop('id')
                elif damage == 'extra_field':
                    row['unexpected'] = 'undeclared'
                elif damage == 'map_container':
                    row['evidence_hashes'] = []
                else:
                    row['evidence_hashes'][reference] = 17
                before = deepcopy((instance, broken))
                with self.assertRaises(ValueError) as leaf:
                    validate_record(record_checker, row, label)
                self.assertIs(type(leaf.exception), ValueError)
                self.assertEqual(str(leaf.exception), reason)
                if damage.startswith('map_'):
                    with self.assertRaises(ValueError) as mapped:
                        validate_record(hashes_checker, row['evidence_hashes'], label + '/evidence_hashes')
                    self.assertIs(type(mapped.exception), ValueError)
                    # validate_record separates the label and an empty path with '/'.
                    mapping_reason = (label + "/evidence_hashes/: [] is not of type 'object'"
                                      if damage == 'map_container' else reason)
                    self.assertEqual(str(mapped.exception), mapping_reason)
                with self.assertRaises(ValueError) as caught:
                    engine.store.save_with_state(head, instance, broken)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((instance, broken), before)
                self.assertEqual(engine.store.load(), published)

    def setUp(self):
        self.sim, self.execution_id, self.resolution = rejection_case()
        self.engine = self.sim.engine
        self.basis = self.engine._solution_basis()

    def test_resolution_seals_current_records_and_is_idempotent(self):
        engine = self.engine
        rejection = deepcopy(engine.runtime['external_rejections'][-1])
        expected = {'rejection_id': rejection['id'], 'rejection_sha256': exact_content_hash(rejection),
            'solution_basis': self.basis, 'requirements_sha256': academic.current_requirements(engine.instance)['sha256'],
            'execution_id': self.execution_id, 'decision': 'resolved', 'evidence': self.resolution['evidence'],
            'evidence_refs': self.resolution['evidence_refs'], 'evidence_hashes': {
                ref: exact_content_hash(engine.instance['knowledge'][ref]) for ref in self.resolution['evidence_refs']}}
        expected['id'] = 'AR-' + exact_content_hash(expected)[:24]
        expected['sha256'] = exact_content_hash(expected)
        for _ in range(2):
            result = academic.record_resolution(engine.instance, engine.runtime, self.basis, self.resolution,
                                                execution_id=self.execution_id)
            self.assertEqual(result, expected)
        self.assertEqual(engine.runtime['academic_resolution_records'], [expected])
        result['evidence_refs'].clear()
        self.assertEqual(engine.runtime['academic_resolution_records'], [expected])
        engine._save()
        self.assertEqual(engine.store.load()[2]['academic_resolution_records'], [expected])
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, self.basis), [])

    def test_resolution_rejects_missing_or_stale_rejection_basis(self):
        for basis, resolution in ((None, self.resolution),
                                  ({**self.basis, 'goal_ref': 'changed'}, self.resolution),
                                  (self.basis, {**self.resolution, 'id': 'missing'})):
            with self.subTest(basis=basis, rejection=resolution['id']):
                before = deepcopy(self.engine.runtime)
                with self.assertRaisesRegex(ValueError, '^rejection basis is not current$'):
                    academic.record_resolution(self.engine.instance, self.engine.runtime, basis, resolution,
                                                execution_id=self.execution_id)
                self.assertEqual(self.engine.runtime, before)

    def test_resolution_rejects_nonplanner_and_changed_input_basis(self):
        for key, value in (('role', 'research_work'), ('input_solution_basis', None)):
            with self.subTest(key=key):
                runtime = deepcopy(self.engine.runtime)
                runtime['executions'][self.execution_id][key] = value
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^planner execution lacks current solution input$'):
                    academic.record_resolution(self.engine.instance, runtime, self.basis, self.resolution,
                                                execution_id=self.execution_id)
                self.assertEqual(runtime, before)

    def test_resolution_rejects_invalid_verdict_or_assessment_text(self):
        for key, value in (('decision', 'approved'), ('evidence', None), ('evidence', ' \t')):
            with self.subTest(key=key, value=value):
                before = deepcopy(self.engine.runtime)
                with self.assertRaisesRegex(ValueError, '^resolution requires verdict and actual assessment$'):
                    academic.record_resolution(self.engine.instance, self.engine.runtime, self.basis,
                        {**self.resolution, key: value}, execution_id=self.execution_id)
                self.assertEqual(self.engine.runtime, before)

    def test_resolution_requires_nonempty_resolvable_evidence(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^resolution needs resolvable evidence$'):
            academic.record_resolution(self.engine.instance, self.engine.runtime, self.basis,
                {**self.resolution, 'evidence_refs': []}, execution_id=self.execution_id)
        self.assertEqual(self.engine.runtime, before)

    def test_resolution_batch_is_atomic_when_later_evidence_is_missing(self):
        engine = self.engine
        engine._academic_control({'id': self.execution_id, 'action': 'decision', 'created_at': self.sim.clock.now(),
            'config': {'change': {'kind': 'academic_rejection', 'actor': '합성 심사자', 'text': '두 번째 반려'}}})
        missing = 'runtime/artifacts/BA-academic-absent/missing.md'
        for ref, reason in (
                ('missing', '^state paths must be files below research/ or runtime/$'),
                (missing, '^academic evidence must resolve uniquely: ' + missing.replace('.', r'\.') + '$')):
            with self.subTest(ref=ref):
                bad = {**self.resolution, 'id': engine.runtime['external_rejections'][-1]['id'],
                       'evidence_refs': [ref]}
                before = deepcopy(engine.runtime)
                with self.assertRaisesRegex(ValueError, reason):
                    engine._apply_academic_resolutions({'role': 'research_plan'}, self.execution_id,
                                                       [self.resolution, bad])
                self.assertEqual(engine.runtime, before)

    def test_resolution_batch_rejects_wrong_role_and_duplicate_ids(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^academic resolutions require designated planner$'):
            self.engine._apply_academic_resolutions({'role': 'research_work'}, self.execution_id, [self.resolution])
        self.assertEqual(self.engine.runtime, before)
        with self.assertRaisesRegex(ValueError, '^rejection resolution IDs must be distinct$'):
            self.engine._apply_academic_resolutions({'role': 'research_plan'}, self.execution_id,
                                                     [self.resolution, deepcopy(self.resolution)])
        self.assertEqual(self.engine.runtime, before)

    def test_empty_resolution_batch_changes_nothing(self):
        before = deepcopy(self.engine.runtime)
        self.engine._apply_academic_resolutions({'role': 'research_plan'}, self.execution_id, [])
        self.assertEqual(self.engine.runtime, before)

    def test_successful_batch_publishes_exact_single_resolution(self):
        expected_runtime = deepcopy(self.engine.runtime)
        expected = academic.record_resolution(self.engine.instance, expected_runtime, self.basis,
                                             self.resolution, execution_id=self.execution_id)
        self.engine._apply_academic_resolutions({'role': 'research_plan'}, self.execution_id, [self.resolution])
        self.assertEqual(self.engine.runtime['academic_resolution_records'], [expected])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['academic_resolution_records'], [expected])

    def test_unresolved_verdict_keeps_exact_rejection(self):
        resolution = {**self.resolution, 'decision': 'unresolved'}
        academic.record_resolution(self.engine.instance, self.engine.runtime, self.basis, resolution,
                                   execution_id=self.execution_id)
        before = deepcopy(self.engine.runtime['external_rejections'])
        result = academic.unresolved_rejections(self.engine.instance, self.engine.runtime, self.basis)
        self.assertEqual(result, before)
        result[0]['text'] = '변조'
        self.assertEqual(self.engine.runtime['external_rejections'], before)

    def test_changed_or_missing_evidence_reopens_rejection(self):
        engine = self.engine
        academic.record_resolution(engine.instance, engine.runtime, self.basis, self.resolution, execution_id=self.execution_id)
        ref = self.resolution['evidence_refs'][0]
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, self.basis), [])
        for absent in (False, True):
            with self.subTest(absent=absent):
                instance = deepcopy(engine.instance)
                if absent:
                    instance['knowledge'].pop(ref)
                else:
                    instance['knowledge'][ref]['summary'] = '변조'
                self.assertEqual(academic.unresolved_rejections(instance, engine.runtime, self.basis),
                                 engine.runtime['external_rejections'])

    def test_other_solution_rejections_do_not_block_this_solution(self):
        runtime = deepcopy(self.engine.runtime)
        runtime['external_rejections'][0]['solution_basis'] = {**self.basis, 'goal_ref': 'older'}
        before = deepcopy(runtime)
        self.assertEqual(academic.unresolved_rejections(self.engine.instance, runtime, self.basis), [])
        self.assertEqual(runtime, before)

    def test_duplicate_evidence_identity_is_ambiguous(self):
        ref = self.resolution['evidence_refs'][0]
        runtime = deepcopy(self.engine.runtime)
        runtime['executions'][ref] = deepcopy(runtime['executions'][self.execution_id])
        with self.assertRaisesRegex(ValueError, '^academic evidence must resolve uniquely: ' + ref + '$'):
            academic.evidence_record(self.engine.instance, runtime, ref)
        self.assertEqual(self.engine.runtime['executions'].get(ref), None)

    def test_stored_byte_evidence_is_hashed_and_missing_reader_does_not_resolve(self):
        engine = self.engine
        ref = 'runtime/artifacts/BA-academic-response/response.md'
        content = '합성 반려 답변'.encode('utf-8')
        engine._save({ref: content})
        self.assertEqual(engine._academic_evidence(ref), content)
        resolution = {**self.resolution, 'evidence_refs': [ref]}
        record = academic.record_resolution(engine.instance, engine.runtime, self.basis, resolution,
            execution_id=self.execution_id, resolve_evidence=engine._academic_evidence)
        self.assertEqual(record['evidence_hashes'], {ref: hashlib.sha256(content).hexdigest()})
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, self.basis,
                                                       resolve_evidence=engine._academic_evidence), [])
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, self.basis),
                         engine.runtime['external_rejections'])

    def test_missing_stored_evidence_callback_still_rejects_resolution(self):
        ref = 'runtime/artifacts/BA-academic-absent/missing.md'
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^academic evidence must resolve uniquely: ' + ref + '$'):
            academic.evidence_record(self.engine.instance, self.engine.runtime, ref, self.engine._academic_evidence)
        self.assertEqual(self.engine.runtime, before)


class AcademicControlValidationTests(unittest.TestCase):
    def test_unrelated_control_returns_false_without_changing_state(self):
        engine = consumer_sim().engine
        before = deepcopy(engine.runtime)
        self.assertIs(engine._academic_control({'action': 'pause'}), False)
        self.assertEqual(engine.runtime, before)

    def test_rejection_requires_actor_and_preserved_text(self):
        engine = consumer_sim().engine
        for field, value in (('actor', ''), ('text', ' \n'), ('actor', None)):
            with self.subTest(field=field, value=value):
                before = deepcopy(engine.runtime)
                change = {'kind': 'academic_rejection', 'actor': '합성 심사자', 'text': '합성 반려', field: value}
                with self.assertRaisesRegex(ValueError, '^external rejection needs its actor and preserved original text$'):
                    engine._academic_control({'action': 'decision', 'config': {'change': change}})
                self.assertEqual(engine.runtime, before)
