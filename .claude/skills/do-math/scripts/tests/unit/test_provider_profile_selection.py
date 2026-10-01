"""Execution profiles (``execution_profiles``, ``model_policy``, layer 2): immutable editions, selection and evidence.

A profile is a sealed edition (``EP-`` content hash) of one role's model,
observation mode, window, input limit, boundary rules, tools and capacity.
A call is pinned to one edition; configuration changes add editions and keep
the old ones registered. Selection looks only at the adopted editions a role
and task permit. Capability evidence ties provider facts to one edition and
one observed identity, and never widens what a help text proves.
"""
from copy import deepcopy
import json
import unittest

from do_math import contracts, execution_profiles, model_policy
from do_math.canonical import canonical_json
from do_math.initialization import capability_requirements
from do_math.observations import observation_rule_contract, tracker_config
from support.provider_inputs import PROFILE_CONFIG
from support.observation_inputs import observation_rule
from support.provider_probes import ObservedCalls


def profiles(**changes):
    from support.entry import entry
    _entry = entry()
    return execution_profiles.build_profiles({**PROFILE_CONFIG, "lean_command": ["lean-A"], **changes}, host=_entry.ports.host)


def role_profile(state, role, **ai):
    return next(p for p in state["execution_profiles"].values()
                if p["role"] == role and all(p.get("ai", {}).get(key) == value for key, value in ai.items()))


