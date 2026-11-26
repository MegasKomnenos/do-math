"""Shared fixture of the runtime tests: a small instance whose canon is compiled by the stand-in compiler.

The instance is created once per test process by the operator's `init` command (runner.main), whose
`initialize` builds the canon through a real broker with tests/canon_lean.py as its compiler. A test
works on a copy of its own, made when the test first uses it.
Tests that change the canon go through the real candidate, build and publication path with the
helpers below; nothing here writes the index or the model by hand.
"""
import atexit
import functools
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from canon import beyond_allowed
from canon_tool import build_candidate, main as canon_tool_main, verify
from check import check_session, tree_hashes
from lean_broker import Paths, broker_alive, terminate_tree
from runner import Runner, main, uid
from runtime_support import alive, read_json, remove_tree, write_json
from settings import defaults

HERE = Path(__file__).resolve().parent
POPEN = subprocess.Popen  # captured before any test patches it

DEFS = '''module

@[expose] public section

namespace Small

/-- The sum of the first `n` odd numbers. -/
def oddSum : Nat → Nat
  | 0 => 0
  | n + 1 => oddSum n + (2 * n + 1)

end Small
'''
ROOT = '''module

public import Small.Defs

@[expose] public section

namespace Small

/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  sorry

end Small
'''
RECORDS = {
    'Small/oddSum.md': '''---
short: sum of odd numbers
weight: unit
---
## Description

The sum of the first n odd numbers, defined by recursion on n.
''',
    'Small/root.md': '''---
short: odd numbers sum to a square
weight: unit
---
## Description

The sum of the first n odd numbers equals n times n.

## Statement

For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.
''',
}
# The same root as one closed proposition. The stand-in compiler confirms a `refutes:` claim by comparing
# the texts of two statements, which it can do only for statements without binders before the colon. The
# negation of this root, `¬ (∀ n : Nat, oddSum n = n * n)`, is such a statement and is valid Lean as well.
ROOT_CLOSED = ROOT.replace('theorem root (n : Nat) : oddSum n = n * n', 'theorem root : ∀ n : Nat, oddSum n = n * n')
ROOTS = {'default': ROOT, 'closed': ROOT_CLOSED}


def theorem(name, statement, uses=(), proof='sorry', doc=None):
    """The Lean text of a statement in the stand-in compiler's subset.

    An informal proof names in Lean what it rests on, one `have` per element, and ends in `sorry`.
    With another last line, such as `rfl`, the proof counts as complete in Lean."""
    lines = [f'/-- {doc or "A statement of the test canon."} -/', f'theorem {name} {statement} := by']
    lines += [f'  have h{number} := {used}' for number, used in enumerate(uses, 1)]
    return '\n'.join(lines + ['  ' + proof])


def record_text(description, weight='step', proof=None, statement=None, **meta):
    lines = ['---', f'weight: {weight}'] + [f'{key}: {value}' for key, value in meta.items()] + ['---',
             '## Description', '', description, '']
    if statement:
        lines += ['## Statement', '', statement, '']
    if proof:
        lines += ['## Proof', '', proof, '']
    return '\n'.join(lines)


def module_text(body, imports=('Small.Defs',)):
    header = ''.join(f'public import {name}\n' for name in imports)
    return f'module\n\n{header}\n@[expose] public section\n\nnamespace Small\n\n{body.strip()}\n\nend Small\n'


# The canon of the variant 'layered'. The root's module imports `Small.Facts`, which imports the definitions
# and holds a theorem without a proof. `Small.Side` imports the definitions as well, and the root's module does
# not import it. The modules that the root's module imports, directly or through one another, are `Small.Defs`
# and `Small.Facts` (canon.definition_modules).
ROOTS['layered'] = ROOT.replace('public import Small.Defs', 'public import Small.Facts')
LAYERED = {
    'lean/Small/Facts.lean': module_text(theorem('factZero', ': oddSum 0 = 0')),
    'lean/Small/Side.lean': module_text(theorem('sideOne', ': oddSum 1 = 1')),
    'records/Small/factZero.md': record_text('The empty sum is zero.', weight='unit'),
    'records/Small/sideOne.md': record_text('The first odd number is one.'),
}


