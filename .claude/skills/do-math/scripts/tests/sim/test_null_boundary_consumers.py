"""Null values through real status and external-operation owners, on port fakes."""
from copy import deepcopy
from pathlib import Path
import unittest

from do_math import reporting, scheduled_operator
from support.engine_lifecycle import external_sim, extended, http_fails, http_grant, run_machine, warm_external
from support.entry import entry

setUpModule = warm_external


class NullOwnerTests(unittest.TestCase):
    def test_snapshot_observations_and_operational_live_guard_have_separate_inputs(self):
        sim = external_sim()
        options = entry()
        snapshot = reporting.snapshot_report(sim.engine.store.repository, sim.instance['id'],
            snapshot=sim.engine.head, requested_areas=['record_storage'],
            backend=sim.ports.git_backend, clock=sim.clock)
        self.assertEqual({key: snapshot[key] for key in reporting.OBSERVED_FIELDS},
                         dict.fromkeys(reporting.OBSERVED_FIELDS))
        human = reporting.render_human_report(snapshot)
        self.assertIn('work sessions: not observed', human)
        self.assertIn('observed (Asia/Seoul): not observed', human)
        live = scheduled_operator.read_status(sim.engine.store.repository, sim.instance['id'],
            ports=sim.ports, codex_home=options.codex_home, environment=options.environment, host_id=options.host_id)
        self.assertEqual(live['snapshot'], snapshot['snapshot'])
        self.assertIs(type(live['provider_waits']['providers']), dict)
        guard = scheduled_operator.engine_start_guard(sim.engine.store.repository, sim.instance['id'],
            Path(sim.instance['workspace']), ports=sim.ports, codex_home=options.codex_home,
            environment=options.environment, host_id=options.host_id)
        self.assertEqual(guard['outcome'], 'startable')
        self.assertEqual(guard['before']['provider_waits'], live['provider_waits'])
        self.assertIsNotNone(guard['before']['research_observed_at'])
        self.assertEqual(sim.engine.store.load()[0], snapshot['snapshot'])

    def test_sent_transport_exception_keeps_unknown_facts_in_execution_and_activity(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        extended(sim.engine, 'external', config)
        # The ordinary OSError branch in execute_operation leaves these facts
        # absent. An unexpected transport error reaches the owner's explicit
        # null production after the durable send marker.
        http_fails(sim, RuntimeError('remote outcome unavailable'))
        run_machine(sim, 'external_action')
        operation = sim.runtime['external_operations'][config['id']]
        self.assertEqual(len(sim.ports.http.requests), 1)
        self.assertEqual(operation['status'], 'unknown')
        self.assertIs(operation['transmitted'], True)
        self.assertIsNone(operation['succeeded'])
        self.assertIsNone(operation['effect_absent'])
        self.assertNotIn('http_status', operation)
        execution = sim.runtime['executions'][operation['execution_id']]
        self.assertIsNone(execution['http_status'])
        self.assertIsNone(execution['succeeded'])
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        self.assertNotIn('submission_receipt', execution)
        activity = sim.runtime['activities'][execution['owner_activity_id']]
        self.assertEqual(activity['waiting']['kind'], 'external_reconciliation')
        self.assertEqual(activity['waiting']['next_owner'], 'user')
        expected = deepcopy((operation, execution, activity))
        sim.restart()
        self.assertEqual((sim.runtime['external_operations'][config['id']],
            sim.runtime['executions'][execution['id']], sim.runtime['activities'][activity['id']]), expected)
