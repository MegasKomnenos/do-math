"""Separate knowledge authorities and derived, never-persisted K/proposal views."""
from __future__ import annotations

from copy import deepcopy
from .formal import FORMAL_EVIDENCE_FIELDS, forbidden_axioms, lean_source_sha256
from .planning import record_index
from .repository import exact_content_hash, new_id

FAMILIES = ("knowledge", "formal_results", "expositions", "identity_assessments", "assessment_uses")
# planning.RECORD_FAMILIES keys of the research-space records that all_records indexes.
RESEARCH_RECORD_FAMILIES = ("knowledge", "formal-result", "exposition", "identity-assessment", "assessment-use",
                            "kind-definition", "trust-environment", "relation", "goal-judgment")
EXPOSITION_FIELDS = ("definitions", "assumptions", "statement", "explanation", "summary")
# Lifecycle of knowledge, exposition and relation records.
RECORD_LIFECYCLES = frozenset({"active", "superseded", "withdrawn"})
# States of the use of one identity assessment.
ASSESSMENT_USE_STATUSES = frozenset({"active", "suspended", "withdrawn"})


def record_digest(record):
    """Canonical metadata plus exact hashes of the family's mathematical payload."""
    fields = {'formal_results': ('lean_code', 'declaration_names', 'verification'),
              'expositions': ('items', 'relation_claim')}.get(record.get('family'), ())
    return exact_content_hash({'metadata': {k: v for k, v in record.items() if k not in fields},
                   'exact_payload': {k: exact_content_hash(record[k]) for k in fields if k in record}})


def initialize_families(instance):
    output = deepcopy(instance)
    for family in FAMILIES:
        output.setdefault(family, {})
    return output


def all_records(instance):
    return {rid: record for rid, (_, record) in
            record_index(instance, {}, families=RESEARCH_RECORD_FAMILIES).items()}


def exposition_items(candidate):
    """Stable local coordinates participate in the identity review basis."""
    items = []
    for field in EXPOSITION_FIELDS:
        value = candidate.get(field)
        if not value:
            continue
        values = value if isinstance(value, list) else [value]
        for index, text in enumerate(values):
            if not isinstance(text, str) or not text.strip():
                raise ValueError("exposition text must be nonempty")
            items.append({"id": field + ":" + str(index + 1), "kind": field,
                          "text": text, "declaration_refs": list(candidate.get("declaration_names", []))})
    return items


def create_candidate(output, candidate, *, source_ref, actor_ref):
    """Write one checked candidate into the caller's own copy; import_candidate owns the checks."""
    for family in FAMILIES:
        output.setdefault(family, {})
    kid = candidate.get("id") or new_id("KN")
    fid = candidate.get("formal_result_ref") or (new_id("FR") if candidate.get("lean_code") else None)
    xid = new_id("XP")
    if fid and not candidate.get("formal_result_ref"):
        output["formal_results"][fid] = {
            "id": fid, "family": "formal_results", "lean_code": candidate["lean_code"],
            "declaration_names": list(candidate["declaration_names"]),
            "dependencies": list(candidate.get("dependencies", [])),
            "publication_state": "candidate", "formal_use": "suspended",
            "verification": {}, "producer_execution": actor_ref,
            "origin_refs": [source_ref],
        }
    output["expositions"][xid] = {
        "id": xid, "family": "expositions", "formal_result_id": fid,
        "items": exposition_items(candidate), "lifecycle": "active",
        "producer_execution": actor_ref, "origin_refs": [source_ref],
    }
    if candidate.get("relation_claim"):
        output["expositions"][xid]["relation_claim"] = deepcopy(candidate["relation_claim"])
    excluded = {"id", "lean_code", "declaration_names", "formal_result_ref", *EXPOSITION_FIELDS}
    record = {key: deepcopy(value) for key, value in candidate.items() if key not in excluded}
    record.update(id=kid, family="knowledge", lifecycle="active", formal_result_id=fid,
                  exposition_id=xid, producer_execution=actor_ref,
                  origin_refs=list(dict.fromkeys([*candidate.get("origin_refs", []), source_ref])))
    output["knowledge"][kid] = record
    return output, kid


