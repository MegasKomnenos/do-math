"""Connect shared provider admission to preserved research actions."""
from copy import deepcopy
from pathlib import Path

from .provider_wait import provider_for
from .session_slots import SessionSlots


class ProviderEngineMixin:
    def _pause_for_model_policy(self, execution_id, model, result):
        self.runtime["model_policy_violation"] = {"execution_id": execution_id, "assigned_model": model,
                                                   "reported_models": deepcopy(result.get("reported_models"))}
        if self.runtime["status"] not in {"closed", "completed"}:
            self.runtime["status"] = "paused"

    def _release_call_slot(self, execution_id):
        slots = self._provider_slots()
        released = slots.release(execution_id)
        if released and self._slots is None and not getattr(self, "_executor_running", False):
            slots.close()
            self._classic_provider_slots = None
        return released

    def _provider_slots(self):
        if self._slots is not None:
            return self._slots
        if getattr(self, "_classic_provider_slots", None) is None:
            self._classic_provider_slots = SessionSlots(Path(self.instance["workspace"]), self.instance["id"])
        return self._classic_provider_slots

    def _provider_status(self):
        slots = self._slots or getattr(self, "_classic_provider_slots", None)
        if slots is not None:
            return slots.provider_snapshot()
        observer = SessionSlots(Path(self.instance["workspace"]), self.instance["id"], observer=True)
        try:
            return observer.provider_snapshot()
        finally:
            observer.close()

    def _provider_admit(self, action, execution_id, pool, model):
        slots = self._provider_slots()
        admitted = slots.acquire(execution_id, pool, model, provider=provider_for(model),
                                 enforce_capacity=self._session_mode())
        if not admitted:
            action["dispatch_wait"] = {"kind": slots.admission_reason, "provider": provider_for(model)}
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
        if gate["state"] == "waiting":
            self._schedule_provider_wake()
        return gate

    def _schedule_provider_wake(self):
        if not self.instance["config"].get("operator_enabled"):
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
            "generation": gate["generation"], "retry_at": gate.get("retry_at")}
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
