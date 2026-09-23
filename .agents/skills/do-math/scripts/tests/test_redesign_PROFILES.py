"""Profile pinning, admission atomicity and observed provider evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import model_policy, scheduled_operator


CONFIG = {
    "tier_models": dict(model_policy.MODELS), "role_tiers": dict(model_policy.ROLE_TIERS),
    "session_limits": deepcopy(model_policy.LIMITS), "effort": "medium",
    "max_input_bytes": 500000, "call_timeout_seconds": 600, "run_timeout_seconds": 7200,
    "operator_timeout_seconds": 5400, "operator_effort": "high",
    "observation_mode": "event_driven", "observation_interval_seconds": 300,
    "observation_idle_seconds": 120, "observation_unbounded_wait_seconds": 600,
    "max_observation_reviews": 3, "checkpoint_grace_seconds": 10,
    "finish_notice_seconds": 60, "dispatch_reserve_seconds": 300,
    "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False,
    "operator_model": "gpt-5.6-sol", "provider_retry_initial_seconds": 300, "provider_retry_max_seconds": 7200,
}


class ProfileTests(unittest.TestCase):
    def test_normal_final_delivery_rendering_preserves_the_sealed_profile(self):
        from do_math import execution_profiles as api, contracts
        profile = next(p for p in api.build_profiles(CONFIG)['execution_profiles'].values()
                       if p['role'] == 'research_work')
        original = deepcopy(profile)
        role_prompt = contracts.render_prompt('research_work', {'action': {'role': 'research_work'}}, documents=[])
        delivered = api.prepare_prompt(role_prompt, profile)
        self.assertIn('normal JSON final', delivered)
        self.assertIn('optional early submission', delivered)
        self.assertNotIn("Submit proposals through the execution's supplied submission tools.", delivered)
        self.assertEqual(profile, original)
        self.assertEqual(api.profile_ref(profile), api.profile_ref(original))
        for rule in original['boundary']['rules']:
            if not rule.startswith('Submit proposals'):
                self.assertIn(rule, delivered)
        changed = deepcopy(profile)
        changed['boundary']['rules'][0] = 'Use unassigned inputs.'
        with self.assertRaises(ValueError): api.validate_profile(changed)

    def capability_adapter(self, *, supported=True):
        from unittest.mock import Mock
        adapter = Mock()
        identity = {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "fixture"}}
        adapter.capability_identity.return_value = identity
        adapter.describe.return_value = {"scope": "cli_command_surface_only", "identity": identity,
            "verified": True, "supported": {key: supported for key in ("jsonl", "model", "structured_output")}}
        return adapter

    def test_execution_control_is_registered_and_round_trips_in_child(self):
        import subprocess
        from do_math.control_transport import ControlTransport
        from do_math import codex_worker, claude_worker
        from do_math.model_runner import CodexModelRunner
        from test_model_runner import Adapter
        api = self.profiles()
        profile = next(p for p in api.build_profiles({**CONFIG, "scholarly_server": {
                       "command": sys.executable, "args": [str(Path(__file__).resolve())]}})["execution_profiles"].values()
                       if p["role"] == "research_work")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transport = ControlTransport(root / "transport")
            binding = transport.issue("EX-bound", "GR-bound")
            adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}})
            runner = CodexModelRunner("fake")
            runner._adapter = adapter
            runner.run(prompt=api.prepare_prompt("test", profile), input_seal=api.prompt_seal(api.prepare_prompt("test", profile)), output_schema={}, workspace=root,
                evidence_dir=root / "evidence", model=profile["ai"]["model"], effort=profile["ai"]["effort"],
                timeout_seconds=600, execution_id="EX-bound", profile=profile, control_binding=binding)
            self.assertEqual(adapter.request["control_binding"], binding)
            request = codex_worker.load_request(root / "evidence" / "request.json")
            argv = codex_worker.build_argv(request)
            config = ControlTransport.mcp_server_config(binding)
            self.assertIn("mcp_servers.execution_control.command=" + json.dumps(config["command"], ensure_ascii=False), argv)
            self.assertIn("mcp_servers.execution_control.args=" + json.dumps(config["args"], ensure_ascii=False), argv)
            claude_request = {k: v for k, v in request.items()
                              if k not in {"codex_path", "sandbox", "windows_sandbox", "approval_policy"}}
            claude_request["claude_path"] = "claude"
            path = root / "claude-request.json"
            path.write_text(json.dumps(claude_request), encoding="utf-8")
            argv = claude_worker.build_argv(claude_worker.load_request(path))
            servers = json.loads(argv[argv.index("--mcp-config") + 1])["mcpServers"]
            self.assertEqual(servers["execution_control"], config)
            self.assertEqual(set(servers), {"execution_control", "scholarly"})
            process = subprocess.Popen([config["command"], *config["args"]], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            sequence = 0
            def rpc(method, params):
                nonlocal sequence
                sequence += 1
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": sequence, "method": method, "params": params}) + "\n")
                process.stdin.flush()
                response = json.loads(process.stdout.readline())
                self.assertEqual(response["id"], sequence)
                self.assertNotIn("error", response)
                return response["result"]
            def call(name, arguments):
                return json.loads(rpc("tools/call", {"name": name, "arguments": arguments})["content"][0]["text"])
            try:
                self.assertEqual(rpc("initialize", {"protocolVersion": "2024-11-05"})["serverInfo"]["version"], "5")
                self.assertEqual({t["name"] for t in rpc("tools/list", {})["tools"]},
                                 {"control_submit", "control_receipt", "control_self_check", "submit_draft"})
                submitted = call("control_submit", {"request_id": "REQ-one", "kind": "submit_intent",
                    "execution_id": "EX-cannot-override-bound-execution",
                    "payload": {"draft_path": "draft.json"}})
                self.assertEqual(submitted["state"], "submitted")
                self.assertIsNone(call("control_receipt", {"request_id": "REQ-one"}))
                publications = []
                def publish(request):
                    self.assertEqual((request["execution_id"], request["grant_id"]), ("EX-bound", "GR-bound"))
                    publications.append(request)
                    return {"state": "accepted", "published": True, "snapshot": "test-published-head"}
                transport.pump(publish)
                receipt = call("control_receipt", {"request_id": "REQ-one"})
                self.assertEqual(receipt["state"], "accepted")
                self.assertEqual(receipt["execution_id"], "EX-bound")
                self.assertEqual(receipt["snapshot"], "test-published-head")
                other = transport.issue("EX-other", "GR-other")
                self.assertIsNone(ControlTransport.worker_receipt(other, "REQ-one"))
                transport.pump(publish)
                self.assertEqual(len(publications), 1)
                transport.request_self_check(binding, self_check_id="SC-one", payload={"obligations": ["answer"]})
                self.assertEqual(call("control_self_check", {"self_check_id": "SC-one"})["execution_id"], "EX-bound")
                call("control_self_check", {"self_check_id": "SC-one", "response": {"answered": True}})
                transport.pump(publish)
                self.assertEqual(call("control_receipt", {"request_id": "self-check-SC-one"})["state"], "accepted")
                transport.close(binding, reason="execution ended")
                self.assertEqual(call("control_submit", {"request_id": "REQ-after", "kind": "submit_intent",
                    "payload": {"manifest": []}})["state"], "closed")
            finally:
                process.stdin.close()
                process.wait(timeout=10)
                self.assertEqual(process.returncode, 0, process.stderr.read())
                process.stdout.close()
                process.stderr.close()
            for worker_request in (request, claude_request):
                worker_request["control_binding"] = {**binding, "execution_id": "EX-other"}
                with self.assertRaises(ValueError):
                    codex_worker.validate_execution_binding(worker_request)
            with self.assertRaises(ValueError):
                runner.run(prompt=api.prepare_prompt("wrong", profile), input_seal=api.prompt_seal(api.prepare_prompt("wrong", profile)), output_schema={}, workspace=root, evidence_dir=root / "wrong",
                    model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=600,
                    execution_id="EX-other", profile=profile, control_binding=binding)
            self.assertFalse((root / "wrong").exists())

    def test_both_adapters_snapshot_the_exact_control_binding(self):
        from unittest.mock import Mock
        from do_math.control_transport import ControlTransport
        from do_math.codex_adapter import CodexExecAdapter
        from do_math.claude_adapter import ClaudePrintAdapter
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "workspace"
            work.mkdir()
            binding = ControlTransport(root / "transport").issue("EX-snapshot", "GR-snapshot", workspace=work)
            prompt, schema = root / "input.txt", root / "schema.json"
            prompt.write_text("test", encoding="utf-8")
            schema.write_text("{}", encoding="utf-8")
            common = {"prompt_path": str(prompt), "output_schema_path": str(schema), "cwd": str(work),
                "model": "test", "effort": "low", "max_runtime_seconds": 10,
                **{key: str(root / key) for key in ("stdout_path", "stderr_path", "final_path", "status_path")},
                "execution_id": "EX-snapshot", "profile_ref": {"id": "EP-test", "revision": 1, "sha256": "a" * 64},
                "control_binding": binding}
            for adapter, options in ((CodexExecAdapter("codex"), {"codex_path": "codex", "sandbox": "danger-full-access", "approval_policy": "never"}),
                                     (ClaudePrintAdapter("claude"), {"claude_path": "claude"})):
                request = root / (adapter.executable_key + ".json")
                request.write_text(json.dumps({**common, **options}), encoding="utf-8")
                with patch("do_math.codex_adapter.WindowsJob", return_value=Mock()):
                    execution = adapter.start(request, cwd=root, env={})
                snap = json.loads(execution.request_path.read_text(encoding="utf-8"))
                self.assertEqual(snap["control_binding"], binding)
                self.assertEqual(snap["execution_id"], binding["execution_id"])
                request.write_text("{}", encoding="utf-8")
                self.assertEqual(json.loads(execution.request_path.read_text(encoding="utf-8"))["control_binding"], binding)

    def test_session_slots_has_only_git_authority(self):
        from do_math import session_slots
        source = Path(session_slots.__file__).read_text(encoding="utf-8")
        self.assertNotIn("sqlite3", source)
        instance = self.profiles().build_profiles(CONFIG)
        runtime = {"executions": {}, "reservations": {}}
        with tempfile.TemporaryDirectory() as directory:
            slots = session_slots.SessionSlots(Path(directory), "test", runtime=runtime, instance=instance)
            self.assertIsInstance(slots, session_slots.GitSessionSlots)
            self.assertEqual(list(Path(directory).iterdir()), [])
            with self.assertRaises(TypeError):
                session_slots.SessionSlots(Path(directory), "test")

    def test_adopted_call_limits_share_git_ledger_without_becoming_sessions(self):
        from do_math.session_slots import GitSessionSlots
        api = self.profiles()
        config = {**deepcopy(CONFIG), "session_limits": None, "model": "adopted-model",
                  "role_models": {"research_plan": "adopted-planner"}, "work_calls": 1, "operations_calls": 2}
        instance = api.build_profiles(config)
        runtime = {"executions": {}, "reservations": {}}
        chosen = model_policy.selection(config, {"role": "research_work"}, {}, {}, profiles=instance["execution_profiles"])
        self.assertEqual(chosen["model"], "adopted-model")
        profile = api.resolve_profile(instance["execution_profiles"], chosen["profile_ref"])
        self.assertEqual(profile["ai"]["capacity_refs"], [])
        slots = GitSessionSlots(runtime, instance)
        self.assertTrue(slots.acquire("EX-call", "work", chosen["model"], profile=profile,
                                    execution={"id": "EX-call", "role": "research_work"}))
        self.assertTrue(slots.release("EX-call"))
        # Call mode counts admitted attempts, including failures, as the old call budget did.
        self.assertFalse(slots.acquire("EX-second", "work", chosen["model"], profile=profile,
                                     execution={"id": "EX-second", "role": "research_work"}))
        plan = model_policy.selection(config, {"role": "research_plan"}, {}, {}, profiles=instance["execution_profiles"])
        self.assertEqual(plan["model"], "adopted-planner")
        self.assertTrue(all(c["kind"] == "cumulative" for c in instance["capacity_constraints"].values()))
        self.assertEqual(slots.usage_snapshot()["work"]["used"], 1)
        # Raising a limit creates a new edition, not a fresh unspent budget.
        changed = api.build_profiles({**config, "work_calls": 2})
        instance["execution_profiles"].update(changed["execution_profiles"])
        instance["capacity_constraints"].update(changed["capacity_constraints"])
        instance["role_profile_refs"] = changed["role_profile_refs"]
        new_profile = next(p for p in changed["execution_profiles"].values() if p["role"] == "research_work")
        self.assertTrue(slots.acquire("EX-edition", "work", chosen["model"], profile=new_profile,
                                    execution={"id": "EX-edition", "role": "research_work"}))
        self.assertFalse(slots.acquire("EX-third", "work", chosen["model"], profile=new_profile,
                                     execution={"id": "EX-third", "role": "research_work"}))
        self.assertEqual(slots.usage_snapshot()["work"]["used"], 2)

    def test_work_has_no_deadline_and_operations_keep_their_call_window(self):
        from do_math.model_runner import CodexModelRunner
        from test_model_runner import Adapter
        api = self.profiles()
        profiles = api.build_profiles({key: value for key, value in CONFIG.items()
            if key not in api.LEGACY_WINDOW_KEYS})["execution_profiles"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for role, timeout in (("research_work", None), ("operational_review", 600)):
                profile = next(p for p in profiles.values() if p["role"] == role)
                self.assertNotIn('run_timeout_seconds', profile['window'])
                self.assertNotIn('dispatch_reserve_seconds', profile['window'])
                runner = CodexModelRunner("fake")
                runner._adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}})
                runner.run(prompt=api.prepare_prompt("test", profile), input_seal=api.prompt_seal(api.prepare_prompt("test", profile)), output_schema={}, workspace=root, evidence_dir=root / role,
                    model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=timeout,
                    execution_id="EX-" + role, profile=profile)
                self.assertEqual(runner._adapter.request['max_runtime_seconds'], timeout)
                if role == 'operational_review':
                    for invalid in (None, CONFIG['call_timeout_seconds'] + 1):
                        with self.assertRaisesRegex(ValueError, "deadline"):
                            runner.run(prompt=api.prepare_prompt("test", profile), input_seal=api.prompt_seal(api.prepare_prompt("test", profile)), output_schema={}, workspace=root, evidence_dir=root / (role + "-over"),
                                model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=invalid,
                                execution_id="EX-" + role, profile=profile)

    def profiles(self):
        self.assertIsNotNone(importlib.util.find_spec("do_math.execution_profiles"),
                             "immutable execution profiles are absent")
        from do_math import execution_profiles
        return execution_profiles

    def test_legacy_profile_identity_is_preserved_without_restoring_its_deadline(self):
        api = self.profiles()
        current = api.build_profiles({key: value for key, value in CONFIG.items()
            if key not in api.LEGACY_WINDOW_KEYS})['execution_profiles']
        old_registry = {}
        for profile in current.values():
            body = deepcopy(profile)
            body['window'].update({key: CONFIG[key] for key in api.LEGACY_WINDOW_KEYS})
            old = api.seal_profile(body)
            old_registry[old['id']] = old
        self.assertEqual(api.build_profiles(CONFIG)['execution_profiles'], old_registry)
        chosen = model_policy.selection(CONFIG, {'role': 'operational_review'}, {}, {}, profiles=old_registry)
        profile = old_registry[chosen['profile_ref']['id']]
        self.assertEqual(api.profile_ref(profile), chosen['profile_ref'])
        self.assertNotIn('run_timeout_seconds', api.runtime_config(profile))
        self.assertNotIn('dispatch_reserve_seconds', api.runtime_config(profile))

    def test_selection_is_pinned_and_contract_allowlist_is_enforced(self):
        api = self.profiles()
        state = api.build_profiles(CONFIG)
        action = {"role": "research_work", "model_assessment": {
            "difficulty": "low", "importance": "low", "reason": "bounded arithmetic"}}
        selected = model_policy.selection(CONFIG, action, {}, {}, profiles=state["execution_profiles"])
        profile = api.resolve_profile(state["execution_profiles"], selected["profile_ref"])
        frozen = api.runtime_config(profile)
        config = deepcopy(CONFIG)
        config["max_input_bytes"] = 1
        self.assertEqual(frozen["max_input_bytes"], 500000)
        with self.assertRaises(ValueError):
            api.select_profile(state["execution_profiles"], action, selected, allowed_refs=[])
        self.assertEqual(api.select_profile(state["execution_profiles"], action, selected,
                         allowed_refs=[profile["id"]])["id"], profile["id"])
        broken = deepcopy(state["execution_profiles"])
        broken[profile["id"]]["ai"]["model"] = "different"
        with self.assertRaises(ValueError):
            api.resolve_profile(broken, selected["profile_ref"])
        changed = {**deepcopy(CONFIG), "max_input_bytes": 400000}
        editions = api.build_profiles(changed)
        registry = {**state["execution_profiles"], **editions["execution_profiles"]}
        newest = model_policy.selection(changed, action, {}, {}, profiles=registry)
        self.assertIn(newest["profile_ref"]["id"], editions["execution_profiles"])

    def test_modes_machine_fields_and_profile_rebinding(self):
        api = self.profiles()
        profiles = api.build_profiles(CONFIG)["execution_profiles"]
        mode = {p["role"]: p["observation"]["mode"] for p in profiles.values()}
        self.assertEqual(mode["research_work"], "event_driven")
        self.assertEqual(mode["identity_review"], "periodic")
        self.assertEqual(mode["operational_review"], "deadline_only")
        machine = next(p for p in profiles.values() if p["role"] == "formal_check")
        self.assertNotIn("ai", machine)
        execution = {"id": "EX-one", "role": "formal_check"}
        api.bind_execution(execution, machine)
        self.assertIn("execution_profile_ref", execution)
        other = next(p for p in profiles.values() if p["role"] == "trust_check")
        with self.assertRaises(ValueError):
            api.bind_execution(execution, other)

    def test_research_profile_binds_all_implemented_signal_kinds_not_counter_names(self):
        from do_math.observations import observation_rule_contract, tracker_config
        api = self.profiles()
        profile = next(p for p in api.build_profiles({**CONFIG, "tool_review_window_seconds": 60,
                       "self_check_response_window_seconds": 60})["execution_profiles"].values()
                       if p["role"] == "research_work")
        rule = {"id": "SC-attempts", "operator": "counter_gte",
                "subject": {"kind": "counter", "id": "attempts"},
                "basis": {"source": "checkpoint", "unit": "count"}, "threshold": 1,
                "required_evidence": ["checkpoint.json"]}
        config = tracker_config(profile, initial_self_check_rules=[rule])
        self.assertEqual(config["observation_rule_bindings"], observation_rule_contract())

    def test_git_admission_all_or_nothing_and_unknown_release(self):
        api = self.profiles()
        from do_math.session_slots import GitSessionSlots
        instance = api.build_profiles(CONFIG)
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        profile = next(p for p in instance["execution_profiles"].values()
                       if p["role"] == "research_work" and p["ai"]["model"] == CONFIG["tier_models"]["low"])
        slots = GitSessionSlots(runtime, instance)
        for i in range(3):
            self.assertTrue(slots.acquire(f"EX-{i}", "work", profile["ai"]["model"],
                            profile=profile, execution={"id": f"EX-{i}", "role": "research_work"}))
        from do_math.state_contract import STATE_FORMAT_VERSION
        self.assertTrue(all(r["schema_version"] == STATE_FORMAT_VERSION for r in runtime["reservations"].values()))
        before = deepcopy(runtime)
        self.assertFalse(slots.acquire("EX-over", "work", profile["ai"]["model"],
                         profile=profile, execution={"id": "EX-over", "role": "research_work"}))
        self.assertEqual(runtime, before)
        slots.started("EX-0", {"job_name": "test-job", "pid": 1})
        with patch("do_math.windows_job.named_job_empty", return_value=None):
            self.assertFalse(slots.release("EX-0"))
        self.assertEqual(slots.snapshot()["work"][profile["ai"]["model"]]["used"], 3)
        with patch("do_math.windows_job.named_job_empty", return_value=True):
            self.assertTrue(slots.release("EX-0"))
            self.assertTrue(slots.release("EX-0"))
        self.assertEqual(slots.snapshot()["work"][profile["ai"]["model"]]["used"], 2)
        operation = next(p for p in instance["execution_profiles"].values()
                         if p["role"] == "maintenance" and p["ai"]["model"] == profile["ai"]["model"])
        self.assertTrue(slots.acquire("EX-op", "operations", operation["ai"]["model"],
                        profile=operation, execution={"id": "EX-op", "role": "maintenance"}))

    def test_admission_accepts_registered_queued_execution_exactly_once(self):
        from do_math.session_slots import GitSessionSlots
        api = self.profiles()
        instance = api.build_profiles(CONFIG)
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        execution = {"id": "EX-registered", "role": "research_work", "status": "queued",
                     "execution_profile_ref": api.profile_ref(profile), "owner_activity_id": "AY-one"}
        runtime = {"executions": {execution["id"]: execution}, "reservations": {}}
        slots = GitSessionSlots(runtime, instance)
        self.assertTrue(slots.acquire(execution["id"], "work", profile["ai"]["model"], profile=profile, execution=execution))
        self.assertIs(runtime["executions"][execution["id"]], execution)
        self.assertEqual(execution["owner_activity_id"], "AY-one")
        before = deepcopy(runtime)
        with self.assertRaises(ValueError):
            slots.acquire(execution["id"], "work", profile["ai"]["model"], profile=profile, execution=execution)
        self.assertEqual(runtime, before)

    def test_supervisor_does_not_call_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(scheduled_operator, "read_status", return_value={"status": "ready"}), \
                 patch.object(scheduled_operator, "ResearchRepository") as repository, \
                 patch("do_math.submission.install_tools", return_value={}), \
                 patch.object(scheduled_operator, "reconcile_wake", return_value={"status": "not_needed"}), \
                 patch.object(scheduled_operator, "schedule", return_value={"state": "Running"}), \
                 patch.object(scheduled_operator.ModelRunner, "run", side_effect=AssertionError("normal supervision called AI")):
                repository.return_value.load.return_value = ("head", {"config": CONFIG}, {})
                result = scheduled_operator.check(root, "instance", root)
            self.assertEqual(result["outcome"], "engine_requested")

    def test_runner_pins_request_and_exposes_reported_evidence(self):
        from test_model_runner import Adapter
        from do_math.model_runner import CodexModelRunner
        import inspect
        self.assertIn("profile", inspect.signature(CodexModelRunner.run).parameters)
        api = self.profiles()
        profile = next(p for p in api.build_profiles(CONFIG)["execution_profiles"].values()
                       if p["role"] == "research_work")
        adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'},
                           "jsonl": {"usage_total": {"output_tokens": 3}, "stop_reason": "end_turn"}})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner = CodexModelRunner("fake")
            runner._adapter = adapter
            result = runner.run(prompt=api.prepare_prompt("test", profile), input_seal=api.prompt_seal(api.prepare_prompt("test", profile)), output_schema={}, workspace=root,
                evidence_dir=root / "evidence", model=profile["ai"]["model"], effort=profile["ai"]["effort"],
                timeout_seconds=600, execution_id="EX-bound", profile=profile)
            self.assertEqual(adapter.request["execution_id"], "EX-bound")
            self.assertEqual(adapter.request["profile_ref"], api.profile_ref(profile))
            self.assertEqual(result["provider_observation"]["stop_reason"], "end_turn")
            self.assertEqual(result["provider_observation"]["remote_termination"], "unknown")
            self.assertEqual(result["provider_observation"]["usage_scope"], "reported_execution_counters_not_invoice")
            self.assertEqual(result["execution_id"], "EX-bound")

    def test_issued_workspace_binding_reaches_both_runners_and_worker_contracts(self):
        from do_math.control_transport import ControlTransport
        from do_math import codex_worker, claude_worker
        from do_math.model_runner import CodexModelRunner, ClaudeModelRunner
        from test_model_runner import Adapter
        api = self.profiles()
        for runner_type, worker, model in ((CodexModelRunner, codex_worker, 'gpt-6-astra'),
                                          (ClaudeModelRunner, claude_worker, 'claude-opus-5')):
            with self.subTest(provider=model), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / 'workspace'; workspace.mkdir()
                config = {**CONFIG, 'tier_models': {tier: model for tier in ('high', 'medium', 'low')},
                          'session_limits': {pool: {model: 3} for pool in ('work', 'operations')}}
                profile = next(p for p in api.build_profiles(config)['execution_profiles'].values()
                               if p['role'] == 'research_work')
                binding = ControlTransport(root / 'transport').issue('EX-bound', 'GR-bound', workspace=workspace)
                runner = runner_type('fixture-cli')
                runner._adapter = Adapter({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}})
                prompt = api.prepare_prompt('test', profile)
                options = dict(prompt=prompt, input_seal=api.prompt_seal(prompt), output_schema={},
                    workspace=workspace, model=model, effort=profile['ai']['effort'], timeout_seconds=60,
                    execution_id='EX-bound', profile=profile)
                runner.run(**options, evidence_dir=root / 'evidence', control_binding=binding)
                request_path = root / 'evidence/request.json'
                request = worker.load_request(request_path)
                self.assertEqual(request['control_binding'], binding)
                self.assertIn('--workspace=' + str(workspace.resolve()),
                              ControlTransport.mcp_server_config(binding)['args'])
                self.assertTrue(worker.build_argv(request))
                variants = [dict(binding, unexpected='reject'), dict(binding, execution_id='EX-other'),
                            dict(binding, endpoint='relative'), dict(binding, workspace='relative'),
                            dict(binding, workspace=''), dict(binding, workspace=None),
                            dict(binding, workspace=str(root / 'other'))]
                for index, invalid in enumerate(variants):
                    with self.subTest(invalid=index):
                        request_path.write_text(json.dumps({**request, 'control_binding': invalid}), encoding='utf-8')
                        with self.assertRaises(ValueError): worker.load_request(request_path)
                        with self.assertRaises(ValueError):
                            runner.run(**options, evidence_dir=root / ('invalid-' + str(index)), control_binding=invalid)
                        self.assertFalse((root / ('invalid-' + str(index))).exists())

    def test_workers_validate_execution_binding(self):
        from do_math import codex_worker
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = {"codex_path": "codex", "prompt_path": "input.txt", "cwd": str(root),
                "model": "model", "effort": "medium", "approval_policy": "never", "sandbox": "danger-full-access",
                "max_runtime_seconds": 60, "stdout_path": "out", "stderr_path": "err", "final_path": "final",
                "status_path": "status", "execution_id": "EX-bound",
                "profile_ref": {"id": "EP-x", "revision": 1, "sha256": "a" * 64}}
            path = root / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            try:
                loaded = codex_worker.load_request(path)
            except ValueError as error:
                self.fail("worker rejects execution/profile binding: " + str(error))
            self.assertEqual(loaded["execution_id"], "EX-bound")
            del request["execution_id"]
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaises(ValueError):
                codex_worker.load_request(path)

    def test_provider_wait_is_canonical_and_serializes_retry_probe(self):
        api = self.profiles()
        from do_math.session_slots import GitSessionSlots
        from do_math.repository import canonical_json
        instance = api.build_profiles(CONFIG)
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        slots = GitSessionSlots(runtime, instance)
        admit = lambda eid, t: slots.acquire(eid, "work", profile["ai"]["model"], profile=profile,
                         execution={"id": eid, "role": "research_work"}, current_time=t)
        self.assertTrue(admit("EX-failure", 10))
        failure = {"kind": "provider_limit", "provider": profile["ai"]["provider"],
                   "retry_at": "1970-01-01T00:00:20+00:00", "evidence_ref": "stdout.jsonl"}
        slots.provider_result("EX-failure", profile["ai"]["provider"], failure=failure, current_time=10.5)
        self.assertTrue(all(key == row["id"] for key, row in runtime["provider_waits"].items()),
                        "provider gates must persist as individual family records")
        try:
            canonical_json(runtime)
        except ValueError as error:
            self.fail("Git reservation path emits noncanonical state: " + str(error))
        self.assertFalse(admit("EX-too-early", 19))
        self.assertTrue(admit("EX-probe", 21))
        self.assertFalse(admit("EX-concurrent-probe", 21))
        slots.provider_result("EX-probe", profile["ai"]["provider"], response_observed=True, current_time=22)
        self.assertTrue(admit("EX-after", 22))

    def test_capability_identity_has_host_worker_and_cli_hashes(self):
        from do_math.codex_adapter import CodexExecAdapter
        self.assertTrue(hasattr(CodexExecAdapter, "capability_identity"), "adapter evidence is not bound to host/implementation")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cli.exe"
            path.write_bytes(b"first")
            adapter = CodexExecAdapter(str(path))
            first = adapter.capability_identity()
            self.assertIn("windows_job_sha256", first)
            path.write_bytes(b"second")
            second = adapter.capability_identity()
            self.assertNotEqual(first["cli_sha256"], second["cli_sha256"])
            self.assertEqual(first["worker_sha256"], second["worker_sha256"])
            self.assertIn("host", first)

    def test_git_publication_and_recovery_exclude_engine_writer(self):
        import subprocess
        from do_math.repository import ResearchRepository
        from do_math.session_slots import GitSessionSlots
        api = self.profiles()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            iid = "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"
            repository = ResearchRepository(root, iid)
            api.register_families(repository.contract)
            instance = {**api.build_profiles(CONFIG), "feature_version": 5, "id": iid,
                        "config": CONFIG, "workspace": str(root)}
            runtime = {"feature_version": 5, "status": "ready", "executions": {}, "reservations": {}, "provider_waits": {}}
            head = repository.initialize(instance, runtime)
            failure = {"kind": "engine_unavailable", "error": "installation test failure"}
            with repository.writer_lock(), patch.object(scheduled_operator.ModelRunner, "run") as runner:
                self.assertEqual(scheduled_operator.recovery(root, iid, root, failure=failure)["outcome"], "engine_running")
                runner.assert_not_called()
            with patch.object(scheduled_operator.ModelRunner, "run", return_value={"status": "failed", "error": "fixture"}), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()):
                result = scheduled_operator.recovery(root, iid, root, failure=failure)
            self.assertEqual(result["outcome"], "recovery_failed")
            new_head, instance, runtime = repository.load()
            self.assertNotEqual(head, new_head)
            execution = runtime["executions"][result["execution_id"]]
            self.assertEqual(execution["role"], "recovery")
            self.assertEqual(execution["status"], "ended")
            self.assertEqual(execution["error"], "fixture")
            self.assertEqual(execution["input_manifest"]["repair_authority"]["source"], "adopted_operator_repair_scope")
            self.assertTrue(all(row["state"] == "settled" for row in runtime["reservations"].values()))
            self.assertFalse((root / "session-slots").exists())
            self.assertTrue(any("execution_profiles/EP-" in p for p in repository.list_files("research/", new_head)))
            prior_activity = execution["owner_activity_id"]
            with patch.object(scheduled_operator.ModelRunner, 'run') as duplicate:
                held = scheduled_operator.recovery(root, iid, root, failure=failure)
            self.assertEqual(held['reason'], 'same failure and installation already attempted')
            duplicate.assert_not_called()
            real_run = subprocess.run
            def verification(command, **options):
                if len(command) > 1 and Path(command[1]).name == "probe_cli.py":
                    return subprocess.CompletedProcess(command, 0, "verified", "")
                return real_run(command, **options)
            def repaired(**arguments):
                _, _, published = repository.load()
                self.assertEqual(published["executions"][arguments["execution_id"]]["status"], "starting")
                self.assertIn("Do not change research records, goals, budgets, grants", arguments["prompt"])
                from do_math.git_store import GitStateStoreLockError
                with self.assertRaises(GitStateStoreLockError), repository.writer_lock():
                    self.fail("recovery model ran without excluding the engine")
                arguments["on_started"]({"job_name": "fixture-job", "pid": 17})
                _, _, published = repository.load()
                self.assertEqual(published["executions"][arguments["execution_id"]]["capacity"]["process"]["pid"], 17)
                return {"status": "completed", "output": {"summary": "fixture repair", "observed_status": "ready",
                    "actions": [], "evidence_paths": [], "user_questions": [], "next_step": "launcher verification"}}
            def restart(*args):
                from do_math.session_slots import _lock, _unlock
                with repository.writer_lock():
                    maintenance = _lock(repository._store._git_dir / "do-math-installation-maintenance.lock")
                    self.assertIsNotNone(maintenance, "restart still owns the maintenance lock")
                    _unlock(maintenance)
                    _, _, published = repository.load()
                    self.assertTrue(all(r["state"] == "settled" for r in published["reservations"].values()))
                return {"outcome": "engine_requested"}
            with patch.object(scheduled_operator.ModelRunner, "run", side_effect=repaired), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()), \
                 patch('do_math.repair_execution.installation_fingerprint', return_value='b' * 64), \
                 patch.object(scheduled_operator.subprocess, "run", side_effect=verification), \
                 patch.object(scheduled_operator, "wake", side_effect=restart), \
                 patch("do_math.windows_job.named_job_empty", return_value=True):
                result = scheduled_operator.recovery(root, iid, root, failure=failure)
            self.assertEqual(result["outcome"], "repaired")
            _, _, runtime = repository.load()
            execution = runtime["executions"][result["execution_id"]]
            self.assertEqual(execution["outcome"], "output_accepted")
            self.assertEqual(execution["owner_activity_id"], prior_activity)
            self.assertEqual(len(runtime["activities"][prior_activity]["assigned_execution_ids"]), 2)
            self.assertEqual(runtime["activities"][prior_activity]["status"], "finished")

    def test_recovery_never_restarts_with_unknown_local_termination(self):
        from contextlib import nullcontext
        from unittest.mock import Mock
        import subprocess
        api = self.profiles()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance = {**api.build_profiles(CONFIG), "config": CONFIG}
            runtime = {"executions": {}, "reservations": {}, "activities": {}, "status": "ready"}
            repo = Mock()
            repo.writer_lock.return_value = nullcontext()
            repo.load.return_value = ("head", instance, runtime)
            repo.save.return_value = "published"
            repo._store._git_dir = root
            def model(**arguments):
                self.assertEqual(arguments.get("input_seal"), api.prompt_seal(arguments["prompt"]))
                sealed = runtime["executions"][arguments["execution_id"]]["input_manifest"]["prompt"]
                self.assertEqual(sealed, arguments["input_seal"])
                raw_prompt = arguments["prompt"].split(api.boundary_prompt(arguments["profile"]))[0]
                self.assertEqual(json.loads(raw_prompt.rsplit("\n", 1)[1])["installation"],
                                 str(root / "live-installation"))
                arguments["on_started"]({"job_name": "still-unknown", "pid": 42})
                return {"status": "completed", "output": {"summary": "report is not termination evidence"}}
            with patch.object(scheduled_operator, "ResearchRepository", return_value=repo), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()), \
                 patch.object(scheduled_operator, "LIVE_INSTALLATION_ROOT", root / "live-installation", create=True), \
                 patch.object(scheduled_operator, "register_profile_families"), \
                 patch.object(scheduled_operator.ModelRunner, "run", side_effect=model), \
                 patch.object(scheduled_operator.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "ok", "")) as verify, \
                 patch("do_math.windows_job.named_job_empty", return_value=None), \
                 patch.object(scheduled_operator, "wake") as wake:
                result = scheduled_operator.recovery(root, "test", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})
            wake.assert_not_called()
            self.assertEqual(result["outcome"], "recovery_termination_unknown")
            self.assertEqual(Path(verify.call_args.args[0][1]), root / "live-installation/scripts/probe_cli.py")
            self.assertTrue(all(r["state"] == "held" for r in runtime["reservations"].values()))

    def test_recovery_requires_current_profile_capability_before_reservation(self):
        from contextlib import nullcontext
        from unittest.mock import Mock
        api = self.profiles()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance = {**api.build_profiles(CONFIG), "config": CONFIG}
            runtime = {"executions": {}, "reservations": {}, "status": "ready"}
            repo = Mock()
            repo.writer_lock.return_value = nullcontext()
            repo.load.return_value = ("head", instance, runtime)
            repo.save.return_value = "capability-published"
            repo._store._git_dir = root
            with patch.object(scheduled_operator, "ResearchRepository", return_value=repo), \
                 patch.object(scheduled_operator, "register_profile_families"), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter(supported=False)), \
                 patch.object(scheduled_operator.ModelRunner, "run") as runner:
                result = scheduled_operator.recovery(root, "test", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})
            self.assertEqual(result["outcome"], "recovery_waiting")
            self.assertEqual(result["reason"], "profile_capability_unavailable")
            runner.assert_not_called()
            self.assertFalse(runtime["reservations"])
            evidence = next(iter(instance["capability_evidence"].values()))
            self.assertEqual(evidence["capabilities"]["structured_output"]["status"], "unsupported")

    def test_recovery_cannot_ignore_hold_or_unknown_live_job(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduled_operator.hold(root, reason="test")
            with patch.object(scheduled_operator.ModelRunner, "run") as runner:
                self.assertEqual(scheduled_operator.recovery(root, "unused", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})["outcome"], "held")
                runner.assert_not_called()

    def test_supervisor_has_engine_independent_launcher(self):
        import subprocess
        result = subprocess.run([sys.executable, str(Path(scheduled_operator.__file__)), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--instance", result.stdout)

    def test_capability_evidence_does_not_promote_surface_to_job_proof(self):
        api = self.profiles()
        self.assertTrue(hasattr(api, "capability_evidence"), "profile capability evidence has no independent record")
        profile = next(p for p in api.build_profiles(CONFIG)["execution_profiles"].values() if p["actor_kind"] == "ai")
        description = {"scope": "cli_command_surface_only", "verified": True,
            "identity": {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "test"}},
            "supported": {"jsonl": True, "model": True, "local_job_stop": True},
            "unknown": ["remote_termination"], "version_sha256": "c" * 64, "exec_help_sha256": "d" * 64}
        evidence = api.capability_evidence(profile, description, observed_at="2026-09-20T00:00:00Z")
        self.assertEqual(evidence["execution_profile_ref"], api.profile_ref(profile))
        self.assertEqual(evidence["capabilities"]["jsonl"]["status"], "supported")
        self.assertEqual(evidence["capabilities"]["local_job_stop"]["status"], "unknown")
        self.assertEqual(evidence["capabilities"]["remote_termination"]["status"], "unknown")

    def test_unsupported_job_is_a_profile_failure_not_an_ordinary_retry(self):
        from do_math.model_runner import CodexModelRunner
        from do_math.windows_job import WindowsJobUnsupportedError
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as directory:
            runner = CodexModelRunner("fake")
            runner._adapter = Mock()
            runner._adapter.start.side_effect = WindowsJobUnsupportedError("atomic admission unsupported")
            try:
                result = runner.run(prompt="test", output_schema={}, workspace=Path(directory),
                    evidence_dir=Path(directory) / "evidence", model="test", effort="low", timeout_seconds=1)
            except WindowsJobUnsupportedError:
                self.fail("structural unsupported capability was not classified for the profile gate")
            self.assertEqual(result["error_kind"], "profile_unsupported")
            self.assertEqual(result["capability_failure"]["capability"], "atomic_local_job")


class Audit1Tests(unittest.TestCase):
    def profiles(self, **changes):
        from do_math import execution_profiles as ep
        return ep, ep.build_profiles({**CONFIG, "lean_command": ["lean-A"], "lean_timeout_seconds": 10, **changes})

    def test_machine_profile_changes_with_command_deadline_and_tool_bytes(self):
        ep, a = self.profiles()
        _, b = self.profiles(lean_command=["lean-B"], lean_timeout_seconds=999)
        def formal(state):
            return next(p for p in state["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertNotEqual(ep.profile_ref(formal(a)), ep.profile_ref(formal(b)))
        self.assertTrue(hasattr(ep, "machine_invocation"), "machine invocation has no profile consumer")
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "lean.exe"
            tool.write_bytes(b"edition one")
            _, first = self.profiles(lean_command=[str(tool)])
            p = formal(first)
            env = {"toolchain": {"configured_command": [str(tool)], "version": "fixture"}}
            args = ep.machine_invocation(p, trust_environment=env)
            self.assertIsNone(args["timeout_seconds"])
            self.assertEqual(args["lean_command"], [str(tool)])
            self.assertEqual(args["expected_toolchain"], env["toolchain"])
            tool.write_bytes(b"edition two")
            _, second = self.profiles(lean_command=[str(tool)])
            self.assertNotEqual(ep.profile_ref(p), ep.profile_ref(formal(second)))
            with self.assertRaisesRegex(ValueError, "tool.*changed"):
                ep.machine_invocation(p, trust_environment=env)
            with self.assertRaises(ValueError):
                ep.machine_invocation(formal(second), trust_environment={"toolchain": {"configured_command": ["different"]}})

    def test_machine_command_alias_keeps_adopted_argv_and_checks_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "lean.exe"; tool.write_bytes(b"edition")
            with patch("do_math.execution_profiles.shutil.which", return_value=str(tool)):
                ep, state = self.profiles(lean_command=["lean"])
                p = next(p for p in state["execution_profiles"].values() if p["role"] == "formal_check")
                args = ep.machine_invocation(p, trust_environment={"toolchain": {"configured_command": ["lean"]}})
                self.assertEqual(args["lean_command"], ["lean"])
            other = Path(directory) / "other.exe"; other.write_bytes(b"edition")
            with patch("do_math.execution_profiles.shutil.which", return_value=str(other)):
                with self.assertRaisesRegex(ValueError, "tool.*changed"):
                    ep.machine_invocation(p, trust_environment={"toolchain": {"configured_command": ["lean"]}})


    def test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist(self):
        ep, old = self.profiles()
        profile = next(p for p in old["execution_profiles"].values()
                       if p["role"] == "intent_interpretation" and p["ai"]["tier"] == "high")
        changed = deepcopy(CONFIG)
        changed["tier_models"]["high"] = "replacement-model"
        selected = model_policy.selection(changed, {"role": "intent_interpretation", "profile_ref": ep.profile_ref(profile)}, {}, {},
                                          profiles=old["execution_profiles"])
        self.assertEqual(selected["model"], profile["ai"]["model"])
        low = next(p for p in old["execution_profiles"].values()
                   if p["role"] == "intent_interpretation" and p["ai"]["tier"] == "low")
        with self.assertRaises(ValueError):
            model_policy.selection(CONFIG, {"role": "intent_interpretation", "profile_ref": ep.profile_ref(low)}, {}, {}, profiles=old["execution_profiles"])
        # Task allowlists govern work, while interpretation keeps its own profile.
        model_policy.selection(CONFIG, {"role": "intent_interpretation", "target": "T", "profile_ref": ep.profile_ref(profile)},
                               {"T": {"profile_refs": []}}, {}, profiles=old["execution_profiles"])
        work = next(p for p in old["execution_profiles"].values()
                    if p["role"] == "research_work" and p["ai"]["tier"] == "high")
        with self.assertRaises(ValueError):
            model_policy.selection(CONFIG, {"role": "research_work", "target": "T", "profile_ref": ep.profile_ref(work)},
                                   {"T": {"profile_refs": []}}, {}, profiles=old["execution_profiles"])

    def test_runner_preserves_exact_utf8_input_after_seal(self):
        from do_math.model_runner import CodexModelRunner
        from test_model_runner import Adapter
        import hashlib
        ep, registry = self.profiles()
        p = next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance")
        text = "exact input\n한글\n" + ep.boundary_prompt(p)
        seal = {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner = CodexModelRunner("not-called")
            runner._adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}})
            kwargs = dict(prompt=text, output_schema={}, workspace=root, evidence_dir=root / "evidence",
                model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1, execution_id="EX-exact", profile=p)
            kwargs["input_seal"] = seal
            runner.run(**kwargs)
            self.assertEqual((root / "evidence/input.txt").read_bytes(), text.encode("utf-8"))
            kwargs.update(evidence_dir=root / "changed", prompt=text + "extra", input_seal=seal)
            with self.assertRaisesRegex(ValueError, "seal"):
                runner.run(**kwargs)
            self.assertFalse((root / "changed").exists())
            kwargs.update(prompt=text, evidence_dir=root / "missing")
            kwargs.pop("input_seal")
            with self.assertRaisesRegex(ValueError, "seal"):
                runner.run(**kwargs)

    def test_profile_tools_are_authoritative_and_detached(self):
        ep, registry = self.profiles(scholarly_server={"command": "approved-old-server", "args": []})
        self.assertTrue(hasattr(ep, "runner_tools"), "no pinned tool argument API")
        p = next(p for p in registry["execution_profiles"].values() if p["actor_kind"] == "ai")
        args = ep.runner_tools(p)
        self.assertEqual(args["scholarly_server"]["command"], "approved-old-server")
        args["scholarly_server"]["command"] = "mutated"
        self.assertEqual(ep.runner_tools(p)["scholarly_server"]["command"], "approved-old-server")

    def test_structural_failure_emits_identity_bound_negative_evidence(self):
        from do_math.model_runner import CodexModelRunner
        from do_math.windows_job import WindowsJobUnsupportedError
        from unittest.mock import Mock
        import hashlib
        ep, registry = self.profiles()
        p = next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance")
        identity = {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "observed"}}
        runner = CodexModelRunner("not-called")
        runner._adapter = Mock()
        runner._adapter.capability_identity.return_value = identity
        runner._adapter.start.side_effect = WindowsJobUnsupportedError("fixture structural failure")
        prompt = "input" + ep.boundary_prompt(p)
        with tempfile.TemporaryDirectory() as directory:
            kwargs = dict(prompt=prompt, output_schema={}, workspace=Path(directory), evidence_dir=Path(directory)/"evidence",
                model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1, execution_id="EX-failure", profile=p)
            kwargs["input_seal"] = ep.prompt_seal(prompt)
            result = runner.run(**kwargs)
        self.assertIn("capability_evidence", result)
        evidence = result["capability_evidence"]
        self.assertEqual(evidence["identity"], identity)
        self.assertEqual(evidence["execution_profile_ref"], ep.profile_ref(p))
        self.assertEqual(evidence["capabilities"]["atomic_local_job"]["status"], "unsupported")
        self.assertEqual(evidence["id"], "CE-" + ep._digest({k: v for k, v in evidence.items() if k != "id"}))

    def test_negative_job_fact_vetoes_next_matching_assignment(self):
        from do_math.initialization import capability_requirements
        ep, state = self.profiles()
        p = next(p for p in state["execution_profiles"].values() if p["role"] == "maintenance")
        identity = {"host": {"node": "one"}, "cli_sha256": "a" * 64}
        positive = ep.capability_evidence(p, {"identity": identity, "verified": True,
            "scope": "cli_command_surface_only", "supported": {"jsonl": True, "model": True, "structured_output": True}},
            observed_at="2026-09-20T00:00:00Z")
        negative = ep.structural_failure_evidence(p, identity, observed_at="2026-09-20T00:00:01Z",
            execution_id="EX-failed", evidence_ref="failure.json")
        state["capability_evidence"] = {r["id"]: r for r in (positive, negative)}
        current = capability_requirements(state, ep.profile_ref(p), current_identity=identity, at="2026-09-20T00:00:02Z")
        self.assertFalse(current["satisfied"], "actual structural failure did not block the next identical assignment")
        changed = {"host": {"node": "two"}, "cli_sha256": "a" * 64}
        other = ep.capability_evidence(p, {"identity": changed, "verified": True,
            "scope": "cli_command_surface_only", "supported": {"jsonl": True, "model": True, "structured_output": True}},
            observed_at="2026-09-20T00:00:02Z")
        state["capability_evidence"][other["id"]] = other
        self.assertTrue(capability_requirements(state, ep.profile_ref(p), current_identity=changed,
                        at="2026-09-20T00:00:03Z")["satisfied"], "failure was generalized to a different host")


    def test_native_claude_report_reaches_normal_result_without_scope_expansion(self):
        import hashlib
        from do_math.claude_adapter import ClaudePrintAdapter
        from do_math.codex_adapter import CodexExecution
        from do_math.windows_job import JobInspection
        from test_codex_adapter import _FakeJob
        from test_claude_adapter import stream, INIT, RESULT
        from test_model_runner import Adapter
        from do_math.model_runner import ClaudeModelRunner
        ep, registry = self.profiles()
        p = deepcopy(next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance"))
        p["ai"].update(model="claude:haiku", provider="claude")
        p = ep.seal_profile(p)
        prompt = ep.prepare_prompt("sealed native report fixture", p)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, source, stdout, stderr, final, status = [root/name for name in ("request", "input", "stdout", "stderr", "final", "status")]
            request.write_bytes(json.dumps({"execution_id": "EX-native", "profile_ref": ep.profile_ref(p)}).encode())
            source.write_bytes(prompt.encode())
            native = {**RESULT, "stop_reason": "max_tokens", "modelUsage": {"haiku": {"costUSD": 0.125}}, "total_cost_usd": 0.125}
            stdout.write_bytes(stream(INIT, native)); stderr.write_bytes(b""); final.write_bytes(b'{"ok":true}')
            request_hash = hashlib.sha256(request.read_bytes()).hexdigest()
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            status.write_bytes(json.dumps({"state": "exited", "cli_exit_code": 0, "stdin_sha256": source_hash,
                "request_sha256": request_hash, "schema_sha256": None, "execution_id": "EX-native", "profile_ref": ep.profile_ref(p)}).encode())
            ex = CodexExecution(request, source, request_hash, source_hash, ("worker",), stdout, stderr, final, status,
                                _FakeJob(JobInspection(0, (), True)), root, None)
            collected = ClaudePrintAdapter("not-launched").collect(ex)
            self.assertEqual(collected["result"], "output_collected", collected["reasons"])
            runner = ClaudeModelRunner("not-launched"); runner._adapter = Adapter(collected)
            result = runner.run(prompt=prompt, input_seal=ep.prompt_seal(prompt), output_schema={}, workspace=root,
                evidence_dir=root/"runner", model="haiku", effort=p["ai"]["effort"], timeout_seconds=1,
                profile=p, execution_id="EX-native")
            self.assertEqual(result["status"], "completed")
            stored = ep.execution_observation(result)
            reported = json.loads(stored["reported_fields_json"])
            self.assertEqual(stored["stop_reason"], "max_tokens")
            self.assertEqual(reported["usage"], native["usage"])
            self.assertEqual(reported["model_usage_reported"], native["modelUsage"])
            self.assertEqual(reported["operation_count"], "unknown")
            self.assertEqual(reported["remote_termination"], "unknown")
            self.assertEqual(reported["evidence_sha256"], hashlib.sha256(stdout.read_bytes()).hexdigest())


    def test_surface_seal_and_runner_deliver_identical_complete_input(self):
        from test_redesign_SURFACE import surface_state
        from do_math.context_store import prepare_role_input
        from do_math.model_runner import CodexModelRunner
        from test_model_runner import Adapter
        from do_math import execution_profiles as ep
        from do_math.contracts import schema_for
        schema = schema_for("research_preparation")
        state, runtime = surface_state()
        p = next(p for p in state["execution_profiles"].values() if p["role"] == "research_preparation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({"action": {}, "resources": {}, 'knowledge_catalog': []}, instance=state, runtime=runtime,
                role="research_preparation", profile=p, snapshot="a"*40, workspace=root, activity_id="AC-1",
                output_schema=schema, artifact_prefix="runtime/artifacts/EX-seal")
            self.assertIsNone(fitted["overflow"])
            prompt = fitted["prompt"]
            self.assertEqual(prompt.count(ep.boundary_prompt(p)), 1)
            expected = ep.prompt_seal(prompt)
            self.assertEqual({k: fitted["manifest"]["prompt"][k] for k in expected}, expected)
            runner = CodexModelRunner("not-launched"); runner._adapter = Adapter({"result":"output_collected", "final":{"raw":b'{}'}, "jsonl":{}})
            runner.run(prompt=prompt, input_seal=fitted["manifest"]["prompt"], output_schema=schema, workspace=root,
                evidence_dir=root/"evidence", model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1,
                execution_id="EX-seal", profile=p)
            self.assertEqual((root/"evidence/input.txt").read_bytes(),
                             fitted["artifacts"][fitted["manifest"]["prompt"]["artifact_ref"]])


    def test_native_provider_observation_has_canonical_storage_projection(self):
        from do_math import execution_profiles as ep
        from do_math.repository import canonical_json
        self.assertTrue(hasattr(ep, "execution_observation"), "no canonical observation projection")
        observation = {"stop_reason": "max_tokens", "usage": {"input_tokens": 4, "cost_usd": 0.125},
                       "operation_count": "unknown", "remote_termination": "unknown"}
        stored = ep.execution_observation({"provider_observation": observation})
        canonical_json(stored)
        self.assertEqual(json.loads(stored["reported_fields_json"]), observation)
        self.assertEqual(stored["stop_reason"], "max_tokens")
        self.assertIsNone(ep.execution_observation({}))


if __name__ == "__main__":
    unittest.main()
