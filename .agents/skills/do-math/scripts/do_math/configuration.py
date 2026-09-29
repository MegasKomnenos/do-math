"""Stored configuration defaults and the cross-field rules of the configuration section.

``record_schemas.config_schema`` fixes each key's type and range; this module
adds the defaults a new instance starts from and the rules that relate keys.
"""
from __future__ import annotations

from copy import deepcopy

import jsonschema

from . import execution_profiles, model_policy
from .record_schemas import config_schema
from .scholarly import validate_scholarly_server
from .migration_defaults import host_or_local


DEFAULT_CONFIG = {
    "tier_models": deepcopy(model_policy.MODELS), "role_tiers": deepcopy(model_policy.ROLE_TIERS),
    "session_limits": deepcopy(model_policy.LIMITS),
    "effort": "medium", "call_timeout_seconds": 600,
     "reviewers": 2,
    "goal_auditors": 2, "max_input_bytes": 2000000, "max_output_repairs": 1,
    "lean_command": None,
    "review_rounds": 3, "review_research_limit": 3, "research_reconsider_seconds": 86400,
    "observation_mode": "event_driven", "observation_interval_seconds": 300,
    "plan_settle_seconds": 300,
    "max_artifact_bytes": 268435456,
    "operator_enabled": True, "operator_interval_seconds": 7200,
    "operator_timeout_seconds": 5400, "operator_effort": "high",
    "scholarly_enabled": True, "scholarly_server": None,
    "claude_only_assigned_model": False,
    "provider_retry_initial_seconds": 300, "provider_retry_max_seconds": 7200,
    "finish_notice_seconds": 60,
}


def validate_config(config: dict, *, host_id=None) -> None:
    """The configuration section fixes keys, types and ranges; only cross-field rules remain here."""
    schema = config_schema()
    unknown = set(config) - set(schema["properties"])
    if unknown:
        raise ValueError("configuration has fields outside the stored configuration section: "
                         + ", ".join(sorted(unknown)))
    config = {**DEFAULT_CONFIG, **config}
    # A requested host constraint may still carry its request authority alias,
    # which the stored schema refuses; the host section is checked below instead.
    error = next(jsonschema.Draft202012Validator(schema).iter_errors(
        {key: value for key, value in config.items() if key != "host_resources"}), None)
    if error is not None:
        raise ValueError("config/" + "/".join(str(part) for part in error.absolute_path) + ": " + error.message)
    model_policy.validate_policy(config)
    if config["scholarly_server"] is not None:
        validate_scholarly_server(config["scholarly_server"])
    if config["provider_retry_max_seconds"] < config["provider_retry_initial_seconds"]:
        raise ValueError("provider retry maximum must be at least the initial interval")
    if config["lean_command"] is not None and any("\0" in part for part in config["lean_command"]):
        raise ValueError("lean_command arguments must be NUL-free strings")
    if config.get('host_resources') is not None:
        execution_profiles.validate_host_resources(config['host_resources'])
        if config['host_resources']['constraint']['host_id'] != host_or_local(host_id):
            raise ValueError('host_resources must name this local host')
