"""7-A/2-D: Hypothesis rules inject individual events into the real Sim.

No sampled canned scenario list: controls, clock, owner passes and restart can
be interleaved and shrunk independently. Exceptions are never caught here:
public rejection is a recorded receipt, every escaping exception fails 2-D.
The long machine adds knowledge revision while an identity cycle is open.
"""
from copy import deepcopy

from hypothesis import settings, strategies as st, Verbosity
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from do_math import knowledge, knowledge_records
from support.cross_contracts import ContractOracle
from support.sim import Sim


SHORT = settings(max_examples=2, stateful_step_count=4, deadline=None, database=None,
                 derandomize=True, report_multiple_bugs=False, verbosity=Verbosity.verbose)
LONG = settings(SHORT, max_examples=6, stateful_step_count=20)


class ControlMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.sim = self.new_sim()
        self.oracle = ContractOracle(self.sim)
        self.events = []

    def new_sim(self):
        return Sim.activated()

    def control(self, action, **options):
        if options.get('request_id') is None and options.get('idempotency_key') is None:
            options['idempotency_key'] = self.sim.clock.new_id('EV')
        self.events.append((action, deepcopy(options)))
        pause_before = deepcopy(self.sim.runtime.get('user_pause'))
        request = self.sim.control(action, **options)
        self.last_control = deepcopy(request)
        self.sim.engine.process_controls()
        result = self.sim.engine.control_result(request['request_id'])
        # Rejection is data, not an exception. Pin the one expected terminal
        # rejection rather than accepting arbitrary reasons/helper failures.
        if result.get('effect') == 'rejected':
            if (action == 'resume' and 'expected_user_pause_reason' in options.get('config', {})
                    and result['reason'] == 'the effective user pause is not the released HOLD'):
                assert result['reason'] == 'the effective user pause is not the released HOLD', result
                assert self.sim.runtime.get('user_pause') == pause_before, result
            else:
                assert self.sim.runtime['status'] in {'closed', 'completed'}, result
                assert 'closed/completed' in result['reason'], result
        return result

    @rule()
    def pause(self):
        self.control('pause', text='Cross machine user stop')

    @rule()
    def resume(self):
        from support.cross_obligations import assert_no_resume_replay
        failed = deepcopy(self.sim.runtime.get('waiting_actions', {}))
        self.control('resume', text='Cross machine explicit user resume')
        assert_no_resume_replay(failed, self.sim.runtime)

    @precondition(lambda self: self.sim.runtime['status'] != 'closed')
    @precondition(lambda self: not self.sim.runtime.get('maintenance_fence'))
    @rule()
    def quiesce(self):
        self.control('quiesce', origin='operator', text='Cross machine maintenance')

    @precondition(lambda self: bool(self.sim.runtime.get('maintenance_fence')))
    @rule()
    def release_quiesce(self):
        self.control('release_quiesce', origin='operator', text='Release this fence only',
                     config={'fence_id': self.sim.runtime['maintenance_fence']['request_id']})

    @rule()
    def hold(self):
        self.control('pause', text='User requested scheduled operator HOLD cross-hold')

    @rule()
    def release_hold(self):
        self.control('resume', config={'expected_user_pause_reason':
                                      'User requested scheduled operator HOLD cross-hold'})

    @precondition(lambda self: self.sim.runtime['status'] != 'closed')
    @rule(seconds=st.integers(min_value=1, max_value=60))
    def configure(self, seconds):
        self.control('configure', config={'plan_settle_seconds': seconds})

    @precondition(lambda self: self.sim.runtime['status'] != 'closed')
    @rule(slots=st.integers(min_value=0, max_value=3))
    def configure_capacity(self, slots):
        limits = deepcopy(self.sim.instance['config']['session_limits'])
        limits['work'] = {model: slots for model in limits['work']}
        self.control('configure', config={'session_limits': limits})
        # Reservations are checked independently by CapacityWitness. Selecting
        # with the same product predicate here would merely confirm itself.
        assert self.sim.instance['config']['session_limits']['work'] == limits['work']

    @rule(seconds=st.sampled_from([0, 1, 61, 86401]))
    def advance(self, seconds):
        self.events.append(('advance', seconds))
        self.sim.advance(seconds)

    @rule()
    def owner_pass(self):
        self.events.append(('step',))
        self.sim.step()

    @rule()
    def restart(self):
        self.events.append(('restart',))
        self.sim.restart()

    @rule()
    def close(self):
        self.control('close', text='Cross machine permanent closure')

    @invariant()
    def contracts_after_every_event(self):
        self.oracle.check(self.sim)


