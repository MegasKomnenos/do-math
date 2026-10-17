"""Long-only, individual model-result and recovery rules with public producers."""
from copy import deepcopy
from datetime import datetime, timedelta

from hypothesis import strategies as st
from hypothesis.stateful import precondition, rule

from do_math.contracts import SCHEMAS, REVIEW_ITEM, PLAN_DISPOSITION
from do_math.governance import INTERPRETATION_DECISIONS
from support.cross_machine import ControlMachine, ResearchMachine
from support.cross_obligations import assert_preserved_reasons, assert_replacement, actions
from support.cross_states import applied, assert_event, queued


class RoleInputSelection:
    """Shared generation gates, not an oracle for expected product outcomes."""
    def current_action(self, role, stage=None):
        """사건 입력만 고른다. 개정·사용자·반복 대기 중인 배정은 응답할 수 없다."""
        from do_math.planning import contract_hash, review_basis_key, revision_waits
        from do_math.questions import user_waits
        from do_math.revisions import action_repetition_waits
        from do_math.task_contracts import TERMINAL_TASK_STATUSES
        for index, action in enumerate(self.sim.runtime['queue']):
            if action['role'] != role or (stage is not None and action.get('stage') != stage):
                continue
            # Input generation only: the real call gate retires these before
            # starting a worker. Never arm an answer that cannot be consumed.
            if self.sim.engine._obsolete_action_reason(action):
                continue
            if role == 'goal_audit' and action.get('basis') != self.sim.engine._goal_basis_key():
                continue
            from do_math.execution_profiles import task_research
            if task_research(action):
                from do_math.planning import task_ready
                task = self.sim.runtime['tasks'].get(action.get('target'))
                if not task or task_ready(task, self.sim.instance, self.sim.runtime, action=action,
                        evaluation_context=self.sim.engine._evaluation_context())['state'] != 'ready':
                    continue
                if action.get('selected_contract_sha256') not in {None, contract_hash(task)}:
                    continue
            if (revision_waits(action, self.sim.instance, self.sim.runtime)
                    or user_waits(action, self.sim.instance, self.sim.runtime)
                    or action_repetition_waits(self.sim.instance, self.sim.runtime, action)):
                continue
            if role == 'task_contract_review':
                task = self.sim.runtime['tasks'].get(action.get('target'))
                if not task or task['status'] in TERMINAL_TASK_STATUSES or not task.get('model_assessment'):
                    continue
                from do_math.task_contracts import returned_task_ids
                if task['id'] in returned_task_ids(self.sim.runtime['tasks']) and any(
                        prior['role'] == 'research_plan' for prior in self.sim.runtime['queue'][:index]):
                    # The earlier assessment can terminate this task before a
                    # delayed review answer starts. Other task reviews remain selectable.
                    continue
                basis = {'revision': task['revision'], 'contract_sha256': contract_hash(task),
                         **self.sim.engine._governance_revisions()}
                if action.get('contract_basis') != basis or action.get('review_basis_key') != review_basis_key(
                        task, self.sim.instance, self.sim.runtime):
                    continue
            return action
        return None

    def ready(self, role, stage=None):
        if (self.sim.runtime['status'] in {'paused', 'closed', 'completed'}
                or self.sim.runtime.get('maintenance_fence') or self.sim.engine._owner_stopping()[1]):
            return False
        action = self.current_action(role, stage)
        if action is None:
            return False
        try:
            # The copied action may acquire a profile/grant; never publish it.
            # Effective adopted authority is narrower than all active grants.
            profile = self.sim.engine._action_lifecycle_gate(deepcopy(action))
        except ValueError as error:
            # Revocation/expiry can legitimately leave a queued input without
            # authority. A broken profile or an unknown gate error must fail
            # 2-D, even if a nested helper uses the same rejection text.
            from do_math.lifecycle_engine import LifecycleEngineMixin
            allowed = {
                'narrow initial operating grant required',
                'initial operating authority: no current grant permits this action',
                'initial operating authority: ambiguous current grants',
                'research authority: no current grant permits this action',
                'research authority: ambiguous current grants',
            }
            origin = error.__traceback__
            while origin.tb_next is not None:
                origin = origin.tb_next
            if (str(error) not in allowed or origin.tb_frame.f_code is not
                    LifecycleEngineMixin._action_lifecycle_gate.__code__):
                raise
            return False
        # Product admission restricts generation only. CapacityWitness, not this
        # admission result, supplies the independent expected reservation value.
        return self.sim.engine._session_slots().admission_check(profile)['allowed']

    def assessment_ready(self):
        from do_math.task_contracts import returned_task_ids
        return self.ready('research_plan') and bool(returned_task_ids(self.sim.runtime['tasks']))

    def answer(self, role, event, value, stage=None):
        action = deepcopy(self.current_action(role, stage))
        assert action is not None
        self.events.append((event, value, action['id']))
        result = assert_event(self.sim, action, event, value)
        self.oracle.check(self.sim)
        return result


