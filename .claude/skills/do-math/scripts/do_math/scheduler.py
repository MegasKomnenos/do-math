"""Instance scheduler: model calls run concurrently, state transitions run serially.

The owner loop, dispatch judgment and model selection live here; the
preparation and planning outputs are applied by planning_engine.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

from .execution_profiles import LEAN_ROLES, MACHINE_ROLES, PLANNING_ROLES, RESEARCH_PRODUCER_ROLES, task_research
from .git_store import ARTIFACT_ROOT
from .model_policy import selection
from .parallel import ModelCalls, failed_result
from .payloads import json_safe
from .session_slots import SLOT_WAITS, SessionSlots

# Upper bound of an owner wait while calls run, and the idle --watch pause.
# Calls wake the owner at once; this bound only paces file-borne controls,
# transport requests and clock checks. Tunable: stop response is at most one
# pass plus the call's flag check.
OWNER_POLL_SECONDS = 0.25
# Readiness and dispatch are judged again after any published state change
# except an applied observation, and otherwise at most this often. Tunable: a
# transition that only time makes due (a clock condition, grant expiry, plan
# settling, provider retry) or that an observation enqueued waits at most this long.
OWNER_RESCAN_SECONDS = 1.0


class SchedulerMixin:
    def _local_call_returned(self, execution_id, result):
        if execution_id is None:
            return
        execution = self.runtime['executions'][execution_id]
        if execution.get('launch_ticket'):
            from .launch import mark_returned
            mark_returned(execution['launch_ticket'], result)

    def _evaluate_stops(self):
        """Every head movement passes here: judge live calls' stop reasons; flags carry the verdict."""
        calls = self._calls
        if calls is not None:
            calls.judge()

    def _settle_stops(self, *, clock=True):
        """Publish pending owner changes, then compare time-bound stop reasons with the clock."""
        if not self._calls.futures:
            return
        if clock:
            self._check_conversations()
        self._save()  # A publication runs the stop judgments; an unchanged state does not.
        if clock and self._stop_time_due():
            self._calls.judge()

    def _scan_due(self):
        """Publish pending owner changes; True when readiness and dispatch need judging again."""
        self._save()
        instant = time.monotonic()
        if self._scan_head == self.head and instant - self._scan_at < OWNER_RESCAN_SECONDS:
            return False
        self._scan_head, self._scan_at = self.head, instant
        return True

    def _publish_observation(self, artifacts=None):
        """Publish an applied observation; it alone does not make a judged head due again."""
        judged = self._scan_head == self.head
        self._save(artifacts)
        if judged:
            self._scan_head = self.head

    def _goal_basis_key_at_head(self):
        """Stop judgments read published state, so one goal basis serves every judgment at a head."""
        memo = self._goal_basis_memo
        if memo is None or memo[0] != self.head:
            memo = self._goal_basis_memo = (self.head, self._goal_basis_key())
        return memo[1]

    def _stop_time_due(self):
        """True when a time-bound stop reason fell due since the previous owner pass."""
        from .governance import timestamp
        now, instant = self._lifecycle_now(), time.monotonic()
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

    def _run_machine_steps(self, generator, *, calculator=None):
        """Start only the blocking calculation; the owner resumes its continuation when it returns."""
        try:
            execution_id, arguments = next(generator)
        except StopIteration as completed:
            return completed.value
        self._live_execution_ids.add(execution_id)
        self._calls.start_call(generator, calculator or self.formal_verifier, arguments, execution_id=execution_id)
        return False  # The queued request remains owned until completion.

    def _abort_parallel_calls(self):
        """Preserve returned evidence and reconcile confirmed Jobs after owner failure."""
        from .repository import canonical_json, new_id
        from .governance import timestamp
        returned = []
        for future, generator in self._calls.futures.items():
            execution_id = future.execution_id
            try:
                result = future.result()
            except BaseException as error:
                result = failed_result(error)
            if execution_id:
                raw = canonical_json(json_safe(result))
                # This local copy remains available even if publication itself failed.
                path = Path(self.instance['workspace']) / 'execution-recovery' / execution_id / 'returned-result.json'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                returned.append((execution_id, raw, str(path), result))
            generator.close()
        self._reload()
        artifacts = {}
        for execution_id, raw, local_path, result in returned:
            execution = self.runtime['executions'].get(execution_id)
            if not execution or execution['status'] == 'ended':
                continue
            reference = f'{ARTIFACT_ROOT}{new_id("BA")}/interrupted-result.json'
            artifacts[reference] = raw
            execution['result_ref'] = reference
            execution['stop_requested'] = 'engine_error'
            self._local_call_returned(execution_id, result)
            execution['error'] = 'executor failed while this call was pending; returned evidence was preserved'
            if self._settle_recovered_execution(execution_id, at=timestamp().isoformat(),
                    disposition={'kind': 'engine_error', 'result_ref': reference, 'local_result': local_path}):
                action = execution['action']
                self._remove_action(action)
                if action.get('id') and not self._instance_closed():
                    self.runtime.setdefault('waiting_actions', {})[action['id']] = {
                        'action': deepcopy(action), 'kind': 'execution_failure', 'execution_id': execution_id,
                        'reason': execution['error'], 'next_owner': 'operational_review'}
                    self.route_failed_action(action, execution_id,
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
        from .planning import schedule_reconsideration
        if self.instance['lifecycle']['state'] != 'active' or self.runtime['status'] in {
                'paused', 'closed', 'completed'}:
            return
        runtime = self.runtime
        annotations = ('assigned_to', 'assigned_at')
        published = {e['id']: {k: e[k] for k in annotations if k in e} for e in runtime.get('events', [])}
        status = runtime['status']
        runtime['status'] = 'active'
        try:
            requests = runtime['queue'] + [e.get('action', {}) for e in runtime['executions'].values()
                                           if e.get('status') != 'ended']
            requests += [w['action'] for w in runtime.get('waiting_actions', {}).values() if 'action' in w]
            assigned = {ref: a.get('id') for a in requests for ref in a.get('event_refs', [])}
            for event in runtime.get('events', []):
                event.pop('assigned_to', None)
                event.pop('assigned_at', None)
                if event['id'] in assigned:
                    event['assigned_to'] = assigned[event['id']]
            return schedule_reconsideration(self.instance, runtime,
                now=observed_at, evaluation_context={**self._evaluation_context(), 'now': observed_at})
        finally:
            # Only the query's working annotations are undone; its new events and requests stay.
            runtime['status'] = status
            for event in runtime.get('events', []):
                event.pop('assigned_to', None)
                event.pop('assigned_at', None)
                event.update(published.get(event['id'], {}))

    def _failed_live_review(self, action, reason):
        parent = self.runtime["executions"].get(action.get("target"))
        if action.get("live") and parent and parent["status"] != "ended":
            parent["stop_requested"] = "operating_review_unavailable"
            parent["after_stop"] = {"decision": "wait", "reason": reason}


    def _session_resources(self):
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
                         instance=self.instance)

    def _plan_settle_waits(self, action):
        """Approvals arriving minutes apart are decided by one plan; a slow review delays it only up to the limit."""
        from .governance import timestamp
        limit = self.instance["config"]["plan_settle_seconds"]
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
        if task_research(action) and any(
                e["role"] in RESEARCH_PRODUCER_ROLES and e.get("action", {}).get("target") == target
                and not e.get("action", {}).get("review_cycle_id") for e in live):
            return False
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
        admission = SessionSlots(self.runtime, self.instance, observer=True).admission_check(profile)
        if not admission['allowed']:
            action['dispatch_wait'] = admission['wait']
        return admission['allowed']

    def _run_parallel(self, *, max_steps=None, watch=False, until_active=False):
        # Bound before the loop: the maintenance exit leaves the loop before its
        # stopping check, and the settlement after the loop still reads this name.
        from .repair_execution import pending_installation_repair
        self._calls = ModelCalls(on_returned=self._local_call_returned,
                                 on_observation_error=self._observation_failed)
        self._stop_deadlines, self._stop_clock = {}, None
        self._scan_head = None  # Every run judges readiness and dispatch in its first pass.
        steps = 0
        try:
            while True:
                # Calculations only read stop flags, so the owner receives controls and
                # transport requests every pass. Controls enter a published state, and a
                # request received in this pass precedes the clock's stop reasons.
                self._settle_stops(clock=False)
                self._controls()
                self._settle_stops()
                collected = self._calls.collect()
                self._check_installation()
                if self.runtime.get('maintenance_fence'):
                    if self._calls.futures:
                        self._calls.wait(OWNER_POLL_SECONDS)
                        continue
                    from .maintenance_gate import settle
                    settle(self.runtime)
                    self._save()
                    break
                limited = self.runtime['status'] == 'paused' and any(
                    self._limited_recovery_allowed(a) for a in self.runtime['queue'])
                stopping = (self._instance_closed()
                            or (self.runtime['status'] == 'paused' and not limited))
                stopping = stopping or pending_installation_repair(self.runtime) is not None
                if stopping:
                    if not self._calls.futures:
                        break
                    self._calls.wait(OWNER_POLL_SECONDS)
                    continue
                if until_active and self.instance['lifecycle']['state'] == 'active':
                    if self._calls.futures:
                        self._calls.wait(OWNER_POLL_SECONDS)
                        continue
                    break
                draining = max_steps is not None and steps >= max_steps
                if draining:
                    if not self._calls.futures:
                        # A completed local check can unblock a sealed submission.
                        # Give the owner loop one more control/publication pass
                        # before returning from a bounded run.
                        if collected:
                            continue
                        break
                scan = self._scan_due()
                if scan:
                    self._refresh_readiness()
                if self._instance_closed() or (self.runtime['status'] == 'paused' and not limited):
                    continue
                self._resume_environment_waits()
                if not self.runtime["queue"] and not self._calls.futures:
                    if self.instance["lifecycle"]["state"] == "initializing":
                        self._save()
                        if not watch:
                            break
                        time.sleep(OWNER_POLL_SECONDS)
                        continue
                    # _refresh_readiness already asks TASKS about obligations,
                    # exhaustion and repetition lineage. An empty queue or an
                    # old cycle counter is not authority to generate new work.
                    self.runtime["status"] = "waiting"
                action = scan and next((a for a in list(self.runtime["queue"])
                                        if (not draining or a.get("live")) and self._dispatchable(a)), None)
                if action:
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
                            self._calls.start_call(generator, self.runner.run, arguments,
                                                   execution_id=arguments.get('execution_id'))
                    if not action.get("live"):
                        steps += 1
                    continue
                if self._calls.futures:
                    self._calls.wait(OWNER_POLL_SECONDS)
                    continue
                only_capacity = bool(self.runtime["queue"]) and all(
                    a.get("dispatch_wait", {}).get("kind") in SLOT_WAITS
                    for a in self.runtime["queue"])
                if self.runtime['status'] != 'paused':
                    self.runtime["status"] = "capacity_waiting" if only_capacity else "waiting"
                self._save()
                if not watch:
                    break
                time.sleep(OWNER_POLL_SECONDS)
            if self.runtime["status"] not in {"initializing", "paused", "closed", "completed", "waiting", "capacity_waiting"}:
                self.runtime["status"] = "ready"
            if (pending_installation_repair(self.runtime) is not None
                    and self.runtime['status'] != 'paused' and not self._instance_closed()):
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
