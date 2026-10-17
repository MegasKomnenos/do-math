"""Atomic response bundles. No mathematical independence is certified.

Domain mutation, live authority/currentness and durable Git CAS remain explicit
callbacks. Mutation callbacks operate only on the supplied candidate dictionaries;
they must not perform external effects. A failed publish never returns acceptance.
"""
from __future__ import annotations

from copy import deepcopy

import jsonschema

from .contracts import MANIFEST_SCHEMA, REFS, TEXT, closed_object
from .execution_profiles import task_research
from .values import json_copy
from .input_basis import CurrentnessChanged
from .canonical import exact_content_hash


REFERENCE_KEYS = {"dependencies", "inputs", "reuse", "source", "target", "evidence_refs",
                  "formal_result_refs", "assessment_refs", "record_ids", "record_id",
                  "source_refs", "origin_refs", "target_ids", "authority_refs",
                  "knowledge_revision_targets", "evidence_ids", "task_id", "task_title"}


def issue(rule_id, path, message, integration_id=None):
    identity = [rule_id, integration_id, path]
    return {"issue_id": "SI-" + exact_content_hash(identity)[:24], "rule_id": rule_id,
            "integration_id": integration_id, "path": path, "message": message}


def failure_kind(issues):
    """Classify at the recorded validation boundary, never from error prose."""
    rules = {row.get('rule_id', '') for row in issues}
    if 'integration.publication' in rules:
        return 'publication_failure'
    # Changed premises alone refresh the decision; any other error stays the producer's.
    if rules == {'integration.currentness'}:
        return 'currentness_changed'
    if any(rule.startswith('schema.') for rule in rules):
        return 'output_schema'
    if 'submission.parse' in rules:
        return 'output_parse'
    if 'submission.read' in rules:
        return 'input_failure'
    return 'output_contract'


SUBMISSION_OUTCOMES = {
    'accepted': {'output_repair': False, 'next_owner': None},
    'publication_wait': {'output_repair': False, 'next_owner': 'engine'},
    'impact_review': {'output_repair': False, 'next_owner': 'impact_review'},
    'premises_changed': {'output_repair': False, 'next_owner': 'refresh_decision'},
    'output_rejected': {'output_repair': True, 'next_owner': 'producer'},
}


def submission_outcome(received):
    """Classify the actual bundle receipt before counting a producer repair."""
    if not isinstance(received['status'], str) or received['status'] not in {'accepted', 'partial', 'returned'}:
        raise ValueError('unknown integration receipt status: ' + repr(received['status']))
    if received['status'] == 'accepted':
        return 'accepted'
    owners = {row.get('next_owner') for row in received['bundles']}
    if 'engine' in owners:
        return 'publication_wait'
    if 'impact_review' in owners:
        return 'impact_review'
    if failure_kind(received['issues']) == 'currentness_changed':
        return 'premises_changed'
    return 'output_rejected'


class ImpactReviewRequired(ValueError):
    """A current mutation needs a designated judgment, not a rewritten declaration."""
    def __init__(self, request):
        super().__init__("designated independent impact review required")
        self.request = deepcopy(request)


