"""Engine judgment (layer 2): the domain decisions and state transformations of ``ResearchEngine``.

``CoreEngineMixin`` holds every engine method that judges or transforms state and reaches
the outside only through ports, the store and the file system. ``engine`` keeps the
public entry points, the assembly of default implementations and the run loop (layer 3).
"""
from __future__ import annotations
from .wait_rules import update_waiting_action, waiting_action
from .wait_rules import FAILED_ACTION_WAITS, IMPACT_PENDING_WAITS
from copy import deepcopy
import base64
import binascii
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any
import jsonschema
from .contracts import render_prompt, reading_map, action_schema, with_integration_schema, task_candidate_record, OPERATING_DOCUMENTS
from . import governance, knowledge, planning, knowledge_io, knowledge_records, academic, task_scope, delegations
from .input_basis import capture_sources, sources_current, decision_basis_changes, CurrentnessChanged
from .context_store import collect_outputs, input_class, input_scope, materialize_inputs, restore_continuation, verify_manifest_artifacts
from .operation_trace import phase, measured  # layer: telemetry span only; results do not depend on it
from .trace_report import progress as operation_progress
from .observation_transport import ObservationBatch
from .observations import ObservationTracker, CHECKPOINT_SCHEMA, checkpoint_value, preserve_checkpoint, validate_rules, write_checkpoint_reminder, publish_worker_feedback, persistent_record, read_checkpoint, task_rules_from_execution, capture_checkpoint_files
from .governance_engine import bind_host_configuration
from .native_final import verified_native_final
from .repository import ResearchRepository
from .canonical import canonical_json, exact_content_hash, same_json_value
from .repository import mark_artifact_verified, sealed_bytes
from .state_checks import inspect_state
from .state_contract import ARTIFACT_ROOT
from .git_store import GitStateStoreError
from .scholarly_config import resolve_scholarly_server
from .task_scope import apply_task_dispositions
from . import model_policy
from .question_engine import resolve_pointer
from . import questions, reporting
from . import revisions
from . import submission, integration
from . import activities, execution_lifecycle, execution_profiles, initialization, launch
from .session_slots import held_reservations, live_action_ids, local_termination_confirmed
from .wait_rules import REVIEW_WAITS, REVIEW_ADMISSION_WAITS, REVIEW_RESTORATION_WAITS, review_wait_kind
from . import task_contracts, operational_dispositions, retention, repair_execution
from .control_protocol import SAFETY_BOUNDARY, SELF_CHECK_RESPONSE, SUBMISSION_PREVIEW, SUBMIT_INTENT, self_check_response_errors
from .file_io import cached_sha256, fingerprint_settled, os_lock, stat_fingerprint, write_bytes_atomic
from .configuration import DEFAULT_CONFIG, validate_config
from .control_contracts import OPERATOR_ACTIONS, REQUESTABLE_ROLES, user_decision_changed, control_request_id, normalized_source, normalized_source_bytes, validate_control_payload, validate_request_id
from .input_recovery import overflow_requests, validate_resolutions
from .maintenance_gate import apply_control, settle
from .review_cycle import resource_disposition
from .trust_validation import environment_changed
from .payloads import json_safe
from .call_engine import InputPreparationInterrupted, ReviewPreparationDeferred


def _artifact_format_valid(reference, raw):
    """Validate the supported file format, never its mathematical assertion."""
    suffix = Path(reference["path"]).suffix.lower()
    try:
        if suffix == ".json":
            if Path(reference["path"]).name == "checkpoint.json":
                checkpoint_value(raw)
            else:
                submission.load_json(raw)
            return True
        if suffix in {".txt", ".md", ".tsv", ".csv"}:
            return "\0" not in raw.decode("utf-8-sig")
    except (ValueError, UnicodeError, jsonschema.ValidationError):
        return False
    # No installed validator for another format is evidence of validity.
    return False


# Last settled edition per resolved installation root: (documents, listing, manifest).
_HASHED_INSTALLATION = {}


def _installation_listing(root, documents):
    """Fingerprints of the files an installation manifest hashes, from directory listings.

    One ``scandir`` pass per directory below ``scripts/do_math`` and per
    document directory yields every ``.py`` file and listed document with its
    (size, modification, birth) fingerprint, without a stat call per file. An
    added or removed file changes the key set and a rewrite its fingerprint.
    A Windows directory entry shows a rewrite once its writer closes the file.
    """
    rows = {}

    def walk(directory, prefix):
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    walk(entry.path, prefix + entry.name + "/")
                elif entry.name.lower().endswith(".py"):
                    rows[prefix + entry.name] = stat_fingerprint(entry.stat())

    walk(root / "scripts" / "do_math", "scripts/do_math/")
    by_directory = {}
    for relative in documents:
        parent, _, name = relative.rpartition("/")
        by_directory.setdefault(parent, {})[os.path.normcase(name)] = relative
    for parent, names in by_directory.items():
        with os.scandir(root / parent) as entries:
            for entry in entries:
                relative = names.get(os.path.normcase(entry.name))
                if relative is not None:
                    rows[relative] = stat_fingerprint(entry.stat())
    return rows


def _evaluation_context_for(store, snapshot, *, lean_available, clock):
    def read_artifact(path, commit):
        if not isinstance(path, str) or not path.startswith(ARTIFACT_ROOT):
            raise ValueError("task evidence must identify an immutable archived artifact")
        return store.read(path, commit)
    return {"snapshot": snapshot, "read_artifact": read_artifact, "git_dir": store.git_dir,
            "validate_artifact": _artifact_format_valid, "now": clock.now(), "lean_available": lean_available}


