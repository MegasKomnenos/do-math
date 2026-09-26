"""Knowledge currentness and Lean trust-environment transitions.

This module records and propagates semantic state.  It does not run formal
tools, enforce OS isolation, or infer mathematical equivalence.
"""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .repository import exact_content_hash, new_id, semantic_content_hash
from .input_basis import capture_sources, sources_current
from .planning import READ_REFERENCE_FIELDS, READ_REFERENCE_ID_FIELDS, record_index


def _hash(record: Any) -> str:
    if isinstance(record, dict) and record.get('family') in {'formal_results', 'expositions'}:
        from .knowledge_records import record_digest
        return record_digest(record)
    return semantic_content_hash(record)


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty")


# planning.RECORD_FAMILIES keys whose records a basis row or an impact closure can name.
BASIS_FAMILIES = frozenset({"knowledge", "formal-result", "exposition", "identity-assessment", "assessment-use",
                            "kind-definition", "trust-environment", "relation", "goal-judgment",
                            "task", "activity", "execution"})


def _basis_records(instance: dict, runtime: dict) -> dict[str, dict]:
    return {rid: record for rid, (_, record) in record_index(instance, runtime, families=BASIS_FAMILIES).items()}


def _status(record: dict) -> str:
    for key in ("status", "lifecycle", "decision"):
        if isinstance(record.get(key), str):
            return record[key]
    return "present"


def capture_basis(instance: dict, runtime: dict, record_ids: list[str]) -> list[dict]:
    if not isinstance(record_ids, list) or len(record_ids) != len(set(record_ids)):
        raise ValueError("record_ids must be a list of distinct IDs")
    basis = []
    records = _basis_records(instance, runtime)
    for record_id in record_ids:
        _require_text(record_id, "record ID")
        record = records.get(record_id)
        if record is None:
            raise ValueError(f"unknown record ID: {record_id}")
        basis.append({"id": record_id, "sha256": _hash(record), "status": _status(record)})
    return basis


def validate_basis(basis: list[dict], instance: dict, runtime: dict) -> dict:
    reasons: list[str] = []
    if not isinstance(basis, list):
        return {"valid": False, "reasons": ["basis_not_a_list"]}
    seen: set[str] = set()
    records = _basis_records(instance, runtime)
    for row in basis:
        if not isinstance(row, dict) or set(row) != {"id", "sha256", "status"}:
            reasons.append("invalid_basis_row")
            continue
        record_id = row["id"]
        if not isinstance(record_id, str) or record_id in seen:
            reasons.append(f"duplicate_or_invalid_id:{record_id}")
            continue
        seen.add(record_id)
        record = records.get(record_id)
        if record is None:
            reasons.append(f"missing:{record_id}")
            continue
        if _hash(record) != row["sha256"]:
            reasons.append(f"hash_changed:{record_id}")
        if _status(record) != row["status"]:
            reasons.append(f"status_changed:{record_id}")
    return {"valid": not reasons, "reasons": reasons}


# Bookkeeping has no authored mathematical meaning. Unknown fields remain in
# the projection, so adding a new author field cannot silently weaken checks.
_DECISION_BOOKKEEPING = frozenset({
    "id", "revision", "status", "lifecycle", "history", "reviews", "review_history",
    "use_history", "verified_at", "created_at", "updated_at", "formal", "identity_assessment",
    "review_cycle_id", "previous_review_cycle_id", "producer_execution", "producer_execution_ids",
    "source_ref", "actor_ref", "task_id", "required_reviews", "use_suspended", "use_suspensions",
    "use_suspension_reasons", "source_basis", "relation_endpoint_basis",
})


def content_hash(record: dict) -> str:
    return _hash({key: value for key, value in record.items() if key not in _DECISION_BOOKKEEPING})


def decision_reference(record: dict, instance: dict) -> dict:
    formal = instance.get("formal_results", {}).get(record.get("formal_result_id"), {})
    environment = formal.get("trust_environment_id")
    return {"id": record["id"], "revision": record.get("revision", 1),
            "content_sha256": content_hash(record), "status": _status(record),
            "use_suspended": bool(record.get("use_suspended")),
            "usable": assess_use(record, instance)["valid"],
            "trust_environment_id": formal.get("trust_environment_id"),
            "trust_environment_state": ({"status": instance.get("trust_environments", {}).get(environment, {}).get("status"),
                                          "active": instance.get("active_trust_environment") == environment} if environment else None),
            "source_basis": deepcopy(record.get("source_basis", []))}


# Impact also follows evidence and provenance fields beyond the shared read fields.
_STRICT_REFERENCE_KEYS = frozenset({key for key, mode in READ_REFERENCE_FIELDS.items() if mode == "strict"}
                                   | {"formal_result_refs", "assessment_refs", "knowledge_refs", "record_refs"})
_REFERENCE_KEYS = frozenset({key for key, mode in READ_REFERENCE_FIELDS.items() if mode == "lenient"} | {
    "used_sources", "exact_refs", "record_refs", "knowledge_refs",
    "evidence_refs", "source_refs", "formal_result_refs", "assessment_refs", "origin_refs",
})
# Preserved earlier versions are history, not current dependencies of the record.
_HISTORY_KEYS = frozenset({"history", "use_history", "review_history", "revision_history",
                           "assessment_history", "governance_history", "previous_initial_reviews"})
