"""Persistent research workflow using observable Codex CLI executions.

The executable contract is do-math-cli/1. It preserves distinct mathematical,
semantic, goal, authority and execution judgments; it does not claim the old
draft/9 provider-call or OS read-isolation guarantees.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import base64
import binascii
import hashlib
import json
from pathlib import Path
import time
from typing import Any

import jsonschema

from .contracts import render_prompt, schema_for
from .formal import verify_lean
from .model_runner import CodexModelRunner
from .repository import ResearchRepository, canonical_json, new_id

CONTRACT = "do-math-cli/1"
ENGINE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit"}
DEFAULT_CONFIG = {
    "model": "gpt-5.6-sol", "effort": "medium", "role_models": {},
    "work_calls": 40, "operations_calls": 30, "call_timeout_seconds": 600,
    "run_timeout_seconds": 7200, "max_cycles": 5, "reviewers": 2,
    "goal_auditors": 2, "max_input_bytes": 500000, "max_output_repairs": 1,
    "lean_command": None, "lean_timeout_seconds": 120,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"sha256": hashlib.sha256(value).hexdigest(), "text": value.decode("utf-8", "replace")}
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
    if set(config) - set(DEFAULT_CONFIG) or (set(DEFAULT_CONFIG) - {"max_output_repairs"}) - set(config):
        raise ValueError("configuration fields differ from do-math-cli/1")
    if not isinstance(config["model"], str) or not config["model"].strip():
        raise ValueError("model is required")
    if config["effort"] not in {"minimal", "low", "medium", "high", "xhigh"}:
        raise ValueError("unsupported reasoning effort")
    if not isinstance(config["role_models"], dict) or any(not isinstance(v, str) or not v for v in config["role_models"].values()):
        raise ValueError("role_models must map roles to model names")
    for role in config["role_models"]:
        schema_for(role)
    for key in ("work_calls", "operations_calls", "call_timeout_seconds", "run_timeout_seconds",
                "max_cycles", "reviewers", "goal_auditors", "max_input_bytes", "lean_timeout_seconds"):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if isinstance(config.get("max_output_repairs", 1), bool) or not isinstance(config.get("max_output_repairs", 1), int) or config.get("max_output_repairs", 1) < 0:
        raise ValueError("max_output_repairs must be a nonnegative integer")
    command = config["lean_command"]
    if command is not None and (not isinstance(command, list) or not command or
                               any(not isinstance(x, str) or not x or "\0" in x for x in command)):
        raise ValueError("lean_command must be a nonempty argv list")


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
    if action not in {"pause", "resume", "close", "input", "configure", "request"}:
        raise ValueError("unknown control action")
    _, instance, runtime = ResearchRepository(repository, instance_id).load()
    if action == "configure":
        candidate = {**instance["config"], **(config or {})}
        validate_config(candidate)
    if action == "input" and not text.strip():
        raise ValueError("input text is required")
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


class ResearchEngine:
    def __init__(self, repository: Path, instance_id: str, *, runner: Any = None, formal_verifier: Any = None):
        self.store = ResearchRepository(repository, instance_id)
        self.runner = runner or CodexModelRunner()
        self.formal_verifier = formal_verifier or verify_lean
        self.head, self.instance, self.runtime = self.store.load()
        if self.instance.get("contract_id") != CONTRACT or self.runtime.get("contract_id") != CONTRACT:
            raise ValueError("unsupported instance contract; explicit migration is required")

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

    def process_controls(self) -> dict:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self._controls()
        return self.status()

    def status(self) -> dict:
        self.head, self.instance, self.runtime = self.store.load()
        executions = list(self.runtime["executions"].values())
        return {"instance_id": self.instance["id"], "snapshot": self.head, "title": self.instance["title"],
                "goal": self.instance["goal"], "goal_status": self.instance["goal_status"],
                "status": self.runtime["status"], "active_execution": self.runtime["active_execution"],
                "pending_actions": len(self.runtime["queue"]), "cycles": self.runtime["cycles"],
                "tasks": [{"id": t["id"], "title": t["title"], "status": t["status"]} for t in self.runtime["tasks"].values()],
                "knowledge": {"K": sum(k["status"] == "verified" for k in self.instance["knowledge"].values()),
                              "F": sum(k["status"] != "verified" for k in self.instance["knowledge"].values())},
                "budget": {pool: {"limit": self.instance["config"][pool + "_calls"],
                                  "used": sum(e.get("budget_kind") == pool for e in executions)} for pool in ("work", "operations")},
                "usage": [e.get("usage", {}) for e in executions if e.get("usage")],
                "latest_results": list(self.runtime["activities"].values())[-5:],
                "questions": self.runtime["questions"], "pending_controls": len(self._inbox()),
                "assurance": {"read_scope": "instructions_and_selected_inputs", "provider_operations": "not_observed",
                              "token_usage": "CLI_reported_after_execution", "formal": "Lean_and_axiom_check",
                              "review": "fresh_sessions_without_peer_results_in_inputs"}}

    def run(self, *, max_steps: int | None = None) -> dict:
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive")
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self._controls()
            if self.runtime["active_execution"]:
                ex = self.runtime["executions"][self.runtime["active_execution"]]
                ex.update(status="ended", outcome="execution_incomplete", error="previous executor disappeared", ended_at=now())
                if ex.get("activity_id") in self.runtime["activities"]:
                    self.runtime["activities"][ex["activity_id"]]["status"] = "unresolved"
                self.runtime["active_execution"] = None
                self.runtime["status"] = "paused"
                self.runtime["history"].append({"kind": "recovery", "execution_id": ex["id"], "remote_termination": "unknown"})
                self._save()
            deadline = time.monotonic() + self.instance["config"]["run_timeout_seconds"]
            steps = 0
            while self.runtime["status"] in {"ready", "running"}:
                self._controls()
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
                else:
                    if not self._call(action, deadline):
                        break
                steps += 1
            self._controls()
        return self.status()

    def _context(self, action: dict, workspace: Path) -> dict:
        directory = workspace / "input"
        directory.mkdir(parents=True, exist_ok=True)
        catalog = []
        for kid, knowledge in sorted(self.instance["knowledge"].items()):
            # Hide the current review group's partial results. Completed prior
            # stages are public evidence needed by planners and goal auditors.
            hidden_reviews = ((action["role"] == "identity_review" and kid == action.get("target")) or
                              len(knowledge["reviews"]) < knowledge.get("required_reviews", 1))
            record = {k: v for k, v in knowledge.items() if not (k == "reviews" and hidden_reviews)}
            path = directory / "knowledge" / (kid + ".json")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(canonical_json(record))
            catalog.append({"id": kid, "kind": knowledge["kind"], "title": knowledge["title"],
                            "summary": knowledge["summary"], "status": knowledge["status"],
                            "path": path.relative_to(workspace).as_posix()})
        sources = []
        for i, source in enumerate(self.instance["sources"]):
            raw = self.store.read(source["path"], self.head)
            path = directory / "sources" / f"{i:04d}-{source['name']}"
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(raw)
            sources.append({**source, "local_path": path.relative_to(workspace).as_posix()})
        target = action.get("target")
        task = self.runtime["tasks"].get(target)
        context = {"snapshot": self.head, "goal": self.instance["goal"], "goal_kind": self.instance["goal_kind"],
                   "policies": self.instance["policies"], "action": action, "task": task,
                   "tasks": list(self.runtime["tasks"].values()), "knowledge_catalog": catalog,
                   "relations": self.instance["relations"], "sources": sources,
                   "user_inputs": self.runtime["inputs"], "open_questions": self.runtime["questions"],
                   "recent_history": self.runtime["history"][-8:],
                   "instructions": "Read input/ and your workspace only. Ask for missing inputs. Never read other runs or the central repository. New research source code belongs in this workspace."}
        if action["role"] in {"identity_review", "goal_audit"}:
            context.pop("recent_history")
        if action["role"] == "identity_review":
            context.pop("tasks")
        if action["role"] == "identity_review":
            context["proposal"] = {k: v for k, v in self.instance["knowledge"][target].items() if k != "reviews"}
        if action["role"] == "goal_audit":
            context["eligible_knowledge"] = [{"id": k["id"], "statement": k["statement"],
                "explanation": k["explanation"], "summary": k["summary"],
                "formal_verification": {key: k["formal"].get(key) for key in
                                        ("status", "source_sha256", "declarations", "axioms", "artifact_ref", "toolchain")},
                "identity_reviews": k["reviews"]} for k in self.instance["knowledge"].values() if k["status"] == "verified"]
            context["tasks"] = [{k: v for k, v in t.items() if k not in {"reviews", "assessment"}}
                                for t in self.runtime["tasks"].values()]
        if action["role"] == "operational_review":
            context["execution_to_review"] = self.runtime["executions"].get(target)
        return context

    def _call(self, action: dict, deadline: float) -> bool:
        role = action["role"]
        pool = "work" if role in WORK_ROLES else "operations"
        used = sum(e.get("budget_kind") == pool for e in self.runtime["executions"].values())
        config = self.instance["config"]
        if used >= config[pool + "_calls"]:
            self.runtime["status"] = "budget_exhausted"
            self._save()
            return False
        execution_id, activity_id = new_id("EX"), new_id("AY")
        base = Path(self.instance["workspace"]) / "runs" / execution_id
        workspace = base / "workspace"
        workspace.mkdir(parents=True)
        context = self._context(action, workspace)
        prompt = render_prompt(role, context)
        if len(prompt.encode("utf-8")) > config["max_input_bytes"]:
            self.runtime["status"] = "waiting"
            self.runtime["questions"].append(f"Input for {role} exceeds max_input_bytes; revise inputs or increase that explicit limit.")
            self._save()
            return False
        execution = {"id": execution_id, "activity_id": activity_id, "role": role, "action": action,
                     "budget_kind": pool, "status": "starting", "created_at": now(),
                     "input_snapshot": self.head, "input_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                     "model": config["role_models"].get(role, config["model"]), "effort": config["effort"],
                     "engine_sha256": ENGINE_SHA256}
        self.runtime["executions"][execution_id] = execution
        self.runtime["activities"][activity_id] = {"id": activity_id, "role": role, "status": "active", "execution_ids": [execution_id]}
        self.runtime["active_execution"] = execution_id
        self.runtime["status"] = "running"
        self._save()

        def started(identity: dict) -> None:
            execution.update(status="running", process=json_safe(identity))
            self._save()

        def should_stop() -> bool:
            return time.monotonic() >= deadline or any(x["action"] in {"pause", "close"} for x in self._inbox())

        try:
            result = self.runner.run(prompt=prompt, output_schema=schema_for(role), workspace=workspace,
                                     evidence_dir=base / "evidence", model=execution["model"], effort=execution["effort"],
                                     timeout_seconds=min(config["call_timeout_seconds"], max(.1, deadline-time.monotonic())),
                                     should_stop=should_stop, on_started=started)
        except Exception as error:
            result = {"status": "failed", "output": None, "usage": {}, "error": f"{type(error).__name__}: {error}"}
        result = json_safe(result)
        bundle = new_id("BA")
        artifacts = {f"runtime/artifacts/{bundle}/input.txt": prompt.encode("utf-8"),
                     f"runtime/artifacts/{bundle}/result.json": canonical_json(result),
                     f"runtime/artifacts/{bundle}/schema.json": canonical_json(schema_for(role))}
        if result.get("output") is not None:
            artifacts[f"runtime/artifacts/{bundle}/output.json"] = canonical_json(result["output"])
        execution.update(status="ended", ended_at=now(), usage=result.get("usage", {}),
                         artifact_bundle=bundle, outcome="output_accepted" if result["status"] == "completed" else "execution_incomplete",
                         error=result.get("error"))
        self.runtime["active_execution"] = None
        self.runtime["activities"][activity_id]["status"] = "finished" if result["status"] == "completed" else "unresolved"
        self.runtime["activities"][activity_id]["result_ref"] = f"runtime/artifacts/{bundle}/result.json"
        if result["status"] == "completed":
            try:
                jsonschema.validate(result["output"], schema_for(role))
                # Roll back semantic changes if output relations fail validation.
                before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
                self.runtime["queue"].pop(0)
                self._apply(action, result["output"], execution_id)
                self.runtime["questions"] = [q for q in self.runtime["questions"] if not (
                    q.startswith(f"Invalid output for {role}:") or q.startswith(f"{role} did not finish:"))]
                self.runtime["history"].append({"role": role, "execution_id": execution_id, "summary": result["output"]["summary"]})
                if self.runtime["status"] == "running":
                    self.runtime["status"] = "ready"
            except Exception as error:
                if "before_instance" in locals():
                    self.instance, self.runtime = before_instance, before_runtime
                self.runtime["executions"][execution_id].update(outcome="execution_incomplete", error=f"output validation: {error}")
                self.runtime["activities"][activity_id]["status"] = "unresolved"
                attempts = action.get("repair_attempt", 0)
                if attempts < config.get("max_output_repairs", 1):
                    self.runtime["queue"][0] = {**action, "repair_attempt": attempts + 1,
                                                 "repair": {"error": str(error), "previous_output": result["output"]}}
                    self.runtime["status"] = "ready"
                else:
                    self.runtime["status"] = "paused"
                    self.runtime["questions"].append(f"Invalid output for {role}: {error}")
        else:
            if result["status"] == "failed" and role != "operational_review" and action.get("recovery_attempt", 0) < 1:
                self.runtime["status"] = "ready"
                self.runtime["queue"].insert(0, {"role": "operational_review", "target": execution_id,
                                                  "reason": "diagnose the preserved execution failure before selecting a recovery"})
            else:
                self.runtime["status"] = "paused"
            self.runtime["questions"].append(f"{role} did not finish: {result.get('error')}; results and inputs are preserved.")
        self._save(artifacts)
        self._controls()
        return self.runtime["status"] in {"ready", "running"}

    def _enqueue(self, role: str, target: str | None = None, **extra: Any) -> None:
        action = {"role": role, **extra}
        if target is not None:
            action["target"] = target
        if action not in self.runtime["queue"]:
            self.runtime["queue"].append(action)

    def _apply(self, action: dict, output: dict, execution_id: str) -> None:
        role, target = action["role"], action.get("target")
        self.runtime["questions"].extend(q for q in output["questions"] if q not in self.runtime["questions"])
        if role == "research_preparation":
            self.runtime["cycles"] += 1
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
                self.runtime["tasks"][tid] = {**proposal, "id": tid, "revision": (old["revision"]+1 if old else 1),
                                              "status": "planned", "producer_execution": execution_id,
                                              "results": old.get("results", []) if old else [], "reviews": []}
                self._enqueue("task_contract_review", tid)
            self._enqueue("research_plan")
        elif role == "task_contract_review":
            task = self.runtime["tasks"][target]
            if task["producer_execution"] == execution_id:
                raise ValueError("contract author cannot review its own contract")
            task["reviews"].append({"execution_id": execution_id, "revision": task["revision"], **output})
            task["status"] = "ready" if output["decision"] == "approved" else "needs_revision"
        elif role == "research_plan":
            self._apply_plan(output, execution_id)
        elif role in {"research_work", "supplemental_research"}:
            if not output["report"].strip():
                raise ValueError("work must report its actual scope, outcome and remaining work")
            task = self.runtime["tasks"][target]
            task["results"].append({"execution_id": execution_id, **output})
            task["status"] = "waiting" if output["outcome"] == "waiting" else "assessing"
            task["remaining_work"] = output["remaining_work"]
            new_items = {}
            for item in output["knowledge"]:
                kid = new_id("KN")
                record = {**item, "id": kid, "status": "candidate", "producer_execution": execution_id,
                          "task_id": target, "created_at": now(), "reviews": [],
                          "required_reviews": self.instance["config"]["reviewers"]}
                self.instance["knowledge"][kid] = record
                if item["title"] in new_items:
                    raise ValueError("knowledge titles must be unique within one output")
                new_items[item["title"]] = kid
                if item["lean_code"]:
                    if not item["declaration_names"]:
                        raise ValueError("Lean proposal requires declaration_names")
                    self._enqueue("formal_check", kid)
            for relation in output["relations"]:
                source = new_items.get(relation["source"], relation["source"])
                destination = new_items.get(relation["target"], relation["target"])
                if source not in self.instance["knowledge"] or destination not in self.instance["knowledge"]:
                    raise ValueError("relation endpoints must identify existing knowledge or this output's titles")
                self.instance["relations"].append({**relation, "id": new_id("RL"), "source": source, "target": destination,
                                                    "producer_execution": execution_id, "authority": "research_connection"})
            self._enqueue("research_plan")
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
            judgment = {"execution_id": execution_id, "slot": action["slot"], "basis": action["basis"], "required": action["required"], **output}
            self.instance["goal_judgments"].append(judgment)
            judgments = [j for j in self.instance["goal_judgments"] if j["basis"] == action["basis"]]
            if len(judgments) == action["required"]:
                satisfied = all(j["decision"] == "satisfied" and j["scope_complete"] for j in judgments)
                eligible = [k for k in self.instance["knowledge"].values() if k["status"] == "verified"]
                if self.instance["goal_kind"] == "mathematical" and not eligible:
                    satisfied = False
                if satisfied:
                    self.instance["goal_status"] = "mathematically_solved" if self.instance["goal_kind"] == "mathematical" else "research_goal_satisfied"
                    self.runtime["status"] = "completed"
                    self.runtime["queue"] = []
                    if self.runtime["questions"]:
                        self.runtime["history"].append({"kind": "questions_preserved_at_goal_completion", "questions": self.runtime["questions"]})
                        self.runtime["questions"] = []
        elif role == "intent_interpretation":
            self.runtime["history"].append({"kind": "interpreted_input", "request_id": target, **output})
            if not output["needs_clarification"]:
                self._enqueue("research_preparation", reason="new user information", interpretation=output["interpretation"])
        elif role == "operational_review":
            if output["decision"] == "stop":
                self.runtime["status"] = "paused"
            elif output["decision"] == "wait":
                self.runtime["status"] = "waiting"
            elif output["decision"] == "revise":
                failed = self.runtime["executions"].get(target)
                if failed:
                    self.runtime["queue"] = [a for a in self.runtime["queue"] if a != failed.get("action")]
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
            task["assessment"] = {"execution_id": execution_id, **assessment}
            task["status"] = {"completed": "completed", "closed": "closed", "incomplete": "needs_revision"}[assessment["decision"]]
        for tid in selected:
            tasks[tid]["status"] = "performing"
            tasks[tid]["selected_by"] = execution_id
            self._enqueue("research_work", tid)
        for entry in output["deferred"]:
            tasks[entry["task_id"]]["deferred_reason"] = entry["reason"]
        if output["goal_audit"]:
            basis = hashlib.sha256(canonical_json({"goal": self.instance["goal"], "knowledge": self.instance["knowledge"],
                                                   "tasks": tasks, "goal_kind": self.instance["goal_kind"],
                                                   "user_inputs": self.runtime["inputs"],
                                                   "required": self.instance["config"]["goal_auditors"],
                                                   "input_contract": hashlib.sha256(render_prompt("goal_audit", {}).encode()).hexdigest()})).hexdigest()
            if not any(j["basis"] == basis for j in self.instance["goal_judgments"]):
                for slot in range(self.instance["config"]["goal_auditors"]):
                    self._enqueue("goal_audit", slot=slot, basis=basis, required=self.instance["config"]["goal_auditors"])
        if output["preparation_requests"]:
            self._enqueue("research_preparation", reason="\n".join(output["preparation_requests"]))
        if not selected and not output["goal_audit"] and not output["preparation_requests"] and not self.runtime["queue"]:
            self.runtime["status"] = "waiting"

    def _formal(self, action: dict) -> None:
        item = self.instance["knowledge"][action["target"]]
        execution_id = new_id("EX")
        workspace = Path(self.instance["workspace"]) / "formal" / execution_id
        workspace.mkdir(parents=True)
        execution = {"id": execution_id, "role": "formal_check", "status": "running", "created_at": now(), "action": action}
        self.runtime["executions"][execution_id] = execution
        self.runtime["active_execution"] = execution_id
        self._save()
        try:
            result = self.formal_verifier(source=item["lean_code"], declarations=item["declaration_names"], workspace=workspace,
                                          lean_command=self.instance["config"]["lean_command"],
                                          timeout_seconds=self.instance["config"]["lean_timeout_seconds"])
        except Exception as error:
            result = {"status": "failed", "reason": str(error)}
        result = json_safe(result)
        bundle = new_id("BA")
        item["formal"] = {**result, "execution_id": execution_id, "artifact_ref": f"runtime/artifacts/{bundle}/formal.json"}
        execution.update(status="ended", ended_at=now(), outcome=result["status"], artifact_bundle=bundle)
        self.runtime["active_execution"] = None
        self.runtime["queue"].pop(0)
        if result["status"] == "verified":
            for slot in reversed(range(item["required_reviews"])):
                self.runtime["queue"].insert(0, {"role": "identity_review", "target": item["id"], "slot": slot})
        self._save({f"runtime/artifacts/{bundle}/proposal.lean": item["lean_code"].encode("utf-8"),
                    f"runtime/artifacts/{bundle}/formal.json": canonical_json(result)})

    def check(self) -> dict:
        self.head, instance, runtime = self.store.load()
        errors = []
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
                if len(item["reviews"]) != item["required_reviews"] or not all(r["decision"] == "match" and r["scope_complete"] for r in item["reviews"]):
                    errors.append(f"{kid}: K lacks complete semantic reviews")
                ids = [r["execution_id"] for r in item["reviews"]]
                if len(ids) != len(set(ids)) or item["producer_execution"] in ids:
                    errors.append(f"{kid}: reviewer identity collision")
                if len({r["slot"] for r in item["reviews"]}) != len(item["reviews"]):
                    errors.append(f"{kid}: duplicate review slot")
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
            if execution["status"] != "ended" and eid != active:
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
