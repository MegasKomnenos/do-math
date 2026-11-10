"""Questions: objects of understanding that explorers occupy, proposed and resolved through review."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from availability import no_research_outcome
from check import Invalid, assessment_check, check_session, organization_check, record_check
from coordination import (board, main as coordination_main, question_availability, question_lease,
                          question_lease_table, question_release, question_take, question_wait, updates)
from knowledge import canonical_question, render, replay
from runner import Runner, main, operator_questions, status
from runtime_support import git, read_json, write_json
from test_research import InstanceCase, assessment, claim_row, implication, record, solution


def question(qid, statement=None):
    return {'id': qid, 'statement': statement or ('What ' + qid + ' asks.'),
            'grounds': 'Several records stall at the same scale; understanding it would show why.'}


def resolution(rid, qid, cid):
    return {'id': rid, 'question': qid, 'claim': cid}


class QuestionKnowledgeTests(InstanceCase):
    def frontier(self, model=None):
        render(self.instance, model or replay(self.instance), [])
        return (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')

    def test_root_question_is_always_present_open_and_unresolvable(self):
        model = replay(self.instance)
        self.assertEqual(model['questions']['q0']['state'], 'open')
        self.assertEqual(model['questions']['q0']['origin'], 'root')
        folder = self.root / 'candidate'
        folder.mkdir()
        (folder / 'record.md').write_text('An explanation.', encoding='utf-8')
        data = record([claim_row('why')], question_resolutions=[resolution('r', 'q0', 'why')])
        with self.assertRaisesRegex(Invalid, 'root question'):
            record_check(data, folder, model)
        frontier = self.frontier(model)
        self.assertIn('## q0\n', frontier)
        self.assertIn('Source: the root statement', frontier)
        self.assertIn('State: open', frontier.split('## q0\n', 1)[1])

    def formal_root(self, rid, outcome='proved'):
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p', outcome)])
        self.publish(rid, data, assessment(data, ['p']), role='formalizer')

    def test_root_question_is_resolved_by_the_root_formal_settlement(self):
        for outcome in ('proved', 'refuted'):
            with self.subTest(outcome=outcome):
                self.setUp()
                self.questions('qops', [question('op-scale')])
                self.formal_root('r1', outcome)
                model = replay(self.instance)
                q0 = model['questions']['q0']
                self.assertEqual(model['nodes']['root']['state'], 'formal_' + outcome)
                self.assertEqual(q0['state'], 'resolved')
                self.assertEqual(q0['resolutions'], [])
                self.assertEqual(q0['root_settlement'],
                                 {'node': 'root', 'state': 'formal_' + outcome, 'proofs': ['r1/p']})
                self.assertIsNone(model['questions']['op-scale']['root_settlement'])
                self.assertEqual(model['questions']['op-scale']['state'], 'open')
                section = self.frontier(model).split('## q0\n', 1)[1].split('\n## ', 1)[0]
                self.assertIn('State: resolved', section)
                self.assertIn("Resolved by the root's formal settlement, not by an explanation: node root is formal_"
                              + outcome + ' through [r1/p](records/r1/record.json)', section)
                self.assertEqual(read_json(self.instance / 'knowledge/state.json')['questions']['q0'], q0)
                # An explanation still cannot resolve it, and it is still never merged.
                folder = self.root / 'candidate'
                folder.mkdir(exist_ok=True)
                (folder / 'record.md').write_text('An explanation.', encoding='utf-8')
                with self.assertRaisesRegex(Invalid, 'root question'):
                    record_check(record([claim_row('why')], question_resolutions=[resolution('r', 'q0', 'why')]),
                                 folder, model)
                with self.assertRaisesRegex(Invalid, 'root question'):
                    organization_check({'batch': [], 'modules': [], 'shared_context': [], 'merge_questions': [
                        {'from': 'op-scale', 'into': 'q0', 'reason': 'No.'}]}, model, [])

    def test_an_informal_or_contested_root_leaves_the_root_question_open(self):
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        self.publish('r1', data)
        model = replay(self.instance)
        self.assertEqual(model['nodes']['root']['state'], 'informal_proved')
        self.assertEqual(model['questions']['q0']['state'], 'open')
        self.assertIsNone(model['questions']['q0']['root_settlement'])
        self.assertIn('State: open', self.frontier(model).split('## q0\n', 1)[1])
        # A formal proof against an accepted refutation leaves the root contested, not settled.
        self.formal_root('r2')
        self.publish('r3', record([claim_row('n')], solutions=[solution('n', 'root', 'n', 'refuted')]))
        model = replay(self.instance)
        self.assertEqual(model['nodes']['root']['state'], 'contested')
        self.assertEqual(model['questions']['q0']['state'], 'open')
        self.assertIsNone(model['questions']['q0']['root_settlement'])

    def test_withdrawing_the_root_formal_settlement_reopens_the_root_question(self):
        self.formal_root('r1')
        self.assertEqual(replay(self.instance)['questions']['q0']['state'], 'resolved')
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed',
                                                'reason': 'The Lean statement is not the root proposition.',
                                                'invalidates': [{'record': 'r1', 'claim': 'p'}]}]})
        model = replay(self.instance)
        self.assertEqual(model['nodes']['root']['state'], 'unresolved')
        self.assertEqual(model['questions']['q0']['state'], 'open')
        self.assertIsNone(model['questions']['q0']['root_settlement'])
        section = self.frontier(model).split('## q0\n', 1)[1].split('\n## ', 1)[0]
        self.assertIn('State: open', section)
        self.assertNotIn("root's formal settlement, not", section)
        # The withdrawal stays visible beside the reopened question, as for any other question.
        self.assertIn('not the root proposition', section)
        self.assertIn('reviews/v1/assessment.json', section)

    def test_review_admits_declines_or_asks_to_revise_question_proposals(self):
        self.questions('qops', [question('op-existing')])
        data = record([claim_row('obs')], questions=[question('speer-sharp'), question('speer-dup'), question('speer-vague')])
        review = assessment(data)
        review['questions'] = [
            {'proposal': 'speer-sharp', 'verdict': 'admitted', 'reason': 'Important and exact.'},
            {'proposal': 'speer-dup', 'verdict': 'declined', 'duplicate_of': 'op-existing',
             'reason': 'op-existing already asks this.'},
            {'proposal': 'speer-vague', 'verdict': 'revise',
             'reason': 'Name the regime and the quantity whose behaviour is asked about.'}]
        self.publish('r1', data, review)
        model = replay(self.instance)
        self.assertEqual(model['questions']['speer-sharp']['source'], 'r1')
        self.assertEqual(model['questions']['speer-sharp']['origin'], 'record')
        self.assertNotIn('speer-dup', model['questions'])
        self.assertNotIn('speer-vague', model['questions'])
        self.assertEqual([(p['id'], p['verdict'], p.get('duplicate_of')) for p in model['question_proposals']],
                         [('speer-dup', 'declined', 'op-existing'), ('speer-vague', 'revise', None)])
        frontier = self.frontier(model)
        self.assertIn('## speer-sharp\n', frontier)
        self.assertIn('Source: [r1](records/r1/record.json)', frontier)
        self.assertIn('- revise: What speer-vague asks. — review: Name the regime', frontier)
        self.assertIn('- declined (duplicate of op-existing): What speer-dup asks.', frontier)

    def test_resolution_follows_its_claim_and_a_withdrawal_reopens_the_question(self):
        self.questions('qops', [question('op-scale')])
        self.publish('r1', record([claim_row('explain')], question_resolutions=[resolution('res', 'op-scale', 'explain')]))
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'resolved')
        self.assertEqual(model['questions']['op-scale']['resolutions'], ['r1/res'])
        self.assertIn('Resolved by [r1/res](records/r1/record.json) through claim r1/explain', self.frontier(model))
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed',
                                                'reason': 'The explanation assumes the conclusion.',
                                                'invalidates': [{'record': 'r1', 'claim': 'explain'}]}]})
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'open')
        self.assertEqual(model['questions']['op-scale']['resolutions'], [])
        section = self.frontier(model).split('## op-scale\n', 1)[1].split('\n## ', 1)[0]
        self.assertIn('State: open', section)
        self.assertIn('assumes the conclusion', section)
        self.assertIn('reviews/v1/assessment.json', section)

    def test_unaccepted_resolution_leaves_the_question_open(self):
        self.questions('qops', [question('op-scale')])
        data = record([claim_row('partial')], question_resolutions=[resolution('res', 'op-scale', 'partial')])
        review = assessment(data)
        review['question_resolutions'] = [{'proposal': 'res', 'resolved': False, 'reason': 'Explains one regime only.'}]
        self.publish('r1', data, review)
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-scale']['state'], 'open')
        self.assertEqual(model['question_resolutions'], {})

    def test_organizer_merges_duplicate_questions_and_preserves_aliases(self):
        self.questions('qops', [question('op-a'), question('op-b')])
        model = replay(self.instance)
        organization = {'batch': [], 'modules': [], 'shared_context': [],
                        'merge_questions': [{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask about the same scale.'}]}
        organization_check(organization, model, [])
        for merge in ({'from': 'q0', 'into': 'op-b'}, {'from': 'op-a', 'into': 'q0'}):
            with self.subTest(merge=merge), self.assertRaisesRegex(Invalid, 'root question'):
                organization_check({**organization, 'merge_questions': [{**merge, 'reason': 'No.'}]}, model, [])
        with self.assertRaisesRegex(Invalid, 'existing questions'):
            organization_check({**organization, 'merge_questions': [{'from': 'op-a', 'into': 'missing', 'reason': 'No.'}]}, model, [])
        self.event('o1', 'organization', organization)
        model = replay(self.instance)
        self.assertEqual(canonical_question(model, 'op-a'), 'op-b')
        self.assertEqual(model['questions']['op-a']['canonical'], 'op-b')
        # A resolution recorded against the old identity resolves the merged question.
        self.publish('r1', record([claim_row('e')], question_resolutions=[resolution('res', 'op-a', 'e')]))
        model = replay(self.instance)
        self.assertEqual(model['questions']['op-b']['state'], 'resolved')
        frontier = self.frontier(model)
        self.assertNotIn('\n## op-a\n', frontier)
        self.assertIn('Aliases: op-a', frontier)


class OperatorQuestionTests(InstanceCase):
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
        self.publish('rq', self.reduction())  # node Q
        # Review identifies proposal P with the root, so P is a node alias without being a node.
        data = record([claim_row('same')], [{'id': 'P', 'statement': 'The root again.', 'connection': 'same'}])
        review = assessment(data)
        review['nodes'] = [{'proposal': 'P', 'node': 'root', 'reason': 'The same statement.'}]
        self.publish('rp', data, review)
        self.questions('qops', [question('op-a'), question('op-b')])
        self.event('o1', 'organization', {'batch': [], 'modules': [], 'shared_context': [],
                                          'merge_questions': [{'from': 'op-a', 'into': 'op-b', 'reason': 'Same.'}]})
        model = replay(self.instance)
        self.assertEqual((model['aliases'], model['question_aliases']), ({'P': 'root'}, {'op-a': 'op-b'}))
        self.assertNotIn('P', model['nodes'])
        good = question('op-new')
        cases = (
            ('Expecting', '{not json'),
            ('is an object', [good]),
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
            ('invalid question id', {'reason': 'R.', 'questions': [{**good, 'id': 7}]}),
            ('invalid question id', {'reason': 'R.', 'questions': [{k: v for k, v in good.items() if k != 'id'}]}),
            ('q0 is the root question', {'reason': 'R.', 'questions': [{**good, 'id': 'q0'}]}),
            ('duplicate question id: op-new', {'reason': 'R.', 'questions': [good, good]}),
            ('already names a question', {'reason': 'R.', 'questions': [{**good, 'id': 'op-b'}]}),
            ('already names a question', {'reason': 'R.', 'questions': [{**good, 'id': 'op-a'}]}),
            ('already names a question', {'reason': 'R.', 'questions': [{**good, 'id': 'Q'}]}),
            ('already names a question', {'reason': 'R.', 'questions': [{**good, 'id': 'root'}]}),
            ('already names a question', {'reason': 'R.', 'questions': [{**good, 'id': 'P'}]}),
            ('needs a nonempty "statement"', {'reason': 'R.', 'questions': [{**good, 'statement': ' '}]}),
            ('needs a nonempty "statement"', {'reason': 'R.', 'questions': [{**good, 'statement': None}]}),
            ('needs a nonempty "grounds"', {'reason': 'R.', 'questions': [{**good, 'grounds': ''}]}),
            ('needs a nonempty "grounds"', {'reason': 'R.', 'questions': [{k: v for k, v in good.items() if k != 'grounds'}]}),
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

    def test_the_runner_publishes_the_request_and_the_frontier_shows_the_operator_as_its_source(self):
        items = [question('op-scale'), question('op-block')]
        reason = 'Two places the records keep stalling.'
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
        self.assertEqual(read_json(self.instance / 'knowledge/state.json')['questions'], model['questions'])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        section = frontier.split('## op-scale\n', 1)[1].split('\n## ', 1)[0]
        self.assertIn(f'Source: operator publication [{eid}](questions/{eid}/questions.json)', section)
        # The request is collected once.
        runner.ingest_inputs()
        Runner(self.instance, self.skill).ingest_inputs()
        self.assertEqual(self.events(), [name])

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
        runner.prepare_questions(Path(answer['request']).name, reason, items)
        prepared = runner.state['publication']
        stage = self.instance / 'runner' / ('stage-' + prepared['event']['id'])
        stage.mkdir()
        (stage / 'questions.json').write_text('{"partial', encoding='utf-8')
        recovered = Runner(self.instance, self.skill)
        recovered.ingest_inputs()  # the request counts as collected; the prepared publication waits
        self.assertEqual(self.events(), [])
        recovered.collect()
        eid = prepared['event']['id']
        self.assertEqual(self.events(), [eid + '.json'])
        self.assertEqual(read_json(self.instance / 'knowledge/questions' / eid / 'questions.json'), prepared['questions'])
        self.assertEqual(list((self.instance / 'runner').glob('stage-*')), [])
        self.assertIsNone(recovered.state['publication'])

    def test_an_identifier_taken_before_collection_is_refused_and_the_runner_continues(self):
        code, first = self.command({'reason': 'R.', 'questions': [question('op-scale')]})
        self.assertEqual(code, 0)
        code, second = self.command({'reason': 'R.', 'questions': [question('op-block')]})
        self.assertEqual(code, 0)
        # Between the command's check and the runner's collection, a record's review admits op-scale.
        self.publish('r1', record([claim_row('c')], questions=[question('op-scale')]))
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
                         ('record', 'r1'))
        # The other request is published in the same pass; the refused one is not collected again.
        self.assertEqual(model['questions']['op-block']['origin'], 'operator')
        self.assertEqual(len([n for n in self.events() if n != 'r1.json']), 1)
        runner.ingest_inputs()
        self.assertEqual(runner.state['last_error'], error)
        self.assertEqual(len(self.events()), 2)

    def test_the_question_migration_event_keeps_replaying_as_an_operator_publication(self):
        # The running instance holds one questions event that the one-time migration script wrote outside
        # the runner; its event and file carry the extra keys source and migration. Replay reads both forms.
        folder = self.instance / 'knowledge/questions/qmigrated'
        folder.mkdir(parents=True)
        write_json(folder / 'questions.json', {
            'source': 'operator', 'reason': 'Initial questions.', 'questions': [question('op-scale')], 'at': 1.0,
            'migration': 'do-math question introduction; placed by the operator, not through peer and review'})
        write_json(self.instance / 'knowledge/events/qmigrated.json',
                   {'id': 'qmigrated', 'kind': 'questions', 'sequence': 1, 'folder': 'questions/qmigrated',
                    'at': 1.0, 'source': 'operator-migration'})
        model = replay(self.instance)
        entry = model['questions']['op-scale']
        self.assertEqual((entry['origin'], entry['source'], entry['state']), ('operator', 'qmigrated', 'open'))
        render(self.instance, model, [])
        self.assertIn('Source: operator publication [qmigrated](questions/qmigrated/questions.json)',
                      (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))
        # An operator publication through the command after it takes the next revision.
        self.assertEqual(self.command({'reason': 'R.', 'questions': [question('op-block')]})[0], 0)
        self.assertEqual(self.command({'reason': 'R.', 'questions': [question('op-scale')]})[0], 1)
        runner = Runner(self.instance, self.skill)
        runner.ingest_inputs()
        model = replay(self.instance)
        self.assertEqual(model['sequence'], 2)
        self.assertEqual(model['questions']['op-scale']['source'], 'qmigrated')
        self.assertEqual(model['questions']['op-block']['origin'], 'operator')


class QuestionCheckTests(InstanceCase):
    def candidate(self):
        folder = self.root / 'candidate'
        folder.mkdir(exist_ok=True)
        (folder / 'record.md').write_text('An account.', encoding='utf-8')
        return folder

    def test_record_check_guards_question_proposals_and_resolutions(self):
        self.questions('qops', [question('op-scale'), question('speer-taken')])
        self.publish('rnode', record([claim_row('reduce')],
                                     [{'id': 'speer-node', 'statement': 'N', 'connection': 'reduce'}],
                                     [implication('reduce', 'speer-node')]))
        model = replay(self.instance)
        folder = self.candidate()
        record_check(record([claim_row('c')], questions=[question('speer-new')],
                            question_resolutions=[resolution('res', 'op-scale', 'c')]), folder, model, 'speer')
        cases = (
            ('peer session prefix', record([claim_row('c')], questions=[question('other-new')])),
            ('already names a question or node', record([claim_row('c')], questions=[question('speer-taken')])),
            ('already names a question or node', record([claim_row('c')], questions=[question('speer-node')])),
            ('question.grounds', record([claim_row('c')], questions=[{'id': 'speer-x', 'statement': 'S'}])),
            ('existing question', record([claim_row('c')], question_resolutions=[resolution('r', 'speer-x', 'c')])),
            ('resolving claim', record([claim_row('c')], question_resolutions=[resolution('r', 'op-scale', 'missing')])),
            ('distinct from solution', record([claim_row('c')], solutions=[solution('r', 'root', 'c')],
                                              question_resolutions=[resolution('r', 'op-scale', 'c')])),
        )
        for pattern, data in cases:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(Invalid, pattern):
                record_check(data, folder, model, 'speer')

    def test_assessment_check_requires_a_verdict_for_every_question_and_resolution(self):
        self.questions('qops', [question('op-scale')])
        model = replay(self.instance)
        data = record([claim_row('c')], questions=[question('speer-new')],
                      question_resolutions=[resolution('res', 'op-scale', 'c')])
        folder = self.candidate()
        out = self.root / 'review'
        out.mkdir()
        (out / 'feedback.md').write_text('Review.', encoding='utf-8')
        good = assessment(data)
        assessment_check(good, out, data, folder, model, self.instance, 's1')
        cases = {
            'assess every question proposal': {**good, 'questions': []},
            'assess every question resolution': {**good, 'question_resolutions': []},
            'admitted, declined or revise': {**good, 'questions': [{'proposal': 'speer-new', 'verdict': 'maybe', 'reason': 'x'}]},
            'a duplicate is declined': {**good, 'questions': [{'proposal': 'speer-new', 'verdict': 'revise',
                                                              'duplicate_of': 'op-scale', 'reason': 'x'}]},
            'existing question': {**good, 'questions': [{'proposal': 'speer-new', 'verdict': 'declined',
                                                        'duplicate_of': 'nope', 'reason': 'x'}]},
            'supported claim': {**good, 'claims': [{'claim': 'c', 'status': 'unsupported', 'reason': 'Gap.'}]},
        }
        for pattern, bad in cases.items():
            with self.subTest(pattern=pattern), self.assertRaisesRegex(Invalid, pattern):
                assessment_check(bad, out, data, folder, model, self.instance, 's1')
        excluded = {**good, 'publish': False,
                    'question_resolutions': [{'proposal': 'res', 'resolved': False, 'reason': 'Not shown.'}]}
        with self.assertRaisesRegex(Invalid, 'excluded candidate'):
            assessment_check(excluded, out, data, folder, model, self.instance, 's1')
        excluded['questions'] = [{'proposal': 'speer-new', 'verdict': 'declined', 'reason': 'Nothing to keep.'}]
        assessment_check(excluded, out, data, folder, model, self.instance, 's1')

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


class QuestionCoordinationTests(InstanceCase):
    def setUp(self):
        super().setUp()
        self.engine = Runner(self.instance, self.skill)

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

    def test_explorer_takes_one_question_through_its_lease(self):
        self.questions('qops', [question('op-scale'), question('op-block')])
        self.engine.model = replay(self.instance)
        a, b = self.session('sa'), self.session('sb')
        # While q0 is free, an explorer takes it before any narrower question.
        self.assertIn('q0', question_lease(a, 'op-scale')['reason'])
        root = self.session('sroot')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_take(root, 'q0')['taken'])
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        refused = question_lease(b, 'op-scale')
        self.assertFalse(refused['leased'])
        self.assertEqual(refused['holders'], ['sa'])
        self.assertIn('lease', question_take(b, 'op-scale')['reason'])
        taken = question_take(a, 'op-scale')
        self.assertTrue(taken['taken'], taken)
        self.assertEqual(read_json(a / 'declaration.json')['question']['id'], 'op-scale')
        self.assertNotIn('op-scale', question_lease_table(self.instance))
        # An explorer holds one question; a question another exploration holds is refused.
        self.assertTrue(question_lease(a, 'op-block')['leased'])
        self.assertIn('already occupies', question_take(a, 'op-block')['reason'])
        question_release(a, 'op-block')
        self.assertNotIn('op-block', question_lease_table(self.instance))
        self.assertIn('holds this question', question_lease(b, 'op-scale')['reason'])
        rows = {r['session']: r['question'] for r in board(self.instance, self.engine.state)}
        self.assertEqual(rows, {'sa': 'op-scale', 'sb': None, 'sroot': 'q0'})
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual(view['free'], ['op-block'])
        self.assertEqual(view['occupied'], {'q0': ['sroot'], 'op-scale': ['sa']})
        self.assertEqual(view['choosing'], [read_json(b / 'input.json')['pipeline']])
        listed = {q['id']: (q['state'], q['occupied_by'], q['free']) for q in updates(b)['questions']}
        self.assertEqual(listed['op-scale'], ('open', ['sa'], False))
        self.assertEqual(listed['op-block'], ('open', [], True))
        render(self.instance, self.engine.model, board(self.instance, self.engine.state))
        visible = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
        self.assertIn('· explore · producing · question: op-scale', visible)
        self.assertIn('· explore · producing · question: (choosing)', visible)

    def test_waiters_receive_the_question_lease_in_order_and_a_resolved_question_is_refused(self):
        self.questions('qops', [question('op-scale')])
        self.engine.model = replay(self.instance)
        a, b = self.session('sa'), self.session('sb')
        # Another explorer holds q0, so the narrower question can be leased.
        root = self.session('sroot')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_take(root, 'q0')['taken'])
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        self.assertEqual(question_wait(b, 'op-scale', timeout=0)['position'], 1)
        # A held lease blocks the runner from counting the question as free.
        self.assertEqual(question_availability(self.instance, self.engine.state)['free'], [])
        question_release(a, 'op-scale')
        self.assertTrue(question_wait(b, 'op-scale', timeout=0)['leased'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])
        self.publish('r1', record([claim_row('e')], question_resolutions=[resolution('res', 'op-scale', 'e')]))
        c = self.session('sc')
        self.assertIn('resolved', question_lease(c, 'op-scale')['reason'])
        self.assertIn('resolved', question_wait(c, 'op-scale', timeout=0)['reason'])
        self.assertIn('holds this question', question_lease(c, 'q0')['reason'])

    def test_a_narrower_question_is_refused_while_the_root_question_is_free(self):
        self.questions('qops', [question('op-scale')])
        self.engine.model = replay(self.instance)
        a, b = self.session('sa'), self.session('sb')
        # An explorer still choosing when q0 becomes free takes q0, as the runner's assignment would have.
        self.assertIn('q0', question_lease(a, 'op-scale')['reason'])
        self.assertIn('q0', question_wait(a, 'op-scale', timeout=0)['reason'])
        self.assertTrue(question_lease(a, 'q0')['leased'])
        # Once another explorer holds q0's lease, a narrower question can be taken.
        self.assertTrue(question_lease(b, 'op-scale')['leased'])
        self.assertTrue(question_take(a, 'q0')['taken'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])

    def test_a_take_is_refused_once_the_question_is_resolved_or_q0_is_free_under_the_lease(self):
        self.questions('qops', [question('op-scale'), question('op-block')])
        self.engine.model = replay(self.instance)
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        # A lease on q0 keeps q0 from counting as free, so both narrower questions can be leased.
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_lease(a, 'op-scale')['leased'])
        self.assertTrue(question_lease(b, 'op-block')['leased'])
        self.publish('r1', record([claim_row('e')], question_resolutions=[resolution('res', 'op-scale', 'e')]))
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
        self.questions('qops', [question('op-scale')])
        self.engine.model = replay(self.instance)
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        self.assertTrue(question_lease(root, 'q0')['leased'])
        self.assertTrue(question_take(root, 'q0')['taken'])
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        self.publish('r1', data, assessment(data, ['p']), role='formalizer')
        # The exploration that held q0 keeps it through its peer and review.
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied'], view['free']), ({'q0': ['sroot']}, ['op-scale']))
        self.assertEqual([r['question'] for r in board(self.instance, self.engine.state)
                          if r['session'] == 'sroot'], ['q0'])
        # Once that pipeline ends, the resolved q0 is neither free nor takeable, and it no longer
        # holds back a narrower question for an explorer still choosing.
        pipeline = self.engine.state['jobs'][self.engine.state['sessions']['sroot']['job']]['pipeline']
        self.engine.state['pipelines'][pipeline]['stage'] = 'done'
        self.engine.save()
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied'], view['free']), ({}, ['op-scale']))
        refused = question_lease(a, 'q0')
        self.assertFalse(refused['leased'])
        self.assertIn('formally settled', refused['reason'])
        self.assertIn('formally settled', question_wait(a, 'q0', timeout=0)['reason'])
        self.assertTrue(question_lease(b, 'op-scale')['leased'])
        self.assertTrue(question_take(b, 'op-scale')['taken'])
        listed = {q['id']: q for q in updates(a)['questions']}
        self.assertEqual((listed['q0']['state'], listed['q0']['free']), ('resolved', False))
        self.assertEqual(status(self.instance)['questions']['free'], [])

    def test_a_merge_of_two_held_questions_leaves_both_explorers_holding_it_until_each_pipeline_ends(self):
        # An organizer's merge is an exception to one explorer per question, as it is for a node's
        # single lease holder: occupations taken before the merge continue to their own ends, and
        # meanwhile the merged question is not free to any further explorer.
        self.questions('qops', [question('op-a'), question('op-b')])
        self.engine.model = replay(self.instance)
        root, a, b = self.session('sroot'), self.session('sa'), self.session('sb')
        for folder, qid in ((root, 'q0'), (a, 'op-a'), (b, 'op-b')):
            self.assertTrue(question_lease(folder, qid)['leased'])
            self.assertTrue(question_take(folder, qid)['taken'])
        self.event('o1', 'organization', {'batch': [], 'modules': [], 'shared_context': [],
                                          'merge_questions': [{'from': 'op-a', 'into': 'op-b', 'reason': 'Same scale.'}]})
        self.engine.model = replay(self.instance)
        rows = {r['session']: r['question'] for r in board(self.instance, self.engine.state)}
        self.assertEqual(rows, {'sroot': 'q0', 'sa': 'op-b', 'sb': 'op-b'})
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((sorted(view['occupied']['op-b']), view['free']), (['sa', 'sb'], []))
        self.assertFalse(self.engine.question_slot())  # the runner launches no explorer for the merged question
        listed = {q['id']: (sorted(q['occupied_by']), q['free']) for q in updates(b)['questions']}
        self.assertEqual(listed['op-b'], (['sa', 'sb'], False))
        self.assertNotIn('op-a', listed)
        render(self.instance, self.engine.model, board(self.instance, self.engine.state))
        visible = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
        self.assertEqual(visible.count('· explore · producing · question: op-b'), 2)
        # A further explorer can take the merged question under neither identifier.
        c = self.session('sc')
        for qid in ('op-b', 'op-a'):
            refused = question_lease(c, qid)
            self.assertFalse(refused['leased'])
            self.assertIn('hold this question', refused['reason'])
            self.assertEqual(sorted(refused['occupied_by']), ['sa', 'sb'])
        # The occupations end separately; the question stays held while either lasts.
        pipelines = {sid: read_json(folder / 'input.json')['pipeline'] for sid, folder in (('sa', a), ('sb', b))}
        self.engine.state['pipelines'][pipelines['sa']]['stage'] = 'done'
        self.engine.save()
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['occupied']['op-b'], view['free']), (['sb'], []))
        self.assertIn('holds this question', question_lease(c, 'op-b')['reason'])
        self.engine.state['pipelines'][pipelines['sb']]['stage'] = 'done'
        self.engine.save()
        view = question_availability(self.instance, self.engine.state)
        self.assertEqual((view['free'], 'op-b' in view['occupied']), (['op-b'], False))
        self.assertTrue(question_lease(c, 'op-a')['leased'])
        taken = question_take(c, 'op-b')
        self.assertTrue(taken['taken'], taken)
        self.assertEqual(taken['question'], 'op-b')

    def test_only_explorers_use_question_commands(self):
        # The converse, that explorers do not register sections, is tested with the node commands (test_research).
        attempt = self.session('sattempt', role='attempt')
        with self.assertRaisesRegex(ValueError, 'only explorers'):
            question_lease(attempt, 'q0')

    def test_question_commands_answer_through_the_command_line_with_the_documented_exit_codes(self):
        # Explorers reach these commands only through the argv in input.json; the entry point is checked here.
        self.questions('qops', [question('op-scale')])
        self.engine.model = replay(self.instance)
        a, b, c = self.session('sa'), self.session('sb'), self.session('sc')

        def run(*argv):
            with patch('sys.argv', ['coordination.py', *argv]), patch('builtins.print') as shown:
                code = coordination_main()
            return code, json.loads(shown.call_args.args[0])

        code, answer = run('question-lease', str(a), 'q0')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('question-take', str(a), 'q0')
        self.assertEqual((code, answer['taken'], answer['question']), (0, True, 'q0'))
        self.assertEqual(read_json(a / 'declaration.json')['question']['by'], 'session')
        code, answer = run('question-lease', str(b), 'q0')
        self.assertEqual(code, 1)
        self.assertIn('holds this question', answer['reason'])
        code, answer = run('question-lease', str(b), 'op-scale')
        self.assertEqual((code, answer['leased']), (0, True))
        code, answer = run('question-wait', str(c), 'op-scale', '--timeout', '0')
        self.assertEqual((code, answer['timeout'], answer['position']), (124, True, 1))
        code, answer = run('question-release', str(c), 'op-scale')
        self.assertEqual((code, answer['released']), (0, True))
        code, answer = run('question-take', str(b), 'op-scale')
        self.assertEqual((code, answer['taken']), (0, True))
        code, answer = run('question-lease', str(b), 'nope')
        self.assertEqual((code, answer['error']), (1, 'unknown question'))


class QuestionDispatchTests(InstanceCase):
    def runner(self):
        return Runner(self.instance, self.skill)

    def occupy_root(self, runner):
        """An attempt holding the whole root, so that no node is available to a new attempt."""
        key = runner.producer('attempt')
        job = runner.state['jobs'][key]
        sid = 'sholder'
        folder = runner.session_dir(sid)
        folder.mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'attempt',
                                           'pipeline': job['pipeline'], 'task': {}})
        write_json(folder / 'declaration.json', {'sections': [
            {'id': sid + '-1', 'node': 'root', 'whole': True, 'statement': None, 'reasons': {}, 'at': 1}], 'at': 1})
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
            self.assertIn('"question": "q0"', (runner.session_dir(sid) / 'pack.md').read_text(encoding='utf-8'))
            self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'], {'q0': [sid]})
            # With the root question occupied, a further explorer launches without an assignment and chooses.
            self.questions('qops', [question('op-scale')])
            runner.model = replay(self.instance)
            second = runner.producer('explore')
            self.assertTrue(runner.dispatch(second))
            later = runner.state['jobs'][second]['session']
            self.assertNotIn('question', runner.state['jobs'][second]['task'])
            self.assertFalse((runner.session_dir(later) / 'declaration.json').exists())
        self.assertFalse(runner.question_slot())  # one free question, one explorer still choosing
        self.assertTrue(question_take(runner.session_dir(later), 'op-scale')['taken']
                        if question_lease(runner.session_dir(later), 'op-scale')['leased'] else False)
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], [])

    def test_root_assignment_is_saved_before_the_explorer_launches(self):
        runner = self.runner()
        seen = []
        prepare = runner.make_pack

        def observe(sid, job):
            # An explorer's question command reads the saved state, not the runner's memory.
            seen.append(question_availability(self.instance)['occupied'])
            return prepare(sid, job)

        with patch.object(runner, 'make_pack', side_effect=observe), patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            self.assertTrue(runner.dispatch(runner.producer('explore')))
        self.assertEqual(list(seen[0]), ['q0'])

    def test_occupied_nodes_fill_free_questions_with_explorers_one_request_at_a_time(self):
        self.questions('qops', [question('op-scale'), question('op-block')])
        runner = self.runner()
        runner.settings['max_sessions'] = 8
        runner.settings['launch_interval'] = 0  # launch spacing has its own test
        self.occupy_root(runner)
        self.assertEqual(runner.available_nodes(), [])
        self.assertFalse(runner.state['explore_requested'])
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.schedule()
        explorers = [sid for sid, s in runner.active() if s['role'] == 'explore']
        self.assertEqual(len(explorers), 3)
        assigned = [read_json(runner.session_dir(sid) / 'declaration.json')['question']['id']
                    for sid in explorers if (runner.session_dir(sid) / 'declaration.json').exists()]
        self.assertEqual(assigned, ['q0'])
        # The request is renewed while nodes stay occupied, and waits for a free question.
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

    def test_question_stays_occupied_through_peer_and_review(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, 'q0')
        runner.finish(sid, session)
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(pipeline['stage'], 'peer')
        peer = runner.state['jobs'][pipeline['id'] + ':peer']
        self.assertEqual(peer['task']['question'], 'q0')
        self.assertEqual(peer['task']['sections'], [])
        view = question_availability(self.instance, runner.state, runner.model)
        self.assertEqual((view['occupied'], view['free']), ({'q0': [sid]}, []))
        rows = board(self.instance, runner.state, runner.model)
        self.assertEqual([(r['stage'], r['question']) for r in rows], [('peer', 'q0')])
        pipeline['stage'] = 'done'
        runner.save()
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['free'], ['q0'])

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
        self.publish('r1', record([claim_row('e')], question_resolutions=[resolution('res', 'op-scale', 'e')]))
        runner.model = replay(self.instance)
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

    def test_an_exploration_that_reached_peer_without_a_question_is_not_choosing(self):
        runner = self.runner()
        sid, session, job, folder = self.ended_explorer(runner, None)
        # An interrupted explorer with retained material goes to peer even though it took no question.
        session['exit_code'] = 1
        runner.finish(sid, session)
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'peer')
        view = question_availability(self.instance, runner.state, runner.model)
        self.assertEqual((view['free'], view['choosing']), (['q0'], []))
        self.assertTrue(runner.question_slot())

    def test_status_reports_question_availability(self):
        runner = self.runner()
        self.ended_explorer(runner, 'q0')
        result = status(self.instance)
        self.assertEqual(result['questions']['free'], [])
        self.assertEqual(list(result['questions']['occupied']), ['q0'])
        self.assertFalse(result['questions']['explore_requested'])

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


if __name__ == '__main__':
    unittest.main()