def earlier_form(index):
    """An index as the code wrote it before the extraction asked Lean for the axioms.

    An entry carries `direct_axioms` where it now carries `axioms`, a hidden declaration carries `axioms`
    where it now carries `sorry`, and `judged` names the theorems proved from the default allowed axioms."""
    allowed = defaults()['lean']['allowed_axioms']
    return {**index,
            'entries': {name: {**{key: value for key, value in entry.items() if key != 'axioms'},
                               'direct_axioms': entry['axioms']} for name, entry in index['entries'].items()},
            'hidden': {name: {**{key: value for key, value in item.items() if key != 'sorry'},
                              'axioms': ['sorryAx'] if item['sorry'] else []} for name, item in index['hidden'].items()},
            'judged': {name: index['revision'] for name, entry in index['entries'].items()
                       if entry['kind'] == 'theorem' and not beyond_allowed(entry, allowed)}}


def fixture_settings():
    config = defaults()
    # No external tools: the tests do not depend on the literature server being installed.
    config.update(max_sessions=2, retry_seconds=1, retry_max_seconds=2, launch_interval=0, roles={},
                  mcp_servers={})
    config['lean'].update(command=[sys.executable, '-B', str(HERE / 'canon_lean.py')],
                          version_command=[sys.executable, '-B', str(HERE / 'canon_lean.py'), '--version'],
                          min_free_memory_mb=0, memory_budget_mb=512, calibration_expect_mb=64,
                          priority='normal')  # the stand-in compiler competes on equal terms with other load
    return config


def write_canon(folder, root=ROOT, more=()):
    """The canon a test instance is created from; `more` holds the further files of a variant by their paths."""
    for name, text in (('lean/Small/Defs.lean', DEFS), ('lean/Small/Root.lean', root),
                       *(('records/' + key, value) for key, value in RECORDS.items()), *dict(more).items()):
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')


def stop_broker(instance):
    info = broker_alive(Paths(instance))
    if info and alive(info['process']):
        terminate_tree(info['process']['pid'])
        deadline = time.monotonic() + 10
        while alive(info['process']) and time.monotonic() < deadline:
            time.sleep(0.05)


def kept_copy(instance, prefix):
    """A copy of an instance that is kept for the whole test process: taken with the instance's broker
    stopped, in a temporary folder that is removed when the process ends."""
    stop_broker(instance)
    base = Path(tempfile.mkdtemp(prefix=prefix))
    atexit.register(remove_tree, base)
    shutil.copytree(instance, base / 'instance')
    return base / 'instance'


def session_record(sid, role, job, status='running', **fields):
    """A session's entry in the runner's state, with every key that dispatch writes (Runner.dispatch).

    `fields` replace a value given here or add a key that a later step of the runner writes, such as `exit_code`."""
    return {'id': sid, 'role': role, 'job': job, 'status': status, 'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh',
            'provider': 'codex', 'started_at': time.time(), 'host': None, 'cli': None, 'record': None, **fields}


_TEMPLATES = {}
_SCENARIOS = {}


def template(variant='default'):
    """One compiled instance per root variant for the whole test process; every test works on a copy of it."""
    if variant not in _TEMPLATES:
        base = Path(tempfile.mkdtemp(prefix='do-math-template-'))
        atexit.register(remove_tree, base)
        (base / 'goal.md').write_text('For every natural number n, the sum of the first n odd numbers is n * n.',
                                      encoding='utf-8')
        write_json(base / 'settings.json', fixture_settings())
        write_canon(base / 'canon', ROOTS[variant], LAYERED if variant == 'layered' else ())
        # By the command the operator runs, so that its arguments and its exit code are part of every test's start.
        with patch('builtins.print') as shown:
            refused = main(['init', str(base / 'instance'), '--root', str(base / 'goal.md'),
                            '--canon', str(base / 'canon'), '--root-declaration', 'Small.root',
                            '--settings', str(base / 'settings.json')])
        if refused:
            raise RuntimeError(f'init refused the canon of the fixture: {shown.call_args}')
        _TEMPLATES[variant] = base / 'instance'
    return _TEMPLATES[variant]


