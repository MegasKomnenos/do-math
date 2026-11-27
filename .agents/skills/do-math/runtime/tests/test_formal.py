"""What makes a statement formal, and whether the settled root is the root that was posed.

A statement is formal when its module compiles and Lean reports that its proof depends on allowed
axioms only. The report is `Lean.collectAxioms`, asked in the extraction of the index
(canon.extraction_source); do-math works out no axioms of its own and nothing checks Lean's answer a
second time. Whether the root that was settled is the root of the instance's first commit is read
from the two indexes and from the files of the modules that the root's module imported at that
commit (canon.statement_differences, canon.definition_modules, Runner.check_root). A candidate that
would change one of those files is refused when it is prepared and again at publication
(canon.check_definition_modules).

The first classes run with the stand-in compiler of tests/canon_lean.py and show what the runtime does
with the rows: which modules it extracts, what it stores, what it does with files and state that an
earlier version of this code left. The last class runs the same paths with Lean itself, because the
point of the design is that Lean gives the answer: a `sorry`, an axiom of the author and
`native_decide` are reported by Lean, a theorem in a module that did not change is compiled again
and reported anew when what it rests on changed, and the statement identities compared for the root
are those of Lean's terms. It needs Lean 4.36.0, looked for under `.skill-workspace/do-math-toolchains`
of a folder above this file, or named by the environment variable DO_MATH_TEST_LEAN, and is skipped
without it. A name in that variable that is not a file is an error, so that these tests are not skipped unnoticed.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import uuid
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_tool
import runner as runtime
import support
from canon import (Canon, beyond_allowed, copy_tree, definition_modules, empty_index, library_modules, start_build,
                   statement_differences, update_index, wait_build)
from canon_tool import view
from knowledge import frontier_lines, replay
from lean_broker import Paths, job_record
from runtime_support import read_json, write_json
from settings import load_settings, validate
from support import (ROOT, ROOT_STATEMENTS, SUM_ZERO, InstanceCase, ScenarioCase, earlier_form, fixture_settings,
                     module_text, record_text, theorem)

ALLOWED = ['propext', 'Classical.choice', 'Quot.sound']
OPEN_ZERO = theorem('sumZero', SUM_ZERO)
ZERO = theorem('sumZero', SUM_ZERO, proof='rfl')
ZERO_RECORD = record_text('The empty sum is zero.', weight='unit')
PROVED_ZERO_RECORD = record_text('The empty sum is zero.', weight='unit', proof='By the definition.')
ABOVE = theorem('fromZero', SUM_ZERO, uses=['sumZero'], proof='exact h1')
ABOVE_RECORD = record_text('The same value, from the lemma.')
DEFINITION_CHANGED = 'the text of the definition Small.oddSum is not the text the first commit has'
FILE_CHANGED = 'the file of the definition module Small.Defs is not the file the first commit has'


def reindex(case):
    """Take the index of the canon's sources again, as `init` takes it, and install it under the next revision.

    A test changes a source of the canon behind the runner and then calls this, so that the index says
    what Lean now makes of the sources. No publication could bring that state about; the check of the
    root exists for the case that it came about all the same."""
    canon = Canon(case.instance)
    library = read_json(case.instance / 'instance.json')['library']
    stage = case.root / ('reindex-' + uuid.uuid4().hex)
    copy_tree(canon.lean, stage)
    modules = [module for module, _ in library_modules(stage, library)]
    before = canon.load_index()
    outcome = wait_build(case.instance, start_build(case.instance, stage, library, 'operator', case.expect_mb, modules, []),
                         case.patience)
    case.assertTrue(outcome and outcome['ok'], outcome)
    index = update_index(empty_index(), outcome['rows'], {}, stage, before['revision'] + 1)
    index['pairs'] = before['pairs']
    write_json(canon.index, index)
    return index


def rewrite(path, old, new):
    text = path.read_text(encoding='utf-8')
    assert old in text, old
    path.write_text(text.replace(old, new), encoding='utf-8', newline='\n')


class BothCompilers:
    """What the stand-in compiler and Lean itself are both held to: a test written here runs in a class of each.

    FormalStatusTests runs it on the instance that tests/canon_lean.py compiled and LeanItselfTests on the
    instance that Lean compiled, so that the two compilers are asked the same thing with one expectation."""

    def element(self, name):
        return replay(self.instance)['elements'][name]

    def test_an_axiom_the_author_declares_is_refused_and_what_rests_on_it_is_not_formal(self):
        body = 'private axiom shortcut : oddSum 1 = 1\n\n' + theorem('onShortcut', ': oddSum 1 = 1', uses=['shortcut'], proof='exact h1')
        folder = self.candidate(modules={'Small/Short.lean': module_text(body)},
                                records={'Small/onShortcut.md': record_text('One odd number sums to one.')}, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertTrue(any('Small.shortcut is declared as an axiom in Small.Short' in error for error in result['errors']),
                        result['errors'])
        entry = result['entries']['Small.onShortcut']
        self.assertEqual((entry['lean_proof'], entry['axioms']), ('complete', ['_private.Small.Short.0.Small.shortcut']))
        self.assertEqual(beyond_allowed(entry, ALLOWED), ['_private.Small.Short.0.Small.shortcut'])

    def test_a_proof_that_names_a_statement_its_file_does_not_import_does_not_compile(self):
        # `fromZero` names `sumZero`, and its module imports the definitions alone. Lean reads the modules a file
        # imports and no other, so the name is unknown there although the candidate holds the module that declares it.
        folder = self.candidate(modules={'Small/Zero.lean': module_text(OPEN_ZERO), 'Small/Above.lean': module_text(ABOVE)},
                                records={'Small/sumZero.md': ZERO_RECORD, 'Small/fromZero.md': ABOVE_RECORD}, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'])
        self.assertTrue(any(error.startswith('Small.Above:') and 'sumZero' in error for error in result['errors']),
                        result['errors'])

    def test_a_private_helper_under_the_name_of_a_statement_belongs_to_that_statement(self):
        # `holder.step` is private and its name extends `holder`. The proof of `holder` is complete and does not
        # name it; the proof of `throughStep` names it.
        body = '\n\n'.join(['private theorem holder.step : oddSum 1 = 1 := by\n  sorry',
                            theorem('holder', SUM_ZERO, proof='rfl'),
                            theorem('throughStep', ': oddSum 1 = 1', uses=['holder.step'], proof='exact h1')])
        folder = self.candidate(modules={'Small/Helper.lean': module_text(body)},
                                records={'Small/holder.md': record_text('The empty sum is zero.'),
                                         'Small/throughStep.md': record_text('One odd number sums to one.')})
        result = read_json(folder / 'prepared.json')
        self.assertEqual(result['added'], ['Small.holder', 'Small.throughStep'])  # the helper is no element
        holder, through = result['entries']['Small.holder'], result['entries']['Small.throughStep']
        # The helper's open proof counts as the statement's, although Lean's list of axioms for the statement is empty.
        self.assertEqual((holder['lean_proof'], holder['axioms'], beyond_allowed(holder, ALLOWED)), ('sorry', [], ['sorryAx']))
        # A proof that names the helper names the statement, and Lean reports the `sorry` beneath it.
        self.assertIn('Small.holder', through['uses'])
        self.assertEqual((through['lean_proof'], through['axioms']), ('complete', ['sorryAx']))


class FormalStatusTests(BothCompilers, InstanceCase):

    def lemma_and_what_rests_on_it(self):
        """`sumZero` without a proof in one module, and `fromZero`, proved from it, in a module that imports it.

        Published once for the test process (InstanceCase.scenario); a test that asks works on a copy of it."""
        def build():
            folder = self.candidate(modules={'Small/Zero.lean': module_text(OPEN_ZERO),
                                             'Small/Above.lean': module_text(ABOVE, imports=('Small.Defs', 'Small.Zero'))},
                                    records={'Small/sumZero.md': ZERO_RECORD, 'Small/fromZero.md': ABOVE_RECORD})
            self.publish(folder)
        self.scenario('open lemma and what rests on it', build)

    def test_a_published_proof_is_formal_by_the_axioms_lean_reported(self):
        folder = self.candidate(modules={'Small/Zero.lean': module_text(ZERO)}, records={'Small/sumZero.md': ZERO_RECORD})
        # Whether a proof is formal is Lean's report of its axioms and no judgment of review. Review leaves the
        # proof undetermined here, so the publication asks no compile of the review's own.
        self.publish(folder, self.verdicts(folder, **{'Small.sumZero': {'correct': 'undetermined', 'accepted': False}}))
        entry = Canon(self.instance).load_index()['entries']['Small.sumZero']
        self.assertEqual((entry['axioms'], entry['lean_proof']), ([], 'complete'))
        self.assertTrue(self.element('Small.sumZero')['formal'])
        self.assertIn('proved in Lean from the allowed axioms', view(self.instance, replay(self.instance), 'Small.sumZero'))
        # The root has no proof: Lean reports `sorryAx` for it.
        root = self.element('Small.root')
        self.assertEqual((root['axioms'], root['lean_proof'], root['formal']), (['sorryAx'], 'sorry', False))

    def test_a_complete_proof_that_names_an_open_statement_is_a_proof_and_is_not_formal(self):
        self.lemma_and_what_rests_on_it()
        above = self.element('Small.fromZero')
        self.assertEqual((above['lean_proof'], above['axioms'], above['formal']), ('complete', ['sorryAx'], False))
        self.assertEqual(above['standing'], 'accepted')
        self.assertFalse(above['settled'])  # it rests on a statement without a proof

    def test_a_theorem_in_a_module_that_did_not_change_becomes_formal_when_what_it_rests_on_is_proved(self):
        self.lemma_and_what_rests_on_it()
        source = self.instance / 'canon/lean/Small/Above.lean'
        before = source.read_bytes()
        folder = self.candidate(replace={'Small.sumZero': ZERO}, records={'Small/sumZero.md': PROVED_ZERO_RECORD})
        # The module of `fromZero` is not changed by the candidate, and its index is taken again with it.
        self.assertEqual(read_json(folder / 'prepared.json')['changed_modules'], ['Small.Zero'])
        # Review leaves the proof of the lemma undetermined at first, so the lemma is not settled and its proof
        # can still be taken out again. What Lean reports for the theorem above follows the proof all the same.
        unconfirmed = self.verdicts(folder, **{'Small.sumZero': {'correct': 'undetermined', 'accepted': False}})
        _, engine = self.publish(folder, unconfirmed)
        self.assertEqual(source.read_bytes(), before)
        above = self.element('Small.fromZero')
        self.assertEqual((above['axioms'], above['formal'], above['settled']), ([], True, False))
        # And back: when the proof of the lemma is opened again, what rests on it is no longer formal.
        folder = self.candidate(replace={'Small.sumZero': OPEN_ZERO}, records={'Small/sumZero.md': ZERO_RECORD})
        self.publish(folder, engine=engine)
        above = self.element('Small.fromZero')
        self.assertEqual((above['axioms'], above['formal']), (['sorryAx'], False))
        # A proof of the lemma that review confirms and accepts settles what rests on it as well.
        folder = self.candidate(replace={'Small.sumZero': ZERO}, records={'Small/sumZero.md': PROVED_ZERO_RECORD})
        self.publish(folder, engine=engine)
        above = self.element('Small.fromZero')
        self.assertEqual((above['axioms'], above['formal'], above['settled']), ([], True, True))


class EarlierFilesTests(ScenarioCase):
    """Settings, an index and a runner state that an earlier version of this code wrote."""

    def test_a_settings_file_that_names_a_judge_is_accepted_and_the_key_has_no_effect(self):
        for value in ('auto', None, {'export': ['leanexport'], 'compare': ['lake', 'comparator']}):
            with self.subTest(value=value):
                self.configure(lean={'judge': value})
                self.assertIn('judge', read_json(self.instance / 'settings.json')['lean'])
                self.assertNotIn('judge', load_settings(self.instance)['lean'])
                runtime.Runner(self.instance, self.skill)
                self.assertEqual(runtime.status(self.instance)['root_state'], 'unresolved')
        # Another unknown key is still a mistake.
        with self.assertRaisesRegex(ValueError, 'unknown setting: lean.jugde'):
            validate({**fixture_settings(), 'lean': {**fixture_settings()['lean'], 'jugde': None}})

    def test_an_index_of_the_earlier_code_is_read_as_it_stood_and_rewritten_by_the_next_publication(self):
        self.formal()
        canon = Canon(self.instance)
        present = canon.load_index()
        model = replay(self.instance)
        write_json(canon.index, earlier_form(present))
        self.assertIn('direct_axioms', read_json(canon.index)['entries']['Small.root'])
        self.assertEqual(canon.load_index(), present)
        again = replay(self.instance)
        self.assertEqual(again['root_state'], 'formal_proved')
        self.assertEqual({name: (e['formal'], e['axioms']) for name, e in again['elements'].items()},
                         {name: (e['formal'], e['axioms']) for name, e in model['elements'].items()})
        self.assertEqual(runtime.status(self.instance)['root_state'], 'formal_proved')
        # Reading wrote nothing. A publication that changes a Lean source leaves the file in the present form.
        self.assertIn('direct_axioms', read_json(canon.index)['entries']['Small.root'])
        folder = self.candidate(modules={'Small/Zero.lean': module_text(ZERO)}, records={'Small/sumZero.md': ZERO_RECORD})
        # What is read below is the form of the index, not the verdict on the new proof. That proof is complete
        # in Lean and is left undetermined, so that no compile of the review is due.
        self.publish(folder, self.verdicts(folder, **{'Small.sumZero': {'correct': 'undetermined', 'accepted': False}}))
        written = read_json(canon.index)
        self.assertEqual(sorted(written), ['aux', 'entries', 'hidden', 'modules', 'pairs', 'revision'])
        self.assertTrue(all('axioms' in entry and 'direct_axioms' not in entry for entry in written['entries'].values()))
        self.assertEqual(replay(self.instance)['root_state'], 'formal_proved')

    def test_a_publication_that_the_earlier_code_left_waiting_for_its_judge_is_staged_again_and_published(self):
        engine = runtime.Runner(self.instance, self.skill)
        folder = self.candidate(modules={'Small/Zero.lean': module_text(ZERO)}, records={'Small/sumZero.md': ZERO_RECORD})
        # Review leaves the proof undetermined: its verdict is not what this test is about, and a confirmed proof
        # would ask for a compile of the review's own before the publication is queued. Lean's report makes it formal all the same.
        unconfirmed = self.verdicts(folder, **{'Small.sumZero': {'correct': 'undetermined', 'accepted': False}})
        with patch.object(InstanceCase, 'drain'):
            self.publish(folder, unconfirmed, engine=engine, expect=False)  # queued, and not carried further
        with patch.object(support.subprocess, 'Popen', support.POPEN):
            engine.publish()
        publication = engine.state['publication']
        self.assertEqual(publication['stage'], 'build')
        # As the earlier code saved it: no mark of the extraction, the stage after the check, the judge's
        # bookkeeping, and a staged index in the earlier form.
        stage = self.instance / 'runner' / ('stage-' + publication['event']['id'])
        del publication['extraction']
        publication.update(stage='judge', built=publication['build'],
                           judge={'names': ['Small.sumZero'], 'job': 'j' + '0' * 32, 'attempts': 1})
        write_json(stage / 'index.json', earlier_form(Canon(self.instance).load_index()))
        engine.save()
        engine = runtime.Runner(self.instance, self.skill)
        self.drain(engine)
        self.assertIsNone(engine.state['publication'])
        self.assertTrue(replay(self.instance)['elements']['Small.sumZero']['formal'])
        self.assertNotIn('direct_axioms', read_json(Canon(self.instance).index)['entries']['Small.sumZero'])

    def test_a_candidate_build_made_with_another_extraction_is_made_again(self):
        folder = self.candidate(modules={'Small/Zero.lean': module_text(ZERO)}, records={'Small/sumZero.md': ZERO_RECORD},
                                prepare=False)
        work = self.root / 'prepare'
        first = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        state = read_json(work / 'state.json')
        self.assertEqual(state['extraction'], canon_tool.EXTRACTION)
        # The same candidate on the same canon keeps its build.
        self.assertEqual(canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')['build'], first['build'])
        self.assertEqual(read_json(work / 'state.json')['build'], state['build'])
        # A build kept from a version whose extraction printed other rows is not read.
        write_json(work / 'state.json', {key: value for key, value in state.items() if key != 'extraction'})
        self.assertTrue(canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')['ok'])
        self.assertNotEqual(read_json(work / 'state.json')['build'], state['build'])


class RootCheckTests(ScenarioCase):
    def requests(self):
        return [read_json(path) for path in sorted((self.instance / 'control/requests').glob('*.json'))]

    def test_nothing_is_compared_before_the_root_is_formally_settled(self):
        self.direct()  # an accepted proof that is written and not complete in Lean
        engine = runtime.Runner(self.instance, self.skill)
        engine.check_root()
        self.assertIsNone(engine.state.get('root_check'))
        self.assertIsNone(runtime.status(self.instance)['root_check'])

    def test_the_root_as_proved_is_the_root_as_posed(self):
        self.formal()
        engine = runtime.Runner(self.instance, self.skill)
        engine.check_root()
        first = runtime.git(self.instance, 'rev-list', '--max-parents=0', 'HEAD').split()[0]
        record = runtime.status(self.instance)['root_check']
        self.assertEqual({key: record[key] for key in ('proof', 'revision', 'status', 'differences', 'compared_with_commit')},
                         {'proof': 'Small.root', 'revision': engine.model['revision'], 'status': 'unchanged',
                          'differences': [], 'compared_with_commit': first})
        self.assertEqual(self.requests(), [])
        # The frontier ends at such a root, and its line says that the proof which settles it is formal.
        self.assertEqual(frontier_lines(engine.model),
                         ['- `Small.root` — odd numbers sum to a square — settled by a formal proof'])
        # The same proof on the same library is not compared again.
        with patch.object(runtime, 'git', side_effect=AssertionError('compared again')):
            engine.check_root()
        self.assertEqual(engine.state['root_check'], record)

    def test_a_definition_that_changed_since_the_first_commit_is_found_and_sent_to_review(self):
        self.formal()
        rewrite(self.instance / 'canon/lean/Small/Defs.lean', '| 0 => 0', '| 0 => 0 * 1')
        reindex(self)
        engine = runtime.Runner(self.instance, self.skill)
        engine.check_root()
        record = engine.state['root_check']
        # The stand-in compiler takes the whole text of this definition for its statement, since the text
        # has no `:=`. Lean keeps the type and the body apart; LeanItselfTests shows what it reports.
        difference = 'the statement of Small.oddSum is not the statement the first commit has'
        # The edit also left the file of the definition's module other than the first commit has it.
        self.assertEqual((record['status'], record['differences']), ('changed', [difference, FILE_CHANGED]))
        requests = self.requests()
        self.assertEqual([(r['kind'], r['elements']) for r in requests], [('review', ['Small.root'])])
        self.assertIn('is not what the first commit of the instance fixed: ' + difference, requests[0]['reason'])
        self.assertEqual(record['review_request'], str(sorted((self.instance / 'control/requests').glob('*.json'))[0]))
        # The library changes again and the difference is the same: it is recorded and not asked about twice.
        index = Canon(self.instance).load_index()
        write_json(Canon(self.instance).index, {**index, 'revision': index['revision'] + 1})
        engine = runtime.Runner(self.instance, self.skill)
        engine.check_root()
        self.assertEqual((engine.state['root_check']['revision'], engine.state['root_check']['status']),
                         (index['revision'] + 1, 'changed'))
        self.assertEqual(len(self.requests()), 1)

    def test_a_changed_file_of_a_definition_module_is_found_although_the_index_is_the_same(self):
        # The index says of a definition what Lean made of it when its module was last extracted. A source
        # edited behind the runner leaves the index as it was, and the comparison of the files finds it.
        self.formal()
        source = self.instance / 'canon/lean/Small/Defs.lean'
        source.write_text(source.read_text(encoding='utf-8') + '\n-- A line added by hand.\n', encoding='utf-8',
                          newline='\n')
        engine = runtime.Runner(self.instance, self.skill)
        engine.check_root()
        record = runtime.status(self.instance)['root_check']
        self.assertEqual((record['status'], record['differences']), ('changed', [FILE_CHANGED]))
        self.assertEqual([(r['kind'], r['elements']) for r in self.requests()], [('review', ['Small.root'])])

    def test_an_instance_created_by_the_earlier_code_is_compared_through_its_first_index(self):
        # The first commit of such an instance holds an index in the earlier form; what is compared is in both forms.
        self.formal()
        first = runtime.git(self.instance, 'rev-list', '--max-parents=0', 'HEAD').split()[0]
        index = read_json(Canon(self.instance).index)
        posed = earlier_form(json.loads(runtime.git(self.instance, 'show', first + ':canon/index.json')))
        self.assertEqual(statement_differences(posed, index, 'Small.root'), [])
        index['entries']['Small.oddSum']['source_sha'] = 'rewritten'
        self.assertEqual(statement_differences(posed, index, 'Small.root'), [DEFINITION_CHANGED])


class DefinitionModuleTests(InstanceCase):
    """The files of the modules that the root's module imported when the instance was created do not change
    (canon.check_definition_modules). The canon of these tests is the variant 'layered' of tests/support.py."""
    root_variant = 'layered'
    LOCKED = "the candidate changes the file of Small.Facts. The modules that the root's module imported when"

    def test_a_proof_that_would_change_a_definition_module_is_refused_when_prepared_and_again_at_publication(self):
        facts = self.instance / 'canon/lean/Small/Facts.lean'
        before = facts.read_bytes()
        folder = self.candidate(replace={'Small.factZero': theorem('factZero', SUM_ZERO, proof='rfl')}, prepare=False)
        receipt = self.prepare(folder, expect_ok=False)
        self.assertEqual(len(receipt['errors']), 1, receipt['errors'])
        self.assertIn(self.LOCKED, receipt['errors'][0])
        self.assertIsNone(receipt['build'])  # refused before anything is compiled
        # The runner makes the same check itself: with a receipt that claims success the candidate is still
        # refused, the module stays as it was, and a replacement peer receives the reason.
        write_json(folder / 'prepared.json', {**receipt, 'ok': True, 'errors': []})
        _, engine = self.publish(folder, expect=False)
        peers = [job for job in engine.state['jobs'].values() if job['role'] == 'peer' and job['status'] == 'pending']
        self.assertEqual(len(peers), 1)
        self.assertIn('could not be published on the current canon: ' + self.LOCKED, peers[0]['task']['previous_error'])
        self.assertEqual(facts.read_bytes(), before)
        # What the refusal names in its place: the same proof as a declaration of its own, in a new module.
        proved = module_text(theorem('factZeroProved', SUM_ZERO, proof='rfl'), imports=('Small.Facts',))
        folder = self.candidate(modules={'Small/FactProof.lean': proved},
                                records={'Small/factZeroProved.md': record_text('The empty sum is zero.',
                                                                                proves='Small.factZero')})
        self.assertEqual(read_json(folder / 'prepared.json')['added'], ['Small.factZeroProved'])

    def test_a_rearrangement_that_rewrites_or_deletes_a_definition_module_is_refused(self):
        facts = (self.instance / 'canon/lean/Small/Facts.lean').read_text(encoding='utf-8')
        for label, rewritten, delete in (('rewritten', facts.replace('  sorry', '  rfl'), []),
                                         ('deleted', None, ['Small.Facts'])):
            with self.subTest(label):
                folder = self.candidate(prepare=False)
                write_json(folder / 'organization.json', {'batch': [], 'merge_questions': [], 'delete': delete})
                if rewritten:
                    (folder / 'rewrite/lean/Small').mkdir(parents=True)
                    (folder / 'rewrite/lean/Small/Facts.lean').write_text(rewritten, encoding='utf-8', newline='\n')
                receipt = self.prepare(folder, role='organizer', expect_ok=False)
                self.assertEqual(len(receipt['errors']), 1, receipt['errors'])
                self.assertIn(self.LOCKED, receipt['errors'][0])
                self.assertIsNone(receipt['build'])

    def test_a_theorem_outside_the_definition_modules_is_proved_where_it_stands(self):
        # `Small.Side` is a module of the first commit that the root's module does not import, and the root's
        # own module is not locked either: its header takes the import that the proof of the root needs.
        self.assertEqual(definition_modules(self.instance), ['Small.Defs', 'Small.Facts'])
        root = theorem('root', ROOT_STATEMENTS['default'], uses=['sideOne'],
                       doc='The sum of the first `n` odd numbers is the square of `n`.')
        folder = self.candidate(
            replace={'Small.sideOne': theorem('sideOne', ': oddSum 1 = 1', proof='rfl'), 'Small.root': root},
            imports={'Small.root': ['Small.Side']},
            records={'Small/root.md': record_text('The sum of the first n odd numbers equals n times n.',
                                                  weight='unit', proof='From the sum of one term.')})
        # The proof of `sideOne` is complete in Lean and is left undetermined, so that no compile of the review is due.
        self.publish(folder, self.verdicts(folder, **{'Small.sideOne': {'correct': 'undetermined', 'accepted': False}}))
        lean = self.instance / 'canon/lean/Small'
        self.assertIn('  rfl', (lean / 'Side.lean').read_text(encoding='utf-8'))
        self.assertIn('public import Small.Side', (lean / 'Root.lean').read_text(encoding='utf-8'))
        # The definition modules are those of the first commit, whatever the root's module imports now.
        self.assertEqual(definition_modules(self.instance), ['Small.Defs', 'Small.Facts'])


# ------------------------------------------------------------------------------------------------ Lean itself

def lean_program():
    named = os.environ.get('DO_MATH_TEST_LEAN')
    if named:
        if not Path(named).is_file():
            # A skip would say that no compiler was found, of a run that was given one by name.
            raise FileNotFoundError(f'DO_MATH_TEST_LEAN names {named}, which is not a file')
        return Path(named)
    name = 'lean.exe' if os.name == 'nt' else 'lean'
    for folder in Path(__file__).resolve().parents:
        found = sorted((folder / '.skill-workspace/do-math-toolchains').glob('lean-4.36.0/*/bin/' + name))
        if found:
            return found[0]
    return None


LEAN = lean_program()
EXPECT_MB, PATIENCE = 2048, 1800
KINDS = '\n\n'.join([
    theorem('sumZero', SUM_ZERO),                                              # no proof
    # Proved by compiled evaluation. The statement names nothing of another module: in a `module` file the
    # compiled evaluation of a definition imported from one needs a `meta` import of it.
    theorem('computed', ': (2 : Nat) ^ 10 = 1024', proof='native_decide'),
    theorem('plain', ': oddSum 2 = 4', proof='rfl'),                           # proved, from no axiom
    theorem('byChoice', '(p : Prop) : p ∨ ¬p', proof='exact Classical.em p')])  # proved, from the allowed axioms
ABOVE_KINDS = '\n\n'.join([ABOVE, theorem('fromComputed', ': (2 : Nat) ^ 10 = 1024', uses=['computed'], proof='exact h1')])
KIND_RECORDS = {'Small/sumZero.md': ZERO_RECORD,
                'Small/computed.md': record_text('Two to the tenth power is 1024.'),
                'Small/plain.md': record_text('The first two odd numbers sum to four.'),
                'Small/byChoice.md': record_text('A proposition holds or fails.'),
                'Small/fromZero.md': ABOVE_RECORD,
                'Small/fromComputed.md': record_text('The same value, from the computation.')}


def lean_settings():
    """The settings of the test instances with Lean itself as the compiler, one compile at a time."""
    config = fixture_settings()
    config['lean'].update(command=[str(LEAN)], version_command=[str(LEAN), '--version'],
                          memory_budget_mb=8192, calibration_expect_mb=EXPECT_MB, threads=2, cpu_threads_budget=2)
    return config


@unittest.skipUnless(LEAN, 'Lean 4.36.0 was not found under .skill-workspace/do-math-toolchains; name it in DO_MATH_TEST_LEAN')
class LeanItselfTests(BothCompilers, ScenarioCase):
    """The same instance and the same paths as above, compiled by Lean 4.36.0."""
    root_variant = 'lean'  # the key of this compiler's instance among the instances kept for the test process
    expect_mb, patience = EXPECT_MB, PATIENCE

    def setUp(self):
        # The instance of this compiler states the root as the default instance does, under a key of its own.
        support.ROOTS.setdefault('lean', ROOT)
        support.ROOT_STATEMENTS.setdefault('lean', ROOT_STATEMENTS['default'])
        with patch.object(support, 'fixture_settings', lean_settings):
            super().setUp()

    def kinds(self):
        """Theorems proved in each way and left open, and a module above them that names two of them."""
        def build():
            folder = self.candidate(modules={'Small/Kinds.lean': module_text(KINDS),
                                             'Small/Above.lean': module_text(ABOVE_KINDS, imports=('Small.Defs', 'Small.Kinds'))},
                                    records=KIND_RECORDS)
            self.publish(folder)
        self.scenario('kinds', build)

    def test_lean_reports_sorry_and_native_decide_and_what_rests_on_them(self):
        self.kinds()
        self.assertIn('Lean (version 4.36.0', subprocess.run([str(LEAN), '--version'], capture_output=True, text=True).stdout)
        plain, choice = self.element('Small.plain'), self.element('Small.byChoice')
        self.assertEqual((plain['axioms'], plain['formal']), ([], True))
        self.assertTrue(choice['axioms'] and set(choice['axioms']) <= set(ALLOWED), choice['axioms'])
        self.assertTrue(choice['formal'])
        open_lemma, above = self.element('Small.sumZero'), self.element('Small.fromZero')
        self.assertEqual((open_lemma['lean_proof'], open_lemma['axioms'], open_lemma['formal']), ('sorry', ['sorryAx'], False))
        # The proof above is complete; Lean reports the `sorry` beneath it, in another module.
        self.assertEqual((above['lean_proof'], above['axioms'], above['formal']), ('complete', ['sorryAx'], False))
        computed, further = self.element('Small.computed'), self.element('Small.fromComputed')
        self.assertEqual((computed['lean_proof'], computed['formal'], len(computed['axioms'])), ('complete', False, 1))
        self.assertIn('Small.computed._native.native_decide', computed['axioms'][0])
        self.assertEqual((further['lean_proof'], further['formal'], further['axioms']), ('complete', False, computed['axioms']))
        # The axiom of the computation is no element; the index names it as one Lean generated.
        hidden = Canon(self.instance).load_index()['hidden'][computed['axioms'][0]]
        self.assertEqual((hidden['axiom'], hidden['generated']), (True, True))

    def test_a_theorem_in_a_module_that_did_not_change_is_compiled_again_and_becomes_formal(self):
        self.kinds()
        source = self.instance / 'canon/lean/Small/Above.lean'
        before = source.read_bytes()
        self.assertFalse(self.element('Small.fromZero')['formal'])
        builds = []

        def started(*arguments, **options):
            builds.append(start_build(*arguments, **options))
            return builds[-1]

        with patch.object(canon_tool, 'start_build', started):
            folder = self.candidate(replace={'Small.sumZero': ZERO}, records={'Small/sumZero.md': PROVED_ZERO_RECORD})
        self.assertEqual(read_json(folder / 'prepared.json')['changed_modules'], ['Small.Kinds'])
        # The build: the module whose proof changed is compiled, and so is the module above it, whose source
        # is the same, because the compiled output of what it imports changed. The definitions come from the cache.
        modules = job_record(Paths(self.instance), builds[0])['modules']
        self.assertEqual({name: modules[name]['status'] for name in ('Small.Defs', 'Small.Kinds', 'Small.Above')},
                         {'Small.Defs': 'cached', 'Small.Kinds': 'finished', 'Small.Above': 'finished'})
        self.publish(folder)
        self.assertEqual(source.read_bytes(), before)
        index = Canon(self.instance).load_index()
        self.assertEqual(index['modules']['Small.Above']['sha256'], hashlib.sha256(before).hexdigest())
        lemma, above = self.element('Small.sumZero'), self.element('Small.fromZero')
        self.assertEqual((lemma['lean_proof'], lemma['axioms'], lemma['formal']), ('complete', [], True))
        self.assertEqual((above['axioms'], above['formal'], above['settled']), ([], True, True))
        # What rests on the computation is as it was.
        self.assertFalse(self.element('Small.fromComputed')['formal'])

    def test_the_root_as_proved_is_the_root_as_posed(self):
        self.formal()
        root = self.element('Small.root')
        self.assertTrue(root['formal'] and set(root['axioms']) <= set(ALLOWED), root['axioms'])
        engine = runtime.Runner(self.instance, self.skill)
        self.assertEqual(engine.model['root_state'], 'formal_proved')
        engine.check_root()
        record = engine.state['root_check']
        self.assertEqual((record['proof'], record['status'], record['differences']), ('Small.root', 'unchanged', []))
        self.assertEqual(list((self.instance / 'control/requests').glob('*.json')), [])

    def test_a_changed_definition_under_the_root_is_found(self):
        self.formal()
        rewrite(self.instance / 'canon/lean/Small/Defs.lean', '| 0 => 0', '| 0 => 0 * 1')
        reindex(self)
        engine = runtime.Runner(self.instance, self.skill)
        self.assertEqual(engine.model['root_state'], 'formal_proved')  # the proof still compiles; the object is another
        engine.check_root()
        record = engine.state['root_check']
        self.assertEqual((record['status'], record['differences']), ('changed', [DEFINITION_CHANGED, FILE_CHANGED]))
        requests = [read_json(path) for path in (self.instance / 'control/requests').glob('*.json')]
        self.assertEqual([(r['kind'], r['elements']) for r in requests], [('review', ['Small.root'])])

    def test_a_changed_statement_of_the_root_is_found(self):
        first = runtime.git(self.instance, 'rev-list', '--max-parents=0', 'HEAD').split()[0]
        posed = json.loads(runtime.git(self.instance, 'show', first + ':canon/index.json'))
        self.assertEqual(statement_differences(posed, Canon(self.instance).load_index(), 'Small.root'), [])
        rewrite(self.instance / 'canon/lean/Small/Root.lean', 'oddSum n = n * n', 'oddSum n = n * n + 0')
        index = reindex(self)
        self.assertEqual(statement_differences(posed, index, 'Small.root'),
                         ['the statement of Small.root is not the statement the first commit has'])
        # A runner does not start on such a canon at all.
        with self.assertRaisesRegex(ValueError, 'root statement changed'):
            runtime.Runner(self.instance, self.skill)

    def test_lean_decides_a_claim_of_another_proof_or_a_refutation_and_keeps_what_an_open_proof_names(self):
        # The stand-in compiler decides both from the text: a pair by comparing two statements as they are
        # written, and what a proof names by the names that occur in it. Lean compares the terms of the two
        # statements and gives the constants of the proof term, where a `have` that the rest of an open proof
        # does not use still stands.
        statements = '\n\n'.join([theorem('rootAgain', ROOT_STATEMENTS['default']),
                                  theorem('notRoot', ': ¬ (∀ n : Nat, oddSum n = n * n)'),
                                  theorem('other', '(n : Nat) : oddSum n = n + n'),
                                  theorem('viaAgain', ': oddSum 1 = 1', uses=['rootAgain'])])
        records = {'Small/rootAgain.md': record_text('The root once more.', proves='Small.root'),
                   'Small/notRoot.md': record_text('The negation of the root.', refutes='Small.root'),
                   'Small/other.md': record_text('Not the root.', proves='Small.root'),
                   'Small/viaAgain.md': record_text('One odd number sums to one.')}
        # The module imports the root's module alone and reaches the definitions through it. Both of those modules
        # come from the cache, and the compile of this module is the first of the build, so their files are in the
        # build's lib only because the broker put them there for this compile (lean_broker.Broker.advance_build).
        # The stand-in compilers look for the files of the modules a source imports itself and not for those
        # behind them, so it is here that Lean is seen to find a module it reads through another.
        folder = self.candidate(modules={'Small/Pairs.lean': module_text(statements, imports=('Small.Root',))},
                                records=records, prepare=False)
        builds = []

        def started(*arguments, **options):
            builds.append(start_build(*arguments, **options))
            return builds[-1]

        with patch.object(canon_tool, 'start_build', started):
            result = self.prepare(folder, expect_ok=False)
        modules = job_record(Paths(self.instance), builds[0])['modules']
        self.assertEqual({name: modules[name]['status'] for name in ('Small.Defs', 'Small.Root', 'Small.Pairs')},
                         {'Small.Defs': 'cached', 'Small.Root': 'cached', 'Small.Pairs': 'finished'})
        # The two claims that hold are confirmed, and the one that does not is the only thing refused.
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertIn('Small.other: Lean did not confirm that its statement is the statement of Small.root',
                      result['errors'][0])
        self.assertIn('Small.rootAgain', result['entries']['Small.viaAgain']['uses'])


if __name__ == '__main__':
    unittest.main()
