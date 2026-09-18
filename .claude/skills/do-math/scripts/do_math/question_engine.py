"""Question text stays in its original result; links own routing and resolution."""
from copy import deepcopy
import json

from . import questions


def _pointer(value, pointer):
    for token in pointer.strip("/").split("/"):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


class QuestionEngineMixin:
    def _question_view(self):
        rows = deepcopy(self.runtime.get("question_links", []))
        refs = list(dict.fromkeys(row["source_ref"] for row in rows if row.get("source_ref")))
        sources = {ref: json.loads(raw) for ref, raw in self.store.read_many(refs, self.head).items()} if refs else {}
        for row in rows:
            decision = self.instance.get('decisions', {}).get(row.get('resolution_ref'))
            if decision:
                row['resolution'] = {key: deepcopy(decision[key]) for key in ('id', 'kind', 'change', 'source_ref', 'created_at') if key in decision}
            try:
                source = (sources[row["source_ref"]] if row.get("source_ref") else
                          self.runtime["review_cycles"][row["source_id"]] if row.get("source_kind") == "review_cycle" else
                          self.runtime["executions"][row["origin_execution_id"]])
                row["text"] = _pointer(source, row["origin_field"])
                if row.get("question_kind") == "grant":
                    row["text"] = "External action requires a user grant: " + row["text"]
            except (KeyError, IndexError, ValueError, TypeError):
                row["text"] = None
                row["source_status"] = "unavailable"
        return rows

    def _record_output_questions(self, action, output, execution_id, *, public=False):
        if not output.get("questions") or (action.get("review_cycle_id") and not public):
            return
        execution = self.runtime["executions"][execution_id]
        inline = bool(execution.get("parent_execution_id"))
        source = None
        review_source = None
        if public and action.get("review_cycle_id"):
            cycle = self.runtime["review_cycles"][action["review_cycle_id"]]
            review_source = next(key for key, row in cycle["results"].items() if row["execution_id"] == execution_id)
        else:
            source = (self.runtime["activities"][execution["activity_id"]]["result_ref"] if inline else
                      f"runtime/artifacts/{execution['artifact_bundle']}/output.json")
        routes = {row["question_index"]: row for row in execution.get("extensions", {}).get("question_routes", [])}
        default_owner = "operations" if action["role"] in {"operational_review", "maintenance"} else "research"
        if action["role"] == "intent_interpretation" and output.get("needs_clarification"):
            default_owner = "user"
        for index, text in enumerate(output.get("questions", [])):
            route = routes.get(index, {})
            owner = route.get("owner", default_owner)
            targets = route.get("target_ids", [self.instance["id"]] if owner == "user" else [action["target"]] if action.get("target") else [])
            field = ("results/" + review_source + "/output/" if review_source else "output/" if inline else "") + "questions/" + str(index)
            row = questions.link(self.runtime, execution_id=execution_id, field=field,
                owner=owner, targets=targets, source_ref=source, reason=route.get("reason"))
            if review_source:
                row.update(source_kind="review_cycle", source_id=action["review_cycle_id"])

    def _apply_question_resolutions(self, execution_id):
        extension = self.runtime["executions"][execution_id].get("extensions", {})
        by_id = {row["id"]: row for row in self.runtime.get("question_links", [])}
        for resolution in extension.get("question_resolutions", []):
            row = by_id[resolution["question_id"]]
            if row["status"] != "open" or row["owner"] not in {"research", "operations"}:
                raise ValueError("question resolution is no longer applicable")
            row.update(status=resolution["disposition"], resolution_ref=execution_id,
                       resolution_evidence=deepcopy(resolution["evidence_refs"]), resolution_reason=resolution["reason"])

    def _record_review_questions(self, cycle, execution_id):
        fields = ["research/" + key + "/question" for key, request in cycle.get("research", {}).items()
                  if request.get("status") in {"pending", "unresolved"}]
        fields.extend(f"research/{key}/result/output/questions/{index}"
                      for key, request in cycle.get("research", {}).items()
                      for index, _ in enumerate(request.get("result", {}).get("output", {}).get("questions", [])))
        fields.extend(f"followup/{index}/research_requests/{number}/question"
                      for index, entry in enumerate(cycle.get("followup", []))
                      for number, _ in enumerate(entry.get("research_requests", [])))
        for field in fields:
            row = questions.link(self.runtime, execution_id=execution_id, field=field, owner="research",
                                 targets=[cycle.get("knowledge_id")] if cycle.get("knowledge_id") else [])
            row.update(source_kind="review_cycle", source_id=cycle["id"])

    def _user_questions(self):
        return [row["text"] for row in self._question_view() if row["owner"] == "user" and row["status"] == "open" and row.get("text")]

    def _has_global_user_question(self):
        return any(self.instance["id"] in row["target_ids"] for row in questions.open_links(self.runtime, "user"))
