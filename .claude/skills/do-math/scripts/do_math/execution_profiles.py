"""Immutable execution contracts; configuration is only a profile authoring input.

Instruction boundaries organize cooperating sessions. They provide neither OS
isolation nor authenticated transport between processes of the same user.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .values import validate_profile_ref
from .model_policy import ROLE_TIERS, TIERS
from .canonical import exact_content_hash
from .provider_wait import provider_for

# Only work roles reserve a model slot; operational AI roles run on their pinned
# model without a reservation, and machine roles use host limits alone.
WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}
# Roles whose action works on its target task: the task's end makes the action obsolete.
TASK_TARGET_ROLES = frozenset({"research_work", "supplemental_research", "task_contract_review"})
# Roles whose output is task research, and the roles that prepare and plan tasks.
RESEARCH_PRODUCER_ROLES = frozenset({"research_work", "supplemental_research"})
PLANNING_ROLES = frozenset({"research_preparation", "research_plan"})
# Roles that run while an instance initializes: an initial grant authorizes no other role.
INITIAL_ROLES = frozenset({"intent_interpretation", "maintenance"})
MACHINE_ROLES = {"formal_check", "trust_check", "trust_activate", "external_action"}
# Machine roles that run a Lean command in a native Job.
LEAN_ROLES = {"formal_check", "trust_check"}
# Roles without a host resource cap: the approved trust environment bounds them.
UNCAPPED_ROLES = LEAN_ROLES | {"trust_activate"}
OBSERVATION_KEYS = ("observation_interval_seconds",
                    "self_check_response_window_seconds", "tool_review_window_seconds")
WINDOW_KEYS = ("call_timeout_seconds", "finish_notice_seconds")
# The observation modes a profile may pin (profile ``observation.mode``).
OBSERVATION_MODES = ("event_driven", "periodic", "deadline_only")
PROFILE_ROLES = set(ROLE_TIERS) | MACHINE_ROLES
HOST_ROLES = PROFILE_ROLES - UNCAPPED_ROLES
BOUNDARY = {"mode": "instructions", "os_isolation": False, "authenticated_caller": False,
            "rules": ["Use only assigned inputs, allowed queries and your execution workspace.",
                      "Do not read other reviewers' private work or modify central records directly.",
                      "Deliver proposals as a normal JSON final, or use the supplied tools for optional early submission.",
                      "Do not issue user controls or expand research goals, budgets or external authority."]}


def task_research(action: dict) -> bool:
    """A research producer's work on its task, not supplemental research a review cycle requested."""
    return action.get("role") in RESEARCH_PRODUCER_ROLES and not action.get("review_cycle_id")


def review_research(action: dict) -> bool:
    """Supplemental research that a review cycle requested for its proposal."""
    return action.get("role") == "supplemental_research" and bool(action.get("review_cycle_id"))


def _research_observation_rule_contract() -> list[dict]:
    from .observations import observation_rule_contract
    return observation_rule_contract()


def seal_profile(body: dict) -> dict:
    """Create a new immutable edition; never edit an existing registered row."""
    value = deepcopy(body)
    value.pop("id", None)
    value.pop("sha256", None)
    value.setdefault("revision", 1)
    digest = exact_content_hash(value)
    value.update(id="EP-" + digest, sha256=digest)
    validate_profile(value)
    return value


def profile_ref(profile: dict) -> dict:
    """The reference of a stored or sealed profile; the profile is not hashed again."""
    return {key: profile[key] for key in ("id", "revision", "sha256")}


def validate_profile(profile: dict) -> None:
    body = {key: value for key, value in profile.items() if key not in {"id", "sha256"}}
    digest = exact_content_hash(body)
    if profile.get("sha256") != digest or profile.get("id") != "EP-" + digest:
        raise ValueError("execution profile content differs from its immutable identity")
    if type(profile.get("revision")) is not int or profile["revision"] < 1:
        raise ValueError("unsupported profile edition")
    role, actor = profile.get("role"), profile.get("actor_kind")
    if actor not in {"ai", "machine"}:
        raise ValueError("profile requires an actor")
    if actor == "machine":
        if role not in MACHINE_ROLES or "ai" in profile:
            raise ValueError("machine profile cannot contain AI fields")
        # Lean roles pin only the command; the approved trust environment fixes its identity.
        # Activation reads the toolchain record and needs no machine settings.
        machine = profile.get("machine")
        if (role in LEAN_ROLES and (not isinstance(machine, dict) or set(machine) != {"lean_command"})
                or role not in LEAN_ROLES and machine is not None):
            raise ValueError("machine profile settings differ from the role contract")
    elif not isinstance(profile.get("ai"), dict) or not profile["ai"].get("model"):
        raise ValueError("AI profile requires a model")
    elif bool(profile["ai"].get("capacity_refs")) != (role in WORK_ROLES):
        raise ValueError("only work roles reserve a model slot")
    expected_mode = ("deadline_only" if actor == "machine" or role not in WORK_ROLES
                     else None if role == "research_work" else "periodic")
    mode = profile.get("observation", {}).get("mode")
    if mode not in OBSERVATION_MODES or expected_mode and mode != expected_mode:
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
    return {"id": "CP-" + exact_content_hash(body), **body}


