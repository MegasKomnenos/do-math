"""첫 gap의 확장 의미 분기를 정상 생산자 자료와 스키마 적합 입력으로 검사한다."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import contracts, external, governance, integration, knowledge, knowledge_io, questions, revisions, submission
from support.default_responder import common
from support.fakes.clock import FakeClock
from support.observation_inputs import observation_rule
from support.record_builders import observation_knowledge, research_work_context, two_observation_output


class ExtensionMeaningTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.context = {**research_work_context(), 'execution_id': 'EX-meaning',
            'kind_definitions': knowledge_io.catalog_definitions(knowledge_io.ensure_ontology({})),
            'tasks': [{'id': 'TK-1'}]}

    def check(self, extensions, *, context=None, output=None):
        """정상 외곽과 선언 소유권을 유지하며 실제 payload 의미 검사를 호출한다."""
        context = deepcopy(context if context is not None else self.context)
        output = deepcopy(output if output is not None else two_observation_output())
        if 'integration_bundles' not in output:
            output = integration.protocol_output(output, extensions, context)
        else:
            output['integration_bundles'][0]['members'].extend(path for path in
                integration.member_values(output, extensions, context) if path.startswith('activity-extensions.json/'))
        schema = contracts.action_schema(context['action'])
        jsonschema.Draft202012Validator(schema).validate(output)
        jsonschema.Draft202012Validator(submission.extension_schema(context['action'])).validate(extensions)
        before = deepcopy((output, context, extensions))
        result = submission.payload_issues(output, schema, context, extensions, self.workspace, clock=self.clock)
        self.assertEqual((output, context, extensions), before)
        self.owner = output['integration_bundles'][0]['integration_id']
        return result

    def assert_rejection(self, extensions, path, message, *, context=None, output=None):
        issues = self.check(extensions, context=context, output=output)
        self.assertEqual([(row['path'], row['message'], row['integration_id']) for row in issues],
                         [(path, message, self.owner)])

    def test_proposed_kind_is_actually_registered_before_checking_its_consumer(self):
        definition = {'family': 'knowledge', 'token': 'bounded_note',
                      'meaning': '범위가 명시된 관찰 기록', 'constraints': {}}
        output = two_observation_output()
        output['knowledge'][0]['kind'] = definition['token']
        self.assertEqual(self.check({'kind_definitions': [definition]}, output=output), [])
        self.assert_rejection({'kind_definitions': [{**definition, 'token': 'invalid token'}]},
            'activity-extensions.json/kind_definitions/0', 'kind definition has an invalid family or token')

    def test_relation_metadata_requires_registered_kind_and_existing_endpoints(self):
        context = deepcopy(self.context)
        first, second = self.clock.new_id('KN'), self.clock.new_id('KN')
        context['knowledge_catalog'] = [{'id': first}, {'id': second}]
        claim = {'kind': context['kind_definitions']['relations'][0]['token'],
                 'source': first, 'target': second, 'confirmed_scope': '기존 두 결과 사이의 관계'}
        metadata = {'title': 'A', 'relation_claim': claim}
        self.assertEqual(self.check({'knowledge_metadata': [metadata]}, context=context), [])
        for field, value in (('kind', 'unregistered'), ('source', 'KN-outside'), ('target', 'KN-outside')):
            with self.subTest(field=field):
                self.assert_rejection({'knowledge_metadata': [{**metadata, 'relation_claim': {**claim, field: value}}]},
                    'activity-extensions.json/knowledge_metadata/0/relation_claim',
                    'relation claim requires a registered relation kind and existing knowledge endpoints', context=context)

    def test_persisted_observation_rules_require_the_assigned_task(self):
        extension = {'observation_rules': [observation_rule()]}
        self.assertEqual(self.check(extension), [])
        context = {**self.context, 'action': {'role': 'research_work', 'target': 'TK-outside'}}
        self.assert_rejection(extension, 'activity-extensions.json/observation_rules',
                              'persisted rules require the assigned task', context=context)

    def test_question_resolution_checks_each_supplied_evidence_reference(self):
        question = questions.link({}, execution_id='EX-question', field='output/questions/0',
            owner='research', targets=['TK-1'], clock=self.clock)
        context = {**self.context, 'question_links': [question]}
        resolution = {'question_id': question['id'], 'disposition': 'resolved',
                      'evidence_refs': ['TK-1'], 'reason': '제공된 과제의 근거를 확인했다.'}
        self.assertEqual(self.check({'question_resolutions': [resolution]}, context=context), [])
        self.assert_rejection({'question_resolutions': [{**resolution, 'evidence_refs': ['TK-outside']}]},
            'activity-extensions.json/question_resolutions/0/evidence_refs',
            'reference must identify supplied input, a record of the input snapshot or a preserved workspace file: TK-outside; '
            'use an exact reference_catalog value, a record_index ID or workspace:<preserved-file>', context=context)

    def test_time_bounded_http_preview_uses_the_fixed_input_time(self):
        grant = governance.normalized_grant({'kind': 'http', 'reuse': 'reusable',
            'allowed_origins': ['https://example.test'], 'allowed_methods': ['GET'], 'allowed_path_prefixes': ['/'],
            'expires_at': '2099-01-01T00:00:00+00:00'}, gid='GR-preview', created_at=self.clock.now(),
            source_ref='SO-grant', decision_id='DC-grant')
        operation = external.prepare_operation({'method': 'GET', 'url': 'https://example.test/read'},
                                               grant['id'], 'submission-preview')
        extension = {'external_requests': [{'request': operation['request'], 'grant_id': grant['id'],
                                           'purpose': '제공된 HTTP 권한의 고정 시각을 검사한다.'}]}
        context = {**self.context, 'grants': [grant], 'submission_contract': {'basis_time': self.clock.now()}}
        self.assertEqual(self.check(extension, context=context), [])
        context['submission_contract'] = {}
        self.assert_rejection(extension, 'activity-extensions.json/external_requests/0',
                              'time-bounded grant preview requires a fixed input basis_time', context=context)

    def test_queued_request_is_checked_against_the_advertised_queue(self):
        context = {**self.context, 'action': {'role': 'research_plan'}, 'ready_task_ids': [],
                   'queued_work': [{'id': 'AC-visible', 'role': 'maintenance'}]}
        extension = {'queued_requests': [{'request_id': 'AC-visible', 'decision': 'keep', 'reason': '주어진 대기 작업을 유지한다.'}]}
        self.assertEqual(self.check(extension, context=context, output=common('research_plan')), [])
        context['queued_work'] = []
        issues = self.check(extension, context=context, output=common('research_plan'))
        # 가족 전체를 가리키는 오류는 원소 소유권이 아닌 전역 반려다.
        self.assertEqual([(row['path'], row['message'], row['integration_id']) for row in issues],
            [('activity-extensions.json/queued_requests', 'request was not available for planning', None)])

    def test_knowledge_revision_kind_must_come_from_the_fixed_catalog(self):
        state, runtime, identifier = knowledge_io.import_candidate({}, {}, observation_knowledge('기존 관찰'),
            source_ref='SO-original', actor_ref='user', plan_nonformal=False, clock=self.clock)
        record = state['knowledge'][identifier]
        digest = knowledge.content_hash(record)
        context = {**self.context, 'knowledge_catalog': [{**record, 'content_sha256': digest}],
                   'action': {**self.context['action'], 'revision_targets': revisions.capture_targets(state, runtime, [identifier])}}
        output = two_observation_output()
        output['integration_bundles'] = [{'integration_id': 'IN-A', 'members': ['output'],
            'impact_set': [], 'authority_refs': [], 'previous_hashes': {identifier: digest}}]
        change = {'id': identifier, 'changes': {'kind': 'observation'}, 'reason': '관찰 종류를 명시한다.', 'impact_set': []}
        resolutions = [{'record_id': identifier, 'disposition': 'revised', 'reason': '선언한 대상을 개정한다.'}]
        self.assertEqual(self.check({'knowledge_changes': [change], 'revision_resolutions': resolutions}, context=context, output=output), [])
        self.assert_rejection({'knowledge_changes': [{**change, 'changes': {'kind': 'unregistered'}}],
                               'revision_resolutions': resolutions},
            'activity-extensions.json/knowledge_changes/0/changes/kind', 'revision kind must be registered',
            context=context, output=output)
