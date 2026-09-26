"""Installed, explicit feature-five storage contract, distinct from wire schemas."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, replace
from functools import cached_property, lru_cache
import re
from typing import Callable

import jsonschema

from .file_io import json_digest
from .git_store import check_path_segment

STATE_FORMAT_VERSION = 5
STATE_CONTRACT_ID = "do-math-state/6"
# A record ID names its file research/<family>/<id>.json, so it excludes path
# separators and ':'. The validator also applies the Git path segment rule
# (git_store.check_path_segment), which refuses Windows device names.
RECORD_ID = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
_ABSENT = object()


def check_schema(schema):
    """Meta-schema check for a schema from outside the product.

    Built-in family schemas are product constants; their well-formedness is a
    test (test_state_contract_registration), not a check at every process start.
    """
    jsonschema.Draft202012Validator.check_schema(schema)


@dataclass(frozen=True)
class RegisteredFamily:
    root: str
    name: str
    shape: str
    schema: dict
    validator: Callable | None = None
    references: Callable | None = None
    identity: bool = True

    @cached_property
    def checker(self):
        """The schema validator, built once; a registered schema never changes."""
        return jsonschema.Draft202012Validator(self.schema)


class StateContract:
    def __init__(self):
        self._families = {}
        self.validation_generation = 0
        # Generation at which this contract equals the installed default;
        # None for contracts built by hand.
        self.installed_generation = None
        self._manifest = None

    @classmethod
    def default(cls):
        # Installation validates every built-in schema. Keep that validated
        # template, but give each repository an independent mutable contract.
        contract = deepcopy(_default_template(cls))
        contract.installed_generation = contract.validation_generation
        return contract

    def register_family(self, root, name, *, shape="map", schema=None,
                        validator=None, references=None, identity=True):
        if root not in {"research", "runtime"} or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError("invalid family root/name")
        if shape not in {"map", "list", "singleton", "metadata"}:
            raise ValueError("invalid family shape")
        if shape == "metadata" and identity:
            raise ValueError("metadata fields cannot allocate independent record identities")
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
            self.validation_generation += 1
            return
        if schema is None:
            raise ValueError("explicit record schema is required: " + name)
        schema = deepcopy(schema)
        if (shape in {"map", "list"} or identity) and (schema.get("type") != "object" or schema.get("additionalProperties") is not False):
            raise ValueError("record schema must reject unknown fields: " + name)
        self._families[root, name] = RegisteredFamily(root, name, shape, schema, validator, references, identity)
        self.validation_generation += 1

    def family(self, root, name):
        return self._families.get((root, name))

    def families(self):
        return tuple(self._families[key] for key in sorted(self._families))

    def manifest(self):
        """Describe the installed schema; its digest identifies the writer.

        Families change only through register_family, which advances the
        validation generation, so the digest is computed once per generation.
        """
        if self._manifest is None or self._manifest[0] != self.validation_generation:
            families = [{"root": f.root, "name": f.name, "shape": f.shape, "identity": f.identity,
                         "schema": f.schema} for f in self.families()]
            payload = {"contract_id": STATE_CONTRACT_ID, "families": families}
            digest = json_digest(payload)
            self._manifest = (self.validation_generation, digest)
        return {"contract_id": STATE_CONTRACT_ID, "sha256": self._manifest[1]}

    def validate(self, instance, runtime, parent=None):
        """Pure schema and relationship validation; no ID/time allocation.

        ``parent`` is an (instance, runtime) pair already validated under this
        contract. A record equal to the parent's record at the same family and
        ID skips the record-local checks (schema and family validator), whose
        result depends on the record alone. Relations, identity uniqueness and
        semantic rules are still checked over the whole state.
        """
        rows, identifiers = [], {}
        for index, (root, state) in enumerate((("research", instance), ("runtime", runtime))):
            prior_state = parent[index] if parent is not None else {}
            if not isinstance(state, dict):
                raise ValueError(root + " must be an object")
            if root == "research" and state.get("object_format") not in {"sha1", "sha256"}:
                raise ValueError("research object_format is missing or unsupported")
            for name, value in state.items():
                family = self.family(root, name)
                if family is None:
                    raise ValueError("unregistered family: " + root + "/" + name)
                if family.shape == "map":
                    if not isinstance(value, dict):
                        raise ValueError(name + " must be a record map")
                    entries = list(value.items())
                elif family.shape == "list":
                    if not isinstance(value, list):
                        raise ValueError(name + " must be a record list")
                    entries = [(None, row) for row in value]
                else:
                    entries = [(None, value)]
                prior = prior_state.get(name, _ABSENT)
                if family.shape == "list" and isinstance(prior, list):
                    prior = {row.get("id"): row for row in prior if isinstance(row, dict)}
                for key, record in entries:
                    if family.shape in {"map", "list"}:
                        identifier = key if key is not None else record.get("id") if isinstance(record, dict) else None
                        before = prior.get(identifier, _ABSENT) if isinstance(prior, dict) else _ABSENT
                    else:
                        before = prior
                    if before is _ABSENT or before != record:
                        validate_record(family.checker, record, f"{root}/{name}/{key}")
                        if family.validator:
                            family.validator(deepcopy(record))
                    if family.identity:
                        identifier = record.get("id") if isinstance(record, dict) else None
                        if not isinstance(identifier, str) or not re.fullmatch(RECORD_ID, identifier):
                            raise ValueError(name + " requires a path-safe record id")
                        try:
                            check_path_segment(identifier)
                        except ValueError as error:
                            raise ValueError(name + " requires a path-safe record id: " + str(error)) from error
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
        validate_semantics(instance, runtime, identifiers, parent, contract=self)
        return identifiers


def default_state_contract():
    return StateContract.default()


def validate_record(checker, record, label):
    """Raise ValueError naming ``label`` and the first schema violation of ``record``."""
    errors = sorted(checker.iter_errors(record), key=lambda e: str(e.path))
    if errors:
        location = "/".join(str(part) for part in errors[0].absolute_path)
        raise ValueError(f"{label}/{location}: {errors[0].message}")


@lru_cache(maxsize=None)
def installed_checker(root, name):
    """The schema checker of one installed default family, built once per process.

    It is built apart from the shared template, so the copies that
    StateContract.default() makes do not carry a validator.
    """
    return jsonschema.Draft202012Validator(_default_template(StateContract).family(root, name).schema)


@lru_cache(maxsize=16)
def _default_template(contract_type):
    from .record_schemas import install
    contract = contract_type()
    install(contract)
    return contract