def validate_host_constraint(constraint: dict) -> None:
    if not isinstance(constraint, dict):
        raise ValueError('host constraint must be an object')
    expected = host_constraint(host_id=constraint.get("host_id"),
        limits={"jobs": constraint.get("max_jobs"), "memory_bytes": constraint.get("memory_bytes"),
                "cpu_rate_basis_points": constraint.get("cpu_rate_basis_points")},
        control_reserve=constraint.get("control_reserve"), authority_refs=constraint.get("authority_refs"))
    if expected != constraint:
        raise ValueError("host constraint differs from its approved immutable edition")


def with_host_resources(profile: dict, constraint: dict, demands: dict) -> dict:
    validate_host_constraint(constraint)
    _host_amounts(demands, demand=True)
    body = deepcopy(profile)
    body.update(host_capacity_refs=[constraint["id"]], host_capacity_status="adopted_local_job_limits",
                host_resources={"constraint_id": constraint["id"], "scope": constraint["scope"],
                                "host_id": constraint["host_id"], "demands": deepcopy(demands)})
    return seal_profile(body)


def job_resource_limits(profile: dict, *, host_id) -> dict | None:
    """Exact per-execution Job settings, never the shared approval ceiling."""
    host = profile.get("host_resources")
    if host is None:
        return None
    if host["host_id"] != host_id:
        raise ValueError("profile host differs from this local host")
    return {key: host["demands"][key] for key in ("memory_bytes", "cpu_rate_basis_points")}


def validate_host_resources(host) -> None:
    """The configuration's host section: one approved constraint and a demand for exactly the capped roles.

    Before binding, the constraint may still carry its request authority alias.
    """
    if not isinstance(host, dict) or set(host) != {"constraint", "demands_by_role"}:
        raise ValueError("host authoring requires an approved constraint and explicit demands_by_role")
    validate_host_constraint(host["constraint"])
    if not isinstance(host['demands_by_role'], dict):
        raise ValueError('host demands_by_role must be an object')
    for demands in host['demands_by_role'].values():
        _host_amounts(demands, demand=True)
    if HOST_ROLES - set(host["demands_by_role"]):
        raise ValueError("every capped role needs an explicit host demand in an adopted shared scope")
    if set(host['demands_by_role']) - HOST_ROLES:
        raise ValueError('host demands must name capped roles only')


def build_profiles(config: dict, *, host) -> dict:
    """Freeze the profile editions of every role from adopted values.

    ``host`` (the host port) discovers the Lean command when the configuration names
    none; an absent discovery result freezes no Lean command.

    No new capacity, permission or measured limit is invented.
    """
    limits = config["session_limits"]
    constraints = {}
    adopted_host = config.get("host_resources")
    if adopted_host is not None:
        validate_host_resources(adopted_host)
        constraints[adopted_host["constraint"]["id"]] = deepcopy(adopted_host["constraint"])
    for model, work in sorted(limits["work"].items()):
        identifier = "CP-" + exact_content_hash({"model": model, "work": work})
        constraints[identifier] = {"id": identifier, "kind": "concurrency", "model": model,
            "accounting_unit": "execution", "work_slots": work, "scope": "local_execution_not_provider_operations"}
    profiles, refs = {}, {}
    lean = _lean_contract(config, host)
    for role in sorted(PROFILE_ROLES):
        machine = role in MACHINE_ROLES
        mode = (config["observation_mode"] if role == "research_work" else
                "periodic" if role in WORK_ROLES else "deadline_only")
        for tier in ((None,) if machine else TIERS):
            body = {"role": role, "actor_kind": "machine" if machine else "ai",
                    "boundary": deepcopy(BOUNDARY), "host_capacity_refs": [],
                    "host_capacity_status": "unmeasured_not_enforced",
                    "observation": {"mode": mode, "settings": {k: deepcopy(config[k]) for k in OBSERVATION_KEYS if k in config},
                                    "rule_bindings": deepcopy(_research_observation_rule_contract() if role == "research_work" else [])},
                    "window": {k: deepcopy(config[k]) for k in WINDOW_KEYS if k in config},
                    "input": {"max_input_bytes": config["max_input_bytes"], "unit": "utf8_bytes",
                              "provider_context_capacity": "unknown"},
                    "required_capabilities": [] if machine else ["jsonl", "model", "structured_output"],
                    "capability_evidence_refs": []}
            if machine and role in LEAN_ROLES:
                body["machine"] = deepcopy(lean)
            if not machine:
                model = config["tier_models"][tier]
                capacity = next((c["id"] for c in constraints.values() if c.get("model") == model), None)
                if capacity is None:
                    raise ValueError("tier model has no adopted capacity")
                provider = provider_for(model)
                body["ai"] = {"model": model, "tier": tier, "provider": provider,
                              "effort": config["operator_effort"] if role == "recovery" else config["effort"],
                              "capacity_refs": [capacity] if role in WORK_ROLES else [],
                              "provider_operations": "unknown", "remote_termination": "unknown",
                              "maximum_output_enforced": False,
                              "claude_only_assigned_model": config["claude_only_assigned_model"],
                              "scholarly_server": deepcopy(config["scholarly_server"]) if config["scholarly_enabled"] else None}
                if role == "recovery":
                    body["window"]["call_timeout_seconds"] = config["operator_timeout_seconds"]
            profile = seal_profile(body)
            if adopted_host is not None and role in HOST_ROLES:
                profile = with_host_resources(profile, adopted_host["constraint"], adopted_host["demands_by_role"][role])
            profiles[profile["id"]] = profile
            refs.setdefault(role, []).append(profile_ref(profile))
    result = {"execution_profiles": profiles, "capacity_constraints": constraints, "role_profile_refs": refs}
    if adopted_host is not None:
        result["host_capacity_ref"] = adopted_host["constraint"]["id"]
    return result


