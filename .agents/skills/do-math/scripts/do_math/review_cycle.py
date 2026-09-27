"""Deterministic, JSON-serializable orchestration of independent identity review.

The caller owns execution budgets, source storage, and model execution. This module
checks provenance and completeness; mathematical claims remain the reviewers'.
"""
from __future__ import annotations

import copy
import hashlib
import json

import jsonschema

from .contracts import PROFILE_REF, REFS, TEXT
from .file_io import compact_json_bytes, json_digest
from .review_policy import build_review_policy, validate_scope_assessment, minimum_scope_executions


class ReviewRestorationError(ValueError):
    """A precise reconstruction fault, distinct from mathematical input drift."""
    def __init__(self, reason, *, cause_kind, coordinate, expected_sha256=None, observed_sha256=None,
                 verified_indices=(), retryable=False):
        super().__init__(reason)
        self.diagnostics = {'cause_kind': cause_kind, 'coordinate': copy.deepcopy(coordinate),
            'expected_sha256': expected_sha256, 'observed_sha256': observed_sha256,
            'preserved_range': {'slot': coordinate.get('slot'), 'verified_indices': list(verified_indices)},
            'retryable': retryable, 'continuity_broken': False}


def review_action(action):
    """Separate a review seat from the enclosing execution's authority fields."""
    fields = ('stage', 'slot', 'round')
    if action.get('replacement_for') is not None:
        fields += ('id', 'replacement_for', 'grant_id', 'grant_sha256', 'continuity_broken',
                   'actor_kind', 'purpose', 'continuity_break_cause')
    return {name: action[name] for name in fields if name in action}


def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _array(items):
    return {"type": "array", "items": items}


def stage_schema(stage):
    """The same schema is supplied to producers and checked before acceptance."""
    string = copy.deepcopy(TEXT)
    evidence = _array(string)
    finding = _object({"id": string, "statement": string, "evidence": evidence})
    common = {"proposal_digest": string, "summary": string, "used_sources": evidence,
              "questions": evidence}
    if stage in ("initial", "judge"):
        common.update(decision={"enum": ["match", "mismatch", "unresolved"]},
                      scope_complete={"type": "boolean"})
    if stage == "scope":
        # validate_scope_assessment accepts no selected profile, so the wire does too.
        slot = _object({"id": string, "perspective": string, "required_source_refs": {**REFS, "minItems": 1}})
        common.update(scope_complete={"type": "boolean"}, scope_assessment=copy.deepcopy(_object({
            "assessment_id": string, "policy_id": string, "policy_version": {"const": 5},
            "required_perspectives": REFS, "initial_slots": {"type": "array", "minItems": 1, "items": slot},
            "selected_profile_ref": {"anyOf": [{"type": "null"}, PROFILE_REF]},
            "activity_execution_limit": {"type": "integer", "minimum": 1},
            "overflow_disposition": {"enum": ["unresolved", "defer"]}})))
    elif stage == "initial":
        common["findings"] = _array(finding)
    elif stage == "organize":
        ref = _object({"stage": {"enum": ["initial", "judge", "answer"]},
                       "round": {"type": "integer", "minimum": 1}, "slot": string, "id": string})
        common["issues"] = _array(_object({"id": string, "finding_refs": _array(ref),
                                          "answer_role_slot_id": string}))
    elif stage == "answer":
        common["answers"] = _array(_object({"issue_id": string,
            "disposition": {"enum": ["maintain", "revise", "split", "withdraw"]},
            "statement": string, "evidence": evidence}))
        answer_finding = copy.deepcopy(finding)
        answer_finding["properties"]["parent_issue_ids"] = _array(string)
        answer_finding["required"].append("parent_issue_ids")
        common["new_findings"] = _array(answer_finding)
    elif stage == "judge":
        common["issue_verdicts"] = _array(_object({"issue_id": string,
            "decision": {"enum": ["approved", "rejected", "unresolved"]},
            "reason": string, "evidence": evidence}))
        common["new_findings"] = _array(finding)
    else:
        raise ValueError("unknown review stage")
    return _object(common)


def _check_schema(value, schema, label="output"):
    """Read a review schema with the JSON Schema validator the producer's check uses."""
    error = jsonschema.exceptions.best_match(jsonschema.Draft202012Validator(schema).iter_errors(value))
    if error is not None:
        raise ValueError(label + "".join(f"/{part}" for part in error.absolute_path) + ": " + error.message)


def _unique(values, label):
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


def _slots(value, prefix):
    if isinstance(value, int) and not isinstance(value, bool):
        if value < 1:
            raise ValueError("invalid allocation")
        return [f"{prefix}-{i}" for i in range(value)]
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x for x in value):
        raise ValueError("allocation must be a positive count or list of slot IDs")
    _unique(value, "slot")
    return list(value)


def start_review(proposal, reviewers, judges=3, max_rounds=3, previous=None, *, policy=None,
                 scope_assessment=None, owner_activity_id=None):
    if not isinstance(proposal, dict) or proposal.get("revision") is None:
        raise ValueError("proposal requires an exact revision")
    reviewer_slots, requested_judges = _slots(reviewers, "initial"), _slots(judges, "judge")
    if len(requested_judges) != 3 or isinstance(max_rounds, bool) or not isinstance(max_rounds, int) or max_rounds < 1:
        raise ValueError("exactly three judges and a positive round limit are required")
    _unique(reviewer_slots + requested_judges + ["scope", "organize"], "requested role slot")
    policy = build_review_policy(policy, reviewer_count=len(reviewer_slots), max_rounds=max_rounds,
                                 judge_slots=requested_judges)
    assessment = validate_scope_assessment(scope_assessment, policy) if scope_assessment is not None else None
    actual_reviewer_slots = [slot["id"] for slot in assessment["initial_slots"]] if assessment else []
    judge_slots, max_rounds = list(policy["judge_slots"]), policy["round_limit"]
    _unique(actual_reviewer_slots + judge_slots + ["scope", "organize"], "role slot")
    digest = json_digest(proposal)
    previous_reviews, turns, manifests = [], {}, {}
    lineage = proposal.get("review_lineage_id", digest)
    if previous is not None:
        _check_proposal(previous)
        if proposal["revision"] == previous["revision"]:
            raise ValueError("new review requires a new proposal revision")
        if assessment is not None and (not set(previous["reviewer_slots"]).issubset(actual_reviewer_slots) or judge_slots != previous["judge_slots"]):
            raise ValueError("existing logical slots must be retained")
        if proposal.get("review_lineage_id", previous["review_lineage_id"]) != previous["review_lineage_id"]:
            raise ValueError("proposal changes the inherited review lineage")
        if previous.get("review_policy") != policy:
            raise ValueError("a revised review must retain its frozen review policy")
        lineage = previous["review_lineage_id"]
        turns = copy.deepcopy(previous["turns"])
        manifests = copy.deepcopy(previous["transcript_manifest"])
        previous_reviews = copy.deepcopy(previous["previous_reviews"])
        previous_reviews.append({k: copy.deepcopy(previous[k]) for k in
            ("revision", "proposal_digest", "proposal", "results", "sealed", "issues", "status", "decision")})
        previous_reviews[-1]["research"] = copy.deepcopy(previous.get("research", {}))
    return {"proposal": copy.deepcopy(proposal), "proposal_digest": digest,
        "revision": proposal["revision"], "review_lineage_id": lineage,
        "reviewers": len(actual_reviewer_slots), "requested_reviewer_slots": reviewer_slots,
        "retained_reviewer_slots": list(previous["reviewer_slots"]) if previous is not None else [],
        "judges": 3, "reviewer_slots": actual_reviewer_slots,
        "judge_slots": judge_slots, "max_rounds": max_rounds, "round": 1,
        "review_policy": policy, "scope_assessment": assessment, "owner_activity_id": owner_activity_id,
        "activity_execution_limit": assessment["activity_execution_limit"] if assessment else policy["activity_execution_limit"],
        "required_source_refs": sorted({ref for slot in assessment["initial_slots"] for ref in slot["required_source_refs"]}) if assessment else [],
        "execution_accounting": {"executions_used": [], "reserved_execution_slots": []},
        "phase": "initial" if assessment is not None else "scope", "status": "working", "decision": None,
        "results": {}, "sealed": [], "turns": turns, "transcript_manifest": manifests,
        "issues": {}, "findings": {}, "pending_findings": [], "answer_requests": [],
        "history": [], "previous_reviews": previous_reviews, "followup": [],
        "deferred_actions": {}, "research": {}, "recovery_events": [],
        "continuity_events": [], "blocked_actions": {}, "replacement_actions": {},
        "replacement_receipts": []}


def _check_proposal(cycle):
    if json_digest(cycle["proposal"]) != cycle["proposal_digest"] or cycle["revision"] != cycle["proposal"]["revision"]:
        raise ValueError("sealed proposal changed")


