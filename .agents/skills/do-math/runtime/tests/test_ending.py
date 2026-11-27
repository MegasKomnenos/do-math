import json
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from cli_adapter import Command
from coordination import board, session_live
from ending import request_prompt, run_turn
from launch import open_messages, worker_command
from runner import Runner, main
from runtime_support import alive, process_identity, read_json, session_host, write_json
from settings import defaults, validate
from support import InstanceCase, take

RUNTIME = Path(__file__).resolve().parents[1]

# A deterministic CLI conversation, used only by these tests. It stands in for the external CLI that
# the session host launches for every turn: it reads work/ending-test.json for what the test wants
# of this run, counts its turns in work/turns.jsonl, and speaks the Codex stream unless told to speak
# Claude's. A peer leaves a candidate change as a peer does: its files in output/ and the receipt of
# commands.prepare for exactly those files (a change without Lean is prepared without a build).
CLI = r'''
import json
import os
from pathlib import Path
import sys
import time

session = Path.cwd()
config = json.loads((session / 'work/ending-test.json').read_text())
sys.stdin.reconfigure(encoding='utf-8')  # the host hands over the bytes of a UTF-8 file, whatever the locale
prompt = sys.stdin.read()
history = session / 'work/turns.jsonl'
number = len(history.read_text().splitlines()) if history.exists() else 0
with history.open('a', encoding='utf-8') as stream:
    stream.write(json.dumps({'turn': number, 'prompt': prompt}) + '\n')
identity = '01234567-89ab-cdef-0123-456789abcdef'
if config.get('change_identity_at') == number:
    identity = 'fedcba98-7654-3210-fedc-ba9876543210'
if config.get('claude_stream'):
    print(json.dumps({'type': 'system', 'subtype': 'init', 'session_id': identity}), flush=True)
elif not config.get('omit_identity'):
    print(json.dumps({'type': 'thread.started', 'thread_id': identity}), flush=True)
print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message',
                  'text': f'Retained mathematical work from turn {number}.'}}), flush=True)
(session / 'output/report.md').write_text(f'Research through turn {number}.', encoding='utf-8')
inp = json.loads((session / 'input.json').read_text(encoding='utf-8'))
if inp['role'] == 'peer':
    sys.path.insert(0, sys.argv[1])
    from canon_tool import build_candidate
    from runtime_support import write_json
    write_json(session / 'output/change.json', {'title': 'Retained investigation',
                                                'description': 'A developed contribution.'})
    write_json(session / 'output/prepared.json', build_candidate(
        inp['instance'], inp['session'], session / 'output', session / 'work/prepare', 64, None, 'peer'))
if inp['role'] == 'review' and number >= config.get('assess_at', 0):
    # A reviewer leaves its assessment in the turn in which it has its sub-reviews; before that turn, none.
    (session / 'output/feedback.md').write_text('The questioned proof was examined.', encoding='utf-8')
    (session / 'output/assessment.json').write_text(json.dumps({'feedback': 'feedback.md', 'findings': [],
                                                                'concerns': []}))
if number in config.get('context_at', []):
    # A Claude turn in which a request of the session itself has reached the size at which the host sends its
    # message. The CLI's hook would hand the message over with the next batch of tool calls; here the session
    # is taken to have it once it waits, and answers the request the host opened when the test says how.
    (session / 'work/compaction-off').write_text(os.environ.get('DISABLE_AUTO_COMPACT', ''), encoding='utf-8')
    print(json.dumps({'type': 'assistant', 'session_id': identity, 'parent_tool_use_id': None, 'message': {
        'role': 'assistant', 'content': [], 'usage': {
            'input_tokens': 5, 'cache_creation_input_tokens': 1000, 'cache_read_input_tokens': 811_340}}}),
          flush=True)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not list((session / 'messages').glob('*.json')):
        time.sleep(.02)
    if config.get('context_basis'):
        asked = json.loads((session / 'end-request.json').read_text(encoding='utf-8'))
        (session / 'output/end-decision.json').write_text(json.dumps({
            'request_id': asked['id'], 'decision': 'end', 'basis': config['context_basis'],
            'explanation': 'Answered in the turn in which the message came.'}))
if number in config.get('context_limit_at', []):
    # The Claude CLI's own stream when, with automatic compaction off, the next request no longer fits the window.
    print(json.dumps({'type': 'assistant', 'session_id': identity, 'error': 'invalid_request',
                      'is_api_error_message': True,
                      'message': {'model': '<synthetic>', 'role': 'assistant',
                                  'content': [{'type': 'text', 'text': 'Prompt is too long'}]}}), flush=True)
    print(json.dumps({'type': 'result', 'subtype': 'success', 'is_error': True, 'session_id': identity,
                      'stop_reason': 'stop_sequence', 'terminal_reason': 'blocking_limit',
                      'result': 'Prompt is too long'}), flush=True)
    raise SystemExit(1)
if config.get('hold_at') == number:
    # A turn still running when the operator ends the session; only termination ends it early.
    (session / 'work/holding').write_text('', encoding='utf-8')
    time.sleep(120)
if config.get('refuse_at') == number:
    print(json.dumps({'type': 'error', 'message': "You've hit your usage limit. Try again later."}), flush=True)
    raise SystemExit(config.get('refuse_exit', 1))
if config.get('fail_at') == number:
    raise SystemExit(2)
if number in config.get('output_limit_at', []):
    # The Claude CLI's own stream when one response reaches the output-token cap.
    message = ("API Error: Claude's response exceeded the 64000 output token maximum. "
               "To configure this behavior, set the CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable.")
    print(json.dumps({'type': 'assistant', 'session_id': identity, 'error': 'max_output_tokens',
                      'is_api_error_message': True, 'api_error': 'max_output_tokens',
                      'message': {'model': '<synthetic>', 'role': 'assistant',
                                  'content': [{'type': 'text', 'text': message}]}}), flush=True)
    print(json.dumps({'type': 'result', 'subtype': 'success', 'is_error': True, 'session_id': identity,
                      'api_error': 'max_output_tokens', 'terminal_reason': 'api_error',
                      'result': message}), flush=True)
    raise SystemExit(1)
if config.get('no_research'):
    (session / 'output/outcome.json').write_text('{"disposition":"no_research"}')
if config.get('decide_unasked') and not number:
    # A decision the session wrote in its first turn, before the host had asked for one.
    (session / 'output/end-decision.json').write_text(json.dumps({
        'request_id': 'no request yet', 'decision': 'end', 'basis': 'task_completed',
        'explanation': 'Decided before being asked.'}))
if number:
    request = json.loads((session / 'end-request.json').read_text(encoding='utf-8'))
    target = session / 'output/end-decision.json'
    if config.get('malformed_at') == number:
        target.write_text('{broken')
    elif config.get('stale_at') == number:
        target.write_text(json.dumps({'request_id': 'old-request', 'decision': 'end',
                                     'basis': 'task_completed', 'explanation': 'Stale decision.'}))
    elif number >= config.get('end_after', 100):
        target.write_text(json.dumps({'request_id': request['id'], 'decision': 'end',
                                     'basis': config.get('basis', 'no_way_forward'),
                                     'explanation': config.get('explanation',
                                                               'The scripted investigation has reached its endpoint.'),
                                     **config.get('extra_fields', {})}))
'''


# These tests run the session host inside the test process. The real host puts its own process into a
# job that nothing can leave (runtime_support.contain_session_processes), and a process in such a job can
# no longer start a Lean broker (lean_broker.ensure_broker): every later test of the same run that builds
# through a broker would wait for one and fail. Here a stand-in answers for the containment, and the host
# is checked for asking it before its first turn and recording the answer; the containment itself is
# tested on real host processes in test_containment.
CONTAINMENT = patch('runtime_support.contain_session_processes', return_value={'contained': True})


def setUpModule():
    CONTAINMENT.start()


def tearDownModule():
    CONTAINMENT.stop()


