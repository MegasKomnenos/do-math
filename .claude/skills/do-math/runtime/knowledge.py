"""Derive the research state from the canon and the published events. Prose is never interpreted.

The canon's structural index says which declarations exist and what each uses; the summary of the
records says what their authors declared about them; the events carry review's judgments in the
order they were published. From these the standing of every element, the frontier and the state of
the root are computed afresh on each replay, so no session writes them.
"""
from copy import deepcopy
from pathlib import Path

from canon import Canon, beyond_allowed, name_path, read_approaches
from runtime_support import read_json, write_json, write_text

ROOT_QUESTION = 'q0'
ROOT_QUESTION_STATEMENT = 'The root problem itself, taken as a whole.'
ROOT_QUESTION_GROUNDS = ('An explorer holding this question investigates the root proposition, its objects and the '
                         'mathematics accumulated around them without a narrower focus.')
STANDINGS = {'no_proof': 'no proof', 'not_confirmed': 'proof not confirmed',
             'held': 'correct, held back', 'accepted': 'accepted'}
REMAINING = ('no_proof', 'not_confirmed', 'held')


def canonical_question(model, question):
    """Questions are merged by the organizer; aliases lead to the surviving identity."""
    seen = set()
    while question in model['question_aliases']:
        if question in seen:
            raise ValueError('question alias cycle')
        seen.add(question)
        question = model['question_aliases'][question]
    return question


def new_model(instance):
    canon = Canon(instance)
    meta = read_json(Path(instance) / 'instance.json')
    index = canon.load_index()
    summary = read_json(canon.root / 'records.json') if (canon.root / 'records.json').exists() else {}
    elements = {}
    for name, entry in index['entries'].items():
        record = summary.get(name, {})
        elements[name] = {
            'name': name, 'kind': entry['kind'], 'module': entry['module'], 'statement': entry['statement'],
            'statement_hash': entry['statement_hash'], 'lean_proof': entry['lean_proof'],
            # What Lean reported for the declaration: every axiom its proof depends on (canon.update_index).
            'axioms': entry['axioms'],
            'uses': entry['uses'], 'statement_uses': entry['statement_uses'], 'library': entry['library'],
            'weight': record.get('weight', 'step'), 'short': record.get('short') or '',
            'description': record.get('description') or '', 'written_proof': bool(record.get('proof')),
            'proves': record.get('proves'), 'refutes': record.get('refutes'), 'source': record.get('source'),
            'approaches': record.get('approaches', []), 'verdict': None, 'concerns': [], 'findings': []}
    return {'root': meta['root'], 'library': meta['library'], 'revision': index['revision'],
            'allowed_axioms': read_json(Path(instance) / 'settings.json')['lean']['allowed_axioms'],
            'elements': elements, 'pairs': index.get('pairs', {}),
            'verdicts': {}, 'changes': {}, 'organized': [],
            'questions': {ROOT_QUESTION: {'id': ROOT_QUESTION, 'statement': ROOT_QUESTION_STATEMENT,
                                          'grounds': ROOT_QUESTION_GROUNDS, 'source': None, 'origin': 'root',
                                          'resolutions': []}},
            'question_aliases': {}, 'question_proposals': [],
            'concerns': {}, 'findings': [], 'sequence': 0}


# ----------------------------------------------------------------------------- events

def add_concerns(model, values, source):
    for item in values:
        cid = source + '/' + item['id']
        model['concerns'][cid] = {**deepcopy(item), 'id': cid, 'source': source, 'status': 'pending'}


