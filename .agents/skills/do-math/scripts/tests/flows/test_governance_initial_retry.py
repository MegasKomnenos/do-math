"""A failed initial interpretation retried by public request (``call_engine``, ``lifecycle_engine``), moved from ``test_initial_intent_connection``.

The legacy test assembled the adopted initializing state on an in-memory
``FakeEngine`` seed, published it to a real Git repository, and ran the engine
with a runner that raised before any start (``FailingRunner``); the retry ran
under ``PublicInitializationRunner`` with ``windows_job.named_job_empty``
patched. Here the adopted state is the public controls' own
(``support.scheduling_initial.adopted_sim``: the engine queued the initial
interpretation and no owner pass ran it). The first attempt runs the product's
model runner up to its Job launch, which the Jobs port refuses (``OSError``), so
the call ends before any start as the legacy runner's did. The retry goes
through the public request control, a restarted engine, and the model double
answering the interpretation through the worker; the Jobs port answers the
termination queries.
"""
from contextlib import contextmanager
from copy import deepcopy
import unittest

from support.scheduling_initial import GRANT, adopted_sim

LAUNCH_FAILURE = 'fixture: the Job could not be created'
NOT_ORIGINAL = '^retry requires the ended failed interpretation of the original initial input$'


@contextmanager
def launch_refused(sim):
    """Every Job launch on ``sim``'s Jobs port fails as a refused Job creation does."""
    def launch(argv, **options):
        raise OSError(LAUNCH_FAILURE)
    sim.jobs.launch = launch
    try:
        yield
    finally:
        del sim.jobs.launch


def failed(sim):
    return any(row['kind'] == 'execution_failure' for row in sim.runtime.get('waiting_actions', {}).values())


class InitialFailureRetryTests(unittest.TestCase):
    def test_public_retry_preserves_original_input_and_ended_predecessor(self):
        """About 3 s after the adopted template is built: a failed owner pass, four rejected retries, a public request,
        a restart and the retried call."""
        sim = adopted_sim()
        original = deepcopy(sim.instance['lifecycle']['immutable_input'])
        with launch_refused(sim):
            # The first pass activates the trust environment queued ahead; the next runs the interpretation.
            sim.run_until(failed, max_steps=3)
        engine = sim.engine
        aid, held = next((a, h) for a, h in engine.runtime['waiting_actions'].items() if h['kind'] == 'execution_failure')
        predecessor = deepcopy(engine.runtime['executions'][held['execution_id']])
        self.assertEqual(predecessor['status'], 'ended')
        self.assertIsNone(predecessor.get('started_at'))
        self.assertIn(LAUNCH_FAILURE, predecessor['error'])
        failure_state = deepcopy(engine.runtime)
        for change, reason in (('live', NOT_ORIGINAL), ('source', NOT_ORIGINAL),
                               ('grant', '^initial operating authority: no current grant permits this action$'),
                               ('termination', '^initial retry requires confirmed local termination and released reservations$')):
            with self.subTest(rejected=change):
                engine.runtime = deepcopy(failure_state)
                saved_instance = deepcopy(engine.instance)
                if change == 'live':
                    engine.runtime['executions'][predecessor['id']]['status'] = 'running'
                elif change == 'source':
                    engine.runtime['waiting_actions'][aid]['action']['target'] = 'UI-other'
                elif change == 'grant':
                    engine.instance['grants'][GRANT]['status'] = 'revoked'
                else:
                    # Only SessionSlots.release confirms local termination, and it settles the
                    # execution's reservations first; unconfirmed termination still holds them.
                    engine.runtime['executions'][predecessor['id']]['capacity']['local_termination'] = 'unknown'
                with self.assertRaisesRegex(ValueError, reason):
                    engine._retry_input_overflow_action({'id': 'UC-negative', 'config': {'retry_action': aid}})
                self.assertIn(aid, engine.runtime['waiting_actions'])
                engine.instance = saved_instance
        engine.runtime = deepcopy(failure_state)
        request = sim.control('request', config={'retry_action': aid}, request_id='UC-initial-retry')
        self.assertTrue(request['accepted'])
        sim.restart()
        restarted = sim.engine
        restarted.process_controls()
        self.assertNotIn(aid, restarted.runtime['waiting_actions'], restarted.runtime['history'][-3:])
        retry = next(a for a in restarted.runtime['queue'] if a['id'] == aid)
        self.assertEqual(retry['continuation_of'], predecessor['id'])
        self.assertEqual(restarted.runtime['executions'][predecessor['id']], predecessor)
        self.assertFalse(any(a['role'] == 'operational_review' and a.get('target') == predecessor['id']
                             for a in restarted.runtime['queue']))

        def continued(s):
            return any(e.get('continuation_of') == predecessor['id'] and e['status'] == 'ended'
                       for e in s.runtime['executions'].values())
        sim.run_until(continued, max_steps=3)
        successor = next(e for e in sim.runtime['executions'].values() if e.get('continuation_of') == predecessor['id'])
        self.assertEqual(successor['outcome'], 'output_accepted', successor)
        self.assertEqual(successor['owner_activity_id'], predecessor['owner_activity_id'])
        self.assertTrue(sim.runtime['intent_imports'])
        self.assertEqual(sim.instance['lifecycle']['immutable_input'], original)


if __name__ == '__main__':
    unittest.main()
