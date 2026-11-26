"""Fresh-instance do-math runner: autonomous work, peer development, independent review."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import uuid

from canon import (EXTRACT_MODULE, EXTRACTION, Canon, CanonError, apply_lean, apply_rearrangement, apply_written,
                   build_outcome, candidate_records, check_applied, copy_tree, declaration_text, drop_modules,
                   empty_index, history_entry, library_modules, load_change, name_path, parse_record, read_index,
                   read_record, record_file, required_pairs, retire_approaches, sha256_text, start_build,
                   statement_differences, sync_tree, update_index, wait_build, with_importers)
from check import CANDIDATE_CHANGED, IDENTIFIER, PREPARED, check_session, regular_tree, taken_question_ids, tree_hashes
from cli_adapter import provider_for_model
from launch import worker_command
from coordination import (ACTIVE_STATUSES, board, claims_lock, lease_table, question_availability,
                          question_entry, section_entries)
from availability import (availability_view, no_research_outcome, opening_since,
                          reported_availability)
from knowledge import (ROOT_QUESTION, canonical_question, formalizable, instance_metadata, record_summary,
                       refuting_proofs, render, replay, root_settlement, root_solved)
from retention import capture, refusal
from ending import authorize, turn_directory
from runtime_support import (EmergencyMemory, InstanceLock, alive, archive_work, available_memory, file_stamp, git,
                             popen_options, process_identity, read_json, read_json_cached, remove_tree, rename_directory,
                             replace_file, session_host,
                             terminate_process, write_json, write_text)
from settings import PRODUCERS, defaults, load_settings, validate
# The functions that use context and lean_broker, here and in canon, import them at that point.
# Both are loaded here as well, so that a process started from this file holds the whole runtime from its
# start. The runner and a session host run for hours, and a module first loaded during that time comes from
# the installed files as they have become: it fails where it names something that the modules loaded at the
# start do not have.
import context
import lean_broker

SCRIPT = Path(__file__).resolve()
RUNTIME = SCRIPT.parent
SKILL = RUNTIME.parent
PRIORITY = {'review': 0, 'peer': 1, 'formalizer': 2, 'organizer': 3, 'explore': 4, 'attempt': 5}


def uid(prefix):
    return prefix + uuid.uuid4().hex


def operator_questions(data, model):
    """The reason and questions of an operator publication, checked against the current research.

    The questions command checks its file with this, and the runner checks the request again when it
    collects it, because a question with the same ID can be published in between."""
    if not isinstance(data, dict):
        raise ValueError('a questions file is an object with "reason" and "questions"')
    extra = sorted(set(data) - {'reason', 'questions'})
    if extra:
        raise ValueError('unknown key in a questions file: ' + ', '.join(extra))
    reason, items = data.get('reason'), data.get('questions')
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('a questions file needs a nonempty "reason"')
    if not isinstance(items, list) or not items:
        raise ValueError('a questions file needs a nonempty "questions" array')
    taken = taken_question_ids(model)
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('each question is an object with "id", "statement" and "grounds"')
        extra = sorted(set(item) - {'id', 'statement', 'grounds'})
        if extra:
            raise ValueError('unknown key in a question: ' + ', '.join(extra))
        qid = item.get('id')
        if not isinstance(qid, str) or not IDENTIFIER.fullmatch(qid):
            raise ValueError(f'invalid question id: {qid!r}')
        if qid == ROOT_QUESTION:
            raise ValueError('q0 is the root question, which the runtime creates')
        if qid in seen:
            raise ValueError('duplicate question id: ' + qid)
        if qid in taken:
            raise ValueError('question id already names a question or a question alias: ' + qid)
        for key in ('statement', 'grounds'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'question {qid} needs a nonempty "{key}"')
        seen.add(qid)
    return reason, [{'id': q['id'], 'statement': q['statement'], 'grounds': q['grounds']} for q in items]


def initialize(instance, root_file, canon_folder, root_declaration, settings_file=None):
    """Create an instance whose root is fixed in Lean.

    canon_folder holds what the operator wrote with the user: lean/ with the modules that define the
    root's objects and state the root, records/ with a record for every declaration in them, and
    optionally bibliography.bib. The library is compiled here, through the instance's own broker, and
    its structural index extracted; an instance whose root does not compile is not created."""
    from lean_broker import Paths, broker_alive
    instance = Path(instance).resolve()
    root = Path(root_file).read_bytes()
    if not root.decode('utf-8-sig').strip():
        raise ValueError('the root statement must be nonempty UTF-8')
    source = Path(canon_folder).resolve()
    if not (source / 'lean').is_dir():
        raise ValueError('the canon folder needs lean/ with the modules that state the root')
    tops = sorted({p.relative_to(source / 'lean').parts[0].removesuffix('.lean')
                   for p in (source / 'lean').rglob('*.lean')})
    if len(tops) != 1:
        raise ValueError('the modules of the canon share one top-level name, the library; found: ' + ', '.join(tops))
    library = tops[0]
    config = validate(read_json(settings_file)) if settings_file else defaults()
    # A session whose server does not start begins its turn without the tool and says nothing, so a
    # server that cannot be started is refused here. The default names the literature server.
    absent = [f'{name} ({server["command"]})' for name, server in config['mcp_servers'].items()
              if 'command' in server and not shutil.which(str(server['command']))]
    if absent:
        raise ValueError('mcp_servers names a command that was not found: ' + ', '.join(absent)
                         + '; give the installed path, or set "mcp_servers" to {} to run without external tools')
    instance.mkdir(parents=True, exist_ok=False)
    for name in ('knowledge/events', 'knowledge/changes', 'knowledge/reviews', 'knowledge/organizations',
                 'sessions', 'runner', 'control/inputs', 'control/requests', 'canon'):
        (instance / name).mkdir(parents=True)
    canon = Canon(instance)
    shutil.copytree(source / 'lean', canon.lean)
    if (source / 'records').is_dir():
        shutil.copytree(source / 'records', canon.records)
    if (source / 'bibliography.bib').is_file():
        shutil.copyfile(source / 'bibliography.bib', canon.bibliography)
    (instance / 'root.md').write_bytes(root)
    write_json(instance / 'settings.json', config)
    write_text(instance / '.gitignore', '/sessions/\n/runner/\n/control/\n')
    state = {'schema': 2, 'sessions': {}, 'pipelines': {}, 'jobs': {}, 'blocks': {},
             'attempt_launches': 0,
             'attempt_availability_epoch': 0, 'attempt_dispatch_gate': None,
             'explore_requested': False, 'complete': False,
             'processed_concerns': [], 'processed_conflicts': [], 'publication': None, 'publish_queue': [],
             'seen_requests': [], 'last_error': None, 'finished': False}
    write_json(instance / 'runner/state.json', state)
    records = {p.relative_to(canon.records).as_posix()[:-3]:
               parse_record(p.read_text(encoding='utf-8-sig'), p.relative_to(canon.records).as_posix())
               for p in sorted(canon.records.rglob('*.md'))} if canon.records.is_dir() else {}
    stage = instance / 'runner/stage-genesis/lean'
    copy_tree(canon.lean, stage)
    modules = [module for module, _ in library_modules(stage, library)]
    paths = Paths(instance)
    try:
        build = start_build(instance, stage, library, 'operator', config['lean']['calibration_expect_mb'],
                            modules, required_pairs(records))
        outcome = wait_build(instance, build)
        if not outcome['ok']:
            raise ValueError('the canon does not compile: ' + '; '.join(
                f"{e['module']}: {e['status']} {e.get('reason') or ''} {e['output']}" for e in outcome['errors']))
        index = update_index(empty_index(), outcome['rows'], outcome['pairs'], stage, 0)
        checked = check_applied(empty_index(), index, {'replace': [], 'retire': []}, records, lambda name: False,
                                config['lean']['allowed_axioms'])
    finally:
        # No session exists yet; the runner starts the broker it needs when it runs. The broker is gone
        # before this command returns or refuses, so that a refused instance's folder can be removed at once:
        # a process that is still ending keeps its log file open.
        info = broker_alive(paths)
        if info:
            terminate_process(info['process'])
            deadline = time.monotonic() + 30
            while alive(info['process']) and time.monotonic() < deadline:
                time.sleep(0.1)
    entry = index['entries'].get(root_declaration)
    if entry is None or entry['kind'] != 'theorem' or not entry['prop']:
        checked['errors'].append(f'the root declaration {root_declaration} is not a theorem of the canon')
    elif entry['lean_proof'] != 'sorry' or (records.get(name_path(root_declaration)) or {}).get('sections', {}).get('Proof'):
        # The research is what proves or refutes the root, and the frontier begins at a root without a proof.
        checked['errors'].append(f'the root declaration {root_declaration} already has a proof; the root enters with '
                                 'its Lean proof left as `by sorry` and no "## Proof" in its record')
    if checked['errors']:
        raise ValueError('the canon cannot be fixed as it is: ' + '; '.join(checked['errors']))
    remove_tree(instance / 'runner/stage-genesis')
    write_json(canon.index, index)
    write_json(canon.root / 'records.json', record_summary(instance, index))
    write_json(instance / 'instance.json', {'schema': 2, 'root_sha256': hashlib.sha256(root).hexdigest(),
                                            'root': root_declaration, 'library': library,
                                            'root_statement_hash': entry['statement_hash']})
    render(instance, replay(instance), [])
    git(instance, 'init')
    git(instance, 'add', '--', 'root.md', 'settings.json', 'instance.json', '.gitignore', 'knowledge', 'canon')
    git(instance, 'commit', '-m', 'Initialize autonomous mathematical research')


class Runner:
    def __init__(self, instance, skill=SKILL):
        self.instance = Path(instance).resolve()
        self.skill = Path(skill).resolve()
        if not (self.instance / '.git').is_dir():
            raise ValueError('fresh instance with its own Git required')
        metadata = read_json(self.instance / 'instance.json')
        fixed = Canon(self.instance).load_index()['entries'].get(metadata.get('root'), {}).get('statement_hash')
        if (metadata.get('schema') != 2 or fixed != metadata['root_statement_hash']
                or hashlib.sha256((self.instance / 'root.md').read_bytes()).hexdigest() != metadata['root_sha256']):
            raise ValueError('root statement changed; a changed mathematical problem requires a new instance')
        self.settings = load_settings(self.instance)
        self.state_path = self.instance / 'runner/state.json'
        self.state = read_json(self.state_path)
        self.identity = process_identity(os.getpid())
        self.hosts = {}
        self.broker = None
        self.broker_attempt = 0
        self.build_seen = None  # the build of a publication whose record this runner has read (advance_build)
        self.reserve = None
        self.model = replay(self.instance)
        self.last_board = None
        self.settings_stamp = None
        self.archiver = None
        self.archive_due = False

    def save(self):
        try:
            write_json(self.state_path, self.state)
        except MemoryError:
            if self.reserve is None or not self.reserve.release():
                raise
            write_json(self.state_path, self.state)

    def session_dir(self, sid):
        return self.instance / 'sessions' / sid

    def active(self):
        return [(sid, s) for sid, s in self.state['sessions'].items() if s['status'] in ACTIVE_STATUSES]

    def enqueue(self, role, task, pipeline=None, key=None):
        key = key or uid('j')
        exists = key in self.state['jobs']
        self.state['jobs'].setdefault(key, {'id': key, 'role': role, 'task': task, 'pipeline': pipeline,
                                           'status': 'pending', 'session': None, 'retries': 0, 'not_before': 0})
        if not exists:
            self.save()
        return key

    def producer(self, role, task=None):
        pid = uid('p')
        self.state['pipelines'][pid] = {'id': pid, 'role': role, 'stage': 'producing', 'producer': None,
                                         'peer': None, 'review': None, 'record': None,
                                         'element': (task or {}).get('element'), 'previous_peers': []}
        key = self.enqueue(role, task or {}, pid, pid + ':producer')
        self.save()
        return key

    def selection(self, role):
        now = time.time()
        for item in self.settings['roles'].get(role, self.settings['models']):
            provider = provider_for_model(item['model'])
            if all(self.state['blocks'].get(key, {}).get('until', 0) <= now
                   for key in ('provider:' + provider, 'model:' + item['model'])):
                return item
        return None

    def make_pack(self, sid, job):
        from context import assemble
        if job['role'] == 'organizer' and not job['task'].get('batch_frozen'):
            job['task']['batch'] = [c for c in self.model['changes'] if c not in self.model['organized']]
            job['task']['batch_frozen'] = True
        return assemble(self.skill, self.instance, self.session_dir(sid), job['role'],
                        job['task'], job['pipeline'], self.model['sequence'], self.settings)

    def dispatch(self, key):
        job = self.state['jobs'][key]
        if job['role'] == 'attempt' and not self.attempt_dispatch_ready():
            return False
        selected = self.selection(job['role'])
        if selected is None:
            return False
        sid = uid('s')
        session = self.session_dir(sid)
        session.mkdir()
        for name in ('output', 'work', 'inbox'):
            (session / name).mkdir()
        if job['role'] == 'explore':
            # The root question is never left free while an explorer launches: the runner assigns
            # it, under the coordination lock, so no explorer choosing at the same moment takes it.
            try:
                with claims_lock(self.instance):
                    # What was recorded for this job, or for any other exploration still waiting to
                    # launch, is not occupancy: an earlier assignment, or the declaration of a failed
                    # earlier session that its pipeline still names as producer until a relaunch
                    # replaces it. Decide afresh without them (question_view).
                    job['task'].pop('question', None)
                    free = self.question_view(launching=True)['free']
                    if ROOT_QUESTION in free:
                        job['task']['question'] = ROOT_QUESTION
                        now = time.time()
                        write_json(session / 'declaration.json',
                                   {'question': {'id': ROOT_QUESTION, 'at': now, 'by': 'runner'}, 'at': now})
                    # Other sessions' question commands read the saved state, so the assignment is saved
                    # before the lock is released.
                    self.save()
            except RuntimeError:
                # Sessions' coordination commands held the lock past its wait. The launch is left to a
                # later pass rather than ending the runner, and its empty session folder goes with it.
                shutil.rmtree(session)
                return False
        self.make_pack(sid, job)
        provider = provider_for_model(selected['model'])
        s = {'id': sid, 'role': job['role'], 'job': key, 'status': 'starting',
             'model': selected['model'], 'effort': selected['effort'], 'provider': provider,
             'started_at': time.time(), 'host': None, 'cli': None, 'record': None}
        self.state['sessions'][sid] = s
        job.update(status='running', session=sid)
        if job['pipeline']:
            pipeline = self.state['pipelines'][job['pipeline']]
            if job['role'] in PRODUCERS:
                pipeline['producer'] = sid
                if job['role'] == 'formalizer':
                    # The assigned element is the formalizer's whole section; it registers nothing itself.
                    now = time.time()
                    write_json(session / 'declaration.json', {'sections': [
                        # Sections attach to the statement, also when the proof to formalize is another declaration of it.
                        {'id': sid + '-1',
                         'element': self.model['elements'][job['task']['element']]['statement_of'],
                         'whole': True, 'statement': None,
                         'new': None, 'reasons': {}, 'at': now}], 'at': now})
            else:
                pipeline[job['role']] = sid
        if job['role'] in ('attempt', 'explore'):
            # One spacing for both roles: the next attempt or exploration waits for launch_interval.
            self.state['last_launch'] = time.time()
        if job['role'] == 'attempt':
            # Every explore_every-th attempt launch requests an exploration.
            self.state['attempt_launches'] += 1
            if self.state['attempt_launches'] % self.settings['explore_every'] == 0:
                self.state['explore_requested'] = True
            gate = self.state['attempt_dispatch_gate']
            if gate and gate['mode'] == 'reassess':
                gate['probe_session'] = sid
        elif job['role'] == 'explore':
            self.state['explore_requested'] = False
        self.save()
        try:
            command = worker_command(self.settings['cli'][provider], selected['model'], selected['effort'], session,
                                     self.settings['mcp_servers'])
            launch = {'runner': self.identity, 'command': {'argv': command.argv, 'cwd': str(command.cwd)}}
            # Every role is supervised by its host across turns. A producing role and a peer are asked to
            # reconsider ending; a review and an organizer are resumed while their output does not pass the
            # transport check (ending.py). The role in the policy tells the host which of the two applies.
            launch['end_check'] = {'maximum': self.settings['max_end_resumptions'],
                                   'resume_guidance': str(self.skill / 'resume'),
                                   'instance': str(self.instance), 'role': job['role'],
                                   'provider': provider, 'model': selected['model'], 'effort': selected['effort'],
                                   'executable': self.settings['cli'][provider],
                                   'mcp_servers': self.settings['mcp_servers'],
                                   'retry_seconds': self.settings['retry_seconds']}
            write_json(session / 'launch.json', launch)
            with (session / 'host.log').open('wb') as log:
                host = subprocess.Popen([sys.executable, '-B', str(SCRIPT), '_session', str(session)],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=log, cwd=session,
                                        **popen_options(detached=True))
            self.hosts[sid] = host
            s.update(host=process_identity(host.pid), status='running')
            self.save()
            (session / 'GO').write_bytes(b'go\n')
        except (OSError, ValueError) as exc:
            s['launch_error'] = str(exc)
            (session / 'CANCEL').touch()
            self.save()
        return True

    def backoff(self, attempts):
        """The wait after the given number of consecutive failures: retry_seconds, doubling each time up to
        retry_max_seconds. A job's retry and a refusal without a known reset both wait this long."""
        return min(self.settings['retry_max_seconds'], self.settings['retry_seconds'] * 2 ** min(attempts - 1, 20))

    def retry(self, job, session, reason, *, availability=True):
        job['retries'] += 1
        delay = self.backoff(job['retries'])
        now = time.time()
        job.update(status='pending', session=None,
                   not_before=now + (min(delay, 1) if availability else delay), last_error=reason)
        job['task']['previous_error'] = reason
        block_key = 'model:' + session['model']
        # A typed refusal already recorded its own scope and backoff history.
        # Invalid output is a job failure, not evidence that its model is unavailable.
        if availability and not session.get('refusal') and self.state['blocks'].get(
                'provider:' + session['provider'], {}).get('until', 0) <= now:
            until = now + delay
            if self.state['blocks'].get(block_key, {}).get('until', 0) < until:
                self.state['blocks'][block_key] = {'until': until, 'reason': reason, 'source': 'retry'}
        session.update(status='failed', reason=reason)
        if job['role'] not in PRODUCERS:
            # The replacement continues this job's own stage. A review job assesses one candidate, so the
            # review of an earlier candidate that a new peer replaced is not partial work of this job.
            previous = job['task'].setdefault('previous_partial_sessions', [])
            path = str(self.session_dir(session['id']))
            if path not in previous:
                previous.append(path)
        if job['role'] == 'peer':
            # A failed peer's sections stay with its pipeline until review ends (coordination.board).
            self.state['pipelines'][job['pipeline']]['previous_peers'].append(session['id'])
        self.save()

    def finish(self, sid, s):
        job = self.state['jobs'][s['job']]
        if job['status'] == 'done':
            return
        session = self.session_dir(sid)
        ending = session / 'end-check.json'
        if not ending.exists() and (session / 'launch.json').exists():
            policy = read_json(session / 'launch.json')['end_check']
            authorize(session, {'maximum': policy['maximum'], 'resumptions': 0, 'request': None},
                      'runner', 'interrupted', 'Session host ended before starting end reconsideration.')
        if ending.exists():
            s['end_check'] = read_json(ending)
            if s['end_check']['authorization'] is None:
                # Host loss is an interruption, never the worker deciding to end.
                authorize(session, s['end_check'], 'runner', 'interrupted',
                          'Session host ended before end reconsideration could finish.')
            self.save()
        if not s.get('retained'):
            # File errors leave this stage incomplete for restart recovery.
            retention = capture(session, s['provider'])
            last_turn = turn_directory(session, s.get('end_check', {}).get('resumptions', 0))
            signal = refusal(last_turn, s['provider'], s['model'],
                             s.get('invocation_started_at', s['started_at']), self.settings['retry_seconds'])
            if signal:
                previous = self.state['blocks'].get(signal['key'], {})
                # The count rises when this invocation began after the wait of the earlier refusal had passed.
                # A session already in flight when that block was set is refused by the same outage: as its
                # success would not show recovery (below), its refusal is not a further failure after a wait.
                waited = s.get('invocation_started_at', s['started_at']) >= previous.get('until', 0)
                signal['attempts'] = max(previous.get('attempts', 0) + (1 if waited else 0), 1)
                if signal['source'] in ('fallback', 'backoff'):
                    signal['until'] = time.time() + self.backoff(signal['attempts'])
            write_json(session / 'termination.json', {'cause': 'refusal' if signal else 'launch_error' if s.get('launch_error') else 'process_exit',
                                                      'exit_code': s.get('exit_code'), 'refusal': signal,
                                                      'at': time.time()})
            if signal:
                if previous.get('until', 0) <= signal['until']:
                    self.state['blocks'][signal['key']] = signal
                s['refusal'] = signal
            s['retention'] = retention
            s['retained'] = True
            self.save()
        if (s.get('exit_code') == 0 and not s.get('refusal') and not s.get('launch_error')
                and (s['retention']['cli_activity'] or s['retention']['native_activity'])):
            # A successful request launched after the wait establishes recovery.
            # An older in-flight success must not erase a later refusal's block.
            recovered = [key for key in ('provider:' + s['provider'], 'model:' + s['model'])
                         if key in self.state['blocks']
                    and s.get('invocation_started_at', s['started_at']) >= self.state['blocks'][key]['until']]
            for key in recovered:
                del self.state['blocks'][key]
            if recovered:
                self.save()
        if s['role'] in PRODUCERS:
            if (s.get('exit_code') == 0 and not s.get('refusal') and not s.get('launch_error')
                    and s.get('end_check', {}).get('authorization', {}).get('basis') != 'interrupted'):
                try:
                    outcome = no_research_outcome(session, s['role'])
                except (OSError, ValueError) as exc:
                    # An invalid opt-out cannot discard retained research.
                    s['no_research_error'] = str(exc)
                    outcome = None
                if outcome is not None:
                    self.finish_no_research(sid, s, job, outcome)
                    return
            material = (s['retention']['cli_activity'] or s['retention']['native_activity']
                        or any((session / name).is_dir() and any((session / name).rglob('*')) for name in ('output', 'work')))
            if not material:
                # A failed launch or a CLI that ended without work counts against its model, so the retry
                # can take the role's next one. A cancellation, such as kill-session, says nothing about the model.
                cancelled = (session / 'CANCEL').exists() and not s.get('launch_error')
                self.retry(job, s, s.get('launch_error') or 'session ended without retained research material',
                           availability=not cancelled)
                return
            # Finish the reads of the producer's declaration before marking the producer complete, as for the
            # candidate of a peer below: a failed read must remain collectable after the fatal-error save.
            pipeline = self.state['pipelines'][job['pipeline']]
            task = {'source': str(session), 'source_role': s['role'], 'element': pipeline['element'],
                    'sections': self.producer_sections(sid), 'question': self.producer_question(sid)}
            s['status'] = 'ended'
            job['status'] = 'done'
            pipeline['stage'] = 'peer'
            self.enqueue('peer', task, pipeline['id'], pipeline['id'] + ':peer')
            self.save()
            return
        # A cancellation recorded by the host, even after a clean CLI exit between turns,
        # leaves this stage unfinished; a replacement receives the partial material.
        authorization = s.get('end_check', {}).get('authorization') or {}
        interrupted = authorization.get('basis') == 'interrupted'
        # Any other end authorization by the host ends the session normally, even when its last turn stopped
        # at the output-token cap with a nonzero exit: a peer's own decision, the host's check of a review's
        # or an organizer's output, and for all three the resumption limit or an unavailable resumption.
        # The output then goes to the transport check.
        failed = s.get('exit_code') != 0 and not (authorization and not interrupted)
        if failed or s.get('refusal') or s.get('launch_error') or interrupted:
            reason = (s.get('launch_error') or (s.get('refusal') or {}).get('reason') or
                      (f"processing session ended without successful completion (exit_code={s.get('exit_code')!r})"
                       if failed else authorization['explanation']))
            self.retry(job, s, reason,
                       availability=bool(s.get('refusal') or s.get('launch_error')))
            return
        errors = check_session(session)
        if errors:
            if (s['role'] == 'review' and job['task']['kind'] == 'candidate'
                    and errors == [CANDIDATE_CHANGED]):
                self.recover_candidate(job, s, errors[0])
                return
            # Invalid output is a job failure; refusals and launch errors returned above.
            self.retry(job, s, '; '.join(errors), availability=False)
            return
        if s['role'] == 'peer':
            candidate = session / 'candidate'
            if not candidate.exists():
                staging = session / 'candidate.part'
                if staging.exists():
                    remove_tree(staging)
                shutil.copytree(session / 'output', staging)
                rename_directory(staging, candidate)
            # Finish all candidate reads before marking the peer complete. A
            # failed read must remain collectable after the fatal-error save.
            hashes = tree_hashes(candidate)
            s['status'] = 'ended'
            job['status'] = 'done'
            pipeline = self.state['pipelines'][job['pipeline']]
            pipeline['stage'] = 'review'
            self.enqueue('review', {'kind': 'candidate', 'candidate': str(candidate),
                                    'candidate_hashes': hashes,
                                    'source': str(self.session_dir(pipeline['producer'])),
                                    'peer': str(session)}, pipeline['id'], pipeline['id'] + ':review:' + sid)
            self.save()
            return
        if s['role'] == 'review' and job['task']['kind'] == 'candidate':
            assessment = read_json(session / 'output/assessment.json')
            if not assessment['publish']:
                s.update(status='integrated', rejected=True)
                job['status'] = 'done'
                self.state['pipelines'][job['pipeline']].update(stage='done', rejection_session=sid)
                self.archive_due = True
                self.save()
                return
            kind = 'change'
        elif s['role'] == 'review':
            kind = 'review'
        else:
            kind = 'organization'
        # One publication at a time changes the canon; a build can take minutes, so later ones wait in order.
        self.state['publish_queue'].append({'session': sid, 'job': job['id'], 'kind': kind})
        s['status'] = 'publishing'
        self.save()
        self.publish()

    def producer_sections(self, sid):
        """The sections a producer registered, as a peer assignment lists them."""
        return [{key: entry.get(key) for key in ('id', 'element', 'whole', 'statement', 'new')}
                for entry in section_entries(self.instance, sid, self.model)]

    def producer_question(self, sid):
        """The question an explorer occupies, or None for other producers."""
        held = question_entry(self.instance, sid, self.model)
        return held['id'] if held else None

    def recover_candidate(self, job, session, reason):
        """Keep the damaged evidence; restore verified bytes or have a fresh peer develop a candidate."""
        task = job['task']
        peer = Path(task['peer'])
        original = peer / 'output'
        expected = task['candidate_hashes']
        try:
            regular_tree(original)
            recoverable = tree_hashes(original) == expected
        except (OSError, ValueError):
            recoverable = False
        if recoverable:
            restored = peer / ('candidate-recovered-' + session['id'])
            if not restored.exists():
                staging = restored.with_name(restored.name + '.part')
                if staging.exists():
                    remove_tree(staging)
                shutil.copytree(original, staging)
                if tree_hashes(staging) != expected:
                    raise ValueError('peer output changed during candidate recovery')
                rename_directory(staging, restored)
            regular_tree(restored)
            if tree_hashes(restored) != expected:
                raise ValueError('recovered candidate does not match the assigned hashes')
            task['candidate'] = str(restored)
            self.retry(job, session, reason, availability=False)
            return
        self.replace_peer(job, session, reason)

    def replace_peer(self, job, session, reason):
        """A new peer gets the original research, the earlier peer work and the reason, and makes a new candidate.

        The cancelled review remains in history; the new peer's own review receives a distinct job."""
        task = job['task']
        peer = Path(task['peer'])
        pipeline = self.state['pipelines'][job['pipeline']]
        # The producer's declaration is read before anything is changed. If the read fails, the runner ends and
        # saves its state (run), and in that state the session whose work is handed over is still collected.
        sections = self.producer_sections(pipeline['producer'])
        question = self.producer_question(pipeline['producer'])
        self.retry(job, session, reason, availability=False)
        job['status'] = 'cancelled'
        if peer.name not in pipeline['previous_peers']:
            pipeline['previous_peers'].append(peer.name)
        pipeline['stage'] = 'peer'
        self.enqueue('peer', {'source': task['source'], 'source_role': pipeline['role'],
                             'element': pipeline['element'], 'sections': sections, 'question': question,
                             'previous_error': reason,
                             'previous_partial_sessions': [str(self.session_dir(x)) for x in pipeline['previous_peers']]},
                     pipeline['id'], pipeline['id'] + ':peer-recovery:' + session['id'])
        self.save()

    def prepare_publication(self, sid, job, kind):
        rid = uid({'change': 'c', 'review': 'v', 'organization': 'o'}[kind])
        folder = {'change': 'changes/', 'review': 'reviews/', 'organization': 'organizations/'}[kind] + rid
        event = {'id': rid, 'kind': kind, 'sequence': self.model['sequence'] + 1, 'folder': folder,
                 'session': sid, 'at': time.time()}
        if kind == 'change':
            pipeline = self.state['pipelines'][job['pipeline']]
            event.update(producer_role=pipeline['role'], pipeline=pipeline['id'], element=pipeline['element'],
                         question=self.producer_question(pipeline['producer']))
        # The work leaves the queue in the save that records its publication. Until then it waits there: the read
        # of the producer's declaration above can fail, on which the runner ends and saves its state (run).
        self.state['publish_queue'] = [queued for queued in self.state['publish_queue'] if queued.get('session') != sid]
        self.state['publication'] = {'event': event, 'job': job['id'], 'session': sid, 'stage': 'apply'}
        self.state['sessions'][sid].update(status='publishing', record=rid)
        self.save()

    def prepare_questions(self, item):
        """An operator publication of questions, which has no session or job behind it.

        Its content is saved with the publication's identity, so a restart writes the same files."""
        eid = uid('q')
        event = {'id': eid, 'kind': 'questions', 'sequence': self.model['sequence'] + 1,
                 'folder': 'questions/' + eid, 'at': item['at'], 'source': 'operator'}
        self.state['publish_queue'] = [queued for queued in self.state['publish_queue'] if queued is not item]
        self.state['publication'] = {'event': event, 'job': None, 'session': None, 'stage': 'commit',
                                     'questions': {'source': 'operator', 'reason': item['reason'],
                                                   'questions': item['questions'], 'at': item['at']}}
        self.save()

    def record_declined(self, publication, candidate, assessment):
        """A proof that review declined to put in place of the canon's stays among the approaches tried.

        The peer's own approach entry for the statement serves when the candidate carries one. Where it
        carries none, the entry is made here from the candidate's description, the declined written
        proof and review's reason, each taken as it stands. Like every approach entry, it names the
        sessions whose originals hold the work, the producer and the peer, and it carries review's
        assessment of what the change contributed."""
        canon = Canon(self.instance)
        event = publication['event']
        elements = self.model['elements']
        job = self.state['jobs'][publication['job']]
        pipeline = self.state['pipelines'][job['pipeline']]
        sessions = ', '.join(sid for sid in (pipeline['producer'], pipeline['peer']) if sid)
        change = None
        for verdict in assessment['elements']:
            if verdict.get('replaces') is not False:
                continue
            name = verdict['element']
            folder = name_path(elements[name]['statement_of'] if name in elements else name)
            carried = candidate / 'approaches' / folder
            target = canon.approaches / folder / ('declined-' + event['id'] + '.md')
            if (carried.is_dir() and any(carried.glob('*.md'))) or target.exists():
                continue
            change = change or load_change(candidate)
            record = candidate / 'records' / (name_path(name) + '.md')
            proof = parse_record(record.read_text(encoding='utf-8-sig'))['sections'].get('Proof') if record.is_file() else ''
            offered = f'\n\nThe proof as it was offered:\n\n{proof}' if proof else ''
            target.parent.mkdir(parents=True, exist_ok=True)
            write_text(target, f"---\ntitle: Proof offered by change {event['id']} and not put in place\n"
                               f"sessions: {sessions}\n---\n\n"
                               f"## Idea\n\n{change['title'].strip()}. {change['description'].strip()}{offered}\n\n"
                               '## Established\n\nNothing of it took the place of the proof the canon has.\n\n'
                               f"## Where it stops\n\n{verdict['reason'].strip()}\n\n"
                               f"## Review\n\nChange {event['id']} (revision {event['sequence']}): "
                               f"{assessment['contribution'].strip()}\n")

    def join_question_texts(self, publication):
        """When an organizer merges questions, the surviving question keeps one understanding text.

        The absorbed question's text becomes the surviving one's when that has none. Otherwise it
        goes to the surviving question's history, where the question's view shows it on request."""
        canon = Canon(self.instance)
        data = read_json(self.session_dir(publication['session']) / 'output/organization.json')
        for merge in data.get('merge_questions', []):
            source = canon.questions / (canonical_question(self.model, merge['from']) + '.md')
            into = canonical_question(self.model, merge['into'])
            target = canon.questions / (into + '.md')
            if not source.is_file() or source == target:
                continue
            if target.is_file():
                target = (canon.history / 'questions' / into
                          / f"{publication['event']['sequence']:06d}-merged-{source.stem}.md")
            target.parent.mkdir(parents=True, exist_ok=True)
            replace_file(source, target)

    def publication_candidate(self, publication):
        """The folder a publication applies to the canon: a peer's frozen candidate, or an organizer's output."""
        job = self.state['jobs'][publication['job']]
        if publication['event']['kind'] == 'change':
            return Path(job['task']['candidate'])
        return self.session_dir(publication['session']) / 'output'

    def effective_change(self, publication):
        """The candidate's change without the replacements that review declined, and its records.

        Review says for each proof a candidate would replace whether the new proof takes the place of
        the old one. A declined replacement leaves the declaration and its record as the canon has them."""
        candidate = self.publication_candidate(publication)
        change = load_change(candidate)
        declined = set()
        if publication['event']['kind'] == 'change':
            assessment = read_json(self.session_dir(publication['session']) / 'output/assessment.json')
            replaced = {item['declaration'] for item in change['replace']}
            declined = {v['element'] for v in assessment['elements']
                        if v.get('replaces') is False and v['element'] in replaced}
        change['replace'] = [item for item in change['replace'] if item['declaration'] not in declined]
        skipped = {name_path(name) for name in declined}
        records = {path: record for path, record in candidate_records(candidate, change).items() if path not in skipped}
        return change, records

    def publication_failed(self, publication, reason):
        """A candidate that cannot be applied or does not build on the canon as it now is.

        A build that failed would break the canon for every session, and the peer could not know what
        was published after its session ended. A replacement peer therefore receives the original work,
        the earlier peer's work and the reason, and its candidate receives a new review. An organizer's
        change is made again by a replacement organizer."""
        job = self.state['jobs'][publication['job']]
        session = self.state['sessions'][publication['session']]
        # As where a changed candidate is found (advance_build), the session is left as running until its work has
        # been handed over. If the handover fails, the runner ends and saves this state (run); a session left as
        # publishing would then belong to no publication and never be collected.
        session.update(status='running', record=None)
        self.state['publication'] = None
        # That state is saved before the stage is removed. A removal can stop part-way, when the runner is ended
        # or Windows refuses a file that another process holds. A publication still saved would then have a stage
        # without its index and with part of its modules; the next runner would check the candidate against the
        # canon's own index, where a refused replacement shows no difference, and install what is left of the stage.
        self.save()
        stage = self.instance / 'runner' / ('stage-' + publication['event']['id'])
        if stage.exists():
            remove_tree(stage)
        if publication['event']['kind'] == 'change':
            self.replace_peer(job, session, 'the candidate could not be published on the current canon: ' + reason)
        else:
            self.retry(job, session, 'the change could not be published on the current canon: ' + reason,
                       availability=False)
        return False

    def advance_build(self, publication):
        """Apply a candidate to a copy of the canon, build it through the broker and check what it changed.

        Returns True when the publication is ready to be committed and False while it waits for the
        build or after it failed. Each stage is saved, so a restarted runner continues the same build."""
        event = publication['event']
        organizer = event['kind'] == 'organization'
        candidate = self.publication_candidate(publication)
        canon = Canon(self.instance)
        stage = self.instance / 'runner' / ('stage-' + event['id'])
        if organizer and not (candidate / 'change.json').exists():
            publication.update(stage='commit', applied=None)
            self.save()
            return True
        if publication['stage'] != 'apply' and publication.get('extraction') != EXTRACTION:
            # A runner with another extraction staged this publication, and the index it staged holds rows of
            # another form. An earlier version of this code, which also had a stage `judge` after `check`, is
            # such a runner. The candidate is staged again; the modules come from the broker's cache.
            publication['stage'] = 'apply'
        if publication['stage'] == 'build' and self.build_seen == publication['build']:
            # Asked on every pass while the build runs. The broker writes a build's result file when the build
            # ends and at no other time. Until that file is there, nothing has changed since this runner read
            # the build's record below, and the broker's state and the index, each read whole, stay unread.
            from lean_broker import Paths, result_file
            if not result_file(Paths(self.instance), publication['build']).exists():
                return False
        index = canon.load_index()
        if publication['stage'] == 'apply':
            job = self.state['jobs'][publication['job']]
            if not organizer and tree_hashes(candidate) != job['task']['candidate_hashes']:
                self.state['publication'] = None
                session = self.state['sessions'][publication['session']]
                # The review no longer waits for a publication. If the recovery below fails, the runner ends
                # and saves this state (run); a session left as publishing would then belong to no publication
                # and never be collected. As running it is collected again by the next runner, whose transport
                # check finds the changed candidate as it does when a review ends (finish).
                session.update(status='running', record=None)
                self.recover_candidate(job, session, CANDIDATE_CHANGED)
                return False
            if stage.exists():
                remove_tree(stage)
            copy_tree(canon.lean, stage / 'lean')
            try:
                change, records = self.effective_change(publication)
                receipt = read_json(candidate / PREPARED)
                changed = apply_lean(stage / 'lean', candidate, change, index, receipt.get('bases'),
                                     self.model['library'])
                removed = []
                if organizer:
                    written, removed = apply_rearrangement(
                        stage / 'lean', candidate, read_json(candidate / 'organization.json').get('delete', []))
                    changed = sorted(set(changed) | set(written))
            except (CanonError, OSError, ValueError) as exc:
                return self.publication_failed(publication, str(exc))
            # A module that imports a changed one is compiled in a new environment, so its index is taken again
            # too: an unchanged statement can come out different when its module's imports bring more into scope.
            extracted = with_importers(stage / 'lean', self.model['library'], changed)
            publication.update(changed=changed, extracted=extracted, removed=removed, extraction=EXTRACTION)
            if changed or removed:
                publication.update(stage='build', build=start_build(
                    self.instance, stage / 'lean', self.model['library'], 'runner',
                    self.settings['lean']['calibration_expect_mb'], extracted, required_pairs(records)))
            else:
                publication['stage'] = 'check'
            self.save()
        if publication['stage'] == 'build':
            outcome = build_outcome(self.instance, publication['build'])
            self.build_seen = publication['build']
            if outcome is None:
                return False
            if not outcome['ok']:
                return self.publication_failed(publication, '; '.join(
                    f"{e['module'] or 'build'}: {e['status']} {e.get('reason') or ''}\n{e['output']}"
                    for e in outcome['errors']))
            write_json(stage / 'index.json', update_index(
                drop_modules(index, publication['removed']), outcome['rows'], outcome['pairs'],
                stage / 'lean', event['sequence'], publication['extracted']))
            publication['stage'] = 'check'
            self.save()
        if publication['stage'] == 'check':
            change, records = self.effective_change(publication)
            new = read_json(stage / 'index.json') if (stage / 'index.json').exists() else {**index, 'revision': event['sequence']}
            checked = check_applied(index, new, change, records,
                                    lambda name: read_record(canon, name),
                                    self.settings['lean']['allowed_axioms'], organizer=organizer)
            if checked['errors']:
                return self.publication_failed(publication, '; '.join(checked['errors']))
            # Nothing further is asked about the proofs the change brings. The library compiled, so Lean's
            # kernel accepted every declaration, and the index holds Lean's account of each proof's axioms.
            publication.update(applied={key: checked[key] for key in ('added', 'replaced', 'records', 'retired')},
                               stage='commit')
            self.save()
        return True

    def keep_replaced_proofs(self, publication):
        """Leave in the history the Lean text of every proof this publication takes out of the source.

        It runs before the new sources are installed. A repeat after a crash finds the entry already
        written, sources that no longer match the old index, or sources and an index that are already
        those of the stage, and writes nothing then."""
        event, applied = publication['event'], publication['applied']
        canon = Canon(self.instance)
        stage = self.instance / 'runner' / ('stage-' + event['id'])
        if not (stage / 'index.json').exists() or not (stage / 'lean').exists():
            return
        old, new = canon.load_index()['entries'], read_index(stage / 'index.json')['entries']
        for name in applied['replaced'] + [item['into'] for item in applied['retired']]:
            if name not in old or name not in new:
                continue
            if (canon.history / name_path(name) / f"{event['sequence']:06d}-proof.md").exists():
                continue
            source = canon.lean / old[name]['file']
            if not source.is_file():
                continue
            before = declaration_text(source.read_text(encoding='utf-8').replace('\r\n', '\n'), old[name]['span'])
            after = declaration_text((stage / 'lean' / new[name]['file']).read_text(encoding='utf-8').replace('\r\n', '\n'),
                                     new[name]['span'])
            if sha256_text(before) == old[name]['source_sha'] and before != after:
                history_entry(canon, name, 'proof', event['sequence'], event['id'], before, after,
                              'lean/' + new[name]['file'])

    def install_canon(self, publication):
        """Put the built module root and its index in place of the canon's. Each step can be repeated after a crash.

        The stage is left in place: publish removes it once the publication is saved as installed."""
        event = publication['event']
        canon = Canon(self.instance)
        stage = self.instance / 'runner' / ('stage-' + event['id'])
        if (stage / 'lean').exists():
            (stage / 'lean' / (EXTRACT_MODULE + '.lean')).unlink(missing_ok=True)
            sync_tree(stage / 'lean', canon.lean)
        if (stage / 'index.json').exists():
            # Read as an index of any version: a publication that an earlier version of this code carried
            # past its checks is installed by this one in the present form.
            write_json(canon.index, read_index(stage / 'index.json'))

    def publish(self):
        """Carry the current publication forward, and start the next one in the queue when none is underway."""
        if not self.state['publication'] and self.state['publish_queue']:
            # The item leaves the queue in the save that records its publication (prepare_questions,
            # prepare_publication), so it still waits there in the state the runner saves when preparing it fails.
            item = self.state['publish_queue'][0]
            if item['kind'] == 'questions':
                self.prepare_questions(item)
            else:
                self.prepare_publication(item['session'], self.state['jobs'][item['job']], item['kind'])
        publication = self.state['publication']
        if not publication:
            return
        event = publication['event']
        kind = event['kind']
        sid = publication['session']
        job = self.state['jobs'][publication['job']] if publication['job'] else None
        if kind in ('change', 'organization') and publication['stage'] != 'commit' and not self.advance_build(publication):
            return
        canon = Canon(self.instance)
        destination = self.instance / 'knowledge' / event['folder']
        applied = publication.get('applied')
        if kind == 'organization' and not publication.get('installed'):
            # Before the event is written: the merges are read against the questions as they stood before this
            # publication (self.model), and a runner that starts after the event was written has them merged.
            self.join_question_texts(publication)
        if not destination.exists():
            stage = self.instance / 'runner' / ('event-' + event['id'])
            if stage.exists():
                remove_tree(stage)
            if kind == 'change':
                shutil.copytree(self.session_dir(sid) / 'output', stage)
                shutil.copyfile(self.publication_candidate(publication) / 'change.json', stage / 'change.json')
                write_json(stage / 'applied.json', applied)
                pipeline = self.state['pipelines'][job['pipeline']]
                write_json(stage / 'provenance.json', {
                    'producer_session': pipeline['producer'], 'peer_session': pipeline['peer'],
                    'review_session': sid, 'pipeline': pipeline['id']})
                verified = self.session_dir(sid) / 'work/verify/outcome.json'
                if verified.is_file():
                    shutil.copyfile(verified, stage / 'verify.json')
            elif kind == 'questions':
                stage.mkdir()
                write_json(stage / 'questions.json', publication['questions'])
            elif kind == 'organization':
                stage.mkdir()
                output = self.session_dir(sid) / 'output'
                for name in ('organization.json', 'change.json'):
                    if (output / name).is_file():
                        shutil.copyfile(output / name, stage / name)
                write_json(stage / 'applied.json', applied or {'added': [], 'replaced': [], 'records': [], 'retired': []})
            else:
                shutil.copytree(self.session_dir(sid) / 'output', stage)
            # knowledge/questions/ appears with an instance's first operator publication of questions.
            destination.parent.mkdir(exist_ok=True)
            rename_directory(stage, destination)
        # The event is written before the canon is put in place, and a replay counts the event of a change to
        # the library only once the index carries its sequence (knowledge.replay). Every command a session
        # runs replays, at whatever moment of a publication it is called. It then has the canon without this
        # change or with it, and in the second case each proof the change brought has the verdict of its
        # review. An index in place before its event would show such a reader complete proofs without a
        # verdict, and a proof without a verdict stands as accepted (knowledge.standing_of).
        event_path = self.instance / 'knowledge/events' / (event['id'] + '.json')
        if not event_path.exists():
            write_json(event_path, event)
        if not publication.get('installed'):
            if applied is not None:
                candidate = self.publication_candidate(publication)
                change = load_change(candidate)
                self.keep_replaced_proofs(publication)
                self.install_canon(publication)
                assessment = (read_json(self.session_dir(sid) / 'output/assessment.json') if kind == 'change' else None)
                apply_written(canon, candidate, change, applied, event['sequence'], event['id'],
                              assessment['contribution'] if assessment else None,
                              lambda qid: canonical_question(self.model, qid))
                if assessment:
                    self.record_declined(publication, candidate, assessment)
                for item in applied['retired']:
                    # The alternative's record goes with its declaration; the statement's own record stays.
                    old = record_file(canon, item['alternative'])
                    if old.is_file():
                        target = canon.history / name_path(item['alternative']) / f"{event['sequence']:06d}-retired.md"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        replace_file(old, target)
                write_json(canon.root / 'records.json', record_summary(self.instance, canon.load_index()))
            publication['installed'] = True
            self.save()
        # The stage is removed only here, after the save that marks the canon as installed. A removal can stop
        # part-way, when the runner is ended or Windows refuses a file that another process holds. A runner that
        # installed again from what such a removal left would take the missing modules out of the canon (sync_tree).
        staged = self.instance / 'runner' / ('stage-' + event['id'])
        if staged.exists():
            remove_tree(staged)
        self.model = replay(self.instance)
        # When a statement has an accepted proof, under any of its declarations, the approaches tried on it
        # go to its history. Any publication can bring that about: a change that adds or replaces the proof,
        # a change that writes an entry on a statement whose proof is already accepted, the entry that
        # record_declined made above for a replacement review declined, or a review's finding that restores
        # a proof's confirmation. Read from the model, so that a repeat after a crash finds them gone. The
        # model has each element's entries from the summary of the records, which is written again below once
        # entries have moved. A runner that ended between the move and that writing left the summary listing
        # entries that are gone, and the repeat moves nothing, so the summary is written again as well when
        # it still lists entries on such a statement.
        stale = False
        for name, element in self.model['elements'].items():
            if element['standing'] == 'accepted':
                for target in {name, element['statement_of']}:
                    stale = (retire_approaches(canon, target, event['sequence'])
                             or bool(self.model['elements'][target]['approaches']) or stale)
        if stale:
            write_json(canon.root / 'records.json', record_summary(self.instance, canon.load_index()))
            self.model = replay(self.instance)
        self.attempt_dispatch_ready()
        render(self.instance, self.model, board(self.instance, self.state, self.model),
               lease_table(self.instance, self.state, self.model))
        if not git(self.instance, 'log', '-1', '--format=%H', '--', 'knowledge/' + event['folder']):
            git(self.instance, 'add', '-A', '--', 'knowledge', 'canon')
            git(self.instance, 'commit', '-m', 'Publish ' + event['id'], '--', 'knowledge', 'canon')
        if sid:
            self.state['sessions'][sid]['status'] = 'integrated'
        if job:
            job.update(status='done', record=event['id'])
            if job['pipeline']:
                self.state['pipelines'][job['pipeline']].update(stage='done', record=event['id'])
        if event['kind'] == 'review':
            self.state['processed_concerns'] = sorted(set(self.state['processed_concerns']) | set(job['task']['concerns']))
            self.state['processed_conflicts'] = sorted(set(self.state['processed_conflicts']) | set(job['task']['conflicts']))
        self.notify(event)
        self.state['publication'] = None
        self.state['complete'] = root_solved(self.model)
        self.archive_due = True
        self.save()

    def notify(self, event):
        for sid, session in self.active():
            directory = self.session_dir(sid) / 'inbox'
            directory.mkdir(exist_ok=True)
            write_json(directory / (event['id'] + '.json'), {'event': event['id'], 'kind': event['kind'],
                                                            'revision': event['sequence'],
                                                            'text': 'The canon changed. Read the frontier and the elements concerned before relying on the change.'})

    def collect(self):
        if self.state['publication'] or self.state['publish_queue']:
            self.publish()
        for sid, s in list(self.active()):
            if s['status'] == 'publishing':
                # Its work is done and waits in the publication queue; publish() carries it from here.
                continue
            session = self.session_dir(sid)
            # Read again only when the file has changed (read_json_cached): this runs on every pass.
            current = read_json_cached(session / 'end-check.json')
            if current is not None and s.get('end_check') != current:
                s['end_check'] = current
                self.save()
            if not (session / 'GO').exists():
                (session / 'CANCEL').touch()
            data = read_json_cached(session / 'process.json')
            if data is not None and s.get('cli') != data['process']:
                s.update(cli=data['process'], cli_started_at=data['started_at'])
                self.save()
            if alive(s.get('host')) or alive(s.get('cli')):
                continue
            # The host has exited, so this poll reaps it. finish() takes the session off the active
            # list, after which no later pass would poll its host again.
            child = self.hosts.pop(sid, None)
            if child is not None:
                child.poll()
            exit_file = session / 'exit.json'
            if exit_file.exists():
                s.update(read_json(exit_file))
            self.finish(sid, s)

    def ensure_broker(self):
        """Start the Lean broker when none is alive, at most every ten seconds, without waiting for it."""
        from lean_broker import Paths, broker_alive, launch_broker
        if self.broker is not None and self.broker.poll() is not None:
            self.broker = None
        paths = Paths(self.instance)
        if broker_alive(paths) or time.monotonic() - self.broker_attempt < 10:
            return
        self.broker_attempt = time.monotonic()
        self.broker = launch_broker(paths)

    # -- the settled root against the root as it was posed ------------------------------------------------

    def check_root(self):
        """Once the root is formally settled, compare its statement with the root the first commit fixed.

        A formal settlement says that some declaration is proved in Lean from the allowed axioms and that
        Lean confirmed its statement to be the root's, or the negation of the root's. What remains to be
        shown is that the root's statement, with every definition it is made of, is still the one that
        was posed. Every publication is refused that would change a statement or a definition in place,
        so this holds by construction; here it is read off once more from the two ends, the index in the
        instance's first commit and the index as it stands (canon.statement_differences). The comparison
        reads two files and is repeated whenever the settling proof or the library's revision is another.

        A difference is kept with its description, and a comprehensive review of the settling proof is
        requested once for it, so that sessions examine what the settlement now rests on."""
        settlement = root_settlement(self.model)
        if settlement is None:
            return
        root = self.model['root']
        proof = sorted(settlement['proofs'], key=lambda name: (name != root, name))[0]
        record = self.state.get('root_check')
        if record and record['proof'] == proof and record['revision'] == self.model['revision']:
            return
        commit = git(self.instance, 'rev-list', '--max-parents=0', 'HEAD').split()[0]
        first = json.loads(git(self.instance, 'show', commit + ':canon/index.json'))
        differences = statement_differences(first, Canon(self.instance).load_index(), root)
        checked = {'proof': proof, 'revision': self.model['revision'], 'compared_with_commit': commit,
                   'status': 'changed' if differences else 'unchanged', 'differences': differences, 'at': time.time()}
        if differences and not (record and record['differences'] == differences):
            request = self.instance / 'control/requests' / (uid('request') + '.json')
            write_json(request, {'kind': 'review', 'elements': [proof], 'concerns': [],
                                 'reason': 'The root is formally settled, and its statement or a definition under it '
                                           'is not what the first commit of the instance fixed: '
                                           + '; '.join(differences)})
            checked['review_request'] = str(request)
        self.state['root_check'] = checked
        self.save()

    def conflicts(self):
        """Contested statements, each with the judgments that currently oppose one another.

        The key changes when a proof on either side is judged again, so the same opposition is
        examined once and a new one is a new cause."""
        elements = self.model['elements']
        keys = []
        for name in self.model['contested']:
            sides = [p for p in elements[name]['proofs'] if elements[p]['settled']]
            sides += [p for p in refuting_proofs(self.model, name) if p not in sides]
            keys.append(name + ':' + ','.join(sorted(str((elements[p]['verdict'] or {}).get('change')) for p in sides)))
        return keys

    def populate(self):
        model = self.model
        pending = [j for j in self.state['jobs'].values() if j['status'] in ('pending', 'running')]
        if not any(j['role'] == 'review' and j['task']['kind'] == 'comprehensive' for j in pending):
            concerns = [key for key, value in model['concerns'].items() if value['status'] != 'cleared' and key not in self.state['processed_concerns']]
            conflicts = [key for key in self.conflicts() if key not in self.state['processed_conflicts']]
            if concerns or conflicts:
                self.enqueue('review', {'kind': 'comprehensive', 'concerns': concerns, 'conflicts': conflicts,
                                        'purpose': 'Trace the questioned proofs to their evidence and through the elements that actually use them; report precise findings.'})
        # One formalizer at a time holds a statement whole, whichever of its proofs it was given, so a formalizer
        # still at work keeps the statement when the proof to formalize becomes another declaration of it.
        statement = lambda name: model['elements'].get(name, {}).get('statement_of') or name
        active = {statement(p['element']) for p in self.state['pipelines'].values()
                  if p['role'] == 'formalizer' and p['stage'] != 'done'}
        for name in formalizable(model):
            if statement(name) not in active:
                previous = [p['record'] for p in self.state['pipelines'].values()
                            if p['role'] == 'formalizer' and p['record'] and p['element'] == name]
                self.producer('formalizer', {'element': name, 'previous_changes': previous})
        due = [cid for cid, change in model['changes'].items() if cid not in model['organized']]
        if len(due) >= self.settings['organizer_every_records'] and not any(j['role'] == 'organizer' for j in pending):
            # make_pack fixes the batch from the published changes when the organizer launches.
            self.enqueue('organizer', {})

    def current_availability(self):
        return availability_view(self.model, board(self.instance, self.state, self.model),
                                 self.state['attempt_availability_epoch'])

    def finish_no_research(self, sid, session, job, outcome):
        """Terminal for this session even when its separate availability report is stale.

        An explorer that found no free question closes the same way; only attempts report occupancy."""
        observed = None
        if session['role'] == 'attempt':
            try:
                observed = reported_availability(self.session_dir(sid), outcome)
            except (OSError, ValueError) as exc:
                session['availability_report'] = {'status': 'invalid', 'error': str(exc)}
        if observed is not None:
            current = self.current_availability()
            if (observed['epoch'] != current['epoch']
                    or opening_since(observed, current)):
                session['availability_report'] = {'status': 'stale'}
            else:
                self.state['attempt_dispatch_gate'] = {
                    'mode': 'suppressed', 'reported_by': sid,
                    'snapshot': outcome['availability']['snapshot'],
                    'baseline': current, 'probe_session': None,
                    'reason': 'all_unresolved_work_occupied'}
                session['availability_report'] = {'status': 'accepted'}
        session.update(status='ended', disposition='no_research')
        job['status'] = 'done'
        self.state['pipelines'][job['pipeline']].update(stage='done', disposition='no_research')
        self.archive_due = True
        self.save()

    def attempt_dispatch_ready(self):
        gate = self.state['attempt_dispatch_gate']
        if gate is None:
            return True
        before = json.dumps(gate, sort_keys=True)
        current = self.current_availability()
        if gate['mode'] == 'suppressed':
            reason = opening_since(gate['baseline'], current)
            if reason:
                gate.update(mode='reassess', reason=reason, probe_session=None)
        # Track settled elements leaving the work that remains, so a later reopening is a new opportunity.
        # Additions and publication revisions alone do not release suppression.
        gate['baseline'] = current
        sid = gate['probe_session']
        if gate['mode'] == 'reassess' and sid:
            if section_entries(self.instance, sid, self.model):
                self.state['attempt_dispatch_gate'] = None
                self.save()
                return True
            if self.state['sessions'][sid]['status'] not in ACTIVE_STATUSES:
                gate['probe_session'] = None
        if before != json.dumps(gate, sort_keys=True):
            self.save()
        return gate['mode'] == 'reassess' and gate['probe_session'] is None

    def available_elements(self):
        """Elements of the work that remains where another attempt could still register a section.

        The runner does not judge whether mathematical work remains; it only refrains from launching
        an attempt when every element the frontier shows as remaining is held whole or already has a
        session waiting for its lease, since launching another attempt there would only lengthen that
        queue. Whether anything can be taken on is the attempt's judgment (reference/retained-work.md)."""
        rows = board(self.instance, self.state, self.model)
        whole = {s['element'] for r in rows for s in r['sections'] if s['whole']}
        leases = lease_table(self.instance, self.state, self.model)
        queued = {n for n, entry in leases.items() if entry['queue']}
        # Sections and leases stand on the statement, so another proof of it is held with it.
        statement = lambda name: self.model['elements'][name]['statement_of'] or name
        return [n for n in self.model['remaining'] if statement(n) not in whole and statement(n) not in queued]

    def launch_due(self):
        """Attempt and exploration launches share one spacing, so each new attempt or explorer can
        take its lease before the next one reads the board."""
        last = self.state.get('last_launch')
        return last is None or time.time() - last >= self.settings['launch_interval']

    def waits_for_its_kind(self, job):
        """Whether a comprehensive review or organizer waits for another of its kind that is running.

        Those launch one at a time: dispatch_pending() holds the waiting one back until the running one
        has finished."""
        if job['role'] == 'organizer' or (job['role'] == 'review' and job['task']['kind'] == 'comprehensive'):
            return any(other['status'] == 'running' and other['role'] == job['role']
                       and other['task'].get('kind') == job['task'].get('kind')
                       for other in self.state['jobs'].values())
        return False

    def question_view(self, launching=False):
        """Free, occupied and choosing questions as the runner counts them.

        While an exploration waits to launch or relaunch, its pipeline may still record a question:
        the runner's earlier assignment in its job, or the declaration of a failed session that the
        pipeline names as producer until the relaunch replaces it. No live explorer holds that
        question, and the pipeline is not choosing yet. When a pending exploration is launched, every
        pending exploration's pipeline is therefore left out, and such a question is free to whichever
        of them launches first. Leaving out only the launching job's own pipeline would let two pending
        explorations hold each other back for good: each would count the other as a chooser, or as the
        holder of the question it would itself take, while that question stays free."""
        rows = board(self.instance, self.state, self.model)
        if launching:
            pending = {j['pipeline'] for j in self.state['jobs'].values()
                       if j['role'] == 'explore' and j['status'] == 'pending'}
            rows = [row for row in rows if row['pipeline'] not in pending]
        return question_availability(self.instance, self.state, self.model, rows)

    def question_slot(self, launching=False):
        """Whether one more explorer could still find a question of its own.

        Explorers whose pipelines hold no question yet are choosing among the free questions. With
        launching, a pending exploration is being launched, and every pending exploration's
        pipeline is left out of the count (question_view): each waiting job is decided on its own
        pass, against the questions the launches before it leave free, and the one launched becomes
        a producing row that the next pass counts. Without a job to dispatch, waiting jobs count, so
        that schedule() does not create another exploration for a question a waiting one will take."""
        view = self.question_view(launching=launching)
        return len(view['free']) > len(view['choosing'])

    def dispatch_pending(self):
        changed = False
        for job in sorted(self.state['jobs'].values(), key=lambda j: PRIORITY[j['role']]):
            if job['status'] != 'pending' or len(self.active()) >= self.settings['max_sessions']:
                continue
            if self.state['complete'] and job['role'] in ('attempt', 'explore'):
                job['status'] = 'cancelled'
                if job['pipeline']:
                    self.state['pipelines'][job['pipeline']]['stage'] = 'done'
                changed = True
                continue
            if job['role'] == 'explore' and (not self.launch_due()
                                             or not self.question_slot(launching=True)):
                continue
            if job['role'] == 'formalizer' and job['task']['element'] not in formalizable(self.model):
                job['status'] = 'cancelled'
                self.state['pipelines'][job['pipeline']]['stage'] = 'done'
                changed = True
                continue
            if job['role'] == 'attempt':
                if not self.attempt_dispatch_ready():
                    continue
                if not self.available_elements():
                    continue
                if not self.launch_due():
                    continue
                if self.state['explore_requested'] and self.selection('explore') and self.question_slot():
                    # An exploration that can launch now outranks the attempt; schedule() creates it
                    # after this pass. A request without a free question does not hold the attempt.
                    continue
            if self.waits_for_its_kind(job):
                continue
            if job['not_before'] <= time.time() and self.selection(job['role']):
                self.dispatch(job['id'])
                changed = True
        if changed:
            self.save()

    def schedule(self):
        self.populate()
        self.dispatch_pending()
        if self.state['complete']:
            return
        while len(self.active()) < self.settings['max_sessions']:
            available = self.available_elements()
            self.attempt_dispatch_ready()
            suppressed = (self.state['attempt_dispatch_gate'] or {}).get('mode') == 'suppressed'
            if not available or suppressed:
                # Capacity that no attempt can use goes to understanding. The request is renewed
                # after every exploration launched here, so free questions fill one by one.
                if not self.state['explore_requested']:
                    self.state['explore_requested'] = True
                    self.save()
            if (self.state['explore_requested'] and self.launch_due()
                    and self.selection('explore') and self.question_slot()):
                # The request is consumed by the launch; without a free question it stays
                # in force until one opens, and attempts are not held for it. Before the launch
                # interval has passed the request waits; the attempt below waits for the same interval.
                key = self.producer('explore')
                if not self.dispatch(key):
                    # The queued exploration launches from dispatch_pending() on a later pass.
                    break
                continue
            # dispatch_pending() above has already filled free capacity in priority order, so a slot that
            # opened went to waiting review or peer work before any attempt. Work still pending waits for
            # its retry time, a model or another of its kind, not for capacity, and holds no attempt back.
            if (not available or not self.launch_due()
                    or not self.attempt_dispatch_ready() or not self.selection('attempt')):
                break
            key = self.producer('attempt')
            self.dispatch(key)

    def refresh(self):
        rows = board(self.instance, self.state, self.model)
        leases = lease_table(self.instance, self.state, self.model)
        investigations = [(j['id'], j['status']) for j in self.state['jobs'].values()
                          if j['role'] == 'review' and j['task']['kind'] == 'comprehensive']
        # Lease grant times change on every read of a free lease; the board shows only who holds and waits.
        holding = {n: ([h['session'] for h in e['holders']], [w['session'] for w in e['queue']]) for n, e in leases.items()}
        signature = json.dumps([rows, holding, self.model['sequence'], investigations], sort_keys=True)
        if signature != self.last_board:
            render(self.instance, self.model, rows, leases)
            self.last_board = signature

    def ingest_inputs(self):
        for path in sorted((self.instance / 'control/requests').glob('*.json')):
            if path.name in self.state['seen_requests']:
                continue
            request = read_json(path)
            if request['kind'] == 'questions':
                try:
                    reason, questions = operator_questions(
                        {key: value for key, value in request.items() if key != 'kind'}, self.model)
                except ValueError as exc:
                    # A question published since the command checked the file can take an ID.
                    # The refusal is left in status for the operator, and the runner continues.
                    self.state['last_error'] = {'at': time.time(),
                                                'error': f'questions request {path.name} refused: {exc}'}
                    self.state['seen_requests'].append(path.name)
                    self.save()
                    continue
                # Another publication can be underway, waiting for its build. The questions take their
                # turn in the same queue, and the request counts as collected in the same save, so it is
                # never published twice.
                self.state['publish_queue'].append({'kind': 'questions', 'reason': reason, 'questions': questions,
                                                    'at': time.time()})
                self.state['seen_requests'].append(path.name)
                self.save()
                self.publish()
                continue
            if request['kind'] == 'review':
                task = {'kind': 'comprehensive', 'concerns': request['concerns'], 'conflicts': [],
                        'requested_elements': request['elements'], 'purpose': request['reason']}
                self.enqueue('review', task, key='operator:' + path.stem)
            elif request['kind'] == 'organize':
                self.enqueue('organizer', {}, key='operator:' + path.stem)
            elif request['kind'] == 'reconsider-attempts':
                self.state['attempt_availability_epoch'] += 1
                probe = (self.state['attempt_dispatch_gate'] or {}).get('probe_session')
                if self.state['sessions'].get(probe, {}).get('status') not in ACTIVE_STATUSES:
                    probe = None
                self.state['attempt_dispatch_gate'] = {
                    'mode': 'reassess', 'reported_by': None, 'snapshot': None,
                    'baseline': self.current_availability(), 'probe_session': probe,
                    'reason': 'operator_request'}
            else:
                raise ValueError('unknown operator request')
            self.state['seen_requests'].append(path.name)
            self.save()

    def archive(self):
        if self.archiver is not None and self.archiver.poll() is not None:
            self.archiver = None
        if self.archive_due and self.archiver is None:
            self.archive_due = False
            with (self.instance / 'runner/archive.log').open('ab') as log:
                self.archiver = subprocess.Popen([sys.executable, '-B', str(SCRIPT), '_archive', str(self.instance)],
                                                cwd=self.instance, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                                **popen_options(detached=True))

    def reload_settings(self):
        """Apply settings.json when it changes; keep the last valid settings if an edit is rejected."""
        try:
            stamp = file_stamp(self.instance / 'settings.json')
            if stamp == self.settings_stamp and not self.state.get('settings_error'):
                return
            self.settings_stamp = stamp
            self.settings = load_settings(self.instance)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # As in the Lean broker, a file caught mid-write may not change its stamp again,
            # so a rejected edit is read again on every tick until it is accepted.
            if (self.state.get('settings_error') or {}).get('error') != str(exc):
                self.state['settings_error'] = {'at': time.time(), 'error': str(exc)}
                self.save()
            return
        if self.state.get('settings_error'):
            self.state['settings_error'] = None
            self.save()

    def tick(self):
        self.collect()
        self.archive()
        self.reload_settings()
        complete = root_solved(self.model)
        if self.state['complete'] != complete:
            self.state['complete'] = complete
            self.save()
        # Before the requests are read, so that the review a difference asked for is taken up in this pass.
        self.check_root()
        self.ingest_inputs()
        self.attempt_dispatch_ready()
        self.refresh()
        if not (self.instance / 'control/STOP').exists():
            self.schedule()
        remaining = any(j['status'] in ('pending', 'running') for j in self.state['jobs'].values())
        finished = self.state['complete'] and not self.active() and not remaining
        if self.state['finished'] != finished:
            self.state['finished'] = finished
            self.save()
        if not self.state['finished']:
            self.ensure_broker()
        # A running archiver uses an earlier state snapshot. Dispatch any later
        # archive request before exiting; the final detached archiver can finish alone.
        return self.state['finished'] and not self.archive_due

    def run(self, token=None):
        with InstanceLock(self.instance / 'runner/lock'):
            self.state = read_json(self.state_path)
            self.reserve = EmergencyMemory()
            self.archive_due = True
            write_json(self.instance / 'runner/process.json', {'process': self.identity, 'token': token, 'at': time.time()})
            print(json.dumps({'started': self.identity, 'token': token, 'instance': str(self.instance)}), flush=True)
            while True:
                try:
                    if self.reserve.buffer is None:
                        if available_memory() < 512 * 1024 * 1024:
                            time.sleep(5)
                            continue
                        self.reserve.restore()
                        self.state = read_json(self.state_path)
                        self.model = replay(self.instance)
                        self.last_board = None
                    if self.tick():
                        return
                except MemoryError:
                    self.reserve.release()
                except Exception as exc:
                    # Log before saving: a second storage error must not erase
                    # the original failure's operation and call stack.
                    traceback.print_exc(file=sys.stderr)
                    self.state['last_error'] = {'at': time.time(), 'error': str(exc)}
                    self.save()
                    print(json.dumps({'error': str(exc)}), file=sys.stderr, flush=True)
                    raise
                time.sleep(0.25)