def proposal_view(instance, knowledge_id):
    record = deepcopy(instance["knowledge"][knowledge_id])
    exposition = instance["expositions"][record["exposition_id"]]
    formal = instance.get("formal_results", {}).get(record.get("formal_result_id"), {})
    for field in EXPOSITION_FIELDS:
        values = [item["text"] for item in exposition["items"] if item["kind"] == field]
        record[field] = values if field in {"definitions", "assumptions"} else "\n".join(values)
    record.update(lean_code=formal.get("lean_code", ""), declaration_names=formal.get("declaration_names", []),
                  formal=deepcopy(formal.get("verification", {})))
    if formal.get("trust_environment_id"):
        record["formal"]["trust_environment_id"] = formal["trust_environment_id"]
    record["status"] = "verified" if usable_links(instance, knowledge_id) else "candidate"
    return record


def reader_view(instance, knowledge_id):
    """Delivered evidence only; never copy these projections into a new candidate."""
    record = proposal_view(instance, knowledge_id)
    formal = instance.get('formal_results', {}).get(record.get('formal_result_id'), {})
    # Exact split records are available to readers of this already-delivered file.
    record["formal_result"] = deepcopy(formal)
    record["identity_assessments"] = [deepcopy(row) for row in instance.get("identity_assessments", {}).values()
        if row.get("formal_result_id") == record.get("formal_result_id")
        and row.get("exposition_id") == record.get("exposition_id")]
    assessment_ids = {row["id"] for row in record["identity_assessments"]}
    record["assessment_uses"] = [deepcopy(row) for row in instance.get("assessment_uses", {}).values()
        if row.get("assessment_id") in assessment_ids]
    return record


def formal_usable(instance, formal):
    # The toolchain dict is the identity of the environment; comparing it
    # replaces hashing the whole environment record on every use check.
    env_id = formal.get("trust_environment_id")
    env = instance.get("trust_environments", {}).get(env_id, {})
    verification = formal.get("verification", {})
    return (formal.get("publication_state") == "accepted" and formal.get("formal_use") == "active"
            and verification.get("status") == "verified" and env_id is not None
            and env.get("status") == "active" and instance.get("active_trust_environment") == env_id
            and verification.get("source_sha256") == lean_source_sha256(formal["lean_code"])
            and verification.get("toolchain") == env.get("toolchain"))


def identity_premise(formal, exposition):
    # Mutable use state is deliberately outside the immutable judgment premise.
    return {"formal": exact_content_hash({key: formal.get(key) for key in
            ("id", "lean_code", "declaration_names", "verification", "trust_environment_id")}),
            "exposition": exact_content_hash({key: exposition.get(key) for key in ("id", "formal_result_id", "items", "relation_claim")})}


def premise_failures(instance, record):
    """Yield, in order, the failed record premises shared by K support and research reuse."""
    if record.get("lifecycle") != "active" or record.get("kind_use_suspended"):
        yield "record_not_active"
    definition = instance.get("kind_definitions", {}).get(record.get("kind_definition_id"))
    if not definition or definition.get("status") != "active":
        yield "kind_not_active"
    from .input_basis import sources_current
    if not sources_current(record.get("source_basis", []), instance):
        yield "sources_changed"


def record_premises_current(instance, record, visiting=()):
    """K premises of one knowledge record: shared premises, usable dependencies, current relation endpoints.

    visiting holds the records whose premises are being judged; a dependency
    among them is a cycle and is not usable."""
    if next(premise_failures(instance, record), None) is not None:
        return False
    inner = {*visiting, record["id"]}
    if any(not usable_links(instance, dependency, inner) for dependency in record.get("dependencies", [])):
        return False
    if record.get("relation_claim"):
        from .knowledge import validate_basis
        return bool(record.get("relation_endpoint_basis")) and validate_basis(record["relation_endpoint_basis"], instance, {})["valid"]
    return True


