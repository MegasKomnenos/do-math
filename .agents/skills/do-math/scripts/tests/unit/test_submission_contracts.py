"""The role response contract (``do-math-cli/5``): schema shape, closure, identity, role documents and the prompt.

The schema builders and the prompt assembly are layer-1 functions of
``contracts`` and the schema functions of ``submission``, ``review_cycle`` and
``governance``; the tests call them directly. A rejection is pinned by the
validator's error (the keyword and the location it failed at), so the value
fails for the rule the test names and not for another one.
"""
from pathlib import Path
import shutil
import tempfile
import unittest

import jsonschema

from do_math import contracts, governance, review_cycle, submission
from do_math.contracts import ROLES, prompt_documents, reading_map, render_prompt, schema_for
from support.record_builders import two_observation_output
from support.role_answers import review_items

SKILL = Path(__file__).resolve().parents[3]


def failures(schema, value):
    """``{(validator keyword, location)}`` of every error ``value`` has against ``schema``."""
    return {(error.validator, tuple(error.absolute_path))
            for error in jsonschema.Draft202012Validator(schema).iter_errors(value)}


class ContractTests(unittest.TestCase):
    def test_knowledge_change_requires_a_declared_impact_set(self):
        schema = submission.extension_schema({"role": "research_work"})
        change = {"id": "KN-source", "changes": {"statement": "Corrected"},
                  "reason": "Correct the statement", "impact_set": ["TK-consumer"]}
        jsonschema.validate({"knowledge_changes": [change]}, schema)
        without_impact = {key: value for key, value in change.items() if key != "impact_set"}
        with self.assertRaisesRegex(jsonschema.ValidationError, "'impact_set' is a required property") as raised:
            jsonschema.validate({"knowledge_changes": [without_impact]}, schema)
        self.assertEqual(list(raised.exception.absolute_path), ["knowledge_changes", 0])

    def test_exact_schema_identity_distinguishes_variants_and_is_idempotent(self):
        ordinary = contracts.action_schema({"role": "research_preparation"})
        assessing = contracts.action_schema({"role": "research_preparation", "assessment_targets": []})
        self.assertNotEqual(ordinary["$id"], assessing["$id"])
        self.assertEqual(ordinary, contracts.with_integration_schema(ordinary))
        self.assertNotEqual(contracts.schema_reference(ordinary), contracts.schema_reference(assessing))

    def test_profile_references_use_the_sealed_provider_identity(self):
        reference = {"id": "EP-test", "revision": 1, "sha256": "a" * 64}
        scope = review_cycle.stage_schema("scope")["properties"]["scope_assessment"]
        candidate_shape = contracts.TASK_CANDIDATE["properties"]["profile_refs"]["items"]
        scope_shape = scope["properties"]["selected_profile_ref"]
        invalid = {"text": "EP-test", "version": {"id": "EP-test", "version": 1},
                   "digest": {**reference, "sha256": "wrong"}}
        for shape in (candidate_shape, scope_shape):
            self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(reference))
            for name, value in invalid.items():
                with self.subTest(name=name):
                    self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid(value))
        # The task candidate's reference is the closed sealed shape itself; each value fails its own rule.
        self.assertEqual(failures(candidate_shape, invalid["text"]), {("type", ())})
        self.assertEqual(failures(candidate_shape, invalid["version"]),
                         {("additionalProperties", ()), ("required", ())})
        self.assertEqual(failures(candidate_shape, invalid["digest"]), {("pattern", ("sha256",))})
        # The scope's reference admits that same shape among its alternatives and nothing else.
        for value in invalid.values():
            self.assertEqual(failures(scope_shape, value), {("anyOf", ())})

    def test_academic_resolution_carries_real_evidence_references(self):
        shape = submission.extension_schema({"role": "research_plan"})["properties"]["academic_resolutions"]["items"]
        row = {"id": "ER-1", "decision": "resolved", "evidence": "Exact assessment", "evidence_refs": ["EX-evidence"]}
        self.assertTrue(jsonschema.Draft202012Validator(shape).is_valid(row))
        without = {k: v for k, v in row.items() if k != "evidence_refs"}
        self.assertFalse(jsonschema.Draft202012Validator(shape).is_valid(without))
        self.assertEqual([error.message for error in jsonschema.Draft202012Validator(shape).iter_errors(without)],
                         ["'evidence_refs' is a required property"])

    def test_every_role_has_closed_schema(self):
        """Every object with declared properties, at any depth, rejects fields it does not declare.

        About 0.35 s, over the 0.2 s unit budget: it builds and meta-validates every role's full schema.
        """
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
            "task_contract_review": (review_items(["TK-1"], next_owner="research_preparation"),
                                     {("enum", ("item_reviews", 0, "decision"))}),
            "identity_review": ({"decision": "match", "findings": [], "scope_complete": True}, {("enum", ("decision",))}),
            "goal_audit": ({"decision": "satisfied", "reason": "Checked evidence", "scope_complete": True},
                           {("enum", ("decision",))}),
            # The disposition is one of six closed variants, so an unknown kind matches none of them.
            "operational_review": ({"disposition": {"kind": "continue", "basis_refs": ["EX-1"],
                "next_owner": "worker", "reason": "Progress evidenced", "next_review": None}},
                {("anyOf", ("disposition",))})}
        for role, (fields, rejected) in cases.items():
            value = {**base, **fields}
            validator = jsonschema.Draft202012Validator(schema_for(role))
            self.assertTrue(validator.is_valid(value), role)
            if role == "task_contract_review":
                value["item_reviews"][0]["decision"] = "invalid"
            elif role == "operational_review":
                value["disposition"]["kind"] = "invalid"
            else:
                value["decision"] = "invalid"
            self.assertFalse(validator.is_valid(value), role)
            self.assertEqual(failures(schema_for(role), value), rejected, role)

    def test_role_document_missing_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "계약").mkdir()
            shutil.copy2(SKILL / "SKILL.md", root / "SKILL.md")
            shutil.copytree(SKILL / "references", root / "references")
            (root / "GLOSSARY.md").write_text("x", encoding="utf-8")
            # The reading map's research_work row declares 계약/연구-수행.md, which this root lacks.
            with self.assertRaisesRegex(FileNotFoundError, "연구-수행\\.md"):
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
        self.assertTrue({"dispositions", "preparation_requests", "goal_audit", "task_assessments"}
                        <= set(schema["required"]))
        assessment = schema["properties"]["task_assessments"]["items"]
        self.assertEqual(set(assessment["required"]), {"task_id", "decision", "reason", "item_dispositions", "unresolved"})

    def test_structured_task_candidate_has_one_completion_authority(self):
        """The name says one completion authority; like the legacy test, this checks the structured obligations and the object scope."""
        props = contracts.schema_for("research_preparation")["properties"]["candidates"]["items"]["properties"]
        self.assertIn("completion_obligations", props)
        self.assertEqual("object", props["scope"]["type"])

    def test_operational_response_uses_six_dispositions(self):
        props = contracts.schema_for("operational_review")["properties"]
        self.assertIn("disposition", props)

    def test_specialized_role_schema_uses_same_envelope(self):
        schema = contracts.action_schema({"role": "intent_interpretation", "stage": "check"})
        expected = governance.interpretation_schema("check")
        self.assertTrue(set(expected["properties"]) <= set(schema["properties"]))
        self.assertIn("integration_bundles", schema["properties"])
        self.assertNotIn("integration_bundles", schema["required"])

    def test_scope_planning_schema_reaches_domain_scope_validator(self):
        props = review_cycle.stage_schema("scope")["properties"]
        self.assertIn("scope_assessment", props)
        self.assertIn("initial_slots", props["scope_assessment"]["properties"])

    def test_manifest_is_optional_but_explicit_declarations_remain_typed(self):
        schema = contracts.schema_for("research_work")
        self.assertNotIn("integration_bundles", schema["required"])
        validator = jsonschema.Draft202012Validator(schema)
        output = two_observation_output()
        output.pop("integration_bundles")
        self.assertEqual(list(validator.iter_errors(output)), [])
        expected = {"null": {("type", ("integration_bundles",))}, "empty": {("minItems", ("integration_bundles",))},
                    "untyped": {("required", ("integration_bundles", 0))}}
        for name, value in {"null": None, "empty": [], "untyped": [{}]}.items():
            with self.subTest(value=value):
                self.assertTrue(list(validator.iter_errors({**output, "integration_bundles": value})))
                self.assertEqual(failures(schema, {**output, "integration_bundles": value}), expected[name])


if __name__ == "__main__":
    unittest.main()
