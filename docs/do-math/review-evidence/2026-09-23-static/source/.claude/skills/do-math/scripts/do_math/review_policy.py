"""Versioned policy and independent scope contracts for identity review."""
from __future__ import annotations

from copy import deepcopy


_OVERFLOW_DISPOSITIONS = {"unresolved", "defer"}


def _positive(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _strings(values, label, *, allow_empty=False):
    if not isinstance(values, list) or (not values and not allow_empty) or any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{label} must be a {'nonempty ' if not allow_empty else ''}list of strings")
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")
    return list(values)


def build_review_policy(policy=None, *, reviewer_count=None, max_rounds=None, judge_slots=None):
    """Return a frozen v5 review policy, deriving only legacy-safe defaults."""
    if policy is None:
        count = _positive(reviewer_count, "reviewer count")
        rounds = _positive(max_rounds, "round limit")
        judges = list(judge_slots or ["judge-0", "judge-1", "judge-2"])
        policy = {
            "id": "review-policy-v5-default",
            "version": 5,
            "required_perspectives": [],
            "minimum_initial_slots": count,
            "judge_slots": judges,
            "round_limit": rounds,
            # This is a derived finite upper bound for the existing finite cycle,
            # not an asserted host or provider capacity.
            "activity_execution_limit": count + rounds * (count + len(judges) + 1),
            "overflow_disposition": "unresolved",
        }
    if not isinstance(policy, dict):
        raise ValueError("review policy must be an object")
    required = {"id", "version", "required_perspectives", "minimum_initial_slots", "judge_slots",
                "round_limit", "activity_execution_limit", "overflow_disposition"}
    if set(policy) != required:
        raise ValueError("review policy fields differ from v5 contract")
    if not isinstance(policy["id"], str) or not policy["id"]:
        raise ValueError("review policy ID is required")
    if policy["version"] != 5:
        raise ValueError("review policy must use feature version 5")
    _strings(policy["required_perspectives"], "required perspectives", allow_empty=True)
    _positive(policy["minimum_initial_slots"], "minimum initial slots")
    judges = _strings(policy["judge_slots"], "judge slots")
    if len(judges) != 3:
        raise ValueError("review policy requires exactly three judge slots")
    _positive(policy["round_limit"], "round limit")
    _positive(policy["activity_execution_limit"], "activity execution limit")
    if policy["overflow_disposition"] not in _OVERFLOW_DISPOSITIONS:
        raise ValueError("unsupported review overflow disposition")
    return deepcopy(policy)


def default_scope_assessment(policy, reviewer_slots):
    """Adapt the old all-proposal assignment without inventing expertise claims."""
    slots = _strings(list(reviewer_slots), "reviewer slots")
    return {
        "assessment_id": "legacy-full-proposal-scope",
        "policy_id": policy["id"],
        "policy_version": policy["version"],
        "required_perspectives": list(policy["required_perspectives"]),
        "initial_slots": [{"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
        "selected_profile_ref": None,
        "activity_execution_limit": policy["activity_execution_limit"],
        "overflow_disposition": policy["overflow_disposition"],
    }


def validate_scope_assessment(assessment, policy):
    """Validate an assessment without letting it split the proposal's review scope."""
    policy = build_review_policy(policy)
    if not isinstance(assessment, dict):
        raise ValueError("scope assessment must be an object")
    required = {"assessment_id", "policy_id", "policy_version", "required_perspectives", "initial_slots",
                "selected_profile_ref", "activity_execution_limit", "overflow_disposition"}
    if set(assessment) != required:
        raise ValueError("scope assessment fields differ from v5 contract")
    if not isinstance(assessment["assessment_id"], str) or not assessment["assessment_id"]:
        raise ValueError("scope assessment ID is required")
    if assessment["policy_id"] != policy["id"] or assessment["policy_version"] != policy["version"]:
        raise ValueError("scope assessment belongs to another review policy")
    perspectives = _strings(assessment["required_perspectives"], "required perspectives", allow_empty=True)
    if not set(policy["required_perspectives"]).issubset(perspectives):
        raise ValueError("scope assessment omits a required perspective")
    slots = assessment["initial_slots"]
    if not isinstance(slots, list) or len(slots) < policy["minimum_initial_slots"]:
        raise ValueError("scope assessment has too few initial slots")
    normalized = []
    for slot in slots:
        if not isinstance(slot, dict) or set(slot) != {"id", "perspective", "required_source_refs"}:
            raise ValueError("scope assessment slot fields differ from v5 contract")
        if not isinstance(slot["id"], str) or not slot["id"] or not isinstance(slot["perspective"], str) or not slot["perspective"]:
            raise ValueError("scope assessment slot needs an ID and perspective")
        normalized.append({"id": slot["id"], "perspective": slot["perspective"],
                           "required_source_refs": _strings(slot["required_source_refs"], "required source refs")})
    if len({slot["id"] for slot in normalized}) != len(normalized):
        raise ValueError("duplicate scope assessment slot")
    if {slot['id'] for slot in normalized}.intersection([*policy['judge_slots'], 'scope', 'organize']):
        raise ValueError('scope assessment reuses an independent role slot')
    if not set(perspectives).issubset({slot["perspective"] for slot in normalized}):
        raise ValueError("scope assessment has no slot for a required perspective")
    profile = assessment["selected_profile_ref"]
    if profile is not None and (not isinstance(profile, dict) or set(profile) != {"id", "revision", "sha256"} or
                                not isinstance(profile["id"], str) or not profile["id"] or
                                type(profile["revision"]) is not int or profile["revision"] < 1 or
                                not isinstance(profile['sha256'], str) or len(profile['sha256']) != 64 or
                                any(c not in '0123456789abcdef' for c in profile['sha256'])):
        raise ValueError("scope assessment profile reference is invalid")
    limit = _positive(assessment["activity_execution_limit"], "scope activity execution limit")
    if limit > policy["activity_execution_limit"]:
        raise ValueError("scope assessment exceeds the policy execution limit")
    if assessment["overflow_disposition"] != policy["overflow_disposition"]:
        raise ValueError("scope assessment changes the policy overflow disposition")
    return {"assessment_id": assessment["assessment_id"], "policy_id": assessment["policy_id"],
            "policy_version": assessment["policy_version"], "required_perspectives": perspectives,
            "initial_slots": normalized, "selected_profile_ref": deepcopy(profile),
            "activity_execution_limit": limit, "overflow_disposition": assessment["overflow_disposition"]}
