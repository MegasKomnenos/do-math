"""Read-only structural checks of the installed, self-contained skill.

These checks load local contracts; they do not establish semantic correctness,
research quality, execution authority, or live tool availability.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .contracts import ROLES, all_prompt_documents, schema_for, action_schema


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
        from jsonschema import Draft7Validator
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
        schemas["fixed_research:extensions"] = extension_schema({"role": "supplemental_research", "review_cycle_id": "fixed"}, definitions)
        schemas['identity:extensions'] = extension_schema({'role': 'identity_review', 'review_cycle_id': 'fixed'}, definitions)
        for schema in schemas.values():
            Draft202012Validator.check_schema(schema)
            Draft7Validator.check_schema({key: value for key, value in schema.items() if key not in {"$schema", "x-contract-id"}})
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
