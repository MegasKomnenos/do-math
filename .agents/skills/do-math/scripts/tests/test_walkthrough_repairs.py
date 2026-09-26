"""Regression cases for the producer/consumer walkthrough (no model calls)."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash

from do_math import governance as gov, planning, submission, task_contracts


class WalkthroughRepairs(unittest.TestCase):
    def test_processed_rejection_cannot_erase_a_fresh_equal_or_changed_assessment(self):
        from do_math.scheduler import SchedulerMixin
        from do_math.model_policy import assessment_basis, LIMITS
        from test_redesign_TASKS import approved_fixture
        from test_model_assessment_flow import rating
        from research_fixtures import prepared_rule_conditions
        class Host(SchedulerMixin):
            pass
        for unchanged in (False, True):
            with self.subTest(unchanged=unchanged):
                task, instance, runtime = approved_fixture()
                rules = prepared_rule_conditions([task['id']])[0]['observation_rules']
                task['initial_observation_rules'] = deepcopy(rules)
                instance['config'] = {'session_limits': deepcopy(LIMITS)}
                task.update(academic_requirement_id='R', revision_requested={'execution_id': 'REJECT'},
                    model_assessment=rating())
                task['reviews'] = [{**assessment_basis(task), 'decision': 'revision_required', 'execution_id': 'REJECT'}]
                host = Host(); host.instance = instance; host.runtime = runtime
                host._ensure_model_assessments()
                revised = rating() if unchanged else {**rating(), 'importance': 'high'}
                task['model_assessment'] = deepcopy(revised)
                task['initial_observation_rules'] = deepcopy(rules)
                runtime['queue'] = [{'id': 'NEW-REVIEW', 'role': 'task_contract_review', 'target': task['id']}]
                for _ in range(3):
                    host._ensure_model_assessments()
                self.assertEqual(task['model_assessment'], revised)
                self.assertEqual(len(task['model_assessment_history']), 1)
                self.assertEqual([a['id'] for a in runtime['queue']], ['NEW-REVIEW'])
                task['reviews'].append({**assessment_basis(task), 'decision': 'unresolved', 'execution_id': 'REJECT-NEW'})
                host._ensure_model_assessments()
                self.assertNotIn('model_assessment', task)
                self.assertEqual(len(task['model_assessment_history']), 2)

    def test_intent_input_exposes_actual_consumers_and_exact_source(self):
        from test_governance_engine import CentralGovernanceTests
        host, _, _ = CentralGovernanceTests().host()
        host.runtime['inputs'] = [{'id': 'UI-exact', 'text': 'e\u0301 has two code points', 'config': {}}]
        context = host._governance_context({'role': 'intent_interpretation', 'target': 'UI-exact'}, {})
        self.assertEqual(context['user_request']['text'], context['original_source']['text'])
        kinds = {row['owner_kind'] for row in context['import_consumers']}
        self.assertEqual(kinds, gov.GOVERNANCE_KINDS | {'grant', 'revoke', 'delegation', 'question_answer',
            'task_scope'} | set(host._governance_owner_handlers()))
        self.assertEqual(context['governance_records'], list(host.instance['governance'].values()))
        for row in context['import_consumers']:
            document = Path(__file__).resolve().parents[2] / row['payload_contract']['document']
            self.assertIn(row['owner_kind'], document.read_text(encoding='utf-8'))

    def test_initial_configuration_keeps_its_owner_through_completion(self):
        from test_initial_intent_connection import InitialIntentConnectionTests
        from do_math.initialization import initial_intent_evidence
        from do_math.engine import DEFAULT_CONFIG
        instance, runtime, _ = InitialIntentConnectionTests().applied('Use this exact configuration')
        instance['config'] = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
        source = gov.import_input_source(instance, runtime, instance['lifecycle']['input_id'])
        def configure(i, r, unit, approval):
            changed = deepcopy(i)
            changed['config'].update(unit['payload']['config'])
            return changed, deepcopy(r)
        handlers = gov.register_configuration_owner(gov.import_owner_handlers(), apply=configure)
        payload = {'kind': 'configuration', 'config': {'effort': 'high'}}
        output = {'questions': [], 'question_details': [], 'needs_clarification': False,
            'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                'interpretation': 'Use the approved effort', 'owner_kind': 'configuration',
                'owner_ref': instance['id'], 'payload': payload, 'decision_refs': [], 'question_refs': []}]}
        runtime['executions']['EX-config-author'] = {'id': 'EX-config-author', 'role': 'intent_interpretation'}
        bundle = gov.prepare_import(instance, runtime, source, output, execution_id='EX-config-author',
            input_ref=instance['lifecycle']['input_id'], owner_handlers=handlers)
        runtime['executions']['EX-config-check'] = {'id': 'EX-config-check', 'role': 'intent_interpretation',
            'intent_import_sha256': bundle['sha256']}
        bundle = gov.check_import(instance, runtime, bundle['id'], {'bundle_sha256': bundle['sha256'],
            'decision': 'approved', 'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []},
            execution_id='EX-config-check', owner_handlers=handlers)
        instance, runtime, _ = gov.apply_import_control(instance, runtime, {'id': 'APPROVAL-config',
            'action': 'decision', 'origin': 'user', 'text': 'Approve this exact effort', 'config': {
                'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                'check_sha256': bundle['check']['sha256'], 'unit_hashes': {'U': exact_content_hash(payload)}}},
            owner_handlers=handlers)
        self.assertEqual(instance['config']['effort'], 'high')
        receipt = initial_intent_evidence(instance, runtime, owner_handlers=handlers)
        self.assertEqual(receipt['interpretation_execution_id'], 'EX-config-author')

    def test_initial_advisory_question_does_not_become_a_blocking_gate(self):
        from test_initial_intent_connection import InitialIntentConnectionTests
        from do_math.initialization import initial_intent_evidence
        instance, runtime, original_id = InitialIntentConnectionTests().applied('Prove the stated goal')
        original = runtime['intent_imports'][original_id]
        output = deepcopy(original['output'])
        uid = output['import_units'][0]['unit_id']
        output.update(questions=['Optional presentation preference?'], needs_clarification=True,
            question_details=[{'id': 'Q-advice', 'question_index': 0, 'target_ids': [instance['id']],
                'blocks': False, 'reason': 'Presentation preference is optional', 'source_unit_ids': [uid], 'options': []}])
        output['import_units'][0]['question_refs'] = ['Q-advice']
        runtime['executions']['EX-advice'] = {'role': 'intent_interpretation'}
        bundle = gov.prepare_import(instance, runtime, original['source'], output, execution_id='EX-advice',
            input_ref=instance['lifecycle']['input_id'])
        runtime['executions']['EX-advice-check'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        gov.check_import(instance, runtime, bundle['id'], {'decision': 'approved', 'scope_complete': True,
            'bundle_sha256': bundle['sha256'], 'unit_ids': [uid], 'question_ids': ['Q-advice'], 'findings': []},
            execution_id='EX-advice-check')
        instance, runtime, receipt = gov.apply_import(instance, runtime, bundle['id'])
        self.assertEqual(receipt['status'], 'applied')
        self.assertEqual(initial_intent_evidence(instance, runtime)['interpretation_execution_id'], 'EX-advice')
        self.assertEqual(runtime['question_links'][-1]['status'], 'open')

    def test_unrelated_progress_preserves_checked_import_but_relevant_changes_do_not(self):
        from test_redesign_GOVERNANCE import AuditRepairTests
        instance, runtime, bundle, request = AuditRepairTests().checked_import()
        runtime['tasks']['TK-other'] = {'id': 'TK-other', 'revision': 2, 'status': 'active', 'question': 'Unrelated'}
        instance['decisions']['DC-other'] = {'id': 'DC-other', 'change': {'note': 'Unrelated'}}
        changed, _, receipt = gov.apply_import_control(instance, runtime, request)
        self.assertEqual(receipt['status'], 'applied')
        self.assertEqual(gov.governance_view(changed)['goal'], 'Prove Q')
        instance['decisions']['D']['revoked'] = True
        with self.assertRaises(ValueError):
            gov.apply_import_control(instance, runtime, request)

    def test_initial_blocking_question_waits_and_answer_reopens_original_once(self):
        from datetime import datetime, timezone
        from unittest.mock import patch
        from test_governance_engine import CentralGovernanceTests
        from do_math.lifecycle_engine import LifecycleEngineMixin
        host, _, _ = CentralGovernanceTests().host()
        text = 'Which domain?'
        source = gov.preserve_source('UNUSED', text, origin='user')
        host.instance['lifecycle'] = {'state': 'initializing', 'input_id': 'UI-original',
            'immutable_input': {k: source[k] for k in ('text', 'sha256', 'bytes')},
            'adoption': {'initial_profile_ref': {'id': 'P'}, 'initial_grant_ids': ['GR-initial']}}
        host.instance['grants']['GR-initial'] = {'roles': ['intent_interpretation']}
        host.runtime['inputs'] = [{'id': 'UI-original', 'text': text, 'config': {}}]
        host.runtime['queue'] = []
        host.runtime['waiting_actions'] = {}
        action = {'id': 'AC-interpret', 'role': 'intent_interpretation', 'target': 'UI-original', 'stage': 'interpret'}
        host.runtime['executions']['AUTHOR'] = {'id': 'AUTHOR', 'role': 'intent_interpretation', 'status': 'ended', 'action': action}
        output = {'questions': [text], 'needs_clarification': True, 'question_details': [{'id': 'Q-domain',
            'question_index': 0, 'target_ids': [host.instance['id']], 'blocks': True, 'reason': 'Domain is needed',
            'source_unit_ids': ['U'], 'options': []}], 'import_units': [{'unit_id': 'U',
            'source_range': {'start': 0, 'end': len(text)}, 'interpretation': 'Ask the domain',
            'owner_kind': 'charter', 'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': ['Q-domain']}]}
        bundle = host._apply_governance_intent(action, output, 'AUTHOR')
        check = host.runtime['queue'].pop()
        host.runtime['executions']['CHECK'] = {'id': 'CHECK', 'role': 'intent_interpretation', 'status': 'ended',
            'intent_import_sha256': bundle['sha256'], 'action': check}
        host._apply_governance_intent(check, {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
            'scope_complete': True, 'unit_ids': ['U'], 'question_ids': ['Q-domain'], 'findings': []}, 'CHECK')
        self.assertEqual(len(host.runtime['waiting_actions']), 1)
        host._capability_requirements = lambda ref: {'satisfied': True}
        host._lifecycle_now = lambda: datetime.now(timezone.utc)
        with patch('do_math.initialization.grant_current', return_value=True):
            for _ in range(3):
                LifecycleEngineMixin._queue_initial_intent(host)
        self.assertEqual(host.runtime['queue'], [])
        question = host.runtime['question_links'][-1]
        host.instance, host.runtime, _ = gov.apply_decision(host.instance, host.runtime,
            {'kind': 'question_answer', 'text': 'Natural numbers', 'target_ids': [host.instance['id']],
             'resolves_questions': [question['id']]}, source_ref='S')
        host._resume_import_question_waits()
        host._resume_import_question_waits()
        self.assertEqual(len(host.runtime['queue']), 1)
        self.assertEqual(host.runtime['queue'][0]['previous_import_id'], bundle['id'])
        self.assertEqual(host.runtime['queue'][0]['target'], 'UI-original')
        self.assertEqual(host.runtime['waiting_actions'], {})

    def test_question_references_are_stable_ids_at_both_boundaries(self):
        from test_redesign_GOVERNANCE import DomainGovernanceTests
        instance = DomainGovernanceTests().initial()
        source = gov.preserve_source('SOURCE', 'Which domain?', origin='user')
        output = {'questions': ['Which domain?'], 'needs_clarification': True,
            'question_details': [{'id': 'Q-domain', 'question_index': 0,
                'target_ids': [instance['id']], 'blocks': True, 'reason': 'Domain changes the goal',
                'source_unit_ids': ['U'], 'options': []}],
            'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                'interpretation': 'The domain needs a user decision', 'owner_kind': 'charter',
                'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': ['Q-domain']}]}
        gov.validate_import_units(instance, {}, source, output)
        self.assertEqual(submission._intent_import_issues(output, {'user_request': {'text': source['text']}}), [])
        output['import_units'][0]['question_refs'] = ['output/questions/0']
        self.assertTrue(submission._intent_import_issues(output, {'user_request': {'text': source['text']}}))

    def test_primary_and_extension_dependencies_are_preserved(self):
        candidate = {'dependencies': ['TK-existing']}
        self.assertEqual(task_contracts.prepared_dependencies(candidate, {'observation_rules': []}), ['TK-existing'])
        self.assertEqual(task_contracts.prepared_dependencies(candidate,
            {'dependencies': ['new task', 'TK-existing']}, {'new task': 'TK-new'}), ['TK-existing', 'TK-new'])

    def test_engine_preserves_primary_dependency_when_extension_only_sets_condition(self):
        from types import SimpleNamespace
        from do_math.scheduler import SchedulerMixin
        from do_math.engine import ResearchEngine
        from test_redesign_TASKS import approved_fixture
        from research_fixtures import candidate
        prior, instance, runtime = approved_fixture()
        proposal = candidate('Followup')
        proposal['dependencies'] = [prior['id']]
        runtime.update(cycles=0, executions={'EX-prepare': {'status': 'ended', 'extensions': {
            'task_conditions': [{'task_title': 'Followup', 'occurrence_condition': {'op': 'always'}}]}}})
        class Host(SchedulerMixin, SimpleNamespace):
            pass
        host = Host(instance=instance, runtime=runtime,
            _record_output_questions=lambda *args, **kwargs: None, _evaluation_context=lambda: {},
            _available_inputs=lambda: [], _governance=lambda: gov.governance_view(instance))
        host._enqueue = lambda role, target=None, **fields: runtime['queue'].append(
            {'id': gov.new_id('AC'), 'role': role, 'target': target, **fields})
        ResearchEngine._apply(host, {'role': 'research_preparation'}, {'candidates': [proposal]}, 'EX-prepare')
        applied = next(t for t in runtime['tasks'].values() if t.get('title') == 'Followup')
        self.assertEqual(applied['dependencies'], [prior['id']])
        self.assertEqual(applied['occurrence_condition']['args'][1]['task_id'], prior['id'])

    def test_required_certification_condition_tracks_current_identity_effect(self):
        from test_redesign_KNOWLEDGE import KnowledgeRedesign
        instance, runtime, kid, _ = KnowledgeRedesign().verified()
        condition = {'op': 'record_field_equals', 'space': 'research', 'family': 'knowledge',
            'record_id': kid, 'pointer': '/usable_as_k', 'value': True}
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime)['state'], 'ready')
        for use in instance['assessment_uses'].values():
            use['status'] = 'suspended'
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime)['state'], 'not_ready')
        with self.assertRaises(ValueError):
            planning.validate_condition({**condition, 'value': 1})

    def test_documented_readiness_examples_match_the_live_grammar(self):
        import re
        path = Path(__file__).resolve().parents[2] / 'references' / '과제-착수조건.md'
        blocks = re.findall(r'```json\s+(.*?)```', path.read_text(encoding='utf-8'), re.S)
        self.assertGreaterEqual(len(blocks), 2)
        for block in blocks:
            value = json.loads(block)
            conditions = [value] if 'op' in value else [row['occurrence_condition'] for row in value['task_conditions']]
            for condition in conditions:
                planning.validate_condition(condition)

    def test_interpretation_binds_referenced_source_alias(self):
        from test_redesign_GOVERNANCE import DomainGovernanceTests
        instance, runtime, source, output = DomainGovernanceTests().import_fixture()
        instance['sources'] = [{'id': 'SO-table', 'name': 'table.txt', 'path': 'sources/table.txt', 'sha256': 'a'*64}]
        output['used_sources'] = ['source:table.txt']
        bundle = gov.prepare_import(instance, runtime, source, output, execution_id='AUTHOR')
        instance['sources'][0]['sha256'] = 'b'*64
        with self.assertRaisesRegex(ValueError, 'targets changed'):
            gov._current_import(instance, runtime, bundle['id'])

    def test_research_reuse_keeps_dependency_and_source_currentness(self):
        from do_math.knowledge import assess_research_use
        from do_math.knowledge_records import create_candidate
        instance = {'sources': [{'id': 'S', 'name': 'data', 'sha256': 'a'*64, 'path': 'data'}],
            'kind_definitions': {'KD': {'id': 'KD', 'status': 'active'}}}
        instance, parent = create_candidate(instance, {'id': 'KN-parent', 'kind_definition_id': 'KD',
            'statement': 'Finite observation', 'source_basis': [{'name': 'data', 'sha256': 'a'*64}]},
            source_ref='S', actor_ref='AUTHOR')
        instance, child = create_candidate(instance, {'id': 'KN-child', 'kind_definition_id': 'KD',
            'statement': 'Uses that observation', 'dependencies': [parent]}, source_ref='S', actor_ref='AUTHOR')
        self.assertTrue(assess_research_use(instance['knowledge'][child], instance)['valid'])
        instance['sources'][0]['sha256'] = 'b'*64
        self.assertFalse(assess_research_use(instance['knowledge'][child], instance)['valid'])

    def test_assessment_only_input_contains_waiting_contract_and_review_history(self):
        from test_redesign_SURFACE import surface_state
        from do_math.context_store import prepare_role_input
        instance, runtime = surface_state()
        task = {'id': 'TK-rejected', 'status': 'waiting', 'question': 'Compare the two methods',
            'reviews': [{'execution_id': 'EX-review', 'decision': 'revision_required'}],
            'model_assessment_history': [{'assessment': {'difficulty': 'high'}}]}
        runtime['tasks'] = {task['id']: task}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_preparation')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'action': {'id': 'A', 'role': 'research_preparation',
                'assessment_targets': {task['id']: {'revision': 1}}}, 'resources': {},
                'tasks': [deepcopy(task)], 'knowledge_catalog': [], 'blocked_actions': []},
                instance=instance, runtime=runtime, role='research_preparation', profile=profile,
                snapshot='a'*40, workspace=root, activity_id='ACT', install_submission_tools=True,
                max_artifact_bytes=100000)
            supplied = fitted['context']['tasks']
            self.assertEqual([t['id'] for t in supplied], [task['id']])
            original = json.loads((root / supplied[0]['source_ref']['path']).read_bytes())
            self.assertEqual(original, task)
            checked = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertEqual(checked['tasks'], [task])

    def test_nonformal_research_reuse_is_ready_but_not_certified(self):
        from test_redesign_TASKS import approved_fixture, approve
        from do_math.knowledge import assess_use
        from do_math.knowledge_records import create_candidate
        task, instance, runtime = approved_fixture()
        instance.setdefault('kind_definitions', {})['KD-observation'] = {'id': 'KD-observation', 'status': 'active'}
        instance, kid = create_candidate(instance, {'id': 'KN-computation', 'kind': 'observation',
            'kind_definition_id': 'KD-observation', 'statement': 'Computed n=1 through 20',
            'explanation': 'Bounded exact computation', 'summary': 'Finite evidence', 'dependencies': []},
            source_ref='SO-1', actor_ref='EX-compute')
        task['reuse'] = [kid]
        approve(task, instance, runtime)
        self.assertFalse(assess_use(instance['knowledge'][kid], instance)['valid'])
        self.assertEqual(planning.task_ready(task, instance, runtime)['state'], 'ready')
        for field, value in [('lifecycle', 'withdrawn'), ('use_suspended', True), ('kind_use_suspended', True)]:
            changed = deepcopy(instance)
            changed['knowledge'][kid][field] = value
            approve(task, changed, runtime)
            self.assertEqual(planning.task_ready(task, changed, runtime)['state'], 'not_ready', field)

    def test_documented_research_grant_permits_formal_check(self):
        path = Path(__file__).resolve().parents[2] / 'references' / '초기화-운전.md'
        blocks = path.read_text(encoding='utf-8').split('```json\n')[1:]
        grant = next(json.loads(block.split('```')[0])['grant'] for block in blocks
                     if '"id": "GR-research-01"' in block.split('```')[0])
        grant['status'] = 'active'
        self.assertTrue(gov.authorize({'grants': {grant['id']: grant}}, {'role': 'formal_check'},
            at='2026-09-22T00:00:00+00:00')['allowed'])


if __name__ == '__main__':
    unittest.main()
