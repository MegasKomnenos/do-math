"""Live coordination information, node and question leases, and session-owned declarations.

A section is an exact part of a node's question that an attempt or peer works on. A question is
an object of understanding that one explorer at a time occupies whole. Both are kept in the
registering session's declaration.json and last until that session's pipeline finishes review.
Choosing is serialized per node or question: one session at a time holds the lease, registers
and so passes the lease to the next waiting session. Leases and registrations are decided
first-wins under one instance lock."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time
import uuid
from availability import availability_view, retain_snapshot
from knowledge import ROOT_QUESTION, canonical, canonical_question, replay
from runtime_support import alive, read_json, write_json

CLAIM_LOCK_SECONDS = 30.0
WAIT_POLL_SECONDS = 1.0
SECTION_ROLES = ('attempt', 'peer')
QUESTION_ROLES = ('explore',)


@contextmanager
def claims_lock(instance):
    """One coordination change at a time per instance; the OS releases the lock if its holder dies."""
    path = Path(instance) / 'runner' / 'claims.lock'
    deadline = time.monotonic() + CLAIM_LOCK_SECONDS
    with path.open('a+b') as stream:
        if path.stat().st_size == 0:
            stream.write(b'0')
            stream.flush()
        while True:
            stream.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('another coordination change is still in progress; run the command again')
                time.sleep(0.05)
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def session_live(state, sid):
    """The broker's rule for an ended session: its stage is over, or its host and CLI are both gone."""
    session = (state or {}).get('sessions', {}).get(sid)
    if session is None or session['status'] not in ('starting', 'running'):
        return False
    return session.get('cli') is None or alive(session.get('host')) or alive(session.get('cli'))


def section_entries(instance, sid, model):
    """Sections one session declared."""
    path = Path(instance) / 'sessions' / sid / 'declaration.json'
    if not sid or not path.is_file():
        return []
    data = read_json(path)
    return [{**row, 'node': canonical(model, row['node']), 'session': sid} for row in data.get('sections', [])
            if row['node'] in model['nodes'] or row['node'] in model['aliases']]


def question_entry(instance, sid, model):
    """The question one explorer declared, or None while it is still choosing."""
    if not sid:
        return None
    path = Path(instance) / 'sessions' / sid / 'declaration.json'
    if not path.is_file():
        return None
    held = read_json(path).get('question')
    if not held or (held['id'] not in model['questions'] and held['id'] not in model['question_aliases']):
        return None
    return {**held, 'id': canonical_question(model, held['id']), 'session': sid}


def board(instance, state=None, model=None):
    """Producing work and its sections or question. A pipeline's occupancy ends with its review.

    An exploration's question is its producer's declared question, or the question the runner
    assigned in its job while the explorer has not yet been launched."""
    instance = Path(instance)
    state = state or read_json(instance / 'runner/state.json')
    model = model or replay(instance)
    rows = []
    for pid, pipeline in state['pipelines'].items():
        if pipeline['stage'] == 'done':
            continue
        owners = [pipeline['producer'], *pipeline.get('previous_peers', []), pipeline.get('peer')]
        sections = [s for sid in dict.fromkeys(x for x in owners if x) for s in section_entries(instance, sid, model)]
        question = None
        if pipeline['role'] == 'explore':
            held = question_entry(instance, pipeline['producer'], model)
            assigned = state['jobs'].get(pid + ':producer', {}).get('task', {}).get('question')
            if held:
                question = held['id']
            elif assigned and (assigned in model['questions'] or assigned in model['question_aliases']):
                question = canonical_question(model, assigned)
        rows.append({'pipeline': pid, 'session': pipeline['producer'], 'role': pipeline['role'],
                     'stage': pipeline['stage'] if pipeline['producer'] else 'queued',
                     'nodes': sorted({s['node'] for s in sections}), 'sections': sections,
                     'question': question,
                     'declared_at': min((s['at'] for s in sections if s.get('at')), default=None)})
    return rows


