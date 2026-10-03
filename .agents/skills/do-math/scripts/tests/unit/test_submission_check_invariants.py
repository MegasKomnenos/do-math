"""submission 빈 분기의 체크 불변식과 정상 외곽 안의 중첩 metadata 오류.
설치와 정상 대조군을 포함하는 경계 입력 시험은 실측 0.218초까지 걸린다. 입력과 단언을 줄이지 않는다.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import contracts, integration, submission
from do_math.canonical import canonical_json, exact_content_hash
from support.fakes.clock import FakeClock
from support.record_builders import research_work_context, two_observation_output
from support.submission_obligations import maintenance_output


class CheckInvariantTests(unittest.TestCase):
    def test_control_request_checks_kind_budget_binding_and_workspace_in_order(self):
        from support.submission_protocol import ProtocolScene
        with tempfile.TemporaryDirectory() as directory:
            scene = ProtocolScene(Path(directory))
            self.assertEqual(submission.control_request_payload(scene.workspace, scene.draft,
                kind='submit_intent', wait_seconds=0), (scene.binding, {'draft_path': '.scratch/draft.json'}))
            with self.assertRaisesRegex(ValueError, '^unsupported submission control kind$'):
                submission.control_request_payload(scene.workspace, scene.draft, kind='absent', wait_seconds=0)
            for value in (True, -1, float('nan'), float('inf'), '0', None):
                with self.subTest(value=value), self.assertRaisesRegex(ValueError,
                        '^wait_seconds must be a finite nonnegative caller budget$'):
                    submission.control_request_payload(scene.workspace, scene.draft,
                        kind='submit_intent', wait_seconds=value)
            with self.assertRaisesRegex(ValueError, '^draft has no matching execution control binding$'):
                submission.control_request_payload(scene.workspace, scene.draft, kind='submit_intent',
                    wait_seconds=0, binding={**scene.binding, 'execution_id': 'EX-other'})
            with self.assertRaisesRegex(ValueError, '^submission draft must be inside this workspace$'):
                submission.control_request_payload(scene.workspace, Path(directory) / 'outside.json',
                    kind='submit_intent', wait_seconds=0)

    def test_metadata_relation_claim_contributes_only_current_explicit_edges(self):
        output = maintenance_output()
        metadata = {'title': '관계 주장', 'relation_claim': {'kind': 'supports', 'source': 'KN-A',
            'target': 'KN-B', 'confirmed_scope': 'KN-prose', 'history': [{'source': 'KN-history'}],
            'origin_refs': ['KN-origin']}}
        self.assertEqual(submission.reported_references(output, {'knowledge_metadata': [metadata]}),
                         ['KN-A', 'KN-B'])

    def test_sibling_boundaries_distinguish_duplicates_from_outside_input(self):
        from support.role_answers import candidate
        from support.record_builders import transfer_assessment
        _, runtime, _ = transfer_assessment()
        row = {'task_id': 'TK-1', 'revision': runtime['tasks']['TK-1']['revision'],
               'boundary': '별개의 주장 범위', 'independent_of_next_revision': True}
        def errors(rows):
            return submission.contract_check_errors(candidate(), {'sibling_boundaries': rows}, [],
                runtime['tasks'], set(), set())
        self.assertEqual(errors([row]), [])
        self.assertEqual(errors([row, row]),
                         [('contract_check.sibling_boundary', 'sibling boundaries must name distinct tasks')])
        self.assertEqual(errors([{**row, 'task_id': 'TK-outside'}]), [('contract_check.sibling_boundary',
            'sibling boundary names a task outside the supplied input: TK-outside')])

    def test_check_modes_and_history_limits_are_not_coerced(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, '^unknown submission check mode$'):
                submission.check_submission({}, {}, {}, {}, Path(directory), mode='absent',
                    execution_id='EX-mode', tool_sha256='a' * 64, clock=clock)
        for value in (True, False, -1, 1.5, '1', None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError,
                    '^history_window must be a nonnegative integer$'):
                submission.summarize_checks([], history_window=value)
        for snapshot, limit in ((None, 1), ('', 1), (0, 1), ('snapshot', True), ('snapshot', -1)):
            with self.subTest(snapshot=snapshot, limit=limit), self.assertRaisesRegex(ValueError,
                    '^snapshot and nonnegative history_window are required$'):
                submission.summarize_snapshot_checks([], snapshot=snapshot,
                    read_artifact=lambda path, commit: self.fail('인자 반려 전에 읽기를 요청함'), history_window=limit)

    def test_changed_tool_is_distinguished_from_changed_input(self):
        context = {'action': {'role': 'maintenance'}, 'execution_id': 'EX-tools', 'snapshot': 'a' * 40}
        schema = contracts.action_schema(context['action'])
        with tempfile.TemporaryDirectory() as directory:
            def checked(tool, previous=None):
                return submission.check_submission(maintenance_output(), schema, context, {}, Path(directory),
                    mode='receiver', execution_id='EX-tools', tool_sha256=tool, previous=previous, clock=FakeClock())
            first = checked('a' * 64)
            self.assertEqual((first['passed'], first['issues']), (True, []))
            changed = checked('b' * 64, first)
            self.assertEqual(changed['comparison'], {'status': 'tool_changed', 'previous_check_id': first['id']})
            self.assertEqual((changed['passed'], changed['issues'], changed['input_hashes']),
                             (True, [], first['input_hashes']))

    def test_producer_lock_outside_draft_and_schema_drift_have_distinct_contracts(self):
        from support.submission_protocol import ProtocolScene
        with tempfile.TemporaryDirectory() as directory:
            scene = ProtocolScene(Path(directory))
            lock = scene.workspace / 'checks/.producer-lock'
            lock.parent.mkdir(exist_ok=True)
            lock.write_bytes(b'owner')
            with self.assertRaisesRegex(ValueError, '^another producer check owns this workspace$'):
                submission.producer_check(scene.workspace, scene.draft, clock=scene.clock)
            self.assertEqual(lock.read_bytes(), b'owner')
            lock.unlink()
            outside = Path(directory) / 'outside.json'
            outside.write_bytes(canonical_json(scene.output))
            check = submission.producer_check(scene.workspace, outside, clock=scene.clock)
            self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in check['issues']],
                [('submission.read', 'submission', 'submission draft must be inside this workspace')])
            schema_path = scene.workspace / 'input/submission/schema.json'
            schema = deepcopy(scene.schema)
            schema['description'] = '다른 설치 스키마'
            schema_path.write_bytes(canonical_json(schema))
            check = submission.producer_check(scene.workspace, scene.draft, clock=scene.clock)
            self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in check['issues']],
                [('submission.read', 'submission', 'installed response schema differs from its exact contract reference')])

    def test_capture_rejects_wrong_execution_and_ambiguous_byte_sources(self):
        from support.submission_protocol import ProtocolScene
        with tempfile.TemporaryDirectory() as directory:
            scene = ProtocolScene(Path(directory))
            for execution_id, raw in (('EX-other', None), ('EX-worker', b'{}')):
                sealed = submission.seal_submission(scene.workspace, scene.draft, raw_output=raw,
                    execution_id=execution_id, context=scene.context, schema=scene.schema,
                    max_artifact_bytes=1024 * 1024, clock=scene.clock)
                message = ('central context belongs to another execution' if execution_id == 'EX-other'
                           else 'central capture requires exactly one byte source')
                self.assertFalse(sealed['passed'])
                self.assertFalse(sealed['capture_eligible'])
                self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in sealed['check']['issues']],
                                 [('submission.read', 'submission', message)])

    def test_partial_capture_requires_correct_owner_and_at_least_one_good_bundle(self):
        output, context = two_observation_output(), research_work_context()
        local = integration.issue('schema.type', 'output/knowledge/0/title', 'invalid title', 'IN-A')
        self.assertTrue(submission.capture_eligible(output, {}, context, [local]))
        # 정상 생산자는 output 전체를 IN-A에 배정한다. 그 하위 경로는
        # 이름이 outside여도 무소유가 아니다. 확장 밖 좌표와 구별한다.
        self.assertIn('output', output['integration_bundles'][0]['members'])
        self.assertTrue(submission.capture_eligible(output, {}, context,
            [{**local, 'path': 'output/outside'}]))
        for issues in ([{**local, 'integration_id': 'IN-B'}],
                       [{**local, 'path': 'activity-extensions.json/outside/0'}],
                       [{**local, 'rule_id': 'artifact.preservation'}],
                       [local, integration.issue('schema.type', 'output/knowledge/1/title', 'invalid title', 'IN-B')]):
            with self.subTest(issues=issues):
                self.assertFalse(submission.capture_eligible(output, {}, context, issues))

    def test_capture_flags_reject_nonboolean_or_cross_bundle_inconsistency(self):
        for check, reason in [
            ({'passed': True, 'issues': [{}], 'capture_eligible': True}, 'machine check pass flag differs from its issues'),
            ({'passed': True, 'issues': [], 'capture_eligible': False}, 'invalid machine capture eligibility'),
            ({'passed': False, 'issues': [{}], 'capture_eligible': 1}, 'invalid machine capture eligibility'),
            ({'passed': False, 'issues': [{'integration_id': 'IN-A'}], 'capture_eligible': True,
              'check_subject': {'role': 'maintenance'}}, 'partial capture requires exclusively local independent bundle issues'),
            ({'passed': False, 'issues': [{}], 'capture_eligible': True,
              'check_subject': {'role': 'research_work'}}, 'partial capture requires exclusively local independent bundle issues')]:
            with self.subTest(check=check), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                submission.captured_check(check)
        self.assertFalse(submission.captured_check({'passed': False, 'issues': [{}], 'capture_eligible': False}))

    def test_nested_metadata_title_keeps_its_original_coordinate_and_owner(self):
        output = two_observation_output()
        coordinate = 'activity-extensions.json/knowledge_metadata/0'
        output['integration_bundles'][0]['members'].append(coordinate)
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.action_schema({'role': 'research_work'}),
                research_work_context(), {'knowledge_metadata': [{'title': []}]}, Path(directory), clock=FakeClock())
        self.assertEqual([(i['rule_id'], i['path'], i['message'], i['integration_id']) for i in issues],
                         [('schema.type', coordinate + '/title', "[] is not of type 'string'", 'IN-A')])
        self.assertTrue(submission.capture_eligible(output, {'knowledge_metadata': [{'title': []}]},
                                                   research_work_context(), issues))

    def test_checkpoint_limit_reports_exact_size_rule_without_parsing(self):
        result = submission._captured_checkpoint({'checkpoint.json': b' ' * (submission.CHECKPOINT_MAX_BYTES + 1)})
        self.assertEqual(result, {'status': 'invalid', 'error': 'ValueError: checkpoint exceeds the 4 MiB record limit'})

    def test_load_extensions_preserves_nonobject_and_unknown_empty_family(self):
        for value in (None, [], 0):
            with self.subTest(value=value):
                self.assertEqual(submission.load_extensions(canonical_json(value)), value)
        all_empty = {family: [] for family in submission.EXTENSION_ROLES}
        self.assertEqual(submission.load_extensions(canonical_json({**all_empty, 'unknown': []})), {'unknown': []})

    def test_producer_chain_identity_and_sequence_are_separate_checks(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = {'action': {'role': 'maintenance'}, 'execution_id': 'EX-sequence', 'snapshot': 'a' * 40}
            submission.install_tools(root, context, contracts.schema_for('maintenance'), None, clock=clock)
            draft = root / 'draft.json'
            draft.write_bytes(canonical_json(maintenance_output()))
            first = submission.producer_check(root, draft, clock=clock)
            second = submission.producer_check(root, draft, clock=clock)
            self.assertTrue(first['passed'])
            self.assertTrue(second['passed'])
            self.assertEqual([r['id'] for r in submission.read_producer_checks(root, second['id'])], [first['id'], second['id']])
            for value in ('MC-wrong', 0, '../outside'):
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, '^invalid or cyclic producer check chain$'):
                    submission.read_producer_checks(root, value)
            malformed = deepcopy(second)
            malformed['producer_sequence'] = True
            malformed['id'] = 'MC-' + exact_content_hash({k: v for k, v in malformed.items() if k != 'id'})[:24]
            (root / 'checks' / (malformed['id'] + '.json')).write_bytes(canonical_json(malformed))
            with self.assertRaisesRegex(ValueError, '^producer check lacks an explicit sequence$'):
                submission.read_producer_checks(root, malformed['id'])
            changed = deepcopy(second)
            changed['producer_sequence'] = 9
            with self.assertRaisesRegex(ValueError, '^producer check sequence or execution differs$'):
                submission._validate_producer_sequence([first, changed])

    def test_blocked_scope_must_match_target_and_every_judgment_coordinate(self):
        action = {'role': 'research_preparation', 'target': 'TK-1', 'assessment_targets': {'TK-1': 'h'}}
        blocked = submission.blocked_action_row('AC-failed', {'kind': 'execution_failure',
            'action': action, 'reason': 'failed', 'execution_id': 'EX-failed'})
        self.assertEqual(submission.action_resolution_errors(blocked, deepcopy(action)), [])
        # With no evidence action this pure scope check leaves acceptance to its caller.
        self.assertEqual(submission.action_resolution_errors(blocked, None), [])
        self.assertEqual(blocked, submission.blocked_action_row('AC-failed', {
            'kind': 'execution_failure', 'action': action, 'reason': 'failed', 'execution_id': 'EX-failed'}))
        for field, value in (('target', 'TK-2'), ('role', 'research_plan'), ('assessment_targets', {})):
            with self.subTest(field=field):
                self.assertEqual(submission.action_resolution_errors(blocked, {**action, field: value}),
                    ['resolution evidence must be an execution of the same judgment scope as the failed action'])
        self.assertEqual(submission.action_resolution_errors({**blocked, 'kind': 'environment'}, action),
                         ['only an output_validation or execution_failure wait can be resolved; this action waits for environment'])
