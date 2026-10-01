"""What one model call may run with and what its evidence means (layer 2).

``model_runner`` launches the worker's Job, observes its stream and collects
its files, and ``parallel`` runs calls on threads. These functions judge
around them: the result of a call that raised or whose stop judgment raised,
whether the runner's assignment matches the pinned execution profile, which
fields the worker request carries, the result records of a failed start, how
stream bytes frame into observation rows, and what status and error a
collected run has.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

import jsonschema

from .canonical import canonical_json
from .observation_transport import decode_observation_row
from .values import strict_json_loads


def failed_result(error):
    """The one result a call records when its calculation raised instead of returning."""
    return {"status": "failed", "output": None, "usage": {}, "error": f"{type(error).__name__}: {error}"}


def judged_result(result, judge_error):
    """A call whose stop judgment raised fails with that error, whatever it returned."""
    if judge_error is not None and isinstance(result, dict):
        return {**result, "status": "failed",
                "error": f"stop judgment failed: {type(judge_error).__name__}: {judge_error}"}
    return result


def runner_assignment(*, provider: str, cli_model: str, effort: str, timeout_seconds, execution_id, profile,
                      launch_ticket, jobs, scholarly_server, claude_only_assigned_model, input_seal, prompt,
                      publishes_start: bool, host_id) -> dict[str, Any]:
    """Check the runner's assignment against its pinned profile.

    Returns the profile reference, the Job resource limits and the tools the
    worker receives; a pinned profile alone supplies ``scholarly_server`` and
    ``claude_only_assigned_model``. ``publishes_start`` tells whether the caller
    publishes the start before resume, which host-bound limits require.
    """
    reference = None
    resource_limits = None
    if provider == "claude" and not cli_model.strip():
        raise ValueError("claude: requires a Claude model name or alias")
    from .worker_request import validate_max_runtime
    validate_max_runtime(timeout_seconds)  # The worker applies the same rule to its request.
    if profile is not None:
        from .launch import validate_start
        validate_start(launch_ticket, jobs=jobs, execution_id=execution_id, profile_sha256=profile['sha256'])
        from .execution_profiles import profile_ref, prompt_seal, job_resource_limits, WORK_ROLES
        reference = profile_ref(profile)
        resource_limits = job_resource_limits(profile, host_id=host_id)
        if resource_limits is not None and not publishes_start:
            raise ValueError("host-bound runner requires on_started publication before resume")
        ai = profile.get("ai", {})
        if not execution_id or cli_model != ai.get("model", "").removeprefix("claude:") or effort != ai.get("effort"):
            raise ValueError("runner assignment differs from the pinned execution profile")
        if profile["role"] not in WORK_ROLES and (
                timeout_seconds is None or timeout_seconds > profile["window"]["call_timeout_seconds"]):
            raise ValueError("runner deadline exceeds the pinned profile")
        # A pinned profile alone supplies the runner's tools and model lock.
        if scholarly_server is not None or claude_only_assigned_model is not None:
            raise ValueError("a pinned profile supplies scholarly_server and claude_only_assigned_model")
        scholarly_server = ai.get("scholarly_server")
        claude_only_assigned_model = ai["claude_only_assigned_model"]
        if not isinstance(input_seal, dict) or any(input_seal.get(k) != v for k, v in prompt_seal(prompt).items()):
            raise ValueError("runner input differs from its UTF-8 seal")
        if input_seal["bytes"] > profile["input"]["max_input_bytes"]:
            raise ValueError("sealed input exceeds the pinned profile limit")
    elif execution_id is not None:
        raise ValueError("execution identity requires a pinned profile")
    return {"reference": reference, "resource_limits": resource_limits, "scholarly_server": scholarly_server,
            "claude_only_assigned_model": claude_only_assigned_model}


def worker_request_fields(options: dict, *, prompt_path, workspace, evidence_dir, cli_model: str, effort: str,
                          timeout_seconds, schema_path, execution_id, reference, resource_limits, control_binding,
                          scholarly_server, claude_only_assigned_model) -> dict[str, Any]:
    """The worker request: the adapter's options, the evidence paths and what the assignment binds."""
    request = {**options, "prompt_path": str(prompt_path),
               "cwd": str(workspace), "model": cli_model, "effort": effort, "max_runtime_seconds": timeout_seconds,
               "stdout_path": str(evidence_dir / "stdout.jsonl"), "stderr_path": str(evidence_dir / "stderr.txt"),
               "status_path": str(evidence_dir / "worker-status.json")}
    if schema_path is not None:
        request["output_schema_path"] = str(schema_path)
    if reference is not None:
        request.update(execution_id=execution_id, profile_ref=reference)
    if resource_limits is not None:
        request["resource_limits"] = resource_limits
    if control_binding is not None:
        request["control_binding"] = deepcopy(control_binding)
    if scholarly_server is not None:
        request["scholarly_server"] = scholarly_server
    if claude_only_assigned_model and "claude_path" in request:
        request["claude_only_assigned_model"] = True
    return request


