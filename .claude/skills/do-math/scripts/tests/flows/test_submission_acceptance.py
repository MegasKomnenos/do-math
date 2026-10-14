"""Regression contracts for evidence acceptance and bounded failure recovery, on a Sim.

The owner, its scheduler, the Git snapshots and reservations are the product's
on the port fakes; the model answers are scripted
(``support.submission_calls``), which makes the otherwise nondeterministic
failure ordering reproducible. What a legacy runner did while its call was in
flight (send a control and wait for the owner to apply it, watch for a stop)
happens in the call through the model double's hooks, with the owner taking
its turns in between. Each scene runs model calls through the worker, over the
2 s Sim budget, so the module is a flow.

The start of most scenes is ``support.scheduling_parallel.ready_work_sim``: the
legacy ``prepared_tasks`` build (tasks ``"0"`` ... actually prepared,
contract-reviewed and selected by a plan until one research work per task is
queued) with ``max_output_repairs`` 0, as the legacy boundary fixture set it.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.knowledge import plan_impact, revision_roots
from support.role_answers import assessment, candidate, contract_review, disposition
from support.observation_inputs import supply_observation_rules
from support.default_responder import common, contract_checks
from support.engine_lifecycle import applied
from support.model import amend
from support.scheduling_parallel import ready_work_sim, round_robin
from support.sim import Sim, warm_template
from support.submission_calls import applied_now, failed, submission_model, submitted

NO_REPAIR = {'max_output_repairs': 0}


def setUpModule():
    warm_template()
    ready_work_sim(1, **NO_REPAIR)
    ready_work_sim(2, **NO_REPAIR)
    ready_work_sim(1, max_input_bytes=500000, **NO_REPAIR)


def note(title="Computation", **changes):
    return {"kind": "observation", "title": title, "statement": "The result is one.",
            "summary": "A bounded computation.", "explanation": "Exact finite computation.",
            "lean_code": "", "declaration_names": [], "dependencies": [], **changes}


def returned(role, **changes):
    """The legacy runner's completed output for ``role``."""
    output = common(role)
    if role == "research_work":
        output.update(outcome="submitted", report="The assigned scope was examined.", checkpoint="Ready.")
    return {**output, **changes}


def imported(sim, candidate_row):
    applied(sim, "knowledge", config={"operation": "import", "candidate": candidate_row})
    return next(kid for kid, row in sim.instance["knowledge"].items() if row["title"] == candidate_row["title"])


def keep(sim, predicate):
    """Keep only the queued actions ``predicate`` accepts and publish the queue."""
    sim.engine.runtime["queue"] = [a for a in sim.engine.runtime["queue"] if predicate(a)]
    sim.engine._save()


def stop_requested(workspace):
    """The owner's stop request to a running worker: the file its stop judgment writes into the workspace."""
    return any(Path(workspace).rglob("stop-request.json"))


