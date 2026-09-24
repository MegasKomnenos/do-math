from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from do_math.contracts import schema_for  # noqa: E402
from do_math.engine import ResearchEngine, control, initialize, validate_config  # noqa: E402
from do_math.repository import ResearchRepository  # noqa: E402
from v5_fixtures import local_job_runner, planning_model_assessments, supply_observation_rules, read_fixture_context
from v5_fixtures import (activate, install_adapter_fixture, candidate, contract_review, disposition,
                         assessment, intent_response, seal_response, submit_intent, bind_candidates)


def context_from(prompt: str, workspace=None) -> dict:
    if workspace is not None:
        return read_fixture_context(prompt, workspace)
    marker = "--- CANONICAL INPUT CONTEXT ---\n"
    return json.loads(prompt.split(marker, 1)[1].split("\n--- OUTPUT JSON SCHEMA ---", 1)[0])


def contract_checks(candidates: list[dict]) -> list[dict]:
    """The smallest self-check a fixture contract needs: no symbols, no cited sibling, two outcomes."""
    return [{"task_title": item["title"], "symbols": [], "sibling_boundaries": [], "outcome_branches": [
        {"outcome": "The fixture obligation is met", "completion": "Every criterion is judged from the report"},
        {"outcome": "The fixture obligation is not met", "completion": "The report records the unmet criterion"}]}
        for item in candidates]


def common(role: str) -> dict:
    """Neutral response fields only; judgments must come from the actual input."""
    base = {"summary": role, "used_sources": [], "questions": []}
    shapes = {
        "research_preparation": {"candidates": []},
        "research_plan": {"dispositions": [], "task_assessments": [], "preparation_requests": [], "goal_audit": False},
        "task_contract_review": {"item_reviews": []},
        "research_work": {"outcome": "no_result", "report": "", "knowledge": [], "relations": [], "remaining_work": [], "checkpoint": ""},
        "supplemental_research": {"outcome": "no_result", "report": "", "knowledge": [], "relations": [], "remaining_work": [], "checkpoint": ""},
        "maintenance": {"report": "", "remaining_work": []},
    }
    return {**base, **shapes.get(role, {})}


