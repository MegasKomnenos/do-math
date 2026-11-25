"""Check transport structure and evidence identities; sessions judge mathematics."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from availability import no_research_outcome, reported_availability
from canon import BESIDE_CANDIDATE, PREPARED, CanonError, beyond_allowed, load_change, name_path, tree_hash
from coordination import section_entries
from knowledge import ROOT_QUESTION, canonical_question, replay
from runtime_support import read_json
from settings import PRODUCERS

VERDICTS = ('confirmed', 'not_confirmed', 'undetermined', 'not_applicable')


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def text(value, name):
    need(isinstance(value, str) and bool(value.strip()), name + ': nonempty text required')
    return value


# The ID rule of questions, concerns and proposals. The questions command applies it to operator questions as well.
IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*')


def identifier(value):
    need(isinstance(value, str) and IDENTIFIER.fullmatch(value),
         f'invalid identifier: {value!r}; an identifier consists of letters, digits, "_" and "-" and begins with '
         'a letter or a digit')
    return value


def taken_question_ids(model):
    """IDs a new question cannot take, whether a peer proposes it or the operator publishes it."""
    return set(model['questions']) | set(model['question_aliases'])


def array(value, name):
    need(isinstance(value, list), name + ': array required')
    return value


def file(root, name):
    from canon import relative_file
    try:
        return relative_file(root, name)
    except CanonError as exc:
        raise Invalid(str(exc)) from None


def regular_tree(root):
    for p in [Path(root), *Path(root).rglob('*')]:
        need(not p.is_symlink() and not p.is_junction(), 'filesystem links cannot be published: ' + str(p))


def tree_hashes(root):
    """The file identities under which the runner freezes a candidate and review checks it."""
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


def unique(rows):
    ids = [identifier(row.get('id')) for row in rows]
    need(len(ids) == len(set(ids)), 'duplicate id')
    return set(ids)


def prepared_candidate(root):
    """The receipt that `prepare` left for exactly these candidate files, or the reason there is none.

    prepare applies the candidate to a copy of the canon, builds it and extracts what it adds and
    replaces. The receipt names the files it saw, so a candidate edited afterwards has to be
    prepared again before review can rely on the lists of elements in it."""
    path = Path(root) / PREPARED
    need(path.is_file(), 'the candidate has not been prepared; run commands.prepare and correct what it reports')
    receipt = read_json(path)
    need(receipt.get('tree') == tree_hash(root, skip=BESIDE_CANDIDATE),
         'the candidate changed after it was prepared; run commands.prepare again')
    need(receipt.get('ok') is True, 'prepare reported errors: ' + '; '.join(receipt.get('errors', []))[:2000])
    return receipt


def carried_by(model, declaration):
    """What a settled statement has through the proof of this declaration alone: 'settled', 'formal', both or neither.

    A statement is settled through its settled proofs and formal through those of them that are
    formal. When one declaration holds the only such proof, replacing that proof decides whether the
    statement stays settled, or stays formal."""
    elements = model['elements']
    element = elements.get(declaration)
    if element is None or not element.get('statement_of'):
        return set()
    statement = elements[element['statement_of']]
    if not statement['statement_settled']:
        return set()
    settled = [p for p in statement['proofs'] if elements[p]['settled']]
    formal = [p for p in settled if elements[p]['formal']]
    return ({'settled'} if settled == [declaration] else set()) | ({'formal'} if formal == [declaration] else set())


def stays_settled(model, receipt, declaration):
    """A settled statement's proof is replaced only by a proof under which the statement stays settled.

    A statement that supersedes a settled one is better only once it is settled itself, so the
    derivation of the old statement from it replaces the old proof after that and not before. What a
    machine can decide of the new proof is checked here: it is complete in Lean, every statement it
    names is settled, and where the old proof made the statement formal, the new one is formal too.
    Review's acceptance of it is the remaining condition, which the check of the assessment makes."""
    carried = carried_by(model, declaration)
    if not carried:
        return
    elements, entry = model['elements'], receipt['entries'][declaration]
    statement = elements[declaration]['statement_of']
    need(entry['lean_proof'] == 'complete',
         f'{statement} is settled through the proof of {declaration}; that proof is replaced only by a proof that is '
         'complete in Lean and names settled statements, so that the statement stays settled. A further proof of '
         'another kind enters as a declaration of its own with "proves"')
    for used in entry['uses']:
        if used in elements:
            if elements[used]['kind'] != 'theorem':
                continue
            target = elements[elements[used]['statement_of']]
            need(target['statement_settled'],
                 f'{statement} is settled, and the new proof of {declaration} names {used}, which is not settled; '
                 'the statement would no longer be settled')
            need('formal' not in carried or target['statement_formal'],
                 f'{statement} has a formal proof, and the new proof of {declaration} names {used}, which has none; '
                 'the statement would no longer be formal')
        else:
            added = receipt['entries'].get(used)
            need(added is None or added['kind'] != 'theorem',
                 f'{statement} is settled, and the new proof of {declaration} names {used}, which this candidate adds '
                 'and which is not settled yet. Publish the new statement first; the derivation of the old statement '
                 'from it replaces the old proof once the new statement is settled')
    need('formal' not in carried or not beyond_allowed(entry, model['allowed_axioms']),
         f'{statement} has a formal proof, and the new proof of {declaration} is not formal; the statement would no '
         'longer be formal')