class EndingTests(InstanceCase):
    def prepare(self, maximum=3, role='attempt', config=None, task=None):
        engine = Runner(self.instance, self.skill)
        engine.settings['max_end_resumptions'] = maximum
        engine.settings['roles'] = {}  # the scripted CLI speaks the Codex stream for every role
        if role == 'review':
            # A comprehensive review, unless the test gives the assignment of a candidate's review.
            key = engine.enqueue('review', task or {'kind': 'comprehensive', 'concerns': [], 'conflicts': [],
                                                    'purpose': 'Examine the questioned proof.'})
        else:
            key = engine.producer('attempt' if role == 'peer' else role,
                                  {'element': 'Small.root', 'previous_changes': []} if role == 'formalizer' else None)
        if role == 'peer':
            pipeline = engine.state['jobs'][key]['pipeline']
            engine.state['jobs'][key]['status'] = 'done'
            engine.state['pipelines'][pipeline].update(role='attempt', stage='peer', producer='source')
            key = engine.enqueue('peer', {'source': str(self.instance / 'sessions/source'), 'source_role': 'attempt',
                                          'element': None, 'sections': [], 'question': None}, pipeline)
        with patch('runner.subprocess.Popen') as host, patch('runner.worker_command') as build:
            host.return_value.pid = engine.identity['pid']
            build.return_value = self.command(None, None, None, self.instance)
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        directory = engine.session_dir(sid)
        launch = read_json(directory / 'launch.json')
        launch['command']['cwd'] = str(directory)
        write_json(directory / 'launch.json', launch)
        write_json(directory / 'work/ending-test.json', config or {})
        if role == 'attempt' and not (config or {}).get('no_research'):
            self.assertTrue(take(directory, 'Small.root')['registered'])
        return engine, sid, directory

    @staticmethod
    def command(executable, model, effort, session, *args, **kwargs):
        return Command('codex', [sys.executable, '-B', '-c', CLI, str(RUNTIME)], Path(session))

    def run_host(self, directory):
        with patch('ending.worker_command', side_effect=self.command):
            self.assertEqual(session_host(directory), 0)
        # The host contains its session before the first turn (runtime_support.contain_session_processes)
        # and leaves the answer in the session folder.
        receipt = read_json(directory / 'process-job.json')
        self.assertIs(receipt['contained'], True)
        self.assertLessEqual(receipt['at'], read_json(directory / 'turn-termination.json')['result']['invocation_started_at'])
        return read_json(directory / 'end-check.json')

    def waiting(self, directory, status):
        """The host's end-check record once it reports the given status, looked for over at most ten seconds."""
        path = directory / 'end-check.json'
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not (path.exists() and read_json(path)['status'] == status):
            time.sleep(.05)
        record = read_json(path)
        self.assertEqual(record['status'], status)
        return record

    def resume_text(self, role):
        """The text of a role for a resumed turn, as the host puts it into the prompt of such a turn.

        Read as the tests read a prompt, with the line endings of the file turned into `\\n`, so that the
        two compare in a tree that is checked out with either line ending."""
        return (self.skill / 'resume' / (role + '.md')).read_text(encoding='utf-8-sig').strip()

    def test_worker_end_resumes_exact_conversation_and_preserves_context(self):
        for role in ('attempt', 'formalizer', 'explore', 'peer'):
            with self.subTest(role=role):
                engine, sid, directory = self.prepare(role=role, config={'end_after': 1})
                pack = (directory / 'pack.md').read_bytes()
                declaration_path = directory / 'declaration.json'
                declaration = declaration_path.read_bytes() if declaration_path.exists() else None
                with patch('ending.worker_command', side_effect=self.command) as resume:
                    session_host(directory)
                self.assertEqual(resume.call_count, 1)
                self.assertEqual(resume.call_args.kwargs['resume_id'], '01234567-89ab-cdef-0123-456789abcdef')
                state = read_json(directory / 'end-check.json')
                self.assertEqual(state['authorization']['source'], 'worker')
                self.assertEqual(state['authorization']['basis'], 'no_way_forward')
                self.assertEqual(state['resumptions'], 1)
                self.assertEqual(pack, (directory / 'pack.md').read_bytes())
                # The CLI of the first turn had the pack itself on its standard input, below the opening lines of
                # the first prompt (context.assemble): the host hands over the prompt as the runner wrote it.
                first = json.loads((directory / 'work/turns.jsonl').read_text().splitlines()[0])
                self.assertTrue(first['prompt'].endswith('\n\n' + pack.decode('utf-8')))
                self.assertEqual(declaration, declaration_path.read_bytes() if declaration_path.exists() else None)
                # The resumed turn was given the text of its role for a resumed turn and, as a role that ends on
                # a decision is, the ID of the request that its decision answers.
                prompt = (directory / 'turns/0001/prompt.txt').read_text(encoding='utf-8')
                self.assertIn(self.resume_text(role), prompt)
                self.assertIn(read_json(directory / 'turns/0001/request.json')['id'], prompt)
                self.assertTrue((directory / 'turns/0001/turn-termination.json').is_file())
                # The resumed turn put the receipt of its own CLI in the place of the first turn's: the runner
                # and kill-session find the running CLI through the session's process.json.
                self.assertEqual(read_json(directory / 'process.json'),
                                 read_json(directory / 'turns/0001/process.json'))
                # Runner restart sees the same logical session, then collects it once.
                engine = Runner(self.instance, self.skill)
                s = engine.state['sessions'][sid]
                s.update(read_json(directory / 'exit.json'))
                s.update(host=None, cli=None)
                engine.finish(sid, s)
                engine.finish(sid, s)
                pipeline = engine.state['jobs'][s['job']]['pipeline']
                self.assertEqual(engine.state['pipelines'][pipeline]['stage'], 'review' if role == 'peer' else 'peer')
                if role == 'peer':
                    self.assertEqual((directory / 'candidate/report.md').read_text(), 'Research through turn 1.')
                    self.assertEqual(read_json(directory / 'candidate/change.json')['title'], 'Retained investigation')
                    # The ending decision stays with its turn; it is not frozen into the candidate.
                    self.assertFalse((directory / 'candidate/end-decision.json').exists())
                    self.assertTrue((directory / 'turns/0001/submitted-end-decision.json').is_file())
                    self.assertEqual(len([j for j in engine.state['jobs'].values()
                                          if j['role'] == 'review' and j['pipeline'] == pipeline]), 1)
                self.assertEqual(len([j for j in engine.state['jobs'].values()
                                      if j['role'] == 'peer' and j['pipeline'] == pipeline]), 1)
                body = (directory / 'conversation.md').read_text(encoding='utf-8')
                self.assertIn('work from turn 0', body)
                self.assertIn('work from turn 1', body)
                self.assertEqual(len(s['retention']['streams']), 4)
                # Finish this role's pipeline so that the next role can take the root.
                engine.state['pipelines'][pipeline]['stage'] = 'done'
                engine.save()

    def test_a_review_whose_turn_ended_without_its_assessment_is_resumed_in_the_same_conversation(self):
        # The first turn ends as a reviewer's does while the sub-reviewers it delegated to are still at work:
        # cleanly, and without an assessment. The second turn leaves one.
        engine, sid, directory = self.prepare(role='review', config={'assess_at': 1})
        with patch('ending.worker_command', side_effect=self.command) as resume:
            self.assertEqual(session_host(directory), 0)
        self.assertEqual(resume.call_count, 1)
        self.assertEqual(resume.call_args.kwargs['resume_id'], '01234567-89ab-cdef-0123-456789abcdef')
        state = read_json(directory / 'end-check.json')
        self.assertEqual((state['resumptions'], state['authorization']['source'], state['authorization']['basis']),
                         (1, 'runner', 'output_checked'))
        # The next turn was given the text of a review for a resumed turn and what the transport check found,
        # the missing assessment. It was asked for no end decision: its prompt carries no ID of a request.
        prompt = (directory / 'turns/0001/prompt.txt').read_text(encoding='utf-8')
        request = read_json(directory / 'turns/0001/request.json')
        self.assertIn('assessment.json', request['previous_error'])
        self.assertIn(request['previous_error'], prompt)
        self.assertIn(self.resume_text('review'), prompt)
        self.assertNotIn(request['id'], prompt)
        # The runner collects that same session with its assessment; no second review takes the assignment.
        engine = Runner(self.instance, self.skill)
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        engine.finish(sid, s)
        self.assertEqual(engine.state['jobs'][s['job']]['status'], 'done')
        self.assertEqual(len([j for j in engine.state['jobs'].values() if j['role'] == 'review']), 1)

    def test_a_review_that_never_leaves_its_assessment_goes_to_a_new_session_at_the_limit(self):
        engine, sid, directory = self.prepare(maximum=1, role='review', config={'assess_at': 9})
        with patch('ending.worker_command', side_effect=self.command):
            self.assertEqual(session_host(directory), 0)
        state = read_json(directory / 'end-check.json')
        self.assertEqual((state['resumptions'], state['authorization']['basis']), (1, 'resumption_limit'))
        engine = Runner(self.instance, self.skill)
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        engine.finish(sid, s)
        job = engine.state['jobs'][s['job']]
        self.assertEqual((s['status'], job['status']), ('failed', 'pending'))
        self.assertIn('assessment.json', job['last_error'])

    def test_a_review_whose_candidate_changed_is_left_to_the_runner_without_a_further_turn(self):
        # Restoring a candidate that changed after the review was assigned is the runner's work, so the host
        # resumes nothing for that one finding of the transport check and names it in the authorization.
        # What the runner then does with the candidate is tested in test_publication.
        candidate = self.root / 'candidate'
        candidate.mkdir()
        (candidate / 'report.md').write_text('The candidate as it stands now.', encoding='utf-8')
        _, _, directory = self.prepare(role='review', config={'assess_at': 9}, task={
            'kind': 'candidate', 'candidate': str(candidate),
            'candidate_hashes': {'report.md': 'the hash fixed when the review was assigned'}})
        with patch('ending.worker_command', side_effect=self.command) as resume:
            self.assertEqual(session_host(directory), 0)
        resume.assert_not_called()
        authorization = read_json(directory / 'end-check.json')['authorization']
        self.assertEqual((authorization['source'], authorization['basis'], authorization['explanation'],
                          authorization['resumptions']),
                         ('runner', 'output_checked', 'candidate changed after review assignment', 0))

    def test_guidance_edits_reach_next_turn_without_restarting_host(self):
        self.changes_guides = True  # this test rewrites two resume texts, so it works on its own copy of the guides
        _, _, directory = self.prepare(maximum=2, role='explore')
        guidance = self.skill / 'resume'
        original_common = (guidance / 'common.md').read_bytes()
        original_role = (guidance / 'explore.md').read_bytes()
        def update_after_turn(session, folder, command, state):
            result = run_turn(session, folder, command, state)
            if Path(folder) == directory:
                (guidance / 'common.md').write_bytes(original_common + b'\nCommon update between turns.\n')
            else:
                (guidance / 'explore.md').write_bytes(original_role + b'\nRole update between turns.\n')
            return result
        with patch('ending.run_turn', side_effect=update_after_turn):
            state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        first = directory / 'turns/0001'
        second = directory / 'turns/0002'
        self.assertIn('Common update between turns.', (first / 'prompt.txt').read_text(encoding='utf-8'))
        self.assertNotIn('Role update between turns.', (first / 'prompt.txt').read_text(encoding='utf-8'))
        self.assertIn('Role update between turns.', (second / 'prompt.txt').read_text(encoding='utf-8'))
        self.assertEqual((first / 'guidance/explore.md').read_bytes(), original_role)
        self.assertIn(b'Role update between turns.', (second / 'guidance/explore.md').read_bytes())

    def test_limit_authorizes_end_instead_of_waiting_or_resuming_indefinitely(self):
        _, _, directory = self.prepare(maximum=2)
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        self.assertEqual(state['authorization']['source'], 'runner')
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertTrue(state['authorization']['authorized'])
        self.assertEqual(len((directory / 'work/turns.jsonl').read_text().splitlines()), 3)

    def test_zero_limit_authorizes_initial_exit_without_native_id(self):
        _, _, directory = self.prepare(maximum=0, config={'omit_identity': True})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 0)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')

    def test_stale_decision_is_not_reused_and_can_be_corrected(self):
        _, _, directory = self.prepare(config={'end_after': 1, 'stale_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        self.assertEqual(state['authorization']['source'], 'worker')
        first = read_json(directory / 'turns/0001/request.json')
        second = read_json(directory / 'turns/0002/request.json')
        self.assertNotEqual(first['id'], second['id'])
        self.assertIn('another reconsideration', second['previous_error'])
        self.assertEqual(read_json(directory / 'turns/0001/submitted-end-decision.json')['request_id'], 'old-request')

    def test_rejected_decision_is_not_reported_again_after_a_continuing_turn(self):
        _, _, directory = self.prepare(config={'stale_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertIn('another reconsideration', read_json(directory / 'turns/0002/request.json')['previous_error'])
        # Turn 2 continued without a decision; the rejected file remains only in turn 1's receipts.
        self.assertIsNone(read_json(directory / 'turns/0003/request.json')['previous_error'])
        self.assertFalse((directory / 'output/end-decision.json').exists())
        self.assertEqual(read_json(directory / 'turns/0001/submitted-end-decision.json')['request_id'], 'old-request')

    def test_a_decision_written_before_any_request_is_set_aside_and_the_session_is_asked(self):
        # A decision counts only as the answer to a request (reference/retained-work.md). One written in the
        # first turn is taken out of output/ unchecked, and the session is resumed to be asked.
        _, _, directory = self.prepare(maximum=1, config={'decide_unasked': True, 'end_after': 1})
        state = self.run_host(directory)
        self.assertEqual((state['resumptions'], state['authorization']['source']), (1, 'worker'))
        self.assertEqual(read_json(directory / 'submitted-end-decision.json')['request_id'], 'no request yet')
        self.assertFalse((directory / 'decision-check.json').exists())
        self.assertIsNone(read_json(directory / 'turns/0001/request.json')['previous_error'])

    def test_malformed_decision_still_ends_at_configured_limit(self):
        _, _, directory = self.prepare(maximum=1, config={'malformed_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertIn('not valid JSON', read_json(directory / 'turns/0001/decision-check.json')['error'])

    def test_availability_only_exit_skips_reconsideration(self):
        _, _, directory = self.prepare(config={'no_research': True})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'no_research')
        self.assertEqual(state['resumptions'], 0)

    def test_a_rejected_no_research_outcome_is_reported_to_the_next_turn(self):
        # An attempt that registered a section cannot close through no_research (reference/retained-work.md).
        # The host resumes it and names the reason, as the transport check would. The second turn leaves the
        # same outcome and a decision that answers another request, and the third turn is told both problems.
        _, _, directory = self.prepare(maximum=2, config={'no_research': True, 'stale_at': 1})
        self.assertTrue(take(directory, 'Small.root')['registered'])
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertIn('no_research is incompatible with registered sections',
                      read_json(directory / 'turns/0001/request.json')['previous_error'])
        told = read_json(directory / 'turns/0002/request.json')['previous_error']
        self.assertIn('no_research is incompatible with registered sections', told)
        self.assertIn('Ending decision check: ', told)
        self.assertIn('another reconsideration', told)

    def test_a_defect_of_the_program_met_while_an_opt_out_is_read_ends_the_host_and_is_not_told_to_the_session(self):
        # What a session wrote wrongly in outcome.json fails with a ValueError, and a file that cannot be read
        # with an OSError; the next turn is told either, as in the test above. A KeyError comes from the program's
        # own code, and no file of a session causes it. The host ends with it and resumes nothing, and the runner
        # collects the session as one whose host was lost
        # (test_host_loss_is_recorded_as_interruption_and_retained_work_reaches_peer).
        _, _, directory = self.prepare(maximum=1)
        with patch('ending.no_research_outcome', side_effect=KeyError('sections')), \
                patch('ending.worker_command', side_effect=self.command) as resume, self.assertRaises(KeyError):
            session_host(directory)
        resume.assert_not_called()
        self.assertIsNone(read_json(directory / 'end-check.json')['authorization'])
        self.assertFalse((directory / 'exit.json').exists())

    def test_refusal_is_interruption_not_worker_authorization(self):
        # The refusal in the turn's stream ends the session, whatever exit code the CLI gave the refused turn:
        # the host starts no further turn against a provider that has just refused one.
        for code in (1, 0):
            with self.subTest(exit_code=code):
                engine, sid, directory = self.prepare(config={'refuse_at': 1, 'refuse_exit': code})
                state = self.run_host(directory)
                self.assertEqual((state['authorization']['basis'], state['resumptions']), ('interrupted', 1))
                receipt = read_json(directory / 'turns/0001/turn-termination.json')
                self.assertEqual(receipt['refusal']['reason'], 'usage_limit')
                self.assertEqual(read_json(directory / 'exit.json')['exit_code'], code)
                self.assertEqual(len((directory / 'work/turns.jsonl').read_text().splitlines()), 2)
                pipeline = engine.state['jobs'][engine.state['sessions'][sid]['job']]['pipeline']
                engine.state['pipelines'][pipeline]['stage'] = 'done'
                engine.save()

    def prepare_claude(self, maximum=3, role='attempt', config=None):
        engine, sid, directory = self.prepare(maximum, role, {'claude_stream': True, **(config or {})})
        launch = read_json(directory / 'launch.json')
        launch['end_check']['provider'] = 'claude'
        write_json(directory / 'launch.json', launch)
        return engine, sid, directory

    def test_output_limit_resumes_same_conversation_with_the_reason(self):
        _, _, directory = self.prepare_claude(config={'output_limit_at': [0], 'end_after': 1})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 1)
        self.assertEqual(state['authorization']['source'], 'worker')
        self.assertEqual(state['authorization']['basis'], 'no_way_forward')
        self.assertEqual(read_json(directory / 'turn-termination.json')['result']['exit_code'], 1)
        request = read_json(directory / 'turns/0001/request.json')
        self.assertIn('exceeded the output-token limit', request['previous_error'])
        self.assertIn('exceeded the 64000 output token maximum', request['previous_error'])
        self.assertIn(request['previous_error'], (directory / 'turns/0001/prompt.txt').read_text(encoding='utf-8'))
        # The resumption continues the conversation the failed turn announced.
        self.assertEqual(state['conversation_id'], '01234567-89ab-cdef-0123-456789abcdef')

    def test_output_limit_during_reconsideration_keeps_decision_error_and_counts_resumption(self):
        _, _, directory = self.prepare_claude(config={'output_limit_at': [1], 'end_after': 2})

        def decided_before_the_limit(session, folder, command, state):
            result = run_turn(session, folder, command, state)
            if Path(folder).name == '0001':
                # What the session had written in the turn that then reached the limit: a decision nobody can read.
                (directory / 'output/end-decision.json').write_text('{broken', encoding='utf-8')
            return result

        with patch('ending.run_turn', side_effect=decided_before_the_limit):
            state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        self.assertEqual(state['authorization']['basis'], 'no_way_forward')
        self.assertIsNone(read_json(directory / 'turns/0001/request.json')['previous_error'])
        told = read_json(directory / 'turns/0002/request.json')['previous_error']
        self.assertIn('output-token limit', told)
        self.assertIn('Ending decision check: ', told)
        self.assertIn('not valid JSON', told)

    def test_output_limit_at_the_last_allowed_turn_hands_off_with_the_reason(self):
        engine, sid, directory = self.prepare_claude(maximum=1, config={'output_limit_at': [0, 1]})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 1)
        self.assertEqual(state['authorization']['source'], 'runner')
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertIn('output-token limit', state['authorization']['explanation'])
        # The producer's retained work still reaches peer even though its last CLI exit failed.
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        self.assertEqual(s['exit_code'], 1)
        engine.finish(sid, s)
        self.assertEqual(s['status'], 'ended')
        self.assertEqual(engine.state['pipelines'][engine.state['jobs'][s['job']]['pipeline']]['stage'], 'peer')

    def test_output_limit_at_the_last_allowed_peer_turn_sends_its_candidate_to_review(self):
        engine, sid, directory = self.prepare_claude(maximum=1, role='peer', config={'output_limit_at': [0, 1]})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        self.assertEqual(s['exit_code'], 1)
        engine.finish(sid, s)
        # The host's own end authorization is not an interruption: the candidate is frozen for
        # review instead of the stage being handed to a replacement peer.
        pipeline = engine.state['jobs'][s['job']]['pipeline']
        self.assertEqual(s['status'], 'ended')
        self.assertEqual(engine.state['pipelines'][pipeline]['stage'], 'review')
        self.assertTrue(read_json(directory / 'candidate/prepared.json')['ok'])
        self.assertEqual(read_json(directory / 'candidate/change.json')['title'], 'Retained investigation')

    def test_a_review_whose_turn_ended_at_the_output_limit_is_told_the_reason_and_what_the_check_found(self):
        # A review runs on Claude by default, where one response can reach the output-token cap. Its turn then
        # ends with a failed exit and without an assessment. The host resumes the same conversation and tells
        # it both things: why the turn ended and what the transport check found.
        _, _, directory = self.prepare_claude(role='review', config={'output_limit_at': [0], 'assess_at': 1})
        state = self.run_host(directory)
        self.assertEqual(read_json(directory / 'turn-termination.json')['result']['exit_code'], 1)
        self.assertEqual((state['resumptions'], state['authorization']['source'], state['authorization']['basis']),
                         (1, 'runner', 'output_checked'))
        told = read_json(directory / 'turns/0001/request.json')['previous_error']
        self.assertIn('exceeded the output-token limit', told)
        self.assertIn('The transport check of your output found: ', told)
        self.assertIn('assessment.json', told)
        self.assertNotIn('Ending decision check', told)

    def test_output_limit_is_resumable_only_for_the_claude_stream(self):
        _, _, directory = self.prepare(config={'output_limit_at': [0]})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'interrupted')
        self.assertEqual(state['resumptions'], 0)

    def test_failed_turn_is_interruption_not_worker_authorization(self):
        _, _, directory = self.prepare(config={'fail_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['source'], 'runner')
        self.assertEqual(state['authorization']['basis'], 'interrupted')
        self.assertEqual(state['resumptions'], 1)
        receipt = read_json(directory / 'turns/0001/turn-termination.json')
        self.assertEqual(receipt['result']['exit_code'], 2)
        self.assertIsNone(receipt['refusal'])

    def test_only_a_complete_decision_on_the_two_ending_bases_authorizes_a_worker_end(self):
        # reference/retained-work.md asks for exactly four fields, one of the two bases and an explanation
        # of the grounds; any other decision is rejected and the session continues to the limit.
        cases = (({'basis': 'task_completed'}, 'task_completed', None),
                 ({'basis': 'partial_result'}, 'resumption_limit', 'task_completed or no_way_forward'),
                 # The basis that hands a task over answers only the request of the host's message.
                 ({'basis': 'handed_over'}, 'resumption_limit', 'task_completed or no_way_forward.'),
                 ({'explanation': ' '}, 'resumption_limit', 'nonempty explanation'),
                 ({'extra_fields': {'confidence': 'high'}}, 'resumption_limit',
                  'request_id, decision, basis and explanation'))
        for decision, expected, error in cases:
            with self.subTest(decision=decision):
                engine, sid, directory = self.prepare(maximum=1, config={'end_after': 1, **decision})
                state = self.run_host(directory)
                self.assertEqual(state['authorization']['basis'], expected)
                found = read_json(directory / 'turns/0001/decision-check.json')['error']
                if error is None:
                    self.assertIsNone(found)
                else:
                    self.assertIn(error, found)
                pipeline = engine.state['jobs'][engine.state['sessions'][sid]['job']]['pipeline']
                engine.state['pipelines'][pipeline]['stage'] = 'done'
                engine.save()

    def test_missing_or_changed_identity_does_not_start_a_fresh_conversation(self):
        for config in ({'omit_identity': True}, {'change_identity_at': 1, 'end_after': 1}):
            engine, sid, directory = self.prepare(config=config)
            state = self.run_host(directory)
            self.assertEqual(state['authorization']['basis'], 'resume_unavailable')
            pipeline = engine.state['jobs'][engine.state['sessions'][sid]['job']]['pipeline']
            engine.state['pipelines'][pipeline]['stage'] = 'done'
            engine.save()

    def test_stop_holds_same_host_and_scope_until_resumed(self):
        engine, sid, directory = self.prepare(maximum=1)
        stop = self.instance / 'control/STOP'
        stop.touch()
        result = []
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=lambda: result.append(session_host(directory)), daemon=True)
            thread.start()
            try:
                self.assertEqual(self.waiting(directory, 'waiting_dispatch')['resumptions'], 0)
                self.assertTrue(thread.is_alive())
                self.assertTrue(session_live(engine.state, sid))
                self.assertEqual(board(self.instance)[0]['stage'], 'producing')
                restarted = Runner(self.instance, self.skill)
                restarted.collect()
                self.assertEqual(len(restarted.active()), 1)
                # The runner's state carries the record of a host that still holds its session, and `status`
                # returns that state: the wait behind the stop and the count of resumed turns show there
                # (reference/operations.md, Session hosts and continuation turns).
                self.assertEqual(read_json(restarted.state_path)['sessions'][sid]['end_check']['status'],
                                 'waiting_dispatch')
                self.assertFalse(any(j['role'] == 'peer' for j in restarted.state['jobs'].values()))
                stop.unlink()
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(result, [0])
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)

    def test_kill_session_ends_a_running_turn_and_retained_work_reaches_peer(self):
        # kill-session while a CLI turn is still running: the command terminates the identified CLI,
        # the host records an interruption without launching another turn, and the producer's
        # retained work goes to peer (reference/operations.md, Commands).
        engine, sid, directory = self.prepare(config={'hold_at': 0})
        errors = []
        def run():
            try:
                session_host(directory)
            except Exception as exc:
                errors.append(exc)
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline and not (
                        (directory / 'work/holding').exists() and (directory / 'process.json').exists()):
                    time.sleep(.05)
                cli = read_json(directory / 'process.json')['process']
                self.assertTrue(alive(cli))
                import io
                with patch('sys.stdout', new=io.StringIO()):
                    self.assertEqual(main(['kill-session', str(self.instance), sid]), 0)
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(errors, [])
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)
        self.assertFalse(alive(cli))
        state = read_json(directory / 'end-check.json')
        self.assertEqual((state['authorization']['basis'], state['resumptions']), ('interrupted', 0))
        self.assertEqual(len((directory / 'work/turns.jsonl').read_text().splitlines()), 1)
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        self.assertNotIn(s['exit_code'], (0, None))
        s.update(host=None, cli=None)
        engine.finish(sid, s)
        self.assertEqual(engine.state['pipelines'][engine.state['jobs'][s['job']]['pipeline']]['stage'], 'peer')

    def test_cancelled_peer_resumption_gets_a_replacement_instead_of_review(self):
        engine, sid, directory = self.prepare(role='peer')
        (self.instance / 'control/STOP').touch()
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=session_host, args=(directory,), daemon=True)
            thread.start()
            try:
                self.waiting(directory, 'waiting_dispatch')
                import io
                with patch('sys.stdout', new=io.StringIO()):
                    self.assertEqual(main(['kill-session', str(self.instance), sid]), 0)
                thread.join(10)
                self.assertFalse(thread.is_alive())
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)
        # The first turn exited cleanly with a structurally valid candidate, but the operator
        # cancelled the pending resumption: the peer stage is unfinished, not ready for review.
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        engine.finish(sid, s)
        # kill-session cancelled the pending resumption, so no further turn was launched.
        self.assertEqual((s['end_check']['authorization']['basis'], s['end_check']['resumptions']), ('interrupted', 0))
        self.assertFalse((directory / 'candidate').exists())
        job = engine.state['jobs'][s['job']]
        self.assertEqual((job['status'], s['status']), ('pending', 'failed'))
        self.assertIn(str(directory), job['task']['previous_partial_sessions'])
        self.assertFalse(any(j['role'] == 'review' for j in engine.state['jobs'].values()))

    def test_a_peer_whose_resumed_turn_failed_sends_the_candidate_it_had_prepared_to_review(self):
        # The first turn ended cleanly and left a prepared candidate; the turn in which the peer was to judge its
        # ending again failed, or the provider refused it. The host records an interruption, and the runner puts
        # the output to the transport check all the same. A candidate changed after it was prepared is refused,
        # and a replacement peer takes the stage with the error of the failed turn; a prepared one is frozen for
        # review. The refused turn comes last: the block it leaves on the provider holds back a later dispatch.
        for config, changed in (({'fail_at': 1}, True), ({'refuse_at': 1}, False)):
            with self.subTest(config=config):
                engine, sid, directory = self.prepare(role='peer', config=config)
                state = self.run_host(directory)
                self.assertEqual((state['authorization']['basis'], state['resumptions']), ('interrupted', 1))
                self.assertEqual(read_json(directory / 'turn-termination.json')['result']['exit_code'], 0)
                if changed:
                    (directory / 'output/report.md').write_text('Rewritten after the candidate was prepared.',
                                                                encoding='utf-8')
                s = engine.state['sessions'][sid]
                s.update(read_json(directory / 'exit.json'))
                s.update(host=None, cli=None)
                engine.finish(sid, s)
                job = engine.state['jobs'][s['job']]
                stage = engine.state['pipelines'][job['pipeline']]['stage']
                reviews = [j for j in engine.state['jobs'].values()
                           if j['role'] == 'review' and j['pipeline'] == job['pipeline']]
                if changed:
                    self.assertEqual((job['status'], s['status'], stage), ('pending', 'failed', 'peer'))
                    self.assertIn('exit_code=2', job['last_error'])
                    self.assertIn(str(directory), job['task']['previous_partial_sessions'])
                    self.assertFalse((directory / 'candidate').exists())
                    self.assertEqual(reviews, [])
                else:
                    self.assertEqual((job['status'], s['status'], stage), ('done', 'ended', 'review'))
                    self.assertEqual((directory / 'candidate/report.md').read_text(), 'Research through turn 1.')
                    self.assertTrue(read_json(directory / 'candidate/prepared.json')['ok'])
                    self.assertEqual(len(reviews), 1)
                    # The record still says what the host saw, and the refusal keeps its block on the provider.
                    self.assertEqual(s['end_check']['authorization']['basis'], 'interrupted')
                    self.assertEqual(engine.state['blocks']['provider:codex']['reason'], 'usage_limit')

    def test_a_peer_whose_host_is_lost_after_its_first_turn_sends_the_candidate_it_had_prepared_to_review(self):
        # The first turn ended cleanly and left a prepared candidate, and the host recorded the request of the turn
        # in which the peer judges its ending again. A host that is then lost, as every host is when the machine
        # goes down, writes no exit.json: while it waits to start that turn, or while the turn runs. The runner
        # records an interruption and puts the output to the transport check all the same, and the candidate is
        # frozen for review. A host lost before it recorded how the first turn ended has recorded no such request:
        # that peer is replaced, although the same candidate stands in its output. The host is lost here by an
        # error that leaves it at the point named, so the session folder holds what a host ended there leaves.
        from ending import wait_to_resume

        def lost(*args):
            raise RuntimeError('the host is lost')

        for point, kept in (('first turn', False), ('wait', True), ('resumed turn', True)):
            with self.subTest(point=point):
                engine, sid, directory = self.prepare(role='peer')

                def turn(session, folder, command, state):
                    if point == 'resumed turn' and Path(folder) != directory:
                        lost()
                    result = run_turn(session, folder, command, state)
                    if point == 'first turn':
                        lost()
                    return result

                with patch('ending.worker_command', side_effect=self.command), \
                        patch('ending.run_turn', side_effect=turn), \
                        patch('ending.wait_to_resume', side_effect=lost if point == 'wait' else wait_to_resume), \
                        self.assertRaisesRegex(RuntimeError, 'the host is lost'):
                    session_host(directory)
                self.assertFalse((directory / 'exit.json').exists())
                s = engine.state['sessions'][sid]
                s.update(host=None, cli=None)
                engine.finish(sid, s)
                job = engine.state['jobs'][s['job']]
                stage = engine.state['pipelines'][job['pipeline']]['stage']
                reviews = [j for j in engine.state['jobs'].values()
                           if j['role'] == 'review' and j['pipeline'] == job['pipeline']]
                self.assertEqual(s['end_check']['authorization']['basis'], 'interrupted')
                if kept:
                    self.assertEqual((job['status'], s['status'], stage), ('done', 'ended', 'review'))
                    self.assertEqual((directory / 'candidate/report.md').read_text(), 'Research through turn 0.')
                    self.assertTrue(read_json(directory / 'candidate/prepared.json')['ok'])
                    self.assertEqual(len(reviews), 1)
                else:
                    self.assertEqual((job['status'], s['status'], stage), ('pending', 'failed', 'peer'))
                    self.assertIn(str(directory), job['task']['previous_partial_sessions'])
                    self.assertFalse((directory / 'candidate').exists())
                    self.assertEqual(reviews, [])

    def test_another_sessions_provider_block_holds_resumption(self):
        engine, _, directory = self.prepare(maximum=1)
        engine.state['blocks']['provider:codex'] = {'until': time.time() + 60, 'reason': 'usage_limit'}
        engine.save()
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=session_host, args=(directory,), daemon=True)
            thread.start()
            try:
                self.assertEqual(self.waiting(directory, 'waiting_provider')['resumptions'], 0)
                engine.state['blocks'].clear()
                engine.save()
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(read_json(directory / 'end-check.json')['authorization']['basis'], 'resumption_limit')
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)

    def test_host_loss_is_recorded_as_interruption_and_retained_work_reaches_peer(self):
        engine, sid, directory = self.prepare()
        write_json(directory / 'end-check.json', {'maximum': 3, 'resumptions': 0,
                   'status': 'running', 'request': None, 'authorization': None})
        (directory / 'output/report.md').write_text('Retained interrupted mathematics.')
        s = engine.state['sessions'][sid]
        s.update(host=None, cli=None, exit_code=None)
        engine.finish(sid, s)
        self.assertEqual(s['end_check']['authorization']['basis'], 'interrupted')
        self.assertEqual(engine.state['pipelines'][engine.state['jobs'][s['job']]['pipeline']]['stage'], 'peer')

    def told(self, role='attempt', config=None):
        """A session on Claude that receives messages, as the runner launches one, with the scripted CLI."""
        engine, sid, directory = self.prepare_claude(role=role, config=config)
        open_messages(directory)
        return engine, sid, directory

    def collected(self, engine, sid, directory):
        """The session and its job once the runner has collected the ended session."""
        s = engine.state['sessions'][sid]
        s.update(read_json(directory / 'exit.json'))
        s.update(host=None, cli=None)
        engine.finish(sid, s)
        return s, engine.state['jobs'][s['job']]

    def relaunch(self, engine, launch):
        """Have the runner launch what waits, with the stand-ins of `prepare` for the host and the command."""
        with patch('runner.subprocess.Popen') as host, patch('runner.worker_command') as build:
            host.return_value.pid = engine.identity['pid']
            build.return_value = self.command(None, None, None, self.instance)
            return launch()

    def test_a_session_that_hands_its_task_over_is_continued_by_a_new_session_of_its_role(self):
        engine, sid, directory = self.told(config={'context_at': [0], 'context_basis': 'handed_over'})
        with patch('ending.worker_command', side_effect=self.command) as resume:
            self.assertEqual(session_host(directory), 0)
        # The message opened a request, and the decision of the same turn answers it: no turn follows.
        resume.assert_not_called()
        state = read_json(directory / 'end-check.json')
        self.assertEqual((state['authorization']['source'], state['authorization']['basis'], state['resumptions']),
                         ('worker', 'handed_over', 0))
        self.assertEqual(state['request']['context'], 812_345)
        (message,) = (directory / 'messages').glob('*.json')
        self.assertIn('Its request ID is ' + state['request']['id'], read_json(message)['text'])
        # The CLI of a session that is told when its context is nearly full runs with compaction off.
        self.assertEqual((directory / 'work/compaction-off').read_text(encoding='utf-8'), '1')
        s, job = self.collected(engine, sid, directory)
        pipeline = engine.state['pipelines'][job['pipeline']]
        # Nothing failed and nothing goes to a peer: the same job waits for its next session, with the folder
        # of this one, and the section stays held meanwhile.
        self.assertEqual((s['status'], job['status'], job['retries'], job['not_before'], pipeline['stage']),
                         ('ended', 'pending', 0, 0, 'producing'))
        self.assertEqual(job['task']['continues'], [str(directory)])
        self.assertEqual(engine.state['blocks'], {})
        self.assertFalse(any(j['role'] == 'peer' for j in engine.state['jobs'].values()))
        self.assertEqual(board(self.instance, engine.state)[0]['elements'], ['Small.root'])
        # The next session is launched although the task itself holds the one remaining element whole, which
        # keeps a new attempt from launching, and it is not counted as an attempt launch.
        launches = engine.state['attempt_launches']
        self.relaunch(engine, engine.dispatch_pending)
        self.assertEqual((job['status'], engine.state['attempt_launches']), ('running', launches))
        self.assertNotEqual(job['session'], sid)
        successor = engine.session_dir(job['session'])
        row = board(self.instance, engine.state)[0]
        self.assertEqual((row['session'], row['elements']), (job['session'], ['Small.root']))
        self.assertEqual(read_json(successor / 'input.json')['task']['continues'], [str(directory)])
        # The pack tells the new session where the report of the session before it is.
        self.assertIn(str(directory / 'output/report.md'), (successor / 'pack.md').read_text(encoding='utf-8'))
        # The task is handed over a second time. It then lists both folders, oldest first, and the session
        # that follows is pointed at the report of the second session and not at that of the first.
        second = job['session']
        launch = read_json(successor / 'launch.json')
        launch['command']['cwd'] = str(successor)
        launch['end_check']['provider'] = 'claude'
        write_json(successor / 'launch.json', launch)
        write_json(successor / 'work/ending-test.json',
                   {'claude_stream': True, 'context_at': [0], 'context_basis': 'handed_over'})
        open_messages(successor)
        self.assertEqual(self.run_host(successor)['authorization']['basis'], 'handed_over')
        s, job = self.collected(engine, second, successor)
        self.assertEqual(job['task']['continues'], [str(directory), str(successor)])
        self.relaunch(engine, engine.dispatch_pending)
        self.assertNotIn(job['session'], (None, sid, second))
        pack = (engine.session_dir(job['session']) / 'pack.md').read_text(encoding='utf-8')
        self.assertIn(str(successor / 'output/report.md'), pack)
        self.assertNotIn(str(directory / 'output/report.md'), pack)

    def test_a_handed_over_exploration_keeps_its_question_for_the_session_that_continues_it(self):
        engine, sid, directory = self.told(role='explore', config={'context_at': [0],
                                                                   'context_basis': 'handed_over'})
        self.run_host(directory)
        s, job = self.collected(engine, sid, directory)
        self.assertEqual((job['status'], job['task']['continues']), ('pending', [str(directory)]))
        # While the task waits for its next session, no other exploration is launched onto its question.
        self.assertNotIn('q0', engine.question_view(launching=True)['free'])
        self.assertTrue(self.relaunch(engine, lambda: engine.dispatch(job['id'])))
        successor = engine.session_dir(job['session'])
        self.assertEqual(job['task']['question'], 'q0')
        self.assertEqual(read_json(successor / 'declaration.json'), read_json(directory / 'declaration.json'))
        row = board(self.instance, engine.state)[0]
        self.assertEqual((row['session'], row['question']), (job['session'], 'q0'))

    def test_a_peer_that_hands_its_task_over_keeps_its_sections_for_the_peer_that_continues_it(self):
        engine, sid, directory = self.told(role='peer', config={'context_at': [0], 'context_basis': 'handed_over'})
        # A peer can register sections of its own; this one holds the whole root.
        self.assertTrue(take(directory, 'Small.root')['registered'])
        state = self.run_host(directory)
        self.assertEqual((state['authorization']['source'], state['authorization']['basis']), ('worker', 'handed_over'))
        s, job = self.collected(engine, sid, directory)
        pipeline = engine.state['pipelines'][job['pipeline']]
        # The stage is not over. The same job waits for its next peer, with the folder of this one; the candidate
        # this peer had prepared is not frozen, and nothing goes to review.
        self.assertEqual((s['status'], job['status'], job['retries'], pipeline['stage']), ('ended', 'pending', 0, 'peer'))
        self.assertEqual(job['task']['continues'], [str(directory)])
        self.assertFalse((directory / 'candidate').exists())
        self.assertFalse(any(j['role'] == 'review' for j in engine.state['jobs'].values()))
        self.assertTrue(self.relaunch(engine, lambda: engine.dispatch(job['id'])))
        # The next peer takes the peer's place in the pipeline. What the first peer registered goes on holding
        # its element, as after a peer that failed, and the pack names the report that a peer leaves in work/.
        self.assertEqual((pipeline['peer'], pipeline['previous_peers']), (job['session'], [sid]))
        [row] = board(self.instance, engine.state)
        self.assertEqual([(section['session'], section['whole']) for section in row['sections']], [(sid, True)])
        self.assertIn(str(directory / 'work/report.md'),
                      (engine.session_dir(job['session']) / 'pack.md').read_text(encoding='utf-8'))

    def test_an_ending_decided_in_answer_to_the_message_needs_no_further_turn(self):
        engine, sid, directory = self.told(config={'context_at': [0], 'context_basis': 'task_completed'})
        with patch('ending.worker_command', side_effect=self.command) as resume:
            self.assertEqual(session_host(directory), 0)
        resume.assert_not_called()
        authorization = read_json(directory / 'end-check.json')['authorization']
        self.assertEqual((authorization['source'], authorization['basis'], authorization['resumptions']),
                         ('worker', 'task_completed', 0))
        # The work is done, so it goes to a peer as after any ending the session decided.
        s, job = self.collected(engine, sid, directory)
        self.assertEqual((s['status'], job['status']), ('ended', 'done'))
        self.assertNotIn('continues', job['task'])
        self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'peer')

    def test_a_session_that_ended_its_turn_without_answering_the_message_is_asked_the_same_request_again(self):
        # The message is handed over with the results of tool calls, so a turn can end before the session has it.
        _, _, directory = self.told(config={'context_at': [0], 'end_after': 1, 'basis': 'handed_over'})
        state = self.run_host(directory)
        self.assertEqual((state['authorization']['source'], state['authorization']['basis'], state['resumptions']),
                         ('worker', 'handed_over', 1))
        # Sent once: the resumed turn holds the same request, under the ID the waiting message names.
        (message,) = (directory / 'messages').glob('*.json')
        text = read_json(message)['text']
        request_id = read_json(directory / 'turns/0001/request.json')['id']
        self.assertIn('Its request ID is ' + request_id, text)
        # The prompt of the resumed turn ends with the text of the message. What stands before it is what every
        # resumed turn of the role is asked: the text of the role, and the ID of the request to answer.
        prompt = (directory / 'turns/0001/prompt.txt').read_text(encoding='utf-8')
        self.assertTrue(prompt.endswith(text + '\n'))
        asked = prompt[:-len(text + '\n')]
        self.assertIn(self.resume_text('attempt'), asked)
        self.assertIn(request_id, asked)

    def test_a_turn_that_ends_at_the_limit_of_the_context_window_is_continued_from_the_files(self):
        for role in ('attempt', 'review'):
            with self.subTest(role=role):
                engine, sid, directory = self.told(role=role, config={'context_limit_at': [0], 'assess_at': 9})
                state = self.run_host(directory)
                # No provider and no model refused anything, and no further turn of a full conversation is started.
                self.assertEqual((state['authorization']['source'], state['authorization']['basis'],
                                  state['resumptions']), ('runner', 'context_limit', 0))
                self.assertIsNone(read_json(directory / 'turn-termination.json')['refusal'])
                s, job = self.collected(engine, sid, directory)
                self.assertEqual(s['exit_code'], 1)
                self.assertEqual((s['status'], job['status'], job['retries']), ('ended', 'pending', 0))
                self.assertEqual(job['task']['continues'], [str(directory)])
                self.assertNotIn('previous_error', job['task'])
                self.assertEqual(engine.state['blocks'], {})
        # A session that is sent no message keeps its compaction, and such an end of its turn is a failed turn.
        _, _, directory = self.prepare_claude(role='explore', config={'context_limit_at': [0]})
        self.assertEqual(self.run_host(directory)['authorization']['basis'], 'interrupted')

    def test_a_decision_written_before_the_turn_met_the_limit_of_the_window_ends_the_session(self):
        # The session answered the message with an ending, and the request after its answer no longer fitted.
        engine, sid, directory = self.told(config={'context_at': [0], 'context_basis': 'task_completed',
                                                   'context_limit_at': [0]})
        authorization = self.run_host(directory)['authorization']
        self.assertEqual((authorization['source'], authorization['basis']), ('worker', 'task_completed'))
        self.assertEqual(read_json(directory / 'decision-check.json')['decision']['basis'], 'task_completed')
        # The work is done: it goes to a peer, and no session of the role is launched to continue it.
        s, job = self.collected(engine, sid, directory)
        self.assertEqual((s['exit_code'], s['status'], job['status']), (1, 'ended', 'done'))
        self.assertNotIn('continues', job['task'])
        self.assertEqual(engine.state['pipelines'][job['pipeline']]['stage'], 'peer')

    def test_a_review_ends_on_a_decision_of_its_own_only_where_the_decision_hands_its_task_over(self):
        # A review writes no decision to end on: its session ends when its output passes the transport check. The
        # one decision of a review that its host takes is the answer to the message that hands the task over.
        engine, sid, directory = self.told(role='review', config={'context_at': [0], 'context_basis': 'handed_over',
                                                                  'assess_at': 9})
        state = self.run_host(directory)
        self.assertEqual((state['authorization']['source'], state['authorization']['basis'], state['resumptions']),
                         ('worker', 'handed_over', 0))
        s, job = self.collected(engine, sid, directory)
        # The assignment waits for its next review, which is told where this one left its report.
        self.assertEqual((s['status'], job['status'], job['retries']), ('ended', 'pending', 0))
        self.assertEqual(job['task']['continues'], [str(directory)])
        self.assertTrue(self.relaunch(engine, lambda: engine.dispatch(job['id'])))
        self.assertIn(str(directory / 'work/report.md'),
                      (engine.session_dir(job['session']) / 'pack.md').read_text(encoding='utf-8'))
        # A review that answers the message on another basis has not ended by that. This one left its assessment
        # in the same turn, so it ends as a review does, on the check of its output.
        _, _, directory = self.told(role='review', config={'context_at': [0], 'context_basis': 'task_completed'})
        authorization = self.run_host(directory)['authorization']
        self.assertEqual((authorization['source'], authorization['basis']), ('runner', 'output_checked'))