_KNOWLEDGE_ID = re.compile(r"^KN-[A-Z0-9][A-Z0-9-]*$")
_ID_KEYS = frozenset({"id", "ref", "record_id", "knowledge_id"})


def _field_refs(value: Any, *, strict: bool, known_ids: set[str]) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, str):
        if strict or value in known_ids or _KNOWLEDGE_ID.fullmatch(value):
            refs.add(value)
    elif isinstance(value, list):
        for item in value:
            refs.update(_field_refs(item, strict=strict, known_ids=known_ids))
    if isinstance(value, dict):
        identifiers = [item for key, item in value.items()
                       if key in _ID_KEYS and isinstance(item, str)]
        for item in identifiers:
            if strict or item in known_ids or _KNOWLEDGE_ID.fullmatch(item):
                refs.add(item)
        # A source-ref object is a locator.  Its path/hash/range strings are
        # validated by context_store, not interpreted as knowledge IDs here.
        if not identifiers and strict:
            for item in value.values():
                refs.update(_field_refs(item, strict=True, known_ids=known_ids))
    return refs


def _explicit_refs(value: Any, known_ids: set[str]) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _HISTORY_KEYS:
                continue
            if key in _STRICT_REFERENCE_KEYS:
                refs.update(_field_refs(item, strict=True, known_ids=known_ids))
            elif key in _REFERENCE_KEYS:
                refs.update(_field_refs(item, strict=False, known_ids=known_ids))
            elif key == "basis" and isinstance(item, list):
                refs.update(_field_refs(item, strict=False, known_ids=known_ids))
            else:
                refs.update(_explicit_refs(item, known_ids))
    elif isinstance(value, list):
        for item in value:
            refs.update(_explicit_refs(item, known_ids))
    return refs


def assess_research_use(record: dict, instance: dict, _visiting=None) -> dict:
    """Use a current research record at its stated evidence level, without certifying it.

    The shared record premises are knowledge_records.premise_failures; research use
    adds use suspension, an active exposition and research-level dependencies."""
    from .knowledge_records import premise_failures
    identifier = record.get('id')
    visiting = set(_visiting or ())
    reasons = []
    if not identifier or identifier in visiting:
        reasons.append('missing_or_cyclic_research_dependency')
    reasons.extend('research_' + failure for failure in premise_failures(instance, record))
    if record.get('use_suspended') and 'research_record_not_active' not in reasons:
        reasons.append('research_record_not_active')
    exposition = instance.get('expositions', {}).get(record.get('exposition_id'), {})
    if exposition.get('lifecycle') != 'active':
        reasons.append('research_exposition_not_active')
    if reasons:
        return {'valid': False, 'reasons': reasons}
    visiting.add(identifier)
    for dependency in record.get('dependencies', []):
        prior = instance.get('knowledge', {}).get(dependency)
        if prior is None or not assess_research_use(prior, instance, visiting)['valid']:
            reasons.append('research_dependency_not_current:' + dependency)
    return {'valid': not reasons, 'reasons': reasons}


def assess_use(record: dict, instance: dict) -> dict:
    if not isinstance(record, dict):
        raise TypeError("record must be an object")
    from .knowledge_records import usable_links, formal_usable, assessment_current
    family = record.get("family", "knowledge")
    if family == "knowledge":
        links = usable_links(instance, record.get("id"))
        valid = bool(links)
        return {"valid": valid, "reasons": [] if valid else ["no_current_verified_exposition"], "basis": links}
    if family == "formal_results":
        valid = formal_usable(instance, record)
        return {"valid": valid, "reasons": [] if valid else ["formal_result_not_current"], "basis": []}
    if family == "identity_assessments":
        uses = [use for use in instance.get("assessment_uses", {}).values()
                if use['assessment_id'] == record['id'] and use['status'] == 'active']
        valid = assessment_current(instance, record['id']) and bool(uses)
        return {"valid": valid, "reasons": [] if valid else ["assessment_not_current"],
                "basis": [{"assessment_id": record['id'], "assessment_use_id": use['id']} for use in uses] if valid else []}
    return {"valid": False, "reasons": ["record_is_not_a_verified_knowledge_authority"], "basis": []}


def _impact_refs(record, known_ids):
    from .relation_refs import relation_endpoints
    refs = _explicit_refs(record, known_ids)
    # Only declared authority coordinates count; prose and historical judgments do not.
    for key in READ_REFERENCE_ID_FIELDS:
        if isinstance(record.get(key), str):
            refs.add(record[key])
    # Evidence locators use _explicit_refs' existing record filter. Unlike a
    # read/source catalog, impact closure cannot treat a file path as a record.
    refs.update(relation_endpoints(record))
    refs.update(relation_endpoints(record.get('relation_claim') or {}))
    return refs


