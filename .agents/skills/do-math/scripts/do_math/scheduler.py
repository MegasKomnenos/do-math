"""Instance scheduler: model calls run concurrently, state transitions run serially."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

from .model_policy import assessment_basis, selection, validate_assessments, preparation_only
from .parallel import ModelCalls
from .session_slots import SessionSlots

MACHINE_ROLES = {"formal_check", "trust_check", "trust_activate", "external_action"}
WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}


class SchedulerMixin:
    def _local_call_returned(self, execution_id, result):
        if execution_id is None:
            return
        execution = self.runtime['executions'][execution_id]
        if execution.get('launch_ticket'):
            execution['launch_ticket']['phase'] = 'not_started' if result.get('launch_not_created') is True else 'finished'

    def _run_machine_steps(self, generator, *, calculator=None):
        """Start only the blocking calculation; resume its owner continuation once."""
        try:
            execution_id, arguments = next(generator)
        except StopIteration as completed:
            return completed.value
        if not hasattr(self, '_live_execution_ids'):
            self._live_execution_ids = set()
        self._live_execution_ids.add(execution_id)
        calculator = calculator or self.formal_verifier
        if getattr(self, '_calls', None) is not None:
            self._calls.start_call(generator, calculator, arguments, execution_id=execution_id)
            return False  # The queued request remains owned until completion.
        try:
            result = calculator(**arguments)
        except Exception as error:
            result = {'status': 'failed', 'reason': f'{type(error).__name__}: {error}'}
        self._local_call_returned(execution_id, result)
        try:
            generator.send(result)
        except StopIteration as completed:
            return completed.value
        finally:
            self._live_execution_ids.discard(execution_id)
        raise RuntimeError('machine execution yielded more than one calculation')

    def _abort_parallel_calls(self):
        """Preserve returned evidence and reconcile confirmed Jobs after owner failure."""
        from .repository import canonical_json, new_id
        from .governance import timestamp
        from .engine import json_safe
        returned = []
        for future, generator in self._calls.futures.items():
            execution_id = future.execution_id
            try:
                result = future.result()
            except BaseException as error:
                result = {'status': 'failed', 'reason': f'{type(error).__name__}: {error}'}
            if execution_id:
                raw = canonical_json(json_safe(result))
                # This local copy remains available even if publication itself failed.
                path = Path(self.instance['workspace']) / 'execution-recovery' / execution_id / 'returned-result.json'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                returned.append((execution_id, raw, str(path), result))
            generator.close()
        self.head, self.instance, self.runtime = self.store.load()
        self._saved_state = self._state_signature()
        artifacts = {}
        for execution_id, raw, local_path, result in returned:
            execution = self.runtime['executions'].get(execution_id)
            if not execution or execution['status'] == 'ended':
                continue
            reference = f'runtime/artifacts/{new_id("BA")}/interrupted-result.json'
            artifacts[reference] = raw
            execution['result_ref'] = reference
            execution['stop_requested'] = 'engine_error'
            self._local_call_returned(execution_id, result)
            execution['error'] = 'executor failed while this call was pending; returned evidence was preserved'
            if self._settle_recovered_execution(execution_id, at=timestamp().isoformat(),
                    disposition={'kind': 'engine_error', 'result_ref': reference, 'local_result': local_path}):
                action = execution['action']
                self._remove_action(action)
                if action.get('id') and self.runtime['status'] not in {'closed', 'completed'}:
                    self.runtime.setdefault('waiting_actions', {})[action['id']] = {
                        'action': deepcopy(action), 'kind': 'execution_failure', 'execution_id': execution_id,
                        'reason': execution['error'], 'next_owner': 'operational_review'}
                    from .repair_execution import route_failed_action
                    route_failed_action(self, action, execution_id,
                        reason='Assess the interrupted execution using its preserved result and remaining obligation')
                self._settle_activity(execution_id)
        self._live_execution_ids.clear()
        for execution_id, binding in list(self._transport_bindings.items()):
            self._transport.close(binding, reason='engine shutdown after error')
            self._transport_bindings.pop(execution_id, None)
        self._save(artifacts)

    def _schedule_reconsideration(self, observed_at):
        """Adapt runtime availability to TASKS' active-research query contract.

        Assignment lives in request event_refs. The owner's working event
        annotations are a query projection and never rewrite published facts.
        """
        from .initialization import governance_working_view
        from .planning import schedule_reconsideration
        if self.instance['lifecycle']['state'] != 'active' or self.runtime['status'] in {
                'paused', 'closed', 'completed'}:
            return
        original_events = {e['id']: deepcopy(e) for e in self.runtime.get('events', [])}
        candidate = deepcopy(self.runtime)
        status = candidate['status']
        candidate['status'] = 'active'
        requests = candidate['queue'] + [e.get('action', {}) for e in candidate['executions'].values()
                                       if e.get('status') != 'ended']
        requests += [w['action'] for w in candidate.get('waiting_actions', {}).values() if 'action' in w]
        assigned = {ref: a.get('id') for a in requests for ref in a.get('event_refs', [])}
        for event in candidate.get('events', []):
            event.pop('assigned_to', None)
            event.pop('assigned_at', None)
            if event['id'] in assigned:
                event['assigned_to'] = assigned[event['id']]
        state = schedule_reconsideration(governance_working_view(self.instance), candidate,
            now=observed_at, evaluation_context={**self._evaluation_context(), 'now': observed_at})
        candidate['status'] = status
        for index, event in enumerate(candidate.get('events', [])):
            if event['id'] in original_events:
                candidate['events'][index] = original_events[event['id']]
            else:
                event.pop('assigned_to', None)
                event.pop('assigned_at', None)
        self.runtime = candidate
        return state

    def _failed_live_review(self, action, reason):
        parent = self.runtime["executions"].get(action.get("target"))
        if action.get("live") and parent and parent["status"] != "ended":
            parent["stop_requested"] = "operating_review_unavailable"
            parent["after_stop"] = {"decision": "wait", "reason": reason}


    def _session_resources(self):
        if getattr(self, "_slots", None) is not None:
            return self._slots.snapshot()
        return SessionSlots(self.runtime, self.instance, observer=True).snapshot()

    def _select_model(self, action):
        if action.get("model_selection"):
            return deepcopy(action["model_selection"])
        action = deepcopy(action)
        parent = self.runtime["executions"].get(action.get("target"), {})
        if parent.get("model_selection") and not action.get("model_assessment"):
            chosen = parent["model_selection"]
            action["model_assessment"] = chosen.get("assessment") or {
                "difficulty": chosen["tier"], "importance": chosen["tier"],
                "reason": "Preserve the reviewed execution's model requirement."}
        return selection(self.instance["config"], action, self.runtime["tasks"], self.instance["knowledge"],
                         profiles=self.instance["execution_profiles"])

    def _apply_model_metadata(self, action, output, execution_id):
        extensions = self.runtime["executions"][execution_id].get("extensions", {})
        if action["role"] not in {"research_preparation", "research_plan"}:
            if extensions.get("model_assessments"):
                raise ValueError("only preparation and planning author model assessments")
            return
        identified = validate_assessments(action, output, extensions)
        if preparation_only(action):
            for field in ('assessment_targets', 'observation_rule_targets'):
                for tid, basis in action.get(field, {}).items():
                    task = self.runtime['tasks'].get(tid)
                    if not task or task.get('status') in {'completed', 'closed'} or assessment_basis(task) != basis:
                        raise ValueError(field + ' task edition changed: ' + tid)
                    if any(e.get('status') != 'ended' and e.get('action', {}).get('target') == tid
                           for e in self.runtime['executions'].values()):
                        raise ValueError('preparation target has a live execution: ' + tid)
            from .observations import validate_rule_preparation
            validate_rule_preparation(action, extensions, self.runtime['tasks'])
            self.runtime['executions'][execution_id]['model_decisions'] = identified
            return
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
            if task and action['role'] in {'research_work', 'supplemental_research'}:
                from .execution_profiles import resolve_profile
                current = [resolve_profile(self.instance['execution_profiles'], ref)
                           for ref in self.instance['role_profile_refs'].get(action['role'], [])]
                if current and all(not observation_settings_errors(p) for p in current) and not task.get('academic_requirement_id'):
                    self._enqueue('research_preparation', task['id'],
                        reason='Reprepare the task with valid current observation profiles; preserve its old profile references in revision history')
                continue
            fresh = deepcopy(action)
            for key in ('profile_ref', 'model_selection', 'actor_kind', 'budget_kind', 'dispatch_wait'):
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
                    and entry['action']['role'] in {'research_work', 'supplemental_research'}):
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
        from .planning import _records, _hash
        records = _records(self.instance, self.runtime)
        values = {}
        for ref in {ref for row in deferrals for ref in row['missing_inputs']}:
            if ref == 'user_input':
                values[ref] = [row.get('id') for row in self.runtime['inputs']]
            elif ref in records:
                values[ref] = _hash(records[ref][1])
            else:
                source = next((s for s in self.instance['sources'] if ref in aliases(s)), None)
                values[ref] = source['sha256'] if source else None
        return values

    def _ensure_model_assessments(self):
        """Prepare ratings and academic observation rules before contract review."""
        from .observations import validate_task_rules
        live = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        for tid, task in self.runtime["tasks"].items():
            if (not task.get('academic_requirement_id') or not task.get('revision_requested')
                    or task.get('status') in {'completed', 'closed'}):
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
                   if (task.get("status") in {"planned", "active", "waiting"}) and (not task.get("model_assessment"))}
        missing_rules = {}
        for tid, task in self.runtime['tasks'].items():
            if not task.get('academic_requirement_id') or task.get('status') in {'completed', 'closed'}:
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

    def _apply_queue_plan(self, action, execution_id):
        dispositions = self.runtime["executions"][execution_id].get("extensions", {}).get("queued_requests", [])
        if not dispositions:
            return
        if action["role"] != "research_plan":
            raise ValueError("only research planning reorders queued work")
        _, _, original = self.store.load(self.runtime["executions"][execution_id]["input_snapshot"])
        original_live = {e.get("action", {}).get("id") for e in original["executions"].values() if e["status"] != "ended"}
        allowed = {a["id"] for a in original["queue"] if a.get("id") and a["role"] in WORK_ROLES and a["id"] not in original_live}
        live = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        current = {a.get("id"): a for a in self.runtime["queue"]}
        ordered, seen = [], set()
        for row in dispositions:
            if set(row) != {"request_id", "decision", "reason"} or row["decision"] not in {"keep", "cancel"} or not isinstance(row["reason"], str) or not row["reason"].strip():
                raise ValueError("queued request disposition requires identity, keep/cancel and reason")
            aid = row["request_id"]
            if aid not in allowed or aid in seen:
                raise ValueError("queued request was not in the planning input or is repeated")
            seen.add(aid)
            if aid in live or aid not in current:
                self.runtime["history"].append({"kind": "queue_plan_not_applied", "execution_id": execution_id, **row})
                continue
            request = current[aid]
            if row["decision"] == "cancel":
                self._remove_action(request)
                task = self.runtime["tasks"].get(request.get("target"))
                if task and request["role"] in {"research_work", "supplemental_research"} and not request.get("review_cycle_id") and task["status"] == "active":
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

    def _plan_settle_waits(self, action):
        """Approvals arriving minutes apart are decided by one plan; a slow review delays it only up to the limit."""
        from .governance import timestamp
        limit = self.instance["config"].get("plan_settle_seconds", 300)
        if action.get("requested_by") or action.get("recovery"):
            return False
        if not any(a["role"] == "task_contract_review" for a in self.runtime["queue"]):
            return False
        started = timestamp(action.setdefault("settle_started_at", timestamp().isoformat()))
        if (timestamp() - started).total_seconds() >= limit:
            return False
        action["dispatch_wait"] = {"kind": "plan_settle", "since": action["settle_started_at"], "limit_seconds": limit}
        return True

    def _dispatchable(self, action):
        action.pop("dispatch_wait", None)
        try:
            self._action_lifecycle_gate(action)
        except ValueError as error:
            action["dispatch_wait"] = {"kind": "lifecycle", "reason": str(error)}
            return False
        live = [e for e in self.runtime["executions"].values() if e["status"] != "ended"]
        if any(e.get("action", {}).get("id") == action.get("id") for e in live if action.get("id")):
            return False
        role, target = action["role"], action.get("target")
        if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id"):
            from .planning import task_ready
            task = self.runtime["tasks"].get(target)
            from .initialization import governance_working_view
            evaluation = task_ready(task, governance_working_view(self.instance), self.runtime, action=action,
                evaluation_context={**self._evaluation_context(), "now": self._lifecycle_now().isoformat()}) if task else {
                    "state": "not_ready", "errors": ["task is absent"], "basis": []}
            self._record_readiness(target, evaluation, self._lifecycle_now().isoformat())
            if evaluation["state"] != "ready":
                action["dispatch_wait"] = {"kind": "task_readiness", **evaluation}
                return False
        waits = self._revision_dispatch_waits(action)
        if waits:
            action["dispatch_wait"] = {"kind": "contract_revision", "blockers": waits}
            return False
        if not self._selected_action_current(action, evaluation_context=self._evaluation_context()):
            return False
        if role == "research_plan" and self._plan_settle_waits(action):
            return False
        identity_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis", "review_basis_key", "live")
        if any(all(e.get("action", {}).get(key) == action.get(key) for key in identity_keys) for e in live):
            return False
        if role in {"research_preparation", "research_plan"} and any(e["role"] == role for e in live):
            return False
        if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id") and any(
                e["role"] in {"research_work", "supplemental_research"} and e.get("action", {}).get("target") == target
                and not e.get("action", {}).get("review_cycle_id") for e in live):
            return False
        if role in MACHINE_ROLES:
            if role in {'formal_check', 'trust_check'} and any(e['role'] in {'formal_check', 'trust_check'} for e in live):
                action['dispatch_wait'] = {'kind': 'formal_execution'}
                return False
            from .session_slots import SessionSlots
            profile = self._execution_profile(action)
            admission = SessionSlots(self.runtime, self.instance, observer=True).admission_check(profile)
            if not admission['allowed']:
                action['dispatch_wait'] = admission['wait']
            return admission['allowed']
        if action.get("live") and self.runtime["executions"].get(target, {}).get("status") == "ended":
            self._remove_action(action)
            return False
        chosen = self._select_model(action)
        action["model_selection"] = chosen
        reference = action.get("profile_ref") or chosen.get("execution_profile_ref")
        if reference is None:
            from .execution_profiles import profile_ref
            reference = profile_ref(self._execution_profile(action))
        capability = self._capability_requirements(reference)
        if not capability["satisfied"]:
            action["dispatch_wait"] = {"kind": "capability_evidence", **capability}
            return False
        from .session_slots import SessionSlots
        profile = self._execution_profile(action)
        admission = SessionSlots(self.runtime, self.instance, observer=True).admission_check(profile)
        if not admission['allowed']:
            action['dispatch_wait'] = admission['wait']
        return admission['allowed']

    def _run_parallel(self, *, max_steps=None, watch=False):
        from .repository import new_id
        self._slots = SessionSlots(
                                   runtime=self.runtime, instance=self.instance)
        self._calls = ModelCalls(on_returned=self._local_call_returned)
        steps = 0
        try:
            while True:
                self._controls()
                self._calls.collect()
                self._check_installation()
                if self.runtime.get('maintenance_fence'):
                    if self._calls.futures:
                        time.sleep(.02)
                        continue
                    from .maintenance_gate import settle
                    settle(self.runtime)
                    self._save()
                    break
                limited = self.runtime['status'] == 'paused' and any(
                    self._limited_recovery_allowed(a) for a in self.runtime['queue'])
                stopping = (self.runtime["status"] in {"closed", "completed"}
                            or (self.runtime['status'] == 'paused' and not limited))
                from .repair_execution import pending_installation_repair
                stopping = stopping or pending_installation_repair(self.runtime) is not None
                if stopping:
                    if not self._calls.futures:
                        break
                    time.sleep(.02)
                    continue
                draining = max_steps is not None and steps >= max_steps
                if draining:
                    if not self._calls.futures:
                        break
                self.instance["available_input_refs"] = self._available_inputs()
                self._retry_provider_actions()
                self._refresh_readiness()
                if self.runtime["status"] in {"closed", "completed"} or (self.runtime['status'] == 'paused' and not limited):
                    continue
                if not self.runtime["queue"] and not self._calls.futures:
                    if self.instance["lifecycle"]["state"] == "initializing":
                        self._save()
                        if not watch:
                            break
                        time.sleep(.2)
                        continue
                    # _refresh_readiness already asks TASKS about obligations,
                    # exhaustion and repetition lineage. An empty queue or an
                    # old cycle counter is not authority to generate new work.
                    self.runtime["status"] = "waiting"
                action = next((a for a in list(self.runtime["queue"])
                               if (not draining or a.get("live")) and self._dispatchable(a)), None)
                if action is not None:
                    if action["role"] == "formal_check":
                        self._formal(action)
                    elif self._process_machine_action(action):
                        pass
                    else:
                        generator = self._call_steps(action)
                        try:
                            arguments = next(generator)
                        except StopIteration:
                            pass
                        else:
                            self._calls.start(generator, self.runner, arguments, execution_id=arguments.get('execution_id'))
                    if not action.get("live"):
                        steps += 1
                    continue
                if self._calls.futures:
                    time.sleep(.02)
                    continue
                only_capacity = bool(self.runtime["queue"]) and all(
                    a.get("dispatch_wait", {}).get("kind") in {"capacity", "host_capacity"}
                    for a in self.runtime["queue"])
                if self.runtime['status'] != 'paused':
                    self.runtime["status"] = "capacity_waiting" if only_capacity else "waiting"
                self._save()
                if not watch:
                    break
                time.sleep(.2)
            if self.runtime["status"] not in {"initializing", "paused", "closed", "completed", "waiting", "capacity_waiting"}:
                self.runtime["status"] = "ready"
            if (pending_installation_repair(self.runtime) is not None
                    and self.runtime['status'] not in {'paused', 'closed', 'completed'}):
                self.runtime['status'] = 'waiting'
            self._save()
        except BaseException as error:
            self._calls.close()
            try:
                self._abort_parallel_calls()
            except BaseException as cleanup_error:
                error.add_note('Execution cleanup incomplete; preserved state requires recovery: ' + str(cleanup_error))
            raise
        finally:
            self._calls.close()
            self._calls = None
            self._slots = None
