"""Standing and the frontier, occupancy of elements, and the runner's scheduling and recovery.

The canon of every test is built through the real candidate, build and publication path of
tests/support.py; a test that only needs a research state starts from one of its scenarios.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from availability import availability_view
from canon import Canon
from coordination import (board, claims_lock, lease, lease_table, main as coordination_main, message, release,
                          section, updates, wait)
from knowledge import STANDINGS, canonical_question, formalizable, render, replay, rests_on, root_settlement, root_solved
from lean_broker import Paths, broker_status, ensure_broker
from runner import Runner, archive_finished, initialize, main, start, status
from runtime_support import InstanceLock, alive, git, read_json, remove_tree, terminate_process, write_json
from settings import defaults, validate
from support import (GAP_REASON, HELD_REASON, RECORDS, ROOT, ROOT_STATEMENTS, SUM_SUCC, SUM_ZERO, RefutedRootCase,
                     ScenarioCase, comprehensive, finding, fixture_settings, module_text, record_text, session_record,
                     stop_broker, take, theorem, write_canon)


def concern(cid, *targets):
    return {'id': cid, 'targets': list(targets), 'reason': 'A boundary case needs checking.', 'evidence': 'The case n = 0.'}


def frontier_view(instance):
    """The frontier part of frontier.md, without the questions that follow it."""
    return (Path(instance) / 'knowledge/frontier.md').read_text(encoding='utf-8').split('# Questions')[0]


def publish_second_proof(case):
    """Publish Small.rootAlt, another proof of the root's statement, with a written proof that review accepts."""
    folder = case.candidate(
        modules={'Small/Second.lean': module_text(theorem('rootAlt', ROOT_STATEMENTS[case.root_variant]))},
        records={'Small/rootAlt.md': record_text('The root by another argument.', weight='unit',
                                                 proof='Count an n by n square in L-shaped layers.',
                                                 proves='Small.root')})
    case.publish(folder)


def second_proof(case):
    """The root has no proof of its own; Small.rootAlt, another proof of its statement, is accepted."""
    case.scenario('second', lambda: publish_second_proof(case))


def initialized(base, name, root=ROOT, modules=None, records=None, declaration='Small.root'):
    """An instance created through runner.initialize, as the operator creates one: the fixture's canon with
    the given text of the root module, and further modules and records (which replace the fixture's own).
    `declaration` is the name given to init as the root declaration."""
    base = Path(base)
    canon = base / (name + '-canon')
    write_canon(canon, root)
    for relative, text in [('lean/' + k, v) for k, v in (modules or {}).items()] + \
                          [('records/' + k, v) for k, v in (records or {}).items()]:
        path = canon / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
    (base / 'goal.md').write_text('For every natural number n, the sum of the first n odd numbers is n * n.',
                                  encoding='utf-8')
    write_json(base / 'settings.json', fixture_settings())
    initialize(base / name, base / 'goal.md', canon, declaration, base / 'settings.json')
    return base / name


def comprehensive_jobs(runner):
    return [j for j in runner.state['jobs'].values() if j['role'] == 'review' and j['task']['kind'] == 'comprehensive']


def publish_comprehensive(runner, job, data):
    """Publish a comprehensive review's assessment as the runner does when its session ends."""
    sid = 'scomprehensive'
    output = runner.session_dir(sid) / 'output'
    output.mkdir(parents=True)
    write_json(output / 'assessment.json', data)
    (output / 'feedback.md').write_text('What the tracing found.', encoding='utf-8')
    runner.state['sessions'][sid] = session_record(sid, 'review', job['id'])
    job.update(status='running', session=sid)
    runner.prepare_publication(sid, job, 'review')
    runner.publish()


class KnowledgeTests(ScenarioCase):
    def elements(self):
        return replay(self.instance)['elements']

    def test_the_four_states_follow_the_proof_and_the_verdict_review_gave_it(self):
        self.assertEqual(STANDINGS, {'no_proof': 'no proof', 'not_confirmed': 'proof not confirmed',
                                     'held': 'correct, held back', 'accepted': 'accepted'})
        written = ('caseGap', 'caseOpen', 'caseHeld', 'caseDone')
        folder = self.candidate(
            modules={'Small/Cases.lean': module_text('\n\n'.join([
                theorem('caseNone', ': oddSum 1 = 1'), theorem('caseGap', ': oddSum 2 = 4'),
                theorem('caseOpen', ': oddSum 3 = 9'), theorem('caseHeld', ': oddSum 4 = 16'),
                theorem('caseDone', ': oddSum 5 = 25'), theorem('caseLean', SUM_ZERO, proof='rfl')]))},
            records={'Small/caseNone.md': record_text('A statement left open.'),
                     **{f'Small/{name}.md': record_text('A statement with a written proof.', proof='Add the terms.')
                        for name in written},
                     'Small/caseLean.md': record_text('A statement proved in Lean alone.')})
        change, _ = self.publish(folder, self.verdicts(folder, **{
            'Small.caseGap': {'correct': 'not_confirmed', 'accepted': False, 'reason': GAP_REASON},
            'Small.caseOpen': {'correct': 'undetermined', 'accepted': False, 'reason': 'The source could not be read in full.'},
            'Small.caseHeld': {'accepted': False, 'reason': HELD_REASON}}))
        elements = self.elements()
        self.assertEqual({name.removeprefix('Small.'): element['standing'] for name, element in elements.items()},
                         {'oddSum': None, 'root': 'no_proof', 'caseNone': 'no_proof', 'caseGap': 'not_confirmed',
                          'caseOpen': 'not_confirmed', 'caseHeld': 'held', 'caseDone': 'accepted', 'caseLean': 'accepted'})
        # A proof is a complete Lean proof or a written one; the record of caseLean has no written proof.
        self.assertEqual((elements['Small.caseLean']['lean_proof'], elements['Small.caseLean']['written_proof']),
                         ('complete', False))
        self.assertEqual((elements['Small.caseDone']['lean_proof'], elements['Small.caseDone']['written_proof']),
                         ('sorry', True))
        # The verdict stands with the element it judged, with review's reason and the change that carried it.
        held = elements['Small.caseHeld']['verdict']
        self.assertEqual((held['correct'], held['accepted'], held['reason'], held['change']),
                         ('confirmed', False, HELD_REASON, change))
        # A definition has none of the four states and is neither a proof nor settled.
        definition = elements['Small.oddSum']
        self.assertEqual((definition['kind'], definition['proofs'], definition['settled'], definition['statement_of']),
                         ('def', [], False, None))

    def test_a_verdict_belongs_to_the_proof_it_judged(self):
        # The root's accepted proof names statements without a proof, so the root is not settled, and review may
        # put in its place a proof that it holds back (check.assessment_check).
        self.split()
        first = self.elements()['Small.root']['verdict']['change']
        source = Canon(self.instance).lean / 'Small/Root.lean'
        original = source.read_bytes()

        def offer(proof, **verdict):
            folder = self.candidate(replace={'Small.root': self.root_text(proof=proof)},
                                    records={'Small/root.md': self.root_record('By cases on $n$.')})
            return self.publish(folder, self.verdicts(folder, **{'Small.root': verdict}))[0]

        def unjudged(change):
            """The change with the verdicts taken out of its published assessment, where the replay reads them.

            The transport check passes no assessment that leaves a proof of the candidate unjudged, so the
            change is published with a verdict and the file is changed afterwards."""
            path = self.instance / 'knowledge/changes' / change / 'assessment.json'
            write_json(path, {**read_json(path), 'elements': []})
            return change

        # Review declined the replacement: the canon keeps its proof, and that proof keeps its verdict.
        offer('cases n <;> sorry', correct='not_confirmed', accepted=False, replaces=False,
              reason='No better than the proof the canon has.')
        root = self.elements()['Small.root']
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual((root['standing'], root['verdict']['change']), ('accepted', first))
        # A proof that takes the place of the old one stands under review's judgment of it.
        second = offer('cases n <;> sorry', accepted=False, reason=HELD_REASON)
        root = self.elements()['Small.root']
        self.assertNotEqual(source.read_bytes(), original)
        self.assertEqual((root['standing'], root['verdict']['change'], root['verdict']['reason']),
                         ('held', second, HELD_REASON))
        # A later proof that the review of its change did not judge does not inherit the judgment of the proof
        # it replaced, and it is not confirmed either.
        third = unjudged(offer('induction n <;> sorry'))
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['verdict']['correct'], root['verdict']['accepted'], root['verdict']['change']),
                         ('undetermined', False, third))
        self.assertEqual((root['standing'], root['settled'], model['root_state']), ('not_confirmed', False, 'unresolved'))
        # The same holds for a proof that is complete in Lean. Lean's check stands where review's judgment would
        # only for the elements an instance began with: a proof that a reviewed change brought without a verdict
        # has had no reading of its statement against what was meant, so it settles nothing.
        folder = self.candidate(replace={'Small.root': self.root_formal()})
        # The verdict is taken out below, so the review gives none that confirms the proof: confirming a proof
        # that is complete in Lean would have it compile the candidate first (InstanceCase.publish).
        undetermined = {'Small.root': {'correct': 'undetermined', 'accepted': False}}
        unjudged(self.publish(folder, self.verdicts(folder, **undetermined))[0])
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['lean_proof'], root['verdict']['correct'], root['standing'], root['settled'],
                          model['root_state']), ('complete', 'undetermined', 'not_confirmed', False, 'unresolved'))

    def test_settled_is_a_least_fixed_point_and_a_held_proof_settles_nothing_that_uses_it(self):
        folder = self.candidate(
            modules={'Small/Chain.lean': module_text('\n\n'.join([
                theorem('chainB', ': oddSum 2 = 4'), theorem('chainA', ': oddSum 1 = 1', uses=['chainB']),
                theorem('heldQ', ': oddSum 3 = 9')]))},
            replace={'Small.root': self.root_text(uses=['chainA', 'heldQ'])}, imports={'Small.root': ['Small.Chain']},
            records={'Small/chainB.md': record_text('Two terms.'),
                     'Small/chainA.md': record_text('One term, through two.', proof='Remove the second term.'),
                     'Small/heldQ.md': record_text('Three terms.', proof='Add the terms one at a time.'),
                     'Small/root.md': self.root_record()})
        self.publish(folder, self.verdicts(folder, **{'Small.heldQ': {'accepted': False, 'reason': HELD_REASON}}))
        model = replay(self.instance)
        elements = model['elements']
        # Accepted proofs above a statement without a proof are not settled, and neither is what a held proof carries.
        self.assertEqual({n: elements['Small.' + n]['standing'] for n in ('root', 'chainA', 'chainB', 'heldQ')},
                         {'root': 'accepted', 'chainA': 'accepted', 'chainB': 'no_proof', 'heldQ': 'held'})
        self.assertFalse(any(elements[name]['settled'] for name in elements))
        self.assertEqual(model['root_state'], 'unresolved')
        # The held proof is used all the same: the root's proof names it, and Lean compiled that.
        self.assertEqual(elements['Small.root']['uses'], ['Small.chainA', 'Small.heldQ'])
        self.assertEqual(elements['Small.heldQ']['used_by'], ['Small.root'])

        self.replace_proof('Small.chainB', theorem('chainB', ': oddSum 2 = 4', proof='unfold oddSum\n  sorry'),
                           'Unfold the definition twice.', weight='step')
        model = replay(self.instance)
        elements = model['elements']
        # A definition the proof uses has no standing and does not enter the computation.
        self.assertIn('Small.oddSum', elements['Small.chainB']['uses'])
        self.assertIsNone(elements['Small.oddSum']['standing'])
        self.assertEqual({n: elements['Small.' + n]['settled'] for n in ('root', 'chainA', 'chainB', 'heldQ')},
                         {'root': False, 'chainA': True, 'chainB': True, 'heldQ': False})
        self.assertEqual(model['root_state'], 'unresolved')

        self.replace_proof('Small.heldQ', theorem('heldQ', ': oddSum 3 = 9'), 'Add the three terms at once.', weight='step')
        model = replay(self.instance)
        self.assertTrue(all(model['elements']['Small.' + n]['settled'] for n in ('root', 'chainA', 'chainB', 'heldQ')))
        self.assertEqual(model['root_state'], 'informal_proved')

    def test_a_statement_is_settled_through_any_one_of_its_proofs_and_findings_withdraw_and_restore(self):
        second_proof(self)
        model = replay(self.instance)
        root, other = model['elements']['Small.root'], model['elements']['Small.rootAlt']
        # Which declarations prove one statement is declared in the record and confirmed by Lean.
        self.assertTrue(model['pairs']['same|Small.rootAlt|Small.root'])
        self.assertEqual((root['proofs'], other['statement_of'], other['proves']),
                         (['Small.root', 'Small.rootAlt'], 'Small.root', 'Small.root'))
        # Each proof keeps its own state; the statement is settled as soon as one of them is.
        self.assertEqual((root['standing'], root['settled'], other['standing'], other['settled']),
                         ('no_proof', False, 'accepted', True))
        self.assertTrue(root['statement_settled'])
        self.assertEqual(model['root_state'], 'informal_proved')

        withdrawal = finding('The layers are counted twice.', invalidates=['Small.rootAlt'])
        self.event('v1', 'review', comprehensive([withdrawal]))
        model = replay(self.instance)
        other = model['elements']['Small.rootAlt']
        self.assertEqual((other['standing'], other['verdict']['later_review'], other['verdict']['reason']),
                         ('not_confirmed', 'v1', 'The layers are counted twice.'))
        self.assertEqual(model['root_state'], 'unresolved')
        self.event('v2', 'review', comprehensive([finding('Each layer is counted once after all.', status='cleared',
                                                          validates=['Small.rootAlt'])]))
        model = replay(self.instance)
        self.assertEqual((model['elements']['Small.rootAlt']['standing'], model['root_state']), ('accepted', 'informal_proved'))

        # With a second accepted proof, the statement survives the withdrawal of either and not of both.
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.')
        self.event('v3', 'review', comprehensive([withdrawal]))
        model = replay(self.instance)
        self.assertEqual({n: model['elements'][n]['standing'] for n in ('Small.root', 'Small.rootAlt')},
                         {'Small.root': 'accepted', 'Small.rootAlt': 'not_confirmed'})
        self.assertEqual(model['root_state'], 'informal_proved')
        self.event('v4', 'review', comprehensive([finding('The induction step fails.', invalidates=['Small.root'])]))
        self.assertEqual(replay(self.instance)['root_state'], 'unresolved')

    def test_statements_whose_proofs_name_each_other_do_not_settle_each_other(self):
        folder = self.candidate(
            modules={'Small/Loop.lean': module_text(theorem('loopB', ': oddSum 2 = 4', uses=['root']),
                                                    imports=('Small.Root',)),
                     'Small/LoopAlt.lean': module_text(theorem('rootAlt', ROOT_STATEMENTS[self.root_variant], uses=['loopB']),
                                                       imports=('Small.Loop',))},
            records={'Small/loopB.md': record_text('Two terms, from the root.', weight='unit', proof='The case n = 2 of the root.'),
                     'Small/rootAlt.md': record_text('The root, from two terms.', weight='unit',
                                                     proof='Extend the case of two terms.', proves='Small.root')})
        self.publish(folder)
        model = replay(self.instance)
        elements = model['elements']
        # Both proofs are accepted, and each rests on the statement the other proves.
        self.assertEqual((elements['Small.loopB']['standing'], elements['Small.rootAlt']['standing']), ('accepted', 'accepted'))
        self.assertEqual((elements['Small.loopB']['uses'], elements['Small.rootAlt']['uses']), (['Small.root'], ['Small.loopB']))
        self.assertFalse(any(elements[name]['settled'] for name in ('Small.root', 'Small.loopB', 'Small.rootAlt')))
        self.assertFalse(elements['Small.root']['statement_settled'])
        self.assertEqual(model['root_state'], 'unresolved')
        # The descent of the frontier ends where the statement comes round again.
        self.assertEqual([(row['name'], row['kind'], row['depth']) for row in model['frontier']],
                         [('Small.root', 'statement', 0), ('Small.rootAlt', 'proof', 1),
                          ('Small.loopB', 'statement', 2), ('Small.root', 'repeat', 3)])
        self.assertEqual(model['remaining'], ['Small.root'])
        # A proof of the root that rests on neither settles all three.
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.')
        model = replay(self.instance)
        self.assertTrue(all(model['elements'][name]['settled'] for name in ('Small.root', 'Small.loopB', 'Small.rootAlt')))
        self.assertEqual(model['root_state'], 'informal_proved')

    def test_formal_follows_the_axioms_through_everything_of_the_canon_a_proof_uses(self):
        self.proved()
        model = replay(self.instance)
        self.assertFalse(any(model['elements']['Small.' + n]['formal'] for n in ('root', 'sumZero', 'sumSucc', 'sumTwo')))
        # A proof that is complete in Lean is not formal while something it uses still rests on sorry.
        self.replace_proof('Small.root', self.root_formal(uses=['sumZero', 'sumSucc']),
                           'By induction on $n$, from the empty sum and the passage from $n$ to $n + 1$.')
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['lean_proof'], root['axioms'], root['formal'], root['settled'], root['statement_formal']),
                         ('complete', ['sorryAx'], False, True, False))
        self.assertEqual((model['root_state'], root_solved(model)), ('informal_proved', False))
        # Once what it uses is proved in Lean as well, the closure is within the allowed axioms.
        folder = self.candidate(replace={'Small.sumZero': theorem('sumZero', SUM_ZERO, proof='rfl'),
                                         'Small.sumSucc': theorem('sumSucc', SUM_SUCC, proof='rfl')})
        self.publish(folder)
        model = replay(self.instance)
        elements = model['elements']
        self.assertEqual({n: (elements['Small.' + n]['axioms'], elements['Small.' + n]['formal'])
                          for n in ('root', 'sumZero', 'sumSucc')},
                         {'root': ([], True), 'sumZero': ([], True), 'sumSucc': ([], True)})
        self.assertEqual((elements['Small.sumTwo']['axioms'], elements['Small.sumTwo']['formal']), (['sorryAx'], False))
        self.assertEqual((model['root_state'], root_solved(model)), ('formal_proved', True))

    def test_the_root_question_is_resolved_only_by_the_roots_formal_settlement(self):
        model = replay(self.instance)
        self.assertEqual((model['root_state'], model['questions']['q0']['state']), ('unresolved', 'open'))
        self.direct()
        model = replay(self.instance)
        self.assertEqual((model['root_state'], root_solved(model), model['questions']['q0']['state']),
                         ('informal_proved', False, 'open'))
        self.formal()
        model = replay(self.instance)
        settlement = {'state': 'formal_proved', 'proofs': ['Small.root']}
        self.assertEqual((model['root_state'], root_solved(model), root_settlement(model)),
                         ('formal_proved', True, settlement))
        question = model['questions']['q0']
        self.assertEqual((question['state'], question['root_settlement'], question['resolutions']),
                         ('resolved', settlement, []))
        # A finding that withdraws the root's proof withdraws the settlement, and the root question reopens.
        self.event('v1', 'review', comprehensive([finding('The step fails at zero.', invalidates=['Small.root'])]))
        model = replay(self.instance)
        self.assertEqual((model['root_state'], root_solved(model), model['questions']['q0']['state']),
                         ('unresolved', False, 'open'))

    def test_nothing_rests_on_a_contested_statement_and_a_refuted_one_needs_another_proof_above_it(self):
        self.proved()
        self.assertEqual(replay(self.instance)['root_state'], 'informal_proved')
        folder = self.candidate(
            modules={'Small/Against.lean': module_text(theorem('notZero', ': ¬ (oddSum 0 = 0)'))},
            records={'Small/notZero.md': record_text('The empty sum is not zero.', weight='unit',
                                                     proof='A miscount of the empty sum.', refutes='Small.sumZero')})
        self.publish(folder)
        model = replay(self.instance)
        elements = model['elements']
        self.assertTrue(model['pairs']['negation|Small.notZero|Small.sumZero'])
        self.assertEqual(elements['Small.notZero']['refutes'], 'Small.sumZero')
        # The statement and its negation both carry settled proofs. Both are contested, and neither counts
        # as settled, so the root's proof, which names one of them, is not settled any more.
        self.assertEqual(model['contested'], ['Small.sumZero'])
        for name in ('Small.sumZero', 'Small.notZero'):
            element = elements[name]
            self.assertEqual((element['contested'], element['settled'], element['statement_settled'],
                              element['statement_formal'], element['refuted_by']), (True, True, False, False, []), name)
        self.assertEqual((elements['Small.root']['standing'], elements['Small.root']['settled'], model['root_state']),
                         ('accepted', False, 'unresolved'))
        # A contested statement is not formalized, and what rests on it waits.
        self.assertEqual(formalizable(model), ['Small.sumSucc'])
        # The frontier opens it under the root and says so; it is review's to examine, not an attempt's to take on.
        self.assertEqual([(row['name'], row['standing'], row['contested']) for row in model['frontier']],
                         [('Small.root', 'accepted', False), ('Small.sumZero', 'accepted', True)])
        self.assertEqual(model['remaining'], [])
        view = frontier_view(self.instance)
        self.assertIn('  - `Small.sumZero` — The empty sum is zero. — accepted · contested: it and its negation both carry '
                      'settled proofs\n', view)
        self.assertIn('Contested: a statement and its negation both carry settled proofs, and nothing rests on either '
                      'until a comprehensive review locates the failure: `Small.sumZero`.', view)
        runner = Runner(self.instance, self.skill)
        session = self.session(runner, 'sa')
        self.assertIn('contested', lease(session, 'Small.sumZero')['reason'])

        # With the proof withdrawn the refutation stands alone: the statement is refuted, not contested.
        self.event('v1', 'review', comprehensive([finding('The empty sum was miscounted.', invalidates=['Small.sumZero'])]))
        model = replay(self.instance)
        elements = model['elements']
        self.assertEqual((model['contested'], elements['Small.sumZero']['contested'], elements['Small.sumZero']['refuted_by']),
                         ([], False, ['Small.notZero']))
        self.assertTrue(elements['Small.notZero']['settled'] and elements['Small.notZero']['statement_settled'])
        # The refutation refutes that statement and not the root, whose proof only named it. That proof
        # cannot become settled as it stands, so the root is work that remains, although its proof is accepted;
        # no work remains on the refuted statement, and nothing is opened beneath it.
        self.assertEqual((model['root_state'], elements['Small.root']['standing'], elements['Small.root']['names_refuted']),
                         ('unresolved', 'accepted', ['Small.sumZero']))
        self.assertEqual([(row['name'], row['refuted_by'], row['names_refuted']) for row in model['frontier']],
                         [('Small.root', [], ['Small.sumZero']), ('Small.sumZero', ['Small.notZero'], [])])
        self.assertEqual(model['remaining'], ['Small.root'])
        render(self.instance, model, [])
        view = frontier_view(self.instance)
        self.assertIn('- `Small.root` — odd numbers sum to a square — accepted · its proof names `Small.sumZero`, refuted since; '
                      'the statement needs another proof\n', view)
        self.assertIn('  - `Small.sumZero` — The empty sum is zero. — refuted by `Small.notZero`\n', view)
        self.assertNotIn('Contested:', view)
        self.assertIn('refuted by Small.notZero', lease(session, 'Small.sumZero')['reason'])
        self.assertTrue(lease(session, 'Small.root')['leased'])

    def test_a_concern_annotates_without_changing_standing_and_a_finding_changes_it(self):
        self.half()
        self.event('v1', 'review', comprehensive(concerns=[concern('boundary', 'Small.sumZero')]))
        model = replay(self.instance)
        element = model['elements']['Small.sumZero']
        self.assertEqual(model['concerns']['v1/boundary']['status'], 'pending')
        self.assertEqual((element['concerns'], element['standing'], element['settled']), (['v1/boundary'], 'accepted', True))
        # The questioned proof is still accepted mathematics: its formalization goes ahead.
        self.assertEqual(formalizable(model), ['Small.sumZero'])
        render(self.instance, model, [])
        self.assertIn('- v1/boundary on `Small.sumZero`: A boundary case needs checking. (pending); '
                      'comprehensive review pending assignment', frontier_view(self.instance))
        # Only a finding changes standing: it withdraws the confirmation, and what rested on it is recomputed.
        self.event('v2', 'review', comprehensive([finding('The boundary case fails.', concerns=['v1/boundary'],
                                                          invalidates=['Small.sumZero'])]))
        model = replay(self.instance)
        element = model['elements']['Small.sumZero']
        self.assertEqual((element['standing'], element['settled'], element['verdict']['later_review']),
                         ('not_confirmed', False, 'v2'))
        self.assertEqual([model['findings'][number]['source'] for number in element['findings']], ['v2'])
        self.assertEqual(model['concerns']['v1/boundary']['status'], 'confirmed')
        self.assertEqual(model['concerns']['v1/boundary']['finding'], {'review': 'v2', 'reason': 'The boundary case fails.'})
        self.assertEqual((formalizable(model), model['remaining']), ([], ['Small.sumSucc', 'Small.sumZero']))
        # A finding that clears the concern and restores the confirmation closes it.
        self.event('v3', 'review', comprehensive([finding('The boundary case holds on a second reading.', status='cleared',
                                                          concerns=['v1/boundary'], validates=['Small.sumZero'])]))
        model = replay(self.instance)
        self.assertEqual((model['elements']['Small.sumZero']['standing'], model['concerns']['v1/boundary']['status']),
                         ('accepted', 'cleared'))
        render(self.instance, model, [])
        self.assertNotIn('## Concerns', frontier_view(self.instance))

    def test_a_finding_on_an_element_the_instance_began_with_judges_the_proof_it_began_with(self):
        # No review has judged an element the instance began with. Lean's check of a complete proof stands
        # where review's judgment would; a proof that is written only waits for a review.
        self.instance = initialized(
            self.root, 'began',
            modules={'Small/Known.lean': module_text('\n\n'.join([theorem('knownLean', SUM_ZERO, proof='rfl'),
                                                                  theorem('knownWritten', ': oddSum 1 = 1')]))},
            records={'Small/knownLean.md': record_text('The empty sum is zero.', weight='unit'),
                     'Small/knownWritten.md': record_text('The first odd number is one.', weight='unit',
                                                          proof='The sum has the one term 1.')})
        self.addCleanup(stop_broker, self.instance)
        names = ('Small.knownLean', 'Small.knownWritten')

        def standings():
            elements = replay(self.instance)['elements']
            return tuple(elements[name]['standing'] for name in names)

        elements = replay(self.instance)['elements']
        self.assertEqual([(elements[n]['lean_proof'], elements[n]['written_proof'], elements[n]['verdict']) for n in names],
                         [('complete', False, None), ('sorry', True, None)])
        self.assertEqual(standings(), ('accepted', 'not_confirmed'))
        self.event('v1', 'review', comprehensive([finding('Both arguments skip the case of no terms.', invalidates=list(names))]))
        self.assertEqual(standings(), ('not_confirmed', 'not_confirmed'))
        # Restoring the confirmation restores what the proof stood on before: Lean's check for the complete
        # proof, which stands accepted again, and no acceptance for the written one, which stands held.
        self.event('v2', 'review', comprehensive([finding('The case of no terms is covered after all.', status='cleared',
                                                          validates=list(names))]))
        self.assertEqual(standings(), ('accepted', 'held'))
        verdict = replay(self.instance)['elements']['Small.knownLean']['verdict']
        self.assertEqual((verdict['correct'], verdict['accepted'], verdict['change'], verdict['later_review']),
                         ('confirmed', True, None, 'v2'))

    def test_a_finding_that_confirms_a_proof_says_whether_the_proof_is_accepted(self):
        # The review of its change did not confirm diagD, so no review asked of it the two questions that decide
        # acceptance. A later review that confirms it answers them in the same finding, as the review of a
        # candidate does, and its reason becomes the reason of the verdict.
        self.ways()

        def verdict(name):
            element = replay(self.instance)['elements'][name]
            return element['standing'], element['verdict']['reason'], element['verdict'].get('later_review')

        self.assertEqual(verdict('Small.diagD'), ('not_confirmed', GAP_REASON, None))
        accepts = 'The addition is carried out in full, and no step of it can be dropped.'
        self.event('v1', 'review', comprehensive([finding(accepts, status='cleared', validates=['Small.diagD'],
                                                          accepted=True)]))
        self.assertEqual(verdict('Small.diagD'), ('accepted', accepts, 'v1'))
        # The judgment is taken whichever way it goes: said of a proof that stood accepted, it holds that proof back.
        holds = 'Correct; the step for four terms repeats the step for three.'
        self.event('v2', 'review', comprehensive([finding(holds, validates=['Small.stepE'], accepted=False)]))
        self.assertEqual(verdict('Small.stepE'), ('held', holds, 'v2'))

    def test_a_status_alone_changes_no_standing(self):
        self.half()
        self.event('v1', 'review', comprehensive(concerns=[concern('boundary', 'Small.sumZero')]))
        self.event('v2', 'review', comprehensive([finding('The boundary case could not be decided.', status='undetermined',
                                                          concerns=['v1/boundary'])]))
        model = replay(self.instance)
        self.assertEqual(model['concerns']['v1/boundary']['status'], 'undetermined')
        self.assertEqual((model['elements']['Small.sumZero']['standing'], model['elements']['Small.sumZero']['settled']),
                         ('accepted', True))

    def test_questions_are_resolved_by_an_accepted_resolution_reopened_by_a_finding_and_merged(self):
        self.questions('qops', [{'id': 'scale', 'statement': 'Why do the methods stall at the same scale?',
                                 'grounds': 'Several approaches stop there.'},
                                {'id': 'block', 'statement': 'What does the common block say about the object?',
                                 'grounds': 'The same obstruction recurs.'}])
        folder = self.candidate(
            understanding={'scale.md': 'The scale is the first place where two squares overlap.\n',
                           'block.md': 'The block has not been explained.\n',
                           'q0.md': 'The sum grows by one odd number at a time.\n'},
            resolutions=[{'id': 'answer', 'question': 'scale'}, {'id': 'guess', 'question': 'block'},
                         {'id': 'whole', 'question': 'q0'}])
        assessment = self.verdicts(folder)
        assessment['resolutions'][1].update(resolved=False, reason='The account does not say why the block recurs.')
        change, _ = self.publish(folder, assessment, role='explore', question='scale')
        model = replay(self.instance)
        questions = model['questions']
        self.assertEqual({qid: (q['state'], q['resolutions']) for qid, q in questions.items() if qid != 'q0'},
                         {'scale': ('resolved', [change + '/answer']), 'block': ('open', [])})
        # The root question asks the root problem itself, so no account resolves it, whatever review said of one.
        self.assertEqual((questions['q0']['state'], questions['q0']['root_settlement']), ('open', None))

        published = {path: path.read_bytes() for path in (self.instance / 'knowledge').rglob('*')
                     if path.is_file() and 'changes' in path.parts}
        # An organizer merges two questions that ask the same thing; the merged one keeps what resolved either.
        self.organize(batch=[change], merge_questions=[{'from': 'scale', 'into': 'block', 'reason': 'Both ask about the block.'}])
        model = replay(self.instance)
        self.assertEqual((canonical_question(model, 'scale'), model['question_aliases']), ('block', {'scale': 'block'}))
        self.assertEqual((model['questions']['block']['state'], model['questions']['block']['resolutions']),
                         ('resolved', [change + '/answer']))
        self.assertEqual(model['questions']['scale']['canonical'], 'block')
        render(self.instance, model, [])
        view = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        # A resolved question takes one line of the list, with what resolved it and its aliases.
        self.assertNotIn('\n## scale\n', view)
        self.assertNotIn('\n## block\n', view)
        self.assertIn(f'\n## Resolved questions\n\n- block — resolved by {change}/answer · aliases: scale\n', view)
        # A finding reopens the question, and stays beside it as a later review.
        self.event('v1', 'review', comprehensive([finding('The overlap is not the cause.', reopens=['block'])]))
        model = replay(self.instance)
        self.assertEqual((model['questions']['block']['state'], model['questions']['block']['resolutions']), ('open', []))
        render(self.instance, model, [])
        self.assertIn('- Later review (confirmed): The overlap is not the cause. — v1',
                      (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))
        # Publications are never rewritten, and replaying them gives the same model.
        self.assertEqual({path: path.read_bytes() for path in published}, published)
        self.assertEqual(replay(self.instance), model)