def plan_impact(instance, runtime, roots, declared_impact, *, sensitive=False, excluded_dependents=()):
    from .knowledge_records import usable_links
    records = _basis_records(instance, runtime)
    roots, declared = set(roots), set(declared_impact)
    excluded = set(excluded_dependents)
    if not roots or roots - set(records):
        raise ValueError("impact roots must exist")
    if declared - set(records):
        raise ValueError("declared impact refers to unknown records")
    if excluded - set(records):
        raise ValueError("excluded impact dependents must exist")
    known = set(records)
    # Record references and K support links stay fixed while the closure grows.
    refs = {rid: _impact_refs(record, known) for rid, record in records.items()}
    links = {kid: usable_links(instance, kid) for kid in instance.get("knowledge", {})}
    affected = set(roots)
    while True:
        found = {rid for rid, targets in refs.items() if rid not in excluded and targets & affected}
        # K depends on the available positive links, not on every historical vote.
        # An unaffected independent link continues to support the same K.
        for kid, support in links.items():
            if support and all({link['assessment_id'], link['assessment_use_id']} & affected for link in support):
                found.add(kid)
        if found <= affected:
            break
        affected |= found
    computed = affected - roots
    unknown = sorted({ref for rid in affected for ref in refs[rid] if ref not in records})
    plan = {"roots": sorted(roots), "computed_impact": sorted(computed), "declared_impact": sorted(declared),
            "missing_declarations": sorted(computed - declared), "extra_declarations": sorted(declared - computed),
            "unresolved_refs": unknown, "sensitive": sensitive,
            "requires_independent_review": bool(sensitive or computed != declared or unknown),
            "basis": {rid: _hash(records[rid]) for rid in sorted(affected | declared)}}
    plan["digest"] = _hash(plan)
    return plan


def _confirmed_impact(plan, confirmation):
    if plan.get("digest") != _hash({key: value for key, value in plan.items() if key != "digest"}):
        raise ValueError("impact plan digest is invalid")
    affected = set(plan["computed_impact"])
    if plan["requires_independent_review"]:
        confirmation = confirmation or {}
        if (confirmation.get("plan_digest") != plan["digest"] or confirmation.get("decision") != "approve"
                or not confirmation.get("review_ref") or not confirmation.get("reviewer_ref")
                or not confirmation.get("producer_ref") or confirmation["reviewer_ref"] == confirmation["producer_ref"]
                or set(confirmation.get("affected_ids", [])) != affected | set(plan["declared_impact"])):
            raise ValueError("impact requires independent scope and disposition confirmation")
        affected |= set(plan["declared_impact"])
    return affected


def _apply_impact_effects(instance, runtime, affected, roots, *, reason, impact_digest, in_place=False):
    # in_place is for callers that already hold their own copies of both views.
    output, new_runtime = (instance, runtime) if in_place else (deepcopy(instance), deepcopy(runtime))
    records = _basis_records(output, new_runtime)
    semantic_only = all(records[rid].get('family') in {'identity_assessments', 'assessment_uses'} for rid in roots)
    for rid in sorted(affected):
        record = records[rid]
        family = record.get("family")
        if family == "formal_results":
            if semantic_only:
                continue  # A semantic judgment defect does not refute checked Lean code.
            record["formal_use"] = "suspended"
        elif family == "assessment_uses":
            if record.get("status") != "withdrawn":
                record["status"] = "suspended"
                record.pop("environment_revalidation", None)
        elif family == "identity_assessments":
            for use in output.get("assessment_uses", {}).values():
                if use["assessment_id"] == rid and use["status"] != "withdrawn":
                    use["status"] = "suspended"
                    use.pop("environment_revalidation", None)
            continue  # Sealed judgment is immutable.
        elif rid in new_runtime.get("tasks", {}):
            if isinstance(record.get("assessment"), dict):
                record["assessment"]["current"] = False
            # Task lifecycle belongs to TASKS; its readiness consumes this currentness.
            record["input_current"] = False
        elif record in output.get("relations", []):
            record["status"] = "suspended"
        elif record in output.get("goal_judgments", []):
            record["current"] = False
        elif family in {"knowledge", "expositions"}:
            # Currentness is derived from the actual premise/use, not a duplicate lifecycle.
            continue
        elif rid in new_runtime.get('executions', {}) or rid in new_runtime.get('activities', {}):
            # Preserve historical attempts and activity results. Their input
            # snapshots and execution currentness checks own validity; the
            # affected IDs remain in the reassessment event below.
            continue
        else:
            record["input_current"] = False
        record.setdefault("use_history", []).append({"reason": reason, "impact_digest": impact_digest})
    new_runtime.setdefault("history", []).append({"kind": "knowledge_reassessment_required",
        "affected_ids": sorted(affected), "reason": reason, "impact_digest": impact_digest})
    if affected:
        action = {"role": "research_plan", "reason": "knowledge currentness changed", "affected_ids": sorted(affected)}
        if not any(all(queued.get(key) == value for key, value in action.items())
                   for queued in new_runtime.setdefault("queue", [])):
            action["id"] = action["lineage_id"] = new_id("AC")
            new_runtime["queue"].append(action)
    return output, new_runtime


