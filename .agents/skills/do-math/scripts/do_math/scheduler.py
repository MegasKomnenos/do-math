"""Instance scheduler: model calls run concurrently, state transitions run serially (layer 3).

The owner loop lives here: it orders controls, stop settlement, collection and
dispatch, waits, and routes each dispatched action to its executor. Its
judgments (dispatch, model selection, stopping and status) are
``dispatch_engine``; the preparation and planning outputs are applied by
planning_engine.
"""
from __future__ import annotations


from pathlib import Path

from .parallel import failed_result
from .payloads import json_safe

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
    def _schedule_provider_wake(self):
        """Register or cancel the operator's one-shot wake for the earliest provider wait (layer 3 wiring)."""
        from .scheduled_operator import reconcile_wake
        from .supervision import supervision_facts
        facts = supervision_facts(self.instance, self.runtime)
        if not facts["operator_enabled"] and not self.runtime.get('provider_wake'):
            return
        try:
            result = reconcile_wake(self.store.repository, self.instance["id"], Path(self.instance["workspace"]),
                                    facts=facts, providers=self._provider_status()["providers"],
                                    scheduler=self.ports.scheduler, clock=self.ports.clock)
            result.pop("observed", None)
        except Exception as error:
            result = {"status": "failed", "error": str(error)}
        self.runtime["provider_wake"] = result

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
        instant = self.ports.clock.monotonic()
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
        from .canonical import canonical_json
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
        artifacts = self._record_interrupted_calls(returned)
        self._live_execution_ids.clear()
        for execution_id, binding in list(self._transport_bindings.items()):
            self._transport.close(binding, reason='engine shutdown after error')
            self._transport_bindings.pop(execution_id, None)
        self._save(artifacts)

    def _run_parallel(self, *, max_steps=None, watch=False, until_active=False):
        self._calls = self.ports.calls.new(on_returned=self._local_call_returned,
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
                    settle(self.runtime, clock=self.ports.clock)
                    self._save()
                    break
                limited, stopping = self._owner_stopping()
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
                self._resume_formal_waits()
                if not self.runtime["queue"] and not self._calls.futures:
                    if self.instance["lifecycle"]["state"] == "initializing":
                        self._save()
                        if not watch:
                            break
                        self.ports.clock.sleep(OWNER_POLL_SECONDS)
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
                self._idle_wait_status()
                self._save()
                if not watch:
                    break
                self.ports.clock.sleep(OWNER_POLL_SECONDS)
            self._settled_run_status()
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
