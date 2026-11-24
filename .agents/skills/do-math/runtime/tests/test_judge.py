"""The judge of formal proofs: which theorems it is given, the job that runs it, and what each verdict does.

do-math takes a statement for formal from its own index. The judge has the same theorems exported with
everything they rest on and checked by a program that reads the export alone (judge.py). Here the
exporter and the comparator are the stand-ins of tests/canon_lean.py, started by the stand-in of the
Lean file that starts them, so the tests follow the real path from the runner to the two commands and
back. A module with a line `-- judge rejects: <message>` is one the stand-in comparator rejects; with it
a test has the judge disagree with the index. What the real exporter and comparator do is not shown here.
"""
import base64
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import judge
import runner as runtime
from canon import Canon
from canon_tool import view
from knowledge import replay
from runtime_support import read_json, write_json
from support import HERE, InstanceCase, ScenarioCase, SUM_ZERO, module_text, record_text, test_settings, theorem, write_canon

STAND_IN = [sys.executable, '-B', str(HERE / 'canon_lean.py')]
JUDGE = {'export': STAND_IN + ['export'], 'compare': STAND_IN + ['compare']}
ALLOWED = ['propext', 'Classical.choice', 'Quot.sound']
ZERO = theorem('sumZero', SUM_ZERO, proof='rfl')
ZERO_RECORD = record_text('The empty sum is zero.', weight='unit')


def entry(name, uses=(), axioms=(), kind='theorem', module='S.M'):
    return {'name': name, 'kind': kind, 'module': module, 'uses': list(uses), 'statement_uses': [],
            'direct_axioms': list(axioms)}


def index_of(*entries, judged=None):
    return {'entries': {e['name']: e for e in entries}, 'judged': judged or {}}


class CommandTests(unittest.TestCase):
    def test_the_tools_are_looked_for_beside_the_lean_command(self):
        with tempfile.TemporaryDirectory() as folder:
            suffix = '.exe' if os.name == 'nt' else ''
            for name in ('lean', 'leanexport', 'lake'):
                Path(folder, name + suffix).write_text('', encoding='utf-8')
            lean = {'command': [str(Path(folder, 'lean' + suffix))], 'judge': 'auto'}
            with patch.object(judge, 'program_folders', return_value=(['/programs', '/git'], [])):
                commands, why = judge.judge_commands(lean)
            self.assertIsNone(why)
            self.assertEqual(commands['export'], [Path(folder, 'leanexport' + suffix).as_posix()])
            self.assertEqual(commands['compare'][:2], [Path(folder, 'lake' + suffix).as_posix(), 'comparator'])
            if os.name == 'nt':
                # The comparator's sandbox needs Linux namespaces, so it is switched off where it cannot run.
                self.assertEqual(commands['compare'][2:], ['--inadvisably-no-sandbox'])
            # The folders of the programs the comparator looks up go with the commands.
            self.assertEqual(commands['path'], ['/programs', '/git'])
            # A program that is not found leaves a judge that is asked for and cannot run. That is an error
            # which names the program, and not the absence of a judge.
            with patch.object(judge, 'program_folders', return_value=(['/git'], ['which', 'env'])):
                with self.assertRaisesRegex(ValueError, 'cannot run on this machine.*not found: which, env.*lean.judge to null'):
                    judge.judge_commands(lean)
            # An installation without the exporter, as Lean before 4.35 is, has no judge, and says why.
            Path(folder, 'leanexport' + suffix).unlink()
            with patch.object(judge, 'program_folders', return_value=([], ['which'])):
                commands, why = judge.judge_commands(lean)
            self.assertIsNone(commands)
            self.assertIn('leanexport', why)

    def test_the_programs_the_comparator_looks_up_are_found_on_path_and_where_git_for_windows_has_them(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder).resolve()
            if os.name == 'nt':
                # Git for Windows: `git` is on PATH from <Git>\cmd, `which` and `env` stand in <Git>\usr\bin, which
                # is on PATH only in Git's own shell. A `which.cmd`, as a Node package installs one, is not a
                # program the comparator can start by the bare name.
                on_path, programs = [base / 'Git/cmd', base / 'npm'], base / 'Git/usr/bin'
                files = [base / 'Git/cmd/git.exe', programs / 'which.exe', programs / 'env.exe', base / 'npm/which.cmd']
                expected = [str(programs), str(base / 'Git/cmd')]
            else:
                on_path, programs = [base / 'bin'], base / 'bin'
                files = [programs / 'git', programs / 'which', programs / 'env']
                expected = [str(programs)]
            for file in files:
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('', encoding='utf-8')
                file.chmod(0o755)
            with patch.dict(os.environ, {'PATH': os.pathsep.join(str(p) for p in on_path)}):
                self.assertEqual(judge.program_folders(), (expected, []))
                (programs / ('env.exe' if os.name == 'nt' else 'env')).unlink()
                self.assertEqual(judge.program_folders()[1], ['env'])
            with patch.dict(os.environ, {'PATH': str(base / 'nothing')}):
                self.assertEqual(judge.program_folders(), ([], ['which', 'git', 'env']))

    def test_the_settings_can_name_the_commands_or_switch_the_judge_off(self):
        lean = {'command': ['lean'], 'judge': JUDGE}
        self.assertEqual(judge.judge_commands(lean), (JUDGE, None))
        commands, why = judge.judge_commands({'command': ['lean'], 'judge': None})
        self.assertIsNone(commands)
        self.assertIn('null', why)
        config = test_settings()
        for value in ('auto', None, JUDGE):
            config['lean']['judge'] = value
            runtime.validate(config)
        for value in ('yes', {'export': ['x']}, {'export': [], 'compare': ['y']}):
            config['lean']['judge'] = value
            with self.assertRaisesRegex(ValueError, 'lean.judge'):
                runtime.validate(config)


