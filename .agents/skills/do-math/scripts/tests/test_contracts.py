from __future__ import annotations

import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts
from do_math.contracts import ROLES, reading_map, prompt_documents, render_prompt, schema_for


class ContractTests(unittest.TestCase):
    def test_knowledge_change_carries_declared_impact_and_typed_confirmation(self):
        from do_math import submission
        schema = submission.extension_schema({"role": "research_work"}, {})
        change = {"id": "KN-source", "changes": {"statement": "Corrected"},
                  "reason": "Correct the statement", "impact_set": ["TK-consumer"]}
        jsonschema.validate({"knowledge_changes": [change]}, schema)
        without_impact = {key: value for key, value in change.items() if key != "impact_set"}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate({"knowledge_changes": [without_impact]}, schema)
        confirmed = {**change, "independent_confirmation": {"plan_digest": "a" * 64,
            "decision": "approve", "review_ref": "RV-sealed", "reviewer_ref": "EX-reviewer",
            "producer_ref": "EX-producer", "affected_ids": ["TK-consumer"]}}
        jsonschema.validate({"knowledge_changes": [confirmed]}, schema)
        confirmed["independent_confirmation"]["plan_digest"] = "not-a-hash"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate({"knowledge_changes": [confirmed]}, schema)

    def test_exact_schema_identity_distinguishes_variants_and_is_idempotent(self):
        ordinary = contracts.action_schema({"role": "research_preparation"}, {})
        assessing = contracts.action_schema({"role": "research_preparation", "assessment_targets": []}, {})
        self.assertNotEqual(ordinary["$id"], assessing["$id"])
        self.assertEqual(ordinary, contracts.with_integration_schema(ordinary))
        self.assertNotEqual(contracts.schema_reference(ordinary), contracts.schema_reference(assessing))

    def test_profile_references_use_the_sealed_provider_identity(self):
        reference = {"id": "EP-test", "revision": 1, "sha256": "a" * 64}
        shapes = [contracts.TASK_CANDIDATE["properties"]["profile_refs"]["items"],
                  contracts.SCOPE_ASSESSMENT["properties"]["selected_profile_ref"]]
        for shape in shapes:
            self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(reference))
            for invalid in ("EP-test", {"id": "EP-test", "version": 1}, {**reference, "sha256": "wrong"}):
                self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid(invalid))

    def test_academic_resolution_carries_real_evidence_references(self):
        from do_math.submission import extension_schema
        shape = extension_schema({"role": "research_plan"}, {})["properties"]["academic_resolutions"]["items"]
        row = {"id": "ER-1", "decision": "resolved", "evidence": "Exact assessment", "evidence_refs": ["EX-evidence"]}
        self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(row))
        self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid({k: v for k, v in row.items() if k != "evidence_refs"}))

    def test_every_role_has_closed_schema(self):
        for role in ROLES:
            schema = schema_for(role)
            self.assertFalse(schema["additionalProperties"])
            self.assertTrue({"summary", "used_sources", "questions"} <= set(schema["required"]))
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_invalid_decisions_fail(self):
        base = {"summary": "Checked", "used_sources": [], "questions": [], "integration_bundles": [
            {"integration_id": "IN-review", "members": ["output"], "impact_set": [], "authority_refs": []}]}
        cases = {
            "task_contract_review": {"item_reviews": [{"item_id": item, "decision": "approved", "evidence_refs": ["TK-1"],
                "findings": [], "missing_inputs": [], "next_owner": "research_preparation"} for item in contracts.CONTRACT_REVIEW_ITEMS]},
            "identity_review": {"decision": "match", "findings": [], "scope_complete": True},
            "goal_audit": {"decision": "satisfied", "reason": "Checked evidence", "scope_complete": True},
            "operational_review": {"disposition": {"kind": "continue", "basis_refs": ["EX-1"],
                "next_owner": "worker", "reason": "Progress evidenced", "next_review": None}}}
        for role, fields in cases.items():
            value = {**base, **fields}
            validator = jsonschema.Draft202012Validator(schema_for(role))
            self.assertTrue(validator.is_valid(value), role)
            if role == "task_contract_review": value["item_reviews"][0]["decision"] = "invalid"
            elif role == "operational_review": value["disposition"]["kind"] = "invalid"
            else: value["decision"] = "invalid"
            self.assertFalse(validator.is_valid(value), role)

    def test_role_document_missing_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "계약").mkdir()
            source = Path(__file__).resolve().parents[2]
            shutil.copy2(source / "SKILL.md", root / "SKILL.md")
            shutil.copytree(source / "references", root / "references")
            (root / "GLOSSARY.md").write_text("x", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                prompt_documents("research_work", skill_root=root)

    def test_prompt_contains_actual_documents_context_and_schema(self):
        prompt = render_prompt("research_work", {"z": 1, "a": "입력"})
        self.assertIn("DOCUMENT SKILL.md", prompt)
        self.assertIn("DOCUMENT GLOSSARY.md", prompt)
        self.assertIn("DOCUMENT 계약/연구-수행.md", prompt)
        self.assertIn('{"a":"입력","z":1}', prompt)
        self.assertIn('"do-math-cli/5"', prompt)
        self.assertIn("without Markdown or text outside JSON", prompt)

    def test_declared_role_documents_are_complete(self):
        self.assertEqual(set(reading_map()), set(ROLES))

    def test_plan_assessment_fields_are_required(self):
        schema = schema_for("research_plan")
        self.assertTrue({"dispositions", "preparation_requests", "goal_audit", "task_assessments"} <= set(schema["required"]))
        self.assertFalse({"selections", "deferred"} & set(schema["properties"]))
        assessment = schema["properties"]["task_assessments"]["items"]
        self.assertEqual(set(assessment["required"]), {"task_id", "decision", "reason", "item_dispositions", "unresolved"})


if __name__ == "__main__":
    unittest.main()
