"""Installation recovery waits for an unended execution whose local termination is unconfirmed (``scheduled_operator.recovery``).

``recovery`` opens the instance's repository itself (the real Git process; it
takes no ports yet) and, under the writer lock, refuses to start a repair while
any unended execution lacks a confirmed local termination. The repository is
a real one initialized through the public ``initialize`` with the real ports,
holding a stored running execution without a launch ticket. The model runner
is observed on the unchanged product (``ObservedCalls``).
"""
from pathlib import Path
import tempfile
import unittest

from do_math import scheduled_operator
from do_math.activities import assign_execution, open_activity
from do_math.engine import ResearchEngine, initialize
from do_math.execution_lifecycle import create_execution, transition_execution
from do_math.model_runner import ModelRunner
from do_math.wiring import real_ports
from support.fakes.git_backend import make_repository
from support.provider_probes import ObservedCalls


class SupervisorRecoveryTests(unittest.TestCase):
    def test_recovery_waits_for_unended_execution_without_confirmed_termination(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace = root / 'repository', root / 'work'
            make_repository(repository)
            instance_id = initialize(repository, goal='Recovery wait fixture', workspace=workspace,
                                     config={'operator_enabled': True, 'scholarly_enabled': False},
                                     ports=ports, codex_home=_entry.codex_home, host_id=_entry.host_id)['instance_id']
            engine = ResearchEngine(repository, instance_id, ports=ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
            at = ports.clock.now()
            with engine.store.writer_lock():
                activity = open_activity(engine.runtime, activity_id='AY-live', activity_kind='maintenance',
                                         owner_ref=instance_id, input_refs=[], opened_at=at)
                execution = create_execution(execution_id='EX-live', owner_activity_id=activity['id'],
                                             actor_kind='ai', input_manifest=[],
                                             profile_ref=engine.instance['role_profile_refs']['maintenance'][0],
                                             created_at=at)
                execution['role'] = 'maintenance'
                transition_execution(execution, 'starting', at=at)
                transition_execution(execution, 'running', at=at)
                assign_execution(engine.runtime, activity['id'], execution)
                engine._save()
            _, _, stored = engine.store.load()
            self.assertEqual(stored['executions']['EX-live']['status'], 'running')
            self.assertNotIn('launch_ticket', stored['executions']['EX-live'])
            with ObservedCalls(run=ModelRunner.run) as observed:
                result = scheduled_operator.recovery(repository, instance_id, workspace,
                                                     failure={'kind': 'engine_unavailable', 'error': 'fixture'}, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
            self.assertEqual((result['outcome'], result['execution_id']), ('recovery_waiting', 'EX-live'))
            self.assertEqual(result['reason'], 'existing execution termination is unconfirmed')
            self.assertEqual(observed.count('run'), 0)


if __name__ == '__main__':
    unittest.main()
