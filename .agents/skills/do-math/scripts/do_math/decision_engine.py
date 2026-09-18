"""Decision currentness, separate from exact evidence and action applicability."""
from copy import deepcopy

from . import planning, submission
from .input_basis import capture_decision_basis, decision_basis_changes, CurrentnessChanged
from .repository import new_id


class DecisionEngineMixin:
    def _apply_action_resolutions(self, execution_id):
        execution = self.runtime["executions"][execution_id]
        for claim in execution.get("extensions", {}).get("action_resolutions", []):
            identifier = claim["action_id"]
            entry = self.runtime.get("waiting_actions", {}).get(identifier)
            if not entry or entry.get("kind") not in {"output_validation", "execution_failure"}:
                raise ValueError("action resolution requires a current failed action")
            evidence_id = execution_id if claim["evidence_execution_id"] == "current" else claim["evidence_execution_id"]
            evidence = self.runtime["executions"].get(evidence_id, {})
            previous, current = entry["action"], evidence.get("action", {})
            keys = ("role", "stage", "slot", "round", "review_cycle_id", "assessment_targets", "live")
            same_target = previous.get("target") == current.get("target") or previous.get("target") in current.get("revision_targets", {})
            if evidence.get("outcome") != "output_accepted" or not same_target or not all(previous.get(key) == current.get(key) for key in keys):
                raise ValueError("resolution evidence must be an accepted execution of the same judgment scope")
            # Current output was validated immediately before this atomic apply;
            # its own accepted edits are not concurrent premise changes.
            if evidence_id != execution_id and decision_basis_changes(evidence.get("decision_basis"), self.instance, self.runtime):
                raise ValueError("resolution evidence no longer has current premises")
            required = set(previous.get("revision_targets", {}))
            revised = {row["record_id"] for row in evidence.get("extensions", {}).get("revision_resolutions", []) if row["disposition"] == "revised"}
            if required - revised:
                raise ValueError("failed revision obligations require the actual accepted revisions")
            self.runtime["history"].append({"kind": "failed_action_explicitly_resolved", "action_id": identifier,
                "failed_execution_id": entry.get("execution_id"), "resolved_by": evidence_id,
                "decision_execution_id": execution_id, "reason": claim["reason"], "previous": deepcopy(entry)})
            del self.runtime["waiting_actions"][identifier]
            for event in self.runtime.get("events", []):
                if event.get("assigned_to") == identifier and not event.get("consumed_at"):
                    event.pop("assigned_to", None)
                    event.pop("assigned_at", None)

    def _execution_requirement_changes(self, action):
        if action.get("role") not in {"research_work", "supplemental_research"} or action.get("review_cycle_id"):
            return []
        task = self.runtime["tasks"].get(action.get("target"))
        if not task or task.get("status") in planning.TERMINAL_TASK_STATUSES:
            return []
        result = planning.task_ready({**task, "status": "ready"}, self.instance, self.runtime,
                                     include_scheduling_waits=False)
        return ([] if result["state"] == "ready" else [{"id": task["id"], "field": "required_use_conditions",
                                                         "reason": result["errors"]}])

    def _decision_references(self, action):
        # A global plan's conflict scope is wider than its actual decision
        # premises; bind its selected/assessed/cited records on submission.
        refs = (set() if action.get("role") == "research_plan" else
                planning.action_read_ids(action, self.instance, self.runtime))
        # Peer review appends are governed by the sealed proposal digest/slot.
        if action.get("review_cycle_id"):
            refs.discard(action.get("target"))
        task = self.runtime["tasks"].get(action.get("target"), {})
        refs.update(ref for key in ("inputs", "reuse") for ref in task.get(key, []))
        return sorted(refs)

    def _validate_decision_acceptance(self, action, output, execution, context):
        _, original_instance, original_runtime = self.store.load(execution["input_snapshot"])
        refs = {row["id"] for row in execution.get("decision_basis", {}).get("records", [])}
        refs.update(row["name"] for row in execution.get("decision_basis", {}).get("sources", []))
        refs.update(submission.reported_references(output, execution.get("extensions", {}), context))
        if action.get("review_cycle_id"):
            refs.discard(action.get("target"))
        execution["decision_basis"] = capture_decision_basis(original_instance, original_runtime, refs)
        changes = decision_basis_changes(execution["decision_basis"], self.instance, self.runtime)
        changes.extend(self._execution_requirement_changes(action))
        from .questions import user_waits
        changes.extend({"field": "user_decision", **row} for row in user_waits(action, self.instance, self.runtime))
        if output.get("confirmed_question_ids"):
            open_questions = {row["id"] for row in self.runtime.get("question_links", []) if row["status"] == "open" and row["owner"] == "user"}
            changes.extend({"id": identifier, "field": "question_applicability", "reason": "the user question is no longer open"}
                           for identifier in output["confirmed_question_ids"] if identifier not in open_questions)
        if action["role"] == "goal_audit" and action.get("basis") != self._goal_basis_key():
            changes.append({"field": "goal_audit_basis", "reason": "the complete goal judgment basis changed"})
        if execution["goal_revision"] != self.instance.get("goal_revision", 1) or execution["policy_revision"] != self.instance.get("policy_revision", 1):
            changes.append({"field": "goal_or_policy_revision", "reason": "decision input changed"})
        current = self.runtime["tasks"].get(action.get("target"))
        if current and execution.get("contract_sha256") != planning.contract_hash(current):
            changes.append({"id": current["id"], "field": "contract_sha256", "reason": "action contract changed"})
        if action["role"] == "research_plan":
            target_ids = [*output["selections"], *(row["task_id"] for row in output["deferred"]),
                          *(row["task_id"] for row in output["task_assessments"])]
            for identifier in target_ids:
                before = original_runtime["tasks"].get(identifier)
                after = self.runtime["tasks"].get(identifier)
                if not before or not after or after.get("status") in planning.TERMINAL_TASK_STATUSES:
                    changes.append({"id": identifier, "field": "target_applicability", "reason": "planning target ended or missing"})
                    continue
                if planning.contract_hash(before) != planning.contract_hash(after):
                    changes.append({"id": identifier, "field": "contract_sha256", "reason": "planning target contract changed"})
                if identifier in output["selections"]:
                    ready = planning.task_ready(after, self.instance, self.runtime)
                    if ready["state"] != "ready":
                        changes.append({"id": identifier, "field": "selection_applicability", "reason": ready["errors"]})
            for assessment in output["task_assessments"]:
                identifier = assessment["task_id"]
                before = original_runtime["tasks"].get(identifier, {})
                after = self.runtime["tasks"].get(identifier, {})
                if planning._hash(before.get("results", [])) != planning._hash(after.get("results", [])):
                    changes.append({"id": identifier, "field": "assessment_result_set", "reason": "assessment requires the current complete results"})
        if changes:
            raise CurrentnessChanged(changes)

    def _refresh_changed_decision(self, action, execution_id, changes, original_position=0):
        self._remove_action(action)
        execution = self.runtime["executions"][execution_id]
        execution.update(outcome="execution_incomplete", error_kind="currentness_changed", currentness_changes=deepcopy(changes),
                         error="Decision premises changed; see currentness_changes")
        if action.get("refresh", {}).get("attempt", 0) < 1:
            refreshed = {**deepcopy(action), "refresh": {"execution_id": execution_id, "changes": deepcopy(changes), "attempt": 1}}
            refreshed.pop("model_selection", None)
            if action["role"] == "task_contract_review":
                task = self.runtime["tasks"][action["target"]]
                refreshed["contract_basis"] = {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                    "goal_revision": self.instance["goal_revision"], "policy_revision": self.instance["policy_revision"]}
                refreshed["review_basis_key"] = planning.review_basis_key(task, self.instance, self.runtime)
            self.runtime["queue"].insert(original_position, refreshed)
            if self.runtime["status"] not in {"paused", "closed"}:
                self.runtime["status"] = "ready"
        else:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": deepcopy(action),
                "kind": "execution_failure", "failure_kind": "currentness_changed", "changes": deepcopy(changes),
                "reason": "decision premises changed again after one refresh", "execution_id": execution_id}
            if action["role"] != "operational_review" and action.get("recovery_attempt", 0) < 1:
                self._enqueue("operational_review", execution_id, reason="Resolve repeated decision premise conflicts")
            elif action.get("recovery_attempt", 0) >= 1:
                self._finish_failed_investigation(action, execution_id, "Repeated premise conflict")
            if self.runtime["status"] not in {"paused", "closed"}:
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