class AcceptanceTests(unittest.TestCase):
    def test_newly_reported_knowledge_dependencies_bind_the_read_snapshot(self):
        for declaration in ("used_sources", "dependencies", "knowledge_path"):
            with self.subTest(declaration=declaration):
                sim = ready_work_sim(1, **NO_REPAIR)
                kid = imported(sim, note())
                keep(sim, lambda a: a["role"] == "research_work")
                model = submission_model(sim)
                read = []

                def revise(context, workspace):
                    original = json.loads((Path(workspace) / "input/knowledge" / (kid + ".json")).read_bytes())
                    read.append(original["statement"])
                    applied_now(sim, "knowledge", config={"operation": "revise", "id": kid,
                        "changes": {"statement": "The result is two."}, "reason": "Correct the computation."})
                model.before("research_work", revise)
                dependencies = [kid] if declaration == "dependencies" else []
                used = [kid] if declaration == "used_sources" else []
                if declaration == "knowledge_path":
                    used = ["input/knowledge/" + kid + ".json"]
                model.on("research_work").reply(submitted(returned(
                    "research_work", used_sources=used, knowledge=[note("Derived", dependencies=dependencies)])))
                sim.step()
                # The call read the revision it was given, before the concurrent revision.
                self.assertEqual(read, ["The result is one."])
                execution = next(e for e in sim.runtime["executions"].values() if e["role"] == "research_work")
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertEqual(execution['error_kind'], 'currentness_changed')
                self.assertTrue(any(row['rule_id'] == 'integration.currentness'
                                    for row in execution['integration_result']['issues']))
                self.assertFalse(any(k["title"] == "Derived" for k in sim.instance["knowledge"].values()))

    def test_identity_review_ignores_unrelated_source_change_but_checks_required_source(self):
        sources = tempfile.TemporaryDirectory()
        self.addCleanup(sources.cleanup)
        for required in (False, True):
            with self.subTest(required=required):
                # Outside the Sim's root: each restore replaces the previous copy.
                source = Path(sources.name) / ("required.txt" if required else "unrelated.txt")
                source.write_text("original", encoding="utf-8")
                sim = Sim.activated()
                model = submission_model(sim)

                def correct(context, workspace):
                    if context["action"].get("stage") == "initial":
                        source.write_text("corrected", encoding="utf-8")
                        applied_now(sim, "source", config={"path": str(source)})
                model.before("identity_review", correct)
                model.on("identity_review", stage="initial").reply(amend(used_sources=["proposal:statement"]))
                applied(sim, "source", config={"path": str(source)})
                kid = imported(sim, note("Formal claim", kind="theorem", lean_code="theorem t : True := by trivial",
                                         declaration_names=["t"], source_refs=[source.name] if required else []))
                completed = []
                for _ in range(25):
                    keep(sim, lambda a: a.get('target') == kid and a['role'] in {'formal_check', 'identity_review'})
                    sim.step()
                    completed = [e for e in sim.runtime['executions'].values()
                                 if e['role'] == 'identity_review' and e['action'].get('stage') == 'initial'
                                 and e['status'] == 'ended']
                    if completed:
                        break
                else:
                    self.fail('The fixed initial review never ran: ' + str({
                        'executions': [{k: e.get(k) for k in ('role', 'outcome', 'error', 'integration_result')}
                                       for e in sim.runtime['executions'].values()],
                        'queue': sim.runtime['queue'], 'review_cycles': sim.runtime['review_cycles']}))
                self.assertEqual(completed[0]["outcome"], "execution_incomplete" if required else "output_accepted")

    def test_changed_prerequisite_task_assessment_invalidates_its_running_consumer(self):
        sim = ready_work_sim(2, **NO_REPAIR)
        kid = imported(sim, note())
        tasks = sorted(sim.runtime["tasks"].values(), key=lambda t: t["title"])
        prerequisite_id, consumer_id = [t["id"] for t in tasks]
        model = submission_model(sim)
        model.on("task_contract_review").reply(submitted(lambda ctx: returned("task_contract_review", **contract_review(ctx))))
        model.on("research_plan").reply(submitted(lambda ctx: returned(
            "research_plan", task_assessments=[assessment(next(t for t in ctx["tasks"] if t["id"] == prerequisite_id))],
            dispositions=[{**disposition(tid, kind="not_selected"), "uncertainty": ""} for tid in ctx["ready_task_ids"]],
            goal_audit=False, preparation_requests=[])))
        model.on("research_work", target=prerequisite_id).reply(submitted(returned("research_work", used_sources=[kid])))
        model.on("research_work", target=consumer_id).reply(
            submitted(returned("research_work", used_sources=[prerequisite_id])))
        revisions = []

        def revise(context, workspace):
            if context["action"]["target"] != consumer_id:
                return
            impact = plan_impact(sim.engine.instance, sim.engine.runtime, revision_roots(sim.engine.instance, kid), [])
            request = applied_now(sim, "knowledge", config={
                "operation": "revise", "id": kid, "changes": {"statement": "The result is two."},
                "declared_impact": impact["computed_impact"], "reason": "Correct a prerequisite result."})
            revisions.append(any(h.get("kind") == "user_control" and h.get("request", {}).get("id") == request["request_id"]
                                 for h in sim.engine.runtime["history"]))
        model.before("research_work", revise)
        keep(sim, lambda a: a.get("target") == prerequisite_id)
        sim.step()
        prerequisite = sim.runtime["tasks"][prerequisite_id]
        self.assertTrue(prerequisite["results"], "Prerequisite must have actual accepted work before assessment")
        sim.engine.runtime["queue"] = [{"id": sim.clock.new_id("AC"), "role": "research_plan", "target": None,
                                        "reason": "Assess the returned prerequisite"}]
        sim.engine._save()
        sim.step()
        self.assertEqual("completed", sim.runtime["tasks"][prerequisite_id]["status"])
        task = sim.engine.runtime["tasks"][consumer_id]
        task.update(dependencies=[prerequisite_id], reviews=[], status="planned", revision=task["revision"] + 1)
        sim.engine.runtime["queue"] = [{"id": sim.clock.new_id("AC"), "role": "task_contract_review", "target": consumer_id,
                                        "reason": "Independently inspect the consumer dependency"}]
        sim.engine._save()
        sim.step()
        self.assertTrue(sim.runtime["tasks"][consumer_id]["reviews"])
        sim.engine.runtime["queue"] = [{"id": sim.clock.new_id("AC"), "role": "research_work", "target": consumer_id,
                                        "reason": "Consume the approved prerequisite"}]
        sim.engine._save()
        sim.step()
        self.assertEqual(revisions, [True], "The concurrent knowledge revision must actually be accepted")
        execution = next(e for e in sim.runtime["executions"].values()
                         if e["role"] == "research_work" and e["action"]["target"] == consumer_id)
        self.assertFalse(sim.runtime["tasks"][prerequisite_id]["assessment"]["current"])
        self.assertEqual(execution["outcome"], "execution_incomplete")

    def test_failed_request_does_not_stop_a_running_independent_worker(self):
        sim = ready_work_sim(2, **NO_REPAIR)
        # The default resumes the earliest ready call; the waiting call must let its peer start.
        sim.ports.calls.choose = round_robin()
        model = submission_model(sim)
        titles = {tid: row["title"] for tid, row in sim.runtime["tasks"].items()}
        entered, observed = [], {"stopped": False, "watched": 0}

        def work(context, workspace):
            from support.fakes.calls import owner_turn
            if titles[context["action"]["target"]] == "0":
                for _ in range(200):
                    if entered:
                        return
                    owner_turn()
                raise AssertionError("peer never started")
            (Path(workspace) / "result.txt").write_text("Independent result.", encoding="utf-8")
            entered.append(context["execution_id"])
            # The legacy worker polled its stop flag for 2 s; this one watches the owner's stop request for 20 passes.
            for _ in range(20):
                owner_turn()
                observed["watched"] += 1
                if stop_requested(workspace):
                    observed["stopped"] = True
                    return
            # The owner parked the failed request while this worker was still running.
            observed["failure_parked"] = failed_id in sim.engine.runtime["waiting_actions"]
        model.before("research_work", work)
        failed_action = next(a for a in sim.runtime['queue'] if a['role'] == 'research_work'
                             and titles[a['target']] == '0')
        failed_id = failed_action["id"]
        model.on("research_work", target=failed_action["target"]).reply(failed("diagnosed retry failed"))
        # The failure's diagnosis is not under test; it ends without stopping anyone.
        model.on("operational_review").reply(failed("diagnosis not under test"))
        model.on("research_work").reply(submitted(returned("research_work")))
        sim.engine.run(max_steps=2)
        self.assertEqual(observed["watched"], 20)
        self.assertTrue(observed.get("failure_parked"), observed)
        self.assertFalse(observed["stopped"], "one failed request revoked an independent worker")
        self.assertNotEqual(sim.runtime["status"], "paused")
        self.assertIn(failed_id, sim.runtime["waiting_actions"])
        peer = next(e for e in sim.runtime["executions"].values()
                    if e["role"] == "research_work" and e["action"]["id"] != failed_id)
        self.assertEqual(peer["outcome"], "output_accepted")
        self.assertTrue(any(f["path"] == "result.txt" for f in peer["output_files"]))
        applied(sim, "resume", origin="operator")
        self.assertNotIn(failed_id, [a.get("id") for a in sim.runtime["queue"]])

    def test_execution_failure_is_parked_before_diagnosis(self):
        sim = ready_work_sim(1, **NO_REPAIR)
        model = submission_model(sim)
        model.on("research_work").reply(failed("local execution failure"))
        failed_id = sim.runtime["queue"][0]["id"]
        sim.step()
        self.assertNotIn(failed_id, [a.get("id") for a in sim.runtime["queue"]])
        self.assertEqual(sim.runtime["waiting_actions"][failed_id]["kind"], "execution_failure")
        self.assertTrue(any(a["role"] == "operational_review" for a in sim.runtime["queue"]))

    def test_same_oversized_contract_is_not_automatically_requeued(self):
        sim = ready_work_sim(1, max_input_bytes=500000, **NO_REPAIR)
        model = submission_model(sim)
        engine = sim.engine
        task = next(iter(engine.runtime["tasks"].values()))
        task.update(question="q" * 600000, status="planned", reviews=[])
        engine.runtime["queue"] = []
        engine._save()
        sim.step()
        for _ in range(3):
            sim.engine._refresh_readiness()
        # An oversized contract must not start a model.
        self.assertEqual(model.calls, [])
        failures = [row for row in sim.runtime.get("input_overflows", []) if row["action"]["role"] == "task_contract_review"]
        self.assertEqual(len(failures), 1)
        attempts = [e for e in sim.runtime['executions'].values()
                    if e['role'] == 'task_contract_review' and e['action'].get('target') == task['id']
                    and e.get('input_preparation', {}).get('reason') == 'input overflow']
        self.assertEqual(len(attempts), 1)
        self.assertFalse(attempts[0].get('started_at'))
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == task['id']
                             for a in sim.runtime['queue']))

    def test_large_accepted_report_survives_revision_review_and_resumed_work(self):
        from support.engine_context import assert_result_documents, assert_result_damage_rejected
        sim = ready_work_sim(1, **NO_REPAIR)
        model = submission_model(sim)
        work_calls, resumed = [], []

        def work(context, workspace):
            work_calls.append(context["task"]["revision"])
            if len(work_calls) == 1:
                (Path(workspace) / "evidence.txt").write_bytes(b"preserved partial evidence")
                return
            prior_task = next(t for t in context['tasks'] if t['id'] == context['task']['id'])
            assert_result_documents(self, prior_task['results'], workspace, sim.engine,
                                    owner='results', task_id=prior_task['id'], snapshot=context['snapshot'])
            assert_result_documents(self, prior_task['results'][0]['output_files'], workspace, sim.engine,
                                    owner='materialized_output_files', task_id=prior_task['id'], snapshot=context['snapshot'])
            assert_result_damage_rejected(self, prior_task['results'], workspace, sim.engine,
                task_id=prior_task['id'], borrowed_path='input/sources/0000-unrelated.txt')
            previous = next(f for prior_task in context['tasks'] if prior_task['id'] == context['task']['id']
                            for result in prior_task['results']
                            for f in result.get('output_files', []) if f['path'] == 'evidence.txt')
            resumed.append((context["task"]["results"][0]["report"] == "p" * 600000,
                            (Path(workspace) / previous["local_path"]).read_bytes()))
        model.before("research_work", work)
        model.on("research_work").reply(submitted(returned(
            "research_work", outcome="partial", report="p" * 600000, remaining_work=["Resolve the remaining case."]))
        ).reply(submitted(returned("research_work")))

        def plan(ctx):
            return [{"task_id": task["id"], "decision": "incomplete", "reason": "The remaining case is explicit.",
                     "item_dispositions": [{"obligation_id": obligation["id"], "kind": "open", "evidence_refs": []}
                                           for obligation in task["completion_obligations"]],
                     "unresolved": []}
                    for task in ctx["tasks"] if task['id'] in ctx.get('returned_task_ids', [])]
        model.on("research_plan").reply(submitted(
            lambda ctx: returned("research_plan", task_assessments=plan(ctx),
                dispositions=[{**disposition(tid), "uncertainty": ""} for tid in ctx["ready_task_ids"]],
                goal_audit=False, preparation_requests=[]),
            extensions=lambda ctx: {"model_assessments": [
                {"task_id": tid, "difficulty": "high", "importance": "medium",
                 "reason": "Continue the explicit unresolved fixture case."} for tid in ctx["ready_task_ids"]],
                "revision_requests": [{"record_ids": [row["task_id"]], "reason": "Revise the explicit unfinished case."}
                    for row in plan(ctx) if next(t for t in ctx['tasks'] if t['id'] == row['task_id'])['revision'] == 1]}))

        def proposal(ctx):
            task = ctx["tasks"][0]
            return candidate(task['title'], formal=False, revises=task['id'])

        def preparation_extensions(ctx):
            task = ctx["tasks"][0]
            extensions = {"model_assessments": [
                {"task_title": task["title"], "difficulty": "high", "importance": "medium",
                 "reason": "The revised fixture retains the unresolved case."}],
                "contract_checks": contract_checks([task]),
                "revision_resolutions": [{"record_id": task["id"], "disposition": "revised",
                                          "reason": "The remaining case is the new contract."}]}
            supply_observation_rules([proposal(ctx)], extensions)
            return extensions
        model.on("research_preparation").reply(submitted(
            lambda ctx: returned("research_preparation", candidates=[proposal(ctx)]), extensions=preparation_extensions))
        model.on("task_contract_review").reply(submitted(lambda ctx: returned("task_contract_review", **contract_review(ctx))))
        for _ in range(12):
            sim.step()
            if len(work_calls) == 2:
                break
        roles = [call["role"] for call in model.calls]
        self.assertEqual(len(work_calls), 2, {
            'executions': [{k: e.get(k) for k in ('role', 'outcome', 'error', 'integration_result')}
                           for e in sim.runtime['executions'].values()],
            'waiting': sim.runtime.get('waiting_actions'), 'queue': sim.runtime['queue'], 'roles': [c['role'] for c in model.calls]})
        self.assertEqual(set(roles) - {"research_work", "research_plan", "research_preparation", "task_contract_review"},
                         set(), "unexpected role")
        self.assertGreater(work_calls[1], work_calls[0])
        self.assertIn("task_contract_review", roles)
        # The resumed work read the accepted 600 000-character report and the partial evidence file.
        self.assertEqual(resumed, [(True, b"preserved partial evidence")])
        self.assertFalse(sim.runtime.get("input_overflows"))
        worker_results = [e["outcome"] for e in sim.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertEqual(worker_results, ["output_accepted", "output_accepted"], [
            {k: e.get(k) for k in ('outcome', 'error', 'error_kind', 'integration_result')}
            for e in sim.runtime['executions'].values() if e['role'] == 'research_work'])


if __name__ == "__main__":
    unittest.main()
