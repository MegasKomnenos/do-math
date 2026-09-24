"""Consume an admitted repair as an evidenced, deterministic ENGINE file effect.

This is not another provider attempt, permission ledger or execution registry.
The existing OD record owns progress; immutable Git artifacts own byte evidence.
Execution IDs on local effects identify the affected execution, not a claim
that its former worker performed the repair. No prose is executable here.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets

from . import activities, execution_profiles, operational_dispositions
from .git_store import GitStateStoreError, PhysicalBoundary
from .repository import canonical_json


class RepairNeedsDecision(ValueError):
    """The observed effect no longer permits deterministic continuation."""


def route_failed_action(engine, action, execution_id, *, reason, front=False):
    """Choose a diagnosis allowed in the current lifecycle, without recursion."""
    wait = engine.runtime['waiting_actions'][action['id']]
    if engine.instance.get('lifecycle', {}).get('state') == 'initializing':
        wait['next_owner'] = 'maintenance'
        if action['role'] == 'intent_interpretation' and not action.get('diagnosis_attempt'):
            engine._enqueue('maintenance', execution_id, initial_submission_diagnosis=True, reason=reason)
        return
    wait['next_owner'] = 'operational_review'
    if action['role'] != 'operational_review' and action.get('recovery_attempt', 0) < 1:
        engine._enqueue('operational_review', execution_id, front=front, reason=reason)


def route_submission_return(engine, action, received, execution_id, output, *, rejected_submission=None):
    """Keep a bounded producer repair, then diagnose the preserved actual error."""
    retry = {**deepcopy(action), 'continuation_of': execution_id,
        'repair_attempt': action.get('repair_attempt', 0) + 1,
        'repair': {'execution_id': execution_id, 'previous_output': output,
            'retry_bundle_ids': received['retry_bundle_ids'],
            'bundle_results': received['bundles'], 'issues': received['issues']}}
    if rejected_submission:
        retry['repair'].update(deepcopy(rejected_submission))
    if retry['repair_attempt'] <= engine.instance['config']['max_output_repairs'] and not action.get('diagnosis_attempt'):
        engine.runtime.get('waiting_actions', {}).pop(action['id'], None)
        engine.runtime['queue'].append(retry)
        return
    engine.runtime.setdefault('waiting_actions', {})[action['id']] = {
        'action': retry, 'kind': 'output_validation', 'execution_id': execution_id,
        'reason': 'Producer repair was rejected again; diagnose the preserved contract and receiver errors',
        'next_owner': 'operations', 'detail': {'issues': deepcopy(received['issues'])}}
    route_failed_action(engine, action, execution_id,
        reason='Bounded submission repair exhausted; distinguish producer, input, contract and installation defects')


def initial_diagnosis_input(engine, action):
    if engine.instance['lifecycle']['state'] != 'initializing':
        raise ValueError('initial submission diagnosis requires initialization')
    execution = engine.runtime['executions'].get(action.get('target'), {})
    if execution.get('role') != 'intent_interpretation' or execution.get('status') != 'ended':
        raise ValueError('initial diagnosis must identify an ended interpretation')
    wait = engine.runtime.get('waiting_actions', {}).get(execution['action']['id'])
    if not wait or wait.get('kind') not in {'output_validation', 'execution_failure', 'submission_failure'} or wait.get('execution_id') != execution['id']:
        raise ValueError('initial diagnosis no longer owns this failure')
    engine._validate_initial_retry(wait, diagnostic_action_id=action.get('id'))
    return execution, wait


def apply_initial_diagnosis(engine, action, output, execution_id):
    failed, wait = initial_diagnosis_input(engine, action)
    decision = output['initial_submission_diagnosis']
    if not decision['guidance'].strip():
        raise ValueError('initial diagnosis requires concrete repair or waiting guidance')
    wait['diagnosis'] = {'execution_id': execution_id, **deepcopy(decision)}
    if decision['decision'] == 'wait':
        wait.update(reason=decision['guidance'], next_owner='maintenance')
        return
    if decision['decision'] != 'retry' or wait['action'].get('diagnosis_attempt'):
        raise ValueError('initial diagnosis allows one bounded follow-up, not repeated automatic diagnosis')
    # This runs inside an integration candidate. Native-final recovery publishes
    # evidence, so only the owner may continue after this diagnosis is committed.
    wait['next_owner'] = 'engine'


def continue_initial_retries(engine):
    if (engine.instance.get('lifecycle', {}).get('state') != 'initializing'
            or engine.runtime.get('status') in {'paused', 'closed', 'completed'}
            or engine.runtime.get('user_pause')):
        return
    for identifier in list(engine.runtime.get('waiting_actions', {})):
        wait = engine.runtime['waiting_actions'].get(identifier)
        if not wait:
            continue
        diagnosis = wait.get('diagnosis', {})
        reviewer = engine.runtime['executions'].get(diagnosis.get('execution_id'), {})
        if (diagnosis.get('decision') != 'retry' or diagnosis.get('retry_error')
                or reviewer.get('role') != 'maintenance' or reviewer.get('status') != 'ended'
                or reviewer.get('outcome') != 'output_accepted'
                or reviewer.get('action', {}).get('target') != wait.get('execution_id')
                or not reviewer.get('action', {}).get('initial_submission_diagnosis')):
            continue
        try:
            engine._continue_initial_execution(wait, request_id=reviewer['id'], diagnosis=diagnosis)
        except (ValueError, OSError, GitStateStoreError) as error:
            current = engine.runtime.get('waiting_actions', {}).get(identifier)
            if current:
                current['diagnosis']['retry_error'] = str(error)
                current.update(next_owner='maintenance', reason=str(error))
        engine._save()


def installation_fingerprint(root):
    root = Path(root)
    files = {path.relative_to(root).as_posix(): _digest(path.read_bytes())
        for path in root.rglob('*') if path.is_file() and '__pycache__' not in path.parts
        and (path.suffix in {'.py', '.md', '.ps1'} or path.name == 'requirements.txt')}
    return _digest(canonical_json(files))


def pending_installation_repair(runtime):
    rows = runtime.get('operational_dispositions', {}).values()
    for status in ('installation_repair_pending', 'installation_repair_waiting'):
        found = next((row for row in rows if row.get('status') == status), None)
        if found is not None:
            return found
    return None


def installation_failure(runtime, record):
    """Resolve a published independent diagnosis; a caller label is not authority."""
    current = runtime.get('operational_dispositions', {}).get(record.get('id'))
    reviewer = runtime.get('executions', {}).get(record.get('execution_id'), {})
    target = runtime.get('executions', {}).get(record.get('target_execution_id'), {})
    disposition = record.get('disposition', {})
    binding = record.get('result', {}).get('installation_repair', {})
    if (current != record or record.get('status') not in {'installation_repair_pending', 'installation_repair_waiting'}
            or reviewer.get('role') != 'operational_review' or reviewer.get('outcome') != 'output_accepted'
            or reviewer.get('status') != 'ended' or reviewer.get('action', {}).get('target') != target.get('id')
            or target.get('status') != 'ended' or not target.get('error')
            or disposition.get('kind') != 'repair' or disposition.get('meaning_preserving') is not True
            or not disposition.get('repair_target', '').startswith('installation:')
            or not binding.get('installation_sha256') or not binding.get('evidence_refs')):
        raise ValueError('installation repair requires a preserved accepted diagnosis of an ended failure')
    return {'kind': 'installation_defect', 'diagnosis_id': record['id'],
        'error': disposition['reason'], 'repair_target': disposition['repair_target'],
        'verification': disposition['verification'], 'target_execution_id': target['id'],
        'failure_sha256': _digest(canonical_json({'role': target.get('role'),
            'lineage': target.get('action', {}).get('lineage_id') or target.get('action', {}).get('id'),
            'target': target.get('action', {}).get('target'),
            'contract_sha256': target.get('contract_sha256'),
            'goal_revision': target.get('goal_revision'), 'policy_revision': target.get('policy_revision'),
            'decision_basis': target.get('decision_basis'),
            'issues': target.get('integration_result', {}).get('issues') or target['error']})),
        **{key: deepcopy(binding[key]) for key in ('installation_sha256', 'evidence_refs')}}


def validate_installation_target(disposition, target, root):
    if disposition.get('meaning_preserving') is not True:
        raise ValueError('installation repair cannot change research meaning or authority')
    root = Path(root)
    relative = disposition['repair_target'].removeprefix('installation:')
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or path.as_posix() != relative
            or any(p in {'.', '..'} or ':' in p or '\\' in p for p in path.parts)
            or not (root / relative).is_file() or not (root / relative).resolve().is_relative_to(root.resolve())):
        raise ValueError('installation repair target must name an existing file inside the installed skill')
    if target.get('status') != 'ended' or not target.get('error'):
        raise ValueError('installation repair requires a preserved ended failure')
    refs = [target[key] for key in ('result_ref', 'submission_check_ref', 'submitted_output_ref') if target.get(key)]
    if not refs:
        raise ValueError('installation defect has no preserved failure artifacts')
    return refs


def request_installation_repair(engine, record):
    disposition = record['disposition']
    root = Path(__file__).resolve().parents[2]
    target = engine.runtime['executions'][record['target_execution_id']]
    refs = validate_installation_target(disposition, target, root)
    record['status'] = 'installation_repair_pending'
    record.setdefault('result', {})['installation_repair'] = {
        'installation_sha256': installation_fingerprint(root), 'evidence_refs': refs}
    engine.runtime['operational_dispositions'][record['id']] = record
    engine._save()
    return deepcopy(engine.runtime['operational_dispositions'][record['id']])


def resume_installation_repair(runtime, record, *, repaired_by, at):
    """Resume the preserved rejected response, retaining its repair lineage."""
    target_id = record['target_execution_id']
    target = runtime['executions'][target_id]
    previous = runtime.get('waiting_actions', {}).get(target['action']['id'])
    action = activities.continue_activity(runtime, target_id, at=at,
        reason='verified_installation_repair:' + record['id'])
    if previous and previous.get('execution_id') == target_id:
        # The waiting request owns the latest returned bundles and error report.
        action.update(deepcopy(previous['action']), continuation_of=target_id,
                      owner_activity_id=target['owner_activity_id'])
        runtime['waiting_actions'].pop(target['action']['id'], None)
    record['status'] = 'applied'
    record.setdefault('result', {})['installation_repair'].update(
        status='repaired', repaired_by=repaired_by, continuation_action_id=action['id'])
    target.pop('pending_operational_disposition', None)
    runtime['status'] = 'ready'
    return action


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _input_path(workspace, relative):
    path = PurePosixPath(relative)
    if (not isinstance(relative, str) or path.as_posix() != relative or path.is_absolute()
            or len(path.parts) < 2 or path.parts[0] != "input"
            or any(p in {".", ".."} or ":" in p or "\\" in p for p in path.parts)):
        raise ValueError("repair target must be an exact sealed input path")
    destination = workspace.joinpath(*path.parts)
    boundary = PhysicalBoundary(workspace)
    # Check every existing parent, including Windows junctions, before writes.
    PhysicalBoundary(destination.parent)
    if not destination.parent.resolve().is_relative_to(workspace.absolute()):
        raise ValueError("repair parent escapes execution workspace")
    if destination.exists() or destination.is_symlink():
        with boundary.open(destination, "rb"):
            pass
    return destination, boundary


def _read_input(boundary, path):
    try:
        with boundary.open(path, "rb") as stream:
            return stream.read()
    except FileNotFoundError:
        return None


def _replace_input(boundary, path, raw):
    """Atomic same-directory replacement; no mutation of linked-file contents.

    This protects ordinary accidental path escape, not a hostile process with
    the same OS identity racing directory renames. The adopted boundary remains
    instructional, not OS isolation.
    """
    temporary = path.with_name(".repair-" + secrets.token_hex(12))
    try:
        with boundary.open(temporary, "xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _input_path(boundary.root, path.relative_to(boundary.root).as_posix())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _verify_input(boundary, path, binding):
    raw = _read_input(boundary, path)
    return {"sha256": None if raw is None else _digest(raw),
            "bytes": None if raw is None else len(raw),
            "passed": raw is not None and _digest(raw) == binding["sha256"] and len(raw) == binding["bytes"]}


def complete_repair(engine, record):
    """One hook for ENGINE._complete_operational_disposition, before its fallback.

    The caller holds the existing instance writer lock and has admitted this
    operational judgment. ``engine`` supplies instance/runtime/head/store and
    its ordinary ``_save(artifacts=None)`` CAS. Reacquire records after saves:
    ENGINE replaces its assembled views. Never fall through to a research retry.

    Supported request: repair_target is an exact manifest catalog/detail path;
    verification is exactly ``sha256:<that entry's hash>``. Other requests are
    returned with reason/next owner, not evaluated as programs. Only an ended
    execution's private input is restored from its immutable Git input bundle.
    The former provider is not restarted here. A verified repair opens its
    existing activity's explicit continuation, for ordinary fresh admission.
    """
    identifier = record["id"]
    current = engine.runtime.get("operational_dispositions", {}).get(identifier)
    if current is None or current != record:
        raise ValueError("repair must consume the current authoritative OD record")
    record = deepcopy(current)
    disposition = operational_dispositions.validate_disposition(record["disposition"])
    if disposition["kind"] != "repair":
        raise ValueError("complete_repair only consumes repair dispositions")
    if disposition['repair_target'].startswith('installation:'):
        if record['status'] in {'installation_repair_pending', 'installation_repair_waiting', 'applied'}:
            return record
        return request_installation_repair(engine, record)
    state = deepcopy(record.get("result", {}).get("repair", {}))
    if record["status"] == "applied" and state:
        if (not state.get("repair_effect") or not state.get("repair_resume")
                or state.get("repair_verification", {}).get("passed") is not True
                or state.get("repair_verification", {}).get("meaning_preserved") is not True):
            raise ValueError("applied repair lacks verified effects and explicit continuation")
        return record
    if record["status"] in {"repair_verification_failed", "repair_deferred"}:
        return record

    def defer(reason, owner="operational_review"):
        latest = deepcopy(engine.runtime["operational_dispositions"][identifier])
        latest["status"] = "repair_deferred"
        latest.setdefault("result", {})["followup"] = {"kind": "repair_requires_decision",
            "reason": reason, "next_owner": owner, "target_execution_id": record["target_execution_id"]}
        engine.runtime["operational_dispositions"][identifier] = latest
        engine._save()
        return deepcopy(engine.runtime["operational_dispositions"][identifier])

    target = engine.runtime["executions"][record["target_execution_id"]]
    reviewer = engine.runtime["executions"].get(record["execution_id"])
    if target["status"] != "ended":
        raise ValueError("input repair requires an ended predecessor")
    if not disposition["meaning_preserving"]:
        return defer("A semantic change needs a new research preparation judgment", "research_preparation")
    if not reviewer or reviewer.get("role") != "operational_review" or reviewer.get("action", {}).get("target") != target["id"]:
        return defer("Repair lacks the matching operational review execution")
    activity = engine.runtime["activities"][target["owner_activity_id"]]
    if activity["status"] == "finished" or any(engine.runtime["executions"][eid]["status"] != "ended"
            for eid in activity["assigned_execution_ids"]):
        return defer("Original activity is finished or has a live successor; do not overwrite its input")
    if not target.get("action", {}).get("id"):
        return defer("Original activity has no identified continuation action")

    def basis_refs():
        live_target = engine.runtime["executions"][target["id"]]
        action = engine.runtime["executions"][reviewer["id"]].get("action", {})
        refs = {live_target["id"], *action.get("observation_refs", []), *action.get("obligation_ids", [])}
        refs.update(ref for ref in (live_target.get("result_ref"),
            engine.runtime.get("checkpoints", {}).get(target["id"], {}).get("artifact_ref")) if ref)
        return refs

    if not operational_dispositions.disposition_is_current(disposition, basis_refs()):
        return defer("Operational judgment cites a basis outside its current input")
    try:
        profile = execution_profiles.resolve_profile(engine.instance["execution_profiles"], target["execution_profile_ref"])
        review_profile = execution_profiles.resolve_profile(engine.instance["execution_profiles"], reviewer["execution_profile_ref"])
        if review_profile["role"] != "operational_review" or review_profile["actor_kind"] != reviewer["actor_kind"]:
            raise ValueError("authorizing reviewer differs from its fixed execution profile")
        manifest = target["input_manifest"]
        if manifest.get("execution_profile_ref") != target["execution_profile_ref"] or profile["role"] != target["role"]:
            raise ValueError("sealed input and selected profile differ")
        bundle = target["input_bundle"]
        if not isinstance(bundle, str) or not bundle or any(c in bundle for c in "/\\:") or bundle in {".", ".."}:
            raise ValueError("input bundle is not one immutable artifact identity")
        base = "runtime/artifacts/" + bundle
        sealed_manifest = engine.store.read(base + "/manifest.json", engine.head)
        if json.loads(sealed_manifest) != manifest:
            raise ValueError("current execution manifest differs from sealed input manifest")
        relative = disposition["repair_target"]
        matches = [row for row in [*manifest.get("catalog", []), *manifest.get("detail_sources", [])]
                   if row.get("path") == relative]
        if len(matches) != 1:
            raise ValueError("repair target is not one exact sealed catalog/detail entry")
        entry = matches[0]
        if (not isinstance(entry.get("sha256"), str) or len(entry["sha256"]) != 64
                or type(entry.get("bytes")) is not int or entry["bytes"] < 0):
            raise ValueError("sealed entry needs a SHA-256 hash and integer byte length")
        if disposition["verification"] != "sha256:" + entry["sha256"]:
            raise ValueError("verification needs the exact supported sha256:<sealed hash> contract; prose is not executed")
        source_ref = base + "/" + relative
        if entry.get("artifact_ref", source_ref) != source_ref:
            raise ValueError("input entry names a different artifact bundle")
        raw = engine.store.read(source_ref, engine.head)
        if _digest(raw) != entry["sha256"] or len(raw) != entry["bytes"]:
            raise ValueError("sealed source bytes fail their manifest hash/length")
        workspace = Path(engine.instance["workspace"]).absolute() / "runs" / target["id"] / "workspace"
        destination, boundary = _input_path(workspace, relative)
        binding = {"kind": "restore_sealed_input", "executor": "engine_local_file_effect",
            "execution_id": target["id"], "authorizing_execution_id": reviewer["id"],
            "disposition_sha256": _digest(canonical_json(disposition)),
            "execution_profile_ref": target["execution_profile_ref"],
            "review_profile_ref": reviewer["execution_profile_ref"], "manifest_sha256": _digest(sealed_manifest),
            "source_ref": source_ref, "target": relative, "sha256": entry["sha256"], "bytes": entry["bytes"],
            "workspace": str(workspace)}
        if state and state.get("binding") != binding:
            raise ValueError("repair binding changed after its first effect intent")
    except (ValueError, KeyError, OSError, GitStateStoreError) as error:
        return defer(str(error))

    # Git seals the whole bundle on its first publication, not just each file.
    artifact_base = "runtime/artifacts/" + identifier + "-repair-"
    pending = {}
    if not state:
        before = _read_input(boundary, destination)
        state = {"binding": binding, "before_sha256": None if before is None else _digest(before),
                 "intent_ref": artifact_base + "intent/receipt.json"}
        pending[state["intent_ref"]] = canonical_json({**binding, "before_sha256": state["before_sha256"],
                                                     "effect_key": identifier + ":repair"})
    else:
        intent = json.loads(engine.store.read(state["intent_ref"], engine.head))
        if intent != {**binding, "before_sha256": state["before_sha256"], "effect_key": identifier + ":repair"}:
            return defer("Persisted repair intent differs from immutable evidence")

    def publish(value):
        nonlocal state
        saved = deepcopy(value)
        for field in ("repair_effect", "repair_verification", "repair_resume"):
            if field in saved:
                state[field] = saved.pop(field)
        saved.setdefault("result", {})["repair"] = deepcopy(state)
        if saved["status"] == "repair_verification_failed":
            saved["result"]["followup"] = {"kind": "repair_verification_failed", "next_owner": "operational_review",
                "reason": "Restored bytes did not match the same sealed input; no continuation opened"}
        engine.runtime["operational_dispositions"][identifier] = saved
        engine._save(artifacts=dict(pending) or None)
        pending.clear()

    def repair(plan):
        observed = _read_input(boundary, destination)
        digest = None if observed is None else _digest(observed)
        if digest != binding["sha256"]:
            if digest != state["before_sha256"]:
                raise RepairNeedsDecision("repair target changed after intent; independent reconciliation required")
            _replace_input(boundary, destination, raw)
        effect_ref = artifact_base + "effect/receipt.json"
        effect = {"execution_id": target["id"], "executor": "engine_local_file_effect",
            "authorizing_execution_id": reviewer["id"], "target": relative,
            "effect_key": plan["effect_key"], "effect_refs": [effect_ref]}
        pending[effect_ref] = canonical_json({**binding, "effect_key": plan["effect_key"],
                                            "intent_ref": state["intent_ref"]})
        return effect

    def verify(plan, effect):
        expected_ref = artifact_base + "effect/receipt.json"
        expected_receipt = {**binding, "effect_key": identifier + ":repair", "intent_ref": state["intent_ref"]}
        if (effect.get("execution_id") != target["id"] or effect.get("effect_refs") != [expected_ref]
                or json.loads(engine.store.read(expected_ref, engine.head)) != expected_receipt):
            raise RepairNeedsDecision("repair verification references a different effect or immutable receipt")
        facts = _verify_input(boundary, destination, binding)
        ref = artifact_base + "verification/receipt.json"
        proof = {"execution_id": target["id"], "executor": "engine_local_file_effect",
            "effect_key": plan["effect_key"], "passed": facts["passed"], "meaning_preserved": facts["passed"],
            "effect_refs": effect["effect_refs"], "evidence_refs": [ref]}
        pending[ref] = canonical_json({**proof, "observed": facts, "source_ref": source_ref,
                                     "expected_sha256": binding["sha256"], "expected_bytes": binding["bytes"]})
        return proof

    def resume(plan, verification):
        expected_ref = artifact_base + "verification/receipt.json"
        receipt = json.loads(engine.store.read(expected_ref, engine.head))
        if (verification.get("evidence_refs") != [expected_ref]
                or any(receipt.get(key) != value for key, value in verification.items())
                or receipt.get("expected_sha256") != binding["sha256"]
                or receipt.get("source_ref") != source_ref):
            raise RepairNeedsDecision("continuation lacks the exact immutable verification receipt")
        if not _verify_input(boundary, destination, binding)["passed"]:
            raise RepairNeedsDecision("verified input changed before continuation; no research was resumed")
        # The queue and OD applied receipt are saved together by publish below.
        action = activities.continue_activity(engine.runtime, target["id"], at=_now(),
            reason="verified_input_repair:" + identifier, next_owner="engine")
        return {"request_id": action["id"], "continuation_of": target["id"], "effect_key": plan["effect_key"],
                "owner_activity_id": target["owner_activity_id"], "verification_refs": verification["evidence_refs"]}

    value = deepcopy(record)
    value.update({k: deepcopy(state[k]) for k in ("repair_effect", "repair_verification", "repair_resume") if k in state})
    # Safe reconciliation is specific to this idempotent byte restoration and
    # read-only verifier. It is not permission to replay arbitrary repairs.
    reconciled = {"repair_running": "repair_required", "repair_verifying": "repair_verification_required",
                  "repair_resuming": "repair_resume_required"}
    value["status"] = reconciled.get(value["status"], value["status"])
    if value["status"] == "applied" and not state.get("repair_effect"):
        # The current ENGINE producer prelabels new ODs applied. No effect has
        # actually been accepted until this consumer publishes all three phases.
        value["status"] = "repair_required"
    try:
        operational_dispositions.execute_repair(value, target_execution=target, current_basis_refs=basis_refs,
            repair=repair, verify=verify, resume=resume, publish=publish)
    except RepairNeedsDecision as error:
        return defer(str(error))
    return deepcopy(engine.runtime["operational_dispositions"][identifier])
