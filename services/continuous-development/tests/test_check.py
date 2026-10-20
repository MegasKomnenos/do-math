import copy
import json
import os
import subprocess
import sys
import unittest

from support import ENGINE, Fixture, check, write_json


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def test_initial_example_and_cli(self):
        self.f.check.phase("001")
        result = subprocess.run([sys.executable, str(ENGINE / "check.py"), "phase", str(self.f.repo), str(self.f.records), "001"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"PASS phase 001", result.stdout)

    def test_phase_rejects_bad_assignments(self):
        original = self.f.spec()
        cases = {
            "empty tasks": lambda s: s.update(tasks=[]),
            "duplicate task": lambda s: s["tasks"].append(copy.deepcopy(s["tasks"][0])),
            "unknown seam": lambda s: s["tasks"][0].update(provides=["S99"]),
            "duplicate provider": lambda s: s["tasks"][1].update(provides=["S1"]),
            "write overlap": lambda s: s["tasks"][1].update(writes=["src/linecount/"]),
            "review writes": lambda s: s.update(kind="review"),
            "unknown key": lambda s: s.update(purpos="typo"),
            "wrong task type": lambda s: s.update(tasks="core"),
            "bad task ID": lambda s: s["tasks"][0].update(id="../core"),
            "missing input": lambda s: s["tasks"][0].update(inputs=["repo:missing.txt"]),
            "bad anchor": lambda s: s["tasks"][0].update(inputs=["run:context.md#G99"]),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                spec = copy.deepcopy(original)
                mutate(spec)
                self.f.save_spec(spec)
                with self.assertRaises(check.Invalid):
                    self.f.check.phase("001")
        self.f.save_spec(original)

    def test_optional_model_and_effort_settings(self):
        spec = self.f.spec()
        spec["tasks"][0].update(model="a-model", effort="high")
        self.f.save_spec(spec)
        settings = self.f.records / "settings.json"
        write_json(settings, {"manager": {"model": "another-model", "effort": "medium"}})
        self.f.check.phase("001")
        for bad in ({"manager": {"model": ""}}, {"manager": {"effort": 1}}, {"manager": {"reasoning": "high"}}, {"manager": []}):
            with self.subTest(settings=bad):
                write_json(settings, bad)
                with self.assertRaises(check.Invalid):
                    self.f.check.phase("001")
        write_json(settings, {"manager": {}})
        spec["tasks"][0]["effort"] = None
        self.f.save_spec(spec)
        with self.assertRaises(check.Invalid):
            self.f.check.phase("001")

    def test_write_scope_paths(self):
        spec = self.f.spec()
        for value in ("../outside.py", "/absolute.py", "C:/absolute.py", "C:relative.py", "src/../escape.py", "src\\file.py", "./file.py", "src//file.py", "src/*.py"):
            with self.subTest(path=value):
                spec["tasks"][0]["writes"] = [value]
                self.f.save_spec(spec)
                with self.assertRaises(check.Invalid):
                    self.f.check.phase("001")

    def test_records_cannot_contain_project(self):
        with self.assertRaisesRegex(check.Invalid, "must not contain"):
            check.Check(self.f.repo, self.f.base)

    def test_symlink_aliases_and_escape(self):
        try:
            (self.f.repo / "alias").symlink_to(self.f.repo / "src", target_is_directory=True)
            (self.f.repo / "outside").symlink_to(self.f.records, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        spec = self.f.spec()
        spec["tasks"][1]["writes"] = ["alias/linecount/core.py"]
        self.f.save_spec(spec)
        with self.assertRaisesRegex(check.Invalid, "overlaps"):
            self.f.check.phase("001")
        spec["tasks"][1]["writes"] = ["outside/context.md"]
        self.f.save_spec(spec)
        with self.assertRaisesRegex(check.Invalid, "outside its root"):
            self.f.check.phase("001")

    @unittest.skipUnless(os.name == "nt", "Windows path comparison")
    def test_windows_case_aliases_overlap(self):
        spec = self.f.spec()
        spec["tasks"][1]["writes"] = ["SRC/LINECOUNT/CORE.PY"]
        self.f.save_spec(spec)
        with self.assertRaisesRegex(check.Invalid, "overlaps"):
            self.f.check.phase("001")

    def test_fenced_headings_do_not_create_criteria(self):
        path = self.f.phase_path() / "tasks/core/objective.md"
        content = path.read_text("utf-8")
        path.write_text(content + "\n```markdown\n### A999 Example only\nNot a criterion\n```\n", encoding="utf-8")
        self.f.report()
        self.f.check.report("001", "core")

    def test_code_block_is_content_even_though_its_headings_are_not_ids(self):
        path = self.f.phase_path() / "tasks/core/objective.md"
        path.write_text(
            '## 목적과 역할\nImplement the callable.\n'
            '## 완료 조건\n### A1 Output shape\n```json\n{"a": 1}\n```\n'
            '### A2 Contract code\n```python\n# examples may contain headings\npass\n```\n'
            '## 판단과 경계\nUse the public interface.\n'
            '## 검증 방법\nRun the assigned checks.\n', encoding='utf-8'
        )
        self.f.check.phase("001")

    def test_empty_or_duplicate_objective_criteria_are_invalid(self):
        path = self.f.phase_path() / "tasks/core/objective.md"
        original = path.read_text("utf-8")
        for bad in (original.replace("### A2 자체 검증", "### A1 자체 검증"), original.replace("## 판단과 경계", "## Wrong heading"), original.replace("### A1 S1 구현", "### A1 S1 구현\n### A3 Empty previous criterion")):
            path.write_text(bad, encoding="utf-8")
            with self.assertRaises(check.Invalid):
                self.f.check.phase("001")

    def test_report_status_and_evidence_rules(self):
        original = self.f.report()
        cases = {
            "missing A": lambda d: d["acceptance"].pop(),
            "duplicate A": lambda d: d["acceptance"].append(copy.deepcopy(d["acceptance"][0])),
            "no pass evidence": lambda d: d["acceptance"][0].update(evidence=[]),
            "missing evidence file": lambda d: d["acceptance"][0].update(evidence=["run:missing.txt"]),
            "complete but failed": lambda d: d["acceptance"][0].update(result="fail"),
            "partial but all passed": lambda d: d.update(status="partial"),
            "unknown S": lambda d: d["seams"][0].update(id="S2"),
            "wrong seam result": lambda d: d["seams"][0].update(result="pass"),
            "outside writes": lambda d: d["changes"].append({"path": "src/linecount/__main__.py", "detail": "Not owned."}),
            "boolean exit code": lambda d: d["checks"][0].update(exit_code=True),
            "executed no exit code": lambda d: d["checks"][0].update(exit_code=None),
            "not run has exit code": lambda d: d["checks"][0].update(result="not_run"),
            "checks evidence empty": lambda d: d["checks"][0].update(evidence=[]),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                data = copy.deepcopy(original)
                mutate(data)
                self.f.save_report(data)
                with self.assertRaises(check.Invalid):
                    self.f.check.report("001", "core")

    def test_partial_and_blocked_are_valid_reports(self):
        for status in ("partial", "blocked"):
            data = self.f.report()
            data["status"] = status
            data["acceptance"][0].update(result="not_run", evidence=[], detail="Dependency unavailable.")
            data["checks"][0].update(result="not_run", exit_code=None, evidence=[], detail="Dependency unavailable.")
            self.f.save_report(data)
            self.f.check.report("001", "core")

    def test_report_preserves_detailed_free_form_prose(self):
        data = self.f.report()
        narrative = ('구현의 배경과 판단 근거를 설명한다. 인용부호 "와" 줄바꿈을 보존한다.\n\n'
                     '### 관찰과 검증\n\n예외 조건과 실제 관찰을 연결한다.\n\n'
                     '```python\nvalue = {"counts": [1, 2]}\n```\n\n') * 100
        data["narrative"] = narrative
        data["acceptance"][0]["detail"] = narrative
        self.f.save_report(data)
        actual = self.f.check.report("001", "core")
        self.assertEqual(actual["narrative"], narrative)
        self.assertEqual(actual["acceptance"][0]["detail"], narrative)

    def test_expected_nonzero_command_can_pass(self):
        data = self.f.report()
        data["checks"][0].update(exit_code=2, detail="Expected invalid-input exit code 2 observed.")
        self.f.save_report(data)
        self.f.check.report("001", "core")

    def test_bom_is_accepted_but_duplicate_keys_and_nan_are_not(self):
        self.f.report()
        path = self.f.phase_path() / "tasks/core/report.json"
        original = path.read_text("utf-8")
        path.write_text(original, encoding="utf-8-sig")
        self.f.check.report("001", "core")
        for bad in ('{"status":"complete","status":"blocked"}', '{"exit_code":NaN}'):
            path.write_text(bad, encoding="utf-8")
            with self.assertRaises(check.Invalid):
                self.f.check.report("001", "core")

    def test_continuation_and_same_seam_edit(self):
        self.f.report("core")
        self.f.report("cli")
        self.f.new_phase()
        self.f.manager()
        path = self.f.records / "seams.md"
        path.write_text(path.read_text("utf-8").replace("구현 예정", "구현 존재"), encoding="utf-8")
        self.f.check.handoff("001")

    def test_handoff_requires_every_finding_to_have_a_disposition(self):
        report = self.f.report("core")
        report["findings"] = [self.f.finding()]
        self.f.save_report(report)
        self.f.report("cli")
        self.f.new_phase()
        manager = self.f.manager()
        with self.assertRaisesRegex(check.Invalid, "dispositions"):
            self.f.check.handoff("001")
        manager["dispositions"] = [{"item": "001/core/F1", "action": "carry", "destination": ["run:phases/002/tasks/followup/objective.md"], "reason": "Follow-up assigned.", "evidence": ["run:phases/001/tasks/core/report.json"]}]
        self.f.save_manager(manager)
        self.f.check.handoff("001")
        manager["dispositions"][0]["destination"] = ["repo:pyproject.toml"]
        self.f.save_manager(manager)
        with self.assertRaisesRegex(check.Invalid, "carry destination"):
            self.f.check.handoff("001")

    def test_missing_and_invalid_reports_can_be_recovered(self):
        self.f.report("cli")
        self.f.new_phase()
        manager = self.f.manager()
        manager["reports"][0].update(state="missing", detail="Recover in followup.", evidence=["run:phases/002/tasks/followup/objective.md"])
        self.f.save_manager(manager)
        self.f.check.handoff("001")
        report_path = self.f.phase_path() / "tasks/core/report.json"
        report_path.write_text('{"status":', encoding="utf-8")
        with self.assertRaisesRegex(check.Invalid, "report exists"):
            self.f.check.handoff("001")
        manager["reports"][0]["state"] = "invalid"
        self.f.save_manager(manager)
        self.f.check.handoff("001")
        self.f.report("core")
        with self.assertRaisesRegex(check.Invalid, "report is valid"):
            self.f.check.handoff("001")

    def test_missing_cannot_be_claimed_read(self):
        self.f.report("cli")
        self.f.new_phase()
        self.f.manager()
        with self.assertRaises(check.Invalid):
            self.f.check.handoff("001")

    def test_next_phase_cannot_be_reused(self):
        self.f.report("core")
        self.f.report("cli")
        self.f.new_phase()
        manager = self.f.manager()
        manager["next"] = "001"
        self.f.save_manager(manager)
        with self.assertRaisesRegex(check.Invalid, "new phase"):
            self.f.check.handoff("001")
        manager["next"] = "002"
        self.f.save_manager(manager)
        self.f.report("followup", "002")
        with self.assertRaisesRegex(check.Invalid, "already has reports"):
            self.f.check.handoff("001")

    def test_context_update_must_point_to_existing_item(self):
        self.f.report("core")
        self.f.report("cli")
        self.f.new_phase()
        manager = self.f.manager()
        manager["context_updates"] = [{"item": "C99", "action": "amend", "destination": ["run:context.md#C1"], "reason": "Incorrect item.", "evidence": ["run:phases/001/tasks/core/report.json"]}]
        self.f.save_manager(manager)
        with self.assertRaisesRegex(check.Invalid, "updated C item missing"):
            self.f.check.handoff("001")

    def test_work_cannot_declare_completion(self):
        self.f.report("core")
        self.f.report("cli")
        self.f.manager(next_phase=None)
        with self.assertRaisesRegex(check.Invalid, "only a review"):
            self.f.check.handoff("001")

    def test_review_completion_requires_all_goals_and_complete_reviews(self):
        self.f.new_phase(kind="review")
        report = self.f.report("followup", "002")
        original = self.f.manager("002", None)
        self.f.check.handoff("002")
        for field in ("criteria", "review_reports"):
            with self.subTest(field=field):
                manager = copy.deepcopy(original)
                manager["completion"][field].pop()
                self.f.save_manager(manager, "002")
                with self.assertRaises(check.Invalid):
                    self.f.check.handoff("002")
        self.f.save_manager(original, "002")
        report["status"] = "blocked"
        report["acceptance"][0].update(result="not_run", evidence=[])
        self.f.save_report(report, "followup", "002")
        with self.assertRaisesRegex(check.Invalid, "all review tasks"):
            self.f.check.handoff("002")

    def test_review_findings_can_start_a_work_phase(self):
        self.f.new_phase("002", "review")
        report = self.f.report("followup", "002")
        report["findings"] = [self.f.finding("followup", "002")]
        self.f.save_report(report, "followup", "002")
        self.f.new_phase("003", "work")
        manager = self.f.manager("002", "003")
        manager["dispositions"] = [{"item": "002/followup/F1", "action": "carry", "destination": ["run:phases/003/tasks/followup/objective.md"], "reason": "Repair before another review.", "evidence": ["run:phases/002/tasks/followup/report.json"]}]
        self.f.save_manager(manager, "002")
        self.f.check.handoff("002")

    def test_invalid_json_cli_returns_one_without_traceback(self):
        (self.f.phase_path() / "phase.json").write_text("{", encoding="utf-8")
        result = subprocess.run([sys.executable, str(ENGINE / "check.py"), "phase", str(self.f.repo), str(self.f.records), "001"], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertIn(b"JSON line", result.stderr)


if __name__ == "__main__":
    unittest.main()
