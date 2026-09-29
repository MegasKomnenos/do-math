"""Regression contracts for evidence acceptance and bounded failure recovery.

The scheduler, Git snapshots and Git reservations are real. Model replies are
scripted to make the otherwise nondeterministic failure ordering reproducible.
"""
import json
from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import purpose_fixtures as purpose
from purpose_fixtures import CheckedRunner
from runner_fixtures import common, contract_checks, formal_ok
from do_math.engine import control
from do_math.knowledge import assess_use, revise_knowledge
from do_math.context_store import fit_context
from do_math.planning import contract_hash
from do_math.canonical import canonical_json
from research_fixtures import FixtureAdapter, await_control, restore_template
from state_fixtures import ACTIVE_LEAN_COMMAND, active_instance
from do_math.engine import ResearchEngine
from unittest.mock import patch
from research_fixtures import candidate, contract_review, disposition, assessment, supply_observation_rules


def prepared_tasks(root, shared, *, config, count):
    """``restore_template`` build: validated active state with ``count`` nonformal tasks
    ``"0"``..., each actually prepared, contract-reviewed and selected by the plan,
    so that ``count`` ``research_work`` actions are queued. Returns the instance ID.

    Preparation and approval are real applications, never injected ready flags.
    """
    runner = purpose.PurposeRunner()
    original = runner.answer
    def answer(role, context, workspace):
        if role != "research_preparation":
            return original(role, context, workspace)
        candidates = [candidate(str(i), formal=False) for i in range(count)]
        (workspace / "activity-extensions.json").write_bytes(canonical_json({
            "contract_checks": contract_checks(candidates), "model_assessments": [
                {"task_title": item["title"], "difficulty": "high", "importance": "medium", "reason": "Bounded scenario"}
                for item in candidates]}))
        return {**common(role), "candidates": candidates}
    runner.answer = answer
    instance_id = active_instance(root, shared, config=config)
    engine = ResearchEngine(root / "repository", instance_id, runner=runner, formal_verifier=purpose.formal_fixture)
    with patch("do_math.local_host.adapter_for", return_value=FixtureAdapter()):
        for _ in range(45):
            engine.run(max_steps=1)
            if sum(a["role"] == "research_work" for a in engine.runtime["queue"]) == count:
                break
        else:
            raise AssertionError("The prepared tasks were not queued for work: " + repr(engine.status()))
    if any(e["status"] != "ended" for e in engine.runtime["executions"].values()):
        raise AssertionError("A template must not end with unfinished executions")
    return instance_id


class BoundaryFixture(purpose.ActivatedPurposeHarness):
    def engine(self, runner, count=1, **configuration):
        # Public initialization and the preparation chain have separate coverage.
        # Start these boundary cases from a copy of validated active state with
        # ``count`` actually prepared and reviewed tasks (``prepared_tasks``).
        # A rejected submission is not retried (max_output_repairs=0), as the
        # currentness cases require; the other cases reach no rejected
        # submission, so one value lets all cases share their start state.
        config = self.fixture_config(**{"max_output_repairs": 0, **configuration})
        if count:
            self.root, instance_id = restore_template(prepared_tasks, config=config, count=count)
            engine, _ = self._engine(instance_id, purpose.PurposeRunner())
        else:
            engine, _ = self.make_active(**config)
        engine.runner = CheckedRunner(runner)
        return engine


def note(title="Computation", **changes):
    return {"kind": "observation", "title": title, "statement": "The result is one.",
            "summary": "A bounded computation.", "explanation": "Exact finite computation.",
            "lean_code": "", "declaration_names": [], "dependencies": [], **changes}