def apply_findings(model, findings, source, followup=True):
    """A finding is the only thing that changes a judgment already published.

    It can withdraw the confirmation of an element's proof or restore it, and it can reopen a
    question whose resolution it found insufficient. A status alone changes nothing."""
    for number, finding in enumerate(findings):
        affected = set(finding.get('invalidates', [])) | set(finding.get('validates', []))
        for cid in finding['concerns']:
            affected.update(model['concerns'][cid]['targets'])
        model['findings'].append({'source': source, 'reason': finding['reason'], 'status': finding['status'],
                                  'elements': sorted(affected), 'questions': list(finding.get('reopens', []))})
        for cid in finding['concerns']:
            item = model['concerns'][cid]
            item['status'] = finding['status']
            item['finding'] = {'review': source, 'reason': finding['reason']}
        def unjudged(name):
            # An element the instance began with has no verdict. A complete Lean proof among these stood
            # as accepted, and a finding that restores its confirmation restores that.
            began = model['elements'].get(name, {}).get('lean_proof') == 'complete'
            return {'element': name, 'accepted': began, 'change': None}

        for name in finding.get('invalidates', []):
            verdict = model['verdicts'].setdefault(name, unjudged(name))
            if verdict.get('correct') == 'confirmed':
                # Kept for a restoration: the reason a confirmed proof stood with says why it is held back
                # and where work on it begins.
                verdict['confirmed_reason'] = verdict.get('reason')
            verdict.update(correct='not_confirmed', later_review=source, reason=finding['reason'])
        for name in finding.get('validates', []):
            verdict = model['verdicts'].setdefault(name, unjudged(name))
            if verdict.get('correct') != 'confirmed':
                # A restored confirmation brings back the reason the proof was confirmed with. A proof that
                # was not confirmed before takes the reason of the finding that confirms it.
                verdict['reason'] = verdict.pop('confirmed_reason', None) or finding['reason']
            verdict.update(correct='confirmed', later_review=source)
        for qid in finding.get('reopens', []):
            question = model['questions'].get(canonical_question(model, qid))
            if question:
                question['resolutions'] = []
        if followup and finding.get('invalidates') and not finding['concerns']:
            add_concerns(model, [{'id': 'withdrawal-' + str(number), 'targets': finding['invalidates'],
                                  'reason': finding['reason'],
                                  'evidence': 'The source review explicitly withdrew these confirmations.'}], source)


def change_event(model, event, folder):
    """A reviewed change: its elements enter with the verdicts review wrote for them."""
    applied = read_json(folder / 'applied.json')
    assessment = read_json(folder / 'assessment.json')
    change = read_json(folder / 'change.json')
    cid = event['id']
    judged = {v['element']: v for v in assessment['elements']}
    for name in applied['added'] + applied['replaced']:
        verdict = judged.get(name)
        if verdict is not None:
            model['verdicts'][name] = {**deepcopy(verdict), 'change': cid, 'sequence': event['sequence']}
        else:
            # A proof that a reviewed change brought and that its review did not judge carries no earlier
            # proof's verdict, and it is not confirmed either. Only the elements an instance began with
            # stand without a verdict (standing_of); if this one did, a complete Lean proof would count
            # as accepted although no review compared its statement with what was meant.
            model['verdicts'][name] = {'element': name, 'correct': 'undetermined', 'accepted': False, 'change': cid,
                                       'sequence': event['sequence'],
                                       'reason': 'The review of the change that brought this proof did not judge it.'}
    model['changes'][cid] = {'id': cid, 'sequence': event['sequence'], 'title': change['title'],
                             'description': change['description'], 'contribution': assessment['contribution'],
                             'role': event['producer_role'], 'added': applied['added'], 'replaced': applied['replaced'],
                             'records': applied['records'], 'question': event.get('question')}
    verdicts = {x['proposal']: x for x in assessment.get('questions', [])}
    for proposal in change.get('questions', []):
        verdict = verdicts.get(proposal['id'])
        if verdict is None:
            continue
        if verdict['verdict'] == 'admitted':
            model['questions'].setdefault(proposal['id'], {
                'id': proposal['id'], 'statement': proposal['statement'], 'grounds': proposal['grounds'],
                'source': cid, 'origin': 'change', 'resolutions': []})
        else:
            # A declined proposal stays visible with review's reason, so a later peer can tell a question
            # worth proposing again in sharper form from one the research does not want.
            model['question_proposals'].append({
                'change': cid, 'id': proposal['id'], 'statement': proposal['statement'],
                'grounds': proposal['grounds'], 'verdict': verdict['verdict'],
                'reason': verdict['reason'], 'duplicate_of': verdict.get('duplicate_of')})
    accepted = {x['proposal'] for x in assessment.get('resolutions', []) if x['resolved']}
    for resolution in change.get('resolutions', []):
        if resolution['id'] in accepted:
            question = model['questions'].get(canonical_question(model, resolution['question']))
            if question:
                question['resolutions'].append(cid + '/' + resolution['id'])
    add_concerns(model, assessment.get('concerns', []), cid)
    apply_findings(model, assessment.get('findings', []), cid)