class ResearchMachine(ControlMachine):
    def new_sim(self):
        from support.review_research import research_sim
        return research_sim()

    @precondition(lambda self: self.sim.runtime['status'] not in {'closed', 'paused'}
                  and self.sim.runtime['queue'] and self.sim.runtime['queue'][0]['role'] == 'identity_review'
                  and self.sim.runtime['queue'][0].get('stage') == 'scope'
                  and not self.sim.runtime.get('maintenance_fence'))
    @rule()
    def expand_review_scope(self):
        from support.model import Answer

        def expand(out, context):
            out['scope_assessment']['initial_slots'].append({'id': 'initial-cross',
                'perspective': 'Independent domain boundary', 'required_source_refs': ['proposal']})
            return out

        self.events.append(('expand_review_scope',))
        self.sim.model.on('identity_review', stage='scope').reply(Answer(expand))
        self.sim.step()

    @precondition(lambda self: self.sim.runtime['status'] != 'closed')
    @rule()
    def import_knowledge(self):
        source = 'theorem cross_identity : 1 = 1 := rfl'
        self.sim.lean.allow(source, ['cross_identity'], signatures={'cross_identity': 'cross_identity : 1 = 1'},
            declaration_evidence={'cross_identity': {'type': '1 = 1', 'value': None}}, axioms={'cross_identity': []}, dependencies={'cross_identity': {}})
        self.control('knowledge', config={'operation': 'import', 'candidate': {
            'kind': 'theorem', 'title': 'cross identity', 'statement': 'One equals one',
            'summary': 'Reflexivity', 'explanation': 'By reflexivity.',
            'lean_code': source,
            'declaration_names': ['cross_identity'], 'dependencies': []}})

    @precondition(lambda self: self.sim.runtime['status'] != 'closed' and any(
        row.get('review_cycle_id') and self.sim.runtime['review_cycles'][row['review_cycle_id']]['status'] == 'working'
        for row in self.sim.instance['knowledge'].values()))
    @rule(index=st.integers(min_value=0, max_value=10))
    def revise_during_identity_review(self, index):
        candidates = [row for row in self.sim.instance['knowledge'].values() if row.get('review_cycle_id')
                      and self.sim.runtime['review_cycles'][row['review_cycle_id']]['status'] == 'working']
        item = candidates[index % len(candidates)]
        proposal = knowledge_records.proposal_view(self.sim.instance, item['id'])
        roots = knowledge.revision_roots(self.sim.instance, item['id'])
        self.control('knowledge', config={'operation': 'revise', 'id': item['id'],
            'changes': {'explanation': proposal['explanation'] + ' The domain remains unchanged.'},
            'declared_impact': knowledge.plan_impact(self.sim.instance, self.sim.runtime, roots, [])['computed_impact'],
            'reason': 'Revise while the old identity cycle is open'})

    @precondition(lambda self: self.sim.runtime['status'] != 'closed')
    @rule()
    def change_charter(self):
        from support.cross_obligations import actions, assert_independent_actions
        independent = [a['id'] for a in actions(self.sim.runtime)
                       if a['role'] in {'identity_review', 'trust_check', 'trust_activate', 'maintenance'}]
        current = self.sim.engine._governance()['charter']
        self.control('decision', config={'change': {'kind': 'charter', 'record': {
            'id': self.sim.clock.new_id('CH'), 'kind': 'charter', 'revision': current['revision'] + 1,
            'supersedes': [current['id']], 'content': {**deepcopy(current['content']),
                'goal': current['content']['goal'] + ' Retain the explicit domain.'}}}})
        assert_independent_actions(independent, self.sim.runtime)

    @precondition(lambda self: self.sim.runtime['status'] != 'closed'
                  and self.sim.instance['grants']['GR-research-sim']['status'] == 'active')
    @rule()
    def revoke_authority(self):
        self.control('decision', config={'change': {'kind': 'revoke', 'grant_id': 'GR-research-sim'}})


