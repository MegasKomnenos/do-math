"""Installed, explicit feature-five storage contract, distinct from wire schemas."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, replace
from functools import lru_cache
import hashlib
import json
import re
from typing import Callable

import jsonschema

STATE_FORMAT_VERSION = 5
SCHEMA_VERSION = 2
STATE_CONTRACT_ID = "do-math-state/5"
CONTRACT_ID = STATE_CONTRACT_ID


@lru_cache(maxsize=256)
def _check_schema_text(text):
    """Reuse only schema well-formedness, never record or authority validation."""
    jsonschema.Draft202012Validator.check_schema(json.loads(text))


@dataclass(frozen=True)
class RegisteredFamily:
    root: str
    name: str
    shape: str
    schema: dict
    validator: Callable | None = None
    references: Callable | None = None
    identity: bool = True
    derived: Callable | None = None


class StateContract:
    def __init__(self, version=STATE_FORMAT_VERSION):
        if version != STATE_FORMAT_VERSION:
            raise ValueError("unsupported state contract version")
        self.version = version
        self._families = {}

    @classmethod
    def default(cls):
        from .record_schemas import install
        contract = cls()
        install(contract)
        return contract

    def register_family(self, root, name, *, shape="map", schema=None,
                        validator=None, references=None, identity=True, derived=None):
        if root not in {"research", "runtime"} or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError("invalid family root/name")
        if shape not in {"map", "list", "singleton", "metadata", "derived", "events"}:
            raise ValueError("invalid family shape")
        if shape == "metadata" and identity:
            raise ValueError("metadata fields cannot allocate independent record identities")
        if shape == "derived" and not callable(derived):
            raise ValueError("derived family requires a reconstruction function")
        existing = self.family(root, name)
        if existing is not None:
            # Existing owner adapters may repeat registration of an installed
            # family. They may not redefine its schema or physical layout.
            if schema is not None or shape != existing.shape:
                raise ValueError("record family already registered: " + name)
            if validator is not None:
                prior = existing.validator
                def combined(record):
                    if prior:
                        prior(record)
                    validator(record)
                existing = replace(existing, validator=combined)
            if references is not None:
                prior_refs = existing.references
                def all_references(record):
                    if prior_refs:
                        yield from prior_refs(record)
                    yield from references(record)
                existing = replace(existing, references=all_references)
            self._families[root, name] = existing
            return
        if schema is None:
            raise ValueError("explicit record schema is required: " + name)
        schema = deepcopy(schema)
        schema_text = json.dumps(schema, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":"), allow_nan=False)
        _check_schema_text(schema_text)
        if (shape in {"map", "list", "events"} or identity) and (schema.get("type") != "object" or schema.get("additionalProperties") is not False):
            raise ValueError("record schema must reject unknown fields: " + name)
        self._families[root, name] = RegisteredFamily(root, name, shape, schema, validator, references, identity, derived)

    def family(self, root, name):
        return self._families.get((root, name))

    def families(self):
        return tuple(self._families[key] for key in sorted(self._families))

    def manifest(self):
        """Record the format version and the writer's schema declarations.

        The installed validators run on every load and publication. Their source
        bytes belong to the engine installation identity; a compatible repair
        must be able to read the records it repairs. A semantic reinterpretation
        of existing values requires a new schema_version or contract_id. The
        declaration digest is provenance: compatible optional-field additions
        are decided by validating the actual saved layouts and records.
        """
        families = [{"root": f.root, "name": f.name, "shape": f.shape, "identity": f.identity,
                     "schema": f.schema} for f in self.families()]
        payload = {"contract_id": STATE_CONTRACT_ID, "schema_version": SCHEMA_VERSION, "families": families}
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return {"contract_id": STATE_CONTRACT_ID, "schema_version": SCHEMA_VERSION, "sha256": digest}

    def validate(self, instance, runtime):
        """Pure schema and relationship validation; no ID/time allocation."""
        rows, identifiers = [], {}
        for root, state in (("research", instance), ("runtime", runtime)):
            if not isinstance(state, dict):
                raise ValueError(root + " must be an object")
            if type(state.get("feature_version")) is not int or state["feature_version"] != STATE_FORMAT_VERSION:
                raise ValueError(root + " feature_version is missing or unsupported")
            if state.get("contract_id") != STATE_CONTRACT_ID:
                raise ValueError(root + " contract_id is missing or unsupported")
            if root == "research" and state.get("object_format") not in {"sha1", "sha256"}:
                raise ValueError("research object_format is missing or unsupported")
            for name, value in state.items():
                family = self.family(root, name)
                if family is None:
                    raise ValueError("unregistered family: " + root + "/" + name)
                if family.shape == "derived":
                    if value != family.derived(instance, runtime):
                        raise ValueError("stale derived view: " + name)
                    continue
                if family.shape == "map":
                    if not isinstance(value, dict):
                        raise ValueError(name + " must be a record map")
                    entries = list(value.items())
                elif family.shape in {"list", "events"}:
                    if family.shape == "events" and isinstance(value, dict):
                        entries = list(value.items())
                    elif isinstance(value, list):
                        entries = [(None, row) for row in value]
                    else:
                        raise ValueError(name + " must be a record list")
                else:
                    entries = [(None, value)]
                for key, record in entries:
                    errors = sorted(jsonschema.Draft202012Validator(family.schema).iter_errors(record), key=lambda e: str(e.path))
                    if errors:
                        location = "/".join(str(part) for part in errors[0].absolute_path)
                        raise ValueError(f"{root}/{name}/{key}/{location}: {errors[0].message}")
                    if family.validator:
                        family.validator(deepcopy(record))
                    if family.identity:
                        identifier = record.get("id") if isinstance(record, dict) else None
                        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", identifier):
                            raise ValueError(name + " requires a path-safe record id")
                        if key is not None and key != identifier:
                            raise ValueError(name + " map key and id differ")
                        if identifier in identifiers:
                            raise ValueError("record IDs must be globally unique: " + identifier)
                        identifiers[identifier] = (root, name, record)
                    rows.append((family, record))
        if instance.get("id"):
            if instance["id"] in identifiers:
                raise ValueError("record IDs must be globally unique: " + instance["id"])
            identifiers[instance["id"]] = ("research", "id", instance)
        for family, record in rows:
            for ref in family.references(record) if family.references else ():
                target, expected_family = ref if isinstance(ref, tuple) else (ref, None)
                if target is None:
                    continue
                if not isinstance(target, str) or target not in identifiers:
                    raise ValueError(f"{family.name} references unknown record: {target}")
                if expected_family and identifiers[target][1] not in expected_family.split("|"):
                    raise ValueError(f"{family.name} reference has wrong family: {target}")
        from .record_schemas import validate_semantics
        validate_semantics(instance, runtime, identifiers)
        return identifiers


def default_state_contract():
    return StateContract.default()


def register_record_family(contract, root, name, **kwargs):
    contract.register_family(root, name, **kwargs)
