"""Questions: objects of understanding that explorers occupy, proposed and resolved through review.

A question carries its understanding so far, a text in canon/questions/. A resolution is that text
together with review's judgment that it settles what the question asks. Question q0 is the root
problem as a whole: it is resolved by the root's formal settlement and by nothing else."""
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from availability import no_research_outcome
from canon import Canon, split_review
from canon_tool import main as canon_main, question_view
from check import Invalid, assessment_check, change_check, check_session, findings_check, organization_check
from coordination import (board, main as coordination_main, question_availability, question_lease,
                          question_lease_table, question_release, question_take, question_wait, updates)
from knowledge import canonical_question, render, replay
from runner import Runner, main, operator_questions, status, uid
from runtime_support import git, read_json, write_json
from support import InstanceCase, module_text, record_text

ROLES = ('attempt', 'explore', 'formalizer', 'peer', 'review', 'organizer')

# The root as each variant of the fixture states it (support.ROOTS). The closed form has no binders before
# the colon, so its negation can be stated, in valid Lean and in the stand-in compiler's subset alike.
ROOT_HEADS = {'default': 'theorem root (n : Nat) : oddSum n = n * n := by\n',
              'closed': 'theorem root : ∀ n : Nat, oddSum n = n * n := by\n'}
ROOT_DOC = '/-- The sum of the first `n` odd numbers is the square of `n`. -/\n'
# The stand-in compiler reads a statement as the negation of the root's when the text after the name is
# `: ¬ (<the root's statement text>)` (canon_lean.extract).
REFUTATION = module_text('/-- The root statement fails. -/\n'
                         'theorem root_false : ¬ (∀ n : Nat, oddSum n = n * n) := by\n  rfl')
ROOT_RECORD = record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                          proof='By induction on $n$: each step adds $2n + 1$ and completes the next square.',
                          statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                          short='odd numbers sum to a square')
REFUTATION_RECORD = record_text('The root statement fails.', weight='unit', refutes='Small.root',
                                proof='A direct evaluation contradicts the identity.')
ACCOUNT = ('Both estimates lose the same factor at this scale, because each bounds `Small.oddSum` term by term.\n'
           'What is not yet understood is whether a telescoping argument avoids the loss.\n')
LATER_ACCOUNT = ('The loss comes from bounding `Small.oddSum` term by term; a telescoping argument avoids it.\n'
                 'What remains open is the same question for sums over other progressions.\n')
CONTRIBUTION = 'Closed what it took on.'  # the contribution support.verdicts writes for review


def question(qid, statement=None):
    return {'id': qid, 'statement': statement or ('What ' + qid + ' asks.'),
            'grounds': 'Several proofs stall at the same scale; understanding it would show why.'}


def resolution(rid, qid):
    return {'id': rid, 'question': qid}


