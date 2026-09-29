"""Doubles at the provider, host-process and external-service boundaries.

Nothing here starts a model, a Lean compiler or a network service of its own.
Each double stands where the product reaches something outside the process:

- Model runner: ``Adapter`` is a scripted provider collector for a real
  ``ModelRunner`` (``runner_with``); ``mock_adapter`` is a bare Mock with the
  provider's real worker options. ``Job`` and ``Execution`` are the process
  handles ``Adapter.start`` returns. ``FakeJob`` answers ``inspect`` with a
  fixed ``JobInspection``.
- Claude stream: ``claude_stream(*events)`` encodes JSONL rows;
  ``CLAUDE_INIT`` and ``CLAUDE_RESULT`` are the first and last rows of a
  successful run.
- Provider limits over session slots: ``provider_repository(root)`` initializes
  one ready instance in the Git repository at ``root`` whose three tiers all use
  ``PROVIDER_MODEL`` (three work slots). ``admit`` registers and admits one
  execution, ``report`` applies a synthetic runner result (a
  ``PROVIDER_LIMIT_FAILURE`` or a completed call), ``finish`` releases and ends
  it, and ``transact`` runs one such operation under the writer lock and saves.
  ``instant`` turns epoch seconds into the ISO time the records use.
- Execution profiles: ``PROFILE_CONFIG`` is a complete profile configuration
  for ``build_profiles``; ``host_capacity_fixture()`` adds an approved host
  constraint and host-bounded work, recovery and formal-check profiles.
- Lean: ``actual_command()`` is the installed compiler command
  (``DO_MATH_KNOWLEDGE_TEST_LEAN`` overrides it); only ``lean``-labelled tests call it.
- HTTP: ``HTTPFixtureHandler`` answers POST with 201 and GET with a redirect.
"""
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
import json
import os
import platform

import do_math.model_runner as runner
from do_math import activities, execution_lifecycle as lifecycle, execution_profiles as profiles, model_policy
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.lean_evidence import portable_bin
from do_math.formal import toolchain_root
from do_math.repository import ResearchRepository
from do_math.system_clock import new_id
from do_math.session_slots import SessionSlots


class Job:
    pid = 7
    creation_filetime = 9

    def terminate(self): self.terminated = True

    def close(self): self.closed = True


class Execution:
    job = Job()
    request_sha256 = "a"


class Adapter:
    """A scripted collector; the worker request fields are its provider's real ones."""
    def __init__(self, result, provider='codex'):
        self.result = result; self.done = False; self.stopped = False
        from do_math.claude_adapter import provider_adapter
        self.worker_options = provider_adapter(provider, 'fake').worker_options

    def start(self, *a, **k):
        self.request = json.loads(a[0].read_text(encoding='utf-8'))
        return Execution()

    def resume(self, *a): self.resumed = True

    def wait_for_termination(self, *a): self.done = True; return True

    def stop(self, *a): self.stopped = True

    def collect(self, *a):
        # A real collector reports provider facts in every result; derive them like it does.
        from do_math.codex_adapter import _provider_observation
        return {'provider_observation': _provider_observation(self.request, self.result.get('jsonl', {}), None), **self.result}

    def provider_failure(self, parsed): return None


def mock_adapter(provider='codex'):
    """A Mock adapter whose worker request fields are its provider's real ones."""
    from unittest.mock import Mock
    from do_math.claude_adapter import provider_adapter
    return Mock(worker_options=provider_adapter(provider, 'fake').worker_options)


def runner_with(adapter, provider='codex'):
    """A ModelRunner that starts ``adapter`` for ``provider``'s models."""
    r = runner.ModelRunner(); r.adapters[provider] = adapter
    return r


class FakeJob:
    """A job whose ``inspect`` reports ``state``."""
    def __init__(self, state): self.state = state

    def inspect(self): return self.state


def claude_stream(*events):
    return b"".join(json.dumps(event).encode() + b"\n" for event in events)


CLAUDE_INIT = {"type": "system", "subtype": "init", "session_id": "session-one"}
CLAUDE_RESULT = {"type": "result", "subtype": "success", "is_error": False,
                 "session_id": "session-one", "structured_output": {"ok": True},
                 "usage": {"input_tokens": 7, "output_tokens": 3}}


PROVIDER_MODEL = "claude-opus-5"
PROVIDER_LIMIT_FAILURE = {"kind": "provider_limit", "provider": "claude", "retry_at": None,
                          "evidence_ref": "synthetic-provider-limit.json", "limit_windows": []}


def instant(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def provider_repository(root):
    """Initialize one ready instance in the Git repository at ``root``; returns its ``ResearchRepository``."""
    from research_fixtures import current_state
    iid = new_id("RI")
    config = {**deepcopy(DEFAULT_CONFIG), "scholarly_enabled": False,
              "tier_models": {tier: PROVIDER_MODEL for tier in ("low", "medium", "high")},
              "session_limits": {"work": {PROVIDER_MODEL: 3}}}
    instance, runtime = current_state(
        {"id": iid, "workspace": str(root), "config": config, **build_profiles(config)},
        {"status": "ready", "executions": {}, "activities": {}, "reservations": {}, "provider_waits": {}})
    repository = ResearchRepository(root, iid)
    repository.initialize(instance, runtime)
    return repository


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


def transact(repository, operation):
    with repository.writer_lock():
        head, instance, runtime = repository.load()
        slots = SessionSlots(runtime, instance)
        result = operation(slots, instance, runtime)
        repository.save_with_state(head, instance, runtime)[0]
        return result


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
    from do_math.governance import preserve_source
    instance = profiles.build_profiles(PROFILE_CONFIG)
    source = preserve_source("GS-host-test", "Temporary test approval only: jobs 4, commit bytes 536870912, CPU basis points 8000; control reserve jobs 1, commit bytes 134217728, CPU basis points 2000.", origin="user")
    instance["governance_sources"] = {source["id"]: source}
    constraint = profiles.host_constraint(host_id=platform.node(),
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


class HTTPFixtureHandler(BaseHTTPRequestHandler):
    """POST answers 201 ``ok``; GET redirects to another origin."""
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', '0'))); body = b'ok'
        self.send_response(201); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        self.send_response(302); self.send_header('Location', 'http://evil/'); self.send_header('Content-Length', '0'); self.end_headers()

    def log_message(self, *a): pass
