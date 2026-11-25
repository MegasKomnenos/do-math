"""What a session runs to read the canon and to prepare a change to it. See ../reference/canon.md.

Reading is deterministic traversal: a command names a starting point and a rule, and returns
everything the rule selects, in an order fixed by the Lean structure, with the count. No command
here starts Lean to read. `prepare` and `verify` build through the instance's Lean broker.
"""
import argparse
import json
from pathlib import Path
import sys

from canon import (BESIDE_CANDIDATE, EXTRACTION, PREPARED, Canon, CanonError, Conflict, apply_lean, apply_rearrangement,
                   build_outcome, candidate_records, check_applied, copy_tree, declaration_text, drop_modules,
                   load_change, name_path, read_approaches, read_question_account, read_record, required_pairs,
                   start_build, tree_hash, update_index, wait_build, with_importers)
from knowledge import (REMAINING, STANDINGS, canonical_question, frontier_lines, frontier_notes, has_proof,
                       is_statement, question_lines, replay)
from runtime_support import read_json, write_json


def context(session):
    given, session = session, Path(session).resolve()
    if (session / 'instance.json').is_file():
        # The operator reads the canon with the same commands and gives the instance folder itself.
        return session, {'instance': str(session), 'role': 'operator', 'session': 'operator'}, session
    if not (session / 'input.json').is_file():
        # Another argument stands where the session directory belongs: it was left out, or it does not come first.
        raise CanonError(f'{given} is not a session directory: it holds no input.json. The session directory comes '
                         'directly after the name of the command, and the arguments of the command follow it')
    inp = read_json(session / 'input.json')
    return session, inp, Path(inp['instance'])


def standing(element):
    return STANDINGS.get(element['standing'], element['kind'])


def head(element):
    """One line for a view that passes over many elements: what the record says, with the current standing."""
    proves = f" · another proof of {element['statement_of']}" if element['statement_of'] not in (None, element['name']) else ''
    state = f" · {standing(element)}" if is_statement(element) else ''  # a definition has no proof and no standing
    return f"{element['name']} · {element['kind']} · {element['weight']}{state}{proves} — {element['description']}"


def mentions(canon, question, name):
    """Whether a question, or the understanding written for it, names an element between backticks."""
    mark = '`' + name + '`'
    if mark in question['statement'] or mark in (question['grounds'] or ''):
        return True
    path = canon.questions / (question['id'] + '.md')
    return path.is_file() and mark in path.read_text(encoding='utf-8')


def holders(instance, model):
    from coordination import board
    held = {}
    for row in board(instance, model=model):
        for name in row['elements']:
            held[name] = held.get(name, 0) + 1
    return held


def with_standing(model, names):
    return ', '.join(f"{n} ({standing(model['elements'][n])})" if n in model['elements'] else n for n in names) or '(none)'


