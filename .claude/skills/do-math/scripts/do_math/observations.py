"""Version-5 observation facts, self-check obligations, and review triggers."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import time
from typing import Any

from jsonschema import Draft202012Validator

from .context_store import is_excluded, read_stable, safe_path
from .control_transport import (CONTROL_SERVER, RECEIPT_TOOL, SAFETY_BOUNDARY, SELF_CHECK_RESPONSE,
                                SELF_CHECK_TOOL, SUBMIT_TOOL, self_check_request_id, self_check_response_errors)
from .file_io import is_sha256, now, parse_utc, strict_json_loads
from .repository import validate_storage_value
from .state_contract import default_state_contract, validate_record
from .execution_profiles import OBSERVATION_MODES
from .file_io import read_bytes_shared, write_bytes_atomic, file_fingerprint, fingerprint_settled

CHECKPOINT_MAX_BYTES = 4 * 1024 * 1024
RULES_MAX_BYTES = 65536
# The one operator table: each operator's subject kind, unit, and the one
# source that actually produces its value during an execution.
OPERATORS = {
    "counter_gte": {"subject_kind": "counter", "unit": "count", "source": "checkpoint"},
    "iteration_gte": {"subject_kind": "iteration", "unit": "count", "source": "checkpoint"},
    "checkpoint_count_gte": {"subject_kind": "checkpoint", "unit": "count", "source": "checkpoint"},
    "tool_call_completed": {"subject_kind": "tool_call", "unit": "count", "source": "adapter_calls"},
    "safe_boundary_recorded": {"subject_kind": "safe_boundary", "unit": "count", "source": "control_receipts"},
    "wall_time_reached": {"subject_kind": "clock", "unit": "UTC", "source": "clock"},
}
_ONE_TIME_OPERATORS = frozenset({"tool_call_completed", "safe_boundary_recorded"})
_RULE_FIELDS = {"id", "operator", "subject", "basis", "threshold", "repeat_interval", "required_evidence"}
# Fields a worker may read from its feedback file. Every producer builds its
# feedback through ``worker_feedback`` so that a stray field fails before ENGINE saves.
WORKER_FEEDBACK_FIELDS = frozenset({
    "kind", "reason", "errors", "obligation_id", "execution_id", "rule_revision", "due",
    "deadline_offset_ms", "active_revision", "active_rules_sha256",
    "previous_rules_sha256", "previous_rules_preserved", "next_owner"})


def worker_feedback(feedback: dict) -> dict:
    if not isinstance(feedback, dict) or set(feedback) - WORKER_FEEDBACK_FIELDS:
        raise ValueError("worker feedback contains private or unknown fields")
    return feedback


def observation_rule_contract() -> list[dict]:
    """Return the sealed, actually-produced signal kinds available to a profile.

    A profile names signal kinds only. Counter names are local to a
    particular execution and are checked against that execution's snapshot,
    rather than being guessed while a reusable profile is authored.
    """
    return [{"source": spec["source"], "operator": operator,
             "subject_kind": spec["subject_kind"], "unit": spec["unit"]}
            for operator, spec in sorted(OPERATORS.items())]

CHECKPOINT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "current_claim": {"type": "string"},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "attempts": {"type": "array", "items": {"type": "string"}},
        "remaining_work": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
        "progress_state": {"type": "string", "enum": ["working", "blocked", "no_progress", "ready_to_submit"]},
        "iteration": {"type": "integer", "minimum": 0},
        "counters": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    },
    "required": ["current_claim", "evidence_paths", "attempts", "remaining_work", "next_step", "progress_state"],
}
_CHECKPOINT_VALIDATOR = Draft202012Validator(CHECKPOINT_SCHEMA)

def validate_rule_proposal(proposal: dict, *, current_revision: int) -> list[dict]:
    if not isinstance(proposal, dict) or set(proposal) != {"current_revision", "reason", "rules"}:
        raise ValueError("rule proposal requires current_revision, reason and rules")
    if type(proposal["current_revision"]) is not int or proposal["current_revision"] != current_revision:
        raise ValueError("rule proposal revision is stale")
    if not isinstance(proposal["reason"], str) or not proposal["reason"].strip():
        raise ValueError("rule proposal needs a reason")
    return validate_rules(proposal["rules"])


def _json_safe(value: Any) -> Any:
    from .repository import canonical_json
    return json.loads(canonical_json(value))


def _raw_json(value: Any) -> str:
    # Provider payloads can contain fractional metrics. Keep their original
    # numeric semantics as JSON text, outside the integer-only state tree.
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)


# The obligation field that holds its response deadline while a research call runs.
_HELD = "deadline_held_offset_ms"


def _stored(family: str, record: dict) -> dict:
    """``record`` checked by the storage gate's own checker of runtime ``family`` (이음새-정본.md §6)."""
    validate_record(default_state_contract().family("runtime", family).checker, record,
                    f"runtime/{family}/{record.get('id')}")
    return record


def _deadline_passed(obligation: dict, offset: int) -> bool:
    """A held deadline has not passed; it moves when the hold ends (ObservationTracker._hold_deadlines)."""
    deadline = obligation["deadline_offset_ms"]
    return deadline is not None and _HELD not in obligation and offset > deadline


def persistent_record(record: dict, *, artifact_ref: str | None = None) -> dict:
    """Validate the integer-only record after ENGINE has preserved raw bytes."""
    value = deepcopy(record)
    if "raw" in value:
        raw = value.pop("raw")
        if not isinstance(artifact_ref, str) or not artifact_ref:
            raise ValueError("raw observation needs a preserved artifact reference")
        if not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != value.get("sha256"):
            raise ValueError("observation artifact hash differs from raw bytes")
        value["artifact_ref"] = artifact_ref
    return _json_safe(value)


def _execution_bound_subject(rule):
    # A checkpoint count and a checkpoint iteration are keyed by the execution itself.
    return rule['subject']['kind'] == 'checkpoint' or rule['operator'] == 'iteration_gte'


def validate_task_rules(rules):
    """Reusable task rules cannot name a future or previous execution."""
    checked = validate_rules(rules)
    for rule in checked:
        if _execution_bound_subject(rule) and rule['subject']['id'] != '$execution':
            raise ValueError('task rule execution-bound subject must be $execution')
    return checked


def bind_task_rules(rules, execution_id):
    checked = validate_task_rules(rules)
    for rule in checked:
        if _execution_bound_subject(rule):
            rule['subject']['id'] = execution_id
    return checked


def validate_rule_preparation(action, extensions, tasks):
    """The producer and receiver enforce the same assigned edition and coverage."""
    targets = action.get('observation_rule_targets', {})
    if 'observation_rule_targets' not in action:
        return {}
    from .model_policy import assessment_basis
    from .task_contracts import TERMINAL_TASK_STATUSES
    for tid, basis in targets.items():
        task = tasks.get(tid)
        if (not task or task.get('status') in TERMINAL_TASK_STATUSES
                or assessment_basis(task) != basis):
            raise ValueError('observation rule target contract edition changed: ' + tid)
    prepared = {}
    for row in extensions.get('task_conditions', []):
        if set(row) != {'task_id', 'observation_rules'}:
            raise ValueError('rule preparation permits only task_id and observation_rules')
        tid = row['task_id']
        if tid in prepared:
            raise ValueError('duplicate observation rule target: ' + tid)
        prepared[tid] = validate_task_rules(row['observation_rules'])
    deferred = []
    for row in extensions.get('observation_rule_deferrals', []):
        if (set(row) != {'task_id', 'reason', 'missing_inputs', 'next_owner'}
                or not isinstance(row['reason'], str) or not row['reason'].strip()
                or not isinstance(row['missing_inputs'], list) or not row['missing_inputs']
                or any(not isinstance(ref, str) or not ref.strip() for ref in row['missing_inputs'])
                or len(row['missing_inputs']) != len(set(row['missing_inputs']))
                or row['next_owner'] not in {'user', 'research_preparation', 'research_plan', 'maintenance'}):
            raise ValueError('rule deferral needs reason, distinct missing_inputs and next_owner')
        deferred.append(row['task_id'])
    if (len(deferred) != len(set(deferred)) or set(deferred) & set(prepared)
            or set(prepared) | set(deferred) != set(targets)):
        raise ValueError('observation rule coverage must dispose every assigned target exactly once')
    return prepared


