"""Questions: objects of understanding that explorers occupy, proposed and resolved through review."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from availability import no_research_outcome
from check import Invalid, assessment_check, check_session, organization_check, record_check
from coordination import (board, lease, question_availability, question_lease, question_lease_table,
                          question_release, question_take, question_wait, updates)
from knowledge import canonical_question, render, replay
from runner import Runner, status
from runtime_support import read_json, write_json
from settings import defaults
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

    def test_operator_questions_enter_the_frontier_with_their_origin(self):
        self.questions('qops', [question('op-critical-scale'), question('op-common-block')])
        model = replay(self.instance)
        self.assertEqual({q for q, v in model['questions'].items() if v['state'] == 'open'},
                         {'q0', 'op-critical-scale', 'op-common-block'})
        self.assertEqual(model['questions']['op-critical-scale']['origin'], 'operator')
        self.assertEqual(model['questions']['op-critical-scale']['source'], 'qops')
        frontier = self.frontier(model)
        self.assertIn('## op-critical-scale\n', frontier)
        self.assertIn('operator publication [qops](questions/qops/questions.json)', frontier)
        self.assertEqual(read_json(self.instance / 'knowledge/state.json')['questions'], model['questions'])

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
        with self.assertRaisesRegex(Invalid, 'root question'):
            organization_check({**organization, 'merge_questions': [{'from': 'q0', 'into': 'op-b', 'reason': 'No.'}]}, model, [])
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
                                           'pipeline': job['pipeline'], 'task': {}})
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
        self.assertEqual(view['occupied'], {'q0': 'sroot', 'op-scale': 'sa'})
        self.assertEqual(view['choosing'], [read_json(b / 'input.json')['pipeline']])
        listed = {q['id']: (q['state'], q['occupied_by'], q['free']) for q in updates(b)['questions']}
        self.assertEqual(listed['op-scale'], ('open', 'sa', False))
        self.assertEqual(listed['op-block'], ('open', None, True))
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

    def test_only_explorers_use_question_commands(self):
        attempt = self.session('sattempt', role='attempt')
        with self.assertRaisesRegex(ValueError, 'only explorers'):
            question_lease(attempt, 'q0')
        explorer = self.session('sexplore')
        with self.assertRaisesRegex(ValueError, 'only attempts and peers'):
            lease(explorer, 'root')
        with self.assertRaisesRegex(ValueError, 'unknown question'):
            question_lease(explorer, 'nope')


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

    def test_default_exploration_cadence_is_every_research_start(self):
        self.assertEqual(defaults()['explore_every'], 1)
        self.assertEqual(read_json(self.instance / 'settings.json')['explore_every'], 1)

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
            self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'], {'q0': sid})
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

    def test_a_retried_explorer_is_assigned_the_root_question_its_failed_launch_was_given(self):
        runner = self.runner()
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            key = runner.producer('explore')
            self.assertTrue(runner.dispatch(key))
            job = runner.state['jobs'][key]
            failed = job['session']
            # The launch ends without research material: the job is pending again, and its pipeline
            # still names the failed session, whose declaration records the runner's assignment of q0.
            runner.retry(job, runner.state['sessions'][failed], 'session ended without retained research material',
                         availability=False)
            self.assertEqual(runner.state['pipelines'][job['pipeline']]['producer'], failed)
            job['not_before'] = 0
            self.assertTrue(runner.question_slot(exclude_job=key))
            runner.dispatch_pending()
        relaunched = job['session']
        self.assertEqual(job['status'], 'running')
        self.assertNotIn(relaunched, (None, failed))
        self.assertEqual(job['task']['question'], 'q0')
        self.assertEqual(read_json(runner.session_dir(relaunched) / 'declaration.json')['question']['id'], 'q0')
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'], {'q0': relaunched})

    def test_occupied_nodes_fill_free_questions_with_explorers_one_request_at_a_time(self):
        self.questions('qops', [question('op-scale'), question('op-block')])
        runner = self.runner()
        runner.settings['max_sessions'] = 8
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
            runner.state['last_attempt_launch'] = 0
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
        self.assertEqual((view['occupied'], view['free']), ({'q0': sid}, []))
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
        self.assertTrue(runner.question_slot(exclude_job=job['id']))
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = runner.identity['pid']
            runner.dispatch_pending()
        self.assertNotIn(job['session'], (None, sid))
        self.assertEqual(job['task']['question'], 'q0')
        self.assertEqual(question_availability(self.instance, runner.state, runner.model)['occupied'],
                         {'q0': job['session']})

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
