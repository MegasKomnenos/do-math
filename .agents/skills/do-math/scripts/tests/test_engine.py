"""The research engine's own operations: initialization and activation, queueing, dispatch, publication and installation checks."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from do_math import activities, execution_profiles, submission_tool
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import control, initialize, ResearchEngine
from do_math.canonical import canonical_json
from do_math.repository import ResearchRepository
from engine_fixtures import initialized, routing_engine
from research_fixtures import (activate, candidate, charter_change, current_state, FixtureAdapter, git_init,
                               governance_start, install_adapter_fixture, restore_template, send_control)
from runner_fixtures import context_from, formal_ok, ScriptedRunner


def formal_fail(**_): return {"status": "failed", "reason": "mock formal failure; not Lean sorry evidence"}


class EngineTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.repo = git_init(self.root / "repo")

    def tearDown(self): self.temp.cleanup()

    def make(self, runner, verifier=formal_ok, **config):
        config.setdefault('plan_settle_seconds', 1)
        init = initialize(self.repo, goal="goal", workspace=self.root / "work", config={"reviewers": 2, "goal_auditors": 2,  "lean_command": ["test-lean"], "scholarly_enabled": False, "operator_enabled": False, **config})
        engine = ResearchEngine(self.repo, init["instance_id"], runner=runner, formal_verifier=verifier)
        activate(engine, self.root, initialization_runner=ScriptedRunner())
        return engine, init["instance_id"]

    def active(self, runner, verifier=formal_ok, **config):
        """Start from a copy of validated active state; only the public-initialization test needs make().

        The copy replaces the previous one (``research_fixtures.restore_template``),
        so finish with an earlier engine before asking for the next.
        """
        from state_fixtures import ACTIVE_LEAN_COMMAND, active_instance
        config = {"reviewers": 2, "goal_auditors": 2, "lean_command": list(ACTIVE_LEAN_COMMAND),
                  "scholarly_enabled": False, "operator_enabled": False, "plan_settle_seconds": 1, **config}
        self.root, instance_id = restore_template(active_instance, config=config)
        self.repo = self.root / "repository"
        return ResearchEngine(self.repo, instance_id, runner=runner, formal_verifier=verifier), instance_id

    def test_initialization_reports_missing_values_without_model_dispatch(self):
        init = initialize(self.repo, goal="Explicit initial input", workspace=self.root / "work",
                          config={"scholarly_enabled": False, "operator_enabled": False})
        runner = ScriptedRunner()
        engine = ResearchEngine(self.repo, init["instance_id"], runner=runner)
        engine.run(max_steps=1)
        self.assertEqual(engine.instance["lifecycle"]["state"], "initializing")
        missing = engine.instance["lifecycle"]["activation"]["missing"]
        self.assertTrue({"governance", "configuration", "independent_intent", "trust_environment",
                         "research_authority"} <= set(missing))
        self.assertEqual(runner.prompts, [])
        self.assertEqual(engine.instance["grants"], {})
        _, stored_instance, stored_runtime = engine.store.load()
        self.assertEqual(stored_instance["lifecycle"]["activation"]["missing"], missing)
        self.assertEqual(stored_runtime["availability"], {
            "state": "blocked", "reason": "initialization_incomplete", "next_owner": "user"})

    def test_public_initialization_reaches_active_with_distinct_interpretation(self):
        engine, _ = self.make(ScriptedRunner())
        self.assertEqual(engine.instance["lifecycle"]["state"], "active")
        check = engine.instance["lifecycle"]["intent_check"]
        self.assertNotEqual(check["interpretation_execution_id"], check["check_execution_id"])
        self.assertTrue(engine.instance["capability_evidence"])
        self.assertEqual(engine.instance["lifecycle"]["activation"]["missing"], [])

    def test_nonformal_mathematical_goal_is_not_solved(self):
        engine, _ = self.active(ScriptedRunner())
        # The decisive point is the required goal audits' judgment of the
        # nonformal result; later steps only repeat preparation and that judgment.
        for _ in range(20):
            status = engine.run(max_steps=1)
            audits = [e for e in engine.runtime["executions"].values()
                      if e["role"] == "goal_audit" and e["status"] == "ended"]
            if len(audits) >= engine.instance["config"]["goal_auditors"]:
                break
        self.assertTrue(audits, engine.runtime["history"][-3:])
        self.assertTrue(any(task.get("results") for task in engine.runtime["tasks"].values()),
                        engine.runtime["history"][-3:])
        self.assertNotEqual(status["goal_status"], "mathematically_solved")
        self.assertEqual(status["knowledge"]["K"], 0)

    def test_formal_requires_two_blind_reviews_and_failure_does_not_create_k(self):
        runner = ScriptedRunner(formal=True); engine, _ = self.active(runner)
        for step in range(0, 30, 4):
            solved = engine.run(max_steps=min(4, 30 - step))
            if solved['knowledge']['K'] == 1:
                break
        else:
            self.fail('The fixture did not publish formally reviewed knowledge: ' + json.dumps({
                'snapshot':engine.head, 'status':engine.runtime['status'],
                'queue':engine.runtime['queue'], 'waiting':engine.runtime.get('waiting_actions',{}),
                'executions':[{key:value.get(key) for key in ('id','role','status','outcome','error','result_ref')}
                              for value in engine.runtime['executions'].values()]},ensure_ascii=False))
        from do_math.knowledge_records import usable_links
        self.assertEqual(solved["knowledge"]["K"], 1)
        kid = next(kid for kid in engine.instance['knowledge'] if usable_links(engine.instance, kid))
        assessment_id = usable_links(engine.instance, kid)[0]['assessment_id']
        cycle_id = engine.instance['identity_assessments'][assessment_id]['review_cycle_id']
        reviews = [prompt for role, prompt in runner.prompts if role == "identity_review"
                   and context_from(prompt)["action"]["stage"] == "initial"
                   and context_from(prompt)['action']['target'] == kid
                   and context_from(prompt)['action']['review_cycle_id'] == cycle_id
                   and engine.runtime['executions'][context_from(prompt)['execution_id']]['outcome'] == 'output_accepted']
        self.assertEqual(len(reviews), 2, [(context_from(p)['action'],
            engine.runtime['executions'][context_from(p)['execution_id']].get('outcome'))
            for role, p in runner.prompts if role == 'identity_review'])
        self.assertEqual(len({context_from(p)['action']['slot'] for p in reviews}), 2)
        self.assertEqual(len({context_from(p)['action']['review_cycle_id'] for p in reviews}), 1)
        self.assertTrue(all('"reviews"' not in prompt for prompt in reviews))
        verified = engine.instance['knowledge'][kid]
        self.assertEqual(engine.instance["trust_environments"][engine.instance["formal_results"][verified["formal_result_id"]]["trust_environment_id"]]["status"], "active")
        self.assertEqual(engine.instance["active_trust_environment"], engine.instance["formal_results"][verified["formal_result_id"]]["trust_environment_id"])
        self.assertEqual(engine.instance["formal_results"][verified["formal_result_id"]]["verification"]["toolchain"],
                         engine.instance['trust_environments'][engine.instance['active_trust_environment']]['toolchain'])
        failed_runner = ScriptedRunner(formal=True); failed, _ = self.active(failed_runner, formal_fail)
        for _ in range(0, 20, 4):
            failed_status = failed.run(max_steps=4)
            if any(ex['role'] == 'formal_check' and ex.get('status') == 'ended'
                   and ex.get('formal_status') == 'failed' for ex in failed.runtime['executions'].values()):
                break
        else:
            self.fail('The fixture did not reach a failed formal check')
        self.assertEqual(failed_status["knowledge"]["K"], 0)

    def test_plan_rejects_missing_candidate_and_criterion(self):
        for invalid in ("missing", "criterion"):
            # Output repair is covered elsewhere; the first rejection is the rule here.
            engine, _ = self.active(ScriptedRunner(invalid_plan=invalid), max_output_repairs=0)
            for _ in range(20):
                state = engine.run(max_steps=1)
                failed = [w for w in state['waiting_actions'].values() if w['role'] == 'research_plan'
                          and w['kind'] in {'output_validation', 'execution_failure'}]
                if failed:
                    break
            else:
                self.fail('The invalid plan never reached its preserved failure wait')
            self.assertNotEqual(state['status'], 'completed')
            self.assertTrue(all(engine.runtime['executions'][w['execution_id']]['status'] == 'ended' for w in failed))
            self.assertTrue(any(('derived-ready' if invalid == 'missing' else 'obligation') in w['reason']
                                for w in failed), failed)


    def test_crash_recovery_and_artifact_immutability(self):
        engine, instance = self.active(ScriptedRunner())
        engine._enqueue('research_preparation', reason='The first AI action of an active instance')
        action = engine.runtime['queue'][0]
        crashed = engine._register_execution(action, {'id': 'EX-crash', 'role': action['role'],
            'status': 'queued', 'input_snapshot': engine.head, 'input_manifest': []})
        profile=engine._execution_profile(action)
        self.assertTrue(engine._provider_admit(action,crashed['id'],profile=profile,execution=crashed))
        from do_math.windows_job import WindowsJob, process_identity
        # A separate exited process supplies a real dead owner. The unittest
        # process remains alive and must never count as a crashed launch owner.
        owner_program=('import json,sys; sys.path.insert(0,sys.argv[1]); '
            'from do_math.windows_job import owner_identity; print(json.dumps(owner_identity()))')
        crashed['launch_ticket']['owner']=json.loads(subprocess.check_output(
            [sys.executable,'-c',owner_program,str(SCRIPTS)]))
        crashed['launch_ticket']['phase']='dispatched'
        job = WindowsJob([sys.executable, '-c', 'pass'], cwd=self.root,
                         name=crashed['launch_ticket']['job_name'])
        self.addCleanup(job.close)
        from do_math.system_clock import now
        engine._session_slots().started(crashed['id'],{**process_identity(job), 'job_name': job.name},at=now())
        job.resume()
        from types import SimpleNamespace
        from do_math.codex_adapter import CodexExecAdapter
        # Root signal alone can precede the Job's active-count update.
        # Use the real collector barrier with the original ten-second limit.
        self.assertTrue(CodexExecAdapter('fixture-cli').wait_for_termination(SimpleNamespace(job=job), 10))
        self.assertEqual(job.inspect().active_processes, 0)
        engine._save()
        ResearchEngine(self.repo, instance, runner=ScriptedRunner()).run(max_steps=1)
        _, _, runtime = ResearchRepository(self.repo, instance).load()
        self.assertEqual(runtime['executions']['EX-crash']['outcome'], 'execution_incomplete')
        owner = runtime['activities'][crashed['owner_activity_id']]
        self.assertIn('EX-crash', owner['assigned_execution_ids'])
        self.assertTrue(runtime['recoveries'])
        self.assertTrue(owner.get('waiting') or owner['unresolved'])
        store = ResearchRepository(self.repo, instance)
        head, instance_data, runtime_data = store.load()
        recovered = runtime_data['executions']['EX-crash']
        self.assertTrue(store.read(recovered['result_ref'], head))
        bundle = recovered['artifact_bundle']
        with self.assertRaises(ValueError):
            store.save_with_state(head, instance_data, runtime_data,
                       artifacts={f"runtime/artifacts/{bundle}/other.txt": b"mutate"})[0]


class QueryIdentity(unittest.TestCase):
    def test_exact_evidence_binds_persisted_bytes_and_code_points(self):
        from do_math.engine import _record_evidence
        from do_math.canonical import exact_content_hash
        record = {"id": "FR-one", "title": "e\u0301", "verification": {"K": "e\u0301", "K": "é"}}
        def evidence(value):
            raw = canonical_json({"record": value})
            row = {"snapshot": "snapshot", "path": "research/formal_results/FR-one.json", "record": value,
                "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "json_pointer": "/record"}
            return _record_evidence(row)
        first = evidence(record)
        self.assertEqual(first["json_pointer"], "/record")
        self.assertEqual(first["sha256"], hashlib.sha256(canonical_json({"record": record})).hexdigest())
        self.assertEqual(first["logical_sha256"], exact_content_hash(record))
        same_metadata = {**record, "title": "é"}
        self.assertNotEqual(first["logical_sha256"], evidence(same_metadata)["logical_sha256"])
        changed_payload = {**record, "verification": {"K": "é", "K": "é"}}
        self.assertNotEqual(first["logical_sha256"], evidence(changed_payload)["logical_sha256"])

    def test_duplicate_id_is_rejected_across_families(self):
        # The state contract checks global record IDs of every bundle candidate
        # (_validate_bundle_candidate -> validate_candidate) before publication.
        from do_math.state_contract import default_state_contract
        instance, runtime = current_state(
            {"object_format": "sha1", "sources": [{"id": "DUP", "path": "input.txt", "sha256": "a" * 64}]},
            {"events": [{"id": "DUP", "kind": "created"}]})
        with self.assertRaisesRegex(ValueError, "record IDs must be globally unique: DUP"):
            default_state_contract().validate(instance, runtime)


class ObservationMerge(unittest.TestCase):
    def test_merged_review_keeps_all_obligations_and_evidence_refs(self):
        engine = routing_engine()
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


class PublicGitFlow(unittest.TestCase):
    def test_public_activation_work_receipt_assessment_and_next_plan(self):
        from research_fixtures import activate, install_adapter_fixture, candidate, contract_review, intent_response, assessment, seal_response, local_job_runner
        from do_math import submission, task_contracts
        from do_math.control_transport import ControlTransport
        install_adapter_fixture(self)
        class Runner:
            def __init__(self): self.roles = []
            @local_job_runner
            def run(runner, **arguments):
                try:
                    return runner.execute(**arguments)
                except Exception:
                    import traceback
                    traceback.print_exc(file=sys.stdout)
                    raise
            def execute(runner, **arguments):
                workspace = arguments["workspace"]
                context = json.loads((workspace / "input/submission/context.json").read_bytes())
                role = context["action"]["role"]; runner.roles.append(role)
                arguments["on_started"]()
                output = {"summary": role, "used_sources": [], "questions": []}
                if role == "intent_interpretation":
                    output = intent_response(context)
                elif role == "research_preparation":
                    row = candidate("bounded observation")
                    row["profile_refs"] = [execution_profiles.profile_ref(p) for p in context["execution_profiles"] if p["role"] == "research_work"]
                    row["authority_refs"] = ["GR-research-fixture"]
                    output["candidates"] = [row] if not context["tasks"] else []
                    if "observed_at" in arguments["output_schema"]["properties"]:
                        output["observed_at"] = context["observed_at"]
                    if output["candidates"]:
                        rules = [{"id": "rule-attempt", "operator": "counter_gte", "subject": {"kind": "counter", "id": "attempts"},
                            "basis": {"source": "checkpoint", "unit": "count"}, "threshold": 10, "required_evidence": ["checkpoint.json"]}]
                        from runner_fixtures import contract_checks
                        (workspace / "activity-extensions.json").write_bytes(canonical_json({
                            "contract_checks": contract_checks(output["candidates"]),
                            "task_conditions": [{"task_title": row["title"], "occurrence_condition": {"op": "always"},
                                "dependencies": [], "knowledge_revision_targets": [], "observation_rules": rules}],
                            "model_assessments": [{"task_title": row["title"], "difficulty": "low",
                                "importance": "low", "reason": "Bounded synthetic task"}],
                        }))
                elif role == "task_contract_review":
                    output.update(contract_review(context))
                elif role == "research_plan":
                    tasks = {t["id"]: t for t in context["tasks"]}
                    output.update(dispositions=[{"task_id": tid, "kind": "selected", "reason": "Perform approved bounded work",
                        "uncertainty": "Outcome is unconfirmed before execution", "parallel_task_ids": [],
                        "expected_research_change": "Preserve an explicit observation", "revisit": {"at": None, "event_refs": []},
                        "missing_inputs": [], "next_owner": "research_work"} for tid in context["ready_task_ids"]],
                        task_assessments=[assessment(tasks[tid]) for tid in task_contracts.returned_task_ids(tasks)],
                        preparation_requests=[], goal_audit=False)
                    from research_fixtures import planning_model_assessments
                    (workspace / "activity-extensions.json").write_bytes(canonical_json({
                        "model_assessments": planning_model_assessments(output, context)}))
                elif role == "research_work":
                    output.update(outcome="submitted", report="The observation is bounded to this synthetic execution and its stated domain.",
                        checkpoint="Observation preserved", remaining_work=[], relations=[], knowledge=[{
                            "kind": "observation", "title": "Bounded observation", "statement": "The synthetic runner returned an observation.",
                            "explanation": "Evidence is this explicit synthetic execution", "summary": "A bounded observation",
                            "lean_code": "", "declaration_names": [], "dependencies": []}])
                else:
                    raise AssertionError("Unexpected role in minimum actual Git flow: " + role)
                seal_response(output, context, workspace)
                draft = workspace / "draft.json"; draft.write_bytes(canonical_json(output))
                self.assertEqual(context["control_binding"], arguments["control_binding"])
                # Only research work answers self checks, so only its binding offers the tool.
                self.assertEqual(context["control_binding"].get("self_check", False), role == "research_work")
                # Queue through the real transport; the owner loop receives it on its
                # next pass and the worker waits for the durable receipt.
                delivery = submission_tool.request_control(workspace, "draft.json", kind="submit_intent", wait_seconds=0)
                self.assertIn(delivery["state"], {"submitted", "already_received"}, delivery)
                receipt = ControlTransport.wait_receipt(arguments["control_binding"], delivery["request_id"], 60)
                self.assertEqual(receipt["state"], "accepted", receipt)
                return {"status": "completed", "output": output, "usage": {}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            identifier = initialized(root / "repo", goal="Record and assess a bounded observation", workspace=root / "work", config={
                 "scholarly_enabled": False, "operator_enabled": False, "lean_command": ["fixture-lean"],
                "observation_mode": "periodic", "tool_review_window_seconds": 600, "self_check_response_window_seconds": 60,
                "import_rework_limit": 3, "selection_failure_limit": 3, "exhaustion_empty_limit": 3,
                "proposal_version_limit": 3, "contract_revision_limit": 3})
            runner = Runner(); engine = ResearchEngine(root / "repo", identifier, runner=runner)
            run = engine.run
            def checked_run(**kwargs):
                result = run(**kwargs)
                failures = [{key: execution.get(key) for key in ("id", "role", "outcome", "error")}
                    for execution in engine.runtime["executions"].values()
                    if execution["status"] == "ended" and execution.get("outcome") != "output_accepted"]
                self.assertEqual(failures, [], {"failures": failures, "repair_issues": [
                    action.get("repair", {}).get("issues", []) for action in engine.runtime["queue"]]})
                return result
            engine.run = checked_run
            activate(engine, root, initialization_runner=runner)
            self.assertEqual(engine.instance["lifecycle"]["state"], "active")
            for _ in range(15):
                engine.run(max_steps=1)
                if any(t.get("status") == "completed" for t in engine.runtime["tasks"].values()): break
            else: self.fail("Public flow did not assess returned work: " + repr(engine.runtime["history"][-5:]))
            task = next(t for t in engine.runtime["tasks"].values() if t["status"] == "completed")
            self.assertEqual(task["assessment"]["item_dispositions"][0]["kind"], "fulfilled")
            self.assertTrue(engine.instance["knowledge"])
            self.assertGreaterEqual(runner.roles.count("research_plan"), 2)
            self.assertEqual(runner.roles.count("research_work"), 1)
            _, instance, runtime = engine.store.load()
            self.assertEqual(runtime["tasks"][task["id"]]["status"], "completed")
            self.assertTrue(runtime["integrations"])


class MaintenanceConnections(unittest.TestCase):
    def test_maintenance_archives_complete_run_before_approved_cleanup(self):
        from do_math import execution_lifecycle, governance
        from do_math.repository import ResearchRepository
        from do_math.system_clock import new_id
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_init(root / "repo")
            engine = routing_engine(); identifier = new_id("RI")
            engine.instance, engine.runtime = current_state(
                governance_start({"id": identifier, "workspace": str(root / "work"), **execution_profiles.build_profiles(DEFAULT_CONFIG)}),
                {"executions": {}, "activities": {}, "tasks": {}, "history": [], "queue": []})
            engine.instance["governance_sources"] = {"SOURCE-cleanup": governance.preserve_source(
                "SOURCE-cleanup", "Authorize local maintenance and cleanup of the requested ended run.", origin="user")}
            engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
                {"kind": "grant", "decision_id": "DEC-cleanup", "grant": {"id": "GR-cleanup", "kind": "local",
                    "roles": ["maintenance"], "reuse": "reusable"}}, source_ref="SOURCE-cleanup")
            action = {"id": "AC-cleanup", "role": "maintenance", "actor_kind": "ai",
                      "grant_id": "GR-cleanup", "requested_by": "UC-cleanup", "cleanup_execution_ids": ["EX-finished"]}
            engine.runtime["history"].append({"kind": "user_control", "request": {"id": "UC-cleanup", "origin": "user",
                "action": "request", "config": {"role": "maintenance", "cleanup_execution_ids": ["EX-finished"]}}})
            profile = next(p for p in engine.instance["execution_profiles"].values() if p["role"] == "maintenance")
            for eid in ("EX-finished", "EX-maintenance"):
                aid = "AY-" + eid
                activities.open_activity(engine.runtime, activity_id=aid, activity_kind="maintenance", owner_ref="GR-cleanup", input_refs=[], opened_at="2026-09-20T00:00:00Z")
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid, actor_kind="ai",
                    input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at="2026-09-20T00:00:00Z")
                execution.update(role="maintenance", action=deepcopy(action), grant_id="GR-cleanup")
                activities.assign_execution(engine.runtime, aid, execution)
                execution_lifecycle.transition_execution(execution, "ended", at="2026-09-20T00:00:01Z", outcome="cancelled")
                # Explicit synthetic termination evidence; all scope, schemas, references and Git I/O are real.
                from do_math.launch import ticket
                execution["launch_ticket"] = {**ticket(eid, profile), "phase":"not_started"}
                execution["capacity"] = {"local_termination": "confirmed"}
                activities.finish_activity(engine.runtime, aid, result_refs=[], unresolved=[], followups=[], at="2026-09-20T00:00:01Z")
            engine.store = ResearchRepository(root / "repo", identifier)
            engine.head = engine.store.initialize(engine.instance, engine.runtime)
            run = root / "work/runs/EX-finished"
            (run / "workspace").mkdir(parents=True); (run / "evidence").mkdir()
            (run / "workspace/draft.txt").write_bytes(b"draft retained")
            (run / "evidence/runner.json").write_bytes(b'{"local_job_empty":true}')
            with engine.store.writer_lock():
                before = engine.head
                with self.assertRaisesRegex(ValueError, "exact user-approved"):
                    engine._maintenance_cleanup({**action, "cleanup_execution_ids": ["EX-maintenance"]}, "EX-maintenance")
                self.assertEqual(engine.head, before)
                self.assertTrue(run.exists())
                result = engine._maintenance_cleanup(action, "EX-maintenance")
            self.assertEqual(result["deleted"], ["runs/EX-finished"],
                {"result": result, "candidates": engine.runtime["history"][-1]["candidates"]})
            self.assertFalse(run.exists())
            manifest = engine.runtime["executions"]["EX-finished"]["collection"]["retention_manifest"]
            self.assertEqual(len(manifest), 2)
            for row in manifest:
                raw = engine.store.read(row["artifact_ref"], row["snapshot"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])


class SourceIntegrityCheckTests(unittest.TestCase):
    def test_current_corrupt_source_is_found_by_the_explicit_full_byte_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.txt"; source.write_text("preserved original", encoding="utf-8")
            identifier = initialized(root / "repo", goal="Read the preserved source", workspace=root / "work", sources=[source])
            store = ResearchRepository(root / "repo", identifier)
            head, instance, runtime = store.load()
            raw_store = store._store
            # Deliberate corruption fixture: only bypass the writer's immutable-artifact
            # guard while injecting damage. The tested read and recovery gates are real.
            with patch.object(raw_store, "_validate_artifact_changes", return_value=None):
                damaged = raw_store.publish(head, {instance["sources"][0]["path"]: b"corrupt bytes"}).head
            # run and controls check artifact presence and length only; full bytes belong to check.
            report = ResearchEngine(root / "repo", identifier).check(requested_areas=["record_storage"])
            self.assertFalse(report["passed"])
            self.assertTrue(any(instance["sources"][0]["path"] in row["evidence"]
                                for row in report["inspection"]["findings"]), report["inspection"]["findings"])
            self.assertEqual(raw_store.read_snapshot().head, damaged)


def efficiency_instance(root, shared, *, config, charter):
    """``restore_template`` build: the synthetic active state with one queued, published preparation.

    These tests start after activation. They keep real state publication and
    the preparation request they exercise, without replaying input approval.
    ``charter`` also approves academic requirement ``explain`` through a public
    charter control, which opens a plan for the charter event.
    """
    from state_fixtures import active_instance
    instance_id = active_instance(root, shared, config=config)
    engine = ResearchEngine(root / "repository", instance_id)
    (root / "work-0" / "runs").mkdir(exist_ok=True)
    engine._enqueue("research_preparation", reason="Prepare the bounded efficiency fixture")
    engine._save()
    if charter:
        send_control(engine, "decision", config={"change":
            charter_change(engine, academic_requirements=[
                {"id": "explain", "scope": "solution", "criteria": ["explain structure"],
                 "assessor": "research_plan"}])})
    return instance_id


EFFICIENCY_CONFIG = {"operator_enabled": False, "scholarly_enabled": False, "lean_command": ["test-lean"],
                     "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}


class QueuedPreparationTests(unittest.TestCase):
    """An engine over the synthetic active state with one queued, published preparation (``efficiency_instance``)."""

    @contextmanager
    def model_process(self, arguments, *, resume):
        from do_math.windows_job import WindowsJob, process_identity
        job = WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'],
                         cwd=arguments['workspace'], name=arguments['launch_ticket']['job_name'])
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            if resume:
                job.resume()
            yield
        finally:
            try:
                job.terminate()
                self.assertTrue(job.wait(10))
                self.assertEqual(job.inspect().active_processes, 0)
            finally:
                job.close()

    def setUp(self):
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()))
        self.open(charter=False)

    def open(self, *, charter):
        """Make ``self.engine`` a new engine, with a new ``ScriptedRunner``, on a copy of ``efficiency_instance``."""
        self.root, instance_id = restore_template(efficiency_instance, config=EFFICIENCY_CONFIG, charter=charter)
        self.workspace = self.root / "work-0"
        self.engine = ResearchEngine(self.root / "repository", instance_id, runner=ScriptedRunner())

    def startup(self):
        self.open(charter=True)
        e = self.engine
        e._refresh_readiness()
        return next(a for a in e.runtime["queue"] if a["role"] == "research_plan")

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
        self.startup()
        e = self.engine
        e.runner = ScriptedRunner()
        e._save()
        e.run(max_steps=3)
        plans = [context_from(prompt) for role, prompt in e.runner.prompts if role == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]['ready_task_ids'], [])
        self.assertCountEqual([role for role, _ in e.runner.prompts],
                         ['research_preparation', 'task_contract_review', 'research_plan'])
        event = next(row for row in reversed(e.runtime['events']) if row['kind'] == 'user_decision_applied')
        self.assertTrue(any(row.get('kind') == 'event_consumption' and event['id'] in row['event_ids']
                            for row in e.runtime['history']))
        self.assertNotIn(event['id'], e.runtime['pending_events'])

    def test_regular_empty_plan_can_still_dispatch(self):
        self.assertTrue(self.engine._dispatchable({"role": "research_plan", "reason": "assess failed approach"}))

    def test_pause_received_during_input_preparation_prevents_model_start(self):
        e = self.engine
        before_executions = set(e.runtime["executions"])
        before_calls = len(e.runner.prompts)
        before_runs = set((self.workspace / "runs").iterdir())
        original = e._context
        def prepare(action, workspace, **kwargs):
            context = original(action, workspace, **kwargs)
            control(e.store.repository, e.instance["id"], "pause", text="stop during materialization")
            return context
        # Preparation applies user controls only; periodic upkeep waits for the owner loop.
        with patch.object(e, '_context', side_effect=prepare), \
                patch.object(e, '_upkeep', side_effect=AssertionError('input preparation ran the upkeep')):
            generator = e._call_steps(e.runtime["queue"][0])
            with self.assertRaises(StopIteration):
                next(generator)
        self.assertEqual(e.runtime["status"], "paused")
        self.assertEqual(len(e.runner.prompts), before_calls)
        added = set(e.runtime['executions']) - before_executions
        self.assertEqual(len(added), 1)
        execution = e.runtime['executions'][added.pop()]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'cancelled'))
        self.assertIsNone(execution.get('started_at'))
        self.assertNotIn('capacity', execution)
        self.assertEqual(set((self.workspace / "runs").iterdir()), before_runs)

    def test_pause_before_model_resume_has_no_checkpoint_grace(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        try:
            with self.model_process(arguments, resume=False):
                control(e.store.repository, e.instance['id'], 'pause', text='stop before model resume')
                e._apply_inbox(pump=False)  # The owner pass applies and publishes the control.
                e._upkeep()
                self.assertTrue(arguments['should_stop'](), 'a suspended model must not resume for checkpoint grace')
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'stopped before resume'})

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
            with self.model_process(arguments, resume=True):
                self.assertFalse(arguments['should_stop']())
                control(e.store.repository, e.instance['id'], 'pause', text='stop running work')
                e._apply_inbox(pump=False)  # The owner pass applies and publishes the control.
                e._upkeep()
                self.assertTrue(arguments['should_stop']())
                execution = e.runtime['executions'][arguments['execution_id']]
                self.assertEqual(execution['status'], 'stopping')
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'local stop requested'})

    def test_installation_polling_is_bounded_and_forced_checks_still_detect_edits(self):
        e = self.engine
        self.assertTrue(callable(getattr(e, '_check_installation', None)), 'bounded installation checks required')
        with patch.object(e, '_installation_manifest', return_value=e._installation) as probe:
            for _ in range(10):
                self.assertTrue(e._check_installation())
            self.assertLessEqual(probe.call_count, 1)
        with patch.object(e, '_installation_manifest', return_value={"sha256": "changed"}):
            self.assertFalse(e._check_installation(force=True))
        self.assertEqual(e.runtime["status"], "paused")

    def test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check(self):
        from do_math import engine as engine_module
        repository = self.engine.store.repository
        source = self.root / 'note.txt'
        source.write_bytes(b'archived source bytes')
        control(repository, self.engine.instance['id'], 'source', config={'path': str(source)})
        self.engine.process_controls()
        self.assertTrue(self.engine.instance['sources'])
        with patch.object(ResearchEngine, '_installation_manifest', side_effect=AssertionError('run hashes the installation')), \
                patch.object(engine_module, 'all_prompt_documents', side_effect=AssertionError('a prompt loads documents')):
            engine = ResearchEngine(repository, self.engine.instance['id'])
            with patch.object(engine.store, 'read', side_effect=AssertionError('status reads no artifact bytes')), \
                    patch.object(engine.store, 'read_many', side_effect=AssertionError('status reads no artifact bytes')):
                status = engine.status()
        self.assertEqual(status['submission_checks']['status'], 'not_evaluated')
        storage = next(area for area in status['inspection']['areas'] if area['name'] == 'record_storage')
        self.assertIn('artifact presence and length', storage['checked_invariants'])

    def test_installation_change_cannot_reopen_a_terminal_instance(self):
        e = self.engine
        e._installation  # run hashes the loaded edition before any periodic check
        for terminal in ('closed', 'completed'):
            with self.subTest(terminal=terminal):
                e.runtime['status'] = terminal
                with patch.object(e, '_installation_manifest', return_value={'sha256': 'changed'}):
                    self.assertFalse(e._check_installation(force=True))
                self.assertEqual(e.runtime['status'], terminal)

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
        e = self.engine
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "running", "input_snapshot": e.head, "goal_revision": 1, "policy_revision": 1,
            "action": {"id": "A", "role": "research_preparation", "reason": "derive last-car recurrence",
                       "repair": {"previous_output": {"secret": "private draft"}}}}
        from do_math.context_store import prepare_role_input
        context = e._context({"role": "research_plan"}, self.root / "plan")
        profile = next(p for p in e.instance["execution_profiles"].values() if p["role"] == "research_plan")
        # Unfinished preparations reach the plan as ongoing_work rows built from state.
        fitted = prepare_role_input(context, instance=e.instance, runtime=e.runtime, role="research_plan",
            profile=profile, snapshot=e.head, workspace=self.root / "plan", activity_id="AC-plan")
        activities = [row for row in fitted["context"]["ongoing_work"] if row.get("execution_id") == "E"]
        self.assertEqual(len(activities), 1)
        self.assertEqual((activities[0]["goal_revision"], activities[0]["policy_revision"]), (1, 1))
        self.assertEqual(activities[0]["reason"], "derive last-car recurrence")
        self.assertEqual(activities[0]["input_snapshot"], e.head)
        self.assertNotIn("private draft", str(activities))

    def test_task_result_materialization_batches_reads_without_losing_files(self):
        e = self.engine
        files = {f'runtime/artifacts/results/{i}.bin': bytes(range(256)) + bytes([i]) for i in range(12)}
        entries = [{'artifact_ref': path, 'path': Path(path).name,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)} for path, raw in files.items()]
        e.runtime['tasks']['T'] = {**candidate('materialization'), 'id': 'T', 'revision': 1, 'status': 'active', 'reviews': [], 'results': [
            {'execution_id': 'E', 'output_files': entries}]}
        e.runtime['tasks']['T'].pop('revises_task_id')
        e._save(files)
        with patch.object(e.store._store._backend, '_run', wraps=e.store._store._backend._run) as calls:
            context = e._context({'role': 'research_plan'}, self.root / 'results-plan')
        reads = [c for c in calls.call_args_list if c.args[1] == 'cat-file']
        self.assertEqual(len(reads), 1)
        restored = context['tasks'][0]['results'][0]['output_files']
        self.assertEqual(len(restored), 12)
        for item in restored:
            self.assertEqual((self.root / 'results-plan' / item['local_path']).read_bytes(), files[item['artifact_ref']])

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
        e = self.engine
        e._save()
        head = e.head
        reopened = ResearchEngine(e.store.repository, e.instance['id'])
        reopened._save()
        self.assertEqual(reopened.head, head)

    def test_merged_user_requests_keep_all_request_references(self):
        e = self.engine
        e.runtime['queue'] = []
        e._enqueue('research_plan', reason='first instruction', requested_by='UC-first')
        e._enqueue('research_plan', reason='second instruction', requested_by='UC-second')
        self.assertEqual(e.runtime['queue'][0].get('requested_by_refs'), ['UC-first', 'UC-second'])

    def test_readiness_is_derived_and_changes_with_contract_review_evidence(self):
        e = self.engine
        e.runner = ScriptedRunner()
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


if __name__ == "__main__": unittest.main(verbosity=2)
