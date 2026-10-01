"""The engine's queue, dispatch, publication and call steps on a Sim, from one queued, published preparation.

The legacy ``efficiency_instance`` restored a synthetic active state and queued a
preparation; here the start is the Sim's public activation with the same queued,
published preparation (``QueuedPreparation.open``). Engine methods are called
directly where the case is one layer-2 rule; a pause arrives by public control;
the model process of a call is a Jobs-fake Job carrying the launch ticket's name.
"""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math.context_store import prepare_role_input
from do_math.engine import ResearchEngine
from do_math.windows_job import process_identity
from support.engine_context import GitBatches, record_contexts
from support.sim import Sim, warm_template

setUpModule = warm_template


def apply_control(sim, action, **options):
    """A public control the owner applies now; a rejection fails the test's setup."""
    request = sim.control(action, **options)
    sim.engine.process_controls()
    rejected = [row for row in sim.runtime['history'] if row.get('kind') == 'rejected_user_control'
                and row.get('request', {}).get('id') == request['request_id']]
    if rejected:
        raise AssertionError('public control rejected: ' + repr(rejected))
    return request


def charter_change(engine, **content_changes):
    """A change to the current charter; its approval stays public (legacy ``research_fixtures.charter_change``)."""
    current = engine._governance()["charter"]
    return {"kind": "charter", "record": {"id": engine.ports.clock.new_id("CH"), "kind": "charter",
        "revision": current["revision"] + 1, "supersedes": [current["id"]],
        "content": {**deepcopy(current["content"]), **deepcopy(content_changes)}}}


class ObservationMerge(unittest.TestCase):
    def test_merged_review_keeps_all_obligations_and_evidence_refs(self):
        engine = Sim.activated().engine
        engine.runtime["queue"] = []
        engine._enqueue("operational_review", "EX-worker", live=True,
                        obligation_ids=["OB-a"], observation_refs=["artifact:a"],
                        observation={"kind": "operational_review_due", "reason": "explicit", "sequence": 1})
        first = deepcopy(engine.runtime["queue"][0])
        engine._enqueue("operational_review", "EX-worker", live=True,
                        obligation_ids=["OB-b"], observation_refs=["artifact:b"],
                        observation={"kind": "operational_review_due", "reason": "periodic", "sequence": 2})
        self.assertEqual(len(engine.runtime["queue"]), 1)
        merged = engine.runtime["queue"][0]
        self.assertEqual(merged["id"], first["id"])
        self.assertEqual(merged["obligation_ids"], ["OB-a", "OB-b"])
        self.assertEqual(merged["observation_refs"], ["artifact:a", "artifact:b"])
        self.assertEqual(merged["observation"]["sequence"], 2)


