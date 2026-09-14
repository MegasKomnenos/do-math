"""Deterministic, JSON-serializable orchestration of independent identity review.

The caller owns execution budgets, source storage, and model execution. This module
checks provenance and completeness; mathematical claims remain the reviewers'.
"""
from __future__ import annotations

import copy
import hashlib
import json


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _array(items):
    return {"type": "array", "items": items}


def stage_schema(stage):
    """The same schema is supplied to producers and checked before acceptance."""
    string = {"type": "string", "minLength": 1}
    evidence = _array(string)
    finding = _object({"id": string, "statement": string, "evidence": evidence})
    common = {"proposal_digest": string, "summary": string, "used_sources": evidence,
              "questions": evidence}
    if stage in ("initial", "judge"):
        common.update(decision={"enum": ["match", "mismatch", "unresolved"]},
                      scope_complete={"type": "boolean"})
    if stage == "initial":
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


def _validate(value, schema, path="output"):
    kind = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    if kind and (not isinstance(value, types[kind]) or (kind == "integer" and isinstance(value, bool))):
        raise ValueError(f"{path}: expected {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: invalid value")
    if kind == "object":
        if set(schema["required"]) - value.keys():
            raise ValueError(f"{path}: missing required fields")
        if schema.get("additionalProperties") is False and value.keys() - schema["properties"].keys():
            raise ValueError(f"{path}: unknown fields")
        for key, child in value.items():
            _validate(child, schema["properties"][key], f"{path}.{key}")
    elif kind == "array":
        for i, child in enumerate(value):
            _validate(child, schema["items"], f"{path}[{i}]")
    elif kind == "string" and len(value.strip()) < schema.get("minLength", 0):
        raise ValueError(f"{path}: empty string")
    elif kind == "integer" and value < schema.get("minimum", value):
        raise ValueError(f"{path}: below minimum")


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


def start_review(proposal, reviewers, judges=3, max_rounds=3, previous=None):
    if not isinstance(proposal, dict) or proposal.get("revision") is None:
        raise ValueError("proposal requires an exact revision")
    reviewer_slots, judge_slots = _slots(reviewers, "initial"), _slots(judges, "judge")
    if len(judge_slots) != 3 or isinstance(max_rounds, bool) or not isinstance(max_rounds, int) or max_rounds < 1:
        raise ValueError("exactly three judges and a positive round limit are required")
    _unique(reviewer_slots + judge_slots + ["organize"], "role slot")
    digest = _digest(proposal)
    previous_reviews, turns, manifests = [], {}, {}
    lineage = proposal.get("review_lineage_id", digest)
    if previous is not None:
        _check_proposal(previous)
        if proposal["revision"] == previous["revision"]:
            raise ValueError("new review requires a new proposal revision")
        if not set(previous["reviewer_slots"]).issubset(reviewer_slots) or judge_slots != previous["judge_slots"]:
            raise ValueError("existing logical slots must be retained")
        if proposal.get("review_lineage_id", previous["review_lineage_id"]) != previous["review_lineage_id"]:
            raise ValueError("proposal changes the inherited review lineage")
        lineage = previous["review_lineage_id"]
        turns = copy.deepcopy(previous["turns"])
        manifests = copy.deepcopy(previous["transcript_manifest"])
        previous_reviews = copy.deepcopy(previous["previous_reviews"])
        previous_reviews.append({k: copy.deepcopy(previous[k]) for k in
            ("revision", "proposal_digest", "proposal", "results", "sealed", "issues", "status", "decision")})
        previous_reviews[-1]["research"] = copy.deepcopy(previous.get("research", {}))
    return {"proposal": copy.deepcopy(proposal), "proposal_digest": digest,
        "revision": proposal["revision"], "review_lineage_id": lineage,
        "reviewers": len(reviewer_slots), "judges": 3, "reviewer_slots": reviewer_slots,
        "judge_slots": judge_slots, "max_rounds": max_rounds, "round": 1,
        "phase": "initial", "status": "working", "decision": None,
        "results": {}, "sealed": [], "turns": turns, "transcript_manifest": manifests,
        "issues": {}, "findings": {}, "pending_findings": [], "answer_requests": [],
        "history": [], "previous_reviews": previous_reviews, "followup": [],
        "deferred_actions": {}, "research": {}}


