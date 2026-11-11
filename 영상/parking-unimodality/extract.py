"""Extract a time-stamped event timeline from a do-math instance for the film.

Sources, all inside the instance: knowledge/events, knowledge/records|reviews|organizations|questions
(replayed with do-math's own knowledge model so node and question states follow its semantics),
sessions/*/{launch,input,declaration,termination}.json and GO, control/{inputs,retired-inputs,pause-formalization},
settings.json and the per-session settings snapshots. Output: timeline.json next to this script.
"""
import json, os, sys, time, datetime
from pathlib import Path

INSTANCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803')
RUNTIME = Path(r'C:\math\.agents\skills\do-math\runtime')
OUT = Path(__file__).resolve().parent / 'timeline.json'
sys.path.insert(0, str(RUNTIME))
import knowledge  # noqa: E402
from runtime_support import read_json  # noqa: E402


def mtime(p):
    return os.path.getmtime(p)


# ---------- knowledge replay with per-event snapshots ----------
root_statement = (INSTANCE / 'root.md').read_text(encoding='utf-8-sig')
model = knowledge.new_model(root_statement)
events = sorted((read_json(p) for p in (INSTANCE / 'knowledge/events').glob('*.json')), key=lambda e: e['sequence'])
handlers = {'record': knowledge.record_event, 'review': knowledge.assessment_event,
            'organization': knowledge.organization_event, 'questions': knowledge.questions_event}

nodes, questions, relations, proofs, records, ev_out = {}, {}, {}, {}, {}, []
node_state, q_state = {}, {}
t_start = time.time()
for ev in events:
    t = float(ev['at'])
    handlers[ev['kind']](model, ev, INSTANCE / 'knowledge' / ev['folder'])
    model['sequence'] = ev['sequence']
    knowledge.settle(model)
    ev_out.append({'id': ev['id'], 'kind': ev['kind'], 'seq': ev['sequence'], 't': t,
                   'session': ev.get('session'), 'role': ev.get('producer_role')})
    if ev['kind'] == 'record':
        r = model['records'][ev['id']]
        records[ev['id']] = {'id': ev['id'], 't': t, 'seq': ev['sequence'], 'role': r['producer_role'],
                             'session': ev.get('session'), 'title': r['title']}
    for nid, n in model['nodes'].items():
        if nid not in nodes:
            nodes[nid] = {'id': nid, 'birth': t, 'source': n.get('source'), 'transitions': [], 'alias_of': None}
        can = n.get('canonical', nid)
        if can != nid and nodes[nid]['alias_of'] is None:
            nodes[nid]['alias_of'] = can
            nodes[nid]['alias_t'] = t
        st = n.get('state', 'unresolved')
        if node_state.get(nid) != st:
            node_state[nid] = st
            nodes[nid]['transitions'].append([t, st])
    for qid, q in model['questions'].items():
        if qid not in questions:
            questions[qid] = {'id': qid, 'birth': t if q.get('source') else None, 'origin': q.get('origin'),
                              'source': q.get('source'), 'transitions': []}
        st = q.get('state', 'open')
        if q_state.get(qid) != st:
            q_state[qid] = st
            questions[qid]['transitions'].append([t, st])
    for rid, r in model['relations'].items():
        if rid not in relations:
            relations[rid] = {'id': rid, 'birth': t, 'record': r['record'],
                              'premises': [[knowledge.canonical(model, p['node']), p['outcome']] for p in r['premises']],
                              'conclusion': [knowledge.canonical(model, r['conclusion']['node']), r['conclusion']['outcome']]}
    for pid, p in model['direct'].items():
        if pid not in proofs:
            proofs[pid] = {'id': pid, 'birth': t, 'node': knowledge.canonical(model, p['node']), 'level': p['level'],
                           'outcome': p['outcome'], 'record': p['record']}
print(f'replayed {len(events)} events in {time.time()-t_start:.1f}s', file=sys.stderr)