def change_check(root, model, owner, held=None):
    """A peer's candidate change: its manifest, its files, and what a machine can decide about them."""
    try:
        change = load_change(root)
    except CanonError as exc:
        raise Invalid(str(exc)) from None
    receipt = prepared_candidate(root)
    known = set(model['elements']) | set(receipt['added'])
    if held is not None:
        for item in change['replace']:
            statement = model['elements'].get(item['declaration'], {}).get('statement_of')
            if statement and model['elements'][statement]['statement_settled']:
                # A settled statement can no longer be taken, so no section is asked for it.
                stays_settled(model, receipt, item['declaration'])
            else:
                need(statement in held,
                     f"replacing the proof of {item['declaration']} requires holding a section on "
                     f"{statement or 'it'}; register one through its lease")
    paths = {name_path(name): name for name in known}
    for relative in change['approaches']:
        folder, _, entry = relative.rpartition('/')
        need(folder in paths, f'approaches/{relative}: its folder follows the name of no element')
        identifier(entry[:-3])
    for relative in change['understanding']:
        need('/' not in relative, f'questions/{relative}: one file per question, named by its ID')
        qid = relative[:-3]
        need(qid in model['questions'] or qid in model['question_aliases'],
             f'questions/{relative} names no question of the frontier')
    questions = array(change['questions'], 'questions')
    proposed = unique(questions)
    prefix = identifier(owner) + '-'
    need(all(q.startswith(prefix) and len(q) > len(prefix) for q in proposed),
         'new question proposals must use their peer session prefix: ' + prefix)
    need(not proposed & taken_question_ids(model), 'question proposal ID already names a question')
    for question in questions:
        need(set(question) == {'id', 'statement', 'grounds'}, 'a question proposal has "id", "statement" and "grounds"')
        text(question.get('statement'), 'question.statement')
        text(question.get('grounds'), 'question.grounds')
    resolutions = array(change['resolutions'], 'resolutions')
    unique(resolutions)
    for resolution in resolutions:
        target = resolution.get('question')
        need(target in model['questions'] or target in model['question_aliases'],
             'a resolution must name an existing question')
        need(canonical_question(model, target) != ROOT_QUESTION, 'the root question is not resolved by an explanation')
        need(any(canonical_question(model, relative[:-3]) == canonical_question(model, target)
                 for relative in change['understanding']),
             f'a resolution of {target} comes with the text that settles it, as questions/{target}.md')
    need(not change['retire'], 'only the organizer retires an alternative proof')
    regular_tree(root)
    return change, receipt


