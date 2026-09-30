"""``Sim``: the real engine on the port fakes (설계 4.1).

A Sim builds an instance through the public ``initialize`` and controls and
runs the real ``ResearchEngine`` on a Ports bundle of fakes: a clock whose
wall time is a distant year (a real-clock value that reaches the state stands
out), a process-free Git repository, the deterministic calls port, a Jobs fake
whose programs run the product's worker modules in process with the model
and Lean doubles at their spawn seam, fake scheduler and
HTTP ports, and a fake host. Tests inject events: controls, owner passes,
clock moves and restarts. They never replace engine methods or the store.

- ``Sim(root)``: an initialized instance; ``Sim.activated(root)`` also runs the
  public activation. ``Sim.activated()`` restores a copy of one activation this
  process built (설계 4.4): the public path costs seconds, a restore a fraction.
- ``control(action, text=..., config=...)``: queue a public control.
- ``step()`` runs one owner pass; ``run_until(condition, max_steps)`` runs passes
  until ``condition(sim)`` holds and otherwise fails with the waiting items.
- ``advance(seconds)`` moves wall and monotonic time; ``restart()`` drops all
  process state and builds the engine again from the repository.
- ``real_time_leaks()`` lists stored timestamps a real clock made while this Sim ran.

Two engine behaviours catch tests that hold state across a step. ``engine._save()``
may replace ``engine.runtime`` with the published object, so read
``sim.runtime`` (or ``engine.runtime``) again after anything that saves rather
than keeping an earlier reference. A public control reloads the published
state, so a change made directly on the engine and not saved before it is lost.

Determinism: one sequence of events and calls-port choices runs one way, and
every time and identifier from the clock port is the same between runs. The
file system is real, so what the product derives from it is not: the trust
record's fingerprint holds file creation times, which Windows cannot set, and
the content hashes and Git object IDs built on it differ between runs.
"""
from __future__ import annotations

import atexit
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

from do_math.engine import ResearchEngine, control, initialize
from do_math.ports import Ports
from support.fakes.calls import make_fake as fake_calls
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake as fake_git, make_repository
from support.fakes.host import make_fake as fake_host
from support.fakes.http import make_fake as fake_http
from support.fakes.jobs import FakeJobs
from support.fakes.scheduler import make_fake as fake_scheduler
from support.lean import LeanDouble
from support.model import ModelDouble

