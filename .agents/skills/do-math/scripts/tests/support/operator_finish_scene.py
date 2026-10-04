"""Operator scenes on real repositories/runners; doubles stop at Jobs and worker spawn.

The CLI reads the real worker prompt and schema. Command children run the shared
formal worker, whose spawn alone supplies external stdout/stderr/exit evidence.
"""
from copy import deepcopy
from contextlib import chdir
from dataclasses import replace
import json
import hashlib
from pathlib import Path

from do_math import formal, scheduled_operator as operator
from support.provider_runs import ProviderJobs, ScriptedCLI, claude_result, CLAUDE_INIT
from support.sim import Sim


class OperatorCLI(ScriptedCLI):
    def __init__(self):
        super().__init__()
        self.answer = None
        self.on_input = lambda call: None

    def spawn(self, command, **options):
        process = super().spawn(command, **options)
        return InputProcess(self, process, self.calls[-1])


class InputProcess:
    def __init__(self, cli, process, call):
        self.cli, self.process, self.call = cli, process, call

    @property
    def returncode(self):
        return self.process.returncode

    def communicate(self, input=None, timeout=None):
        command = self.call['command']
        self.call['prompt'] = input.decode('utf-8')
        if '--output-schema' in command:
            schema = json.loads(Path(command[command.index('--output-schema') + 1]).read_bytes())
        else:
            schema = json.loads(command[command.index('--json-schema') + 1])
        self.call['schema'] = schema
        if self.cli.answer is None:
            output = {key: rule['const'] if 'const' in rule else 'finished'
                      for key, rule in schema['properties'].items()}
        else:
            output = deepcopy(self.cli.answer)
        self.cli.final = json.dumps(output).encode('utf-8')
        self.call['output'] = output
        self.cli.on_input(self.call)
        return self.process.communicate(input, timeout)

    def kill(self):
        return self.process.kill()


class CommandProcess:
    def __init__(self, scene, command, options):
        self.scene, self.command, self.options = scene, list(command), options

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def wait(self):
        self.scene.commands.append({'command': self.command, **self.options})
        self.scene.on_command(self.command)
        self.options['stdout'].write(self.scene.stdout.encode('utf-8'))
        self.options['stderr'].write(self.scene.stderr.encode('utf-8'))
        return self.scene.exit_code


class Scene:
    def __init__(self, sim=None):
        self.sim = sim or Sim.activated()
        self.sim._apply('configure', config={'operator_enabled': True})
        self.cli = OperatorCLI()
        self.jobs = ProviderJobs(self.cli, clock=self.sim.clock)
        self.jobs.programs.append((
            lambda argv: argv[1:3] == ['-B', '-c'] and 'do_math.formal import _worker' in argv[3],
            lambda argv, cwd, env: formal._worker(Path(argv[5]), spawn=self.spawn_command)))
        self.ports = replace(self.sim.ports, jobs=self.jobs)
        self.workspace = Path(self.sim.instance['workspace'])
        self.args = (self.sim.repository, self.sim.instance_id, self.workspace)
        self.installation = self.sim.root / 'operator-finish-installation'
        self.installation.mkdir(exist_ok=True)
        (self.installation / 'SKILL.md').write_text('Synthetic installation edition', encoding='utf-8')
        self.commands = []
        self.command_error = None
        self.stdout, self.stderr, self.exit_code = '{}', '', 0
        self.on_command = lambda command: None
        operator.schedule('install', repository=self.args[0], instance=self.args[1], workspace=self.args[2],
                          scheduler=self.ports.scheduler, interval_seconds=7200, operator_timeout_seconds=5400)
        self.ports.scheduler.calls.clear()

    def spawn_command(self, command, **options):
        if self.command_error is not None:
            raise self.command_error
        return CommandProcess(self, command, options)

    def call(self, function, **options):
        if function in (operator.recovery, operator.check, operator.run_engine):
            options.setdefault('installation_root', self.installation)
        with chdir(self.sim.root):
            return function(*self.args, ports=self.ports, environment=self.sim.environment,
                            host_id=self.sim.host_id, codex_home=self.sim.codex_home, **options)

    def load(self):
        return self.sim.engine.store.load()

    def answer(self, outcome='repaired', *, diagnosed=False):
        output = {'summary': 'synthetic repair', 'observed_status': outcome,
                  'actions': ['fixture inspection'], 'evidence_paths': ['regression.txt'],
                  'user_questions': [], 'next_step': 'launcher continuation'}
        if diagnosed:
            output.update(repair_outcome=outcome, verification_evidence=['regression.txt'])
        self.cli.answer = output
        self.cli.on_input = lambda call: (Path(call['cwd']) / 'regression.txt').write_text(
            'Synthetic regression: former input now accepted', encoding='utf-8')
        return output

    def claude(self):
        config = self.sim.instance['config']
        self.sim._apply('configure', config={
            'tier_models': {**config['tier_models'], 'high': 'claude-opus-5'},
            'session_limits': {'work': {**config['session_limits']['work'], 'claude-opus-5': 3}},
            'claude_only_assigned_model': True})

    def limited(self):
        self.cli.stdout = b''.join(json.dumps(row).encode() + b'\n' for row in [
            {'type': 'rate_limit_event', 'rate_limit_info': {'status': 'rejected', 'rateLimitType': 'five_hour'}},
            CLAUDE_INIT, claude_result(b'{}', subtype='error_during_execution', is_error=True)])

    def wrong_model(self):
        self.cli.stdout = b''.join(json.dumps(row).encode() + b'\n' for row in [
            CLAUDE_INIT, claude_result(b'{}', modelUsage={'other-model': {'inputTokens': 1}})])