def organization_event(model, event, folder):
    """An organizer's change. What it adds was proved in Lean from the allowed axioms and enters accepted."""
    data = read_json(folder / 'organization.json')
    applied = read_json(folder / 'applied.json')
    oid = event['id']
    for merge in data.get('merge_questions', []):
        source, target = canonical_question(model, merge['from']), canonical_question(model, merge['into'])
        if source != target:
            model['question_aliases'][source] = target
            model['questions'][target]['resolutions'] += model['questions'][source]['resolutions']
    for name in applied['added']:
        model['verdicts'][name] = {'element': name, 'correct': 'confirmed', 'accepted': True, 'change': oid,
                                   'sequence': event['sequence'],
                                   'reason': 'Proved in Lean from the allowed axioms; added by the organizer.'}
    for item in applied.get('retired', []):
        # The proof that stood under the alternative's name now stands under the statement's own.
        verdict = model['verdicts'].pop(item['alternative'], None)
        if verdict is not None:
            model['verdicts'][item['into']] = {**verdict, 'element': item['into']}
        else:
            model['verdicts'].pop(item['into'], None)
    model['organized'] = sorted(set(model['organized']) | set(data['batch']))


def assessment_event(model, event, folder):
    assessment = read_json(folder / 'assessment.json')
    add_concerns(model, assessment.get('concerns', []), event['id'])
    apply_findings(model, assessment['findings'], event['id'], followup=False)


def questions_event(model, event, folder):
    """Questions placed on the frontier by the operator, outside the peer and review path."""
    data = read_json(folder / 'questions.json')
    for item in data['questions']:
        model['questions'].setdefault(item['id'], {
            'id': item['id'], 'statement': item['statement'], 'grounds': item['grounds'],
            'source': event['id'], 'origin': data['source'], 'resolutions': []})


def replay(instance):
    instance = Path(instance)
    model = new_model(instance)
    for event in sorted((read_json(p) for p in (instance / 'knowledge/events').glob('*.json')),
                        key=lambda e: e['sequence']):
        folder = instance / 'knowledge' / event['folder']
        {'change': change_event, 'review': assessment_event, 'organization': organization_event,
         'questions': questions_event}[event['kind']](model, event, folder)
        model['sequence'] = event['sequence']
    settle(model)
    return model


# ----------------------------------------------------------------------------- standing

def is_statement(element):
    return element['kind'] == 'theorem'


def has_proof(element):
    """A statement has a proof when its Lean proof is complete or its record carries a written one."""
    return element['lean_proof'] == 'complete' or element['written_proof']


def standing_of(element):
    if not is_statement(element):
        return None
    if not has_proof(element):
        return 'no_proof'
    verdict = element['verdict']
    if verdict is None:
        # No review has judged this proof: the instance began with it. Lean has checked a proof that
        # is complete, and that check stands where review's judgment would; a written proof waits for one.
        return 'accepted' if element['lean_proof'] == 'complete' else 'not_confirmed'
    if verdict.get('correct') != 'confirmed':
        return 'not_confirmed'
    return 'accepted' if verdict.get('accepted') else 'held'


def statement_of(model, name):
    """The statement a declaration proves: itself, or the one its record names and Lean confirmed."""
    seen = set()
    while name in model['elements'] and name not in seen:
        seen.add(name)
        target = model['elements'][name]['proves']
        if not target or target not in model['elements'] or not model['pairs'].get(f'same|{name}|{target}'):
            break
        name = target
    return name


