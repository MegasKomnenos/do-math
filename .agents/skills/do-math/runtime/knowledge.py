"""Replay reviewed publications into research state. Prose is never interpreted."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from runtime_support import read_json, write_json, write_text


def claim_key(ref, local=None):
    return ref if isinstance(ref, str) else (local if ref['record'] == 'self' and local else ref['record']) + '/' + ref['claim']


def canonical(model, node):
    seen = set()
    while node in model['aliases']:
        if node in seen:
            raise ValueError('node alias cycle')
        seen.add(node)
        node = model['aliases'][node]
    return node


def new_model(statement):
    return {'nodes': {'root': {'id': 'root', 'statement': statement, 'source': None}},
            'aliases': {}, 'claims': {}, 'direct': {}, 'relations': {}, 'proofs': {},
            'records': {}, 'concerns': {}, 'terms': {}, 'global_terms': {},
            'modules': [], 'shared_context': [], 'organized': [], 'dependency_overrides': {},
            'findings': [], 'sequence': 0}


def flip(outcome):
    return 'refuted' if outcome == 'proved' else 'proved'


def concerned(model, key, concern, seen=None):
    """Whether a claim rests, directly or through its dependencies, on a target of an open concern."""
    if concern['status'] == 'cleared':
        return False
    if key in concern['targets']:
        return True
    visited = set(seen or ())
    if key in visited:
        return False
    visited.add(key)
    return any(concerned(model, dep, concern, visited)
               for dep in model['claims'].get(key, {}).get('dependencies', []))


def clause(model, relation):
    """A relation as a propositional clause: each premise negated, the conclusion as written."""
    items = [(canonical(model, p['node']), flip(p['outcome'])) for p in relation['premises']]
    items.append((canonical(model, relation['conclusion']['node']), relation['conclusion']['outcome']))
    return items


def settle(model):
    """Hold every supported solution and relation true and draw their propositional consequences.

    A supported direct solution is a fact. A supported relation is a clause: whenever all of
    its signed statements but one are established, the remaining one follows, in whichever
    direction that is. A node established both ways is contested; its statements are not
    used to derive anything further until review resolves the opposition. A concern only
    annotates the outcomes that rest on the questioned claim.
    """
    direct = {}
    for pid, proof in model['direct'].items():
        if model['claims'].get(proof['claim'], {}).get('status') != 'supported':
            continue
        node = canonical(model, proof['node'])
        concerns = sorted(cid for cid, c in model['concerns'].items() if concerned(model, proof['claim'], c))
        direct[pid] = {**proof, 'node': node, 'claims': [proof['claim']], 'nodes': [node],
                       'formal_dependencies': model['dependency_overrides'].get(pid, proof.get('formal_dependencies', [])),
                       'concerns': concerns, 'concerned': bool(concerns)}
    relations = {rid: r for rid, r in model['relations'].items()
                 if model['claims'].get(r['claim'], {}).get('status') == 'supported'}

    def derive(excluded):
        proofs = dict(direct)

        def uses(pid, target):
            pending, visited = [pid], set()
            while pending:
                current = pending.pop()
                if current == target:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                pending.extend(proofs.get(current, {}).get('premise_proofs', []))
            return False

        changed = True
        while changed:
            changed = False
            for rid, relation in relations.items():
                literals = clause(model, relation)
                for index, (node, outcome) in enumerate(literals):
                    forward = index == len(literals) - 1
                    pid = rid if forward else f'{rid}~{index}'
                    needed = [(n, flip(o)) for i, (n, o) in enumerate(literals) if i != index]
                    selected = []
                    for n, o in needed:
                        if n in excluded:
                            break
                        candidates = sorted((p['concerned'], qid) for qid, p in proofs.items()
                                            if p['node'] == n and p['outcome'] == o and not uses(qid, pid))
                        if not candidates:
                            break
                        selected.append(candidates[0][1])
                    if len(selected) != len(needed):
                        continue
                    concerns = sorted({cid for cid, c in model['concerns'].items() if concerned(model, relation['claim'], c)}
                                      | {cid for q in selected for cid in proofs[q]['concerns']})
                    existing = proofs.get(pid)
                    if existing is not None and (existing['concerned'], len(existing['concerns'])) <= (bool(concerns), len(concerns)):
                        continue
                    proofs[pid] = {'id': pid, 'node': node, 'outcome': outcome, 'level': 'informal',
                                   'claim': relation['claim'],
                                   'claims': sorted({relation['claim']} | {c for q in selected for c in proofs[q]['claims']}),
                                   'nodes': sorted({node} | {m for q in selected for m in proofs[q]['nodes']}),
                                   'premise_proofs': selected, 'relation': rid,
                                   'derivation': 'forward' if forward else 'backward',
                                   'formal_dependencies': model['dependency_overrides'].get(
                                       pid, [{'node': n, 'outcome': o} for n, o in needed]),
                                   'record': relation['record'], 'concerns': concerns, 'concerned': bool(concerns)}
                    changed = True
        return proofs

    excluded, first = set(), None
    while True:
        proofs = derive(excluded)
        if first is None:
            first = proofs
        outcomes = {}
        for p in proofs.values():
            outcomes.setdefault(p['node'], set()).add(p['outcome'])
        contested = {n for n, seen in outcomes.items() if len(seen) > 1}
        if contested <= excluded:
            break
        excluded |= contested
    # The opposing evidence of a contested node stays visible for review.
    for pid, p in first.items():
        if p['node'] in excluded and pid not in proofs:
            proofs[pid] = p
    for proof in proofs.values():
        proof['concerns'] = sorted(set(proof['concerns']) | {'conflict:' + n for n in proof['nodes'] if n in excluded})
        proof['concerned'] = bool(proof['concerns'])
    model['proofs'] = proofs
    for nid, node in model['nodes'].items():
        representative = canonical(model, nid)
        node['canonical'] = representative
        node['proofs'] = [pid for pid, p in proofs.items() if p['node'] == representative]
        outcomes = {proofs[pid]['outcome'] for pid in node['proofs']}
        node['contested'] = representative in excluded
        node['state'] = 'unresolved'
        if node['contested']:
            node['state'] = 'contested'
        elif outcomes:
            outcome = next(iter(outcomes))
            level = 'formal' if any(proofs[pid]['level'] == 'formal' for pid in node['proofs']) else 'informal'
            node['state'] = level + '_' + outcome
        node['concerns'] = sorted({cid for pid in node['proofs'] for cid in proofs[pid]['concerns']})
        # A withdrawn support must leave its explanation visible on a reopened node.
        evidence = {p['claim'] for p in model['direct'].values() if canonical(model, p['node']) == representative}
        evidence.update(r['claim'] for r in model['relations'].values()
                        if representative in {canonical(model, x['node']) for x in r['premises'] + [r['conclusion']]})
        node['annotations'] = [i for i, finding in enumerate(model['findings']) if evidence.intersection(finding['claims'])]
        node['concern_history'] = [cid for cid, concern in model['concerns'].items()
                                   if any(concerned(model, key, {**concern, 'status': 'pending'}) for key in evidence)]


def sufficient_closure(model):
    """The signed statements from which the root's proof or refutation is reachable.

    Starting from the root settled either way, every accepted relation whose clause
    contains a reachable statement makes the negations of its other statements reachable,
    because establishing those is what derives it. A statement outside this set cannot
    move the root however it is settled, so formal work is not sent for it."""
    root = canonical(model, 'root')
    reachable = {(root, 'proved'), (root, 'refuted')}
    relations = [r for r in model['relations'].values()
                 if model['claims'].get(r['claim'], {}).get('status') == 'supported']
    changed = True
    while changed:
        changed = False
        for relation in relations:
            literals = clause(model, relation)
            for index, literal in enumerate(literals):
                if literal not in reachable:
                    continue
                for other, (n, o) in enumerate(literals):
                    if other != index and (n, flip(o)) not in reachable:
                        reachable.add((n, flip(o)))
                        changed = True
    return reachable


def root_path(model, closure, node):
    """How settling a node stands to the root: both outcomes reach it, only one does, or neither."""
    node = canonical(model, node)
    proved, refuted = (node, 'proved') in closure, (node, 'refuted') in closure
    if proved and refuted:
        return 'either outcome reaches the root'
    if proved:
        return 'on a sufficient path to the root: its proof can carry the root'
    if refuted:
        return 'a necessary condition only: its refutation refutes the root; its proof cannot carry the root'
    return 'not connected to the root by an accepted relation'


def add_terms(model, entries, publication, location):
    for term in entries:
        key = publication + '/' + term['id']
        model['terms'][key] = {**deepcopy(term), 'id': key, 'record': publication, 'location': location}


def add_concerns(model, values, source):
    for item in values:
        cid = source + '/' + item['id']
        model['concerns'][cid] = {**deepcopy(item), 'id': cid, 'source': source,
                                 'targets': [claim_key(x, source) for x in item['targets']],
                                 'status': 'pending'}


def record_event(model, event, folder):
    record, review = read_json(folder / 'record.json'), read_json(folder / 'review/assessment.json')
    rid = event['id']
    model['records'][rid] = {'id': rid, 'sequence': event['sequence'], 'title': record['title'],
                            'description': record['description'], 'exposition': record['exposition'],
                            'review': review['index_assessment'], 'producer_role': event['producer_role']}
    for claim in record['claims']:
        key = rid + '/' + claim['id']
        verdict = next(x for x in review['claims'] if x['claim'] == claim['id'])
        model['claims'][key] = {**deepcopy(claim), 'record': rid, 'status': verdict['status'],
                                'review_reason': verdict['reason'],
                                'dependencies': [claim_key(x, rid) for x in claim.get('dependencies', [])]}
    resolutions = {x['proposal']: x['node'] for x in review['nodes']}
    for proposal in record.get('nodes', []):
        target = resolutions.get(proposal['id'])
        if target:
            model['nodes'].setdefault(target, {'id': target, 'statement': proposal['statement'], 'source': rid})
            if target != proposal['id']:
                model['aliases'][proposal['id']] = canonical(model, target)
    solutions = {x['proposal']: x for x in review['solutions']}
    for solution in record.get('solutions', []):
        verdict = solutions.get(solution['id'])
        if verdict and verdict['level'] in ('informal', 'formal'):
            pid = rid + '/' + solution['id']
            model['direct'][pid] = {**deepcopy(solution), 'id': pid, 'record': rid,
                                    'claim': rid + '/' + solution['claim'], 'level': verdict['level'],
                                    'formal_dependencies': deepcopy(verdict.get('formal_dependencies', solution.get('formal_dependencies', []))),
                                    'formal_check': verdict.get('formal_check')}
    accepted = {x['proposal'] for x in review['relations'] if x['accepted']}
    for relation in record.get('relations', []):
        if relation['id'] in accepted:
            key = rid + '/' + relation['id']
            model['relations'][key] = {**deepcopy(relation), 'record': rid, 'claim': rid + '/' + relation['claim']}
    add_terms(model, record['glossary'], rid, event['folder'] + '/record.json')
    add_terms(model, review.get('glossary', []), rid + '/review', event['folder'] + '/review/assessment.json')
    for term in record['glossary']:
        key = rid + '/' + term['id']
        if review['glossary_approved'] and term.get('global_candidate'):
            model['global_terms'][key] = {'term': key, 'membership': 'candidate', 'aliases': [], 'merged': []}
    add_concerns(model, review.get('concerns', []), rid)
    apply_findings(model, review.get('findings', []), rid)


def assessment_event(model, event, folder):
    assessment = read_json(folder / 'assessment.json')
    add_terms(model, assessment.get('glossary', []), event['id'], event['folder'] + '/assessment.json')
    add_concerns(model, assessment.get('concerns', []), event['id'])
    apply_findings(model, assessment['findings'], event['id'], followup=False)


def apply_findings(model, findings, source, followup=True):
    for number, finding in enumerate(findings):
        affected = {claim_key(ref) for key in ('invalidates', 'validates') for ref in finding.get(key, [])}
        for cid in finding.get('concerns', []):
            affected.update(model['concerns'].get(cid, {}).get('targets', []))
        model['findings'].append({'source': source, 'reason': finding['reason'], 'status': finding['status'], 'claims': sorted(affected)})
        for update in finding.get('dependency_updates', []):
            model['dependency_overrides'][update['proof']] = deepcopy(update['dependencies'])
        for cid in finding.get('concerns', []):
            if cid in model['concerns']:
                item = model['concerns'][cid]
                item['status'] = finding['status']
                item['finding'] = {'review': source, 'reason': finding['reason']}
        for ref in finding.get('invalidates', []):
            key = claim_key(ref)
            model['claims'][key]['status'] = 'unsupported'
            model['claims'][key]['later_review'] = source
        for ref in finding.get('validates', []):
            key = claim_key(ref)
            model['claims'][key]['status'] = 'supported'
            model['claims'][key]['later_review'] = source
        if followup and finding.get('invalidates') and not finding.get('concerns'):
            add_concerns(model, [{'id': 'withdrawal-' + str(number), 'targets': finding['invalidates'],
                                 'reason': finding['reason'], 'evidence': 'The source review explicitly withdrew these claims.'}], source)


def organization_event(model, event, folder):
    data = read_json(folder / 'organization.json')
    add_terms(model, data.get('glossary', []), event['id'], event['folder'] + '/organization.json')
    for merge in data.get('merge_nodes', []):
        source, target = canonical(model, merge['from']), canonical(model, merge['into'])
        if source != target:
            model['aliases'][source] = target
    for key in data.get('promote', []):
        key = next((primary for primary, member in model['global_terms'].items() if key in member['merged']), key)
        existing = model['global_terms'].get(key, {})
        model['global_terms'][key] = {**existing, 'term': key, 'membership': 'permanent',
                                     'aliases': existing.get('aliases', []), 'merged': existing.get('merged', [])}
    for key in data.get('refuse', []):
        current = model['global_terms'].get(key)
        if current and current['membership'] == 'candidate':
            del model['global_terms'][key]
    for merge in data.get('merge_terms', []):
        target = model['global_terms'][merge['keep']]
        for source in merge['others']:
            if source == merge['keep']:
                continue
            other = model['global_terms'].pop(source, None)
            if not other:
                continue
            term = model['terms'][source]
            target['aliases'] = sorted(set(target['aliases'] + other['aliases'] +
                                          [term['name']] + ([term['symbol']] if term.get('symbol') else [])))
            target['merged'] = sorted(set(target['merged'] + other['merged'] + [source]))
            if other['membership'] == 'permanent':
                target['membership'] = 'permanent'
    # A complete layout only replaces organizational metadata, never record prose.
    model['modules'] = deepcopy(data['modules'])
    model['shared_context'] = list(data['shared_context'])
    model['organized'] = sorted(set(model['organized']) | set(data['batch']))


def replay(instance):
    instance = Path(instance)
    model = new_model((instance / 'root.md').read_text(encoding='utf-8'))
    for event in sorted((read_json(p) for p in (instance / 'knowledge/events').glob('*.json')),
                        key=lambda e: e['sequence']):
        folder = instance / 'knowledge' / event['folder']
        {'record': record_event, 'review': assessment_event, 'organization': organization_event}[event['kind']](model, event, folder)
        model['sequence'] = event['sequence']
        settle(model)
    settle(model)
    return model


def formal_ready(model, proof):
    # Concerns inform the formalizer's judgment. They hold new mechanical
    # deductions in settle(), not research on a still-accepted solution.
    if proof['level'] != 'informal':
        return False
    for dep in proof.get('formal_dependencies', []):
        node = model['nodes'][canonical(model, dep['node'])]
        if node['contested'] or not any(model['proofs'][p]['level'] == 'formal'
                                       and model['proofs'][p]['outcome'] == dep['outcome']
                                       for p in node['proofs']):
            return False
    return True


def root_solved(model):
    return model['nodes'][canonical(model, 'root')]['state'] in ('formal_proved', 'formal_refuted')


def escape(text):
    return str(text).replace('<', '&lt;').replace('>', '&gt;')


def render(instance, model, board, leases=None):
    base = Path(instance) / 'knowledge'
    def write_view(path, content):
        # Board changes trigger rendering too. Leave unchanged research files alone.
        try:
            if path.read_bytes() == content.encode('utf-8'):
                return
        except FileNotFoundError:
            pass
        write_text(path, content)

    state_path = Path(instance) / 'runner/state.json'
    state = read_json(state_path) if state_path.exists() else {'jobs': {}}
    investigations = [j for j in state['jobs'].values() if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive']
    def assessment_link(source, prefix=''):
        path = f'records/{source}/review/assessment.json' if source in model['records'] else f'reviews/{source}/assessment.json'
        return f'[{source}]({prefix}{path})'
    def investigation(cid):
        matches = [j for j in investigations if cid in j['task'].get('concerns', [])]
        return ', '.join(j['id'] + ' (' + j['status'] + ')' for j in matches) or 'pending assignment'
    closure = sufficient_closure(model)
    established = {(p['node'], p['outcome']) for p in model['proofs'].values()
                   if not model['nodes'][p['node']]['contested']}
    lines = ['# Frontier', '', f"Revision: {model['sequence']}", '']
    for nid, node in model['nodes'].items():
        if node['canonical'] != nid:
            continue
        lines += [f'## {nid}', '', node['statement'], '', f"State: {node['state']}", '']
        if nid != canonical(model, 'root'):
            lines += [f"Path to root: {root_path(model, closure, nid)}", '']
        for pid in node['proofs']:
            p = model['proofs'][pid]
            how = '' if 'relation' not in p else f" (derived {p['derivation']} through relation {p['relation']})"
            marker = ' — rests on a questioned claim' if any(not c.startswith('conflict:') for c in p['concerns']) else ''
            lines.append(f"- {p['outcome']}, {p['level']}: [{pid}](records/{p['record']}/record.json){how}{marker}")
        for key, relation in model['relations'].items():
            if canonical(model, relation['conclusion']['node']) == nid or any(canonical(model, p['node']) == nid for p in relation['premises']):
                premises = ', '.join(
                    p['outcome'] + ' ' + canonical(model, p['node'])
                    + (' (established)' if (canonical(model, p['node']), p['outcome']) in established else ' (open)')
                    for p in relation['premises'])
                standing = model['claims'][relation['claim']]['status']
                lines.append(f"- Relation [{key}](records/{relation['record']}/record.json), {standing}: [{premises}] implies {relation['conclusion']['outcome']} {canonical(model, relation['conclusion']['node'])}")
        for number in node['annotations']:
            finding = model['findings'][number]
            lines.append(f"- Later review ({finding['status']}): {finding['reason']} — {assessment_link(finding['source'])}")
        for cid in sorted(set(node['concerns']) | set(node['concern_history'])):
            if cid.startswith('conflict:'):
                lines.append('- Opposing accepted outcomes: see the proofs of node ' + cid.partition(':')[2] + '. Comprehensive review is required.')
                continue
            c = model['concerns'][cid]
            lines.append(f"- Concern {cid}: {c['reason']} ({c['status']}); source {assessment_link(c['source'])}; comprehensive review {investigation(cid)}")
        aliases = [n for n in model['aliases'] if canonical(model, n) == nid]
        if aliases:
            lines.append('Aliases: ' + ', '.join(aliases))
        lines.append('')
    write_view(base / 'frontier.md', '\n'.join(lines) + '\n')
    glossary = ['# Global glossary', '', f"Research revision: {model['sequence']}", '',
                'Use primary names in new writing. Historical names and symbols below are scoped to their linked definitions.',
                'Definitions retain their source wording; consult the [frontier](frontier.md) for current node status.', '']
    for key, member in model['global_terms'].items():
        term = model['terms'][key]
        glossary += [f"## {term['name']}", '']
        if term.get('symbol'):
            glossary += [f"Symbol: {term['symbol']}", '']
        glossary += [term['definition'], '', f"Membership: {member['membership']}",
                     f"Source: [local definition]({term['location']}) — {key}", '']
        for alias_key in member['merged']:
            alias = model['terms'][alias_key]
            label = alias['name'] + (f" ({alias['symbol']})" if alias.get('symbol') else '')
            glossary += [f"Historical name/symbol: {label} — [local definition]({alias['location']}) — {alias_key}"]
        if member['merged']:
            glossary.append('')
    write_view(base / 'glossary.md', '\n'.join(glossary) + '\n')
    entries = {}
    def entry(rid, prefix=''):
        if (rid, prefix) in entries:
            return entries[rid, prefix]
        r = model['records'][rid]
        result = [f"### {escape(r['title'])}", '', r['description'], '',
                  f"Review: {r['review']}", '', f"[Record]({prefix}records/{rid}/record.json) · [Exposition]({prefix}records/{rid}/{quote(r['exposition'], safe='/')}) · [Review]({prefix}records/{rid}/review/assessment.json)", '']
        for finding in model['findings']:
            if any(key.startswith(rid + '/') for key in finding['claims']):
                result += [f"Later review ({finding['status']}): {finding['reason']} — {assessment_link(finding['source'], prefix)}", '']
        for cid, concern in model['concerns'].items():
            if concern['status'] != 'cleared' and any(concerned(model, k, concern) for k, c in model['claims'].items() if c['record'] == rid):
                result += [f"Concern {cid}: {concern['reason']} ({concern['status']}); {assessment_link(concern['source'], prefix)}; comprehensive review {investigation(cid)}", '']
        if any(n['contested'] and any(model['proofs'][p]['record'] == rid for p in n['proofs']) for n in model['nodes'].values()):
            result += [f'Opposing accepted outcomes: consult the [frontier]({prefix}frontier.md) and comprehensive review.', '']
        entries[rid, prefix] = result
        return result
    index = ['# Research index', '', f"Research revision: {model['sequence']}", '',
             '[Frontier](frontier.md) · [Full glossary](glossary.md) · [Board](board.md)', '',
             'Module summaries reflect the latest organization; newer reviewed records appear under [Unfiled records](#unfiled-records).', '',
             '## Shared context', '']
    for rid in model['shared_context']:
        index += entry(rid)
    index += ['## Modules', '']
    directory = base / 'index'
    directory.mkdir(exist_ok=True)
    wanted = set()
    filed = set(model['shared_context'])
    for module in model['modules']:
        name = module['id'] + '.md'
        wanted.add(name)
        filed.update(module['records'])
        index += [f"- [{module['title']}](index/{name}): {module['description']}"]
        body = [f"# {module['title']}", '', f"Research revision: {model['sequence']}", '', module['description'], '']
        for rid in module['records']:
            body += entry(rid, '../')
        write_view(directory / name, '\n'.join(body) + '\n')
    for path in directory.glob('*.md'):
        if path.name not in wanted:
            path.unlink()
    index += ['', '## Unfiled records', '']
    for rid in model['records']:
        if rid not in filed:
            index += entry(rid)
    write_view(base / 'index.md', '\n'.join(index) + '\n')
    board_lines = ['# Research work and occupied sections', '', f"Research revision: {model['sequence']}", '',
                   'Saved pipeline state, not process liveness. Sections remain occupied through peer and review.', '']
    for row in board:
        producer = row.get('session') or '(not launched)'
        # An attempt still producing may not have registered a section yet; it is choosing.
        holds = ', '.join(row['nodes']) or ('(choosing)' if row['role'] == 'attempt' and row['stage'] in ('producing', 'queued') else '(none)')
        board_lines += [f"- {row['pipeline']} · producer: {producer} · {row['role']} · {row['stage']} · nodes: {holds}"]
        for section in row.get('sections', []):
            scope = 'the whole node' if section['whole'] else escape(section['statement'])
            board_lines.append(f"  Section {section['id']} on {section['node']} (session {section['session']}): {scope}")
        for nid in row['nodes']:
            node = model['nodes'].get(canonical(model, nid), {})
            if node.get('concerns') or node.get('concern_history'):
                board_lines.append(f'  Concern: see [frontier](frontier.md) for {nid}.')
    if leases:
        board_lines += ['', '## Node leases', '', 'One session at a time chooses a section on a node; others wait in order.', '']
        for nid, entry in sorted(leases.items()):
            holders = ', '.join(h['session'] for h in entry['holders']) or '(free)'
            queue = ', '.join(w['session'] for w in entry['queue']) or '(none)'
            board_lines.append(f'- {nid} · lease: {holders} · waiting: {queue}')
    write_view(base / 'board.md', '\n'.join(board_lines) + '\n')
    try:
        previous = read_json(base / 'state.json')
    except FileNotFoundError:
        previous = None
    if previous != model:
        write_json(base / 'state.json', model)