class ScriptedRunner:
    def __init__(self, *, formal: bool = False, invalid_plan: str | None = None, fail_role: str | None = None,
                 preparation_candidates=None, model_rating=None):
        self.formal, self.invalid_plan, self.fail_role = formal, invalid_plan, fail_role
        self.prompts: list[tuple[str, str]] = []
        self.preparation_candidates = preparation_candidates
        self.model_rating = model_rating or {"difficulty": "low", "importance": "medium", "reason": "Bounded explicit fixture argument"}

    @local_job_runner
    def run(self, *, prompt, output_schema, workspace, evidence_dir, model, effort, timeout_seconds,
            should_stop, on_started, control_binding=None, **kwargs):
        role = prompt.split("You are the do-math role: ", 1)[1].split(".", 1)[0]
        ctx = context_from(prompt, workspace)
        self.prompts.append((role, prompt))
        on_started()
        if role == self.fail_role:
            return {"status": "failed", "output": None, "usage": {}, "error": "interrupted"}
        out = common(role)
        if role == "intent_interpretation":
            out = intent_response(ctx)
        elif role == "research_preparation":
            from copy import deepcopy
            out["candidates"] = ([] if any(key in ctx['action'] for key in ('assessment_targets', 'observation_rule_targets')) else
                deepcopy(self.preparation_candidates) if self.preparation_candidates is not None else [candidate(formal=self.formal)])
        elif role == "task_contract_review":
            out.update(contract_review(ctx))
        elif role == "research_plan":
            from do_math.task_contracts import returned_task_ids
            tasks = {t["id"]: t for t in ctx["tasks"]}
            out.update(dispositions=[disposition(tid) for tid in ctx["ready_task_ids"]],
                task_assessments=[assessment(tasks[tid]) for tid in returned_task_ids(tasks)],
                goal_audit=bool(ctx["knowledge_catalog"]))
            if self.invalid_plan == "missing":
                out["dispositions"] = []
            if self.invalid_plan == "criterion":
                for row in out["task_assessments"]:
                    row["item_dispositions"] = []
        elif role == "research_work":
            out.update(outcome="submitted", report="The domain is Nat. Applying Nat.add_zero proves n + 0 = n.",
                checkpoint="Argument and domain recorded", knowledge=[{
                "kind": "theorem", "title": "T", "statement": "True", "explanation": "True holds by its constructor", "summary": "True holds",
                "lean_code": "theorem t : True := by trivial" if self.formal else "",
                "declaration_names": ["t"] if self.formal else [], "dependencies": []}])
        elif role == "identity_review":
            stage = ctx["action"]["stage"]
            if stage == "scope":
                from v5_fixtures import scope_response
                out.update(scope_response(ctx))
            else:
                review = ctx["role_review"]
                out["proposal_digest"] = review["proposal_digest"]
                out["used_sources"] = ["proposal"]
                if stage == "initial": out.update(decision="match", findings=[], scope_complete=True)
                elif stage == "organize": out["issues"] = []
                elif stage == "answer": out.update(answers=[], new_findings=[])
                elif stage == "judge": out.update(decision="match", scope_complete=True, issue_verdicts=[], new_findings=[])
        elif role == "goal_audit":
            eligible = ctx.get("eligible_knowledge", [])
            out.update(decision="satisfied" if eligible else "not_satisfied",
                used_sources=[k["id"] for k in eligible], reason="Use only the supplied eligible formal records",
                scope_complete=True, additional_audits=[])
        elif role == "operational_review":
            out["disposition"] = {"kind": "user_decision", "basis_refs": [ctx["action"]["target"]],
                "next_owner": "user", "reason": "The fixture scenario has stopped after a preserved failure",
                "question": "Should the synthetic scenario continue?", "effect": "Choose the fixture continuation"}
        if role == "research_preparation" and ctx.get("budget_unit") == "concurrent_sessions":
            key = "task_id" if ctx["action"].get("assessment_targets") else "task_title"
            ids = list(ctx["action"].get("assessment_targets", {})) if key == "task_id" else [c["title"] for c in out["candidates"]]
            extensions = {"model_assessments": [{key: ident, **self.model_rating} for ident in ids]}
            if out["candidates"]: extensions["contract_checks"] = contract_checks(out["candidates"])
            (workspace / "activity-extensions.json").write_text(json.dumps(extensions), encoding="utf-8")
        if role in {"research_preparation", "research_plan"}:
            path = workspace / "activity-extensions.json"
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            if role == "research_preparation":
                supply_observation_rules(out.get("candidates", []), extensions)
                if ctx['action'].get('observation_rule_targets'):
                    from v5_fixtures import prepared_rule_conditions
                    extensions['task_conditions'] = prepared_rule_conditions(ctx['action']['observation_rule_targets'])
            elif ctx.get("budget_unit") == "concurrent_sessions":
                extensions["model_assessments"] = planning_model_assessments(out, ctx)
            if extensions:
                path.write_text(json.dumps(extensions), encoding="utf-8")
        bind_candidates(out, ctx)
        seal_response(out, ctx, workspace)
        jsonschema.validate(out, output_schema)
        submit_intent(control_binding, should_stop, workspace, out)
        return {"status": "completed", "output": out, "usage": {"calls": 1}, "error": None}


def formal_ok(*, source, declarations, workspace, lean_command, timeout_seconds,
              allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None):
    if source == "theorem t : True := by trivial" and declarations == ["t"]:
        signature, dependencies, value = "True", ["True", "True.intro"], "True.intro"
    elif (source == "theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n"
          and declarations == ["add_zero_fixture"]):
        signature, dependencies, value = "(n : Nat) -> n + 0 = n", ["Nat", "Nat.add_zero"], "Nat.add_zero"
    else:
        raise AssertionError("No explicit compiler fixture covers this source and declaration set")
    signatures = {name: f"{name} : {signature}" for name in declarations}
    return {"status": "verified", "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "declarations": declarations, "axioms": {name: [] for name in declarations},
            "declaration_signatures": signatures,
            "signature_hash": hashlib.sha256(json.dumps(signatures, sort_keys=True).encode()).hexdigest(),
            "allowed_axioms": list(allowed_axioms),
            "dependency_closure": {name: dependencies for name in declarations},
            "dependency_evidence": {name: {ref: "fixture-" + ref for ref in dependencies} for name in declarations},
            "declaration_evidence": {name: {"type": signature, "value": value} for name in declarations},
            "toolchain": expected_toolchain or {"executable": "test-lean", "sha256": "f" * 64,
                          "version": "Lean test 4.32.0", "version_exit": 0, "configured_command": list(lean_command)}}