def task_rules_from_execution(rules, execution_id):
    """Preserve a separate reusable rule without rewriting the execution evidence."""
    checked = validate_rules(rules)
    for rule in checked:
        if _execution_bound_subject(rule):
            if rule['subject']['id'] not in {'$execution', execution_id}:
                raise ValueError('persisted rule refers to another execution')
            rule['subject']['id'] = '$execution'
    return validate_task_rules(checked)


def observation_settings_used(profile: dict) -> list[str]:
    """The observation settings a profile's mode and role use; each is required."""
    used = []
    if profile['observation']['mode'] != 'deadline_only':
        used.extend(['tool_review_window_seconds', 'observation_interval_seconds'])
    if profile['role'] == 'research_work':
        used.append('self_check_response_window_seconds')
    return used


def observation_settings_errors(profile: dict) -> list[dict]:
    """Check profile settings without requiring a not-yet-authored task's rules."""
    settings = profile['observation']['settings']
    errors = []
    for field in observation_settings_used(profile):
        try:
            duration_ms(settings.get(field), field, required=True)
        except ValueError as error:
            errors.append({'role': profile['role'], 'profile_id': profile['id'],
                           'field': field, 'reason': str(error)})
    return errors


def tracker_config(profile: dict, *, initial_self_check_rules: list[dict] | None = None,
                   no_progress_limit: int | None = None) -> dict:
    """Build admission config solely from a selected, sealed profile edition."""
    from .execution_profiles import profile_ref
    reference = profile_ref(profile)
    settings = deepcopy(profile["observation"]["settings"])
    research = profile["role"] == "research_work"
    errors = observation_settings_errors(profile)
    if errors:
        raise ValueError(json.dumps(errors, ensure_ascii=False))
    if research:
        validate_rules(initial_self_check_rules)
        validate_execution_rules(initial_self_check_rules, bindings=profile["observation"].get("rule_bindings"), execution_id=None)
    return {**settings,
            "observation_mode": profile["observation"]["mode"],
            "observation_profile_ref": reference, "research_self_checks": research,
            "observation_rule_bindings": deepcopy(profile["observation"].get("rule_bindings", [])),
            "observation_rules": deepcopy(initial_self_check_rules or []),
            "self_check_revision": 0, "no_progress_limit": no_progress_limit,
            "checkpoint_expected": research}


def _utc(value: str, field: str) -> datetime:
    try:
        return parse_utc(value)
    except ValueError as error:
        raise ValueError(field + " must be an ISO timestamp with a timezone") from error


def duration_ms(seconds: Any, field: str, *, required: bool = False) -> int | None:
    """Convert admitted seconds to an exact positive integer millisecond value."""
    if seconds is None and not required:
        return None
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float, str)):
        raise ValueError(field + " must be a positive millisecond-exact duration")
    try:
        milliseconds = Decimal(str(seconds)) * 1000
    except InvalidOperation as error:
        raise ValueError(field + " must be a positive millisecond-exact duration") from error
    if not milliseconds.is_finite() or milliseconds <= 0 or milliseconds != milliseconds.to_integral_value():
        raise ValueError(field + " must be a positive millisecond-exact duration")
    return int(milliseconds)


def _offset_ms(started: float, current: float) -> int:
    return max(0, int((Decimal(str(current)) - Decimal(str(started))) * 1000))


def validate_rules(rules: list[dict], *, allow_empty: bool = False) -> list[dict]:
    if not isinstance(rules, list) or len(rules) > 16 or (not rules and not allow_empty):
        raise ValueError("observation rules must be a nonempty list of at most 16 rules")
    seen = set()
    for rule in rules:
        expected = _RULE_FIELDS if isinstance(rule, dict) and "repeat_interval" in rule else _RULE_FIELDS - {"repeat_interval"}
        if not isinstance(rule, dict) or set(rule) != expected:
            raise ValueError("invalid observation rule fields")
        if not isinstance(rule.get("id"), str) or not rule["id"] or rule["id"] in seen:
            raise ValueError("observation rule IDs must be distinct and nonempty")
        seen.add(rule["id"])
        operator = rule.get("operator")
        if not isinstance(operator, str) or operator not in OPERATORS:
            raise ValueError("unsupported observation operator")
        spec = OPERATORS[operator]
        subject, basis = rule.get("subject"), rule.get("basis")
        if not isinstance(subject, dict) or set(subject) != {"kind", "id"}:
            raise ValueError("rule subject must contain exactly kind and id")
        if subject.get("kind") != spec["subject_kind"] or not isinstance(subject.get("id"), str) or not subject["id"]:
            raise ValueError("rule subject is incompatible with its operator")
        if basis != {"source": spec["source"], "unit": spec["unit"]}:
            raise ValueError("rule basis of " + operator + " must be source " + spec["source"] + " in " + spec["unit"])
        evidence = rule.get("required_evidence")
        if (not isinstance(evidence, list) or not evidence or
                any(not isinstance(ref, str) or not ref for ref in evidence) or len(evidence) != len(set(evidence))):
            raise ValueError("rule required_evidence must be a nonempty unique string list")
        if operator == "wall_time_reached":
            _utc(rule.get("threshold"), "wall_time_reached threshold")
            if "repeat_interval" in rule:
                raise ValueError("wall_time_reached cannot repeat")
            continue
        threshold = rule.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
            raise ValueError("rule threshold must be a positive integer")
        interval = rule.get("repeat_interval")
        if "repeat_interval" in rule and (isinstance(interval, bool) or not isinstance(interval, int) or interval < 1):
            raise ValueError("repeat_interval must be a positive integer")
        if operator in _ONE_TIME_OPERATORS and (threshold != 1 or interval is not None):
            raise ValueError(operator + " is a one-time recorded event")
    return deepcopy(rules)


def _boundary_key(rule: dict) -> str:
    # IDs and revisions name presentations, not new occurrences of an event.
    identity = {key: rule[key] for key in ("operator", "subject", "basis")}
    if rule["operator"] == "wall_time_reached":
        identity["threshold"] = _utc(rule["threshold"], "threshold").isoformat()
    return hashlib.sha256(_raw_json(identity).encode()).hexdigest()


def validate_observation_rule_contract(bindings: list[dict]) -> list[dict]:
    """Validate profile signal kinds against the implemented snapshot producers.

    Profiles use the signal kinds emitted by observation_rule_contract.
    """
    if not isinstance(bindings, list):
        raise ValueError("profile observation rule contract must be a list")
    contract, checked = observation_rule_contract(), []
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"source", "operator", "subject_kind", "unit"}:
            raise ValueError("invalid profile observation binding")
        if binding not in contract:
            raise ValueError("profile observation contract has no implemented producer for its signal kind")
        if binding in checked:
            raise ValueError("profile observation contract repeats a signal kind")
        checked.append(deepcopy(binding))
    return checked


def validate_execution_rules(rules: list[dict], *, bindings: list[dict], execution_id: str | None) -> list[dict]:
    """Admit only signals registered in the immutable profile's observation contract.

    Bindings are {source, operator, subject_kind, unit}. Syntax alone
    does not establish that an execution-local name has appeared in a snapshot.
    """
    checked = validate_rules(rules, allow_empty=True)
    if not isinstance(bindings, list) or (checked and not bindings):
        raise ValueError("profile lacks observation rule bindings")
    bindings = validate_observation_rule_contract(bindings)
    for rule in checked:
        subject = rule["subject"]
        if execution_id is not None and _execution_bound_subject(rule) and subject["id"] != execution_id:
            raise ValueError("rule subject belongs to a different execution")
        def matches(binding):
            return (binding["operator"] == rule["operator"] and binding["source"] == rule["basis"]["source"] and
                    binding["unit"] == rule["basis"]["unit"] and binding["subject_kind"] == subject["kind"])
        if not any(matches(binding) for binding in bindings):
            raise ValueError("rule has no registered observable subject/source/unit: " + rule["id"])
    return checked


