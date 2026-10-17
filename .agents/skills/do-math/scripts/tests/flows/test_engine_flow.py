"""The research engine's owner loop on a Sim: initialization and activation, research flows, recovery and checks.

The legacy tests ran these on a synthetic active template with a scripted runner
that started a real Windows Job per call; here the model double answers at the
workers' spawn seam (``support.default_responder.DefaultResponder``'s answers), the Lean
double at the formal worker's, and every other external resource is a port fake.
"""
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.repository import ResearchRepository
from do_math.windows_job import process_identity
from support.default_responder import DefaultResponder
from support.engine_context import damage, record_contexts
from support.model import Answer
from support.sim import Sim, warm_template

setUpModule = warm_template


def adopted_profile(engine, role):
    """The role's adopted profile edition (the registry also keeps editions activation replaced)."""
    from do_math.execution_profiles import resolve_profile
    return resolve_profile(engine.instance['execution_profiles'], engine.instance['role_profile_refs'][role][0])


class EngineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_initialization_reports_missing_values_without_model_dispatch(self):
        sim = Sim(self.root, goal="Explicit initial input")
        engine = sim.engine
        engine.run(max_steps=1)
        self.assertEqual(engine.instance["lifecycle"]["state"], "initializing")
        missing = engine.instance["lifecycle"]["activation"]["missing"]
        self.assertTrue({"governance", "configuration", "independent_intent", "trust_environment",
                         "research_authority"} <= set(missing))
        self.assertEqual(sim.model.calls, [])
        self.assertEqual(sim.jobs.launched, [], 'no worker was started either')
        self.assertEqual(engine.instance["grants"], {})
        _, stored_instance, stored_runtime = engine.store.load()
        self.assertEqual(stored_instance["lifecycle"]["activation"]["missing"], missing)
        self.assertEqual(stored_runtime["availability"], {
            "state": "blocked", "reason": "initialization_incomplete", "next_owner": "user"})

    def test_public_initialization_reaches_active_with_distinct_interpretation(self):
        """About 4 s, over the 2 s Sim budget: the public path from an empty repository is what it checks."""
        from do_math import formal
        from support.provider_probes import ObservedCalls
        with ObservedCalls(verifier=formal.verify_lean, worker=formal._worker) as calls:
            sim = Sim.activated(self.root)
        engine = sim.engine
        self.assertEqual((calls.count('verifier'), calls.count('worker')), (0, 0))
        self.assertEqual(sim.lean.checks, [])
        self.assertEqual(engine.instance["lifecycle"]["state"], "active")
        check = engine.instance["lifecycle"]["intent_check"]
        self.assertNotEqual(check["interpretation_execution_id"], check["check_execution_id"])
        self.assertTrue(engine.instance["capability_evidence"])
        self.assertEqual(engine.instance["lifecycle"]["activation"]["missing"], [])

    def test_nonformal_mathematical_goal_is_not_solved(self):
        """About 13 s, over the 2 s Sim budget: the goal audits' judgment of the nonformal result is reached through every role."""
        engine = Sim.activated().engine
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
        """About 34 s, over the 2 s Sim budget: formal work, its check and two blind reviews run through every role, twice."""
        from do_math.knowledge_records import usable_links
        sim = Sim.activated()
        model = record_contexts(sim, DefaultResponder(formal=True))
        engine = sim.engine
        for step in range(0, 30, 4):
            solved = engine.run(max_steps=min(4, 30 - step))
            if solved['knowledge']['K'] == 1:
                break
        else:
            self.fail('The fixture did not publish formally reviewed knowledge: ' + json.dumps({
                'snapshot': engine.head, 'status': engine.runtime['status'],
                'queue': engine.runtime['queue'], 'waiting': engine.runtime.get('waiting_actions', {}),
                'executions': [{key: value.get(key) for key in ('id', 'role', 'status', 'outcome', 'error', 'result_ref')}
                               for value in engine.runtime['executions'].values()]}, ensure_ascii=False, default=str))
        self.assertEqual(solved["knowledge"]["K"], 1)
        kid = next(kid for kid in engine.instance['knowledge'] if usable_links(engine.instance, kid))
        assessment_id = usable_links(engine.instance, kid)[0]['assessment_id']
        cycle_id = engine.instance['identity_assessments'][assessment_id]['review_cycle_id']
        # The reviews are chosen and judged on what the model actually received: the raw prompt its
        # provider CLI read and the context in it (the legacy runner's prompts).
        reviews = [(ctx, prompt) for role, ctx, prompt in model.prompts if role == "identity_review"
                   and ctx["action"].get("stage") == "initial" and ctx["action"].get("target") == kid
                   and ctx["action"].get("review_cycle_id") == cycle_id
                   and engine.runtime['executions'][ctx['execution_id']].get('outcome') == 'output_accepted']
        self.assertEqual(len(reviews), 2, [(ctx['action'], engine.runtime['executions'][ctx['execution_id']].get('outcome'))
                                           for role, ctx, _ in model.prompts if role == 'identity_review'])
        self.assertEqual(len({ctx['action']['slot'] for ctx, _ in reviews}), 2)
        self.assertEqual(len({ctx['action']['review_cycle_id'] for ctx, _ in reviews}), 1)
        self.assertTrue(all('"reviews"' not in prompt for _, prompt in reviews))
        # The engine archived the same prompt below each review's input bundle.
        for ctx, prompt in reviews:
            bundle = engine.runtime['executions'][ctx['execution_id']]['input_bundle']
            self.assertEqual(engine.store.read(f"runtime/artifacts/{bundle}/input.txt", engine.head).decode('utf-8'), prompt)
        verified = engine.instance['knowledge'][kid]
        result = engine.instance["formal_results"][verified["formal_result_id"]]
        self.assertEqual(engine.instance["trust_environments"][result["trust_environment_id"]]["status"], "active")
        self.assertEqual(engine.instance["active_trust_environment"], result["trust_environment_id"])
        self.assertEqual(result["verification"]["toolchain"],
                         engine.instance['trust_environments'][engine.instance['active_trust_environment']]['toolchain'])
        # The same flow whose central check fails: the work names a declaration its source does not
        # define, so Lean exits with an unknown identifier (a compile failure, not sorry evidence).
        failed = Sim.activated()
        failed.model.responder = DefaultResponder(formal=True)
        failed.model.on('research_work').reply(Answer(lambda out, ctx: {**out, 'knowledge': [
            {**row, 'declaration_names': ['t', 'u']} for row in out['knowledge']]}))
        for _ in range(0, 20, 4):
            failed_status = failed.engine.run(max_steps=4)
            if any(ex['role'] == 'formal_check' and ex.get('status') == 'ended'
                   and ex.get('formal_status') == 'failed' for ex in failed.runtime['executions'].values()):
                break
        else:
            self.fail('The fixture did not reach a failed formal check')
        self.assertEqual(failed_status["knowledge"]["K"], 0)

    def test_plan_rejects_missing_candidate_and_criterion(self):
        """About 15 s, over the 2 s Sim budget: each case runs preparation, contract review and the rejected plan."""
        for invalid in ("missing", "criterion"):
            sim = Sim.activated()
            # Output repair is covered elsewhere; the first rejection is the rule here.
            sim.control('configure', config={'max_output_repairs': 0})
            sim.engine.process_controls()
            self.assertEqual(sim.instance['config']['max_output_repairs'], 0)
            from support.model import default
            sim.model.responder = DefaultResponder(invalid_plan=invalid)
            plan = sim.model.on('research_plan')
            if invalid == 'criterion':
                # The first plan selects work; its returned-task assessment is in the next call.
                plan.reply(default())
            plan.reply(default(expected_receipt='rejected'))
            engine = sim.engine
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
            # The worker submitted the plan through the workspace tool; the receiver rejected it and its
            # durable receipt keeps the check (the legacy runner raised that receipt as the wait's error).
            executions = {w['execution_id'] for w in failed}
            receipts = [row for row in engine.runtime.get('control_receipts', {}).values()
                        if row.get('execution_id') in executions and row.get('state') == 'rejected']
            checks = [json.loads(engine.store.read(row['payload']['submission_check']['check_ref'], engine.head))
                      for row in receipts if row.get('payload', {}).get('submission_check')]
            messages = [issue['message'] for check in checks for issue in check['issues']]
            self.assertTrue(any(('derived-ready' if invalid == 'missing' else 'obligation') in text for text in messages),
                            (receipts, messages))

    def test_crash_recovery_and_artifact_immutability(self):
        sim = Sim.activated()
        engine = sim.engine
        engine._enqueue('research_preparation', reason='The first AI action of an active instance')
        action = engine.runtime['queue'][0]
        crashed = engine._register_execution(action, {'id': 'EX-crash', 'role': action['role'],
            'status': 'queued', 'input_snapshot': engine.head, 'input_manifest': []})
        profile = engine._execution_profile(action)
        self.assertTrue(engine._provider_admit(action, crashed['id'], profile=profile, execution=crashed))
        # The launch owner has ended: its process ID now names another process (another creation time).
        crashed['launch_ticket']['owner'] = {**sim.jobs.owner_identity(), 'creation_filetime': '1'}
        crashed['launch_ticket']['phase'] = 'dispatched'
        sim.jobs.programs.insert(0, (lambda argv: argv == ['model', 'process'], lambda argv, cwd, env: 0))
        job = sim.jobs.launch(['model', 'process'], cwd=self.root, name=crashed['launch_ticket']['job_name'])
        self.addCleanup(job.close)
        engine._session_slots().started(crashed['id'], {**process_identity(job), 'job_name': job.name},
                                        at=engine.ports.clock.now())
        job.resume()
        self.assertTrue(job.wait(10))
        self.assertEqual(job.inspect().active_processes, 0)
        engine._save()
        ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id).run(max_steps=1)
        _, _, runtime = ResearchRepository(sim.repository, sim.instance_id, backend=sim.ports.git_backend,
                                           clock=sim.clock).load()
        self.assertEqual(runtime['executions']['EX-crash']['outcome'], 'execution_incomplete')
        owner = runtime['activities'][crashed['owner_activity_id']]
        self.assertIn('EX-crash', owner['assigned_execution_ids'])
        self.assertTrue(runtime['recoveries'])
        self.assertTrue(owner.get('waiting') or owner['unresolved'])
        store = ResearchRepository(sim.repository, sim.instance_id, backend=sim.ports.git_backend, clock=sim.clock)
        head, instance_data, runtime_data = store.load()
        recovered = runtime_data['executions']['EX-crash']
        self.assertTrue(store.read(recovered['result_ref'], head))
        bundle = recovered['artifact_bundle']
        with self.assertRaisesRegex(ValueError, 'existing runtime artifact bundles are immutable'):
            store.save_with_state(head, instance_data, runtime_data,
                                  artifacts={f"runtime/artifacts/{bundle}/other.txt": b"mutate"})