def apply_reviewed_impacts(instance, runtime, plans, confirmations, *, reason):
    """Apply one already-current S0 decision set without recomputing an S1 plan."""
    _require_text(reason, "reason")
    if not isinstance(plans, dict) or not plans:
        raise ValueError("reviewed impacts require at least one named plan")
    affected, roots = set(), set()
    for scope, plan in plans.items():
        confirmation = confirmations.get(scope) if isinstance(confirmations, dict) else None
        affected.update(_confirmed_impact(plan, confirmation))
        roots.update(plan["roots"])
    impact_digest = _hash({"plan_digests": sorted(plan["digest"] for plan in plans.values()),
                           "affected_ids": sorted(affected)})
    return _apply_impact_effects(instance, runtime, affected, roots,
        reason=reason, impact_digest=impact_digest)


def apply_impact(instance, runtime, plan, *, reason, independent_confirmation=None):
    _require_text(reason, "reason")
    current = plan_impact(instance, runtime, plan["roots"], plan["declared_impact"], sensitive=plan["sensitive"])
    if current != plan:
        raise ValueError("impact plan is stale or altered")
    return _apply_current_plan(instance, runtime, plan, reason=reason,
        independent_confirmation=independent_confirmation)


def _apply_current_plan(instance, runtime, plan, *, reason, independent_confirmation=None, in_place=False):
    # For a plan the caller has just computed from these same views. A supplied
    # or stored plan goes through apply_impact, which recomputes it first.
    _require_text(reason, "reason")
    affected = _confirmed_impact(plan, independent_confirmation)
    return _apply_impact_effects(instance, runtime, affected, set(plan["roots"]),
        reason=reason, impact_digest=plan["digest"], in_place=in_place)


def _propagate(instance, runtime, roots, reason):
    # System-observed failures have a computed scope. Producer changes must use
    # plan_impact/apply_impact with their declaration before altering the root.
    preview = plan_impact(instance, runtime, roots, [])
    plan = plan_impact(instance, runtime, roots, preview["computed_impact"])
    if plan["requires_independent_review"]:
        runtime.setdefault("pending_knowledge_impacts", []).append({"plan": plan, "reason": reason})
        return
    # Callers pass their own copies, and this plan was just computed from them.
    _apply_current_plan(instance, runtime, plan, reason=reason, in_place=True)


def assessment_reassessment_proposal(instance, assessment_id, *, runtime):
    """Review the original judgment's validity, never silently reinterpret a new K vote."""
    assessment = instance['identity_assessments'][assessment_id]
    original = runtime.get('review_cycles', {}).get(assessment.get('review_cycle_id'), {})
    authors = (set(assessment.get('execution_ids', []))
        | set(original.get('proposal', {}).get('producer_execution_ids', []))
        | {entry['execution_id'] for entry in original.get('results', {}).values()})
    return {'revision': 1, 'producer_execution_ids': sorted(authors),
        'assessment_reassessment': {'assessment_id': assessment_id, 'assessment_sha256': _hash(assessment),
            'policy_ref': assessment['policy_ref'], 'original_basis': deepcopy(assessment['basis']),
            'original_decision': assessment['decision'],
            'predicate': 'The original judgment kind, value, basis and resulting effect are justified.',
            'decision_meanings': {'match': 'reaffirmed', 'mismatch': 'error_confirmed', 'unresolved': 'inconclusive'}}}


def _assessment_disposition(instance, runtime, assessment_id, status, *, reason, actor_ref,
                            reason_refs, reassessment_ref=None):
    from .knowledge_records import set_assessment_use
    output, run = deepcopy(instance), deepcopy(runtime)
    use = next(u for u in output['assessment_uses'].values() if u['assessment_id'] == assessment_id)
    if reassessment_ref and any(h.get('reassessment_ref') == reassessment_ref for h in use['history']):
        return output, run
    old_status = use['status']
    # Calculate fallout while the original support is still visible.
    if status != 'active' and old_status == 'active':
        _propagate(output, run, [assessment_id], reason)
    # Restore the root's state for the transition primitive: propagation can also
    # reach its AU, but its own explicit disposition must retain the actual prior state.
    use = next(u for u in output['assessment_uses'].values() if u['assessment_id'] == assessment_id)
    use['status'] = old_status
    output = set_assessment_use(output, assessment_id, status, reason, actor_ref)
    use = next(u for u in output['assessment_uses'].values() if u['assessment_id'] == assessment_id)
    evidence = {'reason_refs': list(reason_refs)}
    if reassessment_ref:
        evidence['reassessment_ref'] = reassessment_ref
        evidence['assessment_sha256'] = _hash(output['identity_assessments'][assessment_id])
        evidence['proposal_digest'] = run['review_cycles'][reassessment_ref]['proposal_digest']
    if old_status == status:
        use['history'].append({'from': old_status, 'to': status, 'reason': reason, 'actor_ref': actor_ref})
    use['history'][-1].update(evidence)
    return output, run


def suspend_assessment_use(instance, runtime, assessment_id, *, reason, actor_ref, reason_refs):
    """Apply a caller-authorized confirmed defect/independent semantic objection.

    This domain transition does not authorize ordinary reports or external actions.
    The central owner must open the bounded reassessment using the frozen policy.
    """
    if not isinstance(reason_refs, list) or not reason_refs or any(not isinstance(r, str) or not r for r in reason_refs):
        raise ValueError('suspension requires concrete defect or independent objection references')
    return _assessment_disposition(instance, runtime, assessment_id, 'suspended', reason=reason,
        actor_ref=actor_ref, reason_refs=reason_refs)