def concerns_check(values, known):
    unique(array(values, 'concerns'))
    for concern in values:
        text(concern.get('reason'), 'concern.reason')
        text(concern.get('evidence'), 'concern.evidence')
        targets = array(concern.get('targets'), 'concern.targets')
        need(bool(targets), 'a concern names the elements whose proof it questions')
        for name in targets:
            need(name in known, 'concern targets an unknown element: ' + str(name))


def findings_check(values, model, known):
    for finding in array(values, 'findings'):
        need(finding.get('status') in ('cleared', 'confirmed', 'undetermined'), 'unknown finding status')
        text(finding.get('reason'), 'finding.reason')
        for cid in array(finding.get('concerns'), 'finding.concerns'):
            need(cid in model['concerns'], 'unknown concern')
        for key in ('invalidates', 'validates'):
            for name in array(finding.get(key, []), key):
                need(name in known, 'finding targets an unknown element: ' + str(name))
        for qid in array(finding.get('reopens', []), 'reopens'):
            need(qid in model['questions'] or qid in model['question_aliases'], 'finding reopens an unknown question')


def audit_formal(instance, session, check, receipt):
    """Review's own compile of the candidate: a finished build of this session that compiled the changed modules afresh."""
    from lean_broker import BUILD_ID, Paths, job_record
    need(isinstance(check, dict), 'confirming a proof that is complete in Lean needs formal_check')
    build = text(check.get('build'), 'formal_check.build')
    need(BUILD_ID.fullmatch(build), 'formal_check.build is the ID of the build that commands.verify reported')
    record = job_record(Paths(instance), build)
    if record and record['status'] == 'duplicate':
        record = job_record(Paths(instance), record['duplicate_of'])
    need(record and record['status'] == 'finished' and record['session'] == session,
         'formal check must be a finished build of this reviewing session')
    modules = record['modules']
    need(all(m['status'] == 'cached' or (m['status'] == 'finished' and m.get('exit_code') == 0) for m in modules.values()),
         'the review build did not compile')
    for module in receipt['changed_modules']:
        need(modules.get(module, {}).get('job') and modules[module]['status'] == 'finished',
             f'review must compile the changed module {module} itself (commands.verify does)')
    outcome = Path(instance) / 'sessions' / session / 'work/verify/outcome.json'
    need(outcome.is_file() and read_json(outcome).get('build') == record['id'] and read_json(outcome).get('ok') is True,
         'formal_check.build is not the build of the last successful commands.verify')