class PublicGitFlow(unittest.TestCase):
    def test_public_activation_work_receipt_assessment_and_next_plan(self):
        """About 11 s, over the 2 s Sim budget: the public activation and every role of one research round are what it checks."""
        from support.engine_flow import BoundedObservationResponder, record_submissions, worker_bindings
        from do_math.canonical import canonical_json, exact_content_hash
        from do_math.submission import issued_input, read_sealed_submission
        with tempfile.TemporaryDirectory() as temporary:
            sim = Sim(Path(temporary), goal="Record and assess a bounded observation", config={
                "observation_mode": "periodic", "tool_review_window_seconds": 600,
                "self_check_response_window_seconds": 60, "import_rework_limit": 3, "selection_failure_limit": 3,
                "exhaustion_empty_limit": 3, "proposal_version_limit": 3, "contract_revision_limit": 3})
            model = record_submissions(sim, BoundedObservationResponder())
            engine = sim.engine

            def check_runs():
                failures = [{key: execution.get(key) for key in ("id", "role", "outcome", "error")}
                            for execution in engine.runtime["executions"].values()
                            if execution["status"] == "ended" and execution.get("outcome") != "output_accepted"]
                self.assertEqual(failures, [], {"failures": failures, "repair_issues": [
                    action.get("repair", {}).get("issues", []) for action in engine.runtime["queue"]]})
            sim.activate()
            check_runs()
            self.assertEqual(engine.instance["lifecycle"]["state"], "active")
            for _ in range(15):
                engine.run(max_steps=1)
                check_runs()
                if any(t.get("status") == "completed" for t in engine.runtime["tasks"].values()):
                    break
            else:
                self.fail("Public flow did not assess returned work: " + repr(engine.runtime["history"][-5:]))
            task = next(t for t in engine.runtime["tasks"].values() if t["status"] == "completed")
            self.assertEqual(task["assessment"]["item_dispositions"][0]["kind"], "fulfilled")
            self.assertTrue(engine.instance["knowledge"])
            roles = [call["role"] for call in model.calls]
            self.assertGreaterEqual(roles.count("research_plan"), 2)
            self.assertEqual(roles.count("research_work"), 1)
            _, instance, runtime = engine.store.load()
            self.assertEqual(runtime["tasks"][task["id"]]["status"], "completed")
            self.assertTrue(runtime["integrations"])
            # Every bound call: the checker context holds the binding the runner was given (the worker
            # request), only research work is offered the self-check tool, and the submission made with
            # the workspace tool was delivered and accepted by the owner's durable receipt.
            requested = worker_bindings(sim)
            self.assertEqual(len(model.submissions), len([call for call in model.calls]))
            for row in model.submissions:
                with self.subTest(role=row["role"], execution=row["binding"]["execution_id"]):
                    self.assertEqual(row["binding"], requested[row["binding"]["execution_id"]])
                    self.assertEqual(row["binding"].get("self_check", False), row["role"] == "research_work")
                    self.assertIn(row["delivery"], {"submitted", "already_received"})
                    self.assertEqual(row["receipt"], "accepted")
                    execution = runtime['executions'][row['binding']['execution_id']]
                    context, schema = issued_input(execution, engine.head, engine.store.read)
                    archived = engine.store.read(f"runtime/artifacts/{execution['input_bundle']}/schema.json", engine.head)
                    self.assertEqual(archived, row['schema_bytes'])
                    self.assertEqual(archived, canonical_json(schema))
                    sealed = read_sealed_submission(execution, engine.head, engine.store.read)
                    self.assertEqual(sealed['check']['mode'], 'receiver')
                    self.assertTrue(sealed['check']['passed'], sealed['check'])
                    self.assertEqual(sealed['check']['input_hashes']['schema'], hashlib.sha256(archived).hexdigest())
                    self.assertEqual(sealed['check']['input_hashes']['context'], exact_content_hash(context))
                    self.assertTrue(sealed['output']['integration_bundles'])
                    if row['role'] == 'research_preparation':
                        for candidate in sealed['output']['candidates']:
                            self.assertTrue(candidate['profile_refs'])
                            self.assertTrue(all(ref in context['role_profile_refs']['research_work']
                                                for ref in candidate['profile_refs']))
                            self.assertTrue(candidate['authority_refs'])
                            self.assertLessEqual(set(candidate['authority_refs']),
                                {grant['id'] for grant in context['grants']
                                 if grant['status'] == 'active' and 'research_work' in grant['roles']})


