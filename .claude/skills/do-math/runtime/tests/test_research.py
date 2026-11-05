import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check import Invalid, assessment_check, organization_check, record_check
from cli_adapter import Command
from coordination import board, claim
from knowledge import canonical, formal_ready, render, replay, root_solved
from runner import Runner, initialize
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
        for name in ('reference', 'roles'):
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

    def test_concern_preserves_previous_consequence_but_blocks_new_ones(self):
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
        self.assertEqual(m['nodes']['root']['state'], 'informal_proved')
        self.assertTrue(m['proofs']['r1/reduce']['concerned'])
        for nid in ('R', 'S'):
            self.assertEqual(m['nodes'][nid]['state'], 'unresolved')
            self.assertEqual(m['nodes'][nid]['proofs'], [])
            self.assertIn('v1/boundary', m['nodes'][nid]['possible_concerns'])
        render(self.instance, m, [{'pipeline': 'p', 'role': 'attempt', 'stage': 'producing', 'nodes': ['S']}])
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        for nid in ('R', 'S'):
            section = frontier.split('## ' + nid + '\n', 1)[1].split('\n## ', 1)[0]
            self.assertIn('Possible dependency through a recorded relation', section)
            self.assertIn('v1/boundary', section)
            self.assertIn('reviews/v1/assessment.json', section)
        index = (self.instance / 'knowledge/index.md').read_text(encoding='utf-8')
        self.assertIn('Possible dependency through a recorded relation; effect undetermined.', index)
        self.assertIn('Concern: see [frontier](frontier.md) for S.',
                      (self.instance / 'knowledge/board.md').read_text(encoding='utf-8'))

    def test_concern_does_not_ban_formalizer_work_on_accepted_mathematics(self):
        self.publish('r1', record([claim_row('p')], solutions=[solution('s', 'root', 'p')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'question',
            'targets': [{'record': 'r1', 'claim': 'p'}], 'reason': 'A use needs examination.', 'evidence': 'Source location.'}]})
        model = replay(self.instance)
        self.assertTrue(model['proofs']['r1/s']['concerned'])
        self.assertTrue(formal_ready(model, model['proofs']['r1/s']))

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

    def test_review_can_clear_one_exact_use_before_the_whole_concern(self):
        self.publish('r1', self.reduction())
        self.publish('r2', record([claim_row('q')], solutions=[solution('q', 'Q', 'q')]))
        self.event('v1', 'review', {'findings': [], 'concerns': [{'id': 'issue', 'targets': [{'record': 'r2', 'claim': 'q'}], 'reason': 'A questioned range.', 'evidence': 'Source.'}]})
        self.publish('r3', record([claim_row('next')], [{'id': 'R', 'statement': 'R', 'connection': 'next'}], [implication('next', 'Q', 'R')]))
        self.event('v2', 'review', {'findings': [{'concerns': ['v1/issue'], 'status': 'undetermined', 'reason': 'This exact use avoids the issue.',
                                                'cleared_uses': [{'relation': 'r3/next', 'premise_proofs': ['r2/q']}]}]})
        m = replay(self.instance)
        self.assertEqual(m['nodes']['R']['state'], 'informal_proved')
        self.assertFalse(m['proofs']['r3/next']['concerned'])
        self.assertTrue(m['proofs']['r2/q']['concerned'])
        self.assertEqual(m['nodes']['R']['possible_concerns'], [])
        render(self.instance, m, [])
        section = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8').split('## R\n', 1)[1].split('\n## ', 1)[0]
        self.assertNotIn('Possible dependency through a recorded relation', section)

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

    def test_occupancy_survives_producer_exit(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        claim(runner.session_dir(sid), 'root')
        runner.finish(sid, session)
        self.assertEqual(board(self.instance, runner.state)[0]['nodes'], ['root'])
        self.assertEqual(board(self.instance, runner.state)[0]['stage'], 'peer')

    def test_claim_overlap_informs_instead_of_rejecting(self):
        runner = self.runner()
        sid, session, job = self.ended(runner, 'attempt')
        claim(runner.session_dir(sid), 'root')
        second = runner.session_dir('sother')
        second.mkdir(); write_json(second / 'input.json', {'instance': str(self.instance), 'role': 'attempt', 'session': 'sother'})
        result = claim(second, 'root')
        self.assertTrue(result['warnings'])
        self.assertEqual(result['nodes'], ['root'])

    def test_default_pool_and_provider_fallback(self):
        runner = self.runner()
        self.assertEqual(runner.selection('review')['model'], 'codex/gpt-6.1-sol')
        runner.state['blocks']['provider:codex'] = {'until': 10**12}
        self.assertEqual(runner.selection('review')['model'], 'claude/opus')

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
                    runner.retry(runner.state['jobs'][key], session, 'incomplete output')
                self.assertEqual(runner.state['blocks'][block_key]['until'], expected_until)
                self.assertEqual(runner.state['jobs'][key]['status'], 'pending')
                if deadline > 1060:
                    self.assertEqual(runner.state['blocks'][block_key], previous)
                with patch('runner.time.time', return_value=1061):
                    self.assertEqual(runner.selection('review')['model'], expected_model)

    def check_refusal_handoff(self, message, expected_key, expected_model):
        runner = self.runner()
        runner.settings['roles']['peer'] = [
            {'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'},
            {'model': 'codex/other', 'effort': 'xhigh'},
            {'model': 'claude/opus', 'effort': 'xhigh'},
        ]
        write_json(self.instance / 'settings.json', runner.settings)
        sid, session, job = self.ended(runner, 'attempt')
        folder = runner.session_dir(sid)
        with (folder / 'cli.stdout.jsonl').open('a', encoding='utf-8') as stream:
            stream.write('\n' + json.dumps({'type': 'error', 'message': message}) + '\n')
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
        self.check_refusal_handoff("You've hit your usage limit. Try again later.",
                                   'provider:codex', 'claude/opus')

    def test_model_refusal_retains_work_and_keeps_other_models_available(self):
        self.check_refusal_handoff('Selected model is at capacity',
                                   'model:codex/gpt-6.1-sol', 'codex/other')

    def test_waiting_review_blocks_fresh_attempt_even_when_other_provider_free(self):
        runner = self.runner()
        runner.settings['roles']['review'] = [{'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'}]
        runner.state['blocks']['provider:codex'] = {'until': 10**12}
        runner.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        runner.schedule()
        self.assertFalse(any(p['role'] == 'attempt' for p in runner.state['pipelines'].values()))

    def test_organizer_batch_excludes_arrivals_during_processing(self):
        for i in range(4): self.publish('r' + str(i), record())
        runner = self.runner(); runner.populate()
        job = next(j for j in runner.state['jobs'].values() if j['role'] == 'organizer')
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
                runner.retry(runner.state['jobs'][key], session, 'incomplete output')
                self.assertEqual(runner.state['jobs'][key]['task']['previous_partial_sessions'],
                                 [str(runner.session_dir('s' + role))])
                self.assertEqual(runner.state['jobs'][key]['status'], 'pending')

    def test_root_change_requires_new_instance(self):
        (self.instance / 'root.md').write_text('A different proposition.', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'new instance'):
            self.runner()

    def test_sorry_axiom_cannot_be_enabled(self):
        config = defaults(); config['lean']['allowed_axioms'].append('sorryAx')
        with self.assertRaises(ValueError): validate(config)

    def test_board_can_show_a_producer_waiting_for_its_first_model(self):
        runner = self.runner()
        runner.producer('attempt')
        rows = board(self.instance, runner.state)
        self.assertEqual(rows[0]['stage'], 'queued')
        self.assertIsNone(rows[0]['session'])
        self.assertEqual(runner.available_nodes(), (['root'], 1))


if __name__ == '__main__':
    unittest.main()
