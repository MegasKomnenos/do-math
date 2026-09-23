from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import questions
from do_math.question_engine import QuestionEngineMixin


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.instance = {"id": "I", "knowledge": {}}
        self.runtime = {"tasks": {"A": {"id": "A"}, "B": {"id": "B"}}, "question_links": []}
        self.a = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True)
        self.b = questions.link(self.runtime, execution_id="E2", field="output/questions/0", owner="user", targets=["B"], blocks=True)

    def test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks(self):
        self.assertEqual(len(questions.user_waits({"role": "research_work", "target": "A"}, self.instance, self.runtime)), 1)
        self.assertEqual(questions.user_waits({"role": "research_work", "target": "C"}, self.instance, self.runtime), [])
        self.assertEqual(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime), [])
        questions.link(self.runtime, execution_id="E3", field="output/questions/0", owner="user", targets=["I"], blocks=True)
        self.assertTrue(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime))
        self.assertFalse(questions.user_waits({"role": "intent_interpretation"}, self.instance, self.runtime))

    def test_resolving_one_user_question_preserves_the_other(self):
        questions.resolve_user(self.runtime, [self.a["id"]], resolution_ref="D", affected_ids=["A"])
        self.assertEqual(self.a["status"], "resolved")
        self.assertEqual(self.b["status"], "open")
        with self.assertRaises(ValueError):
            questions.resolve_user(self.runtime, [self.b["id"]], resolution_ref="unrelated", affected_ids=["A"])

    def test_an_ai_extension_cannot_resolve_a_user_question(self):
        context = {"instance_id": "I", "action": {"role": "research_plan"}, "question_links": self.runtime["question_links"]}
        extensions = {"question_resolutions": [{"question_id": self.a["id"], "disposition": "resolved", "evidence_refs": ["E"], "reason": "guess"}]}
        self.assertTrue(questions.validate_extensions({}, extensions, context))

    def test_source_identity_not_equal_text_controls_deduplication(self):
        same = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True)
        self.assertEqual(same["id"], self.a["id"])
        self.assertNotEqual(self.a["id"], self.b["id"])
        self.assertNotIn("text", self.a)

    def test_retry_bypasses_only_the_question_for_its_held_overflow(self):
        other = questions.link(self.runtime, execution_id="E3", field="output/questions/0",
                               owner="user", targets=["A"], blocks=True)
        action = {"id": "AC-1", "role": "research_work", "target": "A",
                  "input_overflow_retry": {"question_id": self.a["id"], "state": "pending"}}
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual([row["question_id"] for row in waits], [other["id"]])

        action["input_overflow_retry"]["state"] = "resolved"
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual({row["question_id"] for row in waits}, {self.a["id"], other["id"]})

    def test_overflow_question_text_follows_its_artifact_pointer(self):
        class Store:
            def read_many(inner, refs, head):
                return {refs[0]: b'{"resolution_question":{"question":"Choose an authorized larger profile."}}'}
        reader = QuestionEngineMixin()
        reader.store, reader.head, reader.instance = Store(), "H", {"decisions": {}}
        reader.runtime = {"question_links": [{
            "id": "QU-overflow", "origin_execution_id": "EX-overflow",
            "origin_field": "resolution_question/question",
            "source_ref": "runtime/artifacts/BA-overflow/input-overflow.json",
            "owner": "user", "target_ids": ["AC-held"], "unresolved_target_ids": ["AC-held"],
            "blocks": True, "status": "open", "resolution_ref": None}]}
        row = reader._question_view()[0]
        self.assertEqual(row["text"], "Choose an authorized larger profile.")
        self.assertNotIn("source_status", row)


if __name__ == "__main__":
    unittest.main()
