"""7-A/2-D finite long exploration and explicit alphabet reachability witnesses.

The twelve LONG alphabets already live in the three current role-family modules; these are the remaining seeds.
LONG stays six examples of twenty events; per-event detection is at most twelve
owner passes and each public start producer at most sixty. No sleeps/retries.
"""
from copy import deepcopy
import unittest

from support.cross_contracts import ContractOracle
from support.cross_machine import LONG, assert_machine
from support.cross_obligations import assert_independent_actions, assert_preserved_reasons, actions
from support.cross_research_machine import (AlphabetMachine, ReviewAlphabetMachine, OperationAlphabetMachine,
    InvestigationAlphabetMachine, CheckpointAlphabetMachine, AssessmentAlphabetMachine,
    KindAlphabetMachine, ImpactAlphabetMachine, InitialDiagnosisAlphabetMachine)
from support.cross_states import (activate, applied, drive, assert_event, queued, plan_ready, review_stage,
    goal_ready, investigation_ready, failure_ready, interpretation_ready, returned_plan, waived_plan, checkpoint_failure)
from support.sim import warm_template

setUpModule = warm_template




class RequiredEventSeedTests(unittest.TestCase):
    def test_closed_initialization_absorbs_real_restart_and_owner_events(self):
        machine = InitialDiagnosisAlphabetMachine()
        self.addCleanup(machine.teardown)
        machine.close()
        before = deepcopy(machine.sim.runtime['executions'])
        machine.owner_pass()
        machine.contracts_after_every_event()
        machine.restart()
        machine.owner_pass()
        machine.contracts_after_every_event()
        self.assertEqual(machine.sim.runtime['status'], 'closed')
        self.assertEqual(machine.sim.runtime['executions'], before)
        self.assertEqual([event[0] for event in machine.events[-3:]], ['step', 'restart', 'step'])

    def test_unknown_invariant_at_closed_initialization_propagates(self):
        machine = InitialDiagnosisAlphabetMachine()
        self.addCleanup(machine.teardown)
        machine.close()
        check = machine.oracle.check
        def unknown(sim):
            check(sim)
            raise AssertionError('independent unknown invariant at initialization stop')
        machine.oracle.check = unknown
        with self.assertRaisesRegex(AssertionError, '^independent unknown invariant at initialization stop$'):
            machine.owner_pass()
            machine.contracts_after_every_event()

    def test_closed_initialization_owner_keeps_the_terminal_receipt(self):
        machine = InitialDiagnosisAlphabetMachine()
        self.addCleanup(machine.teardown)
        machine.close()
        before = deepcopy(machine.sim.runtime)
        machine.owner_pass()
        machine.contracts_after_every_event()
        self.assertEqual(machine.sim.runtime['status'], 'closed')
        self.assertEqual(machine.sim.runtime['executions'], before['executions'])
        self.assertEqual(machine.sim.runtime['processed_controls'], before['processed_controls'])

    def test_operational_question_reaches_its_actual_producer_and_receiver(self):
        sim = failure_ready()
        action = deepcopy(queued(sim, 'operational_review'))
        observed = assert_event(sim, action, 'operation', 'user_decision')
        self.assertEqual(observed['output']['disposition']['kind'], 'user_decision')

    def test_requested_maintenance_during_review_uses_a_normal_role_response(self):
        machine = ReviewAlphabetMachine()
        self.addCleanup(machine.teardown)
        for event in ('owner_pass', 'restart', 'request_maintenance', 'owner_pass',
                      'restart', 'request_maintenance', 'owner_pass', 'owner_pass',
                      'change_requirements', 'owner_pass'):
            getattr(machine, event)()
            machine.contracts_after_every_event()
        self.assertIn('maintenance', [call['role'] for call in machine.sim.model.calls])
        self.assertEqual(machine.sim.model.responder.failures, [])

    def test_closure_preserves_reasons_and_continues_following_real_events(self):
        machine = AssessmentAlphabetMachine()
        self.addCleanup(machine.teardown)
        machine.retire_knowledge(0)
        machine.contracts_after_every_event()
        before = deepcopy(machine.oracle.requests)
        machine.close()
        machine.contracts_after_every_event()
        machine.owner_pass()
        machine.contracts_after_every_event()
        machine.restart()
        machine.contracts_after_every_event()
        assert_preserved_reasons(before, machine.sim.runtime)
        self.assertEqual(machine.sim.runtime['status'], 'closed')
        self.assertEqual([event[0] for event in machine.events[-3:]], ['close', 'step', 'restart'])

    def test_unknown_invariant_after_known_closure_propagates_from_generation(self):
        from hypothesis.stateful import invariant
        from support.cross_machine import SHORT
        class UnknownAfterClosure(AssessmentAlphabetMachine):
            def __init__(self):
                super().__init__()
                self.retire_knowledge(0)
                self.contracts_after_every_event()
                self.close()

            @invariant()
            def contracts_after_every_event(self):
                super().contracts_after_every_event()
                if self.sim.runtime['status'] == 'closed':
                    assert False, 'unknown invariant after the actual closure'

        with self.assertRaisesRegex(AssertionError, '^unknown invariant after the actual closure$'):
            assert_machine(UnknownAfterClosure, SHORT)

    def test_close_preserves_actual_merged_requests_and_receipt(self):
        machine = AssessmentAlphabetMachine()
        self.addCleanup(machine.teardown)
        machine.retire_knowledge(0)
        machine.contracts_after_every_event()
        before = deepcopy(machine.oracle.requests)
        self.assertTrue(before)
        machine.close()
        machine.contracts_after_every_event()
        assert_preserved_reasons(before, machine.sim.runtime)

    def test_public_delegation_cannot_manufacture_a_review_replacement_original(self):
        sim = review_stage()
        action = deepcopy(queued(sim, 'identity_review'))
        self.assertIsNotNone(action)
        before = deepcopy(sim.instance['decisions'])
        for change, reason in (
            ({'kind': 'review_replacement', 'action': action},
             'unsupported governance decision: review_replacement'),
            ({'kind': 'delegation', 'delegation': {
                'id': 'DG-cross-missing-original', 'status': 'active',
                'decision_kind': 'review_replacement', 'original_decision_id': 'DC-cross-not-produced',
                'included_targets': [action['target']], 'excluded_targets': [],
                'external_effects': [], 'resource_limits': {}, 'expires_at': None}},
             'delegation must bind an actual current user decision of the same kind'),
        ):
            request = sim.control('decision', text='Authorize exactly this review replacement', config={'change': change})
            sim.engine.process_controls()
            result = sim.engine.control_result(request['request_id'])
            self.assertEqual(result['effect'], 'rejected')
            self.assertEqual(result['reason'], reason)
            self.assertEqual(sim.instance['decisions'], before)
            self.assertFalse(sim.runtime.get('delegation_applications'))
        sim.restart()
        self.assertEqual(sim.instance['decisions'], before)
        ContractOracle(sim).check(sim)

    def test_control_alphabet_preserves_user_stop_and_terminal_authority(self):
        machine = AlphabetMachine()
        try:
            machine.hold()
            machine.pause()
            stop = deepcopy(machine.sim.runtime['user_pause'])
            machine.release_hold()
            self.assertEqual(machine.sim.runtime['user_pause'], stop)
            self.assertEqual(machine.sim.runtime['status'], 'paused')
            machine.resume()
            machine.quiesce()
            machine.release_quiesce()
            machine.configure(3)
            machine.configure_capacity(2)
            machine.advance(1)
            machine.owner_pass()
            machine.restart()
            machine.contracts_after_every_event()
            machine.close()
            ended = set(machine.sim.runtime['executions'])
            machine.resume()
            machine.owner_pass()
            machine.restart()
            self.assertEqual(machine.sim.runtime['status'], 'closed')
            self.assertEqual(set(machine.sim.runtime['executions']), ended)
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_import_retirement_and_audit_requests_preserve_explicit_values(self):
        machine = AlphabetMachine()
        try:
            for requested in (False, True):
                if not machine.ready('research_plan'):
                    machine.control('request', config={'role': 'research_plan'}, text='Compare the current audit need')
                self.assertTrue(machine.ready('research_plan'))
                observed = machine.answer('research_plan', 'audit', requested)
                self.assertIs(observed['output']['goal_audit'], requested)
                machine.contracts_after_every_event()
            before = set(machine.sim.instance['knowledge'])
            machine.import_knowledge()
            added = set(machine.sim.instance['knowledge']) - before
            self.assertEqual(len(added), 1)
            index = next(i for i, row in enumerate(machine.sim.instance['knowledge'].values()) if row['id'] in added)
            machine.retire_knowledge(index)
            self.assertEqual(machine.sim.instance['knowledge'][next(iter(added))]['lifecycle'], 'withdrawn')
            machine.restart()
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_academic_requirements_preserve_audit_and_mathematical_goal_change_retires_it(self):
        from support.cross_research_machine import TaskOperationAlphabetMachine
        from support.state_builders import charter_change
        machine = TaskOperationAlphabetMachine()
        try:
            machine.request_audit(True)
            old = deepcopy(queued(machine.sim, 'goal_audit'))
            self.assertIsNotNone(old)
            self.assertTrue(machine.ready('goal_audit'))
            machine.change_requirements()
            self.assertEqual(old['basis'], machine.sim.engine._goal_basis_key())
            self.assertEqual(machine.current_action('goal_audit')['id'], old['id'])
            self.assertTrue(machine.ready('goal_audit'))
            self.assertEqual(machine.sim.model.responder.pending, {})
            machine.control('decision', config={'change': charter_change(machine.sim.engine,
                goal=machine.sim.engine._governance()['goal'] + ' with the mathematical target explicitly changed')})
            self.assertNotEqual(old['basis'], machine.sim.engine._goal_basis_key())
            self.assertIsNone(machine.current_action('goal_audit'))
            self.assertFalse(machine.ready('goal_audit'))
            self.assertEqual(machine.sim.model.responder.pending, {})
            drive(machine.sim, lambda s: not any(a['id'] == old['id'] for a in s.runtime['queue']), bound=12)
            self.assertFalse(any(c['action']['id'] == old['id'] for c in machine.sim.model.calls))
            machine.restart()
            self.assertFalse(any(a['id'] == old['id'] for a in machine.sim.runtime['queue']))
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_repeated_goal_changes_choose_unblocked_review_and_preserve_revision_wait(self):
        """축소된 사건 열에서 막힌 첫 검토와 응답 가능한 다른 검토를 구분한다."""
        from support.cross_research_machine import TaskOperationAlphabetMachine
        from do_math.planning import revision_waits
        machine = TaskOperationAlphabetMachine()
        try:
            machine.restart()
            machine.request_operational_revision()
            # Keep this Root regression's failed-writer wait explicit. The
            # default cross writer now resolves its actual revision targets.
            from support.model import raw
            writers = [a for a in machine.sim.runtime['queue']
                       if a['role'] == 'research_preparation' and a.get('revision_targets')]
            self.assertTrue(writers)
            for writer in writers:
                machine.sim.model.on('research_preparation', id=writer['id']).reply(raw({'invalid': True}, expected_receipt='rejected'))
            machine.advance(seconds=61)
            machine.change_charter()
            machine.advance(seconds=1)
            machine.change_charter()
            machine.request_audit(requested=False)
            stale = deepcopy(queued(machine.sim, 'task_contract_review'))
            self.assertIsNotNone(stale)
            waits = revision_waits(stale, machine.sim.instance, machine.sim.runtime)
            self.assertTrue(waits)
            self.assertTrue(all(row['kind'] == 'contract_revision' for row in waits))
            writers = {row['action_id'] for row in waits if row.get('action_id')}
            self.assertTrue(writers)
            self.assertTrue(writers <= {row['id'] for row in actions(machine.sim.runtime)})
            selected = deepcopy(machine.current_action('task_contract_review'))
            self.assertIsNotNone(selected)
            self.assertNotEqual(selected['id'], stale['id'])
            self.assertEqual(revision_waits(selected, machine.sim.instance, machine.sim.runtime), [])
            machine.restart()
            self.assertEqual(revision_waits(stale, machine.sim.instance, machine.sim.runtime), waits)
            machine.contract_decision(value='revision_required')
            rows = [row for row in machine.sim.runtime['executions'].values()
                    if row['action']['id'] == selected['id'] and row['status'] == 'ended']
            self.assertTrue(rows)
            self.assertTrue(all(row['outcome'] == 'output_accepted' for row in rows))
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_operational_revision_pins_evidence_then_replaces_the_contract(self):
        """운영 개정 요청부터 준비 수신·이력 보존·재시작 재적재까지 확인한다."""
        from support.cross_research_machine import TaskOperationAlphabetMachine
        from support.cross_obligations import assert_replacement
        machine = TaskOperationAlphabetMachine()
        try:
            task_id, before, request = machine.assert_operational_revision()
            machine.restart()
            pending = next(row for row in actions(machine.sim.runtime) if row['id'] == request['id'])
            self.assertEqual(pending['revision_targets'], request['revision_targets'])
            self.assertEqual(pending['reason'], request['reason'])
            observed = machine.answer('research_preparation', 'revision', True)
            proposal = next(row for row in observed['output']['candidates']
                            if row['revises_task_id'] == task_id)
            assert_replacement(before, proposal, machine.sim.runtime['tasks'][task_id])
            replaced = deepcopy(machine.sim.runtime['tasks'][task_id])
            machine.restart()
            self.assertEqual(machine.sim.runtime['tasks'][task_id], replaced)
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_operational_task_decisions(self):
        from support.cross_states import operational_task_ready
        for value in ('completed', 'incomplete', 'closed'):
            with self.subTest(value=value):
                sim = operational_task_ready()
                assert_event(sim, queued(sim, 'operational_review'), 'task_operation', value)

    def test_live_continue_and_retry_settle_before_restart(self):
        from support.cross_live_operations import LiveOperationMachine
        for value in ('continue', 'retry'):
            with self.subTest(value=value):
                machine = LiveOperationMachine()
                try:
                    machine.live_disposition(value)
                    dispositions = deepcopy(machine.sim.runtime['operational_dispositions'])
                    self.assertTrue(dispositions)
                    self.assertTrue(all(row['disposition']['kind'] == value for row in dispositions.values()))
                    machine.restart()
                    machine.contracts_after_every_event()
                    self.assertEqual(machine.sim.runtime['operational_dispositions'], dispositions)
                finally:
                    machine.teardown()

    def test_kind_definition_decisions(self):
        from support.cross_states import kind_ready
        for value in ('approved', 'revision_required', 'unresolved'):
            with self.subTest(value=value):
                sim = kind_ready()
                assert_event(sim, queued(sim, 'maintenance'), 'kind_check', value)

    def test_impact_decisions(self):
        from support.review_sim import impact_sim
        for value in ('approve', 'reject', 'unresolved'):
            with self.subTest(value=value):
                sim = impact_sim()
                assert_event(sim, queued(sim, 'maintenance', 'impact_review'), 'impact', value)

    def test_initial_diagnosis_decisions(self):
        from support.cross_states import initial_diagnosis_ready
        for value in ('retry', 'wait'):
            with self.subTest(value=value):
                sim = initial_diagnosis_ready()
                try:
                    assert_event(sim, queued(sim, 'maintenance'), 'initial_diagnosis', value)
                finally:
                    sim.cross_temporary.cleanup()

    def test_contract_decisions(self):
        for value in ('approved', 'revision_required', 'unresolved'):
            with self.subTest(value=value):
                sim = activate()
                drive(sim, lambda s: queued(s, 'task_contract_review') is not None)
                assert_event(sim, queued(sim, 'task_contract_review'), 'contract', value)

    def test_plan_selections(self):
        for value in ('selected', 'not_selected', 'not_assessable'):
            with self.subTest(value=value):
                sim = plan_ready()
                assert_event(sim, queued(sim, 'research_plan'), 'selection', value)

    def test_parked_plan_prefix_restoration_keeps_readiness_and_isolates_configuration(self):
        """Three actual public prefixes retain records and input gates across fresh owners."""
        for produce in (plan_ready, returned_plan, waived_plan):
            with self.subTest(prefix=produce.__name__):
                first = produce()
                before = deepcopy((first.engine.head, first.instance, first.runtime, first.clock.state()))
                readiness = deepcopy(first.engine._task_readiness)
                self.assertTrue(readiness)
                self.assertIsNotNone(queued(first, 'research_plan'))
                self.assertTrue(all(row['status'] == 'ended' for row in first.runtime['executions'].values()))
                self.assertFalse(first.ports.calls.created)
                self.assertEqual(first.model.calls, [])
                applied(first, 'configure', config={
                    'plan_settle_seconds': first.instance['config']['plan_settle_seconds'] + 1})
                ContractOracle(first).check(first)
                restored = produce()
                self.assertEqual(restored.root, first.root)
                self.assertEqual((restored.engine.head, restored.instance, restored.runtime, restored.clock.state()), before)
                self.assertEqual(restored.engine._task_readiness, readiness)
                self.assertFalse(restored.ports.calls.created)
                self.assertEqual(restored.model.calls, [])
                ContractOracle(restored).check(restored)

    def test_work_outcomes(self):
        for value in ('submitted', 'partial', 'waiting', 'no_result'):
            with self.subTest(value=value):
                sim = plan_ready()
                drive(sim, lambda s: queued(s, 'research_work') is not None)
                assert_event(sim, queued(sim, 'research_work'), 'work', value)

    def test_supplemental_work_outcomes(self):
        from support.cross_states import supplemental_ready
        for value in ('submitted', 'partial', 'waiting', 'no_result'):
            with self.subTest(value=value):
                sim = supplemental_ready()
                assert_event(sim, queued(sim, 'supplemental_research'), 'work', value)

    def test_returned_task_decisions(self):
        for value in ('completed', 'incomplete', 'closed'):
            with self.subTest(value=value):
                sim = waived_plan() if value == 'closed' else returned_plan()
                observed = assert_event(sim, queued(sim, 'research_plan'), 'assessment', value)
                for row in observed['output']['task_assessments']:
                    task = sim.runtime['tasks'][row['task_id']]
                    self.assertEqual(task['assessment']['decision'], value)

    def test_identity_and_goal_decisions(self):
        for role, event, values, producer in (
            ('identity_review', 'identity', ('match', 'mismatch', 'unresolved'), review_stage),
            ('goal_audit', 'goal', ('satisfied', 'not_satisfied', 'unresolved'), goal_ready)):
            for value in values:
                with self.subTest(role=role, value=value):
                    sim = producer()
                    assert_event(sim, queued(sim, role), event, value)

    def test_review_answer_dispositions(self):
        for value in ('maintain', 'revise', 'split', 'withdraw'):
            with self.subTest(value=value):
                sim = review_stage('answer')
                assert_event(sim, queued(sim, 'identity_review', 'answer'), 'answer', value)

    def test_judge_verdicts(self):
        for value in ('approved', 'rejected', 'unresolved'):
            with self.subTest(value=value):
                sim = review_stage('judge')
                assert_event(sim, queued(sim, 'identity_review', 'judge'), 'verdict', value)

    def test_interpretation_decisions(self):
        for value in ('approved', 'revision_required', 'unresolved'):
            with self.subTest(value=value):
                sim = interpretation_ready()
                assert_event(sim, queued(sim, 'intent_interpretation', 'check'), 'interpretation', value)

    def test_investigation_outcomes(self):
        for value in ('answered', 'unresolved'):
            with self.subTest(value=value):
                sim = investigation_ready()
                assert_event(sim, queued(sim, 'supplemental_research'), 'investigation', value)

    def test_operational_dispositions(self):
        for value in ('continue', 'retry', 'repair', 'resume'):
            with self.subTest(value=value):
                sim = checkpoint_failure() if value == 'resume' else failure_ready()
                original = deepcopy(sim.runtime['executions'])
                assert_event(sim, queued(sim, 'operational_review'), 'operation', value)
                sim.restart()
                ContractOracle(sim).check(sim)
                for eid, row in original.items():
                    self.assertEqual(sim.runtime['executions'][eid]['outcome'], row['outcome'])

    def test_limited_recovery_is_composable_with_pause_and_restart(self):
        machine = AlphabetMachine()
        try:
            machine.request_maintenance()
            machine.pause()
            machine.limited_recovery()
            machine.contracts_after_every_event()
            machine.owner_pass()
            machine.restart()
            machine.contracts_after_every_event()
            self.assertEqual(machine.sim.runtime['status'], 'paused')
            self.assertTrue(any(row['role'] == 'maintenance' and row['outcome'] == 'output_accepted'
                                for row in machine.sim.runtime['executions'].values()))
        finally:
            machine.teardown()


    def test_revision_replaces_and_preserves_merged_request_reasons(self):
        machine = AlphabetMachine()
        try:
            machine.request_revision()
            before = deepcopy(actions(machine.sim.runtime))
            machine.replace_contract()
            machine.contracts_after_every_event()
            assert_preserved_reasons(before, machine.sim.runtime)
        finally:
            machine.teardown()

    def test_withdrawal_retires_targets_and_preserves_unbound_requests(self):
        from support.cross_states import split_writer_plan_ready
        class WithdrawalMachine(AlphabetMachine):
            def new_sim(self):
                return split_writer_plan_ready()
        machine = WithdrawalMachine()
        self.addCleanup(machine.sim.cross_temporary.cleanup)
        try:
            machine.request_revision()
            before = deepcopy(actions(machine.sim.runtime))
            machine.control('decision', config={'change': {'kind': 'revoke', 'grant_id': 'GR-cross-writer'}})
            # A fresh plan still sees the ready population after explicit
            # revision requests; this seed fails at its bound if it does not.
            machine.control('request', config={'role': 'research_plan'}, text='Reconsider remaining independent obligations')
            machine.withdraw_tasks()
            self.assertTrue(any(a.get('revision_targets') for a in before))
            self.assertFalse(any(a.get('revision_targets') for a in actions(machine.sim.runtime)))
            pending = [a for a in before if a.get('revision_targets')]
            self.assertTrue(pending)
            for writer in pending:
                self.assertTrue(writer.get('unbound_request'))
                self.assertTrue(any(a['id'] == writer['id'] for a in actions(machine.sim.runtime)))
                self.assertFalse(any(e['action']['id'] == writer['id']
                                     for e in machine.sim.runtime['executions'].values() if e.get('action')))
            machine.owner_pass()
            assert_preserved_reasons(before, machine.sim.runtime)
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_zero_work_capacity_keeps_independent_operating_assignment(self):
        from support.scheduling_parallel import ready_work_sim
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        limits = deepcopy(sim.instance['config']['session_limits'])
        limits['work'] = {model: 0 for model in limits['work']}
        applied(sim, 'configure', config={'session_limits': limits})
        applied(sim, 'request', config={'role': 'maintenance'}, text='Independent operational inspection')
        drive(sim, lambda s: any(eid not in before and row['role'] == 'maintenance'
              and row['status'] == 'ended' for eid, row in s.runtime['executions'].items()), bound=12)
        self.assertFalse(any(eid not in before and row['role'] == 'research_work'
                             for eid, row in sim.runtime['executions'].items()))

    def test_installation_repair_unresolved_settles_and_does_not_repeat(self):
        from support.cross_installation import recover_report
        from support.operator_finish_scene import Scene
        from do_math import scheduled_operator
        sim = failure_ready()
        assert_event(sim, queued(sim, 'operational_review'), 'operation', 'repair')
        drive(sim, lambda s: any(r['status'] == 'installation_repair_pending'
              for r in s.runtime['operational_dispositions'].values()), bound=12)
        recover_report(sim, 'unresolved')
        before = set(sim.runtime['executions'])
        scene = Scene(sim)
        scene.installation = sim.engine.installation_root
        result = scene.call(scheduled_operator.recovery)
        sim.restart()
        self.assertEqual(set(sim.runtime['executions']), before, result)
        self.assertEqual(result['outcome'], 'recovery_waiting')

    def test_installation_repair_report_releases_one_successor(self):
        from support.cross_installation import recover_report
        sim = failure_ready()
        action = queued(sim, 'operational_review')
        target = action['target']
        assert_event(sim, action, 'operation', 'repair')
        drive(sim, lambda s: any(r['status'] == 'installation_repair_pending'
              for r in s.runtime['operational_dispositions'].values()), bound=12)
        recover_report(sim, 'repaired')
        self.assertEqual(sum(a.get('continuation_of') == target for a in sim.runtime['queue']), 1)
        ContractOracle(sim).check(sim)

    def test_goal_change_retains_independent_review_actions(self):
        from support.cross_machine import ResearchMachine
        machine = ResearchMachine()
        try:
            before = [a['id'] for a in actions(machine.sim.runtime) if a['role'] == 'identity_review']
            self.assertTrue(before)
            machine.change_charter()
            assert_independent_actions(before, machine.sim.runtime)
            machine.restart()
            machine.contracts_after_every_event()
        finally:
            machine.teardown()




