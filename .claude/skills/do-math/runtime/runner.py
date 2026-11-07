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

from check import check_session, regular_tree, tree_hashes
from cli_adapter import provider_for_model
from launch import worker_command as build_command
from coordination import board, lease_table, section_entries
from availability import (availability_view, no_research_outcome, opening_since,
                          reported_availability)
from knowledge import canonical, formal_ready, render, replay, root_solved, sufficient_closure
from retention import capture, refusal
from ending import ROLES as END_CHECK_ROLES, authorize, turn_directory
from runtime_support import (EmergencyMemory, InstanceLock, alive, archive_work, available_memory, file_stamp, git,
                             popen_options, process_identity, read_json, rename_directory, session_host,
                             terminate_process, write_json, write_text)
from settings import PRODUCERS, defaults, load_settings, validate

SCRIPT = Path(__file__).resolve()
RUNTIME = SCRIPT.parent
SKILL = RUNTIME.parent
PRIORITY = {'review': 0, 'peer': 1, 'formalizer': 2, 'organizer': 3, 'explore': 4, 'attempt': 5}


def uid(prefix):
    return prefix + uuid.uuid4().hex


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
             'attempt_research_starts': 0,
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
        return [(sid, s) for sid, s in self.state['sessions'].items() if s['status'] in ('starting', 'running', 'publishing')]

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
                                         'node': (task or {}).get('node'), 'previous_peers': [], 'previous_reviews': []}
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
        if job['role'] == 'attempt':
            self.state['last_attempt_launch'] = time.time()
            gate = self.state.get('attempt_dispatch_gate')
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

    def retry(self, job, session, reason, *, availability=True):
        job['retries'] += 1
        delay = min(self.settings['retry_max_seconds'], self.settings['retry_seconds'] * 2 ** min(job['retries'] - 1, 20))
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
            previous = job['task'].setdefault('previous_partial_sessions', [])
            path = str(self.session_dir(session['id']))
            if path not in previous:
                previous.append(path)
        if job['pipeline']:
            pipeline = self.state['pipelines'][job['pipeline']]
            if job['role'] in ('peer', 'review'):
                pipeline['previous_' + ('peers' if job['role'] == 'peer' else 'reviews')].append(session['id'])
                job['task']['previous_partial_sessions'] = [str(self.session_dir(x)) for x in pipeline['previous_' + ('peers' if job['role'] == 'peer' else 'reviews')]]
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
            if s['end_check'].get('authorization') is None:
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
                    signal['until'] = time.time() + min(self.settings['retry_max_seconds'], self.settings['retry_seconds'] * 2 ** min(signal['attempts'] - 1, 20))
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
                and (s['retention'].get('cli_activity') or s['retention'].get('native_activity'))):
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
            material = (s['retention'].get('cli_activity') or s['retention'].get('native_activity')
                        or any((session / name).is_dir() and any((session / name).rglob('*')) for name in ('output', 'work')))
            if not material:
                self.retry(job, s, s.get('launch_error') or 'session ended without retained research material')
                return
            s['status'] = 'ended'
            job['status'] = 'done'
            pipeline = self.state['pipelines'][job['pipeline']]
            pipeline['stage'] = 'peer'
            self.enqueue('peer', {'source': str(session), 'source_role': s['role'],
                                  'node': pipeline.get('node'), 'sections': self.producer_sections(sid),
                                  'retention': s['retention']},
                         pipeline['id'], pipeline['id'] + ':peer')
            self.save()
            return
        # A cancellation recorded by the host, even after a clean CLI exit between turns,
        # leaves this stage unfinished; a replacement receives the partial material.
        interrupted = s.get('end_check', {}).get('authorization', {}).get('basis') == 'interrupted'
        if s.get('exit_code') != 0 or s.get('refusal') or s.get('launch_error') or interrupted:
            reason = (s.get('launch_error') or (s.get('refusal') or {}).get('reason') or
                      (s['end_check']['authorization']['explanation'] if s.get('exit_code') == 0 else
                       f"processing session ended without successful completion (exit_code={s.get('exit_code')!r})"))
            self.retry(job, s, reason,
                       availability=bool(s.get('refusal') or s.get('launch_error')))
            return
        errors = check_session(session)
        if errors:
            if (s['role'] == 'review' and job['task'].get('kind') == 'candidate'
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
                    if staging.resolve().parent != session.resolve():
                        raise ValueError('invalid candidate staging path')
                    shutil.rmtree(staging)
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
        if s['role'] == 'review' and job['task'].get('kind') == 'candidate':
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
                    if staging.is_symlink() or staging.is_junction() or staging.resolve().parent != peer.resolve():
                        raise ValueError('invalid candidate recovery staging path')
                    shutil.rmtree(staging)
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
                             'node': pipeline.get('node'), 'sections': self.producer_sections(pipeline['producer']),
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
            event.update(producer_role=pipeline['role'], pipeline=pipeline['id'], node=pipeline.get('node'))
        self.state['publication'] = {'event': event, 'job': job['id'], 'session': sid}
        self.state['sessions'][sid].update(status='publishing', record=rid)
        self.save()

    def publish(self):
        publication = self.state['publication']
        if not publication:
            return
        event = publication['event']
        sid = publication['session']
        job = self.state['jobs'][publication['job']]
        destination = self.instance / 'knowledge' / event['folder']
        if not destination.exists():
            stage = self.instance / 'runner' / ('stage-' + event['id'])
            if stage.exists():
                if stage.resolve().parent != (self.instance / 'runner').resolve():
                    raise ValueError('invalid staging directory')
                shutil.rmtree(stage)
            if event['kind'] == 'record':
                candidate = Path(job['task']['candidate'])
                regular_tree(candidate)
                shutil.copytree(candidate, stage)
                if tree_hashes(stage) != job['task']['candidate_hashes']:
                    # The damaged candidate stays where review read it; its staged copy is not evidence.
                    shutil.rmtree(stage)
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
            else:
                shutil.copytree(self.session_dir(sid) / 'output', stage)
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
        self.state['sessions'][sid]['status'] = 'integrated'
        job.update(status='done', record=event['id'])
        if job['pipeline']:
            self.state['pipelines'][job['pipeline']].update(stage='done', record=event['id'])
        if event['kind'] == 'review':
            self.state['processed_concerns'] = sorted(set(self.state['processed_concerns']) | set(job['task'].get('concerns', [])))
            self.state['processed_conflicts'] = sorted(set(self.state['processed_conflicts']) | set(job['task'].get('conflicts', [])))
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
            child = self.hosts.get(sid)
            if child is not None and child.poll() is not None:
                del self.hosts[sid]
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
            exit_file = session / 'exit.json'
            if exit_file.exists():
                s.update(read_json(exit_file))
            self.finish(sid, s)

    def ensure_broker(self):
        if self.broker is not None and self.broker.poll() is not None:
            self.broker = None
        receipt = self.instance / 'runner/lean/process.json'
        try:
            if receipt.exists() and alive(read_json(receipt)['process']):
                return
        except (OSError, ValueError, KeyError):
            pass
        if time.monotonic() - self.broker_attempt < 10:
            return
        self.broker_attempt = time.monotonic()
        directory = self.instance / 'runner/lean'
        directory.mkdir(exist_ok=True)
        with (directory / 'broker.log').open('ab') as log:
            self.broker = subprocess.Popen([sys.executable, '-B', str(RUNTIME / 'lean_broker.py'), 'serve', str(self.instance)],
                                          cwd=self.instance, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                          **popen_options(detached=True))

    def populate(self):
        model = self.model
        pending = [j for j in self.state['jobs'].values() if j['status'] in ('pending', 'running')]
        if not any(j['role'] == 'review' and j['task'].get('kind') == 'comprehensive' for j in pending):
            concerns = [key for key, value in model['concerns'].items() if value['status'] != 'cleared' and key not in self.state['processed_concerns']]
            conflicts = [nid + ':' + ','.join(n['proofs']) for nid, n in model['nodes'].items()
                         if n['canonical'] == nid and n['contested'] and nid + ':' + ','.join(n['proofs']) not in self.state['processed_conflicts']]
            if concerns or conflicts:
                self.enqueue('review', {'kind': 'comprehensive', 'concerns': concerns, 'conflicts': conflicts,
                                        'purpose': 'Trace the questioned claims to their evidence and through actual dependent uses; report precise findings.'})
        closure = sufficient_closure(model)
        for nid, node in model['nodes'].items():
            if node['canonical'] != nid or node['state'] not in ('informal_proved', 'informal_refuted'):
                continue
            if (nid, node['state'].split('_', 1)[1]) not in closure:
                continue  # settled, but no accepted relation carries this outcome to the root
            if any(p['role'] == 'formalizer' and p['stage'] != 'done' and canonical(model, p['node']) == nid for p in self.state['pipelines'].values()):
                continue
            proofs = [pid for pid in node['proofs'] if formal_ready(model, model['proofs'][pid])]
            if proofs:
                previous = [p['record'] for p in self.state['pipelines'].values() if p['role'] == 'formalizer' and p.get('record') and canonical(model, p['node']) == nid]
                self.producer('formalizer', {'node': nid, 'proofs': proofs, 'previous_records': previous})
        due = [rid for rid in model['records'] if rid not in model['organized']]
        if len(due) >= self.settings['organizer_every_records'] and not any(j['role'] == 'organizer' for j in pending):
            # make_pack fixes the batch from the published records when the organizer launches.
            self.enqueue('organizer', {})

    def current_availability(self):
        return availability_view(self.model, board(self.instance, self.state, self.model),
                                 self.state.get('attempt_availability_epoch', 0))

    def finish_no_research(self, sid, session, job, outcome):
        """Terminal for this session even when its separate availability report is stale."""
        try:
            observed = reported_availability(self.session_dir(sid), outcome)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            observed = None
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
                self.state['explore_requested'] = True
        session.update(status='ended', disposition='no_research')
        job['status'] = 'done'
        self.state['pipelines'][job['pipeline']].update(stage='done', disposition='no_research')
        self.archive_due = True
        self.save()

    def observe_attempt_selections(self):
        selected = [s for sid, s in self.state['sessions'].items()
                    if s['role'] == 'attempt' and not s.get('research_counted')
                    and s.get('disposition') != 'no_research'
                    and section_entries(self.instance, sid, self.model)]
        for session in selected:
            session['research_counted'] = True
            self.state['attempt_research_starts'] += 1
            if self.state['attempt_research_starts'] % self.settings['explore_every'] == 0:
                self.state['explore_requested'] = True
            self.save()

    def attempt_dispatch_ready(self):
        gate = self.state.get('attempt_dispatch_gate')
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
        sid = gate.get('probe_session')
        if gate['mode'] == 'reassess' and sid:
            if section_entries(self.instance, sid, self.model):
                self.state['attempt_dispatch_gate'] = None
                self.save()
                return True
            if self.state['sessions'][sid]['status'] not in ('starting', 'running', 'publishing'):
                gate['probe_session'] = None
        if before != json.dumps(gate, sort_keys=True):
            self.save()
        return gate['mode'] == 'reassess' and gate.get('probe_session') is None

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

    def attempt_launch_due(self):
        """Launches are spaced so each attempt can take a lease before the next one reads the board."""
        last = self.state.get('last_attempt_launch')
        return last is None or time.time() - last >= self.settings['attempt_launch_interval']

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
            if job['role'] == 'formalizer':
                node = self.model['nodes'][canonical(self.model, job['task']['node'])]
                ready = [p for p in node['proofs'] if formal_ready(self.model, self.model['proofs'][p])]
                settled = node['state'] in ('informal_proved', 'informal_refuted')
                carries = settled and (node['canonical'], node['state'].split('_', 1)[1]) in sufficient_closure(self.model)
                if not settled or not ready or not carries:
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
                if any(j['status'] == 'pending' and j['role'] in ('peer', 'review') for j in self.state['jobs'].values()):
                    continue
                if not self.attempt_launch_due():
                    continue
                exploration = any(p['role'] == 'explore' and p['stage'] != 'done'
                                  for p in self.state['pipelines'].values())
                if not exploration and self.selection('explore') and self.state['explore_requested']:
                    # schedule() creates eligible exploration after this pass.
                    # Leave capacity for it before launching another attempt.
                    continue
            if job['role'] == 'review' and job['task'].get('kind') == 'comprehensive' and any(
                    other['status'] == 'running' and other['role'] == 'review' and other['task'].get('kind') == 'comprehensive'
                    for other in self.state['jobs'].values()):
                continue
            if job['not_before'] <= time.time() and self.selection(job['role']):
                if job['role'] == 'organizer' and any(j['role'] == 'organizer' and j['status'] == 'running' for j in self.state['jobs'].values()):
                    continue
                self.dispatch(job['id'])
                changed = True
        if changed:
            self.save()

    def schedule(self):
        self.observe_attempt_selections()
        self.populate()
        self.dispatch_pending()
        if self.state['complete']:
            return
        while len(self.active()) < self.settings['max_sessions']:
            nodes = self.available_nodes()
            self.attempt_dispatch_ready()
            suppressed = (self.state.get('attempt_dispatch_gate') or {}).get('mode') == 'suppressed'
            exploration = any(p['role'] == 'explore' and p['stage'] != 'done' for p in self.state['pipelines'].values())
            if (not nodes or suppressed) and not exploration:
                if not self.state['explore_requested']:
                    self.state['explore_requested'] = True
                    self.save()
            if self.state['explore_requested'] and not exploration and self.selection('explore'):
                key = self.producer('explore')
                self.dispatch(key)
                continue
            waiting = any(j['status'] == 'pending' and j['role'] in ('peer', 'review') for j in self.state['jobs'].values())
            organizer_running = any(j['role'] == 'organizer' and j['status'] == 'running'
                                    for j in self.state['jobs'].values())
            higher_ready = any(j['status'] == 'pending' and j['role'] not in PRODUCERS
                               and j['not_before'] <= time.time() and self.selection(j['role'])
                               and (j['role'] != 'organizer' or not organizer_running)
                               for j in self.state['jobs'].values())
            if (waiting or higher_ready or not nodes or not self.attempt_launch_due()
                    or not self.attempt_dispatch_ready() or not self.selection('attempt')):
                break
            key = self.producer('attempt')
            self.dispatch(key)

    def refresh(self):
        rows = board(self.instance, self.state, self.model)
        leases = lease_table(self.instance, self.state, self.model)
        investigations = [(j['id'], j['status']) for j in self.state['jobs'].values()
                          if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive']
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
            if request['kind'] == 'review':
                task = {'kind': 'comprehensive', 'concerns': request.get('concerns', []), 'conflicts': [],
                        'requested_records': request.get('records', []), 'requested_nodes': request.get('nodes', []),
                        'purpose': request.get('reason', 'Operator requested a renewed independent assessment.')}
                self.enqueue('review', task, key='operator:' + path.stem)
            elif request['kind'] == 'organize':
                self.enqueue('organizer', {}, key='operator:' + path.stem)
            elif request['kind'] == 'reconsider-attempts':
                self.state['attempt_availability_epoch'] = self.state.get('attempt_availability_epoch', 0) + 1
                probe = (self.state.get('attempt_dispatch_gate') or {}).get('probe_session')
                if self.state['sessions'].get(probe, {}).get('status') not in ('starting', 'running', 'publishing'):
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
        self.observe_attempt_selections()
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
                    return {'pid': child.pid, 'stdout': str(stdout), 'stderr': str(stderr), 'instance': str(instance)}
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
    return {'instance': str(instance), 'runner_alive': bool(receipt and alive(receipt['process'])),
            'root_state': model['nodes'][canonical(model, 'root')]['state'], 'finished': state['finished'],
            'stopped': (instance / 'control/STOP').exists(), 'board': board(instance, state, model),
            'attempt_dispatch': state.get('attempt_dispatch_gate'),
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
                if finished and session['status'] not in ('starting', 'running', 'publishing'):
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
    for name in ('init', 'start', 'run', 'status', 'stop', 'resume', 'input', 'render', 'review', 'organize', 'reconsider-attempts', 'restart-broker', 'kill-session', '_session', '_archive'):
        p = sub.add_parser(name)
        p.add_argument('instance', type=Path)
        if name == 'init':
            p.add_argument('--root', required=True, type=Path)
            p.add_argument('--settings', type=Path)
        if name == 'run':
            p.add_argument('--token')
        if name == 'input':
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
        elif args.command == 'restart-broker':
            from lean_broker import Paths, broker_status, ensure_broker
            state = read_json(instance / 'runner/state.json')
            if not (instance / 'control/STOP').exists():
                raise ValueError('stop new dispatch before replacing the Lean environment')
            # A session held behind STOP for its next turn has no running CLI and
            # continues with the replaced broker after resume.
            held, active = [], []
            for sid, s in state['sessions'].items():
                if s['status'] not in ('starting', 'running', 'publishing'):
                    continue
                check = instance / 'sessions' / sid / 'end-check.json'
                waiting = check.is_file() and read_json(check).get('status') == 'waiting_dispatch'
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