# final-state check against the instance's own state.json
final = read_json(INSTANCE / 'knowledge/state.json')
mismatch = [(k, v['state'], node_state.get(k)) for k, v in final['nodes'].items() if v['state'] != node_state.get(k)]
print('state mismatches vs state.json:', mismatch, file=sys.stderr)

# depth to root along relations (conclusion -> premises)
children = {}
for r in relations.values():
    children.setdefault(r['conclusion'][0], set()).update(p[0] for p in r['premises'])
depth = {'root': 0}
frontier = ['root']
while frontier:
    nxt = []
    for u in frontier:
        for v in children.get(u, ()):
            if v not in depth:
                depth[v] = depth[u] + 1
                nxt.append(v)
    frontier = nxt
for nid in nodes:
    nodes[nid]['depth'] = depth.get(nodes[nid]['alias_of'] or nid)

# ---------- sessions ----------
sessions = {}
sdir = INSTANCE / 'sessions'
for d in sorted(sdir.iterdir()):
    try:
        launch = read_json(d / 'launch.json')
        inp = read_json(d / 'input.json')
    except Exception as e:
        print('skip', d.name, e, file=sys.stderr)
        continue
    ec = launch.get('end_check') or {}
    role = ec.get('role') or inp.get('role')
    argv = (launch.get('command') or {}).get('argv') or []
    model_name = ec.get('model') or next((argv[i + 1] for i, a in enumerate(argv[:-1]) if a == '--model'), None)
    start = mtime(d / 'GO') if (d / 'GO').exists() else mtime(d / 'input.json')
    end = None
    if (d / 'termination.json').exists():
        end = float(read_json(d / 'termination.json')['at'])
    s = {'id': d.name, 'role': role, 'model': model_name, 'start': start, 'end': end,
         'pipeline': inp.get('pipeline'), 'nodes': [], 'question': None, 'producer': None}
    if (d / 'declaration.json').exists():
        dec = read_json(d / 'declaration.json')
        s['nodes'] = sorted({sec['node'] for sec in dec.get('sections', [])})
        if dec.get('question'):
            s['question'] = dec['question']['id']
        s['declared_at'] = dec.get('at')
    task = inp.get('task') or {}
    if task.get('source'):
        s['producer'] = Path(task['source']).name
    if task.get('node'):
        s['nodes'] = sorted(set(s['nodes']) | {task['node']})
    sessions[d.name] = s
# a producer that published a record but left no declaration is placed on the nodes its record touched
touched = {}
for nid, n in nodes.items():
    if n['source']:
        touched.setdefault(n['source'], set()).add(nid)
for p in proofs.values():
    touched.setdefault(p['record'], set()).add(p['node'])
for r in relations.values():
    touched.setdefault(r['record'], set()).add(r['conclusion'][0])
for rec in records.values():
    s = sessions.get(rec['session'])
    if s is not None and not s['nodes'] and not s['question'] and rec['id'] in touched:
        # only nodes that already existed when the session started: a node the record itself
        # proposes is born at publication, after the session ended, and must not be pointed at early
        existing = sorted(n for n in touched[rec['id']] if nodes[n]['birth'] < s['start'] or n == 'root')
        if existing:
            s['nodes'] = existing
            s['target_from'] = 'record'
# peer/review inherit the producer's targets
for s in sessions.values():
    p = sessions.get(s['producer']) if s['producer'] else None
    if p:
        if not s['nodes']:
            s['nodes'] = list(p['nodes'])
        if not s['question']:
            s['question'] = p['question']
        s['producer_role'] = p['role']
# explorers without a question object (before 2026-11-09) investigated the root problem itself
for s in sessions.values():
    if s['role'] == 'explore' and not s['question'] and not s['nodes']:
        s['question'] = 'q0'
    if s.get('producer_role') == 'explore' and not s['question'] and not s['nodes']:
        s['question'] = 'q0'

# ---------- operator rule changes ----------
rules = []


def first_line(p):
    return p.read_text(encoding='utf-8-sig').splitlines()[0].lstrip('# ').strip()


