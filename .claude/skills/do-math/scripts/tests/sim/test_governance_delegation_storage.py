"""A delegation application stored and reloaded through the repository (``delegations``, ``repository``), moved from ``test_delegations``.

The legacy test initialized an instance with one source through the public
``initialize`` on a real Git repository (``research_fixtures.new_instance``) and
saved and reloaded the state through ``ResearchRepository``. Here the public
``initialize`` runs on a Sim (``Sim(root, sources=...)``), and the repository is
the Sim engine's ``ResearchRepository`` over the Git port's fake; every save
passes the storage contract.
"""
from pathlib import Path
import tempfile
import unittest

from do_math import activities, execution_lifecycle, execution_profiles, governance
from do_math.delegations import authorize_delegated_case, prepare_application, record_judgment
from support.sim import Sim


class DelegationStorageTests(unittest.TestCase):
    def test_structured_reference_survives_git_and_stales_when_its_record_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "source.txt"
            source_path.write_text("The original source bytes.", encoding="utf-8")
            sim = Sim(root / "sim", goal="Preserve an independently checked delegated case.", sources=[source_path])
            store = sim.engine.store
            head, instance, runtime = store.load()
            source_id = instance["sources"][0]["id"]
            instance.setdefault("governance_sources", {})["GS-delegation"] = governance.preserve_source(
                "GS-delegation", "User authorizes this bounded delegated grant case.", origin="user")
            instance, runtime, _ = governance.apply_decision(instance, runtime,
                {"kind": "grant", "decision_id": "DC-original", "grant": {
                    "id": "GR-original", "kind": "local", "roles": ["maintenance"], "reuse": "reusable"}},
                source_ref="GS-delegation", clock=sim.ports.clock)
            instance, runtime, _ = governance.apply_decision(instance, runtime,
                {"kind": "delegation", "decision_id": "DC-delegation", "delegation": {
                    "id": "DG-source", "status": "active", "decision_kind": "grant",
                    "original_decision_id": "DC-original", "included_targets": [source_id],
                    "excluded_targets": [], "external_effects": [], "resource_limits": {}, "expires_at": None}},
                source_ref="GS-delegation", clock=sim.ports.clock)
            case = {"id": "CASE-source", "decision_kind": "grant", "target_id": source_id,
                    "external_effects": [], "resources": {}, "effect": {"operation": "bounded source review"},
                    "basis_refs": [{"id": source_id}]}
            application = prepare_application(instance, runtime, "DG-source", case, now_iso=sim.ports.clock.now())
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)

            profile = next(profile for profile in instance["execution_profiles"].values()
                           if profile["role"] == "intent_interpretation")
            for stage, suffix in (("interpret", "one"), ("check", "two")):
                activity_id, execution_id = "AY-judgment-" + suffix, "EX-judgment-" + suffix
                activities.open_activity(runtime, activity_id=activity_id, activity_kind="delegation_judgment",
                                         owner_ref=application["id"], input_refs=[], opened_at="2026-09-21T00:00:00Z")
                execution = execution_lifecycle.create_execution(
                    execution_id=execution_id, owner_activity_id=activity_id, actor_kind="ai",
                    input_manifest={}, profile_ref=execution_profiles.profile_ref(profile),
                    created_at="2026-09-21T00:00:00Z")
                execution.update(role="intent_interpretation", delegation_input_sha256=application["input_sha256"])
                activities.assign_execution(runtime, activity_id, execution)
                record_judgment(runtime, application["id"],
                    {"input_sha256": application["input_sha256"], "decision": "within_scope",
                     "reason": "The checked case remains within the preserved grant decision."},
                    execution_id=execution_id, stage=stage)
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)
            allowed = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime, now_iso=sim.ports.clock.now())
            self.assertTrue(allowed["allowed"], allowed)

            instance["sources"][0]["revision"] = 2
            head = store.save_with_state(head, instance, runtime)[0]
            _, instance, runtime = store.load(head)
            rejected = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime, now_iso=sim.ports.clock.now())
            self.assertFalse(rejected["allowed"])
            self.assertEqual(rejected["reason"], "delegation application stale")


if __name__ == '__main__':
    unittest.main()