def question_availability(instance, state=None, model=None, rows=None):
    """Which questions an explorer could take now, and how many explorers are still choosing.

    A question is free when it is open, no unfinished exploration holds or was assigned it, and
    no live session holds or waits for its lease. Explorers still producing, or waiting to launch,
    whose pipelines have no question yet are choosing; an exploration that reached peer without one
    chooses nothing more. The runner launches another explorer only while free questions outnumber
    the choosing ones, so that each explorer launched can find a question. When it launches a
    pending exploration, it passes board rows without every pending exploration's pipeline: what a
    failed earlier launch of any of them held or was assigned is held by no live explorer and is
    free to whichever of them launches first (Runner.question_view)."""
    instance = Path(instance)
    state = state or read_json(instance / 'runner/state.json')
    model = model or replay(instance)
    rows = board(instance, state, model) if rows is None else rows
    occupied = {row['question']: row['session'] for row in rows if row['role'] == 'explore' and row['question']}
    leases = question_lease_table(instance, state, model)
    free = [qid for qid, q in model['questions'].items()
            if q['canonical'] == qid and q['state'] == 'open' and qid not in occupied and qid not in leases]
    # Only an explorer still producing, or still waiting to launch, can go on to choose; an
    # exploration that reached peer without a question will never take one.
    choosing = [row['pipeline'] for row in rows
                if row['role'] == 'explore' and not row['question'] and row['stage'] in ('producing', 'queued')]
    return {'free': free, 'occupied': occupied, 'choosing': choosing}


def normalize(table, state):
    """Drop holders and waiters whose sessions ended and give a free lease to the longest waiter."""
    result = {}
    for node, entry in table.items():
        holders = [h for h in entry.get('holders', []) if session_live(state, h['session'])]
        present = {h['session'] for h in holders}
        queue = []
        for waiter in sorted(entry.get('queue', []), key=lambda w: w['since']):
            if session_live(state, waiter['session']) and waiter['session'] not in present:
                present.add(waiter['session'])
                queue.append(waiter)
        if not holders and queue:
            head = queue.pop(0)
            holders = [{'session': head['session'], 'since': time.time(), 'waited_since': head['since']}]
        if holders or queue:
            result[node] = {'holders': holders, 'queue': queue}
    return result


def lease_table(instance, state=None, model=None):
    """Leases in force, keyed by canonical node. A merge of two leased nodes keeps both holders."""
    instance = Path(instance)
    state = state or read_json(instance / 'runner/state.json')
    model = model or replay(instance)
    path = instance / 'runner' / 'leases.json'
    merged = {}
    for node, entry in (read_json(path) if path.exists() else {}).items():
        if node in model['nodes'] or node in model['aliases']:
            target = merged.setdefault(canonical(model, node), {'holders': [], 'queue': []})
            target['holders'] += entry.get('holders', [])
            target['queue'] += entry.get('queue', [])
    return normalize(merged, state)


def question_lease_table(instance, state=None, model=None):
    """Question leases in force, keyed by canonical question; kept apart from node leases."""
    instance = Path(instance)
    state = state or read_json(instance / 'runner/state.json')
    model = model or replay(instance)
    path = instance / 'runner' / 'question-leases.json'
    merged = {}
    for question, entry in (read_json(path) if path.exists() else {}).items():
        if question in model['questions'] or question in model['question_aliases']:
            target = merged.setdefault(canonical_question(model, question), {'holders': [], 'queue': []})
            target['holders'] += entry.get('holders', [])
            target['queue'] += entry.get('queue', [])
    return normalize(merged, state)


def blocked(model, rows, node, pipeline):
    """Why no session of this pipeline can register on the node, or None."""
    if model['nodes'][node]['state'] != 'unresolved':
        return 'This node is not unresolved; read its evidence instead of choosing a section on it.'
    whole = [s for r in rows if r['pipeline'] != pipeline for s in r['sections'] if s['node'] == node and s['whole']]
    if whole:
        return 'Session ' + whole[0]['session'] + ' holds this whole node; no other section can be registered on it.'
    return None


def context(session):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    if inp['role'] not in SECTION_ROLES:
        raise ValueError('only attempts and peers register sections; other roles pursue their assigned responsibilities')
    return inp, Path(inp['instance'])


def known(model, node):
    if node not in model['nodes'] and node not in model['aliases']:
        raise ValueError('unknown node')
    return canonical(model, node)


def leave(table, sid, keep=None):
    """A session stands in at most one lease relation, so taking or joining one ends any other."""
    for node, entry in table.items():
        if node != keep:
            entry['holders'] = [h for h in entry['holders'] if h['session'] != sid]
            entry['queue'] = [w for w in entry['queue'] if w['session'] != sid]