class InstanceCase(unittest.TestCase):
    root_variant = 'default'  # 'closed' states the root without binders, so that its negation can be stated
    expect_mb, patience = 64, 120  # of a build: the memory expected for one compile in MiB, the seconds it may take
    changes_guides = False  # set by a class or a test that writes into the guides; it then works on a copy of them

    def setUp(self):
        # A client that waits for a build looks for its result at pauses that grow to a second
        # (lean_broker.await_record), which suits a compile of minutes. A build of the stand-in compiler ends within
        # seconds, and at those pauses a test waits half a second longer on average than its build takes. The
        # pauses themselves are tested on a stand-in clock in test_waiting.py.
        pauses = patch.multiple('lean_broker', WAIT_FIRST=0.05, WAIT_CAP=0.05)
        pauses.start()
        self.addCleanup(pauses.stop)
        # The folder is removed by remove_tree, as the folders this fixture keeps are. The host of a compile holds
        # its log for a moment after it has recorded the exit, and that removal waits for the file.
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(remove_tree, self.root)
        self.starts_from = self.starting_instance()

    @functools.cached_property
    def instance(self):
        """The test's own copy of the instance it starts from, made when the test first asks for it.

        A test that asks for a scenario before it has used its instance is given a copy of that scenario
        and no other (scenario), and a test that uses no instance is given none."""
        folder = self.root / 'instance'
        shutil.copytree(self.starts_from, folder)
        self.addCleanup(stop_broker, folder)
        return folder

    @functools.cached_property
    def skill(self):
        """The folder of guides a runner is given; a session's pack and its resume texts are read from it.

        It is the installed skill, which a runner and a session host read and do not write. Where
        `changes_guides` is set, by a class for all of its tests or by one test before it first asks, it is
        the test's own copy of the installed guides, made when the test first asks for it."""
        installed = Path(__file__).resolve().parents[2]
        if not self.changes_guides:
            return installed
        folder = self.root / 'skill'
        for name in ('reference', 'roles', 'resume'):
            shutil.copytree(installed / name, folder / name)
        shutil.copyfile(installed / 'SKILL.md', folder / 'SKILL.md')
        return folder

    def starting_instance(self):
        """The instance a test receives a copy of: the one `init` created.

        A subclass that keeps a published state for the whole test process returns that state once it
        has made it, so that each of its tests receives one copy and not a second one in its place."""
        return template(self.root_variant)

    def configure(self, **changes):
        """Change settings.json of the instance; keys given under `lean` are merged into the Lean settings."""
        config = read_json(self.instance / 'settings.json')
        config['lean'].update(changes.pop('lean', {}))
        config.update(changes)
        write_json(self.instance / 'settings.json', config)

    def scenario(self, name, build):
        """Research state that several tests start from, published once per test process.

        The first test that asks for a scenario builds it through the real publication path, on a
        fresh copy of the instance as it was created, and a copy of the built instance is kept. Every
        test that asks receives the scenario in place of its instance, whatever it did before; a test
        that has not used its instance yet is given the scenario as its one copy. The settings of the
        asking test stay in force. A build can start from another scenario by asking for that one first."""
        key = (self.root_variant, name)
        # A test works on a copy once it has asked for `instance`; until then there is none to replace.
        settings = read_json((self.instance if 'instance' in vars(self) else self.starts_from) / 'settings.json')

        def replace_instance(source):
            if 'instance' in vars(self):
                stop_broker(self.instance)
                remove_tree(self.instance)
                shutil.copytree(source, self.instance)
            else:
                self.starts_from = source

        if key not in _SCENARIOS:
            replace_instance(template(self.root_variant))
            build()
            _SCENARIOS[key] = kept_copy(self.instance, 'do-math-scenario-')
        else:
            replace_instance(_SCENARIOS[key])
        write_json(self.instance / 'settings.json', settings)

    # -- candidates and their publication, through the real path ------------------------------------------

    def candidate(self, modules=None, replace=None, records=None, approaches=None, understanding=None,
                  questions=None, resolutions=None, imports=None, title='A contribution', prepare=True):
        """A prepared candidate folder. modules, records, approaches and understanding map relative
        paths to text; replace maps a declaration to its new complete text."""
        folder = self.root / ('candidate-' + uuid.uuid4().hex)
        for sub, files in (('lean', modules), ('records', records), ('approaches', approaches),
                           ('questions', understanding)):
            for name, text in (files or {}).items():
                path = folder / sub / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8', newline='\n')
        entries = []
        for number, (name, text) in enumerate((replace or {}).items()):
            path = folder / 'replace' / f'{number}.lean'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
            entries.append({'declaration': name, 'file': f'replace/{number}.lean', 'imports': (imports or {}).get(name, [])})
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'change.json', {'title': title, 'description': 'A precise contribution with its limitations.',
                                            'replace': entries, 'questions': questions or [],
                                            'resolutions': resolutions or []})
        if prepare:
            self.prepare(folder)
        return folder

    def prepare(self, folder, role='peer', expect_ok=True):
        result = build_candidate(self.instance, 'test', folder, self.root / ('prepare-' + uuid.uuid4().hex),
                                 self.expect_mb, self.patience, role)
        self.assertIsNotNone(result, 'the candidate build did not finish')
        write_json(folder / 'prepared.json', result)
        if expect_ok:
            self.assertTrue(result['ok'], result['errors'])
        return result

    def verdicts(self, folder, **overrides):
        """An assessment that confirms and accepts every proof of a prepared candidate, unless overridden."""
        receipt = read_json(folder / 'prepared.json')
        change = read_json(folder / 'change.json')
        rows = []
        for name in receipt['added'] + receipt['replaced']:
            entry = receipt['entries'][name]
            proved = entry['kind'] == 'theorem' and (entry['lean_proof'] == 'complete' or entry['written_proof'])
            row = {'element': name, 'correct': 'confirmed' if proved else 'not_applicable',
                   'accepted': bool(proved), 'reason': 'Argument checked.'}
            if name in receipt['replaced']:
                row['replaces'] = True
            row.update(overrides.get(name, {}))
            rows.append(row)
        return {'publish': True, 'reason': 'Useful work.', 'contribution': 'Closed what it took on.',
                'feedback': 'feedback.md', 'elements': rows, 'concerns': [], 'findings': [],
                'questions': [{'proposal': q['id'], 'verdict': 'admitted', 'reason': 'Important and exactly stated.'}
                              for q in change['questions']],
                'resolutions': [{'proposal': r['id'], 'resolved': True, 'reason': 'The account settles the question.'}
                                for r in change['resolutions']]}

    def publish(self, folder, assessment=None, role='attempt', question=None, engine=None, expect=True):
        """Publish a prepared candidate as the runner does after a review: queue it and carry it through.

        The review's output passes the transport check first, which the runner makes before it queues a
        publication. An assessment that confirms a proof complete in Lean rests on the review's own compile of
        the candidate; where the assessment given names none, the compile is made here by the command a review
        runs. A verdict that does not confirm such a proof, such as `undetermined`, needs no compile."""
        engine = engine or Runner(self.instance, self.skill)
        state = engine.state
        producer, peer, review, pid = uid('s'), uid('s'), uid('s'), uid('p')
        for sid in (producer, peer, review):
            (engine.session_dir(sid) / 'output').mkdir(parents=True)
        if question:
            write_json(engine.session_dir(producer) / 'declaration.json',
                       {'question': {'id': question, 'at': time.time(), 'by': 'session'}, 'at': time.time()})
        session = engine.session_dir(review)
        task = {'kind': 'candidate', 'candidate': str(folder), 'candidate_hashes': tree_hashes(folder),
                'source': str(engine.session_dir(producer)), 'peer': str(engine.session_dir(peer))}
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': review, 'role': 'review',
                                            'pipeline': pid, 'task': task})
        assessment = assessment or self.verdicts(folder)
        entries = read_json(folder / 'prepared.json')['entries']
        if 'formal_check' not in assessment and any(
                row.get('correct') == 'confirmed' and entries.get(row.get('element'), {}).get('lean_proof') == 'complete'
                for row in assessment.get('elements', [])):
            with patch.object(subprocess, 'Popen', POPEN), patch('builtins.print') as shown:
                self.assertEqual(verify(session, self.expect_mb, self.patience), 0, shown.call_args)
            build = read_json(session / 'work/verify/outcome.json')['build']
            assessment = {**assessment, 'formal_check': {'build': build}}
        write_json(session / 'output/assessment.json', assessment)
        (session / 'output/feedback.md').write_text('Checked.', encoding='utf-8')
        self.assertEqual(check_session(session), [])
        key = pid + ':review:' + peer
        state['pipelines'][pid] = {'id': pid, 'role': role, 'stage': 'review', 'producer': producer, 'peer': peer,
                                   'review': review, 'record': None, 'element': None, 'previous_peers': []}
        state['jobs'][pid + ':producer'] = {'id': pid + ':producer', 'role': role, 'task': {}, 'pipeline': pid,
                                            'status': 'done', 'session': producer, 'retries': 0, 'not_before': 0}
        state['jobs'][key] = {'id': key, 'role': 'review', 'pipeline': pid, 'status': 'running', 'session': review,
                              'retries': 0, 'not_before': 0, 'task': task}
        for sid, session_role, job in ((producer, role, pid + ':producer'), (peer, 'peer', key), (review, 'review', key)):
            state['sessions'][sid] = session_record(sid, session_role, job, 'ended', model='codex/test', effort='low')
        state['sessions'][review]['status'] = 'publishing'
        state['publish_queue'].append({'session': review, 'job': key, 'kind': 'change'})
        engine.save()
        self.drain(engine)
        if expect:
            self.assertEqual(state['pipelines'][pid]['stage'], 'done', state['jobs'][key].get('last_error'))
        return state['pipelines'][pid]['record'], engine

    def drain(self, engine):
        """Carry queued publications to their end; a build goes through the instance's broker."""
        deadline = time.monotonic() + self.patience
        while engine.state['publication'] or engine.state['publish_queue']:
            with patch.object(subprocess, 'Popen', POPEN):
                engine.publish()
            self.assertLess(time.monotonic(), deadline, 'publication did not finish')
            if engine.state['publication']:
                time.sleep(0.05)  # its build is still running; a publication waits for nothing else

    def event(self, eid, kind, data):
        """A comprehensive review as the replay reads one: its output and its event, written here by hand.

        The output passes the transport check first, as the output of a review session does before the runner
        publishes it. The runner takes no part after that: no view is rendered and nothing is committed."""
        session = self.root / ('review-' + uuid.uuid4().hex)
        output = session / 'output'
        output.mkdir(parents=True)
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': session.name, 'role': 'review',
                                            'pipeline': None, 'task': {'kind': 'comprehensive'}})
        write_json(output / 'assessment.json', data)
        (output / 'feedback.md').write_text('What the tracing found.', encoding='utf-8')
        self.assertEqual(check_session(session), [])
        sequence = max([read_json(p)['sequence'] for p in (self.instance / 'knowledge/events').glob('*.json')], default=0) + 1
        shutil.copytree(output, self.instance / 'knowledge/reviews' / eid)
        write_json(self.instance / 'knowledge/events' / (eid + '.json'),
                   {'id': eid, 'sequence': sequence, 'kind': kind, 'folder': 'reviews/' + eid})

    def questions(self, eid, items):
        """An operator publication of questions, made as the operator makes it."""
        source = self.root / ('questions-' + uuid.uuid4().hex + '.json')
        write_json(source, {'reason': 'The operator placed these questions on the frontier.', 'questions': items})
        with patch('builtins.print') as shown:
            self.assertEqual(main(['questions', str(self.instance), '--file', str(source)]), 0, shown.call_args)
        with patch.object(subprocess, 'Popen', POPEN), \
                patch('runner.uid', side_effect=lambda prefix: eid if prefix == 'q' else uid(prefix)):
            engine = Runner(self.instance, self.skill)
            engine.ingest_inputs()
        event = self.instance / 'knowledge/events' / (eid + '.json')
        self.assertTrue(event.is_file(), engine.state['last_error'])

    def note(self, text, engine=None):
        """Publish a change that touches no Lean: an exploration's understanding so far of q0.

        Nothing is built for it, so it serves where a test needs a published change and not its mathematics."""
        folder = self.candidate(understanding={'q0.md': text + '\n'})
        return self.publish(folder, role='explore', question='q0', engine=engine)

    def organize(self, batch=None, merge_questions=(), engine=None):
        """Publish an organizer's output that carries no change of its own, as the runner publishes one.

        The output passes the transport check first, which the runner makes before it queues a publication."""
        engine = engine or Runner(self.instance, self.skill)
        state = engine.state
        sid, key = uid('s'), uid('j')
        session = engine.session_dir(sid)
        output = session / 'output'
        output.mkdir(parents=True)
        if batch is None:
            batch = [cid for cid in engine.model['changes'] if cid not in engine.model['organized']]
        task = {'batch': batch, 'batch_frozen': True}
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'organizer',
                                            'pipeline': None, 'task': task})
        write_json(output / 'organization.json', {'batch': batch, 'merge_questions': list(merge_questions)})
        self.assertEqual(check_session(session), [])
        state['jobs'][key] = {'id': key, 'role': 'organizer', 'pipeline': None, 'status': 'running', 'session': sid,
                              'retries': 0, 'not_before': 0, 'task': task}
        state['sessions'][sid] = session_record(sid, 'organizer', key, 'publishing', model='codex/test', effort='low')
        state['publish_queue'].append({'session': sid, 'job': key, 'kind': 'organization'})
        engine.save()
        self.drain(engine)
        self.assertEqual(state['jobs'][key]['status'], 'done', state['jobs'][key].get('last_error'))
        return state['jobs'][key]['record'], engine

    def reader(self, sid='sreader', role='attempt'):
        """A session folder from which the reading commands of canon_tool can be run."""
        folder = self.instance / 'sessions' / sid
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'pipeline': None, 'task': {}, 'user_inputs': []})
        return folder

    def command_line(self, *argv):
        """The exit code and the output of canon_tool for one command line."""
        stream = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='\n')
        with patch('sys.stdout', stream):
            returned = canon_tool_main([str(argument) for argument in argv])
        stream.flush()
        return returned, stream.buffer.getvalue().decode('utf-8')

    def session(self, engine, sid, role='attempt'):
        """A producing session as dispatch leaves it: its pipeline on the board and its input.json in place."""
        key = engine.producer(role)
        job = engine.state['jobs'][key]
        folder = engine.session_dir(sid)
        for name in ('output', 'work', 'inbox'):
            (folder / name).mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'pipeline': job['pipeline'], 'task': {}, 'user_inputs': []})
        engine.state['pipelines'][job['pipeline']]['producer'] = sid
        engine.state['sessions'][sid] = session_record(sid, role, key)
        job.update(status='running', session=sid)
        engine.save()
        return folder