class TargetTests(unittest.TestCase):
    def test_a_publication_has_judged_what_it_proved_and_what_became_formal_through_it(self):
        old = index_of(entry('S.lemma', axioms=['sorryAx']), entry('S.above', uses=['S.lemma']),
                       entry('S.settled', axioms=['propext']), entry('S.replaced'), entry('S.open', axioms=['sorryAx']),
                       entry('S.object', kind='def'))
        new = index_of(entry('S.lemma'), entry('S.above', uses=['S.lemma']), entry('S.settled', axioms=['propext']),
                       entry('S.replaced', axioms=['Quot.sound']), entry('S.open', axioms=['sorryAx']),
                       entry('S.object', kind='def'), entry('S.added'), entry('S.foreign', axioms=['S.assumed']))
        touched = {'S.lemma', 'S.replaced', 'S.open', 'S.added', 'S.foreign'}
        # `above` was not touched: it is formal only now that the lemma it names has a formal proof.
        # `settled` was formal and is as it was. `open` and `foreign` are touched and not formal.
        self.assertEqual(judge.publication_targets(old, new, touched, ALLOWED),
                         ['S.above', 'S.added', 'S.lemma', 'S.replaced'])
        self.assertEqual(judge.formal_names(new, ALLOWED), ['S.above', 'S.added', 'S.lemma', 'S.replaced', 'S.settled'])

    def test_an_earlier_judgment_holds_for_a_theorem_the_change_left_as_it_was(self):
        index = index_of(entry('S.kept'), entry('S.replaced'), judged={'S.kept': 3, 'S.replaced': 4, 'S.gone': 2})
        self.assertEqual(judge.carried(index, {'S.replaced'}), {'S.kept': 3})

    def test_the_names_of_one_export_fit_a_command_line(self):
        names = [f'S.theorem_with_a_long_name_{number:04d}' for number in range(2000)]
        module_of = {name: f'S.Part{number % 7}' for number, name in enumerate(names)}
        groups = list(judge.batches(names, module_of, ALLOWED))
        self.assertGreater(len(groups), 1)
        self.assertEqual([name for _, group in groups for name in group], names)
        for modules, group in groups:
            self.assertEqual(modules, sorted({module_of[name] for name in group}))
            arguments = [*modules, '--', *judge.export_targets(group, ALLOWED)]
            self.assertLess(sum(len(a) + 1 for a in arguments), judge.ARGUMENT_BUDGET + 200)
        # The export names what the comparator asks of every export beside the theorems themselves.
        targets = judge.export_targets(['S.a'], ALLOWED)
        self.assertEqual(targets[:5], ['Quot', 'Quot.mk', 'Quot.lift', 'Quot.ind', 'S.a'])
        self.assertTrue({'propext', 'Nat.add', 'semiOutParam'} <= set(targets))
        self.assertNotIn('Quot', judge.export_targets(['S.a'], ['propext']))

    def test_a_theorem_that_another_named_theorem_uses_is_judged_in_that_export(self):
        # root uses mid through a definition; mid uses leaf; side is used by nothing; lone uses an entry
        # that is not named. The export of root carries mid and leaf, so only root, side and lone are named.
        index = index_of(entry('S.leaf'), entry('S.mid', uses=['S.leaf']), entry('S.d', uses=['S.mid'], kind='def'),
                         entry('S.root', uses=['S.d']), entry('S.side'), entry('S.open'),
                         entry('S.lone', uses=['S.open']))
        index['entries']['S.root']['statement_uses'] = ['S.d']
        names = ['S.leaf', 'S.lone', 'S.mid', 'S.root', 'S.side']
        self.assertEqual(judge.covering(index, names), ['S.lone', 'S.root', 'S.side'])
        # A theorem keeps its place when the theorem that uses it is not among the names.
        self.assertEqual(judge.covering(index, ['S.leaf', 'S.mid', 'S.side']), ['S.mid', 'S.side'])
        self.assertEqual(judge.covering(index, ['S.leaf']), ['S.leaf'])
        # Entries that use one another are each reached by the other; one of them stays, and what it
        # reaches below the circle is still left out.
        circle = index_of(entry('S.a', uses=['S.b']), entry('S.b', uses=['S.a', 'S.c']), entry('S.c'))
        self.assertEqual(judge.covering(circle, ['S.a', 'S.b', 'S.c']), ['S.a'])
        self.assertEqual(judge.covering(circle, ['S.c', 'S.b', 'S.a']), ['S.b'])
        # Every name is kept or is reached from a kept one.
        for chosen in (names, ['S.mid', 'S.side', 'S.leaf']):
            kept, entries = judge.covering(index, chosen), index['entries']
            reach, todo = set(kept), list(kept)
            while todo:
                item = entries[todo.pop()]
                for used in item['uses'] + item['statement_uses']:
                    if used not in reach:
                        reach.add(used)
                        todo.append(used)
            self.assertTrue(set(chosen) <= reach)

    def test_the_file_that_starts_the_tools_carries_its_plan_and_quotes_what_it_passes(self):
        plan = {'cases': [{'names': ['S.a'], 'exports': [
            {'command': ['C:/tools/lean export.exe'], 'args': ['S.M', '--', 'S.a'], 'lib': 'C:\\build "x"\\lib', 'file': 'e.ndjson'}],
            'compare': {'command': ['lake', 'comparator'], 'args': ['--config', 'c.json'], 'log': 'c.log'}}]}
        source = judge.launcher_source(plan)
        line = next(line for line in source.splitlines() if line.startswith(judge.PLAN_MARK))
        self.assertEqual(json.loads(base64.b64decode(line[len(judge.PLAN_MARK):])), plan)
        self.assertIn('DoMathJudge.exportTo "C:/tools/lean export.exe" #["S.M", "--", "S.a"] "C:\\\\build \\"x\\"\\\\lib" "e.ndjson"', source)
        self.assertIn('IO.println s!"@@judge 0 export 0 {e0x0}"', source)
        self.assertIn('if e0x0 == 0 then', source)
        self.assertIn('DoMathJudge.compare "lake" #["comparator", "--config", "c.json"] #[] "c.log"', source)
        self.assertIn('IO.println "@@judge done"', source)
        self.assertNotIn('import ', source)
        # The folders of the programs the comparator looks up are handed to the function that starts it,
        # which puts them first on the comparator's PATH.
        plan['cases'][0]['compare']['path'] = ['C:\\Git\\usr\\bin', 'C:\\Git\\cmd']
        source = judge.launcher_source(plan)
        self.assertIn('DoMathJudge.compare "lake" #["comparator", "--config", "c.json"] '
                      '#["C:\\\\Git\\\\usr\\\\bin", "C:\\\\Git\\\\cmd"] "c.log"', source)
        self.assertIn('env := #[("PATH", some path)]', source)

    def test_the_theorem_that_carries_the_root_to_the_judge(self):
        self.assertEqual(judge.wrapper('Small.root', 'Small.Root', 'proved'),
                         'import Small.Root\n\ntheorem DoMathJudgeRoot.statement : type_of% @Small.root := @Small.root\n')
        self.assertEqual(judge.wrapper('Small.root', 'Small.Root', 'proved', 'Small.other', 'Small.Other'),
                         'import Small.Root\nimport Small.Other\n\n'
                         'theorem DoMathJudgeRoot.statement : type_of% @Small.root := @Small.other\n')
        self.assertEqual(judge.wrapper('Small.root', 'Small.Root', 'refuted'),
                         'import Small.Root\n\ntheorem DoMathJudgeRoot.statement : ¬ (type_of% @Small.root) := sorry\n')
        self.assertEqual(judge.wrapper('Small.root', 'Small.Root', 'refuted', 'Small.no', 'Small.Root'),
                         'import Small.Root\n\ntheorem DoMathJudgeRoot.statement : ¬ (type_of% @Small.root) := @Small.no\n')