def apply_assessment_reassessment(instance, runtime, assessment_id, review_cycle_id, *, reason, actor_ref):
    """Consume a sealed independent review of the exact original judgment.

    Replay uses the existing review state machine, including scope, sealing and
    finite-round decisions. Reviewer semantics are evidence, not a machine proof.
    """
    from . import review_cycle as reviews
    assessment = instance['identity_assessments'][assessment_id]
    cycle = runtime.get('review_cycles', {}).get(review_cycle_id, {})
    expected = assessment_reassessment_proposal(instance, assessment_id, runtime=runtime)
    if (cycle.get('proposal', {}).get('assessment_reassessment') != expected['assessment_reassessment']
            or cycle.get('policy_ref') != assessment['policy_ref']):
        raise ValueError('reassessment must identify the exact original judgment and policy')
    original = runtime.get('review_cycles', {}).get(assessment.get('review_cycle_id'), {})
    if not original or cycle.get('review_policy') != original.get('review_policy'):
        raise ValueError('reassessment must retain the original review policy')
    reviews._check_proposal(cycle)
    authors = set(expected['producer_execution_ids'])
    if not authors <= set(cycle['proposal'].get('producer_execution_ids', [])):
        raise ValueError('reassessment omits original author exclusions')
    replay = reviews.validate_sealed_review(cycle, runtime, instance=instance,
        excluded_execution_ids=authors)
    status = {'match': 'active', 'mismatch': 'withdrawn', 'unresolved': 'suspended'}[replay['decision']]
    if status == 'active':
        from .knowledge_records import assessment_current
        # Reaffirming the original judgment does not establish its present premises.
        if not assessment_current(instance, assessment_id):
            status = 'suspended'
    return _assessment_disposition(instance, runtime, assessment_id, status, reason=reason,
        actor_ref=actor_ref, reason_refs=[entry['execution_id'] for entry in replay['results'].values()],
        reassessment_ref=review_cycle_id)


def validate_changes(changes: dict) -> None:
    """Structural revision rules shared by author preview and application."""
    if not isinstance(changes, dict) or not changes:
        raise ValueError("changes must be a nonempty object")
    forbidden = _DECISION_BOOKKEEPING
    if forbidden & set(changes):
        raise ValueError("changes contain engine-owned fields")


def revision_roots(instance, knowledge_id):
    record = instance["knowledge"][knowledge_id]
    roots = {knowledge_id, record["exposition_id"]}
    # Formal results are immutable and may support other expositions. Replacing
    # source does not invalidate the original result merely because it exists.
    return sorted(roots)


def replace_knowledge(instance: dict, runtime: dict, knowledge_id: str, changes: dict,
                      *, reason: str, actor_ref: str, replacement_id=None,
                      reserved_dependency_ids=()) -> tuple[dict, dict]:
    """Create one replacement after its bundle's impact disposition is complete."""
    from . import knowledge_records as kr
    _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    validate_changes(changes)
    permitted = {"kind", "title", "statement", "explanation", "summary", "definitions", "assumptions",
                 "lean_code", "declaration_names", "dependencies", "source_refs", "origin_refs",
                 "confirmed_scope", "epistemic_status", "selection_relevance", "uncertainty_assessment", "relation_claim"}
    if set(changes) - permitted:
        raise ValueError("unsupported authored knowledge fields")
    old = instance["knowledge"][knowledge_id]
    view = kr.proposal_view(instance, knowledge_id)
    candidate = {key: deepcopy(value) for key, value in view.items() if key in permitted}
    candidate.update(deepcopy(changes))
    if replacement_id is not None:
        candidate["id"] = replacement_id
    from .knowledge_io import import_candidate
    output, new_runtime, actual_replacement_id = import_candidate(instance, runtime, candidate,
        source_ref=(old.get("origin_refs") or [actor_ref])[0], actor_ref=actor_ref,
        reserved_dependency_ids=reserved_dependency_ids)
    replacement = output["knowledge"][actual_replacement_id]
    replacement["supersedes"] = knowledge_id
    replacement["revision"] = old.get("revision", 1) + 1
    replacement["revision_reason"] = reason
    output["knowledge"][knowledge_id]["lifecycle"] = "superseded"
    output["expositions"][old["exposition_id"]]["lifecycle"] = "superseded"
    old_fid = old.get("formal_result_id")
    # Reuse unchanged formal evidence only while it is currently usable.
    formal_changed = any(candidate.get(key) != view.get(key) for key in ("lean_code", "declaration_names", "dependencies"))
    reuse_formal = not formal_changed and kr.formal_usable(
        output, output.get("formal_results", {}).get(old_fid, {}))
    if reuse_formal:
        unused = replacement.get("formal_result_id")
        if unused:
            del output["formal_results"][unused]
        replacement["formal_result_id"] = old_fid
        output["expositions"][replacement["exposition_id"]]["formal_result_id"] = old_fid
    # Superseding the authored record retires its pending checks at the domain
    # boundary, including callers that apply a revision through integration.
    # Completed executions and unrelated work remain available as history.
    new_runtime["queue"] = [action for action in new_runtime.get("queue", [])
        if action.get("target") != actual_replacement_id and not (
            action.get("target") == knowledge_id and (
                action.get("role") in {"formal_check", "identity_review"}
                or (action.get("role") == "supplemental_research" and action.get("review_cycle_id"))))]
    next_role = "identity_review" if reuse_formal else "formal_check"
    if not replacement.get("formal_result_id"):
        next_role = "research_plan"
    action_id = new_id("AC")
    new_runtime["queue"].append({"id": action_id, "lineage_id": action_id, "role": next_role,
        "target": actual_replacement_id, "reason": reason})
    return output, new_runtime