class QuestionCase(InstanceCase):
    """Brings the root, questions and merges into a state through the real publication path."""

    def frontier(self, model=None):
        render(self.instance, model or replay(self.instance), [])
        return (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')

    @staticmethod
    def part(frontier, qid):
        """What the frontier shows under one question's heading."""
        return frontier.split('## ' + qid + '\n', 1)[1].split('\n## ', 1)[0]

    def prove_root(self, formal=True, engine=None):
        """Replace the root's proof: a complete Lean proof, or one that ends in sorry beside a written proof."""
        text = ROOT_DOC + ROOT_HEADS[self.root_variant] + ('  rfl' if formal else '  sorry')
        folder = self.candidate(replace={'Small.root': text}, records={'Small/root.md': ROOT_RECORD})
        return self.publish(folder, role='formalizer' if formal else 'attempt', engine=engine)[0]

    def refute_root(self, engine=None):
        """Add a theorem with a complete Lean proof whose statement Lean confirms as the root's negation."""
        folder = self.candidate(modules={'Small/Refutation.lean': REFUTATION},
                                records={'Small/root_false.md': REFUTATION_RECORD})
        return self.publish(folder, role='formalizer', engine=engine)[0]

    def account(self, qid, text=ACCOUNT, resolution_id=None, resolved=True, engine=None):
        """Publish an exploration's change that writes a question's understanding, optionally as its resolution."""
        folder = self.candidate(understanding={qid + '.md': text},
                                resolutions=[resolution(resolution_id, qid)] if resolution_id else None)
        review = self.verdicts(folder)
        if resolution_id and not resolved:
            review['resolutions'] = [{'proposal': resolution_id, 'resolved': False, 'reason': 'Explains one regime only.'}]
        return self.publish(folder, review, role='explore', question=qid, engine=engine)[0]

    def organize(self, merges, engine=None):
        """Publish an organizer's question merges through InstanceCase.organize; returns the publication's ID."""
        return super().organize(merge_questions=merges, engine=engine)[0]

    def empty_output(self):
        """An output folder with nothing in it, as an organizer that only merges questions leaves."""
        folder = self.root / ('organizer-' + uid('o'))
        folder.mkdir()
        return folder

    def assert_root_question_is_closed_to_explanations_and_merges(self, model, other):
        folder = self.candidate(understanding={'q0.md': ACCOUNT}, resolutions=[resolution('r', 'q0')])
        with self.assertRaisesRegex(Invalid, 'root question'):
            change_check(folder, model, 'speer')
        # The same text without the resolution is an ordinary replacement of q0's understanding.
        change_check(self.candidate(understanding={'q0.md': ACCOUNT}), model, 'speer')
        output = self.empty_output()
        for merge in ({'from': 'q0', 'into': other}, {'from': other, 'into': 'q0'}):
            with self.subTest(merge=merge), self.assertRaisesRegex(Invalid, 'root question'):
                organization_check({'batch': [], 'merge_questions': [{**merge, 'reason': 'No.'}]}, output, model, [])

    def assert_settlement(self, state, proofs):
        model = replay(self.instance)
        q0 = model['questions']['q0']
        self.assertEqual(model['root_state'], state)
        self.assertEqual((q0['state'], q0['resolutions']), ('resolved', []))
        self.assertEqual(q0['root_settlement'], {'state': state, 'proofs': proofs})
        other = model['questions']['op-scale']
        self.assertEqual((other['state'], other['root_settlement']), ('open', None))
        # The runner rendered the frontier and the model when it published the settlement.
        section = self.part((self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'), 'q0')
        self.assertIn('State: resolved', section)
        self.assertIn("Resolved by the root's formal settlement, not by an explanation: "
                      + ', '.join('`' + name + '`' for name in proofs), section)
        self.assertEqual(read_json(self.instance / 'knowledge/state.json')['questions']['q0'], q0)
        self.assertTrue(read_json(self.instance / 'runner/state.json')['complete'])
        # An explanation still cannot resolve it, and it is still never merged.
        self.assert_root_question_is_closed_to_explanations_and_merges(model, 'op-scale')


class QuestionKnowledgeTests(QuestionCase):
    def test_root_question_is_always_present_open_and_unresolvable(self):
        self.questions('qops', [question('op-scale')])
        model = replay(self.instance)
        q0 = model['questions']['q0']
        self.assertEqual((q0['state'], q0['origin'], q0['canonical'], q0['resolutions'], q0['root_settlement']),
                         ('open', 'root', 'q0', [], None))
        self.assertEqual(model['root_state'], 'unresolved')
        self.assert_root_question_is_closed_to_explanations_and_merges(model, 'op-scale')
        frontier = self.frontier(model)
        self.assertIn('## q0\n', frontier)
        section = self.part(frontier, 'q0')
        self.assertIn('Source: the root statement', section)
        self.assertIn('State: open', section)
        self.assertNotIn('Resolved by', section)

    def test_root_question_is_resolved_by_a_formal_proof_of_the_root(self):
        self.questions('qops', [question('op-scale')])
        self.prove_root()
        self.assert_settlement('formal_proved', ['Small.root'])

    def test_withdrawing_the_root_formal_settlement_reopens_the_root_question(self):
        self.prove_root()
        model = replay(self.instance)
        self.assertEqual(model['questions']['q0']['state'], 'resolved')
        findings = [{'concerns': [], 'status': 'confirmed', 'reason': 'The Lean proof does not establish the root proposition.',
                     'invalidates': ['Small.root']}]
        findings_check(findings, model, set(model['elements']))
        self.event('v1', 'review', {'findings': findings, 'concerns': []})
        model = replay(self.instance)
        self.assertEqual(model['root_state'], 'unresolved')
        self.assertEqual(model['elements']['Small.root']['standing'], 'not_confirmed')
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['root_settlement']), ('open', None))
        frontier = self.frontier(model)
        section = self.part(frontier, 'q0')
        self.assertIn('State: open', section)
        self.assertNotIn("root's formal settlement", section)
        # The withdrawal stays visible in the frontier, on the root whose proof it withdrew.
        self.assertIn('does not establish the root proposition', frontier)

    def test_a_finding_that_withdraws_a_proof_the_root_settlement_rests_on_stands_beside_the_root_question(self):
        # The root's formal proof names lemma0; stray is proved beside it, and the root rests on nothing of it.
        parts = module_text('/-- The empty sum. -/\ntheorem lemma0 : oddSum 0 = 0 := by\n  rfl\n\n'
                            '/-- The first odd number. -/\ntheorem stray : oddSum 1 = 1 := by\n  rfl')
        folder = self.candidate(modules={'Small/Parts.lean': parts},
                                replace={'Small.root': ROOT_DOC + ROOT_HEADS[self.root_variant] + '  have h := lemma0\n  rfl'},
                                imports={'Small.root': ['Small.Parts']},
                                records={'Small/root.md': ROOT_RECORD, 'Small/lemma0.md': record_text('The empty sum is zero.'),
                                         'Small/stray.md': record_text('The first odd number is one.')})
        self.publish(folder, role='formalizer')
        model = replay(self.instance)
        self.assertEqual(model['elements']['Small.root']['uses'], ['Small.lemma0'])
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['annotations']), ('resolved', []))

        def withdraw(eid, reason, name):
            findings = [{'concerns': [], 'status': 'confirmed', 'reason': reason, 'invalidates': [name]}]
            findings_check(findings, replay(self.instance), set(replay(self.instance)['elements']))
            self.event(eid, 'review', {'findings': findings, 'concerns': []})
            return replay(self.instance)

        # A withdrawal of what the settlement does not rest on leaves the root question as it was.
        model = withdraw('v1', 'The single term is miscounted.', 'Small.stray')
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['annotations']), ('resolved', []))
        # A withdrawal of a proof beneath the root's proof ends the settlement. The finding names no question,
        # and it stands beside q0 all the same, under q0 in the frontier.
        model = withdraw('v2', 'The empty sum is taken over the wrong range.', 'Small.lemma0')
        self.assertEqual((model['findings'][1]['source'], model['findings'][1]['questions']), ('v2', []))
        q0 = model['questions']['q0']
        self.assertEqual((q0['state'], q0['root_settlement'], q0['annotations']), ('open', None, [1]))
        section = self.part(self.frontier(model), 'q0')
        self.assertIn('- Later review (confirmed): The empty sum is taken over the wrong range. — v2', section)
        self.assertNotIn('miscounted', section)
        # The other questions carry no annotation of it.
        self.assertFalse([qid for qid, entry in model['questions'].items() if qid != 'q0' and entry['annotations']])

    def test_review_admits_declines_or_asks_to_revise_question_proposals(self):
        self.questions('qops', [question('op-existing')])
        folder = self.candidate(questions=[question('speer-sharp'), question('speer-dup'), question('speer-vague')])
        review = self.verdicts(folder)
        review['questions'] = [
            {'proposal': 'speer-sharp', 'verdict': 'admitted', 'reason': 'Important and exact.'},
            {'proposal': 'speer-dup', 'verdict': 'declined', 'duplicate_of': 'op-existing',
             'reason': 'op-existing already asks this.'},
            {'proposal': 'speer-vague', 'verdict': 'revise',
             'reason': 'Name the regime and the quantity whose behaviour is asked about.'}]
        cid, _ = self.publish(folder, review, role='explore')
        model = replay(self.instance)
        admitted = model['questions']['speer-sharp']
        self.assertEqual((admitted['source'], admitted['origin'], admitted['state'], admitted['statement'], admitted['grounds']),
                         (cid, 'change', 'open', 'What speer-sharp asks.', question('speer-sharp')['grounds']))
        self.assertNotIn('speer-dup', model['questions'])
        self.assertNotIn('speer-vague', model['questions'])
        self.assertEqual([(p['id'], p['verdict'], p['duplicate_of'], p['change']) for p in model['question_proposals']],
                         [('speer-dup', 'declined', 'op-existing', cid), ('speer-vague', 'revise', None, cid)])
        self.assertIn('Name the regime', model['question_proposals'][1]['reason'])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        self.assertIn('## speer-sharp\n', frontier)
        self.assertIn('Source: change ' + cid, self.part(frontier, 'speer-sharp'))
        self.assertNotIn('## speer-dup\n', frontier)
        self.assertNotIn('## speer-vague\n', frontier)
        self.assertIn('- revise: What speer-vague asks. — review: Name the regime', frontier)
        self.assertIn('- declined (duplicate of op-existing): What speer-dup asks.', frontier)
        # An admitted question is one an explorer can take; a proposal review did not admit is not.
        self.assertEqual(sorted(question_availability(self.instance)['free']), ['op-existing', 'q0', 'speer-sharp'])

    def test_a_resolution_comes_with_its_text_and_a_later_finding_reopens_the_question(self):
        self.questions('qops', [question('op-scale')])
        cid = self.account('op-scale', resolution_id='res')
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'resolved')
        self.assertEqual(model['questions']['op-scale']['resolutions'], [cid + '/res'])
        self.assertEqual(model['changes'][cid]['question'], 'op-scale')
        self.assertEqual(read_json(self.instance / 'knowledge/events' / (cid + '.json'))['question'], 'op-scale')
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        section = self.part(frontier, 'op-scale')
        self.assertIn('State: resolved', section)
        self.assertIn(f'- Resolved by {cid}/res', section)
        # The text that settles the question is its understanding so far, with review's assessment under it.
        body, review = split_review((Canon(self.instance).questions / 'op-scale.md').read_text(encoding='utf-8'))
        self.assertEqual(body, ACCOUNT)
        self.assertEqual(review, f'Change {cid} (revision 2): {CONTRIBUTION}')
        self.assertIn('canon/questions/op-scale.md', git(self.instance, 'ls-files', '--', 'canon/questions'))
        findings = [{'concerns': [], 'status': 'confirmed', 'reason': 'The account assumes the conclusion.',
                     'reopens': ['op-scale']}]
        findings_check(findings, model, set(model['elements']))
        self.event('v1', 'review', {'findings': findings, 'concerns': []})
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'open')
        self.assertEqual(model['questions']['op-scale']['resolutions'], [])
        section = self.part(self.frontier(model), 'op-scale')
        self.assertIn('State: open', section)
        self.assertNotIn('Resolved by', section)
        # The finding stays visible beside the reopened question.
        self.assertIn('assumes the conclusion', section)
        self.assertIn('v1', section)
        # A later account that review accepts resolves it again.
        again = self.account('op-scale', LATER_ACCOUNT, resolution_id='res')
        model = replay(self.instance)
        self.assertEqual((model['questions']['op-scale']['state'], model['questions']['op-scale']['resolutions']),
                         ('resolved', [again + '/res']))

    def test_unaccepted_resolution_leaves_the_question_open(self):
        self.questions('qops', [question('op-scale')])
        cid = self.account('op-scale', resolution_id='res', resolved=False)
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'open')
        self.assertEqual(model['questions']['op-scale']['resolutions'], [])
        self.assertNotIn('Resolved by', self.part(self.frontier(model), 'op-scale'))
        # Review judges and does not gate: the account is the question's understanding so far all the same.
        body, review = split_review((Canon(self.instance).questions / 'op-scale.md').read_text(encoding='utf-8'))
        self.assertEqual(body, ACCOUNT)
        self.assertIn(cid, review)

    def test_organizer_merges_duplicate_questions_and_preserves_aliases(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        model = replay(self.instance)
        output = self.empty_output()
        merge = {'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}
        organization_check({'batch': [], 'merge_questions': [merge]}, output, model, [])
        cases = (
            ('root question', {'batch': [], 'merge_questions': [{**merge, 'from': 'q0'}]}),
            ('root question', {'batch': [], 'merge_questions': [{**merge, 'into': 'q0'}]}),
            ('existing questions', {'batch': [], 'merge_questions': [{**merge, 'into': 'missing'}]}),
            ('existing questions', {'batch': [], 'merge_questions': [{**merge, 'from': 'missing'}]}),
            ('existing questions', {'batch': [], 'merge_questions': [{'into': 'op-b', 'reason': 'No source.'}]}),
            ('question merge reason', {'batch': [], 'merge_questions': [{**merge, 'reason': ' '}]}),
            ('question merge reason', {'batch': [], 'merge_questions': [{'from': 'op-a', 'into': 'op-b'}]}),
            ('merge_questions: array', {'batch': [], 'merge_questions': merge}),
            ('exact assigned batch', {'batch': ['c-other'], 'merge_questions': [merge]}),
            ('exact assigned batch', {'merge_questions': [merge]}),
        )
        for pattern, data in cases:
            with self.subTest(pattern=pattern, data=data), self.assertRaisesRegex(Invalid, pattern):
                organization_check(data, output, model, [])
        # An organizer's own change holds Lean modules, replacements and records, not questions or accounts.
        for extra in ({'questions': [question('o-new')]}, {'understanding': {'op-a.md': ACCOUNT}},
                      {'understanding': {'op-a.md': ACCOUNT}, 'resolutions': [resolution('res', 'op-a')]}):
            with self.subTest(extra=sorted(extra)), self.assertRaisesRegex(Invalid, 'Lean modules, replacements and records only'):
                organization_check({'batch': [], 'merge_questions': [merge]}, self.candidate(**extra), model, [])
        oid = self.organize([merge])
        event = read_json(self.instance / 'knowledge/events' / (oid + '.json'))
        self.assertEqual((event['kind'], event['folder']), ('organization', 'organizations/' + oid))
        self.assertEqual(read_json(self.instance / 'knowledge/organizations' / oid / 'organization.json')['merge_questions'],
                         [merge])
        model = replay(self.instance)
        self.assertEqual(model['question_aliases'], {'op-a': 'op-b'})
        self.assertEqual(canonical_question(model, 'op-a'), 'op-b')
        self.assertEqual(model['questions']['op-a']['canonical'], 'op-b')
        self.assertEqual(model['questions']['op-b']['canonical'], 'op-b')
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        self.assertNotIn('\n## op-a\n', frontier)
        self.assertIn('Aliases: op-a', self.part(frontier, 'op-b'))
        # A merge the other way round would now join the question to itself, and changes nothing.
        self.organize([{'from': 'op-b', 'into': 'op-a', 'reason': 'The same question again.'}])
        self.assertEqual(replay(self.instance)['question_aliases'], {'op-a': 'op-b'})

    def test_a_resolution_against_a_merged_alias_resolves_the_surviving_question(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}])
        model = replay(self.instance)
        # A peer whose exploration took op-a before the merge still names it; the check accepts the account
        # under either identity.
        for name in ('op-a.md', 'op-b.md'):
            change_check(self.candidate(understanding={name: ACCOUNT}, resolutions=[resolution('res', 'op-a')]),
                         model, 'speer')
        cid = self.account('op-a', resolution_id='res')
        model = replay(self.instance)
        survivor = model['questions']['op-b']
        self.assertEqual((survivor['state'], survivor['resolutions']), ('resolved', [cid + '/res']))
        self.assertEqual(model['changes'][cid]['question'], 'op-b')
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        self.assertNotIn('\n## op-a\n', frontier)
        section = self.part(frontier, 'op-b')
        self.assertIn('State: resolved', section)
        self.assertIn(f'- Resolved by {cid}/res', section)
        self.assertIn('Aliases: op-a', section)

    def test_a_question_resolved_before_its_merge_resolves_the_question_it_merges_into(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        cid = self.account('op-a', resolution_id='res')
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}])
        model = replay(self.instance)
        self.assertEqual(model['organized'], [cid])
        survivor = model['questions']['op-b']
        self.assertEqual((survivor['state'], survivor['resolutions']), ('resolved', [cid + '/res']))
        section = self.part((self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'), 'op-b')
        self.assertIn('State: resolved', section)
        self.assertIn(f'- Resolved by {cid}/res', section)

    def test_an_account_written_under_a_merged_alias_is_the_surviving_questions_understanding(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}])
        self.account('op-a', resolution_id='res')
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-b']['state'], 'resolved')
        # The question is one question after the merge, so the text that settled it is what a session
        # reads when it asks for that question, under either identifier.
        for qid in ('op-b', 'op-a'):
            with self.subTest(question=qid):
                shown = question_view(self.instance, model, qid)
                self.assertEqual(shown.splitlines()[0], 'op-b · resolved')
                self.assertIn(ACCOUNT.strip(), shown)

    def test_a_finding_that_reopens_through_an_alias_reopens_the_surviving_question_and_stays_beside_it(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        self.account('op-b', resolution_id='res')
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}])
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-b']['state'], 'resolved')
        findings = [{'concerns': [], 'status': 'confirmed', 'reason': 'The account covers one regime only.',
                     'reopens': ['op-a']}]
        findings_check(findings, model, set(model['elements']))
        self.event('v1', 'review', {'findings': findings, 'concerns': []})
        model = replay(self.instance)
        self.assertEqual((model['questions']['op-b']['state'], model['questions']['op-b']['resolutions']), ('open', []))
        section = self.part(self.frontier(model), 'op-b')
        self.assertIn('State: open', section)
        self.assertIn('covers one regime only', section)