def formal_fail(**_): return {"status": "failed", "reason": "mock formal failure; not Lean sorry evidence"}


class EngineTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.repo = self.root / "repo"; self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)

    def tearDown(self): self.temp.cleanup()

    def make(self, runner, verifier=formal_ok, goal_kind="mathematical", **config):
        config.setdefault('plan_settle_seconds', 1)
        init = initialize(self.repo, goal="goal", goal_kind=goal_kind, workspace=self.root / "work", config={"reviewers": 2, "goal_auditors": 2, "max_cycles": 8, "lean_command": ["test-lean"], "scholarly_enabled": False, "operator_enabled": False, **config})
        engine = ResearchEngine(self.repo, init["instance_id"], runner=runner, formal_verifier=verifier)
        activate(engine, self.root, initialization_runner=ScriptedRunner())
        return engine, init["instance_id"]

    def assert_persisted_state_clean(self, engine):
        checked = engine.check()
        self.assertEqual(checked['errors'], [], checked)
        # Snapshot inspection deliberately leaves live trust files unexamined.
        self.assertEqual(checked['inspection']['not_checked'], ['governance_trust'], checked)
        self.assertEqual({(row['area'], row['status']) for row in checked['inspection']['findings']},
                         {('governance_trust', 'incomplete')}, checked)

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

    def test_nonformal_task_cannot_claim_final_research_goal_guarantee(self):
        runner = ScriptedRunner(); engine, _ = self.make(runner, goal_kind="research")
        for _ in range(20):
            status = engine.run(max_steps=1)
            if any(task['status'] == 'completed' for task in engine.runtime['tasks'].values()):
                break
        else:
            self.fail('The returned nonformal task was never independently assessed complete')
        self.assertNotIn(status["goal_status"], {"research_goal_satisfied", "mathematically_solved"})
        self.assertTrue(any(task.get("results") for task in engine.runtime["tasks"].values()),
                        engine.runtime["history"][-3:])
        self.assert_persisted_state_clean(engine)
        self.assertEqual(status["knowledge"]["K"], 0)

    def test_nonformal_mathematical_goal_is_not_solved(self):
        engine, _ = self.make(ScriptedRunner())
        status = engine.run(max_steps=20)
        self.assertTrue(any(task.get("results") for task in engine.runtime["tasks"].values()),
                        engine.runtime["history"][-3:])
        self.assertNotEqual(status["goal_status"], "mathematically_solved")
        self.assertEqual(status["knowledge"]["K"], 0)

    def test_formal_requires_two_blind_reviews_and_failure_does_not_create_k(self):
        runner = ScriptedRunner(formal=True); engine, _ = self.make(runner, plan_settle_seconds=1)
        for step in range(0, 30, 4):
            solved = engine.run(max_steps=min(4, 30 - step))
            if solved['knowledge']['K'] == 1:
                break
        else:
            self.fail('The fixture did not publish formally reviewed knowledge')
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
        self.assertEqual(engine.instance["formal_results"][verified["formal_result_id"]]["verification"]["toolchain"]["sha256"], "f" * 64)
        failed_runner = ScriptedRunner(formal=True); failed, _ = self.make(failed_runner, formal_fail, plan_settle_seconds=1)
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
            engine, _ = self.make(ScriptedRunner(invalid_plan=invalid))
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

    def test_work_budget_pause_resume_preserves_failed_request_without_replay(self):
        runner = ScriptedRunner(fail_role="research_work"); engine, instance = self.make(runner, work_calls=2, operations_calls=None)
        paused = engine.run(max_steps=10)
        self.assertIn(paused["status"], {"waiting", "capacity_waiting"})
        before = ResearchRepository(self.repo, instance).load()[2]["waiting_actions"]
        self.assertTrue(any(item["action"]["role"] == "research_work" for item in before.values()))
        work_calls = sum(role == "research_work" for role, _ in runner.prompts)
        control(self.repo, instance, "resume")
        resumed = engine.run(max_steps=1)
        after = ResearchRepository(self.repo, instance).load()[2]["waiting_actions"]
        self.assertEqual(before, after)
        self.assertEqual(sum(role == "research_work" for role, _ in runner.prompts), work_calls)
        self.assertIn(resumed["status"], {"waiting", "capacity_waiting"})

    def test_work_budget_exhaustion_does_not_prevent_operations(self):
        runner = ScriptedRunner()
        engine, _ = self.make(runner, work_calls=1, operations_calls=10)
        for _ in range(10):
            engine.run(max_steps=1)
            if any(a['role'] == 'research_work' for a in engine.runtime['queue']):
                break
        blocked = next(a.copy() for a in engine.runtime['queue'] if a['role'] == 'research_work')
        before = engine.status()["budget"]
        self.assertEqual(before["work"]["used"], before["work"]["limit"])
        engine._enqueue("research_plan", reason="Assess next steps with the remaining operating budget")
        engine._save()
        status = engine.run(max_steps=1)
        self.assertEqual(runner.prompts[-1][0], "research_plan")
        self.assertEqual(status["budget"]["operations"]["used"], before["operations"]["used"] + 1)
        self.assertEqual(status["budget"]["work"]["used"], before["work"]["used"])
        retained = next(a for a in engine.runtime['queue'] if a['id'] == blocked['id'])
        self.assertEqual({key: retained[key] for key in blocked}, blocked)

    def test_unlimited_budgets_continue_after_finite_exhaustion(self):
        runner = ScriptedRunner(formal=True)
        engine, instance = self.make(runner, work_calls=1, operations_calls=10)
        exhausted = engine.run(max_steps=20)
        self.assertIn(exhausted["status"], {"capacity_waiting", "waiting"})
        self.assertEqual(exhausted['budget']['work']['available'], 0)
        pinned_work = next(action for action in engine.runtime['queue'] if action['role'] == 'research_work')
        pinned_profile_ref = pinned_work['profile_ref']
        old_executions = set(engine.runtime["executions"])
        from v5_fixtures import send_control
        from do_math.execution_profiles import resolve_profile, profile_ref
        send_control(engine, "configure", config={"work_calls": None, "operations_calls": None})
        current_profiles = [resolve_profile(engine.instance['execution_profiles'], ref)
                            for refs in engine.instance['role_profile_refs'].values() for ref in refs]
        send_control(engine, "decision", config={"change": {"kind": "initialization",
            "operation": "probe", "profile_refs": [profile_ref(p) for p in current_profiles
                                               if p['actor_kind'] == 'ai']}})
        engine._enqueue("research_plan", reason="Inspect the newly unbounded work budget", front=True)
        engine._save()
        for _ in range(8):
            status = engine.run(max_steps=1)
            if status['budget']['operations']['used'] > exhausted['budget']['operations']['used']:
                break
        else:
            self.fail('Lifting the finite limits did not admit an operating call')
        self.assertTrue(old_executions <= set(engine.runtime["executions"]))
        for pool in ("work", "operations"):
            self.assertIsNone(status["budget"][pool]["limit"])
        self.assertGreater(status["budget"]["operations"]["used"], exhausted["budget"]["operations"]["used"])
        self.assertTrue(any(action['role'] == 'research_work' and action['profile_ref'] == pinned_profile_ref
                            for action in engine.runtime['queue']))
        fresh_work_profile = resolve_profile(engine.instance['execution_profiles'],
                                             engine.instance['role_profile_refs']['research_work'][0])
        self.assertNotEqual(profile_ref(fresh_work_profile), pinned_profile_ref)
        fresh_constraint = engine.instance['capacity_constraints'][fresh_work_profile['ai']['usage_constraint_ids'][0]]
        self.assertEqual(fresh_constraint['limit'], {'kind': 'unlimited'})
        # Admission is checked on an isolated copy: the old selected task keeps
        # its pinned profile, while newly prepared work can use this edition.
        from copy import deepcopy
        from do_math.repository import new_id
        from do_math.session_slots import SessionSlots
        from do_math.provider_wait import provider_for
        scratch = deepcopy(engine.runtime)
        candidate = {'id': new_id('EX'), 'role': 'research_work', 'status': 'queued'}
        slots = SessionSlots(engine.instance['workspace'], engine.instance['id'],
                             runtime=scratch, instance=deepcopy(engine.instance))
        self.assertTrue(slots.acquire(candidate['id'], 'work', fresh_work_profile['ai']['model'],
                                      profile=fresh_work_profile, execution=candidate,
                                      provider=provider_for(fresh_work_profile['ai']['model'])))
        self.assert_persisted_state_clean(engine)

    def test_budget_config_allows_null_only_for_call_limits(self):
        validate_config({"work_calls": None, "operations_calls": None})
        for field in ("work_calls", "operations_calls"):
            for value in (0, -1, True, "unlimited", 1.5):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    validate_config({field: value})
        with self.assertRaises(ValueError):
            validate_config({"run_timeout_seconds": None})

    def test_each_unlimited_pool_keeps_the_other_pool_finite(self):
        for work, operations, exhausted_pool in ((None, 1, "operations"), (1, None, "work")):
            with self.subTest(work=work, operations=operations):
                engine, _ = self.make(ScriptedRunner(), work_calls=None, operations_calls=None)
                before = engine.status()['budget']
                limits = {pool + '_calls': None if limit is None else before[pool]['used'] + limit
                          for pool, limit in (('work', work), ('operations', operations))}
                control(self.repo, engine.instance['id'], 'configure', config=limits)
                engine.process_controls()
                from do_math.execution_profiles import profile_ref
                selected = {ref['id'] for refs in engine.instance['role_profile_refs'].values() for ref in refs}
                control(self.repo, engine.instance['id'], 'decision', config={'change': {
                    'kind': 'initialization', 'operation': 'probe', 'profile_refs': [profile_ref(p)
                    for pid, p in engine.instance['execution_profiles'].items()
                    if pid in selected and p['actor_kind'] == 'ai']}})
                engine.process_controls()
                for _ in range(0, 20, 4):
                    status = engine.run(max_steps=4)
                    budget = status['budget']
                    unlimited_pool = 'work' if work is None else 'operations'
                    if (budget[exhausted_pool]['used'] > before[exhausted_pool]['used']
                            and budget[unlimited_pool]['used'] > before[unlimited_pool]['used']):
                        break
                else:
                    self.fail('Both budget pools were not exercised within 20 steps')
                self.assertEqual(status["budget"][exhausted_pool]["used"] - before[exhausted_pool]['used'], 1,
                    {'budget': status['budget'], 'waits': status['waiting_actions'], 'queue': engine.runtime['queue']})
                self.assertEqual(status['budget'][exhausted_pool]['available'], 0)
                self.assertFalse(engine._budget_available(exhausted_pool, 0))
                self.assertIsNone(status["budget"][unlimited_pool]["limit"])
                self.assertTrue(engine._budget_available(unlimited_pool, 0))
                self.assertGreater(status["budget"][unlimited_pool]["used"], before[unlimited_pool]['used'])

    def test_crash_recovery_and_artifact_immutability(self):
        engine, instance = self.make(ScriptedRunner())
        action = engine.runtime['queue'][0]
        crashed = engine._register_execution(action, {'id': 'EX-crash', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': []})
        from do_math.windows_job import WindowsJob, process_identity
        from uuid import uuid4
        job = WindowsJob([sys.executable, '-c', 'pass'], cwd=self.root,
                         name='CORE-CRASH-' + uuid4().hex)
        self.addCleanup(job.close)
        crashed['process'] = {**process_identity(job), 'job_name': job.name}
        job.resume()
        from types import SimpleNamespace
        from do_math.codex_adapter import CodexExecAdapter
        # Root signal alone can precede the Job's active-count update.
        # Use the real collector barrier with the original ten-second limit.
        self.assertTrue(CodexExecAdapter('fixture-cli').wait_for_termination(SimpleNamespace(job=job), 10))
        self.assertEqual(job.inspect().active_processes, 0)
        engine.runtime['active_execution'] = crashed['id']
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
            store.save(head, instance_data, runtime_data,
                       artifacts={f"runtime/artifacts/{bundle}/other.txt": b"mutate"})


if __name__ == "__main__": unittest.main(verbosity=2)