def start(instance):
    instance = Path(instance).resolve()
    token = uuid.uuid4().hex
    stdout = instance / 'runner' / ('start-' + token + '.stdout.log')
    stderr = instance / 'runner' / ('start-' + token + '.stderr.log')
    with stdout.open('wb') as out, stderr.open('wb') as err:
        child = subprocess.Popen([sys.executable, '-B', str(SCRIPT), 'run', str(instance), '--token', token],
                                 cwd=instance, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                 **popen_options(detached=True))
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        path = instance / 'runner/process.json'
        if path.exists():
            receipt = read_json(path)
            if receipt.get('token') == token and token in stdout.read_text(encoding='utf-8'):
                if alive(receipt['process']) or read_json(instance / 'runner/state.json')['finished']:
                    # The runner's own start record names the process to end. On Windows a virtual
                    # environment's python.exe is a redirector, and the runner is its child process.
                    return {'pid': receipt['process']['pid'], 'stdout': str(stdout), 'stderr': str(stderr),
                            'instance': str(instance)}
        if child.poll() is not None:
            raise RuntimeError('runner exited before readiness; read ' + str(stderr))
        time.sleep(0.05)
    raise RuntimeError('readiness unconfirmed; inspect ' + str(stdout) + ' and ' + str(stderr) + ' before retrying')