def settle(model):
    """Attach verdicts, compute every element's standing and which statements are settled.

    An element is settled when its proof is accepted and every statement of the canon that proof
    names is settled. A statement with several proofs is settled as soon as one of them is.
    A statement and its negation that both carry settled proofs are contested, and nothing rests on
    either until a review locates the failure. Definitions and library declarations have no standing
    and do not enter the computation."""
    elements = model['elements']
    allowed = set(model['allowed_axioms'])
    proofs = {}
    for name, element in elements.items():
        element['verdict'] = model['verdicts'].get(name)
        element['standing'] = standing_of(element)
        # Formal: a statement whose proof, by Lean's own account of its axioms, depends on allowed axioms only.
        # A `sorry` anywhere below it is the axiom `sorryAx`, which cannot be allowed (settings.validate).
        element['formal'] = is_statement(element) and not beyond_allowed(element, allowed)
        element['statement_of'] = statement_of(model, name) if is_statement(element) else None
        element['used_by'], element['mentioned_by'] = [], []
        element['settled'] = False
        if is_statement(element):
            proofs.setdefault(element['statement_of'], []).append(name)
    for name, element in elements.items():
        for used in element['uses']:
            if used in elements:
                elements[used]['used_by'].append(name)
        for used in element['statement_uses']:
            if used in elements:
                elements[used]['mentioned_by'].append(name)
    for name, element in elements.items():
        element['proofs'] = sorted(proofs.get(name, []), key=lambda p: (p != name, p)) if is_statement(element) else []
        target = element['refutes']
        element['refutes'] = target if target in elements and model['pairs'].get(f'negation|{name}|{target}') else None

    def named(element):
        return [elements[u]['statement_of'] for u in element['uses'] if u in elements and is_statement(elements[u])]

    def settled_without(excluded):
        settled = set()
        changed = True
        while changed:
            changed = False
            for name, element in elements.items():
                if name in settled or element['standing'] != 'accepted':
                    continue
                if all(s not in excluded and any(p in settled for p in elements[s]['proofs']) for s in named(element)):
                    settled.add(name)
                    changed = True
        return settled

    # Correct proofs cannot reach opposite outcomes for one statement. While a statement and its
    # negation both carry settled proofs, no proof may rest on either of the two, so both are taken
    # out of what a proof can name and the computation is repeated: without them another pair can
    # come to stand in the same condition, and a pair once excluded stays excluded.
    excluded, contested = set(), set()
    while True:
        settled = settled_without(excluded)
        refuted = {}
        for name, element in elements.items():
            # The declaration whose record says `refutes:` carries the negation as its statement. The
            # negation is settled when one of its proofs is, under this declaration or under another
            # declaration of the same statement.
            if element['refutes'] and any(p in settled for p in elements[element['statement_of']]['proofs']):
                refuted.setdefault(elements[element['refutes']]['statement_of'], []).append(name)
        found = {s for s in refuted if any(p in settled for p in elements[s]['proofs'])}
        sides = found | {elements[r]['statement_of'] for s in found for r in refuted[s]}
        contested |= found
        if sides <= excluded:
            break
        excluded |= sides
    for name, element in elements.items():
        element['settled'] = name in settled
        element['contested'] = name in excluded
        element['statement_settled'] = name not in excluded and any(p in settled for p in element['proofs'])
        element['statement_formal'] = name not in excluded and any(
            p in settled and elements[p]['formal'] for p in element['proofs'])
        # A statement whose negation is settled is refuted: no work on it remains, and a proof that
        # names it cannot become settled, so the statement that proof belongs to needs another one.
        element['refuted_by'] = sorted(refuted.get(name, [])) if name not in excluded else []
    for name, element in elements.items():
        element['names_refuted'] = sorted({s for s in named(element) if elements[s]['refuted_by']})
    model['contested'] = sorted(contested)
    for cid, concern in model['concerns'].items():
        for name in concern['targets']:
            if name in elements:
                elements[name]['concerns'].append(cid)
    for number, finding in enumerate(model['findings']):
        for name in finding['elements']:
            if name in elements:
                elements[name]['findings'].append(number)
    root = elements.get(model['root'])
    if root is None:
        raise ValueError('the root declaration is missing from the canon: ' + model['root'])
    refuters = refuted.get(model['root'], [])
    if root['contested']:
        state = 'contested'
    elif root['statement_formal']:
        state = 'formal_proved'
    elif any(elements[elements[r]['statement_of']]['statement_formal'] for r in refuters):
        state = 'formal_refuted'
    elif root['statement_settled']:
        state = 'informal_proved'
    elif refuters:
        state = 'informal_refuted'
    else:
        state = 'unresolved'
    model['root_state'] = state
    model['frontier'] = frontier(model)
    model['remaining'] = sorted({row['name'] for row in model['frontier']
                                 if row['kind'] != 'repeat' and not row['refuted_by'] and not row['settled']
                                 and (row['standing'] in REMAINING or row['names_refuted'])})
    settle_questions(model)


