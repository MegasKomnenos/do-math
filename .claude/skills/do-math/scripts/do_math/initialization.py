"""Initialization and activation contracts, using the owners' sealed records."""
from __future__ import annotations

from copy import deepcopy

from .execution_profiles import match_profile_ref
from .governance import grant_time_reason, source_record, timestamp
from .repository import exact_content_hash, new_id

INITIAL_ROLES = {"intent_interpretation", "maintenance"}


def original_input_bytes(record):
    """Return and verify the one exact UTF-8 representation of immutable input."""
    text = record.get('text')
    if not isinstance(text, str):
        raise ValueError('immutable input text is missing')
    if any(record.get(key) != value for key, value in source_record(text).items()):
        raise ValueError('immutable input bytes or hash differs')
    return text.encode('utf-8')


def adapter_for(profile):
    from .claude_adapter import provider_adapter
    return provider_adapter(profile["ai"]["provider"])


def capability_requirements(instance, reference, *, current_identity=None, at=None):
    """Use exact profile/host/implementation evidence, never profile booleans."""
    missing = []
    try:
        profile = match_profile_ref(instance.get("execution_profiles", {}), reference)
        missing = sorted(set(profile.get("required_capabilities", [])))
        if profile["actor_kind"] == "machine":
            return {"satisfied": not missing, "missing": missing, "profile_ref": reference, "evidence_refs": []}
        identity = current_identity if current_identity is not None else adapter_for(profile).capability_identity()
        current_time = timestamp(at)
        evidence = [row for row in instance.get("capability_evidence", {}).values()
                    if row.get("execution_profile_ref") == reference and row.get("identity") == identity
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


def _capability_batch_requirements(instance, references, *, at=None):
    """Observe each provider once for this check; validate every exact profile."""
    identities = {}
    for reference in references:
        try:
            profile = match_profile_ref(instance.get("execution_profiles", {}), reference)
            identity = None
            if profile["actor_kind"] == "ai":
                adapter = adapter_for(profile)
                key = (profile['ai']['provider'], adapter.observation_key())
                if key not in identities:
                    identities[key] = adapter.capability_identity()
                identity = identities[key]
            yield capability_requirements(instance, reference, current_identity=identity, at=at)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            yield {"satisfied": False, "profile_ref": reference, "reason": str(exc)}


def governance_basis(instance):
    return exact_content_hash(instance.get('governance', {}))


def governance_or_initial_view(instance, runtime):
    """Governance view of one state; before charter adoption, the original input stands in."""
    from .governance import governance_view
    lifecycle = instance.get("lifecycle", {}).get("state")
    unadopted = lifecycle == "initializing" or (lifecycle == "paused" and (
        runtime.get("resume_lifecycle") == "initializing" or
        runtime.get("status") == "closed" and not instance["lifecycle"].get("activated_at")))
    if unadopted and not any(row.get("kind") == "charter" and row.get("status") == "active"
                            for row in instance.get("governance", {}).values()):
        initial_input = next(row for row in runtime["inputs"]
                             if row["id"] == instance["lifecycle"]["input_id"])
        return {**deepcopy(initial_input["config"]), "policies": "",
                "status": "unadopted_input", "goal_revision": 0, "policy_revision": 0,
                "source": deepcopy(instance["lifecycle"]["immutable_input"])}
    return governance_view(instance)


def governance_working_view(instance):
    """Ephemeral input for readers; never publish these derived authority fields."""
    from .governance import governance_view
    return {**instance, **governance_view(instance)}


def initial_intent_evidence(instance, runtime, *, owner_handlers=None):
    """Resolve the sealed, independently checked and actually applied original."""
    from .governance import current_import, validate_independent_execution
    lifecycle = instance['lifecycle']
    original = lifecycle['immutable_input']
    original_input_bytes(original)
    original_sha256 = original['sha256']
    for row in reversed(list(runtime.get('intent_imports', {}).values())):
        if row.get('input_ref') != lifecycle.get('input_id') or row.get('superseded_by'):
            continue
        bundle = current_import(instance, runtime, row['id'], owner_handlers=owner_handlers)
        check, application = bundle.get('check', {}), bundle.get('application', {})
        expected_units = {u['unit_id'] for u in bundle['output']['import_units'] if u['payload']}
        if (bundle['source']['sha256'] != original_sha256 or bundle['source']['text'] != original['text']
                or any(q.get('blocks') for q in bundle['output'].get('question_details', [])) or bundle['status'] != 'approved'
                or check.get('decision') != 'approved' or check.get('scope_complete') is not True
                or check.get('bundle_sha256') != bundle['sha256']
                or check.get('sha256') != exact_content_hash({k:v for k,v in check.items() if k != 'sha256'})
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


def observed_profile_refs(instance):
    """The current role profile references: the editions dispatch selects from.

    Adopting the configuration adopts these editions; activation checks their
    observation settings and capability evidence.
    """
    return [ref for refs in instance.get('role_profile_refs', {}).values() for ref in refs]


# Windows a Lean compile consumes: one call outlasting the tool review window
# opens an operational review. The self-check response window is not one of
# them, because research calls hold that deadline (ObservationTracker._hold_deadlines).
COMPILE_BOUND_WINDOWS = ('tool_review_window_seconds',)


def observation_window_warnings(instance, runtime):
    """Used observation windows shorter than a registered toolchain's representative compile.

    A window shorter than one compile expires while the worker waits on that
    compile. This is advice returned with adoption results, never a refusal;
    an unreadable toolchain record gives no warning because activation checks it.
    """
    from .observations import observation_settings_used
    from .trust_inventory import read_record, representative_check_seconds
    compiles = {}
    for environment_id, environment in instance.get('trust_environments', {}).items():
        if environment.get('status') == 'invalid':
            continue
        try:
            record = read_record(environment['toolchain_record']['path'])
            baseline = record['baselines'][runtime['trust_bindings'][environment_id]['baseline']]
            compiles[environment_id] = representative_check_seconds(baseline['validation'])
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            continue
    warnings, seen = [], set()
    for ref in observed_profile_refs(instance):
        try:
            profile = match_profile_ref(instance['execution_profiles'], ref)
        except (ValueError, KeyError, TypeError):
            continue
        if profile['id'] in seen:
            continue
        seen.add(profile['id'])
        settings = profile['observation']['settings']
        for field in observation_settings_used(profile):
            if field not in COMPILE_BOUND_WINDOWS or not isinstance(settings.get(field), int):
                continue
            for environment_id, seconds in compiles.items():
                if settings[field] < seconds:
                    warnings.append({'role': profile['role'], 'profile_id': profile['id'], 'field': field,
                                     'window_seconds': settings[field], 'environment_id': environment_id,
                                     'representative_check_seconds': seconds})
    return warnings


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
    if adoption.get("config_sha256") != exact_content_hash(instance.get("config", {})):
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
        if adoption.get("review_policy_sha256") != exact_content_hash(policy):
            raise ValueError("review policy not adopted")
    except (ValueError, TypeError):
        missing.append("review_policy")
    from .trust_validation import environment_errors
    env = instance.get("trust_environments", {}).get(instance.get("active_trust_environment"))
    if (not env or env.get("status") != "active"
            or environment_errors(env, runtime.get("trust_bindings", {}).get(instance.get("active_trust_environment")))):
        missing.append("trust_environment")
    references = observed_profile_refs(instance)
    if not references:
        missing.append("profiles")
    from .observations import observation_settings_errors
    observation_errors = []
    checked_profiles = set()
    for ref in references:
        try:
            profile = match_profile_ref(instance['execution_profiles'], ref)
        except (ValueError, KeyError, TypeError):
            missing.append('profiles')
            continue
        if profile['id'] in checked_profiles:
            continue
        checked_profiles.add(profile['id'])
        observation_errors.extend(observation_settings_errors(profile))
    if observation_errors:
        missing.append('observation_configuration')
    for capability in _capability_batch_requirements(instance, references, at=at):
        if not capability["satisfied"]:
            missing.append("capability_evidence")
            break
    grants = adoption.get("research_grant_ids", [])
    now = timestamp(at)
    if not grants or any(not grant_current(instance, gid, now, initial=False) for gid in grants):
        missing.append("research_authority")
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
                    or grant.get('reuse') != 'reusable'):
        return False
    if not initial and (grant.get("initialization_only") or gid in
                        instance.get('lifecycle', {}).get('adoption', {}).get('initial_grant_ids', [])):
        return False
    return bool(grant.get("roles")) and grant_time_reason(grant, at) is None


def initialize_state(*, instance_id, goal, workspace, config, source_input,
                     title="", created_at=None):
    if not isinstance(source_input, str) or not source_input.strip():
        raise ValueError("initialization requires the original nonempty input")
    when = timestamp(created_at).isoformat()
    original = source_record(source_input)
    input_id = new_id('UI')
    instance = {"id": instance_id, "title": title or goal[:80],
        "config": deepcopy(config),
        "workspace": str(workspace), "created_at": when, "knowledge": {}, "relations": [],
        "sources": [], "goal_judgments": [], "goal_status": "unsolved", "grants": {}, "decisions": {},
        "governance": {}, "governance_sources": {},
        "trust_environments": {}, "active_trust_environment": None,
        "lifecycle": {"state": "initializing", "immutable_input": original,
            'input_id': input_id,
            "adoption": {}, "activation": {}}}
    runtime = {"status": "initializing",
        "availability": {"state": "blocked", "reason": "initialization_incomplete"},
        "tasks": {}, "executions": {}, "activities": {}, "queue": [], "history": [],
        "inputs": [{'id': input_id, 'text': source_input, 'sha256': original['sha256'],
                    'config': {'goal': goal}, 'created_at': when}],
        "questions": [], "question_links": [], "events": [], "pending_events": [],
        "cycles": 0, "processed_controls": [], "reservations": {}, "provider_waits": {},
        "updated_at": when, "last_observed_utc": when, "recovery_checked": False,
        "review_cycles": {}, "external_operations": {}, "trust_transitions": {}, "conversations": {},
        "checkpoints": {}, "observations": {}, "extended_controls": {}}
    instance["lifecycle"]["activation"]["missing"] = activation_requirements(instance, runtime, at=when)["missing"]
    return instance, runtime
