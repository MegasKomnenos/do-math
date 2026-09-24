"""Initialization and activation contracts, using the owners' sealed records."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import shutil

from .state_contract import STATE_FORMAT_VERSION, STATE_CONTRACT_ID
from .execution_profiles import resolve_profile
from .governance import timestamp
from .repository import canonical_json, new_id

INITIAL_ROLES = {"intent_interpretation", "maintenance"}
FOUNDATION_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def original_input_bytes(record):
    """Return and verify the one exact UTF-8 representation of immutable input."""
    if not isinstance(record.get('text'), str):
        raise ValueError('immutable input text is missing')
    raw = record['text'].encode('utf-8')
    if record.get('sha256') != hashlib.sha256(raw).hexdigest() or record.get('bytes') != len(raw):
        raise ValueError('immutable input bytes or hash differs')
    return raw


def adapter_for(profile):
    from .codex_adapter import CodexExecAdapter
    from .claude_adapter import ClaudePrintAdapter
    provider = profile["ai"]["provider"]
    if provider == "claude":
        return ClaudePrintAdapter(shutil.which("claude") or "claude")
    if provider == "codex":
        return CodexExecAdapter(shutil.which("codex") or "codex")
    raise ValueError("unsupported profile provider")


def capability_requirements(instance, reference, required=(), *, current_identity=None, at=None):
    """Use exact profile/host/implementation evidence, never profile booleans."""
    missing = sorted(set(required))
    try:
        profile = resolve_profile(instance.get("execution_profiles", {}), reference)
        missing = sorted(set(required) | set(profile.get("required_capabilities", [])))
        if profile["actor_kind"] == "machine":
            return {"satisfied": not missing, "missing": missing, "profile_ref": reference, "evidence_refs": []}
        identity = current_identity if current_identity is not None else adapter_for(profile).capability_identity()
        current_time = timestamp(at)
        evidence = [row for row in instance.get("capability_evidence", {}).values()
                    if row.get("execution_profile_ref") == reference and row.get("identity") == identity
                    and row.get('id') == 'CE-' + digest({key: value for key, value in row.items() if key != 'id'})
                    and timestamp(row["observed_at"]) <= current_time]
        # The most recent observation supersedes older contradictory claims.
        evidence.sort(key=lambda row: (timestamp(row["observed_at"]), row["id"]))
        facts = {}
        structural = None
        for row in evidence:
            facts.update(row.get("capabilities", {}))
            job = row.get('capabilities', {}).get('atomic_local_job', {})
            if job.get('status') == 'unsupported' and job.get('scope') == 'actual_local_start_failure':
                structural = row['id']
            # Help/version output cannot clear a concrete failed local start.
        missing = [name for name in missing if facts.get(name, {}).get("status") != "supported"]
        if structural and 'atomic_local_job' not in missing:
            missing.append('atomic_local_job')
        return {"satisfied": bool(evidence) and not missing, "missing": missing,
                "profile_ref": reference, "evidence_refs": [row["id"] for row in evidence]}
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {"satisfied": False, "missing": missing, "profile_ref": reference, "reason": str(exc)}


def trust_environment_errors(environment, *, verify_files=True):
    """Validate the approved manifest and its exact currently installed bytes."""
    if not isinstance(environment, dict):
        return ["trust environment absent"]
    manifest = environment.get("manifest", {})
    errors = []
    from .formal import toolchain_errors
    errors.extend(toolchain_errors(environment.get('toolchain')))
    if not isinstance(manifest, dict) or environment.get("manifest_sha256") != digest(manifest):
        return ["trust manifest missing or changed"]
    if set(manifest) != {"command", "foundation_profile", "files", "validation"}:
        errors.append("trust manifest fields differ from the current contract")
    if not environment.get("source_ref"):
        errors.append("trust environment has no explicit adoption")
    if set(environment.get("allowed_axioms", [])) != FOUNDATION_AXIOMS:
        errors.append("foundation axiom profile differs")
    foundation = manifest.get("foundation_profile", {})
    if foundation.get("allowed_axioms") != sorted(FOUNDATION_AXIOMS) or not {"sorryAx", "Lean.trustCompiler", "additional_axioms"}.issubset(foundation.get("forbidden", [])):
        errors.append("foundation profile is incomplete")
    command = environment.get("toolchain", {}).get("configured_command")
    if not command or manifest.get("command") != command:
        errors.append("manifest command differs from toolchain")
    files = manifest.get("files", [])
    required_roles = {"lean_binary", "lean_source", "lake_binary", "mathlib_source", "mathlib_build", "checker"}
    if not isinstance(files, list) or not required_roles.issubset({r.get("role") for r in files if isinstance(r, dict)}):
        errors.append("manifest lacks required source, binary, build or checker evidence")
    else:
        paths = set()
        for entry in files:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not Path(entry["path"]).is_absolute():
                errors.append("manifest file must have an absolute path")
                continue
            path = Path(entry["path"])
            resolved = str(path.resolve()).casefold()
            if resolved in paths:
                errors.append("duplicate manifest path")
            paths.add(resolved)
            if verify_files:
                try:
                    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
                        errors.append("trust file changed: " + str(path))
                except OSError:
                    errors.append("trust file unavailable: " + str(path))
    validation = manifest.get("validation", {})
    if validation.get("status") != "verified" or not validation.get("evidence_refs"):
        errors.append("trust validation evidence absent")
    return errors


def governance_basis(instance):
    return digest(instance.get('governance', {}))


def require_trust_environment(instance, runtime):
    """Check the actual current environment at a formal-use admission boundary."""
    if any(row.get('status') in {'checking', 'ready'} for row in runtime.get('trust_transitions', {}).values()):
        raise ValueError('formal admission is blocked during a trust transition')
    environment = instance.get('trust_environments', {}).get(instance.get('active_trust_environment'))
    errors = trust_environment_errors(environment)
    if not environment or environment.get('status') != 'active' or errors:
        raise ValueError('approved fixed trust environment required: ' + '; '.join(errors))
    return deepcopy(environment)


def governance_working_view(instance):
    """Ephemeral input for readers; never publish these derived authority fields."""
    from .governance import governance_view
    return {**instance, **governance_view(instance)}


def initial_intent_evidence(instance, runtime, *, owner_handlers=None):
    """Resolve the sealed, independently checked and actually applied original."""
    from .governance import _current_import, validate_independent_execution
    lifecycle = instance['lifecycle']
    original = lifecycle['immutable_input']
    original_bytes = original_input_bytes(original)
    original_sha256 = hashlib.sha256(original_bytes).hexdigest()
    for row in reversed(list(runtime.get('intent_imports', {}).values())):
        if row.get('input_ref') != lifecycle.get('input_id') or row.get('superseded_by'):
            continue
        bundle = _current_import(instance, runtime, row['id'], owner_handlers=owner_handlers)
        check, application = bundle.get('check', {}), bundle.get('application', {})
        expected_units = {u['unit_id'] for u in bundle['output']['import_units'] if u['payload']}
        if (bundle['source']['sha256'] != original_sha256 or bundle['source']['text'].encode('utf-8') != original_bytes
                or any(q.get('blocks') for q in bundle['output'].get('question_details', [])) or bundle['status'] != 'approved'
                or check.get('decision') != 'approved' or check.get('scope_complete') is not True
                or check.get('bundle_sha256') != bundle['sha256']
                or check.get('sha256') != digest({k:v for k,v in check.items() if k != 'sha256'})
                or application.get('status') != 'applied' or application.get('import_id') != bundle['id']
                or set(application.get('applied_units', [])) != expected_units):
            raise ValueError('initial input requires a sealed, fully checked applied import')
        validate_independent_execution(runtime, check['execution_id'], [bundle['execution_id']])
        checker = runtime['executions'][check['execution_id']]
        if (checker.get('role') != 'intent_interpretation' or checker.get('intent_import_sha256') != bundle['sha256']
                or bundle['execution_id'] not in runtime['executions']):
            raise ValueError('initial interpretation execution evidence does not resolve')
        return {'input_sha256': original_sha256, 'interpretation_execution_id': bundle['execution_id'],
                'check_execution_id': check['execution_id']}
    raise ValueError('initial input has no applied independent import')


def operations_capacity_available(instance, runtime):
    """Read approved concurrency/cumulative limits through the Git ledger view."""
    from .session_slots import SessionSlots
    if not instance.get('capacity_constraints') or not instance.get('role_profile_refs'):
        return False
    slots = SessionSlots(runtime, instance, observer=True)
    return any(cell['available'] > 0 for cell in slots.snapshot()['operations'].values())


def activation_requirements(instance, runtime, *, at=None, owner_handlers=None):
    """Evaluate current evidence; none of these checks creates authority."""
    lifecycle = instance.get("lifecycle", {})
    adoption = lifecycle.get("adoption", {})
    missing = []
    source = lifecycle.get("immutable_input", {})
    try:
        if not original_input_bytes(source):
            raise ValueError('empty original')
    except (ValueError, KeyError, TypeError):
        missing.append("immutable_input")
    if adoption.get("governance_sha256") != governance_basis(instance):
        missing.append("governance")
    try:
        from .governance import validate_governance_state
        validate_governance_state(instance)
        governance_working_view(instance)
    except (ValueError, KeyError, TypeError):
        missing.append('governance')
    if adoption.get("config_sha256") != digest(instance.get("config", {})):
        missing.append("configuration")
    if instance.get("conversation_loss_policy") not in {"pause", "continue_authorized"}:
        missing.append("conversation_policy")
    if "external_policy" not in adoption:
        missing.append("external_policy")
    try:
        if lifecycle.get('intent_check') != initial_intent_evidence(instance, runtime, owner_handlers=owner_handlers):
            raise ValueError('initial intent receipt differs from applied import')
    except (ValueError, KeyError, TypeError):
        missing.append("independent_intent")
    policy = instance.get("review_policy")
    try:
        from .review_policy import build_review_policy
        build_review_policy(policy)
        if adoption.get("review_policy_sha256") != digest(policy):
            raise ValueError("review policy not adopted")
    except (ValueError, TypeError):
        missing.append("review_policy")
    env = instance.get("trust_environments", {}).get(instance.get("active_trust_environment"))
    if not env or env.get("status") != "active" or trust_environment_errors(env):
        missing.append("trust_environment")
    references = adoption.get("profile_refs", [])
    if not references:
        missing.append("profiles")
    from .execution_profiles import resolve_profile
    from .observations import observation_settings_errors
    observation_errors = []
    # Dispatch uses role_profile_refs after activation; a narrow bootstrap
    # adoption must not hide incomplete profiles that will then be selected.
    selected = [*references, *(ref for refs in instance.get('role_profile_refs', {}).values() for ref in refs)]
    checked_profiles = set()
    for ref in selected:
        try:
            profile = resolve_profile(instance['execution_profiles'], ref)
        except (ValueError, KeyError, TypeError):
            missing.append('profiles')
            continue
        if profile['id'] in checked_profiles:
            continue
        checked_profiles.add(profile['id'])
        observation_errors.extend(observation_settings_errors(profile))
    if observation_errors:
        missing.append('observation_configuration')
    for ref in references:
        if not capability_requirements(instance, ref, at=at)["satisfied"]:
            missing.append("capability_evidence")
            break
    grants = adoption.get("research_grant_ids", [])
    now = timestamp(at)
    if not grants or any(not grant_current(instance, gid, now, initial=False) for gid in grants):
        missing.append("research_authority")
    if not operations_capacity_available(instance, runtime):
        missing.append("operations_capacity")
    if not runtime.get("recovery_checked"):
        missing.append("recovery_check")
    if any(row.get("status") in {"checking", "ready"} for row in runtime.get("trust_transitions", {}).values()):
        missing.append("trust_transition")
    return {"satisfied": not missing, "missing": list(dict.fromkeys(missing)),
            "observation_errors": observation_errors,
            "trust_environment_id": instance.get("active_trust_environment")}


def grant_current(instance, gid, at, *, initial):
    grant = instance.get("grants", {}).get(gid, {})
    if grant.get("kind") != "local" or grant.get("status") != "active" or not grant.get("source_ref"):
        return False
    if initial and (not grant.get("expires_at") or not set(grant.get("roles", [])).issubset(INITIAL_ROLES)
                    or grant.get("budget_kind") != "operations" or grant.get('reuse') != 'reusable'):
        return False
    if not initial and (grant.get("initialization_only") or gid in
                        instance.get('lifecycle', {}).get('adoption', {}).get('initial_grant_ids', [])):
        return False
    return bool(grant.get("roles")) and (not grant.get("expires_at") or timestamp(grant["expires_at"]) > at) and (
        not grant.get("valid_from") or timestamp(grant["valid_from"]) <= at)


def initialize_state(*, instance_id, goal, workspace, config, source_input,
                     title="", policies="", created_at=None):
    if not isinstance(source_input, str) or not source_input.strip():
        raise ValueError("initialization requires the original nonempty input")
    when = timestamp(created_at).isoformat()
    raw = source_input.encode('utf-8')
    input_id = new_id('UI')
    instance = {"id": instance_id, "feature_version": STATE_FORMAT_VERSION, "title": title or goal[:80],
        'contract_id': STATE_CONTRACT_ID,
        "config": deepcopy(config),
        "workspace": str(workspace), "created_at": when, "knowledge": {}, "relations": [],
        "sources": [], "goal_judgments": [], "goal_status": "unsolved", "grants": {}, "decisions": {},
        "governance": {}, "governance_sources": {},
        "trust_environments": {}, "active_trust_environment": None,
        "lifecycle": {"state": "initializing", "immutable_input": {
            "text": source_input, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)},
            'input_id': input_id,
            "adoption": {}, "activation": {}}}
    runtime = {"feature_version": STATE_FORMAT_VERSION, "status": "initializing",
        'contract_id': STATE_CONTRACT_ID,
        "availability": {"state": "blocked", "reason": "initialization_incomplete"},
        "tasks": {}, "executions": {}, "activities": {}, "queue": [], "history": [],
        "inputs": [{'id': input_id, 'text': source_input, 'sha256': hashlib.sha256(raw).hexdigest(),
                    'config': {'goal': goal, 'policies': policies}, 'created_at': when}],
        "questions": [], "question_links": [], "events": [], "pending_events": [],
        "last_observed_utc": when, "recovery_checked": False,
        "review_cycles": {}, "external_operations": {}, "trust_transitions": {}, "conversations": {},
        "checkpoints": {}, "observations": {}, "condition_states": {}, "extended_controls": {}}
    instance["lifecycle"]["activation"]["missing"] = activation_requirements(instance, runtime, at=when)["missing"]
    return instance, runtime