def refuting_proofs(model, statement, formal=False):
    """The settled proofs through which a statement is refuted, by name.

    They are the settled proofs of the negation that a declaration with `refutes:` carries, whichever
    declaration of that negation holds each proof. With formal, only the formal ones."""
    elements = model['elements']
    found = set()
    for refuter in elements[statement]['refuted_by'] or [
            n for n, e in elements.items() if e['refutes'] and elements[e['refutes']]['statement_of'] == statement]:
        for proof in elements[elements[refuter]['statement_of']]['proofs']:
            if elements[proof]['settled'] and (elements[proof]['formal'] or not formal):
                found.add(proof)
    return sorted(found)


def root_settlement(model):
    """The root's formal settlement as the root question's answer, or None while the root lacks one."""
    if model['root_state'] not in ('formal_proved', 'formal_refuted'):
        return None
    elements = model['elements']
    if model['root_state'] == 'formal_proved':
        proofs = [p for p in elements[model['root']]['proofs'] if elements[p]['settled'] and elements[p]['formal']]
    else:
        proofs = refuting_proofs(model, elements[model['root']]['statement_of'], formal=True)
    return {'state': model['root_state'], 'proofs': sorted(proofs)}


def settle_questions(model):
    """A question is resolved while review's acceptance of a resolving account stands.

    The root question is never resolved by an explanation. It asks the root problem itself, so it is
    resolved while the root is formally proved or refuted, and that is derived on every replay."""
    settlement = root_settlement(model)
    elements = model['elements']
    reached = set(rests_on(model, model['root']))
    for name, element in elements.items():
        if element['refutes'] and elements[element['refutes']]['statement_of'] == elements[model['root']]['statement_of']:
            reached |= rests_on(model, name)
    # The proofs the root's settlement could rest on whose confirmation a review has withdrawn.
    withdrawn = {proof for statement in reached for proof in elements[statement]['proofs']
                 if (elements[proof]['verdict'] or {}).get('later_review')
                 and elements[proof]['verdict'].get('correct') != 'confirmed'}
    for qid, question in model['questions'].items():
        representative = canonical_question(model, qid)
        question['canonical'] = representative
        root = representative == ROOT_QUESTION
        question['root_settlement'] = deepcopy(settlement) if root else None
        question['state'] = 'resolved' if (settlement if root else question['resolutions']) else 'open'
        # A later review stays beside the question it reopened, under whatever name it used for it, and
        # beside the root question when it withdrew a confirmation the root's settlement rested on.
        question['annotations'] = [
            i for i, finding in enumerate(model['findings'])
            if any(canonical_question(model, q) == representative for q in finding['questions']
                   if q in model['questions'] or q in model['question_aliases'])
            or (root and finding['status'] != 'cleared' and withdrawn & set(finding['elements']))]


def root_solved(model):
    return root_settlement(model) is not None


def rests_on(model, name):
    """Every statement of the canon reached from a statement through what its proofs name."""
    elements = model['elements']
    reached, pending = set(), [elements[name]['statement_of']]
    while pending:
        statement = pending.pop()
        if statement in reached:
            continue
        reached.add(statement)
        for proof in elements[statement]['proofs']:
            for used in elements[proof]['uses']:
                if used in elements and is_statement(elements[used]):
                    pending.append(elements[used]['statement_of'])
    return reached


