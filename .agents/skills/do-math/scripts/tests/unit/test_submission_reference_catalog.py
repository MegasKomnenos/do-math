"""Reference hints are projections of visibility, never additional authority."""
from pathlib import Path
import tempfile
import unittest
from support.provider_probes import ObservedCalls

from do_math.submission import reference_catalog, reported_references, validate_reference


class CatalogTests(unittest.TestCase):
    def test_large_manifest_is_indexed_once_without_authorizing_the_projection(self):
        from do_math import submission
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [f"environment/module-{i}.olean" for i in range(2000)]
            context = {"manifest": {"files": [{"path": p} for p in paths]},
                       "reference_catalog": [{"path": "invented"}],
                       "proposal": {"valid": {}},
                       "other": [{"ref": "proposal:missing"}]}
            with ObservedCalls(locators=submission.supplied_locators) as observed:
                values = {row['value'] for row in reference_catalog(context, root)}
                self.assertEqual(observed.count('locators'), 1)
            self.assertTrue(set(paths).issubset(values))
            self.assertNotIn('invented', values)
            self.assertNotIn('proposal:missing', values)
            context['manifest']['files'].pop()
            with self.assertRaisesRegex(ValueError, "reference must identify supplied input, a record of the input snapshot or a preserved workspace file"):
                validate_reference(paths[-1], context, root)

    def test_current_aliases_and_historical_bytes_remain_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "input/knowledge/K.json"
            path.parent.mkdir(parents=True)
            path.write_text('{}')
            context = {"action": {"role": "research_plan"},
                "knowledge_catalog": [{"id": "K", "path": "input/knowledge/K.json"}],
                "tasks": [{"id": "T"}], "sources": [{"id": "S", "name": "paper",
                    "path": "research/source/paper", "local_path": "input/sources/paper"}],
                "previous_execution": {"id": "E", "result_source": {"artifact_ref": "runtime/artifacts/old/result.json"}}}
            rows = reference_catalog(context, root)
            for row in rows:
                validate_reference(row["value"], context, root)
            values = {row["value"]: row for row in rows}
            self.assertEqual(values["input/knowledge/K.json"]["canonical_ref"], "K")
            self.assertEqual(values["runtime/artifacts/old/result.json"]["kind"], "historical_artifact")
            refs = reported_references({"used_sources": ["workspace:input/knowledge/K.json", "source:paper",
                "S", "runtime/artifacts/old/result.json"]}, {}, context)
            self.assertEqual(refs, ["K", "paper", "runtime/artifacts/old/result.json"])
            context["reference_catalog"] = [{"value": "unprovided", "path": "unprovided"}]
            with self.assertRaisesRegex(ValueError, "reference must identify supplied input, a record of the input snapshot or a preserved workspace file"):
                validate_reference("unprovided", context, root)

    def test_fixed_question_catalog_only_exposes_its_source_set(self):
        with tempfile.TemporaryDirectory() as directory:
            context = {"action": {"role": "supplemental_research", "review_cycle_id": "R"},
                "knowledge_catalog": [{"id": "allowed"}, {"id": "other"}],
                "review_research": {"sources": [{"ref": "allowed"}]}}
            self.assertEqual([r["value"] for r in reference_catalog(context, Path(directory))], ["allowed"])

    def test_workspace_root_reference_returns_a_submission_issue(self):
        from support.entry import entry
        _entry = entry()
        from do_math import contracts, submission
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = {'action': {'id': 'AC-check', 'role': 'maintenance'},
                       'execution_id': 'EX-check', 'snapshot': 'fixed'}
            output = {'summary': 'Inspect', 'used_sources': [], 'questions': [],
                      'report': 'Inspected the supplied material', 'remaining_work': []}
            schema = contracts.schema_for('maintenance')
            for reference in ('.', './', 'workspace:.', 'workspace:./'):
                with self.subTest(reference=reference):
                    issues = submission.payload_issues(
                        {**output, 'used_sources': [reference]}, schema, context, {}, root, clock=_entry.ports.clock)
                    self.assertEqual(len(issues), 1, issues)
                    self.assertEqual(issues[0]['path'], 'output/used_sources/0')
                    self.assertIn('unsafe relative path', issues[0]['message'])
            (root / 'evidence.txt').write_bytes(b'preserved evidence')
            self.assertEqual(submission.payload_issues(
                {**output, 'used_sources': ['workspace:evidence.txt']},
                schema, context, {}, root, clock=_entry.ports.clock), [])


if __name__ == "__main__":
    unittest.main()
