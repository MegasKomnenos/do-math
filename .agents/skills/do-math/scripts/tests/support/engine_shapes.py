"""Malformed control payloads of the engine region's control shape tests, with the shape check's reasons.

``ACTIONS`` is every public control action, from the product's own list
(``control_contracts.PAYLOADS``) and ``configure``, so a new action is covered.
``NOT_OBJECTS`` are configurations that are not objects. ``BAD_PAYLOADS`` are
``(action, config, reason)``: an object whose nested structure is wrong, and the
exact reason ``control_contracts.validate_control_payload`` gives for it.
``inbox(sim)`` is the instance's control inbox folder.
"""
from pathlib import Path

from do_math.control_contracts import PAYLOADS

ACTIONS = (*PAYLOADS, 'configure')
NOT_OBJECTS = ([], [1], False, 0, 'text')
NOT_OBJECT = 'config: invalid type (expected object)'
BAD_PAYLOADS = [
    ('decision', {'change': []}, 'config/change: invalid type (expected object)'),
    ('decision', {'change': {'kind': 'charter', 'record': {'kind': 'charter', 'content': []}}},
     'config/change/record/content: invalid type (expected object)'),
    ('decision', {'change': {'kind': 'grant', 'grant': {'kind': 'local', 'roles': ['maintenance'], 'expires_at': 1}}},
     "config/change/grant/expires_at: invalid type (expected ['string', 'null'])"),
    ('decision', {'change': {'kind': 'initialization', 'operation': 'probe', 'profile_ref': []}},
     'config/change/profile_ref: invalid type (expected object)'),
    ('request', {'role': 'maintenance', 'review_replacement': {'action': []}},
     'config/review_replacement/action: invalid type (expected object)'),
    ('request', {'role': 'maintenance', 'review_restoration': {'action': []}},
     'config/review_restoration/action: invalid type (expected object)'),
    ('knowledge', {'operation': 'import', 'candidate': []}, 'config/candidate: invalid type (expected object)'),
    ('knowledge', {'operation': 'import-relation', 'relation': []}, 'config/relation: invalid type (expected object)'),
    ('knowledge', {'operation': 'revise', 'id': 'KN-one', 'changes': [], 'reason': 'test'},
     'config/changes: invalid type (expected object)'),
    ('trust', {'operation': 'register', 'toolchain': [], 'manifest': {}, 'allowed_axioms': []},
     'config/toolchain: invalid type (expected object)'),
    ('external', {'operation': 'reconcile', 'id': 'EO-one', 'evidence': []}, 'config/evidence: invalid type (expected object)'),
    ('conversation', {'operation': 'attach', 'id': 'one', 'generation': [], 'lease_seconds': 60},
     'config/generation: invalid type (expected integer)'),
]


def inbox(sim):
    return Path(sim.instance['workspace']) / 'control' / sim.instance_id
