"""Execute one ``codex exec`` request without a shell or API-key fallback."""
from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping

try:  # This module is also the direct ``python codex_worker.py`` Job root.
    from do_math.scholarly import validate_scholarly_server
    from do_math.control_transport import ControlTransport
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regression.
    from scholarly import validate_scholarly_server
    from control_transport import ControlTransport


_REMOVED_ENV = frozenset({
    "OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_BASE_URL",
    "OPENAI_API_BASE", "OPENAI_API_TYPE", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID",
    "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT",
})
_EFFORTS = frozenset({"minimal", "low", "medium", "high", "xhigh", "max", "ultra"})
_SANDBOXES = frozenset({"read-only", "workspace-write", "danger-full-access"})
_WINDOWS_SANDBOXES = frozenset({"unelevated", "elevated"})
_ENV_ALLOWLIST = frozenset({"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME",
                            "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "PROGRAMFILES",
                            "PROGRAMFILES(X86)", "COMMONPROGRAMFILES", "CODEX_HOME", "OS", "HOMEDRIVE", "HOMEPATH"})


def sanitized_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Keep ChatGPT login state while preventing a CLI API-key route."""
    return {key: value for key, value in (os.environ if source is None else source).items()
            if key.upper() in _ENV_ALLOWLIST and key.upper() not in _REMOVED_ENV}


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + key)
        value[key] = item
    return value


def validate_execution_binding(request):
    fields = {"execution_id", "profile_ref", "control_binding", "resource_limits"}
    if not fields.intersection(request):
        return
    ref = request.get("profile_ref")
    if (not isinstance(request.get("execution_id"), str) or not request["execution_id"].strip()
            or not isinstance(ref, dict) or set(ref) != {"id", "revision", "sha256"}
            or not isinstance(ref["id"], str) or not ref["id"]
            or type(ref["revision"]) is not int or ref["revision"] < 1
            or not isinstance(ref["sha256"], str) or len(ref["sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in ref["sha256"])):
        raise ValueError("worker execution binding requires exact execution_id and profile_ref")
    if "resource_limits" in request:
        try:
            from do_math.windows_job import validate_resource_limits
        except ModuleNotFoundError:
            from windows_job import validate_resource_limits
        if request["resource_limits"] is None:
            raise ValueError("explicit resource limits cannot be null")
        validate_resource_limits(request["resource_limits"])
    if "control_binding" in request:
        binding = request["control_binding"]
        names = {"endpoint", "transport_id", "capability", "execution_id", "grant_id"}
        if (not isinstance(binding, dict) or names - set(binding) or set(binding) - names - {"workspace"}
                or any(not isinstance(binding[key], str) or not binding[key].strip() or "\0" in binding[key] for key in names)
                or binding["execution_id"] != request["execution_id"]
                or not Path(binding["endpoint"]).is_absolute()):
            raise ValueError("control binding must identify this execution and an absolute local endpoint")
        if "workspace" in binding:
            workspace = binding["workspace"]
            if (not isinstance(workspace, str) or not workspace.strip() or "\0" in workspace
                    or not Path(workspace).is_absolute()):
                raise ValueError("control binding workspace must be an absolute local path")
            if "cwd" in request:
                cwd = request["cwd"]
                if (not isinstance(cwd, str) or not cwd.strip() or "\0" in cwd
                        or not Path(cwd).is_absolute() or Path(workspace).resolve() != Path(cwd).resolve()):
                    raise ValueError("control binding workspace differs from execution cwd")


def load_request(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError("worker request must be an object")
    required = ("codex_path", "prompt_path", "cwd", "model", "effort", "approval_policy",
                "max_runtime_seconds", "stdout_path", "stderr_path", "final_path", "status_path")
    missing = [name for name in required if name not in value]
    if missing:
        raise ValueError("worker request misses " + ", ".join(missing))
    if not isinstance(value["codex_path"], str) or not value["codex_path"] or "\x00" in value["codex_path"]:
        raise ValueError("codex_path must be one NUL-free executable string")
    if "codex_argv" in value:
        raise ValueError("codex_argv is forbidden; production accepts one executable only")
    unknown = set(value) - set(required) - {"sandbox", "filesystem", "windows_sandbox", "output_schema_path", "scholarly_server", "execution_id", "profile_ref", "control_binding", "resource_limits"}
    if unknown:
        raise ValueError("unknown worker request fields: " + ", ".join(sorted(unknown)))
    validate_execution_binding(value)
    if not isinstance(value["effort"], str) or value["effort"] not in _EFFORTS or value["approval_policy"] != "never":
        raise ValueError("unsupported effort or approval policy")
    if "filesystem" in value:
        if "sandbox" in value:
            raise ValueError("filesystem and legacy sandbox are mutually exclusive")
    elif not isinstance(value.get("sandbox"), str) or value["sandbox"] not in _SANDBOXES:
        raise ValueError("a supported legacy sandbox or filesystem profile is required")
    if not isinstance(value["model"], str) or not value["model"]:
        raise ValueError("model must be non-empty")
    timeout = value["max_runtime_seconds"]
    if timeout is not None and (not isinstance(timeout, (int, float)) or isinstance(timeout, bool)
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("max_runtime_seconds must be positive and finite or null")
    for name in ("prompt_path", "cwd", "stdout_path", "stderr_path", "final_path", "status_path"):
        if not isinstance(value[name], str) or not value[name] or "\x00" in value[name]:
            raise ValueError(name + " must be a non-empty path")
    if "output_schema_path" in value and (not isinstance(value["output_schema_path"], str)
                                          or not value["output_schema_path"] or "\x00" in value["output_schema_path"]):
        raise ValueError("output_schema_path must be a non-empty path when present")
    if "windows_sandbox" in value and value["windows_sandbox"] not in _WINDOWS_SANDBOXES:
        raise ValueError("windows_sandbox must be elevated or unelevated when present")
    if "scholarly_server" in value and value["scholarly_server"] is not None:
        value["scholarly_server"] = validate_scholarly_server(value["scholarly_server"])
    if "filesystem" in value:
        fs = value["filesystem"]
        if value.get("windows_sandbox") != "elevated" or not isinstance(fs, dict):
            raise ValueError("filesystem profile requires elevated windows sandbox")
        if set(fs) != {"read_roots", "write_roots", "deny_roots"}:
            raise ValueError("filesystem has exactly read_roots, write_roots, deny_roots")
        seen = set()
        for field in ("read_roots", "write_roots", "deny_roots"):
            roots = fs.get(field, [])
            if not isinstance(roots, list): raise ValueError(field + " must be a list")
            for root in roots:
                if (not isinstance(root, str) or "\x00" in root or any(char in root for char in "*?[]")
                        or not Path(root).is_absolute()):
                    raise ValueError("filesystem roots must be distinct absolute paths")
                key = str(Path(root).resolve()).casefold()
                if key in seen:
                    raise ValueError("filesystem roots must be distinct absolute paths")
                seen.add(key)
        if set(x.casefold() for x in fs.get("read_roots", [])) & set(x.casefold() for x in fs.get("write_roots", [])):
            raise ValueError("read and write roots overlap")
    return value


def build_argv(request: Mapping[str, Any]) -> list[str]:
    """Use only documented non-interactive flags and a stdin prompt sentinel."""
    validate_execution_binding(request)
    argv = [request["codex_path"], "--ask-for-approval", request["approval_policy"], "exec",
            "--json", "--color", "never", "--output-last-message", request["final_path"],
            "--model", request["model"], "--cd", request["cwd"],
            "--strict-config", "--config", 'model_reasoning_effort="' + request["effort"] + '"',
            "--config", "project_doc_max_bytes=0",
            "--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check"]
    if "output_schema_path" in request:
        argv.extend(["--output-schema", request["output_schema_path"]])
    if "windows_sandbox" in request:
        argv.extend(["--config", 'windows.sandbox="' + request["windows_sandbox"] + '"'])
    if "control_binding" in request:
        control = ControlTransport.mcp_server_config(request["control_binding"])
        argv.extend(["--config", "mcp_servers.execution_control.command=" + json.dumps(control["command"], ensure_ascii=False),
                     "--config", "mcp_servers.execution_control.args=" + json.dumps(control["args"], ensure_ascii=False)])
    scholarly = request.get("scholarly_server")
    if scholarly is not None:
        server = validate_scholarly_server(scholarly)
        data_dir = str((Path(request["cwd"]).resolve() / "scholarly-data"))
        args = [*server["args"], "--data-dir", data_dir]
        argv.extend(["--config", "mcp_servers.scholarly.command=" + json.dumps(server["command"], ensure_ascii=False),
                     "--config", "mcp_servers.scholarly.args=" + json.dumps(args, ensure_ascii=False)])
    if "filesystem" in request:
        fs = request["filesystem"]; entries = {'":minimal"': '"read"'}
        for field, mode in (("read_roots", "read"), ("write_roots", "write"), ("deny_roots", "deny")):
            for root in fs.get(field, []): entries[json.dumps(Path(root).resolve().as_posix(), ensure_ascii=False)] = '"' + mode + '"'
        inline = "{" + ",".join(key + "=" + value for key, value in entries.items()) + "}"
        argv.extend(["--config", 'default_permissions="do_math"', "--config", "permissions.do_math.filesystem=" + inline,
                     "--config", "permissions.do_math.network.enabled=false"])
    else:
        argv.extend(["--sandbox", request["sandbox"]])
    return [*argv, "-"]


def _write_status(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        temporary = Path(handle.name)
    os.replace(temporary, path)


def run(request_path: Path) -> int:
    request = load_request(request_path)
    request_bytes = request_path.read_bytes()
    prompt = Path(request["prompt_path"]).read_bytes()
    schema = Path(request["output_schema_path"]).read_bytes() if "output_schema_path" in request else None
    stdout_path, stderr_path, status_path = (Path(request[name]) for name in ("stdout_path", "stderr_path", "status_path"))
    for path in (stdout_path, stderr_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    command = build_argv(request)
    status: dict[str, Any] = {"argv_sha256": hashlib.sha256("\0".join(command).encode("utf-8")).hexdigest(),
                              "state": "starting", "cli_exit_code": None,
                              "request_sha256": hashlib.sha256(request_bytes).hexdigest(),
                              "stdin_sha256": hashlib.sha256(prompt).hexdigest(),
                              "schema_sha256": None if schema is None else hashlib.sha256(schema).hexdigest()}
    status.update({key: request[key] for key in ("execution_id", "profile_ref") if key in request})
    environment = sanitized_environment()
    temporary = Path(request["cwd"]) / ".scratch" / ".execution-temp"
    temporary.mkdir(parents=True, exist_ok=True)
    environment.update(TEMP=str(temporary.resolve()), TMP=str(temporary.resolve()))
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                       cwd=request["cwd"], env=environment, shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            try:
                process.communicate(input=prompt, timeout=request["max_runtime_seconds"])
                status.update(state="exited", cli_exit_code=process.returncode)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                status.update(state="timeout", cli_exit_code=process.returncode, runner_stop_required=True)
    except BaseException as exc:
        status.update(state="worker_error", error_type=type(exc).__name__)
    _write_status(status_path, status)
    return 0


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        raise SystemExit("usage: codex_worker.py REQUEST.json")
    return run(Path(arguments[0]))


if __name__ == "__main__":
    raise SystemExit(main())