def view(instance, model, name, part=None, full=False):
    """One element as one view: the structure Lean gave, joined by name with what its record says."""
    canon = Canon(instance)
    element = model['elements'].get(name)
    if element is None:
        raise CanonError('no such element: ' + name)
    record = read_record(canon, name)
    sections = record['sections'] if record else {}
    index = canon.load_index()['entries'][name]
    if part == 'source':
        text = (canon.lean / index['file']).read_text(encoding='utf-8').replace('\r\n', '\n')
        return declaration_text(text, index['span'])
    if part == 'history':
        folder = canon.history / name_path(name)
        # The folder also holds the folders of the elements whose names extend this name; those are not read.
        files = sorted([*folder.glob('*.md'), *folder.glob('[0-9]*-approaches/*.md')]) if folder.is_dir() else []
        return '\n\n'.join(p.read_text(encoding='utf-8') for p in files) or 'No history.'
    if part == 'approaches':
        entries = read_approaches(canon, name)
        if not entries:
            return 'No approaches recorded.'
        return '\n\n'.join(f'### Approach {key}\n\n' + (canon.approaches / name_path(name) / (key + '.md')).read_text(encoding='utf-8')
                           for key in entries)
    if part:
        title = part.capitalize()
        return sections.get(title) or f'The record has no "{title}" part.'
    statements = [u for u in element['uses'] if u in model['elements'] and is_statement(model['elements'][u])]
    objects = sorted({u for u in element['uses'] + element['statement_uses']
                      if u in model['elements'] and not is_statement(model['elements'][u])})
    span = index['span']
    lines = [head(element), '',
             f"Lean          {element['statement']}",
             f"source        canon/lean/{index['file']}, lines {span[0]}-{span[2]}"]
    if element['short']:
        lines.append(f"short name    {element['short']}")
    if is_statement(element):
        proof = ('complete in Lean' if element['lean_proof'] == 'complete' else
                 'written in the record; its Lean proof ends in sorry' if element['written_proof'] else 'none')
        lines.append(f'proof         {proof}')
        premises = []
        for used in statements:
            premise = model['elements'][used]
            settlement = 'settled' if premise['settled'] else 'unsettled'
            formality = 'formal' if premise['formal'] else 'not formal'
            premises.append(f"{used} ({standing(premise)}, {settlement}, {formality})")
        lines.append('rests on      ' + (', '.join(premises) or '(none)'))
        lines.append(f"settled       {'yes' if element['settled'] else 'no'}"
                     + (' · proved in Lean from the allowed axioms' if element['formal'] else ''))
        if len(element['proofs']) > 1:
            lines.append(f"proofs        {with_standing(model, element['proofs'])}")
    else:
        # The body of a definition is what the definition says, so its view carries the Lean text.
        text = (canon.lean / index['file']).read_text(encoding='utf-8').replace('\r\n', '\n')
        lines += ['', '```lean', declaration_text(text, span), '```', '']
    lines.append(f"objects       {', '.join(objects) or '(none)'}")
    lines.append(f"used by       {with_standing(model, element['used_by'])}")
    if element['mentioned_by']:
        lines.append(f"stated with   {len(element['mentioned_by'])} statements mention it (list --about {name})")
    if element['library']:
        shown = element['library'][:12]
        more = f" and {len(element['library']) - len(shown)} more" if len(element['library']) > len(shown) else ''
        lines.append(f"library       {', '.join(shown)}{more}")
    if element['axioms']:
        lines.append(f"axioms        {', '.join(element['axioms'])}")
    verdict = element['verdict']
    if verdict:
        # Acceptance is a judgment of a confirmed proof. While a later review has withdrawn the
        # confirmation, the earlier acceptance is not in force, and the review that withdrew it is named.
        accepted = ('' if verdict.get('correct') != 'confirmed' else
                    ', accepted' if verdict.get('accepted') else ', not accepted')
        lines.append(f"verdict       for statement {element['statement_hash']}: {verdict.get('correct')}{accepted} "
                     f"({verdict.get('later_review') or verdict.get('change')})")
        lines.append(f"              {verdict.get('reason', '')}")
    if element['contested']:
        lines.append('contested     it and its negation both carry settled proofs; nothing rests on either until a '
                     'comprehensive review locates the failure')
    if element['refuted_by']:
        lines.append(f"refuted by    {with_standing(model, element['refuted_by'])}")
    if is_statement(element) and has_proof(element) and element['names_refuted']:
        lines.append(f"names refuted {', '.join(element['names_refuted'])} (its proof cannot become settled as it stands)")
    asking = sorted(qid for qid, question in model['questions'].items()
                    if question['canonical'] == qid and mentions(canon, question, name))
    if asking:
        lines.append(f"questions     {', '.join(asking)} (their text names this element)")
    for cid in element['concerns']:
        concern = model['concerns'][cid]
        lines.append(f"concern       {cid} ({concern['status']}): {concern['reason']}")
    for number in element['findings']:
        finding = model['findings'][number]
        lines.append(f"later review  {finding['source']} ({finding['status']}): {finding['reason']}")
    from coordination import board
    for row in board(instance, model=model):
        for section in row['sections']:
            if section['element'] in (name, element['statement_of']):
                scope = ('the whole element' if section['whole'] else
                         'a new statement aimed at it: ' + section['new']['lean'] if section.get('new') else
                         ' '.join(str(section['statement']).split())[:160])
                lines.append(f"held by       {section['session']} ({row['role']}, {row['stage']}): {scope}")
    approaches = read_approaches(canon, name)
    for key, entry in approaches.items():
        lines.append(f"approach      {key}: {entry['meta']['title']} — stops: "
                     + ' '.join(entry['sections']['Where it stops'].split())[:200])
    available = [title for title in ('Statement', 'Explanation', 'Proof', 'Literature') if sections.get(title)]
    if full:
        for title in available:
            lines += ['', '## ' + title, '', sections[title]]
        if approaches:
            lines += ['', view(instance, model, name, 'approaches')]
    else:
        # The parts are named as --part takes them, so that a name read off this line can be given to the option.
        parts = ', '.join([title.lower() for title in available] + (['approaches'] if approaches else [])) or 'none'
        lines += ['', f'record parts  {parts} (read one with --part, all with --full; --part source prints the Lean text)']
    return '\n'.join(lines)


