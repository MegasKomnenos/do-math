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
            'modules': [], 'shared_context': [], 'organized': [], 'cleared_uses': {}, 'dependency_overrides': {},
            'findings': [], 'sequence': 0}


def concerned(model, key, concern=None, seen=None):
    concerns = [concern] if concern else list(model['concerns'].values())
    for item in concerns:
        if item['status'] == 'cleared' or key in item.get('cleared_claims', []):
            continue
        if key in item['targets']:
            return True
        visited = set(seen or ())
        if key in visited:
            continue
        visited.add(key)
        if any(concerned(model, dep, item, visited)
               for dep in model['claims'].get(key, {}).get('dependencies', [])):
            return True
    return False


def settle(model):
    """Maintain reviewed direct supports and forward consequences of explicit relations.

    A concern preserves previously established consequences while blocking new ones.
    An explicitly withdrawn claim removes the supports that actually cite it.
    """
    old = model['proofs']
    proofs = {}
    for pid, proof in model['direct'].items():
        if model['claims'].get(proof['claim'], {}).get('status') != 'supported':
            continue
        node = canonical(model, proof['node'])
        concerns = [cid for cid, c in model['concerns'].items() if concerned(model, proof['claim'], c)]
        proofs[pid] = {**proof, 'node': node, 'claims': [proof['claim']], 'nodes': [node],
                       'formal_dependencies': model['dependency_overrides'].get(pid, proof.get('formal_dependencies', [])),
                       'concerns': concerns, 'concerned': bool(concerns)}
    prior_valid = [p for p in old.values() if all(model['claims'].get(c, {}).get('status') == 'supported' for c in p['claims'])]
    directions = {}
    for proof in list(proofs.values()) + prior_valid:
        directions.setdefault(canonical(model, proof['node']), set()).add(proof['outcome'])
    conflicts = {n for n, outcomes in directions.items() if len(outcomes) > 1}
    for proof in proofs.values():
        if proof['node'] in conflicts:
            proof['concerns'].append('conflict:' + proof['node'])
            proof['concerned'] = True
    def uses_route(pid, target):
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
        for rid, relation in model['relations'].items():
            if (rid in proofs and not proofs[rid]['concerned']) or model['claims'].get(relation['claim'], {}).get('status') != 'supported':
                continue
            conclusion = canonical(model, relation['conclusion']['node'])
            selected = []
            previous = old.get(rid, {})
            for index, premise in enumerate(relation['premises']):
                candidates = [(pid, p) for pid, p in proofs.items()
                              if p['node'] == canonical(model, premise['node'])
                              and p['outcome'] == premise['outcome'] and not uses_route(pid, rid)]
                previous_ids = previous.get('premise_proofs', [])
                preferred = previous_ids[index] if index < len(previous_ids) else None
                candidates.sort(key=lambda row: (row[1]['concerned'], row[0] != preferred, row[0]))
                if not candidates:
                    break
                selected.append(candidates[0])
            if len(selected) != len(relation['premises']):
                continue
            selections = [selected]
            for uses in model['cleared_uses'].values():
                for cleared in uses:
                    if cleared['relation'] != rid:
                        continue
                    ids = cleared['premise_proofs']
                    if len(ids) != len(relation['premises']) or any(pid not in proofs or uses_route(pid, rid) for pid in ids):
                        continue
                    alternative = [(pid, proofs[pid]) for pid in ids]
                    if all(p['node'] == canonical(model, premise['node'])
                           and p['outcome'] == premise['outcome']
                           for (_, p), premise in zip(alternative, relation['premises'])):
                        selections.append(alternative)
            eligible = []
            for selection in selections:
                claims = sorted({relation['claim']} | {c for _, p in selection for c in p['claims']})
                use = {'relation': rid, 'premise_proofs': [pid for pid, _ in selection]}
                concerns = sorted(({cid for cid, c in model['concerns'].items()
                                    if concerned(model, relation['claim'], c)} |
                                   {cid for _, p in selection for cid in p['concerns']}) -
                                  {cid for cid, uses in model['cleared_uses'].items() if use in uses})
                if not concerns or previous.get('claims') == claims:
                    eligible.append((bool(concerns), selection, claims, concerns))
            if not eligible:
                continue
            flagged, selected, claims, concerns = min(eligible, key=lambda row: (row[0], len(row[3])))
            if rid in proofs and flagged:
                continue
            premise_ids = [pid for pid, _ in selected]
            proofs[rid] = {'id': rid, 'node': conclusion, 'outcome': relation['conclusion']['outcome'],
                           'level': 'informal', 'claim': relation['claim'], 'claims': claims,
                           'nodes': sorted({conclusion} | {n for _, p in selected for n in p['nodes']}),
                           'premise_proofs': premise_ids, 'concerns': concerns,
                           'formal_dependencies': model['dependency_overrides'].get(rid, relation['premises']), 'record': relation['record'],
                           'concerned': flagged}
            changed = True
    model['proofs'] = proofs
    directions = {}
    for proof in proofs.values():
        directions.setdefault(proof['node'], set()).add(proof['outcome'])
    conflicts = {n for n, outcomes in directions.items() if len(outcomes) > 1}
    for proof in proofs.values():
        proof['concerns'] = sorted(set(proof['concerns']) | {'conflict:' + n for n in proof['nodes'] if n in conflicts})
        proof['concerned'] = bool(proof['concerns'])
    for nid, node in model['nodes'].items():
        representative = canonical(model, nid)
        node['canonical'] = representative
        node['proofs'] = [pid for pid, p in proofs.items() if p['node'] == representative]
        outcomes = {proofs[pid]['outcome'] for pid in node['proofs']}
        node['contested'] = len(outcomes) > 1
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
                                   if any(concerned(model, key, {**concern, 'status': 'pending', 'cleared_claims': []}) for key in evidence)]
        node['possible_concerns'] = []
    # A held implication has no proof object yet. Keep its possible dependencies
    # visible without treating a concern as a mathematical verdict or a new proof.
    histories = {n['canonical']: set(n['concern_history']) | (set(n['concerns']) & set(model['concerns']))
                 for n in model['nodes'].values()}
    possible = {nid: set() for nid in histories}
    changed = True
    while changed:
        changed = False
        for rid, relation in model['relations'].items():
            if rid in proofs:
                continue  # Its actual proof already records concerns and exact-use clearance.
            conclusion = canonical(model, relation['conclusion']['node'])
            inherited = set()
            for premise in relation['premises']:
                source = canonical(model, premise['node'])
                inherited.update(histories[source] | possible[source])
            if not inherited <= possible[conclusion]:
                possible[conclusion].update(inherited)
                changed = True
    for node in model['nodes'].values():
        node['possible_concerns'] = sorted(possible[node['canonical']] - histories[node['canonical']])


