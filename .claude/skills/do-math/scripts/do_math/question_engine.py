"""Question text stays in its original result; links own routing and resolution."""
from copy import deepcopy
import json

from . import academic, questions


def resolve_pointer(value, pointer):
    for token in pointer.strip("/").split("/"):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def question_view(instance, runtime, read_many):
    """Question links with the text each resolves to in its original source.

    ``read_many(paths)`` reads the source artifacts of one snapshot. A source
    that no longer resolves leaves the text None and marks it unavailable.
    """
    rows = deepcopy(runtime.get("question_links", []))
    refs = list(dict.fromkeys(row["source_ref"] for row in rows if row.get("source_ref")))
    sources = {ref: json.loads(raw) for ref, raw in read_many(refs).items()} if refs else {}
    for row in rows:
        decision = instance.get('decisions', {}).get(row.get('resolution_ref'))
        if decision:
            row['resolution'] = {key: deepcopy(decision[key]) for key in ('id', 'kind', 'change', 'source_ref', 'created_at') if key in decision}
        try:
            source = (sources[row["source_ref"]] if row.get("source_ref") else
                      runtime["intent_imports"][row["source_id"]] if row.get("source_kind") == "intent_import" else
                      runtime["review_cycles"][row["source_id"]] if row.get("source_kind") == "review_cycle" else
                      runtime["history"] if row.get("source_kind") == "history" else
                      runtime["executions"][row["origin_execution_id"]])
            field = row["origin_field"]
            row["text"] = resolve_pointer(source, field)
            if row.get("question_kind") == "grant":
                row["text"] = "External action requires a user grant: " + row["text"]
        except (KeyError, IndexError, ValueError, TypeError):
            row["text"] = None
            row["source_status"] = "unavailable"
    return rows


def user_questions(view):
    """The texts of the open questions a user owns, from a ``question_view``."""
    return [row["text"] for row in view if row["owner"] == "user" and row["status"] == "open" and row.get("text")]


class QuestionEngineMixin:
    def _question_view(self):
        return question_view(self.instance, self.runtime, lambda refs: self.store.read_many(refs, self.head))

    def _record_output_questions(self, action, output, execution_id, *, public=False, source_ref=None):
        # v5 intent questions are published only by governance.apply_import after check.
        if action.get("role") == "intent_interpretation":
            return
        if not output.get("questions") or (action.get("review_cycle_id") and not public):
            return
        execution = self.runtime["executions"][execution_id]
        source = None
        review_source = None
        if public and action.get("review_cycle_id"):
            cycle = self.runtime["review_cycles"][action["review_cycle_id"]]
            review_source = next(key for key, row in cycle["results"].items() if row["execution_id"] == execution_id)
        else:
            source = source_ref or (execution.get("submission_intent", {}).get("output_ref") or
                      f"runtime/artifacts/{execution['artifact_bundle']}/output.json")
        routes = {row["question_index"]: row for row in execution.get("extensions", {}).get("question_routes", [])}
        default_owner = "operations" if action["role"] in questions.OPERATIONS_ROLES else "research"
        for index, text in enumerate(output.get("questions", [])):
            route = routes.get(index, {})
            owner = route.get("owner", default_owner)
            targets = route.get("target_ids", [self.instance["id"]] if owner == "user" else [action["target"]] if action.get("target") else [])
            field = ("results/" + review_source + "/output/" if review_source else "") + "questions/" + str(index)
            row = questions.link(self.runtime, execution_id=execution_id, field=field,
                owner=owner, targets=targets, source_ref=source, reason=route.get("reason"), blocks=route.get("blocks", False))
            if review_source:
                row.update(source_kind="review_cycle", source_id=action["review_cycle_id"])

    def _apply_question_resolutions(self, execution_id):
        extension = self.runtime["executions"][execution_id].get("extensions", {})
        rows = deepcopy(self.runtime.get("question_links", []))
        by_id = {row["id"]: row for row in rows}
        role = self.runtime["executions"][execution_id].get("role")
        seen = set()
        for resolution in extension.get("question_resolutions", []):
            identifier = resolution["question_id"]
            # The receiver's schema already fixed disposition, reason and evidence.
            error = questions.resolution_error(None if identifier in seen else by_id.get(identifier), role)
            if error:
                raise ValueError(error)
            seen.add(identifier)
            row = by_id[identifier]
            for ref in resolution["evidence_refs"]:
                academic.evidence_record(self.instance, self.runtime, ref, self._academic_evidence)
            questions.close(row, kind="ai_resolution", status=resolution["disposition"], resolution_ref=execution_id,
                            affected_ids=questions.open_targets(row),
                            evidence={"evidence_refs": resolution["evidence_refs"], "reason": resolution["reason"]})
        self.runtime["question_links"] = rows

    def _record_review_questions(self, cycle, execution_id):
        fields = ["research/" + key + "/question" for key, request in cycle.get("research", {}).items()
                  if request.get("status") in {"pending", "unresolved"}]
        fields.extend(f"research/{key}/result/output/questions/{index}"
                      for key, request in cycle.get("research", {}).items()
                      for index, _ in enumerate((request.get("result") or {}).get("output", {}).get("questions", [])))
        fields.extend(f"followup/{index}/research_requests/{number}/question"
                      for index, entry in enumerate(cycle.get("followup", []))
                      for number, _ in enumerate(entry.get("research_requests", [])))
        for field in fields:
            row = questions.link(self.runtime, execution_id=execution_id, field=field, owner="research",
                                 targets=[cycle.get("knowledge_id")] if cycle.get("knowledge_id") else [])
            row.update(source_kind="review_cycle", source_id=cycle["id"])

    def _user_questions(self):
        return user_questions(self._question_view())