def usable_links(instance, knowledge_id, _visiting=None):
    record = instance.get("knowledge", {}).get(knowledge_id, {})
    if knowledge_id in (_visiting or ()) or not record_premises_current(instance, record, _visiting or ()):
        return []
    fid = record.get("formal_result_id")
    formal = instance.get("formal_results", {}).get(fid, {})
    if not formal_usable(instance, formal):
        return []
    links = []
    for assessment in instance.get("identity_assessments", {}).values():
        if (assessment.get("formal_result_id") != fid or assessment.get("decision") != "match"
                or assessment.get("exposition_id") != record.get("exposition_id")):
            continue
        exposition = instance.get("expositions", {}).get(assessment.get("exposition_id"), {})
        if (exposition.get("lifecycle") != "active" or exposition.get("formal_result_id") != fid
                or assessment.get("basis") != identity_premise(formal, exposition)):
            continue
        uses = [use for use in instance.get("assessment_uses", {}).values()
                if use.get("assessment_id") == assessment["id"] and use.get("status") == "active"]
        if uses:
            links.append({"formal_result_id": fid, "exposition_id": exposition["id"],
                          "assessment_id": assessment["id"], "assessment_use_id": uses[0]["id"]})
    return sorted(links, key=lambda link: link["assessment_id"])


def knowledge_view(instance):
    return [{"id": kid, "title": record.get("title"), "lifecycle": record.get("lifecycle"),
             "formal_result_id": record.get("formal_result_id"),
             "formal_valid": formal_usable(instance, instance.get("formal_results", {}).get(record.get("formal_result_id"), {})),
             "usable": bool(links), "links": links}
            for kid, record in sorted(instance.get("knowledge", {}).items())
            for links in [usable_links(instance, kid)]]


def validate_formal_evidence(formal, verification, env):
    if verification.get("toolchain") != env.get("toolchain"):
        raise ValueError("verification toolchain differs from approved environment")
    if verification.get("source_sha256") != lean_source_sha256(formal["lean_code"]):
        raise ValueError("verification source differs from formal result")
    if verification.get("declarations") != formal["declaration_names"]:
        raise ValueError("verification declarations differ from formal result")
    for field in FORMAL_EVIDENCE_FIELDS:
        if set(verification.get(field, {})) != set(formal["declaration_names"]):
            raise ValueError("verification evidence incomplete: " + field)
    for declaration in formal["declaration_names"]:
        if set(verification["dependency_evidence"][declaration]) != set(verification["dependency_closure"][declaration]):
            raise ValueError("dependency body evidence differs from the closure")
    if verification.get("status") == "verified" and forbidden_axioms(verification["axioms"], env.get("allowed_axioms", [])):
        raise ValueError("verification uses unapproved axioms")


def record_formal_result(instance, knowledge_id, verification, trust_environment_id, *, runtime):
    output = initialize_families(instance)
    formal = output["formal_results"][output["knowledge"][knowledge_id]["formal_result_id"]]
    env = output.get("trust_environments", {}).get(trust_environment_id)
    if not env or env.get("status") != "active" or output.get("active_trust_environment") != trust_environment_id:
        raise ValueError("formal verification requires a preapproved active environment")
    if any(t.get("status") in {"checking", "ready"} for t in runtime.get("trust_transitions", {}).values()):
        raise ValueError("formal publication waits for the trust transition")
    validate_formal_evidence(formal, verification, env)
    sealed = deepcopy(verification)
    if formal.get("verification"):
        if formal["verification"] == sealed and formal.get("trust_environment_id") == trust_environment_id:
            return output
        raise ValueError("sealed formal result must be replaced with a new result ID")
    formal.update(verification=sealed, trust_environment_id=trust_environment_id,
                  publication_state="accepted" if verification.get("status") == "verified" else "rejected",
                  formal_use="active" if verification.get("status") == "verified" else "suspended")
    return output


def record_identity_assessment(instance, knowledge_id, assessment, policy_ref, *, runtime):
    return seal_identity_assessment(deepcopy(instance), knowledge_id, assessment, policy_ref, runtime=runtime)