class CrossTransitionRegressionTests(unittest.TestCase):
    def test_contract_review_after_pending_assessment_uses_a_dispatchable_target(self):
        machine = AssessmentAlphabetMachine()
        try:
            machine.retire_knowledge(0)
            machine.quiesce()
            machine.change_charter()
            machine.release_quiesce()
            old = deepcopy(queued(machine.sim, 'task_contract_review'))
            self.assertIsNotNone(old)
            self.assertIsNone(machine.current_action('task_contract_review'))
            self.assertFalse(machine.ready('task_contract_review'))
            self.assertEqual(getattr(machine.sim.model.responder, 'pending', {}), {})
            machine.owner_pass()
            current = machine.current_action('task_contract_review')
            self.assertIsNotNone(current)
            self.assertNotEqual(current['target'], old['target'])
            machine.contract_decision('unresolved')
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_installation_repair_pending_has_no_model_answer_admission(self):
        machine = CheckpointAlphabetMachine()
        try:
            machine.change_charter()
            machine.change_charter()
            machine.operational_disposition('repair')
            self.assertTrue(any(r['status'] == 'installation_repair_pending'
                                for r in machine.sim.runtime['operational_dispositions'].values()))
            self.assertFalse(machine.ready('research_plan'))
            self.assertEqual(machine.sim.model.responder.pending, {})
            machine.installation_recovery('repaired')
            self.assertTrue(machine.ready('research_plan'))
            machine.restart()
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_unchanged_assessed_report_is_not_a_new_completion_event(self):
        from support.cross_research_machine import TaskOperationAlphabetMachine
        machine = TaskOperationAlphabetMachine()
        try:
            machine.request_audit(True)
            machine.change_requirements()
            machine.request_audit(False)
            self.assertFalse(machine.assessment_ready())
            observed = machine.sim.model.responder.observed[-1]
            self.assertEqual(observed['input']['returned_task_ids'], [])
            self.assertEqual(observed['output']['task_assessments'], [])
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_pending_completion_fulfils_reported_items_instead_of_retaining_open_items(self):
        from support.cross_research_machine import TaskOperationAlphabetMachine
        machine = TaskOperationAlphabetMachine()
        try:
            machine.assess_returned_work('completed')
            completed = [t for t in machine.sim.runtime['tasks'].values() if t.get('results')]
            self.assertTrue(completed)
            self.assertTrue(all(t['status'] == 'completed' for t in completed))
            self.assertTrue(all(row['kind'] == 'fulfilled' for t in completed
                                for row in t['assessment']['item_dispositions']))
            machine.contracts_after_every_event()
        finally:
            machine.teardown()