class RefutationTests(RefutedRootCase):
    def test_a_settled_refutation_of_the_root_refutes_it_informally_then_formally(self):
        self.refuted()
        model = replay(self.instance)
        self.assertTrue(model['pairs']['negation|Small.notRoot|Small.root'])
        self.assertEqual(model['elements']['Small.notRoot']['refutes'], 'Small.root')
        self.assertEqual((model['root_state'], root_solved(model), model['contested']), ('informal_refuted', False, []))
        self.assertEqual(model['questions']['q0']['state'], 'open')
        self.formally_refuted()
        model = replay(self.instance)
        settlement = {'state': 'formal_refuted', 'proofs': ['Small.notRoot']}
        self.assertEqual((model['root_state'], root_solved(model), root_settlement(model)),
                         ('formal_refuted', True, settlement))
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['root_settlement']),
                         ('resolved', settlement))
        # A refutation whose confirmation is withdrawn refutes nothing.
        self.event('v1', 'review', comprehensive([finding('The sum of the first two is four.', invalidates=['Small.notRoot'])]))
        self.assertEqual(replay(self.instance)['root_state'], 'unresolved')

    def test_a_settled_informal_refutation_of_the_root_is_sent_for_its_formal_proof(self):
        # The obligation to prove formally is unchanged (design record, section 5), and the instance is
        # complete on a formal refutation as on a formal proof. A settled refutation of the root that has
        # no formal proof is therefore work for a formalizer, as a settled proof of the root is.
        self.refuted()
        self.assertEqual(formalizable(replay(self.instance)), ['Small.notRoot'])

    def test_a_negation_settled_through_another_declaration_refutes_the_root(self):
        # The declaration that carries the negation has no proof of its own. A second declaration with the
        # same statement, marked as another proof of it, is complete in Lean and accepted. The negation is
        # then settled, and the root is refuted through the declaration that holds the proof.
        folder = self.candidate(
            modules={'Small/Against.lean': module_text(theorem('notRoot', self.NEGATION))},
            records={'Small/notRoot.md': record_text('Some initial sum of odd numbers is not a square.', weight='unit',
                                                     refutes='Small.root')})
        self.publish(folder)
        model = replay(self.instance)
        self.assertEqual((model['elements']['Small.notRoot']['standing'], model['root_state']), ('no_proof', 'unresolved'))
        folder = self.candidate(
            modules={'Small/AgainstAlt.lean': module_text(
                theorem('notRootAlt', self.NEGATION, proof='intro h\n  exact absurd (h 2) (by decide)'), imports=('Small.Against',))},
            records={'Small/notRootAlt.md': record_text('The same negation, proved from the second value.', weight='unit',
                                                        proves='Small.notRoot')})
        self.publish(folder)
        model = replay(self.instance)
        elements = model['elements']
        self.assertEqual(elements['Small.notRootAlt']['statement_of'], 'Small.notRoot')
        self.assertEqual((elements['Small.notRoot']['standing'], elements['Small.notRoot']['statement_settled']), ('no_proof', True))
        self.assertEqual(elements['Small.root']['refuted_by'], ['Small.notRoot'])
        settlement = {'state': 'formal_refuted', 'proofs': ['Small.notRootAlt']}
        self.assertEqual((model['root_state'], root_solved(model), root_settlement(model)), ('formal_refuted', True, settlement))
        self.assertEqual((model['remaining'], formalizable(model), model['contested']), ([], [], []))
        # A proof of the root beside it makes the pair contested, as when the negation's own declaration holds the proof.
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.')
        model = replay(self.instance)
        self.assertEqual((model['root_state'], model['contested']), ('contested', ['Small.root']))

    def test_a_root_with_settled_proofs_of_itself_and_of_its_negation_is_contested(self):
        self.contested()
        model = replay(self.instance)
        self.assertEqual((model['root_state'], model['contested']), ('contested', ['Small.root']))
        for name in ('Small.root', 'Small.notRoot'):
            element = model['elements'][name]
            self.assertEqual((element['contested'], element['statement_settled'], element['statement_formal']),
                             (True, False, False), name)
        self.assertEqual((model['remaining'], formalizable(model)), ([], []))
        # A contested root is not a solved one, although its refutation is formal, and it does not close q0.
        self.assertEqual((root_solved(model), root_settlement(model), model['questions']['q0']['state']),
                         (False, None, 'open'))
        view = frontier_view(self.instance)
        self.assertIn('State: contested', view)
        self.assertIn('- `Small.root` — odd numbers sum to a square — accepted · contested: it and its negation both carry '
                      'settled proofs\n', view)
        self.assertIn('nothing rests on either until a comprehensive review locates the failure: `Small.root`.', view)