def review_authors(cycle):
    """Every execution that authored this proposal or an earlier revision of its review lineage."""
    authors = set(cycle.get('producer_execution_ids', [])) | set(cycle['proposal'].get('producer_execution_ids', []))
    for previous in cycle.get('previous_reviews', []):
        authors.update(previous['proposal'].get('producer_execution_ids', []))
    return authors


def validate_review_independence(cycle, runtime, execution_id, action, *, excluded_execution_ids=()):
    """The one ancestry check for admission, live acceptance and sealed replay.

    It follows continuation and context origins transitively, so a reviewer that
    inherits author or peer context through any number of steps is rejected when
    its result arrives, not only when the finished review is reconstructed.
    """
    from .governance import validate_independent_execution
    authors = set(excluded_execution_ids) | review_authors(cycle)
    validate_independent_execution(runtime, execution_id, authors)
    pending, visited = [execution_id], set()
    while pending:
        eid = pending.pop()
        if eid in authors:
            raise ValueError('review inherited original author context')
        if eid in visited:
            continue
        visited.add(eid)
        row = runtime.get('executions', {}).get(eid)
        if row is None:
            raise ValueError('review context lineage does not resolve')
        for field in ('continuation_of', 'context_origin'):
            values = row.get(field) or []
            pending.extend([values] if isinstance(values, str) else values)
        origin_action = row.get('action', {})
        if eid != execution_id and origin_action.get('review_cycle_id') == cycle.get('id'):
            if origin_action.get('slot', origin_action.get('requesting_slot')) != action.get('slot', action.get('requesting_slot')):
                raise ValueError('logical review slot inherited private peer context')


def validate_review_execution(cycle, runtime, execution_id, action, output=None, *, instance=None, excluded_execution_ids=(), allow_incomplete=False):
    """Check actual ancestry, assignment and input/profile bindings, not an AI claim."""
    validate_review_independence(cycle, runtime, execution_id, action, excluded_execution_ids=excluded_execution_ids)
    execution = runtime['executions'][execution_id]
    actual = execution.get('action', {})
    role = action.get('role', 'identity_review')
    if instance is not None:
        from .execution_profiles import resolve_profile
        profile = resolve_profile(instance.get('execution_profiles', {}), execution.get('execution_profile_ref'))
        if profile['role'] != role or execution.get('actor_kind') != 'ai' or profile['actor_kind'] != 'ai':
            raise ValueError('review execution profile does not belong to its actual AI role')
    if (execution.get('role') != role or actual.get('review_cycle_id') != cycle.get('id')
            or any(actual.get(k) != v for k, v in action.items())
            or execution.get('status') not in {'running', 'stopping', 'ended'}
            or (not allow_incomplete and output is not None and 'output' in execution and execution['output'] != output)
            or (execution.get('status') == 'ended' and execution.get('outcome') != 'output_accepted'
                and not (allow_incomplete and execution.get('outcome') in {'execution_incomplete', 'cancelled', 'start_failed'}))):
        raise ValueError('review result is not bound to its actual accepted execution')
    if 'input_bindings' in cycle and role == 'identity_review':
        binding = cycle['input_bindings'].get(execution_id)
        if (not binding or binding.get('input_snapshot') != execution.get('input_snapshot')
                or binding.get('input_sha256') != execution['input_manifest']['prompt']['sha256']):
            raise ValueError('review input binding does not match the actual execution')
        if (binding.get('proposal_digest') != cycle['proposal_digest'] or binding.get('role_slot_id') != action['slot']
                or binding.get('profile_ref') != execution.get('execution_profile_ref')
                or cycle.get('slot_profiles', {}).get(action['slot']) != execution.get('execution_profile_ref')):
            raise ValueError('review profile or proposal binding changed')
    return execution


def validate_sealed_review(cycle, runtime, *, instance=None, excluded_execution_ids=(), read_artifact=None, git_dir=None, _seen=()):
    """Reconstruct a conclusion using the same accepting state machine as live review.

    No caller-supplied approval bit substitutes for execution, source or authority
    evidence. A repository owner may additionally verify exact artifact bytes.
    """
    _check_proposal(cycle)
    cid = cycle.get('id')
    if not cid or cid in _seen or cycle.get('status') == 'working' or cycle.get('decision') not in {'match', 'mismatch', 'unresolved'}:
        raise ValueError('review is not a completely sealed finite cycle')
    previous = None
    if cycle.get('previous_reviews'):
        archived = cycle['previous_reviews'][-1]
        matches = [row for identifier, row in runtime.get('review_cycles', {}).items() if identifier != cid
                   and all(row.get(k) == v for k, v in archived.items())]
        if len(matches) != 1:
            raise ValueError('previous review does not resolve to one preserved cycle')
        previous = matches[0]
        if previous['proposal'].get('assessment_reassessment') != cycle['proposal'].get('assessment_reassessment'):
            raise ValueError('previous review has a different judgment purpose')
        validate_sealed_review(previous, runtime, instance=instance, excluded_execution_ids=excluded_execution_ids,
                               read_artifact=read_artifact, git_dir=git_dir, _seen=(*_seen, cid))
    has_scope = any(e['action']['stage'] == 'scope' for e in cycle['results'].values())
    resource = validate_resource_disposition(cycle, runtime, read_artifact=read_artifact, instance=instance)
    if cycle['proposal'].get('assessment_reassessment') and not has_scope and resource is None:
        raise ValueError('reassessment requires an actual independent scope execution')
    replay = start_review(cycle['proposal'], cycle['requested_reviewer_slots'], cycle['judge_slots'], cycle['max_rounds'],
                          previous, policy=cycle['review_policy'], scope_assessment=None if has_scope else cycle['scope_assessment'])
    replay.update(id=cid, knowledge_id=cycle.get('knowledge_id'), identity_basis=copy.deepcopy(cycle.get('identity_basis')),
                  policy_ref=cycle.get('policy_ref'))
    consumed = []
    closures = [h for h in cycle.get('history', []) if h.get('event') == 'investigation_limit_closed']
    if len(closures) > 1:
        raise ValueError('review has conflicting closure evidence')
    while next_actions(replay):
        action = next_actions(replay)[0]
        if (closures or resource) and slot_key(action) not in cycle['results']:
            action = next((a for a in next_actions(replay) if slot_key(a) in cycle['results']), action)
        key = slot_key(action)
        if resource and key not in cycle['results']:
            if resource['state'] != 'ended':
                raise ValueError('review resource disposition has not ended')
            replay.update(status='unresolved', decision='unresolved', phase='done')
            break
        # Supplemental work returns only to its requesting slot before its final vote.
        for event in cycle.get('history', []):
            if event.get('event') != 'review_deferred_for_research' or event['action'] != action:
                continue
            records = [cycle['research'][rid] for rid in event['request_ids']]
            if all(r['id'] in replay['research'] for r in records):
                continue
            requester = records[0]['requested_by']
            messages = [m for m in cycle['turns'].get(action['slot'], []) if m.get('message_id') == requester + ':assistant']
            if len(messages) != 1 or 'provisional_result' not in messages[0]['content']:
                raise ValueError('supplemental request has no preserved provisional response')
            provisional = messages[0]['content']
            validate_review_execution(cycle, runtime, requester, action, provisional['provisional_result'], instance=instance, excluded_execution_ids=excluded_execution_ids)
            replay = defer_for_research(replay, action, provisional['provisional_result'], provisional['research_requests'], requester,
                                        limit=len(cycle['research']))
            for record in records:
                generated = replay['research'].get(record['id'])
                if generated is None or any(generated.get(k) != record.get(k) for k in ('question', 'source_refs', 'proposal_digest', 'action', 'requested_by')):
                    raise ValueError('fixed supplemental request changed')
                sources = record.get('source_records', [])
                if sources:
                    if research_request_digest(record['question'], cycle['proposal_digest'], sources) != record['request_digest']:
                        raise ValueError('supplemental fixed source digest changed')
                    from .repository import sealed_bytes
                    for source in sources:
                        if 'inline' in source:
                            raw = compact_json_bytes(source['inline'])
                            if len(raw) != source['bytes'] or hashlib.sha256(raw).hexdigest() != source['sha256']:
                                raise ValueError('supplemental source bytes changed')
                        elif read_artifact:
                            # A sealed row is compared once per process (contract S3).
                            sealed_bytes(git_dir, source['artifact_ref'], source['sha256'], source['bytes'],
                                         lambda: read_artifact(source['artifact_ref'], source['snapshot']),
                                         needed=False, error='supplemental source bytes changed')
                    generated.update(source_records=copy.deepcopy(sources), request_digest=record['request_digest'])
                elif generated['request_digest'] != record['request_digest']:
                    raise ValueError('supplemental request digest changed')
                result = record.get('result')
                if not result:
                    raise ValueError('supplemental investigation is incomplete')
                research_action = {'role': 'supplemental_research', 'research_request_id': record['id']}
                validate_review_execution(cycle, runtime, result['execution_id'], research_action, result['output'],
                    instance=instance, excluded_execution_ids=excluded_execution_ids, allow_incomplete=result.get('execution_status') == 'incomplete')
                replay = accept_research_result(replay, record['id'], result['output'], result['execution_id'],
                    result.get('source_records'), execution_status=result.get('execution_status', 'completed'))
        entry = cycle['results'].get(key)
        if entry is None and closures and closures[0]['action'] == action:
            closure = closures[0]
            eid = closure['execution_id']
            messages = [m for m in cycle['turns'].get(action['slot'], []) if m.get('message_id') == eid + ':assistant']
            if len(messages) != 1 or 'provisional_result' not in messages[0]['content']:
                raise ValueError('review closure lacks its actual provisional response')
            provisional = messages[0]['content']
            validate_review_execution(cycle, runtime, eid, action, provisional['provisional_result'], instance=instance, excluded_execution_ids=excluded_execution_ids)
            limit = (instance or {}).get('config', {}).get('review_research_limit', 3)
            if limit != closure['limit']:
                raise ValueError('review closure limit no longer matches its governing configuration')
            available = closure['budget_available']
            if not available:
                used = cycle.get('execution_accounting', {}).get('executions_used', [])
                if eid not in used or len(used) != len(set(used)) or any(i not in runtime['executions'] for i in used):
                    raise ValueError('review budget closure has no actual execution accounting')
                projected = {**runtime['executions'], eid: {**runtime['executions'][eid], 'status': 'ended'}}
                reserved = reserved_review_slots(replay, projected)
                if len(used) + len(provisional['research_requests']) + len(reserved) <= cycle['activity_execution_limit']:
                    raise ValueError('review budget closure is not exhausted')
            replay = defer_for_research(replay, action, provisional['provisional_result'], provisional['research_requests'], eid,
                                        limit=limit, budget_available=available)
            if replay['status'] == 'working':
                raise ValueError('review closure is not justified by its limits')
            break
        if entry is None or (key not in cycle.get('sealed', []) and not closures and not resource):
            raise ValueError('review is not completely sealed')
        actual_action = entry['action']
        if actual_action.get('replacement_for') is not None:
            replay = _replay_replacement(replay, cycle, actual_action, instance, runtime)
        validate_review_execution(cycle, runtime, entry['execution_id'], actual_action, entry['output'], instance=instance, excluded_execution_ids=excluded_execution_ids)
        if actual_action['stage'] == 'scope':
            used = cycle.get('execution_accounting', {}).get('executions_used', [])
            replay['execution_accounting']['executions_used'] = used[:used.index(entry['execution_id']) + 1] if entry['execution_id'] in used else []
        replay = accept_result(replay, actual_action, entry['output'], entry['execution_id'], entry.get('manifest'))
        consumed.append(key)
    if (set(consumed) != set(cycle['results']) or any(replay[k] != cycle[k] for k in
            ('status', 'decision', 'phase', 'round', 'results', 'sealed', 'scope_assessment', 'issues', 'findings',
             'previous_reviews', 'research', 'replacement_receipts', 'reviewer_slots', 'judge_slots',
             'activity_execution_limit', 'required_source_refs'))):
        raise ValueError('review conclusion differs from sealed evidence')
    # Use the restoration checker on each finished logical slot without exposing
    # one slot's private conversation to another.
    for slot in cycle['turns']:
        validate_transcript(cycle, slot)
    return replay