def formalizable(model):
    """For each settled statement the root, or a refutation of it, rests on that has no formal proof yet, one proof to formalize.

    The proof is one through which the statement is settled, the statement's own declaration before
    any other, and it is ready once the statements it names have formal proofs. A proof whose own Lean
    text is complete is among these when it is still not formal: it names a declaration whose Lean
    proof is open although the statement has a formal proof under another declaration, or it uses an
    axiom the instance does not allow. The runner reads what the formal proof will need from what the
    proof names in Lean."""
    elements = model['elements']
    ready = []
    # The root is settled formally by a proof or by a refutation, so what a settled refutation of
    # the root rests on is formalized as well.
    reached = set(rests_on(model, model['root']))
    for refuter in elements[elements[model['root']]['statement_of']]['refuted_by']:
        reached |= rests_on(model, refuter)
    for statement in sorted(reached):
        if elements[statement]['statement_formal'] or elements[statement]['contested']:
            continue
        for proof in elements[statement]['proofs']:
            element = elements[proof]
            if (element['settled'] and not element['formal']
                    and all(elements[elements[u]['statement_of']]['statement_formal']
                            for u in element['uses'] if u in elements and is_statement(elements[u]))):
                ready.append(proof)
                break
    return ready


def frontier(model):
    """The view from the root downward: each statement that is not settled, with all of its proofs.

    A row is a statement, a proof of it, or a repeat of a statement already shown. A step whose own
    proof is accepted is passed through, so that the view stays at the level of the units of the
    proof; a step that is itself work that remains is shown. `depth` is the indentation."""
    elements = model['elements']
    rows, shown = [], set()

    def line(name, depth, kind):
        element = elements[name]
        verdict = element['verdict'] or {}
        return {'name': name, 'depth': depth, 'kind': kind, 'weight': element['weight'],
                'standing': element['standing'], 'short': element['short'] or element['description'],
                'reason': verdict.get('reason') if element['standing'] in ('not_confirmed', 'held') else None,
                'approaches': len(element['approaches']), 'settled': element['statement_settled'],
                'formal': element['statement_formal'],
                'contested': element['contested'], 'refuted_by': element['refuted_by'],
                'names_refuted': element['names_refuted'] if has_proof(element) else []}

    def open_statement(statement, depth):
        if statement in shown:
            rows.append(line(statement, depth, 'repeat'))
            return
        shown.add(statement)
        proofs = elements[statement]['proofs']
        rows.append(line(statement, depth, 'statement'))
        if elements[statement]['refuted_by'] or elements[statement]['statement_settled']:
            # Nothing beneath a settled statement remains to be done, and what lies beneath a refuted
            # one is no longer work toward the root. Only the root reaches this line when settled.
            return
        for proof in proofs:
            if proof != statement:
                rows.append(line(proof, depth + 1, 'proof'))
            if has_proof(elements[proof]):
                descend(proof, depth + (1 if proof == statement else 2), set())

    def descend(proof, depth, passed):
        for used in elements[proof]['uses']:
            if used not in elements or not is_statement(elements[used]):
                continue
            statement = elements[used]['statement_of']
            target = elements[statement]
            if target['statement_settled']:
                continue
            passable = (target['weight'] == 'step' and target['standing'] == 'accepted'
                        and len(target['proofs']) == 1 and statement not in passed)
            if passable:
                descend(statement, depth, passed | {statement})
            else:
                open_statement(statement, depth)

    open_statement(elements[model['root']]['statement_of'], 0)
    return rows


# ----------------------------------------------------------------------------- views

def describe(row):
    text = STANDINGS.get(row['standing'], '')
    if row['kind'] == 'repeat':
        return 'shown above'
    if row['refuted_by']:
        return 'refuted by ' + ', '.join('`' + name + '`' for name in row['refuted_by'])
    if row['settled']:
        return 'settled by a formal proof' if row['formal'] else 'settled; no formal proof yet'
    if row['reason']:
        text += ': ' + ' '.join(row['reason'].split())[:160]
    if row['contested']:
        text += ' · contested: it and its negation both carry settled proofs'
    if row['names_refuted']:
        text += (' · its proof names ' + ', '.join('`' + name + '`' for name in row['names_refuted'])
                 + ', refuted since; the statement needs another proof')
    if row['approaches']:
        text += f" · {row['approaches']} approach{'es' if row['approaches'] != 1 else ''} tried"
    return text


