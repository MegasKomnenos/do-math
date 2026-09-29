"""The request rules every CLI worker checks inside its Job, and the command a checked request becomes (layer 1).

A worker (``codex_worker``, ``claude_worker``) is a direct Python root inside
its Windows Job and imports this module by bare name; the engine side imports it
from the package. The rules decide only from the request: its fields, the
execution binding, the resource limits, the control binding and each provider's
own fields. The argv assembly takes what it needs from outside as values: the
control server command, the scholarly data directory and the output schema.
Reading files and running the CLI stay with the workers.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import struct
from typing import Any, Mapping

try:  # The package module, or a bare sibling inside the worker's Job.
    from do_math.control_protocol import BINDING_FIELDS, CONTROL_SERVER
    from do_math.scholarly import validate_scholarly_server
    from do_math.values import validate_profile_ref
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regressions.
    from control_protocol import BINDING_FIELDS, CONTROL_SERVER
    from scholarly import validate_scholarly_server
    from values import validate_profile_ref


# Request fields every worker binds to its status, and the collector compares.
STATUS_BINDING_KEYS = ("execution_id", "profile_ref")
COMMON_REQUIRED = frozenset({"prompt_path", "cwd", "model", "effort", "max_runtime_seconds",
                             "stdout_path", "stderr_path", "status_path"})
COMMON_OPTIONAL = frozenset({"output_schema_path", "scholarly_server", "execution_id", "profile_ref",
                             "control_binding", "resource_limits"})
# Environment names every CLI may keep; a provider adds its own login and configuration names.
ENV_ALLOWLIST = frozenset({"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME",
                           "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "PROGRAMFILES",
                           "PROGRAMFILES(X86)", "COMMONPROGRAMFILES", "OS", "HOMEDRIVE", "HOMEPATH"})


def allowed_names(source: Mapping[str, str], extra: frozenset[str]) -> dict[str, str]:
    """The entries of ``source`` whose names are allowed, with a provider's ``extra`` names."""
    allowed = ENV_ALLOWLIST | extra
    return {key: value for key, value in source.items() if key.upper() in allowed}


def validate_resource_limits(value):
    """Job limits: positive commit bytes within the native size type, and a CPU hard cap in basis points."""
    if value is None:
        return None
    if (not isinstance(value, Mapping) or set(value) != {"memory_bytes", "cpu_rate_basis_points"}
            or any(type(v) is not int or v <= 0 for v in value.values())
            or value["memory_bytes"] > (1 << (8 * struct.calcsize("N"))) - 1
            or value["cpu_rate_basis_points"] > 10000):
        raise ValueError("Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000")
    return dict(value)


def validate_control_binding(binding: Any, *, execution_id: str, cwd: str | None = None) -> None:
    """A worker's binding names this execution, an absolute endpoint and, when given, its cwd."""
    if (not isinstance(binding, dict) or set(BINDING_FIELDS) - set(binding)
            or set(binding) - set(BINDING_FIELDS) - {"workspace", "self_check"}
            or binding.get("self_check", True) is not True
            or any(not isinstance(binding[key], str) or not binding[key].strip() or "\0" in binding[key]
                   for key in BINDING_FIELDS)
            or binding["execution_id"] != execution_id
            or not Path(binding["endpoint"]).is_absolute()):
        raise ValueError("control binding must identify this execution and an absolute local endpoint")
    if "workspace" in binding:
        workspace = binding["workspace"]
        if (not isinstance(workspace, str) or not workspace.strip() or "\0" in workspace
                or not Path(workspace).is_absolute()):
            raise ValueError("control binding workspace must be an absolute local path")
        if cwd is not None and (not isinstance(cwd, str) or not cwd.strip() or "\0" in cwd
                or not Path(cwd).is_absolute()
                or Path(workspace).resolve() != Path(cwd).resolve()):  # layer: resolves links to compare the two paths; nothing is written
            raise ValueError("control binding workspace differs from execution cwd")


def validate_execution_binding(request):
    fields = {"execution_id", "profile_ref", "control_binding", "resource_limits"}
    if not fields.intersection(request):
        return
    if not isinstance(request.get("execution_id"), str) or not request["execution_id"].strip():
        raise ValueError("worker execution binding requires exact execution_id and profile_ref")
    try:
        validate_profile_ref(request.get("profile_ref"))
    except ValueError:
        raise ValueError("worker execution binding requires exact execution_id and profile_ref") from None
    if "resource_limits" in request:
        if request["resource_limits"] is None:
            raise ValueError("explicit resource limits cannot be null")
        validate_resource_limits(request["resource_limits"])
    if "control_binding" in request:
        validate_control_binding(request["control_binding"], execution_id=request["execution_id"],
                                 cwd=request.get("cwd"))


