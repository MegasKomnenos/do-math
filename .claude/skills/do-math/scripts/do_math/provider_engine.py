"""Connect shared provider admission to preserved research actions."""
from copy import deepcopy

from .planning import instance_ended
from .session_slots import SessionSlots


def record_model_policy_violation(instance, runtime, execution_id, model, result):
    """Pause on a reported model other than the assigned one; the user decides the next step."""
    runtime["model_policy_violation"] = {"execution_id": execution_id, "assigned_model": model,
                                         "reported_models": deepcopy(result.get("reported_models"))}
    if not instance_ended(instance, runtime):
        runtime["status"] = "paused"


class ProviderEngineMixin:
    def _session_slots(self):
        """A fresh ledger view over the engine's current state; it holds no state of its own."""
        return SessionSlots(self.runtime, self.instance, clock=self.ports.clock, jobs=self.ports.jobs, host_id=self.host_id)

    def _settle_recovered_execution(self, execution_id, *, at, disposition=None):
        """Stage local reservation settlement and execution end for one CAS.

        The caller owns the repository lock and saves this runtime together with
        the recovery disposition. Local Job evidence is independent of remote
        provider termination. Already ended executions may still need settlement.
        Only an admitted execution has a launch barrier whose end can be confirmed.
        """
        from .execution_lifecycle import end_recovered
        execution = self.runtime["executions"][execution_id]
        if not execution.get("capacity"):
            return False
        candidate = deepcopy(execution)
        if candidate["status"] != "ended":
            end_recovered(candidate, at=at, outcome="execution_incomplete",
                          disposition=disposition or "preserved_for_followup")
        if not self._session_slots().release(execution_id, reason="recovery local termination confirmed"):
            return False
        candidate["capacity"] = deepcopy(execution["capacity"])
        execution.clear()
        execution.update(candidate)
        return True

    def _provider_status(self):
        return SessionSlots(self.runtime, self.instance, observer=True, clock=self.ports.clock, jobs=self.ports.jobs, host_id=self.host_id).provider_snapshot()

    def _provider_admit(self, action, execution_id, *, profile, execution):
        """Reserve a registered profile's capacity and its starting execution together.

        ENGINE must save the candidate runtime through its single CAS before the
        corresponding runner starts.
        """
        slots = self._session_slots()
        admitted = slots.acquire(execution_id, profile=profile, execution=execution)
        if not admitted:
            action['dispatch_wait'] = deepcopy(slots.admission_wait)
        else:
            action.pop("dispatch_wait", None)
        return admitted

    def _provider_outcome(self, execution_id, result):
        return self._session_slots().provider_result_from_run(execution_id, result, self.instance["config"])

    def _publish_provider_result(self, artifacts=None):
        """Publish result disposition before the scheduler re-reads its Git ledger."""
        self._save(artifacts)
        previous = deepcopy(self.runtime.get('provider_wake'))
        self._schedule_provider_wake()
        if self.runtime.get('provider_wake') != previous:
            self._save()

    def _requeue_provider_action(self, action, execution_id, gate):
        """A provider-limited request waits in the queue for its gate, like any admission wait."""
        from .activities import wait_for
        from .execution_profiles import match_profile_ref
        self._remove_action(action)
        restored = {**deepcopy(action), "recovery": {"execution_id": execution_id,
                    "reason": "provider admission retry", "provider_generation": gate.get("generation")}}
        profile = match_profile_ref(self.instance["execution_profiles"], action["profile_ref"])
        wait = SessionSlots(self.runtime, self.instance, observer=True, clock=self.ports.clock, jobs=self.ports.jobs, host_id=self.host_id).provider_wait(profile)
        if wait is not None:
            restored["dispatch_wait"] = wait
            activity_id = self.runtime["executions"][execution_id]["owner_activity_id"]
            wait_for(self.runtime, activity_id, reason="provider admission deferred",
                     condition=deepcopy(wait), next_owner=wait["next_owner"],
                     at=self._lifecycle_now().isoformat())
        self.runtime["queue"].append(restored)
        if self.runtime["status"] != "paused" and not self._instance_closed():
            self.runtime["status"] = "ready"