def frontier_lines(model, holders=None):
    """The frontier as text. holders maps an element to the number of sessions holding sections on it."""
    lines = []
    for row in model['frontier']:
        label = {'statement': '', 'proof': 'other proof: ', 'repeat': ''}[row['kind']]
        held = (holders or {}).get(row['name'])
        tail = f" · held by {held} session{'s' if held != 1 else ''}" if held else ''
        step = ' (step)' if row['weight'] == 'step' and row['kind'] != 'repeat' else ''
        lines.append(f"{'  ' * row['depth']}- {label}`{row['name']}`{step} — {row['short']} — {describe(row)}{tail}")
    return lines


def frontier_notes(model, investigation=None):
    """What stands beside the lines of the frontier: contested statements and the concerns not yet cleared."""
    lines = []
    if model['contested']:
        lines += ['', 'Contested: a statement and its negation both carry settled proofs, and nothing rests on either '
                  'until a comprehensive review locates the failure: '
                  + ', '.join('`' + s + '`' for s in model['contested']) + '.']
    pending = [c for c in model['concerns'].values() if c['status'] != 'cleared']
    if pending:
        lines += ['', '## Concerns', '']
        for concern in pending:
            tail = f"; comprehensive review {investigation(concern['id'])}" if investigation else ''
            lines.append(f"- {concern['id']} on {', '.join('`' + t + '`' for t in concern['targets'])}: "
                         f"{concern['reason']} ({concern['status']}){tail}")
    return lines


def question_lines(model):
    """The questions that follow the frontier: each with its grounds, its state and where it came from."""
    lines = ['', '# Questions', '']
    for qid, question in model['questions'].items():
        if question['canonical'] != qid:
            continue
        lines += [f'## {qid}', '', question['statement'], '']
        if question['grounds']:
            lines += [f"Grounds: {question['grounds']}", '']
        lines.append(f"State: {question['state']}")
        if question['origin'] == 'change':
            lines.append(f"Source: change {question['source']}")
        elif question['origin'] == 'root':
            lines.append('Source: the root statement')
        else:
            lines.append(f"Source: {question['origin']} publication {question['source']}")
        for key in question['resolutions']:
            lines.append(f'- Resolved by {key}')
        if question['root_settlement']:
            lines.append("- Resolved by the root's formal settlement, not by an explanation: "
                         + ', '.join('`' + p + '`' for p in question['root_settlement']['proofs']))
        for number in question['annotations']:
            finding = model['findings'][number]
            lines.append(f"- Later review ({finding['status']}): {finding['reason']} — {finding['source']}")
        aliases = [q for q in model['question_aliases'] if canonical_question(model, q) == qid]
        if aliases:
            lines.append('Aliases: ' + ', '.join(aliases))
        lines.append('')
    if model['question_proposals']:
        lines += ['## Question proposals review did not admit', '',
                  'A proposal marked revise lacked specificity or clarity; the review reason beside it says what would make it a question. '
                  'A declined proposal duplicated an existing question or did not meet the bar of importance.', '']
        for item in model['question_proposals']:
            duplicate = f" (duplicate of {item['duplicate_of']})" if item['duplicate_of'] else ''
            lines.append(f"- {item['verdict']}{duplicate}: {item['statement']} — review: {item['reason']} — change {item['change']}")
        lines.append('')
    return lines


def escape(text):
    return str(text).replace('<', '&lt;').replace('>', '&gt;')


