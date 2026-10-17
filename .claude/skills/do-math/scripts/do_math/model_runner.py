"""Evidence-producing CLI runners sharing validation and local lifetime handling."""
from __future__ import annotations
from .operation_trace import measured


import json
import os
from pathlib import Path
from threading import Lock
from typing import Callable


from do_math.claude_adapter import ADAPTERS, provider_adapter
from do_math.provider_wait import provider_for
from do_math.canonical import canonical_json
from .observation_transport import ObservationBatch
from .provider_final import output_contract
from .model_call import (classify_run, frame_rows, launch_conflict_result, runner_assignment,
                         unsupported_result, worker_request_fields)

# A stream read is an I/O unit, not an indivisible owner transaction. Four
# native rows keep each queued application finite before controls/returns can
# take the owner again (one second in the 0.25-second-per-row progress model).
OBSERVATION_BATCH_ROWS = 4


class ModelRunner:
    """Run one configured model through its provider's adapter (``claude_adapter.ADAPTERS``).

    ``adapters`` maps each provider to the adapter this runner starts; a caller
    may replace an entry. Capacity remains keyed by the configured model name.
    """

    def __init__(self, codex_path: str | None = None, claude_path: str | None = None, *, jobs,
                 clock, environment, host_id) -> None:
        paths = {"codex": codex_path, "claude": claude_path}
        self.jobs = jobs
        self.host_id, self.environment = host_id, environment
        # The clock port: observation times, run deadlines and polling.
        self.clock = clock
        self.adapters = {provider: provider_adapter(provider, paths.get(provider), jobs=jobs, clock=self.clock)
                         for provider in ADAPTERS}

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
        provider = provider_for(model)
        adapter = self.adapters[provider]
        # A Claude model is configured as ``claude:<name>``; its CLI receives the bare name.
        cli_model = model.removeprefix("claude:")
        assignment = runner_assignment(provider=provider, cli_model=cli_model, effort=effort,
            timeout_seconds=timeout_seconds, execution_id=execution_id, profile=profile, launch_ticket=launch_ticket,
            jobs=self.jobs, scholarly_server=scholarly_server, claude_only_assigned_model=claude_only_assigned_model,
            input_seal=input_seal, prompt=prompt, publishes_start=callable(on_started), host_id=self.host_id)
        reference, resource_limits = assignment["reference"], assignment["resource_limits"]
        scholarly_server = assignment["scholarly_server"]
        claude_only_assigned_model = assignment["claude_only_assigned_model"]
        if control_binding is not None:
            from .worker_request import validate_execution_binding
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
        schema_path = None
        if control_binding is None:
            # Unbound consumers use the structured final response, so only they
            # hand the CLI a schema file. Research binds its full schema to the
            # central draft submission instead; its input bundle preserves that schema.
            schema_path = evidence_dir / "output.schema.json"
            schema_path.write_text(json.dumps(output_schema, ensure_ascii=False, sort_keys=True, allow_nan=False), encoding="utf-8")
            if provider == "codex":
                # Preserve the original separately. The worker snapshots and hashes
                # the transport contract, whose description carries the original.
                schema_path = evidence_dir / "transport.schema.json"
                schema_path.write_text(json.dumps(output_contract(provider, output_schema),
                    ensure_ascii=False, sort_keys=True, allow_nan=False), encoding="utf-8")
        request = worker_request_fields(adapter.worker_options(evidence_dir), prompt_path=prompt_path,
            workspace=workspace, evidence_dir=evidence_dir, cli_model=cli_model, effort=effort,
            timeout_seconds=timeout_seconds, schema_path=schema_path, execution_id=execution_id, reference=reference,
            resource_limits=resource_limits, control_binding=control_binding, scholarly_server=scholarly_server,
            claude_only_assigned_model=claude_only_assigned_model)
        request_path = evidence_dir / "request.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        from .windows_job import WindowsJobUnsupportedError
        try:
            execution = adapter.start(request_path, cwd=evidence_dir, env=self.environment,
                **({'job_name':launch_ticket['job_name']} if launch_ticket is not None else {}))
        except FileExistsError as error:
            return launch_conflict_result(error, evidence_dir=evidence_dir, execution_id=execution_id,
                                          reference=reference)
        except WindowsJobUnsupportedError as error:
            result = unsupported_result(error, evidence_dir=evidence_dir, execution_id=execution_id,
                                        reference=reference, cli_model=cli_model)
            # Only a failed start records the local identity it failed under.
            if profile is not None:
                identity = adapter.capability_identity()
                from .execution_profiles import structural_failure_evidence
                failure_path = evidence_dir / "capability-failure.json"
                failure_path.write_bytes(canonical_json({**result["capability_failure"], "error": str(error),
                                                        "identity": identity, "execution_id": execution_id}))
                result["capability_evidence"] = structural_failure_evidence(profile, identity,
                    observed_at=self.clock.now(), execution_id=execution_id,
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
            events, offsets, rows, buffer = frame_rows(buffer + chunk, begin, final=final)
            current = self.clock.monotonic()
            if chunk or final or current - last_tick >= 1:
                last_tick = current
                received_at = self.clock.now()
                for first in range(0, max(1, len(rows)), OBSERVATION_BATCH_ROWS):
                    end = min(first + OBSERVATION_BATCH_ROWS, len(rows))
                    # Only the final part reaches this read's offset and can
                    # evaluate its tick. Preserve blank/partial trailing bytes
                    # there; all other parts end at their last complete row.
                    end_offset = offset if end == len(rows) else offsets[end - 1][1]
                    on_observation(ObservationBatch(events[first:end], offsets[first:end], rows[first:end],
                        rows_emitted + first, received_at, current, end_offset, stdout_path, terminated,
                        ends_read=end == len(rows)))
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
            deadline = None if timeout_seconds is None else self.clock.monotonic() + timeout_seconds
            stopped = False
            while not adapter.wait_for_termination(execution, 0):
                observe()
                if adapter.wait_for_termination(execution, 0):
                    break
                if not stopped and ((should_stop and should_stop()) or
                                    (deadline is not None and self.clock.monotonic() >= deadline)):
                    adapter.stop(execution); stopped = True
                self.clock.sleep(.2)
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
        return classify_run(collected, started=started, stopped=stopped, cli_model=cli_model,
                            claude_only_assigned_model=claude_only_assigned_model, control_binding=control_binding,
                            output_schema=output_schema, evidence_dir=evidence_dir, execution_id=execution_id,
                            reference=reference, provider_failure=adapter.provider_failure, now=self.clock.now)
