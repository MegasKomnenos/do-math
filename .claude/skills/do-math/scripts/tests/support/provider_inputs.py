"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
import platform
from do_math import activities, execution_lifecycle as lifecycle, execution_profiles as profiles, model_policy
from do_math.execution_profiles import profile_ref
from do_math.lean_evidence import portable_bin
from do_math.formal import toolchain_root


def claude_stream(*events):
    return b"".join(json.dumps(event).encode() + b"\n" for event in events)


from support.provider_runs import CLAUDE_INIT


CLAUDE_RESULT = {"type": "result", "subtype": "success", "is_error": False,
                 "session_id": "session-one", "structured_output": {"ok": True},
                 "usage": {"input_tokens": 7, "output_tokens": 3}}


PROVIDER_MODEL = "claude-opus-5"


PROVIDER_LIMIT_FAILURE = {"kind": "provider_limit", "provider": "claude", "retry_at": None,
                          "evidence_ref": "synthetic-provider-limit.json", "limit_windows": []}


def instant(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def admit(slots, instance, runtime, identifier, role="research_work", current=100):
    """Admit a work role (a model slot) or an operational role such as maintenance (no slot)."""
    reference = instance["role_profile_refs"][role][-1]
    profile = instance["execution_profiles"][reference["id"]]
    aid = "AY-" + identifier
    execution = lifecycle.create_execution(execution_id=identifier, owner_activity_id=aid,
        actor_kind="ai", input_manifest=[], profile_ref=profile_ref(profile), created_at=instant(current))
    execution["role"] = role
    if not slots.acquire(identifier, profile=profile, execution=execution, current_time=current):
        return False
    activities.open_activity(runtime, activity_id=aid, activity_kind=role,
        owner_ref=instance["id"], input_refs=[], opened_at=instant(current))
    activities.assign_execution(runtime, aid, execution)
    return True


def report(slots, instance, identifier, current, failure=None, **config):
    """Apply a synthetic runner result: a provider_limit failure, or a completed call."""
    result = ({"status": "failed", "error_kind": "provider_limit", "failure": failure}
              if failure is not None else {"status": "completed"})
    return slots.provider_result_from_run(identifier, result, {**instance["config"], **config},
                                          current_time=current)


def finish(slots, runtime, identifier, current, *, close_activity=True):
    if not slots.release(identifier):
        raise AssertionError("test execution without an acknowledged process did not settle")
    execution = runtime["executions"][identifier]
    lifecycle.transition_execution(execution, "stopping", at=instant(current))
    lifecycle.transition_execution(execution, "ended", at=instant(current), outcome="start_failed",
        disposition={"kind": "synthetic_provider_observation"})
    if not close_activity:
        return
    activities.finish_activity(runtime, execution["owner_activity_id"], result_refs=[],
        unresolved=[{"reason": "No model process was started in this allocator fixture"}],
        followups=[], at=instant(current))


PROFILE_CONFIG = {
    "tier_models": dict(model_policy.MODELS), "role_tiers": dict(model_policy.ROLE_TIERS),
    "session_limits": deepcopy(model_policy.LIMITS), "effort": "medium",
    "max_input_bytes": 500000, "call_timeout_seconds": 600,
    "operator_timeout_seconds": 5400, "operator_effort": "high",
    "observation_mode": "event_driven", "observation_interval_seconds": 300,
    "finish_notice_seconds": 60,
    "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False,
    "provider_retry_initial_seconds": 300, "provider_retry_max_seconds": 7200,
}


def host_capacity_fixture():
    """``(instance, selected, constraint)``: ``PROFILE_CONFIG`` profiles under an approved host constraint.

    ``selected`` maps research_work, recovery and formal_check to a profile
    that reserves one job, 128 MiB and 20% CPU of ``constraint``.
    """
    from support.entry import entry
    _entry = entry()
    from do_math.governance import preserve_source
    instance = profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
    source = preserve_source("GS-host-test", "Temporary test approval only: jobs 4, commit bytes 536870912, CPU basis points 8000; control reserve jobs 1, commit bytes 134217728, CPU basis points 2000.", origin="user")
    instance["governance_sources"] = {source["id"]: source}
    constraint = profiles.host_constraint(host_id=_entry.host_id,
        limits={"jobs": 4, "memory_bytes": 512 * 1024**2, "cpu_rate_basis_points": 8000},
        control_reserve={"jobs": 1, "memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 2000},
        authority_refs=[source["id"]])
    instance["capacity_constraints"][constraint["id"]] = constraint
    instance["host_capacity_ref"] = constraint["id"]
    selected = {}
    for role in ("research_work", "recovery", "formal_check"):
        original = next(p for p in instance["execution_profiles"].values() if p["role"] == role)
        profile = profiles.with_host_resources(original, constraint,
            {"jobs": 1, "memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 2000})
        instance["execution_profiles"][profile["id"]] = profile
        selected[role] = profile
    return instance, selected, constraint


def actual_command():
    # Explicit portable compiler coverage; Mathlib readiness is checked separately.
    return [os.environ.get('DO_MATH_KNOWLEDGE_TEST_LEAN', str(portable_bin(toolchain_root()) / 'lean.exe'))]
