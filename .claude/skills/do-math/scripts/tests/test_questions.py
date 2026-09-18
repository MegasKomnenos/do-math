from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import questions


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.instance = {"id": "I", "knowledge": {}}
        self.runtime = {"tasks": {"A": {"id": "A"}, "B": {"id": "B"}}, "question_links": []}
        self.a = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"])
        self.b = questions.link(self.runtime, execution_id="E2", field="output/questions/0", owner="user", targets=["B"])

    def test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks(self):
        self.assertEqual(len(questions.user_waits({"role": "research_work", "target": "A"}, self.instance, self.runtime)), 1)
        self.assertEqual(questions.user_waits({"role": "research_work", "target": "C"}, self.instance, self.runtime), [])
        self.assertEqual(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime), [])
        questions.link(self.runtime, execution_id="E3", field="output/questions/0", owner="user", targets=["I"])
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
        same = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"])
        self.assertEqual(same["id"], self.a["id"])
        self.assertNotEqual(self.a["id"], self.b["id"])
        self.assertNotIn("text", self.a)


if __name__ == "__main__":
    unittest.main()
