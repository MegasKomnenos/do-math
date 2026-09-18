"""Declared revision boundaries and target-by-target disposition checks."""
from copy import deepcopy

from . import knowledge, planning


def capture_targets(instance, runtime, identifiers, *, required=False, source_ref=None):
    result = {}
    for identifier in identifiers:
        if identifier in runtime.get("tasks", {}):
            task = runtime["tasks"][identifier]
            row = {"revision": task.get("revision", 1), "contract_sha256": planning.contract_hash(task)}
        elif identifier in instance.get("knowledge", {}):
            item = instance["knowledge"][identifier]
            row = {"revision": item.get("revision", 1), "content_sha256": knowledge.content_hash(item)}
        else:
            raise ValueError("revision target must name an existing task or knowledge: " + identifier)
        row["required"] = required
        if source_ref:
            row["source_refs"] = [source_ref]
        result[identifier] = row
    return result


def target_changes(targets, instance, runtime):
    changes = []
    for identifier, previous in targets.items():
        try:
            current = capture_targets(instance, runtime, [identifier])[identifier]
        except ValueError:
            changes.append({"id": identifier, "field": "revision_target", "reason": "missing"})
            continue
        for key in ("revision", "contract_sha256", "content_sha256"):
            if previous.get(key) != current.get(key):
                changes.append({"id": identifier, "field": key, "before": previous.get(key), "after": current.get(key)})
    return changes


def submission_errors(output, extensions, context):
    action = context["action"]
    if "revision_targets" not in action:
        return []  # Historical preview inputs retain their original contract.
    declared = action["revision_targets"]
    tasks = {row["id"]: row for row in context.get("tasks", [])}
    if context.get("task"):
        tasks[context["task"]["id"]] = context["task"]
    known_knowledge = {row["id"] for row in context.get("knowledge_catalog", [])}
    errors = []
    def issue(path, message):
        errors.append({"path": "activity-extensions.json/" + path, "message": message})
    requests = [identifier for row in extensions.get("revision_requests", []) for identifier in row["record_ids"]]
    if len(requests) != len(set(requests)) or set(requests) - tasks.keys() - known_knowledge:
        issue("revision_requests", "revision requests must name distinct provided tasks or knowledge")
    if set(requests) & set(output.get("selections", [])):
        issue("revision_requests", "the same output cannot revise and select a task")
    task_writes = {row["revises_task_id"] for row in output.get("candidates", []) if row.get("revises_task_id")}
    knowledge_writes = {row["id"] for row in extensions.get("knowledge_changes", [])}
    if (task_writes | knowledge_writes) - declared.keys():
        issue("revision_targets", "existing records must be declared before this execution; submit revision_requests for new targets")
    resolutions = extensions.get("revision_resolutions", [])
    withdrawals = {row["task_id"] for row in extensions.get("task_dispositions", [])} & declared.keys()
    identifiers = [row["record_id"] for row in resolutions]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) & withdrawals or set(identifiers) | withdrawals != set(declared):
        issue("revision_resolutions", "resolve each declared target exactly once, using a task withdrawal only for task targets")
    prepared = {row["title"]: row for row in output.get("candidates", [])}
    conditions = {row.get("task_title"): row for row in extensions.get("task_conditions", []) if row.get("task_title")}
    for row in resolutions:
        identifier, disposition = row["record_id"], row["disposition"]
        if identifier not in declared:
            continue
        if disposition == "revised" and identifier not in task_writes | knowledge_writes:
            issue("revision_resolutions", "revised requires the corresponding authored change: " + identifier)
        if disposition != "revised" and identifier in task_writes | knowledge_writes:
            issue("revision_resolutions", "an authored revision must have disposition revised: " + identifier)
        if disposition == "unchanged":
            task = tasks.get(identifier, {})
            required = declared[identifier].get("required") or task.get("revision_requested") or any(
                review.get("revision") == task.get("revision") and review.get("decision") != "approved" for review in task.get("reviews", []))
            if required:
                issue("revision_resolutions", "a required revision or rejected contract cannot be cancelled as unchanged")
        if disposition == "delegated":
            title = row.get("task_title")
            if identifier not in known_knowledge or title not in prepared or identifier not in conditions.get(title, {}).get("knowledge_revision_targets", []):
                issue("revision_resolutions", "delegated requires a prepared work task declaring this knowledge target")
        elif "task_title" in row:
            issue("revision_resolutions", "task_title belongs only to a delegated knowledge revision")
    for row in extensions.get("task_conditions", []):
        identifiers = set(row.get("knowledge_revision_targets", []))
        if identifiers - known_knowledge or identifiers - declared.keys():
            issue("task_conditions", "knowledge revision work must name declared knowledge targets")
    return errors


def dependency_cycles(tasks):
    """Return explicit task dependency cycles, including self-dependency."""
    cycles, done, path = [], set(), []
    def visit(identifier):
        if identifier in path:
            cycles.append(path[path.index(identifier):] + [identifier])
            return
        if identifier in done:
            return
        path.append(identifier)
        for dependency in tasks[identifier].get("dependencies", []):
            if dependency in tasks:
                visit(dependency)
        path.pop()
        done.add(identifier)
    for identifier in tasks:
        visit(identifier)
    return cycles