def revise_knowledge(instance: dict, runtime: dict, knowledge_id: str, changes: dict,
                     *, reason: str, actor_ref: str, declared_impact=None,
                     independent_confirmation=None, replacement_id=None) -> tuple[dict, dict]:
    roots = revision_roots(instance, knowledge_id)
    preview = plan_impact(instance, runtime, roots, declared_impact or [])
    # No declaration is harmless only when there are no downstream consumers.
    output, new_runtime = _apply_current_plan(instance, runtime, preview, reason=reason,
                                              independent_confirmation=independent_confirmation)
    return replace_knowledge(output, new_runtime, knowledge_id, changes,
        reason=reason, actor_ref=actor_ref, replacement_id=replacement_id)


def invalidate_knowledge(instance, runtime, knowledge_id, *, reason, actor_ref,
                         declared_impact=None, independent_confirmation=None):
    _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    plan = plan_impact(instance, runtime, [knowledge_id], declared_impact or [])
    output, new_runtime = _apply_current_plan(instance, runtime, plan, reason=reason,
                                              independent_confirmation=independent_confirmation)
    output["knowledge"][knowledge_id].update(lifecycle="withdrawn", withdrawal_reason=reason, withdrawn_by=actor_ref)
    return output, new_runtime


def suspend_for_source_change(instance, runtime, knowledge_id, *, source_name, reason, actor_ref):
    _require_text(source_name, "source_name"); _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    output, new_runtime = deepcopy(instance), deepcopy(runtime)
    record = output["knowledge"][knowledge_id]
    xid = record["exposition_id"]
    for assessment in output.get("identity_assessments", {}).values():
        if assessment["exposition_id"] == xid:
            for use in output.get("assessment_uses", {}).values():
                if use["assessment_id"] == assessment["id"] and use["status"] != "withdrawn":
                    use["status"] = "suspended"
                    use.pop("environment_revalidation", None)
                    use.setdefault("use_history", []).append({"reason": reason,
                        "source_name": source_name, "actor_ref": actor_ref})
    _propagate(output, new_runtime, {knowledge_id}, reason)
    return output, new_runtime


def register_environment(instance: dict, toolchain: dict,
                         allowed_axioms: list[str]) -> tuple[dict, str]:
    if not isinstance(toolchain, dict) or not toolchain:
        raise ValueError("toolchain must be a nonempty object")
    if (not isinstance(allowed_axioms, list) or len(allowed_axioms) != len(set(allowed_axioms))
            or any(not isinstance(item, str) or not item for item in allowed_axioms)):
        raise ValueError("allowed_axioms must contain distinct nonempty strings")
    output = deepcopy(instance); environment_id = new_id("TE")
    output.setdefault("trust_environments", {})[environment_id] = {
        "id": environment_id, "toolchain": deepcopy(toolchain),
        "allowed_axioms": list(allowed_axioms), "status": "registered"}
    return output, environment_id


def begin_transition(instance: dict, new_env_id: str) -> dict:
    from . import knowledge_records as kr
    from .formal import FORMAL_EVIDENCE_FIELDS, lean_source_sha256
    environments = instance.get("trust_environments", {})
    if new_env_id not in environments or environments[new_env_id].get("status") == "invalid":
        raise ValueError("unknown or invalid transition environment")
    old_env_id = instance.get("active_trust_environment")
    if old_env_id == new_env_id:
        raise ValueError("new trust environment is already active")
    targets = []
    for kid, record in sorted(instance.get("knowledge", {}).items()):
        formal = instance.get("formal_results", {}).get(record.get("formal_result_id"))
        if record.get("lifecycle") != "active" or not formal or formal.get("publication_state") != "accepted":
            continue
        verification = formal.get("verification", {})
        targets.append({"id": kid, "formal_result_id": formal["id"],
            "exposition_id": record["exposition_id"],
            "source_sha256": lean_source_sha256(formal["lean_code"]),
            "basis": {"id": kid, "sha256": _hash(record), "status": _status(record)},
            "formal_basis": kr.record_digest(formal), "exposition_basis": kr.record_digest(instance["expositions"][record["exposition_id"]]),
            **{field: deepcopy(verification.get(field)) for field in FORMAL_EVIDENCE_FIELDS},
            "previous_environment_ids": [formal.get("trust_environment_id")]})
    return {"id": new_id("TR"), "from_environment": old_env_id, "to_environment": new_env_id,
            "targets": targets, "results": {}, "status": "checking"}


