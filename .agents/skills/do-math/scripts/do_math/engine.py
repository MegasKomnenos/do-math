"""Persistent research workflow using observable Codex CLI executions.

The executable contract is do-math-cli/1. It preserves distinct mathematical,
semantic, goal, authority and execution judgments; it does not claim the old
draft/9 provider-call or OS read-isolation guarantees.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import base64
import binascii
import hashlib
import json
import inspect
from pathlib import Path
import time
from typing import Any

import jsonschema

from .contracts import render_prompt, schema_for, all_prompt_documents, reading_map
from .formal import verify_lean, discover_lean
from . import governance, knowledge, planning, knowledge_io
from .input_basis import capture_sources, sources_current
from .context_store import collect_outputs, fit_context, materialize_inputs
from .observations import ObservationTracker, CHECKPOINT_SCHEMA, recovered_checkpoint, request_checkpoint, validate_rules
from .review_engine import ReviewEngineMixin
from .lifecycle_engine import LifecycleEngineMixin
from .academic_engine import AcademicEngineMixin
from .model_runner import CodexModelRunner
from .repository import ResearchRepository, canonical_json, new_id
from .state_checks import state_errors

CONTRACT = "do-math-cli/1"
ENGINE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}
DEFAULT_CONFIG = {
    "model": "gpt-5.6-sol", "effort": "medium", "role_models": {},
    "work_calls": 40, "operations_calls": 30, "call_timeout_seconds": 600,
    "run_timeout_seconds": 7200, "max_cycles": 5, "reviewers": 2,
    "goal_auditors": 2, "max_input_bytes": 500000, "max_output_repairs": 1,
    "lean_command": None, "lean_timeout_seconds": 120,
    "review_rounds": 3, "review_research_limit": 3, "research_reconsider_seconds": 86400,
    "observation_mode": "event_driven", "observation_interval_seconds": 300,
    "observation_idle_seconds": 120, "max_observation_reviews": 3,
    "checkpoint_grace_seconds": 10, "max_artifact_bytes": 268435456,
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"sha256": hashlib.sha256(value).hexdigest(), "text": value.decode("utf-8", "replace"),
                "base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > (1 << 53) - 1:
        return str(value)
    return value


def validate_config(config: dict) -> None:
    if set(config) - set(DEFAULT_CONFIG):
        raise ValueError("configuration fields differ from do-math-cli/1")
    config = {**DEFAULT_CONFIG, **config}
    if not isinstance(config["model"], str) or not config["model"].strip():
        raise ValueError("model is required")
    if config["effort"] not in {"minimal", "low", "medium", "high", "xhigh"}:
        raise ValueError("unsupported reasoning effort")
    if not isinstance(config["role_models"], dict) or any(not isinstance(v, str) or not v for v in config["role_models"].values()):
        raise ValueError("role_models must map roles to model names")
    for role in config["role_models"]:
        schema_for(role)
    for key in ("work_calls", "operations_calls", "call_timeout_seconds", "run_timeout_seconds",
                "max_cycles", "reviewers", "goal_auditors", "max_input_bytes", "lean_timeout_seconds",
                "review_rounds", "review_research_limit", "research_reconsider_seconds", "observation_interval_seconds",
                "observation_idle_seconds", "max_observation_reviews", "checkpoint_grace_seconds", "max_artifact_bytes"):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if isinstance(config.get("max_output_repairs", 1), bool) or not isinstance(config.get("max_output_repairs", 1), int) or config.get("max_output_repairs", 1) < 0:
        raise ValueError("max_output_repairs must be a nonnegative integer")
    command = config["lean_command"]
    if command is not None and (not isinstance(command, list) or not command or
                               any(not isinstance(x, str) or not x or "\0" in x for x in command)):
        raise ValueError("lean_command must be a nonempty argv list")
    if config["observation_mode"] not in {"event_driven", "periodic"}:
        raise ValueError("observation_mode must be event_driven or periodic")
    if not isinstance(config["allowed_axioms"], list) or any(not isinstance(a, str) or not a for a in config["allowed_axioms"]):
        raise ValueError("allowed_axioms must contain axiom names")


def initialize(repository: Path, *, goal: str, workspace: Path, config: dict | None = None,
               title: str = "", goal_kind: str = "mathematical", policies: str = "",
               instance_id: str | None = None, sources: list[Path] | None = None) -> dict:
    if not goal.strip() or goal_kind not in {"mathematical", "research"}:
        raise ValueError("a goal and mathematical/research goal_kind are required")
    settings = deepcopy(DEFAULT_CONFIG)
    settings.update(config or {})
    validate_config(settings)
    instance_id = instance_id or new_id("RI")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    instance = {"contract_id": CONTRACT, "id": instance_id, "title": title or goal[:80],
                "goal": goal, "goal_kind": goal_kind, "policies": policies, "config": settings,
                "workspace": str(workspace), "created_at": now(), "knowledge": {}, "relations": [],
                "sources": [], "goal_judgments": [], "goal_status": "unresolved"}
    runtime = {"contract_id": CONTRACT, "status": "ready", "tasks": {}, "executions": {},
               "activities": {}, "queue": [{"role": "research_preparation", "reason": "initial research preparation"}],
               "cycles": 0, "active_execution": None, "processed_controls": [], "inputs": [],
               "questions": [], "history": [], "updated_at": now()}
    instance = knowledge_io.ensure_ontology(governance.ensure_governance(instance))
    instance["feature_version"] = 2
    runtime["feature_version"] = 2
    store = ResearchRepository(repository, instance_id)
    with store.writer_lock():
        head = store.initialize(instance, runtime)
        if sources:
            artifacts = {}
            bundle = new_id("BA")
            for i, source in enumerate(sources):
                raw = source.read_bytes()
                path = f"runtime/artifacts/{bundle}/{i:04d}-{source.name}"
                artifacts[path] = raw
                instance["sources"].append({"path": path, "name": source.name,
                                            "sha256": hashlib.sha256(raw).hexdigest()})
            head = store.save(head, instance, runtime, artifacts=artifacts)
    return {"instance_id": instance_id, "snapshot": head, "status": runtime["status"]}


def control(repository: Path, instance_id: str, action: str, *, text: str = "", config: dict | None = None) -> dict:
    """Queue user commands; only the owning engine publishes authority changes."""
    if action not in {"pause", "resume", "close", "input", "configure", "request",
                      "decision", "knowledge", "trust", "external", "conversation", "source"}:
        raise ValueError("unknown control action")
    _, instance, runtime = ResearchRepository(repository, instance_id).load()
    if action == "configure":
        candidate = {**instance["config"], **(config or {})}
        validate_config(candidate)
    if action == "input" and not text.strip():
        raise ValueError("input text is required")
    if action == "source":
        config = dict(config or {})
        path = Path(config["path"]).resolve(strict=True)
        raw = path.read_bytes()
        name = config.get("name") or path.name
        if not isinstance(name, str) or name in {"", ".", ".."} or "/" in name or "\\" in name:
            raise ValueError("source name must be a file name")
        config = {"name": name, "body_base64": base64.b64encode(raw).decode("ascii"),
                  "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    if action == "request":
        role = (config or {}).get("role")
        if role not in {"research_preparation", "research_plan", "supplemental_research", "operational_review", "maintenance"}:
            raise ValueError("unsupported requested role")
        if runtime["status"] in {"closed", "completed"}:
            raise ValueError("closed/completed instance cannot accept new research activities")
        if role == "supplemental_research" and runtime["tasks"].get((config or {}).get("target"), {}).get("status") != "ready":
            raise ValueError("supplemental research requires the ID of a reviewed ready task")
        if role == "operational_review" and (config or {}).get("target") not in runtime["executions"]:
            raise ValueError("operational review requires an existing execution ID")
    request = {"id": new_id("UC"), "instance_id": instance_id, "action": action,
               "text": text, "config": config or {}, "created_at": now()}
    inbox = Path(instance["workspace"]) / "control" / instance_id
    inbox.mkdir(parents=True, exist_ok=True)
    temporary = inbox / (request["id"] + ".tmp")
    temporary.write_bytes(canonical_json(request))
    temporary.replace(inbox / (request["id"] + ".json"))
    return {"accepted": True, "request_id": request["id"], "effect": "pending engine processing"}


def _records(instance: dict, runtime: dict) -> list[dict]:
    records = []
    for knowledge in instance["knowledge"].values():
        records.append({"family": "knowledge", **knowledge})
    for relation in instance["relations"]:
        records.append({"family": "relation", **relation})
    for task in runtime["tasks"].values():
        records.append({"family": "task", **task})
    for activity in runtime["activities"].values():
        records.append({"family": "activity", **activity})
    for execution in runtime["executions"].values():
        records.append({"family": "execution", **execution})
    for family, container in (("grant", instance.get("grants", {})), ("decision", instance.get("decisions", {})),
                              ("external-operation", runtime.get("external_operations", {})),
                              ("review-cycle", runtime.get("review_cycles", {})),
                              ("trust-environment", instance.get("trust_environments", {}))):
        for record in container.values():
            records.append({"family": family, **record})
    for source in instance.get("sources", []):
        if source.get("id"):
            records.append({"family": "source", **source})
    for key, definition in instance.get("kind_definitions", {}).items():
        records.append({**definition, "id": "KD-" + key, "family": "kind-definition", "definition_family": definition["family"]})
    return sorted(records, key=lambda r: r["id"])


def query_records(repository: Path, instance_id: str, *, snapshot: str | None = None,
                  kind: str | None = None, text: str = "", limit: int = 50,
                  cursor: str | None = None, related_to: str | None = None, direction: str = "both") -> dict:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    if direction not in {"incoming", "outgoing", "both"}:
        raise ValueError("direction must be incoming, outgoing or both")
    parameters = {"instance_id": instance_id, "kind": kind, "text": text, "related_to": related_to, "direction": direction}
    last = None
    if cursor:
        try:
            decoded = json.loads(base64.urlsafe_b64decode(cursor).decode("utf-8"))
            if decoded["parameters"] != parameters or (snapshot is not None and snapshot != decoded["snapshot"]):
                raise ValueError("cursor query or snapshot changed")
            snapshot, last = decoded["snapshot"], decoded["last"]
        except (KeyError, UnicodeError, json.JSONDecodeError, binascii.Error) as error:
            raise ValueError("invalid cursor") from error
    head, instance, runtime = ResearchRepository(repository, instance_id).load(snapshot)
    records = _records(instance, runtime)
    if kind:
        records = [r for r in records if r["family"] == kind or r.get("kind") == kind]
    if text:
        records = [r for r in records if text.casefold() in canonical_json(r).decode("utf-8").casefold()]
    if related_to:
        relations = [r for r in instance["relations"] if
                     (direction in {"outgoing", "both"} and r["source"] == related_to) or
                     (direction in {"incoming", "both"} and r["target"] == related_to)]
        ids = {r["id"] for r in relations} | {r["target"] for r in relations if r["source"] == related_to} | {
            r["source"] for r in relations if r["target"] == related_to}
        records = [r for r in records if r["id"] in ids]
    total = len(records)
    if last is not None:
        if last not in {r["id"] for r in records}:
            raise ValueError("cursor does not name a record in the fixed query")
        records = [r for r in records if r["id"] > last]
    selected = records[:limit]
    truncated = len(records) > limit
    next_cursor = None
    if truncated:
        next_cursor = base64.urlsafe_b64encode(canonical_json({"parameters": parameters, "snapshot": head,
                                                             "last": selected[-1]["id"]})).decode("ascii")
    return {"snapshot": head, "total": total, "loaded": len(selected), "truncated": truncated,
            "items": [{"record": r, "sha256": hashlib.sha256(canonical_json(r)).hexdigest()} for r in selected],
            "next_cursor": next_cursor}


def read_record(repository: Path, instance_id: str, record_id: str, *, snapshot: str | None = None) -> dict:
    head, instance, runtime = ResearchRepository(repository, instance_id).load(snapshot)
    for record in _records(instance, runtime):
        if record["id"] == record_id:
            return {"snapshot": head, "record": record, "sha256": hashlib.sha256(canonical_json(record)).hexdigest()}
    raise KeyError(f"record not found at {head}: {record_id}")


class ResearchEngine(ReviewEngineMixin, LifecycleEngineMixin, AcademicEngineMixin):
    def __init__(self, repository: Path, instance_id: str, *, runner: Any = None, formal_verifier: Any = None):
        self.store = ResearchRepository(repository, instance_id)
        self.runner = runner or CodexModelRunner()
        self.formal_verifier = formal_verifier or verify_lean
        self.head, self.instance, self.runtime = self.store.load()
        if self.instance.get("contract_id") != CONTRACT or self.runtime.get("contract_id") != CONTRACT:
            raise ValueError("unsupported instance contract; explicit migration is required")
        self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), **self.instance["config"]}
        self._live_execution_ids = set()
        self._inline_reviewing = False
        self._documents = all_prompt_documents()
        self._installation = self._installation_manifest()
        self._upgrade_runtime()
        self.instance = knowledge_io.ensure_ontology(self.instance)

    @staticmethod
    def _installation_manifest() -> dict:
        root = Path(__file__).resolve().parents[2]
        documents = dict.fromkeys(relative for paths in reading_map(skill_root=root).values() for relative in paths)
        paths = [*sorted((root / "scripts" / "do_math").glob("*.py")), *(root / relative for relative in documents)]
        files = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        return {"feature_version": 2, "files": files, "sha256": hashlib.sha256(canonical_json(files)).hexdigest()}

    def _render_prompt(self, role: str, context: dict, **kwargs) -> str:
        return render_prompt(role, context, documents=self._documents[role], **kwargs)

    def _input_artifacts(self, bundle: str, role: str, prompt: str, schema: dict, fitted: dict) -> dict[str, bytes]:
        base = f"runtime/artifacts/{bundle}"
        documents = self._documents[role]
        manifest = [*fitted["manifest"], *({"key": "implementation_document", "logical_path": document["path"],
            "path": "input/implementation/" + document["path"], "sha256": document["sha256"],
            "bytes": len(document["content"].encode("utf-8"))} for document in documents)]
        return {f"{base}/input.txt": prompt.encode("utf-8"), f"{base}/schema.json": canonical_json(schema),
                f"{base}/manifest.json": canonical_json(manifest),
                **{f"{base}/input/implementation/{document['path']}": document["content"].encode("utf-8")
                   for document in documents}}

    def _save(self, artifacts: dict[str, bytes] | None = None) -> None:
        self.runtime["updated_at"] = now()
        self.head = self.store.save(self.head, self.instance, self.runtime, artifacts=artifacts)

    def _inbox(self) -> list[dict]:
        path = Path(self.instance["workspace"]) / "control" / self.instance["id"]
        results = []
        for file in sorted(path.glob("*.json")):
            if file.stem in self.runtime["processed_controls"]:
                continue
            request = json.loads(file.read_text(encoding="utf-8"))
            if request.get("id") != file.stem or request.get("instance_id") != self.instance["id"]:
                raise ValueError("control identity mismatch")
            results.append(request)
        return results

    def _controls(self) -> None:
        for request in self._inbox():
            action = request["action"]
            if action == "source":
                spec = request["config"]
                raw = base64.b64decode(spec["body_base64"], validate=True)
                if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
                    self._reject_control(request, "source bytes differ from the accepted request")
                    continue
                old = next((s for s in self.instance["sources"] if s["name"] == spec["name"]), None)
                if old and old["sha256"] == spec["sha256"]:
                    self.runtime["processed_controls"].append(request["id"])
                    self.runtime["history"].append({"kind": "source_unchanged", "request_id": request["id"], "name": spec["name"]})
                    self._save()
                    continue
                bundle = new_id("BA")
                entry = {"id": old.get("id", new_id("SO")) if old else new_id("SO"), "name": spec["name"],
                         "path": f"runtime/artifacts/{bundle}/source.bin", "sha256": spec["sha256"], "bytes": len(raw),
                         "revision": old.get("revision", 1)+1 if old else 1, "status": "active", "source_ref": request["id"]}
                if old:
                    entry["history"] = [*old.get("history", []), {k: v for k, v in old.items() if k != "history"}]
                    self.instance["sources"].remove(old)
                self.instance["sources"].append(entry)
                names = {entry["name"], "source:"+entry["name"], entry["id"]}
                if old: names.add(old["path"])
                for task in self.runtime["tasks"].values():
                    if names.intersection(task.get("inputs", [])):
                        task["newinput"] = request["id"]
                        if old and task["status"] != "closed":
                            reason = "Required source content changed: " + spec["name"]
                            if task["status"] != "completed":
                                task["status"] = "planned"
                            if task.get("assessment"):
                                task["assessment"].update(current=False, invalidated_reason=reason)
                            for review in task.get("reviews", []): review["inputs_current"] = False
                        for execution in self.runtime["executions"].values():
                            if execution.get("action", {}).get("target") == task["id"] and execution["status"] != "ended":
                                execution["stop_requested"] = "required_input_changed"
                for kid in list(self.instance["knowledge"]):
                    record = self.instance["knowledge"][kid]
                    basis = record.get("source_basis", [])
                    if (record.get("status") != "withdrawn" and any(row.get("name") == spec["name"] for row in basis)
                            and not sources_current(basis, self.instance)):
                        self.instance, self.runtime = knowledge.suspend_for_source_change(self.instance, self.runtime, kid,
                            source_name=spec["name"], reason="Required source content changed: " + spec["name"], actor_ref=request["id"])
                self._invalidate_goal_currentness()
                if self.runtime["status"] in {"waiting", "budget_exhausted"}: self.runtime["status"] = "ready"
                self.runtime["processed_controls"].append(request["id"])
                self.runtime["history"].append({"kind": "user_control", "request": request, "source_id": entry["id"]})
                self._lifecycle_event("source_imported", target=entry["id"], source_ref=request["id"])
                self._save({entry["path"]: raw})
                continue
            try:
                handled = self._knowledge_io_control(request) or self._academic_control(request) or self._apply_extended_control(request)
            except (ValueError, KeyError, TypeError) as error:
                self._reject_control(request, str(error))
                continue
            if handled:
                self.runtime["processed_controls"].append(request["id"])
                self.runtime["history"].append({"kind": "user_control", "request": request})
                self._save()
                continue
            if action == "pause":
                if self.runtime["status"] not in {"completed", "closed"}:
                    self.runtime["status"] = "paused"
            elif action == "close":
                self.runtime["status"] = "closed"
                self.runtime["queue"] = []
            elif action == "resume":
                if self.runtime["status"] in {"closed", "completed"}:
                    self._reject_control(request, "closed/completed instance cannot resume")
                    continue
                self.runtime["status"] = "ready"
                self.runtime.pop("stop_requested", None)
                for waiting in self.runtime.pop("waiting_actions", {}).values():
                    self.runtime["queue"].append(waiting["action"])
                if not self.runtime["queue"]:
                    role = "research_plan" if self.runtime["tasks"] or self.instance["knowledge"] else "research_preparation"
                    self.runtime["queue"].append({"role": role, "reason": request["text"] or "explicit user resume"})
            elif action == "input":
                if self.runtime["status"] in {"closed", "completed"}:
                    self._reject_control(request, "new research input requires an unfinished instance")
                    continue
                self.runtime["inputs"].append(request)
                self.runtime["questions"] = []
                if self.runtime["status"] not in {"closed", "completed", "paused"}:
                    self.runtime["status"] = "ready"
                self.runtime["queue"].insert(0, {"role": "intent_interpretation", "target": request["id"], "reason": "new user input"})
            elif action == "configure":
                self.instance["config"].update(request["config"])
                validate_config(self.instance["config"])
                if self.runtime["status"] == "budget_exhausted":
                    self.runtime["status"] = "ready"
            elif action == "request":
                role, target = request["config"]["role"], request["config"].get("target")
                if self.runtime["status"] in {"completed", "closed"}:
                    self._reject_control(request, "instance ended before the activity request was applied")
                    continue
                if role == "supplemental_research":
                    task = self.runtime["tasks"].get(target)
                    if task is None or task["status"] != "ready":
                        self._reject_control(request, "supplemental task is no longer ready")
                        continue
                    task.update(status="performing", selected_by=request["id"])
                requested = {"role": role, "reason": request["text"], "requested_by": request["id"]}
                if target:
                    requested["target"] = target
                self.runtime["queue"].insert(0, requested)
                if self.runtime["status"] in {"waiting", "budget_exhausted"}:
                    self.runtime["status"] = "ready"
            else:
                raise ValueError("unsupported control action")
            self.runtime["processed_controls"].append(request["id"])
            self.runtime["history"].append({"kind": "user_control", "request": request})
            self._save()

    def _reject_control(self, request: dict, reason: str) -> None:
        self.runtime["processed_controls"].append(request["id"])
        self.runtime["history"].append({"kind": "rejected_user_control", "request": request, "reason": reason})
        self._save()

    def _knowledge_io_control(self, request: dict) -> bool:
        if request["action"] != "knowledge": return False
        spec = request["config"]
        operation = spec.get("operation")
        if operation not in {"import", "register-kind", "import-relation"}: return False
        if operation == "import":
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime, spec["candidate"],
                source_ref=request["id"], actor_ref=request["id"])
            # An omitted source_refs declares no source dependency; it does not mean every imported source.
            self.instance["knowledge"][kid]["source_basis"] = capture_sources(self.instance, spec["candidate"].get("source_refs", []))
            for execution in self.runtime["executions"].values():
                if execution["status"] != "ended" and execution.get("action", {}).get("target") == kid:
                    execution["stop_requested"] = "imported_knowledge_revision"
        elif operation == "register-kind":
            self.instance, _ = knowledge_io.register_kind_definition(self.instance, spec["definition"], source_ref=request["id"], actor_ref=request["id"])
        else:
            self.instance, _ = knowledge_io.import_relation(self.instance, spec["relation"], source_ref=request["id"], actor_ref=request["id"])
        self._invalidate_goal_currentness()
        if self.runtime["status"] in {"waiting", "completed"}: self.runtime["status"] = "ready"
        return True

    def process_controls(self) -> dict:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), **self.instance["config"]}
            self._upgrade_runtime()
            self.instance = knowledge_io.ensure_ontology(self.instance)
            self._controls()
            _, persisted_instance, persisted_runtime = self.store.load(self.head)
            if self.instance != persisted_instance or self.runtime != persisted_runtime:
                self._save()
        return self.status()

    def status(self) -> dict:
        self.head, self.instance, self.runtime = self.store.load()
        executions = list(self.runtime["executions"].values())
        return {"instance_id": self.instance["id"], "snapshot": self.head, "title": self.instance["title"],
                "goal": self.instance["goal"], "goal_status": self.instance["goal_status"],
                "status": self.runtime["status"], "active_execution": self.runtime["active_execution"],
                "pending_actions": len(self.runtime["queue"]), "cycles": self.runtime["cycles"],
                "tasks": [{"id": t["id"], "title": t["title"], "status": t["status"]} for t in self.runtime["tasks"].values()],
                "knowledge": {"K": sum(k["status"] == "verified" and knowledge.assess_use(k, self.instance)["valid"] for k in self.instance["knowledge"].values()),
                              "F": sum(k["status"] != "verified" for k in self.instance["knowledge"].values()),
                              "suspended_K": sum(k["status"] == "verified" and not knowledge.assess_use(k, self.instance)["valid"] for k in self.instance["knowledge"].values())},
                "budget": {pool: {"limit": self.instance["config"][pool + "_calls"],
                                  "used": sum(e.get("budget_kind") == pool for e in executions)} for pool in ("work", "operations")},
                "usage": [e.get("usage", {}) for e in executions if e.get("usage")],
                "latest_results": list(self.runtime["activities"].values())[-5:],
                "questions": self.runtime["questions"], "pending_controls": len(self._inbox()),
                "grants": [{"id": g["id"], "kind": g.get("kind"), "status": g.get("status"), "expires_at": g.get("expires_at")}
                           for g in self.instance.get("grants", {}).values()],
                "pending_events": self.runtime.get("pending_events", []),
                "observations": self.runtime.get("observations", {}),
                "checkpoints": self.runtime.get("checkpoints", {}),
                "external_operations": list(self.runtime.get("external_operations", {}).values()),
                "active_trust_environment": self.instance.get("active_trust_environment"),
                "academic_validation": self._academic_status(),
                "assurance": {"read_scope": "instructions_and_selected_inputs", "provider_operations": "not_observed",
                              "token_usage": "CLI_reported_after_execution", "formal": "Lean_and_axiom_check",
                              "review": "fresh_sessions_without_peer_results_in_inputs"}}

    def run(self, *, max_steps: int | None = None, watch: bool = False) -> dict:
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive")
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), **self.instance["config"]}
            self._upgrade_runtime()
            previous = self.runtime.get("installation")
            self.instance = knowledge_io.ensure_ontology(self.instance)
            if previous != self._installation:
                self.runtime.setdefault("implementation_history", []).append({"from": previous, "to": self._installation,
                    "at": now(), "migration": "known CLI record contract; additive feature-2 fields and preserved prior artifacts"})
                self.runtime["installation"] = deepcopy(self._installation)
                self._save()
            self._controls()
            self._recover_disappeared()
            self._ensure_academic_followup()
            deadline = time.monotonic() + self.instance["config"]["run_timeout_seconds"]
            steps = 0
            while self.runtime["status"] in {"ready", "running"} or (watch and self.runtime["status"] == "waiting"):
                self._controls()
                if self._installation_manifest() != self._installation:
                    self.runtime["status"] = "paused"
                    self.runtime["questions"].append("Installed code or role documents changed. Restart the executor to load one consistent version, then resume.")
                    self._save()
                    break
                self.instance["available_input_refs"] = self._available_inputs()
                self._refresh_readiness()
                if self.runtime["status"] == "waiting" and watch and time.monotonic() < deadline:
                    time.sleep(.5)
                    continue
                if self.runtime["status"] not in {"ready", "running"}:
                    break
                if time.monotonic() >= deadline or (max_steps is not None and steps >= max_steps):
                    self.runtime["status"] = "ready"
                    self._save()
                    break
                if not self.runtime["queue"]:
                    if self.runtime["questions"]:
                        self.runtime["status"] = "waiting"
                    elif self.runtime["cycles"] >= self.instance["config"]["max_cycles"]:
                        self.runtime["status"] = "waiting"
                        self.runtime["questions"].append("Configured research cycles finished; inspect results and resume or revise the goal.")
                    else:
                        self.runtime["queue"].append({"role": "research_preparation", "reason": "use prior results and remaining questions"})
                    self._save()
                    if self.runtime["status"] == "waiting":
                        break
                action = self.runtime["queue"][0]
                if action["role"] == "formal_check":
                    self._formal(action)
                elif self._process_machine_action(action):
                    pass
                else:
                    if not self._call(action, deadline):
                        break
                steps += 1
            self._controls()
            _, persisted_instance, persisted_runtime = self.store.load(self.head)
            if self.instance != persisted_instance or self.runtime != persisted_runtime:
                self._save()
        return self.status()

    def _recover_disappeared(self) -> None:
        unfinished = [e for e in self.runtime["executions"].values() if e["status"] != "ended"]
        if not unfinished:
            return
        artifacts = {}
        for execution in unfinished:
            eid, bundle = execution["id"], new_id("BA")
            workspace = Path(self.instance["workspace"]) / "runs" / eid / "workspace"
            if execution["role"] == "formal_check":
                workspace = Path(self.instance["workspace"]) / "formal" / eid
            elif execution["role"] == "trust_check":
                workspace = Path(self.instance["workspace"]) / "trust" / eid
            files = collect_outputs(workspace, max_bytes=self.instance["config"]["max_artifact_bytes"])
            entries = []
            for path, raw in files["files"].items():
                ref = f"runtime/artifacts/{bundle}/files/{path}"
                artifacts[ref] = raw
                entries.append({"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
            evidence_path = Path(self.instance["workspace"]) / "runs" / eid / "evidence"
            if evidence_path.is_dir():
                evidence = collect_outputs(evidence_path, max_bytes=self.instance["config"]["max_artifact_bytes"])
                for path, raw in evidence["files"].items():
                    artifacts[f"runtime/artifacts/{bundle}/adapter-evidence/{path}"] = raw
                artifacts[f"runtime/artifacts/{bundle}/adapter-evidence-manifest.json"] = canonical_json(evidence["manifest"])
            checkpoint = json_safe(recovered_checkpoint(workspace))
            observed = self.runtime.get("checkpoints", {}).get(eid)
            if checkpoint["kind"] != "worker_checkpoint" and isinstance(observed, dict) and observed.get("kind") == "worker_checkpoint":
                # An unreadable final checkpoint file never replaces the last valid checkpoint observed during execution.
                checkpoint = {**observed, "final_observation": checkpoint}
            self.runtime.setdefault("checkpoints", {})[eid] = checkpoint
            artifacts[f"runtime/artifacts/{bundle}/checkpoint-recovery.json"] = canonical_json(checkpoint)
            artifacts[f"runtime/artifacts/{bundle}/output-manifest.json"] = canonical_json(files["manifest"])
            artifacts[f"runtime/artifacts/{bundle}/omitted.json"] = canonical_json(files["omitted"])
            execution.update(status="ended", outcome="execution_incomplete", error="previous executor disappeared", ended_at=now(),
                             artifact_bundle=bundle, output_files=entries, outputs_complete=files["complete"])
            activity = self.runtime["activities"].get(execution.get("activity_id"))
            if activity:
                activity.update(status="unresolved", result_ref=f"runtime/artifacts/{bundle}/checkpoint-recovery.json")
            action = execution.get("action", {})
            if action and not execution.get("parent_execution_id") and execution["role"] != "external_action":
                self._remove_action(action)
                self.runtime["queue"].append({**action, "recovery": {"execution_id": eid, "reason": "executor_disappeared"}})
            self.runtime["history"].append({"kind": "recovery", "execution_id": eid, "remote_termination": "unknown"})
        for operation in self.runtime.get("external_operations", {}).values():
            if operation["status"] == "running":
                if operation.get("transmitted") is False:
                    # transmitted=true is published before transport, so a published false proves that no request left.
                    operation.update(status="failed", error="executor disappeared before transmission")
                else:
                    operation.update(status="unknown", error="executor disappeared after recording transmission intent")
                self.runtime["queue"] = [a for a in self.runtime["queue"] if not (a["role"] == "external_action" and a.get("target") == operation["id"])]
                self._external_execution_record(operation)
        self.runtime["active_execution"] = None
        if self.runtime["status"] != "closed": self.runtime["status"] = "paused"
        self._save(artifacts)

    def _context(self, action: dict, workspace: Path) -> dict:
        directory = workspace / "input"
        directory.mkdir(parents=True, exist_ok=True)
        documents = self._documents[action["role"]]
        materialize_inputs(workspace, {"implementation/" + document["path"]: document["content"].encode("utf-8")
                                      for document in documents})
        implementation_documents = [{"path": document["path"], "local_path": "input/implementation/" + document["path"],
                                     "sha256": document["sha256"], "bytes": len(document["content"].encode("utf-8"))}
                                    for document in documents]
        catalog = []
        for kid, knowledge_record in sorted(self.instance["knowledge"].items()):
            # Hide the current review group's partial results. Completed prior
            # stages are public evidence needed by planners and goal auditors.
            hidden_reviews = ((action["role"] == "identity_review" and kid == action.get("target")) or
                              len(knowledge_record["reviews"]) < knowledge_record.get("required_reviews", 1))
            record = {k: v for k, v in knowledge_record.items() if not (k == "reviews" and hidden_reviews)}
            path = directory / "knowledge" / (kid + ".json")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(canonical_json(record))
            use = knowledge.assess_use(knowledge_record, self.instance)
            catalog.append({"id": kid, "kind": knowledge_record["kind"], "title": knowledge_record["title"],
                            "summary": knowledge_record["summary"], "status": knowledge_record["status"],
                            "use_suspended": bool(knowledge_record.get("use_suspended")),
                            "usable_as_k": use["valid"], "use_reasons": use["reasons"],
                            "path": path.relative_to(workspace).as_posix()})
            cycle_id = knowledge_record.get("review_cycle_id")
            cycle = self.runtime.get("review_cycles", {}).get(cycle_id)
            if cycle and cycle["status"] in {"completed", "unresolved"} and not (
                    action["role"] == "identity_review" and action.get("review_cycle_id") == cycle_id):
                cycle_path = directory / "review-cycles" / (cycle_id + ".json")
                cycle_path.parent.mkdir(exist_ok=True)
                cycle_path.write_bytes(canonical_json(cycle))
                catalog[-1]["review_cycle_source"] = {"path": cycle_path.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(cycle_path.read_bytes()).hexdigest()}
        sources = []
        for i, source in enumerate(self.instance["sources"]):
            raw = self.store.read(source["path"], self.head)
            path = directory / "sources" / f"{i:04d}-{source['name']}"
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(raw)
            sources.append({**source, "local_path": path.relative_to(workspace).as_posix()})
        target = action.get("target")
        task = self.runtime["tasks"].get(target)
        target_execution_action = self.runtime["executions"].get(target, {}).get("action", {}) if action["role"] == "operational_review" else {}
        private_review_context = bool(action.get("review_cycle_id") or target_execution_action.get("review_cycle_id"))
        task_views = deepcopy(list(self.runtime["tasks"].values()))
        if not private_review_context:
            for view in task_views:
                for result in view.get("results", []):
                    producing = self.runtime["executions"].get(result.get("execution_id"), {})
                    restored = []
                    for file in result.get("output_files", producing.get("output_files", [])):
                        raw = self.store.read(file["artifact_ref"], self.head)
                        if hashlib.sha256(raw).hexdigest() != file["sha256"]:
                            raise ValueError("task result artifact hash changed")
                        path = directory / "task-results" / view["id"] / result["execution_id"] / file["path"]
                        if not path.resolve().is_relative_to(directory.resolve()):
                            raise ValueError("task result artifact path escapes input")
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(raw)
                        restored.append({**file, "local_path": path.relative_to(workspace).as_posix()})
                    result["output_files"] = restored
        context = {"snapshot": self.head, "workspace": str(workspace.resolve()), "goal": self.instance["goal"], "goal_kind": self.instance["goal_kind"],
                   "policies": self.instance["policies"], "action": action, "task": task,
                   "tasks": task_views, "knowledge_catalog": catalog, "implementation_documents": implementation_documents,
                   "relations": self.instance["relations"], "sources": sources,
                   "user_inputs": self.runtime["inputs"], "open_questions": self.runtime["questions"],
                   "recent_history": self.runtime["history"][-8:],
                   "instructions": "Read input/ and your workspace only. Pass the exact absolute workspace as workdir on every shell call, with login=false. Use absolute paths under this workspace for file reads and writes; a shell's default working directory may differ. Ask for missing inputs. Never read other runs or the central repository. New research source code belongs in this workspace."}
        context.update(goal_revision=self.instance.get("goal_revision", 1), policy_revision=self.instance.get("policy_revision", 1),
                       grants=[{k: v for k, v in grant.items() if k != "credential_env"} for grant in self.instance.get("grants", {}).values()],
                       task_readiness=self.runtime.get("task_readiness", {}),
                       checkpoint_schema=CHECKPOINT_SCHEMA, checkpoint_path="checkpoint.json",
                       external_operations=list(self.runtime.get("external_operations", {}).values()),
                       events=[e for e in self.runtime.get("events", []) if e["id"] in action.get("event_refs", [])],
                       available_input_refs=self.instance.get("available_input_refs", []))
        context["resources"] = {pool: {"limit": self.instance["config"][pool+"_calls"],
            "used": sum(e.get("budget_kind") == pool for e in self.runtime["executions"].values())} for pool in ("work", "operations")}
        context["execution_limits"] = {key: self.instance["config"][key] for key in
            ("call_timeout_seconds", "run_timeout_seconds", "checkpoint_grace_seconds", "review_rounds")}
        active_environment = self.instance.get("trust_environments", {}).get(self.instance.get("active_trust_environment"), {})
        context["formal_verifier"] = {"reference": "tool:lean", "mechanism": "central_after_submission",
            "command": self.instance["config"].get("lean_command") or discover_lean(),
            "observed_toolchain": active_environment.get("toolchain"),
            "allowed_axioms": self.instance["config"]["allowed_axioms"],
            "instruction": "Submit self-contained lean_code and declaration_names. The executor runs the verifier after submission. A configured command is not a completed verification. Version is unknown until observed_toolchain or a recorded formal result supplies it; no worker-local Lean preview is advertised."}
        context["academic_requirements"] = self.instance.get("academic_requirements", {})
        context["academic_phase"] = "postsolution" if self.instance["goal_status"] == "mathematically_solved" else "deferred_until_goal_solved"
        context["kind_definitions"] = knowledge_io.catalog_definitions(self.instance)
        context["academic_validation"] = self._academic_status()
        context["external_rejections"] = self.runtime.get("external_rejections", [])
        if action["role"] in {"identity_review", "goal_audit"}:
            context.pop("recent_history")
        if action["role"] == "identity_review":
            context.pop("tasks")
        if action["role"] == "identity_review":
            context["proposal"] = {k: v for k, v in self.instance["knowledge"][target].items() if k != "reviews"}
            if action.get("review_cycle_id"):
                context["role_review"] = self._review_context(action, workspace)
        if action["role"] == "goal_audit":
            context["eligible_knowledge"] = [{"id": k["id"], "statement": k["statement"],
                "explanation": k["explanation"], "summary": k["summary"],
                "formal_verification": {key: k["formal"].get(key) for key in
                                        ("status", "source_sha256", "declarations", "declaration_signatures", "signature_hash", "axioms", "artifact_ref", "toolchain", "trust_environment_id", "trust_environment_status")},
                "identity_reviews": k["reviews"], "identity_assessment": k.get("identity_assessment"),
                "use_status": knowledge.assess_use(k, self.instance)} for k in self.instance["knowledge"].values()
                if k["status"] == "verified" and knowledge.assess_use(k, self.instance)["valid"]]
            for entry in context["eligible_knowledge"]:
                item = self.instance["knowledge"][entry["id"]]
                cycle = self.runtime.get("review_cycles", {}).get(item.get("review_cycle_id"))
                if cycle:
                    final_ids = set(item.get("identity_assessment", {}).get("execution_ids", []))
                    entry["identity_final_judgments"] = [r for r in cycle["results"].values() if r["execution_id"] in final_ids]
                    entry["review_cycle_source"] = next((k.get("review_cycle_source") for k in catalog if k["id"] == entry["id"]), None)
            context["tasks"] = [{k: v for k, v in t.items() if k not in {"reviews", "assessment"}} for t in task_views]
        if action["role"] == "operational_review":
            reviewed_execution = deepcopy(self.runtime["executions"].get(target))
            context["execution_to_review"] = reviewed_execution
            context["observation"] = action.get("observation", self.runtime.get("observations", {}).get(target))
            context["live_review"] = action.get("live", False)
            if reviewed_execution and not context["live_review"] and reviewed_execution.get("artifact_bundle"):
                source_snapshot = self.head
                bundle = reviewed_execution["artifact_bundle"]
                prefix = "operational-review/" + reviewed_execution["id"]
                materialized = {}

                def recover(artifact_ref: str, relative: str, *, expected_sha256: str | None = None,
                            expected_bytes: int | None = None) -> dict:
                    raw = self.store.read(artifact_ref, source_snapshot)
                    digest = hashlib.sha256(raw).hexdigest()
                    if expected_sha256 is not None and digest != expected_sha256:
                        raise ValueError("operational review artifact hash changed")
                    if expected_bytes is not None and len(raw) != expected_bytes:
                        raise ValueError("operational review artifact size changed")
                    logical = prefix + "/" + relative
                    materialized[logical] = raw
                    return {"artifact_ref": artifact_ref, "snapshot": source_snapshot,
                            "local_path": "input/" + logical, "sha256": digest, "bytes": len(raw)}

                normal_result_ref = f"runtime/artifacts/{bundle}/result.json"
                checkpoint_ref = f"runtime/artifacts/{bundle}/checkpoint-recovery.json"
                activity = self.runtime["activities"].get(reviewed_execution.get("activity_id"), {})
                activity_result_ref = activity.get("result_ref")
                if activity_result_ref:
                    selected_result_ref = activity_result_ref
                elif reviewed_execution.get("error") == "previous executor disappeared":
                    selected_result_ref = checkpoint_ref
                else:
                    selected_result_ref = normal_result_ref
                result_kind = ("execution_result" if selected_result_ref == normal_result_ref else
                               "checkpoint_recovery" if selected_result_ref == checkpoint_ref else
                               "activity_result")
                result_source = recover(selected_result_ref,
                    "result.json" if result_kind == "execution_result" else
                    "checkpoint-recovery.json" if result_kind == "checkpoint_recovery" else "activity-result.json")
                checkpoint_source = (result_source if selected_result_ref == checkpoint_ref else
                                     recover(checkpoint_ref, "checkpoint-recovery.json"))
                output_files = []
                for entry in reviewed_execution.get("output_files", []):
                    restored = recover(entry["artifact_ref"], "files/" + entry["path"],
                                       expected_sha256=entry.get("sha256"), expected_bytes=entry.get("bytes"))
                    output_files.append({**entry, **restored})
                materialize_inputs(workspace, materialized)
                context["recovery_materials"] = {"execution_id": reviewed_execution["id"],
                    "source_snapshot": source_snapshot,
                    "checkpoint": deepcopy(self.runtime.get("checkpoints", {}).get(target)),
                    "checkpoint_source": checkpoint_source, "result_source": result_source,
                    "result_kind": result_kind,
                    "final_result_status": "available" if result_kind == "execution_result" else "not_produced",
                    "output_files": output_files}
        if action["role"] == "intent_interpretation":
            context["user_request"] = next((r for r in self.runtime["inputs"] if r["id"] == target), None)
            context["interpretation_stage"] = action.get("stage", "interpret")
            context["interpretation_to_check"] = self.runtime.get("interpretations", {}).get(target)
        if task:
            previous = next((e for e in reversed(list(self.runtime["executions"].values()))
                             if e.get("action", {}).get("target") == target and e.get("role") in WORK_ROLES
                             and e.get("artifact_bundle") and e.get("output_files")), None)
            if previous:
                restored = []
                for entry in previous["output_files"]:
                    raw = self.store.read(entry["artifact_ref"], self.head)
                    path = directory / "previous-output" / entry["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
                    restored.append({**entry, "local_path": path.relative_to(workspace).as_posix()})
                context["previous_output_files"] = restored
                context["resume_checkpoint"] = self.runtime.get("checkpoints", {}).get(previous["id"])
        if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
            context.update(self._review_research_context(action, workspace))
        reviewed_action = self.runtime["executions"].get(target, {}).get("action", {}) if action["role"] == "operational_review" else action
        if reviewed_action.get("review_cycle_id"):
            for key in ("open_questions", "recent_history", "tasks"):
                context.pop(key, None)
        if action["role"] in {"research_preparation", "research_plan"}:
            context["config"] = deepcopy(self.instance["config"])
            context["recent_history"] = self._planning_history("research_plan", workspace)
            if action["role"] == "research_preparation":
                context["preparation_history"] = self._planning_history("research_preparation", workspace)
        return context

    def _planning_history(self, role: str, workspace: Path) -> list[dict]:
        """Keep rejected and incomplete submissions readable after later events."""
        history = []
        for execution in self.runtime["executions"].values():
            if execution.get("role") != role or execution.get("status") != "ended":
                continue
            row = {"execution_id": execution["id"], "role": role, "outcome": execution.get("outcome"),
                   "error": execution.get("error"), "action": deepcopy(execution.get("action", {}))}
            if execution.get("artifact_bundle"):
                activity = self.runtime["activities"].get(execution.get("activity_id"), {})
                reference = activity.get("result_ref") or f"runtime/artifacts/{execution['artifact_bundle']}/result.json"
                raw = self.store.read(reference, self.head)
                relative = f"planning-history/{execution['id']}.json"
                materialize_inputs(workspace, {relative: raw})
                row.update(artifact_ref=reference, local_path="input/" + relative,
                           sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            history.append(row)
        return history

    def _response_schema(self, action: dict) -> dict:
        if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
            return self._review_research_schema(action)
        if action["role"] == "identity_review" and action.get("review_cycle_id"):
            return self._review_schema(action)
        if action["role"] == "intent_interpretation":
            return governance.interpretation_schema(action.get("stage", "interpret"))
        result = schema_for(action["role"])
        if action["role"] in {"research_work", "supplemental_research"}:
            result["properties"]["knowledge"]["items"]["properties"]["kind"]["enum"] = [d["token"] for d in knowledge_io.catalog_definitions(self.instance)["knowledge"]]
        if action["role"] == "operational_review" and action.get("live"):
            result["properties"]["decision"]["enum"] = ["continue", "checkpoint", "revise", "wait", "stop"]
        return result

    def _available_inputs(self) -> list[str]:
        result = {"SKILL.md", "GLOSSARY.md", "context:goal", "context:policy"}
        if self.instance["config"].get("lean_command") or discover_lean():
            result.add("tool:lean")
        result.update(self.instance["knowledge"])
        result.update(self.runtime["tasks"])
        for source in self.instance["sources"]:
            result.update((source["path"], source["name"], "source:"+source["name"]))
            if source.get("id"): result.add(source["id"])
        return sorted(result)

    def _remove_action(self, action: dict) -> None:
        aid = action.get("id")
        self.runtime["queue"] = [a for a in self.runtime["queue"] if not (
            a.get("id") == aid if aid else a == action)]

    def _consume_action_events(self, action: dict, execution_id: str) -> None:
        consumed = set(action.get("event_refs", []))
        for event in self.runtime.get("events", []):
            if event["id"] in consumed:
                event.update(consumed_by=execution_id, consumed_at=now())
                if event["kind"] == "task_new_input" and event.get("target") in self.runtime["tasks"]:
                    self.runtime["tasks"][event["target"]]["newinput"] = False
        self.runtime["pending_events"] = [eid for eid in self.runtime.get("pending_events", []) if eid not in consumed]

    def _read_extensions(self, workspace: Path) -> dict:
        path = workspace / "activity-extensions.json"
        if not path.exists():
            return {}
        if path.is_symlink() or not path.resolve().is_relative_to(workspace.resolve()):
            raise ValueError("extensions must stay in the execution workspace")
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        allowed = {"task_conditions", "research_insights", "external_requests", "knowledge_changes", "knowledge_metadata", "relations", "observation_rules", "research_requests", "academic_resolutions"}
        if not isinstance(value, dict) or set(value) - allowed or any(not isinstance(v, list) for v in value.values()):
            raise ValueError("invalid activity extension families")
        return value

    def _observe_running(self, execution_id: str, tracker: ObservationTracker, event: dict, deadline: float) -> None:
        self._controls()
        if self._check_conversations(): self._save()
        for observed in tracker.observe(event):
            if observed["kind"] == "observation_rules":
                bundle = new_id("BA")
                ref = f"runtime/artifacts/{bundle}/observation-rules.json"
                self.runtime.setdefault("observation_rules", {})[execution_id] = {k: v for k, v in observed.items() if k != "raw"}
                self._save({ref: observed["raw"]})
            elif observed["kind"] == "checkpoint":
                bundle = new_id("BA")
                ref = f"runtime/artifacts/{bundle}/checkpoint.json"
                self.runtime.setdefault("checkpoints", {})[execution_id] = {
                    "kind": "worker_checkpoint", "value": observed["value"], "sha256": observed["sha256"],
                    "artifact_ref": ref, "observed_at": observed["observed_at"]}
                self._save({ref: observed["raw"]})
            elif observed["kind"] == "operational_review_due":
                self.runtime.setdefault("observations", {})[execution_id] = json_safe(observed)
                self._save()
                if not self._inline_reviewing and self.runtime["status"] not in {"paused", "closed"}:
                    self._run_inline_review(execution_id, observed, deadline)

    def _run_inline_review(self, parent_id: str, observation: dict, deadline: float) -> None:
        config = self.instance["config"]
        if sum(e.get("budget_kind") == "operations" for e in self.runtime["executions"].values()) >= config["operations_calls"]:
            self.runtime["executions"][parent_id]["stop_requested"] = "operating_budget_unavailable"
            return
        action = {"id": new_id("AC"), "role": "operational_review", "target": parent_id,
                  "live": True, "observation": json_safe(observation)}
        authority = governance.authorize(self.instance, action)
        if not authority["allowed"]:
            self.runtime["executions"][parent_id]["stop_requested"] = "operating_authority_unavailable"
            return
        eid, aid = new_id("EX"), new_id("AY")
        base = Path(self.instance["workspace"]) / "runs" / eid
        workspace = base / "workspace"
        workspace.mkdir(parents=True)
        context = self._context(action, workspace)
        schema = self._response_schema(action)
        overhead = len(self._render_prompt(action["role"], {}, output_schema=schema).encode()) + 2048
        fitted = fit_context(context, max_bytes=max(1, config["max_input_bytes"]-overhead), workspace=workspace,
            mandatory_keys=[key for key in ("goal", "action", "execution_to_review", "observation") if key in context])
        prompt = self._render_prompt(action["role"], fitted["context"], output_schema=schema)
        if fitted["overflow"] or len(prompt.encode()) > config["max_input_bytes"]:
            self.runtime["executions"][parent_id]["stop_requested"] = "operating_review_input_overflow"
            return
        input_bundle = new_id("BA")
        execution = {"id": eid, "activity_id": aid, "parent_execution_id": parent_id, "role": action["role"],
                     "action": action, "budget_kind": "operations", "status": "starting", "created_at": now(),
                     "model": config["role_models"].get("operational_review", config["model"]), "effort": config["effort"],
                     "grant_id": authority["grant_id"], "engine_sha256": ENGINE_SHA256,
                     "input_snapshot": self.head, "input_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                     "input_bundle": input_bundle}
        self.runtime["executions"][eid] = execution
        self.runtime["activities"][aid] = {"id": aid, "role": action["role"], "status": "active", "execution_ids": [eid]}
        self._live_execution_ids.add(eid)
        self._inline_reviewing = True
        self._save(self._input_artifacts(input_bundle, action["role"], prompt, schema, fitted))
        def started(identity):
            self.runtime["executions"][eid].update(status="running", process=json_safe(identity))
            self._save()
        def stop():
            self._controls()
            if self._check_conversations(): self._save()
            return (self.runtime["status"] in {"paused", "closed"} or self.runtime.get("stop_requested") or
                    not governance.authorize(self.instance, action)["allowed"] or time.monotonic() >= deadline)
        try:
            result = self.runner.run(prompt=prompt, output_schema=schema, workspace=workspace,
                evidence_dir=base / "evidence", model=execution["model"],
                effort=execution["effort"], timeout_seconds=max(.1, min(config["call_timeout_seconds"], deadline-time.monotonic())),
                should_stop=stop, on_started=started)
        except Exception as error:
            result = {"status": "failed", "error": str(error), "output": None, "usage": {}}
        finally:
            self._inline_reviewing = False
            self._live_execution_ids.discard(eid)
        bundle = new_id("BA")
        result = json_safe(result)
        if result["status"] == "completed":
            try:
                jsonschema.validate(result["output"], schema)
                if not governance.authorize(self.instance, action)["allowed"]:
                    raise ValueError("operating authority changed before acceptance")
            except (jsonschema.ValidationError, ValueError) as error:
                result.update(status="failed", error=str(error))
        execution = self.runtime["executions"][eid]
        execution.update(status="ended", ended_at=now(), artifact_bundle=bundle,
                         outcome="output_accepted" if result["status"] == "completed" else "execution_incomplete",
                         error=result.get("error"), usage=result.get("usage", {}))
        self.runtime["activities"][aid].update(status="finished" if result["status"] == "completed" else "unresolved",
                                               result_ref=f"runtime/artifacts/{bundle}/result.json")
        if result["status"] == "completed":
            decision = result["output"]["decision"]
            self.runtime.setdefault("observations", {}).setdefault(parent_id, {})["operational_decision"] = result["output"]
            if decision == "checkpoint":
                parent_workspace = Path(self.instance["workspace"]) / "runs" / parent_id / "workspace"
                (parent_workspace / "observation-feedback.json").write_bytes(canonical_json(result["output"]))
            elif decision in {"revise", "wait", "stop"}:
                parent = self.runtime["executions"][parent_id]
                parent["stop_requested"] = "operational_" + decision
                parent["after_stop"] = {"decision": decision, "reason": result["output"]["reason"]}
        else:
            # A deterministic bound still works if the operating model is unavailable.
            self.runtime["executions"][parent_id]["stop_requested"] = "operating_review_unavailable"
        files = collect_outputs(workspace, max_bytes=config["max_artifact_bytes"])
        artifacts = {f"runtime/artifacts/{bundle}/result.json": canonical_json(result),
                     f"runtime/artifacts/{bundle}/output-manifest.json": canonical_json(files["manifest"]),
                     f"runtime/artifacts/{bundle}/omitted.json": canonical_json(files["omitted"])}
        execution["output_files"] = []
        for path, raw in files["files"].items():
            ref = f"runtime/artifacts/{bundle}/files/{path}"
            artifacts[ref] = raw
            execution["output_files"].append({"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        self._save(artifacts)

    def _call(self, action: dict, deadline: float) -> bool:
        action.setdefault("id", new_id("AC"))
        action = deepcopy(action)
        role = action["role"]
        if role == "goal_audit" and action.get("basis") != self._goal_basis_key():
            for judgment in self.instance["goal_judgments"]:
                if judgment["basis"] == action.get("basis"): judgment["current"] = False
            self.runtime["queue"] = [a for a in self.runtime["queue"] if not (a["role"] == "goal_audit" and a.get("basis") == action.get("basis"))]
            self._enqueue("research_plan", reason="Goal audit inputs changed before the complete independent group finished")
            self._save()
            return True
        pool = "work" if role in WORK_ROLES else "operations"
        config = self.instance["config"]
        used = sum(e.get("budget_kind") == pool for e in self.runtime["executions"].values())
        if used >= config[pool + "_calls"]:
            self.runtime["status"] = "budget_exhausted"
            self._save()
            return False
        authority = governance.authorize(self.instance, action)
        if not authority["allowed"]:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": action, "reason": authority["reason"]}
            self._remove_action(action)
            if action.get("target") in self.runtime["tasks"]:
                self.runtime["tasks"][action["target"]]["status"] = "waiting"
            self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            self._save()
            return bool(self.runtime["queue"])
        if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id"):
            check_task = deepcopy(self.runtime["tasks"][action["target"]])
            check_task["status"] = "ready"
            ready = planning.task_ready(check_task, self.instance, self.runtime)
            if ready["state"] != "ready":
                self.runtime["tasks"][action["target"]]["status"] = "waiting"
                self.runtime["tasks"][action["target"]]["readiness_error"] = ready
                self._remove_action(action)
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
                self._save()
                return bool(self.runtime["queue"])
        execution_id, activity_id = new_id("EX"), new_id("AY")
        base = Path(self.instance["workspace"]) / "runs" / execution_id
        workspace = base / "workspace"
        workspace.mkdir(parents=True)
        self.instance["available_input_refs"] = self._available_inputs()
        context = self._context(action, workspace)
        schema = self._response_schema(action)
        overhead = len(self._render_prompt(role, {}, output_schema=schema).encode()) + 2048
        mandatory = [key for key in ("goal", "goal_kind", "policies", "action", "task", "proposal", "role_review", "user_request", "interpretation_to_check") if key in context]
        fitted = fit_context(context, max_bytes=max(1, config["max_input_bytes"]-overhead), workspace=workspace, mandatory_keys=mandatory)
        prompt = self._render_prompt(role, fitted["context"], output_schema=schema)
        if fitted["overflow"] or len(prompt.encode()) > config["max_input_bytes"]:
            detail = fitted["overflow"] or {"reason": "rendered_prompt_exceeds_limit", "actual_bytes": len(prompt.encode())}
            self.runtime.setdefault("input_overflows", []).append({"action": action, "detail": detail, "source_catalog": fitted["manifest"]})
            self._remove_action(action)
            if role == "identity_review":
                self.instance["knowledge"][action["target"]]["status"] = "needs_reconstruction"
                self._enqueue("research_preparation", reason="Split the oversized proposal into independently verifiable results", reconstruction_target=action["target"])
                self.runtime["status"] = "ready"
            else:
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": action, "reason": "input_overflow", "detail": detail}
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
                self.runtime["questions"].append(f"Required input for {role} exceeds the selected model input limit; source files are preserved.")
            self._save()
            return self.runtime["status"] == "ready"
        input_bundle = new_id("BA")
        basis_ids = []
        source_refs = None
        if action.get("target") in self.runtime["tasks"]:
            task = self.runtime["tasks"][action["target"]]
            source_refs = task.get("inputs", [])
            basis_ids = [k for k in {*task.get("dependencies", []), *task.get("reuse", []), *task.get("inputs", [])} if k in self.instance["knowledge"]]
        elif action.get("target") in self.instance["knowledge"]:
            proposal = self.instance["knowledge"][action["target"]]
            basis_ids = [k for k in proposal.get("dependencies", []) if k in self.instance["knowledge"]]
        elif role == "goal_audit":
            if action["basis"] != self._goal_basis_key():
                raise ValueError("goal audit inputs changed before acceptance")
            basis_ids = [k["id"] for k in self.instance["knowledge"].values() if knowledge.assess_use(k, self.instance)["valid"]]
        execution = {"id": execution_id, "activity_id": activity_id, "role": role, "action": action,
                     "budget_kind": pool, "status": "starting", "created_at": now(), "input_snapshot": self.head,
                     "input_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_bundle": input_bundle,
                     "model": config["role_models"].get(role, config["model"]), "effort": config["effort"],
                     "engine_sha256": ENGINE_SHA256, "grant_id": authority["grant_id"],
                     "goal_revision": self.instance.get("goal_revision", 1), "policy_revision": self.instance.get("policy_revision", 1),
                     "validity_basis": knowledge.capture_basis(self.instance, self.runtime, basis_ids),
                     "source_basis": capture_sources(self.instance, source_refs),
                     "input_reductions": fitted["reductions"]}
        if action.get("target") in self.runtime["tasks"]:
            execution["contract_sha256"] = planning.contract_hash(self.runtime["tasks"][action["target"]])
            if self.runtime["tasks"][action["target"]].get("academic_requirement_id"):
                execution["academic_requirements_sha256"] = self.instance["academic_requirements"]["sha256"]
        self.runtime["executions"][execution_id] = execution
        self.runtime["activities"][activity_id] = {"id": activity_id, "role": role, "status": "active", "execution_ids": [execution_id]}
        self.runtime["active_execution"] = execution_id
        self._live_execution_ids.add(execution_id)
        self.runtime["status"] = "running"
        if role == "identity_review" and action.get("review_cycle_id"):
            self._record_review_input(action, execution_id)
        self._save(self._input_artifacts(input_bundle, role, prompt, schema, fitted))
        task = self.runtime["tasks"].get(action.get("target"), {})
        rules = self.runtime.get("task_observation_rules", {}).get(action.get("target"), task.get("initial_observation_rules", []))
        tracker = ObservationTracker(execution_id, workspace, {**config, "observation_rules": rules})
        stop_started = None
        # Work-budget executions (research, review, audit) carry no per-execution
        # deadline; they end by submission, stop conditions or the run deadline.
        call_deadline = deadline if pool == "work" else min(deadline, time.monotonic()+config["call_timeout_seconds"])
        def started(identity):
            self.runtime["executions"][execution_id].update(status="running", process=json_safe(identity))
            self._save()
        def should_stop():
            nonlocal stop_started
            self._controls()
            if self._check_conversations(): self._save()
            current = self.runtime["executions"][execution_id]
            allowed = governance.authorize(self.instance, action)["allowed"]
            changed = (current["goal_revision"] != self.instance.get("goal_revision", 1) or
                       current["policy_revision"] != self.instance.get("policy_revision", 1))
            if not knowledge.validate_basis(current.get("validity_basis", []), self.instance, self.runtime)["valid"]:
                changed = True
            if not sources_current(current.get("source_basis", []), self.instance): changed = True
            if current.get("academic_requirements_sha256") and current["academic_requirements_sha256"] != self.instance.get("academic_requirements", {}).get("sha256"):
                changed = True
            if current.get("contract_sha256") and action.get("target") in self.runtime["tasks"]:
                target_task = self.runtime["tasks"][action["target"]]
                changed = changed or planning.contract_hash(target_task) != current["contract_sha256"] or target_task["status"] == "closed"
            requested = (self.runtime["status"] in {"paused", "closed"} or self.runtime.get("stop_requested")
                         or current.get("stop_requested") or not allowed or changed or time.monotonic() >= call_deadline)
            if not requested:
                return False
            reason = current.get("stop_requested") or ("authority_changed" if not allowed or changed else "user_or_deadline_stop")
            immediate = not allowed or time.monotonic() >= call_deadline or self.runtime["status"] == "closed"
            if stop_started is None:
                stop_started = time.monotonic()
                current["stop_reason"] = reason
                request_checkpoint(workspace, str(reason), immediate=immediate,
                    deadline=(datetime.now(timezone.utc)+timedelta(seconds=0 if immediate else config["checkpoint_grace_seconds"])).isoformat())
            return immediate or time.monotonic()-stop_started >= config["checkpoint_grace_seconds"]
        arguments = dict(prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=base/"evidence",
                         model=execution["model"], effort=execution["effort"],
                         timeout_seconds=max(.1, call_deadline-time.monotonic()), should_stop=should_stop, on_started=started)
        params = inspect.signature(self.runner.run).parameters
        if "on_observation" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
            arguments["on_observation"] = lambda event: self._observe_running(execution_id, tracker, event, deadline)
        try:
            result = self.runner.run(**arguments)
        except Exception as error:
            result = {"status": "failed", "output": None, "usage": {}, "error": f"{type(error).__name__}: {error}"}
        self._live_execution_ids.discard(execution_id)
        result = json_safe(result)
        if result["status"] == "completed" and stop_started is not None and (
                self.runtime["executions"][execution_id].get("after_stop") or self.runtime["status"] == "paused"):
            # The stop request already revoked general authority; keep the late output only as preserved evidence.
            result = {**result, "status": "stopped",
                      "error": "final output was collected after a pause or operational stop request; preserved without acceptance"}
        bundle = new_id("BA")
        files = collect_outputs(workspace, max_bytes=config["max_artifact_bytes"])
        artifacts = {f"runtime/artifacts/{bundle}/result.json": canonical_json(result),
                     f"runtime/artifacts/{bundle}/output-manifest.json": canonical_json(files["manifest"]),
                     f"runtime/artifacts/{bundle}/omitted.json": canonical_json(files["omitted"])}
        output_files = []
        for path, raw in files["files"].items():
            ref = f"runtime/artifacts/{bundle}/files/{path}"
            artifacts[ref] = raw
            output_files.append({"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        if result.get("output") is not None:
            artifacts[f"runtime/artifacts/{bundle}/output.json"] = canonical_json(result["output"])
        checkpoint = json_safe(recovered_checkpoint(workspace, tracker.messages))
        observed = self.runtime.get("checkpoints", {}).get(execution_id)
        if checkpoint["kind"] != "worker_checkpoint" and isinstance(observed, dict) and observed.get("kind") == "worker_checkpoint":
            # An unreadable final checkpoint file never replaces the last valid checkpoint observed during execution.
            checkpoint = {**observed, "final_observation": checkpoint}
        self.runtime.setdefault("checkpoints", {})[execution_id] = checkpoint
        artifacts[f"runtime/artifacts/{bundle}/checkpoint-recovery.json"] = canonical_json(checkpoint)
        execution = self.runtime["executions"][execution_id]
        execution.update(status="ended", ended_at=now(), usage=result.get("usage", {}), artifact_bundle=bundle,
                         output_files=output_files, outputs_complete=files["complete"],
                         outcome="output_accepted" if result["status"] == "completed" else "execution_incomplete", error=result.get("error"))
        self.runtime["active_execution"] = None
        self.runtime["activities"][activity_id].update(status="finished" if result["status"] == "completed" else "unresolved",
                                                      result_ref=f"runtime/artifacts/{bundle}/result.json")
        previous_instance, previous_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        if self.runtime["status"] == "closed":
            self.runtime["executions"][execution_id]["outcome"] = "output_preserved_after_close"
            self.runtime["queue"] = []
        elif result["status"] == "completed":
            try:
                jsonschema.validate(result["output"], schema)
                if not files["complete"]:
                    raise ValueError("required execution artifacts could not be preserved")
                if execution["goal_revision"] != self.instance.get("goal_revision", 1) or execution["policy_revision"] != self.instance.get("policy_revision", 1):
                    raise ValueError("decision input changed during execution")
                if execution.get("contract_sha256") and planning.contract_hash(self.runtime["tasks"][action["target"]]) != execution["contract_sha256"]:
                    raise ValueError("task contract changed during execution")
                if not knowledge.validate_basis(execution["validity_basis"], self.instance, self.runtime)["valid"]:
                    raise ValueError("a decision dependency changed during execution")
                if not sources_current(execution["source_basis"], self.instance):
                    raise ValueError("required source content changed during execution")
                if execution.get("academic_requirements_sha256") and execution["academic_requirements_sha256"] != self.instance.get("academic_requirements", {}).get("sha256"):
                    raise ValueError("academic requirements changed during execution")
                if not governance.authorize(self.instance, action)["allowed"]:
                    raise ValueError("execution authority was revoked before result acceptance")
                execution["extensions"] = self._read_extensions(workspace)
                self._remove_action(action)
                if not self._defer_review_for_research(action, result["output"], execution_id):
                    self._apply(action, result["output"], execution_id)
                self._apply_extensions(action, execution_id)
                self._ensure_academic_followup()
                self._consume_action_events(action, execution_id)
                self.runtime["questions"] = [q for q in self.runtime["questions"] if not (q.startswith(f"Invalid output for {role}:") or q.startswith(f"{role} did not finish:"))]
                self.runtime["history"].append({"role": role, "execution_id": execution_id, "summary": result["output"]["summary"]})
                if self.runtime["status"] == "running": self.runtime["status"] = "ready"
            except Exception as error:
                self.instance, self.runtime = previous_instance, previous_runtime
                self.runtime["executions"][execution_id].update(outcome="execution_incomplete", error=f"output validation: {error}")
                self.runtime["activities"][activity_id]["status"] = "unresolved"
                self._remove_action(action)
                held_status = self.runtime["status"] if self.runtime["status"] in {"paused", "closed"} else None
                if action.get("repair_attempt", 0) < config.get("max_output_repairs", 1):
                    self.runtime["queue"].insert(0, {**action, "repair_attempt": action.get("repair_attempt", 0)+1,
                        "repair": {"error": str(error), "previous_output": result["output"]}})
                    self.runtime["status"] = "ready"
                else:
                    self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": action, "reason": str(error)}
                    self.runtime["status"] = "paused"
                    self.runtime["questions"].append(f"Invalid output for {role}: {error}")
                if held_status:
                    self.runtime["status"] = held_status
                    if held_status == "closed": self.runtime["queue"] = []
        else:
            after = execution.get("after_stop")
            if after:
                held_pause = self.runtime["status"] == "paused"
                self._remove_action(action)
                self._abandon_review_research(action, execution_id, after["reason"])
                if action.get("target") in self.runtime["tasks"]:
                    self.runtime["tasks"][action["target"]]["status"] = "needs_revision" if after["decision"] == "revise" else "waiting"
                if after["decision"] == "revise": self._enqueue("research_preparation", reason=after["reason"])
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
                if held_pause or after["decision"] == "stop": self.runtime["status"] = "paused"
            elif result["status"] == "failed" and role != "operational_review" and action.get("recovery_attempt", 0) < 1 and self.runtime["status"] != "closed":
                # A pause applied while this execution was stopping stays in force; the diagnosis runs after resume.
                if self.runtime["status"] != "paused":
                    self.runtime["status"] = "ready"
                self.runtime["queue"].insert(0, {"id": new_id("AC"), "role": "operational_review", "target": execution_id,
                                               "reason": "Diagnose the preserved failure before selecting recovery"})
            elif self.runtime["status"] not in {"closed", "paused"}:
                self.runtime["status"] = "paused"
            self.runtime["questions"].append(f"{role} did not finish: {result.get('error')}; partial files and checkpoint are preserved.")
        self._save(artifacts)
        self._controls()
        if self.runtime["status"] not in {"paused", "closed", "completed"}:
            self._refresh_readiness()
            self._save()
        return self.runtime["status"] in {"ready", "running"}

    def _enqueue(self, role: str, target: str | None = None, **extra: Any) -> None:
        action = {"role": role, **extra}
        if target is not None:
            action["target"] = target
        compare_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis", "transition_id")
        live_actions = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] in {"starting", "running"}}
        for queued in self.runtime["queue"]:
            if queued.get("id") not in live_actions and all(queued.get(k) == action.get(k) for k in compare_keys):
                if action.get("event_refs"):
                    queued["event_refs"] = list(dict.fromkeys([*queued.get("event_refs", []), *action["event_refs"]]))
                return
        action.setdefault("id", new_id("AC"))
        self.runtime["queue"].append(action)

    def _apply_extensions(self, action: dict, execution_id: str) -> None:
        extension = self.runtime["executions"][execution_id].get("extensions", {})
        self._apply_academic_resolutions(action, execution_id, extension.get("academic_resolutions", []))
        for relation in extension.get("relations", []):
            self.instance, _ = knowledge_io.import_relation(self.instance, relation, source_ref=execution_id, actor_ref=execution_id)
        if extension.get("observation_rules"):
            rules = validate_rules(extension["observation_rules"])
            if action.get("target") not in self.runtime["tasks"]:
                raise ValueError("persisted observation rules require a task target; live rules belong in observation-rules.json")
            self.runtime.setdefault("task_observation_rules", {})[action["target"]] = deepcopy(rules)
        if extension.get("knowledge_changes"):
            if action["role"] not in {"research_preparation", "research_work", "supplemental_research"}:
                raise ValueError("this role may report a defect but cannot author a knowledge revision")
            for change in extension["knowledge_changes"]:
                kid = change["id"]
                previous_cycle = self.instance["knowledge"][kid].get("review_cycle_id")
                cycle = self.runtime.get("review_cycles", {}).get(previous_cycle)
                if cycle and cycle["status"] == "working":
                    # A sealed proposal must not change under an open review: close that review
                    # as unresolved before the revised proposal starts its own review.
                    cycle.update(status="unresolved", decision="unresolved", phase="ended")
                    cycle.setdefault("history", []).append({"event": "worker_knowledge_change", "source_ref": execution_id, "reason": change["reason"]})
                    for investigation in cycle.get("research", {}).values():
                        if investigation.get("status") == "pending":
                            investigation.update(status="cancelled", cancellation={"source_ref": execution_id, "reason": change["reason"]})
                    cycle["deferred_actions"] = {}
                self.instance, self.runtime = knowledge.revise_knowledge(self.instance, self.runtime, kid,
                    change["changes"], reason=change["reason"], actor_ref=execution_id)
                item = self.instance["knowledge"][kid]
                item["previous_review_cycle_id"] = previous_cycle
                item.pop("review_cycle_id", None)
                if isinstance(item.get("identity_assessment"), dict):
                    item["identity_assessment"]["effective"] = False
                    item["identity_assessment"]["reason"] = "Knowledge revision awaits a fresh full review"
                self.runtime["queue"] = [a for a in self.runtime["queue"] if not (a.get("target") == kid and
                    (a.get("role") in {"identity_review", "formal_check"} or (a.get("role") == "supplemental_research" and a.get("review_cycle_id"))))]
                if item.get("lean_code"):
                    self._enqueue("formal_check", kid)
            self._invalidate_goal_currentness()
        for index, request in enumerate(extension.get("external_requests", [])):
            task = self.runtime["tasks"].get(action.get("target"), {})
            academic_effect = request.get("academic_effect_id")
            if academic_effect:
                required = next((effect for effect in task.get("required_external_effects", []) if effect["id"] == academic_effect), None)
                if required is None: raise ValueError("external request names no academic effect in this task")
                if required.get("grant_id") and required["grant_id"] != request.get("grant_id"):
                    raise ValueError("academic effect requires its specified grant")
            if not request.get("grant_id"):
                self.runtime.setdefault("permission_requests", []).append({"execution_id": execution_id, **request})
                self.runtime["questions"].append("External action requires a user grant: " + request.get("purpose", ""))
                continue
            logical_ref = action["id"] + ":external:" + str(request.get("id", index))
            operation_id = "EO-" + hashlib.sha256(logical_ref.encode()).hexdigest()[:24]
            self._external_control({"operation": "prepare", "request": request["request"], "grant_id": request["grant_id"],
                                    "id": operation_id}, logical_ref)
            entry = self.runtime["external_operations"][operation_id]
            entry["producer_executions"] = list(dict.fromkeys([*entry.get("producer_executions", []), execution_id]))
            if academic_effect:
                entry["academic_binding"] = {"task_id": task["id"], "requirement_id": task["academic_requirement_id"],
                    "requirements_sha256": task["requirements_sha256"], "solution_basis": deepcopy(task["solution_basis"]),
                    "effect_id": academic_effect}
            pending_external = [a for a in self.runtime["queue"] if a["role"] == "external_action" and a.get("target") == operation_id]
            self.runtime["queue"] = pending_external + [a for a in self.runtime["queue"] if a not in pending_external]
        insights = extension.get("research_insights", [])
        if action.get("review_cycle_id"):
            cycle_id = action["review_cycle_id"]
            self.runtime.setdefault("private_insights", {}).setdefault(cycle_id, []).extend(
                {"source_execution": execution_id, **insight} for insight in insights)
            cycle = self.runtime["review_cycles"][cycle_id]
            if cycle["status"] not in {"completed", "unresolved"}:
                return
            insights = self.runtime["private_insights"].pop(cycle_id, [])
        for insight in insights:
            if not all(isinstance(insight.get(k), str) and insight[k].strip() for k in ("kind", "title", "statement", "summary")):
                raise ValueError("an incidental insight must state its kind, title, claim and summary")
            kid = new_id("KN")
            self.instance["knowledge"][kid] = {"id": kid, "revision": 1, "kind": insight["kind"],
                "title": insight["title"], "statement": insight["statement"], "summary": insight["summary"],
                "explanation": insight.get("explanation", insight["statement"]), "status": "candidate",
                "information_state": insight.get("information_state", "hypothesis"), "lean_code": "",
                "declaration_names": [], "dependencies": insight.get("evidence_ids", []), "reviews": [],
                "required_reviews": self.instance["config"]["reviewers"], "created_at": now(),
                "producer_execution": insight.get("source_execution", execution_id)}
        if insights:
            self._enqueue("research_plan", reason="Incidental research knowledge is now available")

    def _apply(self, action: dict, output: dict, execution_id: str) -> None:
        role, target = action["role"], action.get("target")
        if not action.get("review_cycle_id"):
            self.runtime["questions"].extend(q for q in output["questions"] if q not in self.runtime["questions"])
        if role == "supplemental_research" and action.get("review_cycle_id"):
            self._apply_review_research(action, output, execution_id)
        elif role == "research_preparation":
            self.runtime["cycles"] += 1
            titles = {}
            for proposal in output["candidates"]:
                if any(not proposal[key].strip() for key in ("title", "question", "scope", "expected_result")):
                    raise ValueError("a task requires a title, question, scope and expected result")
                criteria = proposal["completion_criteria"]
                if not criteria or any(not c.strip() for c in criteria) or len(criteria) != len(set(criteria)):
                    raise ValueError("completion criteria must be nonempty, distinct and assessable")
                tid = proposal["revises_task_id"] or new_id("TK")
                old = self.runtime["tasks"].get(tid)
                if proposal["revises_task_id"] and (old is None or old["status"] in {"completed", "closed", "performing"}):
                    raise ValueError("revision must identify an existing unfinished task")
                if old:
                    # Preserve unfinished obligations while independently reviewing
                    # the new wording and additional criteria of the same task.
                    criteria = list(dict.fromkeys([*old["completion_criteria"], *criteria]))
                    proposal = {**proposal, "completion_criteria": criteria}
                    self.runtime.get("task_observation_rules", {}).pop(tid, None)
                self.runtime["tasks"][tid] = {**proposal, "id": tid, "revision": (old["revision"]+1 if old else 1),
                                              "status": "planned", "producer_execution": execution_id,
                                              "results": old.get("results", []) if old else [], "reviews": [],
                                              "occurrence_condition": {"op": "always"}, "dependencies": [],
                                              "initial_observation_rules": deepcopy(old.get("initial_observation_rules", [])) if old else [],
                                              "revision_history": [*old.get("revision_history", []),
                                                  {k: v for k, v in old.items() if k != "revision_history"}] if old else []}
                if proposal["title"] in titles:
                    raise ValueError("task titles must be unique within a preparation result")
                titles[proposal["title"]] = tid
                self._enqueue("task_contract_review", tid)
            for specification in self.runtime["executions"][execution_id].get("extensions", {}).get("task_conditions", []):
                tid = titles.get(specification.get("task_title"), specification.get("task_id"))
                if tid not in titles.values():
                    raise ValueError("task condition must identify a prepared task")
                condition = deepcopy(specification.get("occurrence_condition", {"op": "always"}))
                def bind_names(node):
                    if isinstance(node, dict):
                        for name in ("record_id", "task_id", "from_id", "to_id"):
                            if node.get(name) in titles: node[name] = titles[node[name]]
                        for value in node.values(): bind_names(value)
                    elif isinstance(node, list):
                        for value in node: bind_names(value)
                bind_names(condition)
                dependencies = [titles.get(d, d) for d in specification.get("dependencies", [])]
                task_conditions = [{"op": "task_disposition_is", "task_id": d, "value": "completed"}
                                   for d in dependencies if d in self.runtime["tasks"]]
                if task_conditions:
                    condition = {"op": "all", "args": [condition, *task_conditions]}
                evaluated = planning.evaluate_condition(condition, self.instance, self.runtime)
                if evaluated["state"] == "evaluation_error":
                    raise ValueError("invalid task occurrence condition: " + "; ".join(evaluated["errors"]))
                self.runtime["tasks"][tid].update(occurrence_condition=condition, dependencies=dependencies)
                if "observation_rules" in specification:
                    self.runtime["tasks"][tid]["initial_observation_rules"] = deepcopy(validate_rules(specification["observation_rules"]))
            available = set(self._available_inputs())
            for tid in titles.values():
                task = self.runtime["tasks"][tid]
                task["inputs"] = [titles.get(ref, ref) for ref in task["inputs"]]
                task["reuse"] = [titles.get(ref, ref) for ref in task["reuse"]]
                unknown = {ref for ref in (set(task["inputs"]) | set(task["reuse"])) - available if not ref.startswith("source:")}
                if unknown:
                    raise ValueError("task inputs must copy available source refs; unknown: " + ", ".join(sorted(unknown)))
                basis = {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                         "goal_revision": self.instance.get("goal_revision", 1), "policy_revision": self.instance.get("policy_revision", 1)}
                for pending in self.runtime["queue"]:
                    if pending["role"] == "task_contract_review" and pending.get("target") == tid:
                        pending["contract_basis"] = basis
            self._enqueue("research_plan")
        elif role == "task_contract_review":
            task = self.runtime["tasks"][target]
            if task["producer_execution"] == execution_id:
                raise ValueError("contract author cannot review its own contract")
            basis = action.get("contract_basis", {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                "goal_revision": self.instance.get("goal_revision", 1), "policy_revision": self.instance.get("policy_revision", 1)})
            if basis["contract_sha256"] != planning.contract_hash(task):
                raise ValueError("contract changed while being reviewed")
            task["reviews"].append({"id": new_id("CR"), "execution_id": execution_id, **basis, **output})
            task["status"] = "planned" if output["decision"] == "approved" else "needs_revision"
            if output["decision"] != "approved":
                # The unapproved contract's defects and open questions go back to preparation.
                self._enqueue("research_preparation", target,
                              reason="Task contract review returned " + output["decision"] + "; revise the contract from its findings or preserve the obligation with the open questions",
                              contract_review_execution=execution_id)
        elif role == "research_plan":
            self._apply_plan(output, execution_id)
        elif role in {"research_work", "supplemental_research"}:
            if not output["report"].strip():
                raise ValueError("work must report its actual scope, outcome and remaining work")
            task = self.runtime["tasks"][target]
            task["results"].append({"execution_id": execution_id, **output,
                                    "output_files": deepcopy(self.runtime["executions"][execution_id].get("output_files", []))})
            task["status"] = "waiting" if output["outcome"] == "waiting" else "assessing"
            task["remaining_work"] = output["remaining_work"]
            new_items = {}
            metadata_entries = self.runtime["executions"][execution_id].get("extensions", {}).get("knowledge_metadata", [])
            metadata = {entry["title"]: entry for entry in metadata_entries}
            if len(metadata) != len(metadata_entries) or set(metadata) - {item["title"] for item in output["knowledge"]}:
                raise ValueError("knowledge_metadata titles must be distinct and match new knowledge titles in this output")
            for item in output["knowledge"]:
                extra = metadata.get(item["title"], {})
                if set(extra) - {"title", "relation_claim", "confirmed_scope", "epistemic_status", "selection_relevance", "uncertainty_assessment"}:
                    raise ValueError("unknown knowledge metadata")
                item = {**item, **extra}
                kid = new_id("KN")
                record = {**item, "id": kid, "revision": 1, "status": "candidate", "producer_execution": execution_id,
                          "source_basis": deepcopy(self.runtime["executions"][execution_id].get("source_basis", [])),
                          "task_id": target, "created_at": now(), "reviews": [],
                          "required_reviews": self.instance["config"]["reviewers"]}
                self.instance["knowledge"][kid] = record
                if record.get("relation_claim"):
                    claim = record["relation_claim"]
                    if not isinstance(claim, dict) or set(claim) != {"kind", "source", "target", "confirmed_scope"}:
                        raise ValueError("relation_claim needs kind, source, target and confirmed_scope")
                    record["relation_endpoint_basis"] = knowledge.capture_basis(self.instance, self.runtime, list(dict.fromkeys([claim["source"], claim["target"]])))
                if item["title"] in new_items:
                    raise ValueError("knowledge titles must be unique within one output")
                new_items[item["title"]] = kid
                if item["lean_code"]:
                    if not item["declaration_names"]:
                        raise ValueError("Lean proposal requires declaration_names")
                    self._enqueue("formal_check", kid)
            for kid in new_items.values():
                record = self.instance["knowledge"][kid]
                record["dependencies"] = [new_items.get(ref, ref) for ref in record.get("dependencies", [])]
                if kid in record["dependencies"] or any(ref not in self.instance["knowledge"] for ref in record["dependencies"]):
                    raise ValueError("knowledge dependencies must identify other knowledge records or this output's titles")
            for relation in output["relations"]:
                source = new_items.get(relation["source"], relation["source"])
                destination = new_items.get(relation["target"], relation["target"])
                if source not in self.instance["knowledge"] or destination not in self.instance["knowledge"]:
                    raise ValueError("relation endpoints must identify existing knowledge or this output's titles")
                self.instance, _ = knowledge_io.import_relation(self.instance, {**relation, "source": source, "target": destination},
                                                                source_ref=execution_id, actor_ref=execution_id)
            self._enqueue("research_plan")
        elif role == "identity_review" and action.get("review_cycle_id"):
            self._apply_identity_review(action, output, execution_id)
        elif role == "identity_review":
            item = self.instance["knowledge"][target]
            if action["slot"] in {r["slot"] for r in item["reviews"]} or execution_id == item["producer_execution"]:
                raise ValueError("review slot already sealed or reviewer is the producer")
            item["reviews"].append({"execution_id": execution_id, "slot": action["slot"], **output})
            if len(item["reviews"]) == item["required_reviews"]:
                formal = item.get("formal", {})
                if (formal.get("status") == "verified" and
                    formal.get("source_sha256") == hashlib.sha256(item["lean_code"].encode()).hexdigest() and
                    all(r["decision"] == "match" and r["scope_complete"] for r in item["reviews"])):
                    item["status"] = "verified"
                    item["verified_at"] = now()
                else:
                    item["status"] = "needs_revision"
                self._enqueue("research_plan")
        elif role == "goal_audit":
            if any(j["basis"] == action["basis"] and j["slot"] == action["slot"] for j in self.instance["goal_judgments"]):
                raise ValueError("goal audit slot already sealed")
            if action["basis"] != self._goal_basis_key():
                raise ValueError("goal audit inputs changed before acceptance")
            usable = [k for k in self.instance["knowledge"].values() if k["status"] == "verified" and knowledge.assess_use(k, self.instance)["valid"]]
            known = {k["id"] for k in usable} | {t["id"] for t in self.runtime["tasks"].values() if t.get("results")}
            cited = [ref for ref in output["used_sources"] if ref in known]
            dependencies = cited or ([k["id"] for k in usable] if self.instance["goal_kind"] == "mathematical"
                                     else [t["id"] for t in self.runtime["tasks"].values() if t.get("results")])
            judgment = {"execution_id": execution_id, "slot": action["slot"], "basis": action["basis"], "required": action["required"],
                        "dependencies": dependencies, "record_basis": knowledge.capture_basis(self.instance, self.runtime, dependencies),
                        "basis_is_conservative": not bool(cited), "goal_revision": self.instance.get("goal_revision", 1),
                        "source_basis": deepcopy(self.runtime["executions"][execution_id].get("source_basis", [])),
                        "policy_revision": self.instance.get("policy_revision", 1), "current": True, **output}
            self.instance["goal_judgments"].append(judgment)
            judgments = [j for j in self.instance["goal_judgments"] if j["basis"] == action["basis"]]
            if len(judgments) == action["required"]:
                satisfied = all(j["decision"] == "satisfied" and j["scope_complete"] and j.get("current", True) for j in judgments)
                eligible = usable
                if self.instance["goal_kind"] == "mathematical" and not eligible:
                    satisfied = False
                if satisfied:
                    self.instance["goal_status"] = "mathematically_solved" if self.instance["goal_kind"] == "mathematical" else "research_goal_satisfied"
                    self.instance["goal_assessment_basis"] = action["basis"]
                    self.runtime["status"] = "completed"
                    self.runtime["queue"] = []
                    self._ensure_academic_followup()
                    if self.runtime["questions"]:
                        self.runtime["history"].append({"kind": "questions_preserved_at_goal_completion", "questions": self.runtime["questions"]})
                        self.runtime["questions"] = []
        elif role == "intent_interpretation":
            if action.get("stage", "interpret") == "interpret":
                self.runtime.setdefault("interpretations", {})[target] = {"execution_id": execution_id, **output}
                if output["needs_clarification"]:
                    self.runtime["questions"].extend(output["questions"])
                else:
                    self._enqueue("intent_interpretation", target, stage="check", reason="Independently compare interpretation with the preserved user request")
            else:
                interpretation = self.runtime["interpretations"][target]
                if interpretation["execution_id"] == execution_id:
                    raise ValueError("interpretation cannot check itself")
                interpretation["check"] = {"execution_id": execution_id, **output}
                if output["decision"] == "match" and output["scope_complete"]:
                    for change in interpretation["proposed_changes"]:
                        if change["kind"] == "none": continue
                        translated = {"kind": change["kind"], "goal" if change["kind"] == "goal" else "text": change["text"]}
                        self.instance, self.runtime, _ = governance.apply_decision(self.instance, self.runtime, translated, source_ref=target)
                    self._enqueue("research_preparation", reason="checked user information", interpretation=interpretation["interpretation"])
                else:
                    self.runtime["questions"].append("User intent could not be confirmed: " + "; ".join(output["findings"]))
        elif role == "operational_review":
            if output["decision"] == "stop":
                self.runtime["status"] = "paused"
            elif output["decision"] == "wait":
                self.runtime["status"] = "waiting"
            elif output["decision"] == "revise":
                failed = self.runtime["executions"].get(target)
                if failed:
                    self.runtime["queue"] = [a for a in self.runtime["queue"] if a != failed.get("action")]
                    failed_task = self.runtime["tasks"].get(failed.get("action", {}).get("target"))
                    if failed_task is not None and failed_task["status"] not in {"completed", "closed"}:
                        # The diagnosed contract returns to preparation; the current revision stays unschedulable until revised.
                        failed_task["status"] = "needs_revision"
                        failed_task["revision_requested"] = {"source": execution_id, "revision": failed_task.get("revision"), "reason": output["reason"]}
                self._enqueue("research_preparation", reason=output["reason"])
            elif output["decision"] == "retry":
                failed = self.runtime["executions"].get(target)
                if not failed or failed.get("outcome") == "output_accepted" or failed.get("role") == "formal_check":
                    raise ValueError("retry requires an incomplete AI execution")
                previous = failed["action"]
                if previous.get("recovery_attempt", 0) >= 1:
                    self.runtime["status"] = "waiting"
                    self.runtime["questions"].append("A diagnosed retry also failed; revise inputs or execution configuration.")
                else:
                    self.runtime["queue"] = [a for a in self.runtime["queue"] if a != previous]
                    self.runtime["queue"].insert(0, {**previous, "recovery_attempt": 1,
                        "recovery": {"execution_id": target, "diagnosis": output["reason"], "review_execution": execution_id}})
        elif role == "maintenance":
            self.runtime["history"].append({"kind": "maintenance", **output})
        else:
            raise ValueError(f"unsupported activity {role}")

    def _goal_basis_key(self) -> str:
        tasks = [{key: deepcopy(task.get(key)) for key in
                  ("id", "revision", "question", "scope", "completion_criteria", "results", "status")}
                 for task in self.runtime["tasks"].values()]
        return hashlib.sha256(canonical_json({"goal": self.instance["goal"], "goal_revision": self.instance.get("goal_revision", 1),
            "policy_revision": self.instance.get("policy_revision", 1), "knowledge": self.instance["knowledge"],
            "tasks": tasks, "goal_kind": self.instance["goal_kind"], "sources": capture_sources(self.instance),
            "user_inputs": self.runtime["inputs"], "required": self.instance["config"]["goal_auditors"],
            "input_contract": hashlib.sha256(self._render_prompt("goal_audit", {}).encode()).hexdigest()})).hexdigest()

    def _apply_plan(self, output: dict, execution_id: str) -> None:
        tasks = self.runtime["tasks"]
        selected = output["selections"]
        deferred = [d["task_id"] for d in output["deferred"]]
        eligible = {tid for tid, task in tasks.items() if task["status"] == "ready"}
        if len(selected + deferred) != len(set(selected + deferred)) or set(selected + deferred) != eligible:
            raise ValueError("plan must select or defer every ready task exactly once")
        assessment_ids = [a["task_id"] for a in output["task_assessments"]]
        required_assessments = {tid for tid, task in tasks.items() if task["status"] == "assessing"}
        if len(assessment_ids) != len(set(assessment_ids)) or not required_assessments <= set(assessment_ids):
            raise ValueError("plan must assess every returned task exactly once")
        for assessment in output["task_assessments"]:
            task = tasks.get(assessment["task_id"])
            if task is None or task["status"] not in {"assessing", "waiting"}:
                raise ValueError("assessment requires a task with returned work")
            checks = assessment["criteria_results"]
            if sorted(c["criterion"] for c in checks) != sorted(task["completion_criteria"]):
                raise ValueError("task assessment must cover the exact completion criteria")
            if assessment["decision"] == "completed" and not all(c["satisfied"] and c["evidence"].strip() for c in checks):
                raise ValueError("completed task requires evidence for every completion criterion")
            if assessment["decision"] == "closed" and task.get("scope_disposition", {}).get("kind") not in {"withdraw", "transfer", "superseded_requirements"}:
                raise ValueError("closing unfinished obligations requires an explicit scope transfer or withdrawal; use incomplete to return unfinished research")
            task["assessment"] = {"execution_id": execution_id, **assessment}
            task["status"] = {"completed": "completed", "closed": "closed", "incomplete": "needs_revision"}[assessment["decision"]]
            self._record_academic_assessment(task, assessment, execution_id)
        for tid in selected:
            if self.instance["goal_status"] in {"mathematically_solved", "research_goal_satisfied"} and not tasks[tid].get("academic_requirement_id"):
                raise ValueError("new research production cannot be selected after goal satisfaction")
            tasks[tid]["status"] = "performing"
            tasks[tid]["selected_by"] = execution_id
            self._enqueue("research_work", tid)
        for entry in output["deferred"]:
            tasks[entry["task_id"]]["deferred_reason"] = entry["reason"]
        if output["goal_audit"] and self.instance["goal_status"] not in {"mathematically_solved", "research_goal_satisfied"}:
            basis = self._goal_basis_key()
            if not any(j["basis"] == basis for j in self.instance["goal_judgments"]):
                for slot in range(self.instance["config"]["goal_auditors"]):
                    self._enqueue("goal_audit", slot=slot, basis=basis, required=self.instance["config"]["goal_auditors"])
        if output["preparation_requests"]:
            self._enqueue("research_preparation", reason="\n".join(output["preparation_requests"]))
        if not selected and not output["goal_audit"] and not output["preparation_requests"] and not self.runtime["queue"]:
            self.runtime["status"] = "waiting"
        self._ensure_academic_followup()

    def _formal(self, action: dict) -> None:
        action.setdefault("id", new_id("AC"))
        action = deepcopy(action)
        kid = action["target"]
        item = self.instance["knowledge"][kid]
        execution_id, activity_id = new_id("EX"), new_id("AY")
        workspace = Path(self.instance["workspace"]) / "formal" / execution_id
        workspace.mkdir(parents=True)
        source, declarations = item["lean_code"], item["declaration_names"]
        authority = governance.authorize(self.instance, action)
        if not authority["allowed"]:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": action, "reason": authority["reason"]}
            self._remove_action(action)
            self._save()
            return
        execution = {"id": execution_id, "activity_id": activity_id, "role": "formal_check", "status": "running",
                     "created_at": now(), "action": action, "grant_id": authority["grant_id"], "engine_sha256": ENGINE_SHA256}
        self.runtime["executions"][execution_id] = execution
        self.runtime["activities"][activity_id] = {"id": activity_id, "role": "maintenance", "actor_kind": "machine", "status": "active", "execution_ids": [execution_id]}
        self.runtime["active_execution"] = execution_id
        self._save()
        def stop():
            self._controls()
            if self._check_conversations(): self._save()
            return (self.runtime["status"] in {"paused", "closed"} or self.runtime.get("stop_requested") or
                    not governance.authorize(self.instance, action)["allowed"])
        kwargs = dict(source=source, declarations=declarations, workspace=workspace,
                      lean_command=self.instance["config"]["lean_command"], timeout_seconds=self.instance["config"]["lean_timeout_seconds"])
        parameters = inspect.signature(self.formal_verifier).parameters
        accepts_extra = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
        if "should_stop" in parameters or accepts_extra: kwargs["should_stop"] = stop
        if "allowed_axioms" in parameters or accepts_extra: kwargs["allowed_axioms"] = tuple(self.instance["config"]["allowed_axioms"])
        try:
            result = self.formal_verifier(**kwargs)
        except Exception as error:
            result = {"status": "failed", "reason": str(error)}
        result = self._bind_formal_environment(json_safe(result))
        bundle = new_id("BA")
        item = self.instance["knowledge"][kid]
        source_unchanged = hashlib.sha256(item["lean_code"].encode()).hexdigest() == hashlib.sha256(source.encode()).hexdigest()
        if not source_unchanged:
            result.update(status="failed", reason="proposal changed during formal verification")
        item["formal"] = {**result, "execution_id": execution_id, "artifact_ref": f"runtime/artifacts/{bundle}/formal.json"}
        self.runtime["executions"][execution_id].update(status="ended", ended_at=now(), outcome=result["status"], artifact_bundle=bundle)
        self.runtime["activities"][activity_id].update(status="finished" if result["status"] in {"verified", "rejected"} else "unresolved",
                                                     result_ref=f"runtime/artifacts/{bundle}/formal.json")
        self.runtime["active_execution"] = None
        if result["status"] != "stopped":
            self._remove_action(action)
        if result["status"] == "verified" and result.get("trust_environment_status") == "active":
            previous_cycle = item.get("previous_review_cycle_id") or item.get("review_cycle_id")
            self._start_identity_review(kid, previous_cycle_id=previous_cycle)
            review_actions = [a for a in self.runtime["queue"] if a.get("role") == "identity_review" and a.get("target") == kid]
            self.runtime["queue"] = review_actions + [a for a in self.runtime["queue"] if a not in review_actions]
        elif result["status"] == "stopped":
            if self.runtime["status"] != "closed": self.runtime["status"] = "paused"
        else:
            self._enqueue("research_plan", reason="Formal verification returned a result requiring a new research decision", formal_target=kid)
        self._save({f"runtime/artifacts/{bundle}/proposal.lean": source.encode(),
                    f"runtime/artifacts/{bundle}/formal.json": canonical_json(result)})

    def check(self) -> dict:
        self.head, instance, runtime = self.store.load()
        errors = state_errors(instance, runtime)
        evidence_refs = [(source.get("path"), source.get("sha256"), source.get("bytes")) for source in instance.get("sources", [])]
        for execution in runtime["executions"].values():
            evidence_refs.extend((entry.get("artifact_ref"), entry.get("sha256"), entry.get("bytes")) for entry in execution.get("output_files", []))
            if execution.get("input_bundle") and execution.get("input_sha256"):
                evidence_refs.append((f"runtime/artifacts/{execution['input_bundle']}/input.txt", execution["input_sha256"], None))
        for ref, digest, size in evidence_refs:
            try:
                raw = self.store.read(ref, self.head)
                if hashlib.sha256(raw).hexdigest() != digest or (size is not None and len(raw) != size):
                    errors.append(f"{ref}: preserved artifact differs from its content reference")
            except (KeyError, ValueError, OSError) as error:
                errors.append(f"{ref}: preserved artifact cannot be read: {error}")
        if instance.get("contract_id") != CONTRACT or runtime.get("contract_id") != CONTRACT:
            errors.append("unsupported instance/runtime contract")
        if runtime["status"] not in {"ready", "running", "paused", "waiting", "budget_exhausted", "completed", "closed"}:
            errors.append("unknown runtime status")
        try:
            validate_config(instance["config"])
        except ValueError as error:
            errors.append(str(error))
        for kid, item in instance["knowledge"].items():
            if item["status"] == "verified":
                if item.get("formal", {}).get("status") != "verified":
                    errors.append(f"{kid}: K lacks formal verification")
                elif item["formal"].get("source_sha256") != hashlib.sha256(item["lean_code"].encode()).hexdigest():
                    errors.append(f"{kid}: formal source changed")
                if item.get("review_cycle_id"):
                    cycle = runtime.get("review_cycles", {}).get(item["review_cycle_id"])
                    assessment = item.get("identity_assessment", {})
                    if not cycle or cycle["status"] != "completed" or cycle["decision"] != "match" or not assessment.get("effective"):
                        errors.append(f"{kid}: K lacks an effective completed review cycle")
                    elif assessment.get("proposal_digest") != cycle["proposal_digest"]:
                        errors.append(f"{kid}: review cycle proposal binding changed")
                    ids = assessment.get("execution_ids", [])
                else:
                    if len(item["reviews"]) != item["required_reviews"] or not all(r["decision"] == "match" and r["scope_complete"] for r in item["reviews"]):
                        errors.append(f"{kid}: K lacks complete semantic reviews")
                    ids = [r["execution_id"] for r in item["reviews"]]
                if len(ids) != len(set(ids)) or item["producer_execution"] in ids:
                    errors.append(f"{kid}: reviewer identity collision")
                for rid in ids:
                    execution = runtime["executions"].get(rid, {})
                    if execution.get("role") != "identity_review" or execution.get("action", {}).get("target") != kid or execution.get("outcome") != "output_accepted":
                        errors.append(f"{kid}: review is not bound to an accepted execution")
        for task in runtime["tasks"].values():
            if task["status"] not in {"planned", "ready", "needs_revision", "performing", "waiting", "assessing", "completed", "closed"}:
                errors.append(f"{task['id']}: unknown task state")
            if task["status"] == "completed" and task.get("assessment", {}).get("decision") != "completed":
                errors.append(f"{task['id']}: task completion lacks independent assessment")
            elif task["status"] == "completed":
                checks = task["assessment"]["criteria_results"]
                if sorted(c["criterion"] for c in checks) != sorted(task["completion_criteria"]) or not all(c["satisfied"] and c["evidence"].strip() for c in checks):
                    errors.append(f"{task['id']}: completion criteria are not established")
                if any(e.get("action", {}).get("target") == task["id"] and e.get("role") in {"research_work", "supplemental_research"} and e["status"] != "ended" for e in runtime["executions"].values()):
                    errors.append(f"{task['id']}: completed task has a live work execution")
        for aid, activity in runtime["activities"].items():
            if any(eid not in runtime["executions"] or runtime["executions"][eid].get("activity_id") != aid for eid in activity["execution_ids"]):
                errors.append(f"{aid}: activity/execution binding is invalid")
        active = runtime["active_execution"]
        if active is not None and runtime["executions"].get(active, {}).get("status") not in {"starting", "running"}:
            errors.append("active execution is absent or ended")
        for eid, execution in runtime["executions"].items():
            if execution["status"] not in {"starting", "running", "ended"}:
                errors.append(f"{eid}: unknown execution state")
            if execution["status"] != "ended" and eid != active and execution.get("parent_execution_id") != active:
                errors.append(f"{eid}: unowned live execution")
        for relation in instance["relations"]:
            if any(relation[k] not in instance["knowledge"] for k in ("source", "target")):
                errors.append(f"{relation['id']}: absent endpoint")
        if runtime["status"] == "completed":
            judgments = instance["goal_judgments"]
            if not judgments:
                errors.append("goal completion lacks audits")
            else:
                last = judgments[-1]
                group = [j for j in judgments if j["basis"] == last["basis"]]
                expected = last.get("required", instance["config"]["goal_auditors"])
                if len(group) != expected or len({j["slot"] for j in group}) != expected or not all(j["decision"] == "satisfied" and j["scope_complete"] for j in group):
                    errors.append("goal completion lacks complete agreeing audits")
                if instance["goal_kind"] == "mathematical" and not any(k["status"] == "verified" for k in instance["knowledge"].values()):
                    errors.append("mathematical goal has no verified formal result")
        return {"passed": not errors, "snapshot": self.head, "errors": errors,
                "scope": "persisted CLI workflow relationships; no new mathematical or OS verification"}
