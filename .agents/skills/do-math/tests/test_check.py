"""Small handoff examples; no model, Lean, or runner is invoked."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check.py"
spec = importlib.util.spec_from_file_location("do_math_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8", newline="")


def envelope(category, **fields):
    return {"category": category, "references": [], "supersedes": [], **fields}


def judgment(verdict):
    return {"verdict": verdict, "reason": "Illustrative judgment, not a mathematical check."}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.instance = Path(self.temp.name)
        (self.instance / "knowledge").mkdir()
        (self.instance / "goal.md").write_text("Example goal.", encoding="utf-8")

    def session(self, name, output, **task_fields):
        session = self.instance / "sessions" / name
        task = {"instructions": "Example instruction.", "references": [], **task_fields}
        write_json(session / "input.json", {
            "instance": str(self.instance), "category": output["category"],
            "context": {"common": [str(self.instance / "goal.md")], "category": str(SCRIPT.parent / "protocol.md")},
            "task": task,
        })
        write_json(session / "output" / "output.json", output)
        return session

    def research(self):
        output = envelope("research", results=[{
            "id": "r1", "exposition": "exposition.md", "verification": "No mathematical check was performed.",
            "lean": {"sources": ["Proof.lean"], "version": "Illustrative version string"},
        }], failed_attempts=[{"description": "An unfinished approach.", "verification": "Only a sketch was made."}],
            open_questions=["Can this approach be completed?"])
        session = self.session("author", output, supersedes=[])
        (session / "output" / "exposition.md").write_text("An unsupported example claim.", encoding="utf-8")
        # Intentionally invalid Lean: the official checker must not compile it.
        (session / "output" / "Proof.lean").write_text("not a Lean program", encoding="utf-8")
        return session, output

    def publish(self, session, record):
        self.assertEqual(checker.check_session(session), [])
        shutil.copytree(session / "output", self.instance / "knowledge" / record)

    def test_public_handoff_and_cli(self):
        request = {"instructions": "Investigate the goal.", "references": [], "supersedes": [],
                   "model": "codex/example", "effort": "high", "selection_reason": "Example override."}
        plan = self.session("plan", envelope("plan", reason="Start research.", research=[request],
                            reviews=[], goal_review=None, wait=None), events=[{"kind": "start"}])
        self.publish(plan, "p1")
        author, _ = self.research()
        self.publish(author, "k1")
        # Review must remain usable after the author's working files disappear.
        shutil.rmtree(author)
        target = {"kind": "research", "record": "k1"}
        review_output = envelope("review", target=target, results=[{
            "result": "r1", "assessment": judgment("undetermined"),
            "lean": judgment("not_checked"), "alignment": judgment("not_checked"),
        }], summary="Review is incomplete.")
        review = self.session("review", review_output, target=target)
        self.publish(review, "k2")
        followup_output = envelope("plan", reason="Need the user's scope clarification.", research=[],
            reviews=[{"target": target, "instructions": "Check independently.", "references": []}],
            goal_review={"instructions": "Check the goal.", "references": []},
            wait={"needed": "Clarify scope.", "reason": "The goal has two readings."})
        followup_output["references"] = [{"record": "k1", "file": "Proof.lean", "result": "r1"}]
        followup = self.session("followup", followup_output, events=[
            {"kind": "review_finished", "record": "k2"},
            {"kind": "session_failed", "session": "s3", "reason": "No output."},
            {"kind": "user_input", "text": "New scope information."},
        ])
        self.publish(followup, "p2")
        goal_output = envelope("review", target={"kind": "goal"}, goal=judgment("achieved"))
        goal_output["references"] = [{"record": "k1"}, {"record": "k2"}]
        goal = self.session("goal", goal_output, target={"kind": "goal"})
        result = subprocess.run([sys.executable, str(SCRIPT), str(goal)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True, "errors": []})

    def test_missing_structure_and_review_coverage(self):
        author, original = self.research()
        missing = copy.deepcopy(original)
        del missing["results"][0]["lean"]["version"]
        write_json(author / "output" / "output.json", missing)
        self.assertIn("results[0].lean.version", checker.check_session(author)[0])
        result = subprocess.run([sys.executable, str(SCRIPT), str(author)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        write_json(author / "output" / "output.json", original)
        self.publish(author, "k1")
        target = {"kind": "research", "record": "k1"}
        review = self.session("review", envelope("review", target=target, results=[], summary="Forgot r1."), target=target)
        self.assertIn("each target result exactly once", checker.check_session(review)[0])

    def test_unreadable_json_returns_diagnostics(self):
        author, _ = self.research()
        path = author / "output" / "output.json"
        depth = sys.getrecursionlimit() + 100
        for content in ("[]", "[" * depth + "0" + "]" * depth):
            with self.subTest(deep=len(content) > 2):
                path.write_text(content, encoding="utf-8")
                errors = checker.check_session(author)
                self.assertEqual(len(errors), 1)
                self.assertEqual(errors[0].count(str(path)), 1)
                result = subprocess.run([sys.executable, str(SCRIPT), str(author)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertFalse(json.loads(result.stdout)["ok"])

    def test_broken_references_and_public_files(self):
        author, original = self.research()
        self.publish(author, "k1")
        cases = [
            ("references", [{"record": "absent"}], "record does not exist"),
            ("references", [{"record": "k1", "file": "absent.md"}], "file does not exist"),
            ("references", [{"record": "k1", "file": "bad\0name.md"}], "expected a relative"),
            ("references", [{"record": "k1", "result": "absent"}], "result does not exist"),
            ("supersedes", ["absent"], "record does not exist"),
        ]
        for key, value, message in cases:
            with self.subTest(key=key, value=value):
                output = copy.deepcopy(original)
                output[key] = value
                write_json(author / "output" / "output.json", output)
                self.assertIn(message, checker.check_session(author)[0])
        write_json(author / "output" / "output.json", original)
        (author / "output" / "exposition.md").unlink()
        self.assertIn("results[0].exposition", checker.check_session(author)[0])


if __name__ == "__main__":
    unittest.main()