def _check_proposal(cycle):
    if _digest(cycle["proposal"]) != cycle["proposal_digest"] or cycle["revision"] != cycle["proposal"]["revision"]:
        raise ValueError("sealed proposal changed")


def _key(action):
    return f"{action['stage']}:{action['round']}:{action['slot']}"


def _phase_actions(cycle):
    stage = cycle["phase"]
    if stage == "initial":
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
    if cycle["status"] != "working":
        return []
    return [a for a in _phase_actions(cycle) if _key(a) not in cycle["results"]
            and _key(a) not in cycle.get("deferred_actions", {})]


def research_schema():
    text = {"type": "string", "minLength": 1}
    return _object({"summary": copy.deepcopy(text), "used_sources": _array(copy.deepcopy(text)),
        "questions": _array(copy.deepcopy(text)), "research_request_id": copy.deepcopy(text),
        "request_digest": copy.deepcopy(text), "outcome": {"enum": ["answered", "unresolved"]},
        "answer": copy.deepcopy(text), "scope_complete": {"type": "boolean"},
        "evidence_refs": _array(copy.deepcopy(text))})


def defer_for_research(cycle, action, output, requests, execution_id, *, limit=3, budget_available=True):
    """Preserve a provisional response without turning it into a sealed verdict."""
    if action not in next_actions(cycle): raise ValueError("review action is not pending")
    _validate(output, stage_schema(action["stage"]))
    if output["proposal_digest"] != cycle["proposal_digest"]: raise ValueError("another proposal")
    if action["stage"] in ("initial", "judge") and output["decision"] != "unresolved":
        raise ValueError("a review requesting investigation must return unresolved provisionally")
    if not isinstance(requests, list) or not requests: raise ValueError("research requests must be a nonempty list")
    spec = _object({"id": {"type": "string", "minLength": 1}, "question": {"type": "string", "minLength": 1},
                    "source_refs": _array({"type": "string", "minLength": 1})})
    for request in requests:
        _validate(request, spec, "research_request")
        if not request["source_refs"]: raise ValueError("fixed investigation requires exact source references")
        _unique(request["source_refs"], "research source")
    _unique([r["id"] for r in requests], "research request ID")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0: raise ValueError("invalid research limit")
    used = {entry["execution_id"] for entry in cycle["results"].values()}
    used.update(r["requested_by"] for r in cycle.get("research", {}).values())
    used.update(r["result"]["execution_id"] for r in cycle.get("research", {}).values() if r.get("result"))
    if not isinstance(execution_id, str) or not execution_id or execution_id in used:
        raise ValueError("research request requires a fresh review execution")
    n = copy.deepcopy(cycle)
    n = record_turn(n, action["slot"], [{"role": "assistant", "message_id": f"{execution_id}:assistant",
                                        "content": {"provisional_result": output, "research_requests": requests}}])
    if len(n.get("research", {})) + len(requests) > limit or not budget_available:
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
        n["research"][identifier] = {"id": identifier, **copy.deepcopy(payload), "request_digest": _digest(payload),
            "action": copy.deepcopy(action), "requested_by": execution_id, "status": "pending", "result": None}
        identifiers.append(identifier)
    n.setdefault("deferred_actions", {})[_key(action)] = identifiers
    n["history"].append({"event": "review_deferred_for_research", "action": copy.deepcopy(action), "request_ids": identifiers})
    return n


def accept_research_result(cycle, request_id, output, execution_id, source_records=None, *, execution_status="completed"):
    _check_proposal(cycle)
    request = cycle.get("research", {}).get(request_id)
    if cycle["status"] != "working" or not request or request["status"] != "pending":
        raise ValueError("investigation is not pending")
    _validate(output, research_schema())
    if execution_status not in {"completed", "incomplete"} or (execution_status == "incomplete" and output["outcome"] != "unresolved"):
        raise ValueError("an incomplete investigation cannot supply an answered result")
    if output["research_request_id"] != request_id or output["request_digest"] != request["request_digest"]:
        raise ValueError("investigation result belongs to a different fixed question")
    if output["outcome"] == "answered" and (not output["scope_complete"] or not output["evidence_refs"] or output["questions"]):
        raise ValueError("answered investigation requires complete scope and exact evidence")
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
    n = record_turn(n, request["action"]["slot"], [{"role": "tool", "kind": "supplemental_research",
        "message_id": f"{execution_id}:research-result", "call": "supplemental_research",
        "arguments": {"research_request_id": request_id, "request_digest": request["request_digest"]},
        "content": copy.deepcopy(entry)}])
    key = _key(request["action"])
    if all(n["research"][rid]["status"] != "pending" for rid in n["deferred_actions"][key]):
        del n["deferred_actions"][key]
    return n