def listing(model, names, units=False):
    names = [n for n in names if n in model['elements'] and (not units or model['elements'][n]['weight'] == 'unit')]
    return '\n'.join([head(model['elements'][n]) for n in names] + [f'{len(names)} elements.'])


def select(model, args):
    elements = model['elements']
    if args.module:
        prefix = args.module
        return sorted(n for n, e in elements.items() if e['module'] == prefix or e['module'].startswith(prefix + '.'))
    if args.uses:
        closure, pending = [], list(elements[args.uses]['uses'])
        while pending:
            name = pending.pop(0)
            if name in elements and name not in closure:
                closure.append(name)
                if args.deep:
                    pending += elements[name]['uses']
        return closure
    if args.used_by:
        closure, pending = [], list(elements[args.used_by]['used_by'])
        while pending:
            name = pending.pop(0)
            if name not in closure:
                closure.append(name)
                if args.deep:
                    pending += elements[name]['used_by']
        return closure
    if args.about:
        return sorted(set(elements[args.about]['mentioned_by']) | set(elements[args.about]['used_by']))
    if args.remaining:
        return [n for n in model['remaining']]
    return sorted(elements)


def question_view(instance, model, qid, history=False):
    canon = Canon(instance)
    if qid not in model['questions'] and qid not in model['question_aliases']:
        raise CanonError('no such question: ' + qid)
    qid = canonical_question(model, qid)
    question = model['questions'][qid]
    lines = [f"{qid} · {question['state']}", '', question['statement'], '']
    if question['grounds']:
        lines += ['Grounds: ' + question['grounds'], '']
    body, review = read_question_account(canon, qid)
    if body or review:
        lines += ['## Understanding so far', '', body.strip(), '']
        if review:
            lines += ['## Review of the work that wrote it', '', review, '']
    else:
        lines += ['No understanding has been written for this question yet.', '']
    folder = canon.history / 'questions' / qid
    earlier = sorted(folder.glob('*.md')) if folder.is_dir() else []
    if history:
        lines += ['## Earlier texts', '', '\n\n'.join(p.read_text(encoding='utf-8') for p in earlier) or 'None.', '']
    elif earlier:
        lines += [f'{len(earlier)} earlier text{"s" if len(earlier) != 1 else ""} of this understanding '
                  'can be read with --history.', '']
    return '\n'.join(lines)


def log(model, last):
    changes = sorted(model['changes'].values(), key=lambda c: c['sequence'])[-last:]
    lines = []
    for change in changes:
        lines += [f"{change['id']} · revision {change['sequence']} · {change['role']} · {change['title']}",
                  f"  {change['description']}", f"  Review: {change['contribution']}",
                  f"  Added: {', '.join(change['added']) or '(none)'}; proofs replaced: {', '.join(change['replaced']) or '(none)'}", '']
    return '\n'.join(lines) or 'No change has been published yet.'


# ----------------------------------------------------------------------------- preparing a change

def entry_info(index, name, written):
    entry = index['entries'][name]
    return {'kind': entry['kind'], 'statement': entry['statement'], 'statement_hash': entry['statement_hash'],
            'lean_proof': entry['lean_proof'], 'written_proof': written, 'uses': entry['uses'],
            'statement_uses': entry['statement_uses'], 'axioms': entry['axioms']}