class AlphabetMachine(RoleInputSelection, ResearchMachine):
    """Each rule submits exactly one event; owner passes remain independent."""
    def new_sim(self):
        from support.cross_states import plan_ready
        return plan_ready()

    @precondition(lambda self: self.ready('task_contract_review'))
    @rule(value=st.sampled_from(REVIEW_ITEM['properties']['decision']['enum']))
    def contract_decision(self, value):
        self.answer('task_contract_review', 'contract', value)

    @precondition(lambda self: self.ready('research_plan') and any(
        row['state'] == 'ready' for row in self.sim.engine._task_readiness.values()))
    @rule(value=st.sampled_from(PLAN_DISPOSITION['properties']['kind']['enum']))
    def plan_selection(self, value):
        self.answer('research_plan', 'selection', value)

    @precondition(lambda self: self.ready('research_plan') and any(
        t['status'] in {'planned', 'waiting'} and not t.get('results') and t.get('producer_execution')
        for t in self.sim.runtime['tasks'].values()))
    @rule()
    def withdraw_tasks(self):
        observed = self.answer('research_plan', 'withdraw', True)
        targets = [t['id'] for t in observed['input']['tasks'] if t['status'] in {'planned', 'waiting'}
                   and not t.get('results') and t.get('producer_execution')]
        for tid in targets:
            assert self.sim.runtime['tasks'][tid]['status'] == 'closed'

    @precondition(lambda self: self.ready('research_plan') and any(
        row['state'] == 'ready' for row in self.sim.engine._task_readiness.values()))
    @rule()
    def request_revision(self):
        before = deepcopy(actions(self.sim.runtime))
        self.answer('research_plan', 'revision_request', True)
        assert_preserved_reasons(before, self.sim.runtime)

    @precondition(lambda self: self.ready('research_preparation') and bool(
        self.current_action('research_preparation').get('revision_targets')) and set(
        self.current_action('research_preparation')['revision_targets']) <= self.sim.runtime['tasks'].keys())
    @rule()
    def replace_contract(self):
        before = deepcopy(self.sim.runtime['tasks'])
        observed = self.answer('research_preparation', 'revision', True)
        for proposal in observed['output']['candidates']:
            tid = proposal['revises_task_id']
            assert_replacement(before[tid], proposal, self.sim.runtime['tasks'][tid])

    @precondition(lambda self: self.ready('research_plan'))
    @rule(requested=st.booleans())
    def request_audit(self, requested):
        self.answer('research_plan', 'audit', requested)

    @precondition(lambda self: self.assessment_ready())
    @rule(value=st.sampled_from(['completed', 'incomplete']))
    def assess_returned_work(self, value):
        self.answer('research_plan', 'assessment', value)

    @precondition(lambda self: self.sim.runtime['status'] not in {'closed', 'completed'} and any(
        row.get('lifecycle') != 'withdrawn' for row in self.sim.instance['knowledge'].values()))
    @rule(index=st.integers(min_value=0, max_value=10))
    def retire_knowledge(self, index):
        from do_math.knowledge import plan_impact
        candidates = [row for row in self.sim.instance['knowledge'].values() if row.get('lifecycle') != 'withdrawn']
        identifier = candidates[index % len(candidates)]['id']
        before = deepcopy(self.sim.instance['knowledge'][identifier])
        self.control('knowledge', config={'operation': 'invalidate', 'id': identifier,
            'reason': 'Retire this supplied premise while preserving its evidence.',
            'declared_impact': plan_impact(self.sim.instance, self.sim.runtime, [identifier], [])['computed_impact']})
        assert self.sim.instance['knowledge'][identifier]['lifecycle'] == 'withdrawn'
        assert self.sim.instance['knowledge'][identifier]['exposition_id'] == before['exposition_id']

    @precondition(lambda self: self.sim.runtime['status'] not in {'closed', 'completed'})
    @rule()
    def interpretation_input(self):
        self.control('input', text='Keep the natural-number domain explicit in the current question.')

    @precondition(lambda self: self.ready('research_work'))
    @rule(value=st.sampled_from(SCHEMAS['research_work']['properties']['outcome']['enum']))
    def work_outcome(self, value):
        self.answer('research_work', 'work', value)

    @precondition(lambda self: self.ready('supplemental_research') and not
                  self.current_action('supplemental_research').get('review_cycle_id'))
    @rule(value=st.sampled_from(SCHEMAS['supplemental_research']['properties']['outcome']['enum']))
    def supplemental_outcome(self, value):
        self.answer('supplemental_research', 'work', value)

    @precondition(lambda self: self.ready('identity_review', 'initial'))
    @rule(value=st.sampled_from(SCHEMAS['identity_review']['properties']['decision']['enum']))
    def identity_decision(self, value):
        self.answer('identity_review', 'identity', value, 'initial')

    @precondition(lambda self: self.ready('goal_audit'))
    @rule(value=st.sampled_from(SCHEMAS['goal_audit']['properties']['decision']['enum']))
    def goal_decision(self, value):
        self.answer('goal_audit', 'goal', value)

    @precondition(lambda self: self.ready('intent_interpretation', 'check'))
    @rule(value=st.sampled_from(INTERPRETATION_DECISIONS))
    def interpretation_decision(self, value):
        self.answer('intent_interpretation', 'interpretation', value, 'check')

    @precondition(lambda self: self.ready('intent_interpretation') and bool(
        self.current_action('intent_interpretation').get('delegation_application_id')))
    @rule(value=st.sampled_from(['within_scope', 'outside_scope', 'unresolved']))
    def delegation_decision(self, value):
        self.answer('intent_interpretation', 'delegation', value)

    @precondition(lambda self: self.ready('operational_review'))
    @rule(value=st.sampled_from(['continue', 'retry', 'repair', 'user_decision']))
    def operational_disposition(self, value):
        self.answer('operational_review', 'operation', value)

    @precondition(lambda self: self.ready('maintenance') and bool(self.current_action('maintenance').get('kind_definition_id')))
    @rule(value=st.sampled_from(['approved', 'revision_required', 'unresolved']))
    def kind_definition_decision(self, value):
        self.answer('maintenance', 'kind_check', value)

    @precondition(lambda self: self.ready('maintenance', 'impact_review'))
    @rule(value=st.sampled_from(['approve', 'reject', 'unresolved']))
    def impact_decision(self, value):
        self.answer('maintenance', 'impact', value, 'impact_review')

    @precondition(lambda self: self.ready('maintenance') and bool(self.current_action('maintenance').get('initial_submission_diagnosis')))
    @rule(value=st.sampled_from(['retry', 'wait']))
    def initialization_diagnosis(self, value):
        self.answer('maintenance', 'initial_diagnosis', value)

    @precondition(lambda self: self.sim.runtime['status'] not in {'closed', 'completed'})
    @rule()
    def request_maintenance(self):
        self.control('request', text='Inspect retained recovery evidence', config={'role': 'maintenance'})

    def maintenance_grants(self):
        return [g for g in self.sim.instance['grants'].values()
                if g['status'] == 'active' and 'maintenance' in g.get('roles', [])
                and (not g.get('expires_at') or datetime.fromisoformat(g['expires_at'].replace('Z', '+00:00'))
                     > self.sim.clock.wall())]

    @precondition(lambda self: self.sim.runtime['status'] == 'paused'
                  and self.current_action('maintenance') is not None and bool(self.maintenance_grants()))
    @rule()
    def limited_recovery(self):
        action = self.current_action('maintenance')
        # Selection supplies an input reference, not the expected verdict.
        reference = self.sim.engine._select_model(action)['profile_ref']
        grants = self.maintenance_grants()
        assert grants, 'public activation must provide the maintenance authority'
        self.control('decision', config={'change': {'kind': 'limited_recovery', 'action_id': action['id'],
            'grant_id': grants[0]['id'], 'profile_ref': reference,
            'purpose': 'Inspect retained recovery evidence', 'procedure': 'Read and report the preserved state',
            'expires_at': (self.sim.clock.wall() + timedelta(minutes=5)).isoformat()}})
        assert self.sim.runtime['status'] == 'paused'

    @precondition(lambda self: self.sim.runtime['status'] not in {'closed', 'completed'})
    @rule()
    def change_requirements(self):
        from support.state_builders import charter_change
        from support.purpose_answers import requirement
        wanted = [requirement(['Explain the explicit Nat domain'])]
        self.control('decision', config={'change': charter_change(self.sim.engine, academic_requirements=wanted)})
        assert self.sim.engine._governance()['charter']['content']['academic_requirements'] == wanted

    @precondition(lambda self: self.sim.runtime['status'] not in {'paused', 'closed', 'completed'}
                  and not self.sim.runtime.get('maintenance_fence') and any(
        r['status'] == 'installation_repair_pending' for r in self.sim.runtime.get('operational_dispositions', {}).values()))
    @rule(outcome=st.sampled_from(['unresolved', 'repaired']))
    def installation_recovery(self, outcome):
        from support.cross_installation import recover_report
        recover_report(self.sim, outcome)
        self.oracle.check(self.sim)


class ReviewAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import review_stage
        return review_stage('answer')

    @precondition(lambda self: self.ready('identity_review', 'answer'))
    @rule(value=st.sampled_from(['maintain', 'revise', 'split', 'withdraw']))
    def answer_disposition(self, value):
        self.answer('identity_review', 'answer', value, 'answer')

    @precondition(lambda self: self.ready('identity_review', 'judge'))
    @rule(value=st.sampled_from(['approved', 'rejected', 'unresolved']))
    def issue_verdict(self, value):
        self.answer('identity_review', 'verdict', value, 'judge')


class DelegationAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.governance_delegation import public_replacement_case
        sim, config = public_replacement_case()
        applied(sim, 'request', text='Independently judge this exact delegated review replacement.', config=config)
        return sim


class OperationAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import failure_ready
        return failure_ready()

class CheckpointAlphabetMachine(OperationAlphabetMachine):
    def new_sim(self):
        from support.cross_states import checkpoint_failure
        return checkpoint_failure()

    @precondition(lambda self: self.ready('operational_review') and bool(self.sim.runtime.get('checkpoints', {}).get(
        self.current_action('operational_review')['target'])))
    @rule()
    def resume_checkpoint(self):
        self.answer('operational_review', 'operation', 'resume')


class AssessmentAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import waived_plan
        return waived_plan()

    @precondition(lambda self: self.assessment_ready())
    @rule()
    def close_with_scope_authority(self):
        self.answer('research_plan', 'assessment', 'closed')


class InvestigationAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import investigation_ready
        return investigation_ready()

    @precondition(lambda self: self.ready('supplemental_research') and bool(
        self.current_action('supplemental_research').get('review_cycle_id')))
    @rule(value=st.sampled_from(['answered', 'unresolved']))
    def investigation_outcome(self, value):
        self.answer('supplemental_research', 'investigation', value)


class KindAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import kind_ready
        return kind_ready()


class TaskOperationAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import operational_task_ready
        return operational_task_ready()

    @precondition(lambda self: self.ready('operational_review') and self.sim.runtime['executions'][
        self.current_action('operational_review')['target']]['action'].get('target') in self.sim.runtime['tasks'])
    @rule(value=st.sampled_from(['completed', 'incomplete', 'closed']))
    def task_disposition(self, value):
        self.answer('operational_review', 'task_operation', value)

    def assert_operational_revision(self):
        """운영 검토의 현행 확장 제출로 개정 근거와 후속 배정을 고정한다."""
        from do_math.planning import contract_hash
        action = deepcopy(self.current_action('operational_review'))
        task_id = self.sim.runtime['executions'][action['target']]['action']['target']
        before = deepcopy(self.sim.runtime['tasks'][task_id])
        self.answer('operational_review', 'operation_revision', 'continue')
        execution = next(row for row in self.sim.runtime['executions'].values()
                         if row['action']['id'] == action['id'] and row['status'] == 'ended')
        request = execution['extensions']['revision_requests']
        assert len(request) == 1 and request[0]['record_ids'] == [task_id], request
        followups = [row for row in actions(self.sim.runtime) if row['role'] == 'research_preparation'
                     and task_id in row.get('revision_targets', {})]
        assert len(followups) == 1, followups
        followup = followups[0]
        assert followup['requested_by'] == execution['id'], followup
        assert followup['revision_targets'][task_id] == {
            'revision': before['revision'], 'contract_sha256': contract_hash(before),
            'required': False, 'source_refs': [execution['id']]}, followup
        assert request[0]['reason'] in followup['reason'].split('\n'), followup
        assert self.sim.runtime['tasks'][task_id]['revision'] == before['revision']
        self.oracle.check(self.sim)
        return task_id, before, deepcopy(followup)

    @precondition(lambda self: self.ready('operational_review') and self.sim.runtime['executions'][
        self.current_action('operational_review')['target']]['action'].get('target') in self.sim.runtime['tasks'])
    @rule()
    def request_operational_revision(self):
        self.assert_operational_revision()


class ImpactAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.review_sim import impact_sim
        return impact_sim()


class SupplementalAlphabetMachine(AlphabetMachine):
    def new_sim(self):
        from support.cross_states import supplemental_ready
        return supplemental_ready()


class InitialDiagnosisAlphabetMachine(RoleInputSelection, ControlMachine):
    def new_sim(self):
        from support.cross_states import initial_diagnosis_ready
        return initial_diagnosis_ready()

    @precondition(lambda self: self.ready('maintenance')
                  and bool(self.current_action('maintenance').get('initial_submission_diagnosis')))
    @rule(value=st.sampled_from(['retry', 'wait']))
    def initialization_diagnosis(self, value):
        self.answer('maintenance', 'initial_diagnosis', value)

    def teardown(self):
        try:
            super().teardown()
        finally:
            self.sim.cross_temporary.cleanup()