def save(instance, table, state):
    write_json(Path(instance) / 'runner' / 'leases.json', normalize(table, state))


def view(node, table, rows):
    entry = table.get(node, {'holders': [], 'queue': []})
    return {'node': node, 'holders': [h['session'] for h in entry['holders']],
            'queue': [w['session'] for w in entry['queue']],
            'sections': [s for r in rows for s in r['sections'] if s['node'] == node]}


def lease(session, node):
    """Take a node's lease if no one holds it. A refusal records nothing."""
    inp, instance = context(session)
    sid = inp['session']
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        node = known(model, node)
        rows, table = board(instance, state, model), lease_table(instance, state, model)
        reason = blocked(model, rows, node, inp.get('pipeline'))
        entry = table.get(node, {'holders': [], 'queue': []})
        mine = any(h['session'] == sid for h in entry['holders'])
        if reason is None and entry['holders'] and not mine:
            reason = 'Another session holds this node\'s lease. Wait for it with commands.wait or choose another node.'
        if reason:
            return {'leased': False, 'reason': reason, **view(node, table, rows)}
        leave(table, sid, keep=node)
        if not mine:
            table[node] = {'holders': [{'session': sid, 'since': time.time()}], 'queue': entry['queue']}
        save(instance, table, state)
        return {'leased': True, **view(node, table, rows)}


def wait(session, node, timeout=None):
    """Join the node's queue and return once the lease is this session's, or at the timeout."""
    inp, instance = context(session)
    sid = inp['session']
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        with claims_lock(instance):
            model, state = replay(instance), read_json(instance / 'runner/state.json')
            node = known(model, node)
            rows, table = board(instance, state, model), lease_table(instance, state, model)
            reason = blocked(model, rows, node, inp.get('pipeline'))
            if reason:
                # Only this node's place ends; a place on another node is kept.
                entry = table.get(node)
                if entry:
                    entry['holders'] = [h for h in entry['holders'] if h['session'] != sid]
                    entry['queue'] = [w for w in entry['queue'] if w['session'] != sid]
                    save(instance, table, state)
                return {'leased': False, 'reason': reason, **view(node, table, rows)}
            entry = table.setdefault(node, {'holders': [], 'queue': []})
            if not any(x['session'] == sid for x in entry['holders'] + entry['queue']):
                leave(table, sid, keep=node)
                entry['queue'].append({'session': sid, 'since': time.time()})
            table = normalize(table, state)
            save(instance, table, state)
            if any(h['session'] == sid for h in table.get(node, {}).get('holders', [])):
                return {'leased': True, **view(node, table, rows)}
            position = [w['session'] for w in table[node]['queue']].index(sid) + 1
        if deadline is not None and time.monotonic() >= deadline:
            return {'leased': False, 'waiting': True, 'position': position, 'timeout': True,
                    'hint': 'Your place is kept; run wait again, or take another node.', **view(node, table, rows)}
        time.sleep(WAIT_POLL_SECONDS)


def release(session, node):
    """Give up a node's lease, or leave its queue, without registering a section."""
    inp, instance = context(session)
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        node = known(model, node)
        table = lease_table(instance, state, model)
        entry = table.get(node, {'holders': [], 'queue': []})
        entry['holders'] = [h for h in entry['holders'] if h['session'] != inp['session']]
        entry['queue'] = [w for w in entry['queue'] if w['session'] != inp['session']]
        save(instance, table, state)
        return {'released': True, **view(node, normalize(table, state), board(instance, state, model))}