GOAL = 'Establish that adding zero to any natural number leaves it unchanged.'
WALL_YEAR = 2090
# The product's defaults, except what a Sim cannot offer: no scholarly server, no scheduled
# operator, and the synthetic trust environment's Lean (``activate`` builds it at ``shared/trust``).
CONFIG = {'scholarly_enabled': False, 'operator_enabled': False}
TIMESTAMP = re.compile(r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')


class Sim:
    def __init__(self, root, *, goal=GOAL, config=None, host=None, shared=None):
        """``shared`` holds the synthetic trust toolchain (default: ``root``); a template never copies it."""
        self.root = Path(root).resolve()
        self.shared = Path(shared).resolve() if shared is not None else self.root
        self._wire(FakeClock(wall=datetime(WALL_YEAR, 1, 1, tzinfo=timezone.utc)), host)
        self.repository = make_repository(self.root / 'repository')
        self.instance_id = initialize(self.repository, goal=goal, workspace=self.root / 'work',
                                      config={**CONFIG, 'lean_command': [str(self.trust_lean)], **(config or {})},
                                      ports=self.ports)['instance_id']
        self.engine = ResearchEngine(self.repository, self.instance_id, ports=self.ports)

    def _wire(self, clock, host, objects=None):
        self.started = datetime.now(timezone.utc).replace(microsecond=0)  # real time, to recognize leaks
        self.clock = clock
        self.model = ModelDouble(self.clock)
        self.lean = LeanDouble()
        self.jobs = FakeJobs(self._programs())
        self.ports = Ports(clock=self.clock, git_backend=fake_git(objects), calls=fake_calls(self.clock), jobs=self.jobs,
                           scheduler=fake_scheduler(), http=fake_http({}), host=host or fake_host())

    @classmethod
    def activated(cls, root=None, **options):
        """An active instance: built at ``root``, or without one restored from this process's template."""
        if root is None:
            if options:
                raise ValueError('the template Sim has the default options; pass a root to build another')
            return _template().restore()
        sim = cls(root, **options)
        sim.activate()
        return sim

    def process_state(self):
        """What the fakes hold outside the files: the clock, the Job fake's process identities and the Git objects."""
        return {'clock': self.clock.state(), 'next_pid': self.jobs._next_pid, 'owner': dict(self.jobs.owner),
                'git_objects': _copy_objects(self.ports.git_backend.objects)}

    @classmethod
    def restored(cls, root, shared, instance_id, state):
        """A new process on a repository and workspace a template copied back to ``root``."""
        sim = cls.__new__(cls)
        sim.root, sim.shared = Path(root).resolve(), Path(shared).resolve()
        sim._wire(FakeClock(*state['clock']), None, _copy_objects(state['git_objects']))
        sim.jobs._next_pid, sim.jobs.owner = state['next_pid'], dict(state['owner'])
        sim.repository, sim.instance_id = sim.root / 'repository', instance_id
        sim.engine = ResearchEngine(sim.repository, instance_id, ports=sim.ports)
        return sim

    def _programs(self):
        from do_math import claude_worker, codex_worker

        def worker(module):
            return lambda argv, cwd, env: module.run(Path(argv[2]), spawn=self.model.spawn)

        def lean(argv, cwd, env):
            from do_math import formal
            return formal._worker(Path(argv[5]), spawn=self.lean.spawn)

        return [(lambda argv: Path(argv[1]).name == 'codex_worker.py', worker(codex_worker)),
                (lambda argv: Path(argv[1]).name == 'claude_worker.py', worker(claude_worker)),
                # formal._job_run: [python, -B, -c, <import formal._worker>, <scripts>, <request>]
                (lambda argv: argv[1:3] == ['-B', '-c'] and 'do_math.formal import _worker' in argv[3], lean)]

    @property
    def trust_lean(self):
        """The synthetic toolchain's Lean executable; ``activate`` creates it under ``shared/trust``."""
        return self.shared / 'trust' / 'toolchain' / 'bin' / 'lean.exe'

    @property
    def instance(self):
        return self.engine.instance

    @property
    def runtime(self):
        return self.engine.runtime

    def control(self, action, **options):
        return control(self.repository, self.instance_id, action, ports=self.ports, **options)

    def step(self):
        self.engine.run(max_steps=1)

    def run_until(self, condition, max_steps):
        for _ in range(max_steps):
            if condition(self):
                return
            self.step()
        if condition(self):
            return
        raise AssertionError(f'condition not reached in {max_steps} owner passes; waiting: ' + json.dumps(
            self.waiting(), ensure_ascii=False, default=str))

    def waiting(self):
        """What the instance is waiting for: status, availability, waiting actions and open questions."""
        runtime = self.runtime
        return {'status': runtime.get('status'), 'availability': runtime.get('availability'),
                'lifecycle': self.instance.get('lifecycle', {}).get('state'),
                'activation_missing': self.instance.get('lifecycle', {}).get('activation', {}).get('missing'),
                'waiting_actions': [row.get('action', {}).get('kind') or row.get('reason')
                                    for row in runtime.get('waiting_actions', {}).values()],
                'questions': [question.get('id') for question in runtime.get('questions', [])]}

    def advance(self, seconds):
        self.clock.advance(seconds)

    def restart(self):
        """A new owner process on the same repository: nothing of the old process state survives."""
        self.jobs.owner = {**self.jobs.owner, 'pid': self.jobs.owner['pid'] + 4}
        self.engine = ResearchEngine(self.repository, self.instance_id, ports=self.ports)

    def activate(self, *, initial_roles=('intent_interpretation',), external_policy='disabled'):
        """The public activation: approvals, grants, probe and trust by control, then owner passes until active.

        The synthetic approval, trust and capability inputs are this Sim's; the
        engine applies the lifecycle changes and checks every activation gate.
        ``initial_roles`` are the roles of the initial grant (the product's
        initialization roles are intent interpretation and maintenance).
        ``external_policy`` is the adopted external policy; an active contract
        cannot change it later, so a Sim for HTTP effects adopts ``'explicit_grants'`` here.
        """
        from datetime import timedelta
        from do_math.canonical import exact_content_hash
        from do_math.model_policy import selection
        from research_fixtures import ROLES, charter_record, trust_fixture
        text = 'Synthetic Sim input; not actual host verification or user approval'
        windows = {key: value for key, value in {'tool_review_window_seconds': 60,
                                                 'self_check_response_window_seconds': 5}.items()
                   if key not in self.instance['config']}
        if windows:
            self._apply('configure', config=windows)
        expiry = (self.clock.wall() + timedelta(days=1)).isoformat()
        config_sha256 = exact_content_hash(self.instance['config'])
        initial_ref = selection(self.instance['config'], {'role': 'intent_interpretation'}, {},
                                self.instance['knowledge'], instance=self.instance)['profile_ref']
        charter = charter_record(self.instance['lifecycle']['immutable_input']['text'])
        controls = [
            ('decision', {'change': {'kind': 'initialization', 'operation': 'governance', 'records': [charter]}}),
            ('decision', {'change': {'kind': 'grant', 'grant': {'id': 'GR-initial-sim', 'kind': 'local',
                'roles': list(initial_roles), 'reuse': 'reusable', 'expires_at': expiry}}}),
            ('decision', {'change': {'kind': 'grant', 'grant': {'id': 'GR-research-sim', 'kind': 'local',
                'roles': list(ROLES) + ['formal_check'], 'reuse': 'reusable', 'expires_at': expiry}}}),
            ('decision', {'change': {'kind': 'initialization', 'operation': 'probe', 'config_sha256': config_sha256}}),
            ('trust', trust_fixture(self.shared, self.instance['config']['lean_command'], directory=self.shared / 'trust'))]
        for action, config in controls:
            self.control(action, text=text, config=config)
        self.engine.process_controls()
        self._check_applied()
        environment = next(iter(self.instance['trust_environments']))
        self._apply('trust', config={'operation': 'transition', 'env_id': environment})
        self._apply('decision', config={'change': {'kind': 'initialization', 'config_sha256': config_sha256,
            'adopt_current_governance': True, 'conversation_loss_policy': 'continue_authorized',
            'external_policy': external_policy, 'adopt_default_review_policy': True, 'initial_profile_ref': initial_ref,
            'initial_grant_ids': ['GR-initial-sim'], 'research_grant_ids': ['GR-research-sim']}})
        self.engine.run(until_active=True)
        if self.instance['lifecycle']['state'] != 'active':
            raise AssertionError('public activation did not reach active: ' + json.dumps(self.waiting(), default=str))

    def _apply(self, action, **options):
        self.control(action, **options)
        self.engine.process_controls()
        self._check_applied()

    def _check_applied(self):
        rejected = [row for row in self.runtime['history'] if row.get('kind') == 'rejected_user_control']
        if rejected:
            raise AssertionError('Sim controls rejected: ' + repr(rejected))

    def real_time_leaks(self):
        """Stored timestamps a real clock made while this Sim ran: product time that bypassed the clock port.

        The fake wall clock runs in a distant year, so no fake time falls in the
        real window; fixed times in fixture data fall before it.
        """
        text = json.dumps({'instance': self.instance, 'runtime': self.runtime}, default=str)
        now = datetime.now(timezone.utc)
        return sorted({match.group(0) for match in TIMESTAMP.finditer(text)
                       if self.started <= datetime.fromisoformat(match.group(0)).replace(tzinfo=timezone.utc) <= now})


def _remove(path):
    def unlock(function, target, _):
        os.chmod(target, stat.S_IWRITE)  # Git objects are written read-only
        function(target)
    if Path(path).exists():
        shutil.rmtree(path, onexc=unlock)


def _copy_objects(objects):
    """A copy of the Git fake's object maps; the objects themselves are immutable and shared."""
    return {git_dir: dict(stored) for git_dir, stored in objects.items()}


class _Template:
    """One activation built in this process, its untouched copy, and the fixed path copies are restored to.

    The same absolute path keeps the absolute paths inside the state true, so a
    restore replaces the previous copy: finish with one Sim before asking for the
    next. ``shared`` holds the trust toolchain and is never copied or cleared:
    the trust record fingerprints its files by creation time, which a copy changes.
    """

    def __init__(self, build=None):
        """``build(root, shared)`` returns the Sim to copy; by default the public activation."""
        self.base = Path(tempfile.mkdtemp(prefix='do-math-sim-')).resolve()
        atexit.register(_remove, self.base)
        self.live, self.pristine, self.shared = (self.base / name for name in ('live', 'pristine', 'shared'))
        sim = build(self.live, self.shared) if build is not None else Sim.activated(self.live, shared=self.shared)
        self.instance_id, self.state = sim.instance_id, sim.process_state()
        shutil.copytree(self.live, self.pristine)
        self.used = False

    def restore(self):
        if self.used:
            _remove(self.live)
            shutil.copytree(self.pristine, self.live)
        self.used = True
        return Sim.restored(self.live, self.shared, self.instance_id, self.state)


_TEMPLATE = []


def warm_template():
    """Build this process's template now; a test module's ``setUpModule`` so no test pays the build."""
    _template()


def _template():
    """This process's template; a failed build is not retried, since every later test would repeat its cost."""
    if not _TEMPLATE:
        _TEMPLATE.append('failed')
        _TEMPLATE[0] = _Template()
    elif _TEMPLATE[0] == 'failed':
        raise AssertionError('the Sim template failed to build earlier in this process')
    return _TEMPLATE[0]


_BUILT = {}


def built(name, build):
    """A restored copy of this process's template ``name``, which ``build(root, shared)`` makes once.

    For a start state the public path reaches only through slow steps (another
    activation option, model calls): the build runs once per process and every
    test restores its copy, as ``Sim.activated()`` does for the default activation.
    A failed build is not retried.
    """
    if name not in _BUILT:
        _BUILT[name] = 'failed'
        _BUILT[name] = _Template(build)
    elif _BUILT[name] == 'failed':
        raise AssertionError(f'the Sim template {name!r} failed to build earlier in this process')
    return _BUILT[name].restore()