def identity_assessment(cycle, *, reason):
    """Derive the public judgment receipt from a sealed review cycle."""
    final_entries = [cycle['results'][key] for key in cycle['sealed']
                     if cycle['results'][key]['action']['stage'] == ('initial' if not cycle['issues'] else 'judge')]
    if cycle['issues']:
        final_entries = [entry for entry in final_entries if entry['action']['round'] == cycle['round']]
    return {'review_cycle_id': cycle['id'],
            'proposal_digest': cycle['proposal_digest'], 'decision': cycle['decision'],
            'execution_ids': [entry['execution_id'] for entry in final_entries],
            'scope_complete': bool(final_entries) and all(entry['output'].get('scope_complete') for entry in final_entries),
            'summary': reason}


def _manifest_fault(message, entry, position):
    """Why one transcript message fails its manifest row, or None when it verifies."""
    if (not isinstance(message, dict) or not {'role', 'content'} <= message.keys()
            or not isinstance(entry, dict) or not {'sha256', 'bytes', 'index', 'proposal_digest', 'ref'} <= entry.keys()
            or entry['index'] != position):
        return 'invalid_manifest'
    raw = compact_json_bytes(message)
    if hashlib.sha256(raw).hexdigest() != entry['sha256'] or len(raw) != entry['bytes']:
        return 'content_mismatch'
    return None


def _verified_transcript(turns, manifests):
    """Pair each message whose original hash still verifies with its manifest; list the rest."""
    verified, omitted = [], []
    for position in range(max(len(turns), len(manifests))):
        if (position < len(turns) and position < len(manifests)
                and _manifest_fault(turns[position], manifests[position], position) is None):
            verified.append((turns[position], manifests[position]))
        else:
            omitted.append(position)
    return verified, omitted


def _replacement_sealed_input(cycle, verified_manifests):
    """Sealed replacement input; authorization and sealed replay hash this same value."""
    return {'proposal_digest': cycle['proposal_digest'], 'identity_basis': cycle.get('identity_basis'),
            'policy_ref': cycle.get('policy_ref'), 'scope_assessment': cycle.get('scope_assessment'),
            'sealed_results': {k: cycle['results'][k] for k in cycle['sealed']},
            'verified_transcript': verified_manifests}


def _replay_replacement(replay, cycle, action, instance, runtime):
    if instance is None:
        raise ValueError('replacement replay requires current governance sources')
    receipts = [r for r in cycle.get('replacement_receipts', []) if r['action'] == action]
    if len(receipts) != 1 or not receipts[0].get('authorization'):
        raise ValueError('replacement has no preserved authorization and sealed input')
    authorization = receipts[0]['authorization']
    index = action['replacement_for']
    event = cycle['recovery_events'][index]
    if event['retryable'] or event['action'] != {k: action[k] for k in ('stage', 'slot', 'round')}:
        raise ValueError('replacement recovery coordinate changed')
    authority = replacement_authority(instance, runtime, cycle, authorization, receipts[0]['execution_id'])
    if not authority['allowed'] or authority['grant_sha256'] != action['grant_sha256']:
        raise ValueError('replacement authority is not current')
    archive = next((r for r in cycle.get('transcript_replacements', []) if r['recovery_event'] == index and r['slot'] == action['slot']), None)
    if archive is None:
        raise ValueError('replacement transcript archive is missing')
    verified, omitted = _verified_transcript(archive['turns'], archive['manifest'])
    sealed_input = _replacement_sealed_input(replay, [manifest for _, manifest in verified])
    if (omitted != authorization['omitted_indices'] or omitted != archive['omitted_indices']
            or json_digest(sealed_input) != authorization['sealed_input_sha256']):
        raise ValueError('replacement sealed input changed')
    replay['blocked_actions'][slot_key(action)] = index
    replay['replacement_actions'][slot_key(action)] = copy.deepcopy(authorization)
    return replay


def replacement_authority(instance, runtime, cycle, replacement, execution_id=None):
    """One authority check for live admission/acceptance and sealed reconstruction."""
    from .governance import authorize_review_replacement
    from .repository import exact_content_hash
    binding = cycle.get('input_bindings', {}).get(execution_id, {})
    consumed = binding.get('delegation_authority') or cycle.get('execution_accounting', {}).get(
        'admissions', {}).get(execution_id, {}).get('delegation_authority')
    if consumed is not None:
        from .delegations import validate_delegation
        try:
            app = runtime['delegation_applications'][consumed['application_id']]
            if exact_content_hash(app) != consumed['application_sha256'] or not app.get('application'):
                raise ValueError('applied delegation receipt changed')
            if replacement.get('case', {}).get('application_id') != app['id'] or replacement.get('delegation_id') != app['delegation_id']:
                raise ValueError('replacement names another applied delegation')
            basis = app['basis']
            if validate_delegation(instance['delegations'][app['delegation_id']]) != basis['delegation']:
                raise ValueError('delegation authority changed after admission')
            for name in ('original_decision', 'approval'):
                if instance['decisions'].get(basis[name]['id']) != basis[name]:
                    raise ValueError('delegation approval changed after admission')
            for name in ('source', 'original_source'):
                if instance['governance_sources'].get(basis[name]['id']) != basis[name]:
                    raise ValueError('delegation source changed after admission')
            for judgment in app['judgments'].values():
                if exact_content_hash(runtime['executions'][judgment['execution_id']]) != consumed['judgment_executions'][judgment['execution_id']]:
                    raise ValueError('delegation judgment execution changed after admission')
        except (KeyError, ValueError) as error:
            return {'allowed': False, 'reason': str(error)}
        authority = authorize_review_replacement(instance, runtime, replacement['authority_request'])
    else:
        authority = authorize_review_replacement(instance, runtime, replacement['authority_request'],
            delegation_id=replacement.get('delegation_id'), case=replacement.get('case'))
    if authority.get('allowed') and authority['grant_sha256'] != replacement['grant_sha256']:
        return {'allowed': False, 'reason': 'replacement grant changed'}
    return authority


