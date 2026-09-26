"""Read-only structural checks of the installed, self-contained skill.

These checks load local contracts; they do not establish semantic correctness,
research quality, execution authority, or live tool availability.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .contracts import OPERATING_DOCUMENTS, ROLES, all_prompt_documents, schema_for, action_schema
from .file_io import compact_json_bytes

# Installed documents checked besides the role reading map.
INSTALLED_DOCUMENTS = ("README.md", "references/CLI-실행-계약.md", "requirements.txt", *OPERATING_DOCUMENTS)


@lru_cache(maxsize=128)
def _check_schema_pair(text: str) -> None:
    """Cache schema well-formedness, not document, data or authority checks."""
    from jsonschema import Draft7Validator
    schema = json.loads(text)
    Draft202012Validator.check_schema(schema)
    Draft7Validator.check_schema({key: value for key, value in schema.items()
                                 if key not in {"$schema", "x-contract-id"}})


def inspect_current_state(instance: dict, runtime: dict) -> dict:
    """Minimum structural gate of a current feature-5 state.

    The state contract applies it to every validated state
    (``record_schemas.validate_semantics``), so every loaded or published
    state already satisfies it. Repository/ref integrity, artifact bytes and
    domain relations are the contract's other checks.
    """
    errors: list[dict] = []
    if not isinstance(instance, dict) or not isinstance(runtime, dict):
        return {"valid": False, "errors": [{"check": "state_shape", "reason": "instance and runtime must be objects"}]}
    from .state_contract import STATE_FORMAT_VERSION
    version = instance.get('feature_version')
    if (type(version) is not int or type(runtime.get('feature_version')) is not int
            or version != STATE_FORMAT_VERSION or runtime.get('feature_version') != version):
        errors.append({'check': 'feature_version', 'reason': 'only the current version-five contract is supported'})
    if version == STATE_FORMAT_VERSION:
        lifecycle = instance.get("lifecycle")
        if not isinstance(lifecycle, dict) or lifecycle.get("state") not in {"initializing", "active", "paused"}:
            errors.append({"check": "lifecycle", "reason": "feature-5 state has no valid lifecycle state"})
        if runtime.get("status") not in {"initializing", "ready", "running", "paused", "waiting", "capacity_waiting", "completed", "closed"}:
            errors.append({"check": "runtime_status", "reason": "feature-5 runtime status is invalid"})
        if isinstance(lifecycle, dict) and lifecycle.get('permanently_closed') and runtime.get('status') != 'closed':
            errors.append({'check':'terminal_closure', 'reason':'permanently closed instance cannot have a live projection'})
        if not isinstance(runtime.get("last_observed_utc"), str):
            errors.append({"check": "clock_high_water", "reason": "feature-5 state has no persisted UTC high-water"})
        else:
            from .file_io import parse_utc
            try:
                parse_utc(runtime['last_observed_utc'])
                if not runtime['last_observed_utc'].endswith(('Z', '+00:00')):
                    raise ValueError('UTC offset required')
            except ValueError:
                errors.append({'check': 'clock_high_water', 'reason': 'invalid UTC high-water timestamp'})
        if any(t.get('status') == 'ready' for t in runtime.get('tasks', {}).values()):
            errors.append({'check': 'derived_readiness', 'reason': 'derived task readiness cannot be persisted'})
    return {"valid": not errors, "errors": errors, "feature_version": version}


def preserve_rejected_candidate(store, snapshot, *, raw, reason):
    """Keep rejected bytes on the verified head, never publish the rejected state.

    Loading ``snapshot`` validates it under the state contract; a head that
    does not load is damaged and is not rewritten.
    """
    from .repository import new_id, canonical_json
    if not isinstance(raw, bytes):
        raise TypeError('candidate raw bytes required')
    try:
        _, instance, runtime = store.load(snapshot)
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        raise ValueError('damaged current state cannot be rewritten: ' + str(exc)) from exc
    identity = new_id('RJ')
    path = 'runtime/artifacts/' + identity + '/candidate.raw'
    audit = 'runtime/artifacts/' + identity + '/rejection.json'
    new_head = store.save_with_state(snapshot, instance, runtime, artifacts={path: raw, audit: canonical_json({
        'id': identity, 'candidate_ref': path, 'sha256': hashlib.sha256(raw).hexdigest(),
        'base_snapshot': snapshot, 'reason': reason, 'disposition': 'rejected_not_applied'})})[0]
    return {'snapshot': new_head, 'raw_ref': path, 'audit_ref': audit}


def inspect_bundle(skill_root: Path | None = None) -> dict:
    """Inspect only the specified skill directory, or this installation."""
    root = (skill_root or Path(__file__).resolve().parents[2]).resolve()
    checks = []
    try:
        roles = all_prompt_documents(skill_root=root)
        documents = {document["path"]: document["sha256"]
                     for assigned in roles.values() for document in assigned}
        for name in INSTALLED_DOCUMENTS:
            path = root / name
            if not path.resolve().is_relative_to(root):
                raise ValueError(f"document leaves the skill: {name}")
            raw = path.read_bytes()
            if not raw.decode("utf-8").strip():
                raise ValueError(f"empty document: {name}")
            documents[name] = hashlib.sha256(raw).hexdigest()
        checks.append({"check": "installed_documents", "status": "verified",
                       "roles": len(roles), "documents": documents})
    except (OSError, ValueError) as exc:
        checks.append({"check": "installed_documents", "status": "incomplete", "reason": str(exc)})
    try:
        from .review_cycle import stage_schema, research_schema
        from .governance import interpretation_schema
        from .scheduled_operator import OPERATOR_SCHEMA
        from .submission import extension_schema
        from .repository import exact_content_hash
        schemas = {role: schema_for(role) for role in ROLES}
        schemas.update({"identity_review:" + stage: stage_schema(stage) for stage in ("scope", "initial", "organize", "answer", "judge")})
        schemas.update({"intent_interpretation:" + stage: interpretation_schema(stage) for stage in ("interpret", "check")})
        schemas.update(review_research=research_schema(), independent_operator=OPERATOR_SCHEMA)
        schemas.update({role + ':bound_action': action_schema({'role': role}) for role in ROLES})
        schemas['assessment:main'] = action_schema({'role': 'research_preparation', 'assessment_targets': {}})
        schemas['live_operations:main'] = action_schema({'role': 'operational_review', 'live': True})
        for role in ROLES:
            schemas[role + ":extensions"] = extension_schema({"role": role})
        schemas["assessment:extensions"] = extension_schema({"role": "research_preparation", "assessment_targets": {}})
        preparation = {'role': 'research_preparation', 'assessment_targets': {}, 'observation_rule_targets': {}}
        schemas['preparation:main'] = action_schema(preparation)
        schemas['preparation:extensions'] = extension_schema(preparation)
        schemas["fixed_research:extensions"] = extension_schema({"role": "supplemental_research", "review_cycle_id": "fixed"})
        schemas['identity:extensions'] = extension_schema({'role': 'identity_review', 'review_cycle_id': 'fixed'})
        for schema in schemas.values():
            _check_schema_pair(compact_json_bytes(schema).decode("utf-8"))
        checks.append({"check": "role_output_schemas", "status": "verified", "roles": len(ROLES),
                       "schemas": {name: exact_content_hash(schema) for name, schema in schemas.items()},
                       "claude_conversion": "Only top-level $schema and x-contract-id are removed; constraints are preserved."})
    except (ValueError, SchemaError) as exc:
        checks.append({"check": "role_output_schemas", "status": "incomplete", "reason": str(exc)})
    return {"scope": "installed_skill_structure",
            "status": "verified" if all(row["status"] == "verified" for row in checks) else "incomplete",
            "checks": checks,
            "not_verified": ["document_semantics", "runtime_execution", "research_roles", "Lean",
                             "research_efficacy"]}
