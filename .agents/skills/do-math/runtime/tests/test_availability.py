"""No-work exits, state-dependent dispatch suppression and one-at-a-time reassessment."""
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from availability import opening_since, snapshot_token
from check import check_session
from coordination import updates
from knowledge import replay
from runner import Runner, main
from runtime_support import read_json, write_json
from support import SUM_SUCC, SUM_ZERO, ScenarioCase, module_text, record_text, take, theorem


class AvailabilityTests(ScenarioCase):
    def setUp(self):
        super().setUp()
        self.configure(max_sessions=8)  # the occupying attempts of these tests leave room for further launches
        self.runner = Runner(self.instance, self.skill)
        self.serial = 0

    def attempt(self, role='attempt'):
        """A producing session that has ended cleanly after some activity."""
        self.serial += 1
        runner = self.runner
        sid = 'stest' + str(self.serial)
        self.session(runner, sid, role)  # as dispatch leaves it; the rest is what the CLI that ended left
        session = runner.state['sessions'][sid]
        session.update(model='codex/gpt-6.1-sol', provider='codex', started_at=time.time(), exit_code=0,
                       retained=True, retention={'cli_activity': True})
        runner.save()
        return sid, session, runner.state['jobs'][session['job']]

    def occupied(self):
        """Two attempts hold two parts of the root, the only element that remains."""
        first, _, job = self.attempt()
        a = take(self.runner.session_dir(first), 'Small.root', 'Left cases')
        self.assertTrue(a['registered'])
        second, _, _ = self.attempt()
        b = take(self.runner.session_dir(second), 'Small.root', 'Right cases',
                 {a['section']['id']: 'Different cases'})
        self.assertTrue(b['registered'])
        return job['pipeline'], a['section']['id'], b['section']['id']

    def report(self, availability=True):
        """An attempt that found nothing to take on, with or without the report that everything is occupied."""
        sid, session, job = self.attempt()
        folder = self.runner.session_dir(sid)
        value = {'disposition': 'no_research'}
        if availability:
            value['availability'] = {'status': 'all_unresolved_work_occupied',
                                     'snapshot': updates(folder)['availability_snapshot']}
        write_json(folder / 'output/outcome.json', value)
        return sid, session, job

    def reduce(self):
        """Publish a proof of the root that names two statements without a proof: new work that remains."""
        folder = self.candidate(
            modules={'Small/Parts.lean': module_text(theorem('sumZero', SUM_ZERO) + '\n\n' + theorem('sumSucc', SUM_SUCC))},
            replace={'Small.root': self.root_text(uses=['sumZero', 'sumSucc'])}, imports={'Small.root': ['Small.Parts']},
            records={'Small/sumZero.md': record_text('The empty sum is zero.', weight='unit'),
                     'Small/sumSucc.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.', weight='unit'),
                     'Small/root.md': self.root_record()})
        self.publish(folder, engine=self.runner)

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

    def test_the_report_names_the_elements_that_remain_and_the_sections_on_each(self):
        _, left, right = self.occupied()
        sid, session, _ = self.report()
        folder = self.runner.session_dir(sid)
        token = read_json(folder / 'output/outcome.json')['availability']['snapshot']
        observed = read_json(folder / 'availability' / (token + '.json'))
        self.assertEqual(observed, {'epoch': 0, 'elements': {'Small.root': sorted([left, right])}})
        self.assertEqual(snapshot_token(observed), token)
        self.assertEqual(observed, self.runner.current_availability())
        self.runner.finish(sid, session)
        gate = self.runner.state['attempt_dispatch_gate']
        self.assertEqual((gate['mode'], gate['reported_by'], gate['snapshot'], gate['reason'], gate['baseline']),
                         ('suppressed', sid, token, 'all_unresolved_work_occupied', observed))
        self.assertEqual(session['availability_report'], {'status': 'accepted'})

    def test_valid_coverage_survives_restart_time_and_unrelated_publication(self):
        self.occupied()
        sid, session, _ = self.report()
        self.assertEqual(check_session(self.runner.session_dir(sid)), [])
        self.runner.finish(sid, session)
        self.assertFalse(self.runner.attempt_dispatch_ready())
        self.note('The sum grows by one odd number at a time.')
        self.runner = Runner(self.instance, self.skill)
        self.assertEqual(self.runner.model['sequence'], 1)
        with patch('runner.time.time', return_value=time.time() + 10**6):
            self.assertFalse(self.runner.attempt_dispatch_ready())
        third, _, _ = self.attempt()
        # Adding a section does not open work, even if a worker mistakenly reports overlap.
        write_json(self.runner.session_dir(third) / 'declaration.json',
                   {'sections': [{'id': 'new', 'element': 'Small.root', 'whole': False,
                                  'statement': 'More occupied cases', 'at': 1}]})
        self.assertFalse(self.runner.attempt_dispatch_ready())

    def test_release_allows_exactly_one_probe_until_it_registers(self):
        pipeline, _, other = self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        self.runner.state['pipelines'][pipeline]['stage'] = 'done'
        self.runner.save()
        self.assertTrue(self.runner.attempt_dispatch_ready())
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['reason'], 'ended_occupancy')
        key = self.runner.producer('attempt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = self.runner.identity['pid']
            self.assertTrue(self.runner.dispatch(key))
            second = self.runner.producer('attempt')
            self.assertFalse(self.runner.dispatch(second))
        probe = self.runner.state['jobs'][key]['session']
        self.runner = Runner(self.instance, self.skill)
        self.assertFalse(self.runner.attempt_dispatch_ready())
        self.assertTrue(take(self.runner.session_dir(probe), 'Small.root', 'Left cases',
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

    def test_a_bad_report_does_not_reopen_or_send_terminal_attempt_to_peer(self):
        sid, session, job = self.report()
        folder = self.runner.session_dir(sid)
        value = read_json(folder / 'output/outcome.json')
        # The report as updates gave it passes. Each refusal changes one thing of it, and the check names that thing.
        self.assertEqual(check_session(folder), [])
        for message, changed in (('unknown availability status', {'status': 'some_work_is_free'}),
                                 ('availability needs exactly the fields status and snapshot, and no others',
                                  {'note': 'Nothing else was looked at.'})):
            with self.subTest(message=message):
                write_json(folder / 'output/outcome.json', {**value, 'availability': {**value['availability'], **changed}})
                self.assertEqual(check_session(folder), [message])
        value['availability']['snapshot'] = '../not-a-token'
        write_json(folder / 'output/outcome.json', value)
        self.assertEqual(check_session(folder), ['availability.snapshot must be a token returned by updates'])
        self.runner.finish(sid, session)
        self.assertEqual(job['status'], 'done')
        self.assertEqual(session['availability_report']['status'], 'invalid')
        self.assertEqual(len(self.runner.state['jobs']), 1)

    def test_claimed_or_interrupted_work_cannot_opt_out(self):
        for kind in ('claimed', 'interrupted', 'refused', 'occupied_question', 'explorer_reports_availability',
                     'other_disposition'):
            with self.subTest(kind=kind):
                explorer = kind in ('occupied_question', 'explorer_reports_availability')
                sid, session, job = self.attempt('explore' if explorer else 'attempt')
                folder = self.runner.session_dir(sid)
                write_json(folder / 'output/outcome.json', {'disposition': 'no_research'})
                if kind == 'claimed':
                    write_json(folder / 'declaration.json', {'sections': [
                        {'id': sid + '-1', 'element': 'Small.root', 'whole': True, 'statement': None,
                         'new': None, 'reasons': {}, 'at': 1}], 'at': 1})
                elif kind == 'occupied_question':
                    write_json(folder / 'declaration.json', {'question': {'id': 'q0', 'at': 1, 'by': 'runner'}, 'at': 1})
                elif kind == 'explorer_reports_availability':
                    write_json(folder / 'output/outcome.json', {'disposition': 'no_research', 'availability': {
                        'status': 'all_unresolved_work_occupied', 'snapshot': '0' * 64}})
                elif kind == 'other_disposition':
                    # Only no_research closes the pipeline; any other disposition leaves the research for peer.
                    write_json(folder / 'output/outcome.json', {'disposition': 'research_done'})
                elif kind == 'interrupted':
                    session['exit_code'] = 1
                elif kind == 'refused':
                    session['refusal'] = {'reason': 'usage_limit'}
                self.runner.finish(sid, session)
                self.assertEqual(self.runner.state['pipelines'][job['pipeline']]['stage'], 'peer')

    def test_new_work_and_reopening_trigger_but_an_accepted_proof_does_not(self):
        self.occupied()
        sid, session, _ = self.report()
        self.runner.finish(sid, session)
        # The root's proof is accepted. Nothing remains, and work that went away opens nothing.
        self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.',
                           engine=self.runner)
        self.assertEqual(self.runner.model['remaining'], [])
        self.assertFalse(self.runner.attempt_dispatch_ready())
        # A finding withdraws that proof. The root is work that remains again, which is a new opportunity
        # although the same sections still stand on it.
        self.event('v1', 'review', {'feedback': 'feedback.md', 'concerns': [], 'findings': [{
            'concerns': [], 'status': 'confirmed', 'reason': 'The step fails at zero.', 'invalidates': ['Small.root']}]})
        self.runner.model = replay(self.instance)
        self.assertEqual(self.runner.model['remaining'], ['Small.root'])
        self.assertTrue(self.runner.attempt_dispatch_ready())
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['reason'], 'new_or_reopened_element')
        # A proof of the root that names statements without a proof brings new work.
        self.runner.state['attempt_dispatch_gate']['mode'] = 'suppressed'
        self.reduce()
        self.assertEqual(self.runner.model['remaining'], ['Small.sumSucc', 'Small.sumZero'])
        self.assertTrue(self.runner.attempt_dispatch_ready())
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['reason'], 'new_or_reopened_element')

    def test_new_work_makes_a_delayed_report_stale(self):
        self.occupied()
        sid, session, _ = self.report()
        self.reduce()
        self.runner.finish(sid, session)
        self.assertEqual(session['availability_report']['status'], 'stale')
        self.assertIsNone(self.runner.state['attempt_dispatch_gate'])

    def test_operator_reconsideration_rejects_older_reports_and_preserves_stop(self):
        self.occupied()
        sid, session, _ = self.report()
        (self.instance / 'control/STOP').touch()
        with patch('builtins.print'):
            self.assertEqual(main(['reconsider-attempts', str(self.instance)]), 0)
        self.runner.ingest_inputs()
        epoch = self.runner.state['attempt_availability_epoch']
        self.assertEqual(epoch, 1)
        self.runner.ingest_inputs()
        self.assertEqual(self.runner.state['attempt_availability_epoch'], epoch)
        self.runner.finish(sid, session)
        self.assertEqual(session['availability_report']['status'], 'stale')
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['mode'], 'reassess')
        self.assertEqual(self.runner.state['attempt_dispatch_gate']['reason'], 'operator_request')
        self.assertTrue((self.instance / 'control/STOP').exists())

    def test_suppression_stops_pending_attempt_and_fills_free_questions_with_explorers(self):
        self.assertEqual(self.runner.settings['launch_interval'], 0)  # launch spacing has its own test
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
        # Occupied elements renew the request after each launch; it waits for a free question.
        self.assertTrue(self.runner.state['explore_requested'])
        self.questions('qops', [{'id': 'op-scale', 'statement': 'Why do the methods stall at the same scale?',
                                 'grounds': 'Several approaches stop there.'},
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

    def test_tampered_snapshot_cannot_suppress_dispatch(self):
        sid, session, job = self.report()
        folder = self.runner.session_dir(sid)
        value = read_json(folder / 'output/outcome.json')
        snapshot = folder / 'availability' / (value['availability']['snapshot'] + '.json')
        write_json(snapshot, {'epoch': 0, 'elements': {}})
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


class OpeningTests(unittest.TestCase):
    """availability.opening_since on views written by hand; no instance is needed."""

    def test_opening_is_new_remaining_work_or_an_ended_occupation(self):
        observed = {'elements': {'Small.root': ['a', 'b'], 'Small.sumZero': ['c']}}
        self.assertIsNone(opening_since(observed, observed))
        # A further section, or an element that is no longer work that remains, opens nothing.
        self.assertIsNone(opening_since(observed, {'elements': {'Small.root': ['a', 'b', 'd'], 'Small.sumZero': ['c']}}))
        self.assertIsNone(opening_since(observed, {'elements': {'Small.root': ['a', 'b']}}))
        self.assertEqual(opening_since(observed, {'elements': {'Small.root': ['a'], 'Small.sumZero': ['c']}}),
                         'ended_occupancy')
        self.assertEqual(opening_since(observed, {'elements': {**observed['elements'], 'Small.sumSucc': ['e']}}),
                         'new_or_reopened_element')


if __name__ == '__main__':
    unittest.main()