class RefutedRootQuestionTests(QuestionCase):
    """The root stated without binders, so that a statement can be its negation."""
    root_variant = 'closed'

    def test_root_question_is_resolved_by_a_formal_refutation_of_the_root(self):
        self.questions('qops', [question('op-scale')])
        self.refute_root()
        self.assert_settlement('formal_refuted', ['Small.root_false'])

    def test_an_informal_or_contested_root_leaves_the_root_question_open(self):
        self.prove_root(formal=False)
        model = replay(self.instance)
        self.assertEqual(model['root_state'], 'informal_proved')
        self.assertEqual(model['elements']['Small.root']['standing'], 'accepted')
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['root_settlement']), ('open', None))
        self.assertIn('State: open', self.part(self.frontier(model), 'q0'))
        self.assertFalse(read_json(self.instance / 'runner/state.json')['complete'])
        # A formal proof against an accepted formal refutation leaves the root contested, not settled.
        self.prove_root()
        self.assertEqual(replay(self.instance)['questions']['q0']['state'], 'resolved')
        self.refute_root()
        model = replay(self.instance)
        self.assertEqual(model['root_state'], 'contested')
        self.assertEqual((model['questions']['q0']['state'], model['questions']['q0']['root_settlement']), ('open', None))
        section = self.part(self.frontier(model), 'q0')
        self.assertIn('State: open', section)
        self.assertNotIn("root's formal settlement", section)
        self.assertFalse(read_json(self.instance / 'runner/state.json')['complete'])


class UnderstandingTests(QuestionCase):
    """The understanding so far of a question: where sessions receive it and read it."""

    HEADING = '# Understanding so far of the root problem as a whole (question q0)\n'

    def pack(self, role):
        """The part of a new session's starting context that carries q0's understanding."""
        engine = Runner(self.instance, self.skill)
        sid = uid('s')
        engine.session_dir(sid).mkdir(parents=True)
        engine.make_pack(sid, {'role': role, 'task': {}, 'pipeline': None})
        text = (engine.session_dir(sid) / 'pack.md').read_text(encoding='utf-8')
        self.assertEqual(text.count(self.HEADING), 1)
        return text.split(self.HEADING, 1)[1].split('\n# Board at launch\n', 1)[0]

    def reader(self):
        folder = self.instance / 'sessions/sreader'
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': 'sreader', 'role': 'attempt',
                                           'pipeline': None, 'task': {}})
        return folder

    def tool(self, *argv):
        """Run a canon_tool command and return its exit code with what it wrote to standard output."""
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding='utf-8')
        with patch('sys.stdout', stream):
            code = canon_main(list(argv))
            stream.flush()
        return code, buffer.getvalue().decode('utf-8')

    def test_the_starting_context_carries_the_understanding_so_far_of_q0(self):
        for role in ROLES:
            with self.subTest(role=role, written=False):
                self.assertIn('No exploration has written it yet.', self.pack(role))
        cid = self.account('q0')
        self.assertEqual(replay(self.instance)['questions']['q0']['state'], 'open')
        for role in ROLES:
            with self.subTest(role=role, written=True):
                received = self.pack(role)
                self.assertNotIn('No exploration has written it yet.', received)
                self.assertIn(ACCOUNT.strip(), received)
                # Review's assessment of the exploration's contribution stands with the text.
                self.assertIn('## Review', received)
                self.assertIn(f'Change {cid} (revision 1): {CONTRIBUTION}', received)
                self.assertLess(received.index(ACCOUNT.strip()), received.index('## Review'))

    def test_a_later_account_replaces_the_text_and_leaves_the_difference_in_the_history(self):
        first = self.account('q0')
        second = self.account('q0', LATER_ACCOUNT)
        canon = Canon(self.instance)
        body, review = split_review((canon.questions / 'q0.md').read_text(encoding='utf-8'))
        self.assertEqual(body, LATER_ACCOUNT)
        self.assertEqual(review, f'Change {second} (revision 2): {CONTRIBUTION}')
        # What the replacement removed is kept apart from the text a session reads.
        history = sorted((canon.history / 'questions/q0').glob('*.md'))
        self.assertEqual([p.name for p in history], ['000002.md'])
        kept = history[0].read_text(encoding='utf-8')
        self.assertIn(second, kept)
        self.assertIn('each bounds `Small.oddSum` term by term', kept)
        self.assertIn(first, kept)  # the replaced text's own review stamp
        shown = question_view(self.instance, replay(self.instance), 'q0')
        self.assertIn(LATER_ACCOUNT.strip(), shown)
        self.assertNotIn('each bounds `Small.oddSum` term by term', shown)
        self.assertNotIn(first, shown)
        # The view says that an earlier text exists, and shows it only when asked for the history.
        self.assertIn('1 earlier text of this understanding can be read with --history.', shown)
        asked = question_view(self.instance, replay(self.instance), 'q0', history=True)
        self.assertIn(LATER_ACCOUNT.strip(), asked)
        self.assertIn('## Earlier texts', asked)
        self.assertIn(kept, asked)
        self.assertIn(LATER_ACCOUNT.strip(), self.pack('explore'))

    def test_a_merge_leaves_the_surviving_question_one_understanding_and_keeps_the_absorbed_text_in_its_history(self):
        self.questions('qops', [question('op-a'), question('op-b'), question('op-c'), question('op-d')])
        self.account('op-a')                   # of op-a and op-b, only the question to be absorbed has a text
        self.account('op-c')                   # op-c and op-d both have one
        self.account('op-d', LATER_ACCOUNT)
        canon = Canon(self.instance)
        texts = {qid: (canon.questions / (qid + '.md')).read_text(encoding='utf-8') for qid in ('op-a', 'op-c', 'op-d')}
        oid = self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'},
                             {'from': 'op-c', 'into': 'op-d', 'reason': 'Both ask about the same block.'}])
        sequence = read_json(self.instance / 'knowledge/events' / (oid + '.json'))['sequence']
        # One understanding text per question that remains.
        self.assertEqual(sorted(p.name for p in canon.questions.glob('*.md')), ['op-b.md', 'op-d.md'])
        self.assertEqual((canon.questions / 'op-b.md').read_text(encoding='utf-8'), texts['op-a'])
        self.assertEqual((canon.questions / 'op-d.md').read_text(encoding='utf-8'), texts['op-d'])
        self.assertEqual(sorted(p.relative_to(canon.history).as_posix() for p in canon.history.rglob('*') if p.is_file()),
                         [f'questions/op-d/{sequence:06d}-merged-op-c.md'])
        self.assertEqual((canon.history / 'questions/op-d' / f'{sequence:06d}-merged-op-c.md').read_text(encoding='utf-8'),
                         texts['op-c'])
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        # The question command shows the surviving text, and the absorbed one when asked for the history.
        reader = self.reader()
        code, shown = self.tool('question', str(reader), 'op-d')
        self.assertEqual((code, shown.splitlines()[0]), (0, 'op-d · open'))
        self.assertIn(LATER_ACCOUNT.strip(), shown)
        self.assertNotIn(ACCOUNT.strip(), shown)
        self.assertIn('1 earlier text of this understanding can be read with --history.', shown)
        code, shown = self.tool('question', str(reader), 'op-d', '--history')
        self.assertEqual(code, 0)
        self.assertIn('## Earlier texts\n\n' + texts['op-c'], shown)
        # The question that had no text of its own reads the absorbed one, under either name.
        for qid in ('op-b', 'op-a'):
            with self.subTest(question=qid):
                code, shown = self.tool('question', str(reader), qid)
                self.assertEqual((code, shown.splitlines()[0]), (0, 'op-b · open'))
                self.assertIn(ACCOUNT.strip(), shown)
                self.assertNotIn('earlier text', shown)

    def test_the_question_command_prints_the_question_its_state_and_the_understanding_with_reviews_assessment(self):
        self.questions('qops', [question('op-scale')])
        reader = self.reader()
        code, shown = self.tool('question', str(reader), 'op-scale')
        self.assertEqual(code, 0)
        self.assertEqual(shown.splitlines()[0], 'op-scale · open')
        self.assertIn('What op-scale asks.', shown)
        self.assertIn('Grounds: ' + question('op-scale')['grounds'], shown)
        self.assertIn('No understanding has been written for this question yet.', shown)
        self.assertNotIn('## Understanding so far', shown)
        cid = self.account('op-scale', resolution_id='res')
        code, shown = self.tool('question', str(reader), 'op-scale')
        self.assertEqual(code, 0)
        self.assertEqual(shown.splitlines()[0], 'op-scale · resolved')
        self.assertNotIn('No understanding has been written', shown)
        stamp = f'Change {cid} (revision 2): {CONTRIBUTION}'
        places = [shown.index(text) for text in ('What op-scale asks.', '## Understanding so far', ACCOUNT.strip(),
                                                 '## Review of the work that wrote it', stamp)]
        self.assertEqual(places, sorted(places))
        self.assertEqual(shown, question_view(self.instance, replay(self.instance), 'op-scale') + '\n')
        # The root question is read the same way; nothing has been written for it here.
        code, shown = self.tool('question', str(reader), 'q0')
        self.assertEqual((code, shown.splitlines()[0]), (0, 'q0 · open'))
        self.assertIn('The root problem itself, taken as a whole.', shown)
        self.assertIn('No understanding has been written for this question yet.', shown)
        code, shown = self.tool('question', str(reader), 'nope')
        self.assertEqual((code, json.loads(shown)), (1, {'error': 'no such question: nope'}))


