"""현재 없어진 과제·프로필과 후속 실행을 복구 선택으로 다시 광고하지 않는다."""
from copy import deepcopy
import unittest

from do_math import input_recovery, operational_dispositions
from do_math.task_contracts import TERMINAL_TASK_STATUSES
from support.record_builders import approved_task


class RecoveryChoiceTests(unittest.TestCase):
    def test_native_retry_preserves_incomplete_or_duplicate_outputs_and_obeys_the_current_limit(self):
        """T3 7.7 s: one actual failed native interpretation supplies all retained bytes."""
        from support.scheduling_initial import native_failure_sim
        import re
        sim = native_failure_sim()
        engine = sim.engine
        waiting = next(row for row in sim.runtime['waiting_actions'].values()
                       if row['action']['role'] == 'intent_interpretation')
        eid = waiting['execution_id']
        original_i, original_r = deepcopy(sim.instance), deepcopy(sim.runtime)
        self.assertTrue(original_r['executions'][eid]['outputs_complete'])
        self.assertTrue(original_r['executions'][eid]['output_files'])
        for case, reason in [('incomplete', 'native recovery requires complete preserved workspace outputs'),
                             ('duplicate', 'preserved native output differs from its execution manifest'),
                             ('limit', 'preserved native outputs exceed the current artifact limit')]:
            engine.instance, engine.runtime = deepcopy(original_i), deepcopy(original_r)
            execution = engine.runtime['executions'][eid]
            if case == 'incomplete':
                execution['outputs_complete'] = False
            elif case == 'duplicate':
                execution['output_files'].append(deepcopy(execution['output_files'][0]))
            else:
                engine.instance['config']['max_artifact_bytes'] = 1
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            stored = engine.store.load()
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                engine._resume_initial_native_final({'id': 'UC-native-guards'}, waiting, execution)
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
            self.assertEqual(engine.store.load(), stored)

    def test_native_retry_replays_the_durable_receipt_without_a_new_attempt(self):
        """T3 9.9 s: real capture and acceptance establish authority rejection and receipt replay."""
        from support.scheduling_initial import native_failure_sim
        sim = native_failure_sim()
        engine = sim.engine
        waiting = next(row for row in sim.runtime['waiting_actions'].values()
                       if row['action']['role'] == 'intent_interpretation')
        request = {'id': 'UC-native-replay', 'config': {'retry_action': waiting['action']['id']}}
        state = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^native recovery no longer has current request authority$'):
            engine._finish_native_recovery({'id': 'UC-never-captured'}, waiting['execution_id'])
        self.assertEqual((engine.head, engine.instance, engine.runtime), state)
        before = set(sim.runtime['executions'])
        first = engine._retry_input_overflow_action(request)
        self.assertEqual(set(sim.runtime['executions']), before)
        self.assertEqual(sim.runtime['executions'][waiting['execution_id']]['outcome'], 'output_accepted')
        execution = sim.runtime['executions'][waiting['execution_id']]
        activity = sim.runtime['activities'][execution['owner_activity_id']]
        pending = [row for row in engine.runtime['queue'] if row.get('owner_activity_id') == activity['id']]
        self.assertEqual([row['stage'] for row in pending], ['check'])
        self.assertEqual(activity['status'], 'ready')
        self.assertEqual(activity['result_refs'], [execution['result_ref']])
        self.assertEqual(activity['unresolved'], [])
        # The accepted native final has already produced its ready check in
        # this activity. Recovery can reenter before its public caller saves.
        queue = deepcopy(engine.runtime['queue'])
        receipt = deepcopy(execution['submission_receipt'])
        result = engine._finish_native_recovery(request, execution['id'])
        self.assertEqual(result['status'], 'accepted')
        self.assertEqual(engine.runtime['queue'], queue)
        self.assertEqual(engine.runtime['activities'][activity['id']]['status'], 'ready')
        self.assertEqual(engine.runtime['executions'][execution['id']]['submission_receipt'], receipt)
        engine._save()  # The public inbox caller publishes the completed recovery and its receipt together.
        published = deepcopy((engine.head, engine.instance, engine.runtime))
        self.assertEqual(engine._retry_input_overflow_action(request), first)
        self.assertEqual((engine.head, engine.instance, engine.runtime), published)
        self.assertEqual(engine.store.load()[2], sim.runtime)

    def test_initial_retry_refuses_changed_owner_overlap_and_a_duplicate_request(self):
        """T3 3.1 s: real registration checks overlap against the original waiting activity."""
        from support.scheduling_initial import adopted_sim, initial_failure
        from do_math import activities
        import re
        sim = adopted_sim()
        action, waiting = initial_failure(sim)
        engine = sim.engine
        original_i, original_r = deepcopy(engine.instance), deepcopy(engine.runtime)
        cases = [('owner', 'initial retry requires its original waiting activity'),
                 ('live', 'initial retry requires its original waiting activity'),
                 ('queued', 'initial retry action is already queued'),
                 ('diagnosis', 'initial retry cannot overlap its operational diagnosis')]
        for case, reason in cases:
            engine.instance, engine.runtime = deepcopy(original_i), deepcopy(original_r)
            activity = engine.runtime['activities'][action['owner_activity_id']]
            if case == 'owner':
                activities.resume_activity(engine.runtime, activity['id'],
                    condition=activity['waiting']['condition'], at=sim.clock.now())
            elif case in {'live', 'diagnosis'}:
                live = engine._register_execution({'id': 'AC-overlap', 'role': 'maintenance',
                    **({'owner_activity_id': activity['id']} if case == 'live' else
                       {'target': waiting['execution_id'], 'initial_submission_diagnosis': True})},
                    {'id': 'EX-overlap', 'role': 'maintenance'})
                self.assertIsNotNone(live)
            else:
                engine.runtime['queue'].append(deepcopy(action))
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                engine._validate_initial_retry(waiting)
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        engine.instance, engine.runtime = original_i, original_r
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^retry action differs from the held initial action$'):
            engine._retry_initial_execution_action({'id': 'UC-wrong', 'config': {'retry_action': 'AC-other'}}, waiting)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_overflow_retry_refuses_stale_owner_wait_and_overlapping_work(self):
        from support.engine_overflow import overflowed_sim, held
        from do_math import activities
        import re
        sim = overflowed_sim()
        engine = sim.engine
        identifier, waiting = held(sim)
        owner = waiting['action']['owner_activity_id']
        base_i, base_r = deepcopy(engine.instance), deepcopy(engine.runtime)
        cases = [('closed', 'closed/completed instance cannot retry an input overflow'),
            ('absent', 'retry_action must name a current input_overflow action'),
            ('queued', 'input_overflow action is already queued'),
            ('owner_absent', 'input_overflow owner activity is absent or finished'),
            ('owner_finished', 'input_overflow owner activity is absent or finished'),
            ('working', 'input_overflow owner activity is not waiting on this failure'),
            ('condition', 'activity wait does not name the held input_overflow action')]
        for case, reason in cases:
            engine.instance, engine.runtime = deepcopy(base_i), deepcopy(base_r)
            if case == 'closed': engine.runtime['status'] = 'closed'
            elif case == 'absent': del engine.runtime['waiting_actions'][identifier]
            elif case == 'queued': engine.runtime['queue'].append(deepcopy(waiting['action']))
            elif case == 'owner_absent': del engine.runtime['activities'][owner]
            elif case == 'owner_finished':
                activities.finish_activity(engine.runtime, owner, result_refs=[], unresolved=[], followups=[], at=sim.clock.now())
            elif case == 'working':
                activity = engine.runtime['activities'][owner]
                activities.resume_activity(engine.runtime, owner, condition=activity['waiting']['condition'], at=sim.clock.now())
            elif case == 'condition': engine.runtime['activities'][owner]['waiting']['condition'] = {'action_ids': ['AC-other']}
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                engine._resume_input_overflow_action(identifier, 'UC-retry')
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        engine.instance, engine.runtime = base_i, base_r
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        for value in (None, '', []):
            with self.subTest(retry_action=value), self.assertRaisesRegex(ValueError, '^retry_action must name one held action$'):
                engine._retry_input_overflow_action({'id': 'UC-retry', 'config': {'retry_action': value}})
        with self.assertRaisesRegex(ValueError, '^input_overflow retry question is unknown$'):
            engine._resolve_input_overflow_question('QU-missing', execution_id='EX-one', kind='accepted', evidence={})
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_absent_and_terminal_tasks_never_become_overflow_choices(self):
        task, instance, runtime = approved_task()
        runtime['waiting_actions'] = {'AC-size': {'kind': 'input_overflow', 'next_owner': 'research_plan',
            'action': {'role': 'research_work', 'target': task['id']}, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': []}}}
        for status in [None, *sorted(TERMINAL_TASK_STATUSES)]:
            with self.subTest(status=status):
                state = deepcopy(runtime)
                if status is None:
                    state['tasks'] = {}
                else:
                    state['tasks'][task['id']]['status'] = status
                before = deepcopy(state)
                self.assertEqual(input_recovery.overflow_requests(instance, state), [])
                self.assertEqual(state, before)

    def test_removed_profile_is_not_offered_and_wait_detail_is_detached(self):
        task, instance, runtime = approved_task()
        task['profile_refs'] = [{'id': 'PF-removed', 'revision': 1, 'sha256': 'b' * 64}]
        runtime['waiting_actions'] = {'AC-size': {'kind': 'input_overflow', 'next_owner': 'research_plan',
            'action': {'role': 'research_work', 'target': task['id'], 'owner_activity_id': 'AY-one',
                       'selected_contract_sha256': 'c' * 64}, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': ['PF-removed']}}}
        rows = input_recovery.overflow_requests(instance, runtime)
        self.assertEqual(rows, [{'action_id': 'AC-size', 'owner_activity_id': 'AY-one', 'task_id': task['id'],
            'contract_revision': task['revision'], 'contract_sha256': 'c' * 64, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': ['PF-removed']},
            'model_assessment': task.get('model_assessment'), 'allowed_profile_refs': []}])
        rows[0]['detail']['allowed_profile_candidates'].clear()
        self.assertEqual(runtime['waiting_actions']['AC-size']['detail']['allowed_profile_candidates'], ['PF-removed'])

    def test_unsupported_disposition_and_missing_execution_have_precise_reasons(self):
        for value in (None, [], {}, {'kind': 'made-up'}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '^operational disposition kind is unsupported$'):
                    operational_dispositions.validate_disposition(value)
        with self.assertRaisesRegex(ValueError, '^operational disposition has no execution target$'):
            operational_dispositions.admissible_basis_refs({}, {'executions': {}}, {'target': 'EX-missing'})

    def test_successor_evidence_and_superseded_receipt_are_exact(self):
        runtime = {'executions': {
            'EX-old': {'id': 'EX-old', 'owner_activity_id': 'AY-one', 'status': 'ended',
                       'action': {}, 'result_ref': 'old-result', 'pending_operational_disposition': 'OD-one'},
            'EX-new': {'id': 'EX-new', 'owner_activity_id': 'AY-one', 'status': 'ended',
                       'continuation_of': 'EX-old', 'result_ref': 'new-result'}},
            'queue': [], 'checkpoints': {'EX-old': {'artifact_ref': 'checkpoint'}}}
        refs = operational_dispositions.admissible_basis_refs({}, runtime, {'target': 'EX-old',
            'observation_refs': ['OF-one'], 'obligation_ids': ['OB-one']})
        self.assertEqual(refs, sorted(['EX-old', 'EX-new', 'old-result', 'new-result', 'checkpoint', 'OF-one', 'OB-one']))
        record = {'id': 'OD-one', 'status': 'proposed', 'target_execution_id': 'EX-old', 'disposition': {'kind': 'retry'}}
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime, record))
        self.assertEqual(record['result'], {'successor': {'state': 'continued', 'execution_ids': ['EX-new'],
                          'live_execution_ids': [], 'action_ids': []}})
        self.assertNotIn('pending_operational_disposition', runtime['executions']['EX-old'])
        before = deepcopy((runtime, record))
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime, record))
        self.assertEqual((runtime, record), before)
