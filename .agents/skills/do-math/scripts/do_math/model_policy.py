"""Model requirements and instance-local capacity defaults; no semantic scoring."""
from __future__ import annotations

from copy import deepcopy

TIERS = ("low", "medium", "high")
MODELS = {"high": "gpt-6-astra", "medium": "gpt-5.6-sol", "low": "gpt-5.6-terra"}
LIMITS = {"work": {model: 3 for model in MODELS.values()},
          "operations": {model: 3 for model in MODELS.values()}}
# Bootstrap judgments must be possible before a research planner has run.
ROLE_TIERS = {"research_preparation": "high", "research_plan": "high",
              "research_work": "low", "supplemental_research": "low",
              "task_contract_review": "medium", "identity_review": "high",
              "goal_audit": "high", "operational_review": "medium",
              "intent_interpretation": "high", "maintenance": "medium",
              "independent_operator": "high"}
ASSESSMENT_SCHEMA = {"type": "object", "additionalProperties": False,
    "properties": {"difficulty": {"type": "string", "enum": list(TIERS)},
                   "importance": {"type": "string", "enum": list(TIERS)},
                   "reason": {"type": "string", "minLength": 1}},
    "required": ["difficulty", "importance", "reason"]}


def assessment_tier(assessment: dict) -> str:
    import jsonschema
    jsonschema.validate(assessment, ASSESSMENT_SCHEMA)
    if not assessment["reason"].strip():
        raise ValueError("model assessment requires a substantive reason")
    return max((assessment["difficulty"], assessment["importance"]), key=TIERS.index)


def preparation_only(action: dict) -> bool:
    return 'assessment_targets' in action or 'observation_rule_targets' in action


def assessment_key(action: dict) -> str:
    return "task_title" if action["role"] == "research_preparation" and not preparation_only(action) else "task_id"


def validate_assessments(action: dict, output: dict, extensions: dict, *, required: bool) -> dict:
    """One shared completeness check for the supplied checker and receiver."""
    key = assessment_key(action)
    rows = extensions.get("model_assessments", [])
    identified = {}
    for entry in rows:
        identity = entry[key]
        if identity in identified:
            raise ValueError("duplicate model assessment: " + identity)
        assessment = {k: entry[k] for k in ASSESSMENT_SCHEMA["properties"]}
        assessment_tier(assessment)
        identified[identity] = assessment
    if preparation_only(action):
        if output.get("candidates"):
            raise ValueError("assessment-only preparation cannot create or revise contracts")
        allowed = {'model_assessments', 'model_assessment_deferrals'}
        if 'observation_rule_targets' in action:
            allowed.update({'task_conditions', 'observation_rule_deferrals'})
        if set(extensions) - allowed:
            raise ValueError("assessment-only preparation may only assess or defer its assigned tasks")
        expected = set(action.get("assessment_targets", {}))
        deferred = [entry["task_id"] for entry in extensions.get("model_assessment_deferrals", [])]
        if len(deferred) != len(set(deferred)) or set(deferred) & set(identified):
            raise ValueError("assessment and deferral must identify each target exactly once")
        supplied = set(identified) | set(deferred)
        required = True
    else:
        from .task_contracts import selected_task_ids
        expected = ({item["title"] for item in output.get("candidates", [])}
                    if action["role"] == "research_preparation" else set(selected_task_ids(output)))
        supplied = set(identified)
    missing, unexpected = expected - supplied, supplied - expected
    if unexpected or (required and missing):
        import json
        raise ValueError("model assessment coverage: " + json.dumps(
            {"missing": sorted(missing), "unexpected": sorted(unexpected)}, ensure_ascii=False))
    return identified


def assessment_basis(task: dict) -> dict:
    from .planning import contract_hash
    return {"revision": task["revision"], "contract_sha256": contract_hash(task)}


