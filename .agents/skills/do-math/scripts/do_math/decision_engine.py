"""Decision currentness, separate from exact evidence and action applicability."""
from copy import deepcopy

from . import planning, submission
from .execution_profiles import task_research
from .input_basis import capture_decision_basis, decision_basis_changes, CurrentnessChanged
from .repository import exact_content_hash, new_id
from .session_slots import held_reservations


class DecisionEngineMixin:
    def _apply_action_resolutions(self, execution_id, *, accepting_current=False):
        execution = self.runtime["executions"][execution_id]
        for claim in execution.get("extensions", {}).get("action_resolutions", []):
            identifier = claim["action_id"]
            entry = self.runtime.get("waiting_actions", {}).get(identifier)
            if not entry:
                raise ValueError("action resolution requires a current failed action")
            evidence_id = execution_id if claim["evidence_execution_id"] == "current" else claim["evidence_execution_id"]
            evidence = self.runtime["executions"].get(evidence_id, {})
            previous = entry["action"]
            # The producer ran the same check on its fixed blocked_actions row.
            errors = submission.action_resolution_errors(submission.blocked_action_row(identifier, entry),
                                                         evidence.get("action", {}))
            if errors:
                raise ValueError(errors[0])
            if not (evidence.get("outcome") == "output_accepted" or (accepting_current and evidence_id == execution_id)):
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
            failed = self.runtime["executions"].get(entry.get("execution_id"), {})
            activity_id = previous.get("owner_activity_id") or failed.get("owner_activity_id")
            activity = self.runtime.get("activities", {}).get(activity_id)
            pending = [*self.runtime.get("queue", []),
                       *(row["action"] for row in self.runtime["waiting_actions"].values())]
            if (activity and activity["status"] == "waiting"
                    and activity.get("waiting", {}).get("condition") == {"action_ids": [identifier]}
                    and not any(row.get("owner_activity_id") == activity_id for row in pending)
                    and all(self.runtime["executions"][eid]["status"] == "ended"
                            for eid in activity["assigned_execution_ids"])
                    and not held_reservations(self.runtime, activity["assigned_execution_ids"])
                    and all(isinstance(row, dict) and row.get("action_id") == identifier
                            for row in [*activity["unresolved"], *activity["followups"]])):
                from .activities import finish_activity
                finish_activity(self.runtime, activity_id,
                    result_refs=[*activity["result_refs"], evidence_id], unresolved=[],
                    followups=[{"action_id": identifier, "resolved_by": evidence_id,
                                "decision_execution_id": execution_id, "reason": claim["reason"]}],
                    at=self._lifecycle_now().isoformat())

    def _execution_requirement_changes(self, action, *, evaluation_context=None):
        if not task_research(action):
            return []
        task = self.runtime["tasks"].get(action.get("target"))
        if not task or task.get("status") in planning.TERMINAL_TASK_STATUSES:
            return []
        result = planning.task_ready(task, self.instance, self.runtime,
                                     include_scheduling_waits=False, action=action,evaluation_context=evaluation_context)
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

    def _validate_decision_acceptance(self, action, output, execution, context, *, evaluation_context=None):
        _, original_instance, original_runtime = self.store.load(execution["input_snapshot"])
        refs = {row["id"] for row in execution.get("decision_basis", {}).get("records", [])}
        refs.update(row["name"] for row in execution.get("decision_basis", {}).get("sources", []))
        refs.update(submission.reported_references(output, execution.get("extensions", {}), context))
        if action.get("review_cycle_id"):
            refs.discard(action.get("target"))
        execution["decision_basis"] = capture_decision_basis(original_instance, original_runtime, refs)
        changes = decision_basis_changes(execution["decision_basis"], self.instance, self.runtime)
        changes.extend(self._execution_requirement_changes(action,evaluation_context=evaluation_context))
        from .questions import open_links, user_waits
        changes.extend({"field": "user_decision", **row} for row in user_waits(action, self.instance, self.runtime))
        if output.get("confirmed_question_ids"):
            open_questions = {row["id"] for row in open_links(self.runtime, "user")}
            changes.extend({"id": identifier, "field": "question_applicability", "reason": "the user question is no longer open"}
                           for identifier in output["confirmed_question_ids"] if identifier not in open_questions)
        if action["role"] == "goal_audit" and action.get("basis") != self._goal_basis_key():
            changes.append({"field": "goal_audit_basis", "reason": "the complete goal judgment basis changed"})
        governance = planning.governance_revisions(self.instance)
        if any(execution[key] != value for key, value in governance.items()):
            changes.append({"field": "goal_or_policy_revision", "reason": "decision input changed"})
        current = self.runtime["tasks"].get(action.get("target"))
        if current and execution.get("contract_sha256") != planning.contract_hash(current):
            changes.append({"id": current["id"], "field": "contract_sha256", "reason": "action contract changed"})
        if current and action.get('role')=='task_contract_review':
            previous=original_runtime['tasks'].get(current['id'])
            if previous is None or planning.capture_task_basis(previous,original_instance,original_runtime)!=planning.capture_task_basis(current,self.instance,self.runtime):
                changes.append({'id':current['id'],'field':'task_basis','reason':'review source, decision, knowledge, trust or profile premise changed'})
        if action["role"] == "research_plan":
            target_ids = [*(row['task_id'] for row in output['dispositions']),
                          *(row["task_id"] for row in output["task_assessments"])]
            from .task_contracts import selected_task_ids
            for identifier in target_ids:
                before = original_runtime["tasks"].get(identifier)
                after = self.runtime["tasks"].get(identifier)
                if not before or not after or after.get("status") in planning.TERMINAL_TASK_STATUSES:
                    changes.append({"id": identifier, "field": "target_applicability", "reason": "planning target ended or missing"})
                    continue
                if planning.contract_hash(before) != planning.contract_hash(after):
                    changes.append({"id": identifier, "field": "contract_sha256", "reason": "planning target contract changed"})
                if identifier in selected_task_ids(output):
                    ready = planning.task_ready(after, self.instance, self.runtime,evaluation_context=evaluation_context)
                    if ready["state"] != "ready":
                        changes.append({"id": identifier, "field": "selection_applicability", "reason": ready["errors"]})
            for assessment in output["task_assessments"]:
                identifier = assessment["task_id"]
                before = original_runtime["tasks"].get(identifier, {})
                after = self.runtime["tasks"].get(identifier, {})
                if exact_content_hash(before.get("results", [])) != exact_content_hash(after.get("results", [])):
                    changes.append({"id": identifier, "field": "assessment_result_set", "reason": "assessment requires the current complete results"})
        if changes:
            raise CurrentnessChanged(changes)

    def _apply_task_plan(self, output, execution_id, input_tasks, ready_ids, *, reference_tasks=None, evaluation_context=None):
        """Owner application for one indivisible planning response."""
        from .task_scope import apply_task_assessments
        planning.validate_plan_submission(output, input_tasks, ready_ids)
        for row in output['dispositions']:
            current=self.runtime['tasks'].get(row['task_id'])
            before=input_tasks.get(row['task_id'])
            if not current or not before or planning.contract_hash(current)!=planning.contract_hash(before):
                raise ValueError('candidate contract changed before plan application')
            if row['kind']=='selected' and planning.task_ready(current,self.instance,self.runtime,evaluation_context=evaluation_context)['state']!='ready':
                raise ValueError('selected task is no longer ready')
        instance,runtime=apply_task_assessments(self.instance,self.runtime,output.get('task_assessments',[]),
            execution_id=execution_id,input_tasks=input_tasks,reference_tasks=reference_tasks,evaluation_context=evaluation_context)
        for row in output['dispositions']:
            task=runtime['tasks'][row['task_id']]
            if row['kind']=='selected' and planning.contract_hash(task)!=planning.contract_hash(input_tasks[task['id']]):
                raise ValueError('assessment changed a selected recipient contract; replan after review')
            task['selection_disposition']={**deepcopy(row),'execution_id':execution_id,'contract_sha256':planning.contract_hash(task)}
            if row['kind']=='selected':
                action = {'id':new_id('AC'),'role':'research_work','target':task['id'],
                    'selected_contract_sha256':planning.contract_hash(task),'selection_execution_id':execution_id}
                assessment = runtime['executions'][execution_id].get('model_decisions', {}).get(task['id'])
                if assessment is not None:
                    from .model_policy import selection
                    action['model_assessment'] = deepcopy(assessment)
                    try:
                        selection(instance['config'], action, runtime['tasks'], instance['knowledge'],
                                  instance=instance)
                    except ValueError as error:
                        raise ValueError('Selected task ' + task['id'] + ' cannot meet the plan model requirement '
                            'with its allowed profiles; defer or revise its contract: ' + str(error)) from error
                task['status']='active';task['selected_by']=execution_id
                task.pop('waiting',None)
                runtime.setdefault('queue',[]).append(action)
        runtime.setdefault('history',[]).append({'kind':'task_plan_applied','execution_id':execution_id,
            'dispositions':deepcopy(output['dispositions']),'task_assessments':deepcopy(output.get('task_assessments',[]))})
        for reason in output.get('preparation_requests',[]):
            runtime.setdefault('queue',[]).append({'id':new_id('AC'),'role':'research_preparation','reason':reason,'requested_by':execution_id})
        self.instance,self.runtime=instance,runtime
        # Bind exact semantic repetition premises to requests created by this plan.
        from .revisions import bind_repetition_bases
        for action in self.runtime.get('queue',[]):
            if action.get('requested_by')==execution_id:
                bind_repetition_bases(self.instance,self.runtime,action)

    def _refresh_changed_decision(self, action, execution_id, changes, original_position=0):
        self._remove_action(action)
        execution = self.runtime["executions"][execution_id]
        execution.update(outcome="execution_incomplete", error_kind="currentness_changed", currentness_changes=deepcopy(changes),
                         error="Decision premises changed; see currentness_changes")
        from .revisions import record_execution_outcome
        record_execution_outcome(self.instance,self.runtime,action,{},execution_id,accepted=False)
        if action.get("refresh", {}).get("attempt", 0) < 1:
            refreshed = {**deepcopy(action), "refresh": {"execution_id": execution_id, "changes": deepcopy(changes), "attempt": 1}}
            refreshed.pop("model_selection", None)
            if action["role"] == "task_contract_review":
                task = self.runtime["tasks"][action["target"]]
                refreshed["contract_basis"] = {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                    **planning.governance_revisions(self.instance)}
                refreshed["review_basis_key"] = planning.review_basis_key(task, self.instance, self.runtime)
            self.runtime["queue"].insert(original_position, refreshed)
        else:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": deepcopy(action),
                "kind": "execution_failure", "failure_kind": "currentness_changed", "changes": deepcopy(changes),
                "reason": "decision premises changed again after one refresh", "execution_id": execution_id}
            if action["role"] != "operational_review":
                self._enqueue("operational_review", execution_id, reason="Resolve repeated decision premise conflicts")
            else:
                self.runtime['waiting_actions'][action['id']].update(next_owner='operations',
                    release_condition='new consistent decision input', owner='ai')
