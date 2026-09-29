"""The ingress kind (설계 3.3; 의무 2-A): every input the owner loop receives rejects malformed shapes in its own form.

An ingress takes outside input into the state: a public control action, a
workspace submission, a provider event, an observation, a control transport
request. Its contract has three parts: it rejects only in its declared form
(a ``ValueError`` from its check, a rejection record), never with another
exception; a rejected item is consumed exactly once; a valid item after it is
still processed.

``CONTROL_ACTIONS`` are the public control actions, generated from the
product's own list (``control_contracts.PAYLOADS``) so a new action is covered
without being declared here. ``malformed(schema)`` makes the wrong shapes for
one JSON schema: values that are not the declared object, and for each declared
property a value of another type and a value outside its enumeration; the
workspace-relative path fields a caller names also get an empty, root, parent
and drive path. Every shape is outside the schema, so a check that follows its
schema rejects each one. Other ingress groups join by a table and a test of the
same form in their region.
"""
from __future__ import annotations

WRONG = {
    'string': [0, None, [], {}],
    'array': ['x', 0, None, {}],
    'object': [[], 'x', 0, None],
    'integer': ['1', None, 1.5, True],
    'number': ['1', None, True],
    'boolean': ['true', 0, None],
    'null': ['x', 0],
}
NOT_OBJECTS = [None, [], 0, 'x', True]
NOT_TEXTS = [None, [], {}, 0, True]
PATHS = ['', '/', '..', '../outside', 'C:\\']


def _types(schema):
    declared = schema.get('type')
    return set(declared) if isinstance(declared, list) else {declared} if declared else set()


def malformed(schema, *, paths=()):
    """``(label, value)`` wrong shapes for ``schema``; each is outside what the schema accepts.

    ``paths`` names the properties that hold workspace-relative paths.
    """
    rows = [('not an object: ' + repr(value), value) for value in NOT_OBJECTS if 'object' in _types(schema)
            and not (value is None and 'null' in _types(schema))]
    for name, prop in sorted(schema.get('properties', {}).items()):
        allowed = _types(prop)
        for kind in sorted(allowed):
            for value in WRONG.get(kind, []):
                if not any(_is_type(value, other) for other in allowed):
                    rows.append((f'{name}: {value!r} for {kind}', {name: value}))
        if 'enum' in prop:
            rows.append((f'{name}: outside its enumeration', {name: 'not-a-member'}))
        if name in paths:
            rows += [(f'{name}: path {value!r}', {name: value}) for value in PATHS]
    return rows


def _is_type(value, kind):
    return {'string': isinstance(value, str), 'array': isinstance(value, list), 'object': isinstance(value, dict),
            'integer': type(value) is int, 'number': type(value) in (int, float), 'boolean': type(value) is bool,
            'null': value is None}.get(kind, False)


def control_actions():
    """``{action: payload schema}`` for every action the control check accepts.

    That is every entry of ``control_contracts.PAYLOADS`` and ``configure``, whose
    schema is the configuration vocabulary (``_configure_validator``).
    """
    from do_math.control_contracts import PAYLOADS, _configure_validator
    return {**PAYLOADS, 'configure': _configure_validator().schema}
