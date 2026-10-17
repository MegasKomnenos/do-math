"""Installed, explicit storage contract, distinct from wire schemas."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property, lru_cache
import re
from typing import Callable

import jsonschema

from .values import check_path_segment, json_digest
from .canonical import same_json_value

# The one stored contract identifier: the root manifest of each snapshot names
# it, and loading accepts no other. Records carry no version marker of their own.
STATE_CONTRACT_ID = "do-math-state/10"
# Archived artifacts live under this prefix; an existing bundle there never changes.
ARTIFACT_ROOT = "runtime/artifacts/"
# A record ID names its file research/<family>/<id>.json, so it excludes path
# separators and ':'. The validator also applies the Git path segment rule
# (values.check_path_segment), which refuses Windows device names.
RECORD_ID = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
_ABSENT = object()


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
    """Record families with their schemas, record validators and references.

    Families are registered while the contract is built (record_schemas.install)
    and never after its first use: validated reads are cached per contract
    object (repository._VALIDATED_READS), and the manifest digest is computed once.
    """

    def __init__(self):
        self._families = {}
        self._manifest = None

    def register_family(self, root, name, *, shape="map", schema=None,
                        validator=None, references=None, identity=True):
        if root not in {"research", "runtime"} or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError("invalid family root/name")
        if shape not in {"map", "list", "singleton", "metadata"}:
            raise ValueError("invalid family shape")
        if shape == "metadata" and identity:
            raise ValueError("metadata fields cannot allocate independent record identities")
        if self.family(root, name) is not None:
            raise ValueError("record family already registered: " + name)
        if schema is None:
            raise ValueError("explicit record schema is required: " + name)
        schema = deepcopy(schema)
        if (shape in {"map", "list"} or identity) and (schema.get("type") != "object" or schema.get("additionalProperties") is not False):
            raise ValueError("record schema must reject unknown fields: " + name)
        self._families[root, name] = RegisteredFamily(root, name, shape, schema, validator, references, identity)
        self._manifest = None

    def family(self, root, name):
        return self._families.get((root, name))

    def families(self):
        return tuple(self._families[key] for key in sorted(self._families))

    def manifest(self):
        """Describe the registered schemas; its digest identifies the writer.

        The digest is computed once; only register_family resets it.
        """
        if self._manifest is None:
            families = [{"root": f.root, "name": f.name, "shape": f.shape, "identity": f.identity,
                         "schema": f.schema} for f in self.families()]
            self._manifest = json_digest({"contract_id": STATE_CONTRACT_ID, "families": families})
        return {"contract_id": STATE_CONTRACT_ID, "sha256": self._manifest}

    def validate(self, instance, runtime, parent=None):
        """Pure schema and relationship validation; no ID/time allocation.

        ``parent`` is an (instance, runtime) pair already validated under this
        contract. A record equal to the parent's record at the same family and
        ID skips the record-local checks (schema and family validator), whose
        result depends on the record alone. Relations, identity uniqueness and
        semantic rules are still checked over the whole state.

        Equality is the canonical storage-value comparison: booleans and
        integers differ even when Python compares them equal. Encoding uses
        the same rule, so skipping a check cannot retain another JSON value's
        bytes. Floats are rejected by candidate sealing before comparison.
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
                    if before is _ABSENT or not same_json_value(before, record):
                        validate_record(family.checker, record, f"{root}/{name}/{key}")
                        if family.validator:
                            family.validator(deepcopy(record))
                    if family.identity:
                        # The family schema holds the RECORD_ID pattern; the
                        # path segment rule adds what a pattern cannot say.
                        identifier = record.get("id") if isinstance(record, dict) else None
                        if not isinstance(identifier, str):
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


@lru_cache(maxsize=1)
def default_state_contract():
    """The installed contract, built once per process and shared by every repository.

    Nothing registers a family after installation, so the shared object never
    changes. A test that needs another family builds its own StateContract.
    """
    from .record_schemas import install
    contract = StateContract()
    install(contract)
    return contract


def validate_record(checker, record, label):
    """Raise ValueError naming ``label`` and the first schema violation of ``record``."""
    errors = sorted(checker.iter_errors(record), key=lambda e: str(e.path))
    if errors:
        location = "/".join(str(part) for part in errors[0].absolute_path)
        raise ValueError(f"{label}/{location}: {errors[0].message}")
