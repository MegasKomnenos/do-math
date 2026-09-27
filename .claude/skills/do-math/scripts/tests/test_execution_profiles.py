"""Execution profiles: pinning and selection, admission atomicity, resource waits and observed provider evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash
from research_fixtures import dispatched_launch
from do_math import execution_profiles, model_policy
from provider_fixtures import PROFILE_CONFIG
from do_math.configuration import DEFAULT_CONFIG
from do_math.session_slots import SessionSlots


class ProfileTests(unittest.TestCase):

    def test_selection_cost_depends_on_allowed_profiles_not_retained_editions(self):
        registry = {}
        for edition in range(12):
            config = {**deepcopy(PROFILE_CONFIG), "max_input_bytes": 500000 + edition,
                      "lean_command": ["fixture-no-lean"]}
            current = execution_profiles.build_profiles(config)
            registry.update(current["execution_profiles"])
        allowed = current["role_profile_refs"]["maintenance"]
        instance = {"execution_profiles": registry, "role_profile_refs": current["role_profile_refs"]}
        before = deepcopy(registry)
        with patch.object(execution_profiles, "match_profile_ref", wraps=execution_profiles.match_profile_ref) as resolve:
            chosen = model_policy.selection(config, {"role": "maintenance"}, {}, {}, instance=instance)
        self.assertIn(chosen["profile_ref"], allowed)
        self.assertLessEqual(resolve.call_count, 2 * len(allowed))
        self.assertEqual(registry, before)

        requirement = {key: chosen[key] for key in ("model", "tier")}
        selected = execution_profiles.select_profile(registry, {"role": "maintenance"}, requirement,
                                      allowed_refs=[*allowed, allowed[0]])
        self.assertEqual(execution_profiles.profile_ref(selected), chosen["profile_ref"])
        with self.assertRaisesRegex(ValueError, "permitted role/model edition"):
            execution_profiles.select_profile(registry, {"role": "maintenance"}, requirement, allowed_refs=[])
        stale = {**allowed[0], "revision": allowed[0]["revision"] + 1}
        with self.assertRaisesRegex(ValueError, "absent or stale"):
            execution_profiles.select_profile(registry, {"role": "maintenance"}, requirement, allowed_refs=[stale])
        old = next(p for p in registry.values() if p["role"] == "maintenance"
                   and p["ai"]["tier"] == chosen["tier"] and execution_profiles.profile_ref(p) not in allowed)
        with self.assertRaisesRegex(ValueError, "permitted role/model edition"):
            execution_profiles.select_profile(registry, {"role": "maintenance", "profile_ref": execution_profiles.profile_ref(old)},
                               requirement, allowed_refs=allowed)

    def test_ai_selection_uses_adopted_editions_without_building_or_reading_lean(self):
        config = {**deepcopy(PROFILE_CONFIG), "lean_command": ["fixture-no-lean"]}
        instance = execution_profiles.build_profiles(config)
        registry = instance["execution_profiles"]
        with patch.object(execution_profiles, "_lean_contract", side_effect=AssertionError("AI selection read Lean")), \
             patch.object(execution_profiles, "seal_profile", wraps=execution_profiles.seal_profile) as seals:
            chosen = model_policy.selection(config, {"role": "maintenance"}, {}, {}, instance=instance)
        self.assertEqual(registry[chosen["profile_ref"]["id"]]["role"], "maintenance")
        self.assertIn(chosen["profile_ref"], instance["role_profile_refs"]["maintenance"])
        self.assertEqual(seals.call_count, 0)

    def test_profile_authoring_rejects_missing_unknown_and_invalid_host_demands(self):
        constraint = execution_profiles.host_constraint(host_id="fixture-host",
            limits={"jobs": 3, "memory_bytes": 4096, "cpu_rate_basis_points": 10000},
            control_reserve={"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000},
            authority_refs=["GS-fixture"])
        demands = {role: {"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000}
                   for role in execution_profiles.HOST_ROLES}
        config = {**deepcopy(PROFILE_CONFIG), "lean_command": ["fixture-no-lean"],
                  "host_resources": {"constraint": constraint, "demands_by_role": demands}}
        self.assertEqual(execution_profiles.build_profiles(config)["host_capacity_ref"], constraint["id"])
        for defect in ("missing", "unknown", "invalid"):
            bad = deepcopy(config)
            rows = bad["host_resources"]["demands_by_role"]
            if defect == "missing":
                del rows["research_work"]
            elif defect == "unknown":
                rows["invented"] = deepcopy(rows["research_work"])
            else:
                rows["research_work"]["memory_bytes"] = 0
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                execution_profiles.build_profiles(bad)

    def test_normal_final_delivery_rendering_preserves_the_sealed_profile(self):
        from do_math import execution_profiles as api, contracts
        profile = next(p for p in api.build_profiles(PROFILE_CONFIG)['execution_profiles'].values()
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

    def test_execution_control_is_registered_and_round_trips_in_child(self):
        import subprocess
        from do_math.control_transport import ControlTransport
        from do_math import cli_worker, codex_worker, claude_worker
        from provider_fixtures import Adapter, runner_with
        profile = next(p for p in execution_profiles.build_profiles({**PROFILE_CONFIG, "scholarly_server": {
                       "command": sys.executable, "args": [str(Path(__file__).resolve())]}})["execution_profiles"].values()
                       if p["role"] == "research_work")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transport = ControlTransport(root / "transport")
            binding = transport.issue("EX-bound", "GR-bound")
            adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}})
            runner = runner_with(adapter)
            runner.run(prompt=execution_profiles.prepare_prompt("test", profile), input_seal=execution_profiles.prompt_seal(execution_profiles.prepare_prompt("test", profile)), output_schema={}, workspace=root,
                evidence_dir=root / "evidence", model=profile["ai"]["model"], effort=profile["ai"]["effort"],
                timeout_seconds=600, execution_id="EX-bound", profile=profile, launch_ticket=dispatched_launch("EX-bound", profile), control_binding=binding)
            self.assertEqual(adapter.request["control_binding"], binding)
            request = codex_worker.load_request(root / "evidence" / "request.json")
            argv = codex_worker.build_argv(request)
            config = ControlTransport.mcp_server_config(binding)
            self.assertIn("mcp_servers.execution_control.command=" + json.dumps(config["command"], ensure_ascii=False), argv)
            self.assertIn("mcp_servers.execution_control.args=" + json.dumps(config["args"], ensure_ascii=False), argv)
            claude_request = {k: v for k, v in request.items()
                              if k not in {"codex_path", "sandbox", "windows_sandbox", "approval_policy", "final_path"}}
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
            def exchange(method, params):
                nonlocal sequence
                sequence += 1
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": sequence, "method": method, "params": params}) + "\n")
                process.stdin.flush()
                response = json.loads(process.stdout.readline())
                self.assertEqual(response["id"], sequence)
                return response
            def rpc(method, params):
                response = exchange(method, params)
                self.assertNotIn("error", response)
                return response["result"]
            def call(name, arguments):
                return json.loads(rpc("tools/call", {"name": name, "arguments": arguments})["content"][0]["text"])
            try:
                self.assertEqual(rpc("initialize", {"protocolVersion": "2024-11-05"})["serverInfo"]["version"], "5")
                listed = {t["name"]: t for t in rpc("tools/list", {})["tools"]}
                tools = {name: tool["inputSchema"] for name, tool in listed.items()}
                self.assertEqual(set(tools), {"control_submit", "control_receipt", "control_self_check", "submit_draft"})
                # The worker sees the kinds the transport accepts and the answer schema it will be checked against.
                # The answer schema travels in the description; the input node keeps the plain object shape
                # that preserved provider runs accepted.
                from do_math.control_transport import REQUEST_KINDS, SELF_CHECK_RESPONSE_SCHEMA
                self.assertEqual(set(tools["control_submit"]["properties"]["kind"]["enum"]), REQUEST_KINDS)
                self.assertEqual(tools["control_self_check"]["properties"]["response"], {"type": "object"})
                self.assertIn(json.dumps(SELF_CHECK_RESPONSE_SCHEMA, sort_keys=True), listed["control_self_check"]["description"])
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
                transport.request_self_check(binding, request={"self_check_id": "SC-one", "execution_id": "EX-bound",
                                                               "payload": {"obligations": ["answer"]}})
                self.assertEqual(call("control_self_check", {"self_check_id": "SC-one"})["execution_id"], "EX-bound")
                # A malformed answer is a tool error the worker can correct; nothing is delivered.
                refused = exchange("tools/call", {"name": "control_self_check",
                                                  "arguments": {"self_check_id": "SC-one", "response": {"answered": True}}})
                self.assertEqual(refused["error"]["code"], -32602)
                self.assertIsNone(ControlTransport.worker_receipt(binding, "self-check-SC-one"))
                self.assertFalse((Path(binding["endpoint"]) / "inbox" / "self-check-SC-one.json").exists())
                answer = {"obligation_id": "SC-one", "execution_id": "EX-bound", "rule_revision": 0,
                          "rule_results": [{"rule_id": "R-1", "status": "normal", "evidence_refs": ["EV-1"],
                                            "missing_evidence_refs": [], "reason": "checked"}],
                          "progress": "progress", "attempts": ["checked"], "next_method": "continue"}
                call("control_self_check", {"self_check_id": "SC-one", "response": answer})
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
                    cli_worker.validate_execution_binding(worker_request)
            with self.assertRaises(ValueError):
                runner.run(prompt=execution_profiles.prepare_prompt("wrong", profile), input_seal=execution_profiles.prompt_seal(execution_profiles.prepare_prompt("wrong", profile)), output_schema={}, workspace=root, evidence_dir=root / "wrong",
                    model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=600,
                    execution_id="EX-other", profile=profile, launch_ticket=dispatched_launch("EX-other", profile), control_binding=binding)
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
                **{key: str(root / key) for key in ("stdout_path", "stderr_path", "status_path")},
                "execution_id": "EX-snapshot", "profile_ref": {"id": "EP-test", "revision": 1, "sha256": "a" * 64},
                "control_binding": binding}
            for adapter, options in ((CodexExecAdapter("codex"), {"codex_path": "codex", "sandbox": "danger-full-access",
                                                                  "approval_policy": "never", "final_path": str(root / "final_path")}),
                                     (ClaudePrintAdapter("claude"), {"claude_path": "claude"})):
                request = root / (adapter.executable_key + ".json")
                request.write_text(json.dumps({**common, **options}), encoding="utf-8")
                with patch("do_math.codex_adapter.WindowsJob", return_value=Mock()):
                    execution = adapter.start(request, cwd=root, env={})
                # The worker runs the snapshot request its argv names, not the original file.
                snapshot = Path(execution.worker_argv[-1])
                snap = json.loads(snapshot.read_text(encoding="utf-8"))
                self.assertEqual(snap["control_binding"], binding)
                self.assertEqual(snap["execution_id"], binding["execution_id"])
                request.write_text("{}", encoding="utf-8")
                self.assertEqual(json.loads(snapshot.read_text(encoding="utf-8"))["control_binding"], binding)

    def test_admission_probe_preserves_history_and_provider_gate_across_capacity_editions(self):
        from do_math.session_slots import SessionSlots
        instance = {**execution_profiles.build_profiles(PROFILE_CONFIG), "config": deepcopy(PROFILE_CONFIG)}
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        slots = SessionSlots(runtime, instance)
        model = profile["ai"]["model"]
        self.assertTrue(slots.acquire("EX-history", profile=profile,
                                     execution={"id": "EX-history", "role": "research_work", "status": "queued"}))
        self.assertTrue(slots.release("EX-history"))
        history_id = runtime["executions"]["EX-history"]["capacity"]["reservation_ids"][0]
        history = deepcopy(runtime["reservations"][history_id])
        limits = deepcopy(PROFILE_CONFIG["session_limits"])
        limits["work"][model] = 1
        instance["config"]["session_limits"] = limits
        execution_profiles.apply_editions(instance, execution_profiles.build_profiles(instance["config"]))
        provider = profile["ai"]["provider"]
        runtime["provider_waits"]["PW-" + provider] = {
            "id": "PW-" + provider, "provider": provider, "generation": 1,
            "state": "waiting", "retry_at": 100, "attempts": 1,
            "evidence": {"evidence_ref": "fixture-limit"},
            "probe_owner": None, "probe_started_at": None}
        before = deepcopy(runtime)
        observer = SessionSlots(runtime, instance, observer=True)
        self.assertTrue(observer.admission_check(profile, current_time=100)["allowed"])
        self.assertEqual(runtime, before)
        self.assertTrue(slots.acquire("EX-held", profile=profile,
            execution={"id": "EX-held", "role": "research_work", "status": "queued"}, current_time=100))
        self.assertEqual(runtime["reservations"][history_id], history)
        held_id = runtime["executions"]["EX-held"]["capacity"]["reservation_ids"][0]
        self.assertNotEqual(runtime["reservations"][held_id]["constraint_id"], history["constraint_id"])
        before = deepcopy(runtime)
        self.assertEqual(observer.admission_check(profile, current_time=100)["wait"]["kind"], "provider_limit")
        self.assertEqual(runtime, before)
        runtime["provider_waits"].clear()
        before = deepcopy(runtime)
        denied = observer.admission_check(profile, current_time=100)
        self.assertFalse(denied["allowed"])
        self.assertEqual(denied["wait"]["kind"], "capacity")
        self.assertEqual(runtime, before)

    def test_work_has_no_deadline_and_operations_keep_their_call_window(self):
        from provider_fixtures import Adapter, runner_with
        profiles = execution_profiles.build_profiles(PROFILE_CONFIG)["execution_profiles"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for role, timeout in (("research_work", None), ("operational_review", 600)):
                profile = next(p for p in profiles.values() if p["role"] == role)
                self.assertNotIn('run_timeout_seconds', profile['window'])
                self.assertNotIn('dispatch_reserve_seconds', profile['window'])
                adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}})
                runner = runner_with(adapter)
                runner.run(prompt=execution_profiles.prepare_prompt("test", profile), input_seal=execution_profiles.prompt_seal(execution_profiles.prepare_prompt("test", profile)), output_schema={}, workspace=root, evidence_dir=root / role,
                    model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=timeout,
                    execution_id="EX-" + role, profile=profile, launch_ticket=dispatched_launch("EX-" + role, profile))
                self.assertEqual(adapter.request['max_runtime_seconds'], timeout)
                if role == 'operational_review':
                    for invalid in (None, PROFILE_CONFIG['call_timeout_seconds'] + 1):
                        with self.assertRaisesRegex(ValueError, "deadline"):
                            runner.run(prompt=execution_profiles.prepare_prompt("test", profile), input_seal=execution_profiles.prompt_seal(execution_profiles.prepare_prompt("test", profile)), output_schema={}, workspace=root, evidence_dir=root / (role + "-over"),
                                model=profile["ai"]["model"], effort=profile["ai"]["effort"], timeout_seconds=invalid,
                                execution_id="EX-" + role, profile=profile, launch_ticket=dispatched_launch("EX-" + role, profile))

    def test_selection_is_pinned_and_contract_allowlist_is_enforced(self):
        state = execution_profiles.build_profiles(PROFILE_CONFIG)
        action = {"role": "research_work", "model_assessment": {
            "difficulty": "low", "importance": "low", "reason": "bounded arithmetic"}}
        selected = model_policy.selection(PROFILE_CONFIG, action, {}, {}, instance=state)
        profile = execution_profiles.resolve_profile(state["execution_profiles"], selected["profile_ref"])
        frozen = execution_profiles.runtime_config(profile)
        config = deepcopy(PROFILE_CONFIG)
        config["max_input_bytes"] = 1
        self.assertEqual(frozen["max_input_bytes"], 500000)
        with self.assertRaises(ValueError):
            execution_profiles.select_profile(state["execution_profiles"], action, selected, allowed_refs=[])
        self.assertEqual(execution_profiles.select_profile(state["execution_profiles"], action, selected,
                         allowed_refs=[execution_profiles.profile_ref(profile)])["id"], profile["id"])
        broken = deepcopy(state["execution_profiles"])
        broken[profile["id"]]["ai"]["model"] = "different"
        # Lookup compares the reference only; an unsaved edit is caught by validate_profile.
        with self.assertRaises(ValueError):
            execution_profiles.validate_profile(broken[profile["id"]])
        changed = {**deepcopy(PROFILE_CONFIG), "max_input_bytes": 400000}
        editions = execution_profiles.build_profiles(changed)
        registry = {**state["execution_profiles"], **editions["execution_profiles"]}
        newest = model_policy.selection(changed, action, {}, {}, instance={
            "execution_profiles": registry, "role_profile_refs": editions["role_profile_refs"]})
        self.assertIn(newest["profile_ref"]["id"], editions["execution_profiles"])

    def test_modes_machine_fields_and_profile_rebinding(self):
        profiles = execution_profiles.build_profiles(PROFILE_CONFIG)["execution_profiles"]
        mode = {p["role"]: p["observation"]["mode"] for p in profiles.values()}
        self.assertEqual(mode["research_work"], "event_driven")
        self.assertEqual(mode["identity_review"], "periodic")
        self.assertEqual(mode["operational_review"], "deadline_only")
        machine = next(p for p in profiles.values() if p["role"] == "formal_check")
        self.assertNotIn("ai", machine)
        execution = {"id": "EX-one", "role": "formal_check"}
        execution_profiles.bind_execution(execution, machine)
        self.assertIn("execution_profile_ref", execution)
        other = next(p for p in profiles.values() if p["role"] == "trust_check")
        with self.assertRaises(ValueError):
            execution_profiles.bind_execution(execution, other)

    def test_research_profile_binds_all_implemented_signal_kinds_not_counter_names(self):
        from do_math.observations import observation_rule_contract, tracker_config
        profile = next(p for p in execution_profiles.build_profiles({**PROFILE_CONFIG, "tool_review_window_seconds": 60,
                       "self_check_response_window_seconds": 60})["execution_profiles"].values()
                       if p["role"] == "research_work")
        from research_fixtures import observation_rule
        rule = observation_rule(threshold=1, id="SC-attempts", required_evidence=["checkpoint.json"])
        config = tracker_config(profile, initial_self_check_rules=[rule])
        self.assertEqual(config["observation_rule_bindings"], observation_rule_contract())

    def test_git_admission_all_or_nothing_and_unknown_release(self):
        from do_math.session_slots import SessionSlots
        instance = execution_profiles.build_profiles(PROFILE_CONFIG)
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        profile = next(p for p in instance["execution_profiles"].values()
                       if p["role"] == "research_work" and p["ai"]["model"] == PROFILE_CONFIG["tier_models"]["low"])
        slots = SessionSlots(runtime, instance)
        for i in range(3):
            self.assertTrue(slots.acquire(f"EX-{i}", profile=profile,
                            execution={"id": f"EX-{i}", "role": "research_work", "status": "queued"}))
        from do_math.state_contract import default_state_contract, validate_record
        for reservation in runtime["reservations"].values():
            validate_record(default_state_contract().family("runtime", "reservations").checker, reservation, "reservation")
        before = deepcopy(runtime)
        self.assertFalse(slots.acquire("EX-over", profile=profile,
                         execution={"id": "EX-over", "role": "research_work", "status": "queued"}))
        self.assertEqual(runtime, before)
        identity = {"job_name": runtime["executions"]["EX-0"]["launch_ticket"]["job_name"], "pid": 1}
        started = slots.started("EX-0", identity, at="2026-01-01T00:00:00+00:00")
        self.assertIs(started, runtime["executions"]["EX-0"])
        self.assertEqual((started["status"], started["started_at"], started["capacity"]["process"]),
                         ("running", "2026-01-01T00:00:00+00:00", identity))
        repeated = deepcopy(runtime)
        self.assertIs(slots.started("EX-0", identity, at="2026-01-01T00:00:01+00:00"), started)
        self.assertEqual(runtime, repeated)
        with patch("do_math.windows_job.named_job_empty", return_value=None):
            self.assertFalse(slots.release("EX-0"))
        self.assertEqual(slots.snapshot()[profile["ai"]["model"]]["used"], 3)
        with patch("do_math.windows_job.named_job_empty", return_value=True):
            self.assertTrue(slots.release("EX-0"))
            self.assertTrue(slots.release("EX-0"))
        self.assertEqual(slots.snapshot()[profile["ai"]["model"]]["used"], 2)
        # Operational AI roles reserve no model slot, even when every work slot is taken.
        self.assertTrue(slots.acquire("EX-3", profile=profile,
                        execution={"id": "EX-3", "role": "research_work", "status": "queued"}))
        operation = next(p for p in instance["execution_profiles"].values()
                         if p["role"] == "maintenance" and p["ai"]["model"] == profile["ai"]["model"])
        self.assertEqual(operation["ai"]["capacity_refs"], [])
        self.assertTrue(slots.acquire("EX-op", profile=operation,
                        execution={"id": "EX-op", "role": "maintenance", "status": "queued"}))
        self.assertEqual(runtime["executions"]["EX-op"]["capacity"]["reservation_ids"], [])
        self.assertEqual(slots.snapshot()[profile["ai"]["model"]]["used"], 3)

    def test_admission_accepts_registered_queued_execution_exactly_once(self):
        from do_math.session_slots import SessionSlots
        instance = execution_profiles.build_profiles(PROFILE_CONFIG)
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        execution = {"id": "EX-registered", "role": "research_work", "status": "queued",
                     "execution_profile_ref": execution_profiles.profile_ref(profile), "owner_activity_id": "AY-one"}
        runtime = {"executions": {execution["id"]: execution}, "reservations": {}}
        slots = SessionSlots(runtime, instance)
        self.assertTrue(slots.acquire(execution["id"], profile=profile, execution=execution))
        self.assertIs(runtime["executions"][execution["id"]], execution)
        self.assertEqual(execution["owner_activity_id"], "AY-one")
        before = deepcopy(runtime)
        with self.assertRaises(ValueError):
            slots.acquire(execution["id"], profile=profile, execution=execution)
        self.assertEqual(runtime, before)

    def test_runner_pins_request_and_exposes_reported_evidence(self):
        from provider_fixtures import Adapter, runner_with
        profile = next(p for p in execution_profiles.build_profiles(PROFILE_CONFIG)["execution_profiles"].values()
                       if p["role"] == "research_work")
        adapter = Adapter({"result": "output_collected", "final": {"raw": b'{}'},
                           "jsonl": {"usage_total": {"output_tokens": 3}, "stop_reason": "end_turn"}})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner = runner_with(adapter)
            result = runner.run(prompt=execution_profiles.prepare_prompt("test", profile), input_seal=execution_profiles.prompt_seal(execution_profiles.prepare_prompt("test", profile)), output_schema={}, workspace=root,
                evidence_dir=root / "evidence", model=profile["ai"]["model"], effort=profile["ai"]["effort"],
                timeout_seconds=600, execution_id="EX-bound", profile=profile, launch_ticket=dispatched_launch("EX-bound", profile))
            self.assertEqual(adapter.request["execution_id"], "EX-bound")
            self.assertEqual(adapter.request["profile_ref"], execution_profiles.profile_ref(profile))
            self.assertEqual(result["provider_observation"]["stop_reason"], "end_turn")
            self.assertEqual(result["provider_observation"]["remote_termination"], "unknown")
            self.assertEqual(result["provider_observation"]["usage_scope"], "reported_execution_counters_not_invoice")
            self.assertEqual(result["execution_id"], "EX-bound")

    def test_issued_workspace_binding_reaches_both_runners_and_worker_contracts(self):
        from do_math.control_transport import ControlTransport
        from do_math import codex_worker, claude_worker
        from provider_fixtures import Adapter, runner_with
        for provider, worker, model in (('codex', codex_worker, 'gpt-6-astra'),
                                        ('claude', claude_worker, 'claude-opus-5')):
            with self.subTest(provider=model), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / 'workspace'; workspace.mkdir()
                config = {**PROFILE_CONFIG, 'tier_models': {tier: model for tier in ('high', 'medium', 'low')},
                          'session_limits': {'work': {model: 3}}}
                profile = next(p for p in execution_profiles.build_profiles(config)['execution_profiles'].values()
                               if p['role'] == 'research_work')
                binding = ControlTransport(root / 'transport').issue('EX-bound', 'GR-bound', workspace=workspace)
                runner = runner_with(Adapter({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}},
                                             provider), provider)
                prompt = execution_profiles.prepare_prompt('test', profile)
                options = dict(prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt), output_schema={},
                    workspace=workspace, model=model, effort=profile['ai']['effort'], timeout_seconds=60,
                    execution_id='EX-bound', profile=profile, launch_ticket=dispatched_launch('EX-bound', profile))
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
        from do_math.session_slots import SessionSlots
        from do_math.repository import canonical_json
        instance = execution_profiles.build_profiles(PROFILE_CONFIG)
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        slots = SessionSlots(runtime, instance)
        admit = lambda eid, t: slots.acquire(eid, profile=profile,
                         execution={"id": eid, "role": "research_work", "status": "queued"}, current_time=t)
        self.assertTrue(admit("EX-failure", 10))
        failure = {"kind": "provider_limit", "provider": profile["ai"]["provider"],
                   "retry_at": "1970-01-01T00:00:20+00:00", "evidence_ref": "stdout.jsonl"}
        slots.provider_result_from_run("EX-failure", {"status": "failed", "error_kind": "provider_limit",
                                                      "failure": failure}, PROFILE_CONFIG, current_time=10.5)
        self.assertTrue(all(key == row["id"] for key, row in runtime["provider_waits"].items()),
                        "provider gates must persist as individual family records")
        try:
            canonical_json(runtime)
        except ValueError as error:
            self.fail("Git reservation path emits noncanonical state: " + str(error))
        self.assertFalse(admit("EX-too-early", 19))
        self.assertTrue(admit("EX-probe", 21))
        self.assertFalse(admit("EX-concurrent-probe", 21))
        slots.provider_result_from_run("EX-probe", {"status": "completed"}, PROFILE_CONFIG, current_time=22)
        self.assertTrue(admit("EX-after", 22))

    def test_capability_identity_has_host_worker_and_cli_hashes(self):
        from do_math.codex_adapter import CodexExecAdapter
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cli.exe"
            path.write_bytes(b"first")
            adapter = CodexExecAdapter(str(path))
            first = adapter.capability_identity()
            self.assertIn("windows_job", first["module_sha256"])
            path.write_bytes(b"second")
            second = adapter.capability_identity()
            self.assertNotEqual(first["cli_sha256"], second["cli_sha256"])
            self.assertEqual(first["module_sha256"], second["module_sha256"])
            self.assertIn("host", first)
        # Every module a worker runs in its Job, or its collector uses, identifies the implementation.
        from do_math.claude_adapter import ClaudePrintAdapter
        self.assertEqual(set(CodexExecAdapter("codex").capability_identity()["module_sha256"]),
                         {"cli_worker", "codex_worker", "control_transport", "file_io", "windows_job", "scholarly",
                          "codex_adapter"})
        self.assertEqual(set(ClaudePrintAdapter("claude").capability_identity()["module_sha256"]),
                         {"claude_worker", "cli_worker", "codex_worker", "control_transport", "file_io", "windows_job",
                          "scholarly", "codex_adapter", "claude_adapter", "claude_stream"})

    def test_unchanged_cli_and_sources_are_not_rehashed_for_each_identity(self):
        from do_math import file_io
        from do_math.codex_adapter import CodexExecAdapter
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cli.exe"
            path.write_bytes(b"first")
            adapter = CodexExecAdapter(str(path))
            # A fresh file's birth time cannot be aged; treat any past fingerprint as settled.
            with patch.object(file_io, "RACY_NS", 0):
                first = adapter.capability_identity()
                with patch.object(file_io, "sha256_file", side_effect=AssertionError("unchanged file was rehashed")):
                    self.assertEqual(adapter.capability_identity(), first)

    def test_capability_evidence_does_not_promote_surface_to_job_proof(self):
        profile = next(p for p in execution_profiles.build_profiles(PROFILE_CONFIG)["execution_profiles"].values() if p["actor_kind"] == "ai")
        description = {"scope": "cli_command_surface_only", "verified": True,
            "identity": {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "test"}},
            "supported": {"jsonl": True, "model": True, "local_job_stop": True},
            "unknown": ["remote_termination"], "version_sha256": "c" * 64, "exec_help_sha256": "d" * 64}
        evidence = execution_profiles.capability_evidence(profile, description, observed_at="2026-09-20T00:00:00Z")
        self.assertEqual(evidence["execution_profile_ref"], execution_profiles.profile_ref(profile))
        self.assertEqual(evidence["capabilities"]["jsonl"]["status"], "supported")
        self.assertEqual(evidence["capabilities"]["local_job_stop"]["status"], "unknown")
        self.assertEqual(evidence["capabilities"]["remote_termination"]["status"], "unknown")

    def test_unsupported_job_is_a_profile_failure_not_an_ordinary_retry(self):
        from provider_fixtures import mock_adapter, runner_with
        from do_math.windows_job import WindowsJobUnsupportedError
        with tempfile.TemporaryDirectory() as directory:
            adapter = mock_adapter()
            adapter.start.side_effect = WindowsJobUnsupportedError("atomic admission unsupported")
            runner = runner_with(adapter)
            try:
                result = runner.run(prompt="test", output_schema={}, workspace=Path(directory),
                    evidence_dir=Path(directory) / "evidence", model="test", effort="low", timeout_seconds=1)
            except WindowsJobUnsupportedError:
                self.fail("structural unsupported capability was not classified for the profile gate")
            self.assertEqual(result["error_kind"], "profile_unsupported")
            self.assertEqual(result["capability_failure"]["capability"], "atomic_local_job")


class MachineAndProviderEvidenceTests(unittest.TestCase):
    def profiles(self, **changes):
        from do_math import execution_profiles as ep
        return ep, ep.build_profiles({**PROFILE_CONFIG, "lean_command": ["lean-A"],  **changes})

    def approved(self, tool, command):
        """An approved identity whose recorded executable is this tool file."""
        import hashlib
        from do_math import formal
        digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        checker = Path(formal.__file__).resolve()
        return {"executable": str(Path(tool).resolve()), "sha256": digest(tool), "configured_command": command,
                "version": "fixture", "version_exit": 0, "verifier_sha256": digest(checker),
                "verifier_path": str(checker), "executables": {str(Path(tool).resolve()): digest(tool)}, "project": None}

    def test_machine_profile_pins_the_command_and_the_verifier_checks_tool_bytes(self):
        from do_math import formal
        ep, a = self.profiles()
        _, b = self.profiles(lean_command=["lean-B"], )
        def formal_profile(state):
            return next(p for p in state["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertNotEqual(ep.profile_ref(formal_profile(a)), ep.profile_ref(formal_profile(b)))
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "lean.exe"
            tool.write_bytes(b"edition one")
            _, first = self.profiles(lean_command=[str(tool)])
            p = formal_profile(first)
            env = {"toolchain": self.approved(tool, [str(tool)])}
            args = ep.machine_invocation(p, trust_environment=env)
            self.assertNotIn("timeout_seconds", args)
            self.assertEqual(args["lean_command"], [str(tool)])
            self.assertEqual(args["expected_toolchain"], env["toolchain"])
            tool.write_bytes(b"edition two")
            _, second = self.profiles(lean_command=[str(tool)])
            # The profile names the command only; the approved identity binds its bytes once, in the verifier.
            self.assertEqual(ep.profile_ref(p), ep.profile_ref(formal_profile(second)))
            self.assertEqual(ep.machine_invocation(p, trust_environment=env), args)
            with patch("do_math.formal._job_run", side_effect=AssertionError("changed tool was started")):
                result = formal.verify_lean(source="theorem t : True := True.intro", declarations=["t"],
                                            workspace=Path(directory), **args)
            self.assertEqual((result["status"], result["reason"]), ("rejected", "approved toolchain changed before execution"))
            self.assertEqual(result["identity_errors"], ["approved toolchain file changed: " + str(tool.resolve())])
            self.assertEqual(result["error_kind"], "trust_environment")
            with self.assertRaises(ValueError):
                ep.machine_invocation(formal_profile(second), trust_environment={"toolchain": {"configured_command": ["different"]}})

    def test_machine_command_alias_keeps_adopted_argv_and_the_verifier_checks_resolution(self):
        from do_math import formal
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "lean.exe"; tool.write_bytes(b"edition")
            ep, state = self.profiles(lean_command=["lean"])
            p = next(p for p in state["execution_profiles"].values() if p["role"] == "formal_check")
            args = ep.machine_invocation(p, trust_environment={"toolchain": self.approved(tool, ["lean"])})
            self.assertEqual(args["lean_command"], ["lean"])
            other = Path(directory) / "other.exe"; other.write_bytes(b"edition")
            with patch("do_math.formal.shutil.which", return_value=str(other)), \
                 patch("do_math.formal._job_run", side_effect=AssertionError("another resolution was started")):
                result = formal.verify_lean(source="theorem t : True := True.intro", declarations=["t"],
                                            workspace=Path(directory), **args)
            self.assertEqual((result["status"], result["reason"]), ("rejected", "approved toolchain changed before execution"))
            self.assertEqual(result["error_kind"], "trust_environment")

    def test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist(self):
        ep, old = self.profiles()
        profile = next(p for p in old["execution_profiles"].values()
                       if p["role"] == "intent_interpretation" and p["ai"]["tier"] == "high")
        changed = deepcopy(PROFILE_CONFIG)
        changed["tier_models"]["high"] = "replacement-model"
        selected = model_policy.selection(changed, {"role": "intent_interpretation", "profile_ref": ep.profile_ref(profile)}, {}, {},
                                          instance=old)
        self.assertEqual(selected["model"], profile["ai"]["model"])
        low = next(p for p in old["execution_profiles"].values()
                   if p["role"] == "intent_interpretation" and p["ai"]["tier"] == "low")
        with self.assertRaises(ValueError):
            model_policy.selection(PROFILE_CONFIG, {"role": "intent_interpretation", "profile_ref": ep.profile_ref(low)}, {}, {}, instance=old)
        # Task allowlists govern work, while interpretation keeps its own profile.
        model_policy.selection(PROFILE_CONFIG, {"role": "intent_interpretation", "target": "T", "profile_ref": ep.profile_ref(profile)},
                               {"T": {"profile_refs": []}}, {}, instance=old)
        work = next(p for p in old["execution_profiles"].values()
                    if p["role"] == "research_work" and p["ai"]["tier"] == "high")
        with self.assertRaises(ValueError):
            model_policy.selection(PROFILE_CONFIG, {"role": "research_work", "target": "T", "profile_ref": ep.profile_ref(work)},
                                   {"T": {"profile_refs": []}}, {}, instance=old)

    def test_runner_preserves_exact_utf8_input_after_seal(self):
        from provider_fixtures import Adapter, runner_with
        import hashlib
        ep, registry = self.profiles()
        p = next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance")
        text = "exact input\n한글\n" + ep.boundary_prompt(p)
        seal = {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner = runner_with(Adapter({"result": "output_collected", "final": {"raw": b'{}'}, "jsonl": {}}))
            kwargs = dict(prompt=text, output_schema={}, workspace=root, evidence_dir=root / "evidence",
                model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1, execution_id="EX-exact", profile=p, launch_ticket=dispatched_launch("EX-exact", p))
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
        p = next(p for p in registry["execution_profiles"].values() if p["actor_kind"] == "ai")
        args = ep.runner_tools(p)
        self.assertEqual(args["scholarly_server"]["command"], "approved-old-server")
        args["scholarly_server"]["command"] = "mutated"
        self.assertEqual(ep.runner_tools(p)["scholarly_server"]["command"], "approved-old-server")

    def test_structural_failure_emits_identity_bound_negative_evidence(self):
        from provider_fixtures import mock_adapter, runner_with
        from do_math.windows_job import WindowsJobUnsupportedError
        import hashlib
        ep, registry = self.profiles()
        p = next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance")
        identity = {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "observed"}}
        adapter = mock_adapter()
        adapter.capability_identity.return_value = identity
        adapter.start.side_effect = WindowsJobUnsupportedError("fixture structural failure")
        runner = runner_with(adapter)
        prompt = "input" + ep.boundary_prompt(p)
        with tempfile.TemporaryDirectory() as directory:
            kwargs = dict(prompt=prompt, output_schema={}, workspace=Path(directory), evidence_dir=Path(directory)/"evidence",
                model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1, execution_id="EX-failure", profile=p, launch_ticket=dispatched_launch("EX-failure", p))
            kwargs["input_seal"] = ep.prompt_seal(prompt)
            result = runner.run(**kwargs)
        self.assertIn("capability_evidence", result)
        evidence = result["capability_evidence"]
        self.assertEqual(evidence["identity"], identity)
        self.assertEqual(evidence["execution_profile_ref"], ep.profile_ref(p))
        self.assertEqual(evidence["capabilities"]["atomic_local_job"]["status"], "unsupported")
        self.assertEqual(evidence["id"], "CE-" + exact_content_hash({k: v for k, v in evidence.items() if k != "id"}))

    def test_identity_is_observed_only_for_a_structural_start_failure(self):
        from provider_fixtures import mock_adapter, runner_with
        ep, registry = self.profiles()
        p = next(p for p in registry["execution_profiles"].values() if p["role"] == "maintenance")
        adapter = mock_adapter()
        adapter.start.side_effect = FileExistsError("fixture launch conflict")
        runner = runner_with(adapter)
        prompt = "input" + ep.boundary_prompt(p)
        with tempfile.TemporaryDirectory() as directory:
            result = runner.run(prompt=prompt, output_schema={}, workspace=Path(directory),
                evidence_dir=Path(directory) / "evidence", model=p["ai"]["model"], effort=p["ai"]["effort"],
                timeout_seconds=1, execution_id="EX-conflict", profile=p,
                launch_ticket=dispatched_launch("EX-conflict", p), input_seal=ep.prompt_seal(prompt))
        self.assertEqual(result["error_kind"], "launch_conflict")
        # Hashing the CLI and adapter sources is evidence for a failed start only.
        adapter.capability_identity.assert_not_called()

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
        from do_math.codex_adapter import CLIExecution
        from do_math.windows_job import JobInspection
        from provider_fixtures import FakeJob
        from provider_fixtures import claude_stream, CLAUDE_INIT, CLAUDE_RESULT
        from provider_fixtures import Adapter, runner_with
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
            native = {**CLAUDE_RESULT, "stop_reason": "max_tokens", "modelUsage": {"haiku": {"costUSD": 0.125}}, "total_cost_usd": 0.125}
            stdout.write_bytes(claude_stream(CLAUDE_INIT, native)); stderr.write_bytes(b""); final.write_bytes(b'{"ok":true}')
            request_hash = hashlib.sha256(request.read_bytes()).hexdigest()
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            status.write_bytes(json.dumps({"state": "exited", "cli_exit_code": 0, "stdin_sha256": source_hash,
                "request_sha256": request_hash, "schema_sha256": None, "execution_id": "EX-native", "profile_ref": ep.profile_ref(p)}).encode())
            ex = CLIExecution(request_hash, source_hash, ("worker",), stdout, stderr, final, status,
                              FakeJob(JobInspection(0, (), True)), None, request.read_bytes(), source.read_bytes())
            collected = ClaudePrintAdapter("not-launched").collect(ex)
            self.assertEqual(collected["result"], "output_collected", collected["reasons"])
            runner = runner_with(Adapter(collected, "claude"), "claude")
            result = runner.run(prompt=prompt, input_seal=ep.prompt_seal(prompt), output_schema={}, workspace=root,
                evidence_dir=root/"runner", model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1,
                profile=p, execution_id="EX-native", launch_ticket=dispatched_launch("EX-native", p))
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
        from record_fixtures import surface_state
        from do_math.context_store import prepare_role_input
        from provider_fixtures import Adapter, runner_with
        from do_math import execution_profiles as ep
        from do_math.contracts import schema_for
        schema = schema_for("research_preparation")
        state, runtime = surface_state()
        p = next(p for p in state["execution_profiles"].values() if p["role"] == "research_preparation")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({"action": {}, "resources": {}, 'knowledge_catalog': [], 'blocked_actions': []}, instance=state, runtime=runtime,
                role="research_preparation", profile=p, snapshot="a"*40, workspace=root, activity_id="AC-1",
                output_schema=schema, artifact_prefix="runtime/artifacts/EX-seal")
            self.assertIsNone(fitted["overflow"])
            prompt = fitted["prompt"]
            self.assertEqual(prompt.count(ep.boundary_prompt(p)), 1)
            expected = ep.prompt_seal(prompt)
            self.assertEqual({k: fitted["manifest"]["prompt"][k] for k in expected}, expected)
            runner = runner_with(Adapter({"result":"output_collected", "final":{"raw":b'{}'}, "jsonl":{}}))
            runner.run(prompt=prompt, input_seal=fitted["manifest"]["prompt"], output_schema=schema, workspace=root,
                evidence_dir=root/"evidence", model=p["ai"]["model"], effort=p["ai"]["effort"], timeout_seconds=1,
                execution_id="EX-seal", profile=p, launch_ticket=dispatched_launch("EX-seal", p))
            self.assertEqual((root/"evidence/input.txt").read_bytes(),
                             fitted["artifacts"][fitted["manifest"]["prompt"]["artifact_ref"]])

    def test_native_provider_observation_has_canonical_storage_projection(self):
        from do_math import execution_profiles as ep
        from do_math.repository import canonical_json
        observation = {"stop_reason": "max_tokens", "usage": {"input_tokens": 4, "cost_usd": 0.125},
                       "operation_count": "unknown", "remote_termination": "unknown"}
        stored = ep.execution_observation({"provider_observation": observation})
        canonical_json(stored)
        self.assertEqual(json.loads(stored["reported_fields_json"]), observation)
        self.assertEqual(stored["stop_reason"], "max_tokens")
        self.assertIsNone(ep.execution_observation({}))


class ResourceWaitTests(unittest.TestCase):
    def state(self, **changes):
        config = {**deepcopy(DEFAULT_CONFIG), **changes}
        instance = {**execution_profiles.build_profiles(config), 'config': config}
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        return instance, runtime, profile

    def test_zero_capacity_and_provider_probe_are_distinct_and_read_only(self):
        config = deepcopy(DEFAULT_CONFIG)
        for model in config['session_limits']['work']:
            config['session_limits']['work'][model] = 0
        instance, runtime, profile = self.state(**config)
        slots = SessionSlots(runtime, instance)
        wait = slots.admission_check(profile)['wait']
        self.assertEqual((wait['kind'], wait['next_owner']), ('capacity', 'user'))
        self.assertNotIn('retry_at', wait)
        provider = profile['ai']['provider']
        runtime['provider_waits']['PW-' + provider] = {'provider': provider, 'state': 'waiting',
            'retry_at': 100, 'probe_owner': None, 'probe_started_at': None}
        before = deepcopy(runtime)
        self.assertEqual(slots.admission_check(profile, current_time=90)['wait']['kind'], 'provider_limit')
        self.assertEqual(slots.admission_check(profile, current_time=110)['wait']['kind'], 'capacity')
        self.assertEqual(runtime, before)

    def test_configure_wakes_only_changed_resource_waits_and_keeps_pinned_profile(self):
        from engine_fixtures import governance_host
        e, _, _ = governance_host()
        e.instance['workspace'] = str(Path('.').resolve())
        e.instance['config']['session_limits']['work'] = {m: 0 for m in e.instance['config']['tier_models'].values()}
        e.instance.update(execution_profiles.build_profiles(e.instance['config']))
        e.runtime.update(status='waiting', queue=[{'id': 'AC-wait', 'role': 'goal_audit',
            'profile_ref': deepcopy(e.instance['role_profile_refs']['goal_audit'][0]),
            'dispatch_wait': {'kind': 'capacity', 'next_owner': 'user'}}])
        original = deepcopy(e.runtime['queue'][0]['profile_ref'])
        request = {'origin': 'user', 'config': {'session_limits': deepcopy(DEFAULT_CONFIG['session_limits'])}}
        _, state = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(state['status'], 'ready')
        self.assertNotIn('dispatch_wait', state['queue'][0])
        self.assertEqual(state['queue'][0]['profile_ref'], original)
        self.assertEqual(e.runtime['status'], 'waiting')
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'waiting')
        e.runtime['status'] = 'capacity_waiting'
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'capacity_waiting')
        e.runtime['status'] = 'paused'
        _, paused = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(paused['status'], 'paused')


if __name__ == "__main__":
    unittest.main()
