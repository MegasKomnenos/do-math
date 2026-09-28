"""Engine integration for the preparation and planning outputs: model assessments, observation rules and the queue plan."""
from __future__ import annotations

from copy import deepcopy
from .execution_profiles import PLANNING_ROLES, RESEARCH_PRODUCER_ROLES, task_research
from .model_policy import assessment_basis, edition_current, validate_assessments, preparation_only
from .planning import revision_requested
from .session_slots import live_action_ids
from .task_contracts import TERMINAL_TASK_STATUSES

class PlanningEngineMixin:
    def _apply_model_metadata(self, action, output, execution_id):
        extensions = self.runtime["executions"][execution_id].get("extensions", {})
        if action["role"] not in PLANNING_ROLES:
            if extensions.get("model_assessments"):
                raise ValueError("only preparation and planning author model assessments")
            return
        identified = validate_assessments(action, output, extensions, self.runtime["tasks"])
        if preparation_only(action):
            for field in ('assessment_targets', 'observation_rule_targets'):
                for tid, basis in action.get(field, {}).items():
                    if not edition_current(self.runtime['tasks'].get(tid), basis):
                        raise ValueError(field + ' task edition changed: ' + tid)
                    if any(e.get('status') != 'ended' and e.get('action', {}).get('target') == tid
                           for e in self.runtime['executions'].values()):
                        raise ValueError('preparation target has a live execution: ' + tid)
            from .observations import validate_rule_preparation
            validate_rule_preparation(action, extensions, self.runtime['tasks'])
        # Keep the authored wire candidate unchanged. The task constructor's
        # caller installs these assessed values in the resulting task record.
        self.runtime["executions"][execution_id]["model_decisions"] = identified

    def _assessment_input_version(self):
        from .initialization import governance_working_view
        view = governance_working_view(self.instance)
        return {"goal": view['goal_revision'], "policy": view['policy_revision'],
                "sources": [{"name": s["name"], "sha256": s["sha256"]} for s in self.instance["sources"]],
                "inputs": [i.get("id") for i in self.runtime["inputs"]]}

    def _retry_observation_configuration(self):
        from .observations import observation_settings_errors
        for aid, entry in list(self.runtime.get('waiting_actions', {}).items()):
            if entry.get('kind') != 'observation_configuration':
                continue
            action = entry['action']
            task = self.runtime['tasks'].get(action.get('target'))
            if task and action['role'] in RESEARCH_PRODUCER_ROLES:
                from .execution_profiles import match_profile_ref
                current = [match_profile_ref(self.instance['execution_profiles'], ref)
                           for ref in self.instance['role_profile_refs'].get(action['role'], [])]
                if current and all(not observation_settings_errors(p) for p in current) and not task.get('academic_requirement_id'):
                    self._enqueue('research_preparation', task['id'],
                        reason='Reprepare the task with valid current observation profiles; preserve its old profile references in revision history')
                continue
            fresh = deepcopy(action)
            for key in ('profile_ref', 'model_selection', 'actor_kind', 'dispatch_wait'):
                fresh.pop(key, None)
            try:
                profile = self._execution_profile(fresh)
            except ValueError:
                continue
            if observation_settings_errors(profile) or fresh['profile_ref'] == action.get('profile_ref'):
                continue
            self.runtime['history'].append({'kind': 'observation_configuration_reprepared',
                'action_id': aid, 'previous': deepcopy(entry), 'profile_ref': deepcopy(fresh['profile_ref'])})
            self.runtime['queue'].append(fresh)
            del self.runtime['waiting_actions'][aid]

    def _resolve_task_observation_waits(self, task_id, execution_id):
        for aid, entry in list(self.runtime.get('waiting_actions', {}).items()):
            if (entry.get('kind') in {'observation_rules', 'observation_configuration'}
                    and entry.get('action', {}).get('target') == task_id
                    and entry['action']['role'] in RESEARCH_PRODUCER_ROLES):
                self.runtime['history'].append({'kind': entry['kind'] + '_resolved', 'action_id': aid,
                    'failed_execution_id': entry.get('execution_id'), 'resolved_by': execution_id,
                    'previous': deepcopy(entry)})
                del self.runtime['waiting_actions'][aid]
                activity_id = entry['action'].get('owner_activity_id')
                activity = self.runtime.get('activities', {}).get(activity_id)
                pending = [*self.runtime['queue'], *(w['action'] for w in self.runtime['waiting_actions'].values())]
                if (activity and activity['status'] != 'finished'
                        and not any(a.get('owner_activity_id') == activity_id for a in pending)
                        and all(self.runtime['executions'][eid]['status'] == 'ended' for eid in activity['assigned_execution_ids'])):
                    from .activities import finish_activity
                    finish_activity(self.runtime, activity_id, result_refs=[execution_id], unresolved=[],
                        followups=[task_id], at=self._lifecycle_now().isoformat())

    def _rule_deferral_inputs(self, deferrals):
        from .input_basis import aliases
        from .planning import record_index
        from .repository import exact_content_hash
        records = record_index(self.instance, self.runtime)
        values = {}
        for ref in {ref for row in deferrals for ref in row['missing_inputs']}:
            if ref == 'user_input':
                values[ref] = [row.get('id') for row in self.runtime['inputs']]
            elif ref in records:
                values[ref] = exact_content_hash(records[ref][1])
            else:
                source = next((s for s in self.instance['sources'] if ref in aliases(s)), None)
                values[ref] = source['sha256'] if source else None
        return values

    def _ensure_model_assessments(self):
        """Prepare ratings and academic observation rules before contract review."""
        from .observations import validate_task_rules
        live = live_action_ids(self.runtime)
        for tid, task in self.runtime["tasks"].items():
            if (not task.get('academic_requirement_id') or not revision_requested(task)
                    or task.get('status') in TERMINAL_TASK_STATUSES):
                continue
            basis = assessment_basis(task)
            review = next((r for r in reversed(task.get("reviews", []))
                           if all(r.get(k) == v for k, v in basis.items())), None)
            if not review or review.get("decision") == "approved":
                continue
            if any(row.get('contract_review_execution') == review['execution_id']
                   for row in task.get('observation_rule_history', [])):
                # A fresh assessment may legitimately keep the same value.
                # Its pending independent review, not an already-consumed
                # rejection, owns the next judgment.
                continue
            if task.get('model_assessment'):
                task.setdefault('model_assessment_history', []).append({
                    **basis, 'assessment': task.pop('model_assessment'),
                    'contract_review_execution': review['execution_id']})
            task.setdefault('observation_rule_history', []).append({
                **basis, 'rules': task.pop('initial_observation_rules', []),
                'contract_review_execution': review['execution_id']})
            self.runtime.get('task_observation_rules', {}).pop(tid, None)
        missing = {tid: assessment_basis(task) for tid, task in self.runtime["tasks"].items()
                   if task.get("status") not in TERMINAL_TASK_STATUSES and not task.get("model_assessment")}
        missing_rules = {}
        for tid, task in self.runtime['tasks'].items():
            if not task.get('academic_requirement_id') or task.get('status') in TERMINAL_TASK_STATUSES:
                continue
            try:
                validate_task_rules(task.get('initial_observation_rules', []))
            except ValueError:
                missing_rules[tid] = assessment_basis(task)
        missing_by_field = {'assessment_targets': missing, 'observation_rule_targets': missing_rules}
        for aid, entry in list(self.runtime.get("waiting_actions", {}).items()):
            if entry.get('kind') not in {'model_assessment_input', 'observation_rule_input'}:
                continue
            inputs_changed = (entry.get('rule_input_version') != self._rule_deferral_inputs(entry.get('observation_rule_deferrals', []))
                if entry.get('kind') == 'observation_rule_input' and not entry['action'].get('assessment_targets')
                else entry.get('input_version') != self._assessment_input_version())
            if (inputs_changed
                    or any(missing_by_field[field].get(tid) != basis for field in missing_by_field
                           for tid, basis in entry['action'].get(field, {}).items())):
                self.runtime["history"].append({"kind": "assessment_inputs_changed", "action_id": aid})
                self.runtime["questions"] = [q for q in self.runtime["questions"] if q != entry.get("question")]
                del self.runtime["waiting_actions"][aid]
        self.runtime["queue"][:] = [a for a in self.runtime["queue"] if not (
            a["role"] == "task_contract_review" and a.get("target") in missing.keys() | missing_rules.keys() and a.get("id") not in live)]
        pending = (self.runtime['queue'] + [e['action'] for e in self.runtime.get('waiting_actions', {}).values()]
                   + [e['action'] for e in self.runtime['executions'].values() if e['status'] != 'ended'])
        targets = {}
        for field, needed in missing_by_field.items():
            covered = {tid for a in pending for tid, basis in a.get(field, {}).items() if needed.get(tid) == basis}
            uncovered = {tid: basis for tid, basis in needed.items() if tid not in covered}
            if uncovered:
                targets[field] = uncovered
        if targets:
            from .repository import new_id
            self.runtime["queue"].append({"id": new_id("AC"), "role": "research_preparation",
                **targets, 'reason': 'Prepare the assigned ratings and observation rules before independent review. '
                'Preserve the user contract. Read prior reviews and preparation histories when repairing rejected preparation.'})
        return set(missing) | set(missing_rules)

    def _finish_assessment_preparation(self, action, execution_id):
        from .initialization import governance_working_view
        from .observations import validate_rule_preparation, validate_task_rules
        from .planning import review_basis_key
        view = governance_working_view(self.instance)
        execution = self.runtime['executions'][execution_id]
        extensions = execution.get('extensions', {})
        rules = validate_rule_preparation(action, extensions, self.runtime['tasks'])
        ratings = execution.get('model_decisions', {})
        self._cancel_selected_revision_targets(action)
        for tid in set(rules) | set(ratings):
            task = self.runtime['tasks'][tid]
            if tid in rules and task.get('initial_observation_rules') != rules[tid]:
                previous = deepcopy(task)
                previous.pop('revision_history', None)
                task.setdefault('revision_history', []).append(previous)
                task.update(revision=task['revision'] + 1, initial_observation_rules=deepcopy(rules[tid]),
                            status='planned', producer_execution=execution_id)
                self.runtime.get('task_observation_rules', {}).pop(tid, None)
                task.pop('selected_by', None)
                task.pop('selection_disposition', None)
            if tid in ratings:
                task['model_assessment'] = deepcopy(ratings[tid])
            try:
                validate_task_rules(task.get('initial_observation_rules', []))
            except ValueError:
                continue
            if not task.get('model_assessment'):
                continue
            from .model_policy import work_profile_selection
            work_profile_selection(self.instance['config'], task, self.instance)
            basis = {**assessment_basis(task), 'goal_revision': view['goal_revision'], 'policy_revision': view['policy_revision']}
            self._enqueue('task_contract_review', tid, contract_basis=basis,
                review_basis_key=review_basis_key(task, self.instance, self.runtime),
                reason='Prepared execution settings require independent contract review')
            if tid in rules:
                self._resolve_task_observation_waits(tid, execution_id)
        deferred = extensions.get('model_assessment_deferrals', [])
        deferred_rules = extensions.get('observation_rule_deferrals', [])
        if deferred or deferred_rules:
            pending = {field: {row['task_id']: assessment_basis(self.runtime['tasks'][row['task_id']]) for row in rows}
                       for field, rows in (('assessment_targets', deferred), ('observation_rule_targets', deferred_rules)) if rows}
            question = 'Task preparation pending: ' + '; '.join(row['task_id'] + ': ' + row['reason'] for row in [*deferred, *deferred_rules])
            self.runtime["questions"].append(question)
            held_action = {key: value for key, value in action.items() if key not in {'assessment_targets', 'observation_rule_targets'}}
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": {**held_action, **pending}, "kind": 'observation_rule_input' if deferred_rules else 'model_assessment_input',
                'observation_rule_deferrals': deepcopy(deferred_rules),
                'rule_input_version': self._rule_deferral_inputs(deferred_rules),
                "reason": question, "question": question, "input_version": self._assessment_input_version(), "execution_id": execution_id}

    def _apply_queue_plan(self, execution_id):
        # The receiver's submission check fixed every row before this application: only
        # research_plan may write this family (extension_schema), and each row names a distinct
        # request of its input's queued_work with keep or cancel and a reason. What can differ
        # now is the current queue, which this loop checks.
        dispositions = self.runtime["executions"][execution_id].get("extensions", {}).get("queued_requests", [])
        if not dispositions:
            return
        live = live_action_ids(self.runtime)
        current = {a.get("id"): a for a in self.runtime["queue"]}
        ordered = []
        for row in dispositions:
            aid = row["request_id"]
            if aid in live or aid not in current:
                self.runtime["history"].append({"kind": "queue_plan_not_applied", "execution_id": execution_id, **row})
                continue
            request = current[aid]
            if row["decision"] == "cancel":
                self._remove_action(request)
                task = self.runtime["tasks"].get(request.get("target"))
                if task and task_research(request) and task["status"] == "active":
                    task.update(status="planned", deferred_reason=row["reason"])
            else:
                ordered.append(request)
            self.runtime["history"].append({"kind": "queue_plan_applied", "execution_id": execution_id, **row})
        # Keep non-work requests in their existing positions and preserve unseen
        # requests, including those created after the planning snapshot.
        reorder_ids = {a["id"] for a in ordered}
        positions = [i for i, a in enumerate(self.runtime["queue"]) if a.get("id") in reorder_ids]
        for position, request in zip(positions, ordered):
            self.runtime["queue"][position] = request
