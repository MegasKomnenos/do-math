import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check import Invalid, assessment_check, findings_check, organization_check
from coordination import board, lease, lease_table, release, section, wait
from knowledge import canonical, formal_ready, render, replay, root_solved, sufficient_closure
from runner import Runner, archive_finished, initialize, main
from runtime_support import read_json, write_json
from settings import defaults, validate


def record(claims=None, nodes=None, relations=None, solutions=None, glossary=None):
    return {'title': 'Investigation', 'description': 'A precise contribution with its limitations.',
            'exposition': 'record.md', 'claims': claims or [], 'nodes': nodes or [],
            'relations': relations or [], 'solutions': solutions or [], 'glossary': glossary or []}


def claim_row(cid, dependencies=None):
    return {'id': cid, 'statement': cid, 'evidence': 'record.md', 'by': 'producer', 'dependencies': dependencies or []}


def assessment(data, formal=()):
    return {'publish': True, 'reason': 'Useful work.', 'index_assessment': 'Supported within its scope.',
            'feedback': 'feedback.md', 'glossary_approved': True,
            'claims': [{'claim': c['id'], 'status': 'supported', 'reason': 'Argument checked.'} for c in data['claims']],
            'nodes': [{'proposal': n['id'], 'node': n['id'], 'reason': 'Connection checked.'} for n in data['nodes']],
            'relations': [{'proposal': r['id'], 'accepted': True, 'reason': 'Implication checked.'} for r in data['relations']],
            'solutions': [{'proposal': s['id'], 'level': 'formal' if s['id'] in formal else 'informal', 'reason': 'Exact statement.'} for s in data['solutions']],
            'concerns': []}


def take(session, node, statement=None, reasons=None, leased=False):
    """Register a section through the node's lease: the whole node unless a statement is given."""
    session = Path(session)
    request = session / ('section-' + uuid.uuid4().hex + '.json')
    write_json(request, {'whole': statement is None, 'statement': statement, 'reasons': reasons or {}})
    if not leased:
        taken = lease(session, node)
        if not taken['leased']:
            return {'registered': False, **taken}
    return section(session, node, request)


def implication(rid, premise, conclusion='root', outcome='proved'):
    return {'id': rid, 'claim': rid, 'premises': [{'node': premise, 'outcome': outcome}],
            'conclusion': {'node': conclusion, 'outcome': 'proved'}}


def solution(sid, node, cid, outcome='proved', dependencies=None):
    return {'id': sid, 'node': node, 'outcome': outcome, 'claim': cid, 'formal_dependencies': dependencies or [], 'lean': None}


class InstanceCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'goal.md').write_text('For every natural number n, n + 0 = n.', encoding='utf-8')
        self.instance = self.root / 'instance'
        initialize(self.instance, self.root / 'goal.md')
        self.seq = 0
        self.skill = self.root / 'skill'
        installed = Path(__file__).resolve().parents[2]
        for name in ('reference', 'roles', 'resume'):
            shutil.copytree(installed / name, self.skill / name)
        shutil.copyfile(installed / 'SKILL.md', self.skill / 'SKILL.md')

    def publish(self, rid, data, review=None, role='attempt'):
        self.seq += 1
        folder = self.instance / 'knowledge/records' / rid
        (folder / 'review').mkdir(parents=True)
        write_json(folder / 'record.json', data)
        write_json(folder / 'review/assessment.json', review or assessment(data))
        (folder / 'record.md').write_text('The complete argument.', encoding='utf-8')
        (folder / 'review/feedback.md').write_text('Checked.', encoding='utf-8')
        write_json(self.instance / 'knowledge/events' / (rid + '.json'),
                   {'id': rid, 'sequence': self.seq, 'kind': 'record', 'producer_role': role, 'folder': 'records/' + rid})
        return folder

    def event(self, eid, kind, data):
        self.seq += 1
        sub = 'reviews' if kind == 'review' else 'organizations'
        folder = self.instance / 'knowledge' / sub / eid
        folder.mkdir(parents=True)
        write_json(folder / ('assessment.json' if kind == 'review' else 'organization.json'), data)
        write_json(self.instance / 'knowledge/events' / (eid + '.json'),
                   {'id': eid, 'sequence': self.seq, 'kind': kind, 'folder': sub + '/' + eid})

    def reduction(self):
        return record([claim_row('reduce')], [{'id': 'Q', 'statement': 'Q', 'connection': 'reduce'}],
                      [implication('reduce', 'Q')])


