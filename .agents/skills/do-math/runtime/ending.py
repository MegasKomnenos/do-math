"""Bounded continuation of mathematical sessions, supervised by their session hosts.

The host stays alive across turns, preserving the logical session's capacity and
coordination identity. The runner collects only after this host has finished.
"""
from pathlib import Path
import shutil
import subprocess
import time
import uuid

from availability import no_research_outcome
from launch import worker_command, worker_environment
from retention import conversation_identity, events, output_limit, refusal
from runtime_support import (alive, file_stamp, popen_options, process_identity, read_json,
                             terminate_process, write_json, write_text)

ROLES = ('attempt', 'formalizer', 'explore', 'peer')
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
    if role not in ROLES + OUTPUT_ROLES:
        raise ValueError('no continuation guidance for role: ' + role)
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


def output_problems(session):
    """What the transport check finds in a session's output, as the runner will find it when it collects the
    session, and whether that is the one finding no further turn of the session can remove."""
    # check reads the canon, which the host of a producing role never needs, so it is loaded only here.
    from check import CANDIDATE_CHANGED, check_session
    problems = check_session(session)
    return problems, problems == [CANDIDATE_CHANGED]


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
        now = time.time()
        unavailable = any(blocks.get(key, {}).get('until', 0) > now
                          for key in ('provider:' + policy['provider'], 'model:' + policy['model']))
        status = 'waiting_dispatch' if stopped else 'waiting_provider' if unavailable else 'resuming'
        if state['status'] != status:
            state['status'] = status
            write_json(session / 'end-check.json', state)
        if not stopped and not unavailable:
            return True
        time.sleep(.25)


def run_turn(session, folder, command):
    """Retain one invocation's receipts; publish the current CLI identity for the runner."""
    started = time.time()
    result = {'exit_code': None, 'invocation_started_at': started}
    child = None
    with (folder / 'prompt.txt').open('rb') as inp, \
            (folder / 'cli.stdout.jsonl').open('wb') as out, \
            (folder / 'cli.stderr.log').open('wb') as err:
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
            shutil.move(session / 'output/end-decision.json', submitted)
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
        except (OSError, ValueError, TypeError, KeyError) as exc:
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
            problems, beyond_repair = output_problems(session)
            if not problems or beyond_repair:
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
