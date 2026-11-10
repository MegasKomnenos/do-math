"""Fresh-instance do-math runner: autonomous work, peer development, independent review."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback
import uuid

from check import check_session, regular_tree, tree_hashes
from cli_adapter import provider_for_model
from launch import worker_command as build_command
from coordination import (ACTIVE_STATUSES, board, claims_lock, lease_table, question_availability,
                          question_entry, section_entries)
from availability import (availability_view, no_research_outcome, opening_since,
                          reported_availability)
from knowledge import (ROOT_QUESTION, canonical, formal_ready, render, replay, root_solved,
                       sufficient_closure)
from retention import capture, refusal
from ending import ROLES as END_CHECK_ROLES, authorize, turn_directory
from runtime_support import (EmergencyMemory, InstanceLock, alive, archive_work, available_memory, file_stamp, git,
                             popen_options, process_identity, read_json, remove_tree, rename_directory, session_host,
                             terminate_process, write_json, write_text)
from settings import PRODUCERS, defaults, load_settings, validate

SCRIPT = Path(__file__).resolve()
RUNTIME = SCRIPT.parent
SKILL = RUNTIME.parent
PRIORITY = {'review': 0, 'peer': 1, 'formalizer': 2, 'organizer': 3, 'explore': 4, 'attempt': 5}
QUESTION_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*')


def uid(prefix):
    return prefix + uuid.uuid4().hex


def operator_questions(data, model):
    """The reason and questions of an operator publication, checked against the current research.

    The questions command checks its file with this, and the runner checks the request again when it
    collects it, because a question or node with the same ID can be published in between."""
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
    taken = set(model['questions']) | set(model['question_aliases']) | set(model['nodes']) | set(model['aliases'])
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('each question is an object with "id", "statement" and "grounds"')
        extra = sorted(set(item) - {'id', 'statement', 'grounds'})
        if extra:
            raise ValueError('unknown key in a question: ' + ', '.join(extra))
        qid = item.get('id')
        if not isinstance(qid, str) or not QUESTION_ID.fullmatch(qid):
            raise ValueError(f'invalid question id: {qid!r}')
        if qid == ROOT_QUESTION:
            raise ValueError('q0 is the root question, which the runtime creates')
        if qid in seen:
            raise ValueError('duplicate question id: ' + qid)
        if qid in taken:
            raise ValueError('question id already names a question, question alias, node or node alias: ' + qid)
        for key in ('statement', 'grounds'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'question {qid} needs a nonempty "{key}"')
        seen.add(qid)
    return reason, [{'id': q['id'], 'statement': q['statement'], 'grounds': q['grounds']} for q in items]


def initialize(instance, root_file, settings_file=None):
    instance = Path(instance).resolve()
    root = Path(root_file).read_bytes()
    if not root.decode('utf-8-sig').strip():
        raise ValueError('the root statement must be nonempty UTF-8')
    config = validate(read_json(settings_file)) if settings_file else defaults()
    instance.mkdir(parents=True, exist_ok=False)
    for name in ('knowledge/events', 'knowledge/records', 'knowledge/reviews', 'knowledge/organizations',
                 'sessions', 'runner', 'control/inputs', 'control/requests'):
        (instance / name).mkdir(parents=True)
    (instance / 'root.md').write_bytes(root)
    write_json(instance / 'instance.json', {'schema': 1, 'root_sha256': hashlib.sha256(root).hexdigest()})
    write_json(instance / 'settings.json', config)
    write_text(instance / '.gitignore', '/sessions/\n/runner/\n/control/\n')
    state = {'schema': 1, 'sessions': {}, 'pipelines': {}, 'jobs': {}, 'blocks': {},
             'attempt_launches': 0,
             'attempt_availability_epoch': 0, 'attempt_dispatch_gate': None,
             'explore_requested': False, 'complete': False,
             'processed_concerns': [], 'processed_conflicts': [], 'publication': None,
             'seen_requests': [], 'last_error': None, 'finished': False}
    write_json(instance / 'runner/state.json', state)
    render(instance, replay(instance), [])
    git(instance, 'init')
    git(instance, 'add', '--', 'root.md', 'settings.json', 'instance.json', '.gitignore', 'knowledge')
    git(instance, 'commit', '-m', 'Initialize autonomous mathematical research')


class Runner:
    def __init__(self, instance, skill=SKILL):
        self.instance = Path(instance).resolve()
        self.skill = Path(skill).resolve()
        if not (self.instance / '.git').is_dir():
            raise ValueError('fresh instance with its own Git required')
        metadata = read_json(self.instance / 'instance.json')
        if metadata.get('schema') != 1 or hashlib.sha256((self.instance / 'root.md').read_bytes()).hexdigest() != metadata['root_sha256']:
            raise ValueError('root statement changed; a changed mathematical problem requires a new instance')
        self.settings = load_settings(self.instance)
        self.state_path = self.instance / 'runner/state.json'
        self.state = read_json(self.state_path)
        self.identity = process_identity(os.getpid())
        self.hosts = {}
        self.broker = None
        self.broker_attempt = 0
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
                                         'node': (task or {}).get('node'), 'previous_peers': []}
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
            job['task']['batch'] = [r for r in self.model['records'] if r not in self.model['organized']]
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
                    # The assigned node is the formalizer's whole section; it registers nothing itself.
                    now = time.time()
                    write_json(session / 'declaration.json', {'sections': [
                        {'id': sid + '-1', 'node': job['task']['node'], 'whole': True, 'statement': None,
                         'reasons': {}, 'at': now}], 'at': now})
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
            command = build_command(self.settings['cli'][provider], selected['model'], selected['effort'], session,
                                    self.settings['mcp_servers'])
            launch = {'runner': self.identity, 'command': {'argv': command.argv, 'cwd': str(command.cwd)}}
            if job['role'] in END_CHECK_ROLES:
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
            policy = read_json(session / 'launch.json').get('end_check')
            if policy is not None:
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
                signal['attempts'] = previous.get('attempts', 0) + 1
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
                except (OSError, ValueError, TypeError, KeyError) as exc:
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
            s['status'] = 'ended'
            job['status'] = 'done'
            pipeline = self.state['pipelines'][job['pipeline']]
            pipeline['stage'] = 'peer'
            self.enqueue('peer', {'source': str(session), 'source_role': s['role'],
                                  'node': pipeline['node'], 'sections': self.producer_sections(sid),
                                  'question': self.producer_question(sid)},
                         pipeline['id'], pipeline['id'] + ':peer')
            self.save()
            return
        # A cancellation recorded by the host, even after a clean CLI exit between turns,
        # leaves this stage unfinished; a replacement receives the partial material.
        authorization = s.get('end_check', {}).get('authorization') or {}
        interrupted = authorization.get('basis') == 'interrupted'
        # Any other end authorization by the host (a worker decision, the resumption limit or an
        # unavailable resumption) ends a peer normally, even when its last turn stopped at the
        # output-token cap with a nonzero exit; its output then goes to the structural check.
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
                    and errors == ['candidate changed after review assignment']):
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
            kind = 'record'
        elif s['role'] == 'review':
            kind = 'review'
        else:
            kind = 'organization'
        self.prepare_publication(sid, job, kind)
        self.publish()

    def producer_sections(self, sid):
        """The sections a producer registered, as a peer assignment lists them."""
        return [{key: entry.get(key) for key in ('id', 'node', 'whole', 'statement')}
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
        # A new peer gets the original research and earlier peer work. The cancelled
        # review remains in history; the new peer's own review receives a distinct job.
        self.retry(job, session, reason, availability=False)
        job['status'] = 'cancelled'
        pipeline = self.state['pipelines'][job['pipeline']]
        if peer.name not in pipeline['previous_peers']:
            pipeline['previous_peers'].append(peer.name)
        pipeline['stage'] = 'peer'
        self.enqueue('peer', {'source': task['source'], 'source_role': pipeline['role'],
                             'node': pipeline['node'], 'sections': self.producer_sections(pipeline['producer']),
                             'question': self.producer_question(pipeline['producer']),
                             'previous_error': reason,
                             'previous_partial_sessions': [str(self.session_dir(x)) for x in pipeline['previous_peers']]},
                     pipeline['id'], pipeline['id'] + ':peer-recovery:' + session['id'])
        self.save()

    def prepare_publication(self, sid, job, kind):
        rid = uid({'record': 'r', 'review': 'v', 'organization': 'o'}[kind])
        folder = {'record': 'records/', 'review': 'reviews/', 'organization': 'organizations/'}[kind] + rid
        event = {'id': rid, 'kind': kind, 'sequence': self.model['sequence'] + 1, 'folder': folder,
                 'session': sid, 'at': time.time()}
        if kind == 'record':
            pipeline = self.state['pipelines'][job['pipeline']]
            event.update(producer_role=pipeline['role'], pipeline=pipeline['id'], node=pipeline['node'])
        self.state['publication'] = {'event': event, 'job': job['id'], 'session': sid}
        self.state['sessions'][sid].update(status='publishing', record=rid)
        self.save()

    def prepare_questions(self, request, reason, questions):
        """An operator publication of questions, which has no session or job behind it.

        Its content is saved with the publication's identity, so a restart writes the same files, and
        the request counts as collected in the same save, so it is never published twice."""
        eid = uid('q')
        now = time.time()
        event = {'id': eid, 'kind': 'questions', 'sequence': self.model['sequence'] + 1,
                 'folder': 'questions/' + eid, 'at': now, 'source': 'operator'}
        self.state['publication'] = {'event': event, 'job': None, 'session': None,
                                     'questions': {'source': 'operator', 'reason': reason,
                                                   'questions': questions, 'at': now}}
        self.state['seen_requests'].append(request)
        self.save()

    def publish(self):
        publication = self.state['publication']
        if not publication:
            return
        event = publication['event']
        sid = publication['session']
        job = self.state['jobs'][publication['job']] if publication['job'] else None
        destination = self.instance / 'knowledge' / event['folder']
        if not destination.exists():
            stage = self.instance / 'runner' / ('stage-' + event['id'])
            if stage.exists():
                remove_tree(stage)
            if event['kind'] == 'record':
                candidate = Path(job['task']['candidate'])
                regular_tree(candidate)
                shutil.copytree(candidate, stage)
                if tree_hashes(stage) != job['task']['candidate_hashes']:
                    # The damaged candidate stays where review read it; its staged copy is not evidence.
                    remove_tree(stage)
                    self.state['publication'] = None
                    session = self.state['sessions'][sid]
                    session['record'] = None
                    self.recover_candidate(job, session, 'candidate changed after review assignment')
                    return
                shutil.copytree(self.session_dir(sid) / 'output', stage / 'review')
                pipeline = self.state['pipelines'][job['pipeline']]
                write_json(stage / 'provenance.json', {'producer_session': pipeline['producer'], 'peer_session': pipeline['peer'],
                                                      'review_session': sid, 'pipeline': pipeline['id']})
                self.copy_formal_evidence(stage, sid)
            elif event['kind'] == 'questions':
                stage.mkdir()
                write_json(stage / 'questions.json', publication['questions'])
            else:
                shutil.copytree(self.session_dir(sid) / 'output', stage)
            # knowledge/questions/ appears with an instance's first operator publication of questions.
            destination.parent.mkdir(exist_ok=True)
            rename_directory(stage, destination)
        event_path = self.instance / 'knowledge/events' / (event['id'] + '.json')
        if not event_path.exists():
            write_json(event_path, event)
        self.model = replay(self.instance)
        self.attempt_dispatch_ready()
        render(self.instance, self.model, board(self.instance, self.state, self.model),
               lease_table(self.instance, self.state, self.model))
        if not git(self.instance, 'log', '-1', '--format=%H', '--', 'knowledge/' + event['folder']):
            git(self.instance, 'add', '-A', '--', 'knowledge')
            git(self.instance, 'commit', '-m', 'Publish ' + event['id'], '--', 'knowledge')
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

    def copy_formal_evidence(self, stage, sid):
        assessment = read_json(stage / 'review/assessment.json')
        from lean_broker import Paths, job_record, BUILD_ID
        paths = Paths(self.instance)
        for item in assessment['solutions']:
            if item['level'] != 'formal':
                continue
            jid = item['formal_check']['job']
            receipt = job_record(paths, jid)
            if receipt['status'] == 'duplicate':  # the audit followed it to the original submission
                receipt = job_record(paths, receipt['duplicate_of'])
            # The folder keeps the ID the reviewer recorded, so formal_check.job still leads here.
            directory = stage / 'review/lean-evidence' / jid
            directory.mkdir(parents=True, exist_ok=True)
            write_json(directory / 'result.json', receipt)
            jobs = [m['job'] for m in receipt['modules'].values() if m.get('job')] if BUILD_ID.match(jid) else [receipt['id']]
            for job_id in jobs:
                target = directory / job_id
                target.mkdir(exist_ok=True)
                for name in ('result.json', 'stdout.log', 'stderr.log', 'launch.json'):
                    source = paths.job(job_id) / name
                    if source.exists():
                        # launch.json includes the environment; preserve command evidence without environment values.
                        if name == 'launch.json':
                            launch = read_json(source)
                            write_json(target / name, {k: launch[k] for k in ('argv', 'cwd') if k in launch})
                        else:
                            shutil.copyfile(source, target / name)

    def notify(self, event):
        for sid, session in self.active():
            directory = self.session_dir(sid) / 'inbox'
            directory.mkdir(exist_ok=True)
            write_json(directory / (event['id'] + '.json'), {'event': event['id'], 'kind': event['kind'],
                                                            'revision': event['sequence'],
                                                            'text': 'Shared research changed. Read the frontier, index and relevant evidence before relying on the change.'})

    def collect(self):
        if self.state['publication']:
            self.publish()
        for sid, s in list(self.active()):
            session = self.session_dir(sid)
            ending = session / 'end-check.json'
            if ending.exists():
                current = read_json(ending)
                if s.get('end_check') != current:
                    s['end_check'] = current
                    self.save()
            if not (session / 'GO').exists():
                (session / 'CANCEL').touch()
            receipt = session / 'process.json'
            if receipt.exists():
                data = read_json(receipt)
                if s.get('cli') != data['process']:
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

    def formalizable(self, nid, closure):
        """The proofs a formalizer is sent to formalize on canonical node nid, or none.

        A node qualifies while it is informally proved or refuted and an accepted relation carries that
        outcome to the root (closure, from sufficient_closure); a settled node off every such path is not
        formalized. Its qualifying proofs are those formal_ready accepts."""
        node = self.model['nodes'][nid]
        if node['state'] not in ('informal_proved', 'informal_refuted'):
            return []
        if (nid, node['state'].split('_', 1)[1]) not in closure:
            return []
        return [p for p in node['proofs'] if formal_ready(self.model, self.model['proofs'][p])]

    def populate(self):
        model = self.model
        pending = [j for j in self.state['jobs'].values() if j['status'] in ('pending', 'running')]
        if not any(j['role'] == 'review' and j['task']['kind'] == 'comprehensive' for j in pending):
            concerns = [key for key, value in model['concerns'].items() if value['status'] != 'cleared' and key not in self.state['processed_concerns']]
            conflicts = [nid + ':' + ','.join(n['proofs']) for nid, n in model['nodes'].items()
                         if n['canonical'] == nid and n['contested'] and nid + ':' + ','.join(n['proofs']) not in self.state['processed_conflicts']]
            if concerns or conflicts:
                self.enqueue('review', {'kind': 'comprehensive', 'concerns': concerns, 'conflicts': conflicts,
                                        'purpose': 'Trace the questioned claims to their evidence and through actual dependent uses; report precise findings.'})
        closure = sufficient_closure(model)
        for nid, node in model['nodes'].items():
            if node['canonical'] != nid:
                continue
            if any(p['role'] == 'formalizer' and p['stage'] != 'done' and canonical(model, p['node']) == nid for p in self.state['pipelines'].values()):
                continue
            proofs = self.formalizable(nid, closure)
            if proofs:
                previous = [p['record'] for p in self.state['pipelines'].values() if p['role'] == 'formalizer' and p['record'] and canonical(model, p['node']) == nid]
                self.producer('formalizer', {'node': nid, 'proofs': proofs, 'previous_records': previous})
        due = [rid for rid in model['records'] if rid not in model['organized']]
        if len(due) >= self.settings['organizer_every_records'] and not any(j['role'] == 'organizer' for j in pending):
            # make_pack fixes the batch from the published records when the organizer launches.
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
            except (OSError, ValueError, TypeError, KeyError) as exc:
                session['availability_report'] = {'status': 'invalid', 'error': str(exc)}
        if observed is not None:
            current = self.current_availability()
            if (observed['epoch'] != current['epoch']
                    or opening_since(observed, current, self.model)):
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
            reason = opening_since(gate['baseline'], current, self.model)
            if reason:
                gate.update(mode='reassess', reason=reason, probe_session=None)
        # Track solved nodes disappearing, so a later reopening is a new opportunity.
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

    def available_nodes(self):
        """Unresolved nodes where another attempt could still register a section.

        A node is unavailable while any pipeline holds it whole, or while a session already waits
        for its lease: launching another attempt there would only lengthen that queue."""
        rows = board(self.instance, self.state, self.model)
        whole = {s['node'] for r in rows for s in r['sections'] if s['whole']}
        leases = lease_table(self.instance, self.state, self.model)
        queued = {n for n, entry in leases.items() if entry['queue']}
        return [n for n, v in self.model['nodes'].items()
                if v['canonical'] == n and v['state'] == 'unresolved' and n not in whole and n not in queued]

    def launch_due(self):
        """Attempt and exploration launches share one spacing, so each new attempt or explorer can
        take its lease before the next one reads the board."""
        last = self.state.get('last_launch')
        return last is None or time.time() - last >= self.settings['launch_interval']

    def waits_for_its_kind(self, job):
        """Whether a comprehensive review or organizer waits for another of its kind that is running.

        Those launch one at a time: dispatch_pending() holds the waiting one back. It then takes the slot
        the running one frees, ahead of any attempt, so it does not hold fresh attempts back as peer or
        review work waiting for capacity or an available model does."""
        if job['role'] == 'organizer' or (job['role'] == 'review' and job['task']['kind'] == 'comprehensive'):
            return any(other['status'] == 'running' and other['role'] == job['role']
                       and other['task'].get('kind') == job['task'].get('kind')
                       for other in self.state['jobs'].values())
        return False

    def peer_or_review_waiting(self):
        """Whether a peer or review job waits to launch; fresh attempts are held back while one does.

        A comprehensive review that waits only for another of its kind does not count: it takes the slot
        that one frees, ahead of any attempt (waits_for_its_kind)."""
        return any(j['status'] == 'pending' and j['role'] in ('peer', 'review') and not self.waits_for_its_kind(j)
                   for j in self.state['jobs'].values())

    def question_view(self, launching=False):
        """Free, occupied and choosing questions as the runner counts them.

        While an exploration waits to launch or relaunch, its pipeline may still record a question:
        the runner's earlier assignment in its job, or the declaration of a failed session that the
        pipeline names as producer until the relaunch replaces it. No live explorer holds that
        question, and the pipeline is not choosing yet. When a pending exploration is launched, every
        pending exploration's pipeline is therefore left out, and such a question is free to whichever
        of them launches first. Leaving out only the launching job's own pipeline let two pending
        explorations hold each other back for good: each counted the other as a chooser, or as the
        holder of the question it would itself take, while that question stayed free."""
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
            if job['role'] == 'formalizer':
                ready = self.formalizable(canonical(self.model, job['task']['node']), sufficient_closure(self.model))
                if not ready:
                    job['status'] = 'cancelled'
                    self.state['pipelines'][job['pipeline']]['stage'] = 'done'
                    changed = True
                    continue
                job['task']['proofs'] = ready
            if job['role'] == 'attempt':
                if not self.attempt_dispatch_ready():
                    continue
                if not self.available_nodes():
                    continue
                if self.peer_or_review_waiting():
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
            nodes = self.available_nodes()
            self.attempt_dispatch_ready()
            suppressed = (self.state['attempt_dispatch_gate'] or {}).get('mode') == 'suppressed'
            if not nodes or suppressed:
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
            waiting = self.peer_or_review_waiting()
            # dispatch_pending() above has already launched each peer, review or organizer job that could
            # launch; what remains waits for its retry time, a model or another of its kind. Of those, only
            # a waiting peer or review holds the attempt back.
            if (waiting or not nodes or not self.launch_due()
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
                if self.state['publication']:
                    # Its event holds the next sequence number; the questions wait for a later pass.
                    break
                try:
                    reason, questions = operator_questions(
                        {key: value for key, value in request.items() if key != 'kind'}, self.model)
                except ValueError as exc:
                    # A question or node published since the command checked the file can take an ID.
                    # The refusal is left in status for the operator, and the runner continues.
                    self.state['last_error'] = {'at': time.time(),
                                                'error': f'questions request {path.name} refused: {exc}'}
                    self.state['seen_requests'].append(path.name)
                    self.save()
                    continue
                self.prepare_questions(path.name, reason, questions)
                self.publish()
                continue
            if request['kind'] == 'review':
                task = {'kind': 'comprehensive', 'concerns': request['concerns'], 'conflicts': [],
                        'requested_records': request['records'], 'requested_nodes': request['nodes'],
                        'purpose': request['reason']}
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
                except (OSError, ValueError, KeyError, RuntimeError) as exc:
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
            'root_state': model['nodes'][canonical(model, 'root')]['state'], 'finished': state['finished'],
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
            p.add_argument('--root', required=True, type=Path)
            p.add_argument('--settings', type=Path)
        if name == 'run':
            p.add_argument('--token')
        if name in ('input', 'questions'):
            p.add_argument('--file', required=True, type=Path)
        if name == 'kill-session':
            p.add_argument('session')
        if name == 'review':
            p.add_argument('--record', action='append', default=[])
            p.add_argument('--node', action='append', default=[])
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
        if args.command != 'init' and read_json(instance / 'instance.json').get('schema') != 1:
            raise ValueError('a fresh-runtime instance is required')
        if args.command == 'init':
            initialize(instance, args.root, args.settings)
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
                if not (args.record or args.node or args.concern):
                    raise ValueError('name the evidence to review with --record, --node or --concern')
                model = replay(instance)
                if any(r not in model['records'] for r in args.record) or any(n not in model['nodes'] for n in args.node) or any(c not in model['concerns'] for c in args.concern):
                    raise ValueError('unknown review target')
                request.update(records=args.record, nodes=args.node, concerns=args.concern, reason=args.reason)
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
            # continues with the replaced broker after resume.
            held, active = [], []
            for sid, s in state['sessions'].items():
                if s['status'] not in ACTIVE_STATUSES:
                    continue
                check = instance / 'sessions' / sid / 'end-check.json'
                waiting = check.is_file() and read_json(check)['status'] == 'waiting_dispatch'
                (held if waiting and not alive(s.get('cli')) else active).append(sid)
            if active:
                raise ValueError('let active CLI turns finish before replacing the Lean environment: '
                                 + ', '.join(sorted(active)))
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