class OperatorQuestionTests(QuestionCase):
    """The questions command: the operator's publication of questions, outside peer and review."""

    def command(self, content):
        """Run the questions command on a file with the given JSON value, or raw text when a str is given."""
        source = self.root / 'operator-questions.json'
        source.write_text(content if isinstance(content, str) else json.dumps(content), encoding='utf-8')
        with patch('builtins.print') as shown:
            code = main(['questions', str(self.instance), '--file', str(source)])
        return code, json.loads(shown.call_args.args[0])

    def requests(self):
        return sorted(p.name for p in (self.instance / 'control/requests').glob('*.json'))

    def events(self):
        return sorted(p.name for p in (self.instance / 'knowledge/events').glob('*.json'))

    def test_the_command_refuses_a_file_outside_the_format_or_the_identifier_rules(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Same.'}])
        model = replay(self.instance)
        self.assertEqual(model['question_aliases'], {'op-a': 'op-b'})
        good = question('op-new')
        cases = (
            ('Expecting', '{not json'),
            ('is an object', [good]),
            ('is an object', 'null'),
            ('unknown key in a questions file: note', {'reason': 'R.', 'questions': [good], 'note': 'x'}),
            ('nonempty "reason"', {'questions': [good]}),
            ('nonempty "reason"', {'reason': '  ', 'questions': [good]}),
            ('nonempty "reason"', {'reason': 5, 'questions': [good]}),
            ('nonempty "questions" array', {'reason': 'R.'}),
            ('nonempty "questions" array', {'reason': 'R.', 'questions': []}),
            ('nonempty "questions" array', {'reason': 'R.', 'questions': {'id': 'op-new'}}),
            ('each question is an object', {'reason': 'R.', 'questions': ['op-new']}),
            ('unknown key in a question: why', {'reason': 'R.', 'questions': [{**good, 'why': 'x'}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': '-leading'}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': 'with space'}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': 'Small.root'}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': ''}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': 7}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{k: v for k, v in good.items() if k != 'id'}]}),
            ('q0 is the root question', {'reason': 'R.', 'questions': [{**good, 'id': 'q0'}]}),
            ('duplicate question id: op-new', {'reason': 'R.', 'questions': [good, good]}),
            ('already names a question or a question alias: op-b', {'reason': 'R.', 'questions': [{**good, 'id': 'op-b'}]}),
            ('already names a question or a question alias: op-a', {'reason': 'R.', 'questions': [{**good, 'id': 'op-a'}]}),
            ('question op-new needs a nonempty "statement"', {'reason': 'R.', 'questions': [{**good, 'statement': ' '}]}),
            ('question op-new needs a nonempty "statement"', {'reason': 'R.', 'questions': [{**good, 'statement': None}]}),
            ('question op-new needs a nonempty "statement"',
             {'reason': 'R.', 'questions': [{k: v for k, v in good.items() if k != 'statement'}]}),
            ('question op-new needs a nonempty "grounds"', {'reason': 'R.', 'questions': [{**good, 'grounds': ''}]}),
            ('question op-new needs a nonempty "grounds"', {'reason': 'R.', 'questions': [{**good, 'grounds': ['x']}]}),
            ('question op-new needs a nonempty "grounds"',
             {'reason': 'R.', 'questions': [{k: v for k, v in good.items() if k != 'grounds'}]}),
            # One bad question refuses the whole file.
            ('invalid question id', {'reason': 'R.', 'questions': [good, {**good, 'id': 'bad id'}]}),
        )
        requests, events = self.requests(), self.events()
        for pattern, content in cases:
            with self.subTest(pattern=pattern, content=content):
                code, answer = self.command(content)
                self.assertEqual(code, 1)
                self.assertIn(pattern, answer['error'])
        # A refused file leaves no request for the runner and nothing in the published research.
        self.assertEqual((self.requests(), self.events()), (requests, events))
        code, answer = self.command({'reason': 'R.', 'questions': [good]})
        self.assertEqual(code, 0)
        self.assertEqual(self.requests(), sorted(requests + [Path(answer['request']).name]))
        self.assertEqual(self.events(), events)

    def test_the_command_reads_a_file_with_a_byte_order_mark_and_keeps_only_the_named_fields(self):
        source = self.root / 'operator-questions.json'
        source.write_text(json.dumps({'reason': 'R.', 'questions': [question('op-new')]}), encoding='utf-8-sig')
        with patch('builtins.print') as shown:
            self.assertEqual(main(['questions', str(self.instance), '--file', str(source)]), 0, shown.call_args)
        request = read_json(Path(json.loads(shown.call_args.args[0])['request']))
        self.assertEqual(request, {'kind': 'questions', 'reason': 'R.', 'questions': [question('op-new')]})

    def test_the_runner_publishes_the_request_and_the_frontier_shows_the_operator_as_its_source(self):
        items = [question('op-scale'), question('op-block')]
        reason = 'Two places the proofs keep stalling.'
        code, answer = self.command({'reason': reason, 'questions': items})
        self.assertEqual(code, 0)
        request = Path(answer['request'])
        self.assertEqual(self.requests(), [request.name])
        self.assertEqual(read_json(request), {'kind': 'questions', 'reason': reason, 'questions': items})
        # The command writes no research: the runner is the one writer of the published events.
        self.assertEqual(self.events(), [])
        self.assertFalse((self.instance / 'knowledge/questions').exists())
        runner = Runner(self.instance, self.skill)
        runner.ingest_inputs()
        [name] = self.events()
        event = read_json(self.instance / 'knowledge/events' / name)
        eid = event['id']
        self.assertEqual(name, eid + '.json')
        self.assertEqual((event['kind'], event['folder'], event['sequence'], event['source']),
                         ('questions', 'questions/' + eid, 1, 'operator'))
        published = read_json(self.instance / 'knowledge/questions' / eid / 'questions.json')
        self.assertEqual(published, {'source': 'operator', 'reason': reason, 'questions': items, 'at': event['at']})
        self.assertEqual(sorted(p.name for p in (self.instance / 'knowledge/questions' / eid).iterdir()),
                         ['questions.json'])
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + eid), 1)
        self.assertIn('knowledge/questions/' + eid + '/questions.json',
                      git(self.instance, 'ls-files', '--', 'knowledge/questions'))
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assertIsNone(runner.state['publication'])
        self.assertIn(request.name, read_json(self.instance / 'runner/state.json')['seen_requests'])
        self.assertIsNone(runner.state['last_error'])
        model = replay(self.instance)
        for item in items:
            entry = model['questions'][item['id']]
            self.assertEqual((entry['statement'], entry['grounds'], entry['origin'], entry['source'], entry['state']),
                             (item['statement'], item['grounds'], 'operator', eid, 'open'))
        self.assertEqual(runner.model, model)
        # Nothing besides the published questions enters the model, and the runner's own rendering
        # carries them into state.json.
        self.assertEqual(set(model['questions']), {'q0'} | {item['id'] for item in items})
        self.assertEqual(model['elements'].keys(), {'Small.oddSum', 'Small.root'})
        self.assertEqual(read_json(self.instance / 'knowledge/state.json')['questions'], model['questions'])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        for item in items:
            section = self.part(frontier, item['id'])
            self.assertIn(item['statement'], section)
            self.assertIn('Grounds: ' + item['grounds'], section)
            self.assertIn('State: open', section)
            self.assertIn('Source: operator publication ' + eid, section)
        # The request is collected once.
        runner.ingest_inputs()
        Runner(self.instance, self.skill).ingest_inputs()
        self.assertEqual(self.events(), [name])

    def test_questions_collected_while_a_change_waits_for_its_build_are_published_after_it(self):
        step = module_text('/-- Adding the next odd number. -/\n'
                           'theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by\n  rfl')
        folder = self.candidate(modules={'Small/Step.lean': step},
                                records={'Small/oddSum_succ.md': record_text('Passing from n to n + 1 adds 2n + 1.')})
        runner = Runner(self.instance, self.skill)
        with patch.object(self, 'drain'):
            self.publish(folder, engine=runner, expect=False)
        # The change's publication is underway and its build has not finished when the runner collects the request.
        with patch('runner.build_outcome', return_value=None):
            runner.publish()
            waiting = runner.state['publication']
            self.assertEqual((waiting['event']['kind'], waiting['stage']), ('change', 'build'))
            code, answer = self.command({'reason': 'R.', 'questions': [question('op-scale')]})
            self.assertEqual(code, 0)
            runner.ingest_inputs()
        request = Path(answer['request']).name
        # The questions take their turn behind the change, which stays the publication underway.
        self.assertEqual((runner.state['publication']['event']['id'], runner.state['publication']['stage']),
                         (waiting['event']['id'], 'build'))
        self.assertEqual([(item['kind'], item['questions']) for item in runner.state['publish_queue']],
                         [('questions', [question('op-scale')])])
        self.assertEqual(read_json(self.instance / 'runner/state.json')['seen_requests'].count(request), 1)
        self.assertEqual(self.events(), [])
        self.drain(runner)
        events = sorted((read_json(p) for p in (self.instance / 'knowledge/events').glob('*.json')),
                        key=lambda event: event['sequence'])
        self.assertEqual([(event['kind'], event['sequence']) for event in events], [('change', 1), ('questions', 2)])
        self.assertEqual(events[0]['id'], waiting['event']['id'])
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines()[:2],
                         ['Publish ' + events[1]['id'], 'Publish ' + events[0]['id']])
        model = replay(self.instance)
        self.assertIn('Small.oddSum_succ', model['elements'])
        self.assertEqual((model['questions']['op-scale']['origin'], model['questions']['op-scale']['source']),
                         ('operator', events[1]['id']))
        # The request was collected once.
        runner.ingest_inputs()
        Runner(self.instance, self.skill).ingest_inputs()
        self.assertEqual(len(self.events()), 2)

    def test_a_restart_completes_the_same_questions_publication_after_a_failed_commit(self):
        code, answer = self.command({'reason': 'R.', 'questions': [question('op-scale')]})
        self.assertEqual(code, 0)
        runner = Runner(self.instance, self.skill)

        def broken(instance, *args):
            if args[0] == 'commit':
                raise RuntimeError('simulated unavailable commit')
            return git(instance, *args)

        with patch('runner.git', side_effect=broken), self.assertRaisesRegex(RuntimeError, 'simulated'):
            runner.ingest_inputs()
        saved = read_json(self.instance / 'runner/state.json')
        prepared = saved['publication']
        self.assertEqual(prepared['event']['kind'], 'questions')
        self.assertIn(Path(answer['request']).name, saved['seen_requests'])
        recovered = Runner(self.instance, self.skill)
        recovered.collect()
        recovered.ingest_inputs()
        recovered.collect()
        eid = prepared['event']['id']
        self.assertEqual(self.events(), [eid + '.json'])
        self.assertEqual(read_json(self.instance / 'knowledge/events' / (eid + '.json')), prepared['event'])
        self.assertEqual(read_json(self.instance / 'knowledge/questions' / eid / 'questions.json'), prepared['questions'])
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + eid), 1)
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(replay(self.instance)['questions']['op-scale']['source'], eid)

    def test_a_restart_replaces_a_stale_stage_and_writes_the_saved_content(self):
        code, answer = self.command({'reason': 'R.', 'questions': [question('op-scale')]})
        self.assertEqual(code, 0)
        runner = Runner(self.instance, self.skill)
        request = read_json(Path(answer['request']))
        reason, items = operator_questions({k: v for k, v in request.items() if k != 'kind'}, runner.model)
        # The runner ended after saving the prepared publication and while staging its files.
        runner.state['seen_requests'].append(Path(answer['request']).name)
        runner.prepare_questions({'kind': 'questions', 'reason': reason, 'questions': items, 'at': 0.0})
        prepared = runner.state['publication']
        stage = self.instance / 'runner' / ('event-' + prepared['event']['id'])
        stage.mkdir()
        (stage / 'questions.json').write_text('{"partial', encoding='utf-8')
        recovered = Runner(self.instance, self.skill)
        recovered.ingest_inputs()  # the request counts as collected; the prepared publication waits
        self.assertEqual(self.events(), [])
        recovered.collect()
        eid = prepared['event']['id']
        self.assertEqual(self.events(), [eid + '.json'])
        self.assertEqual(read_json(self.instance / 'knowledge/questions' / eid / 'questions.json'), prepared['questions'])
        self.assertEqual([p.name for p in (self.instance / 'runner').iterdir()
                          if p.name.startswith(('event-', 'stage-'))], [])
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(replay(self.instance)['questions']['op-scale']['origin'], 'operator')

    def test_an_identifier_taken_before_collection_is_refused_and_the_runner_continues(self):
        code, first = self.command({'reason': 'R.', 'questions': [question('op-scale')]})
        self.assertEqual(code, 0)
        code, second = self.command({'reason': 'R.', 'questions': [question('op-block')]})
        self.assertEqual(code, 0)
        # Between the command's check and the runner's collection, a change's review admits op-scale.
        cid, _ = self.publish(self.candidate(questions=[question('op-scale')]), role='explore')
        runner = Runner(self.instance, self.skill)
        runner.ingest_inputs()
        refused = Path(first['request']).name
        error = runner.state['last_error']
        self.assertIn('questions request ' + refused + ' refused', error['error'])
        self.assertIn('already names a question', error['error'])
        self.assertIn('op-scale', error['error'])
        saved = read_json(self.instance / 'runner/state.json')
        self.assertEqual(saved['last_error'], error)
        self.assertCountEqual(saved['seen_requests'], [refused, Path(second['request']).name])
        self.assertEqual(status(self.instance)['state']['last_error'], error)
        model = replay(self.instance)
        self.assertEqual((model['questions']['op-scale']['origin'], model['questions']['op-scale']['source']),
                         ('change', cid))
        # The other request is published in the same pass; the refused one is not collected again.
        self.assertEqual(model['questions']['op-block']['origin'], 'operator')
        self.assertEqual(len([n for n in self.events() if n != cid + '.json']), 1)
        runner.ingest_inputs()
        self.assertEqual(runner.state['last_error'], error)
        self.assertEqual(len(self.events()), 2)