def section(session, node, request_file):
    """Register a section while holding the node's lease; registration ends the lease.

    The tool refuses what it can decide: no lease, a settled node, a conflict with a whole-node
    section, an identical statement, or a missing non-overlap reason. Overlap itself is the
    registering session's judgement, recorded with its reasons."""
    inp, instance = context(session)
    sid = inp['session']
    request = read_json(request_file)
    whole = request.get('whole', False)
    reasons = request.get('reasons', {})
    if type(whole) is not bool or not isinstance(reasons, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in reasons.items()):
        raise ValueError('the request needs "whole" as Boolean and "reasons" mapping section IDs to text')
    statement = None if whole else request.get('statement')
    if not whole and not (isinstance(statement, str) and statement.strip()):
        raise ValueError('a section needs its exact "statement", or "whole": true for the whole node')
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        node = known(model, node)
        rows, table = board(instance, state, model), lease_table(instance, state, model)

        def refuse(reason):
            return {'registered': False, 'reason': reason, **view(node, table, rows)}

        if not any(h['session'] == sid for h in table.get(node, {}).get('holders', [])):
            return refuse('Take the node\'s lease with commands.lease or commands.wait before registering.')
        reason = blocked(model, rows, node, inp.get('pipeline'))
        if reason:
            return refuse(reason)
        existing = [s for r in rows for s in r['sections'] if s['node'] == node]
        others = [s for r in rows if r['pipeline'] != inp.get('pipeline') for s in r['sections'] if s['node'] == node]
        if whole and others:
            return refuse('Sections of other sessions exist on this node, so the whole node cannot be registered.')
        if whole and any(s['whole'] for s in existing):
            return refuse('Your processing already holds this whole node.')
        if not whole and any(s['statement'] and ' '.join(s['statement'].split()) == ' '.join(statement.split())
                             for s in existing):
            return refuse('A section with this exact statement is already registered on this node.')
        missing = [s['id'] for s in others if not reasons.get(s['id'], '').strip()]
        if missing:
            return refuse('State why your section does not overlap each of these sections: ' + ', '.join(missing))
        path = Path(session).resolve() / 'declaration.json'
        data = read_json(path) if path.exists() else {'sections': [], 'at': time.time()}
        data.setdefault('sections', [])
        entry = {'id': f'{sid}-{len(data["sections"]) + 1}', 'node': node, 'whole': whole, 'statement': statement,
                 'reasons': {s['id']: reasons[s['id']] for s in others}, 'at': time.time()}
        data['sections'].append(entry)
        write_json(path, data)
        table[node]['holders'] = [h for h in table[node]['holders'] if h['session'] != sid]
        save(instance, table, state)
        rows = board(instance, state, model)
        return {'registered': True, 'section': entry, **view(node, normalize(table, state), rows)}


def question_context(session):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    if inp['role'] not in QUESTION_ROLES:
        raise ValueError('only explorers occupy questions; other roles pursue their assigned responsibilities')
    return inp, Path(inp['instance'])


def known_question(model, question):
    if question not in model['questions'] and question not in model['question_aliases']:
        raise ValueError('unknown question')
    return canonical_question(model, question)


def question_blocked(model, rows, table, question, pipeline, sid):
    """Why no session of this pipeline can take the question, or None.

    While question 0 is free, a narrower question is refused: an explorer takes the root problem as
    a whole whenever no exploration holds it, and the runner's assignment at launch cannot reach an
    explorer that is already choosing when question 0 becomes free."""
    if model['questions'][question]['state'] != 'open':
        return 'This question is resolved; read its resolution instead of occupying it.'
    holder = next((r for r in rows if r['role'] == 'explore' and r['pipeline'] != pipeline and r['question'] == question), None)
    if holder:
        return ('Exploration ' + (holder['session'] or holder['pipeline'])
                + ' holds this question; one explorer at a time occupies a question.')
    if question != ROOT_QUESTION and root_free(rows, table, sid):
        return ('Question ' + ROOT_QUESTION + ', the root problem as a whole, is free, and an explorer takes it '
                'before any narrower question. Lease and take ' + ROOT_QUESTION + ' instead.')
    return None


def root_free(rows, table, sid):
    """Whether question 0 is free to this session, as the runner counts it free: no exploration
    holds it, and no other session holds or waits for its lease."""
    if any(r['role'] == 'explore' and r['question'] == ROOT_QUESTION for r in rows):
        return False
    entry = table.get(ROOT_QUESTION, {'holders': [], 'queue': []})
    return not any(x['session'] != sid for x in entry['holders'] + entry['queue'])


def question_view(question, table, rows):
    entry = table.get(question, {'holders': [], 'queue': []})
    return {'question': question, 'holders': [h['session'] for h in entry['holders']],
            'queue': [w['session'] for w in entry['queue']],
            'occupied_by': next((r['session'] for r in rows if r['role'] == 'explore' and r['question'] == question), None)}


def save_question_leases(instance, table, state):
    write_json(Path(instance) / 'runner' / 'question-leases.json', normalize(table, state))