def build_candidate(instance, session_id, candidate, folder, expect_mb, timeout, role, fresh=False):
    """Apply a candidate to a copy of the current canon, build it and say what it adds and replaces.

    Returns None while the build runs, so that the caller can come back for it; the build is kept
    with the candidate's file identity, and is started again only when the candidate changed, the canon
    was published to, the build was made with another extraction than this code's (canon.EXTRACTION), or
    the build ended without compiling."""
    canon = Canon(instance)
    meta = read_json(Path(instance) / 'instance.json')
    settings = read_json(Path(instance) / 'settings.json')
    candidate, folder = Path(candidate), Path(folder)
    tree = tree_hash(candidate, skip=BESIDE_CANDIDATE)
    index = canon.load_index()
    result = {'ok': False, 'tree': tree, 'revision': index['revision'], 'build': None, 'errors': [],
              'changed_modules': [], 'added': [], 'replaced': [], 'records': [], 'retired': [], 'entries': {},
              'bases': {}}
    try:
        change = load_change(candidate)
    except (CanonError, OSError, ValueError) as exc:
        result['errors'] = [str(exc)]
        return result
    organizer = role == 'organizer'
    organization = read_json(candidate / 'organization.json') if organizer else {}
    records = candidate_records(candidate, change)
    state_path = folder / 'state.json'
    state = read_json(state_path) if state_path.exists() else {}
    lean_root = folder / 'lean'
    touches_lean = bool(change['modules'] or change['replace'] or (candidate / 'rewrite').is_dir()
                        or organization.get('delete'))
    new_index = index
    if touches_lean:
        kept = (state.get('tree') == tree and state.get('revision') == index['revision']
                and state.get('fresh') == fresh and state.get('extraction') == EXTRACTION)
        if kept:
            # A build that ended without compiling is not kept. A compile can end for a reason that is not in
            # the candidate's files: the system ended Lean, the broker refused or lost the compile, the build
            # was cancelled. The same command, run again, then has to build again.
            ended = build_outcome(instance, state['build'])
            kept = ended is None or ended['ok']
        if not kept:
            folder.mkdir(parents=True, exist_ok=True)
            copy_tree(canon.lean, lean_root)
            try:
                changed = apply_lean(lean_root, candidate, change, index, library=meta['library'])
                removed = []
                if organizer:
                    written, removed = apply_rearrangement(lean_root, candidate, organization.get('delete', []))
                    changed = sorted(set(changed) | set(written))
            except (CanonError, OSError) as exc:
                result['errors'] = [str(exc)]
                return result
            # A module that imports a changed one is compiled in a new environment, so its index is taken again too.
            extracted = with_importers(lean_root, meta['library'], changed)
            build = start_build(instance, lean_root, meta['library'], session_id, expect_mb, extracted,
                                required_pairs(records), fresh=fresh, targets=changed if fresh else None)
            state = {'tree': tree, 'revision': index['revision'], 'fresh': fresh, 'build': build,
                     'changed': changed, 'extracted': extracted, 'removed': removed, 'extraction': EXTRACTION}
            write_json(state_path, state)
        outcome = wait_build(instance, state['build'], timeout)
        if outcome is None:
            return None
        result.update(build=outcome['build'], changed_modules=state['changed'])
        if not outcome['ok']:
            result['errors'] = [f"{e['module'] or 'build'}: {e['status']}"
                                + (f" (exit code {e['exit_code']})" if e.get('exit_code') is not None else '')
                                + (f": {e['reason']}" if e.get('reason') else '')
                                + ('\n' + e['output'] if e.get('output') else '') for e in outcome['errors']]
            return result
        new_index = update_index(drop_modules(index, state['removed']), outcome['rows'], outcome['pairs'],
                                 lean_root, index['revision'], state['extracted'])
    checked = check_applied(index, new_index, change, records, lambda name: read_record(canon, name),
                            settings['lean']['allowed_axioms'], organizer=organizer)
    paths = {name_path(name): name for name in new_index['entries']}
    by_name = {paths[path]: record for path, record in records.items() if path in paths}

    def written(name):
        record = by_name.get(name) or read_record(canon, name)
        return bool(record and record['sections'].get('Proof'))

    result.update(ok=not checked['errors'], errors=checked['errors'], added=checked['added'],
                  replaced=checked['replaced'], records=checked['records'], retired=checked['retired'],
                  entries={name: entry_info(new_index, name, written(name))
                           for name in checked['added'] + checked['replaced'] if name in new_index['entries']},
                  bases={name: index['entries'][name]['source_sha'] for name in checked['replaced']
                         if name in index['entries']})
    return result


def report(result):
    if result is None:
        print(json.dumps({'waiting': True, 'hint': 'the build continues; run the same command again'}))
        return 124
    summary = {key: result[key] for key in ('ok', 'build', 'added', 'replaced', 'records', 'errors')}
    summary['axioms'] = {name: info['axioms'] for name, info in result['entries'].items() if info['kind'] == 'theorem'}
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if result['ok'] else 1


def prepare(session, expect_mb, timeout):
    """A peer's or organizer's own check of its candidate before it ends: output/prepared.json."""
    session, inp, instance = context(session)
    if inp['role'] not in ('peer', 'organizer'):
        raise CanonError('prepare is for the session that writes a change: a peer or an organizer; '
                         'a producing session builds its working Lean files through commands.lean')
    result = build_candidate(instance, inp['session'], session / 'output', session / 'work/prepare',
                             expect_mb, timeout, inp['role'])
    if result is not None:
        write_json(session / 'output' / PREPARED, result)
    return report(result)


