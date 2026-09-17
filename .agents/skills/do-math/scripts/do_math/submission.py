"""Shared, read-only submission checks over the producer's fixed visible input.

These checks do not apply state, run Lean, contact a service, or certify meaning.
The receiving engine separately rechecks current authority and dependencies.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import jsonschema

from . import knowledge_io, planning, review_cycle
from .context_store import collect_outputs, materialize_inputs, _safe_path, _excluded
from .external import prepare_operation, validate_operation
from .model_policy import ASSESSMENT_SCHEMA, assessment_key, validate_assessments
from .observations import read_checkpoint, validate_rules, CHECKPOINT_MAX_BYTES, RULES_MAX_BYTES
from .repository import canonical_json, _unique_pairs, _reject_constant


TEXT = {"type": "string", "minLength": 1, "pattern": r"\S"}
STRINGS = {"type": "array", "items": TEXT, "uniqueItems": True}
PRODUCERS = {"research_work", "supplemental_research"}
PLANNERS = {"research_preparation", "research_plan"}
EXTENSION_ROLES = {
    "task_conditions": {"research_preparation"}, "task_dispositions": PLANNERS,
    "research_insights": {"research_preparation", "research_plan", "research_work",
        "supplemental_research", "identity_review", "task_contract_review", "goal_audit",
        "operational_review", "intent_interpretation", "maintenance"},
    "external_requests": PRODUCERS, "knowledge_changes": {*PRODUCERS, "research_preparation"},
    "knowledge_metadata": PRODUCERS, "relations": PRODUCERS, "observation_rules": PRODUCERS,
    "research_requests": {"identity_review"}, "academic_resolutions": {"research_plan"},
    "model_assessments": PLANNERS, "model_assessment_deferrals": {"research_preparation"}, "queued_requests": {"research_plan"},
}


def _object(properties, required=None):
    return {"type": "object", "properties": properties, "additionalProperties": False,
            "required": list(properties) if required is None else required}


def extension_schema(action: dict, definitions: dict) -> dict:
    """The installed schema describes only families available to this role."""
    kind = {"type": "string", "enum": [d["token"] for d in definitions.get("knowledge", [])]}
    claim = _object({"kind": TEXT, "source": TEXT, "target": TEXT, "confirmed_scope": TEXT})
    relation = _object({"id": TEXT, "kind": TEXT, "source": TEXT, "target": TEXT, "evidence": TEXT,
        "evidence_refs": STRINGS, "formal_result_refs": STRINGS, "assessment_refs": STRINGS,
        "confirmed_scope": TEXT}, ["kind", "source", "target"])
    shapes = {
        "task_conditions": _object({"task_id": TEXT, "task_title": TEXT, "dependencies": STRINGS,
            "occurrence_condition": {"type": "object"}, "observation_rules": {"type": "array"}}, []),
        "task_dispositions": _object({"task_id": TEXT, "disposition": {"const": "withdraw"}, "reason": TEXT}),
        "research_insights": _object({"kind": kind, "title": TEXT, "statement": TEXT, "summary": TEXT,
            "explanation": TEXT, "information_state": TEXT, "evidence_ids": STRINGS},
            ["kind", "title", "statement", "summary"]),
        "external_requests": _object({"id": TEXT, "request": {"type": "object"}, "grant_id": {"type": ["string", "null"]},
            "purpose": TEXT, "academic_effect_id": TEXT}, ["request", "purpose"]),
        "knowledge_changes": _object({"id": TEXT, "changes": {"type": "object", "minProperties": 1}, "reason": TEXT}),
        "knowledge_metadata": _object({"title": TEXT, "relation_claim": claim, "confirmed_scope": TEXT,
            "epistemic_status": TEXT, "selection_relevance": TEXT, "uncertainty_assessment": {}}, ["title"]),
        "relations": relation,
        "observation_rules": {"type": "object"},
        "research_requests": _object({"id": TEXT, "question": TEXT, "source_refs": {**STRINGS, "minItems": 1}}),
        "academic_resolutions": _object({"id": TEXT, "decision": {"enum": ["resolved", "unresolved"]}, "evidence": TEXT}),
        "model_assessments": _object({assessment_key(action): TEXT,
            **ASSESSMENT_SCHEMA["properties"]}),
        "model_assessment_deferrals": _object({"task_id": TEXT, "reason": TEXT}),
        "queued_requests": _object({"request_id": TEXT, "decision": {"enum": ["keep", "cancel"]}, "reason": TEXT}),
    }
    allowed = {name for name, roles in EXTENSION_ROLES.items() if action["role"] in roles}
    if "assessment_targets" in action:
        allowed &= {"model_assessments", "model_assessment_deferrals"}
    else:
        allowed.discard("model_assessment_deferrals")
    if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
        allowed.clear()
    if not action.get("review_cycle_id"):
        allowed.discard("research_requests")
    return _object({name: {"type": "array", "items": shapes[name]} for name in sorted(allowed)}, [])


def load_json(raw: bytes):
    value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    canonical_json(value)
    return value


def read_extensions(workspace: Path) -> dict:
    path = _safe_path(workspace, "activity-extensions.json")
    value = load_json(path.read_bytes()) if path.exists() else {}
    if isinstance(value, dict):
        return {key: items for key, items in value.items() if items != [] or key not in EXTENSION_ROLES}
    return value


def reported_references(output: dict, extensions: dict, context: dict | None = None) -> list[str]:
    """Read explicit dependency fields, never historical records or free prose."""
    refs = list(output.get("used_sources", []))
    for item in output.get("knowledge", []):
        refs.extend(item.get("dependencies", []))
    for candidate in output.get("candidates", []):
        refs.extend([*candidate.get("inputs", []), *candidate.get("reuse", [])])
    for relation in [*output.get("relations", []), *extensions.get("relations", [])]:
        refs.extend([relation.get("source"), relation.get("target"),
                     *relation.get("evidence_refs", []), *relation.get("formal_result_refs", [])])
    for entry in extensions.get("research_insights", []):
        refs.extend(entry.get("evidence_ids", []))
    for entry in extensions.get("knowledge_changes", []):
        refs.append(entry.get("id"))
        refs.extend(entry.get("changes", {}).get("dependencies", []))
        refs.extend(entry.get("changes", {}).get("source_refs", []))
    for entry in extensions.get("knowledge_metadata", []):
        claim = entry.get("relation_claim", {})
        refs.extend([claim.get("source"), claim.get("target")])
    for entry in extensions.get("research_requests", []):
        refs.extend(entry.get("source_refs", []))
    aliases = {}
    if context:
        aliases.update({row["path"]: row["id"] for row in context.get("knowledge_catalog", [])})
        aliases.update({row["local_path"]: row["name"] for row in context.get("sources", [])})
    # A supplied input file keeps its record identity when cited as workspace:<path>.
    return list(dict.fromkeys(aliases.get(ref.removeprefix("workspace:"), ref) for ref in refs if isinstance(ref, str)))


def _issue(path, message):
    return {"path": path, "message": message}


def _schema_issues(value, schema, path):
    return [_issue(path + "".join("/" + str(part) for part in error.absolute_path), error.message)
            for error in jsonschema.Draft202012Validator(schema).iter_errors(value)]


def _reference_ids(context):
    ids = {row["id"] for row in context.get("knowledge_catalog", [])}
    ids.update(row["id"] for row in context.get("tasks", []))
    ids.update(row["id"] for row in context.get("sources", []) if row.get("id"))
    for source in context.get("sources", []):
        ids.update((source["name"], source["path"], "source:" + source["name"]))
    ids.update(row["id"] for row in context.get("grants", []))
    for key in ("user_inputs", "events", "external_operations", "external_rejections"):
        ids.update(row["id"] for row in context.get(key, []) if row.get("id"))
    for key in ("recent_history", "preparation_history"):
        ids.update(row["execution_id"] for row in context.get(key, []) if row.get("execution_id"))
    for task in context.get("tasks", []):
        ids.update(row["execution_id"] for row in task.get("results", []) if row.get("execution_id"))
    for key in ("task", "user_request", "execution_to_review", "previous_execution"):
        if isinstance(context.get(key), dict) and context[key].get("id"):
            ids.add(context[key]["id"])
    return ids


def validate_reference(reference: str, context: dict, workspace: Path) -> None:
    """A reference must identify supplied material or an output that is kept."""
    if reference in _reference_ids(context) | set(context.get("available_input_refs", [])) | {"context:goal", "context:policy"}:
        return
    proposal = context.get("proposal") or context.get("role_review", {}).get("proposal")
    if reference == "proposal" and proposal is not None:
        return
    if reference.startswith("proposal:") and proposal is not None:
        value = proposal
        for token in reference.removeprefix("proposal:").replace("/", ".").strip(".").split("."):
            if not isinstance(value, dict) or token not in value:
                raise ValueError("unknown proposal source coordinate: " + reference)
            value = value[token]
        return
    if reference.startswith("issue:") and reference.removeprefix("issue:") in context.get("role_review", {}).get("issues", {}):
        return
    locators = set()
    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"path", "local_path", "artifact_ref", "ref", "source_ref"} and isinstance(child, str):
                    locators.add(child)
                elif isinstance(child, (dict, list)):
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    # Historical artifact locators identify their original bytes, not the
    # newest knowledge revision with a similar ID.
    collect(context)
    for source in context.get("sources", []):
        locators.update((source["name"], "source:" + source["name"]))
    if reference in locators:
        return
    name = reference.removeprefix("workspace:")
    path = _safe_path(workspace, name)
    relative = Path(name)
    if (relative.parts[0] != "input" and _excluded(relative)) or not path.is_file():
        raise ValueError("reference must identify supplied input or a preserved workspace file: " + reference)


def validate_research_reference(reference: str, context: dict, workspace: Path) -> None:
    from .input_basis import aliases
    supplied = {row["id"] for row in context.get("knowledge_catalog", [])}
    for source in context.get("sources", []):
        supplied.update(aliases(source))
    supplied.update(row["ref"] for row in context.get("role_review", {}).get("source_refs", []))
    if reference in supplied:
        return
    if reference == "proposal" or reference.startswith(("proposal:", "issue:")):
        validate_reference(reference, context, workspace)
        return
    raise ValueError("research source must be a proposal coordinate, public issue, supplied source or knowledge ID: " + reference)


def payload_issues(output: dict, schema: dict, context: dict, extensions: dict, workspace: Path) -> list[dict]:
    """Check producer-visible conditions; application-time state stays separate."""
    issues = _schema_issues(output, schema, "output")
    action = context["action"]
    extension_errors = _schema_issues(extensions, extension_schema(action, context.get("kind_definitions", {})), "activity-extensions.json")
    if issues or extension_errors:
        return issues + extension_errors

    def check(path, operation):
        try:
            operation()
        except (ValueError, TypeError, KeyError, OSError) as error:
            issues.append(_issue(path, str(error)))

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    known = _reference_ids(context)
    knowledge_ids = {row["id"] for row in context.get("knowledge_catalog", [])}
    tasks = {row["id"]: row for row in context.get("tasks", [])}
    if isinstance(context.get("task"), dict):
        tasks[context["task"]["id"]] = context["task"]
    available = {*context.get("available_input_refs", []), *known}
    new_knowledge = {item["title"] for item in output.get("knowledge", [])}
    new_tasks = {item["title"] for item in output.get("candidates", [])}
    if not (action["role"] == "supplemental_research" and action.get("review_cycle_id")):
        for index, ref in enumerate(output.get("used_sources", [])):
            check(f"output/used_sources/{index}", lambda ref=ref: validate_reference(ref, context, workspace))
    for label, rows in (("knowledge", output.get("knowledge", [])), ("candidates", output.get("candidates", []))):
        check("output/" + label, lambda rows=rows: require(len({x["title"] for x in rows}) == len(rows), "titles must be unique within one output"))

    if action["role"] == "research_preparation":
        for index, item in enumerate(output["candidates"]):
            def candidate(item=item):
                require(all(item[key].strip() for key in ("title", "question", "scope", "expected_result")), "task text fields must be nonempty")
                criteria = item["completion_criteria"]
                require(bool(criteria) and all(c.strip() for c in criteria) and len(criteria) == len(set(criteria)), "completion criteria must be nonempty and distinct")
                missing = {r for r in [*item["inputs"], *item["reuse"]] if r not in available | new_tasks and not r.startswith("source:")}
                require(not missing, "unknown task inputs: " + ", ".join(sorted(missing)))
                if item["revises_task_id"]:
                    old = tasks.get(item["revises_task_id"])
                    require(bool(old) and old.get("status") not in {"completed", "closed", "performing"}, "revision requires an existing unfinished task")
                    require(not old.get("academic_requirement_id"), "user academic requirements have a separate decision path")
            check(f"output/candidates/{index}", candidate)
    if action["role"] == "research_plan":
        check("output", lambda: planning.validate_plan_submission(output, tasks, context.get("ready_task_ids", [])))
    if action["role"] in PRODUCERS and not action.get("review_cycle_id"):
        check("output/report", lambda: require(bool(output["report"].strip()), "report must state the actual scope and outcome"))
        for index, item in enumerate(output["knowledge"]):
            def candidate(item=item):
                require(all(item[key].strip() for key in ("title", "statement", "explanation", "summary")), "knowledge text fields must be nonempty")
                require(item["title"] not in knowledge_ids, "a new title cannot collide with an existing knowledge ID")
                refs = item["dependencies"]
                require(len(refs) == len(set(refs)) and not set(refs) - knowledge_ids - new_knowledge, "knowledge dependencies must name provided knowledge or unique new titles")
                require(item["title"] not in refs, "knowledge cannot depend on itself")
                declarations = item["declaration_names"]
                require(len(declarations) == len(set(declarations)), "declaration names must be distinct")
                require(not item["lean_code"] or bool(declarations), "Lean proposal requires declaration_names")
            check(f"output/knowledge/{index}", candidate)

    for index, insight in enumerate(extensions.get("research_insights", [])):
        check(f"activity-extensions.json/research_insights/{index}/evidence_ids", lambda insight=insight:
              require(not set(insight.get("evidence_ids", [])) - known, "insight evidence must name existing input records"))
    metadata = extensions.get("knowledge_metadata", [])
    check("activity-extensions.json/knowledge_metadata", lambda: require(
        len({x["title"] for x in metadata}) == len(metadata) and not {x["title"] for x in metadata} - new_knowledge,
        "metadata titles must be distinct and name new knowledge in this output"))
    for index, entry in enumerate(metadata):
        if "relation_claim" in entry:
            claim = entry["relation_claim"]
            check(f"activity-extensions.json/knowledge_metadata/{index}/relation_claim", lambda claim=claim: require(
                {claim["source"], claim["target"]} <= knowledge_ids and claim["kind"] in {d["token"] for d in context["kind_definitions"]["relations"]},
                "relation claim requires a registered relation kind and existing knowledge endpoints"))
    for index, entry in enumerate(extensions.get("knowledge_changes", [])):
        check(f"activity-extensions.json/knowledge_changes/{index}", lambda entry=entry: require(
            entry["id"] in knowledge_ids, "knowledge revision requires an existing input record"))
        from .knowledge import validate_changes
        check(f"activity-extensions.json/knowledge_changes/{index}/changes", lambda entry=entry: validate_changes(entry["changes"]))
        if "dependencies" in entry["changes"]:
            check(f"activity-extensions.json/knowledge_changes/{index}/changes/dependencies", lambda entry=entry: require(
                isinstance(entry["changes"]["dependencies"], list) and
                set(entry["changes"]["dependencies"]) <= knowledge_ids - {entry["id"]}, "revision dependencies must name other provided knowledge"))
        if "kind" in entry["changes"]:
            check(f"activity-extensions.json/knowledge_changes/{index}/changes/kind", lambda entry=entry: require(
                entry["changes"]["kind"] in {d["token"] for d in context["kind_definitions"]["knowledge"]}, "revision kind must be registered"))
    for name in ("observation_rules",):
        if name in extensions:
            check("activity-extensions.json/" + name, lambda: validate_rules(extensions[name]))
            check("activity-extensions.json/" + name, lambda: require(action.get("target") in tasks, "persisted rules require the assigned task"))
    conditions = extensions.get("task_conditions", [])
    targeted = []
    for index, entry in enumerate(conditions):
        key = entry.get("task_title", entry.get("task_id"))
        targeted.append(key)
        targets = new_tasks | {x["revises_task_id"] for x in output.get("candidates", []) if x["revises_task_id"]}
        check(f"activity-extensions.json/task_conditions/{index}", lambda entry=entry, key=key: require(
            ("task_id" in entry) != ("task_title" in entry) and key in targets, "task condition must name exactly one prepared target"))
        check(f"activity-extensions.json/task_conditions/{index}/dependencies", lambda entry=entry: require(
            set(entry.get("dependencies", [])) <= known | new_tasks, "task dependencies must name provided records or prepared titles"))
        if "observation_rules" in entry:
            check(f"activity-extensions.json/task_conditions/{index}/observation_rules", lambda entry=entry: validate_rules(entry["observation_rules"]))
        if "occurrence_condition" in entry:
            check(f"activity-extensions.json/task_conditions/{index}/occurrence_condition", lambda entry=entry: planning.validate_condition(entry["occurrence_condition"]))
    check("activity-extensions.json/task_conditions", lambda: require(len(targeted) == len(set(targeted)), "task conditions must not repeat a target"))
    for family, key in (("task_dispositions", "task_id"), ("queued_requests", "request_id"),
                        ("research_requests", "id"), ("academic_resolutions", "id")):
        rows = extensions.get(family, [])
        check("activity-extensions.json/" + family, lambda rows=rows, key=key: require(
            len({row[key] for row in rows}) == len(rows), "entries must identify distinct targets"))
    if action["role"] in PLANNERS:
        check("activity-extensions.json/model_assessments", lambda: validate_assessments(
            action, output, extensions, required=context.get("budget_unit") == "concurrent_sessions"))
    for entry in extensions.get("queued_requests", []):
        check("activity-extensions.json/queued_requests", lambda entry=entry: require(
            entry["request_id"] in {a["id"] for a in context.get("queued_work", [])}, "request was not available for planning"))
    assessed = {row["task_id"]: row["decision"] for row in output.get("task_assessments", [])}
    for entry in extensions.get("task_dispositions", []):
        def disposition(entry=entry):
            task = tasks.get(entry["task_id"], {})
            # The receiver withdraws after this output's task assessments; returned work is withdrawn only after an incomplete assessment.
            status = {"completed": "completed", "closed": "closed", "incomplete": "needs_revision"}.get(
                assessed.get(entry["task_id"]), task.get("status"))
            require(status in {"planned", "ready", "waiting", "needs_revision"}, "task is not withdrawable after this output's task assessments")
            require(not task.get("academic_requirement_id"), "academic requirements cannot be withdrawn autonomously")
            require(entry["task_id"] not in output.get("selections", []) and entry["task_id"] not in {c["revises_task_id"] for c in output.get("candidates", [])}, "cannot withdraw and select or revise the same task")
        check("activity-extensions.json/task_dispositions", disposition)
    for entry in extensions.get("academic_resolutions", []):
        check("activity-extensions.json/academic_resolutions", lambda entry=entry: require(
            entry["id"] in {r["id"] for r in context.get("external_rejections", [])}, "resolution must identify an external rejection"))

    for index, entry in enumerate(extensions.get("external_requests", [])):
        def external(entry=entry):
            operation = prepare_operation(entry["request"], entry.get("grant_id") or "ungranted", "submission-preview")
            if entry.get("grant_id"):
                grant = next((g for g in context.get("grants", []) if g["id"] == entry["grant_id"]), None)
                require(grant is not None and grant.get("kind") == "http", "external request needs a provided HTTP grant")
                from datetime import datetime, timezone
                validate_operation(operation, grant, datetime.now(timezone.utc).isoformat())
            if entry.get("academic_effect_id"):
                effect = next((e for e in (context.get("task") or {}).get("required_external_effects", []) if e["id"] == entry["academic_effect_id"]), None)
                require(effect is not None, "academic effect must belong to the assigned task")
                require(not effect.get("grant_id") or effect["grant_id"] == entry.get("grant_id"), "academic effect requires its specified grant")
        check(f"activity-extensions.json/external_requests/{index}", external)

    relations = [*output.get("relations", []), *extensions.get("relations", [])]
    if relations:
        def relational():
            # Load the actual records needed for proof/endpoint validation. Other
            # catalog entries provide only the status facts already visible.
            records = {r["id"]: deepcopy(r) for r in context.get("knowledge_catalog", [])}
            by_id = {r["id"]: r for r in context.get("knowledge_catalog", [])}
            needed = {ref for relation in relations for ref in [relation["source"], relation["target"], *relation.get("formal_result_refs", [])]}
            for ref in needed & knowledge_ids:
                records[ref] = load_json(_safe_path(workspace, by_id[ref]["path"], require_input=True).read_bytes())
            records.update({x["title"]: {**x, "id": x["title"], "status": "candidate"} for x in output.get("knowledge", [])})
            formal = context.get("formal_verifier", {})
            env = formal.get("environment_id")
            instance = {"knowledge": records, "sources": context.get("sources", []), "active_trust_environment": env,
                "trust_environments": {env: {"status": formal.get("environment_status")}} if env else {},
                "kind_definitions": {d["family"] + ":" + d["token"]: d for rows in context.get("kind_definitions", {}).values() for d in rows}}
            for relation in relations:
                result = knowledge_io.validate_relation(instance, relation)
                require(result["valid"], "; ".join(result["reasons"]))
        check("relations", relational)
    if action["role"] == "identity_review" and action.get("review_cycle_id"):
        check("output", lambda: review_cycle.validate_visible_output(context["role_review"], action, output,
                    requesting_research=bool(extensions.get("research_requests"))))
        for entry in extensions.get("research_requests", []):
            for ref in entry["source_refs"]:
                check("activity-extensions.json/research_requests/source_refs", lambda ref=ref: validate_research_reference(ref, context, workspace))
    if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
        research = context["review_research"]
        check("output", lambda: require(output["outcome"] != "answered" or (
            output["scope_complete"] and output["evidence_refs"] and not output["questions"]), "answered requires complete scope, evidence and no unresolved question"))
        for ref in [*output["used_sources"], *output["evidence_refs"]]:
            def source(ref=ref):
                if ref in {s["ref"] for s in research["sources"]}:
                    return
                require(ref.startswith("workspace:"), "investigation evidence is outside its fixed source set")
                name = ref.removeprefix("workspace:")
                path = _safe_path(workspace, name)
                require(not _excluded(Path(name)) and path.is_file(), "evidence must be a collectable workspace file: " + name)
            check("output/evidence_refs", source)
    return issues


def install_tools(workspace: Path, context: dict, schema: dict, max_artifact_bytes: int | None) -> dict:
    """Copy one installed code edition, never the central research state."""
    package = Path(__file__).resolve().parent
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as bundle:
        for path in sorted(package.glob("*.py")):
            entry = zipfile.ZipInfo("do_math/" + path.name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, path.read_bytes())
    files = {"tools/submission-support.zip": archive.getvalue()}
    files["tools/check_submission.py"] = (b"import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
        b"sys.path.insert(0, str(Path(__file__).with_name('submission-support.zip')))\n"
        b"from do_math.submission import main\nraise SystemExit(main())\n")
    if "formal_verifier" in context:
        files["tools/check_lean.py"] = (b"import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
            b"sys.path.insert(0, str(Path(__file__).with_name('submission-support.zip')))\n"
            b"from do_math.formal_preview import main\nraise SystemExit(main())\n")
        context["formal_verifier"]["preview"] = {
            "command": [sys.executable, "-B", "input/tools/check_lean.py"],
            "arguments": "--source <workspace-relative .lean file> --declaration <name> (repeat for each declaration)",
            "authoritative": False,
            "environment": "Same verifier edition and configured command. Shared libraries and Lake caches are not isolated. Central verification is mandatory."}
    contract = {"command": [sys.executable, "-B", "input/tools/check_submission.py"],
        "workspace": str(workspace.resolve()),
        "schema_path": "input/submission/schema.json", "context_path": "input/submission/context.json",
        "extensions_schema_path": "input/submission/extensions.schema.json",
        "limits": {"max_artifact_bytes": max_artifact_bytes, "checkpoint_bytes": CHECKPOINT_MAX_BYTES,
                   "observation_rules_bytes": RULES_MAX_BYTES},
        "scratch_directory": ".scratch", "not_checked": ["mathematical_meaning", "Lean", "application_time_currentness", "final_authority_and_provenance"]}
    context["submission_contract"] = contract
    files["submission/context.json"] = canonical_json(context)
    files["submission/schema.json"] = canonical_json(schema)
    files["submission/extensions.schema.json"] = canonical_json(extension_schema(context["action"], context.get("kind_definitions", {})))
    materialize_inputs(workspace, files)
    return contract


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    workspace = Path.cwd().resolve()
    try:
        context = load_json((workspace / "input/submission/context.json").read_bytes())
        schema = load_json((workspace / "input/submission/schema.json").read_bytes())
        draft = args.output.resolve()
        if not draft.is_relative_to(workspace):
            raise ValueError("submission draft must be inside this workspace")
        raw = draft.read_bytes()
        output = load_json(raw)
        extensions = read_extensions(workspace)
        issues = payload_issues(output, schema, context, extensions, workspace)
        limits = context["submission_contract"]["limits"]
        files = (collect_outputs(workspace, max_bytes=limits["max_artifact_bytes"])
                 if limits["max_artifact_bytes"] is not None else {"manifest": [], "omitted": []})
        issues.extend(_issue(row["path"], row["reason"]) for row in files["omitted"])
        checkpoint = read_checkpoint(workspace)
        if checkpoint["status"] not in {"missing", "valid"}:
            issues.append(_issue("checkpoint.json", checkpoint.get("error", checkpoint["status"])))
        elif checkpoint["status"] == "valid":
            for reference in checkpoint["value"]["evidence_paths"]:
                try:
                    validate_reference(reference, context, workspace)
                except (ValueError, TypeError, OSError) as error:
                    issues.append(_issue("checkpoint.json/evidence_paths", str(error)))
        rules_path = _safe_path(workspace, "observation-rules.json")
        if rules_path.exists():
            try:
                rules = rules_path.read_bytes()
                if len(rules) > limits["observation_rules_bytes"]:
                    raise ValueError("observation rules exceed 64 KiB")
                validate_rules(load_json(rules))
            except (ValueError, TypeError, OSError) as error:
                issues.append(_issue("observation-rules.json", str(error)))
        result = {"passed": not issues, "issues": issues, "output_sha256": hashlib.sha256(raw).hexdigest(),
            "input_snapshot": context.get("snapshot"), "files": files["manifest"],
            "not_checked": context["submission_contract"]["not_checked"]}
    except (ValueError, TypeError, KeyError, OSError) as error:
        result = {"passed": False, "issues": [_issue("submission", str(error))]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1