def seal_identity_assessment(output, knowledge_id, assessment, policy_ref, *, runtime):
    """Seal into caller-owned state in place; the caller discards it if this raises."""
    if not isinstance(policy_ref, str) or not policy_ref.strip():
        raise ValueError("identity assessment requires a fixed policy reference")
    for family in FAMILIES:
        output.setdefault(family, {})
    record = output["knowledge"][knowledge_id]
    fid, xid = record["formal_result_id"], record["exposition_id"]
    formal, exposition = output["formal_results"][fid], output["expositions"][xid]
    decision = assessment.get("decision")
    if decision == "match" and any(t.get("status") in {"checking", "ready"} for t in runtime.get("trust_transitions", {}).values()):
        raise ValueError("identity publication waits for the trust transition")
    if decision not in {"match", "mismatch", "unresolved"}:
        raise ValueError("invalid identity decision")
    if decision == "match" and not formal_usable(output, formal):
        raise ValueError("match cannot activate without current formal evidence")
    expected_basis = identity_premise(formal, exposition)
    if assessment.get("basis") != expected_basis:
        raise ValueError("identity assessment must name the exact current formal and exposition basis")
    aid = assessment.get("id") or new_id("IA")
    sealed = {key: deepcopy(value) for key, value in assessment.items() if key not in {"effective", "status"}}
    sealed.update(id=aid, family="identity_assessments", formal_result_id=fid,
                  exposition_id=xid, policy_ref=policy_ref, basis=expected_basis)
    if exposition.get("relation_claim"):
        sealed["relation_claim"] = deepcopy(exposition["relation_claim"])
    if aid in all_records(output):
        if output["identity_assessments"].get(aid) == sealed:
            return output, aid
        raise ValueError("immutable assessment ID already exists")
    output["identity_assessments"][aid] = sealed
    uid = new_id("AU")
    output["assessment_uses"][uid] = {"id": uid, "family": "assessment_uses", "assessment_id": aid,
        "status": "active", "history": []}
    return output, aid


def identity_basis(instance, knowledge_id):
    record = instance["knowledge"][knowledge_id]
    return identity_premise(instance["formal_results"][record["formal_result_id"]],
                            instance["expositions"][record["exposition_id"]])


def formal_overlay(instance, formal_id, **changes):
    """Read-only view with one formal result replaced; never mutate or persist it."""
    formal_results = dict(instance["formal_results"])
    formal_results[formal_id] = {**formal_results[formal_id], **changes}
    return {**instance, "formal_results": formal_results}


def assessment_current(instance, assessment_id):
    """Premise validity is independent of the judgment's positive/negative value."""
    assessment = instance.get('identity_assessments', {}).get(assessment_id, {})
    formal = instance.get('formal_results', {}).get(assessment.get('formal_result_id'), {})
    exposition = instance.get('expositions', {}).get(assessment.get('exposition_id'), {})
    if (not formal_usable(instance, formal) or exposition.get('lifecycle') != 'active'
            or assessment.get('basis') != identity_premise(formal, exposition)):
        return False
    return any(record.get('exposition_id') == exposition.get('id') and record.get('formal_result_id') == formal.get('id')
               and record_premises_current(instance, record) for record in instance.get('knowledge', {}).values())


def set_assessment_use(instance, assessment_id, status, reason, actor_ref):
    """State primitive; production restoration is authorized by the reassessment consumer."""
    if status not in {"active", "suspended", "withdrawn"} or not reason or not actor_ref:
        raise ValueError("assessment use requires status, reason and actor")
    output = deepcopy(instance)
    assessment = output["identity_assessments"][assessment_id]
    if status == "active":
        if not assessment_current(output, assessment_id):
            raise ValueError("cannot restore an obsolete assessment")
    uses = [use for use in output["assessment_uses"].values() if use["assessment_id"] == assessment_id]
    if len(uses) != 1:
        raise ValueError("assessment must have exactly one use record")
    use = uses[0]
    # A later semantic disposition cannot be discharged by environment repair.
    use.pop("environment_revalidation", None)
    if use["status"] == "withdrawn" and status != "withdrawn":
        raise ValueError("withdrawn assessment use cannot be restored")
    if use["status"] != status:
        use["history"].append({"from": use["status"], "to": status, "reason": reason, "actor_ref": actor_ref})
        use["status"] = status
    return output


def validate_knowledge_records(instance):
    """The knowledge-family rules no record schema or reference table states.

    Field shapes, states and record references are the storage contract's
    (record_schemas); what remains is uniqueness across records.
    """
    for exposition in instance.get("expositions", {}).values():
        items = exposition.get("items", [])
        if len({item["id"] for item in items}) != len(items):
            raise ValueError("duplicate exposition item ID")
    seen = set()
    for use in instance.get("assessment_uses", {}).values():
        if use["assessment_id"] in seen:
            raise ValueError("duplicate assessment use")
        seen.add(use["assessment_id"])
    return True