def slot_key(action):
    """The key of one logical seat in results, blocked and replacement maps."""
    return f"{action['stage']}:{action['round']}:{action['slot']}"


def reserved_review_slots(cycle, executions):
    """Potential mandatory continuations; optional work cannot spend these seats."""
    if cycle.get('status') != 'working':
        return []
    slots = cycle['reviewer_slots'] or cycle['requested_reviewer_slots']
    candidates = [{'stage': 'scope', 'slot': 'scope', 'round': 1}]
    candidates += [{'stage': 'initial', 'slot': slot, 'round': 1} for slot in slots]
    for number in range(1, cycle['max_rounds'] + 1):
        candidates.append({'stage': 'organize', 'slot': 'organize', 'round': number})
        if number > 1:
            candidates += [{'stage': 'answer', 'slot': slot, 'round': number} for slot in slots]
        candidates += [{'stage': 'judge', 'slot': slot, 'round': number} for slot in cycle['judge_slots']]
    ranks = {'scope': 0, 'initial': 1, 'organize': 2, 'answer': 3, 'judge': 4}
    current = (cycle['round'], ranks[cycle['phase']])
    live = {slot_key(row['action']) for row in executions.values()
            if row.get('status') != 'ended' and row.get('action', {}).get('review_cycle_id') == cycle.get('id')
            and row['action'].get('role') == 'identity_review'}
    return [row for row in candidates if (row['round'], ranks[row['stage']]) >= current
            and slot_key(row) not in cycle['results'] and slot_key(row) not in live]


def _phase_actions(cycle):
    stage = cycle["phase"]
    if stage == "scope":
        slots = ["scope"]
    elif stage == "initial":
        slots = cycle["reviewer_slots"]
    elif stage == "organize":
        slots = ["organize"]
    elif stage == "judge":
        slots = cycle["judge_slots"]
    elif stage == "answer":
        slots = [slot for slot in cycle["reviewer_slots"] if any(
            cycle["issues"][i]["answer_role_slot_id"] == slot for i in cycle["answer_requests"])]
    else:
        slots = []
    return [{"stage": stage, "slot": slot, "round": cycle["round"]} for slot in slots]


def next_actions(cycle):
    _check_proposal(cycle)
    if cycle["status"] != "working" or resource_disposition(cycle):
        return []
    pending = []
    for action in _phase_actions(cycle):
        key = slot_key(action)
        if key in cycle["results"] or key in cycle.get("deferred_actions", {}):
            continue
        replacement = cycle.get("replacement_actions", {}).get(key)
        if replacement is not None:
            pending.append(copy.deepcopy(replacement["action"]))
        elif key not in cycle.get("blocked_actions", {}):
            pending.append(action)
    return pending


def resource_disposition(cycle):
    return next((row for row in cycle.get('history', []) if row.get('event') == 'review_resource_disposition'), None)


def validate_resource_disposition(cycle, runtime, *, read_artifact=None, instance=None):
    """Check machine closure evidence without manufacturing an identity judgment."""
    record = resource_disposition(cycle)
    if record is None:
        return None
    if sum(row.get('event') == 'review_resource_disposition' for row in cycle['history']) != 1:
        raise ValueError('review has duplicate resource dispositions')
    if record.get('state') not in {'draining', 'deferred', 'ended'}:
        raise ValueError('unknown review resource disposition state')
    if record['state'] == 'ended' and (cycle['status'], cycle['decision'], cycle['phase']) != ('unresolved', 'unresolved', 'done'):
        raise ValueError('ended resource disposition must preserve an unresolved review')
    if (record['proposal_digest'] != cycle['proposal_digest'] or record['policy'] != cycle['review_policy']
            or record['limit'] != cycle['activity_execution_limit']
            or record['disposition'] != cycle['review_policy']['overflow_disposition']):
        raise ValueError('review resource disposition changed its fixed basis')
    used = record['executions_used']
    if len(used) != len(set(used)) or used != cycle['execution_accounting']['executions_used']:
        raise ValueError('review resource disposition changed execution accounting')
    for eid in used:
        execution = runtime.get('executions', {}).get(eid, {})
        if execution.get('actor_kind') != 'ai' or execution.get('owner_activity_id') != cycle['owner_activity_id']:
            raise ValueError('review resource disposition lacks actual owned AI attempts')
    detail = record['detail']
    reason = record['reason']
    if reason == 'review_budget_exhausted':
        if len(used) < record['limit']:
            raise ValueError('review execution limit is not exhausted')
    elif reason == 'review_scope_unaffordable':
        count = max(cycle['review_policy']['minimum_initial_slots'], len(cycle['retained_reviewer_slots']))
        if minimum_scope_executions(count, cycle['max_rounds'], len(used) + 1) <= record['limit']:
            raise ValueError('minimum review scope fits the execution limit')
    elif reason == 'review_followup_reserved':
        if len(used) + 1 + len(detail['reserved_execution_slots']) <= record['limit']:
            raise ValueError('review followup fits the available resources')
    elif reason == 'review_input_overflow':
        overflow = detail['overflow']
        if (overflow.get('cause') != 'current_proposal_or_required_sources'
                or overflow['without_restored_dialogue_bytes'] <= overflow['limit_bytes']
                or detail['execution_id'] not in used):
            raise ValueError('review overflow does not establish a proposal input excess')
        if read_artifact is not None and json.loads(read_artifact(detail['overflow_ref'], None)) != overflow:
            raise ValueError('review overflow differs from preserved measurement')
    elif reason == 'review_host_configuration_changed':
        if not detail.get('profile_refs'):
            raise ValueError('review host change has no pinned profile evidence')
        pinned = [*cycle.get('slot_profiles', {}).values(),
                  (cycle.get('scope_assessment') or {}).get('selected_profile_ref')]
        pinned += [runtime['executions'][eid].get('execution_profile_ref') for eid in used]
        if any(ref not in pinned for ref in detail['profile_refs']):
            raise ValueError('review host change refers to a profile outside the frozen review')
        if instance is not None:
            from .execution_profiles import resolve_profile
            approved = detail['adopted_host_ref']
            if approved is not None and instance['capacity_constraints'][approved]['kind'] != 'host':
                raise ValueError('review host change names no adopted host constraint')
            expected = [approved] if approved else []
            if any(resolve_profile(instance['execution_profiles'], ref).get('host_capacity_refs', []) == expected
                   for ref in detail['profile_refs']):
                raise ValueError('review pinned profile already matches the host configuration')
    else:
        raise ValueError('unknown review resource disposition')
    if record['state'] == 'ended' and any(runtime['executions'][eid]['status'] != 'ended' for eid in used):
        raise ValueError('review closed before its attempts ended')
    return record


def research_request_digest(question, proposal_digest, sources):
    """Bind a fixed investigation to its question, proposal edition and exact source bytes."""
    from .repository import exact_content_hash
    return exact_content_hash({'question': question, 'proposal_digest': proposal_digest,
        'sources': [{key: source[key] for key in ('ref', 'sha256', 'bytes')} for source in sources]})


def research_schema():
    # Every field gets its own copy; deepcopy of one shared node keeps it shared.
    def text():
        return copy.deepcopy(TEXT)
    return _object({"summary": text(), "used_sources": _array(text()),
        "questions": _array(text()), "research_request_id": text(),
        "request_digest": text(), "outcome": {"enum": ["answered", "unresolved"]},
        "answer": text(), "scope_complete": {"type": "boolean"},
        "evidence_refs": _array(text())})


def research_request_schema():
    """One fixed investigation request, as installed for producers and replayed by review."""
    return copy.deepcopy(_object({"id": TEXT, "question": TEXT, "source_refs": {**REFS, "minItems": 1}}))


def validate_research_requests(requests):
    """Shared by the producer's check and review deferral: exact sources, distinct request IDs."""
    _check_schema(requests, {"type": "array", "minItems": 1, "items": research_request_schema()}, "research_requests")
    _unique([r["id"] for r in requests], "research request ID")


def validate_provisional(proposal_digest, action, output):
    """A review that requests investigation returns an unresolved provisional result for this proposal."""
    _check_schema(output, stage_schema(action["stage"]))
    if output["proposal_digest"] != proposal_digest:
        raise ValueError("result belongs to another proposal")
    if action["stage"] in ("initial", "judge") and output["decision"] != "unresolved":
        raise ValueError("a review requesting investigation must return unresolved provisionally")