def status(instance):
    instance = Path(instance).resolve()
    state = read_json(instance / 'runner/state.json')
    path = instance / 'runner/process.json'
    receipt = read_json(path) if path.exists() else None
    model = replay(instance)
    from lean_broker import Paths, broker_status
    rows = board(instance, state, model)
    return {'instance': str(instance), 'runner_alive': bool(receipt and alive(receipt['process'])),
            'root_state': model['root_state'], 'finished': state['finished'],
            # Whether the formally settled root still states what the first commit fixed (Runner.check_root);
            # nothing until the root is formally settled and a runner has seen it.
            'root_check': state.get('root_check'),
            'stopped': (instance / 'control/STOP').exists(), 'board': rows,
            'attempt_dispatch': state['attempt_dispatch_gate'],
            'questions': {**question_availability(instance, state, model, rows),
                          'explore_requested': state['explore_requested']},
            'blocks': state['blocks'], 'lean': broker_status(Paths(instance)), 'state': state}


def archive_finished(instance):
    import lzma
    import tarfile
    try:
        with InstanceLock(Path(instance) / 'runner/archive-lock', 'archiver'):
            state = read_json(Path(instance) / 'runner/state.json')
            for sid, session in state['sessions'].items():
                job = state['jobs'][session['job']]
                pipeline = state['pipelines'].get(job['pipeline'])
                finished = pipeline['stage'] == 'done' if pipeline else job['status'] in ('done', 'cancelled')
                if finished and session['status'] not in ACTIVE_STATUSES:
                    try:
                        archive_work(Path(instance) / 'sessions' / sid)
                    except (OSError, ValueError, RuntimeError, tarfile.TarError, lzma.LZMAError, EOFError) as exc:
                        print(json.dumps({'session': sid, 'error': str(exc)}), file=sys.stderr, flush=True)
    except RuntimeError:
        pass
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'start', 'run', 'status', 'stop', 'resume', 'input', 'render', 'review', 'organize', 'reconsider-attempts', 'questions', 'restart-broker', 'kill-session', '_session', '_archive'):
        p = sub.add_parser(name)
        p.add_argument('instance', type=Path)
        if name == 'init':
            p.add_argument('--root', required=True, type=Path, help='the root statement in words')
            p.add_argument('--canon', required=True, type=Path,
                           help='a folder with lean/ and records/ for the root and the objects it speaks of')
            p.add_argument('--root-declaration', required=True, help='the Lean name of the root statement')
            p.add_argument('--settings', type=Path)
        if name == 'run':
            p.add_argument('--token')
        if name in ('input', 'questions'):
            p.add_argument('--file', required=True, type=Path)
        if name == 'kill-session':
            p.add_argument('session')
        if name == 'review':
            p.add_argument('--element', action='append', default=[])
            p.add_argument('--concern', action='append', default=[])
            p.add_argument('--reason', default='Operator requested renewed examination.')
    args = parser.parse_args(argv)
    instance = args.instance.resolve()
    try:
        result = {'instance': str(instance)}
        if args.command == '_session':
            return session_host(instance)
        if args.command == '_archive':
            return archive_finished(instance)
        if args.command != 'init':
            instance_metadata(instance)  # refuses an instance that the earlier runtime created
        if args.command == 'init':
            initialize(instance, args.root, args.canon, args.root_declaration, args.settings)
        elif args.command == 'run':
            Runner(instance).run(args.token)
        elif args.command == 'start':
            result = start(instance)
        elif args.command == 'status':
            result = status(instance)
        elif args.command == 'stop':
            (instance / 'control/STOP').touch()
        elif args.command == 'resume':
            (instance / 'control/STOP').unlink(missing_ok=True)
        elif args.command == 'input':
            content = args.file.read_text(encoding='utf-8-sig')
            if not content.strip():
                raise ValueError('empty user input')
            path = instance / 'control/inputs' / (f'{time.time_ns()}-' + uuid.uuid4().hex + '.txt')
            write_text(path, content)
            result['input'] = str(path)
        elif args.command == 'render':
            with InstanceLock(instance / 'runner/lock'):
                render(instance, replay(instance), board(instance), lease_table(instance))
        elif args.command == 'kill-session':
            state = read_json(instance / 'runner/state.json')
            if args.session not in state['sessions']:
                raise ValueError('unknown session')
            directory = instance / 'sessions' / args.session
            receipt = read_json(directory / 'process.json') if (directory / 'process.json').exists() else {'process': None}
            if alive(state['sessions'][args.session].get('host')) or alive(receipt['process']):
                # A persistent cancellation also covers the gap between turns.
                (directory / 'CANCEL').touch()
            if alive(receipt['process']):
                terminate_process(receipt['process'])
            elif not alive(state['sessions'][args.session].get('host')):
                raise ValueError('session is no longer running')
            result['terminated'] = args.session
        elif args.command in ('review', 'organize', 'reconsider-attempts'):
            request = {'kind': args.command}
            if args.command == 'review':
                if not (args.element or args.concern):
                    raise ValueError('name the evidence to review with --element or --concern')
                model = replay(instance)
                if any(e not in model['elements'] for e in args.element) or any(c not in model['concerns'] for c in args.concern):
                    raise ValueError('unknown review target')
                request.update(elements=args.element, concerns=args.concern, reason=args.reason)
            path = instance / 'control/requests' / (uid('request') + '.json')
            write_json(path, request)
            result['request'] = str(path)
        elif args.command == 'questions':
            reason, questions = operator_questions(json.loads(args.file.read_text(encoding='utf-8-sig')),
                                                   replay(instance))
            path = instance / 'control/requests' / (uid('request') + '.json')
            write_json(path, {'kind': 'questions', 'reason': reason, 'questions': questions})
            result['request'] = str(path)
        elif args.command == 'restart-broker':
            from lean_broker import Paths, broker_status, ensure_broker
            state = read_json(instance / 'runner/state.json')
            if not (instance / 'control/STOP').exists():
                raise ValueError('stop new dispatch before replacing the Lean environment')
            # A session held behind STOP for its next turn has no running CLI and
            # continues with the replaced broker after resume. A session whose work waits
            # for publication has no CLI either; publication goes on under the stop.
            held, active, publishing = [], [], []
            for sid, s in state['sessions'].items():
                if s['status'] not in ACTIVE_STATUSES:
                    continue
                if s['status'] == 'publishing':
                    publishing.append(sid)
                    continue
                check = instance / 'sessions' / sid / 'end-check.json'
                waiting = check.is_file() and read_json(check)['status'] == 'waiting_dispatch'
                (held if waiting and not alive(s.get('cli')) else active).append(sid)
            if active:
                raise ValueError('let active CLI turns finish before replacing the Lean environment: '
                                 + ', '.join(sorted(active)))
            if publishing:
                raise ValueError('let the publications under way finish before replacing the Lean environment; '
                                 'the work of these sessions waits in state.publication or state.publish_queue: '
                                 + ', '.join(sorted(publishing)))
            result['held_sessions'] = sorted(held)
            paths = Paths(instance)
            current = broker_status(paths)
            if current['queued'] or current['running']:
                raise ValueError('wait for queued/running Lean jobs to finish or be cancelled')
            if current['broker_alive']:
                identity = current['broker']['process']
                terminate_process(identity)
                deadline = time.monotonic() + 10
                while alive(identity) and time.monotonic() < deadline:
                    time.sleep(.05)
                if alive(identity):
                    raise RuntimeError('broker termination not yet confirmed')
            result['broker'] = ensure_broker(paths)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
