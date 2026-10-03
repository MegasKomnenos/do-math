"""Public CLI init on the existing Sim ports, before any engine or repository exists."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
from pathlib import Path

from do_math import cli
from do_math.engine import ResearchEngine
from support.fakes.clock import FakeClock
from support.sim import CONFIG, GOAL, Sim, WALL_YEAR


def git_init_main(argv, values):
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(argv, ports=values.ports, environment=values.environment,
                        codex_home=values.codex_home, host_id=values.host_id)
    return code, json.loads(output.getvalue())


def git_init_sim(root, shared, *, object_format='sha1', empty=False):
    sim = Sim.__new__(Sim)
    sim.root, sim.shared = Path(root).resolve(), Path(shared).resolve()
    sim.root.mkdir(parents=True, exist_ok=True)
    sim._wire(FakeClock(wall=datetime(WALL_YEAR, 1, 1, tzinfo=timezone.utc)), None)
    sim.ports.git_backend.init_object_format = object_format
    sim.repository = sim.root / 'repository'
    if empty:
        sim.repository.mkdir()
    config = sim.root / 'git-init-config.json'
    config.write_text(json.dumps({**CONFIG, 'lean_command': [str(sim.trust_lean)]}), encoding='utf-8')
    code, envelope = git_init_main(['init', '--repository', str(sim.repository),
        '--create-repository', '--workspace', str(sim.root / 'work'), '--goal', GOAL,
        '--config-file', str(config)], sim)
    if code != 0:
        raise AssertionError(envelope)
    sim.instance_id = envelope['result']['instance_id']
    sim.engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports,
        codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
    return sim
