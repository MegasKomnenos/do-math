from __future__ import annotations

import sys
import tempfile
import shutil
import unittest
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts
from do_math.contracts import ROLES, reading_map, prompt_documents, render_prompt, schema_for
from research_fixtures import review_items
from record_fixtures import two_observation_output


class ContractTests(unittest.TestCase):
    def test_knowledge_change_requires_a_declared_impact_set(self):
        from do_math import submission
        schema = submission.extension_schema({"role": "research_work"})
        change = {"id": "KN-source", "changes": {"statement": "Corrected"},
                  "reason": "Correct the statement", "impact_set": ["TK-consumer"]}
        jsonschema.validate({"knowledge_changes": [change]}, schema)
        without_impact = {key: value for key, value in change.items() if key != "impact_set"}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate({"knowledge_changes": [without_impact]}, schema)

    def test_exact_schema_identity_distinguishes_variants_and_is_idempotent(self):
        ordinary = contracts.action_schema({"role": "research_preparation"})
        assessing = contracts.action_schema({"role": "research_preparation", "assessment_targets": []})
        self.assertNotEqual(ordinary["$id"], assessing["$id"])
        self.assertEqual(ordinary, contracts.with_integration_schema(ordinary))
        self.assertNotEqual(contracts.schema_reference(ordinary), contracts.schema_reference(assessing))

    def test_profile_references_use_the_sealed_provider_identity(self):
        reference = {"id": "EP-test", "revision": 1, "sha256": "a" * 64}
        from do_math import review_cycle
        scope = review_cycle.stage_schema("scope")["properties"]["scope_assessment"]
        shapes = [contracts.TASK_CANDIDATE["properties"]["profile_refs"]["items"],
                  scope["properties"]["selected_profile_ref"]]
        for shape in shapes:
            self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(reference))
            for invalid in ("EP-test", {"id": "EP-test", "version": 1}, {**reference, "sha256": "wrong"}):
                self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid(invalid))

    def test_academic_resolution_carries_real_evidence_references(self):
        from do_math.submission import extension_schema
        shape = extension_schema({"role": "research_plan"})["properties"]["academic_resolutions"]["items"]
        row = {"id": "ER-1", "decision": "resolved", "evidence": "Exact assessment", "evidence_refs": ["EX-evidence"]}
        self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(row))
        self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid({k: v for k, v in row.items() if k != "evidence_refs"}))

    def test_schema_builders_return_copies_that_share_no_node(self):
        """A builder's result shares no container with a module global or within itself.

        A caller may then change any node in place without changing another
        field of the same schema or a schema built later in the process.
        """
        from do_math import governance, integration, record_schemas, review_cycle, scheduled_operator, submission

        def containers(value):
            found, pending = [], [value]
            while pending:
                node = pending.pop()
                if isinstance(node, (dict, list)):
                    found.append(node)
                    pending.extend(node.values() if isinstance(node, dict) else node)
            return found

        request = {"integration_id": "IN-1", "payload_sha256": "a" * 64, "producer_execution_id": "EX-1",
                   "input_snapshot": "b" * 40, "plans": {"scope": {"digest": "c" * 64}}}
        built = {
            **{"schema_for " + role: schema_for(role) for role in ROLES},
            **{"action_schema " + role: contracts.action_schema({"role": role})
               for role in ("research_preparation", "research_work", "maintenance", "intent_interpretation")},
            "disposition_schema": contracts.disposition_schema(),
            "extension_schema": submission.extension_schema({"role": "research_work", "review_cycle_id": "RC-1"}),
            "impact_review_response_schema": integration.impact_review_response_schema(request),
            **{"stage_schema " + stage: review_cycle.stage_schema(stage)
               for stage in ("scope", "initial", "organize", "answer", "judge")},
            "research_schema": review_cycle.research_schema(),
            "research_request_schema": review_cycle.research_request_schema(),
            **{"interpretation_schema " + stage: governance.interpretation_schema(stage) for stage in ("interpret", "check")},
            "config_schema": record_schemas.config_schema(),
            "repair_report_schema": scheduled_operator.repair_report_schema(diagnosed=True),
        }
        global_nodes = set()
        for name, module in list(sys.modules.items()):
            if name == "do_math" or name.startswith("do_math."):
                for value in vars(module).values():
                    global_nodes.update(id(node) for node in containers(value))
        for name, schema in built.items():
            with self.subTest(builder=name):
                nodes = [id(node) for node in containers(schema)]
                self.assertEqual(len(nodes), len(set(nodes)), "a node appears twice in the result")
                self.assertFalse(global_nodes & set(nodes), "the result holds a module-global node")

    def test_every_role_has_closed_schema(self):
        """Every object with declared properties, at any depth, rejects fields it does not declare."""
        def objects(node, path):
            if isinstance(node, dict):
                if "properties" in node:
                    yield path, node
                for key, value in node.items():
                    yield from objects(value, path + "/" + key)
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    yield from objects(value, f"{path}/{index}")
        for role in ROLES:
            schema = schema_for(role)
            for path, node in objects(schema, role):
                with self.subTest(path=path):
                    self.assertIs(node.get("additionalProperties"), False)
            self.assertTrue({"summary", "used_sources", "questions"} <= set(schema["required"]))
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_invalid_decisions_fail(self):
        base = {"summary": "Checked", "used_sources": [], "questions": [], "integration_bundles": [
            {"integration_id": "IN-review", "members": ["output"], "impact_set": [], "authority_refs": []}]}
        cases = {
            "task_contract_review": review_items(["TK-1"], next_owner="research_preparation"),
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
        assessment = schema["properties"]["task_assessments"]["items"]
        self.assertEqual(set(assessment["required"]), {"task_id", "decision", "reason", "item_dispositions", "unresolved"})

    def test_structured_task_candidate_has_one_completion_authority(self):
        props = contracts.schema_for("research_preparation")["properties"]["candidates"]["items"]["properties"]
        self.assertIn("completion_obligations", props)
        self.assertEqual("object", props["scope"]["type"])

    def test_operational_response_uses_six_dispositions(self):
        props = contracts.schema_for("operational_review")["properties"]
        self.assertIn("disposition", props)

    def test_specialized_role_schema_uses_same_envelope(self):
        from do_math import governance
        schema = contracts.action_schema({"role": "intent_interpretation", "stage": "check"})
        expected = governance.interpretation_schema("check")
        self.assertTrue(set(expected["properties"]) <= set(schema["properties"]))
        self.assertIn("integration_bundles", schema["properties"])
        self.assertNotIn("integration_bundles", schema["required"])

    def test_scope_planning_schema_reaches_domain_scope_validator(self):
        from do_math import review_cycle
        props = review_cycle.stage_schema("scope")["properties"]
        self.assertIn("scope_assessment", props)
        self.assertIn("initial_slots", props["scope_assessment"]["properties"])

    def test_manifest_is_optional_but_explicit_declarations_remain_typed(self):
        schema = contracts.schema_for("research_work")
        self.assertNotIn("integration_bundles", schema["required"])
        validator = __import__("jsonschema").Draft202012Validator(schema)
        output = two_observation_output(); output.pop("integration_bundles")
        self.assertEqual(list(validator.iter_errors(output)), [])
        for value in (None, [], [{}]):
            with self.subTest(value=value):
                self.assertTrue(list(validator.iter_errors({**output, "integration_bundles": value})))


if __name__ == "__main__":
    unittest.main()