def _add_findings(cycle, action, output):
    findings = output.get("findings", output.get("new_findings", []))
    for finding in findings:
        ref = dict(action, id=finding["id"])
        key = _digest(ref)
        cycle["findings"][key] = {"ref": ref, "finding": copy.deepcopy(finding)}
        cycle["pending_findings"].append(key)
    # Questions and uncompleted scope must remain explicit input to organization.
    questions = list(output.get("questions", []))
    if action["stage"] == "initial" and (not output["scope_complete"] or output["decision"] == "unresolved"):
        questions.append("Required initial review scope or judgment remains unresolved.")
    for i, question in enumerate(questions):
        ref = dict(action, id=f"__question_{i}")
        key = _digest(ref)
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
        keys = [_digest(ref) for ref in refs]
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


def _aggregate_judges(cycle, entries):
    retry = []
    for issue_id, issue in cycle["issues"].items():
        votes = [next(v for v in entry["output"]["issue_verdicts"] if v["issue_id"] == issue_id) for entry in entries]
        decisions = {v["decision"] for v in votes}
        status = next(iter(decisions)) if len(decisions) == 1 else "unresolved"
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
    if len(decisions) == 1 and "unresolved" not in decisions and complete and not cycle["pending_findings"] and not unresolved_issues:
        _finish(cycle, next(iter(decisions)), "All three independent final judgments sealed")
    else:
        _finish(cycle, "unresolved", "Review incomplete, disputed, or at its round limit")


def accept_result(cycle, action, output, execution_id, input_manifest=None):
    if action not in next_actions(cycle):
        raise ValueError("action is not pending")
    _validate(output, stage_schema(action["stage"]))
    if output["proposal_digest"] != cycle["proposal_digest"]:
        raise ValueError("result belongs to another proposal")
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
    producers = set(cycle["proposal"].get("producer_execution_ids", []))
    for previous in cycle["previous_reviews"]:
        producers.update(previous["proposal"].get("producer_execution_ids", []))
    if execution_id in producers:
        raise ValueError("author execution cannot review")
    manifest = copy.deepcopy(input_manifest or {})
    if not isinstance(manifest, dict):
        raise ValueError("input manifest must be an object")
    if manifest.get("proposal_digest", cycle["proposal_digest"]) != cycle["proposal_digest"]:
        raise ValueError("input manifest belongs to another proposal")
    if manifest.get("role_slot_id", action["slot"]) != action["slot"]:
        raise ValueError("input manifest has another role slot")
    origins = manifest.get("context_origin", [])
    origins = [origins] if isinstance(origins, str) else origins
    continued = manifest.get("continuation_of", [])
    continued = [continued] if isinstance(continued, str) else continued
    if producers.intersection((origins or []) + (continued or [])):
        raise ValueError("author context cannot be inherited by a reviewer")
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
                           (r["action"]["slot"] == action["slot"] or _key(r["action"]) in cycle["sealed"]))
            allowed.update(r["result"]["execution_id"] for p in cycle["previous_reviews"] for r in p.get("research", {}).values()
                           if r.get("result") and (r["action"]["slot"] == action["slot"] or _key(r["action"]) in p["sealed"]))
            if set(manifest[field]) - allowed:
                raise ValueError("input contains unsealed peer results")
    stage = action["stage"]
    if stage in ("initial", "judge") and output["decision"] == "match" and not output["scope_complete"]:
        raise ValueError("match requires complete scope")
    findings = output.get("findings", output.get("new_findings", []))
    _unique([f["id"] for f in findings], "finding ID")
    if any(f["id"].startswith("__question_") or not f["evidence"] for f in findings):
        raise ValueError("finding requires evidence and a nonreserved ID")
    if stage == "initial":
        if output["decision"] == "match" and (findings or output["questions"]):
            raise ValueError("match requires no open findings or questions")
        if output["decision"] == "mismatch" and not findings:
            raise ValueError("mismatch requires findings")
    n = copy.deepcopy(cycle)
    if stage == "organize":
        _organize(n, output)
    elif stage == "answer":
        _answer(n, action, output)
    elif stage == "judge":
        _judge(n, output)
    key = _key(action)
    n["results"][key] = {"action": copy.deepcopy(action), "stage": stage,
        "output": copy.deepcopy(output), "execution_id": execution_id, "manifest": manifest,
        "proposal_digest": n["proposal_digest"]}
    # The final assistant output belongs in its slot even if the caller never resends it.
    n = record_turn(n, action["slot"], [{"role": "assistant", "content": copy.deepcopy(output),
                                       "message_id": f"{execution_id}:assistant"}])
    batch = [a for a in _phase_actions(cycle)]
    if all(_key(a) in n["results"] for a in batch):
        keys = [_key(a) for a in batch]
        n["sealed"].extend(keys)
        entries = [n["results"][k] for k in keys]
        n["history"].append({"round": cycle["round"], "stage": stage, "sealed": keys})
        if stage == "initial":
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
    if slot not in cycle["reviewer_slots"] + cycle["judge_slots"] + ["organize"]:
        raise ValueError("unknown logical slot")
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")
    n = copy.deepcopy(cycle)
    turns = n["turns"].setdefault(slot, [])
    manifest = n["transcript_manifest"].setdefault(slot, [])
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in ("system", "user", "assistant", "tool") or "content" not in message:
            raise ValueError("invalid public transcript message")
        data = _bytes(message)
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


