"""Evidence-producing CLI runners sharing validation and local lifetime handling."""
from __future__ import annotations
from .operation_trace import measured


import json
import os
from pathlib import Path
from threading import Lock
import time
from typing import Callable

import jsonschema

from do_math.claude_adapter import ADAPTERS, provider_adapter, request_provider
from do_math.provider_wait import provider_for
from do_math.file_io import now, strict_json_loads
from do_math.repository import canonical_json
from do_math.session_slots import local_termination_confirmed
from .observation_transport import ObservationBatch, decode_observation_row


class ModelRunner:
    """Run one configured model through its provider's adapter (``claude_adapter.ADAPTERS``).

    ``adapters`` maps each provider to the adapter this runner starts; a caller
    may replace an entry. Capacity remains keyed by the configured model name.
    """

    def __init__(self, codex_path: str | None = None, claude_path: str | None = None) -> None:
        paths = {"codex": codex_path, "claude": claude_path}
        self.adapters = {provider: provider_adapter(provider, paths.get(provider)) for provider in ADAPTERS}

    @measured('model_execution')
    def run(self, *, prompt: str, output_schema: dict, workspace: Path, evidence_dir: Path,
            model: str, effort: str, timeout_seconds: float | None,
            execution_id: str | None = None, profile: dict | None = None,
            launch_ticket: dict | None = None,
            control_binding: dict | None = None,
            input_seal: dict | None = None,
            scholarly_server: dict | None = None,
            claude_only_assigned_model: bool | None = None,
            should_stop: Callable[[], bool] | None = None,
            on_started: Callable[[dict], None] | None = None,
            on_observation: Callable[[ObservationBatch], None] | None = None) -> dict:
        reference = None
        resource_limits = None
        provider = provider_for(model)
        adapter = self.adapters[provider]
        # A Claude model is configured as ``claude:<name>``; its CLI receives the bare name.
        cli_model = model.removeprefix("claude:")
        if provider == "claude" and not cli_model.strip():
            raise ValueError("claude: requires a Claude model name or alias")
        from .cli_worker import validate_max_runtime
        validate_max_runtime(timeout_seconds)  # The worker applies the same rule to its request.
        if profile is not None:
            from .launch import validate_start
            validate_start(launch_ticket, execution_id=execution_id, profile_sha256=profile['sha256'])
            from .execution_profiles import profile_ref, prompt_seal, job_resource_limits, WORK_ROLES
            reference = profile_ref(profile)
            resource_limits = job_resource_limits(profile)
            if resource_limits is not None and not callable(on_started):
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
        if control_binding is not None:
            from .cli_worker import validate_execution_binding
            validate_execution_binding({"execution_id": execution_id, "profile_ref": reference,
                                        "control_binding": control_binding, "cwd": str(workspace.resolve())})
        workspace, evidence_dir = workspace.resolve(), evidence_dir.resolve()
        if evidence_dir.exists():
            raise FileExistsError("evidence_dir must be new")
        if not isinstance(prompt, str) or not isinstance(output_schema, dict):
            raise ValueError("invalid prompt or schema")
        evidence_dir.mkdir(parents=True)
        prompt_path = evidence_dir / "input.txt"
        prompt_path.write_bytes(prompt.encode("utf-8"))
        request = {**adapter.worker_options(evidence_dir), "prompt_path": str(prompt_path),
                   "cwd": str(workspace), "model": cli_model, "effort": effort, "max_runtime_seconds": timeout_seconds,
                   "stdout_path": str(evidence_dir / "stdout.jsonl"), "stderr_path": str(evidence_dir / "stderr.txt"),
                   "status_path": str(evidence_dir / "worker-status.json")}
        if control_binding is None:
            # Unbound consumers use the structured final response, so only they
            # hand the CLI a schema file. Research binds its full schema to the
            # central draft submission instead; its input bundle preserves that schema.
            schema_path = evidence_dir / "output.schema.json"
            schema_path.write_text(json.dumps(output_schema, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            request["output_schema_path"] = str(schema_path)
        if reference is not None:
            request.update(execution_id=execution_id, profile_ref=reference)
        if resource_limits is not None:
            request["resource_limits"] = resource_limits
        if control_binding is not None:
            from copy import deepcopy
            request["control_binding"] = deepcopy(control_binding)
        if scholarly_server is not None:
            request["scholarly_server"] = scholarly_server
        if claude_only_assigned_model and "claude_path" in request:
            request["claude_only_assigned_model"] = True
        request_path = evidence_dir / "request.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        from .windows_job import WindowsJobUnsupportedError
        try:
            execution = adapter.start(request_path, cwd=evidence_dir, env=os.environ,
                **({'job_name':launch_ticket['job_name']} if launch_ticket is not None else {}))
        except FileExistsError as error:
            return {'status':'failed','output':None,'usage':{},'error_kind':'launch_conflict',
                    'error':str(error),'launch_not_created':True,'evidence_dir':str(evidence_dir),
                    'execution_id':execution_id,'profile_ref':reference}
        except WindowsJobUnsupportedError as error:
            result = {"status": "failed", "output": None, "usage": {}, "evidence_dir": str(evidence_dir),
                    "execution_id": execution_id, "profile_ref": reference, "assigned_model": cli_model,
                    "error_kind": "profile_unsupported", "error": str(error), "launch_not_created":True,
                    "capability_failure": {"capability": getattr(error, "capability", "atomic_local_job"), "status": "unsupported",
                                           "execution_profile_ref": reference, "error_type": type(error).__name__}}
            # Only a failed start records the local identity it failed under.
            if profile is not None:
                identity = adapter.capability_identity()
                from .execution_profiles import structural_failure_evidence
                failure_path = evidence_dir / "capability-failure.json"
                failure_path.write_bytes(canonical_json({**result["capability_failure"], "error": str(error),
                                                        "identity": identity, "execution_id": execution_id}))
                result["capability_evidence"] = structural_failure_evidence(profile, identity,
                    observed_at=now(), execution_id=execution_id,
                    evidence_ref=str(failure_path), capability=result["capability_failure"]["capability"])
            return result
        offset = 0
        buffer = b""
        rows_emitted = 0
        last_tick = 0.0
        # The owner applies queued batches later and may probe after this call
        # returns. A closed Job has terminated; never inspect its closed handle.
        job_closed, job_guard = False, Lock()

        def terminated() -> bool:
            with job_guard:
                return job_closed or adapter.wait_for_termination(execution, 0)

        def observe(final: bool = False) -> None:
            """Deliver complete rows; after termination, ``final`` also delivers an unterminated last row."""
            nonlocal offset, buffer, rows_emitted, last_tick
            if on_observation is None:
                return
            stdout_path = evidence_dir / "stdout.jsonl"
            chunk = b''
            begin = offset - len(buffer)
            if stdout_path.exists():
                with stdout_path.open("rb") as stream:
                    stream.seek(offset)
                    chunk = stream.read(1024 * 1024)
                    offset = stream.tell()
            data = buffer + chunk
            end = len(data) if final else data.rfind(b"\n") + 1
            buffer = data[end:]
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
            current = time.monotonic()
            if chunk or final or current - last_tick >= 1:
                last_tick = current
                on_observation(ObservationBatch(events, offsets, rows, rows_emitted,
                    now(), current, offset, stdout_path, terminated))
                rows_emitted += len(rows)
        from .windows_job import process_identity
        started = {**process_identity(execution.job),
                   "request_sha256": execution.request_sha256, "job_name": getattr(execution.job, "name", None)}
        if reference is not None:
            started.update(execution_id=execution_id, profile_ref=reference)
        try:
            if resource_limits is not None:
                started["host_resources"] = execution.job.resource_usage()
                if started["host_resources"]["limits"] != resource_limits:
                    raise RuntimeError("local Job settings differ from pinned profile before resume")
            if on_started: on_started(started)
            if should_stop and should_stop():
                adapter.stop(execution)
                if not adapter.wait_for_termination(execution, timeout_seconds):
                    raise RuntimeError("termination barrier not reached after pre-start stop")
                collected = adapter.collect(execution)
                return {"status":"stopped","output":None,"usage":{},"evidence_dir":str(evidence_dir),
                        "execution_id": execution_id, "profile_ref": reference,
                        "provider_observation": collected["provider_observation"],
                        "execution":{"started":started,"collect":collected},"error":"stop requested before resume"}
            adapter.resume(execution)
            deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
            stopped = False
            while not adapter.wait_for_termination(execution, 0):
                observe()
                if adapter.wait_for_termination(execution, 0):
                    break
                if not stopped and ((should_stop and should_stop()) or
                                    (deadline is not None and time.monotonic() >= deadline)):
                    adapter.stop(execution); stopped = True
                time.sleep(.2)
            # Drain complete local stream bytes once the Job has ended. The
            # batch's fresh barrier probe prevents replay from opening live work.
            stdout_path = evidence_dir / "stdout.jsonl"
            while on_observation is not None and stdout_path.exists() and offset < stdout_path.stat().st_size:
                observe()
            if buffer:
                observe(final=True)
            collected = adapter.collect(execution)
        except Exception:
            adapter.stop(execution)
            if not adapter.wait_for_termination(execution, timeout_seconds):
                raise RuntimeError("termination barrier not reached during exception cleanup")
            raise
        finally:
            with job_guard:
                job_closed = True
            execution.job.close()
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
            limit = adapter.provider_failure(parsed)
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


def verified_native_final(result, execution, context):
    """Revalidate captured native evidence against the published start and input.

    This consumes adapter evidence after the real local termination barrier.
    A completed runner status or an arbitrary final file is not sufficient.
    """
    import base64
    if result.get('status') != 'completed':
        raise ValueError('native execution did not complete normally')
    try:
        evidence = result['execution']; collected = evidence['collect']; started = evidence['started']
        barrier = collected['termination_barrier']
        if (collected['result'] != 'output_collected' or collected.get('reasons')
                or collected.get('stop_receipts') or barrier.get('confirmed') is not True
                or barrier.get('root_signaled') is not True or barrier.get('active_processes') != 0
                or barrier.get('process_ids') not in ([], ())
                or not local_termination_confirmed(execution)):
            raise ValueError('native collection or local termination is incomplete')
        def raw_artifact(name):
            # Collection hashed these bytes once; its recorded digests are compared, not recomputed.
            artifact = collected[name]; raw = artifact['raw']
            if isinstance(raw, dict):
                if raw['sha256'] != artifact['sha256']:
                    raise ValueError('serialized native artifact differs')
                raw = base64.b64decode(raw['base64'], validate=True)
            if (not isinstance(raw, bytes) or artifact.get('present') is not True
                    or not isinstance(artifact['sha256'], str) or artifact['bytes'] != len(raw)):
                raise ValueError('native artifact hash or size differs: ' + name)
            return raw
        request_raw = raw_artifact('source_request'); raw_artifact('source_prompt')
        stdout = raw_artifact('stdout'); final = raw_artifact('final')
        request = strict_json_loads(request_raw); status = collected['worker_status']
        request_hash = collected['source_request']['sha256']; prompt_hash = collected['source_prompt']['sha256']
        published = execution.get('capacity', {}).get('process') or {}
        if (started.get('request_sha256') != request_hash
                or published.get('request_sha256') != request_hash
                or prompt_hash != execution['input_manifest']['prompt']['sha256']
                or status.get('state') != 'exited' or status.get('cli_exit_code') != 0
                or status.get('request_sha256') != request_hash or status.get('stdin_sha256') != prompt_hash
                or status.get('schema_sha256') is not None or 'output_schema_path' in request):
            raise ValueError('native request, input, or worker completion differs from the published execution')
        for key, expected in [('execution_id', execution['id']), ('profile_ref', execution['execution_profile_ref'])]:
            if any(row.get(key) != expected for row in (request, status, collected, started)):
                raise ValueError('native execution/profile binding differs')
        binding = request['control_binding']
        if (context.get('execution_id') != execution['id'] or binding.get('execution_id') != execution['id']
                or binding.get('grant_id') != execution.get('grant_id')
                or context.get('action', {}).get('grant_id') != execution.get('grant_id')):
            raise ValueError('native input or authority binding differs')
        def exact_integer(value):
            if type(value) is int and value > 0:
                return value
            if isinstance(value, str) and value.isascii() and value.isdecimal() and int(value) > 0:
                return int(value)
            raise ValueError('native process identity requires an exact positive integer')
        for key in ('pid', 'creation_filetime'):
            expected = exact_integer(published.get(key))
            if any(exact_integer(row.get(key)) != expected for row in (started, collected['process_identity'])):
                raise ValueError('native collected/start identity differs from its published process')
        if not started.get('job_name') or published.get('job_name') != started['job_name']:
            raise ValueError('native Job identity differs from its published process')
        adapter = provider_adapter(request_provider(request), 'evidence-only')
        parsed = adapter.parse_response(stdout, request)
        if (not parsed.get('parse_complete') or not parsed.get('turn_completed') or parsed.get('turn_failed')
                or adapter.validate_final(parsed, final)):
            raise ValueError('native stream does not establish this exact completed final')
        return final
    except (KeyError, TypeError, OSError, IndexError) as error:
        raise ValueError('native completion evidence is missing or malformed') from error
