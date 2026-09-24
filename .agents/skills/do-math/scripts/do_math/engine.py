"""Persistent research workflow using observable Codex CLI executions.

The persisted contract is do-math-state/5. Mathematical, semantic, goal,
authority and execution judgments remain distinct. Session boundaries are
instructions and do not claim OS isolation.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import base64
import binascii
import hashlib
import json
import inspect
import os
import shutil
from pathlib import Path
import time
from typing import Any

import jsonschema

from .contracts import render_prompt, schema_for, all_prompt_documents, reading_map, prompt_metrics, action_schema, with_integration_schema, contract_review_decision, task_candidate_record
from .formal import verify_lean, discover_lean
from . import governance, knowledge, planning, knowledge_io, knowledge_records, academic, task_scope, delegations
from .input_basis import capture_sources, sources_current, capture_decision_basis, decision_basis_changes, CurrentnessChanged
from .context_store import collect_outputs, prepare_role_input, defer_input_overflow, materialize_inputs, read_source, prefetch_artifacts
from .observations import ObservationTracker, CHECKPOINT_SCHEMA, recovered_checkpoint, request_checkpoint, validate_rules, write_checkpoint_reminder, self_check_feedback, publish_worker_feedback, tracker_config, persistent_record, read_checkpoint
from .review_engine import ReviewEngineMixin
from .lifecycle_engine import LifecycleEngineMixin
from .academic_engine import AcademicEngineMixin
from .governance_engine import GovernanceEngineMixin
from .model_runner import ModelRunner
from .repository import ResearchRepository, canonical_json, lossless_json, exact_content_hash, semantic_content_hash, new_id
from .state_checks import state_errors, inspect_state
from .git_store import GitStateStoreError
from .scholarly import resolve_scholarly_server, validate_scholarly_server
from .task_scope import apply_task_dispositions
from . import model_policy
from .scheduler import SchedulerMixin, WORK_ROLES
from .session_slots import SessionSlots
from .provider_engine import ProviderEngineMixin
from .decision_engine import DecisionEngineMixin
from .revision_engine import RevisionEngineMixin
from .question_engine import QuestionEngineMixin
from . import questions, reporting
from . import revisions
from . import submission, execution_window, integration
from . import activities, execution_lifecycle, execution_profiles, initialization
from .preflight import inspect_current_state
from .state_contract import STATE_FORMAT_VERSION, STATE_CONTRACT_ID, default_state_contract
from . import task_contracts, operational_dispositions, retention, repair_execution
from .control_transport import ControlTransport

CONTRACT = STATE_CONTRACT_ID


def _repository(repository: Path, instance_id: str) -> ResearchRepository:
    contract = default_state_contract()
    knowledge_records.register_storage_families(contract)
    execution_profiles.register_families(contract)
    integration.register_families(contract)
    return ResearchRepository(repository, instance_id, contract=contract)


def _require_current_contract(instance, runtime):
    if any(root.get("contract_id") != CONTRACT or root.get("feature_version") != STATE_FORMAT_VERSION
           for root in (instance, runtime)):
        raise ValueError("only the installed version-five contract can execute; no automatic migration is performed")
    checked = inspect_current_state(instance, runtime)
    if not checked["valid"]:
        raise ValueError("current state is corrupt: " + json.dumps(checked["errors"], ensure_ascii=False))


class InputPreparationInterrupted(Exception):
    """An unpublished input was abandoned before any model execution."""


class ReviewPreparationDeferred(Exception):
    def __init__(self, outcome):
        self.outcome = outcome
        super().__init__("review input restoration requires its recorded recovery")


ENGINE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
DEFAULT_CONFIG = {
    "tier_models": deepcopy(model_policy.MODELS), "role_tiers": deepcopy(model_policy.ROLE_TIERS),
    "session_limits": deepcopy(model_policy.LIMITS),
    "model": "gpt-5.6-sol", "effort": "medium", "role_models": {},
    "work_calls": None, "operations_calls": None, "call_timeout_seconds": 600,
    "max_cycles": 5, "reviewers": 2,
    "goal_auditors": 2, "max_input_bytes": 500000, "max_output_repairs": 1,
    "lean_command": None, "lean_timeout_seconds": None,
    "review_rounds": 3, "review_research_limit": 3, "research_reconsider_seconds": 86400,
    "observation_mode": "event_driven", "observation_interval_seconds": 300,
    "observation_idle_seconds": 120, "max_observation_reviews": 3,
    "observation_unbounded_wait_seconds": 600, "plan_settle_seconds": 300,
    "checkpoint_grace_seconds": 10, "max_artifact_bytes": 268435456,
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "operator_enabled": True, "operator_interval_seconds": 7200,
    "operator_timeout_seconds": 5400, "operator_model": "gpt-5.6-sol", "operator_effort": "high",
    "scholarly_enabled": True, "scholarly_server": None,
    "claude_only_assigned_model": False,
    "provider_retry_initial_seconds": 300, "provider_retry_max_seconds": 7200,
    "finish_notice_seconds": 60,
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
    if isinstance(value, float):
        # Opaque provider reports retain their original artifact bytes. State
        # projections represent decimals explicitly without integer rounding.
        return {"reported_decimal": repr(value)}
    return value


OPTIONAL_CONFIG = {"tool_review_window_seconds", "self_check_response_window_seconds", "no_progress_limit",
    "import_rework_limit", "selection_failure_limit", "exhaustion_empty_limit", "proposal_version_limit", "contract_revision_limit"}
# Read existing configurations without restoring their retired run-wide limit.
RETIRED_CONFIG = {"run_timeout_seconds", "dispatch_reserve_seconds"}


def _artifact_format_valid(reference, raw):
    """Validate the supported file format, never its mathematical assertion."""
    suffix = Path(reference["path"]).suffix.lower()
    try:
        if suffix == ".json":
            value = submission.load_json(raw)
            if Path(reference["path"]).name == "checkpoint.json":
                jsonschema.Draft202012Validator(CHECKPOINT_SCHEMA).validate(value)
            return True
        if suffix in {".txt", ".md", ".tsv", ".csv"}:
            return "\0" not in raw.decode("utf-8-sig")
    except (ValueError, UnicodeError, jsonschema.ValidationError):
        return False
    # No installed validator for another format is evidence of validity.
    return False


def _evaluation_context_for(store, snapshot):
    def read_artifact(commit, path):
        if not isinstance(path, str) or not path.startswith("runtime/artifacts/"):
            raise ValueError("task evidence must identify an immutable archived artifact")
        return store.read(path, commit)
    return {"snapshot": snapshot, "read_artifact": read_artifact,
            "validate_artifact": _artifact_format_valid, "now": now()}


def validate_config(config: dict) -> None:
    if set(config) - set(DEFAULT_CONFIG) - OPTIONAL_CONFIG - RETIRED_CONFIG - {'host_resources'}:
        raise ValueError("configuration fields differ from do-math-cli/5")
    for key in (OPTIONAL_CONFIG | RETIRED_CONFIG) & config.keys():
        if type(config[key]) is not int or config[key] <= 0:
            raise ValueError(key + " must be an explicitly adopted positive integer")
    config = {**DEFAULT_CONFIG, **config}
    model_policy.validate_policy(config)
    if not isinstance(config["model"], str) or not config["model"].strip():
        raise ValueError("model is required")
    if config["effort"] not in {"minimal", "low", "medium", "high", "xhigh"}:
        raise ValueError("unsupported reasoning effort")
    if not isinstance(config["role_models"], dict) or any(not isinstance(v, str) or not v for v in config["role_models"].values()):
        raise ValueError("role_models must map roles to model names")
    for role in config["role_models"]:
        schema_for(role)
    for key in ("operator_enabled", "scholarly_enabled", "claude_only_assigned_model"):
        if not isinstance(config[key], bool):
            raise ValueError(f"{key} must be a boolean")
    if not isinstance(config["operator_model"], str) or not config["operator_model"].strip():
        raise ValueError("operator_model must be nonempty")
    if config["operator_effort"] not in {"minimal", "low", "medium", "high", "xhigh", "max", "ultra"}:
        raise ValueError("unsupported operator reasoning effort")
    if config["scholarly_server"] is not None:
        validate_scholarly_server(config["scholarly_server"])
    for key in ("work_calls", "operations_calls"):
        if config[key] is not None and (isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1):
            raise ValueError(f"{key} must be a positive integer or null (unlimited)")
    for key in ("call_timeout_seconds",
                "max_cycles", "reviewers", "goal_auditors", "max_input_bytes",
                "review_rounds", "review_research_limit", "research_reconsider_seconds", "observation_interval_seconds",
                "observation_idle_seconds", "max_observation_reviews", "checkpoint_grace_seconds", "max_artifact_bytes",
                "operator_interval_seconds", "operator_timeout_seconds",
                "provider_retry_initial_seconds", "provider_retry_max_seconds", "finish_notice_seconds",
                "observation_unbounded_wait_seconds", "plan_settle_seconds"):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if isinstance(config.get("max_output_repairs", 1), bool) or not isinstance(config.get("max_output_repairs", 1), int) or config.get("max_output_repairs", 1) < 0:
        raise ValueError("max_output_repairs must be a nonnegative integer")
    if config["provider_retry_max_seconds"] < config["provider_retry_initial_seconds"]:
        raise ValueError("provider retry maximum must be at least the initial interval")
    command = config["lean_command"]
    if command is not None and (not isinstance(command, list) or not command or
                               any(not isinstance(x, str) or not x or "\0" in x for x in command)):
        raise ValueError("lean_command must be a nonempty argv list")
    if config["observation_mode"] not in {"event_driven", "periodic"}:
        raise ValueError("observation_mode must be event_driven or periodic")
    if not isinstance(config["allowed_axioms"], list) or any(not isinstance(a, str) or not a for a in config["allowed_axioms"]):
        raise ValueError("allowed_axioms must contain axiom names")
    if config.get('host_resources') is not None:
        import platform
        editions = execution_profiles.build_profiles(config)
        constraint = editions['capacity_constraints'][editions['host_capacity_ref']]
        if constraint['host_id'] != platform.node():
            raise ValueError('host_resources must name this local host')


def initialize(repository: Path, *, goal: str, workspace: Path, config: dict | None = None,
               title: str = "", goal_kind: str = "mathematical", policies: str = "",
               instance_id: str | None = None, sources: list[Path] | None = None) -> dict:
    if not goal.strip() or goal_kind not in {"mathematical", "research"}:
        raise ValueError("a goal and mathematical/research goal_kind are required")
    settings = deepcopy(DEFAULT_CONFIG)
    settings.update(config or {})
    if config and "session_limits" not in config and {"work_calls", "operations_calls", "model", "role_models", "operator_model"}.intersection(config):
        settings["session_limits"] = None
    if settings["session_limits"] is not None and config and {"model", "operator_model"}.intersection(config):
        raise ValueError("session mode selects models with tier_models; model is a legacy option")
    validate_config(settings)
    if settings["scholarly_enabled"]:
        settings["scholarly_server"] = resolve_scholarly_server(settings["scholarly_server"], start=Path.cwd())
    source_inputs = [(source.name, source.read_bytes()) for source in (sources or [])]
    instance_id = instance_id or new_id("RI")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    instance, runtime = initialization.initialize_state(instance_id=instance_id, goal=goal,
        goal_kind=goal_kind, workspace=workspace, config=settings, source_input=goal,
        title=title, policies=policies, created_at=now())
    from .governance_engine import bind_host_configuration
    settings = bind_host_configuration(instance, settings, origin='user')
    instance['config'] = settings
    profiles = execution_profiles.build_profiles(settings)
    instance.update(contract_id=CONTRACT, grants={})
    instance.update(profiles)
    runtime.update(contract_id=CONTRACT, cycles=0, active_execution=None, processed_controls=[],
                   question_links=[], updated_at=now(), reservations={}, provider_waits={})
    instance = knowledge_io.ensure_ontology(governance.ensure_governance(instance))
    instance = knowledge_records.initialize_families(instance)
    instance["feature_version"] = runtime["feature_version"] = STATE_FORMAT_VERSION
    store = _repository(repository, instance_id)
    with store.writer_lock():
        head = store.initialize(instance, runtime)
        if source_inputs:
            artifacts = {}
            bundle = new_id("BA")
            for i, (source_name, raw) in enumerate(source_inputs):
                path = f"runtime/artifacts/{bundle}/{i:04d}-{source_name}"
                artifacts[path] = raw
                instance["sources"].append({"id": new_id("SO"), "path": path, "name": source_name,
                                            "sha256": hashlib.sha256(raw).hexdigest()})
            head = store.save(head, instance, runtime, artifacts=artifacts)
    return {"instance_id": instance_id, "snapshot": head, "status": runtime["status"]}


def _control_result(store, head, runtime, request_id):
    row = next((row for row in runtime.get("history", [])
        if row.get("kind") in {"user_control", "rejected_user_control"}
        and row.get("request", {}).get("id") == request_id), None)
    if row is None or "result" not in row:
        return None
    parent = row["publication_parent"]
    store._store._validate_oid(parent)
    # One CAS has one parent. The first descendant contains this immutable receipt;
    # later requests must not substitute their status or configuration for it.
    commits = store._git("rev-list", "--first-parent", "--reverse", parent + ".." + head).stdout.decode().splitlines()
    if not commits:
        raise ValueError("control receipt has no published successor")
    return {**deepcopy(row["result"]), "snapshot": commits[0]}


def control(repository: Path, instance_id: str, action: str, *, text: str = "", config: dict | None = None,
            origin: str = "user", request_id: str | None = None, idempotency_key: str | None = None) -> dict:
    """Queue user commands; only the owning engine publishes authority changes."""
    if action not in {"pause", "resume", "close", "input", "configure", "request",
                      "decision", "knowledge", "trust", "external", "conversation", "source"}:
        raise ValueError("unknown control action")
    if origin not in {"user", "operator"}:
        raise ValueError("control origin must be user or operator")
    if origin == "operator" and action not in {"pause", "resume", "request", "configure", "source"}:
        raise ValueError("operator controls are limited to pause, resume, request, configure, and source")
    if request_id is not None and (not isinstance(request_id, str) or not 1 <= len(request_id) <= 128 or
            any(not (character.isascii() and (character.isalnum() or character in "-_")) for character in request_id)):
        raise ValueError("request_id must be a safe nonempty ASCII identifier")
    store = _repository(repository, instance_id)
    head, instance, runtime = store.load()
    if request_id is not None and idempotency_key is not None:
        raise ValueError("request_id and idempotency_key are mutually exclusive")
    if action == "source":
        config = dict(config or {})
        if "body_base64" in config:
            if set(config) != {"name", "body_base64", "sha256", "bytes"}:
                raise ValueError("normalized source requires exact name, body, hash and size")
            raw = base64.b64decode(config["body_base64"], validate=True)
            name = config["name"]
            if hashlib.sha256(raw).hexdigest() != config["sha256"] or len(raw) != config["bytes"]:
                raise ValueError("normalized source content differs from hash or size")
        else:
            path = Path(config["path"]).resolve(strict=True)
            raw = path.read_bytes()
            name = config.get("name") or path.name
        if not isinstance(name, str) or name in {"", ".", ".."} or "/" in name or "\\" in name:
            raise ValueError("source name must be a file name")
        config = {"name": name, "body_base64": base64.b64encode(raw).decode("ascii"),
                  "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    payload = {"instance_id": instance_id, "action": action, "text": text, "config": config or {}, "origin": origin}
    if request_id is None:
        from .cli import control_request_id
        request_id = control_request_id(instance_id, action, text=text, config=config, origin=origin,
                                        idempotency_key=idempotency_key)
    inbox = Path(instance["workspace"]) / "control" / instance_id
    destination = inbox / (request_id + ".json")
    def replay(prior):
        if lossless_json({key: prior.get(key) for key in payload}) != lossless_json(payload):
            raise ValueError("request_id reused with different payload")
        result = _control_result(store, head, runtime, request_id)
        return {"accepted": True, "request_id": request_id, "replayed": True,
                "effect": "already processed" if request_id in runtime.get("processed_controls", []) else "pending engine processing",
                **(result or {})}
    if destination.is_file():
        return replay(json.loads(destination.read_bytes()))
    for row in runtime.get("history", []):
        prior = row.get("request", {})
        if prior.get("id") == request_id:
            return replay(prior)
    _require_current_contract(instance, runtime)
    if action == "configure":
        current_config = {**deepcopy(DEFAULT_CONFIG), "session_limits": None, **instance["config"]}
        candidate = {**current_config, **(config or {})}
        if candidate.get("session_limits") is not None and {"model", "operator_model"}.intersection(config or {}):
            raise ValueError("session mode selects models with tier_models; model is a legacy option")
        if candidate.get("session_limits") is not None and {"work_calls", "operations_calls"}.intersection(config or {}):
            raise ValueError("session mode uses session_limits; explicitly set session_limits=null to configure legacy call budgets")
        validate_config(candidate)
        execution_profiles.build_profiles(candidate)
        if origin == "operator" and any(candidate[key] != current_config.get(key)
                                         for key in ("work_calls", "operations_calls", "session_limits", "tier_models", "role_tiers", "model", "role_models", "operator_model", "claude_only_assigned_model")):
            raise ValueError("changing resource capacity or model allocation requires a user decision")
    if action == "input" and not text.strip():
        raise ValueError("input text is required")
    if action == "input":
        responses = (config or {}).get("responds_to", [])
        available = {row["id"] for row in questions.open_links(runtime, "user")}
        if not isinstance(responses, list) or any(not isinstance(value, str) for value in responses) or len(responses) != len(set(responses)) or set(responses) - available:
            raise ValueError("responds_to must identify distinct open user questions")
    if action == "request":
        role = (config or {}).get("role")
        retry_action = (config or {}).get("retry_action")
        reassessment = (config or {}).get("assessment_reassessment")
        if retry_action is not None:
            if (not isinstance(retry_action, str) or not retry_action
                    or set(config or {}) != {"retry_action"}):
                raise ValueError("retry_action must be the sole nonempty request mode")
        elif role == "identity_review" and reassessment is not None:
            if (not isinstance(reassessment, dict) or set(reassessment) != {"assessment_id", "assessment_sha256", "evidence"}
                    or not isinstance(reassessment["evidence"], dict)):
                raise ValueError("assessment reassessment requires the exact assessment hash and defect evidence")
            assessment = instance.get("identity_assessments", {}).get(reassessment["assessment_id"])
            if not assessment or knowledge_records.digest(assessment) != reassessment["assessment_sha256"]:
                raise ValueError("assessment reassessment must identify the current original judgment")
            original = runtime.get("review_cycles", {}).get(assessment["review_cycle_id"], {})
            if config.get("target") not in {None, original.get("knowledge_id")}:
                raise ValueError("assessment reassessment target differs from the original judgment")
        elif role not in {"research_preparation", "research_plan", "supplemental_research", "operational_review", "maintenance"}:
            raise ValueError("unsupported requested role")
        if "cleanup_execution_ids" in (config or {}):
            ids = config["cleanup_execution_ids"]
            if role != "maintenance" or not isinstance(ids, list) or not ids or any(not isinstance(eid, str) for eid in ids) or len(set(ids)) != len(ids) or set(ids) - runtime["executions"].keys():
                raise ValueError("maintenance cleanup requires distinct existing execution IDs")
        if runtime["status"] in {"closed", "completed"}:
            raise ValueError("closed/completed instance cannot accept new research activities")
        if role == "supplemental_research":
            task = runtime["tasks"].get((config or {}).get("target"))
            if not task or planning.task_ready(task, instance, runtime, evaluation_context=_evaluation_context_for(store, head))["state"] != "ready":
                raise ValueError("supplemental research requires a task whose current contract is ready")
        if role == "operational_review" and (config or {}).get("target") not in runtime["executions"]:
            raise ValueError("operational review requires an existing execution ID")
    request = {"id": request_id, **payload, "created_at": now(),
               "accepted_order": f"{time.perf_counter_ns():020d}"}
    inbox.mkdir(parents=True, exist_ok=True)
    temporary = inbox / (request_id + "." + new_id("TMP") + ".tmp")
    temporary.write_bytes(lossless_json(request))
    try:
        # Publish a complete inbox record without overwriting a concurrent same-ID request.
        os.link(temporary, destination)
    except FileExistsError:
        return replay(json.loads(destination.read_bytes()))
    finally:
        temporary.unlink(missing_ok=True)
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
    for question in runtime.get("question_links", []):
        records.append({"family": "question", **question})
    for key, definition in instance.get("kind_definitions", {}).items():
        records.append({**definition, "family": "kind-definition", "definition_family": definition["family"]})
    for family in ("formal_results", "expositions", "identity_assessments", "assessment_uses",
                   "execution_profiles", "capacity_constraints", "capability_evidence"):
        records.extend({**record, "family": family} for record in instance.get(family, {}).values())
    for family in ("integrations", "reservations", "operational_dispositions", "observations"):
        records.extend({**record, "family": family} for record in runtime.get(family, {}).values()
                       if isinstance(record, dict) and record.get("id"))
    seen = set()
    for record in records:
        if record["id"] in seen:
            raise ValueError("record ID collision across families: " + record["id"])
        seen.add(record["id"])
    return sorted(records, key=lambda r: r["id"])


def _record_evidence(row):
    record = row["record"]
    semantic = semantic_content_hash(record)
    return {"snapshot": row["snapshot"], "path": row["path"], "json_pointer": row.get("json_pointer", "/record"),
            "sha256": row["sha256"], "bytes": len(row["bytes"]), "byte_scope": "persisted_file",
            "logical_sha256": exact_content_hash(record), "semantic_sha256": semantic,
            "semantic_projection": "exact_canonical_record/2"}


def _query_record(row):
    aliases = {"relations": "relation", "tasks": "task", "activities": "activity", "executions": "execution",
               "grants": "grant", "decisions": "decision", "external_operations": "external-operation",
               "review_cycles": "review-cycle", "trust_environments": "trust-environment", "sources": "source",
               "question_links": "question", "kind_definitions": "kind-definition"}
    record = deepcopy(row["record"])
    if row["family"] == "kind_definitions":
        record["definition_family"] = record["family"]
    record["family"] = aliases.get(row["family"], row["family"])
    return record


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
    store = _repository(repository, instance_id)
    head, instance, runtime = store.load(snapshot)
    descriptors = {row["id"]: row for row in store.records(head) if row["id"]}
    records = sorted((_query_record(row) for row in descriptors.values()), key=lambda row: row["id"])
    if kind:
        records = [r for r in records if r["family"] == kind or r.get("kind") == kind]
    if text:
        records = [r for r in records if text.casefold() in lossless_json(r).decode("utf-8").casefold()]
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
        next_cursor = base64.urlsafe_b64encode(lossless_json({"parameters": parameters, "snapshot": head,
                                                             "last": selected[-1]["id"]})).decode("ascii")
    return {"snapshot": head, "total": total, "loaded": len(selected), "truncated": truncated,
            "items": [{"record": r, **_record_evidence(descriptors[r["id"]])} for r in selected],
            "query_basis": {"parameters": parameters, "limit": limit, "complete": not truncated,
                            "snapshot": head, "loaded_ids": [row["id"] for row in selected]},
            "next_cursor": next_cursor}


def read_record(repository: Path, instance_id: str, record_id: str, *, snapshot: str | None = None) -> dict:
    store = _repository(repository, instance_id)
    row = store.read_record(record_id, snapshot)
    return {"record": _query_record(row), **_record_evidence(row)}


class ResearchEngine(QuestionEngineMixin, RevisionEngineMixin, DecisionEngineMixin, ProviderEngineMixin, SchedulerMixin, ReviewEngineMixin, LifecycleEngineMixin, AcademicEngineMixin, GovernanceEngineMixin):
    def _evaluation_context(self, snapshot=None):
        return _evaluation_context_for(self.store, snapshot or self.head)

    def _governance(self):
        lifecycle = self.instance.get("lifecycle", {}).get("state")
        unadopted = lifecycle == "initializing" or (lifecycle == "paused" and (
            self.runtime.get("resume_lifecycle") == "initializing" or
            self.runtime.get("status") == "closed" and not self.instance["lifecycle"].get("activated_at")))
        if unadopted and not any(row.get("kind") == "charter" and row.get("status") == "active"
                                for row in self.instance.get("governance", {}).values()):
            initial_input = next(row for row in self.runtime["inputs"]
                                 if row["id"] == self.instance["lifecycle"]["input_id"])
            return {**deepcopy(initial_input["config"]),
                    "status": "unadopted_input", "goal_revision": 0, "policy_revision": 0,
                    "source": deepcopy(self.instance["lifecycle"]["immutable_input"])}
        return governance.governance_view(self.instance)

    def __init__(self, repository: Path, instance_id: str, *, runner: Any = None, formal_verifier: Any = None):
        self.store = _repository(repository, instance_id)
        self.runner = runner or ModelRunner()
        self.formal_verifier = formal_verifier or verify_lean
        self.head, self.instance, self.runtime = self.store.load()
        self._saved_state = self._state_signature()
        _require_current_contract(self.instance, self.runtime)
        self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), "session_limits": None, **self.instance["config"]}
        self._live_execution_ids = set()
        self._executor_running = False
        self._inline_reviewing = False
        self._calls = None
        self._slots = None
        self._documents = all_prompt_documents()
        self._installation = self._installation_manifest()
        self._next_installation_check = 0.0
        self._preparing_input = False
        self._transport = ControlTransport(Path(self.instance["workspace"]) / "execution-control" / instance_id)
        self._transport_bindings = {}
        self._trackers = {}
        self._upgrade_runtime()
        self.instance = knowledge_io.ensure_ontology(self.instance)

    @staticmethod
    def _installation_manifest() -> dict:
        root = Path(__file__).resolve().parents[2]
        documents = dict.fromkeys(relative for paths in reading_map(skill_root=root).values() for relative in paths)
        documents.update(dict.fromkeys(["계약/독립-운영.md", "scripts/operator_schedule.ps1", "scripts/do_math.py"]))
        paths = [*sorted((root / "scripts" / "do_math").rglob("*.py")), *(root / relative for relative in documents)]
        files = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        return {"feature_version": STATE_FORMAT_VERSION, "files": files, "sha256": hashlib.sha256(canonical_json(files)).hexdigest()}

    def _execution_profile(self, action):
        profiles = self.instance["execution_profiles"]
        if action["role"] in execution_profiles.MACHINE_ROLES:
            selection = {}
        else:
            selection = self._select_model(action)
        allowed = self.instance.get("role_profile_refs", {}).get(action["role"])
        task = self.runtime["tasks"].get(action.get("target"))
        if task and action["role"] in {"research_work", "supplemental_research"}:
            task_refs = task.get("profile_refs", [])
            allowed = [execution_profiles.profile_ref(profiles[ref]) if isinstance(ref, str) else ref
                       for ref in task_refs]
        profile = execution_profiles.select_profile(profiles, action, selection, allowed_refs=allowed)
        action["profile_ref"] = execution_profiles.profile_ref(profile)
        action.update(actor_kind=profile["actor_kind"], budget_kind=profile["budget_kind"])
        if selection:
            action["model_selection"] = {**selection, "profile_ref": deepcopy(action["profile_ref"])}
        return profile

    def _activity_for_action(self, action):
        action.setdefault("id", new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        parent_id = action.get("continuation_of")
        if not parent_id:
            for field in ("repair", "recovery", "refresh"):
                parent_id = action.get(field, {}).get("execution_id")
                if parent_id:
                    break
        if parent_id:
            parent = self.runtime["executions"].get(parent_id)
            if parent is None or parent["status"] != "ended":
                raise ValueError("continuation requires an ended, explicitly referenced execution")
            action["continuation_of"] = parent_id
            if action.get("owner_activity_id", parent["owner_activity_id"]) != parent["owner_activity_id"]:
                raise ValueError("continuation cannot change its activity")
            action["owner_activity_id"] = parent["owner_activity_id"]
        aid = action.get("owner_activity_id")
        if aid is None:
            aid = new_id("AY")
            activities.open_activity(self.runtime, activity_id=aid, activity_kind=action["role"],
                owner_ref=action["lineage_id"], input_refs=[action["target"]] if action.get("target") else [],
                opened_at=now())
            action["owner_activity_id"] = aid
        activity = self.runtime["activities"][aid]
        if activity["status"] == "finished":
            raise ValueError("finished activity cannot be continued")
        for queued in self.runtime["queue"]:
            if queued.get("id") == action["id"]:
                queued.update(deepcopy(action))
        return activity

    def _register_execution(self, action, execution):
        """Shared binding used by AI, formal, trust and external creation sites."""
        revisions.bind_repetition_bases(self.instance, self.runtime, action)
        profile = self._execution_profile(action)
        activity = self._activity_for_action(action)
        requested_state = execution.get("status", "queued")
        base = execution_lifecycle.create_execution(execution_id=execution["id"], owner_activity_id=activity["id"],
            actor_kind=profile["actor_kind"], input_manifest=execution.get("input_manifest", []),
            profile_ref=execution_profiles.profile_ref(profile), created_at=execution.get("created_at", now()),
            continuation_of=action.get("continuation_of"), context_origin=action.get("context_origin", []))
        execution.update(base, action=deepcopy(action), budget_kind=profile["budget_kind"])
        if action["role"] == "intent_interpretation" and action.get("stage") == "check":
            execution["intent_import_sha256"] = self.runtime["intent_imports"][action["import_id"]]["sha256"]
        execution.pop("activity_id", None)
        execution_profiles.bind_execution(execution, profile)
        if profile["actor_kind"] == "ai":
            execution.update(model=profile["ai"]["model"], effort=profile["ai"]["effort"])
        else:
            for field in ("model", "effort", "model_selection"):
                execution.pop(field, None)
        held = activity.get("waiting", {}).get("reason") in {"review_input_restoration", "review_recovery"}
        admission = ({"disposition": "review_input_restoration"} if held else self._admit_review_execution(action, execution))
        if admission["disposition"] not in {"admitted", "already_admitted", "not_applicable"}:
            if admission['disposition'] in {'review_budget_exhausted', 'review_scope_unaffordable',
                                             'review_followup_reserved', 'review_resource_pending'}:
                self._request_review_resource_disposition(action, admission['disposition'], admission)
                return None
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": deepcopy(action),
                "kind": admission["disposition"], "detail": admission, "next_owner": "review_policy"}
            activities.wait_for(self.runtime, activity["id"], reason=admission["disposition"],
                condition=admission, next_owner="review_policy", at=now())
            self._remove_action(action)
            return None
        if activity["status"] == "waiting":
            activities.resume_activity(self.runtime, activity["id"], condition=activity["waiting"]["condition"], at=now())
        machine_admission = profile["actor_kind"] == "machine" and requested_state in {"starting", "running"}
        if machine_admission:
            slots = self._provider_slots()
            if not slots.acquire(execution["id"], profile["budget_kind"], None,
                                 profile=profile, execution=execution):
                action["dispatch_wait"] = deepcopy(slots.admission_wait)
                activities.wait_for(self.runtime, activity["id"], reason="machine capacity unavailable",
                    condition=deepcopy(action["dispatch_wait"]), next_owner=action["dispatch_wait"]["next_owner"], at=now())
                return None
            action.pop("dispatch_wait", None)
            execution["action"] = deepcopy(action)
        elif requested_state in {"starting", "running"}:
            execution_lifecycle.transition_execution(execution, "starting", at=now())
        if requested_state == "running" and not (machine_admission and profile.get("host_resources")):
            execution_lifecycle.transition_execution(execution, "running", at=now())
        activities.assign_execution(self.runtime, activity["id"], execution)
        revisions.record_import_rework(self.instance, self.runtime, action, execution['id'])
        return execution

    def _machine_started(self, execution_id, identity):
        """Publish the admitted machine Job identity before its root resumes."""
        execution = self.runtime["executions"][execution_id]
        if execution["actor_kind"] != "machine":
            raise ValueError("machine process callback requires a machine execution")
        self._provider_slots().started(execution_id, identity)
        execution_lifecycle.transition_execution(execution, "running", at=now())
        execution.update(process=json_safe(identity), started_at=now())
        self._save()

    def _settle_activity(self, execution_id):
        self._settle_review_resource_dispositions()
        execution = self.runtime["executions"][execution_id]
        aid = execution["owner_activity_id"]
        activity = self.runtime["activities"][aid]
        cycle = self.runtime.get("review_cycles", {}).get(execution.get("action", {}).get("review_cycle_id"), {})
        from .review_cycle import resource_disposition
        if resource_disposition(cycle):
            return
        if cycle.get("proposal", {}).get("assessment_reassessment"):
            self._settle_assessment_reassessments()
            activity = self.runtime["activities"][aid]
        if activity["status"] == "finished" or any(
                self.runtime["executions"][eid]["status"] != "ended" for eid in activity["assigned_execution_ids"]):
            return
        repairs = [row["id"] for row in self.runtime.get("operational_dispositions", {}).values()
            if row.get("disposition", {}).get("kind") == "repair"
            and row.get("target_execution_id") in activity["assigned_execution_ids"]
            and row.get("status") not in {"applied", "repair_deferred", "repair_verification_failed"}]
        if repairs:
            if activity["status"] != "waiting":
                activities.wait_for(self.runtime, aid, reason="operational repair remains pending",
                    condition={"operational_disposition_ids": repairs}, next_owner="engine", at=now())
            return
        pending = [row for row in self.runtime["queue"] if row.get("owner_activity_id") == aid]
        waiting = [row for row in self.runtime.get("waiting_actions", {}).values()
                   if row.get("action", {}).get("owner_activity_id") == aid]
        references = [self.runtime["executions"][eid]["result_ref"] for eid in activity["assigned_execution_ids"]
                      if self.runtime["executions"][eid].get("result_ref")]
        activity["result_refs"] = list(dict.fromkeys(references))
        if pending:
            return
        if waiting:
            wait = waiting[0]
            reason = (wait['kind'] if wait.get('kind') in {'review_input_restoration', 'review_recovery', 'review_authority'}
                      else wait.get('reason') or wait['kind'])
            activities.wait_for(self.runtime, aid, reason=reason,
                condition={"action_ids": [row["action"]["id"] for row in waiting]},
                next_owner=waiting[0].get("next_owner", "engine"), at=now())
            return
        activities.finish_activity(self.runtime, aid, result_refs=activity["result_refs"],
            unresolved=[] if execution["outcome"] == "output_accepted" or execution.get("formal_status") == "verified"
                          else [{"execution_id": execution_id, "reason": execution.get("error") or execution["outcome"]}],
            followups=[], at=now())

    def _render_prompt(self, role: str, context: dict, **kwargs) -> str:
        return render_prompt(role, context, documents=self._documents[role], **kwargs)

    def _check_installation(self, *, force=False):
        current = time.monotonic()
        if not force and current < self._next_installation_check:
            return True
        self._next_installation_check = current + 1.0
        if self._installation_manifest() == self._installation:
            return True
        if self.runtime["status"] not in {"closed", "completed"}:
            self.runtime["status"] = "paused"
        message = "Installed code or role documents changed. Restart the executor to load one consistent version, then resume."
        if message not in self.runtime["questions"]:
            self.runtime["questions"].append(message)
        self._save()
        return False

    def _preparation_checkpoint(self):
        if self._preparing_input and self._inbox():
            raise InputPreparationInterrupted()

    def _continue_prepared_action(self, execution):
        """Retain one action's activity and explicit attempt lineage after cancellation."""
        aid = execution["action"]["id"]
        actions = [row for row in self.runtime["queue"] if row.get("id") == aid]
        actions += [row["action"] for row in self.runtime.get("waiting_actions", {}).values()
                    if row.get("action", {}).get("id") == aid]
        for action in actions:
            action.update(owner_activity_id=execution["owner_activity_id"], continuation_of=execution["id"])

    def _discard_prepared_input(self, base: Path, execution_id: str, *, reason="input preparation interrupted", cancelled=True):
        resolved = base.resolve(strict=True)
        runs = (Path(self.instance["workspace"]) / "runs").resolve()
        execution = self.runtime["executions"].get(execution_id)
        if (resolved.parent != runs or resolved.name != execution_id or not execution
                or execution["status"] != "queued" or execution.get("input_bundle")):
            raise ValueError("only this unpublished execution input may be discarded")
        execution_lifecycle.end_preparation(execution, at=now(),
            stage=execution.get("input_preparation", {}).get("stage", "context"), reason=reason, cancelled=cancelled)
        self._continue_prepared_action(execution)
        self._settle_activity(execution_id)
        self._save()
        binding = self._transport_bindings.pop(execution_id, None)
        if binding is not None:
            self._transport.close(binding, reason="execution was not admitted")
        shutil.rmtree(resolved)

    def _input_artifacts(self, bundle: str, role: str, prompt: str, schema: dict, fitted: dict,
                         workspace: Path) -> dict[str, bytes]:
        base = f"runtime/artifacts/{bundle}"
        documents = self._documents[role]
        manifest = deepcopy(fitted["manifest"])
        support = []
        artifacts = {f"{base}/input.txt": prompt.encode("utf-8"), f"{base}/schema.json": lossless_json(schema),
                     f"{base}/manifest.json": canonical_json(manifest),
                     **{f"{base}/input/implementation/{document['path']}": document["content"].encode("utf-8")
                        for document in documents}}
        for entry in manifest["catalog"]:
            source = read_source(workspace, entry, limit=max(1, entry["bytes"]))
            if source["status"] != "ok" or source["truncated"]:
                raise ValueError("input catalog could not be preserved: " + entry["path"])
            artifacts[f"{base}/{entry['path']}"] = source["bytes"]
        for directory in (workspace / "input/tools", workspace / "input/submission"):
            for path in sorted(directory.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                raw = path.read_bytes()
                relative = path.relative_to(workspace).as_posix()
                artifacts[f"{base}/{relative}"] = raw
                support.append({"key": "submission_support", "path": relative,
                                 "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        artifacts[f"{base}/support-manifest.json"] = canonical_json(support)
        artifacts.update(fitted.get("artifacts", {}))
        return artifacts

    def _state_signature(self):
        return (self.head, lossless_json(self.instance),
                lossless_json({k: v for k, v in self.runtime.items() if k != "updated_at"}))

    def _save(self, artifacts: dict[str, bytes] | None = None) -> None:
        if self._session_mode():
            live = [eid for eid, e in self.runtime["executions"].items() if e["status"] != "ended"]
            self.runtime["active_executions"] = live
            self.runtime["active_execution"] = live[0] if live else None
        for task_id, task in self.runtime["tasks"].items():
            if not task.get("pending_withdrawal"):
                continue
            live_work = any(execution.get("status") != "ended"
                            and execution.get("role") in {"research_work", "supplemental_research"}
                            and execution.get("action", {}).get("target") == task_id
                            and not execution.get("action", {}).get("review_cycle_id")
                            for execution in self.runtime["executions"].values())
            if not live_work:
                task["status"] = "closed"
                task.pop("pending_withdrawal")
                self.runtime["queue"] = [action for action in self.runtime["queue"]
                                         if action.get("target") != task_id]
        state = self._state_signature()
        if not artifacts and state == self._saved_state:
            return
        anchor = getattr(self, "_clock_anchor", None)
        # A rejected later sample never overwrites the last accepted anchor.
        # Persist that accepted high-water mark with this ordinary state change.
        if anchor:
            if anchor[0] > governance.timestamp(self.runtime["last_observed_utc"]):
                self.runtime["last_observed_utc"] = anchor[0].isoformat()
        self.runtime["updated_at"] = now()
        self.head, self.instance, self.runtime = self.store.save_with_state(
            self.head, self.instance, self.runtime, artifacts=artifacts)
        self._saved_state = self._state_signature()
        for slots in (getattr(self, "_slots", None), getattr(self, "_classic_provider_slots", None)):
            if slots is not None and hasattr(slots, "runtime"):
                slots.runtime, slots.instance = self.runtime, self.instance

    def _record_control_result(self, request, *, rejected=False, reason=None, **details):
        self.runtime["history"].append({"kind": "rejected_user_control" if rejected else "user_control",
            "request": deepcopy(request), "reason": reason, **details, "publication_parent": self.head,
            "result": {"effect": "rejected" if rejected else "applied", "reason": reason,
                "status": self.runtime["status"], "config": deepcopy(self.instance["config"])
                    if request["action"] == "configure" else None}})

    def control_result(self, request_id):
        return _control_result(self.store, self.head, self.runtime, request_id)

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
        # ULID suffixes are random within a millisecond; they do not preserve
        # the order in which a pause, release, or newer user control arrived.
        # Distinct calls can share even the complete wall-clock timestamp.
        # Preserve their host acceptance order; old records retain the ID tie-break.
        return sorted(results, key=lambda request: (request["created_at"], request.get("accepted_order", ""), request["id"]))

    def _controls(self, *, pump=True) -> None:
        if pump and self._calls is not None:
            self._calls.pump()
        if pump and getattr(self, "_transport", None) is not None:
            self._transport.pump(self._publish_control_request)
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
                    self._record_control_result(request, reason="source content unchanged", source_id=old["id"])
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
                if self.runtime["status"] in {"waiting", "budget_exhausted", "capacity_waiting"}: self.runtime["status"] = "ready"
                self.runtime["processed_controls"].append(request["id"])
                self._record_control_result(request, source_id=entry["id"])
                self._lifecycle_event("source_imported", target=entry["id"], source_ref=request["id"])
                self._save({entry["path"]: raw})
                continue
            try:
                handled = self._review_recovery_control(request) or self._knowledge_io_control(request) or self._academic_control(request) or self._governance_control(request) or self._apply_extended_control(request)
            except (ValueError, KeyError, TypeError) as error:
                self._reject_control(request, str(error))
                continue
            if handled:
                self.runtime["processed_controls"].append(request["id"])
                self._record_control_result(request)
                self._save()
                continue
            if action == "pause":
                if self.runtime["status"] not in {"completed", "closed"}:
                    self._pause_lifecycle(request["text"] or "user_pause")
                    if request.get("config", {}).get("model_policy_violation"):
                        self.runtime["model_policy_violation"] = deepcopy(request["config"]["model_policy_violation"])
                    if request.get("origin", "user") == "user":
                        self.runtime["user_pause"] = {"request_id": request["id"],
                            "reason": request["text"], "created_at": request["created_at"]}
            elif action == "close":
                self.runtime["status"] = "closed"
                self.runtime["queue"] = []
            elif action == "resume":
                try:
                    self._check_conversations()
                    self._resume_lifecycle(request)
                except (ValueError, RuntimeError) as error:
                    self._reject_control(request, str(error))
                    continue
                if self.instance["lifecycle"]["state"] == "initializing":
                    self._activate_initialization()
                    self.runtime["processed_controls"].append(request["id"])
                    self._record_control_result(request)
                    self._save()
                    continue
                for aid, waiting in list(self.runtime.get("waiting_actions", {}).items()):
                    # Resume resolves the pause, not unrelated input or authority conditions.
                    if waiting.get("kind") not in {"paused", "user_pause", "conversation_lost"}:
                        continue
                    if waiting.get("question"):
                        self.runtime["questions"] = [q for q in self.runtime["questions"] if q != waiting["question"]]
                    self.runtime["queue"].append(waiting["action"])
                    del self.runtime["waiting_actions"][aid]
                if not self.runtime["queue"]:
                    role = "research_plan" if self.runtime["tasks"] or self.instance["knowledge"] else "research_preparation"
                    self._enqueue(role, reason=request["text"] or "explicit user resume")
            elif action == "input":
                if self.runtime["status"] in {"closed", "completed"}:
                    self._reject_control(request, "new research input requires an unfinished instance")
                    continue
                self.runtime["inputs"].append(request)
                if self.runtime["status"] not in {"closed", "completed", "paused"}:
                    self.runtime["status"] = "ready"
                self._enqueue("intent_interpretation", request["id"], reason="new user input", front=not self._session_mode())
            elif action == "request":
                if self.runtime["status"] in {"completed", "closed"}:
                    self._reject_control(request, "instance ended before the activity request was applied")
                    continue
                if request["config"].get("retry_action") is not None:
                    try:
                        self._retry_input_overflow_action(request)
                    except (ValueError, KeyError, TypeError) as error:
                        self._reject_control(request, str(error))
                        continue
                    self.runtime["processed_controls"].append(request["id"])
                    self._record_control_result(request, retry_action=request["config"]["retry_action"])
                    self._save()
                    continue
                role, target = request["config"]["role"], request["config"].get("target")
                if role == "supplemental_research":
                    task = self.runtime["tasks"].get(target)
                    if task is None or planning.task_ready(task, self.instance, self.runtime, evaluation_context=self._evaluation_context())["state"] != "ready":
                        self._reject_control(request, "supplemental task is no longer ready")
                        continue
                    task.update(selected_by=request["id"])
                requested = {"role": role, "reason": request["text"], "requested_by": request["id"]}
                if target:
                    requested["target"] = target
                if role == "maintenance" and "cleanup_execution_ids" in request["config"]:
                    requested["cleanup_execution_ids"] = deepcopy(request["config"]["cleanup_execution_ids"])
                self._enqueue(requested.pop("role"), requested.pop("target", None), front=not self._session_mode(), **requested)
                if self.runtime["status"] in {"waiting", "budget_exhausted", "capacity_waiting"}:
                    self.runtime["status"] = "ready"
            else:
                raise ValueError("unsupported control action")
            self.runtime["processed_controls"].append(request["id"])
            self._record_control_result(request)
            self._save()
        self._schedule_operational_reviews()
        self._retry_submission_publications()
        self._retry_impact_reviews()
        if self._reconcile_review_host_profiles() or self._settle_review_resource_dispositions():
            self._save()
        repair_execution.continue_initial_retries(self)
        self._run_pending_operational_repairs()
        if any(cycle.get("proposal", {}).get("assessment_reassessment") for cycle in self.runtime.get("review_cycles", {}).values()):
            if self._settle_assessment_reassessments():
                self._save()
        delivered = getattr(self, "_feedback_delivered", set())
        for receipt in self.runtime.get("control_receipts", {}).values():
            execution = self.runtime["executions"].get(receipt["execution_id"], {})
            if receipt["id"] not in delivered and execution.get("status") == "running":
                try:
                    self._redeliver_control_feedback(receipt)
                except OSError:
                    continue  # Delivery can be retried without revoking its durable receipt.
                delivered.add(receipt["id"])
        self._feedback_delivered = delivered

    def _retry_submission_publications(self):
        if self.runtime.get("status") in {"paused", "closed"} or getattr(self, "_retrying_publication", False):
            return
        pending = [deepcopy(row) for row in self.runtime.get("waiting_actions", {}).values()
                   if row.get("kind") == "submission_publication"]
        self._retrying_publication = True
        try:
            for waiting in pending:
                execution = self.runtime["executions"][waiting["execution_id"]]
                action = waiting["action"]
                prefix = f"runtime/artifacts/{execution['input_bundle']}"
                try:
                    context = submission.load_json(self.store.read(prefix + "/input/submission/context.json", self.head))
                    schema = submission.load_json(self.store.read(prefix + "/schema.json", self.head))
                    self._receive_submission(action, {}, execution["id"], context, schema,
                        Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace", preserved=True)
                    if (execution.get('role') == 'goal_audit'
                            and self.runtime['executions'][execution['id']].get('outcome') == 'output_accepted'):
                        self._settle_activity(execution['id'])
                    self._save()
                except submission.SealedSubmissionError as error:
                    live = self.runtime.setdefault("waiting_actions", {})[action["id"]]
                    live.update(kind="submission_failure", reason=str(error), next_owner="engine")
                    repair_execution.route_failed_action(self, action, execution["id"],
                        reason="Diagnose unreadable sealed submission")
                    self._save()
                except (ValueError, OSError, GitStateStoreError) as error:
                    self.runtime.setdefault("waiting_actions", {})[action["id"]] = {**waiting, "reason": str(error)}
                    self._save()
        finally:
            self._retrying_publication = False

    def _sealed_submission_files(self, execution):
        """Recover exact research files frozen by the accepted submission receipt."""
        intent = execution.get("submission_intent", {})
        entries = intent.get("file_refs")
        if not isinstance(entries, list):
            return None
        files = {}
        manifest = []
        for row in entries:
            raw = self.store.read(row["artifact_ref"], self.head)
            if hashlib.sha256(raw).hexdigest() != row["sha256"] or len(raw) != row["bytes"]:
                raise ValueError("sealed submission file differs from its receipt: " + row["path"])
            files[row["path"]] = raw
            manifest.append({key: deepcopy(row[key]) for key in ("path", "sha256", "bytes")})
        return {"files": files, "manifest": manifest, "omitted": [], "complete": True}

    def _hold_impact_reviews(self, action, execution_id, received):
        waiting = self.runtime.setdefault("waiting_actions", {}).setdefault(action["id"], {
            "action": deepcopy(action), "kind": "impact_review", "execution_id": execution_id,
            "review_requests": {}, "review_execution_ids": {}, "next_owner": "impact_review",
            "reason": "The preserved bundle requires independent impact judgment"})
        waiting.update(kind="impact_review", next_owner="impact_review")
        for row in received["bundles"]:
            if row.get("next_owner") != "impact_review":
                continue
            request = row["impact_review_request"]
            identifier = row["integration_id"]
            if identifier in waiting["review_requests"]:
                if waiting["review_requests"][identifier] != request:
                    waiting.update(kind="impact_review_changed", next_owner="research_preparation",
                                   reason="Impact premises changed while the original mutation remained held")
                    self._enqueue("research_preparation", reason=waiting["reason"])
                continue
            waiting["review_requests"][identifier] = deepcopy(request)
            self._enqueue("maintenance", execution_id, stage="impact_review", basis=request["payload_sha256"],
                input_basis={"impact_review": deepcopy(request)},
                reason="Independently judge the exact preserved bundle and its whole/per-change impact plans")

    def _hold_unreadable_impact_submission(self, waiting, error):
        action = waiting["action"]
        live = self.runtime["waiting_actions"][action["id"]]
        live.update(kind="submission_failure", next_owner="engine", reason=str(error))
        repair_execution.route_failed_action(self, action, waiting["execution_id"],
            reason="Diagnose unreadable sealed impact submission")
        self._save()

    def _retry_impact_reviews(self):
        if self.runtime.get("status") in {"paused", "closed", "completed"}:
            return
        pending = [deepcopy(row) for row in self.runtime.get("waiting_actions", {}).values()
                   if row.get("kind") == "impact_review"]
        for waiting in pending:
            judgments, references = {}, {}
            try:
                producer = self.runtime["executions"][waiting["execution_id"]]
                producer_output = submission.read_sealed_submission(producer, self.head,
                    lambda snapshot, path: self.store.read(path, snapshot))["output"]
            except (ValueError, OSError, GitStateStoreError) as error:
                self._hold_unreadable_impact_submission(waiting, error)
                continue
            failed = False
            for identifier, request in waiting["review_requests"].items():
                reviews = [execution for execution in self.runtime["executions"].values()
                    if execution.get("status") == "ended" and execution.get("outcome") == "output_accepted"
                    and execution.get("action", {}).get("stage") == "impact_review"
                    and execution["action"].get("input_basis", {}).get("impact_review") == request]
                if not reviews:
                    break
                review = reviews[-1]
                try:
                    review_output = submission.read_sealed_submission(review, self.head,
                        lambda snapshot, path: self.store.read(path, snapshot))["output"]
                    judgments[identifier] = integration.validate_impact_review_response(request, review_output)
                except (ValueError, OSError, GitStateStoreError) as error:
                    self._hold_unreadable_impact_submission(waiting, error)
                    failed = True
                    break
                references[identifier] = review["id"]
            if failed:
                continue
            if set(judgments) != set(waiting["review_requests"]):
                continue
            live = self.runtime["waiting_actions"][waiting["action"]["id"]]
            live["review_execution_ids"] = references
            if any(row["decision"] != "approve" for decisions in judgments.values() for row in decisions.values()):
                live.update(kind="impact_review_blocked", next_owner="research_preparation",
                            reason="Independent impact review rejected or could not resolve the held mutation")
                execution = self.runtime["executions"][waiting["execution_id"]]
                self._record_task_receipt(waiting["action"], producer_output, execution["id"], accepted=False)
                self._enqueue("research_preparation", reason=live["reason"])
                self._save()
                continue
            execution = self.runtime["executions"][waiting["execution_id"]]
            prefix = "runtime/artifacts/" + execution["input_bundle"]
            context = submission.load_json(self.store.read(prefix + "/input/submission/context.json", self.head))
            schema = submission.load_json(self.store.read(prefix + "/schema.json", self.head))
            self._receive_submission(waiting["action"], {}, execution["id"], context, schema,
                Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace", preserved=True)
            self._settle_activity(execution["id"])
            self._save()

    def _schedule_operational_reviews(self):
        due = []
        for execution in self.runtime["executions"].values():
            request = execution.get("operational_continuation", {})
            next_review = request.get("next_review")
            if (execution["status"] == "running" and next_review and not request.get("dispatched_at")
                    and execution["id"] not in getattr(self, "_trackers", {})):
                if governance.timestamp(next_review["at"]) <= self._lifecycle_now():
                    due.append((execution["id"], request, next_review))
        if not due or not self._clock_guard()["usable"]:
            return
        for identifier, request, next_review in due:
            self._enqueue("operational_review", identifier, live=True,
                reason=next_review["reason"], observation={"kind": "scheduled_review_due", "disposition_id": request["disposition_id"]},
                observation_refs=[request["disposition_id"]])
            request["dispatched_at"] = now()
        self._save()

    def _publish_control_request(self, request):
        """A transport acceptance acknowledges this CAS, not mathematical acceptance."""
        safe_request = {key: deepcopy(value) for key, value in request.items() if key != "capability"}
        digest = hashlib.sha256(lossless_json(safe_request)).hexdigest()
        prior = next((row for row in self.runtime.get("control_receipts", {}).values()
                      if row["request_id"] == request["request_id"]), None)
        if prior:
            if prior["request_sha256"] != digest:
                return {"state": "rejected", "reason": "request identity reused with different content"}
            self._redeliver_control_feedback(prior)
            return self._control_receipt_response(prior)
        execution = self.runtime["executions"].get(request["execution_id"])
        if not execution or execution["status"] != "running" or execution.get("grant_id") != request["grant_id"]:
            return {"state": "rejected", "reason": "execution is no longer running under this grant"}
        if not governance.authorize(self.instance, {**execution["action"], "grant_id": request["grant_id"]}, runtime=self.runtime)["allowed"]:
            return {"state": "rejected", "reason": "execution authority no longer permits this request"}
        if not self._clock_guard()["usable"]:
            return {"state": "rejected", "reason": "clock regression prevents new acceptance"}
        if request["kind"] == "submission_preview":
            try:
                return {"state": "previewed", "result": self._preview_submission(execution, request["payload"])}
            except (ValueError, KeyError, TypeError, OSError):
                return {"state": "rejected", "reason": "preview input or authority could not be verified"}
        submission_artifacts = {}
        sealed_submission = None
        if request["kind"] == "submit_intent":
            workspace = Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace"
            draft_path = request["payload"].get("draft_path") or request["payload"].get("raw_output_path")
            if not isinstance(draft_path, str):
                return {"state": "rejected", "reason": "submission requires a workspace-relative draft_path"}
            base = f"runtime/artifacts/{execution['input_bundle']}"
            context = submission.load_json(self.store.read(base + "/input/submission/context.json", self.head))
            schema = submission.load_json(self.store.read(base + "/schema.json", self.head))
            try:
                sealed_submission = submission.seal_submission(workspace, draft_path,
                    execution_id=execution["id"], context=context, schema=schema,
                    max_artifact_bytes=self.instance["config"]["max_artifact_bytes"])
            except (ValueError, KeyError, TypeError, OSError) as error:
                return {"state": "rejected", "reason": str(error)}
        original_instance, original_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        original_head = self.head
        tracker = self._trackers.get(execution["id"]) if hasattr(self, "_trackers") else None
        live_tracker = tracker
        tracker = deepcopy(tracker) if tracker is not None else None
        boundary_updates = []
        feedback = []
        receipt = {"id": new_id("CT"), "request_id": request["request_id"], "request_sha256": digest,
            "execution_id": execution["id"], "kind": request["kind"], "state": "accepted", "received_at": now(),
            "request": safe_request, "parent_snapshot": self.head}
        try:
            if request["kind"] == "submit_intent":
                submission_artifacts = self._stage_submission_capture(execution, sealed_submission, receipt,
                    origin='explicit_tool')
                if sealed_submission['capture_eligible'] and tracker is not None:
                    tracker.set_execution_status("stopping")
            elif request["kind"] == "safety_boundary":
                payload = request["payload"]
                if payload.get("inflight_calls") is not False:
                    raise ValueError("safety boundary must explicitly report no inflight calls")
                execution["safe_boundary_report"] = {"receipt_id": receipt["id"], **deepcopy(payload)}
                if tracker is not None:
                    call_ids = payload.get("call_ids", [])
                    if not isinstance(call_ids, list) or any(cid not in tracker.pending_tools for cid in call_ids):
                        raise ValueError("safe boundary call IDs must identify observed calls of this execution")
                    pending_research = set(tracker.pending_tools) - tracker.self_check_call_ids
                    if pending_research - set(call_ids):
                        raise ValueError("safe boundary omits observed inflight research calls")
                    boundary_updates = tracker.record_safe_boundary(receipt["id"], call_ids=call_ids)
                    self.runtime.setdefault("self_check_obligations", {}).update(deepcopy(tracker.obligations))
            elif request["kind"] == "self_check_response":
                if tracker is None:
                    raise ValueError("self-check has no current tracker")
                payload = request["payload"]
                response = payload["response"]
                if response.get("obligation_id") != payload["self_check_id"]:
                    raise ValueError("self-check response refers to another issued obligation")
                available = self._control_evidence_refs(execution)
                record = tracker.record_self_check_response(response, available_evidence_refs=available, receipt_id=receipt["id"])
                record = persistent_record(record)
                self.runtime.setdefault("self_check_responses", {})[record["id"]] = record
                self.runtime.setdefault("self_check_obligations", {}).update(deepcopy(tracker.obligations))
                if record["kind"] == "self_check_rejected":
                    receipt["state"] = "rejected"
                for item in (record, record.get("rule_update", {})):
                    if item.get("worker_feedback"):
                        feedback.append(item["worker_feedback"])
                if record["followup"]["kind"] == "operational_review_due":
                    self._enqueue("operational_review", execution["id"], live=True,
                        observation=deepcopy(record), obligation_ids=[response["obligation_id"]],
                        observation_refs=[record["id"]])
            self.runtime.setdefault("control_receipts", {})[receipt["id"]] = receipt
            self._save(submission_artifacts)
        except Exception as error:
            # A publisher can commit and then lose its acknowledgment. Resolve
            # the receipt from durable state before deciding whether to retry.
            persisted = None
            try:
                head, instance, runtime = self.store.load()
                persisted = next((row for row in runtime.get("control_receipts", {}).values()
                    if row["request_id"] == request["request_id"] and row["request_sha256"] == digest), None)
                self.head, self.instance, self.runtime = head, instance, runtime
            except Exception:
                if self.head == original_head:
                    self.instance, self.runtime = original_instance, original_runtime
            if not persisted:
                return {"state": "rejected", "reason": str(error)}
            receipt = persisted
        if live_tracker is not None and tracker is not None:
            live_tracker.__dict__.clear()
            live_tracker.__dict__.update(tracker.__dict__)
        workspace = Path(self.instance.get("workspace", ".")) / "runs" / execution["id"] / "workspace"
        for obligation in boundary_updates:
            feedback.append(self_check_feedback(obligation))
        for item in feedback:
            try:
                publish_worker_feedback(workspace / ".control", item)
            except OSError as error:
                self.runtime["history"].append({"kind": "feedback_delivery_failed", "receipt_id": receipt["id"], "error": str(error)})
        return self._control_receipt_response(receipt)

    def _control_receipt_response(self, receipt):
        result = {"state": receipt["state"], "published": True, "snapshot": self.head, "publication_id": receipt["id"]}
        if receipt["state"] == "rejected":
            result["reason"] = receipt.get('reason', "self-check response was preserved and returned for correction")
            evidence = receipt.get('payload', {}).get('submission_check')
            if evidence:
                result['result'] = submission.load_json(self.store.read(evidence['check_ref'], self.head))
        return result

    def _redeliver_control_feedback(self, receipt):
        feedback = []
        for record in self.runtime.get("self_check_responses", {}).values():
            if record.get("receipt_ref") == receipt["id"]:
                feedback.extend(item["worker_feedback"] for item in (record, record.get("rule_update", {})) if item.get("worker_feedback"))
        for obligation in self.runtime.get("self_check_obligations", {}).values():
            if obligation.get("boundary_receipt_ref") == receipt["id"]:
                feedback.append(self_check_feedback(obligation))
        workspace = Path(self.instance.get("workspace", ".")) / "runs" / receipt["execution_id"] / "workspace"
        for item in feedback:
            publish_worker_feedback(workspace / ".control", item)

    def _control_evidence_refs(self, execution):
        base = f"runtime/artifacts/{execution['input_bundle']}"
        context = submission.load_json(self.store.read(base + "/input/submission/context.json", self.head))
        refs = {row["value"] for row in context.get("reference_catalog", [])}
        for family in ("observation_facts", "self_check_obligations", "self_check_responses"):
            refs.update(row["id"] for row in self.runtime.get(family, {}).values()
                        if row.get("execution_id") == execution["id"])
        for row in execution.get("output_files", []):
            raw = self.store.read(row["artifact_ref"], self.head)
            if hashlib.sha256(raw).hexdigest() == row["sha256"]:
                refs.add(row["artifact_ref"])
        return refs

    def _reject_control(self, request: dict, reason: str) -> None:
        self.runtime["processed_controls"].append(request["id"])
        self._record_control_result(request, rejected=True, reason=reason)
        self._save()

    def _review_recovery_control(self, request):
        if request.get("config", {}).get("assessment_reassessment") is not None:
            if self.runtime.get("status") in {"closed", "completed"} or self.instance.get("lifecycle", {}).get("permanently_closed"):
                raise ValueError("closed/completed instance cannot start an assessment reassessment")
            return bool(self._assessment_reassessment_control(request))
        if request["action"] != "request" or not {"review_replacement", "review_restoration"}.intersection(request.get("config", {})):
            return False
        config = request["config"]
        if config.get("role") != "maintenance":
            raise ValueError("review recovery request requires maintenance role")
        if "review_restoration" in config:
            spec = config["review_restoration"]
            action = deepcopy(spec["action"])
            waiting = next((entry for entry in self.runtime.get("waiting_actions", {}).values()
                if entry.get("kind") in {"review_input_restoration", "review_recovery"}
                and all(entry.get("action", {}).get(key) == action.get(key)
                        for key in ("id", "review_cycle_id", "stage", "round", "slot"))), None)
            if waiting is None:
                raise ValueError("review restoration must identify the exact held slot action")
            workspace = Path(self.instance["workspace"]) / "review-restoration" / request["id"]
            outcome = self._retry_review_restoration(waiting["action"], workspace, at=now())
            self.runtime["history"].append({"kind": "review_restoration", "request_id": request["id"], "outcome": outcome})
            return True
        spec = config["review_replacement"]
        action = deepcopy(spec["action"])
        cycle = self._review_cycle(action)
        if action.get("target") != cycle["knowledge_id"]:
            raise ValueError("review recovery target differs from the frozen cycle")
        if spec.get("delegation_id"):
            case = deepcopy(spec["case"])
            effect = case.get("effect", {})
            if (case.get("decision_kind") != "review_replacement" or case.get("target_id") != action["target"]
                    or any(effect.get(key) != action.get(key) for key in ("review_cycle_id", "stage", "round", "slot"))):
                raise ValueError("delegated recovery case differs from the actual review slot")
            application = delegations.prepare_application(self.instance, self.runtime, spec["delegation_id"], case)
            # The original request is the recovery routing authority. The two
            # judgments receive the same case and neither receives the other verdict.
            for stage in ("delegation_interpret", "delegation_check"):
                self._enqueue("intent_interpretation", action["target"], stage=stage,
                    delegation_application_id=application["id"], requested_by=request["id"],
                    reason="Independently compare this case with the exact original decision and approved delegation")
        else:
            outcome = self._authorize_review_replacement(action, grant_id=spec.get("grant_id"), at=now())
            if outcome["disposition"] != "replacement_ready":
                raise ValueError("review replacement is not authorized: " + str(outcome.get("authority")))
        return True

    def _apply_delegation_judgment(self, action, output, execution_id):
        application_id = action["delegation_application_id"]
        stage = {"delegation_interpret": "interpret", "delegation_check": "check"}[action["stage"]]
        record = delegations.record_judgment(self.runtime, application_id, output["delegation_judgment"],
                                            execution_id=execution_id, stage=stage)
        if set(record["judgments"]) != {"interpret", "check"}:
            return
        if any(row["output"]["decision"] != "within_scope" for row in record["judgments"].values()):
            questions.link(self.runtime, execution_id=execution_id, field="delegation_judgment",
                owner="user", targets=[record["basis"]["case"]["target_id"]],
                reason="Independent delegation judgments did not establish authority for this exact case")
            return
        request = next((row["request"] for row in self.runtime.get("history", [])
            if row.get("kind") == "user_control" and row.get("request", {}).get("id") == action["requested_by"]), None)
        if request is None:
            raise ValueError("delegated recovery must resolve its preserved request")
        spec = request["config"]["review_replacement"]
        case = {**deepcopy(record["basis"]["case"]), "application_id": application_id}
        outcome = self._authorize_review_replacement(deepcopy(spec["action"]), grant_id=spec.get("grant_id"),
            delegation_id=record["delegation_id"], case=case, at=now())
        if outcome["disposition"] != "replacement_ready":
            raise ValueError("independently checked case no longer authorizes recovery: " +
                             str(outcome.get("authority", {}).get("reason", outcome["disposition"])))

    def _knowledge_io_control(self, request: dict) -> bool:
        if request["action"] != "knowledge": return False
        spec = request["config"]
        operation = spec.get("operation")
        if operation not in {"import", "register-kind", "check-kind", "activate-kind", "withdraw-kind", "import-relation"}: return False
        if operation == "import":
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime, spec["candidate"],
                source_ref=request["id"], actor_ref=request["id"])
            # An omitted source_refs declares no source dependency; it does not mean every imported source.
            self.instance["knowledge"][kid]["source_basis"] = capture_sources(self.instance, spec["candidate"].get("source_refs", []))
            for execution in self.runtime["executions"].values():
                if execution["status"] != "ended" and execution.get("action", {}).get("target") == kid:
                    execution["stop_requested"] = "imported_knowledge_revision"
        elif operation == "register-kind":
            self._propose_kind(spec["definition"], request["id"])
        elif operation in {"check-kind", "activate-kind"}:
            definition = knowledge_io._lookup_definition(self.instance, spec["family"], spec["token"])
            if not definition:
                raise ValueError("kind definition does not exist")
            check = definition.get("check", {})
            execution = self.runtime["executions"].get(check.get("execution_id"), {})
            if (check.get("decision") != "approved" or execution.get("outcome") != "output_accepted"
                    or (spec.get("check_ref") and spec["check_ref"] != check.get("execution_id"))):
                raise ValueError("kind activation requires a published independent semantic check")
            if definition["status"] != "active":
                raise ValueError("kind check is no longer active; submit a revised definition")
        elif operation == "withdraw-kind":
            self.instance, self.runtime = knowledge_io.withdraw_kind_definition(self.instance, self.runtime,
                spec["family"], spec["token"], reason=spec["reason"], actor_ref=request["id"])
        else:
            self.instance, _ = knowledge_io.import_relation(self.instance, spec["relation"], source_ref=request["id"], actor_ref=request["id"])
        self._invalidate_goal_currentness()
        if self.runtime["status"] in {"waiting", "completed"}: self.runtime["status"] = "ready"
        return True

    def process_controls(self) -> dict:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self._inspect_before_write()
            self._saved_state = self._state_signature()
            self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), "session_limits": None, **self.instance["config"]}
            self._upgrade_runtime()
            self.instance = knowledge_io.ensure_ontology(self.instance)
            self._controls()
            _, persisted_instance, persisted_runtime = self.store.load(self.head)
            if self.instance != persisted_instance or self.runtime != persisted_runtime:
                self._save()
        return self.status()

    def status(self, snapshot=None) -> dict:
        self.head, self.instance, self.runtime = self.store.load(snapshot)
        self._saved_state = self._state_signature()
        self.instance["config"] = {**deepcopy(DEFAULT_CONFIG), "session_limits": None, **self.instance["config"]}
        for slots in (getattr(self, "_slots", None), getattr(self, "_classic_provider_slots", None)):
            if slots is not None and hasattr(slots, "runtime"):
                slots.runtime, slots.instance = self.runtime, self.instance
        executions = list(self.runtime["executions"].values())
        dispatch_waits = reporting.dispatch_waits(self.runtime)
        evaluation_context = self._evaluation_context()
        return {"instance_id": self.instance["id"], "snapshot": self.head, "title": self.instance["title"],
                "research_wake_reasons": planning.research_wake_reasons(self.instance, self.runtime,
                    now=evaluation_context["now"], evaluation_context=evaluation_context),
                "submission_checks": self._submission_check_summary(self.head, self.runtime),
                "goal": self._governance()["goal"], "goal_status": self.instance["goal_status"],
                "status": self.runtime["status"], "active_execution": self.runtime["active_execution"],
                "pending_actions": len(self.runtime["queue"]), "cycles": self.runtime["cycles"],
                "installation_repair": deepcopy(repair_execution.pending_installation_repair(self.runtime)),
                "tasks": reporting.task_status(self.instance, self.runtime),
                "dispatch_waits": dispatch_waits,
                "research_observed_at": now(), "budget_observed_at": now(),
                "knowledge": {"K": sum(row["usable"] for row in knowledge_records.knowledge_view(self.instance)),
                              "formal_results": len(self.instance.get("formal_results", {})),
                              "expositions": len(self.instance.get("expositions", {})),
                              "identity_assessments": len(self.instance.get("identity_assessments", {}))},
                "inspection": inspect_state(self.instance, self.runtime, snapshot=self.head,
                    read_artifact=lambda path: self.store.read(path, self.head),
                    read_artifacts=lambda paths: self.store.read_many(paths, self.head)),
                "research_effectiveness": {"status": "not_evaluated"},
                "budget": self._session_resources() if self._session_mode() else self._provider_slots().usage_snapshot(),
                "budget_unit": "concurrent_sessions" if self._session_mode() else "execution_attempts",
                "active_executions": [e["id"] for e in executions if e["status"] != "ended"],
                "execution_attempts": {pool: sum(e.get("budget_kind") == pool for e in executions) for pool in ("work", "operations")},
                "capacity_waiting": [{k: a[k] for k in ('role', 'target', 'model_selection')}
                                     for a in dispatch_waits if a['wait']['kind'] in {'capacity', 'host_capacity'}],
                "usage": [e.get("usage", {}) for e in executions if e.get("usage")],
                "latest_results": list(self.runtime["activities"].values())[-5:],
                "provider_waits": self._provider_status(),
                "questions": self._user_questions() if self.instance.get("feature_version", 1) >= 4 else deepcopy(self.runtime["questions"]),
                "question_scope": "open_user_questions" if self.instance.get("feature_version", 1) >= 4 else "legacy_unclassified",
                "question_links": self._question_view(),
                "operational_notices": deepcopy(self.runtime["questions"]) if self.instance.get("feature_version", 1) >= 4 else [],
                "pending_controls": len(self._inbox()),
                "user_pause": deepcopy(self.runtime.get("user_pause")),
                "conversation_lost": (self.runtime.get('stop_requested') == 'conversation_lost'
                    and self.instance.get('conversation_loss_policy') == 'pause'),
                "model_policy_violation": deepcopy(self.runtime.get("model_policy_violation")),
                "waiting_actions": {aid: {"role": entry["action"].get("role"),
                    "target": entry["action"].get("target"), "kind": entry.get("kind"),
                    "reason": entry.get("reason"), "execution_id": entry.get("execution_id"),
                    "failure_kind": entry.get("failure_kind"), "retry_at": entry.get("retry_at")}
                    for aid, entry in self.runtime.get("waiting_actions", {}).items()},
                "grants": [{"id": g["id"], "kind": g.get("kind"), "status": g.get("status"), "expires_at": g.get("expires_at")}
                           for g in self.instance.get("grants", {}).values()],
                "pending_events": self.runtime.get("pending_events", []),
                "observations": self.runtime.get("observations", {}),
                "checkpoints": self.runtime.get("checkpoints", {}),
                "external_operations": list(self.runtime.get("external_operations", {}).values()),
                "active_trust_environment": self.instance.get("active_trust_environment"),
                "academic_validation": ({"status": "initialization_incomplete"}
                    if self._governance().get("status") == "unadopted_input" else self._academic_status()),
                "assurance": {"read_scope": "instructions_and_selected_inputs", "provider_operations": "not_observed",
                              "token_usage": "CLI_reported_after_execution", "formal": "Lean_and_axiom_check",
                              "review": "fresh_sessions_without_peer_results_in_inputs"}}

    def run(self, *, max_steps: int | None = None, watch: bool = False) -> dict:
        # Budget-mode conversion is valid only while no executor loop can dispatch.
        self._executor_running = True
        try:
            return self._run_executor(max_steps=max_steps, watch=watch)
        finally:
            self._executor_running = False
            if getattr(self, "_classic_provider_slots", None) is not None:
                self._classic_provider_slots.close()
                self._classic_provider_slots = None

    def _run_executor(self, *, max_steps: int | None = None, watch: bool = False) -> dict:
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive")
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            _require_current_contract(self.instance, self.runtime)
            self._inspect_before_write()
            self._saved_state = self._state_signature()
            self._upgrade_runtime()
            previous = self.runtime.get("installation")
            if previous != self._installation:
                self.runtime.setdefault("implementation_history", []).append({
                    "from": previous, "to": self._installation, "at": now(),
                    "effect": "loaded installed version; no stored record migration"})
                self.runtime["installation"] = deepcopy(self._installation)
            self._controls()
            self._recover_disappeared()
            repair_execution.reroute_initial_failures(self)
            self.runtime["recovery_checked"] = True
            if self.instance["lifecycle"]["state"] == "initializing" and not self.runtime.get("user_pause"):
                self._activate_initialization()
            self._save()
            if not self._clock_guard()["usable"]:
                self.runtime["availability"] = {"state": "blocked", "reason": "clock_regression", "next_owner": "operator"}
                self._save()
                return self.status()
            if self.instance["lifecycle"]["state"] != "initializing":
                self._ensure_academic_followup()
            self._retry_provider_actions()
            self._run_parallel(max_steps=max_steps, watch=watch)
        return self.status()

    def _restore_goal_audit_publication(self, execution):
        """Reconnect a committed producer to its sealed submission, never rerun it."""
        action = execution['action']
        waits = self.runtime.setdefault('waiting_actions', {})
        previous = waits.get(action['id'])
        if previous and previous.get('execution_id') == execution['id'] and previous.get('kind') in {
                'submission_publication', 'submission_failure'}:
            return False
        if previous:
            self.runtime.setdefault('history', []).append({'kind': 'goal_audit_publication_recovered',
                'execution_id': execution['id'], 'previous_wait': deepcopy(previous)})
        waiting = {'action': deepcopy(action), 'execution_id': execution['id'],
                   'kind': 'submission_publication', 'next_owner': 'engine',
                   'reason': 'Finish the original committed goal audit submission'}
        waits[action['id']] = waiting
        try:
            submission.read_sealed_submission(execution, self.head,
                lambda snapshot, path: self.store.read(path, snapshot))
        except submission.SealedSubmissionError as error:
            waiting.update(kind='submission_failure', reason=str(error))
            repair_execution.route_failed_action(self, action, execution['id'],
                reason='Diagnose unreadable sealed goal audit submission')
        return True

    def _recover_disappeared(self) -> None:
        restored = False
        for execution in list(self.runtime['executions'].values()):
            if (execution.get('role') == 'goal_audit' and execution.get('status') == 'ended'
                    and execution.get('outcome') != 'output_accepted'
                    and execution.get('capacity', {}).get('local_termination') == 'confirmed'
                    and not any(r.get('owner_id') == execution['id'] and r.get('state') == 'held'
                                for r in self.runtime.get('reservations', {}).values())
                    and self._committed_goal_audit(execution['id'])):
                restored = self._restore_goal_audit_publication(execution) or restored
        if restored:
            self._save()
        publication_pending = {row["execution_id"] for row in self.runtime.get("waiting_actions", {}).values()
            if row.get("kind") == "submission_publication" and
            self.runtime["executions"].get(row.get("execution_id"), {}).get("capacity", {}).get("local_termination") == "confirmed"}
        unfinished = [row["id"] for row in self.runtime["executions"].values()
                      if row["status"] != "ended" and row["id"] not in publication_pending]
        if not unfinished:
            return
        recovery_id = new_id("RY")
        self.runtime.setdefault("recoveries", {})[recovery_id] = {
            "id": recovery_id, "started_at": now(), "execution_ids": unfinished, "dispositions": []}
        self._save()
        for eid in unfinished:
            execution = self.runtime["executions"][eid]
            state = execution["status"]
            if state == "queued":
                reservations = [row for row in self.runtime.get("reservations", {}).values()
                                if row.get("owner_id") == eid and row.get("status") != "released"]
                if reservations:
                    observation = {"fact": "queued_reservation_requires_reconciliation", "next_owner": "operator"}
                    execution["recovery_disposition"] = "preserve_space_and_reservations"
                else:
                    observation = {"fact": "no_execution_or_reservation"}
                    execution_lifecycle.recover_execution(execution, observation, at=now())
                    execution_lifecycle.end_preparation(execution, at=now(), stage="recovery",
                        reason="executor disappeared during unpublished preparation", cancelled=True)
                    self._continue_prepared_action(execution)
                    self._settle_activity(eid)
                self.runtime["recoveries"][recovery_id]["dispositions"].append({"execution_id": eid, **observation})
                continue
            initial_fact = ("start_unknown" if state == "starting" else
                            "previous_engine_lost" if state == "running" else
                            "engine_restarted" if execution.get("stop_phase") == "checkpointing" else
                            "termination_barrier_pending")
            execution_lifecycle.recover_execution(execution, {"fact": initial_fact}, at=now())
            transport = execution.get("control_transport")
            if transport and getattr(self, "_transport", None):
                self._transport.close(transport, reason="executor restarted")
            identity = execution.get("process", {})
            local_ended = False
            if identity.get("job_name"):
                from .windows_job import named_job_empty
                local_ended = named_job_empty(identity["job_name"]) is True
            elif execution.get("actor_kind") == "machine":
                # The old writer lock is released; subprocess lifetime is still unknown without a Job observation.
                local_ended = execution.get("local_termination_observed") is True
            disposition = {"execution_id": eid, "local_termination_confirmed": local_ended,
                           "remote_termination": "unknown", "next_owner": "operator"}
            if not local_ended:
                self.runtime["recoveries"][recovery_id]["dispositions"].append(disposition)
                continue
            if execution.get('role') == 'goal_audit' and self._committed_goal_audit(eid):
                if self._settle_recovered_execution(eid, at=now(),
                        disposition={'kind': 'committed_submission_pending'}):
                    self._restore_goal_audit_publication(execution)
                    disposition['next_owner'] = 'engine'
                self.runtime['recoveries'][recovery_id]['dispositions'].append(disposition)
                self._save()
                continue
            bundle = new_id("BA")
            workspace = Path(self.instance["workspace"]) / "runs" / eid / "workspace"
            if execution["role"] in {"formal_check", "trust_check"}:
                workspace = Path(self.instance["workspace"]) / ("formal" if execution["role"] == "formal_check" else "trust") / eid
            files = (self._sealed_submission_files(execution)
                     or collect_outputs(workspace, max_bytes=self.instance["config"]["max_artifact_bytes"]))
            control_files = collect_outputs(workspace / ".control",
                                            max_bytes=self.instance["config"]["max_artifact_bytes"])
            checkpoint = json_safe(recovered_checkpoint(workspace))
            reference = f"runtime/artifacts/{bundle}/checkpoint-recovery.json"
            artifacts = {
                reference: lossless_json(checkpoint),
                f"runtime/artifacts/{bundle}/control-manifest.json": canonical_json(control_files["manifest"]),
                f"runtime/artifacts/{bundle}/control-omitted.json": canonical_json(control_files["omitted"]),
            }
            entries = []
            for path, raw in files["files"].items():
                ref = f"runtime/artifacts/{bundle}/files/{path}"
                artifacts[ref] = raw
                entries.append({"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
            for path, raw in control_files["files"].items():
                artifacts[f"runtime/artifacts/{bundle}/control/{path}"] = raw
            execution.update(result_ref=reference, artifact_bundle=bundle, output_files=entries,
                             outputs_complete=files["complete"], error="previous executor disappeared")
            from .observations import bind_checkpoint_artifact
            checkpoint = bind_checkpoint_artifact(checkpoint, entries, self.runtime.get('checkpoints', {}).get(eid))
            artifacts[reference] = lossless_json(checkpoint)
            self.runtime.setdefault("checkpoints", {})[eid] = checkpoint
            if not self._settle_recovered_execution(eid, at=now(), disposition={
                    "local_process": "terminated", "remote_state": "unknown", "artifact_ref": reference}):
                self.runtime["recoveries"][recovery_id]["dispositions"].append({**disposition,
                    "local_termination_confirmed": False, "reason": "reservation settlement not confirmed"})
                continue
            action = execution.get("action", {})
            self._remove_action(action)
            if action.get("id"):
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                    "action": deepcopy(action), "kind": "execution_failure", "execution_id": eid,
                    "reason": "previous executor disappeared", "next_owner": "operational_review"}
                repair_execution.route_failed_action(self, action, eid,
                    reason="Assess this recovered execution's preserved work and remaining authority")
            disposition["next_owner"] = self.runtime.get("waiting_actions", {}).get(action.get("id"), {}).get("next_owner", "operational_review")
            self.runtime["recoveries"][recovery_id]["dispositions"].append(disposition)
            self._settle_activity(eid)
            self._save(artifacts)
        self.runtime["recoveries"][recovery_id]["finished_at"] = now()
        self._save()

    def _context(self, action: dict, workspace: Path, *, execution_id: str | None = None) -> dict:
        evaluation_context = self._evaluation_context()
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
            self._preparation_checkpoint()
            record = knowledge_records.reader_view(self.instance, kid)
            path = directory / "knowledge" / (kid + ".json")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(lossless_json(record))
            use = knowledge.assess_use(knowledge_record, self.instance)
            verified_summaries = []
            seen_items = set()
            for link in use["basis"]:
                exposition = self.instance["expositions"][link["exposition_id"]]
                for item in exposition["items"]:
                    key = (exposition["id"], item["id"])
                    if item["kind"] == "summary" and key not in seen_items:
                        verified_summaries.append({"text": item["text"], "item_id": item["id"],
                            "exposition_id": exposition["id"], "basis": deepcopy(link)})
                        seen_items.add(key)
            catalog.append({"id": kid, "kind": knowledge_record["kind"], "title": knowledge_record["title"],
                            "summary": record.get("summary", ""), "lifecycle": knowledge_record["lifecycle"],
                            "verified_summaries": verified_summaries,
                            "formal_valid": knowledge_records.formal_usable(self.instance, record["formal_result"]),
                            "formal_result_id": knowledge_record.get("formal_result_id"),
                            "exposition_id": knowledge_record["exposition_id"],
                            "content_sha256": knowledge.content_hash(knowledge_record),
                            "usable_as_k": use["valid"], "use_reasons": use["reasons"],
                             "path": path.relative_to(workspace).as_posix()})
            catalog[-1]["identity_assessment_ids"] = [row["id"] for row in record["identity_assessments"]]
            cycle_id = knowledge_record.get("review_cycle_id")
            cycle = self.runtime.get("review_cycles", {}).get(cycle_id)
            if cycle and cycle["status"] in {"completed", "unresolved"} and not (
                    action["role"] == "identity_review" and action.get("review_cycle_id") == cycle_id):
                cycle_path = directory / "review-cycles" / (cycle_id + ".json")
                cycle_path.parent.mkdir(exist_ok=True)
                cycle_path.write_bytes(lossless_json(cycle))
                catalog[-1]["review_cycle_source"] = {"path": cycle_path.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(cycle_path.read_bytes()).hexdigest()}
        sources = []
        self._preparation_checkpoint()
        source_bytes = self.store.read_many([s["path"] for s in self.instance["sources"]], self.head)
        for i, source in enumerate(self.instance["sources"]):
            self._preparation_checkpoint()
            raw = source_bytes[source["path"]]
            if hashlib.sha256(raw).hexdigest() != source["sha256"]:
                raise ValueError("source artifact hash changed")
            path = directory / "sources" / f"{i:04d}-{source['name']}"
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(raw)
            sources.append({**source, "local_path": path.relative_to(workspace).as_posix()})
        target = action.get("target")
        task = self.runtime["tasks"].get(target)
        target_execution_action = self.runtime["executions"].get(target, {}).get("action", {}) if action["role"] == "operational_review" else {}
        private_review_context = bool(action.get("review_cycle_id") or target_execution_action.get("review_cycle_id"))
        task_views = [{**deepcopy(row), "content_sha256": knowledge.content_hash(row)} for row in self.runtime["tasks"].values()]
        if not private_review_context:
            result_bytes = self.store.read_many([
                file["artifact_ref"] for view in task_views for result in view.get("results", [])
                for file in result.get("output_files", self.runtime["executions"].get(
                    result.get("execution_id"), {}).get("output_files", []))], self.head)
            for view in task_views:
                for result in view.get("results", []):
                    producing = self.runtime["executions"].get(result.get("execution_id"), {})
                    restored = []
                    for file in result.get("output_files", producing.get("output_files", [])):
                        self._preparation_checkpoint()
                        raw = result_bytes[file["artifact_ref"]]
                        if hashlib.sha256(raw).hexdigest() != file["sha256"]:
                            raise ValueError("task result artifact hash changed")
                        path = directory / "task-results" / view["id"] / result["execution_id"] / file["path"]
                        if not path.resolve().is_relative_to(directory.resolve()):
                            raise ValueError("task result artifact path escapes input")
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(raw)
                        restored.append({**file, "local_path": path.relative_to(workspace).as_posix()})
                    result["output_files"] = restored
        governance_input = self._governance()
        context = {"snapshot": self.head, "execution_id": execution_id, "workspace": str(workspace.resolve()), "goal": governance_input["goal"], "goal_kind": governance_input["goal_kind"],
                   "policies": governance_input["policies"], "governance": governance_input, "action": action, "task": task,
                   "tasks": task_views, "knowledge_catalog": catalog, "implementation_documents": implementation_documents,
                   "relations": self.instance["relations"], "sources": sources,
                   "user_inputs": self.runtime["inputs"], "open_questions": self._user_questions(),
                   "instance_id": self.instance["id"], "question_links": self._question_view(),
                   "recent_history": self.runtime["history"][-8:],
                   "instructions": "Read input/ and your workspace only. Pass the exact absolute workspace as workdir on every shell call, with login=false. Use absolute paths under this workspace for file reads and writes; a shell's default working directory may differ. Ask for missing inputs. Never read other runs or the central repository. New research source code belongs in this workspace."}
        context.update(goal_revision=self._governance().get("goal_revision", 1), policy_revision=self._governance().get("policy_revision", 1),
                       grants=[{k: v for k, v in grant.items() if k != "credential_env"} for grant in self.instance.get("grants", {}).values()],
                        task_readiness={tid: planning.task_ready(task, self.instance, self.runtime, evaluation_context=evaluation_context)
                                       for tid, task in self.runtime["tasks"].items()},
                       checkpoint_schema=CHECKPOINT_SCHEMA, checkpoint_path="checkpoint.json",
                       external_operations=list(self.runtime.get("external_operations", {}).values()),
                       events=[e for e in self.runtime.get("events", []) if e["id"] in action.get("event_refs", [])],
                       available_input_refs=self.instance.get("available_input_refs", []))
        context["resources"] = self._session_resources() if self._session_mode() else self._provider_slots().usage_snapshot()
        context["budget_unit"] = "concurrent_sessions" if self._session_mode() else "execution_attempts"
        if self._session_mode():
            context["model_policy"] = {"tier_models": self.instance["config"]["tier_models"],
                "role_tiers": self.instance["config"]["role_tiers"], "assessment_schema": model_policy.ASSESSMENT_SCHEMA,
                "selected": action.get("model_selection"), "missing_assessment": "Existing tasks require assessment-only preparation before contract review; preparation uses its configured role floor."}
        if action["role"] == "research_plan" and self._session_mode():
            live_ids = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
            context["queued_work"] = [deepcopy(a) for a in self.runtime["queue"] if a["role"] in WORK_ROLES and a.get("id") not in live_ids]
        if action['role'] == 'research_plan':
            context['review_followups'] = [deepcopy(cycle) for cid, cycle in self.runtime.get('review_cycles', {}).items()
                if cid in action.get('evidence_refs', [])]
        context["execution_limits"] = {key: self.instance["config"][key] for key in
            ("call_timeout_seconds", "checkpoint_grace_seconds", "review_rounds")}
        scholarly_enabled = self.instance["config"]["scholarly_enabled"]
        context["scholarly"] = {"enabled": scholarly_enabled,
            "configured": bool(scholarly_enabled and self.instance["config"]["scholarly_server"]),
            "artifact_directory": "scholarly-data",
            "availability": "Confirm the tools actually exposed in this execution; configuration is not a successful call."}
        active_environment = self.instance.get("trust_environments", {}).get(self.instance.get("active_trust_environment"), {})
        preview_invocation = {}
        if active_environment.get("status") == "active":
            try:
                preview_profile = self._execution_profile({"role": "formal_check"})
                preview_invocation = execution_profiles.machine_invocation(preview_profile, trust_environment=active_environment)
            except ValueError:
                pass  # Preview is unavailable; authoritative dispatch reports the exact gate failure.
        context["formal_verifier"] = {"reference": "tool:lean", "mechanism": "central_after_submission",
            "environment_id": active_environment.get("id"), "environment_status": active_environment.get("status"),
            "command": preview_invocation.get("lean_command"),
            "observed_toolchain": active_environment.get("toolchain"),
            "expected_toolchain": preview_invocation.get("expected_toolchain"),
            "allowed_axioms": active_environment.get("allowed_axioms", []),
            "timeout_seconds": preview_invocation.get("timeout_seconds"),
            "instruction": "Submit self-contained lean_code and declaration_names. Use preview for non-authoritative compiler feedback when a command is supplied. It uses this verifier edition and configured command, but does not isolate shared libraries or Lake caches. The executor always verifies the submitted exact source again. A configured command is not a completed verification; report only the toolchain actually observed."}
        context["academic_requirements"] = ({} if governance_input.get("status") == "unadopted_input"
                                             else academic.current_requirements(self.instance))
        context["academic_phase"] = "postsolution" if self.instance["goal_status"] == "mathematically_solved" else "deferred_until_goal_solved"
        context["kind_definitions"] = knowledge_io.catalog_definitions(self.instance)
        if action.get("kind_definition_id"):
            definition = self.instance["kind_definitions"][action["kind_definition_id"]]
            if integration.digest(definition) != action["kind_definition_sha256"]:
                raise ValueError("kind definition changed before independent review")
            context["kind_definition_to_check"] = deepcopy(definition)
            context["proposal"] = deepcopy(definition)
            context["maintenance_objective"] = (
                "Independently compare the complete proposed meaning and constraints with the adopted governance and existing kinds. "
                "Approve only when the meaning is coherent, distinguishable and does not create research, trust, budget or external authority. "
                "Return revision_required with concrete defects or unresolved with missing evidence; structural schema validity alone is insufficient.")
        if action.get("stage") == "impact_review":
            request = action["input_basis"]["impact_review"]
            producer = self.runtime["executions"][request["producer_execution_id"]]
            sealed = submission.read_sealed_submission(producer, self.head,
                lambda snapshot, path: self.store.read(path, snapshot))
            context["impact_review_input"] = {"request": deepcopy(request),
                "output": sealed["output"], "extensions": sealed["extensions"],
                "records": {rid: deepcopy(record) for rid, (_, record) in planning._records(self.instance, self.runtime).items()
                    if any(rid in plan.get("basis", {}) or rid in plan.get("computed_impact", [])
                        or rid in plan.get("declared_impact", []) or rid in plan.get("roots", [])
                        for plan in request["plans"].values())}}
        context["decisions"] = deepcopy(list(self.instance.get("decisions", {}).values()))
        if action["role"] in {"research_preparation", "research_plan", "operational_review", "maintenance"}:
            context["goal_judgments"] = deepcopy(self.instance.get("goal_judgments", []))
        context["execution_profiles"] = deepcopy(list(self.instance.get("execution_profiles", {}).values()))
        context["role_profile_refs"] = deepcopy(self.instance.get("role_profile_refs", {}))
        context["observed_at"] = evaluation_context["now"]
        context["repetition_lineages"] = task_contracts.repetition_lineages(self.instance, self.runtime, target)
        context['repetition_holds'] = list(revisions.active_repetition_holds(self.runtime).values())
        if action.get("profile_ref"):
            profile = execution_profiles.resolve_profile(self.instance["execution_profiles"], action["profile_ref"])
            context["execution_profile"] = profile
            context["execution_limits"] = execution_profiles.runtime_config(profile)
            tools = execution_profiles.runner_tools(profile)
            context["scholarly"].update(enabled=tools["scholarly_server"] is not None,
                                       configured=tools["scholarly_server"] is not None)
        context["academic_validation"] = ({"status": "initialization_incomplete"}
            if governance_input.get("status") == "unadopted_input" else self._academic_status())
        context["external_rejections"] = self.runtime.get("external_rejections", [])
        if action["role"] in {"identity_review", "goal_audit"}:
            context.pop("recent_history")
        if action["role"] == "identity_review":
            context.pop("tasks")
        if action["role"] == "identity_review":
            if action.get("review_cycle_id"):
                prepared = self._prepare_review_context(action, workspace, sources=sources)
                if prepared["disposition"] != "ready":
                    raise ReviewPreparationDeferred(prepared)
                context["role_review"] = prepared["context"]
            else:
                context["proposal"] = knowledge_records.proposal_view(self.instance, target)
        if action["role"] == "goal_audit":
            context["eligible_knowledge"] = []
            for kid, record in self.instance["knowledge"].items():
                links = knowledge_records.usable_links(self.instance, kid)
                if not links:
                    continue
                proposal = knowledge_records.proposal_view(self.instance, kid)
                context["eligible_knowledge"].append({"id": kid,
                    "proposal": proposal, "links": links,
                    "formal_result": deepcopy(self.instance["formal_results"][record["formal_result_id"]]),
                    "exposition": deepcopy(self.instance["expositions"][record["exposition_id"]]),
                    "identity_assessments": [deepcopy(self.instance["identity_assessments"][link["assessment_id"]])
                                             for link in links]})
            context["tasks"] = [{k: v for k, v in t.items() if k not in {"reviews", "assessment"}} for t in task_views]
        if action["role"] == "operational_review":
            reviewed_execution = deepcopy(self.runtime["executions"].get(target))
            context["execution_to_review"] = reviewed_execution
            task_id = (reviewed_execution or {}).get("action", {}).get("target")
            if task_id in self.runtime["tasks"]:
                context["proposal"] = {"task": deepcopy(self.runtime["tasks"][task_id]),
                    "instruction": "A task_disposition must include one matching task_assessments entry with a disposition for every obligation. Fulfilment requires the designated independent judge; waivers and transfers require current source-bound user authority."}
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
                activity_result_ref = reviewed_execution.get("result_ref")
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
                if selected_result_ref == checkpoint_ref:
                    checkpoint_source = result_source
                elif (reviewed_execution.get("role") == "formal_check" or
                      reviewed_execution.get("parent_execution_id")) and checkpoint_ref not in self.store.list_files(
                          f"runtime/artifacts/{bundle}/", source_snapshot):
                    # These producers do not create a recovery checkpoint on normal completion.
                    checkpoint_source = None
                else:
                    checkpoint_source = recover(checkpoint_ref, "checkpoint-recovery.json")
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
        context["execution_window"] = {"path": ".control/execution-window.json", "finish_request_path": ".control/finish-request.json",
            "stop_request_path": ".control/stop-request.json", "feedback_path": ".control/observation-feedback.json",
            "instruction": "Read management notices under .control after start. A finish request asks for normal submission and does not revoke authority."}
        if action.get("delegation_application_id"):
            context["delegation_case"] = delegations.judgment_input(self.runtime, action["delegation_application_id"])
            request = next(row["request"] for row in self.runtime["history"]
                if row.get("kind") == "user_control" and row.get("request", {}).get("id") == action["requested_by"])
            context["user_request"] = {"request": deepcopy(request), "delegation_case": deepcopy(context["delegation_case"])}
            for key in ("recent_history", "user_inputs", "open_questions", "question_links"):
                context.pop(key, None)
            context["interpretation_stage"] = action["stage"]
            context["interpretation_to_check"] = None
        from .context_store import restore_continuation
        context.update(restore_continuation(self.runtime, action, workspace, snapshot=self.head,
            read_artifact=lambda path: self.store.read(path, self.head), checkpoint=self._preparation_checkpoint))
        self._submission_repair_context(context, action)
        if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
            context.update(self._review_research_context(action, workspace))
        reviewed_action = self.runtime["executions"].get(target, {}).get("action", {}) if action["role"] == "operational_review" else action
        if reviewed_action.get("review_cycle_id"):
            for key in ("open_questions", "question_links", "recent_history", "tasks"):
                context.pop(key, None)
        if action["role"] == "operational_review":
            context["blocked_actions"] = [{"action_id": aid, "role": entry["action"].get("role"),
                "target": entry["action"].get("target"), "kind": entry.get("kind"), "reason": entry.get("reason"),
                "execution_id": entry.get("execution_id")} for aid, entry in self.runtime.get("waiting_actions", {}).items()
                if entry.get("execution_id") == action.get("target")]
        if action["role"] == "maintenance":
            # Queue repairs are checked against the engine's own revision state.
            context["pending_revisions"] = deepcopy(planning.pending_revisions(self.runtime))
            context["revision_cycles"] = deepcopy(self.runtime.get("revision_cycles", []))
            context["blocked_actions"] = [{"action_id": aid, "role": entry["action"].get("role"),
                "target": entry["action"].get("target"), "kind": entry.get("kind"),
                "reason": entry.get("reason"), "execution_id": entry.get("execution_id")}
                for aid, entry in self.runtime.get("waiting_actions", {}).items()]
            if action.get('initial_submission_diagnosis'):
                failed, waiting = repair_execution.initial_diagnosis_input(self, action)
                context['initial_submission_diagnosis'] = deepcopy(waiting)
                context['initial_submission_diagnosis']['failed_execution'] = deepcopy(failed)
                context['initial_submission_diagnosis']['checkpoint'] = deepcopy(self.runtime.get('checkpoints', {}).get(failed['id']))
                context['initial_submission_diagnosis']['preserved_output_files'] = deepcopy(failed.get('output_files', []))
                refs = [ref for ref in (failed.get('result_ref'), waiting['action'].get('repair', {}).get('raw_output_ref'),
                        waiting['action'].get('repair', {}).get('check_ref'), failed.get('submitted_output_ref'),
                        failed.get('submission_check_ref')) if ref]
                refs.extend(row['artifact_ref'] for row in failed.get('output_files', []))
                if failed.get('input_bundle'):
                    prefix = 'runtime/artifacts/' + failed['input_bundle']
                    refs.extend([prefix + '/input.txt', prefix + '/schema.json', prefix + '/input/submission/context.json'])
                context['initial_submission_diagnosis']['materials'] = []
                for index, ref in enumerate(dict.fromkeys(refs)):
                    raw = self.store.read(ref, self.head)
                    local = 'initial-diagnosis/' + str(index) + '.txt'
                    materialize_inputs(workspace, {local: raw})
                    context['initial_submission_diagnosis']['materials'].append({
                        'artifact_ref': ref, 'local_path': 'input/' + local, 'sha256': hashlib.sha256(raw).hexdigest()})
        if action["role"] in {"research_preparation", "research_plan"}:
            context["resources"] = self._session_resources() if self._session_mode() else self._provider_slots().usage_snapshot()
            context["config"] = deepcopy(self.instance["config"])
            context["ready_task_ids"] = planning.ready_task_ids(self.runtime, self.instance, evaluation_context=evaluation_context)
            context["pending_revisions"] = deepcopy(planning.pending_revisions(self.runtime))
            context["revision_cycles"] = deepcopy(self.runtime.get("revision_cycles", []))
            context["blocked_actions"] = [{"action_id": aid, "role": entry["action"].get("role"),
                "target": entry["action"].get("target"), "kind": entry.get("kind"),
                "reason": entry.get("reason"), "execution_id": entry.get("execution_id")}
                for aid, entry in self.runtime.get("waiting_actions", {}).items()]
            context["recent_history"] = self._planning_history("research_plan", workspace)
            context["ongoing_preparation"] = [
                {"execution_id": e["id"], "status": e["status"],
                 "input_snapshot": e.get("input_snapshot"),
                 "revision_targets": deepcopy(e.get("action", {}).get("revision_targets", {})),
                 "goal_revision": e.get("goal_revision"), "policy_revision": e.get("policy_revision"),
                 "reason": e.get("action", {}).get("reason", ""),
                 "target": e.get("action", {}).get("target"),
                 "assessment_targets": deepcopy(e.get("action", {}).get("assessment_targets", {})),
                 "observation_rule_targets": deepcopy(e.get("action", {}).get("observation_rule_targets", {}))}
                for e in self.runtime["executions"].values()
                if e["role"] == "research_preparation" and e["status"] != "ended"]
            if action["role"] == "research_preparation":
                context["preparation_history"] = self._planning_history("research_preparation", workspace)
        return self._governance_context(action, context)

    def _planning_history(self, role: str, workspace: Path) -> list[dict]:
        """Keep rejected and incomplete submissions readable after later events."""
        history = []
        references = {e["id"]: e.get("result_ref")
                      or f"runtime/artifacts/{e['artifact_bundle']}/result.json"
                      for e in self.runtime["executions"].values()
                      if e.get("role") == role and e.get("status") == "ended" and e.get("artifact_bundle")}
        self._preparation_checkpoint()
        preserved = self.store.read_many(list(references.values()), self.head)
        for execution in self.runtime["executions"].values():
            if execution.get("role") != role or execution.get("status") != "ended":
                continue
            self._preparation_checkpoint()
            row = {"execution_id": execution["id"], "role": role, "outcome": execution.get("outcome"),
                   "error": execution.get("error"), "action": deepcopy(execution.get("action", {}))}
            if "repair" in row["action"]:
                # Rejected claims remain exact evidence, never an inline current-state assertion.
                raw_action = lossless_json(row["action"])
                relative_action = f"planning-history/{execution['id']}-action.json"
                materialize_inputs(workspace, {relative_action: raw_action})
                row["action_source"] = {"snapshot": self.head, "execution_id": execution["id"],
                    "local_path": "input/" + relative_action,
                    "sha256": hashlib.sha256(raw_action).hexdigest(), "bytes": len(raw_action)}
                row["action"]["repair"] = {key: value for key, value in row["action"]["repair"].items()
                                           if key != "previous_output"}
            if execution.get("artifact_bundle"):
                reference = references[execution['id']]
                raw = preserved[reference]
                relative = f"planning-history/{execution['id']}.json"
                materialize_inputs(workspace, {relative: raw})
                row.update(artifact_ref=reference, local_path="input/" + relative,
                           sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            history.append(row)
        return history

    def _response_schema(self, action: dict) -> dict:
        if action["role"] == "supplemental_research" and action.get("review_cycle_id"):
            schema = self._review_research_schema(action)
        elif action["role"] == "identity_review" and action.get("review_cycle_id"):
            schema = self._review_schema(action)
        elif action.get("delegation_application_id"):
            schema = action_schema({"role": "maintenance"}, knowledge_io.catalog_definitions(self.instance))
            schema["properties"].pop("report"); schema["properties"].pop("remaining_work")
            schema["required"] = [key for key in schema["required"] if key not in {"report", "remaining_work"}]
            schema["properties"]["delegation_judgment"] = {"type": "object", "additionalProperties": False,
                "properties": {"input_sha256": {"const": self.runtime["delegation_applications"][action["delegation_application_id"]]["input_sha256"]},
                    "decision": {"enum": ["within_scope", "outside_scope", "unresolved"]},
                    "reason": {"type": "string", "minLength": 1}}, "required": ["input_sha256", "decision", "reason"]}
            schema["required"].append("delegation_judgment")
        elif action["role"] == "intent_interpretation":
            schema = governance.interpretation_schema(action.get("stage", "interpret"))
        else:
            schema = action_schema(action, knowledge_io.catalog_definitions(self.instance))
        if action["role"] == "operational_review":
            schema = deepcopy(schema)
            schema["properties"]["task_assessments"] = deepcopy(action_schema(
                {"role": "research_plan"}, knowledge_io.catalog_definitions(self.instance))["properties"]["task_assessments"])
            schema.setdefault("allOf", []).append({"if": {"properties": {"disposition": {"properties": {"kind": {"const": "task_disposition"}}}}},
                "then": {"required": ["task_assessments"], "properties": {"task_assessments": {"minItems": 1, "maxItems": 1}}}})
        if action["role"] == "maintenance" and action.get("kind_definition_id"):
            schema = deepcopy(schema)
            schema["properties"]["kind_definition_check"] = {"type": "object", "additionalProperties": False,
                "properties": {"definition_id": {"const": action["kind_definition_id"]},
                    "definition_sha256": {"const": action["kind_definition_sha256"]},
                    "decision": {"enum": ["approved", "revision_required", "unresolved"]},
                    "findings": {"type": "array", "items": {"type": "string", "minLength": 1}}},
                "required": ["definition_id", "definition_sha256", "decision", "findings"]}
            schema["required"].append("kind_definition_check")
        if action['role'] == 'maintenance' and action.get('initial_submission_diagnosis'):
            schema = deepcopy(schema)
            schema['properties']['initial_submission_diagnosis'] = {'type':'object', 'additionalProperties':False,
                'properties': {'decision': {'enum':['retry','wait']}, 'guidance': {'type':'string','minLength':1}},
                'required':['decision','guidance']}
            schema['required'].append('initial_submission_diagnosis')
        return with_integration_schema(self._governance_schema(action, schema))

    def _impact_review_execution(self, runtime, action, integration_id):
        return runtime.get("waiting_actions", {}).get(action.get("id"), {}).get("review_execution_ids", {}).get(integration_id)

    def _validate_bundle_impacts(self, instance, runtime, bundle, *, action, execution_id):
        return integration.require_bundle_impact_review(instance, runtime, bundle,
            producer_execution_id=execution_id, input_snapshot=runtime["executions"][execution_id]["input_snapshot"],
            review_execution_id=self._impact_review_execution(runtime, action, bundle["integration_id"]),
            snapshot=self.head, read_artifact=lambda snapshot, path: self.store.read(path, snapshot))

    def _validate_bundle_current(self, instance, runtime, bundle, *, action, execution_id, context):
        execution = runtime["executions"][execution_id]
        original_instance, original_runtime = self.instance, self.runtime
        try:
            self.instance, self.runtime = instance, runtime
            self._validate_bundle_impacts(instance, runtime, bundle, action=action, execution_id=execution_id)
            self._validate_decision_acceptance(action, bundle["output"], execution, context, evaluation_context=self._evaluation_context())
            reported = submission.reported_references(bundle["output"], bundle["extensions"], context)
            _, input_instance, _ = self.store.load(execution["input_snapshot"])
            execution["source_basis"] = capture_sources(input_instance,
                [row["name"] for row in execution.get("source_basis", [])] + reported)
            if not sources_current(execution["source_basis"], instance):
                raise CurrentnessChanged([{"field": "sources", "reason": "required source content changed"}])
            if execution.get("academic_requirements_sha256") and execution["academic_requirements_sha256"] != academic.current_requirements(instance).get("sha256"):
                raise ValueError("academic requirements changed during execution")
            authority = governance.authorize(instance, action, runtime=runtime)
            if not authority["allowed"]:
                raise ValueError("execution authority was revoked before result acceptance")
            for reference in bundle["authority_refs"]:
                grant = instance.get("grants", {}).get(reference)
                if grant is not None:
                    scoped = governance.authorize(instance, {**action, "grant_id": reference}, runtime=runtime)
                    if not scoped["allowed"]:
                        raise ValueError("bundle authority is no longer current: " + reference)
                elif reference not in instance.get("decisions", {}):
                    raise ValueError("bundle authority disappeared: " + reference)
        finally:
            self.instance, self.runtime = original_instance, original_runtime

    def _validate_bundle_candidate(self, instance, runtime, bundle, *, artifacts=None):
        # Storage performs its registered family/relation checks before the CAS.
        # These checks also reject malformed domain projections before publication.
        knowledge_records.validate_knowledge_records(instance)
        _records(instance, runtime)
        if artifacts:
            from .question_engine import _pointer
            for row in runtime.get("question_links", []):
                if row.get("source_ref") in artifacts:
                    _pointer(submission.load_json(artifacts[row["source_ref"]]), row["origin_field"])
        self.store.validate_candidate(instance, runtime, self.head, artifacts=artifacts)

    def _apply_bundle_candidate(self, instance, runtime, bundle, *, action, execution_id, extensions,
                                question_source_ref=None):
        previous_instance, previous_runtime = self.instance, self.runtime
        try:
            self.instance, self.runtime = instance, runtime
            if bundle["extensions"].get("knowledge_changes"):
                if action["role"] not in {"research_preparation", "research_work", "supplemental_research"}:
                    raise ValueError("this role may report a defect but cannot author a knowledge revision")
                self.instance, self.runtime = integration.apply_reviewed_knowledge_changes(
                    self.instance, self.runtime, bundle, actor_ref=execution_id, producer_execution_id=execution_id,
                    input_snapshot=self.runtime["executions"][execution_id]["input_snapshot"],
                    review_execution_id=self._impact_review_execution(self.runtime, action, bundle["integration_id"]),
                    snapshot=self.head, read_artifact=lambda snapshot, path: self.store.read(path, snapshot))
                self._invalidate_goal_currentness()
            elif integration.mutation_members(bundle["output"], bundle["extensions"]):
                request = integration.bundle_impact_request(self.instance, self.runtime, bundle,
                    producer_execution_id=execution_id, input_snapshot=self.runtime["executions"][execution_id]["input_snapshot"])
                if request["plans"]:
                    confirmations = self._validate_bundle_impacts(self.instance, self.runtime, bundle,
                        action=action, execution_id=execution_id)
                    self.instance, self.runtime = knowledge.apply_impact(self.instance, self.runtime,
                        request["plans"]["bundle"], reason="Apply the validated impact of integration " + bundle["integration_id"],
                        independent_confirmation=confirmations.get("bundle"))
            execution = self.runtime["executions"][execution_id]
            execution["extensions"] = deepcopy(bundle["extensions"])
            execution["integration_id"] = bundle["integration_id"]
            if bundle["owns_response"]:
                self._apply_model_metadata(action, bundle["output"], execution_id)
            deferred = (bundle["owns_response"] and
                self._defer_review_for_research(action, bundle["output"], execution_id))
            if not deferred:
                self._apply(action, bundle["output"], execution_id, owns_response=bundle["owns_response"],
                            question_source_ref=question_source_ref)
            self._apply_extensions(action, execution_id)
            if bundle["owns_response"]:
                self._apply_revision_followup(action, bundle["output"], execution_id)
                self._apply_action_resolutions(execution_id, accepting_current=True)
                self._apply_question_resolutions(execution_id)
                self._consume_action_events(action, execution_id)
            # Domain owners may return replacement projections.
            if self.instance is not instance:
                instance.clear()
                instance.update(self.instance)
            if self.runtime is not runtime:
                runtime.clear()
                runtime.update(self.runtime)
            runtime["executions"][execution_id]["extensions"] = deepcopy(extensions)
            runtime["executions"][execution_id].pop("integration_id", None)
        finally:
            self.instance, self.runtime = previous_instance, previous_runtime


    def _apply_submission_bundles(self, action, output, extensions, execution_id, context, issues):
        """Publish independent candidates without an enclosing execution rollback."""
        def publish(instance, runtime, bundle):
            # Normalize public events before the CAS. No fallible post-commit read
            # may make an already published bundle look like a rejected candidate.
            self.head, normalized_instance, normalized_runtime = self.store.save_with_state(
                self.head, instance, runtime)
            instance.clear()
            instance.update(normalized_instance)
            runtime.clear()
            runtime.update(normalized_runtime)

        result = integration.apply_bundles(self.instance, self.runtime, output, extensions, context,
            execution_id=execution_id, apply_bundle=lambda instance, runtime, bundle: self._apply_bundle_candidate(
                instance, runtime, bundle, action=action, execution_id=execution_id, extensions=extensions),
            validate_current=lambda instance, runtime, bundle: self._validate_bundle_current(
                instance, runtime, bundle, action=action, execution_id=execution_id, context=context),
            validate_candidate=self._validate_bundle_candidate, publish=publish, submission_issues=issues)
        if any(row.get("next_owner") == "engine" for row in result["bundles"]):
            self.head, self.instance, self.runtime = self.store.load()
            result["instance"], result["runtime"] = self.instance, self.runtime
        else:
            self.instance, self.runtime = result["instance"], result["runtime"]
        self._saved_state = self._state_signature()
        self.runtime["executions"][execution_id]["integration_result"] = {
            key: deepcopy(result[key]) for key in ("status", "bundles", "issues", "retry_bundle_ids")}
        return result

    def _submission_repair_context(self, context, action):
        repair = action.get("repair", {})
        context["submission_failures"] = deepcopy(repair.get("issues", []))
        ancestors, execution_id = set(), action.get("continuation_of") or repair.get("execution_id")
        while execution_id and execution_id not in ancestors:
            ancestors.add(execution_id)
            previous_action = self.runtime["executions"].get(execution_id, {}).get("action", {})
            execution_id = previous_action.get("continuation_of") or previous_action.get("repair", {}).get("execution_id")
        accepted = [receipt for receipt in self.runtime.get("integrations", {}).values()
                    if receipt["execution_id"] in ancestors and "response_sha256" in receipt]
        if accepted:
            if len({row["response_sha256"] for row in accepted}) != 1:
                raise ValueError("one response lineage has conflicting accepted response hashes")
            context["accepted_response"] = {"integration_id": accepted[0]["id"],
                                            "response_sha256": accepted[0]["response_sha256"]}
        context["accepted_integration_ids"] = sorted(receipt["id"] for receipt in
            self.runtime.get("integrations", {}).values() if receipt["execution_id"] in ancestors)

    def _preview_submission(self, execution, payload):
        """Use the issued input and sole receiver callbacks; return no state projection."""
        base = f"runtime/artifacts/{execution['input_bundle']}"
        context = submission.load_json(self.store.read(base + "/input/submission/context.json", self.head))
        schema = submission.load_json(self.store.read(base + "/schema.json", self.head))
        workspace = Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace"
        draft_path = payload.get("draft_path") or payload.get("raw_output_path")
        sealed = submission.seal_submission(workspace, draft_path, execution_id=execution["id"],
            context=context, schema=schema, max_artifact_bytes=self.instance["config"]["max_artifact_bytes"])
        if not sealed["capture_eligible"]:
            return {"contract_id": "do-math-candidate-preview/5", "passed": False,
                    "issues": sealed["check"]["issues"], "bundles": [], "authoritative": False,
                    "not_checked": ["candidate_application", "mathematical_meaning", "Lean"]}
        output = submission.load_json(sealed["artifacts"]["output.json"])
        extensions = submission.load_json(sealed["artifacts"]["extensions.json"])
        action = execution["action"]
        preview_prefix = f"runtime/artifacts/preview/{execution['id']}"
        preview_artifacts = {preview_prefix + "/" + path: raw for path, raw in sealed["artifacts"].items()}
        preview_output_ref = preview_prefix + "/output.json"
        return submission.preview_submission(output, schema, context, extensions, workspace,
            execution_id=execution["id"], tool_sha256=context["submission_contract"]["tool_sha256"],
            instance=self.instance, runtime=self.runtime, check=sealed["check"],
            apply_bundle=lambda instance, runtime, bundle: self._apply_bundle_candidate(
                instance, runtime, bundle, action=action, execution_id=execution["id"], extensions=extensions,
                question_source_ref=preview_output_ref),
            validate_current=lambda instance, runtime, bundle: self._validate_bundle_current(
                instance, runtime, bundle, action=action, execution_id=execution["id"], context=context),
            validate_candidate=lambda instance, runtime, bundle: self._validate_bundle_candidate(
                instance, runtime, bundle, artifacts=preview_artifacts))

    def _receive_submission(self, action, result, execution_id, context, schema, workspace, *, preserved=False):
        """Preserve the check and raw candidate even when every bundle is rejected."""
        previous_wait = deepcopy(self.runtime.get('waiting_actions', {}).get(action.get('id')))
        rejected = result.get('rejected_submission')
        if rejected:
            check = submission.load_json(self.store.read(rejected['check_ref'], self.head))
            received = {'status': 'returned', 'bundles': [], 'retry_bundle_ids': [], 'issues': check['issues']}
            execution = self.runtime['executions'][execution_id]
            execution.update(error_kind=integration.failure_kind(check['issues']),
                             error='native final failed central structural validation')
            execution_lifecycle.transition_execution(execution, 'ended', at=now(), outcome='execution_incomplete',
                disposition={'kind': 'submission_returned', 'check_ref': rejected['check_ref']})
            self._remove_action(action)
            repair_execution.route_submission_return(self, action, received, execution_id, result.get('output'),
                rejected_submission=rejected)
            self._record_task_receipt(action, {}, execution_id, accepted=False)
            return received
        output = result.get("output")
        execution = self.runtime["executions"][execution_id]
        if execution.get("submission_intent", {}).get("output_ref"):
            preserved = True
        if preserved:
            sealed = submission.read_sealed_submission(execution, self.head,
                lambda snapshot, path: self.store.read(path, snapshot))
            output, extensions, check = sealed["output"], sealed["extensions"], sealed["check"]
        else:
            try:
                extensions = self._read_extensions(workspace)
            except (ValueError, TypeError, OSError) as error:
                extensions = {}
                extension_issues = [integration.issue(
                    "submission.extensions", "activity-extensions.json", str(error))]
            else:
                extension_issues = []
            check = submission.check_submission(output, schema, context, extensions, workspace,
                mode="receiver", execution_id=execution_id,
                tool_sha256=context.get("submission_contract", {}).get("tool_sha256", ENGINE_SHA256))
            check["issues"].extend(extension_issues)
            check["issues"].append(integration.issue(
                "submission.sealed_candidate", "submission_receipt",
                "worker output was not captured by the central submit path"))
            check["passed"] = not check["issues"]
            check['capture_eligible'] = False
            check["id"] = "MC-" + integration.digest({key: value for key, value in check.items() if key != "id"})[:24]
            bundle_id = new_id("BA")
            prefix = f"runtime/artifacts/{bundle_id}"
            execution = self.runtime["executions"][execution_id]
            execution["submission_check_ref"] = prefix + "/check.json"
            execution["submitted_output_ref"] = prefix + "/output.json"
            execution["submitted_extensions_ref"] = prefix + "/extensions.json"
            execution["extensions"] = extensions
            self.runtime.setdefault("events", []).append({"id": new_id("EV"), "kind": "submission_unsealed",
                "execution_id": execution_id, "at": now(), "evidence_refs": [prefix + "/check.json"],
                "reason": "worker output did not pass through the central submit capture"})
            self._save({prefix + "/check.json": lossless_json(check),
                        prefix + "/output.json": lossless_json(output),
                        prefix + "/extensions.json": lossless_json(extensions)})
        received = self._apply_submission_bundles(action, output, extensions, execution_id, context, check["issues"])
        self._remove_action(action)
        execution = self.runtime["executions"][execution_id]
        if received["status"] == "accepted":
            disposition = {"kind": "submission_integrated", "integration_ids": [row["integration_id"] for row in received["bundles"]]}
            if execution["status"] == "ended":
                # Integration can finish after the process. Updating its result never
                # reopens execution authority or changes the physical end time.
                execution.update(outcome="output_accepted", result_disposition=disposition)
            else:
                execution_lifecycle.transition_execution(execution, "ended", at=now(), outcome="output_accepted", disposition=disposition)
            # Domain application may have replaced this wait with a new obligation.
            # Only the exact publication/impact wait discharged by this receipt ends.
            if (previous_wait and previous_wait.get('kind') in {'submission_publication', 'impact_review'}
                    and previous_wait.get('execution_id') == execution_id
                    and self.runtime.get('waiting_actions', {}).get(action.get('id')) == previous_wait):
                del self.runtime['waiting_actions'][action['id']]
            execution["error"] = None
            self._resolve_failed_actions(action, execution_id)
            if self.instance.get("lifecycle", {}).get("state") != "initializing":
                self._ensure_academic_followup()
            self.runtime["history"].append({"role": action["role"], "execution_id": execution_id,
                                            "summary": output["summary"]})
            if action["role"] == "operational_review":
                target_id = action["target"]
                tracker = self._trackers.get(target_id)
                if tracker and action.get("observation_refs"):
                    tracker.acknowledge_review(observation_refs=action["observation_refs"])
                disposition = output["disposition"]
                if tracker and disposition["kind"] == "continue" and disposition.get("next_review"):
                    review = disposition["next_review"]
                    disposition_id = self.runtime["executions"][target_id]["operational_continuation"]["disposition_id"]
                    tracker.schedule_review(disposition_id, at=review["at"], reason=review["reason"],
                                            basis_ref=disposition_id)
                if self.runtime["executions"][target_id]["status"] == "running":
                    try:
                        publish_worker_feedback(Path(self.instance["workspace"]) / "runs" / target_id / "workspace" / ".control",
                                                operational_dispositions.worker_feedback(output["disposition"]))
                    except OSError as error:
                        self.runtime["history"].append({"kind": "feedback_delivery_failed", "execution_id": execution_id, "error": str(error)})
        else:
            if not any(row.get("next_owner") == "engine" for row in received["bundles"]):
                execution_lifecycle.transition_execution(execution, "ended", at=now(), outcome="execution_incomplete",
                    disposition={"kind": "submission_returned", "retry_bundle_ids": received["retry_bundle_ids"]})
            execution.update(error_kind=integration.failure_kind(received['issues']),
                             error="one or more integration bundles were returned")
            # This remains an AI-owned repair; a counter never creates user authority.
            if any(row.get("next_owner") == "engine" for row in received["bundles"]):
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                    **self.runtime.get("waiting_actions", {}).get(action["id"], {}), "action": deepcopy(action),
                    "kind": "submission_publication", "execution_id": execution_id, "next_owner": "engine",
                    "reason": "Reload current Git state and reapply only unpublished candidate bundles"}
            elif any(row.get("next_owner") == "impact_review" for row in received["bundles"]):
                self._hold_impact_reviews(action, execution_id, received)
            else:
                repair_execution.route_submission_return(self, action, received, execution_id, output)
        publication_pending = any(row.get("next_owner") in {"engine", "impact_review"} for row in received["bundles"])
        if not publication_pending:
            self._record_task_receipt(action, output or {}, execution_id, accepted=received["status"] == "accepted")
            if action["role"] == "operational_review":
                self._save()
                try:
                    self._run_pending_operational_repairs()
                except (ValueError, OSError, GitStateStoreError) as error:
                    # The response is already authoritative; local-effect recovery
                    # never revokes an accepted bundle or repeats its task receipt.
                    self.head, self.instance, self.runtime = self.store.load()
                    self._saved_state = self._state_signature()
                    self.runtime["history"].append({"kind": "operational_repair_interrupted",
                        "execution_id": execution_id, "reason": str(error), "next_owner": "engine"})
        if received["status"] == "accepted" and action["role"] == "maintenance" and action.get("cleanup_execution_ids"):
            self._save()
            try:
                self._maintenance_cleanup(action, execution_id)
            except (ValueError, OSError) as error:
                self.runtime["history"].append({"kind": "maintenance_cleanup_failed", "execution_id": execution_id,
                    "reason": str(error), "next_owner": "maintenance"})
        if self.runtime["status"] == "running":
            self.runtime["status"] = "ready"
        return received

    def _available_inputs(self) -> list[str]:
        result = {"SKILL.md", "GLOSSARY.md", "context:goal", "context:policy"}
        if self.instance["config"].get("lean_command") or discover_lean():
            result.add("tool:lean")
        if self.instance["config"]["scholarly_enabled"] and self.instance["config"]["scholarly_server"]:
            result.add("tool:scholarly")
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

    def _retry_initial_execution_action(self, request: dict, waiting: dict) -> dict:
        """Retry an ended initial interpretation without replacing its source or authority."""
        if request['config']['retry_action'] != waiting.get('action', {}).get('id'):
            raise ValueError('retry action differs from the held initial action')
        return self._continue_initial_execution(waiting, request_id=request['id'])

    def _validate_initial_retry(self, waiting, *, diagnostic_action_id=None):
        original = waiting.get('action', {})
        identifier = original.get('id')
        lifecycle = self.instance['lifecycle']
        predecessor = self.runtime['executions'].get(waiting.get('execution_id'), {})
        if (lifecycle['state'] != 'initializing' or lifecycle.get('intent_check')
                or original.get('id') != identifier or original.get('role') != 'intent_interpretation'
                or original.get('target') != lifecycle.get('input_id')
                or predecessor.get('status') != 'ended'
                or predecessor.get('outcome') != 'execution_incomplete'
                or predecessor.get('action', {}).get('id') != identifier
                or predecessor.get('action', {}).get('target') != original.get('target')):
            raise ValueError('retry requires the ended failed interpretation of the original initial input')
        source = next((row for row in self.runtime.get('inputs', [])
                       if row['id'] == lifecycle['input_id']), {})
        if any(source.get(key) != lifecycle['immutable_input'][key] for key in ('text', 'sha256')):
            raise ValueError('initial retry source differs from the immutable original input')
        activity_id = original.get('owner_activity_id')
        activity = self.runtime.get('activities', {}).get(activity_id, {})
        condition = activity.get('waiting', {}).get('condition', {})
        if (activity.get('status') != 'waiting' or identifier not in condition.get('action_ids', [])
                or predecessor.get('owner_activity_id') != activity_id):
            raise ValueError('initial retry requires its original waiting activity')
        if any(self.runtime['executions'][eid]['status'] != 'ended'
               for eid in activity.get('assigned_execution_ids', [])):
            raise ValueError('initial retry cannot overlap a live predecessor')
        if (predecessor.get('capacity', {}).get('local_termination') != 'confirmed'
                or any(row.get('owner_id') == predecessor['id'] and row.get('state') == 'held'
                       for row in self.runtime.get('reservations', {}).values())):
            raise ValueError('initial retry requires confirmed local termination and released reservations')
        if any(row.get('id') == identifier for row in self.runtime['queue']):
            raise ValueError('initial retry action is already queued')
        if any(row['status'] != 'ended' and (row.get('action', {}).get('role') == 'operational_review'
                   or row.get('action', {}).get('initial_submission_diagnosis'))
               and (diagnostic_action_id is None or row.get('action', {}).get('id') != diagnostic_action_id)
               and row.get('action', {}).get('target') == predecessor['id']
               for row in self.runtime['executions'].values()):
            raise ValueError('initial retry cannot overlap its operational diagnosis')
        return original, predecessor, source, activity, condition

    def _continue_initial_execution(self, waiting, *, request_id, diagnosis=None):
        original, predecessor, source, activity, condition = self._validate_initial_retry(waiting)
        identifier, activity_id = original['id'], activity['id']
        lifecycle = self.instance['lifecycle']
        request = {'id': request_id}
        action = deepcopy(original)
        if diagnosis is not None:
            action['diagnosis_attempt'] = 1
            if 'repair' in action:
                action['repair']['diagnosis'] = deepcopy(diagnosis)
            else:
                action['recovery'] = {'execution_id': predecessor['id'], 'reason': diagnosis['guidance']}
        # Check present initial authority even if the old native final is reusable.
        for field in ('profile_ref', 'model_selection', 'actor_kind', 'budget_kind', 'dispatch_wait', 'grant_id'):
            action.pop(field, None)
        action['profile_ref'] = deepcopy(lifecycle.get('adoption', {}).get('initial_profile_ref'))
        self._action_lifecycle_gate(action)
        if self._resume_initial_native_final(request, waiting, predecessor):
            return deepcopy(original)
        action['continuation_of'] = predecessor['id']
        superseded = [deepcopy(row) for row in self.runtime['queue']
                      if (row.get('role') == 'operational_review' or row.get('initial_submission_diagnosis'))
                      and row.get('target') == predecessor['id']]
        activities.resume_activity(self.runtime, activity_id, condition=condition, at=now())
        del self.runtime['waiting_actions'][identifier]
        self.runtime['queue'] = [row for row in self.runtime['queue'] if row not in superseded]
        self.runtime['queue'].insert(0, action)
        self.runtime.setdefault('history', []).append({'kind': 'initial_execution_retry_started',
            'request_id': request['id'], 'action_id': identifier, 'activity_id': activity_id,
            'execution_id': predecessor['id'], 'input_ref': source['id'], 'input_sha256': source['sha256'],
            'prior_failure': deepcopy(waiting), 'superseded_diagnoses': superseded,
            'profile_ref': deepcopy(action['profile_ref']), 'grant_id': action['grant_id'], 'started_at': now()})
        self.runtime['status'] = 'initializing'
        return action

    def _resume_initial_native_final(self, request, waiting, execution):
        """Reuse a preserved normal terminal after central retry validation."""
        if not execution.get('result_ref'):
            return False
        result = json.loads(self.store.read(execution['result_ref'], self.head))
        legacy_unsealed = (result.get('status') == 'failed'
            and result.get('error_kind') == 'execution_failure'
            and result.get('error') == 'Execution ended without a centrally sealed submission')
        if (execution.get('submission_intent') or result.get('collection') != 'provider_evidence_only'
                or not (result.get('status') == 'completed' or legacy_unsealed)):
            return False
        from .model_runner import verified_native_final
        base = f"runtime/artifacts/{execution['input_bundle']}"
        context = submission.load_json(self.store.read(base + '/input/submission/context.json', self.head))
        schema = submission.load_json(self.store.read(base + '/schema.json', self.head))
        raw = verified_native_final(result, execution, context, recovery=True)
        if execution.get('outputs_complete') is not True:
            raise ValueError('native recovery requires complete preserved workspace outputs')
        files, manifest = {}, []
        for row in execution.get('output_files', []):
            path = row['path']
            data = self.store.read(row['artifact_ref'], self.head)
            if path in files or hashlib.sha256(data).hexdigest() != row['sha256'] or len(data) != row['bytes']:
                raise ValueError('preserved native output differs from its execution manifest')
            files[path] = data
            manifest.append({key: row[key] for key in ('path', 'sha256', 'bytes')})
        if sum(map(len, files.values())) > self.instance['config']['max_artifact_bytes']:
            raise ValueError('preserved native outputs exceed the current artifact limit')
        preserved = {'files': files, 'manifest': manifest, 'omitted': [], 'complete': True}
        self.runtime['history'].append({'kind': 'native_final_recovery_requested', 'request_id': request['id'],
            'execution_id': execution['id'], 'action_id': execution['action']['id'],
            'activity_id': execution['owner_activity_id'], 'prior_failure': deepcopy(waiting),
            'prior_result_ref': execution['result_ref'], 'prior_outcome': execution['outcome'],
            'original_final_sha256': hashlib.sha256(raw).hexdigest()})
        workspace = Path(self.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
        receipt = self._capture_native_submission(execution, result, context, schema, workspace, raw,
            recovery_request=request['id'], captured_outputs=preserved)
        if receipt['state'] != 'accepted':
            raise ValueError('preserved native final failed central validation: ' + receipt['payload']['submission_check']['check_ref'])
        self._finish_native_recovery(request, execution['id'])
        return True

    def _finish_native_recovery(self, request, execution_id):
        execution = self.runtime['executions'][execution_id]
        if (execution.get('submission_receipt', {}).get('recovery_request_id') != request['id']
                or execution['status'] != 'ended' or execution.get('stop_requested')
                or self.runtime['status'] in {'paused', 'closed', 'completed'}
                or not governance.authorize(self.instance, execution['action'], runtime=self.runtime)['allowed']):
            raise ValueError('native recovery no longer has current request authority')
        action = deepcopy(execution['action'])
        activity = self.runtime['activities'][execution['owner_activity_id']]
        if activity['status'] == 'waiting':
            activities.resume_activity(self.runtime, activity['id'], condition=deepcopy(activity['waiting']['condition']), at=now())
        self.runtime.get('waiting_actions', {}).pop(action['id'], None)
        self.runtime['queue'] = [row for row in self.runtime['queue']
            if not ((row.get('role') == 'operational_review' or row.get('initial_submission_diagnosis'))
                    and row.get('target') == execution_id)]
        base = f"runtime/artifacts/{execution['input_bundle']}"
        context = submission.load_json(self.store.read(base + '/input/submission/context.json', self.head))
        schema = submission.load_json(self.store.read(base + '/schema.json', self.head))
        workspace = Path(self.instance['workspace']) / 'runs' / execution_id / 'workspace'
        received = self._receive_submission(action, {}, execution_id, context, schema, workspace, preserved=True)
        self.runtime['history'].append({'kind': 'native_final_recovery_completed', 'request_id': request['id'],
            'execution_id': execution_id, 'action_id': action['id'], 'result': deepcopy(received)})
        self.runtime['status'] = 'initializing'
        return received

    def _retry_input_overflow_action(self, request: dict) -> dict:
        """Requeue one exact held action; admission still decides recovery."""
        identifier = request.get("config", {}).get("retry_action")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("retry_action must name one held action")
        if self.runtime.get("status") in {"completed", "closed"} or self.instance.get("lifecycle", {}).get("permanently_closed"):
            raise ValueError("closed/completed instance cannot retry an input overflow")
        native = next((row for row in self.runtime.get('executions', {}).values()
            if row.get('submission_receipt', {}).get('kind') == 'native_final'
            and row['submission_receipt'].get('recovery_request_id') == request['id']
            and row.get('action', {}).get('id') == identifier), None)
        if native:
            if native.get('outcome') != 'output_accepted':
                self._finish_native_recovery(request, native['id'])
            return deepcopy(native['action'])
        waiting = self.runtime.get("waiting_actions", {}).get(identifier)
        if waiting and waiting.get("kind") in {"execution_failure", "submission_failure", "output_validation"}:
            return self._retry_initial_execution_action(request, waiting)
        return self._resume_input_overflow_action(identifier, request['id'])

    def _resume_input_overflow_action(self, identifier, decision_id, *, selected_profile=None):
        """Continue the existing obligation after either an authorized user or plan decision."""
        if self.runtime.get('status') in {'completed', 'closed'} or self.instance.get('lifecycle', {}).get('permanently_closed'):
            raise ValueError('closed/completed instance cannot retry an input overflow')
        waiting = self.runtime.get('waiting_actions', {}).get(identifier)
        if not waiting or waiting.get("kind") != "input_overflow":
            raise ValueError("retry_action must name a current input_overflow action")
        original = waiting.get("action", {})
        if original.get("id") != identifier:
            raise ValueError("held input_overflow action identity differs")
        if any(row.get("id") == identifier for row in self.runtime.get("queue", [])):
            raise ValueError("input_overflow action is already queued")
        activity_id = original.get("owner_activity_id")
        activity = self.runtime.get("activities", {}).get(activity_id)
        if activity is None or activity.get("status") == "finished":
            raise ValueError("input_overflow owner activity is absent or finished")
        live = [eid for eid in activity.get("assigned_execution_ids", [])
                if self.runtime.get("executions", {}).get(eid, {}).get("status") != "ended"]
        if live:
            raise ValueError("input_overflow retry cannot overlap a live execution")
        if activity.get("status") != "waiting" or activity.get("waiting", {}).get("reason") != "input_overflow":
            raise ValueError("input_overflow owner activity is not waiting on this failure")
        condition = activity["waiting"]["condition"]
        if identifier not in condition.get("action_ids", []):
            raise ValueError("activity wait does not name the held input_overflow action")
        action = deepcopy(original)
        for field in ("profile_ref", "model_selection", "actor_kind", "budget_kind", "dispatch_wait"):
            action.pop(field, None)
        if selected_profile is not None:
            action['profile_ref'] = deepcopy(selected_profile)
        action["input_overflow_retry"] = {"action_id": identifier,
            "question_id": waiting["question_id"], "request_id": decision_id,
            "started_at": now(), "state": "pending"}
        # This is a technical retry, not new authority. Recheck the currently
        # adopted profile, current grant and current lifecycle before mutation.
        self._action_lifecycle_gate(action)
        activities.resume_activity(self.runtime, activity_id, condition=condition, at=now())
        del self.runtime["waiting_actions"][identifier]
        self.runtime["queue"].insert(0, action)
        self.runtime.setdefault("history", []).append({"kind": "input_overflow_retry_started",
            "action_id": identifier, "activity_id": activity_id, "question_id": waiting["question_id"],
            "request_id": decision_id, "started_at": action["input_overflow_retry"]["started_at"],
            "profile_ref": deepcopy(action.get("profile_ref")), "grant_id": action.get("grant_id")})
        self.runtime["status"] = "ready"
        return action

    def _apply_input_overflow_resolutions(self, choices, fixed, execution_id):
        if not choices:
            return
        from .input_recovery import overflow_requests, validate_resolutions
        supplied = fixed.get('input_overflow_requests', [])
        validate_resolutions(choices, supplied)
        current = overflow_requests(self.instance, self.runtime)
        validate_resolutions(choices, current)
        before = {row['action_id']: row for row in supplied}
        after = {row['action_id']: row for row in current}
        for choice in choices:
            identifier = choice['action_id']
            if before[identifier] != after[identifier]:
                raise ValueError('input overflow request changed before profile selection: ' + identifier)
            task = self.runtime['tasks'][after[identifier]['task_id']]
            if planning.contract_hash(task) != after[identifier]['contract_sha256']:
                raise ValueError('input overflow task contract changed: ' + identifier)
        for choice in choices:
            self._resume_input_overflow_action(choice['action_id'], execution_id,
                                               selected_profile=choice['profile_ref'])

    @staticmethod
    def _pending_input_overflow_retry(action: dict) -> dict | None:
        retry = action.get("input_overflow_retry")
        if retry and retry.get("state", "pending") == "pending":
            return retry
        return None

    def _set_input_overflow_retry_state(self, action: dict, state: str, **detail) -> dict:
        retry = action["input_overflow_retry"]
        retry.update(state=state, **detail)
        candidates = list(self.runtime.get("queue", []))
        candidates.extend(row.get("action", {}) for row in self.runtime.get("waiting_actions", {}).values())
        for candidate in candidates:
            stored = candidate.get("input_overflow_retry")
            if (candidate.get("id") == action.get("id") and stored
                    and stored.get("question_id") == retry.get("question_id")
                    and stored.get("request_id") == retry.get("request_id")):
                candidate["input_overflow_retry"] = deepcopy(retry)
        return retry

    def _resolve_input_overflow_question(self, identifier: str, *, execution_id: str,
                                         kind: str, evidence: dict) -> str:
        row = next((row for row in self.runtime.get("question_links", []) if row["id"] == identifier), None)
        if row is None:
            raise ValueError("input_overflow retry question is unknown")
        if row.get("status") in {"resolved", "superseded"} and not row.get("unresolved_target_ids"):
            return "already_resolved"
        if row.get("status") != "open":
            raise ValueError("input_overflow retry question is no longer open")
        row.update(status="resolved", resolution_ref=execution_id, unresolved_target_ids=[])
        row.setdefault("resolution_history", []).append({"kind": kind,
            "resolution_ref": execution_id, "evidence": deepcopy(evidence)})
        return "resolved"

    def _consume_action_events(self, action: dict, execution_id: str) -> None:
        consumed = set(action.get("event_refs", []))
        if consumed:
            self.runtime["history"].append({"kind": "event_consumption", "event_ids": sorted(consumed),
                                            "execution_id": execution_id, "consumed_at": now()})
        for event in self.runtime.get("events", []):
            if event["id"] in consumed:
                if event["kind"] == "task_new_input" and event.get("target") in self.runtime["tasks"]:
                    self.runtime["tasks"][event["target"]]["newinput"] = False
        self.runtime["pending_events"] = [entry for entry in self.runtime.get("pending_events", [])
                                           if isinstance(entry, dict) or entry not in consumed]

    def _read_extensions(self, workspace: Path) -> dict:
        return submission.read_extensions(workspace)

    def _review_observation_source(self, execution_id, event):
        execution = self.runtime["executions"][execution_id]
        action = execution.get("action", {})
        if (action.get("role") != "identity_review" or not action.get("review_cycle_id")
                or event.get("type") in {"transport_bytes_received", "tick"}):
            return None
        cursors = getattr(self, "_review_event_cursors", {})
        index, offset = cursors.get(execution_id, (0, 0))
        path = Path(self.instance["workspace"]) / "runs" / execution_id / "evidence/stdout.jsonl"
        with path.open("rb") as stream:
            stream.seek(offset)
            raw = stream.readline()
            while raw and not raw.strip():
                index += 1
                raw = stream.readline()
            offset = stream.tell()
        if not raw:
            raise ValueError("review observation has no actual provider JSONL row")
        try:
            decoded = json.loads(raw)
        except (UnicodeError, json.JSONDecodeError):
            decoded = {"type": "unparsed_observation", "bytes": len(raw.rstrip(b"\n"))}
        if decoded != event:
            raise ValueError("review observation differs from its actual provider row")
        return {"raw": raw, "event_index": index, "next_cursor": (index + 1, offset),
                "artifact_ref": f"runtime/artifacts/{new_id('BA')}/provider-event.jsonl"}

    def _drain_review_observations(self, execution_id, tracker):
        action = self.runtime["executions"][execution_id]["action"]
        if action.get("role") != "identity_review" or not action.get("review_cycle_id"):
            return
        path = Path(self.instance["workspace"]) / "runs" / execution_id / "evidence/stdout.jsonl"
        if not path.is_file():
            return
        while True:
            _, offset = getattr(self, "_review_event_cursors", {}).get(execution_id, (0, 0))
            with path.open("rb") as stream:
                stream.seek(offset)
                raw = stream.readline()
                while raw and not raw.strip():
                    raw = stream.readline()
            if not raw:
                return
            try:
                event = json.loads(raw)
            except (UnicodeError, json.JSONDecodeError):
                event = {"type": "unparsed_observation", "bytes": len(raw.rstrip(b"\n"))}
            self._observe_running(execution_id, tracker, event)

    def _observe_running(self, execution_id: str, tracker: ObservationTracker, event: dict) -> None:
        self._controls()
        if self._check_conversations():
            self._save()
        candidate = deepcopy(tracker)
        # These are provider-observed MCP identities, not IDs claimed in a draft.
        calls = []
        item = event.get("item", {})
        if (event.get("type") in {"item.started", "item.completed"} and item.get("type") == "mcp_tool_call"
                and item.get("server") == "execution_control" and item.get("tool") in {"control_self_check", "control_submit", "control_receipt"}):
            calls.append(item)
        if event.get("type") == "assistant":
            calls.extend(block for block in event.get("message", {}).get("content", [])
                if isinstance(block, dict) and block.get("type") == "tool_use"
                and block.get("name") in {"mcp__execution_control__control_self_check", "mcp__execution_control__control_submit", "mcp__execution_control__control_receipt"})
        candidate.register_self_check_calls([call["id"] for call in calls if isinstance(call.get("id"), str)])
        pending = set(candidate.pending_tools)
        if pending and pending <= candidate.self_check_call_ids:
            checkpoint = read_checkpoint(candidate.workspace)
            if checkpoint["status"] == "valid" and checkpoint["sha256"] not in candidate.seen_checkpoints:
                candidate.register_self_check_checkpoint(checkpoint["sha256"])
        original_instance, original_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        artifacts, self_checks, feedback = {}, [], []
        remind = False
        coordinate = None
        try:
            coordinate = self._review_observation_source(execution_id, event)
            if coordinate:
                artifacts[coordinate["artifact_ref"]] = coordinate["raw"]
                self._record_review_observation(execution_id, event, artifact_ref=coordinate["artifact_ref"],
                                                event_index=coordinate["event_index"])
            for observed in candidate.observe(event):
                kind = observed["kind"]
                if kind == "observation_fact":
                    self.runtime.setdefault("observation_facts", {})[observed["id"]] = persistent_record(observed)
                elif kind == "self_check_due":
                    self_checks.append(deepcopy(observed))
                elif kind in {"observation_rules", "checkpoint"}:
                    ref = f"runtime/artifacts/{new_id('BA')}/{kind}.json"
                    record = persistent_record(observed, artifact_ref=ref)
                    artifacts[ref] = observed["raw"]
                    if kind == "checkpoint":
                        record["kind"] = "worker_checkpoint"
                        self.runtime.setdefault("checkpoints", {})[execution_id] = record
                    else:
                        self.runtime.setdefault("observation_rules", {})[execution_id] = record
                elif kind == "checkpoint_reminder_due":
                    remind = True
                else:
                    record = persistent_record(observed if observed.get("id") else
                        candidate._fact("observation_fact", observed, candidate.clock()))
                    self.runtime.setdefault("observation_facts", {})[record["id"]] = record
                    trigger = kind in {"operational_review_due", "tool_review_due", "periodic_review_due", "explicit_review_due"}
                    trigger = trigger or observed.get("followup", {}).get("kind") == "operational_review_due"
                    if trigger and not self._inline_reviewing and self.runtime["status"] not in {"paused", "closed"}:
                        observation = {**persistent_record(observed), "observation_refs": [record["id"]]}
                        self.runtime.setdefault("observations", {})[execution_id] = observation
                        self._enqueue("operational_review", execution_id, live=True, observation=observation,
                            obligation_ids=observed.get("obligation_ids", [observed["obligation_id"]] if observed.get("obligation_id") else []),
                            observation_refs=[record["id"]])
                    if observed.get("worker_feedback"):
                        feedback.append(observed["worker_feedback"])
            self.runtime.setdefault("self_check_obligations", {}).update(deepcopy(candidate.obligations))
            self._save(artifacts or None)
        except Exception:
            self.instance, self.runtime = original_instance, original_runtime
            raise
        tracker.__dict__.clear()
        tracker.__dict__.update(candidate.__dict__)
        if coordinate:
            if not hasattr(self, "_review_event_cursors"):
                self._review_event_cursors = {}
            self._review_event_cursors[execution_id] = coordinate["next_cursor"]
        for obligation in self_checks:
            self._transport.request_self_check(self._transport_bindings[execution_id],
                self_check_id=obligation["id"], payload=self_check_feedback(obligation))
        if remind:
            write_checkpoint_reminder(candidate.workspace / ".control")
        for item in feedback:
            publish_worker_feedback(candidate.workspace / ".control", item)

    def _run_inline_review(self, parent_id: str, observation: dict) -> None:
        # All operational reviews use the same fixed-profile execution and receipt path.
        self._enqueue("operational_review", parent_id, live=True, observation=json_safe(observation),
                      obligation_ids=observation.get("obligation_ids", []),
                      observation_refs=observation.get("observation_refs", []))
        self._save()

    def _budget_available(self, pool: str, used: int, required: int = 1) -> bool:
        if self._session_mode():
            return True  # Future sequential investigations reserve only when actually dispatched.
        remaining = self._provider_slots().usage_snapshot()[pool]["available"]
        return remaining is None or remaining >= required

    def _runner_tools(self, arguments: dict) -> None:
        parameters = inspect.signature(self.runner.run).parameters
        extra = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
        for name, value in execution_profiles.runner_tools(arguments["profile"]).items():
            if name in parameters or extra:
                arguments[name] = value
            elif value:
                raise ValueError("runner cannot consume profile field: " + name)

    def _collect_submitted_result(self, execution, result, context, schema, workspace):
        """Consume the sole central candidate, or capture a verified normal final."""
        intent = execution.get("submission_intent")
        if not intent:
            if result.get('collection') != 'provider_evidence_only':
                return result
            try:
                from .model_runner import verified_native_final
                raw = verified_native_final(result, execution, context)
                receipt = self._capture_native_submission(execution, result, context, schema, workspace, raw)
                if receipt['state'] != 'accepted':
                    evidence = receipt['payload']['submission_check']
                    check = submission.load_json(self.store.read(evidence['check_ref'], self.head))
                    if check.get('failure_kind') == 'output_validation':
                        prefix = evidence['check_ref'].rsplit('/', 1)[0]
                        return {**result, 'status': 'failed', 'output': None, 'error_kind': 'output_validation',
                            'error': 'native final failed central structural validation; see ' + evidence['check_ref'],
                            'rejected_submission': {'check_ref': evidence['check_ref'],
                                'raw_output_ref': prefix + '/output.json', 'raw_output_sha256': receipt['final_sha256']}}
                    raise ValueError('native final failed central structural validation; see ' +
                                     receipt['payload']['submission_check']['check_ref'])
                execution = self.runtime['executions'][execution['id']]
                intent = execution['submission_intent']
            except (ValueError, KeyError, TypeError, OSError, GitStateStoreError) as error:
                return {**result, 'status': 'failed', 'output': None, 'error_kind': 'execution_failure',
                        'error': str(error)}
        if (result.get('error_kind') == 'model_policy' or execution.get('currentness_changes')
                or execution.get('stop_requested') or self.runtime['status'] in {'paused', 'closed', 'completed'}):
            return result
        try:
            raw = self.store.read(intent['output_ref'], self.head)
            if hashlib.sha256(raw).hexdigest() != intent.get('output_sha256'):
                raise ValueError('sealed submission output hash differs')
            output = submission.load_json(raw)
        except (ValueError, TypeError, KeyError, OSError, GitStateStoreError) as error:
            return {**result, 'status': 'failed', 'output': None, 'error_kind': 'execution_failure',
                    'error': 'existing sealed submission cannot be read: ' + str(error)}
        return {**result, 'status': 'completed', 'output': output,
                'collection': 'sealed_submission', 'provider_result_status': result['status']}

    def _stage_submission_capture(self, execution, sealed, receipt, *, origin):
        """Stage one central check and its byte artifacts in the caller's CAS."""
        prefix = f"runtime/artifacts/{new_id('BA')}/submission"
        artifacts = {prefix + '/' + path: raw for path, raw in sealed['artifacts'].items()}
        receipt['payload'] = {'origin': origin, 'submission_check': {
            'check_ref': prefix + '/check.json',
            'artifacts': [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                          for path, raw in artifacts.items()]}}
        if not sealed['capture_eligible']:
            receipt.update(state='rejected', reason='candidate validation failed')
        payload = {**(sealed['intent'] or {}), 'output_ref': prefix + '/output.json',
            'extensions_ref': prefix + '/extensions.json', 'check_ref': prefix + '/check.json',
            'manifest_ref': prefix + '/manifest.json',
            'file_refs': [{**row, 'artifact_ref': prefix + '/files/' + row['path']} for row in sealed['manifest']]}
        if sealed['capture_eligible']:
            if not sealed['passed']:
                receipt['reason'] = 'Candidate sealed; independent bundle issues remain for application'
            execution_lifecycle.record_submission_intent(execution, payload, receipt)
        details = {'basis': {'origin': origin, 'receipt': deepcopy(receipt)}} if origin == 'native_final' else {}
        self._lifecycle_event('submission_checked', target=execution['id'],
            source_ref=execution['id'] if origin == 'native_final' else receipt['id'],
            schedule=False, evidence_refs=[prefix + '/check.json'], **details)
        return artifacts

    def _capture_native_submission(self, execution, result, context, schema, workspace, raw, *, recovery_request=None, captured_outputs=None):
        """Publish native capture without inventing a worker control request."""
        prior = next((event['basis']['receipt'] for event in self.runtime.get('events', [])
            if event['kind'] == 'submission_checked' and event.get('target') == execution['id']
            and event.get('basis', {}).get('origin') == 'native_final'), None)
        if prior:
            if prior['final_sha256'] != hashlib.sha256(raw).hexdigest():
                raise ValueError('a different native final was already captured for this execution')
            return prior
        if (execution.get('submission_intent') or execution.get('currentness_changes')
                or execution.get('stop_requested') or execution.get('authority_revocation')
                or execution.get('stop_reason') or self.runtime.get('stop_requested')
                or self.runtime['status'] in {'paused', 'closed', 'completed'}
                or execution['status'] != ('ended' if recovery_request else 'running')
                or not governance.authorize(self.instance, execution['action'], runtime=self.runtime)['allowed']
                or not self._clock_guard()['usable']):
            raise ValueError('native candidate no longer has current submission authority')
        changes = decision_basis_changes(execution.get('decision_basis'), self.instance, self.runtime)
        changes.extend(self._execution_requirement_changes(execution['action'], evaluation_context=self._evaluation_context()))
        if (changes or not sources_current(execution.get('source_basis', []), self.instance)
                or any(execution.get(key) != value for key, value in planning.governance_revisions(self.instance).items())
                or execution['action']['role'] == 'goal_audit' and execution['action'].get('basis') != self._goal_basis_key()):
            raise ValueError('native candidate input premises changed before capture')
        base = f"runtime/artifacts/{execution['input_bundle']}"
        fixed = submission.load_json(self.store.read(base + '/input/submission/context.json', self.head))
        fixed_schema = submission.load_json(self.store.read(base + '/schema.json', self.head))
        if fixed != context or fixed_schema != schema:
            raise ValueError('native capture differs from the published input or schema')
        sealed = submission.seal_submission(workspace, execution_id=execution['id'], context=fixed,
            schema=fixed_schema, raw_output=raw, captured_outputs=captured_outputs,
            max_artifact_bytes=self.instance['config']['max_artifact_bytes'])
        proof = deepcopy(result)
        proof['output'] = None
        proof['execution']['collect']['final'] = {key: value for key, value in
            proof['execution']['collect']['final'].items() if key != 'raw'}
        proof['execution']['collect']['final']['artifact'] = 'output.json'
        sealed['artifacts']['native-evidence.json'] = lossless_json(json_safe(proof))
        receipt = {'id': new_id('NF'), 'kind': 'native_final', 'state': 'accepted',
            'execution_id': execution['id'], 'received_at': now(), 'parent_snapshot': self.head,
            'final_sha256': hashlib.sha256(raw).hexdigest()}
        if recovery_request:
            receipt['recovery_request_id'] = recovery_request
        original_instance, original_runtime, original_head = deepcopy(self.instance), deepcopy(self.runtime), self.head
        try:
            artifacts = self._stage_submission_capture(execution, sealed, receipt, origin='native_final')
            self._save(artifacts)
        except Exception:
            head, instance, runtime = self.store.load()
            self.head, self.instance, self.runtime = head, instance, runtime
            saved = next((event['basis']['receipt'] for event in runtime.get('events', [])
                if event['kind'] == 'submission_checked' and event.get('basis', {}).get('origin') == 'native_final'
                and event['basis']['receipt']['id'] == receipt['id']), None)
            if saved:
                return saved
            if head == original_head:
                self.instance, self.runtime = original_instance, original_runtime
            raise
        return receipt

    def _resolve_failed_actions(self, action: dict, execution_id: str) -> None:
        keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "assessment_targets", "observation_rule_targets", "review_basis_key", "live")
        for aid, entry in list(self.runtime.get("waiting_actions", {}).items()):
            previous = entry["action"]
            if entry.get("kind") not in {"output_validation", "execution_failure"}:
                continue
            if previous.get("lineage_id", previous.get("id")) != action.get("lineage_id", action.get("id")):
                continue
            if not all(previous.get(key) == action.get(key) for key in keys):
                continue
            self.runtime["history"].append({"kind": "failed_action_resolved", "action_id": aid,
                "failed_execution_id": entry.get("execution_id"), "resolved_by": execution_id,
                "previous": deepcopy(entry)})
            del self.runtime["waiting_actions"][aid]
            # Keep unconsumed events available for a current action instead of
            # leaving their ownership attached to the retired failed action.
            for event in self.runtime.get("events", []):
                if event.get("assigned_to") == aid and not event.get("consumed_at"):
                    event.pop("assigned_to", None)
                    event.pop("assigned_at", None)

    def _call(self, action: dict) -> bool:
        generator = self._call_steps(action)
        try:
            arguments = next(generator)
        except StopIteration as result:
            return result.value
        try:
            output = self.runner.run(**arguments)
        except Exception as error:
            output = {"status": "failed", "output": None, "usage": {}, "error": f"{type(error).__name__}: {error}"}
        try:
            generator.send(output)
        except StopIteration as result:
            return result.value
        raise RuntimeError("model call did not finish")

    def _obsolete_action_reason(self, action: dict, *, execution_id=None) -> str | None:
        judgment = self._goal_audit_seal(action)
        if judgment and judgment['execution_id'] != execution_id:
            return 'The goal audit slot is already sealed by ' + judgment['execution_id']
        if action.get("role") == "operational_review" and action.get("live"):
            parent = self.runtime["executions"].get(action.get("target"))
            if not parent or parent.get("status") == "ended":
                return "The live observation target has ended"
        if action.get('role') == 'operational_review' and not action.get('live'):
            if any(row.get('kind') in {'failed_action_resolved', 'failed_action_explicitly_resolved'}
                   and row.get('failed_execution_id') == action.get('target') for row in self.runtime.get('history', [])):
                return 'The failed action has already been resolved; its execution remains historical evidence'
        for field in ('assessment_targets', 'observation_rule_targets'):
            for tid, basis in action.get(field, {}).items():
                task = self.runtime["tasks"].get(tid)
                if not task or task.get("status") in {"completed", "closed"} or model_policy.assessment_basis(task) != basis:
                    return field + " contract edition changed: " + tid
        task = self.runtime["tasks"].get(action.get("target"))
        if (task and action["role"] in {"research_work", "supplemental_research", "task_contract_review"}
                and task.get("status") in {"completed", "closed"}):
            return "The assigned task is already completed or closed"
        return self._obsolete_review_reason(action)

    def _call_steps(self, action: dict):
        if not self._check_installation(force=True):
            return False
        if not self._clock_guard()["usable"]:
            self.runtime["availability"] = {"state": "blocked", "reason": "clock_regression", "next_owner": "operator"}
            self._save()
            return False
        self._action_lifecycle_gate(action)
        if action["role"] == "identity_review" and not action.get("review_cycle_id"):
            item = self.instance["knowledge"][action["target"]]
            predecessor = self.instance["knowledge"].get(item.get("supersedes"), {})
            self._start_identity_review(action["target"], previous_cycle_id=predecessor.get("review_cycle_id"))
            self._remove_action(action)
            self._save()
            return True
        action.setdefault("id", new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        self._bind_revision_action(action)
        waits = self._revision_dispatch_waits(action)
        if waits:
            action["dispatch_wait"] = {"kind": "contract_revision", "blockers": waits}
            return False
        if not self._selected_action_current(action, evaluation_context=self._evaluation_context()):
            return True
        action = deepcopy(action)
        role = action["role"]
        obsolete = self._obsolete_action_reason(action)
        if obsolete:
            self._remove_action(action)
            self.runtime["history"].append({"kind": "obsolete_action", "action": action, "reason": obsolete})
            self._save()
            return True
        if role == "goal_audit" and action.get("basis") != self._goal_basis_key():
            for judgment in self.instance["goal_judgments"]:
                if judgment["basis"] == action.get("basis"): judgment["current"] = False
            self.runtime["queue"] = [a for a in self.runtime["queue"] if not (a["role"] == "goal_audit" and a.get("basis") == action.get("basis"))]
            self._enqueue("research_plan", reason="Goal audit inputs changed before the complete independent group finished")
            self._save()
            return True
        profile = self._execution_profile(action)
        activity = self._activity_for_action(action)
        pool = profile["budget_kind"]
        config = {**self.instance["config"], **execution_profiles.runtime_config(profile)}
        task = self.runtime["tasks"].get(action.get("target"), {})
        rules = (self.runtime.get("task_observation_rules", {}).get(
            action.get("target"), task.get("initial_observation_rules", []))
            if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id") else [])
        execution_id = new_id('EX')
        if config["observation_mode"] == "deadline_only":
            rules = []
        from .observations import observation_settings_errors
        settings_errors = observation_settings_errors(profile)
        try:
            if settings_errors:
                raise ValueError(json.dumps(settings_errors, ensure_ascii=False))
            if role == 'research_work':
                from .observations import bind_task_rules
                rules = bind_task_rules(rules, execution_id)
            observation_config = tracker_config(profile, initial_self_check_rules=rules,
                                              no_progress_limit=config.get("no_progress_limit"))
        except ValueError as error:
            next_owner = "research_preparation" if role == "research_work" and not settings_errors else "execution_profile"
            kind = "observation_rules" if next_owner == "research_preparation" else "observation_configuration"
            activities.wait_for(self.runtime, activity["id"], reason=str(error),
                condition={"kind": kind, "task_id": action.get("target")}, next_owner=next_owner, at=now())
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": deepcopy(action), "kind": kind, "reason": str(error), "next_owner": next_owner}
            if settings_errors:
                self.runtime['waiting_actions'][action['id']]['observation_errors'] = settings_errors
            self._remove_action(action)
            if next_owner == "research_preparation":
                self._enqueue("research_preparation", action.get("target"), reason="Supply valid observation rules before research starts")
            self._save()
            return True
        authority = governance.authorize(self.instance, action, runtime=self.runtime)
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
            ready = planning.task_ready(check_task, self.instance, self.runtime, action=action, include_scheduling_waits=False,
                                        evaluation_context=self._evaluation_context())
            if ready["state"] != "ready":
                self.runtime["tasks"][action["target"]]["status"] = "waiting"
                self.runtime["tasks"][action["target"]]["readiness_error"] = ready
                self._remove_action(action)
                self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
                self._save()
                return bool(self.runtime["queue"])
        activity_id = activity["id"]
        queued = self._register_execution(action, {"id": execution_id, "role": role, "status": "queued",
            "created_at": now(), "input_snapshot": self.head, "grant_id": authority["grant_id"]})
        if queued is None:
            self._save()
            return True
        execution_lifecycle.begin_preparation(queued, at=now())
        self._save()
        base = Path(self.instance["workspace"]) / "runs" / execution_id
        workspace = base / "workspace"
        workspace.mkdir(parents=True)
        self.instance["available_input_refs"] = self._available_inputs()
        preparation_started = time.monotonic()
        input_head = self.head
        self._preparing_input = True
        try:
            context = self._context(action, workspace, execution_id=execution_id)
        except ReviewPreparationDeferred as error:
            recovery = error.outcome["recovery"]
            reason = "review_authority" if error.outcome["disposition"] == "authorization_denied" else "review_input_restoration"
            next_owner = recovery["next_owner"]
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": deepcopy(action), "kind": reason, "next_owner": next_owner,
                "reason": "review input or authority requires resolution", "detail": deepcopy(recovery)}
            self._remove_action(action)
            self._discard_prepared_input(base, execution_id,
                reason="review input or authority requires resolution", cancelled=False)
            return True
        except InputPreparationInterrupted:
            self._controls(pump=False)
            self._discard_prepared_input(base, execution_id)
            return self.runtime["status"] not in {"paused", "closed", "completed"}
        except (ValueError, KeyError, TypeError, OSError) as error:
            self._discard_prepared_input(base, execution_id, reason=str(error), cancelled=False)
            raise
        finally:
            self._preparing_input = False
        binding = self._transport.issue(execution_id, authority["grant_id"], workspace=workspace)
        self._transport_bindings[execution_id] = binding
        context["control_binding"] = deepcopy(binding)
        schema = self._response_schema(action)
        if role == "intent_interpretation":
            context.setdefault("interpretation_to_check", None)
        try:
            fitted = prepare_role_input(context, instance=self.instance, runtime=self.runtime, role=role, profile=profile,
                snapshot=input_head, workspace=workspace, activity_id=activity_id, output_schema=schema,
                documents=self._documents[role], artifact_prefix=f"runtime/artifacts/{execution_id}",
                install_submission_tools=True, max_artifact_bytes=config["max_artifact_bytes"])
        except (ValueError, KeyError, TypeError, OSError) as error:
            self._discard_prepared_input(base, execution_id, reason=str(error), cancelled=False)
            raise
        context = submission.load_json((workspace / "input/submission/context.json").read_bytes())
        prompt = fitted["prompt"]
        self._controls(pump=False)
        if (self.runtime["status"] in {"paused", "closed", "completed"}
                or not self._check_installation(force=True)):
            self._discard_prepared_input(base, execution_id)
            return False
        if self.head != input_head:
            # A user control changed the input while it was materialized.
            # Keep its obligations queued and prepare a new immutable input.
            self._discard_prepared_input(base, execution_id)
            return True
        if fitted["overflow"]:
            detail = deepcopy(fitted["overflow"])
            if (role == 'identity_review' and action.get('review_cycle_id')
                    and detail.get('cause') == 'current_proposal_or_required_sources'
                    and detail.get('suggested_disposition') == 'unresolved_to_review_plan'):
                overflow_ref = f"runtime/artifacts/{new_id('BA')}/input-overflow.json"
                self.runtime.setdefault('input_overflows', []).append({
                    'action': deepcopy(action), 'detail': detail, 'source_catalog': fitted['manifest']})
                self.runtime['executions'][execution_id]['input_manifest'] = deepcopy(fitted['manifest'])
                execution_lifecycle.end_preparation(self.runtime['executions'][execution_id], at=now(),
                    stage='packing', reason='review proposal input overflow', cancelled=True)
                self._transport.close(binding, reason='review proposal input overflow')
                self._transport_bindings.pop(execution_id, None)
                self._request_review_resource_disposition(action, 'review_input_overflow', {
                    'execution_id': execution_id, 'action': deepcopy(action), 'overflow': detail, 'overflow_ref': overflow_ref})
                self._save({**fitted['artifacts'], overflow_ref: lossless_json(detail)})
                return True
            resolution = detail.setdefault("resolution_question", {"question": "Which authorized profile or scope change should resolve this input overflow?", "next_owner": "user"})
            overflow_ref = f"runtime/artifacts/{new_id('BA')}/input-overflow.json"
            question = questions.link(self.runtime, execution_id=execution_id, field="resolution_question/question",
                owner="research" if resolution["next_owner"] == "research_plan" else "user",
                targets=[action.get("target") or action["id"]], source_ref=overflow_ref,
                reason=resolution["question"], blocks=resolution["next_owner"] == "user")
            retry = self._pending_input_overflow_retry(action)
            if retry:
                question_disposition = self._resolve_input_overflow_question(
                    retry["question_id"], execution_id=execution_id,
                    kind="input_overflow_retry_replaced", evidence={
                        "action_id": action["id"], "request_id": retry["request_id"],
                        "replacement_question_id": question["id"], "overflow_ref": overflow_ref})
                self._set_input_overflow_retry_state(action, "failed",
                    failure_execution_id=execution_id, question_disposition=question_disposition)
                self.runtime.setdefault("history", []).append({"kind": "input_overflow_retry_failed",
                    "action_id": action["id"], "activity_id": activity_id, "request_id": retry["request_id"],
                    "prior_question_id": retry["question_id"], "question_id": question["id"],
                    "execution_id": execution_id, "profile_ref": deepcopy(action.get("profile_ref")),
                    "overflow_ref": overflow_ref, "question_disposition": question_disposition,
                    "failed_at": now()})
            self.runtime.setdefault("input_overflows", []).append({"action": action, "detail": detail, "source_catalog": fitted["manifest"]})
            self._remove_action(action)
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {"action": action,
                "kind": "input_overflow", "reason": "input_overflow", "detail": detail, "question_id": question["id"],
                "next_owner": resolution["next_owner"]}
            defer_input_overflow(self.runtime, detail, at=now(), question_ref=question["id"])
            self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            if resolution["next_owner"] == "research_plan":
                self._enqueue("research_plan", reason="Select an already authorized profile for the preserved input overflow",
                              input_overflow=deepcopy(detail), overflow_activity_id=activity_id)
            execution_lifecycle.end_preparation(self.runtime["executions"][execution_id], at=now(),
                stage="packing", reason="input overflow", cancelled=True)
            self._continue_prepared_action(self.runtime["executions"][execution_id])
            self._transport.close(binding, reason="input overflow")
            self._transport_bindings.pop(execution_id, None)
            self._settle_activity(execution_id)
            self._save({overflow_ref: lossless_json(detail)})
            return self.runtime["status"] == "ready"
        input_bundle = new_id("BA")
        basis_ids = []
        source_refs = []
        if action.get("target") in self.runtime["tasks"]:
            task = self.runtime["tasks"][action["target"]]
            source_refs = task.get("inputs", [])
            basis_ids = [k for k in {*task.get("dependencies", []), *task.get("reuse", []), *task.get("inputs", [])}
                         if k in self.instance["knowledge"] or k in self.runtime["tasks"]]
        elif action.get("target") in self.instance["knowledge"]:
            proposal = self.instance["knowledge"][action["target"]]
            basis_ids = [k for k in proposal.get("dependencies", []) if k in self.instance["knowledge"]]
            source_refs = [row["name"] for row in proposal.get("source_basis", [])]
        elif role == "goal_audit":
            if action["basis"] != self._goal_basis_key():
                raise ValueError("goal audit inputs changed before acceptance")
            basis_ids = [k["id"] for k in self.instance["knowledge"].values() if knowledge.assess_use(k, self.instance)["valid"]]
        chosen_model = action["model_selection"]
        model = chosen_model["model"] if chosen_model else config["role_models"].get(role, config["model"])
        if self._revision_dispatch_waits(action):
            self._discard_prepared_input(base, execution_id)
            return False
        retry = self._pending_input_overflow_retry(action)
        if retry:
            evidence = {"action_id": action["id"], "request_id": retry["request_id"],
                "profile_ref": deepcopy(action.get("profile_ref")),
                "prompt_bytes": fitted["actual_bytes"],
                "limit_bytes": profile["input"]["max_input_bytes"],
                "prompt_sha256": fitted["manifest"]["prompt"]["sha256"]}
            question_disposition = self._resolve_input_overflow_question(
                retry["question_id"], execution_id=execution_id,
                kind="input_overflow_retry_resolved", evidence=evidence)
            self._set_input_overflow_retry_state(action, "resolved",
                resolved_execution_id=execution_id, question_disposition=question_disposition)
            self.runtime.setdefault("history", []).append({"kind": "input_overflow_retry_resolved",
                "activity_id": activity_id, "execution_id": execution_id,
                "question_disposition": question_disposition, "resolved_at": now(), **deepcopy(evidence)})
        execution = {"id": execution_id, "role": role, "action": action,
                     "budget_kind": pool, "status": "queued", "created_at": now(), "input_snapshot": self.head,
                     "input_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_bundle": input_bundle,
                     "model": chosen_model["model"] if chosen_model else config["role_models"].get(role, config["model"]), "effort": config["effort"],
                     "model_selection": chosen_model,
                     "engine_sha256": ENGINE_SHA256, "grant_id": authority["grant_id"], "observed_at": context["observed_at"],
                     "goal_revision": self._governance().get("goal_revision", 1), "policy_revision": self._governance().get("policy_revision", 1),
                     "validity_basis": knowledge.capture_basis(self.instance, self.runtime, basis_ids),
                     "decision_basis": capture_decision_basis(self.instance, self.runtime, self._decision_references(action)),
                     "source_basis": capture_sources(self.instance, source_refs),
                     "input_preparation_milliseconds": int((time.monotonic() - preparation_started) * 1000),
                     "input_manifest": deepcopy(fitted["manifest"]),
                     "input_reductions": fitted["reductions"],
                     "input_metrics": prompt_metrics(prompt, fitted["context"], schema, self._documents[role])}
        if action.get("target") in self.runtime["tasks"]:
            execution["contract_sha256"] = planning.contract_hash(self.runtime["tasks"][action["target"]])
            if self.runtime["tasks"][action["target"]].get("academic_requirement_id"):
                execution["academic_requirements_sha256"] = academic.current_requirements(self.instance)["sha256"]
        if role == "research_plan":
            solution_basis = self._solution_basis()
            if solution_basis is not None:
                execution["input_solution_basis"] = solution_basis
        if action.get("delegation_application_id"):
            execution["delegation_input_sha256"] = context["delegation_case"]["input_sha256"]
        if action.get("kind_definition_id"):
            execution["input_basis"] = {"kind_definition": {"id": action["kind_definition_id"],
                                                           "sha256": action["kind_definition_sha256"]}}
        self._bind_governance_input(action, execution, fitted["context"])
        self.runtime["executions"][execution_id].update(execution)
        execution = self.runtime["executions"][execution_id]
        tracker = ObservationTracker(execution_id, workspace, observation_config)
        if observation_config['observation_rules']:
            execution['observation_rules'] = deepcopy(observation_config['observation_rules'])
        admitted = self._provider_admit(action, execution_id, pool, model, profile=profile, execution=execution)
        if not admitted:
            self._transport.close(binding, reason="execution was not admitted")
            self._transport_bindings.pop(execution_id, None)
            execution_lifecycle.transition_execution(execution, "ended", at=now(), outcome="start_failed",
                reason="provider admission deferred", disposition=deepcopy(action.get("dispatch_wait")))
            self._continue_prepared_action(execution)
            for queued in self.runtime['queue']:
                if queued.get('id') == action['id']:
                    queued['dispatch_wait'] = deepcopy(action['dispatch_wait'])
            activities.wait_for(self.runtime, activity_id, reason="provider admission deferred",
                condition=deepcopy(action["dispatch_wait"]), next_owner=action["dispatch_wait"]["next_owner"], at=now())
            self._save(self._input_artifacts(input_bundle, role, prompt, schema, fitted, workspace))
            return False
        if execution["status"] == "queued":
            execution_lifecycle.transition_execution(execution, "starting", at=now())
        self.runtime["active_execution"] = execution_id
        self._live_execution_ids.add(execution_id)
        self.runtime["status"] = "running"
        if role in {"research_work", "supplemental_research"} and not action.get("review_cycle_id"):
            self.runtime["tasks"][action["target"]]["status"] = "active"
        execution["control_transport"] = {key: value for key, value in binding.items() if key != "capability"}
        if role == "identity_review" and action.get("review_cycle_id"):
            self._record_review_input(action, execution_id)
            self._record_review_prompt(execution_id, prompt, artifact_ref=f"runtime/artifacts/{input_bundle}/input.txt")
        self._save(self._input_artifacts(input_bundle, role, prompt, schema, fitted, workspace))
        execution = self.runtime["executions"][execution_id]
        execution["input_published_at"] = now()
        self._trackers[execution_id] = tracker
        stop_started = None
        before_resume = True
        # Research ends by submission or an effective stop/authority condition.
        # Only operations-budget AI has a per-call execution deadline.
        call_deadline = None if pool == "work" else time.monotonic() + config["call_timeout_seconds"]
        def started(identity):
            self._provider_slots().started(execution_id, identity)
            window = execution_window.publish(workspace, execution_id, call_deadline, config, pool,
                deadline_source="none" if call_deadline is None else "operational_call")
            current = self.runtime["executions"][execution_id]
            execution_lifecycle.transition_execution(current, "running", at=now())
            current.update(process=json_safe(identity), started_at=now(), execution_window=window)
            self._save()
        def should_stop():
            nonlocal stop_started, before_resume
            first_check = before_resume
            before_resume = False
            self._controls()
            if self._check_conversations(): self._save()
            current = self.runtime["executions"][execution_id]
            if role == "operational_review" and action.get("live") and self._obsolete_action_reason(action):
                current["stop_requested"] = "observation_target_ended"
            allowed = governance.authorize(self.instance, action, runtime=self.runtime)["allowed"]
            changed = (current["goal_revision"] != self._governance().get("goal_revision", 1) or
                       current["policy_revision"] != self._governance().get("policy_revision", 1))
            premise_changes = decision_basis_changes(current.get("decision_basis"), self.instance, self.runtime)
            premise_changes.extend(self._execution_requirement_changes(action, evaluation_context=self._evaluation_context()))
            if role == "goal_audit" and action.get("basis") != self._goal_basis_key():
                premise_changes.append({"field": "goal_audit_basis", "reason": "complete goal judgment basis changed"})
            if premise_changes:
                changed = True
            if not sources_current(current.get("source_basis", []), self.instance): changed = True
            if current.get("academic_requirements_sha256") and current["academic_requirements_sha256"] != academic.current_requirements(self.instance).get("sha256"):
                changed = True
            if current.get("contract_sha256") and action.get("target") in self.runtime["tasks"]:
                target_task = self.runtime["tasks"][action["target"]]
                changed = changed or planning.contract_hash(target_task) != current["contract_sha256"] or target_task["status"] == "closed"
            if changed:
                current["currentness_changes"] = premise_changes or [{"field": "action_contract_or_authority", "reason": "execution input changed"}]
            requested = (current.get("submission_intent") or self.runtime["status"] in {"paused", "closed", "completed"} or self.runtime.get("stop_requested")
                         or current.get("stop_requested") or not allowed or changed
                         or (call_deadline is not None and time.monotonic() >= call_deadline))
            if not requested:
                execution_window.request_finish(workspace, call_deadline, config, pool)
                return False
            reason = current.get("stop_requested") or ("authority_changed" if not allowed or changed else
                "submission_intent" if current.get("submission_intent") else "user_or_deadline_stop")
            # CodexModelRunner first checks this while its Job is suspended.
            # There is no model work to checkpoint before that first resume.
            immediate = True  # Instruction boundaries cannot enforce checkpoint-only research after stop.
            if stop_started is None:
                stop_started = time.monotonic()
                current["stop_reason"] = reason
                current["stop_observed_at"] = now()
                tracker.set_execution_status("stopping")
                execution_lifecycle.transition_execution(current, "stopping", at=now(),
                    reason=str(reason), stop_phase="terminating")
                self._save()
                request_checkpoint(workspace / ".control", str(reason), immediate=immediate,
                    deadline=(datetime.now(timezone.utc)+timedelta(seconds=0 if immediate else config["checkpoint_grace_seconds"])).isoformat())
            return immediate or time.monotonic()-stop_started >= config["checkpoint_grace_seconds"]
        arguments = dict(prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=base/"evidence",
                         model=execution["model"], effort=execution["effort"],
                         execution_id=execution_id, profile=profile,
                         control_binding=binding,
                         input_seal=deepcopy(fitted["manifest"]["prompt"]),
                         timeout_seconds=None if call_deadline is None else max(.1, call_deadline-time.monotonic()),
                         should_stop=should_stop, on_started=started)
        self._runner_tools(arguments)
        params = inspect.signature(self.runner.run).parameters
        if "on_observation" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
            arguments["on_observation"] = lambda event: self._observe_running(execution_id, tracker, event)
        result = yield arguments
        tracker.set_execution_status("stopping")
        self._drain_review_observations(execution_id, tracker)
        self._transport.pump(self._publish_control_request)
        self._transport.close(binding, reason="execution process ended")
        tracker.set_execution_status("ended")
        self._trackers.pop(execution_id, None)
        self._check_installation(force=True)
        self._live_execution_ids.discard(execution_id)
        provider_state = self._provider_outcome(execution_id, execution["model"], result)
        observation = execution_profiles.execution_observation(result)
        if observation is not None:
            self.runtime["executions"][execution_id]["provider_observation"] = observation
        if result.get("capability_evidence"):
            evidence = result["capability_evidence"]
            if evidence["execution_profile_ref"] != execution_profiles.profile_ref(profile):
                raise ValueError("capability evidence differs from the attempted profile")
            self.instance.setdefault("capability_evidence", {})[evidence["id"]] = deepcopy(evidence)
        if not self._release_call_slot(execution_id):
            pending = self.runtime["executions"][execution_id]
            execution_lifecycle.transition_execution(pending, "stopping", at=now(), stop_phase="terminating",
                reason="Local Job termination remains unconfirmed")
            pending["error"] = "Local Job termination is unconfirmed; slot and output remain held for recovery."
            result_ref = f"runtime/artifacts/{new_id('BA')}/result.json"
            pending['result_ref'] = result_ref
            for key in ('error_kind', 'failure'):
                if key in result:
                    pending[key] = deepcopy(result[key])
            self._publish_provider_result({result_ref: lossless_json(result)})
            return True
        result = self._collect_submitted_result(self.runtime["executions"][execution_id], result, context, schema, workspace)
        result = json_safe(result)
        if result.get('status') == 'failed':
            result.setdefault('error_kind', 'execution_failure')
        stopped_execution = self.runtime["executions"][execution_id]
        if result.get("error_kind") == "model_policy":
            self._pause_for_model_policy(execution_id, execution["model"], result)
        if result["status"] == "completed" and (
                stopped_execution.get("stop_requested") or stopped_execution.get("after_stop")
                or self.runtime["status"] == "paused"):
            # The stop request already revoked general authority; keep the late output only as preserved evidence.
            result = {**result, "status": "stopped",
                      "error": "final output was collected after " + str(stopped_execution.get("stop_requested")
                          or "a pause or operational stop request") + "; preserved without acceptance"}
        bundle = new_id("BA")
        files = (self._sealed_submission_files(self.runtime["executions"][execution_id])
                 or collect_outputs(workspace, max_bytes=config["max_artifact_bytes"]))
        control_files = collect_outputs(workspace / ".control", max_bytes=config["max_artifact_bytes"])
        artifacts = {f"runtime/artifacts/{bundle}/result.json": lossless_json(result),
                      f"runtime/artifacts/{bundle}/output-manifest.json": canonical_json(files["manifest"]),
                      f"runtime/artifacts/{bundle}/omitted.json": canonical_json(files["omitted"]),
                      f"runtime/artifacts/{bundle}/control-manifest.json": canonical_json(control_files["manifest"]),
                      f"runtime/artifacts/{bundle}/control-omitted.json": canonical_json(control_files["omitted"])}
        output_files = []
        for path, raw in files["files"].items():
            ref = f"runtime/artifacts/{bundle}/files/{path}"
            artifacts[ref] = raw
            output_files.append({"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        for path, raw in control_files["files"].items():
            ref = f"runtime/artifacts/{bundle}/control/{path}"
            artifacts[ref] = raw
        if result.get("output") is not None:
            artifacts[f"runtime/artifacts/{bundle}/output.json"] = lossless_json(result["output"])
        checkpoint = json_safe(recovered_checkpoint(workspace))
        evidence = collect_outputs(base / "evidence", max_bytes=config["max_artifact_bytes"])
        checkpoint["observation_sources"] = []
        for path, raw in evidence["files"].items():
            reference = f"runtime/artifacts/{bundle}/provider-evidence/{path}"
            artifacts[reference] = raw
            checkpoint["observation_sources"].append({"artifact_ref": reference,
                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "path": path})
        checkpoint["observation_evidence_complete"] = evidence["complete"]
        checkpoint["observation_evidence_omitted"] = deepcopy(evidence["omitted"])
        observed = self.runtime.get("checkpoints", {}).get(execution_id)
        if checkpoint["kind"] != "worker_checkpoint" and isinstance(observed, dict) and observed.get("kind") == "worker_checkpoint":
            # An unreadable final checkpoint file never replaces the last valid checkpoint observed during execution.
            checkpoint = {**observed, "final_observation": checkpoint}
        from .observations import bind_checkpoint_artifact
        checkpoint = bind_checkpoint_artifact(checkpoint, output_files, observed)
        self.runtime.setdefault("checkpoints", {})[execution_id] = checkpoint
        artifacts[f"runtime/artifacts/{bundle}/checkpoint-recovery.json"] = lossless_json(checkpoint)
        execution = self.runtime["executions"][execution_id]
        if execution["status"] != "stopping":
            execution_lifecycle.transition_execution(execution, "stopping", at=now(), stop_phase="terminating")
        obsolete = self._obsolete_action_reason(action, execution_id=execution_id)
        accepting = ((result["status"] == "completed" or result.get("error_kind") == "output_validation")
            and self.runtime["status"] not in {"closed", "completed"} and not obsolete
            and not execution.get("currentness_changes"))
        if not accepting:
            cancelled = result["status"] == "stopped" and (self.runtime["status"] in {"paused", "closed"}
                or self.runtime.get("stop_requested"))
            execution_lifecycle.transition_execution(execution, "ended", at=now(), outcome="cancelled" if cancelled else "execution_incomplete",
                disposition={"kind": "preserved_for_followup", "artifact_ref": f"runtime/artifacts/{bundle}/result.json"})
            if cancelled:
                self._continue_prepared_action(execution)
        execution.update(usage=result.get("usage", {}), artifact_bundle=bundle,
                          output_files=output_files, outputs_complete=files["complete"],
                          result_ref=f"runtime/artifacts/{bundle}/result.json", error=result.get("error"))
        for key in ("usage_segments", "model_usage_reported", "usage_scope", "reported_models", "error_kind", "failure"):
            if key in result:
                execution[key] = deepcopy(result[key])
        self.runtime["active_execution"] = None
        # Raw evidence is durable before any domain bundle is attempted.
        self._save(artifacts)
        artifacts = {}
        obsolete = self._obsolete_action_reason(action, execution_id=execution_id)
        if self.runtime["status"] == "closed":
            self.runtime["executions"][execution_id]["result_disposition"] = {"kind": "preserved_after_close"}
            self.runtime["queue"] = []
        elif self.runtime["status"] == "completed":
            self.runtime["executions"][execution_id]["result_disposition"] = {"kind": "preserved_after_goal_completion"}
            self._remove_action(action)
        elif obsolete:
            self.runtime["executions"][execution_id].update(result_disposition={"kind": "preserved_after_target_change"}, preserved_reason=obsolete)
            self._remove_action(action)
            if self.runtime["status"] == "running":
                self.runtime["status"] = "ready"
        elif execution.get("currentness_changes") and self.runtime["status"] != "paused":
            self._refresh_changed_decision(action, execution_id, execution["currentness_changes"])
        elif result.get("error_kind") == "provider_limit":
            self._hold_provider_action(action, execution_id, provider_state, result.get("error"))
        elif result.get("error_kind") == "model_policy":
            self._remove_action(action)
            self.runtime["status"] = "paused"
            self.runtime["questions"].append("A reported model differed from the locked assignment; inspect " + execution_id)
        elif result["status"] == "completed" or result.get("error_kind") == "output_validation":
            try:
                if not files["complete"]:
                    raise ValueError("required execution artifacts could not be preserved")
                self._receive_submission(action, result, execution_id, context, schema, workspace)
            except Exception as error:
                # Never restore an execution-wide copy: earlier bundles may have committed.
                current = self.runtime["executions"][execution_id]
                execution_lifecycle.transition_execution(current, "ended", at=now(), outcome="execution_incomplete",
                    disposition={"kind": "submission_failure"})
                current.update(error=str(error), error_kind="submission_failure")
                self._remove_action(action)
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                    "action": deepcopy(action), "kind": "submission_failure", "reason": str(error),
                    "execution_id": execution_id, "next_owner": "engine"}
                repair_execution.route_failed_action(self, action, execution_id,
                    reason="Resolve the preserved submission or publication failure")
                if self.runtime["status"] not in {"paused", "closed", "completed"}:
                    self.runtime["status"] = "ready"
        else:
            pending_disposition = execution.get("pending_operational_disposition")
            if pending_disposition:
                self._remove_action(action)
                self._complete_operational_disposition(self.runtime["operational_dispositions"][pending_disposition])
            elif self._session_mode() and role == "operational_review" and action.get("live"):
                self._remove_action(action)
                self._failed_live_review(action, "Live operational review did not finish: " + str(result.get("error")))
                if self.runtime["status"] not in {"closed", "paused"}:
                    self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            elif result["status"] == "failed" or (result["status"] == "stopped"
                    and self.runtime["status"] not in {"paused", "closed"}
                    and not self.runtime.get("stop_requested")):
                self._remove_action(action)
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                    "action": action, "kind": "execution_failure", "reason": result.get("error"),
                    "failure_kind": result.get("error_kind", "execution_failure"),
                    "execution_id": execution_id, "input_snapshot": execution["input_snapshot"]}
                returned = (result['status'] == 'stopped' and role == 'supplemental_research'
                            and action.get('research_request_id')
                            and self._finish_failed_investigation(action, execution_id, result.get('error')))
                if not returned:
                    repair_execution.route_failed_action(self, action, execution_id, front=not self._session_mode(),
                        reason="Diagnose the preserved failure before selecting recovery")
                    if action.get("recovery_attempt", 0) >= 1:
                        self._finish_failed_investigation(action, execution_id, result.get("error"))
                if self.runtime["status"] not in {"paused", "closed"}:
                    self.runtime["status"] = "ready" if self.runtime["queue"] else "waiting"
            elif self.runtime["status"] not in {"closed", "paused"}:
                self.runtime["status"] = "paused"
        self._settle_activity(execution_id)
        self._publish_provider_result(artifacts)
        self._controls()
        if self.runtime["status"] not in {"paused", "closed", "completed"}:
            self._refresh_readiness()
            self._save()
        return self.runtime["status"] in {"ready", "running"}

    def _enqueue(self, role: str, target: str | None = None, *, front=False, **extra: Any) -> None:
        action = {"role": role, **extra}
        if target is not None:
            action["target"] = target
        self._bind_revision_action(action)
        compare_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis", "transition_id",
                        "assessment_targets", "observation_rule_targets", "review_basis_key", "live", "grant_id", "profile_ref",
                         "cleanup_execution_ids", "delegation_application_id", "initial_submission_diagnosis")
        live_actions = {e.get("action", {}).get("id") for e in self.runtime["executions"].values() if e["status"] != "ended"}
        for queued in self.runtime["queue"]:
            if queued.get("id") not in live_actions and all(queued.get(k) == action.get(k) for k in compare_keys):
                # A request without revision targets must outlive the retirement of merged targets.
                if not queued.get("revision_targets") or not action.get("revision_targets"):
                    queued["unbound_request"] = True
                if action.get("reason"):
                    reasons = queued.setdefault("reasons", [queued["reason"]] if queued.get("reason") else [])
                    if action["reason"] not in reasons:
                        reasons.append(action["reason"])
                    queued["reason"] = "\n".join(reasons)
                if action.get("requested_by"):
                    queued["requested_by_refs"] = list(dict.fromkeys([
                        *queued.get("requested_by_refs", [queued["requested_by"]] if queued.get("requested_by") else []),
                        action["requested_by"]]))
                    queued["requested_by"] = action["requested_by"]
                if action.get("event_refs"):
                    queued["event_refs"] = list(dict.fromkeys([*queued.get("event_refs", []), *action["event_refs"]]))
                for key in ("obligation_ids", "observation_refs", "receipt_refs", "evidence_refs"):
                    if action.get(key):
                        queued[key] = list(dict.fromkeys([*queued.get(key, []), *action[key]]))
                if action.get("observation"):
                    queued["observation"] = deepcopy(action["observation"])
                if action.get("revision_parent_ids"):
                    queued["revision_parent_ids"] = list(dict.fromkeys([*queued.get("revision_parent_ids", []), *action["revision_parent_ids"]]))
                for identifier, basis in action.get("revision_targets", {}).items():
                    old = queued.setdefault("revision_targets", {}).get(identifier)
                    if old and old != basis:
                        queued.setdefault("superseded_revision_bases", []).append({identifier: deepcopy(old)})
                    merged = {**deepcopy(basis), "required": bool(basis.get("required") or (old or {}).get("required"))}
                    merged["source_refs"] = list(dict.fromkeys([*(old or {}).get("source_refs", []), *basis.get("source_refs", [])]))
                    queued["revision_targets"][identifier] = merged
                if action.get("id") and action["id"] != queued.get("id"):
                    queued["merged_action_ids"] = list(dict.fromkeys([*queued.get("merged_action_ids", []), action["id"]]))
                self._cancel_selected_revision_targets(queued)
                if front:
                    self.runtime["queue"].remove(queued)
                    self.runtime["queue"].insert(0, queued)
                return
        action.setdefault("id", new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        if front:
            self.runtime["queue"].insert(0, action)
        else:
            self.runtime["queue"].append(action)
        self._cancel_selected_revision_targets(action)

    def _apply_extensions(self, action: dict, execution_id: str) -> None:
        extension = self.runtime["executions"][execution_id].get("extensions", {})
        for definition in extension.get("kind_definitions", []):
            self._propose_kind(definition, execution_id)
        if extension.get("task_dispositions"):
            if action["role"] not in {"research_preparation", "research_plan"}:
                raise ValueError("only preparation and planning may withdraw AI-prepared tasks")
            execution = self.runtime["executions"][execution_id]
            _, _, input_runtime = self.store.load(execution["input_snapshot"])
            self.instance, self.runtime = apply_task_dispositions(self.instance, self.runtime,
                extension["task_dispositions"], execution_id=execution_id, input_tasks=input_runtime["tasks"])
        self._apply_queue_plan(action, execution_id)
        self._apply_academic_resolutions(action, execution_id, extension.get("academic_resolutions", []))
        for relation in extension.get("relations", []):
            self.instance, _ = knowledge_io.import_relation(self.instance, relation, source_ref=execution_id, actor_ref=execution_id)
        if extension.get("observation_rules"):
            from .observations import task_rules_from_execution
            rules = task_rules_from_execution(extension["observation_rules"], execution_id)
            if action.get("target") not in self.runtime["tasks"]:
                raise ValueError("persisted observation rules require a task target; live rules belong in observation-rules.json")
            self.runtime.setdefault("task_observation_rules", {})[action["target"]] = deepcopy(rules)
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
                question = questions.link(self.runtime, execution_id=execution_id,
                    field="extensions/external_requests/" + str(index) + "/purpose", owner="user",
                    targets=[action.get("target") or self.instance["id"]], reason="External action requires a user grant")
                question["question_kind"] = "grant"
                continue
            integration_id = self.runtime["executions"][execution_id].get("integration_id", action["id"])
            logical_ref = integration_id + ":external:" + str(request.get("id", index))
            operation_id = "EO-" + hashlib.sha256(logical_ref.encode()).hexdigest()[:24]
            previous_binding = getattr(self, "_external_preparation_binding", None)
            self._external_preparation_binding = ({"task_id": task["id"], "requirement_id": task["academic_requirement_id"],
                "requirements_sha256": task["requirements_sha256"], "solution_basis": deepcopy(task["solution_basis"]),
                "effect_id": academic_effect} if academic_effect else None)
            try:
                self._external_control({"operation": "prepare", "request": request["request"], "grant_id": request["grant_id"],
                                        "id": operation_id}, logical_ref)
            finally:
                self._external_preparation_binding = previous_binding
            entry = self.runtime["external_operations"][operation_id]
            entry["producer_executions"] = list(dict.fromkeys([*entry.get("producer_executions", []), execution_id]))
            if academic_effect:
                entry["academic_binding"] = {"task_id": task["id"], "requirement_id": task["academic_requirement_id"],
                    "requirements_sha256": task["requirements_sha256"], "solution_basis": deepcopy(task["solution_basis"]),
                    "effect_id": academic_effect}
            pending_external = [a for a in self.runtime["queue"] if a["role"] == "external_action" and a.get("target") == operation_id]
            self.runtime["queue"] = pending_external + [a for a in self.runtime["queue"] if a not in pending_external]
        insights = extension.get("research_insights", [])
        private_cycle = action.get("review_cycle_id")
        if action["role"] == "operational_review":
            private_cycle = self.runtime["executions"].get(action.get("target"), {}).get("action", {}).get("review_cycle_id")
        if private_cycle:
            cycle_id = private_cycle
            self.runtime.setdefault("private_insights", {}).setdefault(cycle_id, []).extend(
                {"source_execution": execution_id, **insight} for insight in insights)
            cycle = self.runtime["review_cycles"][cycle_id]
            if cycle["status"] not in {"completed", "unresolved"}:
                return
            insights = self.runtime["private_insights"].pop(cycle_id, [])
        imported_insights = []
        for insight in insights:
            producer = insight.get("source_execution", execution_id)
            try:
                knowledge_io.validate_insight(self.instance, self.runtime, insight)
            except (ValueError, TypeError) as error:
                if producer == execution_id:
                    raise
                # A malformed item held by an older implementation belongs to
                # its original author; it cannot reject another reviewer's work.
                self.runtime["history"].append({"kind": "incidental_insight_not_published", "source_execution": producer,
                    "insight": deepcopy(insight), "reason": str(error)})
                self.runtime["questions"].append("Correct the preserved incidental insight from " + producer + ": " + str(error))
                continue
            source_basis, changed = [], []
            refs = insight.get("evidence_ids", [])
            if refs:
                try:
                    origin = self.runtime["executions"][producer]["input_snapshot"]
                    _, origin_instance, origin_runtime = self.store.load(origin)
                    basis = knowledge.capture_basis(origin_instance, origin_runtime,
                        sorted(set(refs) & (set(origin_instance["knowledge"]) | set(origin_runtime["tasks"]))))
                    changed = knowledge.validate_basis(basis, self.instance, self.runtime)["reasons"]
                    source_basis = capture_sources(origin_instance, refs)
                    if not sources_current(source_basis, self.instance):
                        changed.append("required_source_changed")
                except (ValueError, KeyError, OSError, GitStateStoreError) as error:
                    changed.append("origin input could not be established: " + str(error))
            candidate = {key: deepcopy(insight[key]) for key in ("kind", "title", "statement", "summary")}
            candidate.update(explanation=insight.get("explanation", insight["statement"]), lean_code="",
                declaration_names=[], dependencies=[ref for ref in insight.get("evidence_ids", []) if ref in self.instance["knowledge"]])
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime,
                candidate, source_ref=producer, actor_ref=producer, plan_nonformal=False)
            imported_insights.append(kid)
            self.instance["knowledge"][kid].update(source_basis=source_basis, created_at=now())
            if changed:
                self.instance["knowledge"][kid].update(use_suspended=True, use_suspensions=[{
                    "kind": "dependency", "root_ids": list(refs), "reason": "Incidental evidence changed before publication: " + "; ".join(changed)}])
        if imported_insights:
            self._enqueue("research_plan", reason="Incidental research knowledge is now available",
                receipt_refs=[execution_id], evidence_refs=imported_insights)

    def _import_research_records(self, action: dict, output: dict, execution_id: str) -> list[str]:
        """Create domain-owned records from one producer-declared bundle."""
        entries = self.runtime["executions"][execution_id].get("extensions", {}).get("knowledge_metadata", [])
        metadata = {entry["title"]: entry for entry in entries}
        candidates = output.get("knowledge", [])
        titles = [item["title"] for item in candidates]
        if len(set(titles)) != len(titles):
            raise ValueError("knowledge titles must be unique within an integration bundle")
        if len(metadata) != len(entries) or set(metadata) - set(titles):
            raise ValueError("knowledge metadata must identify a member of the same bundle")
        identifiers = {item["title"]: item.get("id") or new_id("KN") for item in candidates}
        pending = []
        for item in candidates:
            extra = metadata.get(item["title"], {})
            if set(extra) - {"title", "relation_claim", "confirmed_scope", "epistemic_status", "selection_relevance", "uncertainty_assessment"}:
                raise ValueError("unknown knowledge metadata")
            candidate = {**deepcopy(item), **deepcopy(extra), "id": identifiers[item["title"]]}
            candidate["dependencies"] = [identifiers.get(ref, ref) for ref in candidate.get("dependencies", [])]
            if candidate.get("relation_claim"):
                for endpoint in ("source", "target"):
                    ref = candidate["relation_claim"][endpoint]
                    candidate["relation_claim"][endpoint] = identifiers.get(ref, ref)
            pending.append(candidate)
        while pending:
            ready = next((item for item in pending
                if set(item["dependencies"]) <= self.instance["knowledge"].keys()
                and (not item.get("relation_claim") or all(item["relation_claim"][key] in self.instance["knowledge"]
                                                         for key in ("source", "target")))), None)
            if ready is None:
                raise ValueError("knowledge dependencies are missing or cyclic within the declared bundle")
            self.instance, self.runtime, kid = knowledge_io.import_candidate(
                self.instance, self.runtime, ready, source_ref=execution_id, actor_ref=execution_id, plan_nonformal=False)
            self.instance["knowledge"][kid].update(task_id=action.get("target"), created_at=now(),
                source_basis=deepcopy(self.runtime["executions"][execution_id].get("source_basis", [])))
            pending.remove(ready)
        for relation in output.get("relations", []):
            row = {**relation, **{key: identifiers.get(relation[key], relation[key]) for key in ("source", "target")}}
            self.instance, _ = knowledge_io.import_relation(self.instance, row,
                                                            source_ref=execution_id, actor_ref=execution_id)
        return list(identifiers.values())

    def _apply(self, action: dict, output: dict, execution_id: str, *, owns_response: bool = True,
               question_source_ref=None) -> None:
        role, target = action["role"], action.get("target")
        if owns_response and role != "intent_interpretation":
            self._record_output_questions(action, output, execution_id, source_ref=question_source_ref)
        if role == "supplemental_research" and action.get("review_cycle_id"):
            self._apply_review_research(action, output, execution_id)
        elif role == "research_preparation":
            if model_policy.preparation_only(action):
                self._finish_assessment_preparation(action, execution_id)
                return
            self.runtime["cycles"] += 1
            titles = {}
            authoring_environment = None
            if any(proposal['work_class'] == 'formal' for proposal in output['candidates']):
                _, authoring_instance, _ = self.store.load(self.runtime['executions'][execution_id]['input_snapshot'])
                authoring_environment = authoring_instance.get('active_trust_environment')
                if authoring_environment is None:
                    raise ValueError('formal task requires the trust environment supplied to its author')
            for proposal in output["candidates"]:
                tid = proposal["revises_task_id"] or new_id("TK")
                old = self.runtime["tasks"].get(tid)
                if proposal["revises_task_id"] and (old is None or old["status"] in {"completed", "closed", "active"}):
                    raise ValueError("revision must identify an existing unfinished task")
                if old and old.get("academic_requirement_id"):
                    raise ValueError("user-defined academic contracts require an academic_requirements decision")
                contract = task_candidate_record(proposal, task_id=tid, previous=old,
                    trust_environment_id=authoring_environment)
                contract.pop("revises_task_id", None)
                assessment = self.runtime["executions"][execution_id].get("model_decisions", {}).get(proposal["title"])
                if assessment is not None:
                    contract["model_assessment"] = deepcopy(assessment)
                if old:
                    # This is a complete replacement contract. Previous obligations
                    # remain in revision_history, not in the new completion criteria.
                    self.runtime.get("task_observation_rules", {}).pop(tid, None)
                self.runtime["tasks"][tid] = {**contract,
                                              "status": "planned", "producer_execution": execution_id,
                                              "results": old.get("results", []) if old else [], "reviews": [],
                                              "occurrence_condition": {"op": "always"},
                                              "initial_observation_rules": deepcopy(old.get("initial_observation_rules", [])) if old else [],
                                              "revision_history": [*old.get("revision_history", []),
                                                  {k: v for k, v in old.items() if k != "revision_history"}] if old else []}
                if old and old.get("revision_request_action_id"):
                    self.runtime["tasks"][tid]["revision_request_action_id"] = old["revision_request_action_id"]
                if proposal["title"] in titles:
                    raise ValueError("task titles must be unique within a preparation result")
                titles[proposal["title"]] = tid
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
                dependencies = task_contracts.prepared_dependencies(self.runtime["tasks"][tid], specification, titles)
                task_conditions = [{"op": "task_disposition_is", "task_id": d, "value": "completed"}
                                   for d in dependencies if d in self.runtime["tasks"]]
                if task_conditions:
                    condition = {"op": "all", "args": [condition, *task_conditions]}
                evaluated = planning.evaluate_condition(condition, self.instance, self.runtime, evaluation_context=self._evaluation_context())
                if evaluated["state"] == "evaluation_error":
                    raise ValueError("invalid task occurrence condition: " + "; ".join(evaluated["errors"]))
                self.runtime["tasks"][tid].update(occurrence_condition=condition, dependencies=dependencies,
                    knowledge_revision_targets=deepcopy(specification.get("knowledge_revision_targets", [])))
                if "observation_rules" in specification:
                    self.runtime["tasks"][tid]["initial_observation_rules"] = deepcopy(validate_rules(specification["observation_rules"]))
            cycles = revisions.dependency_cycles(self.runtime["tasks"])
            if any(set(cycle) & set(titles.values()) for cycle in cycles):
                raise ValueError("explicit task dependency cycle: " + str(cycles))
            available = set(self._available_inputs())
            for tid in titles.values():
                task = self.runtime["tasks"][tid]
                task["inputs"] = [titles.get(ref, ref) for ref in task["inputs"]]
                task["reuse"] = [titles.get(ref, ref) for ref in task["reuse"]]
                task["dependencies"] = [titles.get(ref, ref) for ref in task["dependencies"]]
                unknown = {ref for ref in (set(task["inputs"]) | set(task["reuse"])) - available if not ref.startswith("source:")}
                if unknown:
                    raise ValueError("task inputs must copy available source refs; unknown: " + ", ".join(sorted(unknown)))
                basis = {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                         "goal_revision": self._governance().get("goal_revision", 1), "policy_revision": self._governance().get("policy_revision", 1)}
                review_key = planning.review_basis_key(task, self.instance, self.runtime)
                live_actions = {row.get("action", {}).get("id") for row in self.runtime["executions"].values() if row["status"] != "ended"}
                for pending in list(self.runtime["queue"]):
                    if (pending["role"] == "task_contract_review" and pending.get("target") == tid
                            and pending.get("id") not in live_actions
                            and (pending.get("contract_basis") != basis or pending.get("review_basis_key") != review_key)):
                        self._remove_action(pending)
                        self.runtime["history"].append({"kind": "obsolete_contract_review_request", "action": deepcopy(pending),
                                                        "replaced_by_revision": task["revision"]})
                self._enqueue("task_contract_review", tid, contract_basis=basis, review_basis_key=review_key)
                self._resolve_task_observation_waits(tid, execution_id)
            # A plan decides over ready and assessing tasks. With neither, and a contract review
            # still pending, that review's approval event or returned revision brings the next decision.
            decidable = bool(planning.ready_task_ids(self.runtime, self.instance, evaluation_context=self._evaluation_context())) or any(
                task["status"] == "waiting" and task.get("results") for task in self.runtime["tasks"].values())
            # Empty preparation already opens its required plan when the actual
            # receipt is recorded by revisions.record_execution_outcome.
            if output["candidates"] and (decidable or not any(a["role"] == "task_contract_review" for a in self.runtime["queue"])):
                self._enqueue("research_plan")
            definition = self.instance.get("kind_definitions", {}).get(action.get("kind_definition_id"))
            if definition and definition["status"] == "candidate":
                self._enqueue("maintenance", definition["id"], kind_definition_id=definition["id"],
                    kind_definition_sha256=integration.digest(definition),
                    reason="Independently reconsider the unresolved kind using the newly prepared evidence")
        elif role == "task_contract_review":
            task = self.runtime["tasks"][target]
            if task.get("producer_execution") == execution_id:
                raise ValueError("contract author cannot review its own contract")
            basis = action.get("contract_basis", {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                "goal_revision": self._governance().get("goal_revision", 1), "policy_revision": self._governance().get("policy_revision", 1)})
            if basis["contract_sha256"] != planning.contract_hash(task):
                raise ValueError("contract changed while being reviewed")
            review = planning.seal_contract_review(task, output, self.instance, self.runtime, execution_id=execution_id)
            task["reviews"].append(review)
            decision = review["decision"]
            task["status"] = "planned" if decision == "approved" else "waiting"
            if decision != "approved":
                task["revision_requested"] = {"execution_id": execution_id, "item_reviews": deepcopy(output["item_reviews"])}
                if task.get("academic_requirement_id"):
                    self._ensure_model_assessments()
                    return
                # The unapproved contract's defects and open questions go back to preparation.
                self._enqueue("research_preparation", target,
                              reason="Task contract review returned " + decision + "; revise the contract from its findings or preserve the obligation with the open questions",
                              contract_review_execution=execution_id)
        elif role == "research_plan":
            self._apply_plan(output, execution_id)
        elif role in {"research_work", "supplemental_research"}:
            if owns_response:
                if not output["report"].strip():
                    raise ValueError("work must report its actual scope, outcome and remaining work")
                task = self.runtime["tasks"][target]
                task["results"].append({"execution_id": execution_id,
                    **{key: deepcopy(value) for key, value in output.items()
                       if key not in {"knowledge", "relations", "integration_bundles"}},
                    "output_files": deepcopy(self.runtime["executions"][execution_id].get("output_files", []))})
                task["status"] = "waiting"
                task["remaining_work"] = deepcopy(output["remaining_work"])
            imported = self._import_research_records(action, output, execution_id)
            if owns_response or imported or output.get('relations'):
                self._enqueue("research_plan", reason="Assess accepted research report and knowledge",
                              receipt_refs=[execution_id], evidence_refs=imported)
        elif role == "identity_review" and action.get("review_cycle_id"):
            self._apply_identity_review(action, output, execution_id)
            cycle = self.runtime["review_cycles"][action["review_cycle_id"]]
            if cycle.get("transition_id") and cycle["status"] in {"completed", "unresolved"}:
                self._enqueue("trust_activate", transition_id=cycle["transition_id"],
                    reason="Consume the sealed staged review through the original authorized trust transition")
        elif role == "identity_review":
            raise ValueError("identity decisions require an independently scoped, sealed review cycle")
        elif role == "goal_audit":
            self._apply_governance_goal_audit(action, output, execution_id)
        elif role == "intent_interpretation" and action.get("delegation_application_id"):
            self._apply_delegation_judgment(action, output, execution_id)
        elif role == "intent_interpretation":
            self._apply_governance_intent(action, output, execution_id)
        elif role == "operational_review":
            self.runtime["executions"][execution_id]["output"] = deepcopy(output)
            self._apply_operational_disposition(action, output["disposition"], execution_id)
        elif role == "maintenance":
            if action.get('initial_submission_diagnosis'):
                repair_execution.apply_initial_diagnosis(self, action, output, execution_id)
            elif action.get("stage") == "impact_review":
                integration.validate_impact_review_response(action["input_basis"]["impact_review"], output)
            elif action.get("kind_definition_id"):
                self._apply_kind_definition_check(action, output["kind_definition_check"], execution_id)
            self.runtime["history"].append({"kind": "maintenance", "execution_id": execution_id, **output})
        else:
            raise ValueError(f"unsupported activity {role}")

    def _cleanup_scope(self, action, instance=None, runtime=None):
        instance, runtime = instance or self.instance, runtime or self.runtime
        requested = action.get("cleanup_execution_ids", [])
        request = next((row["request"] for row in runtime.get("history", [])
            if row.get("kind") == "user_control" and row.get("request", {}).get("id") == action.get("requested_by")), None)
        if (not request or request.get("origin", "user") != "user" or request.get("action") != "request"
                or request.get("config", {}).get("role") != "maintenance"
                or request["config"].get("cleanup_execution_ids") != requested):
            raise ValueError("cleanup has no preserved exact user-approved execution scope")
        authority = governance.authorize(instance, action, runtime=runtime)
        if not authority["allowed"]:
            raise ValueError("maintenance authority no longer permits cleanup")
        return list(requested)

    def _retention_state(self, action):
        head, instance, runtime = self.store.load()
        if head != self.head:
            raise ValueError("cleanup state changed outside the held writer lock")
        records = {row["id"]: deepcopy(row["record"]) for row in self.store.records(head) if row.get("id")}
        reference_keys = {"references", "dependencies", "source_refs", "origin_refs", "input_refs", "inputs", "reuse",
            "artifact_ref", "path", "checkpoint_ref", "source_ref", "formal_result_id", "exposition_id",
            "assessment_id", "evidence_refs", "authority_refs", "basis_refs", "record_refs", "result_ref"}
        def references(value):
            result = []
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in reference_keys:
                        # Task reuse is a list of record references; grant reuse
                        # is a policy enum and does not name an artifact.
                        if key == "reuse" and isinstance(child, str):
                            continue
                        if isinstance(child, str):
                            result.append(child)
                        elif isinstance(child, list):
                            result.extend(item for item in child if isinstance(item, str))
                        elif isinstance(child, dict):
                            result.extend(child[name] for name in ("id", "ref", "artifact_ref", "path") if isinstance(child.get(name), str))
                    if isinstance(child, (dict, list)):
                        result.extend(references(child))
            elif isinstance(value, list):
                for child in value:
                    result.extend(references(child))
            return result
        for record in records.values():
            record["references"] = sorted(set(references(record)))
        for source in instance.get("sources", []):
            if source.get("id") in records:
                for alias in (source.get("name"), "source:" + source.get("name", "")):
                    if alias:
                        records.setdefault(alias, {"references": [source["id"]]})
        # These issued semantic references do not name materialized run files.
        for alias in ("context:goal", "context:policy", "tool:lean", "tool:scholarly"):
            records.setdefault(alias, {"references": []})
        protected = [row["id"] for row in self.store.records(head) if row.get("id") and
                     (row["root"] == "research" or row["family"] in {"tasks", "question_links", "review_cycles"})]
        protected.extend(references(runtime.get("waiting_actions", {})))
        return {"executions": runtime["executions"], "runtime": runtime,
                "approved_execution_ids": self._cleanup_scope(action, instance, runtime),
                "protected_references": protected, "reference_records": records}

    def _maintenance_cleanup(self, action, execution_id):
        """Archive complete local runs, then recheck scope/closure before cleanup.

        Called under the executor's existing instance writer lock, after the
        maintenance response CAS. A local cleanup failure never undoes research.
        """
        scope = self._cleanup_scope(action)
        artifacts, archived, failures = {}, {}, []
        workspace = Path(self.instance["workspace"])
        for identifier in scope:
            execution = self.runtime["executions"].get(identifier, {})
            if execution.get("status") != "ended" or execution.get("capacity", {}).get("local_termination") != "confirmed":
                continue
            try:
                path = retention._run_path(workspace, identifier)
                inventory = retention._inventory(path)
                prefix = f"runtime/artifacts/{new_id('BA')}"
                manifest = []
                for relative, proof in inventory.items():
                    raw = submission._read_stable(submission._safe_path(path, relative))
                    if hashlib.sha256(raw).hexdigest() != proof["sha256"] or len(raw) != proof["bytes"]:
                        raise ValueError("run changed during archival")
                    ref = prefix + "/files/" + relative
                    artifacts[ref] = raw
                    manifest.append({"path": relative, "artifact_ref": ref, **proof})
                termination = canonical_json({"execution_id": identifier, "local_terminated": True,
                    "basis": deepcopy(execution["capacity"]), "remote_termination": "not_established"})
                ref = prefix + "/termination.json"
                artifacts[ref] = termination
                archived[identifier] = (manifest, {"local_terminated": True, "evidence_ref": ref,
                    "sha256": hashlib.sha256(termination).hexdigest(), "bytes": len(termination)})
            except (ValueError, OSError) as error:
                failures.append({"path": "runs/" + identifier, "error": str(error), "status": "degraded", "next_owner": "maintenance"})
        if artifacts:
            self._save(artifacts)
            archive_snapshot = self.head
            for identifier, (manifest, termination) in archived.items():
                execution = self.runtime["executions"][identifier]
                execution["termination"] = {**termination, "snapshot": archive_snapshot}
                execution.setdefault("collection", {})["retention_manifest"] = [
                    {**row, "snapshot": archive_snapshot} for row in manifest]
            self._save()
        state = self._retention_state(action)
        reader = lambda path, snapshot: self.store.read(path, snapshot)
        candidates = retention.cleanup_candidates(workspace, **state, read_artifact=reader)
        result = retention.cleanup(workspace, candidates, current_state=lambda: self._retention_state(action), read_artifact=reader)
        result["failures"].extend(failures)
        if failures:
            result["status"] = "degraded"
        self.runtime["history"].append({"kind": "maintenance_cleanup", "execution_id": execution_id,
            "approved_execution_ids": scope, "candidates": candidates, "result": deepcopy(result)})
        self._save()
        return result

    def _validate_external(self, operation, grant):
        if operation.get("status") == "prepared" and not operation.get("attempts") and not operation.get("transmitted"):
            binding = getattr(self, "_external_preparation_binding", None)
            if binding is not None:
                operation["academic_binding"] = deepcopy(binding)
            if (grant.get("academic_only") or grant.get("requires_academic") or binding is not None) and not operation.get("academic_basis"):
                bound = academic.bind_external_prerequisite(self.instance, self.runtime, self._solution_basis(), operation,
                    resolve_evidence=self._academic_evidence)
                operation.update(bound)
        return super()._validate_external(operation, grant)

    def _propose_kind(self, definition, source_ref):
        self.instance, token = knowledge_io.register_kind_definition(self.instance, definition,
            source_ref=source_ref, actor_ref=source_ref)
        registered = knowledge_io._lookup_definition(self.instance, definition["family"], token)
        self.runtime.setdefault("pending_kind_checks", []).append({"family": definition["family"],
            "token": token, "definition_id": registered["id"], "source_ref": source_ref, "actor_ref": source_ref})
        self._enqueue("maintenance", registered["id"], kind_definition_id=registered["id"],
            kind_definition_sha256=integration.digest(registered),
            reason="Independently check the proposed kind meaning, constraints and authority boundary before activation")

    def _apply_kind_definition_check(self, action, output, execution_id):
        identifier = action["kind_definition_id"]
        definition = self.instance["kind_definitions"][identifier]
        governance.validate_independent_execution(self.runtime, execution_id, [definition["actor_ref"]])
        expected = {"id": identifier, "sha256": action["kind_definition_sha256"]}
        if (output["definition_id"] != identifier or output["definition_sha256"] != expected["sha256"]
                or integration.digest(definition) != expected["sha256"]
                or self.runtime["executions"][execution_id].get("input_basis", {}).get("kind_definition") != expected):
            raise ValueError("kind checker did not read the current exact definition")
        verdict = output["decision"]
        if verdict not in {"approved", "revision_required", "unresolved"}:
            raise ValueError("unknown kind semantic verdict")
        if verdict != "approved" and not output["findings"]:
            raise ValueError("kind rejection or uncertainty requires explicit findings")
        if verdict == "approved":
            self.instance = knowledge_io.check_kind_definition(self.instance, definition["family"], definition["token"],
                check_ref=execution_id, actor_ref=execution_id)
            self.instance = knowledge_io.activate_kind_definition(self.instance, definition["family"], definition["token"],
                approval_ref=execution_id, actor_ref=execution_id)
        self.instance["kind_definitions"][identifier]["check"] = {**deepcopy(output), "execution_id": execution_id}
        self.runtime["pending_kind_checks"] = [row for row in self.runtime.get("pending_kind_checks", [])
                                               if row.get("definition_id") != identifier]
        if verdict == "revision_required":
            self.instance, self.runtime = knowledge_io.withdraw_kind_definition(self.instance, self.runtime,
                definition["family"], definition["token"], reason="; ".join(output["findings"]), actor_ref=execution_id)
        if verdict != "approved":
            self._enqueue("research_preparation", reason="Resolve the independent kind definition findings; revise withdrawn definitions or provide the missing evidence for an unresolved candidate",
                          kind_definition_id=identifier, kind_definition_sha256=integration.digest(self.instance["kind_definitions"][identifier]))

    def _apply_operational_disposition(self, action, proposal, execution_id):
        disposition = operational_dispositions.validate_new_disposition(proposal)
        target = self.runtime["executions"].get(action.get("target"))
        if target is None:
            raise ValueError("operational disposition has no execution target")
        current_refs = {target["id"]}
        current_refs.update(action.get("observation_refs", []))
        current_refs.update(action.get("obligation_ids", []))
        current_refs.update(hold['event_ref'] for hold in revisions.action_repetition_waits(
            self.instance, self.runtime, target.get('action', {})))
        current_refs.update(ref for ref in (target.get("result_ref"),
            self.runtime.get("checkpoints", {}).get(target["id"], {}).get("artifact_ref")) if ref)
        if not operational_dispositions.disposition_is_current(disposition, current_refs):
            raise ValueError("operational disposition cites evidence outside its current input")
        if disposition['kind'] == 'repair' and disposition['repair_target'].startswith('installation:'):
            repair_execution.validate_installation_target(disposition, target, Path(__file__).resolve().parents[2])
        record_id = new_id("OD")
        record = {"id": record_id, "execution_id": execution_id, "target_execution_id": target["id"],
                  "disposition": disposition, "obligation_ids": deepcopy(action.get("obligation_ids", [])),
                  "created_at": now(), "status": "applied"}
        self.runtime.setdefault("operational_dispositions", {})[record_id] = record
        kind = disposition["kind"]
        if kind == "repair":
            record["status"] = "repair_required"
        if kind == "continue":
            if disposition["next_review"]:
                governance.timestamp(disposition["next_review"]["at"])
            target["operational_continuation"] = {"disposition_id": record_id, "next_review": disposition["next_review"]}
            return
        if target["status"] != "ended" and kind in {"repair", "resume", "retry", "task_disposition"}:
            target["stop_requested"] = "operational_" + kind
            target["pending_operational_disposition"] = record_id
            record["status"] = "awaiting_termination"
            return
        if kind == "repair":
            return  # Candidate application is pure; the published judgment owns the later local effect.
        self._complete_operational_disposition(record)

    def _complete_operational_disposition(self, record):
        disposition = record["disposition"]
        target = self.runtime["executions"][record["target_execution_id"]]
        kind = disposition["kind"]
        previous = target.get("action", {})
        if kind == "repair":
            if self.runtime["executions"][record["execution_id"]]["status"] != "ended":
                record["status"] = "repair_required"
                return record
            result = repair_execution.complete_repair(self, record)
            target = self.runtime["executions"][record["target_execution_id"]]
            if result["status"] in {"applied", "repair_verification_failed", "repair_deferred"}:
                if target.get("pending_operational_disposition") == record["id"]:
                    target.pop("pending_operational_disposition")
                followup = result.get("result", {}).get("followup")
                if followup:
                    owner = followup["next_owner"]
                    if owner in {"operational_review", "research_preparation"}:
                        self._enqueue(owner, target["id"] if owner == "operational_review" else previous.get("target"),
                            reason=followup["reason"], operational_disposition_id=record["id"])
                    else:
                        questions.link(self.runtime, execution_id=record["execution_id"], field="repair/" + record["id"],
                            owner=owner, targets=[target["id"]], reason=followup["reason"])
            return result
        if kind in {"resume", "retry"}:
            if record.get('result', {}).get('continuation_action_id'):
                return record
            if target["status"] != "ended":
                raise ValueError("recovery cannot overlap a live predecessor")
            if ((target.get('capacity') or target.get('process'))
                    and target.get('capacity', {}).get('local_termination') != 'confirmed'):
                raise ValueError('recovery requires confirmed local termination')
            if kind == "resume" and disposition["checkpoint_ref"] != self.runtime.get("checkpoints", {}).get(target["id"], {}).get("artifact_ref"):
                raise ValueError("resume must name the preserved current checkpoint")
            if kind == 'resume':
                checkpoint = self.runtime['checkpoints'][target['id']]
                raw = self.store.read(disposition['checkpoint_ref'], self.head)
                if hashlib.sha256(raw).hexdigest() != checkpoint.get('sha256'):
                    raise ValueError('resume checkpoint bytes differ from the preserved checkpoint')
            predecessors, predecessor = set(), target
            while predecessor and predecessor['id'] not in predecessors:
                predecessors.add(predecessor['id'])
                predecessor = self.runtime['executions'].get(predecessor.get('continuation_of'))
            if any(op.get('status') == 'unknown' and predecessors &
                   {*op.get('producer_executions', []), op.get('execution_id')}
                   for op in self.runtime.get('external_operations', {}).values()):
                raise ValueError('recovery requires reconciliation of unknown external effects')
            if target.get('input_bundle'):
                from .context_store import verify_manifest_artifacts
                base = 'runtime/artifacts/' + target['input_bundle']
                manifest = submission.load_json(self.store.read(base + '/manifest.json', self.head))
                if manifest != target['input_manifest'] or verify_manifest_artifacts(
                        manifest, lambda ref: self.store.read(ref, self.head)):
                    raise ValueError('retry requires intact sealed input evidence')
                support = submission.load_json(self.store.read(base + '/support-manifest.json', self.head))
                for entry in support:
                    raw = self.store.read(base + '/' + entry['path'], self.head)
                    if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
                        raise ValueError('retry submission support differs from its sealed input')
            held = self.runtime.get('waiting_actions', {}).get(previous.get('id'))
            retry = activities.continue_activity(self.runtime, target['id'], at=now(),
                reason='operational_' + kind + ':' + record['id'])
            if held and held.get('execution_id') == target['id']:
                retry.update(deepcopy(held['action']), continuation_of=target['id'])
                del self.runtime['waiting_actions'][previous['id']]
            retry['recovery'] = {'execution_id': target['id'], 'disposition_id': record['id'],
                                 'reason': disposition['reason']}
            retry.pop("after_stop", None)
            activity = self.runtime['activities'][target['owner_activity_id']]
            if activity['status'] == 'waiting':
                activities.resume_activity(self.runtime, activity['id'], condition=activity['waiting']['condition'], at=now())
            record.setdefault('result', {})['continuation_action_id'] = retry['id']
        elif kind == "task_disposition":
            task = self.runtime["tasks"].get(disposition["task_id"])
            if task is None or previous.get("target") != task["id"]:
                raise ValueError("operational task disposition differs from the target's task")
            reviewer = self.runtime["executions"][record["execution_id"]]
            assessments = reviewer.get("output", {}).get("task_assessments", [])
            if (len(assessments) != 1 or assessments[0].get("task_id") != task["id"]
                    or assessments[0].get("decision") != disposition["task_state"]):
                raise ValueError("operational task disposition requires one matching item assessment")
            _, _, input_runtime = self.store.load(reviewer["input_snapshot"])
            self.instance, self.runtime = task_scope.apply_task_assessments(self.instance, self.runtime,
                assessments, execution_id=record["execution_id"], input_tasks=input_runtime["tasks"],
                evaluation_context=self._evaluation_context())
            target = self.runtime["executions"][record["target_execution_id"]]
            record = self.runtime.get("operational_dispositions", {}).get(record["id"], record)
        elif kind == "user_decision":
            link = questions.link(self.runtime, execution_id=record["execution_id"],
                field="output/disposition/question", owner="user", targets=[previous.get("target") or self.instance["id"]],
                reason=disposition["effect"])
            record["question_id"] = link["id"]
        record["status"] = "applied"
        target.pop("pending_operational_disposition", None)

    def _run_pending_operational_repairs(self):
        """Finish accepted dispositions after termination, including a restart."""
        if self.runtime["status"] in {"paused", "closed", "completed"}:
            return
        for identifier in list(self.runtime.get("operational_dispositions", {})):
            record = self.runtime["operational_dispositions"][identifier]
            kind = record.get('disposition', {}).get('kind')
            if kind == 'repair':
                if record['status'] in {'applied', 'repair_deferred', 'repair_verification_failed',
                        'installation_repair_pending', 'installation_repair_waiting', 'installation_repair_resolved'}:
                    continue
            elif kind not in {'resume', 'retry', 'task_disposition'} or record['status'] != 'awaiting_termination':
                continue
            if any(self.runtime["executions"][record[key]]["status"] != "ended"
                   for key in ("execution_id", "target_execution_id")):
                continue
            self._complete_operational_disposition(record)
            self._save()

    def _goal_basis_key(self) -> str:
        tasks = [{key: deepcopy(task.get(key)) for key in
                  ("id", "revision", "question", "scope", "completion_obligations", "expected_outputs", "results", "status")}
                 for task in self.runtime["tasks"].values()]
        return hashlib.sha256(lossless_json({"goal": self._governance()["goal"], "goal_revision": self._governance().get("goal_revision", 1),
            "policy_revision": self._governance().get("policy_revision", 1), "knowledge": self.instance["knowledge"],
            "formal_results": self.instance.get("formal_results", {}), "expositions": self.instance.get("expositions", {}),
            "identity_assessments": self.instance.get("identity_assessments", {}),
            "assessment_uses": self.instance.get("assessment_uses", {}),
            "trust_environments": self.instance.get("trust_environments", {}),
            "tasks": tasks, "goal_kind": self._governance()["goal_kind"], "sources": capture_sources(self.instance),
            "user_inputs": self.runtime["inputs"], "required": self.instance["config"]["goal_auditors"],
            "input_contract": hashlib.sha256(self._render_prompt("goal_audit", {}).encode()).hexdigest()})).hexdigest()

    def _apply_plan(self, output: dict, execution_id: str) -> None:
        execution = self.runtime["executions"][execution_id]
        _, _, input_runtime = self.store.load(execution["input_snapshot"])
        fixed = submission.load_json(self.store.read(
            "runtime/artifacts/" + execution["input_bundle"] + "/input/submission/context.json", self.head))
        if fixed.get("snapshot") != execution["input_snapshot"] or "ready_task_ids" not in fixed:
            raise ValueError("planning input is missing its fixed candidate population")
        input_tasks = {row["id"]: input_runtime["tasks"][row["id"]] for row in fixed["tasks"]}
        reference_tasks = dict(input_tasks)
        for row in fixed.get('task_catalog', []):
            source = row['source_ref']
            raw = self.store.read(source['artifact_ref'], self.head)
            if source['snapshot'] != execution['input_snapshot'] or hashlib.sha256(raw).hexdigest() != source['sha256']:
                raise ValueError('planning task catalog differs from its fixed source')
            task = input_runtime['tasks'][row['id']]
            if planning.contract_hash(submission.load_json(raw)) != planning.contract_hash(task):
                raise ValueError('planning task catalog differs from its input snapshot')
            reference_tasks[row['id']] = task
        self._apply_task_plan(output, execution_id, input_tasks, fixed["ready_task_ids"],
                              reference_tasks=reference_tasks, evaluation_context=self._evaluation_context())
        self._apply_input_overflow_resolutions(execution.get('extensions', {}).get('input_overflow_resolutions', []),
                                               fixed, execution_id)
        for assessment in output["task_assessments"]:
            task = self.runtime["tasks"][assessment["task_id"]]
            self._record_academic_assessment(task, assessment, execution_id)
        if output["goal_audit"]:
            if self._governance()["goal_kind"] != "mathematical":
                raise ValueError("nonformal work cannot authorize a final goal guarantee")
            if self.instance["goal_status"] != "mathematically_solved":
                basis = self._goal_basis_key()
                self._ensure_goal_audit_requests(basis, execution_id)
        self._ensure_academic_followup()

    def _formal(self, action: dict) -> None:
        return self._run_machine_steps(self._formal_steps(deepcopy(action)))

    def _formal_steps(self, action: dict):
        action.setdefault("id", new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        kid = action["target"]
        proposal = knowledge_records.proposal_view(self.instance, kid)
        profile = self._execution_profile(action)
        execution_id, bundle = new_id("EX"), new_id("BA")
        environment_error = None
        try:
            self._action_lifecycle_gate(action)
            environment = deepcopy(self._formal_environment())
            invocation = execution_profiles.machine_invocation(profile, trust_environment=environment,
                on_started=lambda identity: self._machine_started(execution_id, identity))
        except ValueError as error:
            environment, environment_error = None, str(error)
        environment_id = environment["id"] if environment else None
        authority = governance.authorize(self.instance, action, runtime=self.runtime)
        if not authority["allowed"] or environment is None:
            activity = self._activity_for_action(action)
            reason = authority["reason"] if not authority["allowed"] else environment_error
            activities.wait_for(self.runtime, activity["id"], reason=reason,
                condition={"kind": "formal_authority", "knowledge_id": kid}, next_owner="trust_governance", at=now())
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": deepcopy(action), "kind": "formal_authority", "reason": reason,
                "next_owner": "trust_governance"}
            self._remove_action(action)
            self._save()
            return
        source, declarations = proposal["lean_code"], deepcopy(proposal["declaration_names"])
        predecessor = self.runtime["executions"].get(action.get("continuation_of"))
        manifest = [{"kind": "formal_source", "sha256": hashlib.sha256(source.encode()).hexdigest(),
                     "declaration_names": declarations},
                    {"kind": "trust_environment", "id": environment_id,
                     "sha256": knowledge_records.digest(environment)}]
        if predecessor and predecessor.get("role") == "formal_check":
            prior = predecessor.get("input_manifest", [])
            # Older manifests lack declaration names; their immutable input snapshot
            # supplies the missing part of the original contract.
            if prior and "declaration_names" not in prior[0]:
                _, original, _ = self.store.load(predecessor["input_snapshot"])
                prior = deepcopy(prior)
                prior[0]["declaration_names"] = knowledge_records.proposal_view(original, kid)["declaration_names"]
            if prior != manifest:
                self._remove_action(action)
                self._enqueue("research_plan", reason="Formal continuation inputs changed; reassess the preserved result",
                              evidence_refs=[kid, predecessor["id"]])
                self._settle_activity(predecessor["id"])
                self._save()
                return
        workspace = Path(self.instance["workspace"]) / "formal" / execution_id
        execution = self._register_execution(action, {
            "id": execution_id, "role": "formal_check", "status": "running", "created_at": now(),
            "grant_id": authority["grant_id"], "engine_sha256": ENGINE_SHA256, "input_snapshot": self.head,
            'decision_basis': capture_decision_basis(self.instance, self.runtime,
                planning.action_read_ids(action, self.instance, self.runtime)),
            "input_manifest": manifest})
        if execution is None:
            self._save()
            return
        workspace.mkdir(parents=True)
        self.runtime["active_execution"] = execution_id
        self._save()
        stop_reasons = set()
        def stop():
            self._controls()
            if self._check_conversations():
                self._save()
            reasons = set()
            if self.runtime["status"] in {"closed", "completed"}:
                reasons.add("instance_ended")
            if self.runtime["status"] == "paused" or self.runtime.get("stop_requested"):
                reasons.add("instance_paused")
            if getattr(self, '_calls', None) is not None and self._calls.stopping:
                reasons.add("executor_stopping")
            if self.runtime["executions"][execution_id].get("stop_requested"):
                reasons.add("execution_stop_requested")
            if not governance.authorize(self.instance, action, runtime=self.runtime)["allowed"]:
                reasons.add("authority_changed")
            if (self.instance.get("active_trust_environment") != environment_id
                    or self.instance.get("trust_environments", {}).get(environment_id) != environment):
                reasons.add("trust_environment_changed")
            if decision_basis_changes(execution['decision_basis'], self.instance, self.runtime):
                reasons.add("input_changed")
            stop_reasons.update(reasons)
            return bool(reasons)
        kwargs = dict(source=source, declarations=declarations, workspace=workspace,
                      **invocation)
        parameters = inspect.signature(self.formal_verifier).parameters
        accepts_extra = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
        if "should_stop" in parameters or accepts_extra:
            kwargs["should_stop"] = stop
        if "allowed_axioms" in parameters or accepts_extra:
            kwargs["allowed_axioms"] = tuple(environment.get("allowed_axioms", []))
        result = ({'status': 'stopped', 'reason': 'formal authority changed'} if stop()
                  else (yield execution_id, kwargs))
        self._live_execution_ids.discard(execution_id)
        result = json_safe(result)
        # Preserve returned evidence before currentness checks or domain publication.
        reference = f"runtime/artifacts/{bundle}/formal.json"
        raw_bundle = new_id('BA')
        raw_reference = f'runtime/artifacts/{raw_bundle}/formal-returned.json'
        self.runtime['executions'][execution_id].update(result_ref=raw_reference, raw_result_ref=raw_reference, artifact_bundle=raw_bundle)
        self._save({f'runtime/artifacts/{raw_bundle}/proposal.lean': source.encode(), raw_reference: lossless_json(result)})
        if stop():
            result = {**result, "status": "stopped", "reason": ", ".join(sorted(stop_reasons))}
        current = knowledge_records.proposal_view(self.instance, kid)
        if current["lean_code"] != source or current["declaration_names"] != declarations:
            result = {**result, "status": "failed", "reason": "formal source changed during verification"}
        reference = f"runtime/artifacts/{bundle}/formal.json"
        execution = self.runtime["executions"][execution_id]
        execution.update(result_ref=reference, artifact_bundle=bundle, formal_status=result["status"])
        if not self._release_call_slot(execution_id):
            execution_lifecycle.transition_execution(execution, "stopping", at=now(), stop_phase="terminating",
                reason="Machine Job termination remains unconfirmed")
            execution["error"] = "Machine capacity and result remain held until local Job termination is confirmed."
            self._save({f"runtime/artifacts/{bundle}/proposal.lean": source.encode(), reference: lossless_json(result)})
            return
        # Failed compiler runs remain evidence. Only complete checked evidence can seal a formal result.
        if result["status"] == "verified":
            try:
                if self._formal_environment() != environment:
                    raise ValueError("fixed trust environment changed before admission")
                self.instance = knowledge_records.record_formal_result(self.instance, kid,
                    {**result, "execution_id": execution_id, "artifact_ref": reference}, environment_id, runtime=self.runtime)
            except ValueError as error:
                result = {**result, "status": "failed", "reason": str(error)}
                execution["formal_status"] = "failed"
        execution_lifecycle.transition_execution(execution, "stopping", at=now(), stop_phase="terminating")
        if result["status"] == "verified":
            execution["submission_receipt"] = {"kind": "machine_output", "state": "accepted", "execution_id": execution_id,
                "evidence_ref": reference, "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "trust_environment_id": environment_id, "accepted_at": now()}
        execution_lifecycle.transition_execution(execution, "ended", at=now(),
            outcome="output_accepted" if result["status"] == "verified" else "execution_incomplete",
            disposition={"kind": "formal_result", "status": result["status"], "artifact_ref": reference,
                         "stop_reasons": sorted(stop_reasons)})
        if self.runtime.get('active_execution') == execution_id:
            self.runtime["active_execution"] = None
        resumable = (result["status"] == "stopped" and "instance_paused" in stop_reasons
                     and not stop_reasons.intersection({"instance_ended", "authority_changed",
                                                       "trust_environment_changed", "input_changed"}))
        if resumable:
            activities.continue_activity(self.runtime, execution_id, at=now(), reason="formal_paused")
        else:
            self._remove_action(action)
        if result["status"] != "verified" and result["status"] != "stopped":
            self._enqueue("research_plan", reason="Assess preserved formal verification result", formal_target=kid)
        elif result["status"] == "stopped" and not resumable and "instance_ended" not in stop_reasons:
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                "action": deepcopy(action), "kind": "formal_stopped", "reason": result.get('reason'),
                "execution_id": execution_id, "next_owner": "trust_governance"}
        self._settle_activity(execution_id)
        self._save({f"runtime/artifacts/{bundle}/proposal.lean": source.encode(), reference: lossless_json(result)})
        if result["status"] == "verified":
            try:
                self._start_identity_review(kid)
            except (ValueError, KeyError, TypeError) as error:
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = {
                    "action": {"id": new_id("AC"), "role": "identity_review", "target": kid},
                    "kind": "review_initialization", "execution_id": execution_id,
                    "reason": str(error), "next_owner": "review_policy"}
            self._save()

    def _submission_check_summary(self, snapshot, runtime):
        try:
            seals, covered = [], set()
            receipts = dict(runtime.get('control_receipts', {}))
            for event in runtime.get('events', []):
                if event['kind'] != 'submission_checked':
                    continue
                if event.get('basis', {}).get('origin') == 'native_final':
                    receipt = event['basis']['receipt']
                    if receipt['kind'] != 'native_final' or event['source_ref'] != event['target']:
                        raise ValueError('native check event differs from its execution')
                    receipts[receipt['id']] = receipt
                else:
                    receipt = receipts[event['source_ref']]
                evidence = receipt['payload']['submission_check']
                if (receipt['kind'] not in {'submit_intent', 'native_final'} or receipt['execution_id'] != event['target']
                        or event.get('evidence_refs') != [evidence['check_ref']]):
                    raise ValueError('central check event differs from its receipt')
                covered.add(receipt['id'])
                seals.append({'event_seq': event['event_seq'], 'capture_id': receipt.get('request_id', receipt['id']),
                    'execution_id': receipt['execution_id'], 'state': receipt['state'],
                    'submission_check': evidence})
            required = {row['id'] for row in receipts.values() if row.get('kind') == 'submit_intent'
                        and (row.get('state') == 'accepted' or row.get('payload', {}).get('submission_check'))}
            if required - covered:
                raise ValueError('saved central submissions lack ordered check evidence: ' + ', '.join(sorted(required-covered)))
            for execution in runtime.get('executions', {}).values():
                intent = execution.get('submission_intent')
                if not intent:
                    continue
                receipt_id = execution.get('submission_receipt', {}).get('id')
                if receipt_id not in covered or receipts[receipt_id]['payload']['submission_check']['check_ref'] != intent.get('check_ref'):
                    raise ValueError('saved accepted submission has no matching central check evidence')
            seals.sort(key=lambda row: row['event_seq'])
            summary = submission.summarize_snapshot_checks(seals, snapshot=snapshot,
                read_artifact=lambda selected,path: self.store.read(path,selected), history_window=len(seals))
        except (ValueError, KeyError, TypeError, OSError, GitStateStoreError) as error:
            return {'snapshot':snapshot,'status':'incomplete','error':str(error),'next_owner':'maintenance'}
        summary.update(status='verified')
        return summary

    def _inspect_before_write(self):
        """Reject damaged current evidence before any recovery or installation write."""
        _require_current_contract(self.instance, self.runtime)
        structural = inspect_current_state(self.instance, self.runtime)
        if not structural["valid"]:
            raise ValueError("current state is damaged: " + str(structural))
        snapshot = self.head
        inspection = inspect_state(self.instance, self.runtime, requested_areas=["record_storage"],
            snapshot=snapshot, read_artifact=lambda path: self.store.read(path, snapshot),
            read_artifacts=lambda paths: self.store.read_many(paths, snapshot))
        failed = [row for row in inspection["findings"] if row.get("status") in {"blocked", "incomplete"}]
        if failed:
            raise ValueError("current state evidence must be repaired before publication: " + str(failed))
        inputs = [(execution, f"runtime/artifacts/{execution['input_bundle']}/input.txt")
                  for execution in self.runtime["executions"].values()
                  if execution.get("input_bundle") and execution.get("input_sha256")]
        read = prefetch_artifacts([path for _, path in inputs],
            lambda path: self.store.read(path, snapshot), lambda paths: self.store.read_many(paths, snapshot))
        for execution, path in inputs:
            if hashlib.sha256(read(path)).hexdigest() != execution["input_sha256"]:
                raise ValueError("current input artifact is damaged: " + execution["id"])

    def check(self, snapshot=None, requested_areas=None) -> dict:
        head, instance, runtime = self.store.load(snapshot)
        inspection = inspect_state(instance, runtime, requested_areas=requested_areas,
            snapshot=head, read_artifact=lambda path: self.store.read(path, head),
            read_artifacts=lambda paths: self.store.read_many(paths, head))
        areas = set(inspection["requested_areas"])
        errors = []
        try:
            if "record_storage" in areas:
                _require_current_contract(instance, runtime)
                inputs = [(execution, f"runtime/artifacts/{execution['input_bundle']}/input.txt")
                          for execution in runtime["executions"].values()
                          if execution.get("input_bundle") and execution.get("input_sha256")]
                read = prefetch_artifacts([path for _, path in inputs],
                    lambda path: self.store.read(path, head), lambda paths: self.store.read_many(paths, head))
                for execution, ref in inputs:
                    if hashlib.sha256(read(ref)).hexdigest() != execution["input_sha256"]:
                        errors.append(ref + ": preserved input differs from its content reference")
            if "governance_trust" in areas:
                validate_config(instance["config"])
            if "mathematical_effect" in areas:
                knowledge_records.validate_knowledge_records(instance)
        except (ValueError, KeyError, TypeError, OSError, GitStateStoreError) as error:
            errors.append(str(error))
        summary = self._submission_check_summary(head, runtime) if "repair_iteration" in areas else None
        if summary and summary["status"] == "incomplete":
            inspection["findings"].append({"area": "repair_iteration", "status": "incomplete",
                "message": "Submission check history is incomplete", "blocked_scope": [],
                "evidence": summary.get("incomplete_history_events", [head]), "next_owner": "maintenance"})
            if inspection["status"] != "blocked":
                inspection["status"] = "incomplete"
        if errors:
            inspection["findings"].append({"area": "central_connections", "status": "blocked",
                "message": "; ".join(errors), "blocked_scope": ["dispatch", "integration"],
                "evidence": [head], "next_owner": "engine"})
            inspection["status"] = "blocked"
        return {"snapshot": head, "passed": inspection["status"] == "healthy", "inspection": inspection,
                "submission_checks": summary, "errors": errors,
                "scope": "requested persisted-state areas and their referenced artifact bytes",
                "research_effectiveness": {"status": "not_evaluated"}}
