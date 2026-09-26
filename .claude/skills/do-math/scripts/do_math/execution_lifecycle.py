"""Execution state transitions, receipts, and recovery dispositions."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .control_transport import SUBMIT_INTENT

# Acceptance receipt kinds. A control submission's receipt keeps its request
# kind (control_transport.SUBMIT_INTENT); the others name their own receiver.
NATIVE_FINAL_RECEIPT = "native_final"
MACHINE_OUTPUT_RECEIPT = "machine_output"
RECOVERY_REPORT_RECEIPT = "recovery_report"
# Receipts that accept an AI role's sealed submission.
SUBMISSION_RECEIPT_KINDS = frozenset({SUBMIT_INTENT, NATIVE_FINAL_RECEIPT})
EXECUTION_STATUSES = frozenset({"queued", "starting", "running", "stopping", "ended"})
STOP_PHASES = frozenset({"checkpointing", "terminating"})
OUTCOMES = frozenset({"output_accepted", "execution_incomplete", "cancelled", "start_failed"})
_EDGES = {"queued": {"starting", "ended"}, "starting": {"running", "stopping"},
          "running": {"stopping"}, "stopping": {"ended"}, "ended": set()}


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def create_execution(*, execution_id: str, owner_activity_id: str, actor_kind: str,
                     input_manifest: Any, profile_ref: Any, created_at: str,
                     continuation_of: str | None = None,
                     context_origin: list[str] | None = None) -> dict:
    """Create a queued attempt.  Continuation is explicit, never inferred."""
    _nonempty(execution_id, "execution_id")
    _nonempty(owner_activity_id, "owner_activity_id")
    _nonempty(created_at, "created_at")
    if actor_kind not in {"ai", "machine"}:
        raise ValueError("actor_kind must be ai or machine")
    if input_manifest is None or profile_ref is None:
        raise ValueError("input_manifest and profile_ref are required")
    if continuation_of is not None:
        _nonempty(continuation_of, "continuation_of")
        if continuation_of == execution_id:
            raise ValueError("an execution cannot continue itself")
    if context_origin is not None and (not isinstance(context_origin, list) or
                                       any(not isinstance(item, str) or not item for item in context_origin)):
        raise ValueError("context_origin must be a list of execution IDs")
    return {"id": execution_id, "owner_activity_id": owner_activity_id, "actor_kind": actor_kind,
            "input_manifest": deepcopy(input_manifest), "execution_profile_ref": deepcopy(profile_ref),
            "created_at": created_at, "status": "queued", "continuation_of": continuation_of,
            "context_origin": deepcopy(context_origin or [])}


def transition_execution(execution: dict, target: str, *, at: str, reason: str | None = None,
                         stop_phase: str | None = None, outcome: str | None = None,
                         disposition: Any = None) -> dict:
    """Apply one legal transition; terminal outcomes do not encode activity meaning."""
    current = execution.get("status")
    if current not in EXECUTION_STATUSES or target not in EXECUTION_STATUSES:
        raise ValueError("execution status is invalid")
    _nonempty(at, "at")
    if target != current and target not in _EDGES[current]:
        raise ValueError(f"illegal execution transition {current} -> {target}")
    if target == "stopping":
        if stop_phase not in STOP_PHASES:
            raise ValueError("stopping requires checkpointing or terminating")
        previous = execution.get("stop_phase")
        if previous == "terminating" and stop_phase != "terminating":
            raise ValueError("terminating cannot return to checkpointing")
    elif stop_phase is not None:
        raise ValueError("stop_phase exists only while stopping")
    if target == "ended":
        if outcome not in OUTCOMES:
            raise ValueError("ended requires a closed outcome")
        if outcome == "output_accepted" and not execution.get("submission_receipt"):
            raise ValueError("accepted output requires a recorded submission receipt")
        if current == "queued" and outcome not in {"cancelled", "start_failed"}:
            raise ValueError("a queued execution can end only as cancelled or start_failed")
    elif outcome is not None:
        raise ValueError("outcome exists only at ended")
    if target == current and target == "stopping" and execution.get("stop_phase") != stop_phase:
        execution["stop_phase"] = stop_phase
        execution.setdefault("transitions", []).append({"from": current, "to": target, "at": at,
                                                           "reason": reason, "stop_phase": stop_phase})
        return execution
    if target == current:
        return execution
    execution["status"] = target
    execution.setdefault("transitions", []).append({"from": current, "to": target, "at": at,
                                                       "reason": reason, "stop_phase": stop_phase})
    if target == "stopping":
        execution["stop_phase"] = stop_phase
    elif target == "ended":
        execution.pop("stop_phase", None)
        execution.update(ended_at=at, outcome=outcome, result_disposition=deepcopy(disposition))
    return execution


def record_submission_intent(execution: dict, intent: dict, receipt: dict, *, at: str | None = None) -> dict:
    """Stage receipt, termination phase and execution authority in one candidate.

    The central caller saves this candidate and its control receipt in one CAS
    before transport acceptance. Collection of the declared output remains
    possible; the reusable grant is not revoked by this execution-local fact.
    """
    if (not isinstance(intent, dict) or not isinstance(intent.get("candidate_id"), str)
            or not isinstance(intent.get("output_ref"), str)):
        raise ValueError("submission intent requires a centrally sealed candidate")
    if not isinstance(receipt, dict) or receipt.get("kind") not in SUBMISSION_RECEIPT_KINDS or receipt.get("state") != "accepted":
        raise ValueError("submission intent requires an accepted control receipt")
    if receipt.get("execution_id") != execution.get("id"):
        raise ValueError("submission receipt belongs to another execution")
    previous = execution.get("submission_intent")
    if previous is not None:
        if previous == intent and execution.get("submission_receipt") == receipt:
            return execution
        raise ValueError("a different submission intent or receipt was already recorded")
    recovery = (receipt.get('kind') == NATIVE_FINAL_RECEIPT and receipt.get('recovery_request_id')
        and execution.get('status') == 'ended' and execution.get('outcome') == 'execution_incomplete'
        and execution.get('capacity', {}).get('local_termination') == 'confirmed')
    if execution.get("status") != "running" and not recovery:
        raise ValueError("submission intent requires a running execution or explicit terminated recovery")
    at = _nonempty(at or receipt.get("received_at"), "submission receipt time")
    receipt_id = _nonempty(receipt.get("id") or receipt.get("request_id"), "receipt identity")
    candidate = deepcopy(execution)
    candidate["submission_intent"] = deepcopy(intent)
    candidate["submission_receipt"] = deepcopy(receipt)
    if not recovery:
        transition_execution(candidate, "stopping", at=at, reason="submission_intent", stop_phase="terminating")
    candidate["authority_revocation"] = {"scope": "execution_research", "reason": "submission_intent",
                                          "at": at, "receipt_id": receipt_id}
    execution.clear()
    execution.update(candidate)
    return execution


def begin_preparation(execution: dict, *, at: str, stage: str = "context") -> dict:
    """Record the reached preparation stage while this attempt is still queued.

    ENGINE registers and saves the queued record before preparing private input.
    This function does not publish files or infer that any input is complete.
    """
    if execution.get("status") != "queued":
        raise ValueError("input preparation requires a queued execution")
    _nonempty(at, "at")
    _nonempty(stage, "stage")
    previous = execution.get("input_preparation", {})
    execution["input_preparation"] = {"stage": stage, "started_at": previous.get("started_at", at),
                                      "updated_at": at}
    return execution


def end_preparation(execution: dict, *, at: str, stage: str, reason: str, cancelled: bool) -> dict:
    """Preserve failure/interruption facts before private input is discarded."""
    if type(cancelled) is not bool:
        raise ValueError("cancelled must be boolean")
    _nonempty(reason, "reason")
    candidate = deepcopy(execution)
    begin_preparation(candidate, at=at, stage=stage)
    if candidate.get("capacity"):
        raise ValueError("admitted preparation must reconcile reservations and process before ending")
    candidate["input_preparation"].update(finished_at=at, reason=reason)
    transition_execution(candidate, "ended", at=at, reason=reason,
                         outcome="cancelled" if cancelled else "start_failed",
                         disposition={"kind": "input_preparation", "stage": stage, "reason": reason})
    execution.clear()
    execution.update(candidate)
    return execution


def drive_to_termination(execution: dict, *, at: str, reason: str) -> dict:
    """Move a started or checkpointing execution to the terminating barrier.

    Queued, ended and already terminating executions are unchanged.
    """
    if execution.get("status") in {"starting", "running"} or (
            execution.get("status") == "stopping" and execution.get("stop_phase") == "checkpointing"):
        transition_execution(execution, "stopping", at=at, reason=reason, stop_phase="terminating")
    return execution


def release_or_hold(execution: dict, slots, *, at: str) -> bool:
    """Return the execution's local capacity, or hold it at the termination barrier.

    Without confirmed local termination the execution stays stopping and keeps
    its capacity and output for recovery; an error the call already reported is
    kept. The caller preserves outputs and saves.
    """
    if not execution.get("capacity") or slots.release(execution["id"]):
        return True
    transition_execution(execution, "stopping", at=at, stop_phase="terminating",
                         reason="local Job termination remains unconfirmed")
    if not execution.get("error"):
        execution["error"] = "Local Job termination is unconfirmed; capacity and output remain held for recovery."
    return False


def recover_execution(execution: dict, observation: dict, *, at: str) -> dict:
    """Apply only the disposition justified by a recovery observation.

    The caller supplies adapter/Job observations.  This function never probes a
    provider or guesses remote completion.
    """
    if not isinstance(observation, dict):
        raise ValueError("recovery observation must be a dictionary")
    _nonempty(at, "at")
    state = execution.get("status")
    fact = observation.get("fact")
    if state not in EXECUTION_STATUSES:
        raise ValueError("execution status is invalid")
    execution.setdefault("recovery", []).append({"at": at, "observation": deepcopy(observation)})
    if state == "queued" and fact == "no_execution_or_reservation":
        execution["recovery_disposition"] = "retain_for_recheck"
    elif state == "starting" and fact == "start_unknown":
        drive_to_termination(execution, at=at, reason="recovery cannot establish start")
        execution["recovery_disposition"] = "preserve_space_and_reservations"
    elif state == "running" and fact == "previous_engine_lost":
        drive_to_termination(execution, at=at, reason="previous engine lost")
        execution["recovery_disposition"] = "reconcile_local_and_remote"
    elif state == "stopping" and execution.get("stop_phase") == "checkpointing" and fact == "engine_restarted":
        drive_to_termination(execution, at=at, reason="checkpointing cannot continue after recovery")
        execution["recovery_disposition"] = "preserve_received_checkpoint"
    elif state == "stopping" and fact == "termination_barrier_pending":
        execution["recovery_disposition"] = "preserve_space_and_reservations"
    elif state == "stopping" and fact == "termination_barrier_confirmed":
        outcome = observation.get("outcome", "execution_incomplete")
        transition_execution(execution, "ended", at=at, reason="recovery confirmed termination barrier",
                             outcome=outcome, disposition=observation.get("disposition", "preserved_for_followup"))
    elif state == "ended":
        execution["recovery_disposition"] = "continue_non_execution_followup"
    else:
        raise ValueError(f"observation {fact!r} is not valid for {state}")
    return execution