def bundle_impact_request(instance, runtime, bundle, *, producer_execution_id, input_snapshot):
    """Bind the unchanged held payload to each actual domain plan separately."""
    from . import knowledge, planning
    if producer_execution_id not in runtime.get("executions", {}) or not input_snapshot:
        raise ValueError("impact request needs its original execution and fixed input snapshot")
    if runtime["executions"][producer_execution_id].get("input_snapshot") != input_snapshot:
        raise ValueError("impact request snapshot differs from its original producer input")
    records = {rid: row for rid, (_, row) in planning.record_index(instance, runtime).items()}
    roots, targets, specifications = set(), set(), []
    changes = bundle["extensions"].get("knowledge_changes", [])
    coordinates = [p for p in bundle["members"] if p.startswith("activity-extensions.json/knowledge_changes/")]
    if len(changes) != len(coordinates) or len({row["id"] for row in changes}) != len(changes):
        raise ValueError("impact changes need distinct targets and exact member coordinates")
    for coordinate, change in zip(coordinates, changes):
        target_roots = knowledge.revision_roots(instance, change["id"])
        roots.update(target_roots)
        targets.add(change["id"])
        specifications.append((coordinate, target_roots, change["impact_set"]))
    for coordinate, family, target, row in mutation_members(bundle["output"], bundle["extensions"]):
        if family != "knowledge_changes" and target in records:
            roots.add(target)
            targets.add(target)
    prior = bundle.get("previous_hashes", {})
    if targets - prior.keys():
        raise ValueError("bundle previous hashes missing for mutation targets")
    for identifier, expected in prior.items():
        if identifier not in records or knowledge.content_hash(records[identifier]) != expected:
            raise ValueError("bundle previous semantic hash changed: " + identifier)
    if not roots and bundle["impact_set"]:
        raise ValueError("bundle declares impact without an existing mutation root")

    header = {"integration_id": bundle["integration_id"], "payload_sha256": bundle["payload_sha256"],
              "producer_execution_id": producer_execution_id, "input_snapshot": input_snapshot}
    possible_reviews = set()
    for execution_id, execution in runtime.get("executions", {}).items():
        action = execution.get("action", {})
        assigned = action.get("input_basis", {}).get("impact_review", {})
        if (execution.get("role") == "maintenance" and action.get("stage") == "impact_review"
                and all(assigned.get(key) == value for key, value in header.items())):
            possible_reviews.add(execution_id)

    def request(excluded):
        plans = {scope: knowledge.plan_impact(instance, runtime, target_roots, declared,
                    excluded_dependents=excluded)
                 for scope, target_roots, declared in specifications}
        if roots:
            plans = {"bundle": knowledge.plan_impact(instance, runtime, roots, bundle["impact_set"],
                         excluded_dependents=excluded), **plans}
        return {**header, "plans": plans}

    # A fixed point with any excluded review must equal that review's actual
    # assignment. Check those finite candidates directly. Starting with every
    # same-header review excluded can miss the current assignment when an older
    # review belongs in its impact closure; that would make the new review
    # invalidate its own input as soon as its evidence is recorded.
    assignments = [runtime["executions"][identifier]["action"]["input_basis"]["impact_review"]
                   for identifier in sorted(possible_reviews)]
    checked = []
    for assigned in assignments:
        if assigned in checked:
            continue
        checked.append(assigned)
        excluded = {identifier for identifier in possible_reviews
                    if runtime["executions"][identifier]["action"]["input_basis"]["impact_review"] == assigned}
        current = request(excluded)
        if current == assigned:
            return current
    # No preserved assignment matches: all reviews are historical dependents
    # of the newly computed request, which needs a fresh independent judgment.
    return request(set())


