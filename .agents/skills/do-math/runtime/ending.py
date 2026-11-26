"""Bounded continuation of mathematical sessions, supervised by their session hosts.

The host stays alive across turns, preserving the logical session's capacity and
coordination identity. The runner collects only after this host has finished.
"""
import json
from pathlib import Path
import subprocess
import time
import uuid

from availability import no_research_outcome
from check import CANDIDATE_CHANGED, check_session
from launch import (AUTO_COMPACT_TOKENS, CONTEXT_MESSAGE_TOKENS, receives_messages, send_message,
                    worker_command, worker_environment)
from retention import conversation_identity, events, model_blocked, output_limit, refusal
from runtime_support import (alive, file_stamp, popen_options, process_identity, read_json, replace_file,
                             terminate_process, write_json, write_text)

# A review and an organizer end with their output, an assessment or an organization, and write no end
# decision. When a turn of theirs ends and that output does not pass the transport check, the host
# resumes the same conversation with what the check found, instead of leaving the whole assignment to a
# new session: the turn of a reviewer can end while the sub-reviewers it delegated to are still at work.
OUTPUT_ROLES = ('review', 'organizer')
OUTPUT_LIMIT_NOTICE = (
    'Your previous turn ended because one response exceeded the output-token limit '
    '(CLI message: "{message}"). That response was discarded: its reasoning and anything it was '
    'producing are not in this conversation and were not saved. Your files, your earlier messages '
    'and the results of your earlier tool calls remain; continue your work from them.')
# What the host sends a session, once in its life, when the context of the session's own requests reaches
# launch.CONTEXT_MESSAGE_TOKENS (run_turn). The text stands here and nowhere else.
CONTEXT_MESSAGE = (
    'Your conversation now holds about {size:,} tokens of context. When it nears {window:,} tokens, the CLI '
    'replaces the conversation up to that point with a summary; "What a compaction of your context leaves" '
    'in context/reference/retained-work.md says what comes through a summary and what does not. Your files '
    'come through as you wrote them, so this is the time to wrap up: bring your files to the state from '
    'which your work can be taken over, and then end this turn in the way the guides of your role describe. '
    'What the files need for that is what your work has produced and no file holds yet, such as a statement '
    'you settled on, a proof that closed, the result of a computation, or a line of attack that failed and '
    'where it stopped. Ending the turn does not end the research: the work goes on from your files.')
# The sessions that have been sent CONTEXT_MESSAGE. One host supervises one session through all of its turns.
TOLD = set()


def turn_directory(session, number):
    return Path(session) if number == 0 else Path(session) / 'turns' / f'{number:04d}'


def conversation_id(folder, provider):
    identities = set()
    for event in events(Path(folder) / 'cli.stdout.jsonl'):
        value = conversation_identity(event, provider)
        if value is not None:
            try:
                identities.add(str(uuid.UUID(value)))
            except (ValueError, TypeError, AttributeError):
                raise ValueError('CLI returned an invalid conversation identity') from None
    if len(identities) > 1:
        raise ValueError('CLI returned multiple conversation identities')
    return next(iter(identities), None)


def end_decision(path, request):
    """A decision is valid only for the reconsideration turn that requested it."""
    path = Path(path)
    if not path.exists():
        return None, None
    try:
        data = read_json(path)
    except (ValueError, TypeError):
        return None, 'end-decision.json is not valid JSON.'
    if not isinstance(data, dict) or set(data) != {'request_id', 'decision', 'basis', 'explanation'}:
        return None, 'End decision needs exactly the fields request_id, decision, basis and explanation, and no others.'
    if data['request_id'] != request['id']:
        return None, 'End decision belongs to another reconsideration request.'
    if data['decision'] != 'end' or data['basis'] not in ('task_completed', 'no_way_forward'):
        return None, 'End decision needs decision=end and basis=task_completed or no_way_forward.'
    if not isinstance(data['explanation'], str) or not data['explanation'].strip():
        return None, 'End decision needs a nonempty explanation.'
    return data, None


def request_prompt(request, role, guidance_dir, *, snapshot=None):
    """Read current guidance for each turn; retain the actual source bytes delivered.

    A role that ends with its output is told what the transport check found, in output.md; it is asked
    for no end decision, so that text carries no request ID."""
    directory = Path(guidance_dir)
    frame = 'output.md' if role in OUTPUT_ROLES else 'common.md'
    markers = ('{{role_guidance}}', '{{previous_error}}') + (() if role in OUTPUT_ROLES else ('{{request_id}}',))
    sources = {name: (directory / name).read_bytes() for name in (frame, role + '.md')}
    common, specific = (sources[name].decode('utf-8-sig').strip()
                        for name in (frame, role + '.md'))
    if not common or not specific:
        raise ValueError('continuation guidance must not be empty')
    for marker in markers:
        if common.count(marker) != 1:
            raise ValueError(f'continuation {frame} needs exactly one ' + marker)
    prompt = common.replace('{{role_guidance}}', specific)
    prompt = prompt.replace('{{request_id}}', request['id'])
    prompt = prompt.replace('{{previous_error}}', request['previous_error'] or 'None') + '\n'
    if snapshot is not None:
        snapshot = Path(snapshot)
        snapshot.mkdir(parents=True, exist_ok=True)
        for name, content in sources.items():
            (snapshot / name).write_bytes(content)
    return prompt


