"""No-work exits, state-dependent dispatch suppression and one-at-a-time reassessment."""
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from availability import opening_since
from check import check_session
from coordination import updates
from knowledge import replay
from runner import Runner, main
from runtime_support import read_json, write_json
from test_research import InstanceCase, take, record, claim_row


class AvailabilityTests(InstanceCase):
    def setUp(self):
        super().setUp()
        self.runner = Runner(self.instance, self.skill)
        self.serial = 0

    def attempt(self, role='attempt'):
        self.serial += 1
        runner = self.runner
        key = runner.producer(role)
        job = runner.state['jobs'][key]
        sid = 'stest' + str(self.serial)
        folder = runner.session_dir(sid)
        for name in ('output', 'work', 'inbox'):
            (folder / name).mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid,
                   'role': role, 'pipeline': job['pipeline'], 'task': {}, 'user_inputs': []})
        session = {'id': sid, 'role': role, 'job': key, 'status': 'running',
                   'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': time.time(),
                   'exit_code': 0, 'host': None, 'cli': None, 'retained': True,
                   'retention': {'cli_activity': True}}
        runner.state['sessions'][sid] = session
        job.update(status='running', session=sid)
        runner.state['pipelines'][job['pipeline']]['producer'] = sid
        runner.save()
        return sid, session, job

    def occupied(self):
        first, _, job = self.attempt()
        a = take(self.runner.session_dir(first), 'root', 'Left cases')
        self.assertTrue(a['registered'])
        second, _, _ = self.attempt()
        b = take(self.runner.session_dir(second), 'root', 'Right cases',
                 {a['section']['id']: 'Different cases'})
        self.assertTrue(b['registered'])
        return job['pipeline'], a['section']['id'], b['section']['id']

    def report(self, availability=True):
        sid, session, job = self.attempt()
        folder = self.runner.session_dir(sid)
        value = {'disposition': 'no_research'}
        if availability:
            value['availability'] = {'status': 'all_unresolved_work_occupied',
                                     'snapshot': updates(folder)['availability_snapshot']}
        write_json(folder / 'output/outcome.json', value)
        return sid, session, job

    def test_no_research_closes_once_without_peer_or_review(self):
        sid, session, job = self.report(False)
        self.runner.finish(sid, session)
        self.assertEqual(session['disposition'], 'no_research')
        self.assertEqual(self.runner.state['pipelines'][job['pipeline']]['stage'], 'done')
        self.assertEqual(len(self.runner.state['jobs']), 1)
        self.assertTrue((self.runner.session_dir(sid) / 'output/outcome.json').exists())
        restarted = Runner(self.instance, self.skill)
        restarted.finish(sid, restarted.state['sessions'][sid])
        self.assertEqual(len(restarted.state['jobs']), 1)
        self.assertIsNone(restarted.state['attempt_dispatch_gate'])

    def test_valid_coverage_survives_restart_time_and_unrelated_publication(self):
        self.occupied()
        sid, session, _ = self.report()
        self.assertEqual(check_session(self.runner.session_dir(sid)), [])
        self.runner.finish(sid, session)
        self.assertTrue(self.runner.state['explore_requested'])
        self.assertFalse(self.runner.attempt_dispatch_ready())
        self.publish('rnote', record([claim_row('unrelated')]))
        self.runner = Runner(self.instance, self.skill)
        with patch('runner.time.time', return_value=time.time() + 10**6):
            self.assertFalse(self.runner.attempt_dispatch_ready())
        third, _, _ = self.attempt()
        # Adding a section does not open work, even if a worker mistakenly reports overlap.
        write_json(self.runner.session_dir(third) / 'declaration.json',
                   {'sections': [{'id': 'new', 'node': 'root', 'whole': False,
                                  'statement': 'More occupied cases', 'at': 1}]})
        self.assertFalse(self.runner.attempt_dispatch_ready())

    def test_release_allows_exactly_one_probe_until_it_registers(self):
        pipeline, _, other = self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        self.runner.state['pipelines'][pipeline]['stage'] = 'done'
        self.runner.save()
        self.assertTrue(self.runner.attempt_dispatch_ready())
        key = self.runner.producer('attempt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = self.runner.identity['pid']
            self.assertTrue(self.runner.dispatch(key))
            second = self.runner.producer('attempt')
            self.assertFalse(self.runner.dispatch(second))
        probe = self.runner.state['jobs'][key]['session']
        self.runner = Runner(self.instance, self.skill)
        self.assertFalse(self.runner.attempt_dispatch_ready())
        self.assertTrue(take(self.runner.session_dir(probe), 'root', 'Left cases',
                             {other: 'Different cases'})['registered'])
        self.assertTrue(self.runner.attempt_dispatch_ready())
        self.assertIsNone(self.runner.state['attempt_dispatch_gate'])

    def test_probe_can_report_occupied_again_or_fail_without_sticking(self):
        pipeline, _, _ = self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        self.runner.state['pipelines'][pipeline]['stage'] = 'done'
        self.assertTrue(self.runner.attempt_dispatch_ready())
        probe, failed, _ = self.attempt()
        self.runner.state['attempt_dispatch_gate']['probe_session'] = probe
        failed['status'] = 'failed'
        self.assertTrue(self.runner.attempt_dispatch_ready())
        sid, session, _ = self.report()
        self.runner.state['attempt_dispatch_gate']['probe_session'] = sid
        self.runner.finish(sid, session)
        self.assertFalse(self.runner.attempt_dispatch_ready())

    def test_stale_coverage_does_not_change_terminal_outcome(self):
        pipeline, _, _ = self.occupied()
        sid, session, job = self.report()
        self.runner.state['pipelines'][pipeline]['stage'] = 'done'
        self.runner.finish(sid, session)
        self.assertEqual(job['status'], 'done')
        self.assertEqual(session['availability_report']['status'], 'stale')
        self.assertIsNone(self.runner.state['attempt_dispatch_gate'])
        self.assertFalse(any(j['role'] == 'peer' for j in self.runner.state['jobs'].values()))

    def test_bad_snapshot_does_not_reopen_or_send_terminal_attempt_to_peer(self):
        sid, session, job = self.report()
        folder = self.runner.session_dir(sid)
        value = read_json(folder / 'output/outcome.json')
        value['availability']['snapshot'] = '../not-a-token'
        write_json(folder / 'output/outcome.json', value)
        self.assertTrue(check_session(folder))
        self.runner.finish(sid, session)
        self.assertEqual(job['status'], 'done')
        self.assertEqual(session['availability_report']['status'], 'invalid')
        self.assertEqual(len(self.runner.state['jobs']), 1)

    def test_claimed_or_interrupted_work_cannot_opt_out(self):
        for kind in ('claimed', 'interrupted', 'refused', 'occupied_question', 'explorer_reports_availability'):
            with self.subTest(kind=kind):
                explorer = kind in ('occupied_question', 'explorer_reports_availability')
                sid, session, job = self.attempt('explore' if explorer else 'attempt')
                folder = self.runner.session_dir(sid)
                write_json(folder / 'output/outcome.json', {'disposition': 'no_research'})
                if kind == 'claimed':
                    write_json(folder / 'declaration.json', {'sections': [
                        {'id': sid + '-1', 'node': 'root', 'whole': True, 'statement': None,
                         'reasons': {}, 'at': 1}], 'at': 1})
                elif kind == 'occupied_question':
                    write_json(folder / 'declaration.json', {'question': {'id': 'q0', 'at': 1, 'by': 'runner'}, 'at': 1})
                elif kind == 'explorer_reports_availability':
                    write_json(folder / 'output/outcome.json', {'disposition': 'no_research', 'availability': {
                        'status': 'all_unresolved_work_occupied', 'snapshot': '0' * 64}})
                elif kind == 'interrupted':
                    session['exit_code'] = 1
                elif kind == 'refused':
                    session['refusal'] = {'reason': 'usage_limit'}
                self.runner.finish(sid, session)
                self.assertEqual(self.runner.state['pipelines'][job['pipeline']]['stage'], 'peer')

    def test_explorer_without_a_question_closes_with_no_research(self):
        sid, session, job = self.attempt('explore')
        folder = self.runner.session_dir(sid)
        write_json(folder / 'output/outcome.json', {'disposition': 'no_research'})
        self.assertEqual(check_session(folder), [])
        self.runner.finish(sid, session)
        self.assertEqual(session['disposition'], 'no_research')
        self.assertEqual(self.runner.state['pipelines'][job['pipeline']]['stage'], 'done')
        self.assertFalse(any(j['role'] == 'peer' for j in self.runner.state['jobs'].values()))
        self.assertNotIn('availability_report', session)
        self.assertIsNone(self.runner.state['attempt_dispatch_gate'])

    def test_new_node_and_reopening_trigger_but_solving_does_not(self):
        self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        self.runner.model['nodes']['root']['state'] = 'informal_proved'
        self.assertFalse(self.runner.attempt_dispatch_ready())
        self.runner.model['nodes']['root']['state'] = 'unresolved'
        self.assertTrue(self.runner.attempt_dispatch_ready())
        self.runner.state['attempt_dispatch_gate']['mode'] = 'suppressed'
        self.publish('rnew', self.reduction())
        self.runner.model = replay(self.instance)
        self.assertTrue(self.runner.attempt_dispatch_ready())

    def test_new_node_makes_a_delayed_report_stale(self):
        self.occupied()
        sid, session, _ = self.report()
        self.publish('rnew', self.reduction())
        self.runner.model = replay(self.instance)
        self.runner.finish(sid, session)
        self.assertEqual(session['availability_report']['status'], 'stale')

    def test_operator_reconsideration_rejects_older_reports_and_preserves_stop(self):
        self.occupied()
        sid, session, _ = self.report()
        (self.instance / 'control/STOP').touch()
        with patch('builtins.print'):
            self.assertEqual(main(['reconsider-attempts', str(self.instance)]), 0)
        self.runner.ingest_inputs()
        epoch = self.runner.state['attempt_availability_epoch']
        self.runner.ingest_inputs()
        self.assertEqual(self.runner.state['attempt_availability_epoch'], epoch)
        self.runner.finish(sid, session)
        self.assertEqual(session['availability_report']['status'], 'stale')
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['mode'], 'reassess')
        self.assertTrue((self.instance / 'control/STOP').exists())

    def test_suppression_stops_pending_attempt_and_fills_free_questions_with_explorers(self):
        self.runner.settings['launch_interval'] = 0  # launch spacing has its own test
        self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        key = self.runner.producer('attempt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = self.runner.identity['pid']
            self.runner.schedule()
            self.runner.schedule()
        self.assertEqual(self.runner.state['jobs'][key]['status'], 'pending')
        explorers = [sid for sid, a in self.runner.active() if a['role'] == 'explore']
        self.assertEqual(len(explorers), 1)  # the root question is the only free question
        self.assertEqual(read_json(self.runner.session_dir(explorers[0]) / 'declaration.json')['question']['id'], 'q0')
        # Occupied nodes renew the request after each launch; it waits for a free question.
        self.assertTrue(self.runner.state['explore_requested'])
        self.questions('qops', [{'id': 'op-scale', 'statement': 'Why do the methods stall at the same scale?',
                                 'grounds': 'Several records stop there.'},
                                {'id': 'op-block', 'statement': 'What does the common block tell about the object?',
                                 'grounds': 'The same obstruction recurs.'}])
        self.runner.model = replay(self.instance)
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = self.runner.identity['pid']
            self.runner.schedule()
        self.assertEqual(len([a for _, a in self.runner.active() if a['role'] == 'explore']), 3)
        self.assertEqual(self.runner.state['jobs'][key]['status'], 'pending')
        self.assertFalse(self.runner.question_slot())

    def test_repeated_operator_request_keeps_the_live_reassessment(self):
        with patch('builtins.print'):
            main(['reconsider-attempts', str(self.instance)])
        self.runner.ingest_inputs()
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = self.runner.identity['pid']
            key = self.runner.producer('attempt')
            self.assertTrue(self.runner.dispatch(key))
            probe = self.runner.state['jobs'][key]['session']
            with patch('builtins.print'):
                main(['reconsider-attempts', str(self.instance)])
            self.runner.ingest_inputs()
            self.assertEqual(self.runner.state['attempt_dispatch_gate']['probe_session'], probe)
            self.assertFalse(self.runner.dispatch(self.runner.producer('attempt')))

    def test_merged_nodes_preserve_coverage(self):
        self.publish('rnew', self.reduction())
        model = replay(self.instance)
        previous = {'nodes': {'root': ['a'], 'Q': ['b']}}
        model['aliases']['Q'] = 'root'
        current = {'nodes': {'root': ['a', 'b']}}
        self.assertIsNone(opening_since(previous, current, model))

    def test_tampered_snapshot_cannot_suppress_dispatch(self):
        sid, session, job = self.report()
        folder = self.runner.session_dir(sid)
        value = read_json(folder / 'output/outcome.json')
        snapshot = folder / 'availability' / (value['availability']['snapshot'] + '.json')
        write_json(snapshot, {'epoch': 0, 'nodes': {}})
        self.runner.finish(sid, session)
        self.assertEqual(session['availability_report']['status'], 'invalid')
        self.assertEqual(job['status'], 'done')
        self.assertIsNone(self.runner.state['attempt_dispatch_gate'])

    def test_malformed_terminal_flag_retains_material_for_peer(self):
        sid, session, job = self.attempt()
        (self.runner.session_dir(sid) / 'output/outcome.json').write_text('{', encoding='utf-8')
        self.runner.finish(sid, session)
        self.assertEqual(self.runner.state['pipelines'][job['pipeline']]['stage'], 'peer')

    def test_check_command_reports_transport_errors_through_its_exit_code(self):
        sid, _, _ = self.report()
        folder = self.runner.session_dir(sid)
        script = Path(__file__).resolve().parents[1] / 'check.py'

        def check():
            result = subprocess.run([sys.executable, '-B', str(script), str(folder)], capture_output=True)
            return result.returncode, json.loads(result.stdout.decode('utf-8'))

        self.assertEqual(check(), (0, {'ok': True, 'errors': []}))
        value = read_json(folder / 'output/outcome.json')
        # A malformed token and a well-formed token this session never retained receive the same diagnosis.
        for token in ('not-a-token', '0' * 64):
            with self.subTest(token=token):
                value['availability']['snapshot'] = token
                write_json(folder / 'output/outcome.json', value)
                code, report = check()
                self.assertEqual((code, report['ok']), (1, False))
                self.assertIn('token returned by updates', report['errors'][0])


if __name__ == '__main__':
    import unittest
    unittest.main()