def validate_research_answer(output):
    """An answered investigation states complete scope and exact evidence and leaves no question."""
    if output["outcome"] == "answered" and (not output["scope_complete"] or not output["evidence_refs"] or output["questions"]):
        raise ValueError("answered investigation requires complete scope, exact evidence and no unresolved question")


def classify_research_source(reference, *, proposal, issues, own_source_refs, sources, knowledge_ids):
    """The one admission rule for a fixed investigation source.

    Returns (kind, value): ('proposal', resolved value), ('issue', public issue),
    ('transcript', own-slot reference), ('source', supplied source row) or
    ('knowledge', ID). Each caller passes the records of its own input; the
    receiver's current knowledge IDs contain the catalog it supplied to the producer.
    """
    from .input_basis import aliases
    if reference == "proposal":
        return "proposal", proposal
    if reference.startswith("proposal:"):
        value = proposal
        for token in reference.removeprefix("proposal:").replace("/", ".").strip(".").split("."):
            if not isinstance(value, dict) or token not in value:
                raise ValueError("unknown proposal source coordinate: " + reference)
            value = value[token]
        return "proposal", value
    if reference.startswith("issue:"):
        issue_id = reference.removeprefix("issue:")
        if issue_id not in issues:
            raise ValueError("unknown public issue source: " + reference)
        return "issue", issues[issue_id]
    if reference in own_source_refs:
        return "transcript", reference
    source = next((row for row in sources if reference in aliases(row)), None)
    if source is not None:
        return "source", source
    if reference in knowledge_ids:
        return "knowledge", reference
    raise ValueError("research source must be a proposal coordinate, public issue, own transcript, "
                     "supplied source or knowledge ID: " + reference)


def defer_for_research(cycle, action, output, requests, execution_id, *, limit=3, budget_available=True):
    """Preserve a provisional response without turning it into a sealed verdict."""
    if action not in next_actions(cycle): raise ValueError("review action is not pending")
    validate_provisional(cycle["proposal_digest"], action, output)
    validate_research_requests(requests)
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0: raise ValueError("invalid research limit")
    used = {entry["execution_id"] for entry in cycle["results"].values()}
    used.update(r["requested_by"] for r in cycle.get("research", {}).values())
    used.update(r["result"]["execution_id"] for r in cycle.get("research", {}).values() if r.get("result"))
    if not isinstance(execution_id, str) or not execution_id or execution_id in used:
        raise ValueError("research request requires a fresh review execution")
    n = copy.deepcopy(cycle)
    n = _append_turns(n, action["slot"], [{"role": "assistant", "message_id": f"{execution_id}:assistant",
                                          "content": {"provisional_result": output, "research_requests": requests}}])
    if len(n.get("research", {})) + len(requests) > limit or not budget_available:
        n['history'].append({'event': 'investigation_limit_closed', 'action': copy.deepcopy(action),
                             'execution_id': execution_id, 'limit': limit, 'budget_available': budget_available})
        n["followup"].append({"reason": "supplemental investigation limit or reserved review budget exhausted",
                              "action": copy.deepcopy(action), "research_requests": copy.deepcopy(requests)})
        _finish(n, "unresolved", "Required investigation cannot fit the remaining review resources")
        return n
    identifiers = []
    for request in requests:
        identifier = f"{execution_id}:{request['id']}"
        if identifier in n.setdefault("research", {}): raise ValueError("research request execution was already used")
        payload = {"question": request["question"], "source_refs": request["source_refs"],
                   "proposal_digest": n["proposal_digest"]}
        n["research"][identifier] = {"id": identifier, **copy.deepcopy(payload), "request_digest": json_digest(payload),
            "action": copy.deepcopy(action), "requested_by": execution_id, "status": "pending", "result": None}
        identifiers.append(identifier)
    n.setdefault("deferred_actions", {})[slot_key(action)] = identifiers
    n["history"].append({"event": "review_deferred_for_research", "action": copy.deepcopy(action), "request_ids": identifiers})
    return n


def accept_research_result(cycle, request_id, output, execution_id, source_records=None, *, execution_status="completed"):
    _check_proposal(cycle)
    request = cycle.get("research", {}).get(request_id)
    if cycle["status"] != "working" or not request or request["status"] != "pending":
        raise ValueError("investigation is not pending")
    _check_schema(output, research_schema())
    if execution_status not in {"completed", "incomplete"} or (execution_status == "incomplete" and output["outcome"] != "unresolved"):
        raise ValueError("an incomplete investigation cannot supply an answered result")
    if output["research_request_id"] != request_id or output["request_digest"] != request["request_digest"]:
        raise ValueError("investigation result belongs to a different fixed question")
    validate_research_answer(output)
    used_ids = {entry["execution_id"] for entry in cycle["results"].values()}
    used_ids.update(r["requested_by"] for r in cycle.get("research", {}).values())
    used_ids.update(r["result"]["execution_id"] for r in cycle.get("research", {}).values() if r.get("result"))
    if not isinstance(execution_id, str) or not execution_id or execution_id in used_ids:
        raise ValueError("investigation requires a fresh execution distinct from review slots")
    n = copy.deepcopy(cycle)
    entry = n["research"][request_id]
    entry["status"] = output["outcome"]
    entry["result"] = {"execution_id": execution_id, "output": copy.deepcopy(output),
                       "source_records": copy.deepcopy(source_records or []), "execution_status": execution_status}
    n = _append_turns(n, request["action"]["slot"], [{"role": "tool", "kind": "supplemental_research",
        "message_id": f"{execution_id}:research-result", "call": "supplemental_research",
        "arguments": {"research_request_id": request_id, "request_digest": request["request_digest"]},
        "content": copy.deepcopy(entry)}])
    key = slot_key(request["action"])
    if all(n["research"][rid]["status"] != "pending" for rid in n["deferred_actions"][key]):
        del n["deferred_actions"][key]
    return n


def _add_findings(cycle, action, output):
    findings = output.get("findings", output.get("new_findings", []))
    for finding in findings:
        ref = {**{k: action[k] for k in ('stage', 'slot', 'round')}, 'id': finding['id']}
        key = json_digest(ref)
        cycle["findings"][key] = {"ref": ref, "finding": copy.deepcopy(finding)}
        cycle["pending_findings"].append(key)
    # Questions and uncompleted scope must remain explicit input to organization.
    questions = list(output.get("questions", []))
    if action["stage"] == "initial" and (not output["scope_complete"] or output["decision"] == "unresolved"):
        questions.append("Required initial review scope or judgment remains unresolved.")
    for i, question in enumerate(questions):
        ref = {**{k: action[k] for k in ('stage', 'slot', 'round')}, 'id': f'__question_{i}'}
        key = json_digest(ref)
        cycle["findings"][key] = {"ref": ref, "finding": {"id": ref["id"],
            "statement": question, "evidence": output["used_sources"]}}
        cycle["pending_findings"].append(key)


def _finish(cycle, decision, reason):
    cycle.update(status="unresolved" if decision == "unresolved" else "completed",
                 phase="ended", decision=decision)
    cycle["history"].append({"round": cycle["round"], "event": "closed", "reason": reason})


def _organize(cycle, output):
    _unique([x["id"] for x in output["issues"]], "issue ID")
    linked = []
    for issue in output["issues"]:
        if issue["id"] in cycle["issues"]:
            raise ValueError("organizer cannot replace an existing issue")
        refs = issue["finding_refs"]
        if not refs:
            raise ValueError("issue requires original finding references")
        keys = [json_digest(ref) for ref in refs]
        if any(key not in cycle["pending_findings"] for key in keys):
            raise ValueError("organizer forged or reused an original finding")
        _unique(keys, "finding reference")
        owners = {ref["slot"] for ref in refs if ref["stage"] in ("initial", "answer")}
        if len(owners) > 1:
            raise ValueError("distinct reviewers' findings must retain separate ownership")
        owner = issue["answer_role_slot_id"]
        if owner not in cycle["reviewer_slots"] or (owners and owner not in owners):
            raise ValueError("answer must return to its original reviewer or an eligible assigned slot")
        linked.extend(keys)
        cycle["issues"][issue["id"]] = {**copy.deepcopy(issue), "version": 1,
            "status": "open", "answers": [], "verdicts": [], "answer": None}
        if cycle["round"] > 1:
            cycle["answer_requests"].append(issue["id"])
    _unique(linked, "original finding linkage")
    if set(linked) != set(cycle["pending_findings"]):
        raise ValueError("organizer omitted original findings")
    cycle["pending_findings"] = []
    if not cycle["issues"]:
        _finish(cycle, "unresolved", "No complete issue mapping was available")
    else:
        cycle["phase"] = "answer" if cycle["answer_requests"] else "judge"


