"""정상 역할 응답의 native usage만 바꾸는 CLI spawn 대역. 제품 수신기는 유지한다."""
import json
from pathlib import Path

from support.model import FakeCLI, ModelDouble, codex_stream_bytes
from support.provider_runs import CLAUDE_INIT, claude_result
from support.fakes.jobs import job_turn
from support.sim import Sim, built

USAGE = {'input_tokens': 2 ** 53 + 1, 'output_tokens': 2 ** 53, 'cost_usd': 0.25, 'cache_creation_input_tokens': 0.25}


class NumericModel(ModelDouble):
    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return NumericCLI(self, list(command), stdout, stderr, Path(cwd))


class NumericCLI(FakeCLI):
    def _write_stream(self, final):
        if '--print' in self.command:
            events = [CLAUDE_INIT, claude_result(final.encode('utf-8'),
                structured='--json-schema' in self.command, usage=USAGE)]
        else:
            events = [json.loads(row) for row in codex_stream_bytes(final).splitlines()]
            events[-1]['usage'] = USAGE
            Path(self.command[self.command.index('--output-last-message') + 1]).write_bytes(final.encode('utf-8'))
        for event in events:
            self.stdout.write(json.dumps(event).encode('utf-8') + b'\n')
            self.stdout.flush()
            job_turn()


def _build_claude(root, shared):
    model = 'claude-opus-5'
    sim = Sim(root, shared=shared, config={'tier_models': {tier: model for tier in ('high', 'medium', 'low')},
        'session_limits': {'work': {model: 1}}})
    sim.model = NumericModel(sim.clock)
    sim.activate()
    return sim


def numeric_sim(provider):
    if provider == 'codex':
        sim = Sim.activated()
    elif provider == 'claude':
        sim = built('provider-numeric-claude', _build_claude)
    else:
        raise ValueError('새 공급자의 수치 입력 builder가 필요하다: ' + provider)
    sim.model = NumericModel(sim.clock)
    return sim