def launch_conflict_result(error, *, evidence_dir, execution_id, reference) -> dict[str, Any]:
    """An output path already existed, so no Job was created."""
    return {'status':'failed','output':None,'usage':{},'error_kind':'launch_conflict',
            'error':str(error),'launch_not_created':True,'evidence_dir':str(evidence_dir),
            'execution_id':execution_id,'profile_ref':reference}


def unsupported_result(error, *, evidence_dir, execution_id, reference, cli_model: str) -> dict[str, Any]:
    """The host cannot give the profile its local Job, so no Job was created."""
    return {"status": "failed", "output": None, "usage": {}, "evidence_dir": str(evidence_dir),
            "execution_id": execution_id, "profile_ref": reference, "assigned_model": cli_model,
            "error_kind": "profile_unsupported", "error": str(error), "launch_not_created":True,
            "capability_failure": {"capability": getattr(error, "capability", "atomic_local_job"), "status": "unsupported",
                                   "execution_profile_ref": reference, "error_type": type(error).__name__}}


def frame_rows(data: bytes, begin: int, *, final: bool):
    """Complete stream rows in ``data`` (read from stream offset ``begin``), and the bytes left over.

    After termination, ``final`` also frames an unterminated last row. Returns
    ``(events, offsets, rows, remainder)``; blank rows are skipped.
    """
    end = len(data) if final else data.rfind(b"\n") + 1
    remainder = data[end:]
    events, offsets, rows = [], [], []
    position = 0
    while position < end:
        stop = data.find(b"\n", position, end)
        stop = end if stop < 0 else stop + 1
        row = data[position:stop]
        if row.strip():
            events.append(decode_observation_row(row))
            offsets.append((begin + position, begin + stop))
            rows.append(row)
        position = stop
    return events, offsets, rows, remainder


def classify_run(collected: dict, *, started: dict, stopped: bool, cli_model: str, claude_only_assigned_model,
                 control_binding, output_schema: dict, evidence_dir, execution_id, reference,
                 provider_failure: Callable[[dict], dict | None], now: Callable[[], str]) -> dict[str, Any]:
    """The run's result from its collection: completed, stopped, or failed with its error kind."""
    parsed = collected.get("jsonl", {})
    observation = collected["provider_observation"]
    usage = observation["usage"]
    result = {"status": "stopped" if stopped else "failed", "output": None,
              "usage": usage if isinstance(usage, dict) else {}, "evidence_dir": str(evidence_dir),
              "execution": {"started": started, "collect": collected}, "error": None,
              "error_kind": "execution_failure", "assigned_model": cli_model}
    result.update(execution_id=execution_id, profile_ref=reference, provider_observation=observation)
    for key in ("usage_segments", "model_usage_reported", "usage_scope", "reported_models", "selected_result", "post_result_events", "background_events"):
        if key in parsed:
            result[key] = parsed[key]
    if claude_only_assigned_model and any(name != cli_model for name in parsed.get("reported_models", [])):
        result.update(error="reported model differs from the locked assignment", error_kind="model_policy")
        return result
    if stopped:
        result["error"] = "stop requested or timeout"
        return result
    if collected.get("result") != "output_collected":
        result["error"] = "; ".join(collected.get("reasons", ["collection incomplete"]))
        limit = provider_failure(parsed)
        if limit:
            result.update(error_kind="provider_limit", failure={**limit,
                "observed_at": now(),
                "evidence_ref": str(evidence_dir / "stdout.jsonl")})
        return result
    if control_binding is not None:
        result.update(status="completed", output=None, collection="provider_evidence_only")
        result.pop("error_kind", None)
        return result
    raw = collected["final"].get("raw")
    try:
        output = strict_json_loads(raw.decode("utf-8"))
        canonical_json(output)
        result["output"] = output
        jsonschema.validate(output, output_schema)
    except jsonschema.ValidationError as exc:
        path = "output" + "".join("/" + str(part) for part in exc.absolute_path)
        result.update(error=path + ": " + exc.message, error_kind="output_validation")
        return result
    except Exception as exc:
        result.update(error=f"output JSON: {type(exc).__name__}: {exc}", error_kind="output_validation")
        return result
    result.update(status="completed", output=output)
    result.pop("error_kind", None)
    return result
