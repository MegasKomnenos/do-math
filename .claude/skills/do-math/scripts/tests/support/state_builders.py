"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy
import hashlib


def current_state(instance=None, runtime=None):
    """The smallest (instance, runtime) the current state contract accepts, plus the caller's fields.

    Every validated state passes the lifecycle rules (``record_schemas.validate_lifecycle``):
    a lifecycle with its exact original input, a runtime status and a UTC clock
    high-water. Storage tests extend this with the families they examine.
    """
    raw = b"fixture input"
    base_instance = {"lifecycle": {"state": "initializing", "input_id": "UI-fixture", "immutable_input": {
        "text": raw.decode(), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}}}
    base_runtime = {"status": "initializing",
                    "last_observed_utc": "2026-01-01T00:00:00+00:00",
                    "inputs": [{"id": "UI-fixture", "text": raw.decode(), "sha256": hashlib.sha256(raw).hexdigest(),
                                "config": {"goal": "fixture"}, "created_at": "2026-01-01T00:00:00+00:00"}]}
    return {**base_instance, **(instance or {})}, {**base_runtime, **(runtime or {})}


def governance_start(instance=None):
    """``instance`` with the empty governance families ``initialization.initialize_state`` gives every instance.

    A domain test that calls a governance function on a small instance starts here
    instead of relying on the function to create these families.
    """
    return {"governance": {}, "governance_sources": {}, "decisions": {}, "grants": {}, **(instance or {})}


def installed_contract():
    """A new StateContract holding the installed families, for a test that adds to it.

    Repositories share default_state_contract(), which never gains a family,
    so a test registers extra families on a contract of its own.
    """
    from do_math.record_schemas import install
    from do_math.state_contract import StateContract
    contract = StateContract()
    install(contract)
    return contract


def with_validator(contract, root, name, validator):
    """Give one family of a test-owned ``contract`` this record validator in place of its own."""
    from dataclasses import replace
    contract._families[root, name] = replace(contract.family(root, name), validator=validator)
    contract._manifest = None
    return contract


def charter_change(engine, **content_changes):
    """Propose explicit changes to the actual current charter; approval stays public."""
    current = engine._governance()["charter"]
    return {"kind": "charter", "record": {"id": engine.ports.clock.new_id("CH"), "kind": "charter",
        "revision": current["revision"] + 1, "supersedes": [current["id"]],
        "content": {**deepcopy(current["content"]), **deepcopy(content_changes)}}}


def policy_change(engine, text):
    return {"kind": "policy", "record": {"id": engine.ports.clock.new_id("PO"), "kind": "policy", "revision": 1,
        "supersedes": [], "content": {"rule_id": "fixture-domain", "text": text,
            "scope": [engine._governance()["goal"]], "reason_refs": [engine._governance()["charter"]["id"]],
            "audit_refs": []}}}


def charter(identifier="CH1", goal="Prove P", **content):
    """A charter record proposing ``goal``; ``content`` replaces its other content fields. It grants no approval."""
    return {"id": identifier, "kind": "charter", "revision": 1, "supersedes": [],
            "content": {"rationale": "Research P", "goal": goal, "desired_result": "A proof",
                        "success_criteria": ["P proved"], "partial_success_criteria": ["Cases settled"],
                        "included_scope": ["P"], "excluded_scope": [], "priorities": ["P"],
                        "preferences": [], "evidence_boundary": "Proof, not preference",
                        "academic_requirements": [], "decision_authority": "user", "stop_conditions": [], **content}}


def charter_record(goal):
    """Author explicit synthetic charter content; this grants no approval."""
    return charter("CH-fixture", goal, rationale="Exercise the explicit synthetic research scenario",
        desired_result="A proof of the supplied mathematical goal", success_criteria=[goal],
        partial_success_criteria=["Record an explicit unresolved obligation"], included_scope=[goal],
        priorities=["Proof"], evidence_boundary="Synthetic model and compiler inputs in a temporary repository")


def approved_governance(instance, records, *, source=("S", "User approves P"), approval_id="D"):
    """``instance`` with ``records`` adopted by one explicit synthetic user approval.

    ``source`` is the preserved user text ``(ID, text)``; the approval
    ``approval_id`` binds its hash and each record's exact content hash, as
    ``governance.initialize_governance`` requires. ``instance`` gains the empty
    governance families first (``governance_start``).
    """
    from do_math import governance
    from do_math.canonical import exact_content_hash
    preserved = governance.preserve_source(*source, origin="user")
    approval = {"id": approval_id, "actor": "user", "source_ref": preserved["id"], "source_sha256": preserved["sha256"],
                "record_hashes": {record["id"]: exact_content_hash(record) for record in records}}
    return governance.initialize_governance(governance_start(instance), preserved, approval, records)