class QuestionCheckTests(QuestionCase):
    def test_change_check_guards_question_proposals_and_resolutions(self):
        self.questions('qops', [question('op-scale'), question('op-old'), question('speer-taken')])
        self.organize([{'from': 'op-old', 'into': 'op-scale', 'reason': 'The same question.'}])
        model = replay(self.instance)
        change_check(self.candidate(questions=[question('speer-new')], understanding={'op-scale.md': ACCOUNT},
                                    resolutions=[resolution('res', 'op-scale')]), model, 'speer')
        # An account without a resolution only replaces the understanding so far.
        change_check(self.candidate(understanding={'op-scale.md': ACCOUNT}), model, 'speer')
        account = {'op-scale.md': ACCOUNT}
        cases = (
            ('peer session prefix: speer-', {'questions': [question('other-new')]}),
            ('peer session prefix: speer-', {'questions': [question('speer-')]}),
            ('peer session prefix: speer-', {'questions': [question('speer')]}),
            ('already names a question', {'questions': [question('speer-taken')]}),
            ('invalid identifier', {'questions': [question('speer-new id')]}),
            ('invalid identifier', {'questions': [{'statement': 'S', 'grounds': 'G'}]}),
            ('duplicate id', {'questions': [question('speer-new'), question('speer-new')]}),
            ('"id", "statement" and "grounds"', {'questions': [{'id': 'speer-x', 'statement': 'S'}]}),
            ('"id", "statement" and "grounds"', {'questions': [{**question('speer-x'), 'priority': 'high'}]}),
            ('question.statement', {'questions': [{**question('speer-x'), 'statement': ' '}]}),
            ('question.grounds', {'questions': [{**question('speer-x'), 'grounds': ''}]}),
            ('existing question', {'understanding': account, 'resolutions': [resolution('r', 'speer-x')]}),
            ('existing question', {'understanding': account, 'resolutions': [{'id': 'r'}]}),
            ('duplicate id', {'understanding': account,
                              'resolutions': [resolution('r', 'op-scale'), resolution('r', 'op-scale')]}),
            ('invalid identifier', {'understanding': account, 'resolutions': [{'question': 'op-scale'}]}),
            # A resolution is the text that settles the question, so the candidate carries that text.
            ('comes with the text that settles it, as questions/op-scale.md', {'resolutions': [resolution('r', 'op-scale')]}),
            ('comes with the text that settles it', {'understanding': {'speer-taken.md': ACCOUNT},
                                                     'resolutions': [resolution('r', 'op-scale')]}),
            ('root question', {'understanding': {'q0.md': ACCOUNT}, 'resolutions': [resolution('r', 'q0')]}),
            ('names no question of the frontier', {'understanding': {'speer-new.md': ACCOUNT}}),
            ('names no question of the frontier', {'questions': [question('speer-new')],
                                                   'understanding': {'speer-new.md': ACCOUNT}}),
            ('one file per question', {'understanding': {'op-scale/notes.md': ACCOUNT}}),
        )
        for pattern, parts in cases:
            with self.subTest(pattern=pattern, parts=parts), self.assertRaisesRegex(Invalid, pattern):
                change_check(self.candidate(**parts), model, 'speer')
        # An alias of a merged question is taken as well, and an account may be written under it.
        with self.assertRaisesRegex(Invalid, 'already names a question'):
            change_check(self.candidate(questions=[question('op-old')]), model, 'op')
        change_check(self.candidate(understanding={'op-old.md': ACCOUNT}), model, 'speer')
        # The review section of an understanding text is the runner's; a session never writes it.
        for pattern, text in (('written at publication, from review', ACCOUNT + '\n## Review\n\nIt settles the question.\n'),
                              ('is empty', ' \n')):
            folder = self.candidate(understanding={'op-scale.md': text}, prepare=False)
            with self.subTest(pattern=pattern), self.assertRaisesRegex(Invalid, pattern):
                change_check(folder, model, 'speer')
            self.assertFalse(self.prepare(folder, expect_ok=False)['ok'])

    def test_a_peers_check_reads_the_proposal_prefix_from_its_own_session(self):
        self.questions('qops', [question('op-scale')])
        for sid, proposal, errors in (('speer', 'speer-why', None), ('speer2', 'speer-why', 'peer session prefix: speer2-')):
            session = self.instance / 'sessions' / sid
            session.mkdir(parents=True)
            write_json(session / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'peer',
                                                'pipeline': None, 'task': {'question': 'op-scale'}})
            shutil.copytree(self.candidate(questions=[question(proposal)], understanding={'op-scale.md': ACCOUNT},
                                           resolutions=[resolution('res', 'op-scale')]), session / 'output')
            with self.subTest(session=sid):
                found = check_session(session)
                if errors is None:
                    self.assertEqual(found, [])
                else:
                    self.assertEqual(len(found), 1)
                    self.assertIn(errors, found[0])

    def test_assessment_check_requires_a_verdict_for_every_question_and_resolution(self):
        self.questions('qops', [question('op-scale')])
        model = replay(self.instance)
        folder = self.candidate(questions=[question('speer-new')], understanding={'op-scale.md': ACCOUNT},
                                resolutions=[resolution('res', 'op-scale')])
        out = self.root / 'review'
        out.mkdir()
        (out / 'feedback.md').write_text('Review.', encoding='utf-8')
        good = self.verdicts(folder)
        self.assertEqual(good['elements'], [])  # the change adds no element; only its question parts are judged

        def check(data):
            assessment_check(data, out, folder, model, self.instance, 's1')

        check(good)
        admitted = {'proposal': 'speer-new', 'verdict': 'admitted', 'reason': 'Important and exact.'}
        settled = {'proposal': 'res', 'resolved': True, 'reason': 'The account settles it.'}
        cases = (
            ('assess every question proposal', {'questions': []}),
            ('assess every resolution proposal', {'resolutions': []}),
            ('admitted, declined or revise', {'questions': [{**admitted, 'verdict': 'maybe'}]}),
            ('a duplicate is declined', {'questions': [{**admitted, 'verdict': 'revise', 'duplicate_of': 'op-scale'}]}),
            ('a duplicate is declined', {'questions': [{**admitted, 'duplicate_of': 'op-scale'}]}),
            ('existing question', {'questions': [{**admitted, 'verdict': 'declined', 'duplicate_of': 'nope'}]}),
            ('question assessment reason', {'questions': [{**admitted, 'reason': ''}]}),
            ('unknown/duplicate question proposal', {'questions': [admitted, admitted]}),
            ('unknown/duplicate question proposal', {'questions': [{**admitted, 'proposal': 'speer-other'}]}),
            ('resolved must be Boolean', {'resolutions': [{**settled, 'resolved': 'yes'}]}),
            ('resolution reason', {'resolutions': [{**settled, 'reason': ' '}]}),
            ('unknown/duplicate resolution proposal', {'resolutions': [settled, settled]}),
            ('unknown/duplicate resolution proposal', {'resolutions': [{**settled, 'proposal': 'other'}]}),
        )
        for pattern, changed in cases:
            with self.subTest(pattern=pattern, changed=changed), self.assertRaisesRegex(Invalid, pattern):
                check({**good, **changed})
        check({**good, 'questions': [{**admitted, 'verdict': 'declined', 'duplicate_of': 'op-scale'}]})
        check({**good, 'questions': [{**admitted, 'verdict': 'revise'}], 'resolutions': [{**settled, 'resolved': False}]})
        # A candidate that review excludes changes nothing: no question is admitted and none resolved.
        declined = [{**admitted, 'verdict': 'declined', 'reason': 'Nothing to keep.'}]
        unsettled = [{**settled, 'resolved': False, 'reason': 'Not shown.'}]
        for changed in ({'resolutions': unsettled}, {'questions': declined}):
            with self.subTest(excluded=sorted(changed)), self.assertRaisesRegex(Invalid, 'excluded candidate'):
                check({**good, 'publish': False, **changed})
        check({**good, 'publish': False, 'questions': declined, 'resolutions': unsettled})

    def test_no_research_is_open_to_explorers_holding_no_question(self):
        folder = self.instance / 'sessions/sx'
        (folder / 'output').mkdir(parents=True)
        write_json(folder / 'output/outcome.json', {'disposition': 'no_research'})
        self.assertEqual(no_research_outcome(folder, 'explore'), {'disposition': 'no_research'})
        write_json(folder / 'declaration.json', {'question': {'id': 'q0', 'at': 1, 'by': 'runner'}, 'at': 1})
        with self.assertRaisesRegex(ValueError, 'occupied question'):
            no_research_outcome(folder, 'explore')
        (folder / 'declaration.json').unlink()
        write_json(folder / 'output/outcome.json', {'disposition': 'no_research', 'availability': {
            'status': 'all_unresolved_work_occupied', 'snapshot': '0' * 64}})
        with self.assertRaisesRegex(ValueError, 'only attempts report'):
            no_research_outcome(folder, 'explore')
        with self.assertRaisesRegex(ValueError, 'only attempts and explorers'):
            no_research_outcome(folder, 'formalizer')