def diagnose(scene):
    """An ended rejected response, accepted independent review, then the real repair handoff.

    Registration, context, receipt, disposition, and repair binding use their
    producers. Every intermediate publication goes through the real store.
    """
    from do_math import activities, execution_lifecycle
    from do_math.canonical import canonical_json
    from do_math.control_protocol import SUBMIT_INTENT
    engine = scene.sim.engine
    at = scene.ports.clock.now()
    action = {'id': 'AC-failed', 'role': 'maintenance', 'repair_attempt': 2}
    target = engine._register_execution(action, {'id': 'EX-failed', 'role': 'maintenance', 'status': 'running'})
    source = 'runtime/artifacts/BA-failed/response.json'
    target.update(error='Installed receiver rejected valid output', result_ref=source)
    execution_lifecycle.transition_execution(target, 'stopping', at=at)
    execution_lifecycle.transition_execution(target, 'ended', at=at, outcome='execution_incomplete')
    activities.wait_for(engine.runtime, target['owner_activity_id'], kind='output_validation', reason='output_validation',
                        condition={'action_ids': [action['id']]}, next_owner='operational_review', at=at)
    engine.runtime.setdefault('waiting_actions', {})[action['id']] = {'kind': 'output_validation', 'action': deepcopy(target['action']),
        'execution_id': target['id'], 'reason': target['error']}
    engine._save({source: b'{"preserved":"actual rejected response"}'})
    review_action = {'id': 'AC-review', 'role': 'operational_review', 'target': 'EX-failed'}
    review = engine._register_execution(review_action, {'id': 'EX-review', 'role': 'operational_review', 'status': 'running'})
    review['input_bundle'] = 'BA-review'
    work = scene.workspace / 'review'
    work.mkdir(exist_ok=True)
    context = engine._context(review_action, work)
    prompt = canonical_json(context)
    prompt_ref = 'runtime/artifacts/BA-review/input.txt'
    review['input_manifest'] = {'prompt': {'artifact_ref': prompt_ref,
        'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}}
    engine._save({'runtime/artifacts/BA-review/input/submission/context.json': canonical_json(context),
                  prompt_ref: prompt})
    disposition = {'kind': 'repair', 'basis_refs': ['EX-failed'], 'next_owner': 'installation_recovery',
        'reason': 'Repair the installed receiver', 'repair_target': 'installation:scripts/do_math/engine.py',
        'meaning_preserving': True, 'verification': 'Run the receiver regression'}
    engine._apply_operational_disposition(review_action, disposition, 'EX-review')
    review = engine.runtime['executions']['EX-review']
    output_ref = 'runtime/artifacts/BA-review-output/submission/output.json'
    execution_lifecycle.record_submission_intent(review,
        {'candidate_id': 'CS-review', 'output_ref': output_ref, 'manifest': []},
        {'id': 'UC-review', 'kind': SUBMIT_INTENT, 'state': 'accepted',
         'execution_id': 'EX-review', 'received_at': at})
    execution_lifecycle.transition_execution(review, 'ended', at=at, outcome='output_accepted')
    engine._save({output_ref: canonical_json({'disposition': disposition})})
    record = next(row for row in engine.runtime['operational_dispositions'].values()
                  if row['execution_id'] == 'EX-review')
    return engine.complete_repair(record)