class FrontierTests(ScenarioCase):
    def test_at_the_start_the_frontier_is_the_root_alone_without_a_proof(self):
        model = replay(self.instance)
        self.assertEqual([(row['name'], row['kind'], row['depth'], row['standing']) for row in model['frontier']],
                         [('Small.root', 'statement', 0, 'no_proof')])
        self.assertEqual(model['remaining'], ['Small.root'])

    def test_the_frontier_descends_from_the_root_through_every_proof_and_opens_what_is_not_settled(self):
        self.ways()
        model = replay(self.instance)
        rows = [(row['name'].removeprefix('Small.'), row['kind'], row['depth'], row['standing']) for row in model['frontier']]
        self.assertEqual(rows, [
            ('root', 'statement', 0, 'accepted'),      # opened: its own proof is accepted and rests on unsettled statements
            ('colA', 'statement', 1, 'held'),
            ('leafH', 'statement', 2, 'no_proof'),     # what the held proof names lies beneath it
            ('monoB', 'statement', 1, 'no_proof'),     # reached through stepE, an accepted step, which is passed through
            ('monoBAlt', 'proof', 2, 'not_confirmed'),  # every proof of a statement is shown, whatever its state
            ('leafH', 'repeat', 3, 'no_proof'),
            ('rootAlt', 'proof', 1, 'held'),           # the second way of proving the root
            ('colA', 'repeat', 2, 'held'),             # shown again where another proof names it, and not opened twice
            ('diagD', 'statement', 2, 'not_confirmed'),
            ('stepF', 'statement', 3, 'no_proof'),     # a step that is itself work that remains is shown
        ])
        names = [row[0] for row in rows]
        # unitG is settled and is not opened; stepE is passed through; nothing the root rests on names strayS.
        self.assertFalse({'unitG', 'stepE', 'strayS'} & set(names))
        self.assertEqual(names.count('leafH'), 2)
        self.assertEqual([row for row in rows if row[0] == 'leafH' and row[1] == 'statement'], [('leafH', 'statement', 2, 'no_proof')])
        # The reasons of review stand beside the proofs that remain work; the approaches tried are counted.
        by_name = {row['name']: row for row in model['frontier'] if row['kind'] != 'repeat'}
        self.assertEqual((by_name['Small.colA']['reason'], by_name['Small.diagD']['reason'], by_name['Small.root']['reason']),
                         (HELD_REASON, GAP_REASON, None))
        self.assertEqual((by_name['Small.monoB']['approaches'], by_name['Small.colA']['approaches']), (1, 0))
        self.assertEqual((by_name['Small.stepF']['weight'], by_name['Small.colA']['short']), ('step', 'Col'))

    def test_the_work_that_remains_is_what_the_frontier_shows_without_an_accepted_proof(self):
        self.ways()
        model = replay(self.instance)
        self.assertEqual(model['remaining'], ['Small.colA', 'Small.diagD', 'Small.leafH', 'Small.monoB',
                                              'Small.monoBAlt', 'Small.rootAlt', 'Small.stepF'])
        # The root rests on more than the frontier shows as remaining, and on nothing that no proof of it names.
        self.assertEqual(rests_on(model, 'Small.root'),
                         {'Small.' + n for n in ('root', 'colA', 'leafH', 'stepE', 'monoB', 'unitG', 'diagD', 'stepF')})

    def test_a_settled_part_is_not_opened_and_the_root_is_settled_when_every_part_is(self):
        self.split()
        model = replay(self.instance)
        self.assertEqual([(row['name'], row['depth'], row['standing']) for row in model['frontier']],
                         [('Small.root', 0, 'accepted'), ('Small.sumSucc', 1, 'no_proof'), ('Small.sumZero', 1, 'no_proof')])
        self.assertEqual((model['remaining'], model['root_state']), (['Small.sumSucc', 'Small.sumZero'], 'unresolved'))
        self.half()
        model = replay(self.instance)
        self.assertEqual([(row['name'], row['depth'], row['standing']) for row in model['frontier']],
                         [('Small.root', 0, 'accepted'), ('Small.sumSucc', 1, 'no_proof')])
        self.assertEqual((model['remaining'], model['root_state']), (['Small.sumSucc'], 'unresolved'))
        self.proved()
        model = replay(self.instance)
        self.assertEqual([(row['name'], row['settled']) for row in model['frontier']], [('Small.root', True)])
        self.assertEqual((model['remaining'], model['root_state']), ([], 'informal_proved'))

    def test_a_root_settled_through_another_proof_leaves_no_work_that_remains(self):
        # The frontier stops at statements that are settled, and a statement is settled when one of its
        # proofs is (design record, sections 5 and 6). The root is such a statement here: its own
        # declaration has no proof, and another declaration proves it.
        second_proof(self)
        model = replay(self.instance)
        self.assertTrue(model['elements']['Small.root']['statement_settled'])
        self.assertEqual(model['root_state'], 'informal_proved')
        self.assertEqual(model['remaining'], [])

    def test_a_settled_root_does_not_open_a_second_proof_that_is_not_accepted(self):
        self.direct()
        folder = self.candidate(
            modules={'Small/Second.lean': module_text('\n\n'.join([
                theorem('sideL', ': oddSum 1 = 1'), theorem('rootAlt', ROOT_STATEMENTS[self.root_variant], uses=['sideL'])]))},
            records={'Small/sideL.md': record_text('The first odd number is one.', weight='unit'),
                     'Small/rootAlt.md': record_text('The root by another argument.', weight='unit',
                                                     proof='From the first odd number.', proves='Small.root')})
        self.publish(folder, self.verdicts(folder, **{'Small.rootAlt': {
            'correct': 'not_confirmed', 'accepted': False, 'reason': GAP_REASON}}))
        model = replay(self.instance)
        self.assertTrue(model['elements']['Small.root']['settled'])
        # Nothing remains for a settled root: neither its unconfirmed second proof nor what that proof names.
        self.assertEqual(model['remaining'], [])


class FormalizableTests(ScenarioCase):
    def test_only_settled_statements_the_root_rests_on_are_formalized(self):
        self.half()
        model = replay(self.instance)
        # sumSucc has no proof and the root is not settled; sumTwo is settled, and the root does not rest on it.
        self.assertTrue(model['elements']['Small.sumTwo']['settled'])
        self.assertEqual(formalizable(model), ['Small.sumZero'])

    def test_a_proof_is_formalized_once_what_it_names_has_formal_proofs(self):
        self.proved()
        self.assertEqual(formalizable(replay(self.instance)), ['Small.sumSucc', 'Small.sumZero'])
        folder = self.candidate(replace={'Small.sumZero': theorem('sumZero', SUM_ZERO, proof='rfl')})
        self.publish(folder)
        # sumZero has its formal proof; the root still waits for the other statement its proof names.
        self.assertEqual(formalizable(replay(self.instance)), ['Small.sumSucc'])
        folder = self.candidate(replace={'Small.sumSucc': theorem('sumSucc', SUM_SUCC, proof='rfl')})
        self.publish(folder)
        self.assertEqual(formalizable(replay(self.instance)), ['Small.root'])
        self.formal()
        self.assertEqual(formalizable(replay(self.instance)), [])

    def test_a_complete_lean_proof_that_names_an_open_declaration_is_formalized_once_what_it_names_is_formal(self):
        # The root's own Lean text is complete, but it names sumZero and sumSucc, whose declarations end in sorry,
        # so the root is not formal. Each of the two statements comes to have a formal proof under another
        # declaration; the declarations the root names keep their open Lean proofs.
        self.proved()
        self.replace_proof('Small.root', self.root_formal(uses=['sumZero', 'sumSucc']),
                           'By induction on $n$, from the empty sum and the passage from $n$ to $n + 1$.')
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['lean_proof'], root['formal'], root['settled']), ('complete', False, True))
        self.assertEqual(formalizable(model), ['Small.sumSucc', 'Small.sumZero'])

        def formal_alternative(name, statement, target):
            folder = self.candidate(
                modules={f'Small/{name}.lean': module_text(theorem(name, statement, proof='rfl'))},
                records={f'Small/{name}.md': record_text('The same statement, proved in Lean.', weight='unit',
                                                         proves=target)})
            self.publish(folder)

        formal_alternative('sumZeroAlt', SUM_ZERO, 'Small.sumZero')
        model = replay(self.instance)
        self.assertEqual((model['elements']['Small.sumZero']['lean_proof'], model['elements']['Small.sumZero']['statement_formal']),
                         ('sorry', True))
        # The root still names a statement without a formal proof, and waits.
        self.assertEqual(formalizable(model), ['Small.sumSucc'])
        formal_alternative('sumSuccAlt', SUM_SUCC, 'Small.sumSucc')
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['lean_proof'], root['axioms'], root['formal']), ('complete', ['sorryAx'], False))
        self.assertTrue(all(model['elements'][name]['statement_formal'] for name in ('Small.sumZero', 'Small.sumSucc')))
        self.assertEqual(formalizable(model), ['Small.root'])

    def test_one_proof_per_statement_is_formalized_the_statements_own_declaration_first(self):
        self.direct()
        publish_second_proof(self)
        model = replay(self.instance)
        self.assertTrue(model['elements']['Small.root']['settled'] and model['elements']['Small.rootAlt']['settled'])
        self.assertEqual(formalizable(model), ['Small.root'])
        # When the statement is settled through the other proof alone, that proof is the one to formalize.
        self.event('v1', 'review', comprehensive([finding('The induction step fails.', invalidates=['Small.root'])]))
        self.assertEqual(formalizable(replay(self.instance)), ['Small.rootAlt'])