class MaintenanceConnections(unittest.TestCase):
    def test_maintenance_archives_complete_run_before_approved_cleanup(self):
        from copy import deepcopy
        from do_math import activities, execution_lifecycle, execution_profiles
        from do_math.launch import ticket
        sim = Sim.activated()
        engine = sim.engine
        expiry = (sim.clock.wall() + timedelta(days=1)).isoformat()
        request = sim.control('decision', text='Authorize local maintenance and cleanup of the requested ended run.',
                              config={'change': {'kind': 'grant', 'grant': {'id': 'GR-cleanup', 'kind': 'local',
                                      'roles': ['maintenance'], 'reuse': 'reusable', 'expires_at': expiry}}})
        engine.process_controls()
        self.assertIn('GR-cleanup', engine.instance['grants'], request)
        action = {"id": "AC-cleanup", "role": "maintenance", "actor_kind": "ai",
                  "grant_id": "GR-cleanup", "requested_by": "UC-cleanup", "cleanup_execution_ids": ["EX-finished"]}
        engine.runtime["history"].append({"kind": "user_control", "request": {"id": "UC-cleanup", "origin": "user",
            "action": "request", "config": {"role": "maintenance", "cleanup_execution_ids": ["EX-finished"]}}})
        profile = adopted_profile(engine, 'maintenance')
        for eid in ("EX-finished", "EX-maintenance"):
            aid = "AY-" + eid
            at = sim.clock.now()
            activities.open_activity(engine.runtime, activity_id=aid, activity_kind="maintenance", owner_ref="GR-cleanup",
                                     input_refs=[], opened_at=at)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid, actor_kind="ai",
                input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=at)
            execution.update(role="maintenance", action=deepcopy(action), grant_id="GR-cleanup")
            activities.assign_execution(engine.runtime, aid, execution)
            execution_lifecycle.transition_execution(execution, "ended", at=at, outcome="cancelled")
            # Explicit synthetic termination evidence; scope, schemas, references and the state publication are real.
            execution["launch_ticket"] = {**ticket(eid, profile, jobs=sim.jobs, clock=sim.clock), "phase": "not_started"}
            execution["capacity"] = {"local_termination": "confirmed"}
            activities.finish_activity(engine.runtime, aid, result_refs=[], unresolved=[], followups=[], at=at)
        engine._save()
        run = Path(engine.instance["workspace"]) / "runs/EX-finished"
        (run / "workspace").mkdir(parents=True)
        (run / "evidence").mkdir()
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
                         {"result": result, "candidates": engine.runtime["history"][-1].get("candidates")})
        self.assertFalse(run.exists())
        manifest = engine.runtime["executions"]["EX-finished"]["collection"]["retention_manifest"]
        self.assertEqual(len(manifest), 2)
        for row in manifest:
            raw = engine.store.read(row["artifact_ref"], row["snapshot"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])


class SourceIntegrityCheckTests(unittest.TestCase):
    def test_current_corrupt_source_is_found_by_the_explicit_full_byte_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            sim = Sim.activated()
            source = Path(temporary) / "source.txt"
            source.write_text("preserved original", encoding="utf-8")
            sim.control('source', config={'path': str(source)})
            sim.engine.process_controls()
            path = sim.instance["sources"][0]["path"]
            store = ResearchRepository(sim.repository, sim.instance_id, backend=sim.ports.git_backend, clock=sim.clock)
            # Damage from outside do-math: the head's source bytes differ from their recorded hash.
            damaged = damage(store, path, b"corrupt bytes")
            # run and controls check artifact presence and length only; full bytes belong to check.
            report = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id).check(requested_areas=["record_storage"])
            self.assertFalse(report["passed"])
            self.assertTrue(any(path in row["evidence"] for row in report["inspection"]["findings"]),
                            report["inspection"]["findings"])
            self.assertEqual(store._store.read_snapshot().head, damaged)


if __name__ == '__main__':
    unittest.main()