def _answer(cycle, action, output):
    expected = {i for i in cycle["answer_requests"] if cycle["issues"][i]["answer_role_slot_id"] == action["slot"]}
    ids = [a["issue_id"] for a in output["answers"]]
    _unique(ids, "answer issue")
    if set(ids) != expected:
        raise ValueError("answer must cover every assigned issue exactly once")
    for finding in output["new_findings"]:
        parents = finding["parent_issue_ids"]
        _unique(parents, "parent issue")
        if set(parents) - expected:
            raise ValueError("new finding must retain this answerer's original issue lineage")
    for answer in output["answers"]:
        if not answer["evidence"]:
            raise ValueError("answer disposition requires evidence")
        if answer["disposition"] == "split" and sum(
                answer["issue_id"] in f["parent_issue_ids"] for f in output["new_findings"]) < 2:
            raise ValueError("split must identify at least two derived findings")
    # Applied only once all answers are sealed, so peers never see this result early.


def _judge(cycle, output):
    ids = [v["issue_id"] for v in output["issue_verdicts"]]
    _unique(ids, "judge issue")
    if set(ids) != set(cycle["issues"]):
        raise ValueError("judge must assess every current issue exactly once")
    for verdict in output["issue_verdicts"]:
        if verdict["decision"] != "unresolved" and not verdict["evidence"]:
            raise ValueError("decisive issue verdict requires evidence")
    if output["decision"] == "match" and (output["new_findings"] or output["questions"] or any(
            x["decision"] != "rejected" for x in output["issue_verdicts"])):
        raise ValueError("match cannot conceal an open or established objection")
    if output["decision"] == "mismatch" and not (output["new_findings"] or any(
            x["decision"] == "approved" for x in output["issue_verdicts"])):
        raise ValueError("mismatch requires an identified objection")


def _validate_content(cycle, action, output):
    """Check one stage result; a scope result returns its normalized assessment."""
    _check_schema(output, stage_schema(action["stage"]))
    if output["proposal_digest"] != cycle["proposal_digest"]:
        raise ValueError("result belongs to another proposal")
    stage = action["stage"]
    if stage in ("initial", "judge") and output["decision"] == "match" and not output["scope_complete"]:
        raise ValueError("match requires complete scope")
    findings = output.get("findings", output.get("new_findings", []))
    _unique([f["id"] for f in findings], "finding ID")
    if any(f["id"].startswith("__question_") or not f["evidence"] for f in findings):
        raise ValueError("finding requires evidence and a nonreserved ID")
    if stage == "scope":
        assessment = validate_scope_assessment(output["scope_assessment"], cycle["review_policy"],
            executions_used=cycle.get('scope_executions_used', len(cycle.get('execution_accounting', {}).get('executions_used', []))))
        if not output["scope_complete"] or output["questions"]:
            raise ValueError("scope assessment must be complete and leave no open questions")
        if cycle.get("retained_reviewer_slots") and not set(cycle["retained_reviewer_slots"]).issubset(
                {slot["id"] for slot in assessment["initial_slots"]}):
            raise ValueError("new scope assessment cannot remove retained logical slots")
        return assessment
    if stage == "initial":
        if output["decision"] == "match" and (findings or output["questions"]):
            raise ValueError("match requires no open findings or questions")
        if output["decision"] == "mismatch" and not findings:
            raise ValueError("mismatch requires findings")
    return None


def validate_visible_output(context, action, output, *, requesting_research=False):
    """Use only the public assignment and this slot's input, never peer votes."""
    if requesting_research:
        validate_provisional(context["proposal_digest"], action, output)
        return
    _validate_content(context, action, output)
    view = {"issues": copy.deepcopy(context["issues"]), "round": action["round"],
            "answer_requests": list(context["answer_requests"]), "reviewer_slots": context["reviewer_slots"],
            "pending_findings": [json_digest(row["ref"]) for row in context["pending_findings"]], "history": []}
    if action["stage"] == "organize":
        _organize(view, output)
    elif action["stage"] == "answer":
        _answer(view, action, output)
    elif action["stage"] == "judge":
        _judge(view, output)


def _aggregate_judges(cycle, entries):
    retry = []
    for issue_id, issue in cycle["issues"].items():
        votes = [next(v for v in entry["output"]["issue_verdicts"] if v["issue_id"] == issue_id) for entry in entries]
        decisions = {v["decision"] for v in votes}
        # An objection version that all three judges approved is sealed as established;
        # later votes on the same version cannot undo it (a changed version is judged anew).
        sealed = any(record.get("version") == issue["version"] and record.get("results")
                     and all(result.get("decision") == "approved" for result in record["results"])
                     for record in issue["verdicts"])
        status = "approved" if sealed else (next(iter(decisions)) if len(decisions) == 1 else "unresolved")
        issue["status"] = status
        issue["verdicts"].append({"round": cycle["round"], "version": issue["version"], "results": copy.deepcopy(votes)})
        withdrawal_confirmed = status == "rejected" and issue["answers"] and issue["answers"][-1]["disposition"] == "withdraw"
        if status != "approved" and not withdrawal_confirmed:
            retry.append(issue_id)
    for entry in entries:
        _add_findings(cycle, entry["action"], entry["output"])
    decisions = {entry["output"]["decision"] for entry in entries}
    complete = all(entry["output"]["scope_complete"] for entry in entries)
    if cycle["round"] < cycle["max_rounds"] and (retry or cycle["pending_findings"]):
        cycle["round"] += 1
        cycle["answer_requests"] = retry
        cycle["phase"] = "organize" if cycle["pending_findings"] else "answer"
        return
    if cycle["pending_findings"]:
        cycle["followup"].append({"reason": "new findings at round limit", "finding_refs": [
            copy.deepcopy(cycle["findings"][key]["ref"]) for key in cycle["pending_findings"]]})
    unresolved_issues = [i for i, issue in cycle["issues"].items() if issue["status"] == "unresolved"]
    if unresolved_issues:
        cycle["followup"].append({"reason": "unresolved objections", "issue_ids": unresolved_issues,
                                 "answer_slots": {i: cycle["issues"][i]["answer_role_slot_id"] for i in unresolved_issues}})
    established = [i for i, issue in cycle["issues"].items() if issue["status"] == "approved"]
    if established and decisions == {"match"}:
        cycle["followup"].append({"reason": "match conflicts with an established objection", "issue_ids": established})
    if (len(decisions) == 1 and "unresolved" not in decisions and complete and not cycle["pending_findings"]
            and not unresolved_issues and not (established and decisions == {"match"})):
        _finish(cycle, next(iter(decisions)), "All three independent final judgments sealed")
    else:
        _finish(cycle, "unresolved", "Review incomplete, disputed, or at its round limit")