class CoordinationTests(ScenarioCase):
    def runner(self):
        return Runner(self.instance, self.skill)

    def table(self):
        return {name: ([h['session'] for h in entry['holders']], [w['session'] for w in entry['queue']])
                for name, entry in lease_table(self.instance).items()}

    def test_lease_is_first_wins_and_a_refusal_records_nothing(self):
        self.split()
        runner = self.runner()
        first, second = (self.session(runner, sid) for sid in ('sfirst', 'ssecond'))
        self.assertTrue(lease(first, 'Small.sumZero')['leased'])
        refused = lease(second, 'Small.sumZero')
        self.assertFalse(refused['leased'])
        self.assertEqual((refused['element'], refused['holders'], refused['queue']), ('Small.sumZero', ['sfirst'], []))
        self.assertEqual(self.table(), {'Small.sumZero': (['sfirst'], [])})
        self.assertFalse((second / 'declaration.json').exists())
        # Repeating one's own lease is accepted; the refused attempt can take another element.
        self.assertTrue(lease(first, 'Small.sumZero')['leased'])
        self.assertTrue(lease(second, 'Small.sumSucc')['leased'])

    def test_simultaneous_leases_from_separate_processes_admit_one_holder(self):
        runner = self.runner()
        folders = [self.session(runner, 's' + str(i)) for i in range(6)]
        runtime = str(Path(__file__).resolve().parents[1])
        # Every process imports first and leaves a file that says so. When all six have, the file `go` is made,
        # which each of them looks for every few milliseconds, so that they ask at the same instant.
        launcher = ('import os, sys, time\n'
                    'sys.path.insert(0, %r)\n'
                    'import coordination\n'
                    'session, imported, go = sys.argv[1:]\n'
                    'open(imported, "w").close()\n'
                    'while not os.path.exists(go):\n'
                    '    time.sleep(0.005)\n'
                    'sys.argv = ["coordination.py", "lease", session, "Small.root"]\n'
                    'raise SystemExit(coordination.main())\n') % runtime
        imported, go = [self.root / ('imported-' + f.name) for f in folders], self.root / 'go'
        processes = [subprocess.Popen([sys.executable, '-B', '-c', launcher, str(f), str(mark), str(go)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for f, mark in zip(folders, imported)]
        deadline = time.monotonic() + 60
        while not all(mark.exists() for mark in imported) and time.monotonic() < deadline:
            time.sleep(0.02)
        go.touch()
        results = []
        for process in processes:
            # communicate() reads and closes both pipes; a child that printed no answer shows its traceback.
            out, err = process.communicate(timeout=60)
            self.assertTrue(out.strip(), err.decode('utf-8', 'replace'))
            results.append((process.returncode, json.loads(out.decode('utf-8'))))
        self.assertEqual(sorted(code for code, _ in results), [0, 1, 1, 1, 1, 1], results)
        holders = lease_table(self.instance)['Small.root']['holders']
        self.assertEqual(len(holders), 1)
        self.assertEqual([r['holders'] for code, r in results if code == 0], [[holders[0]['session']]])

    def test_waiters_are_served_in_order_and_registration_passes_the_lease(self):
        runner = self.runner()
        a, b, c = (self.session(runner, sid) for sid in ('sa', 'sb', 'sc'))
        self.assertTrue(lease(a, 'Small.root')['leased'])
        self.assertEqual(wait(b, 'Small.root', timeout=0)['position'], 1)
        self.assertEqual(wait(c, 'Small.root', timeout=0)['position'], 2)
        # The board view shows who holds the element's lease and who waits, in order.
        render(self.instance, replay(self.instance), board(self.instance), lease_table(self.instance))
        self.assertIn('- Small.root · lease: sa · waiting: sb, sc',
                      (self.instance / 'knowledge/board.md').read_text(encoding='utf-8'))
        first = take(a, 'Small.root', 'The identity for every even n.', leased=True)
        self.assertTrue(first['registered'], first)
        sid_a = first['section']['id']
        self.assertEqual(self.table(), {'Small.root': (['sb'], ['sc'])})
        self.assertTrue(wait(b, 'Small.root', timeout=0)['leased'])
        # The tool refuses what it can decide; overlap itself is the registering session's reasoned judgement.
        self.assertIn('whole element cannot', take(b, 'Small.root', leased=True)['reason'])
        self.assertIn('exact statement', take(b, 'Small.root', 'The identity  for every even n.', leased=True)['reason'])
        missing = take(b, 'Small.root', 'The identity for every odd n.', leased=True)
        self.assertIn(sid_a, missing['reason'])
        self.assertFalse((b / 'declaration.json').exists())
        second = take(b, 'Small.root', 'The identity for every odd n.',
                      {sid_a: 'Mine concerns odd n only, where the other section does not apply.'}, leased=True)
        self.assertTrue(second['registered'], second)
        self.assertEqual(second['section']['reasons'], {sid_a: 'Mine concerns odd n only, where the other section does not apply.'})
        self.assertEqual(self.table(), {'Small.root': (['sc'], [])})
        rows = {r['session']: [s['id'] for s in r['sections']] for r in board(self.instance)}
        self.assertEqual(rows, {'sa': [sid_a], 'sb': [second['section']['id']], 'sc': []})
        self.assertEqual({r['session']: r['elements'] for r in board(self.instance)},
                         {'sa': ['Small.root'], 'sb': ['Small.root'], 'sc': []})
        # Parts of an element leave it available to a further attempt.
        self.assertEqual(runner.available_elements(), ['Small.root'])
        # A section's exact statement reaches board.md as written.
        render(self.instance, replay(self.instance), board(self.instance))
        self.assertIn(f'  Section {sid_a} on Small.root (session sa): The identity for every even n.',
                      (self.instance / 'knowledge/board.md').read_text(encoding='utf-8'))

    def test_lease_of_an_ended_session_passes_to_the_next_waiter(self):
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        self.assertTrue(lease(a, 'Small.root')['leased'])
        self.assertFalse(wait(b, 'Small.root', timeout=0)['leased'])
        runner.state['sessions']['sa']['status'] = 'ended'
        runner.save()
        self.assertTrue(wait(b, 'Small.root', timeout=0)['leased'])
        # A running session whose host and CLI are both gone has ended as well.
        c = self.session(runner, 'sc')
        self.assertFalse(wait(c, 'Small.root', timeout=0)['leased'])
        gone = {'pid': 2 ** 22, 'birth': 'gone'}
        runner.state['sessions']['sb'].update(host=gone, cli=gone)
        runner.save()
        self.assertTrue(wait(c, 'Small.root', timeout=0)['leased'])

    def test_a_wait_looks_again_until_the_lease_arrives_or_the_element_closes(self):
        # Every other test asks with a timeout of 0, which is one look. A waiting command looks again after
        # each pause until its timeout, and reference/sections.md promises both ways it then ends. Only the
        # pause is replaced, and what happens during it is another session's command, so the test waits for
        # nothing.
        from types import SimpleNamespace
        runner = self.runner()
        a, b, c = (self.session(runner, sid) for sid in ('sa', 'sb', 'sc'))
        self.assertTrue(lease(a, 'Small.root')['leased'])

        def waiting(session, meanwhile):
            pauses = []

            def pause(seconds):
                pauses.append(seconds)
                if len(pauses) == 1:
                    meanwhile()

            with patch('coordination.time', SimpleNamespace(time=time.time, monotonic=time.monotonic, sleep=pause)):
                answer = wait(session, 'Small.root', timeout=60)
            self.assertEqual(len(pauses), 1)
            return answer

        # sa gives the lease up while sb waits: the next look finds the lease sb's.
        served = waiting(b, lambda: release(a, 'Small.root'))
        self.assertEqual((served['leased'], served['holders']), (True, ['sb']))
        # sb registers the whole element while sc waits: the next look refuses sc, which gives up its place.
        refused = waiting(c, lambda: self.assertTrue(take(b, 'Small.root', leased=True)['registered']))
        self.assertFalse(refused['leased'])
        self.assertIn('holds this whole element', refused['reason'])
        self.assertEqual(lease_table(self.instance), {})

    def test_a_waiting_command_reads_the_research_again_only_when_the_runner_has_saved_its_state(self):
        # A waiting command looks once a second, and in a long run the canon's index and the runner's state
        # are megabytes. What the commands of sessions change without the runner, the leases and the
        # sections, is read at every look; the research and the runner's state are read again once the
        # runner has saved its state. Only the pause is replaced, so the test waits for nothing.
        from types import SimpleNamespace
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        self.assertTrue(lease(a, 'Small.root')['leased'])
        table = self.instance / 'runner/leases.json'
        pauses = []

        def pause(seconds):
            # The table of leases as the look before this pause left it: which file stands there, and when
            # it was written.
            written = os.stat(table)
            pauses.append((written.st_ino, written.st_mtime_ns))
            self.assertLess(len(pauses), 4, 'the waiting command did not read what the runner saved')
            if len(pauses) == 3:
                # The holder's session ends. No command of a session says so; the runner's state does.
                runner.state['sessions']['sa']['status'] = 'ended'
                runner.save()

        with patch('coordination.time', SimpleNamespace(time=time.time, monotonic=time.monotonic, sleep=pause)), \
                patch('coordination.replay', wraps=replay) as read:
            served = wait(b, 'Small.root', timeout=60)
        self.assertEqual((served['leased'], served['holders'], len(pauses)), (True, ['sb'], 3))
        # Four looks: the first reads the research, the next two find the runner's state as it was, and the
        # fourth reads again what the runner saved.
        self.assertEqual(read.call_count, 2)
        # The first look put sb into the queue and wrote the table. The next two found sb still waiting and
        # left the file as the first look had written it.
        self.assertEqual(len(set(pauses)), 1)

    def test_element_commands_answer_through_the_command_line_with_the_documented_exit_codes(self):
        # Attempts and peers reach these commands only through the argv in input.json.
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        request = a / 'section.json'
        write_json(request, {'statement': 'The identity for every even n.'})

        def run(*argv):
            with patch('sys.argv', ['coordination.py', *argv]), patch('builtins.print') as shown:
                code = coordination_main()
            return code, json.loads(shown.call_args.args[0])

        code, answer = run('section', str(a), 'Small.root', '--file', str(request))
        self.assertEqual((code, answer['registered']), (1, False))
        code, answer = run('lease', str(a), 'Small.root')
        self.assertEqual((code, answer['leased'], answer['element']), (0, True, 'Small.root'))
        code, answer = run('wait', str(b), 'Small.root', '--timeout', '0')
        self.assertEqual((code, answer['timeout'], answer['position']), (124, True, 1))
        code, answer = run('section', str(a), 'Small.root', '--file', str(request))
        self.assertEqual((code, answer['registered'], answer['section']['element']), (0, True, 'Small.root'))
        code, answer = run('wait', str(b), 'Small.root', '--timeout', '0')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('release', str(b), 'Small.root')
        self.assertEqual((code, answer['released']), (0, True))
        code, answer = run('lease', str(b), 'Small.missing')
        self.assertEqual((code, answer['error']), (1, 'unknown element; use the declaration name as the canon shows it'))
        # A refusal is exit code 1 with its reason: a definition carries no section.
        code, answer = run('lease', str(b), 'Small.oddSum')
        self.assertEqual((code, answer['leased']), (1, False))
        self.assertIn('definition', answer['reason'])
        code, answer = run('wait', str(b), 'Small.oddSum', '--timeout', '0')
        self.assertEqual((code, answer['leased']), (1, False))
        code, answer = run('updates', str(b))
        self.assertEqual((code, answer['root_state']), (0, 'unresolved'))
        # A command that still finds the coordination lock held when its wait for it ends answers in the same
        # form. Another command holds the lock here, and only the length of the wait is cut, to nothing.
        with claims_lock(self.instance), patch('coordination.CLAIM_LOCK_SECONDS', 0):
            code, answer = run('lease', str(b), 'Small.root')
        self.assertEqual((code, answer), (1, {'error': 'another coordination change is still in progress; '
                                                       'run the command again'}))

    def test_a_session_stands_in_one_lease_relation(self):
        self.split()
        runner = self.runner()
        holder, mover = (self.session(runner, sid) for sid in ('sholder', 'smover'))
        self.assertTrue(lease(holder, 'Small.sumZero')['leased'])
        self.assertFalse(wait(mover, 'Small.sumZero', timeout=0)['leased'])
        self.assertTrue(lease(mover, 'Small.sumSucc')['leased'])
        self.assertEqual(lease_table(self.instance)['Small.sumZero']['queue'], [])
        # Leaving without registering frees the lease for everyone.
        release(mover, 'Small.sumSucc')
        self.assertNotIn('Small.sumSucc', lease_table(self.instance))
        # A refused wait on an element held whole keeps the place already taken on another element.
        self.assertFalse(wait(mover, 'Small.sumZero', timeout=0)['leased'])
        blocked_by = self.session(runner, 'swhole')
        self.assertTrue(take(blocked_by, 'Small.sumSucc')['registered'])
        self.assertIn('whole element', wait(mover, 'Small.sumSucc', timeout=0)['reason'])
        self.assertEqual(self.table()['Small.sumZero'], (['sholder'], ['smover']))
        self.assertIn('already holds', take(blocked_by, 'Small.sumSucc')['reason'])

    def test_whole_element_section_blocks_others_until_its_pipeline_is_done(self):
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        taken = take(a, 'Small.root')
        self.assertTrue(taken['registered'])
        self.assertEqual((taken['section']['whole'], taken['section']['statement'], taken['section']['new']), (True, None, None))
        self.assertIn('holds this whole element', lease(b, 'Small.root')['reason'])
        self.assertEqual(runner.available_elements(), [])
        pipeline = runner.state['jobs'][runner.state['sessions']['sa']['job']]['pipeline']
        runner.state['pipelines'][pipeline]['stage'] = 'done'
        runner.save()
        self.assertEqual(runner.available_elements(), ['Small.root'])
        self.assertTrue(lease(b, 'Small.root')['leased'])

    def test_a_statement_settled_under_the_lease_refuses_registration_waiting_and_leasing(self):
        self.split()
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        self.assertTrue(lease(a, 'Small.sumZero')['leased'])
        self.assertFalse(wait(b, 'Small.sumZero', timeout=0)['leased'])
        # The proof of sumZero is accepted, and it names nothing: sumZero is settled while sa holds its lease
        # and sb waits for it.
        self.replace_proof('Small.sumZero', theorem('sumZero', SUM_ZERO), 'A sum without terms is zero.', engine=runner)
        request = a / 'section.json'
        write_json(request, {'whole': False, 'statement': 'The empty sum, read from the definition.', 'reasons': {}})
        refused = section(a, 'Small.sumZero', request)
        self.assertFalse(refused['registered'])
        self.assertIn('is settled', refused['reason'])
        self.assertEqual(refused['holders'], ['sa'])  # the refusal keeps the lease for its release
        self.assertFalse((a / 'declaration.json').exists())
        waiting = wait(b, 'Small.sumZero', timeout=0)
        self.assertFalse(waiting['leased'])
        self.assertIn('is settled', waiting['reason'])
        self.assertEqual(lease_table(self.instance)['Small.sumZero']['queue'], [])  # the waiting place is given up
        self.assertIn('is settled', lease(b, 'Small.sumZero')['reason'])
        # The root's own proof is accepted too, and it rests on sumSucc, which has no proof. The root is
        # not settled, and an accepted proof alone is no reason to refuse work on its statement.
        self.assertTrue(lease(b, 'Small.root')['leased'])

    def test_a_definition_carries_no_section(self):
        runner = self.runner()
        a = self.session(runner, 'sa')
        for command in (lease, lambda session, name: wait(session, name, timeout=0)):
            refused = command(a, 'Small.oddSum')
            self.assertFalse(refused['leased'])
            self.assertIn('definition', refused['reason'])
        self.assertEqual(lease_table(self.instance), {})
        with self.assertRaisesRegex(ValueError, 'unknown element'):
            lease(a, 'Small.absent')

    def test_sections_expand_through_the_lease_and_are_not_released(self):
        runner = self.runner()
        a = self.session(runner, 'sa')
        self.assertTrue(take(a, 'Small.root', 'The identity for every even n.')['registered'])
        request = a / 'next.json'
        write_json(request, {'whole': False, 'statement': 'The identity for n = 1 and n = 3.', 'reasons': {}})
        self.assertIn('lease', section(a, 'Small.root', request)['reason'])
        self.assertTrue(lease(a, 'Small.root')['leased'])
        # Its own earlier section needs no non-overlap reason.
        self.assertTrue(section(a, 'Small.root', request)['registered'])
        self.assertTrue(lease(a, 'Small.root')['leased'])
        release(a, 'Small.root')
        self.assertEqual([s['id'] for s in read_json(a / 'declaration.json')['sections']], ['sa-1', 'sa-2'])
        self.assertEqual([s['id'] for s in board(self.instance)[0]['sections']], ['sa-1', 'sa-2'])

    def test_peers_register_within_their_pipeline_and_other_roles_cannot(self):
        runner = self.runner()
        a = self.session(runner, 'sa')
        self.assertTrue(take(a, 'Small.root', 'The identity for every even n.')['registered'])
        peer = self.peer_session(runner, 'sa', 'speer')
        # The source's sections belong to the same pipeline, so the peer may take the rest of the element.
        self.assertTrue(take(peer, 'Small.root')['registered'])
        self.assertEqual([s['session'] for s in board(self.instance)[0]['sections']], ['sa', 'speer'])
        for role in ('explore', 'formalizer', 'review', 'organizer'):
            other = self.reader('s' + role, role)
            with self.subTest(role=role), self.assertRaisesRegex(ValueError, 'only attempts and peers'):
                lease(other, 'Small.root')

    def test_a_statement_not_yet_in_the_canon_is_registered_on_the_element_it_is_aimed_at(self):
        self.split()
        runner = self.runner()
        a, b, c = (self.session(runner, sid) for sid in ('sa', 'sb', 'sc'))
        bridge = {'lean': 'theorem sumDouble (n : Nat) : oddSum (n + 2) = oddSum n + 4 * n + 4',
                  'statement': 'Two more odd numbers add 4n + 4.'}
        first = take(a, 'Small.sumSucc', new=bridge)
        self.assertTrue(first['registered'], first)
        entry = first['section']
        self.assertEqual((entry['element'], entry['whole'], entry['statement'], entry['new']),
                         ('Small.sumSucc', False, bridge['lean'], bridge))
        self.assertEqual(self.table(), {})  # registration ends the lease
        # Two attempts that hold different parts and aim at the same statement see each other on the board.
        render(self.instance, replay(self.instance), board(self.instance))
        self.assertIn(f"  Section {entry['id']} on Small.sumSucc (session sa): a new statement aimed at this element: "
                      + bridge['lean'], (self.instance / 'knowledge/board.md').read_text(encoding='utf-8'))
        # The same Lean statement is not registered twice on the element, and another one needs its reason.
        self.assertIn('exact statement', take(b, 'Small.sumSucc', new={**bridge, 'statement': 'The same, said otherwise.'})['reason'])
        other = {'lean': 'theorem sumEven (n : Nat) : oddSum (2 * n) = 4 * n * n', 'statement': 'An even number of terms.'}
        self.assertIn(entry['id'], take(b, 'Small.sumSucc', new=other, leased=True)['reason'])
        second = take(b, 'Small.sumSucc', new=other, reasons={entry['id']: 'A different statement; neither implies the other.'},
                      leased=True)
        self.assertTrue(second['registered'], second)
        # The whole element cannot be taken beside them, and a new statement is not the whole element.
        self.assertIn('whole element cannot', take(c, 'Small.sumSucc')['reason'])
        request = c / 'malformed.json'
        new_form, part_form, whole_form = ('a new statement is registered as "new"', 'a section needs its exact "statement"',
                                           'the request needs "whole" as Boolean')
        for message, wrong in ((new_form, {'new': bridge, 'whole': True}), (new_form, {'new': {'lean': bridge['lean']}}),
                               (new_form, {'new': {**bridge, 'statement': ' '}}), (new_form, {'new': 'theorem sumDouble'}),
                               (part_form, {'statement': ' '}), (whole_form, {'whole': 'yes'})):
            write_json(request, wrong)
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, message):
                section(c, 'Small.sumSucc', request)
        # The peer's assignment and the availability report carry the section like any other.
        self.assertEqual(runner.producer_sections('sa'), [{'id': entry['id'], 'element': 'Small.sumSucc', 'whole': False,
                                                          'statement': bridge['lean'], 'new': bridge}])
        self.assertEqual(runner.current_availability()['elements'],
                         {'Small.sumSucc': sorted([entry['id'], second['section']['id']]), 'Small.sumZero': []})

    def test_a_declaration_that_is_another_proof_is_held_under_the_statement_it_proves(self):
        self.ways()
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        # monoBAlt is another proof of monoB: its lease is the statement's, and so is its section.
        taken = lease(a, 'Small.monoBAlt')
        self.assertEqual((taken['leased'], taken['element']), (True, 'Small.monoB'))
        self.assertEqual(self.table(), {'Small.monoB': (['sa'], [])})
        refused = lease(b, 'Small.monoB')
        self.assertEqual((refused['leased'], refused['holders']), (False, ['sa']))
        registered = take(a, 'Small.monoBAlt', leased=True)
        self.assertEqual((registered['registered'], registered['section']['element']), (True, 'Small.monoB'))
        self.assertEqual(board(self.instance)[0]['elements'], ['Small.monoB'])
        # The whole statement is held, under either name.
        for name in ('Small.monoB', 'Small.monoBAlt'):
            self.assertIn('holds this whole element', lease(b, name)['reason'])

    def test_a_second_proof_that_remains_work_can_be_taken_on_when_the_statements_own_proof_is_accepted(self):
        # rootAlt is correct and held back, so the frontier lists it as work that remains, and replacing
        # its proof requires a section on the statement (design record, sections 5 and 9). The root's own
        # proof is accepted and the root is not settled, which is no reason to refuse the work on the other proof.
        self.ways()
        runner = self.runner()
        self.assertIn('Small.rootAlt', runner.model['remaining'])
        a = self.session(runner, 'sa')
        taken = lease(a, 'Small.rootAlt')
        self.assertTrue(taken['leased'], taken.get('reason'))
        self.assertEqual(taken['element'], 'Small.root')
        self.assertTrue(take(a, 'Small.rootAlt', 'The case split of way 2.', leased=True)['registered'])

    def test_a_second_proof_is_not_available_while_its_statement_is_held_whole(self):
        # Sections attach to the statement, so a whole section on monoB covers monoBAlt as well, and the
        # runner launches no attempt for it. The elements left are those no session holds whole.
        self.ways()
        runner = self.runner()
        a = self.session(runner, 'sa')
        self.assertTrue(take(a, 'Small.monoB')['registered'])
        available = runner.available_elements()
        self.assertNotIn('Small.monoB', available)
        self.assertNotIn('Small.monoBAlt', available)

    def test_the_availability_view_holds_only_the_work_that_remains(self):
        self.split()
        runner = self.runner()
        part = take(self.session(runner, 'sa'), 'Small.sumZero', 'The empty sum, read from the definition.')['section']
        view = availability_view(runner.model, board(self.instance, runner.state, runner.model), 3)
        # The root's proof is accepted and sumTwo is not on the way to the root; neither is work that remains.
        self.assertEqual(view, {'epoch': 3, 'elements': {'Small.sumSucc': [], 'Small.sumZero': [part['id']]}})

    def test_a_section_on_a_statement_is_listed_under_each_of_its_proofs_that_remains(self):
        # A section stands on the statement, so it occupies every proof of that statement that is work that remains.
        self.ways()
        runner = self.runner()
        remaining = runner.model['remaining']
        # monoB and its other proof monoBAlt both remain; of the root, only its other proof rootAlt does.
        self.assertLessEqual({'Small.monoB', 'Small.monoBAlt', 'Small.rootAlt'}, set(remaining))
        self.assertNotIn('Small.root', remaining)
        mono = take(self.session(runner, 'sa'), 'Small.monoB', 'Three terms, added one at a time.')['section']
        root = take(self.session(runner, 'sb'), 'Small.rootAlt', 'The case split of way 2.')['section']
        self.assertEqual((mono['element'], root['element']), ('Small.monoB', 'Small.root'))
        view = availability_view(runner.model, board(self.instance, runner.state, runner.model), 0)
        self.assertEqual(sorted(view['elements']), remaining)
        self.assertEqual({name: ids for name, ids in view['elements'].items() if ids},
                         {'Small.monoB': [mono['id']], 'Small.monoBAlt': [mono['id']], 'Small.rootAlt': [root['id']]})

    def test_messages_reach_the_recipient_inbox_and_its_updates(self):
        runner = self.runner()
        sender, recipient = (self.session(runner, sid) for sid in ('ssender', 'srecipient'))
        note = sender / 'note.md'
        # A message file can begin with a byte order mark, as Windows PowerShell writes UTF-8; it is no part of the text.
        note.write_text('Our sections meet at n = 7; I leave that case to you.', encoding='utf-8-sig')
        delivered = Path(message(sender, 'srecipient', note)['delivered'])
        self.assertEqual(delivered.resolve().parent, (recipient / 'inbox').resolve())
        with self.assertRaisesRegex(ValueError, 'unknown recipient'):
            message(sender, 'snobody', note)
        (sender / 'blank.md').write_text(' \n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'empty coordination message'):
            message(sender, 'srecipient', sender / 'blank.md')
        # A publication leaves a notice in every running session's inbox; it names no sender.
        runner.notify({'id': 'c9', 'kind': 'change', 'sequence': 1})
        runner.notify({'id': 'c1', 'kind': 'review', 'sequence': 2})
        # updates returns an inbox in the order of arrival. The names of the files say nothing of it: a message
        # has a random one, and here the later notice has the earlier name. The files are given times a second
        # apart, as files that arrived a second apart have them, so the test waits for nothing.
        start = time.time()
        arrived = {delivered.name: start, 'c9.json': start + 1, 'c1.json': start + 2}
        for folder in (recipient, sender):
            for path in (folder / 'inbox').iterdir():
                os.utime(path, (arrived[path.name], arrived[path.name]))
        received = updates(recipient)['messages']
        self.assertEqual([m.get('from') or m.get('event') for m in received], ['ssender', 'c9', 'c1'])
        self.assertEqual(received[0]['text'], 'Our sections meet at n = 7; I leave that case to you.')
        self.assertEqual([(m['event'], m['kind'], m['revision']) for m in updates(sender)['messages']],
                         [('c9', 'change', 1), ('c1', 'review', 2)])

    def test_updates_report_the_board_the_leases_and_the_work_that_remains(self):
        self.split()
        self.event('v1', 'review', comprehensive(concerns=[concern('gap', 'Small.sumTwo')]))
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        part = take(a, 'Small.sumZero', 'The empty sum, read from the definition.')['section']
        self.assertTrue(lease(b, 'Small.sumSucc')['leased'])
        runner.populate()
        peer = self.peer_session(runner, 'sa', 'speer')
        seen = updates(b)
        self.assertEqual((seen['revision'], seen['root_state']), (runner.model['sequence'], 'unresolved'))
        rows = {row['session']: row for row in seen['board']}
        self.assertEqual((rows['sa']['role'], rows['sa']['stage'], rows['sa']['elements'], rows['sa']['question']),
                         ('attempt', 'peer', ['Small.sumZero'], None))
        self.assertEqual([(s['id'], s['element'], s['whole'], s['statement'], s['session']) for s in rows['sa']['sections']],
                         [(part['id'], 'Small.sumZero', False, 'The empty sum, read from the definition.', 'sa')])
        self.assertEqual((rows['sb']['stage'], rows['sb']['elements'], rows['sb']['sections']), ('producing', [], []))
        self.assertEqual({name: [h['session'] for h in entry['holders']] for name, entry in seen['leases'].items()},
                         {'Small.sumSucc': ['sb']})
        self.assertEqual(seen['questions'], [{'id': 'q0', 'state': 'open', 'occupied_by': [], 'free': True}])
        self.assertEqual({cid: (c['targets'], c['status']) for cid, c in seen['concerns'].items()},
                         {'v1/gap': (['Small.sumTwo'], 'pending')})
        self.assertEqual([(r['status'], r['task']['concerns']) for r in seen['comprehensive_reviews']],
                         [('pending', ['v1/gap'])])
        # An attempt receives the token of what it saw: the elements that remain and the sections on each.
        snapshot = read_json(b / 'availability' / (seen['availability_snapshot'] + '.json'))
        self.assertEqual(snapshot, {'epoch': 0, 'elements': {'Small.sumSucc': [], 'Small.sumZero': [part['id']]}})
        self.assertEqual(updates(b)['availability_snapshot'], seen['availability_snapshot'])
        # Only attempts judge whether the remaining work is occupied; a peer receives no token.
        self.assertIsNone(updates(peer)['availability_snapshot'])
        self.assertFalse((peer / 'availability').exists())


class RunnerTests(ScenarioCase):
    def setUp(self):
        super().setUp()
        # The scheduling settings as installed; the shared fixture shortens them for tests that wait on them.
        installed = defaults()
        self.configure(**{key: installed[key] for key in (
            'max_sessions', 'explore_every', 'organizer_every_records', 'launch_interval', 'roles',
            'retry_seconds', 'retry_max_seconds')})

    def runner(self):
        return Runner(self.instance, self.skill)

    def ended(self, runner, role, exit_code=42):
        """A producing session that has ended with retained research material."""
        sid = 's' + role
        folder = self.session(runner, sid, role)  # as dispatch leaves it; the rest is what the CLI that ended left
        (folder / 'cli.stdout.jsonl').write_text(json.dumps(
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'A retained observation.'}}), encoding='utf-8')
        (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        (folder / 'work/notes.md').write_text('An unfinished mathematical argument.', encoding='utf-8')
        session = runner.state['sessions'][sid]
        session.update(started_at=1, exit_code=exit_code)
        runner.save()
        return sid, session, runner.state['jobs'][session['job']]

    def launched(self, runner, role):
        return [sid for sid, s in runner.active() if s['role'] == role]

    # -- retries, blocks and refusals ------------------------------------------------------------------

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
        session = session_record(sid, 'organizer', key, started_at=900, exit_code=0)
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

    def test_sessions_refused_in_flight_together_count_once_and_a_refusal_after_the_wait_counts_again(self):
        # One refusal by a provider meets every session that is in flight on the model. The wait doubles with
        # each failure that follows a wait (Runner.backoff), so the refusal of a session that was launched
        # before the block was set leaves the count as it is, and the refusal of one launched after the wait
        # had passed raises it.
        runner = self.runner()
        capacity = json.dumps({'type': 'error', 'message': 'Selected model is at capacity'})

        def refused(role, started, now):
            sid, session, _ = self.ended(runner, role)
            session['started_at'] = started
            with (runner.session_dir(sid) / 'cli.stdout.jsonl').open('a', encoding='utf-8') as stream:
                stream.write('\n' + capacity + '\n')
            with patch('runner.time.time', return_value=now):
                runner.finish(sid, session)
            block = runner.state['blocks']['model:codex/gpt-6.1-sol']
            return block['attempts'], block['until']

        self.assertEqual(refused('attempt', 1000, 2000), (1, 2060))
        self.assertEqual(refused('explore', 1500, 2010), (1, 2070))  # in flight when the block was set
        self.assertEqual(refused('formalizer', 2070, 2100), (2, 2220))  # launched once the wait had passed

    def test_interrupted_work_without_output_manifest_reaches_peer(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        runner.finish(sid, session)
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(pipeline['stage'], 'peer')
        self.assertEqual(session['status'], 'ended')
        self.assertEqual(runner.state['jobs'][pipeline['id'] + ':peer']['task']['source'], str(runner.session_dir(sid)))

    def test_a_session_whose_host_has_ended_is_collected_only_once_its_cli_has_ended_too(self):
        # The runner takes the identity of a session's CLI from the receipt that the host writes when it starts
        # a turn (process.json), and it collects the session once the host and that CLI have both ended
        # (reference/operations.md, Session hosts and continuation turns). A host can end while the CLI it
        # started still runs, as where the session is not contained. That CLI still writes the session's
        # files, so the session waits. The CLI of the receipt is first this test's own process, which is
        # alive, and then a process that is gone.
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'GO').write_bytes(b'go\n')  # the gate that dispatch opened

        def receipt(process):
            write_json(folder / 'process.json', {'process': process, 'pid': process['pid'], 'started_at': 2})

        receipt(runner.identity)
        runner.collect()
        self.assertEqual((session['status'], session['cli']), ('running', runner.identity))
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        gone = {'pid': 2 ** 22, 'birth': 'gone'}
        receipt(gone)
        runner.collect()
        self.assertEqual((session['status'], session['cli']), ('ended', gone))
        self.assertEqual(runner.state['jobs'][job['pipeline'] + ':peer']['task']['source'], str(folder))

    def test_what_each_session_used_is_recorded_when_it_is_collected_and_status_gives_the_total_of_the_run(self):
        # A call of the CLI ends with a report of what it used. Claude's `result` event gives the cost and, for
        # each model, the token counts of the whole conversation so far, the turns before it included; Codex's
        # `turn.completed` event gives token counts and no cost. When the runner collects a session it writes
        # the last report of each turn into the session's usage.json and keeps the session's totals, those of
        # the last turn that has a report, in its state, where status adds them up. The attempt has a first and
        # a resumed turn, whose stream holds two reports; the resumed turn of the explorer was ended from
        # outside and reports nothing; the formalizer ran on Codex; one more session is still running.
        runner = self.runner()

        def counts(read, written):
            return {'inputTokens': 10, 'outputTokens': written, 'cacheReadInputTokens': read,
                    'cacheCreationInputTokens': 5, 'thinkingTokens': 3, 'maxOutputTokens': 128000}

        def report(cost, **models):
            return {'type': 'result', 'is_error': False, 'total_cost_usd': cost, 'usage': {'output_tokens': 1},
                    'modelUsage': models}

        def collected(role, provider, *turns):
            sid, session, _ = self.ended(runner, role)
            session.update(model=provider + '/model', provider=provider)
            folder = runner.session_dir(sid)
            (folder / 'GO').write_bytes(b'go\n')  # the gate that dispatch opened
            for number, rows in enumerate(turns):
                stream = (folder if number == 0 else folder / 'turns' / f'{number:04d}') / 'cli.stdout.jsonl'
                stream.parent.mkdir(parents=True, exist_ok=True)
                stream.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            runner.collect()
            return session['usage'], read_json(folder / 'usage.json')

        said = {'type': 'assistant', 'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'At work.'}]}}
        first = report(1.5, main=counts(1000, 100), helper=counts(200, 20))
        last = report(2.75, main=counts(1800, 160), helper=counts(200, 20))
        used, record = collected('attempt', 'claude', [said, first], [report(2.0, main=counts(1500, 140)), last])
        tokens = {'inputTokens': 20, 'outputTokens': 180, 'cacheReadInputTokens': 2000, 'cacheCreationInputTokens': 10}
        self.assertEqual(used, {'tokens': tokens, 'cost_usd': 2.75, 'turns': 2, 'turns_without_report': 0})
        self.assertEqual(record, {'provider': 'claude', 'totals': used, 'turns': [
            {'stream': 'cli.stdout.jsonl', 'report': {'total_cost_usd': 1.5, 'modelUsage': first['modelUsage']}},
            {'stream': 'turns/0001/cli.stdout.jsonl',
             'report': {'total_cost_usd': 2.75, 'modelUsage': last['modelUsage']}}]})
        used, record = collected('explore', 'claude', [report(0.5, main=counts(300, 30))], [said])
        self.assertEqual(used, {'tokens': {'inputTokens': 10, 'outputTokens': 30, 'cacheReadInputTokens': 300,
                                           'cacheCreationInputTokens': 5},
                                'cost_usd': 0.5, 'turns': 2, 'turns_without_report': 1})
        self.assertIsNone(record['turns'][1]['report'])
        given = {'input_tokens': 700, 'cached_input_tokens': 600, 'output_tokens': 50, 'reasoning_output_tokens': 9}
        used, record = collected('formalizer', 'codex', [{'type': 'turn.completed', 'usage': given}])
        self.assertEqual(used, {'tokens': given, 'cost_usd': None, 'turns': 1, 'turns_without_report': 0})
        self.assertEqual(record['turns'], [{'stream': 'cli.stdout.jsonl', 'report': {'usage': given}}])
        self.session(runner, 'srunning')
        self.assertEqual(status(self.instance)['usage'], {
            'cost_usd': 3.25, 'sessions': 3, 'sessions_without_cost': 1, 'sessions_with_unreported_turns': 1,
            'sessions_without_record': 1,
            'tokens': {'claude': {'inputTokens': 30, 'outputTokens': 210, 'cacheReadInputTokens': 2300,
                                  'cacheCreationInputTokens': 15},
                       'codex': given}})

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

    def test_a_declaration_that_cannot_be_read_leaves_the_ended_producer_to_be_collected_again(self):
        # A peer is assigned the sections and the question that the producer's declaration records. A declaration
        # that does not parse fails that read, on which the runner ends and saves its state (Runner.run). The
        # producer is not yet marked complete in that state, so once the file is repaired the next runner
        # collects the session again and its work reaches a peer.
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        declaration = runner.session_dir(sid) / 'declaration.json'
        declaration.write_text('{not json', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Expecting property name'):
            runner.finish(sid, session)
        self.assertEqual((session['status'], job['status']), ('running', 'running'))
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'producing')
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        runner.save()
        declaration.unlink()
        recovered = self.runner()
        recovered.finish(sid, recovered.state['sessions'][sid])
        self.assertEqual(recovered.state['sessions'][sid]['status'], 'ended')
        self.assertEqual(recovered.state['jobs'][job['pipeline'] + ':peer']['status'], 'pending')

    def test_a_defect_of_the_runner_met_while_an_opt_out_is_read_is_not_charged_to_the_session(self):
        # What a session wrote wrongly in outcome.json, or in the report of availability with it, fails with a
        # ValueError, and a file that cannot be read with an OSError: the opt-out or the report is then not
        # taken, and the session is carried on without it. A KeyError there comes from the runner's own code,
        # and no file of a session causes it. It goes up to the runner's loop, which records it and ends
        # (Runner.run), and the session waits as it stood: once the defect is repaired, it is collected.
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt', exit_code=0)
        write_json(runner.session_dir(sid) / 'output/outcome.json', {'disposition': 'no_research'})
        for reader in ('runner.no_research_outcome', 'runner.reported_availability'):
            with self.subTest(reader=reader):
                with patch(reader, side_effect=KeyError('sections')), self.assertRaises(KeyError):
                    runner.finish(sid, session)
                self.assertEqual((session['status'], job['status']), ('running', 'running'))
                self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        runner.finish(sid, session)
        self.assertEqual((session['status'], session['disposition'], job['status']), ('ended', 'no_research', 'done'))
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])

    def native_profile(self, folder, rows):
        """A Codex profile holding the native transcript of the session in folder."""
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        (folder / 'work/notes.md').unlink()
        (folder / 'cli.stdout.jsonl').write_text(json.dumps({'type': 'thread.started', 'thread_id': identity}), encoding='utf-8')
        profile = self.root / 'native-profile'
        (profile / 'sessions').mkdir(parents=True)
        prompt = {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user',
                                                      'content': [{'type': 'input_text', 'text': 'Study the root.'}]}}
        (profile / 'sessions' / (identity + '.jsonl')).write_text(
            '\n'.join(json.dumps(row) for row in [prompt, *rows]), encoding='utf-8')
        return profile

    def test_native_only_research_reaches_peer(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        observation = 'A mathematical observation retained before interruption.'
        profile = self.native_profile(folder, [{'type': 'response_item', 'payload': {
            'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': observation}]}}])
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
        profile = self.native_profile(runner.session_dir(sid), [{'type': 'response_item', 'payload': {
            'type': 'reasoning', 'summary': [], 'encrypted_content': 'OPAQUE_TRANSPORT'}}])
        with patch.dict('os.environ', {'CODEX_HOME': str(profile)}):
            runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(session['status'], 'failed')
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        self.assertTrue(session['retention']['native_transcripts'])

    def without_material(self, runner):
        """An attempt that ended without any research material; its job waits to be launched again."""
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        (folder / 'work/notes.md').unlink()
        (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        return sid, session, job

    def test_a_cancelled_producer_without_research_is_relaunched_without_blocking_its_model(self):
        # kill-session ends a producer as an interruption; one that left no research material is
        # launched again. The cancellation is not a refusal or a failed launch, so the role keeps
        # its configured first model.
        runner = self.runner()
        sid, session, job = self.without_material(runner)
        (runner.session_dir(sid) / 'CANCEL').touch()
        runner.finish(sid, session)
        self.assertEqual((session['status'], job['status']), ('failed', 'pending'))
        self.assertNotIn(job['pipeline'] + ':peer', runner.state['jobs'])
        self.assertEqual(runner.state['blocks'], {})
        self.assertEqual(runner.selection('attempt')['model'], 'codex/gpt-6.1-sol')

    def test_a_producer_that_ended_without_work_counts_against_its_model(self):
        runner = self.runner()
        sid, session, job = self.without_material(runner)
        with patch('runner.time.time', return_value=1000):
            runner.finish(sid, session)
            self.assertEqual((session['status'], job['status'], job['retries']), ('failed', 'pending', 1))
            self.assertEqual(job['not_before'], 1001)  # the next model takes the job without the backoff
            self.assertEqual(runner.state['blocks']['model:codex/gpt-6.1-sol']['until'], 1060)
            self.assertEqual(runner.selection('attempt')['model'], 'claude/opus')

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

    def test_the_retry_wait_doubles_up_to_its_limit(self):
        runner = self.runner()
        self.assertEqual([runner.backoff(attempts) for attempts in (1, 2, 3, 5, 6, 30)], [60, 120, 240, 960, 1800, 1800])

    def test_standalone_processing_retry_receives_its_partial_work(self):
        runner = self.runner()
        for role, task in [('organizer', {'batch': []}), ('review', {'kind': 'comprehensive', 'concerns': []})]:
            with self.subTest(role=role):
                key = runner.enqueue(role, task)
                session = {'id': 's' + role, 'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'status': 'running'}
                runner.retry(runner.state['jobs'][key], session, 'incomplete output', availability=False)
                self.assertEqual(runner.state['jobs'][key]['task']['previous_partial_sessions'],
                                 [str(runner.session_dir('s' + role))])
                self.assertEqual(runner.state['jobs'][key]['task']['previous_error'], 'incomplete output')
                self.assertEqual(runner.state['jobs'][key]['status'], 'pending')

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

    def test_model_refusal_in_a_failed_turn_is_read_as_the_same_refusal(self):
        # retention.refusal reads the capacity message from a turn.failed error as well as from an error event.
        self.check_refusal_handoff({'type': 'turn.failed', 'error': {'message': 'Selected model is at capacity'}},
                                   'model:codex/gpt-6.1-sol', 'codex/other')

    def test_claude_model_refusal_blocks_only_that_model_and_retains_work(self):
        # Claude's typed refusal for one model blocks that model, not the claude provider.
        self.check_refusal_handoff({'type': 'assistant', 'is_api_error_message': True,
                                    'api_error': 'model_requires_usage_credits'},
                                   'model:claude/opus', 'claude/sonnet', model='claude/opus',
                                   peers=('claude/opus', 'claude/sonnet', 'codex/gpt-6.1-sol'))

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

    # -- retained work and the archive ------------------------------------------------------------------

    def test_archiver_keeps_producer_work_until_its_pipeline_is_done(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        runner.finish(sid, session)
        folder = runner.session_dir(sid)
        work, stream = folder / 'work', folder / 'cli.stdout.jsonl'
        # The producer has ended, but its peer still has to read the retained work and can open the raw conversation.
        archive_finished(self.instance)
        self.assertTrue((work / 'notes.md').is_file())
        self.assertTrue(stream.is_file())
        runner.state['pipelines'][job['pipeline']]['stage'] = 'done'
        runner.save()
        archive_finished(self.instance)
        self.assertFalse(work.exists())
        self.assertTrue((folder / 'work.tar.xz').is_file())
        # The raw conversation is packed in the same pass. The readable conversation stays, and so does the
        # receipt, which names the stream by the path it has inside raw.tar.xz.
        self.assertFalse(stream.exists())
        self.assertTrue((folder / 'raw.tar.xz').is_file())
        self.assertIn('A retained observation.', (folder / 'conversation.md').read_text(encoding='utf-8'))
        self.assertEqual(read_json(folder / 'retention.json')['streams'], ['cli.stdout.jsonl', 'cli.stderr.log'])

    def test_a_session_whose_work_cannot_be_archived_does_not_keep_the_archiver_from_the_next(self):
        # The archiver leaves in place a work/ that it cannot verify, writes the session and the error to its
        # stderr, which the runner sends to runner/archive.log, and goes on to the sessions after it
        # (reference/operations.md, Retention and archives). The work.tar.xz of the first session is no archive.
        import contextlib
        import io
        runner = self.runner()
        folders = {}
        for role in ('attempt', 'explore'):
            sid, session, job = self.ended(runner, role)
            session['status'] = 'ended'
            runner.state['pipelines'][job['pipeline']]['stage'] = 'done'
            folders[sid] = runner.session_dir(sid)
        runner.save()
        (folders['sattempt'] / 'work.tar.xz').write_bytes(b'no archive')
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(archive_finished(self.instance), 0)
        self.assertEqual([json.loads(line)['session'] for line in stderr.getvalue().splitlines()], ['sattempt'])
        self.assertTrue((folders['sattempt'] / 'work/notes.md').is_file())
        self.assertEqual((folders['sattempt'] / 'work.tar.xz').read_bytes(), b'no archive')
        self.assertFalse((folders['sexplore'] / 'work').exists())
        self.assertTrue((folders['sexplore'] / 'work.tar.xz').is_file())
        # What kept the work of the first session from being packed does not keep its raw conversation in place.
        self.assertFalse((folders['sattempt'] / 'cli.stdout.jsonl').exists())
        self.assertTrue((folders['sattempt'] / 'raw.tar.xz').is_file())

    def test_the_work_of_a_review_without_a_pipeline_is_packed_only_once_its_job_has_ended(self):
        # A comprehensive review and an organizer belong to no pipeline, and their work is packed once their own
        # job has completed (reference/operations.md, Retention and archives). Until then the job can launch
        # another session that reads the folder of this one. The review here handed its task over, and the pack
        # of the session that continues it names work/report.md of this one (context.assemble).
        runner = self.runner()
        key = runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        job = runner.state['jobs'][key]
        folder = runner.session_dir('stracing')
        (folder / 'work').mkdir(parents=True)
        (folder / 'work/report.md').write_text('Where the tracing stands.', encoding='utf-8')
        session = runner.state['sessions']['stracing'] = session_record('stracing', 'review', key)
        job.update(status='running', session='stracing')
        runner.hand_over(job, session)
        self.assertEqual((session['status'], job['status']), ('ended', 'pending'))
        archive_finished(self.instance)
        self.assertTrue((folder / 'work/report.md').is_file())
        # Once the job is done, no later session of it reads the folder, and the next pass packs the work.
        job['status'] = 'done'
        runner.save()
        archive_finished(self.instance)
        self.assertFalse((folder / 'work').exists())
        self.assertTrue((folder / 'work.tar.xz').is_file())

    def test_final_archive_request_is_dispatched_before_runner_exit(self):
        self.formal()
        runner = self.runner()
        self.assertTrue(root_solved(runner.model))
        runner.check_root()  # an earlier pass compared the settled root with the first commit; no process starts below
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
            self.assertEqual(launch.call_args.args[0][-2:], ['_archive', str(self.instance)])

    def test_occupancy_survives_producer_exit(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        self.assertTrue(take(runner.session_dir(sid), 'Small.root')['registered'])
        for stage in ('producing', 'peer'):
            if stage == 'peer':
                runner.finish(sid, session)
            rows = board(self.instance, runner.state)
            self.assertEqual(rows[0]['elements'], ['Small.root'])
            self.assertEqual(rows[0]['stage'], stage)
            render(self.instance, replay(self.instance), rows)
            visible = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
            self.assertIn(f'producer: {sid}', visible)
            self.assertIn(f'· {stage} · elements: Small.root', visible)

    def test_the_board_view_is_drawn_again_when_a_lease_changes_hands_and_not_on_every_pass(self):
        # The runner looks at the board on every pass (Runner.refresh) and renders the views only when the
        # pipelines, the holders and waiters of the leases, the revision or the comprehensive reviews have changed.
        runner = self.runner()
        a, b = (self.session(runner, sid) for sid in ('sa', 'sb'))
        view = self.instance / 'knowledge/board.md'
        research = [self.instance / 'knowledge' / name for name in ('index.md', 'state.json')]
        with patch('runner.render', wraps=render) as drawn:
            runner.refresh()
            runner.refresh()
            self.assertEqual(drawn.call_count, 1)
            # index.md and state.json hold the research alone, which no change of the board alters. A runner's
            # first refresh writes them, and a later one neither builds nor reads them. They are taken away
            # here, so that a refresh which handled them would be seen to put them back.
            for path in research:
                path.unlink()
            self.assertTrue(lease(a, 'Small.root')['leased'])
            runner.refresh()
            runner.refresh()
            self.assertEqual(drawn.call_count, 2)
            self.assertIn('- Small.root · lease: sa · waiting: (none)', view.read_text(encoding='utf-8'))
            self.assertFalse(wait(b, 'Small.root', timeout=0)['leased'])
            runner.refresh()
            runner.refresh()
            self.assertEqual(drawn.call_count, 3)
            self.assertIn('- Small.root · lease: sa · waiting: sb', view.read_text(encoding='utf-8'))
            self.assertFalse(any(path.exists() for path in research))
        self.runner().refresh()
        self.assertTrue(all(path.is_file() for path in research))

    def test_peer_task_carries_the_producers_sections(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        taken = take(runner.session_dir(sid), 'Small.root', 'The identity for every even n.')
        self.assertTrue(taken['registered'])
        runner.finish(sid, session)
        task = runner.state['jobs'][job['pipeline'] + ':peer']['task']
        self.assertEqual(task['sections'], [{'id': taken['section']['id'], 'element': 'Small.root', 'whole': False,
                                             'statement': 'The identity for every even n.', 'new': None}])
        self.assertEqual((task['source_role'], task['element'], task['question']), ('attempt', None, None))

    def test_the_sections_of_a_failed_peer_stay_with_its_pipeline_under_the_peer_that_replaces_it(self):
        # A peer can register sections of its own. When it fails, its job launches another peer, which takes the
        # pipeline's peer slot; what the failed peer registered still occupies its element until review ends.
        runner = self.runner()
        producer = self.session(runner, 'sa')
        self.assertTrue(take(producer, 'Small.root', 'The identity for every even n.')['registered'])
        pid = runner.state['jobs'][runner.state['sessions']['sa']['job']]['pipeline']
        runner.state['pipelines'][pid]['stage'] = 'peer'
        key = runner.enqueue('peer', {'source': str(producer), 'source_role': 'attempt'}, pid, pid + ':peer')
        job = runner.state['jobs'][key]
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(key))
            first = job['session']
            self.assertTrue(take(runner.session_dir(first), 'Small.root')['registered'])
            runner.retry(job, runner.state['sessions'][first], 'incomplete output', availability=False)
            self.assertTrue(runner.dispatch(key))
        second = job['session']
        pipeline = runner.state['pipelines'][pid]
        self.assertEqual((pipeline['previous_peers'], pipeline['peer']), ([first], second))
        self.assertEqual(job['task']['previous_partial_sessions'], [str(runner.session_dir(first))])
        [row] = board(self.instance, runner.state)
        self.assertEqual([(s['session'], s['whole']) for s in row['sections']], [('sa', False), (first, True)])
        self.assertEqual(runner.available_elements(), [])

    # -- a publication that the next runner completes ----------------------------------------------------

    def test_approaches_moved_before_a_runner_ended_are_taken_out_of_the_summary_by_the_next_runner(self):
        # A publication moves the approaches tried on a statement whose proof is accepted to its history, and
        # then writes the summary of the records again, from which the research state takes the approaches of
        # each element. A runner that ended between the two left the summary listing an entry that is gone.
        # The runner that completes the publication finds nothing to move, and writes the summary all the same.
        self.direct()  # the root's proof is accepted
        runner = self.runner()
        folder = self.candidate(approaches={'Small/root/induction.md': (
            '---\ntitle: Induction on the number of terms\nsessions: s-early\n---\n'
            '## Idea\n\nCompare the sum for n + 1 with the sum for n.\n\n'
            '## Where it stops\n\nThe comparison is not carried out.\n')})
        summaries = []

        def ended_at_the_second_summary(path, value):
            if Path(path).name == 'records.json':
                summaries.append(value)
                if len(summaries) == 2:  # the first follows the installation of the change, the second the move
                    raise RuntimeError('simulated end of the runner')
            return write_json(path, value)

        with patch('runner.write_json', side_effect=ended_at_the_second_summary), \
                self.assertRaisesRegex(RuntimeError, 'simulated'):
            self.publish(folder, engine=runner, expect=False)
        canon = Canon(self.instance)
        self.assertFalse((canon.approaches / 'Small/root').exists())
        self.assertEqual(read_json(canon.root / 'records.json')['Small.root']['approaches'], ['induction'])
        recovered = self.runner()
        self.drain(recovered)
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(read_json(canon.root / 'records.json')['Small.root']['approaches'], [])
        self.assertEqual(recovered.model['elements']['Small.root']['approaches'], [])
        self.assertEqual([p.name for p in (canon.history / 'Small/root').glob('*-approaches/*.md')], ['induction.md'])

    def test_a_review_refused_at_publication_while_another_session_is_collected_is_left_alone_in_that_pass(self):
        # A pass collects the sessions that were active when it began (Runner.collect), and collecting a review
        # carries the publication queue forward (Runner.finish). The publication of a review that waited in the
        # queue can so end in the middle of a pass. Here it is refused: the candidate replaces a proof that
        # another publication replaced, the review job is cancelled and a replacement peer receives the work.
        # The pass then leaves that review alone. Collected as a session that has just ended, it would be
        # queued again, under a job that is cancelled. Three sessions stand in the order of their launch: a
        # comprehensive review that has ended and is not collected yet, the review of a note, which the pass
        # publishes first, and the review of the candidate, which was prepared before the root's proof changed.
        runner = self.runner()
        task = {'kind': 'comprehensive', 'concerns': [], 'conflicts': []}
        key = runner.enqueue('review', task)
        tracing = runner.session_dir('stracing')
        (tracing / 'output').mkdir(parents=True)
        write_json(tracing / 'input.json', {'instance': str(self.instance), 'session': 'stracing', 'role': 'review',
                                            'pipeline': None, 'task': task})
        write_json(tracing / 'output/assessment.json', comprehensive(concerns=[concern('gap', 'Small.root')]))
        (tracing / 'output/feedback.md').write_text('What the tracing found.', encoding='utf-8')
        (tracing / 'cli.stdout.jsonl').write_text(json.dumps(
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Tracing done.'}}), encoding='utf-8')
        (tracing / 'cli.stderr.log').write_text('', encoding='utf-8')
        (tracing / 'GO').write_bytes(b'go\n')  # the gate that dispatch opened
        runner.state['sessions']['stracing'] = session_record('stracing', 'review', key, exit_code=0)
        runner.state['jobs'][key].update(status='running', session='stracing')
        late = self.candidate(replace={'Small.root': self.root_text(proof='cases n <;> sorry')},
                              records={'Small/root.md': self.root_record('By cases on $n$.')})
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.',
                           engine=runner)
        note = self.candidate(understanding={'q0.md': 'The sum grows by one odd number at a time.\n'})
        with patch.object(self, 'drain'):  # the two are queued and carried no further
            self.publish(note, role='explore', question='q0', engine=runner, expect=False)
            self.publish(late, engine=runner, expect=False)
        queued = runner.state['publish_queue'][-1]
        review, job = runner.state['sessions'][queued['session']], runner.state['jobs'][queued['job']]
        # What the runner had recorded of the review when it queued its work (Runner.finish).
        review.update(exit_code=0, retained=True, retention={'cli_activity': True, 'native_activity': False})
        runner.collect()
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual((review['status'], job['status'], pipeline['stage']), ('failed', 'cancelled', 'peer'))
        self.assertIn('could not be published on the current canon', job['last_error'])
        # The comprehensive review was collected in the pass and waits for its turn; nothing else is queued.
        self.assertEqual(runner.state['publish_queue'], [{'session': 'stracing', 'job': key, 'kind': 'review'}])
        self.drain(runner)
        self.assertEqual((runner.state['sessions']['stracing']['status'], review['status']), ('integrated', 'failed'))
        self.assertEqual([j['status'] for j in runner.state['jobs'].values()
                          if j['role'] == 'peer' and j['pipeline'] == pipeline['id']], ['pending'])

    # -- launch spacing, exploration requests and priority ----------------------------------------------

    def test_attempts_and_explorations_share_one_spacing_and_a_queued_element_launches_none(self):
        self.split()  # sumZero and sumSucc are both available
        runner = self.runner()
        self.assertEqual(runner.settings['launch_interval'], 180)
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
            runner.schedule()
            self.assertEqual((len(self.launched(runner, 'attempt')), len(self.launched(runner, 'explore'))), (1, 0))
            # The attempt launch requested an exploration, which waits for the same interval.
            self.assertTrue(runner.state['explore_requested'])
            # The spacing survives a restart.
            runner = self.runner()
            runner.schedule()
            self.assertEqual((len(self.launched(runner, 'attempt')), len(self.launched(runner, 'explore'))), (1, 0))
            runner.state['last_launch'] -= 181
            runner.schedule()
            # The requested exploration goes ahead of the next attempt and restarts the interval.
            self.assertEqual((len(self.launched(runner, 'attempt')), len(self.launched(runner, 'explore'))), (1, 1))
            self.assertFalse(runner.state['explore_requested'])
            runner.state['last_launch'] -= 181
            runner.schedule()
            attempts = self.launched(runner, 'attempt')
            self.assertEqual((len(attempts), len(self.launched(runner, 'explore'))), (2, 1))
        first, second = (runner.session_dir(sid) for sid in attempts)
        self.assertTrue(lease(first, 'Small.sumZero')['leased'])
        self.assertEqual(runner.available_elements(), ['Small.sumSucc', 'Small.sumZero'])
        self.assertFalse(wait(second, 'Small.sumZero', timeout=0)['leased'])
        # Another attempt launched for an element with a waiting session would only lengthen its queue.
        self.assertEqual(runner.available_elements(), ['Small.sumSucc'])

    def test_waiting_attempt_and_exploration_jobs_also_keep_the_shared_spacing(self):
        # Pending or retried jobs launch from dispatch_pending(), not schedule(); they wait too.
        self.split()
        runner = self.runner()
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(runner.producer('attempt')))
            explore = runner.producer('explore')
            runner.dispatch_pending()
            self.assertEqual(runner.state['jobs'][explore]['status'], 'pending')
            runner.state['last_launch'] -= 181
            runner.dispatch_pending()
            self.assertEqual(runner.state['jobs'][explore]['status'], 'running')
            attempt = runner.producer('attempt')
            runner.dispatch_pending()
            self.assertEqual(runner.state['jobs'][attempt]['status'], 'pending')
            runner.state['last_launch'] -= 181
            runner.dispatch_pending()
            self.assertEqual(runner.state['jobs'][attempt]['status'], 'running')
        self.assertEqual((len(self.launched(runner, 'attempt')), len(self.launched(runner, 'explore'))), (2, 1))

    def test_periodic_exploration_survives_restart_and_coalesces_requests(self):
        runner = self.runner()
        # Every attempt launch requests exploration by default; a longer cadence shows the counting.
        self.assertEqual(runner.settings['explore_every'], 1)
        runner.settings['explore_every'] = 3
        write_json(self.instance / 'settings.json', runner.settings)

        def launch_attempt():
            # The launch alone counts; whether the attempt later registers a section does not matter.
            self.assertTrue(runner.dispatch(runner.producer('attempt')))

        self.assertIs(runner.state['explore_requested'], False)
        with patch('runner.subprocess.Popen'), patch('runner.process_identity', return_value=None):
            for expected in (1, 2):
                launch_attempt()
                self.assertEqual(runner.state['attempt_launches'], expected)
                self.assertIs(runner.state['explore_requested'], False)

            runner = self.runner()
            self.assertEqual(runner.state['attempt_launches'], 2)
            self.assertIs(runner.state['explore_requested'], False)
            for expected in (3, 4, 5, 6):
                launch_attempt()
                self.assertEqual(runner.state['attempt_launches'], expected)
                self.assertIs(runner.state['explore_requested'], True)

            runner = self.runner()
            self.assertEqual(runner.state['attempt_launches'], 6)
            self.assertIs(runner.state['explore_requested'], True)
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            self.assertEqual(runner.state['attempt_launches'], 6)
            self.assertIs(runner.state['explore_requested'], False)
            launch_attempt()
            self.assertEqual(runner.state['attempt_launches'], 7)
            self.assertIs(runner.state['explore_requested'], False)

    def test_review_waiting_for_a_model_does_not_hold_attempts_while_slots_are_free(self):
        # A freed slot goes to waiting review work first through the priority order, which the
        # priority test below checks; a review that waits for a model rather than for capacity
        # leaves the free slots to attempts.
        runner = self.runner()
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        runner.settings['roles']['review'] = [{'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'}]
        runner.state['blocks']['provider:codex'] = {'until': 10**12}
        review = runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual(runner.state['jobs'][review]['status'], 'pending')
        self.assertIn('attempt', [s['role'] for _, s in runner.active()])

    def test_waiting_organizer_does_not_block_attempt_while_another_organizer_runs(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 3
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        first = runner.enqueue('organizer', {})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(first))
            second = runner.enqueue('organizer', {})
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            runner.schedule()
        self.assertEqual(runner.state['jobs'][first]['status'], 'running')
        self.assertEqual(runner.state['jobs'][second]['status'], 'pending')
        self.assertCountEqual([s['role'] for _, s in runner.active()], ['organizer', 'explore', 'attempt'])

    def test_waiting_comprehensive_review_does_not_block_attempt_while_another_runs(self):
        # As for organizers: the waiting review takes the slot the running one frees, ahead of any
        # attempt, so holding attempts back for it would leave capacity idle without serving it sooner.
        runner = self.runner()
        runner.settings['max_sessions'] = 3
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        task = {'kind': 'comprehensive', 'concerns': [], 'conflicts': []}
        first = runner.enqueue('review', dict(task))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(first))
            second = runner.enqueue('review', dict(task))
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            runner.schedule()
        self.assertEqual(runner.state['jobs'][first]['status'], 'running')
        self.assertEqual(runner.state['jobs'][second]['status'], 'pending')
        self.assertCountEqual([s['role'] for _, s in runner.active()], ['review', 'explore', 'attempt'])

    def test_a_requested_comprehensive_review_waits_while_another_runs(self):
        # Comprehensive reviews launch one at a time, as organizers do.
        runner = self.runner()
        task = {'kind': 'comprehensive', 'concerns': [], 'conflicts': []}
        first, second = runner.enqueue('review', dict(task)), runner.enqueue('review', dict(task))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
            self.assertEqual(runner.state['jobs'][first]['status'], 'running')
            self.assertEqual(runner.state['jobs'][second]['status'], 'pending')
            # Once the running review has finished, the waiting one launches.
            runner.state['jobs'][first]['status'] = 'done'
            runner.dispatch_pending()
        self.assertEqual(runner.state['jobs'][second]['status'], 'running')

    def test_ready_jobs_dispatch_in_the_complete_role_priority_order(self):
        self.half()  # sumZero waits for its formal proof, and sumSucc remains for the attempt
        runner = self.runner()
        runner.settings['max_sessions'] = 1
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        before = len(runner.state['sessions'])
        # Reverse insertion order makes dictionary order an incorrect scheduler.
        runner.producer('attempt')
        runner.producer('explore')
        runner.enqueue('organizer', {})
        runner.producer('formalizer', {'element': 'Small.sumZero', 'previous_changes': []})
        runner.enqueue('peer', {'source': str(self.instance / 'sessions/source'), 'source_role': 'attempt'})
        runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            for expected in ('review', 'peer', 'formalizer', 'organizer', 'explore', 'attempt'):
                with self.subTest(role=expected):
                    runner.dispatch_pending()
                    active = runner.active()
                    self.assertEqual([s['role'] for _, s in active], [expected])
                    sid, session = active[0]
                    self.assertEqual(read_json(runner.session_dir(sid) / 'input.json')['role'], expected)
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
        self.assertEqual(len(runner.state['sessions']) - before, 6)
        self.assertTrue(all(j['status'] == 'done' for j in runner.state['jobs'].values()))
        # The last launch, the attempt, requests the next exploration (explore_every 1).
        self.assertTrue(runner.state['explore_requested'])

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

    def test_exploration_in_peer_keeps_its_question_and_does_not_hold_a_pending_attempt(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 1
        previous = runner.producer('explore')
        runner.state['jobs'][previous]['status'] = 'done'
        pipeline = runner.state['pipelines'][runner.state['jobs'][previous]['pipeline']]
        pipeline.update(stage='peer', producer='sprevious')
        runner.session_dir('sprevious').mkdir()
        write_json(runner.session_dir('sprevious') / 'declaration.json',
                   {'question': {'id': 'q0', 'at': 1, 'by': 'runner'}, 'at': 1})
        attempt = runner.producer('attempt')
        runner.state['explore_requested'] = True
        # The only question is occupied through peer and review, so no explorer can launch;
        # the request stays in force and the attempt is not held for it.
        self.assertFalse(runner.question_slot())
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual([s['role'] for _, s in runner.active()], ['attempt'])
        self.assertEqual(runner.state['jobs'][attempt]['status'], 'running')
        self.assertEqual(pipeline['stage'], 'peer')
        self.assertTrue(runner.state['explore_requested'])
        self.assertEqual(sum(p['role'] == 'explore' and p['stage'] != 'done'
                             for p in runner.state['pipelines'].values()), 1)

    # -- attempts launch only where an element can still be taken on ------------------------------------

    def test_attempt_retry_respects_lease_queue_and_whole_element_occupancy(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 3
        sid, session, job = self.without_material(runner)
        runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        job['not_before'] = 0
        runner.state['blocks'].clear()
        holder = self.session(runner, 'sholder')
        waiter = self.session(runner, 'swaiter')
        self.assertTrue(lease(holder, 'Small.root')['leased'])
        self.assertTrue(wait(waiter, 'Small.root', timeout=0)['waiting'])
        exploration = runner.producer('explore')
        runner.state['jobs'][exploration]['status'] = 'done'
        pipeline = runner.state['pipelines'][runner.state['jobs'][exploration]['pipeline']]
        pipeline.update(stage='peer', producer='sprevious')
        runner.save()
        self.assertEqual(runner.model['remaining'], ['Small.root'])
        self.assertLess(len(runner.active()), runner.settings['max_sessions'])
        self.assertTrue(runner.launch_due())
        self.assertIsNotNone(runner.selection('attempt'))
        before = set(runner.state['sessions'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertEqual(runner.available_elements(), [])
            runner.dispatch_pending()
            self.assertEqual(job['status'], 'pending')
            self.assertEqual(set(runner.state['sessions']), before)
            release(waiter, 'Small.root')
            self.assertTrue(take(holder, 'Small.root', leased=True)['registered'])
            holder_job = runner.state['sessions']['sholder']['job']
            holder_pipeline = runner.state['pipelines'][runner.state['jobs'][holder_job]['pipeline']]
            holder_pipeline['stage'] = 'peer'
            runner.save()
            self.assertEqual(runner.available_elements(), [])
            runner.dispatch_pending()
            self.assertEqual(job['status'], 'pending')
            self.assertEqual(set(runner.state['sessions']), before)
            holder_pipeline['stage'] = 'done'
            runner.save()
            self.assertEqual(runner.available_elements(), ['Small.root'])
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        self.assertEqual(set(runner.state['sessions']) - before, {job['session']})

    def test_attempt_retry_waits_when_no_work_remains_for_the_root(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 2
        sid, session, job = self.without_material(runner)
        runner.finish(sid, session)
        self.assertEqual(job['status'], 'pending')
        job['not_before'] = 0
        runner.state['blocks'].clear()
        runner.save()
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.', engine=runner)
        self.assertEqual((runner.model['root_state'], runner.model['remaining']), ('informal_proved', []))
        self.assertFalse(runner.state['complete'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            before = set(runner.state['sessions'])
            runner.dispatch_pending()
        self.assertEqual(set(runner.state['sessions']), before)
        self.assertEqual(job['status'], 'pending')
        self.assertEqual([s['role'] for _, s in runner.active()], ['explore'])

    def test_spare_capacity_explores_and_formalizes_when_no_work_remains_for_the_root(self):
        # Spare capacity requests exploration whether elements are occupied or none remains.
        self.direct()
        runner = self.runner()
        runner.settings['max_sessions'] = 2
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertCountEqual([s['role'] for _, s in runner.active()], ['formalizer', 'explore'])
        self.assertFalse(any(p['role'] == 'attempt' and p['stage'] != 'done' for p in runner.state['pipelines'].values()))
        self.assertFalse(runner.state['explore_requested'])

    def test_a_solved_root_cancels_waiting_attempts_and_explorations(self):
        self.formal()
        runner = self.runner()
        attempt, explore = runner.producer('attempt'), runner.producer('explore')
        runner.check_root()  # an earlier pass compared the settled root with the first commit; no process starts below
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.tick()
        self.assertTrue(runner.state['complete'])
        self.assertEqual([runner.state['jobs'][key]['status'] for key in (attempt, explore)], ['cancelled', 'cancelled'])
        self.assertEqual(runner.active(), [])
        self.assertTrue(all(p['stage'] == 'done' for p in runner.state['pipelines'].values()))

    # -- organizer batches -----------------------------------------------------------------------------

    def test_organizer_batch_is_the_changes_published_and_not_yet_organized(self):
        self.configure(organizer_every_records=2)
        first, _ = self.note('The sum grows by one odd number at a time.')
        runner = self.runner()
        runner.populate()
        # The organizer is due after the configured number of changes not yet in a batch.
        self.assertFalse(any(j['role'] == 'organizer' for j in runner.state['jobs'].values()))
        second, _ = self.note('Each step completes a square.', engine=runner)
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'organizer')
        runner.populate()
        self.assertEqual(sum(j['role'] == 'organizer' for j in runner.state['jobs'].values()), 1)
        runner.session_dir('sorganizer').mkdir()
        runner.make_pack('sorganizer', job)
        self.assertEqual(job['task']['batch'], [first, second])
        self.assertEqual(read_json(runner.session_dir('sorganizer') / 'input.json')['task']['batch'], [first, second])
        # A change that arrives while the organizer works belongs to the next batch.
        third, _ = self.note('The squares are consecutive.', engine=runner)
        job['status'] = 'done'
        self.organize(batch=job['task']['batch'], engine=runner)
        self.assertEqual(runner.model['organized'], sorted([first, second]))
        self.assertEqual([cid for cid in runner.model['changes'] if cid not in runner.model['organized']], [third])
        runner.populate()
        self.assertFalse(any(j['role'] == 'organizer' and j['status'] == 'pending' for j in runner.state['jobs'].values()))

    def test_organizer_freezes_arrivals_at_launch_not_queue_time(self):
        self.configure(organizer_every_records=1)
        first, _ = self.note('The sum grows by one odd number at a time.')
        runner = self.runner()
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'organizer')
        self.assertEqual(job['task'], {})
        second, _ = self.note('Each step completes a square.', engine=runner)
        runner.session_dir('sorganizer').mkdir()
        runner.make_pack('sorganizer', job)
        self.assertEqual(job['task']['batch'], [first, second])
        third, _ = self.note('The squares are consecutive.', engine=runner)
        runner.session_dir('sretry').mkdir()
        runner.make_pack('sretry', job)
        self.assertEqual(job['task']['batch'], [first, second])

    # -- formalizers ------------------------------------------------------------------------------------

    def formalizers(self, runner):
        return [(p['element'], p['stage']) for p in runner.state['pipelines'].values() if p['role'] == 'formalizer']

    def test_a_formalizer_is_sent_for_each_statement_ready_for_its_formal_proof(self):
        self.half()
        runner = self.runner()
        runner.populate()
        runner.populate()
        # sumTwo is settled, and the root does not rest on it; the root itself is not settled yet.
        self.assertEqual(self.formalizers(runner), [('Small.sumZero', 'producing')])
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'formalizer')
        self.assertEqual(job['task'], {'element': 'Small.sumZero', 'previous_changes': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        # The assigned element is the formalizer's whole section; it registers nothing itself.
        declared = read_json(runner.session_dir(job['session']) / 'declaration.json')['sections']
        self.assertEqual([(s['id'], s['element'], s['whole'], s['statement'], s['new']) for s in declared],
                         [(job['session'] + '-1', 'Small.sumZero', True, None, None)])
        row = next(r for r in board(self.instance, runner.state) if r['role'] == 'formalizer')
        self.assertEqual((row['elements'], row['stage']), (['Small.sumZero'], 'producing'))
        self.assertEqual(read_json(runner.session_dir(job['session']) / 'input.json')['task']['element'], 'Small.sumZero')

    def test_a_formalizer_whose_element_is_no_longer_ready_is_cancelled_at_dispatch(self):
        self.half()
        runner = self.runner()
        runner.populate()
        ready = next(j for j in runner.state['jobs'].values() if j['role'] == 'formalizer')
        # A job for a settled statement the root does not rest on, and one whose proof a finding withdrew.
        stray = runner.producer('formalizer', {'element': 'Small.sumTwo', 'previous_changes': []})
        self.event('v1', 'review', comprehensive([finding('The empty sum was miscounted.', invalidates=['Small.sumZero'])]))
        runner.model = replay(self.instance)
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual((runner.state['jobs'][stray]['status'], ready['status']), ('cancelled', 'cancelled'))
        self.assertEqual(sorted(self.formalizers(runner)), [('Small.sumTwo', 'done'), ('Small.sumZero', 'done')])
        self.assertFalse(self.launched(runner, 'formalizer'))
        runner.populate()
        self.assertFalse([j for j in runner.state['jobs'].values() if j['role'] == 'formalizer' and j['status'] == 'pending'])

    def test_a_formalizer_of_another_proof_holds_the_statement_that_proof_proves(self):
        second_proof(self)  # the root is settled through rootAlt alone, which has no formal proof
        runner = self.runner()
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'formalizer')
        self.assertEqual(job['task'], {'element': 'Small.rootAlt', 'previous_changes': []})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        # Sections attach to the statement, so the formalizer's whole section is on the root.
        declared = read_json(runner.session_dir(job['session']) / 'declaration.json')['sections']
        self.assertEqual([(s['element'], s['whole']) for s in declared], [('Small.root', True)])
        row = next(r for r in board(self.instance, runner.state) if r['role'] == 'formalizer')
        self.assertEqual(row['elements'], ['Small.root'])

    def test_one_formalizer_at_a_time_holds_a_statement_whichever_of_its_proofs_is_to_be_formalized(self):
        # The root's own proof and rootAlt both settle the root. A finding withdraws the own proof, so rootAlt is
        # the proof to formalize, and its formalizer holds the root whole.
        self.direct()
        publish_second_proof(self)
        self.event('v1', 'review', comprehensive([finding('The induction step fails.', invalidates=['Small.root'])]))
        runner = self.runner()
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'formalizer')
        self.assertEqual(job['task']['element'], 'Small.rootAlt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        # A later review restores the own proof, which comes first again. The formalizer at work still holds the
        # root whole, so no second formalizer is sent to the same statement.
        self.event('v2', 'review', comprehensive([finding('The induction step holds.', validates=['Small.root'])]))
        runner.model = replay(self.instance)
        self.assertEqual(formalizable(runner.model), ['Small.root'])
        runner.populate()
        self.assertEqual(self.formalizers(runner), [('Small.rootAlt', 'producing')])
        # The formalizer's conversation fills, and it hands its task over. The job is work under way and no new
        # launch: the session that continues it is launched although rootAlt is no longer the proof a new formalizer
        # would be given, it holds the root under the section its predecessor held, and no second formalizer is sent.
        first = job['session']
        held = read_json(runner.session_dir(first) / 'declaration.json')['sections']
        write_json(runner.session_dir(first) / 'end-check.json',
                   {'resumptions': 0, 'authorization': {'basis': 'handed_over'}})
        runner.finish(first, runner.state['sessions'][first])
        self.assertEqual((job['status'], job['task']['continues']), ('pending', [str(runner.session_dir(first))]))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(job['status'], 'running')
        self.assertNotEqual(job['session'], first)
        self.assertEqual(read_json(runner.session_dir(job['session']) / 'declaration.json')['sections'], held)
        runner.populate()
        self.assertEqual(self.formalizers(runner), [('Small.rootAlt', 'producing')])

    def test_the_root_waits_for_the_formal_proofs_of_what_its_proof_names(self):
        self.proved()
        runner = self.runner()
        runner.populate()
        self.assertEqual(sorted(self.formalizers(runner)), [('Small.sumSucc', 'producing'), ('Small.sumZero', 'producing')])

    def test_formalization_has_no_round_cap_and_carries_the_earlier_changes(self):
        self.direct()
        runner = self.runner()
        for i in range(30):
            runner.state['pipelines']['old' + str(i)] = {'id': 'old' + str(i), 'role': 'formalizer', 'stage': 'done',
                                                         'element': 'Small.root', 'record': 'c' + str(i)}
        runner.state['pipelines']['other'] = {'id': 'other', 'role': 'formalizer', 'stage': 'done',
                                              'element': 'Small.sumZero', 'record': 'cother'}
        runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'formalizer' and j['status'] == 'pending')
        self.assertEqual(job['task'], {'element': 'Small.root', 'previous_changes': ['c' + str(i) for i in range(30)]})

    # -- comprehensive review ---------------------------------------------------------------------------

    def test_published_comprehensive_review_is_not_reassigned_for_its_open_concern(self):
        self.event('v1', 'review', comprehensive(concerns=[concern('gap', 'Small.root')]))
        runner = self.runner()
        runner.populate()
        runner.populate()
        [job] = comprehensive_jobs(runner)
        self.assertEqual((job['task']['concerns'], job['task']['conflicts']), (['v1/gap'], []))
        # The review could not settle the concern, so the concern itself stays open.
        publish_comprehensive(runner, job, comprehensive())
        self.assertEqual(runner.model['concerns']['v1/gap']['status'], 'pending')
        self.assertEqual(runner.state['processed_concerns'], ['v1/gap'])
        runner.populate()
        self.assertEqual([j['id'] for j in comprehensive_jobs(runner)], [job['id']])
        # A concern raised afterwards is a new cause.
        self.event('v2', 'review', comprehensive(concerns=[concern('later', 'Small.root')]))
        runner.model = replay(self.instance)
        runner.populate()
        self.assertEqual([j['task']['concerns'] for j in comprehensive_jobs(runner) if j['status'] == 'pending'],
                         [['v2/later']])

    def test_a_cleared_concern_is_not_assigned(self):
        self.event('v1', 'review', comprehensive(concerns=[concern('gap', 'Small.root')]))
        self.event('v2', 'review', comprehensive([finding('The case holds.', status='cleared', concerns=['v1/gap'])]))
        runner = self.runner()
        runner.populate()
        self.assertEqual(comprehensive_jobs(runner), [])

    def test_candidate_review_withdrawal_without_a_named_concern_opens_a_comprehensive_review(self):
        self.direct()
        folder = self.candidate(understanding={'q0.md': 'The induction was read again.\n'})
        assessment = self.verdicts(folder)
        assessment['findings'] = [finding('The case n = 0 fails.', invalidates=['Small.root'])]
        change, _ = self.publish(folder, assessment, role='explore', question='q0')
        model = replay(self.instance)
        self.assertEqual((model['root_state'], model['elements']['Small.root']['standing']), ('unresolved', 'not_confirmed'))
        raised = model['concerns'][change + '/withdrawal-0']
        self.assertEqual((raised['targets'], raised['status'], raised['source']), (['Small.root'], 'pending', change))
        runner = self.runner()
        runner.populate()
        self.assertEqual([j['task']['concerns'] for j in comprehensive_jobs(runner)], [[change + '/withdrawal-0']])
        # A comprehensive review's own withdrawal ends that tracing; it does not open another one.
        self.event('v1', 'review', comprehensive([finding('Traced.', invalidates=['Small.root'])]))
        self.assertEqual([cid for cid in replay(self.instance)['concerns'] if cid.startswith('v1/')], [])

    # -- operator commands ------------------------------------------------------------------------------

    def test_restart_broker_admits_sessions_held_behind_stop(self):
        runner = self.runner()
        for sid in ('sheld', 'sturn'):
            runner.state['sessions'][sid] = {'id': sid, 'role': 'attempt', 'status': 'running', 'cli': None}
            runner.session_dir(sid).mkdir(parents=True, exist_ok=True)
        write_json(runner.session_dir('sheld') / 'end-check.json', {'status': 'waiting_dispatch'})
        runner.save()
        # The broker's own state file, which broker_status reads; no broker process is alive.
        compiles = self.instance / 'runner/lean/state.json'
        compiles.parent.mkdir(parents=True, exist_ok=True)
        write_json(compiles, {'jobs': {'jrun': {'id': 'jrun', 'status': 'running', 'session': 'sheld'}}})

        def refused(reason):
            self.assertEqual(main(['restart-broker', str(self.instance)]), 1)
            self.assertIn(reason, json.loads(shown.call_args.args[0])['error'])

        with patch('lean_broker.ensure_broker', return_value={'started': True}) as begin, \
                patch('builtins.print') as shown:
            refused('stop new dispatch')
            (self.instance / 'control/STOP').touch()
            # A session without a held turn is still an active turn and blocks replacement.
            refused('let active CLI turns finish')
            # A session whose work waits for publication has no CLI turn, and the refusal says what it waits for.
            runner.state['sessions']['sturn']['status'] = 'publishing'
            runner.save()
            refused('let the publications under way finish')
            runner.state['sessions']['sturn']['status'] = 'ended'
            runner.save()
            # A compile still running blocks it as well.
            refused('Lean jobs')
            begin.assert_not_called()
            write_json(compiles, {'jobs': {}})
            self.assertEqual(main(['restart-broker', str(self.instance)]), 0)
        begin.assert_called_once()
        self.assertEqual(json.loads(shown.call_args.args[0])['held_sessions'], ['sheld'])

    def test_restart_broker_ends_the_live_broker_and_starts_another(self):
        # A broker of the instance is alive, as it is after any compile; it is started here as a client starts one.
        paths = Paths(self.instance)
        first = ensure_broker(paths)['process']
        (self.instance / 'control/STOP').touch()
        with patch('builtins.print') as shown:
            self.assertEqual(main(['restart-broker', str(self.instance)]), 0, shown.call_args)
        second = json.loads(shown.call_args.args[0])['broker']['process']
        # The command returns once the old process has ended and another broker has written its receipt.
        self.assertFalse(alive(first))
        self.assertNotEqual(second, first)
        # The instance is then served by that broker: asked for its state, the live broker is the new process.
        self.assertEqual(broker_status(paths)['broker']['process'], second)

    def test_stop_holds_new_sessions_and_queued_follow_ups_until_resume(self):
        # stop and resume write and remove control/STOP. The runner's own pass reads it: while it
        # exists, neither a fresh attempt nor a queued follow-up launches, and after resume both do.
        # The pass still collects under the stop. A session that has ended leaves `running`, which is what the
        # operator waits for before ending the runner (reference/operations.md, Commands), and the peer work that
        # its collection creates waits like the follow-up that was queued before.
        runner = self.runner()
        peer = runner.enqueue('peer', {'source': str(self.instance / 'sessions/source'), 'source_role': 'attempt'})
        sid, session, job = self.ended(runner, 'attempt')
        (runner.session_dir(sid) / 'GO').write_bytes(b'go\n')  # the gate that dispatch opened
        with patch('runner.subprocess.Popen') as host, patch('builtins.print'):
            host.return_value.pid = runner.identity['pid']
            self.assertEqual(main(['stop', str(self.instance)]), 0)
            runner.tick()
            self.assertEqual(runner.active(), [])
            self.assertEqual(runner.state['jobs'][peer]['status'], 'pending')
            self.assertEqual((session['status'], runner.state['jobs'][job['pipeline'] + ':peer']['status']),
                             ('ended', 'pending'))
            self.assertEqual(main(['resume', str(self.instance)]), 0)
            runner.tick()
        self.assertCountEqual([s['role'] for _, s in runner.active()], ['peer', 'peer', 'attempt'])

    def test_work_that_falls_due_under_the_stop_is_queued_and_keeps_the_runner_from_finishing(self):
        # The stop holds back dispatch and nothing else. The root is formally proved, and an organizer is due for
        # the one published change. Under the stop the runner queues that job and does not launch it, so it does
        # not take itself for finished and exit; after resume the organizer launches.
        self.formal()
        self.configure(organizer_every_records=1)
        runner = self.runner()
        runner.check_root()  # an earlier pass compared the settled root with the first commit; no process starts below
        with patch('runner.subprocess.Popen') as host, patch('builtins.print'):
            host.return_value.pid = runner.identity['pid']
            self.assertEqual(main(['stop', str(self.instance)]), 0)
            self.assertFalse(runner.tick())
            self.assertFalse(runner.state['finished'])
            self.assertEqual(runner.active(), [])
            self.assertEqual([job['role'] for job in runner.state['jobs'].values() if job['status'] == 'pending'],
                             ['organizer'])
            self.assertEqual(main(['resume', str(self.instance)]), 0)
            runner.tick()
        self.assertEqual([s['role'] for _, s in runner.active()], ['organizer'])

    def test_status_reports_the_runner_alive_while_the_process_of_its_start_record_lives(self):
        # Runner.run writes its start record, runner/process.json, before its first pass: the runner's process,
        # the token that start gave it and the time. start confirms the runner from that record and from the
        # token on the runner's standard output, and status reports the runner alive while the recorded process
        # lives (reference/operations.md reads a runner that ended by itself from `runner_alive` false). The root
        # is formally proved and dispatch is stopped here, so the runner's own pass finds nothing to do and run
        # returns after it. The runner is this test's own process, which stays alive.
        self.formal()
        runner = self.runner()
        runner.check_root()  # an earlier pass compared the settled root with the first commit; no process starts below
        reported = status(self.instance)
        self.assertEqual((reported['runner_alive'], reported['stopped']), (False, False))  # no runner was started yet
        # `lean` is the broker's own account of this instance (lean_broker.broker_status), where
        # reference/operations.md has the operator read the compiles that wait, under `lean.queued`.
        broker = Paths(self.instance)
        self.assertEqual((reported['lean']['instance'], reported['lean']['calibration']),
                         (str(broker.instance), str(broker.calibration)))
        self.assertIn('queued', reported['lean'])
        with patch('runner.subprocess.Popen'), patch('builtins.print') as shown:
            self.assertEqual(main(['stop', str(self.instance)]), 0)
            runner.run('token-1')
        record = read_json(self.instance / 'runner/process.json')
        self.assertEqual((record['process'], record['token']), (runner.identity, 'token-1'))
        self.assertIsInstance(record['at'], float)
        self.assertEqual(json.loads(shown.call_args.args[0])['token'], 'token-1')
        reported = status(self.instance)
        self.assertEqual((reported['runner_alive'], reported['finished'], reported['stopped']), (True, True, True))
        # The record outlives its process. Once it names a process that is gone, the runner is reported as not alive.
        write_json(self.instance / 'runner/process.json', {**record, 'process': {'pid': 2 ** 22, 'birth': 'gone'}})
        self.assertFalse(status(self.instance)['runner_alive'])

    def test_a_runner_does_not_start_in_a_folder_whose_init_ended_before_its_first_commit(self):
        # init makes the first commit as its last step (runner.initialize). The lock on the definition modules, the
        # check of a settled root and the commit of every publication read from it, so a runner without it ends
        # at its first publication. An init that is ended inside its Git commands leaves instance.json and a
        # repository without a commit. That folder is made here by the real Git: the repository of the instance
        # is removed and made again, which is how init leaves it between `git init` and `git commit`. `run` is
        # the command that start launches. A pass of the runner would mean that it had started.
        remove_tree(self.instance / '.git')
        git(self.instance, 'init')
        with patch.object(Runner, 'tick', side_effect=AssertionError('the runner began its passes')), \
                patch('builtins.print') as shown:
            self.assertEqual(main(['run', str(self.instance)]), 1)
        self.assertIn('the first commit of this instance cannot be read', json.loads(shown.call_args.args[0])['error'])
        self.assertFalse((self.instance / 'runner/process.json').exists())

    def test_operator_review_and_organize_requests_become_assignments(self):
        self.event('v1', 'review', comprehensive(concerns=[concern('gap', 'Small.root')]))
        with patch('builtins.print') as shown:
            for arguments, reason in ((['--element', 'Small.missing'], 'unknown review target'),
                                      (['--concern', 'v1/absent'], 'unknown review target'),
                                      (['--reason', 'Look again.'], 'name the evidence to review with --element or --concern')):
                with self.subTest(arguments=arguments):
                    self.assertEqual(main(['review', str(self.instance), *arguments]), 1)
                    self.assertEqual(json.loads(shown.call_args.args[0]), {'error': reason})
            self.assertEqual(list((self.instance / 'control/requests').glob('*.json')), [])
            self.assertEqual(main(['review', str(self.instance), '--element', 'Small.root', '--element', 'Small.oddSum',
                                   '--concern', 'v1/gap', '--reason', 'Check the base case.']), 0)
            self.assertEqual(main(['organize', str(self.instance)]), 0)
        runner = self.runner()
        runner.ingest_inputs()
        runner.ingest_inputs()
        requested = [j for j in comprehensive_jobs(runner) if j['id'].startswith('operator:')]
        self.assertEqual([j['task'] for j in requested], [{
            'kind': 'comprehensive', 'concerns': ['v1/gap'], 'conflicts': [],
            'requested_elements': ['Small.root', 'Small.oddSum'], 'purpose': 'Check the base case.'}])
        organizers = [j for j in runner.state['jobs'].values() if j['role'] == 'organizer'
                      and j['id'].startswith('operator:')]
        self.assertEqual([j['status'] for j in organizers], ['pending'])
        # The requests are collected once, also by a restarted runner.
        restarted = self.runner()
        restarted.ingest_inputs()
        self.assertEqual(len(restarted.state['jobs']), len(runner.state['jobs']))

    def test_a_request_made_after_the_instance_finished_is_taken_up_and_the_runner_goes_on(self):
        # Once the root is formally settled and the remaining work has ended, the instance is finished and the
        # runner exits. A review requested after that takes effect at the next start, whose runner goes on until
        # that work has ended (reference/operations.md, Commands). So the pass that collects the request takes
        # `finished` back: the runner does not exit while the requested session works, and it keeps a broker
        # alive for that session again, which a session cannot start for itself (Runner.ensure_broker).
        self.formal()
        runner = self.runner()
        runner.check_root()  # an earlier pass compared the settled root with the first commit; no process starts below
        with patch('runner.subprocess.Popen') as host, patch('builtins.print'):
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.tick())
            self.assertTrue(runner.state['finished'])
            host.assert_not_called()
            self.assertEqual(main(['review', str(self.instance), '--element', 'Small.root']), 0)
            self.assertFalse(runner.tick())
        self.assertFalse(runner.state['finished'])
        self.assertEqual([s['role'] for _, s in runner.active()], ['review'])
        # The pass started the host of that session and then the broker.
        self.assertEqual([call.args[0][3] for call in host.call_args_list], ['_session', 'serve'])

    def test_root_change_requires_new_instance(self):
        self.runner()
        (self.instance / 'root.md').write_text('A different proposition.', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'new instance'):
            self.runner()

    def test_a_changed_lean_statement_of_the_root_requires_a_new_instance(self):
        # The root is fixed in Lean as well: its statement hash is recorded when the instance is created.
        index = self.instance / 'canon/index.json'
        data = read_json(index)
        data['entries']['Small.root']['statement_hash'] = 'another-statement'
        write_json(index, data)
        with self.assertRaisesRegex(ValueError, 'new instance'):
            self.runner()

    def test_commands_refuse_an_instance_of_an_earlier_schema(self):
        meta = read_json(self.instance / 'instance.json')
        write_json(self.instance / 'instance.json', {**meta, 'schema': 1})
        with patch('builtins.print') as shown:
            self.assertEqual(main(['status', str(self.instance)]), 1)
        self.assertIn('instance schema 2', json.loads(shown.call_args.args[0])['error'])

    def test_kill_session_refuses_an_unknown_session_and_one_that_has_ended(self):
        # The command acts on a session whose host or CLI is alive. Any other session it refuses with the
        # reason, and it writes no cancellation into the folder of a session that has ended.
        runner = self.runner()
        runner.state['sessions']['sended'] = {'id': 'sended', 'role': 'attempt', 'status': 'ended',
                                              'host': None, 'cli': None}
        runner.session_dir('sended').mkdir(parents=True)
        runner.save()
        with patch('builtins.print') as shown:
            for sid, reason in (('snobody', 'unknown session'), ('sended', 'session is no longer running')):
                with self.subTest(session=sid):
                    self.assertEqual(main(['kill-session', str(self.instance), sid]), 1)
                    self.assertEqual(json.loads(shown.call_args.args[0]), {'error': reason})
        self.assertEqual(list(runner.session_dir('sended').iterdir()), [])

    def test_rejected_settings_edit_keeps_the_last_valid_settings(self):
        runner = self.runner()
        # The settings in force are not the installed ones, which a return to the defaults would give as well.
        self.configure(max_sessions=5)
        runner.reload_settings()
        self.assertEqual(runner.settings['max_sessions'], 5)
        (self.instance / 'settings.json').write_text('{not json', encoding='utf-8')
        runner.reload_settings()
        self.assertEqual(runner.settings['max_sessions'], 5)
        self.assertIn('error', runner.state['settings_error'])
        config = defaults()
        config['max_sessions'] = 3
        write_json(self.instance / 'settings.json', config)
        runner.reload_settings()
        self.assertEqual(runner.settings['max_sessions'], 3)
        self.assertIsNone(runner.state['settings_error'])

    def test_start_does_not_replace_a_live_runner(self):
        # A live runner holds the instance lock. The runner that start launches cannot take it and exits,
        # and start reports that exit, not a readiness it never reached.
        with InstanceLock(self.instance / 'runner/lock'):
            with self.assertRaisesRegex(RuntimeError, 'exited before readiness'):
                start(self.instance)
        # The refused runner wrote no start record that could stand in for the live runner's receipt.
        self.assertFalse((self.instance / 'runner/process.json').exists())
        [log] = (self.instance / 'runner').glob('start-*.stderr.log')
        self.assertIn('already has a running runner', log.read_text(encoding='utf-8'))

    def test_start_waits_for_a_runner_that_is_slow_to_write_its_start_record(self):
        # A runner reads the whole research before it writes its start record (Runner.__init__, Runner.run), so
        # on a large research the record comes seconds after the launch, and start waits up to a minute for it
        # while the process it launched lives. That process and the clock are stood in for: the process stays
        # alive, each pause of the wait moves the clock on by a second, and at the fifteenth second the start
        # record and the line on standard output appear as Runner.run writes them. The test waits for nothing.
        runner = self.runner()
        clock = [0.0]

        def pause(seconds):
            clock[0] += 1.0
            if clock[0] == 15.0:
                argv = launch.call_args.args[0]
                token = argv[argv.index('--token') + 1]
                write_json(self.instance / 'runner/process.json',
                           {'process': runner.identity, 'token': token, 'at': time.time()})
                (self.instance / 'runner' / ('start-' + token + '.stdout.log')).write_text(
                    json.dumps({'started': runner.identity, 'token': token, 'instance': str(self.instance)}),
                    encoding='utf-8')

        with patch('runner.subprocess.Popen') as launch, patch('runner.time.sleep', side_effect=pause), \
                patch('runner.time.monotonic', side_effect=lambda: clock[0]):
            launch.return_value.poll.return_value = None
            started = start(self.instance)
        # The record came at the fifteenth second, and start returned with the process that the record names.
        self.assertEqual(clock[0], 15.0)
        self.assertEqual(started['pid'], runner.identity['pid'])

    def test_start_launches_the_runner_and_returns_once_its_start_record_names_this_launch(self):
        # start launches the detached runner through the run command. It returns that runner's PID and the two log
        # files of this launch once the runner has written its start record with the token start gave it and has
        # printed that token (reference/operations.md). Dispatch is stopped first, so the runner launches no
        # session. The runner is the real process, as are the archiver and the broker that its first pass starts.
        receipt = self.instance / 'runner/process.json'

        def end_runner():
            # As the operator ends a runner: the one process that runner/process.json names.
            if receipt.exists():
                process = read_json(receipt)['process']
                if alive(process):
                    terminate_process(process)
                deadline = time.monotonic() + 10
                while alive(process) and time.monotonic() < deadline:
                    time.sleep(0.05)

        with patch('builtins.print') as shown:
            self.assertEqual(main(['stop', str(self.instance)]), 0)
            self.addCleanup(end_runner)
            self.assertEqual(main(['start', str(self.instance)]), 0, shown.call_args)
        started, record = json.loads(shown.call_args.args[0]), read_json(receipt)
        self.assertEqual((started['pid'], Path(started['stdout']).name, Path(started['stderr']).name),
                         (record['process']['pid'], f"start-{record['token']}.stdout.log",
                          f"start-{record['token']}.stderr.log"))
        # The runner's own start record is the first line of the returned stdout log.
        printed = json.loads(Path(started['stdout']).read_text(encoding='utf-8').splitlines()[0])
        self.assertEqual((printed['started'], printed['token']), (record['process'], record['token']))
        # The root is open, so this runner goes on; under the stop it has launched no session.
        self.assertTrue(alive(record['process']))
        self.assertEqual(read_json(self.instance / 'runner/state.json')['sessions'], {})
        # The archiver and the broker write into the instance from processes of their own. Before the fixture
        # removes the folder, the archiver has held and freed its lock, and the broker has recorded itself, so
        # that the fixture finds it and stops it.
        lock = self.instance / 'runner/archive-lock'
        deadline = time.monotonic() + 30
        while not lock.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        with InstanceLock(lock, 'archiver', wait=30):
            pass
        ensure_broker(Paths(self.instance))
        end_runner()
        self.assertFalse(alive(record['process']))


class ContestedReviewTests(RefutedRootCase):
    """The runner's assignment of comprehensive review for a contested statement."""

    def test_published_comprehensive_review_is_not_reassigned_for_a_statement_it_left_contested(self):
        # A contested statement's opposing judgments are assigned once, as <statement>:<change IDs>.
        # A review that leaves the statement contested is not assigned again; a changed opposition is.
        self.contested()
        runner = Runner(self.instance, self.skill)
        elements = runner.model['elements']
        sides = sorted(elements[name]['verdict']['change'] for name in ('Small.root', 'Small.notRoot'))
        runner.populate()
        [job] = comprehensive_jobs(runner)
        self.assertEqual((job['task']['concerns'], job['task']['conflicts']), ([], ['Small.root:' + ','.join(sides)]))
        # The review could not locate the failure, so the statement stays contested.
        publish_comprehensive(runner, job, comprehensive())
        self.assertEqual(runner.model['root_state'], 'contested')
        self.assertEqual(runner.state['processed_conflicts'], job['task']['conflicts'])
        runner.populate()
        self.assertEqual([j['id'] for j in comprehensive_jobs(runner)], [job['id']])
        # A proof on either side that is judged again changes the opposition, which has not been assigned yet.
        again, _ = self.replace_proof('Small.root', self.root_text(proof='intro n\n  sorry'),
                                      'By induction on $n$, written out for each step.', engine=runner)
        self.assertEqual(runner.model['root_state'], 'contested')
        runner.populate()
        pending = [j['task']['conflicts'] for j in comprehensive_jobs(runner) if j['status'] == 'pending']
        self.assertEqual(pending, [['Small.root:' + ','.join(sorted([again, elements['Small.notRoot']['verdict']['change']]))]])


class InitializeTests(unittest.TestCase):
    """runner.initialize: the root is fixed without a proof, since the research is what proves or refutes it."""

    def setUp(self):
        # Removed by remove_tree, which waits for a file that a job host of `initialize` still holds as it ends.
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(remove_tree, self.root)

    def test_a_canon_refused_after_the_directory_was_created_leaves_no_instance(self):
        # What runner.initialize itself refuses after it has created the directory (reference/operations.md,
        # Create and start): a library that does not compile, a root declaration that is not a theorem, and a
        # root that already has a proof, in Lean or in its record. Each case differs in one thing from the
        # canon of the fixture, which init accepts.
        broken = ROOT.replace('/-- The sum', '-- fail: unknown constant Small.gone\n/-- The sum')
        complete = ROOT.replace('  sorry', '  rfl')
        written = RECORDS['Small/root.md'] + '\n## Proof\n\nBy induction on $n$, comparing consecutive squares.\n'
        proved = ('the root declaration Small.root already has a proof',)
        cases = (('broken', ('the canon does not compile', 'Small.Root', 'unknown constant Small.gone'), {'root': broken}),
                 ('definition', ('the root declaration Small.oddSum is not a theorem of the canon',),
                  {'declaration': 'Small.oddSum'}),
                 ('lean', proved, {'root': complete}),
                 ('written', proved, {'records': {'Small/root.md': written}}))
        for name, reasons, changed in cases:
            with self.subTest(name):
                with self.assertRaises(ValueError) as refused:
                    initialized(self.root, name, **changed)
                for reason in reasons:
                    self.assertIn(reason, str(refused.exception))
                self.assertFalse((self.root / name / 'instance.json').exists())

    def test_a_server_whose_command_is_not_found_is_refused_before_anything_is_created(self):
        # A session whose server does not start begins its turn without the tool and reports nothing.
        config = fixture_settings()
        config['mcp_servers'] = {'scholarly': {'command': str(self.root / 'absent' / 'python.exe'), 'args': []},
                                 'remote': {'url': 'https://example.invalid/mcp'}}
        with patch(__name__ + '.fixture_settings', return_value=config), \
                self.assertRaisesRegex(ValueError, r'mcp_servers names a command that was not found: scholarly \('):
            initialized(self.root, 'unattached')
        self.assertFalse((self.root / 'unattached').exists())

    def test_the_other_refusals_made_before_anything_is_created_leave_nothing_behind(self):
        # Before it creates the instance directory, init also refuses an empty root file, a canon folder without
        # lean/ or with more than one top-level module name, a settings file that is not valid, and a path that
        # exists (reference/operations.md, Create and start). Each case differs in one thing from the input of
        # the last case, which init accepts until it meets the existing path.
        goal, blank, settings, invalid = (self.root / name for name in ('goal.md', 'blank.md', 'settings.json', 'invalid.json'))
        goal.write_text('For every natural number n, the sum of the first n odd numbers is n * n.', encoding='utf-8')
        blank.write_text(' \n', encoding='utf-8')
        write_json(settings, fixture_settings())
        write_json(invalid, {**fixture_settings(), 'max_sessions': 0})
        whole, bare, two = (self.root / name for name in ('whole', 'bare', 'two'))
        write_canon(whole)
        (bare / 'records').mkdir(parents=True)
        write_canon(two)
        (two / 'lean/Other.lean').write_text('module\n', encoding='utf-8')
        target = self.root / 'instance'
        cases = (('the root statement must be nonempty UTF-8', blank, whole, settings),
                 ('the canon folder needs lean/', goal, bare, settings),
                 ('share one top-level name, the library; found: Other, Small', goal, two, settings),
                 ('max_sessions must be a positive integer', goal, whole, invalid))
        for message, root, canon, config in cases:
            with self.subTest(message), self.assertRaisesRegex(ValueError, message):
                initialize(target, root, canon, 'Small.root', config)
            self.assertFalse(target.exists())
        target.mkdir()
        with self.assertRaises(FileExistsError):
            initialize(target, goal, whole, 'Small.root', settings)
        self.assertEqual(list(target.iterdir()), [])

    def test_a_file_that_an_ignore_rule_names_is_in_the_first_commit(self):
        # The first commit holds the instance as it began: the lock on the definition modules and the check of a
        # settled root read the index and the files of the modules from it (canon.definition_modules,
        # Runner.check_root). Git leaves out of `git add` what an ignore rule names. Such a rule can stand in the
        # canon folder that init was given, as here, or in the Git configuration of whoever runs init. The
        # repository and every Git call are real.
        instance = initialized(self.root, 'ignored', records={'.gitignore': 'oddSum.md\n'})
        self.addCleanup(stop_broker, instance)
        self.assertEqual(git(instance, 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'canon/records').splitlines(),
                         ['canon/records/.gitignore', 'canon/records/Small/oddSum.md', 'canon/records/Small/root.md'])

    def test_a_read_only_file_of_the_canon_folder_is_writable_in_the_instance(self):
        # A file of the canon folder that init is given can carry the read-only flag, as a file does that was
        # protected against change or taken from an archive. Windows refuses to replace or to remove a file with
        # that flag, and a publication replaces the root's module and its record when the root receives its proof
        # (canon.sync_tree, canon.apply_written). So init copies the files without the flag. The flag is set on
        # real files, and the instance is created by runner.initialize.
        canon, goal, settings = (self.root / name for name in ('canon', 'goal.md', 'settings.json'))
        write_canon(canon)
        protected = ('lean/Small/Root.lean', 'records/Small/root.md')
        for name in protected:
            os.chmod(canon / name, 0o444)
        goal.write_text('For every natural number n, the sum of the first n odd numbers is n * n.', encoding='utf-8')
        write_json(settings, fixture_settings())
        initialize(self.root / 'instance', goal, canon, 'Small.root', settings)
        self.addCleanup(stop_broker, self.root / 'instance')
        for name in protected:
            self.assertTrue(os.access(self.root / 'instance/canon' / name, os.W_OK), name)


class SettingsTests(unittest.TestCase):
    def test_the_literature_server_is_attached_by_default_and_can_be_left_out(self):
        attached = defaults()['mcp_servers']
        self.assertEqual(list(attached), ['scholarly'])
        # The server of the repository that holds this skill, started without institutional logins.
        home = Path(__file__).resolve().parents[5] / 'services' / 'scholarly-mcp'
        self.assertEqual(attached['scholarly']['args'], [(home / 'server.py').as_posix(), '--public-only'])
        self.assertEqual(Path(attached['scholarly']['command']).parents[1], home / '.venv')
        # An omitted `mcp_servers` receives the default; a given one replaces it, the empty one included.
        self.assertEqual(validate({})['mcp_servers'], attached)
        self.assertEqual(validate({'mcp_servers': {}})['mcp_servers'], {})
        other = {'explicit': {'command': sys.executable, 'args': ['server.py']}}
        self.assertEqual(validate({'mcp_servers': other})['mcp_servers'], other)

    def test_launch_interval_must_be_nonnegative_seconds(self):
        for bad in (-1, 1.5, '180'):
            config = defaults()
            config['launch_interval'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'launch_interval'):
                validate(config)

    def test_the_installed_scheduling_defaults(self):
        config = defaults()
        self.assertEqual({key: config[key] for key in ('max_sessions', 'explore_every', 'organizer_every_records',
                                                       'launch_interval', 'retry_seconds', 'retry_max_seconds')},
                         {'max_sessions': 8, 'explore_every': 1, 'organizer_every_records': 4,
                          'launch_interval': 180, 'retry_seconds': 60, 'retry_max_seconds': 1800})

    def test_sorry_axiom_cannot_be_enabled(self):
        config = defaults()
        config['lean']['allowed_axioms'].append('sorryAx')
        with self.assertRaisesRegex(ValueError, 'sorryAx cannot be allowed'):
            validate(config)

    def test_legacy_or_misspelled_settings_are_rejected(self):
        legacy = {**defaults(), 'limit_wait_seconds': 5}
        misspelled = defaults()
        misspelled['lean']['memory_budget'] = 4096
        executable = defaults()
        executable['cli']['Codex'] = 'C:/tools/codex.exe'
        for name, config in (('legacy', legacy), ('misspelled', misspelled), ('executable', executable)):
            with self.subTest(name), self.assertRaisesRegex(ValueError, 'unknown setting'):
                validate(config)
        role = defaults()
        role['roles']['reviewer'] = role['roles'].pop('review')
        with self.assertRaisesRegex(ValueError, r'unknown setting: roles\.reviewer'):
            validate(role)

    def test_acceptance_criteria_apply_by_default_and_can_be_turned_off(self):
        applied = {'decline_reducible_proofs': True, 'decline_uncomprehended_computation': True}
        self.assertEqual(defaults()['acceptance'], applied)
        self.assertEqual(validate({})['acceptance'], applied)
        one_off = validate({'acceptance': {'decline_uncomprehended_computation': False}})['acceptance']
        self.assertEqual(one_off, {**applied, 'decline_uncomprehended_computation': False})
        cases = (('acceptance must be an object', {'acceptance': True}),
                 (r'unknown setting: acceptance\.decline_computation',
                  {'acceptance': {'decline_computation': False}}),
                 ('acceptance.decline_reducible_proofs must be true or false',
                  {'acceptance': {'decline_reducible_proofs': 0}}))
        for pattern, config in cases:
            with self.subTest(pattern), self.assertRaisesRegex(ValueError, pattern):
                validate(config)

    def test_malformed_setting_structure_is_rejected_by_name(self):
        def lean(**changed):
            config = defaults()
            config['lean'].update(changed)
            return config

        cli_path = defaults()
        cli_path['cli']['codex'] = 5
        cases = (('schema 1 object', {**defaults(), 'schema': 2}),
                 ('cli must be an object', {**defaults(), 'cli': 'C:/tools/codex.exe'}),
                 ('lean must be an object', {**defaults(), 'lean': []}),
                 ('max_sessions must be a positive integer', {**defaults(), 'max_sessions': 0}),
                 ('retry_max_seconds must be at least retry_seconds',
                  {**defaults(), 'retry_seconds': 60, 'retry_max_seconds': 30}),
                 ('roles must be an object', {**defaults(), 'roles': []}),
                 ('mcp_servers must map', {**defaults(), 'mcp_servers': {'scholarly': 'server.py'}}),
                 ('attempt needs an ordered nonempty model list', {**defaults(), 'models': []}),
                 ('model entries need exactly', {**defaults(), 'models': ['codex/gpt-6.1-sol']}),
                 ('fallback', {**defaults(), 'models': [{'model': 'claude/opus', 'effort': 'xhigh', 'fallback': True}]}),
                 ('cli.codex must be', cli_path),
                 ('lean.cache_epoch must be nonempty text', lean(cache_epoch=' ')),
                 ('lean.version_command must be a nonempty command array', lean(version_command=[])),
                 ('lean.cwd must be', lean(cwd=5)),
                 ('lean.env must map strings to strings', lean(env={'PATH': 5})),
                 ('allowed_axioms must be a string list', lean(allowed_axioms='propext')))
        for pattern, config in cases:
            with self.subTest(pattern), self.assertRaisesRegex(ValueError, pattern):
                validate(config)


if __name__ == '__main__':
    unittest.main()
