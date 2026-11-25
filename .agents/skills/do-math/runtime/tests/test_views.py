"""The derived views of the research and the text views a session reads the canon through."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_tool
import knowledge
from canon import Canon
from coordination import board, lease, lease_table, wait
from runner import Runner, main
from runtime_support import InstanceLock, read_json, write_json
from support import GAP_REASON, HELD_REASON, SUM_ZERO, ScenarioCase, module_text, record_text, take, theorem

FRONTIER = '''\
- `Small.root` — odd numbers sum to a square — accepted
  - `Small.colA` — Col — correct, held back: The two cases can be merged into one.
    - `Small.leafH` — The first odd number is one. — no proof
  - `Small.monoB` — Mono — no proof · 1 approach tried
    - other proof: `Small.monoBAlt` — Mono from the first odd number. — proof not confirmed: The addition is not carried out.
      - `Small.leafH` — The first odd number is one. — shown above
  - other proof: `Small.rootAlt` — The root by way 2, from Col and Diag. — correct, held back: Way 2 repeats the case split of way 1.
    - `Small.colA` — Col — shown above
    - `Small.diagD` — Diag — proof not confirmed: The induction step is not justified.
      - `Small.stepF` (step) — The first five odd numbers sum to twenty-five. — no proof
'''


def finding(reason, status='confirmed', concerns=(), **changes):
    return {'concerns': list(concerns), 'status': status, 'reason': reason, **changes}


def comprehensive(findings=(), concerns=()):
    return {'feedback': 'feedback.md', 'findings': list(findings), 'concerns': list(concerns)}


class ViewTests(ScenarioCase):
    """knowledge.render: frontier.md, index.md, board.md and state.json."""

    def view(self, name):
        return (self.instance / 'knowledge' / name).read_text(encoding='utf-8')

    def test_identical_render_does_not_replace_files(self):
        self.ways()
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        with patch('knowledge.write_text') as text, patch('knowledge.write_json') as data:
            knowledge.render(self.instance, model, [])
        text.assert_not_called()
        data.assert_not_called()

    def test_a_board_change_writes_the_board_and_the_frontier_only_where_it_shows_the_holders(self):
        self.ways()
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        row = {'pipeline': 'p1', 'session': 's1', 'role': 'attempt', 'stage': 'producing', 'elements': [],
               'sections': [], 'question': None}
        with patch('knowledge.write_text', wraps=knowledge.write_text) as text, \
                patch('knowledge.write_json') as data:
            knowledge.render(self.instance, model, [row])
        self.assertEqual([call.args[0].name for call in text.call_args_list], ['board.md'])
        data.assert_not_called()
        self.assertIn('not process liveness', self.view('board.md'))
        self.assertIn('- p1 · producer: s1 · attempt · producing · elements: (choosing)', self.view('board.md'))
        # The frontier counts the sessions that hold each element, so it follows a change of what is held.
        section = {'id': 's1-1', 'element': 'Small.colA', 'session': 's1', 'whole': True, 'statement': None, 'new': None}
        with patch('knowledge.write_text', wraps=knowledge.write_text) as text, \
                patch('knowledge.write_json') as data:
            knowledge.render(self.instance, model, [{**row, 'elements': ['Small.colA'], 'sections': [section]}])
        self.assertEqual([call.args[0].name for call in text.call_args_list], ['frontier.md', 'board.md'])
        data.assert_not_called()
        self.assertIn('  - `Small.colA` — Col — correct, held back: The two cases can be merged into one. · held by 1 session\n',
                      self.view('frontier.md'))

    def test_unreadable_existing_view_is_not_treated_as_missing(self):
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        original = Path.read_bytes

        def unreadable(path):
            if path.name == 'frontier.md':
                raise PermissionError('view locked')
            return original(path)

        with patch.object(Path, 'read_bytes', unreadable), patch('knowledge.write_text') as text:
            with self.assertRaisesRegex(PermissionError, 'view locked'):
                knowledge.render(self.instance, model, [])
        text.assert_not_called()

    def test_changed_research_updates_every_view_and_the_saved_state(self):
        self.split()
        before = knowledge.replay(self.instance)
        knowledge.render(self.instance, before, [])
        self.assertEqual(read_json(self.instance / 'knowledge/state.json'), before)
        self.replace_proof('Small.sumZero', theorem('sumZero', SUM_ZERO), 'A sum without terms is zero.',
                           description='The empty sum is zero.')
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        self.assertEqual(model['sequence'], before['sequence'] + 1)
        # state.json is the derived model itself, for whoever reads the research by machine.
        saved = read_json(self.instance / 'knowledge/state.json')
        self.assertEqual(saved, model)
        self.assertEqual((saved['root_state'], saved['remaining'], saved['elements']['Small.sumZero']['standing']),
                         ('unresolved', ['Small.sumSucc'], 'accepted'))
        self.assertIn(f"Revision: {model['sequence']} · Root: `Small.root` · State: unresolved\n", self.view('frontier.md'))
        self.assertIn(f"Revision: {model['sequence']}\n", self.view('index.md'))
        self.assertIn(f"Research revision: {model['sequence']}\n", self.view('board.md'))
        self.assertNotIn('Small.sumZero', self.view('frontier.md'))
        self.assertIn('- `Small.sumZero` · unit · accepted — The empty sum is zero.', self.view('index.md'))

    def test_the_frontier_view_shows_every_way_with_standings_reasons_approaches_and_holders(self):
        self.ways()
        view = self.view('frontier.md')
        self.assertTrue(view.startswith('# Frontier\n\nRevision: 2 · Root: `Small.root` · State: unresolved\n'))
        self.assertIn('A statement that is settled is not opened.', view)
        self.assertEqual(view.split('\n\n')[3] + '\n', FRONTIER)
        self.assertEqual(knowledge.frontier_lines(knowledge.replay(self.instance)), FRONTIER.splitlines())
        # Nothing the frontier passes over is listed: the settled unit, the accepted step, the unused statement.
        for name in ('unitG', 'stepE', 'strayS'):
            self.assertNotIn(name, view)
        # Who holds what stands beside the element, wherever it is shown.
        runner = Runner(self.instance, self.skill)
        a, b, c = (self.session(runner, sid) for sid in ('sa', 'sb', 'sc'))
        first = take(a, 'Small.colA', 'The first of the two cases.')['section']
        self.assertTrue(take(b, 'Small.colA', 'The second of the two cases.', {first['id']: 'The other case.'})['registered'])
        self.assertTrue(take(c, 'Small.monoB')['registered'])
        knowledge.render(self.instance, runner.model, board(self.instance))
        lines = self.view('frontier.md').splitlines()
        self.assertIn('  - `Small.colA` — Col — correct, held back: The two cases can be merged into one. · held by 2 sessions', lines)
        self.assertIn('    - `Small.colA` — Col — shown above · held by 2 sessions', lines)
        self.assertIn('  - `Small.monoB` — Mono — no proof · 1 approach tried · held by 1 session', lines)
        self.assertIn('    - `Small.leafH` — The first odd number is one. — no proof', lines)

    def test_the_frontier_view_names_concerns_with_the_review_that_examines_them(self):
        self.ways()
        self.event('v1', 'review', comprehensive(concerns=[
            {'id': 'gap', 'targets': ['Small.colA', 'Small.unitG'], 'reason': 'A boundary case needs checking.',
             'evidence': 'The case n = 0.'}]))
        runner = Runner(self.instance, self.skill)
        knowledge.render(self.instance, runner.model, [])
        self.assertIn('\n## Concerns\n\n- v1/gap on `Small.colA`, `Small.unitG`: A boundary case needs checking. (pending); '
                      'comprehensive review pending assignment\n', self.view('frontier.md'))
        runner.populate()
        runner.save()
        [job] = [j for j in runner.state['jobs'].values() if j['role'] == 'review' and j['task']['kind'] == 'comprehensive']
        knowledge.render(self.instance, runner.model, [])
        self.assertIn(f"(pending); comprehensive review {job['id']} (pending)\n", self.view('frontier.md'))

    def test_the_frontier_view_keeps_question_proposals_review_did_not_admit(self):
        folder = self.candidate(
            understanding={'q0.md': 'The sum grows by one odd number at a time.\n'},
            questions=[{'id': 'speer-vague', 'statement': 'What is going on with squares?', 'grounds': 'Squares appear.'},
                       {'id': 'speer-again', 'statement': 'What is the root problem as a whole?', 'grounds': 'It is the problem.'},
                       {'id': 'speer-layers', 'statement': 'Why does each odd number complete a square?',
                        'grounds': 'The proof uses the identity without saying what it shows.'}])
        assessment = self.verdicts(folder)
        assessment['questions'][0].update(verdict='revise', reason='Say which property of squares is meant.')
        assessment['questions'][1].update(verdict='declined', reason='This is the root question.', duplicate_of='q0')
        change, _ = self.publish(folder, assessment, role='explore', question='q0')
        view = self.view('frontier.md')
        self.assertIn('## speer-layers\n\nWhy does each odd number complete a square?\n\n'
                      'Grounds: The proof uses the identity without saying what it shows.\n\n'
                      f'State: open\nSource: change {change}\n', view)
        self.assertIn('## q0\n\nThe root problem itself, taken as a whole.\n', view)
        self.assertIn('State: open\nSource: the root statement\n', view)
        proposals = view.split('## Question proposals review did not admit')[1]
        self.assertIn(f'- revise: What is going on with squares? — review: Say which property of squares is meant. — change {change}',
                      proposals)
        self.assertIn('- declined (duplicate of q0): What is the root problem as a whole? — review: This is the root question. '
                      f'— change {change}', proposals)
        self.assertNotIn('## speer-vague', view)

    def test_the_index_lists_what_each_record_says_in_the_order_of_the_lean_structure(self):
        self.ways()
        view = self.view('index.md')
        self.assertTrue(view.startswith('# Index of the canon\n\nRevision: 2\n'))
        self.assertIn('This view is derived; nothing here is written by hand.', view)
        self.assertEqual([line for line in view.splitlines() if line.startswith(('## ', '- '))], [
            '## Small.Defs',
            '- `Small.oddSum` · unit · def — The sum of the first n odd numbers, defined by recursion on n.',
            '## Small.Root',
            '- `Small.root` · unit · accepted — The sum of the first n odd numbers equals n times n.',
            '## Small.Way2',
            '- `Small.monoBAlt` · unit · proof not confirmed — Mono from the first odd number.',
            '- `Small.rootAlt` · unit · correct, held back — The root by way 2, from Col and Diag.',
            '## Small.Ways',
            '- `Small.colA` · unit · correct, held back — The first two odd numbers sum to four.',
            '- `Small.diagD` · unit · proof not confirmed — The first six odd numbers sum to thirty-six.',
            '- `Small.leafH` · unit · no proof — The first odd number is one.',
            '- `Small.monoB` · unit · no proof — The first three odd numbers sum to nine.',
            '- `Small.stepE` · step · accepted — The first four odd numbers sum to sixteen.',
            '- `Small.stepF` · step · no proof — The first five odd numbers sum to twenty-five.',
            # Text of a record is shown as text: a sign that Markdown would read as markup is escaped.
            '- `Small.strayS` · unit · no proof — Seven odd numbers sum to forty-nine, which is &lt; 50.',
            '- `Small.unitG` · unit · accepted — The empty sum is zero.'])

    def test_the_board_shows_the_work_under_way_its_sections_and_the_leases(self):
        self.split()
        runner = Runner(self.instance, self.skill)
        a, b, c, d = (self.session(runner, sid) for sid in ('sa', 'sb', 'sc', 'sd'))
        whole = take(a, 'Small.sumZero')['section']
        part = take(b, 'Small.sumSucc', 'The passage from n to n + 1 for even n.')['section']
        bridge = {'lean': 'theorem sumDouble (n : Nat) : oddSum (n + 2) = oddSum n + 4 * n + 4',
                  'statement': 'Two more odd numbers add 4n + 4.'}
        new = take(c, 'Small.sumSucc', new=bridge, reasons={part['id']: 'A different statement.'})['section']
        self.assertTrue(lease(c, 'Small.sumSucc')['leased'])
        self.assertFalse(wait(d, 'Small.sumSucc', timeout=0)['leased'])
        knowledge.render(self.instance, runner.model, board(self.instance), lease_table(self.instance))
        view = self.view('board.md')
        self.assertTrue(view.startswith(f"# Research work and occupied sections\n\nResearch revision: {runner.model['sequence']}\n"))
        self.assertIn('Sections and questions remain occupied through peer and review.', view)
        pipelines = {sid: runner.state['jobs'][runner.state['sessions'][sid]['job']]['pipeline'] for sid in ('sa', 'sb', 'sc', 'sd')}
        self.assertIn(f"- {pipelines['sa']} · producer: sa · attempt · producing · elements: Small.sumZero\n"
                      f"  Section {whole['id']} on Small.sumZero (session sa): the whole element\n", view)
        self.assertIn(f"- {pipelines['sb']} · producer: sb · attempt · producing · elements: Small.sumSucc\n"
                      f"  Section {part['id']} on Small.sumSucc (session sb): The passage from n to n + 1 for even n.\n", view)
        self.assertIn(f"  Section {new['id']} on Small.sumSucc (session sc): a new statement aimed at this element: "
                      'theorem sumDouble (n : Nat) : oddSum (n + 2) = oddSum n + 4 * n + 4\n', view)
        self.assertIn(f"- {pipelines['sd']} · producer: sd · attempt · producing · elements: (choosing)\n", view)
        self.assertIn('\n## Element leases\n\n- Small.sumSucc · lease: sc · waiting: sd\n', view)
        # The view of an element says of each section held on it which of the three kinds it is.
        zero = canon_tool.view(self.instance, runner.model, 'Small.sumZero').splitlines()
        self.assertIn('held by       sa (attempt, producing): the whole element', zero)
        succ = canon_tool.view(self.instance, runner.model, 'Small.sumSucc').splitlines()
        self.assertIn('held by       sb (attempt, producing): The passage from n to n + 1 for even n.', succ)
        self.assertIn('held by       sc (attempt, producing): a new statement aimed at it: '
                      'theorem sumDouble (n : Nat) : oddSum (n + 2) = oddSum n + 4 * n + 4', succ)

    def test_board_can_show_a_producer_waiting_for_its_first_model(self):
        runner = Runner(self.instance, self.skill)
        runner.producer('attempt')
        rows = board(self.instance, runner.state)
        self.assertEqual(rows[0]['stage'], 'queued')
        self.assertIsNone(rows[0]['session'])
        self.assertEqual(runner.available_elements(), ['Small.root'])
        runner.producer('explore')
        knowledge.render(self.instance, knowledge.replay(self.instance), board(self.instance, runner.state))
        visible = self.view('board.md')
        self.assertIn('producer: (not launched)', visible)
        # The attempt is still choosing an element; the exploration is still choosing a question.
        self.assertIn('· attempt · queued · elements: (choosing)', visible)
        self.assertIn('· explore · queued · question: (choosing)', visible)

    def test_board_view_lists_the_sections_an_exploration_peer_registers(self):
        # Any peer may register a further section through the element's lease. The board rows already count
        # it as occupancy; board.md must show it under the exploration as well.
        runner = Runner(self.instance, self.skill)
        self.session(runner, 'sexplore', role='explore')
        peer = self.peer_session(runner, 'sexplore', 'speer')
        self.assertTrue(take(peer, 'Small.root')['registered'])
        self.assertEqual(runner.available_elements(), [])
        knowledge.render(self.instance, knowledge.replay(self.instance), board(self.instance, runner.state))
        visible = self.view('board.md')
        self.assertIn('· explore · peer · question: (none)', visible)
        self.assertIn('  Section speer-1 on Small.root (session speer): the whole element', visible)

    def test_render_command_rebuilds_the_views_only_while_the_runner_is_off(self):
        self.direct()
        views = [self.instance / 'knowledge' / name for name in ('frontier.md', 'index.md', 'board.md', 'state.json')]
        for path in views:
            path.unlink()
        with InstanceLock(self.instance / 'runner/lock'), patch('builtins.print'):
            self.assertEqual(main(['render', str(self.instance)]), 1)
        self.assertFalse(any(path.exists() for path in views))
        with patch('builtins.print'):
            self.assertEqual(main(['render', str(self.instance)]), 0)
        self.assertIn('State: informal_proved', self.view('frontier.md'))
        # A settled root is the whole frontier, and its line says that no formal proof settles it yet.
        self.assertIn('- `Small.root` — odd numbers sum to a square — settled; no formal proof yet',
                      self.view('frontier.md').splitlines())
        self.assertIn('- `Small.root` · unit · accepted — The sum of the first n odd numbers equals n times n.', self.view('index.md'))
        self.assertIn('Research work and occupied sections', self.view('board.md'))
        self.assertEqual(read_json(views[3]), knowledge.replay(self.instance))


class CanonToolTests(ScenarioCase):
    """The text views of canon_tool, as a session runs them: `canon_tool.py <command> <session> ...`."""

    def tool(self, command, *arguments, code=0):
        stream = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='\n')
        with patch('sys.stdout', stream):
            returned = canon_tool.main([command, str(self.reader()), *arguments])
        stream.flush()
        text = stream.buffer.getvalue().decode('utf-8')
        self.assertEqual(returned, code, text)
        return text

    def changes(self):
        """The IDs of the published changes, in order."""
        model = knowledge.replay(self.instance)
        return [change['id'] for change in sorted(model['changes'].values(), key=lambda c: c['sequence'])]

    def test_frontier_prints_the_view_with_the_holders_and_counts_the_work_that_remains(self):
        self.ways()
        runner = Runner(self.instance, self.skill)
        self.assertTrue(take(self.session(runner, 'sa'), 'Small.diagD')['registered'])
        text = self.tool('frontier')
        lines = text.splitlines()
        self.assertEqual(lines[0], 'Root: Small.root · state: unresolved · revision 2')
        expected = FRONTIER.splitlines()
        expected[8] += ' · held by 1 session'
        self.assertEqual(lines[2:12], expected)
        count = ('Elements of this view that are work that remains: 7. Each has one of the standings "no proof", '
                 '"proof not confirmed", "correct, held back", or a proof that names a statement refuted since.')
        self.assertIn(count, lines)
        # The questions follow, as in frontier.md: each with its grounds, its state and its source.
        self.assertEqual(lines[lines.index(count) + 2:lines.index(count) + 5], ['# Questions', '', '## q0'])
        self.assertIn('State: open', lines)
        self.assertIn('Source: the root statement', lines)
        # What stands beside the lines is printed as in frontier.md: the concerns not yet cleared.
        self.assertNotIn('## Concerns', text)
        self.event('v1', 'review', comprehensive(concerns=[
            {'id': 'gap', 'targets': ['Small.colA'], 'reason': 'A boundary case needs checking.', 'evidence': 'The case n = 0.'}]))
        self.assertIn('\n## Concerns\n\n- v1/gap on `Small.colA`: A boundary case needs checking. (pending)\n', self.tool('frontier'))

    def test_view_joins_the_structure_lean_gave_with_what_the_record_says(self):
        self.ways()
        first = self.changes()[0]
        model = knowledge.replay(self.instance)
        text = self.tool('view', 'Small.colA')
        lines = text.splitlines()
        self.assertEqual(lines[0], 'Small.colA · theorem · unit · correct, held back — The first two odd numbers sum to four.')
        for line in ('Lean          Small.colA : oddSum 2 = 4',
                     'short name    Col',
                     'proof         written in the record; its Lean proof ends in sorry',
                     'rests on      Small.leafH (no proof, unsettled, not formal)',
                     'settled       no',
                     'objects       Small.oddSum',
                     'used by       Small.root (accepted), Small.rootAlt (correct, held back)',
                     'axioms        sorryAx',
                     # Review's verdict is bound to the statement it saw, and carries its reason.
                     f"verdict       for statement {model['elements']['Small.colA']['statement_hash']}: confirmed, not accepted ({first})",
                     '              ' + HELD_REASON,
                     'record parts  statement, proof (read one with --part, all with --full; --part source prints the Lean text)'):
            self.assertIn(line, lines)
        source = next(line for line in lines if line.startswith('source'))
        self.assertRegex(source, r'^source        canon/lean/Small/Ways\.lean, lines \d+-\d+$')
        # The parts of the record are read separately; the head view does not carry them.
        self.assertNotIn('Split into the two terms', text)
        self.assertEqual(self.tool('view', 'Small.colA', '--part', 'proof'), 'Split into the two terms and add them.\n')
        self.assertEqual(self.tool('view', 'Small.colA', '--part', 'statement'), 'The sum $1 + 3$ equals $4$.\n')
        self.assertEqual(self.tool('view', 'Small.colA', '--part', 'explanation'), 'The record has no "Explanation" part.\n')
        self.assertEqual(self.tool('view', 'Small.colA', '--part', 'source'),
                         theorem('colA', ': oddSum 2 = 4', uses=['leafH']) + '\n')
        full = self.tool('view', 'Small.colA', '--full')
        self.assertIn('\n## Statement\n\nThe sum $1 + 3$ equals $4$.\n', full)
        self.assertIn('\n## Proof\n\nSplit into the two terms and add them.\n', full)
        self.assertNotIn('record parts', full)

    def test_view_shows_a_formal_proof_other_proofs_and_what_is_not_confirmed(self):
        self.ways()
        formal = self.tool('view', 'Small.unitG').splitlines()
        self.assertIn('proof         complete in Lean', formal)
        self.assertIn('settled       yes · proved in Lean from the allowed axioms', formal)
        self.assertIn('rests on      (none)', formal)
        self.assertFalse([line for line in formal if line.startswith('axioms')])
        open_statement = self.tool('view', 'Small.monoB').splitlines()
        self.assertEqual(open_statement[0], 'Small.monoB · theorem · unit · no proof — The first three odd numbers sum to nine.')
        self.assertIn('proof         none', open_statement)
        self.assertIn('proofs        Small.monoB (no proof), Small.monoBAlt (proof not confirmed)', open_statement)
        self.assertIn('used by       Small.stepE (accepted)', open_statement)
        other = self.tool('view', 'Small.monoBAlt').splitlines()
        self.assertEqual(other[0], 'Small.monoBAlt · theorem · unit · proof not confirmed · another proof of Small.monoB '
                                   '— Mono from the first odd number.')
        self.assertIn('rests on      Small.leafH (no proof, unsettled, not formal)', other)
        self.assertIn('              The addition is not carried out.', other)
        gap = self.tool('view', 'Small.diagD').splitlines()
        self.assertIn('rests on      Small.stepF (no proof, unsettled, not formal)', gap)
        self.assertTrue([line for line in gap if line.startswith('verdict') and line.endswith(f': not_confirmed ({self.changes()[0]})')])
        self.assertIn('              ' + GAP_REASON, gap)

    def test_the_verdict_of_a_proof_whose_confirmation_a_later_review_withdrew_names_that_review(self):
        self.ways()
        first = self.changes()[0]
        model = knowledge.replay(self.instance)
        names = ('Small.stepE', 'Small.colA')
        statement = {name: model['elements'][name]['statement_hash'] for name in names}

        def verdict(name):
            return next(line for line in self.tool('view', name).splitlines() if line.startswith('verdict'))

        # Before: one proof accepted, one held back, both under the change that published them.
        self.assertEqual(verdict('Small.stepE'),
                         f"verdict       for statement {statement['Small.stepE']}: confirmed, accepted ({first})")
        self.assertEqual(verdict('Small.colA'),
                         f"verdict       for statement {statement['Small.colA']}: confirmed, not accepted ({first})")
        reason = 'The additions are asserted and not carried out.'
        self.event('v1', 'review', comprehensive([finding(reason, invalidates=list(names))]))
        for name in names:
            with self.subTest(name=name):
                # The acceptance given with the confirmation is not in force, so the line says nothing of it,
                # and it names the review that withdrew the confirmation, not the change.
                self.assertEqual(verdict(name), f'verdict       for statement {statement[name]}: not_confirmed (v1)')
                self.assertIn('              ' + reason, self.tool('view', name).splitlines())
        # A later review that restores the confirmations brings back the reasons they were given with, so the
        # held proof shows again where it can be improved, in its view and on the frontier.
        self.event('v2', 'review', comprehensive([finding('The additions are carried out after all.', status='cleared',
                                                          validates=list(names))]))
        self.assertEqual(verdict('Small.stepE'),
                         f"verdict       for statement {statement['Small.stepE']}: confirmed, accepted (v2)")
        self.assertEqual(verdict('Small.colA'),
                         f"verdict       for statement {statement['Small.colA']}: confirmed, not accepted (v2)")
        self.assertIn('              Argument checked.', self.tool('view', 'Small.stepE').splitlines())
        self.assertIn('              ' + HELD_REASON, self.tool('view', 'Small.colA').splitlines())
        self.assertIn('  - `Small.colA` — Col — correct, held back: ' + HELD_REASON, self.tool('frontier').splitlines())

    def test_the_reading_commands_take_the_instance_folder_and_the_others_refuse_it(self):
        # The operator reads the canon with the same commands, giving the instance folder for the session.
        self.ways()
        self.note('Each odd number completes the next square.')

        def run(folder, command, *arguments):
            stream = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='\n')
            with patch('sys.stdout', stream):
                returned = canon_tool.main([command, str(folder), *arguments])
            stream.flush()
            return returned, stream.buffer.getvalue().decode('utf-8')

        for argv in (('frontier',), ('view', 'Small.colA'), ('view', 'Small.monoB', '--full'),
                     ('view', 'Small.colA', '--part', 'source'), ('list',), ('list', '--remaining'),
                     ('list', '--used-by', 'Small.leafH', '--deep'), ('question', 'q0'), ('question', 'q0', '--history'),
                     ('log',), ('log', '--last', '1')):
            with self.subTest(argv=argv):
                code, text = run(self.instance, *argv)
                self.assertEqual(code, 0, text)
                self.assertEqual(text, self.tool(*argv))
        # The commands that build or copy work in a session folder only.
        before = sorted(p.relative_to(self.instance).as_posix() for p in self.instance.rglob('*'))
        target = self.root / 'checked-out'
        for argv in (('prepare',), ('verify',), ('checkout', str(target))):
            with self.subTest(argv=argv):
                code, text = run(self.instance, *argv)
                self.assertEqual((code, json.loads(text)), (1, {
                    'error': argv[0] + ' works in a session folder; the instance folder serves the reading commands only'}))
        self.assertFalse(target.exists())
        self.assertEqual(sorted(p.relative_to(self.instance).as_posix() for p in self.instance.rglob('*')), before)

    def test_view_of_a_definition_carries_its_lean_text(self):
        self.ways()
        text = self.tool('view', 'Small.oddSum')
        lines = text.splitlines()
        self.assertEqual(lines[0], 'Small.oddSum · def · unit — The sum of the first n odd numbers, defined by recursion on n.')
        self.assertIn('```lean\n/-- The sum of the first `n` odd numbers. -/\ndef oddSum : Nat → Nat\n  | 0 => 0\n'
                      '  | n + 1 => oddSum n + (2 * n + 1)\n```\n', text)
        # A definition has no proof and none of the four states.
        self.assertFalse([line for line in lines if line.startswith(('proof ', 'rests on', 'settled', 'verdict'))])
        self.assertIn('stated with   11 statements mention it (list --about Small.oddSum)', lines)

    def test_view_lists_the_library_theorems_a_declaration_uses(self):
        # The stand-in compiler reports no theorem of an imported library, so the index is given what Lean reports.
        self.ways()
        canon = Canon(self.instance)
        index = canon.load_index()
        names = [f'Nat.lemma_{number:02d}' for number in range(14)]
        index['entries']['Small.unitG']['library'] = names[:2]
        index['entries']['Small.colA']['library'] = names
        write_json(canon.index, index)
        self.assertIn('library       Nat.lemma_00, Nat.lemma_01', self.tool('view', 'Small.unitG').splitlines())
        # The first twelve, and the number of the rest.
        self.assertIn('library       ' + ', '.join(names[:12]) + ' and 2 more', self.tool('view', 'Small.colA').splitlines())

    def test_view_shows_concerns_later_reviews_approaches_and_history(self):
        self.ways()
        first = self.changes()[0]
        self.event('v1', 'review', comprehensive(concerns=[
            {'id': 'gap', 'targets': ['Small.colA'], 'reason': 'A boundary case needs checking.', 'evidence': 'The case n = 0.'}]))
        self.event('v2', 'review', comprehensive([finding('The merged case fails at the boundary.', concerns=['v1/gap'],
                                                          invalidates=['Small.colA'])]))
        lines = self.tool('view', 'Small.colA').splitlines()
        self.assertEqual(lines[0], 'Small.colA · theorem · unit · proof not confirmed — The first two odd numbers sum to four.')
        self.assertIn('concern       v1/gap (confirmed): A boundary case needs checking.', lines)
        self.assertIn('later review  v2 (confirmed): The merged case fails at the boundary.', lines)
        self.assertIn('              The merged case fails at the boundary.', lines)
        # The approaches tried stand with the statement they were aimed at, with review's assessment of the work.
        lines = self.tool('view', 'Small.monoB').splitlines()
        self.assertIn('approach      induction: Induction on the number of terms — stops: '
                      'The comparison needs the sum of two terms in a form not yet stated.', lines)
        self.assertIn('record parts  approaches (read one with --part, all with --full; --part source prints the Lean text)', lines)
        approaches = self.tool('view', 'Small.monoB', '--part', 'approaches')
        self.assertTrue(approaches.startswith('### Approach induction\n\n---\ntitle: Induction on the number of terms\nsessions: s-early\n'))
        self.assertIn('## Idea\n\nCompare the sum of three terms with the sum of two.\n', approaches)
        self.assertIn(f'## Review\n\nChange {first} (revision 1): Closed what it took on.\n', approaches)
        self.assertIn('### Approach induction', self.tool('view', 'Small.monoB', '--full'))
        self.assertEqual(self.tool('view', 'Small.colA', '--part', 'approaches'), 'No approaches recorded.\n')
        # Who holds the element, or the statement it proves, stands in its view with the part held.
        runner = Runner(self.instance, self.skill)
        self.assertTrue(take(self.session(runner, 'sa'), 'Small.monoBAlt', 'The addition of three and five.')['registered'])
        for name in ('Small.monoB', 'Small.monoBAlt'):
            self.assertIn('held by       sa (attempt, producing): The addition of three and five.',
                          self.tool('view', name).splitlines())
        self.assertFalse([line for line in self.tool('view', 'Small.colA').splitlines() if line.startswith('held by')])
        # What a replacement left is shown only when asked for: the record and the proof that were replaced.
        history = self.tool('view', 'Small.root', '--part', 'history')
        self.assertIn(f'# Small.root: record replaced at revision 1 by {first}', history)
        self.assertIn(f'# Small.root: proof replaced at revision 1 by {first}', history)
        self.assertIn('The current text is at `lean/Small/Root.lean`.', history)
        self.assertIn('The current text is at `records/Small/root.md`.', history)
        self.assertNotIn('record replaced', self.tool('view', 'Small.root', '--full'))
        self.assertEqual(self.tool('view', 'Small.leafH', '--part', 'history'), 'No history.\n')

    def test_the_history_of_an_element_leaves_out_the_elements_whose_names_extend_the_name(self):
        # `Small.root.even` is an element of its own, and its history folder lies inside that of `Small.root`.
        self.ways()
        even = ': oddSum 2 = 4'
        self.publish(self.candidate(modules={'Small/Even.lean': module_text(theorem('root.even', even))},
                                    records={'Small/root/even.md': record_text('The first two odd numbers sum to four.')}))
        self.publish(self.candidate(replace={'Small.root.even': theorem('root.even', even, proof='rfl')}))
        self.assertIn('# Small.root.even: proof replaced', self.tool('view', 'Small.root.even', '--part', 'history'))
        history = self.tool('view', 'Small.root', '--part', 'history')
        self.assertIn('# Small.root: proof replaced', history)
        self.assertNotIn('Small.root.even', history)

    def test_view_marks_a_contested_statement_a_refuted_one_and_a_proof_that_names_it(self):
        self.proved()
        folder = self.candidate(
            modules={'Small/Against.lean': module_text(theorem('notZero', ': ¬ (oddSum 0 = 0)'))},
            records={'Small/notZero.md': record_text('The empty sum is not zero.', weight='unit',
                                                     proof='A miscount of the empty sum.', refutes='Small.sumZero')})
        self.publish(folder)
        contested = ('contested     it and its negation both carry settled proofs; nothing rests on either until a '
                     'comprehensive review locates the failure')
        for name in ('Small.sumZero', 'Small.notZero'):
            self.assertIn(contested, self.tool('view', name).splitlines())
        self.assertNotIn(contested, self.tool('view', 'Small.root').splitlines())
        text = self.tool('frontier')
        self.assertIn('  - `Small.sumZero` — The empty sum is zero. — accepted · contested: it and its negation both carry '
                      'settled proofs\n', text)
        self.assertIn('\nContested: a statement and its negation both carry settled proofs, and nothing rests on either '
                      'until a comprehensive review locates the failure: `Small.sumZero`.\n', text)
        # Once the proof is withdrawn, the statement is refuted, and the proof above it names a refuted statement.
        self.event('v1', 'review', comprehensive([finding('The empty sum was miscounted.', invalidates=['Small.sumZero'])]))
        refuted = self.tool('view', 'Small.sumZero').splitlines()
        self.assertIn('refuted by    Small.notZero (accepted)', refuted)
        self.assertNotIn(contested, refuted)
        self.assertIn('names refuted Small.sumZero (its proof cannot become settled as it stands)',
                      self.tool('view', 'Small.root').splitlines())
        text = self.tool('frontier')
        self.assertIn('  - `Small.sumZero` — The empty sum is zero. — refuted by `Small.notZero`\n', text)
        self.assertIn('\nElements of this view that are work that remains: 1. Each has one of the standings "no proof", '
                      '"proof not confirmed", "correct, held back", or a proof that names a statement refuted since.'
                      '\n\n# Questions\n', text)

    def test_view_names_the_questions_whose_text_names_the_element(self):
        self.split()
        self.assertFalse([line for line in self.tool('view', 'Small.sumZero').splitlines() if line.startswith('questions')])
        self.questions('qops', [{'id': 'empty', 'statement': 'Why is `Small.sumZero` stated apart from the step?',
                                 'grounds': 'The induction starts there.'}])
        self.note('The step `Small.sumSucc` carries the whole induction; `Small.sumZero` only starts it.')
        self.assertIn('questions     empty, q0 (their text names this element)', self.tool('view', 'Small.sumZero').splitlines())
        self.assertIn('questions     q0 (their text names this element)', self.tool('view', 'Small.sumSucc').splitlines())
        self.assertFalse([line for line in self.tool('view', 'Small.sumTwo').splitlines() if line.startswith('questions')])

    def test_an_unknown_name_is_an_error_with_exit_code_one(self):
        self.assertEqual(json.loads(self.tool('view', 'Small.absent', code=1)), {'error': 'no such element: Small.absent'})
        self.assertEqual(json.loads(self.tool('list', '--uses', 'Small.absent', code=1)), {'error': 'no such element: Small.absent'})
        self.assertEqual(json.loads(self.tool('question', 'absent', code=1)), {'error': 'no such question: absent'})

    def test_an_argument_in_the_place_of_the_session_directory_is_named_in_the_error(self):
        # The element given first and the session directory after it, as sessions have called the command.
        stream = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='\n')
        with patch('sys.stdout', stream):
            returned = canon_tool.main(['view', 'Small.root', str(self.reader())])
        stream.flush()
        error = json.loads(stream.buffer.getvalue().decode('utf-8'))['error']
        self.assertEqual(returned, 1, error)
        self.assertEqual(error, 'Small.root is not a session directory: it holds no input.json. The session directory comes '
                                'directly after the name of the command, and the arguments of the command follow it')

    def listed(self, *arguments):
        """The names a list command returned, after checking the count it printed."""
        lines = self.tool('list', *arguments).splitlines()
        names = [line.split(' · ')[0] for line in lines[:-1]]
        self.assertEqual(lines[-1], f'{len(names)} elements.')
        return [name.removeprefix('Small.') for name in names]

    def test_list_returns_everything_its_rule_selects_with_the_count(self):
        self.ways()
        everything = ['colA', 'diagD', 'leafH', 'monoB', 'monoBAlt', 'oddSum', 'root', 'rootAlt', 'stepE', 'stepF', 'strayS', 'unitG']
        self.assertEqual(self.listed(), everything)
        # One head line per element: what the record says of it, with the current standing.
        lines = self.tool('list', '--module', 'Small.Way2').splitlines()
        self.assertEqual(lines, ['Small.monoBAlt · theorem · unit · proof not confirmed · another proof of Small.monoB '
                                 '— Mono from the first odd number.',
                                 'Small.rootAlt · theorem · unit · correct, held back · another proof of Small.root '
                                 '— The root by way 2, from Col and Diag.',
                                 '2 elements.'])
        # Containment: a module, or every module under a prefix.
        self.assertEqual(self.listed('--module', 'Small.Ways'),
                         ['colA', 'diagD', 'leafH', 'monoB', 'stepE', 'stepF', 'strayS', 'unitG'])
        self.assertEqual(self.listed('--module', 'Small'), everything)
        self.assertEqual(self.listed('--module', 'Small.Way'), [])
        # Use, one step or all the way, in both directions.
        self.assertEqual(self.listed('--uses', 'Small.root'), ['colA', 'stepE', 'unitG'])
        self.assertEqual(self.listed('--uses', 'Small.root', '--deep'), ['colA', 'stepE', 'unitG', 'leafH', 'monoB'])
        self.assertEqual(self.listed('--used-by', 'Small.leafH'), ['colA', 'monoBAlt'])
        self.assertEqual(self.listed('--used-by', 'Small.leafH', '--deep'), ['colA', 'monoBAlt', 'root', 'rootAlt'])
        self.assertEqual(self.listed('--used-by', 'Small.strayS'), [])
        # Object: every element whose statement mentions a definition, or whose proof uses a statement.
        self.assertEqual(self.listed('--about', 'Small.oddSum'), [name for name in everything if name != 'oddSum'])
        self.assertEqual(self.listed('--about', 'Small.colA'), ['root', 'rootAlt'])
        # Standing: the work that remains for the root.
        self.assertEqual(self.listed('--remaining'), ['colA', 'diagD', 'leafH', 'monoB', 'monoBAlt', 'rootAlt', 'stepF'])
        # The units of the proof, without the steps inside one.
        self.assertEqual(self.listed('--remaining', '--units'), ['colA', 'diagD', 'leafH', 'monoB', 'monoBAlt', 'rootAlt'])
        self.assertEqual(self.listed('--module', 'Small.Ways', '--units'), ['colA', 'diagD', 'leafH', 'monoB', 'strayS', 'unitG'])

    def test_question_prints_its_state_and_the_understanding_so_far_with_reviews_assessment(self):
        text = self.tool('question', 'q0')
        self.assertTrue(text.startswith('q0 · open\n\nThe root problem itself, taken as a whole.\n\nGrounds: An explorer holding'))
        self.assertIn('No understanding has been written for this question yet.', text)
        self.questions('qops', [{'id': 'scale', 'statement': 'Why do the methods stall at the same scale?',
                                 'grounds': 'Several approaches stop there.'},
                                {'id': 'block', 'statement': 'What does the common block say about the object?',
                                 'grounds': 'The same obstruction recurs.'}])
        folder = self.candidate(understanding={'q0.md': 'The sum grows by one odd number at a time.\n',
                                               'block.md': 'The block is the overlap of two squares.\n'},
                                resolutions=[{'id': 'answer', 'question': 'block'}])
        change, _ = self.publish(folder, role='explore', question='block')
        text = self.tool('question', 'q0')
        self.assertIn('## Understanding so far\n\nThe sum grows by one odd number at a time.\n', text)
        self.assertIn(f'## Review of the work that wrote it\n\nChange {change} (revision 2): Closed what it took on.\n', text)
        self.assertTrue(self.tool('question', 'block').startswith(
            'block · resolved\n\nWhat does the common block say about the object?\n\nGrounds: The same obstruction recurs.\n'))
        self.assertIn('No understanding has been written', self.tool('question', 'scale'))
        # A merged question answers under either name with the text of the one that remains.
        self.organize(batch=[change], merge_questions=[{'from': 'scale', 'into': 'block', 'reason': 'Both ask about the block.'}])
        merged = self.tool('question', 'scale')
        self.assertTrue(merged.startswith('block · resolved\n\nWhat does the common block say about the object?\n'))
        self.assertIn('The block is the overlap of two squares.', merged)
        # A replaced understanding is kept in the history and printed only when asked for.
        self.assertNotIn('--history', self.tool('question', 'q0'))
        self.assertIn('## Earlier texts\n\nNone.\n', self.tool('question', 'q0', '--history'))
        later, _ = self.note('Each step completes a square.')
        current = self.tool('question', 'q0')
        self.assertIn('## Understanding so far\n\nEach step completes a square.\n', current)
        self.assertNotIn('The sum grows by one odd number at a time.', current)
        self.assertIn('1 earlier text of this understanding can be read with --history.', current)
        earlier = self.tool('question', 'q0', '--history')
        self.assertIn(f'# Question q0: understanding replaced at revision 4 by {later}', earlier)
        self.assertIn('+The sum grows by one odd number at a time.', earlier)

    def test_log_prints_the_recent_changes_with_reviews_assessment_of_each(self):
        self.assertEqual(self.tool('log'), 'No change has been published yet.\n')
        self.ways()
        first, second = self.changes()
        text = self.tool('log')
        self.assertEqual(text.splitlines(), [
            f'{first} · revision 1 · attempt · A contribution',
            '  A precise contribution with its limitations.',
            '  Review: Closed what it took on.',
            '  Added: Small.colA, Small.diagD, Small.leafH, Small.monoB, Small.stepE, Small.stepF, Small.strayS, Small.unitG; '
            'proofs replaced: Small.root',
            '',
            f'{second} · revision 2 · attempt · A contribution',
            '  A precise contribution with its limitations.',
            '  Review: Closed what it took on.',
            '  Added: Small.monoBAlt, Small.rootAlt; proofs replaced: (none)',
            ''])
        last = self.tool('log', '--last', '1')
        self.assertIn(second, last)
        self.assertNotIn(first, last)


if __name__ == '__main__':
    unittest.main()
