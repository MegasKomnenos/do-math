"""Connect explicit academic requirements to ordinary reviewed research tasks."""
from copy import deepcopy

from . import academic, governance
from .file_io import now
from .repository import exact_content_hash, new_id


class AcademicEngineMixin:
    def _settle_goal_completion(self):
        """Close dispatch obligations with evidence, without claiming task success."""
        from . import activities
        pending = {action['id']: {'action': deepcopy(action)} for action in self.runtime['queue']}
        for waiting in self.runtime.get('waiting_actions', {}).values():
            action = waiting['action']
            pending.setdefault(action['id'], {'action': deepcopy(action)})['waiting'] = deepcopy(waiting)
        if not pending:
            return
        self.runtime['queue'] = []
        self.runtime['waiting_actions'] = {}
        owners = set()
        for row in pending.values():
            action = row['action']
            event = {'kind': 'goal_completion_superseded_action', **row,
                     'reason': 'goal_completed_before_dispatch', 'next_owner': 'user'}
            self.runtime['history'].append(event)
            reference = 'runtime/history/' + str(len(self.runtime['history']) - 1)
            if action['role'] == 'intent_interpretation':
                self.runtime['questions'].append(
                    'Goal completed before input ' + str(action.get('target'))
                    + ' was interpreted; the unprocessed request is preserved at ' + reference)
            aid = action.get('owner_activity_id')
            activity = self.runtime.get('activities', {}).get(aid)
            if activity is None or activity['status'] == 'finished':
                continue
            obligation = {'action_id': action['id'], 'reason': 'goal_completed_before_dispatch',
                          'evidence_ref': reference}
            activity['unresolved'].append(obligation)
            activity['followups'].append({**obligation, 'next_owner': 'user'})
            owners.add(aid)
        for aid in owners:
            activity = self.runtime['activities'][aid]
            attempts = [self.runtime['executions'][eid] for eid in activity['assigned_execution_ids']]
            if any(execution['status'] != 'ended' for execution in attempts):
                continue
            references = list(dict.fromkeys([*activity['result_refs'],
                *(execution['result_ref'] for execution in attempts if execution.get('result_ref'))]))
            activities.finish_activity(self.runtime, aid, result_refs=references,
                unresolved=activity['unresolved'], followups=activity['followups'], at=now())

    def _academic_evidence(self, ref):
        return academic.stored_evidence(self.store, self.head, ref)

    def _solution_basis(self):
        return academic.current_solution_basis(self.instance, self.runtime)

    def _academic_status(self):
        return academic.academic_status(self.instance, self.runtime, self._solution_basis(), resolve_evidence=self._academic_evidence)

    def _ensure_academic_followup(self):
        basis = self._solution_basis()
        requirements = academic.current_requirements(self.instance)
        if basis is None or self.runtime["status"] in {"paused", "closed"}: return
        current_hash = requirements["sha256"]
        for task in self.runtime["tasks"].values():
            if task.get("academic_requirement_id") and (task.get("solution_basis") != basis or task.get("requirements_sha256") != current_hash):
                if task["status"] == "closed":
                    continue
                if task["status"] == "completed":
                    # completed is absorbing; the old assessment only stops being current.
                    if isinstance(task.get("assessment"), dict) and task["assessment"].get("current") is not False:
                        task["assessment"].update(current=False, invalidated_reason="Approved academic requirements or solution basis changed")
                    continue
                task["status"] = "closed"
                task["scope_disposition"] = {"kind": "superseded_requirements", "reason": "Approved academic requirements or solution basis changed"}
                self.runtime["queue"] = [a for a in self.runtime["queue"] if a.get("target") != task["id"]]
        created = False
        for requirement in requirements["items"]:
            if any(t.get("academic_requirement_id") == requirement["id"] and t.get("solution_basis") == basis and
                   t.get("requirements_sha256") == current_hash and not (
                       t.get("status") == "completed" and t.get("assessment", {}).get("current") is False)
                   for t in self.runtime["tasks"].values()): continue
            tid = new_id("TK")
            refs = [r["id"] for r in basis["records"] if r["id"] in self.instance["knowledge"]]
            inputs = list(dict.fromkeys([*(row["id"] for row in basis["records"]), *requirement["required_inputs"]]))
            from .execution_profiles import profile_ref, match_profile_ref
            from .task_contracts import validate_task_contract
            view = governance.governance_view(self.instance)
            profiles = [match_profile_ref(self.instance.get("execution_profiles", {}), ref)
                        for ref in self.instance.get("role_profile_refs", {}).get("research_work", [])]
            if any(p["role"] != "research_work" for p in profiles):
                raise ValueError("academic work profile has a different role")
            obligations = academic.criterion_obligations(tid, requirement)
            task = {"id": tid, "revision": 1,
                "title": "Academic validation: " + requirement["id"], "question": requirement["scope"],
                "scope": {"included": [requirement["scope"]], "excluded": []},
                "expected": {"outputs": deepcopy(requirement["criteria"]),
                             "research_change": "Assess the explicit academic requirement: " + requirement["scope"]},
                "completion_obligations": obligations,
                "progress_criteria": [{"id": tid + ":progress", "claim": "Produce evidence for the stated academic criteria",
                                       "evidence_required": []}],
                "profile_refs": [profile_ref(p) for p in profiles],
                "authority_refs": [g["id"] for g in self.instance.get("grants", {}).values()
                                   if g.get("kind") == "local" and "research_work" in g.get("roles", [])],
                "basis_refs": [view["charter"]["id"], view["charter"]["approval_ref"]],
                "inputs": inputs, "reuse": refs,
                "work_class": "nonformal", "status": "planned",
                "results": [], "reviews": [], "dependencies": refs, "occurrence_condition": {"op": "always"},
                "initial_observation_rules": [],
                "academic_requirement_id": requirement["id"], "requirements_sha256": current_hash,
                "solution_basis": deepcopy(basis), "required_external_effects": deepcopy(requirement["external_effects"])}
            validate_task_contract(task)
            self.runtime["tasks"][tid] = task
            created = True
        if created:
            self._ensure_model_assessments()
        status = self._academic_status()["status"]
        if status in {"completed", "not_applicable"}:
            self.runtime["status"] = "completed"
            self._settle_goal_completion()
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
                 "created_at": request["created_at"], "solution_basis": basis}
        self.runtime.setdefault("external_rejections", []).append(entry)
        if self.runtime["status"] == "completed": self.runtime["status"] = "ready"
        self._enqueue("research_plan", reason="Examine the external rejection against the preserved solution evidence", rejection_id=entry["id"])
        return True

    def _record_academic_assessment(self, task, assessment, execution_id):
        if not task.get("academic_requirement_id"): return
        if task.get("solution_basis") != self._solution_basis() or task.get("requirements_sha256") != academic.current_requirements(self.instance)["sha256"]:
            raise ValueError("academic assessment basis changed")
        from .task_scope import assessment_current
        from .task_contracts import validate_item_dispositions
        applied = task.get("assessment", {})
        actor = self.runtime.get("executions", {}).get(execution_id, {})
        if (actor.get("role") != "research_plan" or actor.get("input_solution_basis") != task["solution_basis"]
                or applied.get("execution_id") != execution_id
                or any(applied.get(key) != value for key, value in assessment.items())
                or not assessment_current(task, self.instance, self.runtime)):
            raise ValueError("academic result requires the current applied independent TASKS assessment")
        validate_item_dispositions(task, assessment)
        requirement = next(item for item in academic.current_requirements(self.instance)["items"]
                           if item["id"] == task["academic_requirement_id"])
        expected = academic.criterion_obligations(task["id"], requirement)
        actual = {row["id"]: row for row in task["completion_obligations"]}
        if any(actual.get(row["id"]) != row for row in expected):
            raise ValueError("academic criteria differ from the approved requirement obligations")
        dispositions = {row["obligation_id"]: row for row in assessment["item_dispositions"]}
        evidence = [{"criterion": row["claim"],
                     "satisfied": dispositions.get(row["id"], {}).get("kind") == "fulfilled",
                     "evidence": ", ".join(dispositions.get(row["id"], {}).get("evidence_refs", []))}
                    for row in expected]
        decision = ("satisfied" if assessment["decision"] == "completed" and all(row["satisfied"] for row in evidence)
                    else "unresolved" if assessment.get("unresolved") else "not_satisfied")
        receipts_ok, receipts = academic.effect_receipts(requirement, task_id=task["id"],
            requirements_sha256=task["requirements_sha256"], solution_basis_value=task["solution_basis"], runtime=self.runtime)
        if decision == "satisfied" and not receipts_ok:
            raise ValueError("satisfied academic assessment lacks confirmed successful required external effects")
        result = academic.assess(task["academic_requirement_id"], task["solution_basis"], academic.current_requirements(self.instance),
                                 decision, evidence)
        result.update(execution_id=execution_id, task_id=task["id"], external_effect_receipts=receipts,
                      task_assessment_sha256=exact_content_hash(applied))
        records = self.runtime.setdefault("academic_assessments", [])
        if result not in records: records.append(result)

    def _apply_academic_resolutions(self, action, execution_id, resolutions):
        if not resolutions:
            return
        if action["role"] != "research_plan":
            raise ValueError("academic resolutions require designated planner")
        if len({r.get("id") for r in resolutions}) != len(resolutions):
            raise ValueError("rejection resolution IDs must be distinct")
        # record_resolution appends only to this ledger. Stage the ledger, not the
        # whole runtime, so a rejected resolution still leaves the runtime unchanged.
        basis = self._solution_basis()
        state = {**self.runtime, "academic_resolution_records": list(self.runtime.get("academic_resolution_records", []))}
        for resolution in resolutions:
            academic.record_resolution(self.instance, state, basis, resolution, execution_id=execution_id, resolve_evidence=self._academic_evidence)
        self.runtime["academic_resolution_records"] = state["academic_resolution_records"]
