"""Separate knowledge authorities and derived, never-persisted K/proposal views."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from .repository import canonical_json, exact_content_hash, new_id

FAMILIES = ("knowledge", "formal_results", "expositions", "identity_assessments", "assessment_uses")
EXPOSITION_FIELDS = ("definitions", "assumptions", "statement", "explanation", "summary")


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def exact_digest(value):
    """Bind mathematical text and declaration keys without Unicode normalization."""
    return exact_content_hash(value)


def record_digest(record):
    """Canonical metadata plus exact hashes of the family's mathematical payload."""
    fields = {'formal_results': ('lean_code', 'declaration_names', 'verification'),
              'expositions': ('items', 'relation_claim')}.get(record.get('family'), ())
    return digest({'metadata': {k: v for k, v in record.items() if k not in fields},
                   'exact_payload': {k: exact_digest(record[k]) for k in fields if k in record}})


def initialize_families(instance):
    output = deepcopy(instance)
    for family in FAMILIES:
        output.setdefault(family, {})
    return output


def all_records(instance):
    result = {}
    for family in (*FAMILIES, "kind_definitions", "trust_environments"):
        for record in instance.get(family, {}).values():
            rid = record.get("id")
            if rid:
                if rid in result:
                    raise ValueError("duplicate record ID: " + rid)
                result[rid] = record
    for family in ("relations", "goal_judgments"):
        for record in instance.get(family, []):
            rid = record.get("id")
            if rid:
                if rid in result:
                    raise ValueError("duplicate record ID: " + rid)
                result[rid] = record
    return result


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


def create_candidate(instance, candidate, *, source_ref, actor_ref):
    output = initialize_families(instance)
    kid = candidate.get("id") or new_id("KN")
    if kid in all_records(output):
        raise ValueError("record ID already exists; use an explicit revision: " + kid)
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
    env_id = formal.get("trust_environment_id")
    env = instance.get("trust_environments", {}).get(env_id, {})
    verification = formal.get("verification", {})
    return (formal.get("publication_state") == "accepted" and formal.get("formal_use") == "active"
            and verification.get("status") == "verified" and env_id is not None
            and env.get("status") == "active" and instance.get("active_trust_environment") == env_id
            and verification.get("source_sha256") == hashlib.sha256(formal["lean_code"].encode()).hexdigest()
            and verification.get("toolchain") == env.get("toolchain")
            and verification.get("trust_environment_digest") == digest(env))


def _assessment_basis(formal, exposition):
    # Mutable use state is deliberately outside the immutable judgment premise.
    return {"formal": exact_digest({key: formal.get(key) for key in
            ("id", "lean_code", "declaration_names", "verification", "trust_environment_id")}),
            "exposition": exact_digest({key: exposition.get(key) for key in ("id", "formal_result_id", "items", "relation_claim")})}


def usable_links(instance, knowledge_id, _visiting=None):
    record = instance.get("knowledge", {}).get(knowledge_id, {})
    if record.get("lifecycle") != "active" or record.get("kind_use_suspended"):
        return []
    definition = instance.get("kind_definitions", {}).get(record.get("kind_definition_id"))
    if not definition or definition.get("status") != "active":
        return []
    visiting = set(_visiting or ())
    if knowledge_id in visiting:
        return []
    visiting.add(knowledge_id)
    for dependency in record.get("dependencies", []):
        if not usable_links(instance, dependency, visiting):
            return []
    from .input_basis import sources_current
    if not sources_current(record.get("source_basis", []), instance):
        return []
    if record.get("relation_claim"):
        from .knowledge import validate_basis
        if not record.get("relation_endpoint_basis") or not validate_basis(record["relation_endpoint_basis"], instance, {})["valid"]:
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
                or assessment.get("basis") != _assessment_basis(formal, exposition)):
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
    if verification.get("source_sha256") != hashlib.sha256(formal["lean_code"].encode()).hexdigest():
        raise ValueError("verification source differs from formal result")
    if verification.get("declarations") != formal["declaration_names"]:
        raise ValueError("verification declarations differ from formal result")
    for field in ("dependency_closure", "dependency_evidence", "declaration_evidence", "axioms"):
        if set(verification.get(field, {})) != set(formal["declaration_names"]):
            raise ValueError("verification evidence incomplete: " + field)
    for declaration in formal["declaration_names"]:
        if set(verification["dependency_evidence"][declaration]) != set(verification["dependency_closure"][declaration]):
            raise ValueError("dependency body evidence differs from the closure")
    if verification.get("status") == "verified":
        axioms = {a for values in verification["axioms"].values() for a in values}
        if "sorryAx" in axioms or axioms - set(env.get("allowed_axioms", [])):
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
    sealed = {**deepcopy(verification), "trust_environment_digest": digest(env)}
    if formal.get("verification"):
        if formal["verification"] == sealed and formal.get("trust_environment_id") == trust_environment_id:
            return output
        raise ValueError("sealed formal result must be replaced with a new result ID")
    formal.update(verification=sealed, trust_environment_id=trust_environment_id,
                  publication_state="accepted" if verification.get("status") == "verified" else "rejected",
                  formal_use="active" if verification.get("status") == "verified" else "suspended")
    return output


