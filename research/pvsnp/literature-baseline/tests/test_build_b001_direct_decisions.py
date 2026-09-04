import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "build_b001_direct_decisions.py"
SPEC = importlib.util.spec_from_file_location("build_b001_direct_decisions", MODULE_PATH)
decisions = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(decisions)


class DecisionParsingTests(unittest.TestCase):
    def test_parses_reports_and_binds_every_queue_cluster(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue_path = root / "queue.jsonl"
            report_a = root / "A.md"
            report_b = root / "B.md"
            queue_rows = [
                {
                    "cluster_id": "B001-DIRECT-" + "a" * 20,
                    "member_count": 2,
                    "members": [{"candidate_id": "one"}, {"candidate_id": "two"}],
                    "signal": {"doi": "10.1/a"},
                },
                {
                    "cluster_id": "B001-DIRECT-" + "b" * 20,
                    "member_count": 1,
                    "members": [{"candidate_id": "three"}],
                    "signal": {"title": "p vs np"},
                },
            ]
            queue_path.write_text(
                "".join(json.dumps(row) + "\n" for row in queue_rows),
                encoding="utf-8",
            )
            report_a.write_text(
                "| cluster ID | members | 처분 | 근거 |\n"
                "|---|---:|---|---|\n"
                f"| {'a' * 20} | 2 | standard_pnp_research | evidence A |\n",
                encoding="utf-8",
            )
            report_b.write_text(
                "| # | cluster ID · members | 처분 | 근거 |\n"
                "|---:|---|---|---|\n"
                "| 37 | `bbbbbb…`; 1: *title* | `education_or_commentary` | evidence B |\n"
                "| 순번 | cluster_id |\n"
                "|---:|---|\n"
                f"| 37 | `B001-DIRECT-{'b' * 20}` |\n",
                encoding="utf-8",
            )

            rows = decisions.build_decisions(queue_path, [report_a, report_b])

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["cluster_id"], "B001-DIRECT-" + "a" * 20)
        self.assertEqual(rows[0]["member_count"], 2)
        self.assertEqual(rows[0]["disposition"], "standard_pnp_research")
        self.assertEqual(rows[0]["member_ids"], ["one", "two"])

    def test_rejects_missing_or_duplicate_cluster_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue_path = root / "queue.jsonl"
            report = root / "report.md"
            queue_path.write_text(
                json.dumps(
                    {
                        "cluster_id": "B001-DIRECT-" + "a" * 20,
                        "member_count": 1,
                        "members": [{"candidate_id": "one"}],
                        "signal": {},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            report.write_text("# no table rows\n", encoding="utf-8")

            with self.assertRaises(decisions.DecisionError):
                decisions.build_decisions(queue_path, [report])


if __name__ == "__main__":
    unittest.main()
