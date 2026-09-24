"""Version-5 observation facts, self-check obligations, and review triggers."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import time
from typing import Any

from .context_store import _excluded, _safe_path

CHECKPOINT_MAX_BYTES = 4 * 1024 * 1024
RULES_MAX_BYTES = 65536
OBSERVATION_OPERATORS = frozenset({
    "event_recorded", "counter_gte", "iteration_gte", "checkpoint_count_gte",
    "active_duration_gte", "wall_time_reached", "tool_call_completed", "safe_boundary_recorded",
})
_OPERATOR_SUBJECTS = {
    "event_recorded": "event", "counter_gte": "counter", "iteration_gte": "iteration",
    "checkpoint_count_gte": "checkpoint", "active_duration_gte": "execution",
    "wall_time_reached": "clock", "tool_call_completed": "tool_call",
    "safe_boundary_recorded": "safe_boundary",
}
_RULE_FIELDS = {"id", "operator", "subject", "basis", "threshold", "repeat_interval", "required_evidence"}
OBSERVATION_SOURCES = {
    "checkpoint": {"counter_gte", "iteration_gte", "checkpoint_count_gte"},
    "execution_events": {"event_recorded", "counter_gte", "iteration_gte"},
    "adapter_calls": {"tool_call_completed"},
    "control_receipts": {"safe_boundary_recorded"},
    "adapter_active_intervals": {"active_duration_gte"},
    "clock": {"wall_time_reached"},
}


def observation_rule_contract() -> list[dict]:
    """Return the sealed, actually-produced signal kinds available to a profile.

    A profile names signal kinds only. Counter and event names are local to a
    particular execution and are checked against that execution's snapshot,
    rather than being guessed while a reusable profile is authored.
    """
    return [
        {"source": source, "operator": operator,
         "subject_kind": _OPERATOR_SUBJECTS[operator],
         "unit": ("UTC" if operator == "wall_time_reached" else
                  "milliseconds" if operator == "active_duration_gte" else "count")}
        for source, operators in OBSERVATION_SOURCES.items()
        for operator in sorted(operators)
    ]

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

_TEXT = {"type": "string", "minLength": 1}
_REFS = {"type": "array", "items": _TEXT, "uniqueItems": True}
SELF_CHECK_RESPONSE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["obligation_id", "execution_id", "rule_revision", "rule_results", "progress", "attempts", "next_method"],
    "properties": {
        "obligation_id": _TEXT, "execution_id": _TEXT,
        "rule_revision": {"type": "integer", "minimum": 0},
        "progress": {"enum": ["progress", "no_progress", "contract_mismatch"]},
        "attempts": {"type": "array", "items": _TEXT, "minItems": 1}, "next_method": _TEXT,
        "rule_results": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["rule_id", "status", "evidence_refs", "missing_evidence_refs", "reason"],
            "properties": {"rule_id": _TEXT, "status": {"enum": ["normal", "defect", "indeterminate"]},
                "evidence_refs": _REFS, "missing_evidence_refs": _REFS, "reason": _TEXT}}},
        "rule_proposal": {},
    },
}


def validate_rule_proposal(proposal: dict, *, current_revision: int,
                           allowed_subjects: set[str] | None = None) -> list[dict]:
    if not isinstance(proposal, dict) or set(proposal) != {"current_revision", "reason", "rules"}:
        raise ValueError("rule proposal requires current_revision, reason and rules")
    if type(proposal["current_revision"]) is not int or proposal["current_revision"] != current_revision:
        raise ValueError("rule proposal revision is stale")
    if not isinstance(proposal["reason"], str) or not proposal["reason"].strip():
        raise ValueError("rule proposal needs a reason")
    return validate_rules(proposal["rules"], allowed_subjects=allowed_subjects)


def _json_safe(value: Any) -> Any:
    from .repository import canonical_json
    return json.loads(canonical_json(value))


def _raw_json(value: Any) -> str:
    # Provider payloads can contain fractional metrics. Keep their original
    # numeric semantics as JSON text, outside the integer-only state tree.
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)


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


def validate_task_rules(rules):
    """Reusable task rules cannot name a future or previous execution."""
    checked = validate_rules(rules)
    for rule in checked:
        if rule['subject']['kind'] in {'execution', 'checkpoint'} and rule['subject']['id'] != '$execution':
            raise ValueError('task rule execution/checkpoint subject must be $execution')
    return checked


def bind_task_rules(rules, execution_id):
    checked = validate_task_rules(rules)
    for rule in checked:
        if rule['subject']['kind'] in {'execution', 'checkpoint'}:
            rule['subject']['id'] = execution_id
    return checked


def validate_rule_preparation(action, extensions, tasks):
    """The producer and receiver enforce the same assigned edition and coverage."""
    targets = action.get('observation_rule_targets', {})
    if 'observation_rule_targets' not in action:
        return {}
    from .model_policy import assessment_basis
    for tid, basis in targets.items():
        task = tasks.get(tid)
        if (not task or task.get('status') in {'completed', 'closed'}
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
        if rule['subject']['kind'] in {'execution', 'checkpoint'}:
            if rule['subject']['id'] not in {'$execution', execution_id}:
                raise ValueError('persisted rule refers to another execution')
            rule['subject']['id'] = '$execution'
    return validate_task_rules(checked)


def observation_settings_errors(profile: dict) -> list[dict]:
    """Check profile settings without requiring a not-yet-authored task's rules."""
    settings = profile['observation']['settings']
    required = []
    if profile['observation']['mode'] != 'deadline_only':
        required.extend(['tool_review_window_seconds', 'observation_interval_seconds'])
    if profile['role'] == 'research_work':
        required.append('self_check_response_window_seconds')
    errors = []
    for field in required:
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
    return {**settings, "observation_contract_version": 5,
            "observation_mode": profile["observation"]["mode"],
            "observation_profile_ref": reference, "research_self_checks": research,
            "observation_rule_bindings": deepcopy(profile["observation"].get("rule_bindings", [])),
            "observation_rules": deepcopy(initial_self_check_rules or []),
            "self_check_revision": 0, "no_progress_limit": no_progress_limit,
            "checkpoint_expected": research}


