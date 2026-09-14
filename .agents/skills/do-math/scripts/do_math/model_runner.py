"""Synchronous evidence-producing wrapper around the narrow Codex CLI adapter."""
from __future__ import annotations

import json
import shutil
import os
from pathlib import Path
import time
from typing import Any, Callable

import jsonschema

from do_math.codex_adapter import CodexExecAdapter


class CodexModelRunner:
    def __init__(self, codex_path: str | None = None) -> None:
        self.codex_path = codex_path or shutil.which("codex") or "codex"
        self._adapter = CodexExecAdapter(self.codex_path)

    def run(self, *, prompt: str, output_schema: dict, workspace: Path, evidence_dir: Path,
            model: str, effort: str, timeout_seconds: float,
            should_stop: Callable[[], bool] | None = None,
            on_started: Callable[[dict], None] | None = None) -> dict:
        workspace, evidence_dir = workspace.resolve(), evidence_dir.resolve()
        if evidence_dir.exists():
            raise FileExistsError("evidence_dir must be new")
        if not isinstance(prompt, str) or not isinstance(output_schema, dict) or timeout_seconds <= 0:
            raise ValueError("invalid prompt, schema, or timeout")
        evidence_dir.mkdir(parents=True)
        prompt_path, schema_path = evidence_dir / "input.txt", evidence_dir / "output.schema.json"
        prompt_path.write_text(prompt, encoding="utf-8")
        schema_path.write_text(json.dumps(output_schema, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        request = {"codex_path": self.codex_path, "prompt_path": str(prompt_path), "output_schema_path": str(schema_path),
                   "cwd": str(workspace), "model": model, "effort": effort, "sandbox": "workspace-write",
                   "approval_policy": "never", "windows_sandbox": "elevated", "max_runtime_seconds": timeout_seconds,
                   "stdout_path": str(evidence_dir / "stdout.jsonl"), "stderr_path": str(evidence_dir / "stderr.txt"),
                   "final_path": str(evidence_dir / "final.txt"), "status_path": str(evidence_dir / "worker-status.json")}
        request_path = evidence_dir / "request.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        execution = self._adapter.start(request_path, cwd=evidence_dir, env=os.environ)
        started = {"pid": execution.job.pid, "creation_filetime": execution.job.creation_filetime,
                   "request_sha256": execution.request_sha256}
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
            output = json.loads(raw.decode("utf-8"))
            jsonschema.validate(output, output_schema)
        except Exception as exc:
            result["error"] = type(exc).__name__
            return result
        result.update(status="completed", output=output)
        return result
