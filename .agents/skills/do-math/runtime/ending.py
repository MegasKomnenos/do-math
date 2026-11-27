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
from launch import (CONTEXT_MESSAGE_TOKENS, CONTEXT_WINDOW, MAX_OUTPUT_TOKENS, receives_messages, send_message,
                    worker_command, worker_environment)
from retention import context_limit, conversation_identity, events, model_blocked, output_limit, refusal
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
# The bases on which a decision of the session itself ends it (end_decision). The first two are the session's
# judgment of its work under its role guide. HANDED_OVER says that the work is to go on: the conversation is
# nearly full, and the runner continues the task in a new session of the role (Runner.hand_over). It answers
# only the request of CONTEXT_MESSAGE.
ENDING_BASES = ('task_completed', 'no_way_forward')
HANDED_OVER = 'handed_over'
# The basis of the host's own authorization when a turn ended at the limit of the context window and the session
# had written no valid decision in it (retention.context_limit). The runner continues the task all the same.
CONTEXT_LIMIT = 'context_limit'
# What the host sends a session, once in its life, when the context of the session's own requests reaches
# launch.CONTEXT_MESSAGE_TOKENS (run_turn). It is a request to decide the ending and carries the ID of that
# request; a resumed turn that follows it unanswered is given the same text (request_prompt). The text stands
# here and nowhere else.
# The session reads it in the middle of its work, and what it does next follows from this text. The text
# therefore states the room that is left, what fills it and what happens at the limit, and what the room is for:
# closing the work in the way that hands it over best, judged without haste. The answers come after that. Under
# the line that names its sender the text has to stay within message_hook.WHOLE, the size up to which the CLI
# hands a message over whole.
CONTEXT_MESSAGE = (
    'When this message was sent, your conversation held about {size:,} tokens of context, and the window of your '
    'model holds {window:,}. The conversation is not shortened on the way there, so this session ends within the '
    'room that is left, and this message is the request to decide how it ends. Its request ID is {request}. The '
    'message is sent at this size, and not closer to the limit, so that the session can close its work with care, '
    'and nothing in it presses you for time. What it asks for first is that you close the work in the way that '
    'hands it over best, and that you think through and judge what to do and how, calmly and with patience. '
    '"Handing a task over to a new session" in context/reference/retained-work.md describes what follows, and '
    'this message holds what you need.\n\n'
    'The room you have is the difference between those two figures, less what the conversation has gained since '
    'the message was sent. Each response of yours adds what it holds, its reasoning as well as the text and the '
    'files it writes, and one response can hold up to {response:,} tokens. Each tool call adds what it returns. '
    'Waiting for something that is running adds only the calls that wait. That room is the one bound on this '
    'turn. No clock runs on the turn, and the answer to this request is the last thing you write in it, after the '
    'work is closed. At the limit the CLI refuses the next request and the turn ends at that point. Where that '
    'happens before you have answered, the task goes on in a new session of your role from your files as they '
    'stand at that moment, so what the limit takes is what no file of yours holds by then.\n\n'
    'So begin by taking stock of what you have in hand, and judge of each part of it which leaves the session '
    'that takes the work up after you better placed: that you finish it here, where the reasoning behind it is '
    'present, or that you hand it on as it stands and say exactly how it stands. Measure each against the room '
    'you have. What can be brought to its end within it is worth finishing here, such as a check that takes a '
    'few calls, a wait, or the last pieces of work that is nearly complete. A line of work whose end you cannot '
    'see from here, or one that you have not started, belongs to the session after you.\n\n'
    'What exists only in this conversation, such as an argument you worked out, a statement you settled on or the '
    'reason an approach failed, is what the limit would take, and it is safe once a file holds it; that is the '
    'reason to write it down before the rest. A result that you have reached and not checked, such as a proof you '
    'have not read a second time, a Lean proof that has not been compiled or a bound you quote from memory, can '
    'be checked here by the session that knows how it was found. The session after you has what you wrote and not '
    'the reasoning behind it, and has to establish the result again before it builds on it. What you hand on '
    'unchecked is still worth having when the report says that it is unchecked and what the check would be. A '
    'computation, a compile or a delegated agent that is still at work ends with this session: the broker '
    'cancels a compile that is under way, and on Windows every process this session started ends with it. Its '
    'result can still be had by waiting for it, which is worth the wait where the result bears on what is done '
    'next and its end is in sight. One that you stop, or that ends with the session, can be repeated only from '
    'what the report says of it: the command, its input and how far it got.\n\n'
    'If the work you took on is complete, or you judge under your role guide that you cannot carry it '
    'further, end as your role ends. An attempt, an explorer, a formalizer and a peer write '
    'output/end-decision.json in this turn, with this request ID and the basis task_completed or '
    'no_way_forward. That decision ends the session, and no turn follows in which the judgment is asked '
    'again. The judgment that you cannot carry the work further is therefore the one such a turn asks for: a '
    'conclusion reached through sustained, serious mathematical effort, including possibilities beyond the '
    'approaches that failed. Being able to explain the difficulties or to list what was tried is not itself '
    'a ground for ending. Before the decision says of anything that you have no handle on it, no approach to '
    'it or no way into it, you must first consider whether you really have none or are simply saying so to '
    'justify avoiding it; you really have none only when you yourself have worked on that thing and have '
    'nothing left to try. Work in which a meaningful direction is left is work that is to go on, however '
    'hard or long that direction is. '
    'A review and an organizer write no decision: the session ends when their output passes '
    'the transport check.\n\n'
    'If the work is to go on, it goes on in a new session of your role. The runner launches that session on '
    'the same assignment once you hand the task over. Your registered sections or your question stay held '
    'for it, nothing is published in between, and its assignment names your session folder. It has your '
    'files and not your conversation, and the record of a conversation holds little or none of the '
    'reasoning in it. '
    'So bring your report to the state from which the work can go on without you. What it '
    'needs for that is what your work has produced and no file holds yet, such as the statements you settled '
    'on, the proofs that closed and how far each is checked, the results of computations, the lines of attack '
    'that failed and where each stopped, the argument in hand as far as it goes and the point at which it is '
    'still open, and what you would do next and why. The new session is likely to begin with what you would do '
    'next, so that judgment is worth the same thought as any other in the work, and the report says what it '
    'rests on and how far that has been examined. The new session has a whole conversation of its own ahead of '
    'it and is no more pressed for time than you are, so leave to it how far it pursues a direction and when it '
    'ends. '
    'A peer, a review and '
    'an organizer, whose output is not a report, write this to work/report.md. When the report stands, read what '
    'you wrote for the hand-over once as the new session will read it, with your files and without this '
    'conversation. Then write '
    'output/end-decision.json as {{"request_id": "{request}", "decision": "end", "basis": "handed_over", '
    '"explanation": "<what is done and what remains>"}} and end the turn. Handing the task over ends this '
    'conversation and not the research.')