def validate_max_runtime(timeout: Any) -> None:
    """A CLI runtime limit is a positive finite number of seconds, or none."""
    if timeout is not None and (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("max_runtime_seconds must be positive and finite or null")


def check_common_request(value: Any, *, required: frozenset, optional: frozenset) -> dict[str, Any]:
    """Check the request fields both workers share, then the provider's extra names."""
    if not isinstance(value, dict):
        raise ValueError("worker request must be an object")
    required, optional = COMMON_REQUIRED | required, COMMON_OPTIONAL | optional
    missing = sorted(required - set(value))
    if missing:
        raise ValueError("worker request misses " + ", ".join(missing))
    unknown = sorted(set(value) - required - optional)
    if unknown:
        raise ValueError("unknown worker request fields: " + ", ".join(unknown))
    validate_execution_binding(value)
    for key in (required - {"max_runtime_seconds"}) | ({"output_schema_path"} & set(value)):
        if not isinstance(value[key], str) or not value[key].strip() or "\0" in value[key]:
            raise ValueError(key + " must be a nonempty NUL-free string")
    validate_max_runtime(value["max_runtime_seconds"])
    if value.get("scholarly_server") is not None:
        value["scholarly_server"] = validate_scholarly_server(value["scholarly_server"])
    return value

CODEX_EFFORTS = frozenset({"minimal", "low", "medium", "high", "xhigh", "max", "ultra"})
CODEX_SANDBOXES = frozenset({"read-only", "workspace-write", "danger-full-access"})
CODEX_WINDOWS_SANDBOXES = frozenset({"unelevated", "elevated"})


def check_codex_request(value: Any) -> dict[str, Any]:
    """A Codex worker request: the shared fields, then Codex's effort, approval and sandbox fields."""
    value = check_common_request(value,
                                 required=frozenset({"codex_path", "approval_policy", "sandbox", "final_path"}),
                                 optional=frozenset({"windows_sandbox"}))
    if value["effort"] not in CODEX_EFFORTS or value["approval_policy"] != "never":
        raise ValueError("unsupported effort or approval policy")
    if value["sandbox"] not in CODEX_SANDBOXES:
        raise ValueError("a supported sandbox is required")
    if "windows_sandbox" in value and value["windows_sandbox"] not in CODEX_WINDOWS_SANDBOXES:
        raise ValueError("windows_sandbox must be elevated or unelevated when present")
    return value


def codex_argv(request: Mapping[str, Any], *, control: dict | None, data_dir: str | None) -> list[str]:
    """Only documented non-interactive flags and a stdin prompt sentinel, for a checked request.

    ``control`` is the control server's command when the request is bound, and
    ``data_dir`` the scholarly data directory when it names a scholarly server.
    """
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
        argv.extend(["--config", f"mcp_servers.{CONTROL_SERVER}.command=" + json.dumps(control["command"], ensure_ascii=False),
                     "--config", f"mcp_servers.{CONTROL_SERVER}.args=" + json.dumps(control["args"], ensure_ascii=False)])
    server = request.get("scholarly_server")
    if server is not None:
        args = [*server["args"], "--data-dir", data_dir]
        argv.extend(["--config", "mcp_servers.scholarly.command=" + json.dumps(server["command"], ensure_ascii=False),
                     "--config", "mcp_servers.scholarly.args=" + json.dumps(args, ensure_ascii=False)])
    argv.extend(["--sandbox", request["sandbox"]])
    return [*argv, "-"]


CLAUDE_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})


def check_claude_request(value: Any) -> dict:
    """A Claude worker request: the shared fields, then Claude's schema, effort and model-lock fields."""
    request = check_common_request(value, required=frozenset({"claude_path"}),
                                   optional=frozenset({"claude_only_assigned_model"}))
    if "output_schema_path" not in request and "control_binding" not in request:
        raise ValueError("an unbound Claude worker requires its structured final schema")
    if request["effort"] not in CLAUDE_EFFORTS:
        raise ValueError("Claude effort must be low, medium, high, xhigh or max")
    if not isinstance(request.get("claude_only_assigned_model", False), bool):
        raise ValueError("claude_only_assigned_model must be a boolean")
    if request.get("claude_only_assigned_model") and not request["model"].startswith("claude-"):
        raise ValueError("claude_only_assigned_model requires a full Claude model ID")
    return request


def claude_argv(request: dict, *, control: dict | None, data_dir: str | None, schema: dict | None) -> list[str]:
    """The Claude print command for a checked request.

    ``control`` and ``data_dir`` are as for ``codex_argv``; ``schema`` is the
    parsed output schema when the request names one.
    """
    settings = {"disableAllHooks": True, "autoMemoryEnabled": False}
    if request.get("claude_only_assigned_model", False):
        model = request["model"]
        settings.update(availableModels=[model], fallbackModel=[], switchModelsOnFlag=False,
                        env={"ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})
    servers = {}
    if "control_binding" in request:
        servers[CONTROL_SERVER] = control
    server = request.get("scholarly_server")
    if server is not None:
        servers["scholarly"] = {**server, "args": [*server["args"], "--data-dir", data_dir]}
    # Keep subscription login; --bare deliberately disables OAuth login.
    argv = [request["claude_path"], "--print", "--output-format", "stream-json", "--verbose",
            "--model", request["model"], "--effort", request["effort"],
            "--no-session-persistence", "--setting-sources", "",
            "--settings", json.dumps(settings),
            "--disable-slash-commands", "--disallowedTools", "Agent,Task",
            "--strict-mcp-config", "--mcp-config", json.dumps({"mcpServers": servers}, ensure_ascii=False),
            "--permission-mode", "bypassPermissions"]
    if "output_schema_path" in request:
        if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema":
            schema.pop("$schema")
        schema.pop("x-contract-id", None)
        argv.extend(["--json-schema", json.dumps(schema, ensure_ascii=False)])
    return argv
