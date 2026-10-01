"""Owner-thread machine continuations beside AI calls, on the real engine and scheduler (``scheduler``, ``formal_engine``).

A formal or trust check runs as a calculation of the calls port while the
owner keeps dispatching and collecting AI calls. The engine's own verifier
runs the check in a Lean worker Job, publishes that Job's start and reads its
stop flag; the Lean double's check is held open there
(``scheduling_machine.HeldLean``) until the owner has run a maintenance call
to its end and one owner pass has run on a clock moved by three hours. In the
stop cases a pause or grant revocation is queued as the check answers: the
calculation reads its flag clear and returns the success, and the owner
publishes the stop before it collects that late success and judges its currentness.
Only one Lean check runs at a time, so the second queued Lean request stays
unstarted. The cases start from a restored activation or the lifecycle
template and run the owner loop (``engine.run``) with its real storage.
"""
from contextlib import ExitStack
from pathlib import Path
import json
import unittest

from do_math.git_store import GitStateStoreConflict
from support.engine_lifecycle import warm_lifecycle
from support.fakes.calls import owner_turn
from support.scheduling_machine import (LEAN_ROLES, HeldLean, PassProbe, artifact, formal_scene, hold_lean,
                                        maintenance_ended, new_rows, take_turns, trust_scene)
from support.sim import warm_template
from support.knowledge_verifier_jobs import OutputCompiler
from support.storage_records import held_ref_lock


def setUpModule():
    warm_template()
    warm_lifecycle()


def pause(sim):
    sim.control('pause', text='Pause the research during the machine check')


def paused(sim):
    return sim.runtime['status'] == 'paused'


def revoke(sim):
    for gid, grant in sim.instance['grants'].items():
        if grant['status'] == 'active':
            sim.control('decision', text='Revoke the grant during the machine check',
                        config={'change': {'kind': 'revoke', 'grant_id': gid}})


def revoked(sim):
    return all(grant['status'] == 'revoked' for grant in sim.instance['grants'].values())


