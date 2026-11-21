"""Structured no-research outcomes and the state supporting an availability judgment.

The worker judges mathematical coverage. These helpers preserve that judgment's
grounds and detect changes that can open work; they never interpret report prose.
"""
import hashlib
import json
from pathlib import Path
import re

from runtime_support import read_json, write_json


def availability_view(model, rows, epoch):
    """The work that remains for the root, with the sections registered on each element of it."""
    elements = {name: [] for name in model['remaining']}
    # A section stands on the statement, so it occupies every proof of that statement that remains.
    statement = {name: model['elements'][name]['statement_of'] or name for name in elements}
    for row in rows:
        for section in row['sections']:
            for name in elements:
                if statement[name] == section['element']:
                    elements[name].append(section['id'])
    return {'epoch': epoch, 'elements': {n: sorted(set(ids)) for n, ids in elements.items()}}


def snapshot_token(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def retain_snapshot(session, view):
    token = snapshot_token(view)
    path = Path(session) / 'availability' / (token + '.json')
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        write_json(path, view)
    return token


def opening_since(observed, current, model):
    """Why work may have opened since a report of full occupancy: new remaining work, or an occupation that ended."""
    for name, sections in current['elements'].items():
        if name not in observed['elements']:
            return 'new_or_reopened_element'
        if set(observed['elements'][name]) - set(sections):
            return 'ended_occupancy'
    return None


def no_research_outcome(session, role):
    """An attempt that found no section, or an explorer that found no free question, ends here.

    Either session registered nothing and did nothing beyond assessing availability. Only an
    attempt judges whether all the work that remains is occupied, so only its outcome may report it."""
    path = Path(session) / 'output/outcome.json'
    if not path.exists():
        return None
    value = read_json(path)
    if not isinstance(value, dict) or 'disposition' not in value:
        return None
    if role not in ('attempt', 'explore'):
        raise ValueError('only attempts and explorers may declare disposition: no_research')
    if value['disposition'] != 'no_research':
        raise ValueError('disposition can only be no_research; omit it from the outcome of a session that undertook research')
    declaration = Path(session) / 'declaration.json'
    held = read_json(declaration) if declaration.exists() else {}
    if held.get('sections'):
        raise ValueError('no_research is incompatible with registered sections')
    if held.get('question'):
        raise ValueError('no_research is incompatible with an occupied question')
    if role == 'explore' and 'availability' in value:
        raise ValueError('only attempts report the availability of unresolved work')
    return value


def reported_availability(session, outcome):
    """Validate the optional signal separately from the terminal session outcome."""
    report = outcome.get('availability')
    if report is None:
        return None
    if not isinstance(report, dict) or set(report) != {'status', 'snapshot'}:
        raise ValueError('availability needs exactly the fields status and snapshot, and no others')
    if report['status'] != 'all_unresolved_work_occupied':
        raise ValueError('unknown availability status')
    token = report['snapshot']
    well_formed = isinstance(token, str) and re.fullmatch(r'[0-9a-f]{64}', token)
    # A token of the right form that updates never retained for this session is equally not one of its tokens.
    path = Path(session) / 'availability' / (token + '.json') if well_formed else None
    if path is None or not path.exists():
        raise ValueError('availability.snapshot must be a token returned by updates')
    observed = read_json(path)
    if (not isinstance(observed, dict) or set(observed) != {'epoch', 'elements'}
            or type(observed['epoch']) is not int or observed['epoch'] < 0
            or not isinstance(observed['elements'], dict)
            or not all(isinstance(n, str) and isinstance(ids, list)
                       and all(isinstance(s, str) for s in ids)
                       for n, ids in observed['elements'].items())
            or snapshot_token(observed) != token):
        raise ValueError('availability snapshot is invalid or changed')
    return observed