def apply_editions(instance: dict, editions: dict) -> dict:
    """Adopt built editions; older editions stay registered for admitted executions."""
    instance.setdefault("execution_profiles", {}).update(editions["execution_profiles"])
    instance.setdefault("capacity_constraints", {}).update(editions["capacity_constraints"])
    instance["role_profile_refs"] = editions["role_profile_refs"]
    if editions.get("host_capacity_ref"):
        instance["host_capacity_ref"] = editions["host_capacity_ref"]
    else:
        instance.pop("host_capacity_ref", None)
    return instance


def match_profile_ref(profiles: dict, reference: dict) -> dict:
    """The stored profile a reference names, compared by id, revision and sha256.

    Stored profiles passed validate_profile when saved or sealed, so the profile
    is neither hashed again nor copied. A profile that has not passed through
    storage or ``seal_profile`` must be checked with validate_profile first.
    """
    validate_profile_ref(reference)
    profile = profiles.get(reference["id"])
    if profile is None or any(profile.get(key) != reference[key] for key in ("id", "revision", "sha256")):
        raise ValueError("profile reference is absent or stale")
    return profile


def resolve_profile(profiles: dict, reference: dict) -> dict:
    """A private copy of the stored profile a reference names."""
    return deepcopy(match_profile_ref(profiles, reference))


def select_profile(profiles: dict, action: dict, selection: dict, allowed_refs=None) -> dict:
    """The one stored profile the action may use; like ``match_profile_ref``, not a copy."""
    requested = action.get("profile_ref") or selection.get("profile_ref")
    allowed = None if allowed_refs is None else [profile_ref(match_profile_ref(profiles, r)) for r in allowed_refs]
    candidates = ([match_profile_ref(profiles, requested)] if requested else
                  [profiles[ref["id"]] for ref in {ref["id"]: ref for ref in allowed}.values()]
                  if allowed is not None else list(profiles.values()))
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
    window = profile["window"]
    return deepcopy({**window, **profile["observation"]["settings"],
                     "observation_mode": profile["observation"]["mode"],
                     "max_input_bytes": profile["input"]["max_input_bytes"]})


def _lean_contract(config: dict, host) -> dict:
    command = config.get("lean_command") or host.discover_lean()
    return {"lean_command": deepcopy(command)}


def machine_invocation(profile: dict, *, trust_environment: dict, on_started=None) -> dict:
    """Use the frozen command with the separately approved trust edition; a Lean check has no deadline."""
    machine = profile.get("machine", {})
    command = machine.get("lean_command")
    if profile["actor_kind"] != "machine" or not command:
        raise ValueError("profile has no pinned Lean command")
    # The verifier checks the approved identity's files once, before compiling.
    toolchain = trust_environment["toolchain"]
    if command != toolchain.get("configured_command"):
        raise ValueError("profile command differs from the approved trust environment")
    if profile.get('host_resources'):
        raise ValueError('Lean profiles with host resource caps must be replaced by an uncapped profile')
    arguments = {"lean_command": deepcopy(command),
                 "expected_toolchain": deepcopy(toolchain)}
    if on_started is not None:
        arguments['on_started'] = on_started
    return arguments


def runner_tools(profile: dict) -> dict:
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
    record["id"] = "CE-" + exact_content_hash({k: v for k, v in record.items() if k != "id"})
    return record


def boundary_prompt(profile: dict) -> str:
    return "\n\nExecution boundary (instructions; not OS isolation):\n" + "\n".join(profile["boundary"]["rules"])


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
    record["id"] = "CE-" + exact_content_hash(record)
    return record
