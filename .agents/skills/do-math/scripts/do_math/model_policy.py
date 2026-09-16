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


def selection(config: dict, action: dict, tasks: dict, knowledge: dict) -> dict:
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
    return {"tier": tier, "model": config["tier_models"][tier],
            "assessment": deepcopy(requirement), "reason": reason}
