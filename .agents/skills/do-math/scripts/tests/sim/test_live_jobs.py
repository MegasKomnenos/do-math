"""A live Job (이음매 장부 18): the owner observes a model call while its Job still runs.

The Jobs fake's live mode runs the worker beside its runner, and the model
double hands the runner a turn after each stream row, so the runner's poll loop
observes a running call and the owner applies those observations before the
call returns. By default the Job has ended before the runner first looks.
"""
import json
from pathlib import Path
import unittest

from do_math.observations import ObservationTracker
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()


def facts_of(runtime, execution_id):
    return [fact for fact in runtime['observation_facts'].values() if fact['execution_id'] == execution_id]


class LiveJobTests(unittest.TestCase):
    def test_the_owner_observes_a_running_call_only_when_its_job_runs_live(self):
        """About 2 s per mode, at the Sim budget: a template restore and one owner pass that runs a model call."""
        for live in (False, True):
            with self.subTest(live=live):
                sim = Sim.activated()
                sim.jobs.live = live
                before = set(sim.runtime['executions'])
                # The owner judges each batch live or ended and hands that to the tracker for every event.
                judged = {'observe': lambda arguments: (arguments['self'].execution_id, arguments['live'])}
                with ObservedCalls(capture=judged, observe=ObservationTracker.observe) as calls:
                    sim.step()  # the queued research preparation runs through the Job fake and the model double
                (execution_id,) = [eid for eid in sim.runtime['executions'] if eid not in before]
                flags = [flag for _, (eid, flag) in calls.calls['observe'] if eid == execution_id]
                self.assertGreater(len(flags), 1)
                if live:
                    self.assertIs(flags[0], True)
                    self.assertIs(flags[-1], False)
                    # Which live rows become facts is the product's judgment: a row that arrives after the
                    # owner turned the execution to stopping records none (이음매 장부 25), so it is not pinned here.
                    continue
                self.assertEqual(set(flags), {False})
                stream = Path(sim.instance['workspace']) / 'runs' / execution_id / 'evidence' / 'stdout.jsonl'
                rows = stream.read_bytes().splitlines()
                facts = sorted(facts_of(sim.runtime, execution_id), key=lambda fact: fact['source']['start_offset'])
                self.assertEqual([json.loads(fact['event_json']) for fact in facts], [json.loads(row) for row in rows])


if __name__ == '__main__':
    unittest.main()
