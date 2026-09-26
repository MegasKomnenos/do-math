"""Atomic knowledge-impact bundle regression tests."""
from copy import deepcopy
import hashlib
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash

from do_math import contracts, integration, knowledge_io, submission
from do_math.git_store import GitStateStore
from do_math.knowledge import content_hash
from do_math.repository import canonical_json
import test_redesign_CONTRACTS as contract_tests
from test_redesign_CONTRACTS import context


class ImpactBundleTests(unittest.TestCase):
    def setUp(self):
        fixture = contract_tests.ImpactReviewTests(methodName="test_request_cannot_relabel_the_original_producer_snapshot")
        fixture.setUp()
        self.instance = fixture.instance
        self.runtime = fixture.runtime
        self.ids = fixture.ids
        self.output = fixture.output
        self.extensions = fixture.extensions
        self.bundle = fixture.bundle
        self.review_output = fixture.review_output

    def _request(self):
        return integration.bundle_impact_request(
            self.instance,
            self.runtime,
            self.bundle,
            producer_execution_id="EX-producer",
            input_snapshot="fixed-input",
        )

    def _seal_review(self, request, *, used_sources=()):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        output = self.review_output(request)
        output["used_sources"] = list(used_sources)
        action = {
            "id": "AC-review",
            "role": "maintenance",
            "stage": "impact_review",
            "input_basis": {"impact_review": request},
        }
        fixed = {"action": action, "execution_id": "EX-review",
                 "knowledge_catalog": deepcopy(list(self.instance["knowledge"].values()))}
        review_bundle = next(integration.split_bundles(output, {}, fixed))
        output_ref = "runtime/artifacts/BA-review-output/output.json"
        extensions_ref = "runtime/artifacts/BA-review-output/extensions.json"
        check_ref = "runtime/artifacts/BA-review-output/check.json"
        schema = contracts.action_schema(action)
        check = submission.check_submission(output, schema, fixed, {}, root, mode="receiver",
            execution_id="EX-review", tool_sha256="a" * 64)
        self.assertTrue(check["passed"], check["issues"])
        output_raw, extensions_raw, check_raw = canonical_json(output), canonical_json({}), canonical_json(check)
        artifacts = {output_ref: output_raw, extensions_ref: extensions_raw, check_ref: check_raw}
        self.runtime["executions"]["EX-review"] = {
            "id": "EX-review",
            "role": "maintenance",
            "actor_kind": "ai",
            "status": "ended",
            "outcome": "output_accepted",
            "action": action,
            "input_bundle": "BA-review-input",
            "submission_intent": {"schema_ref": contracts.schema_reference(schema),
                "output_ref": output_ref, "extensions_ref": extensions_ref,
                "check_ref": check_ref, "output_sha256": hashlib.sha256(output_raw).hexdigest(),
                "extensions_sha256": hashlib.sha256(extensions_raw).hexdigest()},
            "submission_receipt": {"execution_id": "EX-review", "state": "accepted",
                "payload": {"submission_check": {"artifacts": [
                    {"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
                    for path, raw in artifacts.items()]}}},
        }
        self.runtime["integrations"] = {
            "IN-review": {
                "id": "IN-review",
                "execution_id": "EX-review",
                "payload_sha256": review_bundle["payload_sha256"],
                "response_sha256": exact_content_hash(
                    integration.member_values(output, {}, fixed)["output"]
                ),
            }
        }
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        store = GitStateStore(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        head = store.publish(
            None,
            {
                "research/fixture.json": b"{}",
                "runtime/artifacts/BA-review-input/input/submission/context.json": canonical_json(fixed),
                **artifacts,
            },
        ).head
        return {
            "producer_execution_id": "EX-producer",
            "input_snapshot": "fixed-input",
            "review_execution_id": "EX-review",
            "snapshot": head,
            "read_artifact": lambda snapshot, path: store.read_bytes(snapshot, path),
        }

    def test_coupled_changes_use_the_single_reviewed_s0_plan(self):
        first, dependent, second = self.ids
        self.instance["knowledge"][dependent]["dependencies"] = [first]
        self.instance = knowledge_io.ensure_ontology(self.instance)
        self.runtime["queue"] = []
        self.extensions["knowledge_changes"] = [
            {
                "id": dependent,
                "changes": {"summary": "Revised dependent"},
                "reason": "Correct dependent explanation",
                "impact_set": [],
            },
            {
                "id": first,
                "changes": {"summary": "Revised premise"},
                "reason": "Correct premise explanation",
                "impact_set": [dependent],
            },
        ]
        self.output["integration_bundles"][0]["impact_set"] = [dependent]
        self.output["integration_bundles"][0]["previous_hashes"] = {
            identifier: content_hash(self.instance["knowledge"][identifier])
            for identifier in (dependent, first)
        }
        self.bundle = next(integration.split_bundles(self.output, self.extensions, context()))
        before_instance = canonical_json(self.instance)
        before_runtime = canonical_json(self.runtime)
        request = self._request()
        args = self._seal_review(request)

        changed, running = integration.apply_reviewed_knowledge_changes(
            self.instance, self.runtime, self.bundle, actor_ref="EX-producer", **args
        )

        self.assertEqual(before_instance, canonical_json(self.instance))
        self.assertNotEqual(before_runtime, canonical_json(running))
        self.assertEqual(
            {dependent, first},
            {row["supersedes"] for row in changed["knowledge"].values() if row.get("supersedes")},
        )
        reassessments = [
            row
            for row in running["history"]
            if row.get("kind") == "knowledge_reassessment_required"
        ]
        self.assertEqual(1, len(reassessments))
        followups = [
            row
            for row in running["queue"]
            if row.get("role") == "research_plan" and row.get("affected_ids")
        ]
        self.assertEqual(1, len(followups))
        self.assertIn(dependent, followups[0]["affected_ids"])

    def test_bundle_level_reviewed_effect_is_applied_once(self):
        target = self.ids[0]
        task_id = "TK-external-premise"
        self.runtime["tasks"] = {
            task_id: {
                "id": task_id,
                "status": "open",
                "assessment": {"current": True, "basis": []},
            }
        }
        self.runtime["queue"] = []
        self.extensions = {
            "knowledge_changes": [
                {
                    "id": target,
                    "changes": {"summary": "Revised once"},
                    "reason": "Correct explanation",
                    "impact_set": [],
                }
            ]
        }
        self.output["integration_bundles"] = [
            {
                "integration_id": "IN-whole-only",
                "members": ["output", "activity-extensions.json/knowledge_changes/0"],
                "impact_set": [task_id],
                "authority_refs": [],
                "previous_hashes": {target: content_hash(self.instance["knowledge"][target])},
            }
        ]
        self.bundle = next(integration.split_bundles(self.output, self.extensions, context()))
        request = self._request()
        args = self._seal_review(request)

        changed, running = integration.apply_reviewed_knowledge_changes(
            self.instance, self.runtime, self.bundle, actor_ref="EX-producer", **args
        )

        self.assertFalse(running["tasks"][task_id]["assessment"]["current"])
        self.assertEqual(
            1,
            len(
                [
                    row
                    for row in running["history"]
                    if row.get("kind") == "knowledge_reassessment_required"
                ]
            ),
        )

    def test_review_rejects_changed_sealed_output_without_execution_output_copy(self):
        args = self._seal_review(self._request())
        original = args['read_artifact']
        args['read_artifact'] = lambda snapshot, path: (b'{"changed":true}'
            if path == self.runtime['executions']['EX-review']['submission_intent']['output_ref']
            else original(snapshot, path))
        with self.assertRaisesRegex(ValueError, 'sealed output_ref hash differs'):
            integration.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)

    def test_ordinary_execution_source_dependency_still_propagates(self):
        root = self.ids[0]
        self.runtime["executions"]["EX-consumer"] = {
            "id": "EX-consumer",
            "role": "research_work",
            "status": "ended",
            "output": {"used_sources": [root], "report": "Consumed the premise."},
        }
        self.runtime["executions"]["EX-other-review"] = {
            "id": "EX-other-review",
            "role": "maintenance",
            "status": "ended",
            "action": {
                "role": "maintenance",
                "stage": "impact_review",
                "input_basis": {"impact_review": {"integration_id": "IN-other"}},
            },
            "output": {"used_sources": [root], "report": "Reviewed a different assignment."},
        }
        from do_math import knowledge

        plan = knowledge.plan_impact(self.instance, self.runtime, [root], [])

        self.assertIn("EX-consumer", plan["computed_impact"])
        self.assertIn("EX-other-review", plan["computed_impact"])

    def test_external_premise_change_after_review_requires_a_new_judgment(self):
        request = self._request()
        args = self._seal_review(request, used_sources=[self.ids[0]])
        changed = deepcopy(self.instance)
        changed["knowledge"][self.ids[1]]["summary"] = "Externally changed premise"
        before_runtime = canonical_json(self.runtime)

        with self.assertRaisesRegex(ValueError, "current assignment"):
            integration.require_bundle_impact_review(changed, self.runtime, self.bundle, **args)

        self.assertEqual(before_runtime, canonical_json(self.runtime))

    def test_explicit_replacement_ids_support_forward_sibling_dependencies(self):
        first, dependent = self.ids[:2]
        new_first = "KN-01ARZ3NDEKTSV4RRFFQ69G5FAA"
        new_dependent = "KN-01ARZ3NDEKTSV4RRFFQ69G5FAB"
        changes = [
            {
                "id": dependent,
                "replacement_id": new_dependent,
                "changes": {"dependencies": [new_first]},
                "reason": "Use the replacement premise",
                "impact_set": [],
            },
            {
                "id": first,
                "replacement_id": new_first,
                "changes": {"summary": "Stable replacement premise"},
                "reason": "Correct the premise",
                "impact_set": [],
            },
        ]
        self.extensions = {"knowledge_changes": changes}
        self.output["integration_bundles"] = [
            {
                "integration_id": "IN-explicit-ids",
                "members": [
                    "output",
                    "activity-extensions.json/knowledge_changes/0",
                    "activity-extensions.json/knowledge_changes/1",
                ],
                "impact_set": [],
                "authority_refs": [],
                "previous_hashes": {
                    identifier: content_hash(self.instance["knowledge"][identifier])
                    for identifier in (dependent, first)
                },
            }
        ]
        self.bundle = next(integration.split_bundles(self.output, self.extensions, context()))
        before_instance = canonical_json(self.instance)
        before_runtime = canonical_json(self.runtime)

        changed, running = integration.apply_reviewed_knowledge_changes(
            self.instance,
            self.runtime,
            self.bundle,
            actor_ref="EX-producer",
            producer_execution_id="EX-producer",
            input_snapshot="fixed-input",
        )

        self.assertEqual([new_first], changed["knowledge"][new_dependent]["dependencies"])
        self.assertEqual(first, changed["knowledge"][new_first]["supersedes"])
        self.assertEqual(dependent, changed["knowledge"][new_dependent]["supersedes"])
        self.assertEqual(before_instance, canonical_json(self.instance))
        self.assertEqual(before_runtime, canonical_json(self.runtime))
        self.assertNotEqual(before_runtime, canonical_json(running))

    def test_replacement_id_schema_and_global_uniqueness_are_enforced(self):
        replacement_id = "KN-01ARZ3NDEKTSV4RRFFQ69G5FAC"
        row = {
            "id": self.ids[0],
            "replacement_id": replacement_id,
            "changes": {"summary": "Revised"},
            "reason": "Correct the record",
            "impact_set": [],
        }
        schema = submission.extension_schema({"role": "research_work"})
        self.assertEqual(
            [],
            list(jsonschema.Draft202012Validator(schema).iter_errors({"knowledge_changes": [row]})),
        )
        sibling = {
            "id": self.ids[1],
            "replacement_id": "KN-01ARZ3NDEKTSV4RRFFQ69G5FAD",
            "changes": {"dependencies": [replacement_id]},
            "reason": "Use the explicit sibling",
            "impact_set": [],
        }
        producer_output = deepcopy(self.output)
        producer_output["integration_bundles"] = [
            {
                "integration_id": "IN-producer-explicit-ids",
                "members": [
                    "output",
                    "activity-extensions.json/knowledge_changes/0",
                    "activity-extensions.json/knowledge_changes/1",
                    "activity-extensions.json/revision_resolutions/0",
                    "activity-extensions.json/revision_resolutions/1",
                ],
                "impact_set": [],
                "authority_refs": [],
            }
        ]
        producer_extensions = {
            "knowledge_changes": [sibling, row],
            "revision_resolutions": [
                {"record_id": identifier, "disposition": "revised", "reason": "Apply the declared revision"}
                for identifier in (self.ids[1], self.ids[0])
            ],
        }
        producer_action = {
            **context()["action"],
            "revision_targets": {identifier: {} for identifier in (self.ids[1], self.ids[0])},
        }
        producer_context = {
            **context(),
            "action": producer_action,
            "execution_id": "EX-producer",
            "knowledge_catalog": [{"id": identifier} for identifier in self.ids],
        }
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            response_schema = contracts.schema_for("research_work")
            submission.install_tools(workspace, producer_context, response_schema, None)
            draft = workspace / ".scratch/draft.json"
            draft.parent.mkdir()
            draft.write_bytes(canonical_json(producer_output))
            (workspace / "activity-extensions.json").write_bytes(canonical_json(producer_extensions))
            producer_check = submission.producer_check(workspace, draft)
            self.assertTrue(producer_check["passed"], producer_check["issues"])

        def bundle_for(rows):
            extensions = {"knowledge_changes": rows}
            self.output["integration_bundles"] = [
                {
                    "integration_id": "IN-id-rejection",
                    "members": ["output"] + [
                        f"activity-extensions.json/knowledge_changes/{index}"
                        for index in range(len(rows))
                    ],
                    "impact_set": [],
                    "authority_refs": [],
                    "previous_hashes": {
                        entry["id"]: content_hash(self.instance["knowledge"][entry["id"]])
                        for entry in rows
                    },
                }
            ]
            return next(integration.split_bundles(self.output, extensions, context()))

        original_instance = canonical_json(self.instance)
        original_runtime = canonical_json(self.runtime)
        duplicate = [
            row,
            {
                **row,
                "id": self.ids[1],
                "changes": {"summary": "Also revised"},
            },
        ]
        # import_candidate rejects the second use of one replacement ID.
        with self.assertRaisesRegex(ValueError, "already exists"):
            integration.apply_reviewed_knowledge_changes(
                self.instance,
                self.runtime,
                bundle_for(duplicate),
                actor_ref="EX-producer",
                producer_execution_id="EX-producer",
                input_snapshot="fixed-input",
            )
        reused = [{**row, "replacement_id": self.ids[2]}]
        with self.assertRaisesRegex(ValueError, "already exists"):
            integration.apply_reviewed_knowledge_changes(
                self.instance,
                self.runtime,
                bundle_for(reused),
                actor_ref="EX-producer",
                producer_execution_id="EX-producer",
                input_snapshot="fixed-input",
            )
        self.assertEqual(original_instance, canonical_json(self.instance))
        self.assertEqual(original_runtime, canonical_json(self.runtime))


if __name__ == "__main__":
    unittest.main()
