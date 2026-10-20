"""Dispatch judgment (layer 2).

Whether a queued action may start and the model it runs, the owner's stop and
status judgments, and the dispositions of calls interrupted by an owner
failure. The owner loop that acts on them is ``scheduler`` (layer 3).
"""
from __future__ import annotations

from .wait_rules import waiting_action
from copy import deepcopy
from .execution_profiles import LEAN_ROLES, MACHINE_ROLES, PLANNING_ROLES, task_research
from .state_contract import ARTIFACT_ROOT
from .model_policy import selection
from .wait_rules import SLOT_WAITS
from .session_slots import SessionSlots


class DispatchEngineMixin:
    def _local_call_returned(self, execution_id, result):
        if execution_id is None:
            return
        execution = self.runtime['executions'][execution_id]
        if execution.get('launch_ticket'):
            from .launch import mark_returned
            mark_returned(execution['launch_ticket'], result)

    def _goal_basis_key_at_head(self):
        """Stop judgments read published state, so one goal basis serves every judgment at a head."""
        memo = self._goal_basis_memo
        if memo is None or memo[0] != self.head:
            memo = self._goal_basis_memo = (self.head, self._goal_basis_key())
        return memo[1]

    def _stop_time_due(self):
        """True when a time-bound stop reason fell due since the previous owner pass."""
        from .governance import timestamp
        now, instant = self._lifecycle_now(), self.ports.clock.monotonic()
        since, self._stop_clock = self._stop_clock, (now, instant)
        if since is None or not self._clock_guard()['usable']:
            return True
        expiries = [grant['expires_at'] for grant in self.instance.get('grants', {}).values()
                    if grant.get('status') == 'active' and grant.get('expires_at')]
        expiries += [execution['action']['repair']['limited_recovery']['expires_at']
                     for execution in self.runtime['executions'].values()
                     if execution.get('status') != 'ended'
                     and execution.get('action', {}).get('repair', {}).get('limited_recovery', {}).get('expires_at')]
        if any(since[0] < timestamp(at) <= now for at in expiries):
            return True
        return any(since[1] < at <= instant
                   for deadlines in self._stop_deadlines.values() for at in deadlines)

    def _observation_failed(self, execution_id, error):
        """An unapplied observation stops its execution; the error is its recorded stop reason."""
        execution = self.runtime['executions'][execution_id]
        execution.setdefault('stop_requested', f'observation_failed: {type(error).__name__}: {error}')
        self._save()

    def _record_interrupted_calls(self, returned):
        """Dispositions of calls pending when the owner failed; returns the artifacts preserving their results."""
        artifacts = {}
        for execution_id, raw, local_path, result in returned:
            execution = self.runtime['executions'].get(execution_id)
            if not execution or execution['status'] == 'ended':
                continue
            reference = f'{ARTIFACT_ROOT}{self.ports.clock.new_id("BA")}/interrupted-result.json'
            artifacts[reference] = raw
            execution['result_ref'] = reference
            execution['stop_requested'] = 'engine_error'
            self._local_call_returned(execution_id, result)
            execution['error'] = 'executor failed while this call was pending; returned evidence was preserved'
            if self._settle_recovered_execution(execution_id, at=self.ports.clock.now(),
                    disposition={'kind': 'engine_error', 'result_ref': reference, 'local_result': local_path}):
                action = execution['action']
                self._remove_action(action)
                if action.get('id') and not self._instance_closed():
                    self.runtime.setdefault('waiting_actions', {})[action['id']] = waiting_action({
                        'action': deepcopy(action), 'kind': 'execution_failure', 'execution_id': execution_id,
                        'reason': execution['error'], 'next_owner': 'operational_review'})
                    self.route_failed_action(action, execution_id,
                        reason='Assess the interrupted execution using its preserved result and remaining obligation')
                self._settle_activity(execution_id)
        return artifacts

    def _schedule_reconsideration(self, observed_at):
        """Adapt runtime availability to TASKS' active-research query contract.

        Assignment lives in request event_refs (planning.assigned_event_refs), which
        the query reads directly; published events are never annotated.
        """
        from .planning import schedule_reconsideration
        if (self.instance['lifecycle']['state'] != 'active' or self.runtime['status'] == 'paused'
                or self._instance_closed()):
            return
        runtime = self.runtime
        status = runtime['status']
        runtime['status'] = 'active'
        try:
            return schedule_reconsideration(self.instance, runtime,
                now=observed_at, evaluation_context={**self._evaluation_context(), 'now': observed_at}, clock=self.ports.clock)
        finally:
            # Only the query's status view is undone; its new events and requests stay.
            runtime['status'] = status

    def _failed_live_review(self, action, reason):
        parent = self.runtime["executions"].get(action.get("target"))
        if action.get("live") and parent and parent["status"] != "ended":
            parent["stop_requested"] = "operating_review_unavailable"
            parent["after_stop"] = {"decision": "wait", "reason": reason}

    def _session_resources(self):
        return SessionSlots(self.runtime, self.instance, observer=True, clock=self.ports.clock, jobs=self.ports.jobs, host_id=self.host_id).snapshot()

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
                         instance=self.instance)

    def _plan_settle_waits(self, action):
        """Approvals arriving minutes apart are decided by one plan; a slow review delays it only up to the limit."""
        from .governance import timestamp
        limit = self.instance["config"]["plan_settle_seconds"]
        # Only a plan a user or operator control requested starts at once; a plan an
        # execution requested (task_scope's continuation plan) settles like the others.
        if action.get("requested_by") in self.runtime["processed_controls"] or action.get("recovery"):
            return False
        if not any(a["role"] == "task_contract_review" for a in self.runtime["queue"]):
            return False
        started = timestamp(action.setdefault("settle_started_at", self.ports.clock.now()))
        if (self.ports.clock.wall() - started).total_seconds() >= limit:
            return False
        action["dispatch_wait"] = {"kind": "plan_settle", "since": action["settle_started_at"], "limit_seconds": limit}
        return True

    def _dispatchable(self, action):
        authored = {key: deepcopy(action[key]) for key in ('grant_id', 'profile_ref') if key in action}
        admitted = False
        try:
            admitted = self._dispatch_candidate(action)
            return admitted
        finally:
            if not admitted:
                # A scan's derived selection is not an authored authority binding.
                # Keep model/wait diagnostics while leaving an unstarted request mergeable.
                for key in ('grant_id', 'profile_ref'):
                    if key in authored:
                        action[key] = authored[key]
                    else:
                        action.pop(key, None)

    def _dispatch_candidate(self, action):
        action.pop("dispatch_wait", None)
        try:
            profile = self._action_lifecycle_gate(action)
        except ValueError as error:
            action["dispatch_wait"] = {"kind": "lifecycle", "reason": str(error)}
            return False
        live = [e for e in self.runtime["executions"].values() if e["status"] != "ended"]
        if any(e.get("action", {}).get("id") == action.get("id") for e in live if action.get("id")):
            return False
        role, target = action["role"], action.get("target")
        if task_research(action):
            from .planning import task_ready
            task = self.runtime["tasks"].get(target)
            evaluation = task_ready(task, self.instance, self.runtime, action=action,
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
        if role in PLANNING_ROLES and any(e["role"] == role for e in live):
            return False
        # task_ready above already refuses every other live execution on this task.
        if role in MACHINE_ROLES:
            if role in LEAN_ROLES and any(e['role'] in LEAN_ROLES for e in live):
                action['dispatch_wait'] = {'kind': 'formal_execution'}
                return False
            return self._admissible(action, profile)
        if action.get("live") and self.runtime["executions"].get(target, {}).get("status") == "ended":
            self._remove_action(action)
            return False
        capability = self._capability_requirements(action["profile_ref"])
        if not capability["satisfied"]:
            action["dispatch_wait"] = {"kind": "capability_evidence", **capability}
            return False
        return self._admissible(action, profile)

    def _admissible(self, action, profile):
        """Check admission without reserving; a refusal records its wait on the request."""
        admission = SessionSlots(self.runtime, self.instance, observer=True, clock=self.ports.clock, jobs=self.ports.jobs, host_id=self.host_id).admission_check(profile)
        if not admission['allowed']:
            action['dispatch_wait'] = admission['wait']
        return admission['allowed']

    def _owner_stopping(self):
        """``(limited, stopping)`` for one owner pass: whether a pause still admits limited recoveries, and
        whether dispatch stops (closure, a pause, a pending installation repair or an unended recovery)."""
        from .repair_execution import pending_installation_repair
        limited = self.runtime['status'] == 'paused' and any(
            self._limited_recovery_allowed(a) for a in self.runtime['queue'])
        stopping = (self._instance_closed()
                    or (self.runtime['status'] == 'paused' and not limited))
        stopping = stopping or pending_installation_repair(self.runtime) is not None
        # An installation recovery the restart recovery could not end has no confirmed
        # local termination; its repair AI may still be changing the installation.
        stopping = stopping or any(row.get('role') == 'recovery' and row.get('status') != 'ended'
                                   for row in self.runtime.get('executions', {}).values())
        return limited, stopping

    def _idle_wait_status(self):
        """Nothing dispatchable and nothing running: capacity_waiting when only slot waits remain, else waiting."""
        only_capacity = bool(self.runtime["queue"]) and all(
            a.get("dispatch_wait", {}).get("kind") in SLOT_WAITS
            for a in self.runtime["queue"])
        if self.runtime['status'] != 'paused':
            self.runtime["status"] = "capacity_waiting" if only_capacity else "waiting"

    def _settled_run_status(self):
        """The status a finished run leaves: ready unless it waits, and waiting while an installation repair is pending."""
        from .repair_execution import pending_installation_repair
        if not self._instance_closed() and self.runtime["status"] not in {"initializing", "paused", "waiting", "capacity_waiting"}:
            self.runtime["status"] = "ready"
        if (pending_installation_repair(self.runtime) is not None
                and self.runtime['status'] != 'paused' and not self._instance_closed()):
            self.runtime['status'] = 'waiting'