def initialize_instance(repository: Path, *, goal: str, workspace: Path, config: dict | None, title: str,
                        instance_id: str | None, sources: list[Path] | None, source_input: str | None,
                        clock, cwd, trace, host, git_backend, codex_home, host_id) -> dict:
    """``initialize`` after its entry-point choices; ``cwd`` and ``trace`` are called where the state is made.

    ``host`` and ``git_backend`` are the ports selected by the entry point.
    """
    if not goal.strip():
        raise ValueError("a nonempty mathematical goal is required")
    settings = deepcopy(DEFAULT_CONFIG)
    settings.update(config or {})
    validate_config(settings, host_id=host_id)
    if settings["scholarly_enabled"]:
        settings["scholarly_server"] = resolve_scholarly_server(settings["scholarly_server"], start=cwd(), codex_home=codex_home)
    source_inputs = [(source.name, source.read_bytes()) for source in (sources or [])]
    instance_id = instance_id or clock.new_id("RI")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    with trace(workspace / 'operations'), phase('initialize'):
        instance, runtime = initialization.initialize_state(instance_id=instance_id, goal=goal,
            workspace=workspace, config=settings, source_input=goal if source_input is None else source_input,
            title=title, created_at=clock.now(), clock=clock, host=host)
        settings = bind_host_configuration(instance, settings, origin='user')
        instance['config'] = settings
        profiles = execution_profiles.build_profiles(settings, host=host)
        execution_profiles.apply_editions(instance, profiles)
        instance = knowledge_io.ensure_ontology(instance)
        instance = knowledge_records.initialize_families(instance)
        store = ResearchRepository(repository, instance_id, backend=git_backend, clock=clock)
        with store.writer_lock():
            head = store.initialize(instance, runtime)
            if source_inputs:
                artifacts = {}
                bundle = clock.new_id("BA")
                for i, (source_name, raw) in enumerate(source_inputs):
                    path = f"{ARTIFACT_ROOT}{bundle}/{i:04d}-{source_name}"
                    artifacts[path] = raw
                    instance["sources"].append({"id": clock.new_id("SO"), "path": path, "name": source_name,
                                                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
                head = store.save_with_state(head, instance, runtime, artifacts=artifacts)[0]
        return {"instance_id": instance_id, "snapshot": head, "status": runtime["status"]}


def _control_result(store, head, runtime, request_id):
    row = next((row for row in runtime.get("history", [])
        if row.get("kind") in {"user_control", "rejected_user_control"}
        and row.get("request", {}).get("id") == request_id), None)
    if row is None or "result" not in row:
        return None
    # One CAS has one parent. The first descendant contains this immutable receipt;
    # later requests must not substitute their status or configuration for it.
    successor = store.first_descendant(row["publication_parent"], head)
    if successor is None:
        raise ValueError("control receipt has no published successor")
    return {**deepcopy(row["result"]), "snapshot": successor}


def _adopts_observation_or_toolchain(request):
    """An applied control that adopts profiles or registers a toolchain; its result carries window warnings."""
    config = request.get("config")
    if request.get("action") == "trust":
        return isinstance(config, dict) and config.get("operation") == "register"
    change = config.get("change") if isinstance(config, dict) else None
    return (request.get("action") == "decision" and isinstance(change, dict)
            and change.get("kind") == "initialization" and change.get("operation", "adopt") == "adopt")


def _user_control_request(runtime, request_id):
    """The preserved request of an applied user control, or None."""
    return next((row["request"] for row in runtime.get("history", [])
                 if row.get("kind") == "user_control" and row.get("request", {}).get("id") == request_id), None)


def _next_control_order(inbox: Path) -> str:
    """Persist an order that remains comparable after a restart or clock change."""
    counter = inbox / ".acceptance-counter"
    if counter.exists():
        previous = int(counter.read_text(encoding="ascii"))
    else:
        # The inbox retains processed requests. Recover if only the counter was
        # lost, without allowing a new request to overtake an older pending one.
        previous = max((int(json.loads(path.read_bytes())["accepted_order"])
                        for path in inbox.glob("*.json")), default=0)
    if previous < 0:
        raise ValueError("control acceptance counter is invalid")
    next_order = previous + 1
    write_bytes_atomic(counter, str(next_order).encode("ascii"), fsync=True)
    return f"{next_order:020d}"


_OPPOSITE_CONTROL = {"pause": "resume", "resume": "pause"}


def _last_opposite_control(inbox: Path, runtime: dict, action: str) -> str | None:
    """ID of the latest accepted control that undoes ``action``: a pending one, else a processed one."""
    opposite = _OPPOSITE_CONTROL[action]
    processed = set(runtime.get("processed_controls", []))
    pending = [request for request in (json.loads(path.read_bytes()) for path in inbox.glob("*.json")
                                       if path.stem not in processed) if request.get("action") == opposite]
    if pending:
        return max(pending, key=lambda request: (request["accepted_order"], request["created_at"], request["id"]))["id"]
    return next((row["request"]["id"] for row in reversed(runtime.get("history", []))
                 if row.get("kind") in {"user_control", "rejected_user_control"}
                 and row.get("request", {}).get("action") == opposite), None)


def submit_control(repository: Path, instance_id: str, action: str, *, text: str, config: dict | None, origin: str,
                   request_id: str | None, idempotency_key: str | None, clock, lean_available,
                   git_backend, host_id) -> dict:
    """``control`` after its entry-point choices; ``lean_available`` observes the host only when a request needs it."""
    config = {} if config is None else config
    validate_control_payload(action, text, config)
    if not isinstance(origin, str) or origin not in {"user", "operator"}:
        raise ValueError("control origin must be user or operator")
    if origin == "operator" and action not in OPERATOR_ACTIONS:
        raise ValueError("operator controls are limited to " + ", ".join(sorted(OPERATOR_ACTIONS)))
    if request_id is not None:
        validate_request_id(request_id)
    store = ResearchRepository(repository, instance_id, backend=git_backend, clock=clock)
    head, instance, runtime = store.load()
    if request_id is not None and idempotency_key is not None:
        raise ValueError("request_id and idempotency_key are mutually exclusive")
    if action == "source":
        if "body_base64" not in config:
            path = Path(config["path"]).resolve(strict=True)
            config = normalized_source(config.get("name") or path.name, path.read_bytes())
        # The inbox consumer applies this same rule to the admitted copy.
        normalized_source_bytes(config)
    payload = {"instance_id": instance_id, "action": action, "text": text, "config": config or {}, "origin": origin}
    inbox = Path(instance["workspace"]) / "control" / instance_id
    if request_id is None:
        after = (_last_opposite_control(inbox, runtime, action)
                 if action in _OPPOSITE_CONTROL and idempotency_key is None else None)
        request_id = control_request_id(instance_id, action, text=text, config=config, origin=origin,
                                        idempotency_key=idempotency_key, after=after)
    destination = inbox / (request_id + ".json")
    def replay(prior):
        if canonical_json({key: prior.get(key) for key in payload}) != canonical_json(payload):
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
    if action == "configure":
        current_config = instance["config"]
        candidate = {**current_config, **(config or {})}
        validate_config(candidate, host_id=host_id)
        if origin == "operator" and user_decision_changed(current_config, candidate):
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
            if not assessment or exact_content_hash(assessment) != reassessment["assessment_sha256"]:
                raise ValueError("assessment reassessment must identify the current original judgment")
            original = runtime.get("review_cycles", {}).get(assessment["review_cycle_id"], {})
            if config.get("target") not in {None, original.get("knowledge_id")}:
                raise ValueError("assessment reassessment target differs from the original judgment")
        elif role not in REQUESTABLE_ROLES:
            raise ValueError("unsupported requested role")
        if "cleanup_execution_ids" in (config or {}):
            ids = config["cleanup_execution_ids"]
            if role != "maintenance" or not isinstance(ids, list) or not ids or any(not isinstance(eid, str) for eid in ids) or len(set(ids)) != len(ids) or set(ids) - runtime["executions"].keys():
                raise ValueError("maintenance cleanup requires distinct existing execution IDs")
        if planning.instance_ended(instance, runtime):
            raise ValueError("closed/completed instance cannot accept new research activities")
        if role == "supplemental_research":
            task = runtime["tasks"].get((config or {}).get("target"))
            if not task or planning.task_ready(task, instance, runtime, evaluation_context=_evaluation_context_for(
                    store, head, lean_available=lean_available(), clock=clock))["state"] != "ready":
                raise ValueError("supplemental research requires a task whose current contract is ready")
        if role == "operational_review" and (config or {}).get("target") not in runtime["executions"]:
            raise ValueError("operational review requires an existing execution ID")
    inbox.mkdir(parents=True, exist_ok=True)
    with os_lock(inbox / ".acceptance.lock", blocking=True):
        if destination.is_file():
            return replay(json.loads(destination.read_bytes()))
        request = {"id": request_id, **payload, "created_at": clock.now(),
                   "accepted_order": _next_control_order(inbox)}
        temporary = inbox / (request_id + "." + clock.new_id("TMP") + ".tmp")
        temporary.write_bytes(canonical_json(request))
        try:
            # Publish a complete inbox record without overwriting a concurrent same-ID request.
            os.link(temporary, destination)
        except FileExistsError:
            return replay(json.loads(destination.read_bytes()))
        finally:
            temporary.unlink(missing_ok=True)
    return {"accepted": True, "request_id": request["id"], "effect": "pending engine processing"}


def _record_evidence(row):
    return {"snapshot": row["snapshot"], "path": row["path"], "json_pointer": row.get("json_pointer", "/record"),
            "sha256": row["sha256"], "bytes": len(row["bytes"]), "byte_scope": "persisted_file",
            "logical_sha256": exact_content_hash(row["record"]),
            **({'payload_refs':deepcopy(row['payload_refs']), 'json_pointer_scope':'decoded_record'} if row.get('payload_refs') else {})}


# Public query family names: the condition grammar's names of the stored families,
# plus question rows. A stored family outside both keeps its stored name.
_QUERY_FAMILIES = {**{key: name for name, (_, key) in planning.RECORD_FAMILIES.items() if key},
                   "question_links": "question"}


def _query_record(row):
    record = deepcopy(row["record"])
    if row["family"] == "kind_definitions":
        record["definition_family"] = record["family"]
    record["family"] = _QUERY_FAMILIES.get(row["family"], row["family"])
    return record


def query_records(repository: Path, instance_id: str, *, snapshot: str | None = None,
                  kind: str | None = None, text: str = "", limit: int = 50,
                  cursor: str | None = None, related_to: str | None = None, direction: str = "both", backend, clock) -> dict:
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
    store = ResearchRepository(repository, instance_id, backend=backend, clock=clock)
    head, instance, runtime, rows = store.load_records(snapshot)
    descriptors = {row["id"]: row for row in rows if row["id"]}
    records = sorted((_query_record(row) for row in descriptors.values()), key=lambda row: row["id"])
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
            "items": [{"record": r, **_record_evidence(descriptors[r["id"]])} for r in selected],
            "query_basis": {"parameters": parameters, "limit": limit, "complete": not truncated,
                            "snapshot": head, "loaded_ids": [row["id"] for row in selected]},
            "next_cursor": next_cursor}


def read_record(repository: Path, instance_id: str, record_id: str, *, snapshot: str | None = None, backend, clock) -> dict:
    store = ResearchRepository(repository, instance_id, backend=backend, clock=clock)
    row = store.read_record(record_id, snapshot)
    return {"record": _query_record(row), **_record_evidence(row)}


class CoreEngineMixin:
    def _lean_discovered(self) -> bool:
        """Rediscover the local Lean through the host port at most once per second, the installation-check period."""
        current = self.ports.clock.monotonic()
        if current >= self._next_lean_discovery:
            self._next_lean_discovery = current + 1.0
            self._lean_found = self.ports.host.discover_lean() is not None
        return self._lean_found

    def _evaluation_context(self, snapshot=None):
        return _evaluation_context_for(self.store, snapshot or self.head, lean_available=self._lean_discovered(),
                                       clock=self.ports.clock)

    def _governance(self):
        return initialization.governance_or_initial_view(self.instance, self.runtime)

    def _governance_revisions(self):
        view = self._governance()
        return {key: view.get(key, 1) for key in ("goal_revision", "policy_revision")}

    def _installation_manifest(self) -> dict:
        """Hash the installed code and role documents; unchanged files reuse their digests.

        While the directory listings of the last hashed edition are unchanged,
        that edition's manifest is returned without reading the role map,
        globbing or hashing. The listing is taken before the files are found
        and hashed, so a later change always differs from it; a listing with a
        fingerprint too recent to be settled is not reused. Callers only
        compare or copy the result.
        """
        root = self.installation_root
        key = os.path.normcase(str(root.resolve()))
        cached = _HASHED_INSTALLATION.get(key)
        if cached is not None:
            documents, listing, manifest = cached
            try:
                if _installation_listing(root, documents) == listing:
                    return manifest
            except OSError:
                pass  # A removed directory is found or reported by hashing below.
        documents = dict.fromkeys(relative for paths in reading_map(skill_root=root).values() for relative in paths)
        documents.update(dict.fromkeys(OPERATING_DOCUMENTS))
        listing = _installation_listing(root, documents)
        paths = [*sorted((root / "scripts" / "do_math").rglob("*.py")), *(root / relative for relative in documents)]
        files = {path.relative_to(root).as_posix(): cached_sha256(path) for path in paths}
        manifest = {"files": files, "sha256": exact_content_hash(files)}
        if all(fingerprint_settled(fingerprint) for fingerprint in listing.values()):
            _HASHED_INSTALLATION[key] = (tuple(documents), listing, manifest)
        return manifest

    def _execution_profile(self, action):
        profiles = self.instance["execution_profiles"]
        if action["role"] in execution_profiles.MACHINE_ROLES:
            selection = {}
        else:
            selection = self._select_model(action)
        allowed = self.instance.get("role_profile_refs", {}).get(action["role"])
        if action['role'] == 'trust_check' and action.get('profile_ref'):
            transition = self.runtime['trust_transitions'].get(action.get('transition_id'), {})
            if transition.get('source_ref'):
                # Preserve a transition's pinned attempt. The machine checks
                # its command against the assigned environment before Lean.
                allowed = [action['profile_ref']]
        task = self.runtime["tasks"].get(action.get("target"))
        if task and action["role"] in execution_profiles.RESEARCH_PRODUCER_ROLES:
            allowed = task.get("profile_refs", [])
        profile = execution_profiles.select_profile(profiles, action, selection, allowed_refs=allowed)
        action["profile_ref"] = execution_profiles.profile_ref(profile)
        action.update(actor_kind=profile["actor_kind"])
        if selection:
            action["model_selection"] = {**selection, "profile_ref": deepcopy(action["profile_ref"])}
        return profile

    def _activity_for_action(self, action):
        action.setdefault("id", self.ports.clock.new_id("AC"))
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
            aid = self.ports.clock.new_id("AY")
            activities.open_activity(self.runtime, activity_id=aid, activity_kind=action["role"],
                owner_ref=action["lineage_id"], input_refs=[action["target"]] if action.get("target") else [],
                opened_at=self.ports.clock.now())
            action["owner_activity_id"] = aid
        activity = self.runtime["activities"][aid]
        if activity["status"] == "finished":
            raise ValueError("finished activity cannot be continued")
        for queued in self.runtime["queue"]:
            if queued.get("id") == action["id"]:
                queued.update(deepcopy(action))
        return activity

    def _register_execution(self, action, execution, *, profile=None):
        """Shared binding used by AI, formal, trust and external creation sites.

        ``profile`` is the profile the caller already selected for this action
        in this owner step; without it the profile is selected here.
        """
        revisions.bind_repetition_bases(self.instance, self.runtime, action)
        if profile is None:
            profile = self._execution_profile(action)
        activity = self._activity_for_action(action)
        requested_state = execution.get("status", "queued")
        base = execution_lifecycle.create_execution(execution_id=execution["id"], owner_activity_id=activity["id"],
            actor_kind=profile["actor_kind"], input_manifest=execution.get("input_manifest", []),
            profile_ref=execution_profiles.profile_ref(profile), created_at=execution.get("created_at", self.ports.clock.now()),
            continuation_of=action.get("continuation_of"), context_origin=action.get("context_origin", []))
        execution.update(base, action=deepcopy(action))
        if action["role"] == "intent_interpretation" and action.get("stage") == "check":
            execution["intent_import_sha256"] = self.runtime["intent_imports"][action["import_id"]]["sha256"]
        execution_profiles.bind_execution(execution, profile)
        if profile["actor_kind"] == "ai":
            execution.update(model=profile["ai"]["model"], effort=profile["ai"]["effort"])
        else:
            for field in ("model", "effort", "model_selection"):
                execution.pop(field, None)
        held = activity.get("waiting", {}).get("reason") in REVIEW_ADMISSION_WAITS
        admission = ({"disposition": "review_input_restoration"} if held else self._admit_review_execution(action, execution))
        if admission["disposition"] not in {"admitted", "already_admitted", "not_applicable"}:
            if admission['disposition'] in {'review_budget_exhausted', 'review_scope_unaffordable',
                                             'review_followup_reserved', 'review_resource_pending'}:
                self._request_review_resource_disposition(action, admission['disposition'], admission)
                return None
            wait_kind = review_wait_kind(admission['disposition'])
            next_owner = activity['waiting']['next_owner'] if held else 'governance'
            self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({"action": deepcopy(action),
                "kind": wait_kind, "detail": admission, "next_owner": next_owner,
                "reason": activity['waiting']['reason'] if held else admission['authority']['reason']})
            activities.wait_for(self.runtime, activity["id"], reason=wait_kind,
                condition=admission, next_owner=next_owner, at=self.ports.clock.now())
            self._remove_action(action)
            return None
        if activity["status"] == "waiting":
            activities.resume_activity(self.runtime, activity["id"], condition=activity["waiting"]["condition"], at=self.ports.clock.now())
        machine_admission = profile["actor_kind"] == "machine" and requested_state in {"starting", "running"}
        if machine_admission:
            slots = self._session_slots()
            if not slots.acquire(execution["id"], profile=profile, execution=execution):
                action["dispatch_wait"] = deepcopy(slots.admission_wait)
                activities.wait_for(self.runtime, activity["id"], reason="machine capacity unavailable",
                    condition=deepcopy(action["dispatch_wait"]), next_owner=action["dispatch_wait"]["next_owner"], at=self.ports.clock.now())
                return None
            action.pop("dispatch_wait", None)
            execution["action"] = deepcopy(action)
            launch.mark_dispatched(execution['launch_ticket'])
        elif requested_state in {"starting", "running"}:
            execution_lifecycle.transition_execution(execution, "starting", at=self.ports.clock.now())
        if requested_state == "running" and not (machine_admission and profile.get("host_resources")):
            execution_lifecycle.transition_execution(execution, "running", at=self.ports.clock.now())
        activities.assign_execution(self.runtime, activity["id"], execution)
        revisions.record_import_rework(self.instance, self.runtime, action, execution['id'], clock=self.ports.clock)
        return execution

    def _machine_started(self, execution_id, identity):
        """Publish the admitted machine Job identity before its root resumes."""
        execution = self.runtime["executions"][execution_id]
        if execution["actor_kind"] != "machine":
            raise ValueError("machine process callback requires a machine execution")
        self._session_slots().started(execution_id, identity, at=self.ports.clock.now())
        self._save()

    def _settle_activity(self, execution_id):
        self._settle_review_resource_dispositions()
        execution = self.runtime["executions"][execution_id]
        aid = execution["owner_activity_id"]
        activity = self.runtime["activities"][aid]
        cycle = self.runtime.get("review_cycles", {}).get(execution.get("action", {}).get("review_cycle_id"), {})
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
            and row.get("status") != "applied"]
        if repairs:
            if activity["status"] != "waiting":
                activities.wait_for(self.runtime, aid, reason="operational repair remains pending",
                    condition={"operational_disposition_ids": repairs}, next_owner="engine", at=self.ports.clock.now())
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
            reason = (wait['kind'] if wait.get('kind') in REVIEW_WAITS
                      else wait.get('reason') or wait['kind'])
            activities.wait_for(self.runtime, aid, reason=reason,
                condition={"action_ids": [row["action"]["id"] for row in waiting]},
                next_owner=waiting[0].get("next_owner", "engine"), at=self.ports.clock.now())
            return
        preserved = [row for row in activity['unresolved'] if isinstance(row, dict)
                     and row.get('reason') == 'goal_completed_before_dispatch']
        followups = [row for row in activity['followups'] if isinstance(row, dict)
                     and row.get('reason') == 'goal_completed_before_dispatch']
        failed = ([] if execution["outcome"] == "output_accepted" or execution.get("formal_status") == "verified"
                  else [{"execution_id": execution_id, "reason": execution.get("error") or execution["outcome"]}])
        activities.finish_activity(self.runtime, aid, result_refs=activity["result_refs"],
            unresolved=[*preserved, *failed], followups=followups, at=self.ports.clock.now())

    def _render_prompt(self, role: str, context: dict, **kwargs) -> str:
        return render_prompt(role, context, documents=self._documents[role], **kwargs)

    def _check_installation(self, *, force=False):
        current = self.ports.clock.monotonic()
        if not force and current < self._next_installation_check:
            return True
        self._next_installation_check = current + 1.0
        if self._installation_manifest() == self._installation:
            return True
        if not self._instance_closed():
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
        execution_lifecycle.end_preparation(execution, at=self.ports.clock.now(),
            stage=execution.get("input_preparation", {}).get("stage", "context"), reason=reason, cancelled=cancelled)
        self._continue_prepared_action(execution)
        self._settle_activity(execution_id)
        self._save()
        binding = self._transport_bindings.pop(execution_id, None)
        if binding is not None:
            self._transport.close(binding, reason="execution was not admitted")
        shutil.rmtree(resolved)

    def _input_artifacts(self, bundle: str, schema: dict, fitted: dict, workspace: Path) -> dict[str, bytes]:
        """The role input's one archive: ``prepare_role_input`` archived the prompt,
        documents, catalog and details below this bundle; add schema, manifest and tools."""
        base = f"{ARTIFACT_ROOT}{bundle}"
        support = []
        artifacts = {**fitted["artifacts"], f"{base}/schema.json": canonical_json(schema),
                     f"{base}/manifest.json": canonical_json(fitted["manifest"])}
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
        return artifacts

    def _unchanged(self):
        """True when the state equals the published state of this head, apart from ``updated_at``.

        The repository keeps the validated state of every head this process
        read or published; comparing with it replaces a serialized copy. An
        evicted entry answers False, and publishing an unchanged state is a no-op.
        """
        published = self.store.published_state(self.head)
        if published is None:
            return False
        return same_json_value(self.instance, published[0]) and same_json_value(
            {k: v for k, v in self.runtime.items() if k != "updated_at"},
            {k: v for k, v in published[1].items() if k != "updated_at"})

    def _reload(self, snapshot=None):
        """Adopt a published head's validated state, then judge live stop reasons."""
        self.head, self.instance, self.runtime = self.store.load(snapshot)
        self._evaluate_stops()

    def _save(self, artifacts: dict[str, bytes] | None = None) -> None:
        if not artifacts and self._unchanged():
            return
        anchor = self._clock_anchor
        # A rejected later sample never overwrites the last accepted anchor.
        # Persist that accepted high-water mark with this ordinary state change.
        if anchor:
            if anchor[0] > governance.timestamp(self.runtime["last_observed_utc"]):
                self.runtime["last_observed_utc"] = anchor[0].isoformat()
        self.runtime["updated_at"] = self.ports.clock.now()
        # Result acceptance reads each live execution's input snapshot again.
        retain = {execution["input_snapshot"] for execution in self.runtime["executions"].values()
                  if execution.get("status") != "ended" and execution.get("input_snapshot")}
        with phase('state_publish', snapshot=self.head):
            self.head, self.instance, self.runtime = self.store.save_with_state(
                self.head, self.instance, self.runtime, artifacts=artifacts, retain=retain)
        self._evaluate_stops()

    def _record_control_result(self, request, *, rejected=False, reason=None, **details):
        result = {"effect": "rejected" if rejected else "applied", "reason": reason,
                  "status": self.runtime["status"], "config": deepcopy(self.instance["config"])
                      if request["action"] == "configure" else None}
        if not rejected and _adopts_observation_or_toolchain(request):
            from .initialization import observation_window_warnings
            result["observation_window_warnings"] = observation_window_warnings(self.instance, self.runtime)
        self.runtime["history"].append({"kind": "rejected_user_control" if rejected else "user_control",
            "request": deepcopy(request), "reason": reason, **details, "publication_parent": self.head,
            "result": result})

    def control_result(self, request_id):
        return _control_result(self.store, self.head, self.runtime, request_id)

    def _inbox(self) -> list[dict]:
        from .values import bytes_evidence
        from .canonical import validate_storage_value
        path = Path(self.instance["workspace"]) / "control" / self.instance["id"]
        processed = set(self.runtime["processed_controls"])
        results = []
        for file in sorted(path.glob("*.json")):
            if file.stem in processed:
                continue
            try:
                raw = file.read_bytes()
            except FileNotFoundError:
                continue
            try:
                request = json.loads(raw)
                validate_storage_value(request)
                if not isinstance(request, dict) or request.get("id") != file.stem or request.get("instance_id") != self.instance["id"]:
                    raise ValueError("control identity mismatch")
                if any(not isinstance(request.get(key), str) for key in ('created_at', 'accepted_order')):
                    raise ValueError('control ordering envelope is invalid')
                if not isinstance(request.get('action'), str) or not request['action']:
                    raise ValueError('control action envelope is invalid')
            except ValueError as error:
                # The filename is the consumption coordinate even if the wire
                # envelope is unreadable or claims another identity. Preserve
                # exact bytes as JSON evidence, without granting it authority.
                self._reject_control({'id': file.stem, 'action': 'invalid_envelope',
                    'instance_id': self.instance['id'], 'origin': 'untrusted_file',
                    'source_file': file.name, 'source': bytes_evidence(raw)}, str(error))
                processed.add(file.stem)
                continue
            results.append(request)
        # ULID suffixes are random within a millisecond; they do not preserve
        # the order in which a pause, release, or newer user control arrived.
        # Distinct calls can share even the complete wall-clock timestamp.
        # Preserve their host acceptance order, including equal wall-clock timestamps.
        return sorted(results, key=lambda request: (request["accepted_order"], request["created_at"], request["id"]))

    def _apply_inbox(self, *, pump=True) -> None:
        """Receive pending calls and transport requests (``pump``), then apply every inbox control.

        Input preparation and the external stop judgment call only this: they
        reflect user controls without the upkeep's unrelated publications.
        """
        if pump and self._calls is not None:
            self._calls.pump()
        if pump and self._transport is not None:
            self._transport.pump(self._publish_control_request)
        for request in self._inbox():
            action = request["action"]
            try:
                validate_control_payload(action, request.get('text'), request.get('config'))
            except ValueError as error:
                self._reject_control(request, str(error))
                continue
            if action == "source":
                spec = request["config"]
                try:
                    raw = normalized_source_bytes(spec)
                except ValueError as error:
                    self._reject_control(request, str(error))
                    continue
                old = next((s for s in self.instance["sources"] if s["name"] == spec["name"]), None)
                if old and old["sha256"] == spec["sha256"]:
                    self.runtime["processed_controls"].append(request["id"])
                    self.runtime["history"].append({"kind": "source_unchanged", "request_id": request["id"], "name": spec["name"]})
                    self._record_control_result(request, reason="source content unchanged", source_id=old["id"])
                    self._save()
                    continue
                bundle = self.ports.clock.new_id("BA")
                entry = {"id": old.get("id", self.ports.clock.new_id("SO")) if old else self.ports.clock.new_id("SO"), "name": spec["name"],
                         "path": f"{ARTIFACT_ROOT}{bundle}/source.bin", "sha256": spec["sha256"], "bytes": len(raw),
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
                            source_name=spec["name"], reason="Required source content changed: " + spec["name"], actor_ref=request["id"], clock=self.ports.clock)
                self._invalidate_goal_currentness()
                if self.runtime["status"] in {"waiting", "capacity_waiting"}: self.runtime["status"] = "ready"
                self.runtime["processed_controls"].append(request["id"])
                self._record_control_result(request, source_id=entry["id"])
                self._lifecycle_event("source_imported", target=entry["id"], source_ref=request["id"])
                self._save({entry["path"]: raw})
                continue
            try:
                handled = apply_control(self.runtime, request) or self._review_recovery_control(request) or self._knowledge_io_control(request) or self._academic_control(request) or self._governance_control(request) or self._apply_extended_control(request)
            except (ValueError, KeyError, TypeError) as error:
                self._reject_control(request, str(error))
                continue
            if handled:
                if action == 'quiesce' and not (self._calls is not None and self._calls.futures):
                    settle(self.runtime, clock=self.ports.clock)
                self.runtime["processed_controls"].append(request["id"])
                self._record_control_result(request)
                self._save()
                continue
            if action == "input":
                if self._instance_closed():
                    self._reject_control(request, "new research input requires an unfinished instance")
                    continue
                self.runtime["inputs"].append(request)
                if self.runtime["status"] != "paused":
                    self.runtime["status"] = "ready"
                self._enqueue("intent_interpretation", request["id"], reason="new user input")
            elif action == "request":
                if self._instance_closed():
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
                self._enqueue(requested.pop("role"), requested.pop("target", None), **requested)
                if self.runtime["status"] in {"waiting", "capacity_waiting"}:
                    self.runtime["status"] = "ready"
            else:
                raise ValueError("unsupported control action")
            self.runtime["processed_controls"].append(request["id"])
            self._record_control_result(request)
            self._save()

    def _upkeep(self) -> None:
        """Periodic owner work that no single control triggers: due reviews and retried obligations."""
        self._schedule_operational_reviews()
        self._retry_submission_publications()
        self._retry_impact_reviews()
        if self._reconcile_review_host_profiles() or self._settle_review_resource_dispositions():
            self._save()
        self.continue_initial_retries()
        self._run_pending_operational_repairs()
        if any(cycle.get("proposal", {}).get("assessment_reassessment") for cycle in self.runtime.get("review_cycles", {}).values()):
            if self._settle_assessment_reassessments():
                self._save()
        for receipt in self.runtime.get("control_receipts", {}).values():
            execution = self.runtime["executions"].get(receipt["execution_id"], {})
            if receipt["id"] not in self._feedback_delivered and execution.get("status") == "running":
                try:
                    self._redeliver_control_feedback(receipt)
                except OSError:
                    continue  # Delivery can be retried without revoking its durable receipt.
                self._feedback_delivered.add(receipt["id"])

    def _retry_submission_publications(self):
        if self.runtime.get('maintenance_fence'):
            return
        if self.runtime.get("status") in {"paused", "closed"} or self._retrying_publication:
            return
        pending = [deepcopy(row) for row in self.runtime.get("waiting_actions", {}).values()
                   if row.get("kind") == "submission_publication"]
        self._retrying_publication = True
        try:
            for waiting in pending:
                if waiting.get('detail', {}).get('environment_id') and not environment_changed(self.instance, waiting['detail']):
                    continue
                execution = self.runtime["executions"][waiting["execution_id"]]
                action = waiting["action"]
                try:
                    context, schema = self._issued_input(execution)
                    self._receive_submission(action, {}, execution["id"], context, schema,
                        Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace", preserved=True)
                    self._settle_activity(execution['id'])
                    self._save()
                except submission.SealedSubmissionError as error:
                    live = self.runtime.setdefault("waiting_actions", {})[action["id"]]
                    update_waiting_action(live, kind='submission_failure', reason=str(error), next_owner='engine')
                    if self._settle_recovered_execution(execution['id'], at=self.ports.clock.now(),
                            disposition={'kind': 'submission_failure', 'reason': str(error)}):
                        execution.update(error_kind='submission_failure', error=str(error))
                        self._settle_activity(execution['id'])
                    self.route_failed_action(action, execution["id"],
                        reason="Diagnose unreadable sealed submission")
                    self._save()
                except (ValueError, OSError, GitStateStoreError) as error:
                    self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({**waiting, "reason": str(error)})
                    self._save()
        finally:
            self._retrying_publication = False

    def _sealed_bytes(self, path, sha256, size=None, *, raw=None, error="sealed artifact differs from its record",
                      needed=True):
        """repository.sealed_bytes against this engine's repository and head."""
        return sealed_bytes(self.store.git_dir, path, sha256, size, lambda: self.store.read(path, self.head),
                            raw=raw, needed=needed, error=error + ": " + path)

    def _sealed_submission_files(self, execution):
        """Recover exact research files frozen by the accepted submission receipt."""
        intent = execution.get("submission_intent", {})
        entries = intent.get("file_refs")
        if not isinstance(entries, list):
            return None
        files = {}
        manifest = []
        for row in entries:
            raw = self._sealed_bytes(row["artifact_ref"], row["sha256"], row["bytes"],
                                     error="sealed submission file differs from its receipt")
            files[row["path"]] = raw
            manifest.append({key: deepcopy(row[key]) for key in ("path", "sha256", "bytes")})
        return {"files": files, "manifest": manifest, "omitted": [], "complete": True}

    def _preserve_outputs(self, execution_id, workspace, bundle, *, max_bytes, evidence_dir=None):
        """Seal one execution's outputs, control files and checkpoint into one artifact bundle.

        The checkpoint is recorded in runtime. ``evidence_dir`` adds the provider
        evidence as the checkpoint's observation sources. Returns the artifacts,
        output file rows, checkpoint reference and whether every output fit.
        """
        prefix = f"{ARTIFACT_ROOT}{bundle}"
        files = (self._sealed_submission_files(self.runtime["executions"][execution_id])
                 or collect_outputs(workspace, max_bytes=max_bytes))
        control_files = collect_outputs(workspace / ".control", max_bytes=max_bytes)
        artifacts = {f"{prefix}/output-manifest.json": canonical_json(files["manifest"]),
                     f"{prefix}/omitted.json": canonical_json(files["omitted"]),
                     f"{prefix}/control-manifest.json": canonical_json(control_files["manifest"]),
                     f"{prefix}/control-omitted.json": canonical_json(control_files["omitted"])}
        output_files = []
        for path, raw in files["files"].items():
            reference = f"{prefix}/files/{path}"
            artifacts[reference] = raw
            output_files.append({"path": path, "artifact_ref": reference,
                                 "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        for path, raw in control_files["files"].items():
            artifacts[f"{prefix}/control/{path}"] = raw
        checkpoint, checkpoint_artifacts = preserve_checkpoint(workspace, artifact_prefix=f"{prefix}/checkpoint",
            max_bytes=max_bytes, previous=self.runtime.get("checkpoints", {}).get(execution_id), clock=self.ports.clock)
        artifacts.update(checkpoint_artifacts)
        if evidence_dir is not None:
            evidence = collect_outputs(evidence_dir, max_bytes=max_bytes)
            checkpoint["observation_sources"] = []
            for path, raw in evidence["files"].items():
                reference = f"{prefix}/provider-evidence/{path}"
                artifacts[reference] = raw
                checkpoint["observation_sources"].append({"artifact_ref": reference,
                    "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "path": path})
            checkpoint["observation_evidence_complete"] = evidence["complete"]
            checkpoint["observation_evidence_omitted"] = deepcopy(evidence["omitted"])
        self.runtime.setdefault("checkpoints", {})[execution_id] = checkpoint
        checkpoint_ref = f"{prefix}/checkpoint-recovery.json"
        artifacts[checkpoint_ref] = canonical_json(checkpoint)
        return artifacts, output_files, checkpoint_ref, files["complete"]

    def _hold_impact_reviews(self, action, execution_id, received):
        waiting = self.runtime.setdefault("waiting_actions", {}).setdefault(action["id"], waiting_action({
            "action": deepcopy(action), "kind": "impact_review", "execution_id": execution_id,
            "review_requests": {}, "review_execution_ids": {}, "next_owner": "impact_review",
            "reason": "The preserved bundle requires independent impact judgment"}))
        update_waiting_action(waiting, kind='impact_review', next_owner='impact_review')
        for row in received["bundles"]:
            if row.get("next_owner") != "impact_review":
                continue
            request = row["impact_review_request"]
            identifier = row["integration_id"]
            if identifier in waiting["review_requests"]:
                if waiting["review_requests"][identifier] != request:
                    update_waiting_action(waiting, kind='impact_review_changed', next_owner='research_preparation', reason='Impact premises changed while the original mutation remained held')
                    self._enqueue("research_preparation", reason=waiting["reason"])
                continue
            waiting["review_requests"][identifier] = deepcopy(request)
            self._enqueue("maintenance", execution_id, stage="impact_review", basis=request["payload_sha256"],
                input_basis={"impact_review": deepcopy(request)},
                reason="Independently judge the exact preserved bundle and its whole/per-change impact plans")

    def _hold_unreadable_impact_submission(self, waiting, error, *, preparation=None):
        action = waiting["action"]
        live = self.runtime["waiting_actions"][action["id"]]
        update_waiting_action(live, kind='submission_failure', next_owner='engine', reason=str(error))
        for pending in list(self.runtime['queue']):
            request = pending.get('input_basis', {}).get('impact_review', {})
            if pending.get('stage') == 'impact_review' and request.get('producer_execution_id') == waiting['execution_id']:
                self.runtime['history'].append({'kind': 'impact_review_retired',
                    'producer_execution_id': waiting['execution_id'], 'reason': str(error),
                    'action': deepcopy(pending)})
                self._remove_action(pending)
        self.route_failed_action(action, waiting["execution_id"],
            reason="Diagnose unreadable sealed impact submission")
        if preparation is None:
            self._save()
        else:
            self._discard_prepared_input(preparation[0], preparation[1], reason=str(error), cancelled=False)

    def _retry_impact_reviews(self):
        if self.runtime.get("status") == "paused" or self._instance_closed():
            return
        pending = [deepcopy(row) for row in self.runtime.get("waiting_actions", {}).values()
                   if row.get("kind") in IMPACT_PENDING_WAITS]
        for waiting in pending:
            judgments, references = {}, {}
            finished = {}
            for identifier, request in waiting["review_requests"].items():
                reviews = [execution for execution in self.runtime["executions"].values()
                    if execution.get("status") == "ended" and execution.get("outcome") == "output_accepted"
                    and execution.get("action", {}).get("stage") == "impact_review"
                    and execution["action"].get("input_basis", {}).get("impact_review") == request]
                if not reviews:
                    break
                finished[identifier] = reviews[-1]
            # Sealed bytes are read only once every requested review has ended.
            if set(finished) != set(waiting["review_requests"]):
                continue
            try:
                producer = self.runtime["executions"][waiting["execution_id"]]
                producer_output = submission.read_sealed_submission(producer, self.head,
                    self.store.read, git_dir=self.store.git_dir)["output"]
            except (ValueError, OSError, GitStateStoreError) as error:
                self._hold_unreadable_impact_submission(waiting, error)
                continue
            failed = False
            for identifier, review in finished.items():
                request = waiting["review_requests"][identifier]
                try:
                    review_output = submission.read_sealed_submission(review, self.head,
                        self.store.read, git_dir=self.store.git_dir)["output"]
                    judgments[identifier] = integration.validate_impact_review_response(request, review_output)
                except (ValueError, OSError, GitStateStoreError) as error:
                    self._hold_unreadable_impact_submission(waiting, error)
                    failed = True
                    break
                references[identifier] = review["id"]
            if failed:
                continue
            live = self.runtime["waiting_actions"][waiting["action"]["id"]]
            live["review_execution_ids"] = references
            if any(row["decision"] != "approve" for decisions in judgments.values() for row in decisions.values()):
                update_waiting_action(live, kind='impact_review_blocked', next_owner='research_preparation', reason='Independent impact review rejected or could not resolve the held mutation')
                execution = self.runtime["executions"][waiting["execution_id"]]
                self._record_task_receipt(waiting["action"], producer_output, execution["id"], accepted=False)
                self._enqueue("research_preparation", reason=live["reason"])
                self._save()
                continue
            execution = self.runtime["executions"][waiting["execution_id"]]
            context, schema = self._issued_input(execution)
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
                    and execution["id"] not in self._trackers):
                if governance.timestamp(next_review["at"]) <= self._lifecycle_now():
                    due.append((execution["id"], request, next_review))
        if not due or not self._clock_guard()["usable"]:
            return
        for identifier, request, next_review in due:
            self._enqueue("operational_review", identifier, live=True,
                reason=next_review["reason"], observation={"kind": "scheduled_review_due", "disposition_id": request["disposition_id"]},
                observation_refs=[request["disposition_id"]])
            request["dispatched_at"] = self.ports.clock.now()
        self._save()

    def _publish_control_request(self, request):
        """A transport acceptance acknowledges this CAS, not mathematical acceptance."""
        safe_request = {key: deepcopy(value) for key, value in request.items() if key != "capability"}
        digest = exact_content_hash(safe_request)
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
        if self.runtime.get("status") == "paused" and not self._limited_recovery_allowed(execution["action"]):
            return {"state": "rejected", "reason": "the current pause does not authorize this recovery"}
        if not governance.authorize(self.instance, {**execution["action"], "grant_id": request["grant_id"]}, runtime=self.runtime, at=self.ports.clock.now())["allowed"]:
            return {"state": "rejected", "reason": "execution authority no longer permits this request"}
        if not self._clock_guard()["usable"]:
            return {"state": "rejected", "reason": "clock regression prevents new acceptance"}
        if request["kind"] == SUBMISSION_PREVIEW:
            try:
                return {"state": "previewed", "result": self._preview_submission(execution, request["payload"])}
            except (ValueError, KeyError, TypeError, OSError):
                return {"state": "rejected", "reason": "preview input or authority could not be verified"}
        submission_artifacts = {}
        sealed_submission = None
        if request["kind"] == SUBMIT_INTENT:
            workspace = Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace"
            draft_path = request["payload"].get("draft_path")
            if not isinstance(draft_path, str):
                return {"state": "rejected", "reason": "submission requires a workspace-relative draft_path"}
            context, schema = self._issued_input(execution)
            try:
                sealed_submission = submission.seal_submission(workspace, draft_path,
                    execution_id=execution["id"], context=context, schema=schema,
                    max_artifact_bytes=self.instance["config"]["max_artifact_bytes"], clock=self.ports.clock)
            except (ValueError, KeyError, TypeError, OSError) as error:
                return {"state": "rejected", "reason": str(error)}
        original_instance, original_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        original_head = self.head
        tracker = self._trackers.get(execution["id"])
        live_tracker = tracker
        tracker = deepcopy(tracker) if tracker is not None else None
        feedback = []
        receipt = {"id": self.ports.clock.new_id("CT"), "request_id": request["request_id"], "request_sha256": digest,
            "execution_id": execution["id"], "kind": request["kind"], "state": "accepted", "received_at": self.ports.clock.now(),
            "request": safe_request, "parent_snapshot": self.head}
        try:
            if request["kind"] == SUBMIT_INTENT:
                submission_artifacts = self._stage_submission_capture(execution, sealed_submission, receipt,
                    origin='explicit_tool')
                if sealed_submission['capture_eligible'] and tracker is not None:
                    tracker.set_execution_status("stopping")
            elif request["kind"] == SAFETY_BOUNDARY:
                payload = request["payload"]
                # The transport's receipt check has already refused an in-flight boundary.
                execution["safe_boundary_report"] = {"receipt_id": receipt["id"], **deepcopy(payload)}
                if tracker is not None:
                    call_ids = payload.get("call_ids", [])
                    if not isinstance(call_ids, list) or any(cid not in tracker.pending_tools for cid in call_ids):
                        raise ValueError("safe boundary call IDs must identify observed calls of this execution")
                    pending_research = (set(tracker.pending_tools) - tracker.self_check_call_ids
                                        - tracker.boundary_call_ids)
                    if pending_research - set(call_ids):
                        raise ValueError("safe boundary omits observed inflight research calls")
                    tracker.record_safe_boundary(receipt["id"], call_ids=call_ids)
                    self.runtime.setdefault("self_check_obligations", {}).update(tracker.stored_obligations())
            elif request["kind"] == SELF_CHECK_RESPONSE:
                if tracker is None:
                    raise ValueError("self-check has no current tracker")
                payload = request["payload"]
                response = payload["response"]
                if response.get("obligation_id") != payload["self_check_id"]:
                    raise ValueError("self-check response refers to another issued obligation")
                available = self._control_evidence_refs(execution, response)
                tracker.bind_control_request(request, receipt_id=receipt["id"])
                record = tracker.record_self_check_response(response, available_evidence_refs=available, receipt_id=receipt["id"])
                record = persistent_record(record)
                self.runtime.setdefault("self_check_responses", {})[record["id"]] = record
                self.runtime.setdefault("self_check_obligations", {}).update(tracker.stored_obligations())
                if record["kind"] == "self_check_rejected":
                    # The worker reads this receipt; name the actual errors, not only the rejection.
                    receipt.update(state="rejected",
                                   reason="self-check response rejected: " + ", ".join(record["errors"]))
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
                self._reload()
                persisted = next((row for row in self.runtime.get("control_receipts", {}).values()
                    if row["request_id"] == request["request_id"] and row["request_sha256"] == digest), None)
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
        workspace = Path(self.instance.get("workspace", ".")) / "runs" / receipt["execution_id"] / "workspace"
        for item in feedback:
            publish_worker_feedback(workspace / ".control", item)

    def _issued_input(self, execution, *, with_schema=True):
        """The fixed context and schema this execution received (submission.issued_input)."""
        return submission.issued_input(execution, self.head, self.store.read, with_schema=with_schema)

    def _control_evidence_refs(self, execution, response):
        """The evidence references of self-check ``response`` that ``execution`` may cite.

        Self checks cite by the submission rule (``submission.validate_reference``): what
        the fixed input shows, records of its snapshot and preserved files of the
        execution's own workspace, such as its checkpoint. The execution's observation
        records are citable too. A response outside its schema cites nothing; the
        tracker rejects it.
        """
        if self_check_response_errors(response):
            return set()
        context, _ = self._issued_input(execution, with_schema=False)
        workspace = Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace"
        own = {row["id"] for family in ("observation_facts", "self_check_obligations", "self_check_responses")
               for row in self.runtime.get(family, {}).values() if row.get("execution_id") == execution["id"]}
        citable = set()
        for ref in {ref for row in response["rule_results"] for ref in row["evidence_refs"]}:
            try:
                if ref not in own:
                    submission.validate_reference(ref, context, workspace)
            except (ValueError, OSError):
                continue
            citable.add(ref)
        return citable

    def _reject_control(self, request: dict, reason: str) -> None:
        self.runtime["processed_controls"].append(request["id"])
        self._record_control_result(request, rejected=True, reason=reason)
        self._save()

    def _review_recovery_control(self, request):
        if request.get("config", {}).get("assessment_reassessment") is not None:
            if self._instance_closed():
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
                if entry.get("kind") in REVIEW_RESTORATION_WAITS
                and all(entry.get("action", {}).get(key) == action.get(key)
                        for key in ("id", "review_cycle_id", "stage", "round", "slot"))), None)
            if waiting is None:
                raise ValueError("review restoration must identify the exact held slot action")
            workspace = Path(self.instance["workspace"]) / "review-restoration" / request["id"]
            outcome = self._retry_review_restoration(waiting["action"], workspace, at=self.ports.clock.now())
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
            application = delegations.prepare_application(self.instance, self.runtime, spec["delegation_id"], case, now_iso=self.ports.clock.now())
            # The original request is the recovery routing authority. The two
            # judgments receive the same case and neither receives the other verdict.
            for stage in ("delegation_interpret", "delegation_check"):
                self._enqueue("intent_interpretation", action["target"], stage=stage,
                    delegation_application_id=application["id"], requested_by=request["id"],
                    reason="Independently compare this case with the exact original decision and approved delegation")
        else:
            outcome = self._authorize_review_replacement(action, grant_id=spec.get("grant_id"), at=self.ports.clock.now())
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
                reason="Independent delegation judgments did not establish authority for this exact case", clock=self.ports.clock)
            return
        request = _user_control_request(self.runtime, action["requested_by"])
        if request is None:
            raise ValueError("delegated recovery must resolve its preserved request")
        spec = request["config"]["review_replacement"]
        case = {**deepcopy(record["basis"]["case"]), "application_id": application_id}
        outcome = self._authorize_review_replacement(deepcopy(spec["action"]), grant_id=spec.get("grant_id"),
            delegation_id=record["delegation_id"], case=case, at=self.ports.clock.now())
        if outcome["disposition"] != "replacement_ready":
            raise ValueError("independently checked case no longer authorizes recovery: " +
                             str(outcome.get("authority", {}).get("reason", outcome["disposition"])))

    def _knowledge_io_control(self, request: dict) -> bool:
        if request["action"] != "knowledge": return False
        spec = request["config"]
        operation = spec.get("operation")
        if operation not in {"import", "register-kind", "withdraw-kind", "import-relation"}: return False
        if self._instance_closed(): raise ValueError("closed/completed instance cannot apply knowledge controls")
        if operation == "import":
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime, spec["candidate"],
                source_ref=request["id"], actor_ref=request["id"], clock=self.ports.clock)
            # An omitted source_refs declares no source dependency; it does not mean every imported source.
            self.instance["knowledge"][kid]["source_basis"] = capture_sources(self.instance, spec["candidate"].get("source_refs", []))
            for execution in self.runtime["executions"].values():
                if execution["status"] != "ended" and execution.get("action", {}).get("target") == kid:
                    execution["stop_requested"] = "imported_knowledge_revision"
        elif operation == "register-kind":
            self._propose_kind(spec["definition"], request["id"])
        elif operation == "withdraw-kind":
            self.instance, self.runtime = knowledge_io.withdraw_kind_definition(self.instance, self.runtime,
                spec["family"], spec["token"], reason=spec["reason"], actor_ref=request["id"], clock=self.ports.clock)
        else:
            self.instance, _ = knowledge_io.import_relation(self.instance, spec["relation"], source_ref=request["id"], actor_ref=request["id"], clock=self.ports.clock)
        self._invalidate_goal_currentness()
        if self.runtime["status"] == "waiting": self.runtime["status"] = "ready"
        return True

    def status(self) -> dict:
        """The status projection of the current head with this host's observations (reporting.status_report)."""
        self._reload()
        evaluation_context = self._evaluation_context()
        return reporting.status_report(self.store, self.head, self.instance, self.runtime, observation={
            "research_observed_at": evaluation_context["now"],
            "research_wake_reasons": planning.research_wake_reasons(self.instance, self.runtime,
                now=evaluation_context["now"], evaluation_context=evaluation_context),
            "operation_progress": operation_progress(Path(self.instance['workspace']) / 'operations', clock=self.ports.clock),
            "pending_controls": len(self._inbox()),
            "budget": self._session_resources(),
            "provider_waits": self._provider_status()}, evaluation_context=evaluation_context)

    def _prepare_executor_pass(self) -> bool:
        """The owner's judgments before the parallel loop: activation, the clock guard and the academic follow-up.

        Returns whether the loop may start; a regressed clock blocks availability instead.
        """
        if self._instance_closed():
            return False
        if self.instance["lifecycle"]["state"] == "initializing" and not self.runtime.get("user_pause"):
            self._activate_initialization()
        self._save()
        if not self._clock_guard()["usable"]:
            self.runtime["availability"] = {"state": "blocked", "reason": "clock_regression", "next_owner": "operator"}
            self._save()
            return False
        if self.instance["lifecycle"]["state"] != "initializing":
            self._ensure_academic_followup()
        self._resume_import_question_waits()
        return True

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
        waiting = waiting_action({'action': deepcopy(action), 'execution_id': execution['id'],
                   'kind': 'submission_publication', 'next_owner': 'engine',
                   'reason': 'Finish the original committed goal audit submission'})
        waits[action['id']] = waiting
        try:
            submission.read_sealed_submission(execution, self.head,
                self.store.read, git_dir=self.store.git_dir)
        except submission.SealedSubmissionError as error:
            update_waiting_action(waiting, kind='submission_failure', reason=str(error))
            self.route_failed_action(action, execution['id'],
                reason='Diagnose unreadable sealed goal audit submission')
        return True

    def _recover_disappeared(self) -> None:
        restored = False
        for execution in list(self.runtime['executions'].values()):
            if (execution.get('role') == 'goal_audit' and execution.get('status') == 'ended'
                    and execution.get('outcome') != 'output_accepted'
                    and local_termination_confirmed(execution)
                    and self._committed_goal_audit(execution['id'])):
                restored = self._restore_goal_audit_publication(execution) or restored
        if restored:
            self._save()
        publication_pending = {row["execution_id"] for row in self.runtime.get("waiting_actions", {}).values()
            if row.get("kind") == "submission_publication" and
            local_termination_confirmed(self.runtime["executions"].get(row.get("execution_id"), {}))}
        unfinished = [row["id"] for row in self.runtime["executions"].values()
                      if row["status"] != "ended" and row["id"] not in publication_pending]
        if not unfinished:
            return
        recovery_id = self.ports.clock.new_id("RY")
        self.runtime.setdefault("recoveries", {})[recovery_id] = {
            "id": recovery_id, "started_at": self.ports.clock.now(), "execution_ids": unfinished, "dispositions": []}
        self._save()
        for eid in unfinished:
            execution = self.runtime["executions"][eid]
            state = execution["status"]
            if state == "queued":
                if held_reservations(self.runtime, [eid]):
                    observation = {"fact": "queued_reservation_requires_reconciliation", "next_owner": "operator"}
                    execution["recovery_disposition"] = "preserve_space_and_reservations"
                else:
                    # Judged cancelled, not start_failed, because an attempt that disappeared
                    # before its authority was recorded never started.
                    observation = {"fact": "no_execution_or_reservation"}
                    execution_lifecycle.end_preparation(execution, at=self.ports.clock.now(), stage="recovery",
                        reason="executor disappeared during unpublished preparation", cancelled=True)
                    self._continue_prepared_action(execution)
                    self._settle_activity(eid)
                self.runtime["recoveries"][recovery_id]["dispositions"].append({"execution_id": eid, **observation})
                continue
            execution_lifecycle.recover_execution(execution, at=self.ports.clock.now())
            transport = execution.get("control_transport")
            if transport and self._transport:
                self._transport.close(transport, reason="executor restarted")
            local_ended = False
            if execution.get('launch_ticket'):
                local_ended = launch.termination_confirmed(execution['launch_ticket'], recovering=True, jobs=self.ports.jobs)
            disposition = {"execution_id": eid, "local_termination_confirmed": local_ended,
                           "remote_termination": "unknown", "next_owner": "operator"}
            if not local_ended:
                self.runtime["recoveries"][recovery_id]["dispositions"].append(disposition)
                continue
            if execution.get('role') == 'goal_audit' and self._committed_goal_audit(eid):
                if self._settle_recovered_execution(eid, at=self.ports.clock.now(),
                        disposition={'kind': 'committed_submission_pending'}):
                    self._restore_goal_audit_publication(execution)
                    disposition['next_owner'] = 'engine'
                self.runtime['recoveries'][recovery_id]['dispositions'].append(disposition)
                self._save()
                continue
            bundle = self.ports.clock.new_id("BA")
            workspace = Path(self.instance["workspace"]) / "runs" / eid / "workspace"
            if execution["role"] in execution_profiles.LEAN_ROLES:
                workspace = Path(self.instance["workspace"]) / ("formal" if execution["role"] == "formal_check" else "trust") / eid
            artifacts, entries, reference, complete = self._preserve_outputs(
                eid, workspace, bundle, max_bytes=self.instance["config"]["max_artifact_bytes"])
            execution.update(result_ref=reference, artifact_bundle=bundle, output_files=entries,
                             outputs_complete=complete, error="previous executor disappeared")
            if not self._settle_recovered_execution(eid, at=self.ports.clock.now(), disposition={
                    "local_process": "terminated", "remote_state": "unknown", "artifact_ref": reference}):
                self.runtime["recoveries"][recovery_id]["dispositions"].append({**disposition,
                    "local_termination_confirmed": False, "reason": "reservation settlement not confirmed"})
                continue
            action = execution.get("action", {})
            self._remove_action(action)
            if action.get("id"):
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({
                    "action": deepcopy(action), "kind": "execution_failure", "execution_id": eid,
                    "reason": "previous executor disappeared", "next_owner": "operational_review"})
                self.route_failed_action(action, eid,
                    reason="Assess this recovered execution's preserved work and remaining authority")
            disposition["next_owner"] = self.runtime.get("waiting_actions", {}).get(action.get("id"), {}).get("next_owner", "operational_review")
            self.runtime["recoveries"][recovery_id]["dispositions"].append(disposition)
            self._settle_activity(eid)
            self._save(artifacts)
        self.runtime["recoveries"][recovery_id]["finished_at"] = self.ports.clock.now()
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
            path.write_bytes(canonical_json(record))
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
            # Only the goal audit reads a finished review's record (계약/목표-감사.md).
            if action["role"] == "goal_audit" and cycle and cycle["status"] in {"completed", "unresolved"}:
                cycle_path = directory / "review-cycles" / (cycle_id + ".json")
                cycle_path.parent.mkdir(exist_ok=True)
                raw = canonical_json(cycle)
                cycle_path.write_bytes(raw)
                catalog[-1]["review_cycle_source"] = {"path": cycle_path.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest()}
        sources = []
        self._preparation_checkpoint()
        source_bytes = self.store.read_many([s["path"] for s in self.instance["sources"]], self.head)
        for i, source in enumerate(self.instance["sources"]):
            self._preparation_checkpoint()
            raw = self._sealed_bytes(source["path"], source["sha256"], raw=source_bytes[source["path"]],
                                     error="source artifact hash changed")
            path = directory / "sources" / f"{i:04d}-{source['name']}"
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(raw)
            sources.append({**source, "local_path": path.relative_to(workspace).as_posix()})
        target = action.get("target")
        task = self.runtime["tasks"].get(target)
        # The class table decides what this input may carry; blocked keys are dropped by
        # prepare_role_input, and their files are never restored here.
        scope = input_scope(action, self.runtime)
        task_views = [{**deepcopy(row), "content_sha256": knowledge.content_hash(row)} for row in self.runtime["tasks"].values()]
        if input_class(scope, "tasks") != "blocked":
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
                        raw = self._sealed_bytes(file["artifact_ref"], file["sha256"], raw=result_bytes[file["artifact_ref"]],
                                                 error="task result artifact hash changed")
                        path = directory / "task-results" / view["id"] / result["execution_id"] / file["path"]
                        if not path.resolve().is_relative_to(directory.resolve()):
                            raise ValueError("task result artifact path escapes input")
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(raw)
                        restored.append({**file, "local_path": path.relative_to(workspace).as_posix()})
                    result["output_files"] = restored
        governance_input = self._governance()
        context = {"snapshot": self.head, "execution_id": execution_id, "workspace": str(workspace.resolve()), "goal": governance_input["goal"],
                   "policies": governance_input["policies"], "governance": governance_input, "action": action, "task": task,
                   "tasks": task_views, "knowledge_catalog": catalog, "implementation_documents": implementation_documents,
                   "relations": self.instance["relations"], "sources": sources,
                   "user_inputs": self.runtime["inputs"], "open_questions": self._user_questions(),
                   "instance_id": self.instance["id"], "question_links": self._question_view(),
                   "recent_history": self.runtime["history"][-8:],
                   "instructions": "Read input/, your workspace and, through record_map.read_tool, the records of the input snapshot that record_map allows. Pass the exact absolute workspace as workdir on every shell call, with login=false. Use absolute paths under this workspace for file reads and writes; a shell's default working directory may differ. Ask for missing inputs. Never read other runs' workspaces or the central repository directly. New research source code belongs in this workspace."}
        context.update(goal_revision=governance_input.get("goal_revision", 1), policy_revision=governance_input.get("policy_revision", 1),
                       grants=[{k: v for k, v in grant.items() if k != "credential_env"} for grant in self.instance.get("grants", {}).values()],
                       checkpoint_schema=CHECKPOINT_SCHEMA, checkpoint_path="checkpoint.json",
                       external_operations=list(self.runtime.get("external_operations", {}).values()),
                       events=[e for e in self.runtime.get("events", []) if e["id"] in action.get("event_refs", [])],
                       available_input_refs=self._available_inputs())
        if input_class(scope, "task_readiness") == "inline":
            # The plan selects and preparation finds tasks waiting only for input by every
            # task's basis; research work confirms the basis that admitted its own task.
            readers = {target: task} if action["role"] == "research_work" else self.runtime["tasks"]
            context["task_readiness"] = {tid: planning.task_ready(row, self.instance, self.runtime, evaluation_context=evaluation_context)
                                         for tid, row in readers.items() if row is not None}
        context["resources"] = self._session_resources()
        context["budget_unit"] = "concurrent_sessions"
        context["model_policy"] = {"tier_models": self.instance["config"]["tier_models"],
            "role_tiers": self.instance["config"]["role_tiers"], "assessment_schema": model_policy.ASSESSMENT_SCHEMA,
            "selected": action.get("model_selection"), "missing_assessment": "Existing tasks require assessment-only preparation before contract review; preparation uses its configured role floor."}
        if action["role"] == "research_plan":
            live_ids = live_action_ids(self.runtime)
            context["queued_work"] = [deepcopy(a) for a in self.runtime["queue"] if a["role"] in execution_profiles.WORK_ROLES and a.get("id") not in live_ids]
            context['review_followups'] = [deepcopy(cycle) for cid, cycle in self.runtime.get('review_cycles', {}).items()
                if cid in action.get('evidence_refs', [])]
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
            "instruction": "Submit self-contained lean_code and declaration_names. Use preview for non-authoritative compiler feedback when a command is supplied. It uses this verifier edition and configured command, but does not isolate shared libraries or Lake caches. The executor always verifies the submitted exact source again. A configured command is not a completed verification; report only the toolchain actually observed."}
        context["academic_requirements"] = ({} if governance_input.get("status") == "unadopted_input"
                                             else academic.current_requirements(self.instance))
        context["academic_phase"] = "postsolution" if self.instance["goal_status"] == "mathematically_solved" else "deferred_until_goal_solved"
        context["kind_definitions"] = knowledge_io.catalog_definitions(self.instance)
        if action.get("kind_definition_id"):
            definition = self.instance["kind_definitions"][action["kind_definition_id"]]
            if exact_content_hash(definition) != action["kind_definition_sha256"]:
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
                self.store.read, git_dir=self.store.git_dir)
            context["impact_review_input"] = {"request": deepcopy(request),
                "output": sealed["output"], "extensions": sealed["extensions"],
                "records": {rid: deepcopy(record) for rid, (_, record) in planning.record_index(self.instance, self.runtime).items()
                    if any(rid in plan.get("basis", {}) or rid in plan.get("computed_impact", [])
                        or rid in plan.get("declared_impact", []) or rid in plan.get("roots", [])
                        for plan in request["plans"].values())}}
        context["decisions"] = deepcopy(list(self.instance.get("decisions", {}).values()))
        if action["role"] in {"research_preparation", "research_plan", "operational_review", "maintenance"}:
            context["goal_judgments"] = deepcopy(self.instance.get("goal_judgments", []))
        context["execution_profiles"] = deepcopy(list(self.instance.get("execution_profiles", {}).values()))
        context["role_profile_refs"] = deepcopy(self.instance.get("role_profile_refs", {}))
        context["observed_at"] = evaluation_context["now"]
        context['repetition_holds'] = list(revisions.active_repetition_holds(self.runtime).values())
        if action.get("profile_ref"):
            profile = execution_profiles.resolve_profile(self.instance["execution_profiles"], action["profile_ref"])
            context["execution_profile"] = profile
            tools = execution_profiles.runner_tools(profile)
            context["scholarly"].update(enabled=tools["scholarly_server"] is not None,
                                       configured=tools["scholarly_server"] is not None)
        context["academic_validation"] = ({"status": "initialization_incomplete"}
            if governance_input.get("status") == "unadopted_input" else self._academic_status())
        # A stored rejection never changes; whether it still blocks the current solution is derived here.
        rejections = self.runtime.get("external_rejections", [])
        solution = self._solution_basis() if rejections else None
        blocking = ({row["id"] for row in academic.unresolved_rejections(self.instance, self.runtime, solution,
                     resolve_evidence=self._academic_evidence)} if solution is not None else set())
        context["external_rejections"] = [{**row, "blocks_current_solution": row["id"] in blocking}
                                          for row in rejections]
        if action["role"] == "identity_review":
            prepared = self._prepare_review_context(action, workspace, sources=sources)
            if prepared["disposition"] != "ready":
                raise ReviewPreparationDeferred(prepared)
            context["role_review"] = prepared["context"]
        if action["role"] == "goal_audit":
            context["eligible_knowledge"] = []
            for kid, record in self.instance["knowledge"].items():
                links = knowledge_records.usable_links(self.instance, kid)
                if not links:
                    continue
                proposal = knowledge_records.proposal_view(self.instance, kid)
                context["eligible_knowledge"].append({"id": kid,
                    "proposal": proposal, "links": links,
                    "formal_result": knowledge_records.judged_formal_result(
                        self.instance["formal_results"][record["formal_result_id"]]),
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
            context['admissible_basis_refs'] = operational_dispositions.admissible_basis_refs(
                self.instance, self.runtime, action)
            checkpoint = deepcopy(self.runtime.get('checkpoints', {}).get(target))
            checkpoint_metadata = ({key: checkpoint[key] for key in
                ('kind', 'status', 'execution_id', 'observed_at', 'sha256', 'artifact_ref', 'bytes',
                 'source', 'recovered', 'checkpoint_status', 'reason', 'limitation') if key in checkpoint}
                if checkpoint else None)
            evidence = {'checkpoint': checkpoint_metadata, 'checkpoint_source': None,
                'checkpoint_status': 'not_preserved', 'execution_status': reviewed_execution['status'],
                'source_snapshot': self.head, 'checkpoint_files': [],
                'checkpoint_evidence_omitted': deepcopy(checkpoint.get('evidence_omitted', [])) if checkpoint else []}
            if checkpoint and checkpoint.get('artifact_ref'):
                raw = self._sealed_bytes(checkpoint['artifact_ref'], checkpoint['sha256'],
                                         error='operational review checkpoint hash changed')
                relative = 'operational-review/' + target + '/latest-checkpoint.json'
                materialize_inputs(workspace, {relative: raw})
                evidence.update(checkpoint_status='preserved', checkpoint_source={
                    'artifact_ref': checkpoint['artifact_ref'], 'snapshot': self.head,
                    'local_path': 'input/' + relative, 'sha256': checkpoint['sha256'], 'bytes': len(raw)})
                for source in checkpoint.get('evidence_files', []):
                    raw = self._sealed_bytes(source['artifact_ref'], source['sha256'], source['bytes'],
                                             error='operational checkpoint evidence bytes changed')
                    relative = 'operational-review/' + target + '/evidence/' + source['path']
                    materialize_inputs(workspace, {relative: raw})
                    evidence['checkpoint_files'].append({**source, 'snapshot': self.head, 'local_path': 'input/' + relative})
            context['operational_evidence'] = evidence
            if reviewed_execution:
                successor=activities.successor_state(self.runtime,reviewed_execution['id'])
                evidence['activity_continuations']={
                    'frontier':successor,
                    'executions':[{key:self.runtime['executions'][eid].get(key)
                                   for key in ('id','status','outcome','error','result_ref')}
                                  for eid in successor['execution_ids']] if successor else [],
                    'instruction':'An existing continuation owns retry/resume. A separate installation defect requires its own evidence; continuation success alone does not settle that defect.'}
            if reviewed_execution and not context["live_review"] and reviewed_execution.get("artifact_bundle"):
                source_snapshot = self.head
                bundle = reviewed_execution["artifact_bundle"]
                prefix = "operational-review/" + reviewed_execution["id"]
                materialized = {}

                def recover(artifact_ref: str, relative: str, *, expected_sha256: str | None = None,
                            expected_bytes: int | None = None) -> dict:
                    raw = None
                    try:
                        raw = self.store.read(artifact_ref, source_snapshot)
                        if expected_sha256 is None:
                            digest = hashlib.sha256(raw).hexdigest()  # no record yet: identity is created here
                        else:
                            digest = expected_sha256
                            self._sealed_bytes(artifact_ref, expected_sha256, raw=raw,
                                               error="operational review artifact hash changed")
                        if expected_bytes is not None and len(raw) != expected_bytes:
                            raise ValueError("operational review artifact size changed")
                    except (ValueError, OSError, GitStateStoreError) as error:
                        # Diagnosis names unreadable evidence; unverified bytes
                        # are never materialized as a restored research result.
                        return {'artifact_ref': artifact_ref, 'snapshot': source_snapshot,
                            'sha256': expected_sha256, 'bytes': expected_bytes,
                            'restoration_error': {'error_type': type(error).__name__, 'reason': str(error),
                                'observed_sha256': hashlib.sha256(raw).hexdigest() if raw is not None else None,
                                'observed_bytes': len(raw) if raw is not None else None}}
                    logical = prefix + "/" + relative
                    materialized[logical] = raw
                    return {"artifact_ref": artifact_ref, "snapshot": source_snapshot,
                            "local_path": "input/" + logical, "sha256": digest, "bytes": len(raw)}

                normal_result_ref = f"{ARTIFACT_ROOT}{bundle}/result.json"
                checkpoint_ref = f"{ARTIFACT_ROOT}{bundle}/checkpoint-recovery.json"
                # Recovery (_recover_disappeared) records its preserved checkpoint as the result_ref.
                selected_result_ref = reviewed_execution.get("result_ref") or normal_result_ref
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
                          f"{ARTIFACT_ROOT}{bundle}/", source_snapshot):
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
                    "checkpoint": deepcopy(checkpoint_metadata),
                    "checkpoint_source": checkpoint_source, "result_source": result_source,
                    "result_kind": result_kind,
                    "final_result_status": "available" if result_kind == "execution_result" else "not_produced",
                    "output_files": output_files}
        context["execution_window"] = {"path": ".control/execution-window.json", "finish_request_path": ".control/finish-request.json",
            "stop_request_path": ".control/stop-request.json", "feedback_path": ".control/observation-feedback.json",
            'self_check_directory': '.control/self-checks',
            "instruction": "Read management notices under .control after start. A finish request asks for normal submission and does not revoke authority."}
        if action.get("delegation_application_id"):
            context["delegation_case"] = delegations.judgment_input(self.runtime, action["delegation_application_id"])
            request = _user_control_request(self.runtime, action["requested_by"])
            if request is None:
                raise ValueError("delegated recovery must resolve its preserved request")
            context["user_request"] = {"request": deepcopy(request), "delegation_case": deepcopy(context["delegation_case"])}
            context["interpretation_stage"] = action["stage"]
            context["interpretation_to_check"] = None
        context.update(restore_continuation(self.runtime, action, workspace, snapshot=self.head,
            read_artifact=lambda path: self.store.read(path, self.head), checkpoint=self._preparation_checkpoint,
            git_dir=self.store.git_dir))
        self._submission_repair_context(context, action)
        if execution_profiles.review_research(action):
            context.update(self._review_research_context(action, workspace))
        if action["role"] == "operational_review":
            # The target's own failed obligations, and an earlier review of the same
            # target that exhausted its repair: its wait names that review's execution.
            context["blocked_actions"] = [submission.blocked_action_row(aid, entry)
                for aid, entry in self.runtime.get("waiting_actions", {}).items()
                if entry.get("kind") in submission.RESOLVABLE_WAITS and (entry.get("execution_id") == action.get("target")
                    or (entry["action"].get("role") == "operational_review"
                        and entry["action"].get("target") == action.get("target")))]
        if action["role"] == "maintenance":
            # Queue repairs are checked against the engine's own revision state.
            context["pending_revisions"] = deepcopy(planning.pending_revisions(self.runtime))
            context["revision_cycles"] = deepcopy(self.runtime.get("revision_cycles", []))
            context["blocked_actions"] = [submission.blocked_action_row(aid, entry)
                for aid, entry in self.runtime.get("waiting_actions", {}).items()]
            if action.get('initial_submission_diagnosis'):
                failed, waiting = self.initial_diagnosis_input(action)
                context['initial_submission_diagnosis'] = deepcopy(waiting)
                context['initial_submission_diagnosis']['failed_execution'] = deepcopy(failed)
                context['initial_submission_diagnosis']['checkpoint'] = deepcopy(self.runtime.get('checkpoints', {}).get(failed['id']))
                context['initial_submission_diagnosis']['preserved_output_files'] = deepcopy(failed.get('output_files', []))
                refs = [ref for ref in (failed.get('result_ref'), waiting['action'].get('repair', {}).get('raw_output_ref'),
                        waiting['action'].get('repair', {}).get('check_ref'), failed.get('submitted_output_ref'),
                        failed.get('submission_check_ref')) if ref]
                refs.extend(row['artifact_ref'] for row in failed.get('output_files', []))
                refs.extend(row['artifact_ref'] for row in (context['initial_submission_diagnosis']['checkpoint'] or {}).get('evidence_files', []))
                if failed.get('input_bundle'):
                    prefix = ARTIFACT_ROOT + failed['input_bundle']
                    refs.extend([failed['input_manifest']['prompt']['artifact_ref'], prefix + '/schema.json',
                                 prefix + '/input/submission/context.json'])
                context['initial_submission_diagnosis']['materials'] = []
                for index, ref in enumerate(dict.fromkeys(refs)):
                    raw = self.store.read(ref, self.head)
                    local = 'initial-diagnosis/' + str(index) + '.txt'
                    materialize_inputs(workspace, {local: raw})
                    context['initial_submission_diagnosis']['materials'].append({
                        'artifact_ref': ref, 'local_path': 'input/' + local, 'sha256': hashlib.sha256(raw).hexdigest()})
        if action["role"] in execution_profiles.PLANNING_ROLES:
            # prepare_role_input derives configuration_source, and for preparation
            # pending_revisions, from state; waiting actions appear in its ongoing_work.
            if action["role"] == "research_plan":
                context["ready_task_ids"] = sorted(tid for tid, row in context["task_readiness"].items()
                                                   if row["state"] == "ready")
                context["pending_revisions"] = deepcopy(planning.pending_revisions(self.runtime))
            else:
                context["ready_task_ids"] = planning.ready_task_ids(self.runtime, self.instance, evaluation_context=evaluation_context)
            context["revision_cycles"] = deepcopy(self.runtime.get("revision_cycles", []))
            context["blocked_actions"] = [submission.blocked_action_row(aid, entry)
                for aid, entry in self.runtime.get("waiting_actions", {}).items()
                if entry.get("kind") in submission.RESOLVABLE_WAITS]
            context["recent_history"] = self._planning_history("research_plan", workspace)
            if action["role"] == "research_preparation":
                context["preparation_history"] = self._planning_history("research_preparation", workspace)
        # The read tool reads this repository at the input snapshot (input_tool.read_main).
        context["record_store"] = {"repository": str(self.store.repository), "instance_id": self.instance["id"]}
        return self._governance_context(action, context)

    def _planning_history(self, role: str, workspace: Path) -> list[dict]:
        """Keep rejected and incomplete submissions readable after later events."""
        history = []
        references = {e["id"]: e["result_ref"]
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
                raw_action = canonical_json(row["action"])
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
        if execution_profiles.review_research(action):
            schema = self._review_research_schema(action)
        elif action["role"] == "identity_review" and action.get("review_cycle_id"):
            schema = self._review_schema(action)
        elif action.get("delegation_application_id"):
            schema = action_schema({"role": "maintenance"})
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
            schema = action_schema(action)
        if action["role"] == "operational_review":
            schema = deepcopy(schema)
            schema["properties"]["task_assessments"] = deepcopy(action_schema(
                {"role": "research_plan"})["properties"]["task_assessments"])
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
            snapshot=self.head, read_artifact=self.store.read, git_dir=self.store.git_dir)

    def _validate_bundle_current(self, instance, runtime, bundle, *, action, execution_id, context):
        execution = runtime["executions"][execution_id]
        original_instance, original_runtime = self.instance, self.runtime
        try:
            self.instance, self.runtime = instance, runtime
            self._validate_bundle_impacts(instance, runtime, bundle, action=action, execution_id=execution_id)
            self._validate_decision_acceptance(action, bundle["output"], execution, context, evaluation_context=self._evaluation_context())
            reported = submission.reported_references(bundle["output"], bundle["extensions"], context)
            _, input_instance, _ = self.store.view(execution["input_snapshot"])
            execution["source_basis"] = capture_sources(input_instance,
                [row["name"] for row in execution.get("source_basis", [])] + reported)
            if not sources_current(execution["source_basis"], instance):
                raise CurrentnessChanged([{"field": "sources", "reason": "required source content changed"}])
            if execution.get("academic_requirements_sha256") and execution["academic_requirements_sha256"] != academic.current_requirements(instance).get("sha256"):
                raise ValueError("academic requirements changed during execution")
            authority = governance.authorize(instance, action, runtime=runtime, at=self.ports.clock.now())
            if not authority["allowed"]:
                raise ValueError("execution authority was revoked before result acceptance")
            if runtime.get("status") == "paused" and not self._limited_recovery_allowed(action):
                raise ValueError("the current pause no longer authorizes this recovery result")
            for reference in bundle["authority_refs"]:
                grant = instance.get("grants", {}).get(reference)
                if grant is not None:
                    scoped = governance.authorize(instance, {**action, "grant_id": reference}, runtime=runtime, at=self.ports.clock.now())
                    if not scoped["allowed"]:
                        raise ValueError("bundle authority is no longer current: " + reference)
                elif reference not in instance.get("decisions", {}):
                    raise ValueError("bundle authority disappeared: " + reference)
        finally:
            self.instance, self.runtime = original_instance, original_runtime

    def _validate_bundle_candidate(self, instance, runtime, bundle, *, artifacts=None):
        """Validate the candidate under the state contract; publication reuses the result.

        The contract checks the registered families, relations, global record
        IDs and the knowledge-record semantics before the CAS.
        """
        if artifacts:
            for row in runtime.get("question_links", []):
                if row.get("source_ref") in artifacts:
                    resolve_pointer(submission.load_json(artifacts[row["source_ref"]]), row["origin_field"])
        return self.store.validate_candidate(instance, runtime, self.head, artifacts=artifacts)

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
                    snapshot=self.head, read_artifact=self.store.read, git_dir=self.store.git_dir, clock=self.ports.clock)
                self._invalidate_goal_currentness()
            elif integration.mutation_members(bundle["output"], bundle["extensions"]):
                request = integration.bundle_impact_request(self.instance, self.runtime, bundle,
                    producer_execution_id=execution_id, input_snapshot=self.runtime["executions"][execution_id]["input_snapshot"])
                if request["plans"]:
                    confirmations = self._validate_bundle_impacts(self.instance, self.runtime, bundle,
                        action=action, execution_id=execution_id)
                    self.instance, self.runtime = knowledge.apply_impact(self.instance, self.runtime,
                        request["plans"]["bundle"], reason="Apply the validated impact of integration " + bundle["integration_id"],
                        independent_confirmation=confirmations.get("bundle"), clock=self.ports.clock)
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
        def publish(instance, runtime, bundle, validated):
            # Normalize public events before the CAS. No fallible post-commit read
            # may make an already published bundle look like a rejected candidate.
            # The candidate step validated exactly this state against this head.
            self.head, normalized_instance, normalized_runtime = self.store.save_validated(
                self.head, validated)
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
            self._reload()
            result["instance"], result["runtime"] = self.instance, self.runtime
        else:
            self.instance, self.runtime = result["instance"], result["runtime"]
            self._evaluate_stops()
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
        context, schema = self._issued_input(execution)
        workspace = Path(self.instance["workspace"]) / "runs" / execution["id"] / "workspace"
        draft_path = payload.get("draft_path")
        sealed = submission.seal_submission(workspace, draft_path, execution_id=execution["id"],
            context=context, schema=schema, max_artifact_bytes=self.instance["config"]["max_artifact_bytes"], clock=self.ports.clock)
        # An ineligible capture may have no parseable output; preview_submission answers from its check.
        output = extensions = None
        if sealed["capture_eligible"]:
            output = submission.load_json(sealed["artifacts"]["output.json"])
            extensions = submission.load_extensions(sealed["artifacts"]["extensions.json"])
        action = execution["action"]
        preview_prefix = f"{ARTIFACT_ROOT}preview/{execution['id']}"
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
                instance, runtime, bundle, artifacts=preview_artifacts), clock=self.ports.clock)

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
            execution_lifecycle.transition_execution(execution, 'ended', at=self.ports.clock.now(), outcome='execution_incomplete',
                disposition={'kind': 'submission_returned', 'check_ref': rejected['check_ref']})
            self._remove_action(action)
            self.route_submission_return(action, received, execution_id, result.get('output'),
                rejected_submission=rejected)
            self._record_task_receipt(action, {}, execution_id, accepted=False)
            return received
        output = result.get("output")
        execution = self.runtime["executions"][execution_id]
        if execution.get("submission_intent", {}).get("output_ref"):
            preserved = True
        if preserved:
            sealed = submission.read_sealed_submission(execution, self.head,
                self.store.read, git_dir=self.store.git_dir)
            output, extensions, check = sealed["output"], sealed["extensions"], sealed["check"]
        else:
            try:
                extensions = submission.read_extensions(workspace)
            except (ValueError, TypeError, OSError) as error:
                extensions = {}
                extension_issues = [integration.issue(
                    "submission.extensions", "activity-extensions.json", str(error))]
            else:
                extension_issues = []
            check = submission.check_submission(output, schema, context, extensions, workspace,
                mode="receiver", execution_id=execution_id,
                tool_sha256=context["submission_contract"]["tool_sha256"], clock=self.ports.clock)
            check["issues"].extend(extension_issues)
            check["issues"].append(integration.issue(
                "submission.sealed_candidate", "submission_receipt",
                "worker output was not captured by the central submit path"))
            check["passed"] = not check["issues"]
            check['capture_eligible'] = False
            check["id"] = "MC-" + exact_content_hash({key: value for key, value in check.items() if key != "id"})[:24]
            bundle_id = self.ports.clock.new_id("BA")
            prefix = f"{ARTIFACT_ROOT}{bundle_id}"
            execution = self.runtime["executions"][execution_id]
            execution["submission_check_ref"] = prefix + "/check.json"
            execution["submitted_output_ref"] = prefix + "/output.json"
            execution["submitted_extensions_ref"] = prefix + "/extensions.json"
            execution["extensions"] = extensions
            self.runtime.setdefault("events", []).append({"id": self.ports.clock.new_id("EV"), "kind": "submission_unsealed",
                "execution_id": execution_id, "at": self.ports.clock.now(), "evidence_refs": [prefix + "/check.json"],
                "reason": "worker output did not pass through the central submit capture"})
            self._save({prefix + "/check.json": canonical_json(check),
                        prefix + "/output.json": canonical_json(output),
                        prefix + "/extensions.json": canonical_json(extensions)})
        received = self._apply_submission_bundles(action, output, extensions, execution_id, context, check["issues"])
        submission_outcome = integration.submission_outcome(received)
        self._remove_action(action)
        refreshed = False
        execution = self.runtime["executions"][execution_id]
        if received["status"] == "accepted":
            disposition = {"kind": "submission_integrated", "integration_ids": [row["integration_id"] for row in received["bundles"]]}
            if execution["status"] == "ended":
                # Integration can finish after the process. Updating its result never
                # reopens execution authority or changes the physical end time.
                execution.update(outcome="output_accepted", result_disposition=disposition)
            else:
                execution_lifecycle.transition_execution(execution, "ended", at=self.ports.clock.now(), outcome="output_accepted", disposition=disposition)
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
            if submission_outcome != 'publication_wait':
                execution_lifecycle.transition_execution(execution, "ended", at=self.ports.clock.now(), outcome="execution_incomplete",
                    disposition={"kind": "submission_returned", "retry_bundle_ids": received["retry_bundle_ids"]})
            execution.update(error_kind=integration.failure_kind(received['issues']),
                             error="one or more integration bundles were returned")
            # This remains an AI-owned repair; a counter never creates user authority.
            if submission_outcome == 'publication_wait':
                environment = next((row['environment_wait'] for row in received['bundles'] if row.get('environment_wait')), None)
                self.runtime.setdefault("waiting_actions", {})[action["id"]] = waiting_action({
                    **self.runtime.get("waiting_actions", {}).get(action["id"], {}), "action": deepcopy(action),
                    "kind": "submission_publication", "execution_id": execution_id, "next_owner": "engine",
                    **({'detail': environment} if environment else {}),
                    "reason": ("Keep the sealed result until the toolchain record or active trust environment changes"
                               if environment else "Reload current Git state and reapply only unpublished candidate bundles")})
            elif submission_outcome == 'impact_review':
                self._hold_impact_reviews(action, execution_id, received)
            elif submission_outcome == 'premises_changed':
                # Premises changed after the input was fixed: refresh with the change
                # table instead of spending the producer's bounded output repair.
                refreshed = True
                self.runtime.get("waiting_actions", {}).pop(action["id"], None)
                self._refresh_changed_decision(action, execution_id, [
                    {"field": "integration_currentness", "integration_id": row.get("integration_id"),
                     "reason": row["message"]} for row in received["issues"]])
            else:
                self.route_submission_return(action, received, execution_id, output)
        publication_pending = submission_outcome in {'publication_wait', 'impact_review'}
        if not publication_pending:
            if not refreshed:  # A refresh records its own outcome.
                self._record_task_receipt(action, output or {}, execution_id, accepted=received["status"] == "accepted")
            if action["role"] == "operational_review":
                self._save()
                try:
                    self._run_pending_operational_repairs()
                except (ValueError, OSError, GitStateStoreError) as error:
                    # The response is already authoritative; local-effect recovery
                    # never revokes an accepted bundle or repeats its task receipt.
                    self._reload()
                    self.runtime["history"].append({"kind": "operational_repair_interrupted",
                        "execution_id": execution_id, "reason": str(error), "next_owner": "engine"})
        if received["status"] == "accepted" and action["role"] == "maintenance" and action.get("cleanup_execution_ids"):
            self._save()
            cleanup_history_start = len(self.runtime['history'])
            try:
                self._maintenance_cleanup(action, execution_id)
            except (ValueError, OSError) as error:
                retention.record_cleanup_interruption(self.runtime, action['cleanup_execution_ids'],
                    execution_id, str(error), history_start=cleanup_history_start)
        if self.runtime["status"] == "running":
            self.runtime["status"] = "ready"
        return received

    def _available_inputs(self) -> list[str]:
        """This host's input references; derived for each role input, never stored."""
        return task_contracts.available_input_refs(self.instance, self.runtime,
            lean_available=bool(self.instance["config"].get("lean_command")) or self._lean_discovered())

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
                or original.get('role') != 'intent_interpretation'
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
        if not local_termination_confirmed(predecessor):
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
        for field in ('profile_ref', 'model_selection', 'actor_kind', 'dispatch_wait', 'grant_id'):
            action.pop(field, None)
        action['profile_ref'] = deepcopy(lifecycle.get('adoption', {}).get('initial_profile_ref'))
        self._action_lifecycle_gate(action)
        if self._resume_initial_native_final(request, waiting, predecessor):
            return deepcopy(original)
        action['continuation_of'] = predecessor['id']
        superseded = [deepcopy(row) for row in self.runtime['queue']
                      if (row.get('role') == 'operational_review' or row.get('initial_submission_diagnosis'))
                      and row.get('target') == predecessor['id']]
        activities.resume_activity(self.runtime, activity_id, condition=condition, at=self.ports.clock.now())
        del self.runtime['waiting_actions'][identifier]
        self.runtime['queue'] = [row for row in self.runtime['queue'] if row not in superseded]
        self.runtime['queue'].insert(0, action)
        self.runtime.setdefault('history', []).append({'kind': 'initial_execution_retry_started',
            'request_id': request['id'], 'action_id': identifier, 'activity_id': activity_id,
            'execution_id': predecessor['id'], 'input_ref': source['id'], 'input_sha256': source['sha256'],
            'prior_failure': deepcopy(waiting), 'superseded_diagnoses': superseded,
            'profile_ref': deepcopy(action['profile_ref']), 'grant_id': action['grant_id'], 'started_at': self.ports.clock.now()})
        self.runtime['status'] = 'initializing'
        return action

    def _resume_initial_native_final(self, request, waiting, execution):
        """Reuse a preserved normal terminal after central retry validation."""
        if not execution.get('result_ref'):
            return False
        result = json.loads(self.store.read(execution['result_ref'], self.head))
        if (execution.get('submission_intent') or result.get('collection') != 'provider_evidence_only'
                or result.get('status') != 'completed'):
            return False
        context, schema = self._issued_input(execution)
        raw = verified_native_final(result, execution, context)
        if execution.get('outputs_complete') is not True:
            raise ValueError('native recovery requires complete preserved workspace outputs')
        files, manifest = {}, []
        for row in execution.get('output_files', []):
            path = row['path']
            if path in files:
                raise ValueError('preserved native output differs from its execution manifest')
            files[path] = self._sealed_bytes(row['artifact_ref'], row['sha256'], row['bytes'],
                error='preserved native output differs from its execution manifest')
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
                or self.runtime['status'] == 'paused' or self._instance_closed()
                or not governance.authorize(self.instance, execution['action'], runtime=self.runtime, at=self.ports.clock.now())['allowed']):
            raise ValueError('native recovery no longer has current request authority')
        action = deepcopy(execution['action'])
        activity = self.runtime['activities'][execution['owner_activity_id']]
        if activity['status'] == 'waiting':
            activities.resume_activity(self.runtime, activity['id'], condition=deepcopy(activity['waiting']['condition']), at=self.ports.clock.now())
        self.runtime.get('waiting_actions', {}).pop(action['id'], None)
        self.runtime['queue'] = [row for row in self.runtime['queue']
            if not ((row.get('role') == 'operational_review' or row.get('initial_submission_diagnosis'))
                    and row.get('target') == execution_id)]
        context, schema = self._issued_input(execution)
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
        if self._instance_closed():
            raise ValueError("closed/completed instance cannot retry an input overflow")
        native = next((row for row in self.runtime.get('executions', {}).values()
            if row.get('submission_receipt', {}).get('kind') == execution_lifecycle.NATIVE_FINAL_RECEIPT
            and row['submission_receipt'].get('recovery_request_id') == request['id']
            and row.get('action', {}).get('id') == identifier), None)
        if native:
            if native.get('outcome') != 'output_accepted':
                self._finish_native_recovery(request, native['id'])
            return deepcopy(native['action'])
        waiting = self.runtime.get("waiting_actions", {}).get(identifier)
        if waiting and waiting.get("kind") in FAILED_ACTION_WAITS:
            return self._retry_initial_execution_action(request, waiting)
        return self._resume_input_overflow_action(identifier, request['id'])

    def _resume_input_overflow_action(self, identifier, decision_id, *, selected_profile=None):
        """Continue the existing obligation after either an authorized user or plan decision."""
        if self._instance_closed():
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
        for field in ("profile_ref", "model_selection", "actor_kind", "dispatch_wait"):
            action.pop(field, None)
        if selected_profile is not None:
            action['profile_ref'] = deepcopy(selected_profile)
        action["input_overflow_retry"] = {"action_id": identifier,
            "question_id": waiting["question_id"], "request_id": decision_id,
            "started_at": self.ports.clock.now(), "state": "pending"}
        # This is a technical retry, not new authority. Recheck the currently
        # adopted profile, current grant and current lifecycle before mutation.
        self._action_lifecycle_gate(action)
        activities.resume_activity(self.runtime, activity_id, condition=condition, at=self.ports.clock.now())
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
        if retry and retry.get("state") == "pending":
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
        if row.get("status") in {"resolved", "superseded"} and not questions.open_targets(row):
            return "already_resolved"
        if row.get("status") != "open":
            raise ValueError("input_overflow retry question is no longer open")
        questions.close(row, kind=kind, resolution_ref=execution_id,
                        affected_ids=questions.open_targets(row), evidence=evidence)
        return "resolved"

    def _consume_action_events(self, action: dict, execution_id: str) -> None:
        consumed = set(action.get("event_refs", []))
        if consumed:
            self.runtime["history"].append({"kind": "event_consumption", "event_ids": sorted(consumed),
                                            "execution_id": execution_id, "consumed_at": self.ports.clock.now()})
        for event in self.runtime.get("events", []):
            if event["id"] in consumed:
                task = self.runtime["tasks"].get(event.get("target")) if event["kind"] == "task_new_input" else None
                # A later input request keeps its own pending signal.
                if task is not None and task.get("newinput") == event.get("request_id"):
                    del task["newinput"]
        self.runtime["pending_events"] = [entry for entry in self.runtime.get("pending_events", [])
                                           if isinstance(entry, dict) or entry not in consumed]

    def _review_observation_source(self, execution_id, batch, index, receipt_key):
        """The runner's own row bytes and row number; nothing is read or decoded again."""
        action = self.runtime["executions"][execution_id].get("action", {})
        if action.get("role") != "identity_review" or not action.get("review_cycle_id"):
            return None
        return {"raw": batch.rows[index], "event_index": batch.first_row + index,
                "artifact_ref": f"{ARTIFACT_ROOT}BA-provider-{receipt_key}/provider-event.jsonl",
                'source': batch.source(batch.offsets[index][1], start_offset=batch.offsets[index][0])}

    @measured('observation_application')
    def _observe_running(self, execution_id: str, tracker: ObservationTracker, batch: ObservationBatch) -> None:
        # The owner loop applies controls and conversation leases. Observation
        # changes only the runtime. The tracker copy is judged first; the runtime
        # is rolled back and published only when the tick has something to write.
        candidate = deepcopy(tracker)
        candidate.fact_sequence = max(candidate.fact_sequence,
            self.runtime['executions'][execution_id].get('observation_fact_sequence', 0))
        events = batch.events
        live = not batch.is_terminated()
        pending = set(candidate.pending_tools)
        if pending and pending <= candidate.self_check_call_ids:
            checkpoint = read_checkpoint(candidate.workspace, clock=self.ports.clock)
            if checkpoint["status"] == "valid" and checkpoint["sha256"] not in candidate.seen_checkpoints:
                candidate.register_self_check_checkpoint(checkpoint["sha256"])
        artifacts, self_checks, feedback = {}, [], []
        remind = False
        observations, review_rows, stream = [], [], None
        receipts = dict(self.runtime['executions'][execution_id].get('observation_receipts', {}))
        for index, event in enumerate(events):
            receipt_key = exact_content_hash({'execution_id': execution_id, 'event_index': batch.first_row + index,
                'offsets': list(batch.offsets[index]), 'sha256': hashlib.sha256(batch.rows[index]).hexdigest()})
            if receipt_key in receipts:
                continue
            receipts[receipt_key] = batch.first_row + index
            coordinate = self._review_observation_source(execution_id, batch, index, receipt_key)
            if coordinate:
                artifacts[coordinate["artifact_ref"]] = coordinate["raw"]
                review_rows.append((event, coordinate))
            observations.extend(candidate.observe(event,
                source=batch.source(batch.offsets[index][1], start_offset=batch.offsets[index][0]), evaluate=False, live=live))
        live = live and not batch.is_terminated()
        if batch.caught_up():
            observations.extend(candidate.observe({'type': 'tick'},
                source=batch.source(batch.end_offset, start_offset=batch.end_offset), live=live))
        previous = self.runtime['executions'][execution_id].get('observation_stream')
        end_offset = max(batch.end_offset, previous['end_offset']) if previous else batch.end_offset
        # An idle tick applies no stream bytes. Refreshing only its clock
        # values would republish the whole state on every one-second poll.
        if (previous is None or previous['end_offset'] != end_offset
                or previous['local_termination_confirmed'] != (not live)):
            stream = {'end_offset': end_offset, 'received_at': batch.received_at,
                'applied_at': self.ports.clock.now(), 'local_termination_confirmed': not live}
        obligations = self.runtime.get("self_check_obligations", {})
        if not (review_rows or observations or stream is not None
                or receipts != self.runtime['executions'][execution_id].get('observation_receipts', {})
                or any(obligations.get(key) != value for key, value in candidate.obligations.items())):
            tracker.__dict__.clear()
            tracker.__dict__.update(candidate.__dict__)
            return
        # With nothing pending, the published state of this head is the rollback;
        # only unpublished owner changes need a copy.
        original_runtime = None if self._unchanged() else deepcopy(self.runtime)
        try:
            for event, coordinate in review_rows:
                try:
                    self._record_review_observation(execution_id, event, artifact_ref=coordinate["artifact_ref"],
                                                    event_index=coordinate["event_index"])
                except ValueError as error:
                    rejection = {'kind': 'observation_input_rejected', 'execution_id': execution_id,
                        'reason': str(error), 'next_owner': 'adapter', 'observed_at': self.ports.clock.now(),
                        'artifact_ref': coordinate['artifact_ref'], 'event_index': coordinate['event_index']}
                    previous_source = candidate.observation_source
                    candidate.observation_source = coordinate['source']
                    observations.append(candidate.fact('observation_fact', rejection, batch.received_monotonic))
                    candidate.observation_source = previous_source
            if receipts != self.runtime['executions'][execution_id].get('observation_receipts', {}):
                self.runtime['executions'][execution_id]['observation_receipts'] = receipts
            self.runtime['executions'][execution_id]['observation_fact_sequence'] = candidate.fact_sequence
            if stream is not None:
                self.runtime['executions'][execution_id]['observation_stream'] = stream
            for observed in observations:
                kind = observed["kind"]
                if kind == "observation_fact":
                    self.runtime.setdefault("observation_facts", {})[observed["id"]] = persistent_record(observed)
                elif kind == "self_check_due":
                    self_checks.append(deepcopy(observed))
                elif kind == "checkpoint":
                    ref = f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}/{kind}.json"
                    record = persistent_record(observed, artifact_ref=ref)
                    artifacts[ref] = observed["raw"]
                    record["kind"] = "worker_checkpoint"
                    files, omitted = capture_checkpoint_files(candidate.workspace, observed['value'],
                        max_bytes=max(0, self.instance['config']['max_artifact_bytes'] - len(observed['raw'])))
                    record['evidence_files'] = []
                    record['evidence_omitted'] = omitted
                    for path, raw in files.items():
                        reference = ref.rsplit('/', 1)[0] + '/evidence/' + path
                        artifacts[reference] = raw
                        record['evidence_files'].append({'path': path, 'artifact_ref': reference,
                            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
                    self.runtime.setdefault("checkpoints", {})[execution_id] = record
                elif kind == "checkpoint_reminder_due":
                    remind = True
                else:
                    record = persistent_record(observed if observed.get("id") else
                        candidate.fact("observation_fact", observed, candidate.clock()))
                    self.runtime.setdefault("observation_facts", {})[record["id"]] = record
                    trigger = kind in {"operational_review_due", "tool_review_due", "periodic_review_due", "explicit_review_due"}
                    trigger = trigger or observed.get("followup", {}).get("kind") == "operational_review_due"
                    if trigger and live and self.runtime["status"] not in {"paused", "closed"}:
                        observation = {**persistent_record(observed), "observation_refs": [record["id"]]}
                        self.runtime.setdefault("observations", {})[execution_id] = observation
                        self._enqueue("operational_review", execution_id, live=True, observation=observation,
                            obligation_ids=observed.get("obligation_ids", [observed["obligation_id"]] if observed.get("obligation_id") else []),
                            observation_refs=[record["id"]])
                    if observed.get("worker_feedback"):
                        feedback.append(observed["worker_feedback"])
            self.runtime.setdefault("self_check_obligations", {}).update(candidate.stored_obligations())
            self._publish_observation(artifacts or None)
        except Exception:
            self.runtime = self.store.load(self.head)[2] if original_runtime is None else original_runtime
            raise
        tracker.__dict__.clear()
        tracker.__dict__.update(candidate.__dict__)
        for obligation in self_checks:
            if batch.is_terminated():
                break
            # One request object is delivered and hashed for its acknowledgement.
            request = tracker.issue_self_check(obligation['id'])
            self._transport.request_self_check(self._transport_bindings[execution_id], request=request)
            tracker.record_delivery(obligation['id'], source_offset=batch.stream_size())
            self.runtime['self_check_obligations'].update(tracker.stored_obligations([obligation['id']]))
        if self_checks:
            self._publish_observation()
        if remind:
            write_checkpoint_reminder(candidate.workspace / ".control")
        for item in feedback:
            publish_worker_feedback(candidate.workspace / ".control", item)

    def _collect_submitted_result(self, execution, result, context, schema, workspace):
        """Consume the sole central candidate, or capture a verified normal final."""
        intent = execution.get("submission_intent")
        if not intent:
            if result.get('collection') != 'provider_evidence_only':
                return result
            try:
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
                or self._execution_stop_requested(execution['action'], execution)):
            return result
        try:
            raw = self._sealed_bytes(intent['output_ref'], intent['output_sha256'],
                                     error='sealed submission output hash differs')
            output = submission.load_json(raw)
        except (ValueError, TypeError, KeyError, OSError, GitStateStoreError) as error:
            return {**result, 'status': 'failed', 'output': None, 'error_kind': 'execution_failure',
                    'error': 'existing sealed submission cannot be read: ' + str(error)}
        return {**result, 'status': 'completed', 'output': output,
                'collection': 'sealed_submission', 'provider_result_status': result['status']}

    def _stage_submission_capture(self, execution, sealed, receipt, *, origin):
        """Stage one central check and its byte artifacts in the caller's CAS."""
        prefix = f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}/submission"
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
                or execution.get('authority_revocation') or execution.get('stop_reason')
                or self._execution_stop_requested(execution['action'], execution)
                or execution['status'] != ('ended' if recovery_request else 'running')
                or not governance.authorize(self.instance, execution['action'], runtime=self.runtime, at=self.ports.clock.now())['allowed']
                or not self._clock_guard()['usable']):
            raise ValueError('native candidate no longer has current submission authority')
        changes = decision_basis_changes(execution.get('decision_basis'), self.instance, self.runtime)
        changes.extend(self._execution_requirement_changes(execution['action'], evaluation_context=self._evaluation_context()))
        if (changes or not sources_current(execution.get('source_basis', []), self.instance)
                or any(execution.get(key) != value for key, value in planning.governance_revisions(self.instance).items())
                or execution['action']['role'] == 'goal_audit' and execution['action'].get('basis') != self._goal_basis_key()):
            raise ValueError('native candidate input premises changed before capture')
        fixed, fixed_schema = self._issued_input(execution)
        if fixed != context or fixed_schema != schema:
            raise ValueError('native capture differs from the published input or schema')
        sealed = submission.seal_submission(workspace, execution_id=execution['id'], context=fixed,
            schema=fixed_schema, raw_output=raw, captured_outputs=captured_outputs,
            max_artifact_bytes=self.instance['config']['max_artifact_bytes'], clock=self.ports.clock)
        proof = deepcopy(result)
        proof['output'] = None
        proof['execution']['collect']['final'] = {key: value for key, value in
            proof['execution']['collect']['final'].items() if key != 'raw'}
        proof['execution']['collect']['final']['artifact'] = 'output.json'
        sealed['artifacts']['native-evidence.json'] = canonical_json(json_safe(proof))
        receipt = {'id': self.ports.clock.new_id('NF'), 'kind': execution_lifecycle.NATIVE_FINAL_RECEIPT, 'state': 'accepted',
            'execution_id': execution['id'], 'received_at': self.ports.clock.now(), 'parent_snapshot': self.head,
            'final_sha256': hashlib.sha256(raw).hexdigest()}
        if recovery_request:
            receipt['recovery_request_id'] = recovery_request
        original_instance, original_runtime, original_head = deepcopy(self.instance), deepcopy(self.runtime), self.head
        try:
            artifacts = self._stage_submission_capture(execution, sealed, receipt, origin='native_final')
            self._save(artifacts)
        except Exception:
            self._reload()
            saved = next((event['basis']['receipt'] for event in self.runtime.get('events', [])
                if event['kind'] == 'submission_checked' and event.get('basis', {}).get('origin') == 'native_final'
                and event['basis']['receipt']['id'] == receipt['id']), None)
            if saved:
                return saved
            if self.head == original_head:
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
                if not model_policy.edition_current(self.runtime["tasks"].get(tid), basis):
                    return field + " contract edition changed: " + tid
        task = self.runtime["tasks"].get(action.get("target"))
        if (task and action["role"] in execution_profiles.TASK_TARGET_ROLES
                and task.get("status") in task_contracts.TERMINAL_TASK_STATUSES):
            return "The assigned task is already completed or closed"
        return self._obsolete_review_reason(action)

    def _enqueue(self, role: str, target: str | None = None, **extra: Any) -> None:
        action = {"role": role, **extra}
        if target is not None:
            action["target"] = target
        self._bind_revision_action(action)
        compare_keys = ("role", "target", "stage", "slot", "round", "review_cycle_id", "basis", "transition_id",
                        "assessment_targets", "observation_rule_targets", "review_basis_key", "live", "grant_id", "profile_ref",
                         "cleanup_execution_ids", "delegation_application_id", "initial_submission_diagnosis")
        live_actions = live_action_ids(self.runtime)
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
                return
        action.setdefault("id", self.ports.clock.new_id("AC"))
        action.setdefault("lineage_id", action["id"])
        self.runtime["queue"].append(action)
        self._cancel_selected_revision_targets(action)

    def _apply_extensions(self, action: dict, execution_id: str) -> None:
        extension = self.runtime["executions"][execution_id].get("extensions", {})
        for definition in extension.get("kind_definitions", []):
            self._propose_kind(definition, execution_id)
        if extension.get("task_dispositions"):
            if action["role"] not in execution_profiles.PLANNING_ROLES:
                raise ValueError("only preparation and planning may withdraw AI-prepared tasks")
            execution = self.runtime["executions"][execution_id]
            _, _, input_runtime = self.store.view(execution["input_snapshot"])
            self.instance, self.runtime = apply_task_dispositions(self.instance, self.runtime,
                extension["task_dispositions"], execution_id=execution_id, input_tasks=input_runtime["tasks"], clock=self.ports.clock)
        self._apply_queue_plan(execution_id)
        self._apply_academic_resolutions(action, execution_id, extension.get("academic_resolutions", []))
        for relation in extension.get("relations", []):
            self.instance, _ = knowledge_io.import_relation(self.instance, relation, source_ref=execution_id, actor_ref=execution_id, clock=self.ports.clock)
        if extension.get("observation_rules"):
            rules = task_rules_from_execution(extension["observation_rules"], execution_id)
            if action.get("target") not in self.runtime["tasks"]:
                raise ValueError("persisted observation rules require a task target; live rules change only through a self-check rule_proposal")
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
                question = questions.link(self.runtime, execution_id=execution_id,
                    field="extensions/external_requests/" + str(index) + "/purpose", owner="user",
                    targets=[action.get("target") or self.instance["id"]], reason="External action requires a user grant", clock=self.ports.clock)
                question["question_kind"] = "grant"
                continue
            integration_id = self.runtime["executions"][execution_id].get("integration_id", action["id"])
            logical_ref = integration_id + ":external:" + str(request.get("id", index))
            operation_id = "EO-" + hashlib.sha256(logical_ref.encode()).hexdigest()[:24]
            binding = ({"task_id": task["id"], "requirement_id": task["academic_requirement_id"],
                "requirements_sha256": task["requirements_sha256"], "solution_basis": deepcopy(task["solution_basis"]),
                "effect_id": academic_effect} if academic_effect else None)
            self._external_control({"operation": "prepare", "request": request["request"], "grant_id": request["grant_id"],
                                    "id": operation_id}, logical_ref, academic_binding=binding)
            entry = self.runtime["external_operations"][operation_id]
            entry["producer_executions"] = list(dict.fromkeys([*entry.get("producer_executions", []), execution_id]))
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
                    _, origin_instance, origin_runtime = self.store.view(origin)
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
                candidate, source_ref=producer, actor_ref=producer, plan_nonformal=False, clock=self.ports.clock)
            imported_insights.append(kid)
            self.instance["knowledge"][kid].update(source_basis=source_basis, created_at=self.ports.clock.now())
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
        identifiers = {item["title"]: item.get("id") or self.ports.clock.new_id("KN") for item in candidates}
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
                self.instance, self.runtime, ready, source_ref=execution_id, actor_ref=execution_id, plan_nonformal=False, clock=self.ports.clock)
            self.instance["knowledge"][kid].update(task_id=action.get("target"), created_at=self.ports.clock.now(),
                source_basis=deepcopy(self.runtime["executions"][execution_id].get("source_basis", [])))
            pending.remove(ready)
        for relation in output.get("relations", []):
            row = {**relation, **{key: identifiers.get(relation[key], relation[key]) for key in ("source", "target")}}
            self.instance, _ = knowledge_io.import_relation(self.instance, row,
                                                            source_ref=execution_id, actor_ref=execution_id, clock=self.ports.clock)
        return list(identifiers.values())

    def _apply(self, action: dict, output: dict, execution_id: str, *, owns_response: bool = True,
               question_source_ref=None) -> None:
        role, target = action["role"], action.get("target")
        if owns_response and role != "intent_interpretation":
            self._record_output_questions(action, output, execution_id, source_ref=question_source_ref)
        if execution_profiles.review_research(action):
            self._apply_review_research(action, output, execution_id)
        elif role == "research_preparation":
            if model_policy.preparation_only(action):
                self._finish_assessment_preparation(action, execution_id)
                return
            revision_ids = [proposal["revises_task_id"] for proposal in output["candidates"]
                            if proposal["revises_task_id"]]
            if len(revision_ids) != len(set(revision_ids)):
                raise ValueError("each existing task may have only one replacement candidate per response")
            self.runtime["cycles"] += 1
            titles = {}
            authoring_environment = None
            if any(proposal['work_class'] == 'formal' for proposal in output['candidates']):
                _, authoring_instance, _ = self.store.view(self.runtime['executions'][execution_id]['input_snapshot'])
                authoring_environment = authoring_instance.get('active_trust_environment')
                if authoring_environment is None:
                    raise ValueError('formal task requires the trust environment supplied to its author')
            for proposal in output["candidates"]:
                tid = proposal["revises_task_id"] or self.ports.clock.new_id("TK")
                old = self.runtime["tasks"].get(tid)
                if proposal["revises_task_id"] and (old is None or old["status"] in task_contracts.TERMINAL_TASK_STATUSES | {"active"}):
                    raise ValueError("revision must identify an existing unfinished task")
                if old and old.get("academic_requirement_id"):
                    raise ValueError("user-defined academic contracts require an academic_requirements decision")
                contract = task_candidate_record(proposal, task_id=tid, previous=old,
                    trust_environment_id=authoring_environment)
                contract.pop("revises_task_id", None)
                assessment = self.runtime["executions"][execution_id].get("model_decisions", {}).get(proposal["title"])
                if assessment is not None:
                    contract["model_assessment"] = deepcopy(assessment)
                model_policy.work_profile_selection(self.instance['config'], contract,
                    self.instance)
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
            if titles:
                fixed, _ = self._issued_input(self.runtime["executions"][execution_id], with_schema=False)
                supplied = {*fixed.get("available_input_refs", []), *fixed.get("supplied_record_ids", []), *titles.values()}
            for tid in titles.values():
                task = self.runtime["tasks"][tid]
                task["inputs"] = [titles.get(ref, ref) for ref in task["inputs"]]
                task["reuse"] = [titles.get(ref, ref) for ref in task["reuse"]]
                task["dependencies"] = [titles.get(ref, ref) for ref in task["dependencies"]]
                unknown = task_contracts.unsupplied_task_inputs([*task["inputs"], *task["reuse"]], supplied,
                                                                admit_named_sources=True)
                if unknown:
                    raise ValueError("task inputs must name available_input_refs, supplied records or titles "
                                     "prepared in this output; unknown: " + ", ".join(unknown))
                basis = {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                         **self._governance_revisions()}
                review_key = planning.review_basis_key(task, self.instance, self.runtime)
                live_actions = live_action_ids(self.runtime)
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
            # Empty preparation records its actual receipt and regeneration
            # condition; a plan still requires something to decide.
            if output["candidates"] and (decidable or not any(a["role"] == "task_contract_review" for a in self.runtime["queue"])):
                self._enqueue("research_plan")
            definition = self.instance.get("kind_definitions", {}).get(action.get("kind_definition_id"))
            if definition and definition["status"] == "candidate":
                self._enqueue("maintenance", definition["id"], kind_definition_id=definition["id"],
                    kind_definition_sha256=exact_content_hash(definition),
                    reason="Independently reconsider the unresolved kind using the newly prepared evidence")
        elif role == "task_contract_review":
            task = self.runtime["tasks"][target]
            basis = action.get("contract_basis", {"revision": task["revision"], "contract_sha256": planning.contract_hash(task),
                **self._governance_revisions()})
            if basis["contract_sha256"] != planning.contract_hash(task):
                raise ValueError("contract changed while being reviewed")
            review = planning.seal_contract_review(task, output, self.instance, self.runtime, execution_id=execution_id)
            task["reviews"].append(review)
            decision = review["decision"]
            task["status"] = "planned" if decision == "approved" else "waiting"
            if decision == "approved" and task.get("waiting", {}).get("kind") == "contract_review":
                task.pop("waiting")
            if decision != "approved":
                task["revision_requested"] = {"revision": task["revision"], "source": execution_id,
                                              "reason": "task contract review returned " + decision}
                if task.get("academic_requirement_id"):
                    self._ensure_model_assessments()
                    return
                # The unapproved contract's defects and open questions go back to preparation.
                self._enqueue("research_preparation", target,
                              reason="Task contract review returned " + decision + "; revise the contract from its findings or preserve the obligation with the open questions",
                              contract_review_execution=execution_id)
        elif role == "research_plan":
            self._apply_plan(output, execution_id)
        elif role in execution_profiles.RESEARCH_PRODUCER_ROLES:
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
                self.apply_initial_diagnosis(action, output, execution_id)
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
        request = _user_control_request(runtime, action.get("requested_by"))
        if (not request or request.get("origin", "user") != "user" or request.get("action") != "request"
                or request.get("config", {}).get("role") != "maintenance"
                or request["config"].get("cleanup_execution_ids") != requested):
            raise ValueError("cleanup has no preserved exact user-approved execution scope")
        authority = governance.authorize(instance, action, runtime=runtime, at=self.ports.clock.now())
        if not authority["allowed"]:
            raise ValueError("maintenance authority no longer permits cleanup")
        return list(requested)

    def _retention_state(self, action):
        head, instance, runtime, rows = self.store.load_records()
        if head != self.head:
            raise ValueError("cleanup state changed outside the held writer lock")
        records, protected = retention.retention_inputs(instance, runtime, rows)
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
        marks = {}  # local file -> (settled fingerprint, proof) within this cleanup
        for identifier in scope:
            execution = self.runtime["executions"].get(identifier, {})
            if execution.get("status") != "ended" or not local_termination_confirmed(execution):
                continue
            try:
                files, manifest, termination = retention.archive_run(
                    workspace, identifier, execution, f"{ARTIFACT_ROOT}{self.ports.clock.new_id('BA')}", marks)
                artifacts.update(files)
                archived[identifier] = (manifest, termination)
            except (ValueError, OSError) as error:
                failures.append({"path": "runs/" + identifier, "error": str(error), "status": "degraded", "next_owner": "maintenance"})
        if artifacts:
            self._save(artifacts)
            archive_snapshot = self.head
            for identifier, (manifest, termination) in archived.items():
                # The published archive rows are the bytes hashed above.
                for ref, row in [(row["artifact_ref"], row) for row in manifest] + [(termination["evidence_ref"], termination)]:
                    mark_artifact_verified(self.store.git_dir, ref, row["sha256"], row["bytes"])
                execution = self.runtime["executions"][identifier]
                execution["termination"] = {**termination, "snapshot": archive_snapshot}
                execution.setdefault("collection", {})["retention_manifest"] = [
                    {**row, "snapshot": archive_snapshot} for row in manifest]
            self._save()
        state, state_head = self._retention_state(action), self.head
        def current_state():
            # Under the held writer lock the head moves only by this engine's
            # publication, so one head's retention state serves every candidate.
            return state if self.head == state_head else self._retention_state(action)
        reader = self.store.read
        candidates = retention.cleanup_candidates(workspace, **state, read_artifact=reader,
                                                  git_dir=self.store.git_dir, marks=marks)
        result = retention.cleanup(workspace, candidates, current_state=current_state,
                                   read_artifact=reader, git_dir=self.store.git_dir, marks=marks)
        result["failures"].extend(failures)
        if failures:
            result["status"] = "degraded"
        self.runtime["history"].append({"kind": "maintenance_cleanup", "execution_id": execution_id,
            "approved_execution_ids": scope, "candidates": candidates, "result": deepcopy(result)})
        self._save()
        return result

    def _propose_kind(self, definition, source_ref):
        self.instance, token = knowledge_io.register_kind_definition(self.instance, definition,
            source_ref=source_ref, actor_ref=source_ref, clock=self.ports.clock)
        registered = knowledge_io.lookup_definition(self.instance, definition["family"], token)
        self.runtime.setdefault("pending_kind_checks", []).append({"family": definition["family"],
            "token": token, "definition_id": registered["id"], "source_ref": source_ref, "actor_ref": source_ref})
        self._enqueue("maintenance", registered["id"], kind_definition_id=registered["id"],
            kind_definition_sha256=exact_content_hash(registered),
            reason="Independently check the proposed kind meaning, constraints and authority boundary before activation")

    def _apply_kind_definition_check(self, action, output, execution_id):
        identifier = action["kind_definition_id"]
        definition = self.instance["kind_definitions"][identifier]
        governance.validate_independent_execution(self.runtime, execution_id, [definition["actor_ref"]])
        expected = {"id": identifier, "sha256": action["kind_definition_sha256"]}
        if (output["definition_id"] != identifier or output["definition_sha256"] != expected["sha256"]
                or exact_content_hash(definition) != expected["sha256"]
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
                definition["family"], definition["token"], reason="; ".join(output["findings"]), actor_ref=execution_id, clock=self.ports.clock)
        if verdict != "approved":
            self._enqueue("research_preparation", reason="Resolve the independent kind definition findings; revise withdrawn definitions or provide the missing evidence for an unresolved candidate",
                          kind_definition_id=identifier, kind_definition_sha256=exact_content_hash(self.instance["kind_definitions"][identifier]))

    def _apply_operational_disposition(self, action, proposal, execution_id):
        disposition = operational_dispositions.validate_disposition(proposal)
        target = self.runtime["executions"].get(action.get("target"))
        if target is None:
            raise ValueError("operational disposition has no execution target")
        # Application rechecks the newest evidence. A citation that the review's
        # input admitted but a later checkpoint or result replaced is a changed
        # premise; it is reported only when the disposition has no other error.
        current_refs = operational_dispositions.admissible_basis_refs(self.instance, self.runtime, action)
        issued, _ = self._issued_input(self.runtime["executions"][execution_id], with_schema=False)
        changes = operational_dispositions.basis_premise_changes(
            disposition, issued["admissible_basis_refs"], current_refs)
        if not changes:
            operational_dispositions.require_basis_refs(disposition, current_refs)
        if disposition['kind'] == 'repair':
            repair_execution.validate_installation_target(disposition, target, self.installation_root)
        if disposition['kind'] == 'continue' and disposition['next_review']:
            governance.timestamp(disposition['next_review']['at'])
        if changes:
            raise CurrentnessChanged(changes)
        record_id = self.ports.clock.new_id("OD")
        record = {"id": record_id, "execution_id": execution_id, "target_execution_id": target["id"],
                  "disposition": disposition, "obligation_ids": deepcopy(action.get("obligation_ids", [])),
                  "created_at": self.ports.clock.now(), "status": "applied"}
        self.runtime.setdefault("operational_dispositions", {})[record_id] = record
        if operational_dispositions.reconcile_recovery(self.runtime, record):
            return
        kind = disposition["kind"]
        if kind == "repair":
            record["status"] = "repair_required"
        if kind == "continue":
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
        if operational_dispositions.reconcile_recovery(self.runtime, record):
            return record
        disposition = record["disposition"]
        target = self.runtime["executions"][record["target_execution_id"]]
        kind = disposition["kind"]
        previous = target.get("action", {})
        if kind == "repair":
            if self.runtime["executions"][record["execution_id"]]["status"] != "ended":
                record["status"] = "repair_required"
                return record
            return self.complete_repair(record)
        if kind in {"resume", "retry"}:
            if record.get('result', {}).get('continuation_action_id'):
                return record
            if target["status"] != "ended":
                raise ValueError("recovery cannot overlap a live predecessor")
            if (target.get('capacity')
                    and not local_termination_confirmed(target)):
                raise ValueError('recovery requires confirmed local termination')
            if kind == "resume" and disposition["checkpoint_ref"] != self.runtime.get("checkpoints", {}).get(target["id"], {}).get("artifact_ref"):
                raise ValueError("resume must name the preserved current checkpoint")
            if kind == 'resume':
                checkpoint = self.runtime['checkpoints'][target['id']]
                self._sealed_bytes(disposition['checkpoint_ref'], checkpoint.get('sha256'), checkpoint.get('bytes'),
                                   needed=False, error='resume checkpoint bytes differ from the preserved checkpoint')
            predecessors, predecessor = set(), target
            while predecessor and predecessor['id'] not in predecessors:
                predecessors.add(predecessor['id'])
                predecessor = self.runtime['executions'].get(predecessor.get('continuation_of'))
            if any(op.get('status') == 'unknown' and predecessors &
                   {*op.get('producer_executions', []), op.get('execution_id')}
                   for op in self.runtime.get('external_operations', {}).values()):
                raise ValueError('recovery requires reconciliation of unknown external effects')
            if target.get('input_bundle'):
                base = ARTIFACT_ROOT + target['input_bundle']
                manifest = submission.load_json(self.store.read(base + '/manifest.json', self.head))
                if manifest != target['input_manifest'] or verify_manifest_artifacts(
                        manifest, lambda ref: self.store.read(ref, self.head), git_dir=self.store.git_dir):
                    raise ValueError('retry requires intact sealed input evidence')
                support = submission.load_json(self.store.read(base + '/support-manifest.json', self.head))
                for entry in support:
                    self._sealed_bytes(base + '/' + entry['path'], entry['sha256'], entry['bytes'], needed=False,
                                       error='retry submission support differs from its sealed input')
            held = self.runtime.get('waiting_actions', {}).get(previous.get('id'))
            retry = activities.continue_activity(self.runtime, target['id'], at=self.ports.clock.now(),
                reason='operational_' + kind + ':' + record['id'])
            if held and held.get('execution_id') == target['id']:
                retry.update(deepcopy(held['action']), continuation_of=target['id'])
                del self.runtime['waiting_actions'][previous['id']]
            retry['recovery'] = {'execution_id': target['id'], 'disposition_id': record['id'],
                                 'reason': disposition['reason']}
            activity = self.runtime['activities'][target['owner_activity_id']]
            if activity['status'] == 'waiting':
                activities.resume_activity(self.runtime, activity['id'], condition=activity['waiting']['condition'], at=self.ports.clock.now())
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
            _, _, input_runtime = self.store.view(reviewer["input_snapshot"])
            self.instance, self.runtime = task_scope.apply_task_assessments(self.instance, self.runtime,
                assessments, execution_id=record["execution_id"], input_tasks=input_runtime["tasks"],
                evaluation_context=self._evaluation_context(), clock=self.ports.clock)
            target = self.runtime["executions"][record["target_execution_id"]]
            record = self.runtime.get("operational_dispositions", {}).get(record["id"], record)
        elif kind == "user_decision":
            link = questions.link(self.runtime, execution_id=record["execution_id"],
                field="output/disposition/question", owner="user", targets=[previous.get("target") or self.instance["id"]],
                reason=disposition["effect"], clock=self.ports.clock)
            record["question_id"] = link["id"]
        record["status"] = "applied"
        target.pop("pending_operational_disposition", None)

    def _run_pending_operational_repairs(self):
        """Finish accepted dispositions after termination, including a restart."""
        if self.runtime["status"] == "paused" or self._instance_closed():
            return
        for identifier in list(self.runtime.get("operational_dispositions", {})):
            record = self.runtime["operational_dispositions"][identifier]
            if record.get('status') == 'superseded':
                continue
            if operational_dispositions.reconcile_recovery(self.runtime, record):
                self._save()
                continue
            kind = record.get('disposition', {}).get('kind')
            if kind == 'repair':
                if record['status'] in {'applied', 'installation_repair_pending', 'installation_repair_waiting'}:
                    continue
            elif kind not in {'resume', 'retry', 'task_disposition'} or record['status'] != 'awaiting_termination':
                continue
            if any(self.runtime["executions"][record[key]]["status"] != "ended"
                   for key in ("execution_id", "target_execution_id")):
                continue
            self._complete_operational_disposition(record)
            self._save()

    def _goal_basis_key(self) -> str:
        from .governance import mathematical_goal_basis
        tasks = [{key: deepcopy(task.get(key)) for key in
                  ("id", "revision", "question", "scope", "completion_obligations", "expected", "results", "status")}
                 for task in self.runtime["tasks"].values()]
        view = self._governance()
        if self._goal_audit_contract is None:
            # Installed role documents are fixed for this engine; a changed installation pauses it.
            self._goal_audit_contract = hashlib.sha256(self._render_prompt("goal_audit", {}).encode()).hexdigest()
        return exact_content_hash({"goal": view["goal"], "goal_basis_sha256": mathematical_goal_basis(view['charter']),
            "policy_revision": view.get("policy_revision", 1), "knowledge": self.instance["knowledge"],
            "formal_results": self.instance.get("formal_results", {}), "expositions": self.instance.get("expositions", {}),
            "identity_assessments": self.instance.get("identity_assessments", {}),
            "assessment_uses": self.instance.get("assessment_uses", {}),
            "trust_environments": self.instance.get("trust_environments", {}),
            "tasks": tasks, "sources": capture_sources(self.instance),
            "user_inputs": self.runtime["inputs"], "required": self.instance["config"]["goal_auditors"],
            "input_contract": self._goal_audit_contract})

    def _apply_plan(self, output: dict, execution_id: str) -> None:
        execution = self.runtime["executions"][execution_id]
        _, _, input_runtime = self.store.view(execution["input_snapshot"])
        fixed, _ = self._issued_input(execution, with_schema=False)
        if fixed.get("snapshot") != execution["input_snapshot"] or "ready_task_ids" not in fixed:
            raise ValueError("planning input is missing its fixed candidate population")
        # The fixed input holds every current task (context_store.prepare_role_input), so assessed
        # tasks and transfer recipients are bound to this one population.
        input_tasks = {row["id"]: input_runtime["tasks"][row["id"]] for row in fixed["tasks"]}
        self._apply_task_plan(output, execution_id, input_tasks, fixed["ready_task_ids"],
                              evaluation_context=self._evaluation_context())
        self._apply_input_overflow_resolutions(execution.get('extensions', {}).get('input_overflow_resolutions', []),
                                               fixed, execution_id)
        for assessment in output["task_assessments"]:
            task = self.runtime["tasks"][assessment["task_id"]]
            self._record_academic_assessment(task, assessment, execution_id)
        if output["goal_audit"]:
            if self.instance["goal_status"] != "mathematically_solved":
                basis = self._goal_basis_key()
                self._ensure_goal_audit_requests(basis, execution_id)
        self._ensure_academic_followup()

    def _submission_check_summary(self, snapshot, runtime):
        try:
            seals, covered = [], set()
            receipts = dict(runtime.get('control_receipts', {}))
            for event in runtime.get('events', []):
                if event['kind'] != 'submission_checked':
                    continue
                if event.get('basis', {}).get('origin') == 'native_final':
                    receipt = event['basis']['receipt']
                    if receipt['kind'] != execution_lifecycle.NATIVE_FINAL_RECEIPT or event['source_ref'] != event['target']:
                        raise ValueError('native check event differs from its execution')
                    receipts[receipt['id']] = receipt
                else:
                    receipt = receipts[event['source_ref']]
                evidence = receipt['payload']['submission_check']
                if (receipt['kind'] not in execution_lifecycle.SUBMISSION_RECEIPT_KINDS or receipt['execution_id'] != event['target']
                        or event.get('evidence_refs') != [evidence['check_ref']]):
                    raise ValueError('central check event differs from its receipt')
                covered.add(receipt['id'])
                seals.append({'event_seq': event['event_seq'], 'capture_id': receipt.get('request_id', receipt['id']),
                    'execution_id': receipt['execution_id'], 'state': receipt['state'],
                    'submission_check': evidence})
            required = {row['id'] for row in receipts.values() if row.get('kind') == SUBMIT_INTENT
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
                read_artifact=self.store.read, history_window=len(seals), git_dir=self.store.git_dir)
        except (ValueError, KeyError, TypeError, OSError, GitStateStoreError) as error:
            return {'snapshot':snapshot,'status':'incomplete','error':str(error),'next_owner':'maintenance'}
        summary.update(status='verified')
        return summary

    def _inspect_before_write(self):
        """Reject missing or truncated current evidence before any recovery or installation write.

        Presence and stored length only; ``check`` compares full bytes. The
        loaded state already passed the state contract.
        """
        snapshot = self.head
        sizes = lambda paths: self.store.blob_sizes(paths, snapshot, missing="omit")
        inspection = inspect_state(self.instance, self.runtime, requested_areas=["record_storage"],
            snapshot=snapshot, artifact_sizes=sizes)
        failed = [row for row in inspection["findings"] if row.get("status") in {"blocked", "incomplete"}]
        if failed:
            raise ValueError("current state evidence must be repaired before publication: " + str(failed))
        # Each sealed role input names its prompt in its manifest.
        prompts = {execution["input_manifest"]["prompt"]["artifact_ref"]: execution["id"]
                   for execution in self.runtime["executions"].values() if execution.get("input_bundle")}
        present = sizes(list(prompts))
        for path, execution_id in prompts.items():
            if path not in present:
                raise ValueError("current input artifact is missing: " + execution_id)

    def check(self, snapshot=None, requested_areas=None) -> dict:
        # Loading validates the state contract; the start_import_input area
        # compares every sealed role input, prompt included, with its manifest.
        head, instance, runtime = self.store.load(snapshot)
        inspection = inspect_state(instance, runtime, requested_areas=requested_areas,
            snapshot=head, read_artifact=lambda path: self.store.read(path, head),
            read_artifacts=lambda paths: self.store.read_many(paths, head, missing="omit"))
        areas = set(inspection["requested_areas"])
        errors = []
        try:
            if "governance_trust" in areas:
                validate_config(instance["config"], host_id=self.host_id)
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
                "scope": "requested persisted-state areas and their referenced artifact bytes"}
