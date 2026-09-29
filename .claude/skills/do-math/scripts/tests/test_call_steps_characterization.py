"""Characterization of the model-call path (``ResearchEngine._call_steps``) before its cut (설계 2.3, 9.3).

The solved purpose scenario runs on the real engine with fake clock, Jobs,
scheduler and HTTP ports and the product's threaded calls port; the clock moves
one second between steps. After every step the published instance, each
runtime field and the text of each file the step's commits changed must match
the digests recorded in ``call_steps_trace.json`` (the full trace is megabytes;
the digests still name the step and field that changed). The files carry what
the state records only by hash, such as preserved outputs; a JSON file is
compared as its value. Values that differ between equal runs or checkouts are
normalized: the temporary root, the checkout's ``scripts`` path, content
hashes, Git object IDs, the fixture child's OS process identity, file
modification times, the synthetic trust directory's random suffix, the worker's
request and check IDs (minted from the worker's own clock and randomness) and
the control transport's tokens. The shipped submission-support archive is
recorded by its members and its size is dropped, because its bytes are the
product code of the worker's tools, not behaviour of the scenario.

The prompt documents are an input the product reads from the checkout, and a
checkout's line endings change their bytes (the main working tree can hold CRLF
where a fresh checkout holds LF), so prompt sizes and fitting differ. The record
therefore carries a fingerprint of the documents as read, and a checkout whose
documents differ skips this test with both fingerprints in the reason.

It takes about a minute, over the ten-second target: the trace needs the fake
clock from initialization on, so no real-clock template can be restored.

After an intended behaviour change, rewrite the digests with
``python tests/test_call_steps_characterization.py --regenerate`` and say why in the
commit. To see what changed, write the full normalized trace with ``--dump PATH``
at both versions and compare the two files.
"""
from datetime import datetime, timezone
from functools import partial
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.contracts import all_prompt_documents
from do_math.engine import ResearchEngine, initialize
from do_math.git_process import GitProcess
from do_math.local_host import LocalHost
from do_math.parallel import ThreadCalls
from do_math.ports import Ports
from purpose_fixtures import AcademicRunner, GOAL, PurposeHarness, formal_fixture
from research_fixtures import FixtureAdapter, _no_formal_check, activate, git_init
from runner_fixtures import ScriptedRunner
from support.fakes.clock import FakeClock
from support.fakes.http import make_fake as fake_http
from support.fakes.jobs import make_fake as fake_jobs
from support.fakes.scheduler import make_fake as fake_scheduler

TRACE = Path(__file__).with_name('call_steps_trace.json')
SCRIPTS = str(Path(__file__).resolve().parents[1])  # the checkout's product path, recorded as the verifier path
STEP_LIMIT = 45
VOLATILE = [
    (re.compile(r'\b(UC|TC|CE|CS|IN)-[0-9a-f]{16,64}\b'), r'\1-<hash>'),
    (re.compile(r'\b[0-9a-f]{64}\b'), '<sha256>'),
    (re.compile(r'\b[0-9a-f]{40}\b'), '<oid>'),
    (re.compile(r'\b[0-9]{16,}\b'), '<file-time>'),
    (re.compile(r'synthetic-trust-[a-z0-9_]{8}'), 'synthetic-trust-<tmp>'),
    (re.compile(r'\b(submit|preview)-RQ-[0-9A-Z]{26}\b'), r'\1-RQ-<id>'),
    (re.compile(r'\bMC-[0-9a-f]{24}\b'), 'MC-<id>'),
]
TOKEN_KEYS = {'transport_id', 'capability', 'endpoint', 'pid', 'creation_filetime'}


def changed_files(repository: Path, before: str, after: str) -> dict:
    """Text of each file the commits from ``before`` to ``after`` changed; ``None`` for a removed file."""
    def git(*arguments, stdin=None):
        return subprocess.run(['git', '-C', str(repository), *arguments], input=stdin, capture_output=True,
                              check=True).stdout
    fields = git('diff', '--name-status', '--no-renames', '-z', before, after).decode().split('\0')[:-1]
    rows = list(zip(fields[::2], fields[1::2]))
    present = [name for status, name in rows if status != 'D']
    batch = git('cat-file', '--batch', stdin=''.join(f'{after}:{name}\n' for name in present).encode())
    texts = {}
    for name in present:  # Each object is "<oid> <type> <size>\n<content>\n".
        header, batch = batch.split(b'\n', 1)
        size = int(header.split()[2])
        raw, batch = batch[:size], batch[size + 1:]
        # An archive ships product code (the worker's submission support); its members are the trace, not its bytes.
        texts[name] = ({'archive_members': sorted(zipfile.ZipFile(io.BytesIO(raw)).namelist())}
                       if name.endswith('.zip') else raw.decode('utf-8', 'replace'))
    return {name: texts.get(name) for _, name in rows}