class SelectionTests(unittest.TestCase):
    def test_selection_cost_depends_on_allowed_profiles_not_retained_editions(self):
        from support.entry import entry
        _entry = entry()
        registry = {}
        for edition in range(12):
            config = {**deepcopy(PROFILE_CONFIG), "max_input_bytes": 500000 + edition,
                      "lean_command": ["fixture-no-lean"]}
            current = execution_profiles.build_profiles(config, host=_entry.ports.host)
            registry.update(current["execution_profiles"])
        allowed = current["role_profile_refs"]["maintenance"]
        instance = {"execution_profiles": registry, "role_profile_refs": current["role_profile_refs"]}
        before = deepcopy(registry)
        # Every call of the reference match counts, from any caller.
        with ObservedCalls(match_profile_ref=execution_profiles.match_profile_ref) as calls:
            chosen = model_policy.selection(config, {"role": "maintenance"}, {}, {}, instance=instance)
        self.assertIn(chosen["profile_ref"], allowed)
        self.assertGreater(calls.count("match_profile_ref"), 0)
        self.assertLessEqual(calls.count("match_profile_ref"), 2 * len(allowed))
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
            execution_profiles.select_profile(
                registry, {"role": "maintenance", "profile_ref": execution_profiles.profile_ref(old)},
                requirement, allowed_refs=allowed)

    def test_ai_selection_uses_adopted_editions_without_building_or_reading_lean(self):
        from support.entry import entry
        _entry = entry()
        config = {**deepcopy(PROFILE_CONFIG), "lean_command": ["fixture-no-lean"]}
        instance = execution_profiles.build_profiles(config, host=_entry.ports.host)
        registry = instance["execution_profiles"]
        with ObservedCalls(lean=execution_profiles._lean_contract, seal=execution_profiles.seal_profile) as calls:
            chosen = model_policy.selection(config, {"role": "maintenance"}, {}, {}, instance=instance)
        self.assertEqual(registry[chosen["profile_ref"]["id"]]["role"], "maintenance")
        self.assertIn(chosen["profile_ref"], instance["role_profile_refs"]["maintenance"])
        self.assertEqual(calls.count("lean"), 0, "AI selection read Lean")
        self.assertEqual(calls.count("seal"), 0)
        # The same probe sees both functions when profiles are authored.
        with ObservedCalls(lean=execution_profiles._lean_contract, seal=execution_profiles.seal_profile) as authoring:
            execution_profiles.build_profiles(config, host=_entry.ports.host)
        self.assertGreater(authoring.count("lean"), 0)
        self.assertGreater(authoring.count("seal"), 0)

    def test_selection_is_pinned_and_contract_allowlist_is_enforced(self):
        from support.entry import entry
        _entry = entry()
        state = execution_profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        action = {"role": "research_work", "model_assessment": {
            "difficulty": "low", "importance": "low", "reason": "bounded arithmetic"}}
        selected = model_policy.selection(PROFILE_CONFIG, action, {}, {}, instance=state)
        profile = execution_profiles.resolve_profile(state["execution_profiles"], selected["profile_ref"])
        self.assertEqual(execution_profiles.runtime_config(profile)["max_input_bytes"], 500000)
        with self.assertRaisesRegex(ValueError, "permitted role/model edition"):
            execution_profiles.select_profile(state["execution_profiles"], action, selected, allowed_refs=[])
        self.assertEqual(execution_profiles.select_profile(state["execution_profiles"], action, selected,
                         allowed_refs=[execution_profiles.profile_ref(profile)])["id"], profile["id"])
        broken = deepcopy(state["execution_profiles"])
        broken[profile["id"]]["ai"]["model"] = "different"
        # Lookup compares the reference only; an unsaved edit is caught by validate_profile.
        with self.assertRaisesRegex(ValueError, "execution profile content differs from its immutable identity"):
            execution_profiles.validate_profile(broken[profile["id"]])
        changed = {**deepcopy(PROFILE_CONFIG), "max_input_bytes": 400000}
        editions = execution_profiles.build_profiles(changed, host=_entry.ports.host)
        registry = {**state["execution_profiles"], **editions["execution_profiles"]}
        newest = model_policy.selection(changed, action, {}, {}, instance={
            "execution_profiles": registry, "role_profile_refs": editions["role_profile_refs"]})
        self.assertIn(newest["profile_ref"]["id"], editions["execution_profiles"])

    def test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist(self):
        old = profiles()
        profile = role_profile(old, "intent_interpretation", tier="high")
        changed = deepcopy(PROFILE_CONFIG)
        changed["tier_models"]["high"] = "replacement-model"
        selected = model_policy.selection(changed, {"role": "intent_interpretation",
                                                    "profile_ref": execution_profiles.profile_ref(profile)},
                                          {}, {}, instance=old)
        self.assertEqual(selected["model"], profile["ai"]["model"])
        low = role_profile(old, "intent_interpretation", tier="low")
        with self.assertRaisesRegex(ValueError, "explicit profile does not meet the role/task model requirement"):
            model_policy.selection(PROFILE_CONFIG, {"role": "intent_interpretation",
                                                    "profile_ref": execution_profiles.profile_ref(low)},
                                   {}, {}, instance=old)
        # Task allowlists govern work, while interpretation keeps its own profile.
        kept = model_policy.selection(PROFILE_CONFIG, {"role": "intent_interpretation", "target": "T",
                                                       "profile_ref": execution_profiles.profile_ref(profile)},
                                      {"T": {"profile_refs": []}}, {}, instance=old)
        self.assertEqual(kept["profile_ref"], execution_profiles.profile_ref(profile))
        work = role_profile(old, "research_work", tier="high")
        with self.assertRaisesRegex(ValueError, "permitted role/model edition"):
            model_policy.selection(PROFILE_CONFIG, {"role": "research_work", "target": "T",
                                                    "profile_ref": execution_profiles.profile_ref(work)},
                                   {"T": {"profile_refs": []}}, {}, instance=old)