def context_message(request):
    """CONTEXT_MESSAGE for a request that carries, as `context`, the size at which the message was sent."""
    return CONTEXT_MESSAGE.format(size=request['context'], window=CONTEXT_WINDOW, response=MAX_OUTPUT_TOKENS,
                                  request=request['id'])


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
    """A decision is valid only for the request that asked for it. The basis HANDED_OVER answers only the
    request of CONTEXT_MESSAGE, which carries `context`."""
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
    bases = ENDING_BASES + ((HANDED_OVER,) if 'context' in request else ())
    if data['decision'] != 'end' or data['basis'] not in bases:
        return None, 'End decision needs decision=end and basis=' + ' or '.join(bases) + '.'
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
    if 'context' in request:
        # The session has been sent CONTEXT_MESSAGE and has not answered it. The message is handed over with
        # the results of tool calls and may still wait, so the prompt of this turn ends with the same text.
        prompt += '\n' + context_message(request) + '\n'
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


def send_context_message(session, stream, rest, state):
    """Read what the stream of a running turn has gained since the last look, and send the session
    CONTEXT_MESSAGE if a request of its own held launch.CONTEXT_MESSAGE_TOKENS or more.

    The message is a request to decide the ending, and a session has one such request at a time. A resumed
    turn was started with one, so the message carries the ID of that one; a first turn has none, and one is
    opened here. From then on the request carries the size as `context`. That is what lets a decision on it
    hand the task over (end_decision), and what says that the session has been sent the message.

    `rest` is the beginning of a line that was not complete at the last look. Returns whether the message
    was sent, and the new `rest`."""
    data = stream.read()
    if not data:
        return False, rest
    *lines, rest = (rest + data).split(b'\n')
    for line in lines:
        size = request_context(line)
        if size is not None and size >= CONTEXT_MESSAGE_TOKENS:
            request = state['request'] or {'id': uuid.uuid4().hex, 'round': state['resumptions'],
                                           'previous_error': None}
            request['context'] = size
            state['request'] = request
            write_json(session / 'end-check.json', state)
            write_json(session / 'end-request.json', request)
            send_message(session, 'runner', context_message(request))
            return True, b''
    return False, rest


