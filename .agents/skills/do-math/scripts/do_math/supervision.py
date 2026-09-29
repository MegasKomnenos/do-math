"""Supervision rules shared by the scheduled operator, the engine and the status report (layer 2).

Which persisted facts may stop supervision from starting research or repair, in
which priority, and the shape of an operator report.
"""
from copy import deepcopy
from typing import Any

# Supervision blockers in priority order; the first present one decides.
# ``held`` is the local HOLD file and ``disabled`` the operator setting.
SUPERVISION_BLOCKS = ('held', 'disabled', 'user_pause', 'maintenance', 'model_policy',
                      'paused', 'closed', 'completed', 'conversation_lost', 'installation_repair')

OPERATOR_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"}, "observed_status": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "user_questions": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
    },
    "required": ["summary", "observed_status", "actions", "evidence_paths", "user_questions", "next_step"],
}


def hold_pause_reason(hold_id: str) -> str:
    """The user pause a HOLD requests; its release resumes only this exact pause."""
    return "User requested scheduled operator HOLD " + hold_id


def supervision_facts(instance: dict, runtime: dict) -> dict[str, Any]:
    """The persisted facts that decide whether supervision may start research or repair."""
    from .repair_execution import pending_installation_repair
    return {'status': runtime.get('status'), 'user_pause': deepcopy(runtime.get('user_pause')),
            'maintenance_fence': deepcopy(runtime.get('maintenance_fence')),
            'model_policy_violation': deepcopy(runtime.get('model_policy_violation')),
            'conversation_lost': (runtime.get('stop_requested') == 'conversation_lost'
                                  and instance.get('conversation_loss_policy') == 'pause'),
            'installation_repair': deepcopy(pending_installation_repair(runtime)),
            'operator_enabled': instance.get('config', {}).get('operator_enabled') is True}


def supervision_block(facts: dict[str, Any]) -> str | None:
    """The first supervision blocker present in ``facts``, or None.

    Facts without ``held`` or ``operator_enabled`` never report those blockers;
    a persisted-state view or an explicit engine start omits them.
    """
    present = {'held': facts.get('held'),
               'disabled': 'operator_enabled' in facts and not facts['operator_enabled'],
               'user_pause': facts.get('user_pause'), 'maintenance': facts.get('maintenance_fence'),
               'model_policy': facts.get('model_policy_violation'),
               'conversation_lost': facts.get('conversation_lost'),
               'installation_repair': facts.get('installation_repair'),
               **{state: facts.get('status') == state for state in ('paused', 'closed', 'completed')}}
    return next((code for code in SUPERVISION_BLOCKS if present[code]), None)