ROOT_STATEMENTS = {'default': '(n : Nat) : oddSum n = n * n', 'closed': ': ∀ n : Nat, oddSum n = n * n'}
SUM_ZERO = ': oddSum 0 = 0'
SUM_SUCC = '(n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1)'
HELD_REASON = 'The two cases can be merged into one.'
GAP_REASON = 'The induction step is not justified.'


def finding(reason, status='confirmed', concerns=(), **changes):
    """A finding of a comprehensive review, with the keys given in `changes` (such as `invalidates`) beside its own."""
    return {'concerns': list(concerns), 'status': status, 'reason': reason, **changes}


def comprehensive(findings=(), concerns=()):
    """The assessment of a comprehensive review."""
    return {'feedback': 'feedback.md', 'findings': list(findings), 'concerns': list(concerns)}


def take(session, element, statement=None, reasons=None, leased=False, new=None):
    """Register a section through the element's lease: the whole element unless a statement is given.

    new registers a statement that is not yet in the canon, aimed at the element."""
    from coordination import lease, section
    session = Path(session)
    request = session / ('section-' + uuid.uuid4().hex + '.json')
    if new is not None:
        write_json(request, {'new': new, 'reasons': reasons or {}})
    else:
        write_json(request, {'whole': statement is None, 'statement': statement, 'reasons': reasons or {}})
    if not leased:
        taken = lease(session, element)
        if not taken['leased']:
            return {'registered': False, **taken}
    return section(session, element, request)