class AuthoringTests(unittest.TestCase):
    def test_profile_authoring_rejects_missing_unknown_and_invalid_host_demands(self):
        from support.entry import entry
        _entry = entry()
        constraint = execution_profiles.host_constraint(host_id="fixture-host",
            limits={"jobs": 3, "memory_bytes": 4096, "cpu_rate_basis_points": 10000},
            control_reserve={"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000},
            authority_refs=["GS-fixture"])
        demands = {role: {"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000}
                   for role in execution_profiles.HOST_ROLES}
        config = {**deepcopy(PROFILE_CONFIG), "lean_command": ["fixture-no-lean"],
                  "host_resources": {"constraint": constraint, "demands_by_role": demands}}
        self.assertEqual(execution_profiles.build_profiles(config, host=_entry.ports.host)["host_capacity_ref"], constraint["id"])
        for defect, message in (("missing", "every capped role needs an explicit host demand"),
                                ("unknown", "host demands must name capped roles only"),
                                ("invalid", r"host amounts must be explicit nonnegative integers \(positive for a demand\)")):
            bad = deepcopy(config)
            rows = bad["host_resources"]["demands_by_role"]
            if defect == "missing":
                del rows["research_work"]
            elif defect == "unknown":
                rows["invented"] = deepcopy(rows["research_work"])
            else:
                rows["research_work"]["memory_bytes"] = 0
            with self.subTest(defect=defect), self.assertRaisesRegex(ValueError, message):
                execution_profiles.build_profiles(bad, host=_entry.ports.host)

    def test_normal_final_delivery_rendering_preserves_the_sealed_profile(self):
        from support.entry import entry
        _entry = entry()
        profile = role_profile(execution_profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host), "research_work")
        original = deepcopy(profile)
        role_prompt = contracts.render_prompt('research_work', {'action': {'role': 'research_work'}}, documents=[])
        delivered = execution_profiles.prepare_prompt(role_prompt, profile)
        self.assertIn('normal JSON final', delivered)
        self.assertIn('optional early submission', delivered)
        self.assertEqual(profile, original)
        self.assertEqual(execution_profiles.profile_ref(profile), execution_profiles.profile_ref(original))
        for rule in original['boundary']['rules']:
            self.assertIn(rule, delivered)
        changed = deepcopy(profile)
        changed['boundary']['rules'][0] = 'Use unassigned inputs.'
        # A changed rule changes the content hash, which the check reads first.
        with self.assertRaisesRegex(ValueError, "execution profile content differs from its immutable identity"):
            execution_profiles.validate_profile(changed)

    def test_modes_machine_fields_and_profile_rebinding(self):
        from support.entry import entry
        _entry = entry()
        state = execution_profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        mode = {p["role"]: p["observation"]["mode"] for p in state["execution_profiles"].values()}
        self.assertEqual(mode["research_work"], "event_driven")
        self.assertEqual(mode["identity_review"], "periodic")
        self.assertEqual(mode["operational_review"], "deadline_only")
        machine = role_profile(state, "formal_check")
        self.assertNotIn("ai", machine)
        execution = {"id": "EX-one", "role": "formal_check"}
        execution_profiles.bind_execution(execution, machine)
        self.assertIn("execution_profile_ref", execution)
        with self.assertRaisesRegex(ValueError, "execution role differs from profile"):
            execution_profiles.bind_execution(execution, role_profile(state, "trust_check"))
        # Another edition of the same role cannot take the execution either.
        other_edition = role_profile(execution_profiles.build_profiles({**PROFILE_CONFIG, "lean_command": ["lean-B"]}, host=_entry.ports.host),
                                     "formal_check")
        self.assertNotEqual(other_edition["id"], machine["id"])
        with self.assertRaisesRegex(ValueError, "an execution cannot change its profile"):
            execution_profiles.bind_execution(execution, other_edition)

    def test_research_profile_binds_all_implemented_signal_kinds_not_counter_names(self):
        from support.entry import entry
        _entry = entry()
        profile = role_profile(execution_profiles.build_profiles({**PROFILE_CONFIG, "tool_review_window_seconds": 60,
                               "self_check_response_window_seconds": 60}, host=_entry.ports.host), "research_work")
        rule = observation_rule(threshold=1, id="SC-attempts", required_evidence=["checkpoint.json"])
        config = tracker_config(profile, initial_self_check_rules=[rule])
        self.assertEqual(config["observation_rule_bindings"], observation_rule_contract())

    def test_profile_tools_are_authoritative_and_detached(self):
        state = profiles(scholarly_server={"command": "approved-old-server", "args": []})
        p = next(p for p in state["execution_profiles"].values() if p["actor_kind"] == "ai")
        args = execution_profiles.runner_tools(p)
        self.assertEqual(args["scholarly_server"]["command"], "approved-old-server")
        args["scholarly_server"]["command"] = "mutated"
        self.assertEqual(execution_profiles.runner_tools(p)["scholarly_server"]["command"], "approved-old-server")


class EvidenceTests(unittest.TestCase):
    def test_capability_evidence_does_not_promote_surface_to_job_proof(self):
        from support.entry import entry
        _entry = entry()
        profile = next(p for p in execution_profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host)["execution_profiles"].values()
                       if p["actor_kind"] == "ai")
        description = {"scope": "cli_command_surface_only", "verified": True,
            "identity": {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "test"}},
            "supported": {"jsonl": True, "model": True, "local_job_stop": True},
            "unknown": ["remote_termination"], "version_sha256": "c" * 64, "exec_help_sha256": "d" * 64}
        evidence = execution_profiles.capability_evidence(profile, description, observed_at="2026-09-20T00:00:00Z")
        self.assertEqual(evidence["execution_profile_ref"], execution_profiles.profile_ref(profile))
        self.assertEqual(evidence["capabilities"]["jsonl"]["status"], "supported")
        self.assertEqual(evidence["capabilities"]["local_job_stop"]["status"], "unknown")
        self.assertEqual(evidence["capabilities"]["remote_termination"]["status"], "unknown")

    def test_negative_job_fact_vetoes_next_matching_assignment(self):
        from support.entry import entry
        _entry = entry()
        state = profiles()
        p = role_profile(state, "maintenance")
        identity = {"host": {"node": "one"}, "cli_sha256": "a" * 64}
        positive = execution_profiles.capability_evidence(p, {"identity": identity, "verified": True,
            "scope": "cli_command_surface_only", "supported": {"jsonl": True, "model": True, "structured_output": True}},
            observed_at="2026-09-20T00:00:00Z")
        negative = execution_profiles.structural_failure_evidence(p, identity, observed_at="2026-09-20T00:00:01Z",
                                                                  execution_id="EX-failed", evidence_ref="failure.json")
        state["capability_evidence"] = {r["id"]: r for r in (positive, negative)}
        reference = execution_profiles.profile_ref(p)
        current = capability_requirements(state, reference, current_identity=identity, at="2026-09-20T00:00:02Z", host=_entry.ports.host)
        self.assertFalse(current["satisfied"], "actual structural failure did not block the next identical assignment")
        changed = {"host": {"node": "two"}, "cli_sha256": "a" * 64}
        other = execution_profiles.capability_evidence(p, {"identity": changed, "verified": True,
            "scope": "cli_command_surface_only", "supported": {"jsonl": True, "model": True, "structured_output": True}},
            observed_at="2026-09-20T00:00:02Z")
        state["capability_evidence"][other["id"]] = other
        self.assertTrue(capability_requirements(state, reference, current_identity=changed,
                        at="2026-09-20T00:00:03Z", host=_entry.ports.host)["satisfied"], "failure was generalized to a different host")

    def test_native_provider_observation_has_canonical_storage_projection(self):
        observation = {"stop_reason": "max_tokens", "usage": {"input_tokens": 4, "cost_usd": 0.125},
                       "operation_count": "unknown", "remote_termination": "unknown"}
        stored = execution_profiles.execution_observation({"provider_observation": observation})
        # Canonical JSON refuses floats: the reported cost stays inside the JSON string.
        canonical_json(stored)
        self.assertEqual(json.loads(stored["reported_fields_json"]), observation)
        self.assertEqual(stored["stop_reason"], "max_tokens")
        self.assertIsNone(execution_profiles.execution_observation({}))


if __name__ == "__main__":
    unittest.main()