class QuestionCoordinationTests(QuestionCase):
    def setUp(self):
        super().setUp()
        self.engine = Runner(self.instance, self.skill)

    def ask(self, *ids):
        """The operator places questions; the test's runner then reads what that publication saved."""
        self.questions('qops', [question(qid) for qid in ids])
        self.engine.state = read_json(self.engine.state_path)
        self.engine.model = replay(self.instance)

    def session(self, sid, role='explore'):
        runner = self.engine
        key = runner.producer(role)
        job = runner.state['jobs'][key]
        folder = runner.session_dir(sid)
        folder.mkdir(parents=True)
        (folder / 'inbox').mkdir()
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'pipeline': job['pipeline'], 'task': {}, 'user_inputs': []})
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        runner.state['sessions'][sid] = {'id': sid, 'role': role, 'job': key, 'status': 'running'}
        job.update(status='running', session=sid)
        runner.save()
        return folder

    def end_pipeline(self, folder):
        pipeline = read_json(folder / 'input.json')['pipeline']
        self.engine.state['pipelines'][pipeline]['stage'] = 'done'
        self.engine.save()

    def board_text(self):
        render(self.instance, self.engine.model, board(self.instance, self.engine.state))
        return (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')

    def test_explorer_takes_one_question_through_its_lease(self):
        self.ask('op-scale', 'op-block')
        a, b = self.session('sa'), self.session('sb')
        # While q0 is free, an explorer takes it before any narrower question.
        self.assertIn('q0', question_lease(a, 'op-scale')['reason'])
        root = self.session('sroot')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        taken = question_take(root, 'q0')
        self.assertTrue(taken['taken'], taken)
        self.assertEqual((taken['question'], taken['occupied_by'], taken['holders']), ('q0', ['sroot'], []))
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        refused = question_lease(b, 'op-scale')
        self.assertFalse(refused['leased'])
        self.assertEqual(refused['holders'], ['sa'])
        self.assertIn('lease', question_take(b, 'op-scale')['reason'])
        taken = question_take(a, 'op-scale')
        self.assertTrue(taken['taken'], taken)
        held = read_json(a / 'declaration.json')['question']
        self.assertEqual((held['id'], held['by']), ('op-scale', 'session'))
        self.assertNotIn('op-scale', question_lease_table(self.instance))
        # An explorer holds one question; a question another exploration holds is refused.
        self.assertTrue(question_lease(a, 'op-block')['leased'])
        self.assertIn('already occupies question op-scale', question_take(a, 'op-block')['reason'])
        question_release(a, 'op-block')
        self.assertNotIn('op-block', question_lease_table(self.instance))
        refused = question_lease(b, 'op-scale')
        self.assertIn('holds this question', refused['reason'])
        self.assertEqual(refused['occupied_by'], ['sa'])
        self.assertIn('holds this question', question_wait(b, 'op-scale', timeout=0)['reason'])
        self.assertFalse((b / 'declaration.json').exists())
        self.assertEqual(question_lease_table(self.instance), {})
        rows = {r['session']: r['question'] for r in board(self.instance, self.engine.state)}
        self.assertEqual(rows, {'sa': 'op-scale', 'sb': None, 'sroot': 'q0'})
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual(view['free'], ['op-block'])
        self.assertEqual(view['occupied'], {'q0': ['sroot'], 'op-scale': ['sa']})
        self.assertEqual(view['choosing'], [read_json(b / 'input.json')['pipeline']])
        answer = updates(b)
        listed = {q['id']: (q['state'], q['occupied_by'], q['free']) for q in answer['questions']}
        self.assertEqual(listed, {'q0': ('open', ['sroot'], False), 'op-scale': ('open', ['sa'], False),
                                  'op-block': ('open', [], True)})
        self.assertEqual(answer['questions'][1]['statement'], 'What op-scale asks.')
        self.assertEqual({r['session']: r['question'] for r in answer['board']}, rows)
        self.assertIsNone(answer['availability_snapshot'])  # only an attempt receives one
        visible = self.board_text()
        self.assertIn('· producer: sa · explore · producing · question: op-scale', visible)
        self.assertIn('· producer: sroot · explore · producing · question: q0', visible)
        self.assertIn('· producer: sb · explore · producing · question: (choosing)', visible)
        reported = status(self.instance)['questions']
        self.assertEqual({key: reported[key] for key in ('free', 'occupied', 'choosing')}, view)

    def test_waiters_receive_the_question_lease_in_order_and_a_resolved_question_is_refused(self):
        self.ask('op-scale')
        a, b, c = self.session('sa'), self.session('sb'), self.session('sc')
        # Another explorer holds q0, so the narrower question can be leased.
        root = self.session('sroot')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_take(root, 'q0')['taken'])
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        self.assertEqual(question_wait(b, 'op-scale', timeout=0)['position'], 1)
        waiting = question_wait(c, 'op-scale', timeout=0)
        self.assertEqual((waiting['leased'], waiting['waiting'], waiting['timeout'], waiting['position']),
                         (False, True, True, 2))
        self.assertEqual((waiting['holders'], waiting['queue']), (['sa'], ['sb', 'sc']))
        leases = updates(b)['question_leases']['op-scale']
        self.assertEqual(([h['session'] for h in leases['holders']], [w['session'] for w in leases['queue']]),
                         (['sa'], ['sb', 'sc']))
        # A held lease blocks the runner from counting the question as free.
        self.assertEqual(question_availability(self.instance, self.engine.state)['free'], [])
        question_release(a, 'op-scale')
        # The lease passes to the longest waiter, not to whoever asks first.
        self.assertEqual(question_wait(c, 'op-scale', timeout=0)['position'], 1)
        self.assertFalse(question_lease(c, 'op-scale')['leased'])
        self.assertTrue(question_wait(b, 'op-scale', timeout=0)['leased'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])
        self.account('op-scale', resolution_id='res', engine=self.engine)
        d = self.session('sd')
        self.assertIn('resolved', question_lease(d, 'op-scale')['reason'])
        self.assertIn('resolved', question_wait(d, 'op-scale', timeout=0)['reason'])
        self.assertIn('holds this question', question_lease(d, 'q0')['reason'])
        listed = {q['id']: (q['state'], q['free']) for q in updates(d)['questions']}
        self.assertEqual(listed['op-scale'], ('resolved', False))

    def test_a_narrower_question_is_refused_while_the_root_question_is_free(self):
        self.ask('op-scale')
        a, b = self.session('sa'), self.session('sb')
        # An explorer still choosing when q0 becomes free takes q0, as the runner's assignment would have.
        self.assertIn('q0', question_lease(a, 'op-scale')['reason'])
        self.assertIn('q0', question_wait(a, 'op-scale', timeout=0)['reason'])
        # The refusals recorded nothing.
        self.assertEqual(question_lease_table(self.instance), {})
        self.assertFalse((a / 'declaration.json').exists())
        self.assertTrue(question_lease(a, 'q0')['leased'])
        # Once another explorer holds q0's lease, a narrower question can be taken.
        self.assertTrue(question_lease(b, 'op-scale')['leased'])
        self.assertTrue(question_take(a, 'q0')['taken'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])

    def test_a_take_is_refused_once_the_question_is_resolved_or_q0_is_free_under_the_lease(self):
        self.ask('op-scale', 'op-block')
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        # A lease on q0 keeps q0 from counting as free, so both narrower questions can be leased.
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        self.assertTrue(question_lease(b, 'op-block')['leased'])
        self.account('op-scale', resolution_id='res', engine=self.engine)
        resolved = question_take(a, 'op-scale')
        self.assertFalse(resolved['taken'])
        self.assertIn('resolved', resolved['reason'])
        question_release(root, 'q0')
        overtaken = question_take(b, 'op-block')
        self.assertFalse(overtaken['taken'])
        self.assertIn('Lease and take q0', overtaken['reason'])
        # Each refusal records nothing and keeps the lease.
        for folder, qid, sid in ((a, 'op-scale', 'sa'), (b, 'op-block', 'sb')):
            self.assertFalse((folder / 'declaration.json').exists())
            self.assertEqual([h['session'] for h in question_lease_table(self.instance)[qid]['holders']], [sid])

    def test_a_formally_settled_root_closes_q0_without_cutting_its_holder_short(self):
        self.ask('op-scale')
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_take(root, 'q0')['taken'])
        self.prove_root(engine=self.engine)
        self.assertEqual(self.engine.model['root_state'], 'formal_proved')
        self.assertEqual(self.engine.model['questions']['q0']['state'], 'resolved')
        # The exploration that held q0 keeps it through its peer and review.
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied'], view['free']), ({'q0': ['sroot']}, ['op-scale']))
        self.assertEqual([r['question'] for r in board(self.instance, self.engine.state)
                          if r['session'] == 'sroot'], ['q0'])
        self.assertIn('· producer: sroot · explore · producing · question: q0', self.board_text())
        # Once that pipeline ends, the resolved q0 is neither free nor takeable, and it no longer
        # holds back a narrower question for an explorer still choosing.
        self.end_pipeline(root)
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied'], view['free']), ({}, ['op-scale']))
        refused = question_lease(a, 'q0')
        self.assertFalse(refused['leased'])
        self.assertIn('formally settled', refused['reason'])
        self.assertIn('formally settled', question_wait(a, 'q0', timeout=0)['reason'])
        self.assertEqual(question_lease_table(self.instance), {})
        self.assertTrue(question_lease(b, 'op-scale')['leased'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])
        answer = updates(a)
        listed = {q['id']: q for q in answer['questions']}
        self.assertEqual((listed['q0']['state'], listed['q0']['free']), ('resolved', False))
        self.assertEqual(answer['root_state'], 'formal_proved')
        self.assertEqual(status(self.instance)['questions']['free'], [])

    def test_a_merge_of_two_held_questions_leaves_both_explorers_holding_it_until_each_pipeline_ends(self):
        # An organizer's merge is an exception to one explorer per question: occupations taken before
        # the merge continue to their own ends, and meanwhile the merged question is not free to any
        # further explorer.
        self.ask('op-a', 'op-b')
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        for folder, qid in ((root, 'q0'), (a, 'op-a'), (b, 'op-b')):
            self.assertTrue(question_lease(folder, qid)['leased'])
            self.assertTrue(question_take(folder, qid)['taken'])
        self.organize([{'from': 'op-a', 'into': 'op-b', 'reason': 'Same scale.'}], engine=self.engine)
        self.assertEqual(self.engine.model['question_aliases'], {'op-a': 'op-b'})
        rows = {r['session']: r['question'] for r in board(self.instance, self.engine.state)}
        self.assertEqual(rows, {'sroot': 'q0', 'sa': 'op-b', 'sb': 'op-b'})
        # The declaration keeps the identifier the explorer took; the alias leads to the merged question.
        self.assertEqual(read_json(a / 'declaration.json')['question']['id'], 'op-a')
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((sorted(view['occupied']['op-b']), view['free']), (['sa', 'sb'], []))
        self.assertFalse(self.engine.question_slot())  # the runner launches no explorer for the merged question
        listed = {q['id']: (sorted(q['occupied_by']), q['free']) for q in updates(b)['questions']}
        self.assertEqual(listed['op-b'], (['sa', 'sb'], False))
        self.assertNotIn('op-a', listed)
        self.assertEqual(self.board_text().count('· explore · producing · question: op-b'), 2)
        # A further explorer can take the merged question under neither identifier.
        c = self.session('sc')
        for qid in ('op-b', 'op-a'):
            refused = question_lease(c, qid)
            self.assertFalse(refused['leased'])
            self.assertIn('hold this question', refused['reason'])
            self.assertEqual(refused['question'], 'op-b')
            self.assertEqual(sorted(refused['occupied_by']), ['sa', 'sb'])
        # The occupations end separately; the question stays held while either lasts.
        self.end_pipeline(a)
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied']['op-b'], view['free']), (['sb'], []))
        self.assertIn('holds this question', question_lease(c, 'op-b')['reason'])
        self.end_pipeline(b)
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['free'], 'op-b' in view['occupied']), (['op-b'], False))
        self.assertTrue(question_lease(c, 'op-a')['leased'])
        taken = question_take(c, 'op-b')
        self.assertTrue(taken['taken'], taken)
        self.assertEqual(taken['question'], 'op-b')
        self.assertEqual(read_json(c / 'declaration.json')['question']['id'], 'op-b')

    def test_only_explorers_use_question_commands(self):
        for role in ('attempt', 'peer', 'review', 'formalizer', 'organizer'):
            # The commands decide by the role in the session's own input.json.
            folder = self.instance / 'sessions' / ('s' + role)
            folder.mkdir(parents=True)
            write_json(folder / 'input.json', {'instance': str(self.instance), 'session': folder.name, 'role': role,
                                               'pipeline': None, 'task': {}, 'user_inputs': []})
            for command in (question_lease, question_take, question_release):
                with self.subTest(role=role, command=command.__name__), self.assertRaisesRegex(ValueError, 'only explorers'):
                    command(folder, 'q0')
            with self.subTest(role=role, command='question_wait'), self.assertRaisesRegex(ValueError, 'only explorers'):
                question_wait(folder, 'q0', timeout=0)
            self.assertFalse((folder / 'declaration.json').exists())
        self.assertEqual(question_lease_table(self.instance), {})
        # Any session reads the questions and who holds them.
        listed = updates(self.session('sreader', role='attempt'))['questions']
        self.assertEqual([(q['id'], q['free']) for q in listed], [('q0', True)])

    def test_question_commands_answer_through_the_command_line_with_the_documented_exit_codes(self):
        # Explorers reach these commands only through the argv in input.json; the entry point is checked here.
        self.ask('op-scale')
        a, b, c = self.session('sa'), self.session('sb'), self.session('sc')
        attempt = self.session('sattempt', role='attempt')

        def run(*argv):
            with patch('sys.argv', ['coordination.py', *argv]), patch('builtins.print') as shown:
                code = coordination_main()
            return code, json.loads(shown.call_args.args[0])

        code, answer = run('question-lease', str(a), 'op-scale')
        self.assertEqual((code, answer['leased']), (1, False))
        self.assertIn('Lease and take q0', answer['reason'])
        code, answer = run('question-take', str(a), 'q0')
        self.assertEqual((code, answer['taken']), (1, False))
        self.assertIn('lease', answer['reason'])
        code, answer = run('question-lease', str(a), 'q0')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('question-take', str(a), 'q0')
        self.assertEqual((code, answer['taken'], answer['question']), (0, True, 'q0'))
        self.assertEqual(read_json(a / 'declaration.json')['question']['by'], 'session')
        code, answer = run('question-lease', str(b), 'q0')
        self.assertEqual(code, 1)
        self.assertIn('holds this question', answer['reason'])
        code, answer = run('question-wait', str(b), 'q0', '--timeout', '0')
        self.assertEqual((code, answer['leased']), (1, False))
        self.assertNotIn('timeout', answer)
        code, answer = run('question-lease', str(b), 'op-scale')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('question-wait', str(c), 'op-scale', '--timeout', '0')
        self.assertEqual((code, answer['timeout'], answer['position']), (124, True, 1))
        code, answer = run('question-release', str(c), 'op-scale')
        self.assertEqual((code, answer['released'], answer['queue']), (0, True, []))
        code, answer = run('question-wait', str(b), 'op-scale', '--timeout', '0')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('question-take', str(b), 'op-scale')
        self.assertEqual((code, answer['taken']), (0, True))
        code, answer = run('question-lease', str(b), 'nope')
        self.assertEqual((code, answer['error']), (1, 'unknown question'))
        code, answer = run('question-lease', str(attempt), 'q0')
        self.assertEqual(code, 1)
        self.assertIn('only explorers', answer['error'])
        code, answer = run('updates', str(attempt))
        self.assertEqual(code, 0)
        self.assertEqual({q['id']: q['occupied_by'] for q in answer['questions']}, {'q0': ['sa'], 'op-scale': ['sb']})