def add_terms(model, entries, publication, location):
    for term in entries:
        key = publication + '/' + term['id']
        model['terms'][key] = {**deepcopy(term), 'id': key, 'record': publication, 'location': location}


def add_concerns(model, values, source):
    for item in values:
        cid = source + '/' + item['id']
        model['concerns'][cid] = {**deepcopy(item), 'id': cid, 'source': source,
                                 'targets': [claim_key(x, source) for x in item['targets']],
                                 'status': 'pending', 'cleared_claims': []}


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
        affected = {claim_key(ref) for key in ('invalidates', 'validates', 'clears') for ref in finding.get(key, [])}
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
                item['cleared_claims'] = sorted(set(item.get('cleared_claims', [])) |
                                                 {claim_key(x) for x in finding.get('clears', [])})
                uses = model['cleared_uses'].setdefault(cid, [])
                for use in finding.get('cleared_uses', []):
                    if use not in uses:
                        uses.append(deepcopy(use))
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


def render(instance, model, board):
    base = Path(instance) / 'knowledge'
    state_path = Path(instance) / 'runner/state.json'
    state = read_json(state_path) if state_path.exists() else {'jobs': {}}
    investigations = [j for j in state['jobs'].values() if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive']
    def assessment_link(source, prefix=''):
        path = f'records/{source}/review/assessment.json' if source in model['records'] else f'reviews/{source}/assessment.json'
        return f'[{source}]({prefix}{path})'
    def investigation(cid):
        matches = [j for j in investigations if cid in j['task'].get('concerns', [])]
        return ', '.join(j['id'] + ' (' + j['status'] + ')' for j in matches) or 'pending assignment'
    lines = ['# Frontier', '', f"Revision: {model['sequence']}", '']
    for nid, node in model['nodes'].items():
        if node['canonical'] != nid:
            continue
        lines += [f'## {nid}', '', node['statement'], '', f"State: {node['state']}", '']
        for pid in node['proofs']:
            p = model['proofs'][pid]
            lines.append(f"- {p['outcome']}, {p['level']}: [{pid}](records/{p['record']}/record.json)" + (' — concern pending' if p['concerned'] else ''))
        for key, relation in model['relations'].items():
            if canonical(model, relation['conclusion']['node']) == nid or any(canonical(model, p['node']) == nid for p in relation['premises']):
                premises = ', '.join(p['outcome'] + ' ' + canonical(model, p['node']) for p in relation['premises'])
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
        for cid in node.get('possible_concerns', []):
            c = model['concerns'][cid]
            lines.append(f"- Possible dependency through a recorded relation: concern {cid}: {c['reason']} ({c['status']}); source {assessment_link(c['source'])}; comprehensive review {investigation(cid)}. This annotation does not determine the effect on this node.")
        lines.append('')
    write_text(base / 'frontier.md', '\n'.join(lines) + '\n')
    glossary = ['# Global glossary', '', 'Use primary names in new writing. Aliases interpret existing records.', '']
    for key, member in model['global_terms'].items():
        term = model['terms'][key]
        glossary += [f"## {term['name']}", '', f"Symbol: {term.get('symbol', '')}", '', term['definition'], '',
                     'Aliases: ' + ', '.join(member['aliases']), f"Membership: {member['membership']}",
                     f"Source: [local definition]({term['location']}) — {key}", '']
    write_text(base / 'glossary.md', '\n'.join(glossary) + '\n')
    def entry(rid, prefix=''):
        r = model['records'][rid]
        result = [f"### {escape(r['title'])}", '', r['description'], '',
                  f"Review: {r['review']}", '', f"[Record]({prefix}records/{rid}/record.json) · [Exposition]({prefix}records/{rid}/{quote(r['exposition'], safe='/')}) · [Review]({prefix}records/{rid}/review/assessment.json)", '']
        for finding in model['findings']:
            if any(key.startswith(rid + '/') for key in finding['claims']):
                result += [f"Later review ({finding['status']}): {finding['reason']} — {assessment_link(finding['source'], prefix)}", '']
        conclusions = {canonical(model, r['conclusion']['node']) for r in model['relations'].values() if r['record'] == rid}
        for cid, concern in model['concerns'].items():
            direct = any(concerned(model, k, concern) for k, c in model['claims'].items() if c['record'] == rid)
            possible = any(cid in model['nodes'][nid].get('possible_concerns', []) for nid in conclusions)
            if concern['status'] != 'cleared' and (direct or possible):
                label = 'Concern' if direct else 'Possible dependency through a recorded relation; effect undetermined. Concern'
                result += [f"{label} {cid}: {concern['reason']} ({concern['status']}); {assessment_link(concern['source'], prefix)}; comprehensive review {investigation(cid)}", '']
        if any(n['contested'] and any(model['proofs'][p]['record'] == rid for p in n['proofs']) for n in model['nodes'].values()):
            result += [f'Opposing accepted outcomes: consult the [frontier]({prefix}frontier.md) and comprehensive review.', '']
        return result
    index = ['# Research index', '', '[Frontier](frontier.md) · [Full glossary](glossary.md) · [Board](board.md)', '', '## Shared context', '']
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
        body = [f"# {module['title']}", '', module['description'], '']
        for rid in module['records']:
            body += entry(rid, '../')
        write_text(directory / name, '\n'.join(body) + '\n')
    for path in directory.glob('*.md'):
        if path.name not in wanted:
            path.unlink()
    index += ['', '## Unfiled records', '']
    for rid in model['records']:
        if rid not in filed:
            index += entry(rid)
    write_text(base / 'index.md', '\n'.join(index) + '\n')
    board_lines = ['# Live board', '', f"Research revision: {model['sequence']}", '']
    for row in board:
        producer = row.get('session') or '(not launched)'
        board_lines += [f"- {row['pipeline']} · producer: {producer} · {row['role']} · {row['stage']} · nodes: {', '.join(row['nodes']) or '(choosing)'}"]
        for nid in row['nodes']:
            node = model['nodes'].get(canonical(model, nid), {})
            if node.get('concerns') or node.get('concern_history') or node.get('possible_concerns'):
                board_lines.append(f'  Concern: see [frontier](frontier.md) for {nid}.')
    write_text(base / 'board.md', '\n'.join(board_lines) + '\n')
    write_json(base / 'state.json', model)