class PublicationTests(InstanceCase):
    def setUp(self):
        super().setUp()
        self.configure(lean={'judge': JUDGE})

    def judged(self):
        return Canon(self.instance).load_index().get('judged', {})

    def zero(self, body=ZERO, **options):
        return self.candidate(modules={'Small/Zero.lean': module_text(body)}, records={'Small/sumZero.md': ZERO_RECORD},
                              **options)

    def test_a_formal_proof_is_judged_before_it_is_published(self):
        record, engine = self.publish(self.zero())
        sequence = read_json(self.instance / 'knowledge/events' / (record + '.json'))['sequence']
        self.assertEqual(self.judged(), {'Small.sumZero': sequence})
        self.assertEqual(read_json(self.instance / 'knowledge/changes' / record / 'provenance.json')['judged'], ['Small.sumZero'])
        self.assertIn(f'judged        at revision {sequence}', view(self.instance, replay(self.instance), 'Small.sumZero'))
        # The root has no formal proof, so the judge was not asked about it.
        self.assertNotIn('judged', view(self.instance, replay(self.instance), 'Small.root'))
        status = runtime.status(self.instance)['judge']
        self.assertEqual((status['available'], status['commands']), (True, JUDGE))

    def test_a_theorem_is_judged_when_the_last_statement_it_rests_on_becomes_formal(self):
        above = theorem('fromZero', SUM_ZERO, uses=['sumZero'], proof='exact h1')
        folder = self.candidate(modules={'Small/Zero.lean': module_text(theorem('sumZero', SUM_ZERO)),
                                         'Small/Above.lean': module_text(above, imports=('Small.Defs', 'Small.Zero'))},
                                records={'Small/sumZero.md': ZERO_RECORD,
                                         'Small/fromZero.md': record_text('The same value, from the lemma.')})
        _, engine = self.publish(folder)
        # `fromZero` is complete in Lean and rests on a statement without a proof, so nothing is formal yet.
        self.assertEqual(self.judged(), {})
        second = self.candidate(replace={'Small.sumZero': ZERO},
                                records={'Small/sumZero.md': record_text('The empty sum is zero.', weight='unit',
                                                                         proof='By the definition.')})
        record, _ = self.publish(second, engine=engine)
        sequence = read_json(self.instance / 'knowledge/events' / (record + '.json'))['sequence']
        self.assertEqual(self.judged(), {'Small.sumZero': sequence, 'Small.fromZero': sequence})

    def test_a_proof_the_judge_rejects_is_not_published_and_goes_to_a_replacement_peer(self):
        before = Canon(self.instance).load_index()
        folder = self.zero('-- judge rejects: the kernel does not accept sumZero\n' + ZERO)
        record, engine = self.publish(folder, expect=False)
        self.assertIsNone(record)
        self.assertEqual(Canon(self.instance).load_index(), before)
        peers = [j for j in engine.state['jobs'].values() if j['role'] == 'peer' and j['status'] == 'pending']
        self.assertEqual(len(peers), 1)
        self.assertIn('the judge does not accept the formal proofs of this change', peers[0]['task']['previous_error'])
        self.assertIn('the kernel does not accept sumZero', peers[0]['task']['previous_error'])

    def test_a_judge_that_cannot_run_stops_the_runner_and_blames_no_candidate(self):
        # The comparator ends with its code for "could not start". That says nothing about the candidate.
        self.configure(lean={'judge': {**JUDGE, 'compare': [sys.executable, '-c', 'import sys; sys.exit(2)']}})
        before = Canon(self.instance).load_index()
        folder = self.zero()
        with self.assertRaisesRegex(RuntimeError, 'the judge of formal proofs could not run'):
            self.publish(folder)
        engine = runtime.Runner(self.instance, self.skill)
        # The build was made once more before the runner gave up, and the publication waits where it stood.
        self.assertEqual((engine.state['publication']['stage'], engine.state['publication']['judge']['attempts']), ('judge', 1))
        self.assertEqual(Canon(self.instance).load_index(), before)
        self.assertEqual([j for j in engine.state['jobs'].values() if j['role'] == 'peer' and j['status'] == 'pending'], [])
        # With the judge repaired, the same publication goes through.
        self.configure(lean={'judge': JUDGE})
        engine = runtime.Runner(self.instance, self.skill)
        self.drain(engine)
        self.assertEqual(list(self.judged()), ['Small.sumZero'])

    def test_the_comparator_is_started_with_the_folders_of_its_programs_first_on_its_path(self):
        # The comparator here prints the PATH it was started with and ends with its code for "could not start",
        # so that the reason the runner stops with shows what the comparator received.
        programs = str(self.root / 'programs')
        show = [sys.executable, '-c', 'import os, sys; print("PATH=" + os.environ["PATH"]); sys.exit(2)']
        commands = {**JUDGE, 'compare': show, 'path': [programs]}
        with patch.object(runtime, 'judge_commands', return_value=(commands, None)):
            with self.assertRaises(RuntimeError) as stopped:
                self.publish(self.zero())
        self.assertIn('PATH=' + programs + os.pathsep, str(stopped.exception))

    def test_a_judge_that_is_asked_for_and_cannot_run_here_is_refused_at_start_and_named_by_the_status(self):
        why = 'the judge of formal proofs cannot run on this machine: these were not found: which, env'
        with patch.object(runtime, 'judge_commands', side_effect=ValueError(why)):
            with patch.object(runtime.subprocess, 'Popen') as launched:
                with self.assertRaisesRegex(ValueError, 'not found: which, env'):
                    runtime.start(self.instance)
            launched.assert_not_called()
            status = runtime.status(self.instance)['judge']
        self.assertEqual((status['available'], status['commands'], status['reason']), (False, None, why))

    def test_an_exporter_that_fails_is_not_a_rejection_either(self):
        self.configure(lean={'judge': {**JUDGE, 'export': [sys.executable, '-c', 'import sys; sys.exit(1)']}})
        with self.assertRaisesRegex(RuntimeError, 'the exporter ended with code 1'):
            self.publish(self.zero())

    def test_without_a_judge_nothing_is_judged_and_the_status_says_why(self):
        self.configure(lean={'judge': 'auto'})  # the stand-in compiler has no exporter beside it
        self.publish(self.zero())
        self.assertEqual(self.judged(), {})
        status = runtime.status(self.instance)['judge']
        self.assertEqual(status['available'], False)
        self.assertIn('leanexport', status['reason'])


