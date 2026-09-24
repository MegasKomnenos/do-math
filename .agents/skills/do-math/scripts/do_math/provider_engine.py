"""Connect shared provider admission to preserved research actions."""
from copy import deepcopy
from pathlib import Path
import time

from .provider_wait import provider_for, provider_wait_disposition
from .session_slots import SessionSlots


class ProviderEngineMixin:
    def _pause_for_model_policy(self, execution_id, model, result):
        self.runtime["model_policy_violation"] = {"execution_id": execution_id, "assigned_model": model,
                                                   "reported_models": deepcopy(result.get("reported_models"))}
        if self.runtime["status"] not in {"closed", "completed"}:
            self.runtime["status"] = "paused"

    def _release_call_slot(self, execution_id):
        slots = self._provider_slots()
        return slots.release(execution_id)

    def _settle_recovered_execution(self, execution_id, *, at,
                                    outcome="execution_incomplete", disposition=None):
        """Stage local reservation settlement and execution end for one CAS.

        The caller owns the repository lock and saves this runtime together with
        the recovery disposition. Local Job evidence is independent of remote
        provider termination. Already ended executions may still need settlement.
        """
        from .execution_lifecycle import recover_execution, transition_execution
        execution = self.runtime["executions"][execution_id]
        candidate = deepcopy(execution)
        if candidate["status"] != "ended":
            if candidate["status"] == "queued":
                transition_execution(candidate, "ended", at=at,
                                     outcome="cancelled" if outcome == "cancelled" else "start_failed",
                                     reason="recovery of reserved preparation", disposition=disposition)
            elif candidate["status"] in {"starting", "running"}:
                transition_execution(candidate, "stopping", at=at, stop_phase="terminating",
                                     reason="recovery local termination reconciliation")
            elif candidate["status"] == "stopping" and candidate.get("stop_phase") == "checkpointing":
                recover_execution(candidate, {"fact": "engine_restarted"}, at=at)
            if candidate["status"] != "ended":
                recover_execution(candidate, {"fact": "termination_barrier_confirmed", "outcome": outcome,
                                               "disposition": disposition or "preserved_for_followup"}, at=at)
        if execution.get("capacity"):
            if not self._provider_slots().release(execution_id, reason="recovery local termination confirmed"):
                return False
            candidate["capacity"] = deepcopy(execution["capacity"])
        else:
            identity = execution.get("process") or {}
            if identity.get("job_name"):
                from .windows_job import named_job_empty
                confirmed = named_job_empty(identity["job_name"]) is True
            else:
                confirmed = execution.get("actor_kind") == "machine" and execution.get("local_termination_observed") is True
            if not confirmed:
                return False
        execution.clear()
        execution.update(candidate)
        return True

    def _provider_slots(self):
        if self._slots is not None and (not hasattr(self._slots, "runtime") or
                self._slots.runtime is self.runtime and self._slots.instance is self.instance):
            return self._slots
        if not {"execution_profiles", "capacity_constraints"}.issubset(self.instance):
            raise ValueError("provider admission requires feature-5 execution profiles")
        # Passing runtime and instance selects SessionSlots.  Do not retain a
        # SQLite fallback: ENGINE holds the writer lock and publishes this same
        # candidate runtime before a worker resumes.
        self._slots = SessionSlots(
                                   runtime=self.runtime, instance=self.instance)
        return self._slots

    def _provider_status(self):
        slots = self._slots
        if slots is not None:
            return slots.provider_snapshot()
        if not {"execution_profiles", "capacity_constraints"}.issubset(self.instance):
            return {"source": "uninitialized_feature_5_runtime", "providers": {}}
        return SessionSlots(self.runtime, self.instance, observer=True).provider_snapshot()

    def _provider_admit(self, action, execution_id, pool, model, *, profile, execution):
        """Reserve a feature-5 profile and its starting execution together.

        ENGINE must save the candidate runtime through its single CAS before the
        corresponding runner starts.  This method deliberately has no legacy
        model-only or SQLite admission path.
        """
        slots = self._provider_slots()
        admitted = slots.acquire(execution_id, pool, model, profile=profile, execution=execution,
                                 provider=provider_for(model))
        if not admitted:
            action['dispatch_wait'] = deepcopy(slots.admission_wait)
            if slots.admission_reason == 'provider_limit':
                action['dispatch_wait']['activity_wait'] = provider_wait_disposition(
                    model=model, attempts=1, current=time.time(),
                    failure={'retry_at': action['dispatch_wait'].get('retry_at')},
                    initial=self.instance['config']['provider_retry_initial_seconds'],
                    maximum=self.instance['config']['provider_retry_max_seconds'])
        else:
            action.pop("dispatch_wait", None)
        return admitted

    def _provider_outcome(self, execution_id, model, result):
        slots = self._provider_slots()
        parsed = result.get("execution", {}).get("collect", {}).get("jsonl", {})
        config = self.instance["config"]
        gate = slots.provider_result(execution_id, provider_for(model),
            failure=result.get("failure") if result.get("error_kind") == "provider_limit" else None,
            response_observed=result.get("status") == "completed" or bool(parsed.get("turn_failed") or parsed.get("turn_completed")),
            initial_seconds=config["provider_retry_initial_seconds"], maximum_seconds=config["provider_retry_max_seconds"])
        return gate

    def _publish_provider_result(self, artifacts=None):
        """Publish result disposition before the scheduler re-reads its Git ledger."""
        self._save(artifacts)
        previous = deepcopy(self.runtime.get('provider_wake'))
        self._schedule_provider_wake()
        if self.runtime.get('provider_wake') != previous:
            self._save()

    def _schedule_provider_wake(self):
        if not self.instance["config"].get("operator_enabled") and not self.runtime.get('provider_wake'):
            return
        from .scheduled_operator import reconcile_wake
        try:
            result = reconcile_wake(self.store._store.repository, self.instance["id"], Path(self.instance["workspace"]),
                                    config=self.instance["config"], status={"user_pause": self.runtime.get("user_pause"),
                                    "status": self.runtime["status"]})
        except Exception as error:
            result = {"status": "failed", "error": str(error)}
        self.runtime["provider_wake"] = result

    def _hold_provider_action(self, action, execution_id, gate, reason):
        self._remove_action(action)
        self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
            "action": deepcopy(action), "kind": "execution_failure", "failure_kind": "provider_limit",
            "reason": reason, "execution_id": execution_id, "provider": gate["provider"],
            "generation": gate["generation"], "retry_at": gate.get("retry_at"),
            "activity_wait": provider_wait_disposition(
                model=action["model_selection"]["model"],
                provider=gate["provider"], attempts=max(1, int(gate.get("attempts", 1))),
                current=time.time(), failure={"retry_at": gate.get("retry_at")},
                initial=self.instance["config"]["provider_retry_initial_seconds"],
                maximum=self.instance["config"]["provider_retry_max_seconds"])}
        if self.runtime["status"] not in {"paused", "closed", "completed"}:
            self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"

    def _retry_provider_actions(self):
        if self.runtime["status"] in {"paused", "closed", "completed"} or self.runtime.get("user_pause"):
            return
        pending = [entry for entry in self.runtime.get("waiting_actions", {}).values()
                   if entry.get("failure_kind") == "provider_limit"]
        if not pending:
            return
        providers = self._provider_status()["providers"]
        queued = {action.get("id") for action in self.runtime["queue"]}
        for entry in pending:
            action = entry["action"]
            gate = providers.get(entry["provider"], {"state": "available"})
            if action.get("id") in queued or not (gate["state"] == "available" or gate.get("due")):
                continue
            if self._obsolete_action_reason(action):
                continue
            restored = {**deepcopy(action), "recovery": {"execution_id": entry["execution_id"],
                        "reason": "provider admission retry", "provider_generation": gate.get("generation")}}
            self.runtime["queue"].append(restored)
            queued.add(action.get("id"))
            self.runtime["status"] = "ready"