def context_for(cycle, action):
    """Expose sealed earlier stages and this logical slot's complete public history."""
    if action not in next_actions(cycle):
        raise ValueError("action is not pending")
    messages, references = [], []
    slot = action["slot"]
    turns = cycle["turns"].get(slot, [])
    manifests = cycle["transcript_manifest"].get(slot, [])
    if len(turns) != len(manifests):
        raise ValueError("transcript restoration is incomplete")
    for message, entry in zip(turns, manifests):
        if _digest(message) != entry["sha256"]:
            raise ValueError("transcript bytes changed")
        old_proposal = message.get("kind") == "proposal" and entry["proposal_digest"] != cycle["proposal_digest"]
        if message["role"] == "tool" or old_proposal:
            ref = {**copy.deepcopy(entry), "slot": slot, "role": message["role"], "kind": message.get("kind", "tool_result"),
                   "call": copy.deepcopy(message.get("call")), "arguments": copy.deepcopy(message.get("arguments"))}
            messages.append({"role": message["role"], "content": {"source_ref": ref}})
            references.append(ref)
        else:
            messages.append(copy.deepcopy(message))
    visible = {key: copy.deepcopy(cycle["results"][key]) for key in cycle["sealed"]}
    supplemental = [copy.deepcopy(r) for r in cycle.get("research", {}).values()
                    if r.get("result") and (r["action"]["slot"] == slot or _key(r["action"]) in cycle["sealed"])]
    for previous in cycle["previous_reviews"]:
        supplemental.extend({**copy.deepcopy(r), "previous_revision": previous["revision"]}
                            for r in previous.get("research", {}).values() if r.get("result") and
                            (r["action"]["slot"] == slot or _key(r["action"]) in previous["sealed"]))
    return {"proposal": copy.deepcopy(cycle["proposal"]), "proposal_digest": cycle["proposal_digest"],
        "action": copy.deepcopy(action), "self_messages": messages, "source_refs": references,
        "issues": copy.deepcopy(cycle["issues"]), "completed_results": visible,
        "supplemental_results": supplemental,
        "pending_findings": [copy.deepcopy(cycle["findings"][k]) for k in cycle["pending_findings"]],
        "answer_requests": [i for i in cycle["answer_requests"] if cycle["issues"][i]["answer_role_slot_id"] == slot],
        "previous_reviews": [{**{k: copy.deepcopy(p[k]) for k in ("revision", "proposal_digest", "issues", "decision")},
                              "completed_results": {key: copy.deepcopy(p["results"][key]) for key in p["sealed"]}}
                             for p in cycle["previous_reviews"]],
        "output_schema": stage_schema(action["stage"])}