def accept_result(cycle, action, output, execution_id, input_manifest=None):
    """Seal one stage result. Callers first run validate_review_independence, which
    rejects every authoring execution of the review lineage and inherited context."""
    if action not in next_actions(cycle):
        raise ValueError("action is not pending")
    if not isinstance(execution_id, str) or not execution_id:
        raise ValueError("execution ID is required")
    all_results = list(cycle["results"].values())
    research_records = list(cycle.get("research", {}).values())
    for previous in cycle["previous_reviews"]:
        all_results.extend(previous["results"].values())
        research_records.extend(previous.get("research", {}).values())
    research_ids = {r["result"]["execution_id"] for r in research_records if r.get("result")}
    research_ids.update(r["requested_by"] for r in research_records)
    if execution_id in {entry["execution_id"] for entry in all_results} | research_ids:
        raise ValueError("execution ID already used")
    manifest = {} if input_manifest is None else copy.deepcopy(input_manifest)
    if not isinstance(manifest, dict):
        raise ValueError("input manifest must be an object")
    if manifest.get("proposal_digest", cycle["proposal_digest"]) != cycle["proposal_digest"]:
        raise ValueError("input manifest belongs to another proposal")
    if manifest.get("role_slot_id", action["slot"]) != action["slot"]:
        raise ValueError("input manifest has another role slot")
    replacement = cycle.get("replacement_actions", {}).get(slot_key(action))
    if action.get("replacement_for") is not None:
        if replacement is None or replacement.get("action") != action:
            raise ValueError("replacement action is not the recorded authorization")
        if manifest.get("replacement_for") != action["replacement_for"]:
            raise ValueError("replacement input manifest omits its continuity break")
        if manifest.get("grant_id") != replacement["grant_id"] or manifest.get("grant_sha256") != replacement["grant_sha256"]:
            raise ValueError("replacement input manifest has another authorization")
    origins = manifest.get("context_origin", [])
    origins = [origins] if isinstance(origins, str) else origins
    continued = manifest.get("continuation_of", [])
    continued = [continued] if isinstance(continued, str) else continued
    if action["stage"] == "judge":
        forbidden = {e["execution_id"] for e in all_results if e["action"]["stage"] in ("initial", "answer", "organize")}
        forbidden.update(r["result"]["execution_id"] for r in research_records if r.get("result"))
        if forbidden.intersection((origins or []) + (continued or [])):
            raise ValueError("judge cannot inherit initial-review or organizer context")
    execution_slots = {entry["execution_id"]: entry["action"]["slot"] for entry in all_results}
    if any(origin in execution_slots and execution_slots[origin] != action["slot"]
           for origin in (origins or []) + (continued or [])):
        raise ValueError("a logical slot cannot inherit another slot's conversation")
    for field in ("visible_execution_ids", "result_execution_ids"):
        if field in manifest:
            allowed = {cycle["results"][key]["execution_id"] for key in cycle["sealed"]}
            allowed.update(e["execution_id"] for p in cycle["previous_reviews"] for key, e in p["results"].items() if key in p["sealed"])
            allowed.update(r["result"]["execution_id"] for r in cycle.get("research", {}).values() if r.get("result") and
                           (r["action"]["slot"] == action["slot"] or slot_key(r["action"]) in cycle["sealed"]))
            allowed.update(r["result"]["execution_id"] for p in cycle["previous_reviews"] for r in p.get("research", {}).values()
                           if r.get("result") and (r["action"]["slot"] == action["slot"] or slot_key(r["action"]) in p["sealed"]))
            if set(manifest[field]) - allowed:
                raise ValueError("input contains unsealed peer results")
    stage = action["stage"]
    assessment = _validate_content(cycle, action, output)
    n = copy.deepcopy(cycle)
    if stage == "scope":
        n["scope_assessment"] = assessment
        n["reviewer_slots"] = [slot["id"] for slot in assessment["initial_slots"]]
        n["reviewers"] = len(n["reviewer_slots"])
        n["activity_execution_limit"] = assessment["activity_execution_limit"]
        n["required_source_refs"] = sorted({ref for slot in assessment["initial_slots"] for ref in slot["required_source_refs"]})
        n["phase"] = "initial"
        n["history"].append({"round": n["round"], "event": "scope_assessment_accepted",
                             "assessment_id": assessment["assessment_id"]})
    elif stage == "organize":
        _organize(n, output)
    elif stage == "answer":
        _answer(n, action, output)
    elif stage == "judge":
        _judge(n, output)
    key = slot_key(action)
    n["results"][key] = {"action": copy.deepcopy(action), "stage": stage,
        "output": copy.deepcopy(output), "execution_id": execution_id, "manifest": manifest,
        "proposal_digest": n["proposal_digest"]}
    if replacement is not None:
        n["blocked_actions"].pop(key, None)
        n["replacement_actions"].pop(key, None)
        n.setdefault("replacement_receipts", []).append({"action": copy.deepcopy(action),
            "recovery_event": action["replacement_for"], "grant_id": action["grant_id"],
            "grant_sha256": action["grant_sha256"], "execution_id": execution_id,
            "continuity_broken": True, "authorization": copy.deepcopy(replacement)})
    # The final assistant output belongs in its slot even if the caller never resends it.
    n = _append_turns(n, action["slot"], [{"role": "assistant", "content": copy.deepcopy(output),
                                         "message_id": f"{execution_id}:assistant"}])
    batch = [a for a in _phase_actions(cycle)]
    if all(slot_key(a) in n["results"] for a in batch):
        keys = [slot_key(a) for a in batch]
        n["sealed"].extend(keys)
        entries = [n["results"][k] for k in keys]
        n["history"].append({"round": cycle["round"], "stage": stage, "sealed": keys})
        if stage == "scope":
            pass
        elif stage == "initial":
            for entry in entries:
                _add_findings(n, entry["action"], entry["output"])
            if all(e["output"]["decision"] == "match" and e["output"]["scope_complete"] for e in entries):
                _finish(n, "match", "All required initial reviewers matched the complete proposal")
            elif any(not e["output"]["scope_complete"] for e in entries):
                _finish(n, "unresolved", "Required initial review scope remains incomplete")
            else:
                n["phase"] = "organize"
        elif stage == "answer":
            for entry in entries:
                for answer in entry["output"]["answers"]:
                    issue = n["issues"][answer["issue_id"]]
                    issue["answers"].append(copy.deepcopy(answer))
                    issue["answer"] = copy.deepcopy(entry)
                    issue["version"] += 1
                    issue["status"] = "withdrawn" if answer["disposition"] == "withdraw" else "open"
                _add_findings(n, entry["action"], entry["output"])
            # Answer findings already identify their reviewer and parent lineage;
            # linking them needs no new semantic organizer decision. This also
            # keeps each (stage, round, slot) unique within the finite cycle.
            for finding_key in n["pending_findings"]:
                source = n["findings"][finding_key]
                issue_id = f"answer-finding-{finding_key}"
                n["issues"][issue_id] = {"id": issue_id,
                    "finding_refs": [copy.deepcopy(source["ref"])],
                    "answer_role_slot_id": source["ref"]["slot"],
                    "parent_issue_ids": copy.deepcopy(source["finding"].get("parent_issue_ids", [])),
                    "version": 1, "status": "open", "answers": [], "verdicts": [],
                    "answer": None}
            n["pending_findings"] = []
            n["answer_requests"] = []
            n["phase"] = "judge"
        elif stage == "judge":
            _aggregate_judges(n, entries)
    return n


def record_turn(cycle, slot, messages):
    """Append immutable public messages; stable message IDs deduplicate resends."""
    _check_proposal(cycle)
    return _append_turns(copy.deepcopy(cycle), slot, messages)


def _append_turns(n, slot, messages):
    """Append in place to a checked cycle copy that the calling transition already owns."""
    if slot not in n["reviewer_slots"] + n["judge_slots"] + ["scope", "organize"]:
        raise ValueError("unknown logical slot")
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")
    turns = n["turns"].setdefault(slot, [])
    manifest = n["transcript_manifest"].setdefault(slot, [])
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in ("system", "user", "assistant", "tool") or "content" not in message:
            raise ValueError("invalid public transcript message")
        data = compact_json_bytes(message)
        message_id = message.get("message_id")
        if message_id is not None:
            existing = [i for i, entry in enumerate(turns) if entry.get("message_id") == message_id]
            if existing:
                if turns[existing[0]] != message:
                    raise ValueError("transcript message ID changed content")
                continue
        index = len(turns)
        turns.append(copy.deepcopy(message))
        manifest.append({"index": index, "sha256": hashlib.sha256(data).hexdigest(),
                         "bytes": len(data), "proposal_digest": n["proposal_digest"],
                         "ref": f"review-transcript:{n['review_lineage_id']}:{slot}:{index}"})
    return n


def record_recovery_event(cycle, action, event):
    """Record a restoration fact; activity ownership decides retry or replacement."""
    if action not in next_actions(cycle):
        raise ValueError("recovery event requires a pending review action")
    if not isinstance(event, dict) or not isinstance(event.get("reason"), str) or not event["reason"]:
        raise ValueError("recovery event requires a reason")
    if not isinstance(event.get("retryable"), bool) or not isinstance(event.get("preserved_range"), dict):
        raise ValueError("recovery event requires retryability and preserved range")
    n = copy.deepcopy(cycle)
    event_index = len(n.setdefault("recovery_events", []))
    entry = {**copy.deepcopy(event), "index": event_index, "action": copy.deepcopy(action), "reason": event["reason"], "retryable": event["retryable"],
             "preserved_range": copy.deepcopy(event["preserved_range"]),
             "expected_sha256": event.get("expected_sha256"), "observed_sha256": event.get("observed_sha256"),
             "continuity_broken": event.get('continuity_broken', not event["retryable"])}
    n["recovery_events"].append(entry)
    if not entry["retryable"]:
        if entry['continuity_broken']:
            n.setdefault("continuity_events", []).append({**copy.deepcopy(entry), "kind": "continuity_broken"})
        n.setdefault("followup", []).append({"reason": event['reason'], "action": copy.deepcopy(action),
                                               "recovery_event": event_index, "owner_activity_id": n.get("owner_activity_id")})
        # A damaged logical slot cannot silently become a new reviewer.  It is
        # held until a current authorization explicitly opens a replacement.
        n.setdefault("blocked_actions", {})[slot_key(action)] = event_index
        n.setdefault('replacement_actions', {}).pop(slot_key(action), None)
    return n