def question_lease(session, question):
    """Take a question's lease if no one holds it. A refusal records nothing."""
    inp, instance = question_context(session)
    sid = inp['session']
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        question = known_question(model, question)
        rows, table = board(instance, state, model), question_lease_table(instance, state, model)
        reason = question_blocked(model, rows, table, question, inp.get('pipeline'), sid)
        entry = table.get(question, {'holders': [], 'queue': []})
        mine = any(h['session'] == sid for h in entry['holders'])
        if reason is None and entry['holders'] and not mine:
            reason = "Another session holds this question's lease. Wait for it with commands.question_wait or choose another question."
        if reason:
            return {'leased': False, 'reason': reason, **question_view(question, table, rows)}
        leave(table, sid, keep=question)
        if not mine:
            table[question] = {'holders': [{'session': sid, 'since': time.time()}], 'queue': entry['queue']}
        save_question_leases(instance, table, state)
        return {'leased': True, **question_view(question, table, rows)}


def question_wait(session, question, timeout=None):
    """Join the question's queue and return once the lease is this session's, or at the timeout."""
    inp, instance = question_context(session)
    sid = inp['session']
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        with claims_lock(instance):
            model, state = replay(instance), read_json(instance / 'runner/state.json')
            question = known_question(model, question)
            rows, table = board(instance, state, model), question_lease_table(instance, state, model)
            reason = question_blocked(model, rows, table, question, inp.get('pipeline'), sid)
            if reason:
                entry = table.get(question)
                if entry:
                    entry['holders'] = [h for h in entry['holders'] if h['session'] != sid]
                    entry['queue'] = [w for w in entry['queue'] if w['session'] != sid]
                    save_question_leases(instance, table, state)
                return {'leased': False, 'reason': reason, **question_view(question, table, rows)}
            entry = table.setdefault(question, {'holders': [], 'queue': []})
            if not any(x['session'] == sid for x in entry['holders'] + entry['queue']):
                leave(table, sid, keep=question)
                entry['queue'].append({'session': sid, 'since': time.time()})
            table = normalize(table, state)
            save_question_leases(instance, table, state)
            if any(h['session'] == sid for h in table.get(question, {}).get('holders', [])):
                return {'leased': True, **question_view(question, table, rows)}
            position = [w['session'] for w in table[question]['queue']].index(sid) + 1
        if deadline is not None and time.monotonic() >= deadline:
            return {'leased': False, 'waiting': True, 'position': position, 'timeout': True,
                    'hint': 'Your place is kept; run question_wait again, or take another question.',
                    **question_view(question, table, rows)}
        time.sleep(WAIT_POLL_SECONDS)


def question_release(session, question):
    """Give up a question's lease, or leave its queue, without taking the question."""
    inp, instance = question_context(session)
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        question = known_question(model, question)
        table = question_lease_table(instance, state, model)
        entry = table.get(question, {'holders': [], 'queue': []})
        entry['holders'] = [h for h in entry['holders'] if h['session'] != inp['session']]
        entry['queue'] = [w for w in entry['queue'] if w['session'] != inp['session']]
        save_question_leases(instance, table, state)
        return {'released': True, **question_view(question, normalize(table, state), board(instance, state, model))}


def question_take(session, question):
    """Occupy the whole question while holding its lease; taking it ends the lease.

    An explorer holds one question for its whole pipeline. The tool refuses what it can decide:
    no lease, a resolved question, a question another exploration holds, a question other than q0
    while q0 is free, or a second question."""
    inp, instance = question_context(session)
    sid = inp['session']
    with claims_lock(instance):
        model, state = replay(instance), read_json(instance / 'runner/state.json')
        question = known_question(model, question)
        rows, table = board(instance, state, model), question_lease_table(instance, state, model)

        def refuse(reason):
            return {'taken': False, 'reason': reason, **question_view(question, table, rows)}

        if not any(h['session'] == sid for h in table.get(question, {}).get('holders', [])):
            return refuse("Take the question's lease with commands.question_lease or commands.question_wait before occupying it.")
        reason = question_blocked(model, rows, table, question, inp.get('pipeline'), sid)
        if reason:
            return refuse(reason)
        path = Path(session).resolve() / 'declaration.json'
        data = read_json(path) if path.exists() else {'at': time.time()}
        if data.get('question'):
            return refuse('This session already occupies question ' + data['question']['id'] + '; an explorer holds one question.')
        data['question'] = {'id': question, 'at': time.time(), 'by': 'session'}
        write_json(path, data)
        table[question]['holders'] = [h for h in table[question]['holders'] if h['session'] != sid]
        save_question_leases(instance, table, state)
        rows = board(instance, state, model)
        return {'taken': True, 'question': question, 'at': data['question']['at'],
                **{k: v for k, v in question_view(question, normalize(table, state), rows).items() if k != 'question'}}


