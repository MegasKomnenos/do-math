"""Structured no-research outcomes and the state supporting an availability judgment.

The worker judges mathematical coverage. These helpers preserve that judgment's
grounds and detect changes that can open work; they never interpret report prose.
"""
import hashlib
import json
from pathlib import Path
import re

from knowledge import canonical
from runtime_support import read_json, write_json


def availability_view(model, rows, epoch=0):
    nodes = {nid: [] for nid, node in model['nodes'].items()
             if canonical(model, nid) == nid and node['state'] == 'unresolved'}
    for row in rows:
        for section in row['sections']:
            if section['node'] in nodes:
                nodes[section['node']].append(section['id'])
    return {'epoch': epoch, 'nodes': {n: sorted(set(ids)) for n, ids in nodes.items()}}


def snapshot_token(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def retain_snapshot(session, view):
    token = snapshot_token(view)
    path = Path(session) / 'availability' / (token + '.json')
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        write_json(path, view)
    return token


def normalized_nodes(view, model):
    """Node merges preserve registered sections, rather than falsely opening a new node."""
    result = {}
    for nid, sections in view['nodes'].items():
        if nid in model['nodes'] or nid in model['aliases']:
            result.setdefault(canonical(model, nid), set()).update(sections)
    return result


def opening_since(observed, current, model):
    previous = normalized_nodes(observed, model)
    for nid, sections in current['nodes'].items():
        if nid not in previous:
            return 'new_or_reopened_node'
        if previous[nid] - set(sections):
            return 'ended_occupancy'
    return None


def no_research_outcome(session, role):
    path = Path(session) / 'output/outcome.json'
    if not path.exists():
        return None
    value = read_json(path)
    if not isinstance(value, dict) or 'disposition' not in value:
        return None
    if role != 'attempt':
        raise ValueError('only attempts may declare disposition: no_research')
    if value['disposition'] != 'no_research':
        raise ValueError('disposition can only be no_research; omit it from the outcome of a session that undertook research')
    declaration = Path(session) / 'declaration.json'
    held = read_json(declaration) if declaration.exists() else {}
    if held.get('sections'):
        raise ValueError('no_research is incompatible with registered sections')
    return value


def reported_availability(session, outcome):
    """Validate the optional signal separately from the terminal session outcome."""
    report = outcome.get('availability')
    if report is None:
        return None
    if not isinstance(report, dict) or set(report) != {'status', 'snapshot'}:
        raise ValueError('availability needs status and snapshot')
    if report['status'] != 'all_unresolved_work_occupied':
        raise ValueError('unknown availability status')
    token = report['snapshot']
    if not isinstance(token, str) or not re.fullmatch(r'[0-9a-f]{64}', token):
        raise ValueError('availability.snapshot must be a token returned by updates')
    observed = read_json(Path(session) / 'availability' / (token + '.json'))
    if (not isinstance(observed, dict) or set(observed) != {'epoch', 'nodes'}
            or type(observed['epoch']) is not int or observed['epoch'] < 0
            or not isinstance(observed['nodes'], dict)
            or not all(isinstance(n, str) and isinstance(ids, list)
                       and all(isinstance(s, str) for s in ids)
                       for n, ids in observed['nodes'].items())
            or snapshot_token(observed) != token):
        raise ValueError('availability snapshot is invalid or changed')
    return observed
