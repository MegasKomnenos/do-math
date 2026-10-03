"""Operational decisions while an actual provider Job is running (finite turns)."""
from copy import deepcopy

from hypothesis import strategies as st
from hypothesis.stateful import precondition, rule

from support.cross_machine import LiveMachine
from support.cross_obligations import assert_dispositions_settled


class LiveOperationMachine(LiveMachine):
    def new_sim(self):
        from support.scheduling_parallel import ready_work_sim
        return ready_work_sim(1, tool_review_window_seconds=1)

    @precondition(lambda self: not self.injected and self.sim.runtime['status'] == 'ready'
                  and not self.sim.runtime.get('maintenance_fence') and self.available())
    @rule(kind=st.sampled_from(['continue', 'retry']))
    def live_disposition(self, kind):
        from support.live_finish_model import execution, install
        from support.model import Answer
        sim = self.sim
        from support.scheduling_parallel import round_robin
        sim.ports.calls.choose = round_robin()
        self.injected = True
        observations = []

        def hook(cli, context):
            if context['action']['role'] != 'research_work':
                return
            target = execution(sim, cli.workspace)
            if observations:
                return  # a successor may run, but never requests itself again
            observations.append(deepcopy(target))
            self.oracle.capacity.check(sim)
            sim.model.on('operational_review', target=target['id']).reply(Answer(lambda out, ctx: {
                **out, 'disposition': {'kind': kind, 'basis_refs': [ctx['execution_to_review']['id']],
                    'next_owner': 'research_work', 'reason': 'Judge the supplied running execution and preserved progress.',
                    **({'next_review': None} if kind == 'continue' else {
                        'scope': 'The same unfinished task', 'replay_safety': 'No result or external effect was submitted'})}}))
            # An ordinary public request is not a live observation assignment.
            # Let the actual observer open it from a provider tool event.
            cli.event({'type': 'item.started', 'item': {
                'type': 'command_execution', 'id': 'cross-operational-tool'}})
            if kind == 'continue':
                cli.until(lambda: any(r['target_execution_id'] == target['id']
                    for r in sim.runtime.get('operational_dispositions', {}).values()),
                    'live operational review did not return', limit=200)
                cli.event({'type': 'item.completed', 'item': {
                    'type': 'command_execution', 'id': 'cross-operational-tool'}})
            else:
                cli.until(lambda: False, 'retry did not stop its live predecessor', limit=200)

        install(sim, hook)
        sim.step()
        assert len(observations) == 1, observations
        target = sim.runtime['executions'][observations[0]['id']]
        assert target['status'] == 'ended', target
        records = [r for r in sim.runtime.get('operational_dispositions', {}).values()
                   if r['target_execution_id'] == target['id']]
        assert records, ('operational review was never applied', target)
        assert all(sim.runtime['executions'][r['execution_id']]['action'].get('live') for r in records)
        assert all(r['disposition']['kind'] == kind for r in records), records
        assert_dispositions_settled(sim.runtime)
        self.oracle.check(sim)