class MachineSchedulerTests(unittest.TestCase):
    def assert_case(self, *, trust=False, cancel=False, stops=None):
        sim, machine_action, _ = trust_scene() if trust else formal_scene()
        control, applied = {False: (None, None), True: (pause, paused), 'revoke': (revoke, revoked)}[cancel]
        lean = HeldLean(sim, control=control)
        take_turns(sim)
        before, cycles = set(sim.runtime['executions']), set(sim.runtime.get('review_cycles', {}))
        sim.engine.run(max_steps=2)
        stops = bool(cancel) if stops is None else stops
        self.assertEqual(lean.failures, [])
        self.assertEqual(lean.held, 1, 'one Lean check ran')
        self.assertTrue(maintenance_ended(sim, before))
        if applied is not None:
            self.assertTrue(applied(sim), json.dumps(sim.waiting(), default=str))
        added = new_rows(sim, 'executions', before)
        machines = [row for row in added if row['role'] in LEAN_ROLES]
        self.assertEqual(len(machines), 1, 'the second Lean request must stay unstarted')
        machine = machines[0]
        self.assertEqual(machine['action']['id'], machine_action['id'])
        self.assertEqual(machine['status'], 'ended')
        self.assertEqual(machine['capacity']['local_termination'], 'confirmed')
        # The engine published the Lean worker Job's own start before it resumed.
        lean_job = next(job for job in sim.jobs.launched if job.name == machine['launch_ticket']['job_name'])
        self.assertEqual(machine['capacity']['process']['pid'], lean_job.pid)
        model = next(row for row in added if row['role'] == 'maintenance')
        self.assertEqual(model['capacity']['local_termination'], 'confirmed')
        # The calculation read its stop flag clear after the check answered, so the success reached
        # the owner; the owner's currentness judgment decided the outcome.
        self.assertEqual(artifact(sim, machine['raw_result_ref'])['status'], 'verified')
        if stops:
            self.assertEqual(machine['outcome'], 'execution_incomplete')
            self.assertEqual(artifact(sim, machine['result_ref'])['status'], 'stopped')
            self.assertEqual(set(sim.runtime.get('review_cycles', {})), cycles, 'no identity review started')
        else:
            self.assertEqual(machine['outcome'], 'output_accepted')
        return sim, machine

    def test_formal_allows_ai_collection_after_long_elapsed_time(self):
        self.assert_case()

    def test_formal_user_stop_rejects_a_late_verified_result(self):
        self.assert_case(cancel=True)

    def test_trust_check_allows_ai_collection_after_long_elapsed_time(self):
        self.assert_case(trust=True)

    def test_trust_check_user_stop_rejects_a_late_verified_result(self):
        self.assert_case(trust=True, cancel=True)

    def test_revoked_authority_rejects_both_kinds_of_formal_result(self):
        self.assert_case(cancel='revoke')

    def test_revoking_research_grants_does_not_stop_a_trust_check(self):
        # Dispatch admits trust checks without a grant; the approved transition is their authority.
        self.assert_case(trust=True, cancel='revoke', stops=False)

    def test_machine_artifacts_publish_to_real_immutable_git_bundles(self):
        for trust in (False, True):
            with self.subTest(trust=trust):
                sim, machine = self.assert_case(trust=trust)
                self.assertNotEqual(machine['raw_result_ref'].split('/')[2], machine['result_ref'].split('/')[2])
                self.assertIn(b'verified', sim.engine.store.read(machine['raw_result_ref'], sim.engine.head))
                self.assertIn(b'verified', sim.engine.store.read(machine['result_ref'], sim.engine.head))
                self.assertEqual(machine['outcome'], 'output_accepted')

    def test_stop_request_reaches_the_calculation_within_one_owner_pass(self):
        sim, action, _ = formal_scene()
        sim.engine.runtime['queue'][:] = [action]
        sim.engine._save()
        before = set(sim.runtime['executions'])
        probe, seen = PassProbe(), {}

        def hold():
            # The check is running: the owner publishes a pause; the check answers once it sees it applied.
            probe.execution_id = next(eid for eid, row in sim.runtime['executions'].items()
                                      if eid not in before and row['role'] == 'formal_check')
            sim.control('pause', text='Pause the running check')
            for _ in range(300):
                owner_turn()
                if sim.runtime['status'] == 'paused':
                    seen['answered'] = probe.passes
                    return
            raise AssertionError('the pause never reached the running check')
        hold_lean(sim, hold)
        take_turns(sim)
        with probe:
            sim.engine.run(max_steps=1)
        setting = [row for row in probe.flags if row[1] is False and row[2] is True]
        self.assertEqual(len(setting), 1, 'the publication itself sets the flag')
        # The calculation reads its flag as soon as the check answers.
        self.assertLessEqual(seen['answered'] - setting[0][0], 1, 'the calculation stops within one owner pass')
        formal = next(row for row in new_rows(sim, 'executions', before) if row['role'] == 'formal_check')
        # The calculation itself honoured the flag: the Job run's poll stopped it (formal._job_run's
        # stop branch; a later read while parsing the evidence would give the error's own reason).
        raw = artifact(sim, formal['raw_result_ref'])
        self.assertEqual((raw['status'], raw['reason']), ('stopped', 'stopped'))
        # The public pause also requests a stop of every running execution (_pause_lifecycle).
        self.assertEqual(formal['result_disposition']['stop_reasons'], ['execution_stop_requested', 'instance_paused'])

    def test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity(self):
        sim, action, _ = formal_scene()
        sim.engine.runtime['queue'][:] = [action]
        sim.engine._save()
        writer = ExitStack()
        self.addCleanup(writer.close)

        def hold():
            # Another writer takes the instance ref, so the owner's next publication fails.
            writer.enter_context(held_ref_lock(sim.engine.store))
            sim.control('request', config={'role': 'research_preparation'}, text='A request the owner publishes')
            for _ in range(300):
                try:
                    owner_turn()
                except RuntimeError:
                    pass  # the calls port shuts down after the owner failed; the flag is set first
                if any(future.stop.is_set() for future in sim.engine._calls.futures):
                    break
            writer.close()
        sim.lean.spawn = OutputCompiler('preserved compiler evidence', during=hold, exit_code=1)
        take_turns(sim)
        before, cycles = set(sim.runtime['executions']), set(sim.runtime.get('review_cycles', {}))
        with self.assertRaisesRegex(GitStateStoreConflict, 'compare-and-swap'):
            sim.engine.run(max_steps=1)
        _, _, runtime = sim.engine.store.load()
        formal = next(row for eid, row in runtime['executions'].items()
                      if eid not in before and row['role'] == 'formal_check')
        self.assertEqual(formal['status'], 'ended')
        self.assertEqual(formal['capacity']['local_termination'], 'confirmed')
        self.assertEqual(set(runtime.get('review_cycles', {})), cycles, 'no identity review started')
        preserved = json.loads(sim.engine.store.read(formal['result_ref']))
        self.assertEqual(preserved['stdout'], 'preserved compiler evidence')
        self.assertEqual(preserved['status'], 'stopped')
        self.assertIn('local_job_usage', preserved)
        self.assertEqual(runtime['waiting_actions'][formal['action']['id']]['kind'], 'execution_failure')
        self.assertFalse(any(a.get('id') == formal['action']['id'] for a in runtime['queue']))
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == formal['id'] for a in runtime['queue']))
        self.assertEqual(runtime['activities'][formal['owner_activity_id']]['status'], 'waiting')

    def test_publication_failure_keeps_local_result_and_durable_unsettled_record(self):
        sim, action, _ = formal_scene()
        sim.engine.runtime['queue'][:] = [action]
        sim.engine._save()
        writer = ExitStack()
        self.addCleanup(writer.close)

        # Another writer takes the ref while the actual compiler finishes.
        sim.lean.spawn = OutputCompiler('retained compiler evidence', exit_code=1,
            during=lambda: writer.enter_context(held_ref_lock(sim.engine.store)))
        take_turns(sim)
        before = set(sim.runtime['executions'])
        with self.assertRaisesRegex(GitStateStoreConflict, 'compare-and-swap'):
            sim.engine.run(max_steps=1)
        writer.close()
        _, _, durable = sim.engine.store.load()
        formal = next(row for eid, row in durable['executions'].items()
                      if eid not in before and row['role'] == 'formal_check')
        self.assertNotEqual(formal['status'], 'ended')
        self.assertNotEqual(formal['capacity']['local_termination'], 'confirmed')
        local = Path(sim.instance['workspace']) / 'execution-recovery' / formal['id'] / 'returned-result.json'
        self.assertIn('retained compiler evidence', local.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