def updates(session):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    instance = Path(inp['instance'])
    with claims_lock(instance):
        model = replay(instance)
        state = read_json(instance / 'runner/state.json')
        rows = board(instance, state, model)
        snapshot = (retain_snapshot(session, availability_view(
            model, rows, state.get('attempt_availability_epoch', 0)))
            if inp['role'] == 'attempt' else None)
    received = [read_json(p) for p in sorted((session / 'inbox').glob('*.json'))]
    availability = question_availability(instance, state, model, rows)
    questions = [{'id': qid, 'statement': q['statement'], 'state': q['state'],
                  'occupied_by': availability['occupied'].get(qid), 'free': qid in availability['free']}
                 for qid, q in model['questions'].items() if q['canonical'] == qid]
    return {'revision': model['sequence'], 'root_state': model['nodes'][canonical(model, 'root')]['state'],
            'board': rows, 'leases': lease_table(instance, state, model),
            'questions': questions, 'question_leases': question_lease_table(instance, state, model),
            'availability_snapshot': snapshot,
            'concerns': model['concerns'],
            'comprehensive_reviews': [{k: j.get(k) for k in ('id', 'status', 'session', 'record', 'task')}
                               for j in state['jobs'].values() if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive'],
            'messages': received,
            'user_inputs': inp.get('user_inputs', [])}


def message(session, target, message_file):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    instance = Path(inp['instance'])
    state = read_json(instance / 'runner/state.json')
    if target not in state['sessions']:
        raise ValueError('unknown recipient session')
    text = Path(message_file).read_text(encoding='utf-8')
    if not text.strip():
        raise ValueError('empty coordination message')
    directory = instance / 'sessions' / target / 'inbox'
    directory.mkdir(exist_ok=True)
    name = uuid.uuid4().hex
    write_json(directory / (name + '.json'), {'id': name, 'from': inp['session'], 'at': time.time(), 'text': text})
    return {'delivered': str(directory / (name + '.json'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('updates', 'lease', 'wait', 'release', 'section', 'message',
                 'question-lease', 'question-wait', 'question-release', 'question-take'):
        p = sub.add_parser(name)
        p.add_argument('session', type=Path)
        if name in ('lease', 'wait', 'release', 'section'):
            p.add_argument('node')
        if name.startswith('question-'):
            p.add_argument('question')
        if name in ('wait', 'question-wait'):
            p.add_argument('--timeout', type=float, default=50.0)
        if name == 'section':
            p.add_argument('--file', required=True, type=Path)
        if name == 'message':
            p.add_argument('target')
            p.add_argument('--file', required=True, type=Path)
    args = parser.parse_args()
    try:
        code = 0
        if args.command == 'lease':
            result = lease(args.session, args.node)
            code = 0 if result['leased'] else 1
        elif args.command == 'wait':
            result = wait(args.session, args.node, args.timeout)
            code = 0 if result['leased'] else 124 if result.get('timeout') else 1
        elif args.command == 'release':
            result = release(args.session, args.node)
        elif args.command == 'section':
            result = section(args.session, args.node, args.file)
            code = 0 if result['registered'] else 1
        elif args.command == 'question-lease':
            result = question_lease(args.session, args.question)
            code = 0 if result['leased'] else 1
        elif args.command == 'question-wait':
            result = question_wait(args.session, args.question, args.timeout)
            code = 0 if result['leased'] else 124 if result.get('timeout') else 1
        elif args.command == 'question-release':
            result = question_release(args.session, args.question)
        elif args.command == 'question-take':
            result = question_take(args.session, args.question)
            code = 0 if result['taken'] else 1
        elif args.command == 'message':
            result = message(args.session, args.target, args.file)
        else:
            result = updates(args.session)
        print(json.dumps(result, ensure_ascii=True))
        return code
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