class EndingConfigurationTests(unittest.TestCase):
    def test_role_guidance_is_selected_and_invalid_templates_fail_before_delivery(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            guidance = Path(tmp) / 'resume'
            shutil.copytree(Path(__file__).resolve().parents[2] / 'resume', guidance)
            request = {'id': 'current-request', 'previous_error': 'Stale decision'}
            for role in ('attempt', 'formalizer', 'explore', 'peer'):
                prompt = request_prompt(request, role, guidance)
                self.assertIn((guidance / (role + '.md')).read_bytes().decode('utf-8-sig').strip(), prompt)
                self.assertIn('current-request', prompt)
                self.assertIn('Stale decision', prompt)
                self.assertNotIn('{{', prompt)
            # A review and an organizer are told what the transport check found; they are asked for no end decision.
            from ending import OUTPUT_ROLES
            self.assertEqual(set(OUTPUT_ROLES), {'review', 'organizer'})
            for role in OUTPUT_ROLES:
                prompt = request_prompt(request, role, guidance)
                self.assertIn((guidance / (role + '.md')).read_bytes().decode('utf-8-sig').strip(), prompt)
                self.assertIn('Stale decision', prompt)
                self.assertNotIn('current-request', prompt)
                self.assertNotIn('{{', prompt)
            (guidance / 'peer.md').unlink()
            with self.assertRaises(FileNotFoundError):
                request_prompt(request, 'peer', guidance)
            # A frame that lacks one of its markers, or holds one twice, is refused, and the refusal names the marker.
            for frame, role, markers in (('common.md', 'explore', ('{{role_guidance}}', '{{previous_error}}', '{{request_id}}')),
                                         ('output.md', 'review', ('{{role_guidance}}', '{{previous_error}}'))):
                installed = (guidance / frame).read_bytes()
                for marker in markers:
                    for changed in (installed.replace(marker.encode(), b''), installed + marker.encode()):
                        (guidance / frame).write_bytes(changed)
                        with self.assertRaises(ValueError) as refused:
                            request_prompt(request, role, guidance)
                        self.assertEqual(str(refused.exception), f'continuation {frame} needs exactly one {marker}')
                (guidance / frame).write_bytes(installed)
            # A role text that holds nothing is refused before the placeholders are looked at.
            (guidance / 'attempt.md').write_bytes(b' \n')
            with self.assertRaises(ValueError) as refused:
                request_prompt(request, 'attempt', guidance)
            self.assertEqual(str(refused.exception), 'continuation guidance must not be empty')

    def test_limit_validation(self):
        self.assertEqual(defaults()['max_end_resumptions'], 1000)
        for value in (0, 1, 8, 1000):
            self.assertEqual(validate({'max_end_resumptions': value})['max_end_resumptions'], value)
        for value in (-1, True, 1.5, '3', None):
            with self.assertRaises(ValueError):
                validate({'max_end_resumptions': value})

    def test_resume_cli_keeps_isolation_and_context_options(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            identity = '01234567-89ab-cdef-0123-456789abcdef'
            for model in ('codex/gpt-6.1-sol', 'claude/opus'):
                command = worker_command('cli', model, 'xhigh', tmp, resume_id=identity)
                if command.provider == 'codex':
                    self.assertEqual(command.argv[-3:], ['resume', identity, '-'])
                    self.assertIn('--ignore-user-config', command.argv)
                    self.assertIn('model_context_window=1000000', command.argv)
                else:
                    self.assertEqual(command.argv[-2:], ['--resume', identity])
                    self.assertIn('--strict-mcp-config', command.argv)
                    self.assertIn('opus[1m]', command.argv)

    def test_a_stream_that_names_two_conversations_or_no_valid_one_gives_the_host_none_to_resume(self):
        # supervise records resume_unavailable for either refusal, so no other conversation is resumed in the
        # session's name. The stream file is what the CLI wrote; conversation_id is called as supervise calls it.
        import json
        import tempfile
        from ending import conversation_id
        first, second = '01234567-89ab-cdef-0123-456789abcdef', 'fedcba98-7654-3210-fedc-ba9876543210'
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)

            def announce(*identities):
                (folder / 'cli.stdout.jsonl').write_text(
                    '\n'.join(json.dumps({'type': 'thread.started', 'thread_id': identity}) for identity in identities),
                    encoding='utf-8')

            self.assertIsNone(conversation_id(folder, 'codex'))
            # One conversation announced twice, in two spellings, is one identity.
            announce(first.upper(), first)
            self.assertEqual(conversation_id(folder, 'codex'), first)
            for identities, message in (((first, second), 'CLI returned multiple conversation identities'),
                                        (('not-an-identity',), 'CLI returned an invalid conversation identity')):
                announce(*identities)
                with self.assertRaises(ValueError) as refused:
                    conversation_id(folder, 'codex')
                self.assertEqual(str(refused.exception), message)

    def test_a_waiting_host_parses_the_runner_state_again_only_when_its_file_has_changed(self):
        # A host can wait behind a dispatch stop or an availability block for hours, and the runner's state,
        # megabytes in a long run, changes far less often than the wait looks at it. Only the clock of the
        # wait is replaced, so the test waits for nothing: each pause is one step of what happens around it.
        import tempfile
        from types import SimpleNamespace
        from ending import wait_to_resume
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / 'instance'
            session = instance / 'sessions/s1'
            for folder in (session, instance / 'control', instance / 'runner'):
                folder.mkdir(parents=True)
            # The block is on the session's model; test_another_sessions_provider_block_holds_resumption holds a
            # host behind a block on its provider.
            write_json(instance / 'runner/state.json', {'blocks': {
                'model:codex/gpt-6.1-sol': {'until': time.time() + 3600, 'reason': 'model_capacity'}}})
            (instance / 'control/STOP').touch()
            policy = {'instance': str(instance), 'provider': 'codex', 'model': 'codex/gpt-6.1-sol'}
            state = {'status': 'running'}
            seen = []

            def pause(seconds):
                seen.append(state['status'])
                if len(seen) == 3:
                    (instance / 'control/STOP').unlink()  # the operator resumes dispatch; the block still holds
                elif len(seen) == 6:
                    write_json(instance / 'runner/state.json', {'blocks': {}})  # the runner clears the block

            with patch('ending.time', SimpleNamespace(time=time.time, sleep=pause)), \
                    patch('ending.read_json', wraps=read_json) as parsed:
                self.assertTrue(wait_to_resume(session, policy, state))
            self.assertEqual(seen, ['waiting_dispatch'] * 3 + ['waiting_provider'] * 3)
            self.assertEqual(read_json(session / 'end-check.json')['status'], 'resuming')
            self.assertEqual(parsed.call_count, 2)


class ContextMessageTests(unittest.TestCase):
    # A stand-in for the Claude CLI during one turn. For each request it is given it writes one `assistant`
    # event, with the context that request held and, for a request of a sub-agent, the tool call that
    # started the agent. Then it stays, as a turn stays at work, until a message waits for the session or
    # the seconds it was given have passed.
    CLI = r'''
import json
from pathlib import Path
import sys
import time

for size, parent in json.loads(sys.argv[1]):
    print(json.dumps({'type': 'assistant', 'parent_tool_use_id': parent, 'message': {
        'role': 'assistant', 'content': [], 'usage': {
            'input_tokens': 5, 'cache_creation_input_tokens': 1000, 'cache_read_input_tokens': size - 1005,
            'output_tokens': 900}}}), flush=True)
deadline = time.monotonic() + float(sys.argv[2])
while time.monotonic() < deadline and not list(Path('messages').glob('*.json')):
    time.sleep(.02)
'''

    def turn(self, session, folder, requests, seconds, state):
        """Run one turn under the host, which keeps `state` as its record of the session; returns the
        messages that wait for the session when the turn has ended."""
        import json
        (folder / 'prompt.txt').write_bytes(b'')
        command = {'argv': [sys.executable, '-c', self.CLI, json.dumps(requests), str(seconds)],
                   'cwd': str(session)}
        self.assertEqual(run_turn(session, folder, command, state)['exit_code'], 0)
        return sorted((session / 'messages').glob('*.json'))

    def test_the_host_sends_the_message_once_when_a_request_of_the_session_itself_reaches_the_size(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp) / 'session'
            (session / 'turns/0001').mkdir(parents=True)
            open_messages(session)
            # The host's record of a session in its first turn, which no request started.
            state = {'request': None, 'resumptions': 0}
            # A request of a sub-agent above the size and a request of the session just below it send
            # nothing. The message is sent for the session's own request and states the size of that one.
            waiting = self.turn(session, session, [[900_000, 'toolu_1'], [799_999, None], [812_345, None]], 30,
                                state)
            self.assertEqual(len(waiting), 1)
            message = read_json(waiting[0])
            self.assertEqual(message['from'], 'runner')
            self.assertIn('about 812,345 tokens', message['text'])
            self.assertIn('holds 1,000,000', message['text'])
            # The message is a request to decide the ending. The host has opened one, the session finds its ID
            # in the message and in end-request.json, and the request allows the basis that hands the task over.
            request = read_json(session / 'end-request.json')
            self.assertEqual(request, state['request'])
            self.assertEqual(request['context'], 812_345)
            self.assertEqual(read_json(session / 'end-check.json')['request'], request)
            self.assertIn('Its request ID is ' + request['id'], message['text'])
            self.assertIn('"request_id": "' + request['id'] + '", "decision": "end", "basis": "handed_over"',
                          message['text'])
            # The message names a section of a guide, and the guide has a section of that title.
            self.assertIn('"Handing a task over to a new session" in context/reference/retained-work.md',
                          message['text'])
            guide = Path(__file__).resolve().parents[2] / 'reference/retained-work.md'
            self.assertIn('\n## Handing a task over to a new session\n', guide.read_text(encoding='utf-8'))
            # Once in the life of the session. The hook has handed the message over, and a later turn with
            # a larger context stays a second for a message that must not come.
            waiting[0].rename(session / 'messages/delivered' / waiting[0].name)
            self.assertEqual(self.turn(session, session / 'turns/0001', [[850_000, None]], 1, state), [])
            # A resumed turn was started with a request. The message opens no second one and carries its ID.
            resumed = Path(tmp) / 'resumed'
            resumed.mkdir()
            open_messages(resumed)
            state = {'request': {'id': 'asked-at-the-resumption', 'round': 1, 'previous_error': None},
                     'resumptions': 1}
            (waiting,) = self.turn(resumed, resumed, [[805_000, None]], 30, state)
            self.assertIn('Its request ID is asked-at-the-resumption.', read_json(waiting)['text'])
            self.assertEqual(state['request'], {'id': 'asked-at-the-resumption', 'round': 1,
                                                'previous_error': None, 'context': 805_000})

    def test_a_message_that_cannot_be_written_leaves_the_turn_running_and_its_request_open(self):
        # The host looks at the stream inside the loop that keeps the turn. When the message cannot be written
        # at such a look, as on a full disk, the error is not the turn's: the CLI works on to its own end. The
        # request that was opened carries the size, so the prompt of the next turn ends with the text of the
        # message, which EndingTests asserts of such a request. Only the file system's answer to the write of
        # the message is stood in for. The stand-in leaves a file that is no message where the message would
        # wait, so that the stand-in CLI ends its wait.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp) / 'session'
            open_messages(session)
            state = {'request': None, 'resumptions': 0}

            def not_written(folder, sender, text):
                (folder / 'messages/not-written.json').write_bytes(b'')
                raise OSError('the message could not be written')

            with patch('ending.send_message', side_effect=not_written):
                waiting = self.turn(session, session, [[812_345, None]], 30, state)
            self.assertEqual([path.name for path in waiting], ['not-written.json'])
            self.assertEqual(state['request']['context'], 812_345)
            self.assertEqual(read_json(session / 'end-request.json'), state['request'])


class CancellationTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'the refusal is what Windows answers to a second TerminateProcess')
    def test_a_cli_that_another_caller_is_already_ending_is_not_recorded_as_a_failed_launch(self):
        # kill-session writes CANCEL and terminates the CLI, and the host terminates it too when it sees
        # CANCEL (runner.main, ending.run_turn). Whichever call comes second can find the process already
        # ended by the first, and Windows then refuses it with access denied. Which call comes second is a
        # matter of timing, so only that is stood in for: the real call ends the real CLI, and the host is
        # given the answer the second caller gets. The turn is then a cancelled turn with its exit code,
        # and no launch error is recorded for it.
        import ctypes
        import tempfile
        import runtime_support
        real = runtime_support.WIN.TerminateProcess

        def already_ending(handle, code):
            real(handle, code)
            ctypes.set_last_error(5)  # ERROR_ACCESS_DENIED
            return 0

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'prompt.txt').write_bytes(b'')
            (folder / 'CANCEL').write_bytes(b'')
            command = {'argv': [sys.executable, '-c', 'import time; time.sleep(120)'], 'cwd': str(folder)}
            with patch.object(runtime_support.WIN, 'TerminateProcess', side_effect=already_ending) as asked:
                result = run_turn(folder, folder, command, {'request': None, 'resumptions': 0})
        self.assertTrue(asked.called)
        self.assertNotIn('launch_error', result)
        self.assertEqual(result['exit_code'], 1)

    def test_an_error_of_the_host_after_the_cli_has_started_is_not_recorded_as_a_failed_launch(self):
        # A CLI that cannot be started is a failed launch, which the runner counts against the model
        # (Runner.finish). Once the CLI runs, an error of the host's own says nothing about the model: the CLI
        # is ended and the error leaves run_turn, so that the host ends with it and the runner collects a lost
        # host. Only the operating system's answer about the started process is stood in for.
        import subprocess
        import tempfile
        state = {'request': None, 'resumptions': 0}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'prompt.txt').write_bytes(b'')
            missing = {'argv': [str(folder / 'no-such-cli')], 'cwd': str(folder)}
            self.assertIn('launch_error', run_turn(folder, folder, missing, state))
            started = []
            real = subprocess.Popen

            def start(*args, **kwargs):
                started.append(real(*args, **kwargs))
                return started[-1]

            command = {'argv': [sys.executable, '-c', 'import time; time.sleep(120)'], 'cwd': str(folder)}
            with patch('ending.subprocess.Popen', side_effect=start), \
                    patch('ending.process_identity', side_effect=OSError('the process could not be read')), \
                    self.assertRaises(OSError):
                run_turn(folder, folder, command, state)
            self.assertIsNotNone(started[0].poll())


