"""Check transport structure and evidence identities; sessions judge mathematics."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from knowledge import claim_key, replay
from runtime_support import read_json
from settings import PRODUCERS
from availability import no_research_outcome, reported_availability


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def text(value, name):
    need(isinstance(value, str) and bool(value.strip()), name + ': nonempty text required')
    return value


def identifier(value):
    need(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value), 'invalid identifier')
    return value


def array(value, name):
    need(isinstance(value, list), name + ': array required')
    return value


def file(root, name):
    text(name, 'file')
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and not any(c in name for c in ('\\', ':', '\0')),
         'file must be a relative /-separated path')
    actual = (Path(root) / name).resolve()
    need(actual.is_relative_to(Path(root).resolve()) and actual.is_file(), 'missing or escaping file: ' + name)
    return actual


def regular_tree(root):
    for p in [Path(root), *Path(root).rglob('*')]:
        need(not p.is_symlink() and not p.is_junction(), 'filesystem links cannot be published: ' + str(p))


def signed(value, known):
    need(isinstance(value, dict) and value.get('node') in known, 'signed statement needs an existing/admitted node')
    need(value.get('outcome') in ('proved', 'refuted'), 'outcome must be proved or refuted')


def unique(rows, key='id'):
    ids = [identifier(row.get(key)) for row in rows]
    need(len(ids) == len(set(ids)), 'duplicate ' + key)
    return set(ids)


def record_check(data, root, model, proposal_owner=None):
    for path in Path(root).iterdir():
        need(path.name.casefold() not in ('review', 'provenance.json'),
             'candidate top-level names review and provenance.json are reserved for publication attachments')
    for key in ('title', 'description'):
        text(data.get(key), key)
    file(root, data.get('exposition'))
    claims = array(data.get('claims'), 'claims')
    ids = unique(claims)
    for claim in claims:
        text(claim.get('statement'), 'claim.statement')
        text(claim.get('evidence'), 'claim.evidence')
        need(claim.get('by') in ('producer', 'peer'), 'claim.by must identify producer or peer')
        for ref in array(claim.get('dependencies', []), 'claim.dependencies'):
            need(isinstance(ref, dict), 'dependency must be a claim reference')
            need((ref.get('record') == 'self' and ref.get('claim') in ids) or claim_key(ref) in model['claims'],
                 'unknown dependency claim')
    nodes = array(data.get('nodes', []), 'nodes')
    proposed = unique(nodes)
    if proposal_owner is not None:
        prefix = identifier(proposal_owner) + '-'
        need(all(node.startswith(prefix) and len(node) > len(prefix) for node in proposed),
             'new node proposals must use their peer session prefix: ' + prefix)
    need(not proposed.intersection(set(model['nodes']) | set(model['aliases'])), 'new node proposal ID already exists; use existing node directly')
    known = set(model['nodes']) | set(model['aliases']) | proposed
    for node in nodes:
        text(node.get('statement'), 'node.statement')
        need(node.get('connection') in ids, 'node.connection must name a claim')
    for relation in array(data.get('relations', []), 'relations'):
        identifier(relation['id'])
        need(relation.get('claim') in ids, 'relation needs its proving claim')
        premises = array(relation.get('premises'), 'relation.premises')
        need(bool(premises), 'relation needs premises')
        for item in premises:
            signed(item, known)
        signed(relation.get('conclusion'), known)
    unique(data.get('relations', []))
    for solution in array(data.get('solutions', []), 'solutions'):
        identifier(solution['id'])
        signed(solution, known)
        need(solution.get('claim') in ids, 'solution needs its proving claim')
        for dep in array(solution.get('formal_dependencies', []), 'formal_dependencies'):
            signed(dep, known)
        lean = solution.get('lean')
        if lean is not None:
            need(isinstance(lean, dict), 'lean must be an object or null')
            text(lean.get('theorem'), 'lean.theorem')
            sources = array(lean.get('sources'), 'lean.sources')
            need(bool(sources), 'Lean solution needs sources')
            for source in sources:
                file(root, source)
    unique(data.get('solutions', []))
    need(not ({s['id'] for s in data.get('solutions', [])} & {r['id'] for r in data.get('relations', [])}),
         'solution and relation IDs must be distinct')
    glossary = array(data.get('glossary'), 'glossary')
    unique(glossary)
    for term in glossary:
        text(term.get('name'), 'term.name')
        text(term.get('definition'), 'term.definition')
        need(isinstance(term.get('symbol', ''), str), 'term.symbol must be text')
        need(type(term.get('global_candidate', False)) is bool, 'global_candidate must be Boolean')
    regular_tree(root)


def concerns_check(values, model, local=None):
    unique(array(values, 'concerns'))
    for concern in values:
        text(concern.get('reason'), 'concern.reason')
        text(concern.get('evidence'), 'concern.evidence')
        targets = array(concern.get('targets'), 'concern.targets')
        need(bool(targets), 'concern needs an identified claim')
        for ref in targets:
            need((local and ref.get('record') == 'self' and ref.get('claim') in local) or claim_key(ref) in model['claims'],
                 'concern targets unknown claim')


def audit_formal(instance, session, check, solution, candidate):
    from lean_broker import Paths, job_record, JOB_ID, BUILD_ID
    need(isinstance(check, dict), 'formal acceptance needs formal_check')
    job = text(check.get('job'), 'formal_check.job')
    need(JOB_ID.fullmatch(job) or BUILD_ID.fullmatch(job), 'invalid broker job ID')
    receipt = job_record(Paths(instance), job)
    if receipt and receipt['status'] == 'duplicate':
        # A repeated submission names the job already doing the work; waiting on either ID gives
        # the same result (lean.md), so the audit follows it to that job as well.
        job = receipt['duplicate_of']
        receipt = job_record(Paths(instance), job)
    need(receipt and receipt['status'] == 'finished' and receipt['session'] == session,
         'formal check must be a finished job of this reviewing session')
    need(check.get('alignment') == 'matches', 'formal acceptance requires exact mathematical correspondence')
    text(check.get('reason'), 'formal_check.reason')
    theorem = solution.get('lean', {}).get('theorem')
    need(theorem and check.get('theorem') == theorem, 'formal theorem differs from candidate')
    if JOB_ID.fullmatch(job):
        need(receipt.get('exit_code') == 0, 'review compile failed')
        log = Path(instance) / 'runner/lean/jobs' / job / 'stdout.log'
    else:
        targets = [receipt['modules'][n] for n in receipt['targets']]
        need(all(m['status'] == 'finished' and m.get('exit_code') == 0 and m.get('job') for m in targets),
             'review must freshly compile targets (use --fresh-targets)')
        log = None
        logs = [Path(instance) / 'runner/lean/jobs' / m['job'] / 'stdout.log' for m in targets]
    output = log.read_text(encoding='utf-8', errors='replace') if log else '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in logs)
    found = re.findall(r"^[ \t]*['\"]?" + re.escape(theorem) + r"['\"]?\s+(?:depends on axioms:\s*\[([^\]]*)\]|(does not depend on any axioms))", output, re.MULTILINE)
    need(bool(found), 'review compile did not print target axiom dependencies')
    axioms = set()
    for names, no_axioms in found:
        if not no_axioms:
            axioms.update(x.strip() for x in names.split(',') if x.strip())
    inp = read_json(Path(instance) / 'sessions' / session / 'input.json')
    allowed = set(inp['settings']['lean']['allowed_axioms'])
    need('sorryAx' not in axioms and axioms <= allowed, 'target uses an unapproved axiom')
    need(set(check.get('axioms', [])) == axioms, 'reported axioms differ from broker output')
    hashes = check.get('source_hashes', {})
    source_files = check.get('source_files', {})
    compiled = {str(Path(m['source']).resolve()): m.get('source_sha256') for m in receipt.get('modules', {}).values()} if BUILD_ID.fullmatch(job) else {str(Path(receipt['source']).resolve()): receipt.get('source_sha256')}
    for source in solution['lean']['sources']:
        original = file(candidate, source).read_bytes()
        need(hashes.get(source) == hashlib.sha256(original).hexdigest(),
             'formal evidence must identify the final candidate source bytes: ' + source)
        working = file(Path(instance) / 'sessions' / session, source_files.get(source))
        need(str(working) in compiled, 'checked source is absent from the reviewing compile')
        copied = working.read_bytes()
        need(compiled[str(working)] == hashlib.sha256(copied).hexdigest(), 'reviewed source bytes differ from the submitted compile')
        need(copied.startswith(original), 'review must compile an unchanged copy of final sources')
        suffix = copied[len(original):].decode('utf-8-sig').strip()
        need(not suffix or all(re.fullmatch(r"\s*#print axioms [A-Za-z0-9_.'\u0080-\uffff]+\s*", line) for line in suffix.splitlines()),
             'only axiom inspection commands may be appended to the reviewed source')


def assessment_check(data, root, record, candidate, model, instance, sid, verify_jobs=True):
    need(type(data.get('publish')) is bool, 'publish must be Boolean')
    text(data.get('reason'), 'assessment.reason')
    text(data.get('index_assessment'), 'index_assessment')
    file(root, data.get('feedback'))
    need(type(data.get('glossary_approved')) is bool, 'glossary_approved must be Boolean')
    ids = {c['id'] for c in record['claims']}
    rows = array(data.get('claims'), 'assessment.claims')
    need(len(rows) == len(ids) and {x.get('claim') for x in rows} == ids, 'assess each candidate claim exactly once')
    supported = set()
    for row in rows:
        need(row.get('status') in ('supported', 'unsupported', 'undetermined'), 'unknown claim assessment')
        text(row.get('reason'), 'claim assessment reason')
        if row['status'] == 'supported':
            supported.add(row['claim'])
    relations = {r['id']: r for r in record.get('relations', [])}
    accepted_relations = []
    seen = set()
    for row in array(data.get('relations'), 'assessment.relations'):
        need(row.get('proposal') in relations and row['proposal'] not in seen, 'unknown/duplicate relation proposal')
        seen.add(row['proposal'])
        need(type(row.get('accepted')) is bool, 'relation accepted must be Boolean')
        text(row.get('reason'), 'relation assessment reason')
        if row['accepted']:
            relation = relations[row['proposal']]
            need(relation['claim'] in supported, 'accepted relation needs a supported claim')
            accepted_relations.append(relation)
    need(seen == set(relations), 'assess every relation proposal')
    nodes = {n['id']: n for n in record.get('nodes', [])}
    resolutions = {}
    for row in array(data.get('nodes'), 'assessment.nodes'):
        need(row.get('proposal') in nodes and row['proposal'] not in resolutions, 'unknown/duplicate node proposal')
        target = row.get('node')
        need(target is None or target == row['proposal'] or target in model['nodes'], 'node resolution must reuse an existing node or admit the proposal')
        text(row.get('reason'), 'node resolution reason')
        if target:
            need(nodes[row['proposal']]['connection'] in supported, 'new node needs supported connection')
        resolutions[row['proposal']] = target
    need(set(resolutions) == set(nodes), 'resolve every node proposal, with null for an unadmitted node')
    connected = set(model['nodes']) | set(model['aliases'])
    for proposal, target in resolutions.items():
        if target in connected:
            connected.add(proposal)
    while True:
        before = set(connected)
        for relation in accepted_relations:
            members = {p['node'] for p in relation['premises']} | {relation['conclusion']['node']}
            if members & connected:
                connected.update(members)
        if before == connected:
            break
    need(all(target is None or proposal in connected for proposal, target in resolutions.items()),
         'admitted nodes must connect to existing research through accepted relations')
    known = set(model['nodes']) | set(model['aliases']) | {p for p, n in resolutions.items() if n}
    for relation in accepted_relations:
        for item in relation['premises'] + [relation['conclusion']]:
            signed(item, known)
    solutions = {s['id']: s for s in record.get('solutions', [])}
    seen = set()
    for row in array(data.get('solutions'), 'assessment.solutions'):
        need(row.get('proposal') in solutions and row['proposal'] not in seen, 'unknown/duplicate solution proposal')
        seen.add(row['proposal'])
        need(row.get('level') in ('none', 'informal', 'formal'), 'unknown assurance level')
        text(row.get('reason'), 'solution assessment reason')
        if row['level'] != 'none':
            solution = solutions[row['proposal']]
            signed(solution, known)
            need(solution['claim'] in supported, 'accepted solution needs a supported claim')
            for dep in row.get('formal_dependencies', solution.get('formal_dependencies', [])):
                signed(dep, known)
            if row['level'] == 'formal' and verify_jobs:
                audit_formal(instance, sid, row.get('formal_check'), solution, candidate)
    need(seen == set(solutions), 'assess every solution proposal')
    concerns_check(data.get('concerns', []), model, ids)
    findings_check(data.get('findings', []), model)
    glossary_check(data.get('glossary', []))
    if not data['publish']:
        need(not accepted_relations and not any(resolutions.values()) and
             not any(r['level'] != 'none' for r in data['solutions']) and not data.get('concerns') and not data.get('findings'),
             'excluded candidate cannot change shared mathematical state')
    regular_tree(root)


def comprehensive_check(data, root, model):
    file(root, data.get('feedback'))
    text(data.get('index_assessment'), 'index_assessment')
    findings_check(data.get('findings'), model)
    concerns_check(data.get('concerns', []), model)
    glossary_check(data.get('glossary', []))
    regular_tree(root)


def findings_check(values, model):
    for finding in array(values, 'findings'):
        need(finding.get('status') in ('cleared', 'confirmed', 'undetermined'), 'unknown finding status')
        text(finding.get('reason'), 'finding.reason')
        for update in finding.get('dependency_updates', []):
            need(update.get('proof') in model['direct'] or update.get('proof') in model['relations'], 'dependency update needs an existing proof route')
            text(update.get('reason'), 'dependency update reason')
            for dep in array(update.get('dependencies'), 'dependency update dependencies'):
                signed(dep, set(model['nodes']) | set(model['aliases']))
        for cid in array(finding.get('concerns'), 'finding.concerns'):
            need(cid in model['concerns'], 'unknown concern')
        need('clears' not in finding and 'cleared_uses' not in finding,
             'a finding withdraws or validates claims; clears and cleared_uses are not applied')
        for key in ('invalidates', 'validates'):
            for ref in array(finding.get(key, []), key):
                need(claim_key(ref) in model['claims'], 'finding targets unknown claim')


def organization_check(data, model, batch):
    need(data.get('batch') == batch, 'organizer must acknowledge its exact assigned batch')
    modules = array(data.get('modules'), 'modules')
    ids = unique(modules)
    need(len({s.lower() for s in ids}) == len(ids), 'module IDs collide on case-insensitive filesystems')
    for module in modules:
        text(module.get('title'), 'module.title')
        text(module.get('description'), 'module.description')
        for rid in array(module.get('records'), 'module.records'):
            need(rid in model['records'], 'module lists unknown record')
    for rid in array(data.get('shared_context'), 'shared_context'):
        need(rid in model['records'], 'unknown shared-context record')
    filed = set(data['shared_context']) | {r for m in modules for r in m['records']}
    need(set(batch) <= filed, 'place each assigned batch record in shared context or a module')
    glossary_check(data.get('glossary', []))
    for key in data.get('promote', []):
        need(key in model['terms'], 'promotion needs a published local term')
    for key in data.get('refuse', []):
        need(key in model['global_terms'] and model['global_terms'][key]['membership'] == 'candidate',
             'only a pending candidate may be refused')
    promoted = {next((primary for primary, member in model['global_terms'].items()
                      if key in member['merged']), key) for key in data.get('promote', [])}
    available = (set(model['global_terms']) | promoted) - set(data.get('refuse', []))
    for merge in data.get('merge_terms', []):
        need(merge['keep'] in available, 'merge primary term is not available')
        for other in merge['others']:
            need(other in available and other != merge['keep'], 'unknown or duplicate merged term')
            available.remove(other)
        text(merge.get('reason'), 'term merge reason')
    for merge in data.get('merge_nodes', []):
        need(merge['from'] in model['nodes'] and merge['into'] in model['nodes'], 'merge needs existing nodes')
        text(merge.get('reason'), 'node merge reason')


def glossary_check(entries):
    unique(array(entries, 'glossary'))
    for term in entries:
        text(term.get('name'), 'term.name')
        text(term.get('definition'), 'term.definition')
        need(isinstance(term.get('symbol', ''), str), 'term.symbol must be text')


def check_session(session, verify_jobs=True):
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
            record_check(read_json(output / 'record.json'), output, model, session.name)
        elif role == 'review' and task['kind'] == 'candidate':
            candidate = Path(task['candidate'])
            actual = {p.relative_to(candidate).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate.rglob('*') if p.is_file()}
            need(actual == task['candidate_hashes'], 'candidate changed after review assignment')
            record = read_json(candidate / 'record.json')
            record_check(record, candidate, model, candidate.parent.name)
            assessment_check(read_json(output / 'assessment.json'), output, record, candidate, model,
                             instance, inp['session'], verify_jobs)
        elif role == 'review':
            comprehensive_check(read_json(output / 'assessment.json'), output, model)
        elif role == 'organizer':
            organization_check(read_json(output / 'organization.json'), model, task['batch'])
            regular_tree(output)
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
