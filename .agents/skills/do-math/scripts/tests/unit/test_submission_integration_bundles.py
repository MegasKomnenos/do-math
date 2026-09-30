"""Integration bundles (``integration``, layer 2): how a producer response is split into bundles, checked,
previewed and applied.

``apply_bundles`` and ``preview_bundles`` take their domain callbacks as
arguments, so the bundle rules run on the product code while the test's
callbacks record what they were given. The one publication test applies
through the real ``ResearchRepository`` on the in-process Git fake, so every
publication passes the storage contract.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import activities, contracts, execution_profiles, integration, knowledge_io, model_policy, submission
from do_math.canonical import exact_content_hash
from do_math.repository import ResearchRepository
from record_fixtures import observation_knowledge, research_work_context, two_observation_output
from research_fixtures import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake, make_repository

EXPLICIT = 'revisions and partially accepted retries require explicit integration_bundles'


class DefaultBundleTests(unittest.TestCase):
    def setUp(self):
        self.context = {**research_work_context(), "execution_id": "EX-default", "action": {
            "id": "AC-default", "role": "research_work", "grant_id": "GR-default"},
            "grants": [{"id": "GR-default"}]}
        self.output = two_observation_output()
        self.output.pop("integration_bundles")

    def test_missing_manifest_is_one_deterministic_unit_without_editing_original(self):
        before = deepcopy(self.output)
        self.assertEqual(integration.inspect_bundles(self.output, {}, self.context), [])
        bundles = list(integration.split_bundles(self.output, {}, self.context))
        self.assertEqual(len(bundles), 1)
        self.assertEqual(set(bundles[0]["members"]), {"output", "output/knowledge/0", "output/knowledge/1"})
        self.assertEqual(bundles[0]["authority_refs"], ["GR-default"])
        self.assertEqual(bundles[0]["impact_set"], [])
        self.assertEqual(self.output, before)
        self.assertEqual(bundles, list(integration.split_bundles(deepcopy(self.output), {}, deepcopy(self.context))))
        changed = deepcopy(self.output)
        changed["report"] += " updated"
        self.assertNotEqual(bundles[0]["integration_id"],
                            list(integration.split_bundles(changed, {}, self.context))[0]["integration_id"])
        changed_context = {**self.context, "execution_id": "EX-other"}
        self.assertNotEqual(bundles[0]["integration_id"],
                            list(integration.split_bundles(self.output, {}, changed_context))[0]["integration_id"])

    def test_revision_and_partial_acceptance_still_require_explicit_declarations(self):
        cases = [({}, {**self.context, "accepted_integration_ids": ["IN-earlier"]}),
                 ({}, {**self.context, "accepted_response": {"response_sha256": "a" * 64}}),
                 ({}, {**self.context, "action": {**self.context["action"], "revision_targets": ["TK-old"]}}),
                 ({"knowledge_changes": [{"id": "KN-old"}]}, self.context),
                 ({"task_dispositions": [{"task_id": "TK-old"}]}, self.context)]
        for extensions, ctx in cases:
            with self.subTest(extensions=extensions, context=ctx):
                issues = integration.inspect_bundles(self.output, extensions, ctx)
                self.assertEqual([("integration.manifest", EXPLICIT)], [(r["rule_id"], r["message"]) for r in issues])
        preparation = {"candidates": [{"revises_task_id": "TK-old"}]}
        issues = integration.inspect_bundles(preparation, {}, self.context)
        self.assertEqual([("integration.manifest", EXPLICIT)], [(r["rule_id"], r["message"]) for r in issues])

    def test_explicit_split_stays_split_and_orphan_impact_fails_structurally(self):
        output = two_observation_output()
        self.assertEqual(len(list(integration.split_bundles(output, {}, self.context))), 2)
        self.assertEqual(integration.inspect_bundles(output, {}, self.context), [])
        output["integration_bundles"][0]["impact_set"] = ["read-source"]
        issues = integration.inspect_bundles(output, {}, self.context)
        self.assertTrue(any(r["rule_id"] == "integration.mutation_root" and r["integration_id"] == "IN-A"
                            for r in issues), issues)
        self.assertEqual(output["integration_bundles"][0]["impact_set"], ["read-source"])


class BundlePublicationTests(unittest.TestCase):
    def test_bundle_receipt_and_records_share_real_git_publication(self):
        """About 0.2-0.45 s, over the 0.2 s unit budget: three publications through the storage contract."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock = FakeClock()
            repo = ResearchRepository(make_repository(root), "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV", backend=make_fake(),
                                      clock=clock)
            profile_state = execution_profiles.build_profiles({
                "session_limits": model_policy.LIMITS, "tier_models": model_policy.MODELS,
                "observation_mode": "event_driven", "max_input_bytes": 500000,
                "effort": "medium", "operator_effort": "high", "operator_timeout_seconds": 600,
                "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False})
            instance, runtime = current_state({"knowledge": {}, "expositions": {},
                **{k: v for k, v in profile_state.items() if k != "role_profile_refs"}}, {"executions": {}})
            instance = knowledge_io.ensure_ontology(instance)
            activity = activities.open_activity(runtime, activity_id="AT-1", activity_kind="research_work",
                owner_ref="task", input_refs=[], opened_at="2026-09-20T00:00:00Z")
            profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
            execution = {"id": "EX-1", "role": "research_work", "actor_kind": "ai", "owner_activity_id": "AT-1",
                "created_at": "2026-09-20T00:00:00Z", "status": "running", "input_manifest": [], "context_origin": []}
            execution_profiles.bind_execution(execution, profile)
            runtime["executions"]["EX-1"] = execution
            activity["assigned_execution_ids"] = ["EX-1"]
            head = repo.initialize(instance, runtime)

            def publish(i, r, bundle, validated):
                nonlocal head
                head = repo.save_validated(head, validated)[0]

            def apply(i, r, bundle):
                for record in bundle["output"]["knowledge"]:
                    updated, running, _ = knowledge_io.import_candidate(i, r, record, source_ref="EX-1",
                                                                        actor_ref="EX-1", clock=clock)
                    i.clear()
                    i.update(updated)
                    r.clear()
                    r.update(running)

            def validate(i, r, bundle):
                return repo.validate_candidate(i, r, head)
            before = deepcopy((instance, runtime))
            preview = integration.preview_bundles(instance, runtime, two_observation_output(), {},
                research_work_context(), execution_id="EX-1",
                apply_bundle=apply, validate_current=lambda *a: None, validate_candidate=validate)
            self.assertEqual("accepted", preview["status"], preview)
            self.assertEqual(before, (instance, runtime))
            self.assertEqual(head, repo._store.read_snapshot().head)
            first = two_observation_output()
            first["knowledge"][1]["kind"] = "undefined_kind"
            result = integration.apply_bundles(instance, runtime, first, {}, research_work_context(),
                execution_id="EX-1", apply_bundle=apply, validate_current=lambda *a: None,
                validate_candidate=validate, publish=publish)
            self.assertEqual("partial", result["status"], result)
            self.assertEqual(["IN-B"], result["retry_bundle_ids"])
            partial_head, partial_instance, partial_runtime = repo.load()
            self.assertEqual({"A"}, {row["title"] for row in partial_instance["knowledge"].values()})
            receipt = partial_runtime["integrations"]["IN-A"]
            retry = two_observation_output()
            retry["knowledge"] = [observation_knowledge("B")]
            retry["integration_bundles"] = [{"integration_id": "IN-B", "members": ["output/knowledge/0"],
                                             "impact_set": [], "authority_refs": []}]
            retry_context = {**research_work_context(), "accepted_response": {
                "integration_id": receipt["id"], "response_sha256": receipt["response_sha256"]}}
            result = integration.apply_bundles(partial_instance, partial_runtime, retry, {}, retry_context,
                execution_id="EX-1", apply_bundle=apply, validate_current=lambda *a: None,
                validate_candidate=validate, publish=publish)
            saved_head, saved_instance, saved_runtime = repo.load()
            self.assertEqual("accepted", result["status"], result["bundles"])
            self.assertEqual(head, saved_head)
            self.assertEqual({"A", "B"}, {row["title"] for row in saved_instance["knowledge"].values()})
            self.assertEqual({"IN-A", "IN-B"}, set(saved_runtime["integrations"]))
            # The legacy test read the parent with ``git rev-parse <head>^``: the final commit's only
            # parent is the partial publication, which holds A's record and receipt and nothing of B.
            self.assertEqual(head, repo._store.first_descendant(partial_head, head))
            _, parent_instance, parent_runtime = repo.load(partial_head)
            self.assertEqual({"A"}, {row["title"] for row in parent_instance["knowledge"].values()})
            self.assertEqual({"IN-A"}, set(parent_runtime["integrations"]))


class BundleApplicationTests(unittest.TestCase):
    def test_local_schema_failure_does_not_block_valid_bundle(self):
        output = two_observation_output()
        del output["knowledge"][1]["statement"]
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"),
                                               research_work_context(), {}, Path(directory))
        self.assertEqual({"IN-B"}, {row.get("integration_id") for row in issues})
        result = integration.apply_bundles({}, {}, output, {}, research_work_context(), execution_id="EX-1",
            apply_bundle=lambda i, r, b: i.update({b["integration_id"]: True}),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None, publish=lambda *a: None,
            submission_issues=issues)
        self.assertEqual({"IN-A": True}, result["instance"])

    def test_structural_failure_never_crashes_on_wrong_record_type(self):
        output = two_observation_output()
        output["knowledge"][0] = None
        issues = integration.inspect_bundles(output, {}, research_work_context())
        self.assertIsInstance(issues, list)

    def test_structural_top_level_failure_returns_without_candidate_application(self):
        for output, extensions in ((None, {}), ([], {}), (two_observation_output(), [])):
            with self.subTest(output=type(output).__name__, extensions=type(extensions).__name__):
                result = integration.apply_bundles({"original": True}, {}, output, extensions,
                    research_work_context(), execution_id="EX-1",
                    apply_bundle=lambda *a: self.fail("Malformed candidate applied"),
                    validate_current=lambda *a: self.fail("Malformed candidate validated"),
                    validate_candidate=lambda *a: self.fail("Malformed candidate validated"),
                    publish=lambda *a: self.fail("Malformed candidate published"))
                self.assertEqual("returned", result["status"])
                self.assertTrue(result["issues"])
                self.assertEqual({"original": True}, result["instance"])

    def test_proposed_kind_and_consumer_must_share_bundle(self):
        output = two_observation_output()
        output["knowledge"][0]["kind"] = "experiment"
        output["integration_bundles"][1]["members"].append("activity-extensions.json/kind_definitions/0")
        extensions = {"kind_definitions": [{"family": "knowledge", "token": "experiment", "meaning": "experiment",
                                            "constraints": {}}]}
        issues = integration.inspect_bundles(output, extensions, research_work_context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_preview_applies_candidate_without_publishing_or_mutating_input(self):
        original = {}
        preview = integration.preview_bundles(original, {}, two_observation_output(), {}, research_work_context(),
            execution_id="EX-1", apply_bundle=lambda i, r, b: i.update({b["integration_id"]: True}),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None)
        self.assertEqual({}, original)
        self.assertEqual({"IN-A": True, "IN-B": True}, preview["instance"])
        self.assertEqual("preview", preview["mode"])

    def test_missing_member_is_rejected(self):
        output = two_observation_output()
        output["integration_bundles"][1]["members"] = ["output/relations/0"]
        issues = integration.inspect_bundles(output, {}, research_work_context())
        self.assertIn("integration.members", {row["rule_id"] for row in issues})

    def test_cross_bundle_new_reference_requires_merge(self):
        output = two_observation_output()
        output["knowledge"][1]["dependencies"] = ["A"]
        issues = integration.inspect_bundles(output, {}, research_work_context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_metadata_cannot_split_from_its_new_record(self):
        output = two_observation_output()
        output["integration_bundles"][1]["members"].append("activity-extensions.json/knowledge_metadata/0")
        issues = integration.inspect_bundles(output, {"knowledge_metadata": [{"title": "A"}]}, research_work_context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_plan_is_one_bundle(self):
        output = two_observation_output()
        ctx = research_work_context()
        ctx["action"]["role"] = "research_plan"
        issues = integration.inspect_bundles(output, {}, ctx)
        self.assertIn("integration.single_bundle", {row["rule_id"] for row in issues})

    def test_failed_candidate_does_not_undo_other_bundle(self):
        original = {"knowledge": {}}
        publications = []

        def apply(instance, runtime, bundle):
            for record in bundle["output"]["knowledge"]:
                instance["knowledge"][record["title"]] = record

        def validate(instance, runtime, bundle):
            if "B" in instance["knowledge"]:
                raise ValueError("B rejected")
        result = integration.apply_bundles(original, {}, two_observation_output(), {}, research_work_context(),
            execution_id="EX-1", apply_bundle=apply, validate_candidate=validate, validate_current=lambda *a: None,
            publish=lambda i, r, b, validated: publications.append(deepcopy(i)))
        self.assertEqual(["accepted", "returned"], [r["status"] for r in result["bundles"]])
        self.assertEqual({"A"}, set(result["instance"]["knowledge"]))
        self.assertEqual({"knowledge": {}}, original)
        self.assertEqual(1, len(publications))
        self.assertIn("IN-B", result["retry_bundle_ids"])
        self.assertEqual(result["bundles"][1]["issues"], result["issues"])

    def test_receipt_is_published_with_state_and_replay_has_no_effect(self):
        published = []
        calls = []
        kwargs = dict(execution_id="EX-1", apply_bundle=lambda i, r, b: calls.append(b["integration_id"]),
                      validate_candidate=lambda *a: None, validate_current=lambda *a: None,
                      publish=lambda i, r, b, validated: published.append(deepcopy(r)))
        first = integration.apply_bundles({}, {}, two_observation_output(), {}, research_work_context(), **kwargs)
        self.assertIn("IN-A", published[0]["integrations"])
        second = integration.apply_bundles(first["instance"], first["runtime"], two_observation_output(), {},
                                           research_work_context(), **kwargs)
        self.assertEqual(2, len(calls))
        self.assertTrue(all(r["status"] == "already_accepted" for r in second["bundles"]))

    def test_retry_only_failed_bundle_does_not_repeat_response_finalization(self):
        output = two_observation_output()
        base = integration.member_values(output, {}, research_work_context())["output"]
        output["knowledge"] = [output["knowledge"][1]]
        output["integration_bundles"] = [dict(integration_id="IN-B", members=["output/knowledge/0"], impact_set=[],
                                              authority_refs=[])]
        ctx = {**research_work_context(), "accepted_response": {"integration_id": "IN-A",
                                                                "response_sha256": exact_content_hash(base)}}
        self.assertEqual([], integration.inspect_bundles(output, {}, ctx))
        calls = []
        result = integration.apply_bundles({}, {}, output, {}, ctx, execution_id="EX-2",
            apply_bundle=lambda i, r, b: calls.append(b["owns_response"]),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None, publish=lambda *a: None)
        self.assertEqual("accepted", result["status"])
        self.assertEqual([False], calls)

    def test_current_authority_failure_precedes_mutation(self):
        calls = []

        def denied(*args):
            raise ValueError("authority revoked")
        result = integration.apply_bundles({}, {}, two_observation_output(), {}, research_work_context(),
            execution_id="EX-1", apply_bundle=lambda *a: calls.append(1), validate_candidate=lambda *a: None,
            validate_current=denied, publish=lambda *a: calls.append(2))
        self.assertEqual([], calls)
        self.assertEqual(["IN-A", "IN-B"], result["retry_bundle_ids"])

    def test_publish_failure_does_not_claim_acceptance(self):
        def conflict(*args):
            raise ValueError("CAS conflict")
        result = integration.apply_bundles({}, {}, two_observation_output(), {}, research_work_context(),
            execution_id="EX-1", apply_bundle=lambda i, r, b: i.update(changed=True),
            validate_candidate=lambda *a: None, validate_current=lambda *a: None, publish=conflict)
        self.assertEqual({}, result["instance"])
        self.assertFalse(result["runtime"].get("integrations"))
        self.assertTrue(all(r["status"] == "returned" for r in result["bundles"]))
        self.assertEqual("returned", result["status"])


if __name__ == "__main__":
    unittest.main()
