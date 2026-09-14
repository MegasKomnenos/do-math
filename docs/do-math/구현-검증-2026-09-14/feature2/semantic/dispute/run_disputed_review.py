"""Actual CLI review debate after two explicitly synthetic initial judgments.

Expected normal path: actual Lean; 2 synthetic initial fixtures; actual organizer,
3 independent judges, original logical-slot answer, and the same 3 judge slots.
No initial fixture is represented as actual-model evidence. No direct API keys.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
SOURCE = 'theorem zero_identity (n : Nat) : n + 0 = n := Nat.add_zero n\n'
STATEMENT = 'For every natural number n, n + 0 = n.'
EXPLANATION = 'The variable n ranges over Nat, the natural numbers. Nat.add_zero n proves the displayed identity. No claim about another domain is being made.'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_manifest(root):
    return [{'path': path.relative_to(root).as_posix(), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
            for path in sorted(root.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']


class BoundedCLI:
    def __init__(self, delegate, evidence, limit):
        self.delegate, self.evidence, self.limit = delegate, evidence, limit
        self.calls = []

    def run(self, **kwargs):
        if len(self.calls) >= self.limit:
            raise RuntimeError('The explicit total actual CLI invocation limit is exhausted')
        prompt = kwargs['prompt']
        context = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
        action = context['action']
        entry = {'number': len(self.calls) + 1, 'action': deepcopy(action), 'actor_kind': 'actual_codex_cli',
                 'prompt_sha256': sha(prompt.encode()), 'workspace': str(kwargs['workspace']), 'evidence_dir': str(kwargs['evidence_dir']),
                 'model': kwargs['model'], 'effort': kwargs['effort'], 'started_at': datetime.now(timezone.utc).isoformat()}
        self.calls.append(entry)
        dump(self.evidence / 'actual-cli-invocations.json', self.calls)
        result = self.delegate.run(**kwargs)
        entry.update(status=result.get('status'), usage=result.get('usage', {}), output=result.get('output'),
                     ended_at=datetime.now(timezone.utc).isoformat(), error=result.get('error'))
        dump(self.evidence / 'actual-cli-invocations.json', self.calls)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', required=True, type=Path, help='Frozen do-math skill root containing scripts/do_math')
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--model', default='gpt-5.6-sol')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--max-cli-calls', type=int, default=8)
    parser.add_argument('--call-timeout', type=int, default=300)
    parser.add_argument('--run-timeout', type=int, default=2400)
    parser.add_argument('--plan-only', action='store_true', help='Write configuration/source manifests without Lean or CLI execution')
    args = parser.parse_args()
    skill_root, evidence = args.skill_root.resolve(), args.evidence.resolve()
    if not (skill_root / 'scripts' / 'do_math' / 'engine.py').is_file():
        parser.error('--skill-root is not a do-math skill root')
    if args.max_cli_calls < 8: parser.error('The complete requested debate requires at least 8 actual CLI invocations')
    evidence.mkdir(parents=True, exist_ok=True)
    manifest = source_manifest(skill_root)
    dump(evidence / 'skill-source-manifest.json', {'skill_root': str(skill_root), 'files': manifest})
    (evidence / 'case.lean').write_text(SOURCE, encoding='utf-8')
    dump(evidence / 'case.json', {'statement': STATEMENT, 'explanation': EXPLANATION,
        'lean_source_sha256': sha(SOURCE.encode()), 'declarations': ['zero_identity'],
        'initial_judgments': 'Two intentionally synthetic fixtures; not actual model executions',
        'expected_actual_stages': ['organize', 'judge', 'judge', 'judge', 'answer', 'judge', 'judge', 'judge'],
        'actual_cli_invocation_limit': args.max_cli_calls, 'model': args.model, 'effort': args.effort,
        'formal_verification': 'Actual frozen verify_lean adapter; no compiler test double',
        'goal_audit': 'Not part of this case; the independent all-real normal workflow owns goal evidence'})
    if args.plan_only:
        print(json.dumps({'prepared': True, 'normal_actual_cli_calls': 8, 'synthetic_initial_judgments': 2,
                          'max_cli_calls': args.max_cli_calls, 'evidence': str(evidence)}))
        return 0
    if (evidence / 'repository').exists():
        parser.error('Use a fresh evidence directory for an actual run; existing evidence is immutable')
    sys.path.insert(0, str(skill_root / 'scripts'))
    from do_math.engine import ResearchEngine, initialize, ENGINE_SHA256
    from do_math.formal import discover_lean
    from do_math.model_runner import CodexModelRunner
    from do_math.contracts import render_prompt
    from do_math.repository import canonical_json, new_id
    import jsonschema

    lean = discover_lean()
    if not lean: raise RuntimeError('No actual Lean installation is available')
    repository = evidence / 'repository'
    repository.mkdir()
    subprocess.run(['git', '-C', str(repository), 'init', '-q'], check=True)
    initialized = initialize(repository, goal=STATEMENT, workspace=evidence / 'workspace',
        config={'model': args.model, 'effort': args.effort, 'reviewers': 2, 'review_rounds': 2,
                'goal_auditors': 2, 'work_calls': args.max_cli_calls, 'operations_calls': 2,
                'call_timeout_seconds': args.call_timeout, 'run_timeout_seconds': args.run_timeout,
                'max_cycles': 3, 'max_output_repairs': 0, 'max_input_bytes': 500000,
                'observation_idle_seconds': args.call_timeout + 60, 'max_observation_reviews': 1,
                'lean_command': lean})
    actual = BoundedCLI(CodexModelRunner(), evidence, args.max_cli_calls)
    engine = ResearchEngine(repository, initialized['instance_id'], runner=actual)
    kid = new_id('KN')
    cycle_id = None
    exit_code = 1
    start = time.monotonic()
    result_report = {'passed': False, 'case': 'actual CLI dispute with explicitly synthetic initial fixtures'}
    try:
        with engine.store.writer_lock():
            engine.instance['knowledge'][kid] = {'id': kid, 'revision': 1, 'kind': 'theorem', 'title': 'Natural zero identity',
                'statement': STATEMENT, 'explanation': EXPLANATION, 'summary': 'Adding zero preserves every natural number.',
                'lean_code': SOURCE, 'declaration_names': ['zero_identity'], 'dependencies': [],
                'status': 'candidate', 'reviews': [], 'required_reviews': 2,
                'producer_execution': 'USER-PROVIDED-CASE', 'source_kind': 'explicit fixed test proposal'}
            engine.runtime['queue'] = []
            engine._enqueue('formal_check', kid)
            engine._save()
            engine._formal(deepcopy(engine.runtime['queue'][0]))
            item = engine.instance['knowledge'][kid]
            dump(evidence / 'actual-formal-result.json', item['formal'])
            if item['formal']['status'] != 'verified' or not item.get('review_cycle_id'):
                raise RuntimeError('Actual Lean verification or active environment binding did not complete')
            cycle_id = item['review_cycle_id']
            for number in range(2):
                action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cycle_id and a.get('stage') == 'initial')
                execution_id, activity_id = new_id('EX'), new_id('AY')
                workspace = evidence / 'synthetic-fixtures' / execution_id
                workspace.mkdir(parents=True)
                context = engine._context(action, workspace)
                schema = engine._response_schema(action)
                prompt = render_prompt('identity_review', context, output_schema=schema)
                output = {'proposal_digest': context['role_review']['proposal_digest'],
                    'summary': 'SYNTHETIC INITIAL FIXTURE, not an actual model judgment: ' + ('a deliberately spurious domain objection' if number == 0 else 'matching control judgment'),
                    'used_sources': ['proposal:statement', 'proposal:explanation', 'proposal:lean_code'], 'questions': [],
                    'decision': 'mismatch' if number == 0 else 'match', 'scope_complete': True,
                    'findings': [{'id': 'synthetic-domain-objection', 'statement': 'The explanation appears to extend n beyond natural numbers, while the Lean binder is Nat.',
                                  'evidence': ['proposal:explanation', 'proposal:lean_code']}] if number == 0 else []}
                jsonschema.validate(output, schema)
                input_bundle, result_bundle = new_id('BA'), new_id('BA')
                engine.runtime['executions'][execution_id] = {'id': execution_id, 'activity_id': activity_id,
                    'role': 'identity_review', 'actor_kind': 'synthetic_fixture', 'model': None,
                    'status': 'ended', 'action': deepcopy(action), 'outcome': 'output_accepted',
                    'input_snapshot': engine.head, 'input_sha256': sha(prompt.encode()), 'input_bundle': input_bundle,
                    'artifact_bundle': result_bundle, 'engine_sha256': ENGINE_SHA256, 'extensions': {},
                    'fixture_notice': 'Not executed by any model; intentionally constructed to exercise the dispute protocol'}
                engine.runtime['activities'][activity_id] = {'id': activity_id, 'role': 'identity_review',
                    'status': 'finished', 'execution_ids': [execution_id], 'actor_kind': 'synthetic_fixture'}
                engine._remove_action(action)
                engine._apply_identity_review(action, output, execution_id)
                fixture = {'type': 'synthetic_initial_fixture', 'actual_model_execution': False,
                           'action': action, 'execution_id': execution_id, 'output': output}
                raw_fixture = canonical_json(fixture)
                engine._save({f'runtime/artifacts/{input_bundle}/input.txt': prompt.encode(),
                    f'runtime/artifacts/{input_bundle}/schema.json': canonical_json(schema),
                    f'runtime/artifacts/{result_bundle}/synthetic-fixture.json': raw_fixture})
                (evidence / f'synthetic-initial-{number}.jsonl').write_text(json.dumps(fixture, ensure_ascii=False) + '\n', encoding='utf-8')
            if engine.runtime['review_cycles'][cycle_id]['phase'] != 'organize':
                raise RuntimeError('The two synthetic fixtures did not open the real dispute path')
        while engine.runtime['review_cycles'][cycle_id]['status'] == 'working':
            if len(actual.calls) >= args.max_cli_calls or time.monotonic() - start > args.run_timeout:
                raise RuntimeError('Bounded debate did not finish within its actual-call/time envelope')
            engine.run(max_steps=1)
            dump(evidence / 'progress.json', {'actual_cli_invocations': len(actual.calls), 'cycle': engine.runtime['review_cycles'][cycle_id],
                                            'runtime_status': engine.runtime['status'], 'questions': engine.runtime['questions']})
            if engine.runtime['status'] in {'paused', 'closed', 'waiting', 'budget_exhausted'}:
                raise RuntimeError('Actual debate stopped: ' + json.dumps(engine.runtime['questions'], ensure_ascii=False))
        cycle = engine.runtime['review_cycles'][cycle_id]
        stages = [call['action'].get('stage') for call in actual.calls]
        expected = ['organize', 'judge', 'judge', 'judge', 'answer', 'judge', 'judge', 'judge']
        if stages != expected: raise RuntimeError('Actual executions took a different stage path: ' + str(stages))
        if any(call.get('status') != 'completed' for call in actual.calls): raise RuntimeError('An actual CLI execution did not complete')
        if cycle['decision'] != 'match' or not engine.instance['knowledge'][kid]['identity_assessment']['effective']:
            raise RuntimeError('The actual debate did not produce an effective identity match')
        answer = next(call for call in actual.calls if call['action']['stage'] == 'answer')
        if answer['action']['slot'] != 'initial-0': raise RuntimeError('The objection was not returned to its original logical slot')
        judges = [[call['action']['slot'] for call in actual.calls if call['action']['stage'] == 'judge' and call['action']['round'] == round_number] for round_number in (1, 2)]
        if judges[0] != judges[1] or len(set(judges[0])) != 3: raise RuntimeError('The same three distinct judge slots were not maintained')
        if source_manifest(skill_root) != manifest: raise RuntimeError('Frozen skill source changed during the actual run')
        result_report.update(passed=True, actual_cli_invocations=len(actual.calls), synthetic_initial_judgments=2,
            actual_stages=stages, cycle_id=cycle_id, knowledge_id=kid, decision=cycle['decision'],
            effective=engine.instance['knowledge'][kid]['identity_assessment']['effective'],
            actual_lean=True, all_initial_judgments_synthetic=True, all_debate_judgments_actual_cli=True,
            elapsed_seconds=time.monotonic()-start)
        exit_code = 0
    except Exception as error:
        result_report.update(error=f'{type(error).__name__}: {error}', traceback=traceback.format_exc(),
                             actual_cli_invocations=len(actual.calls), cycle_id=cycle_id, elapsed_seconds=time.monotonic()-start)
    finally:
        dump(evidence / 'final-instance.json', engine.instance)
        dump(evidence / 'final-runtime.json', engine.runtime)
        dump(evidence / 'result.json', result_report)
        subprocess.run(['git', '-C', str(repository), 'bundle', 'create', str(evidence / 'state.bundle'), '--all'], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jsonl = [{'path': path.relative_to(evidence).as_posix(), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
                 for path in sorted(evidence.rglob('*.jsonl'))]
        dump(evidence / 'jsonl-manifest.json', jsonl)
        print(json.dumps(result_report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
