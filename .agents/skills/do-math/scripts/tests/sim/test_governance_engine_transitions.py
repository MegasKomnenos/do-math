"""실제 엔진의 재해석·감사 봉인 전이와 무효 요청의 부작용 경계."""
from copy import deepcopy
import unittest

from support.governance_cases import auditor_sim, audit_output, question_sim
from support.governance_sim import checked_sim, checked_bundle


class GovernanceEngineTransitionTests(unittest.TestCase):
    def test_authority_wait_cannot_overlap_a_live_attempt_or_duplicate_its_queued_action(self):
        from do_math import governance as gov
        from do_math.execution_lifecycle import transition_execution
        from do_math.wait_rules import action_authority_wait
        from support.engine_lifecycle import clear_work
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='Preserve one action across an authority change')
        action = deepcopy(sim.runtime['queue'][0])
        execution = sim.engine._register_execution(action,
            {'id': 'EX-authority-in-flight', 'role': 'maintenance', 'status': 'running'})
        authority = gov.authorize(sim.instance, action, runtime=sim.runtime, at=sim.clock.now())
        source = sim.instance['grants'][authority['grant_id']]['source_ref']
        sim.engine.instance, sim.engine.runtime, _ = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'revoke', 'grant_id': authority['grant_id']}, source_ref=source, clock=sim.clock)
        denied = gov.authorize(sim.instance, action, runtime=sim.runtime, at=sim.clock.now())
        self.assertFalse(denied['allowed'])
        # The registered boundary accepts preserved waits; an old wait must
        # remain harmless if the same logical action already has a live attempt.
        sim.runtime.setdefault('waiting_actions', {})[action['id']] = action_authority_wait(action, denied)
        sim.engine.instance, sim.engine.runtime, _ = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'grant', 'grant': {'id': 'GR-restored-maintenance', 'kind': 'local',
                'roles': ['maintenance'], 'reuse': 'reusable'}}, source_ref=source, clock=sim.clock)
        self.assertTrue(gov.authorize(sim.instance, action, runtime=sim.runtime, at=sim.clock.now())['allowed'])
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._resume_action_authority_waits()
        self.assertEqual((sim.instance, sim.runtime), before)
        execution = sim.runtime['executions'][execution['id']]
        transition_execution(execution, 'stopping', at=sim.clock.now())
        transition_execution(execution, 'ended', at=sim.clock.now(), outcome='execution_incomplete')
        activity = deepcopy(sim.runtime['activities'][execution['owner_activity_id']])
        queue = deepcopy(sim.runtime['queue'])
        sim.engine._resume_action_authority_waits()
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertEqual(sim.runtime['activities'][activity['id']], activity)
        self.assertEqual(sum(row['id'] == action['id'] for row in queue), 1)
        released = deepcopy(sim.runtime)
        sim.engine._resume_action_authority_waits()
        self.assertEqual(sim.runtime, released)
        sim.engine._settle_activity(execution['id'])
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_applied_secondary_import_during_initialization_does_not_open_research(self):
        from do_math import governance as gov
        sim = checked_sim()
        bundle = checked_bundle(sim)
        draft = gov.import_approval_draft(sim.instance, sim.runtime, bundle['id'],
            owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        sim.engine.instance, sim.engine.runtime, _ = gov.apply_import_control(sim.instance, sim.runtime,
            {'id': 'DC-close-init-secondary', 'action': 'decision', 'origin': 'user', 'text': '후속 입력 승인', 'config': draft},
            owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        sim.instance['lifecycle']['state'] = 'initializing'
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._after_governance_import(bundle['id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_superseded_answered_import_wait_is_removed_without_rework(self):
        from do_math import governance as gov
        from support.governance_cases import question_bundle
        from support.governance_sim import returned
        sim = question_sim()
        bundle = question_bundle(sim)
        question = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        sim.engine.instance, sim.engine.runtime, _ = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'question_answer', 'text': '자연수다.', 'target_ids': [sim.instance['id']],
             'resolves_questions': [question['id']]}, source_ref=bundle['source']['id'], clock=sim.clock)
        output = deepcopy(bundle['output'])
        output['import_units'][0]['interpretation'] += ' 답변을 반영한다.'
        output['repair'] = {'previous_sha256': bundle['sha256'],
            'changed_unit_ids': [output['import_units'][0]['unit_id']], 'actions': ['답변을 반영해 재검토한다.']}
        action = {'id': 'AC-close-rework', 'role': 'intent_interpretation', 'target': bundle['input_ref'],
                  'previous_import_id': bundle['id']}
        returned(sim.engine, action, 'EX-close-rework')
        sim.engine._apply_governance_intent(action, output, 'EX-close-rework')
        queue = deepcopy(sim.runtime['queue'])
        waits = deepcopy(sim.runtime['waiting_actions'])
        expected = {key: row for key, row in waits.items() if row.get('import_id') != bundle['id']}
        sim.engine._resume_import_question_waits()
        self.assertEqual(sim.runtime['waiting_actions'], expected)
        self.assertEqual(sim.runtime['queue'], queue)

    def test_current_seal_finishes_duplicate_activity_without_new_unresolved_item(self):
        from support.governance_goal_seal import committed_goal_audit
        from support.governance_sim import returned
        from support.sim import Sim
        sim = Sim.activated()
        original, judgment = committed_goal_audit(sim)
        duplicate = {key: deepcopy(value) for key, value in original.items()
                     if key not in {'id', 'lineage_id', 'owner_activity_id'}}
        duplicate['id'] = 'AC-close-duplicate'
        sim.engine._enqueue(**duplicate)
        execution = returned(sim.engine, duplicate, 'EX-close-duplicate')
        activity = sim.runtime['activities'][execution['owner_activity_id']]
        sim.engine._save()
        activity = sim.runtime['activities'][activity['id']]
        old_results = deepcopy(activity['result_refs'])
        self.assertTrue(sim.engine._retire_sealed_goal_audit_requests())
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'], [])
        self.assertEqual(activity['result_refs'], old_results)
        self.assertEqual(activity['followups'], [{'action_id': duplicate['id'],
            'judgment_id': judgment['id'], 'reason': 'goal audit request superseded'}])

    def test_completed_goal_preserves_unprocessed_user_input_question(self):
        from support.governance_sim import theorem_sim, adopt_audit, goal_auditor
        sim = theorem_sim()
        adopt_audit(sim)
        request = sim.control('input', text='목표 해결 뒤에도 이 입력을 보존한다.', request_id='IN-close-pending')
        sim.engine.process_controls()
        action, output = goal_auditor(sim.engine, verdict='pass')
        before = deepcopy(sim.runtime['questions'])
        sim.engine._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertEqual(sim.instance['goal_status'], 'mathematically_solved')
        # 실제 사건 어휘는 생산자 AcademicEngineMixin._settle_goal_completion에 고정된다.
        events = [(index, row) for index, row in enumerate(sim.runtime['history'])
                  if row.get('kind') == 'goal_completion_superseded_action'
                  and row['action'].get('target') == request['request_id']]
        self.assertEqual(len(events), 1)
        index, event = events[0]
        self.assertEqual(event['action']['role'], 'intent_interpretation')
        expected = before + ['Goal completed before input ' + request['request_id']
            + ' was interpreted; the unprocessed request is preserved at runtime/history/' + str(index)]
        self.assertEqual(sim.runtime['questions'], expected)
        self.assertEqual(sim.runtime['history'][-1], {'kind': 'questions_preserved_at_goal_completion', 'questions': expected})

    def test_previous_import_is_copied_into_rework_context(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        action = {'role': 'intent_interpretation', 'target': bundle['input_ref'], 'previous_import_id': bundle['id']}
        before = deepcopy(sim.runtime)
        result = sim.engine._governance_context(action, {})
        self.assertEqual(result['previous_interpretation'], bundle)
        self.assertEqual(result['original_source'], bundle['source'])
        result['previous_interpretation']['output']['import_units'].clear()
        self.assertEqual(sim.runtime, before)

    def test_unapplied_import_does_not_trigger_followup(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._after_governance_import(bundle['id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_unanswered_import_questions_keep_waits_and_queue(self):
        sim = question_sim()
        before = deepcopy(sim.runtime)
        sim.engine._resume_import_question_waits()
        self.assertEqual(sim.runtime, before)

    def test_other_wait_kind_is_preserved(self):
        sim = checked_sim()
        before = deepcopy(sim.runtime)
        sim.engine._resume_import_question_waits()
        self.assertEqual(sim.runtime, before)

    def test_nonapproval_rejection_does_not_queue_reinterpretation(self):
        sim = checked_sim()
        before = deepcopy(sim.runtime)
        sim.engine._reject_governance_import({'action': 'input'}, '거부 사유')
        self.assertEqual(sim.runtime, before)

    def test_missing_import_rejection_does_not_queue_reinterpretation(self):
        sim = checked_sim()
        before = deepcopy(sim.runtime)
        sim.engine._reject_governance_import({'action': 'decision', 'config': {'change': {
            'kind': 'import_approval', 'import_id': 'missing'}}}, '거부 사유')
        self.assertEqual(sim.runtime, before)

    def test_superseded_import_rejection_does_not_queue_reinterpretation(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        bundle['superseded_by'] = 'IM-next'
        before = deepcopy(sim.runtime)
        sim.engine._reject_governance_import({'action': 'decision', 'config': {'change': {
            'kind': 'import_approval', 'import_id': bundle['id']}}}, '거부 사유')
        self.assertEqual(sim.runtime, before)

    def test_changed_original_queues_fresh_lineage_before_check_rejection(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        action = deepcopy(sim.runtime['executions'][bundle['check']['execution_id']]['action'])
        request = next(row for row in sim.runtime['inputs'] if row['id'] == bundle['input_ref'])
        request['text'] += ' 명시한 변경'
        before = deepcopy(sim.runtime['queue'])
        check = deepcopy(bundle['check'])
        with self.assertRaisesRegex(ValueError, '^original source changed before independent check$'):
            sim.engine._apply_governance_intent(action, check, check['execution_id'])
        self.assertEqual(sim.runtime['queue'][:-1], before)
        queued = sim.runtime['queue'][-1]
        self.assertEqual((queued['role'], queued['stage'], queued['target']),
                         ('intent_interpretation', 'interpret', bundle['input_ref']))
        self.assertNotIn('previous_import_id', queued)
        self.assertEqual(queued['intent_repair'], {
            'import_id': bundle['id'], 'previous_sha256': bundle['sha256'],
            'check_execution_id': check['execution_id'],
            'findings': ['original source changed before independent check']})
        self.assertEqual(bundle['check'], check)
        sim.engine.store.validate_candidate(sim.instance, sim.runtime)

    def test_audit_schema_adds_required_field_without_changing_argument(self):
        sim = auditor_sim()
        schema = {'type': 'object', 'properties': {}, 'required': []}
        before = deepcopy(schema)
        result = sim.engine._governance_schema({'role': 'goal_audit'}, schema)
        self.assertEqual(schema, before)
        self.assertEqual(result['required'], ['additional_audits'])
        self.assertEqual(result['properties']['additional_audits']['minItems'], 1)
        self.assertEqual(result['properties']['additional_audits']['maxItems'], 1)
        self.assertEqual(sim.engine._governance_schema({'role': 'goal_audit'}, result), result)

    def test_missing_committed_audit_returns_none_without_mutation(self):
        sim = auditor_sim()
        before = deepcopy((sim.instance, sim.runtime))
        self.assertIsNone(sim.engine._committed_goal_audit('missing'))
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_seal_count_conflict_is_rejected_without_mutation(self):
        sim = auditor_sim()
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        sim.engine._apply_governance_goal_audit(action, audit_output(sim), 'EX-close-auditor')
        action['required'] = 3
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^conflicting goal audit slot seals$'):
            sim.engine._goal_audit_seal(action)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_seal_producer_role_change_is_rejected_without_mutation(self):
        sim = auditor_sim()
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        sim.engine._apply_governance_goal_audit(action, audit_output(sim), 'EX-close-auditor')
        sim.runtime['executions']['EX-close-auditor']['role'] = 'maintenance'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^goal audit seal differs from its producer$'):
            sim.engine._goal_audit_seal(action)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_existing_audit_group_cannot_change_required_count(self):
        sim = auditor_sim()
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        sim.engine._apply_governance_goal_audit(action, audit_output(sim), 'EX-close-auditor')
        second = {**action, 'slot': 1}
        sim.instance['goal_judgments'][-1]['required'] = 3
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^goal audit group has inconsistent slots or counts$'):
            sim.engine._apply_governance_goal_audit(second, audit_output(sim), 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