class ScenarioCase(InstanceCase):
    """Research states that tests start from, each published once per test process (InstanceCase.scenario).

    split    the root has an accepted informal proof that names Small.sumZero and Small.sumSucc, which have
             no proof; Small.sumTwo is settled and nothing uses it
    half     split, and Small.sumZero has an accepted informal proof
    proved   half, and Small.sumSucc has one too, so the root is settled informally
    direct   the root has an accepted informal proof that names nothing
    formal   the root has an accepted proof that is complete in Lean
    ways     two ways of proving the root over eight statements in every standing (see ways())"""

    def root_text(self, uses=(), proof='sorry'):
        """The root's declaration with a proof: informal and naming `uses`, or complete with another ending."""
        return theorem('root', ROOT_STATEMENTS[self.root_variant], uses, proof,
                       doc='The sum of the first `n` odd numbers is the square of `n`.')

    def root_formal(self, uses=()):
        """The root's declaration with a proof that is complete in Lean."""
        induction = ('induction n with\n  | zero => rfl\n  | succ k ih =>\n    rw [oddSum, ih]\n'
                     '    simp only [Nat.add_mul, Nat.mul_add, Nat.mul_one, Nat.one_mul]\n    omega')
        return self.root_text(uses, induction if self.root_variant != 'closed' else 'intro n\n  ' + induction)

    def root_record(self, proof='By induction on $n$, from the empty sum and the passage from $n$ to $n + 1$.'):
        return record_text('The sum of the first n odd numbers equals n times n.', weight='unit', proof=proof,
                           statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                           short='odd numbers sum to a square')

    def peer_session(self, engine, producer, sid):
        """The peer of a producing session's pipeline, as dispatch leaves it."""
        pipeline = engine.state['jobs'][engine.state['sessions'][producer]['job']]['pipeline']
        folder = engine.session_dir(sid)
        folder.mkdir()
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'peer',
                                           'pipeline': pipeline, 'task': {}, 'user_inputs': []})
        engine.state['pipelines'][pipeline].update(peer=sid, stage='peer')
        engine.state['sessions'][sid] = session_record(sid, 'peer', 'peerjob')
        engine.save()
        return folder

    def replace_proof(self, name, text, proof, weight='unit', description='A statement of the test canon.',
                      engine=None):
        """Publish a new proof of an existing statement: its Lean text and a record with the written proof."""
        short = name.rsplit('.', 1)[1]
        record = (self.root_record(proof) if short == 'root' else record_text(description, weight=weight, proof=proof))
        folder = self.candidate(replace={name: text}, records={f'Small/{short}.md': record})
        return self.publish(folder, engine=engine)

    def split(self):
        def build():
            folder = self.candidate(
                modules={'Small/Parts.lean': module_text('\n\n'.join([
                    theorem('sumZero', SUM_ZERO), theorem('sumSucc', SUM_SUCC), theorem('sumTwo', ': oddSum 2 = 4')]))},
                replace={'Small.root': self.root_text(uses=['sumZero', 'sumSucc'])},
                imports={'Small.root': ['Small.Parts']},
                records={'Small/sumZero.md': record_text('The empty sum is zero.', weight='unit'),
                         'Small/sumSucc.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.', weight='unit'),
                         'Small/sumTwo.md': record_text('The first two odd numbers sum to four.', weight='unit',
                                                        proof='One plus three is four.'),
                         'Small/root.md': self.root_record()})
            self.publish(folder)
        self.scenario('split', build)

    def half(self):
        def build():
            self.split()
            self.replace_proof('Small.sumZero', theorem('sumZero', SUM_ZERO), 'A sum without terms is zero.',
                               description='The empty sum is zero.')
        self.scenario('half', build)

    def proved(self):
        def build():
            self.half()
            self.replace_proof('Small.sumSucc', theorem('sumSucc', SUM_SUCC),
                               'The sum of the first n + 1 odd numbers is the sum of the first n and the next one.',
                               description='Passing from n to n + 1 adds the odd number 2n + 1.')
        self.scenario('proved', build)

    def direct(self):
        def build():
            self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.')
        self.scenario('direct', build)

    def formal(self):
        def build():
            self.replace_proof('Small.root', self.root_formal(), 'By induction on $n$, comparing consecutive squares.')
        self.scenario('formal', build)

    def ways(self):
        """Two ways of proving the root, with a statement in every standing beneath them.

        way 1 (the root's own proof, accepted) names colA, stepE and unitG; way 2 (rootAlt, held) names
        colA and diagD. colA is held and names leafH. stepE is an accepted step that names monoB, which
        has no proof, one recorded approach and a second proof, monoBAlt, that review did not confirm and
        that names leafH. unitG is proved in Lean. diagD is not confirmed and names the step stepF, which
        has no proof. Nothing uses strayS."""
        def build():
            statements = [theorem('leafH', ': oddSum 1 = 1'), theorem('colA', ': oddSum 2 = 4', uses=['leafH']),
                          theorem('monoB', ': oddSum 3 = 9'), theorem('unitG', SUM_ZERO, proof='rfl'),
                          theorem('stepE', ': oddSum 4 = 16', uses=['monoB']), theorem('stepF', ': oddSum 5 = 25'),
                          theorem('diagD', ': oddSum 6 = 36', uses=['stepF']), theorem('strayS', ': oddSum 7 = 49')]
            folder = self.candidate(
                modules={'Small/Ways.lean': module_text('\n\n'.join(statements))},
                replace={'Small.root': self.root_text(uses=['colA', 'stepE', 'unitG'])},
                imports={'Small.root': ['Small.Ways']},
                records={'Small/leafH.md': record_text('The first odd number is one.', weight='unit'),
                         'Small/colA.md': record_text('The first two odd numbers sum to four.', weight='unit',
                                                      proof='Split into the two terms and add them.', short='Col',
                                                      statement='The sum $1 + 3$ equals $4$.'),
                         'Small/monoB.md': record_text('The first three odd numbers sum to nine.', weight='unit', short='Mono'),
                         'Small/unitG.md': record_text('The empty sum is zero.', weight='unit'),
                         'Small/stepE.md': record_text('The first four odd numbers sum to sixteen.', proof='Add seven to nine.'),
                         'Small/stepF.md': record_text('The first five odd numbers sum to twenty-five.'),
                         'Small/diagD.md': record_text('The first six odd numbers sum to thirty-six.', weight='unit',
                                                       proof='Add eleven to twenty-five.', short='Diag'),
                         'Small/strayS.md': record_text('Seven odd numbers sum to forty-nine, which is < 50.', weight='unit'),
                         'Small/root.md': self.root_record('Way 1: from Col and Mono, through the step for four terms.')},
                approaches={'Small/monoB/induction.md': '---\ntitle: Induction on the number of terms\nsessions: s-early\n---\n'
                            '## Idea\n\nCompare the sum of three terms with the sum of two.\n\n'
                            '## Where it stops\n\nThe comparison needs the sum of two terms in a form not yet stated.\n'})
            self.publish(folder, self.verdicts(folder, **{
                'Small.colA': {'accepted': False, 'reason': HELD_REASON},
                'Small.diagD': {'correct': 'not_confirmed', 'accepted': False, 'reason': GAP_REASON}}))
            folder = self.candidate(
                modules={'Small/Way2.lean': module_text('\n\n'.join([
                    theorem('rootAlt', ROOT_STATEMENTS[self.root_variant], uses=['colA', 'diagD']),
                    theorem('monoBAlt', ': oddSum 3 = 9', uses=['leafH'])]), imports=('Small.Ways',))},
                records={'Small/rootAlt.md': record_text('The root by way 2, from Col and Diag.', weight='unit',
                                                         proof='Way 2: from Col and Diag.', proves='Small.root'),
                         'Small/monoBAlt.md': record_text('Mono from the first odd number.', weight='unit',
                                                          proof='Add three and five to one.', proves='Small.monoB')})
            self.publish(folder, self.verdicts(folder, **{
                'Small.rootAlt': {'accepted': False, 'reason': 'Way 2 repeats the case split of way 1.'},
                'Small.monoBAlt': {'correct': 'not_confirmed', 'accepted': False, 'reason': 'The addition is not carried out.'}}))
        self.scenario('ways', build)