def returned(role, **changes):
    output = common(role)
    if role == "research_work":
        output.update(outcome="submitted", report="The assigned scope was examined.", checkpoint="Ready.")
    return {"status": "completed", "output": {**output, **changes}, "usage": {}, "error": None}


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = BoundaryFixture()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_newly_reported_knowledge_dependencies_bind_the_read_snapshot(self):
        for declaration in ("used_sources", "dependencies", "knowledge_path"):
            with self.subTest(declaration=declaration):
                class Runner:
                    def run(inner, **args):
                        args["on_started"]({"pid": 1})
                        original = json.loads((args["workspace"] / "input/knowledge" / (kid + ".json")).read_bytes())
                        self.assertEqual(original["statement"], "The result is one.")
                        await_control(engine, control(self.fixture.repo, engine.instance["id"], "knowledge", config={
                            "operation": "revise", "id": kid, "changes": {"statement": "The result is two."},
                            "reason": "Correct the computation."}))
                        dependencies = [kid] if declaration == "dependencies" else []
                        used = [kid] if declaration == "used_sources" else []
                        if declaration == "knowledge_path":
                            used = ["input/knowledge/" + kid + ".json"]
                        return returned("research_work", used_sources=used,
                                        knowledge=[note("Derived", dependencies=dependencies)])
                engine = self.fixture.engine(Runner(), count=1)
                control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": note()})
                engine.process_controls()
                kid = next(iter(engine.instance["knowledge"]))
                engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] == "research_work"]
                engine._save()
                engine.run(max_steps=1)
                execution = next(e for e in engine.runtime["executions"].values() if e["role"] == "research_work")
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertEqual(execution['error_kind'], 'currentness_changed')
                self.assertTrue(any(row['rule_id'] == 'integration.currentness'
                                    for row in execution['integration_result']['issues']))
                self.assertFalse(any(k["title"] == "Derived" for k in engine.instance["knowledge"].values()))

    def test_identity_review_ignores_unrelated_source_change_but_checks_required_source(self):
        import tempfile
        sources = tempfile.TemporaryDirectory()
        self.addCleanup(sources.cleanup)
        for required in (False, True):
            with self.subTest(required=required):
                # Outside the engine's root: each engine replaces the previous copy.
                source = Path(sources.name) / ("required.txt" if required else "unrelated.txt")
                source.write_text("original", encoding="utf-8")
                class Runner:
                    def run(inner, **args):
                        context = purpose.parse_context(args["prompt"], args["workspace"])
                        args["on_started"]({"pid": 1})
                        source.write_text("corrected", encoding="utf-8")
                        await_control(engine, control(self.fixture.repo, engine.instance["id"], "source", config={"path": str(source)}))
                        return returned("identity_review", proposal_digest=context["role_review"]["proposal_digest"],
                                        used_sources=["proposal:statement"], decision="match", findings=[], scope_complete=True)
                # Validated active state without prepared tasks; the formal check
                # needs the active environment's configured command.
                engine = self.fixture.engine(Runner(), count=0, lean_command=list(ACTIVE_LEAN_COMMAND))
                engine.formal_verifier = formal_ok
                control(self.fixture.repo, engine.instance["id"], "source", config={"path": str(source)})
                control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate":
                    note("Formal claim", kind="theorem", lean_code="theorem t : True := by trivial",
                         declaration_names=["t"], source_refs=[source.name] if required else [])})
                engine.process_controls()
                kid = next(kid for kid, row in engine.instance['knowledge'].items() if row['title'] == 'Formal claim')
                engine._enqueue('formal_check', kid)
                for _ in range(25):
                    engine.runtime['queue'] = [a for a in engine.runtime['queue']
                        if a.get('target') == kid and a['role'] in {'formal_check', 'identity_review'}]
                    engine._save()
                    engine.run(max_steps=1)
                    completed = [e for e in engine.runtime['executions'].values()
                                 if e['role'] == 'identity_review' and e['action'].get('stage') == 'initial'
                                 and e['status'] == 'ended']
                    if completed:
                        break
                else:
                    self.fail('The fixed initial review never ran: ' + str({
                        'executions': [{k: e.get(k) for k in ('role', 'outcome', 'error', 'integration_result')}
                                       for e in engine.runtime['executions'].values()],
                        'queue': engine.runtime['queue'],
                        'review_cycles': engine.runtime['review_cycles']}))
                execution = completed[0]
                self.assertEqual(execution["outcome"], "execution_incomplete" if required else "output_accepted")

    def test_changed_prerequisite_task_assessment_invalidates_its_running_consumer(self):
        from do_math.system_clock import new_id
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                role = context["action"]["role"]
                args["on_started"]({"pid": 1})
                if role == "task_contract_review":
                    return returned(role, **contract_review(context))
                if role == "research_plan":
                    source = next(t for t in context["tasks"] if t["id"] == prerequisite_id)
                    return returned(role, task_assessments=[assessment(source)],
                        dispositions=[{**disposition(tid, kind="not_selected"), "uncertainty": ""}
                                      for tid in context["ready_task_ids"]],
                        goal_audit=False, preparation_requests=[])
                if context["task"]["id"] == prerequisite_id:
                    return returned("research_work", used_sources=[kid])
                from do_math.knowledge import plan_impact, revision_roots
                changes = {"statement": "The result is two."}
                impact = plan_impact(engine.instance, engine.runtime,
                    revision_roots(engine.instance, kid), [])
                request_id = control(self.fixture.repo, engine.instance["id"], "knowledge", config={
                    "operation": "revise", "id": kid, "changes": changes,
                    "declared_impact": impact["computed_impact"], "reason": "Correct a prerequisite result."})
                await_control(engine, request_id)
                self.assertTrue(any(h.get("kind") == "user_control" and
                    h.get("request", {}).get("id") == request_id["request_id"] for h in engine.runtime["history"]),
                    "The concurrent knowledge revision must actually be accepted")
                return returned("research_work", used_sources=[prerequisite_id])
        engine = self.fixture.engine(Runner(), count=2)
        control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": note()})
        engine.process_controls()
        kid = next(iter(engine.instance["knowledge"]))
        tasks = sorted(engine.runtime["tasks"].values(), key=lambda t: t["title"])
        prerequisite_id, consumer_id = [t["id"] for t in tasks]
        engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a.get("target") == prerequisite_id]
        engine._save()
        engine.run(max_steps=1)
        prerequisite = engine.runtime["tasks"][prerequisite_id]
        self.assertTrue(prerequisite["results"], "Prerequisite must have actual accepted work before assessment")
        engine.runtime["queue"] = [{"id": new_id("AC"), "role": "research_plan", "target": None,
                                    "reason": "Assess the returned prerequisite"}]
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual("completed", engine.runtime["tasks"][prerequisite_id]["status"])
        task = engine.runtime["tasks"][consumer_id]
        task.update(dependencies=[prerequisite_id], reviews=[], status="planned", revision=task["revision"] + 1)
        engine.runtime["queue"] = [{"id": new_id("AC"), "role": "task_contract_review", "target": consumer_id,
                                    "reason": "Independently inspect the consumer dependency"}]
        engine._save()
        engine.run(max_steps=1)
        self.assertTrue(engine.runtime["tasks"][consumer_id]["reviews"])
        engine.runtime["queue"] = [{"id": new_id("AC"), "role": "research_work", "target": consumer_id,
                                    "reason": "Consume the approved prerequisite"}]
        engine._save()
        engine.run(max_steps=1)
        execution = next(e for e in engine.runtime["executions"].values()
                         if e["role"] == "research_work" and e["action"]["target"] == consumer_id)
        self.assertFalse(engine.runtime["tasks"][prerequisite_id]["assessment"]["current"])
        self.assertEqual(execution["outcome"], "execution_incomplete")

    def test_failed_request_does_not_stop_a_running_independent_worker(self):
        peer_started = threading.Event()
        observed = {"stopped": False}
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                args["on_started"]({"pid": 1})
                if context["action"]["role"] != "research_work":
                    # The failure's diagnosis is not under test; it ends without stopping anyone.
                    return {"status": "failed", "output": None, "usage": {}, "error": "diagnosis not under test"}
                if context["task"]["title"] == "0":
                    if not peer_started.wait(10):
                        raise AssertionError("peer never started")
                    return {"status": "failed", "output": None, "usage": {}, "error": "diagnosed retry failed"}
                (args["workspace"] / "result.txt").write_text("Independent result.", encoding="utf-8")
                peer_started.set()
                until = time.monotonic() + 2
                while time.monotonic() < until:
                    if args["should_stop"]():
                        observed["stopped"] = True
                        return {"status": "stopped", "output": None, "usage": {}, "error": "unrelated pause"}
                    time.sleep(.02)
                return returned("research_work")
        engine = self.fixture.engine(Runner(), count=2)
        failed_action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_work'
                             and engine.runtime['tasks'][a['target']]['title'] == '0')
        failed_id = failed_action["id"]
        engine._save()
        engine.run(max_steps=2)
        self.assertFalse(observed["stopped"], "one failed request revoked an independent worker")
        self.assertNotEqual(engine.runtime["status"], "paused")
        self.assertIn(failed_id, engine.runtime["waiting_actions"])
        peer = next(e for e in engine.runtime["executions"].values()
                    if e["role"] == "research_work" and e["action"]["id"] != failed_id)
        self.assertEqual(peer["outcome"], "output_accepted")
        self.assertTrue(any(f["path"] == "result.txt" for f in peer["output_files"]))
        control(self.fixture.repo, engine.instance["id"], "resume", origin="operator")
        engine.process_controls()
        self.assertNotIn(failed_id, [a.get("id") for a in engine.runtime["queue"]])

    def test_execution_failure_is_parked_before_diagnosis(self):
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "local execution failure"}
        engine = self.fixture.engine(Runner(), count=1)
        failed_id = engine.runtime["queue"][0]["id"]
        engine.run(max_steps=1)
        self.assertNotIn(failed_id, [a.get("id") for a in engine.runtime["queue"]])
        self.assertEqual(engine.runtime["waiting_actions"][failed_id]["kind"], "execution_failure")
        self.assertTrue(any(a["role"] == "operational_review" for a in engine.runtime["queue"]))

    def test_same_oversized_contract_is_not_automatically_requeued(self):
        class Runner:
            def run(inner, **args):
                raise AssertionError("oversized contract must not start a model")
        engine = self.fixture.engine(Runner(), count=1, max_input_bytes=500000)
        task = next(iter(engine.runtime["tasks"].values()))
        task.update(question="q" * 600000, status="planned", reviews=[])
        engine.runtime["queue"] = []
        engine._save()
        engine.run(max_steps=1)
        for _ in range(3):
            engine._refresh_readiness()
        failures = [row for row in engine.runtime.get("input_overflows", []) if row["action"]["role"] == "task_contract_review"]
        self.assertEqual(len(failures), 1)
        attempts = [e for e in engine.runtime['executions'].values()
                    if e['role'] == 'task_contract_review' and e['action'].get('target') == task['id']
                    and e.get('input_preparation', {}).get('reason') == 'input overflow']
        self.assertEqual(len(attempts), 1)
        self.assertFalse(attempts[0].get('started_at'))
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == task['id']
                             for a in engine.runtime['queue']))

    def test_large_accepted_report_survives_revision_review_and_resumed_work(self):
        roles, work_calls = [], []
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                role = context["action"]["role"]
                roles.append(role)
                args["on_started"]({"pid": 1})
                if role == "research_work":
                    work_calls.append(context["task"]["revision"])
                    if len(work_calls) == 1:
                        (args["workspace"] / "evidence.txt").write_bytes(b"preserved partial evidence")
                        return returned(role, outcome="partial", report="p" * 600000, remaining_work=["Resolve the remaining case."])
                    self.assertEqual(context["task"]["results"][0]["report"], "p" * 600000)
                    previous = next(f for prior_task in context['tasks']
                                    if prior_task['id'] == context['task']['id']
                                    for result in prior_task['results']
                                    for f in result.get('output_files', []) if f['path'] == 'evidence.txt')
                    self.assertEqual((args["workspace"] / previous["local_path"]).read_bytes(), b"preserved partial evidence")
                    return returned(role)
                if role == "research_plan":
                    assessments = [{"task_id": task["id"], "decision": "incomplete", "reason": "The remaining case is explicit.",
                        "item_dispositions": [{"obligation_id": obligation["id"], "kind": "open", "evidence_refs": []}
                                              for obligation in task["completion_obligations"]],
                        "unresolved": []}
                        for task in context["tasks"] if task['id'] in context.get('returned_task_ids', [])]
                    (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({"model_assessments": [
                        {"task_id": tid, "difficulty": "high", "importance": "medium", "reason": "Continue the explicit unresolved fixture case."}
                        for tid in context["ready_task_ids"]], "revision_requests": [
                            {"record_ids": [a["task_id"]], "reason": "Revise the explicit unfinished case."}
                            for a in assessments if next(t for t in context['tasks'] if t['id'] == a['task_id'])['revision'] == 1]}))
                    return returned(role, dispositions=[{**disposition(tid), "uncertainty": ""} for tid in context["ready_task_ids"]], task_assessments=assessments,
                        goal_audit=False, preparation_requests=[])
                if role == "research_preparation":
                    task = context["tasks"][0]
                    proposal = purpose.candidate(task['title'], formal=False, revises=task['id'])
                    extensions = {"model_assessments": [
                        {"task_title": task["title"], "difficulty": "high", "importance": "medium", "reason": "The revised fixture retains the unresolved case."}],
                        "contract_checks": contract_checks([task]),
                        "revision_resolutions": [{"record_id": task["id"], "disposition": "revised", "reason": "The remaining case is the new contract."}]}
                    supply_observation_rules([proposal], extensions)
                    (args['workspace'] / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                    return returned(role, candidates=[proposal])
                if role == "task_contract_review":
                    return returned(role, **contract_review(context))
                raise AssertionError("unexpected role: " + role)
        engine = self.fixture.engine(Runner(), count=1)
        for _ in range(12):
            engine.run(max_steps=1)
            if len(work_calls) == 2:
                break
        self.assertEqual(len(work_calls), 2, {
            'executions': [{k: e.get(k) for k in ('role', 'outcome', 'error', 'integration_result')}
                           for e in engine.runtime['executions'].values()],
            'waiting': engine.runtime['waiting_actions'], 'queue': engine.runtime['queue']})
        self.assertGreater(work_calls[1], work_calls[0])
        self.assertIn("task_contract_review", roles)
        self.assertFalse(engine.runtime.get("input_overflows"))
        worker_results = [e["outcome"] for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertEqual(worker_results, ["output_accepted", "output_accepted"], [
            {k: e.get(k) for k in ('outcome', 'error', 'error_kind', 'integration_result')}
            for e in engine.runtime['executions'].values() if e['role'] == 'research_work'])


class HistoricalInputTests(unittest.TestCase):
    def test_large_checkpoint_and_operational_evidence_use_exact_readable_references(self):
        import tempfile
        checkpoint = {"current_claim": "x" * 600000, "evidence_paths": [], "attempts": [],
                      "remaining_work": [], "next_step": "Continue.", "progress_state": "working"}
        contexts = [
            ({"resume_checkpoint": {"kind": "worker_checkpoint", "value": checkpoint}}, []),
            ({"recovery_materials": {"checkpoint": checkpoint}}, []),
            ({"execution_to_review": {"id": "EX-old", "role": "research_work", "status": "ended", "details": checkpoint},
              "observation": {"execution_id": "EX-old", "reason": "checkpoint", "sample": {"checkpoint": checkpoint}}},
             ["execution_to_review", "observation"]),
        ]
        for additions, required in contexts:
            with self.subTest(fields=list(additions)), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                original = {"goal": "g", "action": {"role": "operational_review"}, **additions}
                result = fit_context(original, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", *required])
                self.assertEqual("input_overflow", result["overflow"]["kind"])
                self.assertEqual(original, result["context"])
                for key, value in additions.items():
                    ref = next(row for row in result["manifest"] if row["key"] == key)
                    self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), value)

    def test_large_repair_action_and_previous_execution_remain_readable_by_reference(self):
        import tempfile
        action = {"id": "AC-repair", "role": "research_preparation", "repair_attempt": 1,
                  "repair": {"execution_id": "EX-old", "error": "bad extension",
                             "previous_output": {"summary": "x" * 600000, "candidates": []}}}
        context = {"goal": "g", "action": action, "previous_execution": {"id": "EX-old", "action": action}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
            self.assertEqual("input_overflow", result["overflow"]["kind"])
            current = result["context"]["action"]
            self.assertEqual(current["id"], action["id"])
            self.assertEqual(current["role"], action["role"])
            ref = next(row for row in result["manifest"] if row["key"] == "action")
            self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), action)

    def test_preserved_history_does_not_recreate_current_knowledge_dependencies(self):
        from do_math.knowledge_records import create_candidate
        for key in ("history", "use_history", "review_history", "revision_history", "assessment_history", "governance_history", "previous_initial_reviews"):
            with self.subTest(key=key):
                instance, _ = create_candidate({}, {**note(), "id": "KN-A"}, source_ref="source", actor_ref="producer")
                instance, _ = create_candidate(instance, {**note("Independent"), "id": "KN-B", key: [{"dependencies": ["KN-A"]}]},
                                                source_ref="source", actor_ref="producer")
                before = assess_use(instance["knowledge"]["KN-B"], instance)
                changed, _ = revise_knowledge(instance, {}, "KN-A", {"statement": "corrected"}, reason="correction", actor_ref="user")
                self.assertFalse(changed["knowledge"]["KN-B"].get("use_suspended", False))
                self.assertEqual(before, assess_use(changed["knowledge"]["KN-B"], changed))

    def test_large_task_history_is_readable_without_inflating_the_current_contract(self):
        import tempfile
        task = {**candidate("Current contract"), "id": "TK-A", "revision": 2, "results": [{"report": "x" * 600000}],
                "revision_history": [{"question": "old", "results": [{"report": "x" * 600000}]}]}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"goal": "g", "action": {"role": "task_contract_review"}, "task": task}
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", "task"])
            self.assertEqual("input_overflow", result["overflow"]["kind"])
            current = result["context"]["task"]
            self.assertEqual(current["question"], task["question"])
            self.assertEqual(current["completion_obligations"], task["completion_obligations"])
            self.assertEqual(contract_hash(current), contract_hash(task))
            ref = next(row for row in result["manifest"] if row["key"] == "task")
            self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), task)


if __name__ == "__main__":
    unittest.main(verbosity=2)