class SessionGateTests(unittest.TestCase):
    # The runner records a host's identity in its state and only then writes GO, so a host that never
    # sees GO starts no CLI the runner could not follow (runtime_support.session_host). The broker's
    # job host keeps the same gate; test_lean_broker tests that one.
    def launch(self, folder, runner):
        # The stand-in CLI only marks that it was started. The policy is the one dispatch writes for every
        # session, with no resumption allowed, so a host that passes the gate runs this one turn and ends.
        write_json(folder / 'launch.json', {'runner': runner, 'command': {
            'argv': [sys.executable, '-c', "open('started', 'w').close()"], 'cwd': str(folder)},
            'end_check': {'maximum': 0, 'role': 'attempt', 'provider': 'codex', 'model': 'stand-in',
                          'retry_seconds': 60}})
        (folder / 'prompt.txt').write_bytes(b'')

    def test_host_without_go_exits_on_cancel_or_dead_runner_without_starting_a_cli(self):
        # A failed dispatch, or a restarted runner finding no GO, writes CANCEL (runner.dispatch, Runner.collect).
        import tempfile
        dead = {'pid': os.getpid(), 'birth': 'a runner that has died'}
        for gate, runner in (('CANCEL', process_identity(os.getpid())), (None, dead)):
            with self.subTest(gate=gate), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                self.launch(folder, runner)
                if gate:
                    (folder / gate).write_bytes(b'')
                self.assertEqual(session_host(folder), 1)
                self.assertFalse((folder / 'started').exists())
                self.assertFalse((folder / 'exit.json').exists())

    def test_a_missing_key_inside_a_host_or_the_archiver_leaves_the_command_as_it_was_raised(self):
        # A session host and the archiver are detached, and host.log and runner/archive.log are all that says why
        # one ended. The failures the command expects, such as a continuation file the host cannot use, it turns
        # into one line of JSON (reference/operations.md). A missing key is a defect of the program, and its name
        # alone would not say where, so it leaves `main` as it was raised and Python writes the call stack to the
        # log, as for the broker's job host (test_lean_broker). The host is given a launch file without the
        # runner's identity, as a runner that loaded other code than the host can write one, and the archiver a
        # runner's state without its jobs.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.launch(folder, process_identity(os.getpid()))
            launch = read_json(folder / 'launch.json')
            del launch['runner']
            write_json(folder / 'launch.json', launch)
            with self.assertRaisesRegex(KeyError, 'runner'):
                main(['_session', str(folder)])
            self.assertFalse((folder / 'exit.json').exists())
            (folder / 'runner').mkdir()
            write_json(folder / 'runner/state.json', {'sessions': {'s1': {'job': 'j1', 'status': 'ended'}}})
            with self.assertRaisesRegex(KeyError, 'jobs'):
                main(['_archive', str(folder)])

    def test_go_written_as_the_runner_dies_still_starts_the_session(self):
        # The runner can die right after writing GO, between the host's look for GO and its look at the
        # runner. The runner's state already names this host, so the host must start the session.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.launch(folder, {'pid': os.getpid(), 'birth': 'a runner that has died'})

            def died_after_go(identity):
                (folder / 'GO').write_bytes(b'go\n')
                return False

            with patch('runtime_support.alive', side_effect=died_after_go):
                self.assertEqual(session_host(folder), 0)
            self.assertTrue((folder / 'started').exists())
            self.assertEqual(read_json(folder / 'exit.json')['exit_code'], 0)


if __name__ == '__main__':
    unittest.main()
