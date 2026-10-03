"""A maintenance cleanup failure reaches the status projection, on the real engine (``Sim``).

The legacy test replaced the engine's cleanup scope, retention state and save,
and made ``retention._inventory`` raise. Here the cleanup runs the real
``_maintenance_cleanup``: a user-requested maintenance scope under a real
maintenance grant, an ended run with confirmed local termination, and a run
folder another handle holds open without sharing (``storage_files.unlistable``),
so listing it fails with a real sharing violation. The engine publishes its
history through its own save, and ``status_report`` projects the published
snapshot through the engine's repository; ``snapshot_report``, which opens the
real Git backend, adds only that opening (``boundary/test_storage_reporting.py``).
"""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import unittest

from do_math import activities, execution_lifecycle, execution_profiles
from do_math.launch import ticket
from do_math.reporting import render_human_report, status_report
from support.sim import Sim, warm_template
from support.storage_files import unlistable
from support.storage_records import apply_control
from support.engine_lifecycle import applied, clear_work
from support.wait_reporting import assert_wait_report

setUpModule = warm_template


class StatusSnapshotTests(unittest.TestCase):
    def test_no_task_authority_wait_reports_real_owner_and_preserved_coordinates(self):
        sim = Sim.activated()
        grant = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': grant}})
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='Report the actual authority wait')
        action = deepcopy(sim.runtime['queue'][0])
        sim.engine._prepare_call(action)
        head, instance, runtime = sim.engine.store.load()
        entry = deepcopy(runtime['waiting_actions'][action['id']])
        report = status_report(sim.engine.store, head, instance, runtime, requested_areas=['record_storage'])
        row = report['waiting_actions'][action['id']]
        self.assertEqual(row['next_owner'], entry['next_owner'])
        self.assertEqual(row['coordinates']['owner_activity_id'], entry['action']['owner_activity_id'])
        self.assertEqual(row['coordinates']['profile_ref'], entry['action']['profile_ref'])
        self.assertEqual(row['reason'], entry['reason'])
        self.assertIsNone(row['target'])
        text = render_human_report(report)
        self.assertIn('action ' + action['id'] + ': maintenance wait=action_authority next=user', text)
        self.assertIn(entry['reason'], text)
        self.assertIn(entry['action']['owner_activity_id'], text)
        self.assertEqual(sim.engine.store.load(), (head, instance, runtime))
        assert_wait_report(self, sim.engine, action['id'])


    def test_engine_cleanup_failure_reaches_snapshot_reporting(self):
        """About 1.1 s alone, 2.3 s in a loaded T2, near the 2 s budget: a template restore, a grant control and three saves."""
        sim = Sim.activated()
        engine = sim.engine
        expiry = (sim.clock.wall() + timedelta(days=1)).isoformat()
        apply_control(sim, 'decision', text='Authorize local maintenance and cleanup of the requested ended run.',
                      config={'change': {'kind': 'grant', 'grant': {'id': 'GR-cleanup', 'kind': 'local',
                              'roles': ['maintenance'], 'reuse': 'reusable', 'expires_at': expiry}}})
        action = {'id': 'AC-cleanup', 'role': 'maintenance', 'actor_kind': 'ai', 'grant_id': 'GR-cleanup',
                  'requested_by': 'UC-cleanup', 'cleanup_execution_ids': ['EX-1']}
        engine.runtime['history'].append({'kind': 'user_control', 'request': {'id': 'UC-cleanup', 'origin': 'user',
            'action': 'request', 'config': {'role': 'maintenance', 'cleanup_execution_ids': ['EX-1']}}})
        profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'],
                                                     engine.instance['role_profile_refs']['maintenance'][0])
        at = sim.clock.now()
        activities.open_activity(engine.runtime, activity_id='AY-EX-1', activity_kind='maintenance',
                                 owner_ref='GR-cleanup', input_refs=[], opened_at=at)
        execution = execution_lifecycle.create_execution(execution_id='EX-1', owner_activity_id='AY-EX-1',
            actor_kind='ai', input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=at)
        execution.update(role='maintenance', action=deepcopy(action), grant_id='GR-cleanup')
        activities.assign_execution(engine.runtime, 'AY-EX-1', execution)
        # The legacy run ended incomplete; the lifecycle reaches that outcome only through a started run.
        for status in ('starting', 'running', 'stopping'):
            execution_lifecycle.transition_execution(execution, status, at=at)
        execution_lifecycle.transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
        # Explicit synthetic termination evidence; scope, schemas, references and the publication are real.
        execution['launch_ticket'] = {**ticket('EX-1', profile, jobs=sim.jobs, clock=sim.clock), 'phase': 'finished'}
        execution['capacity'] = {'local_termination': 'confirmed'}
        activities.finish_activity(engine.runtime, 'AY-EX-1', result_refs=[], unresolved=[], followups=[], at=at)
        engine._save()
        run = Path(engine.instance['workspace']) / 'runs/EX-1'
        run.mkdir(parents=True)
        (run / 'output.txt').write_bytes(b'unarchived result')
        with unlistable(run), engine.store.writer_lock():
            result = engine._maintenance_cleanup(action, 'EX-maint')
        self.assertEqual(result['status'], 'degraded')
        failure, = [row for row in result['failures'] if row['path'] == 'runs/EX-1']
        self.assertTrue(failure['error'].startswith('[WinError 32] ') and failure['error'].endswith(repr(str(run))),
                        failure)
        self.assertEqual(engine.runtime['history'][-1]['kind'], 'maintenance_cleanup')
        head, instance, runtime = engine.store.load()
        self.assertEqual(head, engine.head)
        report = status_report(engine.store, head, instance, runtime, requested_areas=['record_storage'])
        self.assertTrue(any(row['status'] == 'degraded' and failure['error'] in row['message']
                            for row in report['inspection']['findings']), report['inspection']['findings'])
        self.assertEqual(report['cleanup_failures'][0]['next_owner'], 'maintenance')
        self.assertIn('degraded', render_human_report(report))
        self.assertTrue(run.exists())


if __name__ == '__main__':
    unittest.main()