def record_transition_result(instance: dict, transition: dict, result_for_id: dict) -> dict:
    environment_id = transition.get("to_environment")
    if environment_id not in instance.get("trust_environments", {}):
        raise ValueError(f"unknown trust environment: {environment_id}")
    targets = {target["id"] for target in transition.get("targets", [])}
    result = deepcopy(result_for_id)
    record_id = result.get("id")
    if record_id not in targets: raise ValueError(f"result is not for a transition target: {record_id}")
    if result.get("status") not in {"verified", "failed", "rejected", "unavailable"}:
        raise ValueError("transition result has an unsupported status")
    output = deepcopy(transition); output.setdefault("results", {})[record_id] = result
    output["status"] = "ready" if set(output["results"]) == targets else "checking"
    return output


def _transition_without_identity_reviews(transition):
    normalized = deepcopy(transition)
    for result in normalized.get("results", {}).values():
        result.pop("identity_review", None)
    return normalized


def _staged_review_basis(instance, transition, knowledge_id):
    from . import knowledge_records as kr
    target = next((row for row in transition["targets"] if row["id"] == knowledge_id), None)
    if target is None:
        raise ValueError("staged review target is not in the transition")
    record = instance["knowledge"][knowledge_id]
    formal = instance["formal_results"][target["formal_result_id"]]
    verification = {key: deepcopy(value) for key, value in transition["results"][knowledge_id].items()
                    if key not in {"id", "identity_review"}}
    environment = instance["trust_environments"][transition["to_environment"]]
    view = kr.formal_overlay(instance, formal["id"], verification=verification,
                             trust_environment_id=transition["to_environment"])
    return {
        "identity_basis": kr.identity_basis(view, knowledge_id),
        "transition_basis": exact_content_hash({
            "transition_id": transition["id"], "target": target,
            "verification": verification, "target_environment": environment,
            "from_environment": transition["from_environment"],
        }),
        "target_environment": deepcopy(environment),
        "live_identity_basis": kr.identity_basis(instance, knowledge_id),
        "record": record,
    }


def _validated_staged_identity_review(instance, transition, knowledge_id, receipt, runtime):
    from . import knowledge_records as kr
    from .review_cycle import validate_sealed_review, identity_assessment
    stored = runtime.get("trust_transitions", {}).get(transition.get("id"))
    if stored is None or _transition_without_identity_reviews(stored) != _transition_without_identity_reviews(transition):
        raise ValueError("staged identity review transition is stale or belongs to another transition")
    cycle = runtime.get("review_cycles", {}).get(receipt.get("review_cycle_id"))
    if cycle is None or cycle.get("transition_id") != transition["id"] or cycle.get("knowledge_id") != knowledge_id:
        raise ValueError("staged identity review belongs to another transition target")
    basis = _staged_review_basis(instance, transition, knowledge_id)
    staged = cycle.get("staged_candidate", {})
    if (cycle.get("identity_basis") != basis["identity_basis"]
            or staged.get("identity_basis") != basis["identity_basis"]
            or staged.get("transition_basis") != basis["transition_basis"]
            or staged.get("target_environment") != basis["target_environment"]):
        raise ValueError("staged identity review basis changed")
    environment_id = instance.get("active_trust_environment")
    expected_premises = {
        "identity_basis": basis["live_identity_basis"],
        "active_trust_environment": environment_id,
        "trust_environment": deepcopy(instance.get("trust_environments", {}).get(environment_id)),
        "review_policy": deepcopy(instance.get("review_policy")),
        "governance": deepcopy(instance.get("governance", {})),
    }
    if cycle.get("publication_premises") != expected_premises:
        raise ValueError("staged identity review publication premises changed")
    validate_sealed_review(cycle, runtime, instance=instance)
    expected = {
        **identity_assessment(cycle, reason="Sealed staged identity review"),
        "policy_ref": cycle["policy_ref"],
        "identity_basis": deepcopy(cycle["identity_basis"]),
        "transition_id": transition["id"],
        "knowledge_id": knowledge_id,
        "transition_basis": basis["transition_basis"],
    }
    if receipt != expected or expected["decision"] != "match" or not expected["scope_complete"]:
        raise ValueError("staged identity review receipt is stale, altered, or not a complete match")
    return expected


