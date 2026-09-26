"""Validation and disclosure boundaries for operational-review dispositions.

This module records a reviewer's proposed operational action.  It deliberately
does not mutate executions, activities, tasks, or permissions: ENGINE applies
an accepted proposal only after its own currentness and authority checks.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def validate_disposition(disposition: dict[str, Any]) -> dict[str, Any]:
    """Return a detached v5 disposition or raise before any state transition.

    The producer receives contracts.disposition_schema; this check reads the
    variant of the same schema that the disposition's kind names.
    """
    import jsonschema
    from .contracts import disposition_schema
    variants = {row["properties"]["kind"]["const"]: row for row in disposition_schema()["anyOf"]}
    if not isinstance(disposition, dict) or disposition.get("kind") not in variants:
        raise ValueError("operational disposition kind is unsupported")
    error = jsonschema.exceptions.best_match(
        jsonschema.Draft202012Validator(variants[disposition["kind"]]).iter_errors(disposition))
    if error is not None:
        raise ValueError("operational disposition " + disposition["kind"]
                         + "".join(f"/{part}" for part in error.absolute_path) + ": " + error.message)
    return deepcopy(disposition)


def admissible_basis_refs(instance, runtime, action):
    """Canonical operational evidence, shared by input production and application."""
    from .revisions import action_repetition_waits
    target = runtime.get('executions', {}).get(action.get('target'))
    if target is None:
        raise ValueError('operational disposition has no execution target')
    refs = {target['id'], *action.get('observation_refs', []), *action.get('obligation_ids', [])}
    refs.update(hold['event_ref'] for hold in action_repetition_waits(instance, runtime, target.get('action', {})))
    refs.update(ref for ref in (target.get('result_ref'),
        runtime.get('checkpoints', {}).get(target['id'], {}).get('artifact_ref')) if ref)
    from .activities import successor_state
    successor=successor_state(runtime,target['id'])
    for identifier in successor['execution_ids'] if successor else []:
        refs.add(identifier)
        result=runtime['executions'][identifier].get('result_ref')
        if result:refs.add(result)
    return sorted(refs)


def require_basis_refs(disposition, allowed):
    """Reject source paths or other visible records that are not disposition evidence."""
    invalid = sorted(set(disposition['basis_refs']) - set(allowed))
    if invalid:
        raise ValueError('operational disposition cites evidence outside its current input; '
                         'invalid_basis_refs=' + repr(invalid) + '; admissible_basis_refs=' + repr(sorted(allowed)))




def worker_feedback(disposition: dict[str, Any]) -> dict[str, Any]:
    """Expose only information a worker needs; diagnostics remain with ENGINE."""
    from .observations import worker_feedback as public_feedback
    checked = validate_disposition(disposition)
    return public_feedback({key: checked[key] for key in ("kind", "reason", "next_owner")})


def reconcile_recovery(runtime: dict, record: dict) -> bool:
    """Settle an obsolete recovery proposal without duplicating its successor."""
    if record.get('status') == 'superseded':
        return True
    if record['disposition']['kind'] not in {'retry', 'resume'}:
        return False
    # A successfully applied retry already owns the successor it created.
    if record.get('result', {}).get('continuation_action_id'):
        return False
    from .activities import successor_state
    successor = successor_state(runtime, record['target_execution_id'])
    if successor is None:
        return False
    record['status'] = 'superseded'
    record.setdefault('result', {})['successor'] = successor
    target = runtime['executions'][record['target_execution_id']]
    if target.get('pending_operational_disposition') == record['id']:
        target.pop('pending_operational_disposition')
    return True