class InitTests(unittest.TestCase):
    def create(self, zero, **lean):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        (base / 'goal.md').write_text('For every natural number n, the sum of the first n odd numbers is n * n.', encoding='utf-8')
        config = test_settings()
        config['lean'].update(lean)
        write_json(base / 'settings.json', config)
        write_canon(base / 'canon')
        (base / 'canon/lean/Small/Zero.lean').write_text(module_text(zero), encoding='utf-8', newline='\n')
        (base / 'canon/records/Small/sumZero.md').write_text(ZERO_RECORD, encoding='utf-8', newline='\n')
        runtime.initialize(base / 'instance', base / 'goal.md', base / 'canon', 'Small.root', base / 'settings.json')
        return base / 'instance'

    def test_the_formal_theorems_of_the_first_canon_are_judged(self):
        instance = self.create(ZERO, judge=JUDGE)
        self.assertEqual(Canon(instance).load_index()['judged'], {'Small.sumZero': 0})
        self.assertFalse((instance / 'runner/stage-genesis').exists())

    def test_a_first_canon_the_judge_rejects_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'the judge does not accept a proof of the canon: .*not accepted here'):
            self.create('-- judge rejects: not accepted here\n' + ZERO, judge=JUDGE)

    def test_a_judge_that_cannot_run_refuses_the_instance_and_names_the_way_without_it(self):
        broken = {**JUDGE, 'compare': [sys.executable, '-c', 'import sys; sys.exit(2)']}
        with self.assertRaisesRegex(ValueError, 'could not run.*set lean.judge to null'):
            self.create(ZERO, judge=broken)
        # A judge whose programs are not found on this machine is refused before anything is created.
        with patch.object(runtime, 'judge_commands', side_effect=ValueError('these were not found: which')):
            with self.assertRaisesRegex(ValueError, 'not found: which'):
                self.create(ZERO, judge='auto')
        self.assertFalse((Path(self.temp.name) / 'instance').exists())
        self.assertEqual(Canon(self.create(ZERO, judge=None)).load_index()['judged'], {})