def record_identity_assessment(instance, knowledge_id, assessment, policy_ref, *, runtime):
    if not isinstance(policy_ref, str) or not policy_ref.strip():
        raise ValueError("identity assessment requires a fixed policy reference")
    output = initialize_families(instance)
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
    expected_basis = _assessment_basis(formal, exposition)
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
    return _assessment_basis(instance["formal_results"][record["formal_result_id"]],
                             instance["expositions"][record["exposition_id"]])


def assessment_current(instance, assessment_id):
    """Premise validity is independent of the judgment's positive/negative value."""
    assessment = instance.get('identity_assessments', {}).get(assessment_id, {})
    formal = instance.get('formal_results', {}).get(assessment.get('formal_result_id'), {})
    exposition = instance.get('expositions', {}).get(assessment.get('exposition_id'), {})
    if (not formal_usable(instance, formal) or exposition.get('lifecycle') != 'active'
            or assessment.get('basis') != _assessment_basis(formal, exposition)):
        return False
    from .input_basis import sources_current
    from .knowledge import validate_basis
    for record in instance.get('knowledge', {}).values():
        if (record.get('lifecycle') != 'active' or record.get('exposition_id') != exposition.get('id')
                or record.get('formal_result_id') != formal.get('id') or record.get('kind_use_suspended')
                or instance.get('kind_definitions', {}).get(record.get('kind_definition_id'), {}).get('status') != 'active'
                or not sources_current(record.get('source_basis', []), instance)
                or any(not usable_links(instance, dep, {record['id']}) for dep in record.get('dependencies', []))):
            continue
        if record.get('relation_claim') and (not record.get('relation_endpoint_basis')
                or not validate_basis(record['relation_endpoint_basis'], instance, {})['valid']):
            continue
        return True
    return False


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
    records = all_records(instance)
    for kid, record in instance.get("knowledge", {}).items():
        if {"formal", "lean_code", "identity_assessment", "reviews", "status"} & set(record):
            raise ValueError("knowledge contains another family's authority: " + kid)
        if record.get("lifecycle") not in {"active", "superseded", "withdrawn"}:
            raise ValueError("invalid knowledge lifecycle")
        if record.get("exposition_id") not in instance.get("expositions", {}):
            raise ValueError("missing exposition")
        fid = record.get("formal_result_id")
        if fid is not None and fid not in instance.get("formal_results", {}):
            raise ValueError("missing formal result")
        if any(ref not in records for ref in record.get("dependencies", [])):
            raise ValueError("missing knowledge dependency")
    for exposition in instance.get("expositions", {}).values():
        fid = exposition.get("formal_result_id")
        if fid is not None and fid not in instance.get("formal_results", {}):
            raise ValueError("exposition references missing formal result")
        items = exposition.get("items", [])
        if len({item["id"] for item in items}) != len(items):
            raise ValueError("duplicate exposition item ID")
    for assessment in instance.get("identity_assessments", {}).values():
        if assessment.get("formal_result_id") not in instance.get("formal_results", {}) or assessment.get("exposition_id") not in instance.get("expositions", {}):
            raise ValueError("assessment has missing inputs")
    seen = set()
    for use in instance.get("assessment_uses", {}).values():
        aid = use.get("assessment_id")
        if aid not in instance.get("identity_assessments", {}) or aid in seen:
            raise ValueError("invalid or duplicate assessment use")
        seen.add(aid)
        if use.get("status") not in {"active", "suspended", "withdrawn"}:
            raise ValueError("invalid assessment use status")
    return True


def _validate_family_record(record):
    family = record.get("family")
    required = {
        "formal_results": {"id", "lean_code", "declaration_names", "publication_state", "formal_use", "verification"},
        "expositions": {"id", "formal_result_id", "items", "lifecycle"},
        "identity_assessments": {"id", "formal_result_id", "exposition_id", "decision", "basis", "policy_ref"},
        "assessment_uses": {"id", "assessment_id", "status", "history"},
    }
    if family not in required or required[family] - set(record):
        raise ValueError("incomplete knowledge-family record")
    if family == "formal_results":
        if record["publication_state"] not in {"candidate", "accepted", "rejected"} or record["formal_use"] not in {"active", "suspended", "withdrawn"}:
            raise ValueError("invalid formal state")
    if family == "expositions" and record["lifecycle"] not in {"active", "superseded", "withdrawn"}:
        raise ValueError("invalid exposition lifecycle")
    if family == "identity_assessments" and record["decision"] not in {"match", "mismatch", "unresolved"}:
        raise ValueError("invalid identity decision")
    if family == "assessment_uses" and record["status"] not in {"active", "suspended", "withdrawn"}:
        raise ValueError("invalid assessment effect")