for sub, retired in (('control/inputs', False), ('control/retired-inputs', True)):
    for p in sorted((INSTANCE / sub).iterdir()):
        t = int(p.name.split('-')[0]) / 1e9
        title = first_line(p)
        # the initial conditions are the birth, the writing preference changes no rule, and the pause
        # input repeats the pause-formalization control file published a minute earlier
        shown = not ('독립적인 새 연구의 조건' in title or '글쓰기' in title or '형식화의 임시 보류' in title)
        rules.append({'t': t, 'kind': 'input', 'label': title, 'shown': shown, 'retired': retired, 'file': p.name})
pause = INSTANCE / 'control/pause-formalization'
if pause.exists():
    rules.append({'t': mtime(pause), 'kind': 'pause-formalization', 'label': 'formalization paused', 'shown': True})
for ev in events:
    if ev['kind'] == 'questions':
        rules.append({'t': float(ev['at']), 'kind': 'questions',
                      'label': 'question system introduced; operator questions published', 'shown': True})
# settings change points from per-session snapshots, plus the live file
snap = []
for d in sdir.iterdir():
    try:
        st = read_json(d / 'input.json')['settings']
    except Exception:
        continue
    snap.append((mtime(d / 'input.json'), st.get('max_sessions'), st.get('explore_every')))
observed = Path(__file__).resolve().parent / 'observed-settings.json'
if observed.exists():                           # edits that no session launch recorded; see the file's note
    for o in json.loads(observed.read_text(encoding='utf-8'))['observations']:
        snap.append((float(o['epoch']), o.get('max_sessions'), o.get('explore_every')))
snap.sort()
live = read_json(INSTANCE / 'settings.json')
snap.append((mtime(INSTANCE / 'settings.json'), live.get('max_sessions'), live.get('explore_every')))
prev = None
for t, ms, ee in snap:
    cur = (ms, ee)
    if prev is not None and cur != prev:
        parts = []
        if ms != prev[0]:
            parts.append(f'max_sessions {prev[0]} to {ms}')
        if ee != prev[1]:
            parts.append(f'explore_every {prev[1]} to {ee}')
        rules.append({'t': t, 'kind': 'settings', 'label': ', '.join(parts), 'shown': True})
    prev = cur
rules.sort(key=lambda r: r['t'])

t0 = mtime(INSTANCE / 'root.md')
cutoff = time.time()
out = {'meta': {'instance': str(INSTANCE), 't0': t0, 'cutoff': cutoff, 'extracted_at': cutoff,
                'root_statement': root_statement,
                'counts': {'events': len(ev_out), 'nodes': len(nodes), 'relations': len(relations), 'proofs': len(proofs),
                           'questions': len(questions), 'sessions': len(sessions),
                           'rules_shown': sum(r['shown'] for r in rules)}},
       'events': ev_out, 'records': records, 'nodes': nodes, 'relations': relations, 'proofs': proofs,
       'questions': questions, 'sessions': sessions, 'rules': rules}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')


def fmt(t):
    return datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M')


print('wrote', OUT, out['meta']['counts'], file=sys.stderr)
print('root transitions:', [(fmt(t), s) for t, s in nodes['root']['transitions']], file=sys.stderr)
print('rules shown:', [(fmt(r['t']), r['kind'], r['label'][:40]) for r in rules if r['shown']], file=sys.stderr)
print('sessions without target:', sum(1 for s in sessions.values() if not s['nodes'] and not s['question']),
      'by role:', {r: sum(1 for s in sessions.values() if s['role'] == r and not s['nodes'] and not s['question'])
                   for r in ('attempt', 'explore', 'formalizer', 'peer', 'review', 'organizer')}, file=sys.stderr)

# a browser page opened from file:// cannot fetch JSON, so the same data is also written as a script
(OUT.parent / 'timeline.js').write_text('window.TIMELINE=' + OUT.read_text(encoding='utf-8') + ';', encoding='utf-8')
