"""Evidence-producing CLI runners sharing validation and local lifetime handling."""
from __future__ import annotations

import json
import shutil
import os
from pathlib import Path
import time
from typing import Any, Callable

import jsonschema

from do_math.codex_adapter import CodexExecAdapter
from do_math.claude_adapter import ClaudePrintAdapter
from do_math.repository import canonical_json, _unique_pairs, _reject_constant


class CodexModelRunner:
    def __init__(self, codex_path: str | None = None, *, windows_sandbox: str = "unelevated", sandbox: str = "danger-full-access") -> None:
        self.codex_path = codex_path or shutil.which("codex") or "codex"
        if windows_sandbox not in {"unelevated", "elevated"}:
            raise ValueError("windows_sandbox must be unelevated or elevated")
        self.windows_sandbox = windows_sandbox
        if sandbox not in {"read-only", "workspace-write", "danger-full-access"}:
            raise ValueError("unsupported CLI sandbox")
        self.sandbox = sandbox
        self._adapter = CodexExecAdapter(self.codex_path)

    def worker_options(self) -> dict:
        return {"codex_path": self.codex_path, "sandbox": self.sandbox,
                "approval_policy": "never", "windows_sandbox": self.windows_sandbox}

    def run(self, *, prompt: str, output_schema: dict, workspace: Path, evidence_dir: Path,
            model: str, effort: str, timeout_seconds: float,
            scholarly_server: dict | None = None,
            should_stop: Callable[[], bool] | None = None,
            on_started: Callable[[dict], None] | None = None,
            on_observation: Callable[[dict], None] | None = None) -> dict:
        workspace, evidence_dir = workspace.resolve(), evidence_dir.resolve()
        if evidence_dir.exists():
            raise FileExistsError("evidence_dir must be new")
        if not isinstance(prompt, str) or not isinstance(output_schema, dict) or timeout_seconds <= 0:
            raise ValueError("invalid prompt, schema, or timeout")
        evidence_dir.mkdir(parents=True)
        prompt_path, schema_path = evidence_dir / "input.txt", evidence_dir / "output.schema.json"
        prompt_path.write_text(prompt, encoding="utf-8")
        schema_path.write_text(json.dumps(output_schema, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        request = {**self.worker_options(), "prompt_path": str(prompt_path), "output_schema_path": str(schema_path),
                   "cwd": str(workspace), "model": model, "effort": effort, "max_runtime_seconds": timeout_seconds,
                   "stdout_path": str(evidence_dir / "stdout.jsonl"), "stderr_path": str(evidence_dir / "stderr.txt"),
                   "final_path": str(evidence_dir / "final.txt"), "status_path": str(evidence_dir / "worker-status.json")}
        if scholarly_server is not None:
            request["scholarly_server"] = scholarly_server
        request_path = evidence_dir / "request.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        execution = self._adapter.start(request_path, cwd=evidence_dir, env=os.environ)
        offset = 0
        buffer = b""
        last_tick = 0.0

        def observe() -> None:
            nonlocal offset, buffer, last_tick
            if on_observation is None:
                return
            stdout_path = evidence_dir / "stdout.jsonl"
            if stdout_path.exists():
                with stdout_path.open("rb") as stream:
                    stream.seek(offset)
                    chunk = stream.read()
                    offset = stream.tell()
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        try:
                            event = json.loads(line)
                        except (UnicodeError, json.JSONDecodeError):
                            event = {"type": "unparsed_observation", "bytes": len(line)}
                        on_observation(event)
            current = time.monotonic()
            if current - last_tick >= 1:
                last_tick = current
                on_observation({"type": "tick"})
        started = {"pid": execution.job.pid, "creation_filetime": execution.job.creation_filetime,
                   "request_sha256": execution.request_sha256, "job_name": getattr(execution.job, "name", None)}
        try:
            if on_started: on_started(started)
            if should_stop and should_stop():
                self._adapter.stop(execution)
                if not self._adapter.wait_for_termination(execution, timeout_seconds):
                    raise RuntimeError("termination barrier not reached after pre-start stop")
                collected = self._adapter.collect(execution)
                return {"status":"stopped","output":None,"usage":{},"evidence_dir":str(evidence_dir),
                        "execution":{"started":started,"collect":collected},"error":"stop requested before resume"}
            self._adapter.resume(execution)
            deadline, stopped = time.monotonic() + timeout_seconds, False
            while not self._adapter.wait_for_termination(execution, 0):
                observe()
                if self._adapter.wait_for_termination(execution, 0):
                    break
                if not stopped and ((should_stop and should_stop()) or time.monotonic() >= deadline):
                    self._adapter.stop(execution); stopped = True
                time.sleep(.2)
            collected = self._adapter.collect(execution)
        except Exception:
            self._adapter.stop(execution)
            if not self._adapter.wait_for_termination(execution, timeout_seconds):
                raise RuntimeError("termination barrier not reached during exception cleanup")
            raise
        finally:
            execution.job.close()
        usage = collected.get("jsonl", {}).get("usage", [])
        usage = usage[-1] if isinstance(usage, list) and usage else {}
        result = {"status": "stopped" if stopped else "failed", "output": None,
                  "usage": usage if isinstance(usage, dict) else {}, "evidence_dir": str(evidence_dir),
                  "execution": {"started": started, "collect": collected}, "error": None}
        if stopped:
            result["error"] = "stop requested or timeout"
            return result
        if collected.get("result") != "output_collected":
            result["error"] = "; ".join(collected.get("reasons", ["collection incomplete"]))
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
        if model.startswith("claude:"):
            name = model.removeprefix("claude:")
            if not name.strip():
                raise ValueError("claude: requires a Claude model name or alias")
            return self.claude.run(model=name, **options)
        if model.startswith("claude-"):
            return self.claude.run(model=model, **options)
        return self.codex.run(model=model, **options)
