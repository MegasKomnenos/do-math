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
from retention import events, refusal
from runtime_support import (alive, popen_options, process_identity, read_json,
                             terminate_process, write_json, write_text)

ROLES = ('attempt', 'formalizer', 'explore', 'peer')


def turn_directory(session, number):
    return Path(session) if number == 0 else Path(session) / 'turns' / f'{number:04d}'


def conversation_id(folder, provider):
    identities = set()
    for event in events(Path(folder) / 'cli.stdout.jsonl'):
        value = (event.get('thread_id') if event.get('type') == 'thread.started' else None
                 ) if provider == 'codex' else event.get('session_id')
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
        return None, 'End decision needs request_id, decision, basis and explanation.'
    if data['request_id'] != request['id']:
        return None, 'End decision belongs to another reconsideration request.'
    if data['decision'] != 'end' or data['basis'] not in ('task_completed', 'no_way_forward'):
        return None, 'End decision needs decision=end and basis=task_completed or no_way_forward.'
    if not isinstance(data['explanation'], str) or not data['explanation'].strip():
        return None, 'End decision needs a nonempty explanation.'
    return data, None


def request_prompt(request, role, guidance_dir, *, snapshot=None):
    """Read current guidance for each turn; retain the actual source bytes delivered."""
    if role not in ROLES:
        raise ValueError('no continuation guidance for role: ' + role)
    directory = Path(guidance_dir)
    sources = {name: (directory / name).read_bytes() for name in ('common.md', role + '.md')}
    common, specific = (sources[name].decode('utf-8-sig').strip()
                        for name in ('common.md', role + '.md'))
    if not common or not specific:
        raise ValueError('continuation guidance must not be empty')
    for marker in ('{{role_guidance}}', '{{request_id}}', '{{previous_error}}'):
        if common.count(marker) != 1:
            raise ValueError('continuation common.md needs exactly one ' + marker)
    prompt = common.replace('{{role_guidance}}', specific)
    prompt = prompt.replace('{{request_id}}', request['id'])
    prompt = prompt.replace('{{previous_error}}', request.get('previous_error') or 'None') + '\n'
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
                     'request_id': (state.get('request') or {}).get('id')}
    state.update(status='authorized', authorization=authorization)
    write_json(Path(session) / 'end-check.json', state)
    return authorization


def wait_to_resume(session, policy, state):
    """STOP and scoped availability blocks hold the same host, not a new job."""
    session = Path(session)
    instance = Path(policy['instance'])
    while True:
        if (session / 'CANCEL').exists():
            return False
        stopped = (instance / 'control/STOP').exists()
        blocks = read_json(instance / 'runner/state.json').get('blocks', {})
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
    write_json(folder / 'turn-result.json', result)
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
        if (session / 'CANCEL').exists() or result['exit_code'] != 0 or signal:
            authorize(session, state, 'runner', 'interrupted',
                      'Execution ended by cancellation, failure or provider/model refusal.')
            return result
        try:
            empty = no_research_outcome(session, policy['role'])
        except (OSError, ValueError, TypeError, KeyError):
            empty = None
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
        error = None
        if state['request'] is not None:
            decision, error = end_decision(submitted, state['request'])
            write_json(folder / 'decision-check.json', {'decision': decision, 'error': error})
            if decision is not None:
                authorize(session, state, 'worker', decision['basis'], decision['explanation'])
                return result
        if number >= state['maximum']:
            authorize(session, state, 'runner', 'resumption_limit',
                      'The configured maximum of end-reconsideration resumptions has been reached.')
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