class RootTests(ScenarioCase):
    def setUp(self):
        super().setUp()
        self.out = self.root / 'verdict'

    def judge_root(self, **options):
        with patch('builtins.print'):
            return judge.judge_root(self.instance, self.out, paranoid=False, **options)

    def requests(self):
        return [read_json(path) for path in sorted((self.instance / 'control/requests').glob('*.json'))]

    def test_the_root_as_proved_is_the_root_as_posed(self):
        self.formal()
        self.configure(lean={'judge': JUDGE})
        self.assertEqual(self.judge_root(), 0)
        verdict = read_json(self.out / 'verdict.json')
        first = runtime.git(self.instance, 'rev-list', '--max-parents=0', 'HEAD').split()[0]
        self.assertEqual((verdict['verdict'], verdict['root'], verdict['proof'], verdict['compared_with_commit']),
                         ('accepted', 'Small.root', 'Small.root', first))
        # The challenge is the canon of the first commit, where the root had no proof.
        self.assertIn('sorry', (self.out / 'challenge/Small/Root.lean').read_text(encoding='utf-8'))
        self.assertNotIn('sorry', (self.out / 'solution/Small/Root.lean').read_text(encoding='utf-8'))
        self.assertEqual(self.requests(), [])

    def test_a_definition_that_changed_since_the_first_commit_is_rejected_and_sent_to_review(self):
        self.formal()
        self.configure(lean={'judge': JUDGE})
        defs = self.instance / 'canon/lean/Small/Defs.lean'
        defs.write_text(defs.read_text(encoding='utf-8').replace('| 0 => 0', '| 0 => 0 * 1'), encoding='utf-8', newline='\n')
        self.assertEqual(self.judge_root(), 2)
        verdict = read_json(self.out / 'verdict.json')
        self.assertEqual(verdict['verdict'], 'rejected')
        self.assertIn("Const does not match between challenge and target 'Small.oddSum'", verdict['reason'])
        request = self.requests()[0]
        self.assertEqual((request['kind'], request['elements']), ('review', ['Small.root']))
        self.assertIn('The judge rejected the formal settlement of the root', request['reason'])
        # Without the request, the verdict alone is left.
        shutil.rmtree(self.out)
        for path in (self.instance / 'control/requests').glob('*.json'):
            path.unlink()
        self.assertEqual(self.judge_root(review=False), 2)
        self.assertEqual(self.requests(), [])

    def test_the_runner_has_a_settled_root_judged_once_for_its_proof_and_again_at_the_end_for_a_changed_library(self):
        self.configure(lean={'judge': JUDGE})
        engine = runtime.Runner(self.instance, self.skill)
        # A root without a formal settlement is not judged.
        self.assertIsNone(engine.root_judge_due())
        self.formal()
        self.configure(lean={'judge': JUDGE})
        engine = runtime.Runner(self.instance, self.skill)
        self.assertEqual(engine.root_judge_due(), 'Small.root')
        # While a publication is underway the canon is about to change, and the judge is not started on it.
        engine.state['publish_queue'].append({'kind': 'questions'})
        self.assertIsNone(engine.root_judge_due())
        engine.state['publish_queue'].clear()
        # A judging that has ended leaves its verdict in the state; a process that is gone left none to wait for.
        folder = 'runner/root-judge-test'
        engine.state['root_judge'] = {'proof': 'Small.root', 'revision': engine.model['revision'], 'folder': folder,
                                      'process': None, 'status': 'running', 'started_at': 0}
        self.assertIsNone(engine.root_judge_due())
        (self.instance / folder).mkdir(parents=True)
        write_json(self.instance / folder / 'verdict.json', {'verdict': 'rejected', 'reason': 'Const does not match.'})
        engine.collect_root_judge()
        record = engine.state['root_judge']
        self.assertEqual((record['status'], record['reason']), ('rejected', 'Const does not match.'))
        self.assertEqual(runtime.status(self.instance)['root_judge']['status'], 'rejected')
        # The same proof on the same library is not judged again, at the end either: a verdict is not asked for twice.
        self.assertIsNone(engine.root_judge_due())
        self.assertIsNone(engine.root_judge_due(final=True))
        # A library that changed since is judged once more before the runner finishes, and a new proof at once.
        record['revision'] -= 1
        self.assertIsNone(engine.root_judge_due())
        self.assertEqual(engine.root_judge_due(final=True), 'Small.root')
        record.update(revision=engine.model['revision'], proof='Small.other')
        self.assertEqual(engine.root_judge_due(), 'Small.root')
        # A command that left no verdict is recorded as one that could not answer.
        engine.state['root_judge'] = {'proof': 'Small.root', 'revision': engine.model['revision'],
                                      'folder': 'runner/root-judge-none', 'process': None, 'status': 'running',
                                      'started_at': 0}
        engine.collect_root_judge()
        self.assertEqual(engine.state['root_judge']['status'], 'unavailable')
        # Without a judge nothing is started.
        self.configure(lean={'judge': None})
        engine = runtime.Runner(self.instance, self.skill)
        self.assertIsNone(engine.root_judge_due())

    def test_a_root_without_a_formal_settlement_and_an_instance_without_a_judge_are_refused(self):
        self.configure(lean={'judge': JUDGE})
        with self.assertRaisesRegex(judge.Stop, 'the root is unresolved'):
            self.judge_root()
        self.formal()
        self.configure(lean={'judge': None})
        with self.assertRaisesRegex(judge.Stop, 'no judge is available'):
            self.judge_root()
        with patch('builtins.print'), patch('sys.stderr'):
            self.assertEqual(judge.main([str(self.instance), '--out', str(self.out)]), 1)


if __name__ == '__main__':
    unittest.main()
