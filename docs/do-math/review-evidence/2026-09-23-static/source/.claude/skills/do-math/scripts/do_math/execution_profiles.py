"""Immutable execution contracts; configuration is only a profile authoring input.

Instruction boundaries organize cooperating sessions. They provide neither OS
isolation nor authenticated transport between processes of the same user.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

from .model_policy import ROLE_TIERS, TIERS
from .state_contract import STATE_FORMAT_VERSION

WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}
MACHINE_ROLES = {"formal_check", "trust_check", "trust_activate", "external_action"}
OBSERVATION_KEYS = ("observation_interval_seconds", "observation_idle_seconds",
                    "observation_unbounded_wait_seconds", "max_observation_reviews", "checkpoint_grace_seconds",
                    "self_check_response_window_seconds", "tool_review_window_seconds")
WINDOW_KEYS = ("call_timeout_seconds", "finish_notice_seconds")
LEGACY_WINDOW_KEYS = ("run_timeout_seconds", "dispatch_reserve_seconds")
BOUNDARY = {"mode": "instructions", "os_isolation": False, "authenticated_caller": False,
            "rules": ["Use only assigned inputs, allowed queries and your execution workspace.",
                      "Do not read other reviewers' private work or modify central records directly.",
                      "Submit proposals through the execution's supplied submission tools.",
                      "Do not issue user controls or expand research goals, budgets or external authority."]}


def _digest(value):
    from .repository import canonical_json
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _research_observation_rule_contract() -> list[dict]:
    from .observations import observation_rule_contract
    return observation_rule_contract()


def seal_profile(body: dict) -> dict:
    """Create a new immutable edition; never edit an existing registered row."""
    value = deepcopy(body)
    value.pop("id", None)
    value.pop("sha256", None)
    value.setdefault("revision", 1)
    value.setdefault("feature_version", STATE_FORMAT_VERSION)
    digest = _digest(value)
    value.update(id="EP-" + digest, sha256=digest)
    validate_profile(value)
    return value


def profile_ref(profile: dict) -> dict:
    validate_profile(profile)
    return {key: profile[key] for key in ("id", "revision", "sha256")}


def validate_profile(profile: dict) -> None:
    body = {key: value for key, value in profile.items() if key not in {"id", "sha256"}}
    digest = _digest(body)
    if profile.get("sha256") != digest or profile.get("id") != "EP-" + digest:
        raise ValueError("execution profile content differs from its immutable identity")
    if profile.get("feature_version") != STATE_FORMAT_VERSION or type(profile.get("revision")) is not int or profile["revision"] < 1:
        raise ValueError("unsupported profile edition")
    role, actor = profile.get("role"), profile.get("actor_kind")
    if actor not in {"ai", "machine"} or profile.get("budget_kind") not in {"work", "operations"}:
        raise ValueError("profile requires an actor and budget kind")
    if actor == "machine":
        if role not in MACHINE_ROLES or "ai" in profile:
            raise ValueError("machine profile cannot contain AI fields")
    elif not isinstance(profile.get("ai"), dict) or not profile["ai"].get("model"):
        raise ValueError("AI profile requires a model")
    expected_mode = ("deadline_only" if actor == "machine" or profile["budget_kind"] == "operations"
                     else None if role == "research_work" else "periodic")
    mode = profile.get("observation", {}).get("mode")
    if mode not in {"event_driven", "periodic", "deadline_only"} or expected_mode and mode != expected_mode:
        raise ValueError("observation mode differs from role responsibility")
    bindings = profile.get("observation", {}).get("rule_bindings")
    if role == "research_work":
        from .observations import validate_observation_rule_contract
        validate_observation_rule_contract(bindings)
    elif bindings != []:
        raise ValueError("profile observation bindings differ from the supported role contract")
    if profile.get("boundary") != BOUNDARY:
        raise ValueError("this implementation supports only the declared instruction boundary")
    host = profile.get("host_resources")
    if host is not None:
        if (set(host) != {"constraint_id", "scope", "host_id", "demands"}
                or host["scope"] != "instance_on_host" or not isinstance(host["host_id"], str) or not host["host_id"]
                or profile.get("host_capacity_refs") != [host["constraint_id"]]
                or profile.get("host_capacity_status") != "adopted_local_job_limits"):
            raise ValueError("host profile requires one exact local instance constraint")
        _host_amounts(host["demands"], demand=True)
    elif profile.get("host_capacity_refs"):
        raise ValueError("host references require pinned execution demands")


def _host_amounts(value, *, demand=False):
    units = {"jobs", "memory_bytes", "cpu_rate_basis_points"}
    if not isinstance(value, dict) or set(value) != units:
        raise ValueError("host amounts require explicit jobs, memory_bytes and cpu_rate_basis_points")
    if any(type(v) is not int or v < (1 if demand else 0) for v in value.values()):
        raise ValueError("host amounts must be explicit nonnegative integers (positive for a demand)")
    if value["cpu_rate_basis_points"] > 10000 or demand and value["jobs"] != 1:
        raise ValueError("CPU cap must be at most 10000 and one execution owns one simultaneous Job tree")


def host_constraint(*, host_id: str, limits: dict, control_reserve: dict, authority_refs: list) -> dict:
    """Author an explicit instance-local approval; no host-wide coordinator exists.

    The controller's reserve cannot be borrowed by any admitted child Job.
    CPU is a hard cap relative to an enclosing rate-controlled Job, not a
    processing guarantee. Memory is committed virtual memory, not RSS.
    """
    _host_amounts(limits)
    _host_amounts(control_reserve)
    if (not isinstance(host_id, str) or not host_id.strip() or not isinstance(authority_refs, list)
            or not authority_refs or any(not isinstance(ref, str) or not ref.strip() for ref in authority_refs)
            or any(control_reserve[k] > limits[k] for k in limits)):
        raise ValueError("host constraint needs host, approval and reserve within the adopted limits")
    body = {"kind": "host", "scope": "instance_on_host", "host_id": host_id,
            "max_jobs": limits["jobs"], "memory_bytes": limits["memory_bytes"],
            "cpu_rate_basis_points": limits["cpu_rate_basis_points"],
            "control_reserve": deepcopy(control_reserve), "authority_refs": deepcopy(authority_refs)}
    return {"id": "CP-" + _digest(body), **body}


def validate_host_constraint(constraint: dict) -> None:
    expected = host_constraint(host_id=constraint.get("host_id"),
        limits={"jobs": constraint.get("max_jobs"), "memory_bytes": constraint.get("memory_bytes"),
                "cpu_rate_basis_points": constraint.get("cpu_rate_basis_points")},
        control_reserve=constraint.get("control_reserve"), authority_refs=constraint.get("authority_refs"))
    if expected != constraint:
        raise ValueError("host constraint differs from its approved immutable edition")


def with_host_resources(profile: dict, constraint: dict, demands: dict) -> dict:
    validate_profile(profile)
    validate_host_constraint(constraint)
    _host_amounts(demands, demand=True)
    body = deepcopy(profile)
    body.update(host_capacity_refs=[constraint["id"]], host_capacity_status="adopted_local_job_limits",
                host_resources={"constraint_id": constraint["id"], "scope": constraint["scope"],
                                "host_id": constraint["host_id"], "demands": deepcopy(demands)})
    return seal_profile(body)


def job_resource_limits(profile: dict) -> dict | None:
    """Exact per-execution Job settings, never the shared approval ceiling."""
    import platform
    validate_profile(profile)
    host = profile.get("host_resources")
    if host is None:
        return None
    if host["host_id"] != platform.node():
        raise ValueError("profile host differs from this local host")
    return {key: host["demands"][key] for key in ("memory_bytes", "cpu_rate_basis_points")}


def build_profiles(config: dict) -> dict:
    """Freeze adopted values. No new capacity, permission or measured limit is invented."""
    limits = config.get("session_limits")
    if limits is not None and not isinstance(limits, dict):
        raise ValueError("session limits must be a mapping or explicit call-budget mode")
    constraints = {}
    adopted_host = config.get("host_resources")
    if adopted_host is not None:
        if not isinstance(adopted_host, dict) or set(adopted_host) != {"constraint", "demands_by_role"}:
            raise ValueError("host authoring requires an approved constraint and explicit demands_by_role")
        validate_host_constraint(adopted_host["constraint"])
        constraints[adopted_host["constraint"]["id"]] = deepcopy(adopted_host["constraint"])
    usage_refs = {}
    if limits is None:
        for pool in ("work", "operations"):
            maximum = config[pool + "_calls"]
            if maximum is not None and (type(maximum) is not int or maximum < 0):
                raise ValueError("call budget must be nonnegative or unlimited")
            body = {"kind": "cumulative", "budget_kind": pool, "unit": "local_execution_attempt",
                    "limit": {"kind": "unlimited"} if maximum is None else {"kind": "bounded", "value": maximum},
                    "scope": "admitted_local_attempts_not_provider_operations"}
            identifier = "CP-" + _digest(body)
            constraints[identifier] = {"id": identifier, **body}
            usage_refs[pool] = [identifier]
    for model in sorted(set(limits["work"]) | set(limits["operations"])) if limits is not None else ():
        work, operations = limits["work"].get(model, 0), limits["operations"].get(model, 0)
        if any(type(n) is not int or n < 0 for n in (work, operations)):
            raise ValueError("session capacity must be a nonnegative integer")
        identifier = "CP-" + _digest({"model": model, "work": work, "operations": operations})
        constraints[identifier] = {"id": identifier, "kind": "concurrency", "model": model,
            "accounting_unit": "execution", "work_slots": work, "operations_slots": operations,
            "total_slots": work + operations, "scope": "local_execution_not_provider_operations"}
    profiles, refs = {}, {}
    lean = _lean_contract(config)
    for role in sorted((set(ROLE_TIERS) - {"independent_operator"}) | MACHINE_ROLES | {"recovery"}):
        machine = role in MACHINE_ROLES
        pool = "work" if role in WORK_ROLES else "operations"
        mode = (config["observation_mode"] if role == "research_work" else
                "periodic" if pool == "work" else "deadline_only")
        for tier in ((None,) if machine or limits is None else TIERS):
            body = {"role": role, "actor_kind": "machine" if machine else "ai", "budget_kind": pool,
                    "boundary": deepcopy(BOUNDARY), "host_capacity_refs": [],
                    "host_capacity_status": "unmeasured_not_enforced",
                    "observation": {"mode": mode, "settings": {k: deepcopy(config[k]) for k in OBSERVATION_KEYS if k in config},
                                    "rule_bindings": deepcopy(_research_observation_rule_contract() if role == "research_work" else [])},
                    # Retain old, explicitly stored fields only to reconstruct
                    # their immutable profile IDs. They have no runtime effect.
                    "window": {k: deepcopy(config[k]) for k in (*WINDOW_KEYS, *LEGACY_WINDOW_KEYS) if k in config},
                    "input": {"max_input_bytes": config["max_input_bytes"], "unit": "utf8_bytes",
                              "provider_context_capacity": "unknown"},
                    "required_capabilities": [] if machine else ["jsonl", "model", "structured_output"],
                    "capability_evidence_refs": []}
            if machine and role in {"formal_check", "trust_check", "trust_activate"}:
                body["machine"] = deepcopy(lean)
            if not machine:
                model = (config["tier_models"][tier] if limits is not None else
                         config["operator_model"] if role == "recovery" else
                         config.get("role_models", {}).get(role, config["model"]))
                capacity = next((c["id"] for c in constraints.values() if c.get("model") == model), None)
                if limits is not None and capacity is None:
                    raise ValueError("tier model has no adopted capacity")
                provider = "claude" if model.startswith(("claude:", "claude-")) else "codex"
                body["ai"] = {"model": model, "tier": tier, "provider": provider,
                              "effort": config["operator_effort"] if role == "recovery" else config["effort"],
                              "capacity_refs": [capacity] if capacity else [], "usage_constraint_ids": usage_refs.get(pool, []),
                              "provider_operations": "unknown", "remote_termination": "unknown",
                              "maximum_output_enforced": False,
                              "claude_only_assigned_model": config.get("claude_only_assigned_model", False),
                              "scholarly_server": deepcopy(config.get("scholarly_server")) if config.get("scholarly_enabled", True) else None}
                if role == "recovery":
                    body["window"]["call_timeout_seconds"] = config["operator_timeout_seconds"]
            profile = seal_profile(body)
            if adopted_host is not None:
                if role not in adopted_host["demands_by_role"]:
                    raise ValueError("every role needs an explicit host demand in an adopted shared scope")
                if role not in {"formal_check", "trust_check", "trust_activate"}:
                    profile = with_host_resources(profile, adopted_host["constraint"], adopted_host["demands_by_role"][role])
            profiles[profile["id"]] = profile
            refs.setdefault(role, []).append(profile_ref(profile))
    result = {"execution_profiles": profiles, "capacity_constraints": constraints, "role_profile_refs": refs}
    if adopted_host is not None:
        result["host_capacity_ref"] = adopted_host["constraint"]["id"]
    return result


def resolve_profile(profiles: dict, reference: dict) -> dict:
    if not isinstance(reference, dict) or set(reference) != {"id", "revision", "sha256"}:
        raise ValueError("profile reference requires exact id, revision and sha256")
    profile = profiles.get(reference["id"])
    if profile is None or profile_ref(profile) != reference:
        raise ValueError("profile reference is absent or stale")
    return deepcopy(profile)


def select_profile(profiles: dict, action: dict, selection: dict, allowed_refs=None) -> dict:
    requested = action.get("profile_ref") or selection.get("profile_ref")
    # A content-addressed ID is itself immutable. Task contracts use these IDs;
    # execution records still receive the complete checked edition reference.
    allowed = None if allowed_refs is None else [profile_ref(resolve_profile(profiles,
        profile_ref(profiles[r]) if isinstance(r, str) and r in profiles else r)) for r in allowed_refs]
    candidates = ([resolve_profile(profiles, requested)] if requested else
                  [resolve_profile(profiles, profile_ref(p)) for p in profiles.values()])
    candidates = [p for p in candidates if p["role"] == action["role"]
                  and (p["actor_kind"] == "machine" or p["ai"]["model"] == selection["model"])
                  and (requested or p.get("ai", {}).get("tier") is None or not selection.get("tier")
                       or p["ai"]["tier"] == selection["tier"])
                  and (allowed is None or profile_ref(p) in allowed)]
    if len(candidates) != 1:
        raise ValueError("profile selection must resolve to exactly one permitted role/model edition")
    return candidates[0]


def bind_execution(execution: dict, profile: dict) -> dict:
    reference = profile_ref(profile)
    if execution.get("role") != profile["role"]:
        raise ValueError("execution role differs from profile")
    if execution.get("execution_profile_ref", reference) != reference:
        raise ValueError("an execution cannot change its profile")
    execution["execution_profile_ref"] = reference
    return execution


def runtime_config(profile: dict) -> dict:
    validate_profile(profile)
    window = {key: value for key, value in profile["window"].items() if key not in LEGACY_WINDOW_KEYS}
    return deepcopy({**window, **profile["observation"]["settings"],
                     "observation_mode": profile["observation"]["mode"],
                     "max_input_bytes": profile["input"]["max_input_bytes"]})


def _lean_contract(config: dict) -> dict:
    from .formal import discover_lean
    command = deepcopy(config.get("lean_command") or discover_lean())
    return {"lean_command": command, "lean_timeout_seconds": None,
            "tool_manifest": _command_manifest(command),
            "tool_manifest_scope": "local_command_files_and_checker_not_dependency_closure"}


def _command_manifest(command) -> list:
    if not command:
        return []
    # Preserve adopted argv, but bind its current executable resolution too.
    parts = [shutil.which(command[0]) or command[0], *command[1:]]
    paths = [Path(part).resolve() for part in parts if Path(part).is_file()]
    paths.append(Path(__file__).with_name("formal.py").resolve())
    return [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in dict.fromkeys(paths)]


def machine_invocation(profile: dict, *, trust_environment: dict, on_started=None) -> dict:
    """Use the frozen command/deadline with the separately approved trust edition."""
    validate_profile(profile)
    machine = profile.get("machine", {})
    command = machine.get("lean_command")
    if profile["actor_kind"] != "machine" or not command:
        raise ValueError("profile has no pinned Lean command")
    if _command_manifest(command) != machine["tool_manifest"]:
        raise ValueError("profile tool resolution or edition changed")
    toolchain = trust_environment["toolchain"]
    if command != toolchain.get("configured_command"):
        raise ValueError("profile command differs from the approved trust environment")
    if profile.get('host_resources'):
        raise ValueError('Lean profiles with host resource caps must be replaced by an uncapped profile')
    arguments = {"lean_command": deepcopy(command), "timeout_seconds": None,
                 "expected_toolchain": deepcopy(toolchain)}
    if on_started is not None:
        arguments['on_started'] = on_started
    return arguments


def runner_tools(profile: dict) -> dict:
    validate_profile(profile)
    return deepcopy({key: profile["ai"][key] for key in ("scholarly_server", "claude_only_assigned_model")})


def prepare_prompt(prompt: str, profile: dict) -> str:
    """Complete raw role input before its owner measures and seals UTF-8 bytes."""
    return prompt + boundary_prompt(profile)


def prompt_seal(prompt: str) -> dict:
    raw = prompt.encode("utf-8")
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def execution_observation(result: dict) -> dict | None:
    """Preserve reported numbers losslessly without admitting floats to Git state."""
    observation = result.get("provider_observation")
    if not isinstance(observation, dict):
        return None
    return {"stop_reason": deepcopy(observation.get("stop_reason", "unknown")),
            "reported_fields_json": json.dumps(observation, ensure_ascii=False, allow_nan=False),
            "scope": "provider_report_not_remote_termination_or_invoice"}


def structural_failure_evidence(profile: dict, identity: dict, *, observed_at: str,
                                execution_id: str, evidence_ref: str, capability: str = "atomic_local_job") -> dict:
    if capability not in {"atomic_local_job", "local_job_resources"}:
        raise ValueError("unsupported local structural capability")
    record = capability_evidence(profile, {"identity": identity, "verified": True,
        "scope": "actual_local_start_failure", "supported": {capability: False}}, observed_at=observed_at)
    record["capabilities"][capability].update(execution_id=execution_id, evidence_ref=evidence_ref)
    record["id"] = "CE-" + _digest({k: v for k, v in record.items() if k != "id"})
    return record


def boundary_prompt(profile: dict) -> str:
    validate_profile(profile)
    # Preserve the sealed profile; render its delivery rule through the current
    # central interface. Reviewer isolation and authority rules stay exact.
    rules = ["Deliver proposals as a normal JSON final, or use the supplied tools for optional early submission."
             if rule == "Submit proposals through the execution's supplied submission tools." else rule
             for rule in profile["boundary"]["rules"]]
    return "\n\nExecution boundary (instructions; not OS isolation):\n" + "\n".join(rules)


def register_families(contract) -> None:
    """Register our owned families with STORAGE before initialize/load/save."""
    from .budget import _validate_reservation
    for root, name, validator, references in (
            ("research", "execution_profiles", validate_profile,
             lambda p: p.get("ai", {}).get("capacity_refs", []) + p.get("ai", {}).get("usage_constraint_ids", []) + p.get("host_capacity_refs", [])),
            ("research", "capacity_constraints", None, None),
            ("research", "capability_evidence", None, lambda r: [r["execution_profile_ref"]["id"]]),
            ("runtime", "reservations", _validate_reservation,
             lambda r: [r["constraint_id"], r["owner_id"]] + [a["id"] for a in r["authority_refs"]]),
            ("runtime", "provider_waits", None, None)):
        if contract.family(root, name) is None:
            contract.register_family(root, name, validator=validator, references=references)


def capability_evidence(profile: dict, description: dict, *, observed_at: str) -> dict:
    """Bind command-surface facts to one profile, host and exact implementation.

    Help text is not a process-lifetime, isolation, or provider-behavior test.
    Those claims need independently supplied evidence from their actual probes.
    """
    reference = profile_ref(profile)
    if not description.get("identity") or not observed_at:
        raise ValueError("capability evidence requires current identity and observation time")
    names = set(description.get("supported", {})) | set(description.get("unknown", []))
    surface = {"jsonl", "model", "structured_output", "effort_via_config", "sandbox"}
    facts = {}
    for name in sorted(names):
        supported = description.get("supported", {}).get(name)
        status = ("supported" if supported is True and description.get("verified") is True else
                  "unsupported" if supported is False and description.get("verified") is True else "unknown")
        if description.get("scope") == "cli_command_surface_only" and name not in surface:
            status = "unknown"
        facts[name] = {"status": status, "scope": description.get("scope", "unknown")}
    record = {"execution_profile_ref": reference, "identity": deepcopy(description["identity"]),
              "observed_at": observed_at, "capabilities": facts,
              "version_sha256": description.get("version_sha256"),
              "help_sha256": description.get("exec_help_sha256"),
              "boundary": "instructions_not_os_isolation"}
    record["id"] = "CE-" + _digest(record)
    return record
