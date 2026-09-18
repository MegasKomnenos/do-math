"""Revision requests retain their obligations through delegation and recovery."""
from copy import deepcopy

from . import planning, revisions
from .input_basis import CurrentnessChanged
from .repository import new_id


class RevisionEngineMixin:
    def _retire_closed_revision_targets(self):
        closed = {identifier for identifier, task in self.runtime['tasks'].items()
                  if task.get('status') in planning.TERMINAL_TASK_STATUSES}
        live = {execution.get('action', {}).get('id') for execution in self.runtime['executions'].values()
                if execution.get('status') != 'ended'}
        containers = [(action.get('id'), action, None) for action in list(self.runtime['queue'])]
        containers.extend((identifier, entry['action'], entry) for identifier, entry in list(self.runtime.get('waiting_actions', {}).items()))
        for identifier, action, entry in containers:
            if identifier in live:
                continue
            if (action.get('target') in closed and action.get('role') in {'research_work', 'supplemental_research', 'task_contract_review'}
                    and (not entry or entry.get('kind') != 'revision_dependency')):
                self.runtime['history'].append({'kind': 'action_retired_after_target_disposition', 'action': deepcopy(action),
                                                'previous': deepcopy(entry)})
                if entry:
                    self.runtime['waiting_actions'].pop(identifier, None)
                else:
                    self._remove_action(action)
                continue
            targets = entry.get('revision_targets', action.get('revision_targets', {})) if entry else action.get('revision_targets', {})
            retired = set(targets) & closed
            if not retired:
                continue
            remaining = {key: deepcopy(value) for key, value in targets.items() if key not in retired}
            self.runtime['history'].append({'kind': 'revision_targets_retired_after_disposition',
                'action_id': identifier, 'targets': sorted(retired), 'previous_targets': deepcopy(targets)})
            action['revision_targets'] = remaining
            if action.get('target') in retired:
                action.pop('target', None)
            if entry:
                entry['revision_targets'] = deepcopy(remaining)
                if not remaining:
                    del self.runtime['waiting_actions'][identifier]
            elif not remaining:
                self._remove_action(action)

    def _selected_action_current(self, action):
        if action.get("role") not in {"research_work", "supplemental_research"} or action.get("review_cycle_id"):
            return True
        task = self.runtime["tasks"].get(action.get("target"))
        if not task:
            return True  # The existing obsolete/structural path owns missing tasks.
        contract_changed = action.get("selected_contract_sha256") not in {None, planning.contract_hash(task)}
        ready_task = {**task, "status": "ready"}
        result = planning.task_ready(ready_task, self.instance, self.runtime, include_scheduling_waits=False)
        if not contract_changed and result["state"] == "ready":
            return True
        if result.get("waits"):
            return False
        self._remove_action(action)
        self.runtime["history"].append({"kind": "obsolete_selection", "action": deepcopy(action),
                                        "reason": "selected contract or its approval is no longer current", "readiness": result})
        if task["status"] not in planning.TERMINAL_TASK_STATUSES:
            task["status"] = "waiting"
            task.pop("selected_by", None)
        self._enqueue("research_plan", reason="A selected contract or its approval changed before dispatch")
        return False

    def _bind_revision_action(self, action):
        action.setdefault("revision_targets", {})
        target = action.get("target")
        if action.get("role") == "research_preparation" and "assessment_targets" not in action and not action["revision_targets"] and target in self.runtime["tasks"]:
            task = self.runtime["tasks"][target]
            if task.get("status") not in planning.TERMINAL_TASK_STATUSES:
                required = bool(task.get("revision_requested")) or any(r.get("revision") == task.get("revision") and r.get("decision") != "approved" for r in task.get("reviews", []))
                action["revision_targets"] = revisions.capture_targets(self.instance, self.runtime, [target], required=required,
                    source_ref=action.get("contract_review_execution") or action.get("decision_id"))
        if action.get("role") in {"research_work", "supplemental_research"} and not action.get("review_cycle_id"):
            task = self.runtime["tasks"].get(target, {})
            if task.get("knowledge_revision_targets") and not action["revision_targets"]:
                action["revision_targets"] = revisions.capture_targets(self.instance, self.runtime, task["knowledge_revision_targets"])
            if task.get("revision_request_action_id"):
                action["revision_request_action_id"] = task["revision_request_action_id"]
        if action.get("role") == "research_preparation" and action["revision_targets"]:
            for parent_id, entry in self.runtime.get("waiting_actions", {}).items():
                if entry.get("kind") != "revision_dependency" or parent_id == action.get("id"):
                    continue
                shared = set(action["revision_targets"]) & set(entry.get("revision_targets", {}))
                shared -= set(entry.get("delegated_targets", {}))
                for identifier in shared:
                    basis = action["revision_targets"][identifier]
                    basis["required"] = bool(basis.get("required") or entry["revision_targets"][identifier].get("required"))
                    reference = {"action_id": parent_id, "reason": entry.get("reason")}
                    if reference not in basis.setdefault("obligation_refs", []):
                        basis["obligation_refs"].append(reference)
                if shared:
                    action["revision_parent_ids"] = list(dict.fromkeys([*action.get("revision_parent_ids", []), parent_id]))

    def _reconcile_revision_delegations(self):
        for parent_id, entry in list(self.runtime.get("waiting_actions", {}).items()):
            if entry.get("kind") != "revision_dependency":
                continue
            detached = []
            for identifier, task_id in list(entry.get("delegated_targets", {}).items()):
                task = self.runtime["tasks"].get(task_id, {})
                if task.get("status") in planning.TERMINAL_TASK_STATUSES or identifier not in task.get("knowledge_revision_targets", []):
                    del entry["delegated_targets"][identifier]
                    detached.append({"record_id": identifier, "task_id": task_id})
            if detached:
                entry["delegated_to_task_id"] = next(iter(entry["delegated_targets"].values()), None)
                entry.setdefault("delegation_history", []).extend(detached)
                if self.runtime['status'] not in {'closed', 'completed'}:
                    self._enqueue("research_plan", reason="A delegated task ended or changed while its revision obligation remains: " + parent_id,
                                  revision_followup=detached)

    def _cancel_selected_revision_targets(self, action):
        live_ids = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        for identifier in action.get("revision_targets", {}):
            task = self.runtime["tasks"].get(identifier)
            if not task or task.get("status") != "performing":
                continue
            selected = [a for a in self.runtime["queue"] if a.get("target") == identifier and a["role"] in {"research_work", "supplemental_research"}
                        and not a.get("review_cycle_id") and a.get("id") not in live_ids]
            if any(e.get("action", {}).get("target") == identifier and e["status"] != "ended" for e in self.runtime["executions"].values()):
                continue
            for previous in selected:
                self._remove_action(previous)
                self.runtime["history"].append({"kind": "selection_cancelled_for_revision", "action": deepcopy(previous),
                                                "revision_action_id": action.get("id")})
            task["status"] = "needs_revision"
            task.pop("selected_by", None)

    def _revision_dispatch_waits(self, action):
        self._bind_revision_action(action)
        if action.get("revision_targets"):
            self._cancel_selected_revision_targets(action)
            changes = revisions.target_changes(action["revision_targets"], self.instance, self.runtime)
            if changes:
                previous = deepcopy(action["revision_targets"])
                for identifier in list(action["revision_targets"]):
                    old = action["revision_targets"][identifier]
                    try:
                        current = revisions.capture_targets(self.instance, self.runtime, [identifier])[identifier]
                    except ValueError:
                        continue
                    action["revision_targets"][identifier] = {**old, **{k: v for k, v in current.items() if k != "required"}}
                action.setdefault("superseded_revision_bases", []).append(previous)
        from .questions import user_waits
        return [*user_waits(action, self.instance, self.runtime), *planning.revision_waits(action, self.instance, self.runtime)]

    def _apply_revision_followup(self, action, output, execution_id):
        execution = self.runtime["executions"][execution_id]
        extension = execution.get("extensions", {})
        for request in extension.get("revision_requests", []):
            self._enqueue("research_preparation", reason=request["reason"], requested_by=execution_id,
                revision_targets=revisions.capture_targets(self.instance, self.runtime, request["record_ids"], source_ref=execution_id))
        declared = action.get("revision_targets", {})
        if not declared:
            return
        if action.get("role") in {"research_work", "supplemental_research"} and extension.get("knowledge_changes"):
            task = self.runtime["tasks"].get(action.get("target"))
            if task and task.get("status") not in planning.TERMINAL_TASK_STATUSES and output.get("outcome") != "waiting":
                # Dependency propagation must not hide this writer's newly
                # submitted result from the completion assessor.
                task["status"] = "assessing"
                task.pop("status_before_reassessment", None)
        resolutions = {row["record_id"]: row for row in extension.get("revision_resolutions", [])}
        withdrawals = {row["task_id"] for row in extension.get("task_dispositions", [])}
        unresolved, delegated = {}, {}
        for identifier, basis in declared.items():
            if identifier in withdrawals:
                continue
            row = resolutions[identifier]  # Exact coverage was checked against fixed input.
            disposition = row["disposition"]
            if disposition in {"revised", "unchanged"}:
                continue
            unresolved[identifier] = deepcopy(basis)
            if disposition == "delegated":
                matches = [task for task in self.runtime["tasks"].values()
                           if task.get("producer_execution") == execution_id and task["title"] == row["task_title"]]
                if len(matches) != 1 or identifier not in matches[0].get("knowledge_revision_targets", []):
                    raise ValueError("delegated revision does not identify its prepared knowledge-revision task")
                task = matches[0]
                task["revision_request_action_id"] = action["id"]
                delegated[identifier] = task["id"]
        owners = list(dict.fromkeys([*([action["revision_request_action_id"]] if action.get("revision_request_action_id") else []),
                                     *action.get("revision_parent_ids", [])]))
        for owner in owners:
            entry = self.runtime.get("waiting_actions", {}).get(owner)
            if entry and entry.get("kind") == "revision_dependency":
                remaining = deepcopy(entry.get("revision_targets", {}))
                transferred = False
                for identifier in declared:
                    if identifier not in remaining:
                        continue
                    disposition = resolutions[identifier]["disposition"]
                    if disposition in {"revised", "delegated"} or (disposition == "unchanged" and not remaining[identifier].get("required")):
                        remaining.pop(identifier, None)
                        transferred |= disposition == "delegated"
                    elif disposition == "deferred":
                        entry.setdefault("deferrals", {})[identifier] = {"execution_id": execution_id, "reason": resolutions[identifier]["reason"]}
                        unresolved.pop(identifier, None)
                if remaining:
                    entry["revision_targets"] = remaining
                    entry["action"]["revision_targets"] = deepcopy(remaining)
                    entry["delegated_targets"] = {key: value for key, value in entry.get("delegated_targets", {}).items() if key in remaining}
                else:
                    self.runtime["history"].append({"kind": "revision_obligation_transferred" if transferred else "revision_obligation_resolved", "action_id": owner,
                        "execution_id": execution_id, "to_action_id": action["id"] if transferred else None, "previous": deepcopy(entry)})
                    del self.runtime["waiting_actions"][owner]
        if unresolved:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": {**deepcopy(action), "revision_targets": deepcopy(unresolved)}, "kind": "revision_dependency",
                "revision_targets": unresolved, "delegated_targets": delegated,
                "delegated_to_task_id": next(iter(delegated.values()), None), "execution_id": execution_id,
                "reason": "; ".join(resolutions[identifier]["reason"] for identifier in unresolved)}
        elif action["id"] in self.runtime.get("waiting_actions", {}):
            previous = self.runtime["waiting_actions"][action["id"]]
            if previous.get("kind") == "revision_dependency":
                self.runtime["history"].append({"kind": "revision_obligation_resolved", "action_id": action["id"],
                    "execution_id": execution_id, "previous": deepcopy(previous)})
                del self.runtime["waiting_actions"][action["id"]]
