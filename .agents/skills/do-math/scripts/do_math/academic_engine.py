"""Connect explicit academic requirements to ordinary reviewed research tasks."""
from copy import deepcopy

from . import academic
from .repository import new_id


class AcademicEngineMixin:
    def _solution_basis(self):
        if self.instance.get("goal_status") != "mathematically_solved": return None
        group = self.instance.get("goal_assessment_basis")
        judgments = [j for j in self.instance.get("goal_judgments", []) if j.get("basis") == group]
        if not judgments or any(not j.get("current", True) for j in judgments): return None
        ids = sorted({ref for j in judgments for ref in j.get("dependencies", []) if ref in self.instance["knowledge"]})
        records = [self.instance["knowledge"][kid] for kid in ids]
        records += [{"id": j["execution_id"], **j} for j in judgments]
        return academic.solution_basis(str(self.instance.get("goal_revision", 1)) + ":" + str(group), records)

    def _academic_status(self):
        return academic.academic_status(self.instance, self.runtime, self._solution_basis())

    def _ensure_academic_followup(self):
        basis = self._solution_basis()
        requirements = self.instance.get("academic_requirements", {})
        if basis is None or self.runtime["status"] in {"paused", "closed", "budget_exhausted"}: return
        if not requirements.get("items"):
            rejections = [r for r in self.runtime.get("external_rejections", []) if r["solution_basis"] == basis]
            if rejections and all(r.get("resolved") and r.get("resolution_evidence") for r in rejections):
                self.runtime["status"] = "completed"
                self.runtime["queue"] = []
            return
        current_hash = requirements["sha256"]
        for task in self.runtime["tasks"].values():
            if task.get("academic_requirement_id") and (task.get("solution_basis") != basis or task.get("requirements_sha256") != current_hash):
                if task["status"] == "closed":
                    continue
                if task["status"] == "completed":
                    # completed is absorbing; the old assessment only stops being current.
                    if isinstance(task.get("assessment"), dict) and task["assessment"].get("current") is not False:
                        task["assessment"].update(current=False, invalidated_reason="Academic requirements or solution basis changed; new tasks carry the current basis")
                    continue
                task["status"] = "closed"
                task["scope_disposition"] = {"kind": "superseded_requirements", "reason": "New tasks carry the current requirements and solution basis"}
                self.runtime["queue"] = [a for a in self.runtime["queue"] if a.get("target") != task["id"]]
        created = False
        for requirement in requirements["items"]:
            if any(t.get("academic_requirement_id") == requirement["id"] and t.get("solution_basis") == basis and
                   t.get("requirements_sha256") == current_hash and not (
                       t.get("status") == "completed" and t.get("assessment", {}).get("current") is False)
                   for t in self.runtime["tasks"].values()): continue
            tid = new_id("TK")
            refs = [r["id"] for r in basis["records"] if r["id"] in self.instance["knowledge"]]
            inputs = list(dict.fromkeys([*refs, *requirement["required_inputs"]]))
            self.runtime["tasks"][tid] = {"id": tid, "revision": 1, "feature_version": 2,
                "title": "Academic validation: " + requirement["id"], "question": requirement["scope"],
                "scope": requirement["scope"], "expected_result": "Evidence for the user-defined academic criteria",
                "completion_criteria": deepcopy(requirement["criteria"]), "inputs": inputs, "reuse": refs,
                "work_class": "nonformal", "status": "planned", "producer_execution": "user-requirement:" + requirement["id"],
                "results": [], "reviews": [], "dependencies": refs, "occurrence_condition": {"op": "always"},
                "academic_requirement_id": requirement["id"], "requirements_sha256": current_hash,
                "solution_basis": deepcopy(basis), "required_external_effects": deepcopy(requirement["external_effects"])}
            self._enqueue("task_contract_review", tid, reason="Independently review the concrete academic requirement contract")
            created = True
        status = self._academic_status()["status"]
        if status == "completed":
            self.runtime["status"] = "completed"
            self.runtime["queue"] = []
        elif created or self.runtime["status"] == "completed":
            self.runtime["status"] = "ready"
            self._enqueue("research_plan", reason="Complete the explicit postsolution academic requirements")

    def _academic_control(self, request):
        change = request.get("config", {}).get("change", {})
        if request.get("action") != "decision" or change.get("kind") != "academic_rejection": return False
        basis = self._solution_basis()
        if basis is None: raise ValueError("external rejection requires a current solved mathematical goal")
        if not all(isinstance(change.get(key), str) and change[key].strip() for key in ("actor", "text")):
            raise ValueError("external rejection needs its actor and preserved original text")
        entry = {"id": new_id("RJ"), "actor": change["actor"], "text": change["text"], "source_ref": request["id"],
                 "created_at": request["created_at"], "solution_basis": basis, "resolved": False}
        self.runtime.setdefault("external_rejections", []).append(entry)
        if self.runtime["status"] == "completed": self.runtime["status"] = "ready"
        self._enqueue("research_plan", reason="Examine the external rejection against the preserved solution evidence", rejection_id=entry["id"])
        return True

    def _record_academic_assessment(self, task, assessment, execution_id):
        if not task.get("academic_requirement_id"): return
        if task.get("solution_basis") != self._solution_basis() or task.get("requirements_sha256") != self.instance["academic_requirements"]["sha256"]:
            raise ValueError("academic assessment basis changed")
        decision = "satisfied" if assessment["decision"] == "completed" else "not_satisfied"
        requirement = next(item for item in self.instance["academic_requirements"]["items"]
                           if item["id"] == task["academic_requirement_id"])
        receipts_ok, receipts = academic.effect_receipts(requirement, task_id=task["id"],
            requirements_sha256=task["requirements_sha256"], solution_basis_value=task["solution_basis"], runtime=self.runtime)
        if decision == "satisfied" and not receipts_ok:
            raise ValueError("satisfied academic assessment lacks confirmed successful required external effects")
        result = academic.assess(task["academic_requirement_id"], task["solution_basis"], self.instance["academic_requirements"],
                                 decision, assessment["criteria_results"])
        result.update(execution_id=execution_id, task_id=task["id"], external_effect_receipts=receipts)
        self.runtime.setdefault("academic_assessments", []).append(result)

    def _apply_academic_resolutions(self, action, execution_id, resolutions):
        if resolutions and action["role"] != "research_plan": raise ValueError("academic resolutions require the designated research planner")
        for resolution in resolutions:
            entry = next((r for r in self.runtime.get("external_rejections", []) if r["id"] == resolution.get("id")), None)
            if entry is None or entry["solution_basis"] != self._solution_basis(): raise ValueError("rejection does not bind the current solution")
            if resolution.get("decision") not in {"resolved", "unresolved"} or not isinstance(resolution.get("evidence"), str) or not resolution["evidence"].strip():
                raise ValueError("resolution requires a decision and explicit evidence")
            entry.setdefault("assessment_history", []).append({"execution_id": execution_id, **deepcopy(resolution)})
            if resolution["decision"] == "resolved":
                entry.update(resolved=True, resolution_evidence=resolution["evidence"], resolution_execution_id=execution_id)
            else:
                entry["resolved"] = False
                entry.pop("resolution_evidence", None)
                entry.pop("resolution_execution_id", None)
