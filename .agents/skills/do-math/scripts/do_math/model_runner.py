"""Evidence-producing CLI runners sharing validation and local lifetime handling."""
from __future__ import annotations
from .operation_trace import measured


import json
import math
import shutil
import os
from pathlib import Path
from threading import Lock
import time
from typing import Callable

import jsonschema

from do_math.codex_adapter import CodexExecAdapter
from do_math.claude_adapter import ClaudePrintAdapter
from do_math.claude_stream import provider_limit
from do_math.provider_wait import provider_for
from datetime import datetime, timezone
from do_math.repository import canonical_json, _unique_pairs, _reject_constant
from .observation_transport import ObservationBatch


class CodexModelRunner:
    def __init__(self, codex_path: str | None = None) -> None:
        self.codex_path = codex_path or shutil.which("codex") or "codex"
        self._adapter = CodexExecAdapter(self.codex_path)

    def worker_options(self) -> dict:
        # The adopted local permission mode: existing user permissions, approval never.
        return {"codex_path": self.codex_path, "sandbox": "danger-full-access",
                "approval_policy": "never", "windows_sandbox": "unelevated"}

    @measured('model_execution')
    def run(self, *, prompt: str, output_schema: dict, workspace: Path, evidence_dir: Path,
            model: str, effort: str, timeout_seconds: float | None,
            execution_id: str | None = None, profile: dict | None = None,
            launch_ticket: dict | None = None,
            control_binding: dict | None = None,
            input_seal: dict | None = None,
            scholarly_server: dict | None = None,
            claude_only_assigned_model: bool = False,
            should_stop: Callable[[], bool] | None = None,
            on_started: Callable[[dict], None] | None = None,
            on_observation: Callable[[ObservationBatch], None] | None = None) -> dict:
        reference = None
        resource_limits = None
        if timeout_seconds is not None and (isinstance(timeout_seconds, bool)
                or not isinstance(timeout_seconds, (int, float))
                or not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
            raise ValueError("timeout must be positive and finite or null")
        if profile is not None:
            from .launch import validate_start
            validate_start(launch_ticket, execution_id=execution_id, profile_sha256=profile['sha256'])
            from .execution_profiles import profile_ref, prompt_seal, job_resource_limits
            reference = profile_ref(profile)
            resource_limits = job_resource_limits(profile)
            if resource_limits is not None and not callable(on_started):
                raise ValueError("host-bound runner requires on_started publication before resume")
            ai = profile.get("ai", {})
            if not execution_id or model != ai.get("model", "").removeprefix("claude:") or effort != ai.get("effort"):
                raise ValueError("runner assignment differs from the pinned execution profile")
            if profile["budget_kind"] == "operations" and (
                    timeout_seconds is None or timeout_seconds > profile["window"]["call_timeout_seconds"]):
                raise ValueError("runner deadline exceeds the pinned profile")
            if scholarly_server is not None and scholarly_server != ai.get("scholarly_server"):
                raise ValueError("runner tools differ from the pinned profile")
            scholarly_server = ai.get("scholarly_server")
            claude_only_assigned_model = ai["claude_only_assigned_model"]
            if not isinstance(input_seal, dict) or any(input_seal.get(k) != v for k, v in prompt_seal(prompt).items()):
                raise ValueError("runner input differs from its UTF-8 seal")
            if input_seal["bytes"] > profile["input"]["max_input_bytes"]:
                raise ValueError("sealed input exceeds the pinned profile limit")
        elif execution_id is not None:
            raise ValueError("execution identity requires a pinned profile")
        if control_binding is not None:
            from .codex_worker import validate_execution_binding
            validate_execution_binding({"execution_id": execution_id, "profile_ref": reference,
                                        "control_binding": control_binding, "cwd": str(workspace.resolve())})
        workspace, evidence_dir = workspace.resolve(), evidence_dir.resolve()
        if evidence_dir.exists():
            raise FileExistsError("evidence_dir must be new")
        if not isinstance(prompt, str) or not isinstance(output_schema, dict):
            raise ValueError("invalid prompt, schema, or timeout")
        evidence_dir.mkdir(parents=True)
        prompt_path, schema_path = evidence_dir / "input.txt", evidence_dir / "output.schema.json"
        prompt_path.write_bytes(prompt.encode("utf-8"))
        schema_path.write_text(json.dumps(output_schema, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        request = {**self.worker_options(), "prompt_path": str(prompt_path),
                   "cwd": str(workspace), "model": model, "effort": effort, "max_runtime_seconds": timeout_seconds,
                   "stdout_path": str(evidence_dir / "stdout.jsonl"), "stderr_path": str(evidence_dir / "stderr.txt"),
                   "final_path": str(evidence_dir / "final.txt"), "status_path": str(evidence_dir / "worker-status.json")}
        if control_binding is None:
            # Unbound consumers use the structured final response. Research
            # binds its full schema to the central draft submission instead;
            # verified native finals are captured under that same central schema.
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
            execution = self._adapter.start(request_path, cwd=evidence_dir, env=os.environ,
                **({'job_name':launch_ticket['job_name']} if launch_ticket is not None else {}))
        except FileExistsError as error:
            return {'status':'failed','output':None,'usage':{},'error_kind':'launch_conflict',
                    'error':str(error),'launch_not_created':True,'evidence_dir':str(evidence_dir),
                    'execution_id':execution_id,'profile_ref':reference}
        except WindowsJobUnsupportedError as error:
            result = {"status": "failed", "output": None, "usage": {}, "evidence_dir": str(evidence_dir),
                    "execution_id": execution_id, "profile_ref": reference, "assigned_model": model,
                    "error_kind": "profile_unsupported", "error": str(error), "launch_not_created":True,
                    "capability_failure": {"capability": getattr(error, "capability", "atomic_local_job"), "status": "unsupported",
                                           "execution_profile_ref": reference, "error_type": type(error).__name__}}
            # Only a failed start records the local identity it failed under.
            identity = self._adapter.capability_identity() if profile is not None and hasattr(self._adapter, "capability_identity") else None
            if profile is not None and isinstance(identity, dict) and identity:
                from .execution_profiles import structural_failure_evidence
                failure_path = evidence_dir / "capability-failure.json"
                failure_path.write_bytes(canonical_json({**result["capability_failure"], "error": str(error),
                                                        "identity": identity, "execution_id": execution_id}))
                result["capability_evidence"] = structural_failure_evidence(profile, identity,
                    observed_at=datetime.now(timezone.utc).isoformat(), execution_id=execution_id,
                    evidence_ref=str(failure_path), capability=result["capability_failure"]["capability"])
            return result
        offset = 0
        buffer = b""
        last_tick = 0.0
        # The owner applies queued batches later and may probe after this call
        # returns. A closed Job has terminated; never inspect its closed handle.
        job_closed, job_guard = False, Lock()

        def terminated() -> bool:
            with job_guard:
                return job_closed or self._adapter.wait_for_termination(execution, 0)

        def observe() -> None:
            nonlocal offset, buffer, last_tick
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
            lines = (buffer + chunk).split(b"\n")
            buffer = lines.pop()
            events, offsets = [], []
            for line in lines:
                start = begin
                begin += len(line) + 1
                if line.strip():
                    try:
                        event = json.loads(line)
                    except (UnicodeError, json.JSONDecodeError):
                        event = {"type": "unparsed_observation", "bytes": len(line)}
                    events.append(event)
                    offsets.append((start, begin))
            current = time.monotonic()
            if chunk or current - last_tick >= 1:
                last_tick = current
                on_observation(ObservationBatch(events, offsets, datetime.now(timezone.utc).isoformat(),
                    current, len(chunk), offset, stdout_path, terminated))
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
                self._adapter.stop(execution)
                if not self._adapter.wait_for_termination(execution, timeout_seconds):
                    raise RuntimeError("termination barrier not reached after pre-start stop")
                collected = self._adapter.collect(execution)
                return {"status":"stopped","output":None,"usage":{},"evidence_dir":str(evidence_dir),
                        "execution_id": execution_id, "profile_ref": reference,
                        "provider_observation": collected.get("provider_observation", {}),
                        "execution":{"started":started,"collect":collected},"error":"stop requested before resume"}
            self._adapter.resume(execution)
            deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
            stopped = False
            while not self._adapter.wait_for_termination(execution, 0):
                observe()
                if self._adapter.wait_for_termination(execution, 0):
                    break
                if not stopped and ((should_stop and should_stop()) or
                                    (deadline is not None and time.monotonic() >= deadline)):
                    self._adapter.stop(execution); stopped = True
                time.sleep(.2)
            # Drain complete local stream bytes once the Job has ended. The
            # batch's fresh barrier probe prevents replay from opening live work.
            stdout_path = evidence_dir / "stdout.jsonl"
            while on_observation is not None and stdout_path.exists() and offset < stdout_path.stat().st_size:
                observe()
            collected = self._adapter.collect(execution)
        except Exception:
            self._adapter.stop(execution)
            if not self._adapter.wait_for_termination(execution, timeout_seconds):
                raise RuntimeError("termination barrier not reached during exception cleanup")
            raise
        finally:
            with job_guard:
                job_closed = True
            execution.job.close()
        parsed = collected.get("jsonl", {})
        usage = parsed.get("usage", [])
        usage = parsed.get("usage_total", usage[-1] if isinstance(usage, list) and usage else {})
        result = {"status": "stopped" if stopped else "failed", "output": None,
                  "usage": usage if isinstance(usage, dict) else {}, "evidence_dir": str(evidence_dir),
                  "execution": {"started": started, "collect": collected}, "error": None,
                  "error_kind": "execution_failure", "assigned_model": model}
        result.update(execution_id=execution_id, profile_ref=reference,
            provider_observation=collected.get("provider_observation", {
                "execution_id": execution_id, "operation_ids": "unknown", "operation_count": "unknown",
                "remote_termination": "unknown", "stop_reason": parsed.get("stop_reason", "unknown"),
                "usage": usage if isinstance(usage, dict) else {},
                "usage_scope": "reported_execution_counters_not_invoice"}))
        for key in ("usage_segments", "model_usage_reported", "usage_scope", "reported_models", "selected_result", "post_result_events", "background_events"):
            if key in parsed:
                result[key] = parsed[key]
        if claude_only_assigned_model and any(name != model for name in parsed.get("reported_models", [])):
            result.update(error="reported model differs from the locked assignment", error_kind="model_policy")
            return result
        if stopped:
            result["error"] = "stop requested or timeout"
            return result
        if collected.get("result") != "output_collected":
            result["error"] = "; ".join(collected.get("reasons", ["collection incomplete"]))
            limit = provider_limit(parsed)
            if limit:
                result.update(error_kind="provider_limit", failure={**limit,
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "evidence_ref": str(evidence_dir / "stdout.jsonl")})
            return result
        if control_binding is not None:
            result.update(status="completed", output=None, collection="provider_evidence_only")
            result.pop("error_kind", None)
            return result
        raw = collected["final"].get("raw")
        try:
            output = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
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


class ClaudeModelRunner(CodexModelRunner):
    """Use Claude's request contract with the same result and callback interface."""

    def __init__(self, claude_path: str | None = None) -> None:
        self.claude_path = claude_path or shutil.which("claude") or "claude"
        self._adapter = ClaudePrintAdapter(self.claude_path)

    def worker_options(self) -> dict:
        return {"claude_path": self.claude_path}


class ModelRunner:
    """Route a configured model; capacity remains keyed by its configured name."""

    def __init__(self, codex_path: str | None = None, claude_path: str | None = None) -> None:
        self.codex = CodexModelRunner(codex_path)
        self.claude = ClaudeModelRunner(claude_path)

    def run(self, *, model: str, **options) -> dict:
        if provider_for(model) == "claude":
            name = model.removeprefix("claude:")
            if not name.strip():
                raise ValueError("claude: requires a Claude model name or alias")
            return self.claude.run(model=name, **options)
        options.pop("claude_only_assigned_model", None)
        return self.codex.run(model=model, **options)


def verified_native_final(result, execution, context):
    """Revalidate captured native evidence against the published start and input.

    This consumes adapter evidence after the real local termination barrier.
    A completed runner status or an arbitrary final file is not sufficient.
    """
    import base64
    from .submission import load_json
    from .codex_adapter import CodexExecAdapter
    from .claude_adapter import ClaudePrintAdapter
    if result.get('status') != 'completed':
        raise ValueError('native execution did not complete normally')
    try:
        evidence = result['execution']; collected = evidence['collect']; started = evidence['started']
        barrier = collected['termination_barrier']
        if (collected['result'] != 'output_collected' or collected.get('reasons')
                or collected.get('stop_receipts') or barrier.get('confirmed') is not True
                or barrier.get('root_signaled') is not True or barrier.get('active_processes') != 0
                or barrier.get('process_ids') not in ([], ())
                or execution.get('capacity', {}).get('local_termination') != 'confirmed'):
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
        request = json.loads(request_raw, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant); status = collected['worker_status']
        request_hash = collected['source_request']['sha256']; prompt_hash = collected['source_prompt']['sha256']
        if (started.get('request_sha256') != request_hash
                or execution.get('process', {}).get('request_sha256') != request_hash
                or prompt_hash != execution.get('input_sha256')
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
        published = execution.get('process', {})
        for key in ('pid', 'creation_filetime'):
            expected = exact_integer(published.get(key))
            if any(exact_integer(row.get(key)) != expected for row in (started, collected['process_identity'])):
                raise ValueError('native collected/start identity differs from its published process')
        if not started.get('job_name') or published.get('job_name') != started['job_name']:
            raise ValueError('native Job identity differs from its published process')
        adapter = ClaudePrintAdapter('evidence-only') if 'claude_path' in request else CodexExecAdapter('evidence-only')
        parsed = adapter.parse_response(stdout, request)
        if 'claude_path' not in request:
            events = [json.loads(line, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
                      for line in stdout.splitlines() if line.strip()]
            message = events[-2].get('item', {}) if len(events) >= 2 else {}
            if (events[-2].get('type') != 'item.completed' or message.get('type') != 'agent_message'
                    or not isinstance(message.get('text'), str) or message['text'].encode('utf-8') != final):
                raise ValueError('native final differs from the terminal message bytes')
        if (not parsed.get('parse_complete') or not parsed.get('turn_completed') or parsed.get('turn_failed')
                or adapter.validate_final(parsed, final)):
            raise ValueError('native stream does not establish this exact completed final')
        return final
    except (KeyError, TypeError, OSError, IndexError) as error:
        raise ValueError('native completion evidence is missing or malformed') from error
