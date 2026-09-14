from __future__ import annotations

import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.contracts import ROLES, reading_map, prompt_documents, render_prompt, schema_for


class ContractTests(unittest.TestCase):
    def test_every_role_has_closed_schema(self):
        for role in ROLES:
            schema = schema_for(role)
            self.assertFalse(schema["additionalProperties"])
            self.assertTrue({"summary", "used_sources", "questions"} <= set(schema["required"]))
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_invalid_decisions_fail(self):
        for role, field in (("task_contract_review", "decision"), ("identity_review", "decision"),
                            ("goal_audit", "decision"), ("operational_review", "decision")):
            value = {key: ([] if shape.get("type") == "array" else False if shape.get("type") == "boolean" else "x")
                     for key, shape in schema_for(role)["properties"].items()}
            value[field] = "invalid"
            self.assertFalse(jsonschema.Draft202012Validator(schema_for(role)).is_valid(value), role)

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
        self.assertIn('"do-math-cli/1"', prompt)
        self.assertIn("Do not emit Markdown", prompt)

    def test_declared_role_documents_are_complete(self):
        self.assertEqual(set(reading_map()), set(ROLES))

    def test_plan_assessment_fields_are_required(self):
        schema = schema_for("research_plan")
        self.assertTrue({"selections", "deferred", "preparation_requests", "goal_audit", "task_assessments"} <= set(schema["required"]))
        assessment = schema["properties"]["task_assessments"]["items"]
        self.assertEqual(set(assessment["required"]), {"task_id", "decision", "reason", "criteria_results"})


if __name__ == "__main__":
    unittest.main()
