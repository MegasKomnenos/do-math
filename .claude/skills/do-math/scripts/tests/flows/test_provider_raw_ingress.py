"""strict collector와 live decode의 차이를 실제 worker→runner→owner로 검산한다."""
from copy import deepcopy
import json
import unittest


from do_math.claude_adapter import ADAPTERS
from do_math.observations import ObservationTracker
from do_math.execution_profiles import OBSERVATION_MODES
from support.provider_live import batch, running_execution
from support.provider_runs import ProviderJobs, ScriptedCLI, model_runner, CLAUDE_INIT, claude_result, codex_stream
from support.sim import Sim, warm_template

setUpModule = warm_template

# 외곽 오형태, 중복 키, 유한하지 않은 수. 각 행 뒤에 동일한 정상 사건을 붙인다.
RAW_CASES = (('null', b'null\n'), ('list', b'[]\n'), ('zero', b'0\n'),
    ('string', b'"bad"\n'), ('boolean', b'true\n'),
    ('duplicate', b'{"type":"turn.started","type":"turn.completed"}\n'),
    ('nonfinite', b'{"type":"usage","value":NaN}\n'))


class RawIngressTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.sim = Sim.activated()
        self.scenes = []
        for mode in OBSERVATION_MODES:
            control_id = 'EX-raw-normal-' + mode.replace('_', '-')
            control_workspace = running_execution(self.sim, control_id, 'research_work')
            control = ObservationTracker(control_id, control_workspace,
                {'observation_mode': mode, 'research_self_checks': False}, time_port=self.sim.clock)
            normal = batch(self.sim, [{'type': 'turn.started'}], control_workspace / 'stdout.jsonl', terminated=True)
            normal.stream_path.write_bytes(b''.join(normal.rows))
            self.sim.engine._observe_running(control_id, control, normal)
            self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
            for provider in ADAPTERS:
                for label, raw in RAW_CASES:
                    eid = 'EX-raw-' + mode.replace('_', '-') + '-' + provider + '-' + label
                    workspace = running_execution(self.sim, eid, 'research_work')
                    tracker = ObservationTracker(eid, workspace,
                        {'observation_mode': mode, 'research_self_checks': False}, time_port=self.sim.clock)
                    self.assertEqual(self.sim.runtime['executions'][eid]['status'], 'running')
                    self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                    self.scenes.append((provider, mode + ":" + label, raw, eid, workspace, tracker))

    def test_malformed_raw_rows_are_consumed_once_and_the_following_row_reaches_storage(self):
        failures = []
        for provider, label, raw, eid, workspace, tracker in self.scenes:
            good = {'type': 'turn.started', 'execution_id': eid}
            framing = codex_stream(b'{}').splitlines(keepends=True) if provider == 'codex' else [
                json.dumps(CLAUDE_INIT).encode() + b'\n', json.dumps(claude_result(b'{}')).encode() + b'\n']
            stream = b''.join(framing[:-1]) + raw + json.dumps(good).encode() + b'\n' + framing[-1]
            cli = ScriptedCLI(stdout=stream)
            jobs = ProviderJobs(cli, clock=self.sim.clock)
            before = set(self.sim.runtime['observation_facts'])
            try:
                result = model_runner(workspace.parent, jobs, self.sim.clock).run(prompt='원시 입력 계약 검산',
                    output_schema={}, workspace=workspace, evidence_dir=workspace.parent / 'raw-evidence',
                    model='claude:claude-sonnet-5' if provider == 'claude' else 'test-model',
                    effort='high', timeout_seconds=10,
                    on_observation=lambda incoming: self.sim.engine._observe_running(eid, tracker, incoming))
                added = [json.loads(value['event_json']) for key, value in self.sim.runtime['observation_facts'].items() if key not in before]
                self.assertEqual([event for event in added if event == good], [good])
                rejected = [event for event in added if isinstance(event, dict) and event.get('kind') == 'observation_input_rejected']
                self.assertEqual(len(rejected), 1)
                self.assertEqual(rejected[0]['next_owner'], 'adapter')
                self.assertTrue(rejected[0]['reason'])
                self.assertEqual(result['status'], 'failed')  # strict collector는 같은 오형태 원 바이트를 반려한다.
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                state, head = deepcopy(self.sim.runtime), self.sim.engine.head
                self.sim.engine._observe_running(eid, tracker, batch(self.sim, [], workspace.parent / 'raw-evidence/stdout.jsonl',
                    start=len(stream), terminated=True))
                self.assertEqual(self.sim.runtime, state)
                self.assertEqual(self.sim.engine.head, head)
            except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
                failures.append((provider, label, type(error).__name__, str(error)))
            self.assertEqual(len(cli.calls), 1)
            self.assertTrue(all(job.closed for job in jobs.launched))
        self.assertEqual(failures, [], 'live 반려와 strict collector는 같은 원 바이트 계약을 지켜야 한다')