def authorize(session, state, source, basis, explanation):
    authorization = {'authorized': True, 'source': source, 'basis': basis,
                     'explanation': explanation, 'at': time.time(),
                     'resumptions': state['resumptions'], 'maximum': state['maximum'],
                     'request_id': state['request']['id'] if state['request'] else None}
    state.update(status='authorized', authorization=authorization)
    write_json(Path(session) / 'end-check.json', state)
    return authorization


def wait_to_resume(session, policy, state):
    """STOP and scoped availability blocks hold the same host, not a new job."""
    session = Path(session)
    instance = Path(policy['instance'])
    runner_state = instance / 'runner/state.json'
    stamp = blocks = None
    while True:
        if (session / 'CANCEL').exists():
            return False
        stopped = (instance / 'control/STOP').exists()
        # The runner's state grows to megabytes in a long run and changes far less often than this wait
        # looks at it, so it is parsed again only when its file has changed, as the broker reads it
        # (runner_sessions in lean_broker.py). A block ends by the clock, which needs no new read.
        current = file_stamp(runner_state)
        if current != stamp:
            stamp, blocks = current, read_json(runner_state)['blocks']
        unavailable = model_blocked(blocks, policy['provider'], policy['model'], time.time())
        status = 'waiting_dispatch' if stopped else 'waiting_provider' if unavailable else 'resuming'
        if state['status'] != status:
            state['status'] = status
            write_json(session / 'end-check.json', state)
        if not stopped and not unavailable:
            return True
        time.sleep(.25)