class QuestionDispatchTests(QuestionCase):
    def runner(self):
        return Runner(self.instance, self.skill)

    def occupy_root(self, runner):
        """An attempt holding the whole root, so that no element is available to a new attempt."""
        key = runner.producer('attempt')
        job = runner.state['jobs'][key]
        sid = 'sholder'
        folder = runner.session_dir(sid)
        folder.mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'attempt',
                                           'pipeline': job['pipeline'], 'task': {}})
        write_json(folder / 'declaration.json', {'sections': [
            {'id': sid + '-1', 'element': 'Small.root', 'whole': True, 'statement': None, 'new': None,
             'reasons': {}, 'at': 1}], 'at': 1})
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        runner.state['sessions'][sid] = {'id': sid, 'role': 'attempt', 'job': key, 'status': 'running'}
        job.update(status='running', session=sid)
        runner.save()

    def ended_explorer(self, runner, held):
        key = runner.producer('explore')
        job = runner.state['jobs'][key]
        sid = 'sexplorer' + str(len(runner.state['sessions']))
        folder = runner.session_dir(sid)
        for name in ('output', 'work', 'inbox'):
            (folder / name).mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'explore',
                                           'pipeline': job['pipeline'], 'task': {}, 'user_inputs': []})
        (folder / 'cli.stdout.jsonl').write_text(json.dumps(
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'A retained observation.'}}), encoding='utf-8')
        (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        if held:
            write_json(folder / 'declaration.json', {'question': {'id': held, 'at': 1, 'by': 'runner'}, 'at': 1})
            (folder / 'work/notes.md').write_text('An unfinished observation.', encoding='utf-8')
        session = {'id': sid, 'role': 'explore', 'job': key, 'model': 'codex/gpt-6.1-sol', 'provider': 'codex',
                   'started_at': 1, 'status': 'running', 'exit_code': 0, 'host': None, 'cli': None}
        runner.state['sessions'][sid] = session
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        job.update(status='running', session=sid)
        runner.save()
        return sid, session, job, folder

    def board_text(self, runner):
        render(self.instance, runner.model, board(self.instance, runner.state, runner.model))
        return (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')

    def test_runner_assigns_the_root_question_when_it_is_free(self):
        runner = self.runner()
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            first = runner.producer('explore')
            self.assertTrue(runner.dispatch(first))
            sid = runner.state['jobs'][first]['session']
            self.assertEqual(runner.state['jobs'][first]['task']['question'], 'q0')
            held = read_json(runner.session_dir(sid) / 'declaration.json')['question']
            self.assertEqual((held['id'], held['by']), ('q0', 'runner'))
            self.assertEqual(read_json(runner.session_dir(sid) / 'input.json')['task']['question'], 'q0')
            self.assertIn('"question": "q0"', (runner.session_dir(sid) / 'pack.md').read_text(encoding='utf-8'))
            self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'], {'q0': [sid]})
            self.assertIn(f'· producer: {sid} · explore · producing · question: q0', self.board_text(runner))
            # With the root question occupied, a further explorer launches without an assignment and chooses.
            self.questions('qops', [question('op-scale')])
            runner.model = replay(self.instance)
            second = runner.producer('explore')
            self.assertTrue(runner.dispatch(second))
            later = runner.state['jobs'][second]['session']
            self.assertNotIn('question', runner.state['jobs'][second]['task'])
            self.assertFalse((runner.session_dir(later) / 'declaration.json').exists())
        self.assertFalse(runner.question_slot())  # one free question, one explorer still choosing
        self.assertTrue(question_lease(runner.session_dir(later), 'op-scale')['leased'])
        self.assertTrue(question_take(runner.session_dir(later), 'op-scale')['taken'])
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], [])

    def test_root_assignment_is_saved_before_the_explorer_launches(self):
        runner = self.runner()
        seen = []
        prepare = runner.make_pack

        def observe(sid, job):
            # An explorer's question command reads the saved state, not the runner's memory.
            seen.append((question_availability(self.instance)['occupied'],
                         read_json(self.instance / 'runner/state.json')['jobs'][job['id']]['task'].get('question'),
                         read_json(runner.session_dir(sid) / 'declaration.json')['question']['by']))
            return prepare(sid, job)

        with patch.object(runner, 'make_pack', side_effect=observe), patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(runner.producer('explore')))
            host.assert_called_once()
        self.assertEqual([(list(occupied), assigned, by) for occupied, assigned, by in seen], [(['q0'], 'q0', 'runner')])

    def test_occupied_elements_fill_free_questions_with_explorers_one_request_at_a_time(self):
        self.questions('qops', [question('op-scale'), question('op-block')])
        runner = self.runner()
        runner.settings['max_sessions'] = 8
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        self.assertEqual(runner.available_elements(), ['Small.root'])
        self.occupy_root(runner)
        self.assertEqual(runner.available_elements(), [])
        self.assertFalse(runner.state['explore_requested'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        explorers = [sid for sid, s in runner.active() if s['role'] == 'explore']
        self.assertEqual(len(explorers), 3)
        assigned = [read_json(runner.session_dir(sid) / 'declaration.json')['question']['id']
                    for sid in explorers if (runner.session_dir(sid) / 'declaration.json').exists()]
        self.assertEqual(assigned, ['q0'])
        # The request is renewed while the elements stay occupied, and waits for a free question.
        self.assertTrue(runner.state['explore_requested'])
        self.assertFalse(runner.question_slot())
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual(len([s for _, s in runner.active() if s['role'] == 'explore']), 3)
        self.assertFalse(any(s['role'] == 'attempt' and sid != 'sholder' for sid, s in runner.active()))

    def test_request_outlives_a_missing_question_and_is_served_first_when_one_frees(self):
        runner = self.runner()
        runner.settings['max_sessions'] = 2
        # One launch per pass: the attempt launched first must not be followed by another in the same pass.
        runner.settings['launch_interval'] = 3600
        # The attempt launched below must not renew the request itself; otherwise the request
        # would appear to survive even if the runner had dropped it for want of a free question.
        runner.settings['explore_every'] = 1000
        previous = runner.producer('explore')
        runner.state['jobs'][previous]['status'] = 'done'
        pipeline = runner.state['pipelines'][runner.state['jobs'][previous]['pipeline']]
        pipeline.update(stage='review', producer='sprevious')
        runner.session_dir('sprevious').mkdir()
        write_json(runner.session_dir('sprevious') / 'declaration.json',
                   {'question': {'id': 'q0', 'at': 1, 'by': 'runner'}, 'at': 1})
        runner.state['explore_requested'] = True
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
            self.assertEqual([s['role'] for _, s in runner.active()], ['attempt'])
            self.assertTrue(runner.state['explore_requested'])
            pipeline['stage'] = 'done'
            runner.save()
            runner.state['last_launch'] = 0
            runner.schedule()
        self.assertEqual(sorted(s['role'] for _, s in runner.active()), ['attempt', 'explore'])
        self.assertFalse(runner.state['explore_requested'])
        explorer = next(sid for sid, s in runner.active() if s['role'] == 'explore')
        self.assertEqual(read_json(runner.session_dir(explorer) / 'declaration.json')['question']['id'], 'q0')

    def test_question_stays_occupied_through_peer_and_review(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, 'q0')
        runner.finish(sid, session)
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(pipeline['stage'], 'peer')
        peer = runner.state['jobs'][pipeline['id'] + ':peer']
        self.assertEqual(peer['task']['question'], 'q0')
        self.assertEqual(peer['task']['sections'], [])
        self.assertEqual(peer['task']['source_role'], 'explore')
        view = question_availability(self.instance, runner.state, runner.model)
        self.assertEqual((view['occupied'], view['free']), ({'q0': [sid]}, []))
        rows = board(self.instance, runner.state, runner.model)
        self.assertEqual([(r['stage'], r['question']) for r in rows], [('peer', 'q0')])
        self.assertIn(f'· producer: {sid} · explore · peer · question: q0', self.board_text(runner))
        pipeline['stage'] = 'review'
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], [])
        pipeline['stage'] = 'done'
        runner.save()
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], ['q0'])

    def test_a_question_stays_occupied_when_its_candidate_goes_to_a_replacement_peer(self):
        runner = self.runner()
        # The candidate cannot be published on the canon as it is: one of its records belongs to no declaration.
        folder = self.candidate(understanding={'q0.md': ACCOUNT},
                                records={'Small/ghost.md': record_text('A record without a declaration.')}, prepare=False)
        self.assertFalse(self.prepare(folder, expect_ok=False)['ok'])
        record, _ = self.publish(folder, self.verdicts(folder), role='explore', question='q0', engine=runner, expect=False)
        self.assertIsNone(record)
        [pipeline] = [p for p in runner.state['pipelines'].values() if p['role'] == 'explore']
        self.assertEqual(pipeline['stage'], 'peer')
        [peer] = [j for j in runner.state['jobs'].values() if j['role'] == 'peer' and j['status'] == 'pending']
        self.assertEqual(peer['task']['question'], 'q0')
        self.assertIn('could not be published on the current canon', peer['task']['previous_error'])
        # Nothing of the candidate was published, and the question stays with the exploration.
        self.assertEqual(replay(self.instance)['sequence'], 0)
        self.assertFalse((Canon(self.instance).questions / 'q0.md').exists())
        view = question_availability(self.instance, runner.state, runner.model)
        self.assertEqual((view['occupied'], view['free']), ({'q0': [pipeline['producer']]}, []))
        self.assertIn(f"· producer: {pipeline['producer']} · explore · peer · question: q0", self.board_text(runner))

    def test_a_relaunch_takes_the_root_question_that_its_failed_launch_held(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, 'q0')
        job['task']['question'] = 'q0'
        # The launch retained nothing, so the job is retried rather than sent to a peer.
        (folder / 'work/notes.md').unlink()
        (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        runner.finish(sid, session)
        self.assertEqual((job['status'], session['status']), ('pending', 'failed'))
        job['not_before'] = 0
        runner.state['blocks'].clear()
        self.assertTrue(runner.question_slot(launching=True))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertNotIn(job['session'], (None, sid))
        self.assertEqual(job['task']['question'], 'q0')
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'],
                         {'q0': [job['session']]})

    def test_waiting_explorations_do_not_yield_to_each_other_over_one_free_question(self):
        runner = self.runner()
        first, second = runner.producer('explore'), runner.producer('explore')
        # Two explorations wait to launch and the root question is the only free one. Each job is
        # decided against the launches before it, not against the other waiting job; otherwise
        # both would yield and q0 would stay free with the request in force.
        self.assertTrue(runner.question_slot(launching=True))
        self.assertFalse(runner.question_slot())
        visible = self.board_text(runner)
        self.assertEqual(visible.count('· producer: (not launched) · explore · queued · question: (choosing)'), 2)
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(sorted(runner.state['jobs'][key]['status'] for key in (first, second)), ['pending', 'running'])
        launched = next(key for key in (first, second) if runner.state['jobs'][key]['status'] == 'running')
        self.assertEqual(runner.state['jobs'][launched]['task']['question'], 'q0')
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], [])

    def test_two_pending_explorations_do_not_hold_each_other_back(self):
        self.questions('qops', [question('op-scale')])
        runner = self.runner()
        first, first_session, first_job, first_folder = self.ended_explorer(runner, 'q0')
        second, second_session, second_job, second_folder = self.ended_explorer(runner, None)
        # Neither launch retained research material, so both jobs are pending again while their
        # pipelines still name the failed sessions: one declaring q0, the other having chosen nothing.
        (first_folder / 'work/notes.md').unlink()
        for folder in (first_folder, second_folder):
            (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        runner.finish(first, first_session)
        runner.finish(second, second_session)
        self.assertEqual((first_job['status'], second_job['status']), ('pending', 'pending'))
        # The question the second explorer would have chosen was resolved meanwhile, so q0 is the
        # only open question. Counting the other pending exploration as a chooser, or as q0's holder,
        # would leave both waiting for each other.
        self.account('op-scale', resolution_id='res', engine=runner)
        self.assertEqual(runner.model['questions']['op-scale']['state'], 'resolved')
        for job in (first_job, second_job):
            job['not_before'] = 0
        runner.state['blocks'].clear()
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertEqual(sorted(j['status'] for j in (first_job, second_job)), ['pending', 'running'])
        launched = first_job if first_job['status'] == 'running' else second_job
        self.assertEqual(launched['task']['question'], 'q0')
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'],
                         {'q0': [launched['session']]})

    def test_explorer_finding_no_free_question_closes_without_peer(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, None)
        write_json(folder / 'output/outcome.json', {'disposition': 'no_research'})
        self.assertEqual(check_session(folder), [])
        runner.finish(sid, session)
        self.assertEqual(session['disposition'], 'no_research')
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'done')
        self.assertFalse(any(j['role'] == 'peer' for j in runner.state['jobs'].values()))
        self.assertFalse(runner.state['explore_requested'])
        self.assertIsNone(runner.state['attempt_dispatch_gate'])  # only an attempt's report holds attempts back

    def test_an_exploration_that_reached_peer_without_a_question_is_not_choosing(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, None)
        # An interrupted explorer with retained material goes to peer even though it took no question.
        session['exit_code'] = 1
        runner.finish(sid, session)
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'peer')
        self.assertIsNone(runner.state['jobs'][job['pipeline'] + ':peer']['task']['question'])
        view = question_availability(self.instance, runner.state, runner.model)
        self.assertEqual((view['free'], view['choosing']), (['q0'], []))
        self.assertTrue(runner.question_slot())
        self.assertIn(f'· producer: {sid} · explore · peer · question: (none)', self.board_text(runner))

    def test_status_reports_question_availability(self):
        runner = self.runner()
        sid = self.ended_explorer(runner, 'q0')[0]
        result = status(self.instance)
        self.assertEqual(result['questions'], {'free': [], 'occupied': {'q0': [sid]}, 'choosing': [],
                                               'explore_requested': False})
        self.assertEqual(result['root_state'], 'unresolved')
        self.assertEqual([(r['session'], r['question']) for r in result['board']], [(sid, 'q0')])

    def test_a_busy_coordination_lock_leaves_the_explorer_queued_and_the_runner_running(self):
        runner = self.runner()
        # One slot, so the attempt launch that would follow the explorer (and request the next
        # exploration) does not hide whether the explorer's launch consumed the request.
        runner.settings['max_sessions'] = 1
        runner.state['explore_requested'] = True
        busy = RuntimeError('another coordination change is still in progress; run the command again')
        with patch('runner.claims_lock', side_effect=busy), patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        jobs = [j for j in runner.state['jobs'].values() if j['role'] == 'explore']
        self.assertEqual([j['status'] for j in jobs], ['pending'])
        self.assertEqual(runner.active(), [])
        self.assertEqual(list((self.instance / 'sessions').iterdir()), [])
        self.assertTrue(runner.state['explore_requested'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        self.assertEqual(jobs[0]['status'], 'running')
        self.assertEqual(jobs[0]['task']['question'], 'q0')
        self.assertFalse(runner.state['explore_requested'])

    def test_a_settled_root_cancels_a_waiting_exploration(self):
        runner = self.runner()
        waiting = runner.producer('explore')
        self.prove_root(engine=runner)
        self.assertTrue(runner.state['complete'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
            host.assert_not_called()
        job = runner.state['jobs'][waiting]
        self.assertEqual((job['status'], runner.state['pipelines'][job['pipeline']]['stage']), ('cancelled', 'done'))
        self.assertEqual([s['role'] for _, s in runner.active()], [])
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], [])


if __name__ == '__main__':
    unittest.main()
