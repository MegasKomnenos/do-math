"""Read-only structural checks of the installed, self-contained skill.

These checks load local contracts; they do not establish semantic correctness,
research quality, execution authority, or live tool availability.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .contracts import ROLES, all_prompt_documents, schema_for


def inspect_bundle(skill_root: Path | None = None) -> dict:
    """Inspect only the specified skill directory, or this installation."""
    root = (skill_root or Path(__file__).resolve().parents[2]).resolve()
    checks = []
    try:
        roles = all_prompt_documents(skill_root=root)
        documents = {document["path"]: document["sha256"]
                     for assigned in roles.values() for document in assigned}
        for name in ("README.md", "references/CLI-실행-계약.md", "requirements.txt"):
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
        for role in ROLES:
            Draft202012Validator.check_schema(schema_for(role))
        checks.append({"check": "role_output_schemas", "status": "verified", "roles": len(ROLES)})
    except (ValueError, SchemaError) as exc:
        checks.append({"check": "role_output_schemas", "status": "incomplete", "reason": str(exc)})
    return {"scope": "installed_skill_structure",
            "status": "verified" if all(row["status"] == "verified" for row in checks) else "incomplete",
            "checks": checks,
            "not_verified": ["document_semantics", "runtime_execution", "research_roles", "Lean",
                             "research_efficacy"]}