class KnowledgeTests(InstanceCase):
    def test_node_merge_preserves_old_evidence_and_relation_references(self):
        data = record(
            [claim_row('from_a'), claim_row('from_b')],
            [{'id': node, 'statement': 'The same precise proposition.', 'connection': link}
             for node, link in (('A', 'from_a'), ('B', 'from_b'))],
            [implication('from_a', 'A'), implication('from_b', 'B')])
        nodes = self.publish('rnodes', data)
        proof = self.publish('rproof', record([claim_row('p')],
                                             solutions=[solution('p', 'A', 'p')]))
        saved = {p: p.read_bytes() for folder in (nodes, proof)
                 for p in folder.rglob('*') if p.is_file()}
        before = replay(self.instance)
        self.assertEqual(before['nodes']['B']['state'], 'unresolved')
        self.assertNotIn('rnodes/from_b', before['proofs'])
        organization = {'batch': ['rnodes', 'rproof'], 'modules': [],
                        'shared_context': ['rnodes', 'rproof'],
                        'merge_nodes': [{'from': 'A', 'into': 'B',
                                         'reason': 'The statements and definitions are identical.'}]}
        with self.assertRaisesRegex(Invalid, 'merge needs existing nodes'):
            organization_check({**organization, 'merge_nodes': [
                {'from': 'A', 'into': 'missing', 'reason': 'No such node.'}]},
                before, organization['batch'])
        organization_check(organization, before, organization['batch'])
        self.event('omerge', 'organization', organization)
        model = replay(self.instance)
        self.assertEqual(canonical(model, 'A'), 'B')
        self.assertEqual(model['proofs']['rproof/p']['node'], 'B')
        for node in ('A', 'B', 'root'):
            self.assertEqual(model['nodes'][node]['state'], 'informal_proved')
        for link in ('from_a', 'from_b'):
            self.assertEqual(model['proofs']['rnodes/' + link]['premise_proofs'], ['rproof/p'])
        render(self.instance, model, [])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        self.assertNotIn('\n## A\n', frontier)
        self.assertIn('\n## B\n', frontier)
        self.assertIn('Aliases: A', frontier)
        self.assertEqual({p: p.read_bytes() for p in saved}, saved)
        self.assertEqual(replay(self.instance), model)

    def test_node_merge_keeps_both_attempts_occupied_until_both_pipelines_end(self):
        self.publish('rnodes', record(
            [claim_row('from_a'), claim_row('from_b')],
            [{'id': node, 'statement': 'The same precise proposition.', 'connection': link}
             for node, link in (('A', 'from_a'), ('B', 'from_b'))],
            [implication('from_a', 'A'), implication('from_b', 'B')]))
        engine = Runner(self.instance, self.skill)
        sessions, pipelines, declarations = [], [], {}
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = engine.identity['pid']
            for node in ('A', 'B'):
                key = engine.producer('attempt')
                self.assertTrue(engine.dispatch(key))
                job = engine.state['jobs'][key]
                sid = job['session']
                sessions.append(sid)
                pipelines.append(job['pipeline'])
                self.assertTrue(take(engine.session_dir(sid), node)['registered'])
                path = engine.session_dir(sid) / 'declaration.json'
                declarations[path] = path.read_bytes()
        organization = {'batch': ['rnodes'], 'modules': [], 'shared_context': ['rnodes'],
                        'merge_nodes': [{'from': 'A', 'into': 'B',
                                         'reason': 'The statements and definitions are identical.'}]}
        organization_check(organization, engine.model, ['rnodes'])
        self.event('omerge', 'organization', organization)
        engine = Runner(self.instance, self.skill)
        self.assertCountEqual([sid for sid, _ in engine.active()], sessions)
        self.assertEqual({row['session']: row['nodes'] for row in board(self.instance)},
                         {sid: ['B'] for sid in sessions})
        self.assertEqual(engine.available_nodes(), ['root'])
        self.assertEqual({p: p.read_bytes() for p in declarations}, declarations)
        # Publication and exclusion have lifecycle tests; here release each occupancy
        # to check that the other pipeline still holds the merged identity.
        engine.state['pipelines'][pipelines[0]]['stage'] = 'done'
        engine.save()
        self.assertEqual([(row['session'], row['nodes']) for row in board(self.instance)],
                         [(sessions[1], ['B'])])
        self.assertEqual(engine.available_nodes(), ['root'])
        engine.state['pipelines'][pipelines[1]]['stage'] = 'done'
        engine.save()
        self.assertEqual(board(self.instance), [])
        self.assertCountEqual(engine.available_nodes(), ['root', 'B'])

    def test_informal_propagation_and_formal_readiness_are_separate(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('qproof', 'Q', 'q')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['root']['state'], 'informal_proved')
        self.assertFalse(formal_ready(m, m['proofs']['r1/reduce']))
        self.assertFalse(root_solved(m))
        data = record([claim_row('qformal')], solutions=[solution('qformal', 'Q', 'qformal')])
        self.publish('r3', data, assessment(data, ['qformal']), role='formalizer')
        m = replay(self.instance)
        self.assertTrue(formal_ready(m, m['proofs']['r1/reduce']))
        self.assertEqual(m['nodes']['root']['state'], 'informal_proved')

    def test_refuting_sufficient_premise_does_not_settle_parent(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('notq')], solutions=[solution('refutation', 'Q', 'notq', 'refuted')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['Q']['state'], 'informal_refuted')
        self.assertEqual(m['nodes']['root']['state'], 'unresolved')

    def test_multiple_signed_premises(self):
        data = record([claim_row('joint')], [{'id': n, 'statement': n, 'connection': 'joint'} for n in ('A', 'B')],
                      [{'id': 'joint', 'claim': 'joint', 'premises': [{'node': 'A', 'outcome': 'proved'}, {'node': 'B', 'outcome': 'refuted'}],
                        'conclusion': {'node': 'root', 'outcome': 'proved'}}])
        self.publish('r1', data)
        self.publish('r2', record([claim_row('a')], solutions=[solution('a', 'A', 'a')]))
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'unresolved')
        self.publish('r3', record([claim_row('b')], solutions=[solution('b', 'B', 'b', 'refuted')]))
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'informal_proved')

    def test_alternative_support_survives_a_withdrawal(self):
        for i in (1, 2):
            data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
            self.publish('r' + str(i), data, assessment(data, ['p']))
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed', 'reason': 'First proof has wrong correspondence.',
                                                'invalidates': [{'record': 'r1', 'claim': 'p'}]}]})
        m = replay(self.instance)
        self.assertTrue(root_solved(m))
        self.assertEqual(m['nodes']['root']['proofs'], ['r2/p'])
        self.event('v2', 'review', {'findings': [{'concerns': [], 'status': 'confirmed', 'reason': 'Other support also withdrawn.',
                                                'invalidates': [{'record': 'r2', 'claim': 'p'}]}]})
        self.assertFalse(root_solved(replay(self.instance)))

    def test_concern_annotates_without_blocking_and_a_withdrawal_recomputes(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'boundary', 'targets': [{'record': 'r2', 'claim': 'q'}],
                                                               'reason': 'Boundary needs checking.', 'evidence': 'A missing case.'}]})
        data = record([claim_row('next'), claim_row('onward')],
                      [{'id': 'R', 'statement': 'R', 'connection': 'next'},
                       {'id': 'S', 'statement': 'S', 'connection': 'onward'}],
                      [implication('next', 'Q', 'R'), implication('onward', 'R', 'S')])
        self.publish('r3', data)
        m = replay(self.instance)
        # A pending concern changes nothing about what is held true; it annotates what rests on it.
        for nid in ('root', 'Q', 'R', 'S'):
            self.assertEqual(m['nodes'][nid]['state'], 'informal_proved')
        for pid in ('r2/q', 'r1/reduce', 'r3/next', 'r3/onward'):
            self.assertTrue(m['proofs'][pid]['concerned'])
            self.assertIn('v1/boundary', m['proofs'][pid]['concerns'])
        render(self.instance, m, [{'pipeline': 'p', 'role': 'attempt', 'stage': 'producing', 'nodes': ['S'], 'sections': []}])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        for nid in ('R', 'S'):
            section = frontier.split('## ' + nid + '\n', 1)[1].split('\n## ', 1)[0]
            self.assertIn('rests on a questioned claim', section)
            self.assertIn('v1/boundary', section)
            self.assertIn('reviews/v1/assessment.json', section)
        self.assertNotIn('Possible dependency', frontier)
        self.assertIn('Concern: see [frontier](frontier.md) for S.',
                      (self.instance / 'knowledge/board.md').read_text(encoding='utf-8'))
        # Only a finding changes standing: withdrawing q recomputes everything that rested on it.
        self.event('v2', 'review', {'findings': [{'concerns': ['v1/boundary'], 'status': 'confirmed',
                                                'reason': 'The missing case fails.', 'invalidates': [{'record': 'r2', 'claim': 'q'}]}]})
        m = replay(self.instance)
        for nid in ('root', 'Q', 'R', 'S'):
            self.assertEqual(m['nodes'][nid]['state'], 'unresolved')
        self.assertEqual(m['concerns']['v1/boundary']['status'], 'confirmed')

    def test_concern_does_not_ban_formalizer_work_on_accepted_mathematics(self):
        self.publish('r1', record([claim_row('p')], solutions=[solution('s', 'root', 'p')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'question',
            'targets': [{'record': 'r1', 'claim': 'p'}], 'reason': 'A use needs examination.', 'evidence': 'Source location.'}]})
        model = replay(self.instance)
        self.assertTrue(model['proofs']['r1/s']['concerned'])
        self.assertTrue(formal_ready(model, model['proofs']['r1/s']))

    def test_later_independent_premise_refreshes_a_concerned_relation_application(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'issue',
            'targets': [{'record': 'r2', 'claim': 'q'}],
            'reason': 'The original proof needs checking.', 'evidence': 'A questioned case.'}]})
        self.publish('r3', record(
            [claim_row('a'), claim_row('independent'), claim_row('onward')],
            [{'id': 'A', 'statement': 'A', 'connection': 'independent'},
             {'id': 'S', 'statement': 'S', 'connection': 'onward'}],
            [implication('independent', 'A', 'Q'), implication('onward', 'root', 'S')],
            [solution('a', 'A', 'a')]))
        model = replay(self.instance)
        self.assertTrue(model['proofs']['r2/q']['concerned'])
        self.assertEqual(model['concerns']['v1/issue']['status'], 'pending')
        self.assertEqual(model['proofs']['r1/reduce']['premise_proofs'], ['r3/independent'])
        self.assertFalse(model['proofs']['r1/reduce']['concerned'])
        self.assertEqual(model['nodes']['S']['state'], 'informal_proved')

    def test_glossary_refusal_does_not_reappear_on_replay(self):
        term = {'id': 't', 'name': 'Shared object', 'symbol': 'X', 'definition': 'X := 1.', 'global_candidate': True}
        self.publish('r1', record(glossary=[term]))
        self.event('o1', 'organization', {'batch': ['r1'], 'modules': [], 'shared_context': [], 'refuse': ['r1/t']})
        self.assertNotIn('r1/t', replay(self.instance)['global_terms'])
        self.event('o2', 'organization', {'batch': [], 'modules': [], 'shared_context': [], 'promote': ['r1/t']})
        m = replay(self.instance)
        self.assertEqual(m['global_terms']['r1/t']['membership'], 'permanent')
        with self.assertRaises(Invalid):
            organization_check({'batch': [], 'modules': [], 'shared_context': [], 'refuse': ['r1/t']}, m, [])

    def test_clearance_fields_are_not_applied_and_are_rejected(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        m = replay(self.instance)
        for stale in ({'cleared_uses': [{'relation': 'r1/reduce', 'premise_proofs': ['r2/q']}]},
                      {'clears': [{'record': 'r2', 'claim': 'q'}]}):
            with self.subTest(field=next(iter(stale))), self.assertRaisesRegex(Invalid, 'not applied'):
                findings_check([{'concerns': [], 'status': 'undetermined', 'reason': 'An exact use.', **stale}], m)

    def test_refuting_a_necessary_condition_refutes_the_node(self):
        # root implies K is accepted; K refuted therefore refutes root, with no second relation written.
        self.publish('r1', record([claim_row('necessary')], [{'id': 'K', 'statement': 'K', 'connection': 'necessary'}],
                                 [implication('necessary', 'root', 'K')]))
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'unresolved')
        self.publish('r2', record([claim_row('notk')], solutions=[solution('refutation', 'K', 'notk', 'refuted')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['K']['state'], 'informal_refuted')
        self.assertEqual(m['nodes']['root']['state'], 'informal_refuted')
        proof = m['proofs']['r1/necessary~0']
        self.assertEqual((proof['node'], proof['outcome'], proof['derivation']), ('root', 'refuted', 'backward'))
        self.assertEqual(proof['premise_proofs'], ['r2/refutation'])
        self.assertEqual(proof['formal_dependencies'], [{'node': 'K', 'outcome': 'refuted'}])
        # A proof of K beside its accepted refutation makes K contested, so the refutation
        # of root that rested on K is no longer derived.
        self.publish('r3', record([claim_row('k')], solutions=[solution('k', 'K', 'k')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['K']['state'], 'contested')
        self.assertEqual(m['nodes']['root']['state'], 'unresolved')

    def test_dependency_update_can_name_a_backward_proof_route(self):
        # The proofs object names a relation applied backward as <relation>~<premise position>.
        self.publish('r1', record([claim_row('necessary')], [{'id': 'K', 'statement': 'K', 'connection': 'necessary'}],
                                 [implication('necessary', 'root', 'K')]))
        self.publish('r2', record([claim_row('notk')], solutions=[solution('refutation', 'K', 'notk', 'refuted')]))
        m = replay(self.instance)
        self.assertEqual(m['proofs']['r1/necessary~0']['formal_dependencies'], [{'node': 'K', 'outcome': 'refuted'}])
        finding = {'concerns': [], 'status': 'undetermined', 'reason': 'The route was traced.',
                   'dependency_updates': [{'proof': 'r1/necessary~0', 'dependencies': [],
                                           'reason': 'A direct formalization of the refutation needs no Lean result for K.'}]}
        findings_check([finding], m)
        for proof in ('r1/necessary~1', 'r1/missing~0', 'r1/necessary~'):
            wrong = {**finding, 'dependency_updates': [{**finding['dependency_updates'][0], 'proof': proof}]}
            with self.subTest(proof=proof), self.assertRaisesRegex(Invalid, 'existing proof route'):
                findings_check([wrong], m)
        self.event('v1', 'review', {'feedback': 'feedback.md', 'index_assessment': 'Dependencies corrected.',
                                    'findings': [finding]})
        self.assertEqual(replay(self.instance)['proofs']['r1/necessary~0']['formal_dependencies'], [])

    def test_multi_premise_relation_derives_in_every_direction(self):
        data = record([claim_row('joint')], [{'id': n, 'statement': n, 'connection': 'joint'} for n in ('A', 'B')],
                      [{'id': 'joint', 'claim': 'joint', 'premises': [{'node': 'A', 'outcome': 'proved'}, {'node': 'B', 'outcome': 'proved'}],
                        'conclusion': {'node': 'root', 'outcome': 'proved'}}])
        self.publish('r1', data)
        self.publish('r2', record([claim_row('notroot')], solutions=[solution('notroot', 'root', 'notroot', 'refuted')]))
        self.assertEqual(replay(self.instance)['nodes']['B']['state'], 'unresolved')
        self.publish('r3', record([claim_row('a')], solutions=[solution('a', 'A', 'a')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['B']['state'], 'informal_refuted')
        proof = m['proofs']['r1/joint~1']
        self.assertEqual(sorted(proof['premise_proofs']), ['r2/notroot', 'r3/a'])
        self.assertCountEqual(proof['formal_dependencies'], [{'node': 'A', 'outcome': 'proved'}, {'node': 'root', 'outcome': 'refuted'}])

    def test_contested_node_derives_nothing_further(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'informal_proved')
        self.publish('r3', record([claim_row('notq')], solutions=[solution('notq', 'Q', 'notq', 'refuted')]))
        m = replay(self.instance)
        self.assertEqual(m['nodes']['Q']['state'], 'contested')
        self.assertEqual(m['nodes']['root']['state'], 'unresolved')
        self.assertCountEqual(m['nodes']['Q']['proofs'], ['r2/q', 'r3/notq'])
        render(self.instance, m, [])
        self.assertIn('Opposing accepted outcomes', (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))

    def test_sufficient_closure_and_frontier_labels(self):
        self.publish('r1', self.reduction())  # Q implies root
        self.publish('r2', record([claim_row('necessary')], [{'id': 'K', 'statement': 'K', 'connection': 'necessary'}],
                                 [implication('necessary', 'root', 'K')]))
        m = replay(self.instance)
        closure = sufficient_closure(m)
        self.assertIn(('Q', 'proved'), closure)
        self.assertNotIn(('Q', 'refuted'), closure)
        self.assertIn(('K', 'refuted'), closure)
        self.assertNotIn(('K', 'proved'), closure)
        render(self.instance, m, [])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        q = frontier.split('## Q\n', 1)[1].split('\n## ', 1)[0]
        k = frontier.split('## K\n', 1)[1].split('\n## ', 1)[0]
        self.assertIn('on a sufficient path to the root', q)
        self.assertIn('a necessary condition only', k)
        self.assertNotIn('Path to root', frontier.split('## root\n', 1)[1].split('\n## ', 1)[0])

    def test_frontier_shows_which_parts_of_a_split_are_established(self):
        data = record([claim_row('cover')], [{'id': n, 'statement': n, 'connection': 'cover'} for n in ('L', 'R')],
                      [{'id': 'cover', 'claim': 'cover', 'premises': [{'node': 'L', 'outcome': 'proved'}, {'node': 'R', 'outcome': 'proved'}],
                        'conclusion': {'node': 'root', 'outcome': 'proved'}}])
        self.publish('r1', data)
        self.publish('r2', record([claim_row('left')], solutions=[solution('left', 'L', 'left')]))
        m = replay(self.instance)
        render(self.instance, m, [])
        root = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8').split('## root\n', 1)[1].split('\n## ', 1)[0]
        self.assertIn('proved L (established), proved R (open)', root)
        self.assertEqual(m['nodes']['root']['state'], 'unresolved')
        self.publish('r3', record([claim_row('right')], solutions=[solution('right', 'R', 'right')]))
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'informal_proved')

    def test_signed_cycle_exposes_contradiction_but_cannot_create_a_seed(self):
        data = self.reduction()
        data['claims'].append(claim_row('back'))
        data['relations'].append({'id': 'back', 'claim': 'back', 'premises': [{'node': 'root', 'outcome': 'proved'}],
                                  'conclusion': {'node': 'Q', 'outcome': 'refuted'}})
        self.publish('r1', data)
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'unresolved')
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        self.assertEqual(replay(self.instance)['nodes']['Q']['state'], 'contested')

    def test_modules_can_share_record_and_keep_description(self):
        self.publish('r1', record())
        data = {'batch': ['r1'], 'modules': [{'id': n, 'title': n, 'description': n, 'records': ['r1']} for n in ('a', 'b')],
                'shared_context': ['r1']}
        organization_check(data, replay(self.instance), ['r1'])
        self.event('o1', 'organization', data)
        m = replay(self.instance)
        render(self.instance, m, [])
        for name in ('a', 'b'):
            output = (self.instance / 'knowledge/index' / (name + '.md')).read_text(encoding='utf-8')
            self.assertIn('A precise contribution with its limitations.', output)
            self.assertIn('Supported within its scope.', output)

    def test_speculative_node_is_not_admitted(self):
        data = record([claim_row('hunch')], [{'id': 'Q', 'statement': 'Q', 'connection': 'hunch'}])
        folder = self.root / 'candidate'; folder.mkdir()
        (folder / 'record.md').write_text('A hunch.', encoding='utf-8')
        review = assessment(data)
        out = self.root / 'review'; out.mkdir(); (out / 'feedback.md').write_text('Review.', encoding='utf-8')
        with self.assertRaises(Invalid):
            assessment_check(review, out, data, folder, replay(self.instance), self.instance, 's1')


class RunnerTests(InstanceCase):
    def runner(self):
        return Runner(self.instance, self.skill)

    def test_invalid_processing_output_delays_only_its_job(self):
        runner = self.runner()
        key = runner.enqueue('organizer', {'batch': []})
        sid = 'sbadoutput'
        folder = runner.session_dir(sid)
        (folder / 'output').mkdir(parents=True)
        (folder / 'work').mkdir()
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid,
                                           'role': 'organizer', 'task': {'batch': []}})
        (folder / 'cli.stdout.jsonl').write_text(json.dumps(
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Organization attempted.'}}), encoding='utf-8')
        (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        session = {'id': sid, 'role': 'organizer', 'job': key, 'status': 'running',
                   'provider': 'codex', 'model': 'codex/gpt-6.1-sol', 'started_at': 900, 'exit_code': 0}
        runner.state['sessions'][sid] = session
        job = runner.state['jobs'][key]
        job.update(status='running', session=sid)
        runner.save()
        # The actual output checker rejects the missing organization.json.
        with patch('runner.time.time', return_value=1000):
            runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(job['not_before'], 1060)
        self.assertIn('organization.json', job['last_error'])
        self.assertEqual(runner.state['blocks'], {})
        self.assertEqual(runner.selection('attempt')['model'], 'codex/gpt-6.1-sol')
        self.assertEqual(job['task']['previous_partial_sessions'], [str(folder)])

    def test_successful_post_backoff_launch_resets_availability_history(self):
        runner = self.runner()
        sid, session, _ = self.ended(runner, 'attempt', exit_code=0)
        session['started_at'] = 1001
        for key in ('provider:codex', 'model:codex/gpt-6.1-sol'):
            runner.state['blocks'][key] = {'until': 1000, 'attempts': 5, 'source': 'backoff'}
        with patch('runner.time.time', return_value=1002):
            runner.finish(sid, session)
        self.assertEqual(runner.state['blocks'], {})
        self.assertEqual(self.runner().state['blocks'], {})

        later, limited, _ = self.ended(runner, 'explore', exit_code=0)
        limited['started_at'] = 2001
        (runner.session_dir(later) / 'cli.stdout.jsonl').write_text(json.dumps(
            {'type': 'error', 'message': "You've hit your usage limit. Try again later."}), encoding='utf-8')
        with patch('runner.time.time', return_value=2002):
            runner.finish(later, limited)
        block = runner.state['blocks']['provider:codex']
        self.assertEqual(block['attempts'], 1)
        self.assertEqual(block['until'], 2062)

    def test_old_inflight_success_does_not_erase_newer_availability_blocks(self):
        runner = self.runner()
        sid, session, _ = self.ended(runner, 'attempt', exit_code=0)
        session['started_at'] = 1000
        expected = {
            'provider:codex': {'until': 2000, 'attempts': 5, 'source': 'backoff'},
            'model:codex/gpt-6.1-sol': {'until': 4000, 'attempts': 2, 'source': 'backoff'},
        }
        runner.state['blocks'].update({key: dict(value) for key, value in expected.items()})
        with patch('runner.time.time', return_value=3000):
            runner.finish(sid, session)
        self.assertEqual(runner.state['blocks'], expected)

    def ended(self, runner, role, output=None, exit_code=42):
        key = runner.producer(role)
        job = runner.state['jobs'][key]
        sid = 's' + role
        folder = runner.session_dir(sid)
        (folder / 'output').mkdir(parents=True)
        (folder / 'work').mkdir()
        (folder / 'inbox').mkdir()
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role, 'task': {}})
        (folder / 'cli.stdout.jsonl').write_text(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'A retained observation.'}}), encoding='utf-8')
        (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        (folder / 'work/notes.md').write_text('An unfinished mathematical argument.', encoding='utf-8')
        session = {'id': sid, 'role': role, 'job': key, 'model': 'codex/gpt-6.1-sol', 'provider': 'codex',
                   'started_at': 1, 'status': 'running', 'exit_code': exit_code, 'host': None, 'cli': None}
        runner.state['sessions'][sid] = session
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        job.update(status='running', session=sid)
        runner.save()
        return sid, session, job

    def test_interrupted_work_without_output_manifest_reaches_peer(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        runner.finish(sid, session)
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(pipeline['stage'], 'peer')
        self.assertEqual(session['status'], 'ended')
        self.assertEqual(runner.state['jobs'][pipeline['id'] + ':peer']['task']['source'], str(runner.session_dir(sid)))

    def test_retention_file_error_retries_preservation_after_restart(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        with patch('runner.capture', side_effect=OSError('native transcript temporarily unreadable')):
            with self.assertRaisesRegex(OSError, 'temporarily unreadable'):
                runner.finish(sid, session)
        self.assertFalse(session.get('retained'))
        self.assertEqual(job['status'], 'running')
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        runner.save()
        recovered = self.runner()
        recovered.finish(sid, recovered.state['sessions'][sid])
        self.assertTrue(recovered.state['sessions'][sid]['retained'])
        self.assertTrue((runner.session_dir(sid) / 'retention.json').is_file())
        self.assertEqual(recovered.state['jobs'][job['pipeline'] + ':peer']['task']['source'],
                         str(runner.session_dir(sid)))

    def test_termination_file_error_does_not_persist_a_retained_marker(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        def fail_termination(path, value):
            if Path(path).name == 'termination.json':
                raise OSError('termination receipt temporarily unwritable')
            return write_json(path, value)
        with patch('runner.write_json', side_effect=fail_termination):
            with self.assertRaisesRegex(OSError, 'temporarily unwritable'):
                runner.finish(sid, session)
        self.assertFalse(session.get('retained'))
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        runner.save()
        recovered = self.runner()
        recovered.finish(sid, recovered.state['sessions'][sid])
        self.assertTrue(recovered.state['sessions'][sid]['retained'])
        self.assertEqual(read_json(runner.session_dir(sid) / 'termination.json')['exit_code'], 42)
        self.assertEqual(recovered.state['jobs'][job['pipeline'] + ':peer']['status'], 'pending')

    def test_native_only_research_reaches_peer(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'work/notes.md').unlink()
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        (folder / 'cli.stdout.jsonl').write_text(json.dumps({'type': 'thread.started', 'thread_id': identity}), encoding='utf-8')
        profile = self.root / 'native-profile'
        (profile / 'sessions').mkdir(parents=True)
        observation = 'A mathematical observation retained before interruption.'
        rows = [
            {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user', 'content': [{'type': 'input_text', 'text': 'Study the root.'}]}},
            {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': observation}]}},
        ]
        (profile / 'sessions' / (identity + '.jsonl')).write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
        with patch.dict('os.environ', {'CODEX_HOME': str(profile)}):
            runner.finish(sid, session)
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(pipeline['stage'], 'peer')
        self.assertEqual(job['status'], 'done')
        self.assertEqual(session['status'], 'ended')
        self.assertEqual(runner.state['jobs'][pipeline['id'] + ':peer']['task']['source'], str(folder))
        self.assertIn(observation, (folder / 'conversation.md').read_text(encoding='utf-8'))

    def test_native_prompt_without_research_remains_a_launch_retry(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'work/notes.md').unlink()
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        (folder / 'cli.stdout.jsonl').write_text(json.dumps({'type': 'thread.started', 'thread_id': identity}), encoding='utf-8')
        profile = self.root / 'native-profile'
        (profile / 'sessions').mkdir(parents=True)
        rows = [
            {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user', 'content': [{'type': 'input_text', 'text': 'Study the root.'}]}},
            {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [], 'encrypted_content': 'OPAQUE_TRANSPORT'}},
        ]
        (profile / 'sessions' / (identity + '.jsonl')).write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
        with patch.dict('os.environ', {'CODEX_HOME': str(profile)}):
            runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(session['status'], 'failed')
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        self.assertTrue(session['retention']['native_transcripts'])

    def test_archiver_keeps_producer_work_until_its_pipeline_is_done(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        runner.finish(sid, session)
        work = runner.session_dir(sid) / 'work'
        # The producer has ended, but its peer still has to read the retained work.
        archive_finished(self.instance)
        self.assertTrue((work / 'notes.md').is_file())
        runner.state['pipelines'][job['pipeline']]['stage'] = 'done'
        runner.save()
        archive_finished(self.instance)
        self.assertFalse(work.exists())
        self.assertTrue((runner.session_dir(sid) / 'work.tar.xz').is_file())

    def test_final_archive_request_is_dispatched_before_runner_exit(self):
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        self.publish('rfinal', data, assessment(data, ['p']))
        runner = self.runner()
        self.assertTrue(root_solved(runner.model))
        with patch('runner.subprocess.Popen') as launch:
            # An earlier archiver is still processing its older state snapshot
            # when the final publication requests another archive pass.
            runner.archiver = launch.return_value
            runner.archiver.poll.return_value = None
            runner.archive_due = True
            self.assertFalse(runner.tick())
            self.assertTrue(runner.state['finished'])
            self.assertTrue(runner.archive_due)
            launch.assert_not_called()

            runner.archiver.poll.return_value = 0
            self.assertTrue(runner.tick())
            self.assertFalse(runner.archive_due)
            launch.assert_called_once()
            self.assertEqual(launch.call_args.args[0][-2:],
                             ['_archive', str(self.instance)])

    def test_occupancy_survives_producer_exit(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        self.assertTrue(take(runner.session_dir(sid), 'root')['registered'])
        for stage in ('producing', 'peer'):
            if stage == 'peer':
                runner.finish(sid, session)
            rows = board(self.instance, runner.state)
            self.assertEqual(rows[0]['nodes'], ['root'])
            self.assertEqual(rows[0]['stage'], stage)
            render(self.instance, replay(self.instance), rows)
            visible = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
            self.assertIn(f'producer: {sid}', visible)
            self.assertIn(f'· {stage} · nodes: root', visible)

    def running_attempt(self, runner, sid):
        """A producing attempt whose session the board lists, as dispatch would leave it."""
        key = runner.producer('attempt')
        job = runner.state['jobs'][key]
        folder = runner.session_dir(sid)
        folder.mkdir(parents=True)
        (folder / 'inbox').mkdir()
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'attempt',
                                           'pipeline': job['pipeline'], 'task': {}})
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        runner.state['sessions'][sid] = {'id': sid, 'role': 'attempt', 'job': key, 'status': 'running'}
        job.update(status='running', session=sid)
        runner.save()
        return folder

    def test_lease_is_first_wins_and_a_refusal_records_nothing(self):
        self.publish('r1', self.reduction())  # Q stays available
        runner = self.runner()
        first, second = (self.running_attempt(runner, sid) for sid in ('sfirst', 'ssecond'))
        self.assertTrue(lease(first, 'root')['leased'])
        refused = lease(second, 'root')
        self.assertFalse(refused['leased'])
        self.assertEqual(refused['holders'], ['sfirst'])
        self.assertEqual(refused['queue'], [])
        self.assertEqual({n: [h['session'] for h in e['holders']] for n, e in lease_table(self.instance).items()},
                         {'root': ['sfirst']})
        self.assertFalse((second / 'declaration.json').exists())
        # Repeating one's own lease is accepted; the refused attempt can take another node.
        self.assertTrue(lease(first, 'root')['leased'])
        self.assertTrue(lease(second, 'Q')['leased'])

    def test_simultaneous_leases_from_separate_processes_admit_one_holder(self):
        runner = self.runner()
        folders = [self.running_attempt(runner, 's' + str(i)) for i in range(6)]
        runtime = str(Path(__file__).resolve().parents[1])
        start = time.time() + 3  # every process imports first, then asks at the same instant
        launcher = ('import sys, time; sys.path.insert(0, %r); import coordination; '
                    'time.sleep(max(0, %r - time.time())); '
                    'sys.argv = ["coordination.py", "lease", sys.argv[1], "root"]; '
                    'raise SystemExit(coordination.main())') % (runtime, start)
        processes = [subprocess.Popen([sys.executable, '-B', '-c', launcher, str(f)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for f in folders]
        results = []
        for process in processes:
            # communicate() reads and closes both pipes; a child that printed no answer shows its traceback.
            out, err = process.communicate(timeout=60)
            self.assertTrue(out.strip(), err.decode('utf-8', 'replace'))
            results.append((process.returncode, json.loads(out.decode('utf-8'))))
        self.assertEqual(sorted(code for code, _ in results), [0, 1, 1, 1, 1, 1], results)
        holders = lease_table(self.instance)['root']['holders']
        self.assertEqual(len(holders), 1)
        self.assertEqual([r['holders'] for code, r in results if code == 0], [[holders[0]['session']]])

    def test_waiters_are_served_in_order_and_registration_passes_the_lease(self):
        runner = self.runner()
        a, b, c = (self.running_attempt(runner, sid) for sid in ('sa', 'sb', 'sc'))
        self.assertTrue(lease(a, 'root')['leased'])
        self.assertEqual(wait(b, 'root', timeout=0)['position'], 1)
        self.assertEqual(wait(c, 'root', timeout=0)['position'], 2)
        first = take(a, 'root', 'For every n, b is nondecreasing for l < n - 2.', leased=True)
        self.assertTrue(first['registered'], first)
        sid_a = first['section']['id']
        self.assertEqual([h['session'] for h in lease_table(self.instance)['root']['holders']], ['sb'])
        self.assertTrue(wait(b, 'root', timeout=0)['leased'])
        # The tool refuses what it can decide; overlap itself is the registering session's reasoned judgement.
        self.assertIn('whole node cannot', take(b, 'root', leased=True)['reason'])
        self.assertIn('exact statement',
                      take(b, 'root', 'For every n,  b is nondecreasing for l < n - 2.', leased=True)['reason'])
        missing = take(b, 'root', 'For every n, the last three terms decrease.', leased=True)
        self.assertIn(sid_a, missing['reason'])
        self.assertFalse((b / 'declaration.json').exists())
        second = take(b, 'root', 'For every n, the last three terms decrease.',
                      {sid_a: 'Mine concerns l >= n - 3 only, where the other section does not apply.'}, leased=True)
        self.assertTrue(second['registered'], second)
        self.assertEqual([h['session'] for h in lease_table(self.instance)['root']['holders']], ['sc'])
        rows = {r['session']: [s['id'] for s in r['sections']] for r in board(self.instance)}
        self.assertEqual(rows, {'sa': [sid_a], 'sb': [second['section']['id']], 'sc': []})
        self.assertEqual(runner.available_nodes(), ['root'])

    def test_lease_of_an_ended_session_passes_to_the_next_waiter(self):
        runner = self.runner()
        a, b = (self.running_attempt(runner, sid) for sid in ('sa', 'sb'))
        self.assertTrue(lease(a, 'root')['leased'])
        self.assertFalse(wait(b, 'root', timeout=0)['leased'])
        runner.state['sessions']['sa']['status'] = 'ended'
        runner.save()
        self.assertTrue(wait(b, 'root', timeout=0)['leased'])
        # A running session whose host and CLI are both gone has ended as well.
        c = self.running_attempt(runner, 'sc')
        self.assertFalse(wait(c, 'root', timeout=0)['leased'])
        gone = {'pid': 2 ** 22, 'birth': 'gone'}
        runner.state['sessions']['sb'].update(host=gone, cli=gone)
        runner.save()
        self.assertTrue(wait(c, 'root', timeout=0)['leased'])

    def test_a_session_stands_in_one_lease_relation(self):
        self.publish('r1', self.reduction())
        runner = self.runner()
        holder, mover = (self.running_attempt(runner, sid) for sid in ('sholder', 'smover'))
        self.assertTrue(lease(holder, 'root')['leased'])
        self.assertFalse(wait(mover, 'root', timeout=0)['leased'])
        self.assertTrue(lease(mover, 'Q')['leased'])
        self.assertEqual(lease_table(self.instance)['root']['queue'], [])
        # Leaving without registering frees the lease for everyone.
        release(mover, 'Q')
        self.assertNotIn('Q', lease_table(self.instance))
        # A refused wait on a node held whole keeps the place already taken on another node.
        self.assertFalse(wait(mover, 'root', timeout=0)['leased'])
        blocked_by = self.running_attempt(runner, 'swhole')
        self.assertTrue(take(blocked_by, 'Q')['registered'])
        self.assertIn('whole node', wait(mover, 'Q', timeout=0)['reason'])
        self.assertEqual([w['session'] for w in lease_table(self.instance)['root']['queue']], ['smover'])
        self.assertIn('already holds', take(blocked_by, 'Q')['reason'])

    def test_whole_node_section_blocks_others_until_its_pipeline_is_done(self):
        runner = self.runner()
        a, b = (self.running_attempt(runner, sid) for sid in ('sa', 'sb'))
        self.assertTrue(take(a, 'root')['registered'])
        self.assertIn('whole node', lease(b, 'root')['reason'])
        self.assertEqual(runner.available_nodes(), [])
        pipeline = runner.state['jobs'][runner.state['sessions']['sa']['job']]['pipeline']
        runner.state['pipelines'][pipeline]['stage'] = 'done'
        runner.save()
        self.assertEqual(runner.available_nodes(), ['root'])
        self.assertTrue(lease(b, 'root')['leased'])

    def test_sections_expand_through_the_lease_and_are_not_released(self):
        runner = self.runner()
        a = self.running_attempt(runner, 'sa')
        self.assertTrue(take(a, 'root', 'For every n, the last three terms decrease.')['registered'])
        request = a / 'next.json'
        write_json(request, {'whole': False, 'statement': 'For every n >= 4, b_(n,n-4) > b_(n,n-3).', 'reasons': {}})
        self.assertIn('lease', section(a, 'root', request)['reason'])
        self.assertTrue(lease(a, 'root')['leased'])
        # Its own earlier section needs no non-overlap reason.
        self.assertTrue(section(a, 'root', request)['registered'])
        self.assertTrue(lease(a, 'root')['leased'])
        release(a, 'root')
        self.assertEqual([s['id'] for s in read_json(a / 'declaration.json')['sections']], ['sa-1', 'sa-2'])

    def test_peers_register_within_their_pipeline_and_other_roles_cannot(self):
        runner = self.runner()
        a = self.running_attempt(runner, 'sa')
        self.assertTrue(take(a, 'root', 'For every n, the last three terms decrease.')['registered'])
        job = runner.state['jobs'][runner.state['sessions']['sa']['job']]
        peer = runner.session_dir('speer')
        peer.mkdir()
        write_json(peer / 'input.json', {'instance': str(self.instance), 'session': 'speer', 'role': 'peer',
                                         'pipeline': job['pipeline'], 'task': {}})
        runner.state['pipelines'][job['pipeline']].update(peer='speer', stage='peer')
        runner.state['sessions']['speer'] = {'id': 'speer', 'role': 'peer', 'status': 'running', 'job': 'peerjob'}
        runner.save()
        # The source's sections belong to the same pipeline, so the peer may take the rest of the node.
        self.assertTrue(take(peer, 'root')['registered'])
        self.assertEqual([s['session'] for s in board(self.instance)[0]['sections']], ['sa', 'speer'])
        explorer = runner.session_dir('sexplore')
        explorer.mkdir()
        write_json(explorer / 'input.json', {'instance': str(self.instance), 'session': 'sexplore', 'role': 'explore'})
        with self.assertRaisesRegex(ValueError, 'only attempts and peers'):
            lease(explorer, 'root')

    def test_attempt_launches_are_spaced_and_a_queued_node_launches_none(self):
        self.publish('r1', self.reduction())  # root and Q are both available
        runner = self.runner()
        self.assertEqual(runner.settings['attempt_launch_interval'], 180)
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
            runner.schedule()
            self.assertEqual(len([s for _, s in runner.active() if s['role'] == 'attempt']), 1)
            # The spacing survives a restart.
            runner = self.runner()
            runner.schedule()
            self.assertEqual(len([s for _, s in runner.active() if s['role'] == 'attempt']), 1)
            runner.state['last_attempt_launch'] -= 181
            runner.schedule()
            attempts = [sid for sid, s in runner.active() if s['role'] == 'attempt']
            self.assertEqual(len(attempts), 2)
        first, second = (runner.session_dir(sid) for sid in attempts)
        self.assertTrue(lease(first, 'root')['leased'])
        self.assertCountEqual(runner.available_nodes(), ['root', 'Q'])
        self.assertFalse(wait(second, 'root', timeout=0)['leased'])
        self.assertEqual(runner.available_nodes(), ['Q'])

    def test_attempt_launch_interval_must_be_nonnegative_seconds(self):
        for bad in (-1, 1.5, '180'):
            config = defaults()
            config['attempt_launch_interval'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'attempt_launch_interval'):
                validate(config)

    def test_default_pool_and_provider_fallback(self):
        runner = self.runner()
        self.assertEqual(runner.settings['max_sessions'], 8)
        self.assertEqual(runner.selection('attempt')['model'], 'codex/gpt-6.1-sol')
        for role in ('peer', 'review'):
            self.assertEqual(runner.selection(role)['model'], 'claude/opus')
        runner.state['blocks']['provider:codex'] = {'until': 10**12}
        self.assertEqual(runner.selection('attempt')['model'], 'claude/opus')
        self.assertEqual(runner.selection('review')['model'], 'claude/opus')
        runner.state['blocks']['provider:claude'] = {'until': 10**12}
        self.assertIsNone(runner.selection('review'))
        del runner.state['blocks']['provider:codex']
        self.assertEqual(runner.selection('review')['model'], 'codex/gpt-6.1-sol')
        self.assertEqual(defaults()['roles']['peer'], defaults()['roles']['review'])

    def test_periodic_exploration_survives_restart_and_coalesces_requests(self):
        runner = self.runner()
        def start_research():
            key = runner.producer('attempt')
            self.assertTrue(runner.dispatch(key))
            sid = runner.state['jobs'][key]['session']
            write_json(runner.session_dir(sid) / 'declaration.json', {'sections': [
                {'id': sid + '-1', 'node': 'root', 'whole': True, 'statement': None,
                 'reasons': {}, 'at': 1}], 'at': 1})
            runner.observe_attempt_selections()
        self.assertEqual(runner.settings['explore_every'], 3)
        self.assertEqual(runner.state['attempt_research_starts'], 0)
        self.assertIs(runner.state['explore_requested'], False)
        with patch('runner.subprocess.Popen'), patch('runner.process_identity', return_value=None):
            for expected in (1, 2):
                start_research()
                self.assertEqual(runner.state['attempt_research_starts'], expected)
                self.assertIs(runner.state['explore_requested'], False)

            runner = self.runner()
            self.assertEqual(runner.state['attempt_research_starts'], 2)
            self.assertIs(runner.state['explore_requested'], False)
            for expected in (3, 4, 5, 6):
                start_research()
                self.assertEqual(runner.state['attempt_research_starts'], expected)
                self.assertIs(runner.state['explore_requested'], True)

            runner = self.runner()
            self.assertEqual(runner.state['attempt_research_starts'], 6)
            self.assertIs(runner.state['explore_requested'], True)
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            self.assertEqual(runner.state['attempt_research_starts'], 6)
            self.assertIs(runner.state['explore_requested'], False)
            start_research()
            self.assertEqual(runner.state['attempt_research_starts'], 7)
            self.assertIs(runner.state['explore_requested'], False)

    def test_retry_extends_short_blocks_and_preserves_long_blocks(self):
        for deadline, expected_until, expected_model in (
                (1020, 1060, 'codex/gpt-6.1-sol'),
                (1480, 1480, 'claude/opus')):
            with self.subTest(deadline=deadline):
                runner = self.runner()
                key = runner.enqueue('review', {'kind': 'comprehensive', 'concerns': []})
                session = {'id': 'spartial', 'model': 'codex/gpt-6.1-sol', 'provider': 'codex'}
                block_key = 'model:' + session['model']
                previous = {'until': deadline, 'reason': 'model_capacity', 'source': 'backoff'}
                runner.state['blocks'][block_key] = dict(previous)
                with patch('runner.time.time', return_value=1000):
                    runner.retry(runner.state['jobs'][key], session, 'operational launch failure')
                self.assertEqual(runner.state['blocks'][block_key]['until'], expected_until)
                self.assertEqual(runner.state['jobs'][key]['status'], 'pending')
                if deadline > 1060:
                    self.assertEqual(runner.state['blocks'][block_key], previous)
                with patch('runner.time.time', return_value=1061):
                    self.assertEqual(runner.selection('attempt')['model'], expected_model)

    def check_refusal_handoff(self, row, expected_key, expected_model, model='codex/gpt-6.1-sol',
                              peers=('codex/gpt-6.1-sol', 'codex/other', 'claude/opus')):
        runner = self.runner()
        runner.settings['roles']['peer'] = [{'model': name, 'effort': 'xhigh'} for name in peers]
        write_json(self.instance / 'settings.json', runner.settings)
        sid, session, job = self.ended(runner, 'attempt')
        # The refused session ran under this model; the row is its provider's refusal in the CLI stream.
        session.update(model=model, provider=model.split('/', 1)[0])
        folder = runner.session_dir(sid)
        with (folder / 'cli.stdout.jsonl').open('a', encoding='utf-8') as stream:
            stream.write('\n' + json.dumps(row) + '\n')
        with patch('runner.time.time', return_value=2000):
            runner.finish(sid, session)
            self.assertEqual(set(runner.state['blocks']), {expected_key})
            self.assertGreater(runner.state['blocks'][expected_key]['until'], 2000)
            self.assertEqual((session['status'], job['status']), ('ended', 'done'))
            self.assertEqual(job['retries'], 0)
            self.assertEqual(read_json(folder / 'termination.json')['cause'], 'refusal')
            self.assertTrue((folder / 'work/notes.md').is_file())
            pipeline = runner.state['pipelines'][job['pipeline']]
            self.assertEqual(pipeline['stage'], 'peer')
            peer = runner.state['jobs'][pipeline['id'] + ':peer']
            self.assertEqual(peer['task']['source'], str(folder))
            self.assertEqual(peer['status'], 'pending')
            self.assertEqual(runner.selection('peer')['model'], expected_model)
            recovered = self.runner()
            self.assertEqual(set(recovered.state['blocks']), {expected_key})
            self.assertEqual(recovered.selection('peer')['model'], expected_model)

    def test_provider_refusal_retains_work_and_falls_back_across_providers(self):
        self.check_refusal_handoff({'type': 'error', 'message': "You've hit your usage limit. Try again later."},
                                   'provider:codex', 'claude/opus')

    def test_model_refusal_retains_work_and_keeps_other_models_available(self):
        self.check_refusal_handoff({'type': 'error', 'message': 'Selected model is at capacity'},
                                   'model:codex/gpt-6.1-sol', 'codex/other')

    def test_claude_model_refusal_blocks_only_that_model_and_retains_work(self):
        # Claude's typed refusal for one model blocks that model, not the claude provider.
        self.check_refusal_handoff({'type': 'assistant', 'is_api_error_message': True,
                                    'api_error': 'model_requires_usage_credits'},
                                   'model:claude/opus', 'claude/sonnet', model='claude/opus',
                                   peers=('claude/opus', 'claude/sonnet', 'codex/gpt-6.1-sol'))

    def test_waiting_review_blocks_fresh_attempt_even_when_other_provider_free(self):
        runner = self.runner()
        runner.settings['roles']['review'] = [{'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'}]
        runner.state['blocks']['provider:codex'] = {'until': 10**12}
        runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        runner.schedule()
        self.assertFalse(any(p['role'] == 'attempt' for p in runner.state['pipelines'].values()))

    def test_waiting_organizer_does_not_block_attempt_while_another_organizer_runs(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 3
        first = runner.enqueue('organizer', {'batch': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(first))
            second = runner.enqueue('organizer', {'batch': []})
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            runner.schedule()
        self.assertEqual(runner.state['jobs'][first]['status'], 'running')
        self.assertEqual(runner.state['jobs'][second]['status'], 'pending')
        self.assertCountEqual([s['role'] for _, s in runner.active()],
                              ['organizer', 'explore', 'attempt'])

    def test_ready_jobs_dispatch_in_the_complete_role_priority_order(self):
        self.publish('r1', self.reduction())  # Q remains available for the attempt.
        self.publish('r2', record([claim_row('p')],
                                 solutions=[solution('p', 'root', 'p')]))
        runner = self.runner()
        runner.settings['max_sessions'] = 1
        # Reverse insertion order makes dictionary order an incorrect scheduler.
        runner.producer('attempt')
        runner.producer('explore')
        runner.enqueue('organizer', {'batch': ['r1', 'r2']})
        runner.producer('formalizer', {'node': 'root', 'proofs': ['r2/p'],
                                      'previous_records': []})
        runner.enqueue('peer', {'source': str(self.instance / 'sessions/source'),
                                'source_role': 'attempt'})
        runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [],
                                  'conflicts': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            for expected in ('review', 'peer', 'formalizer', 'organizer',
                             'explore', 'attempt'):
                with self.subTest(role=expected):
                    runner.dispatch_pending()
                    active = runner.active()
                    self.assertEqual([s['role'] for _, s in active], [expected])
                    sid, session = active[0]
                    self.assertEqual(read_json(runner.session_dir(sid) / 'input.json')['role'],
                                     expected)
                    count = len(runner.state['sessions'])
                    runner.dispatch_pending()
                    self.assertEqual(len(runner.state['sessions']), count)
                    # Release this test slot; lifecycle handoffs have their own tests.
                    job = runner.state['jobs'][session['job']]
                    session['status'] = 'integrated'
                    job['status'] = 'done'
                    if job['pipeline']:
                        runner.state['pipelines'][job['pipeline']]['stage'] = 'done'
                    runner.save()
        self.assertEqual(len(runner.state['sessions']), 6)
        self.assertTrue(all(j['status'] == 'done' for j in runner.state['jobs'].values()))
        self.assertFalse(runner.state['explore_requested'])

    def test_eligible_exploration_precedes_a_pending_attempt_retry(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 1
        sid, session, job = self.ended(runner, 'attempt')
        runner.retry(job, session, 'launch ended without research')
        job['not_before'] = 0
        runner.state['explore_requested'] = True
        self.assertIsNotNone(runner.selection('attempt'))
        self.assertIsNotNone(runner.selection('explore'))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual([s['role'] for _, s in runner.active()], ['explore'])
        self.assertEqual(job['status'], 'pending')
        self.assertFalse(runner.state['explore_requested'])
        self.assertEqual(sum(p['role'] == 'explore' and p['stage'] != 'done'
                             for p in runner.state['pipelines'].values()), 1)

    def test_exploration_still_in_peer_does_not_hold_a_pending_attempt(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 1
        previous = runner.producer('explore')
        runner.state['jobs'][previous]['status'] = 'done'
        pipeline = runner.state['pipelines'][runner.state['jobs'][previous]['pipeline']]
        pipeline.update(stage='peer', producer='sprevious')
        attempt = runner.producer('attempt')
        runner.state['explore_requested'] = True
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual([s['role'] for _, s in runner.active()], ['attempt'])
        self.assertEqual(runner.state['jobs'][attempt]['status'], 'running')
        self.assertEqual(pipeline['stage'], 'peer')
        self.assertTrue(runner.state['explore_requested'])
        self.assertEqual(sum(p['role'] == 'explore' and p['stage'] != 'done'
                             for p in runner.state['pipelines'].values()), 1)

    def test_attempt_retry_respects_lease_queue_and_whole_node_occupancy(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 3
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'work/notes.md').unlink()
        (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        job['not_before'] = 0
        runner.state['blocks'].clear()
        holder = self.running_attempt(runner, 'sholder')
        waiter = self.running_attempt(runner, 'swaiter')
        self.assertTrue(lease(holder, 'root')['leased'])
        self.assertTrue(wait(waiter, 'root', timeout=0)['waiting'])
        exploration = runner.producer('explore')
        runner.state['jobs'][exploration]['status'] = 'done'
        pipeline = runner.state['pipelines'][runner.state['jobs'][exploration]['pipeline']]
        pipeline.update(stage='peer', producer='sprevious')
        runner.save()
        self.assertEqual(runner.model['nodes']['root']['state'], 'unresolved')
        self.assertLess(len(runner.active()), runner.settings['max_sessions'])
        self.assertTrue(runner.attempt_launch_due())
        self.assertIsNotNone(runner.selection('attempt'))
        before = set(runner.state['sessions'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertEqual(runner.available_nodes(), [])
            runner.dispatch_pending()
            self.assertEqual(job['status'], 'pending')
            self.assertEqual(set(runner.state['sessions']), before)
            release(waiter, 'root')
            self.assertTrue(take(holder, 'root', leased=True)['registered'])
            holder_job = runner.state['sessions']['sholder']['job']
            holder_pipeline = runner.state['pipelines'][runner.state['jobs'][holder_job]['pipeline']]
            holder_pipeline['stage'] = 'peer'
            runner.save()
            self.assertEqual(runner.available_nodes(), [])
            runner.dispatch_pending()
            self.assertEqual(job['status'], 'pending')
            self.assertEqual(set(runner.state['sessions']), before)
            holder_pipeline['stage'] = 'done'
            runner.save()
            self.assertEqual(runner.available_nodes(), ['root'])
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        self.assertEqual(set(runner.state['sessions']) - before, {job['session']})

    def test_attempt_retry_waits_when_all_nodes_are_informally_solved(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 2
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'work/notes.md').unlink()
        (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        job['not_before'] = 0
        runner.state['blocks'].clear()
        self.publish('rsolved', record([claim_row('p')],
                                      solutions=[solution('p', 'root', 'p')]))
        runner.model = replay(self.instance)
        self.assertEqual(runner.model['nodes']['root']['state'], 'informal_proved')
        self.assertFalse(runner.state['complete'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            before = set(runner.state['sessions'])
            runner.dispatch_pending()
        self.assertEqual(set(runner.state['sessions']), before)
        self.assertEqual(job['status'], 'pending')
        self.assertEqual([s['role'] for _, s in runner.active()], ['explore'])

    def test_spare_capacity_explores_when_every_node_is_informally_solved(self):
        # Spare capacity requests exploration whether nodes are occupied or none remain unresolved.
        self.publish('rsolved', record([claim_row('p')],
                                      solutions=[solution('p', 'root', 'p')]))
        runner = self.runner()
        runner.settings['max_sessions'] = 2
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertCountEqual([s['role'] for _, s in runner.active()], ['formalizer', 'explore'])
        self.assertFalse(any(p['role'] == 'attempt' for p in runner.state['pipelines'].values()))
        self.assertFalse(runner.state['explore_requested'])

    def test_organizer_batch_excludes_arrivals_during_processing(self):
        for i in range(3): self.publish('r' + str(i), record())
        runner = self.runner(); runner.populate()
        # The settled default waits for the fourth new research record.
        self.assertFalse(any(j['role'] == 'organizer' for j in runner.state['jobs'].values()))
        self.publish('r3', record())
        runner.model = replay(self.instance); runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'organizer')
        runner.session_dir('sorganizer').mkdir()
        runner.make_pack('sorganizer', job)
        self.assertEqual(len(job['task']['batch']), 4)
        for i in range(4, 6): self.publish('r' + str(i), record())
        self.event('o1', 'organization', {'batch': job['task']['batch'], 'modules': [], 'shared_context': []})
        m = replay(self.instance)
        self.assertEqual(set(m['records']) - set(m['organized']), {'r4', 'r5'})

    def test_organizer_freezes_arrivals_at_launch_not_queue_time(self):
        for i in range(4): self.publish('r' + str(i), record())
        runner = self.runner(); runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'organizer')
        self.publish('r4', record())
        runner.model = replay(self.instance)
        runner.session_dir('sorganizer').mkdir()
        runner.make_pack('sorganizer', job)
        self.assertEqual(job['task']['batch'], ['r0', 'r1', 'r2', 'r3', 'r4'])
        self.publish('r5', record())
        runner.model = replay(self.instance)
        runner.session_dir('sretry').mkdir()
        runner.make_pack('sretry', job)
        self.assertEqual(job['task']['batch'], ['r0', 'r1', 'r2', 'r3', 'r4'])

    def test_formalizer_is_sent_only_for_outcomes_that_reach_the_root(self):
        self.publish('r1', record([claim_row('necessary')], [{'id': 'K', 'statement': 'K', 'connection': 'necessary'}],
                                 [implication('necessary', 'root', 'K')]))
        self.publish('r2', record([claim_row('k')], solutions=[solution('k', 'K', 'k')]))
        runner = self.runner()
        self.assertEqual(runner.model['nodes']['K']['state'], 'informal_proved')
        runner.populate()
        self.assertFalse(any(p['role'] == 'formalizer' for p in runner.state['pipelines'].values()))
        # A formalizer job enqueued for such an outcome is cancelled at dispatch.
        key = runner.producer('formalizer', {'node': 'K', 'proofs': ['r2/k'], 'previous_records': []})
        with patch('runner.subprocess.Popen'):
            runner.dispatch_pending()
        self.assertEqual(runner.state['jobs'][key]['status'], 'cancelled')
        # The same node refuted reaches the root, so its refutation is formalized.
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed', 'reason': 'Wrong object.',
                                                'invalidates': [{'record': 'r2', 'claim': 'k'}]}]})
        self.publish('r3', record([claim_row('notk')], solutions=[solution('notk', 'K', 'notk', 'refuted')]))
        runner.model = replay(self.instance)
        self.assertEqual(runner.model['nodes']['root']['state'], 'informal_refuted')
        runner.populate()
        nodes = sorted(p['node'] for p in runner.state['pipelines'].values() if p['role'] == 'formalizer' and p['stage'] != 'done')
        self.assertEqual(nodes, ['K'])  # root's own refutation waits for K's formal refutation

    def test_sufficient_premise_proved_is_formalized_and_an_inconsistent_set_sends_nothing(self):
        self.publish('r1', self.reduction())  # Q implies root
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        runner = self.runner()
        runner.populate()
        nodes = sorted(p['node'] for p in runner.state['pipelines'].values() if p['role'] == 'formalizer' and p['stage'] != 'done')
        self.assertEqual(nodes, ['Q'])  # root proved through Q waits for Q's formal proof
        # Accepting root implies K and a refutation of K now makes the accepted set inconsistent:
        # root, Q and K are each derivable both ways, so all three are contested and nothing new is sent.
        self.publish('r3', record([claim_row('necessary')], [{'id': 'K', 'statement': 'K', 'connection': 'necessary'}],
                                 [implication('necessary', 'root', 'K')]))
        self.publish('r4', record([claim_row('notk')], solutions=[solution('notk', 'K', 'notk', 'refuted')]))
        runner.model = replay(self.instance)
        self.assertEqual({n: runner.model['nodes'][n]['state'] for n in ('root', 'Q', 'K')},
                         {'root': 'contested', 'Q': 'contested', 'K': 'contested'})
        runner.populate()
        nodes = sorted(p['node'] for p in runner.state['pipelines'].values() if p['role'] == 'formalizer' and p['stage'] != 'done')
        self.assertEqual(nodes, ['Q'])
        self.assertTrue(any(j['task'].get('kind') == 'comprehensive' and j['task']['conflicts'] for j in runner.state['jobs'].values()))

    def test_peer_task_carries_the_producers_sections(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        taken = take(runner.session_dir(sid), 'root', 'For every n, the last three terms decrease.')
        self.assertTrue(taken['registered'])
        runner.finish(sid, session)
        peer = runner.state['jobs'][job['pipeline'] + ':peer']
        self.assertEqual(peer['task']['sections'], [{'id': taken['section']['id'], 'node': 'root', 'whole': False,
                                                     'statement': 'For every n, the last three terms decrease.'}])

    def test_formalization_has_no_round_cap(self):
        self.publish('r1', record([claim_row('p')], solutions=[solution('p', 'root', 'p')]))
        runner = self.runner()
        for i in range(30):
            runner.state['pipelines']['old' + str(i)] = {'id': 'old' + str(i), 'role': 'formalizer', 'stage': 'done', 'node': 'root', 'record': 'r1'}
        runner.populate()
        self.assertTrue(any(p['role'] == 'formalizer' and p['stage'] == 'producing' for p in runner.state['pipelines'].values()))

    def test_standalone_processing_retry_receives_its_partial_work(self):
        runner = self.runner()
        for role, task in [('organizer', {'batch': []}), ('review', {'kind': 'comprehensive', 'concerns': []})]:
            with self.subTest(role=role):
                key = runner.enqueue(role, task)
                session = {'id': 's' + role, 'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'status': 'running'}
                runner.retry(runner.state['jobs'][key], session, 'incomplete output', availability=False)
                self.assertEqual(runner.state['jobs'][key]['task']['previous_partial_sessions'],
                                 [str(runner.session_dir('s' + role))])
                self.assertEqual(runner.state['jobs'][key]['status'], 'pending')

    def test_published_comprehensive_review_is_not_reassigned_for_its_open_concern(self):
        self.publish('r1', record([claim_row('p')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'gap',
            'targets': [{'record': 'r1', 'claim': 'p'}], 'reason': 'A boundary case needs checking.',
            'evidence': 'The case n = 0.'}]})
        runner = self.runner()
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['task'].get('kind') == 'comprehensive')
        self.assertEqual(job['task']['concerns'], ['v1/gap'])
        sid = 'scomprehensive'
        output = runner.session_dir(sid) / 'output'
        output.mkdir(parents=True)
        # The review could not settle the concern, so the concern itself stays open.
        write_json(output / 'assessment.json', {'feedback': 'feedback.md', 'index_assessment': 'Still undetermined.',
                                                'findings': [], 'concerns': []})
        (output / 'feedback.md').write_text('The boundary case remains undetermined.', encoding='utf-8')
        runner.state['sessions'][sid] = {'id': sid, 'role': 'review', 'status': 'running', 'job': job['id']}
        job.update(status='running', session=sid)
        runner.prepare_publication(sid, job, 'review')
        runner.publish()
        runner.populate()
        self.assertEqual([j['id'] for j in runner.state['jobs'].values()
                          if j['task'].get('kind') == 'comprehensive'], [job['id']])

    def test_operator_review_and_organize_requests_become_assignments(self):
        self.publish('r1', record([claim_row('p')], solutions=[solution('s', 'root', 'p')]))
        with patch('builtins.print'):
            self.assertEqual(main(['review', str(self.instance), '--record', 'missing']), 1)
            self.assertEqual(main(['review', str(self.instance), '--reason', 'Look again.']), 1)
            self.assertEqual(main(['review', str(self.instance), '--record', 'r1', '--node', 'root',
                                   '--reason', 'Check the base case.']), 0)
            self.assertEqual(main(['organize', str(self.instance)]), 0)
        runner = self.runner()
        runner.ingest_inputs()
        runner.ingest_inputs()
        reviews = [j['task'] for j in runner.state['jobs'].values() if j['role'] == 'review']
        self.assertEqual([(t['kind'], t['requested_records'], t['requested_nodes'], t['purpose']) for t in reviews],
                         [('comprehensive', ['r1'], ['root'], 'Check the base case.')])
        organizers = [j for j in runner.state['jobs'].values() if j['role'] == 'organizer'
                      and j['id'].startswith('operator:')]
        self.assertEqual([j['status'] for j in organizers], ['pending'])

    def test_root_change_requires_new_instance(self):
        (self.instance / 'root.md').write_text('A different proposition.', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'new instance'):
            self.runner()

    def test_rejected_settings_edit_keeps_the_last_valid_settings(self):
        runner = self.runner()
        runner.reload_settings()
        (self.instance / 'settings.json').write_text('{not json', encoding='utf-8')
        runner.reload_settings()
        self.assertEqual(runner.settings['max_sessions'], 8)
        self.assertIn('error', runner.state['settings_error'])
        config = defaults(); config['max_sessions'] = 3
        write_json(self.instance / 'settings.json', config)
        runner.reload_settings()
        self.assertEqual(runner.settings['max_sessions'], 3)
        self.assertIsNone(runner.state['settings_error'])

    def test_sorry_axiom_cannot_be_enabled(self):
        config = defaults(); config['lean']['allowed_axioms'].append('sorryAx')
        with self.assertRaises(ValueError): validate(config)

    def test_legacy_or_misspelled_settings_are_rejected(self):
        legacy = {**defaults(), 'limit_wait_seconds': 5}
        misspelled = defaults(); misspelled['lean']['memory_budget'] = 4096
        executable = defaults(); executable['cli']['Codex'] = 'C:/tools/codex.exe'
        for name, config in (('legacy', legacy), ('misspelled', misspelled), ('executable', executable)):
            with self.subTest(name), self.assertRaisesRegex(ValueError, 'unknown setting'):
                validate(config)

    def test_malformed_setting_structure_is_rejected_by_name(self):
        cli_path = defaults(); cli_path['cli']['codex'] = 5
        lean_cwd = defaults(); lean_cwd['lean']['cwd'] = 5
        cases = (('cli must be an object', {**defaults(), 'cli': 'C:/tools/codex.exe'}),
                 ('lean must be an object', {**defaults(), 'lean': []}),
                 ('model entries need exactly', {**defaults(), 'models': ['codex/gpt-6.1-sol']}),
                 ('fallback', {**defaults(), 'models': [{'model': 'claude/opus', 'effort': 'xhigh', 'fallback': True}]}),
                 ('cli.codex must be', cli_path),
                 ('lean.cwd must be', lean_cwd))
        for pattern, config in cases:
            with self.subTest(pattern), self.assertRaisesRegex(ValueError, pattern):
                validate(config)

    def test_board_can_show_a_producer_waiting_for_its_first_model(self):
        runner = self.runner()
        runner.producer('attempt')
        rows = board(self.instance, runner.state)
        self.assertEqual(rows[0]['stage'], 'queued')
        self.assertIsNone(rows[0]['session'])
        self.assertEqual(runner.available_nodes(), ['root'])
        runner.producer('explore')
        render(self.instance, replay(self.instance), board(self.instance, runner.state))
        visible = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
        self.assertIn('producer: (not launched)', visible)
        # Only the attempt can still choose a node; an exploration occupies none.
        self.assertIn('· attempt · queued · nodes: (choosing)', visible)
        self.assertIn('· explore · queued · nodes: (none)', visible)


if __name__ == '__main__':
    unittest.main()
