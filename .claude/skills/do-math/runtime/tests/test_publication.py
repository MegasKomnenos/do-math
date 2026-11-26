"""The publication path of the runner through real builds, and the transport checks of check.py.

A publication applies a reviewed candidate to a copy of the canon, builds it through the broker,
checks by machine what changed, and only then puts it in place (design record, section 10). The
tests publish small real candidates and then read the canon, the event and the Git history. A
candidate that cannot be published is followed to the replacement peer that receives it.
"""
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import unittest
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import runner as runtime
from canon import Canon, declaration_text, parse_approach, tree_hash
from canon_tool import build_candidate, verify
from check import carried_by, change_check, check_session
from knowledge import replay
from runtime_support import git, read_json, write_json
from support import InstanceCase, ROOT, SUM_ZERO, module_text, record_text, theorem

DOC = '/-- The sum of the first `n` odd numbers is the square of `n`. -/\n'
STATEMENT = 'theorem root (n : Nat) : oddSum n = n * n := by\n'
ORIGINAL = DOC + STATEMENT + '  sorry'
# An informal proof names in Lean what it rests on and ends in sorry.
INFORMAL = DOC + STATEMENT + '  have step := oddSum_succ\n  sorry'
FORMAL = DOC + STATEMENT + '  induction n with\n  | zero => rfl\n  | succ k ih => rw [oddSum_succ, ih]; omega'
SKETCH = DOC + STATEMENT + '  -- induction on n; the step adds 2 * n + 1\n  sorry'
PAIRING = DOC + STATEMENT + '  -- pair the k-th odd number with the gnomon of the k-th square\n  sorry'
STEP = module_text('''/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl''')
ZERO = module_text('''/-- The empty sum. -/
theorem oddSum_zero : oddSum 0 = 0 := by
  rfl''')
ROOT_RECORD = record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                          short='odd numbers sum to a square',
                          statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                          proof='By induction on $n$: adding the next odd number $2k + 1$ to $k^2$ gives $(k + 1)^2$.')
STEP_RECORD = record_text('Passing from n to n + 1 adds the odd number 2n + 1 to the sum.', short='next odd number')
ZERO_RECORD = record_text('The sum of no odd numbers is zero.', short='empty sum')
APPROACH = '''---
title: Induction on the number of terms
sessions: sauthor
---
## Idea

Compare the sum for n + 1 with the sum for n.

## Established

Small.oddSum_succ

## Where it stops

The inductive step is stated; the arithmetic identity has not been checked in Lean.
'''
FURTHER = APPROACH.replace('sessions: sauthor', 'sessions: sauthor, slater').replace(
    'The inductive step is stated; the arithmetic identity has not been checked in Lean.',
    'The arithmetic identity is checked by hand for every n; only its Lean form is missing.')
UNDERSTANDING = ('The sum grows by one odd number at a time. What is not understood is why each step '
                 'completes a square. The elements `Small.oddSum` and `Small.root` carry the exact statements.\n')
UNDERSTOOD = ('The sum grows by one odd number at a time, and each odd number is the gnomon that turns '
              'one square into the next. The elements `Small.oddSum` and `Small.root` carry the exact statements.\n')
BIBLIOGRAPHY = '@book{gauss1801,\n  author = {Gauss, C. F.},\n  title = {Disquisitiones Arithmeticae},\n  year = {1801}\n}\n'
HOLD = {'Small.root': {'accepted': False, 'reason': 'Correct; the inductive step can be made shorter.'}}
WHOLE_ROOT = {'sections': [{'id': 'sauthor-1', 'element': 'Small.root', 'whole': True, 'statement': None,
                            'new': None, 'reasons': {}, 'at': 1}], 'at': 1}
# The statements of TransportCheckTests.settled_canon, in the order of their module: the Lean statement
# and the description of each.
SETTLED = {'low': (': oddSum 1 = 1', 'The first odd number is one.'),
           'open3': (': oddSum 3 = 9', 'The first three odd numbers sum to nine.'),
           'heldS': (': oddSum 5 = 25', 'The first five odd numbers sum to twenty-five.'),
           'pair': (': oddSum 2 = 4', 'The first two odd numbers sum to four.'),
           'base': (SUM_ZERO, 'The empty sum is zero.'),
           'twin': (': oddSum 4 = 16', 'The first four odd numbers sum to sixteen.')}
TWIN_ALT = 'The first four odd numbers sum to sixteen, by another argument.'
# A statement from which `oddSum 2 = 4` follows in one line, as the case n = 0.
SHARP = ('(n : Nat) : oddSum (n + 2) = (n + 2) * (n + 2)',
         'The sum of the first n + 2 odd numbers is the square of n + 2.')


def settled_text(name, uses=(), proof='rfl'):
    """The declaration of one of SETTLED with a proof: complete in Lean, unless the proof given is sorry."""
    statement, description = SETTLED[name]
    return theorem(name, statement, uses, proof, doc=description)


def sharp_module():
    return module_text(theorem('sharp', SHARP[0], doc=SHARP[1]))


def sharp_record():
    return record_text(SHARP[1], weight='unit', proof='By induction on $n$, adding $2n + 5$ to $(n + 2)^2$.')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def session_record(sid, role, job, **extra):
    return {'id': sid, 'role': role, 'job': job, 'status': 'running', 'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh',
            'provider': 'codex', 'started_at': 1, 'exit_code': 0, 'host': None, 'cli': None, 'record': None, **extra}