def render(instance, model, board, leases=None):
    instance = Path(instance)
    base = instance / 'knowledge'

    def write_view(path, content):
        # Board changes trigger rendering too. Leave unchanged research files alone.
        try:
            if path.read_bytes() == content.encode('utf-8'):
                return
        except FileNotFoundError:
            pass
        write_text(path, content)

    state = read_json(instance / 'runner/state.json')
    investigations = [j for j in state['jobs'].values() if j['role'] == 'review' and j['task']['kind'] == 'comprehensive']

    def investigation(cid):
        matches = [j for j in investigations if cid in j['task']['concerns']]
        return ', '.join(j['id'] + ' (' + j['status'] + ')' for j in matches) or 'pending assignment'

    holders = {}
    for row in board:
        for element in row['elements']:
            holders[element] = holders.get(element, 0) + 1
    elements = model['elements']
    lines = ['# Frontier', '', f"Revision: {model['sequence']} · Root: `{model['root']}` · State: {model['root_state']}", '',
             'Derived from the root downward along what each proof names. A statement that is settled is not opened. '
             'The work that remains is every line whose proof is not accepted.', '']
    lines += frontier_lines(model, holders)
    lines += frontier_notes(model, investigation)
    lines += question_lines(model)
    write_view(base / 'frontier.md', '\n'.join(lines) + '\n')
    index = ['# Index of the canon', '', f"Revision: {model['sequence']}", '',
             'What each record says about its element, in the order of the Lean structure, with the current standing. '
             'This view is derived; nothing here is written by hand.', '']
    by_module = {}
    for name, element in elements.items():
        by_module.setdefault(element['module'], []).append(element)
    for module in sorted(by_module):
        index += [f'## {module}', '']
        for element in sorted(by_module[module], key=lambda e: e['name']):
            standing = STANDINGS.get(element['standing'], element['kind'])
            index.append(f"- `{element['name']}` · {element['weight']} · {standing} — {escape(element['description'])}")
        index.append('')
    write_view(base / 'index.md', '\n'.join(index) + '\n')
    board_lines = ['# Research work and occupied sections', '', f"Research revision: {model['sequence']}", '',
                   'Saved pipeline state, not process liveness. Sections and questions remain occupied through peer and review.', '']
    for row in board:
        producer = row['session'] or '(not launched)'
        if row['role'] == 'explore':
            held = row['question'] or ('(choosing)' if row['stage'] in ('producing', 'queued') else '(none)')
            board_lines += [f"- {row['pipeline']} · producer: {producer} · {row['role']} · {row['stage']} · question: {held}"]
        else:
            holds = ', '.join(row['elements']) or ('(choosing)' if row['role'] == 'attempt' and row['stage'] in ('producing', 'queued') else '(none)')
            board_lines += [f"- {row['pipeline']} · producer: {producer} · {row['role']} · {row['stage']} · elements: {holds}"]
        for section in row['sections']:
            scope = 'the whole element' if section['whole'] else section['statement']
            if section.get('new'):
                scope = 'a new statement aimed at this element: ' + section['new']['lean']
            board_lines.append(f"  Section {section['id']} on {section['element']} (session {section['session']}): {scope}")
    if leases:
        board_lines += ['', '## Element leases', '']
        for name, entry in sorted(leases.items()):
            lease_holders = ', '.join(h['session'] for h in entry['holders']) or '(free)'
            queue = ', '.join(w['session'] for w in entry['queue']) or '(none)'
            board_lines.append(f'- {name} · lease: {lease_holders} · waiting: {queue}')
    write_view(base / 'board.md', '\n'.join(board_lines) + '\n')
    try:
        previous = read_json(base / 'state.json')
    except FileNotFoundError:
        previous = None
    if previous != model:
        write_json(base / 'state.json', model)


def record_summary(instance, index):
    """What the records declare about their elements, gathered by machine at each publication.

    Replay reads this one file instead of every record. It holds nothing a record does not."""
    from canon import read_record
    canon = Canon(instance)
    summary = {}
    for name in index['entries']:
        record = read_record(canon, name)
        if record is None:
            continue
        meta, sections = record['meta'], record['sections']
        summary[name] = {'weight': meta['weight'], 'short': meta.get('short'), 'proves': meta.get('proves'),
                         'refutes': meta.get('refutes'), 'source': meta.get('source'),
                         'description': ' '.join(sections['Description'].split()),
                         'proof': bool(sections.get('Proof')), 'statement': bool(sections.get('Statement')),
                         'approaches': sorted(read_approaches(canon, name)),
                         'path': 'records/' + name_path(name) + '.md'}
    return summary
