import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "build_b001_axis_decisions.py"
SPEC = importlib.util.spec_from_file_location("build_b001_axis_decisions", MODULE_PATH)
axis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(axis)


class AxisDecisionTests(unittest.TestCase):
    def test_parses_a_b_and_c_table_shapes_and_binds_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / "queue.jsonl"
            ids = [character * 20 for character in "abc"]
            queue.write_text(
                "".join(
                    json.dumps(
                        {
                            "cluster_id": "B001-AXIS-" + cluster_id,
                            "member_count": index,
                            "members": [
                                {"candidate_id": f"m{index}-{number}"}
                                for number in range(index)
                            ],
                            "signal": {"title": cluster_id},
                        }
                    )
                    + "\n"
                    for index, cluster_id in enumerate(ids, start=1)
                ),
                encoding="utf-8",
            )
            report_a = root / "A.md"
            report_a.write_text(
                f"| {ids[0]} | 1 | raw context A | `standard_subaxis_research` |\n",
                encoding="utf-8",
            )
            report_b = root / "B.md"
            report_b.write_text(
                f"| 53 | `B001-AXIS-{ids[1]}`; 2: *title* | context B | `core_barrier_or_method_candidate` |\n",
                encoding="utf-8",
            )
            report_c = root / "C.md"
            report_c.write_text(
                f"| B001-AXIS-{ids[2]} | 3 | title | `conditional_problem_result` | context C |\n",
                encoding="utf-8",
            )

            rows = axis.build_decisions(queue, [report_a, report_b, report_c])

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["disposition"], "standard_subaxis_research")
        self.assertEqual(rows[1]["member_count"], 2)
        self.assertEqual(rows[2]["member_ids"], ["m3-0", "m3-1", "m3-2"])

    def test_rejects_incomplete_report_union(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / "queue.jsonl"
            report = root / "report.md"
            queue.write_text(
                json.dumps(
                    {
                        "cluster_id": "B001-AXIS-" + "a" * 20,
                        "member_count": 1,
                        "members": [{"candidate_id": "one"}],
                        "signal": {},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            report.write_text("# no decisions\n", encoding="utf-8")

            with self.assertRaises(axis.DecisionError):
                axis.build_decisions(queue, [report])


if __name__ == "__main__":
    unittest.main()
