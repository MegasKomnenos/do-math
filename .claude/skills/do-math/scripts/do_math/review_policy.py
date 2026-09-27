"""Versioned policy and independent scope contracts for identity review."""
from __future__ import annotations

from copy import deepcopy

import jsonschema

from .contracts import PROFILE_REF, REFS, TEXT, closed_object
from .file_io import distinct_texts
from .state_contract import validate_record


OVERFLOW_DISPOSITIONS = ("unresolved", "defer")

# The one shape of an independent scope assessment. The scope stage's wire schema
# carries it, and validate_scope_assessment checks it before the meaning conditions.
SCOPE_ASSESSMENT = closed_object({
    "assessment_id": TEXT, "policy_id": TEXT, "required_perspectives": REFS,
    "initial_slots": {"type": "array", "minItems": 1, "items": closed_object(
        {"id": TEXT, "perspective": TEXT, "required_source_refs": {**REFS, "minItems": 1}})},
    "selected_profile_ref": {"anyOf": [{"type": "null"}, PROFILE_REF]},
    "activity_execution_limit": {"type": "integer", "minimum": 1},
    "overflow_disposition": {"enum": list(OVERFLOW_DISPOSITIONS)}})
_SCOPE_CHECKER = jsonschema.Draft202012Validator(SCOPE_ASSESSMENT)


def _positive(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def build_review_policy(policy=None, *, reviewer_count=None, max_rounds=None, judge_slots=None):
    """Validate the adopted review policy or construct the configured default."""
    if policy is None:
        count = _positive(reviewer_count, "reviewer count")
        rounds = _positive(max_rounds, "round limit")
        judges = list(judge_slots or ["judge-0", "judge-1", "judge-2"])
        policy = {
            "id": "review-policy-v5-default",
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
    required = {"id", "required_perspectives", "minimum_initial_slots", "judge_slots",
                "round_limit", "activity_execution_limit", "overflow_disposition"}
    if set(policy) != required:
        raise ValueError("review policy fields differ from the policy contract")
    if not isinstance(policy["id"], str) or not policy["id"]:
        raise ValueError("review policy ID is required")
    distinct_texts(policy["required_perspectives"], "required perspectives")
    _positive(policy["minimum_initial_slots"], "minimum initial slots")
    judges = distinct_texts(policy["judge_slots"], "judge slots", nonempty=True)
    if len(judges) != 3:
        raise ValueError("review policy requires exactly three judge slots")
    _positive(policy["round_limit"], "round limit")
    _positive(policy["activity_execution_limit"], "activity execution limit")
    if policy["overflow_disposition"] not in OVERFLOW_DISPOSITIONS:
        raise ValueError("unsupported review overflow disposition")
    return deepcopy(policy)


def minimum_scope_executions(initial_slots, round_limit, executions_used=0):
    """Attempts already spent plus the mandatory initial/organize/judge path."""
    return executions_used + initial_slots + 1 + (3 if round_limit == 1 else initial_slots + 6)


def validate_scope_assessment(assessment, policy, *, executions_used=0):
    """Validate an assessment without letting it split the proposal's review scope.

    The schema fixes its shape; the checks here are the meaning it has under the policy.
    """
    policy = build_review_policy(policy)
    validate_record(_SCOPE_CHECKER, assessment, "scope_assessment")
    if assessment["policy_id"] != policy["id"]:
        raise ValueError("scope assessment belongs to another review policy")
    perspectives = assessment["required_perspectives"]
    if not set(policy["required_perspectives"]).issubset(perspectives):
        raise ValueError("scope assessment omits a required perspective")
    slots = assessment["initial_slots"]
    if len(slots) < policy["minimum_initial_slots"]:
        raise ValueError("scope assessment has too few initial slots")
    identifiers = [slot["id"] for slot in slots]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate scope assessment slot")
    if set(identifiers).intersection([*policy['judge_slots'], 'scope', 'organize']):
        raise ValueError('scope assessment reuses an independent role slot')
    if not set(perspectives).issubset({slot["perspective"] for slot in slots}):
        raise ValueError("scope assessment has no slot for a required perspective")
    limit = assessment["activity_execution_limit"]
    if limit > policy["activity_execution_limit"]:
        raise ValueError("scope assessment exceeds the policy execution limit")
    minimum = minimum_scope_executions(len(slots), policy['round_limit'], executions_used)
    if limit < minimum:
        raise ValueError(f"scope activity execution limit requires at least {minimum} attempts including {executions_used} already used")
    if assessment["overflow_disposition"] != policy["overflow_disposition"]:
        raise ValueError("scope assessment changes the policy overflow disposition")
    return deepcopy(assessment)