def run_turn(session, folder, command, state):
    """Retain one invocation's receipts; publish the current CLI identity for the runner.

    While the turn runs, a session that receives messages and has not yet been sent CONTEXT_MESSAGE has
    the turn's stream followed for the size of its context (send_context_message). `state` is the host's
    record of the session, in which the request of that message is kept.

    A CLI that could not be started is recorded as a failed launch, which the runner counts against the
    model (Runner.finish). An error of the host's own once the CLI runs, as in reading the identity of the
    process or in writing its receipt, says nothing about the model: the CLI is ended, the error leaves
    this function, and the host ends with it, which the runner collects as a lost host."""
    started = time.time()
    result = {'exit_code': None, 'invocation_started_at': started}
    follow, rest = receives_messages(session) and 'context' not in (state['request'] or {}), b''
    with (folder / 'prompt.txt').open('rb') as inp, \
            (folder / 'cli.stdout.jsonl').open('wb') as out, \
            (folder / 'cli.stderr.log').open('wb') as err, \
            (folder / 'cli.stdout.jsonl').open('rb') as seen:
        try:
            child = subprocess.Popen(command['argv'], cwd=command['cwd'], env=worker_environment(session),
                                     stdin=inp, stdout=out, stderr=err, shell=False, **popen_options())
        except OSError as exc:
            result['launch_error'] = str(exc)
            return result
        try:
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
                        told, rest = send_context_message(session, seen, rest, state)
                    except OSError:
                        # The stream could not be read, or the request or the message not written, at this
                        # look. The turn goes on, and a later request of the session is looked at again.
                        told, rest = False, b''
                    follow = not told
                time.sleep(.1)
            result['exit_code'] = child.wait()
        finally:
            if child.poll() is None:
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
        result = run_turn(session, folder, command, state)
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
        failed = not cancelled and not signal and result['exit_code'] not in (0, None)
        limit = output_limit(folder, policy['provider']) if failed else None
        if failed and limit is None and receives_messages(session) and context_limit(folder, policy['provider']):
            # The conversation is full. With compaction off the CLI shortens nothing, so no further turn of
            # this conversation can do anything. A producing session or a peer may have written its decision
            # before the request that was refused, and the decision is then its answer all the same: the
            # refused request took nothing from its files. A review and an organizer end on a decision only
            # where it hands the task over, which is what follows here in any case. Without a valid decision
            # the files are as the session left them, and the runner starts a new session of the role from
            # them. A session that is sent no message has its compaction and does not end in this way; for it
            # the turn failed as any other.
            decision = None
            if state['request'] is not None and policy['role'] not in OUTPUT_ROLES:
                decision, problem = end_decision(submitted, state['request'])
                write_json(folder / 'decision-check.json', {'decision': decision, 'error': problem})
            if decision is not None:
                authorize(session, state, 'worker', decision['basis'], decision['explanation'])
            else:
                authorize(session, state, 'runner', CONTEXT_LIMIT,
                          'The conversation reached the limit of its context window; the CLI refused its next request.')
            return result
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
        decision = problem = None
        # A producing role and a peer answer every request with a decision. A review and an organizer end
        # with their output; a decision of theirs is read only where it answers the request of
        # CONTEXT_MESSAGE, and counts only where it hands the task over.
        if state['request'] is not None and (not output_role or 'context' in state['request']):
            decision, problem = end_decision(submitted, state['request'])
            write_json(folder / 'decision-check.json', {'decision': decision, 'error': problem})
        if decision is not None and (not output_role or decision['basis'] == HANDED_OVER):
            authorize(session, state, 'worker', decision['basis'], decision['explanation'])
            return result
        if output_role:
            # The session is done when its output passes the check the runner makes of it. What the check
            # finds is what the next turn is told; a candidate that changed is the runner's to restore.
            problems = check_session(session)
            if not problems or problems == [CANDIDATE_CHANGED]:
                authorize(session, state, 'runner', 'output_checked',
                          'The transport check of the output passed.' if not problems else problems[0])
                return result
            error = 'The transport check of your output found: ' + '; '.join(problems)
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
        # A session that has been sent CONTEXT_MESSAGE and has not answered it is asked the same request again,
        # under its ID: the message names that ID and may still wait to be handed over. Every other
        # resumption asks anew.
        told = state['request'] if 'context' in (state['request'] or {}) else None
        request = {'id': told['id'] if told else uuid.uuid4().hex, 'round': number + 1, 'previous_error': error}
        if told:
            request['context'] = told['context']
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