def validate_policy(config: dict) -> None:
    models = config["tier_models"]
    if not isinstance(models, dict) or set(models) != set(TIERS) or any(
            not isinstance(m, str) or not m.strip() for m in models.values()):
        raise ValueError("tier_models must name a model for low, medium and high")
    roles = config["role_tiers"]
    if not isinstance(roles, dict) or set(roles) - set(ROLE_TIERS) or any(t not in TIERS for t in roles.values()):
        raise ValueError("role_tiers contains an unknown role or tier")
    limits = config["session_limits"]
    if limits is None:  # Explicit compatibility mode for existing call-budget instances.
        return
    if not isinstance(limits, dict) or set(limits) != {"work", "operations"}:
        raise ValueError("session_limits requires work and operations model maps")
    for pool, values in limits.items():
        if not isinstance(values, dict) or any(not isinstance(m, str) or not m.strip()
                or isinstance(n, bool) or not isinstance(n, int) or n < 0 for m, n in values.items()):
            raise ValueError(f"session_limits.{pool} must map model names to nonnegative integers")
        if set(models.values()) - set(values):
            raise ValueError(f"session_limits.{pool} must explicitly include every tier model, including zero capacity")
    if config.get("role_models"):
        raise ValueError("session mode uses tier_models and role_tiers; clear legacy role_models on conversion")


def selection(config: dict, action: dict, tasks: dict, knowledge: dict, *, profiles: dict | None = None) -> dict:
    """Bind a requirement to a model without inspecting current slot availability."""
    role, target = action["role"], action.get("target")
    requirement = action.get("model_assessment")
    task = tasks.get(target, {})
    if not task and target in knowledge:
        task = tasks.get(knowledge[target].get("task_id"), {})
    requirement = requirement or task.get("model_assessment")
    floor = config["role_tiers"].get(role, ROLE_TIERS.get(role, "low"))
    if requirement:
        tier = max((assessment_tier(requirement), floor), key=TIERS.index)
        reason = requirement["reason"]
    elif role in {"research_work", "supplemental_research"}:
        tier, reason = "high", "No preserved difficulty/importance assessment; use high until explicitly assessed."
    else:
        tier, reason = floor, "Configured role requirement; raise when task difficulty or importance requires it."
    result = {"tier": tier, "model": config["tier_models"][tier],
              "assessment": deepcopy(requirement), "reason": reason}
    if config.get("session_limits") is None:
        result["model"] = (config["operator_model"] if role in {"recovery", "independent_operator"}
                           else config.get("role_models", {}).get(role, config["model"]))
        result["reason"] = "Preserve the adopted call-budget model assignment."
    if profiles is not None:
        from .execution_profiles import build_profiles, select_profile, profile_ref, resolve_profile
        # A task's allowlist governs its work attempts. Reviewers and other
        # decision roles use their own adopted role profiles, while still
        # inheriting the task's difficulty/importance requirement above.
        allowed = (task.get("execution_profile_refs", task.get("profile_refs"))
                   if role in {"research_work", "supplemental_research"}
                   and not action.get("review_cycle_id") else None)
        if action.get("profile_ref"):
            explicit = resolve_profile(profiles, action["profile_ref"])
            if explicit["actor_kind"] == "ai":
                pinned = explicit["ai"]
                if config.get("session_limits") is not None and (
                        pinned.get("tier") not in TIERS or TIERS.index(pinned["tier"]) < TIERS.index(tier)):
                    raise ValueError("explicit profile does not meet the role/task model requirement")
                result.update(model=pinned["model"], tier=pinned.get("tier"),
                              reason="Explicit immutable profile meeting the role/task requirement.")
        if allowed is None and not action.get("profile_ref"):
            # The registry retains old editions for running executions. New
            # default assignments use only the current adopted configuration.
            allowed = build_profiles(config)["role_profile_refs"].get(role, [])
        selected = select_profile(profiles, action, result, allowed_refs=allowed)
        result["profile_ref"] = profile_ref(selected)
    return result