def assessment_check(data, root, candidate, model, instance, sid):
    need(type(data.get('publish')) is bool, 'publish must be Boolean')
    text(data.get('reason'), 'assessment.reason')
    text(data.get('contribution'), 'assessment.contribution')
    file(root, data.get('feedback'))
    try:
        change = load_change(candidate)
    except CanonError as exc:
        raise Invalid(str(exc)) from None
    receipt = read_json(Path(candidate) / PREPARED)
    judged = receipt['added'] + receipt['replaced']
    rows = array(data.get('elements'), 'assessment.elements')
    need(len(rows) == len(judged) and {x.get('element') for x in rows} == set(judged),
         'judge each element the candidate adds or whose proof it replaces exactly once: ' + ', '.join(judged))
    formal = False
    for row in rows:
        entry = receipt['entries'][row['element']]
        need(row.get('correct') in VERDICTS, 'correct is one of ' + ', '.join(VERDICTS))
        need(type(row.get('accepted')) is bool, 'accepted must be Boolean')
        text(row.get('reason'), 'element reason')
        proved = entry['kind'] == 'theorem' and (entry['lean_proof'] == 'complete' or entry['written_proof'])
        if proved:
            need(row['correct'] != 'not_applicable', f"{row['element']} has a proof; judge whether it is correct")
        else:
            need(row['correct'] == 'not_applicable' and not row['accepted'],
                 f"{row['element']} has no proof to judge; use correct: not_applicable")
        need(not row['accepted'] or row['correct'] == 'confirmed', 'only a proof confirmed as correct can be accepted')
        if row['element'] in receipt['replaced']:
            if model['elements'].get(row['element'], {}).get('standing') == 'no_proof':
                # A first proof has no other proof to take the place of; it enters with the verdict given here.
                need(row.get('replaces') in (None, True),
                     f"{row['element']} has no proof in the canon yet, so its first proof enters with your verdict; "
                     '"replaces" is asked only where the canon already has a proof')
            else:
                # Review says whether the new proof takes the place of the one the canon has; the runner
                # replaces only those, and the others are recorded among the approaches tried.
                need(type(row.get('replaces')) is bool,
                     f"{row['element']} already has a proof in the canon; say with \"replaces\" whether the new one takes its place")
                # A statement that is settled through this proof alone stays settled only under an accepted proof.
                need(not row['replaces'] or not carried_by(model, row['element'])
                     or (row['correct'] == 'confirmed' and row['accepted']),
                     f"{row['element']} holds the proof through which a settled statement is settled; a new proof takes "
                     'its place only when you confirm and accept it, so answer "replaces": false otherwise')
        else:
            need(row.get('replaces') is None,
                 f"{row['element']} is added by the candidate; \"replaces\" is asked only of a proof that would take "
                 'the place of one the canon has, and an added element enters with your verdict')
        formal = formal or (proved and entry['lean_proof'] == 'complete' and row['correct'] == 'confirmed')
    if formal:
        audit_formal(instance, sid, data.get('formal_check'), receipt)
    questions = {q['id'] for q in change['questions']}
    verdicts = {}
    for row in array(data.get('questions', []), 'assessment.questions'):
        need(row.get('proposal') in questions and row['proposal'] not in verdicts, 'unknown/duplicate question proposal')
        need(row.get('verdict') in ('admitted', 'declined', 'revise'), 'question verdict must be admitted, declined or revise')
        text(row.get('reason'), 'question assessment reason')
        duplicate = row.get('duplicate_of')
        need(duplicate is None or duplicate in model['questions'] or duplicate in model['question_aliases'],
             'duplicate_of must name an existing question')
        need(duplicate is None or row['verdict'] == 'declined', 'a duplicate is declined')
        verdicts[row['proposal']] = row['verdict']
    need(set(verdicts) == questions, 'assess every question proposal')
    resolutions = {r['id'] for r in change['resolutions']}
    resolved = {}
    for row in array(data.get('resolutions', []), 'assessment.resolutions'):
        need(row.get('proposal') in resolutions and row['proposal'] not in resolved, 'unknown/duplicate resolution proposal')
        need(type(row.get('resolved')) is bool, 'resolved must be Boolean')
        text(row.get('reason'), 'resolution reason')
        resolved[row['proposal']] = row['resolved']
    need(set(resolved) == resolutions, 'assess every resolution proposal')
    known = set(model['elements']) | set(receipt['added'])
    concerns_check(data.get('concerns', []), known)
    findings_check(data.get('findings', []), model, known)
    if not data['publish']:
        need(not any(v == 'admitted' for v in verdicts.values()) and not any(resolved.values())
             and not data.get('concerns') and not data.get('findings'),
             'excluded candidate cannot change shared mathematical state')
    for path in Path(root).iterdir():
        need(path.name.casefold() not in ('change.json', 'applied.json', 'provenance.json', 'verify.json'),
             'review output top-level names change.json, applied.json, provenance.json and verify.json are '
             'reserved for publication attachments')
    regular_tree(root)


def comprehensive_check(data, root, model):
    file(root, data.get('feedback'))
    findings_check(data.get('findings'), model, set(model['elements']))
    concerns_check(data.get('concerns', []), set(model['elements']))
    regular_tree(root)