class RefutedRootCase(ScenarioCase):
    """States in which a declaration refutes the root: its record says `refutes:` and Lean confirms the negation.

    The root of these tests is the closed proposition ROOT_CLOSED. The stand-in compiler
    reads only the structure of a proof, so the "refutation" of a true statement compiles here."""
    root_variant = 'closed'
    NEGATION = ': ¬ (∀ n : Nat, oddSum n = n * n)'

    def refuted(self):
        def build():
            folder = self.candidate(
                modules={'Small/Against.lean': module_text(theorem('notRoot', self.NEGATION))},
                records={'Small/notRoot.md': record_text('Some initial sum of odd numbers is not a square.', weight='unit',
                                                         proof='The sum of the first two is taken to be five.',
                                                         refutes='Small.root')})
            self.publish(folder)
        self.scenario('refuted', build)

    def formally_refuted(self):
        def build():
            self.refuted()
            folder = self.candidate(replace={'Small.notRoot': theorem(
                'notRoot', self.NEGATION, proof='intro h\n  exact absurd (h 2) (by decide)')})
            self.publish(folder)
        self.scenario('formally refuted', build)

    def contested(self):
        def build():
            self.formally_refuted()
            self.replace_proof('Small.root', self.root_text(), 'By induction on $n$, comparing consecutive squares.')
        self.scenario('contested', build)