def impact_review_response_schema(request):
    """A producer can reject or leave unresolved every explicitly assigned scope."""
    alternatives = []
    for scope, plan in request["plans"].items():
        alternatives.append(closed_object({"scope": {"const": scope}, "plan_digest": {"const": plan["digest"]},
            "decision": {"enum": ["approve", "reject", "unresolved"]}, "affected_ids": REFS, "reason": TEXT}))
    if not alternatives:
        raise ValueError("impact review must name an actual plan")
    schema = closed_object({**{key: {"const": request[key]} for key in
        ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot")},
        "plan_decisions": {"type": "array", "minItems": len(alternatives), "maxItems": len(alternatives),
                           "items": {"oneOf": alternatives}}})
    schema["description"] = (
        "Independently assess the held mutation using the original candidate and the supplied premise records. "
        "For every assigned scope, explain discrepancies between declared and computed dependencies and judge "
        "whether suspending/reassessing the computed-and-declared union is justified and sufficient. "
        "Use unresolved when essential evidence or scope is uncertain, and reject an unjustified disposition. "
        "Do not approve solely because hashes match. This judgment grants no new mathematical result, "
        "user authority or external-effect permission; it only resolves this held bundle's impact gate.")
    return json_copy(schema)


def validate_impact_review_response(request, output):
    response = output.get("impact_review")
    errors = list(jsonschema.Draft202012Validator(impact_review_response_schema(request)).iter_errors(response))
    if errors:
        raise ValueError("impact review response differs from its assignment: " + errors[0].message)
    rows = response["plan_decisions"]
    if {row["scope"] for row in rows} != set(request["plans"]) or len({row["scope"] for row in rows}) != len(rows):
        raise ValueError("impact review must judge every scope exactly once")
    for row in rows:
        plan = request["plans"][row["scope"]]
        if row["decision"] == "approve" and set(row["affected_ids"]) != set(plan["computed_impact"]) | set(plan["declared_impact"]):
            raise ValueError("approved impact scope must cover the computed and declared union")
    return {row["scope"]: deepcopy(row) for row in rows}


def require_bundle_impact_review(instance, runtime, bundle, *, producer_execution_id, input_snapshot,
                                 review_execution_id=None, snapshot=None, read_artifact=None, receiving_execution_id=None,
                                 git_dir=None):
    return _reviewed_impact_request(instance, runtime, bundle, producer_execution_id=producer_execution_id,
        input_snapshot=input_snapshot, review_execution_id=review_execution_id, snapshot=snapshot,
        read_artifact=read_artifact, receiving_execution_id=receiving_execution_id, git_dir=git_dir)[1]


def _reviewed_impact_request(instance, runtime, bundle, *, producer_execution_id, input_snapshot,
                             review_execution_id, snapshot, read_artifact, receiving_execution_id, git_dir=None):
    """Return the current impact request with the confirmations its reviewed plans require."""
    receiver = receiving_execution_id or producer_execution_id
    seen = set()
    while receiver != producer_execution_id:
        if not receiver or receiver in seen or receiver not in runtime.get("executions", {}):
            raise ValueError("impact approval cannot transfer to an unrelated receiving execution")
        seen.add(receiver)
        row = runtime["executions"][receiver]
        action = row.get("action", {})
        receiver = row.get("continuation_of") or action.get("continuation_of") or action.get("repair", {}).get("execution_id")
    request = bundle_impact_request(instance, runtime, bundle,
        producer_execution_id=producer_execution_id, input_snapshot=input_snapshot)
    if not any(plan["requires_independent_review"] for plan in request["plans"].values()):
        return request, {}
    if review_execution_id is None:
        raise ImpactReviewRequired(request)
    from .governance import validate_independent_execution
    from .submission import issued_input, read_sealed_submission
    validate_independent_execution(runtime, review_execution_id, [producer_execution_id])
    review = runtime["executions"][review_execution_id]
    action = review.get("action", {})
    if (review.get("role") != "maintenance" or review.get("actor_kind") != "ai" or review.get("status") != "ended" or
            review.get("outcome") != "output_accepted" or action.get("stage") != "impact_review" or
            action.get("input_basis", {}).get("impact_review") != request):
        raise ValueError("impact review is not the accepted designated current assignment")
    if not snapshot or read_artifact is None or not review.get("input_bundle"):
        raise ValueError("impact review requires sealed input and output artifacts")
    fixed, _ = issued_input(review, snapshot, read_artifact, with_schema=False)
    if fixed.get("execution_id") != review_execution_id or fixed.get("action") != action:
        raise ValueError("impact review input is not the sealed designated assignment")
    output = read_sealed_submission(review, snapshot, read_artifact, git_dir=git_dir)["output"]
    rows = validate_impact_review_response(request, output)
    # The sealed central check admitted one maintenance response without extensions.
    bundle = next(split_bundles(output, {}, fixed))
    receipt = runtime.get("integrations", {}).get(bundle["integration_id"], {})
    if (receipt.get("execution_id") != review_execution_id or receipt.get("payload_sha256") != bundle["payload_sha256"] or
            receipt.get("response_sha256") != exact_content_hash(member_values(output, {}, {"action": action})["output"])):
        raise ValueError("impact review has no matching published response receipt")
    if any(row["decision"] != "approve" for row in rows.values()):
        raise ValueError("independent impact review did not approve every assigned scope")
    return request, {scope: {"plan_digest": row["plan_digest"], "decision": "approve", "affected_ids": row["affected_ids"],
            "review_ref": review_execution_id, "reviewer_ref": review_execution_id,
            "producer_ref": producer_execution_id} for scope, row in rows.items()}


def apply_reviewed_knowledge_changes(instance, runtime, bundle, *, actor_ref, producer_execution_id,
                                     input_snapshot, review_execution_id=None, snapshot=None, read_artifact=None,
                                     receiving_execution_id=None, git_dir=None, clock):
    """Apply the reviewed S0 plans once, then create every replacement candidate."""
    from . import knowledge, knowledge_records
    request, confirmations = _reviewed_impact_request(instance, runtime, bundle,
        producer_execution_id=producer_execution_id, input_snapshot=input_snapshot,
        review_execution_id=review_execution_id, snapshot=snapshot, read_artifact=read_artifact,
        receiving_execution_id=receiving_execution_id, git_dir=git_dir)
    plans = request["plans"]
    # bundle_impact_request, rerun by _reviewed_impact_request, matched these
    # coordinates to the changes; import_candidate rejects existing or repeated IDs.
    changes = bundle["extensions"].get("knowledge_changes", [])
    reasons = list(dict.fromkeys(change["reason"] for change in changes))
    output, running = knowledge.apply_reviewed_impacts(instance, runtime, plans, confirmations,
        reason="; ".join(reasons), clock=clock)
    replacement_ids = [change.get("replacement_id") or clock.new_id("KN") for change in changes]
    reserved = set(replacement_ids)
    for change, replacement_id in zip(changes, replacement_ids):
        output, running = knowledge.replace_knowledge(output, running, change["id"], change["changes"],
            reason=change["reason"], actor_ref=actor_ref, replacement_id=replacement_id,
            reserved_dependency_ids=reserved, clock=clock)
    knowledge_records.validate_knowledge_records(output)
    return output, running


def split_research(context):
    """Ordinary task research, whose knowledge and relation records form independent bundles."""
    action = context.get("action", {})
    return task_research(action) and not action.get("revision_targets")


def member_values(output, extensions, context):
    """Coordinates are producer-visible and remain fixed within the sealed output."""
    base = {key: deepcopy(value) for key, value in output.items()
            if key not in {"integration_bundles", "repair_responses"}}
    members = {}
    if split_research(context):
        for family in ("knowledge", "relations"):
            for index, value in enumerate(base.pop(family, [])):
                members[f"output/{family}/{index}"] = value
    members["output"] = base
    for family, rows in extensions.items():
        if not isinstance(rows, list):
            raise ValueError("extension families must be arrays: " + family)
        for index, value in enumerate(rows):
            members[f"activity-extensions.json/{family}/{index}"] = deepcopy(value)
    return members


def reference_ids(value):
    """IDs named by the REFERENCE_KEYS fields anywhere inside ``value``."""
    refs = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REFERENCE_KEYS:
                if isinstance(child, str):
                    refs.add(child)
                elif isinstance(child, list):
                    refs.update(item for item in child if isinstance(item, str))
            if isinstance(child, (dict, list)):
                refs.update(reference_ids(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(reference_ids(child))
    return refs


def mutation_members(output, extensions):
    """Identify existing-object revisions, excluding reads and ordinary progress."""
    rows = []
    for family in ("knowledge_changes", "task_dispositions", "revision_resolutions"):
        for index, row in enumerate(extensions.get(family, [])):
            if isinstance(row, dict):
                target = row.get("id") or row.get("task_id") or row.get("record_id")
                rows.append((f"activity-extensions.json/{family}/{index}", family, target, row))
    for row in output.get("candidates", []):
        if isinstance(row, dict) and row.get("revises_task_id"):
            rows.append(("output", "candidates", row["revises_task_id"], row))
    return rows


def protocol_output(output, extensions, context):
    """Derive mechanical grouping in memory; the authored bytes remain the source."""
    if "integration_bundles" in output:
        return output
    action = context.get("action", {})
    if (mutation_members(output, extensions) or action.get("revision_targets") or
            context.get("accepted_response") or context.get("accepted_integration_ids")):
        raise ValueError("revisions and partially accepted retries require explicit integration_bundles")
    if not context.get("execution_id") or not context.get("snapshot"):
        raise ValueError("default integration bundle needs the fixed execution and input snapshot")
    members = member_values(output, extensions, context)
    grants = sorted({ref for ref in (action.get("grant_id"), context.get("control_binding", {}).get("grant_id")) if ref})
    declaration = {"members": sorted(members), "impact_set": [], "authority_refs": grants}
    identifier = "IN-" + exact_content_hash({"execution_id": context["execution_id"], "snapshot": context["snapshot"],
        "action": action, "declaration": declaration, "values": members})
    return {**output, "integration_bundles": [{"integration_id": identifier, **declaration}]}


def derived_bundles(output, extensions, context):
    """The protocol output and its member values, derived once per response; raise on a malformed one."""
    output = protocol_output(output, extensions, context)
    return output, member_values(output, extensions, context)


def inspect_bundles(output, extensions, context, *, derived=None):
    """Check declared structure only; live state is checked again before each CAS.

    derived may carry derived_bundles() of these same arguments."""
    if not isinstance(output, dict) or not isinstance(extensions, dict):
        return [issue("integration.manifest", "output" if not isinstance(output, dict) else "activity-extensions.json",
                      "response and extensions must be objects")]
    issues = []
    try:
        output = derived[0] if derived else protocol_output(output, extensions, context)
    except (TypeError, ValueError) as error:
        return [issue("integration.manifest", "output/integration_bundles", str(error))]
    manifest = output.get("integration_bundles")
    errors = list(jsonschema.Draft202012Validator(MANIFEST_SCHEMA).iter_errors(manifest))
    if errors:
        return [issue("integration.manifest", "output/integration_bundles/" +
                      "/".join(map(str, error.absolute_path)), error.message) for error in errors]
    ids = [row["integration_id"] for row in manifest]
    if len(set(ids)) != len(ids):
        issues.append(issue("integration.members", "output/integration_bundles", "integration IDs must be unique"))
    if not split_research(context) and len(manifest) != 1:
        issues.append(issue("integration.single_bundle", "output/integration_bundles",
                            "this role response and all extensions are one judgment"))
    try:
        members = derived[1] if derived else member_values(output, extensions, context)
    except (TypeError, ValueError) as error:
        return issues + [issue("integration.members", "activity-extensions.json", str(error))]
    owners = {}
    for bundle in manifest:
        for coordinate in bundle["members"]:
            if coordinate not in members or coordinate in owners:
                issues.append(issue("integration.members", coordinate, "unknown or multiply assigned member"))
            owners[coordinate] = bundle["integration_id"]
    accepted_response = context.get("accepted_response")
    already_owned = set()
    if accepted_response and split_research(context):
        if ("output" in owners or exact_content_hash(members["output"]) != accepted_response.get("response_sha256")):
            issues.append(issue("integration.response_replay", "output",
                                "accepted response must be unchanged and must not be reassigned"))
        else:
            already_owned.add("output")
    for coordinate in sorted(members.keys() - owners.keys() - already_owned):
        issues.append(issue("integration.members", coordinate, "mutation has no declared integration bundle"))
    if issues:
        return issues
    new_records = {}
    mutations = {}
    for coordinate, value in members.items():
        if coordinate in already_owned:
            continue
        if not isinstance(value, dict):
            continue
        family = coordinate.split("/")[1] if "/" in coordinate else ""
        if family in {"knowledge", "research_insights", "kind_definitions"}:
            for name in (value.get("id"), value.get("title"), value.get("token")):
                if isinstance(name, str) and name:
                    if name in new_records:
                        issues.append(issue("integration.new_identity", coordinate, "duplicate new identity: " + name))
                    new_records[name] = coordinate
        if family == "knowledge_changes" and isinstance(value.get("replacement_id"), str) and value['replacement_id']:
            name = value["replacement_id"]
            if name in new_records:
                issues.append(issue("integration.new_identity", coordinate, "duplicate new identity: " + name))
            new_records[name] = coordinate
    for coordinate, family, target, value in mutation_members(output, extensions):
        # Malformed IDs belong to the schema checker. Structural indexing must
        # not hash an outside JSON value before that rejection can be reported.
        if not isinstance(target, str):
            continue
        if target in mutations and owners[mutations[target]] != owners[coordinate]:
            issues.append(issue("integration.mutation_conflict", coordinate,
                                "mutations of one target must share a bundle", owners[coordinate]))
        mutations[target] = coordinate
    for coordinate, value in members.items():
        if coordinate in already_owned:
            continue
        refs = reference_ids(value)
        if isinstance(value, dict) and isinstance(value.get("kind"), str) and value['kind']:
            refs.add(value["kind"])
        if (coordinate.startswith("activity-extensions.json/knowledge_metadata/")
                and isinstance(value, dict) and isinstance(value.get("title"), str)):
            refs.add(value["title"])
        if coordinate.startswith("activity-extensions.json/question_routes/"):
            if owners[coordinate] != owners.get("output"):
                issues.append(issue("integration.reference_closure", coordinate,
                                    "question routing belongs with the response questions", owners[coordinate]))
        for reference in refs & new_records.keys():
            if owners[coordinate] != owners[new_records[reference]]:
                issues.append(issue("integration.reference_closure", coordinate,
                                    "merge bundles referencing new object: " + reference, owners[coordinate]))
    authorities = {row["id"] for key in ("grants", "decisions")
                   for row in context.get(key, []) if row.get("id")}
    input_records = {row["id"]: row for key in ("knowledge_catalog", "tasks")
                     for row in context.get(key, []) if row.get("id")}
    for bundle in manifest:
        ident = bundle["integration_id"]
        if bundle["impact_set"] and not any(owners[coordinate] == ident for coordinate in mutations.values()):
            issues.append(issue("integration.mutation_root", "output/integration_bundles",
                                "bundle declares impact without an existing mutation root", ident))
        for ref in set(bundle["authority_refs"]) - authorities:
            issues.append(issue("integration.authority_reference", "output/integration_bundles",
                                "authority is not in the fixed visible input: " + ref, ident))
        for target, coordinate in mutations.items():
            if owners[coordinate] != ident:
                continue
            expected = input_records.get(target, {}).get("content_sha256")
            if expected and bundle.get("previous_hashes", {}).get(target) != expected:
                issues.append(issue("integration.previous_hash", coordinate,
                                    "mutation must name the fixed input content hash", ident))
    return issues


def split_bundles(output, extensions, context, *, derived=None):
    """derived may carry derived_bundles() of these same arguments."""
    output, members = derived or derived_bundles(output, extensions, context)
    for declaration in output["integration_bundles"]:
        bundle = deepcopy(declaration)
        bundle["owns_response"] = "output" in declaration["members"]
        if split_research(context):
            sliced = deepcopy(members["output"])
            for family in ("knowledge", "relations"):
                sliced[family] = [deepcopy(members[path]) for path in declaration["members"]
                                  if path.startswith("output/" + family + "/")]
            if not bundle["owns_response"]:
                sliced["questions"] = []
        else:
            sliced = deepcopy(members["output"])
        bundle["output"] = sliced
        bundle["extensions"] = {}
        for path in declaration["members"]:
            if path.startswith("activity-extensions.json/"):
                family = path.split("/")[1]
                bundle["extensions"].setdefault(family, []).append(deepcopy(members[path]))
        # Hash only assigned values, never another independent bundle's report.
        bundle["payload_sha256"] = exact_content_hash({"declaration": declaration,
            "values": {path: members[path] for path in declaration["members"]}})
        yield bundle


def apply_bundles(instance, runtime, output, extensions, context, *, execution_id,
                  apply_bundle, validate_candidate, validate_current, publish,
                  submission_issues=()):
    """Apply one candidate at a time; return receipts and unchanged failed candidates.

    Every callback is mandatory. validate_current must reject stale hashes,
    missing required judgments and revoked permissions, and compute live impact.
    publish receives validate_candidate's result for the same candidate and
    must either complete one Git CAS or raise without publishing.
    CAS recovery/reloading and external actions belong to ENGINE.
    """
    try:
        derived = derived_bundles(output, extensions, context)
    except (TypeError, ValueError, AttributeError):
        derived = None  # inspect_bundles reports the malformed response as a global issue.
    issues = inspect_bundles(output, extensions, context, derived=derived) + list(submission_issues)
    global_issues = [row for row in issues if not row.get("integration_id")]
    working_instance, working_runtime = deepcopy(instance), deepcopy(runtime)
    results = []
    if global_issues:
        return {"instance": working_instance, "runtime": working_runtime, "bundles": [],
                "issues": issues, "retry_bundle_ids": [], "status": "returned"}
    output, members = derived
    for bundle in split_bundles(output, extensions, context, derived=derived):
        ident = bundle["integration_id"]
        local_issues = [row for row in issues if row.get("integration_id") == ident]
        receipt = working_runtime.get("integrations", {}).get(ident)
        if receipt:
            if receipt["payload_sha256"] == bundle["payload_sha256"]:
                results.append({"integration_id": ident, "status": "already_accepted", "issues": []})
                continue
            local_issues.append(issue("integration.id_reuse", "output/integration_bundles",
                                      "accepted ID cannot be reused for changed content", ident))
        stage = "currentness"
        try:
            if local_issues:
                raise ValueError("bundle has unresolved submission issues")
            candidate_instance, candidate_runtime = deepcopy(working_instance), deepcopy(working_runtime)
            validate_current(candidate_instance, candidate_runtime, bundle)
            stage = "application"
            apply_bundle(candidate_instance, candidate_runtime, bundle)
            candidate_runtime.setdefault("integrations", {})[ident] = {
                "id": ident, "execution_id": execution_id, "payload_sha256": bundle["payload_sha256"],
                "members": deepcopy(bundle["members"]), "input_snapshot": context.get("snapshot")}
            if bundle["owns_response"]:
                candidate_runtime["integrations"][ident]["response_sha256"] = exact_content_hash(members["output"])
            stage = "candidate"
            validated = validate_candidate(candidate_instance, candidate_runtime, bundle)
            stage = "publication"
            publish(candidate_instance, candidate_runtime, bundle, validated)
        except Exception as error:
            if not local_issues:
                # A changed premise found while applying is still a currentness return.
                rule = "integration.currentness" if isinstance(error, CurrentnessChanged) else "integration." + stage
                local_issues = [issue(rule, "output/integration_bundles", str(error), ident)]
            results.append({"integration_id": ident, "status": "returned", "issues": local_issues,
                            "next_owner": "producer" if stage != "publication" else "engine"})
            if isinstance(error, ImpactReviewRequired):
                results[-1].update(next_owner="impact_review", impact_review_request=deepcopy(error.request))
            from .trust_validation import EnvironmentUnavailable
            if isinstance(error, EnvironmentUnavailable):
                results[-1].update(next_owner='engine', environment_wait=dict(error.detail))
            # The durable parent may have changed. ENGINE must reload before
            # trying any further publication, never bless a stale candidate.
            if stage == "publication":
                for pending in output["integration_bundles"][len(results):]:
                    results.append({"integration_id": pending["integration_id"], "status": "returned",
                                    "issues": [issue("integration.publication", "output/integration_bundles",
                                        "reload current snapshot before retry", pending["integration_id"])], "next_owner": "engine"})
                break
            continue
        working_instance, working_runtime = candidate_instance, candidate_runtime
        results.append({"integration_id": ident, "status": "accepted", "issues": []})
    # ENGINE carries this list into the next repair contract. Preserve failures
    # first discovered during candidate validation/publication, not only input checks.
    issue_ids = {row["issue_id"] for row in issues}
    for result in results:
        for row in result["issues"]:
            if row["issue_id"] not in issue_ids:
                issues.append(row)
                issue_ids.add(row["issue_id"])
    returned = [row["integration_id"] for row in results if row["status"] == "returned"]
    # Partial only when another bundle is accepted, now or by an earlier receipt.
    status = "accepted" if not returned else "partial" if len(returned) < len(results) else "returned"
    return {"instance": working_instance, "runtime": working_runtime, "bundles": results,
            "issues": issues, "retry_bundle_ids": returned, "status": status}


def preview_bundles(instance, runtime, output, extensions, context, *, execution_id,
                    apply_bundle, validate_candidate, validate_current, submission_issues=()):
    """Run the identical candidate path on supplied fixed projections, without CAS.

    Central callers use the same pure domain callbacks used on receipt. The
    returned working sets and internal errors must stay central; submission's
    preview adapter emits a closed public result. This is not authority approval.
    """
    result = apply_bundles(instance, runtime, output, extensions, context, execution_id=execution_id,
        apply_bundle=apply_bundle, validate_candidate=validate_candidate, validate_current=validate_current,
        publish=lambda *args: None, submission_issues=submission_issues)
    result["mode"] = "preview"
    for row in result["bundles"]:
        if row["status"] == "accepted":
            row["status"] = "preview_passed"
    return result