def _utc(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(field + " must be an ISO UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(field + " must be an ISO UTC timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(field + " must include a timezone")
    return parsed.astimezone(timezone.utc)


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_rules(rules: list[dict], *, allowed_subjects: set[str] | None = None,
                   allow_empty: bool = False) -> list[dict]:
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
        if operator not in OBSERVATION_OPERATORS:
            raise ValueError("unsupported observation operator")
        subject, basis = rule.get("subject"), rule.get("basis")
        if not isinstance(subject, dict) or set(subject) != {"kind", "id"}:
            raise ValueError("rule subject must contain exactly kind and id")
        if subject.get("kind") != _OPERATOR_SUBJECTS[operator] or not isinstance(subject.get("id"), str) or not subject["id"]:
            raise ValueError("rule subject is incompatible with its operator")
        if allowed_subjects is not None and subject["id"] not in allowed_subjects:
            raise ValueError("rule subject is not available to this execution")
        if (not isinstance(basis, dict) or set(basis) != {"source", "unit"} or
                any(not isinstance(basis.get(key), str) or not basis[key] for key in ("source", "unit"))):
            raise ValueError("rule basis must contain nonempty source and unit")
        evidence = rule.get("required_evidence")
        if (not isinstance(evidence, list) or not evidence or
                any(not isinstance(ref, str) or not ref for ref in evidence) or len(evidence) != len(set(evidence))):
            raise ValueError("rule required_evidence must be a nonempty unique string list")
        if operator == "wall_time_reached":
            _utc(rule.get("threshold"), "wall_time_reached threshold")
            if basis["unit"] != "UTC" or "repeat_interval" in rule:
                raise ValueError("wall_time_reached requires UTC and cannot repeat")
            continue
        threshold = rule.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
            raise ValueError("rule threshold must be a positive integer")
        interval = rule.get("repeat_interval")
        if "repeat_interval" in rule and (isinstance(interval, bool) or not isinstance(interval, int) or interval < 1):
            raise ValueError("repeat_interval must be a positive integer")
        if operator in {"event_recorded", "tool_call_completed", "safe_boundary_recorded"} and (threshold != 1 or interval is not None):
            raise ValueError(operator + " is a one-time recorded event")
        if operator == "active_duration_gte" and basis["unit"] != "milliseconds":
            raise ValueError("active_duration_gte uses milliseconds")
        if operator != "active_duration_gte" and basis["unit"] != "count":
            raise ValueError(operator + " uses count")
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
    checked, identities = [], set()
    for binding in bindings:
        if not isinstance(binding, dict):
            raise ValueError("invalid profile observation binding")
        if set(binding) == {"source", "operator", "subject_kind", "unit"}:
            source, operator = binding["source"], binding["operator"]
            subject_kind, unit = binding["subject_kind"], binding["unit"]
            if (not isinstance(source, str) or not isinstance(operator, str) or
                    not isinstance(subject_kind, str) or not isinstance(unit, str) or
                    operator not in OBSERVATION_SOURCES.get(source, set()) or
                    _OPERATOR_SUBJECTS.get(operator) != subject_kind or
                    unit != ("UTC" if operator == "wall_time_reached" else
                             "milliseconds" if operator == "active_duration_gte" else "count")):
                raise ValueError("profile observation contract has no implemented producer for its signal kind")
            normalized = {"source": source, "operator": operator,
                          "subject_kind": subject_kind, "unit": unit}
        else:
            raise ValueError("invalid profile observation binding")
        identity = _raw_json(normalized)
        if identity in identities:
            raise ValueError("profile observation contract repeats a signal kind")
        identities.add(identity)
        checked.append(normalized)
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
        if execution_id is not None and subject["kind"] in {"execution", "checkpoint"} and subject["id"] != execution_id:
            raise ValueError("rule subject belongs to a different execution")
        def matches(binding):
            return (binding["operator"] == rule["operator"] and binding["source"] == rule["basis"]["source"] and
                    binding["unit"] == rule["basis"]["unit"] and binding["subject_kind"] == subject["kind"])
        if not any(matches(binding) for binding in bindings):
            raise ValueError("rule has no registered observable subject/source/unit: " + rule["id"])
    return checked


def evaluate_rules(rules: list[dict], snapshot: dict, *, consumed_boundaries: dict[str, int] | None = None) -> list[dict]:
    """Evaluate all rules against one accumulated observation snapshot."""
    validate_rules(rules, allow_empty=True)
    consumed = consumed_boundaries or {}
    events = set(snapshot.get("event_ids", []))
    calls = set(snapshot.get("completed_call_ids", []))
    boundaries = set(snapshot.get("safe_boundary_ids", []))
    counters = snapshot.get("counters", {})
    iterations = snapshot.get("iterations", {})
    checkpoints = snapshot.get("checkpoint_counts", {})
    due = []
    for rule in rules:
        operator, subject = rule["operator"], rule["subject"]["id"]
        if "by_source" in snapshot:
            source = snapshot["by_source"].get(rule["basis"]["source"], {})
            events, calls, boundaries = (set(source.get(key, [])) for key in ("event_ids", "completed_call_ids", "safe_boundary_ids"))
            counters, iterations, checkpoints = (source.get(key, {}) for key in ("counters", "iterations", "checkpoint_counts"))
        else:
            source = snapshot
        if operator == "event_recorded": value = 1 if subject in events else None
        elif operator == "counter_gte": value = counters.get(subject)
        elif operator == "iteration_gte": value = iterations.get(subject)
        elif operator == "checkpoint_count_gte": value = checkpoints.get(subject)
        elif operator == "active_duration_gte": value = source.get("active_duration_ms")
        elif operator == "wall_time_reached":
            observed = source.get("observed_at")
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


def read_checkpoint(workspace: Path) -> dict:
    path = workspace / "checkpoint.json"
    if not path.exists():
        return {"status": "missing"}
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(workspace.resolve()) or path.is_symlink():
            raise ValueError("checkpoint must stay within the execution workspace")
        before = path.stat()
        if before.st_size > CHECKPOINT_MAX_BYTES:
            raise ValueError("checkpoint exceeds the 4 MiB record limit")
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return {"status": "being_written"}
        digest = hashlib.sha256(raw).hexdigest()
        value = json.loads(raw.decode("utf-8-sig"))
        import jsonschema
        jsonschema.validate(value, CHECKPOINT_SCHEMA)
        for reference in value["evidence_paths"]:
            evidence = _safe_path(workspace, reference)
            relative = Path(reference)
            if (relative.parts[0] != "input" and _excluded(relative)) or not evidence.is_file():
                raise ValueError("checkpoint evidence is unavailable or excluded from preservation: " + reference)
        return {"status": "valid", "value": value, "sha256": digest, "raw": raw, "observed_at": utc_now()}
    except Exception as error:
        return {"status": "invalid", "error": f"{type(error).__name__}: {error}"}


class ObservationTracker:
    """One execution's v5 observation state; persistence remains ENGINE-owned."""

    def __init__(self, execution_id: str, workspace: Path, config: dict, *, clock=time.monotonic):
        if config.get("observation_contract_version", 5) != 5:
            raise ValueError("only observation contract version 5 is supported")
        config = deepcopy(config)
        self.execution_id, self.workspace, self.config, self.clock = execution_id, workspace, config, clock
        self.started = self.last_review = clock()
        self.mode = config.get("observation_mode", "event_driven")
        if self.mode not in {"event_driven", "periodic", "deadline_only"}:
            raise ValueError("unsupported observation mode")
        self.rule_revision = config.get("self_check_revision", 0)
        if isinstance(self.rule_revision, bool) or not isinstance(self.rule_revision, int) or self.rule_revision < 0:
            raise ValueError("self_check_revision must be a nonnegative integer")
        self.research_self_checks = config.get("research_self_checks", self.mode == "event_driven")
        if self.mode == "deadline_only" and (self.research_self_checks or config.get("observation_rules")):
            raise ValueError("deadline_only cannot carry research self-check rules")
        self.allowed_subjects = config.get("observation_subjects")
        self.rules = validate_rules(config.get("observation_rules", []), allowed_subjects=self.allowed_subjects,
                                    allow_empty=not self.research_self_checks)
        self.rule_bindings = config.get("observation_rule_bindings")
        if config.get("observation_profile_ref") or self.rule_bindings is not None:
            self.rules = validate_execution_rules(self.rules, bindings=self.rule_bindings, execution_id=execution_id)
        for rule in self.rules:
            if rule["subject"]["kind"] in {"execution", "checkpoint"} and rule["subject"]["id"] != execution_id:
                raise ValueError("rule subject belongs to a different execution")
        self.rules_digest = hashlib.sha256(json.dumps(self.rules, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.rule_proposal_digest = None
        self.consumed_rules: dict[str, int] = {}
        self.obligations: dict[str, dict] = {}
        self.responses: list[dict] = []
        self.fact_sequence = 0
        self.checkpoint_count = 0
        self.last_checkpoint = None
        self.seen_checkpoints: set[str] = set()
        self.self_check_checkpoints: set[str] = set()
        self.checkpoint_reminded = False
        self.pending_tools: dict[str, dict] = {}
        self.completed_call_ids: set[str] = set()
        self.event_ids: set[str] = set()
        self.safe_boundary_ids: set[str] = set()
        self.counters: dict[str, int] = {}
        self.iterations: dict[str, int] = {}
        self.checkpoint_counters: dict[str, int] = {}
        self.checkpoint_iterations: dict[str, int] = {}
        self.active_duration_ms = 0
        self.active_observed = False
        self.active_started = None
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
        self.control_calls: dict[str, dict] = {}
        self.control_requests: dict[str, dict] = {}
        self.control_server_name = config.get("control_server_name", "execution_control")
        self.explicit_reviews: dict[str, dict] = {}
        self.pending_records: list[dict] = []
        self.last_clock = self.started
        self.reported_unavailable: set[str] = set()

    def _fact(self, kind: str, event: dict, when: float) -> dict:
        self.fact_sequence += 1
        raw = _raw_json(event)
        return {"kind": kind, "id": f"OF-{self.execution_id}-{self.fact_sequence}",
                "execution_id": self.execution_id, "event_json": raw,
                "event_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "observed_at": utc_now(), "monotonic_offset_ms": _offset_ms(self.started, when)}

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

    def _active_value(self, when: float) -> int:
        return self.active_duration_ms + (0 if self.active_started is None else _offset_ms(self.active_started, when))

    def _ingest_event(self, event: dict, when: float) -> None:
        self._observe_control_calls(event)
        event_type = event.get("type")
        if event.get("execution_id", self.execution_id) != self.execution_id:
            raise ValueError("observation belongs to a different execution")
        counters, iterations = dict(self.counters), dict(self.iterations)
        self._merge_monotonic(counters, event.get("counters"), "counters")
        self._merge_monotonic(iterations, event.get("iterations"), "iterations")
        supplied_active = event.get("active_duration_ms")
        if supplied_active is not None:
            if isinstance(supplied_active, bool) or not isinstance(supplied_active, int) or supplied_active < self._active_value(when):
                raise ValueError("active_duration_ms must be a nondecreasing integer")
            self.active_duration_ms, self.active_started = supplied_active, None
            self.active_observed = True
        self.counters, self.iterations = counters, iterations
        if isinstance(event.get("id"), str): self.event_ids.add(event["id"])
        if event_type == "research_activity_started" and self.active_started is None:
            self.active_started = when
            self.active_observed = True
        elif event_type == "research_activity_finished" and self.active_started is not None:
            self.active_duration_ms, self.active_started = self._active_value(when), None
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
        if call_id not in self.self_check_call_ids and call_id not in self.control_calls:
            for obligation in self.obligations.values():
                if obligation["status"] == "open" and obligation["deadline_offset_ms"] is not None:
                    self._miss(obligation, "research_action_before_response")

    def _complete_call(self, call_id: str) -> None:
        self.pending_tools.pop(call_id, None)
        if call_id not in self.self_check_call_ids and call_id not in self.control_calls:
            self.completed_call_ids.add(call_id)

    def _observe_control_calls(self, event: dict) -> None:
        """Match provider-observed identity and arguments before action accounting."""
        calls = []
        item = event.get("item", {})
        if (event.get("type") in {"item.started", "item.completed"} and isinstance(item, dict)
                and item.get("type") == "mcp_tool_call" and item.get("server") == self.control_server_name):
            calls.append((item.get("id"), item.get("tool"), item.get("arguments")))
        if event.get("type") == "assistant":
            message = event.get("message", {})
            for block in message.get("content", []) if isinstance(message, dict) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    prefix = "mcp__" + self.control_server_name + "__"
                    name = block.get("name", "")
                    if isinstance(name, str) and name.startswith(prefix):
                        calls.append((block.get("id"), name[len(prefix):], block.get("input")))
        for call_id, tool, arguments in calls:
            if not isinstance(call_id, str) or not isinstance(arguments, dict): continue
            if tool == "control_self_check":
                oid = arguments.get("self_check_id")
                payload = {"self_check_id": oid, "response": arguments.get("response")}
                request_id = "self-check-" + oid if isinstance(oid, str) else None
            elif tool == "control_submit" and arguments.get("kind") == "self_check_response":
                payload = arguments.get("payload")
                oid = payload.get("self_check_id") if isinstance(payload, dict) else None
                request_id = arguments.get("request_id")
            else:
                continue
            if not isinstance(oid, str) or oid not in self.obligations or not isinstance(request_id, str): continue
            if payload.get("response") is None and tool == "control_self_check":
                # This installed tool reads the already-issued self-check only.
                self.self_check_call_ids.add(call_id)
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

    def bind_control_request(self, request: dict, *, receipt_id: str) -> dict:
        """ENGINE invokes after checking the actual transport binding and grant.

        Payload equality links either arrival order without trusting a worker's
        declaration that an arbitrary research call is a self-check call.
        """
        if (request.get("kind") != "self_check_response" or request.get("execution_id") != self.execution_id
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

    def register_self_check_calls(self, call_ids: list[str]) -> None:
        """ENGINE supplies actual request/call lineage, never a worker claim."""
        if any(not isinstance(call_id, str) or not call_id for call_id in call_ids):
            raise ValueError("self-check call IDs must be nonempty strings")
        self.self_check_call_ids.update(call_ids)

    def register_self_check_checkpoint(self, sha256: str) -> None:
        """Register the response's actual artifact before the next file poll."""
        if not isinstance(sha256, str) or len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise ValueError("self-check checkpoint requires its actual SHA-256")
        if sha256 in self.seen_checkpoints and sha256 not in self.self_check_checkpoints:
            raise ValueError("checkpoint already counted; response lineage must precede file polling")
        self.self_check_checkpoints.add(sha256)

    def record_safe_boundary(self, receipt_id: str, *, call_ids: list[str] = (), self_check_only: bool = False) -> list[dict]:
        """Called only for a validated control receipt, not arbitrary CLI text."""
        if not isinstance(receipt_id, str) or not receipt_id:
            raise ValueError("safe boundary needs a control receipt")
        when = self.clock()
        if not self_check_only:
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
        return updates

    def set_execution_status(self, status: str) -> None:
        if status not in {"running", "stopping", "ended"}:
            raise ValueError("unsupported live execution status")
        if self.execution_status == "ended" and status != "ended":
            raise ValueError("ended execution cannot restart its observation clock")
        when = self.clock()
        if status != "running" and self.active_started is not None:
            self.active_duration_ms, self.active_started = self._active_value(when), None
        self.execution_status = status

    def _miss(self, obligation: dict, reason: str) -> None:
        if obligation.get("missed_reason"):
            return
        obligation["missed_reason"] = reason
        self.pending_records.append({"kind": "self_check_missed", "execution_id": self.execution_id,
            "obligation_id": obligation["id"], "reason": reason, "observed_at": utc_now(),
            "followup": {"kind": "operational_review_due", "trigger": reason,
                "next_owner": "operational_review", "basis_refs": [obligation["id"]]}})

    def _rule_file_events(self) -> list[dict]:
        path = self.workspace / "observation-rules.json"
        if not path.exists(): return []
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(self.workspace.resolve()):
                raise ValueError("observation rules must stay in workspace")
            raw = path.read_bytes()
            if len(raw) > RULES_MAX_BYTES: raise ValueError("observation rules exceed 64 KiB")
            digest = hashlib.sha256(raw).hexdigest()
            if digest == self.rule_proposal_digest: return []
            self.rule_proposal_digest = digest
            proposal = json.loads(raw.decode("utf-8-sig"))
            validate_rule_proposal(proposal, current_revision=self.rule_revision, allowed_subjects=self.allowed_subjects)
            raise ValueError("rule replacement requires rule_proposal in a valid self-check response")
        except (ValueError, TypeError, OSError, UnicodeError, json.JSONDecodeError) as error:
            reason = f"{type(error).__name__}: {error}"
            return [{"kind": "observation_rules_rejected", "execution_id": self.execution_id,
                     "proposal_sha256": self.rule_proposal_digest, "active_revision": self.rule_revision,
                     "active_rules_sha256": self.rules_digest, "reason": reason,
                     "worker_feedback": {"kind": "observation_rules_rejected", "reason": reason,
                         "active_revision": self.rule_revision, "active_rules_sha256": self.rules_digest,
                         "previous_rules_preserved": True, "next_owner": "worker"},
                     "next_owner": "worker", "observed_at": utc_now()}]

    def _replace_rules(self, proposal: dict) -> dict:
        before = self.rules_digest
        try:
            rules = validate_rule_proposal(proposal, current_revision=self.rule_revision, allowed_subjects=self.allowed_subjects)
            if self.rule_bindings is not None:
                rules = validate_execution_rules(rules, bindings=self.rule_bindings, execution_id=self.execution_id)
            digest = hashlib.sha256(json.dumps(rules, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            changed = digest != before
            if changed:
                self.rules, self.rules_digest, self.rule_revision = rules, digest, self.rule_revision + 1
            result = {"kind": "observation_rules_accepted" if changed else "observation_rules_unchanged",
                      "previous_rules_sha256": before, "rules": deepcopy(self.rules)}
        except (ValueError, TypeError) as error:
            result = {"kind": "observation_rules_rejected", "reason": str(error), "previous_rules_preserved": True}
        result.update(execution_id=self.execution_id, active_revision=self.rule_revision,
                      active_rules_sha256=self.rules_digest, observed_at=utc_now())
        result["worker_feedback"] = {key: value for key, value in result.items() if key not in {"rules", "observed_at"}}
        return result

    def _snapshot(self, when: float) -> dict:
        snapshot = {"event_ids": sorted(self.event_ids), "completed_call_ids": sorted(self.completed_call_ids),
                "safe_boundary_ids": sorted(self.safe_boundary_ids), "counters": dict(self.counters),
                "iterations": dict(self.iterations), "checkpoint_counts": {self.execution_id: self.checkpoint_count},
                "active_duration_ms": self._active_value(when) if self.active_observed else None, "observed_at": utc_now()}
        if self.rule_bindings is not None:
            snapshot["by_source"] = {
                "checkpoint": {"counters": dict(self.checkpoint_counters), "iterations": dict(self.checkpoint_iterations),
                               "checkpoint_counts": snapshot["checkpoint_counts"]},
                "execution_events": {key: snapshot[key] for key in ("event_ids", "counters", "iterations")},
                "adapter_calls": {"completed_call_ids": snapshot["completed_call_ids"]},
                "control_receipts": {"safe_boundary_ids": snapshot["safe_boundary_ids"]},
                "adapter_active_intervals": {"active_duration_ms": snapshot["active_duration_ms"]},
                "clock": {"observed_at": snapshot["observed_at"]}}
        return snapshot

    def _self_check_obligation(self, due: list[dict], when: float) -> dict:
        fingerprint = json.dumps({"execution_id": self.execution_id, "revision": self.rule_revision, "due": due}, ensure_ascii=False, sort_keys=True)
        identifier = "SC-" + hashlib.sha256(fingerprint.encode()).hexdigest()[:20]
        if identifier in self.obligations: return self.obligations[identifier]
        opened = _offset_ms(self.started, when)
        available = not any(not details["safe_boundary"] for details in self.pending_tools.values())
        obligation = {"kind": "self_check_due", "id": identifier, "execution_id": self.execution_id,
                      "rule_revision": self.rule_revision, "due": due, "opened_offset_ms": opened,
                      "rules_sha256": self.rules_digest, "snapshot": self._snapshot(when),
                      "consumed_boundaries": dict(self.consumed_rules),
                      "response_availability": "available" if available else "awaiting_safe_boundary",
                      "deadline_offset_ms": None if self.response_window_ms is None or not available else opened + self.response_window_ms,
                      "status": "open", "observed_at": utc_now()}
        self.obligations[identifier] = obligation
        return obligation

    def record_self_check_response(self, response: dict, *, available_evidence_refs: set[str] | None = None,
                                   receipt_id: str | None = None) -> dict:
        now_offset = _offset_ms(self.started, self.clock())
        obligation_id = response.get("obligation_id") if isinstance(response, dict) else None
        obligation = self.obligations.get(obligation_id) if isinstance(obligation_id, str) else None
        errors = []
        import jsonschema
        try:
            jsonschema.validate(response, SELF_CHECK_RESPONSE_SCHEMA)
            _json_safe({key: value for key, value in response.items() if key != "rule_proposal"})
        except (jsonschema.ValidationError, ValueError, TypeError):
            errors.append("invalid_response_schema")
        if obligation is None: errors.append("unknown_obligation")
        if self.execution_status != "running": errors.append("execution_not_running")
        if obligation is not None:
            if obligation["status"] != "open": errors.append("obligation_not_open")
            if response.get("execution_id") != self.execution_id: errors.append("execution_mismatch")
            if response.get("rule_revision") != obligation["rule_revision"]: errors.append("revision_mismatch")
            if obligation["response_availability"] != "available": errors.append("response_boundary_unconfirmed")
            if obligation["deadline_offset_ms"] is not None and now_offset > obligation["deadline_offset_ms"]:
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
            results = response.get("rule_results")
            expected = {row["rule_id"]: row for row in obligation["due"]}
            if not isinstance(results, list): errors.append("rule_results_missing")
            else:
                received = [row.get("rule_id") for row in results if isinstance(row, dict)]
                if len(received) != len(set(received)) or set(received) != set(expected): errors.append("rule_coverage_mismatch")
                for row in results:
                    if not isinstance(row, dict) or set(row) != {"rule_id", "status", "evidence_refs", "missing_evidence_refs", "reason"}:
                        errors.append("invalid_rule_result"); continue
                    if row["status"] not in {"normal", "defect", "indeterminate"}:
                        errors.append("invalid_rule_status"); continue
                    required = set(expected.get(row["rule_id"], {}).get("required_evidence", []))
                    evidence, missing = row.get("evidence_refs"), row.get("missing_evidence_refs")
                    if (not isinstance(evidence, list) or any(not isinstance(ref, str) for ref in evidence) or
                            not isinstance(missing, list) or any(not isinstance(ref, str) for ref in missing) or
                            not isinstance(row.get("reason"), str) or not row["reason"]):
                        errors.append("invalid_rule_evidence"); continue
                    supplied, declared_missing = set(evidence), set(missing)
                    actual_missing = required - supplied
                    if row["status"] == "indeterminate":
                        if declared_missing != actual_missing: errors.append("indeterminate_evidence_mismatch")
                    elif actual_missing or declared_missing: errors.append("required_evidence_missing")
                    if available_evidence_refs is None: errors.append("evidence_currentness_unverified")
                    elif not supplied.issubset(available_evidence_refs): errors.append("evidence_not_current")
        record = {"kind": "self_check_rejected" if errors else "self_check_received",
                  "id": f"SR-{self.execution_id}-{len(self.responses) + 1}", "receipt_ref": receipt_id,
                  "execution_id": self.execution_id,
                  "obligation_id": obligation_id if isinstance(obligation_id, str) else None,
                  "response_json": _raw_json(response),
                  "received_offset_ms": now_offset, "observed_at": utc_now()}
        record["control_call_ids"] = [cid for cid, row in self.control_calls.items() if
            row["obligation_id"] == obligation_id and receipt_id is not None and self.control_requests.get(row["request_id"], {}).get("receipt_id") == receipt_id]
        if errors:
            record.update(errors=sorted(set(errors)), followup={"kind": "operational_review_due",
                "trigger": "self_check_response_defect", "next_owner": "operational_review",
                "basis_refs": [record["id"]] + ([obligation["id"]] if obligation else [])})
            record["worker_feedback"] = {"kind": "self_check_rejected", "errors": sorted(set(errors)),
                                         "obligation_id": obligation_id if isinstance(obligation_id, str) else None, "next_owner": "worker"}
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
        self.responses.append(record)
        return deepcopy(record)

    def observe(self, event: dict) -> list[dict]:
        when, emitted = self.clock(), []
        if when < self.last_clock:
            return [{"kind": "observation_clock_error", "execution_id": self.execution_id,
                     "reason": "monotonic clock regressed", "next_owner": "engine"}]
        self.last_clock = when
        if self.execution_status != "running":
            return []
        try: self._ingest_event(event, when)
        except ValueError as error:
            emitted.append({"kind": "observation_input_rejected", "execution_id": self.execution_id,
                            "reason": str(error), "next_owner": "adapter", "observed_at": utc_now(),
                            "followup": {"kind": "operational_review_due", "trigger": "observation_error", "next_owner": "operational_review"}
                            if self.mode != "deadline_only" else None})
        if event.get("type") != "tick": emitted.append(self._fact("observation_fact", event, when))
        emitted.extend(self._rule_file_events())
        checkpoint = read_checkpoint(self.workspace)
        if checkpoint["status"] == "valid" and checkpoint["sha256"] not in self.seen_checkpoints:
            self.last_checkpoint = checkpoint["sha256"]
            self.seen_checkpoints.add(checkpoint["sha256"])
            self_check_only = checkpoint["sha256"] in self.self_check_checkpoints
            if not self_check_only: self.checkpoint_count += 1
            progress = checkpoint["value"]
            try:
                counters = self.checkpoint_counters if self.rule_bindings is not None else self.counters
                iterations = self.checkpoint_iterations if self.rule_bindings is not None else self.iterations
                if not self_check_only: self._merge_monotonic(counters, progress.get("counters"), "checkpoint counters")
                if not self_check_only and "iteration" in progress:
                    self._merge_monotonic(iterations, {self.execution_id: progress["iteration"]}, "checkpoint iterations")
            except ValueError as error:
                emitted.append({"kind": "checkpoint_observation_rejected", "execution_id": self.execution_id,
                                "reason": str(error), "observed_at": utc_now()})
            emitted.append({"kind": "checkpoint", "execution_id": self.execution_id, **checkpoint})
        if self.research_self_checks:
            snapshot = self._snapshot(when)
            unavailable = []
            # A source capability is not a measurement already produced at
            # execution start. Use the admitted first observation interval.
            measurement_due = (self.max_self_check_interval_ms is None or
                _offset_ms(self.started, when) >= self.max_self_check_interval_ms)
            for rule in self.rules:
                operator, subject = rule["operator"], rule["subject"]["id"]
                source = snapshot.get("by_source", {}).get(rule["basis"]["source"], snapshot)
                missing = ((operator == "active_duration_gte" and source.get("active_duration_ms") is None) or
                           (operator == "counter_gte" and subject not in source.get("counters", {})) or
                           (operator == "iteration_gte" and subject not in source.get("iterations", {})))
                if missing and measurement_due and rule["id"] not in self.reported_unavailable:
                    unavailable.append(rule["id"])
            if unavailable:
                self.reported_unavailable.update(unavailable)
                emitted.append({"kind": "observation_unavailable", "execution_id": self.execution_id,
                    "rule_ids": unavailable, "reason": "required observation signal has not been measured", "observed_at": utc_now(),
                    "followup": {"kind": "operational_review_due", "trigger": "observation_unavailable", "next_owner": "operational_review"}})
            due = evaluate_rules(self.rules, snapshot, consumed_boundaries=self.consumed_rules)
            if self.next_self_check_offset_ms is not None and _offset_ms(self.started, when) >= self.next_self_check_offset_ms:
                due.append({"rule_id": "@maximum_interval", "operator": "wall_time_reached", "subject": self.execution_id,
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
                deadline = obligation["deadline_offset_ms"]
                if obligation["status"] == "open" and deadline is not None and _offset_ms(self.started, when) > deadline:
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
                                    "observed_at": utc_now()})
            if self.mode == "periodic" and self.periodic_interval_ms is not None:
                if _offset_ms(self.last_review, when) >= self.periodic_interval_ms:
                    self.last_review = when
                    emitted.append({"kind": "periodic_review_due", "execution_id": self.execution_id,
                                    "interval_ms": self.periodic_interval_ms,
                                    "basis": {"source": "selected_profile" if self.profile_ref else "admitted_settings", "profile_ref": self.profile_ref,
                                              "field": "observation_interval_seconds", "unit": "milliseconds"},
                                    "observed_at": utc_now()})
            for review in self.explicit_reviews.values():
                if not review["fired"] and _utc(utc_now(), "now") >= _utc(review["at"], "review at"):
                    review["fired"] = True
                    emitted.append({"kind": "explicit_review_due", "execution_id": self.execution_id,
                                    **{key: review[key] for key in ("review_id", "reason", "basis_ref", "at")},
                                    "observed_at": utc_now()})
        if (self.config.get("checkpoint_expected") and not self.checkpoint_reminded and self.checkpoint_count == 0 and
                self.periodic_interval_ms is not None and _offset_ms(self.started, when) >= self.periodic_interval_ms):
            self.checkpoint_reminded = True
            emitted.append({"kind": "checkpoint_reminder_due", "execution_id": self.execution_id,
                            "checkpoint_status": checkpoint["status"], "observed_at": utc_now()})
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


def self_check_feedback(obligation: dict, rejected_rule_reasons: list[dict] | None = None) -> dict:
    if not isinstance(obligation, dict) or obligation.get("kind") != "self_check_due":
        raise ValueError("self-check feedback requires a self_check_due obligation")
    due = obligation.get("due")
    if not isinstance(obligation.get("id"), str) or not isinstance(obligation.get("rule_revision"), int) or not isinstance(due, list) or not due:
        raise ValueError("malformed self-check obligation")
    return {"obligation_id": obligation["id"], "execution_id": obligation["execution_id"],
            "rule_revision": obligation["rule_revision"],
            "due": [{key: item[key] for key in ("rule_id", "operator", "subject", "required_evidence")} for item in due],
            "deadline_offset_ms": obligation.get("deadline_offset_ms"),
            "rejected_rule_reasons": _json_safe(rejected_rule_reasons or [])}


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
    allowed = {"kind", "reason", "errors", "obligation_id", "execution_id", "rule_revision", "due",
               "deadline_offset_ms", "rejected_rule_reasons", "active_revision", "active_rules_sha256",
               "previous_rules_sha256", "previous_rules_preserved", "next_owner"}
    if not isinstance(feedback, dict) or set(feedback) - allowed:
        raise ValueError("worker feedback contains private or unknown fields")
    encoded = json.dumps(_json_safe(feedback), ensure_ascii=False)
    control = _control_root(workspace)
    destination = _safe_path(control, "observation-feedback.json")
    temporary = _safe_path(control, "observation-feedback.json.tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(destination)


def write_checkpoint_reminder(workspace: Path) -> bool:
    destination = _control_root(workspace) / "observation-feedback.json"
    if destination.exists(): return False
    reminder = {"source": "executor", "decision": "checkpoint",
                "reason": "실행 시작 뒤 관찰 간격이 지나도록 유효한 checkpoint.json이 관찰되지 않았다. 다음 연구 행동 전에 "
                          "「공통 실행」의 체크포인트 형식(current_claim, evidence_paths, attempts, remaining_work, next_step, "
                          "progress_state)으로 지금까지 확인한 사실과 그 근거 파일, 남은 작업을 기록한다. "
                          "이 알림은 실행기가 기계적으로 보낸 것이며 진전이나 실패의 판정이 아니다."}
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(reminder, ensure_ascii=False), encoding="utf-8")
    temporary.replace(destination)
    return True


def request_checkpoint(workspace: Path, reason: str, *, immediate: bool, deadline: str) -> dict:
    request = {"reason": reason, "immediate": immediate, "deadline": deadline,
               "instruction": "Preserve only already obtained facts in checkpoint.json and finish. Do not start new research or external actions."}
    destination = _control_root(workspace) / "stop-request.json"
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    temporary.replace(destination)
    return request


def recovered_checkpoint(workspace: Path, messages: list[dict] | None = None) -> dict:
    checkpoint = read_checkpoint(workspace)
    if checkpoint["status"] == "valid":
        return {"kind": "worker_checkpoint", "checkpoint": checkpoint["value"], "sha256": checkpoint["sha256"]}
    return {"kind": "observed_partial_state", "checkpoint_status": checkpoint["status"],
            "messages": messages or [], "workspace": str(workspace),
            "limitation": "No complete worker checkpoint was received; infer no unreported result."}


def bind_checkpoint_artifact(checkpoint, output_files, previous=None):
    """Connect a valid checkpoint to the exact bytes that were preserved."""
    result = deepcopy(checkpoint)
    if result.get('kind') != 'worker_checkpoint':
        return result
    entry = next((row for row in output_files if row.get('path') == 'checkpoint.json'
                  and row.get('sha256') == result['sha256']), None)
    if entry:
        result['artifact_ref'] = entry['artifact_ref']
    elif previous and previous.get('sha256') == result['sha256'] and previous.get('artifact_ref'):
        result['artifact_ref'] = previous['artifact_ref']
    return result