def activate_transition(instance: dict, transition: dict, *, runtime=None) -> dict:
    from . import knowledge_records as kr
    from .formal import compare_formal_results
    output = deepcopy(instance)
    environments = output.get("trust_environments", {})
    target_env_id = transition["to_environment"]
    environment = environments.get(target_env_id)
    if not environment or environment.get("status") == "invalid":
        raise ValueError("transition environment is unavailable")
    if output.get("active_trust_environment") != transition.get("from_environment"):
        raise ValueError("active trust environment changed during transition")
    targets = {target["id"]: target for target in transition["targets"]}
    results = transition.get("results", {})
    if set(targets) != set(results) or any(result.get("status") != "verified" for result in results.values()):
        raise ValueError("all transition targets must be verified")
    comparisons, reviewed = {}, {}
    for kid, target in targets.items():
        record = output["knowledge"].get(kid)
        formal = output.get("formal_results", {}).get(target["formal_result_id"], {})
        exposition = output["expositions"].get((record or {}).get("exposition_id"), {})
        result = results[kid]
        if (not record or record.get("exposition_id") != target["exposition_id"]
                or _hash(record) != target["basis"]["sha256"] or kr.record_digest(formal) != target["formal_basis"]
                or kr.record_digest(exposition) != target["exposition_basis"]):
            raise ValueError("transition basis changed: " + kid)
        # This checks source, toolchain, declarations and axioms. formal is unchanged
        # since begin_transition (record_digest above covers lean_code), so its
        # source hash is target["source_sha256"].
        kr.validate_formal_evidence(formal, result, environment)
        comparison = compare_formal_results(target, result)
        comparisons[kid] = comparison
        if comparison["requires_identity_review"]:
            if runtime is None:
                raise ValueError("transition requires its sealed staged identity review runtime: " + kid)
            reviewed[kid] = _validated_staged_identity_review(
                instance, transition, kid, result.get("identity_review", {}), runtime)
    old_env_id = output.get("active_trust_environment")
    if old_env_id and environments[old_env_id].get("status") != "invalid":
        environments[old_env_id]["status"] = "superseded"
    environment["status"] = "active"
    output["active_trust_environment"] = target_env_id
    for kid, target in targets.items():
        record = output["knowledge"][kid]
        old_formal = output["formal_results"][target["formal_result_id"]]
        old_xid = record["exposition_id"]
        fid, xid = new_id("FR"), new_id("XP")
        result = {key: deepcopy(value) for key, value in results[kid].items() if key not in {"id", "identity_review"}}
        output["formal_results"][fid] = {**deepcopy(old_formal), "id": fid, "verification": result,
            "trust_environment_id": target_env_id, "formal_use": "active", "transition_id": transition["id"],
            "supersedes": old_formal["id"]}
        output["expositions"][xid] = {**deepcopy(output["expositions"][old_xid]), "id": xid,
            "formal_result_id": fid, "supersedes": old_xid}
        record.update(formal_result_id=fid, exposition_id=xid)
        if kid in reviewed:
            receipt = reviewed[kid]
            previous_cycle = record.get("review_cycle_id")
            if previous_cycle:
                record["previous_review_cycle_id"] = previous_cycle
            record["review_cycle_id"] = receipt["review_cycle_id"]
            assessment = {key: deepcopy(receipt[key]) for key in (
                "decision", "scope_complete", "execution_ids", "review_cycle_id",
                "summary", "proposal_digest", "transition_id", "transition_basis")}
            assessment.update(
                basis=kr.identity_basis(output, kid),
                reviewed_identity_basis=deepcopy(receipt["identity_basis"]),
            )
            # output is this activation's own copy; seal in place, not per target.
            kr.seal_identity_assessment(output, kid, assessment, receipt["policy_ref"], runtime={})
            continue
        # Preserve the old sealed judgment. A new continuity judgment names both
        # exact new inputs and the transition comparison instead of mutating it.
        for assessment in list(output.get("identity_assessments", {}).values()):
            if assessment.get("exposition_id") != old_xid or assessment.get("decision") != "match":
                continue
            uses = [use for use in output.get("assessment_uses", {}).values() if use["assessment_id"] == assessment["id"]]
            recoverable = bool(uses and uses[0].get("environment_revalidation", {}).get("environment_id")
                               in target["previous_environment_ids"])
            if not uses or (uses[0]["status"] != "active" and not recoverable):
                continue
            inherited = {key: deepcopy(value) for key, value in assessment.items() if key not in {"id", "formal_result_id", "exposition_id"}}
            inherited.update(basis=kr.identity_basis(output, kid), previous_assessment_id=assessment["id"], transition_id=transition["id"],
                             continuity_comparison=comparisons[kid])
            kr.seal_identity_assessment(output, kid, inherited, assessment["policy_ref"], runtime={})
    return output


def invalidate_environment(instance, runtime, env_id, reason, *, affected_constants=None,
                           scope_evidence=None) -> tuple[dict, dict]:
    _require_text(reason, "reason")
    output, new_runtime = deepcopy(instance), deepcopy(runtime)
    environment = output.get("trust_environments", {}).get(env_id)
    if environment is None:
        raise ValueError("unknown trust environment: " + env_id)
    scoped = bool(affected_constants and scope_evidence)
    candidates = [formal for formal in output.get("formal_results", {}).values()
                  if formal.get("trust_environment_id") == env_id]
    if any(not formal.get("verification", {}).get("dependency_closure") for formal in candidates):
        scoped = False
    if not scoped:
        environment.update(status="invalid", invalidated_reason=reason)
        if output.get("active_trust_environment") == env_id:
            output["active_trust_environment"] = None
    roots = set()
    for formal in candidates:
        closure = {name for names in formal.get("verification", {}).get("dependency_closure", {}).values() for name in names}
        closure.update(formal.get("declaration_names", []))
        if not scoped or closure & set(affected_constants):
            formal["formal_use"] = "suspended"
            formal.setdefault("use_history", []).append({"reason": reason, "environment_id": env_id,
                "affected_constants": sorted(affected_constants or []), "scope_evidence": scope_evidence})
            roots.add(formal["id"])
    previously_active = {uid for uid, use in output.get("assessment_uses", {}).items() if use.get("status") == "active"}
    if roots:
        _propagate(output, new_runtime, roots, reason)
        for uid in previously_active:
            use = output["assessment_uses"][uid]
            if use["status"] == "suspended":
                use["environment_revalidation"] = {"environment_id": env_id, "reason": reason}
    return output, new_runtime