class PublicationCase(InstanceCase):
    def canon(self):
        return Canon(self.instance)

    def canon_bytes(self):
        root = self.instance / 'canon'
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def events(self):
        return sorted((read_json(p) for p in (self.instance / 'knowledge/events').glob('*.json')),
                      key=lambda event: event['sequence'])

    def leftovers(self):
        """Folders the runner uses while a publication is underway; none remains once it has ended."""
        return sorted(p.name for pattern in ('stage-*', 'event-*')
                      for p in (self.instance / 'runner').glob(pattern))

    def root_source(self):
        return (self.canon().lean / 'Small/Root.lean').read_text(encoding='utf-8')

    def root_declaration(self):
        return declaration_text(self.root_source(), self.canon().load_index()['entries']['Small.root']['span'])

    def induction(self, extras=False, records=None, **options):
        """The candidate most tests publish: a new module with the inductive step, an informal proof of the
        root that names it and so needs the module imported, the two records, and the approach taken."""
        folder = self.candidate(modules={'Small/Step.lean': STEP}, replace={'Small.root': INFORMAL},
                                imports={'Small.root': ['Small.Step']},
                                records=records or {'Small/root.md': ROOT_RECORD, 'Small/oddSum_succ.md': STEP_RECORD},
                                approaches={'Small/root/induction.md': APPROACH}, prepare=not extras, **options)
        if extras:
            write(folder / 'evidence/Small/root/squares.csv', 'n,sum\n1,1\n2,4\n3,9\n')
            write(folder / 'bibliography.bib', BIBLIOGRAPHY)
            self.prepare(folder)
        return folder

    def review_job(self, engine, folder):
        return next(job for job in engine.state['jobs'].values()
                    if job['role'] == 'review' and job['task'].get('candidate') == str(folder))

    def assert_sent_to_a_replacement_peer(self, engine, folder, reason, canon_before, events_before):
        """The candidate was not published: the canon is as it was, and a new peer receives the original
        work, the earlier peer's work and the reason (design record, section 10.4)."""
        job = self.review_job(engine, folder)
        pipeline = engine.state['pipelines'][job['pipeline']]
        self.assertEqual((job['status'], pipeline['stage'], pipeline['record']), ('cancelled', 'peer', None))
        review = engine.state['sessions'][pipeline['review']]
        self.assertEqual((review['status'], review['record']), ('failed', None))
        peers = [j for j in engine.state['jobs'].values()
                 if j['role'] == 'peer' and j['pipeline'] == pipeline['id'] and j['status'] == 'pending']
        self.assertEqual(len(peers), 1)
        task = peers[0]['task']
        self.assertIn('could not be published on the current canon', task['previous_error'])
        self.assertIn(reason, task['previous_error'])
        self.assertEqual(task['source'], job['task']['source'])
        self.assertEqual(task['previous_partial_sessions'], [job['task']['peer']])
        self.assertEqual(pipeline['previous_peers'], [Path(job['task']['peer']).name])
        self.assertIsNone(engine.state['publication'])
        self.assertEqual(engine.state['publish_queue'], [])
        self.assertEqual(self.canon_bytes(), canon_before)
        self.assertEqual([event['id'] for event in self.events()], events_before)
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'canon'), '')

    def session(self, engine, sid, role, job, task, pipeline, **extra):
        """A session folder as its CLI left it, and the session's entry in the runner's state."""
        folder = engine.session_dir(sid)
        for name in ('output', 'work', 'inbox'):
            (folder / name).mkdir(parents=True, exist_ok=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'pipeline': pipeline, 'task': task, 'user_inputs': []})
        (folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        engine.state['sessions'][sid] = session_record(sid, role, job, **extra)
        return folder

    def held_sketch(self):
        """The root with a first proof, correct and held back, in place of the test's instance: published
        through the real path once for the test process (InstanceCase.scenario). Returns the change."""
        def build():
            first = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
            self.publish(first, self.verdicts(first, **HOLD))

        self.scenario('held sketch', build)
        [event] = self.events()
        return event['id']


class PublicationTests(PublicationCase):
    def test_a_publication_adds_modules_replaces_a_proof_in_place_and_regenerates_what_is_derived(self):
        before = self.canon().load_index()['entries']['Small.root']
        old_record = (self.canon().records / 'Small/root.md').read_text(encoding='utf-8')
        folder = self.induction(extras=True)
        cid, engine = self.publish(folder, self.verdicts(folder, **HOLD))
        canon, index = self.canon(), self.canon().load_index()
        with self.subTest('the new module is added as the candidate wrote it'):
            self.assertEqual((canon.lean / 'Small/Step.lean').read_text(encoding='utf-8'), STEP)
            self.assertFalse((canon.lean / 'DoMathExtract.lean').exists())
        with self.subTest('the proof is replaced where it stood, with its imports, and nothing else changes'):
            self.assertEqual(self.root_source(),
                             ROOT.replace('public import Small.Defs\n', 'public import Small.Defs\npublic import Small.Step\n')
                             .replace(ORIGINAL, INFORMAL))
            self.assertEqual(self.root_declaration(), INFORMAL)
        with self.subTest('the structural index is extracted again from the compiled library'):
            self.assertEqual(index['revision'], 1)
            step, root = index['entries']['Small.oddSum_succ'], index['entries']['Small.root']
            self.assertEqual((step['kind'], step['module'], step['file'], step['lean_proof'], step['statement_uses'], step['uses']),
                             ('theorem', 'Small.Step', 'Small/Step.lean', 'complete', ['Small.oddSum'], []))
            self.assertEqual((root['uses'], root['statement_uses'], root['lean_proof']),
                             (['Small.oddSum_succ'], ['Small.oddSum'], 'sorry'))
            # Name and statement stay; only the source of the proof is another.
            self.assertEqual(root['statement_hash'], before['statement_hash'])
            self.assertNotEqual(root['source_sha'], before['source_sha'])
            for module in ('Small.Root', 'Small.Step'):
                source = canon.lean / index['modules'][module]['file']
                self.assertEqual(index['modules'][module]['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        with self.subTest('the summary of the records is regenerated'):
            summary = read_json(canon.root / 'records.json')
            self.assertEqual(set(summary), set(index['entries']))
            self.assertEqual((summary['Small.root']['weight'], summary['Small.root']['proof'],
                              summary['Small.root']['approaches'], summary['Small.root']['path']),
                             ('unit', True, ['induction'], 'records/Small/root.md'))
            self.assertEqual((summary['Small.oddSum_succ']['description'], summary['Small.oddSum_succ']['short']),
                             ('Passing from n to n + 1 adds the odd number 2n + 1 to the sum.', 'next odd number'))
        with self.subTest('records are written, and a replaced record leaves its difference in the history'):
            self.assertEqual((canon.records / 'Small/root.md').read_text(encoding='utf-8'), ROOT_RECORD)
            self.assertEqual((canon.records / 'Small/oddSum_succ.md').read_text(encoding='utf-8'), STEP_RECORD)
            left = (canon.history / 'Small/root/000001-record.md').read_text(encoding='utf-8')
            self.assertIn(cid, left)
            self.assertIn('`records/Small/root.md`', left)
            self.assertIn('-## Proof', left)  # the current text has a proof and the replaced one had none
            self.assertNotEqual(old_record, ROOT_RECORD)
            self.assertFalse((canon.history / 'Small/oddSum_succ').exists())
        with self.subTest('the replaced proof leaves its difference in the history'):
            left = (canon.history / 'Small/root/000001-proof.md').read_text(encoding='utf-8')
            self.assertIn(cid, left)
            self.assertIn('`lean/Small/Root.lean`', left)
            self.assertIn('-  have step := oddSum_succ', left)  # the line the current proof has and the old one had not
            self.assertEqual(sorted(p.name for p in (canon.history / 'Small/root').iterdir()),
                             ['000001-proof.md', '000001-record.md'])
        with self.subTest("the approach entry carries review's assessment of what the work contributed"):
            text = (canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith(APPROACH))
            entry = parse_approach(text)
            self.assertEqual(entry['meta']['sessions'], ['sauthor'])
            self.assertEqual(entry['sections']['Review'], f'Change {cid} (revision 1): Closed what it took on.')
        with self.subTest('evidence and sources are added'):
            self.assertEqual((canon.evidence / 'Small/root/squares.csv').read_text(encoding='utf-8'), 'n,sum\n1,1\n2,4\n3,9\n')
            self.assertEqual(canon.bibliography.read_text(encoding='utf-8'), BIBLIOGRAPHY)
        with self.subTest('the event and its folder'):
            [event] = self.events()
            job = self.review_job(engine, folder)
            pipeline = engine.state['pipelines'][job['pipeline']]
            self.assertEqual({key: event[key] for key in ('id', 'kind', 'sequence', 'folder', 'session', 'producer_role',
                                                         'pipeline', 'element', 'question')},
                             {'id': cid, 'kind': 'change', 'sequence': 1, 'folder': 'changes/' + cid,
                              'session': pipeline['review'], 'producer_role': 'attempt', 'pipeline': pipeline['id'],
                              'element': None, 'question': None})
            published = self.instance / 'knowledge/changes' / cid
            self.assertEqual(sorted(p.name for p in published.iterdir()),
                             ['applied.json', 'assessment.json', 'change.json', 'feedback.md', 'provenance.json'])
            self.assertEqual(read_json(published / 'applied.json'),
                             {'added': ['Small.oddSum_succ'], 'replaced': ['Small.root'],
                              'records': ['Small.oddSum_succ', 'Small.root'], 'retired': []})
            self.assertEqual(read_json(published / 'change.json'), read_json(folder / 'change.json'))
            self.assertEqual(read_json(published / 'assessment.json'), self.verdicts(folder, **HOLD))
            self.assertEqual(read_json(published / 'provenance.json'),
                             {'producer_session': pipeline['producer'], 'peer_session': pipeline['peer'],
                              'review_session': pipeline['review'], 'pipeline': pipeline['id']})
        with self.subTest('one Git commit holds the canon and the event'):
            self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines(),
                             ['Publish ' + cid, 'Initialize autonomous mathematical research'])
            self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
            committed = git(self.instance, 'show', '--name-only', '--format=', 'HEAD').splitlines()
            for name in ('canon/lean/Small/Step.lean', 'canon/lean/Small/Root.lean', 'canon/index.json',
                         'canon/records.json', 'canon/records/Small/oddSum_succ.md',
                         'canon/approaches/Small/root/induction.md', 'canon/history/Small/root/000001-record.md',
                         'canon/history/Small/root/000001-proof.md',
                         'knowledge/events/' + cid + '.json', 'knowledge/changes/' + cid + '/applied.json'):
                self.assertIn(name, committed)
        with self.subTest('the research state and the runner state'):
            model = replay(self.instance)
            root = model['elements']['Small.root']
            self.assertEqual((root['standing'], root['verdict']['reason'], root['verdict']['change']),
                             ('held', 'Correct; the inductive step can be made shorter.', cid))
            self.assertEqual(model['elements']['Small.oddSum_succ']['standing'], 'accepted')
            self.assertEqual((model['root_state'], model['remaining'], model['sequence']), ('unresolved', ['Small.root'], 1))
            change = model['changes'][cid]
            self.assertEqual((change['contribution'], change['added'], change['replaced'], change['role']),
                             ('Closed what it took on.', ['Small.oddSum_succ'], ['Small.root'], 'attempt'))
            self.assertIn('- `Small.root` — odd numbers sum to a square — correct, held back: '
                          'Correct; the inductive step can be made shorter. · 1 approach tried',
                          (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))
            self.assertEqual(engine.model, model)
            self.assertEqual((job['status'], job['record'], pipeline['stage'], pipeline['record']), ('done', cid, 'done', cid))
            self.assertEqual(engine.state['sessions'][pipeline['review']]['status'], 'integrated')
            self.assertIsNone(engine.state['publication'])
            self.assertFalse(engine.state['complete'])
            self.assertEqual(self.leftovers(), [])

    def test_an_accepted_proof_takes_the_place_of_the_old_one_whose_text_and_approaches_go_to_the_history(self):
        first = self.induction()
        _, engine = self.publish(first, self.verdicts(first, **HOLD))
        canon = self.canon()
        tried = (canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8')
        second = self.candidate(replace={'Small.root': FORMAL})
        cid, _ = self.publish(second, engine=engine)
        with self.subTest('the new proof stands under the same name and statement'):
            self.assertEqual(self.root_declaration(), FORMAL)
            self.assertEqual(self.root_source().count('public import Small.Step'), 1)
            self.assertNotIn('sorry', self.root_source())
            model = replay(self.instance)
            root = model['elements']['Small.root']
            self.assertEqual((root['standing'], root['settled'], root['formal'], root['lean_proof']),
                             ('accepted', True, True, 'complete'))
            self.assertEqual((model['root_state'], model['remaining']), ('formal_proved', []))
            self.assertTrue(engine.state['complete'])
            # The record was not part of this change, so it stands as the first change wrote it.
            self.assertEqual((canon.records / 'Small/root.md').read_text(encoding='utf-8'), ROOT_RECORD)
            self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'applied.json'),
                             {'added': [], 'replaced': ['Small.root'], 'records': [], 'retired': []})
        with self.subTest('the approaches tried on an element whose proof is accepted move to its history'):
            self.assertFalse((canon.approaches / 'Small/root').exists())
            self.assertEqual((canon.history / 'Small/root/000002-approaches/induction.md').read_text(encoding='utf-8'), tried)
            self.assertEqual(read_json(canon.root / 'records.json')['Small.root']['approaches'], [])
            self.assertEqual(replay(self.instance)['elements']['Small.root']['approaches'], [])
            self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        with self.subTest('the replaced proof is kept in the history only'):
            # Design record, sections 4.4 and 10.3 rule 4: what was replaced remains as the element's history,
            # apart from the files of the canon that a traversal reads.
            kept = [p for p in (canon.history / 'Small/root').rglob('*') if p.is_file()
                    and 'have step := oddSum_succ' in p.read_text(encoding='utf-8')]
            self.assertTrue(kept, 'the history of Small.root does not hold the proof that was replaced')
            self.assertFalse([p for p in canon.lean.rglob('*.lean') if 'have step' in p.read_text(encoding='utf-8')])

    def test_a_settled_statement_is_derived_from_a_statement_that_supersedes_it_once_that_one_is_settled(self):
        # The order the rule asks for (design record, sections 5 and 10.3): the settled statement S keeps its
        # proof while the better statement S' is published and settled, and only then does the one-line
        # derivation of S from S' take the place of the old proof.
        description = SETTLED['pair'][1]
        old = theorem('pair', SETTLED['pair'][0], doc=description)
        first = self.candidate(modules={'Small/Pair.lean': module_text(old)},
                               records={'Small/pair.md': record_text(description, weight='unit',
                                                                     proof='One plus three is four.')})
        _, engine = self.publish(first)
        second = self.candidate(modules={'Small/Sharp.lean': sharp_module()}, records={'Small/sharp.md': sharp_record()})
        self.publish(second, engine=engine)
        elements = replay(self.instance)['elements']
        self.assertEqual([(elements[n]['standing'], elements[n]['settled']) for n in ('Small.pair', 'Small.sharp')],
                         [('accepted', True), ('accepted', True)])
        derivation = theorem('pair', SETTLED['pair'][0], proof='simpa using sharp 0', doc=description)
        third = self.candidate(replace={'Small.pair': derivation}, imports={'Small.pair': ['Small.Sharp']},
                               records={'Small/pair.md': record_text(description, weight='unit',
                                                                     proof='The case $n = 0$ of `Small.sharp`.')})
        # The peer's check carries the derivation without a section, since the statement stays settled under it.
        change_check(third, replay(self.instance), 'speer', held=set())
        cid, _ = self.publish(third, engine=engine)
        canon, index = self.canon(), self.canon().load_index()
        with self.subTest('the statement stays settled, under a proof that names the statement superseding it'):
            pair = replay(self.instance)['elements']['Small.pair']
            self.assertEqual((pair['standing'], pair['settled'], pair['statement_settled'], pair['lean_proof'], pair['uses']),
                             ('accepted', True, True, 'complete', ['Small.sharp']))
            source = (canon.lean / 'Small/Pair.lean').read_text(encoding='utf-8')
            self.assertEqual(declaration_text(source, index['entries']['Small.pair']['span']), derivation)
            self.assertIn('public import Small.Sharp\n', source)
            self.assertNotIn('sorry', source)
            self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'applied.json'),
                             {'added': [], 'replaced': ['Small.pair'], 'records': ['Small.pair'], 'retired': []})
        with self.subTest('the old proof goes to the history'):
            path = canon.history / 'Small/pair' / f"{index['revision']:06d}-proof.md"
            self.assertTrue(path.is_file(), sorted(p.name for p in (canon.history / 'Small/pair').iterdir()))
            left = path.read_text(encoding='utf-8')
            self.assertIn(cid, left)
            self.assertIn('`lean/Small/Pair.lean`', left)
            # The difference turns the current text into the replaced one: every line of the old declaration
            # stands on the replaced side, and the derivation's line is the one the old proof had not.
            lines = left.splitlines()
            for line in old.splitlines():
                self.assertTrue(' ' + line in lines or '+' + line in lines, line)
            self.assertIn('+  sorry', lines)
            self.assertIn('-  simpa using sharp 0', lines)

    def test_a_replacement_that_changes_the_statement_is_refused_when_prepared_and_again_at_publication(self):
        changed = DOC + 'theorem root (n : Nat) : oddSum n = n * n + 0 := by\n  sorry'
        folder = self.candidate(replace={'Small.root': changed}, prepare=False)
        receipt = self.prepare(folder, expect_ok=False)
        self.assertFalse(receipt['ok'])
        self.assertEqual(receipt['errors'], ['the statement of Small.root changed in place; '
                                             'a different statement enters under a new name'])
        # The runner makes the same check itself and does not rely on the receipt a session left.
        write_json(folder / 'prepared.json', {**receipt, 'ok': True, 'errors': []})
        before = self.canon_bytes()
        record, engine = self.publish(folder, expect=False)
        self.assertIsNone(record)
        self.assert_sent_to_a_replacement_peer(engine, folder, 'the statement of Small.root changed in place', before, [])
        self.assertEqual(self.root_declaration(), ORIGINAL)

    def test_a_replacement_that_review_declined_leaves_declaration_and_record_while_the_rest_is_published(self):
        # The root has a proof already, correct and held back; review is asked whether a new one takes its place.
        held, engine = self.held_sketch(), runtime.Runner(self.instance, self.skill)
        before = self.canon_bytes()
        folder = self.induction(records={'Small/root.md': ROOT_RECORD.replace('By induction on $n$', 'By induction on $n$ again'),
                                         'Small/oddSum_succ.md': STEP_RECORD})
        declined = {'Small.root': {'correct': 'not_confirmed', 'accepted': False, 'replaces': False,
                                   'reason': 'The inductive step is asserted and not derived.'}}
        cid, _ = self.publish(folder, self.verdicts(folder, **declined), engine=engine)
        after, canon = self.canon_bytes(), self.canon()
        # The candidate carries its own approach entry for the statement, so no entry is made from the declined proof.
        self.assertEqual(sorted(p.name for p in (canon.approaches / 'Small/root').iterdir()), ['induction.md'])
        for name in sorted(name for name in before if name.startswith(('lean/', 'records/', 'history/'))):
            with self.subTest(unchanged=name):
                self.assertEqual(after[name], before[name])
        self.assertEqual(self.root_declaration(), SKETCH)
        self.assertEqual(sorted(name for name in after if name.startswith('history/')),
                         sorted(name for name in before if name.startswith('history/')))
        # The rest of the candidate is published: the new element with its record and verdict, and the
        # attempt stays recorded among the approaches tried, with review's assessment.
        self.assertEqual((canon.lean / 'Small/Step.lean').read_text(encoding='utf-8'), STEP)
        self.assertEqual((canon.records / 'Small/oddSum_succ.md').read_text(encoding='utf-8'), STEP_RECORD)
        entry = parse_approach((canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8'))
        self.assertIn(cid, entry['sections']['Review'])
        self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'applied.json'),
                         {'added': ['Small.oddSum_succ'], 'replaced': [], 'records': ['Small.oddSum_succ'], 'retired': []})
        # The proof the canon has keeps the verdict of the change that put it there.
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['standing'], root['verdict']['change'], root['verdict']['reason'], root['uses'], root['approaches']),
                         ('held', held, 'Correct; the inductive step can be made shorter.', [], ['induction']))
        self.assertEqual(model['elements']['Small.oddSum_succ']['standing'], 'accepted')
        self.assertEqual(model['changes'][cid]['replaced'], [])

    def test_a_declined_proof_without_an_approach_entry_is_kept_among_the_approaches_tried(self):
        held, engine = self.held_sketch(), runtime.Runner(self.instance, self.skill)
        before = self.canon_bytes()
        offered = 'Pair the k-th odd number with the gnomon of the k-th square, and add the gnomons.'
        folder = self.candidate(
            replace={'Small.root': PAIRING}, title='Pairing odd numbers with gnomons',
            records={'Small/root.md': ROOT_RECORD.replace(
                'By induction on $n$: adding the next odd number $2k + 1$ to $k^2$ gives $(k + 1)^2$.', offered)})
        reason = 'The pairing is described and not carried out.'
        declined = {'Small.root': {'correct': 'not_confirmed', 'accepted': False, 'replaces': False, 'reason': reason}}
        cid, _ = self.publish(folder, self.verdicts(folder, **declined), engine=engine)
        after, canon = self.canon_bytes(), self.canon()
        # The declaration and its record stay as the canon had them.
        kept = sorted(name for name in before if name.startswith(('lean/', 'records/', 'history/')))
        self.assertEqual(sorted(name for name in after if name.startswith(('lean/', 'records/', 'history/'))), kept)
        for name in kept:
            with self.subTest(unchanged=name):
                self.assertEqual(after[name], before[name])
        self.assertEqual(self.root_declaration(), SKETCH)
        # The declined proof stays among the approaches tried on the statement, made from what the candidate
        # said of itself, the proof it offered and review's reason, each as it stands.
        self.assertEqual(sorted(name for name in after if name.startswith('approaches/')),
                         [f'approaches/Small/root/declined-{cid}.md'])
        entry = parse_approach((canon.approaches / f'Small/root/declined-{cid}.md').read_text(encoding='utf-8'))
        pipeline = engine.state['pipelines'][self.review_job(engine, folder)['pipeline']]
        self.assertEqual((entry['meta']['title'], entry['meta']['sessions']),
                         (f'Proof offered by change {cid} and not put in place', [pipeline['producer'], pipeline['peer']]))
        self.assertEqual(entry['sections']['Idea'],
                         'Pairing odd numbers with gnomons. A precise contribution with its limitations.\n\n'
                         'The proof as it was offered:\n\n' + offered)
        self.assertEqual(entry['sections']['Established'], 'Nothing of it took the place of the proof the canon has.')
        self.assertEqual(entry['sections']['Where it stops'], reason)
        # Like every approach entry of a published change, it carries review's assessment of what the change contributed.
        self.assertTrue(entry['sections']['Review'].startswith(f'Change {cid} (revision '))
        self.assertTrue(entry['sections']['Review'].endswith('): Closed what it took on.'))
        self.assertIn(f'canon/approaches/Small/root/declined-{cid}.md',
                      git(self.instance, 'show', '--name-only', '--format=', 'HEAD').splitlines())
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        # The proof the canon has keeps the verdict of the change that put it there.
        model = replay(self.instance)
        root = model['elements']['Small.root']
        self.assertEqual((root['standing'], root['verdict']['change'], root['approaches']), ('held', held, [f'declined-{cid}']))
        self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'applied.json'),
                         {'added': [], 'replaced': [], 'records': [], 'retired': []})
        self.assertIn('· 1 approach tried', (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))

    def test_approaches_brought_to_a_statement_with_an_accepted_proof_go_to_its_history(self):
        # The canon keeps the approaches tried only on a statement whose proof is not accepted (design record,
        # section 7). A publication can bring one to a statement whose proof is already accepted without adding
        # or replacing that proof: an entry of its own, or the entry made for a replacement review declined.
        first = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
        _, engine = self.publish(first)
        self.assertEqual(replay(self.instance)['elements']['Small.root']['standing'], 'accepted')
        self.publish(self.candidate(approaches={'Small/root/induction.md': APPROACH}), engine=engine)
        folder = self.candidate(replace={'Small.root': PAIRING}, records={'Small/root.md': ROOT_RECORD})
        declined = {'Small.root': {'correct': 'not_confirmed', 'accepted': False, 'replaces': False,
                                   'reason': 'The pairing is described and not carried out.'}}
        cid, _ = self.publish(folder, self.verdicts(folder, **declined), engine=engine)
        canon = self.canon()
        self.assertFalse((canon.approaches / 'Small/root').exists())
        self.assertEqual(sorted(p.relative_to(canon.history).as_posix() for p in canon.history.rglob('*.md')
                                if p.parent.name.endswith('-approaches')),
                         ['Small/root/000002-approaches/induction.md', f'Small/root/000003-approaches/declined-{cid}.md'])
        self.assertEqual(replay(self.instance)['elements']['Small.root']['approaches'], [])
        self.assertEqual(read_json(canon.root / 'records.json')['Small.root']['approaches'], [])
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')

    def test_a_new_module_whose_path_now_exists_goes_to_a_replacement_peer(self):
        # Both candidates were written against the same canon and chose the same module path.
        first = self.candidate(modules={'Small/Step.lean': STEP}, records={'Small/oddSum_succ.md': STEP_RECORD})
        second = self.candidate(modules={'Small/Step.lean': ZERO}, records={'Small/oddSum_zero.md': ZERO_RECORD})
        cid, engine = self.publish(first)
        before = self.canon_bytes()
        record, _ = self.publish(second, engine=engine, expect=False)
        self.assertIsNone(record)
        self.assert_sent_to_a_replacement_peer(engine, second, 'module Small/Step.lean already exists in the canon',
                                               before, [cid])
        self.assertNotIn('Small.oddSum_zero', self.canon().load_index()['entries'])

    def test_a_replacement_of_a_proof_that_another_publication_replaced_goes_to_a_replacement_peer(self):
        # Two sessions hold parts of the root, and each replaces the proof it saw (design record, 10.3 rule 2).
        first = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
        second = self.candidate(replace={'Small.root': PAIRING}, records={'Small/root.md': ROOT_RECORD})
        self.assertEqual(read_json(first / 'prepared.json')['bases'], read_json(second / 'prepared.json')['bases'])
        cid, engine = self.publish(first)
        before = self.canon_bytes()
        with patch('runner.start_build', wraps=runtime.start_build) as started:
            record, _ = self.publish(second, engine=engine, expect=False)
        # The runner finds this as it applies the candidate, before any build.
        started.assert_not_called()
        self.assertIsNone(record)
        self.assert_sent_to_a_replacement_peer(engine, second, 'the proof of Small.root was replaced by another publication',
                                               before, [cid])
        self.assertEqual(self.root_declaration(), SKETCH)

    def test_a_candidate_that_does_not_build_on_the_current_canon_goes_to_a_replacement_peer(self):
        # The receipt says what was true when the peer prepared the candidate; the canon may have moved since,
        # so the runner builds the candidate itself before anything is put in place.
        broken = STEP.replace('/-- Adding', '-- fail: unknown constant Small.gone\n/-- Adding')
        folder = self.candidate(modules={'Small/Step.lean': broken}, records={'Small/oddSum_succ.md': STEP_RECORD},
                                prepare=False)
        receipt = self.prepare(folder, expect_ok=False)
        self.assertFalse(receipt['ok'])
        self.assertIn('unknown constant Small.gone', '\n'.join(receipt['errors']))
        write_json(folder / 'prepared.json', {**receipt, 'ok': True, 'errors': [], 'added': ['Small.oddSum_succ'],
                                              'entries': {'Small.oddSum_succ': {'kind': 'theorem', 'lean_proof': 'complete',
                                                                                'written_proof': False}}})
        before = self.canon_bytes()
        record, engine = self.publish(folder, expect=False)
        self.assertIsNone(record)
        self.assert_sent_to_a_replacement_peer(engine, folder, 'unknown constant Small.gone', before, [])
        self.assertFalse((self.canon().lean / 'Small/Step.lean').exists())

    def test_a_defect_of_the_runner_met_while_a_candidate_is_applied_is_not_charged_to_the_candidate(self):
        # A candidate fails to apply on its own account when its files conflict with the canon or cannot be read.
        # A KeyError there comes from the runner's own tables, such as an index entry without a field, and no
        # candidate causes it. It goes up to the runner's loop, which records it and ends (Runner.run), and the
        # publication waits where it stood: once the defect is repaired, the same candidate is published.
        folder = self.candidate(approaches={'Small/root/induction.md': APPROACH})
        engine = runtime.Runner(self.instance, self.skill)
        with patch('runner.apply_lean', side_effect=KeyError('span')), self.assertRaises(KeyError):
            self.publish(folder, engine=engine, expect=False)
        job = self.review_job(engine, folder)
        self.assertEqual((job['status'], engine.state['publication']['stage']), ('running', 'apply'))
        self.assertFalse([j for j in engine.state['jobs'].values() if j['role'] == 'peer'])
        self.assertEqual(self.events(), [])
        self.drain(engine)
        [event] = self.events()
        self.assertEqual((job['status'], job['record']), ('done', event['id']))
        self.assertEqual(self.leftovers(), [])

    def test_two_queued_publications_are_made_one_at_a_time_in_the_order_they_were_queued(self):
        first = self.candidate(modules={'Small/Step.lean': STEP}, records={'Small/oddSum_succ.md': STEP_RECORD})
        second = self.candidate(modules={'Small/Zero.lean': ZERO}, records={'Small/oddSum_zero.md': ZERO_RECORD})
        engine = runtime.Runner(self.instance, self.skill)
        with patch.object(self, 'drain'):
            self.publish(first, engine=engine, expect=False)
            self.publish(second, engine=engine, expect=False)
        self.assertEqual([item['job'] for item in engine.state['publish_queue']],
                         [self.review_job(engine, first)['id'], self.review_job(engine, second)['id']])
        engine.publish()
        # The first is underway and the second waits for it.
        self.assertEqual(engine.state['publication']['job'], self.review_job(engine, first)['id'])
        self.assertEqual([item['job'] for item in engine.state['publish_queue']], [self.review_job(engine, second)['id']])
        self.assertEqual(self.events(), [])
        # While the build runs, a pass of the runner looks only for the build's result file, which the broker
        # writes when the build ends. The broker's state and the canon's index, each read whole, stay unread.
        reread = AssertionError('read again while the build runs')
        with patch('lean_broker.result_file', return_value=self.root / 'no-result.json'), \
                patch('runner.build_outcome', side_effect=reread), \
                patch('runner.Canon.load_index', side_effect=reread):
            engine.publish()
        self.assertEqual(engine.state['publication']['job'], self.review_job(engine, first)['id'])
        self.drain(engine)
        events = self.events()
        self.assertEqual([event['sequence'] for event in events], [1, 2])
        added = [read_json(self.instance / 'knowledge' / event['folder'] / 'applied.json')['added'] for event in events]
        self.assertEqual(added, [['Small.oddSum_succ'], ['Small.oddSum_zero']])
        self.assertEqual([self.review_job(engine, folder)['record'] for folder in (first, second)],
                         [event['id'] for event in events])
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines()[:2],
                         ['Publish ' + events[1]['id'], 'Publish ' + events[0]['id']])
        # The second was applied to the canon that the first left: its commit holds its own module only.
        self.assertEqual([name for name in git(self.instance, 'show', '--name-only', '--format=', 'HEAD').splitlines()
                          if name.startswith('canon/lean/')], ['canon/lean/Small/Zero.lean'])
        index = self.canon().load_index()
        self.assertEqual(index['revision'], 2)
        self.assertLessEqual({'Small.oddSum_succ', 'Small.oddSum_zero'}, set(index['entries']))
        self.assertEqual(self.leftovers(), [])

    def test_review_s_contribution_is_written_into_approach_entries_and_understanding_texts(self):
        canon, library = self.canon(), self.canon().load_index()
        first = self.candidate(approaches={'Small/root/induction.md': APPROACH}, understanding={'q0.md': UNDERSTANDING})
        assessment = {**self.verdicts(first), 'contribution': 'Let the research see where the induction stops.'}
        one, engine = self.publish(first, assessment, role='explore', question='q0')
        stamp = f'\n## Review\n\nChange {one} (revision 1): Let the research see where the induction stops.\n'
        self.assertEqual((canon.questions / 'q0.md').read_text(encoding='utf-8'), UNDERSTANDING + stamp)
        self.assertEqual((canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8'), APPROACH + stamp)
        self.assertFalse(canon.history.exists())
        model = replay(self.instance)
        self.assertEqual((model['changes'][one]['question'], model['changes'][one]['contribution']),
                         ('q0', 'Let the research see where the induction stops.'))
        self.assertEqual(model['elements']['Small.root']['approaches'], ['induction'])
        # A later change carries the approach further and replaces the understanding. Each text holds the
        # assessment of the change that wrote it, and what the new text removed is in the history.
        second = self.candidate(approaches={'Small/root/induction.md': FURTHER}, understanding={'q0.md': UNDERSTOOD})
        assessment = {**self.verdicts(second), 'contribution': 'Closed the arithmetic of the inductive step.'}
        two, _ = self.publish(second, assessment, role='explore', question='q0', engine=engine)
        stamp = f'\n## Review\n\nChange {two} (revision 2): Closed the arithmetic of the inductive step.\n'
        self.assertEqual((canon.questions / 'q0.md').read_text(encoding='utf-8'), UNDERSTOOD + stamp)
        self.assertEqual((canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8'), FURTHER + stamp)
        left = (canon.history / 'questions/q0/000002.md').read_text(encoding='utf-8')
        self.assertIn(two, left)
        self.assertIn('+The sum grows by one odd number at a time. What is not understood is why each step', left)
        self.assertIn(one, left)  # the replaced text ended with the assessment of the change that wrote it
        left = (canon.history / 'Small/root/000002-approach-induction.md').read_text(encoding='utf-8')
        self.assertIn('`approaches/Small/root/induction.md`', left)
        self.assertIn('+The inductive step is stated; the arithmetic identity has not been checked in Lean.', left)
        self.assertEqual(sorted(p.name for p in (canon.history / 'Small/root').iterdir()), ['000002-approach-induction.md'])
        # Neither change touched Lean: the library stands as it was, and so does what the index says of it.
        self.assertEqual(self.root_source(), ROOT)
        index = canon.load_index()
        self.assertEqual((index['entries'], index['modules']), (library['entries'], library['modules']))
        self.assertEqual(replay(self.instance)['sequence'], 2)
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')


class InterruptedPublicationTests(PublicationCase):
    """A publication saves each stage it reaches. A runner that ended at any of them is followed by one
    that completes the same publication, and nothing of it is done twice."""

    def builds(self):
        return sorted(p.name for p in (self.instance / 'runner/lean/builds').iterdir())

    def interrupt(self, target, stage, installed=False, builds=0, event_written=False, side_effect=None):
        folder = self.induction(extras=True)
        engine = runtime.Runner(self.instance, self.skill)
        failure = side_effect or RuntimeError('simulated end of the runner')
        with patch(target, side_effect=failure), self.assertRaisesRegex(RuntimeError, 'simulated'):
            self.publish(folder, self.verdicts(folder, **HOLD), engine=engine, expect=False)
        saved = read_json(self.instance / 'runner/state.json')['publication']
        self.assertEqual((saved['stage'], bool(saved.get('installed'))), (stage, installed))
        self.assertEqual(self.events(), [saved['event']] if event_written else [])
        self.assertNotIn('Publish ' + saved['event']['id'], git(self.instance, 'log', '--format=%s'))
        # The broker makes the folder of a build when it takes the request up, which can be after this line.
        queued = sorted(set(self.builds()) | ({saved['build']} if saved.get('build') else set()))
        recovered = runtime.Runner(self.instance, self.skill)
        with patch('runner.start_build', wraps=runtime.start_build) as started:
            self.drain(recovered)
            recovered.publish()
        # A build that was started is continued, not started again.
        self.assertEqual(started.call_count, builds)
        self.assertEqual(len(self.builds()), len(queued) + builds)
        if saved.get('build'):
            self.assertIn(saved['build'], self.builds())
        self.assert_published_once(recovered, folder, saved['event'])
        # A third runner finds nothing left to do.
        again = runtime.Runner(self.instance, self.skill)
        again.publish()
        self.assert_published_once(again, folder, saved['event'])

    def assert_published_once(self, engine, folder, event):
        cid, canon = event['id'], self.canon()
        self.assertEqual(self.events(), [event])
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines(),
                         ['Publish ' + cid, 'Initialize autonomous mathematical research'])
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assertEqual(self.root_source(),
                         ROOT.replace('public import Small.Defs\n', 'public import Small.Defs\npublic import Small.Step\n')
                         .replace(ORIGINAL, INFORMAL))
        self.assertEqual((canon.lean / 'Small/Step.lean').read_text(encoding='utf-8'), STEP)
        self.assertFalse((canon.lean / 'DoMathExtract.lean').exists())
        self.assertEqual(canon.load_index()['revision'], 1)
        self.assertEqual(read_json(canon.root / 'records.json')['Small.root']['approaches'], ['induction'])
        self.assertEqual((canon.records / 'Small/root.md').read_text(encoding='utf-8'), ROOT_RECORD)
        # The record was replaced once: one entry, and it still shows what the first text lacked.
        self.assertEqual([p.name for p in (canon.history / 'Small/root').glob('*-record.md')], ['000001-record.md'])
        self.assertIn('-## Proof', (canon.history / 'Small/root/000001-record.md').read_text(encoding='utf-8'))
        # The proof was replaced once as well, and its entry still holds the difference to the old text.
        self.assertEqual([p.name for p in (canon.history / 'Small/root').glob('*-proof.md')], ['000001-proof.md'])
        self.assertIn('-  have step := oddSum_succ',
                      (canon.history / 'Small/root/000001-proof.md').read_text(encoding='utf-8'))
        self.assertEqual((canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8'),
                         APPROACH + f'\n## Review\n\nChange {cid} (revision 1): Closed what it took on.\n')
        self.assertEqual(canon.bibliography.read_text(encoding='utf-8'), BIBLIOGRAPHY)
        self.assertEqual(sorted(p.name for p in (self.instance / 'knowledge/changes').iterdir()), [cid])
        self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'applied.json'),
                         {'added': ['Small.oddSum_succ'], 'replaced': ['Small.root'],
                          'records': ['Small.oddSum_succ', 'Small.root'], 'retired': []})
        job = self.review_job(engine, folder)
        self.assertEqual((job['status'], job['record']), ('done', cid))
        self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'done')
        self.assertEqual(engine.state['sessions'][job['session']]['status'], 'integrated')
        self.assertIsNone(engine.state['publication'])
        self.assertEqual(engine.state['publish_queue'], [])
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(replay(self.instance)['elements']['Small.root']['standing'], 'held')

    def test_ended_while_applying_the_candidate(self):
        self.interrupt('runner.start_build', 'apply', builds=1)

    def test_ended_while_the_build_ran(self):
        self.interrupt('runner.build_outcome', 'build')

    def test_ended_while_checking_what_changed(self):
        self.interrupt('runner.check_applied', 'check')

    def test_ended_before_the_canon_was_put_in_place(self):
        self.interrupt('runner.Runner.install_canon', 'commit')

    def test_ended_after_the_library_was_put_in_place_and_before_the_written_part(self):
        self.interrupt('runner.apply_written', 'commit')

    def test_ended_after_the_written_part_and_before_that_was_saved(self):
        self.interrupt('runner.record_summary', 'commit')

    def test_ended_after_the_canon_was_installed_and_before_the_event_was_written(self):
        self.interrupt('runner.rename_directory', 'commit', installed=True)

    def test_ended_at_the_git_commit(self):
        def broken(instance, *args):
            if args[0] == 'commit':
                raise RuntimeError('simulated unavailable commit')
            return git(instance, *args)
        self.interrupt('runner.git', 'commit', installed=True, event_written=True, side_effect=broken)


class ReviewedCandidateTests(PublicationCase):
    """What the runner does with a candidate when its review ends: Runner.finish and the paths from it."""

    def candidate_pipeline(self):
        """A pipeline at review: the producer holds the whole root, the peer's candidate is frozen, and the
        review has written an assessment that confirms and accepts the informal proof."""
        engine = runtime.Runner(self.instance, self.skill)
        producer = engine.producer('attempt')
        pid = engine.state['jobs'][producer]['pipeline']
        engine.state['pipelines'][pid].update(producer='sauthor', peer='speer', review='sreview', stage='review')
        engine.state['jobs'][producer]['status'] = 'done'
        engine.session_dir('sauthor').mkdir(parents=True)
        write_json(engine.session_dir('sauthor') / 'declaration.json', WHOLE_ROOT)
        folder = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
        peer = engine.session_dir('speer')
        peer.mkdir(parents=True)
        candidate = peer / 'candidate'
        shutil.copytree(folder, candidate)
        shutil.copytree(folder, peer / 'output')
        task = {'kind': 'candidate', 'candidate': str(candidate), 'candidate_hashes': runtime.tree_hashes(candidate),
                'peer': str(peer), 'source': str(engine.session_dir('sauthor'))}
        jid = engine.enqueue('review', task, pid, pid + ':review')
        session = self.session(engine, 'sreview', 'review', jid, task, pid)
        write_json(session / 'output/assessment.json', self.verdicts(candidate))
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        engine.state['jobs'][jid].update(status='running', session='sreview')
        engine.save()
        return engine, engine.state['jobs'][jid]

    def finish_replacement_review(self, engine, job, sid='sreplacement'):
        folder = self.session(engine, sid, 'review', job['id'], job['task'], job['pipeline'], started_at=2)
        shutil.copytree(engine.session_dir('sreview') / 'output', folder / 'output', dirs_exist_ok=True)
        job.update(status='running', session=sid)
        engine.state['pipelines'][job['pipeline']]['review'] = sid
        engine.finish(sid, engine.state['sessions'][sid])
        self.drain(engine)

    def test_review_finish_publishes_the_unchanged_assigned_candidate(self):
        engine, job = self.candidate_pipeline()
        self.assertEqual(check_session(engine.session_dir('sreview')), [])
        # The review compiled the candidate itself; what that compile found is published with its assessment.
        with patch('builtins.print'):
            self.assertEqual(verify(engine.session_dir('sreview'), 64, 120), 0)
        compiled = read_json(engine.session_dir('sreview') / 'work/verify/outcome.json')
        engine.finish('sreview', engine.state['sessions']['sreview'])
        self.drain(engine)
        [event] = self.events()
        self.assertEqual((event['kind'], event['session'], event['producer_role']), ('change', 'sreview', 'attempt'))
        self.assertEqual((job['status'], job['record']), ('done', event['id']))
        self.assertEqual(engine.state['sessions']['sreview']['status'], 'integrated')
        self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'done')
        self.assertEqual(self.root_declaration(), SKETCH)
        self.assertEqual((self.canon().records / 'Small/root.md').read_text(encoding='utf-8'), ROOT_RECORD)
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual(read_json(published / 'provenance.json'),
                         {'producer_session': 'sauthor', 'peer_session': 'speer', 'review_session': 'sreview',
                          'pipeline': job['pipeline']})
        self.assertEqual((published / 'feedback.md').read_text(encoding='utf-8'), 'Independent assessment.')
        self.assertEqual(sorted(p.name for p in published.iterdir()),
                         ['applied.json', 'assessment.json', 'change.json', 'feedback.md', 'provenance.json', 'verify.json'])
        self.assertEqual(read_json(published / 'verify.json'), compiled)
        self.assertEqual((compiled['ok'], compiled['replaced']), (True, ['Small.root']))
        self.assertEqual(replay(self.instance)['root_state'], 'informal_proved')

    def test_review_finish_retries_instead_of_publishing_a_changed_candidate(self):
        engine, job = self.candidate_pipeline()
        before = self.canon_bytes()
        candidate = Path(job['task']['candidate'])
        (candidate / 'records/Small/root.md').write_text('A different argument after assignment.', encoding='utf-8')
        engine.finish('sreview', engine.state['sessions']['sreview'])
        self.assertEqual((job['status'], job['retries'], job['last_error']),
                         ('pending', 1, 'candidate changed after review assignment'))
        self.assertEqual(engine.state['sessions']['sreview']['status'], 'failed')
        self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'review')
        self.assertIsNone(engine.state['publication'])
        self.assertEqual(self.events(), [])
        self.assertEqual(self.canon_bytes(), before)
        # The peer's own output still has the assigned bytes, so the review is assigned a restored copy,
        # and the damaged folder is kept as it was found.
        restored = Path(job['task']['candidate'])
        self.assertNotEqual(restored, candidate)
        self.assertEqual(runtime.tree_hashes(restored), job['task']['candidate_hashes'])
        self.assertEqual((candidate / 'records/Small/root.md').read_text(encoding='utf-8'),
                         'A different argument after assignment.')
        self.finish_replacement_review(engine, job)
        self.assertEqual(job['status'], 'done')
        [event] = self.events()
        self.assertEqual((self.canon().records / 'Small/root.md').read_text(encoding='utf-8'), ROOT_RECORD)
        self.assertEqual(self.root_declaration(), SKETCH)

    def test_publication_restart_rechecks_the_copied_candidate(self):
        engine, job = self.candidate_pipeline()
        before = self.canon_bytes()
        self.assertEqual(check_session(engine.session_dir('sreview')), [])
        engine.prepare_publication('sreview', job, 'change')
        candidate = Path(job['task']['candidate'])
        (candidate / 'replace/0.lean').write_text(PAIRING, encoding='utf-8')
        recovered = runtime.Runner(self.instance, self.skill)
        recovered.publish()
        job = recovered.state['jobs'][job['id']]
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual((job['status'], job['last_error']), ('pending', 'candidate changed after review assignment'))
        self.assertEqual(recovered.state['sessions']['sreview']['status'], 'failed')
        self.assertIsNone(recovered.state['sessions']['sreview']['record'])
        self.assertEqual(self.events(), [])
        self.assertEqual(self.canon_bytes(), before)
        self.assertEqual(self.leftovers(), [])
        restored = Path(job['task']['candidate'])
        self.assertNotEqual(restored, candidate)
        self.assertEqual(runtime.tree_hashes(restored), job['task']['candidate_hashes'])
        self.assertEqual((candidate / 'replace/0.lean').read_text(encoding='utf-8'), PAIRING)
        self.finish_replacement_review(recovered, job)
        self.assertEqual(job['status'], 'done')
        self.assertEqual(len(self.events()), 1)
        self.assertEqual(self.root_declaration(), SKETCH)

    def test_a_failed_restoration_before_publication_leaves_the_review_to_be_collected_again(self):
        # The candidate changed after its review ended, and the copy that would restore it from the peer's
        # output fails. The runner ends on that failure and saves its state (Runner.run). In that state the
        # review no longer waits for a publication, so the next runner collects its session again, meets the
        # changed candidate in the transport check and restores it for a fresh review.
        engine, job = self.candidate_pipeline()
        engine.prepare_publication('sreview', job, 'change')
        candidate = Path(job['task']['candidate'])
        (candidate / 'replace/0.lean').write_text(PAIRING, encoding='utf-8')
        with patch('runner.rename_directory', side_effect=PermissionError('injected persistent failure')), \
                patch('runner.traceback.print_exc'), patch('builtins.print'), \
                self.assertRaisesRegex(PermissionError, 'injected persistent failure'):
            engine.run()
        saved = read_json(self.instance / 'runner/state.json')
        self.assertEqual(saved['last_error']['error'], 'injected persistent failure')
        self.assertIsNone(saved['publication'])
        self.assertEqual(saved['jobs'][job['id']]['status'], 'running')
        recovered = runtime.Runner(self.instance, self.skill)
        recovered.collect()
        self.assertEqual(recovered.state['sessions']['sreview']['status'], 'failed')
        job = recovered.state['jobs'][job['id']]
        self.assertEqual((job['status'], job['last_error']), ('pending', 'candidate changed after review assignment'))
        restored = Path(job['task']['candidate'])
        self.assertNotEqual(restored, candidate)
        self.assertEqual(runtime.tree_hashes(restored), job['task']['candidate_hashes'])
        self.assertEqual(self.events(), [])

    def test_restart_replaces_stale_stages_that_hold_a_read_only_file(self):
        # copytree keeps a read-only flag, which Git gives its object files, and Windows refuses to
        # delete a read-only file. The stages an interrupted publication left are still replaced, and
        # the restart completes the same publication from the frozen candidate.
        engine, job = self.candidate_pipeline()
        engine.prepare_publication('sreview', job, 'change')
        identity = engine.state['publication']['event']['id']
        for name in ('stage-', 'event-'):
            stored = self.instance / 'runner' / (name + identity) / 'evidence/repo/.git/objects/ab/cdef'
            stored.parent.mkdir(parents=True)
            stored.write_bytes(b'A Git object')
            os.chmod(stored, stat.S_IREAD)
        recovered = runtime.Runner(self.instance, self.skill)
        self.drain(recovered)
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(recovered.state['jobs'][job['id']]['status'], 'done')
        self.assertEqual(self.leftovers(), [])
        [event] = self.events()
        self.assertEqual(event['id'], identity)
        self.assertFalse((self.instance / 'knowledge' / event['folder'] / 'evidence').exists())
        self.assertFalse((self.canon().lean / 'evidence').exists())
        self.assertEqual(self.root_declaration(), SKETCH)

    def test_changed_candidate_and_changed_peer_output_return_to_peer_then_publish(self):
        engine, job = self.candidate_pipeline()
        candidate = Path(job['task']['candidate'])
        for folder in (candidate, candidate.parent / 'output'):
            (folder / 'records/Small/root.md').write_text('Changed retained bytes.', encoding='utf-8')
        engine.finish('sreview', engine.state['sessions']['sreview'])
        pipeline = engine.state['pipelines'][job['pipeline']]
        self.assertEqual((job['status'], pipeline['stage']), ('cancelled', 'peer'))
        peer_job = next(j for j in engine.state['jobs'].values() if j['role'] == 'peer')
        self.assertEqual(peer_job['status'], 'pending')
        self.assertEqual(peer_job['task']['previous_error'], 'candidate changed after review assignment')
        self.assertIn(str(candidate.parent), peer_job['task']['previous_partial_sessions'])
        self.assertEqual(peer_job['task']['sections'],
                         [{'id': 'sauthor-1', 'element': 'Small.root', 'whole': True, 'statement': None, 'new': None}])
        self.assertEqual((candidate / 'records/Small/root.md').read_text(encoding='utf-8'), 'Changed retained bytes.')
        self.assertEqual(self.events(), [])
        # The new peer develops a candidate of its own on the current canon.
        peer = self.session(engine, 'snewpeer', 'peer', peer_job['id'], peer_job['task'], pipeline['id'], started_at=2)
        (peer / 'output').rmdir()
        developed = self.candidate(replace={'Small.root': PAIRING}, records={'Small/root.md': ROOT_RECORD})
        developed.rename(peer / 'output')
        peer_job.update(status='running', session='snewpeer')
        pipeline['peer'] = 'snewpeer'
        engine.finish('snewpeer', engine.state['sessions']['snewpeer'])
        review_job = next(j for j in engine.state['jobs'].values()
                          if j['role'] == 'review' and j['status'] == 'pending')
        self.assertNotEqual(review_job['id'], job['id'])
        self.assertEqual(Path(review_job['task']['candidate']), peer / 'candidate')
        self.assertEqual(review_job['task']['candidate_hashes'], runtime.tree_hashes(peer / 'output'))
        # A replacement for an interrupted review of the new candidate receives that review's partial
        # work, not the assessment of the damaged candidate the new peer replaced.
        cut = self.session(engine, 'sinterrupted', 'review', review_job['id'], review_job['task'], pipeline['id'],
                           started_at=2, exit_code=1)
        review_job.update(status='running', session='sinterrupted')
        engine.finish('sinterrupted', engine.state['sessions']['sinterrupted'])
        self.assertEqual((review_job['status'], review_job['task']['previous_partial_sessions']),
                         ('pending', [str(cut)]))
        self.finish_replacement_review(engine, review_job)
        self.assertEqual(pipeline['stage'], 'done')
        [event] = self.events()
        self.assertEqual(self.root_declaration(), PAIRING)
        self.assertEqual(read_json(self.instance / 'knowledge' / event['folder'] / 'provenance.json')['peer_session'],
                         'snewpeer')

    def test_interrupted_review_does_not_apply_a_structurally_usable_assessment(self):
        engine, job = self.candidate_pipeline()
        before = self.canon_bytes()
        session = engine.state['sessions']['sreview']
        folder = engine.session_dir('sreview')
        verdict = read_json(folder / 'output/assessment.json')
        for publish in (True, False):
            verdict['publish'] = publish
            write_json(folder / 'output/assessment.json', verdict)
            for code, refusal in ((1, None), (None, None),
                                  (0, {'reason': 'usage_limit'})):
                with self.subTest(publish=publish, exit_code=code, refusal=refusal):
                    self.assertEqual(check_session(folder), [])
                    session.update(status='running', exit_code=code, refusal=refusal)
                    job.update(status='running', session='sreview')
                    engine.finish('sreview', session)
                    self.assertEqual((session['status'], job['status']), ('failed', 'pending'))
                    self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'review')
                    self.assertIn(str(folder), job['task']['previous_partial_sessions'])
                    self.assertIsNone(engine.state['publication'])
                    self.assertEqual(engine.state['publish_queue'], [])
                    self.assertEqual(self.events(), [])
                    self.assertEqual(self.canon_bytes(), before)
                    self.assertFalse(engine.archive_due)

    def test_an_excluded_candidate_changes_nothing_and_releases_its_occupancy(self):
        engine, job = self.candidate_pipeline()
        before = self.canon_bytes()
        pipeline = engine.state['pipelines'][job['pipeline']]
        self.assertEqual(engine.available_elements(), [])
        session = engine.session_dir('sreview')
        verdict = read_json(session / 'output/assessment.json')
        verdict.update(publish=False, reason='No useful material: the argument restates the statement.')
        verdict['elements'][0].update(correct='not_confirmed', accepted=False,
                                      reason='The argument does not establish the statement.')
        write_json(session / 'output/assessment.json', verdict)
        self.assertEqual(check_session(session), [])
        reviewer = engine.state['sessions']['sreview']
        engine.finish('sreview', reviewer)
        self.assertEqual((reviewer['status'], job['status'], pipeline['stage']),
                         ('integrated', 'done', 'done'))
        self.assertTrue(reviewer['rejected'])
        self.assertEqual(pipeline['rejection_session'], 'sreview')
        self.assertIsNone(pipeline['record'])
        self.assertIsNone(engine.state['publication'])
        self.assertEqual(engine.state['publish_queue'], [])
        self.assertEqual(self.events(), [])
        self.assertEqual(self.canon_bytes(), before)
        self.assertEqual(list((self.instance / 'knowledge/changes').iterdir()), [])
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines(), ['Initialize autonomous mathematical research'])
        self.assertEqual(replay(self.instance)['root_state'], 'unresolved')
        self.assertEqual(engine.available_elements(), ['Small.root'])
        recovered = runtime.Runner(self.instance, self.skill)
        self.assertEqual(recovered.available_elements(), ['Small.root'])
        self.assertEqual(recovered.state['jobs'][job['id']]['status'], 'done')

    def test_review_output_cannot_collide_with_the_files_publication_adds(self):
        # Publication copies the review's output into the change's folder and adds change.json, applied.json,
        # provenance.json and verify.json beside it; a review file of one of those names would be replaced.
        engine, _ = self.candidate_pipeline()
        output = engine.session_dir('sreview') / 'output'
        self.assertEqual(check_session(output.parent), [])
        for name, directory in (('change.json', False), ('Change.JSON', False), ('applied.json', False),
                                ('applied.json', True), ('provenance.json', False), ('PROVENANCE.JSON', False),
                                ('verify.json', False), ('verify.json', True)):
            with self.subTest(name=name, directory=directory):
                path = output / name
                if directory:
                    path.mkdir()
                else:
                    path.write_text('Notes of the review.', encoding='utf-8')
                try:
                    errors = check_session(output.parent)
                    self.assertTrue(errors, 'a review file named ' + name + ' was accepted')
                    self.assertIn('reserved', errors[0])
                finally:
                    path.rmdir() if directory else path.unlink()
        # The same names deeper in the output collide with nothing.
        (output / 'notes').mkdir()
        (output / 'notes/change.json').write_text('Notes of the review.', encoding='utf-8')
        self.assertEqual(check_session(output.parent), [])

    def test_a_comprehensive_review_is_published_as_it_was_written_and_changes_no_canon_file(self):
        engine = runtime.Runner(self.instance, self.skill)
        before = self.canon_bytes()
        task = {'kind': 'comprehensive', 'concerns': [], 'conflicts': [], 'requested_elements': ['Small.root'],
                'purpose': 'Operator requested renewed examination.'}
        jid = engine.enqueue('review', task, key='operator:request1')
        session = self.session(engine, 'sexamine', 'review', jid, task, None)
        assessment = {'feedback': 'feedback.md', 'concerns': [],
                      'findings': [{'concerns': [], 'status': 'undetermined', 'validates': [], 'invalidates': [],
                                    'reason': 'The statement of the root was read against its Lean form; nothing was found.'}]}
        write_json(session / 'output/assessment.json', assessment)
        (session / 'output/feedback.md').write_text('Traced the root to its definitions.', encoding='utf-8')
        engine.state['jobs'][jid].update(status='running', session='sexamine')
        engine.save()
        self.assertEqual(check_session(session), [])
        engine.finish('sexamine', engine.state['sessions']['sexamine'])
        self.drain(engine)
        [event] = self.events()
        self.assertEqual((event['kind'], event['sequence'], event['session']), ('review', 1, 'sexamine'))
        self.assertEqual(event['folder'], 'reviews/' + event['id'])
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual(sorted(p.name for p in published.iterdir()), ['assessment.json', 'feedback.md'])
        self.assertEqual(read_json(published / 'assessment.json'), assessment)
        self.assertEqual(self.canon_bytes(), before)
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines()[0], 'Publish ' + event['id'])
        self.assertEqual((engine.state['jobs'][jid]['status'], engine.state['jobs'][jid]['record']), ('done', event['id']))
        model = replay(self.instance)
        self.assertEqual(model['elements']['Small.root']['findings'], [])
        self.assertEqual([finding['source'] for finding in model['findings']], [event['id']])