def evaluate_rules(rules: list[dict], snapshot: dict, *, consumed_boundaries: dict[str, int] | None = None) -> list[dict]:
    """Evaluate already validated rules against one accumulated observation snapshot.

    The tracker validates its rules when it is created and when they are replaced.
    """
    consumed = consumed_boundaries or {}
    calls = set(snapshot.get("completed_call_ids", []))
    boundaries = set(snapshot.get("safe_boundary_ids", []))
    counters = snapshot.get("counters", {})
    iterations = snapshot.get("iterations", {})
    checkpoints = snapshot.get("checkpoint_counts", {})
    due = []
    for rule in rules:
        operator, subject = rule["operator"], rule["subject"]["id"]
        if operator == "counter_gte": value = counters.get(subject)
        elif operator == "iteration_gte": value = iterations.get(subject)
        elif operator == "checkpoint_count_gte": value = checkpoints.get(subject)
        elif operator == "wall_time_reached":
            observed = snapshot.get("observed_at")
            value = 1 if observed is not None and _utc(observed, "observed_at") >= _utc(rule["threshold"], "threshold") else None
        elif operator == "tool_call_completed": value = 1 if subject in calls else None
        else: value = 1 if subject in boundaries else None
        threshold = 1 if operator == "wall_time_reached" else rule["threshold"]
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid observation value for " + rule["id"])
        if value is None or value < threshold:
            continue
        key = _boundary_key(rule)
        previous, interval = consumed.get(key, 0), rule.get("repeat_interval")
        boundary = threshold if previous < threshold else threshold + ((previous - threshold) // interval + 1) * interval if interval is not None else None
        if boundary is None or value < boundary:
            continue
        crossed = boundary if interval is None else threshold + ((value - threshold) // interval) * interval
        due.append({"rule_id": rule["id"], "operator": operator, "subject": subject,
                    "basis": _json_safe(rule["basis"]), "required_evidence": list(rule["required_evidence"]),
                    "value": value, "boundary_key": key, "first_boundary": boundary, "boundary": crossed,
                    "next_boundary": None if interval is None else crossed + interval})
    return due


def checkpoint_value(raw: bytes) -> dict:
    """The checkpoint that ``raw`` holds: strict JSON in the storage value domain that matches CHECKPOINT_SCHEMA.

    The one checkpoint format rule. The tracker's live read, the receiver's capture
    check and the artifact format check all apply it, with one prebuilt validator."""
    value = strict_json_loads(raw.decode("utf-8-sig"))
    validate_storage_value(value)
    _CHECKPOINT_VALIDATOR.validate(value)
    return value


def read_checkpoint(workspace: Path) -> dict:
    path = workspace / "checkpoint.json"
    if not path.exists():
        return {"status": "missing"}
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(workspace.resolve()) or path.is_symlink():
            raise ValueError("checkpoint must stay within the execution workspace")
        before = file_fingerprint(path)
        if before[0] > CHECKPOINT_MAX_BYTES:
            raise ValueError("checkpoint exceeds the 4 MiB record limit")
        raw = read_bytes_shared(path)
        if file_fingerprint(path) != before:
            return {"status": "being_written"}
        digest = hashlib.sha256(raw).hexdigest()
        value = checkpoint_value(raw)
        for reference in value["evidence_paths"]:
            evidence = safe_path(workspace, reference)
            relative = Path(reference)
            if (relative.parts[0] != "input" and is_excluded(relative)) or not evidence.is_file():
                raise ValueError("checkpoint evidence is unavailable or excluded from preservation: " + reference)
        return {"status": "valid", "value": value, "sha256": digest, "raw": raw, "observed_at": now()}
    except Exception as error:
        return {"status": "invalid", "error": f"{type(error).__name__}: {error}"}


def capture_checkpoint_files(workspace, checkpoint, *, max_bytes):
    """Capture only named evidence with stable reads, preserving explicit omissions."""
    from .git_store import PhysicalBoundary
    files, omitted, total = {}, [], 0
    boundary = None
    for name in dict.fromkeys(checkpoint['evidence_paths']):
        try:
            path = safe_path(workspace, name)
            if total + path.stat().st_size > max_bytes:
                raise ValueError('checkpoint evidence exceeds artifact byte limit')
            # One proof of the workspace root serves every evidence read.
            boundary = boundary or PhysicalBoundary(workspace)
            raw = read_stable(path, boundary=boundary)
            if total + len(raw) > max_bytes:
                raise ValueError('checkpoint evidence exceeds artifact byte limit')
            files[name] = raw
            total += len(raw)
        except (OSError, ValueError) as error:
            omitted.append({'path': name, 'reason': str(error)})
    return files, omitted


class ObservationTracker:
    """One execution's v5 observation state; persistence remains ENGINE-owned."""

    def __init__(self, execution_id: str, workspace: Path, config: dict, *, clock=time.monotonic):
        config = deepcopy(config)
        self.execution_id, self.workspace, self.config, self.clock = execution_id, workspace, config, clock
        self.started = self.last_review = clock()
        self.mode = config.get("observation_mode", "event_driven")
        if self.mode not in OBSERVATION_MODES:
            raise ValueError("unsupported observation mode")
        self.rule_revision = config.get("self_check_revision", 0)
        if isinstance(self.rule_revision, bool) or not isinstance(self.rule_revision, int) or self.rule_revision < 0:
            raise ValueError("self_check_revision must be a nonnegative integer")
        self.research_self_checks = config.get("research_self_checks", self.mode == "event_driven")
        if self.mode == "deadline_only" and (self.research_self_checks or config.get("observation_rules")):
            raise ValueError("deadline_only cannot carry research self-check rules")
        self.rules = validate_rules(config.get("observation_rules", []), allow_empty=not self.research_self_checks)
        self.rule_bindings = config.get("observation_rule_bindings")
        if config.get("observation_profile_ref") or self.rule_bindings is not None:
            self.rules = validate_execution_rules(self.rules, bindings=self.rule_bindings, execution_id=execution_id)
        for rule in self.rules:
            if _execution_bound_subject(rule) and rule["subject"]["id"] != execution_id:
                raise ValueError("rule subject belongs to a different execution")
        self.rules_digest = hashlib.sha256(_raw_json(self.rules).encode()).hexdigest()
        self.rule_proposal_digest = None
        self.rule_file_mark = self.checkpoint_mark = None
        self.consumed_rules: dict[str, int] = {}
        self.obligations: dict[str, dict] = {}
        self.response_count = 0
        self.fact_sequence = 0
        self.checkpoint_count = 0
        self.seen_checkpoints: set[str] = set()
        self.self_check_checkpoints: set[str] = set()
        self.checkpoint_reminded = False
        self.pending_tools: dict[str, dict] = {}
        self.completed_call_ids: set[str] = set()
        self.safe_boundary_ids: set[str] = set()
        # Counters and iterations are the worker's checkpoint values; no provider event carries them.
        self.counters: dict[str, int] = {}
        self.iterations: dict[str, int] = {}
        self.tool_review_window_ms = duration_ms(config.get("tool_review_window_seconds"), "tool_review_window_seconds")
        self.periodic_interval_ms = duration_ms(config.get("observation_interval_seconds"), "observation_interval_seconds")
        self.response_window_ms = duration_ms(config.get("self_check_response_window_seconds"), "self_check_response_window_seconds")
        self.profile_ref = _json_safe(config.get("observation_profile_ref")) if config.get("observation_profile_ref") else None
        self.max_self_check_interval_ms = self.periodic_interval_ms if self.research_self_checks else None
        self.next_self_check_offset_ms = self.max_self_check_interval_ms
        self.last_self_check_offset_ms = 0
        self.execution_status = "running"
        self.no_progress_count = 0
        self.no_progress_limit = config.get("no_progress_limit")
        if self.no_progress_limit is not None and (type(self.no_progress_limit) is not int or self.no_progress_limit < 1):
            raise ValueError("no_progress_limit must be a positive contract integer")
        self.self_check_call_ids: set[str] = set()
        self.boundary_call_ids: set[str] = set()
        self.boundary_request_ids: set[str] = set()
        self.control_calls: dict[str, dict] = {}
        self.control_requests: dict[str, dict] = {}
        self.self_check_polls: dict[str, str] = {}
        self.explicit_reviews: dict[str, dict] = {}
        self.pending_records: list[dict] = []
        self.last_clock = self.started
        self.reported_unavailable: set[str] = set()
        self.observation_source = None
        self.live_observation = True

    def fact(self, kind: str, event: dict, when: float) -> dict:
        self.fact_sequence += 1
        raw = _raw_json(event)
        result = {"kind": kind, "id": f"OF-{self.execution_id}-{self.fact_sequence}",
                "execution_id": self.execution_id, "event_json": raw,
                "event_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "observed_at": now(), "monotonic_offset_ms": _offset_ms(self.started, when)}
        if self.observation_source is not None:
            result['source'] = {key: value for key, value in self.observation_source.items()
                                if key != 'received_monotonic'}
            result['source']['received_offset_ms'] = _offset_ms(self.started, when)
        return result

    def _merge_monotonic(self, destination: dict[str, int], values: Any, name: str) -> None:
        if values is None:
            return
        if not isinstance(values, dict):
            raise ValueError(name + " must be an object")
        for key, value in values.items():
            if not isinstance(key, str) or not key or isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(name + " requires nonnegative integer values")
            if value < destination.get(key, 0):
                raise ValueError(name + " cannot decrease")
        destination.update(values)

    def _ingest_event(self, event: dict, when: float) -> None:
        self._observe_control_calls(event)
        event_type = event.get("type")
        if event.get("execution_id", self.execution_id) != self.execution_id:
            raise ValueError("observation belongs to a different execution")
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if event_type == "item.started" and item.get("type") in {"command_execution", "mcp_tool_call"}:
            self._start_call(str(item.get("id", "unknown")), item.get("type"), when)
        elif event_type == "item.completed" and item.get("type") in {"command_execution", "mcp_tool_call"} and isinstance(item.get("id"), str): self._complete_call(item["id"])
        elif event_type == "system" and event.get("subtype") == "task_started" and event.get("is_backgrounded"):
            self._start_call("background:" + str(event.get("task_id")), event.get("task_type"), when)
        elif event_type == "system" and event.get("subtype") == "task_notification":
            self._complete_call("background:" + str(event.get("task_id")))
        elif event_type in {"assistant", "user"}:
            message = event.get("message")
            content = message.get("content", []) if isinstance(message, dict) else []
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict): continue
                if event_type == "assistant" and block.get("type") == "tool_use":
                    self._start_call(str(block.get("id", "unknown")), block.get("name"), when)
                elif event_type == "user" and block.get("type") == "tool_result":
                    self._complete_call(str(block.get("tool_use_id", "unknown")))

    def _start_call(self, call_id: str, name: Any, when: float) -> None:
        if call_id in self.pending_tools or call_id in self.completed_call_ids:
            return
        self.pending_tools[call_id] = {"started": when, "name": name, "review_due": False,
                                       "safe_boundary": False, "review_window_ms": self.tool_review_window_ms}
        if (self.live_observation and call_id not in self.self_check_call_ids
                and call_id not in self.boundary_call_ids and call_id not in self.control_calls):
            for obligation in self.obligations.values():
                after_delivery = (obligation.get('acknowledged_source_offset') is not None and
                    self.observation_source['start_offset'] >= max(obligation['delivered_source_offset'],
                                                                   obligation['acknowledged_source_offset']))
                if after_delivery and obligation["status"] == "open" and obligation["deadline_offset_ms"] is not None:
                    self._miss(obligation, "research_action_before_response")

    def issue_self_check(self, obligation_id) -> dict:
        """Start the response deadline and return the one request object to deliver.

        Its hash is what a successful poll must return.
        """
        obligation = self.obligations[obligation_id]
        obligation['delivered_at'] = now()
        if obligation['response_availability'] == 'available' and self.response_window_ms is not None:
            obligation['deadline_offset_ms'] = _offset_ms(self.started, self.clock()) + self.response_window_ms
        request = self_check_request(obligation)
        obligation['delivered_request_sha256'] = hashlib.sha256(_raw_json(request).encode()).hexdigest()
        return request

    def record_delivery(self, obligation_id, *, source_offset):
        """Stdout bytes before the delivered request's offset cannot violate it."""
        if type(source_offset) is not int or source_offset < 0:
            raise ValueError('self-check delivery requires a nonnegative stream offset')
        obligation = self.obligations[obligation_id]
        if not obligation.get('delivered_request_sha256'):
            raise ValueError('self-check delivery requires an issued request')
        obligation['delivered_source_offset'] = source_offset

    def _complete_call(self, call_id: str) -> None:
        self.pending_tools.pop(call_id, None)
        if (call_id not in self.self_check_call_ids and call_id not in self.boundary_call_ids
                and call_id not in self.control_calls):
            self.completed_call_ids.add(call_id)

    def _observe_control_calls(self, event: dict) -> None:
        """Match provider-observed identity and arguments before action accounting."""
        calls = []
        item = event.get("item", {})
        if (event.get("type") in {"item.started", "item.completed"} and isinstance(item, dict)
                and item.get("type") == "mcp_tool_call" and item.get("server") == CONTROL_SERVER):
            calls.append((item.get("id"), item.get("tool"), item.get("arguments")))
        if event.get("type") == "assistant":
            message = event.get("message", {})
            for block in message.get("content", []) if isinstance(message, dict) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    prefix = "mcp__" + CONTROL_SERVER + "__"
                    name = block.get("name", "")
                    if isinstance(name, str) and name.startswith(prefix):
                        calls.append((block.get("id"), name[len(prefix):], block.get("input")))
        for call_id, tool, arguments in calls:
            if not isinstance(call_id, str) or not isinstance(arguments, dict): continue
            if tool == SUBMIT_TOOL and arguments.get("kind") == SAFETY_BOUNDARY:
                payload = arguments.get("payload")
                request_id = arguments.get("request_id")
                if (isinstance(request_id, str) and request_id and isinstance(payload, dict)
                        and payload.get("inflight_calls") is False
                        and isinstance(payload.get("call_ids", []), list)
                        and all(isinstance(cid, str) for cid in payload.get("call_ids", []))):
                    # Submitting the boundary is not an inflight research operation.
                    # Its receipt still owns validation and making obligations available.
                    self.boundary_call_ids.add(call_id)
                    self.boundary_request_ids.add(request_id)
                continue
            if tool == RECEIPT_TOOL:
                request_id = arguments.get("request_id")
                if isinstance(request_id, str):
                    if request_id in self.control_requests:
                        self.self_check_call_ids.add(call_id)
                    elif request_id in self.boundary_request_ids:
                        self.boundary_call_ids.add(call_id)
                continue
            if tool == SELF_CHECK_TOOL:
                oid = arguments.get("self_check_id")
                payload = {"self_check_id": oid, "response": arguments.get("response")}
                request_id = self_check_request_id(oid) if isinstance(oid, str) else None
            elif tool == SUBMIT_TOOL and arguments.get("kind") == SELF_CHECK_RESPONSE:
                payload = arguments.get("payload")
                oid = payload.get("self_check_id") if isinstance(payload, dict) else None
                request_id = arguments.get("request_id")
            else:
                continue
            if not isinstance(oid, str) or oid not in self.obligations or not isinstance(request_id, str): continue
            if payload.get("response") is None and tool == SELF_CHECK_TOOL:
                # This installed tool reads the already-issued self-check only.
                self.self_check_call_ids.add(call_id)
                if self.self_check_polls.get(call_id, oid) != oid:
                    raise ValueError('self-check poll ID reused for another obligation')
                self.self_check_polls[call_id] = oid
                continue
            fingerprint = hashlib.sha256(_raw_json(payload).encode()).hexdigest()
            row = {"request_id": request_id, "obligation_id": oid, "payload_sha256": fingerprint}
            if call_id in self.control_calls and self.control_calls[call_id] != row:
                raise ValueError("control call ID reused with different request")
            known = self.control_requests.get(request_id)
            if known and known["payload_sha256"] != fingerprint:
                raise ValueError("observed control arguments differ from received request")
            self.control_calls[call_id] = row
            if known: self.self_check_call_ids.add(call_id)
        # A poll attempt or a generic safe boundary does not acknowledge this
        # request. Match the successful provider-observed returned envelope.
        if event.get('type') == 'item.completed' and isinstance(item, dict) and item.get('status') != 'failed' and not item.get('error'):
            self._acknowledge_poll(item.get('id'), item.get('result'))
        message = event.get('message')
        if event.get('type') == 'user' and isinstance(message, dict) and isinstance(message.get('content'), list):
            for block in message['content']:
                if isinstance(block, dict) and block.get('type') == 'tool_result' and not block.get('is_error'):
                    self._acknowledge_poll(block.get('tool_use_id'), block.get('content'))

    def _acknowledge_poll(self, call_id, result):
        if call_id not in self.self_check_polls:
            return
        if isinstance(result, dict) and result.get('isError'):
            return
        if isinstance(result, dict) and 'content' in result:
            result = result['content']
        if isinstance(result, list):
            result = ''.join(row.get('text', '') for row in result if isinstance(row, dict) and row.get('type') == 'text')
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except (ValueError, TypeError):
                return
        if not isinstance(result, dict):
            return
        obligation = self.obligations[self.self_check_polls[call_id]]
        if (not obligation.get('delivered_request_sha256') or
                hashlib.sha256(_raw_json(result).encode()).hexdigest() != obligation['delivered_request_sha256']):
            return
        obligation.setdefault('acknowledged_source_offset', self.observation_source['end_offset'])
        obligation.setdefault('acknowledged_call_id', call_id)

    def bind_control_request(self, request: dict, *, receipt_id: str) -> dict:
        """ENGINE invokes after checking the actual transport binding and grant.

        Payload equality links either arrival order without trusting a worker's
        declaration that an arbitrary research call is a self-check call.
        """
        if (request.get("kind") != SELF_CHECK_RESPONSE or request.get("execution_id") != self.execution_id
                or not isinstance(request.get("request_id"), str) or not isinstance(receipt_id, str) or not receipt_id):
            raise ValueError("control request is not this execution's self-check response")
        payload = request.get("payload")
        if not isinstance(payload, dict) or not isinstance(payload.get("self_check_id"), str) or payload["self_check_id"] not in self.obligations:
            raise ValueError("control request has no issued self-check obligation")
        fingerprint = hashlib.sha256(_raw_json(payload).encode()).hexdigest()
        request_id = request["request_id"]
        matching = [cid for cid, row in self.control_calls.items() if row["request_id"] == request_id]
        if any(self.control_calls[cid]["payload_sha256"] != fingerprint for cid in matching):
            raise ValueError("received control request differs from observed call")
        previous = self.control_requests.get(request_id)
        row = {"request_id": request_id, "obligation_id": payload["self_check_id"], "payload_sha256": fingerprint, "receipt_id": receipt_id}
        if previous and previous != row: raise ValueError("control request identity reused")
        self.control_requests[request_id] = row
        self.self_check_call_ids.update(matching)
        return {**row, "call_ids": matching}

    def register_self_check_checkpoint(self, sha256: str) -> None:
        """Register the response's actual artifact before the next file poll."""
        if not is_sha256(sha256):
            raise ValueError("self-check checkpoint requires its actual SHA-256")
        if sha256 in self.seen_checkpoints and sha256 not in self.self_check_checkpoints:
            raise ValueError("checkpoint already counted; response lineage must precede file polling")
        self.self_check_checkpoints.add(sha256)

    def record_safe_boundary(self, receipt_id: str, *, call_ids: list[str] = ()) -> list[dict]:
        """Called only for a validated control receipt, not arbitrary CLI text."""
        if not isinstance(receipt_id, str) or not receipt_id:
            raise ValueError("safe boundary needs a control receipt")
        when = self.clock()
        self.safe_boundary_ids.add(receipt_id)
        for call_id in call_ids:
            if call_id in self.pending_tools:
                self.pending_tools[call_id]["safe_boundary"] = True
        updates = []
        for obligation in self.obligations.values():
            if obligation["status"] == "open" and obligation["response_availability"] == "awaiting_safe_boundary":
                obligation["response_availability"] = "available"
                obligation["boundary_receipt_ref"] = receipt_id
                obligation["deadline_offset_ms"] = (None if self.response_window_ms is None
                    else _offset_ms(self.started, when) + self.response_window_ms)
                updates.append(deepcopy(obligation))
        self._hold_deadlines(when)
        return updates

    def _research_call_running(self) -> bool:
        """An observed research call is in flight: not a control call and not reported at a safe boundary."""
        control = self.self_check_call_ids | self.boundary_call_ids | self.control_calls.keys()
        return any(not row["safe_boundary"] and call_id not in control for call_id, row in self.pending_tools.items())

    def _hold_deadlines(self, when: float) -> None:
        """Stop each open response deadline while research calls run; resume it when they have all ended.

        A worker busy in a tool call cannot read or answer the request, so the
        time a hold lasts is added to the deadline. A call that starts after the
        deadline has passed does not hold it.
        """
        offset, running = _offset_ms(self.started, when), self._research_call_running()
        for obligation in self.obligations.values():
            deadline = obligation["deadline_offset_ms"]
            if obligation["status"] != "open" or deadline is None:
                continue
            if running and _HELD not in obligation and offset <= deadline:
                obligation[_HELD] = offset
            elif not running and _HELD in obligation:
                obligation["deadline_offset_ms"] = deadline + offset - obligation.pop(_HELD)

    def stored_obligations(self, identifiers=None) -> dict:
        """Copies of the obligations (all, or ``identifiers``) as ENGINE saves them, storage-checked."""
        return {oid: _stored("self_check_obligations", deepcopy(self.obligations[oid]))
                for oid in (self.obligations if identifiers is None else identifiers)}

    def set_execution_status(self, status: str) -> None:
        if status not in {"running", "stopping", "ended"}:
            raise ValueError("unsupported live execution status")
        if self.execution_status == "ended" and status != "ended":
            raise ValueError("ended execution cannot restart its observation clock")
        self.execution_status = status

    def _miss(self, obligation: dict, reason: str) -> None:
        if obligation.get("missed_reason"):
            return
        obligation["missed_reason"] = reason
        self.pending_records.append({"kind": "self_check_missed", "execution_id": self.execution_id,
            "obligation_id": obligation["id"], "reason": reason, "observed_at": now(),
            "followup": {"kind": "operational_review_due", "trigger": reason,
                "next_owner": "operational_review", "basis_refs": [obligation["id"]]}})

    def _changed_checkpoint(self) -> dict:
        """Read the checkpoint unless the settled bytes of a valid read are unchanged.

        Only a valid read is remembered: an invalid one can become valid when
        its named evidence appears, so it is read again.
        """
        try:
            mark = file_fingerprint(self.workspace / "checkpoint.json")
        except OSError:
            mark = None
        if mark is not None and mark == self.checkpoint_mark:
            return {"status": "unchanged"}
        checkpoint = read_checkpoint(self.workspace)
        self.checkpoint_mark = (mark if checkpoint["status"] == "valid" and mark is not None
                                and fingerprint_settled(mark) else None)
        return checkpoint

    def _rule_file_events(self) -> list[dict]:
        path = self.workspace / "observation-rules.json"
        if not path.exists(): return []
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(self.workspace.resolve()):
                raise ValueError("observation rules must stay in workspace")
            # A settled, unchanged fingerprint names the bytes this tracker already judged.
            mark = file_fingerprint(path)
            if mark == self.rule_file_mark: return []
            raw = read_bytes_shared(path)
            digest = hashlib.sha256(raw).hexdigest()
            self.rule_file_mark = mark if fingerprint_settled(mark) and file_fingerprint(path) == mark else None
            if digest == self.rule_proposal_digest: return []
            self.rule_proposal_digest = digest
            if len(raw) > RULES_MAX_BYTES: raise ValueError("observation rules exceed 64 KiB")
            proposal = strict_json_loads(raw.decode("utf-8-sig"))
            validate_rule_proposal(proposal, current_revision=self.rule_revision)
            raise ValueError("rule replacement requires rule_proposal in a valid self-check response")
        except (ValueError, TypeError, OSError, UnicodeError, json.JSONDecodeError) as error:
            reason = f"{type(error).__name__}: {error}"
            return [{"kind": "observation_rules_rejected", "execution_id": self.execution_id,
                     "proposal_sha256": self.rule_proposal_digest, "active_revision": self.rule_revision,
                     "active_rules_sha256": self.rules_digest, "reason": reason,
                     "worker_feedback": worker_feedback({"kind": "observation_rules_rejected", "reason": reason,
                         "active_revision": self.rule_revision, "active_rules_sha256": self.rules_digest,
                         "previous_rules_preserved": True, "next_owner": "worker"}),
                     "next_owner": "worker", "observed_at": now()}]

    def _replace_rules(self, proposal: dict) -> dict:
        before = self.rules_digest
        try:
            rules = validate_rule_proposal(proposal, current_revision=self.rule_revision)
            if self.rule_bindings is not None:
                rules = validate_execution_rules(rules, bindings=self.rule_bindings, execution_id=self.execution_id)
            digest = hashlib.sha256(_raw_json(rules).encode()).hexdigest()
            changed = digest != before
            if changed:
                self.rules, self.rules_digest, self.rule_revision = rules, digest, self.rule_revision + 1
            result = {"kind": "observation_rules_accepted" if changed else "observation_rules_unchanged",
                      "previous_rules_sha256": before, "rules": deepcopy(self.rules)}
        except (ValueError, TypeError) as error:
            result = {"kind": "observation_rules_rejected", "reason": str(error), "previous_rules_preserved": True}
        result.update(execution_id=self.execution_id, active_revision=self.rule_revision,
                      active_rules_sha256=self.rules_digest, observed_at=now())
        result["worker_feedback"] = {key: value for key, value in result.items() if key in WORKER_FEEDBACK_FIELDS}
        return result

    def _snapshot(self) -> dict:
        # Each operator has one source (OPERATORS), so one flat snapshot is unambiguous.
        return {"completed_call_ids": sorted(self.completed_call_ids),
                "safe_boundary_ids": sorted(self.safe_boundary_ids), "counters": dict(self.counters),
                "iterations": dict(self.iterations), "checkpoint_counts": {self.execution_id: self.checkpoint_count},
                "observed_at": now()}

    def _self_check_obligation(self, due: list[dict], when: float) -> dict:
        fingerprint = json.dumps({"execution_id": self.execution_id, "revision": self.rule_revision, "due": due}, ensure_ascii=False, sort_keys=True)
        identifier = "SC-" + hashlib.sha256(fingerprint.encode()).hexdigest()[:20]
        if identifier in self.obligations: return self.obligations[identifier]
        opened = _offset_ms(self.started, when)
        available = not any(not details["safe_boundary"] for details in self.pending_tools.values())
        obligation = {"kind": "self_check_due", "id": identifier, "execution_id": self.execution_id,
                      "rule_revision": self.rule_revision, "due": due, "opened_offset_ms": opened,
                      "rules_sha256": self.rules_digest, "snapshot": self._snapshot(),
                      "consumed_boundaries": dict(self.consumed_rules),
                      "response_availability": "available" if available else "awaiting_safe_boundary",
                      "deadline_offset_ms": None if self.response_window_ms is None or not available else opened + self.response_window_ms,
                      "status": "open", "observed_at": now()}
        self.obligations[identifier] = obligation
        return obligation

    def record_self_check_response(self, response: dict, *, available_evidence_refs: set[str] | None = None,
                                   receipt_id: str | None = None) -> dict:
        now_offset = _offset_ms(self.started, self.clock())
        obligation_id = response.get("obligation_id") if isinstance(response, dict) else None
        obligation = self.obligations.get(obligation_id) if isinstance(obligation_id, str) else None
        errors = []
        try:
            # The one response check the worker's sender also runs (이음새-정본.md §6).
            if self_check_response_errors(response):
                raise ValueError("self-check response does not match its schema")
            _json_safe({key: value for key, value in response.items() if key != "rule_proposal"})
        except (ValueError, TypeError):
            errors.append("invalid_response_schema")
        if obligation is None: errors.append("unknown_obligation")
        if self.execution_status != "running": errors.append("execution_not_running")
        if obligation is not None:
            if obligation["status"] != "open": errors.append("obligation_not_open")
            if response.get("execution_id") != self.execution_id: errors.append("execution_mismatch")
            if response.get("rule_revision") != obligation["rule_revision"]: errors.append("revision_mismatch")
            if obligation["response_availability"] != "available": errors.append("response_boundary_unconfirmed")
            if _deadline_passed(obligation, now_offset):
                errors.append("response_deadline_passed")
            if obligation.get("missed_reason"): errors.append(obligation["missed_reason"])
            calls = [cid for cid, row in self.control_calls.items() if row["obligation_id"] == obligation_id]
            if calls and not any(receipt_id is not None and self.control_requests.get(self.control_calls[cid]["request_id"], {}).get("receipt_id") == receipt_id
                                 for cid in calls):
                errors.append("control_request_unconfirmed")
            bound = [row for row in self.control_requests.values() if receipt_id is not None and row["receipt_id"] == receipt_id]
            if bound:
                fingerprint = hashlib.sha256(_raw_json({"self_check_id": obligation_id, "response": response}).encode()).hexdigest()
                if not any(row["payload_sha256"] == fingerprint for row in bound):
                    errors.append("control_response_mismatch")
        if not errors:
            # The schema has already fixed each row's fields, status and reference lists.
            results = response["rule_results"]
            expected = {row["rule_id"]: row for row in obligation["due"]}
            received = [row["rule_id"] for row in results]
            if len(received) != len(set(received)) or set(received) != set(expected): errors.append("rule_coverage_mismatch")
            for row in results:
                required = set(expected.get(row["rule_id"], {}).get("required_evidence", []))
                supplied, declared_missing = set(row["evidence_refs"]), set(row["missing_evidence_refs"])
                actual_missing = required - supplied
                if row["status"] == "indeterminate":
                    if declared_missing != actual_missing: errors.append("indeterminate_evidence_mismatch")
                elif actual_missing or declared_missing: errors.append("required_evidence_missing")
                if available_evidence_refs is None: errors.append("evidence_currentness_unverified")
                elif not supplied.issubset(available_evidence_refs): errors.append("evidence_not_current")
        record = {"kind": "self_check_rejected" if errors else "self_check_received",
                  "id": f"SR-{self.execution_id}-{self.response_count + 1}", "receipt_ref": receipt_id,
                  "execution_id": self.execution_id,
                  "obligation_id": obligation_id if isinstance(obligation_id, str) else None,
                  "response_json": _raw_json(response),
                  "received_offset_ms": now_offset, "observed_at": now()}
        if errors:
            record.update(errors=sorted(set(errors)), followup={"kind": "operational_review_due",
                "trigger": "self_check_response_defect", "next_owner": "operational_review",
                "basis_refs": [record["id"]] + ([obligation["id"]] if obligation else [])})
            record["worker_feedback"] = worker_feedback({"kind": "self_check_rejected", "errors": sorted(set(errors)),
                "obligation_id": obligation_id if isinstance(obligation_id, str) else None, "next_owner": "worker"})
        else:
            obligation["status"] = "answered"
            obligation["response_ref"] = record["id"]
            statuses = {row["status"] for row in response["rule_results"]}
            progress = response["progress"]
            if progress == "progress": self.no_progress_count = 0
            elif progress == "no_progress": self.no_progress_count += 1
            trigger = ("self_check_defect" if "defect" in statuses else "self_check_indeterminate" if "indeterminate" in statuses
                       else "contract_mismatch" if progress == "contract_mismatch" else
                       "repeated_no_progress" if self.no_progress_limit is not None and self.no_progress_count >= self.no_progress_limit else None)
            if trigger is None:
                record["followup"] = {"kind": "continue", "next_owner": "engine"}
            else:
                record["followup"] = {"kind": "operational_review_due", "next_owner": "operational_review",
                                      "trigger": trigger,
                                      "basis_refs": [obligation["id"], obligation["response_ref"]]}
            self.last_self_check_offset_ms = now_offset
            self.next_self_check_offset_ms = None if self.max_self_check_interval_ms is None else now_offset + self.max_self_check_interval_ms
            record.update(next_self_check_offset_ms=self.next_self_check_offset_ms, no_progress_count=self.no_progress_count)
            if "rule_proposal" in response:
                record["rule_update"] = self._replace_rules(response["rule_proposal"])
        self.response_count += 1
        return _stored("self_check_responses", deepcopy(record))

    def observe(self, event: dict, *, source: dict, evaluate=True, live=True) -> list[dict]:
        """Apply one stream row (or a tick at ``source``'s offset) received as ``source`` describes.

        ``source`` is the runner batch's row coordinate and receipt time
        (``ObservationBatch.source``); a tick carries the batch's end offset.
        """
        when, emitted = source['received_monotonic'], []
        if when < self.last_clock:
            return [{"kind": "observation_clock_error", "execution_id": self.execution_id,
                     "reason": "monotonic clock regressed", "next_owner": "engine"}]
        self.last_clock = when
        if self.execution_status != "running" and live:
            return []
        self.observation_source = source
        self.live_observation = live and self.execution_status == 'running'
        try: self._ingest_event(event, when)
        except ValueError as error:
            emitted.append({"kind": "observation_input_rejected", "execution_id": self.execution_id,
                            "reason": str(error), "next_owner": "adapter", "observed_at": now(),
                            "followup": {"kind": "operational_review_due", "trigger": "observation_error", "next_owner": "operational_review"}
                            if self.mode != "deadline_only" else None})
        self._hold_deadlines(when)
        if event.get("type") != "tick": emitted.append(self.fact("observation_fact", event, when))
        if not evaluate or not self.live_observation:
            # Replaying a terminated stream preserves its order and facts; it
            # cannot start a new wall clock, poll a future checkpoint or oblige
            # an already terminated worker to answer a new live request.
            emitted.extend(self.pending_records)
            self.pending_records.clear()
            return emitted
        emitted.extend(self._rule_file_events())
        checkpoint = self._changed_checkpoint()
        if checkpoint["status"] == "valid" and checkpoint["sha256"] not in self.seen_checkpoints:
            self.seen_checkpoints.add(checkpoint["sha256"])
            self_check_only = checkpoint["sha256"] in self.self_check_checkpoints
            if not self_check_only: self.checkpoint_count += 1
            progress = checkpoint["value"]
            try:
                if not self_check_only: self._merge_monotonic(self.counters, progress.get("counters"), "checkpoint counters")
                if not self_check_only and "iteration" in progress:
                    self._merge_monotonic(self.iterations, {self.execution_id: progress["iteration"]}, "checkpoint iterations")
            except ValueError as error:
                emitted.append({"kind": "checkpoint_observation_rejected", "execution_id": self.execution_id,
                                "reason": str(error), "observed_at": now()})
            emitted.append({"kind": "checkpoint", "execution_id": self.execution_id, **checkpoint})
        if self.research_self_checks:
            snapshot = self._snapshot()
            unavailable = []
            # A source capability is not a measurement already produced at
            # execution start. Use the admitted first observation interval.
            measurement_due = (self.max_self_check_interval_ms is None or
                _offset_ms(self.started, when) >= self.max_self_check_interval_ms)
            for rule in self.rules:
                operator, subject = rule["operator"], rule["subject"]["id"]
                missing = ((operator == "counter_gte" and subject not in snapshot["counters"]) or
                           (operator == "iteration_gte" and subject not in snapshot["iterations"]))
                if missing and measurement_due and rule["id"] not in self.reported_unavailable:
                    unavailable.append(rule["id"])
            if unavailable:
                self.reported_unavailable.update(unavailable)
                emitted.append({"kind": "observation_unavailable", "execution_id": self.execution_id,
                    "rule_ids": unavailable, "reason": "required observation signal has not been measured", "observed_at": now(),
                    "followup": {"kind": "operational_review_due", "trigger": "observation_unavailable", "next_owner": "operational_review"}})
            due = evaluate_rules(self.rules, snapshot, consumed_boundaries=self.consumed_rules)
            if self.next_self_check_offset_ms is not None and _offset_ms(self.started, when) >= self.next_self_check_offset_ms:
                rule_ids = {rule["id"] for rule in self.rules}
                maximum_id = "@maximum_interval"
                suffix = 0
                while maximum_id in rule_ids:
                    suffix += 1
                    maximum_id = f"@maximum_interval:{suffix}"
                due.append({"rule_id": maximum_id, "operator": "wall_time_reached", "subject": self.execution_id,
                    "basis": {"source": "selected_profile" if self.profile_ref else "admitted_settings", "unit": "milliseconds"},
                    "required_evidence": sorted({ref for rule in self.rules for ref in rule["required_evidence"]}),
                    "value": _offset_ms(self.started, when), "boundary": self.next_self_check_offset_ms,
                    "boundary_key": f"maximum:{self.last_self_check_offset_ms}", "next_boundary": None})
                self.next_self_check_offset_ms = None
            if due:
                for item in due: self.consumed_rules[item["boundary_key"]] = item["boundary"]
                obligation = self._self_check_obligation(due, when)
                if obligation["status"] == "open": emitted.append(deepcopy(obligation))
            for obligation in self.obligations.values():
                if obligation["status"] == "open" and _deadline_passed(obligation, _offset_ms(self.started, when)):
                    self._miss(obligation, "response_deadline_passed")
        if self.mode != "deadline_only":
            for call_id, details in self.pending_tools.items():
                window = details["review_window_ms"]
                if window is None and not details["review_due"]:
                    details["review_due"] = True
                    emitted.append({"kind": "observation_capability_missing", "execution_id": self.execution_id,
                        "call_id": call_id, "reason": "selected profile has no tool_review_window_seconds",
                        "next_owner": "profile_admission"})
                if window is not None and _offset_ms(details["started"], when) >= window and not details["review_due"] and not details["safe_boundary"]:
                    details["review_due"] = True
                    emitted.append({"kind": "tool_review_due", "execution_id": self.execution_id,
                                    "call_id": call_id, "window_ms": window,
                                    "elapsed_ms": _offset_ms(details["started"], when),
                                    "basis": {"source": "selected_profile" if self.profile_ref else "admitted_settings", "profile_ref": self.profile_ref,
                                              "field": "tool_review_window_seconds", "unit": "milliseconds"},
                                    "observed_at": now()})
            if self.mode == "periodic" and self.periodic_interval_ms is not None:
                if _offset_ms(self.last_review, when) >= self.periodic_interval_ms:
                    self.last_review = when
                    emitted.append({"kind": "periodic_review_due", "execution_id": self.execution_id,
                                    "interval_ms": self.periodic_interval_ms,
                                    "basis": {"source": "selected_profile" if self.profile_ref else "admitted_settings", "profile_ref": self.profile_ref,
                                              "field": "observation_interval_seconds", "unit": "milliseconds"},
                                    "observed_at": now()})
            for review in self.explicit_reviews.values():
                if not review["fired"] and _utc(now(), "now") >= _utc(review["at"], "review at"):
                    review["fired"] = True
                    emitted.append({"kind": "explicit_review_due", "execution_id": self.execution_id,
                                    **{key: review[key] for key in ("review_id", "reason", "basis_ref", "at")},
                                    "observed_at": now()})
        if (self.config.get("checkpoint_expected") and not self.checkpoint_reminded and self.checkpoint_count == 0 and
                self.periodic_interval_ms is not None and _offset_ms(self.started, when) >= self.periodic_interval_ms):
            self.checkpoint_reminded = True
            emitted.append({"kind": "checkpoint_reminder_due", "execution_id": self.execution_id,
                            "checkpoint_status": checkpoint["status"], "observed_at": now()})
        emitted.extend(self.pending_records)
        self.pending_records = []
        return emitted

    def schedule_review(self, review_id: str, *, at: str, reason: str, basis_ref: str) -> None:
        """ENGINE calls after accepting a current continue disposition."""
        if self.mode == "deadline_only":
            raise ValueError("deadline_only cannot schedule recursive operational review")
        _utc(at, "review at")
        if any(not isinstance(value, str) or not value for value in (review_id, reason, basis_ref)):
            raise ValueError("explicit review requires ID, reason and accepted disposition reference")
        review = {"review_id": review_id, "at": at, "reason": reason, "basis_ref": basis_ref, "fired": False}
        previous = self.explicit_reviews.get(review_id)
        if previous and any(previous[key] != review[key] for key in ("at", "reason", "basis_ref")):
            raise ValueError("review ID cannot be reused with a different schedule")
        if previous is None: self.explicit_reviews[review_id] = review

    def acknowledge_review(self, *, observation_refs: list[str]) -> None:
        if not observation_refs or any(not isinstance(ref, str) or not ref for ref in observation_refs):
            raise ValueError("review acknowledgement needs published observation references")
        self.no_progress_count = 0
        self.last_review = self.clock()


def self_check_feedback(obligation: dict) -> dict:
    if not isinstance(obligation, dict) or obligation.get("kind") != "self_check_due":
        raise ValueError("self-check feedback requires a self_check_due obligation")
    due = obligation.get("due")
    if not isinstance(obligation.get("id"), str) or not isinstance(obligation.get("rule_revision"), int) or not isinstance(due, list) or not due:
        raise ValueError("malformed self-check obligation")
    return worker_feedback({"obligation_id": obligation["id"], "execution_id": obligation["execution_id"],
            "rule_revision": obligation["rule_revision"],
            "due": [{key: item[key] for key in ("rule_id", "operator", "subject", "required_evidence")} for item in due],
            "deadline_offset_ms": obligation.get("deadline_offset_ms")})


def self_check_request(obligation: dict) -> dict:
    """The one request object the transport delivers and the tracker hashes."""
    return {"self_check_id": obligation["id"], "execution_id": obligation["execution_id"],
            "payload": self_check_feedback(obligation)}


def _control_root(workspace: Path) -> Path:
    root = Path(workspace)
    control = root if root.name == ".control" else root / ".control"
    control.mkdir(parents=True, exist_ok=True)
    return control


def publish_worker_feedback(workspace: Path, feedback: dict) -> None:
    """Deliver only a public feedback projection, AFTER ENGINE's state CAS.

    This file is a delivery surface. Immutable facts/receipts remain the
    authoritative history and allow delivery to be retried after a crash.
    """
    encoded = json.dumps(_json_safe(worker_feedback(feedback)), ensure_ascii=False)
    control = _control_root(workspace)
    destination = safe_path(control, "observation-feedback.json")
    write_bytes_atomic(destination, encoded.encode("utf-8"))


def write_checkpoint_reminder(workspace: Path) -> bool:
    destination = _control_root(workspace) / "observation-feedback.json"
    if destination.exists(): return False
    reminder = {"source": "executor", "decision": "checkpoint",
                "reason": "실행 시작 뒤 관찰 간격이 지나도록 유효한 checkpoint.json이 관찰되지 않았다. 다음 연구 행동 전에 "
                          "「공통 실행」의 체크포인트 형식(current_claim, evidence_paths, attempts, remaining_work, next_step, "
                          "progress_state)으로 지금까지 확인한 사실과 그 근거 파일, 남은 작업을 기록한다. "
                          "이 알림은 실행기가 기계적으로 보낸 것이며 진전이나 실패의 판정이 아니다."}
    write_bytes_atomic(destination, json.dumps(reminder, ensure_ascii=False).encode("utf-8"))
    return True


def request_checkpoint(workspace: Path, reason: str, *, immediate: bool, deadline: str) -> dict:
    request = {"reason": reason, "immediate": immediate, "deadline": deadline,
               "instruction": "Preserve only already obtained facts in checkpoint.json and finish. Do not start new research or external actions."}
    destination = _control_root(workspace) / "stop-request.json"
    write_bytes_atomic(destination, json.dumps(request, ensure_ascii=False).encode("utf-8"))
    return request


def preserve_checkpoint(workspace: Path, *, artifact_prefix: str, max_bytes: int, previous=None):
    """Capture final checkpoint bytes independently of submitted output selection.

    A checkpoint already observed owns its evidence version. A later read of
    the same JSON must not substitute changed evidence files for that version.
    Invalid or unpreservable final reads retain the last valid sealed record.
    """
    checkpoint = read_checkpoint(workspace)
    prior = previous if previous and previous.get('kind') == 'worker_checkpoint' and previous.get('artifact_ref') else None
    if checkpoint['status'] == 'valid':
        if prior and prior['sha256'] == checkpoint['sha256']:
            return deepcopy(prior), {}
        raw = checkpoint['raw']
        if len(raw) <= max_bytes:
            reference = artifact_prefix + '/checkpoint.json'
            files, omitted = capture_checkpoint_files(workspace, checkpoint['value'], max_bytes=max_bytes - len(raw))
            artifacts = {reference: raw}
            evidence = []
            for name, data in files.items():
                path = artifact_prefix + '/evidence/' + name
                artifacts[path] = data
                evidence.append({'path': name, 'artifact_ref': path,
                    'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
            return {'kind': 'worker_checkpoint', 'checkpoint': checkpoint['value'],
                    'sha256': checkpoint['sha256'], 'bytes': len(raw), 'artifact_ref': reference,
                    'observed_at': checkpoint['observed_at'], 'evidence_files': evidence,
                    'evidence_omitted': omitted}, artifacts
        checkpoint = {'status': 'not_preserved', 'error': 'checkpoint exceeds artifact byte limit'}
    final = {'kind': 'observed_partial_state', 'checkpoint_status': checkpoint['status'],
             'messages': [], 'workspace': str(workspace),
             'limitation': 'No complete final worker checkpoint was preserved; infer no unreported result.'}
    if checkpoint.get('error'):
        final['reason'] = checkpoint['error']
    return ({**deepcopy(prior), 'final_observation': final} if prior else final), {}