class QueuedPreparationTests(unittest.TestCase):
    """An engine after the public activation with one queued, published preparation."""

    def setUp(self):
        self.open(charter=False)

    def open(self, *, charter):
        """A restored Sim with one published preparation; ``charter`` also approves requirement ``explain``.

        The charter change is a public decision control; it opens a plan for its event.
        """
        self.sim = Sim.activated()
        self.engine = self.sim.engine
        self.workspace = Path(self.engine.instance['workspace'])
        (self.workspace / 'runs').mkdir(exist_ok=True)
        self.engine._enqueue("research_preparation", reason="Prepare the bounded efficiency fixture")
        self.engine._save()
        if charter:
            apply_control(self.sim, 'decision', config={'change': charter_change(self.engine, academic_requirements=[
                {"id": "explain", "scope": "solution", "criteria": ["explain structure"], "assessor": "research_plan"}])})

    def startup(self):
        self.open(charter=True)
        self.engine._refresh_readiness()
        return next(a for a in self.engine.runtime["queue"] if a["role"] == "research_plan")

    @contextmanager
    def model_process(self, arguments):
        """The call's model process: a Job of the launch ticket's name, reported started, ended on exit."""
        self.sim.jobs.programs.insert(0, (lambda argv: argv == ['model', 'process'], lambda argv, cwd, env: 0))
        job = self.sim.jobs.launch(['model', 'process'], cwd=arguments['workspace'],
                                   name=arguments['launch_ticket']['job_name'])
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            yield job
        finally:
            job.terminate()
            self.assertTrue(job.wait(10))
            self.assertEqual(job.inspect().active_processes, 0)
            job.close()

    def test_pending_preparation_keeps_every_reason_without_duplicate_text(self):
        e = self.engine
        e.runtime["queue"] = []
        e._enqueue("research_preparation", reason="Investigate definition A", event_refs=["A"])
        e._enqueue("research_preparation", reason="Check independent obligation B", event_refs=["B"])
        e._enqueue("research_preparation", reason="Check independent obligation B", event_refs=["B"])
        self.assertEqual(len(e.runtime["queue"]), 1)
        action = e.runtime["queue"][0]
        self.assertIn("Investigate definition A", action["reason"])
        self.assertEqual(action["reason"].count("Check independent obligation B"), 1)
        self.assertEqual(action["event_refs"], ["A", "B"])

    def test_stopping_execution_input_is_never_merged(self):
        e = self.engine
        e.runtime["queue"] = [{"id": "A", "role": "research_preparation", "reason": "old"}]
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "stopping", "action": deepcopy(e.runtime["queue"][0])}
        e._enqueue("research_preparation", reason="new", event_refs=["later"])
        self.assertEqual(len(e.runtime["queue"]), 2)
        self.assertEqual(e.runtime["queue"][0]["reason"], "old")
        self.assertNotIn("event_refs", e.runtime["queue"][0])

    def test_active_charter_update_can_plan_and_preserves_its_event(self):
        action = self.startup()
        before = deepcopy(self.engine.runtime["events"])
        self.assertNotIn('initial_preparation_wait', action)
        self.assertTrue(self.engine._dispatchable(action))
        self.assertEqual(self.engine.runtime["events"], before)
        self.assertTrue(self.engine.runtime["pending_events"])

    def test_charter_replanning_preserves_ongoing_preparation_and_consumes_its_event(self):
        """About 5 s, over the 2 s Sim budget: three model calls run through the worker, which is what it checks."""
        self.startup()
        e = self.engine
        model = record_contexts(self.sim)
        e._save()
        e.run(max_steps=3)
        plans = [ctx for role, ctx in model.contexts if role == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]['ready_task_ids'], [])
        self.assertCountEqual([role for role, _ in model.contexts],
                              ['research_preparation', 'task_contract_review', 'research_plan'])
        event = next(row for row in reversed(e.runtime['events']) if row['kind'] == 'user_decision_applied')
        self.assertTrue(any(row.get('kind') == 'event_consumption' and event['id'] in row['event_ids']
                            for row in e.runtime['history']))
        self.assertNotIn(event['id'], e.runtime['pending_events'])

    def test_regular_empty_plan_can_still_dispatch(self):
        self.assertTrue(self.engine._dispatchable({"role": "research_plan", "reason": "assess failed approach"}))

    def test_pause_received_during_input_preparation_prevents_model_start(self):
        from support.provider_probes import ObservedCalls
        from support.storage_finish_installation import at_return
        e = self.engine
        before_executions = set(e.runtime['executions'])
        before_runs = set((self.workspace / 'runs').iterdir())
        with ObservedCalls(upkeep=e._upkeep, model=self.sim.model.spawn, launch=self.sim.jobs.launch) as calls:
            with at_return(e._context, lambda: self.sim.control('pause', text='stop during materialization')) as contexts:
                generator = e._call_steps(e.runtime['queue'][0])
                with self.assertRaises(StopIteration) as stopped:
                    next(generator)
                self.assertIsInstance(stopped.exception.value, bool)
        self.assertEqual(len(contexts), 1)
        self.assertIsInstance(contexts[0], dict)
        self.assertEqual(calls.count('upkeep'), 0)
        self.assertEqual(calls.count('model'), 0)
        self.assertEqual(calls.count('launch'), 0)
        self.assertEqual(e.runtime['status'], 'paused')
        added = set(e.runtime['executions']) - before_executions
        self.assertEqual(len(added), 1)
        execution = e.runtime['executions'][added.pop()]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'cancelled'))
        self.assertIsNone(execution.get('started_at'))
        self.assertNotIn('capacity', execution)
        self.assertEqual(set((self.workspace / 'runs').iterdir()), before_runs)

    def test_pause_before_model_resume_has_no_checkpoint_grace(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        try:
            with self.model_process(arguments):
                self.sim.control('pause', text='stop before model resume')
                e._apply_inbox(pump=False)  # The owner pass applies and publishes the control.
                e._upkeep()
                self.assertTrue(arguments['should_stop'](), 'a suspended model must not resume for checkpoint grace')
        finally:
            with self.assertRaises(StopIteration) as ended:
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'stopped before resume'})
            # The stopped result ends the call: the generator returns the owner's continuation flag.
            self.assertIsInstance(ended.exception.value, bool)
            self.assertEqual(e.runtime['status'], 'paused')

    def test_execution_effort_is_its_pinned_profile_effort_not_the_current_setting(self):
        from do_math.execution_profiles import resolve_profile
        from do_math.record_schemas import EFFORTS
        e = self.engine
        action = e.runtime['queue'][0]
        pinned = resolve_profile(e.instance['execution_profiles'],
                                 e.instance['role_profile_refs'][action['role']][0])['ai']['effort']
        # A configure that changes only the effort leaves pinned profile editions as they were.
        e.instance['config']['effort'] = next(level for level in EFFORTS if level != pinned)
        steps = e._call_steps(action)
        arguments = next(steps)
        try:
            self.assertEqual(arguments['effort'], pinned)
            self.assertEqual(e.runtime['executions'][arguments['execution_id']]['effort'], pinned)
        finally:
            steps.close()

    def test_running_model_stops_immediately_after_public_pause(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        try:
            with self.model_process(arguments):
                self.assertFalse(arguments['should_stop']())
                self.sim.control('pause', text='stop running work')
                e._apply_inbox(pump=False)  # The owner pass applies and publishes the control.
                e._upkeep()
                self.assertTrue(arguments['should_stop']())
                execution = e.runtime['executions'][arguments['execution_id']]
                self.assertEqual(execution['status'], 'stopping')
        finally:
            with self.assertRaises(StopIteration) as ended:
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'local stop requested'})
            # The stopped result ends the call: the generator returns the owner's continuation flag.
            self.assertIsInstance(ended.exception.value, bool)
            self.assertEqual(e.runtime['status'], 'paused')

    def test_initial_wait_ends_on_new_independent_user_decision(self):
        action = self.startup()
        event = self.engine._lifecycle_event("user_decision_applied", decision_id="new-policy")
        action["event_refs"].append(event["id"])
        self.assertTrue(self.engine._dispatchable(action))

    def test_empty_or_failed_initial_preparation_does_not_wait_forever(self):
        action = self.startup()
        for outcome in ("output_accepted", "execution_incomplete"):
            with self.subTest(outcome=outcome):
                self.engine.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
                    "status": "ended", "outcome": outcome, "action": {"role": "research_preparation"}}
                self.assertTrue(self.engine._dispatchable(action))

    def test_plan_receives_public_running_preparation_without_private_output(self):
        from support.entry import entry
        _entry = entry()
        e = self.engine
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "running", "input_snapshot": e.head, "goal_revision": 1, "policy_revision": 1,
            "action": {"id": "A", "role": "research_preparation", "reason": "derive last-car recurrence",
                       "repair": {"previous_output": {"secret": "private draft"}}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = e._context({"role": "research_plan"}, root / "plan")
            profile = next(p for p in e.instance["execution_profiles"].values() if p["role"] == "research_plan")
            # Unfinished preparations reach the plan as ongoing_work rows built from state.
            fitted = prepare_role_input(context, instance=e.instance, runtime=e.runtime, role="research_plan",
                profile=profile, snapshot=e.head, workspace=root / "plan", activity_id="AC-plan", clock=_entry.ports.clock)
        activities = [row for row in fitted["context"]["ongoing_work"] if row.get("execution_id") == "E"]
        self.assertEqual(len(activities), 1)
        self.assertEqual((activities[0]["goal_revision"], activities[0]["policy_revision"]), (1, 1))
        self.assertEqual(activities[0]["reason"], "derive last-car recurrence")
        self.assertEqual(activities[0]["input_snapshot"], e.head)
        self.assertNotIn("private draft", str(activities))

    def test_task_result_materialization_batches_reads_without_losing_files(self):
        from support.role_answers import candidate
        e = self.engine
        files = {f'runtime/artifacts/results/{i}.bin': bytes(range(256)) + bytes([i]) for i in range(12)}
        entries = [{'artifact_ref': path, 'path': Path(path).name,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)} for path, raw in files.items()]
        e.runtime['tasks']['T'] = {**candidate('materialization'), 'id': 'T', 'revision': 1, 'status': 'active', 'reviews': [],
                                   'results': [{'execution_id': 'E', 'output_files': entries}]}
        e.runtime['tasks']['T'].pop('revises_task_id')
        e._save(files)
        with tempfile.TemporaryDirectory() as directory, GitBatches(self.sim.ports.git_backend) as reads:
            root = Path(directory)
            context = e._context({'role': 'research_plan'}, root / 'results-plan')
            # One batch read of the Git port: the real backend starts one cat-file process for it.
            self.assertEqual(reads.count, 1, reads.calls)
            restored = context['tasks'][0]['results'][0]['output_files']
            self.assertEqual(len(restored), 12)
            for item in restored:
                self.assertEqual((root / 'results-plan' / item['local_path']).read_bytes(), files[item['artifact_ref']])

    def test_repeated_idle_save_does_not_publish_but_real_changes_do(self):
        e = self.engine
        e._save()
        first = e.head
        e._save()
        self.assertEqual(e.head, first)
        e.runtime["cycles"] += 1
        e._save()
        self.assertNotEqual(e.head, first)
        second = e.head
        e._save({"runtime/artifacts/idle-test/evidence.bin": b"\x00\xff"})
        self.assertNotEqual(e.head, second)
        self.assertEqual(e.store.read("runtime/artifacts/idle-test/evidence.bin", e.head), b"\x00\xff")

    def test_reopened_idle_engine_does_not_publish_again(self):
        from support.entry import entry
        _entry = entry()
        e = self.engine
        e._save()
        head = e.head
        reopened = ResearchEngine(e.store.repository, e.instance['id'], ports=self.sim.ports, codex_home=self.sim.codex_home, environment=self.sim.environment, host_id=self.sim.host_id)
        reopened._save()
        self.assertEqual(reopened.head, head)

    def test_merged_user_requests_keep_all_request_references(self):
        e = self.engine
        e.runtime['queue'] = []
        e._enqueue('research_plan', reason='first instruction', requested_by='UC-first')
        e._enqueue('research_plan', reason='second instruction', requested_by='UC-second')
        self.assertEqual(e.runtime['queue'][0].get('requested_by_refs'), ['UC-first', 'UC-second'])

    def test_readiness_is_derived_and_changes_with_contract_review_evidence(self):
        """About 3 s, over the 2 s Sim budget: two model calls run through the worker, which is what it checks."""
        e = self.engine
        e.run(max_steps=1)
        tid = next(iter(e.runtime["tasks"]))
        before = deepcopy(e._task_readiness[tid])
        self.assertNotEqual(before["state"], "ready")
        e._save()
        head = e.head
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[tid], before)
        e._save()
        self.assertEqual(e.head, head)
        e.run(max_steps=1)
        self.assertEqual(e.runtime["tasks"][tid]["status"], "planned")
        self.assertEqual(e._task_readiness[tid]["state"], "ready")
        self.assertNotEqual(e._task_readiness[tid], before)
        self.assertNotIn("task_readiness", e.store.load()[2])


if __name__ == '__main__':
    unittest.main()
