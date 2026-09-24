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

from .contracts import ROLES, all_prompt_documents, schema_for, action_schema


@lru_cache(maxsize=128)
def _check_schema_pair(text: str) -> None:
    """Cache schema well-formedness, not document, data or authority checks."""
    from jsonschema import Draft7Validator
    schema = json.loads(text)
    Draft202012Validator.check_schema(schema)
    Draft7Validator.check_schema({key: value for key, value in schema.items()
                                 if key not in {"$schema", "x-contract-id"}})


def inspect_current_state(instance: dict, runtime: dict) -> dict:
    """Read-only minimum gate for a loaded feature-5 state before recovery writes.

    Repository/ref integrity, artifact bytes, and domain relations remain the
    STORAGE and ENGINE checks that consume this structural result.
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
            from datetime import datetime
            try:
                stamp = datetime.fromisoformat(runtime['last_observed_utc'].replace('Z', '+00:00'))
                if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
                    raise ValueError('UTC offset required')
            except (ValueError, TypeError):
                errors.append({'check': 'clock_high_water', 'reason': 'invalid UTC high-water timestamp'})
        if any(t.get('status') == 'ready' for t in runtime.get('tasks', {}).values()):
            errors.append({'check': 'derived_readiness', 'reason': 'derived task readiness cannot be persisted'})
    return {"valid": not errors, "errors": errors, "feature_version": version}


def inspect_persisted_state(store, snapshot):
    """Validate the exact current family bytes without publishing repairs."""
    try:
        head, instance, runtime = store.load(snapshot)
        # load verifies envelopes, family schemas/relations, IDs and public events.
        result = inspect_current_state(instance, runtime)
        result['snapshot'] = head
        return result
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        return {'valid': False, 'snapshot': snapshot,
                'errors': [{'check': 'persisted_families', 'reason': str(exc)}]}


def preserve_rejected_candidate(store, snapshot, *, raw, reason):
    """Keep rejected bytes on the verified head, never publish the rejected state."""
    from .repository import new_id, canonical_json
    if not isinstance(raw, bytes):
        raise TypeError('candidate raw bytes required')
    report = inspect_persisted_state(store, snapshot)
    if not report['valid']:
        raise ValueError('damaged current state cannot be rewritten: ' + str(report['errors']))
    _, instance, runtime = store.load(snapshot)
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
        for name in ("README.md", "references/CLI-실행-계약.md", "계약/독립-운영.md",
                     "scripts/operator_schedule.ps1", "requirements.txt"):
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
        from .knowledge_io import catalog_definitions
        from .repository import canonical_json
        schemas = {role: schema_for(role) for role in ROLES}
        schemas.update({"identity_review:" + stage: stage_schema(stage) for stage in ("initial", "organize", "answer", "judge")})
        schemas.update({"intent_interpretation:" + stage: interpretation_schema(stage) for stage in ("interpret", "check")})
        schemas.update(review_research=research_schema(), independent_operator=OPERATOR_SCHEMA)
        definitions = catalog_definitions({})
        schemas.update({role + ':bound_action': action_schema({'role': role}, definitions) for role in ROLES})
        schemas['assessment:main'] = action_schema({'role': 'research_preparation', 'assessment_targets': {}}, definitions)
        schemas['live_operations:main'] = action_schema({'role': 'operational_review', 'live': True}, definitions)
        for role in ROLES:
            schemas[role + ":extensions"] = extension_schema({"role": role}, definitions)
        schemas["assessment:extensions"] = extension_schema({"role": "research_preparation", "assessment_targets": {}}, definitions)
        preparation = {'role': 'research_preparation', 'assessment_targets': {}, 'observation_rule_targets': {}}
        schemas['preparation:main'] = action_schema(preparation, definitions)
        schemas['preparation:extensions'] = extension_schema(preparation, definitions)
        schemas["fixed_research:extensions"] = extension_schema({"role": "supplemental_research", "review_cycle_id": "fixed"}, definitions)
        schemas['identity:extensions'] = extension_schema({'role': 'identity_review', 'review_cycle_id': 'fixed'}, definitions)
        for schema in schemas.values():
            _check_schema_pair(json.dumps(schema, ensure_ascii=False, sort_keys=True,
                                          separators=(",", ":"), allow_nan=False))
        checks.append({"check": "role_output_schemas", "status": "verified", "roles": len(ROLES),
                       "schemas": {name: hashlib.sha256(canonical_json(schema)).hexdigest() for name, schema in schemas.items()},
                       "claude_conversion": "Only top-level $schema and x-contract-id are removed; constraints are preserved."})
    except (ValueError, SchemaError) as exc:
        checks.append({"check": "role_output_schemas", "status": "incomplete", "reason": str(exc)})
    return {"scope": "installed_skill_structure",
            "status": "verified" if all(row["status"] == "verified" for row in checks) else "incomplete",
            "checks": checks,
            "not_verified": ["document_semantics", "runtime_execution", "research_roles", "Lean",
                             "research_efficacy"]}