class OrganizerTests(PublicationCase):
    def organizer(self, engine, batch=()):
        """An organizer session as the runner launched it, with its output folder still empty."""
        sid = runtime.uid('s')
        task = {'batch': list(batch), 'batch_frozen': True}
        key = engine.enqueue('organizer', task)
        folder = self.session(engine, sid, 'organizer', key, task, None)
        engine.state['jobs'][key].update(status='running', session=sid)
        engine.save()
        return sid, folder / 'output'

    def finish(self, engine, sid):
        """What the runner does when the organizer's session has ended."""
        engine.finish(sid, engine.state['sessions'][sid])
        self.drain(engine)
        return engine.state['jobs'][engine.state['sessions'][sid]['job']]

    def test_an_agreement_the_organizer_proves_in_lean_enters_as_accepted_without_review(self):
        engine = runtime.Runner(self.instance, self.skill)
        sid, output = self.organizer(engine)
        write_json(output / 'organization.json', {'batch': [], 'merge_questions': []})
        write_json(output / 'change.json', {'title': 'The square as a definition',
                                            'description': 'A definition of the square and its agreement with the sum at zero.'})
        write(output / 'lean/Small/Square.lean', module_text('''/-- The square of `n`. -/
def square (n : Nat) : Nat := n * n

/-- The sum of no odd numbers is the square of zero. -/
theorem oddSum_zero_square : oddSum 0 = square 0 := by
  rfl'''))
        write(output / 'records/Small/square.md', record_text('The square of a natural number.'))
        write(output / 'records/Small/oddSum_zero_square.md',
              record_text('At zero the sum of odd numbers and the square agree.', proof='Both sides are zero.'))
        receipt = self.prepare(output, role='organizer')
        self.assertEqual(receipt['added'], ['Small.oddSum_zero_square', 'Small.square'])
        self.assertEqual(check_session(output.parent), [])
        job = self.finish(engine, sid)
        self.assertEqual(job['status'], 'done', job.get('last_error'))
        [event] = self.events()
        oid = event['id']
        self.assertEqual((event['kind'], event['folder'], event['sequence'], job['record']),
                         ('organization', 'organizations/' + oid, 1, oid))
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual(sorted(p.name for p in published.iterdir()), ['applied.json', 'change.json', 'organization.json'])
        self.assertEqual(read_json(published / 'applied.json'),
                         {'added': ['Small.oddSum_zero_square', 'Small.square'], 'replaced': [],
                          'records': ['Small.oddSum_zero_square', 'Small.square'], 'retired': []})
        canon = self.canon()
        self.assertTrue((canon.lean / 'Small/Square.lean').is_file())
        self.assertTrue((canon.records / 'Small/square.md').is_file())
        self.assertEqual(canon.load_index()['revision'], 1)
        self.assertEqual(set(read_json(canon.root / 'records.json')), set(canon.load_index()['entries']))
        model = replay(self.instance)
        agreement = model['elements']['Small.oddSum_zero_square']
        # Lean's check stands for the judgment of correctness, and the two acceptance considerations are not asked.
        self.assertEqual((agreement['standing'], agreement['settled'], agreement['formal']), ('accepted', True, True))
        self.assertEqual((agreement['verdict']['correct'], agreement['verdict']['accepted'], agreement['verdict']['change']),
                         ('confirmed', True, oid))
        self.assertIsNone(model['elements']['Small.square']['standing'])
        self.assertEqual(git(self.instance, 'log', '--format=%s').splitlines()[0], 'Publish ' + oid)
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assertEqual(self.leftovers(), [])

    def test_an_addition_that_is_not_proved_in_lean_is_refused_when_prepared_and_again_at_publication(self):
        engine = runtime.Runner(self.instance, self.skill)
        before = self.canon_bytes()
        sid, output = self.organizer(engine)
        write_json(output / 'organization.json', {'batch': [], 'merge_questions': []})
        write_json(output / 'change.json', {'title': 'An identity', 'description': 'The sum at zero.'})
        write(output / 'lean/Small/Zero.lean', ZERO.replace('  rfl', '  sorry'))
        write(output / 'records/Small/oddSum_zero.md', record_text('The sum of no odd numbers is zero.',
                                                                  proof='The sum is empty.'))
        receipt = self.prepare(output, role='organizer', expect_ok=False)
        # An identity that the organizer cannot prove in Lean it does not establish; it belongs to an attempt.
        self.assertEqual(receipt['errors'], ['Small.oddSum_zero is not proved in Lean from the allowed axioms: sorryAx'])
        errors = check_session(output.parent)
        self.assertEqual(len(errors), 1)
        self.assertIn('prepare reported errors: Small.oddSum_zero is not proved in Lean', errors[0])
        # The runner makes the same check itself: with a receipt that claims success the change is still
        # refused, the canon stays as it was, and the work goes to a replacement organizer with the reason.
        write_json(output / 'prepared.json', {**receipt, 'ok': True, 'errors': []})
        self.assertEqual(check_session(output.parent), [])
        job = self.finish(engine, sid)
        self.assertEqual((job['status'], engine.state['sessions'][sid]['status']), ('pending', 'failed'))
        self.assertIn('could not be published on the current canon', job['last_error'])
        self.assertIn('Small.oddSum_zero is not proved in Lean from the allowed axioms: sorryAx', job['last_error'])
        self.assertEqual(job['task']['previous_partial_sessions'], [str(output.parent)])
        self.assertIsNone(engine.state['publication'])
        self.assertEqual(self.events(), [])
        self.assertEqual(self.canon_bytes(), before)
        self.assertEqual(self.leftovers(), [])

    def test_a_rearrangement_that_changes_a_statement_or_drops_an_element_is_refused(self):
        engine = runtime.Runner(self.instance, self.skill)
        sid, output = self.organizer(engine)
        write_json(output / 'change.json', {'title': 'Rearranged modules', 'description': 'The root in another form.'})
        cases = (
            ({'batch': [], 'merge_questions': []},
             {'rewrite/lean/Small/Root.lean': ROOT.replace('oddSum n = n * n', 'n * n = oddSum n')},
             'the statement of Small.root changed in place'),
            ({'batch': [], 'merge_questions': [], 'delete': ['Small.Root']}, {},
             'declarations disappeared from the canon: Small.root'),
        )
        for organization, files, message in cases:
            with self.subTest(message=message):
                shutil.rmtree(output / 'rewrite', ignore_errors=True)
                write_json(output / 'organization.json', organization)
                for name, text in files.items():
                    write(output / name, text)
                receipt = self.prepare(output, role='organizer', expect_ok=False)
                self.assertFalse(receipt['ok'])
                self.assertIn(message, '\n'.join(receipt['errors']))
                self.assertIn('prepare reported errors', check_session(output.parent)[0])

    def test_a_rearrangement_puts_an_alternative_proof_under_the_statement_s_own_name(self):
        # A second proof of the root entered as a declaration of its own (design record, section 10.3).
        alternative = module_text('''/-- Another proof of the root, by pairing terms. -/
theorem root_alt (n : Nat) : oddSum n = n * n := by
  -- pair the k-th odd number with the gnomon of the k-th square
  sorry''')
        pairing = 'Each odd number $2k + 1$ is the gnomon that turns $k^2$ into $(k + 1)^2$.'
        first = self.candidate(modules={'Small/Alt.lean': alternative},
                               records={'Small/root_alt.md': record_text('The root, proved by pairing terms.',
                                                                         proves='Small.root', proof=pairing)})
        cid, engine = self.publish(first)
        model = replay(self.instance)
        self.assertEqual(model['elements']['Small.root']['proofs'], ['Small.root', 'Small.root_alt'])
        self.assertEqual((model['elements']['Small.root']['standing'], model['root_state']), ('no_proof', 'informal_proved'))
        statement = self.canon().load_index()['entries']['Small.root']['statement_hash']
        alt_record = (self.canon().records / 'Small/root_alt.md').read_text(encoding='utf-8')
        # A candidate under review names the alternative declaration.
        waiting = self.candidate(
            modules={'Small/Twice.lean': module_text('''/-- Twice the sum. -/
theorem twice (n : Nat) : oddSum n + oddSum n = 2 * (n * n) := by
  have h := root_alt
  sorry''', imports=('Small.Defs', 'Small.Alt'))},
            records={'Small/twice.md': record_text('Twice the sum of odd numbers is twice the square.',
                                                   proof='Add the root to itself.')})
        # The organizer moves the proof under the statement's own name and removes the separate declaration.
        sid, output = self.organizer(engine, [cid])
        write_json(output / 'organization.json', {'batch': [cid], 'merge_questions': [], 'delete': ['Small.Alt']})
        write_json(output / 'change.json', {
            'title': 'The pairing proof under the root', 'description': 'The alternative proof stands under Small.root.',
            'retire': [{'alternative': 'Small.root_alt', 'into': 'Small.root',
                        'reason': 'The module of the root can hold the proof now.'}]})
        write(output / 'rewrite/lean/Small/Root.lean', ROOT.replace(ORIGINAL, PAIRING))
        write(output / 'records/Small/root.md', ROOT_RECORD.replace(
            'By induction on $n$: adding the next odd number $2k + 1$ to $k^2$ gives $(k + 1)^2$.', pairing))
        receipt = self.prepare(output, role='organizer')
        self.assertEqual(receipt['retired'], [{'alternative': 'Small.root_alt', 'into': 'Small.root'}])
        self.assertEqual(check_session(output.parent), [])
        job = self.finish(engine, sid)
        self.assertEqual(job['status'], 'done', job.get('last_error'))
        canon, index = self.canon(), self.canon().load_index()
        with self.subTest('every other element keeps its name and statement, and the separate declaration is gone'):
            self.assertEqual(sorted(index['entries']), ['Small.oddSum', 'Small.root'])
            self.assertEqual(index['entries']['Small.root']['statement_hash'], statement)
            self.assertEqual(self.root_declaration(), PAIRING)
            self.assertFalse((canon.lean / 'Small/Alt.lean').exists())
            self.assertNotIn('Small.Alt', index['modules'])
        with self.subTest("the alternative's record goes to the history and the statement's own record stays"):
            self.assertFalse((canon.records / 'Small/root_alt.md').exists())
            self.assertEqual((canon.history / 'Small/root_alt/000002-retired.md').read_text(encoding='utf-8'), alt_record)
            self.assertIn(pairing, (canon.records / 'Small/root.md').read_text(encoding='utf-8'))
            self.assertEqual(sorted(read_json(canon.root / 'records.json')), ['Small.oddSum', 'Small.root'])
        with self.subTest('the verdict of the proof moves with it'):
            model = replay(self.instance)
            root = model['elements']['Small.root']
            self.assertEqual((root['standing'], root['settled'], root['proofs']), ('accepted', True, ['Small.root']))
            self.assertEqual((root['verdict']['element'], root['verdict']['change'], root['verdict']['correct']),
                             ('Small.root', cid, 'confirmed'))
            self.assertNotIn('Small.root_alt', model['elements'])
            self.assertNotIn('Small.root_alt', model['verdicts'])
            self.assertEqual((model['root_state'], model['organized']), ('informal_proved', [cid]))
        with self.subTest('the event'):
            event = self.events()[-1]
            published = self.instance / 'knowledge' / event['folder']
            self.assertEqual((event['kind'], event['sequence']), ('organization', 2))
            self.assertEqual(read_json(published / 'applied.json')['retired'],
                             [{'alternative': 'Small.root_alt', 'into': 'Small.root'}])
            self.assertEqual(read_json(published / 'change.json'), read_json(output / 'change.json'))
            self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        with self.subTest('a candidate that names the removed declaration no longer builds when its turn comes'):
            # Design record, section 11: it takes the path of a candidate that does not build.
            before, events = self.canon_bytes(), [event['id'] for event in self.events()]
            record, _ = self.publish(waiting, engine=engine, expect=False)
            self.assertIsNone(record)
            self.assert_sent_to_a_replacement_peer(engine, waiting, 'Small.Alt', before, events)

    def test_question_merges_are_published_without_a_build_and_without_a_change(self):
        self.questions('qops', [{'id': 'op-a', 'statement': 'Why do the sums complete squares?', 'grounds': 'Unexplained.'},
                                {'id': 'op-b', 'statement': 'What makes each step a square?', 'grounds': 'Unexplained.'}])
        engine = runtime.Runner(self.instance, self.skill)
        before = self.canon_bytes()
        sid, output = self.organizer(engine)
        organization = {'batch': [], 'merge_questions': [{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask the same thing.'}]}
        write_json(output / 'organization.json', organization)
        self.assertEqual(check_session(output.parent), [])
        with patch('runner.start_build', wraps=runtime.start_build) as started:
            job = self.finish(engine, sid)
        started.assert_not_called()
        self.assertEqual(job['status'], 'done', job.get('last_error'))
        event = self.events()[-1]
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual((event['kind'], event['sequence']), ('organization', 2))
        self.assertEqual(sorted(p.name for p in published.iterdir()), ['applied.json', 'organization.json'])
        self.assertEqual(read_json(published / 'organization.json'), organization)
        self.assertEqual(read_json(published / 'applied.json'), {'added': [], 'replaced': [], 'records': [], 'retired': []})
        self.assertEqual(self.canon_bytes(), before)
        model = replay(self.instance)
        self.assertEqual(model['question_aliases'], {'op-a': 'op-b'})
        self.assertEqual(model['questions']['op-a']['canonical'], 'op-b')
        self.assertIn('Aliases: op-a', (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))


class TransportCheckTests(PublicationCase):
    """check.py judges no mathematics: it decides whether a session's output can be carried further."""

    def setUp(self):
        super().setUp()
        self.start_pipeline()

    def start_pipeline(self):
        """A runner on the instance as it stands, and a pipeline whose producer and peer the tests install."""
        self.engine = runtime.Runner(self.instance, self.skill)
        producer = self.engine.producer('attempt')
        self.pipeline = self.engine.state['jobs'][producer]['pipeline']
        self.engine.state['pipelines'][self.pipeline].update(producer='sauthor', peer='speer', stage='peer')
        self.engine.session_dir('sauthor').mkdir(parents=True)
        self.engine.save()

    def operator_questions(self):
        """The two questions the operator placed on the frontier, for a test whose output names a question."""
        self.questions('qops', [
            {'id': 'op-scale', 'statement': 'Why do the sums complete squares?', 'grounds': 'Unexplained so far.'},
            {'id': 'speer-taken', 'statement': 'What makes each step a square?', 'grounds': 'Unexplained so far.'}])
        self.engine = runtime.Runner(self.instance, self.skill)  # the runner as it stands after their publication

    def install(self, sid, role, task, folder=None):
        """A session of the pipeline whose output is the given folder."""
        session = self.engine.session_dir(sid)
        if session.exists():
            shutil.rmtree(session)
        session.mkdir(parents=True)
        (session / 'work').mkdir()
        if folder is None:
            (session / 'output').mkdir()
        else:
            shutil.copytree(folder, session / 'output')
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'pipeline': self.pipeline, 'task': task, 'user_inputs': []})
        return session

    # -- the peer's candidate ---------------------------------------------------------------------------

    def peer_errors(self, change=None, files=None, prepare=True, **options):
        """What the check answers for a peer whose output is this candidate; change adds keys to change.json
        and files adds files, both before the candidate is prepared."""
        folder = self.candidate(prepare=False, **options)
        for name, text in (files or {}).items():
            write(folder / name, text)
        if change:
            write_json(folder / 'change.json', {**read_json(folder / 'change.json'), **change})
        if prepare:
            self.prepare(folder, expect_ok=False)
        return check_session(self.install('speer', 'peer', {'source_role': 'attempt'}, folder))

    def assert_refused(self, errors, message):
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(message, errors[0])

    def test_a_peer_candidate_is_carried_when_it_is_prepared_and_well_formed(self):
        self.operator_questions()
        proposal = {'id': 'speer-why', 'statement': 'Why is each step a square?', 'grounds': 'The proof does not say.'}
        self.assertEqual(self.peer_errors(
            approaches={'Small/root/induction.md': APPROACH},
            understanding={'q0.md': UNDERSTANDING, 'op-scale.md': UNDERSTOOD},
            questions=[proposal], resolutions=[{'id': 'settles', 'question': 'op-scale'}]), [])

    def test_a_peer_candidate_needs_the_receipt_of_prepare_for_exactly_its_files(self):
        self.assert_refused(self.peer_errors(approaches={'Small/root/induction.md': APPROACH}, prepare=False),
                            'the candidate has not been prepared; run commands.prepare')
        session = self.engine.session_dir('speer')
        self.prepare(session / 'output')
        self.assertEqual(check_session(session), [])
        # Any edit after the receipt was written, a new file included, asks for prepare again.
        write(session / 'output/approaches/Small/root/induction.md', FURTHER)
        self.assert_refused(check_session(session), 'the candidate changed after it was prepared; run commands.prepare again')
        self.prepare(session / 'output')
        write(session / 'output/evidence/Small/root/squares.csv', 'n,sum\n1,1\n')
        self.assert_refused(check_session(session), 'the candidate changed after it was prepared')
        self.prepare(session / 'output')
        self.assertEqual(check_session(session), [])
        # The end decision a peer writes beside its candidate is no part of it. Writing it after the preparation
        # asks for no new one, and its removal by the session's host leaves a later receipt valid.
        decision = session / 'output/end-decision.json'
        write_json(decision, {'request_id': 'r1', 'decision': 'end', 'basis': 'task_completed', 'explanation': 'Done.'})
        self.assertEqual(check_session(session), [])
        self.prepare(session / 'output')
        decision.unlink()
        self.assertEqual(check_session(session), [])
        # A receipt that reports errors does not carry the candidate, and says what prepare said.
        self.assert_refused(self.peer_errors(records={'Small/ghost.md': record_text('A record of nothing.')}),
                            'prepare reported errors: records/Small/ghost.md belongs to no declaration of the canon')

    def test_replacing_a_proof_requires_that_the_pipeline_holds_a_section_on_the_statement(self):
        options = {'replace': {'Small.root': SKETCH}, 'records': {'Small/root.md': ROOT_RECORD}}
        self.assert_refused(self.peer_errors(**options),
                            'replacing the proof of Small.root requires holding a section on Small.root')
        # The producer of the pipeline registered the whole root, which its peer inherits.
        write_json(self.engine.session_dir('sauthor') / 'declaration.json', WHOLE_ROOT)
        self.assertEqual(check_session(self.engine.session_dir('speer')), [])
        # A section the peer registered itself counts in the same way.
        (self.engine.session_dir('sauthor') / 'declaration.json').unlink()
        self.assert_refused(check_session(self.engine.session_dir('speer')), 'requires holding a section')
        write_json(self.engine.session_dir('speer') / 'declaration.json',
                   {'sections': [{**WHOLE_ROOT['sections'][0], 'id': 'speer-1', 'whole': False,
                                  'statement': 'the case of even n'}], 'at': 1})
        self.assertEqual(check_session(self.engine.session_dir('speer')), [])

    # -- the proof of a settled statement -----------------------------------------------------------------

    def settled_canon(self):
        """Statements in each relation to settlement that the replacement of a settled statement's proof
        turns on, published through the real path once for the test process (InstanceCase.scenario):

        low, pair  settled, each through its accepted written proof alone, which names nothing
        base       settled through its accepted proof that is complete in Lean alone, so formal as well
        twin       settled through its own accepted written proof and through that of Small.twinAlt,
                   another proof of the same statement
        heldS      not settled: its written proof is correct and held back
        open3      not settled: it has no proof"""
        def build():
            written = {'low': 'One is the first odd number.', 'pair': 'One plus three is four.',
                       'heldS': 'Add the five terms one at a time.', 'twin': 'Add seven to nine.'}
            body = '\n\n'.join(settled_text(name, proof='rfl' if name == 'base' else 'sorry') for name in SETTLED)
            folder = self.candidate(
                modules={'Small/Settled.lean': module_text(body),
                         'Small/Twin.lean': module_text(theorem('twinAlt', SETTLED['twin'][0], doc=TWIN_ALT),
                                                        imports=('Small.Settled',))},
                records={**{f'Small/{name}.md': record_text(description, weight='unit', proof=written.get(name))
                            for name, (_, description) in SETTLED.items()},
                         'Small/twinAlt.md': record_text(TWIN_ALT, weight='unit', proof='Add the four terms in pairs.',
                                                         proves='Small.twin')})
            self.publish(folder, self.verdicts(folder, **{
                'Small.heldS': {'accepted': False, 'reason': 'Correct; the five terms can be added at once.'}}))

        self.scenario('settled statements', build)
        # The scenario stands in place of the instance that setUp prepared, so the pipeline starts again on it.
        self.start_pipeline()
        elements = replay(self.instance)['elements']
        self.assertEqual({name: (elements['Small.' + name]['standing'], elements['Small.' + name]['statement_settled'],
                                 elements['Small.' + name]['statement_formal']) for name in SETTLED},
                         {'low': ('accepted', True, False), 'pair': ('accepted', True, False),
                          'base': ('accepted', True, True), 'twin': ('accepted', True, False),
                          'heldS': ('held', False, False), 'open3': ('no_proof', False, False)})
        self.assertEqual([(elements[n]['standing'], elements[n]['settled']) for n in elements['Small.twin']['proofs']],
                         [('accepted', True), ('accepted', True)])
        self.assertEqual(elements['Small.twin']['proofs'], ['Small.twin', 'Small.twinAlt'])

    def section_on(self, element):
        """The producer of the pipeline registered the whole of the element, which its peer inherits."""
        write_json(self.engine.session_dir('sauthor') / 'declaration.json',
                   {'sections': [{**WHOLE_ROOT['sections'][0], 'element': element}], 'at': 1})

    def test_the_proof_that_alone_settles_a_statement_is_replaced_only_by_one_under_which_it_stays_settled(self):
        self.settled_canon()
        with self.subTest('what a settled statement has through the proof of one declaration alone'):
            model = replay(self.instance)
            self.assertEqual({name: carried_by(model, 'Small.' + name) for name in (*SETTLED, 'twinAlt', 'root', 'oddSum')},
                             {'low': {'settled'}, 'pair': {'settled'}, 'base': {'settled', 'formal'}, 'twin': set(),
                              'twinAlt': set(), 'heldS': set(), 'open3': set(), 'root': set(), 'oddSum': set()})
        # The pipeline holds no section: a settled statement can no longer be taken, so none is asked for.
        with self.subTest('a proof complete in Lean that names settled statements is carried'):
            self.assertEqual(self.peer_errors(replace={'Small.pair': settled_text('pair', ['low'])}), [])
            # The new proof of a formal statement names only a definition and so stays formal.
            self.assertEqual(self.peer_errors(replace={'Small.base': settled_text('base', proof='simp [oddSum]')}), [])
        incomplete = {'replace': {'Small.pair': settled_text('pair', ['low'], 'sorry')}}
        cases = (
            ('Small.pair is settled through the proof of Small.pair; that proof is replaced only by a proof that is '
             'complete in Lean and names settled statements', incomplete),
            ('Small.pair is settled, and the new proof of Small.pair names Small.open3, which is not settled',
             {'replace': {'Small.pair': settled_text('pair', ['open3'])}}),
            ('Small.pair is settled, and the new proof of Small.pair names Small.heldS, which is not settled',
             {'replace': {'Small.pair': settled_text('pair', ['heldS'])}}),
            ('Small.pair is settled, and the new proof of Small.pair names Small.sharp, which this candidate adds and '
             'which is not settled yet. Publish the new statement first',
             {'modules': {'Small/Sharp.lean': sharp_module()}, 'records': {'Small/sharp.md': sharp_record()},
              'replace': {'Small.pair': settled_text('pair', proof='simpa using sharp 0')},
              'imports': {'Small.pair': ['Small.Sharp']}}),
            ('Small.base has a formal proof, and the new proof of Small.base names Small.low, which has none',
             {'replace': {'Small.base': settled_text('base', ['low'])}}),
        )
        for message, options in cases:
            with self.subTest(message=message):
                self.assert_refused(self.peer_errors(**options), message)
        with self.subTest('a statement that is formal through another declaration while its own Lean proof is open'):
            # `low` gains a second proof that is complete in Lean: the statement is formal, and the proof under its
            # own name still ends in sorry. A proof of `base` that names `low` then names a formal statement, and
            # Lean reports the open proof beneath it for the new proof all the same, so that proof is not formal.
            again = self.candidate(
                modules={'Small/LowAgain.lean': module_text(theorem('lowAgain', SETTLED['low'][0], proof='rfl',
                                                                    doc='The first odd number is one, by computation.'))},
                records={'Small/lowAgain.md': record_text('The first odd number is one, by computation.', weight='unit',
                                                          proves='Small.low')})
            self.publish(again, engine=self.engine)
            self.assertTrue(replay(self.instance)['elements']['Small.low']['statement_formal'])
            self.assert_refused(self.peer_errors(replace={'Small.base': settled_text('base', ['low'])}),
                                'Small.base has a formal proof, and the new proof of Small.base is not formal; '
                                'the statement would no longer be formal')
        with self.subTest('a named statement that is settled only through the proof being replaced'):
            # `open3` has no proof under its own name and becomes settled through `open3Alt` alone, another proof
            # of the same statement. A proof of `open3Alt` that names `open3` then names a settled statement, and
            # under it the statement would rest on itself: neither proof would settle it.
            another = 'The first three odd numbers sum to nine, by another argument.'
            self.publish(self.candidate(
                modules={'Small/OpenAlt.lean': module_text(theorem('open3Alt', SETTLED['open3'][0], doc=another),
                                                           imports=('Small.Settled',))},
                records={'Small/open3Alt.md': record_text(another, weight='unit', proof='Add one, three and five.',
                                                          proves='Small.open3')}), engine=self.engine)
            self.assertEqual(carried_by(replay(self.instance), 'Small.open3Alt'), {'settled'})
            circular = theorem('open3Alt', SETTLED['open3'][0], ['open3'], 'exact h1', doc=another)
            self.assert_refused(self.peer_errors(replace={'Small.open3Alt': circular}),
                                'Small.open3 is settled, and the new proof of Small.open3Alt names Small.open3, which is '
                                'settled only through the proof of Small.open3Alt that this candidate replaces')
        with self.subTest('a section held on the statement does not lift the condition'):
            self.section_on('Small.pair')
            self.assert_refused(self.peer_errors(**incomplete), 'that proof is replaced only by a proof that is complete')

    def test_a_statement_settled_through_another_proof_as_well_leaves_the_replacement_of_either_unconditioned(self):
        self.settled_canon()
        # Each of the two proofs can give way to one that ends in sorry and names a statement without a proof,
        # because the other keeps the statement settled; and, the statement being settled, no section is asked.
        self.assertEqual(self.peer_errors(replace={'Small.twin': settled_text('twin', ['open3'], 'sorry')}), [])
        self.assertEqual(self.peer_errors(replace={
            'Small.twinAlt': theorem('twinAlt', SETTLED['twin'][0], ['open3'], doc=TWIN_ALT)}), [])

    def test_the_proof_of_a_statement_that_is_not_settled_is_replaced_under_a_section_as_before(self):
        self.settled_canon()
        # A held proof settles nothing, so the statement can still be taken and its replacement needs a section;
        # under one, a proof that ends in sorry and names a statement without a proof is carried.
        self.assert_refused(self.peer_errors(replace={'Small.heldS': settled_text('heldS', ['open3'], 'sorry')}),
                            'replacing the proof of Small.heldS requires holding a section on Small.heldS')
        self.section_on('Small.heldS')
        self.assertEqual(check_session(self.engine.session_dir('speer')), [])

    def test_a_peer_candidate_is_refused_for_what_a_machine_can_decide_about_its_written_part(self):
        # The rules for question proposals, resolutions and understanding texts are checked with the questions
        # (test_questions.QuestionCheckTests); the other machine-decidable rules of the written part are here.
        cases = (
            ('its folder follows the name of no element', {'approaches': {'Small/ghost/induction.md': APPROACH}}),
            ("invalid identifier: 'two words'", {'approaches': {'Small/root/two words.md': APPROACH}}),
            ('only the organizer retires an alternative proof',
             {'change': {'retire': [{'alternative': 'Small.root', 'into': 'Small.root', 'reason': 'No.'}]}}),
            ('unknown key in change.json: verdict', {'change': {'verdict': 'accepted'}}),
            ('the "## Review" section is written at publication, from review',
             {'approaches': {'Small/root/induction.md': APPROACH + '\n## Review\n\nA fine piece of work.\n'}}),
        )
        for message, options in cases:
            with self.subTest(message=message, options=options):
                self.assert_refused(self.peer_errors(**options), message)

    # -- the review of a candidate ------------------------------------------------------------------------

    def reviewed(self, proved=False):
        """A frozen candidate with every kind of element review judges: a definition, a statement without
        a proof, a statement proved in Lean, and the root with a new informal proof. With proved, the canon
        already has a proof of the root, so the new one would take its place."""
        if proved:
            self.held_sketch()
            self.start_pipeline()  # the scenario stands in place of the instance that setUp prepared
        more = module_text('''/-- The sum of the first `n` even numbers. -/
def evenSum : Nat → Nat
  | 0 => 0
  | n + 1 => evenSum n + 2 * (n + 1)

/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl

/-- A lead: the even sum exceeds the odd sum by `n`. -/
theorem lead (n : Nat) : evenSum n = oddSum n + n := by
  sorry''')
        folder = self.candidate(
            modules={'Small/More.lean': more}, replace={'Small.root': INFORMAL}, imports={'Small.root': ['Small.More']},
            records={'Small/root.md': ROOT_RECORD, 'Small/oddSum_succ.md': STEP_RECORD,
                     'Small/evenSum.md': record_text('The sum of the first n even numbers.'),
                     'Small/lead.md': record_text('The even sum exceeds the odd sum by n; not proved.')},
            questions=[{'id': 'speer-why', 'statement': 'Why is each step a square?', 'grounds': 'The proof does not say.'}])
        self.assertEqual(read_json(folder / 'prepared.json')['added'], ['Small.evenSum', 'Small.lead', 'Small.oddSum_succ'])
        task = {'kind': 'candidate', 'candidate': str(folder), 'candidate_hashes': runtime.tree_hashes(folder)}
        session = self.install('sreview', 'review', task)
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        self.engine.state['sessions']['sreview'] = session_record('sreview', 'review', None)
        self.engine.save()
        return folder, session

    def review_errors(self, session, assessment):
        write_json(session / 'output/assessment.json', assessment)
        return check_session(session)

    @staticmethod
    def judged(assessment, element, **changes):
        """The assessment with one element's verdict changed."""
        rows = [{**row, **changes} if row['element'] == element else row for row in assessment['elements']]
        return {**assessment, 'elements': rows}

    def test_review_judges_each_element_of_the_candidate_exactly_once_and_within_the_rules(self):
        folder, session = self.reviewed(proved=True)
        # The proof that is complete in Lean is left undetermined here, so that no formal check is due.
        good = self.verdicts(folder, **{'Small.oddSum_succ': {'correct': 'undetermined', 'accepted': False}})
        self.assertEqual([(row['element'], row['correct'], row['accepted'], row.get('replaces')) for row in good['elements']],
                         [('Small.evenSum', 'not_applicable', False, None), ('Small.lead', 'not_applicable', False, None),
                          ('Small.oddSum_succ', 'undetermined', False, None), ('Small.root', 'confirmed', True, True)])
        self.assertEqual(self.review_errors(session, good), [])
        # A new proof that is correct and held back, or one that does not take the place of the old one, is
        # judged like any other; review does not gate.
        self.assertEqual(self.review_errors(session, self.judged(good, 'Small.root', accepted=False)), [])
        self.assertEqual(self.review_errors(session, self.judged(good, 'Small.root', correct='not_confirmed',
                                                                 accepted=False, replaces=False)), [])
        rows = good['elements']
        once = 'judge each element the candidate adds or whose proof it replaces exactly once'
        without_replaces = [{k: v for k, v in row.items() if k != 'replaces'} for row in rows]
        cases = (
            (once, {**good, 'elements': rows[1:]}),
            (once, {**good, 'elements': rows + [rows[0]]}),
            (once, {**good, 'elements': rows[1:] + [{**rows[0], 'element': 'Small.oddSum'}]}),
            ('assessment.elements: array required', {k: v for k, v in good.items() if k != 'elements'}),
            ('correct is one of confirmed, not_confirmed, undetermined, not_applicable',
             self.judged(good, 'Small.root', correct='supported')),
            ('accepted must be Boolean', self.judged(good, 'Small.lead', accepted=None)),
            ('element reason', self.judged(good, 'Small.lead', reason=' ')),
            ('Small.root has a proof; judge whether it is correct',
             self.judged(good, 'Small.root', correct='not_applicable', accepted=False)),
            ('Small.oddSum_succ has a proof; judge whether it is correct',
             self.judged(good, 'Small.oddSum_succ', correct='not_applicable')),
            ('Small.evenSum has no proof to judge; use correct: not_applicable',
             self.judged(good, 'Small.evenSum', correct='confirmed')),
            ('Small.lead has no proof to judge', self.judged(good, 'Small.lead', correct='not_confirmed')),
            ('Small.lead has no proof to judge', self.judged(good, 'Small.lead', accepted=True)),
            ('only a proof confirmed as correct can be accepted',
             self.judged(good, 'Small.root', correct='undetermined')),
            ('only a proof confirmed as correct can be accepted',
             self.judged(good, 'Small.root', correct='not_confirmed')),
            ('Small.root already has a proof in the canon; say with "replaces"', {**good, 'elements': without_replaces}),
            ('Small.root already has a proof in the canon; say with "replaces"',
             self.judged(good, 'Small.root', replaces='yes')),
            ('publish must be Boolean', {**good, 'publish': 'yes'}),
            ('assessment.reason', {**good, 'reason': ''}),
            ('assessment.contribution', {k: v for k, v in good.items() if k != 'contribution'}),
            ('missing or escaping file: absent.md', {**good, 'feedback': 'absent.md'}),
            ('file must be a relative /-separated path: ../input.json', {**good, 'feedback': '../input.json'}),
        )
        for message, assessment in cases:
            with self.subTest(message=message):
                self.assert_refused(self.review_errors(session, assessment), message)

    def test_a_first_proof_enters_with_review_s_verdict_and_is_not_asked_whether_it_replaces(self):
        folder = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
        task = {'kind': 'candidate', 'candidate': str(folder), 'candidate_hashes': runtime.tree_hashes(folder)}
        session = self.install('sreview', 'review', task)
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        good = self.verdicts(folder)
        self.assertEqual(self.review_errors(session, good), [])
        row = {k: v for k, v in good['elements'][0].items() if k != 'replaces'}
        self.assertEqual(self.review_errors(session, {**good, 'elements': [row]}), [])
        # Whatever the verdict, the first proof enters; a later session does the repair (design record, 10.2).
        self.assertEqual(self.review_errors(session, {**good, 'elements': [{**row, 'correct': 'not_confirmed',
                                                                             'accepted': False}]}), [])
        self.assert_refused(self.review_errors(session, {**good, 'elements': [{**row, 'replaces': False}]}),
                            'Small.root has no proof in the canon yet, so its first proof enters with your verdict')

    def test_replaces_is_refused_on_an_element_the_candidate_adds(self):
        # The canon has a proof of the root. A declaration that proves the root under another name is an
        # addition all the same: it enters beside that proof with review's verdict, so "replaces" is not asked of it.
        self.held_sketch()
        self.start_pipeline()  # the scenario stands in place of the instance that setUp prepared
        alternative = module_text('/-- Another proof of the root, by pairing terms. -/\n'
                                  'theorem root_alt (n : Nat) : oddSum n = n * n := by\n  sorry')
        folder = self.candidate(modules={'Small/Alt.lean': alternative},
                                records={'Small/root_alt.md': record_text('The root, proved by pairing terms.', proves='Small.root',
                                                                          proof='Pair each odd number with a gnomon.')})
        receipt = read_json(folder / 'prepared.json')
        self.assertEqual((receipt['added'], receipt['replaced']), (['Small.root_alt'], []))
        task = {'kind': 'candidate', 'candidate': str(folder), 'candidate_hashes': runtime.tree_hashes(folder)}
        session = self.install('sreview', 'review', task)
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        good = self.verdicts(folder)
        self.assertEqual(self.review_errors(session, good), [])
        for value in (True, False):
            with self.subTest(replaces=value):
                self.assert_refused(self.review_errors(session, self.judged(good, 'Small.root_alt', replaces=value)),
                                    'Small.root_alt is added by the candidate; "replaces" is asked only of a proof that '
                                    'would take the place of one the canon has')

    def test_a_proof_that_alone_settles_a_statement_gives_way_only_to_a_new_proof_review_confirms_and_accepts(self):
        self.settled_canon()
        # The candidate replaces the proof that alone settles Small.pair, by one that the peer's check carries,
        # and one of the two proofs that settle Small.twin.
        folder = self.candidate(replace={'Small.pair': settled_text('pair', ['low']),
                                         'Small.twin': settled_text('twin', ['low'], 'sorry')})
        task = {'kind': 'candidate', 'candidate': str(folder), 'candidate_hashes': runtime.tree_hashes(folder)}
        session = self.install('sreview', 'review', task)
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        self.engine.state['sessions']['sreview'] = session_record('sreview', 'review', None)
        self.engine.save()
        # Confirming the new proof of Small.pair, which is complete in Lean, needs the review's own compile.
        with patch('builtins.print'):
            self.assertEqual(verify(session, 64, 120), 0)
        good = {**self.verdicts(folder), 'formal_check': {'build': read_json(session / 'work/verify/outcome.json')['build']}}
        self.assertEqual([(row['element'], row['correct'], row['accepted'], row['replaces']) for row in good['elements']],
                         [('Small.pair', 'confirmed', True, True), ('Small.twin', 'confirmed', True, True)])
        self.assertEqual(self.review_errors(session, good), [])
        message = ('Small.pair holds the proof through which a settled statement is settled; a new proof takes its place '
                   'only when you confirm and accept it, so answer "replaces": false otherwise')
        for verdict in ({'correct': 'confirmed', 'accepted': False}, {'correct': 'not_confirmed', 'accepted': False},
                        {'correct': 'undetermined', 'accepted': False}):
            with self.subTest(**verdict):
                self.assert_refused(self.review_errors(session, self.judged(good, 'Small.pair', replaces=True, **verdict)),
                                    message)
                # Leaving the old proof in place is open under every verdict.
                self.assertEqual(self.review_errors(session, self.judged(good, 'Small.pair', replaces=False, **verdict)), [])
                # Small.twin stays settled through Small.twinAlt, so its new proof may take the place of the old one
                # under any verdict.
                self.assertEqual(self.review_errors(session, self.judged(good, 'Small.twin', replaces=True, **verdict)), [])

    def test_review_s_concerns_and_findings_name_what_exists(self):
        # The verdicts on question proposals and resolutions are checked with the questions
        # (test_questions.QuestionCheckTests).
        self.operator_questions()
        folder, session = self.reviewed()
        good = self.verdicts(folder, **{'Small.oddSum_succ': {'correct': 'undetermined', 'accepted': False}})
        concern = {'id': 'gap', 'targets': ['Small.root', 'Small.lead'], 'reason': 'The step is asserted.',
                   'evidence': 'The record gives no derivation.'}
        finding = {'concerns': [], 'status': 'confirmed', 'reason': 'The definition is the intended one.',
                   'validates': ['Small.root'], 'invalidates': [], 'reopens': ['op-scale']}
        # A concern may question an element that this candidate adds.
        self.assertEqual(self.review_errors(session, {**good, 'concerns': [concern], 'findings': [finding]}), [])
        verdict = good['questions'][0]
        cases = (
            ('concern targets an unknown element: Small.ghost', {'concerns': [{**concern, 'targets': ['Small.ghost']}]}),
            ('a concern names the elements whose proof it questions', {'concerns': [{**concern, 'targets': []}]}),
            ('concern.reason', {'concerns': [{**concern, 'reason': ''}]}),
            ('concern.evidence', {'concerns': [{k: v for k, v in concern.items() if k != 'evidence'}]}),
            ('duplicate id', {'concerns': [concern, concern]}),
            ('invalid identifier', {'concerns': [{**concern, 'id': 'a gap'}]}),
            ('unknown finding status', {'findings': [{**finding, 'status': 'withdrawn'}]}),
            ('finding.reason', {'findings': [{**finding, 'reason': ' '}]}),
            ('unknown concern', {'findings': [{**finding, 'concerns': ['c0/none']}]}),
            ('finding targets an unknown element: Small.ghost', {'findings': [{**finding, 'invalidates': ['Small.ghost']}]}),
            ('finding targets an unknown element: Small.ghost', {'findings': [{**finding, 'validates': ['Small.ghost']}]}),
            ('finding reopens an unknown question', {'findings': [{**finding, 'reopens': ['nope']}]}),
        )
        for message, changes in cases:
            with self.subTest(message=message):
                self.assert_refused(self.review_errors(session, {**good, **changes}), message)
        # An excluded candidate changes nothing that is shared: no question admitted, no concern, no finding.
        declined = [{**verdict, 'verdict': 'declined'}]
        excluded = {**good, 'publish': False}
        message = 'excluded candidate cannot change shared mathematical state'
        self.assert_refused(self.review_errors(session, excluded), message)
        self.assert_refused(self.review_errors(session, {**excluded, 'questions': declined, 'concerns': [concern]}), message)
        self.assert_refused(self.review_errors(session, {**excluded, 'questions': declined, 'findings': [finding]}), message)
        self.assertEqual(self.review_errors(session, {**excluded, 'questions': declined}), [])
        # The candidate is the one that was assigned, byte for byte.
        write(folder / 'records/Small/lead.md', record_text('Another description.'))
        self.assertEqual(self.review_errors(session, good), ['candidate changed after review assignment'])

    def test_confirming_a_proof_that_is_complete_in_lean_needs_the_review_s_own_compile(self):
        folder, session = self.reviewed()
        receipt = read_json(folder / 'prepared.json')
        confirmed = self.verdicts(folder)
        self.assertEqual(next(row for row in confirmed['elements'] if row['element'] == 'Small.oddSum_succ')['correct'],
                         'confirmed')
        # Without confirming that proof, review owes no compile.
        self.assertEqual(self.review_errors(session, self.judged(confirmed, 'Small.oddSum_succ', correct='not_confirmed',
                                                                 accepted=False)), [])
        self.assert_refused(self.review_errors(session, confirmed),
                            'confirming a proof that is complete in Lean needs formal_check')
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': 'the build'}}),
                            'formal_check.build is the ID of the build that commands.verify reported')
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': 'b' + '0' * 32}}),
                            'formal check must be a finished build of this reviewing session')
        # The peer's own build of the candidate is not the review's.
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': receipt['build']}}),
                            'formal check must be a finished build of this reviewing session')
        # Nor is a build of the review that took the changed modules from the cache: review compiles them itself.
        cached = build_candidate(self.instance, 'sreview', folder, session / 'work/cached', 64, 120, 'peer')
        self.assertTrue(cached['ok'], cached['errors'])
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': cached['build']}}),
                            'review must compile the changed module')
        # commands.verify compiles the changed modules afresh and leaves its outcome with the session.
        with patch('builtins.print'):
            self.assertEqual(verify(session, 64, 120), 0)
        outcome = read_json(session / 'work/verify/outcome.json')
        self.assertTrue(outcome['ok'])
        self.assertEqual(outcome['tree'], tree_hash(folder, skip=('prepared.json',)))
        self.assertEqual(self.review_errors(session, {**confirmed, 'formal_check': {'build': outcome['build']}}), [])
        # The broker answers a submission repeated while the first still ran with a record that points to
        # the first; the ID of the repeat is audited as the build it stands for.
        repeat = 'b' + 'd' * 32
        (self.instance / 'runner/lean/builds' / repeat).mkdir()
        write_json(self.instance / 'runner/lean/builds' / repeat / 'result.json',
                   {'id': repeat, 'status': 'duplicate', 'duplicate_of': outcome['build']})
        self.assertEqual(self.review_errors(session, {**confirmed, 'formal_check': {'build': repeat}}), [])
        # The build named is the one of the last successful verify.
        write_json(session / 'work/verify/outcome.json', {**outcome, 'ok': False})
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': outcome['build']}}),
                            'formal_check.build is not the build of the last successful commands.verify')
        (session / 'work/verify/outcome.json').unlink()
        self.assert_refused(self.review_errors(session, {**confirmed, 'formal_check': {'build': outcome['build']}}),
                            'formal_check.build is not the build of the last successful commands.verify')

    # -- a comprehensive review ---------------------------------------------------------------------------

    def test_a_comprehensive_review_gives_findings_about_elements_and_questions_that_exist(self):
        self.operator_questions()
        task = {'kind': 'comprehensive', 'concerns': [], 'conflicts': [], 'purpose': 'Trace the questioned proofs.'}
        session = self.install('sexamine', 'review', task)
        (session / 'output/feedback.md').write_text('Traced the root to its definitions.', encoding='utf-8')
        finding = {'concerns': [], 'status': 'confirmed', 'reason': 'The proof was not derived.',
                   'invalidates': ['Small.root'], 'validates': [], 'reopens': ['op-scale']}
        concern = {'id': 'gap', 'targets': ['Small.root'], 'reason': 'The step is asserted.',
                   'evidence': 'The record gives no derivation.'}
        good = {'feedback': 'feedback.md', 'findings': [finding], 'concerns': [concern]}
        self.assertEqual(self.review_errors(session, good), [])
        self.assertEqual(self.review_errors(session, {'feedback': 'feedback.md', 'findings': []}), [])
        cases = (
            ('a file reference is a nonempty relative path', {k: v for k, v in good.items() if k != 'feedback'}),
            ('findings: array required', {k: v for k, v in good.items() if k != 'findings'}),
            ('unknown finding status', {**good, 'findings': [{**finding, 'status': 'open'}]}),
            ('finding.concerns: array required', {**good, 'findings': [{k: v for k, v in finding.items() if k != 'concerns'}]}),
            ('finding targets an unknown element: Small.ghost', {**good, 'findings': [{**finding, 'invalidates': ['Small.ghost']}]}),
            ('finding reopens an unknown question', {**good, 'findings': [{**finding, 'reopens': ['nope']}]}),
            ('concern targets an unknown element: Small.ghost', {**good, 'concerns': [{**concern, 'targets': ['Small.ghost']}]}),
        )
        for message, assessment in cases:
            with self.subTest(message=message):
                self.assert_refused(self.review_errors(session, assessment), message)

    # -- the organizer --------------------------------------------------------------------------------------

    def organizer_errors(self, organization, change=None, files=None, prepare=True, batch=('c1', 'c2'), receipt=None):
        session = self.install('sorganizer', 'organizer', {'batch': list(batch), 'batch_frozen': True})
        output = session / 'output'
        write_json(output / 'organization.json', organization)
        for name, text in (files or {}).items():
            write(output / name, text)
        if change is not None:
            write_json(output / 'change.json', change)
            if prepare:
                self.prepare(output, role='organizer', expect_ok=False)
            if receipt:
                write_json(output / 'prepared.json', {**read_json(output / 'prepared.json'), **receipt})
        return check_session(session)

    def test_an_organizer_answers_for_its_exact_batch(self):
        self.operator_questions()
        # The rules for question merges are checked with the questions (test_questions.QuestionKnowledgeTests).
        merge = {'from': 'op-scale', 'into': 'speer-taken', 'reason': 'Both ask why the sums are squares.'}
        good = {'batch': ['c1', 'c2'], 'merge_questions': [merge]}
        self.assertEqual(self.organizer_errors(good), [])
        self.assertEqual(self.organizer_errors({'batch': ['c1', 'c2']}), [])
        cases = (
            ('organizer must acknowledge its exact assigned batch', {**good, 'batch': ['c1']}),
            ('organizer must acknowledge its exact assigned batch', {**good, 'batch': ['c2', 'c1']}),
            ('organizer must acknowledge its exact assigned batch', {'merge_questions': []}),
        )
        for message, organization in cases:
            with self.subTest(message=message):
                self.assert_refused(self.organizer_errors(organization), message)

    def test_an_organizer_change_is_prepared_and_holds_lean_and_records_only(self):
        self.operator_questions()
        organization = {'batch': ['c1', 'c2'], 'merge_questions': []}
        change = {'title': 'Agreements', 'description': 'Elements stating that two definitions agree.'}
        self.assertEqual(self.organizer_errors(organization, change), [])
        self.assert_refused(self.organizer_errors(organization, change, prepare=False),
                            'the candidate has not been prepared; run commands.prepare')
        self.assert_refused(self.organizer_errors(organization, {'title': 'Agreements'}), 'change.json needs a nonempty "description"')
        only = 'an organizer change holds Lean modules, replacements and records only'
        proposal = {'id': 'sorganizer-why', 'statement': 'Why?', 'grounds': 'Unexplained.'}
        cases = (
            (only, {'change': {**change, 'questions': [proposal]}}),
            (only, {'change': {**change, 'resolutions': [{'id': 'settles', 'question': 'op-scale'}]},
                    'files': {'questions/op-scale.md': UNDERSTOOD}}),
            (only, {'change': change, 'files': {'approaches/Small/root/induction.md': APPROACH}}),
            (only, {'change': change, 'files': {'questions/q0.md': UNDERSTANDING}}),
        )
        for message, options in cases:
            with self.subTest(message=message, options=sorted(options)):
                self.assert_refused(self.organizer_errors(organization, **options), message)
        # A retirement names a declaration that is another proof of the statement it goes into. The receipt
        # is given as successful here, so that the check of the retirement itself is what answers.
        retire = {'alternative': 'Small.oddSum', 'into': 'Small.root', 'reason': 'The proof can stand under the root.'}
        passed = {'ok': True, 'errors': []}
        cases = (
            ('Small.oddSum is not another proof of Small.root', retire),
            ('a retirement has "alternative", "into" and "reason"', {k: v for k, v in retire.items() if k != 'reason'}),
            ('a retirement has "alternative", "into" and "reason"', {**retire, 'note': 'x'}),
        )
        for message, item in cases:
            with self.subTest(message=message):
                self.assert_refused(self.organizer_errors(organization, {**change, 'retire': [item]}, receipt=passed), message)
        self.assert_refused(self.organizer_errors(organization, {**change, 'retire': [retire]}), 'prepare reported errors: retiring')

    def test_lean_files_and_deletions_of_an_organizer_take_effect_only_with_a_change(self):
        organization = {'batch': ['c1', 'c2'], 'merge_questions': []}
        self.assertEqual(self.organizer_errors({**organization, 'delete': []}), [])
        message = 'Lean files and "delete" take effect only as part of a change; write change.json with them'
        cases = (
            ('delete', {**organization, 'delete': ['Small.Root']}, {}),
            ('rewrite/lean', organization, {'rewrite/lean/Small/Root.lean': ROOT}),
            ('lean', organization, {'lean/Small/Zero.lean': ZERO}),
        )
        for label, data, files in cases:
            with self.subTest(label):
                self.assert_refused(self.organizer_errors(data, files=files), message)

    def test_a_retirement_keeps_the_proof_that_stands_higher(self):
        # The proof under the statement's own name leaves the source, and no review compares the two proofs,
        # so the alternative that takes its place may not stand lower than it.
        organization = {'batch': ['c1', 'c2'], 'merge_questions': []}
        change = {'title': 'The alternative under the root', 'description': 'The alternative proof stands under Small.root.',
                  'retire': [{'alternative': 'Small.root_alt', 'into': 'Small.root',
                              'reason': 'The module of the root can hold the proof now.'}]}
        passed = {'ok': True, 'errors': []}  # the check of the retirement itself is what answers
        lower = ('Small.root_alt would take the place of a proof of Small.root that stands higher; '
                 'a retirement keeps the proof with the higher standing')

        def standings():
            elements = replay(self.instance)['elements']
            return [(elements[n]['standing'], elements[n]['lean_proof']) for n in ('Small.root_alt', 'Small.root')]

        def finding(reason, **changes):
            self.event(runtime.uid('v'), 'review', {'feedback': 'feedback.md', 'concerns': [],
                                                    'findings': [{'concerns': [], 'status': 'confirmed', 'reason': reason,
                                                                  **changes}]})

        alternative = module_text('/-- Another proof of the root, by pairing terms. -/\n'
                                  'theorem root_alt (n : Nat) : oddSum n = n * n := by\n  sorry')
        first = self.candidate(modules={'Small/Alt.lean': alternative},
                               records={'Small/root_alt.md': record_text('The root, proved by pairing terms.', proves='Small.root',
                                                                         proof='Pair each odd number with a gnomon.')})
        self.publish(first, engine=self.engine)
        # An accepted alternative may go into a statement without a proof of its own, or with one that stands as high.
        self.assertEqual(standings(), [('accepted', 'sorry'), ('no_proof', 'sorry')])
        self.assertEqual(self.organizer_errors(organization, change, receipt=passed), [])
        own = self.candidate(replace={'Small.root': SKETCH}, records={'Small/root.md': ROOT_RECORD})
        self.publish(own, engine=self.engine)
        self.assertEqual(standings(), [('accepted', 'sorry'), ('accepted', 'sorry')])
        self.assertEqual(self.organizer_errors(organization, change, receipt=passed), [])
        # An alternative that is not confirmed does not take the place of an accepted proof.
        finding('The pairing skips the first term.', invalidates=['Small.root_alt'])
        self.assertEqual(standings(), [('not_confirmed', 'sorry'), ('accepted', 'sorry')])
        self.assert_refused(self.organizer_errors(organization, change, receipt=passed), lower)
        # An accepted informal alternative does not take the place of an accepted proof that is complete in Lean.
        finding('The first term is paired after all.', validates=['Small.root_alt'])
        formal = self.candidate(replace={'Small.root': DOC + STATEMENT + '  rfl'})
        self.publish(formal, engine=self.engine)
        self.assertEqual(standings(), [('accepted', 'sorry'), ('accepted', 'complete')])
        self.assert_refused(self.organizer_errors(organization, change, receipt=passed), lower)


if __name__ == '__main__':
    unittest.main()