def scenario_trace(root: Path) -> list:
    """Published instance, runtime and changed files after each step until the goal is solved."""
    (root / 'shared').mkdir()
    clock = FakeClock(wall=datetime(2026, 9, 29, tzinfo=timezone.utc))
    ports = Ports(clock=clock, git_backend=GitProcess(), calls=ThreadCalls(), jobs=fake_jobs(),
                  scheduler=fake_scheduler(), http=fake_http({}), host=LocalHost())
    trace = []
    with patch('do_math.local_host.adapter_for', side_effect=lambda profile: FixtureAdapter()):
        repository = git_init(root / 'repository')
        instance_id = initialize(repository, goal=GOAL, workspace=root / 'work-0',
                                 config=PurposeHarness.fixture_config(), clock=clock)['instance_id']
        engine = ResearchEngine(repository, instance_id, runner=ScriptedRunner(), formal_verifier=_no_formal_check,
                                ports=ports)
        activate(engine, root / 'shared', initialization_runner=ScriptedRunner())
        engine = ResearchEngine(repository, instance_id, runner=AcademicRunner(),
                                formal_verifier=partial(formal_fixture, jobs=ports.jobs), ports=ports)
        head = engine.head
        for _ in range(STEP_LIMIT):
            engine.run(max_steps=1)
            trace.append(json.loads(json.dumps({'instance': engine.instance, 'runtime': engine.runtime,
                                                'files': changed_files(repository, head, engine.head)})))
            head = engine.head
            if engine.instance['goal_status'] == 'mathematically_solved':
                return trace
            clock.advance(1)
    raise AssertionError('The scenario did not solve its goal within its bounded steps: ' + engine.instance['goal_status'])


def normalized(value, root: str, key=None):
    """``value`` with volatile leaves replaced; objects become sorted pairs so normalized keys cannot collide."""
    if key in TOKEN_KEYS and isinstance(value, (str, int)):
        return '<token>'
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and value['path'].endswith('.zip') and 'bytes' in value:
            value = {**value, 'bytes': '<archive>'}  # the size of shipped product code
        pairs = [[normalized(k, root), normalized(v, root, k)] for k, v in value.items()]
        return sorted(pairs, key=lambda pair: json.dumps(pair, sort_keys=True))
    if isinstance(value, list):
        return [normalized(item, root) for item in value]
    if isinstance(value, str):
        for path, name in ((root, '<root>'), (SCRIPTS, '<scripts>')):
            for form in (path, path.replace('\\', '/'), path.replace('\\', '\\\\')):  # plain, POSIX, JSON-escaped
                value = value.replace(form, name)
        for pattern, replacement in VOLATILE:
            value = pattern.sub(replacement, value)
    return value


def parsed(text):
    """A JSON file's value, so its keys are normalized like the state's; other text as it is."""
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return text


def recorded_now() -> list:
    """The normalized fields of every step: ``{'instance': ..., 'runtime.<key>': ..., 'file:<path>': ...}``."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory).resolve()
        return [{normalized(name, str(root)): normalized(value, str(root)) for name, value in
                 [('instance', step['instance'])]
                 + [('runtime.' + key, v) for key, v in step['runtime'].items()]
                 + [('file:' + path, parsed(text)) for path, text in step['files'].items()]}
                for step in scenario_trace(root)]


def digests(steps: list) -> list:
    return [{name: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
             for name, value in fields.items()} for fields in steps]


def documents_fingerprint() -> str:
    """Digest of every prompt document's path and bytes as the product reads them."""
    documents = {row['path']: row['sha256'] for rows in all_prompt_documents().values() for row in rows}
    return hashlib.sha256(json.dumps(sorted(documents.items())).encode()).hexdigest()


class CallStepsCharacterization(unittest.TestCase):
    def test_every_step_publishes_the_recorded_state(self):
        record = json.loads(TRACE.read_text(encoding='utf-8'))
        if record['documents'] != documents_fingerprint():
            self.skipTest(f"recorded against other prompt-document bytes ({record['documents'][:12]}, here "
                          f"{documents_fingerprint()[:12]}); line endings differ between checkouts. "
                          "Regenerate on this checkout before a behaviour-preserving change to use it here.")
        expected = record['steps']
        actual = digests(recorded_now())
        for step, (want, got) in enumerate(zip(expected, actual)):
            changed = sorted(name for name in want.keys() | got.keys() if want.get(name) != got.get(name))
            self.assertEqual(changed, [], f'step {step} differs from the recorded trace in these fields')
        self.assertEqual(len(actual), len(expected), 'the scenario solved its goal after a different number of steps')


if __name__ == '__main__':
    if sys.argv[1:] == ['--regenerate']:
        TRACE.write_text(json.dumps({'documents': documents_fingerprint(), 'steps': digests(recorded_now())},
                                    indent=1) + '\n', encoding='utf-8')
    elif sys.argv[1:2] == ['--dump'] and len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(json.dumps(recorded_now(), ensure_ascii=False, indent=1), encoding='utf-8')
    else:
        unittest.main()