def organization_check(data, root, model, batch):
    """An organizer's output: the batch it answers for, question merges, and optionally a change of its own.

    Its change adds elements stating that two definitions or statements agree, with Lean proofs, or
    rearranges modules; `retire` names an alternative proof whose text now stands under the statement's
    own name. The machine checks of that change are made when it is prepared and again at publication."""
    need(data.get('batch') == batch, 'organizer must acknowledge its exact assigned batch')
    for merge in array(data.get('merge_questions', []), 'merge_questions'):
        need(merge.get('from') in model['questions'] and merge.get('into') in model['questions'],
             'question merge needs existing questions')
        need(ROOT_QUESTION not in (canonical_question(model, merge['from']), canonical_question(model, merge['into'])),
             'the root question keeps its identity: it neither merges into another question nor absorbs one')
        text(merge.get('reason'), 'question merge reason')
    if not (Path(root) / 'change.json').exists():
        need(not (Path(root) / 'rewrite').exists() and not (Path(root) / 'lean').exists() and not data.get('delete'),
             'Lean files and "delete" take effect only as part of a change; write change.json with them')
    else:
        try:
            change = load_change(root)
        except CanonError as exc:
            raise Invalid(str(exc)) from None
        prepared_candidate(root)
        need(not change['questions'] and not change['resolutions'] and not change['approaches']
             and not change['understanding'],
             'an organizer change holds Lean modules, replacements and records only')
        for item in change['retire']:  # load_change has confirmed the form of each entry
            need(model['elements'].get(item['alternative'], {}).get('statement_of') == item['into'],
                 f"{item['alternative']} is not another proof of {item['into']}")
            # The proof under the statement's own name leaves the source, so the one that takes its
            # place may not stand lower than it: no review has compared the two.
            moving, leaving = model['elements'][item['alternative']], model['elements'][item['into']]
            rank = lambda e: (('no_proof', 'not_confirmed', 'held', 'accepted').index(e['standing']),
                              e['lean_proof'] == 'complete')
            need(rank(moving) >= rank(leaving),
                 f"{item['alternative']} would take the place of a proof of {item['into']} that stands higher; "
                 'a retirement keeps the proof with the higher standing')
    regular_tree(root)


def pipeline_sections(instance, state, pipeline, model, session):
    """The elements on which the sessions of one pipeline hold sections."""
    if pipeline is None:
        return set()
    entry = state['pipelines'][pipeline]
    owners = [entry['producer'], *entry['previous_peers'], entry['peer'], session]
    return {s['element'] for sid in dict.fromkeys(x for x in owners if x)
            for s in section_entries(instance, sid, model)}


def check_session(session):
    try:
        session = Path(session).resolve()
        inp = read_json(session / 'input.json')
        instance, role, task = Path(inp['instance']), inp['role'], inp['task']
        model = replay(instance)
        output = session / 'output'
        if role in PRODUCERS:
            regular_tree(output)
            outcome = no_research_outcome(session, role)
            if outcome is not None:
                reported_availability(session, outcome)
            return []  # research, including interrupted work, remains eligible for peer
        if role == 'peer':
            state = read_json(instance / 'runner/state.json')
            change_check(output, model, session.name,
                         pipeline_sections(instance, state, inp.get('pipeline'), model, session.name))
        elif role == 'review' and task['kind'] == 'candidate':
            candidate = Path(task['candidate'])
            need(tree_hashes(candidate) == task['candidate_hashes'], 'candidate changed after review assignment')
            assessment_check(read_json(output / 'assessment.json'), output, candidate, model,
                             instance, inp['session'])
        elif role == 'review':
            comprehensive_check(read_json(output / 'assessment.json'), output, model)
        elif role == 'organizer':
            organization_check(read_json(output / 'organization.json'), output, model, task['batch'])
        else:
            raise Invalid('unknown role')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [str(exc)]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', type=Path)
    args = parser.parse_args()
    errors = check_session(args.session)
    print(json.dumps({'ok': not errors, 'errors': errors}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
