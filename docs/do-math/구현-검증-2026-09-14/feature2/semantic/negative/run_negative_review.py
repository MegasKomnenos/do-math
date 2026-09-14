"""Exactly two actual CLI initial reviewers for a quantifier-reversal fixture.

The Lean theorem is true and checked by actual Lean. The explanation/summary
are intentionally false fixture data, not fabricated reviewer outputs. This
case stops before organizer/final judgment and does not establish a final
system mismatch assessment or a generic model-detection success rate.
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
SOURCE = '''theorem successor_witness : ∀ n : Nat, ∃ m : Nat, m = n + 1 := by
  intro n
  exact ⟨n + 1, rfl⟩
'''
STATEMENT = 'For every natural number n, there exists a natural number m such that m = n + 1.'
EXPLANATION = 'The proof supplies one fixed natural number m that works simultaneously for every natural number n. In other words, there exists m in Nat such that for all n in Nat, m = n + 1.'
SUMMARY = 'There is a single natural number m equal to n + 1 for every natural number n.'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
def manifest(root):
    return [{'path': p.relative_to(root).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']


class TwoCalls:
    def __init__(self, delegate, evidence): self.delegate, self.evidence, self.calls = delegate, evidence, []
    def run(self, **kwargs):
        if len(self.calls) >= 2: raise RuntimeError('The two actual CLI invocation limit is exhausted')
        prompt = kwargs['prompt']
        context = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
        action = context['action']
        if action['role'] != 'identity_review' or action.get('stage') != 'initial':
            raise RuntimeError('This case authorizes only two actual initial-review CLI calls')
        if context['role_review']['completed_results']:
            raise AssertionError('Current peer results leaked into an initial review input')
        call = {'number': len(self.calls) + 1, 'actor_kind': 'actual_codex_cli', 'action': deepcopy(action),
                'input_sha256': sha(prompt.encode()), 'workspace': str(kwargs['workspace']), 'evidence_dir': str(kwargs['evidence_dir']),
                'model': kwargs['model'], 'effort': kwargs['effort'], 'started_at': datetime.now(timezone.utc).isoformat()}
        self.calls.append(call)
        dump(self.evidence/'actual-cli-invocations.json', self.calls)
        result = self.delegate.run(**kwargs)
        call.update(status=result.get('status'), output=result.get('output'), usage=result.get('usage', {}), error=result.get('error'),
                    ended_at=datetime.now(timezone.utc).isoformat())
        dump(self.evidence/'actual-cli-invocations.json', self.calls)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    skill, evidence = args.skill_root.resolve(), args.evidence.resolve()
    if (evidence/'repository').exists(): parser.error('A fresh evidence directory is required')
    evidence.mkdir(parents=True, exist_ok=True)
    frozen = manifest(skill)
    dump(evidence/'skill-source-manifest.json', {'skill_root': str(skill), 'files': frozen})
    (evidence/'case.lean').write_text(SOURCE, encoding='utf-8')
    own = Path(__file__).read_bytes()
    (evidence/'run_negative_review.py').write_bytes(own)
    dump(evidence/'script-manifest.json', {'path': 'run_negative_review.py', 'sha256': sha(own), 'bytes': len(own)})
    dump(evidence/'case.json', {'source_sha256': sha(SOURCE.encode()), 'true_formal_statement': STATEMENT,
        'deliberately_incorrect_explanation': EXPLANATION, 'deliberately_incorrect_summary': SUMMARY,
        'fixture_error': 'forall n exists m is replaced by exists m forall n in the explanatory material',
        'expected_error_label_not_supplied_to_reviewers': True, 'synthetic_reviewer_outputs': 0,
        'scope': 'Actual primary negative detection only; stop before organize and final adjudication',
        'maximum_actual_cli_invocations': 2})
    sys.path.insert(0, str(skill/'scripts'))
    from do_math.engine import initialize, ResearchEngine
    from do_math.formal import discover_lean
    from do_math.model_runner import CodexModelRunner
    from do_math.repository import new_id
    lean = discover_lean()
    if not lean: raise RuntimeError('Actual Lean is unavailable')
    repository = evidence/'repository'
    repository.mkdir()
    subprocess.run(['git', '-C', str(repository), 'init', '-q'], check=True)
    initialized = initialize(repository, goal=STATEMENT, workspace=evidence/'workspace', config={
        'model': 'gpt-5.6-sol', 'effort': 'medium', 'reviewers': 2, 'review_rounds': 2,
        'work_calls': 2, 'operations_calls': 1, 'max_output_repairs': 0, 'max_input_bytes': 500000,
        'call_timeout_seconds': 300, 'run_timeout_seconds': 900, 'observation_mode': 'event_driven',
        'observation_idle_seconds': 360, 'max_observation_reviews': 1, 'lean_command': lean})
    runner = TwoCalls(CodexModelRunner(sandbox='danger-full-access'), evidence)
    engine = ResearchEngine(repository, initialized['instance_id'], runner=runner)
    kid, cycle_id = new_id('KN'), None
    report = {'passed': False, 'actual_lean': True, 'actual_initial_reviewers': True, 'synthetic_reviewer_outputs': 0}
    started = time.monotonic()
    status = 1
    try:
        with engine.store.writer_lock():
            engine.instance['knowledge'][kid] = {'id': kid, 'revision': 1, 'kind': 'theorem', 'title': 'Successor witness',
                'statement': STATEMENT, 'explanation': EXPLANATION, 'summary': SUMMARY, 'lean_code': SOURCE,
                'declaration_names': ['successor_witness'], 'dependencies': [], 'status': 'candidate', 'reviews': [],
                'required_reviews': 2, 'producer_execution': 'USER-PROVIDED-PROPOSAL'}
            engine.runtime['queue'] = []
            engine._enqueue('formal_check', kid)
            engine._save()
            engine._formal(deepcopy(engine.runtime['queue'][0]))
            item = engine.instance['knowledge'][kid]
            dump(evidence/'actual-formal-result.json', item['formal'])
            if item['formal']['status'] != 'verified' or item['formal'].get('trust_environment_status') != 'active':
                raise RuntimeError('Actual formal validation did not finish under an active environment')
            cycle_id = item['review_cycle_id']
        for number in range(2):
            first = engine.runtime['queue'][0]
            if first.get('stage') != 'initial' or first.get('review_cycle_id') != cycle_id:
                raise RuntimeError('Expected another initial review; refusing to run a later phase')
            engine.run(max_steps=1)
            if engine.runtime['status'] in {'paused', 'closed', 'waiting', 'budget_exhausted'}:
                raise RuntimeError('Initial review did not complete: ' + json.dumps(engine.runtime['questions'], ensure_ascii=False))
        cycle = engine.runtime['review_cycles'][cycle_id]
        if len(runner.calls) != 2 or any(c.get('status') != 'completed' for c in runner.calls):
            raise RuntimeError('Exactly two completed actual CLI initial reviews were required')
        decisions = [c['output']['decision'] for c in runner.calls]
        if any(value not in {'mismatch', 'unresolved'} for value in decisions):
            raise RuntimeError('A reviewer failed to reject or withhold approval of the quantifier reversal: ' + str(decisions))
        if len(cycle['results']) != 2: raise RuntimeError('The two primary judgments were not sealed as initial results')
        item = engine.instance['knowledge'][kid]
        if item['status'] == 'verified' or item.get('identity_assessment', {}).get('effective'):
            raise RuntimeError('Negative initial evidence incorrectly produced usable K')
        if any(c['action']['stage'] != 'initial' for c in runner.calls): raise RuntimeError('A later review phase was called')
        if manifest(skill) != frozen: raise RuntimeError('Frozen source changed during the actual check')
        checks = []
        for call in runner.calls:
            execution = next(ex for ex in engine.runtime['executions'].values() if ex.get('action', {}).get('id') == call['action']['id'])
            raw = engine.store.read(f"runtime/artifacts/{execution['input_bundle']}/input.txt", engine.head)
            if sha(raw) != call['input_sha256']: raise RuntimeError('Actual input hash mismatch')
            context = json.loads(raw.decode().split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
            if context['role_review']['completed_results']: raise RuntimeError('Initial peer result disclosure detected')
            checks.append({'slot': call['action']['slot'], 'execution_id': execution['id'], 'input_sha256': sha(raw), 'peer_blind': True})
        usage = {}
        for call in runner.calls:
            for key, value in call.get('usage', {}).items():
                if isinstance(value, (int, float)) and not isinstance(value, bool): usage[key] = usage.get(key, 0) + value
        report.update(passed=True, actual_cli_invocations=2, initial_decisions=decisions,
            actual_findings=[{'slot': c['action']['slot'], 'findings': c['output'].get('findings', []), 'questions': c['output'].get('questions', [])} for c in runner.calls],
            no_K=True, identity_assessment_effective=False, cycle_phase=cycle['phase'], cycle_status=cycle['status'],
            final_mismatch_not_adjudicated=True, cycle_id=cycle_id, knowledge_id=kid, source_sha256=sha(SOURCE.encode()),
            signature_hash=item['formal'].get('signature_hash'), input_checks=checks, actual_cli_usage=usage,
            final_snapshot=engine.head, elapsed_seconds=time.monotonic()-started)
        status = 0
    except Exception as error:
        report.update(error=f'{type(error).__name__}: {error}', traceback=traceback.format_exc(),
                      actual_cli_invocations=len(runner.calls), elapsed_seconds=time.monotonic()-started)
    finally:
        dump(evidence/'final-instance.json', engine.instance)
        dump(evidence/'final-runtime.json', engine.runtime)
        dump(evidence/'result.json', report)
        subprocess.run(['git', '-C', str(repository), 'bundle', 'create', str(evidence/'state.bundle'), '--all'], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jsonl = [{'path': p.relative_to(evidence).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size} for p in sorted(evidence.rglob('*.jsonl'))]
        dump(evidence/'jsonl-manifest.json', jsonl)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return status

if __name__ == '__main__':
    raise SystemExit(main())
