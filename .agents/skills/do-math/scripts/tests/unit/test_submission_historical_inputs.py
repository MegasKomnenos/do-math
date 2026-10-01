"""Large historical input stays readable by exact reference without inflating the current contract or dependencies.

``context_store.fit_context`` moves input over the byte limit into workspace
files (layer 2); the knowledge record functions keep preserved history out of
current dependencies (layer 1). Both are called directly.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.context_store import fit_context
from do_math.knowledge import assess_use, revise_knowledge
from do_math.knowledge_records import create_candidate
from do_math.planning import contract_hash
from support.role_answers import candidate


def note(title="Computation", **changes):
    return {"kind": "observation", "title": title, "statement": "The result is one.",
            "summary": "A bounded computation.", "explanation": "Exact finite computation.",
            "lean_code": "", "declaration_names": [], "dependencies": [], **changes}


class HistoricalInputTests(unittest.TestCase):
    def test_large_checkpoint_and_operational_evidence_use_exact_readable_references(self):
        """About 0.22 s, at the 0.2 s unit budget: three contexts each move 600 000 characters into workspace files."""
        checkpoint ={"current_claim": "x" * 600000, "evidence_paths": [], "attempts": [],
                      "remaining_work": [], "next_step": "Continue.", "progress_state": "working"}
        contexts = [
            ({"resume_checkpoint": {"kind": "worker_checkpoint", "value": checkpoint}}, []),
            ({"recovery_materials": {"checkpoint": checkpoint}}, []),
            ({"execution_to_review": {"id": "EX-old", "role": "research_work", "status": "ended", "details": checkpoint},
              "observation": {"execution_id": "EX-old", "reason": "checkpoint", "sample": {"checkpoint": checkpoint}}},
             ["execution_to_review", "observation"]),
        ]
        for additions, required in contexts:
            with self.subTest(fields=list(additions)), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                original = {"goal": "g", "action": {"role": "operational_review"}, **additions}
                result = fit_context(original, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", *required])
                self.assertEqual("input_overflow", result["overflow"]["kind"])
                self.assertEqual(original, result["context"])
                for key, value in additions.items():
                    ref = next(row for row in result["manifest"] if row["key"] == key)
                    self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), value)

    def test_large_repair_action_and_previous_execution_remain_readable_by_reference(self):
        """The name also says the previous execution; like the legacy test, only the action's reference is asserted."""
        action = {"id": "AC-repair", "role": "research_preparation", "repair_attempt": 1,
                  "repair": {"execution_id": "EX-old", "error": "bad extension",
                             "previous_output": {"summary": "x" * 600000, "candidates": []}}}
        context = {"goal": "g", "action": action, "previous_execution": {"id": "EX-old", "action": action}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
            self.assertEqual("input_overflow", result["overflow"]["kind"])
            current = result["context"]["action"]
            self.assertEqual(current["id"], action["id"])
            self.assertEqual(current["role"], action["role"])
            ref = next(row for row in result["manifest"] if row["key"] == "action")
            self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), action)

    def test_preserved_history_does_not_recreate_current_knowledge_dependencies(self):
        from support.entry import entry
        _entry = entry()
        for key in ("history", "use_history", "review_history", "revision_history", "assessment_history",
                    "governance_history", "previous_initial_reviews"):
            with self.subTest(key=key):
                instance, _ = create_candidate({}, {**note(), "id": "KN-A"}, source_ref="source", actor_ref="producer", clock=_entry.ports.clock)
                instance, _ = create_candidate(instance, {**note("Independent"), "id": "KN-B", key: [{"dependencies": ["KN-A"]}]},
                                               source_ref="source", actor_ref="producer", clock=_entry.ports.clock)
                before = assess_use(instance["knowledge"]["KN-B"], instance)
                changed, _ = revise_knowledge(instance, {}, "KN-A", {"statement": "corrected"}, reason="correction",
                                              actor_ref="user", clock=_entry.ports.clock)
                self.assertFalse(changed["knowledge"]["KN-B"].get("use_suspended", False))
                self.assertEqual(before, assess_use(changed["knowledge"]["KN-B"], changed))

    def test_large_task_history_is_readable_without_inflating_the_current_contract(self):
        task = {**candidate("Current contract"), "id": "TK-A", "revision": 2, "results": [{"report": "x" * 600000}],
                "revision_history": [{"question": "old", "results": [{"report": "x" * 600000}]}]}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"goal": "g", "action": {"role": "task_contract_review"}, "task": task}
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", "task"])
            self.assertEqual("input_overflow", result["overflow"]["kind"])
            current = result["context"]["task"]
            self.assertEqual(current["question"], task["question"])
            self.assertEqual(current["completion_obligations"], task["completion_obligations"])
            self.assertEqual(contract_hash(current), contract_hash(task))
            ref = next(row for row in result["manifest"] if row["key"] == "task")
            self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), task)


if __name__ == "__main__":
    unittest.main()
