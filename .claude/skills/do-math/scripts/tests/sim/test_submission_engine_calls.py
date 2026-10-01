"""A producer call stopped by the owner while it runs: its grant revoked, or its local deadline passed, on a Sim.

The legacy tests put ``CheckedRunner`` around a scripted runner on the synthetic
active state; here the owner runs on a restored Sim and the model double answers
(``support.submission_calls``). What the legacy runner did while its call was in
flight runs in the call's hook while the owner takes its turns. The other
producer calls of the legacy class run longer and are in
``flows/test_submission_engine_calls.py``.
"""
import json
from pathlib import Path
import unittest

from do_math import governance
from support.purpose_answers import common
from support.engine_lifecycle import applied
from support.sim import Sim, warm_template
from support.submission_calls import applied_now, configured_sim, submission_model, submitted


def setUpModule():
    warm_template()
    configured_sim(call_timeout_seconds=1)


def stop_requested(workspace):
    """The owner's stop request to a running worker: the file its stop judgment writes into the workspace."""
    return any(Path(workspace).rglob('stop-request.json'))


class ProducerCallTests(unittest.TestCase):
    def test_revoked_original_grant_preserves_late_output_despite_alternative_grant(self):
        """About 2 to 2.5 s, at or over the 2 s Sim budget: a grant decision, then one model call through the worker during which a revocation is applied."""
        sim = Sim.activated()
        grant = next(value for value in sim.instance["grants"].values() if "maintenance" in value.get("roles", []))
        # Another grant for the same roles, decided by control (the legacy test copied the grant into the state).
        applied(sim, "decision", config={"change": {"kind": "grant", "grant": {
            "id": "ZZ-alternative", **{key: grant[key] for key in ("kind", "roles", "reuse", "expires_at")}}}})
        sim.engine.runtime["queue"] = [{"id": "AC-revoked", "role": "maintenance"}]
        sim.engine._save()
        model = submission_model(sim)
        alternative = []

        def revoke(context, workspace):
            execution = next(value for value in sim.engine.runtime["executions"].values() if value["status"] == "running")
            applied_now(sim, "decision", config={"change": {"kind": "revoke", "grant_id": execution["grant_id"]}})
            unbound = {key: value for key, value in execution["action"].items() if key != "grant_id"}
            alternative.append(governance.authorize(sim.engine.instance, unbound, at=sim.ports.clock.now())["allowed"])
        model.before("maintenance", revoke)
        late = {**common("Completed before revocation."), "report": "Preserve the completed portion.", "remaining_work": []}
        model.on("maintenance").reply(submitted(late))
        sim.step()
        self.assertEqual(alternative, [True], "the alternative grant still authorizes the role")
        execution = next(e for e in sim.runtime['executions'].values() if e['action']['id'] == 'AC-revoked')
        self.assertEqual(execution['status'], 'ended')
        self.assertNotEqual(execution['outcome'], 'output_accepted')
        self.assertEqual(execution.get('stop_requested'), 'grant_revoked')
        engine = sim.engine
        self.assertEqual(json.loads(engine.store.read(execution['result_ref'], engine.head))['execution_id'], execution['id'])
        # The late output the model wrote is preserved with the execution's output files.
        preserved, = [row for row in execution['output_files'] if row['path'] == 'output.json']
        self.assertEqual(json.loads(engine.store.read(preserved['artifact_ref'], engine.head))['report'],
                         'Preserve the completed portion.')
        self.assertIn("AC-revoked", sim.runtime["waiting_actions"])

    def test_local_call_timeout_parks_only_the_timed_out_request(self):
        """A call past its local deadline is stopped by the owner, and its ``stopped`` result parks only its request.

        The legacy runner slept past the one-second deadline, waited for its stop
        flag and returned ``stopped``. Here the owner's call steps prepare the call
        (``_call_steps``), its model process is a Jobs-fake Job reported started,
        the Sim clock moves past the deadline, the owner's stop judgment answers
        the call's ``should_stop``, and the runner's ``stopped`` result goes back
        into the steps after the calls port reported the call returned: the
        product's routing of a stopped result.
        """
        from do_math.windows_job import process_identity
        # The one-second deadline belongs to the calls under test, not to activation's intent calls.
        sim = configured_sim(call_timeout_seconds=1)
        engine = sim.engine
        engine.runtime["queue"] = [{"id": "AC-timeout", "role": "maintenance"},
                                   {"id": "AC-independent", "role": "research_preparation"}]
        engine._save()
        steps = engine._call_steps(engine.runtime["queue"][0])
        arguments = next(steps)
        sim.jobs.programs.insert(0, (lambda argv: argv == ['model', 'process'], lambda argv, cwd, env: 0))
        job = sim.jobs.launch(['model', 'process'], cwd=arguments['workspace'],
                              name=arguments['launch_ticket']['job_name'])
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            self.assertFalse(arguments['should_stop'](), 'the deadline has not passed yet')
            # The legacy runner slept 1.05 s; the Sim's clock moves past the deadline instead.
            sim.advance(1.05)
            self.assertTrue(arguments['should_stop'](), 'the owner did not stop the call past its deadline')
            self.assertTrue(stop_requested(arguments['workspace']))
        finally:
            job.terminate()
            job.close()
            result = {"status": "stopped", "output": None, "usage": {}, "error": "local call deadline"}
            # The owner's calls port reports the returned local call before it resumes the steps
            # (``ModelCalls.collect`` calls ``on_returned``, the engine's ``_local_call_returned``).
            engine._local_call_returned(arguments['execution_id'], result)
            with self.assertRaises(StopIteration) as ended:
                steps.send(result)
        # The stopped result ends the call; the owner goes on (the steps return its continuation flag).
        self.assertIs(ended.exception.value, True)
        execution = sim.runtime["executions"][arguments['execution_id']]
        self.assertEqual((execution["status"], execution["outcome"]), ("ended", "execution_incomplete"))
        self.assertNotEqual(sim.runtime["status"], "paused")
        self.assertIn("AC-timeout", sim.runtime["waiting_actions"])
        self.assertEqual(sim.runtime["waiting_actions"]["AC-timeout"]["kind"], "execution_failure")
        self.assertTrue(any(a.get("id") == "AC-independent" for a in sim.runtime["queue"]))

if __name__ == "__main__":
    unittest.main()