class LiveMachine(ControlMachine):
    """Execution phase events reach the real ModelRunner and provider worker.

The provider process double yields at the Job port, so the owner actually
applies the stop while the call is live. One example can interleave earlier
controls/restarts with one execution event; controls afterwards remain free.
"""
    role = 'research_work'

    def __init__(self):
        super().__init__()
        self.injected = False
        self.observed = []

    def new_sim(self):
        from support.scheduling_parallel import ready_work_sim
        return ready_work_sim(1)

    def available(self):
        from do_math.execution_profiles import resolve_profile
        queue = self.sim.runtime['queue']
        if not queue or queue[0]['role'] != self.role:
            return False
        selection = self.sim.engine._select_model(queue[0])
        profile = resolve_profile(self.sim.instance['execution_profiles'], selection['profile_ref'])
        return self.sim.engine._session_slots().admission_check(profile)['allowed']

    @precondition(lambda self: not self.injected and self.sim.runtime['status'] not in {'paused', 'closed'}
                  and not self.sim.runtime.get('maintenance_fence')
                  and self.sim.runtime['queue'] and self.sim.runtime['queue'][0]['role'] == self.role
                  and not self.sim.runtime['pending_events']
                  and self.sim.clock.wall().year == 2090
                  and self.sim.clock.wall().day == 1)
    @precondition(lambda self: self.available())
    @rule(phase=st.sampled_from(['success', 'failure', 'pause', 'elapsed_work', 'tool_pause', 'sealed_quiesce']))
    def execution_event(self, phase):
        from support.fakes.jobs import job_turn
        from support.live_finish_model import execution, install
        from support.storage_finish_installation import at_return
        sim = self.sim
        self.injected = True
        self.events.append(('execution_event', phase))

        def hook(cli, context):
            if context['action']['role'] != self.role:
                return
            row = execution(sim, cli.workspace)
            self.oracle.capacity.check(sim)
            self.observed.append({'id': row['id'], 'status': row['status'],
                'grant': deepcopy(sim.instance['grants'][row['action']['grant_id']])})
            (cli.workspace / 'cross-evidence.txt').write_bytes(b'preserve partial work across stops')
            if phase == 'failure':
                return False
            if phase == 'tool_pause':
                cli.event({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'cross-tool'}})
            if phase in {'pause', 'tool_pause'}:
                sim.control('pause', text='Cross stop during the provider call')
            elif phase == 'timeout':
                sim.advance(sim.instance['config']['call_timeout_seconds'] + 1)
            elif phase == 'elapsed_work':
                sim.advance(sim.instance['config']['call_timeout_seconds'] + 1)
                job_turn()
                return
            else:
                return
            for _ in range(100):
                job_turn()
            self.observed.append({'did_not_stop': phase})

        install(sim, hook)
        if phase == 'sealed_quiesce':
            with at_return(sim.engine.runner.run,
                           lambda: sim.control('quiesce', text='Drain after sealed result')):
                sim.step()
        else:
            sim.step()
        assert len(self.observed) == 1, self.observed
        observation = self.observed[0]
        assert observation['status'] == 'running', observation
        assert observation['grant']['status'] == 'active', observation
        row = sim.runtime['executions'][observation['id']]
        assert row['status'] == 'ended', row
        assert any(f['path'] == 'cross-evidence.txt' for f in row['output_files']), row['output_files']
        if phase in {'pause', 'tool_pause'}:
            assert row['outcome'] == 'cancelled', row
            assert sim.runtime['status'] == 'paused', sim.waiting()
        elif phase in {'success', 'elapsed_work', 'sealed_quiesce'}:
            assert row['outcome'] == 'output_accepted', row
        else:
            assert row['outcome'] == 'execution_incomplete', row
        self.oracle.check(sim)


class DeadlineMachine(LiveMachine):
    role = 'research_preparation'

    def new_sim(self):
        return Sim.activated()

    @precondition(lambda self: not self.injected and self.sim.runtime['status'] not in {'paused', 'closed'}
                  and not self.sim.runtime.get('maintenance_fence')
                  and self.sim.runtime['queue'] and self.sim.runtime['queue'][0]['role'] == self.role)
    @rule()
    def operational_timeout(self):
        super().execution_event('timeout')


def assert_machine(machine, configuration):
    """Assertions live in the invariant, including the initial/zero-event state."""
    from hypothesis.stateful import run_state_machine_as_test
    run_state_machine_as_test(machine, settings=configuration)