def authorize_record_replacement(cycle, action, instance, *, runtime, grant_id=None,
                                 delegation_id=None, case=None, at=None):
    """Authorize an exact failed slot through the current source-bound authority API."""
    from .governance import authorize_review_replacement
    from .repository import new_id
    expected = {key: action.get(key) for key in ('stage', 'slot', 'round')}
    if cycle['status'] != 'working' or expected not in _phase_actions(cycle):
        return {'disposition': 'invalid_action', 'cycle': cycle, 'reason': 'not a current working slot'}
    key = slot_key(expected)
    index = cycle.get('blocked_actions', {}).get(key)
    if index is None:
        return {'disposition': 'not_waiting_for_replacement', 'cycle': cycle}
    events = cycle.get('recovery_events', [])
    if type(index) is not int or not 0 <= index < len(events):
        return {'disposition': 'invalid_recovery_record', 'cycle': cycle}
    event = events[index]
    if event['retryable'] or any(event['action'].get(k) != v for k, v in expected.items()):
        return {'disposition': 'invalid_recovery_record', 'cycle': cycle}
    prior = cycle.get('replacement_actions', {}).get(key)
    request = {'id': prior['action']['id'] if prior else new_id('AC'),
               'role': 'identity_review', 'target': cycle.get('knowledge_id'),
               'review_cycle_id': cycle.get('id'), **expected,
               'actor_kind': 'ai', 'purpose': 'record_replacement',
               'replacement_for': index, 'continuity_break_cause': event['reason']}
    if grant_id is not None:
        request['grant_id'] = grant_id
    authority = authorize_review_replacement(instance, runtime, request,
                                             delegation_id=delegation_id, case=case, at=at)
    if not authority['allowed']:
        return {'disposition': 'authorization_denied', 'cycle': cycle, 'authority': authority,
                'reason': authority['reason'], 'recovery_event': copy.deepcopy(event)}
    if prior:
        return {'disposition': 'replacement_ready', 'cycle': cycle,
                'action': copy.deepcopy(prior['action']), 'authority': authority}
    n = copy.deepcopy(cycle)
    if not event.get('continuity_broken'):
        n.setdefault('continuity_events', []).append({'kind': 'continuity_broken', 'recovery_event': index,
            'action': copy.deepcopy(expected), 'grant_id': authority['grant_id'], 'reason': 'authorized record-based replacement'})
    replacement = {k: v for k, v in request.items() if k not in ('role', 'target', 'review_cycle_id')}
    replacement.update(grant_id=authority['grant_id'], grant_sha256=authority['grant_sha256'], continuity_broken=True)
    # Preserve the damaged original in the coordinator's record. Only messages
    # whose original hashes still verify may become replacement-visible input.
    slot = expected['slot']
    turns = n['turns'].get(slot, [])
    manifests = n['transcript_manifest'].get(slot, [])
    if not isinstance(turns, list) or not isinstance(manifests, list):
        return {'disposition': 'invalid_recovery_record', 'cycle': cycle,
                'reason': 'transcript containers cannot be reconstructed as ordered messages'}
    verified, omitted = _verified_transcript(turns, manifests)
    n.setdefault('transcript_replacements', []).append({
        'slot': slot, 'recovery_event': index, 'turns': copy.deepcopy(turns),
        'manifest': copy.deepcopy(manifests), 'omitted_indices': omitted})
    n['turns'][slot] = [message for message, _ in verified]
    n['transcript_manifest'][slot] = [dict(manifest, index=position) for position, (_, manifest) in enumerate(verified)]
    sealed_input = _replacement_sealed_input(cycle, [manifest for _, manifest in verified])
    n.setdefault('replacement_actions', {})[key] = {
        'action': replacement, 'recovery_event': index, 'grant_id': authority['grant_id'],
        'grant_sha256': authority['grant_sha256'], 'authority_request': request,
        'authority': copy.deepcopy(authority), 'delegation_id': delegation_id, 'case': copy.deepcopy(case),
        'sealed_input_sha256': json_digest(sealed_input), 'omitted_indices': omitted}
    n.setdefault('history', []).append({'event': 'replacement_authorized', 'action': expected,
                                       'recovery_event': index, 'grant_id': authority['grant_id']})
    return {'disposition': 'replacement_ready', 'cycle': n, 'action': copy.deepcopy(replacement),
            'authority': authority, 'recovery_event': copy.deepcopy(event)}


def validate_transcript(cycle, slot):
    """Shared exact-byte checker for live restoration and finished review replay."""
    turns = cycle["turns"].get(slot, [])
    manifests = cycle["transcript_manifest"].get(slot, [])
    if not isinstance(turns, list) or not isinstance(manifests, list):
        raise ReviewRestorationError('transcript restoration is incomplete', cause_kind='invalid_container', coordinate={'slot': slot})
    if len(turns) != len(manifests):
        raise ReviewRestorationError('transcript restoration is incomplete', cause_kind='missing_record',
            coordinate={'slot': slot, 'index': min(len(turns), len(manifests))})
    for position, (message, entry) in enumerate(zip(turns, manifests)):
        fault = _manifest_fault(message, entry, position)
        if fault == 'invalid_manifest':
            raise ReviewRestorationError('transcript restoration manifest is incomplete', cause_kind='invalid_manifest',
                coordinate={'slot': slot, 'index': position}, verified_indices=range(position))
        if fault == 'content_mismatch':
            raise ReviewRestorationError('transcript bytes changed', cause_kind='content_mismatch',
                coordinate={'slot': slot, 'index': position}, expected_sha256=entry['sha256'],
                observed_sha256=json_digest(message), verified_indices=range(position))
    return turns, manifests


def context_for(cycle, action):
    """Expose sealed earlier stages and this logical slot's complete public history."""
    if action not in next_actions(cycle):
        raise ValueError("action is not pending")
    messages, references = [], []
    slot = action['slot']
    turns, manifests = validate_transcript(cycle, slot)
    for message, entry in zip(turns, manifests):
        old_proposal = message.get("kind") == "proposal" and entry["proposal_digest"] != cycle["proposal_digest"]
        if message["role"] == "tool" or old_proposal or message.get('kind') == 'delivered_prompt':
            ref = {**copy.deepcopy(entry), "slot": slot, "role": message["role"], "kind": message.get("kind", "tool_result"),
                   "call": copy.deepcopy(message.get("call")), "arguments": copy.deepcopy(message.get("arguments"))}
            messages.append({"role": message["role"], "content": {"source_ref": ref}})
            references.append(ref)
        else:
            messages.append(copy.deepcopy(message))
    visible = {key: copy.deepcopy(cycle["results"][key]) for key in cycle["sealed"]}
    supplemental = [copy.deepcopy(r) for r in cycle.get("research", {}).values()
                    if r.get("result") and (r["action"]["slot"] == slot or slot_key(r["action"]) in cycle["sealed"])]
    for previous in cycle["previous_reviews"]:
        supplemental.extend({**copy.deepcopy(r), "previous_revision": previous["revision"]}
                            for r in previous.get("research", {}).values() if r.get("result") and
                            (r["action"]["slot"] == slot or slot_key(r["action"]) in previous["sealed"]))
    scope_slot = next((entry for entry in (cycle.get("scope_assessment") or {}).get("initial_slots", []) if entry["id"] == slot), None)
    replacement = copy.deepcopy(cycle.get("replacement_actions", {}).get(slot_key(action)))
    return {"proposal": copy.deepcopy(cycle["proposal"]), "proposal_digest": cycle["proposal_digest"],
        **{key: copy.deepcopy(cycle[key]) for key in ('identity_basis', 'policy_ref') if key in cycle},
        "action": copy.deepcopy(action), "reviewer_slots": list(cycle["reviewer_slots"]),
        "review_policy": copy.deepcopy(cycle.get("review_policy")), "scope_assessment": copy.deepcopy(cycle.get("scope_assessment")),
        "owner_activity_id": cycle.get("owner_activity_id"), "activity_execution_limit": cycle.get("activity_execution_limit"),
        "scope_executions_used": len(cycle['execution_accounting']['executions_used']),
        "minimum_scope_execution_limit": minimum_scope_executions(
            max(cycle['review_policy']['minimum_initial_slots'], len(cycle['retained_reviewer_slots'])),
            cycle['max_rounds'], len(cycle['execution_accounting']['executions_used'])),
        "required_source_refs": ["proposal"] if action["stage"] == "scope" else list(scope_slot["required_source_refs"] if scope_slot else []),
        "slot_perspective": "scope" if action["stage"] == "scope" else (scope_slot or {}).get("perspective"),
        "replacement": replacement,
        "self_messages": messages, "source_refs": references,
        "issues": copy.deepcopy(cycle["issues"]), "completed_results": visible,
        "supplemental_results": supplemental,
        "pending_findings": [copy.deepcopy(cycle["findings"][k]) for k in cycle["pending_findings"]],
        "answer_requests": [i for i in cycle["answer_requests"] if cycle["issues"][i]["answer_role_slot_id"] == slot],
        "previous_reviews": [{**{k: copy.deepcopy(p[k]) for k in ("revision", "proposal_digest", "issues", "decision")},
                              "completed_results": {key: copy.deepcopy(p["results"][key]) for key in p["sealed"]}}
                             for p in cycle["previous_reviews"]],
        "output_schema": stage_schema(action["stage"])}
