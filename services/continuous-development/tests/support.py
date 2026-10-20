import json
import shutil
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
import check
import run


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="phase-dev-한글-")
        self.base = Path(self.temp.name) / "with spaces"
        shutil.copytree(ENGINE / "examples" / "linecount", self.base)
        self.repo = self.base / "project"
        self.records = self.base / "records"
        self.check = check.Check(self.repo, self.records)

    def close(self):
        self.temp.cleanup()

    def phase_path(self, phase="001"):
        return self.records / "phases" / phase

    def spec(self, phase="001"):
        return json.loads((self.phase_path(phase) / "phase.json").read_text("utf-8"))

    def save_spec(self, value, phase="001"):
        write_json(self.phase_path(phase) / "phase.json", value)

    def new_phase(self, phase="002", kind="work"):
        directory = self.phase_path(phase)
        (directory / "logs").mkdir(parents=True)
        (directory / "tasks" / "followup" / "evidence").mkdir(parents=True)
        (directory / "tasks" / "followup" / "objective.md").write_text(
            "## 목적과 역할\nFollow up on the previous phase.\n"
            "## 완료 조건\n### A1 Verify result\nInspect the actual result.\n"
            "## 판단과 경계\nReport findings only.\n"
            "## 검증 방법\nCompare the file with the requirement.\n", encoding="utf-8"
        )
        self.save_spec({"kind": kind, "purpose": "Follow up", "tasks": [
            {"id": "followup", "inputs": [], "writes": [], "provides": [], "uses": []}
        ]}, phase)

    def report(self, task="core", phase="001"):
        directory = self.phase_path(phase) / "tasks" / task
        evidence = f"run:phases/{phase}/tasks/{task}/evidence/result.txt"
        (directory / "evidence" / "result.txt").write_text("Synthetic test fixture evidence.\n", encoding="utf-8")
        count = {"core": 2, "cli": 3, "followup": 1}[task]
        data = {
            "status": "complete", "narrative": "Fixture task completed.",
            "acceptance": [{"id": f"A{i}", "result": "pass", "detail": "Fixture criterion satisfied.", "evidence": [evidence]} for i in range(1, count + 1)],
            "changes": [],
            "seams": [] if task == "followup" else [{"id": "S1", "result": "conforms", "detail": "Fixture contract checked.", "evidence": [evidence]}],
            "findings": [],
            "checks": [{"command": "fixture check", "cwd": "repo:.", "result": "pass", "exit_code": 0, "evidence": [evidence], "detail": "Synthetic validation result."}],
        }
        self.save_report(data, task, phase)
        return data

    def save_report(self, data, task="core", phase="001"):
        write_json(self.phase_path(phase) / "tasks" / task / "report.json", data)

    def finding(self, task="core", phase="001"):
        return {"id": "F1", "kind": "issue", "detail": "A fixture concern needs follow-up.",
                "evidence": [f"run:phases/{phase}/tasks/{task}/evidence/result.txt"],
                "affects": ["run:context.md#G1"], "next_action": "Inspect in the next phase."}

    def manager(self, phase="001", next_phase="002"):
        tasks = self.spec(phase)["tasks"]
        evidence = [f"run:phases/{phase}/tasks/{task['id']}/report.json" for task in tasks]
        data = {
            "next": next_phase, "decision": "Continue or finish based on the fixture evidence.",
            "reports": [{"task": task["id"], "state": "read", "detail": "Read the complete fixture report.", "evidence": [ref]} for task, ref in zip(tasks, evidence)],
            "dispositions": [], "context_updates": [], "plan_update": "Fixture plan updated.",
            "seam_updates": [], "completion": None,
        }
        if next_phase is None:
            data["completion"] = {
                "criteria": [{"criterion": f"run:context.md#G{i}", "result": "satisfied", "evidence": evidence} for i in range(1, 5)],
                "review_reports": evidence, "remaining": [],
            }
        self.save_manager(data, phase)
        return data

    def save_manager(self, data, phase="001"):
        write_json(self.phase_path(phase) / "manager.pending.json", data)