def verify(session, expect_mb, timeout):
    """Review's own compile of the frozen candidate on the current canon: work/verify/outcome.json."""
    session, inp, instance = context(session)
    if inp['role'] != 'review' or inp['task'].get('kind') != 'candidate':
        raise CanonError('verify is for the review of a candidate')
    result = build_candidate(instance, inp['session'], inp['task']['candidate'], session / 'work/verify',
                             expect_mb, timeout, 'peer', fresh=True)
    if result is not None:
        # A candidate without a Lean part makes no build, so nothing has created the folder yet.
        (session / 'work/verify').mkdir(parents=True, exist_ok=True)
        write_json(session / 'work/verify/outcome.json', result)
    return report(result)


def checkout(session, target):
    """A copy of the canon's module root for a session to build its own Lean files against."""
    session, inp, instance = context(session)
    target = Path(target)
    target = target if target.is_absolute() else session / target
    if not target.resolve().is_relative_to(session):
        raise CanonError('check the canon out inside your session folder')
    if target.exists() and any(target.iterdir()):
        raise CanonError(f'{target} is not empty; choose a new folder, so that your own files are not overwritten')
    copy_tree(Canon(instance).lean, target)
    return {'checked_out': str(target), 'revision': Canon(instance).load_index()['revision']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('frontier', 'view', 'list', 'question', 'log', 'checkout', 'prepare', 'verify'):
        p = sub.add_parser(name)
        p.add_argument('session', type=Path)
        if name == 'view':
            p.add_argument('element')
            p.add_argument('--part', choices=('statement', 'explanation', 'proof', 'literature', 'approaches',
                                              'history', 'source'))
            p.add_argument('--full', action='store_true')
        if name == 'list':
            group = p.add_mutually_exclusive_group()
            group.add_argument('--module', help='every element of a module, or of the modules under a prefix')
            group.add_argument('--uses', metavar='ELEMENT', help='what the proof of an element names')
            group.add_argument('--used-by', metavar='ELEMENT', help='the elements whose proofs name an element')
            group.add_argument('--about', metavar='ELEMENT', help='every element that mentions a definition or uses a statement')
            group.add_argument('--remaining', action='store_true', help='the work that remains for the root')
            p.add_argument('--deep', action='store_true', help='follow --uses or --used-by all the way')
            p.add_argument('--units', action='store_true', help='only the units of the proof')
        if name == 'question':
            p.add_argument('question')
            p.add_argument('--history', action='store_true', help='also print the texts this understanding replaced')
        if name == 'log':
            p.add_argument('--last', type=int, default=20)
        if name == 'checkout':
            p.add_argument('target', type=Path)
        if name in ('prepare', 'verify'):
            p.add_argument('--expect-mb', type=int, default=None,
                           help='your probable peak private memory of one module compile in MiB (reference/lean.md)')
            p.add_argument('--timeout', type=float, default=50.0)
    args = parser.parse_args(argv)
    try:
        if args.command in ('prepare', 'verify', 'checkout') and (args.session / 'instance.json').is_file():
            raise CanonError(args.command + ' works in a session folder; the instance folder serves the reading commands only')
        if args.command in ('prepare', 'verify'):
            _, inp, instance = context(args.session)
            expect = args.expect_mb or read_json(instance / 'settings.json')['lean']['calibration_expect_mb']
            return (prepare if args.command == 'prepare' else verify)(args.session, expect, args.timeout)
        if args.command == 'checkout':
            print(json.dumps(checkout(args.session, args.target)))
            return 0
        _, inp, instance = context(args.session)
        model = replay(instance)
        if args.command == 'frontier':
            text = '\n'.join([f"Root: {model['root']} · state: {model['root_state']} · revision {model['sequence']}", '']
                             + frontier_lines(model, holders(instance, model)) + frontier_notes(model)
                             + ['', f"Elements of this view that are work that remains: {len(model['remaining'])}. "
                                    'Each has one of the standings ' + ', '.join(f'"{STANDINGS[s]}"' for s in REMAINING)
                                    + ', or a proof that names a statement refuted since.']
                             + question_lines(model))
        elif args.command == 'view':
            text = view(instance, model, args.element, args.part, args.full)
        elif args.command == 'list':
            for name in (args.uses, args.used_by, args.about):
                if name and name not in model['elements']:
                    raise CanonError('no such element: ' + name)
            text = listing(model, select(model, args), args.units)
        elif args.command == 'question':
            text = question_view(instance, model, args.question, args.history)
        else:
            text = log(model, args.last)
        sys.stdout.buffer.write((text + '\n').encode('utf-8'))
        return 0
    except (CanonError, Conflict, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
