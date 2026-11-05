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
import uuid

from check import check_session, regular_tree
from cli_adapter import provider_for_model
from launch import worker_command as build_command
from coordination import board
from knowledge import canonical, formal_ready, render, replay, root_solved
from retention import capture, refusal
from runtime_support import (EmergencyMemory, InstanceLock, LEAN_DEFAULTS, alive, archive_work, available_memory, file_stamp, git, lean_config,
                             popen_options, process_identity, read_json, session_host,
                             terminate_process, write_json, write_text)
from settings import PRODUCERS, ROLES, defaults, load_settings, validate

SCRIPT = Path(__file__).resolve()
RUNTIME = SCRIPT.parent
SKILL = RUNTIME.parent
PRIORITY = {'review': 0, 'peer': 1, 'formalizer': 2, 'organizer': 3, 'explore': 4, 'attempt': 5}


def uid(prefix):
    return prefix + uuid.uuid4().hex


def tree_hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(folder).rglob('*') if p.is_file()}


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
             'attempt_dispatches': 0, 'explore_requested': False, 'complete': False,
             'processed_concerns': [], 'processed_conflicts': [], 'publication': None,
             'seen_inputs': [], 'seen_requests': [], 'last_error': None, 'finished': False}
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
                    write_json(session / 'declaration.json', {'nodes': [job['task']['node']], 'at': time.time()})
            else:
                pipeline[job['role']] = sid
        if job['role'] == 'attempt':
            self.state['attempt_dispatches'] += 1
            if self.state['attempt_dispatches'] % self.settings['explore_every'] == 0:
                self.state['explore_requested'] = True
        elif job['role'] == 'explore':
            self.state['explore_requested'] = False
        self.save()
        try:
            command = build_command(self.settings['cli'][provider], selected['model'], selected['effort'], session,
                                    **({'servers': self.settings['mcp_servers']} if self.settings['mcp_servers'] else {}))
            # Native session persistence retains tool messages beyond the CLI stream.
            argv = [x for x in command.argv if x not in ('--ephemeral', '--no-session-persistence')]
            write_json(session / 'launch.json', {'runner': self.identity, 'command': {'argv': argv, 'cwd': str(command.cwd)}})
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
        session = self.session_dir(sid)
        if not s.get('retained'):
            # File errors leave this stage incomplete for restart recovery.
            retention = capture(session, s['provider'])
            signal = refusal(session, s['provider'], s['model'], s['started_at'], self.settings['retry_seconds'])
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
                         and s['started_at'] >= self.state['blocks'][key]['until']]
            for key in recovered:
                del self.state['blocks'][key]
            if recovered:
                self.save()
        if s['role'] in PRODUCERS:
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
                                  'node': pipeline.get('node'), 'retention': s['retention']},
                         pipeline['id'], pipeline['id'] + ':peer')
            self.save()
            return
        errors = check_session(session)
        if errors:
            self.retry(job, s, '; '.join(errors),
                       availability=bool(s.get('refusal') or s.get('launch_error')))
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
                staging.rename(candidate)
            s['status'] = 'ended'
            job['status'] = 'done'
            pipeline = self.state['pipelines'][job['pipeline']]
            pipeline['stage'] = 'review'
            self.enqueue('review', {'kind': 'candidate', 'candidate': str(candidate),
                                    'candidate_hashes': tree_hashes(candidate),
                                    'source': str(self.session_dir(pipeline['producer'])),
                                    'peer': str(session)}, pipeline['id'], pipeline['id'] + ':review')
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
                shutil.copytree(self.session_dir(sid) / 'output', stage / 'review')
                pipeline = self.state['pipelines'][job['pipeline']]
                write_json(stage / 'provenance.json', {'producer_session': pipeline['producer'], 'peer_session': pipeline['peer'],
                                                      'review_session': sid, 'pipeline': pipeline['id']})
                self.copy_formal_evidence(stage, sid)
            else:
                shutil.copytree(self.session_dir(sid) / 'output', stage)
            stage.rename(destination)
        event_path = self.instance / 'knowledge/events' / (event['id'] + '.json')
        if not event_path.exists():
            write_json(event_path, event)
        self.model = replay(self.instance)
        render(self.instance, self.model, board(self.instance, self.state, self.model))
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
        if self.state.get('finished') and not self.active():
            return
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
        for nid, node in model['nodes'].items():
            if node['canonical'] != nid or node['state'] not in ('informal_proved', 'informal_refuted'):
                continue
            if any(p['role'] == 'formalizer' and p['stage'] != 'done' and canonical(model, p['node']) == nid for p in self.state['pipelines'].values()):
                continue
            proofs = [pid for pid in node['proofs'] if formal_ready(model, model['proofs'][pid])]
            if proofs:
                previous = [p['record'] for p in self.state['pipelines'].values() if p['role'] == 'formalizer' and p.get('record') and canonical(model, p['node']) == nid]
                self.producer('formalizer', {'node': nid, 'proofs': proofs, 'previous_records': previous})
        due = [rid for rid in model['records'] if rid not in model['organized']]
        if len(due) >= self.settings['organizer_every_records'] and not any(j['role'] == 'organizer' for j in pending):
            self.enqueue('organizer', {'batch': due})

    def available_nodes(self):
        rows = board(self.instance, self.state, self.model)
        held = {n for r in rows if r['role'] == 'attempt' for n in r['nodes']}
        nodes = [n for n, v in self.model['nodes'].items() if v['canonical'] == n and v['state'] == 'unresolved' and n not in held]
        choosing = sum(r['role'] == 'attempt' and r['stage'] in ('producing', 'queued') and not r['nodes'] for r in rows)
        return nodes, choosing

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
                if node['state'] not in ('informal_proved', 'informal_refuted') or not ready:
                    job['status'] = 'cancelled'
                    self.state['pipelines'][job['pipeline']]['stage'] = 'done'
                    changed = True
                    continue
                job['task']['proofs'] = ready
            if job['role'] == 'attempt':
                if not any(node['canonical'] == nid and node['state'] == 'unresolved'
                           for nid, node in self.model['nodes'].items()):
                    continue
                if any(j['status'] == 'pending' and j['role'] in ('peer', 'review') for j in self.state['jobs'].values()):
                    continue
                exploration = any(p['role'] == 'explore' and p['stage'] != 'done'
                                  for p in self.state['pipelines'].values())
                if not exploration and self.selection('explore') and (
                        self.state['explore_requested'] or not self.available_nodes()[0]):
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
        self.populate()
        self.dispatch_pending()
        if self.state['complete']:
            return
        while len(self.active()) < self.settings['max_sessions']:
            nodes, choosing = self.available_nodes()
            exploration = any(p['role'] == 'explore' and p['stage'] != 'done' for p in self.state['pipelines'].values())
            if not nodes and not exploration:
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
            if waiting or higher_ready or len(nodes) <= choosing or not self.selection('attempt'):
                break
            key = self.producer('attempt')
            self.dispatch(key)

    def refresh(self):
        rows = board(self.instance, self.state, self.model)
        investigations = [(j['id'], j['status']) for j in self.state['jobs'].values()
                          if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive']
        signature = json.dumps([rows, self.model['sequence'], investigations], sort_keys=True)
        if signature != self.last_board:
            render(self.instance, self.model, rows)
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
                self.enqueue('organizer', {'batch': [r for r in self.model['records'] if r not in self.model['organized']]}, key='operator:' + path.stem)
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
            'blocks': state['blocks'], 'lean': broker_status(Paths(instance)), 'state': state}


def archive_finished(instance):
    import lzma
    import tarfile
    try:
        with InstanceLock(Path(instance) / 'runner/archive-lock'):
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
    for name in ('init', 'start', 'run', 'status', 'stop', 'resume', 'input', 'render', 'review', 'organize', 'restart-broker', 'kill-session', '_session', '_archive'):
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
                render(instance, replay(instance), board(instance))
        elif args.command == 'kill-session':
            state = read_json(instance / 'runner/state.json')
            if args.session not in state['sessions']:
                raise ValueError('unknown session')
            receipt = read_json(instance / 'sessions' / args.session / 'process.json')
            terminate_process(receipt['process'])
            result['terminated'] = args.session
        elif args.command in ('review', 'organize'):
            request = {'kind': args.command}
            if args.command == 'review':
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
            if not (instance / 'control/STOP').exists() or any(s['status'] in ('starting', 'running', 'publishing') for s in state['sessions'].values()):
                raise ValueError('stop new dispatch and let active sessions finish before replacing the Lean environment')
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