def request_context(line):
    """The tokens of context that one request of the session itself held, read from one line of the stream
    of a Claude turn; None for any other line.

    An `assistant` event carries the usage of the request that produced it. What that request sent
    uncached, wrote to the cache and read from the cache is together the conversation it held. An event of
    a sub-agent names the tool call that started the agent, and its context is not the session's."""
    if b'"usage"' not in line:
        return None
    try:
        event = json.loads(line)
        if event['type'] != 'assistant' or event.get('parent_tool_use_id'):
            return None
        usage = event['message']['usage']
        return sum(usage.get(key) or 0
                   for key in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
    except (ValueError, KeyError, TypeError, AttributeError):
        return None  # the stream is the CLI's: a line of another form is not one of these


def send_context_message(session, stream, rest):
    """Read what the stream of a running turn has gained since the last look, and send the session
    CONTEXT_MESSAGE if a request of its own held launch.CONTEXT_MESSAGE_TOKENS or more.

    `rest` is the beginning of a line that was not complete at the last look. Returns whether the message
    was sent, and the new `rest`."""
    data = stream.read()
    if not data:
        return False, rest
    *lines, rest = (rest + data).split(b'\n')
    for line in lines:
        size = request_context(line)
        if size is not None and size >= CONTEXT_MESSAGE_TOKENS:
            send_message(session, 'runner', CONTEXT_MESSAGE.format(size=size, window=AUTO_COMPACT_TOKENS))
            return True, b''
    return False, rest


def run_turn(session, folder, command):
    """Retain one invocation's receipts; publish the current CLI identity for the runner.

    While the turn runs, a session that receives messages and has not yet been sent CONTEXT_MESSAGE has
    the turn's stream followed for the size of its context (send_context_message)."""
    started = time.time()
    result = {'exit_code': None, 'invocation_started_at': started}
    child = None
    follow, rest = receives_messages(session) and session not in TOLD, b''
    with (folder / 'prompt.txt').open('rb') as inp, \
            (folder / 'cli.stdout.jsonl').open('wb') as out, \
            (folder / 'cli.stderr.log').open('wb') as err, \
            (folder / 'cli.stdout.jsonl').open('rb') as seen:
        try:
            child = subprocess.Popen(command['argv'], cwd=command['cwd'], env=worker_environment(),
                                     stdin=inp, stdout=out, stderr=err, shell=False, **popen_options())
            identity = process_identity(child.pid)
            receipt = {'process': identity, 'pid': child.pid, 'started_at': started}
            write_json(folder / 'process.json', receipt)
            if folder != session:
                write_json(session / 'process.json', receipt)
            while child.poll() is None:
                if (session / 'CANCEL').exists() and alive(identity):
                    try:
                        terminate_process(identity)
                    except RuntimeError:
                        if alive(identity):
                            raise
                if follow:
                    try:
                        told, rest = send_context_message(session, seen, rest)
                    except OSError:
                        # The stream could not be read, or the message not written, at this look. The turn
                        # goes on, and a later request of the session is looked at again.
                        told, rest = False, b''
                    if told:
                        TOLD.add(session)
                        follow = False
                time.sleep(.1)
            result['exit_code'] = child.wait()
        except OSError as exc:
            result['launch_error'] = str(exc)
        finally:
            if child is not None and child.poll() is None:
                # A supervision error must not leave an untracked resumed CLI.
                child.terminate()
                child.wait()
    return result


def supervise(session, launch):
    """Run the initial turn and at most the configured number of resumption turns."""
    session = Path(session)
    policy = launch['end_check']
    state = {'status': 'running', 'maximum': policy['maximum'], 'resumptions': 0,
             'conversation_id': None, 'request': None, 'authorization': None}
    write_json(session / 'end-check.json', state)
    command = launch['command']
    while True:
        number = state['resumptions']
        folder = turn_directory(session, number)
        result = run_turn(session, folder, command)
        signal = refusal(folder, policy['provider'], policy['model'],
                         result['invocation_started_at'], policy['retry_seconds'])
        write_json(folder / 'turn-termination.json', {'result': result, 'refusal': signal})
        # A submitted decision is a receipt of this turn, not role output. Left in output/,
        # it would be frozen into a peer's candidate and checked again after a later request.
        submitted = folder / 'submitted-end-decision.json'
        if (session / 'output/end-decision.json').exists():
            replace_file(session / 'output/end-decision.json', submitted)
        cancelled = (session / 'CANCEL').exists()
        # Only the output-token cap is resumable: the conversation and files survive it.
        limit = (output_limit(folder, policy['provider'])
                 if not cancelled and not signal and result['exit_code'] not in (0, None) else None)
        if cancelled or signal or (result['exit_code'] != 0 and limit is None):
            authorize(session, state, 'runner', 'interrupted',
                      'Execution ended by cancellation, failure or provider/model refusal.')
            return result
        output_role = policy['role'] in OUTPUT_ROLES
        rejected = None
        try:
            empty = no_research_outcome(session, policy['role']) if limit is None and not output_role else None
        except (OSError, ValueError) as exc:
            # The session goes on, so the next turn is told why, as the transport check would tell it.
            empty, rejected = None, 'output/outcome.json: ' + str(exc)
        if empty is not None:
            authorize(session, state, 'runner', 'no_research', 'Valid availability-only outcome.')
            return result
        if number:
            try:
                returned = conversation_id(folder, policy['provider'])
                if returned is not None and returned != state['conversation_id']:
                    raise ValueError('Resumption returned a different conversation identity')
            except ValueError as exc:
                authorize(session, state, 'runner', 'resume_unavailable', str(exc))
                return result
        error = rejected
        if output_role:
            # The session is done when its output passes the check the runner makes of it. What the check
            # finds is what the next turn is told; a candidate that changed is the runner's to restore.
            problems = check_session(session)
            if not problems or problems == [CANDIDATE_CHANGED]:
                authorize(session, state, 'runner', 'output_checked',
                          'The transport check of the output passed.' if not problems else problems[0])
                return result
            error = 'The transport check of your output found: ' + '; '.join(problems)
        elif state['request'] is not None:
            decision, problem = end_decision(submitted, state['request'])
            write_json(folder / 'decision-check.json', {'decision': decision, 'error': problem})
            if decision is not None:
                authorize(session, state, 'worker', decision['basis'], decision['explanation'])
                return result
            if problem is not None:
                error = problem if error is None else error + ' Ending decision check: ' + problem
        if limit is not None:
            notice = OUTPUT_LIMIT_NOTICE.format(message=limit)
            error = notice if error is None else notice + (' ' if output_role else ' Ending decision check: ') + error
        if number >= state['maximum']:
            explanation = ('The configured maximum of resumptions has been reached, and the output still does not pass '
                           'the transport check.' if output_role else
                           'The configured maximum of end-reconsideration resumptions has been reached.')
            if limit is not None:
                explanation += ' The last turn ended at the output-token limit: ' + limit
            authorize(session, state, 'runner', 'resumption_limit', explanation)
            return result
        try:
            identity = conversation_id(folder, policy['provider'])
            state['conversation_id'] = state['conversation_id'] or identity
            if state['conversation_id'] is None:
                raise ValueError('No exact native conversation identity is available for resumption')
        except ValueError as exc:
            authorize(session, state, 'runner', 'resume_unavailable', str(exc))
            return result
        request = {'id': uuid.uuid4().hex, 'round': number + 1, 'previous_error': error}
        state['request'] = request
        state['status'] = 'waiting_dispatch'
        write_json(session / 'end-check.json', state)
        write_json(session / 'end-request.json', request)
        if not wait_to_resume(session, policy, state):
            authorize(session, state, 'runner', 'interrupted', 'Operator cancelled the pending resumption.')
            return result
        next_folder = turn_directory(session, number + 1)
        next_folder.mkdir(parents=True)
        write_text(next_folder / 'prompt.txt', request_prompt(
            request, policy['role'], policy['resume_guidance'], snapshot=next_folder / 'guidance'))
        write_json(next_folder / 'request.json', request)
        selected = worker_command(policy['executable'], policy['model'], policy['effort'], session,
                                  policy['mcp_servers'], resume_id=state['conversation_id'])
        command = {'argv': selected.argv, 'cwd': str(selected.cwd)}
        write_json(next_folder / 'launch.json', {'command': command, 'request': request})
        state.update(resumptions=number + 1, status='running')
        write_json(session / 'end-check.json', state)
